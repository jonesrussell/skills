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
| Scoped intro | In the intro, state what the post covers in one sentence. Cover the relevant W's: **What** (what you'll learn), **Why** (why it matters or what problem it solves), **Who** (who it's for, if not obvious). **How** is the body. When/Where are rarely relevant for technical posts. Not all W's apply — use judgment. |
| Code blocks | Always specify language tag. After each block, add 1-2 sentences explaining what it does or why. For error output, reformat for readability — don't carbon-copy terminal noise. |
| Links | Link first mention of products, tools, or projects. Internal: use `relref` (e.g., `{{< relref "post-slug" >}}`), never root-relative paths (the `/blog/` base path breaks them). External: full HTTPS URLs. |
| Headings | H2 for main sections, H3 for variants/subsections. No time estimates. No "Wrapping Up" or "Conclusion". Use SEO-friendly headings with keywords (e.g., "Fix WSL Browser Hangs With BROWSER=echo" not "The Fix"). |
| Em dashes | Use sparingly and on purpose. Heavy "—" usage reads as AI-written. Prefer periods (two short sentences), colons, or commas. One or two per post is enough; zero is fine. |
| Contrast constructions | Don't keep reaching for "X is not Y, it is Z." Once can work. Repetition reads formulaic and AI-written. If the point lands better as a direct sentence, write the direct sentence. |
| Negative framing | Avoid stacking "do not," "does not," "not enough," or repeated "instead of" moves when the direct sentence would be clearer. "Put the defaults in the repo" is better than "keep defaults in the repo instead of your head." |
| Sentence variety | Mix short and medium sentences so the post has rhythm. Avoid sections where every sentence lands at the same length or every paragraph follows the same beat. |
| Filler and jargon | Cut generic AI-sounding words such as "robust," "seamless," "transformative," "game-changing," and "momentum" unless the term is concrete and necessary. Say what the thing does. |
| Section transitions | End each section with a sentence that creates a reason to read the next one. Open questions, unresolved tension, or a "but" that the next section resolves. Don't let the reader stop comfortably between sections. |
| No redundant explanation | Don't re-explain a problem the intro already established. If the reader came here because they have the problem, get to the fix. |
| Diagrams | When explaining flows, pipelines, or relationships between components, use a Mermaid diagram instead of (or alongside) prose. A ```` ```mermaid ```` code block renders natively. Use diagrams for: request/response flows, architecture layers, state machines, data pipelines. Don't use diagrams for: simple lists, single-step processes, or anything that's clearer as a sentence. |
| Explain before naming | Before introducing a named concept (interface, class, pattern), explain what it does in plain language. "A domain router owns one slice of request handling" before showing `DomainRouterInterface`. The reader needs the "what" before the "how." |
| Show, don't describe | If you're writing a sentence like "the handle() method routes to X, Y, and Z", put X/Y/Z in the code example instead. Prose that narrates what code does is redundant when the code is right there. Combine the description into the code block. |
| Back up claims with code | Every behavioral claim ("you can add a new action without changing X") needs an example showing it. If you can't show it, reconsider whether the claim is accurate. |
| Prefer direct imperatives | When you are teaching, prefer direct instructions over contrast setup. Write "Verify the workflow on a fresh shell" rather than "Do not trust the workflow because it looks tidy." |

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

## File Output

Write the primary post artifact as a Hugo leaf bundle:

- Primary file: `content/posts/{slug}/index.md`
- Use the same `slug` from frontmatter for the directory name
- Do not write standalone post files like `content/posts/{slug}.md`
- Frontmatter comes first in the file. `Ahnii!` is the first content paragraph after frontmatter, not before it.

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

## Post Type: Series Index

Use for the landing page of a multi-part series. Every series gets one index post at `series_order: 0`.

**Additional frontmatter:**

```yaml
series: ["series-name"]
series_order: 0
```

**Structure:**

```
Ahnii!

[1-2 sentence intro: what the series covers + who it's for]

### 1. [Post Title]({{< relref "post-slug" >}})

[1-2 sentence description of what the post covers]

### 2. [Post Title]({{< relref "post-slug" >}})

[1-2 sentence description]

### 3. Post Title

[1-2 sentence description — plain text because the post is future-dated]

...

[Optional closing sentence, e.g. "Each post stands alone — start wherever you need."]

Baamaapii
```

**TOC rules:**

| Rule | Detail |
|------|--------|
| Format | Numbered H3 headings, one per post in `series_order` |
| Published posts | Use `relref` links: `[Title]({{< relref "slug" >}})` |
| Future-dated posts | Plain text only — `relref` fails without `--buildFuture` |
| Descriptions | 1-2 sentences per entry describing what the post covers |
| Maintenance | Convert plain text to `relref` links as posts publish |

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

## Facebook

[1–3 sentences hook + link. No strict limit.]

## X (Twitter)

[Short hook, under ~240 chars including URL. Put link at end.]

## LinkedIn

[Professional one-liner or short paragraph + link. Tone fits LinkedIn.]
```

### Platform notes

- **Facebook:** Longer copy is fine. One or two sentences plus the link. Include hashtags. No character limit to target.
- **X (Twitter):** Stay under ~240 characters including the URL so it fits one tweet; put the link at the end.
- **LinkedIn:** One or two sentences, more professional tone; include the link. No hashtags on LinkedIn.

Always include the **canonical URL** in each block so the platform can unfurl it and OG works.

## Accuracy Verification

After writing or updating a post, verify all claims before publishing. Run every check — do not skip items.

| Check | How |
|-------|-----|
| Code blocks compile/run | Verify syntax is correct. If referencing a real repo, read the actual source and confirm the code matches. |
| Tool/product names | Verify tools exist and names are spelled correctly. |
| Links resolve | Internal links: confirm a post with that slug exists. External links: confirm the URL is valid. |
| Behavioral claims | "This does X" or "the output looks like this" — verify against actual behavior by running the command or reading the source. |
| Config/file references | If the post says "add this to Taskfile.yml" or "your lefthook config", verify the file exists and the format matches the real project. |
| State claims | If the post describes something as already implemented ("I wired X into Y"), verify it actually exists in the referenced repo. Do not present aspirational state as current state. |

## Visual Components

The blog has six Hugo shortcodes for breaking up walls of text. Use them when they add information; never use them for decoration. Walls of decoration are worse than walls of text.

Spec and rules: `docs/superpowers/specs/2026-04-06-blog-visual-components-design.md`

| Shortcode | Syntax | Use when | Don't use when |
|-----------|--------|----------|----------------|
| `callout` | `{{</* callout type="info" */>}}body{{</* /callout */>}}` (types: info, warning, tip, note, success) | Asides, gotchas, version notes, prerequisites | General emphasis, decorating prose |
| `steps` | `{{</* steps */>}}` containing `{{</* step "Title" */>}}body{{</* /step */>}}` | Sequential processes with 3+ steps where each step has explanation | Short flat lists, non-sequential items |
| `pullquote` | `{{</* pullquote */>}}line{{</* /pullquote */>}}` | The post's killer line. **Max one per post.** | Decoration, quoting other authors (use `> ` instead) |
| `cta` | `{{</* cta title="..." button="..." href="..." */>}}body{{</* /cta */>}}` | Single concrete action at a meaningful break. **Max one per post.** | Vague "learn more" links, newsletter signup |
| `stats` | `{{</* stats */>}}` containing `{{</* stat "N" "Label" */>}}` | Posts where metrics are central | Posts without real metrics, single-stat scenarios |
| `compare` | `{{</* compare */>}}{{</* before */>}}…{{</* /before */>}}{{</* after */>}}…{{</* /after */>}}{{</* /compare */>}}` | Old way vs new way framings, refactor before/after | Arbitrary contrasts, three-way comparisons |

**Universal rule:** If a component doesn't add information, remove it.

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
| Fabricated code snippets | When a post references real repos, verify every interface signature, method name, and class name against the actual source in `~/dev/`. AI-generated code is frequently hallucinated. |
| Casual/clickbait phrasing | Avoid phrases like "without losing your mind" or "you won't believe". Use direct, professional language. |
| Root-relative internal links | Use `relref`, not `/slug/`. Root-relative paths don't account for the `/blog/` base path and produce 404s. |
| Flat section transitions | Don't end a section and start the next with no pull-through. End with tension, an open question, or a "but" that makes the next heading feel like the answer. |
| Re-explaining the problem after the intro | If the intro establishes why the reader is here, don't spend the next section repeating it. Get to the fix. |
| Documentary announcing pattern | Don't open sections with "Two files do most of the work" or "The template." Lead with what the reader needs to know or a question they need answered, not a table of contents for the section. |
| Adding components for visual interest rather than information | Remove the component. Walls of decoration are worse than walls of text. |
| More than one pullquote or cta per post | Pick the strongest one and delete the rest. Two CTAs means two purposes — split the post. |
| Wordy explanations of visual concepts | If you're writing 3+ sentences to describe a flow, pipeline, or component relationship, replace the prose with a Mermaid diagram. Diagrams communicate structure faster than paragraphs. |
| Naming things without explaining them | Don't drop a class/interface name as a section heading and jump straight to code. Open with 1-2 sentences explaining what it is and why the reader should care. |
| Narrating code instead of showing it | "The method does A, B, and C" followed by a code block that shows A, B, and C. Delete the narration and let the code speak, or fold the explanation into the code as comments. |
| Unverified behavioral claims | "You can't disable the last entity type without a force flag" sounds great but must exist in the actual source. Every claim about what code does must be verified. |
| Repeating "X is not Y, it is Z." style lines | Keep the move if it earns emphasis once. If the draft keeps using that contrast shape, rewrite most of them as direct statements. |
| Flat sentence cadence | If three or four sentences in a row land with the same rhythm, vary the length and structure. A blog post should sound intentional, not metronomic. |
| Generic AI-jargon filler | Replace vague language like "robust," "seamless," "transformative," or "momentum" with the exact behavior, outcome, or tradeoff. |
