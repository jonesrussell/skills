"""Behavior checks for the create-only scaffold. Run from a scratch directory."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest
from scaffold_project import check, scaffold

class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="kickoff-test-", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.destination = self.base / "new-project"
        self.data = dict(name="Example", slug="example", owner="Test owner", date="2026-10-23",
                         purpose="Verify a reusable starter.", stage="Discovery", prefix="EX")

    def test_preview_has_no_filesystem_side_effects(self):
        result = scaffold(self.destination, self.data, False)
        self.assertFalse(self.destination.exists())
        self.assertTrue(any("AGENTS.md" in line for line in result))

    def test_repeat_preserves_personalized_files_and_repairs_missing_file(self):
        scaffold(self.destination, self.data, True)
        original = self.destination / "AGENTS.md"
        original.write_text("User-owned operating guidance\n", encoding="utf-8")
        missing = self.destination / "docs/plan.md"
        missing.unlink()
        result = scaffold(self.destination, self.data, True)
        self.assertEqual(original.read_text(encoding="utf-8"), "User-owned operating guidance\n")
        self.assertTrue(missing.is_file())
        self.assertIn("KEEP AGENTS.md", result)
        self.assertTrue(check(self.destination))

    def test_preflight_rejects_obstruction_before_writing_any_templates(self):
        self.destination.mkdir()
        (self.destination / "docs").write_text("Existing asset", encoding="utf-8")
        with self.assertRaises(ValueError):
            scaffold(self.destination, self.data, True)
        self.assertEqual([p.name for p in self.destination.iterdir()], ["docs"])

    def test_identity_change_does_not_mutate_existing_project(self):
        scaffold(self.destination, self.data, True)
        before = {p.relative_to(self.destination): p.read_bytes()
                  for p in self.destination.rglob("*") if p.is_file()}
        with self.assertRaises(ValueError):
            scaffold(self.destination, {**self.data, "name": "Another project"}, True)
        after = {p.relative_to(self.destination): p.read_bytes()
                 for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_checker_reports_broken_navigation(self):
        scaffold(self.destination, self.data, True)
        (self.destination / "README.md").write_text("[Missing](docs/missing.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing local link"):
            check(self.destination)

    def test_linked_destination_cannot_write_to_other_directory(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            self.destination.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("This account cannot create symbolic links")
        with self.assertRaises(ValueError):
            scaffold(self.destination, self.data, True)
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junction_cannot_redirect_scaffold(self):
        outside = self.base / "outside"
        outside.mkdir()
        command = '$ErrorActionPreference="Stop"; New-Item -ItemType Junction -Path $env:TEST_LINK -Target $env:TEST_TARGET | Out-Null'
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                       env={**os.environ, "TEST_LINK": str(self.destination), "TEST_TARGET": str(outside)}, check=True, capture_output=True)
        with self.assertRaises(ValueError):
            scaffold(self.destination, self.data, True)
        self.assertEqual(list(outside.iterdir()), [])

if __name__ == "__main__":
    unittest.main(verbosity=2)
