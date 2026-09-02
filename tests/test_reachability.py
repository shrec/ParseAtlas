import os

import pytest

from parseatlas.grammar import all_grammars, control_grammar, strict_grammars
from parseatlas.reachability import (
    canonical_leaves,
    catalan_trees,
    constraint_cycle_nodes,
    grammar_binding_power,
    resolve_workers,
    rightmost_minimum_agreement,
    rightmost_minimum_tree,
    strict_reachable,
    tree_constraints,
    verify_characterization,
)

CORPUS = (
    "2*t + 1 - t/2",
    "a - b*c + d/e - f",
    "a/b + c*d - e/f + g",
    "a - b - c",
    "(x + 1)/(x - 2)",
)


def test_claim_a_holds_for_control_and_all_strict_grammars():
    result = rightmost_minimum_agreement(CORPUS)
    assert result["control_grammar"] == control_grammar().id
    assert result["strict_grammar_count"] == 24
    assert result["grammar_count"] == len(all_grammars()) == 25
    assert result["comparison_count"] == len(CORPUS) * 25
    assert result["agreement_count"] == result["comparison_count"]
    assert result["disagreements"] == []
    assert result["disagreement_count"] == 0
    assert result["claim_a_holds"] is True


def test_rightmost_minimum_tree_is_left_associative_on_ties():
    powers = grammar_binding_power(control_grammar())
    assert powers["+"] == powers["-"]
    assert powers["*"] == powers["/"]
    tree = rightmost_minimum_tree(("a", "b", "c"), ("-", "+"), powers)
    assert tree == ("+", ("-", "a", "b"), "c")


def test_rightmost_minimum_tree_splits_at_the_rightmost_minimum():
    powers = {"+": 1, "-": 1, "*": 2, "/": 2}
    tree = rightmost_minimum_tree(("a", "b", "c", "d"), ("+", "*", "+"), powers)
    assert tree == ("+", ("+", "a", ("*", "b", "c")), "d")


def test_verify_characterization_matches_exhaustive_enumeration_up_to_four_operators():
    result = verify_characterization(4)
    assert result["characterization_holds"] is True
    assert result["total_mismatches"] == 0
    assert result["mismatch_examples"] == []
    assert [bucket["operator_count"] for bucket in result["per_k"]] == [2, 3, 4]
    assert [bucket["pattern_count"] for bucket in result["per_k"]] == [16, 64, 256]
    assert [bucket["tree_count"] for bucket in result["per_k"]] == [32, 320, 3584]
    for bucket in result["per_k"]:
        assert bucket["mismatch_count"] == 0
        assert 0.0 < bucket["unreachable_fraction"] < 1.0
    assert result["total_trees"] == 32 + 320 + 3584
    assert result["claim_a_disagreements"] == 0


def test_sequential_and_parallel_verification_agree():
    # workers is explicit on both sides: the default would collapse to 1 on a
    # one- or two-core runner, and the identity assertion below would then
    # compare the sequential path against itself and could never fail.
    sequential = verify_characterization(4, workers=1)
    parallel = verify_characterization(4, workers=2)
    assert sequential["workers"] == 1
    assert parallel["workers"] > 1
    assert {key: value for key, value in sequential.items() if key != "workers"} == {
        key: value for key, value in parallel.items() if key != "workers"
    }


def test_weak_cycle_between_plus_and_star_blocks_reachability():
    operators = ["+", "*", "+"]
    tree = ("+", ("*", ("+", "a", "b"), "c"), "d")
    strict, weak = tree_constraints(tree, operators)
    assert ("+", "*") in weak
    assert ("*", "+") in weak
    assert strict == set()
    assert constraint_cycle_nodes(tree, operators) == frozenset({"+", "*"})
    assert strict_reachable(tree, operators) is False


def test_repeated_operator_is_left_associative_only():
    operators = ["+", "+"]
    left_leaning = ("+", ("+", "a", "b"), "c")
    right_leaning = ("+", "a", ("+", "b", "c"))
    assert strict_reachable(left_leaning, operators) is True
    assert strict_reachable(right_leaning, operators) is False
    strict, _ = tree_constraints(right_leaning, operators)
    assert ("+", "+") in strict


def test_all_distinct_operators_saturate_every_catalan_tree():
    operators = ["+", "*", "-", "/"]
    trees = catalan_trees(canonical_leaves(len(operators) + 1), operators)
    assert len(trees) == 14
    assert all(strict_reachable(tree, operators) for tree in trees)


def test_decision_procedure_matches_grammar_enumeration_on_one_word():
    operators = ["+", "*", "+"]
    leaves = canonical_leaves(4)
    enumerated = {
        rightmost_minimum_tree(leaves, operators, grammar_binding_power(grammar))
        for grammar in strict_grammars()
    }
    for tree in catalan_trees(leaves, operators):
        assert strict_reachable(tree, operators) == (tree in enumerated)


# --------------------------------------------------------------------------
# Worker derivation
# --------------------------------------------------------------------------


def test_resolve_workers_leaves_one_core_of_headroom(monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    assert resolve_workers(1000) == 7
    monkeypatch.setattr(os, "cpu_count", lambda: 16)
    assert resolve_workers(1000) == 15


def test_resolve_workers_never_drops_below_one(monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: 1)
    assert resolve_workers(1000) == 1
    monkeypatch.setattr(os, "cpu_count", lambda: None)
    assert resolve_workers(1000) == 1


def test_resolve_workers_clamps_to_the_task_count(monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: 32)
    assert resolve_workers(3) == 3
    assert resolve_workers(1) == 1
    # An explicit request is clamped the same way.
    assert resolve_workers(3, 10) == 3
    assert resolve_workers(1000, 4) == 4


def test_resolve_workers_honours_an_explicit_count_regardless_of_cores(monkeypatch):
    monkeypatch.setattr(os, "cpu_count", lambda: 1)
    assert resolve_workers(1000, 6) == 6


def test_resolve_workers_rejects_a_non_positive_explicit_count():
    with pytest.raises(ValueError, match="workers must be at least 1"):
        resolve_workers(10, 0)
    with pytest.raises(ValueError, match="workers must be at least 1"):
        resolve_workers(10, -3)


# --------------------------------------------------------------------------
# Input guards
# --------------------------------------------------------------------------


def test_rightmost_minimum_tree_rejects_a_leaf_operator_count_mismatch():
    with pytest.raises(ValueError, match="expected 3 leaves for 2 operators, got 2"):
        rightmost_minimum_tree(("a", "b"), ("+", "-"), {"+": 1, "-": 1})


def test_rightmost_minimum_tree_rejects_an_operator_without_binding_power():
    with pytest.raises(ValueError, match=r"binding power missing for operators: \['\^'\]"):
        rightmost_minimum_tree(("a", "b"), ("^",), {"+": 1})


def test_tree_constraints_rejects_an_operator_count_mismatch():
    with pytest.raises(ValueError, match="tree has 1 operators, word has 2"):
        tree_constraints(("+", "a", "b"), ["+", "*"])


def test_tree_constraints_rejects_a_root_that_is_not_the_word_operator():
    # Operator counts agree, so only the per-node root check can catch this.
    tree = ("-", ("+", "a", "b"), "c")
    with pytest.raises(ValueError, match="tree root '-' at position 1 does not match"):
        tree_constraints(tree, ["+", "*"])


def test_verify_characterization_rejects_fewer_than_two_operators():
    with pytest.raises(ValueError, match="max_operators must be at least 2"):
        verify_characterization(1)
