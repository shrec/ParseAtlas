"""Exact characterization of precedence-reachable parse trees.

Two claims are implemented and cross-validated here.

Claim A (rightmost-minimum characterization).  For a registered grammar ``G``
with binding-power map ``p``, ``parse(E, G)`` equals the tree produced by the
recursion in :func:`rightmost_minimum_tree`: over an operator range with at
least one operator, take the minimum binding power ``lo`` and split at the
*rightmost* position holding an operator of power ``lo``.  The rightmost choice
is what encodes left associativity of equal-power operators.

Claim B (order-feasibility characterization of reachability).  A candidate tree
over a fixed leaf sequence and operator word is reachable by *some* strict
precedence grammar exactly when the binding-power constraints read off the tree
admit a strict total order.  :func:`strict_reachable` decides this from the
constraint digraph alone; it never enumerates grammars.
"""

from __future__ import annotations

import os
import string
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from itertools import product
from typing import Any

from .grammar import OPERATORS, Grammar, all_grammars, control_grammar, strict_grammars
from .parser import Binary, Node, Number, Variable, parse
from .tokenizer import Token, tokenize

Tree = str | tuple[str, "Tree", "Tree"]

LEAF_ALPHABET = string.ascii_lowercase

_STRICT_GRAMMARS: tuple[Grammar, ...] | None = None


def _cached_strict_grammars() -> tuple[Grammar, ...]:
    """The 24 strict grammars, built once per process."""
    global _STRICT_GRAMMARS
    if _STRICT_GRAMMARS is None:
        _STRICT_GRAMMARS = strict_grammars()
    return _STRICT_GRAMMARS


def grammar_binding_power(grammar: Grammar) -> dict[str, int]:
    """Binding powers exactly as :class:`parseatlas.parser.Parser` derives them.

    The level view is authoritative: the tied control grammar ``G0`` groups
    ``*``/``/`` and ``+``/``-`` into two levels, so its two tied pairs must
    receive equal power.  ``Grammar.binding_power`` flattens the ordering and
    would silently break the tie.
    """
    return {
        operator: len(grammar.levels) - level
        for level, group in enumerate(grammar.levels)
        for operator in group
    }


# --------------------------------------------------------------------------
# Claim A: the rightmost-minimum recursion
# --------------------------------------------------------------------------


def rightmost_minimum_tree(
    leaves: Sequence[Any],
    operators: Sequence[str],
    binding_power: Mapping[str, int],
) -> Tree:
    """Build the parse tree of ``leaves``/``operators`` by rightmost-minimum split.

    ``leaves`` normally holds plain strings and is returned unchanged at the
    base case; already-reduced subtrees may be passed in for parenthesized
    groups.  Internal nodes are canonical ``(operator, left, right)`` tuples.
    """
    leaves = tuple(leaves)
    operators = tuple(operators)
    if len(leaves) != len(operators) + 1:
        raise ValueError(
            f"expected {len(operators) + 1} leaves for {len(operators)} operators, got {len(leaves)}"
        )
    missing = {operator for operator in operators if operator not in binding_power}
    if missing:
        raise ValueError(f"binding power missing for operators: {sorted(missing)}")
    return _rightmost_minimum(leaves, operators, binding_power, 0, len(operators))


def _rightmost_minimum(
    leaves: tuple[Any, ...],
    operators: tuple[str, ...],
    binding_power: Mapping[str, int],
    low: int,
    high: int,
) -> Tree:
    if low == high:
        return leaves[low]
    minimum = min(binding_power[operators[index]] for index in range(low, high))
    split = max(index for index in range(low, high) if binding_power[operators[index]] == minimum)
    return (
        operators[split],
        _rightmost_minimum(leaves, operators, binding_power, low, split),
        _rightmost_minimum(leaves, operators, binding_power, split + 1, high),
    )


def canonical_tree(node: Node) -> Tree:
    """Canonical hashable form of a parser AST: strings for leaves, tuples for nodes."""
    if isinstance(node, Number):
        return str(node.value)
    if isinstance(node, Variable):
        return node.name
    if isinstance(node, Binary):
        return (node.operator, canonical_tree(node.left), canonical_tree(node.right))
    raise TypeError(f"unsupported node: {node!r}")


def _leaf_text(token: Token) -> str:
    if token.kind == "name":
        return token.value
    if "/" in token.value:
        numerator, denominator = token.value.split("/", 1)
        return str(Fraction(int(numerator), int(denominator)))
    return str(Fraction(int(token.value)))


def _rightmost_minimum_primary(
    tokens: tuple[Token, ...], index: int, binding_power: Mapping[str, int]
) -> tuple[Tree, int]:
    token = tokens[index]
    if token.kind in ("number", "name"):
        return _leaf_text(token), index + 1
    if token.kind == "left":
        tree, index = _rightmost_minimum_level(tokens, index + 1, binding_power)
        if tokens[index].kind != "right":
            raise ValueError("Expected closing parenthesis")
        return tree, index + 1
    raise ValueError(f"Expected a primary; got {token.value!r}")


def _rightmost_minimum_level(
    tokens: tuple[Token, ...], index: int, binding_power: Mapping[str, int]
) -> tuple[Tree, int]:
    leaf, index = _rightmost_minimum_primary(tokens, index, binding_power)
    leaves: list[Any] = [leaf]
    operators: list[str] = []
    while tokens[index].kind == "operator":
        operators.append(tokens[index].value)
        leaf, index = _rightmost_minimum_primary(tokens, index + 1, binding_power)
        leaves.append(leaf)
    return rightmost_minimum_tree(leaves, operators, binding_power), index


def rightmost_minimum_parse(source: str, binding_power: Mapping[str, int]) -> Tree:
    """Parse ``source`` using only the Claim A recursion, independent of the real parser."""
    tokens = tokenize(source)
    tree, index = _rightmost_minimum_level(tokens, 0, binding_power)
    if tokens[index].kind != "eof":
        raise ValueError(f"Unexpected token: {tokens[index].value!r}")
    return tree


def rightmost_minimum_agreement(sources: Iterable[str]) -> dict[str, Any]:
    """Confirm Claim A against the real parser for the control grammar and all strict grammars."""
    sources = tuple(sources)
    grammars = all_grammars()
    agreement = 0
    disagreements: list[dict[str, Any]] = []
    for source in sources:
        for grammar in grammars:
            powers = grammar_binding_power(grammar)
            predicted = rightmost_minimum_parse(source, powers)
            actual = canonical_tree(parse(source, grammar))
            if predicted == actual:
                agreement += 1
            else:
                disagreements.append(
                    {
                        "source": source,
                        "grammar": grammar.id,
                        "predicted": predicted,
                        "actual": actual,
                    }
                )
    return {
        "source_count": len(sources),
        "grammar_count": len(grammars),
        "control_grammar": control_grammar().id,
        "strict_grammar_count": len(strict_grammars()),
        "comparison_count": len(sources) * len(grammars),
        "agreement_count": agreement,
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
        "claim_a_holds": not disagreements,
    }


# --------------------------------------------------------------------------
# Claim B: constraint extraction and the reachability decision procedure
# --------------------------------------------------------------------------


def operator_count(tree: Tree) -> int:
    """Number of internal nodes, i.e. operators consumed by ``tree``."""
    if isinstance(tree, tuple):
        return 1 + operator_count(tree[1]) + operator_count(tree[2])
    return 0


def tree_constraints(
    tree: Tree, operators: Sequence[str]
) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    """Binding-power constraints induced by ``tree`` over the operator word.

    Returns ``(strict_edges, weak_edges)`` as sets of operator-type pairs.  A
    strict edge ``(a, b)`` demands ``p(a) < p(b)``; a weak edge ``(a, b)``
    demands ``p(a) <= p(b)``.  The left side of a split is weak because the
    recursion takes the rightmost minimum, so an equal-power operator may sit
    to the left of the root but never to its right.
    """
    operators = tuple(operators)
    if operator_count(tree) != len(operators):
        raise ValueError(
            f"tree has {operator_count(tree)} operators, word has {len(operators)}"
        )
    strict: set[tuple[str, str]] = set()
    weak: set[tuple[str, str]] = set()
    _collect_constraints(tree, operators, 0, len(operators), strict, weak)
    return strict, weak


def _collect_constraints(
    tree: Tree,
    operators: tuple[str, ...],
    low: int,
    high: int,
    strict: set[tuple[str, str]],
    weak: set[tuple[str, str]],
) -> None:
    if not isinstance(tree, tuple):
        return
    split = low + operator_count(tree[1])
    root = operators[split]
    if tree[0] != root:
        raise ValueError(
            f"tree root {tree[0]!r} at position {split} does not match word operator {root!r}"
        )
    for index in range(low, split):
        weak.add((root, operators[index]))
    for index in range(split + 1, high):
        strict.add((root, operators[index]))
    _collect_constraints(tree[1], operators, low, split, strict, weak)
    _collect_constraints(tree[2], operators, split + 1, high, strict, weak)


def _is_acyclic(edges: set[tuple[str, str]]) -> bool:
    """Kahn's algorithm over the operator-type digraph."""
    nodes = {node for edge in edges for node in edge}
    outgoing: dict[str, set[str]] = {node: set() for node in nodes}
    indegree: dict[str, int] = {node: 0 for node in nodes}
    for source, target in edges:
        if target not in outgoing[source]:
            outgoing[source].add(target)
            indegree[target] += 1
    ready = [node for node in nodes if indegree[node] == 0]
    visited = 0
    while ready:
        node = ready.pop()
        visited += 1
        for target in outgoing[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    return visited == len(nodes)


def constraint_cycle_nodes(tree: Tree, operators: Sequence[str]) -> frozenset[str]:
    """Operator types that lie on a cycle of the distinct-type constraint digraph."""
    strict, weak = tree_constraints(tree, operators)
    edges = {(a, b) for a, b in strict | weak if a != b}
    nodes = {node for edge in edges for node in edge}
    reachable: dict[str, set[str]] = {node: set() for node in nodes}
    for source, target in edges:
        reachable[source].add(target)
    changed = True
    while changed:
        changed = False
        for source in nodes:
            extension = {step for target in reachable[source] for step in reachable[target]}
            if not extension <= reachable[source]:
                reachable[source] |= extension
                changed = True
    return frozenset(node for node in nodes if node in reachable[node])


def strict_reachable(tree: Tree, operators: Sequence[str]) -> bool:
    """Decide, from the constraint graph alone, whether some strict grammar builds ``tree``.

    No grammar enumeration happens here.  The tree is reachable exactly when

    1. no strict constraint is a self-loop ``p(o) < p(o)``, and
    2. the constraint digraph restricted to distinct operator types is acyclic,
       because a cycle between distinct types forces their binding powers equal
       and no strict total order allows that.
    """
    strict, weak = tree_constraints(tree, operators)
    if any(source == target for source, target in strict):
        return False
    edges = {(a, b) for a, b in strict | weak if a != b}
    return _is_acyclic(edges)


# --------------------------------------------------------------------------
# Exhaustive cross-validation
# --------------------------------------------------------------------------


def catalan_trees(leaves: Sequence[Any], operators: Sequence[str]) -> list[Tree]:
    """Every parenthesization of the fixed leaf/operator sequence (Catalan many)."""
    return _catalan_trees(tuple(leaves), tuple(operators), 0, len(operators))


def _catalan_trees(
    leaves: tuple[Any, ...], operators: tuple[str, ...], low: int, high: int
) -> list[Tree]:
    if low == high:
        return [leaves[low]]
    trees: list[Tree] = []
    for split in range(low, high):
        left_side = _catalan_trees(leaves, operators, low, split)
        right_side = _catalan_trees(leaves, operators, split + 1, high)
        for left in left_side:
            for right in right_side:
                trees.append((operators[split], left, right))
    return trees


def canonical_leaves(count: int) -> tuple[str, ...]:
    if count > len(LEAF_ALPHABET):
        raise ValueError(f"only {len(LEAF_ALPHABET)} canonical leaves are available")
    return tuple(LEAF_ALPHABET[index] for index in range(count))


def flat_source(leaves: Sequence[str], operators: Sequence[str]) -> str:
    parts = [leaves[0]]
    for operator, leaf in zip(operators, leaves[1:]):
        parts.append(f" {operator} {leaf}")
    return "".join(parts)


def _verify_operator_word(payload: tuple[int, tuple[str, ...]]) -> tuple[int, int, int, int, int, list[dict[str, Any]]]:
    """Ground-truth vs. predicate comparison for one operator word.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    size, word = payload
    leaves = canonical_leaves(size + 1)
    source = flat_source(leaves, word)
    grammars = _cached_strict_grammars()
    reachable_truth: set[Tree] = set()
    claim_a_checks = 0
    claim_a_disagreements = 0
    for grammar in grammars:
        actual = canonical_tree(parse(source, grammar))
        predicted = rightmost_minimum_tree(leaves, word, grammar_binding_power(grammar))
        claim_a_checks += 1
        if predicted != actual:
            claim_a_disagreements += 1
        reachable_truth.add(actual)
    trees = catalan_trees(leaves, word)
    unreachable = 0
    mismatches: list[dict[str, Any]] = []
    for tree in trees:
        truth = tree in reachable_truth
        if not truth:
            unreachable += 1
        if strict_reachable(tree, word) != truth:
            mismatches.append(
                {"operators": list(word), "tree": tree, "predicted": not truth, "actual": truth}
            )
    return size, len(trees), unreachable, claim_a_checks, claim_a_disagreements, mismatches


def resolve_workers(task_count: int, workers: int | None = None) -> int:
    """Worker count derived from the observed core count, never a hardcoded constant."""
    if workers is not None:
        if workers < 1:
            raise ValueError("workers must be at least 1")
        return max(1, min(workers, task_count))
    detected = os.cpu_count() or 1
    # One core of headroom so a sweep cannot starve the interactive session.
    return max(1, min(detected - 1, task_count))


def verify_characterization(
    max_operators: int = 6, workers: int | None = None
) -> dict[str, Any]:
    """Cross-validate :func:`strict_reachable` against exhaustive parsing for k = 2..max_operators.

    Work is independent per operator word and CPU-bound, so it is distributed
    across processes by default.  Parallelism changes only speed: every word is
    scored in isolation and the aggregated result is identical to the
    sequential path obtained with ``workers=1``.

    Caller guard: because the default path builds a :class:`ProcessPoolExecutor`
    and Windows uses the ``spawn`` start method, every child re-imports the
    caller's ``__main__`` module.  A plain script that calls this function at
    module level therefore re-executes itself in each child.  Call it from
    inside an ``if __name__ == "__main__":`` block (or pass ``workers=1``) when
    driving it from a script file.  ``python -c`` and pytest are unaffected:
    neither exposes a ``__main__`` file path for the children to re-import.
    """
    if max_operators < 2:
        raise ValueError("max_operators must be at least 2")
    tasks = [
        (size, word)
        for size in range(2, max_operators + 1)
        for word in product(OPERATORS, repeat=size)
    ]
    worker_count = resolve_workers(len(tasks), workers)
    if worker_count == 1:
        results = [_verify_operator_word(task) for task in tasks]
    else:
        chunk = max(1, len(tasks) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            results = list(pool.map(_verify_operator_word, tasks, chunksize=chunk))

    buckets: dict[int, dict[str, Any]] = {
        size: {
            "operator_count": size,
            "pattern_count": 0,
            "tree_count": 0,
            "unreachable_count": 0,
            "mismatch_count": 0,
            "claim_a_checks": 0,
            "claim_a_disagreements": 0,
        }
        for size in range(2, max_operators + 1)
    }
    mismatch_examples: list[dict[str, Any]] = []
    for size, tree_count, unreachable, checks, disagreements, mismatches in results:
        bucket = buckets[size]
        bucket["pattern_count"] += 1
        bucket["tree_count"] += tree_count
        bucket["unreachable_count"] += unreachable
        bucket["mismatch_count"] += len(mismatches)
        bucket["claim_a_checks"] += checks
        bucket["claim_a_disagreements"] += disagreements
        if mismatches and len(mismatch_examples) < 10:
            mismatch_examples.extend(mismatches[: 10 - len(mismatch_examples)])

    per_k = []
    for size in range(2, max_operators + 1):
        bucket = buckets[size]
        bucket["unreachable_fraction"] = (
            bucket["unreachable_count"] / bucket["tree_count"] if bucket["tree_count"] else 0.0
        )
        per_k.append(bucket)

    total_trees = sum(bucket["tree_count"] for bucket in per_k)
    total_unreachable = sum(bucket["unreachable_count"] for bucket in per_k)
    total_mismatches = sum(bucket["mismatch_count"] for bucket in per_k)
    total_claim_a = sum(bucket["claim_a_checks"] for bucket in per_k)
    total_claim_a_bad = sum(bucket["claim_a_disagreements"] for bucket in per_k)
    return {
        "max_operators": max_operators,
        "workers": worker_count,
        "per_k": per_k,
        "total_patterns": sum(bucket["pattern_count"] for bucket in per_k),
        "total_trees": total_trees,
        "total_unreachable": total_unreachable,
        "total_unreachable_fraction": total_unreachable / total_trees if total_trees else 0.0,
        "total_mismatches": total_mismatches,
        "characterization_holds": total_mismatches == 0,
        "claim_a_checks": total_claim_a,
        "claim_a_disagreements": total_claim_a_bad,
        "claim_a_holds": total_claim_a_bad == 0,
        "mismatch_examples": mismatch_examples,
    }
