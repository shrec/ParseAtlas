"""Permutation graph analysis for strict precedence grammars."""

from collections.abc import Iterable
from typing import Any

from .analyze import analyze_expression
from .grammar import Grammar, strict_grammars


def adjacent_swap_edges(grammars: tuple[Grammar, ...] | None = None) -> tuple[tuple[str, str, int], ...]:
    grammars = grammars or strict_grammars()
    by_order = {grammar.precedence: grammar.id for grammar in grammars}
    edges: set[tuple[str, str, int]] = set()
    for grammar in grammars:
        ordering = grammar.precedence
        for index in range(len(ordering) - 1):
            swapped = list(ordering)
            swapped[index], swapped[index + 1] = swapped[index + 1], swapped[index]
            neighbor_id = by_order[tuple(swapped)]
            left, right = sorted((grammar.id, neighbor_id))
            edges.add((left, right, index))
    return tuple(sorted(edges))


def analyze_precedence_graph(expressions: Iterable[str]) -> dict[str, Any]:
    expressions = tuple(expressions)
    reports = [analyze_expression(expression, strict_grammars()) for expression in expressions]
    edges = adjacent_swap_edges()
    changes = []
    for left, right, position in edges:
        changed = sum(
            next(item for item in report["grammars"] if item["id"] == left)["equivalence_class"]
            != next(item for item in report["grammars"] if item["id"] == right)["equivalence_class"]
            for report in reports
        )
        changes.append({"left": left, "right": right, "swap_position": position, "changed_expressions": changed, "change_rate": changed / max(len(expressions), 1)})
    signatures = {
        grammar_id: tuple(
            next(item for item in report["grammars"] if item["id"] == grammar_id)["equivalence_class"]
            for report in reports
        )
        for grammar_id in (grammar.id for grammar in strict_grammars())
    }
    return {"expression_count": len(expressions), "grammar_count": 24, "edge_count": len(edges), "edges": changes, "grammar_signatures": {key: list(value) for key, value in signatures.items()}}
