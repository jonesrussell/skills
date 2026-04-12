# Skill Eval Storage

This directory holds local evaluation data for the writing skills harness.

You keep the harness local and deterministic. It uses Python stdlib only, reads versioned fixtures and rubrics from this tree, uses `tests/fixtures/evals/mock_outputs.json` for the default mock runner, and writes disposable smoke output to `results/`.

## Layout

- `fixtures/` stores curated input cases for each skill. These files are versioned because they define the repeatable test corpus.
- `rubrics/` stores shared rubric metadata used by the evaluator. These files are versioned because they define scoring behavior.
- `baselines/` stores accepted baseline runs copied from approved candidate runs. The promoted `run.json` and `summary.md` are versioned together with the fixture and rubric revisions they were created from.
- `results/` stores local run output and smoke-test artifacts. Treat it as scratch space; only the placeholder `.gitkeep` is versioned and everything else in the directory is ignored.

Keep the files small and deterministic. The harness is meant to run locally without network access.

## Run A Local Smoke Test

You run a quick check from the repo root:

```bash
python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/local-smoke
```

That command writes `evals/results/local-smoke/run.json` and `evals/results/local-smoke/summary.md`. Use the mock runner for smoke tests when you want stable output without an external command.

When you want to measure actual skill behavior, run a narrowed Codex eval:

```bash
python3 scripts/eval_skills.py run --suite writing --runner codex --skill technical-writing --case-id doc_page_happy_path --output-dir evals/results/codex-smoke
```

The `--skill` and `--case-id` filters matter because live runs are more expensive than mock runs.

## Promote A Baseline

You promote a candidate run only after you review the output and want to keep it as the accepted reference:

```bash
python3 scripts/eval_skills.py promote-baseline --candidate evals/results/local-smoke --baseline evals/baselines/writing/v1
```

Promotion copies the full candidate directory into `evals/baselines/writing/v1/`, so `run.json`, `summary.md`, and any supporting artifacts stay together. For the naming and eligibility rules, see [`baselines/README.md`](baselines/README.md).

## Follow Runner Expectations

The harness accepts three runner modes:

- `mock` loads `tests/fixtures/evals/mock_outputs.json` and is the right choice for local smoke tests.
- `codex` uses the local `codex exec` CLI to run the real skill file against the selected fixture prompt in read-only mode.
- `command` runs one external command per case, passes the case and metadata on stdin as JSON, and expects a JSON object on stdout.

All runners record run metadata in `run.json`. That metadata is what lets you compare a candidate against a baseline and decide whether the change is a regression, an improvement, or no regression.

The documented smoke workflow exercises the `mock` runner path. The `codex` runner path requires a working local Codex CLI login. The generic `command` runner path is covered by the unit test suite unless you supply a real external command for manual checking.

## Run Metadata

Each `run.json` written by the harness includes a `metadata` block with:

- `runner`
- `fixture_version`
- `rubric_version`
- `generated_at`
- `command` when the runner has a command to record

That metadata is what makes a run repeatable and eligible for baseline promotion. A candidate run should only be promoted after it includes this metadata block and passes the suite checks you want preserved as a new baseline.
