"""Controlled expression-family experiments."""

from collections.abc import Iterable
from typing import Any

from .analyze import analyze_expression

DEFAULT_CORPUS: tuple[tuple[str, str], ...] = (
    ("linear_01", "2*t + 1 - t/2"),
    ("linear_02", "3*x + 2 - x/3"),
    ("polynomial_01", "2*x*x + 1 - x/2"),
    ("polynomial_02", "x*x*x + 2*x*x - x + 1"),
    ("rational_01", "(x + 1)/(x - 2)"),
    ("rational_02", "(x*x - 1)/(x - 1)"),
)


def run_corpus(corpus: Iterable[tuple[str, str]] = DEFAULT_CORPUS) -> dict[str, Any]:
    experiments = []
    for experiment_id, expression in corpus:
        report = analyze_expression(expression)
        experiments.append(
            {
                "id": experiment_id,
                "expression": expression,
                "grammar_count": len(report["grammars"]),
                "ast_form_count": len({str(item["ast"]) for item in report["grammars"]}),
                "semantic_class_count": len(report["equivalence_classes"]),
                "degrees": sorted({item["properties"].get("degree") for item in report["grammars"] if item["properties"].get("is_polynomial")}),
                "poles": sorted({pole for item in report["grammars"] for pole in item["properties"].get("poles", [])}),
            }
        )
    return {"experiment_count": len(experiments), "experiments": experiments}
