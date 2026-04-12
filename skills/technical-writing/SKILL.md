---
name: technical-writing
description: Use when writing or editing non-blog content like documentation, site copy, README files, guides, landing pages, or any technical prose that is not a blog post. Triggers include writing docs, editing site templates, drafting READMEs, or rewriting copy for clarity.
---

# Technical Writing

## Overview

Write technical content (docs, site copy, READMEs, guides) that matches Russell's voice: second person, direct, instructional. This skill covers everything that is NOT a blog post. For blog posts, use the `blog-writing` skill instead.

## When to Use This vs blog-writing

| Content type | Skill |
|---|---|
| Blog posts (Hugo, frontmatter, Ahnii/Baamaapii) | `blog-writing` |
| Documentation guides, site templates, READMEs, landing pages, project descriptions | `technical-writing` (this skill) |

## Voice Rules

| Element | Rule |
|---------|------|
| Voice | Second person, direct, instructional. "You define an entity type" not "Entities are defined." Not corporate "we". |
| Concise | Short sentences. One idea per paragraph. No filler or throat-clearing. |
| Code blocks | Always specify language tag. After each block, add 1-2 sentences explaining what it does or why. |
| Links | Link first mention of products, tools, or projects. |
| Headings | H2 for main sections, H3 for subsections. Descriptive, keyword-rich. "Define Your Entity Type" not "Step 1". No "Wrapping Up" or "Conclusion". |
| Em dashes | Use sparingly and on purpose. Prefer periods (two short sentences), colons, or commas. One or two per file maximum. Zero is fine. |

## What to Avoid

| Mistake | Fix |
|---------|-----|
| Marketing fluff ("powerful", "seamlessly", "robust", "comprehensive") | State what things DO. "Waaseyaa generates CRUD endpoints" not "Waaseyaa provides a powerful API layer." |
| Passive voice | Active, second person. "You write access policies" not "Access policies can be configured." |
| First person | No "I found", "my setup", "we built". Use "you" throughout. |
| Abstract descriptions | Concrete. "43 packages across 7 layers" not "a modular, extensible architecture." |
| Em dash overuse | Heavy "—" usage reads as AI-written. Replace with periods, colons, commas. |
| Formulaic contrast constructions | Don't keep repeating lines like "X is not Y, it is Z." If the point is clear without the contrast move, write the direct sentence. |
| Casual opposition fillers | Avoid low-value "instead of" and "rather than" phrasing when a direct sentence is clearer. Keep contrast for real tradeoffs, not connective tissue. |
| Flat cadence | Vary sentence and paragraph length. Documentation can be plain without sounding mechanically repetitive. |
| Throat-clearing intros | State what the page/section covers in one sentence. No "In this guide, we will explore..." |
| Generic headings | "Check Access in Controllers" not "Checking Access" or "How to Check Access". Use imperative form. |
| "Wrapping Up" / "Conclusion" / "Summary" sections | End naturally. No closing header needed. |
| Unexplained code blocks | After every code block, 1-2 sentences on what it does or why. |
| Time estimates in headings | Don't add reading time or duration estimates. |

## Sentence Style

**Before (generic/corporate):**
> The entity system provides a comprehensive way to manage structured content through a powerful field API.

**After (correct):**
> The entity system is how you manage structured content. You define entity types in code, attach typed fields, and let the framework handle storage and validation.

**Before (passive/abstract):**
> Access control can be configured through policies that are evaluated at the entity level.

**After (correct):**
> You write access policies. The framework evaluates them at both the entity and field level. If no policy grants access, the operation is denied.

**Before (em dash heavy):**
> Waaseyaa — an entity-first framework — rebuilds Drupal's best ideas — entities, fields, typed storage — on modern PHP.

**After (correct):**
> Waaseyaa rebuilds Drupal's best ideas on modern PHP. Entities, fields, typed storage, access policies. No global state, no legacy baggage.

## Structure Patterns

### Documentation Guide

```
# [Descriptive Title]

[One sentence: what this guide covers.]

## [First Concept or Task]

[Short explanation.]

```language
code example
```

[1-2 sentences: what the code does or why.]

## [Next Concept]

[Continue pattern. Short paragraphs, code, explanation.]
```

### Site Page / Landing Copy

```
[Headline]
[One sentence tagline or description. No filler.]

[Section heading]
[2-3 short sentences max. State what it IS, then what it DOES.]

[Section heading]
[Same pattern. Direct, concrete.]
```

### README

```
# Project Name

[One sentence: what it is.]

## Install

```bash
command
```

[What the command does.]

## Usage

[Show the primary use case with code.]

[Explain what the code does.]
```

## Cultural Context

Russell is Anishinaabe. Some project names have Anishinaabemowin origins:
- **Waaseyaa**: "it is bright" or "there is light"
- **Minoo**: "it is good"

Reference these naturally when relevant. Don't over-explain or make them performative. State the meaning once, directly.

## Checklist

Before finishing any technical writing task, verify:

- [ ] Second person throughout (no "we", "I", or passive voice)
- [ ] No more than 1-2 em dashes in the entire file
- [ ] Contrast constructions like "X is not Y, it is Z" are not repeated as a stylistic crutch
- [ ] No marketing fluff words ("powerful", "seamlessly", "robust")
- [ ] Sentence cadence varies enough that the page does not sound mechanically repetitive
- [ ] Every code block has 1-2 sentences of explanation after it
- [ ] Headings are descriptive and keyword-rich (imperative form)
- [ ] No "Wrapping Up", "Conclusion", or "Summary" section
- [ ] Short sentences. One idea per paragraph.
- [ ] First mentions of tools/projects are linked
