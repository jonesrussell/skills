---
name: changelog
description: Maintain Keep a Changelog format changelogs and run releases via scripts/release.sh
---

# Changelog Maintenance

## When to Use

- **After completing work, before committing.** Add an entry to `[Unreleased]` describing what changed.
- **When running a release.** Use `scripts/release.sh` to promote `[Unreleased]` to a versioned section.

## Changelog Format

Follow [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/).

### Standard Header

Every project's `CHANGELOG.md` starts with:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

### Categories

Use only these categories, in this order. Drop empty ones.

| Category | When to use |
|----------|-------------|
| Added | New features, new capabilities |
| Changed | Changes to existing functionality |
| Fixed | Bug fixes |
| Removed | Removed features or deprecated items |

### Entry Rules

- One entry per issue or PR, not per commit. Squash related commits into a single line.
- Reference issue numbers: `- Description of change (#42)`
- Write in human-readable, user-facing language. Describe **what changed for the user**, not implementation details.
- Use imperative mood: "Add dark mode support" not "Added dark mode support" or "Adds dark mode support".

**Good:**
```markdown
### Added
- Add dark mode support for dashboard (#42)
- Add CSV export for reports (#51)

### Fixed
- Fix login redirect loop when session expires (#38)
```

**Bad:**
```markdown
- Refactored the AuthService class to use strategy pattern
- Updated package.json
- Fixed stuff
```

## How to Add an Entry

1. Open `CHANGELOG.md`
2. Find the `## [Unreleased]` section
3. Add the entry under the appropriate category heading (e.g., `### Added`)
4. If the category does not exist yet, create it under `[Unreleased]` in the standard order: Added, Changed, Fixed, Removed
5. Format: `- Description of change (#issue-number)`

## How to Release

1. Run `scripts/release.sh vX.Y.Z`
2. The script will:
   - Validate the version format
   - Replace `## [Unreleased]` contents with `## [X.Y.Z] - YYYY-MM-DD`
   - Add a fresh empty `## [Unreleased]` section above it
   - Create a git tag
   - Push the tag and commit
3. Optionally, create a GitHub release from the tag using `gh release create`

### Version Bumping Guidelines

| Change type | Bump | Example |
|-------------|------|---------|
| Breaking changes | Major | 1.0.0 -> 2.0.0 |
| New features (backward compatible) | Minor | 1.0.0 -> 1.1.0 |
| Bug fixes only | Patch | 1.0.0 -> 1.0.1 |

## Backfill for New Projects

When adding a changelog to an existing project that does not have one:

1. Run `git log --oneline --no-merges` to review history
2. Group commits by type:
   - `feat` commits -> **Added**
   - `fix` commits -> **Fixed**
   - `refactor`, `chore`, `docs`, `style`, `perf` commits -> **Changed**
3. Create a `## [0.1.0] - YYYY-MM-DD` section using the date of the earliest relevant commit (or today's date)
4. Add an empty `## [Unreleased]` section above it
5. Copy the canonical `scripts/release.sh` from any existing project that has one, or write one following the release steps above

### Backfill Example

```markdown
## [Unreleased]

## [0.1.0] - 2026-01-15

### Added
- Initial project scaffolding with CLI and web server
- User authentication via Fortify (#1)
- Article ingestion pipeline (#5)

### Fixed
- Correct timezone handling in date display (#8)
```

## Reference: `scripts/release.sh`

The release script should accept a single argument (the version tag) and perform:

```bash
#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?Usage: release.sh vX.Y.Z}"
DATE=$(date +%Y-%m-%d)

# Strip leading 'v' for changelog heading
SEMVER="${VERSION#v}"

# Validate semver format
if [[ ! "$SEMVER" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
  echo "Error: Invalid semver format: $SEMVER" >&2
  exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
  echo "Error: Uncommitted changes. Commit or stash first." >&2
  exit 1
fi

# Update CHANGELOG.md
sed -i "s/^## \[Unreleased\]$/## [Unreleased]\n\n## [$SEMVER] - $DATE/" CHANGELOG.md

# Commit changelog, tag, push
git add CHANGELOG.md
git commit -m "release: $VERSION"
git tag -a "$VERSION" -m "Release $VERSION"
git push origin HEAD --follow-tags

echo "Released $VERSION"
```

Adjust the script to fit the project's needs (e.g., adding `gh release create` or running tests before tagging).
