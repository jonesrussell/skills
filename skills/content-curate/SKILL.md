---
name: content-curate
description: Review and curate mined content queue items. Use when user says "curate", "what's in my content queue?", "review content ideas", or "/curate".
---

# Content Curation

## Overview

Present `stage:mined` content queue issues as a batch for quick human decisions: approve, skip, merge, or edit.

## Process

1. **Fetch mined items:**
   ```bash
   gh issue list --repo jonesrussell/jonesrussell --label "stage:mined" --json number,title,body,createdAt --limit 20
   ```

2. **Identify the item source** and present accordingly. Two distinct item types exist:

   **Git-activity items** (from waaseyaa/framework, waaseyaa/giiken, etc.):
   - Show: issue number, title, source repo + commit/issue reference
   - Show: content seed (what was built/changed), suggested type and channels
   - Recommendation: why this makes a good post or why not
   - Path: could become blog post OR standalone text-post

   **North Cloud items** (label: `source:north-cloud`):
   - Show with a `[NC]` prefix so they're visually distinct
   - Show: article title as a link, source domain, quality score, topics
   - Recommendation: whether the article is worth amplifying to your audience
   - Path: always text-post (sharing, not writing) — no blog post
   - Frame the decision as: "Is this worth your audience's attention?"

3. **Ask for a decision on each item:**
   - **Approve** — confirm or adjust channels, then:
     ```bash
     gh issue edit <N> --repo jonesrussell/jonesrussell --remove-label "stage:mined" --add-label "stage:curated"
     ```
   - **Skip** — close with skip label:
     ```bash
     gh issue close <N> --repo jonesrussell/jonesrussell
     gh issue edit <N> --repo jonesrussell/jonesrussell --add-label "skipped"
     ```
   - **Merge** — combine with another item (ask which one), update the target issue's seed, skip the source
   - **Edit** — update the seed material, type, or channels before approving

4. **Batch summary.** After processing all items, report:
   - N approved (ready for production)
   - N skipped
   - N merged
   - Suggest running `/content-produce` next for the approved items

## Presentation Style

Keep it scannable. One item at a time.

**Git-activity item:**
```
**#15: [content] SovereigntyProfile shipped in Waaseyaa**
Source: waaseyaa/framework commit abc1234 (2026-04-04)
Seed: Added SovereigntyProfile to Layer 0. Communities declare local/hybrid/cloud sovereignty mode.
Suggested: text-post → x, linkedin, facebook

Good candidate. Concrete feature, ties to data sovereignty narrative.

→ Approve / Skip / Merge / Edit?
```

**North Cloud item:**
```
[NC] **#47: [content] Why your PHP app is slower than it needs to be**
Source: North Cloud · coforge:core · dev.to (quality: 78)
Article: https://dev.to/example/why-your-php-app-is-slower
Topics: php, performance, optimization

Worth sharing. Practical, audience-relevant, no paywall. Good for a quick reshare with a take.

→ Share / Skip / Edit?
```

## When Queue Is Empty

If no `stage:mined` items exist, say so and suggest:
- Running the mining skill (`/content-mine`) to scan recent activity
- Creating a content idea manually via the issue template
