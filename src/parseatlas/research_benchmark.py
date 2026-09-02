"""Cross-family benchmark and invariant calibration helpers."""

from collections.abc import Iterable
from statistics import median
from typing import Any

from sympy import Symbol, fraction, simplify, solve, sympify
from sympy.parsing.sympy_parser import parse_expr

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
        symbols = {"x": variable}
        left_expression = parse_expr(left, local_dict=symbols, evaluate=False)
        right_expression = parse_expr(right, local_dict=symbols, evaluate=False)
        residual = simplify(left_expression - right_expression)

        def restrictions(expression: Any) -> list[str]:
            _, denominator = fraction(expression)
            return [str(point) for point in solve(denominator, variable)]

        left_restrictions = restrictions(left_expression)
        right_restrictions = restrictions(right_expression)
        counterexamples = []
        for point in (-2, -1, 0, 1, 2):
            if str(point) in left_restrictions or str(point) in right_restrictions:
                continue
            if simplify(left_expression.subs(variable, point) - right_expression.subs(variable, point)) != 0:
                counterexamples.append(point)
        results.append({
            "left": left,
            "right": right,
            "residual": str(residual),
            "left_restrictions": left_restrictions,
            "right_restrictions": right_restrictions,
            "domain_equal": left_restrictions == right_restrictions,
            "counterexamples": counterexamples,
            "is_identity": residual == 0 and left_restrictions == right_restrictions,
            "variables": sorted(str(item) for item in residual.free_symbols) or [str(variable)],
        })
    return {"identity_count": len(results), "valid_count": sum(item["is_identity"] for item in results), "results": results}
