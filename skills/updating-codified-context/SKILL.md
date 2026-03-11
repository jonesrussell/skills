---
name: updating-codified-context
description: Use when a repo has codified context already initialized (CLAUDE.md with orchestration table, docs/specs/ directory, drift-detector) and sessions have revealed stale specs, missing service docs, architecture drift, new subsystems without coverage, or MCP tools not wired.
---

# Updating Codified Context

## Overview

Systematic maintenance of an initialized codified-context repo. Fills gaps by tier (T1 → T2 → T3), verifies with drift-detector, and wires the self-trigger so future sessions auto-load this skill.

**Requires initialized state.** If CLAUDE.md lacks an orchestration table or `docs/specs/` doesn't exist, use `codified-context` skill instead.

## Baseline Failure Modes (Why This Skill Exists)

Without this skill, agents naturally:
1. **Skip creating new spec files** — map new services onto existing specs instead
2. **Miss MCP wiring** — don't check `.claude/settings.local.json` for spec-retrieval tools
3. **Miss self-trigger** — don't add the orchestration table row that auto-loads this skill
4. **Work ad-hoc** — no tier ordering, miss downstream dependencies
5. **Skip verification** — don't re-run drift-detector after changes

## Detect Initialized State

Check before starting:
- `CLAUDE.md` exists with an orchestration table (file pattern → service context → spec)
- `docs/specs/` directory exists with at least one spec file
- `tools/drift-detector.sh` or equivalent exists

If NOT initialized → use `codified-context` skill instead.

## Step 1: Audit (Identify Scope)

Run drift-detector first to establish baseline:
```bash
bash tools/drift-detector.sh 10
```

Then produce a priority table:

| Service | CLAUDE.md | Spec | Drift-detector pattern | MCP wired |
|---------|-----------|------|------------------------|-----------|
| rfp-ingestor | missing | missing | missing | n/a |
| social-publisher | missing | missing | missing | n/a |

Check MCP wiring (server may be in either committed or local config):
```bash
cat .claude/settings.json         # canonical location (committed, see codified-context Step 7)
cat .claude/settings.local.json 2>/dev/null  # local overrides
cat .claude/mcp.json 2>/dev/null  # alternative MCP config
```

Check GitHub workflow governance:
```bash
ls bin/check-milestones 2>/dev/null       # drift-check script
cat .claude/settings.json | grep -A5 SessionStart  # hook wired?
ls docs/specs/workflow.md 2>/dev/null     # governance spec
ls .github/pull_request_template.md 2>/dev/null    # PR template
```

Add to the audit table:

| Component | Present | Gap |
|-----------|---------|-----|
| `bin/check-milestones` | yes/no | create if missing |
| SessionStart hook in `.claude/settings.json` | yes/no | add if missing |
| `docs/specs/workflow.md` | yes/no | create if missing |
| CLAUDE.md GitHub Workflow section | yes/no | add if missing |
| `.github/pull_request_template.md` | yes/no | create if missing |

## Step 2: Update by Tier (T1 → T2 → T3)

### T1: Service CLAUDE.mds + Root Orchestration Table

For each service missing a CLAUDE.md, read the source first:
- Entry point (e.g. `main.go`, `index.ts`, `app.py`) — bootstrap pattern, ports, top-level flow
- Config file (e.g. `config.go`, `config.ts`, `.env.example`) — env vars and defaults
- Key domain files — understand what the service actually does

Write `{service}/CLAUDE.md` following the established pattern in other service CLAUDE.mds.

**After all service CLAUDE.mds are written**, add the self-trigger row to the root CLAUDE.md orchestration table:
```
| docs/specs/**, .claude/**, **/CLAUDE.md | updating-codified-context | — |
```
This causes any session touching context files to auto-load this skill.

### T2: Project Skills

Write or update project-specific skills only if:
- Domain knowledge has materially shifted (new pipeline layer, new platform adapter, etc.)
- Existing skill descriptions no longer match triggering conditions

Skip if no domain knowledge changed.

### T3: Specs + Drift-Detector + MCP

**Create new spec files** for each uncovered service — do NOT reuse existing specs for unrelated services.

Spec file template (`docs/specs/{service}.md`) — aligned with `codified-context` Step 6:
```markdown
# {Service} Specification
## File Map
## Interface Signatures
## Data Flow
## Storage / Schema
## Configuration
## Edge Cases
```

**Update drift-detector**: Add `["{service}/"]="docs/specs/{service}.md"` entries to `PATTERN_TO_SPEC`. Map each service to its own spec file.

**Wire MCP** if spec-retrieval server exists but tools aren't configured:
- Add `list_specs`, `get_spec`, `search_specs` to the `permissions.allow` list
- Add the server to `mcpServers` in `.claude/settings.json` (canonical) or `.claude/settings.local.json` (local-only)

### GitHub Workflow Governance

If the Step 1 audit found missing governance artifacts, create them now following `codified-context` Step 8:
- **`bin/check-milestones`**: bash script querying `gh api` for untriaged issues and stale milestones (exit 0 always)
- **SessionStart hook**: add to `.claude/settings.json` under `hooks.SessionStart` to run `bin/check-milestones`
- **`docs/specs/workflow.md`**: versioning model, milestone list, 5 workflow rules
- **CLAUDE.md GitHub Workflow section**: summarize 5 rules, point to `docs/specs/workflow.md`
- **`.github/pull_request_template.md`**: `Closes #`, summary, checklist (issue ref, milestone, title format)

## Step 3: Verify

Run drift-detector to confirm no regressions:
```bash
bash tools/drift-detector.sh 10
```
Expected: exit 0 with no MISSING or WARNING lines for newly covered services.

Then run the relevant checks from `codified-context` Step 10 (adapted for incremental updates):

**3a. Constitution quality gate** (if CLAUDE.md was modified):
- `wc -l CLAUDE.md` — under 200 = PASS, 200-250 = WARN, over 250 = FAIL
- Verify orchestration table still has pipe-delimited rows for all services

**3b. Coverage verification** (always):
- Cross-reference orchestration table entries against `docs/specs/` and `skills/` on disk
- Any referenced file missing = FAIL — fix before committing
- Check for orphan specs (>1 orphan = WARN)

**3c. MCP tools verification** (if specs were added/modified):
- `list_specs` returns updated spec list including new specs
- `get_spec` with a new spec name returns content with `# ` heading
- `search_specs` with a keyword from new spec returns matches
- `get_spec` with nonexistent name returns error listing available options

**3d. Smoke test** (pick 1-2 newly covered services):
- Trace: file path → orchestration table match → skill reference → spec retrieval via MCP → actionable knowledge
- At least 1 new service must complete the full chain

All checks must PASS or WARN. Fix any FAIL before committing.

## Step 4: Commit

One commit per logical unit:
```
chore(context): update codified context — <summary>
```

Example: `chore(context): fill codified context gaps — rfp-ingestor, social-publisher, MCP wiring, self-trigger`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Mapping new service to existing spec in drift-detector | Create `docs/specs/{service}.md` for each new service |
| Writing CLAUDE.md from task description alone | Read the actual source code first — configs reveal env vars, mapping reveals ES constraints |
| Forgetting self-trigger row in orchestration table | Add `docs/specs/**, .claude/**, **/CLAUDE.md → updating-codified-context` row |
| Skipping MCP wiring check | Check both `.claude/settings.json` (canonical) and `.claude/settings.local.json` for spec-retrieval tools |
| Not running drift-detector before AND after | Run before to establish baseline, after to verify no regressions |
