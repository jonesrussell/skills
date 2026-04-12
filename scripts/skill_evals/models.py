"""Minimal data contracts for writing-skill evaluation fixtures and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


class FixtureValidationError(ValueError):
    """Raised when a fixture payload does not match the expected schema."""


class ResultValidationError(ValueError):
    """Raised when a result payload does not match the expected schema."""


class RubricValidationError(ValueError):
    """Raised when a rubric payload does not match the expected schema."""


def _require_mapping(
    data: Any,
    *,
    label: str,
    error_cls: type[ValueError],
) -> Mapping[str, Any]:
    if not isinstance(data, Mapping):
        raise error_cls(f"{label} must be a mapping")
    return data


def _require_non_empty_str(data: Mapping[str, Any], key: str, *, error_cls: type[ValueError]) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise error_cls(f"{key} must be a non-empty string")
    return value


def _coerce_str_tuple(value: Any, *, label: str, error_cls: type[ValueError]) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise error_cls(f"{label} must be a list of strings")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise error_cls(f"{label} must contain only non-empty strings")
        items.append(item)
    return tuple(items)


def _coerce_numeric_mapping(
    value: Any,
    *,
    label: str,
    error_cls: type[ValueError],
) -> dict[str, int | float] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise error_cls(f"{label} must be a mapping")
    items: dict[str, int | float] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise error_cls(f"{label} must contain only non-empty string keys")
        if not isinstance(item, (int, float)) or isinstance(item, bool):
            raise error_cls(f"{label} must contain only numeric values")
        items[key] = item
    return items


@dataclass(frozen=True)
class EvalRunMetadata:
    runner: str
    fixture_version: str
    rubric_version: str
    generated_at: str
    command: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: Any) -> "EvalRunMetadata":
        payload = _require_mapping(data, label="run metadata", error_cls=ResultValidationError)
        runner = _require_non_empty_str(payload, "runner", error_cls=ResultValidationError)
        fixture_version = _require_non_empty_str(payload, "fixture_version", error_cls=ResultValidationError)
        rubric_version = _require_non_empty_str(payload, "rubric_version", error_cls=ResultValidationError)
        generated_at = _require_non_empty_str(payload, "generated_at", error_cls=ResultValidationError)
        command = _coerce_str_tuple(payload.get("command"), label="command", error_cls=ResultValidationError)
        return cls(
            runner=runner,
            fixture_version=fixture_version,
            rubric_version=rubric_version,
            generated_at=generated_at,
            command=command,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "runner": self.runner,
            "fixture_version": self.fixture_version,
            "rubric_version": self.rubric_version,
            "generated_at": self.generated_at,
        }
        if self.command:
            data["command"] = list(self.command)
        return data


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    prompt: str
    expected_artifact: str
    rubric_targets: tuple[str, ...] = field(default_factory=tuple)
    hard_rule_checks: tuple[str, ...] | None = None
    include_in_style_signals: bool = True

    @classmethod
    def from_dict(cls, data: Any) -> "EvalCase":
        payload = _require_mapping(data, label="case", error_cls=FixtureValidationError)
        case_id = _require_non_empty_str(payload, "case_id", error_cls=FixtureValidationError)
        prompt = _require_non_empty_str(payload, "prompt", error_cls=FixtureValidationError)
        expected_artifact = _require_non_empty_str(payload, "expected_artifact", error_cls=FixtureValidationError)
        rubric_targets = _coerce_str_tuple(
            payload.get("rubric_targets"),
            label="rubric_targets",
            error_cls=FixtureValidationError,
        )
        hard_rule_checks = (
            _coerce_str_tuple(
                payload.get("hard_rule_checks"),
                label="hard_rule_checks",
                error_cls=FixtureValidationError,
            )
            if "hard_rule_checks" in payload
            else None
        )
        include_in_style_signals = payload.get("include_in_style_signals", True)
        if not isinstance(include_in_style_signals, bool):
            raise FixtureValidationError("include_in_style_signals must be a boolean")
        return cls(
            case_id=case_id,
            prompt=prompt,
            expected_artifact=expected_artifact,
            rubric_targets=rubric_targets,
            hard_rule_checks=hard_rule_checks,
            include_in_style_signals=include_in_style_signals,
        )

    def to_dict(self) -> dict[str, Any]:
        data = {
            "case_id": self.case_id,
            "prompt": self.prompt,
            "expected_artifact": self.expected_artifact,
            "rubric_targets": list(self.rubric_targets),
        }
        if self.hard_rule_checks is not None:
            data["hard_rule_checks"] = list(self.hard_rule_checks)
        if not self.include_in_style_signals:
            data["include_in_style_signals"] = False
        return data


@dataclass(frozen=True)
class EvalFixture:
    skill: str
    cases: tuple[EvalCase, ...]
    suite: str = "writing"
    version: str | None = None

    @classmethod
    def from_dict(cls, data: Any) -> "EvalFixture":
        payload = _require_mapping(data, label="fixture", error_cls=FixtureValidationError)
        skill = _require_non_empty_str(payload, "skill", error_cls=FixtureValidationError)
        suite = _require_non_empty_str(payload, "suite", error_cls=FixtureValidationError) if "suite" in payload else "writing"
        version = payload.get("version")
        if version is not None and (not isinstance(version, str) or not version.strip()):
            raise FixtureValidationError("version must be a non-empty string when provided")
        cases_raw = payload.get("cases")
        if not isinstance(cases_raw, list) or not cases_raw:
            raise FixtureValidationError("fixture requires at least one case")
        cases = tuple(EvalCase.from_dict(case) for case in cases_raw)
        return cls(skill=skill, cases=cases, suite=suite, version=version)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "skill": self.skill,
            "suite": self.suite,
            "cases": [case.to_dict() for case in self.cases],
        }
        if self.version is not None:
            data["version"] = self.version
        return data

    def validate_rubric_targets(self, rubric: "RubricDefinition") -> None:
        target_ids = {target for case in self.cases for target in case.rubric_targets}
        if not target_ids:
            return
        if rubric.suite != self.suite:
            raise FixtureValidationError(
                f"fixture rubric_targets require rubric suite {self.suite}, got {rubric.suite}"
            )
        if not rubric.criteria:
            raise FixtureValidationError("fixture rubric_targets require a rubric with criteria")
        known_ids = set(rubric.criterion_ids())
        unknown_ids = sorted(target_ids - known_ids)
        if unknown_ids:
            raise FixtureValidationError(
                "fixture rubric_targets must match rubric criteria ids: " + ", ".join(unknown_ids)
            )


@dataclass(frozen=True)
class EvalCaseResult:
    case_id: str
    passed: bool
    output: str = ""
    artifact_path: str | None = None
    messages: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: Any) -> "EvalCaseResult":
        payload = _require_mapping(data, label="case result", error_cls=ResultValidationError)
        case_id = _require_non_empty_str(payload, "case_id", error_cls=ResultValidationError)
        passed = payload.get("passed")
        if not isinstance(passed, bool):
            raise ResultValidationError("passed must be a boolean")
        output = payload.get("output", "")
        if not isinstance(output, str):
            raise ResultValidationError("output must be a string")
        artifact_path = payload.get("artifact_path")
        if artifact_path is not None and (not isinstance(artifact_path, str) or not artifact_path.strip()):
            raise ResultValidationError("artifact_path must be a non-empty string when provided")
        messages = _coerce_str_tuple(payload.get("messages"), label="messages", error_cls=ResultValidationError)
        return cls(
            case_id=case_id,
            passed=passed,
            output=output,
            artifact_path=artifact_path,
            messages=messages,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "case_id": self.case_id,
            "passed": self.passed,
            "output": self.output,
            "messages": list(self.messages),
        }
        if self.artifact_path is not None:
            data["artifact_path"] = self.artifact_path
        return data


@dataclass(frozen=True)
class EvalRunResult:
    suite: str
    skill: str
    cases: tuple[EvalCaseResult, ...]
    metadata: EvalRunMetadata | None = None
    runner: str = ""
    generated_at: str = ""
    summary: str = ""
    style_signals: dict[str, int | float] | None = None

    @classmethod
    def from_dict(cls, data: Any) -> "EvalRunResult":
        payload = _require_mapping(data, label="run result", error_cls=ResultValidationError)
        suite = _require_non_empty_str(payload, "suite", error_cls=ResultValidationError)
        skill = _require_non_empty_str(payload, "skill", error_cls=ResultValidationError)
        runner = payload.get("runner", "")
        if not isinstance(runner, str):
            raise ResultValidationError("runner must be a string")
        generated_at = payload.get("generated_at", "")
        if not isinstance(generated_at, str):
            raise ResultValidationError("generated_at must be a string")
        summary = payload.get("summary", "")
        if not isinstance(summary, str):
            raise ResultValidationError("summary must be a string")
        style_signals = _coerce_numeric_mapping(
            payload.get("style_signals"),
            label="style_signals",
            error_cls=ResultValidationError,
        )
        metadata_payload = payload.get("metadata")
        metadata = None
        if metadata_payload is not None:
            metadata = EvalRunMetadata.from_dict(metadata_payload)
        cases_raw = payload.get("cases")
        if not isinstance(cases_raw, list) or not cases_raw:
            raise ResultValidationError("run result requires at least one case result")
        cases = tuple(EvalCaseResult.from_dict(case) for case in cases_raw)
        return cls(
            suite=suite,
            skill=skill,
            cases=cases,
            metadata=metadata,
            runner=runner,
            generated_at=generated_at,
            summary=summary,
            style_signals=style_signals,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "suite": self.suite,
            "skill": self.skill,
            "runner": self.runner,
            "generated_at": self.generated_at,
            "summary": self.summary,
            "cases": [case.to_dict() for case in self.cases],
        }
        if self.style_signals is not None:
            data["style_signals"] = dict(self.style_signals)
        if self.metadata is not None:
            data["metadata"] = self.metadata.to_dict()
        return data


@dataclass(frozen=True)
class RubricCriterion:
    criterion_id: str
    description: str

    @classmethod
    def from_dict(cls, data: Any) -> "RubricCriterion":
        payload = _require_mapping(data, label="rubric criterion", error_cls=RubricValidationError)
        criterion_id = _require_non_empty_str(payload, "criterion_id", error_cls=RubricValidationError)
        description = _require_non_empty_str(payload, "description", error_cls=RubricValidationError)
        return cls(criterion_id=criterion_id, description=description)

    def to_dict(self) -> dict[str, Any]:
        return {
            "criterion_id": self.criterion_id,
            "description": self.description,
        }


@dataclass(frozen=True)
class RubricDefinition:
    rubric_id: str
    suite: str
    version: str | None
    criteria: tuple[RubricCriterion, ...] = field(default_factory=tuple)
    rule_checks: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: Any) -> "RubricDefinition":
        payload = _require_mapping(data, label="rubric", error_cls=RubricValidationError)
        rubric_id = _require_non_empty_str(payload, "rubric_id", error_cls=RubricValidationError)
        suite = _require_non_empty_str(payload, "suite", error_cls=RubricValidationError)
        version = payload.get("version")
        if version is not None and (not isinstance(version, str) or not version.strip()):
            raise RubricValidationError("version must be a non-empty string when provided")

        criteria_raw = payload.get("criteria")
        rule_checks_raw = payload.get("rule_checks")

        criteria: tuple[RubricCriterion, ...] = ()
        rule_checks: tuple[str, ...] = ()
        if criteria_raw is not None:
            if not isinstance(criteria_raw, list) or not criteria_raw:
                raise RubricValidationError("criteria must be a non-empty list when provided")
            criteria = tuple(RubricCriterion.from_dict(item) for item in criteria_raw)
        if rule_checks_raw is not None:
            rule_checks = _coerce_str_tuple(rule_checks_raw, label="rule_checks", error_cls=RubricValidationError)
            if not rule_checks:
                raise RubricValidationError("rule_checks must be a non-empty list when provided")

        if not criteria and not rule_checks:
            raise RubricValidationError("rubric requires criteria or rule_checks")

        return cls(
            rubric_id=rubric_id,
            suite=suite,
            version=version,
            criteria=criteria,
            rule_checks=rule_checks,
        )

    def criterion_ids(self) -> tuple[str, ...]:
        return tuple(criterion.criterion_id for criterion in self.criteria)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "rubric_id": self.rubric_id,
            "suite": self.suite,
        }
        if self.version is not None:
            data["version"] = self.version
        if self.criteria:
            data["criteria"] = [criterion.to_dict() for criterion in self.criteria]
        if self.rule_checks:
            data["rule_checks"] = list(self.rule_checks)
        return data
