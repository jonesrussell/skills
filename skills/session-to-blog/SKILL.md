---
name: session-to-blog
description: Use when a Claude Code session produced interesting work worth writing about, or when the user asks to generate a blog post from the current session. Also triggers at session end to offer drafting. Generates Hugo-compatible draft posts in the user's blog repo.
---

# Session to Blog Post

## Overview

Extracts blogworthy moments from a Claude Code session and generates Hugo-compatible draft posts. Avoids topics already well covered in the existing blog.

## When to Use

- User says "write a blog post about this", "draft a post", or invokes `/session-to-blog`
- At session end when substantial, novel work was completed
- When a session involved solving a non-trivial problem with a reusable lesson

## When NOT to Use

- Trivial bug fixes or config changes
- Work that's confidential or not shareable
- Topics already thoroughly covered (check existing posts first)

## Blog Configuration

- **Engine:** Hugo
- **Repo:** `/home/fsd42/dev/blog/`
- **Content:** `content/posts/<category>/`
- **Categories:** `ai`, `go`, `laravel`, `docker`, `devops`, `general`, `cursor`, `psr`
- **Front matter:** YAML
- **Draft convention:** `draft: true`

## Process

### Step 1: Identify Blogworthy Topics

Review the session for:
- **Problem → Solution arcs** — debugging sessions, architectural decisions, clever fixes
- **New patterns discovered** — reusable techniques, framework patterns, tool workflows
- **Migration/integration stories** — porting between frameworks, wiring systems together
- **Tool/workflow insights** — Claude Code usage patterns, skill creation, automation

Rate each topic on two axes:
- **Novelty** — would this teach the reader something they can't easily Google?
- **Reusability** — would this help someone facing a similar situation?

Skip topics that score low on both.

### Step 2: Check for Overlap

Before drafting, scan existing blog posts for overlap:

```bash
ls /home/fsd42/dev/blog/content/posts/*/
grep -rl "<keyword>" /home/fsd42/dev/blog/content/posts/
```

**Well-covered topics to avoid unless you have a genuinely new angle:**
- PSR standards (15 posts — comprehensive)
- Docker fundamentals (7 posts)
- Laravel/DDEV local dev setup (5 posts)
- Codified context basics (5-post series)
- Waaseyaa framework architecture (10-post series)

**Growth areas welcome:**
- Advanced Go patterns, testing strategies
- Kubernetes/orchestration
- Database optimization
- Real-world migration stories (Laravel → Waaseyaa is fresh)
- AI-assisted development workflows (practical, not hype)

### Step 3: Generate Draft Post

Create the post file at the correct path:

```
content/posts/<category>/<slug>/index.md
```

**Front matter template:**
```yaml
---
title: "<Title — specific, actionable, not clickbait>"
date: <YYYY-MM-DD>
categories: [<primary-category>]
tags: [<tag1>, <tag2>, <tag3>]
summary: "<One sentence — what the reader will learn>"
slug: "<url-slug>"
draft: true
---
```

**Writing style:**
- First person, conversational, technical
- Lead with the problem or context, not the solution
- Show real code from the session (sanitize secrets/paths)
- Include "what I tried first" when there was a wrong turn — readers learn from the debugging journey
- End with a takeaway or "what I'd do differently"
- Target 800-1500 words — respect the reader's time
- No filler paragraphs, no "in this post we'll explore..."

**Structure:**
```markdown
## The Problem / Context
(2-3 sentences setting the scene)

## What I Tried / The Approach
(Show the work — code, decisions, trade-offs)

## The Solution
(Working code with explanation)

## What I Learned
(Key takeaway, gotchas, things to watch for)
```

### Step 4: Offer to the User

After generating, tell the user:
- What post(s) were created
- The file path(s)
- A one-line summary of each
- Remind them to review and remove `draft: true` when ready to publish

## Multiple Posts

If a session covers multiple distinct topics, generate separate posts. One focused post beats one rambling mega-post.

## Session-End Trigger

When a session involved substantial work (3+ commits, new features, debugging victories), and the skill hasn't been invoked yet, offer:

> "This session had some interesting work — [brief description]. Want me to draft a blog post about it?"

Only offer once per session. Accept "no" gracefully.

## Quick Reference

| Field | Value |
|-------|-------|
| Blog path | `/home/fsd42/dev/blog/content/posts/<category>/` |
| Front matter | YAML (`---` delimiters) |
| Draft flag | `draft: true` |
| Categories | ai, go, laravel, docker, devops, general, cursor, psr |
| Word target | 800-1500 |
| Post structure | Problem → Approach → Solution → Takeaway |
