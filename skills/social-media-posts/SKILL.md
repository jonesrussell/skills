---
name: social-media-posts
description: Create social media posts promoting blog posts, project milestones, or announcements. Use when user says "social post", "promote this", "share on social", "tweet this", or after publishing a blog post. Matches the blog's voice (second person, direct, Anishinaabemowin greetings where appropriate) and includes real data/results when available.
---

# Social Media Posts

## Overview

Generate ready-to-paste social media copy for three platforms: Facebook, X, LinkedIn. Posts match the author's voice: direct, second person, concise, technically grounded. Include real metrics or results when available. No corporate fluff.

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
| Facebook | Add relevant hashtags at the end (e.g. `#hugo #claudecode #webdev`). 2-4 max. |
| X | Add `#buildinpublic` when the post shares work-in-progress, a shipped feature, or a project milestone. Skip it for purely informational or tutorial posts. No other hashtags. |
| LinkedIn | No hashtags. Keep copy clean. |

## Platform Guidelines

### Facebook

- 2-3 short paragraphs. Hook, context, result.
- Longest of the formats. You have room to explain the "why."
- End with the canonical URL on its own line, then hashtags on the next line.

### X (Twitter)

- Under 240 characters including URL and any hashtag.
- One punchy statement or result. Link at the end.
- If it doesn't fit in one tweet, cut words. Don't thread.

### LinkedIn

- Professional but not stiff. Technical audience.
- 2-3 paragraphs. Problem, solution, result.
- End with the canonical URL on its own line. No hashtags.

## Output Format

Save the social copy as a markdown file. Three platforms only — no Mastodon, no Bluesky.

```markdown
# [Post or Announcement Title]

Blog URL: https://jonesrussell.github.io/blog/{slug}/

## Facebook

[Copy here]

[URL on its own line]

[hashtags on their own line]

## X

[Copy here, under 240 chars with URL and any hashtag]

## LinkedIn

[Copy here]

[URL on its own line]
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
4. Include the canonical URL in every platform block.

### Dev Work Text Post (no blog post)

1. State what was built or fixed and the concrete outcome.
2. **Always include a GitHub reference** the reader can actually look at: a commit, PR, issue, file, or diff. Without this it is just narrative about something invisible.
3. If the work has a vibe coding angle (AI-assisted), surface it where authentic — don't force it.
4. Link to the GitHub reference in every platform block. If there is also a blog post, link that instead and reference the GitHub link in the copy.

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
| "Excited to announce" | Just state what happened. |
| Vague claims ("improved our process") | Use specific numbers: "caught 5 divergences", "relaxed 6 constraints" |
| Same copy on all platforms | Adapt length and tone per platform |
| Hashtags on LinkedIn | LinkedIn copy has no hashtags |
| Missing URL or reference | Every platform block needs a link to something real |
| Corporate voice ("leverage", "synergy") | Write like you're explaining it to a peer |
| Emoji decoration | No emoji. The content is the signal. |
| Threading on X | If it doesn't fit one tweet, cut it down |
| Dev post with no GitHub link | Always include a commit, PR, file, or issue link |
