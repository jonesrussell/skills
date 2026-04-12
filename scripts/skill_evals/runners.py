"""Provider-agnostic runners for skill evaluation cases."""

from __future__ import annotations

import json
import subprocess
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.skill_evals.models import EvalCase


class RunnerError(RuntimeError):
    """Raised when a runner cannot execute a case."""


class EvalRunner(ABC):
    """Base interface for all evaluation runners."""

    name = "base"

    @abstractmethod
    def run_case(self, case: EvalCase, metadata: Mapping[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockRunner(EvalRunner):
    name = "mock"

    def __init__(self, outputs: Mapping[str, Any]):
        self._outputs = dict(outputs)

    def run_case(self, case: EvalCase, metadata: Mapping[str, Any]) -> dict[str, Any]:
        try:
            payload = self._outputs[case.case_id]
        except KeyError as exc:
            raise RunnerError(f"missing mock output for case {case.case_id}") from exc
        if not isinstance(payload, Mapping):
            raise RunnerError(f"mock output for case {case.case_id} must be a mapping")
        return deepcopy(dict(payload))


class CommandRunner(EvalRunner):
    name = "command"

    def __init__(self, command: Sequence[str]):
        if not command:
            raise ValueError("command runner requires at least one command token")
        self.command = tuple(command)

    def run_case(self, case: EvalCase, metadata: Mapping[str, Any]) -> dict[str, Any]:
        payload = {
            "case": case.to_dict(),
            "metadata": _json_safe(metadata),
        }
        try:
            completed = subprocess.run(
                list(self.command),
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=True,
            )
        except (FileNotFoundError, OSError) as exc:
            raise RunnerError(f"command runner could not start for case {case.case_id}") from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else ""
            message = f"command runner failed for case {case.case_id}"
            if stderr:
                message = f"{message}: {stderr}"
            raise RunnerError(message) from exc

        try:
            result = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RunnerError(f"command runner returned invalid JSON for case {case.case_id}") from exc
        if not isinstance(result, Mapping):
            raise RunnerError(f"command runner output for case {case.case_id} must be a mapping")
        return dict(result)


class CodexRunner(EvalRunner):
    """Execute a case against the local Codex CLI using the real skill file."""

    name = "codex"

    def __init__(
        self,
        *,
        repo_root: Path,
        codex_command: Sequence[str] | None = None,
        model: str | None = None,
        profile: str | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.codex_command = tuple(codex_command or ("codex",))
        self.model = model
        self.profile = profile

    def run_case(self, case: EvalCase, metadata: Mapping[str, Any]) -> dict[str, Any]:
        skill = metadata.get("skill")
        if not isinstance(skill, str) or not skill.strip():
            raise RunnerError(f"codex runner requires skill metadata for case {case.case_id}")

        skill_path = self.repo_root / "skills" / skill / "SKILL.md"
        if not skill_path.is_file():
            raise RunnerError(f"codex runner could not find skill file for {skill}: {skill_path}")

        prompt = _build_codex_prompt(
            skill=skill,
            skill_path=skill_path,
            skill_text=skill_path.read_text(encoding="utf-8"),
            case=case,
        )
        schema = _codex_result_schema()

        with tempfile.TemporaryDirectory(prefix="codex-skill-eval-") as tmpdir:
            tmpdir_path = Path(tmpdir)
            schema_path = tmpdir_path / "result.schema.json"
            output_path = tmpdir_path / "result.json"
            schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

            command = [
                *self.codex_command,
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(output_path),
                "-",
            ]
            if self.model:
                command[2:2] = ["--model", self.model]
            if self.profile:
                command[2:2] = ["--profile", self.profile]
            command[2:2] = ["-C", str(self.repo_root)]

            try:
                completed = subprocess.run(
                    command,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    check=True,
                )
            except (FileNotFoundError, OSError) as exc:
                raise RunnerError(f"codex runner could not start for case {case.case_id}") from exc
            except subprocess.CalledProcessError as exc:
                stderr = exc.stderr.strip() if exc.stderr else ""
                stdout = exc.stdout.strip() if exc.stdout else ""
                message = f"codex runner failed for case {case.case_id}"
                if stderr:
                    message = f"{message}: {stderr}"
                elif stdout:
                    message = f"{message}: {stdout}"
                raise RunnerError(message) from exc

            if not output_path.is_file():
                raise RunnerError(f"codex runner did not produce output for case {case.case_id}")

            try:
                result = json.loads(output_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RunnerError(f"codex runner returned invalid JSON for case {case.case_id}") from exc

        if not isinstance(result, Mapping):
            raise RunnerError(f"codex runner output for case {case.case_id} must be a mapping")

        payload = dict(result)
        payload["case_id"] = case.case_id
        return payload


def load_mock_outputs(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("mock outputs file must contain a mapping keyed by case_id")
    return dict(payload)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _build_codex_prompt(*, skill: str, skill_path: Path, skill_text: str, case: EvalCase) -> str:
    return (
        "You are running a single writing-skill evaluation case.\n\n"
        f"Skill: {skill}\n"
        f"Skill file: {skill_path}\n"
        f"Case ID: {case.case_id}\n"
        f"Expected artifact: {case.expected_artifact}\n"
        f"Rubric targets: {', '.join(case.rubric_targets) if case.rubric_targets else 'none'}\n\n"
        "Use the skill instructions below as the canonical authority for tone, structure, and workflow. "
        "Do not browse the web. Do not edit files. Produce the content the skill would produce for this prompt.\n\n"
        "<skill>\n"
        f"{skill_text}\n"
        "</skill>\n\n"
        "<task_prompt>\n"
        f"{case.prompt}\n"
        "</task_prompt>\n\n"
        "Return only a JSON object matching the provided schema with these semantics:\n"
        '- "passed": true if you produced a complete best-effort response for the case.\n'
        '- "output": the full generated content or review text.\n'
        '- "artifact_path": the exact path the skill would write, when applicable. '
        "Use repo-relative paths when the skill requires them, and preserve literal home-relative "
        'paths like "~/brand/..." when the skill specifies those.\n'
        '- "messages": short notes about assumptions or limitations.\n'
    )


def _codex_result_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["case_id", "passed", "output", "artifact_path", "messages"],
        "properties": {
            "case_id": {"type": "string"},
            "passed": {"type": "boolean"},
            "output": {"type": "string"},
            "artifact_path": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "null"},
                ]
            },
            "messages": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }
