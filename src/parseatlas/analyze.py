"""Run a token sequence through the registered grammars."""

import json
from collections import defaultdict
from typing import Any

from .canonical import ast_to_dict, canonicalize, operation_cost
from .grammar import Grammar, all_grammars
from .parser import parse
from .properties import polynomial_properties, rational_properties


def analyze_expression(source: str, grammars: tuple[Grammar, ...] | None = None) -> dict[str, Any]:
    grammars = grammars or all_grammars()
    results = []
    grouped: defaultdict[tuple[str, str, tuple[str, ...]], list[str]] = defaultdict(list)
    for grammar in grammars:
        ast = parse(source, grammar)
        canonical = canonicalize(ast)
        symbolic = canonical["sympy_expression"]
        variables = sorted(symbolic.free_symbols, key=str)
        key = (canonical["expression"], canonical["domain"], tuple(canonical["undefined"]))
        grouped[key].append(grammar.id)
        results.append(
            {
                "id": grammar.id,
                "precedence": [list(level) for level in grammar.levels],
                "ast": ast_to_dict(ast),
                "canonical": canonical["expression"],
                "domain": canonical["domain"],
                "undefined": canonical["undefined"],
                "raw_cost": operation_cost(ast),
                "canonical_cost": {"nodes": len(canonical["expression"]), "depth": 1},
                "properties": {
                    **(polynomial_properties(symbolic, variables[0]) if variables else {"is_polynomial": False}),
                    **(rational_properties(canonical["raw_sympy_expression"], variables[0]) if variables else {"is_rational": False}),
                },
            }
        )
    classes = [
        {
            "id": f"C{index:02d}",
            "canonical": expression,
            "domain": domain,
            "undefined": list(undefined),
            "grammars": grammar_ids,
        }
        for index, ((expression, domain, undefined), grammar_ids) in enumerate(grouped.items(), start=1)
    ]
    class_by_grammar = {grammar_id: item["id"] for item in classes for grammar_id in item["grammars"]}
    for result in results:
        result["equivalence_class"] = class_by_grammar[result["id"]]
    return {"expression": source, "control": next(item for item in results if item["id"] == "G0"), "grammars": results, "equivalence_classes": classes}


def to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=False)


def to_markdown(report: dict[str, Any]) -> str:
    lines = [f"# ParseAtlas Experiment: `{report['expression']}`", "", "## Summary", "", f"- Grammars analyzed: {len(report['grammars'])}", f"- Equivalence classes: {len(report['equivalence_classes'])}", "", "## Equivalence Classes", "", "| Class | Canonical | Domain | Undefined | Grammars |", "|---|---|---|---|---|"]
    for item in report["equivalence_classes"]:
        lines.append(f"| {item['id']} | `{item['canonical']}` | `{item['domain']}` | `{', '.join(item['undefined']) or 'none'}` | {', '.join(item['grammars'])} |")
    lines += ["", "## Evidence", "", "This report is generated from the custom parser and domain-aware grouping. It records observed output; it does not claim that the class count generalizes to other expressions."]
    return "\n".join(lines) + "\n"
