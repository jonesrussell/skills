"""Exercise a real copied skill without relying on the source checkout's assets."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.skill_install import main


class PackagedSkillTests(unittest.TestCase):
    def test_installed_kickoff_runs_with_its_own_templates_and_license(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            installed = base / "agent-skills"
            with redirect_stdout(io.StringIO()):
                result = main(["install", "project-kickoff", "--dest", str(installed)])
            self.assertEqual(result, 0)
            skill = installed / "project-kickoff"
            self.assertIn("Copyright (c) 2026 Russell Jones", (skill / "LICENSE.txt").read_text(encoding="utf-8"))
            config = base / "input.json"
            config.write_text(json.dumps(dict(name="Tutorial", slug="tutorial", owner="Test owner", date="2026-10-24",
                                             purpose="Verify independent installation.", stage="Discovery", prefix="TU")), encoding="utf-8")
            destination = base / "project"
            script = skill / "scripts/scaffold_project.py"
            preview = subprocess.run([sys.executable, str(script), "preview", "--destination", str(destination), "--config", str(config)], cwd=base, text=True, capture_output=True)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertFalse(destination.exists())
            applied = subprocess.run([sys.executable, str(script), "apply", "--destination", str(destination), "--config", str(config)], cwd=base, text=True, capture_output=True)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            checked = subprocess.run([sys.executable, str(script), "check", "--destination", str(destination)], cwd=base, text=True, capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertTrue((destination / "docs/backlog.md").is_file())


if __name__ == "__main__":
    unittest.main()
