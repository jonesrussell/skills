# Writing Skills Eval Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repo-native, local-first evaluation harness that can run curated writing-skill fixtures, score outputs with rule checks and rubric metadata, store a named baseline, and compare future revisions against that baseline before any writing-skill edits are made.

**Architecture:** Use Python stdlib to avoid adding a new runtime to `jonesrussell/skills`. Store fixtures, rubrics, baselines, and run artifacts in a new `evals/` tree. Implement a small Python package under `scripts/skill_evals/` plus an entrypoint script at `scripts/eval_skills.py`. Use a provider-agnostic command runner for live execution and a mock runner for tests so the harness is fully testable without network access.

**Tech Stack:** Python 3 stdlib, JSON fixtures/rubrics/results, `unittest`, repo-local CLI via `python3`

---

### File Structure

**Create:**
- `evals/README.md`
- `evals/fixtures/writing/blog-writing.json`
- `evals/fixtures/writing/blog-reviewing.json`
- `evals/fixtures/writing/technical-writing.json`
- `evals/fixtures/writing/social-media-posts.json`
- `evals/fixtures/writing/substack-writing.json`
- `evals/fixtures/writing/film-review.json`
- `evals/fixtures/writing/session-to-blog.json`
- `evals/rubrics/writing-quality.json`
- `evals/rubrics/process-behavior.json`
- `evals/baselines/README.md`
- `evals/baselines/writing/.gitkeep`
- `evals/results/.gitkeep`
- `scripts/eval_skills.py`
- `scripts/skill_evals/__init__.py`
- `scripts/skill_evals/models.py`
- `scripts/skill_evals/fixtures.py`
- `scripts/skill_evals/runners.py`
- `scripts/skill_evals/rules.py`
- `scripts/skill_evals/comparison.py`
- `scripts/skill_evals/reporting.py`
- `scripts/skill_evals/cli.py`
- `tests/test_skill_evals_models.py`
- `tests/test_skill_evals_fixtures.py`
- `tests/test_skill_evals_rules.py`
- `tests/test_skill_evals_comparison.py`
- `tests/test_skill_evals_cli.py`
- `tests/fixtures/evals/mock_outputs.json`

**Modify:**
- `.gitignore`
- `README.md`

### Task 1: Scaffold Eval Storage and Data Contracts

**Files:**
- Create: `evals/README.md`
- Create: `evals/fixtures/writing/*.json`
- Create: `evals/rubrics/writing-quality.json`
- Create: `evals/rubrics/process-behavior.json`
- Create: `evals/baselines/README.md`
- Create: `evals/baselines/writing/.gitkeep`
- Create: `evals/results/.gitkeep`
- Create: `scripts/skill_evals/models.py`
- Test: `tests/test_skill_evals_models.py`
- Test: `tests/test_skill_evals_fixtures.py`

- [ ] **Step 1: Write failing tests for fixture and result schemas**

```python
import unittest

from scripts.skill_evals.models import EvalFixture, FixtureValidationError


class EvalFixtureSchemaTest(unittest.TestCase):
    def test_requires_at_least_one_case(self) -> None:
        with self.assertRaises(FixtureValidationError):
            EvalFixture.from_dict({"skill": "blog-writing", "cases": []})
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_models tests.test_skill_evals_fixtures -v`

Expected: `ModuleNotFoundError` or schema-constructor failures because the models and fixture loader do not exist yet.

- [ ] **Step 3: Implement minimal schema and fixture loading**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt: str
    expected_artifact: str


@dataclass(frozen=True)
class EvalFixture:
    skill: str
    cases: list[EvalCase]

    @classmethod
    def from_dict(cls, data: dict) -> "EvalFixture":
        cases = [EvalCase(**case) for case in data.get("cases", [])]
        if not data.get("skill") or not cases:
            raise FixtureValidationError("fixture requires skill and at least one case")
        return cls(skill=data["skill"], cases=cases)
```

- [ ] **Step 4: Add initial fixture and rubric JSON files for all seven writing skills**

```json
{
  "skill": "blog-writing",
  "suite": "writing",
  "cases": [
    {
      "case_id": "general_howto_happy_path",
      "prompt": "Draft a blog post about a local development workflow.",
      "expected_artifact": "markdown_document",
      "rubric_targets": ["instruction_compliance", "voice_fidelity", "sentence_variety"]
    }
  ]
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_models tests.test_skill_evals_fixtures -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add evals scripts/skill_evals/models.py tests/test_skill_evals_models.py tests/test_skill_evals_fixtures.py
git commit -m "feat: add eval fixture and result schemas"
```

### Task 2: Build the Harness Core and Runner Interface

**Files:**
- Create: `scripts/skill_evals/fixtures.py`
- Create: `scripts/skill_evals/runners.py`
- Create: `tests/test_skill_evals_cli.py`
- Create: `tests/fixtures/evals/mock_outputs.json`
- Modify: `scripts/eval_skills.py`
- Modify: `scripts/skill_evals/cli.py`

- [ ] **Step 1: Write failing tests for runner selection and fixture loading**

```python
import unittest

from scripts.skill_evals.cli import build_runner


class RunnerSelectionTest(unittest.TestCase):
    def test_supports_mock_runner(self) -> None:
        runner = build_runner("mock", {})
        self.assertEqual(runner.name, "mock")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_cli -v`

Expected: `ImportError` because the CLI and runner factory do not exist yet.

- [ ] **Step 3: Implement a provider-agnostic runner interface**

```python
class EvalRunner:
    name = "base"

    def run_case(self, case, metadata):
        raise NotImplementedError


class MockRunner(EvalRunner):
    name = "mock"

    def __init__(self, outputs):
        self.outputs = outputs

    def run_case(self, case, metadata):
        return self.outputs[case.case_id]
```

- [ ] **Step 4: Implement the command runner and CLI entrypoint**

```python
class CommandRunner(EvalRunner):
    name = "command"

    def __init__(self, command: list[str]):
        self.command = command

    def run_case(self, case, metadata):
        completed = subprocess.run(
            self.command,
            input=json.dumps({"case": case.__dict__, "metadata": metadata}),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)
```

Run shape to support:

```bash
python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/local-smoke
python3 scripts/eval_skills.py run --suite writing --runner command --command ./bin/run-skill-eval
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_cli -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/eval_skills.py scripts/skill_evals/fixtures.py scripts/skill_evals/runners.py scripts/skill_evals/cli.py tests/test_skill_evals_cli.py tests/fixtures/evals/mock_outputs.json
git commit -m "feat: add skill eval runner and cli scaffold"
```

### Task 3: Implement Rule-Based Evaluators for Hard Requirements

**Files:**
- Create: `scripts/skill_evals/rules.py`
- Test: `tests/test_skill_evals_rules.py`
- Modify: `evals/rubrics/process-behavior.json`
- Modify: `evals/fixtures/writing/*.json`

- [ ] **Step 1: Write failing tests for hard-rule checks**

```python
import unittest

from scripts.skill_evals.rules import evaluate_rules


class RuleEvaluationTest(unittest.TestCase):
    def test_flags_missing_ahnii_for_blog_writing(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text="## Prerequisites\n\n- Python",
            artifact_path="content/posts/general/demo/index.md",
        )
        self.assertIn("missing_required_greeting", result.failed_rule_ids)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_rules -v`

Expected: `ImportError` or missing-rule failures.

- [ ] **Step 3: Implement deterministic rule checks**

```python
def evaluate_rules(skill: str, text: str, artifact_path: str | None) -> RuleEvaluation:
    failed = []
    if skill == "blog-writing" and "Ahnii!" not in text:
        failed.append("missing_required_greeting")
    if skill == "substack-writing" and "—" in text:
        failed.append("em_dash_disallowed")
    if skill == "session-to-blog" and artifact_path and not artifact_path.endswith("/index.md"):
        failed.append("invalid_output_path")
    return RuleEvaluation(failed_rule_ids=failed)
```

- [ ] **Step 4: Encode initial hard rules in fixtures and rubric metadata**

```json
{
  "rule_checks": [
    "required_greeting",
    "required_farewell",
    "artifact_path_pattern"
  ]
}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_rules -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/skill_evals/rules.py evals/rubrics/process-behavior.json evals/fixtures/writing tests/test_skill_evals_rules.py
git commit -m "feat: add deterministic rule checks for writing evals"
```

### Task 4: Add Comparison and Reporting

**Files:**
- Create: `scripts/skill_evals/comparison.py`
- Create: `scripts/skill_evals/reporting.py`
- Test: `tests/test_skill_evals_comparison.py`
- Modify: `scripts/skill_evals/cli.py`

- [ ] **Step 1: Write failing tests for baseline comparison and summary output**

```python
import unittest

from scripts.skill_evals.comparison import compare_runs


class ComparisonTest(unittest.TestCase):
    def test_detects_regression_when_candidate_fails_more_rules(self) -> None:
        baseline = {"rule_failures": 0, "rubric": {"sentence_variety": 4}}
        candidate = {"rule_failures": 1, "rubric": {"sentence_variety": 3}}
        result = compare_runs(baseline, candidate)
        self.assertEqual(result.status, "regression")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_comparison -v`

Expected: `ImportError` or missing comparison logic.

- [ ] **Step 3: Implement comparison logic and report writers**

```python
def compare_runs(baseline: dict, candidate: dict) -> ComparisonResult:
    if candidate["rule_failures"] > baseline["rule_failures"]:
        return ComparisonResult(status="regression")
    if candidate["rubric"]["sentence_variety"] < baseline["rubric"]["sentence_variety"]:
        return ComparisonResult(status="regression")
    return ComparisonResult(status="no_regression")
```

```python
def write_markdown_summary(path: Path, run: EvalRunResult) -> None:
    path.write_text(
        f"# Eval Summary\n\n"
        f"- Suite: {run.suite}\n"
        f"- Rule failures: {len(run.rule_failures)}\n"
        f"- Candidate status: {run.comparison_status}\n"
    )
```

- [ ] **Step 4: Wire the CLI to emit JSON plus Markdown summaries**

Run shape to support:

```bash
python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/2026-04-09-smoke
python3 scripts/eval_skills.py compare --baseline evals/baselines/writing/v1/run.json --candidate evals/results/2026-04-09-smoke/run.json
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_comparison -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/skill_evals/comparison.py scripts/skill_evals/reporting.py scripts/skill_evals/cli.py tests/test_skill_evals_comparison.py
git commit -m "feat: add baseline comparison and reporting"
```

### Task 5: Add Repeatability Metadata and Baseline Acceptance Workflow

**Files:**
- Modify: `scripts/skill_evals/models.py`
- Modify: `scripts/skill_evals/cli.py`
- Modify: `evals/baselines/README.md`
- Modify: `evals/README.md`
- Modify: `.gitignore`
- Test: `tests/test_skill_evals_models.py`
- Test: `tests/test_skill_evals_cli.py`

- [ ] **Step 1: Write failing tests for run metadata and baseline promotion**

```python
import unittest

from scripts.skill_evals.models import EvalRunMetadata


class RunMetadataTest(unittest.TestCase):
    def test_records_runner_and_fixture_versions(self) -> None:
        metadata = EvalRunMetadata(runner="mock", fixture_version="2026-04-09")
        self.assertEqual(metadata.runner, "mock")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_models tests.test_skill_evals_cli -v`

Expected: failures because metadata and promote-baseline flow do not exist.

- [ ] **Step 3: Implement metadata capture and baseline promotion**

```python
@dataclass(frozen=True)
class EvalRunMetadata:
    runner: str
    fixture_version: str
    rubric_version: str
    generated_at: str
    command: list[str] | None = None
```

```python
def promote_baseline(candidate_dir: Path, baseline_dir: Path) -> None:
    shutil.copytree(candidate_dir, baseline_dir, dirs_exist_ok=True)
```

- [ ] **Step 4: Document what is versioned and what is ignored**

```gitignore
__pycache__/
evals/results/tmp/
```

Document in `evals/baselines/README.md`:

- when a run is eligible for baseline promotion
- what metadata must be present
- how repeat runs are named

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_models tests.test_skill_evals_cli -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add .gitignore evals/README.md evals/baselines/README.md scripts/skill_evals/models.py scripts/skill_evals/cli.py tests/test_skill_evals_models.py tests/test_skill_evals_cli.py
git commit -m "feat: add eval metadata and baseline promotion flow"
```

### Task 6: Document Usage and Verify the Full Local Harness

**Files:**
- Modify: `README.md`
- Modify: `evals/README.md`
- Test: `tests/test_skill_evals_models.py`
- Test: `tests/test_skill_evals_fixtures.py`
- Test: `tests/test_skill_evals_rules.py`
- Test: `tests/test_skill_evals_comparison.py`
- Test: `tests/test_skill_evals_cli.py`

- [ ] **Step 1: Add docs for local usage, baseline workflow, and runner expectations**

````markdown
## Skill Evaluation

Run a local smoke test:

```bash
python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/local-smoke
```

Promote a run to baseline:

```bash
python3 scripts/eval_skills.py promote-baseline --candidate evals/results/local-smoke --baseline evals/baselines/writing/v1
```
````

- [ ] **Step 2: Run the full unit test suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS

- [ ] **Step 3: Run an end-to-end smoke evaluation**

Run: `python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/local-smoke`

Expected:
- `evals/results/local-smoke/run.json` exists
- `evals/results/local-smoke/summary.md` exists
- output includes `completed writing suite`

- [ ] **Step 4: Run baseline comparison smoke test**

Run: `python3 scripts/eval_skills.py compare --baseline evals/results/local-smoke/run.json --candidate evals/results/local-smoke/run.json`

Expected: `no_regression`

- [ ] **Step 5: Commit**

```bash
git add README.md evals/README.md
git commit -m "docs: add skill eval harness usage"
```

## Verification Checklist

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/local-smoke`
- [ ] `python3 scripts/eval_skills.py compare --baseline evals/results/local-smoke/run.json --candidate evals/results/local-smoke/run.json`

## Notes for Execution

- Keep Phase 1 scoped to harness, fixtures, reports, and baseline acceptance. Do not edit `skills/blog-writing/SKILL.md`, `skills/blog-reviewing/SKILL.md`, `skills/technical-writing/SKILL.md`, `skills/social-media-posts/SKILL.md`, `skills/substack-writing/SKILL.md`, `skills/film-review/SKILL.md`, or `skills/session-to-blog/SKILL.md` during this plan.
- The worktree is already dirty in unrelated and in-progress writing-skill files. Do not revert or overwrite those changes.
- The command runner is intentionally thin. It should accept external execution later without hard-coding a model provider into the repo.
- The em dash and sentence-variety policy belongs to Phase 2 issue `#10`, not this implementation pass.
