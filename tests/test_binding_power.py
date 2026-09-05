"""Experiment 0052: binding power as a vector.

The conservative-extension audit comes first, because nothing else in this file
is worth reading if the vector parser is not the Generation 1 parser widened.
"""

from itertools import product

import pytest

from parseatlas.associativity import (
    LEFT,
    RIGHT,
    AssociativeGrammar,
    associative_tree,
    associativity_space,
)
from parseatlas.binding_power import (
    AUDIT_CORPUS,
    CHAIN_CORPUS,
    COVERAGE_CORPUS,
    PROBE_CORPUS,
    TEMPLATE_CORPUS,
    AmbiguousParse,
    PartialOrderGrammar,
    VectorGrammar,
    agreement_audit,
    associativity_image_audit,
    behaviour_key,
    core_count,
    coverage_table,
    derived_prefix,
    enumerate_2d,
    flat_slice,
    from_associative_grammar,
    from_grammar,
    from_grammar_preorder,
    generation_one_images,
    interior_prefix_probe,
    minimum_brackets,
    new_object_witnesses,
    null_model,
    partial_order_sweep,
    partial_order_tree,
    partial_orders,
    preorders,
    prefix_source,
    prefix_trees,
    reach_2d,
    representatives,
    saturation_scan,
    semantic_key,
    structural_ceiling,
    three_d,
    three_d_representatives,
    vector_parse,
    vector_tree,
    witness_reads_matrix,
    witness_words,
)
from parseatlas.corpus_matrix import restriction_probe_corpus
from parseatlas.grammar import OPERATORS, all_grammars, control_grammar, strict_grammars
from parseatlas.parser import parse
from parseatlas.reachability import canonical_leaves, canonical_tree, catalan_trees, flat_source

# --------------------------------------------------------------------------
# 1.  The conservative-extension audit, and the 2D image of each of the 25
# --------------------------------------------------------------------------

#: The explicit 2D image of every Generation 1 grammar: ``p -> (2p, 2p + 1)``
#: on the level view, so the tied control grammar ``G0`` keeps its two ties.
GENERATION_ONE_IMAGES = {
    "G0": {"*": (4, 5), "+": (2, 3), "-": (2, 3), "/": (4, 5)},
    "G01": {"*": (4, 5), "+": (8, 9), "-": (6, 7), "/": (2, 3)},
    "G02": {"*": (2, 3), "+": (8, 9), "-": (6, 7), "/": (4, 5)},
    "G03": {"*": (6, 7), "+": (8, 9), "-": (4, 5), "/": (2, 3)},
    "G04": {"*": (6, 7), "+": (8, 9), "-": (2, 3), "/": (4, 5)},
    "G05": {"*": (2, 3), "+": (8, 9), "-": (4, 5), "/": (6, 7)},
    "G06": {"*": (4, 5), "+": (8, 9), "-": (2, 3), "/": (6, 7)},
    "G07": {"*": (4, 5), "+": (6, 7), "-": (8, 9), "/": (2, 3)},
    "G08": {"*": (2, 3), "+": (6, 7), "-": (8, 9), "/": (4, 5)},
    "G09": {"*": (6, 7), "+": (4, 5), "-": (8, 9), "/": (2, 3)},
    "G10": {"*": (6, 7), "+": (2, 3), "-": (8, 9), "/": (4, 5)},
    "G11": {"*": (2, 3), "+": (4, 5), "-": (8, 9), "/": (6, 7)},
    "G12": {"*": (4, 5), "+": (2, 3), "-": (8, 9), "/": (6, 7)},
    "G13": {"*": (8, 9), "+": (6, 7), "-": (4, 5), "/": (2, 3)},
    "G14": {"*": (8, 9), "+": (6, 7), "-": (2, 3), "/": (4, 5)},
    "G15": {"*": (8, 9), "+": (4, 5), "-": (6, 7), "/": (2, 3)},
    "G16": {"*": (8, 9), "+": (2, 3), "-": (6, 7), "/": (4, 5)},
    "G17": {"*": (8, 9), "+": (4, 5), "-": (2, 3), "/": (6, 7)},
    "G18": {"*": (8, 9), "+": (2, 3), "-": (4, 5), "/": (6, 7)},
    "G19": {"*": (2, 3), "+": (6, 7), "-": (4, 5), "/": (8, 9)},
    "G20": {"*": (4, 5), "+": (6, 7), "-": (2, 3), "/": (8, 9)},
    "G21": {"*": (2, 3), "+": (4, 5), "-": (6, 7), "/": (8, 9)},
    "G22": {"*": (4, 5), "+": (2, 3), "-": (6, 7), "/": (8, 9)},
    "G23": {"*": (6, 7), "+": (4, 5), "-": (2, 3), "/": (8, 9)},
    "G24": {"*": (6, 7), "+": (2, 3), "-": (4, 5), "/": (8, 9)},
}


def test_every_generation_one_grammar_has_an_explicit_2d_image():
    images = {
        grammar.id: {operator: (left, right) for operator, left, right in image.powers}
        for grammar, image in generation_one_images()
    }
    assert len(images) == 25
    assert images == GENERATION_ONE_IMAGES


def test_the_tied_control_grammar_keeps_its_ties_in_the_image():
    image = from_grammar(control_grammar())
    powers = {operator: (left, right) for operator, left, right in image.powers}
    assert powers["*"] == powers["/"]
    assert powers["+"] == powers["-"]
    assert powers["*"][0] > powers["+"][1]


def test_agreement_audit_is_a_conservative_extension():
    report = agreement_audit()
    assert report["grammar_count"] == 25
    assert report["source_count"] == 36
    assert report["cell_count"] == 900
    assert report["agreement_count"] == 900
    assert report["divergence_count"] == 0
    assert report["grammars_without_image"] == []
    assert report["conservative_extension"] is True
    assert all(record["has_2d_image"] for record in report["grammars"])


def test_audit_corpus_covers_the_earlier_experiments():
    for source in COVERAGE_CORPUS + TEMPLATE_CORPUS + CHAIN_CORPUS:
        assert source in AUDIT_CORPUS
    assert any("(" in source for source in AUDIT_CORPUS)


def _all_right_image(grammar):
    """A deliberately wrong image: every pair written in the other order."""
    from parseatlas.reachability import grammar_binding_power

    powers = grammar_binding_power(grammar)
    return VectorGrammar(
        f"{grammar.id}-BROKEN",
        tuple(
            (operator, 2 * power + 1, 2 * power) for operator, power in sorted(powers.items())
        ),
    )


def _one_broken_image(grammar):
    """Correct for every grammar but ``G07``, where ``+`` and ``-`` are swapped."""
    image = from_grammar(grammar)
    if grammar.id != "G07":
        return image
    powers = {operator: (left, right) for operator, left, right in image.powers}
    powers["+"], powers["-"] = powers["-"], powers["+"]
    return VectorGrammar(
        f"{grammar.id}-BROKEN",
        tuple((operator, left, right) for operator, (left, right) in sorted(powers.items())),
    )


def test_audit_reports_a_divergence_it_is_shown():
    report = agreement_audit(image_of=_all_right_image)
    assert report["conservative_extension"] is False
    assert report["divergence_count"] > 0
    assert report["agreement_count"] + report["divergence_count"] == report["cell_count"]
    assert len(report["grammars_without_image"]) == 25
    example = next(
        record for record in report["grammars"] if record["divergences"]
    )["divergences"][0]
    assert example["expected"] != example["actual"]


def test_audit_names_the_single_grammar_that_diverges():
    report = agreement_audit(image_of=_one_broken_image)
    assert report["conservative_extension"] is False
    assert report["grammars_without_image"] == ["G07"]
    broken = next(record for record in report["grammars"] if record["grammar_id"] == "G07")
    assert broken["divergence_count"] > 0
    assert broken["cell_count"] == 36
    others = [
        record for record in report["grammars"] if record["grammar_id"] != "G07"
    ]
    assert all(record["divergence_count"] == 0 for record in others)


# --------------------------------------------------------------------------
# 2.  Associativity is the order within the pair
# --------------------------------------------------------------------------


def test_pair_order_decides_associativity_on_the_tree():
    leftward = VectorGrammar("left", (("-", 2, 3),))
    rightward = VectorGrammar("right", (("-", 3, 2),))
    assert vector_tree("a - b - c", leftward) == ("-", ("-", "a", "b"), "c")
    assert vector_tree("a - b - c", rightward) == ("-", "a", ("-", "b", "c"))
    assert leftward.sides["-"] == LEFT
    assert rightward.sides["-"] == RIGHT


def test_equal_components_parse_left():
    even = VectorGrammar("even", (("-", 3, 3),))
    assert vector_tree("a - b - c", even) == ("-", ("-", "a", "b"), "c")
    assert even.sides["-"] == LEFT


def test_the_two_numbers_are_the_same_two_numbers():
    """Left and right associativity differ only in the order of one pair."""
    leftward = VectorGrammar("left", (("-", 2, 3),))
    rightward = VectorGrammar("right", (("-", 3, 2),))
    assert {leftward.left["-"], leftward.right["-"]} == {
        rightward.left["-"],
        rightward.right["-"],
    }


def test_associativity_registry_embeds_in_the_pair():
    report = associativity_image_audit()
    assert report["grammar_count"] == 388
    assert report["source_count"] == 5
    assert report["cell_count"] == 1940
    assert report["agreement_count"] == 1940
    assert report["divergence_count"] == 0
    assert report["embeds"] is True
    assert report["distinct_images"] == 388


def test_from_associative_grammar_matches_the_all_left_image():
    for grammar in strict_grammars():
        lifted = AssociativeGrammar(
            f"{grammar.id}-LLLL",
            grammar.levels,
            tuple((operator, LEFT) for operator in OPERATORS),
        )
        assert from_associative_grammar(lifted).powers == from_grammar(grammar).powers


# --------------------------------------------------------------------------
# 3.  The behavioural quotient
# --------------------------------------------------------------------------


def test_two_different_assignments_that_induce_the_same_parser_are_one_point():
    first = VectorGrammar("a", (("+", 1, 2), ("-", 1, 2), ("*", 3, 4), ("/", 3, 4)))
    second = VectorGrammar("b", (("+", 11, 40), ("-", 11, 40), ("*", 90, 99), ("/", 90, 99)))
    assert first.powers != second.powers
    assert first.comparison_matrix(OPERATORS) == second.comparison_matrix(OPERATORS)
    assert behaviour_key(first) == behaviour_key(second)
    for source in COVERAGE_CORPUS + CHAIN_CORPUS:
        assert vector_tree(source, first) == vector_tree(source, second)


def test_two_assignments_that_do_not_induce_the_same_parser_are_two_points():
    first = VectorGrammar("a", (("+", 1, 2), ("-", 1, 2), ("*", 3, 4), ("/", 3, 4)))
    second = VectorGrammar("b", (("+", 2, 1), ("-", 1, 2), ("*", 3, 4), ("/", 3, 4)))
    assert behaviour_key(first) != behaviour_key(second)
    assert vector_tree("a + b + c", first) != vector_tree("a + b + c", second)


def test_the_witness_family_reads_the_comparison_matrix():
    assert len(witness_words(OPERATORS)) == 16
    for grammar in representatives(("+", "-", "*"))[:200]:
        assert witness_reads_matrix(grammar, ("+", "-", "*"))
    for _, image in generation_one_images():
        assert witness_reads_matrix(image)


@pytest.mark.parametrize(
    "operators,bound,raw,behavioural",
    [
        (("+",), 2, 4, 2),
        (("+", "-"), 3, 81, 14),
        (("+", "-", "*"), 4, 4096, 230),
    ],
)
def test_enumerate_2d_reports_raw_and_behavioural_counts(operators, bound, raw, behavioural):
    report = enumerate_2d(operators, bound, workers=1)
    assert report["raw_assignment_count"] == raw
    assert report["behavioural_count"] == behavioural
    assert report["matrix_count"] == behavioural
    assert report["matrix_equals_behaviour"] is True
    assert report["collapse_factor"] == raw / behavioural


def test_the_full_operator_alphabet_has_6902_parsers():
    assert len(representatives(OPERATORS)) == 6902
    assert len(representatives(("+", "-", "*"))) == 230
    assert len(representatives(("+", "-"))) == 14
    assert len(representatives(("+",))) == 2


def test_representatives_agree_with_the_parse_based_quotient():
    for operators, bound in ((("+", "-"), 3), (("+", "-", "*"), 4)):
        by_parse = enumerate_2d(operators, bound, workers=1)
        by_matrix = representatives(operators, bound)
        assert len(by_matrix) == by_parse["behavioural_count"]
        assert len({behaviour_key(grammar, operators) for grammar in by_matrix}) == len(
            by_matrix
        )


def test_the_enumeration_bound_saturates_where_it_is_read():
    report = saturation_scan(("+", "-", "*"), (2, 3, 4, 5, 6))
    assert [row["behavioural_count"] for row in report["levels"]] == [50, 194, 230, 230, 230]
    assert report["saturating_bound"] == 4
    assert report["predicted_saturating_bound"] == 4
    assert report["saturated"] is True
    assert [row["raw_assignment_count"] for row in report["levels"]] == [
        64,
        729,
        4096,
        15625,
        46656,
    ]


def test_the_flat_model_is_730_of_the_6902_parsers():
    """What a scalar binding power can express, levels and associativity included."""
    report = flat_slice(OPERATORS)
    assert report["raw_flat_grammar_count"] == 730
    assert report["flat_parser_count"] == 730
    assert report["vector_parser_count"] == 6902
    assert report["vector_only_parser_count"] == 6172
    assert round(report["flat_fraction"] * 100, 3) == 10.577
    smaller = flat_slice(("+", "-", "*"))
    assert smaller["flat_parser_count"] == 74
    assert smaller["vector_parser_count"] == 230


def test_the_25_registered_grammars_are_inside_the_flat_slice():
    matrices = {
        image.comparison_matrix(OPERATORS) for _, image in generation_one_images()
    }
    assert len(matrices) == 25
    every = {grammar.comparison_matrix(OPERATORS) for grammar in representatives(OPERATORS)}
    assert matrices <= every


def test_the_structural_ceiling_is_arithmetic_past_the_walked_range():
    rows = {row["operator_count"]: row for row in structural_ceiling()["levels"]}
    assert rows[6]["catalan"] == 132
    assert round(rows[6]["vector_ceiling"], 4) == 52.2879
    assert round(rows[9]["vector_ceiling"], 4) == 1.4196
    assert round(rows[10]["vector_ceiling"], 4) == 0.4109
    assert round(rows[7]["associativity_ceiling"], 4) == 0.8951


def test_the_three_d_space_has_41506_parsers():
    assert len(three_d_representatives(OPERATORS)) == 41506
    assert len(three_d_representatives(("+", "-", "*"))) == 1066
    assert len(three_d_representatives(("+", "-"))) == 46
    assert len(three_d_representatives(("+",), prefix_operator="+")) == 4


# --------------------------------------------------------------------------
# 4.  Reach, against 0020 and 0030
# --------------------------------------------------------------------------

#: Experiment 0020 / 0023, quoted from ``experiments/0020_ast_space_coverage``
#: and from 0030's precedence column.
PRECEDENCE_REACHABLE = {2: 28, 3: 196, 4: 1252, 5: 7180, 6: 37420}
#: Experiment 0030, quoted from its headline table.
ASSOCIATIVITY_REACHABLE = {2: 32, 3: 260, 4: 2000, 5: 14192, 6: 92504}
#: This experiment.
VECTOR_REACHABLE = {2: 32, 3: 284, 4: 2552, 5: 22160, 6: 181640}


def test_reach_reproduces_0020_and_0030_and_pins_the_2d_column():
    report = reach_2d(6, workers=1)
    for bucket in report["per_k"]:
        size = bucket["operator_count"]
        assert bucket["precedence_reachable"] == PRECEDENCE_REACHABLE[size]
        assert bucket["associativity_reachable"] == ASSOCIATIVITY_REACHABLE[size]
        assert bucket["vector_reachable"] == VECTOR_REACHABLE[size]
    assert report["total_trees"] == 587616
    assert report["precedence_reachable"] == 46076
    assert report["associativity_reachable"] == 108988
    assert report["vector_reachable"] == 206668
    assert report["unreachable_before"] == 541540
    assert report["associativity_recovered"] == 62912
    assert report["vector_recovered"] == 160592
    assert round(report["associativity_recovered_fraction"] * 100, 3) == 11.617
    assert round(report["vector_recovered_fraction"] * 100, 3) == 29.655
    assert report["vector_beats_associativity"] is True


def test_the_2d_space_reaches_more_than_precedence_with_associativity():
    report = reach_2d(4, workers=1)
    assert report["vector_reachable"] > report["associativity_reachable"]
    assert report["associativity_reachable"] > report["precedence_reachable"]


def test_the_pattern_reduced_walk_equals_the_full_walk():
    reduced = reach_2d(3, workers=1)
    full = reach_2d(3, workers=1, reduce_by_pattern=False)
    assert reduced["task_count"] == 7
    assert full["task_count"] == 80
    for field in (
        "total_trees",
        "total_words",
        "precedence_reachable",
        "associativity_reachable",
        "vector_reachable",
    ):
        assert reduced[field] == full[field]


def test_per_expression_coverage_matches_0020_and_0030_means():
    table = coverage_table()
    assert table["mean_precedence_coverage"] == 0.6801948051948052
    assert table["mean_associativity_coverage"] == 0.814935064935065
    assert table["mean_vector_coverage"] == 0.9267676767676768
    reachable = {
        record["source"]: (
            record["precedence_reachable"],
            record["associativity_reachable"],
            record["vector_reachable"],
        )
        for record in table["expressions"]
    }
    assert reachable["a + b*c"] == (2, 2, 2)
    assert reachable["a + b + c"] == (1, 2, 2)
    assert reachable["2*t + 1 - t/2"] == (14, 14, 14)
    assert reachable["a + b*c - d/e"] == (14, 14, 14)
    assert reachable["a - b*c + d/e - f"] == (19, 24, 42)
    assert reachable["2*x*x + 1 - x/2 + x"] == (17, 42, 74)
    assert all(record["vector_contains_associativity"] for record in table["expressions"])


def test_a_tree_no_precedence_and_no_associativity_reaches_is_reached_by_a_vector():
    """`a * (b + c)` from an asymmetric pair, the parse 0030's space cannot make."""
    source = "a * b + c"
    asymmetric = VectorGrammar(
        "asymmetric", (("+", 2, 3), ("-", 2, 3), ("*", 10, 1), ("/", 10, 1))
    )
    assert vector_tree(source, asymmetric) == ("*", "a", ("+", "b", "c"))
    assert vector_tree("a + b * c", asymmetric) == ("+", "a", ("*", "b", "c"))
    # The same grammar reads `*` as tighter on the left and looser on the right.
    assert asymmetric.left["*"] > asymmetric.left["+"]
    assert asymmetric.right["*"] < asymmetric.right["+"]


# --------------------------------------------------------------------------
# 5.  The third component
# --------------------------------------------------------------------------


def test_the_prefixed_word_space_is_the_catalan_convolution():
    for size in range(1, 6):
        leaves = canonical_leaves(size + 1)
        trees = prefix_trees(leaves, ("+",) * size)
        expected = len(catalan_trees(canonical_leaves(size + 2), ("+",) * (size + 1)))
        assert len(trees) == expected
        assert len(set(trees)) == len(trees)


def test_a_prefix_power_parses_a_prefixed_source():
    grammar = VectorGrammar(
        "p", (("+", 2, 3), ("-", 2, 3), ("*", 4, 5), ("/", 4, 5)), (("-", 9),)
    )
    assert prefix_source(("a", "b"), ("+",)) == "- a + b"
    assert vector_tree("- a + b", grammar) == ("+", ("-", "a"), "b")
    loose = VectorGrammar(
        "q", (("+", 2, 3), ("-", 2, 3), ("*", 4, 5), ("/", 4, 5)), (("-", 1),)
    )
    assert vector_tree("- a + b", loose) == ("-", ("+", "a", "b"))


def test_the_third_component_is_inert_on_words_without_a_prefix():
    space = representatives(OPERATORS)[:400]
    leaves = canonical_leaves(4)
    for word in product(OPERATORS, repeat=3):
        source = flat_source(leaves, word)
        for grammar in space[:20]:
            plain = vector_tree(source, grammar)
            for power in (1, 3, 7, 40):
                lifted = VectorGrammar(grammar.id + "p", grammar.powers, (("-", power),))
                assert vector_tree(source, lifted) == plain


THREE_D_TWO = {2: 71, 3: 638, 4: 5540, 5: 45410}
THREE_D_THREE = {2: 76, 3: 736, 4: 6952, 5: 62320}
THREE_D_TREES = {2: 80, 3: 896, 4: 10752, 5: 135168}


def test_three_d_reach_is_pinned():
    report = three_d(5, workers=15)
    for bucket in report["per_k"]:
        size = bucket["operator_count"]
        assert bucket["tree_count"] == THREE_D_TREES[size]
        assert bucket["two_d_reachable"] == THREE_D_TWO[size]
        assert bucket["three_d_reachable"] == THREE_D_THREE[size]
    assert report["total_trees"] == 146896
    assert report["two_d_reachable"] == 51659
    assert report["three_d_reachable"] == 70084
    assert report["gained"] == 18425
    assert round(report["gain_fraction_of_gap"] * 100, 3) == 19.346
    assert report["gain_ratio_still_rising"] is True
    assert [round(ratio, 4) for ratio in report["gain_ratio_by_k"]] == [
        1.0704,
        1.1536,
        1.2549,
        1.3724,
    ]


def test_the_third_component_still_buys_on_words_the_sweep_omits():
    """The sweep prefixes only the head; this is what it does not produce."""
    report = interior_prefix_probe()
    assert report["source_count"] == 8
    assert report["two_d_trees"] == 18
    assert report["three_d_trees"] == 19
    assert report["gained"] == 1
    assert report["sources_with_a_gain"] == 1
    assert report["containment_holds"] is True


# --------------------------------------------------------------------------
# 6.  Partial orders: refusing instead of choosing
# --------------------------------------------------------------------------


def test_the_preorder_space_is_the_declared_one():
    space = preorders(OPERATORS)
    assert len(space) == 355
    assert sum(1 for grammar in space if grammar.incomparable_pair_count == 0) == 75
    assert sum(1 for grammar in space if grammar.incomparable_pair_count == 6) == 1


def test_the_25_conventional_grammars_are_total_preorders_in_the_space():
    space = {grammar.relation for grammar in preorders(OPERATORS)}
    for registered in all_grammars():
        image = from_grammar_preorder(registered)
        assert image.relation in space
        assert image.incomparable_pair_count == 0
        for source in AUDIT_CORPUS:
            assert partial_order_tree(source, image) == canonical_tree(
                parse(source, registered)
            )


def test_a_partial_order_refuses_an_ambiguous_source():
    unranked = PartialOrderGrammar(
        "plus-times-unranked",
        (("*", "*"), ("+", "+")),
        (("*", LEFT), ("+", LEFT)),
    )
    assert unranked.compare("+", "*") == "incomparable"
    with pytest.raises(AmbiguousParse):
        partial_order_tree("a + b * c", unranked)
    # It refuses; it does not silently pick a reading.
    assert partial_order_tree("a + b + c", unranked) == ("+", ("+", "a", "b"), "c")
    assert partial_order_tree("a + (b * c)", unranked) == ("+", "a", ("*", "b", "c"))
    assert partial_order_tree("(a + b) * c", unranked) == ("*", ("+", "a", "b"), "c")


def test_a_ranked_pair_is_not_refused():
    ranked = PartialOrderGrammar(
        "times-over-plus",
        (("*", "*"), ("+", "+"), ("*", "+")),
        (("*", LEFT), ("+", LEFT)),
    )
    assert ranked.compare("*", "+") == "tighter"
    assert partial_order_tree("a + b * c", ranked) == ("+", "a", ("*", "b", "c"))


def test_minimum_brackets_is_a_minimum_and_writes_the_same_tree():
    antichain = next(
        grammar for grammar in preorders(OPERATORS) if grammar.incomparable_pair_count == 6
    )
    tree = ("+", "a", ("*", "b", "c"))
    assert minimum_brackets(tree, antichain) == 1
    assert minimum_brackets(("+", ("+", "a", "b"), "c"), antichain) == 0
    ranked = from_grammar_preorder(control_grammar())
    assert minimum_brackets(tree, ranked) == 0
    assert minimum_brackets(("*", ("+", "a", "b"), "c"), ranked) == 1


def test_partial_orders_prices_both_sides():
    report = partial_orders(workers=1)
    assert report["preorder_count"] == 355
    assert report["total_preorder_count"] == 75
    assert report["strict_total_order_count"] == 24
    assert report["conventional_preorders_present"] is True
    assert report["cell_count"] == 2130
    assert report["refusal_count"] == 1189
    assert report["true_refusal_count"] == 1189
    assert report["over_refusal_count"] == 0
    assert report["refusal_precision"] == 1.0
    assert report["silent_choice_count"] == 586
    assert report["antichain_refused_sources"] == 5
    assert report["conventional_reading_count"] == 150
    assert report["conventional_readings_needing_brackets"] == 125
    assert report["conventional_readings_unwritable"] == 0
    assert report["mean_minimum_brackets"] == 2.4066666666666667
    assert report["max_minimum_brackets"] == 4
    assert [level["refusal_count"] for level in report["levels"]] == [
        0,
        158,
        323,
        378,
        238,
        87,
        5,
    ]


def test_partial_order_sweep_never_over_refuses():
    report = partial_order_sweep(4)
    assert report["preorder_count"] == 355
    assert report["cell_count"] == 119280
    assert report["refusal_count"] == 58536
    assert report["true_refusal_count"] == 58536
    assert report["over_refusal_count"] == 0
    assert report["refusal_precision"] == 1.0
    assert report["silent_choice_count"] == 56484
    assert [level["refusal_count"] for level in report["levels"]] == [1512, 9576, 47448]
    assert [level["choice_bearing_words"] for level in report["levels"]] == [12, 60, 252]


def test_fixing_associativity_does_not_move_the_refusals():
    """The declared subset defended by observation, not by argument."""
    left = partial_order_sweep(4, side=LEFT)
    right = partial_order_sweep(4, side=RIGHT)
    for field in (
        "cell_count",
        "refusal_count",
        "true_refusal_count",
        "over_refusal_count",
        "silent_choice_count",
    ):
        assert left[field] == right[field]
    assert left["side"] == "left"
    assert right["side"] == "right"


# --------------------------------------------------------------------------
# 7.  The null model
# --------------------------------------------------------------------------


def test_the_probe_corpus_is_the_0024_one():
    generated = tuple(item["source"] for item in restriction_probe_corpus()["expressions"])
    assert PROBE_CORPUS == generated


def test_null_model_answer_is_pinned():
    report = null_model(workers=1)
    assert report["expression_count"] == 31
    assert report["new_classes_over_associativity"] == 32
    assert report["new_classes_over_precedence"] == 57
    assert report["sources_with_new_class"] == 9
    assert report["second_dimension_buys_nothing"] is False
    by_corpus = {record["corpus"]: record for record in report["corpora"]}
    assert by_corpus["0017 corpus"]["new_classes"] == 0
    assert by_corpus["0017 corpus"]["precedence_classes"] == 27
    assert by_corpus["0017 corpus"]["associativity_classes"] == 27
    assert by_corpus["0017 corpus"]["vector_classes"] == 27
    assert by_corpus["0017 corpus"]["associativity_forms"] == 59
    assert by_corpus["0017 corpus"]["vector_forms"] == 59
    assert by_corpus["0020 corpus"]["new_classes"] == 19
    assert by_corpus["0024 restriction probe"]["new_classes"] == 9
    assert by_corpus["chain probe"]["new_classes"] == 4


def test_the_gain_is_stratified_by_operator_support():
    report = null_model(workers=1)
    by_support = {tuple(record["support"]): record for record in report["strata"]}
    assert by_support[("+",)]["new_classes"] == 0
    assert by_support[("*", "+", "-", "/")]["new_classes"] == 19
    assert by_support[("-", "/")]["new_classes"] == 11
    assert by_support[("*", "-")]["new_classes"] == 2
    assert sum(record["new_classes"] for record in report["strata"]) == 32
    single = [record for record in report["strata"] if record["support_size"] == 1]
    assert len(single) == 3
    assert all(record["new_classes"] == 0 for record in single)


def test_the_second_dimension_buys_objects_on_the_corpus_that_bought_none():
    """T30's corpus, on a deterministic 250-source prefix of it."""
    from parseatlas.corpus_matrix import generate_corpus

    sources = tuple(item["source"] for item in generate_corpus()["expressions"])[:250]
    report = null_model({"0024 corpus prefix": sources}, workers=15)
    record = report["corpora"][0]
    assert record["expression_count"] == 250
    assert record["precedence_forms"] == 1800
    assert record["associativity_forms"] == 2700
    assert record["vector_forms"] == 6200
    assert record["precedence_classes"] == 975
    assert record["associativity_classes"] == 975
    assert record["vector_classes"] == 2100
    assert record["new_classes"] == 1125
    assert record["sources_with_new_class"] == 100
    assert record["associativity_forms"] / record["precedence_forms"] == 1.5


def test_a_new_object_has_a_named_witness():
    witnesses = new_object_witnesses(("2*x*x + 1 - x/2 + x",), limit=1)
    assert len(witnesses) == 1
    record = witnesses[0]
    grammar = VectorGrammar(
        "witness",
        tuple((operator, *record["vector"][operator]) for operator in sorted(record["vector"])),
    )
    assert vector_tree(record["source"], grammar) == record["tree"]
    assert semantic_key(record["tree"])[0] == record["canonical"]
    extended = associativity_space()
    known = {semantic_key(associative_tree(record["source"], item)) for item in extended}
    assert semantic_key(record["tree"]) not in known


def test_the_domain_component_of_the_key_is_inert():
    """NF-2026-00005: ``canonicalize`` writes the literal ``R`` for everything."""
    keys = {semantic_key(canonical_tree(parse(source, control_grammar()))) for source in AUDIT_CORPUS}
    assert {key[1] for key in keys} == {"R"}


# --------------------------------------------------------------------------
# 8.  Sequential and parallel agree
# --------------------------------------------------------------------------


def test_core_count_is_observed_not_hardcoded():
    assert core_count() >= 1


def _strip(report):
    return {key: value for key, value in report.items() if key != "workers"}


def test_sequential_and_parallel_reach_agree():
    sequential = reach_2d(3, workers=1)
    parallel = reach_2d(3, workers=2)
    assert sequential["workers"] == 1
    assert parallel["workers"] == 2
    assert _strip(sequential) == _strip(parallel)


def test_sequential_and_parallel_enumeration_agree():
    sequential = enumerate_2d(("+", "-", "*"), 4, workers=1)
    parallel = enumerate_2d(("+", "-", "*"), 4, workers=2)
    assert parallel["workers"] == 2
    assert sequential["behavioural_count"] == parallel["behavioural_count"]
    assert sequential["raw_assignment_count"] == parallel["raw_assignment_count"]
    assert sequential["matrix_count"] == parallel["matrix_count"]


def test_sequential_and_parallel_partial_orders_agree():
    sequential = partial_orders(workers=1)
    parallel = partial_orders(workers=2)
    assert parallel["workers"] == 2
    assert _strip(sequential) == _strip(parallel)


def test_sequential_and_parallel_null_model_agree():
    sequential = null_model(workers=1)
    parallel = null_model(workers=2)
    assert parallel["workers"] == 2
    assert _strip(sequential) == _strip(parallel)


def test_sequential_and_parallel_three_d_agree():
    sequential = three_d(2, workers=1)
    parallel = three_d(2, workers=2)
    assert parallel["workers"] == 2
    assert _strip(sequential) == _strip(parallel)


# --------------------------------------------------------------------------
# Guards on the objects themselves
# --------------------------------------------------------------------------


def test_a_zero_left_power_is_rejected():
    with pytest.raises(ValueError):
        VectorGrammar("bad", (("+", 0, 1),))


def test_an_operator_may_not_be_ranked_twice():
    with pytest.raises(ValueError):
        VectorGrammar("bad", (("+", 1, 2), ("+", 3, 4)))


def test_a_prefix_power_needs_a_ranked_operator():
    with pytest.raises(ValueError):
        VectorGrammar("bad", (("+", 1, 2),), (("-", 3),))


def test_a_non_transitive_relation_is_rejected():
    with pytest.raises(ValueError):
        PartialOrderGrammar(
            "bad",
            (("*", "*"), ("+", "+"), ("-", "-"), ("*", "+"), ("+", "-")),
            (("*", LEFT), ("+", LEFT), ("-", LEFT)),
        )


def test_an_irreflexive_relation_is_rejected():
    with pytest.raises(ValueError):
        PartialOrderGrammar("bad", (("*", "+"),), (("*", LEFT), ("+", LEFT)))


def test_vector_parse_returns_parser_nodes():
    grammar = from_grammar(control_grammar())
    node = vector_parse("a + b*c", grammar)
    assert canonical_tree(node) == ("+", "a", ("*", "b", "c"))
    assert derived_prefix(grammar).prefix_power["-"] == grammar.right["-"]
