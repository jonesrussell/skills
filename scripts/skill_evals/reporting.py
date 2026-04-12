"""Human-readable and machine-readable reporting helpers for skill evals."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.skill_evals.comparison import ComparisonResult
from scripts.skill_evals.models import EvalRunResult


def write_json_report(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def render_run_markdown(run: EvalRunResult) -> str:
    passed = sum(1 for case in run.cases if case.passed)
    failed = len(run.cases) - passed
    lines = [
        "# Eval Summary",
        "",
        f"- Suite: {run.suite}",
        f"- Skill: {run.skill}",
        f"- Runner: {run.runner or 'unknown'}",
        f"- Passed: {passed}",
        f"- Failed: {failed}",
    ]
    if run.summary:
        lines.extend(["", "## Case Summary", "", run.summary])
    if run.style_signals:
        lines.extend(["", "## Style Signals"])
        for name, value in sorted(run.style_signals.items()):
            lines.append(f"- {name}: {value}")
    return "\n".join(lines) + "\n"


def write_run_markdown(path: Path, run: EvalRunResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_run_markdown(run), encoding="utf-8")


def _render_metric_line(name: str, baseline: int | float | None, candidate: int | float | None) -> str:
    return f"- {name}: baseline {baseline} -> candidate {candidate}"


def render_comparison_markdown(result: ComparisonResult) -> str:
    lines = [
        "# Eval Comparison",
        "",
        f"- Status: {result.status}",
        f"- Rule failures: baseline {result.baseline_rule_failures} -> candidate {result.candidate_rule_failures}",
    ]

    if result.metric_comparisons:
        lines.extend(["", "## Rubric Metrics"])
        for metric in result.metric_comparisons:
            lines.append(_render_metric_line(metric.name, metric.baseline, metric.candidate))

    if result.style_signal_comparisons:
        lines.extend(["", "## Style Signals"])
        lines.append("- Heuristic signals that help spot repetitive or overly mechanical writing.")
        for metric in result.style_signal_comparisons:
            lines.append(_render_metric_line(metric.name, metric.baseline, metric.candidate))

    if result.regressions:
        lines.extend(["", "## Regressions"])
        lines.extend(f"- {item}" for item in result.regressions)

    if result.improvements:
        lines.extend(["", "## Improvements"])
        lines.extend(f"- {item}" for item in result.improvements)

    return "\n".join(lines) + "\n"


def write_comparison_markdown(path: Path, result: ComparisonResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_comparison_markdown(result), encoding="utf-8")
