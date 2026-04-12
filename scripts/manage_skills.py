#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SKILLS_DIR = REPO_ROOT / "skills"
CLAUDE_MARKETPLACE_DIR = Path.home() / ".claude/plugins/marketplaces/jonesrussell-skills"
CODEx_SKILLS_DIR = Path.home() / ".codex/skills"
CURSOR_SKILLS_DIR = Path.home() / ".cursor/skills"
CURSOR_INTERNAL_SKILLS_DIR = Path.home() / ".cursor/skills-cursor"


@dataclass(frozen=True)
class Target:
    name: str
    root: Path
    mode: str
    notes: str = ""
    ignored_names: tuple[str, ...] = ()


CLAUDE_DIRECT_DIR = Path.home() / ".claude/skills"
CLAUDE_DIRECT_IGNORED = ("archetypes", "docs", "skills", "spec", "template")

TARGETS = {
    "codex": Target(
        "codex",
        CODEx_SKILLS_DIR,
        "symlink",
        "Leaves built-in `.system` and other non-canonical skills untouched.",
        (".system", "frontend-refactor", "frontend-skill"),
    ),
    "cursor": Target("cursor", CURSOR_SKILLS_DIR, "symlink", "Installs custom skills in `~/.cursor/skills`, not `~/.cursor/skills-cursor`."),
    "claude": Target("claude", CLAUDE_MARKETPLACE_DIR / "skills", "symlink", "Treats the installed marketplace checkout as a mirror only."),
    "claude-direct": Target(
        "claude-direct",
        CLAUDE_DIRECT_DIR,
        "symlink",
        "Symlinks skills directly into ~/.claude/skills/ — the canonical source for Claude Code.",
        CLAUDE_DIRECT_IGNORED,
    ),
}

CLAUDE_METADATA_FILES = (
    (REPO_ROOT / "README.md", CLAUDE_MARKETPLACE_DIR / "README.md"),
    (REPO_ROOT / ".claude-plugin/marketplace.json", CLAUDE_MARKETPLACE_DIR / ".claude-plugin/marketplace.json"),
)


def canonical_skill_dirs() -> dict[str, Path]:
    return {
        path.name: path
        for path in sorted(CANONICAL_SKILLS_DIR.iterdir())
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def list_target_entries(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    return {path.name: path for path in sorted(root.iterdir()) if path.is_dir() or path.is_symlink()}


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def is_same_link(dest: Path, src: Path) -> bool:
    return dest.is_symlink() and dest.resolve() == src.resolve()


def same_tree(src: Path, dest: Path) -> bool:
    if src.is_symlink() or dest.is_symlink():
        return src.resolve() == dest.resolve()
    if src.is_file() and dest.is_file():
        return filecmp.cmp(src, dest, shallow=False)
    if src.is_dir() and dest.is_dir():
        comparison = filecmp.dircmp(src, dest)
        if comparison.left_only or comparison.right_only or comparison.funny_files or comparison.diff_files:
            return False
        return all(same_tree(src / name, dest / name) for name in comparison.common_files + comparison.common_dirs)
    return False


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.is_dir():
        shutil.rmtree(path)


def sync_target(target: Target, clean: bool) -> list[str]:
    changes: list[str] = []
    skills = canonical_skill_dirs()
    target.root.mkdir(parents=True, exist_ok=True)

    existing = list_target_entries(target.root)
    for name, src in skills.items():
        dest = target.root / name
        if is_same_link(dest, src):
            continue
        if dest.exists() or dest.is_symlink():
            remove_path(dest)
        os.symlink(src, dest, target_is_directory=True)
        changes.append(f"{target.name}: linked {dest} -> {src}")

    if clean:
        for name, dest in existing.items():
            if name in skills or name in target.ignored_names:
                continue
            remove_path(dest)
            changes.append(f"{target.name}: removed extra {dest}")

    if target.name == "claude":
        for src, dest in CLAUDE_METADATA_FILES:
            ensure_parent(dest)
            if is_same_link(dest, src):
                continue
            if dest.exists() or dest.is_symlink():
                remove_path(dest)
            os.symlink(src, dest)
            changes.append(f"claude: linked {dest} -> {src}")

    return changes


def audit_target(target: Target) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    notes: list[str] = []
    skills = canonical_skill_dirs()
    existing = list_target_entries(target.root)

    if not target.root.exists():
        issues.append(f"{target.name}: missing install root {target.root}")
        return issues, notes

    for name, src in skills.items():
        dest = target.root / name
        if not dest.exists() and not dest.is_symlink():
            issues.append(f"{target.name}: missing skill {name}")
            continue
        if dest.is_symlink():
            resolved = dest.resolve()
            if resolved != src.resolve():
                issues.append(f"{target.name}: drifted link {name} -> {resolved} (expected {src})")
        elif not same_tree(src, dest):
            issues.append(f"{target.name}: content drift in {name}")

    for name, dest in existing.items():
        if name not in skills and name not in target.ignored_names:
            issues.append(f"{target.name}: extra skill {name} at {dest}")

    if target.name == "cursor" and CURSOR_INTERNAL_SKILLS_DIR.exists():
        notes.append(f"cursor: internal managed skills remain in {CURSOR_INTERNAL_SKILLS_DIR}")

    if target.name == "claude":
        for src, dest in CLAUDE_METADATA_FILES:
            if not dest.exists() and not dest.is_symlink():
                issues.append(f"claude: missing metadata mirror {dest}")
            elif dest.is_symlink() and dest.resolve() != src.resolve():
                issues.append(f"claude: drifted metadata link {dest} -> {dest.resolve()} (expected {src})")
            elif not dest.is_symlink() and not same_tree(src, dest):
                issues.append(f"claude: content drift in metadata file {dest}")

    if target.notes:
        notes.append(f"{target.name}: {target.notes}")
    return issues, notes


def print_audit(target_names: list[str]) -> int:
    exit_code = 0
    print(f"Canonical repo: {REPO_ROOT}")
    print(f"Canonical skills: {len(canonical_skill_dirs())}")
    for name in target_names:
        target = TARGETS[name]
        issues, notes = audit_target(target)
        print()
        print(f"[{target.name}] {target.root}")
        if issues:
            exit_code = 1
            for issue in issues:
                print(f"FAIL  {issue}")
        else:
            print("PASS  no drift detected")
        for note in notes:
            print(f"NOTE  {note}")
    return exit_code


def print_sync(target_names: list[str], clean: bool) -> int:
    changes: list[str] = []
    for name in target_names:
        changes.extend(sync_target(TARGETS[name], clean=clean))
    if changes:
        for change in changes:
            print(change)
    else:
        print("No changes needed.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit and sync canonical custom skills into local agent installs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--targets",
            nargs="+",
            choices=sorted(TARGETS),
            default=sorted(TARGETS),
            help="Targets to operate on.",
        )

    add_common(subparsers.add_parser("audit", help="Report missing skills, extra installs, and drifted content."))
    sync_parser = subparsers.add_parser("sync", help="Install canonical skills into target agent directories.")
    add_common(sync_parser)
    sync_parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove non-canonical custom skills from the selected target install directories.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not CANONICAL_SKILLS_DIR.exists():
        print(f"Canonical skills directory not found: {CANONICAL_SKILLS_DIR}", file=sys.stderr)
        return 2
    if args.command == "audit":
        return print_audit(args.targets)
    if args.command == "sync":
        return print_sync(args.targets, clean=args.clean)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
