"""Precedence-reachable fraction of the full parenthesization space."""

from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from itertools import product
from os import cpu_count
from string import ascii_lowercase
from typing import Any, TypeVar

from .canonical import ast_to_dict
from .grammar import OPERATORS, control_grammar, strict_grammars
from .parser import parse

Tree = str | tuple[str, Any, Any]

Result = TypeVar("Result")


@lru_cache(maxsize=None)
def _enumerate(leaves: tuple[str, ...], operators: tuple[str, ...]) -> tuple[Tree, ...]:
    if not operators:
        return (leaves[0],)
    return tuple(
        (operator, left, right)
        for index, operator in enumerate(operators)
        for left in _enumerate(leaves[: index + 1], operators[:index])
        for right in _enumerate(leaves[index + 1 :], operators[index + 1 :])
    )


def enumerate_parenthesizations(leaves: Sequence[str], operators: Sequence[str]) -> tuple[Tree, ...]:
    """Enumerate every binary tree over a fixed leaf and operator sequence."""
    leaves = tuple(leaves)
    operators = tuple(operators)
    if len(leaves) != len(operators) + 1:
        raise ValueError(f"Expected {len(operators) + 1} leaves for {len(operators)} operators; got {len(leaves)}")
    return _enumerate(leaves, operators)


def _tree_form(node: dict[str, Any]) -> Tree:
    if node["type"] == "number":
        return node["value"]
    if node["type"] == "variable":
        return node["name"]
    return (node["operator"], _tree_form(node["left"]), _tree_form(node["right"]))


def _sorted_trees(trees: Iterable[Tree]) -> tuple[Tree, ...]:
    return tuple(sorted(trees, key=repr))


def reachable_asts(source: str) -> dict[str, Any]:
    """Collect the distinct tree forms the registered grammars produce for one source."""
    strict = {_tree_form(ast_to_dict(parse(source, grammar))) for grammar in strict_grammars()}
    control = _tree_form(ast_to_dict(parse(source, control_grammar())))
    return {"strict": _sorted_trees(strict), "control": control, "all": _sorted_trees(strict | {control})}


def _in_order(tree: Tree) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if isinstance(tree, str):
        return (tree,), ()
    left_leaves, left_operators = _in_order(tree[1])
    right_leaves, right_operators = _in_order(tree[2])
    return left_leaves + right_leaves, left_operators + (tree[0],) + right_operators


def coverage_report(sources: Iterable[str]) -> dict[str, Any]:
    """Compare precedence-reachable trees against the full parenthesization space."""
    records = []
    for source in sources:
        reachable = reachable_asts(source)
        leaves, operators = _in_order(reachable["control"])
        total = len(enumerate_parenthesizations(leaves, operators))
        strict_reachable = len(reachable["strict"])
        all_reachable = len(reachable["all"])
        records.append(
            {
                "source": source,
                "leaf_count": len(leaves),
                "operator_count": len(operators),
                "catalan_total": total,
                "strict_reachable": strict_reachable,
                "all_reachable": all_reachable,
                "strict_coverage": strict_reachable / total,
                "all_coverage": all_reachable / total,
                "control_only_trees": _sorted_trees(set(reachable["all"]) - set(reachable["strict"])),
            }
        )
    return {
        "expression_count": len(records),
        "mean_strict_coverage": sum(item["strict_coverage"] for item in records) / max(len(records), 1),
        "mean_all_coverage": sum(item["all_coverage"] for item in records) / max(len(records), 1),
        "expressions": records,
    }


def canonical_leaves(count: int) -> tuple[str, ...]:
    return tuple(ascii_lowercase[:count])


def pattern_source(leaves: Sequence[str], operators: Sequence[str]) -> str:
    parts = [leaves[0]]
    for operator, leaf in zip(operators, leaves[1:]):
        parts += [operator, leaf]
    return " ".join(parts)


def _pattern_coverage(operators: tuple[str, ...]) -> tuple[float, float]:
    leaves = canonical_leaves(len(operators) + 1)
    total = len(enumerate_parenthesizations(leaves, operators))
    reachable = reachable_asts(pattern_source(leaves, operators))
    return len(reachable["all"]) / total, len(reachable["strict"]) / total


def _pattern_is_control_only(operators: tuple[str, ...]) -> bool:
    leaves = canonical_leaves(len(operators) + 1)
    reachable = reachable_asts(pattern_source(leaves, operators))
    return reachable["control"] not in set(reachable["strict"])


def _resolve_workers(workers: int | None) -> int:
    """Resolve a worker count; ``None`` selects the measured-faster sequential path.

    ``workers=0`` derives the count from the observed core count with one core of
    headroom, so the parallel path never needs a hardcoded constant.
    """
    if workers is None:
        return 1
    if workers <= 0:
        return max((cpu_count() or 1) - 1, 1)
    return workers


def _map_patterns(
    function: Callable[[tuple[str, ...]], Result],
    patterns: tuple[tuple[str, ...], ...],
    workers: int,
) -> list[Result]:
    # Measured on this 16-core Windows host (fresh process per configuration, whole
    # max_operators sweep):
    #   k<=3   workers=1 0.029 s   workers=2 1.218 s   workers=8 2.070 s   workers=15 3.020 s
    #   k<=5   workers=1 0.777 s   workers=2 2.892 s   workers=8 4.248 s   workers=15 5.937 s
    #   k<=6   workers=1 4.607 s   workers=2 5.464 s   workers=8 5.824 s   workers=15 8.206 s
    # Sequential wins at every size, so this workload stays sequential by default:
    # one pattern is microseconds of parsing, while each spawned process pays a fresh
    # interpreter start plus the sympy import chain that parseatlas pulls in, and that
    # fixed cost dominates the work being distributed. The parallel path is kept and
    # exercised because it is measurably identical, not because it is faster; the
    # sequential==parallel test pins that identity.
    if workers == 1:
        return [function(pattern) for pattern in patterns]
    chunksize = max(len(patterns) // (workers * 4), 1)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(function, patterns, chunksize=chunksize))


def operator_pattern_sweep(max_operators: int = 5, workers: int | None = None) -> dict[str, Any]:
    """Sweep every operator pattern of length 2..max_operators over the canonical leaves."""
    resolved = _resolve_workers(workers)
    levels = []
    for operator_count in range(2, max_operators + 1):
        patterns = tuple(product(OPERATORS, repeat=operator_count))
        coverages = _map_patterns(_pattern_coverage, patterns, resolved)
        total = len(enumerate_parenthesizations(canonical_leaves(operator_count + 1), patterns[0]))
        combined = [item[0] for item in coverages]
        strict = [item[1] for item in coverages]
        levels.append(
            {
                "operator_count": operator_count,
                "leaf_count": operator_count + 1,
                "catalan_total": total,
                "pattern_count": len(patterns),
                "mean_coverage": sum(combined) / len(combined),
                "min_coverage": min(combined),
                "max_coverage": max(combined),
                "mean_strict_coverage": sum(strict) / len(strict),
                "full_coverage_fraction": sum(value == 1.0 for value in combined) / len(combined),
            }
        )
    return {"operator_alphabet": list(OPERATORS), "max_operators": max_operators, "levels": levels}


def control_only_pattern_sweep(max_operators: int = 5, workers: int | None = None) -> dict[str, Any]:
    """Count the operator patterns whose control tree no strict ordering reaches.

    A pattern is control-only when the tied-level control grammar ``G0`` produces a tree
    that is absent from the trees the 24 strict orderings produce for the same source.
    """
    resolved = _resolve_workers(workers)
    levels = []
    for operator_count in range(2, max_operators + 1):
        patterns = tuple(product(OPERATORS, repeat=operator_count))
        flags = _map_patterns(_pattern_is_control_only, patterns, resolved)
        control_only = sum(flags)
        levels.append(
            {
                "operator_count": operator_count,
                "leaf_count": operator_count + 1,
                "pattern_count": len(patterns),
                "control_only_patterns": control_only,
                "control_only_fraction": control_only / len(patterns),
            }
        )
    return {"operator_alphabet": list(OPERATORS), "max_operators": max_operators, "levels": levels}
