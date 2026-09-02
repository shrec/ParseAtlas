"""Grammar-space sensitivity and pairwise equivalence measurements."""

from collections.abc import Iterable
from typing import Any

from .analyze import analyze_expression


def representation_sensitivity(report: dict[str, Any], strict_only: bool = True) -> float:
    """Normalize semantic class diversity to [0, 1] for one expression."""
    results = [item for item in report["grammars"] if not strict_only or item["id"] != "G0"]
    classes = {item["equivalence_class"] for item in results}
    denominator = max(len(results) - 1, 1)
    return (len(classes) - 1) / denominator


def equivalence_matrix(expressions: Iterable[str]) -> dict[str, Any]:
    expressions = tuple(expressions)
    reports = [analyze_expression(expression) for expression in expressions]
    grammar_ids = [item["id"] for item in reports[0]["grammars"]]
    matrix: dict[str, dict[str, float]] = {left: {} for left in grammar_ids}
    counts: dict[str, dict[str, int]] = {left: {} for left in grammar_ids}
    for left in grammar_ids:
        for right in grammar_ids:
            equal_count = sum(
                next(item for item in report["grammars"] if item["id"] == left)["equivalence_class"]
                == next(item for item in report["grammars"] if item["id"] == right)["equivalence_class"]
                for report in reports
            )
            counts[left][right] = equal_count
            matrix[left][right] = equal_count / max(len(reports), 1)
    sensitivities = [representation_sensitivity(report) for report in reports]
    return {
        "expression_count": len(expressions),
        "grammar_count": len(grammar_ids),
        "matrix": matrix,
        "equal_counts": counts,
        "sensitivity": {expression: value for expression, value in zip(expressions, sensitivities)},
        "mean_sensitivity": sum(sensitivities) / max(len(sensitivities), 1),
    }
