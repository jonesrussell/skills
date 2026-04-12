# Writing Skills Phase 2 Revision Design

## Goal

Use the new evaluation harness to guide and validate the first revision pass on the highest-leverage writing skills in `jonesrussell/skills`. This phase revises `blog-writing`, `blog-reviewing`, and `technical-writing` only after extending the eval surface enough to measure the intended style changes.

## Scope

Skills in scope for this phase:

- `blog-writing`
- `blog-reviewing`
- `technical-writing`

Skills explicitly out of scope for this first pass:

- `social-media-posts`
- `substack-writing`
- `film-review`
- `session-to-blog`

Those four stay untouched until the first three are revised and evaluated successfully.

## Objectives

Phase 2 should improve how the skills steer outputs away from repetitive AI-writing habits without flattening the intended voice.

The focus areas are:

- em dash restraint and intentional use
- repetitive contrast constructions such as `X is not Y, it is Z`
- sentence-length and paragraph-cadence variety
- filler and generic AI-jargon cleanup
- preserving legitimate stylistic exceptions where the skill requires them

## Design Principles

- Extend the existing harness instead of redesigning it
- Measure before and after on the same fixture set
- Prefer overuse signals over blanket bans unless the skill already requires a hard rule
- Keep the changes skill-specific rather than applying one generic anti-AI style policy everywhere
- Accept revisions only when comparative evals show improvement or no regression

## Approach Options Considered

### Option 1: Minimal wording pass

Make a few style edits in the three skills and rely mostly on editorial judgment.

Rejected because it is weakly measurable and unlikely to move outputs enough to justify the revision cycle.

### Option 2: Policy-plus-harness pass

Add measurable style policy for em dashes, contrast constructions, cadence variety, and filler patterns in the three priority skills. Extend the harness to surface those signals, then revise the skills and compare against baseline.

Recommended because it is scoped, measurable, and uses the new harness as intended.

### Option 3: Full rubric redesign

Redesign the entire writing-quality rubric and revise all writing skills at once.

Rejected for the first pass because it expands the change surface too far and makes regressions harder to interpret.

## Recommended Design

### 1. Extend the eval surface first

Before editing any skill text:

- add anti-pattern signals to the rubric or reporting layer
- add fixtures likely to trigger repetitive contrast structures, punctuation habits, and flat cadence
- make those signals visible enough in reports to compare baseline versus revised skills

The harness should be able to answer:

- did em dash overuse decrease?
- did repetitive contrast constructions decrease?
- did sentence and paragraph variety improve?
- did the changes damage clarity, voice, or structure?

### 2. Revise only the first three skills

Update `blog-writing`, `blog-reviewing`, and `technical-writing` to encode the intended policy clearly.

The revisions should:

- tighten style rules without overfitting into fragile bans
- distinguish forbidden patterns from overused patterns
- preserve instructional clarity and voice
- make review guidance more explicit where the reviewing skill should detect overuse rather than prohibit the pattern entirely

### 3. Validate with comparative evals

Run the revised skills against the same fixtures used for the baseline.

Acceptance rule:

- improvement is preferred
- no meaningful regression is acceptable
- regressions block acceptance until resolved

## Policy Direction By Skill

### `blog-writing`

- Em dashes remain allowed, but explicitly sparse and intentional
- Contrast constructions like `X is not Y, it is Z` should be treated as easy-to-overuse, not forbidden
- Sentence and paragraph variety should be stated as a positive requirement, not just an anti-pattern warning
- Filler, generic emphasis, and repetitive cadence should be called out more directly than they are now

### `blog-reviewing`

- The skill should review for overuse patterns, not blanket-prohibit them
- Findings should distinguish between occasional intentional use and patterned repetition
- The review checklist should explicitly inspect cadence, contrast-pattern repetition, and punctuation overreliance

### `technical-writing`

- Em dashes remain allowed but restrained
- Stronger guidance should push toward direct statements, varied sentence starts, and low-jargon prose
- Anti-patterns should be framed in practical editorial terms, not generic “avoid AI style” language

## Sarah Rearick Signal

Sarah Rearick's April 9, 2026 LinkedIn post is treated as an input signal for this phase, not a complete authority.

What it contributes here:

- overused em dashes can function as an AI tell
- repetitive `X is not Y, it is Z` constructions are common enough to merit explicit attention
- the real issue is repetitive structure and punctuation habits, not the existence of any one device

How it should be encoded:

- `substack-writing` keeps its existing hard “no em dash” rule, but that is outside this phase
- `blog-writing` and `technical-writing` continue to allow em dashes sparingly
- `blog-reviewing` evaluates overuse patterns rather than enforcing a blanket ban
- contrast constructions become an overuse signal in evaluation and guidance, not a universal prohibition

## Evaluation Additions Needed

This phase likely needs additions in the eval harness such as:

- anti-pattern counters or signals for common contrast constructions
- punctuation-frequency reporting
- sentence-length and paragraph-length distribution summaries
- report output that makes “samey” cadence visible enough to compare

These additions should remain heuristic and review-oriented unless there is a strong reason to hard-gate them.

## Success Criteria

Phase 2 is successful when:

- the harness can surface the targeted anti-patterns clearly
- the three revised skills express the intended policy in a stable, usable way
- comparative evals show improvement or no regression against the accepted baseline
- the result is concrete enough to roll out the same ideas to the remaining four writing skills later

## Risks

- over-correcting into rigid anti-pattern bans that flatten useful style
- making the skills more complicated without materially changing outputs
- teaching the harness to reward shallow variety instead of better writing
- broadening scope into all seven writing skills before the first revision loop stabilizes

## Out of Scope

- revising the remaining four writing skills in this pass
- redesigning the full writing-quality rubric from scratch
- changing non-writing skills
- changing the baseline acceptance model itself
