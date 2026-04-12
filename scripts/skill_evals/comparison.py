"""Comparison helpers for baseline and candidate skill eval runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from scripts.skill_evals.models import EvalRunResult


@dataclass(frozen=True)
class MetricComparison:
    """Comparison for a single rubric metric."""

    name: str
    baseline: int | float | None
    candidate: int | float | None

    @property
    def delta(self) -> int | float | None:
        if self.baseline is None or self.candidate is None:
            return None
        return self.candidate - self.baseline


@dataclass(frozen=True)
class ComparisonResult:
    """Structured comparison of a baseline run and a candidate run."""

    status: str
    baseline_rule_failures: int
    candidate_rule_failures: int
    rule_failure_delta: int
    metric_comparisons: tuple[MetricComparison, ...] = field(default_factory=tuple)
    style_signal_comparisons: tuple[MetricComparison, ...] = field(default_factory=tuple)
    regressions: tuple[str, ...] = field(default_factory=tuple)
    improvements: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "baseline_rule_failures": self.baseline_rule_failures,
            "candidate_rule_failures": self.candidate_rule_failures,
            "rule_failure_delta": self.rule_failure_delta,
            "metric_comparisons": [
                {
                    "name": metric.name,
                    "baseline": metric.baseline,
                    "candidate": metric.candidate,
                    "delta": metric.delta,
                }
                for metric in self.metric_comparisons
            ],
            "style_signal_comparisons": [
                {
                    "name": metric.name,
                    "baseline": metric.baseline,
                    "candidate": metric.candidate,
                    "delta": metric.delta,
                }
                for metric in self.style_signal_comparisons
            ],
            "regressions": list(self.regressions),
            "improvements": list(self.improvements),
        }


def _as_mapping(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, EvalRunResult):
        return payload.to_dict()
    if isinstance(payload, Mapping):
        return payload
    raise TypeError("comparison payload must be a mapping or EvalRunResult")


def _extract_rule_failures(payload: Mapping[str, Any]) -> int:
    direct_value = payload.get("rule_failures")
    if isinstance(direct_value, int) and not isinstance(direct_value, bool):
        return direct_value

    cases = payload.get("cases")
    if isinstance(cases, list):
        failures = 0
        for case in cases:
            if not isinstance(case, Mapping):
                continue
            if case.get("passed") is False:
                failures += 1
        return failures

    raise ValueError("comparison payload must include rule_failures or cases")


def _extract_numeric_metrics(payload: Mapping[str, Any], key: str) -> dict[str, int | float]:
    metrics_payload = payload.get(key)
    if not isinstance(metrics_payload, Mapping):
        return {}

    metrics: dict[str, int | float] = {}
    for metric_name, value in metrics_payload.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            metrics[str(metric_name)] = value
    return metrics


def _should_treat_sentence_variety_as_improvement(
    baseline_rubric: Mapping[str, int | float],
    candidate_rubric: Mapping[str, int | float],
) -> bool:
    baseline_clarity = baseline_rubric.get("clarity")
    candidate_clarity = candidate_rubric.get("clarity")
    if not isinstance(baseline_clarity, (int, float)) or isinstance(baseline_clarity, bool):
        return True
    if not isinstance(candidate_clarity, (int, float)) or isinstance(candidate_clarity, bool):
        return True
    return candidate_clarity >= baseline_clarity


def _compare_metric_mapping(
    *,
    baseline_metrics: Mapping[str, int | float],
    candidate_metrics: Mapping[str, int | float],
    baseline_rubric: Mapping[str, int | float],
    candidate_rubric: Mapping[str, int | float],
    suppress_sentence_variety_improvement: bool,
) -> tuple[list[MetricComparison], list[str], list[str]]:
    metric_comparisons: list[MetricComparison] = []
    regressions: list[str] = []
    improvements: list[str] = []

    for name in sorted(set(baseline_metrics) | set(candidate_metrics)):
        baseline_value = baseline_metrics.get(name)
        candidate_value = candidate_metrics.get(name)
        comparison = MetricComparison(name=name, baseline=baseline_value, candidate=candidate_value)
        metric_comparisons.append(comparison)

        if baseline_value is None and candidate_value is not None:
            improvements.append(name)
            continue
        if candidate_value is None and baseline_value is not None:
            regressions.append(name)
            continue

        if baseline_value is None or candidate_value is None:
            continue

        if candidate_value < baseline_value:
            regressions.append(name)
        elif candidate_value > baseline_value:
            if name == "sentence_variety" and suppress_sentence_variety_improvement:
                continue
            improvements.append(name)

    return metric_comparisons, regressions, improvements


def _compare_style_signals(
    *,
    baseline_metrics: Mapping[str, int | float],
    candidate_metrics: Mapping[str, int | float],
) -> tuple[list[MetricComparison], list[str], list[str]]:
    metric_comparisons: list[MetricComparison] = []
    regressions: list[str] = []
    improvements: list[str] = []

    for name in sorted(set(baseline_metrics) | set(candidate_metrics)):
        baseline_value = baseline_metrics.get(name)
        candidate_value = candidate_metrics.get(name)
        comparison = MetricComparison(name=name, baseline=baseline_value, candidate=candidate_value)
        metric_comparisons.append(comparison)

        if baseline_value is None and candidate_value is not None:
            continue
        if candidate_value is None and baseline_value is not None:
            continue
        if baseline_value is None or candidate_value is None:
            continue

        if name == "contrast_pattern_count":
            if candidate_value > baseline_value:
                regressions.append(name)
            elif candidate_value < baseline_value:
                improvements.append(name)
            continue

        if name == "em_dash_count":
            if candidate_value > baseline_value and candidate_value >= 2:
                regressions.append(name)
            elif candidate_value < baseline_value:
                improvements.append(name)
            continue

        if name in {"avg_sentence_length", "avg_paragraph_length", "sentence_length_variance"}:
            continue

        if candidate_value > baseline_value:
            improvements.append(name)
        elif candidate_value < baseline_value:
            regressions.append(name)

    return metric_comparisons, regressions, improvements


def compare_runs(baseline: Any, candidate: Any) -> ComparisonResult:
    """Compare two evaluation payloads and classify the result."""

    baseline_payload = _as_mapping(baseline)
    candidate_payload = _as_mapping(candidate)

    baseline_rule_failures = _extract_rule_failures(baseline_payload)
    candidate_rule_failures = _extract_rule_failures(candidate_payload)
    rule_failure_delta = candidate_rule_failures - baseline_rule_failures

    baseline_metrics = _extract_numeric_metrics(baseline_payload, "rubric")
    candidate_metrics = _extract_numeric_metrics(candidate_payload, "rubric")
    baseline_style_signals = _extract_numeric_metrics(baseline_payload, "style_signals")
    candidate_style_signals = _extract_numeric_metrics(candidate_payload, "style_signals")

    metric_comparisons: list[MetricComparison]
    regressions: list[str] = []
    improvements: list[str] = []

    metric_comparisons, rubric_regressions, rubric_improvements = _compare_metric_mapping(
        baseline_metrics=baseline_metrics,
        candidate_metrics=candidate_metrics,
        baseline_rubric=baseline_metrics,
        candidate_rubric=candidate_metrics,
        suppress_sentence_variety_improvement=not _should_treat_sentence_variety_as_improvement(
            baseline_metrics,
            candidate_metrics,
        ),
    )
    regressions.extend(rubric_regressions)
    improvements.extend(rubric_improvements)

    style_signal_comparisons, style_regressions, style_improvements = _compare_style_signals(
        baseline_metrics=baseline_style_signals,
        candidate_metrics=candidate_style_signals,
    )
    regressions.extend(style_regressions)
    improvements.extend(style_improvements)

    if rule_failure_delta > 0:
        regressions.insert(0, "rule_failures")
    elif rule_failure_delta < 0:
        improvements.insert(0, "rule_failures")

    if regressions or rule_failure_delta > 0:
        status = "regression"
    elif improvements or rule_failure_delta < 0:
        status = "improvement"
    else:
        status = "no_regression"

    return ComparisonResult(
        status=status,
        baseline_rule_failures=baseline_rule_failures,
        candidate_rule_failures=candidate_rule_failures,
        rule_failure_delta=rule_failure_delta,
        metric_comparisons=tuple(metric_comparisons),
        style_signal_comparisons=tuple(style_signal_comparisons),
        regressions=tuple(dict.fromkeys(regressions)),
        improvements=tuple(dict.fromkeys(improvements)),
    )


def load_json_payload(path: Path) -> dict[str, Any]:
    import json

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return dict(payload)
