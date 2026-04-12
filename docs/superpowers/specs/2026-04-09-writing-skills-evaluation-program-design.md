# Writing Skills Evaluation Program Design

## Goal

Establish a measurable, repeatable evaluation program for all skills in `jonesrussell/skills`, starting with the seven writing skills. Phase 1 builds a baseline and harness before any skill edits. Later phases use that harness to test revisions and then extend the pattern to all remaining skill families.

## Scope

### Phase 1: Writing skills baseline and harness

Skills in scope:

- `blog-writing`
- `blog-reviewing`
- `technical-writing`
- `social-media-posts`
- `substack-writing`
- `film-review`
- `session-to-blog`

Phase 1 measures both:

- Output quality
- Prompt and process behavior

Phase 1 does not change skill content. It creates the system that can measure current behavior, store a baseline, and compare future revisions against that baseline.

### Phase 2: Writing skill revisions and comparative testing

Once the baseline is stable, revise writing skills and re-run the harness to verify improvements or catch regressions. This phase explicitly includes a review of em dash policy and sentence-structure variety, informed in part by Sarah Rearick's April 9, 2026 LinkedIn post about common AI writing tells. That post is treated as a signal and test input, not as sole authority.

### Phase 3+: Remaining skill families

Extend the same evaluation pattern to planning, workflow, review, security, framework, and project-specific skill groups.

## Design Principles

- Repo-native and local-first
- Offline evaluation first, online observation later
- Mixed evaluators, not a single judge
- Baselines are snapshots of current behavior, not statements of ideal quality
- Stable fixtures and versioned evaluators are required before results can be trusted
- Human calibration remains part of the loop

## Research Basis

This design follows current April 2026 evaluation patterns from leading tool and model providers:

- OpenAI guidance on prompt versioning, prompt reuse, and eval-driven prompt iteration
- LangSmith guidance to start with curated offline datasets before online evaluation
- Promptfoo guidance for flexible rubric-based checks, model grading, pairwise comparisons, and exportable result artifacts

## Architecture

### Storage model

Add a first-class evaluation area in this repo, expected to look roughly like:

- `evals/fixtures/` for curated evaluation cases
- `evals/rubrics/` for scoring criteria and evaluator prompts
- `evals/baselines/` for accepted baseline snapshots
- `evals/results/` for timestamped run artifacts
- `evals/scripts/` or an equivalent local CLI entrypoint for repeatable runs
- `docs/` for program guidance, interpretation rules, and rollout notes

Exact file layout can change during implementation, but the repo must store fixtures, rubrics, baselines, and summaries in versioned form.

### Evaluation flow

1. Select a skill and fixture set.
2. Run the skill against a curated offline dataset.
3. Collect raw outputs and any generated artifacts.
4. Apply rule-based checks for hard requirements.
5. Apply rubric-based grading for soft qualities.
6. Run pairwise comparison against the accepted baseline where applicable.
7. Emit machine-readable and human-readable reports.
8. Accept or reject the run as the current baseline according to documented rules.

### Evaluator mix

Use multiple evaluator types:

- Rule-based evaluators
  - Greeting and closing requirements
  - Required structure and headings
  - Output path and artifact correctness
  - Presence or absence of banned patterns
  - Required link style or formatting rules
  - Word count or length bands when the skill requires them
- Rubric-based model evaluators
  - Voice fidelity
  - Clarity
  - Specificity
  - Sentence variety
  - Punctuation restraint and intentionality
  - Compliance with stated style rules
- Pairwise comparison evaluators
  - Compare proposed revisions against baseline outputs on the same fixtures
  - Prefer "better than baseline" or "no meaningful regression" over absolute scoring alone
- Human calibration review
  - Sample a subset of runs to ensure the rubric aligns with actual editorial judgment

## Writing-Skill Rubric

Each writing-skill run should score at least these dimensions:

- Instruction compliance
- Voice fidelity
- Structural compliance
- Specificity and usefulness
- Sentence variety
- Punctuation restraint and intentionality
- Anti-pattern frequency
- Artifact correctness

### Writing-specific anti-pattern signals

The harness should detect overuse signals rather than impose blanket bans. Candidate signals include:

- Frequent em dash usage
- Repetitive contrast constructions such as `X is not Y, it is Z`
- Repeated cadence patterns across paragraphs
- Filler intensifiers and generic marketing language
- Repetitive jargon clusters associated with AI-generated prose

These signals should feed reports and rubrics as indicators of overuse, not hard failures in every case.

## Baseline Definition

The baseline is the accepted measurement snapshot of current skill behavior under a stable fixture corpus and evaluator set.

A trustworthy baseline requires:

- Fixed fixture corpus
- Versioned evaluator prompts and rubric definitions
- Recorded model and tool versions
- Stored raw outputs
- Stored structured scores
- Human-readable summary reports
- Repeat runs where stochasticity could materially affect results

The first accepted baseline is not "the ideal writing standard." It is the control condition for later comparisons.

## Writing Skill Phase Plan

### Phase 1

Build the harness and establish the baseline for all seven writing skills, with implementation priority on:

- `blog-writing`
- `blog-reviewing`
- `technical-writing`

The other four writing skills must still be included in Phase 1 planning and fixture design so the harness does not become overly tailored to blog-only cases.

### Phase 2

Use the harness to guide and validate changes to writing skills. Planned work includes:

- revise skills based on baseline findings
- test any rule or language changes against the baseline
- revisit em dash guidance
- measure sentence-structure variety directly
- compare revised outputs against baseline outputs before accepting changes

### Phase 3+

Roll the same approach out to non-writing skills by family, reusing the harness patterns where possible and only specializing the rubric where necessary.

## GitHub Planning Structure

Use milestone-based planning in `jonesrussell/skills`:

1. `Writing Skills Baseline and Harness`
2. `Writing Skill Revisions and Comparative Testing`
3. `Skill Evaluation Rollout for Remaining Skill Families`

Phase 1 should include issues for:

- program spec and success criteria
- harness architecture and local CLI
- writing fixture corpus
- rule-based evaluators
- rubric-based grading and pairwise comparison
- baseline run and reporting
- CI or local repeatability gates

Phase 2 should include issues for:

- writing-skill revision workflow
- em dash and sentence-variety evaluation policy
- comparative test runs for revised skills

Phase 3 should include issues for:

- family-by-family rollout plan for remaining skills
- generalized harness reuse and rubric specialization

## Success Criteria

Phase 1 is complete when:

- the repo contains a runnable evaluation harness for writing skills
- the harness can execute curated fixtures locally and produce reproducible artifacts
- reports include raw outputs, structured scores, and readable summaries
- an accepted baseline exists for the seven writing skills
- comparative evaluation is ready for future skill revisions

Phase 2 is complete when:

- writing-skill edits are tested against the baseline
- the harness can show whether a change improved, regressed, or maintained quality
- em dash and sentence-variety decisions are encoded as measurable policy, not ad-hoc opinion

Phase 3 is complete incrementally as each remaining skill family is onboarded to the evaluation program.

## Open Questions Deferred to Implementation Planning

- exact harness toolchain and runtime
- exact directory layout under `evals/`
- whether to adopt Promptfoo directly, wrap it, or build a thin repo-native runner around similar concepts
- how much of the evaluation should run in CI versus local-only
- which model providers should be used for rubric grading and pairwise judgment
