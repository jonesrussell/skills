---
name: myme-ui-bridge
description: Use when modifying crates/myme-ui/src/ Rust code in MyMe. Covers cxx-qt bridge, QObject models, AppServices singleton, service channels, error mapping.
---
# UI Bridge Specialist

## Scope
Package: `crates/myme-ui/src/` (8945 lines Rust)
Key files:
- `src/app_services.rs` — AppServices singleton (tokio runtime, all clients, channel pairs)
- `src/bridge.rs` — C FFI functions for Qt init/shutdown
- `src/models/*.rs` — 18 QObject models (note, gmail, calendar, organization, repo, etc.)
- `src/services/*.rs` — 11 service message types and async handlers
- `src/error_mapping/*.rs` — Service errors → AppError for UI display
- `build.rs` — cxx-qt code generation config (registers all model files)

## Key Interfaces

**AppServices** singleton:
```rust
static SERVICES: OnceLock<Arc<AppServices>> = OnceLock::new();
impl AppServices {
    pub fn init() -> Arc<Self>;                    // Creates tokio runtime, all channels
    pub fn runtime(&self) -> tokio::runtime::Handle;
    pub fn shutdown(&self);                        // Broadcasts shutdown, clears all state
    pub fn note_client(&self) -> Option<Arc<NoteClient>>;
    pub fn github_client(&self) -> Option<Arc<GitHubClient>>;
    // ... accessors for all clients and channel pairs
}
```

**Channel pattern** (every model follows this):
```rust
// Service message enum
pub enum NoteServiceMessage {
    FetchNotes,
    NotesLoaded(Result<Vec<Todo>, String>),
    CreateNote(TodoCreateRequest),
    NoteCreated(Result<Todo, String>),
    // ...
}

// In model's fetch method:
fn fetch_notes(mut self: Pin<&mut Self>) {
    self.as_mut().set_loading(true);
    let tx = get_note_tx();
    let _ = tx.send(NoteServiceMessage::FetchNotes);
}

// In model's poll_channel:
fn poll_channel(mut self: Pin<&mut Self>) {
    while let Ok(msg) = self.rx.try_recv() {
        match msg { /* update state, emit signals */ }
    }
}
```

**C FFI bridge** (`bridge.rs`):
```rust
#[no_mangle] pub extern "C" fn init_app_services();       // Called from main.cpp
#[no_mangle] pub extern "C" fn shutdown_app_services();    // Called from aboutToQuit
```

**build.rs registration**:
```rust
CxxQtBuilder::new()
    .file("src/models/note_model.rs")
    .file("src/models/gmail_model.rs")
    // ... 18 total model files
    .build();
```

## Architecture

Data flow: QML calls `model.fetch_data()` → model sends request via mpsc tx → background tokio task receives → calls service client → sends result via mpsc tx → QML Timer (100ms) calls `model.poll_channel()` → model updates state → emits signal → QML reacts.

AppServices owns all clients and channels. Models get channel senders/receivers during initialization. Service tasks run on the tokio runtime.

**Shutdown sequence**: Qt `aboutToQuit` signal → `shutdown_app_services()` C FFI → `AppServices::shutdown()` → broadcast shutdown → cancel in-flight ops → clear all state.

## Common Mistakes
- **Never `block_on()` on Qt thread** — always use channel pattern. Violating this freezes the UI.
- **cxx-qt snake_case** — methods exposed to QML keep exact Rust snake_case names. QML calls `model.fetch_notes()`, NOT `model.fetchNotes()`.
- **Register in build.rs** — new model files must be added as `.file("src/models/x.rs")` or cxx-qt won't generate the C++ bridge code.
- **Signal after state change** — must call `self.as_mut().signal_name()` after updating properties, or QML won't react.
- **Pin<&mut Self>** — all mutable model methods take `Pin<&mut Self>`, not `&mut self`.
- **Channel type mismatch** — each service has its own message enum. Don't mix note messages into gmail channels.
- **Missing try_recv loop** — `poll_channel` must use `while let Ok(msg)` not `if let`, to drain all pending messages per poll.

## Testing Patterns
- Models: difficult to test directly (require Qt runtime) — test service logic separately
- Services: test message handling with mock clients
- Error mapping: test that each service error maps to correct AppError variant
- Integration: myme-ui is excluded from `cargo test` (needs Qt) — test via manual UI interaction

## Related Specs
- `docs/specs/ui-bridge.md` — Full AppServices fields, all channel pairs, init/shutdown sequence, build.rs registration list
