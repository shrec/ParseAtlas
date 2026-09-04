"""Validation of experiment 0044: the ceiling, and the criteria that fight each other.

Every number here was measured before it was written down, and every headline is pinned as a
literal rather than recomputed from the module, so a change in the result fails a test instead of
quietly rewriting the finding.

The file is ordered so that the things without which nothing else means anything come first:

* **the correctness bridge** -- round trip and minimality over the whole (writing x world) grid.  A
  bracket count is only a cost if every bracket is load-bearing, and a ``peak_live`` is only a
  property of the object's writing if the rendering reparses to the tree it came from.
* **the trap** -- for ONE fixed tree the peak is the same in every world.  This is checked, not
  assumed, because an experiment that reported it as a finding would be measuring nothing.
* **the null model** -- how many corpus entries the convention can move and how many it cannot.  A
  ranking drawn from the frozen entries is a parsing artifact.

Only then come the frontier, the sweep and the owner's scenario.
"""

from functools import lru_cache

import pytest

from parseatlas.canonical import operation_cost
from parseatlas.grammar import control_grammar
from parseatlas.manifest_properties import CORPUS as LAW_OBJECTS
from parseatlas.parser import Binary, Variable, parse
from parseatlas.memory_ceiling import (
    CHAINS,
    CHAIN_LENGTHS,
    CONTROL,
    CORPUS,
    GRAMMARS,
    GRID_CELL_SECONDS,
    POOL_STARTUP_SECONDS,
    TREE_SECONDS,
    as_formula_corpus,
    ceiling_sweep,
    chain_reference,
    cheapest_is_hungriest,
    conflict_report,
    corpus_audit,
    default_worker_count,
    depth,
    feasible,
    frontier,
    grid_audit,
    identity_audit,
    minimality_audit,
    movability,
    null_model,
    owner_scenario,
    peak_live,
    peak_live_invariance,
    round_trip_audit,
    scan,
    should_parallelise,
    worker_count_for,
    writings_of,
)


@lru_cache(maxsize=1)
def scanned() -> dict:
    return scan()


@lru_cache(maxsize=1)
def grid() -> dict:
    return grid_audit()


@lru_cache(maxsize=1)
def sweep() -> dict:
    return ceiling_sweep()


@lru_cache(maxsize=1)
def owner() -> dict:
    return owner_scenario()


@lru_cache(maxsize=1)
def conflicts() -> dict:
    return conflict_report()


@lru_cache(maxsize=1)
def nulls() -> dict:
    return null_model()


def tree(source: str):
    return parse(source, control_grammar())


# --------------------------------------------------------------- the correctness bridge, first


def test_declared_sources_are_canonical_and_uniquely_named():
    audit = corpus_audit()
    assert audit["size"] == 53
    assert audit["duplicate_names"] == ()
    assert audit["canonical_sources"] is True
    assert audit["areas"] == {
        "algebra": 18,
        "associative_chain": 3,
        "calculus": 11,
        "geometry": 15,
        "linear_algebra": 6,
    }


def test_every_declared_writing_of_an_object_denotes_that_object():
    audit = identity_audit()
    assert audit["checks"] == 53
    assert audit["failures"] == 0
    assert audit["holds"] is True


def test_round_trip_holds_over_the_whole_grid():
    audit = round_trip_audit()
    assert audit["checks"] == 28575
    assert audit["failures"] == 0
    assert audit["holds"] is True


def test_every_bracket_over_the_whole_grid_is_load_bearing():
    audit = minimality_audit()
    assert audit["brackets_checked"] == 122571
    assert audit["violations"] == 0
    assert audit["minimal"] is True


def test_the_grid_is_the_whole_writing_space_times_every_world():
    assert grid()["writings"] == 1143
    assert grid()["grammars"] == 25
    assert grid()["writings"] * grid()["grammars"] == grid()["checks"] == 28575


def test_the_trap_a_fixed_tree_has_the_same_peak_in_every_world():
    audit = peak_live_invariance()
    assert audit["checks"] == 28575
    assert audit["failures"] == 0
    assert audit["holds"] is True


# ------------------------------------------------------------------------- peak_live by eye


def test_peak_live_of_a_leaf_is_one():
    assert peak_live(Variable("a")) == 1
    assert peak_live(tree("7")) == 1


def test_peak_live_of_one_operation_is_two():
    assert peak_live(tree("a + b")) == 2
    assert peak_live(tree("a / b")) == 2


def test_peak_live_takes_the_larger_when_the_sides_differ():
    # (a + b) has 2, c has 1: unequal, so the answer is the larger, 2.
    node = tree("a + b + c")
    assert isinstance(node, Binary)
    assert peak_live(node.left) == 2
    assert peak_live(node.right) == 1
    assert peak_live(node) == 2


def test_peak_live_adds_one_when_the_sides_are_equal():
    # (a + b) has 2 and (c + d) has 2: equal, so the answer is 3.
    node = tree("(a + b) + (c + d)")
    assert isinstance(node, Binary)
    assert peak_live(node.left) == peak_live(node.right) == 2
    assert peak_live(node) == 3


def test_the_eight_term_chain_and_the_balanced_form_by_hand():
    chain = tree("a + b + c + d + e + f + g + h")
    balanced = tree("((a + b) + (c + d)) + ((e + f) + (g + h))")
    assert (depth(chain), peak_live(chain)) == (7, 2)
    assert (depth(balanced), peak_live(balanced)) == (3, 4)


def test_halving_the_critical_path_doubles_the_memory():
    reference = chain_reference(8)
    assert reference["chain"]["depth"] == 7
    assert reference["chain"]["peak_live"] == 2
    assert reference["balanced"]["depth"] == 3
    assert reference["balanced"]["peak_live"] == 4
    assert reference["halving_the_path_doubles_the_memory"] is True


def test_depth_counts_operator_levels_and_is_one_below_experiment_0021():
    for source in ("a", "a + b", "a + b + c", "(a + b) * (c + d)", "a + b + c + d + e + f + g + h"):
        node = tree(source)
        assert depth(node) + 1 == operation_cost(node)["depth"]
    assert depth(Variable("a")) == 0


# ---------------------------------------------------------------------------- the null model


def test_no_world_writes_a_balanced_eight_term_sum_bracket_free():
    reference = chain_reference(8)
    assert reference["balanced"]["bracket_free_worlds"] == ()
    assert reference["balanced"]["costs"] == (3,)
    assert len(reference["chain"]["bracket_free_worlds"]) == 25
    assert reference["chain"]["costs"] == (0,)


def test_every_chain_is_bracket_free_flat_and_bracketed_balanced_in_all_worlds():
    for length in CHAIN_LENGTHS:
        reference = chain_reference(length)
        assert len(reference["chain"]["bracket_free_worlds"]) == 25
        assert reference["balanced"]["bracket_free_worlds"] == ()


def test_the_null_model_split_is_pinned():
    split = nulls()
    assert split["corpus_size"] == 37
    assert split["movable_count"] == 30
    assert split["frozen_count"] == 7
    assert split["tree_frozen"] == ("chain_rule", "chain_4", "chain_6", "chain_8")
    assert split["choice_frozen"] == ("binomial_square", "binomial_cube", "triangle_area")
    assert split["chains_are_frozen"] is True


def test_a_frozen_entry_adds_the_same_constant_to_every_world():
    split = movability()
    for name in split["tree_frozen"] + split["choice_frozen"]:
        for ceiling in split["ceilings_considered"]:
            rows = [row for row in writings_of(name) if row.peak_live <= ceiling]
            if not rows:
                continue
            totals = {
                grammar.id: min(row.costs[grammar.id] for row in rows) for grammar in GRAMMARS
            }
            assert len(set(totals.values())) == 1, (name, ceiling)


def test_every_ranking_is_computed_over_the_movable_set_only():
    split = movability()
    for row in sweep()["rows"]:
        assert set(row["movable_basis"]) <= set(split["movable"])
    for shift in sweep()["shifts"]:
        assert set(shift["basis"]) <= set(split["movable"])


# ------------------------------------------------------------------------- the writing space


def test_the_scan_is_pinned():
    result = scanned()
    assert result["corpus_size"] == 37
    assert result["declared_writings"] == 53
    assert result["trees_enumerated"] == 1511296
    assert result["probe_survivors"] == 1143
    assert result["probe_discarded"] == 1510153
    assert result["confirmed"] == 1143


def test_the_sympy_filter_rejects_nothing_here_and_that_is_a_corpus_fact():
    # The exact rational probe at two declared points already discards every tree that denotes a
    # different object, so SymPy confirms all 1143 survivors and rejects none.  That is a property
    # of THIS corpus, not a licence to drop the confirmation: the probe can only rule a tree out.
    assert scanned()["sympy_rejected"] == 0
    assert scanned()["confirmed"] == scanned()["probe_survivors"] == 1143


def test_the_filter_has_the_power_to_reject_and_the_probe_uses_it():
    # `sympy_rejected == 0` above is a corpus fact and NOT evidence that the confirmation works, so
    # the discriminating power is tested directly: a different parenthesization of the same word is
    # a different object, the probe throws it out, and SymPy agrees that it is not the object.
    from parseatlas.canonical import to_sympy
    from parseatlas.visibility_ceiling import same_object

    reference = to_sympy(tree("a - b + c"))
    assert same_object(tree("(a - b) + c"), reference) is True
    assert same_object(tree("a - (b + c)"), reference) is False
    # and on the real corpus the discarding is what does almost all of the work
    assert scanned()["probe_discarded"] == 1510153
    assert scanned()["probe_discarded"] > 1000 * scanned()["probe_survivors"]


def test_a_sample_of_counted_writings_denotes_the_object():
    from parseatlas.canonical import to_sympy
    from parseatlas.manifest_properties import object_tree
    from parseatlas.visibility_ceiling import same_object

    checked = 0
    for item in CORPUS:
        reference = to_sympy(object_tree(item.writings[0]))
        rows = writings_of(item)
        for row in rows[:4]:
            checked += 1
            assert same_object(row.tree, reference), (item.name, row.rendering)
    assert checked == 96


def test_the_corpus_is_0038s_corpus_plus_exactly_three_chains():
    assert CORPUS[: len(LAW_OBJECTS)] == LAW_OBJECTS
    assert CORPUS[len(LAW_OBJECTS) :] == CHAINS
    assert len(LAW_OBJECTS) == 34
    assert len(CHAINS) == 3
    assert len(CORPUS) == 37
    assert len(as_formula_corpus()) == 53


# --------------------------------------------------------------------------- the Pareto frontier


def test_a_reported_frontier_is_an_antichain():
    for row in conflicts()["frontiers"]:
        front = row["frontier"]
        for first in front:
            for second in front:
                if first is second:
                    continue
                assert not (first[0] <= second[0] and first[1] <= second[1]), row["object"]


def test_every_dominated_point_really_is_dominated():
    for row in conflicts()["frontiers"]:
        for point in row["dominated"]:
            assert any(
                other[0] <= point[0] and other[1] <= point[1] and other != point
                for other in row["frontier"]
            ), (row["object"], point)


def test_the_conflict_count_is_pinned():
    report = conflicts()
    assert report["conflict_count"] == 6
    assert report["conflicting"] == ("circle", "ellipse", "hyperbola", "chain_4", "chain_6", "chain_8")
    assert report["conflicting_movable"] == ("circle", "ellipse", "hyperbola")
    assert report["conflicting_frozen"] == ("chain_4", "chain_6", "chain_8")
    assert report["single_point_count"] == 31
    assert report["largest_frontier"] == 3
    assert report["pareto_writings"] == 226
    assert report["dominated_writings"] == 917
    assert len(report["objects_with_several_pareto_writings"]) == 18


def test_the_chain_frontier_is_re_derived_not_copied():
    row = frontier("chain_8")
    assert row["frontier"] == ((3, 4), (4, 3), (7, 2))
    assert row["dominated"] == ((5, 3), (6, 3))
    assert row["writing_count"] == 429
    assert frontier("chain_4")["frontier"] == ((2, 3), (3, 2))
    assert frontier("chain_6")["frontier"] == ((3, 3), (5, 2))


def test_the_ellipse_and_the_hyperbola_are_the_movable_conflicts():
    for name in ("ellipse", "hyperbola"):
        assert frontier(name)["frontier"] == ((3, 4), (4, 3))
    assert frontier("circle")["frontier"] == ((3, 4), (7, 3))


# ----------------------------------------------------------------------------- the ceiling sweep


def test_the_useful_ceiling_range_is_two_to_four():
    assert sweep()["ceilings"] == (2, 3, 4)
    assert sweep()["unconstrained_ceiling"] == 4


def test_the_feasibility_rows_are_pinned():
    rows = {row["ceiling"]: row for row in sweep()["rows"]}
    assert (rows[2]["feasible_objects"], rows[2]["worlds_covering_corpus"]) == (13, 0)
    assert (rows[3]["feasible_objects"], rows[3]["worlds_covering_corpus"]) == (36, 0)
    assert (rows[4]["feasible_objects"], rows[4]["worlds_covering_corpus"]) == (37, 25)
    assert rows[3]["infeasible_objects"] == ("distance_components",)
    assert rows[4]["infeasible_objects"] == ()
    assert (rows[2]["movable_feasible"], rows[3]["movable_feasible"], rows[4]["movable_feasible"]) == (
        8,
        29,
        30,
    )


def test_the_ranking_headline_values_are_pinned():
    rows = {row["ceiling"]: row for row in sweep()["rows"]}
    assert rows[4]["tiers"][0] == (12, ("G10", "G16", "G18"))
    assert rows[4]["control_total"] == 17
    assert rows[4]["control_rank"] == 6
    assert rows[3]["tiers"][0] == (10, ("G16",))
    assert rows[3]["tiers"][1] == (11, ("G15", "G18"))
    assert rows[3]["control_total"] == 15
    assert rows[3]["control_rank"] == 5
    assert rows[2]["tiers"][0] == (2, ("G02", "G08", "G09"))
    assert rows[2]["control_total"] == 8
    assert rows[2]["control_rank"] == 18


def test_the_ranking_changes_as_the_ceiling_tightens_and_it_first_changes_at_three():
    assert sweep()["first_change_ceiling"] == 3
    assert sweep()["ranking_changes"] == 2
    assert sweep()["tie_break_only"] == ()
    shifts = {shift["tight"]: shift for shift in sweep()["shifts"]}
    assert shifts[3]["basis_size"] == 29
    assert shifts[3]["tiers_changed"] is True
    assert shifts[3]["loose_tiers"][0] == (8, ("G16", "G18"))
    assert shifts[3]["tight_tiers"][0] == (10, ("G16",))
    assert shifts[3]["loose_totals"]["G10"] == 12
    assert shifts[3]["tight_totals"]["G10"] == 18
    assert (shifts[3]["control_total_loose"], shifts[3]["control_total_tight"]) == (13, 15)
    assert shifts[2]["basis_size"] == 8
    assert shifts[2]["tiers_changed"] is True
    assert (shifts[2]["control_rank_loose"], shifts[2]["control_rank_tight"]) == (7, 18)
    assert (shifts[2]["control_total_loose"], shifts[2]["control_total_tight"]) == (3, 8)


def test_a_tier_list_never_disagrees_with_its_own_ranking():
    for row in sweep()["rows"]:
        flattened = tuple(name for _total, names in row["tiers"] for name in names)
        assert sorted(flattened) == sorted(row["ranking"])
        assert len(flattened) == 25


# -------------------------------------------------------------------------- the owner's scenario


def test_feasibility_under_a_ceiling_is_world_invariant():
    strict = owner()["strict_reading"]
    assert strict["object_ceiling_checks"] == 111
    assert strict["grammar_checks"] == 2775
    assert strict["disagreement_count"] == 0
    assert strict["feasibility_is_world_invariant"] is True


def test_no_object_and_ceiling_makes_the_control_infeasible_while_another_world_can():
    # The owner's scenario in its strict reading does NOT occur on this corpus, and the empty
    # witness list is the finding rather than a missing measurement.
    assert owner()["strict_reading"]["witness_count"] == 0
    assert owner()["strict_reading"]["witnesses"] == ()


def test_what_does_occur_is_a_price_difference_and_it_is_pinned():
    report = owner()
    assert report["control_pays_count"] == 7
    assert report["others_pay_count"] == 1
    rows = {(row["object"], row["ceiling"]): row for row in report["premium_rows"]}
    assert len(rows) == 8
    assert rows[("ellipse", 3)]["control_premium"] == 1
    assert len(rows[("ellipse", 3)]["free_worlds"]) == 16
    assert rows[("hyperbola", 3)]["control_premium"] == 1
    assert len(rows[("hyperbola", 3)]["free_worlds"]) == 16
    assert rows[("circle", 3)]["control_premium"] == 0
    assert rows[("circle", 3)]["max_premium"] == 6
    assert len(rows[("circle", 3)]["paying_worlds"]) == 20


def test_the_ellipse_pays_a_bracket_to_come_under_ceiling_three():
    loose = feasible("ellipse", CONTROL, 4)
    tight = feasible("ellipse", CONTROL, 3)
    assert (loose["cost"], loose["premium"], loose["writing"]["peak_live"]) == (2, 0, 4)
    assert (tight["cost"], tight["premium"], tight["writing"]["peak_live"]) == (3, 1, 3)
    assert loose["writing"]["rendering"] == "x * x / (a * a) + y * y / (b * b)"
    assert tight["writing"]["rendering"] == "x * (x / (a * a)) + y * y / (b * b)"


def test_the_circle_is_the_reverse_case():
    control = feasible("circle", CONTROL, 3)
    other = feasible("circle", "G01", 3)
    assert (control["cost"], control["premium"]) == (0, 0)
    assert (other["cost"], other["premium"]) == (8, 6)
    assert control["writing"]["peak_live"] == other["writing"]["peak_live"] == 3


def test_an_infeasible_object_reports_no_cost():
    row = feasible("distance_components", CONTROL, 3)
    assert row["feasible"] is False
    assert row["cost"] is None
    assert row["premium"] is None
    assert row["writings_within"] == 0


def test_the_cheapest_writing_is_sometimes_exclusively_the_hungriest():
    report = cheapest_is_hungriest()
    assert report["occurs"] is True
    assert report["hits"] == 91
    assert report["cells"] == 200
    assert report["objects_considered_count"] == 8
    assert report["by_object"]["circle"] == 20
    assert report["by_object"]["linear_approximation"] == 5


# ------------------------------------------------------------------------------------ multicore


def test_the_worker_count_comes_from_the_observed_cores_and_leaves_headroom():
    assert worker_count_for(16, 400) == 12
    assert worker_count_for(4, 400) == 2
    assert worker_count_for(1, 400) == 1
    assert worker_count_for(16, 3) == 3
    assert default_worker_count(400) >= 1


def test_the_pool_decision_is_made_from_the_measured_costs():
    assert should_parallelise(1511296, TREE_SECONDS, 12) is True
    assert should_parallelise(28575, GRID_CELL_SECONDS, 12) is True
    assert should_parallelise(10, TREE_SECONDS, 12) is False
    assert should_parallelise(1511296, TREE_SECONDS, 1) is False
    assert POOL_STARTUP_SECONDS > 0 and TREE_SECONDS > 0 and GRID_CELL_SECONDS > 0


def test_sequential_and_parallel_agree_on_the_probe():
    corpus = CHAINS
    sequential = scan(corpus, workers=1, use_cache=False)
    parallel = scan(corpus, workers=3, use_cache=False)
    assert sequential == parallel
    assert sequential["trees_enumerated"] == 476
    assert sequential["confirmed"] == 476


def test_sequential_and_parallel_agree_on_the_grid():
    corpus = CHAINS
    sequential = grid_audit(corpus, workers=1, use_cache=False)
    parallel = grid_audit(corpus, workers=3, use_cache=False)
    assert sequential == parallel
    assert sequential["checks"] == 476 * 25
    assert sequential["round_trip_failures"] == ()
    assert sequential["minimality_violations"] == ()


def test_parallelism_changes_what_it_costs_and_never_what_is_produced():
    # The derived numbers, not only the raw chunks: objectives, per-world bracket costs and the
    # frontier itself have to come out identical on both paths.
    corpus = tuple(item for item in CORPUS if item.name in {"ellipse", "hyperbola", "chain_4"})
    sequential = scan(corpus, workers=1, use_cache=False)["objects"]
    parallel = scan(corpus, workers=4, use_cache=False)["objects"]
    assert sequential == parallel
    for name, rows in sequential.items():
        points = sorted({(row.depth, row.peak_live) for row in rows})
        assert points == sorted({(row.depth, row.peak_live) for row in parallel[name]})
        assert [row.costs for row in rows] == [row.costs for row in parallel[name]]
    assert frontier("ellipse")["frontier"] == ((3, 4), (4, 3))


# --------------------------------------------------------------------------------- guard rails


def test_an_unknown_world_is_an_error_not_a_default():
    with pytest.raises(KeyError):
        feasible("chain_4", "G99", 3)


def test_an_unknown_object_is_an_error_not_a_default():
    with pytest.raises(KeyError):
        writings_of("no_such_object")
