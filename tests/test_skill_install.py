from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import skill_install as install
from scripts.catalog import load_catalog, marketplace


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "repo"
        self.destination = self.base / "agent-skills"
        self.data = {"schema_version": 1, "version": "1.0.0", "skills": {}, "bundles": {}}
        for name, status in (("one", "maintained"), ("two", "maintained"), ("old", "legacy"), ("retired", "retired")):
            source = self.repo / "skills" / name
            (source / "references").mkdir(parents=True)
            (source / "SKILL.md").write_text(f"---\nname: {name}\ndescription: A fixture\n---\nUse this fixture.\n", encoding="utf-8")
            (source / "references" / "notes.md").write_text("Supporting content\n", encoding="utf-8")
            self.data["skills"][name] = {"status": status, "title": name, "summary": "Fixture", "category": "tutorial", "review_note": "Fixture"}
        self.data["bundles"]["tutorial-skills"] = {"status": "maintained", "description": "Fixture bundle", "skills": ["one", "two"]}
        self.save_catalog()

    def save_catalog(self):
        (self.repo / "catalog.json").write_text(json.dumps(self.data), encoding="utf-8")

    def run_cli(self, args):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            code = install.main(args, repo_root=self.repo)
        return code, output.getvalue()

    def command(self, *args):
        return self.run_cli(["install", *args, "--dest", str(self.destination)])

    def test_selection_is_required_and_old_clean_option_is_rejected(self):
        self.assertEqual(self.command()[0], 1)
        self.assertFalse(self.destination.exists())
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            install.parser().parse_args(["sync", "--clean"])

    def test_dry_run_creates_nothing(self):
        code, output = self.command("--bundle", "tutorial-skills", "--dry-run")
        self.assertEqual(code, 0, output)
        self.assertFalse(self.destination.exists())

    def test_selective_copy_includes_references_preserves_other_installs(self):
        unrelated = self.destination / "personal" / "note.txt"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text("Private local content", encoding="utf-8")
        code, output = self.command("one")
        self.assertEqual(code, 0, output)
        self.assertTrue((self.destination / "one/references/notes.md").is_file())
        self.assertFalse((self.destination / "two").exists())
        self.assertEqual(unrelated.read_text(), "Private local content")
        receipt = json.loads(install.receipt_path(self.destination, "one").read_text())
        self.assertEqual(receipt["files"], install.inventory(self.destination / "one"))

    def test_repeated_install_is_noop(self):
        self.assertEqual(self.command("one")[0], 0)
        before = install.inventory(self.destination)
        self.assertEqual(self.command("one")[0], 0)
        self.assertEqual(install.inventory(self.destination), before)

    def test_full_batch_preflight_preserves_all_targets_on_conflict(self):
        conflict = self.destination / "two" / "SKILL.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("Local work", encoding="utf-8")
        code, output = self.command("--bundle", "tutorial-skills")
        self.assertEqual(code, 1, output)
        self.assertFalse((self.destination / "one").exists())
        self.assertEqual(conflict.read_text(), "Local work")
        self.assertFalse((self.destination / install.STATE).exists())

    def test_update_preserves_backup_and_requires_unchanged_managed_content(self):
        self.assertEqual(self.command("one")[0], 0)
        source = self.repo / "skills/one/references/notes.md"
        source.write_text("Upstream update", encoding="utf-8")
        self.assertEqual(self.command("one")[0], 1)
        code, output = self.command("one", "--update")
        self.assertEqual(code, 0, output)
        self.assertEqual((self.destination / "one/references/notes.md").read_text(), "Upstream update")
        backups = list((self.destination / install.STATE / "backups").glob("*/one/references/notes.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "Supporting content\n")
        (self.destination / "one/references/notes.md").write_text("New local edit", encoding="utf-8")
        self.assertEqual(self.command("one", "--update")[0], 1)

    def test_explicit_replace_preserves_unmanaged_copy(self):
        local = self.destination / "one" / "SKILL.md"
        local.parent.mkdir(parents=True)
        local.write_text("My local version", encoding="utf-8")
        code, output = self.command("one", "--replace")
        self.assertEqual(code, 0, output)
        backup = next((self.destination / install.STATE / "backups").glob("*/one/SKILL.md"))
        self.assertEqual(backup.read_text(), "My local version")

    def test_source_and_destination_edits_invalidate_preflight(self):
        plan = install.plan_install("one", self.repo / "skills/one", self.destination)
        (self.repo / "skills/one/SKILL.md").write_text("Changed source", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed after preflight"):
            install.apply_plan(plan)
        self.assertFalse(self.destination.exists())

    def test_copy_failure_preserves_original_and_receipt(self):
        self.assertEqual(self.command("one")[0], 0)
        before = install.inventory(self.destination / "one")
        receipt = install.receipt_path(self.destination, "one").read_bytes()
        (self.repo / "skills/one/references/notes.md").write_text("Changed source", encoding="utf-8")
        plan = install.plan_install("one", self.repo / "skills/one", self.destination, update=True)
        with patch.object(install.shutil, "copy2", side_effect=OSError("Copy failed")):
            with self.assertRaises(OSError):
                install.apply_plan(plan)
        self.assertEqual(install.inventory(self.destination / "one"), before)
        self.assertEqual(install.receipt_path(self.destination, "one").read_bytes(), receipt)

    def test_receipt_failure_restores_original(self):
        self.assertEqual(self.command("one")[0], 0)
        before = install.inventory(self.destination / "one")
        (self.repo / "skills/one/references/notes.md").write_text("Changed source", encoding="utf-8")
        plan = install.plan_install("one", self.repo / "skills/one", self.destination, update=True)
        with patch.object(install, "write_receipt", side_effect=OSError("Receipt failed")):
            with self.assertRaises(OSError):
                install.apply_plan(plan)
        self.assertEqual(install.inventory(self.destination / "one"), before)

    def test_legacy_requires_opt_in_and_retired_always_refuses(self):
        self.assertEqual(self.command("old")[0], 1)
        self.assertEqual(self.command("old", "--include-legacy")[0], 0)
        self.assertEqual(self.command("retired", "--include-legacy", "--replace")[0], 1)
        self.assertFalse((self.destination / "retired").exists())

    def test_all_selects_only_maintained_unless_legacy_opt_in(self):
        code, output = self.command("--all")
        self.assertEqual(code, 0, output)
        self.assertTrue((self.destination / "one").exists())
        self.assertTrue((self.destination / "two").exists())
        self.assertFalse((self.destination / "old").exists())

    def test_unknown_and_path_traversal_names_rejected(self):
        for name in ("missing", "../outside", "/absolute"):
            self.assertEqual(self.command(name)[0], 1)
        self.assertFalse(self.destination.exists())

    def test_codex_home_and_agent_destinations(self):
        with patch.dict(os.environ, {"CODEX_HOME": str(self.base / "custom-codex")}):
            self.assertEqual(install.target_root("codex-legacy"), self.base / "custom-codex/skills")
            self.assertEqual(install.target_root("codex"), Path.home() / ".agents/skills")
        self.assertEqual(install.target_root("claude"), Path.home() / ".claude/skills")
        self.assertEqual(install.target_root("cursor"), Path.home() / ".cursor/skills")

    def test_audit_is_read_only_and_unrelated_installs_not_deleted(self):
        code, output = self.run_cli(["audit", "--dest", str(self.destination)])
        self.assertEqual(code, 1, output)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.command("one")[0], 0)
        self.assertEqual(self.run_cli(["audit", "one", "--dest", str(self.destination)])[0], 0)

    def test_symlink_destination_refused_without_touching_target(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            self.destination.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Account cannot create symbolic links")
        self.assertEqual(self.command("one", "--replace")[0], 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_catalog_refuses_a_maintained_bundle_with_legacy_member(self):
        self.data["bundles"]["tutorial-skills"]["skills"].append("old")
        self.save_catalog()
        with self.assertRaisesRegex(ValueError, "Maintained bundle includes legacy"):
            load_catalog(self.repo)

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_windows_junction_cannot_redirect_installation(self):
        outside = self.base / "outside"
        outside.mkdir()
        command = '$ErrorActionPreference="Stop"; New-Item -ItemType Junction -Path $env:TEST_LINK -Target $env:TEST_TARGET | Out-Null'
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                       env={**os.environ, "TEST_LINK": str(self.destination), "TEST_TARGET": str(outside)}, check=True, capture_output=True)
        self.assertEqual(self.command("one", "--replace")[0], 1)
        self.assertEqual(list(outside.iterdir()), [])

    def test_marketplace_has_exact_members_not_all_skills(self):
        generated = marketplace(load_catalog(self.repo))
        entry = generated["plugins"][0]
        self.assertEqual(entry["skills"], ["./skills/one", "./skills/two"])
        self.assertNotIn("./skills", entry["skills"])

    def test_retired_record_without_source_is_never_installable(self):
        self.data["retired"] = {"removed": {"revision": "a" * 40, "disposition": "retired", "reason": "Superseded"}}
        self.save_catalog()
        code, output = self.command("removed")
        self.assertEqual(code, 1)
        self.assertIn("Retired skill", output)
        self.assertFalse(self.destination.exists())

    def test_catalog_rejects_broken_evaluation_contract_and_escape(self):
        self.data["skills"]["one"]["evals"] = "../outside.json"
        self.save_catalog()
        with self.assertRaisesRegex(ValueError, "Evaluation path"):
            load_catalog(self.repo)
        self.data["skills"]["one"]["evals"] = "evals.json"
        (self.repo / "skills/one/evals.json").write_text(json.dumps({"skill_name": "two", "evals": []}), encoding="utf-8")
        self.save_catalog()
        with self.assertRaisesRegex(ValueError, "Invalid evaluation"):
            load_catalog(self.repo)


if __name__ == "__main__":
    unittest.main()
