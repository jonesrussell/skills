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

2. **Sort mined items by confidence score** (highest first). Extract the confidence value from the `**Confidence:**` line in each issue body. Items without a confidence value sort last (legacy items from before grouping was implemented).

3. **Validate each mined item.** For each fetched issue, extract the structured seed data from the issue body and validate against the `mined-seed` schema:
   ```bash
   node ~/dev/blog/schemas/validate.js mined-seed /tmp/mined-seed-<issue-number>.json
   ```
   - If validation **passes**, include in the curation batch.
   - If validation **fails**, flag it to the user: "Issue #N has malformed seed data: <error>. Skipping — fix the issue manually or re-mine."
   - Do not silently process malformed items.

4. **Identify the item source** and present accordingly. Two distinct item types exist:

   **Git-activity items** (from waaseyaa/framework, waaseyaa/giiken, etc.):
   - Show: issue number, title, confidence score, source repo
   - Show: commit count (count comma-separated entries in the **Commits:** line). For items with multiple commits (grouped seeds), show the commit count rather than individual SHAs. The user does not need to see every SHA during curation.
   - Show: content seed (what was built/changed), suggested type and channels
   - Recommendation: why this makes a good post or why not
   - Path: could become blog post OR standalone text-post

   **North Cloud items** (label: `source:north-cloud`):
   - Show with a `[NC]` prefix so they're visually distinct
   - Show: article title as a link, source domain, quality score, topics
   - Recommendation: whether the article is worth amplifying to your audience
   - Path: always text-post (sharing, not writing) — no blog post
   - Frame the decision as: "Is this worth your audience's attention?"

5. **Ask for a decision on each item:**
   - **Approve** — confirm or adjust channels, then build a curated-item JSON and validate:
     ```bash
     cat > /tmp/curated-item-<N>.json << 'CURATED'
     {
       "source": "<from mined seed>",
       "source_ref": "<from mined seed>",
       "content_seed": "<from mined seed, possibly edited>",
       "suggested_type": "<from mined seed>",
       "suggested_channels": <from mined seed>,
       "mined_at": "<from mined seed>",
       "curated_type": "<confirmed type>",
       "curated_channels": ["<confirmed channels>"],
       "curation_action": "approved",
       "curated_at": "<current ISO 8601 timestamp>",
       "editorial_notes": "<optional: human notes on angle>"
     }
     CURATED
     node ~/dev/blog/schemas/validate.js curated-item /tmp/curated-item-<N>.json
     ```
     If validation **fails**, show the error and fix before proceeding.
     If validation **passes**, update the labels:
     ```bash
     gh issue edit <N> --repo jonesrussell/jonesrussell --remove-label "stage:mined" --add-label "stage:curated"
     ```
     After labeling, fetch the source issue for full context, then invoke `social-media-posts` before writing a single word of copy. This is mandatory — not optional, not "check after." The skill defines platform rules (X char limits, hashtag policy, GitHub link requirements) that cannot be reliably recalled from memory.
   - **Skip** — close the issue immediately to remove it from the queue. This distinguishes intentional skips from auto-expiry (which uses the `auto-expired` label).
     ```bash
     gh issue close <N> --repo jonesrussell/jonesrussell --comment "Skipped during curation."
     gh issue edit <N> --repo jonesrussell/jonesrussell --add-label "curate:skipped"
     ```
   - **Merge** — combine with another item (ask which one), update the target issue's seed, skip the source
   - **Edit** — update the seed material, type, or channels before approving

6. **Batch summary.** After processing all items, report:
   - N approved (ready for production)
   - N skipped
   - N merged
   - Suggest running `/content-produce` next for the approved items

## Presentation Style

Keep it scannable. One item at a time.

**Git-activity item:**
```
**#15: [content] SovereigntyProfile shipped in Waaseyaa** (confidence: 0.82)
Source: waaseyaa/framework · 3 commits (2026-04-04)
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
