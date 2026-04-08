---
name: content-mine
description: Scan recent git and GitHub activity to surface content ideas. Use when user says "mine my work", "what's postable?", "content ideas", or "/content-mine".
---

# Content Mining

## Overview

Scan recent activity across repos to surface content ideas. Create content queue issues for anything worth posting about.

## Sources

Two parallel signal sources feed the content queue:

### 1. Git Activity (manual / scheduled)

Run this skill to scan recent dev work. Default time range: last 7 days. User can specify: "mine the last 3 days", "mine since Monday".

**Git commits (key repos):**
```bash
for repo in waaseyaa/framework waaseyaa/giiken jonesrussell/blog jonesrussell/jonesrussell; do
  echo "=== $repo ==="
  gh api repos/$repo/commits --jq '.[].commit | "\(.author.date) \(.message)"' --paginate 2>/dev/null | head -20
done
```

**Closed issues and milestones:**
```bash
for repo in waaseyaa/framework waaseyaa/giiken jonesrussell/jonesrussell; do
  echo "=== $repo ==="
  gh issue list --repo $repo --state closed --json number,title,closedAt --limit 10
done
```

**New design specs:**
```bash
find ~/dev/blog/docs/superpowers/specs/ -name "*.md" -newer /tmp/last-mine-marker 2>/dev/null
```

**Blog posts published:**
```bash
find ~/dev/blog/content/posts/ -name "index.md" -newer /tmp/last-mine-marker 2>/dev/null
```

### 2. North Cloud Classified Content (event-driven / automatic)

A separate signal handler service subscribes to North Cloud's Redis pub/sub and creates content-queue issues automatically. These issues arrive with `source:north-cloud` label.

- **Channel**: `coforge:core` (developer/startup content classified as core relevance)
- **Filters**: quality_score ≥ 65, content_type article or blog_post, deduped by URL
- **Output**: `stage:mined`, `source:north-cloud`, `type:text-post`
- **Brand filter**: only software/AI/builder ecosystem content — no crime, entertainment, mining, indigenous

This source runs independently. When you run `/content-mine`, North Cloud items already in the queue appear alongside git-activity items. You don't need to trigger them manually.

## Process

3. **Filter noise.** Skip:
   - Merge commits, dependency bumps, CI fixes
   - Commits with messages under 10 characters
   - Typo fixes, formatting-only changes
   - Anything already in the content queue (check existing issues)

4. **Assess each candidate.** For each remaining item, ask:
   - Does this demonstrate something interesting? (feature, technique, milestone)
   - Would this resonate with the audience? (AI, Waaseyaa, open source, PHP, Go, software fundamentals)
   - Is there enough substance for a post?

5. **Create queue issues.** For each surfaceable item:
   ```bash
   gh issue create --repo jonesrussell/jonesrussell \
     --title "[content] <descriptive title>" \
     --label "content-queue,stage:mined,type:<suggested-type>" \
     --body "<filled content queue template>"
   ```

6. **Update marker.**
   ```bash
   touch /tmp/last-mine-marker
   ```

7. **Report.** Show what was mined:
   - N items surfaced (with issue numbers)
   - Key themes spotted
   - Suggest running `/curate` to review

## Noise Filtering Heuristics

| Signal | Keep | Skip |
|--------|------|------|
| Feature commit with description | yes | |
| "fix typo", "update deps" | | yes |
| Milestone closed | yes | |
| Issue with 1-line body | | yes |
| Design spec created | yes | |
| CI/CD config change | | yes |
| New blog post published | yes | |
| Merge commit | | yes |

## Over-Surface

When in doubt, create the issue. It's easier to skip during curation than to miss something worth posting about.
