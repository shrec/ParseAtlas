"""Outer-function analysis over the shared inner grammar results."""

from collections.abc import Iterable
from typing import Any, Callable

from sympy import Abs, S, Symbol, acos, asin, atan, cos, exp, log, pi, simplify, sin, sqrt, tan
from sympy.calculus.util import continuous_domain

from .canonical import to_sympy, undefined_terms
from .grammar import Grammar, all_grammars
from .parser import parse

OUTER_FUNCTIONS: dict[str, Callable[[Any], Any]] = {
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "exp": exp,
    "log": log,
    "sqrt": sqrt,
    "abs": Abs,
    "asin": asin,
    "acos": acos,
    "atan": atan,
    "reciprocal": lambda expression: 1 / expression,
    "square": lambda expression: expression**2,
    "cube": lambda expression: expression**3,
}


def _affine_properties(expression: Any, variable: Symbol, function_name: str) -> dict[str, str | bool]:
    derivative = simplify(expression.diff(variable))
    result: dict[str, str | bool] = {"constant_argument": derivative == 0}
    if function_name in {"sin", "cos", "tan"} and derivative.free_symbols.isdisjoint({variable}):
        result["frequency"] = str(Abs(derivative))
        result["period"] = "undefined (constant argument)" if derivative == 0 else str((pi if function_name == "tan" else 2 * pi) / Abs(derivative))
    return result


def _property_summary(expression: Any, variable: Symbol, function_name: str) -> dict[str, Any]:
    properties = _affine_properties(expression, variable, function_name)
    try:
        domain = continuous_domain(expression, variable, S.Reals)
        properties["inner_real_domain"] = str(domain)
    except (NotImplementedError, ValueError):
        properties["inner_real_domain"] = "undetermined"
    try:
        outer = OUTER_FUNCTIONS[function_name](expression)
        properties["real_domain"] = str(continuous_domain(outer, variable, S.Reals))
    except (NotImplementedError, ValueError):
        properties["real_domain"] = "undetermined"
    return properties


def analyze_outer_functions(source: str, function_names: Iterable[str] | None = None, grammars: tuple[Grammar, ...] | None = None) -> dict[str, Any]:
    names = tuple(function_names or OUTER_FUNCTIONS)
    unknown = set(names) - set(OUTER_FUNCTIONS)
    if unknown:
        raise ValueError(f"Unknown outer functions: {', '.join(sorted(unknown))}")
    grammars = grammars or all_grammars()
    variable = Symbol("t", real=True)
    results = []
    for grammar in grammars:
        inner_node = parse(source, grammar)
        inner = to_sympy(inner_node)
        for function_name in names:
            outer = simplify(OUTER_FUNCTIONS[function_name](inner))
            results.append(
                {
                    "grammar": grammar.id,
                    "function": function_name,
                    "inner": str(simplify(inner)),
                    "inner_excluded_points": list(undefined_terms(inner_node)),
                    "canonical": str(outer),
                    "properties": _property_summary(inner, variable, function_name),
                }
            )
    return {"expression": source, "functions": list(names), "results": results}
