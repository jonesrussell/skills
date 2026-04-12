"""Helpers for loading evaluation fixtures from the repo-local eval tree."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.skill_evals.models import EvalFixture


REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_ROOT = REPO_ROOT / "evals"
FIXTURE_ROOT = EVALS_ROOT / "fixtures"


def fixture_path(skill: str, suite: str = "writing") -> Path:
    return FIXTURE_ROOT / suite / f"{skill}.json"


def load_fixture(skill: str, suite: str = "writing") -> EvalFixture:
    path = fixture_path(skill, suite=suite)
    payload = json.loads(path.read_text(encoding="utf-8"))
    fixture = EvalFixture.from_dict(payload)
    if fixture.skill != skill:
        raise ValueError(f"fixture skill mismatch: expected {skill}, found {fixture.skill}")
    if fixture.suite != suite:
        raise ValueError(f"fixture suite mismatch: expected {suite}, found {fixture.suite}")
    return fixture


def list_fixture_paths(suite: str = "writing") -> tuple[Path, ...]:
    root = FIXTURE_ROOT / suite
    if not root.exists():
        return ()
    return tuple(path for path in sorted(root.glob("*.json")) if path.is_file())


def load_fixtures(suite: str = "writing") -> tuple[EvalFixture, ...]:
    return tuple(load_fixture(path.stem, suite=suite) for path in list_fixture_paths(suite))
