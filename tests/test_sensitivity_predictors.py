"""Experiment 0029 tests.

Two kinds of test live here. Most run on hand-written rows or a small slice of the published
corpus and are pure unit tests. A separate block, marked by the ``corpus_table`` fixture, runs the
full 3125-expression corpus once: the trap this card is about is a statement about that corpus, so
the numbers that answer it cannot be pinned on a toy sub-corpus.
"""

import itertools
import math
from fractions import Fraction

import pytest

from parseatlas.corpus_matrix import PARALLEL_MINIMUM_ITEMS, corpus_records, generate_corpus
from parseatlas.grammar import strict_grammars
from parseatlas.sensitivity_predictors import (
    CATEGORICAL_FEATURES,
    FEATURE_BY_NAME,
    FEATURE_NAMES,
    FEATURES,
    INDEPENDENT_FEATURES,
    ORDERED_FEATURES,
    PARSER_RESTATING_FEATURES,
    average_ranks,
    constant_features,
    expression_features,
    explained_partition,
    feature_catalog,
    feature_rows,
    feature_table,
    feature_values,
    ground_truth,
    group_spread,
    holdout_check,
    leave_one_group_out_check,
    literal_value,
    predictor_strength,
    resolve_feature_workers,
    spearman,
    within_support_report,
)
from parseatlas.support_reduction import serialized_ast
from parseatlas.tokenizer import tokenize

LINEAR = "2*x + 3 - 4*x/5"
RIGID_RATIONAL = "(1*x + 2)/(1*x - 3)"
QUADRATIC = "2*x*x + 3*x - 4/5"
CUBIC = "2*x*x*x + 3*x*x - 4*x + 5"
MIXED = "2/3 + 4*x - 5/2"

#: The feature set the report publishes: token shape plus the two unit-coefficient counts.
CHOSEN = ("operator_profile", "parenthesis_pair_count", "unit_multiplier_count", "unit_divisor_count")

SMALL_CORPUS = (
    {"index": 0, "family": "linear", "source": LINEAR},
    {"index": 1, "family": "quadratic", "source": QUADRATIC},
    {"index": 2, "family": "cubic", "source": CUBIC},
    {"index": 3, "family": "rational", "source": RIGID_RATIONAL},
    {"index": 4, "family": "mixed_chain", "source": MIXED},
)


@pytest.fixture(scope="module")
def small_table():
    records = corpus_records(SMALL_CORPUS, workers=1)["records"]
    return feature_table(SMALL_CORPUS, records=records)


@pytest.fixture(scope="module")
def corpus_table():
    """The published 3125-expression corpus, measured once for the whole module."""
    corpus = generate_corpus()
    return feature_table(corpus)


@pytest.fixture(scope="module")
def corpus_strength(corpus_table):
    """One support-size-stratified association pass, shared by every trap test."""
    return predictor_strength(corpus_table)


# ------------------------------------------------------------------------------ feature catalog


def test_the_feature_set_is_closed_and_self_consistent():
    assert len(FEATURE_NAMES) == len(set(FEATURE_NAMES))
    assert set(ORDERED_FEATURES) | set(CATEGORICAL_FEATURES) == set(FEATURE_NAMES)
    assert not set(ORDERED_FEATURES) & set(CATEGORICAL_FEATURES)
    assert set(PARSER_RESTATING_FEATURES) | set(INDEPENDENT_FEATURES) == set(FEATURE_NAMES)
    assert not set(PARSER_RESTATING_FEATURES) & set(INDEPENDENT_FEATURES)
    for feature in FEATURES:
        assert feature.kind in {"ordered", "categorical"}
        assert feature.origin in {"token", "operator-word", "coefficient", "parse"}
        assert feature.motivation.strip()
    assert tuple(entry["name"] for entry in feature_catalog()) == FEATURE_NAMES


def test_every_expression_carries_exactly_the_declared_features():
    assert set(expression_features(LINEAR)) == set(FEATURE_NAMES)


def test_the_parser_restating_features_are_the_declared_four():
    assert PARSER_RESTATING_FEATURES == (
        "support_size",
        "parenthesis_pair_count",
        "distinct_ast_count",
        "strict_reachable_tree_count",
    )


# ----------------------------------------------------------------------------- feature extraction


def test_features_are_deterministic():
    assert expression_features(LINEAR) == expression_features(LINEAR)
    assert expression_features(RIGID_RATIONAL) == expression_features(RIGID_RATIONAL)


def test_hand_computed_feature_vector_for_the_linear_representative():
    # 2*x + 3 - 4*x/5 : tokens 2 * x + 3 - 4 * x / 5
    #   operators  * + - * /   -> 5 tokens, distinct support {*, +, -, /} of size 4
    #   leaves     2 x 3 4 x 5 -> 6, of which x twice is the only variable
    #   multiplicities * x2, + x1, - x1, / x1 -> max 2, one repeated operator
    #   no parentheses, no literal 0 or 1, no rational literal
    #   Catalan(5) = 42 trees over the operator word; 17 of them precedence-reachable
    assert expression_features(LINEAR) == {
        "support_size": 4,
        "operator_count": 5,
        "leaf_count": 6,
        "variable_leaf_count": 2,
        "distinct_variable_count": 1,
        "parenthesis_pair_count": 0,
        "division_operator_count": 1,
        "has_division": 1,
        "max_operator_multiplicity": 2,
        "repeated_operator_count": 1,
        "operator_profile": "* x2, + x1, - x1, / x1",
        "repetition_pattern": "2+1+1+1",
        "unit_literal_count": 0,
        "zero_literal_count": 0,
        "unit_multiplier_count": 0,
        "unit_divisor_count": 0,
        "degenerate_coefficient": 0,
        "fractional_literal_count": 0,
        "distinct_ast_count": 17,
        "operator_word_catalan_count": 42,
        "strict_reachable_tree_count": 17,
    }


def test_hand_computed_feature_vector_for_the_rigid_rational():
    # (1*x + 2)/(1*x - 3) : same operator multiset as the linear one, two parenthesis pairs,
    # two literal 1s and both of them sit next to a *, so unit_multiplier_count is 2 while
    # unit_divisor_count stays 0 - the / is followed by '(' and not by a literal.
    assert expression_features(RIGID_RATIONAL) == {
        "support_size": 4,
        "operator_count": 5,
        "leaf_count": 6,
        "variable_leaf_count": 2,
        "distinct_variable_count": 1,
        "parenthesis_pair_count": 2,
        "division_operator_count": 1,
        "has_division": 1,
        "max_operator_multiplicity": 2,
        "repeated_operator_count": 1,
        "operator_profile": "* x2, + x1, - x1, / x1",
        "repetition_pattern": "2+1+1+1",
        "unit_literal_count": 2,
        "zero_literal_count": 0,
        "unit_multiplier_count": 2,
        "unit_divisor_count": 0,
        "degenerate_coefficient": 1,
        "fractional_literal_count": 0,
        "distinct_ast_count": 4,
        "operator_word_catalan_count": 42,
        "strict_reachable_tree_count": 17,
    }


def test_the_two_hand_computed_vectors_differ_only_where_the_sources_differ():
    linear = expression_features(LINEAR)
    rational = expression_features(RIGID_RATIONAL)
    differing = {name for name in FEATURE_NAMES if linear[name] != rational[name]}
    assert differing == {
        "parenthesis_pair_count",
        "unit_literal_count",
        "unit_multiplier_count",
        "degenerate_coefficient",
        "distinct_ast_count",
    }


def test_a_slash_inside_a_number_token_is_a_literal_and_not_a_division_operator():
    features = expression_features(QUADRATIC)
    assert features["has_division"] == 0
    assert features["division_operator_count"] == 0
    assert features["fractional_literal_count"] == 1
    assert features["support_size"] == 3
    assert literal_value(tokenize("4/5")[0]) == Fraction(4, 5)


def test_unit_divisor_is_counted_only_immediately_after_a_division_operator():
    assert expression_features("2*x + 3 - 4*x/1")["unit_divisor_count"] == 1
    assert expression_features("2*x + 3 - 4*x/1")["unit_multiplier_count"] == 0
    assert expression_features("1*x + 3 - 4*x/5")["unit_divisor_count"] == 0
    assert expression_features("1*x + 3 - 4*x/5")["unit_multiplier_count"] == 1


def test_distinct_ast_count_is_taken_over_the_twenty_four_strict_grammars():
    strict = len({serialized_ast(CUBIC, grammar) for grammar in strict_grammars()})
    assert expression_features(CUBIC)["distinct_ast_count"] == strict == 5
    # corpus_matrix counts the same thing over 25 grammars including the control G0, and for this
    # source the control adds a tree the strict orderings never build: 6, not 5.
    assert corpus_records((CUBIC,), workers=1)["records"][0]["distinct_ast_count"] == 6


def test_operator_word_catalan_count_is_the_catalan_number_of_the_operator_count():
    for source, operators, trees in ((MIXED, 3, 5), (LINEAR, 5, 42), (CUBIC, 9, 4862)):
        features = expression_features(source)
        assert features["operator_count"] == operators
        assert features["operator_word_catalan_count"] == trees
        assert trees == math.comb(2 * operators, operators) // (operators + 1)


def test_the_operator_word_catalan_count_is_blind_to_parentheses_as_its_name_says():
    """The count is over the OPERATOR WORD, never over the token sequence.

    The rational source carries the same operator word as the parenthesis-free linear one, so both
    report 42 - even though the rational's two parenthesis pairs forbid most of those 42 trees
    before any binding power is read. The measured AST count is what shows the gap.
    """
    linear = expression_features(LINEAR)
    rational = expression_features(RIGID_RATIONAL)
    assert linear["parenthesis_pair_count"] == 0
    assert rational["parenthesis_pair_count"] == 2
    assert rational["operator_word_catalan_count"] == linear["operator_word_catalan_count"] == 42
    assert linear["distinct_ast_count"] == 17
    assert rational["distinct_ast_count"] == 4
    assert FEATURE_BY_NAME["operator_word_catalan_count"].origin == "operator-word"
    assert "OPERATOR WORD" in FEATURE_BY_NAME["operator_word_catalan_count"].motivation


def test_reachability_ignores_parentheses_and_therefore_overcounts_the_rational():
    # For a parenthesis-free source the 0023 decision procedure over the operator word reproduces
    # the measured AST count exactly; with parentheses it cannot, because a parenthesis removes
    # trees before any binding power is consulted.
    linear = expression_features(LINEAR)
    assert linear["strict_reachable_tree_count"] == linear["distinct_ast_count"] == 17
    rational = expression_features(RIGID_RATIONAL)
    assert rational["strict_reachable_tree_count"] == 17
    assert rational["distinct_ast_count"] == 4


# ---------------------------------------------------------------------------------- association


def test_spearman_is_tie_corrected_and_undefined_on_a_constant():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)
    assert spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None
    assert spearman([1, 2, 3, 4], [7, 7, 7, 7]) is None
    assert average_ranks([5, 5, 9, 1]) == [2.5, 2.5, 4.0, 1.0]


def test_spearman_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        spearman([1, 2], [1, 2, 3])


def test_group_spread_reports_sizes_next_to_the_coefficient():
    spread = group_spread(["a", "a", "b", "b"], [0.0, 0.0, 1.0, 1.0])
    assert spread["group_sizes"] == {"a": 2, "b": 2}
    assert spread["smallest_group"] == 2
    assert spread["eta_squared"] == pytest.approx(1.0)
    assert spread["between_group_spread"] == pytest.approx(1.0)
    assert spread["largest_within_group_range"] == pytest.approx(0.0)


def test_group_spread_returns_no_eta_squared_when_there_is_nothing_to_explain():
    spread = group_spread(["a", "b"], [0.5, 0.5])
    assert spread["eta_squared"] is None
    assert spread["group_sizes"] == {"a": 1, "b": 1}


# --------------------------------------------------------------------------------------- table


def test_feature_table_joins_the_measured_targets_onto_the_features(small_table):
    assert small_table["expression_count"] == 5
    assert small_table["features"] == FEATURE_NAMES
    by_source = {row["source"]: row for row in small_table["rows"]}
    assert by_source[RIGID_RATIONAL]["sensitivity"] == 0.0
    assert by_source[RIGID_RATIONAL]["class_count"] == 1
    assert by_source[LINEAR]["class_count"] == 8
    assert by_source[LINEAR]["sensitivity"] == pytest.approx(7 / 23)
    assert [row["index"] for row in small_table["rows"]] == [0, 1, 2, 3, 4]


def test_feature_table_refuses_a_record_set_of_the_wrong_size():
    records = corpus_records(SMALL_CORPUS[:2], workers=1)["records"]
    with pytest.raises(ValueError):
        feature_table(SMALL_CORPUS, records=records)


def test_constant_features_and_value_histograms_agree(small_table):
    assert "distinct_variable_count" in constant_features(small_table)
    assert feature_values(small_table, "distinct_variable_count") == {1: 5}
    assert sum(feature_values(small_table, "support_size").values()) == 5


# ------------------------------------------------------------------------------------ multicore


def test_worker_count_is_derived_from_the_core_count_with_headroom(monkeypatch):
    monkeypatch.setattr("parseatlas.corpus_matrix.os.cpu_count", lambda: 8)
    assert resolve_feature_workers(1000, None) == 7
    assert resolve_feature_workers(1000, 0) == 7
    assert resolve_feature_workers(1000, 1) == 1
    assert resolve_feature_workers(1000, 3) == 3
    assert resolve_feature_workers(2, None) == 1  # below PARALLEL_MINIMUM_ITEMS


def test_sequential_and_parallel_feature_extraction_are_identical():
    corpus = generate_corpus()["expressions"][: PARALLEL_MINIMUM_ITEMS + 32]
    sequential = feature_rows(corpus, workers=1)
    parallel = feature_rows(corpus, workers=0)
    assert sequential["workers"] == 1
    assert parallel["workers"] > 1
    assert sequential["rows"] == parallel["rows"]


# ------------------------------------------------------------------------- partition and holdout


HAND_ROWS = (
    {"index": 0, "support_size": 3, "unit_multiplier_count": 0, "sensitivity": 0.4},
    {"index": 1, "support_size": 3, "unit_multiplier_count": 0, "sensitivity": 0.4},
    {"index": 2, "support_size": 3, "unit_multiplier_count": 1, "sensitivity": 0.2},
    {"index": 3, "support_size": 3, "unit_multiplier_count": 1, "sensitivity": 0.2},
    {"index": 4, "support_size": 4, "unit_multiplier_count": 0, "sensitivity": 0.8},
    {"index": 5, "support_size": 4, "unit_multiplier_count": 0, "sensitivity": 0.6},
)


def test_explained_partition_reports_every_cell_with_its_size_and_range():
    result = explained_partition({"rows": HAND_ROWS}, ("support_size", "unit_multiplier_count"))
    assert result["cell_count"] == 3
    assert result["collapsed_cells"] == 2
    assert result["collapsed_expressions"] == 4
    assert result["collapsed_fraction"] == pytest.approx(4 / 6)
    assert result["max_cell_range"] == pytest.approx(0.2)
    assert result["explains_sensitivity"] is False
    assert [cell["size"] for cell in result["cells"]] == [2, 2, 2]
    assert result["uncollapsed_cells"][0]["key"] == {"support_size": 4, "unit_multiplier_count": 0}


def test_a_feature_set_that_collapses_every_cell_is_reported_as_explaining():
    rows = tuple(row for row in HAND_ROWS if row["support_size"] == 3)
    result = explained_partition({"rows": rows}, ("unit_multiplier_count",))
    assert result["explains_sensitivity"] is True
    assert result["max_cell_range"] == 0.0
    assert result["collapsed_fraction"] == 1.0


def test_partition_and_holdout_reject_a_feature_outside_the_closed_set():
    with pytest.raises(KeyError):
        explained_partition({"rows": HAND_ROWS}, ("family",))
    with pytest.raises(KeyError):
        holdout_check({"rows": HAND_ROWS}, ("family",))


def test_holdout_splits_by_index_parity_and_is_deterministic():
    first = holdout_check({"rows": HAND_ROWS}, ("support_size", "unit_multiplier_count"))
    second = holdout_check({"rows": HAND_ROWS}, ("support_size", "unit_multiplier_count"))
    assert first == second
    assert first["half_sizes"] == {"even": 3, "odd": 3}
    assert first["folds"]["even_fit"]["evaluate_size"] == 3


def test_holdout_counts_cells_it_never_saw_in_the_fit_half():
    rows = (
        {"index": 0, "support_size": 3, "sensitivity": 0.1},
        {"index": 1, "support_size": 4, "sensitivity": 0.9},
    )
    result = holdout_check({"rows": rows}, ("support_size",))
    assert result["folds"]["even_fit"]["unseen_cells"] == 1
    assert result["folds"]["odd_fit"]["unseen_cells"] == 1
    assert result["total_unseen_cells"] == 2


def test_leave_one_group_out_withholds_a_whole_group():
    rows = (
        {"index": 0, "operator_profile": "A", "parenthesis_pair_count": 0, "unit_multiplier_count": 0, "sensitivity": 0.1},
        {"index": 1, "operator_profile": "A", "parenthesis_pair_count": 0, "unit_multiplier_count": 1, "sensitivity": 0.2},
        {"index": 2, "operator_profile": "B", "parenthesis_pair_count": 0, "unit_multiplier_count": 0, "sensitivity": 0.9},
    )
    result = leave_one_group_out_check({"rows": rows}, ("operator_profile", "unit_multiplier_count"))
    assert result["group_count"] == 2
    assert result["total_unseen_cells"] == 3
    assert result == leave_one_group_out_check({"rows": rows}, ("operator_profile", "unit_multiplier_count"))


# ------------------------------------------------------- the published corpus: ground truth


def test_the_corpus_ground_truth_of_0024_re_derives(corpus_table):
    truth = ground_truth(corpus_table)
    assert truth["expression_count"] == 3125
    assert truth["sensitivity_distribution"] == {
        0.0: 25,
        0.043478: 200,
        0.086957: 275,
        0.130435: 1500,
        0.173913: 625,
        0.217391: 100,
        0.304348: 400,
    }
    assert truth["class_count_distribution"] == {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}
    assert truth["rigid"] == 25
    assert truth["sensitive"] == 3100
    assert truth["rigid_families"] == {"rational": 25}
    assert truth["mean_sensitivity"] == pytest.approx(0.153739, abs=1e-6)
    assert truth["max_sensitivity"] == pytest.approx(7 / 23)
    assert truth["support_size_counts"] == {3: 1875, 4: 1250}


def test_two_features_are_constant_on_the_published_corpus(corpus_table):
    assert constant_features(corpus_table) == ("distinct_variable_count", "zero_literal_count")


# ------------------------------------------------------- the published corpus: the support trap


def test_support_size_alone_is_a_weak_predictor_of_sensitivity(corpus_table, corpus_strength):
    """The trap feature, measured. |O(E)| forces agreement but barely predicts S(E) here."""
    overall = corpus_strength["overall"]["support_size"]
    assert overall["group_sizes"] == {3: 1875, 4: 1250}
    assert overall["spearman"] == pytest.approx(0.111061, abs=1e-6)
    assert overall["eta_squared"] == pytest.approx(0.067610, abs=1e-6)
    holdout = holdout_check(corpus_table, ("support_size",))
    assert holdout["mean_absolute_error"] == pytest.approx(0.049530, abs=1e-6)
    assert holdout["baseline_mean_absolute_error"] == pytest.approx(0.050699, abs=1e-6)


def test_within_a_fixed_support_size_the_unit_multiplier_count_retains_its_association(corpus_strength):
    """THE TRAP TEST, positive half: a non-parser feature that survives conditioning on |O(E)|."""
    strength = corpus_strength
    assert strength["stratum_sizes"] == {(3,): 1875, (4,): 1250}
    three = strength["within_strata"][(3,)]["features"]["unit_multiplier_count"]
    four = strength["within_strata"][(4,)]["features"]["unit_multiplier_count"]
    assert three["group_sizes"] == {0: 1220, 1: 565, 2: 85, 3: 5}
    assert four["group_sizes"] == {0: 800, 1: 400, 2: 50}
    assert three["spearman"] == pytest.approx(-0.051271, abs=1e-6)
    assert four["spearman"] == pytest.approx(-0.375870, abs=1e-6)
    assert three["eta_squared"] == pytest.approx(0.035931, abs=1e-6)
    assert four["eta_squared"] == pytest.approx(0.113420, abs=1e-6)
    summary = strength["within_strata_summary"]["unit_multiplier_count"]
    assert summary["strata_with_variation"] == 2
    assert summary["constant_in_every_stratum"] is False
    assert summary["weighted_spearman"] == pytest.approx(-0.181110, abs=1e-6)
    assert summary["weighted_eta_squared"] == pytest.approx(0.066926, abs=1e-6)


def test_the_reachability_count_explains_nothing_once_support_size_is_fixed(corpus_strength):
    """THE TRAP TEST, negative half: a feature whose whole association IS the support size."""
    strength = corpus_strength
    overall = strength["overall"]["strict_reachable_tree_count"]
    support = strength["overall"]["support_size"]
    assert overall["group_sizes"] == {17: 1250, 5: 1875}
    assert overall["spearman"] == pytest.approx(support["spearman"])
    assert overall["eta_squared"] == pytest.approx(support["eta_squared"])
    summary = strength["within_strata_summary"]["strict_reachable_tree_count"]
    assert summary["constant_in_every_stratum"] is True
    assert summary["weighted_eta_squared"] is None


def test_the_shape_features_are_constant_inside_support_size_four(corpus_strength):
    """Linear and rational share every operator-multiset feature; only the parentheses see them."""
    strength = corpus_strength
    four = strength["within_strata"][(4,)]["features"]
    for name in ("operator_count", "leaf_count", "operator_profile", "repetition_pattern", "operator_word_catalan_count"):
        assert four[name]["constant"] is True, name
    assert four["parenthesis_pair_count"]["eta_squared"] == pytest.approx(0.623269, abs=1e-6)
    assert four["distinct_ast_count"]["eta_squared"] == pytest.approx(0.623269, abs=1e-6)
    three = strength["within_strata"][(3,)]["features"]
    assert three["operator_count"]["spearman"] == pytest.approx(0.786214, abs=1e-6)
    assert three["parenthesis_pair_count"]["constant"] is True


def test_within_support_report_separates_the_parser_features_from_the_rest(corpus_table):
    report = within_support_report(corpus_table)
    assert report["stratum_sizes"] == {(3,): 1875, (4,): 1250}
    assert set(report["dead_features"]) == {
        "support_size",
        "distinct_variable_count",
        "division_operator_count",
        "has_division",
        "zero_literal_count",
        "strict_reachable_tree_count",
    }
    assert "unit_multiplier_count" in report["retained_independent_features"]
    assert set(report["retained_parser_restating_features"]) == {
        "parenthesis_pair_count",
        "distinct_ast_count",
    }


# ---------------------------------------------- the published corpus: the predictor and its limit


def test_the_published_feature_set_collapses_eighty_seven_percent_of_the_corpus(corpus_table):
    result = explained_partition(corpus_table, CHOSEN)
    assert result["cell_count"] == 18
    assert result["collapsed_expressions"] == 2725
    assert result["collapsed_fraction"] == pytest.approx(0.872)
    assert result["uncollapsed_expressions"] == 400
    assert result["max_cell_range"] == pytest.approx(2 / 23)
    assert result["baseline_range"] == pytest.approx(7 / 23)
    assert result["size_weighted_mean_range"] == pytest.approx(0.007791, abs=1e-6)
    assert result["explains_sensitivity"] is False
    assert [cell["size"] for cell in result["uncollapsed_cells"]] == [200, 160, 40]


def test_the_collapse_survives_conditioning_on_support_size(corpus_table):
    for support, expected_collapsed, expected_fraction in ((3, 1675, 0.893333), (4, 1050, 0.840000)):
        rows = tuple(row for row in corpus_table["rows"] if row["support_size"] == support)
        result = explained_partition({"rows": rows}, CHOSEN)
        assert result["collapsed_expressions"] == expected_collapsed
        assert result["collapsed_fraction"] == pytest.approx(expected_fraction, abs=1e-6)


def test_the_predictor_holds_out_on_the_parity_split(corpus_table):
    result = holdout_check(corpus_table, CHOSEN)
    assert result["half_sizes"] == {"even": 1563, "odd": 1562}
    assert result["mean_absolute_error"] == pytest.approx(0.003896, abs=1e-6)
    assert result["root_mean_square_error"] == pytest.approx(0.011536, abs=1e-6)
    assert result["baseline_mean_absolute_error"] == pytest.approx(0.050699, abs=1e-6)
    assert result["exact_fraction"] == pytest.approx(0.872, abs=1e-4)
    assert result["total_unseen_cells"] == 0
    assert result["folds"]["even_fit"]["cells_fitted"] == 18
    assert result["folds"]["odd_fit"]["cells_fitted"] == 18
    assert result == holdout_check(corpus_table, CHOSEN)


def test_the_predictor_transfers_to_no_unseen_token_shape(corpus_table):
    """The published limit: every cell names its shape, so a new shape gets the fit mean and nothing else."""
    result = leave_one_group_out_check(corpus_table, CHOSEN)
    assert result["group_count"] == 5
    assert result["total_unseen_cells"] == 3125
    assert result["exact_fraction"] == 0.0
    assert result["mean_absolute_error"] == pytest.approx(0.060842, abs=1e-6)
    assert result["mean_absolute_error"] == pytest.approx(result["baseline_mean_absolute_error"])
    assert result["worst_fold_mean_absolute_error"] == pytest.approx(0.128557, abs=1e-6)


# --------------------------------------------- the published corpus: the exhaustive subset search


def test_the_exhaustive_subset_search_reproduces(corpus_table):
    """Report section 8, pinned: the published optimum is a searched minimum, not a pick.

    This runs the whole published search - every subset of size 1..4 over the 19 non-constant
    features, scored by the same deterministic parity hold-out - because the claim it defends is
    "nothing in the closed set does better", and only an exhaustive run can defend that. It is the
    slowest test in this file - the 5035 hold-out fits over 3125 rows measured 88.7 s in a
    standalone run on this 16-core host - and it is worth that: the published figures of report
    section 8 cannot drift silently underneath it.
    """
    usable = tuple(name for name in FEATURE_NAMES if name not in constant_features(corpus_table))
    assert len(usable) == 19
    scored = {
        combo: holdout_check(corpus_table, combo)["mean_absolute_error"]
        for size in (1, 2, 3, 4)
        for combo in itertools.combinations(usable, size)
    }
    assert len(scored) == 5035

    best = min(scored.values())
    assert best == pytest.approx(0.003896, abs=1e-6)
    tied = tuple(sorted(combo for combo, error in scored.items() if error == best))
    assert len(tied) == 12
    for combo in tied:
        assert len(combo) == 4
        assert {"unit_multiplier_count", "unit_divisor_count"} <= set(combo)
        assert set(combo) & set(PARSER_RESTATING_FEATURES)
        partition = explained_partition(corpus_table, combo)
        assert partition["cell_count"] == 18
        assert partition["collapsed_fraction"] == pytest.approx(0.872)
    # the set the report publishes is one of the twelve, up to the order of its names
    assert frozenset(CHOSEN) in {frozenset(combo) for combo in tied}
    assert holdout_check(corpus_table, CHOSEN)["mean_absolute_error"] == best

    # the published best of each size, and the published representative that attains it
    for size, error, representative in (
        (1, 0.035284, ("distinct_ast_count",)),
        (2, 0.025294, ("unit_multiplier_count", "distinct_ast_count")),
        (3, 0.012634, ("operator_count", "unit_multiplier_count", "distinct_ast_count")),
        (4, 0.003896, ("operator_count", "unit_multiplier_count", "unit_divisor_count", "distinct_ast_count")),
    ):
        size_best = min(error for combo, error in scored.items() if len(combo) == size)
        assert size_best == pytest.approx(error, abs=1e-6), size
        assert scored[representative] == size_best, size

    # the two figures the interpretation leans on: dropping every parser-restating feature costs
    # an order of magnitude, and support_size itself is not part of any optimum
    parser_free = {combo: error for combo, error in scored.items() if not set(combo) & set(PARSER_RESTATING_FEATURES)}
    assert min(parser_free.values()) == pytest.approx(0.034206, abs=1e-6)
    assert parser_free[
        ("variable_leaf_count", "unit_literal_count", "unit_multiplier_count", "unit_divisor_count")
    ] == min(parser_free.values())
    with_support = {combo: error for combo, error in scored.items() if "support_size" in combo}
    assert min(with_support.values()) == pytest.approx(0.012634, abs=1e-6)
    assert min(with_support.values()) > best
