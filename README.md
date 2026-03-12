# Skills

Personal [Agent Skills](https://agentskills.io) for use with Claude Code.

## Install

Register as a plugin marketplace in Claude Code:

```
/plugin marketplace add jonesrussell/skills
```

Then install a plugin bundle:

```
/plugin install myme-skills@jonesrussell-skills
/plugin install north-cloud-skills@jonesrussell-skills
/plugin install blog-skills@jonesrussell-skills
/plugin install code-quality-skills@jonesrussell-skills
/plugin install misc-skills@jonesrussell-skills
```

## Plugin Bundles

### myme-skills
MyMe desktop app (Rust/Qt) development skills.
- `myme-core-auth` — App lifecycle, config, OAuth2, token storage
- `myme-data-services` — HTTP clients, SQLite stores, GitHub API, git operations
- `myme-google-services` — Gmail API, Calendar API, SQLite caches, sync queue
- `myme-qml-ui` — QML/Qt themes, page patterns, sidebar navigation
- `myme-ui-bridge` — cxx-qt bridge, QObject models, AppServices singleton
- `myme-weather` — Weather API, platform-native geolocation, caching

### north-cloud-skills
North-Cloud microservices (Go) development skills.
- `nc-classifier` — 4-step classification pipeline, hybrid rule+ML classifiers
- `nc-crawler` — Crawling architecture, job scheduling, frontier fetching
- `nc-infrastructure` — Config loading, structured logging, clients, JWT auth, middleware
- `nc-publisher` — 8-layer routing pipeline, channel management, deduplication
- `nc-search-indexing` — Search query building, index lifecycle, Elasticsearch mappings

### blog-skills
Blog and review writing skills.
- `blog-reviewing` — Review and audit blog posts against standards
- `blog-writing` — Create new blog posts for Hugo blogs
- `film-review` — Write movie reviews for movies-of-war.com

### code-quality-skills
Code quality, architecture, and security review skills.
- `cleaning-up-codebases` — Review codebases for cruft, dead code, anti-patterns
- `codified-context` — Apply three-tier codified context architecture
- `monorepo-cleanup` — Review monorepos for cross-service issues
- `security-review` — Audit services for security vulnerabilities
- `updating-codified-context` — Update existing codified context when specs drift

### misc-skills
Miscellaneous development workflow skills.
- `documenting-session-findings` — Capture session findings before moving on
- `optimizing-responsive-images` — Responsive image sizing, format conversion, srcset

## Creating Skills

Use `template/SKILL.md` as a starting point. See the [Agent Skills spec](https://agentskills.io/specification) for details.
