"""Validate the catalog and generate its public index and Claude marketplace."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
STATUSES = {"maintained", "legacy", "retired"}


def load_catalog(root: Path = ROOT) -> dict:
    data = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported catalog schema")
    skills = data.get("skills", {})
    if not skills:
        raise ValueError("Catalog has no skills")
    for name, entry in skills.items():
        if not NAME.fullmatch(name) or entry.get("status") not in STATUSES:
            raise ValueError(f"Invalid skill name or status: {name}")
        for key in ("title", "summary", "category", "review_note"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise ValueError(f"Missing {key}: {name}")
        source = root / "skills" / name
        info = source.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Linked skill source is not portable: {name}")
        text = (source / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)
        match = re.search(r"^name:\s*['\"]?([a-z0-9-]+)['\"]?\s*$", frontmatter[1] if len(frontmatter) == 3 else "", re.M)
        if not match or match[1] != name:
            raise ValueError(f"SKILL.md name does not match catalog: {name}")
        description = re.search(r"^description:\s*(.+)$", frontmatter[1], re.M)
        if not description or not 1 <= len(description[1].strip().strip("\"'")) <= 1024:
            raise ValueError(f"Missing or oversized description: {name}")
        if len(name) > 64:
            raise ValueError(f"Oversized skill name: {name}")
        # Evaluation cases are inspectable inputs, not a claim they were executed.
        if entry.get("evals"):
            relative = Path(entry["evals"])
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"Evaluation path must stay inside the skill: {name}")
            cases = json.loads((source / relative).read_text(encoding="utf-8"))
            if cases.get("skill_name") != name or not cases.get("evals"):
                raise ValueError(f"Invalid evaluation cases: {name}")
            ids = set()
            for case in cases["evals"]:
                if not isinstance(case.get("id"), int) or case["id"] in ids:
                    raise ValueError(f"Invalid or duplicate evaluation id: {name}")
                ids.add(case["id"])
                if not case.get("prompt") or not case.get("expected_output") or not isinstance(case.get("should_trigger"), bool):
                    raise ValueError(f"Incomplete evaluation case: {name}")
        if entry.get("reviewed_on"):
            date.fromisoformat(entry["reviewed_on"])
    actual = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    if actual != set(skills):
        raise ValueError(f"Uncataloged or missing skills: {sorted(actual ^ set(skills))}")
    for name, entry in data.get("retired", {}).items():
        if not NAME.fullmatch(name) or name in skills or not entry.get("reason"):
            raise ValueError(f"Invalid retirement entry: {name}")
        if not re.fullmatch(r"[a-f0-9]{40}", entry.get("revision", "")):
            raise ValueError(f"Retirement requires an exact recovery revision: {name}")
    for name, bundle in data.get("bundles", {}).items():
        members = bundle.get("skills", [])
        if not NAME.fullmatch(name) or not members or len(members) != len(set(members)):
            raise ValueError(f"Invalid bundle: {name}")
        for member in members:
            if member not in skills or skills[member]["status"] == "retired":
                raise ValueError(f"Bundle {name} contains unknown/retired skill: {member}")
            if bundle.get("status") == "maintained" and skills[member]["status"] != "maintained":
                raise ValueError(f"Maintained bundle includes legacy skill: {name}/{member}")
        if bundle.get("status") not in {"maintained", "legacy"} or not bundle.get("description"):
            raise ValueError(f"Invalid bundle metadata: {name}")
    return data


def marketplace(data: dict) -> dict:
    return {
        "name": "jonesrussell-skills",
        "owner": {"name": "Russell Jones"},
        "metadata": {"version": data["version"], "description": "Practical tutorial, planning and repository skills"},
        "plugins": [
            {
                "name": name,
                "source": "./",
                "version": data["version"],
                "description": ("Legacy, review before use. " if entry["status"] == "legacy" else "") + entry["description"],
                "skills": [f"./skills/{member}" for member in entry["skills"]],
            }
            for name, entry in data["bundles"].items()
        ],
    }


def catalog_markdown(data: dict) -> str:
    lines = ["# Skill catalog", "", "Generated from `catalog.json` with `python scripts/catalog.py generate`.", "",
             "Start with [the tutorial guide](tutorials.md). **Maintained** means reviewed for the documented scope; it does not promise every agent runtime or model has been tested. Removed workflows are listed in [the retirement index](retired.md), outside the installable tree.", ""]
    for status in ("maintained", "legacy", "retired"):
        entries = [(n, e) for n, e in data["skills"].items() if e["status"] == status]
        if not entries:
            continue
        lines += [f"## {status.title()} ({len(entries)})", "", "| Skill | Category | Purpose |", "| --- | --- | --- |"]
        for name, entry in sorted(entries):
            summary = entry["summary"].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| [{name}](../skills/{name}/SKILL.md) | {entry['category']} | {summary} |")
        lines.append("")
    lines += ["## Requirements and evidence", ""]
    for name, entry in sorted(data["skills"].items()):
        lines += [f"### {name}", "", entry.get("requirements", "See the skill's prerequisites."), "", entry["review_note"], ""]
        if entry.get("evals"):
            lines += [f"[Behavior cases](../skills/{name}/{entry['evals']}) are inputs for evaluation, not recorded model results.", ""]
    lines += ["## Bundles", "", "Each marketplace entry lists its exact skill directories. Installing a bundle does not install the entire collection.", ""]
    for name, entry in data["bundles"].items():
        lines += [f"- **{name}** ({entry['status']}): " + ", ".join(f"`{s}`" for s in entry["skills"])]
    return "\n".join(lines) + "\n"


def retirement_markdown(data: dict) -> str:
    lines = ["# Retired skills", "", "Removed from the active collection in version 2.0.0. Git history is preserved. These links are historical recovery evidence, not recommended installation targets.", "",
             "Removal here does not uninstall existing local copies or client plugin caches. Review old installations using your client's plugin manager; the repository installer never prunes them.", "",
             "A project-specific workflow may still be useful in its owning project. This index does not assert that a replacement has been migrated or verified there.", "",
             "| Historical skill | Disposition | Reason |", "| --- | --- | --- |"]
    for name, entry in sorted(data.get("retired", {}).items()):
        url = f"https://github.com/jonesrussell/skills/tree/{entry['revision']}/skills/{name}"
        lines.append(f"| [{name}]({url}) | {entry['disposition']} | {entry['reason']} |")
    lines += ["", "The historical writing evaluation runner, fixtures and captured model runs, Claudia reference docs, old implementation plans and copied specification are recoverable at the same pre-cleanup revision. Those writing checks do not validate the current five-skill collection.", ""]
    return "\n".join(lines)


def generated_files(data: dict) -> dict[str, str]:
    return {
        "docs/catalog.md": catalog_markdown(data),
        "docs/retired.md": retirement_markdown(data),
        ".claude-plugin/marketplace.json": json.dumps(marketplace(data), indent=2) + "\n",
        **{f"skills/{name}/LICENSE.txt": (ROOT / "LICENSE").read_text(encoding="utf-8") for name in data["skills"]},
    }


def check_references(root: Path, data: dict) -> list[str]:
    errors = []
    sources = [root / "README.md", *(root / "docs").glob("*.md")]
    for name, entry in data["skills"].items():
        if entry["status"] == "maintained":
            sources.extend((root / "skills" / name).rglob("*.md"))
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
            target = target.split("#", 1)[0].strip("<>")
            if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            if not (source.parent / target).exists():
                errors.append(f"Missing local link: {source.relative_to(root)} -> {target}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("generate", "check"))
    args = parser.parse_args(argv)
    try:
        data = load_catalog()
        errors = []
        for name, content in generated_files(data).items():
            path = ROOT / name
            if args.action == "generate":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
            elif not path.exists() or path.read_text(encoding="utf-8") != content:
                errors.append(f"Generated file is stale: {name}")
        if args.action == "check":
            errors.extend(check_references(ROOT, data))
        if errors:
            raise ValueError("\n".join(errors))
        print(f"OK: {len(data['skills'])} cataloged skills, {len(data['bundles'])} explicit bundles ({args.action})")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
