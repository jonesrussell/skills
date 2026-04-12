---
name: film-review
description: "Use this skill when writing movie reviews for movies-of-war.com. Triggers include requests to review a war film, draft a review from notes, or help structure movie analysis. The skill captures Russell's personal reviewing style influenced by Roger Ebert — conversational authority, specific observations, honest criticism, and a focus on military history."
---

# War Movie Review Writing

## Overview

This skill produces movie reviews for movies-of-war.com in Russell's established voice and style. Reviews should feel like a knowledgeable friend explaining why a film did or didn't work, not academic film criticism.

## Rating System

Use a 4-star scale (Ebert style):

| Rating | Meaning |
|--------|---------|
| ★★★★ | Essential viewing, achieves what it sets out to do excellently |
| ★★★ | Good film, worth watching, minor flaws |
| ★★ | Mixed — interesting elements but significant problems |
| ★ | Poor — fails at its core goals |

Display as: `★★` or `★★★½` (half-stars acceptable)

## Voice & Tone

**Do:**
- Write with conversational authority — state opinions directly, not hedged
- Lead with a thesis about what the film is trying to do and whether it succeeds
- Use specific scenes as evidence, not vague praise ("the codebreaking bunker scene works because...")
- Be honest about flaws without being cruel
- Acknowledge what works even in weak films
- Note when a film inspires further historical research (this is a positive)
- Make casual comparisons to other war films when useful
- Keep it concise — aim for 400-600 words, not 1000+
- Use em dashes sparingly and on purpose. Zero is fine. Heavy "—" usage reads AI-written and weakens the cadence.
- Vary sentence rhythm. A review can be sharp and direct without every sentence landing the same way.
- Avoid double-negative contrast turns like "does not X, but it also does not Y." Write the direct sentence instead.
- Avoid casual opposition fillers like "rather than" or "instead of" when a plain descriptive sentence is stronger. Save contrast for real analytical weight.

**Don't:**
- Use academic film jargon
- Hedge every opinion ("some viewers might feel...")
- List plot points without analysis
- Over-explain historical context (readers are war history enthusiasts)
- Pad with generic praise or filler
- Lean on formulaic contrasts such as "X is not Y, it is Z." Once may work. Repetition reads formulaic and AI-written. If the point lands better as a direct sentence, write the direct sentence.

## Structure

```markdown
# [Title] ([Year]): [Star Rating]

*Directed by [Director]. Starring [Top 3-4 Cast]. [Runtime].*

---

[Opening paragraph: Thesis about what the film attempts and whether it succeeds. Set expectations.]

[Body paragraphs: Specific observations organized by what works and what doesn't. Use scenes as evidence. Address: character work, historical authenticity, combat sequences, pacing, emotional engagement.]

[Closing: Final verdict, who would enjoy it, rewatch value. If the film sparked historical curiosity, mention it as a genuine positive.]

[Star rating repeated at bottom]
```

## Key Review Elements for War Films

Always address these (not as a checklist, weave naturally):

1. **Historical authenticity** — Does it respect the history? Note obvious liberties.
2. **Character vs. spectacle balance** — Can you care about the people, or are they chess pieces?
3. **Combat sequences** — Clarity, tension, pacing. Do you understand what's happening tactically?
4. **The film's perspective on war** — Glorifying? Critical? Neutral procedural?
5. **Technical choices** — Practical effects, archival footage, period details worth noting.
6. **Emotional engagement** — Did key moments land or fall flat?

## Spoiler Policy

- Films 25+ years old: Spoilers are fine, discuss openly
- Recent films: Warn before major plot reveals
- Historical events: The history itself isn't a spoiler (everyone knows how Midway ended)

## Note-Taking Process

When reviewing from raw notes:
- Extract the specific observations (scene details, dialogue, reactions)
- Identify the throughline (what's the main critique or praise?)
- Don't try to use everything — pick the strongest evidence
- Messy notes are fine; the review should be polished

## Example Opening Lines

Strong openings that establish a thesis:

> "Midway" wants to be two things at once and never fully commits to either.

> "Saving Private Ryan" earns its reputation in two sequences and coasts on goodwill for the rest.

> The problem with "Pearl Harbor" is not the history. Michael Bay thinks the love triangle is more interesting than the war.

## Comparisons

When comparing films (e.g., 1976 Midway vs. 2019 Midway):
- Keep it brief unless writing a dedicated comparison piece
- Focus on what each does differently, not which is "better"
- Link to the other review if it exists on the site

## Output Format

- Markdown for the site
- Use `---` horizontal rule after the metadata line
- Star rating in heading AND at bottom
- Use a colon in the heading before the star rating. Avoid an em dash there.
- Keep paragraphs readable (4-6 sentences max)

## Dependencies

None — plain markdown output for movies-of-war.com
