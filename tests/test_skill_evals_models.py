import json
import unittest
from pathlib import Path

from scripts.skill_evals.models import (
    EvalCase,
    EvalCaseResult,
    EvalFixture,
    EvalRunMetadata,
    EvalRunResult,
    FixtureValidationError,
    ResultValidationError,
    RubricCriterion,
    RubricDefinition,
    RubricValidationError,
)


class EvalFixtureSchemaTest(unittest.TestCase):
    def test_requires_at_least_one_case(self) -> None:
        with self.assertRaises(FixtureValidationError):
            EvalFixture.from_dict({"skill": "blog-writing", "suite": "writing", "cases": []})

    def test_rejects_blank_and_wrong_field_types(self) -> None:
        bad_payloads = [
            {"skill": "", "suite": "writing", "cases": [{"case_id": "x", "prompt": "y", "expected_artifact": "z"}]},
            {"skill": "blog-writing", "suite": "", "cases": [{"case_id": "x", "prompt": "y", "expected_artifact": "z"}]},
            {"skill": "blog-writing", "suite": "writing", "cases": "not-a-list"},
            {"skill": "blog-writing", "suite": "writing", "cases": [{"case_id": "", "prompt": "y", "expected_artifact": "z"}]},
            {"skill": "blog-writing", "suite": "writing", "cases": [{"case_id": "x", "prompt": "y", "expected_artifact": "z", "rubric_targets": "bad"}]},
        ]

        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(FixtureValidationError):
                    EvalFixture.from_dict(payload)

    def test_parses_case_and_rubric_targets(self) -> None:
        fixture = EvalFixture.from_dict(
            {
                "skill": "blog-writing",
                "suite": "writing",
                "version": "2026-04-11",
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "prompt": "Draft a blog post.",
                        "expected_artifact": "markdown_document",
                        "rubric_targets": ["voice_fidelity", "clarity"],
                        "hard_rule_checks": ["required_greeting"],
                        "include_in_style_signals": False,
                    }
                ],
            }
        )

        self.assertEqual(fixture.skill, "blog-writing")
        self.assertEqual(fixture.suite, "writing")
        self.assertEqual(fixture.version, "2026-04-11")
        self.assertEqual(len(fixture.cases), 1)
        self.assertEqual(
            fixture.cases[0],
            EvalCase(
                case_id="general_howto_happy_path",
                prompt="Draft a blog post.",
                expected_artifact="markdown_document",
                rubric_targets=("voice_fidelity", "clarity"),
                hard_rule_checks=("required_greeting",),
                include_in_style_signals=False,
            ),
        )

    def test_round_trip_serialization(self) -> None:
        payload = {
            "skill": "technical-writing",
            "suite": "writing",
            "version": "2026-04-11",
            "cases": [
                {
                    "case_id": "doc_page_happy_path",
                    "prompt": "Write docs.",
                    "expected_artifact": "markdown_document",
                    "rubric_targets": ["voice_fidelity"],
                }
            ],
        }
        fixture = EvalFixture.from_dict(payload)

        self.assertEqual(fixture.to_dict(), payload)

    def test_round_trip_serialization_canonicalizes_sparse_payloads(self) -> None:
        fixture = EvalFixture.from_dict(
            {
                "skill": "blog-writing",
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "prompt": "Draft a blog post.",
                        "expected_artifact": "markdown_document",
                        "hard_rule_checks": [],
                    }
                ],
            }
        )

        self.assertEqual(
            fixture.to_dict(),
            {
                "skill": "blog-writing",
                "suite": "writing",
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "prompt": "Draft a blog post.",
                        "expected_artifact": "markdown_document",
                        "rubric_targets": [],
                        "hard_rule_checks": [],
                    }
                ],
            },
        )

    def test_rubric_targets_must_match_rubric_criteria_ids(self) -> None:
        fixture = EvalFixture.from_dict(
            {
                "skill": "blog-writing",
                "suite": "writing",
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "prompt": "Draft a blog post.",
                        "expected_artifact": "markdown_document",
                        "rubric_targets": ["voice_fidelity", "clarity"],
                    }
                ],
            }
        )
        rubric = RubricDefinition.from_dict(
            {
                "rubric_id": "writing-quality",
                "suite": "writing",
                "criteria": [
                    {"criterion_id": "voice_fidelity", "description": "Matches the voice."},
                    {"criterion_id": "clarity", "description": "Stays clear."},
                ],
            }
        )

        fixture.validate_rubric_targets(rubric)

        with self.assertRaises(FixtureValidationError):
            fixture.validate_rubric_targets(
                RubricDefinition.from_dict(
                    {
                        "rubric_id": "writing-quality",
                        "suite": "other-writing",
                        "criteria": [
                            {"criterion_id": "voice_fidelity", "description": "Matches the voice."},
                            {"criterion_id": "clarity", "description": "Stays clear."},
                        ],
                    }
                )
            )

        with self.assertRaises(FixtureValidationError):
            fixture.validate_rubric_targets(
                RubricDefinition.from_dict(
                    {
                        "rubric_id": "writing-quality",
                        "suite": "writing",
                        "criteria": [
                            {"criterion_id": "voice_fidelity", "description": "Matches the voice."},
                        ],
                    }
                )
            )

        with self.assertRaises(FixtureValidationError):
            fixture.validate_rubric_targets(
                RubricDefinition.from_dict(
                    {
                        "rubric_id": "writing-quality",
                        "suite": "writing",
                        "rule_checks": ["required_greeting"],
                    }
                )
            )

    def test_validate_rubric_targets_rejects_empty_criteria_rubric(self) -> None:
        fixture = EvalFixture.from_dict(
            {
                "skill": "blog-writing",
                "suite": "writing",
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "prompt": "Draft a blog post.",
                        "expected_artifact": "markdown_document",
                        "rubric_targets": ["voice_fidelity"],
                    }
                ],
            }
        )

        with self.assertRaises(FixtureValidationError):
            fixture.validate_rubric_targets(
                RubricDefinition.from_dict(
                    {
                        "rubric_id": "writing-quality",
                        "suite": "writing",
                        "rule_checks": ["required_greeting"],
                    }
                )
            )


class EvalResultSchemaTest(unittest.TestCase):
    def test_parses_style_signals(self) -> None:
        result = EvalRunResult.from_dict(
            {
                "suite": "writing",
                "skill": "blog-writing",
                "runner": "mock",
                "generated_at": "2026-04-09T12:00:00Z",
                "summary": "completed",
                "style_signals": {
                    "em_dash_count": 1,
                    "contrast_pattern_count": 0,
                    "avg_sentence_length": 11.5,
                    "avg_paragraph_length": 3,
                    "sentence_length_variance": 2.25,
                },
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "passed": True,
                        "output": "ok",
                        "messages": ["done"],
                    }
                ],
            }
        )

        self.assertEqual(
            result.style_signals,
            {
                "em_dash_count": 1,
                "contrast_pattern_count": 0,
                "avg_sentence_length": 11.5,
                "avg_paragraph_length": 3,
                "sentence_length_variance": 2.25,
            },
        )
        self.assertEqual(
            result.to_dict()["style_signals"],
            {
                "em_dash_count": 1,
                "contrast_pattern_count": 0,
                "avg_sentence_length": 11.5,
                "avg_paragraph_length": 3,
                "sentence_length_variance": 2.25,
            },
        )

    def test_rejects_non_numeric_style_signals(self) -> None:
        with self.assertRaises(ResultValidationError):
            EvalRunResult.from_dict(
                {
                    "suite": "writing",
                    "skill": "blog-writing",
                    "cases": [{"case_id": "x", "passed": True}],
                    "style_signals": {"em_dash_count": "many"},
                }
            )

    def test_round_trip_serialization_canonicalizes_sparse_payloads(self) -> None:
        payload = {
            "suite": "writing",
            "skill": "blog-writing",
            "cases": [
                {
                    "case_id": "general_howto_happy_path",
                    "passed": True,
                }
            ],
        }
        result = EvalRunResult.from_dict(payload)

        self.assertIsNone(result.style_signals)
        self.assertEqual(
            result.to_dict(),
            {
                "suite": "writing",
                "skill": "blog-writing",
                "runner": "",
                "generated_at": "",
                "summary": "",
                "cases": [
                    {
                        "case_id": "general_howto_happy_path",
                        "passed": True,
                        "output": "",
                        "messages": [],
                    }
                ],
            },
        )

    def test_run_metadata_round_trip(self) -> None:
        metadata = EvalRunMetadata.from_dict(
            {
                "runner": "command",
                "fixture_version": "2026-04-09",
                "rubric_version": "2026-04-09",
                "generated_at": "2026-04-09T12:00:00Z",
                "command": ["python3", "scripts/eval_skills.py", "run"],
            }
        )

        self.assertEqual(
            metadata,
            EvalRunMetadata(
                runner="command",
                fixture_version="2026-04-09",
                rubric_version="2026-04-09",
                generated_at="2026-04-09T12:00:00Z",
                command=("python3", "scripts/eval_skills.py", "run"),
            ),
        )
        self.assertEqual(
            metadata.to_dict(),
            {
                "runner": "command",
                "fixture_version": "2026-04-09",
                "rubric_version": "2026-04-09",
                "generated_at": "2026-04-09T12:00:00Z",
                "command": ["python3", "scripts/eval_skills.py", "run"],
            },
        )

    def test_run_metadata_allows_omitting_command(self) -> None:
        metadata = EvalRunMetadata.from_dict(
            {
                "runner": "mock",
                "fixture_version": "2026-04-09",
                "rubric_version": "2026-04-09",
                "generated_at": "2026-04-09T12:00:00Z",
            }
        )

        self.assertEqual(metadata.command, ())
        self.assertEqual(
            metadata.to_dict(),
            {
                "runner": "mock",
                "fixture_version": "2026-04-09",
                "rubric_version": "2026-04-09",
                "generated_at": "2026-04-09T12:00:00Z",
            },
        )

    def test_run_metadata_rejects_blank_and_wrong_field_types(self) -> None:
        bad_payloads = [
            {},
            {"runner": "", "fixture_version": "2026-04-09", "rubric_version": "2026-04-09", "generated_at": "2026-04-09T12:00:00Z"},
            {"runner": "mock", "fixture_version": "", "rubric_version": "2026-04-09", "generated_at": "2026-04-09T12:00:00Z"},
            {"runner": "mock", "fixture_version": "2026-04-09", "rubric_version": "", "generated_at": "2026-04-09T12:00:00Z"},
            {"runner": "mock", "fixture_version": "2026-04-09", "rubric_version": "2026-04-09", "generated_at": "", "command": ["ok"]},
            {"runner": "mock", "fixture_version": "2026-04-09", "rubric_version": "2026-04-09", "generated_at": "2026-04-09T12:00:00Z", "command": "bad"},
        ]

        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ResultValidationError):
                    EvalRunMetadata.from_dict(payload)

    def test_requires_at_least_one_case_result(self) -> None:
        with self.assertRaises(ResultValidationError):
            EvalRunResult.from_dict({"suite": "writing", "skill": "blog-writing", "cases": []})

    def test_rejects_blank_and_wrong_field_types(self) -> None:
        bad_payloads = [
            {"suite": "", "skill": "blog-writing", "cases": [{"case_id": "x", "passed": True}]},
            {"suite": "writing", "skill": "", "cases": [{"case_id": "x", "passed": True}]},
            {"suite": "writing", "skill": "blog-writing", "cases": "not-a-list"},
            {"suite": "writing", "skill": "blog-writing", "cases": [{"case_id": "x", "passed": "yes"}]},
            {"suite": "writing", "skill": "blog-writing", "cases": [{"case_id": "x", "passed": True, "messages": "oops"}]},
            {"suite": "writing", "skill": "blog-writing", "cases": [{"case_id": "x", "passed": True, "artifact_path": ""}]},
            {"suite": "writing", "skill": "blog-writing", "cases": [{"case_id": "x", "passed": True, "output": 42}]},
        ]

        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ResultValidationError):
                    EvalRunResult.from_dict(payload)

    def test_parses_case_results(self) -> None:
        result = EvalRunResult.from_dict(
            {
                "suite": "writing",
                "skill": "blog-writing",
                "runner": "mock",
                "generated_at": "2026-04-09T12:00:00Z",
                "summary": "completed",
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
                        "messages": ["done"],
                    }
                ],
            }
        )

        self.assertEqual(result.runner, "mock")
        self.assertEqual(result.generated_at, "2026-04-09T12:00:00Z")
        self.assertEqual(result.summary, "completed")
        self.assertEqual(
            result.metadata,
            EvalRunMetadata(
                runner="mock",
                fixture_version="2026-04-09",
                rubric_version="2026-04-09",
                generated_at="2026-04-09T12:00:00Z",
            ),
        )
        self.assertEqual(
            result.cases[0],
            EvalCaseResult(
                case_id="general_howto_happy_path",
                passed=True,
                output="ok",
                messages=("done",),
            ),
        )

    def test_round_trip_serialization(self) -> None:
        payload = {
            "suite": "writing",
            "skill": "blog-writing",
            "runner": "mock",
            "generated_at": "2026-04-09T12:00:00Z",
            "summary": "completed",
            "metadata": {
                "runner": "mock",
                "fixture_version": "2026-04-09",
                "rubric_version": "2026-04-09",
                "generated_at": "2026-04-09T12:00:00Z",
                "command": ["python3", "scripts/eval_skills.py", "run"],
            },
            "cases": [
                {
                    "case_id": "general_howto_happy_path",
                    "passed": True,
                    "output": "ok",
                    "messages": ["done"],
                    "artifact_path": "evals/results/run-1/output.md",
                }
            ],
        }
        result = EvalRunResult.from_dict(payload)

        self.assertEqual(result.to_dict(), payload)


class RubricSchemaTest(unittest.TestCase):
    def test_quality_rubric_includes_style_signal_criteria(self) -> None:
        payload = json.loads(Path("/home/jones/dev/skills/evals/rubrics/writing-quality.json").read_text())
        criterion_ids = {criterion["criterion_id"] for criterion in payload["criteria"]}

        self.assertTrue(
            {"sentence_variety", "punctuation_restraint", "anti_pattern_frequency"}.issubset(criterion_ids)
        )

    def test_parses_quality_and_process_rubrics(self) -> None:
        quality = RubricDefinition.from_dict(
            {
                "rubric_id": "writing-quality",
                "suite": "writing",
                "version": "2026-04-09",
                "criteria": [
                    {"criterion_id": "voice_fidelity", "description": "Matches voice."},
                    {"criterion_id": "clarity", "description": "Stays clear."},
                ],
            }
        )
        process = RubricDefinition.from_dict(
            {
                "rubric_id": "process-behavior",
                "suite": "writing",
                "version": "2026-04-09",
                "rule_checks": ["required_greeting", "required_farewell"],
            }
        )

        self.assertEqual(
            quality.criteria[0],
            RubricCriterion(criterion_id="voice_fidelity", description="Matches voice."),
        )
        self.assertEqual(process.rule_checks, ("required_greeting", "required_farewell"))

    def test_rejects_malformed_rubric_payloads(self) -> None:
        bad_payloads = [
            {},
            {"rubric_id": "", "suite": "writing", "criteria": [{"criterion_id": "x", "description": "y"}]},
            {"rubric_id": "writing-quality", "suite": "", "criteria": [{"criterion_id": "x", "description": "y"}]},
            {"rubric_id": "writing-quality", "suite": "writing", "criteria": []},
            {"rubric_id": "writing-quality", "suite": "writing", "criteria": [{"criterion_id": "", "description": "y"}]},
            {"rubric_id": "writing-quality", "suite": "writing", "rule_checks": []},
        ]

        for payload in bad_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(RubricValidationError):
                    RubricDefinition.from_dict(payload)

    def test_round_trip_serialization(self) -> None:
        payload = {
            "rubric_id": "writing-quality",
            "suite": "writing",
            "version": "2026-04-09",
            "criteria": [
                {"criterion_id": "voice_fidelity", "description": "Matches voice."},
                {"criterion_id": "clarity", "description": "Stays clear."},
            ],
        }
        rubric = RubricDefinition.from_dict(payload)

        self.assertEqual(rubric.to_dict(), payload)
