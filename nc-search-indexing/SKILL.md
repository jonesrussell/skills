---
name: nc-search-indexing
description: Use when modifying search/, index-manager/, or Elasticsearch queries/mappings in north-cloud. Covers search query building, index lifecycle, mapping definitions, aggregations, and the mapping drift problem.
---

# Search & Index Management Specialist

## Scope
- `search/` — full-text search API (queries ES classified_content indices)
- `index-manager/` — ES index lifecycle, mapping definitions, aggregation queries
- `infrastructure/elasticsearch/` — shared ES client

## Key Interfaces

**Search Query Builder** (`search/internal/elasticsearch/query_builder.go`):
- Multi-match with field boosting: title^3.0, og_title^2.0, body^1.0
- Bool query: must (text match) + filter (quality, topics, dates) + should (recency boost)
- Fuzziness: AUTO for typo tolerance
- Aggregations: topics, content_types, sources, quality_ranges

**Index Service** (`index-manager/internal/service/index_service.go`):
- `CreateIndex(req *CreateIndexRequest) error` — creates ES index with mapping + metadata
- `NormalizeSourceName(name) string` — dots→underscores, hyphens→underscores, lowercase
- Index naming: `{normalized_source}_{type}` (e.g., `bbc_news_classified_content`)

**Aggregation Service** (`index-manager/internal/service/aggregation_service.go`):
- Crime, mining, location, overview, source-health aggregations
- All use `size: 0` (no docs, just aggs) with optional filters

**Mapping Versions** (`index-manager/internal/elasticsearch/mappings/versions.go`):
- `RawContentMappingVersion = "2.0.0"`, `ClassifiedContentMappingVersion = "2.2.0"`
- Drift detection at startup (warning, not blocking)

## Architecture

```
Crawler → {source}_raw_content (dynamic mapping by classifier or explicit by index-manager)
Classifier → {source}_classified_content (dynamic mapping)
  ↓
Index-Manager: metadata tracking (index_metadata table), mapping versioning, reindexing
  ↓
Search: multi-index query across *_classified_content → faceted results
```

**Mapping definitions** in `index-manager/internal/elasticsearch/mappings/`:
- `raw_content.go` — id, url, title, raw_text, og_*, crawled_at, classification_status
- `classified_content.go` — all raw fields + content_type, quality_score, topics, source_reputation + nested: crime, mining, location, coforge, indigenous, entertainment, recipe, job
- Helper functions: `getCrimeMapping()`, `getMiningMapping()`, etc. (funlen compliance)

## Common Mistakes

- **CRITICAL — Mapping drift (.keyword)**: Classifier creates indices with dynamic mappings (text fields). Index-manager defines explicit mappings (keyword fields). For aggregations, ALWAYS use `.keyword` sub-fields: `source_name.keyword`, `topics.keyword`, `content_type.keyword`. Bare field name causes ES 400 error (fielddata disabled on text).
- **Port conflict in dev**: Both index-manager and search use port 8090 internally. Docker maps search to 8092.
- **Mappings are immutable in ES**: Cannot change field types. Must delete + recreate index (data loss) or create new index + reindex.
- **Bulk operations return 207 Multi-Status**: Check each item in response for partial failures.
- **Only classified_content is searchable**: If content missing from search results, check `classification_status` in raw index.
- **Max query length 500 chars**: Enforced by validation. Longer queries rejected.
- **Facets are expensive**: Only request with `include_facets=true` when UI needs filter counts.

## Testing Patterns

- Mock ES client implementing `AggregationESClient` interface
- Test query builder independently of ES connection
- Test valid responses, ES errors, malformed JSON, null values, empty results
- Index service tests: mock both ES and DB
- All test helpers MUST call `t.Helper()`

## Related Specs
- `docs/specs/discovery-querying.md` (future) — full search/indexing spec
- `search/CLAUDE.md`, `index-manager/CLAUDE.md` — service-level references
