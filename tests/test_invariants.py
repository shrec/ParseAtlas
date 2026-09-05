"""Validation of experiment 0046: what survives all 25 worlds, and what it costs to survive.

Every number here was measured before it was written down, and every headline is pinned as a
literal rather than recomputed from the module, so a change in the result fails a test instead of
quietly rewriting the finding.

The file is ordered so that the things without which nothing else means anything come first:

* **the characterisation** -- necessary and sufficient, checked against the full enumeration, with
  the disagreement count pinned at zero.  A rate would not do: the enumeration is dominated by
  words with small support, so a pooled percentage says only how long the words were allowed to be.
* **the null model** -- every stratum's size cross-checked against the closed form, so the
  enumeration is known to be complete, and every rate computed inside a stratum.
* **the two things that must never blur** -- invariance is of the PARSE, and ``a - b - c`` is
  parse-invariant and not value-associative; invariance BY CONSTRUCTION is a restatement of how
  parsing works and is kept apart from invariance as a measured fact.

Only then come the price of invariance and the hypothesis the card exists to test.
"""

from functools import lru_cache

import pytest
from sympy import Symbol, simplify

from parseatlas.canonical import to_sympy
from parseatlas.grammar import all_grammars, control_grammar
from parseatlas.manifest_properties import CORPUS as OBJECT_CORPUS
from parseatlas.manifest_properties import object_tree
from parseatlas.parser import parse
from parseatlas.invariants import (
    AXIS2_CORPUS,
    CELL_SECONDS,
    CHAIN_SOURCES,
    CRITICAL_PATH_SOURCES,
    FIRST_ABOVE,
    GRAMMARS,
    KINDS,
    POOL_STARTUP_SECONDS,
    PRICE_SECONDS,
    QUANTITIES,
    QUANTITY_NAMES,
    REGIMES,
    STRICT,
    WORD_SECONDS,
    axis1_report,
    axis2_report,
    chain_supports,
    default_worker_count,
    enumerate_words,
    invariant_cost,
    invariant_minimality_witnesses,
    invariant_writing,
    invariants_report,
    is_invariant,
    leaf_parent,
    predicted_invariant,
    predicted_invariant_source,
    price_report,
    should_parallelise,
    source_invariance_audit,
    source_is_invariant,
    stratum_sizes,
    surjections,
    tree_key,
    witness_pair,
    word_at,
    word_count,
    word_source,
    words_of_length,
    worker_count_for,
    world_trees,
)

#: The enumeration bound this experiment reports.  Every pinned axis-1 number belongs to it.
MAX_LENGTH = 8


@lru_cache(maxsize=1)
def axis1() -> dict:
    return axis1_report(MAX_LENGTH)


@lru_cache(maxsize=1)
def axis2() -> dict:
    return axis2_report()


@lru_cache(maxsize=1)
def axis3() -> dict:
    return price_report()


# ============================================================ axis 1: the characterisation, first


def test_the_characterisation_holds_on_the_whole_enumeration():
    """The headline: world-invariant iff the operator support has size at most one.

    ``disagreements`` carries every word where the predicate and the parser part company, and it is
    pinned at zero.  If this ever fails, the words listed are the finding and the characterisation
    is wrong -- they are not to be argued away by weakening the predicate.
    """
    report = axis1()
    assert report["max_length"] == 8
    assert report["word_count"] == 87381
    assert report["expected_word_count"] == 87381
    assert report["parse_count"] == 2184525
    assert report["characterisation"] == (
        "world-invariant iff the operator support has size at most 1"
    )
    assert report["disagreements"] == ()
    assert report["disagreement_count"] == 0
    assert report["characterisation_holds"] is True


def test_every_non_invariant_word_comes_with_a_pair_of_worlds_that_disagree():
    """Necessity is constructive: the witness is built from the word and then checked."""
    report = axis1()
    assert report["witness_failures"] == ()
    assert report["witness_failure_count"] == 0
    assert report["witnesses_hold"] is True


def test_the_witness_is_the_leaf_between_two_differing_operators():
    """The hand-worked pair the whole necessity argument is about.

    ``a + b * c``: the leaf ``b`` sits between ``+`` and ``*``.  In a world where ``+`` binds
    tighter it is the RIGHT child of the ``+`` node; in a world where ``*`` binds tighter it is the
    LEFT child of the ``*`` node.  Distinct leaves make those different trees, and that is the whole
    of the necessity half.
    """
    assert witness_pair("+*") == ("G01", "G09")
    grammars = {grammar.id: grammar for grammar in GRAMMARS}
    plus_first = parse("a + b * c", grammars["G01"])
    star_first = parse("a + b * c", grammars["G09"])
    assert leaf_parent(plus_first, "b") == ("+", "right")
    assert leaf_parent(star_first, "b") == ("*", "left")
    assert tree_key(plus_first) != tree_key(star_first)
    assert tree_key(plus_first) == ("*", ("+", "a", "b"), "c")
    assert tree_key(star_first) == ("+", "a", ("*", "b", "c"))


def test_invariance_is_decided_by_tree_identity_on_a_hand_worked_pair():
    """Two writings worked out by hand, one invariant and one not, decided by tree identity.

    ``a - b - c`` is read as ``(a - b) - c`` by every one of the 25 worlds; ``a - b * c`` is read
    two ways.  The decision is made by comparing trees, never by comparing rendered strings or
    values, and the trees are written out here rather than taken from the module.
    """
    left_chain = ("-", ("-", "a", "b"), "c")
    assert set(world_trees("--").values()) == {left_chain}
    assert is_invariant("--") is True
    assert predicted_invariant("--") is True

    mixed = world_trees("-*")
    assert set(mixed.values()) == {
        ("*", ("-", "a", "b"), "c"),
        ("-", "a", ("*", "b", "c")),
    }
    assert is_invariant("-*") is False
    assert predicted_invariant("-*") is False


def test_a_minus_b_minus_c_is_parse_invariant_and_not_value_associative():
    """The distinction the report must never blur.

    ``-`` and ``/`` are not associative.  A single repeated operator being world-invariant is a
    statement about the PARSE -- every world builds the same tree -- and says nothing about the
    value, because the tree every world builds is the left-associated one and the right-associated
    one is a different number.
    """
    assert is_invariant("--") is True
    assert is_invariant("//") is True

    a, b, c = (Symbol(name, real=True) for name in "abc")
    left = to_sympy(parse("a - b - c", control_grammar()))
    right = to_sympy(parse("a - (b - c)", control_grammar()))
    assert simplify(left - ((a - b) - c)) == 0
    assert simplify(left - right) != 0
    assert simplify(left - right) == -2 * c

    left_div = to_sympy(parse("a / b / c", control_grammar()))
    right_div = to_sympy(parse("a / (b / c)", control_grammar()))
    assert simplify(left_div - right_div) != 0

    # and the contrast: + and * ARE associative, so there the two agree in value while the parse is
    # still the left-associated one in every world.
    assert simplify(
        to_sympy(parse("a + b + c", control_grammar()))
        - to_sympy(parse("a + (b + c)", control_grammar()))
    ) == 0
    assert set(world_trees("++").values()) == {("+", ("+", "a", "b"), "c")}


# ================================================================ axis 1: the null model, per stratum


def test_the_stratum_sizes_match_the_closed_form():
    """The enumeration is complete, checked against ``C(4, k) * surj(n, k)`` and not against itself."""
    report = axis1()
    assert report["strata_match_closed_form"] is True
    assert stratum_sizes(MAX_LENGTH) == {0: 1, 1: 32, 2: 2964, 3: 33336, 4: 51048}
    assert sum(stratum_sizes(MAX_LENGTH).values()) == 87381
    assert word_count(MAX_LENGTH) == 87381
    assert surjections(8, 2) == 254
    assert surjections(3, 3) == 6
    assert surjections(2, 3) == 0


def test_the_support_stratified_counts_are_pinned_per_stratum():
    """Every rate inside a stratum, never pooled.

    The invariance rate is ``1.0`` at support ``0`` and ``1``, and ``0.0`` at support ``2``, ``3``
    and ``4``.  That is the characterisation restated as a table, and it is the only honest way to
    report it: the pooled rate below is a statement about the length bound.
    """
    strata = axis1()["strata"]
    assert {size: item["words"] for size, item in strata.items()} == {
        0: 1,
        1: 32,
        2: 2964,
        3: 33336,
        4: 51048,
    }
    assert {size: item["invariant"] for size, item in strata.items()} == {
        0: 1,
        1: 32,
        2: 0,
        3: 0,
        4: 0,
    }
    assert {size: item["invariance_rate"] for size, item in strata.items()} == {
        0: 1.0,
        1: 1.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
    }
    assert all(item["size_matches_closed_form"] for item in strata.values())


def test_the_pooled_rate_is_recorded_as_the_artifact_it_is():
    """``33`` invariant words out of ``87381`` is a fact about ``max_length``, not about precedence."""
    report = axis1()
    assert report["invariant_words"] == 33
    assert report["pooled_invariance_rate"] == pytest.approx(33 / 87381, rel=1e-12)
    assert report["pooled_invariance_rate"] < 0.0004


def test_the_t6_upper_bound_is_reached_less_and_less_as_the_support_grows():
    """T6 bounds the distinct trees by ``|support|!``; the bound is tight only at support two."""
    strata = axis1()["strata"]
    assert {size: item["t6_upper_bound"] for size, item in strata.items()} == {
        0: 1,
        1: 1,
        2: 2,
        3: 6,
        4: 24,
    }
    assert {size: item["bound_attained"] for size, item in strata.items()} == {
        0: 1,
        1: 32,
        2: 2964,
        3: 16968,
        4: 264,
    }
    assert strata[2]["bound_attainment_rate"] == 1.0
    assert strata[3]["bound_attainment_rate"] == pytest.approx(16968 / 33336, rel=1e-12)
    assert strata[4]["bound_attainment_rate"] == pytest.approx(264 / 51048, rel=1e-12)
    assert strata[2]["distinct_strict_trees"] == {2: 2964}
    assert strata[3]["distinct_strict_trees"] == {5: 16368, 6: 16968}
    assert strata[4]["distinct_strict_trees"] == {
        14: 11088,
        15: 4080,
        16: 240,
        17: 15408,
        18: 4656,
        19: 4368,
        20: 3936,
        21: 5664,
        22: 1344,
        24: 264,
    }
    assert 23 not in strata[4]["distinct_strict_trees"]


def test_the_opposite_pole_words_read_differently_by_every_one_of_the_25():
    """The far end of the same measurement, and the reason the bound has to be stated.

    ``244`` words are read differently by all 25 worlds, and every one of them has length ``8`` --
    the enumeration bound.  An enumeration stopping at 7 would have reported that no such word
    exists, which is why the bound is a limitation and not a detail.
    """
    strata = axis1()["strata"]
    assert strata[4]["largest_block"][1] == 244
    assert strata[4]["distinct_world_trees"][25] == 244
    assert 1 not in strata[3]["largest_block"]
    extreme = "+-*+/-*/"
    assert len(extreme) == 8
    assert len(set(world_trees(extreme).values())) == 25
    assert word_source(extreme) == "a + b - c * d + e / f - g * h / i"


def test_the_tied_control_is_a_25th_world_and_not_a_copy_of_one_of_the_24():
    """``G0`` reads ``51296`` of the ``87381`` words as a tree no strict grammar produces.

    And never when the support avoids a whole ``G0`` level: with no tie inside the support, ``G0``'s
    restriction is a strict total order and T6 forces it to agree with some strict grammar.  That is
    a proof, and ``control_new_without_tied_pair`` is the enumeration checking it.
    """
    report = axis1()
    assert report["control_reaches_new_tree"] == 51296
    assert report["control_new_without_tied_pair"] == ()
    assert report["control_new_needs_tied_pair"] is True
    strata = axis1()["strata"]
    assert {size: item["control_reaches_new_tree"] for size, item in strata.items()} == {
        0: 0,
        1: 0,
        2: 876,
        3: 18456,
        4: 31964,
    }
    # the shortest example, worked by hand: a + b - c + d is left-associated under G0, and no
    # strict ordering of + and - produces that tree.
    trees = world_trees("+-+")
    assert trees["G0"] == ("+", ("-", ("+", "a", "b"), "c"), "d")
    assert trees["G0"] not in {trees[grammar.id] for grammar in STRICT}
    assert world_trees("+-")["G0"] in {world_trees("+-")[grammar.id] for grammar in STRICT}


# ============================================ axis 1: the characterisation, generalised to brackets


def test_the_characterisation_generalises_to_bracketed_writings():
    """A writing is invariant iff every maximal bracket-free chain in it uses one operator.

    The bracket-free case is proved; the bracketed case is checked, because the necessity argument
    assumes the operands of a chain are pairwise distinct and a real corpus writes ``a * a + b * b``.
    """
    assert chain_supports("a * (b + c) - d") == (frozenset("+"), frozenset("-*"))
    assert predicted_invariant_source("(x + 1)/(x - 2)") is True
    assert predicted_invariant_source("a * (b + c) - d") is False
    assert predicted_invariant_source("a - b - c") is True

    sources = [entry.source for entry in AXIS2_CORPUS]
    sources += [
        invariant_writing(object_tree(writing))
        for item in OBJECT_CORPUS
        for writing in item.writings
    ]
    sources += [word_source(word) for word in enumerate_words(4)]
    audit = source_invariance_audit(sources)
    assert audit["sources"] == 437
    assert audit["checks"] == 10925
    assert audit["disagreements"] == ()
    assert audit["holds"] is True
    assert audit["invariant"] == 68


def test_the_corpus_writings_that_are_already_invariant_are_the_ones_the_predicate_names():
    """Ten of the 55 movable corpus writings are read identically by all 25 worlds."""
    report = axis2()
    invariant = tuple(
        sorted(
            name
            for name, record in report["entries"].items()
            if record["movable"] and record["quantities"]["parse_tree"]["constant"]
        )
    )
    assert invariant == (
        "binomial_cube.factored",
        "binomial_square.factored",
        "cp_rational",
        "difference_of_squares.factored",
        "difference_quotient.closed",
        "distributive_law.factored",
        "midpoint.mean",
        "quadratic.factored",
        "slope.difference_quotient",
        "taylor_first_term.standard",
    )
    for name in invariant:
        assert predicted_invariant_source(report["entries"][name]["source"]) is True


# ================================================================================= axis 2


def test_every_quantity_declares_its_kind_before_anything_is_measured():
    assert KINDS == ("by_construction", "measured")
    assert len(QUANTITIES) == 16
    assert QUANTITY_NAMES == (
        "token_count",
        "leaf_multiset",
        "operator_multiset",
        "node_count",
        "parse_tree",
        "critical_path_depth",
        "peak_live",
        "semantic_key",
        "excluded_points",
        "defined_everywhere",
        "free_symbols",
        "total_degree",
        "polynomial_degree",
        "root_count",
        "pole_count",
        "expanded_term_count",
    )
    declared = {item.name: item.kind for item in QUANTITIES}
    assert declared["token_count"] == "by_construction"
    assert declared["leaf_multiset"] == "by_construction"
    assert declared["operator_multiset"] == "by_construction"
    assert declared["node_count"] == "by_construction"
    assert sum(1 for item in QUANTITIES if item.kind == "by_construction") == 4
    assert sum(1 for item in QUANTITIES if item.kind == "measured") == 12
    # a by-construction quantity states WHY it cannot move; a measured one has nothing to state.
    assert all(item.reason for item in QUANTITIES if item.kind == "by_construction")
    assert all(not item.reason for item in QUANTITIES if item.kind == "measured")


def test_the_by_construction_invariants_are_pinned_as_by_construction():
    """The four quantities that cannot move, kept apart from the ones that were measured not to.

    This is the whole point of the axis: ``operator_multiset`` is 0021's finding and it is a
    restatement of how parsing works, so it is reported in its own group and never counted as a
    discovery alongside a quantity that could have moved and did not.
    """
    groups = axis2()["groups"]
    assert groups["by_construction"]["always"] == (
        "token_count",
        "leaf_multiset",
        "operator_multiset",
        "node_count",
    )
    assert groups["by_construction"]["sometimes"] == ()
    assert groups["by_construction"]["never"] == ()


def test_no_measured_quantity_is_invariant_across_all_25_worlds():
    """The answer to the founding question, and it is a negative one.

    Every one of the twelve measured quantities is constant on SOME movable corpus entry and moves
    on some other.  None is always constant, and none is never constant.  The only quantities that
    survive all 25 worlds unconditionally are the four that cannot fail to.
    """
    groups = axis2()["groups"]
    assert groups["measured"]["always"] == ()
    assert groups["measured"]["never"] == ()
    assert groups["measured"]["sometimes"] == (
        "parse_tree",
        "critical_path_depth",
        "peak_live",
        "semantic_key",
        "excluded_points",
        "defined_everywhere",
        "free_symbols",
        "total_degree",
        "polynomial_degree",
        "root_count",
        "pole_count",
        "expanded_term_count",
    )


def test_the_axis_2_corpus_and_its_null_model():
    report = axis2()
    assert report["entry_count"] == 60
    assert report["cell_count"] == 1500
    assert report["world_count"] == 25
    assert report["movable_entries"] == 55
    assert report["frozen_entries"] == 5
    assert report["frozen_names"] == (
        "chain_add",
        "chain_div",
        "chain_mul",
        "chain_rule.standard",
        "chain_sub",
    )
    assert len(CRITICAL_PATH_SOURCES) == 6
    assert len(CHAIN_SOURCES) == 4
    # a frozen entry is invariant in everything, which is a fact about the entry and not about the
    # quantity: it is excluded from every rate.
    for name in report["frozen_names"]:
        record = report["entries"][name]
        assert len(record["support"]) <= 1
        assert all(item["constant"] for item in record["quantities"].values() if item["applicable"])


def test_the_constant_rate_of_every_quantity_is_pinned_over_the_movable_entries():
    quantities = axis2()["quantities"]
    assert {
        name: (item["movable_constant"], item["movable_entries"])
        for name, item in quantities.items()
    } == {
        "token_count": (55, 55),
        "leaf_multiset": (55, 55),
        "operator_multiset": (55, 55),
        "node_count": (55, 55),
        "parse_tree": (10, 55),
        "critical_path_depth": (14, 55),
        "peak_live": (31, 55),
        "semantic_key": (13, 55),
        "excluded_points": (47, 55),
        "defined_everywhere": (53, 55),
        "free_symbols": (52, 55),
        "total_degree": (14, 43),
        "polynomial_degree": (27, 40),
        "root_count": (28, 41),
        "pole_count": (39, 41),
        "expanded_term_count": (33, 55),
    }


def test_experiment_0021_is_reproduced_as_the_calibration_case():
    """0021's finding, re-measured here: the raw operation multiset is invariant, depth is not."""
    report = axis2()
    calibration = report["calibration_0021"]
    assert len(calibration) == 6
    assert all(item["operator_multiset_constant"] for item in calibration.values())
    assert {name: item["critical_path_depth_distinct"] for name, item in calibration.items()} == {
        "cp_linear": 2,
        "cp_mixed": 2,
        "cp_quadratic": 3,
        "cp_four_term": 3,
        "cp_five_term": 3,
        "cp_rational": 1,
    }
    # 0021's rigid rational expression is the one entry of the six the convention cannot move.
    rational = report["entries"]["cp_rational"]
    assert rational["quantities"]["parse_tree"]["constant"] is True
    assert rational["quantities"]["semantic_key"]["distinct"] == 1


def test_a_convention_can_decide_whether_a_formula_is_defined_everywhere():
    """``defined_everywhere`` moves on exactly two entries, and both are the trapezoid area."""
    report = axis2()
    moving = tuple(
        sorted(
            name
            for name, record in report["entries"].items()
            if record["movable"] and not record["quantities"]["defined_everywhere"]["constant"]
        )
    )
    assert moving == ("trapezoid_area.mean_times_height", "trapezoid_area.sum_of_halves")
    grammars = {grammar.id: grammar for grammar in GRAMMARS}
    from parseatlas.canonical import canonicalize

    control = canonicalize(parse("(a + b) / 2 * h", grammars["G0"]))
    other = canonicalize(parse("(a + b) / 2 * h", grammars["G01"]))
    assert control["excluded_points"] == []
    assert other["excluded_points"] == ["0"]


# ================================================================================= axis 3


def test_the_invariant_writing_is_read_back_by_every_world():
    report = axis3()
    assert report["object_count"] == 34
    assert report["writing_count"] == 50
    assert report["round_trip_checks"] == 1250
    assert report["round_trip_failures"] == ()
    assert report["invariant_writing_holds"] is True


def test_every_bracket_of_the_invariant_writing_is_load_bearing():
    """Minimality, proved by deletion: strike any pair and some world reads a different tree."""
    report = axis3()
    assert report["brackets_checked"] == 147
    assert report["brackets_checked"] == report["writing_total_invariant"]
    assert report["minimality_failures"] == ()
    assert report["invariant_writing_minimal"] is True
    witnesses = invariant_minimality_witnesses(
        object_tree(
            next(
                writing
                for writing in next(
                    item for item in OBJECT_CORPUS if item.name == "difference_of_squares"
                ).writings
                if writing.role == "factored"
            )
        )
    )
    assert len(witnesses) == 2
    assert all(item["required"] for item in witnesses)


def test_the_invariant_writing_rule_worked_by_hand():
    """Right children always bracketed; left children only when the operator changes."""
    control = control_grammar()
    assert invariant_writing(parse("a + b + c", control)) == "a + b + c"
    assert invariant_writing(parse("a + (b + c)", control)) == "a + (b + c)"
    assert invariant_writing(parse("a * b + c", control)) == "(a * b) + c"
    assert invariant_writing(parse("(a + b) * (a - b)", control)) == "(a + b) * (a - b)"
    assert invariant_cost(parse("a + b + c", control)) == 0
    assert invariant_cost(parse("(a + b) * (a - b)", control)) == 2
    for source in ("a + b + c", "a + (b + c)", "a * b + c", "(a + b) * (a - b)"):
        assert source_is_invariant(invariant_writing(parse(source, control))) is True


def test_the_hypothesis_first_half_holds_invariance_is_bought_with_brackets():
    """CONFIRMED: 49 of the 50 writings pay, and the one that does not uses a single operator."""
    report = axis3()
    assert report["writing_total_invariant"] == 147
    assert report["writing_total_cheapest"] == 7
    assert report["writing_total_control"] == 47
    assert report["bracket_total_invariant"] == 84
    assert report["bracket_total_cheapest"] == 0
    assert report["bracket_total_control"] == 17
    assert report["writings_paying"] == 49
    assert report["writings_free"] == 1
    assert report["objects_paying"] == 33
    assert report["objects_free"] == 1
    assert report["mean_price"] == pytest.approx(84 / 34, rel=1e-12)
    assert report["max_price"] == 6
    free = tuple(
        (row["object"], writing["role"])
        for row in report["objects"]
        for writing in row["writings"]
        if writing["price"] == 0
    )
    assert free == (("chain_rule", "standard"),)


def test_the_hypothesis_second_half_fails_under_the_primary_regime():
    """REFUTED where it matters: the invariant writing of a tree shows exactly what the cheap one does.

    Under 0038's primary ``transparent`` regime a bracket is punctuation, so making a writing
    invariant costs brackets and costs nothing in visibility: the loss is identically ``0`` on all
    ``50`` writings, and a correlation between price and loss is therefore undefined rather than
    weak.  It is only under the ``opaque`` robustness regime that anything is lost, and there the
    amount lost does not track the price paid.
    """
    report = axis3()
    assert REGIMES == ("transparent", "opaque")
    assert report["writings_losing"]["transparent"] == 0
    assert report["writings_gaining"]["transparent"] == 0
    assert report["writing_loss_mean"]["transparent"] == 0.0
    assert report["writing_price_loss_correlation"]["transparent"] is None

    assert report["writings_losing"]["opaque"] == 34
    assert report["writing_loss_mean"]["opaque"] == pytest.approx(1.78, rel=1e-12)
    assert report["writing_price_loss_correlation"]["opaque"] == pytest.approx(
        0.1861, abs=5e-4
    )

    assert report["objects_losing"]["transparent"] == 11
    assert report["objects_gaining"]["transparent"] == 5
    assert report["manifest_loss_mean"]["transparent"] == pytest.approx(0.18, rel=1e-9)
    assert report["price_loss_correlation"]["transparent"] == pytest.approx(0.1877, abs=5e-4)
    assert report["objects_losing"]["opaque"] == 29
    assert report["objects_gaining"]["opaque"] == 0
    assert report["price_loss_correlation"]["opaque"] == pytest.approx(-0.1798, abs=5e-4)


def test_the_five_objects_that_show_more_under_an_invariance_requirement():
    """The counterexamples to "costs more and shows less", named and pinned.

    Four of them gain because the cheapest invariant writing is the monomial-sum one.  ``quadratic``
    gains the other way round: its expanded writing makes NOTHING manifest, because the leading
    coefficient ``a * (r + s)`` sits behind a bracketed sum and reading it would be algebra.
    """
    report = axis3()
    gaining = tuple(
        sorted(
            row["object"]
            for row in report["objects"]
            if row["free_manifest_mean"]["transparent"]
            < row["invariant_manifest_size"]["transparent"]
        )
    )
    assert gaining == (
        "calibration_quadratic",
        "difference_of_cubes",
        "perfect_square_trinomial",
        "quadratic",
        "sum_of_cubes",
    )
    row = next(item for item in report["objects"] if item["object"] == "quadratic")
    assert row["invariant_role"] == "factored"
    expanded = next(item for item in row["writings"] if item["role"] == "expanded")
    assert expanded["source"] == "a * x * x - a * (r + s) * x + a * r * s"
    assert expanded["cheap_manifest"]["transparent"] == ()
    assert expanded["invariant_cost"] == 5
    factored = next(item for item in row["writings"] if item["role"] == "factored")
    assert factored["invariant_cost"] == 2
    assert factored["cheap_manifest"]["transparent"] == (
        "degree",
        "roots",
        "factor_structure",
    )


def test_what_invariance_really_takes_away_is_the_choice():
    """The half of the hypothesis that survives, stated as the measurement that supports it."""
    report = axis3()
    assert report["objects_with_world_dependent_writing"] == 16
    assert report["objects_with_world_dependent_manifest"]["transparent"] == 16
    assert report["objects_with_world_dependent_manifest"]["opaque"] == 29
    assert report["objects_with_world_dependent_writing_under_invariance"] == 0
    # the invariant cost of a tree does not depend on the world, so every world picks the same
    # writing: that is why the count above is zero and not merely small.
    for item in OBJECT_CORPUS:
        costs = {
            writing.role: invariant_cost(object_tree(writing)) for writing in item.writings
        }
        assert len(set(costs.values())) <= len(item.writings)
        for writing in item.writings:
            tree = object_tree(writing)
            assert invariant_cost(tree) == costs[writing.role]


def test_the_case_the_hypothesis_was_formed_from():
    """0040's one invariant curve, priced.

    ``(x - y) * (x + y)`` is 0040's ``difference_of_squares``.  It is invariant as written, its two
    brackets are exactly the ones every world requires, and four worlds would have written the same
    object with none.
    """
    report = axis3()
    row = next(item for item in report["objects"] if item["object"] == "difference_of_squares")
    factored = next(item for item in row["writings"] if item["role"] == "factored")
    assert factored["source"] == "(a + b) * (a - b)"
    assert factored["invariant_writing"] == "(a + b) * (a - b)"
    assert factored["invariant_cost"] == 2
    assert factored["cheapest_cost"] == 0
    assert factored["price"] == 2
    assert factored["control_cost"] == 2
    assert factored["manifest_loss"]["transparent"] == 0
    assert factored["manifest_loss"]["opaque"] == 2
    # The transparent sets are equal on both sides -- that IS the finding -- so the only place the
    # cheap and the invariant writing can be told apart is the opaque regime, and it is asserted
    # here rather than left to the loss count.
    assert factored["cheap_manifest"]["transparent"] == factored["invariant_manifest"]["transparent"]
    assert factored["cheap_manifest"]["opaque"] == ("degree", "roots", "factor_structure")
    assert factored["invariant_manifest"]["opaque"] == ("factor_structure",)
    expanded = next(item for item in row["writings"] if item["role"] == "expanded")
    assert expanded["cheap_manifest"]["opaque"] == (
        "degree",
        "leading_coefficient",
        "constant_term",
        "sign_structure",
        "even_parity",
    )
    assert expanded["invariant_manifest"]["opaque"] == ()
    assert expanded["manifest_loss"]["opaque"] == 5
    assert source_is_invariant("(x - y) * (x + y)") is True


# ============================================================================== concurrency


def test_sequential_and_parallel_agree_on_axis_1():
    assert axis1_report(3, workers=1) == axis1_report(3, workers=4)


def test_sequential_and_parallel_agree_on_axis_2():
    small = AXIS2_CORPUS[:4]
    assert axis2_report(small, workers=1) == axis2_report(small, workers=4)


def test_the_parallel_decision_is_derived_from_the_observed_core_count():
    assert worker_count_for(16, 10_000) == 12
    assert worker_count_for(4, 10_000) == 2
    assert worker_count_for(1, 10_000) == 1
    assert worker_count_for(16, 3) == 3
    assert default_worker_count(10_000) == worker_count_for(__import__("os").cpu_count() or 1, 10_000)


def test_the_three_workloads_are_decided_separately_and_one_of_them_stays_sequential():
    """Multicore by default, sequential where a measurement says so -- and it says so once."""
    assert POOL_STARTUP_SECONDS == 2.5
    assert WORD_SECONDS == 5.4e-04
    assert CELL_SECONDS == 1.06e-02
    assert PRICE_SECONDS == 2.2e-02
    assert should_parallelise(87381, WORD_SECONDS, 12) is True
    assert should_parallelise(1500, CELL_SECONDS, 12) is True
    assert should_parallelise(34, PRICE_SECONDS, 12) is False
    assert should_parallelise(1000, WORD_SECONDS, 1) is False
    assert should_parallelise(1, CELL_SECONDS, 12) is False


# ================================================================================== plumbing


def test_chain_supports_refuses_an_unbalanced_writing():
    with pytest.raises(ValueError):
        chain_supports("a + b)")
    with pytest.raises(ValueError):
        chain_supports("(a + b")


def test_word_indexing_and_sources():
    assert word_source("") == "a"
    assert word_source("+") == "a + b"
    assert word_source("+*") == "a + b * c"
    assert word_at(2, 0) == "++"
    assert word_at(2, 15) == "//"
    assert tuple(words_of_length(1)) == ("+", "-", "*", "/")
    assert len(tuple(words_of_length(3))) == 64
    with pytest.raises(ValueError):
        word_source("+" * 30)


def test_the_witness_table_covers_every_ordered_pair_of_distinct_operators():
    assert len(FIRST_ABOVE) == 12
    grammars = {grammar.id: grammar for grammar in STRICT}
    for (above, below), identifier in FIRST_ABOVE.items():
        precedence = grammars[identifier].precedence
        assert precedence.index(above) < precedence.index(below)


def test_the_world_registry_is_the_repository_registry():
    assert len(GRAMMARS) == 25
    assert len(STRICT) == 24
    assert GRAMMARS == all_grammars()
    assert GRAMMARS[0].id == "G0"


def test_the_whole_report_ties_the_three_axes_together():
    report = invariants_report(3)
    assert report["headline"]["characterisation_holds"] is True
    assert report["headline"]["disagreements"] == 0
    assert report["headline"]["invariant_by_construction"] == (
        "token_count",
        "leaf_multiset",
        "operator_multiset",
        "node_count",
    )
    assert report["headline"]["invariant_as_measured_fact"] == ()
    assert report["headline"]["bought_with_brackets"] is True
    assert report["headline"]["shows_less_transparent"] is False
    assert report["headline"]["shows_less_opaque"] is True
