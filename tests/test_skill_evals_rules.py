import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.skill_evals.rules as rules_module
from scripts.skill_evals.rules import evaluate_rules


FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "writing"
RUBRIC_PATH = Path(__file__).resolve().parents[1] / "evals" / "rubrics" / "process-behavior.json"


class RuleMetadataTest(unittest.TestCase):
    def test_process_behavior_rubric_encodes_hard_rule_ids(self) -> None:
        payload = json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))

        self.assertEqual(payload["rubric_id"], "process-behavior")
        self.assertIn("required_greeting", payload["rule_checks"])
        self.assertIn("required_farewell", payload["rule_checks"])
        self.assertIn("artifact_path_pattern", payload["rule_checks"])
        self.assertIn("em_dash_disallowed", payload["rule_checks"])
        self.assertIn("required_greeting", payload["hard_rules"])
        self.assertIn("em_dash_disallowed", payload["hard_rules"])

    def test_skill_fixtures_encode_hard_rule_metadata(self) -> None:
        expected_keys = {
            "blog-writing": {"required_greeting", "required_farewell", "artifact_path_pattern"},
            "session-to-blog": {"artifact_path_pattern"},
            "social-media-posts": {"artifact_path_pattern"},
            "substack-writing": {
                "required_greeting",
                "required_farewell",
                "artifact_path_pattern",
                "em_dash_disallowed",
            },
        }

        for skill, keys in expected_keys.items():
            with self.subTest(skill=skill):
                payload = json.loads((FIXTURE_ROOT / f"{skill}.json").read_text(encoding="utf-8"))
                self.assertTrue(keys.issubset(payload["hard_rules"].keys()))


class RuleEvaluationTest(unittest.TestCase):
    def tearDown(self) -> None:
        rules_module._load_json.cache_clear()

    def test_flags_missing_required_greeting(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text="## Prerequisites\n\n- Python\n\nBaamaapii",
            artifact_path="content/posts/general/demo/index.md",
        )

        self.assertIn("required_greeting", result.failed_rule_ids)
        self.assertNotIn("required_farewell", result.failed_rule_ids)
        self.assertNotIn("artifact_path_pattern", result.failed_rule_ids)

    def test_flags_missing_required_farewell(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text="Ahnii!\n\nYou can do the work.",
            artifact_path="content/posts/general/demo/index.md",
        )

        self.assertIn("required_farewell", result.failed_rule_ids)
        self.assertNotIn("required_greeting", result.failed_rule_ids)
        self.assertNotIn("artifact_path_pattern", result.failed_rule_ids)

    def test_ignores_frontmatter_when_checking_required_greeting(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text=(
                "---\n"
                'title: "Demo"\n'
                "date: 2026-04-11\n"
                "---\n\n"
                "Ahnii!\n\n"
                "You can do the work.\n\n"
                "Baamaapii"
            ),
            artifact_path="content/posts/general/demo/index.md",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.failed_rule_ids, ())

    def test_flags_invalid_artifact_path(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text="Ahnii!\n\nYou can do the work.\n\nBaamaapii",
            artifact_path="docs/social/demo.md",
        )

        self.assertEqual(result.failed_rule_ids, ("artifact_path_pattern",))

    def test_flags_em_dash_forbidden_in_substack(self) -> None:
        result = evaluate_rules(
            skill="substack-writing",
            text="Ahnii!\n\nI built the thing — and learned a lot.\n\nBaamaapii",
            artifact_path="~/brand/substack-issue-7.md",
        )

        self.assertIn("em_dash_disallowed", result.failed_rule_ids)
        self.assertNotIn("required_greeting", result.failed_rule_ids)
        self.assertNotIn("required_farewell", result.failed_rule_ids)
        self.assertNotIn("artifact_path_pattern", result.failed_rule_ids)

    def test_passes_session_to_blog_artifact_path_rule(self) -> None:
        result = evaluate_rules(
            skill="session-to-blog",
            text="any output text",
            artifact_path="content/posts/session-summary/index.md",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.checked_rule_ids, ("artifact_path_pattern",))

    def test_passes_social_media_posts_artifact_path_rule(self) -> None:
        result = evaluate_rules(
            skill="social-media-posts",
            text="any output text",
            artifact_path="docs/social/dev-work-post.md",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.checked_rule_ids, ("artifact_path_pattern",))

    def test_flags_missing_and_blank_artifact_path(self) -> None:
        missing = evaluate_rules(
            skill="session-to-blog",
            text="any output text",
            artifact_path=None,
        )
        blank = evaluate_rules(
            skill="social-media-posts",
            text="any output text",
            artifact_path=" ",
        )

        self.assertIn("artifact_path_pattern", missing.failed_rule_ids)
        self.assertIn("artifact_path_pattern", blank.failed_rule_ids)

    def test_allows_case_level_rule_override_to_skip_hard_rules(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text="## Keep Your Development Process Concrete",
            artifact_path=None,
            rule_ids=(),
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.checked_rule_ids, ())

    def test_rejects_case_level_rule_override_outside_fixture_set(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_rules(
                skill="blog-writing",
                text="Ahnii!\n\nYou can do the work.\n\nBaamaapii",
                artifact_path="content/posts/general/demo/index.md",
                rule_ids=("em_dash_disallowed",),
            )

    def test_passes_when_all_required_hard_rules_match(self) -> None:
        result = evaluate_rules(
            skill="blog-writing",
            text="Ahnii!\n\nYou can do the work.\n\nBaamaapii",
            artifact_path="content/posts/general/demo/index.md",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.failed_rule_ids, ())
        self.assertEqual(result.checked_rule_ids, ("required_greeting", "required_farewell", "artifact_path_pattern"))

    def test_rejects_blank_configured_rule_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            fixture_dir = tmp_root / "evals" / "fixtures" / "writing"
            rubric_dir = tmp_root / "evals" / "rubrics"
            fixture_dir.mkdir(parents=True)
            rubric_dir.mkdir(parents=True)

            (fixture_dir / "demo.json").write_text(
                json.dumps(
                    {
                        "skill": "demo",
                        "suite": "writing",
                        "hard_rule_checks": ["artifact_path_pattern", ""],
                        "hard_rules": {
                            "artifact_path_pattern": {
                                "prefix": "docs/demo/",
                                "suffix": ".md",
                            }
                        },
                        "cases": [
                            {
                                "case_id": "demo",
                                "prompt": "demo",
                                "expected_artifact": "markdown_document",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (rubric_dir / "process-behavior.json").write_text(
                json.dumps(
                    {
                        "rubric_id": "process-behavior",
                        "suite": "writing",
                        "rule_checks": ["artifact_path_pattern"],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(rules_module, "FIXTURE_ROOT", fixture_dir):
                with mock.patch.object(rules_module, "PROCESS_BEHAVIOR_RUBRIC_PATH", rubric_dir / "process-behavior.json"):
                    rules_module._load_json.cache_clear()
                    with self.assertRaises(ValueError):
                        evaluate_rules(skill="demo", text="anything", artifact_path="docs/demo/file.md")

    def test_rejects_missing_expected_rule_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            fixture_dir = tmp_root / "evals" / "fixtures" / "writing"
            rubric_dir = tmp_root / "evals" / "rubrics"
            fixture_dir.mkdir(parents=True)
            rubric_dir.mkdir(parents=True)

            (fixture_dir / "demo.json").write_text(
                json.dumps(
                    {
                        "skill": "demo",
                        "suite": "writing",
                        "hard_rule_checks": ["artifact_path_pattern", "required_greeting"],
                        "hard_rules": {
                            "artifact_path_pattern": {
                                "prefix": "docs/demo/",
                                "suffix": ".md",
                            }
                        },
                        "cases": [
                            {
                                "case_id": "demo",
                                "prompt": "demo",
                                "expected_artifact": "markdown_document",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (rubric_dir / "process-behavior.json").write_text(
                json.dumps(
                    {
                        "rubric_id": "process-behavior",
                        "suite": "writing",
                        "rule_checks": ["required_greeting", "artifact_path_pattern"],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(rules_module, "FIXTURE_ROOT", fixture_dir):
                with mock.patch.object(rules_module, "PROCESS_BEHAVIOR_RUBRIC_PATH", rubric_dir / "process-behavior.json"):
                    rules_module._load_json.cache_clear()
                    with self.assertRaises(ValueError):
                        evaluate_rules(skill="demo", text="Ahnii!", artifact_path="docs/demo/file.md")
