"""Tests for experiment 0034: the notational cost of writing real mathematics.

The first test in this file is the card's core. Everything else in the module is arithmetic over
renderings, so if ``parse(render(tree, g), g) != tree`` for even one pair, every number the
experiment publishes is void.
"""

import pytest

from parseatlas.grammar import all_grammars
from parseatlas.notational_cost import (
    CONTROL,
    CORPUS,
    GRAMMARS,
    Formula,
    RoundTripError,
    area_table,
    binding_powers,
    bracket_pairs,
    child_threshold,
    convention_sensitivity,
    corpus_audit,
    cost_rows,
    cost_table,
    formula_tree,
    free_transition,
    free_under,
    minimality_audit,
    minimality_witnesses,
    needs_brackets,
    notational_cost_report,
    null_model,
    parenthesis_cost,
    render,
    resolve_worker_count,
    round_trip_audit,
    tree_operators,
)
from parseatlas.parser import parse

BY_ID = {grammar.id: grammar for grammar in GRAMMARS}


# ------------------------------------------------------------------- the correctness bridge


def test_render_round_trips_for_every_formula_and_every_grammar():
    """THE load-bearing property: writing an object down never changes which object it is."""
    checks = 0
    for formula in CORPUS:
        tree = formula_tree(formula)
        for grammar in GRAMMARS:
            text = render(tree, grammar, verify=False)
            assert parse(text, grammar) == tree, f"{formula.name} under {grammar.id}: {text!r}"
            checks += 1
    assert checks == len(CORPUS) * len(GRAMMARS) == 1450


def test_round_trip_audit_reports_the_full_grid_with_no_failure():
    audit = round_trip_audit()
    assert audit == {"checks": 1450, "failures": 0, "failing": (), "holds": True}


def test_render_raises_when_the_round_trip_would_fail(monkeypatch):
    """The guard is in the production path, not only in the tests - so prove it fires."""
    import parseatlas.notational_cost as module

    monkeypatch.setattr(module, "_render_node", lambda node, powers: "a * b + c")
    tree = formula_tree(Formula("probe", "algebra", "a * b + a * c"))
    with pytest.raises(RoundTripError):
        module.render(tree, CONTROL)


# ----------------------------------------------------------------------------- minimality


def test_every_bracket_in_every_rendering_is_load_bearing():
    """Minimality by construction: delete each bracket pair and the parse must change."""
    for formula in CORPUS:
        tree = formula_tree(formula)
        for grammar in GRAMMARS:
            for witness in minimality_witnesses(tree, grammar):
                assert witness["required"], (
                    f"{formula.name} under {grammar.id}: bracket {witness['pair']} in "
                    f"{witness['rendering']!r} is not required"
                )


@pytest.mark.parametrize(
    "name", ["binomial_square_factored", "slope_through_two_points", "variance_of_two_points"]
)
def test_named_formulas_have_no_removable_bracket_under_any_grammar(name):
    formula = next(item for item in CORPUS if item.name == name)
    tree = formula_tree(formula)
    checked = 0
    for grammar in GRAMMARS:
        text = render(tree, grammar)
        pairs = bracket_pairs(text)
        assert len(pairs) == text.count("(") == text.count(")")
        for pair in pairs:
            stripped = text[: pair[0]] + text[pair[0] + 1 : pair[1]] + text[pair[1] + 1 :]
            try:
                reparsed = parse(stripped, grammar)
            except ValueError:
                reparsed = None
            assert reparsed != tree, f"{name}/{grammar.id}: {stripped!r} still means the same thing"
            checked += 1
    assert checked > 0


def test_minimality_audit_over_the_whole_grid():
    audit = minimality_audit()
    assert audit["brackets_checked"] == 1397
    assert audit["violations"] == 0
    assert audit["minimal"] is True


# ------------------------------------------------------------------------- the bracket rule


def test_binding_powers_come_from_the_levels_and_tie_in_the_control_grammar():
    control = binding_powers(CONTROL)
    assert control["*"] == control["/"] > control["+"] == control["-"]
    strict = binding_powers(BY_ID["G09"])
    assert len(set(strict.values())) == 4
    assert strict["-"] > strict["*"] > strict["+"] > strict["/"]


def test_child_threshold_is_the_parsers_two_numbers():
    assert child_threshold(3, "left") == 3
    assert child_threshold(3, "right") == 4
    with pytest.raises(ValueError):
        child_threshold(3, "middle")


def test_needs_brackets_follows_the_left_associative_rule_including_ties():
    powers = binding_powers(CONTROL)
    tighter = parse("a * b", CONTROL)
    looser = parse("a + b", CONTROL)
    assert needs_brackets(looser, "*", "left", powers) is True
    assert needs_brackets(looser, "*", "right", powers) is True
    assert needs_brackets(tighter, "+", "left", powers) is False
    assert needs_brackets(tighter, "+", "right", powers) is False
    # equal binding power: free on the left, bracketed on the right
    assert needs_brackets(tighter, "/", "left", powers) is False
    assert needs_brackets(tighter, "/", "right", powers) is True
    assert needs_brackets(parse("a", CONTROL), "*", "right", powers) is False


# -------------------------------------------------------------------------------- corpus


def test_corpus_is_auditable_named_mathematics():
    audit = corpus_audit()
    assert audit["size"] == 58
    assert audit["area_count"] == 6
    assert audit["areas"] == {
        "algebra": 10,
        "arithmetic": 10,
        "calculus": 9,
        "geometry": 9,
        "physics": 11,
        "statistics": 9,
    }
    assert audit["duplicate_names"] == ()
    assert audit["canonical_sources"] is True
    assert audit["non_canonical"] == ()


@pytest.mark.parametrize(
    "name,conventional",
    [
        ("mean_of_two", "(a + b) / 2"),
        ("slope_through_two_points", "(y2 - y1) / (x2 - x1)"),
        ("distributive_law_factored", "a * (b + c)"),
        ("distributive_law_expanded", "a * b + a * c"),
        ("binomial_square_factored", "(a + b) * (a + b)"),
        ("difference_of_squares_expanded", "a * a - b * b"),
        ("z_score", "(x - m) / s"),
        ("kinetic_energy", "m * v * v / 2"),
        ("quadratic_expanded", "a * x * x + b * x + c"),
        ("harmonic_sum", "1 / a + 1 / b"),
    ],
)
def test_control_rendering_is_how_we_actually_write_it(name, conventional):
    """Under G0 the renderer must reproduce conventional notation character for character."""
    formula = next(item for item in CORPUS if item.name == name)
    assert formula.source == conventional
    assert render(formula_tree(formula), CONTROL) == conventional


def test_the_roadmaps_reversal_is_reproduced():
    """Under G01, where ``+`` binds tightest, the distributive law's cheap direction flips."""
    g01 = BY_ID["G01"]
    factored = formula_tree(next(item for item in CORPUS if item.name == "distributive_law_factored"))
    expanded = formula_tree(next(item for item in CORPUS if item.name == "distributive_law_expanded"))
    assert render(factored, CONTROL) == "a * (b + c)" and parenthesis_cost(factored, CONTROL) == 1
    assert render(expanded, CONTROL) == "a * b + a * c" and parenthesis_cost(expanded, CONTROL) == 0
    assert render(factored, g01) == "a * b + c" and parenthesis_cost(factored, g01) == 0
    assert render(expanded, g01) == "(a * b) + (a * c)" and parenthesis_cost(expanded, g01) == 2
    square = formula_tree(next(item for item in CORPUS if item.name == "binomial_square_factored"))
    assert render(square, g01) == "a + b * a + b"


# --------------------------------------------------------------------------- the null model


@pytest.mark.parametrize(
    "name", ["cylinder_volume", "standard_error", "density", "work_done", "ohm_series_resistance"]
)
def test_single_operator_formulas_cost_the_same_under_all_twenty_five_grammars(name):
    formula = next(item for item in CORPUS if item.name == name)
    tree = formula_tree(formula)
    assert len(tree_operators(tree)) == 1
    costs = {grammar.id: parenthesis_cost(tree, grammar) for grammar in GRAMMARS}
    assert len(set(costs.values())) == 1


def test_tree_operators_walks_both_subtrees():
    """Support is the whole tree, not the left spine - a right-hand operator still counts."""
    assert tree_operators(parse("a + b * c", CONTROL)) == ("+", "*")
    assert tree_operators(parse("a - b / c", CONTROL)) == ("-", "/")
    assert tree_operators(parse("a / (b - c) + a", CONTROL)) == ("+", "/", "-")
    rows = {row["name"]: row for row in cost_rows(workers=1)}
    assert rows["mixed_number"]["operators"] == ("+", "/")
    assert rows["mixed_number"]["support_size"] == 2
    assert rows["quadratic_expanded"]["support_size"] == 2
    assert rows["variance_of_two_points"]["support_size"] == 4


def test_a_right_nested_single_operator_tree_is_also_convention_insensitive():
    """One operator type, but a bracket every grammar must pay: constant does not mean free."""
    tree = parse("a - (b - c)", CONTROL)
    assert tree_operators(tree) == ("-",)
    costs = {grammar.id: parenthesis_cost(tree, grammar) for grammar in GRAMMARS}
    assert set(costs.values()) == {1}


def test_null_model_separates_the_forced_floor_from_the_movable_remainder():
    model = null_model()
    assert model["constant_count"] == 5
    assert model["movable_count"] == 53
    assert model["constant_support_sizes"] == {1: 5}
    assert model["single_operator_constant"] == 5
    assert model["constant_at_zero"] == 5
    assert model["forced_total"] == 0
    assert model["full_spread"] == model["movable_spread"] == 54
    assert model["spread_survival"] == 1.0
    assert model["ranking_identical"] is True
    assert model["control_rank_full"] == model["control_rank_movable"] == 11
    assert model["best_full"] == model["best_movable"] == "G09"
    assert model["oracle_total"] == 3
    assert model["best_total"] == 29
    assert model["oracle_gap"] == 26


# ------------------------------------------------------------------------- the cost table


def test_control_grammar_rank_is_pinned():
    table = cost_table()
    assert table["control_id"] == "G0"
    assert table["control_total"] == 53
    assert table["control_rank"] == 11
    assert table["grammar_count"] == 25
    assert table["formula_count"] == 58


def test_cheapest_and_dearest_grammars_are_pinned():
    table = cost_table()
    assert table["best"]["id"] == "G09"
    assert table["best"]["precedence"] == "- * + /"
    assert table["best"]["total"] == 29
    assert table["worst"]["id"] == "G20"
    assert table["worst"]["total"] == 83
    assert table["spread"] == 54
    assert table["control_minus_best"] == 24
    assert round(table["control_minus_best_percent"], 2) == 45.28
    assert table["best_alternative"]["id"] == "G09"


def test_ranking_is_a_competition_ranking_over_all_twenty_five_grammars():
    table = cost_table()
    ranking = table["ranking"]
    assert len(ranking) == 25
    assert {entry["id"] for entry in ranking} == {grammar.id for grammar in all_grammars()}
    totals = [entry["total"] for entry in ranking]
    assert totals == sorted(totals)
    assert ranking[0]["rank"] == 1
    for entry in ranking:
        assert entry["rank"] == 1 + sum(1 for other in ranking if other["total"] < entry["total"])


def test_free_under_control_and_under_the_cheapest_grammar():
    assert len(free_under(CONTROL)) == 24
    assert len(free_under(BY_ID["G09"])) == 39
    assert "distributive_law_expanded" in free_under(CONTROL)
    assert "mean_of_two" not in free_under(CONTROL)
    assert "mean_of_two" in free_under(BY_ID["G09"])


def test_free_transition_names_what_becomes_natural_and_what_stops_being_natural():
    transition = free_transition(CONTROL, BY_ID["G09"])
    assert transition["from"] == "G0" and transition["to"] == "G09"
    assert len(transition["gained"]) == 23
    assert len(transition["lost"]) == 8
    assert "slope_through_two_points" in transition["gained"]
    assert "mean_of_two" in transition["gained"]
    assert "harmonic_sum" in transition["lost"]
    assert "variance_shortcut" in transition["lost"]
    assert set(transition["gained"]) & set(transition["lost"]) == set()
    assert len(transition["free_after"]) == len(transition["kept"]) + len(transition["gained"])


# ------------------------------------------------------------------ sensitivity and areas


def test_convention_sensitivity_separates_immovable_from_swinging_formulas():
    sensitivity = convention_sensitivity()
    assert sensitivity["constant_count"] == 5
    assert sensitivity["variable_count"] == 53
    assert set(sensitivity["constant_formulas"]) == {
        "cylinder_volume",
        "standard_error",
        "density",
        "work_done",
        "ohm_series_resistance",
    }
    assert sensitivity["max_range"] == 6
    assert sensitivity["most_sensitive"] == ("distance_component_sum",)
    assert sensitivity["control_optimal_count"] == 24
    top = sensitivity["by_range"][:2]
    assert [entry["name"] for entry in top] == ["distance_component_sum", "variance_of_two_points"]
    assert top[0]["min"] == 0 and top[0]["max"] == 6 and top[0]["control_cost"] == 4
    for entry in sensitivity["formulas"]:
        assert entry["range"] == entry["max"] - entry["min"]
        assert entry["constant"] is (entry["range"] == 0)


def test_the_ranking_does_not_hold_uniformly_across_areas():
    areas = area_table()
    assert areas["areas"] == ["algebra", "arithmetic", "calculus", "geometry", "physics", "statistics"]
    assert areas["unanimous"] is False
    assert areas["global_best"] == "G09"
    assert set(areas["areas_won_by_global_best"]) == {"algebra", "arithmetic", "calculus", "geometry"}
    assert areas["area_winners"]["statistics"] == ("G14",)
    assert areas["area_winners"]["physics"] == ("G13", "G15")
    assert areas["control_ranks"] == {
        "algebra": 11,
        "arithmetic": 8,
        "calculus": 12,
        "geometry": 17,
        "physics": 8,
        "statistics": 8,
    }
    for report in areas["per_area"].values():
        assert report["best_total"] <= report["control_total"] <= report["worst_total"]


# ------------------------------------------------------------------------------ execution


def test_resolve_worker_count_is_derived_from_cores_and_stays_sequential_on_a_small_corpus():
    assert resolve_worker_count(len(CORPUS)) == 1
    assert resolve_worker_count(10_000) > 1
    assert resolve_worker_count(10_000, workers=3) == 3
    assert resolve_worker_count(2, workers=99) == 2


def test_sequential_and_parallel_paths_agree():
    sequential = cost_rows(workers=1)
    parallel = cost_rows(workers=2)
    assert sequential == parallel
    assert len(sequential) == 58


def test_full_report_assembles_every_section():
    report = notational_cost_report()
    assert report["round_trip"]["holds"] is True
    assert report["minimality"]["minimal"] is True
    assert report["corpus"]["canonical_sources"] is True
    assert report["cost_table"]["control_rank"] == 11
    assert report["null_model"]["best_movable"] == "G09"
    assert len(report["free_under_control"]) == 24
    assert len(report["free_under_best_alternative"]) == 39
    assert report["free_transition"]["to"] == "G09"
