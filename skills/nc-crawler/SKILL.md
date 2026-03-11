---
name: nc-crawler
description: Use when modifying crawler/, internal/crawler/, internal/scheduler/, internal/fetcher/, or internal/frontier/ in north-cloud. Covers crawling architecture, job scheduling, frontier fetching, and content indexing.
---

# Crawler Specialist

## Scope
- `crawler/` — all packages
- Key entry: `crawler/main.go` → `internal/bootstrap/app.go` (7-phase startup)
- Two crawl paths: Colly-based crawler (rich extraction) and frontier fetcher (lightweight)

## Key Interfaces

**CrawlerInterface** (`internal/crawler/crawler.go`):
- `Start(ctx, sourceID) error` — run crawl for a source
- `Stop(ctx) error` — graceful stop
- `Subscribe(handler)` — event handler registration
- Factory pattern: `crawler.NewFactory(params).Create()` returns isolated instances per job

**JobRepositoryInterface** (`internal/database/interfaces.go`):
- `GetJobsReadyToRun(ctx) ([]*Job, error)` — scheduler polls this
- `AcquireLock(ctx, jobID, token, now, duration) (bool, error)` — CAS distributed locking
- `ReleaseLock(ctx, jobID) error`
- `ClearStaleLocks(ctx, cutoff) (int, error)` — 5-min stale recovery

**Storage Interface** (`internal/storage/types/interface.go`):
- `IndexDocument(ctx, index, id, document) error`
- `IndexDocumentIfAbsent(ctx, index, id, document) error` — frontier uses op_type=create

**State Machine** (`internal/scheduler/state_machine.go`):
- States: pending → scheduled → running → completed/failed
- `CanPause(job)`, `CanResume(job)`, `CanCancel(job)`, `CanRetry(job)`
- Cancelled is terminal. Failed allows manual retry (resets counter).

## Architecture

```
Source Manager API → Crawler fetches source configs (lazy, thread-safe)
  ↓
Scheduler (10s poll) → AcquireLock (CAS) → Factory.Create() → isolated Crawler
  ↓
Colly crawl: HTML → Processors → IndexRawContent() → {source}_raw_content ES index
Frontier fetch: URL queue → HTTP fetch → IndexRawContentIfAbsent() (won't overwrite Colly docs)
  ↓
Adaptive scheduling: SHA-256 content hash → adjust next_run_at if unchanged
```

**Retry**: Exponential backoff 60s → 120s → 240s → 480s → 960s → 3600s (capped). Manual retry resets counter.

**Proxy pool**: Domain-sticky round-robin across 4 endpoints (2 Toronto, 2 NYC). Config: `CRAWLER_PROXY_POOL_URLS`.

## Common Mistakes

- **Missing source_id**: Jobs without source_id fail at execution. Always validate via source-manager API first.
- **Interval fields conditional**: `interval_minutes = NULL` → one-time job. Set `schedule_enabled: false` for one-time.
- **Stale lock recovery is 5 minutes**: Don't manually clear locks unless scheduler fully stopped.
- **document_parsing_exception for json_ld_data**: Index created before canonical mapping. Fix: delete index, re-crawl.
- **Max depth defaults to 3**: When `max_depth = 0` in source config. Sources with depth > 5 trigger warning.
- **Frontier writes don't overwrite Colly docs**: `IndexRawContentIfAbsent` uses op_type=create intentionally.
- **Redis Colly storage falls back to in-memory silently**: If Redis unavailable, visited URLs don't persist.

## Testing Patterns

- Factory test: verify `Create()` returns isolated instances with shared `startURLHashes` map
- State machine test: table-driven tests for all valid/invalid transitions
- No-op logger: `infralogger.NewNop()` for test helpers
- All test helpers MUST call `t.Helper()`
- Fixtures in `crawler/fixtures/` for HTTP replay (VCR-like)

## Related Specs
- `docs/specs/content-acquisition.md` (future) — full crawl pipeline spec
- `crawler/docs/INTERVAL_SCHEDULER.md` — scheduler design reference
- `crawler/CLAUDE.md` — service-level quick reference
