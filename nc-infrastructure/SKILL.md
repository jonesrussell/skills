---
name: nc-infrastructure
description: Use when modifying infrastructure/ shared packages in north-cloud. Covers config loading, structured logging, ES/Redis/Postgres clients, JWT auth, pipeline events, retry logic, and HTTP middleware.
---

# Shared Infrastructure Specialist

## Scope
- `infrastructure/` — 27 shared packages used by all Go services
- Module: `github.com/north-cloud/infrastructure`
- Import alias convention: `infralogger`, `infraconfig`

## Key Interfaces

**Logger** (`logger/`):
```go
type Logger interface {
    Debug/Info/Warn/Error/Fatal(msg string, fields ...Field)
    With(fields ...Field) Logger
    Sync() error
}
```
- Creation: `logger.New(config)`, `logger.NewFromLoggingConfig(level, format)`, `logger.NewNop()` (tests)
- Field helpers: `logger.String()`, `logger.Int()`, `logger.Error()`, `logger.Any()`, etc.
- Context: `logger.WithContext(ctx, log)` / `logger.FromContext(ctx)`

**Config** (`config/`):
- `Load[T](path) (*T, error)` — YAML + env overrides
- `LoadWithDefaults[T](path, setDefaults) (*T, error)`
- Env tags: `env:"VARIABLE_NAME"` on struct fields
- Priority: `ENV_FILE` env var → `.env.local` → `.env`

**Pipeline Client** (`pipeline/`):
- `NewClient(baseURL, serviceName)` — if baseURL empty, all methods are no-ops
- `Emit(ctx, event) error` — fire-and-forget with circuit breaker
- Circuit breaker: 5 failures → open, 30s half-open, 2 successes → closed

**JWT Middleware** (`jwt/`):
- `Middleware(secret) gin.HandlerFunc` — validates HMAC tokens
- Skips: `/health`, `/health/*`
- Token from: `Authorization: Bearer <token>` header OR `?token=` query param (SSE)

**Retry** (`retry/`):
- `Retry(ctx, config, fn) error` — exponential backoff
- Defaults: 3 attempts, 100ms initial, 30s max, 2.0 multiplier

## Architecture

All services follow bootstrap pattern:
```
Config (YAML + env) → Logger → Database → ES/Redis → Services → HTTP Server → Lifecycle
```

**Import patterns**:
```go
import infralogger "github.com/north-cloud/infrastructure/logger"
import infraconfig "github.com/north-cloud/infrastructure/config"
```

**Service go.mod**: `require github.com/north-cloud/infrastructure v0.0.0` with `replace => ../infrastructure`

## Common Mistakes

- **NEVER use `os.Getenv` directly**: `forbidigo` linter enforces this. Use `infrastructure/config` with `env` tags.
- **Always JSON logging**: Format is always JSON with snake_case fields. Never configure text output.
- **Context-aware DB methods**: Always use `PingContext()`, `QueryContext()`, etc.
- **Pipeline client no-ops gracefully**: If base URL empty, `Emit()` silently succeeds. Check `IsEnabled()`.
- **Circuit breaker on pipeline**: After 5 consecutive pipeline failures, stops trying for 30s. Don't retry manually.
- **JWT skips health endpoints**: `/health` and `/health/*` bypass auth. Don't add sensitive data there.
- **Redis client pings on creation**: `NewClient()` verifies connection (5s timeout). Fails fast if Redis down.
- **ES client retries on startup**: Default 10 attempts with 3s→15s backoff. Patient connection establishment.

## Testing Patterns

- No-op logger: `logger.NewNop()` — use in all test helpers
- Config: create struct directly, no need to load from file in tests
- Pipeline: `NewClient("", "test")` creates no-op client
- Retry: test with mock functions that fail N times then succeed

## Packages Reference

| Package | Purpose | Key Export |
|---------|---------|-----------|
| `config` | YAML + env config loading | `Load[T]()`, `LoadWithDefaults[T]()` |
| `logger` | Structured JSON logging | `Logger` interface, `New()`, `NewNop()` |
| `elasticsearch` | ES client with TLS + retry | `NewClient(ctx, cfg, log)` |
| `redis` | Redis client wrapper | `NewClient(cfg)` |
| `http` | HTTP client with timeouts | `NewClient(cfg)`, `NewDefaultClient()` |
| `jwt` | JWT auth middleware | `Middleware(secret)`, `GetClaims(c)` |
| `gin` | HTTP middleware stack | `LoggerMiddleware`, `CORSMiddleware`, `RequestIDMiddleware` |
| `pipeline` | Event emission (circuit breaker) | `NewClient(url, svc)`, `Emit(ctx, evt)` |
| `events` | Domain event types | `SourceCreated/Updated/Deleted/Enabled/Disabled` |
| `sse` | Server-Sent Events broker | `Broker`, `Publisher`, `Subscriber` |
| `retry` | Exponential backoff | `Retry(ctx, cfg, fn)` |
| `profiling` | pprof + Pyroscope | `StartPprofServer()`, `StartPyroscope(name)` |
| `monitoring` | Memory health endpoint | `MemoryHealthHandler` |
| `context` | Timeout helpers | `WithDefaultTimeout()`, `WithShutdownTimeout()` |
| `clickurl` | Click tracking URL signing | URL HMAC signing |

## Related Specs
- `docs/specs/shared-infrastructure.md` (future) — full infrastructure spec
