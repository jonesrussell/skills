---
name: nc-classifier
description: Use when modifying classifier/, ml-sidecars/, or classification logic in north-cloud. Covers the 4-step classification pipeline, hybrid rule+ML classifiers, ES mappings, and ML sidecar integration.
---

# Classifier Specialist

## Scope
- `classifier/` — all packages
- `ml-sidecars/` — Python Flask ML services (crime-ml, mining-ml, coforge-ml, entertainment-ml, indigenous-ml)
- Two entry points: `cmd/httpd/` (HTTP API) and `cmd/processor/` (batch poller)

## Key Interfaces

**Classifier** (`internal/classifier/classifier.go`):
- `Classify(ctx, raw *RawContent) (*ClassificationResult, error)` — main orchestrator
- `ResolveSidecars(contentType, subtype) []string` — determines which optional classifiers run
- Steps: ContentType → Quality → Topics → SourceReputation → [Optional: Crime, Mining, Coforge, Entertainment, Indigenous]

**MLClassifier** (shared pattern across all ML clients):
- `Classify(ctx, title, body string) (*ClassifyResponse, error)` — POST /classify to sidecar
- `Health(ctx) error` — GET /health
- Body truncated to 500 chars via `CallMLWithBodyLimit[T]()` helper

**Poller** (`internal/processor/poller.go`):
- Polls `{source}_raw_content` for `classification_status=pending`
- Batch size default 100, poll interval 30s
- Worker pool concurrency default 10

## Architecture

```
ES {source}_raw_content (status=pending)
  ↓ Poller (30s interval, batch=100)
Step 1: ContentType detection (heuristics, OG metadata, URL patterns)
  → article, page, video, image, job, recipe + subtypes (press_release, blotter, event...)
Step 2: Quality scoring (0-100, 4 factors × 25pts: word count, metadata, richness, readability)
Step 3: Topic detection (Aho-Corasick keyword matching, O(n+m), rules from PostgreSQL)
Step 4: Source reputation (lookup/create, update after classification)
  ↓
Optional hybrid classifiers (rule + ML merge via decision matrix):
  Crime → CrimeResult (relevance: core_street_crime/peripheral_crime/not_crime)
  Mining → MiningResult (relevance + mining_stage + commodities)
  + Coforge, Entertainment, Indigenous, Location, Recipe, Job
  ↓
ES {source}_classified_content + PostgreSQL classification_history
```

**Decision matrix pattern** (all hybrid classifiers):
| Rules | ML | Result | Notes |
|-------|-----|--------|-------|
| core | core | core | High confidence (avg) |
| core | not | core | Medium, review_required=true |
| core | unreachable | core | Rule confidence only |
| none | core (>0.9) | peripheral | ML confidence × 0.8 |

## Common Mistakes

- **Missing Body/Source aliases**: `ClassifiedContent.Body` and `.Source` must be set or publisher silently skips. Set in `BuildClassifiedContent()`.
- **Rules cached at startup**: Changes to `classification_rules` table require service restart. No live reload.
- **Optional classifiers are nil when disabled**: Check `if c.crime != nil` before calling. Result field is nil and omitted from ES doc.
- **ML failures are non-blocking**: All hybrid classifiers log warning and fall back to rules-only on ML error.
- **Mining keywords intentionally narrow**: `resource`, `grade`, `deposit`, `reserve` excluded to prevent false positives. ML handles nuance.
- **Spam threshold = 30**: quality_score < 30 flags spam and penalizes source reputation, but document still classified.
- **Content subtype gates sidecars**: `ResolveSidecars()` routing table controls which classifiers run per content type/subtype.

## Testing Patterns

- Mock ML client: implement `Classify(ctx, title, body)` returning fixed response
- Mock source reputation DB: `testhelpers.NewMockSourceReputationDB()` — in-memory map
- Test hybrid classifiers with all decision matrix paths (both agree, rule override, ML override, ML unreachable)
- All test helpers MUST call `t.Helper()`

## Related Specs
- `docs/specs/classification.md` (future) — full classification pipeline spec
- `classifier/CLAUDE.md` — service-level quick reference
- `ARCHITECTURE.md` — publisher routing layers (downstream of classifier)
