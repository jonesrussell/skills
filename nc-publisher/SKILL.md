---
name: nc-publisher
description: Use when modifying publisher/, routing layers, Redis channels, or content publishing in north-cloud. Covers 8-layer routing pipeline, channel management, deduplication, and Redis message format.
---

# Publisher Specialist

## Scope
- `publisher/` — all packages
- Two entry points: `cmd/api/` (channel management REST API) and `cmd/router/` (background routing worker)
- Default: `publisher both` runs API + router concurrently

## Key Interfaces

**RoutingDomain** (`internal/router/domain.go`):
- `Name() string` — domain identifier
- `Routes(item *ContentItem) []ChannelRoute` — returns channels for content item, nil to skip

**Rules** (`internal/models/rules.go`):
- `Matches(qualityScore int, contentType string, topics []string) bool`
- Fields: IncludeTopics, ExcludeTopics, MinQualityScore, ContentTypes

**Channel** (`internal/models/channel.go`):
- ID (UUID), Name, Slug (unique), RedisChannel (unique), Rules (embedded), Enabled

**Service** (`internal/router/service.go`):
- `Start(ctx) error` — main routing loop (poll ES every 30s)
- Cursor-based pagination via `search_after` (persisted in DB for restart safety)

## Architecture

```
ES *_classified_content → Router (30s poll, batch=100, search_after cursor)
  ↓ For each ContentItem:
Layer 1: TopicDomain     → content:{topic} (SKIPS: mining, indigenous, coforge, recipe, jobs)
Layer 2: DBChannelDomain → admin-defined channels with Rules.Matches()
Layer 3: CrimeDomain     → crime:homepage, crime:category:{slug}, crime:courts, crime:context
Layer 4: LocationDomain  → {prefix}:local:{city}, {prefix}:province:{code}, {prefix}:canada
Layer 5: MiningDomain    → content:mining, mining:core, mining:commodity:{slug}, mining:stage:{stage}
Layer 6: EntertainmentDomain → entertainment:homepage, entertainment:category:{slug}
Layer 7: IndigenousDomain    → content:indigenous, indigenous:category:{slug}
Layer 8: CoforgeDomain      → coforge:core, coforge:audience:{slug}, coforge:topic:{slug}
  ↓
Dedup check (per-channel) → Redis PUBLISH → publish_history record
```

**Layer 1 skip topics** (`domain_topic.go`): `mining`, `indigenous`, `coforge`, `recipe`, `jobs` — these MUST be in skip list to prevent bypassing specialized ML classifiers.

**Dedup**: Per-channel via `(article_id, channel_name)` unique check. Same content publishes to many channels but never twice to same channel.

## Common Mistakes

- **Layer 1 skip topics CRITICAL**: If a topic with a dedicated layer isn't in `layer1SkipTopics`, it bypasses ML classification filtering.
- **Mining pipeline gotcha**: If `mining.relevance` absent from all docs, mining-ml wasn't running when classifier ran. Fix: rebuild both containers.
- **Nil nested objects**: Always check `item.Mining == nil` before accessing `.Relevance`. Return nil from Routes() when domain doesn't apply.
- **No pub/sub persistence**: Consumers missing at publish time lose messages. Use Redis Streams if persistence needed.
- **Router processes synchronously**: One item at a time through all domains. Tune BatchSize + PollInterval for throughput.
- **Channel slug and redis_channel must be unique**: Database enforces uniqueness on both.
- **Underscore to hyphen conversion**: Slugs convert underscores to hyphens: `strings.ReplaceAll(name, "_", "-")`.

## Adding a New Routing Domain

1. Create `internal/router/domain_{name}.go` implementing `RoutingDomain`
2. Register in `routeContentItem()` domains slice in `service.go`
3. Add to `layer1SkipTopics` if it has dedicated ML classification
4. Add nested fields to `ContentItem` struct if classifier produces new fields
5. Update ARCHITECTURE.md routing layer table

## Testing Patterns

- Table-driven tests: `{name, item *ContentItem, expected []string}` for each domain
- Helper: `routeChannelNames(routes)` extracts Channel field from ChannelRoute slice
- Test all nil/empty paths (nil nested objects, empty relevance, "not_X" relevance)
- All test helpers MUST call `t.Helper()`

## Redis Message Format
See `publisher/docs/REDIS_MESSAGE_FORMAT.md` for full JSON structure. Key fields:
- `publisher.channel` — Redis channel name
- `publisher.published_at` — timestamp
- `body` — article text (alias for raw_text)
- `source` — URL (alias for URL)
- Crime/mining/indigenous/etc nested objects when present

## Related Specs
- `docs/specs/content-routing.md` (future) — full routing pipeline spec
- `publisher/CLAUDE.md` — service-level quick reference
- `publisher/docs/CONSUMER_GUIDE.md` — consumer integration guide
