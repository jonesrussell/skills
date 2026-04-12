import tempfile
import unittest
import json
from pathlib import Path

from scripts.skill_evals.cli import run_suite
from scripts.skill_evals.comparison import compare_runs
from scripts.skill_evals.reporting import render_comparison_markdown, render_run_markdown, write_comparison_markdown


class ReportingStyleSignalsTest(unittest.TestCase):
    def test_render_run_markdown_includes_style_signals_from_actual_run(self) -> None:
        class SignalRunner:
            name = "mock"

            def run_case(self, case, metadata):  # type: ignore[no-untyped-def]
                output = "Placeholder output."
                messages: list[str] = []
                artifact_path = None

                if case.case_id == "general_howto_happy_path":
                    output = "Ahnii!\n\nX is not Y, it is Z. This matters — and it is clear.\n\nBaamaapii"
                    messages = ["contrast pattern used"]
                elif case.case_id == "style_audit_happy_path":
                    output = "It is not one thing but another. Another sentence follows."
                elif case.case_id == "doc_page_happy_path":
                    output = "Short paragraph.\n\nAnother short paragraph."
                elif case.case_id == "contrast_pattern_overuse_case":
                    output = "Ahnii!\n\nThis is not setup, it is leverage. This is not speed, it is control.\n\nBaamaapii"
                elif case.case_id == "em_dash_heavy_case":
                    output = "Ahnii!\n\nThis works — until it doesn't — and then you need a fix.\n\nBaamaapii"

                if metadata["skill"] == "blog-writing":
                    artifact_path = "content/posts/signal-run/index.md"
                elif metadata["skill"] == "social-media-posts":
                    artifact_path = "docs/social/signal-run.md"
                elif metadata["skill"] == "substack-writing":
                    artifact_path = "~/brand/signal-run.md"
                    if output == "Placeholder output.":
                        output = "Ahnii!\n\nPlaceholder output.\n\nBaamaapii"
                elif metadata["skill"] == "session-to-blog":
                    artifact_path = "content/posts/signal-session/index.md"

                return {
                    "case_id": case.case_id,
                    "passed": True,
                    "output": output,
                    "artifact_path": artifact_path,
                    "messages": messages,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            run = run_suite(suite="writing", runner=SignalRunner(), output_dir=output_dir)
            payload = json.loads((output_dir / "run.json").read_text(encoding="utf-8"))
            markdown = render_run_markdown(run)

        self.assertIn("style_signals", payload)
        self.assertGreater(payload["style_signals"]["contrast_pattern_count"], 0)
        self.assertGreater(payload["style_signals"]["em_dash_count"], 0)
        self.assertIn("## Style Signals", markdown)
        self.assertIn("- contrast_pattern_count:", markdown)
        self.assertIn("- em_dash_count:", markdown)
        self.assertIn("- avg_sentence_length:", markdown)

    def test_render_comparison_markdown_includes_style_signals(self) -> None:
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
                "avg_sentence_length": 13.0,
            },
        }

        result = compare_runs(baseline, candidate)
        markdown = render_comparison_markdown(result)

        self.assertIn("## Style Signals", markdown)
        self.assertIn("- contrast_pattern_count: baseline 1 -> candidate 3", markdown)
        self.assertIn("- em_dash_count: baseline 0 -> candidate 2", markdown)
        self.assertIn("- avg_sentence_length: baseline 12.0 -> candidate 13.0", markdown)

    def test_write_comparison_markdown_persists_style_signal_section(self) -> None:
        baseline = {
            "rule_failures": 0,
            "rubric": {"clarity": 4},
            "style_signals": {"contrast_pattern_count": 1},
        }
        candidate = {
            "rule_failures": 0,
            "rubric": {"clarity": 4},
            "style_signals": {"contrast_pattern_count": 4},
        }

        result = compare_runs(baseline, candidate)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "comparison.md"
            write_comparison_markdown(report_path, result)
            markdown = report_path.read_text(encoding="utf-8")

        self.assertIn("## Style Signals", markdown)
        self.assertIn("- contrast_pattern_count: baseline 1 -> candidate 4", markdown)
