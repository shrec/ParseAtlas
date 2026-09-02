"""Cross-family benchmark and invariant calibration helpers."""

from collections.abc import Iterable
from statistics import median
from typing import Any

from sympy import Symbol, simplify, sympify

from .benchmark import benchmark_expression

DEFAULT_BENCHMARK_CORPUS: tuple[tuple[str, str], ...] = (
    ("affine", "2*x + 1 - x/2"),
    ("quadratic", "2*x*x + 1 - x/2"),
    ("rational", "(x + 1)/(x - 2)"),
    ("nested", "2*(x + 1) - x/2"),
)

DEFAULT_IDENTITIES: tuple[tuple[str, str], ...] = (
    ("(x + 1)**2", "x**2 + 2*x + 1"),
    ("(x - 1)*(x + 1)", "x**2 - 1"),
    ("sin(x)**2 + cos(x)**2", "1"),
    ("(x + 2)**3", "x**3 + 6*x**2 + 12*x + 8"),
)


def benchmark_corpus(corpus: Iterable[tuple[str, str]] = DEFAULT_BENCHMARK_CORPUS, repetitions: int = 5) -> dict[str, Any]:
    results = []
    for family, expression in corpus:
        result = benchmark_expression(expression, repetitions)
        result["family"] = family
        result["canonicalization_to_parse_ratio"] = round(result["canonicalization_seconds_median"] / max(result["parse_seconds_median"], 1e-12), 2)
        results.append(result)
    return {"expression_count": len(results), "results": results}


def mine_identities(identities: Iterable[tuple[str, str]] = DEFAULT_IDENTITIES) -> dict[str, Any]:
    variable = Symbol("x", real=True)
    results = []
    for left, right in identities:
        residual = simplify(sympify(left) - sympify(right))
        results.append({"left": left, "right": right, "residual": str(residual), "is_identity": residual == 0, "variables": sorted(str(item) for item in residual.free_symbols) or [str(variable)]})
    return {"identity_count": len(results), "valid_count": sum(item["is_identity"] for item in results), "results": results}
