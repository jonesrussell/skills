---
name: blog-writing
description: Use when creating new blog posts, drafting content, or writing articles for this Hugo blog. Triggers include requests to write, draft, or create a post.
---

# Blog Writing

## Overview

Write blog posts that match this blog's voice: second person, direct, instructional, culturally grounded with Anishinaabemowin greetings. Reference post: `content/posts/laravel-boost-ddev.md`. Full style guide: `docs/blog-style.md`.

## Style Rules (Canonical Authority)

| Element | Rule |
|---------|------|
| Greeting | Always open with "Ahnii!" (exclamation mark, own paragraph) |
| Farewell | Always close with "Baamaapii" (no emoji, own paragraph) |
| Voice | Second person, direct, instructional. Address reader as "you"/"your". Not corporate. |
| Concise | Short sentences. One idea per paragraph. No filler or throat-clearing. |
| Scoped intro | In the intro, state what the post covers in one sentence |
| Code blocks | Always specify language tag. After each block, add 1-2 sentences explaining what it does or why. For error output, reformat for readability — don't carbon-copy terminal noise. |
| Links | Link first mention of products, tools, or projects. Internal: root-relative with trailing slash `/slug/`. External: full HTTPS URLs. |
| Headings | H2 for main sections, H3 for variants/subsections. No time estimates. No "Wrapping Up" or "Conclusion". Use SEO-friendly headings with keywords (e.g., "Fix WSL Browser Hangs With BROWSER=echo" not "The Fix"). |
| Em dashes | Use sparingly. Heavy "—" usage reads as AI-written. Prefer periods (two short sentences), colons, or commas. One or two per post is enough; zero is fine. |

## Frontmatter (Required Fields)

```yaml
---
title: "Post Title"        # sentence case, descriptive
date: YYYY-MM-DD
categories: []              # lowercase, hyphenated for multi-word
tags: []                    # max 4 tags
summary: ""                 # one sentence: outcome or audience
slug: "url-slug"            # kebab-case
draft: true
---
```

For series posts, add: `series: ["series-name"]`

## Post Type: General

Use for standalone posts (tutorials, tools, project showcases).

```
Ahnii!

[Intro: what the thing is (link first mentions) + one sentence on scope]

## Prerequisites

- [Requirement 1]
- [Requirement 2]

## [Main Section]

[Content with code examples]
[After each code block: 1-2 sentences explaining what it does]

## [Additional Sections as needed]

[Use H3 for variants, e.g. "Standard Setup" / "WSL Setup"]

## [Verify / Follow-up section when relevant]

[e.g. "Verify It Works", "Keeping X Updated"]

Baamaapii
```

## Post Type: Series

Use for posts in a multi-part series (e.g., PSR php-fig-standards series).

```
Ahnii!

> **Prerequisites:** [requirements]. **Recommended:** Read [Link](/slug/) first. **Pairs with:** [related posts].

[Intro: what this standard/topic is + one sentence on scope]

## What Problem Does [Topic] Solve?

[Why this matters — the "before" pain point]

## Core Interfaces / Core Concepts

### 1. [First Concept]
[Code with inline comments]
[1-2 sentences explaining the code]

### 2. [Second Concept]
[Code with inline comments]
[1-2 sentences explaining the code]

## Real-World Implementation

[Working code example — practical, not theoretical]
[Explanation of what the code does]

## Common Mistakes and Fixes

### 1. [Mistake]
[Bad code → Good code with comments explaining why]

### 2. [Mistake]
[Bad code → Good code]

## Framework Integration

### [Framework 1]
[Code example + explanation]

### [Framework 2]
[Code example + explanation]

## Try It Yourself

[Commands to run from companion repo or hands-on steps]

## What's Next

[Link to next post in series with brief description]

Baamaapii
```

## Screenshots

When a post covers UI, web tools, or anything visual, use the Playwright MCP to capture screenshots.

### When to Include Screenshots

- Documentation or dashboard walkthroughs
- Before/after UI changes
- Error messages in browser dev tools
- OAuth flows or login screens
- Any step where "what you should see" helps the reader

### How to Capture

1. Use `browser_navigate` to load the page
2. Use `browser_take_screenshot` to capture:
   - `filename`: Save to `static/images/posts/{slug}/` with descriptive name
   - `fullPage: true` for full-page captures when needed
   - `element` + `ref` to screenshot a specific element (get ref from `browser_snapshot`)

### In the Post

```markdown
![Description of what the screenshot shows](/blog/images/posts/{slug}/screenshot-name.png)
```

Note: The `/blog/` prefix is required because the site's baseURL is `https://jonesrussell.github.io/blog/`. Without it, images break in both local dev and production.

Add a brief caption or follow with 1-2 sentences explaining what the reader should notice.

## Social media artifact

After creating or updating a post, generate a **companion markdown file** with ready-to-paste copy for different platforms. The file lets you share the post with the canonical link in the body so Open Graph (OG) can fetch title, description, and image when the link is shared.

### Where to put it

- Path: `docs/social/{slug}.md` (same `slug` as the post).
- Create or overwrite this file whenever you create or substantially update a post.

### Canonical URL

- Use the full post URL: `https://jonesrussell.github.io/blog/{slug}/`.
- Include it in every platform block so OG does its job when the link is previewed.

### File structure

Use this structure in the artifact. Keep platform copy concise; the link drives the preview.

```markdown
# Social copy: [Post Title]

**Canonical URL:** https://jonesrussell.github.io/blog/{slug}/

## Mastodon / Bluesky / long-form

[1–3 sentences hook + link. No strict limit.]

## X (Twitter)

[Short hook, under ~240 chars including URL. Put link at end.]

## LinkedIn

[Professional one-liner or short paragraph + link. Tone fits LinkedIn.]
```

### Platform notes

- **Mastodon / Bluesky:** Longer copy is fine. One or two sentences plus the link. No character limit to target.
- **X (Twitter):** Stay under ~240 characters including the URL so it fits one tweet; put the link at the end.
- **LinkedIn:** One or two sentences, more professional tone; include the link.

Always include the **canonical URL** in each block so the platform can unfurl it and OG works.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Adding emoji to farewell | Farewell is "Baamaapii" — no emoji |
| First-person voice | Use second person: "your project", "you can" — not "I found", "my setup" |
| No explanation after code blocks | After every code block, add 1-2 sentences on what it does or why |
| Not linking first mentions | Link products/tools/projects on first mention |
| Generic closing ("Wrapping Up", "Conclusion") | No closing header — transition naturally to farewell |
| Time estimates in headings | Don't add reading time to headings |
| More than 4 tags | Pick the 4 most relevant; fewer is fine |
| Using `description` field | Use `summary` in frontmatter, not `description` |
| Filler in intro | State what the post covers in one sentence. No throat-clearing. |
| Generic headings | Use descriptive, keyword-rich headings. "Why CLI Tools Hang in WSL" not "The Problem". |
| Carbon-copy terminal output | Reformat error output for readability. Break long lines, remove noise, keep the key details. |
| Too narrow scope | If a fix applies broadly, generalize the post. Cover the pattern, not just one tool. |
| Overusing em dashes (—) | Replace with periods (split into two sentences), colons, or commas. Heavy dash use reads as AI slop. |

