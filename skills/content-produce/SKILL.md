---
name: content-produce
description: Draft a Hugo blog post and accompanying social copy from a curated content queue issue. Use when a content queue item is ready for writing, or when user says "produce", "write the post", "draft this".
---

# Content Production

## Overview

Turn a `stage:curated` content queue issue into a full Hugo blog draft plus companion social copy. The blog post is the canonical source of truth — the social copy links back to it. Nothing gets published automatically. The user flips `draft: false` manually when the post is ready to go live.

## Prerequisites

- Blog repo: `/home/jones/dev/blog` (Hugo + PaperMod, deployed to `https://jonesrussell.github.io/blog/`)
- Blog style guide: `/home/jones/dev/blog/docs/blog-style.md`
- Reference post for voice/structure: `/home/jones/dev/blog/content/posts/laravel/laravel-boost-ddev/index.md`
- Brand voice: `~/brand/identity.md`
- Social copy convention: `docs/social/{slug}.md` in the blog repo (consumed later by `/content-pipeline`)

## Process

### 1. Identify the issue

User provides an issue number or find curated issues:

```bash
gh issue list --repo jonesrussell/jonesrussell --label "stage:curated" --json number,title
```

Read the issue body. Extract:
- Content seed (the raw material and context)
- Source (commit SHAs, closed issues, repos referenced)
- Channels (which social platforms will eventually get copy)

### 2. Pick the slug (SEO-aware)

Slugs are permanent. Get them right the first time.

Rules:
- **3–6 words.** Short enough to read, long enough to be descriptive.
- **Primary keyword first.** What would someone search for?
- **Kebab-case, lowercase.** ASCII only.
- **No stopwords** (a, the, and, of, in, to, for) unless removing them breaks meaning.
- **No dates, no numbers** unless they're part of the identity (e.g., `psr-7-http-message-interfaces`).
- **No clickbait verbs** ("how-i-shipped", "the-story-of"). Lead with the noun.
- **Check collision:** `ls /home/jones/dev/blog/content/posts/**/` to make sure the slug isn't already taken.

Examples, keyword-first:

| Seed | Bad slug | Good slug |
|------|----------|-----------|
| Built a content pipeline on my personal repo | `how-i-built-a-content-pipeline` | `github-content-pipeline-claude-code` |
| Swapped custom HttpResponse for Symfony Response in Waaseyaa | `using-symfony-response` | `waaseyaa-symfony-response-migration` |
| Giiken — community knowledge management on Waaseyaa | `giiken-story` | `giiken-community-knowledge-management` |

### 3. Pick the category

Use the existing category directories under `content/posts/`:

| Category | Use for |
|----------|---------|
| `ai/` | Claude Code workflows, AI-assisted development, agent systems, Waaseyaa framework, Giiken, Claudriel |
| `devops/` | Servers, Ansible, SSH, monitoring, backup, networking, shell tooling |
| `docker/` | Docker, Dockerfile, containers, whalebrew |
| `go/` | Go language, interfaces, testing, Bubble Tea, struct alignment |
| `laravel/` | Laravel, DDEV, Drupal-adjacent |
| `psr/` | PSR standards (reserved for the PSR series) |
| `cursor/` | Cursor IDE |
| `general/` | Career, imposter syndrome, tool roundups, meta-posts about writing or the blog itself |

If the post doesn't cleanly fit, pick the closest and move on — don't invent new categories.

### 4. Create the post skeleton

```bash
cd /home/jones/dev/blog
task new-post -- <slug>
```

This creates `content/posts/<slug>/index.md` with the archetype applied. Move it into the right category directory:

```bash
mkdir -p content/posts/<category>
mv content/posts/<slug> content/posts/<category>/<slug>
```

### 5. Fill in the front matter

Set these fields (keep `draft: true` — never flip it):

```yaml
---
title: "Sentence case, descriptive"
date: YYYY-MM-DD
categories: [ai]        # or whichever, single value usually
tags: [claude-code, waaseyaa, hugo]   # max 4
summary: "One sentence: what the reader gets or who it's for."
slug: "slug-from-step-2"
draft: true
---
```

Today's date from the environment. Tags are keywords a reader would filter by, not every noun in the post. Summary is the hook that shows on index pages.

### 6. Write the post

Follow the blog-style.md conventions:

- **Open with "Ahnii!"** on its own line
- **Prerequisites line** (bold "Prerequisites:" blockquote) when relevant — versions, tools, background knowledge
- **One-paragraph intro:** what this post is about + one sentence on scope
- **H2 sections** for the main body. H3 for variants inside a section.
- **After every code block**, one or two sentences explaining what it does or why it matters
- **Second person, direct**, reader-focused ("your project", "you can")
- **Link the first mention** of products/projects (e.g., `[Hugo](https://gohugo.io/)`, `[Claude Code](https://claude.com/claude-code)`)
- **Close with "Baamaapii"** on its own line

**CRITICAL: verify code snippets against source repos.** This is a documented rule in the blog CLAUDE.md. Interface signatures, method names, class names, and file paths are frequently hallucinated. Before writing any code block, read the actual file in `~/dev/<repo>/` and copy from there. Never invent.

Length target: match similar posts in the same category. The `ai/` posts tend to run 800–1500 words. Shorter is fine if the material is tight.

### 7. Draft the social copy file

Invoke `social-media-posts` before writing a single word of copy. That skill defines the authoritative platform rules (X char limits, hashtag policy, GitHub link requirements, voice). Do not reproduce those rules here — follow the skill directly.

Save the output to `docs/social/<slug>.md` in the blog repo. The format that `/content-pipeline` expects:

```markdown
# <Post title>

Blog URL: https://jonesrussell.github.io/blog/<slug>/

## Facebook

<copy>

## X

<copy>

## LinkedIn

<copy>
```

### 8. Show both drafts for review

Present:
1. The blog post front matter + a summary of sections + any code blocks that need verification
2. Full social copy for all three platforms

Ask: "Approve, edit, or hold?"

### 9. On approval: commit to the blog repo

```bash
cd /home/jones/dev/blog
git add content/posts/<category>/<slug>/ docs/social/<slug>.md
git commit -m "$(cat <<'EOF'
Draft: <Post title>

From content queue issue #<NUMBER>.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

**Do not push.** User decides when to push. Do not flip `draft: false`.

### 10. Update the queue issue

Append to the issue body's "Generated Artifacts" section and move the label:

```bash
gh issue edit <NUMBER> --repo jonesrussell/jonesrussell --body "<updated body>"
gh issue edit <NUMBER> --repo jonesrussell/jonesrussell --remove-label "stage:curated" --add-label "stage:ready"
```

The updated Generated Artifacts section should include:
- Blog draft path: `content/posts/<category>/<slug>/index.md`
- Social copy path: `docs/social/<slug>.md`
- Target URL: `https://jonesrussell.github.io/blog/<slug>/`
- Status: "Draft committed to blog repo. Flip `draft: false` to publish."

## Handoff

After this skill runs, the user's workflow is:
1. Review the committed draft locally (`task serve` in the blog repo)
2. Edit as needed
3. Flip `draft: false` and push — GitHub Actions deploys
4. Run `/content-pipeline` to distribute the social copy via Buffer

## What This Skill Does Not Do

- Does not push to the blog repo
- Does not flip `draft: false`
- Does not post to Buffer (that's `/content-pipeline`)
- Does not invent code snippets — always verify against source repos
- Does not create new categories — use what exists
