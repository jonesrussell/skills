---
name: myme-core-auth
description: Use when modifying crates/myme-core/ or crates/myme-auth/ in MyMe. Covers app lifecycle, config, error types, OAuth2, token storage.
---
# Core & Auth Specialist

## Scope
Packages: `crates/myme-core/` (908 lines), `crates/myme-auth/` (963 lines)
Key files:
- `crates/myme-core/src/config.rs` — TOML config loading, validation, caching
- `crates/myme-core/src/error.rs` — Error hierarchy with `user_message()`
- `crates/myme-auth/src/oauth.rs` — OAuth2Provider trait, PKCE flow, warp callback
- `crates/myme-auth/src/storage.rs` — SecureStorage (system keyring), TokenSet
- `crates/myme-auth/src/github.rs` — GitHubAuth implementing OAuth2Provider
- `crates/myme-auth/src/google.rs` — GoogleOAuth2Provider for Gmail/Calendar

## Key Interfaces

**Config** (`config.rs`):
```rust
impl Config {
    pub fn load() -> Result<Self>;                          // From platform-specific TOML
    pub fn load_cached() -> Arc<Self>;                      // OnceLock singleton
    pub fn load_validated() -> Result<(Self, ValidationResult)>;
    pub fn validate(&self) -> ValidationResult;
    pub fn save(&self) -> Result<()>;
}
```
Sections: `services`, `ui`, `weather`, `projects`, `repos`, `github`, `google` (Option), `notes`.

**SecureStorage** (`storage.rs`):
```rust
impl SecureStorage {
    pub fn new() -> Self;
    pub fn store(&self, key: &str, token_set: &TokenSet) -> Result<()>;
    pub fn load(&self, key: &str) -> Result<Option<TokenSet>>;
    pub fn delete(&self, key: &str) -> Result<()>;
    pub fn migrate_legacy_tokens(&self) -> Result<()>;  // Plaintext -> keyring
}
pub struct TokenSet { pub access_token: String, pub refresh_token: Option<String>, pub expires_at: Option<DateTime<Utc>> }
```
Key namespaces: `myme.github`, `myme.google`

**OAuth2Provider** trait (`oauth.rs`):
```rust
pub trait OAuth2Provider {
    fn authorization_url(&self, state: &str, port: u16) -> String;
    async fn exchange_code(&self, code: &str, port: u16) -> Result<TokenSet>;
}
```
Dynamic port discovery on 8080-8089 via `find_available_port()`.

**Error hierarchy** (`error.rs`):
- `AppError` — top-level with `user_message()` for UI display
- `AuthError` — authentication failures (token expired, invalid, etc.)
- `GitHubError` — GitHub API errors (rate limit, not found, etc.)

## Architecture

Config path resolution: `dirs::config_dir()` → `myme/config.toml`. Created with defaults on first run.

OAuth flow: `authorization_url()` → browser opens → warp server on `localhost:PORT/callback` → `exchange_code()` → `SecureStorage::store()`.

Google requires `access_type=offline&prompt=consent` for refresh tokens. GitHub refresh is different (PAT-based, no refresh token flow).

## Common Mistakes
- **Wrong token namespace**: Use `myme.github` and `myme.google` — mixing causes token conflicts
- **Missing `prompt=consent`**: Google won't return refresh_token on re-auth without it
- **Blocking on OAuth**: OAuth exchange is async — never `block_on()` from Qt thread
- **Config validation vs load**: `load()` succeeds with invalid values; `load_validated()` reports warnings
- **Forgetting `is_configured()`**: Always check `GitHubConfig::is_configured()` before using client_id/secret

## Testing Patterns
- Config: test with `tempdir()` for config file creation/load/save cycle
- Auth storage: keyring operations are platform-specific — mock `SecureStorage` in unit tests
- OAuth: mock warp callback server, test state parameter validation
- Errors: test `user_message()` returns human-readable strings for each variant

## Related Specs
- `docs/specs/core-auth.md` — Full interface signatures, config struct fields, error enum variants
