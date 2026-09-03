import os
from itertools import product

import pytest

from parseatlas.associativity import (
    LEFT,
    PARALLEL_MINIMUM_ITEMS,
    RIGHT,
    SIDES,
    AssociativeGrammar,
    all_associativity_grammars,
    all_left_agreement,
    assignment_reachable,
    associative_parse,
    associative_tree,
    associativity_space,
    control_associativity_space,
    coverage_with_associativity,
    from_grammar,
    node_profiles,
    reachability_with_associativity,
    resolve_item_workers,
    semantic_diversity,
    split_parse,
    split_rule_agreement,
    split_tree,
    tree_constraints_with_associativity,
    verify_associativity_characterization,
)
from parseatlas.grammar import OPERATORS, all_grammars, control_grammar, strict_grammars
from parseatlas.parser import parse
from parseatlas.reachability import (
    canonical_leaves,
    canonical_tree,
    catalan_trees,
    flat_source,
    rightmost_minimum_tree,
    strict_reachable,
    tree_constraints,
)

CORPUS = (
    "2*t + 1 - t/2",
    "a - b*c + d/e - f",
    "a/b + c*d - e/f + g",
    "a - b - c",
    "(x + 1)/(x - 2)",
)


# --------------------------------------------------------------------------
# The registry extension
# --------------------------------------------------------------------------


def test_associativity_space_is_twenty_four_times_sixteen():
    space = associativity_space()
    assert len(OPERATORS) == 4
    assert len(space) == 384 == 24 * 2**4
    assert len({grammar.id for grammar in space}) == 384
    assert len({(grammar.levels, grammar.associativity) for grammar in space}) == 384
    for grammar in space:
        assert len(grammar.levels) == 4
        assert all(len(level) == 1 for level in grammar.levels)
        assert set(grammar.sides) == set(OPERATORS)


def test_all_left_slice_is_exactly_the_generation_1_strict_registry():
    space = associativity_space()
    all_left = [grammar for grammar in space if grammar.is_all_left]
    assert len(all_left) == 24
    assert [grammar.id for grammar in all_left] == [f"G{index:02d}-LLLL" for index in range(1, 25)]
    assert [grammar.base_grammar() for grammar in all_left] == list(strict_grammars())


def test_control_associativity_space_is_one_choice_per_level():
    control = control_associativity_space()
    assert len(control) == 4 == 2 ** len(control_grammar().levels)
    assert {grammar.id for grammar in control} == {"G0-LLLL", "G0-RRLL", "G0-LLRR", "G0-RRRR"}
    for grammar in control:
        for level in grammar.levels:
            assert len({grammar.sides[operator] for operator in level}) == 1


def test_all_associativity_grammars_is_control_plus_strict():
    assert len(all_associativity_grammars()) == 388 == 4 + 384


def test_a_level_may_not_mix_associativity():
    with pytest.raises(ValueError, match="mixes associativity"):
        AssociativeGrammar(
            "bad",
            (("*", "/"), ("+", "-")),
            (("*", LEFT), ("/", RIGHT), ("+", LEFT), ("-", LEFT)),
        )


def test_grammar_construction_rejects_incomplete_assignments():
    with pytest.raises(ValueError, match="associativity missing"):
        AssociativeGrammar("bad", (("+",), ("-",)), (("+", LEFT),))


def test_from_grammar_lifts_and_tags_an_explicit_assignment():
    base = strict_grammars()[0]
    assert base.id == "G01"
    lifted = from_grammar(base, {"+": RIGHT, "-": LEFT, "*": LEFT, "/": RIGHT})
    assert lifted.id == "G01-RLLR"
    assert lifted.levels == base.levels
    assert lifted.binding_power == {"+": 4, "-": 3, "*": 2, "/": 1}
    assert from_grammar(base).id == "G01-LLLL"
    assert from_grammar(base).is_all_left is True


# --------------------------------------------------------------------------
# Claim A': the parser and the generalized split
# --------------------------------------------------------------------------


def test_all_left_slice_reproduces_every_generation_1_parse():
    result = all_left_agreement(CORPUS)
    assert result["grammar_count"] == len(all_grammars()) == 25
    assert result["comparison_count"] == len(CORPUS) * 25 == 125
    assert result["parser_agreement_count"] == 125
    assert result["split_agreement_count"] == 125
    assert result["disagreements"] == []
    assert result["all_left_slice_reproduces_generation_1"] is True
    assert result["claim_a_prime_holds"] is True


def test_all_left_parse_is_ast_identical_not_merely_equivalent():
    for source in CORPUS:
        for grammar in all_grammars():
            assert associative_parse(source, from_grammar(grammar)) == parse(source, grammar)


def test_split_rule_agrees_with_the_parser_over_the_whole_extended_space():
    result = split_rule_agreement(CORPUS)
    assert result["grammar_count"] == 388
    assert result["comparison_count"] == len(CORPUS) * 388 == 1940
    assert result["agreement_count"] == 1940
    assert result["disagreement_count"] == 0
    assert result["claim_a_prime_holds"] is True


def test_split_tree_is_rightmost_minimum_when_left_associative():
    grammar = from_grammar(strict_grammars()[0])
    leaves = ("a", "b", "c", "d")
    word = ("+", "*", "+")
    assert split_tree(leaves, word, grammar) == rightmost_minimum_tree(
        leaves, word, grammar.binding_power
    )


def test_split_tree_is_leftmost_minimum_when_right_associative():
    base = control_grammar()
    left = from_grammar(base)
    right = from_grammar(base, {operator: RIGHT for operator in OPERATORS})
    leaves = ("a", "b", "c")
    word = ("-", "+")
    assert split_tree(leaves, word, left) == ("+", ("-", "a", "b"), "c")
    assert split_tree(leaves, word, right) == ("-", "a", ("+", "b", "c"))


def test_right_associativity_produces_the_right_leaning_chain():
    base = strict_grammars()[0]
    right = from_grammar(base, {"+": LEFT, "-": RIGHT, "*": LEFT, "/": LEFT})
    assert associative_tree("a - b - c", from_grammar(base)) == ("-", ("-", "a", "b"), "c")
    assert associative_tree("a - b - c", right) == ("-", "a", ("-", "b", "c"))


def test_right_associativity_does_not_disturb_higher_precedence_operators():
    grammar = AssociativeGrammar(
        "probe",
        (("*",), ("/",), ("+",), ("-",)),
        (("*", LEFT), ("/", LEFT), ("+", RIGHT), ("-", LEFT)),
    )
    assert associative_tree("a + b*c + d", grammar) == (
        "+",
        "a",
        ("+", ("*", "b", "c"), "d"),
    )


def test_split_parse_handles_explicit_parentheses():
    grammar = from_grammar(control_grammar(), {operator: RIGHT for operator in OPERATORS})
    assert split_parse("(a - b) - c", grammar) == ("-", ("-", "a", "b"), "c")
    assert split_parse("(a - b) - c", grammar) == associative_tree("(a - b) - c", grammar)


# --------------------------------------------------------------------------
# Claim B' / Claim C: reachability
# --------------------------------------------------------------------------


def test_all_left_constraints_reproduce_experiment_0023():
    for size in (2, 3, 4):
        for word in product(OPERATORS, repeat=size):
            assignment = {operator: LEFT for operator in OPERATORS}
            for tree in catalan_trees(canonical_leaves(size + 1), word):
                assert tree_constraints_with_associativity(tree, word, assignment) == (
                    tree_constraints(tree, word)
                )


def test_precedence_only_verdict_matches_experiment_0023_predicate():
    for size in (2, 3, 4):
        for word in product(OPERATORS, repeat=size):
            for tree in catalan_trees(canonical_leaves(size + 1), word):
                decision = reachability_with_associativity(tree, word)
                assert decision["precedence_only_reachable"] == strict_reachable(tree, word)


def test_decomposed_decision_matches_naive_assignment_enumeration():
    """Claim C: the one-pass decision equals a brute-force search over all 2**m sides."""
    for size in (2, 3, 4):
        for word in product(OPERATORS, repeat=size):
            types = sorted(set(word))
            assignments = [
                dict(zip(types, choice)) for choice in product(SIDES, repeat=len(types))
            ]
            for tree in catalan_trees(canonical_leaves(size + 1), word):
                decision = reachability_with_associativity(tree, word)
                feasible = [
                    assignment
                    for assignment in assignments
                    if assignment_reachable(tree, word, assignment)
                ]
                assert decision["reachable"] == bool(feasible)
                assert decision["feasible_assignments"] == len(feasible)
                assert decision["assignment_space"] == 2 ** len(types)
                if feasible:
                    assert decision["witness"] in feasible


def test_repeated_operator_chain_is_recovered_by_right_associativity():
    word = ("+", "+")
    right_leaning = ("+", "a", ("+", "b", "c"))
    assert strict_reachable(right_leaning, word) is False
    decision = reachability_with_associativity(right_leaning, word)
    assert decision["reachable"] is True
    assert decision["witness"] == {"+": RIGHT}
    assert decision["allowed_sides"] == {"+": [RIGHT]}
    grammar = from_grammar(strict_grammars()[0], {"+": RIGHT, "-": LEFT, "*": LEFT, "/": LEFT})
    assert associative_tree("a + b + c", grammar) == right_leaning


def test_cyclic_constraint_stays_unreachable_under_every_associativity():
    word = ("+", "*", "+")
    tree = ("+", ("*", ("+", "a", "b"), "c"), "d")
    assert strict_reachable(tree, word) is False
    decision = reachability_with_associativity(tree, word)
    assert decision["acyclic"] is False
    assert decision["reachable"] is False
    assert decision["witness"] is None
    assert decision["feasible_assignments"] == 0


def test_node_profiles_reject_a_tree_that_does_not_match_the_word():
    with pytest.raises(ValueError, match="does not match word operator"):
        node_profiles(("+", ("*", "a", "b"), "c"), ("+", "+"))


# --------------------------------------------------------------------------
# Exhaustive cross-validation
# --------------------------------------------------------------------------


def test_verify_associativity_characterization_up_to_four_operators():
    result = verify_associativity_characterization(4, workers=1)
    assert result["grammar_count"] == 384
    assert result["characterization_holds"] is True
    assert result["total_mismatches"] == 0
    assert result["mismatch_examples"] == []
    assert result["claim_a_prime_holds"] is True
    assert result["split_disagreements"] == 0
    assert result["split_checks"] == (16 + 64 + 256) * 384 == 129024
    assert result["agrees_with_0023"] is True
    assert result["precedence_mismatch_count"] == 0
    assert result["precedence_subset_of_associativity"] is True
    assert [bucket["operator_count"] for bucket in result["per_k"]] == [2, 3, 4]
    assert [bucket["pattern_count"] for bucket in result["per_k"]] == [16, 64, 256]
    assert [bucket["catalan_per_pattern"] for bucket in result["per_k"]] == [2, 5, 14]
    # 0023 reported 4, 124 and 2332 precedence-unreachable trees for k = 2, 3, 4.
    assert [bucket["unreachable_before"] for bucket in result["per_k"]] == [4, 124, 2332]
    assert [bucket["unreachable_after"] for bucket in result["per_k"]] == [0, 60, 1584]
    assert [bucket["recovered_count"] for bucket in result["per_k"]] == [4, 64, 748]


def test_associativity_never_loses_a_precedence_reachable_tree():
    result = verify_associativity_characterization(4, workers=1)
    for bucket in result["per_k"]:
        assert bucket["associativity_reachable"] >= bucket["precedence_reachable"]
        assert bucket["nesting_violations"] == 0


def test_every_two_operator_tree_becomes_reachable():
    result = verify_associativity_characterization(2, workers=1)
    bucket = result["per_k"][0]
    assert bucket["tree_count"] == 32
    assert bucket["associativity_reachable"] == 32
    assert bucket["associativity_coverage"] == 1.0
    assert bucket["recovered_fraction_of_gap"] == 1.0


def test_sequential_and_parallel_verification_agree():
    sequential = verify_associativity_characterization(3, workers=1)
    parallel = verify_associativity_characterization(3, workers=2)
    assert sequential["workers"] == 1
    assert parallel["workers"] == 2
    assert {key: value for key, value in sequential.items() if key != "workers"} == {
        key: value for key, value in parallel.items() if key != "workers"
    }


def test_verify_rejects_a_degenerate_range():
    with pytest.raises(ValueError, match="at least 2"):
        verify_associativity_characterization(1)


# --------------------------------------------------------------------------
# The measured multicore threshold
# --------------------------------------------------------------------------


def test_worker_count_is_derived_from_the_core_count_with_headroom():
    detected = os.cpu_count() or 1
    assert resolve_item_workers(PARALLEL_MINIMUM_ITEMS) == max(
        1, min(detected - 1, PARALLEL_MINIMUM_ITEMS)
    )
    assert resolve_item_workers(10_000) == max(1, detected - 1)


def test_small_workloads_stay_sequential_by_measurement():
    assert PARALLEL_MINIMUM_ITEMS == 128
    assert resolve_item_workers(PARALLEL_MINIMUM_ITEMS - 1) == 1
    assert resolve_item_workers(1) == 1
    # 16 + 64 = 80 operator words for k <= 3, below the threshold; 336 for k <= 4.
    assert verify_associativity_characterization(3)["workers"] == 1


def test_an_explicit_worker_count_always_overrides_the_threshold():
    assert resolve_item_workers(4, workers=3) == 3
    assert resolve_item_workers(2, workers=8) == 2
    with pytest.raises(ValueError, match="at least 1"):
        resolve_item_workers(10, workers=0)


# --------------------------------------------------------------------------
# Coverage
# --------------------------------------------------------------------------


def test_coverage_with_associativity_on_a_repeated_operator_expression():
    record = coverage_with_associativity("a + b + c")
    assert record["catalan_total"] == 2
    assert record["precedence_grammar_count"] == 24
    assert record["associativity_grammar_count"] == 384
    assert record["precedence_reachable"] == 1
    assert record["associativity_reachable"] == 2
    assert record["precedence_coverage"] == 0.5
    assert record["associativity_coverage"] == 1.0
    assert record["recovered_fraction_of_gap"] == 1.0
    assert record["precedence_subset_of_associativity"] is True


def test_coverage_is_bounded_by_the_registry_size_and_never_shrinks():
    for source in ("a + b*c - d/e", "a - b*c + d/e - f", "2*x*x + 1 - x/2 + x"):
        record = coverage_with_associativity(source)
        assert record["precedence_reachable"] <= min(24, record["catalan_total"])
        assert record["associativity_reachable"] <= min(384, record["catalan_total"])
        assert record["associativity_reachable"] >= record["precedence_reachable"]
        assert record["precedence_subset_of_associativity"] is True
        assert record["unreachable_after"] <= record["unreachable_before"]


def test_coverage_agrees_with_the_decision_procedure_on_a_flat_word():
    word = ("+", "*", "+")
    leaves = canonical_leaves(4)
    source = flat_source(leaves, word)
    record = coverage_with_associativity(source)
    predicted = sum(
        reachability_with_associativity(tree, word)["reachable"]
        for tree in catalan_trees(leaves, word)
    )
    assert record["associativity_reachable"] == predicted


# --------------------------------------------------------------------------
# Semantic diversity
# --------------------------------------------------------------------------


def test_semantic_diversity_uses_the_project_class_key_and_grows():
    result = semantic_diversity(("a - b - c",), workers=1)
    record = result["expressions"][0]
    assert result["precedence_grammar_count"] == 24
    assert result["associativity_grammar_count"] == 384
    assert record["precedence_classes"] == 1
    assert record["associativity_classes"] == 2
    assert record["new_classes"] == 1
    assert record["precedence_subset_of_associativity"] is True
    # S(E) = (classes - 1) / 23 is exactly experiment 0017's definition.
    assert record["precedence_sensitivity"] == 0.0
    assert record["associativity_sensitivity"] == pytest.approx(1 / 383)


def test_semantic_diversity_never_loses_a_precedence_class():
    result = semantic_diversity(("2*t + 1 - t/2", "a - b - c"), workers=1)
    assert result["source_count"] == 2
    for record in result["expressions"]:
        assert record["associativity_classes"] >= record["precedence_classes"]
        assert record["associativity_ast_forms"] >= record["precedence_ast_forms"]
        assert record["precedence_subset_of_associativity"] is True
    assert result["class_ratio"] >= 1.0


def test_sequential_and_parallel_semantic_diversity_agree():
    sources = ("a - b - c", "a + b + c")
    sequential = semantic_diversity(sources, workers=1)
    parallel = semantic_diversity(sources, workers=2)
    assert sequential["workers"] == 1
    assert parallel["workers"] == 2
    assert {key: value for key, value in sequential.items() if key != "workers"} == {
        key: value for key, value in parallel.items() if key != "workers"
    }


def test_semantic_diversity_requires_a_source():
    with pytest.raises(ValueError, match="at least one source"):
        semantic_diversity(())


# --------------------------------------------------------------------------
# The extension leaves Generation 1 untouched
# --------------------------------------------------------------------------


def test_generation_1_registry_is_unchanged_by_the_extension():
    assert len(strict_grammars()) == 24
    assert len(all_grammars()) == 25
    assert control_grammar().levels == (("*", "/"), ("+", "-"))
    assert canonical_tree(parse("a - b - c", control_grammar())) == ("-", ("-", "a", "b"), "c")
