"""Experiment 0050: where the flat precedence model ends.

The order is the order of the card. The conservative-extension audit comes first, because if the
tiered parser does not reproduce Generation 1 on Generation 1's own language then no other number
in the module means anything - and the audit itself is put in front of a real divergence rather
than only asked whether it says "conservative", which is the hole a surviving mutant found in 0045.

Every expensive sweep is a module-scoped fixture computed once. The parallel path is the measured
default; the two tests whose subject is the pool force both paths over the same work.
"""

from fractions import Fraction

import os

import pytest

from parseatlas.grammar import all_grammars
from parseatlas.parser import Binary, Number, Variable, parse
from parseatlas.tiered_syntax import (
    ALIAS_JUXTAPOSITION,
    BINARY_OPERATORS,
    CONTROL_BASE,
    CONTROL_CONVENTION,
    CONVENTION_KINDS,
    CONVENTION_SPACE_SIZE,
    CONVENTIONS,
    CORPUS_3,
    CORPUS_SOURCES,
    JUX,
    LITERAL_POLICIES,
    LITERAL_POLICY,
    NEG,
    REJECTED,
    ROLES,
    TIGHT_JUXTAPOSITION,
    Convention,
    Negate,
    agreement_audit,
    audit_cell,
    alias_equals_tie,
    ambiguity_atlas,
    cached_object_key,
    conventions_over,
    default_worker_count,
    flat_conventions,
    flat_equivalence,
    flat_twin_of,
    formula_tree,
    juxtaposition_sites,
    layered_translation_audit,
    literal_policy_sensitivity,
    minimality_witness,
    null_model,
    parallel_decision,
    parenthesis_cost,
    parse_flat,
    parse_tiered,
    placements,
    prefix_minus_sites,
    render_audit,
    render_extension_check,
    render_tiered,
    restricted_juxtaposition_check,
    role_support,
    should_parallelise,
    slots,
    tokenize_tiered,
    worker_count_for,
)


@pytest.fixture(scope="module")
def audit():
    return agreement_audit()


@pytest.fixture(scope="module")
def translation():
    return layered_translation_audit()


@pytest.fixture(scope="module")
def headline():
    return flat_equivalence()


@pytest.fixture(scope="module")
def rendering():
    return render_audit()


@pytest.fixture(scope="module")
def atlas():
    return ambiguity_atlas()


@pytest.fixture(scope="module")
def nulls():
    return null_model()


# ------------------------------------- FIRST: the tiered language is a conservative extension


def test_tiered_parser_reproduces_generation_one_on_every_cell(audit):
    """The load-bearing audit: 2874732 cells, byte-identical trees, zero disagreements."""
    assert audit["conservative"] is True
    assert audit["disagreements"] == 0
    assert audit["disagreeing"] == ()
    assert audit["cells"] == 2874732


def test_agreement_audit_grid_is_the_declared_one(audit):
    assert audit["sources"] == 98
    assert audit["generation_one_grammars"] == 25
    assert audit["embeddings"] == 123
    assert audit["conventions_per_embedding"] == (98, 242)
    assert audit["literal_policy"] == "split"
    assert audit["cells"] == 98 * (24 * 5 * 242 + 3 * 98)


def test_agreement_corpus_contains_no_new_syntax_at_all(audit):
    """The census, not an assurance: zero juxtaposition sites and zero prefix minus sites."""
    assert audit["site_census"] == {"juxtaposition_sites": 0, "prefix_minus_sites": 0}


def _saboteur(source, convention, literal_policy):
    """A tiered parser that is wrong on exactly one Generation 1 string."""
    tree = parse_tiered(source, convention, literal_policy)
    if source == "a - b - c":
        return Number(Fraction(0, 1))
    return tree


def test_the_audit_reports_an_injected_divergence(audit):
    """The audit is put in front of a real disagreement and must name it.

    0045 had a surviving mutant here because every test only asserted that the audit returns
    ``conservative``. An audit that cannot fail is not an audit.
    """
    sabotaged = agreement_audit(grammars=all_grammars()[:1], workers=1, tiered_parse=_saboteur)
    assert sabotaged["conservative"] is False
    assert sabotaged["disagreements"] == 294
    assert {item["source"] for item in sabotaged["disagreeing"]} == {"a - b - c"}
    assert sabotaged["cells"] == 3 * 98 * 98


def test_the_audit_reports_a_real_language_divergence():
    """Not a mock: the ``none`` literal policy is a genuine language, and it is NOT conservative.

    Dropping the composite rational literal changes what ``1/2 + a`` means, and the audit has to
    say so cell by cell rather than reporting an aggregate verdict of "conservative".
    """
    diverged = agreement_audit(grammars=all_grammars()[:1], literal_policy="none", workers=1)
    assert diverged["conservative"] is False
    assert diverged["disagreements"] == 1470
    assert {item["source"] for item in diverged["disagreeing"]} == {
        "1/2",
        "1/2 * a",
        "1/2 + a",
        "a * 1/2",
        "(1/2 + a) * b",
    }
    assert diverged["disagreements"] == 5 * 3 * 98


def test_the_audit_counts_a_rejection_as_a_disagreement():
    """The branch no passing run reaches, reached on purpose.

    The site census is zero, so no Generation 1 cell ever makes the tiered parser reject, and an
    audit that treated a rejection as agreement would pass every other test in this file. A mutant
    that did exactly that survived until this test existed.
    """
    rejecting = Convention("H0", ("gap", 1), ("gap", 3), False)
    with pytest.raises(ValueError):
        parse_tiered("a * -b", rejecting)
    expected = parse("a * b", all_grammars()[0])
    cell = audit_cell("a * -b", rejecting, LITERAL_POLICY, expected)
    assert cell is not None
    assert cell["produced"].startswith("REJECTED")
    assert cell["source"] == "a * -b"
    assert cell["convention"] == rejecting.id


def test_the_audit_cell_is_silent_when_the_trees_agree():
    conventional = all_grammars()[0]
    for source in ("a * b + c", "a - b - c", "1/2 + a"):
        expected = parse(source, conventional)
        assert audit_cell(source, CONTROL_CONVENTION, LITERAL_POLICY, expected) is None


def test_the_default_policy_is_conservative_and_gen1_is_too():
    for policy in ("gen1", "split"):
        result = agreement_audit(grammars=all_grammars()[:1], literal_policy=policy, workers=1)
        assert result["conservative"] is True, policy
        assert result["disagreements"] == 0, policy


# --------------------------------------------------------------------- the convention space


def test_the_convention_space_is_the_declared_size():
    assert CONVENTION_SPACE_SIZE == 3518642
    assert len(CONVENTIONS) == 91922
    assert placements(3) == (
        ("gap", 0), ("tie", 0), ("gap", 1), ("tie", 1), ("gap", 2), ("tie", 2), ("gap", 3),
    )
    assert len(placements(5)) == 11
    assert len(slots(3)) == 49
    assert len(slots(5)) == 121
    assert len(conventions_over(CONTROL_BASE)) == 49 * 49 * 2


def test_every_convention_has_exactly_one_kind():
    counts = {kind: 0 for kind in CONVENTION_KINDS}
    for convention in CONVENTIONS:
        counts[convention.kind] += 1
    assert counts == {"linear": 14569, "exponent_prefix": 14569, "split": 62784}
    assert sum(counts.values()) == len(CONVENTIONS)


def test_the_seven_roles_are_the_five_operators_plus_two():
    assert ROLES == BINARY_OPERATORS + (JUX, NEG)
    assert len(ROLES) == 7


def test_the_alias_reading_is_the_tie_placement_and_not_a_separate_axis():
    """Measured, not asserted: rewriting juxtaposition to ``*`` agrees on every source."""
    result = alias_equals_tie()
    assert result["alias_is_the_tie"] is True
    assert result["disagreements"] == 0
    assert result["tie_placement"] == ("tie", 1)
    assert result["sources"] == len(CORPUS_SOURCES)


def test_the_two_published_readings_of_half_x_are_both_reachable():
    assert cached_object_key(parse_tiered("1/2x", TIGHT_JUXTAPOSITION))[0] == "1/(2*x)"
    assert cached_object_key(parse_tiered("1/2x", ALIAS_JUXTAPOSITION))[0] == "x/2"


def test_the_two_published_readings_of_minus_x_squared_are_both_reachable():
    conventional = Convention("H0", ("gap", 1), ("gap", 1), True)
    spreadsheet = Convention("H0", ("gap", 1), ("gap", 0), True)
    assert cached_object_key(parse_tiered("-x^2", conventional))[0] == "-x**2"
    assert cached_object_key(parse_tiered("-x^2", spreadsheet))[0] == "x**2"
    assert cached_object_key(parse_tiered("-2^2", conventional))[0] == "-4"
    assert cached_object_key(parse_tiered("-2^2", spreadsheet))[0] == "4"


# ----------------------------------------------------------------------------- the tokenizer


def test_what_the_tokenizer_accepts_as_juxtaposition():
    assert [token.kind for token in tokenize_tiered("2x")][:2] == ["number", "name"]
    assert juxtaposition_sites("2x") == 1
    assert juxtaposition_sites("2(x + 1)") == 1
    assert juxtaposition_sites("(a + b)(a - b)") == 1
    assert juxtaposition_sites("2 x y") == 2
    assert juxtaposition_sites("a * b") == 0


def test_what_the_tokenizer_refuses_as_juxtaposition():
    """Maximal munch is Generation 1's rule, kept: ``xy`` is one variable, not a product."""
    assert [token.value for token in tokenize_tiered("xy")][:1] == ["xy"]
    assert juxtaposition_sites("xy") == 0
    assert juxtaposition_sites("x2") == 0
    assert juxtaposition_sites("x y") == 1


def test_the_composite_literal_rule_is_the_declared_axis():
    assert [token.value for token in tokenize_tiered("1/2x", "gen1")][:2] == ["1/2", "x"]
    assert [token.value for token in tokenize_tiered("1/2x", "split")][:4] == ["1", "/", "2", "x"]
    assert [token.value for token in tokenize_tiered("1/2 x", "split")][:2] == ["1/2", "x"]
    assert [token.value for token in tokenize_tiered("1/2 + a", "split")][:3] == ["1/2", "+", "a"]
    assert LITERAL_POLICY == "split"
    assert LITERAL_POLICIES == ("gen1", "split", "none")


def test_prefix_minus_sites_are_counted_by_position():
    assert prefix_minus_sites("-x") == 1
    assert prefix_minus_sites("a - b") == 0
    assert prefix_minus_sites("a - -b") == 1
    assert prefix_minus_sites("-x - -y") == 2


def test_exponentiation_stays_right_associative():
    tree = parse_tiered("2^3^2", CONTROL_CONVENTION)
    assert tree == Binary("^", Number(Fraction(2)), Binary("^", Number(Fraction(3)), Number(Fraction(2))))


def test_role_support_is_reported_for_stratification():
    assert role_support("1/2x") == ("/", JUX)
    assert role_support("-x^2") == ("^", NEG)
    assert role_support("a * b + c") == ("*", "+")


# ---------------------------------------------------------- round trip and minimality, by search


def test_round_trip_and_minimality_over_the_whole_grid(rendering):
    assert rendering["round_trip_failures"] == 0
    assert rendering["failing"] == ()
    assert rendering["minimal"] is True
    assert rendering["trees"] == 46
    assert rendering["conventions"] == 4802
    assert rendering["cells"] == 220892


def test_minimality_is_confirmed_by_exhaustive_search_not_by_argument(rendering):
    assert rendering["writings_checked"] == 900872
    assert rendering["cheaper_writings_refuted"] == 679980
    assert rendering["bracket_pairs"] == 100156


def test_the_render_grids_bound_is_disclosed_and_checked_beyond():
    """The grid stops at the conventional base for time; this is what lies past the bound."""
    extension = render_extension_check()
    assert extension["conventions"] == 484
    assert extension["trees"] == 46
    assert extension["cells"] == 22264
    assert extension["round_trip_failures"] == 0
    assert extension["minimal"] is True
    assert extension["writings_checked"] == 124262
    assert extension["cheaper_writings_refuted"] == 101998
    assert extension["bracket_pairs"] == 13164


def test_every_rendering_reparses_to_its_own_tree():
    for formula in CORPUS_3:
        tree = formula_tree(formula)
        for convention in (TIGHT_JUXTAPOSITION, ALIAS_JUXTAPOSITION):
            text = render_tiered(tree, convention)
            assert parse_tiered(text, convention) == tree, (formula.source, convention.id)


def test_leaf_brackets_never_lower_a_bracket_count():
    """The one restriction on the writing enumeration, checked rather than argued (0047)."""
    for formula in CORPUS_3:
        tree = formula_tree(formula)
        for convention in (TIGHT_JUXTAPOSITION, ALIAS_JUXTAPOSITION):
            narrow = minimality_witness(tree, convention)
            wide = minimality_witness(tree, convention, leaf_brackets=True)
            assert narrow["pairs"] == wide["pairs"], (formula.source, convention.id)


def test_a_juxtaposition_boundary_is_spaced_only_where_the_tokenizer_needs_it():
    tree = parse_tiered("2 x", ALIAS_JUXTAPOSITION)
    assert render_tiered(tree, TIGHT_JUXTAPOSITION) in ("2x", "2 * x")
    both_names = Binary("*", Variable("x"), Variable("y"))
    text = render_tiered(both_names, TIGHT_JUXTAPOSITION)
    assert parse_tiered(text, TIGHT_JUXTAPOSITION) == both_names


# ------------------------------------------------------------------------------ THE HEADLINE


def test_every_linear_tier_stack_translates_to_a_flat_table_exactly(translation):
    """T26's first half, as an identity rather than an existence claim."""
    assert translation["translation_is_exact"] is True
    assert translation["disagreements"] == 0
    assert translation["conventions"] == 14569
    assert translation["cells"] == 670174


def test_the_translation_is_read_off_the_stack():
    convention = Convention("H0", ("gap", 1), ("gap", 1), False)
    twin = flat_twin_of(convention)
    assert twin is not None
    powers = twin.powers
    assert powers["^"] > powers[JUX] > powers[NEG] > powers["*"] == powers["/"] > powers["+"]
    assert twin.prefix_rule == "level"
    assert flat_twin_of(Convention("H0", ("gap", 1), ("gap", 1), True)) is None


def test_no_linear_convention_lacks_a_flat_twin(headline):
    assert headline["by_kind"]["linear"]["conventions"] == 14569
    assert headline["by_kind"]["linear"]["without_flat_twin"] == 0
    assert headline["by_kind"]["linear"]["shortest_separator"] is None


def test_the_context_dependent_kinds_do_lack_flat_twins(headline):
    assert headline["by_kind"]["exponent_prefix"]["conventions"] == 14569
    assert headline["by_kind"]["exponent_prefix"]["without_flat_twin"] == 6707
    assert headline["by_kind"]["split"]["conventions"] == 62784
    assert headline["by_kind"]["split"]["without_flat_twin"] == 41244
    assert headline["conventions_with_flat_twin"] == 43971
    assert headline["conventions_without_flat_twin"] == 47951


def test_the_flat_search_is_exhaustive(headline):
    assert headline["flat_models"] == 94586
    assert len(flat_conventions()) == 94586
    assert len({convention.ranks for convention in flat_conventions()}) == 47293


def test_the_shortest_separating_sources_are_pinned(headline):
    assert headline["by_kind"]["exponent_prefix"]["shortest_separator"]["source"] == "a * -b"
    assert headline["by_kind"]["split"]["shortest_separator"]["source"] == "2^-3"
    assert headline["by_kind"]["exponent_prefix"]["shortest_tree_separator"]["source"] == "e^-k t"
    assert headline["separating_sources"] == (
        "-m x + c",
        "1 - x^2/2 + x^4/24",
        "2^-3",
        "a * -b",
        "a - -b",
        "a x + b y - c",
        "a x^2 + b x + c",
        "b^2 - 4 a c",
        "e^-k t",
        "x - x^3/6",
        "x^2y",
    )


def test_the_printed_mathematics_convention_itself_has_no_flat_twin(headline):
    """The control convention of this experiment is one of the ones a flat table cannot reach.

    ``TIGHT_JUXTAPOSITION`` is the printed reading: ``1/2x`` is ``1/(2x)``, ``-x^2`` is ``-(x^2)``,
    and ``x^-2`` parses. Its sibling differs in exactly one bit - Python's exponent-prefix rule -
    and THAT one has a flat twin, which is what isolates the feature responsible.
    """
    sibling = Convention("H0", ("gap", 1), ("gap", 1), False)
    assert TIGHT_JUXTAPOSITION == Convention("H0", ("gap", 1), ("gap", 1), True)
    assert TIGHT_JUXTAPOSITION.id in headline["separators"]
    assert headline["separators"][TIGHT_JUXTAPOSITION.id]["source"] == "-m x + c"
    assert headline["separators"][TIGHT_JUXTAPOSITION.id]["kind"] == "exponent_prefix"
    assert sibling.kind == "linear"
    assert sibling.id not in headline["separators"]


def test_the_control_convention_reads_the_named_ambiguities_as_print_does():
    readings = {
        "1/2x": "1/(2*x)",
        "-x^2": "-x**2",
        "-2^2": "-4",
        "2x^2": "2*x**2",
        "6/2(1 + 2)": "1",
    }
    for source, object_form in readings.items():
        assert cached_object_key(parse_tiered(source, TIGHT_JUXTAPOSITION))[0] == object_form
    assert parse_tiered("x^-2", TIGHT_JUXTAPOSITION) == Binary(
        "^", Variable("x"), Negate(Number(Fraction(2)))
    )


def _reads(flat, source):
    try:
        return str(parse_flat(source, flat))
    except ValueError:
        return REJECTED


def _tiered_reading(convention, source):
    try:
        return str(parse_tiered(source, convention))
    except ValueError:
        return REJECTED


def test_a_flat_twin_is_corpus_relative_and_the_search_finds_a_real_one():
    """The linear sibling's twin is exhibited, so "has a flat twin" is not only a count."""
    sibling = Convention("H0", ("gap", 1), ("gap", 1), False)
    twin = flat_twin_of(sibling)
    assert twin is not None
    for source in CORPUS_SOURCES:
        assert _tiered_reading(sibling, source) == _reads(twin, source), source


def test_the_swept_region_and_the_unswept_one_are_both_reported(headline):
    assert headline["conventions_swept"] == 91922
    assert headline["convention_space_size"] == 3518642
    assert headline["unswept_conventions"] == 3426720
    assert headline["sources"] == 46
    assert headline["distinct_tiered_vectors"] == 4903
    assert headline["distinct_flat_vectors"] == 7034


# ------------------------------------------------------------------------- the ambiguity atlas


def _row(atlas, source):
    return next(row for row in atlas["rows"] if row["source"] == source)


def test_minus_x_squared_is_pinned_by_the_object_it_denotes(atlas):
    row = _row(atlas, "-x^2")
    assert {item["object"]: item["conventions"] for item in row["objects"]} == {
        "-x**2": 4116,
        "x**2": 686,
    }
    assert row["published_readings_missing"] == ()
    assert row["rejected_by"] == 0


def test_half_x_is_pinned_by_the_object_it_denotes(atlas):
    row = _row(atlas, "1/2x")
    assert {item["object"]: item["conventions"] for item in row["objects"]} == {
        "x/2": 2744,
        "1/(2*x)": 2058,
    }
    assert row["published_readings_missing"] == ()


def test_the_viral_division_reaches_both_published_answers(atlas):
    row = _row(atlas, "6/2(1 + 2)")
    assert {item["object"]: item["conventions"] for item in row["objects"]} == {"9": 2744, "1": 2058}


def test_the_literal_negative_power_follows_the_same_split(atlas):
    row = _row(atlas, "-2^2")
    assert {item["object"]: item["conventions"] for item in row["objects"]} == {"-4": 4116, "4": 686}


def test_the_coefficient_square_has_no_published_second_reading(atlas):
    row = _row(atlas, "2x^2")
    assert {item["object"]: item["conventions"] for item in row["objects"]} == {
        "2*x**2": 3430,
        "4*x**2": 1372,
    }


def test_the_exponent_juxtaposition_is_rejected_by_some_conventions(atlas):
    row = _row(atlas, "x^2y")
    assert row["rejected_by"] == 588
    assert {item["object"]: item["conventions"] for item in row["objects"]} == {
        "x**2*y": 3528,
        "x**(2*y)": 686,
    }


# ---------------------------------------------------------------------------- the null model


def test_the_null_model_answer_is_pinned_literally(nulls):
    """Three objects, all of them from the split kind, on one of forty-six sources."""
    assert nulls["objects_only_tiered"] == 3
    assert nulls["objects_only_flat"] == 3
    assert nulls["sources_with_excess"] == 1
    assert nulls["sources_with_deficit"] == 2
    assert nulls["total_tiered_objects"] == 94
    assert nulls["total_flat_objects"] == 94
    assert nulls["excess_by_kind"] == {"linear": 0, "exponent_prefix": 0, "split": 3}


def test_the_excess_is_stratified_by_role_support(nulls):
    assert nulls["stratified_by_role_support"] == {
        1: {"sources": 4, "tiered_objects": 4, "flat_objects": 4, "excess": 0, "deficit": 0},
        2: {"sources": 27, "tiered_objects": 41, "flat_objects": 41, "excess": 0, "deficit": 0},
        3: {"sources": 15, "tiered_objects": 49, "flat_objects": 49, "excess": 3, "deficit": 3},
    }


def test_the_three_excess_objects_are_named(nulls):
    row = next(row for row in nulls["rows"] if row["objects_only_tiered"])
    assert row["source"] == "a x^2 + b x + c"
    assert row["objects_only_tiered_list"] == (
        "a*x**((b + 2)*(c + x))",
        "a*x**(b*x + c + 2)",
        "a*x**(c + x*(b + 2))",
    )


# --------------------------------------------------------- sensitivity and what is not enumerated


def test_the_composite_literal_rule_moves_the_named_ambiguity():
    result = literal_policy_sensitivity()
    rows = {row["literal_policy"]: row for row in result["rows"]}
    assert rows["gen1"]["readings_of_half_x"] == 1
    assert rows["gen1"]["objects"] == ("x/2",)
    assert rows["split"]["readings_of_half_x"] == 2
    assert rows["gen1"]["conservative_over_generation_one"] is True
    assert rows["split"]["conservative_over_generation_one"] is True
    assert rows["none"]["conservative_over_generation_one"] is False


def test_the_restriction_the_space_does_not_contain_does_not_change_the_answer():
    result = restricted_juxtaposition_check()
    assert result["linear_without_flat_twin"] == 0
    assert result["verdict_shape_unchanged"] is True
    assert result["verdict_by_kind"] == {
        "linear": {"unrestricted": 0, "restricted": 0},
        "exponent_prefix": {"unrestricted": 31, "restricted": 28},
        "split": {"unrestricted": 2755, "restricted": 2590},
    }


# ------------------------------------------------------------------------------- the multicore


def test_worker_count_is_derived_from_the_observed_core_count():
    assert worker_count_for(16, 1000) == 15
    assert worker_count_for(2, 1000) == 1
    assert worker_count_for(16, 3) == 3
    assert default_worker_count(1000) >= 1


def test_the_parallel_decision_is_taken_from_observed_costs():
    assert should_parallelise(1, 10.0, 15) is False
    assert should_parallelise(1000, 10.0, 1) is False
    assert should_parallelise(1000, 10.0, 15) is True
    assert should_parallelise(2, 1e-06, 15) is False


def tiered_syntax_cores():
    return os.cpu_count()


def test_the_routing_decision_runs_and_reports_its_own_timings():
    """The timing path is code too, and an untested one rots."""
    decision = parallel_decision(repeats=1, workers=2)
    assert decision["workers"] == 2
    assert decision["cores"] == tiered_syntax_cores()
    assert decision["pool_startup_seconds"] > 0
    assert decision["audit_payloads"] == 123
    assert decision["sweep_payloads"] >= 1
    for key in ("audit_parallel", "sweep_parallel", "render_parallel"):
        assert decision[key] in (True, False)


def test_bracket_cost_shows_what_juxtaposition_buys():
    tree = parse_tiered("1/(2 * x)", ALIAS_JUXTAPOSITION)
    assert parenthesis_cost(tree, ALIAS_JUXTAPOSITION) == 1
    assert parenthesis_cost(tree, TIGHT_JUXTAPOSITION) == 0
    assert render_tiered(tree, ALIAS_JUXTAPOSITION) == "1 / (2 * x)"
    assert render_tiered(tree, TIGHT_JUXTAPOSITION) == "1 / 2x"


def test_sequential_and_parallel_agree_on_the_translation_audit():
    conventions = tuple(c for c in conventions_over(CONTROL_BASE, splits=False) if c.layered)[:24]
    sequential = layered_translation_audit(conventions=conventions, workers=1)
    parallel = layered_translation_audit(conventions=conventions, workers=4)
    assert sequential == parallel
    assert sequential["cells"] == 24 * len(CORPUS_SOURCES)


def test_sequential_and_parallel_agree_on_the_render_audit():
    conventions = conventions_over(CONTROL_BASE, splits=False)[:12]
    sequential = render_audit(conventions=conventions, corpus=CORPUS_3[:10], workers=1)
    parallel = render_audit(conventions=conventions, corpus=CORPUS_3[:10], workers=4)
    assert sequential == parallel
    assert sequential["round_trip_failures"] == 0


def test_sequential_and_parallel_agree_on_the_agreement_audit():
    sequential = agreement_audit(grammars=all_grammars()[:1], workers=1)
    parallel = agreement_audit(grammars=all_grammars()[:1], workers=3)
    assert sequential == parallel
