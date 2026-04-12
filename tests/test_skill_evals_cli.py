import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from scripts.skill_evals.cli import REPO_ROOT, build_runner, main, parse_args, promote_baseline, run_suite
from scripts.skill_evals.fixtures import load_fixture, load_fixtures
from scripts.skill_evals.models import EvalCase
from scripts.skill_evals.runners import CodexRunner, CommandRunner, MockRunner, RunnerError, _build_codex_prompt


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "writing"
MOCK_OUTPUTS_PATH = Path(__file__).resolve().parent / "fixtures" / "evals" / "mock_outputs.json"


class RunnerSelectionTest(unittest.TestCase):
    def test_supports_mock_runner(self) -> None:
        runner = build_runner("mock", {"outputs_path": MOCK_OUTPUTS_PATH})
        self.assertEqual(runner.name, "mock")
        self.assertIsInstance(runner, MockRunner)

    def test_supports_command_runner(self) -> None:
        runner = build_runner("command", {"command": ["./bin/run-skill-eval"]})
        self.assertEqual(runner.name, "command")
        self.assertIsInstance(runner, CommandRunner)
        self.assertEqual(runner.command, ("./bin/run-skill-eval",))

    def test_supports_codex_runner(self) -> None:
        runner = build_runner("codex", {"model": "gpt-5.4-mini", "profile": "eval"})
        self.assertEqual(runner.name, "codex")
        self.assertIsInstance(runner, CodexRunner)
        self.assertEqual(runner.model, "gpt-5.4-mini")
        self.assertEqual(runner.profile, "eval")

    def test_codex_prompt_requests_exact_skill_defined_artifact_path(self) -> None:
        case = EvalCase(
            case_id="newsletter_happy_path",
            prompt="Draft issue #42 of a personal newsletter about a recent build session.",
            expected_artifact="markdown_document",
        )

        prompt = _build_codex_prompt(
            skill="substack-writing",
            skill_path=REPO_ROOT / "skills" / "substack-writing" / "SKILL.md",
            skill_text="Save draft to ~/brand/substack-issue-N.md",
            case=case,
        )

        self.assertIn('the exact path the skill would write', prompt)
        self.assertIn('paths like "~/brand/..."', prompt)
        self.assertNotIn("repo-relative path where the skill would write", prompt)

    def test_command_runner_normalizes_startup_failures(self) -> None:
        runner = CommandRunner(["/definitely/not/a/real/command"])
        case = EvalCase(
            case_id="startup_failure",
            prompt="irrelevant",
            expected_artifact="markdown_document",
        )

        with self.assertRaises(RunnerError):
            runner.run_case(case, {"suite": "writing", "skill": "blog-writing"})

    def test_command_runner_rejects_invalid_json_and_non_mapping_output(self) -> None:
        runner = CommandRunner(["/bin/echo"])
        case = EvalCase(
            case_id="bad_output",
            prompt="irrelevant",
            expected_artifact="markdown_document",
        )

        invalid_completed = mock.Mock(stdout="not-json")
        mapping_completed = mock.Mock(stdout='["not", "a", "mapping"]')

        with mock.patch("scripts.skill_evals.runners.subprocess.run", return_value=invalid_completed):
            with self.assertRaises(RunnerError):
                runner.run_case(case, {"suite": "writing", "skill": "blog-writing"})

        with mock.patch("scripts.skill_evals.runners.subprocess.run", return_value=mapping_completed):
            with self.assertRaises(RunnerError):
                runner.run_case(case, {"suite": "writing", "skill": "blog-writing"})

    def test_rejects_unsupported_runner(self) -> None:
        with self.assertRaises(ValueError):
            build_runner("nope", {})


class FixtureLoadingTest(unittest.TestCase):
    def test_load_fixture_reads_a_single_skill(self) -> None:
        fixture = load_fixture("blog-writing")
        self.assertEqual(fixture.skill, "blog-writing")
        self.assertEqual(fixture.suite, "writing")
        self.assertGreaterEqual(len(fixture.cases), 5)
        self.assertEqual(fixture.cases[0].case_id, "general_howto_happy_path")
        self.assertIn("contrast_pattern_overuse_case", {case.case_id for case in fixture.cases})

    def test_load_fixtures_returns_all_writing_suites(self) -> None:
        fixtures = load_fixtures()
        expected = {
            "blog-reviewing",
            "blog-writing",
            "film-review",
            "session-to-blog",
            "social-media-posts",
            "substack-writing",
            "technical-writing",
        }
        self.assertTrue(expected.issubset({fixture.skill for fixture in fixtures}))
        self.assertGreaterEqual(len(fixtures), len(expected))

    def test_run_suite_writes_summary_file(self) -> None:
        runner = build_runner("mock", {"outputs_path": MOCK_OUTPUTS_PATH})
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            result = run_suite(suite="writing", runner=runner, output_dir=output_dir)

            self.assertEqual(result.skill, "__suite__")
            self.assertEqual(result.runner, "mock")
            self.assertIsNotNone(result.metadata)
            self.assertEqual(result.metadata.fixture_version, "2026-04-11")
            self.assertEqual(result.metadata.rubric_version, "2026-04-09")
            self.assertEqual(result.metadata.generated_at, result.generated_at)
            summary_path = output_dir / "run.json"
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["suite"], "writing")
            self.assertEqual(payload["skill"], "__suite__")
            self.assertIn("metadata", payload)
            self.assertEqual(payload["metadata"]["runner"], "mock")
            self.assertEqual(payload["metadata"]["fixture_version"], "2026-04-11")
            self.assertEqual(payload["metadata"]["rubric_version"], "2026-04-09")
            self.assertEqual(payload["metadata"]["generated_at"], result.generated_at)
            self.assertGreaterEqual(len(payload["cases"]), 1)

    def test_run_suite_excludes_opted_out_cases_from_style_signals(self) -> None:
        class ReviewSignalRunner:
            name = "mock"

            def run_case(self, case, metadata):  # type: ignore[no-untyped-def]
                if metadata["skill"] == "blog-reviewing":
                    output = "This is not X, it is Y — and it is not A, but B."
                else:
                    output = "Plain output."
                    if metadata["skill"] == "blog-writing":
                        output = "Ahnii!\n\nPlain output.\n\nBaamaapii"
                artifact_path = None
                if metadata["skill"] == "blog-writing":
                    artifact_path = "content/posts/demo/index.md"
                return {
                    "case_id": case.case_id,
                    "passed": True,
                    "output": output,
                    "artifact_path": artifact_path,
                    "messages": [],
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            result = run_suite(
                suite="writing",
                runner=ReviewSignalRunner(),
                output_dir=output_dir,
                skills=("blog-reviewing", "blog-writing"),
                case_ids=("contrast_pattern_review_case", "general_howto_happy_path"),
            )

        self.assertIsNotNone(result.style_signals)
        self.assertEqual(result.style_signals["contrast_pattern_count"], 0)
        self.assertEqual(result.style_signals["em_dash_count"], 0)

    def test_run_suite_applies_hard_rules_to_runner_output(self) -> None:
        class IncompleteBlogRunner:
            name = "mock"

            def run_case(self, case, metadata):  # type: ignore[no-untyped-def]
                return {
                    "case_id": case.case_id,
                    "passed": True,
                    "output": "Body only.",
                    "artifact_path": "content/posts/mock-blog/index.md",
                    "messages": [],
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            result = run_suite(
                suite="writing",
                runner=IncompleteBlogRunner(),
                output_dir=output_dir,
                skills=("blog-writing",),
                case_ids=("general_howto_happy_path",),
            )

        self.assertEqual(len(result.cases), 1)
        self.assertFalse(result.cases[0].passed)
        self.assertTrue(any("required_greeting" in message for message in result.cases[0].messages))

    def test_run_suite_filters_by_skill_and_case(self) -> None:
        runner = build_runner("mock", {"outputs_path": MOCK_OUTPUTS_PATH})
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "run"
            result = run_suite(
                suite="writing",
                runner=runner,
                output_dir=output_dir,
                skills=("film-review",),
                case_ids=("review_happy_path",),
            )

        self.assertEqual([case.case_id for case in result.cases], ["review_happy_path"])

    def test_promote_baseline_copies_candidate_run(self) -> None:
        runner = build_runner("mock", {"outputs_path": MOCK_OUTPUTS_PATH})
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            candidate_dir = root / "candidate"
            baseline_dir = root / "baseline" / "writing" / "v1"
            run_suite(suite="writing", runner=runner, output_dir=candidate_dir)

            result = promote_baseline(candidate_dir=candidate_dir, baseline_dir=baseline_dir)

            self.assertEqual(result.metadata.runner, "mock")
            self.assertEqual(result.metadata.fixture_version, "2026-04-11")
            self.assertTrue((baseline_dir / "run.json").is_file())
            self.assertTrue((baseline_dir / "summary.md").is_file())
            self.assertEqual(
                json.loads((baseline_dir / "run.json").read_text(encoding="utf-8"))["metadata"]["runner"],
                "mock",
            )
            self.assertEqual(
                json.loads((baseline_dir / "run.json").read_text(encoding="utf-8"))["metadata"]["fixture_version"],
                "2026-04-11",
            )

    def test_promote_baseline_rejects_existing_destination(self) -> None:
        runner = build_runner("mock", {"outputs_path": MOCK_OUTPUTS_PATH})
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            candidate_dir = root / "candidate"
            baseline_dir = root / "baseline" / "writing" / "v1"
            run_suite(suite="writing", runner=runner, output_dir=candidate_dir)
            baseline_dir.mkdir(parents=True, exist_ok=True)
            (baseline_dir / "sentinel.txt").write_text("keep", encoding="utf-8")

            with self.assertRaises(ValueError):
                promote_baseline(candidate_dir=candidate_dir, baseline_dir=baseline_dir)

    def test_promote_baseline_rejects_runs_without_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate_dir = Path(tmpdir) / "candidate"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            (candidate_dir / "run.json").write_text(
                json.dumps(
                    {
                        "suite": "writing",
                        "skill": "__suite__",
                        "runner": "mock",
                        "generated_at": "2026-04-09T12:00:00Z",
                        "summary": "",
                        "cases": [
                            {
                                "case_id": "general_howto_happy_path",
                                "passed": True,
                                "output": "ok",
                                "messages": [],
                            }
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                promote_baseline(candidate_dir=candidate_dir, baseline_dir=Path(tmpdir) / "baseline")

    def test_promote_baseline_rejects_metadata_conflicts(self) -> None:
        conflict_payloads = [
            {
                "runner": "command",
                "generated_at": "2026-04-09T12:00:00Z",
            },
            {
                "runner": "mock",
                "generated_at": "2026-04-09T12:01:00Z",
            },
        ]

        for payload_overrides in conflict_payloads:
            with self.subTest(payload_overrides=payload_overrides):
                with tempfile.TemporaryDirectory() as tmpdir:
                    candidate_dir = Path(tmpdir) / "candidate"
                    candidate_dir.mkdir(parents=True, exist_ok=True)
                    candidate_payload = {
                        "suite": "writing",
                        "skill": "__suite__",
                        "runner": "mock",
                        "generated_at": "2026-04-09T12:00:00Z",
                        "summary": "",
                        "metadata": {
                            "runner": "mock",
                            "fixture_version": "2026-04-09",
                            "rubric_version": "2026-04-09",
                            "generated_at": "2026-04-09T12:00:00Z",
                        },
                        "cases": [
                            {
                                "case_id": "general_howto_happy_path",
                                "passed": True,
                                "output": "ok",
                                "messages": [],
                            }
                        ],
                    }
                    candidate_payload.update(payload_overrides)
                    (candidate_dir / "run.json").write_text(json.dumps(candidate_payload, indent=2), encoding="utf-8")

                    with self.assertRaises(ValueError):
                        promote_baseline(candidate_dir=candidate_dir, baseline_dir=Path(tmpdir) / "baseline")

    def test_promote_baseline_rejects_incomplete_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            candidate_dir = Path(tmpdir) / "candidate"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            (candidate_dir / "run.json").write_text(
                json.dumps(
                    {
                        "suite": "writing",
                        "skill": "__suite__",
                        "runner": "mock",
                        "generated_at": "2026-04-09T12:00:00Z",
                        "summary": "",
                        "metadata": {
                            "runner": "mock",
                            "fixture_version": "",
                            "rubric_version": "2026-04-09",
                            "generated_at": "2026-04-09T12:00:00Z",
                        },
                        "cases": [
                            {
                                "case_id": "general_howto_happy_path",
                                "passed": True,
                                "output": "ok",
                                "messages": [],
                            }
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                promote_baseline(candidate_dir=candidate_dir, baseline_dir=Path(tmpdir) / "baseline")


class ParseArgsTest(unittest.TestCase):
    def test_parses_run_command_shape(self) -> None:
        args = parse_args(["run", "--suite", "writing", "--runner", "mock"])

        self.assertEqual(args.subcommand, "run")
        self.assertEqual(args.suite, "writing")
        self.assertEqual(args.runner, "mock")
        self.assertEqual(args.output_dir, REPO_ROOT / "evals" / "results" / "local-smoke")

    def test_parses_codex_run_options(self) -> None:
        args = parse_args(
            [
                "run",
                "--suite",
                "writing",
                "--runner",
                "codex",
                "--model",
                "gpt-5.4-mini",
                "--profile",
                "eval",
                "--skill",
                "technical-writing",
                "--case-id",
                "doc_page_happy_path",
            ]
        )

        self.assertEqual(args.runner, "codex")
        self.assertEqual(args.model, "gpt-5.4-mini")
        self.assertEqual(args.profile, "eval")
        self.assertEqual(args.skills, ["technical-writing"])
        self.assertEqual(args.case_ids, ["doc_page_happy_path"])

    def test_parses_promote_baseline_shape(self) -> None:
        args = parse_args(["promote-baseline", "--candidate", "evals/results/local-smoke", "--baseline", "evals/baselines/writing/v1"])

        self.assertEqual(args.subcommand, "promote-baseline")
        self.assertEqual(args.candidate, Path("evals/results/local-smoke"))
        self.assertEqual(args.baseline, Path("evals/baselines/writing/v1"))

    def test_main_returns_failure_status_for_runner_errors(self) -> None:
        with mock.patch("scripts.skill_evals.cli.build_runner", side_effect=RunnerError("boom")):
            exit_code = main(["run", "--suite", "writing", "--runner", "mock"])

        self.assertEqual(exit_code, 2)
