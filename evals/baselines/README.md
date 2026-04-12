# Baselines

This directory stores accepted evaluation runs.

Use a baseline only after you have reviewed the candidate run and confirmed the results are stable.

The `writing/` subdirectory is reserved for the writing-skill suite.

## Promotion Rules

A candidate run is eligible for promotion when:

- `run.json` exists in the candidate directory.
- `run.json` contains a `metadata` block.
- The metadata records `runner`, `fixture_version`, `rubric_version`, and `generated_at`.
- The candidate was produced from the fixture and rubric versions you want to preserve as the baseline.

When a run is promoted, copy the whole candidate directory into `evals/baselines/<suite>/<name>/` so the `run.json`, `summary.md`, and any supporting artifacts stay together.

## Naming

Keep baseline directories stable and versioned by promotion order, for example `v1`, `v2`, or a date stamp like `2026-04-09`. Repeatable smoke runs belong under `evals/results/` instead of `evals/baselines/`.

## Ignored Output

Generated smoke runs and scratch outputs stay out of version control. Only the baseline tree and placeholder files are tracked.
