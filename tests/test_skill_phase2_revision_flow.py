import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PhaseTwoSkillPolicyTest(unittest.TestCase):
    def test_blog_writing_mentions_contrast_pattern_and_sentence_variety(self) -> None:
        text = (REPO_ROOT / "skills" / "blog-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn('"X is not Y, it is Z."', text)
        self.assertIn("sentence variety", text.lower())
        self.assertIn("generic AI-sounding", text)
        self.assertIn("Negative framing", text)
        self.assertIn('"instead of"', text)

    def test_blog_reviewing_checks_for_overused_ai_writing_patterns(self) -> None:
        text = (REPO_ROOT / "skills" / "blog-reviewing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn('Contrast constructions like "X is not Y, it is Z"', text)
        self.assertIn("mechanically repetitive", text)
        self.assertIn("Generic AI-jargon filler", text)

    def test_technical_writing_checks_formulaic_contrasts_and_cadence(self) -> None:
        text = (REPO_ROOT / "skills" / "technical-writing" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn('lines like "X is not Y, it is Z."', text)
        self.assertIn("mechanically repetitive", text)
        self.assertIn("Use sparingly and on purpose", text)
        self.assertIn('"instead of"', text)

    def test_session_to_blog_checks_contrast_patterns_and_em_dash_restraint(self) -> None:
        text = (REPO_ROOT / "skills" / "session-to-blog" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn('"X is not Y, it is Z."', text)
        self.assertIn("Use sparingly and on purpose", text)
        self.assertIn("mechanically repetitive", text)
        self.assertIn("Negative framing", text)
        self.assertIn('"rather than"', text)
        self.assertIn("/home/jones/dev/blog/", text)

    def test_film_review_checks_em_dash_and_formulaic_contrast_overuse(self) -> None:
        text = (REPO_ROOT / "skills" / "film-review" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("sparingly and on purpose", text)
        self.assertIn('"X is not Y, it is Z."', text)
        self.assertIn("formulaic", text)
        self.assertIn("direct sentence", text)
        self.assertIn('# [Title] ([Year]): [Star Rating]', text)
        self.assertIn("double-negative", text)
        self.assertIn('"rather than"', text)
