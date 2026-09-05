"""Experiment 0048: the complex domain, and the branch cut as a second convention.

The first test in this file is the one the rest of the experiment rests on: the complex-aware key
built in :mod:`parseatlas.complex_worlds` reproduces the key the repository already computes,
cell by cell, wherever the domain is ``R``.  If that ever fails, the ``R`` column and the ``C``
column are measuring different things and no number below means anything.
"""

from fractions import Fraction
from functools import cache

import pytest

from parseatlas.canonical import canonicalize
from parseatlas.complex_worlds import (
    CONVENTIONS,
    CONVENTIONS_BY_NAME,
    CORPUS,
    GRAMMARS,
    GRID_MESH,
    GRID_RADIUS,
    LEAK_WITNESS,
    MICROSECONDS_SCALE_MINIMUM,
    QUADRATICS,
    SECONDS_SCALE_MINIMUM,
    STRADDLE_OFFSETS,
    agreeing_pairs_audit,
    agreement_audit,
    axis_cross,
    axis_cross_table,
    constant_class_deficit,
    diamond_angle,
    domain_shift,
    domain_shift_table,
    encoding_faithfulness_audit,
    excluded_points,
    existing_key,
    is_constant_reading,
    log_jumps,
    notation_audit,
    prune_control,
    real_solve_leak_audit,
    reducibility_table,
    refinement_sweep,
    resolve_worker_count,
    sample_grid,
    semantic_key,
    sheet_index,
    sqrt_jumps,
    straddle_audit,
    straddle_pair,
    sweep_sources,
    sympy_default_audit,
)
from parseatlas.parser import parse

CONTROL = GRAMMARS[0]


@cache
def _agreement():
    return agreement_audit()


@cache
def _shift():
    return domain_shift_table(workers=1)


@cache
def _cross():
    # workers=1: the pool's spawn cost under pytest on Windows exceeds the work it distributes for
    # a twelve-item table.  parallel_decision measures both paths outside the test process.
    return axis_cross_table(workers=1)


@cache
def _straddle():
    return straddle_audit()


@cache
def _reducibility():
    return reducibility_table()


# ============================================================ the audit the experiment rests on


def test_the_complex_aware_key_reproduces_the_existing_key_over_R_cell_by_cell():
    """FIRST, and load-bearing: 300 cells, no disagreement.

    Twelve corpus sources times twenty-five grammars.  The ``R`` branch of
    :func:`semantic_key` is written out independently of :mod:`parseatlas.canonical` precisely so
    that this equality is a check and not a delegation.
    """
    audit = _agreement()
    assert audit["cells"] == len(CORPUS) * len(GRAMMARS) == 300
    assert audit["failures"] == 0
    assert audit["failing"] == ()
    assert audit["holds"] is True


def test_the_agreement_holds_component_by_component_and_not_only_as_a_tuple():
    """Named cell, spelled out: canonical form, domain label and excluded tuple each agree."""
    tree = parse("(x*x - 1)/(x - 1)", CONTROL)
    mine = semantic_key(tree, "R")
    theirs = existing_key(tree)
    canonical = canonicalize(tree)
    assert mine[0] == theirs[0] == canonical["expression"] == "x + 1"
    assert mine[1] == theirs[1] == canonical["domain"] == "R"
    assert mine[2] == theirs[2] == ("1",)


def test_the_domain_label_the_repository_hard_codes_is_the_defect_this_card_measures():
    """NF-2026-00005 restated as a test: the existing key says ``R`` for every expression."""
    labels = {
        canonicalize(parse(entry.source, grammar))["domain"]
        for entry in CORPUS
        for grammar in GRAMMARS
    }
    assert labels == {"R"}
    assert {semantic_key(parse(entry.source, CONTROL), "C")[1] for entry in CORPUS} == {"C"}


def test_the_R_label_on_the_existing_key_is_a_symbol_assumption_and_not_a_domain_restriction():
    """A second defect, found by this card: ``solve`` on a ``real=True`` symbol can return ``I``.

    Clean on this corpus and demonstrably not clean in general, so the corpus number and the
    witness are both reported.  The direction matters and is asserted: a leak can only put complex
    points into the ``R`` key, so it can only make the domain look MORE inert than it is.
    """
    audit = real_solve_leak_audit()
    assert audit["cells"] == 300
    assert audit["leaking_cells"] == 0
    assert audit["clean_on_corpus"] is True
    assert audit["witness"] == LEAK_WITNESS == "1 / (x*x*x*x + 3*x*x + 3)"
    assert audit["witness_real_points"] == 4
    assert audit["witness_complex_points"] == 4
    assert audit["witness_non_real_under_R"] == 4
    assert audit["witness_leaks"] is True


# ============================================================ the excluded-points component


def test_the_card_s_named_case_has_an_empty_real_pole_set_and_a_two_point_complex_one():
    """``1 / (x*x + 1)``: nothing to exclude over R, two points to exclude over C."""
    tree = parse("1 / (x*x + 1)", CONTROL)
    assert excluded_points(tree, "R") == ()
    assert excluded_points(tree, "C") == ("-I", "I")
    assert semantic_key(tree, "R") == ("1/(x**2 + 1)", "R", ())
    assert semantic_key(tree, "C") == ("1/(x**2 + 1)", "C", ("-I", "I"))


def test_a_real_pole_is_seen_identically_by_both_domains():
    tree = parse("(x + 1)/(x - 2)", CONTROL)
    assert excluded_points(tree, "R") == excluded_points(tree, "C") == ("2",)


def test_the_excluded_set_is_read_off_the_tree_and_not_off_the_simplified_value():
    """``(x*x - 1)/(x - 1)`` denotes ``x + 1`` and is still undefined at ``1`` in both domains."""
    tree = parse("(x*x - 1)/(x - 1)", CONTROL)
    assert semantic_key(tree, "C")[0] == "x + 1"
    assert excluded_points(tree, "R") == excluded_points(tree, "C") == ("1",)


# ============================================================ half A: R against C


HALF_A_ROWS = {
    "support_one_sum": (1, 1, "equal", 0),
    "support_two_quadratic": (2, 2, "equal", 0),
    "support_two_ratio": (2, 2, "equal", 0),
    "complex_pole_reciprocal": (2, 2, "equal", 13),
    "complex_pole_product": (4, 4, "equal", 13),
    "complex_pole_sum": (4, 4, "equal", 21),
    "real_pole": (1, 1, "equal", 0),
    "removable": (2, 2, "equal", 0),
    "reciprocal_sweep": (5, 5, "equal", 4),
    "standing_linear": (8, 8, "equal", 0),
    "standing_quadratic": (8, 8, "equal", 0),
    "refinement_witness": (3, 4, "refinement", 6),
}


def test_the_R_and_C_class_counts_are_pinned_per_corpus_entry():
    """Twelve sources, the R count, the C count and the verdict, each named."""
    rows = {row["name"]: row for row in _shift()["rows"]}
    assert set(rows) == set(HALF_A_ROWS)
    for name, (real, complex_, verdict, excluded) in HALF_A_ROWS.items():
        assert rows[name]["real_classes"] == real, name
        assert rows[name]["complex_classes"] == complex_, name
        assert rows[name]["verdict"] == verdict, name
        assert rows[name]["excluded_differs_count"] == excluded, name


def test_the_refinement_verdict_is_pinned_and_neither_coarsening_nor_crossing_occurs():
    """The structural answer: where the partition moves at all it REFINES, in one direction only."""
    table = _shift()
    assert table["verdicts"] == {"equal": 11, "refinement": 1}
    assert table["strict_count"] == 1
    assert table["no_coarsening"] is True
    assert table["no_crossing"] is True
    assert table["partition_unchanged"] is False


def test_the_excluded_component_differs_far_more_often_than_the_partition_moves():
    """57 cells of 300 carry a different excluded set; 51 of those are invisible to the partition."""
    table = _shift()
    assert table["cells"] == 300
    assert table["excluded_differs_sources"] == 5
    assert table["excluded_differs_cells"] == 57
    assert table["invisible_excluded_cells"] == 51
    assert table["canonical_disagreement_cells"] == 0


def test_the_single_moving_source_is_named_and_its_mechanism_is_pinned():
    """The C partition splits one R class in two, and the split is carried by six grammars."""
    row = domain_shift("(x * x + 1) / 1 - (x * x + 2)")
    assert row["real_classes"] == 3
    assert row["complex_classes"] == 4
    assert row["verdict"] == "refinement"
    assert row["excluded_differs"] == ("G09", "G10", "G12", "G13", "G15", "G16")
    assert len(row["moved_grammars"]) == 13
    real_keys = {key for key in row["real_partition"]}
    complex_keys = {key for key in row["complex_partition"]}
    assert len(real_keys) == 3
    assert len(complex_keys) == 4
    assert "('-1', 'C', ('-I', 'I'))" in complex_keys
    assert "('-1', 'C', ())" in complex_keys


def test_the_null_model_split_is_pinned_per_stratum_for_half_A():
    """Rates only inside a stratum: a support-1 source has one reading and cannot move at all."""
    strata = {item["support_size"]: item for item in _shift()["strata"]}
    assert set(strata) == {1, 2, 3, 4}
    assert [strata[size]["reading_ceiling"] for size in (1, 2, 3, 4)] == [1, 2, 6, 24]
    assert [strata[size]["sources"] for size in (1, 2, 3, 4)] == [1, 2, 6, 3]
    assert [strata[size]["strict_count"] for size in (1, 2, 3, 4)] == [0, 0, 0, 1]
    assert strata[1]["can_move"] is False
    assert all(strata[size]["can_move"] is True for size in (2, 3, 4))
    assert strata[4]["strict_rate"] == pytest.approx(1 / 3)
    assert [strata[size]["excluded_differs_cells"] for size in (1, 2, 3, 4)] == [0, 0, 51, 6]


# ============================================================ the sweep and its prune control


def test_the_sweep_space_is_exactly_the_declared_alphabet():
    assert len(sweep_sources(1)) == 5**2 * 4**1 == 100
    assert len(sweep_sources(2)) == 5**3 * 4**2 == 2000
    assert len(sweep_sources(3)) == 5**4 * 4**3 == 40000


def test_the_shortest_sweep_finds_no_moving_source_at_all():
    run = refinement_sweep(1, workers=1)
    assert run["space"] == 100
    assert run["pruned"] == 90
    assert run["live"] == 10
    assert run["strict_count"] == 0
    assert run["verdicts"] == {"equal": 100}
    strata = {item["support_size"]: item for item in run["strata"]}
    assert [strata[size]["sources"] for size in (1, 2, 3)] == [36, 32, 32]
    assert [strata[size]["live"] for size in (1, 2, 3)] == [0, 0, 10]


def test_the_prune_screen_is_controlled_rather_than_trusted():
    """Every source the divisor-signature screen pruned, recomputed the expensive way."""
    control = prune_control(1, workers=1)
    assert control["space"] == 100
    assert control["pruned"] == 90
    assert control["checked"] == 90
    assert control["wrong"] == 0
    assert control["holds"] is True


# ============================================================ half B: the branch conventions


def test_the_diamond_angle_is_an_exact_surrogate_for_the_principal_argument():
    """``k*pi/4 -> k/2`` exactly, on the whole range ``(-2, 2]``, with no float anywhere."""
    assert diamond_angle(Fraction(1), Fraction(0)) == Fraction(0)
    assert diamond_angle(Fraction(1), Fraction(1)) == Fraction(1, 2)
    assert diamond_angle(Fraction(0), Fraction(1)) == Fraction(1)
    assert diamond_angle(Fraction(-1), Fraction(1)) == Fraction(3, 2)
    assert diamond_angle(Fraction(-1), Fraction(0)) == Fraction(2)
    assert diamond_angle(Fraction(-1), Fraction(-1)) == Fraction(-3, 2)
    assert diamond_angle(Fraction(0), Fraction(-1)) == Fraction(-1)
    assert diamond_angle(Fraction(1), Fraction(-1)) == Fraction(-1, 2)
    with pytest.raises(ValueError):
        diamond_angle(Fraction(0), Fraction(0))


def test_sympy_s_own_branch_is_named_as_a_convention_rather_than_used_unnamed():
    """``principal`` reproduces SymPy's ``sqrt`` and ``log`` on nine probes, eighteen checks."""
    audit = sympy_default_audit()
    assert audit["probes"] == 9
    assert audit["checks"] == 18
    assert audit["failures"] == 0
    assert audit["holds"] is True
    assert [item.name for item in CONVENTIONS if item.is_sympy_default] == ["principal"]


CUTS = {
    "principal": ("-pi", Fraction(-2), (-1, 0), "(-pi, pi]"),
    "negative_imaginary": ("-pi/2", Fraction(-1), (0, -1), "(-pi/2, 3*pi/2]"),
    "positive_axis": ("0", Fraction(0), (1, 0), "(0, 2*pi]"),
    "positive_imaginary": ("pi/2", Fraction(1), (0, 1), "(pi/2, 5*pi/2]"),
}


def test_each_declared_convention_is_pinned_by_where_its_cut_lies():
    assert [item.name for item in CONVENTIONS] == list(CUTS)
    for convention in CONVENTIONS:
        angle, diamond, ray, interval = CUTS[convention.name]
        assert convention.cut_angle == angle
        assert convention.cut_diamond == diamond
        assert convention.ray == ray
        assert convention.arg_interval == interval


def test_every_convention_is_discontinuous_on_its_own_cut_and_continuous_on_every_other():
    """Sixteen ordered pairs, ``sqrt`` and ``log`` each: the identity of a cut is measured.

    A convention is not identified by its name but by the ray on which its branch jumps, and the
    probe points straddle that ray by an exact rational offset.
    """
    audit = _straddle()
    assert audit["checks"] == 32
    assert audit["violations"] == ()
    assert audit["holds"] is True
    rows = {(row["cut_of"], row["measured_under"]): row for row in audit["rows"]}
    assert len(rows) == 16
    for owner in CUTS:
        for other in CUTS:
            assert rows[(owner, other)]["sqrt_jumps"] is (owner == other), (owner, other)
            assert rows[(owner, other)]["log_jumps"] is (owner == other), (owner, other)


def test_a_named_straddle_of_the_negative_real_axis_moves_only_the_principal_branch():
    """The value that straddles the cut is written out, not left implicit in a loop."""
    above, below = straddle_pair(CONVENTIONS_BY_NAME["principal"])
    assert above == (Fraction(-4), Fraction(-1, 1000))
    assert below == (Fraction(-4), Fraction(1, 1000))
    assert sqrt_jumps(above, below, CONVENTIONS_BY_NAME["principal"]) is True
    assert log_jumps(above, below, CONVENTIONS_BY_NAME["principal"]) is True
    assert sqrt_jumps(above, below, CONVENTIONS_BY_NAME["negative_imaginary"]) is False
    assert log_jumps(above, below, CONVENTIONS_BY_NAME["negative_imaginary"]) is False


def test_the_straddle_classification_does_not_move_with_the_offset():
    """The offset is swept rather than declared once, so it is not a hidden threshold."""
    assert STRADDLE_OFFSETS[0] == Fraction(1, 10)
    coarse = straddle_audit(offset=STRADDLE_OFFSETS[0])
    assert coarse["holds"] is True
    assert coarse["violations"] == ()


def test_the_sheet_index_is_the_whole_content_of_a_convention():
    """One bit per point, and the cut ray itself belongs to the counter-clockwise branch."""
    on_negative_real = (Fraction(-4), Fraction(0))
    assert sheet_index(on_negative_real, CONVENTIONS_BY_NAME["principal"]) == 0
    assert sheet_index(on_negative_real, CONVENTIONS_BY_NAME["negative_imaginary"]) == 0
    third_quadrant = (Fraction(-1), Fraction(-1))
    assert sheet_index(third_quadrant, CONVENTIONS_BY_NAME["principal"]) == 0
    assert sheet_index(third_quadrant, CONVENTIONS_BY_NAME["negative_imaginary"]) == 1

    # The docstring's second clause, actually checked.  Review found that no probe here ever landed
    # ON a cut ray, so changing the boundary comparison from <= to < -- which moves the ray itself
    # from one sheet to the other and flips branch_sqrt(4, positive_axis) from -2 to +2 -- passed
    # the whole suite.  This point lies exactly on positive_axis's cut.
    on_the_cut = (Fraction(1), Fraction(0))
    assert sheet_index(on_the_cut, CONVENTIONS_BY_NAME["positive_axis"]) == 1


# ============================================================ half B: crossing the two axes


def test_the_independence_verdict_is_pinned_with_the_product_and_the_measured_count():
    """The headline: 172 if the axes were independent, 160 measured, a deficit of 12."""
    table = _cross()
    assert table["convention_count"] == 4
    assert table["grid_radius"] == GRID_RADIUS == 4
    assert table["grid_mesh"] == GRID_MESH == 3
    assert table["grid_points"] == 625
    assert table["product"] == 172
    assert table["measured"] == 160
    assert table["difference"] == 12
    assert table["independent_sources"] + table["interacting_sources"] == len(CORPUS) == 12
    assert table["interaction_carried_by_constants"] is True


def test_the_deficit_equals_the_value_derived_without_any_grid():
    """A constant reading forces the collapse; the grid is only asked to converge to it."""
    derived = constant_class_deficit()
    assert derived["constant_classes"] == 5
    assert derived["predicted_deficit"] == 12
    assert _cross()["difference"] == derived["predicted_deficit"]
    assert _cross()["constant_classes"] == 5
    assert _cross()["constant_collapse"] == 12
    assert _cross()["non_constant_collapse"] == ()


def test_a_coarser_grid_reports_a_larger_deficit_and_the_extra_is_a_sampling_artefact():
    """The computational limit named as one: a coarse lattice invents collapse it cannot see past."""
    coarse = axis_cross_table(radius=1, mesh=1, workers=4)
    assert coarse["grid_points"] == 9
    assert coarse["product"] == 172
    assert coarse["difference"] > 12
    assert coarse["interaction_carried_by_constants"] is False
    assert len(coarse["non_constant_collapse"]) > 0


def test_no_grammar_pair_that_agrees_under_one_convention_disagrees_under_another():
    """Forced rather than found, and counted anyway: same value everywhere means same sheet."""
    audit = agreeing_pairs_audit(radius=2, mesh=1)
    assert audit["pairs_examined"] == len(CORPUS) * (len(GRAMMARS) * (len(GRAMMARS) - 1)) // 2 == 3600
    assert audit["conventions"] == 4
    assert audit["splitting_pairs"] == 0
    assert audit["holds"] is True
    assert _cross()["partition_stable_everywhere"] is True


def test_the_value_and_sheet_encoding_counts_the_same_composites_the_real_functions_do():
    """Half B is counted through an encoding, so the encoding is checked against SymPy itself."""
    audit = encoding_faithfulness_audit(grammars=GRAMMARS[:8], radius=1, mesh=1)
    assert audit["grid_points"] == 9
    assert audit["cells"] == 32
    assert audit["encoded_distinct"] == audit["sqrt_distinct"] == audit["log_distinct"]
    assert audit["sqrt_agrees"] is True
    assert audit["log_agrees"] is True
    assert audit["holds"] is True


def test_a_constant_reading_is_recognised_by_its_free_symbols_and_not_by_its_source_text():
    """``x / x + 1`` mentions ``x`` and denotes ``2``; a string test would get this wrong."""
    assert is_constant_reading(parse("x / x + 1", CONTROL)) is True
    assert is_constant_reading(parse("x * x + 1", CONTROL)) is False
    row = axis_cross("x / x + 1", radius=2, mesh=1)
    assert row["inner_classes"] == 2
    assert row["constant_classes"] == 1


def test_the_null_model_split_is_pinned_per_stratum_for_half_B():
    """The same stratification as half A, over the product and the measured count."""
    strata = {item["support_size"]: item for item in _cross()["strata"]}
    assert set(strata) == {1, 2, 3, 4}
    assert [strata[size]["sources"] for size in (1, 2, 3, 4)] == [1, 2, 6, 3]
    assert sum(strata[size]["product"] for size in (1, 2, 3, 4)) == 172
    assert sum(strata[size]["measured"] for size in (1, 2, 3, 4)) == 160
    assert strata[1]["can_move"] is False
    assert strata[1]["product"] == 4


# ============================================================ half C: reducibility over C


def test_the_three_quadratics_factor_over_three_different_fields():
    table = _reducibility()
    rows = {row["name"]: row for row in table["rows"]}
    assert rows["reducible_over_Q"]["factors_over_Q"] is True
    assert rows["reducible_over_R_only"]["factors_over_Q"] is False
    assert rows["reducible_over_R_only"]["factors_over_R"] is True
    assert rows["reducible_over_C_only"]["factors_over_R"] is False
    assert all(row["factors_over_C"] for row in table["rows"])
    assert (table["factor_over_Q"], table["factor_over_R"], table["factor_over_C"]) == (1, 2, 3)


def test_the_manager_s_measurement_for_the_mathematician_is_reproduced():
    """``2x^2 + 3x - 5``: the factored writing is cheaper in exactly 8 of the 25 worlds."""
    rows = {row["name"]: row for row in _reducibility()["rows"]}
    writing = rows["reducible_over_Q"]["writing"]
    assert writing["grammar_count"] == 25
    assert writing["factored_cheaper"] == 8
    assert writing["expanded_cheaper"] == 9
    assert writing["tie"] == 8


def test_the_wider_domain_buys_the_equivalence_and_buys_the_notation_nothing():
    """Two more quadratics factor over C; zero more become writable in Generation 1."""
    table = _reducibility()
    assert table["writable_in_generation_one"] == 1
    assert table["domain_buys_equivalence"] == 2
    assert table["domain_buys_notation"] == 0
    assert [row["factored"] for row in table["rows"]] == ["(2 * x + 5) * (x - 1)", None, None]


def test_generation_one_can_write_the_string_and_cannot_denote_the_object():
    """The limitation measured where it actually lies: ``i`` is a legal VARIABLE name."""
    audit = notation_audit()
    assert audit["attempts"] == 3
    assert audit["parse_successes"] == 3
    assert audit["denote_successes"] == 0
    rows = {row["name"]: row for row in audit["rows"]}
    assert rows["factored_with_i"]["canonical"] == "-i**2 + x**2"
    assert rows["factored_with_i"]["free_symbols"] == ("i", "x")
    assert rows["bare_i_squared"]["canonical"] == "i**2"


def test_the_factored_shape_costs_the_same_in_eight_worlds_whichever_field_supplies_the_roots():
    """The bracket count reads the shape, not the field the roots live in."""
    table = _reducibility()
    assert table["shape_factored_cheaper"] == (8, 8, 8)
    assert table["shape_factored_cheaper_constant"] is True


def test_only_the_quadratic_with_non_real_roots_gains_excluded_points_over_C():
    table = _reducibility()
    rows = {row["name"]: row for row in table["rows"]}
    assert rows["reducible_over_C_only"]["reciprocal_excluded_R"] == ()
    assert rows["reducible_over_C_only"]["reciprocal_excluded_C"] == ("-I", "I")
    assert rows["reducible_over_Q"]["reciprocal_excluded_R"] == rows["reducible_over_Q"]["reciprocal_excluded_C"]
    assert table["reciprocal_gains"] == 1
    assert len(QUADRATICS) == 3


# ============================================================ execution


def test_the_worker_count_is_derived_from_the_cores_and_from_a_per_workload_floor():
    """One floor per workload scale, because a screen item and a table item differ by orders."""
    assert SECONDS_SCALE_MINIMUM == 2
    assert MICROSECONDS_SCALE_MINIMUM == 4096
    assert resolve_worker_count(1, minimum=SECONDS_SCALE_MINIMUM) == 1
    assert resolve_worker_count(12, minimum=SECONDS_SCALE_MINIMUM) > 1
    assert resolve_worker_count(12, minimum=MICROSECONDS_SCALE_MINIMUM) == 1
    assert resolve_worker_count(2000, minimum=MICROSECONDS_SCALE_MINIMUM) == 1
    assert resolve_worker_count(40000, minimum=MICROSECONDS_SCALE_MINIMUM) > 1
    assert resolve_worker_count(40000, workers=3) == 3
    assert resolve_worker_count(2, workers=99) == 2


def test_sequential_and_parallel_agree_on_half_A():
    assert domain_shift_table(workers=1)["rows"] == domain_shift_table(workers=2)["rows"]


def test_sequential_and_parallel_agree_on_half_B():
    sequential = axis_cross_table(radius=1, mesh=1, workers=1)
    parallel = axis_cross_table(radius=1, mesh=1, workers=2)
    assert sequential["rows"] == parallel["rows"]
    assert sequential["measured"] == parallel["measured"]


def test_sequential_and_parallel_agree_on_the_sweep():
    sequential = refinement_sweep(1, workers=1)
    parallel = refinement_sweep(1, workers=2)
    assert sequential["verdicts"] == parallel["verdicts"]
    assert sequential["witnesses"] == parallel["witnesses"]
    assert sequential["pruned"] == parallel["pruned"] == 90


def test_the_declared_grid_is_exactly_what_the_two_parameters_say():
    assert len(sample_grid(1, 1)) == 9
    assert len(sample_grid(4, 3)) == 625
    assert sample_grid(1, 2)[0] == (Fraction(-1), Fraction(-1))
    assert (Fraction(1, 3), Fraction(0)) in sample_grid(1, 3)
