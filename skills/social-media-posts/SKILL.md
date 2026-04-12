---
name: social-media-posts
description: Create social media posts promoting blog posts, project milestones, or announcements. Use when user says "social post", "promote this", "share on social", "tweet this", or after publishing a blog post. Matches the blog's voice (second person, direct, Anishinaabemowin greetings where appropriate) and includes real data/results when available.
---

# Social Media Posts

## Overview

Generate ready-to-paste social media copy for three platforms: Facebook, X, LinkedIn. Posts match the author's voice: direct, second person, concise, technically grounded. Include real metrics or results when available. No corporate fluff.

**2026 key insight:** Links in post bodies suppress reach on all three platforms. Always put URLs in the first comment (LinkedIn, Facebook) or first self-reply (X). Write the post as pure text.

## Voice Rules

| Element | Rule |
|---------|------|
| Tone | Direct, technical, conversational. Not corporate. Not salesy. |
| Person | Second person when addressing readers ("your AI assistant", "you develop"). First person when sharing results ("I built", "first audit"). |
| Concise | Short sentences. One idea per sentence. No filler. |
| Em dashes | Use sparingly. Prefer periods, colons, or commas. |
| Emoji | None. Let the content speak. |
| Real data | When audit results, metrics, or concrete outcomes exist, include them. Specificity beats vague claims. |

## Hashtag Rules

| Platform | Rule |
|----------|------|
| Facebook | 1-2 relevant hashtags only. More than 2 drops engagement. Append at the end. |
| X | Embed 1-2 niche hashtags naturally in the sentence — mid-sentence placement gets ~28% more engagement than appended. Add `#buildinpublic` when sharing work-in-progress, shipped features, or milestones. 3+ hashtags penalized ~40% by algorithm. |
| LinkedIn | 3-5 niche hashtags at the bottom of the post body (e.g. `#softwaredevelopment #opensource #buildinpublic`). LinkedIn uses them for topic classification, not discovery — keep them relevant, not keyword-stuffed. |

## Platform Guidelines

### X (Twitter)

- **Post body: 70-150 characters.** Short punchy statement or concrete outcome. No link in the body — links suppress reach.
- **Link goes in your first self-reply**, posted immediately after. This is the standard pattern in 2026.
- Embed hashtags naturally in the sentence rather than appending. 1-2 max.
- Single post only. No threads unless you genuinely have 4+ connected points — threads are for teaching, single posts win for reach.
- First 30 minutes are the critical distribution window. Early engagement (especially retweets) weights the algorithm heavily.

### LinkedIn

- **1,200-1,800 characters** for technical/developer content. This range outperforms both shorter and longer posts for the audience.
- **Hook in the first 2-3 lines** (before "see more"). Lead with the outcome or problem, not preamble. This is the single biggest factor in whether the post gets expanded.
- Line breaks every 1-3 lines. Walls of text kill engagement.
- **Link goes in the first comment**, not the post body. Link-in-comment delivers ~2.9x more reach and ~2.7x more clicks than link-in-post (documented A/B tests, 2025-2026).
- 3-5 niche hashtags at the bottom of the post body.
- Professional but not stiff. Write like you're explaining to a peer.

### Facebook

- 2-3 short paragraphs. Hook, context, result.
- **Text-only post body** — no link in the body. Link goes in the first comment. Text posts reach further than link posts on personal profiles.
- 1-2 hashtags at the end. They won't meaningfully expand reach beyond your existing network — they're decorative. Keep them or skip them; don't use more than 2.
- Expect reach limited to your existing network. Facebook text posts don't surface to non-followers in 2026. Optimize for the audience you have, not discovery.

## Output Format

Save the social copy as a markdown file. Three platforms only — no Mastodon, no Bluesky.

The file captures the post body copy and the first-comment/reply URL separately, so the poster knows what to put where.

```markdown
# [Post or Announcement Title]

Reference URL: https://...

## X

[Post body — 70-150 chars, no link, hashtags embedded naturally]

**First reply:**
[URL]

## LinkedIn

[Post body — 1,200-1,800 chars, hook first, line breaks, hashtags at bottom, no link]

**First comment:**
[URL]

## Facebook

[Post body — 2-3 paragraphs, no link, 1-2 hashtags at end]

**First comment:**
[URL]
```

### Where to save

- For blog posts: `docs/social/{slug}.md` in the blog repo.
- For text posts (no blog post): `docs/social/{topic-slug}.md` in the blog repo.
- Always use the same slug as the source content.

## Content Types

### Blog Post Promotion

1. Read the blog post (fetch URL or read local file).
2. Identify the core insight or result. What would make someone click?
3. If the post has data (audit scores, performance numbers, before/after), lead with it.
4. The canonical blog URL goes in the first comment/reply — not the post body.

### Dev Work Text Post (no blog post)

1. State what was built or fixed and the concrete outcome.
2. **Always include a GitHub reference** the reader can actually look at: a commit, PR, issue, file, or diff. Without this it is just narrative about something invisible.
3. If the work has a vibe coding angle (AI-assisted), surface it where authentic — don't force it.
4. The GitHub URL goes in the first comment/reply on each platform.

### Milestone / Release Announcement

1. State what shipped and why it matters.
2. Include one concrete metric or outcome if available.
3. Link to the relevant post, PR, or changelog — in the first comment/reply.

### Audit / Report Results

1. Lead with the most surprising or impactful finding.
2. Include specific numbers (compliance scores, divergence counts, candidates found).
3. Link to the full report or blog post — in the first comment/reply.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Link in post body | Links suppress reach on all three platforms. First comment/reply only. |
| "Excited to announce" | Just state what happened. |
| Vague claims ("improved our process") | Use specific numbers: "caught 5 divergences", "relaxed 6 constraints" |
| Same copy on all platforms | Adapt length and tone per platform |
| No hashtags on LinkedIn | 3-5 niche hashtags at the bottom. They aid topic classification. |
| 2-4 hashtags on Facebook | 1-2 max. More than 2 drops engagement. |
| X body over 150 chars | Cut it. Shorter posts outperform longer ones on X. |
| Hashtags appended on X | Embed naturally in the sentence for ~28% more engagement. |
| 3+ hashtags on X | Penalized ~40% by algorithm. |
| Missing URL or reference | Every platform needs a link — in the first comment/reply. |
| Corporate voice ("leverage", "synergy") | Write like you're explaining it to a peer. |
| Emoji decoration | No emoji. The content is the signal. |
| Threading on X | Single post wins for reach. Thread only for 4+ genuinely connected points. |
| Dev post with no GitHub link | Always include a commit, PR, file, or issue link. |
