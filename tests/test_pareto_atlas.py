"""Validation of experiment 0049: the Pareto atlas of equivalent writings.

Every number here was measured before it was written down, and every headline is pinned as a
literal rather than recomputed from the module, so a change in the result fails a test instead of
quietly rewriting the finding.

The file is ordered cheap-first on purpose.  Four things are checked before anything touches the
667-writing grid, because without them nothing else means anything:

* **the measures are the imported objects**, checked by identity, not by equality -- a copied
  ``peak_live`` would pass an ``==`` check and would fail this one;
* **the benefit/cost signs**, pinned by a hand-built pair in which visibility alone decides, so a
  sign inversion fails on a two-line fixture rather than only in a total that a reader might not
  recompute;
* **dominance is a strict partial order**, asserted on the relation the module actually computes;
* **the round trip and the minimality of every bracket** over the whole grid, because the bracket
  axis is a cost only if every bracket in the rendering is required and the string reads back as the
  tree that was measured.

Object counts and cell counts are pinned in SEPARATE tests with separate names.  Experiment 0047 was
rejected for reporting one where the other was asked for, and a test that pins them together would
not catch the substitution.
"""

import itertools
import math

from parseatlas import manifest_properties as origin_visibility
from parseatlas import memory_ceiling as origin_memory
from parseatlas import notational_cost as origin_cost
from parseatlas import parallel_worlds as origin_depth
from parseatlas import visibility_ceiling as origin_space
from parseatlas.manifest_properties import CONTROL, CORPUS, GRAMMARS, OBJECT_BY_NAME
from parseatlas.pareto_atlas import (
    AXES,
    AXES_3,
    AXES_4,
    BENEFIT_AXES,
    CELL_SECONDS,
    COST_AXES,
    POOL_STARTUP_SECONDS,
    Profile,
    Representation,
    _grid,
    _map_chunks,
    _chunks,
    atlas,
    axis_lattice,
    cell_count,
    containment_audit,
    control_bracket_minimum,
    default_worker_count,
    dominates,
    frontier,
    frontier_audit,
    incomparability,
    minimality_audit,
    natural_writing,
    null_model,
    order_audit,
    profile,
    reference_world_sweep,
    representation_text,
    representation_tree,
    round_trip_audit,
    should_parallelise,
    sign_control,
    size_curve,
    space_provenance,
    vector,
    worker_count_for,
    writings_of,
)

# ---- measured once, then pinned; these are the numbers the report publishes --------------------

#: Sample sizes.  OBJECTS and CELLS are different quantities and are pinned in different tests.
OBJECTS = 34
DECLARED_WRITINGS = 50
REPRESENTATIONS = 667
WORLDS = 25
CELLS = 16_675

FULL_SPACE_TREES = 1_510_820

#: The four headline counts, 4-axis, reference world ``G0``.
OPTIMAL_FOUR = 59
DOMINATED_FOUR = 608
CONTROL_ON_FRONTIER = 34
CONTROL_DOMINATED = 0
CREATED_FOUR = 12

#: The same four, 3-axis.
OPTIMAL_THREE = 50
DOMINATED_THREE = 617
CREATED_THREE = 7

#: Question 4's denominator: objects where at least one world's natural writing differs from ``G0``'s.
OBJECTS_WITH_AN_ALTERNATIVE = 16

#: The null model.
MOVABLE_OBJECTS = 22
ONE_VECTOR_OBJECTS = 12
MOVABLE_BY_AXIS = {"brackets": 22, "depth": 13, "peak_live": 9, "visibility": 18}

#: The partial order over writings, pooled over all objects.
PAIRS = 127_423
ORDERED_FOUR = 63_407
INCOMPARABLE_FOUR = 54_768
EQUAL_FOUR = 9_248
ORDERED_THREE = 87_981
INCOMPARABLE_THREE = 28_653
EQUAL_THREE = 10_789

#: The 12 objects whose frontier carries a point ``G0`` would not write, 4-axis.
CREATED_OBJECTS_FOUR = (
    "calibration_quadratic",
    "distributive_law",
    "binomial_square",
    "quadratic",
    "binomial_cube",
    "perfect_square_trinomial",
    "line",
    "circle",
    "parabola",
    "trapezoid_area",
    "difference_quotient",
    "linear_approximation",
)

#: The 7 that survive when peak live is dropped from the axis set.
CREATED_OBJECTS_THREE = (
    "calibration_quadratic",
    "binomial_square",
    "quadratic",
    "binomial_cube",
    "perfect_square_trinomial",
    "circle",
    "parabola",
)


# ============================================================== the measures are imported, by identity


def test_every_measure_is_the_object_its_own_card_declares() -> None:
    """Identity, not equality: a re-implemented measure would pass ``==`` and fail this."""
    from parseatlas import pareto_atlas

    assert pareto_atlas.peak_live is origin_memory.peak_live
    assert pareto_atlas.depth is origin_depth.depth
    assert pareto_atlas.parenthesis_cost is origin_cost.parenthesis_cost
    assert pareto_atlas.manifest_set is origin_visibility.manifest_set
    assert pareto_atlas.chosen_writing is origin_visibility.chosen_writing
    assert pareto_atlas.ceiling_table is origin_space.ceiling_table
    assert pareto_atlas.CORPUS is origin_visibility.CORPUS


def test_the_axis_declaration_is_a_partition_of_costs_and_one_benefit() -> None:
    assert COST_AXES | BENEFIT_AXES == set(AXES)
    assert not COST_AXES & BENEFIT_AXES
    assert BENEFIT_AXES == {"visibility"}
    assert COST_AXES == {"brackets", "depth", "peak_live"}
    assert set(AXES_3) < set(AXES_4)
    assert set(AXES_4) == set(AXES)
    assert set(AXES_4) - set(AXES_3) == {"peak_live"}


# ================================================================== the sign, pinned by hand


def test_visibility_alone_decides_dominance_and_it_decides_it_upwards() -> None:
    """The hand-built pair the card asks for: everything ties but the benefit axis.

    ``left`` and ``right`` agree on all three costs and differ only in visibility, where ``left``
    shows one property more.  More manifest properties is BETTER, so ``left`` dominates ``right``
    and never the reverse.  Treating visibility as a cost inverts exactly this assertion, which is
    why it is pinned here and not only in a total.
    """
    left = Profile(brackets=2, depth=3, peak_live=3, visibility=4)
    right = Profile(brackets=2, depth=3, peak_live=3, visibility=3)
    assert dominates(vector(left, AXES_4), vector(right, AXES_4), AXES_4)
    assert not dominates(vector(right, AXES_4), vector(left, AXES_4), AXES_4)
    assert dominates(vector(left, AXES_3), vector(right, AXES_3), AXES_3)
    # and dropping the axis that carries the difference makes the pair incomparable, not ordered
    two = ("brackets", "depth")
    assert not dominates(vector(left, two), vector(right, two), two)
    assert not dominates(vector(right, two), vector(left, two), two)


def test_each_cost_axis_decides_dominance_downwards() -> None:
    base = Profile(brackets=2, depth=3, peak_live=3, visibility=3)
    for axis, better in (
        ("brackets", Profile(1, 3, 3, 3)),
        ("depth", Profile(2, 2, 3, 3)),
        ("peak_live", Profile(2, 3, 2, 3)),
    ):
        assert axis in COST_AXES
        assert dominates(vector(better, AXES_4), vector(base, AXES_4), AXES_4)
        assert not dominates(vector(base, AXES_4), vector(better, AXES_4), AXES_4)


def test_a_mixed_pair_is_incomparable_and_an_equal_pair_is_not_dominated() -> None:
    cheap = Profile(brackets=0, depth=6, peak_live=3, visibility=4)
    shallow = Profile(brackets=3, depth=3, peak_live=3, visibility=3)
    assert not dominates(vector(cheap, AXES_4), vector(shallow, AXES_4), AXES_4)
    assert not dominates(vector(shallow, AXES_4), vector(cheap, AXES_4), AXES_4)
    same = vector(cheap, AXES_4)
    assert not dominates(same, same, AXES_4)


def test_an_axis_set_is_normalised_and_a_bad_one_is_refused() -> None:
    left = Profile(1, 2, 3, 4)
    assert vector(left, ("visibility", "brackets")) == vector(left, ("brackets", "visibility"))
    for bad in ((), ("brackets", "brackets"), ("bracket",)):
        try:
            vector(left, bad)
        except ValueError:
            continue
        raise AssertionError(f"axis set {bad!r} should have been refused")


# ============================================================ the space is 0039's, and unbounded


def test_the_writing_space_is_0039s_and_no_bound_was_applied() -> None:
    provenance = space_provenance()
    assert provenance["space_total"] == FULL_SPACE_TREES
    assert provenance["trees_probed"] == FULL_SPACE_TREES
    assert provenance["no_bound_applied"]
    assert provenance["same_object_trees"] == REPRESENTATIONS
    assert provenance["representations_match_0039"]
    # the exact-rational probe discarded nothing SymPy would have kept back
    assert provenance["probe_survivors"] == REPRESENTATIONS
    assert provenance["probe_discarded_nothing_sympy_would_keep"]


def test_writings_of_returns_same_object_trees_including_the_declared_ones() -> None:
    item = OBJECT_BY_NAME["calibration_quadratic"]
    reps = writings_of(item)
    assert len(reps) == 5
    assert all(isinstance(rep, Representation) for rep in reps)
    declared = {natural_writing(item, world) for world in GRAMMARS}
    assert declared <= set(reps)
    for rep in reps:
        assert representation_tree(rep) is not None


# ====================================================== object counts and cell counts, separately


def test_object_counts_are_object_counts() -> None:
    counts = cell_count()
    assert counts["objects"] == OBJECTS
    assert counts["declared_writings"] == DECLARED_WRITINGS
    assert counts["objects"] == len(CORPUS)
    # 34 objects, not 34 x 25: no world multiplier may reach an object count
    assert counts["objects"] != counts["objects"] * counts["worlds"]


def test_cell_counts_are_cell_counts_and_are_a_different_number() -> None:
    counts = cell_count()
    assert counts["representations"] == REPRESENTATIONS
    assert counts["worlds"] == WORLDS
    assert counts["cells"] == CELLS
    assert counts["cells"] == counts["representations"] * counts["worlds"]
    assert counts["cells"] != counts["objects"]
    assert counts["representations"] != counts["objects"]


# =================================================================== the correctness bridge


def test_round_trip_over_the_whole_grid() -> None:
    """Counted forwards: 16675 round trips WITNESSED, not 0 counterexamples missed."""
    audit = round_trip_audit()
    assert audit["cells"] == CELLS
    assert audit["verified"] == CELLS
    assert audit["failure_count"] == 0
    assert audit["failures"] == ()


def test_every_bracket_in_every_rendering_is_required() -> None:
    """Also counted forwards: 88171 brackets each carrying a deletion witness.

    An audit that only reports a surplus reads the same whether the detector fired or never ran,
    so the number pinned here is the count of brackets PROVED required.
    """
    audit = minimality_audit()
    assert audit["cells"] == CELLS
    assert audit["brackets_checked"] == 88_171
    assert audit["brackets_required"] == 88_171
    assert audit["surplus_count"] == 0
    assert audit["surplus"] == ()


# =============================================================== dominance is a partial order


def test_dominance_is_a_strict_partial_order_on_the_computed_relation() -> None:
    """Irreflexive, antisymmetric and transitive, checked and not assumed.

    Transitivity is quantified over the distinct criteria vectors of each object rather than over
    its writings.  Dominance is a function of the vector alone, so the two quantifications are
    equivalent; one object here has 502 writings and 50 distinct vectors, and the unreduced walk
    would be 126 million comparisons of the same 50 tuples.  The distinct-vector count is asserted
    so the reduction is auditable rather than a claim.
    """
    for axes, distinct in ((AXES_3, 135), (AXES_4, 154)):
        audit = order_audit(axes)
        assert audit["irreflexive"], audit["reflexive_violations"]
        assert audit["antisymmetric"], audit["antisymmetric_violations"]
        assert audit["transitive"], audit["transitive_violations"]
        assert audit["pairs_checked"] == PAIRS
        assert audit["distinct_vectors"] == distinct


def test_no_frontier_point_is_dominated_and_no_dominated_writing_is_optimal() -> None:
    for axes in (AXES_3, AXES_4):
        audit = frontier_audit(axes)
        assert audit["checked"] == REPRESENTATIONS
        assert audit["dominated_on_frontier"] == ()
        assert audit["optimal_off_frontier"] == ()
        assert audit["clean"]


def test_the_four_axis_frontier_contains_the_three_axis_frontier_per_object() -> None:
    """Asserted per object, and asserted as a measurement rather than as a theorem.

    Adding an axis does NOT in general enlarge a Pareto frontier: two writings that tie on every
    axis of the smaller set and differ on the added one become ordered, and the loser leaves the
    frontier.  ``pairs_at_risk`` counts exactly those pairs -- there are 1541 of them -- so the
    containment below is a fact about this corpus and the risk it survived is on the record.
    """
    audit = containment_audit()
    assert audit["contained_everywhere"]
    assert audit["failures"] == ()
    for row in audit["rows"]:
        three = frozenset(frontier(row["object"], AXES_3))
        four = frozenset(frontier(row["object"], AXES_4))
        assert three <= four, row["object"]
        assert len(four) >= len(three), row["object"]
    assert audit["three_total"] == OPTIMAL_THREE
    assert audit["four_total"] == OPTIMAL_FOUR
    assert audit["enlargement_total"] == OPTIMAL_FOUR - OPTIMAL_THREE == 9
    assert audit["objects_enlarged"] == 7
    assert audit["objects_unchanged"] == 27
    assert audit["objects_shrunk"] == 0
    assert audit["pairs_at_risk"] == 1541
    assert audit["pairs_at_risk_on_the_three_axis_frontier"] == 0


def test_more_axes_does_not_in_general_mean_a_bigger_frontier() -> None:
    """The counterexample, named, so the containment above is not read as a law.

    ``calibration_quadratic`` has three writings of minimal depth; adding the bracket axis orders
    two of them behind a third and the frontier shrinks from 3 to 2.  The lost writing is
    ``2 * (x * x) + (3 * x - 5)`` at ``(brackets 2, depth 3)``, beaten by ``2 * x * x + (3 * x - 5)``
    at ``(brackets 1, depth 3)``.
    """
    depth_only = frozenset(frontier("calibration_quadratic", ("depth",)))
    with_brackets = frozenset(frontier("calibration_quadratic", ("brackets", "depth")))
    assert len(depth_only) == 3
    assert len(with_brackets) == 2
    assert not depth_only <= with_brackets
    lost = {representation_text(rep) for rep in depth_only - with_brackets}
    assert "2 * (x * x) + (3 * x - 5)" in lost
    assert "2 * x * x + (3 * x - 5)" in {representation_text(rep) for rep in with_brackets}


# ======================================================================= the four headline counts


def test_headline_counts_four_axis() -> None:
    result = atlas(AXES_4)
    assert result["representations"] == REPRESENTATIONS
    assert result["optimal"] == OPTIMAL_FOUR
    assert result["dominated"] == DOMINATED_FOUR
    assert result["optimal"] + result["dominated"] == REPRESENTATIONS
    assert result["control_on_frontier"] == CONTROL_ON_FRONTIER
    assert result["control_dominated"] == CONTROL_DOMINATED
    assert result["created_points"] == CREATED_FOUR
    assert result["created_objects"] == CREATED_OBJECTS_FOUR
    assert result["created_object_count"] == CREATED_FOUR
    assert (
        result["objects_with_a_distinct_natural_alternative_count"]
        == OBJECTS_WITH_AN_ALTERNATIVE
    )
    assert result["alternatives_dominated"] == OBJECTS_WITH_AN_ALTERNATIVE - CREATED_FOUR == 4


def test_headline_counts_three_axis() -> None:
    result = atlas(AXES_3)
    assert result["optimal"] == OPTIMAL_THREE
    assert result["dominated"] == DOMINATED_THREE
    assert result["optimal"] + result["dominated"] == REPRESENTATIONS
    assert result["control_on_frontier"] == CONTROL_ON_FRONTIER
    assert result["control_dominated"] == CONTROL_DOMINATED
    assert result["created_points"] == CREATED_THREE
    assert result["created_objects"] == CREATED_OBJECTS_THREE
    assert (
        result["objects_with_a_distinct_natural_alternative_count"]
        == OBJECTS_WITH_AN_ALTERNATIVE
    )
    assert result["alternatives_dominated"] == OBJECTS_WITH_AN_ALTERNATIVE - CREATED_THREE == 9


def test_the_headline_is_not_zero_and_names_the_writings_it_counts() -> None:
    """The owner's sharpest question, with the answer written out rather than summarised."""
    result = atlas(AXES_4)
    rows = {row["object"]: row for row in result["rows"]}
    assert rows["distributive_law"]["created"][0]["text"] == "a * (b + c)"
    assert rows["binomial_square"]["created"][0]["text"] == "(a + b) * (a + b)"
    assert rows["quadratic"]["created"][0]["text"] == "a * (x - r) * (x - s)"
    assert rows["line"]["created"][0]["text"] == "y1 + m * (x - x1)"
    assert (
        rows["circle"]["created"][0]["text"] == "(x - h) * (x - h) + (y - k) * (y - k)"
    )
    assert rows["linear_approximation"]["created"][0]["text"] == "fa + dfa * (x - a)"
    # and G0 writes none of them
    for name, row in rows.items():
        for created in row["created"]:
            assert created["text"] != row["control_writing"]["text"], name


def test_question_three_is_forced_by_the_bracket_axis_and_must_be_read_that_way() -> None:
    """The null model for question 3: ``G0`` cannot be dominated because it is the strict minimum.

    In all 34 objects the writing ``G0`` chooses unprompted is the UNIQUE minimum of the bracket
    axis over the whole 667-writing space, so nothing can tie it there and beat it elsewhere.  The
    answer ``34 of 34`` is therefore decided by one axis, and it is evidence about the bracket axis
    alone.  If this ever stops holding, the headline stops being forced -- and the test says so.
    """
    audit = control_bracket_minimum()
    assert audit["objects"] == OBJECTS
    assert audit["unique_minimum"] == OBJECTS
    assert audit["tied_at_the_minimum"] == 0
    assert audit["above_the_minimum"] == 0
    assert audit["forced_on_the_frontier"] == CONTROL_ON_FRONTIER


def test_in_a_foreign_reference_world_the_control_is_no_longer_forced() -> None:
    """The informative version of question 3: priced in another world's brackets, ``G0`` is dominated.

    Under ``G17`` the conventional expanded quadratic costs the same two brackets as the factored
    writing, and the factored writing is shallower and shows three properties more -- so the tie on
    the bracket axis lets the other three axes decide, and the conventional habit loses.
    """
    beaten = [
        world.id
        for world in GRAMMARS
        if control_bracket_minimum(world)["unique_minimum"] < OBJECTS
    ]
    assert "G0" not in beaten
    assert len(beaten) == 24
    sweep = reference_world_sweep()
    assert sweep["four_control_on_frontier_range"] == (29, 34)
    seventeen = next(world for world in GRAMMARS if world.id == "G17")
    audit = control_bracket_minimum(seventeen)
    assert audit["attains_minimum"] == OBJECTS
    assert audit["unique_minimum"] == 31
    result = atlas(AXES_4, seventeen)
    dominated = [row["object"] for row in result["rows"] if not row["control_on_frontier"]]
    assert dominated == ["quadratic"]
    row = next(row for row in result["rows"] if row["object"] == "quadratic")
    assert row["control_writing"]["vector"] == (2, 5, 3, 0)
    assert (2, 3, 3, 3) in {point["vector"] for point in row["frontier"]}


def test_the_reference_world_moves_the_coordinate_and_never_the_habit() -> None:
    """A foreign world prices ``G0``'s writing; it does not substitute its own.

    Under ``G01`` the two readings come apart sharply: ``G0``'s habit is the unique bracket minimum
    for 20 objects, while ``G01``'s own habit is for 32.  Reporting the second under the first's
    name would make the conventional world look far better than it is, so the writing being priced
    is asserted by role as well as by count.
    """
    one = next(world for world in GRAMMARS if world.id == "G01")
    audit = control_bracket_minimum(one)
    assert audit["unique_minimum"] == 20
    assert audit["attains_minimum"] == 22
    assert audit["tied_at_the_minimum"] == 2
    assert audit["above_the_minimum"] == 12
    assert audit["unique_minimum"] + audit["tied_at_the_minimum"] + audit[
        "above_the_minimum"
    ] == OBJECTS
    priced = {row["object"]: row["role"] for row in audit["rows"]}
    control_roles = {
        item.name: natural_writing(item, CONTROL).role for item in CORPUS
    }
    assert priced == control_roles
    # and G01 really would have written something else for these objects
    differing = [
        item.name
        for item in CORPUS
        if natural_writing(item, one).role != control_roles[item.name]
    ]
    assert len(differing) == 14
    assert "distributive_law" in differing


# ================================================================================ the null model


def test_the_null_model_names_the_objects_that_cannot_move() -> None:
    model = null_model()
    assert model["objects"] == OBJECTS
    assert model["movable_object_count"] == MOVABLE_OBJECTS
    assert model["one_vector_object_count"] == ONE_VECTOR_OBJECTS
    assert model["single_representation_object_count"] == ONE_VECTOR_OBJECTS
    assert model["movable_by_axis"] == MOVABLE_BY_AXIS
    assert model["movable_object_count"] + model["one_vector_object_count"] == OBJECTS
    assert model["movable_representations"] == REPRESENTATIONS - ONE_VECTOR_OBJECTS == 655


def test_rates_over_the_movable_set_are_reported_and_differ_from_the_pooled_ones() -> None:
    result = atlas(AXES_4)
    assert result["movable_objects"] == MOVABLE_OBJECTS
    assert result["movable_representations"] == 655
    assert result["movable_dominated"] == DOMINATED_FOUR
    assert math.isclose(result["movable_dominated_fraction"], 608 / 655)
    assert result["movable_dominated_fraction"] > result["dominated_fraction"]


def test_one_object_carries_almost_all_the_pairs_and_the_report_says_so() -> None:
    """0047 was rejected for a tail of two objects reading as fifty; this is the same hazard."""
    result = atlas(AXES_4)
    assert result["largest_object"] == "binomial_cube"
    assert math.isclose(result["largest_object_share"], 502 / 667)
    counts = incomparability(AXES_4)
    assert counts["largest_object"] == "binomial_cube"
    assert counts["largest_object_pair_share"] > 0.98


# ================================================================== the partial order over writings


def test_incomparability_sums_to_the_pair_count_per_object_and_in_total() -> None:
    for axes, ordered, incomparable, equal in (
        (AXES_3, ORDERED_THREE, INCOMPARABLE_THREE, EQUAL_THREE),
        (AXES_4, ORDERED_FOUR, INCOMPARABLE_FOUR, EQUAL_FOUR),
    ):
        counts = incomparability(axes)
        assert counts["pairs"] == PAIRS
        assert counts["ordered"] == ordered
        assert counts["incomparable"] == incomparable
        assert counts["equal"] == equal
        assert counts["sums"]
        assert counts["all_rows_sum"]
        for row in counts["rows"]:
            expected = row["representations"] * (row["representations"] - 1) // 2
            assert row["pairs"] == expected, row["object"]
            assert row["ordered"] + row["incomparable"] + row["equal"] == expected


def test_a_total_ranking_would_have_to_invent_more_than_half_the_order_at_four_axes() -> None:
    four = incomparability(AXES_4)
    three = incomparability(AXES_3)
    assert math.isclose(four["invented_fraction"], (INCOMPARABLE_FOUR + EQUAL_FOUR) / PAIRS)
    assert four["invented_fraction"] > 0.5
    assert three["invented_fraction"] < 0.5
    # the pooled figure is one object's figure; the per-object mean is reported beside it
    assert math.isclose(four["per_object_mean_invented"], 0.4317276925073284, rel_tol=1e-9)
    assert math.isclose(three["per_object_mean_invented"], 0.22739485148889446, rel_tol=1e-9)


def test_the_pairwise_classes_agree_with_a_direct_walk_on_a_small_object() -> None:
    """The grouped count is a reduction, so it is checked against the unreduced walk."""
    name = "quadratic"
    reps = writings_of(OBJECT_BY_NAME[name])
    values = {rep: vector(profile(rep, CONTROL), AXES_4) for rep in reps}
    ordered = equal = incomparable = 0
    for left, right in itertools.combinations(reps, 2):
        if values[left] == values[right]:
            equal += 1
        elif dominates(values[left], values[right], AXES_4) or dominates(
            values[right], values[left], AXES_4
        ):
            ordered += 1
        else:
            incomparable += 1
    row = next(row for row in incomparability(AXES_4)["rows"] if row["object"] == name)
    assert (row["ordered"], row["incomparable"], row["equal"]) == (
        ordered,
        incomparable,
        equal,
    )
    assert (ordered, incomparable, equal) == (34, 5, 6)


# ============================================================================= the sweeps


def test_the_axis_lattice_is_published_whole_and_is_not_monotone() -> None:
    lattice = axis_lattice()
    assert lattice["sizes"]["brackets"] == 34
    assert lattice["sizes"]["depth"] == 65
    assert lattice["sizes"]["peak_live"] == 475
    assert lattice["sizes"]["visibility"] == 179
    assert lattice["sizes"]["brackets+depth+visibility"] == OPTIMAL_THREE
    assert lattice["sizes"]["brackets+depth+peak_live+visibility"] == OPTIMAL_FOUR
    assert len(lattice["sizes"]) == 15
    assert lattice["non_monotone_pairs"] == 26
    assert lattice["sharpest_loss"]["subset"] == ("peak_live",)
    assert lattice["sharpest_loss"]["superset"] == ("brackets", "peak_live")
    assert lattice["sharpest_loss"]["loss"] == 432


def test_the_reference_world_sweep_publishes_the_spread_not_a_default() -> None:
    sweep = reference_world_sweep()
    assert sweep["worlds"] == WORLDS
    assert sweep["four_optimal_range"] == (52, 66)
    assert sweep["three_optimal_range"] == (46, 57)
    assert sweep["four_created_range"] == (12, 15)
    assert sweep["three_created_range"] == (7, 14)
    control = next(row for row in sweep["rows"] if row["world"] == "G0")
    assert control["four_optimal"] == OPTIMAL_FOUR
    assert control["four_created"] == CREATED_FOUR
    assert control["three_created"] == CREATED_THREE
    # the control's own coordinates are the FRIENDLIEST to the control: nowhere is `created` smaller
    assert control["four_created"] == sweep["four_created_range"][0]


def test_the_size_curve_is_published_over_its_whole_range_and_turns() -> None:
    curve = size_curve()
    sizes = [row["representations"] for row in curve["rows"]]
    assert sizes == [1, 2, 3, 4, 5, 6, 10, 37, 42, 502]
    assert curve["rows"][0]["objects"] == ONE_VECTOR_OBJECTS
    assert math.isclose(curve["rows"][0]["mean_optimal_fraction"], 1.0)
    assert math.isclose(curve["rows"][-1]["mean_optimal_fraction"], 3 / 502)
    assert not curve["monotone"]
    assert curve["rise_count"] == 2
    assert [(rise["from"], rise["to"]) for rise in curve["rises"]] == [(3, 4), (6, 10)]


def test_the_sign_control_measures_what_a_sign_error_would_have_cost() -> None:
    for axes, correct, inverted in ((AXES_3, OPTIMAL_THREE, 61), (AXES_4, OPTIMAL_FOUR, 68)):
        control = sign_control(axes)
        assert control["correct_optimal"] == correct
        assert control["inverted_optimal"] == inverted
        assert control["difference"] == inverted - correct
        # and the inversion is INVISIBLE in question 3, which is why the pin above is by hand
        assert control["correct_control_on_frontier"] == CONTROL_ON_FRONTIER
        assert control["inverted_control_on_frontier"] == CONTROL_ON_FRONTIER


# ==================================================================== the multicore decision


def test_worker_count_is_derived_from_the_observed_core_count_with_headroom() -> None:
    assert worker_count_for(16, 44) == 12
    assert worker_count_for(4, 44) == 2
    assert worker_count_for(1, 44) == 1
    assert worker_count_for(16, 3) == 3
    assert default_worker_count(44) == worker_count_for(__import__("os").cpu_count() or 1, 44)


def test_the_measured_decision_for_this_grid_is_sequential_and_the_crossover_is_named() -> None:
    """A sequential path is a valid outcome; the measurement is what justifies it.

    At the declared floor constants the pool pays for itself above ``17225`` cells, and this corpus
    has ``16675``.  The floor is declared rather than the typical startup cost because a smaller
    startup is the reading that FAVOURS the pool, and the pool still loses.
    """
    workers = 12
    crossover = POOL_STARTUP_SECONDS / (CELL_SECONDS * (1 - 1 / workers))
    assert math.ceil(crossover) == 17_225
    assert not should_parallelise(CELLS, CELL_SECONDS, workers)
    assert should_parallelise(17_300, CELL_SECONDS, workers)
    assert not should_parallelise(CELLS, CELL_SECONDS, 1)


def test_sequential_and_parallel_produce_the_same_grid() -> None:
    reps = tuple(rep for item in CORPUS for rep in writings_of(item))
    payloads = _chunks(reps)
    assert len(payloads) == 44
    sequential = _map_chunks(payloads, workers=1)
    parallel = _map_chunks(payloads, workers=4)
    assert sequential == parallel
    assert sum(len(chunk) for chunk in sequential) == REPRESENTATIONS


# ========================================================================= the frontier itself


def test_a_frontier_point_is_a_writing_and_the_vector_is_not_compressed() -> None:
    """No weighted sum, no score, no best-representation column: the frontier is the result."""
    from parseatlas import pareto_atlas

    source = open(pareto_atlas.__file__, encoding="utf-8").read()
    for forbidden in ("weighted_sum", "def score", '"score"', "best_representation"):
        assert forbidden not in source
    assert not hasattr(Profile, "total")
    assert not hasattr(Profile, "score")


def test_the_control_writing_and_one_created_point_have_the_measured_vectors() -> None:
    grid = _grid()
    item = OBJECT_BY_NAME["distributive_law"]
    control = natural_writing(item, CONTROL)
    assert representation_text(control) == "a * b + a * c"
    assert vector(grid["profiles"][control]["G0"], AXES_4) == (0, 2, 3, 3)
    created = next(
        rep
        for rep in frontier(item, AXES_4)
        if representation_text(rep) == "a * (b + c)"
    )
    assert vector(grid["profiles"][created]["G0"], AXES_4) == (1, 2, 2, 2)
    # 3 axes order the pair; the fourth is what pulls the factored writing onto the frontier
    assert dominates(
        vector(grid["profiles"][control]["G0"], AXES_3),
        vector(grid["profiles"][created]["G0"], AXES_3),
        AXES_3,
    )
    assert not dominates(
        vector(grid["profiles"][control]["G0"], AXES_4),
        vector(grid["profiles"][created]["G0"], AXES_4),
        AXES_4,
    )
    assert len(frontier(item, AXES_3)) == 1
    assert len(frontier(item, AXES_4)) == 2


def test_profile_agrees_with_the_grid_for_every_world_of_one_object() -> None:
    grid = _grid()
    for rep in writings_of(OBJECT_BY_NAME["line"]):
        for world in GRAMMARS:
            assert profile(rep, world) == grid["profiles"][rep][world.id]
