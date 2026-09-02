"""Small deterministic coefficient sweeps for research calibration."""

from collections import Counter
from itertools import product
from time import perf_counter
from typing import Any

from .analyze import analyze_expression


def linear_sweep(values: tuple[int, ...] = (-1, 1, 2)) -> tuple[tuple[str, str], ...]:
    def literal(value: int) -> str:
        return str(value) if value >= 0 else f"(0 - {abs(value)})"

    return tuple(
        (f"linear_a{a}_b{b}_c{c}", f"{literal(a)}*x + {literal(b)} - {literal(c)}*x/2")
        for a, b, c in product(values, repeat=3)
    )


def run_sweep(expressions: tuple[tuple[str, str], ...] | None = None) -> dict[str, Any]:
    expressions = expressions or linear_sweep()
    records = []
    class_counts = Counter()
    ast_counts = Counter()
    for experiment_id, expression in expressions:
        started = perf_counter()
        report = analyze_expression(expression)
        elapsed = perf_counter() - started
        class_count = len(report["equivalence_classes"])
        ast_count = len({str(item["ast"]) for item in report["grammars"]})
        class_counts[class_count] += 1
        ast_counts[ast_count] += 1
        records.append({
            "id": experiment_id,
            "expression": expression,
            "grammar_count": len(report["grammars"]),
            "ast_form_count": ast_count,
            "semantic_class_count": class_count,
            "elapsed_seconds": round(elapsed, 6),
        })
    return {
        "expression_count": len(records),
        "class_count_distribution": dict(sorted(class_counts.items())),
        "ast_count_distribution": dict(sorted(ast_counts.items())),
        "records": records,
    }
