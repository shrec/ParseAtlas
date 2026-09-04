"""Experiment 0043: reachability outranks cost.

The order of this file is the order the argument has to be defended in.  The correctness bridge
comes first, because a reachability verdict about a rendering that does not re-parse to its own
tree is a verdict about nothing.  Then soundness: no task may be called reachable on a witness that
does not actually satisfy it, or whose manifest claims ground truth denies.  Only after both does
anything measure conventions.

Every headline number is pinned LITERALLY rather than recomputed from the module, so a change in
the result fails a test instead of silently rewriting the report.
"""

from __future__ import annotations

import math
from itertools import combinations

import pytest

from parseatlas import manifest_properties as mp
from parseatlas import reachability_first as rf
from parseatlas.reachability_first import (
    BRACKET_BUDGET,
    BUDGET_SWEEP,
    CELL_SECONDS,
    CONTROL,
    CORPUS,
    FACTOR_BLIND_EXPECTED,
    GRAMMARS,
    POOL_STARTUP_SECONDS,
    REGIMES,
    REQUIREMENTS,
    TASK_KINDS,
    Task,
    budget_sweep,
    ceiling_crosscheck,
    cost_ranking,
    cost_vs_reach,
    default_worker_count,
    dominance,
    factor_blindness,
    grid_index,
    reachability_table,
    reachable,
    should_parallelise,
    slow_but_possible,
    tasks,
    witness_audit,
    worker_count_for,
)


# ------------------------------------------------------------------------------------- fixtures


@pytest.fixture(scope="module")
def index():
    return grid_index()


@pytest.fixture(scope="module")
def costs():
    return cost_ranking()


@pytest.fixture(scope="module")
def transparent(index):
    return reachability_table(index=index)


@pytest.fixture(scope="module")
def opaque(index):
    return reachability_table(regime="opaque", index=index)


@pytest.fixture(scope="module")
def sweep(index):
    return budget_sweep(index=index)


# --------------------------------------------------------------- 1. the correctness bridge, first


def test_bridge_round_trip_and_minimality_over_the_whole_grid():
    """Nothing below means anything unless every rendering re-parses and carries no free bracket."""
    audit = rf.bridge()
    assert audit["round_trip"]["checks"] == 1250
    assert audit["round_trip"]["failures"] == 0
    assert audit["round_trip"]["holds"] is True
    assert audit["minimality"]["brackets_checked"] == 1811
    assert audit["minimality"]["violations"] == 0
    assert audit["minimality"]["minimal"] is True
    assert audit["surface_mirror"]["checks"] == 1250
    assert audit["surface_mirror"]["failures"] == 0


def test_grid_index_covers_every_writing_in_every_world(index):
    assert index["cells"] == 1250
    assert len(index["objects"]) == 34
    assert len(index["grammars"]) == 25
    assert len(index["cost"]) == 1250
    assert len(index["manifest"]["transparent"]) == 1250
    assert len(index["manifest"]["opaque"]) == 1250
    assert len(index["default"]) == 34 * 25


def test_index_cost_agrees_with_render(index):
    """The cost the budget is compared against is ``render``'s own bracket count, not a recount."""
    from parseatlas.notational_cost import render

    for item in CORPUS:
        for writing in item.writings:
            tree = mp.object_tree(writing)
            for grammar in GRAMMARS:
                key = (item.name, writing.role, grammar.id)
                text = render(tree, grammar)
                assert index["cost"][key] == text.count("(")
                assert index["text"][key] == text


# --------------------------------------------------------- 2. soundness: manifest implies true


def test_reachable_never_reports_a_witness_that_does_not_satisfy_the_task(index):
    """The sweep 0038 runs for ``manifest => true``, recounted over the witnesses THIS module picks.

    Every reachable cell, in both regimes, at every budget: the witness must satisfy the
    requirement, must be within the budget, and every property it makes manifest must be one ground
    truth confirms.
    """
    audit = witness_audit(index=index)
    assert audit["checks"] == 71246
    assert audit["claims"] == 229493
    assert audit["violations"] == ()
    assert audit["sound"] is True


def test_every_task_asks_only_for_properties_that_are_true():
    """A task that asked a world to show something false would be a defect, not a finding."""
    for task in tasks():
        item = mp.OBJECT_BY_NAME[task.object]
        truth = set(mp.ground_truth(mp.object_tree(item.writings[0]), item.variable))
        for name in task.properties:
            assert name in truth, f"{task.name} asks for a property ground truth denies"


def test_the_rules_are_imported_by_identity_not_copied():
    """A copied rule set would pass an equality check and quietly drift from 0038."""
    assert rf.PROPERTIES is mp.PROPERTIES
    assert rf.manifest_set is mp.manifest_set
    assert rf.ground_truth is mp.ground_truth
    assert rf.CORPUS is mp.CORPUS
    assert rf.GRAMMARS is mp.GRAMMARS
    assert rf.CONTROL is mp.CONTROL


# --------------------------------------------------------------------------- 3. the task corpus


def test_task_count_and_kinds():
    built = tasks()
    assert len(built) == 481
    assert sum(1 for task in built if task.kind == "property") == 140
    assert sum(1 for task in built if task.kind == "property_pair") == 307
    assert sum(1 for task in built if task.kind == "writable") == 34
    assert len({task.name for task in built}) == 481


def test_every_requirement_kind_has_a_named_rule():
    assert TASK_KINDS == ("property", "property_pair", "writable")
    assert tuple(item.rule for item in REQUIREMENTS) == (
        "manifest_in_some_writing",
        "simultaneous_in_one_writing",
        "within_bracket_budget",
    )
    for item in REQUIREMENTS:
        assert item.prose.strip()


def test_property_pair_demands_one_writing_and_not_two():
    """The pair rule is where 0038 found the hard limits; it must not be satisfiable by a union."""
    pair = REQUIREMENTS[1]
    assert pair.kind == "property_pair"
    assert pair.holds(frozenset({"degree", "roots"}), ("degree", "roots")) is True
    assert pair.holds(frozenset({"degree"}), ("degree", "roots")) is False
    assert pair.holds(frozenset({"roots"}), ("degree", "roots")) is False


# ------------------------------------------------- 4. the factor-blind five and the cost podium


def test_factor_structure_blindness_is_pinned_literally(index):
    """Re-derived here, not quoted from 0038, and then asserted to agree with it."""
    result = factor_blindness(index=index)
    assert result["blind"] == ("G0", "G15", "G16", "G18", "G24")
    assert result["blind"] == FACTOR_BLIND_EXPECTED
    assert result["matches_0038"] is True
    assert result["blind_count"] == 5
    assert result["sighted_count"] == 20


def test_the_0037_cost_podium_is_pinned_literally(index):
    """Rank three is a TIE, so the podium holds four worlds and 'the three cheapest' is not a set."""
    result = factor_blindness(index=index)
    assert result["podium"] == ("G18", "G16", "G0", "G10")
    assert result["podium_size"] == 4
    ranking = cost_ranking()
    assert ranking["totals"]["G18"] == 42
    assert ranking["totals"]["G16"] == 44
    assert ranking["totals"]["G0"] == 45
    assert ranking["totals"]["G10"] == 45
    assert ranking["ranks"]["G0"] == 3
    assert ranking["ranks"]["G10"] == 3


def test_the_overlap_between_podium_and_blindness_is_not_total(index):
    """The card's headline as stated does not survive: G10 is on the podium and is NOT blind."""
    result = factor_blindness(index=index)
    assert result["overlap"] == ("G18", "G16", "G0")
    assert result["overlap_count"] == 3
    assert result["podium_outside_blind"] == ("G10",)
    assert result["overlap_total"] is False


def test_cost_selects_factor_blind_conventions_by_how_much(index):
    """What survives the correction, as a number: the blind five are far cheaper than the rest."""
    result = factor_blindness(index=index)
    assert result["blind_cost_ranks"] == {"G0": 3, "G15": 5, "G16": 2, "G18": 1, "G24": 10}
    assert result["mean_cost_rank_blind"] == pytest.approx(4.2)
    assert result["mean_cost_rank_sighted"] == pytest.approx(15.05)
    assert result["mean_cost_total_blind"] == pytest.approx(46.8)
    assert result["mean_cost_total_sighted"] == pytest.approx(75.15)


# ----------------------------------------------------------------------- 5. the three-way split


def test_three_way_split_is_pinned(transparent):
    """The null model first: only the routable set can order conventions."""
    assert transparent["tasks"] == 481
    assert transparent["reachable_everywhere"] == 140
    assert transparent["reachable_nowhere"] == 236
    assert transparent["routable"] == 105
    assert (
        transparent["reachable_everywhere"]
        + transparent["reachable_nowhere"]
        + transparent["routable"]
        == 481
    )


def test_three_way_split_by_kind_is_pinned(transparent):
    assert transparent["split_by_kind"] == {
        "property": {"everywhere": 53, "nowhere": 46, "routable": 41},
        "property_pair": {"everywhere": 60, "nowhere": 190, "routable": 57},
        "writable": {"everywhere": 27, "nowhere": 0, "routable": 7},
    }


def test_expensive_is_never_reported_as_impossible(transparent):
    """The two blocking reasons are separate columns and are never summed."""
    assert transparent["blocked_cells"] == {"no_witness": 5900, "budget": 1006}
    assert transparent["nowhere_blocked"] == {"no_witness": 236, "budget": 0, "mixed": 0}
    # Nothing is unreachable in EVERY world merely because of the budget: the ceiling is a fact
    # about the shape rules, and the budget only ever separates one world from another.
    assert transparent["nowhere_blocked"]["budget"] == 0


def test_the_ceiling_cross_checks_against_0039s_forty_six(index):
    """Computed by a different route from 0038's and required to give the same forty-six pairs."""
    result = ceiling_crosscheck(index=index)
    assert result["ours_count"] == 46
    assert result["theirs_count"] == 46
    assert result["agree"] is True
    assert result["pair_tasks_nowhere"] == 190
    assert result["writable_tasks_nowhere"] == 0


# -------------------------------------------------------------- 6. the answer to the owner


def test_tasks_unreachable_in_g0_but_reachable_elsewhere_are_pinned_by_name(transparent):
    """The card's first headline question, pinned so it cannot drift."""
    assert transparent["control_gap_count"] == 6
    assert tuple(entry["name"] for entry in transparent["control_gap"]) == (
        "binomial_cube:roots",
        "binomial_cube:factor_structure",
        "binomial_cube:degree+roots",
        "binomial_cube:degree+factor_structure",
        "binomial_cube:roots+factor_structure",
        "distance_components:writable",
    )
    for entry in transparent["control_gap"]:
        assert entry["world_count"] == 12
        assert entry["cheapest_cost"] == 0
        assert entry["control_blocked_by"] == "budget"


def test_the_binomial_cube_is_pinned_with_its_witness_writing(index):
    """One task, end to end: what G0 cannot do, what G01 does for nothing, and the string itself."""
    task = Task("binomial_cube", "property", ("roots",))
    control = reachable(task, "G0", index=index)
    assert control.reachable is False
    assert control.blocked_by == "budget"
    assert control.witness is None
    assert control.default_role == "expanded"
    assert control.default_cost == 0

    other = reachable(task, "G01", index=index)
    assert other.reachable is True
    assert other.witness == "factored"
    assert other.cost == 0
    assert other.free is True
    assert other.premium == 0
    assert index["text"][("binomial_cube", "factored", "G01")] == "a + b * a + b * a + b"
    assert index["text"][("binomial_cube", "factored", "G0")] == "(a + b) * (a + b) * (a + b)"
    assert index["cost"][("binomial_cube", "factored", "G0")] == 3 > BRACKET_BUDGET


def test_distance_components_is_not_writable_in_g0_within_budget(index):
    task = Task("distance_components", "writable", ())
    control = reachable(task, "G0", index=index)
    assert control.reachable is False
    assert control.blocked_by == "budget"
    assert index["cost"][("distance_components", "squared", "G0")] == 4
    other = reachable(task, "G09", index=index)
    assert other.reachable is True
    assert other.cost == 0
    assert (
        index["text"][("distance_components", "squared", "G09")]
        == "x2 - x1 * x2 - x1 + y2 - y1 * y2 - y1"
    )


def test_reachable_works_without_a_precomputed_index(index):
    """The public entry point must stand alone; the index is only a speed-up."""
    task = Task("binomial_cube", "property", ("roots",))
    for grammar_id in ("G0", "G01", "G18"):
        assert reachable(task, grammar_id) == reachable(task, grammar_id, index=index)
    grammar = next(item for item in GRAMMARS if item.id == "G01")
    assert reachable(task, grammar, index=index) == reachable(task, "G01", index=index)


def test_reachable_rejects_an_unknown_regime(index):
    with pytest.raises(ValueError):
        reachable(Task("binomial_cube", "writable", ()), "G0", regime="translucent", index=index)


# ------------------------------------------------------------------------ 7. the partial order


def test_dominance_is_a_strict_partial_order(transparent):
    """Antisymmetry and transitivity are ASSERTED over the whole relation, not assumed."""
    order = dominance(transparent)
    relation = set(order["relation"])
    for first, second in relation:
        assert first != second, "irreflexive"
        assert (second, first) not in relation, "antisymmetric"
    for first, second in relation:
        for third_first, third_second in relation:
            if second == third_first:
                assert (first, third_second) in relation, "transitive"


def test_dominance_maximal_elements_are_pinned(transparent):
    order = dominance(transparent)
    assert order["maximal"] == (
        "G0",
        "G01",
        "G03",
        "G04",
        "G07",
        "G09",
        "G10",
        "G15",
        "G16",
        "G18",
    )
    assert order["control_is_maximal"] is True
    assert order["control_dominated_by"] == ()
    assert order["control_dominates"] == ("G13", "G14", "G17", "G23", "G24")


def test_the_order_is_genuinely_partial_and_not_a_disguised_total_order(transparent):
    order = dominance(transparent)
    assert order["total_pairs"] == 300
    assert order["comparable_pairs"] == 46
    assert order["incomparable_pairs"] == 243
    assert order["equal_pairs"] == 11
    assert (
        order["comparable_pairs"] + order["incomparable_pairs"] + order["equal_pairs"] == 300
    )
    assert order["distinct_reach_sets"] == 18
    assert order["reach_set_groups"][0] == (99, ("G0", "G15", "G16", "G18"))


def test_dominance_is_computed_over_the_routable_set_only(transparent):
    """A task everyone reaches or nobody reaches cannot separate two worlds, so it is excluded."""
    order = dominance(transparent)
    assert order["routable"] == 105
    assert max(order["reach_sets"].values()) <= 105


# ------------------------------------------------------------------------- 8. cost versus reach


def test_cost_and_reach_rankings_disagree_by_a_measured_amount(transparent, costs):
    result = cost_vs_reach(transparent, costs)
    assert result["spearman"] == pytest.approx(0.8911, abs=5e-5)
    assert result["agree"] is False
    assert result["max_displacement"] == 6
    assert result["mean_absolute_displacement"] == pytest.approx(3.12)
    assert result["control"] == {
        "id": "G0",
        "cost_rank": 3,
        "cost_total": 45,
        "reach": 99,
        "reach_rank": 1,
        "displacement": -2,
    }


def test_no_world_is_cheap_and_weak_or_dear_and_strong_at_the_declared_gap(transparent, costs):
    """At the declared threshold both lists are empty; the extremes are reported by name anyway."""
    result = cost_vs_reach(transparent, costs)
    assert result["rank_gap"] == 8
    assert result["cheap_and_weak"] == ()
    assert result["dear_and_strong"] == ()
    assert result["cheapest_relative_to_reach"] == ("G10", "G21", "G11")
    assert result["largest_positive_displacement"] == 5
    assert result["strongest_relative_to_cost"] == ("G03",)
    assert result["largest_negative_displacement"] == -6


def test_no_dear_world_out_reaches_every_cheap_one_but_twelve_reach_past_the_podium(
    transparent, costs
):
    """Headline five: not domination, but routing - and every world that does it is dear."""
    result = cost_vs_reach(transparent, costs)
    assert result["podium"] == ("G0", "G10", "G16", "G18")
    assert result["strictly_out_reaching_podium"] == ()
    assert result["beyond_podium_worlds"] == (
        "G01",
        "G02",
        "G03",
        "G04",
        "G05",
        "G06",
        "G07",
        "G08",
        "G11",
        "G19",
        "G20",
        "G21",
    )
    assert result["beyond_podium_max"] == 5
    assert min(result["beyond_podium_cost_ranks"]) == 14


# ---------------------------------------------------------------- 9. the owner's exact scenario


def test_slow_but_possible_is_pinned(transparent, costs, index):
    """The 'even if it is slow' premium, measured - and it turns out to be negative."""
    result = slow_but_possible(transparent, costs, index=index)
    assert result["count"] == 6
    assert result["control_reachable_tasks"] == 239
    assert result["control_mean_cost"] == pytest.approx(0.6109, abs=5e-5)
    assert result["control_cost_distribution"] == {0: 158, 1: 16, 2: 65}
    assert result["mean_cost_elsewhere"] == pytest.approx(0.0)
    assert result["mean_premium"] == pytest.approx(-0.6109, abs=5e-5)
    assert result["all_cheaper_elsewhere"] is True


def test_slow_but_possible_names_the_cheapest_world_and_the_witness_text(
    transparent, costs, index
):
    result = slow_but_possible(transparent, costs, index=index)
    first = result["entries"][0]
    assert first["name"] == "binomial_cube:roots"
    assert first["cheapest_world"] == "G01"
    assert first["cheapest_world_cost_rank"] == 17
    assert first["cost_there"] == 0
    assert first["witness"] == "factored"
    assert first["witness_text"] == "a + b * a + b * a + b"
    assert first["control_cost_if_budget_lifted"] == 3
    assert first["best_cost_rank_that_reaches"] == 14

    last = result["entries"][-1]
    assert last["name"] == "distance_components:writable"
    assert last["cheapest_world"] == "G09"
    assert last["cost_there"] == 0
    assert last["control_cost_if_budget_lifted"] == 4
    assert last["best_cost_rank_that_reaches"] == 3


def test_the_free_and_paid_columns_are_kept_apart(transparent):
    """Reachable-but-not-free is the price of seeing what the convention does not show you."""
    assert transparent["free_total"] == 4011
    assert transparent["paid_total"] == 1108
    assert transparent["mean_premium"] == pytest.approx(1.1715, abs=5e-5)
    assert transparent["premium_distribution"] == {0: 268, 1: 382, 2: 458}
    assert transparent["control_reach_routable"] == 99
    assert transparent["control_reach_rank"] == 1


# ---------------------------------------------------------------------------- 10. the sweep


def test_budget_sweep_shows_the_answer_is_a_function_of_the_threshold(sweep):
    result = sweep
    rows = {(row["regime"], row["budget"]): row for row in result["rows"]}
    assert len(result["rows"]) == len(REGIMES) * len(BUDGET_SWEEP)
    assert [rows[("transparent", budget)]["control_gap"] for budget in BUDGET_SWEEP] == [
        75,
        65,
        6,
        1,
        0,
        0,
        0,
        0,
        0,
    ]
    assert [rows[("opaque", budget)]["control_gap"] for budget in BUDGET_SWEEP] == [
        75,
        72,
        63,
        62,
        61,
        61,
        61,
        61,
        61,
    ]
    assert result["control_gap_range"] == (0, 75)


def test_the_transparent_routable_set_is_made_entirely_by_the_budget(sweep):
    """The null this module has to publish: with nothing excluded there is nothing to route."""
    result = sweep
    unbounded = next(
        row for row in result["rows"] if row["regime"] == "transparent" and row["budget"] == 8
    )
    assert unbounded["routable"] == 0
    assert unbounded["everywhere"] == 245
    assert unbounded["nowhere"] == 236
    assert result["transparent_routable_is_budget_made"] is True


def test_the_opaque_regime_keeps_a_routable_set_at_every_budget(sweep):
    """The robustness check: where a bracket hides, reachability is not a thresholded cost."""
    result = sweep
    opaque_rows = [row for row in result["rows"] if row["regime"] == "opaque"]
    assert all(row["routable"] > 0 for row in opaque_rows)
    unbounded = opaque_rows[-1]
    assert unbounded["budget"] == 8
    assert unbounded["routable"] == 192
    assert unbounded["control_gap"] == 61
    assert unbounded["control_reach_rank"] == 3


def test_the_qualitative_conclusion_survives_the_rule_change(opaque, costs):
    """0038's opaque regime, recounted: G0 misses more, not less, and is no longer joint-first."""
    assert opaque["reachable_everywhere"] == 35
    assert opaque["reachable_nowhere"] == 244
    assert opaque["routable"] == 202
    assert opaque["control_gap_count"] == 63
    assert opaque["control_reach_routable"] == 139
    assert opaque["control_reach_rank"] == 3
    order = dominance(opaque)
    assert order["control_is_maximal"] is True
    assert order["distinct_reach_sets"] == 22
    collision = cost_vs_reach(opaque, costs)
    assert collision["spearman"] == pytest.approx(0.8695, abs=5e-5)
    assert collision["dear_and_strong"] == ("G06",)


# ------------------------------------------------------------------------------ 11. concurrency


def test_sequential_and_parallel_agree():
    """Two paths over the same payloads must return identical records, in identical order."""
    payloads = [
        (item.name, writing.role, grammar.id)
        for item in CORPUS[:6]
        for writing in item.writings
        for grammar in GRAMMARS[:5]
    ]
    sequential = rf._map_cells(payloads, workers=1)
    parallel = rf._map_cells(payloads, workers=4)
    assert sequential == parallel
    assert len(sequential) == len(payloads)


def test_reachability_table_is_identical_on_both_paths():
    """The published table must not depend on how many processes computed it."""
    corpus = CORPUS[:8]
    grammars = GRAMMARS[:6]
    one = reachability_table(corpus, grammars, index=grid_index(corpus, grammars, workers=1))
    many = reachability_table(corpus, grammars, index=grid_index(corpus, grammars, workers=4))
    assert one["reach_all"] == many["reach_all"]
    assert one["reachable_everywhere"] == many["reachable_everywhere"]
    assert one["reachable_nowhere"] == many["reachable_nowhere"]
    assert one["routable"] == many["routable"]
    assert [row["reached"] for row in one["rows"]] == [row["reached"] for row in many["rows"]]


def test_worker_count_comes_from_the_observed_core_count():
    assert worker_count_for(16, 1250) == 12
    assert worker_count_for(4, 1250) == 2
    assert worker_count_for(64, 1250) == 12
    assert worker_count_for(16, 1) == 1
    assert worker_count_for(1, 1250) == 1
    assert default_worker_count(1250) == worker_count_for(rf.os.cpu_count() or 1, 1250)


def test_the_parallel_decision_is_arithmetic_on_measured_numbers_not_a_cell_count():
    """Both directions are pinned, so removing the measurement cannot pass silently."""
    assert should_parallelise(1250, CELL_SECONDS, 12) is False
    assert should_parallelise(20000, CELL_SECONDS, 12) is True
    assert should_parallelise(1250, CELL_SECONDS, 1) is False
    assert should_parallelise(1, CELL_SECONDS, 12) is False
    assert POOL_STARTUP_SECONDS + 1250 * CELL_SECONDS / 12 > 1250 * CELL_SECONDS


def test_the_sequential_verdict_survives_the_whole_measured_range():
    """The per-cell cost varied 2.25e-4 to 5.2e-4 with load; the verdict must not depend on which."""
    for seconds_per_cell in (2.25e-04, 5.2e-04):
        for startup in (1.32, 3.74):
            sequential = 1250 * seconds_per_cell
            assert startup + sequential / 12 > sequential


# ------------------------------------------------------------------------- 12. internal coherence


def test_reach_counts_agree_with_the_per_task_rows(transparent):
    for grammar_id in transparent["grammars"]:
        assert transparent["reach_all"][grammar_id] == sum(
            1 for row in transparent["rows"] if row["per_world"][grammar_id].reachable
        )
        assert transparent["reach_routable"][grammar_id] == sum(
            1 for row in transparent["routable_rows"] if row["per_world"][grammar_id].reachable
        )


def test_free_implies_reachable_and_premium_is_never_negative(transparent):
    for row in transparent["rows"]:
        for verdict in row["per_world"].values():
            if verdict.free:
                assert verdict.reachable
            if verdict.reachable:
                assert verdict.premium is not None and verdict.premium >= 0
                assert verdict.cost is not None and verdict.cost <= BRACKET_BUDGET
            else:
                assert verdict.blocked_by in ("no_witness", "budget")


def test_a_reachable_task_always_has_its_default_writing_within_budget(index):
    """The implication that lets ``reachable`` drop a budget clause from the free column.

    The default writing is the cheapest one, so a witness within budget forces the default within
    budget too.  It is asserted over the whole grid, at every budget and in both regimes, rather
    than written into the code as a guard no test could falsify.
    """
    for regime in REGIMES:
        for budget in BUDGET_SWEEP:
            for task in tasks():
                for grammar in GRAMMARS:
                    verdict = reachable(task, grammar.id, budget, regime, index)
                    if verdict.reachable:
                        assert verdict.default_cost <= budget
                        assert verdict.default_cost <= verdict.cost


def test_a_pair_task_is_never_reachable_where_both_its_halves_are_not(transparent):
    """Simultaneity implies each half separately; the converse is exactly what 0038 denied."""
    by_name = {row["name"]: row for row in transparent["rows"]}
    for row in transparent["rows"]:
        if row["kind"] != "property_pair":
            continue
        first, second = row["properties"]
        left = by_name[f"{row['object']}:{first}"]
        right = by_name[f"{row['object']}:{second}"]
        for grammar_id in transparent["grammars"]:
            if row["per_world"][grammar_id].reachable:
                assert left["per_world"][grammar_id].reachable
                assert right["per_world"][grammar_id].reachable


def test_the_pair_rule_really_bites_somewhere(transparent):
    """If no pair were ever harder than its halves the second requirement kind would be noise."""
    by_name = {row["name"]: row for row in transparent["rows"]}
    strictly_harder = 0
    for row in transparent["rows"]:
        if row["kind"] != "property_pair":
            continue
        first, second = row["properties"]
        left = by_name[f"{row['object']}:{first}"]
        right = by_name[f"{row['object']}:{second}"]
        for grammar_id in transparent["grammars"]:
            if (
                left["per_world"][grammar_id].reachable
                and right["per_world"][grammar_id].reachable
                and not row["per_world"][grammar_id].reachable
            ):
                strictly_harder += 1
    assert strictly_harder > 0


def test_spearman_helper_is_correct_on_known_inputs():
    assert rf._spearman([1, 2, 3, 4], [1, 2, 3, 4]) == pytest.approx(1.0)
    assert rf._spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert math.isnan(rf._spearman([1], [1]))
    # midranks for ties: two tied values share the average of the ranks they span
    assert rf._spearman([1, 1, 2, 2], [1, 1, 2, 2]) == pytest.approx(1.0)


def test_competition_ranking_matches_the_project_convention():
    assert rf._competition_rank({"a": 3, "b": 3, "c": 1}, descending=True) == {
        "a": 1,
        "b": 1,
        "c": 3,
    }
    assert rf._competition_rank({"a": 3, "b": 3, "c": 1}, descending=False) == {
        "c": 1,
        "a": 2,
        "b": 2,
    }


def test_every_pair_of_worlds_is_classified_exactly_once(transparent):
    order = dominance(transparent)
    relation = set(order["relation"])
    reach_sets = {
        grammar_id: frozenset(
            row["name"]
            for row in transparent["routable_rows"]
            if row["per_world"][grammar_id].reachable
        )
        for grammar_id in transparent["grammars"]
    }
    for first, second in combinations(transparent["grammars"], 2):
        comparable = (first, second) in relation or (second, first) in relation
        equal = reach_sets[first] == reach_sets[second]
        assert comparable != equal or (not comparable and not equal)
