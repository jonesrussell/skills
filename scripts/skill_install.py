"""Selective, copy-based installation with conflict checks and retained backups."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import uuid

try:
    from .catalog import ROOT, load_catalog
except ImportError:
    from catalog import ROOT, load_catalog

TARGETS = {"codex": ".agents/skills", "codex-legacy": ".codex/skills", "claude": ".claude/skills", "cursor": ".cursor/skills"}


def is_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    # Path.is_junction arrived in 3.12. Reparse attributes also cover 3.11 on Windows.
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def safe_directory(path: Path) -> Path:
    """Check before resolving: a junction must not redirect an install or backup."""
    path = Path(os.path.abspath(path.expanduser()))
    if path == Path(path.anchor):
        raise ValueError("Choose an agent skill directory, not a drive root")
    for candidate in (*reversed(path.parents), path):
        if is_link(candidate):
            raise ValueError(f"Linked destination needs manual handling: {candidate}")
        if candidate.exists() and not candidate.is_dir():
            raise ValueError(f"Expected a directory: {candidate}")
    return path.resolve()


def inventory(root: Path) -> dict[str, str]:
    """Fingerprint installed content without machine-generated Python caches."""
    if is_link(root):
        raise ValueError(f"Linked skill needs manual handling: {root}")
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if ".git" in relative.parts or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if is_link(path):
            raise ValueError(f"Linked skill content needs manual handling: {path}")
        if path.is_file():
            result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def selected_names(data: dict, names: list[str], bundles: list[str], all_skills: bool, include_legacy: bool) -> list[str]:
    selected = set(names)
    if all_skills:
        selected.update(n for n, e in data["skills"].items() if e["status"] == "maintained" or (include_legacy and e["status"] == "legacy"))
    for bundle in bundles:
        if bundle not in data["bundles"]:
            raise ValueError(f"Unknown bundle: {bundle}")
        selected.update(data["bundles"][bundle]["skills"])
    if not selected:
        raise ValueError("Select a skill name, --bundle NAME or --all; no implicit bulk install")
    for name in sorted(selected):
        entry = data["skills"].get(name)
        if not entry:
            if name in data.get("retired", {}):
                raise ValueError(f"Retired skill cannot be installed: {name}. See docs/retired.md for its disposition and recovery revision.")
            raise ValueError(f"Unknown skill: {name}")
        if entry["status"] == "retired":
            raise ValueError(f"Retired skill cannot be installed: {name}. Read its retirement note.")
        if entry["status"] == "legacy" and not include_legacy:
            raise ValueError(f"Legacy skill requires --include-legacy after review: {name}")
    return sorted(selected)


@dataclass
class Plan:
    name: str
    source: Path
    root: Path
    destination: Path
    source_files: dict[str, str]
    existing_files: dict[str, str] | None
    action: str


def state_directory(root: Path) -> Path:
    # Backups contain SKILL.md. Keep them outside the host's discovery directory.
    return root.with_name(f".{root.name}-jonesrussell-state")


def receipt_path(root: Path, name: str) -> Path:
    return state_directory(root) / "receipts" / f"{name}.json"


def plan_install(name: str, source: Path, root: Path, *, update: bool = False, replace: bool = False) -> Plan:
    root = safe_directory(root)
    old_state = root / ".jonesrussell-skills"
    if old_state.exists() or is_link(old_state):
        raise ValueError(f"Historical installer state is inside skill discovery: {old_state}. Preserve and move it to {state_directory(root)} before installing; do not overwrite an existing state directory.")
    destination = root / name
    safe_directory(destination)
    safe_directory(state_directory(root) / "receipts")
    safe_directory(state_directory(root) / "backups")
    source = safe_directory(source)
    if destination == source or source in destination.parents or destination in source.parents:
        raise ValueError("The install destination must be separate from the source skill")
    source_files = inventory(source)
    if "SKILL.md" not in source_files:
        raise ValueError(f"Missing SKILL.md: {source}")
    existing = inventory(destination) if destination.exists() else None
    if existing == source_files:
        action = "unchanged"
    elif existing is None:
        action = "install"
    else:
        receipt = receipt_path(root, name)
        if is_link(receipt):
            raise ValueError(f"Linked receipt needs manual handling: {receipt}")
        recorded = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else {}
        managed_clean = recorded.get("schema_version") == 1 and recorded.get("name") == name and recorded.get("files") == existing
        if replace:
            action = "replace with backup"
        elif update and managed_clean:
            action = "update with backup"
        else:
            state = "modified or unmanaged" if not managed_clean else "an older managed version"
            option = "--replace" if not managed_clean else "--update"
            raise ValueError(f"{name}: destination contains {state}; inspect it, then use {option} to retain a backup and replace only this skill")
    return Plan(name, source, root, destination, source_files, existing, action)


def write_receipt(plan: Plan) -> None:
    receipt = receipt_path(plan.root, plan.name)
    if is_link(receipt):
        raise ValueError(f"Linked receipt needs manual handling: {receipt}")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": 1, "name": plan.name, "files": plan.source_files,
            "installed_at": datetime.now(timezone.utc).isoformat(), "source": "jonesrussell/skills"}
    pending = receipt.with_name(f".{plan.name}-{uuid.uuid4().hex}.tmp")
    pending.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(pending, receipt)


def apply_plan(plan: Plan) -> str:
    if plan.action == "unchanged":
        return f"UNCHANGED {plan.name}"
    # Recheck immediately before mutation so a stale plan cannot replace newer edits.
    safe_directory(plan.destination)
    state_root = safe_directory(state_directory(plan.root))
    safe_directory(state_root / "receipts")
    backups = safe_directory(state_root / "backups")
    current = inventory(plan.destination) if plan.destination.exists() else None
    if current != plan.existing_files or inventory(plan.source) != plan.source_files:
        raise ValueError(f"Content changed after preflight: {plan.name}; inspect and retry")
    plan.root.mkdir(parents=True, exist_ok=True)
    state_root.mkdir(exist_ok=True)
    # Stage under the same filesystem. Copy failures leave the existing install intact.
    with tempfile.TemporaryDirectory(prefix="stage-", dir=state_root) as temporary:
        staging = Path(temporary) / plan.name
        staging.mkdir()
        for relative in plan.source_files:
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(plan.source / relative, target)
        if inventory(staging) != plan.source_files:
            raise ValueError(f"Source changed while copying: {plan.name}")
        # Copying can take time. Check local edits again before moving their directory.
        if (inventory(plan.destination) if plan.destination.exists() else None) != plan.existing_files:
            raise ValueError(f"Destination changed while copying: {plan.name}")
        backup = None
        if plan.destination.exists():
            backup = backups / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}" / plan.name
            safe_directory(backup.parent)
            backup.parent.mkdir(parents=True)
            os.replace(plan.destination, backup)
        try:
            os.replace(staging, plan.destination)
            write_receipt(plan)
        except Exception:
            # Move a newly installed copy back to staging before restoring the original.
            if plan.destination.exists() and not staging.exists():
                os.replace(plan.destination, staging)
            if backup is not None and backup.exists():
                os.replace(backup, plan.destination)
            raise
    return f"INSTALLED {plan.name}" + (f"; previous copy: {backup}" if backup else "")


def target_root(name: str) -> Path:
    if name == "codex-legacy" and os.environ.get("CODEX_HOME"):
        return Path(os.environ["CODEX_HOME"]).expanduser() / "skills"
    return Path.home() / TARGETS[name]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="Show maintained skills by default")
    listing.add_argument("--status", choices=("maintained", "legacy", "retired", "all"), default="maintained")
    listing.add_argument("--category")
    for action in ("install", "sync", "audit"):
        sub = commands.add_parser(action, help="Inspect or install explicitly selected skills; sync is an install alias")
        sub.add_argument("names", nargs="*")
        sub.add_argument("--bundle", action="append", default=[])
        sub.add_argument("--all", action="store_true", help="Select maintained skills; add --include-legacy to include historical ones")
        sub.add_argument("--include-legacy", action="store_true")
        targets = sub.add_mutually_exclusive_group()
        targets.add_argument("--target", dest="targets", action="append", choices=TARGETS)
        targets.add_argument("--targets", nargs="+", choices=TARGETS)
        sub.add_argument("--dest", type=Path, help="Override the skill install root for one target")
        if action != "audit":
            sub.add_argument("--dry-run", action="store_true")
            flags = sub.add_mutually_exclusive_group()
            flags.add_argument("--update", action="store_true", help="Update an unchanged managed copy, keeping a backup")
            flags.add_argument("--replace", action="store_true", help="Explicitly replace a modified/unmanaged copy, keeping a backup")
    return result


def main(argv: list[str] | None = None, *, repo_root: Path = ROOT) -> int:
    args = parser().parse_args(argv)
    try:
        data = load_catalog(repo_root)
        if args.command == "list":
            for name, entry in sorted(data["skills"].items()):
                if args.status != "all" and entry["status"] != args.status:
                    continue
                if args.category and entry["category"] != args.category:
                    continue
                print(f"{name} [{entry['status']}; {entry['category']}]\n  {entry['summary']}")
            return 0
        if args.command == "audit" and not (args.names or args.bundle or args.all):
            args.all = True
        names = selected_names(data, args.names, args.bundle, args.all, args.include_legacy)
        targets = args.targets or ["codex"]
        if args.dest and len(targets) != 1:
            raise ValueError("--dest requires exactly one target")
        roots = [(target, safe_directory(args.dest or target_root(target))) for target in dict.fromkeys(targets)]
        if len({root for _, root in roots}) != len(roots):
            raise ValueError("Selected targets resolve to the same directory")
        plans = []
        errors = []
        for target, root in roots:
            for name in names:
                try:
                    plan = plan_install(name, repo_root / "skills" / name, root,
                                        update=getattr(args, "update", False), replace=getattr(args, "replace", False))
                    plans.append(plan)
                    print(f"{target}: {plan.action.upper()} {name} -> {plan.destination}")
                    if args.command == "audit" and plan.action != "unchanged":
                        errors.append(f"{name}: not installed")
                except (OSError, ValueError) as error:
                    errors.append(str(error))
            if args.command == "audit" and root.exists():
                unmanaged = [p.name for p in root.iterdir() if not p.name.startswith('.') and p.is_dir() and p.name not in data['skills']]
                if unmanaged:
                    print(f"{target}: {len(unmanaged)} unrelated local directories left outside this catalog")
        if errors:
            raise ValueError("\n".join(errors))
        if args.command == "audit" or args.dry_run:
            print("Read-only: no files changed.")
            return 0
        for plan in plans:
            print(apply_plan(plan))
        print("Selected files installed. Refresh or restart your agent if needed; runtime discovery was not verified.")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
