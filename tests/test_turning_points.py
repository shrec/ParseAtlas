"""Validation of experiment 0047: sweep the parameter, publish the shape.

The card this file validates is judged on discipline more than on numbers, so the tests are written
to fail on a change of *shape* and not only on a change of headline:

* every swept curve is pinned as a **sequence**, together with the sample size behind each point,
  so a curve that keeps its argmax while changing its shape still fails;
* the **monotonicity verdict** of each curve is pinned separately from its values, so a curve that
  starts to turn fails even if the values move only slightly;
* every **turning point** is pinned with the parameter it occurs at and the fall that follows it;
* the **stratification** is pinned -- which strata exist, how many objects sit in each, and that no
  rate anywhere in the report is computed across strata;
* the **distinct-object column** is pinned beside the cell column wherever a cell is a product of
  an object with a writing and a world, because a two-object tail carrying fifty cells is the
  shape that makes a thin tail look thick;
* the sequential and parallel paths are asserted to agree rather than assumed to.

**Both withdrawals are pinned too.**  This module's subject has been rejected twice for the same
mistake -- an enumeration restriction read as a property of the rules -- and the second time inside
the repair of the first.  Round 1 published ``attainable 0 1 0`` for the witness cell and concluded
that the rules admit the tax curve; round 2 enumerated bracket sites at compound nodes only, so a
bracket around a leaf was never produced, and published "no cell of the corpus ever rises".  The
tests below pin both withdrawn blocks as data, and construct the two writings that refute them:
``((a * b)) * (c * d)`` for round 1 and ``(a) * (b + c)`` for round 2.

**The enumeration is pinned as a census.**  Curve A enumerates every bracket *pattern* -- every
antichain of positions, leaves and root included -- and the tests assert what that census stands
for: that a writing with brackets inside brackets has the manifest set of its outermost pattern and
at least its pattern's bracket count.  That is the answer to *what does this enumeration not
produce*, and it is checked here rather than argued.

**What is pinned at which scale.**  Curves B and C are published at word length ``7`` and ``6``;
that run takes tens of minutes and is not affordable inside the suite.  So the published tables are
written down here in full, and:

* every value the default suite can reach is asserted against them -- curve B's per-length rows are
  independent of where the sweep stops, so the affordable sweep to length ``5`` checks a genuine
  prefix of the published numbers, value by value;
* the values past that prefix, and curve C's published width curves -- which are means over the
  whole stratum and therefore *not* a prefix of a shorter sweep -- are asserted by the tests marked
  ``full_sweep``, which run only when ``PARSEATLAS_FULL_SWEEP=1`` is set.

The reports say the same thing in the same words.  The pinned values were produced by the recorded
run before they were written down.
"""

import os

import pytest

from parseatlas.grammar import OPERATORS
from parseatlas.manifest_properties import CORPUS as MANIFEST_CORPUS
from parseatlas.manifest_properties import (
    PROPERTIES,
    PROPERTY_NAMES,
    REGIMES,
    bracket_count,
    object_tree,
    surface,
    surface_text,
)
from parseatlas.notational_cost import GRAMMARS, parenthesis_cost
from parseatlas.parser import Binary, parse
from parseatlas.turning_points import (
    AXIS_CHAIN,
    BRACKET_WITNESS,
    OPERAND_NAMES,
    PARALLEL_MINIMUM_ITEMS,
    PATTERN_MINIMUM_ITEMS,
    WITHDRAWN,
    _map_payloads,
    _words_of_length,
    argmax_point,
    attainable_with_padding,
    axis_grammars,
    axis_width_sweep,
    bracket_cell,
    bracket_patterns,
    bracket_sites,
    bracket_sweep,
    bracketed_surface,
    catalan,
    curve_summary,
    enumeration_audit,
    first_differences,
    leaf_bracket_witness,
    length_sweep,
    maximal_positions,
    monotonicity,
    operator_word,
    padding_witness,
    pooling_audit,
    resolve_sweep_workers,
    support_ceiling,
    turning_points,
    turning_points_report,
    witness_sweep,
    word_record,
    writing_audit,
)

#: The published scale of curves B and C costs tens of minutes.  It is pinned, and it runs when
#: this is set, so the published numbers are checked by the same assertions the suite uses.
full_sweep = pytest.mark.skipif(
    os.environ.get("PARSEATLAS_FULL_SWEEP") != "1",
    reason="set PARSEATLAS_FULL_SWEEP=1 to check the published scale of curves B and C",
)


def rounded(values, places=4):
    return [round(float(value), places) for value in values]


def manifest_set_of(written, opaque, variable):
    """The 0038 manifest set of a written form, so a test can compare two writings directly."""
    return tuple(rule.name for rule in PROPERTIES if rule.shape(written, opaque, variable))


# =============================================================== the curve vocabulary


def test_first_differences_is_the_sequence_a_turn_shows_up_in():
    assert first_differences([1, 3, 6, 4]) == (2, 3, -2)
    assert first_differences([5]) == ()


def test_monotonicity_verdicts():
    assert monotonicity([1, 1, 1]) == "constant"
    assert monotonicity([1, 2, 2, 3]) == "non-decreasing"
    assert monotonicity([3, 3, 2, 1]) == "non-increasing"
    assert monotonicity([1, 3, 2]) == "non-monotone"


def test_a_one_point_curve_is_undefined_and_not_trivially_monotone():
    assert monotonicity([7]) == "undefined"
    assert monotonicity([]) == "undefined"


def test_turning_point_names_the_parameter_and_the_drop_after_it():
    found = turning_points([0, 1, 2, 3], [1.0, 4.0, 2.0, 0.5])
    assert len(found) == 1
    assert found[0]["kind"] == "peak"
    assert found[0]["parameter"] == 1
    assert found[0]["value"] == 4.0
    assert found[0]["drop_after"] == pytest.approx(3.5)


def test_a_flat_stretch_does_not_break_a_run():
    """``1 2 2 1`` turns once, and the flat top is named at its right-hand end."""
    found = turning_points([0, 1, 2, 3], [1.0, 2.0, 2.0, 1.0])
    assert [entry["kind"] for entry in found] == ["peak"]
    assert found[0]["parameter"] == 2
    assert found[0]["drop_after"] == pytest.approx(1.0)


def test_trough_is_reported_with_the_rise_after_it():
    found = turning_points([0, 1, 2], [3.0, 1.0, 5.0])
    assert [entry["kind"] for entry in found] == ["trough"]
    assert found[0]["rise_after"] == pytest.approx(4.0)


def test_argmax_takes_the_first_of_a_tie():
    assert argmax_point([0, 1, 2], [2.0, 2.0, 1.0]) == {"parameter": 0, "value": 2.0}


def test_a_curve_cannot_be_built_without_naming_its_stratum():
    with pytest.raises(ValueError):
        curve_summary([0, 1], [1.0, 2.0], [5, 5], stratum="", measurement="anything")


def test_curve_summary_publishes_the_whole_shape_not_only_the_argmax():
    summary = curve_summary(
        [0, 1, 2], [1.0, 3.0, 2.0], [10, 10, 10], stratum="test", measurement="test"
    )
    assert summary["value"] == [1.0, 3.0, 2.0]
    assert summary["first_difference"] == [2.0, -1.0]
    assert summary["sample_size"] == [10, 10, 10]
    assert summary["monotone"] == "non-monotone"
    assert summary["is_monotone"] is False
    assert summary["argmax"] == {"parameter": 1, "value": 3.0}
    assert summary["turning_points"][0]["parameter"] == 1
    assert summary["still_moving_at_end"] is True


def test_a_curve_carries_an_object_column_beside_its_cell_column():
    """Fifty cells over two objects is a two-object point, and the audit must be able to see it."""
    summary = curve_summary(
        [0, 1], [1.0, 2.0], [50, 50], stratum="test", measurement="test", objects=[34, 2]
    )
    assert summary["sample_size"] == [50, 50]
    assert summary["objects"] == [34, 2]
    assert summary["minimum_sample_size"] == 50
    assert summary["minimum_objects"] == 2


def test_a_curve_without_an_object_column_says_so_rather_than_guessing():
    summary = curve_summary([0, 1], [1.0, 2.0], [5, 5], stratum="test", measurement="test")
    assert summary["objects"] is None
    assert summary["minimum_objects"] is None


def test_the_object_column_must_have_the_length_of_the_curve():
    with pytest.raises(ValueError):
        curve_summary(
            [0, 1], [1.0, 2.0], [5, 5], stratum="test", measurement="test", objects=[5]
        )


# =============================================================== the withdrawal


def test_the_module_records_both_withdrawals_and_what_replaced_them():
    """The retracted blocks are data, not only prose, so a test can hold them in place."""
    rounds = WITHDRAWN["rounds"]
    assert [entry["round"] for entry in rounds] == [1, 2]
    assert rounds[0]["claim"] == "The rules admit the tax curve."
    assert rounds[0]["published_as"] == {"brackets": [1, 2, 3], "attainable": [0, 1, 0]}
    assert rounds[0]["corrected_to"] == {"brackets": [1, 2, 3], "attainable": [0, 1, 1]}
    assert rounds[0]["witness"] == "((a * b)) * (c * d)"
    assert rounds[1]["claim"] == "No cell of the 34-object corpus ever rises."
    assert rounds[1]["published_as"] == {
        "brackets": [1, 2],
        "attainable": [0, 0],
        "verdict": "constant",
    }
    assert rounds[1]["corrected_to"] == {
        "brackets": [1, 2],
        "attainable": [0, 1],
        "verdict": "non-decreasing",
    }
    assert rounds[1]["witness"] == "(a) * (b + c)"
    assert "declared at" in WITHDRAWN["lesson"]


def test_the_round_one_block_is_refuted_by_a_writing_that_exists():
    """One writing settles it: three brackets, same tree, ``factor_structure`` still manifest."""
    found = padding_witness()
    assert found["round"] == 1
    assert found["three_brackets"]["writing"] == "((a * b)) * (c * d)"
    assert found["three_brackets"]["brackets"] == 3
    assert found["three_brackets"]["reparses_to_the_same_tree"] is True
    assert found["three_brackets"]["manifest"] == ["factor_structure"]
    assert found["withdrawn_attainable_at_three"] == 0
    assert found["attainable_at_three"] == 1


def test_the_round_two_block_is_refuted_by_a_writing_that_exists():
    """A bracket around a LEAF, which the earlier enumeration never produced.

    ``a * (b + c)`` shows nothing under the opaque rules; ``(a) * (b + c)`` shows
    ``factor_structure``, costs one more bracket, and reparses to the same tree.  That is the whole
    of the round 2 correction, in one writing.
    """
    found = leaf_bracket_witness()
    assert found["round"] == 2
    assert found["one_bracket"] == {
        "writing": "a * (b + c)",
        "brackets": 1,
        "manifest": [],
    }
    assert found["two_brackets"]["writing"] == "(a) * (b + c)"
    assert found["two_brackets"]["brackets"] == 2
    assert found["two_brackets"]["manifest"] == ["factor_structure"]
    assert found["two_brackets"]["reparses_to_the_same_tree"] is True
    assert found["withdrawn_attainable"] == [0, 0]
    assert found["attainable"] == [0, 1]
    assert found["sites"] == [[], ["l"], ["r"], ["r", "l"], ["r", "r"]]
    assert found["sites_an_earlier_revision_enumerated"] == [[], ["r"]]


def test_attainable_with_padding_is_the_running_maximum_of_the_enumerated_curve():
    assert attainable_with_padding([1, 2, 3], [0, 1, 0]) == (0, 1, 1)
    assert attainable_with_padding([2, 3, 4], [1, 1, 0]) == (1, 1, 1)
    assert attainable_with_padding([1, 2, 3, 4], [0, 2, 1, 0]) == (0, 2, 2, 2)


def test_padding_does_not_carry_out_of_a_bracket_free_writing():
    """At zero brackets there is nothing to double, so the first bracket may still cost."""
    assert attainable_with_padding([0, 1, 2], [3, 0, 0]) == (3, 0, 0)
    assert attainable_with_padding([0, 1, 2], [3, 1, 0]) == (3, 1, 1)


def test_a_padded_attainable_curve_can_never_carry_a_peak():
    """The structural claim, checked on every short sequence rather than argued once.

    A rise is possible only inside the running-maximum stretch and a fall only at the step out of
    the bracket-free writing, which no rise can precede.  So a peak is impossible, which is exactly
    why the withdrawn witness block could not have been what it claimed to be.
    """
    from itertools import product

    for minimum in (0, 1, 2):
        counts = [minimum + index for index in range(4)]
        for enumerated in product(range(3), repeat=4):
            carried = attainable_with_padding(counts, enumerated)
            found = turning_points(counts, carried)
            assert [entry["kind"] for entry in found] in ([], ["trough"])


def test_attainable_with_padding_refuses_a_mismatched_pair():
    with pytest.raises(ValueError):
        attainable_with_padding([0, 1], [1])


# =============================================================== curve A: the machinery


def test_the_minimum_bracket_set_is_the_one_0034_measures():
    for item in MANIFEST_CORPUS[:6]:
        for writing in item.writings:
            tree = object_tree(writing)
            for grammar in GRAMMARS[:5]:
                _, forced = bracket_sites(tree, grammar)
                assert len(forced) == parenthesis_cost(tree, grammar)


def test_no_optional_brackets_reproduces_0038_surface_exactly():
    for item in MANIFEST_CORPUS[:8]:
        for writing in item.writings:
            tree = object_tree(writing)
            for grammar in GRAMMARS:
                assert bracketed_surface(tree, grammar, ()) == surface(tree, grammar)


def test_every_enumerated_writing_denotes_the_same_object():
    audit = writing_audit(MANIFEST_CORPUS[:6], GRAMMARS[:6], workers=1)
    assert audit["failure_count"] == 0
    assert audit["all_writings_denote_the_same_tree"] is True
    assert audit["minimum_agrees_with_0038_surface"] is True
    assert audit["writings_checked"] > 0


def test_the_root_is_a_bracketable_site_and_is_never_forced():
    tree = object_tree(MANIFEST_CORPUS[0].writings[0])
    for grammar in GRAMMARS:
        sites, forced = bracket_sites(tree, grammar)
        assert () in sites
        assert () not in forced


def test_every_node_is_a_bracket_site_and_leaves_are_never_forced():
    """The round 2 defect, in the one line that would have caught it.

    An earlier revision walked only compound nodes, so a tree of ``n`` leaves offered ``n`` fewer
    sites than it has, and the missing ones were exactly the ones the opaque rules react to.
    """
    for item in MANIFEST_CORPUS:
        for writing in item.writings:
            tree = object_tree(writing)
            expected = _nodes_of(tree)
            for grammar in GRAMMARS[:4]:
                sites, forced = bracket_sites(tree, grammar)
                assert sorted(sites) == sorted(expected)
                assert all(_at(tree, path) is not None for path in sites)
                assert all(isinstance(_at(tree, path), Binary) for path in forced)


def _at(tree, path):
    node = tree
    for step in path:
        if not isinstance(node, Binary):
            return None
        node = node.left if step == "l" else node.right
    return node


def _nodes_of(tree, path=()):
    found = [path]
    if isinstance(tree, Binary):
        found += _nodes_of(tree.left, path + ("l",))
        found += _nodes_of(tree.right, path + ("r",))
    return found


def test_a_bracket_around_a_leaf_is_a_writing_of_the_same_object():
    """``(a) * (b + c)`` is not a different object, and the builder must be able to write it."""
    item = next(entry for entry in MANIFEST_CORPUS if entry.name == "distributive_law")
    writing = next(entry for entry in item.writings if entry.role == "factored")
    tree = object_tree(writing)
    grammar = GRAMMARS[0]
    written = bracketed_surface(tree, grammar, (("l",),))
    assert surface_text(written) == "(a) * (b + c)"
    assert parse(surface_text(written), grammar) == tree


def test_the_pattern_census_is_the_antichains_of_the_tree():
    """A pattern is a set of outermost brackets, so the count follows the tree and not a bound."""
    item = next(entry for entry in MANIFEST_CORPUS if entry.name == "distributive_law")
    writing = next(entry for entry in item.writings if entry.role == "factored")
    tree = object_tree(writing)
    sites, _ = bracket_sites(tree, GRAMMARS[0])
    patterns = bracket_patterns(tree, sites)
    assert len(sites) == 5
    assert len(patterns) == 11
    assert len({paths for paths, _size, _covers, _own in patterns}) == 11
    for paths, size, _covers, _own in patterns:
        assert size == len(paths)
        assert maximal_positions(paths) == paths


def test_maximal_positions_keeps_only_the_outermost_brackets():
    assert maximal_positions([(), ("l",), ("r", "l")]) == frozenset({()})
    assert maximal_positions([("l",), ("r",)]) == frozenset({("l",), ("r",)})
    assert maximal_positions([]) == frozenset()


def test_the_census_stands_for_every_writing_the_object_has():
    """What the enumeration does NOT produce, and why it cannot change the answer.

    It produces one writing per bracket pattern.  Everything else is a writing with a bracket
    inside a bracket, and the audit checks -- over a census of every bracket subset of every small
    enough writing, and over a seeded sample of arbitrarily nested ones -- that such a writing has
    the manifest set of its pattern and at least its pattern's bracket count.
    """
    audit = enumeration_audit(MANIFEST_CORPUS[:8], GRAMMARS[:5], sample=400)
    assert audit["census_stands_for_every_writing"] is True
    assert audit["failure_count"] == 0
    assert audit["sites"]["every_node_is_a_site"] is True
    assert audit["reduction"]["manifest_set_is_the_pattern_s"] is True
    assert audit["reduction"]["writings_covered"] > 0
    assert audit["reduction"]["bracket_subsets_checked"] > 0
    nesting = audit["nesting"]
    assert nesting["sample"] == 400
    assert nesting["writings_no_subset_enumeration_reaches"] > 0
    assert nesting["manifest_set_is_the_pattern_s"] == 400
    assert nesting["bracket_count_at_least_the_pattern_minimum"] == 400
    assert nesting["reparses_to_the_intended_tree"] == 400


def test_a_doubled_bracket_is_a_carry_and_not_a_flat_continuation():
    """The datum round 1 read backwards, pinned with the reading that is correct."""
    item = next(entry for entry in MANIFEST_CORPUS if entry.name == "binomial_square")
    writing = next(entry for entry in item.writings if entry.role == "factored")
    tree = object_tree(writing)
    for grammar in GRAMMARS[:5]:
        sites, _ = bracket_sites(tree, grammar)
        for path in sites:
            base = bracketed_surface(tree, grammar, (path,))
            padded = bracketed_surface(tree, grammar, (path,), (path,))
            for regime in REGIMES:
                opaque = regime == "opaque"
                assert manifest_set_of(base, opaque, item.variable) == manifest_set_of(
                    padded, opaque, item.variable
                )
            assert bracket_count(padded) == bracket_count(base) + 1
            assert parse(surface_text(padded), grammar) == tree


# =============================================================== curve A: the sweep


@pytest.fixture(scope="module")
def brackets():
    return bracket_sweep()


TRANSPARENT_POOLED = [
    2.0755,
    1.8448,
    1.9924,
    2.1377,
    2.3011,
    2.4673,
    2.6383,
    2.7191,
    2.7917,
    2.9286,
    3.6842,
    3.6842,
    3.9286,
    3.9286,
    3.9286,
]
OPAQUE_POOLED = [
    2.0755,
    0.1067,
    0.2076,
    0.1601,
    0.1593,
    0.1499,
    0.1191,
    0.0449,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
]
#: The attainable curve, padding admitted.  Compare the unpadded one below: they part company at
#: three brackets, and that gap is this card's round 1 correction.
OPAQUE_POOLED_ATTAINABLE = [
    2.0755,
    0.1505,
    0.2426,
    0.2302,
    0.1791,
    0.1699,
    0.1191,
    0.0449,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
]
#: What the census reaches before the padding carry: the best a pattern whose minimum bracket count
#: is exactly that one can show.
OPAQUE_POOLED_UNPADDED = [
    2.0755,
    0.1505,
    0.2426,
    0.1719,
    0.1727,
    0.1569,
    0.1191,
    0.0449,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
]
POOLED_SAMPLE_SIZES = [424, 638, 1051, 995, 631, 306, 235, 89, 48, 28, 19, 19, 14, 14, 14]
#: Distinct objects behind each bracket count.  The tail is two objects wide, not fourteen.
POOLED_OBJECTS = [34, 34, 34, 33, 30, 18, 16, 9, 7, 4, 3, 3, 2, 2, 2]
BRACKET_COUNTS = list(range(15))


def test_the_bracket_sweep_covers_the_whole_0038_grid(brackets):
    assert brackets["corpus_objects"] == 34
    assert brackets["writings"] == 50
    assert brackets["worlds"] == 25
    assert brackets["cells"] == 2500
    assert brackets["regimes"] == ["transparent", "opaque"]


def test_the_census_size_is_the_pattern_count_and_the_axis_has_no_gap(brackets):
    """The enumeration is a census and its size is a fact about the trees, not about a budget."""
    assert brackets["patterns"] == 156475
    assert brackets["patterns_legal_per_cell"] == 1962688
    assert brackets["every_axis_is_gap_free"] is True


def test_transparent_pooled_curve_is_pinned_as_a_sequence(brackets):
    curve = brackets["regime_results"]["transparent"]["pooled_mean_curve"]
    assert curve["parameter"] == BRACKET_COUNTS
    assert rounded(curve["value"]) == TRANSPARENT_POOLED
    assert curve["sample_size"] == POOLED_SAMPLE_SIZES
    assert curve["objects"] == POOLED_OBJECTS


def test_under_the_transparent_rules_the_mean_and_the_attainable_curve_coincide(brackets):
    """A bracket is invisible there, so every writing of a cell shows the same set: max = mean."""
    regime = brackets["regime_results"]["transparent"]
    assert rounded(regime["pooled_attainable_curve"]["value"]) == TRANSPARENT_POOLED
    assert rounded(regime["pooled_unpadded_attainable_curve"]["value"]) == TRANSPARENT_POOLED
    assert regime["cells_padding_changed"] == 0


def test_the_transparent_pooled_curve_appears_to_turn(brackets):
    """It troughs at one bracket and climbs to the end of a two-object tail."""
    curve = brackets["regime_results"]["transparent"]["pooled_mean_curve"]
    assert curve["monotone"] == "non-monotone"
    assert [
        (entry["kind"], entry["parameter"]) for entry in curve["turning_points"]
    ] == [("trough", 1)]
    trough = curve["turning_points"][0]
    assert round(trough["value"], 4) == 1.8448
    assert round(trough["rise_after"], 4) == 2.0837
    assert curve["argmax"]["parameter"] == 12
    assert round(curve["argmax"]["value"], 4) == 3.9286


def test_the_transparent_turn_is_entirely_sample_composition(brackets):
    """The pooled curve turns; every cell in it is exactly flat.  That gap is the whole card."""
    regime = brackets["regime_results"]["transparent"]
    paired = regime["paired_first_difference_mean"]
    assert [entry["from"] for entry in paired] == list(range(14))
    assert [entry["cells"] for entry in paired] == PAIRED_CELLS
    assert all(entry["mean_delta"] == 0.0 for entry in paired)
    assert all(entry["rises"] == 0 and entry["falls"] == 0 for entry in paired)
    for reading in ("within_cell", "within_cell_unpadded_attainable", "within_cell_pattern_mean"):
        block = regime[reading]
        assert block["cells"] == 1250
        assert block["constant"] == 1250
        assert block["cells_that_ever_rise"] == 0
        assert block["cells_with_a_peak"] == 0
    assert regime["rising_cells"] == {"cells": 0, "by_object": {}, "by_property": {}}


def test_opaque_pooled_curve_is_pinned_as_a_sequence(brackets):
    curve = brackets["regime_results"]["opaque"]["pooled_mean_curve"]
    assert curve["parameter"] == BRACKET_COUNTS
    assert rounded(curve["value"]) == OPAQUE_POOLED
    assert curve["sample_size"] == POOLED_SAMPLE_SIZES
    assert curve["objects"] == POOLED_OBJECTS
    assert curve["monotone"] == "non-monotone"


def test_the_opaque_attainable_curve_is_pinned_against_the_unpadded_one(brackets):
    """Both readings are published, because the difference between them is the round 1 finding."""
    regime = brackets["regime_results"]["opaque"]
    assert rounded(regime["pooled_attainable_curve"]["value"]) == OPAQUE_POOLED_ATTAINABLE
    assert (
        rounded(regime["pooled_unpadded_attainable_curve"]["value"]) == OPAQUE_POOLED_UNPADDED
    )
    assert regime["cells_padding_changed"] == 66


def test_the_opaque_pooled_turns_are_pinned_and_are_composition(brackets):
    curve = brackets["regime_results"]["opaque"]["pooled_mean_curve"]
    assert [
        (entry["kind"], entry["parameter"]) for entry in curve["turning_points"]
    ] == [("trough", 1), ("peak", 2)]
    peak = curve["turning_points"][1]
    assert round(peak["value"], 4) == 0.2076
    assert round(peak["drop_after"], 4) == 0.2076


def test_even_the_pooled_attainable_curve_turns_while_no_cell_peaks(brackets):
    """A pooled curve of running maxima still turns, which is composition and nothing else."""
    curve = brackets["regime_results"]["opaque"]["pooled_attainable_curve"]
    peaks = [entry for entry in curve["turning_points"] if entry["kind"] == "peak"]
    assert [entry["parameter"] for entry in peaks] == [2]
    assert [round(entry["value"], 4) for entry in peaks] == [0.2426]
    assert brackets["regime_results"]["opaque"]["within_cell"]["cells_with_a_peak"] == 0


#: Cells present at both ends of each paired step.  The same for both regimes, because a cell's
#: bracket-count axis does not depend on how the rules read it.
PAIRED_CELLS = [424, 638, 906, 549, 302, 219, 85, 44, 28, 19, 19, 14, 14, 14]


def test_opaque_paired_first_differences_are_pinned(brackets):
    paired = brackets["regime_results"]["opaque"]["paired_first_difference_mean"]
    assert [entry["cells"] for entry in paired] == PAIRED_CELLS
    assert [round(entry["mean_delta"], 4) for entry in paired] == [
        -1.9715,
        0.0926,
        -0.0506,
        -0.0155,
        -0.0137,
        0.0037,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    assert [entry["rises"] for entry in paired] == [0, 140, 65, 20, 12, 4, 0, 0, 0, 0, 0, 0, 0, 0]
    assert [entry["falls"] for entry in paired] == [334, 24, 91, 29, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def test_the_within_cell_attainable_curve_moves_at_the_first_two_brackets_only(brackets):
    """Padding admitted, a cell's attainable curve falls once at the first bracket and can RISE.

    The rise is the round 2 correction: ``68`` cells rise at the step from one bracket to two and
    ``4`` more at the step to three, and no cell moves at all after that.
    """
    paired = brackets["regime_results"]["opaque"]["paired_first_difference_attainable"]
    assert [round(entry["mean_delta"], 4) for entry in paired] == [
        -1.9057,
        0.1066,
        0.0044,
    ] + [0.0] * 11
    assert [entry["rises"] for entry in paired] == [0, 68, 4] + [0] * 11
    assert [entry["falls"] for entry in paired] == [334] + [0] * 13
    transparent = brackets["regime_results"]["transparent"][
        "paired_first_difference_attainable"
    ]
    assert [entry["mean_delta"] for entry in transparent] == [0.0] * 14


def test_seventy_two_opaque_cells_rise_and_none_of_them_peaks(brackets):
    """The round 2 correction, as the number it replaces.

    The withdrawn claim was ``0`` cells rise.  The leaf-admitting census says ``72``, and names
    them: four writings, one property, and not one turn.
    """
    regime = brackets["regime_results"]["opaque"]
    assert regime["within_cell"] == {
        "reading": "attainable",
        "cells": 1250,
        "constant": 844,
        "non_decreasing": 72,
        "non_increasing": 334,
        "non_monotone": 0,
        "cells_that_ever_rise": 72,
        "cells_with_a_peak": 0,
    }
    assert regime["rising_cells"] == {
        "cells": 72,
        "by_object": {
            "chain_rule/standard": 25,
            "trapezoid_area/mean_times_height": 21,
            "distributive_law/factored": 13,
            "taylor_first_term/standard": 13,
        },
        "by_property": {"factor_structure": 72},
    }


def test_the_other_two_readings_of_the_same_cells_are_pinned(brackets):
    """The unpadded reading and the pattern mean, kept so the size of each correction is visible."""
    regime = brackets["regime_results"]["opaque"]
    assert regime["within_cell_unpadded_attainable"] == {
        "reading": "unpadded_attainable",
        "cells": 1250,
        "constant": 778,
        "non_decreasing": 72,
        "non_increasing": 400,
        "non_monotone": 0,
        "cells_that_ever_rise": 72,
        "cells_with_a_peak": 0,
    }
    assert regime["within_cell_pattern_mean"] == {
        "reading": "mean",
        "cells": 1250,
        "constant": 688,
        "non_decreasing": 72,
        "non_increasing": 362,
        "non_monotone": 128,
        "cells_that_ever_rise": 200,
        "cells_with_a_peak": 0,
    }


def test_the_sample_size_and_the_object_count_at_every_bracket_count_are_pinned(brackets):
    """A thin tail cannot quietly carry a turn, and cells are not objects."""
    for regime in REGIMES:
        for name in (
            "pooled_mean_curve",
            "pooled_attainable_curve",
            "pooled_unpadded_attainable_curve",
        ):
            curve = brackets["regime_results"][regime][name]
            assert curve["sample_size"] == POOLED_SAMPLE_SIZES
            assert curve["objects"] == POOLED_OBJECTS
            assert curve["minimum_sample_size"] == 14
            assert curve["minimum_objects"] == 2


def test_the_pooled_rise_after_the_trough_rests_on_a_two_object_tail(brackets):
    """The rise the pooled curve shows after its trough is carried by a shrinking object count."""
    curve = brackets["regime_results"]["transparent"]["pooled_mean_curve"]
    tail = [
        (parameter, cells, objects)
        for parameter, cells, objects in zip(
            curve["parameter"], curve["sample_size"], curve["objects"]
        )
        if parameter >= 8
    ]
    assert tail == [
        (8, 48, 7),
        (9, 28, 4),
        (10, 19, 3),
        (11, 19, 3),
        (12, 14, 2),
        (13, 14, 2),
        (14, 14, 2),
    ]


# =============================================================== curve A: the strata


#: Cells whose object actually HAS the property, per regime, and the distinct objects behind them.
#: Every rate for a property is computed inside its own stratum, so these are the denominators, and
#: they are pinned because a rate whose denominator moved would otherwise change silently.
PROPERTY_STRATUM_CELLS = {
    "degree": 875,
    "leading_coefficient": 875,
    "constant_term": 875,
    "roots": 875,
    "factor_structure": 800,
    "sign_structure": 1200,
    "even_parity": 125,
}
PROPERTY_STRATUM_OBJECTS = {
    "degree": 21,
    "leading_coefficient": 21,
    "constant_term": 21,
    "roots": 21,
    "factor_structure": 20,
    "sign_structure": 32,
    "even_parity": 4,
}


def test_every_property_stratum_is_the_truth_set_and_is_pinned(brackets):
    for regime in REGIMES:
        strata = brackets["regime_results"][regime]["property_strata"]
        assert sorted(strata) == sorted(PROPERTY_NAMES)
        assert {name: entry["cells"] for name, entry in strata.items()} == PROPERTY_STRATUM_CELLS
        assert {
            name: entry["objects"] for name, entry in strata.items()
        } == PROPERTY_STRATUM_OBJECTS
        assert sum(PROPERTY_STRATUM_CELLS.values()) != 1250


#: The reachability rate for the one property a bracket can switch ON, padding admitted, under the
#: OPAQUE rules.  It is non-monotone, and the within-cell count below shows the turn is composition.
FACTOR_STRUCTURE_RATE = [
    0.1618,
    0.2359,
    0.3778,
    0.3646,
    0.2825,
    0.2374,
    0.1772,
    0.0727,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
]
#: The same rate under the TRANSPARENT rules, where a bracketed leaf is still a leaf.  The two
#: curves are not the same, and the opaque one is the higher of the two wherever they differ.
FACTOR_STRUCTURE_RATE_TRANSPARENT = [
    0.1618,
    0.1671,
    0.2356,
    0.2994,
    0.2725,
    0.2374,
    0.1772,
    0.0727,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
]
FACTOR_STRUCTURE_CELLS_AT = [272, 407, 675, 628, 400, 219, 158, 55, 26, 18, 13, 13, 13, 13, 13]
FACTOR_STRUCTURE_OBJECTS_AT = [20, 20, 20, 19, 17, 12, 12, 6, 4, 2, 1, 1, 1, 1, 1]


def test_the_factor_structure_stratum_curve_is_pinned(brackets):
    block = brackets["regime_results"]["opaque"]["property_strata"]["factor_structure"]
    curve = block["curve"]
    assert block["cells"] == 800
    assert block["objects"] == 20
    assert rounded(curve["value"]) == FACTOR_STRUCTURE_RATE
    assert curve["sample_size"] == FACTOR_STRUCTURE_CELLS_AT
    assert curve["objects"] == FACTOR_STRUCTURE_OBJECTS_AT
    assert curve["monotone"] == "non-monotone"
    assert [
        (entry["kind"], entry["parameter"]) for entry in curve["turning_points"]
    ] == [("peak", 2)]
    assert curve["minimum_objects"] == 1


def test_the_opaque_rules_make_factor_structure_MORE_reachable_than_the_transparent_ones(brackets):
    """The one place opacity helps, and the mechanism is the leaf bracket the census now produces.

    Under the transparent rules a bracketed leaf is still a leaf, so ``(a) * (b + c)`` has one
    compound numerator factor and ``factor_structure`` stays invisible.  Under the opaque rules the
    bracket makes the leaf uninspectable and therefore *not an atom*, and the rule fires.  So the
    two reachability curves do not agree, and the opaque one is the higher wherever they differ --
    which reverses the direction the withdrawn revision reported.
    """
    transparent = brackets["regime_results"]["transparent"]["property_strata"][
        "factor_structure"
    ]["curve"]
    opaque = brackets["regime_results"]["opaque"]["property_strata"]["factor_structure"]["curve"]
    assert rounded(opaque["value"]) == FACTOR_STRUCTURE_RATE
    assert rounded(transparent["value"]) == FACTOR_STRUCTURE_RATE_TRANSPARENT
    assert rounded(transparent["value"]) != rounded(opaque["value"])
    assert all(
        opaque_value >= transparent_value
        for opaque_value, transparent_value in zip(opaque["value"], transparent["value"])
    )
    differ = [
        index
        for index in range(len(FACTOR_STRUCTURE_RATE))
        if FACTOR_STRUCTURE_RATE[index] != FACTOR_STRUCTURE_RATE_TRANSPARENT[index]
    ]
    assert differ == [1, 2, 3, 4]


def test_six_of_the_seven_rules_collapse_to_zero_at_the_first_opaque_bracket(brackets):
    strata = brackets["regime_results"]["opaque"]["property_strata"]
    collapsing = {
        name: rounded(strata[name]["curve"]["value"])[:2]
        for name in PROPERTY_NAMES
        if name != "factor_structure"
    }
    assert collapsing == {
        "degree": [0.9187, 0.0],
        "leading_coefficient": [0.4878, 0.0],
        "constant_term": [0.4959, 0.0],
        "roots": [0.3577, 0.0],
        "sign_structure": [0.6373, 0.0],
        "even_parity": [0.8095, 0.0],
    }
    for name, entry in strata.items():
        if name != "factor_structure":
            assert entry["curve"]["monotone"] == "non-increasing"


def test_exactly_one_property_ever_becomes_visible_by_adding_a_bracket(brackets):
    """A flat manifest COUNT can hide one property switching on as another switches off.

    It does here.  ``72`` cells have a rising manifest *count*, but ``100`` have
    ``factor_structure`` join their reachable set: in the other ``28`` a lower-count writing shows
    it while a higher-count one shows more properties, so the count never moves.  That is why this
    reading exists, and the withdrawn revision reported ``0`` for it.
    """
    per_property = {
        regime: {
            name: entry["cells_that_ever_rise"]
            for name, entry in brackets["regime_results"][regime][
                "per_property_within_cell"
            ].items()
        }
        for regime in REGIMES
    }
    for regime in REGIMES:
        block = brackets["regime_results"][regime]["per_property_within_cell"]
        assert sorted(block) == sorted(PROPERTY_NAMES)
        assert {name: entry["cells"] for name, entry in block.items()} == {
            name: 1250 for name in PROPERTY_NAMES
        }
    assert per_property["transparent"] == {name: 0 for name in PROPERTY_NAMES}
    assert per_property["opaque"] == {
        "degree": 0,
        "leading_coefficient": 0,
        "constant_term": 0,
        "roots": 0,
        "factor_structure": 100,
        "sign_structure": 0,
        "even_parity": 0,
    }
    assert sum(per_property["opaque"].values()) + sum(per_property["transparent"].values()) == 100


def test_the_per_property_reading_admits_padding():
    """The reading is taken off the CARRIED sets, so a property once shown stays counted.

    Hand-built, because the grid does not separate the two readings: on this corpus and on the
    witnesses a property that goes on never goes off again, so ``shown`` and ``reachable`` give the
    same ``100``.  That coincidence is an observation and not a law, and the function's contract is
    the carried one, so a record where the two differ is what pins it.
    """
    from parseatlas.turning_points import _per_property_within_cell

    record = {
        "bracket_counts": [0, 1, 2],
        "shown": [["factor_structure"], [], ["factor_structure"]],
        "reachable": [["factor_structure"], ["factor_structure"], ["factor_structure"]],
    }
    block = _per_property_within_cell([record])
    assert block["factor_structure"] == {"cells": 1, "cells_that_ever_rise": 0}


def test_no_rate_in_the_bracket_sweep_is_pooled_across_strata(brackets):
    for regime in REGIMES:
        strata = brackets["regime_results"][regime]["property_strata"]
        for name, entry in strata.items():
            assert entry["stratum"] == f"regime={regime}; {name} true of the object"
            if entry["curve"] is not None:
                assert entry["curve"]["stratum"] == entry["stratum"]
                assert entry["cells"] < brackets["cells"]


# =============================================================== curve A: the witness


@pytest.fixture(scope="module")
def witness():
    return witness_sweep(workers=1)


def test_the_witness_objects_are_outside_the_0038_corpus():
    corpus_names = {item.name for item in MANIFEST_CORPUS}
    for item in BRACKET_WITNESS:
        assert item.name not in corpus_names
        assert item.field == "witness"


def test_the_opaque_rules_admit_a_rise_and_admit_no_peak(witness):
    """The half of the witness result that survives, and the half that is withdrawn.

    ``peaks_before_padding`` is empty too, and that is the round 2 correction reaching back into
    round 1: the peak the first revision published needed BOTH restrictions.  The leaf bracket
    supplies the missing three-bracket pattern, so the unpadded curve no longer falls either.
    """
    assert witness["cells"] == 200
    assert witness["cells_that_rise"] == 50
    assert witness["cells_with_a_peak"] == 0
    assert witness["peaks"] == []
    assert witness["cells_with_a_peak_before_padding"] == 0
    assert witness["peaks_before_padding"] == []


def test_the_witness_cells_rise_and_then_stay_up(witness):
    opaque = witness["regime_results"]["opaque"]
    assert opaque["within_cell"] == {
        "reading": "attainable",
        "cells": 100,
        "constant": 50,
        "non_decreasing": 50,
        "non_increasing": 0,
        "non_monotone": 0,
        "cells_that_ever_rise": 50,
        "cells_with_a_peak": 0,
    }
    assert opaque["within_cell_unpadded_attainable"] == {
        "reading": "unpadded_attainable",
        "cells": 100,
        "constant": 37,
        "non_decreasing": 50,
        "non_increasing": 13,
        "non_monotone": 0,
        "cells_that_ever_rise": 50,
        "cells_with_a_peak": 0,
    }
    assert opaque["rising_cells"] == {
        "cells": 50,
        "by_object": {
            "witness_product_of_pairs/paired": 25,
            "witness_triple_product/paired": 25,
        },
        "by_property": {"factor_structure": 50},
    }
    assert opaque["cells_padding_changed"] == 13
    assert witness["regime_results"]["transparent"]["cells_padding_changed"] == 0


def test_the_witness_cell_is_pinned_in_both_readings():
    """``0 1 0`` was round 1's answer; ``0 1 1`` is the cell's, in both readings now."""
    record = bracket_cell(("witness_product_of_pairs", "paired", "G0", "opaque"))
    assert record["bracket_counts"] == [1, 2, 3]
    assert record["patterns"] == [1, 4, 1]
    assert record["unpadded_attainable"] == [0, 1, 1]
    assert record["attainable"] == [0, 1, 1]
    assert record["shown"] == [[], ["factor_structure"], ["factor_structure"]]
    assert record["reachable"] == [[], ["factor_structure"], ["factor_structure"]]
    assert record["padding_changed_the_curve"] is False
    assert record["monotone_attainable"] == "non-decreasing"


def test_the_corpus_cell_the_round_two_withdrawal_is_about():
    """``distributive_law`` factored: published ``[0, 0]`` and ``constant``; it rises."""
    record = bracket_cell(("distributive_law", "factored", "G0", "opaque"))
    assert record["bracket_counts"] == [1, 2]
    assert record["patterns"] == [1, 2]
    assert record["unpadded_attainable"] == [0, 1]
    assert record["attainable"] == [0, 1]
    assert record["shown"] == [[], ["factor_structure"]]
    assert record["reachable"] == [[], ["factor_structure"]]
    assert record["monotone_attainable"] == "non-decreasing"


def test_the_padding_carry_still_lands_inside_the_corpus():
    """The round 1 correction on a named identity: the unpadded curve falls, the cell's does not."""
    record = bracket_cell(("calibration_quadratic", "factored", "G0", "opaque"))
    assert record["bracket_counts"] == [2, 3]
    assert record["unpadded_attainable"] == [1, 0]
    assert record["attainable"] == [1, 1]
    assert record["reachable"] == [["factor_structure"], ["factor_structure"]]
    assert record["padding_changed_the_curve"] is True
    assert record["monotone_attainable"] == "constant"


def test_the_widest_riser_needs_two_brackets_and_is_a_named_identity():
    """``chain_rule`` is ``dfg * dg``: one bracket is not enough, two are, and it rises in all 25."""
    record = bracket_cell(("chain_rule", "standard", "G0", "opaque"))
    assert record["bracket_counts"] == [0, 1, 2]
    assert record["patterns"] == [1, 3, 1]
    assert record["attainable"] == [0, 0, 1]
    assert record["reachable"] == [[], [], ["factor_structure"]]
    assert record["monotone_attainable"] == "non-decreasing"


def test_nothing_anywhere_in_the_experiment_carries_a_within_cell_peak(brackets, witness):
    """The headline, mechanically: no cell of curve A peaks, in either grid, in either regime.

    Every reading is checked, not only the one the verdicts are taken from, because a peak in the
    mean reading would be a peak whatever the attainable curve did.
    """
    for sweep in (brackets["regime_results"], witness["regime_results"]):
        for regime in REGIMES:
            for reading in (
                "within_cell",
                "within_cell_unpadded_attainable",
                "within_cell_pattern_mean",
            ):
                assert sweep[regime][reading]["cells_with_a_peak"] == 0
            assert sweep[regime]["within_cell"]["non_monotone"] == 0
            assert sweep[regime]["within_cell_unpadded_attainable"]["non_monotone"] == 0


# =============================================================== curve B


@pytest.fixture(scope="module")
def lengths():
    return length_sweep(exhaustive_to=5)


def test_the_word_family_is_declared_and_uses_distinct_operands():
    assert operator_word(("+", "*")) == "a + b * c"
    assert OPERAND_NAMES[:3] == ("a", "b", "c")
    tree = parse(operator_word(("+", "*")), GRAMMARS[0])
    assert tree is not None


def test_the_t6_ceiling_is_the_null_model():
    assert catalan(4) == 14
    assert support_ceiling(4, 4) == 14
    assert support_ceiling(4, 5) == 25
    assert support_ceiling(2, 6) == 3
    assert support_ceiling(1, 6) == 2


#: The support-stratified split of the PUBLISHED sweep, exhaustive to length 7.  The rows for a
#: given ``(support, length)`` do not depend on where the sweep stops, so the affordable sweep to
#: length 5 checks the first entries of each list value for value.
LENGTH_STRATUM_WORDS_PUBLISHED = {
    "1": [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4)],
    "2": [(2, 12), (3, 36), (4, 84), (5, 180), (6, 372), (7, 756)],
    "3": [(3, 24), (4, 144), (5, 600), (6, 2160), (7, 7224)],
    "4": [(4, 24), (5, 240), (6, 1560), (7, 8400)],
}

#: Mean distinct semantic classes per word, inside each support stratum, against word length.
LENGTH_CLASS_CURVES_PUBLISHED = {
    "1": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "2": [1.8333, 1.8889, 1.9286, 1.9556, 1.9731, 1.9841],
    "3": [4.1667, 4.4722, 4.7067, 4.9019, 5.067],
    "4": [10.75, 12.05, 13.1115, 14.0486],
}

#: Mean of (classes / distinct ASTs) per word -- NOT the quotient of the two means: how much of the parse diversity sympy collapses.
LENGTH_COLLAPSE_CURVES_PUBLISHED = {
    "1": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "2": [0.9167, 0.9074, 0.9008, 0.8963, 0.8934, 0.8915],
    "3": [0.8333, 0.839, 0.8435, 0.8469, 0.8493],
    "4": [0.7679, 0.7812, 0.7961, 0.8098],
}

#: Mean distinct ASTs per word, the numerator of the collapse ratio.
LENGTH_AST_CURVES_PUBLISHED = {
    "1": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "2": [2.0, 2.1111, 2.1905, 2.2444, 2.2796, 2.3016],
    "3": [5.0, 5.3333, 5.5867, 5.7981, 5.9779],
    "4": [14.0, 15.4167, 16.459, 17.3362],
}

#: The T6 ceiling printed beside every count.
LENGTH_CEILINGS_PUBLISHED = {
    "1": [1, 2, 2, 2, 2, 2, 2],
    "2": [2, 3, 3, 3, 3, 3],
    "3": [5, 7, 7, 7, 7],
    "4": [14, 25, 25, 25],
}

#: The class count as a fraction of the T6 ceiling: non-monotone in every moving stratum, because
#: the ceiling jumps where the Catalan bound gives way to the support bound.
LENGTH_CEILING_FRACTIONS_PUBLISHED = {
    "1": [1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    "2": [0.9167, 0.6296, 0.6429, 0.6519, 0.6577, 0.6614],
    "3": [0.8333, 0.6389, 0.6724, 0.7003, 0.7239],
    "4": [0.7679, 0.482, 0.5245, 0.5619],
}

LENGTH_STRATUM_WORDS = {
    key: [row for row in rows if row[0] <= 5]
    for key, rows in LENGTH_STRATUM_WORDS_PUBLISHED.items()
}


def _prefix(published, key, observed):
    return published[key][: len(observed)]


def test_the_support_stratified_split_is_pinned(lengths):
    assert sorted(lengths["strata"]) == ["1", "2", "3", "4"]
    assert {
        key: [(row["length"], row["words"]) for row in entry["table"]]
        for key, entry in lengths["strata"].items()
    } == LENGTH_STRATUM_WORDS
    assert lengths["words"] == 1364
    assert lengths["strata_partition_the_corpus"] is True


def test_the_class_curve_of_every_stratum_is_a_prefix_of_the_published_one(lengths):
    for key in LENGTH_CLASS_CURVES_PUBLISHED:
        curve = lengths["strata"][key]["classes_curve"]
        assert rounded(curve["value"]) == _prefix(
            LENGTH_CLASS_CURVES_PUBLISHED, key, curve["value"]
        )
        assert curve["sample_size"] == [words for _, words in LENGTH_STRATUM_WORDS[key]]
        assert curve["objects"] == curve["sample_size"]
        assert curve["stratum"] == f"operator support = {key}"


def test_no_class_curve_turns_and_the_moving_ones_are_still_rising(lengths):
    verdicts = {
        key: lengths["strata"][key]["classes_curve"]["monotone"]
        for key in LENGTH_CLASS_CURVES_PUBLISHED
    }
    assert verdicts == {
        "1": "constant",
        "2": "non-decreasing",
        "3": "non-decreasing",
        "4": "non-decreasing",
    }
    for key in LENGTH_CLASS_CURVES_PUBLISHED:
        curve = lengths["strata"][key]["classes_curve"]
        assert curve["turning_points"] == []
        assert curve["still_moving_at_end"] is (key != "1")


def test_every_curve_b_argmax_is_pinned(lengths):
    """The methods paragraph promises an argmax for every curve, so every one of them is pinned."""
    argmaxes = {
        key: {
            name: lengths["strata"][key][name]["argmax"]["parameter"]
            for name in ("classes_curve", "asts_curve", "collapse_curve", "ceiling_curve")
        }
        for key in LENGTH_CLASS_CURVES_PUBLISHED
    }
    assert argmaxes == {
        "1": {
            "classes_curve": 1,
            "asts_curve": 1,
            "collapse_curve": 1,
            "ceiling_curve": 1,
        },
        "2": {
            "classes_curve": 5,
            "asts_curve": 5,
            "collapse_curve": 2,
            "ceiling_curve": 2,
        },
        "3": {
            "classes_curve": 5,
            "asts_curve": 5,
            "collapse_curve": 5,
            "ceiling_curve": 3,
        },
        "4": {
            "classes_curve": 5,
            "asts_curve": 5,
            "collapse_curve": 5,
            "ceiling_curve": 4,
        },
    }


def test_the_collapse_ratio_moves_in_opposite_directions_across_strata(lengths):
    """The single clearest reason nothing here may be pooled: the strata disagree in sign."""
    for key in LENGTH_COLLAPSE_CURVES_PUBLISHED:
        curve = lengths["strata"][key]["collapse_curve"]
        assert rounded(curve["value"]) == _prefix(
            LENGTH_COLLAPSE_CURVES_PUBLISHED, key, curve["value"]
        )
    verdicts = {
        key: lengths["strata"][key]["collapse_curve"]["monotone"]
        for key in LENGTH_COLLAPSE_CURVES_PUBLISHED
    }
    assert verdicts == {
        "1": "constant",
        "2": "non-increasing",
        "3": "non-decreasing",
        "4": "non-decreasing",
    }


def test_the_ast_curve_and_the_ceiling_fraction_are_prefixes_of_the_published_ones(lengths):
    for key in LENGTH_AST_CURVES_PUBLISHED:
        asts = lengths["strata"][key]["asts_curve"]
        ceiling = lengths["strata"][key]["ceiling_curve"]
        assert rounded(asts["value"]) == _prefix(LENGTH_AST_CURVES_PUBLISHED, key, asts["value"])
        assert rounded(ceiling["value"]) == _prefix(
            LENGTH_CEILING_FRACTIONS_PUBLISHED, key, ceiling["value"]
        )


def test_the_t6_ceiling_is_pinned_next_to_every_count(lengths):
    ceilings = {
        key: [row["ceiling"] for row in entry["table"]]
        for key, entry in lengths["strata"].items()
    }
    assert ceilings == {
        key: _prefix(LENGTH_CEILINGS_PUBLISHED, key, value)
        for key, value in ceilings.items()
    }
    assert ceilings["4"] == [14, 25]


def test_the_exhaustive_limit_of_curve_b_is_named_a_computational_one(lengths):
    assert lengths["exhaustive_limit_is_computational"] is True
    assert lengths["coverage"] == {index: "exhaustive" for index in range(1, 6)}
    assert "null model" in lengths["pooled_warning"]


@full_sweep
def test_the_published_scale_of_curve_b_is_pinned_in_full():
    """The published tables, checked at the scale they were published at."""
    published = length_sweep(exhaustive_to=7, sampled_to=9, sample_size=256)
    assert published["words"] == 22356
    assert sum(
        row["words"] for entry in published["strata"].values() for row in entry["table"]
        if row["exhaustive"]
    ) == 21844
    assert {
        key: [(row["length"], row["words"]) for row in entry["table"] if row["exhaustive"]]
        for key, entry in published["strata"].items()
    } == LENGTH_STRATUM_WORDS_PUBLISHED
    for key, expected in LENGTH_CLASS_CURVES_PUBLISHED.items():
        assert rounded(published["strata"][key]["classes_curve"]["value"]) == expected
        assert rounded(published["strata"][key]["asts_curve"]["value"]) == (
            LENGTH_AST_CURVES_PUBLISHED[key]
        )
        assert rounded(published["strata"][key]["collapse_curve"]["value"]) == (
            LENGTH_COLLAPSE_CURVES_PUBLISHED[key]
        )
        assert rounded(published["strata"][key]["ceiling_curve"]["value"]) == (
            LENGTH_CEILING_FRACTIONS_PUBLISHED[key]
        )
        assert [
            row["ceiling"] for row in published["strata"][key]["table"] if row["exhaustive"]
        ] == LENGTH_CEILINGS_PUBLISHED[key]
    assert {
        key: entry["sampled_continuation"]["thinnest"]
        for key, entry in published["strata"].items()
    } == {"1": None, "2": 3, "3": 77, "4": 164}


# =============================================================== curve C


@pytest.fixture(scope="module")
def axis():
    return axis_width_sweep(exhaustive_to=4)


def test_the_axis_chain_is_declared_and_its_registries_are_the_expected_sizes():
    assert [list(entry) for entry in AXIS_CHAIN] == [
        [],
        ["+"],
        ["+", "-"],
        ["+", "-", "*"],
        ["+", "-", "*", "/"],
    ]
    assert [len(axis_grammars(entry)) for entry in AXIS_CHAIN] == [24, 48, 96, 192, 384]
    assert len(axis_grammars(OPERATORS)) == 384


#: Mean distinct semantic classes per word at axis widths 0..4, at the PUBLISHED scale, which is
#: exhaustive to word length 6.  A width curve is a mean over the whole stratum, so a shorter sweep
#: does not produce a prefix of it: it produces different numbers over a different word set.  Both
#: sets are therefore pinned, and each is labelled with the scale it belongs to.
AXIS_WIDTH_CURVES_PUBLISHED = {
    "1": [1.0, 1.0, 1.2083, 1.2083, 1.4167],
    "2": [1.9561, 1.9561, 2.6199, 2.6199, 3.4357],
    "3": [4.8347, 4.8347, 6.3402, 6.3402, 8.153],
    "4": [12.9408, 12.9408, 15.6798, 15.6798, 18.6886],
}
AXIS_STRATUM_WORDS_PUBLISHED = {"1": 24, "2": 684, "3": 2928, "4": 1824}

#: The same curves over the sweep the suite can afford, exhaustive to word length 4.
AXIS_WIDTH_CURVES = {
    "1": [1.0, 1.0, 1.1875, 1.1875, 1.375],
    "2": [1.9091, 1.9091, 2.3561, 2.3561, 2.8485],
    "3": [4.4286, 4.4286, 5.0, 5.0, 5.5714],
    "4": [10.75, 10.75, 10.75, 10.75, 10.75],
}
AXIS_STRATUM_WORDS = {"1": 16, "2": 132, "3": 168, "4": 24}


def test_widening_the_convention_axis_never_loses_a_meaning(axis):
    assert axis["nested_widening_never_loses"] is True
    assert axis["single_widening_never_loses"] is True
    assert axis["words_where_a_widening_lost_a_meaning"] == 0
    assert axis["words"] == 340
    assert axis["strata_partition_the_corpus"] is True


def test_the_axis_width_curve_of_every_stratum_is_pinned_as_a_sequence(axis):
    for key, expected in AXIS_WIDTH_CURVES.items():
        curve = axis["strata"][key]["width_curve"]
        assert curve["parameter"] == [0, 1, 2, 3, 4]
        assert rounded(curve["value"]) == expected
        assert curve["sample_size"] == [AXIS_STRATUM_WORDS[key]] * 5
        assert curve["objects"] == [AXIS_STRATUM_WORDS[key]] * 5
        assert curve["turning_points"] == []


def test_no_axis_widening_curve_turns(axis):
    verdicts = {key: axis["strata"][key]["width_curve"]["monotone"] for key in AXIS_WIDTH_CURVES}
    assert verdicts == {
        "1": "non-decreasing",
        "2": "non-decreasing",
        "3": "non-decreasing",
        "4": "constant",
    }


def test_every_curve_c_argmax_is_pinned(axis):
    argmaxes = {
        key: axis["strata"][key]["width_curve"]["argmax"]["parameter"]
        for key in AXIS_WIDTH_CURVES
    }
    assert argmaxes == {"1": 4, "2": 4, "3": 4, "4": 0}


def test_two_of_the_four_axis_dimensions_are_exactly_inert(axis):
    """Freeing the associativity of ``+`` or ``*`` doubles the registry and adds no meaning."""
    for key in AXIS_WIDTH_CURVES:
        singles = axis["strata"][key]["single_widening"]
        assert singles["+"]["mean_new_classes"] == 0.0
        assert singles["*"]["mean_new_classes"] == 0.0
        assert singles["+"]["words_gaining"] == 0
        assert singles["*"]["words_gaining"] == 0


def test_the_live_axis_dimensions_are_pinned(axis):
    """``-`` and ``/`` are the two live dimensions, and at this scale their yields coincide exactly.

    The coincidence is a pinned observation and not a law: over the published sweep to length 6 the
    two still gain in the same number of words in every stratum, but their mean yields separate in
    the SECOND decimal -- ``1.5055`` against ``1.5171`` at support 3 and ``2.7390`` against
    ``2.7544`` at support 4 -- which the full-scale test below pins.
    """
    live = {
        key: (
            round(axis["strata"][key]["single_widening"]["-"]["mean_new_classes"], 4),
            axis["strata"][key]["single_widening"]["-"]["words_gaining"],
        )
        for key in AXIS_WIDTH_CURVES
    }
    assert live == {"1": (0.1875, 3), "2": (0.447, 39), "3": (0.5714, 36), "4": (0.0, 0)}
    for key in AXIS_WIDTH_CURVES:
        minus = axis["strata"][key]["single_widening"]["-"]
        slash = axis["strata"][key]["single_widening"]["/"]
        assert minus["mean_new_classes"] == slash["mean_new_classes"]
        assert minus["words_gaining"] == slash["words_gaining"]


def test_nothing_is_ever_lost_by_a_widening_so_a_decay_cannot_be_a_turn(axis):
    for key in AXIS_WIDTH_CURVES:
        singles = axis["strata"][key]["single_widening"]
        assert all(entry["mean_lost_classes"] == 0.0 for entry in singles.values())


#: Yield per grammar added at the published scale: the quantity that is free to fall, and does.
AXIS_YIELD_PUBLISHED = {
    "1": [0.0, 0.004340, 0.0, 0.001085],
    "2": [0.0, 0.013828, 0.0, 0.004249],
    "3": [0.0, 0.031364, 0.0, 0.009442],
    "4": [0.0, 0.057063, 0.0, 0.015671],
}

#: The two LIVE widenings at the published scale, as ``(mean new classes, words gaining)``.  They
#: gain in the same number of words in every stratum and their mean yields separate in the SECOND
#: decimal at supports 3 and 4, which is the claim the report makes about them.
AXIS_LIVE_PUBLISHED = {
    "1": {"-": (0.2083, 5), "/": (0.2083, 5)},
    "2": {"-": (0.6637, 282), "/": (0.6637, 282)},
    "3": {"-": (1.5055, 1356), "/": (1.5171, 1356)},
    "4": {"-": (2.739, 720), "/": (2.7544, 720)},
}


@full_sweep
def test_the_published_scale_of_curve_c_is_pinned_in_full():
    published = axis_width_sweep(exhaustive_to=6, sampled_to=8, sample_size=256)
    assert published["exhaustive_words"] == 5460
    assert published["words"] == 5972
    assert published["nested_widening_never_loses"] is True
    assert published["single_widening_never_loses"] is True
    assert published["words_where_a_widening_lost_a_meaning"] == 0
    assert published["widenings_checked"] == 47776
    for key, expected in AXIS_WIDTH_CURVES_PUBLISHED.items():
        curve = published["strata"][key]["width_curve"]
        assert rounded(curve["value"]) == expected
        assert curve["sample_size"] == [AXIS_STRATUM_WORDS_PUBLISHED[key]] * 5
        assert curve["turning_points"] == []
        assert rounded(published["strata"][key]["yield_per_grammar_added"], 6) == (
            AXIS_YIELD_PUBLISHED[key]
        )
        singles = published["strata"][key]["single_widening"]
        assert {
            operator: (
                round(singles[operator]["mean_new_classes"], 4),
                singles[operator]["words_gaining"],
            )
            for operator in ("-", "/")
        } == AXIS_LIVE_PUBLISHED[key]


# =============================================================== discipline and plumbing


#: Every curve the experiment publishes, counted mechanically.  The earlier revision printed ``38``,
#: which was the count with the witness sweep's curves left out; the structure the module builds
#: carries ``50``.
PUBLISHED_CURVE_COUNT = 50


def test_every_curve_in_the_experiment_is_stratified(brackets, lengths, axis, witness):
    """The mechanical form of the card's rule, applied to every curve the experiment publishes."""
    assembled = {
        "brackets": {key: value for key, value in brackets.items() if key != "cell_records"},
        "witness": witness,
        "length": lengths,
        "axis": axis,
    }
    audit = pooling_audit(assembled)
    assert audit["curves"] == PUBLISHED_CURVE_COUNT
    assert audit["curves_without_stratum"] == []
    assert audit["curves_without_sample_sizes"] == []
    assert audit["every_curve_is_stratified"] is True


def test_the_thin_point_verdict_counts_objects_and_not_cells(brackets, lengths, axis, witness):
    """Curve A's tail holds fifty cells over two objects, and the audit must call that thin."""
    assembled = {
        "brackets": {key: value for key, value in brackets.items() if key != "cell_records"},
        "witness": witness,
        "length": lengths,
        "axis": axis,
    }
    audit = pooling_audit(assembled)
    assert audit["thin_point_threshold"] == 3
    assert audit["curves_with_an_object_column"] == PUBLISHED_CURVE_COUNT
    thin = audit["curves_with_a_thin_point"]
    assert len(thin) == 30
    assert all(entry["counted"] == "objects" for entry in thin)
    assert all(entry["thinnest_point"] <= 2 for entry in thin)
    assert all(entry["minimum_sample_size"] >= 8 for entry in thin)
    assert {entry["stratum"].split(";")[0] for entry in thin} == {
        "regime=transparent",
        "regime=opaque",
    }
    assert min(entry["minimum_sample_size"] for entry in thin) == 8
    assert max(entry["minimum_sample_size"] for entry in thin) == 14


def test_a_curve_without_an_object_column_falls_back_to_counting_cells():
    audit = pooling_audit(
        {
            "curve": curve_summary(
                [0, 1], [1.0, 2.0], [2, 2], stratum="test", measurement="thin in cells"
            )
        }
    )
    assert audit["curves_with_an_object_column"] == 0
    assert audit["curves_with_a_thin_point"][0]["counted"] == "cells"
    assert audit["curves_with_a_thin_point"][0]["thinnest_point"] == 2


def test_the_report_names_every_curve_it_publishes_and_its_argmaxes(brackets, lengths, axis):
    report = turning_points_report(
        length_exhaustive_to=2,
        axis_exhaustive_to=2,
        corpus=MANIFEST_CORPUS[:3],
        grammars=GRAMMARS[:4],
        enumeration_sample=200,
    )
    assert sorted(report["curves"]) == ["axis_width", "brackets", "brackets_witness", "length"]
    assert [entry["curve"] for entry in report["computational_limits"]] == ["B", "C"]
    assert report["pooling_audit"]["every_curve_is_stratified"] is True
    assert report["audits"]["writings_denote_one_object"]["failure_count"] == 0
    assert report["audits"]["enumeration_completeness"]["failure_count"] == 0
    assert report["withdrawn"] == WITHDRAWN
    assert sorted(report["witnesses"]) == ["round_1_padding", "round_2_leaf_bracket"]
    assert len(report["argmax_by_curve"]) == report["pooling_audit"]["curves"]
    assert all(entry["argmax"] is not None for entry in report["argmax_by_curve"])


def test_every_sweep_says_what_it_does_not_produce(brackets, lengths, axis):
    """The question both rejections came down to, answered per sweep inside the report itself."""
    report = turning_points_report(
        length_exhaustive_to=2,
        axis_exhaustive_to=2,
        corpus=MANIFEST_CORPUS[:3],
        grammars=GRAMMARS[:4],
        enumeration_sample=200,
    )
    entries = report["what_each_sweep_does_not_produce"]
    assert [entry["curve"] for entry in entries] == ["A", "B", "C"]
    for entry in entries:
        assert entry["not_produced"]
        assert entry["why_it_cannot_change_the_answer"]
        assert entry["checked"]
    assert entries[0]["checked"]["census_stands_for_every_writing"] is True


def test_pooling_audit_finds_a_curve_without_a_stratum():
    broken = {"curve": {"measurement": "x", "monotone": "constant", "sample_size": [1], "stratum": ""}}
    audit = pooling_audit(broken)
    assert audit["curves"] == 1
    assert audit["every_curve_is_stratified"] is False
    assert audit["curves_without_stratum"] == ["x"]


def test_sequential_and_parallel_agree_on_bracket_cells():
    corpus = MANIFEST_CORPUS[:4]
    grammars = GRAMMARS[:5]
    sequential = bracket_sweep(corpus, grammars, workers=1)
    parallel = bracket_sweep(corpus, grammars, workers=2)
    assert sequential["cell_records"] == parallel["cell_records"]
    assert sequential["regime_results"] == parallel["regime_results"]


def test_sequential_and_parallel_agree_on_word_records():
    words = _words_of_length(3)
    assert _map_payloads(word_record, words, 1) == _map_payloads(word_record, words, 2)


def test_worker_count_comes_from_the_observed_core_count_not_a_constant():
    assert resolve_sweep_workers(10) == 1
    assert resolve_sweep_workers(10, 3) == 3
    assert resolve_sweep_workers(100000) > 1


def test_each_sweep_carries_its_own_measured_floor():
    """One constant cannot serve both payloads, and the two floors are what says so.

    The corpus's ``50`` writings are ``50`` pattern censuses and are worth a pool; ``50`` word
    records are not, and the same call with the word floor stays sequential.
    """
    assert PATTERN_MINIMUM_ITEMS < PARALLEL_MINIMUM_ITEMS
    assert resolve_sweep_workers(50, minimum_items=PATTERN_MINIMUM_ITEMS) > 1
    assert resolve_sweep_workers(50) == 1
    assert resolve_sweep_workers(16, minimum_items=PATTERN_MINIMUM_ITEMS) == 1
