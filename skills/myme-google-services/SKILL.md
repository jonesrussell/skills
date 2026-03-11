---
name: myme-google-services
description: Use when modifying crates/myme-gmail/ or crates/myme-calendar/ in MyMe. Covers Gmail API, Calendar API, SQLite caches, sync queue, offline support.
---
# Google Services Specialist

## Scope
Packages: `crates/myme-gmail/` (1560 lines), `crates/myme-calendar/` (1296 lines)
Key files:
- `crates/myme-gmail/src/client.rs` — Gmail REST API client
- `crates/myme-gmail/src/cache.rs` — SQLite offline cache for messages/labels
- `crates/myme-gmail/src/sync.rs` — Offline action sync queue
- `crates/myme-gmail/src/types.rs` — Message, Label, API response types
- `crates/myme-calendar/src/client.rs` — Calendar REST API client
- `crates/myme-calendar/src/cache.rs` — SQLite offline cache for events
- `crates/myme-calendar/src/types.rs` — Event, Calendar types

## Key Interfaces

**GmailClient**:
```rust
impl GmailClient {
    pub fn new(access_token: &str) -> Self;
    pub async fn list_message_ids(&self, query: Option<&str>, page_token: Option<&str>) -> Result<MessageListResponse, GmailError>;
    pub async fn get_message(&self, message_id: &str) -> Result<Message, GmailError>;
    pub async fn send_message(&self, to: &str, subject: &str, body: &str, reply_to_id: Option<&str>) -> Result<Message, GmailError>;
    pub async fn modify_labels(&self, message_id: &str, add: &[&str], remove: &[&str]) -> Result<(), GmailError>;
    pub async fn mark_as_read/unread/star/unstar/archive/trash(&self, message_id: &str) -> Result<(), GmailError>;
}
```

**CalendarClient**:
```rust
impl CalendarClient {
    pub fn new(access_token: &str) -> Self;
    pub async fn list_calendars(&self) -> Result<Vec<Calendar>, CalendarError>;
    pub async fn list_events(&self, calendar_id: &str, time_min: DateTime<Utc>, time_max: DateTime<Utc>) -> Result<Vec<Event>, CalendarError>;
    pub async fn create_event(&self, calendar_id: &str, event: &NewEvent) -> Result<Event, CalendarError>;
    pub async fn update_event/delete_event/quick_add(&self, ...) -> Result<...>;
}
```

**Error types** — both implement:
```rust
pub fn should_refresh_token(&self) -> bool;  // true for 401
pub fn is_retryable(&self) -> bool;          // true for 429, 5xx
pub fn user_message(&self) -> String;        // human-readable
```

**SyncQueue** (`sync.rs`):
```rust
impl SyncQueue {
    pub fn open(path: &Path) -> Result<Self>;
    pub fn enqueue(&self, action: SyncAction) -> Result<()>;
    pub fn dequeue(&self) -> Result<Option<(i64, SyncAction)>>;  // FIFO
    pub fn complete(&self, id: i64) -> Result<()>;
    pub fn retry(&self, id: i64) -> Result<()>;
}
```

## Architecture

**Gmail sync**: Initial fetch of 500 messages → store `historyId` → incremental via `history.list` → on 404, full resync.

**Calendar sync**: Fetch 3 months (1 past + 2 future) with `singleEvents=true` → store `syncToken` → incremental via syncToken → on 410 Gone, full resync.

**Offline queue**: Actions (mark read, star, archive, trash, send) queued in SQLite SyncQueue. On reconnect, dequeue FIFO and replay. Retry with exponential backoff on failures.

Both caches use SQLite with same patterns as data-services (UUID PKs, ISO timestamps, JSON arrays in TEXT).

## Common Mistakes
- **Token expiry**: Google access tokens expire in 1 hour — ALWAYS check/refresh before API calls
- **History vs sync tokens**: Gmail uses numeric `historyId` (404 = expired), Calendar uses opaque `syncToken` (410 = expired) — different error handling paths
- **Partial sync failures**: When syncing multiple items, one failure must not stop others — collect errors and continue
- **Rate limiting**: Google APIs have per-user quota — respect 429 with backoff
- **Message body encoding**: Gmail returns base64url-encoded body parts — decode with `base64::engine::general_purpose::URL_SAFE_NO_PAD`
- **All-day events**: Check `is_all_day` flag — all-day events use date (not datetime) in Google API

## Testing Patterns
- **Client tests**: `wiremock` with JSON response bodies matching Google API format
- **Cache tests**: `tempfile::tempdir()` + fresh SQLite per test
- **Sync queue**: test FIFO ordering, retry count increment, complete removes entry
- **35 Gmail tests, 21 Calendar tests** in the crate test suites

## Related Specs
- `docs/specs/google-services.md` — Full SQLite schemas, all type definitions, API response parsing
