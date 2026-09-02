"""Run the 10,000-function catalog over every registered grammar."""

from collections import Counter
from typing import Any

from sympy import Symbol, simplify

from .canonical import to_sympy, undefined_terms
from .function_catalog import FunctionSpec, build_catalog
from .grammar import all_grammars
from .parser import parse


BASELINE = "2*t + 1 - t/2"


def run_catalog(catalog: tuple[FunctionSpec, ...] | None = None) -> dict[str, Any]:
    catalog = catalog or build_catalog()
    variable = Symbol("t", real=True)
    family_counts: Counter[str] = Counter()
    constant_counts: Counter[str] = Counter()
    total_results = 0
    inner_excluded_points_by_grammar = {}
    for grammar in all_grammars():
        inner_node = parse(BASELINE, grammar)
        inner = to_sympy(inner_node)
        inner_excluded_points_by_grammar[grammar.id] = list(undefined_terms(inner_node))
        for spec in catalog:
            output = simplify(spec.apply(inner))
            family_counts[spec.family] += 1
            total_results += 1
            if not output.has(variable):
                constant_counts[spec.family] += 1
    return {
        "baseline": BASELINE,
        "function_count": len(catalog),
        "grammar_count": len(all_grammars()),
        "total_results": total_results,
        "families": sorted({spec.family for spec in catalog}),
        "family_result_counts": dict(sorted(family_counts.items())),
        "constant_result_counts": dict(sorted(constant_counts.items())),
        "inner_excluded_points_by_grammar": inner_excluded_points_by_grammar,
    }
