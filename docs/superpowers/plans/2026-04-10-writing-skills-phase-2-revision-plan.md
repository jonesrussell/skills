# Writing Skills Phase 2 Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the evaluation harness to measure repetitive AI-writing signals, then revise `blog-writing`, `blog-reviewing`, and `technical-writing` so comparative evals show improvement or no regression against the accepted baseline.

**Architecture:** Keep the existing Python stdlib eval harness and add heuristic reporting for anti-pattern signals rather than hard bans. Expand fixtures and reporting first so Phase 2 has a measurable before/after loop. Then revise only the three in-scope skill files, run the same fixtures, and compare against the baseline and pre-revision smoke runs.

**Tech Stack:** Python 3 stdlib, JSON fixture/rubric/report artifacts, markdown skill files, `unittest`

---

### File Structure

**Create:**
- `tests/test_skill_evals_reporting.py`
- `tests/test_skill_phase2_revision_flow.py`

**Modify:**
- `skills/blog-writing/SKILL.md`
- `skills/blog-reviewing/SKILL.md`
- `skills/technical-writing/SKILL.md`
- `evals/fixtures/writing/blog-writing.json`
- `evals/fixtures/writing/blog-reviewing.json`
- `evals/fixtures/writing/technical-writing.json`
- `evals/rubrics/writing-quality.json`
- `scripts/skill_evals/models.py`
- `scripts/skill_evals/comparison.py`
- `scripts/skill_evals/reporting.py`
- `scripts/skill_evals/cli.py`
- `tests/test_skill_evals_models.py`
- `tests/test_skill_evals_comparison.py`

### Task 1: Extend Eval Data Contracts for Style-Signal Reporting

**Files:**
- Modify: `scripts/skill_evals/models.py`
- Modify: `evals/rubrics/writing-quality.json`
- Modify: `tests/test_skill_evals_models.py`

- [ ] **Step 1: Write failing tests for new style-signal and rubric fields**

```python
import unittest

from scripts.skill_evals.models import EvalRunResult, ResultValidationError


class StyleSignalSchemaTest(unittest.TestCase):
    def test_accepts_style_signal_summary(self) -> None:
        result = EvalRunResult.from_dict(
            {
                "suite": "writing",
                "skill": "__suite__",
                "runner": "mock",
                "generated_at": "2026-04-10T12:00:00Z",
                "summary": "",
                "cases": [{"case_id": "x", "passed": True, "output": "", "messages": []}],
                "style_signals": {
                    "em_dash_count": 1,
                    "contrast_pattern_count": 0,
                    "avg_sentence_length": 11.5,
                },
            }
        )
        self.assertEqual(result.style_signals["em_dash_count"], 1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_models -v`

Expected: FAIL because the current model does not accept the new style signal fields.

- [ ] **Step 3: Implement minimal style-signal support and rubric criteria additions**

Add data-contract support for numeric style signals such as:

- `em_dash_count`
- `contrast_pattern_count`
- `avg_sentence_length`
- `avg_paragraph_length`
- `sentence_length_variance`

Update `evals/rubrics/writing-quality.json` to include criteria like:

- `sentence_variety`
- `punctuation_restraint`
- `anti_pattern_frequency`

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_models -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_evals/models.py evals/rubrics/writing-quality.json tests/test_skill_evals_models.py
git commit -m "feat: add style signal fields for writing evals"
```

### Task 2: Add Style-Signal Reporting and Comparison Heuristics

**Files:**
- Modify: `scripts/skill_evals/reporting.py`
- Modify: `scripts/skill_evals/comparison.py`
- Modify: `scripts/skill_evals/cli.py`
- Create: `tests/test_skill_evals_reporting.py`
- Modify: `tests/test_skill_evals_comparison.py`

- [ ] **Step 1: Write failing tests for style-signal markdown and comparison behavior**

```python
import unittest

from scripts.skill_evals.comparison import compare_runs


class StyleSignalComparisonTest(unittest.TestCase):
    def test_repetitive_contrast_patterns_count_as_regression(self) -> None:
        baseline = {
            "rule_failures": 0,
            "rubric": {"sentence_variety": 4},
            "style_signals": {"contrast_pattern_count": 1},
        }
        candidate = {
            "rule_failures": 0,
            "rubric": {"sentence_variety": 4},
            "style_signals": {"contrast_pattern_count": 3},
        }
        result = compare_runs(baseline, candidate)
        self.assertIn("contrast_pattern_count", result.regressions)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_comparison tests.test_skill_evals_reporting -v`

Expected: FAIL because style signals are not yet compared or rendered.

- [ ] **Step 3: Implement style-signal extraction, markdown output, and comparison heuristics**

Extend reporting so `summary.md` or comparison markdown surfaces:

- em dash counts
- contrast-pattern counts
- average sentence length
- average paragraph length
- sentence-length variance

Extend comparison heuristics so:

- more contrast-pattern repetition counts as a regression signal
- higher em dash count can count as regression where the skill allows sparse use
- sentence variety improvements can offset overly flat cadence only if clarity does not regress

Use heuristics and comparisons, not hard bans.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_comparison tests.test_skill_evals_reporting -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/skill_evals/reporting.py scripts/skill_evals/comparison.py scripts/skill_evals/cli.py tests/test_skill_evals_comparison.py tests/test_skill_evals_reporting.py
git commit -m "feat: report and compare writing style signals"
```

### Task 3: Expand Priority Fixtures to Trigger the New Signals

**Files:**
- Modify: `evals/fixtures/writing/blog-writing.json`
- Modify: `evals/fixtures/writing/blog-reviewing.json`
- Modify: `evals/fixtures/writing/technical-writing.json`
- Modify: `tests/test_skill_evals_models.py`

- [ ] **Step 1: Write failing tests for new priority-skill fixture coverage**

```python
import json
import unittest
from pathlib import Path


class PhaseTwoFixtureCoverageTest(unittest.TestCase):
    def test_priority_fixtures_include_ai_tell_cases(self) -> None:
        path = Path("evals/fixtures/writing/blog-writing.json")
        payload = json.loads(path.read_text())
        case_ids = {case["case_id"] for case in payload["cases"]}
        self.assertIn("contrast_pattern_overuse_case", case_ids)
        self.assertIn("flat_cadence_case", case_ids)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_skill_evals_models -v`

Expected: FAIL because the fixtures do not yet include the new cases.

- [ ] **Step 3: Add new fixture cases for the three target skills**

Add cases designed to expose:

- contrast construction repetition
- heavy em dash usage
- flat sentence cadence
- filler/generic AI-jargon phrasing

Each new case should define:

- a distinct `case_id`
- prompt/context shaped to trigger the target anti-pattern
- relevant rubric targets

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_skill_evals_models tests.test_skill_evals_fixtures -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add evals/fixtures/writing/blog-writing.json evals/fixtures/writing/blog-reviewing.json evals/fixtures/writing/technical-writing.json tests/test_skill_evals_models.py
git commit -m "test: add phase two fixtures for writing anti-patterns"
```

### Task 4: Revise `blog-writing` Style Policy

**Files:**
- Modify: `skills/blog-writing/SKILL.md`
- Create: `tests/test_skill_phase2_revision_flow.py`

- [ ] **Step 1: Write a failing policy test or content assertion for the intended style language**

```python
import unittest
from pathlib import Path


class BlogWritingPolicyTest(unittest.TestCase):
    def test_blog_writing_mentions_contrast_pattern_overuse(self) -> None:
        text = Path("skills/blog-writing/SKILL.md").read_text()
        self.assertIn("X is not Y, it is Z", text)
        self.assertIn("sentence variety", text.lower())
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_skill_phase2_revision_flow -v`

Expected: FAIL because the current skill wording is not specific enough yet.

- [ ] **Step 3: Revise the blog-writing skill**

Add or tighten guidance so it explicitly covers:

- em dashes allowed but sparse and intentional
- repetitive `X is not Y, it is Z` constructions as overuse signals
- sentence and paragraph variety as a positive requirement
- filler emphasis and generic AI-ish cadence

Do not create a brittle blanket ban.

- [ ] **Step 4: Run the policy test and targeted harness tests**

Run: `python3 -m unittest tests.test_skill_phase2_revision_flow tests.test_skill_evals_models tests.test_skill_evals_comparison -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/blog-writing/SKILL.md tests/test_skill_phase2_revision_flow.py
git commit -m "feat: refine blog-writing style policy"
```

### Task 5: Revise `blog-reviewing` Detection Guidance

**Files:**
- Modify: `skills/blog-reviewing/SKILL.md`
- Modify: `tests/test_skill_phase2_revision_flow.py`

- [ ] **Step 1: Add a failing test for overuse-pattern review guidance**

```python
def test_blog_reviewing_checks_cadence_and_contrast_pattern_overuse(self):
    text = Path("skills/blog-reviewing/SKILL.md").read_text()
    self.assertIn("contrast", text.lower())
    self.assertIn("cadence", text.lower())
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_skill_phase2_revision_flow -v`

Expected: FAIL if the checklist does not yet cover the new review focus.

- [ ] **Step 3: Revise the blog-reviewing checklist**

Make the checklist explicitly evaluate:

- overused em dashes rather than merely counting them
- repetitive contrast constructions
- repetitive sentence openings or cadence
- filler and generic AI-jargon patterns

Keep the skill in a reviewing posture, not a writing posture.

- [ ] **Step 4: Run the policy test and targeted harness tests**

Run: `python3 -m unittest tests.test_skill_phase2_revision_flow tests.test_skill_evals_comparison -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/blog-reviewing/SKILL.md tests/test_skill_phase2_revision_flow.py
git commit -m "feat: refine blog-reviewing anti-pattern checks"
```

### Task 6: Revise `technical-writing` Style Policy and Run Comparative Eval

**Files:**
- Modify: `skills/technical-writing/SKILL.md`
- Modify: `tests/test_skill_phase2_revision_flow.py`

- [ ] **Step 1: Add a failing test for the intended technical-writing policy language**

```python
def test_technical_writing_mentions_varied_sentence_starts_and_low_jargon(self):
    text = Path("skills/technical-writing/SKILL.md").read_text().lower()
    self.assertIn("varied sentence", text)
    self.assertIn("jargon", text)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_skill_phase2_revision_flow -v`

Expected: FAIL if the current technical-writing guidance is still too broad.

- [ ] **Step 3: Revise the technical-writing skill**

Add or tighten guidance around:

- sparse, intentional em dash use
- varied sentence starts and cadence
- low-jargon, concrete language
- avoiding repetitive contrast-pattern structures

- [ ] **Step 4: Run the full eval suite and comparative smoke checks**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/phase2-revision
python3 scripts/eval_skills.py compare --baseline evals/results/local-smoke/run.json --candidate evals/results/phase2-revision/run.json
```

Expected:

- full test suite PASS
- phase2 run writes `run.json` and `summary.md`
- compare returns either `improvement` or `no_regression`

- [ ] **Step 5: Commit**

```bash
git add skills/technical-writing/SKILL.md tests/test_skill_phase2_revision_flow.py
git commit -m "feat: refine technical-writing style policy"
```

## Verification Checklist

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] `python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/phase2-revision`
- [ ] `python3 scripts/eval_skills.py compare --baseline evals/results/local-smoke/run.json --candidate evals/results/phase2-revision/run.json`

## Notes for Execution

- Only `blog-writing`, `blog-reviewing`, and `technical-writing` should be revised in this phase.
- Do not edit `social-media-posts`, `substack-writing`, `film-review`, or `session-to-blog` during this pass.
- Keep anti-pattern measurement heuristic unless there is a clear reason to hard-gate it.
- `substack-writing` already has a hard no-em-dash rule, but it is outside this phase and should not be changed here.
- Treat the current local-smoke baseline as the comparison control unless a newer named baseline is explicitly promoted first.
