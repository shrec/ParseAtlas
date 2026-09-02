"""Raw operation-multiset invariance against grammar-dependent critical-path depth."""

from collections.abc import Iterable
from typing import Any

from sympy import count_ops

from .canonical import canonicalize, operation_cost
from .grammar import Grammar, all_grammars
from .parser import parse

RAW_COST_KEYS = ("add", "sub", "mul", "div", "nodes")

EMPTY_CORPUS_MESSAGE = "cost_invariance_report needs at least one expression: invariance over an empty corpus is vacuous."


def _signature_from_cost(cost: dict[str, int]) -> tuple[tuple[str, int], ...]:
    """Project one ``operation_cost`` result onto the depth-free hashable signature."""
    return tuple((key, cost[key]) for key in RAW_COST_KEYS)


def raw_cost_signature(source: str, grammar: Grammar) -> tuple[tuple[str, int], ...]:
    """Return the depth-free operation multiset of one parse as a hashable signature."""
    return _signature_from_cost(operation_cost(parse(source, grammar)))


def _grammar_entry(source: str, grammar: Grammar) -> dict[str, Any]:
    """Parse the source once and read both depth and raw signature off the single cost result."""
    cost = operation_cost(parse(source, grammar))
    return {"id": grammar.id, "depth": cost["depth"], "raw_signature": _signature_from_cost(cost)}


def depth_profile(source: str) -> dict[str, Any]:
    """Record critical-path depth and raw signature for the control plus all strict grammars."""
    entries = [_grammar_entry(source, grammar) for grammar in all_grammars()]
    depths = [entry["depth"] for entry in entries]
    min_depth = min(depths)
    max_depth = max(depths)
    control_depth = next(entry["depth"] for entry in entries if entry["id"] == "G0")
    return {
        "expression": source,
        "grammar_count": len(entries),
        "grammars": entries,
        "min_depth": min_depth,
        "max_depth": max_depth,
        "depth_spread": max_depth - min_depth,
        "min_depth_grammars": sorted(entry["id"] for entry in entries if entry["depth"] == min_depth),
        "max_depth_grammars": sorted(entry["id"] for entry in entries if entry["depth"] == max_depth),
        "control_depth": control_depth,
        "control_is_minimal": control_depth == min_depth,
    }


def _canonical_operation_counts(source: str) -> list[int]:
    return [int(count_ops(canonicalize(parse(source, grammar))["sympy_expression"])) for grammar in all_grammars()]


def cost_invariance_report(expressions: Iterable[str]) -> dict[str, Any]:
    """Compare the invariant raw multiset with the grammar-sensitive depth and canonical cost.

    An empty corpus raises ``ValueError``: reporting ``all_raw_signatures_invariant`` from an
    empty ``all()`` would announce the headline result while nothing at all was measured.
    """
    expressions = tuple(expressions)
    if not expressions:
        raise ValueError(EMPTY_CORPUS_MESSAGE)
    reports = []
    for source in expressions:
        profile = depth_profile(source)
        signatures = {entry["raw_signature"] for entry in profile["grammars"]}
        canonical_counts = _canonical_operation_counts(source)
        reports.append(
            {
                "expression": source,
                "raw_signature": next(entry["raw_signature"] for entry in profile["grammars"] if entry["id"] == "G0"),
                "distinct_raw_signatures": len(signatures),
                "raw_signature_invariant": len(signatures) == 1,
                "depth_profile": profile,
                "canonical_cost": {
                    "min": min(canonical_counts),
                    "max": max(canonical_counts),
                    "distinct": len(set(canonical_counts)),
                },
            }
        )
    spreads = [report["depth_profile"]["depth_spread"] for report in reports]
    return {
        "expression_count": len(expressions),
        "grammar_count": len(all_grammars()),
        "expressions": reports,
        "all_raw_signatures_invariant": all(report["raw_signature_invariant"] for report in reports),
        "mean_depth_spread": sum(spreads) / len(spreads),
        "max_depth_spread": max(spreads),
    }
