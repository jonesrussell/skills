"""Create missing project-management files without overwriting user work."""
from __future__ import annotations
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

VERSION = "1.0.0"
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "project"
MANIFEST = Path(".project/kickoff.json")
FIELDS = {"name", "slug", "owner", "date", "purpose", "stage", "prefix"}
TOKEN = re.compile(r"\{\{([A-Z_]+)\}\}")

def is_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    # Python 3.11 lacks Path.is_junction; Windows reparse attributes cover junctions.
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)

def inputs(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ValueError("Config must contain exactly: " + ", ".join(sorted(FIELDS)))
    for key, value in data.items():
        if not isinstance(value, str) or not value.strip() or len(value) > 1200:
            raise ValueError(f"Invalid text field: {key}")
        if any(ord(char) < 32 for char in value):
            raise ValueError(f"Config fields must be single-line text: {key}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["slug"]):
        raise ValueError("Slug must contain lowercase letters, digits and hyphens")
    if not re.fullmatch(r"[A-Z][A-Z0-9]{0,9}", data["prefix"]):
        raise ValueError("Task prefix must be 1-10 uppercase letters/digits")
    date.fromisoformat(data["date"])
    return data

def safe_root(destination: Path) -> Path:
    if not destination.is_absolute():
        raise ValueError("Destination must be absolute")
    if ".." in destination.parts:
        raise ValueError("Destination must not contain parent traversal")
    if destination == Path(destination.anchor):
        raise ValueError("Destination must be a project directory, not a drive root")
    # Check links before resolving so junctions cannot redirect writes.
    for candidate in (*reversed(destination.parents), destination):
        if is_link(candidate):
            raise ValueError(f"Linked destination requires manual handling: {candidate}")
        if candidate.exists() and not candidate.is_dir():
            raise ValueError(f"Directory path occupied by a file: {candidate}")
    return destination.resolve()

def render(data: dict[str, str]) -> dict[Path, str]:
    replacements = {key.upper(): value for key, value in data.items()}
    files: dict[Path, str] = {}
    for template in sorted(ASSETS.rglob("*.tpl")):
        content = template.read_text(encoding="utf-8")
        missing = set(TOKEN.findall(content)) - replacements.keys()
        if missing:
            raise ValueError(f"Unknown template fields: {sorted(missing)}")
        files[template.relative_to(ASSETS).with_suffix("")] = TOKEN.sub(
            lambda match: replacements[match[1]], content)
    if not files:
        raise ValueError("No project templates found")
    origin = {
        "schema_version": 1, "template": "project-kickoff", "template_version": VERSION,
        "inputs": data,
        "baseline_sha256": {path.as_posix(): hashlib.sha256(content.encode("utf-8")).hexdigest()
                            for path, content in files.items()},
    }
    files[MANIFEST] = json.dumps(origin, indent=2, ensure_ascii=False) + "\n"
    return files

def preflight(root: Path, files: dict[Path, str], data: dict[str, str]) -> None:
    for relative in files:
        target = root / relative
        safe_root(target.parent)
        if is_link(target):
            raise ValueError(f"Refusing linked target: {target}")
        if target.exists() and not target.is_file():
            raise ValueError(f"Expected a file path: {target}")
    origin_path = root / MANIFEST
    if origin_path.exists():
        origin = json.loads(origin_path.read_text(encoding="utf-8"))
        if origin.get("inputs") != data or origin.get("template_version") != VERSION:
            raise ValueError("Existing kickoff identity/version differs; merge changes manually")

def scaffold(destination: Path, data: dict[str, str], apply: bool) -> list[str]:
    root = safe_root(destination)
    files = render(data)
    preflight(root, files, data)
    results = []
    for relative, content in files.items():
        target = root / relative
        if target.exists():
            results.append(f"KEEP {relative.as_posix()}")
            continue
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation preserves files created after preflight too.
            try:
                with target.open("x", encoding="utf-8", newline="\n") as stream:
                    stream.write(content)
            except FileExistsError:
                results.append(f"KEEP {relative.as_posix()} (created concurrently)")
                continue
        results.append(f"{'CREATED' if apply else 'WOULD CREATE'} {relative.as_posix()}")
    return results

def check(destination: Path) -> list[str]:
    root = safe_root(destination)
    required = [p.relative_to(ASSETS).with_suffix("") for p in ASSETS.rglob("*.tpl")]
    errors = [f"Missing {p.as_posix()}" for p in (*required, MANIFEST) if not (root / p).is_file()]
    if errors:
        raise ValueError("; ".join(errors))
    origin = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    if origin.get("schema_version") != 1 or origin.get("template") != "project-kickoff":
        raise ValueError("Unsupported kickoff manifest")
    sources = [root / "AGENTS.md", root / "README.md", *(root / "docs").rglob("*.md")]
    for source in sources:
        text = source.read_text(encoding="utf-8")
        if TOKEN.search(text):
            errors.append(f"Unresolved field in {source.relative_to(root)}")
        for link in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
            target = link.split("#", 1)[0].strip("<>")
            if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            if not (source.parent / target).exists():
                errors.append(f"Missing local link {target} in {source.relative_to(root)}")
    if errors:
        raise ValueError("; ".join(errors))
    return [f"OK: {len(required)} starter files, origin manifest and Markdown file links",
            "Content accuracy, remote links, HTML rendering and product behavior are not checked."]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("preview", "apply", "check"))
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    try:
        if args.action == "check":
            result = check(args.destination)
        elif args.config is None:
            parser.error("preview/apply require --config")
        else:
            result = scaffold(args.destination, inputs(args.config), args.action == "apply")
        print("\n".join(result))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
