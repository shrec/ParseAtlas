"""Experiment 0045: does the flagship result survive exponentiation?

Every assertion here is a pin on measured output, and the order is the order of the card: the
conservative-extension audit comes first, because if Generation 2 does not reproduce Generation 1
on Generation 1's own language then no other number in the module means anything.

The expensive whole-registry sweeps are computed once per module and shared, and the sequential
path is forced with ``workers=1`` everywhere except the one test whose subject is the pool.
"""

from fractions import Fraction

import pytest

from parseatlas import generation_two
from parseatlas.generation_two import (
    ASSOCIATIVITY,
    CONTROL_1,
    CONTROL_2,
    CORPUS_2,
    GRAMMARS_1,
    GRAMMARS_2,
    OPERATORS_2,
    POOL_STARTUP_SECONDS,
    PUBLISHED_CLAIMS,
    QUADRATIC_GENERATION_ONE,
    QUADRATIC_GENERATION_TWO,
    Formula2,
    agreement_audit,
    canonicalize2,
    child_threshold2,
    control_ranking,
    corpus_audit2,
    default_worker_count,
    distinguishing_power,
    embed_generation_one,
    embeddings_of,
    formula_tree2,
    generation_one_sources,
    minimality_audit2,
    minimality_witnesses2,
    object_groups,
    pair_is_required,
    parenthesis_cost2,
    parse2,
    quadratic_worlds,
    rank_percentile,
    render2,
    restricted_order,
    roots_over_c,
    round_trip_audit2,
    should_parallelise,
    survival_table,
    to_sympy2,
    tokenize2,
    worker_count_for,
)
from parseatlas.grammar import Grammar
from parseatlas.notational_cost import bracket_pairs
from parseatlas.parser import Binary, Number, Variable, parse


@pytest.fixture(scope="module")
def agreement():
    return agreement_audit()


@pytest.fixture(scope="module")
def quadratic():
    return quadratic_worlds(workers=1)


@pytest.fixture(scope="module")
def survival():
    return survival_table(workers=1)


@pytest.fixture(scope="module")
def ranking():
    return control_ranking(workers=1)


# ------------------------------------------- FIRST: Generation 2 is a conservative extension


def test_generation_two_reproduces_generation_one_on_every_cell(agreement):
    """The load-bearing audit: 11562 cells, byte-identical trees, zero disagreements."""
    assert agreement["conservative"] is True
    assert agreement["disagreements"] == 0
    assert agreement["disagreeing"] == ()
    assert agreement["sources"] == 94
    assert agreement["generation_one_grammars"] == 25
    assert agreement["embeddings"] == 123
    assert agreement["cells"] == 11562


def test_the_audit_covers_every_position_the_power_can_be_embedded_at():
    """24 strict grammars give 5 positions each and the tied control gives 3: 123 embeddings."""
    assert len(embeddings_of(CONTROL_1)) == 3
    assert sum(len(embeddings_of(grammar)) for grammar in GRAMMARS_1) == 123
    embedded = embed_generation_one(CONTROL_1, 0)
    assert embedded.levels == (("^",), ("*", "/"), ("+", "-"))
    assert embed_generation_one(CONTROL_1, 2).levels == (("*", "/"), ("+", "-"), ("^",))


def test_the_audit_compares_trees_and_not_strings(agreement):
    """A cell is dataclass equality on Generation 1's own node types, so nothing is translated."""
    source = "a * b + c * d"
    assert parse2(source, embed_generation_one(CONTROL_1, 0)) == parse(source, CONTROL_1)
    assert isinstance(parse2(source, CONTROL_2), Binary)
    assert agreement["cells"] == len(generation_one_sources()) * 123


def test_the_audit_would_fail_if_the_generation_two_parser_diverged():
    """The audit is a real check: a grammar whose restriction differs really does disagree."""
    reordered = Grammar("H_reordered", ("^", "+", "-", "*", "/"))
    assert parse2("a * b + c", reordered) != parse("a * b + c", CONTROL_1)


def test_the_agreement_audit_notices_a_divergence_when_one_is_put_in_front_of_it():
    """The audit's comparison must be load-bearing, not merely present.

    ``agreement_audit`` is this module's first obligation -- if the Generation 2 parser is not a
    conservative extension then nothing else here is about the same language.  Review found that
    replacing its comparison with ``if False:`` left every test passing, because each test asserted
    only that the audit RETURNS conservative.  None put a real divergence in front of it and made it
    notice, so the audit could report a clean pass while comparing nothing.

    A divergence cannot be injected through the public arguments -- the audit builds its own
    Generation 2 embeddings -- so the parser it calls is replaced for the duration with one that
    mis-parses a single source.  An audit that compares reports it; an audit whose comparison has
    been disabled reports conservative and fails here.
    """
    honest = agreement_audit()
    assert honest["conservative"] is True
    assert honest["disagreements"] == 0
    assert honest["disagreeing"] == ()
    assert honest["cells"] > 10_000

    real_parse2 = generation_two.parse2
    poisoned_source = "a * b + c"

    def divergent(source, grammar):
        tree = real_parse2(source, grammar)
        if source == poisoned_source:
            return Binary("+", Variable("a"), Variable("b"))
        return tree

    generation_two.parse2 = divergent
    try:
        caught = agreement_audit(sources=(poisoned_source, "a - b"))
    finally:
        generation_two.parse2 = real_parse2

    assert caught["conservative"] is False, "the audit did not notice a divergence"
    assert caught["disagreements"] > 0
    assert all(row["source"] == poisoned_source for row in caught["disagreeing"])

    # and the module is left exactly as it was found
    assert agreement_audit()["conservative"] is True


# ------------------------------------------------------- the power is right-associative


def test_the_power_is_right_associative_on_the_hand_worked_example():
    """``2^3^2`` is ``2^9 = 512``, not ``(2^3)^2 = 64``."""
    tree = parse2("2^3^2", CONTROL_2)
    assert to_sympy2(tree) == 512
    assert to_sympy2(tree) != 64


def test_the_power_is_right_associative_as_a_tree():
    """The same statement without arithmetic: the nesting is to the right."""
    two, three = Number(Fraction(2)), Number(Fraction(3))
    assert parse2("2^3^2", CONTROL_2) == Binary("^", two, Binary("^", three, two))
    assert parse2("2^3^2", CONTROL_2) != Binary("^", Binary("^", two, three), two)


def test_every_other_operator_stays_left_associative():
    a, b, c = Variable("a"), Variable("b"), Variable("c")
    assert parse2("a - b - c", CONTROL_2) == Binary("-", Binary("-", a, b), c)
    assert parse2("a / b / c", CONTROL_2) == Binary("/", Binary("/", a, b), c)
    assert ASSOCIATIVITY == {"^": "right", "*": "left", "/": "left", "+": "left", "-": "left"}


def test_right_associativity_decides_which_side_needs_a_bracket():
    """``a^b^c`` is free and ``(a^b)^c`` costs one, in every grammar of the registry."""
    a, b, c = Variable("a"), Variable("b"), Variable("c")
    right = Binary("^", a, Binary("^", b, c))
    left = Binary("^", Binary("^", a, b), c)
    for grammar in GRAMMARS_2:
        assert render2(right, grammar) == "a^b^c"
        assert render2(left, grammar) == "(a^b)^c"


def test_the_bracket_thresholds_are_the_two_parser_terms():
    """Left threshold follows the CHILD's associativity, right threshold the PARENT's."""
    assert child_threshold2(3, "left", "left", "left") == 3
    assert child_threshold2(3, "left", "left", "right") == 4
    assert child_threshold2(3, "right", "right", "left") == 3
    assert child_threshold2(3, "right", "left", "left") == 4
    with pytest.raises(ValueError):
        child_threshold2(3, "middle", "left", "left")


def test_the_registry_is_one_hundred_and_twenty_strict_orderings_plus_the_control():
    assert OPERATORS_2 == ("^", "*", "/", "+", "-")
    assert len(GRAMMARS_2) == 121
    assert GRAMMARS_2[0] is CONTROL_2
    assert CONTROL_2.id == "H0"
    assert CONTROL_2.levels == (("^",), ("*", "/"), ("+", "-"))
    assert len({grammar.id for grammar in GRAMMARS_2}) == 121
    assert len({grammar.precedence for grammar in GRAMMARS_2[1:]}) == 120
    assert all(len(grammar.levels) == 5 for grammar in GRAMMARS_2[1:])


def test_the_tokenizer_keeps_generation_ones_rational_literal():
    """``1/2`` unspaced is ONE literal in both generations; changing it would break the audit."""
    assert [token.value for token in tokenize2("1/2 + a")][:3] == ["1/2", "+", "a"]
    assert [token.value for token in tokenize2("1 / 2")][:3] == ["1", "/", "2"]
    assert parse2("1/2 + a", CONTROL_2) == Binary("+", Number(Fraction(1, 2)), Variable("a"))


# ------------------------------------------------------------ round trip and minimality


def test_the_round_trip_holds_over_the_whole_grid():
    audit = round_trip_audit2()
    assert audit["holds"] is True
    assert audit["failures"] == 0
    assert audit["checks"] == 4598
    assert audit["checks"] == len(CORPUS_2) * len(GRAMMARS_2)


def test_every_bracket_is_load_bearing_over_the_whole_grid():
    audit = minimality_audit2()
    assert audit["minimal"] is True
    assert audit["violations"] == 0
    assert audit["brackets_checked"] == 5665


def test_minimality_is_checked_by_deletion_and_not_by_argument():
    tree = formula_tree2(Formula2("probe", "algebra", "(a + b)^2"))
    witnesses = minimality_witnesses2(tree, CONTROL_2)
    assert len(witnesses) == 1
    assert witnesses[0]["without_pair"] == "a + b^2"
    assert witnesses[0]["required"] is True


def test_a_redundant_bracket_would_be_caught():
    """The minimality check is exercised on a writing that really does carry a spare bracket."""
    tree = formula_tree2(Formula2("probe", "algebra", "a^b^c"))
    assert render2(tree, CONTROL_2) == "a^b^c"
    redundant = "a^(b^c)"
    assert parse2(redundant, CONTROL_2) == tree
    assert pair_is_required(redundant, bracket_pairs(redundant)[0], tree, CONTROL_2)["required"] is False
    required = "(a^b)^c"
    left = parse2(required, CONTROL_2)
    assert pair_is_required(required, bracket_pairs(required)[0], left, CONTROL_2)["required"] is True


def test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement():
    """``NF-2026-00005``: Generation 2 reuses the project's triple, domain constant and all."""
    quadratic = canonicalize2(parse2("a * x^2 + b * x + c", CONTROL_2))
    reciprocal = canonicalize2(parse2("1 / x", CONTROL_2))
    assert quadratic["domain"] == reciprocal["domain"] == "R"
    assert quadratic["excluded_points"] == []
    assert reciprocal["excluded_points"] == ["0"]


def test_the_corpus_is_written_minimally_in_both_languages():
    audit = corpus_audit2()
    assert audit["canonical_sources"] is True
    assert audit["non_canonical"] == ()
    assert audit["duplicate_names"] == ()
    assert audit["size"] == 38
    assert audit["area_count"] == 6
    assert audit["expressible_in_generation_one"] == 26
    assert len(audit["generation_two_only"]) == 12


# -------------------------------------------------------------------------- THE HEADLINE


def test_the_flagship_split_does_not_survive(quadratic):
    """The answer the report opens with, pinned literally."""
    assert quadratic["verdict"] == "does not survive"
    assert quadratic["survives"] is False
    assert quadratic["objects_generation_one"] == 2
    assert quadratic["objects_generation_two"] == 6
    assert quadratic["cubic_survives"] is False
    assert quadratic["quadratic_survives"] is True


def test_the_generation_one_split_is_thirteen_twelve(quadratic):
    """0035's own measurement, re-derived here rather than quoted."""
    block = quadratic["generation_one"]
    assert block["source"] == QUADRATIC_GENERATION_ONE
    assert block["registry_size"] == 25
    assert block["objects"] == 2
    assert [group["count"] for group in block["groups"]] == [13, 12]
    assert [group["canonical"] for group in block["groups"]] == [
        "a*x**2 + b*x + c",
        "a*x*(b + x)*(c + x)",
    ]
    assert block["groups"][0]["contains_control"] is True
    assert block["groups"][1]["root_roots"] == ["0", "-b", "-c"]
    assert block["groups"][1]["root_requires_radical"] is False


def test_thirteen_and_twelve_are_registry_sizes_and_not_mathematics(quadratic):
    """The SAME string in the 121-grammar registry splits 61/60: two blocks either way."""
    block = quadratic["generation_two_old_writing"]
    assert block["registry_size"] == 121
    assert block["blocks"] == 2
    assert block["objects"] == 2
    assert [group["count"] for group in block["groups"]] == [61, 60]
    assert [group["canonical"] for group in block["groups"]] == [
        "a*x**2 + b*x + c",
        "a*x*(b + x)*(c + x)",
    ]
    assert quadratic["registry_effect_only"] is True


def test_the_generation_two_writing_denotes_six_objects_in_blocks_of_twenty(quadratic):
    """Group sizes, canonical forms and the control's group, pinned cell by cell."""
    block = quadratic["generation_two"]
    assert block["source"] == QUADRATIC_GENERATION_TWO
    assert block["support"] == ("+", "*", "^")
    assert block["blocks"] == 6
    assert block["grammars_per_block"] == 20
    assert block["objects"] == 6
    assert [group["count"] for group in block["groups"]] == [21, 20, 20, 20, 20, 20]
    assert [group["canonical"] for group in block["groups"]] == [
        "a*x**2 + b*x + c",
        "(a*x)**((b + 2)*(c + x))",
        "(a*x)**(b*x + c + 2)",
        "a*(b + x**2)*(c + x)",
        "a**2*x**2 + b*x + c",
        "a*x**(b + 2)*(c + x)",
    ]
    assert [group["restricted_orders"] for group in block["groups"]] == [
        ("^ > * > +",),
        ("+ > * > ^",),
        ("* > + > ^",),
        ("^ > + > *",),
        ("* > ^ > +",),
        ("+ > ^ > *",),
    ]


def test_the_control_sits_in_the_quadratic_group_of_twenty_one(quadratic):
    block = quadratic["generation_two"]
    assert block["control_object"] == "O01"
    control = block["groups"][0]
    assert control["contains_control"] is True
    assert control["count"] == 21
    assert control["canonical"] == "a*x**2 + b*x + c"
    assert control["root_degree"] == 2
    assert control["root_roots"] == [
        "(-b - sqrt(-4*a*c + b**2))/(2*a)",
        "(-b + sqrt(-4*a*c + b**2))/(2*a)",
    ]
    assert control["root_requires_radical"] is True
    assert quadratic["quadratic_worlds_generation_two"] == 21


def test_no_generation_two_world_reads_the_radical_free_cubic(quadratic):
    """The object 0035 is known for is denoted by none of the 121 worlds."""
    block = quadratic["generation_two"]
    assert "a*x*(b + x)*(c + x)" not in block["canonical_forms"]
    solved = [group for group in block["groups"] if group["root_attempted"]]
    assert [group["root_requires_radical"] for group in solved] == [True, True, True]
    assert not any(group["root_requires_radical"] is False for group in solved)


def test_the_roots_of_every_solved_generation_two_reading_are_pinned(quadratic):
    block = quadratic["generation_two"]
    by_id = {group["canonical"]: group for group in block["groups"]}
    assert by_id["a*(b + x**2)*(c + x)"]["root_roots"] == ["-c", "-sqrt(-b)", "sqrt(-b)"]
    assert by_id["a*(b + x**2)*(c + x)"]["root_degree"] == 3
    assert by_id["a**2*x**2 + b*x + c"]["root_roots"] == [
        "(-b - sqrt(-4*a**2*c + b**2))/(2*a**2)",
        "(-b + sqrt(-4*a**2*c + b**2))/(2*a**2)",
    ]


def test_a_reading_without_roots_says_so_instead_of_reporting_none(quadratic):
    """An empty root list would read as "no roots"; an unattempted one must say it was not tried."""
    block = quadratic["generation_two"]
    unattempted = [group for group in block["groups"] if not group["root_attempted"]]
    assert len(unattempted) == 3
    for group in unattempted:
        assert group["root_roots"] == []
        assert group["root_requires_radical"] is None
        assert group["root_reason"] == (
            "the reading is neither a polynomial nor a rational function in the variable"
        )


def test_roots_over_c_refuses_a_symbolic_exponent_rather_than_guessing():
    expression = to_sympy2(parse2("(a * x)^(b * x + c + 2)", CONTROL_2))
    record = roots_over_c(expression, "x")
    assert record["attempted"] is False
    assert record["requires_radical"] is None
    assert record["root_domain"] == "C"
    absent = roots_over_c(to_sympy2(parse2("a + b", CONTROL_2)), "x")
    assert absent["reason"] == "the reading does not contain the variable"


# ------------------------------------------------- every published claim, pinned by name


EXPECTED_VERDICTS = {
    "0035_quadratic_object_count": "does not survive",
    "0035_quadratic_radical_free_cubic": "does not survive",
    "0035_quadratic_radical_free_worlds": "does not survive",
    "0035_binomial_square_object_count": "does not survive",
    "0035_binomial_square_present": "survives with different numbers",
    "0035_difference_of_squares_object_count": "survives",
    "0035_circle_object_count": "survives",
    "0035_circle_present": "survives with different numbers",
    "0036_pythagorean_identity": "survives with different numbers",
}


def test_every_published_claim_has_a_pinned_verdict(survival):
    assert survival["claims"] == len(PUBLISHED_CLAIMS) == 9
    assert {row["claim_id"]: row["verdict"] for row in survival["rows"]} == EXPECTED_VERDICTS


def test_the_claims_that_do_not_survive_are_named(survival):
    assert survival["does_not_survive"] == (
        "0035_quadratic_object_count",
        "0035_quadratic_radical_free_cubic",
        "0035_quadratic_radical_free_worlds",
        "0035_binomial_square_object_count",
    )
    assert survival["survives_with_different_numbers"] == (
        "0035_binomial_square_present",
        "0035_circle_present",
        "0036_pythagorean_identity",
    )
    assert survival["survives"] == (
        "0035_difference_of_squares_object_count",
        "0035_circle_object_count",
    )


def test_only_the_conventional_object_survives_the_rewriting(survival):
    """In every row the single object the two generations share is the control's own reading."""
    assert survival["shared_object_counts"] == (1,) * 9
    assert survival["only_the_control_object_is_shared"] is True
    assert survival["control_objects_unchanged"] is True


def test_the_pythagorean_identity_holds_in_sixty_one_of_the_one_hundred_and_twenty_one(survival):
    row = next(row for row in survival["rows"] if row["claim_id"] == "0036_pythagorean_identity")
    assert row["generation_one_source"] == "s * s + c * c"
    assert row["generation_two_source"] == "s^2 + c^2"
    assert row["measured_generation_one"] == 13
    assert row["measured_generation_two"] == 61
    assert row["generation_one_objects"] == row["generation_two_objects"] == 2
    assert row["generation_two_canonical_forms"] == ("c**2 + s**2", "s**((c + 2)**2)")
    assert round(row["generation_one_share"], 2) == 52.0
    assert round(row["generation_two_share"], 2) == 50.41


def test_the_circle_keeps_its_object_count_but_not_its_objects(survival):
    row = next(row for row in survival["rows"] if row["claim_id"] == "0035_circle_object_count")
    assert row["generation_one_objects"] == row["generation_two_objects"] == 4
    assert row["generation_one_group_sizes"] == (9, 8, 4, 4)
    assert row["generation_two_group_sizes"] == (41, 40, 20, 20)
    assert row["same_object_set"] is False
    assert row["shared_objects"] == ("-r**2 + x**2 + y**2",)


def test_the_binomial_square_gains_objects_and_merges_two_blocks(survival):
    row = next(
        row for row in survival["rows"] if row["claim_id"] == "0035_binomial_square_object_count"
    )
    assert row["generation_one_objects"] == 2
    assert row["generation_two_objects"] == 5
    assert row["generation_two_blocks"] == 6
    assert row["generation_two_group_sizes"] == (41, 20, 20, 20, 20)
    groups = object_groups("a^2 + 2 * a * b + b^2", 2, "a", False, 1)
    assert groups["groups"][0]["restricted_orders"] == ("^ > * > +", "* > ^ > +")
    assert groups["groups"][0]["block_count"] == 2


def test_the_quadratic_needs_a_radical_in_every_generation_two_world_that_can_be_solved(survival):
    row = next(
        row for row in survival["rows"] if row["claim_id"] == "0035_quadratic_radical_free_worlds"
    )
    assert row["measured_generation_one"] == 12
    assert row["measured_generation_two"] == 0
    assert row["generation_one_unattempted_worlds"] == 0
    assert row["generation_two_unattempted_worlds"] == 60


def test_the_semantic_key_is_not_canonical_text_alone():
    """The Generation 2 sine series: 17 objects, 16 canonical texts, two of them reading ``0``."""
    groups = object_groups("x - x^3 / 6 + x^5 / 120", 2, "x", False, 1)
    assert groups["objects"] == 17
    assert len({group["canonical"] for group in groups["groups"]}) == 16
    zeros = [group for group in groups["groups"] if group["canonical"] == "0"]
    assert len(zeros) == 2
    assert zeros[0]["excluded_points"] != zeros[1]["excluded_points"]
    assert zeros[0]["excluded_points"] == ["-6"]
    assert sum(group["count"] for group in groups["groups"]) == 121


def test_the_control_group_is_found_by_its_flag_and_not_by_being_the_largest():
    """``m * v^2 / 2``: the control's object holds 41 worlds and another holds 60."""
    groups = object_groups("m * v^2 / 2", 2, "v", False, 1)
    assert [group["count"] for group in groups["groups"]] == [60, 41, 20]
    assert groups["control_object"] == "O02"
    assert groups["groups"][0]["contains_control"] is False
    assert groups["groups"][1]["contains_control"] is True
    assert groups["groups"][1]["canonical"] == "m*v**2/2"
    assert groups["control_canonical"] == "m*v**2/2"


# ------------------------------------------------------------------------- the null model


def test_the_null_model_split_is_pinned(ranking):
    """Entries that can separate all 120 against entries that cannot, and by how much."""
    power = ranking["distinguishing"]
    assert power["corpus_size"] == 38
    assert power["strict_count"] == 120
    assert power["separating_all_count"] == 3
    assert power["separating_all"] == (
        "taylor_second_order",
        "projectile_height",
        "annuity_future_value",
    )
    assert power["not_separating_all_count"] == 35
    assert power["support_histogram"] == {1: 3, 2: 10, 3: 17, 4: 5, 5: 3}


def test_an_entrys_blocks_are_the_factorial_of_its_support():
    power = distinguishing_power(workers=1)
    by_name = {entry["name"]: entry for entry in power["entries"]}
    assert by_name["iterated_power"]["support_size"] == 1
    assert by_name["iterated_power"]["blocks"] == 1
    assert by_name["iterated_power"]["grammars_per_block"] == 120
    assert by_name["quadratic_expanded"]["support_size"] == 3
    assert by_name["quadratic_expanded"]["blocks"] == 6
    assert by_name["quadratic_expanded"]["grammars_per_block"] == 20
    assert by_name["projectile_height"]["support_size"] == 5
    assert by_name["projectile_height"]["blocks"] == 120
    assert by_name["projectile_height"]["grammars_per_block"] == 1


def test_the_upper_bound_of_one_hundred_and_twenty_is_never_reached():
    """Full support is necessary but not sufficient: the best entry writes 36 distinct strings."""
    power = distinguishing_power(workers=1)
    by_name = {entry["name"]: entry for entry in power["entries"]}
    assert by_name["taylor_second_order"]["distinct_renderings"] == 36
    assert by_name["projectile_height"]["distinct_renderings"] == 28
    assert by_name["annuity_future_value"]["distinct_renderings"] == 16
    assert max(entry["distinct_renderings"] for entry in power["entries"]) == 36


def test_four_entries_cannot_move_a_ranking_at_all(ranking):
    assert ranking["constant_entries"] == (
        "power_of_power_rule",
        "iterated_power",
        "binary_place_value",
        "exponential_growth",
    )
    assert len(ranking["movable_entries"]) == 34
    assert ranking["control_rank_stable"] is True
    assert ranking["ranking_identical"] is True


def test_the_corpus_as_a_whole_separates_every_grammar_in_the_registry(ranking):
    """No single entry sees past its block; the 38 together resolve all 121 conventions."""
    assert ranking["full"]["distinct_cost_profiles"] == 121
    assert ranking["full"]["distinct_rendering_profiles"] == 121
    assert ranking["full"]["distinct_totals"] == 40


def test_the_restricted_order_is_the_block_label():
    assert restricted_order(CONTROL_2, ("+", "*", "^")) == "^ > * > +"
    assert restricted_order(CONTROL_2, ("+", "-", "*", "/")) == "* = / > + = -"
    assert restricted_order(GRAMMARS_2[1], ("+", "-", "*", "/")) == "* > / > + > -"


# ------------------------------------------------------------------------ the cost ranking


def test_the_generation_two_control_is_second_of_one_hundred_and_twenty_one(ranking):
    full = ranking["full"]
    assert full["entries"] == 38
    assert full["registry_size"] == 121
    assert full["control_total"] == 25
    assert full["control_rank"] == 2
    assert round(full["control_percentile"], 2) == 1.65
    assert full["control_rank_among_strict"] == 2
    assert round(full["control_percentile_among_strict"], 2) == 1.67
    assert full["strictly_cheaper_count"] == 1
    assert full["best"] == {"rank": 1, "id": "H001", "total": 24}
    assert full["worst"] == {"rank": 121, "id": "H120", "total": 70}
    assert full["spread"] == 46


def test_the_one_grammar_that_beats_the_control_beats_it_by_one_tie_break():
    """H001 is the control with its ties broken; the single bracket is the ``* /`` tie."""
    assert GRAMMARS_2[1].id == "H001"
    assert GRAMMARS_2[1].precedence == ("^", "*", "/", "+", "-")
    differing = [
        formula.name
        for formula in CORPUS_2
        if parenthesis_cost2(formula_tree2(formula), CONTROL_2)
        != parenthesis_cost2(formula_tree2(formula), GRAMMARS_2[1])
    ]
    assert differing == ["gaussian_exponent"]
    tree = formula_tree2(next(f for f in CORPUS_2 if f.name == "gaussian_exponent"))
    assert render2(tree, CONTROL_2) == "(x - m)^2 / (2 * s^2)"
    assert render2(tree, GRAMMARS_2[1]) == "(x - m)^2 / 2 * s^2"


def test_the_same_mathematics_ranks_the_generation_one_control_sixth_of_twenty_five(ranking):
    """Same 26 objects, one written with powers and one with product chains."""
    assert ranking["shared_corpus_size"] == 26
    shared_two = ranking["shared_generation_two"]
    shared_one = ranking["shared_generation_one"]
    assert shared_two["control_rank"] == 2
    assert round(shared_two["control_percentile"], 2) == 1.65
    assert shared_one["control_id"] == "G0"
    assert shared_one["registry_size"] == 25
    assert shared_one["control_rank"] == 6
    assert round(shared_one["control_percentile"], 2) == 24.0
    assert shared_one["best"]["id"] == "G10"


def test_the_cost_of_the_corpus_is_exactly_linear_in_where_the_power_sits(ranking):
    """T25's question answered over all 120: each position holds 24 grammars, and the means step."""
    table = ranking["power_position"]
    assert [table["positions"][position]["grammars"] for position in (1, 2, 3, 4, 5)] == [24] * 5
    assert table["means"] == [34.0, 40.5, 47.0, 53.5, 60.0]
    assert table["steps"] == [6.5, 6.5, 6.5, 6.5]
    assert table["monotone"] is True
    assert table["constant_step"] is True
    assert table["gap"] == 26.0
    assert table["control_total"] == 25


def test_writing_the_same_objects_with_powers_costs_the_control_less(ranking):
    assert ranking["shared_generation_one"]["control_total"] == 26
    assert ranking["shared_generation_two"]["control_total"] == 14
    assert ranking["shared_control_saving"] == 12
    assert round(ranking["shared_control_saving_percent"], 2) == 46.15
    assert ranking["power_position_shared"]["steps"] == [6.25, 6.25, 6.25, 6.25]


def test_a_rank_is_reported_with_its_percentile_because_ordinals_do_not_compare():
    assert rank_percentile(3, 25) == 12.0
    assert round(rank_percentile(15, 120), 4) == 12.5
    assert round(rank_percentile(2, 121), 2) == 1.65


# ---------------------------------------------------------------------------- multicore


def test_sequential_and_parallel_agree_on_the_semantic_grid():
    sequential = object_groups(QUADRATIC_GENERATION_TWO, 2, "x", False, workers=1)
    parallel = object_groups(QUADRATIC_GENERATION_TWO, 2, "x", False, workers=2)
    assert sequential == parallel


def test_sequential_and_parallel_agree_on_the_cost_grid():
    from parseatlas.generation_two import cost_rows2

    assert cost_rows2(workers=1) == cost_rows2(workers=2)


def test_the_worker_count_comes_from_the_observed_cores_with_headroom():
    assert worker_count_for(16, 1000) == 15
    assert worker_count_for(1, 1000) == 1
    assert worker_count_for(16, 3) == 3
    assert default_worker_count(1000) >= 1


def test_the_parallel_decision_is_a_measurement_and_not_a_cell_count():
    """A pool is raised only when the divided work beats the measured startup it has to pay."""
    assert should_parallelise(121, 6.3e-03, 15) is False
    assert should_parallelise(5000, 6.3e-03, 15) is True
    assert should_parallelise(5000, 6.3e-03, 1) is False
    assert should_parallelise(1, 10.0, 15) is False
    assert POOL_STARTUP_SECONDS > 0
