"""Experiment 0042: does fragment routing survive the seams?

The order of this file is the order of the argument. The correctness bridge comes first, because a
cost number is meaningless if the rendering does not denote the tree it came from. The seam
obligation comes second and is the decisive test: every routed composite must equal the single-world
composite as an OBJECT, on the project semantic key, over the whole corpus. Everything after that is
pinning what was measured.

Headline numbers are written as LITERALS. A test that recomputes the module's own answer and
compares it to itself pins nothing.
"""

import pytest

from parseatlas.alternative_mathematics import semantic_key as project_semantic_key
from parseatlas.alternative_mathematics import semantic_key
from parseatlas.canonical import canonicalize
from parseatlas.fragment_routing import (
    BRACKET_CELL_SECONDS,
    COMPOSITE_BY_NAME,
    CORPUS,
    EXCLUDED,
    GRAMMAR_BY_ID,
    MINIMUM_FRAGMENTS,
    MODELS,
    NAMING_UNIT_COST,
    OBJECTIVES,
    POOL_STARTUP_SECONDS,
    VERDICT_CELL_SECONDS,
    Composite,
    best_world,
    best_worlds,
    composite_tree,
    control_level,
    corpus_audit,
    decode_routing,
    decomposition_table,
    default_worker_count,
    depth_discrimination,
    fragment_cost,
    fragment_table,
    fragments,
    global_host_verdict,
    hole_name,
    host_table,
    minimality_audit,
    naming_break_even,
    objective_agreement,
    oracle_bound,
    readable_routing_audit,
    reassociations,
    round_trip_audit,
    route,
    seam_profile,
    should_parallelise,
    split,
    substitute,
    verdict_table,
    verify_routing,
    visibility_regime_audit,
    world_scores,
)
from parseatlas.grammar import all_grammars, control_grammar
from parseatlas.notational_cost import render
from parseatlas.parallel_worlds import depth as imported_depth
from parseatlas.parser import Binary, Variable, parse

GRAMMARS = all_grammars()
CONTROL = control_grammar()


@pytest.fixture(scope="module")
def table():
    """The verdict sweep, once. This is what the headline numbers are read from."""
    return verdict_table(workers=1)


@pytest.fixture(scope="module")
def globals_table():
    return global_host_verdict()


# --------------------------------------------------------------- 1. the correctness bridge, first


def test_round_trip_holds_over_the_whole_grid():
    """Every composite AND every fragment, rendered under all 25 worlds, reparses to itself."""
    audit = round_trip_audit()
    assert audit["checks"] == 3125
    assert audit["failures"] == 0
    assert audit["holds"] is True


def test_every_bracket_emitted_is_load_bearing():
    """Minimality by construction: deleting any bracket must change or break the parse."""
    audit = minimality_audit()
    assert audit["brackets_checked"] == 1945
    assert audit["violations"] == 0
    assert audit["minimal"] is True


def test_the_grid_covers_composites_and_their_fragments():
    """125 records x 25 worlds = 3125: the bridge covers what the module actually renders."""
    assert len(CORPUS) == 38
    assert corpus_audit()["fragment_total"] == 87
    assert (38 + 87) * 25 == 3125


# ------------------------------------------------- 2. THE DECISIVE ONE: the obligation at the seam


def test_every_routed_composite_equals_the_single_world_composite_as_an_object(table):
    """The card's load-bearing assertion, over the whole corpus and both architectures.

    Compared on the project semantic key, not on the rendered string: a routing that produced a
    different function would have solved a different problem, however cheap its writing.
    """
    assert table["cells"] == 38 * len(OBJECTIVES) * len(MODELS) == 304
    assert all(row["preserved"] for row in table["rows"])
    assert table["all_preserved"] is True


def test_the_seam_check_is_on_the_semantic_key_and_not_on_the_string():
    """Two writings of one object differ as strings and agree as objects."""
    item = COMPOSITE_BY_NAME["ellipse.standard"]
    record = route(item, "brackets", "inline")
    assert record["document"] != item.source
    check = verify_routing(record, item)
    assert check["routed_key"] == check["single_key"]
    assert check["preserved"] is True


def test_the_seam_check_catches_a_mis_declared_world():
    """A negative control: the obligation is not vacuous.

    ``ellipse.standard`` routes both fragments to ``G01``, where ``x * x / a * a`` denotes
    ``(x*x)/(a*a)``. Reading the same characters in ``G0`` gives ``x*x/a*a = x**2``, a different
    function, and the semantic key says so.
    """
    item = COMPOSITE_BY_NAME["ellipse.standard"]
    record = route(item, "brackets", "inline")
    assert record["worlds"] == ("G01", "G01")
    mutant = dict(record, worlds=("G0", "G0"))
    check = verify_routing(mutant, item)
    assert check["preserved"] is False
    assert check["routed_key"][0] == "x**2 + y**2"
    assert check["single_key"][0] != check["routed_key"][0]


def test_the_decode_reads_each_piece_in_its_declared_world():
    """The decode uses only the document's parts and their declared worlds, not the split record."""
    item = COMPOSITE_BY_NAME["circle.center_radius"]
    record = route(item, "brackets", "inline")
    assert decode_routing(record) == composite_tree(item)


def test_the_domain_slot_of_the_semantic_key_is_inert():
    """NF-2026-00005, restated here: ``domain`` is always ``"R"``, so it discriminates nothing."""
    item = COMPOSITE_BY_NAME["quotient_rule.split"]
    check = verify_routing(route(item, "brackets", "named"), item)
    assert check["routed_key"][1] == "R"
    assert check["single_key"][1] == "R"
    assert project_semantic_key(canonicalize(composite_tree(item)))[1] == "R"


# ------------------------------------------------------------------ 3. the splitting rule, declared


def test_the_splitting_rule_is_deterministic():
    """The same tree cut twice gives the same fragments, skeleton and positions."""
    for item in CORPUS:
        first = split(composite_tree(item))
        second = split(composite_tree(item))
        assert first == second


def test_the_splitting_rule_produces_the_pinned_fragment_counts():
    audit = corpus_audit()
    assert audit["size"] == 38
    assert audit["fragment_total"] == 87
    assert audit["fragment_histogram"] == {2: 31, 3: 5, 4: 1, 6: 1}
    assert audit["min_fragments"] == 2
    assert audit["max_fragments"] == 6
    assert audit["excluded_count"] == 12
    assert audit["duplicate_names"] == ()
    assert audit["sources_canonical"] is True
    assert audit["hole_prefix_free"] is True


def test_named_objects_are_cut_where_the_rule_says_and_not_by_hand():
    """Three worked splits, spelled out."""
    parts = split(composite_tree(COMPOSITE_BY_NAME["circle.general"]))
    assert parts.count == 6
    assert tuple(render(fragment, CONTROL) for fragment in parts.fragments) == (
        "x * x",
        "2 * h * x",
        "h * h",
        "y * y",
        "2 * k * y",
        "k * k",
    )
    parts = split(composite_tree(COMPOSITE_BY_NAME["ellipse.standard"]))
    assert tuple(render(fragment, CONTROL) for fragment in parts.fragments) == (
        "x * x / (a * a)",
        "y * y / (b * b)",
    )
    parts = split(composite_tree(COMPOSITE_BY_NAME["slope.difference_quotient"]))
    assert tuple(render(fragment, CONTROL) for fragment in parts.fragments) == (
        "y2 - y1",
        "x2 - x1",
    )
    assert parts.join_operator == "/"


def test_the_rule_reads_the_control_grammars_levels():
    assert control_level("+") == ("+", "-")
    assert control_level("/") == ("*", "/")
    assert CONTROL.levels == (("*", "/"), ("+", "-"))


def test_leaves_are_never_fragments():
    """``2 * (a + b)`` has one fragment, not two: ``2`` is a token no convention can charge for."""
    tree = parse("2 * (a + b)", CONTROL)
    assert tuple(render(fragment, CONTROL) for fragment in fragments(tree)) == ("a + b",)


def test_a_homogeneous_level_object_has_nothing_to_route():
    """``a / (b * c)`` is one multiplicative chain: no operand of it is a fragment."""
    assert fragments(parse("a / (b * c)", CONTROL)) == ()


def test_the_skeleton_plus_the_fragments_rebuild_the_object_exactly():
    for item in CORPUS:
        parts = split(composite_tree(item))
        mapping = {
            hole_name(index): fragment for index, fragment in enumerate(parts.fragments)
        }
        assert substitute(parts.skeleton, mapping) == composite_tree(item)


def test_the_excluded_writings_are_published_with_their_counts():
    assert len(EXCLUDED) == 12
    assert all(entry["fragments"] < MINIMUM_FRAGMENTS for entry in EXCLUDED)
    names = {entry["name"] for entry in EXCLUDED}
    assert "chain_rule.standard" in names
    assert "midpoint.mean" in names


# ------------------------------------------------------------------------- 4. the three objectives


def test_the_four_objectives_agree_on_77_of_87_fragments():
    report = objective_agreement()
    assert report["fragments"] == 87
    assert report["all_objectives_agree"] == 77
    assert report["pairwise_agreement"] == {
        "brackets_vs_visibility": 77,
        "brackets_vs_visibility_opaque": 82,
        "brackets_vs_depth": 77,
        "visibility_vs_visibility_opaque": 82,
        "visibility_vs_depth": 87,
        "visibility_opaque_vs_depth": 82,
    }
    assert report["distinct_choice_patterns"] == 3
    assert report["choice_patterns"] == (
        ("G0", "G0", "G0", "G0"),
        ("G01", "G0", "G0", "G0"),
        ("G01", "G0", "G01", "G0"),
    )
    assert report["reconcilable"] == 87


def test_two_objectives_cannot_separate_any_world():
    """Transparent visibility and depth tie all 25 worlds on all 87 fragments: they are blind."""
    ties = objective_agreement()["ties"]
    assert ties["visibility"]["all_worlds_tied"] == 87
    assert ties["depth"]["all_worlds_tied"] == 87
    assert ties["visibility"]["mean_tie_size"] == 25.0
    assert ties["visibility_opaque"]["all_worlds_tied"] == 75
    assert ties["visibility_opaque"]["control_among_best"] == 82
    assert ties["brackets"]["all_worlds_tied"] == 70
    assert ties["brackets"]["control_among_best"] == 77
    assert ties["brackets"]["control_unique_best"] == 0


def test_the_two_visibility_regimes_answer_differently_for_a_structural_reason():
    """Under the transparent regime a shape rule looks THROUGH a bracket, so the manifest set of a
    fixed tree is a function of the tree and not of the world. The opaque regime is the one that can
    express a preference at all, and this is why the direction of the transparent objective is
    unobservable on this corpus."""
    report = visibility_regime_audit()
    assert report["visibility"]["regime"] == "transparent"
    assert report["visibility"]["varying"] == 0
    assert report["visibility"]["max_range"] == 0
    assert report["visibility"]["world_invariant"] is True
    assert report["visibility"]["control_is_best"] == 87
    assert report["visibility_opaque"]["regime"] == "opaque"
    assert report["visibility_opaque"]["varying"] == 12
    assert report["visibility_opaque"]["max_range"] == 5
    assert report["visibility_opaque"]["world_invariant"] is False
    assert report["visibility_opaque"]["control_is_best"] == 82


def test_the_five_fragments_where_cost_and_opaque_visibility_disagree():
    rows = [
        row
        for row in objective_agreement()["rows"]
        if row["chosen"]["brackets"] != row["chosen"]["visibility_opaque"]
    ]
    assert len(rows) == 5
    assert sorted(row["source"] for row in rows) == [
        "(y - k) * (y - k)",
        "(y2 - y1) * (y2 - y1)",
        "u * dv / (v * v)",
        "y * y / (b * b)",
        "y * y / (b * b)",
    ]
    assert all(row["chosen"]["brackets"] == "G01" for row in rows)
    assert all(row["chosen"]["visibility_opaque"] == "G0" for row in rows)


def test_the_ten_fragments_that_leave_the_conventional_world_all_go_to_g01():
    rows = [row for row in fragment_table()["rows"] if row["chosen"]["brackets"] != "G0"]
    assert len(rows) == 10
    assert {row["chosen"]["brackets"] for row in rows} == {"G01"}
    assert {row["min_cost"] for row in rows} == {0}
    assert sorted({row["source"] for row in rows}) == [
        "(x - h) * (x - h)",
        "(x2 - x1) * (x2 - x1)",
        "(y - k) * (y - k)",
        "(y2 - y1) * (y2 - y1)",
        "a * (r + s) * x",
        "u * dv / (v * v)",
        "x * x / (a * a)",
        "y * y / (b * b)",
    ]


def test_depth_is_the_imported_critical_path_and_it_is_world_invariant():
    report = depth_discrimination()
    assert report["fragments"] == 87
    assert report["world_invariant"] == 87
    assert report["shallower_available"] == 0
    assert report["reassociable"] == 20
    assert report["degenerate"] is True
    fragment = fragments(COMPOSITE_BY_NAME["circle.center_radius"])[0]
    assert world_scores(fragment, "depth") == {
        grammar.id: imported_depth(fragment) for grammar in GRAMMARS
    }


def test_a_same_operator_right_child_is_bracketed_in_every_world():
    """The structural reason depth cannot discriminate: the cheapest chain writing is the deepest."""
    balanced = parse("(a + b) + (c + d)", CONTROL)
    assert all(fragment_cost(balanced, grammar) >= 1 for grammar in GRAMMARS)
    left_leaning = parse("a + b + c + d", CONTROL)
    assert all(fragment_cost(left_leaning, grammar) == 0 for grammar in GRAMMARS)
    assert imported_depth(left_leaning) == 3
    assert imported_depth(balanced) == 2


def test_reassociations_keep_the_token_word_and_exclude_minus_and_slash():
    forms = reassociations(parse("a + b + c", CONTROL))
    assert len(forms) == 2
    assert {render(form, CONTROL) for form in forms} == {"a + b + c", "a + (b + c)"}
    assert reassociations(parse("a - b - c", CONTROL)) == (parse("a - b - c", CONTROL),)


def test_ties_break_to_the_conventional_world():
    """The conservative tie-break, pinned: an undecided fragment stays with ``G0``."""
    fragment = parse("a + b", CONTROL)
    assert best_worlds(fragment, "brackets") == tuple(grammar.id for grammar in GRAMMARS)
    assert best_world(fragment, "brackets").id == "G0"


# ------------------------------------------------------------------- 5. the seam, never blended in


def test_seam_cost_is_separated_from_total_cost_in_every_row(table):
    """The seam is a column of its own in all 304 cells, and the accounting closes on all of them."""
    for row in table["rows"]:
        assert {"interior_cost", "skeleton_cost", "seam_cost", "routed_cost"} <= set(row)
        assert row["routed_cost"] == row["interior_cost"] + row["skeleton_cost"] + row["seam_cost"]
        assert row["accounting_closes"] is True
    for entry in table["totals"].values():
        assert entry["routed_total"] == (
            entry["interior_total"] + entry["skeleton_total"] + entry["seam_total"]
        )
        assert entry["accounting_closes"] is True


def test_the_seam_is_never_silently_zero(table):
    """Every case carries a seam, and Model II's seam is a named intermediate per fragment."""
    for key, entry in table["totals"].items():
        assert entry["seam_total"] > 0, key
    assert table["totals"]["brackets/named"]["seam_total"] == 87
    assert table["totals"]["brackets/inline"]["seam_total"] == 6
    assert table["totals"]["visibility/inline"]["seam_total"] == 5


def test_the_inline_seam_has_two_independent_reasons():
    profile = seam_profile()["brackets/inline"]
    assert profile["wraps"] == 6
    assert profile["wraps_precedence_only"] == 2
    assert profile["wraps_unreadable_only"] == 4
    assert profile["wraps_both"] == 0
    assert profile["documents"] == 38
    assert profile["documents_host_readable"] == 34
    assert profile["fragments_routed_off_control"] == 10
    assert profile["forfeited_by_one_convention"] == 9


def test_model_two_pays_naming_units_and_not_brackets():
    profile = seam_profile()["brackets/named"]
    assert profile["wraps"] == 0
    assert profile["seam_total"] == 87 * NAMING_UNIT_COST
    assert profile["documents_host_readable"] == 38
    record = route(COMPOSITE_BY_NAME["slope.difference_quotient"], "brackets", "named")
    assert record["naming_units"] == 2
    assert record["self_describing"] is True
    assert len(record["lines"]) == 3
    assert record["lines"][-1].startswith("result := ")


def test_a_bracket_does_not_carry_a_convention():
    """The one object where inline routing beats the best single world is not host-readable.

    ``sum_of_cubes.factored`` routes both fragments to ``G0`` and hosts them in ``G01``. The seam
    bracket keeps the JOIN right and can do nothing about the interior, which a ``G01`` reader
    re-associates. This is the measurement behind the card's verdict.
    """
    record = route(COMPOSITE_BY_NAME["sum_of_cubes.factored"], "brackets", "inline")
    assert record["host"] == "G01"
    assert record["document"] == "a + b * (a * a - a * b + b * b)"
    assert record["total_cost"] == 1
    assert record["seam_cost"] == 1
    assert record["host_readable"] is False
    assert parse(record["document"], GRAMMAR_BY_ID["G01"]) != composite_tree(
        COMPOSITE_BY_NAME["sum_of_cubes.factored"]
    )
    assert verify_routing(record)["preserved"] is True


# --------------------------------------------------------- 6. the headline verdict, pinned literally


def test_the_oracle_the_seam_and_what_survives_are_three_separate_numbers():
    bound = oracle_bound()
    assert bound["objects"] == 38
    assert bound["single_world"] == 33
    assert bound["single_world_id"] == "G18"
    assert bound["control_total"] == 35
    assert bound["per_object_oracle"] == 7
    assert bound["per_object_gap"] == 26
    assert bound["fragment_oracle"] == 0
    assert bound["fragment_interior_oracle"] == 0
    assert bound["fragment_skeleton_oracle"] == 0
    assert bound["prize"] == 33
    assert bound["published_0034"]["gap"] == 26
    assert bound["published_0034"]["status"].startswith("seamless upper bound")


def test_the_cost_of_a_single_world_document_sits_at_the_joins():
    report = decomposition_table()
    assert report["control"] == {
        "id": "G0",
        "whole": 35,
        "interior": 14,
        "skeleton": 0,
        "joins": 21,
    }
    assert report["best"] == {"id": "G18", "whole": 33, "interior": 9, "skeleton": 3, "joins": 21}
    assert report["interior_floor"] == 0
    assert report["skeleton_floor"] == 0
    assert report["join_floor"] == 21


def test_the_per_object_verdict_totals(table):
    """Model I wins by 1 bracket of 7; Model II loses by 80."""
    totals = table["totals"]
    assert totals["brackets/inline"]["best_single_total"] == 7
    assert totals["brackets/inline"]["routed_total"] == 6
    assert totals["brackets/inline"]["seam_total"] == 6
    assert totals["brackets/inline"]["interior_total"] == 0
    assert (totals["brackets/inline"]["wins"], totals["brackets/inline"]["ties"]) == (1, 37)
    assert totals["brackets/inline"]["loses"] == 0
    assert totals["brackets/named"]["routed_total"] == 87
    assert totals["brackets/named"]["loses"] == 36
    assert totals["visibility/inline"]["routed_total"] == 19
    assert totals["visibility/inline"]["loses"] == 5
    assert totals["visibility/named"]["routed_total"] == 101
    assert totals["visibility_opaque/inline"]["routed_total"] == 13
    assert totals["visibility_opaque/inline"]["interior_total"] == 7
    assert totals["visibility_opaque/inline"]["seam_total"] == 6
    assert totals["visibility_opaque/named"]["routed_total"] == 94
    assert totals["depth/inline"]["routed_total"] == 19
    assert totals["depth/named"]["routed_total"] == 101


def test_the_global_host_verdict_is_the_headline(globals_table):
    """One host convention for all 38 documents, against one convention with no routing at all."""
    cases = globals_table["per_case"]
    assert globals_table["single_world"] == 33
    assert globals_table["single_world_id"] == "G18"
    assert cases["brackets/inline"]["routed_total"] == 29
    assert cases["brackets/inline"]["best_hosts"] == ("G18",)
    assert cases["brackets/inline"]["margin"] == 4
    assert cases["brackets/inline"]["wins"] is True
    assert cases["brackets/inline"]["routed_breakdown"] == {
        "total": 29,
        "interior": 0,
        "skeleton": 3,
        "seam": 26,
        "host_readable": 35,
    }
    assert cases["brackets/named"]["routed_total"] == 87
    assert cases["brackets/named"]["margin"] == -54
    assert cases["visibility/inline"]["routed_total"] == 35
    assert cases["visibility/inline"]["margin"] == -2
    assert cases["visibility_opaque/inline"]["routed_total"] == 33
    assert cases["visibility_opaque/inline"]["margin"] == 0
    assert cases["visibility_opaque/inline"]["wins"] is False
    assert cases["visibility_opaque/named"]["routed_total"] == 94
    assert cases["depth/inline"]["routed_total"] == 35
    assert cases["visibility/named"]["routed_total"] == 101
    assert cases["depth/named"]["routed_total"] == 101


def test_only_one_eighth_of_the_seamless_prize_survives_the_seam(globals_table, table):
    """The card's third headline, as a percentage, from both baselines."""
    prize = 33
    survives = prize - globals_table["per_case"]["brackets/inline"]["routed_total"]
    assert survives == 4
    assert round(100.0 * survives / prize, 1) == 12.1
    per_object_prize = 7
    per_object_survives = per_object_prize - table["totals"]["brackets/inline"]["routed_total"]
    assert per_object_survives == 1
    assert round(100.0 * per_object_survives / per_object_prize, 1) == 14.3


def test_a_host_readable_inline_document_gains_exactly_nothing():
    """The sharpest result of the card, checked over the whole 25 x 87 x 25 grid.

    ``render(F, h)`` is the minimum-bracket ``h``-writing of a fragment, so any world whose
    rendering ``h`` reads correctly costs at least as much. Routing that a host reader can decode
    without a side channel therefore delivers zero.
    """
    audit = readable_routing_audit()
    assert audit["fragments"] == 87
    assert audit["hosts"] == 25
    assert audit["checks"] == 54375
    assert audit["cheaper_readable_alternatives"] == 0
    assert audit["counterexamples"] == ()
    assert audit["total_gain"] == 0
    assert audit["holds"] is True
    assert audit["per_host"]["G18"] == {
        "readable_interior": 9,
        "native_interior": 9,
        "gain": 0,
        "mean_readable_worlds": pytest.approx(24.310344827586206),
    }


def test_five_objects_flip_their_verdict_when_the_objective_changes(table):
    """Headline five: routing ties under ``brackets`` and loses under ``visibility`` on these."""
    verdicts = {}
    for row in table["rows"]:
        if row["model"] == "inline":
            verdicts.setdefault(row["composite"], {})[row["objective"]] = (
                "win" if row["wins"] else "tie" if row["ties"] else "lose"
            )
    flipped = sorted(name for name, cells in verdicts.items() if len(set(cells.values())) > 1)
    assert flipped == [
        "circle.center_radius",
        "distance_components.squared",
        "ellipse.standard",
        "hyperbola.standard",
        "quotient_rule.split",
    ]
    for name in flipped:
        assert verdicts[name]["brackets"] == "tie"
        assert verdicts[name]["visibility"] == "lose"
        assert verdicts[name]["visibility_opaque"] == "lose"
        assert verdicts[name]["depth"] == "lose"


def test_how_often_the_conventional_world_is_the_right_host(table):
    """Headline six, reported twice so the tie-break cannot be mistaken for a finding."""
    report = host_table(workers=1)["per_case"]
    assert report["brackets/inline"]["control_chosen"] == 24
    assert report["brackets/inline"]["control_among_optimal"] == 24
    assert report["brackets/inline"]["control_uniquely_optimal"] == 1
    assert report["brackets/inline"]["distinct_hosts"] == 5
    assert report["brackets/named"]["control_chosen"] == 38
    assert report["brackets/named"]["all_worlds_tied"] == 31
    assert report["visibility/inline"]["control_chosen"] == 29
    assert report["visibility_opaque/inline"]["control_chosen"] == 25
    assert report["visibility_opaque/inline"]["distinct_hosts"] == 5


def test_the_naming_rate_at_which_model_two_would_start_winning():
    report = naming_break_even(workers=1)["per_objective"]
    assert report["brackets"]["names"] == 87
    assert report["brackets"]["global"]["baseline"] == 33
    assert round(report["brackets"]["global"]["break_even_rate"], 4) == 0.3793
    assert report["brackets"]["global"]["largest_winning_integer_rate"] == 0
    assert report["brackets"]["per_object"]["baseline"] == 7
    assert round(report["brackets"]["per_object"]["break_even_rate"], 4) == 0.0805
    assert round(report["visibility"]["global"]["break_even_rate"], 4) == 0.2184
    assert round(report["visibility_opaque"]["global"]["break_even_rate"], 4) == 0.2989
    assert report["visibility_opaque"]["fixed_cost"] == 7


# ---------------------------------------------------------------- 7. concurrency changes only speed


def test_sequential_and_parallel_agree():
    """Two workers over the same cells return byte-identical records."""
    sequential = verdict_table(CORPUS[:6], workers=1)
    parallel = verdict_table(CORPUS[:6], workers=2)
    assert sequential["rows"] == parallel["rows"]
    assert sequential["totals"] == parallel["totals"]


def test_the_worker_count_comes_from_the_observed_cores():
    import os

    cores = os.cpu_count() or 1
    assert default_worker_count(10_000) == max(1, min(cores - 2, 12))
    assert default_worker_count(3) == min(3, max(1, min(cores - 2, 12)))


def test_the_parallel_decision_is_taken_from_measured_seconds():
    """304 verdict cells clear the pool cost; 87 bracket cells do not. Measured, not assumed.

    The sweep is 38 writings x 4 objectives x 2 models. An earlier revision passed 228 here, which is
    the same product before ``visibility_opaque`` was added as a fourth objective.
    """
    assert should_parallelise(304, VERDICT_CELL_SECONDS, 12) is True
    assert should_parallelise(87, BRACKET_CELL_SECONDS, 12) is False
    assert should_parallelise(304, VERDICT_CELL_SECONDS, 1) is False
    assert POOL_STARTUP_SECONDS == 1.8


# -------------------------------------------------------------------------------- 8. guard rails


def test_route_rejects_an_unknown_objective_or_model():
    item = CORPUS[0]
    with pytest.raises(ValueError):
        route(item, "cheapness", "inline")
    with pytest.raises(ValueError):
        route(item, "brackets", "spreadsheet")
    with pytest.raises(ValueError):
        world_scores(composite_tree(item), "cheapness")
    assert OBJECTIVES == ("brackets", "visibility", "visibility_opaque", "depth")


def test_route_refuses_an_object_with_nothing_to_route():
    item = Composite("probe", "algebra", "probe", "only", None, "a / (b * c)")
    with pytest.raises(ValueError, match="nothing to route"):
        route(item, "brackets", "inline")


def test_hole_names_cannot_collide_with_a_corpus_variable():
    assert hole_name(0) == "_f00"
    assert all("_" not in item.source for item in CORPUS)
    skeleton = split(composite_tree(COMPOSITE_BY_NAME["circle.general"])).skeleton
    text = render(skeleton, CONTROL)
    assert "_f05" in text and "_f00" in text
    assert parse(text, CONTROL) == skeleton


def test_a_named_host_is_honoured_and_reported_as_optimal_or_not():
    item = COMPOSITE_BY_NAME["ellipse.standard"]
    forced = route(item, "brackets", "inline", host="G20")
    assert forced["host"] == "G20"
    assert forced["host_is_optimal"] is False
    assert forced["total_cost"] >= route(item, "brackets", "inline")["total_cost"]


def test_fragment_table_counts_the_corpus_the_report_publishes():
    report = fragment_table()
    assert report["fragments"] == 87
    assert report["distinct_sources"] == 67
    assert report["free_in_control"] == 77
    assert report["free_in_every_world"] == 70
    assert report["free_in_some_world"] == 87
    assert report["interior_floor"] == 0
    assert report["interior_under_control"] == 14


# ---- the half of the key nothing was exercising, added after review ----------------------------


def test_the_seam_obligation_really_compares_excluded_points_and_not_only_canonical_form():
    """Dropping excluded points from the comparison must not be able to pass unnoticed.

    ``verify_routing`` compares the full project key ``(canonical form, domain, excluded points)``.
    A review replaced that with a canonical-form-only comparison on an isolated copy and the whole
    suite still passed: every routing in this corpus happens to agree on excluded points, so the
    third component was load-bearing in production and untested here.

    This asserts the discrimination directly, on the classic pair that separates the two: ``x / x``
    and ``1`` share a canonical form and differ only in that ``x = 0`` is excluded from the first.
    A key that cannot tell them apart cannot certify a seam.
    """
    same_form = semantic_key(canonicalize(parse("x / x", CONTROL)))
    plain_one = semantic_key(canonicalize(parse("1", CONTROL)))

    assert same_form[0] == plain_one[0], "the pair must agree on canonical form, or it proves nothing"
    assert same_form != plain_one, "the key must separate them somewhere"
    assert same_form[2] != plain_one[2], "and the difference must be in the excluded points"

    # The domain slot is inert (NF-2026-00005) and is asserted as inert rather than assumed useful,
    # so this test says exactly which component is doing the work.
    assert same_form[1] == plain_one[1] == "R"
