"""Deterministic hard-rule checks for writing skill evals."""

from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "evals" / "fixtures" / "writing"
PROCESS_BEHAVIOR_RUBRIC_PATH = REPO_ROOT / "evals" / "rubrics" / "process-behavior.json"
SUPPORTED_RULE_IDS = {
    "required_greeting",
    "required_farewell",
    "artifact_path_pattern",
    "em_dash_disallowed",
}


@dataclass(frozen=True)
class RuleEvaluation:
    """Result of running the deterministic hard rules for a skill output."""

    skill: str
    checked_rule_ids: tuple[str, ...] = field(default_factory=tuple)
    passed_rule_ids: tuple[str, ...] = field(default_factory=tuple)
    failed_rule_ids: tuple[str, ...] = field(default_factory=tuple)
    messages: tuple[str, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        return not self.failed_rule_ids


@functools.lru_cache(maxsize=None)
def _load_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _validate_rule_id(rule_id: Any, *, label: str, path: Path) -> str:
    if not isinstance(rule_id, str) or not rule_id.strip():
        raise ValueError(f"{path} {label} must contain non-empty strings")
    if rule_id not in SUPPORTED_RULE_IDS:
        raise ValueError(f"{path} {label} contains unsupported rule id: {rule_id}")
    return rule_id


def _load_fixture_rules(skill: str) -> tuple[tuple[str, ...], Mapping[str, Any]]:
    fixture_path = FIXTURE_ROOT / f"{skill}.json"
    payload = _load_json(fixture_path)
    rule_checks_raw = payload.get("hard_rule_checks")
    if not isinstance(rule_checks_raw, list):
        raise ValueError(f"{fixture_path} hard_rule_checks must be a list")
    hard_rule_checks = tuple(
        _validate_rule_id(rule_id, label="hard_rule_checks", path=fixture_path) for rule_id in rule_checks_raw
    )
    hard_rules = payload.get("hard_rules", {})
    if hard_rules is None:
        hard_rules = {}
    if not isinstance(hard_rules, Mapping):
        raise ValueError(f"{fixture_path} hard_rules must be a JSON object")
    actual_rule_ids = tuple(key for key in hard_rules.keys())
    for rule_id in actual_rule_ids:
        _validate_rule_id(rule_id, label="hard_rules", path=fixture_path)
    if set(actual_rule_ids) != set(hard_rule_checks):
        missing = sorted(set(hard_rule_checks) - set(actual_rule_ids))
        extra = sorted(set(actual_rule_ids) - set(hard_rule_checks))
        problems: list[str] = []
        if missing:
            problems.append("missing configs for " + ", ".join(missing))
        if extra:
            problems.append("unexpected configs for " + ", ".join(extra))
        raise ValueError(f"{fixture_path} hard_rules and hard_rule_checks must match exactly: {'; '.join(problems)}")
    return hard_rule_checks, hard_rules


def _load_active_rule_ids() -> tuple[str, ...]:
    payload = _load_json(PROCESS_BEHAVIOR_RUBRIC_PATH)
    rule_checks = payload.get("rule_checks", ())
    if not isinstance(rule_checks, list):
        raise ValueError("process-behavior rubric rule_checks must be a list")
    normalized = tuple(_validate_rule_id(rule, label="rule_checks", path=PROCESS_BEHAVIOR_RUBRIC_PATH) for rule in rule_checks)
    if len(set(normalized)) != len(normalized):
        raise ValueError("process-behavior rubric rule_checks must not contain duplicates")
    unknown = sorted(set(normalized) - SUPPORTED_RULE_IDS)
    if unknown:
        raise ValueError("process-behavior rubric contains unsupported rule ids: " + ", ".join(unknown))
    return normalized


def _paragraphs(text: str) -> tuple[str, ...]:
    normalized = text.strip()
    if normalized.startswith("---"):
        parts = normalized.split("\n")
        if parts and parts[0].strip() == "---":
            for index in range(1, len(parts)):
                if parts[index].strip() == "---":
                    normalized = "\n".join(parts[index + 1 :]).strip()
                    break

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    return tuple(paragraphs)


def _check_required_paragraph(
    *,
    rule_id: str,
    text: str,
    expected: str,
    position: str,
) -> tuple[bool, str]:
    paragraphs = _paragraphs(text)
    if not paragraphs:
        return False, f"{rule_id}: output is empty"
    if position == "first":
        actual = paragraphs[0]
        if actual == expected:
            return True, ""
        return False, f"{rule_id}: expected first paragraph to be {expected!r}, found {actual!r}"
    if position == "last":
        actual = paragraphs[-1]
        if actual == expected:
            return True, ""
        return False, f"{rule_id}: expected last paragraph to be {expected!r}, found {actual!r}"
    raise ValueError(f"unsupported paragraph position: {position}")


def _check_artifact_path(rule_id: str, artifact_path: str | None, config: Mapping[str, Any]) -> tuple[bool, str]:
    if artifact_path is None or not str(artifact_path).strip():
        return False, f"{rule_id}: artifact path is missing or blank"

    value = str(artifact_path)
    prefix = config.get("prefix")
    if isinstance(prefix, str) and prefix and not value.startswith(prefix):
        return False, f"{rule_id}: expected path to start with {prefix!r}, found {value!r}"

    suffix = config.get("suffix")
    if isinstance(suffix, str) and suffix and not value.endswith(suffix):
        return False, f"{rule_id}: expected path to end with {suffix!r}, found {value!r}"

    contains = config.get("contains")
    if isinstance(contains, str) and contains and contains not in value:
        return False, f"{rule_id}: expected path to contain {contains!r}, found {value!r}"

    pattern = config.get("pattern")
    if isinstance(pattern, str) and pattern:
        if re.fullmatch(pattern, value) is None:
            return False, f"{rule_id}: expected path to match {pattern!r}, found {value!r}"

    return True, ""


def _check_em_dash(rule_id: str, text: str, config: Mapping[str, Any]) -> tuple[bool, str]:
    forbidden = config.get("character", "—")
    if not isinstance(forbidden, str) or not forbidden:
        forbidden = "—"
    if forbidden in text:
        return False, f"{rule_id}: found forbidden character {forbidden!r}"
    return True, ""


def evaluate_rules(
    skill: str,
    text: str,
    artifact_path: str | None,
    *,
    rule_ids: tuple[str, ...] | None = None,
) -> RuleEvaluation:
    """Evaluate the deterministic hard rules for a writing skill output."""

    active_rule_ids = _load_active_rule_ids()
    hard_rule_checks, fixture_rules = _load_fixture_rules(skill)
    selected_rule_ids = hard_rule_checks if rule_ids is None else rule_ids

    unknown_rule_ids = sorted(set(selected_rule_ids) - set(hard_rule_checks))
    if unknown_rule_ids:
        raise ValueError(
            f"{skill} case hard_rule_checks must be a subset of fixture hard_rule_checks: {', '.join(unknown_rule_ids)}"
        )
    if set(selected_rule_ids) - set(active_rule_ids):
        missing = ", ".join(sorted(set(selected_rule_ids) - set(active_rule_ids)))
        raise ValueError(f"{skill} hard_rule_checks reference rules missing from process-behavior rubric: {missing}")
    if set(hard_rule_checks) - set(active_rule_ids):
        missing = ", ".join(sorted(set(hard_rule_checks) - set(active_rule_ids)))
        raise ValueError(f"{skill} hard_rule_checks reference rules missing from process-behavior rubric: {missing}")

    passed_rule_ids: list[str] = []
    failed_rule_ids: list[str] = []
    messages: list[str] = []

    for rule_id in selected_rule_ids:
        config = fixture_rules[rule_id]
        if not isinstance(config, Mapping):
            raise ValueError(f"fixture rule {rule_id} for {skill} must be a JSON object")

        if rule_id in {"required_greeting", "required_farewell"}:
            expected = config.get("text")
            position = config.get("paragraph_position")
            if not isinstance(expected, str) or not expected.strip():
                raise ValueError(f"{skill} {rule_id} requires a non-empty text value")
            if position not in {"first", "last"}:
                raise ValueError(f"{skill} {rule_id} requires paragraph_position to be first or last")
            passed, message = _check_required_paragraph(
                rule_id=rule_id,
                text=text,
                expected=expected,
                position=position,
            )
        elif rule_id == "artifact_path_pattern":
            passed, message = _check_artifact_path(rule_id, artifact_path, config)
        elif rule_id == "em_dash_disallowed":
            passed, message = _check_em_dash(rule_id, text, config)
        else:
            raise ValueError(f"unsupported hard rule: {rule_id}")

        if passed:
            passed_rule_ids.append(rule_id)
            continue

        failed_rule_ids.append(rule_id)
        messages.append(message)

    return RuleEvaluation(
        skill=skill,
        checked_rule_ids=selected_rule_ids,
        passed_rule_ids=tuple(passed_rule_ids),
        failed_rule_ids=tuple(failed_rule_ids),
        messages=tuple(messages),
    )
