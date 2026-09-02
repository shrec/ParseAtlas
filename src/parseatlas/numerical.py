"""Numerical cross-checks for symbolic grammar interpretations."""

from typing import Any

from sympy import Symbol, zoo

from .canonical import canonicalize, to_sympy
from .grammar import all_grammars
from .parser import parse


def validate_expression(source: str, sample_points: tuple[Any, ...] = (-2, -1, 0, 1, 2)) -> dict[str, Any]:
    variable = Symbol("x", real=True)
    checked = 0
    skipped = 0
    mismatches: list[dict[str, Any]] = []
    grammar_results = []
    for grammar in all_grammars():
        node = parse(source, grammar)
        canonical = canonicalize(node)
        raw = canonical["raw_sympy_expression"]
        simplified = canonical["sympy_expression"]
        grammar_checked = 0
        grammar_skipped = 0
        for point in sample_points:
            try:
                raw_value = raw.subs(variable, point)
                simplified_value = simplified.subs(variable, point)
                if raw_value in (zoo, -zoo) or simplified_value in (zoo, -zoo):
                    grammar_skipped += 1
                    skipped += 1
                    continue
                raw_numeric = complex(raw_value.evalf(30))
                simplified_numeric = complex(simplified_value.evalf(30))
            except (TypeError, ValueError, ZeroDivisionError):
                grammar_skipped += 1
                skipped += 1
                continue
            grammar_checked += 1
            checked += 1
            if abs(raw_numeric - simplified_numeric) > 1e-20:
                mismatches.append({"grammar": grammar.id, "point": point, "raw": str(raw_value), "canonical": str(simplified_value)})
        grammar_results.append({"grammar": grammar.id, "checked": grammar_checked, "skipped": grammar_skipped, "matches": not any(item["grammar"] == grammar.id for item in mismatches)})
    return {"expression": source, "grammar_count": len(all_grammars()), "checked": checked, "skipped": skipped, "mismatches": mismatches, "all_match": not mismatches, "grammars": grammar_results}
