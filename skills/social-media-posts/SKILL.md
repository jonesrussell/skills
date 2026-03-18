---
name: social-media-posts
description: Create social media posts promoting blog posts, project milestones, or announcements. Use when user says "social post", "promote this", "share on social", "tweet this", or after publishing a blog post. Matches the blog's voice (second person, direct, Anishinaabemowin greetings where appropriate) and includes real data/results when available.
---

# Social Media Posts

## Overview

Generate ready-to-paste social media copy for multiple platforms. Posts match the author's voice: direct, second person, concise, technically grounded. Include real metrics or results when available. No corporate fluff.

## Voice Rules

| Element | Rule |
|---------|------|
| Tone | Direct, technical, conversational. Not corporate. Not salesy. |
| Person | Second person when addressing readers ("your AI assistant", "you develop"). First person when sharing results ("I built", "first audit"). |
| Concise | Short sentences. One idea per sentence. No filler. |
| Em dashes | Use sparingly. Prefer periods, colons, or commas. |
| Emoji | None. Let the content speak. |
| Hashtags | None unless user requests them. They reduce engagement on most platforms. |
| Real data | When audit results, metrics, or concrete outcomes exist, include them. Specificity beats vague claims. |

## Platform Guidelines

### Facebook

- 2-3 short paragraphs. Hook, context, result.
- Longest of the formats. You have room to explain the "why."
- End with the canonical URL on its own line so OG can unfurl.

### X (Twitter)

- Under 240 characters including URL.
- One punchy statement or result. Link at the end.
- If it doesn't fit in one tweet, cut words. Don't thread.

### LinkedIn

- Professional but not stiff. Technical audience.
- 2-3 paragraphs. Problem, solution, result.
- End with the canonical URL on its own line.

### Mastodon / Bluesky

- Similar to Twitter length but no character pressure.
- Slightly more room to breathe. 1-3 sentences plus link.
- Technical audience. Skip the "excited to announce" framing.

## Output Format

Save the social copy as a markdown file. Structure:

```markdown
# Social copy: [Post or Announcement Title]

**Canonical URL:** https://jonesrussell.github.io/blog/{slug}/

## Facebook

[Copy here]

[URL on its own line]

## X (Twitter)

[Copy here, under 240 chars with URL]

[URL]

## LinkedIn

[Copy here]

[URL on its own line]

## Mastodon / Bluesky

[Copy here]

[URL]
```

### Where to save

- For blog posts: `docs/social/{slug}.md` in the blog repo or the project repo.
- For project announcements: `docs/social/{topic}.md` in the relevant project repo.
- Always use the same slug as the source content.

## Content Types

### Blog Post Promotion

1. Read the blog post (fetch URL or read local file).
2. Identify the core insight or result. What would make someone click?
3. If the post has data (audit scores, performance numbers, before/after), lead with it.
4. Include the canonical URL in every platform block.

### Milestone / Release Announcement

1. State what shipped and why it matters.
2. Include one concrete metric or outcome if available.
3. Link to the relevant post, PR, or changelog.

### Audit / Report Results

1. Lead with the most surprising or impactful finding.
2. Include specific numbers (compliance scores, divergence counts, candidates found).
3. Link to the full report or blog post.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| "Excited to announce" | Just state what happened. Excitement is implied by sharing it. |
| Vague claims ("improved our process") | Use specific numbers: "caught 5 divergences", "scored 46%" |
| Same copy on all platforms | Adapt length and tone per platform |
| Hashtag spam | No hashtags unless explicitly requested |
| Missing URL | Every platform block needs the canonical URL |
| Corporate voice ("leverage", "synergy") | Write like you're explaining it to a peer |
| Emoji decoration | No emoji. The content is the signal. |
| Threading on Twitter | If it doesn't fit one tweet, cut it down |
