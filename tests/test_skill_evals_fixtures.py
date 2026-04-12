import json
import unittest
from pathlib import Path

from scripts.skill_evals.models import EvalFixture, RubricDefinition


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "writing"
RUBRIC_DIR = Path(__file__).resolve().parents[1] / "evals" / "rubrics"
EXPECTED_SKILLS = [
    "blog-writing",
    "blog-reviewing",
    "technical-writing",
    "social-media-posts",
    "substack-writing",
    "film-review",
    "session-to-blog",
]
PRIORITY_SKILL_CASES = {
    "blog-writing": {
        "contrast_pattern_overuse_case": {"clarity", "sentence_variety", "anti_pattern_frequency"},
        "em_dash_heavy_case": {"clarity", "punctuation_restraint", "anti_pattern_frequency"},
        "flat_cadence_case": {"clarity", "sentence_variety", "voice_fidelity"},
        "filler_jargon_case": {"clarity", "voice_fidelity", "anti_pattern_frequency"},
    },
    "blog-reviewing": {
        "contrast_pattern_review_case": {"clarity", "sentence_variety", "anti_pattern_frequency"},
        "em_dash_audit_case": {"clarity", "punctuation_restraint", "anti_pattern_frequency"},
        "flat_cadence_review_case": {"clarity", "sentence_variety", "voice_fidelity"},
        "filler_jargon_review_case": {"clarity", "voice_fidelity", "anti_pattern_frequency"},
    },
    "technical-writing": {
        "contrast_pattern_doc_case": {"clarity", "sentence_variety", "anti_pattern_frequency"},
        "em_dash_heavy_doc_case": {"clarity", "punctuation_restraint", "anti_pattern_frequency"},
        "flat_cadence_doc_case": {"clarity", "sentence_variety", "voice_fidelity"},
        "filler_jargon_doc_case": {"clarity", "voice_fidelity", "anti_pattern_frequency"},
    },
}


class EvalFixtureFileTest(unittest.TestCase):
    def test_all_writing_fixture_files_load(self) -> None:
        for skill in EXPECTED_SKILLS:
            with self.subTest(skill=skill):
                fixture_path = FIXTURE_DIR / f"{skill}.json"
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
                fixture = EvalFixture.from_dict(payload)

                self.assertEqual(fixture.skill, skill)
                self.assertEqual(fixture.suite, "writing")
                self.assertGreaterEqual(len(fixture.cases), 1)
                self.assertGreaterEqual(len(fixture.cases[0].rubric_targets), 1)

    def test_shared_rubric_files_are_valid_json(self) -> None:
        rubric_files = [
            RUBRIC_DIR / "writing-quality.json",
            RUBRIC_DIR / "process-behavior.json",
        ]

        for rubric_path in rubric_files:
            with self.subTest(rubric=rubric_path.name):
                payload = json.loads(rubric_path.read_text(encoding="utf-8"))
                rubric = RubricDefinition.from_dict(payload)
                self.assertEqual(rubric.rubric_id, payload["rubric_id"])

    def test_writing_fixture_targets_match_writing_quality_criteria_ids(self) -> None:
        rubric_payload = json.loads((RUBRIC_DIR / "writing-quality.json").read_text(encoding="utf-8"))
        rubric = RubricDefinition.from_dict(rubric_payload)
        known_ids = set(rubric.criterion_ids())

        for skill in EXPECTED_SKILLS:
            with self.subTest(skill=skill):
                fixture_path = FIXTURE_DIR / f"{skill}.json"
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
                fixture = EvalFixture.from_dict(payload)

                for case in fixture.cases:
                    self.assertLessEqual(set(case.rubric_targets), known_ids)

    def test_priority_fixtures_include_phase_two_ai_tell_cases(self) -> None:
        for skill, expected_cases in PRIORITY_SKILL_CASES.items():
            with self.subTest(skill=skill):
                fixture_path = FIXTURE_DIR / f"{skill}.json"
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
                fixture = EvalFixture.from_dict(payload)
                cases_by_id = {case.case_id: case for case in fixture.cases}

                for case_id, expected_targets in expected_cases.items():
                    with self.subTest(skill=skill, case_id=case_id):
                        self.assertIn(case_id, cases_by_id)
                        self.assertGreaterEqual(len(cases_by_id[case_id].prompt), 20)
                        self.assertEqual(set(cases_by_id[case_id].rubric_targets), expected_targets)

    def test_blog_writing_fragment_cases_override_full_post_hard_rules(self) -> None:
        fixture_path = FIXTURE_DIR / "blog-writing.json"
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture = EvalFixture.from_dict(payload)
        cases_by_id = {case.case_id: case for case in fixture.cases}

        for case_id in (
            "contrast_pattern_overuse_case",
            "em_dash_heavy_case",
            "flat_cadence_case",
            "filler_jargon_case",
        ):
            with self.subTest(case_id=case_id):
                self.assertEqual(cases_by_id[case_id].hard_rule_checks, ())

    def test_substack_fixture_supplies_issue_number_for_artifact_path(self) -> None:
        fixture_path = FIXTURE_DIR / "substack-writing.json"
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture = EvalFixture.from_dict(payload)

        self.assertIn("issue #42", fixture.cases[0].prompt.lower())

    def test_blog_reviewing_cases_opt_out_of_style_signal_aggregation(self) -> None:
        fixture_path = FIXTURE_DIR / "blog-reviewing.json"
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture = EvalFixture.from_dict(payload)

        for case in fixture.cases:
            with self.subTest(case_id=case.case_id):
                self.assertFalse(case.include_in_style_signals)
