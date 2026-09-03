"""Outer-function analysis over the shared inner grammar results.

Every slot this module reports about a grammar's reading is a function of the **denoted
value**, never of the parse tree that happens to denote it.  That is the whole point of the
``(canonical form, domain, excluded points)`` triple: two grammars that denote the same partial
function must produce the same triple, or every downstream partition is measuring syntax.

The rule has one concrete consequence in the code below and it is easy to get wrong.  A parse
tree may carry *structural residue* -- a removable singularity such as ``(6 - 3*t)/(2 - t)``,
which denotes the constant ``3`` -- while another grammar of the same token sequence yields the
bare ``Integer(3)``.  The two are the same value with the same validity restriction, and the
restriction is recorded in the excluded-points slot by :func:`parseatlas.canonical.undefined_terms`,
which reads the parse tree on purpose.  The domain slot must therefore be computed on the
canonicalised argument; computing it on the raw tree makes it disagree between grammars that
agree on the value, which is exactly the failure the triple exists to prevent (NF-2026-00004).
"""

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


def canonical_argument(expression: Any) -> Any:
    """The denoted value of an inner reading, as a single canonical SymPy expression.

    Named and exported so that every consumer composes the outer function on the *same* object.
    Callers that already hold the canonical form pass it straight through -- ``simplify`` is
    idempotent here, but it is not cheap, so the sweep computes it once per grammar.
    """
    return simplify(expression)


def _affine_properties(argument: Any, variable: Symbol, function_name: str) -> dict[str, str | bool]:
    derivative = simplify(argument.diff(variable))
    result: dict[str, str | bool] = {"constant_argument": derivative == 0}
    if function_name in {"sin", "cos", "tan"} and derivative.free_symbols.isdisjoint({variable}):
        result["frequency"] = str(Abs(derivative))
        result["period"] = "undefined (constant argument)" if derivative == 0 else str((pi if function_name == "tan" else 2 * pi) / Abs(derivative))
    return result


def _property_summary(argument: Any, variable: Symbol, function_name: str) -> dict[str, Any]:
    """Properties of ``f(argument)``.

    ``argument`` must be the canonicalised inner value from :func:`canonical_argument`.  Both
    domain slots are therefore properties of the denoted function; the parse tree's own validity
    restrictions travel separately, in ``inner_excluded_points``.
    """
    properties = _affine_properties(argument, variable, function_name)
    try:
        properties["inner_real_domain"] = str(continuous_domain(argument, variable, S.Reals))
    except (NotImplementedError, ValueError):
        properties["inner_real_domain"] = "undetermined"
    try:
        outer = OUTER_FUNCTIONS[function_name](argument)
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
        argument = canonical_argument(to_sympy(inner_node))
        excluded = list(undefined_terms(inner_node))
        inner_text = str(argument)
        for function_name in names:
            outer = simplify(OUTER_FUNCTIONS[function_name](argument))
            results.append(
                {
                    "grammar": grammar.id,
                    "function": function_name,
                    "inner": inner_text,
                    "inner_excluded_points": list(excluded),
                    "canonical": str(outer),
                    "properties": _property_summary(argument, variable, function_name),
                }
            )
    return {"expression": source, "functions": list(names), "results": results}
