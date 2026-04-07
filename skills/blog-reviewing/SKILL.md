---
name: blog-reviewing
description: Use when reviewing, auditing, or preparing blog posts for publication. Triggers include checking post consistency, reviewing drafts, or auditing all posts against blog standards.
---

# Blog Reviewing

## Overview

Systematically audit blog posts against the canonical style rules defined in the blog-writing skill. Every review follows the same checklist — no ad-hoc exploration.

**Canonical authority:** The style rules in `.claude/skills/blog-writing/SKILL.md` and `docs/blog-style.md` are the source of truth. Read both before reviewing. Reference post: `content/posts/laravel-boost-ddev.md`.

## Review Process

1. Read the blog-writing skill and `docs/blog-style.md` to load current rules
2. Identify the post type (series or general) from frontmatter `series` field
3. Run through the checklist below in order
4. Report findings using the standard format
5. **Auto-generate social copy if missing** — if `docs/social/{slug}.md` does not exist, generate it now using the Social media artifact rules in the blog-writing skill. Do not just flag it as MISSING and move on.

## Checklist

Run every check. Do not skip items.

### Frontmatter

- [ ] `title` present, sentence case, descriptive
- [ ] `date` in YYYY-MM-DD format
- [ ] `categories` present, lowercase, hyphenated for multi-word
- [ ] `tags` present, **max 4**
- [ ] `summary` field used (not `description`). One sentence: outcome or audience.
- [ ] `slug` present, kebab-case
- [ ] `draft` field present
- [ ] **Series posts only:** `series` field present with correct series name

### Structure

- [ ] Opens with "Ahnii!" (exclamation mark, own paragraph)
- [ ] Closes with "Baamaapii" (no emoji, own paragraph)
- [ ] Intro states what the post covers in one sentence (scoped)
- [ ] Intro covers the relevant W's: **What** (what the reader learns), **Why** (why it matters or what problem it solves), **Who** (who it's for, if not obvious from context). Not all W's are required — use judgment based on post type.
- [ ] No "Wrapping Up" or "Conclusion" heading
- [ ] No time estimates in section headings
- [ ] Heading hierarchy: H2 for main sections, H3 for variants/subsections
- [ ] Prerequisites section (bullet list) when relevant

### Series Index Structure (only if `series_order: 0`)

- [ ] `series_order: 0` in frontmatter
- [ ] 1-2 sentence intro stating what the series covers and who it's for
- [ ] Numbered H3 TOC listing every post in the series
- [ ] Published posts (date <= today) use `relref` links
- [ ] Future-dated posts use plain text titles (no `relref`)
- [ ] Each TOC entry has 1-2 sentence description
- [ ] TOC order matches `series_order` values across the series

### Series Post Structure (only if `series` field exists and `series_order` > 0)

- [ ] Prerequisites blockquote after greeting
- [ ] Problem statement section
- [ ] Core concepts/interfaces section with code
- [ ] Real-world implementation section
- [ ] Common mistakes section with bad/good code pairs
- [ ] Framework integration section
- [ ] Try it yourself section with companion repo commands
- [ ] What's next section linking to next post in series

### Series Consistency (only if `series` field exists)

- [ ] "Part N" references in body text match `series_order` in frontmatter
- [ ] "Next" teaser points to the correct next post (by `series_order`, not by topic similarity)
- [ ] "Next" link uses `relref` (or plain text if the target post is future-dated)
- [ ] No duplicate dates with other posts in the same series
- [ ] Series index post (`series_order: 0`) exists and lists all posts in the series

### Content

- [ ] All code blocks have language tags
- [ ] After each code block: 1-2 sentences explaining what it does or why
- [ ] First mention of products/tools/projects is linked
- [ ] Internal links use `relref` shortcode (e.g., `{{< relref "post-slug" >}}`), not root-relative paths
- [ ] External links use full HTTPS URLs
- [ ] Voice is second person, direct, instructional ("you"/"your", not "I"/"my")
- [ ] Concise: short sentences, one idea per paragraph, no filler
- [ ] Em dashes used sparingly (one or two per post max; zero is fine)
- [ ] Headings are SEO-friendly with keywords (not generic like "The Problem" or "The Full Picture")
- [ ] Tags match post content (every tag should be substantiated in the body)

### Visual Components

- [ ] Numbered lists with 3+ items where each item has explanatory content → suggest `steps` shortcode
- [ ] Inline link CTAs at the end of a project-showcase post → suggest `cta` shortcode
- [ ] Asides or warnings written as bare paragraphs → suggest `callout` shortcode
- [ ] More than one `pullquote` shortcode per post → flag as INCORRECT (max one per post)
- [ ] More than one `cta` shortcode per post → flag as INCORRECT (max one per post)
- [ ] Component used decoratively without adding information → flag as INCORRECT (walls of decoration are worse than walls of text)
- [ ] `compare` used for non-before/after contrasts → flag as INCORRECT (use a markdown table instead)
- [ ] `stats` used in a post without real metrics → flag as INCORRECT (don't invent numbers)

## Findings Format

Report each finding as:

```
**[CATEGORY]** Line N: description
  Fix: exact correction
```

**Categories:**
- **MISSING** — Required element is absent
- **INCORRECT** — Element exists but violates a rule
- **SUGGESTION** — Not a rule violation, but would improve the post

Always include the line number and a specific fix. Do not report findings without both.

**Example:**
```
**MISSING** Line 50: No farewell. Post ends without "Baamaapii"
  Fix: Add "Baamaapii" as the final line, on its own paragraph

**INCORRECT** Line 13: Greeting uses comma ("Ahnii,") instead of exclamation mark
  Fix: Change "Ahnii," to "Ahnii!"

**INCORRECT** Line 102: Farewell has emoji ("Baamaapii 👋")
  Fix: Change to "Baamaapii" — no emoji
```

### Accuracy

- [ ] All code blocks are syntactically correct
- [ ] Code referencing specific projects matches actual source in that repo
- [ ] Tool/product names are correct and current
- [ ] Internal links have matching slugs that exist
- [ ] External links use valid HTTPS URLs
- [ ] Behavioral claims ("this does X", "the output looks like") are verifiable
- [ ] Config/file references match actual state in referenced repos
- [ ] No aspirational state presented as current state
- [ ] Code referencing repos in `~/dev/` has been verified against the actual source (AI-generated interface signatures, method names, and class names are frequently hallucinated)

### Social Media Artifact

- [ ] Companion file exists at `docs/social/{slug}.md` — **if missing, generate it now** (do not flag and skip)
- [ ] Canonical URL present and correct (`https://jonesrussell.github.io/blog/{slug}/`)
- [ ] Facebook: 1-3 sentence hook + link + hashtags
- [ ] X (Twitter): under ~240 characters including URL, link at end
- [ ] LinkedIn: professional tone, no hashtags, link included
- [ ] All platform blocks include the canonical URL

## Self-Improving Audit Loop

After completing a review, check whether any finding was **not already covered** by an existing checklist item or common mistakes entry. If so:

1. Add the new check to the appropriate skill file:
   - New checklist item → `~/dev/skills/skills/blog-reviewing/SKILL.md`
   - New common mistake → `~/dev/skills/skills/blog-writing/SKILL.md` (Common Mistakes table)
   - New style rule → both files as appropriate
2. Sync the updated skill to the installed copy at `~/.claude/skills/blog-*/SKILL.md`
3. The PR review process on the `~/dev/skills/` repo is the human gate for accepting or rejecting new rules

This ensures every review session that discovers a gap automatically improves future reviews.

## Batch Mode

When asked to review multiple posts:

1. List all target posts (e.g., all drafts: `grep -rl "draft: true" content/posts/`)
2. Identify each post's type (series vs general)
3. Review each post against the checklist
4. Group findings by post with a summary count

**Output format for batch:**
```
## [post-slug.md] — [N findings: X missing, Y incorrect, Z suggestions]
[findings]

## [post-slug.md] — [N findings: ...]
[findings]
```

