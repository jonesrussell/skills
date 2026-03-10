---
name: myme-data-services
description: Use when modifying crates/myme-services/, crates/myme-integrations/, or crates/myme-organizations/ in MyMe. Covers HTTP clients, SQLite stores, GitHub API, git operations, retry logic.
---
# Data Services Specialist

## Scope
Packages: `crates/myme-services/` (2791 lines), `crates/myme-integrations/` (1026 lines), `crates/myme-organizations/` (712 lines)
Key files:
- `crates/myme-services/src/note_client.rs` — Async NoteClient wrapping SQLite
- `crates/myme-services/src/github.rs` — GitHubClient with retry
- `crates/myme-services/src/retry.rs` — RetryConfig, exponential backoff
- `crates/myme-services/src/project_store.rs` — ProjectStore with schema migrations
- `crates/myme-integrations/src/git/mod.rs` — git2 operations (discover, clone, pull, push)
- `crates/myme-integrations/src/github/mod.rs` — GitHub REST API wrapper
- `crates/myme-organizations/src/store.rs` — OrganizationStore for BD pipeline

## Key Interfaces

**SQLite Store Pattern** (all stores follow this):
```rust
impl Store {
    pub fn open(path: &Path) -> Result<Self>;    // CREATE TABLE IF NOT EXISTS
    pub fn create(&self, item: &Item) -> Result<()>;
    pub fn get(&self, id: &str) -> Result<Option<Item>>;
    pub fn list(&self) -> Result<Vec<Item>>;     // ORDER BY updated_at DESC
    pub fn update(&self, item: &Item) -> Result<()>;
    pub fn delete(&self, id: &str) -> Result<()>;
}
```

**Key types**: UUID TEXT PKs, ISO 8601 TEXT timestamps, enums via `serde_json`, arrays as JSON TEXT.

**RetryConfig** (`retry.rs`):
```rust
pub struct RetryConfig { pub max_retries: u32, pub initial_delay: Duration, pub max_delay: Duration }
impl RetryConfig {
    pub fn default() -> Self;  // 3 retries, 100ms initial, 5s max
}
pub async fn with_retry<F, T>(config: &RetryConfig, operation: F) -> Result<T>;
```
Retries: timeouts, 5xx, 429. No retry: 4xx.

**GitOperations** (`git/mod.rs`):
```rust
impl GitOperations {
    pub fn discover_repositories(search_path: &str) -> Vec<LocalRepo>;
    pub async fn clone(url: &str, path: &Path, token: Option<&str>, cancel: CancellationToken) -> Result<()>;
    pub fn fetch(path: &Path, token: Option<&str>) -> Result<()>;
    pub fn pull(path: &Path, token: Option<&str>) -> Result<()>;
    pub fn push(path: &Path, token: Option<&str>) -> Result<()>;
}
```

**ProspectStage** enum:
```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ProspectStage { Lead, Qualified, Contacted, Proposal, Negotiation, Won, Lost }
```

## Architecture

Local-first SQLite: each domain owns its DB file. No cross-DB queries — UI layer fetches separately and joins in memory.

NoteClient wraps SQLite via `spawn_blocking` for async compatibility. GitHubClient uses reqwest with `with_retry()`. ProjectStore has 3-version schema migration on open.

## Common Mistakes
- **Enum serialization**: `#[serde(rename_all = "lowercase")]` is required — without it, serde produces `"Lead"` not `"lead"`
- **JSON in TEXT columns**: Use `serde_json::to_string(&vec)` for array columns, `serde_json::from_str` on read
- **UPSERT pattern**: Use `INSERT OR REPLACE` for sync operations, not separate insert/update
- **Cascade deletes**: Test that deleting a parent (org → prospects, project → tasks) cascades correctly
- **Retry on 4xx**: Never retry 401/403/404 — they indicate client errors, not transient failures
- **CancellationToken**: Must check token before AND during git clone operations

## Testing Patterns
- **SQLite stores**: `tempfile::tempdir()` + fresh DB per test, test CRUD in order
- **HTTP clients**: `wiremock::MockServer::start().await` for API simulation
- **Retry**: Override `RetryConfig { max_retries: 1, .. }` in tests for speed
- **Git operations**: test with bare git repos created in tempdir
- **Cascade**: explicitly verify children are gone after parent delete

## Related Specs
- `docs/specs/data-services.md` — Full SQLite schemas, all struct definitions, migration details
