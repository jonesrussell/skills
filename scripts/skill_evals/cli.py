"""CLI scaffold for running skill evaluation suites."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone
from statistics import mean, pvariance
from typing import Any

from scripts.skill_evals.comparison import compare_runs, load_json_payload
from scripts.skill_evals.fixtures import load_fixtures
from scripts.skill_evals.models import EvalCaseResult, EvalRunMetadata, EvalRunResult, ResultValidationError, RubricDefinition
from scripts.skill_evals.reporting import write_comparison_markdown, write_json_report, write_run_markdown
from scripts.skill_evals.rules import evaluate_rules
from scripts.skill_evals.runners import CodexRunner, CommandRunner, EvalRunner, MockRunner, RunnerError, load_mock_outputs


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MOCK_OUTPUTS_PATH = REPO_ROOT / "tests" / "fixtures" / "evals" / "mock_outputs.json"
_CONTRAST_PATTERNS = (
    re.compile(r"\bnot\b[^.!?\n]{0,80}\bit\b", re.IGNORECASE),
    re.compile(r"\bnot\b[^.!?\n]{0,80}\bbut\b", re.IGNORECASE),
    re.compile(r"\brather than\b", re.IGNORECASE),
    re.compile(r"\binstead\b", re.IGNORECASE),
)


def build_runner(name: str, options: dict[str, Any]) -> EvalRunner:
    if name == "mock":
        outputs_path = Path(options.get("outputs_path") or DEFAULT_MOCK_OUTPUTS_PATH)
        return MockRunner(load_mock_outputs(outputs_path))
    if name == "codex":
        return CodexRunner(
            repo_root=REPO_ROOT,
            codex_command=options.get("codex_command"),
            model=options.get("model"),
            profile=options.get("profile"),
        )
    if name == "command":
        command = options.get("command")
        if command is None:
            raise ValueError("command runner requires a command")
        if isinstance(command, (str, Path)):
            command = [str(command)]
        return CommandRunner([str(token) for token in command])
    raise ValueError(f"unsupported runner: {name}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="eval_skills.py", description="Run repo-local writing skill evaluation fixtures.")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    run_parser = subparsers.add_parser("run", help="Run a suite of fixtures with the selected runner.")
    run_parser.add_argument("--suite", default="writing", help="Fixture suite to run.")
    run_parser.add_argument(
        "--runner",
        choices=("mock", "codex", "command"),
        default="mock",
        help="Runner implementation to use.",
    )
    run_parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "evals" / "results" / "local-smoke",
        help="Directory where run.json will be written.",
    )
    run_parser.add_argument(
        "--command",
        nargs="+",
        dest="runner_command",
        help="Command to execute for the command runner.",
    )
    run_parser.add_argument("--model", default=None, help="Model override for the codex runner.")
    run_parser.add_argument("--profile", default=None, help="Profile override for the codex runner.")
    run_parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="Restrict the run to one or more skill ids. Repeatable.",
    )
    run_parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Restrict the run to one or more case ids. Repeatable.",
    )
    run_parser.add_argument(
        "--mock-outputs",
        type=Path,
        default=DEFAULT_MOCK_OUTPUTS_PATH,
        help="Path to the mock output fixture file.",
    )

    compare_parser = subparsers.add_parser("compare", help="Compare a candidate run against a baseline run.")
    compare_parser.add_argument("--baseline", type=Path, required=True, help="Path to the baseline run JSON.")
    compare_parser.add_argument("--candidate", type=Path, required=True, help="Path to the candidate run JSON.")
    compare_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where comparison.json and comparison.md will be written.",
    )

    promote_parser = subparsers.add_parser("promote-baseline", help="Promote a completed candidate run into baselines.")
    promote_parser.add_argument("--candidate", type=Path, required=True, help="Path to the candidate run directory.")
    promote_parser.add_argument("--baseline", type=Path, required=True, help="Path to the baseline directory to create.")
    return parser.parse_args(argv)


def _shared_version(values: list[str | None], *, label: str, suite: str) -> str:
    versions = {value for value in values if value is not None}
    if any(value is None for value in values) or len(versions) != 1:
        raise ValueError(f"{label} versions for suite {suite} must be present and identical")
    return next(iter(versions))


def _load_run_metadata(*, suite: str, runner: EvalRunner, fixtures: list[Any]) -> EvalRunMetadata:
    fixture_version = _shared_version([fixture.version for fixture in fixtures], label="fixture", suite=suite)

    rubric_paths = (
        REPO_ROOT / "evals" / "rubrics" / "writing-quality.json",
        REPO_ROOT / "evals" / "rubrics" / "process-behavior.json",
    )
    rubrics = [RubricDefinition.from_dict(load_json_payload(path)) for path in rubric_paths]
    rubric_version = _shared_version([rubric.version for rubric in rubrics], label="rubric", suite=suite)

    command = tuple(getattr(runner, "command", ()))
    metadata_kwargs: dict[str, Any] = {
        "runner": runner.name,
        "fixture_version": fixture_version,
        "rubric_version": rubric_version,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    if command:
        metadata_kwargs["command"] = command
    return EvalRunMetadata.from_dict(metadata_kwargs)


def run_suite(
    *,
    suite: str,
    runner: EvalRunner,
    output_dir: Path,
    skills: tuple[str, ...] = (),
    case_ids: tuple[str, ...] = (),
) -> EvalRunResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    fixtures = list(load_fixtures(suite=suite))
    if skills:
        skill_filter = set(skills)
        fixtures = [fixture for fixture in fixtures if fixture.skill in skill_filter]
    if not fixtures:
        raise ValueError(f"no fixtures found for suite {suite}")
    run_metadata = _load_run_metadata(suite=suite, runner=runner, fixtures=fixtures)

    run_results: list[EvalCaseResult] = []
    style_signal_cases: list[EvalCaseResult] = []
    summary_lines: list[str] = []
    case_filter = set(case_ids)
    for fixture in fixtures:
        for case in fixture.cases:
            if case_filter and case.case_id not in case_filter:
                continue
            case_metadata = {
                "suite": fixture.suite,
                "skill": fixture.skill,
                "case_id": case.case_id,
            }
            result_payload = runner.run_case(case, case_metadata)
            case_result = _finalize_case_result(fixture.skill, case, result_payload)
            run_results.append(case_result)
            if getattr(case, "include_in_style_signals", True):
                style_signal_cases.append(case_result)
            summary_lines.append(f"{fixture.skill}:{case.case_id} -> {'PASS' if case_result.passed else 'FAIL'}")

    if not run_results:
        raise ValueError(f"no cases selected for suite {suite}")

    result = EvalRunResult(
        suite=suite,
        skill="__suite__",
        runner=runner.name,
        generated_at=run_metadata.generated_at,
        summary="\n".join(summary_lines),
        cases=tuple(run_results),
        metadata=run_metadata,
        style_signals=_extract_style_signals(style_signal_cases),
    )
    run_payload = _run_payload(result)
    write_json_report(output_dir / "run.json", run_payload)
    write_run_markdown(output_dir / "summary.md", result)
    return result


def promote_baseline(*, candidate_dir: Path, baseline_dir: Path) -> EvalRunResult:
    run_path = candidate_dir / "run.json"
    if not run_path.is_file():
        raise ValueError(f"candidate run is missing {run_path.name}")
    if baseline_dir.exists():
        raise ValueError(f"baseline directory already exists: {baseline_dir}")
    payload = load_json_payload(run_path)
    _require_metadata_consistency(payload)
    try:
        result = EvalRunResult.from_dict(payload)
    except ResultValidationError as exc:
        raise ValueError(f"candidate run {run_path.name} is not eligible for promotion") from exc
    _require_promotion_metadata(result)

    baseline_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(candidate_dir, baseline_dir, dirs_exist_ok=True)
    return result


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.subcommand == "run":
            runner_options: dict[str, Any] = {}
            if args.runner == "command":
                runner_options["command"] = args.runner_command
            elif args.runner == "codex":
                runner_options["model"] = args.model
                runner_options["profile"] = args.profile
            else:
                runner_options["outputs_path"] = args.mock_outputs

            runner = build_runner(args.runner, runner_options)
            result = run_suite(
                suite=args.suite,
                runner=runner,
                output_dir=args.output_dir,
                skills=tuple(args.skills or ()),
                case_ids=tuple(args.case_ids or ()),
            )
            print(json.dumps(_run_payload(result), indent=2))
            return 0

        if args.subcommand == "compare":
            baseline_payload = load_json_payload(args.baseline)
            candidate_payload = load_json_payload(args.candidate)
            result = compare_runs(baseline_payload, candidate_payload)
            output_dir = args.output_dir or args.candidate.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            write_json_report(output_dir / "comparison.json", result.to_dict())
            write_comparison_markdown(output_dir / "comparison.md", result)
            print(json.dumps(result.to_dict(), indent=2))
            return 1 if result.status == "regression" else 0

        if args.subcommand == "promote-baseline":
            result = promote_baseline(candidate_dir=args.candidate, baseline_dir=args.baseline)
            print(
                json.dumps(
                    {
                        "status": "promoted",
                        "candidate": str(args.candidate),
                        "baseline": str(args.baseline),
                        "metadata": result.metadata.to_dict() if result.metadata is not None else None,
                    },
                    indent=2,
                )
            )
            return 0
    except (ValueError, RunnerError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 2


def _run_payload(result: EvalRunResult) -> dict[str, Any]:
    payload = result.to_dict()
    passed_cases = sum(1 for case in result.cases if case.passed)
    failed_cases = len(result.cases) - passed_cases
    total_cases = len(result.cases)
    payload["rule_failures"] = failed_cases
    payload["rubric"] = {
        "pass_rate": (passed_cases / total_cases) if total_cases else 0.0,
    }
    if result.style_signals is not None:
        payload["style_signals"] = dict(result.style_signals)
    return payload


def _finalize_case_result(skill: str, case: Any, payload: dict[str, Any]) -> EvalCaseResult:
    case_result = EvalCaseResult.from_dict(payload)
    rule_result = evaluate_rules(
        skill=skill,
        text=case_result.output,
        artifact_path=case_result.artifact_path,
        rule_ids=getattr(case, "hard_rule_checks", None),
    )
    if rule_result.passed:
        return case_result

    return EvalCaseResult(
        case_id=case_result.case_id,
        passed=False,
        output=case_result.output,
        artifact_path=case_result.artifact_path,
        messages=tuple(case_result.messages) + tuple(rule_result.messages),
    )


def _extract_style_signals(cases: list[EvalCaseResult]) -> dict[str, int | float] | None:
    texts = [text for case in cases if (text := _case_text(case))]
    if not texts:
        return None

    em_dash_count = 0
    contrast_pattern_count = 0
    sentence_lengths: list[int] = []
    paragraph_lengths: list[int] = []

    for text in texts:
        em_dash_count += text.count("—")
        contrast_pattern_count += sum(len(pattern.findall(text)) for pattern in _CONTRAST_PATTERNS)

        sentences = _split_sentences(text)
        sentence_lengths.extend(_word_count(sentence) for sentence in sentences)

        paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
        paragraph_lengths.extend(_word_count(paragraph) for paragraph in paragraphs)

    style_signals: dict[str, int | float] = {
        "em_dash_count": em_dash_count,
        "contrast_pattern_count": contrast_pattern_count,
    }
    if sentence_lengths:
        style_signals["avg_sentence_length"] = mean(sentence_lengths)
        style_signals["sentence_length_variance"] = pvariance(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
    if paragraph_lengths:
        style_signals["avg_paragraph_length"] = mean(paragraph_lengths)
    return style_signals


def _case_text(case: EvalCaseResult) -> str:
    parts = [case.output.strip()] if case.output.strip() else []
    parts.extend(message.strip() for message in case.messages if message.strip())
    return "\n".join(parts).strip()


def _split_sentences(text: str) -> list[str]:
    normalized = text.replace("\n", " ")
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", normalized) if sentence.strip()]
    if sentences:
        return sentences
    if normalized.strip():
        return [normalized.strip()]
    return []


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\S+\b", text))


def _require_promotion_metadata(result: EvalRunResult) -> None:
    metadata = result.metadata
    if metadata is None:
        raise ValueError("candidate run is missing metadata")
    if not metadata.runner or not metadata.fixture_version or not metadata.rubric_version or not metadata.generated_at:
        raise ValueError("candidate run metadata is incomplete")


def _require_metadata_consistency(payload: dict[str, Any]) -> None:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return

    top_level_runner = payload.get("runner")
    nested_runner = metadata.get("runner")
    if isinstance(top_level_runner, str) and isinstance(nested_runner, str) and top_level_runner != nested_runner:
        raise ValueError("candidate run metadata conflicts: runner")

    top_level_generated_at = payload.get("generated_at")
    nested_generated_at = metadata.get("generated_at")
    if (
        isinstance(top_level_generated_at, str)
        and isinstance(nested_generated_at, str)
        and top_level_generated_at != nested_generated_at
    ):
        raise ValueError("candidate run metadata conflicts: generated_at")
