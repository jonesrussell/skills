import json
import io
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout

from scripts.skill_evals.cli import build_runner, main, parse_args, run_suite
from scripts.skill_evals.comparison import compare_runs
from scripts.skill_evals.reporting import write_comparison_markdown


class ComparisonTest(unittest.TestCase):
    def test_rejects_boolean_rule_failures_payload(self) -> None:
        baseline = {"rule_failures": False, "rubric": {"sentence_variety": 4}}
        candidate = {"rule_failures": 0, "rubric": {"sentence_variety": 4}}

        with self.assertRaises(ValueError):
            compare_runs(baseline, candidate)

    def test_detects_regression_when_candidate_fails_more_rules(self) -> None:
        baseline = {"rule_failures": 0, "rubric": {"sentence_variety": 4}}
        candidate = {"rule_failures": 1, "rubric": {"sentence_variety": 3}}

        result = compare_runs(baseline, candidate)

        self.assertEqual(result.status, "regression")
        self.assertEqual(result.rule_failure_delta, 1)
        self.assertIn("rule_failures", result.regressions)
        self.assertIn("sentence_variety", result.regressions)

    def test_detects_improvement_when_candidate_reduces_failures_and_scores_higher(self) -> None:
        baseline = {"rule_failures": 2, "rubric": {"sentence_variety": 3}}
        candidate = {"rule_failures": 0, "rubric": {"sentence_variety": 5}}

        result = compare_runs(baseline, candidate)

        self.assertEqual(result.status, "improvement")
        self.assertEqual(result.rule_failure_delta, -2)
        self.assertIn("rule_failures", result.improvements)
        self.assertIn("sentence_variety", result.improvements)

    def test_flags_repetitive_style_signals_as_soft_regressions(self) -> None:
        baseline = {
            "rule_failures": 0,
            "rubric": {"clarity": 4},
            "style_signals": {
                "contrast_pattern_count": 1,
                "em_dash_count": 0,
                "avg_sentence_length": 12.0,
            },
        }
        candidate = {
            "rule_failures": 0,
            "rubric": {"clarity": 4},
            "style_signals": {
                "contrast_pattern_count": 3,
                "em_dash_count": 2,
                "avg_sentence_length": 13.5,
            },
        }

        result = compare_runs(baseline, candidate)

        self.assertEqual(result.status, "regression")
        self.assertIn("contrast_pattern_count", result.regressions)
        self.assertIn("em_dash_count", result.regressions)

    def test_sentence_variety_improvement_does_not_override_clarity_regression(self) -> None:
        baseline = {
            "rule_failures": 0,
            "rubric": {"sentence_variety": 3, "clarity": 4},
            "style_signals": {"avg_sentence_length": 12.0},
        }
        candidate = {
            "rule_failures": 0,
            "rubric": {"sentence_variety": 5, "clarity": 3},
            "style_signals": {"avg_sentence_length": 11.0},
        }

        result = compare_runs(baseline, candidate)

        self.assertEqual(result.status, "regression")
        self.assertIn("clarity", result.regressions)
        self.assertNotIn("sentence_variety", result.improvements)


class ComparisonReportTest(unittest.TestCase):
    def test_writes_human_readable_markdown_summary(self) -> None:
        baseline = {"rule_failures": 0, "rubric": {"sentence_variety": 4}}
        candidate = {"rule_failures": 1, "rubric": {"sentence_variety": 3}}
        result = compare_runs(baseline, candidate)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "comparison.md"
            write_comparison_markdown(report_path, result)

            markdown = report_path.read_text(encoding="utf-8")

        self.assertIn("# Eval Comparison", markdown)
        self.assertIn("- Status: regression", markdown)
        self.assertIn("- Rule failures: baseline 0 -> candidate 1", markdown)
        self.assertIn("- sentence_variety: baseline 4 -> candidate 3", markdown)

    def test_writes_style_signal_summary_when_available(self) -> None:
        baseline = {
            "rule_failures": 0,
            "rubric": {"clarity": 4},
            "style_signals": {"contrast_pattern_count": 1, "em_dash_count": 0},
        }
        candidate = {
            "rule_failures": 0,
            "rubric": {"clarity": 4},
            "style_signals": {"contrast_pattern_count": 3, "em_dash_count": 2},
        }
        result = compare_runs(baseline, candidate)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "comparison.md"
            write_comparison_markdown(report_path, result)
            markdown = report_path.read_text(encoding="utf-8")

        self.assertIn("## Style Signals", markdown)
        self.assertIn("- contrast_pattern_count: baseline 1 -> candidate 3", markdown)
        self.assertIn("- em_dash_count: baseline 0 -> candidate 2", markdown)


class ComparisonCliTest(unittest.TestCase):
    def test_parse_args_supports_compare_command_shape(self) -> None:
        args = parse_args(
            [
                "compare",
                "--baseline",
                "evals/baselines/writing/v1/run.json",
                "--candidate",
                "evals/results/2026-04-09-smoke/run.json",
            ]
        )

        self.assertEqual(args.subcommand, "compare")
        self.assertEqual(args.baseline, Path("evals/baselines/writing/v1/run.json"))
        self.assertEqual(args.candidate, Path("evals/results/2026-04-09-smoke/run.json"))

    def test_compare_command_writes_json_and_markdown_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            baseline_path = tmp_root / "baseline.json"
            candidate_path = tmp_root / "candidate.json"
            output_dir = tmp_root / "reports"

            baseline_payload = {"rule_failures": 0, "rubric": {"sentence_variety": 4}}
            candidate_payload = {"rule_failures": 0, "rubric": {"sentence_variety": 4}}
            baseline_path.write_text(json.dumps(baseline_payload), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_payload), encoding="utf-8")

            exit_code = main(
                [
                    "compare",
                    "--baseline",
                    str(baseline_path),
                    "--candidate",
                    str(candidate_path),
                    "--output-dir",
                    str(output_dir),
                ]
            )

            comparison_json = json.loads((output_dir / "comparison.json").read_text(encoding="utf-8"))
            comparison_md = (output_dir / "comparison.md").read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertEqual(comparison_json["status"], "no_regression")
        self.assertIn("# Eval Comparison", comparison_md)
        self.assertIn("- Status: no_regression", comparison_md)

    def test_compare_command_surfaces_style_signal_comparisons(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            baseline_dir = tmp_root / "baseline"
            candidate_dir = tmp_root / "candidate"
            output_dir = tmp_root / "reports"

            class BaselineRunner:
                name = "mock"

                def run_case(self, case, metadata):  # type: ignore[no-untyped-def]
                    output = "Plain baseline output."
                    artifact_path = None
                    if case.case_id == "general_howto_happy_path":
                        output = "Ahnii!\n\nX is not Y, it is Z.\n\nBaamaapii"
                    if metadata["skill"] == "blog-writing":
                        artifact_path = "content/posts/baseline-run/index.md"
                    elif metadata["skill"] == "social-media-posts":
                        artifact_path = "docs/social/baseline-run.md"
                    elif metadata["skill"] == "substack-writing":
                        artifact_path = "~/brand/baseline-run.md"
                        if output == "Plain baseline output.":
                            output = "Ahnii!\n\nPlain baseline output.\n\nBaamaapii"
                    elif metadata["skill"] == "session-to-blog":
                        artifact_path = "content/posts/baseline-session/index.md"
                    return {
                        "case_id": case.case_id,
                        "passed": True,
                        "output": output,
                        "artifact_path": artifact_path,
                        "messages": [],
                    }

            class CandidateRunner:
                name = "mock"

                def run_case(self, case, metadata):  # type: ignore[no-untyped-def]
                    output = "Plain candidate output."
                    artifact_path = None
                    if case.case_id == "general_howto_happy_path":
                        output = "Ahnii!\n\nX is not Y, it is Z — and it is not A, but B — now.\n\nBaamaapii"
                    if metadata["skill"] == "blog-writing":
                        artifact_path = "content/posts/candidate-run/index.md"
                    elif metadata["skill"] == "social-media-posts":
                        artifact_path = "docs/social/candidate-run.md"
                    elif metadata["skill"] == "substack-writing":
                        artifact_path = "~/brand/candidate-run.md"
                        if output == "Plain candidate output.":
                            output = "Ahnii!\n\nPlain candidate output.\n\nBaamaapii"
                    elif metadata["skill"] == "session-to-blog":
                        artifact_path = "content/posts/candidate-session/index.md"
                    return {
                        "case_id": case.case_id,
                        "passed": True,
                        "output": output,
                        "artifact_path": artifact_path,
                        "messages": [],
                    }

            baseline_run = run_suite(suite="writing", runner=BaselineRunner(), output_dir=baseline_dir)
            candidate_run = run_suite(suite="writing", runner=CandidateRunner(), output_dir=candidate_dir)

            baseline_path = baseline_dir / "run.json"
            candidate_path = candidate_dir / "run.json"
            baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))
            candidate_payload = json.loads(candidate_path.read_text(encoding="utf-8"))

            exit_code = main(
                [
                    "compare",
                    "--baseline",
                    str(baseline_path),
                    "--candidate",
                    str(candidate_path),
                    "--output-dir",
                    str(output_dir),
                ]
            )

            comparison_json = json.loads((output_dir / "comparison.json").read_text(encoding="utf-8"))
            comparison_md = (output_dir / "comparison.md").read_text(encoding="utf-8")

        self.assertEqual(exit_code, 1)
        self.assertEqual(comparison_json["status"], "regression")
        self.assertIn("style_signal_comparisons", comparison_json)
        self.assertIn("style_signals", baseline_payload)
        self.assertIn("style_signals", candidate_payload)
        self.assertGreater(candidate_run.style_signals["contrast_pattern_count"], baseline_run.style_signals["contrast_pattern_count"])
        self.assertGreater(candidate_run.style_signals["em_dash_count"], baseline_run.style_signals["em_dash_count"])
        self.assertIn("## Style Signals", comparison_md)
        self.assertIn("- contrast_pattern_count: baseline 1 -> candidate 2", comparison_md)
        self.assertIn("- em_dash_count: baseline 0 -> candidate 2", comparison_md)

    def test_compare_command_works_on_real_run_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            runner = build_runner("mock", {})

            run_suite(suite="writing", runner=runner, output_dir=output_dir)
            run_payload = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))
            comparison = compare_runs(run_payload, run_payload)

        self.assertIn("rule_failures", run_payload)
        self.assertIn("rubric", run_payload)
        self.assertEqual(comparison.status, "no_regression")

    def test_run_command_stdout_matches_run_json_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "run",
                        "--suite",
                        "writing",
                        "--runner",
                        "mock",
                        "--output-dir",
                        str(output_dir),
                    ]
                )

            stdout_payload = json.loads(stdout.getvalue())
            file_payload = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout_payload, file_payload)
