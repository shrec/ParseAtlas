"""Tests for the equivalence-preserving transformation axes of experiment 0026.

The sub-corpus used here is deliberately tiny.  The full 40-formula sweep belongs to the
experiment run, not to the test suite; what these tests assert is that the proof obligation is
strict, that the counters are internally consistent, and that the parallel path changes nothing
except how long the sweep takes.
"""

import pytest
from sympy import Mul, Pow, Symbol, cos, sin, sqrt, sympify, tan

from parseatlas import transformation_axes
from parseatlas.canonical import operation_cost
from parseatlas.critical_path import depth_profile
from parseatlas.grammar import all_grammars
from parseatlas.parser import parse
from parseatlas.transformation_axes import (
    AXES,
    AXIS_DEFINITIONS,
    CORPUS,
    DEPTH_CONVENTIONS,
    DOMAINS,
    WORKER_CAP,
    WORKER_HEADROOM_CORES,
    Program,
    as_program,
    axis_yield_report,
    default_worker_count,
    depth_convention_sensitivity,
    excluded_points,
    generate_candidates,
    inline,
    parse_formula,
    safe_sample_points,
    spearman_rank_correlation,
    structural_cost,
    verify_equivalence,
    worker_count_for,
)

X = Symbol("x", real=True)
A = Symbol("a", real=True)
B = Symbol("b", real=True)

SUB_CORPUS = tuple(
    formula for formula in CORPUS if formula.id in ("a_cancelling_quotient", "n_odd_gap")
)

# The measured verdict distribution of the sub-corpus, pinned candidate by candidate.
SUB_CORPUS_VERDICTS: dict[tuple[str, str], dict[str, int]] = {
    ("a_cancelling_quotient", "mul_square_trade"): {"equivalent": 2, "domain_violating": 1},
    ("a_cancelling_quotient", "sign_placement"): {"equivalent": 2},
    ("a_cancelling_quotient", "algebraic_rewrite"): {"equivalent": 1, "domain_violating": 1},
    ("a_cancelling_quotient", "operation_fusion"): {},
    ("a_cancelling_quotient", "common_subexpression_reuse"): {},
    ("n_odd_gap", "mul_square_trade"): {"equivalent": 1},
    ("n_odd_gap", "sign_placement"): {"equivalent": 2},
    ("n_odd_gap", "algebraic_rewrite"): {"equivalent": 1},
    ("n_odd_gap", "operation_fusion"): {},
    ("n_odd_gap", "common_subexpression_reuse"): {},
}


def unevaluated_x_over_x() -> Mul:
    """``x/x`` as a representation rather than as a value.

    SymPy cancels ``x/x`` to ``1`` during construction, so the interesting pair cannot be
    written down at all without ``evaluate=False``.  That is not a trick: it is the same
    cancellation the rewrite under test performs, moved from the rewriter into the parser.
    """
    return Mul(X, Pow(X, -1, evaluate=False), evaluate=False)


# --- the closed vocabulary --------------------------------------------------


def test_axis_vocabulary_is_closed_and_documented():
    assert AXES == (
        "mul_square_trade",
        "sign_placement",
        "algebraic_rewrite",
        "operation_fusion",
        "common_subexpression_reuse",
    )
    assert set(AXIS_DEFINITIONS) == set(AXES)
    assert all(AXIS_DEFINITIONS[axis].strip() for axis in AXES)


def test_an_unlisted_axis_is_a_rejection_and_not_a_new_class():
    with pytest.raises(ValueError, match="vocabulary is closed"):
        generate_candidates(A * B, "coordinate_systems")


# --- the proof obligation ---------------------------------------------------


def test_verify_equivalence_accepts_a_known_equivalent_pair():
    result = verify_equivalence(X * X - 1, (X - 1) * (X + 1), ("x",))
    assert result["verdict"] == "equivalent"
    assert result["symbolic_equal"] is True
    assert result["domain_preserved"] is True
    assert result["numeric_points_checked"] == 3
    assert result["numeric_equal"] is True
    assert result["symbolic_numeric_disagreement"] is False


def test_verify_equivalence_rejects_x_over_x_against_one_as_domain_violating():
    """The load-bearing test: a rewrite that deletes a restriction is a rejection, not a win."""
    result = verify_equivalence(unevaluated_x_over_x(), sympify("1"), ("x",))
    assert result["verdict"] == "domain_violating"
    assert result["symbolic_equal"] is True
    assert result["domain_preserved"] is False
    assert result["excluded_original"] == ["0"]
    assert result["excluded_candidate"] == []
    # The numeric probe cannot see this, which is precisely why the domain check exists.
    assert result["numeric_equal"] is True
    assert result["symbolic_numeric_disagreement"] is False


def test_verify_equivalence_rejects_a_genuinely_non_equivalent_pair():
    result = verify_equivalence(X * X - 1, (X - 1) * (X + 2), ("x",))
    assert result["verdict"] == "unsound"
    assert result["symbolic_equal"] is False
    assert result["unprovable"] is False
    assert result["numeric_equal"] is False
    assert result["symbolic_numeric_disagreement"] is False


def test_the_sub_corpus_verdicts_are_exactly_the_measured_distribution():
    """Which candidate gets which verdict, and why.

    Asserting that the verdict is one of three strings asserts nothing: ``verify_equivalence``
    ends in an ``if/elif/else`` over those three literals and cannot return anything else.  What
    is worth pinning is the distribution itself, and -- for every candidate -- that the verdict
    rests on the evidence it claims to rest on: an ``equivalent`` has a zero residual *and* the
    same excluded set, a ``domain_violating`` is symbolically equal *and* strictly loses
    excluded points, an ``unsound`` is not symbolically equal.
    """
    for formula in SUB_CORPUS:
        expression = parse_formula(formula)
        for axis in AXES:
            counts: dict[str, int] = {}
            for candidate in generate_candidates(expression, axis):
                verdict = verify_equivalence(expression, candidate, formula.variables)
                counts[verdict["verdict"]] = counts.get(verdict["verdict"], 0) + 1
                if verdict["verdict"] == "equivalent":
                    assert verdict["residual"] == "0"
                    assert set(verdict["excluded_original"]) == set(verdict["excluded_candidate"])
                elif verdict["verdict"] == "domain_violating":
                    assert verdict["symbolic_equal"] is True
                    assert set(verdict["excluded_candidate"]) < set(verdict["excluded_original"])
                else:
                    assert verdict["symbolic_equal"] is False
            assert counts == SUB_CORPUS_VERDICTS[(formula.id, axis)]


def test_the_domain_check_inspects_only_numeric_exponent_divisions():
    """The three known gaps in condition (2), pinned so they cannot drift unannounced.

    ``excluded_points`` recognises exactly one shape, ``Pow(base, negative number)``.  All three
    cases below are outside this experiment's corpus -- it has no radical, no logarithm and no
    symbolic exponent -- which is why no reported number depends on them, and all three are
    named in the docstring and in the report's limitations.
    """
    exponent = Symbol("n")
    # (a) a radical branch restriction is invisible: sqrt(x)**2 needs x >= 0 and x does not,
    #     yet the pair is admitted as equivalent.
    radical = Pow(sqrt(X), 2, evaluate=False)
    assert excluded_points(radical) == ()
    assert verify_equivalence(radical, X, ("x",))["verdict"] == "equivalent"
    # (b) a symbolic exponent hides a division: x**n * x**-n excludes x = 0 and 1 does not.
    #     The outer Mul needs evaluate=False as well: without it SymPy folds the product to
    #     Integer(1) before the check ever runs, and both assertions below become true for
    #     every possible implementation.  The two guards keep that collapse from returning.
    hidden = Mul(Pow(X, exponent), Pow(X, -exponent, evaluate=False), evaluate=False)
    assert hidden != 1
    assert hidden.free_symbols == {X, exponent}
    assert excluded_points(hidden) == ()
    assert verify_equivalence(hidden, sympify("1"), ("x", "n"))["verdict"] == "equivalent"
    # (c) over-strict the other way: a pole that is not a Pow is not seen as a shared
    #     restriction, so an honest rewrite is rejected.
    tangent = verify_equivalence(sin(X) / cos(X), tan(X), ("x",))
    assert tangent["verdict"] == "domain_violating"
    assert tangent["excluded_original"]  # the poles of cos, which tan has as well
    assert tangent["excluded_candidate"] == []


def test_the_numeric_probe_samples_both_signs():
    values = [value for assignment in safe_sample_points(("x", "y")) for value in assignment.values()]
    assert any(value > 0 for value in values)
    assert any(value < 0 for value in values)


def test_the_signed_probe_confirms_a_sign_dependent_rejection_instead_of_contradicting_it():
    """``sqrt(x*x)`` is ``|x|``, not ``x``.

    The symbolic verdict rejects it under either sample set; the point of sampling both signs is
    that the independent numeric check now agrees with that rejection.  On a positive-only
    sample set every probe point satisfies the false identity, so the probe would report
    agreement and be recorded as disagreeing with a correct symbolic verdict.
    """
    result = verify_equivalence(sqrt(X * X), X, ("x",))
    assert result["verdict"] == "unsound"
    assert result["numeric_equal"] is False
    assert result["symbolic_numeric_disagreement"] is False


def test_excluded_points_follow_the_canonical_undefined_terms_convention():
    assert excluded_points(unevaluated_x_over_x()) == ("0",)
    assert excluded_points(sympify("1")) == ()
    assert excluded_points(1 / (A - B)) == ("b",)


def test_a_reuse_program_does_not_look_like_a_domain_change():
    temporary = Symbol("_t0")
    program = Program(((temporary, A - B),), X / temporary)
    assert excluded_points(program) == ("b",)
    assert verify_equivalence(X / (A - B), program, ("a", "b", "x"))["verdict"] == "equivalent"


# --- structural cost --------------------------------------------------------


@pytest.mark.parametrize("source", ["2*x + 3*y", "(x + 1)*(y + 2)", "a + b*c"])
def test_structural_cost_depth_matches_the_critical_path_convention(source):
    """Both conventions count the leaf level, and agree on any node SymPy keeps binary."""
    control = all_grammars()[0]
    parser_depth = operation_cost(parse(source, control))["depth"]
    assert structural_cost(sympify(source))["depth"] == parser_depth
    assert depth_profile(source)["control_depth"] == parser_depth


@pytest.mark.parametrize("source", ["2*x + 3*y", "(x + 1)*(y + 2)", "a + b*c"])
def test_all_three_depth_conventions_agree_wherever_sympy_keeps_the_tree_binary(source):
    """The n-ary charge is a choice, but it is an invisible one until a node is flattened."""
    depths = {
        convention: structural_cost(sympify(source), convention)["depth"]
        for convention in DEPTH_CONVENTIONS
    }
    assert len(set(depths.values())) == 1


def test_the_depth_conventions_diverge_exactly_on_a_flattened_node():
    flattened = sympify("a + b + c + d")
    assert structural_cost(flattened, "balanced")["depth"] == 3  # ceil(log2(4)) = 2 over a leaf
    assert structural_cost(flattened, "left_chain")["depth"] == 4  # 4 - 1 = 3 over a leaf
    assert structural_cost(flattened, "flat")["depth"] == 2  # one level over a leaf
    for convention in DEPTH_CONVENTIONS:
        assert structural_cost(flattened, convention)["total_operations"] == 3


def test_an_unknown_depth_convention_is_a_rejection_and_not_a_silent_default():
    with pytest.raises(ValueError, match="unknown depth convention"):
        structural_cost(A + B, "wavefront")
    with pytest.raises(ValueError, match="unknown depth convention"):
        axis_yield_report(SUB_CORPUS, workers=1, depth_convention="wavefront")


def test_structural_cost_counts_a_leaf_as_depth_one():
    assert structural_cost(X)["depth"] == 1
    assert structural_cost(X)["total_operations"] == 0


def test_structural_cost_reports_kinds_and_their_total():
    cost = structural_cost(sympify("a*b + a*c"))
    assert cost["mul"] == 2
    assert cost["add"] == 1
    assert cost["total_operations"] == 3
    assert cost["total_operations"] == sum(cost[kind] for kind in ("add", "mul", "div", "pow", "neg", "func"))


def test_structural_cost_charges_a_reused_temporary_once_and_keeps_its_depth():
    temporary = Symbol("_t0")
    program = Program(((temporary, Symbol("t", real=True) * Symbol("w", real=True)),),
                      Symbol("A", real=True) * cos(temporary) + Symbol("B", real=True) * sin(temporary))
    inlined = structural_cost(inline(program))
    reused = structural_cost(program)
    assert reused["mul"] == inlined["mul"] - 1
    assert reused["depth"] == inlined["depth"]
    assert reused["assignments"] == 1


# --- candidate generation ---------------------------------------------------


def test_an_axis_with_no_applicable_rewrite_yields_zero_candidates_without_raising():
    formula = next(item for item in CORPUS if item.id == "t_pythagorean")
    expression = parse_formula(formula)
    assert generate_candidates(expression, "operation_fusion") == ()
    assert generate_candidates(expression, "common_subexpression_reuse") == ()
    assert generate_candidates(Symbol("z", real=True), "mul_square_trade") == ()


def test_every_generated_candidate_differs_structurally_from_its_input():
    for formula in SUB_CORPUS:
        expression = parse_formula(formula)
        original = as_program(expression).key()
        for axis in AXES:
            candidates = generate_candidates(expression, axis)
            keys = [candidate.key() for candidate in candidates]
            assert original not in keys
            assert len(keys) == len(set(keys))


def test_generation_is_deterministic():
    expression = parse_formula(next(item for item in CORPUS if item.id == "n_odd_gap"))
    for axis in AXES:
        first = [candidate.key() for candidate in generate_candidates(expression, axis)]
        second = [candidate.key() for candidate in generate_candidates(expression, axis)]
        assert first == second


def test_the_difference_of_squares_trade_reaches_the_shorter_representation():
    expression = parse_formula(next(item for item in CORPUS if item.id == "n_odd_gap"))
    baseline = structural_cost(expression)
    reached = [
        structural_cost(candidate)
        for candidate in generate_candidates(expression, "mul_square_trade")
        if verify_equivalence(expression, candidate, ("n",))["verdict"] == "equivalent"
    ]
    assert any(
        cost["total_operations"] < baseline["total_operations"] and cost["depth"] < baseline["depth"]
        for cost in reached
    )


# --- the corpus -------------------------------------------------------------


def test_the_corpus_covers_eight_domains_with_several_formulas_each():
    assert len(DOMAINS) == 8
    assert len(CORPUS) == 40
    counts = {domain: sum(item.domain == domain for item in CORPUS) for domain in DOMAINS}
    assert all(count >= 5 for count in counts.values())
    assert len({item.id for item in CORPUS}) == len(CORPUS)


def test_every_corpus_formula_parses_with_its_declared_variables():
    for formula in CORPUS:
        expression = parse_formula(formula)
        assert {str(symbol) for symbol in expression.free_symbols} <= set(formula.variables)


# --- rank correlation -------------------------------------------------------


def test_spearman_is_one_on_a_monotone_pair_and_minus_one_when_reversed():
    assert spearman_rank_correlation([1, 2, 3, 4], [2, 4, 6, 8]) == pytest.approx(1.0)
    assert spearman_rank_correlation([1, 2, 3, 4], [8, 6, 4, 2]) == pytest.approx(-1.0)


def test_spearman_is_undefined_rather_than_zero_when_a_side_is_constant():
    assert spearman_rank_correlation([1, 1, 1], [1, 2, 3]) is None
    assert spearman_rank_correlation([1], [1]) is None
    assert spearman_rank_correlation([1, 2], [1]) is None


# --- the yield report -------------------------------------------------------


def test_axis_yield_report_counts_are_internally_consistent():
    report = axis_yield_report(SUB_CORPUS, workers=1)
    for scope in (report["per_axis"], report["per_domain"], report["per_domain_axis"]):
        for cell in scope.values():
            assert cell["candidates"] == cell["equivalent"] + cell["domain_violating"] + cell["unsound"]
            assert cell["reduces_both"] <= min(cell["reduces_operations"], cell["reduces_depth"])
            assert cell["reduces_depth_only"] == cell["reduces_depth"] - cell["reduces_both"]
    totals = report["totals"]
    assert totals["candidates"] == totals["equivalent"] + totals["domain_violating"] + totals["unsound"]
    assert totals["candidates"] == sum(cell["candidates"] for cell in report["per_axis"].values())
    assert report["correlated_pairs"] == totals["equivalent"]


def test_axis_yield_report_records_the_domain_violating_rejection_as_a_rejection():
    report = axis_yield_report(SUB_CORPUS, workers=1)
    assert report["totals"]["domain_violating"] >= 1
    violations = [item for item in report["examples"] if item["kind"] == "domain_violating"]
    assert violations
    assert any(item["formula"] == "a_cancelling_quotient" for item in violations)
    for item in violations:
        assert set(item["excluded_candidate"]) != set(item["excluded_original"])


def test_axis_yield_report_rejects_an_empty_corpus_instead_of_reporting_a_vacuous_yield():
    with pytest.raises(ValueError, match="at least one formula"):
        axis_yield_report((), workers=1)


def test_sequential_and_parallel_reports_are_identical():
    sequential = axis_yield_report(SUB_CORPUS, workers=1)
    parallel = axis_yield_report(SUB_CORPUS, workers=2)
    assert sequential["execution"] == "sequential"
    assert parallel["execution"] == "parallel"
    assert sequential["workers"] == 1
    assert parallel["workers"] == 2
    for report in (sequential, parallel):
        report.pop("execution")
        report.pop("workers")
    assert sequential == parallel


def test_the_depth_convention_moves_depth_alone_and_never_the_verdicts():
    """The invariant that makes the report's three-convention sensitivity table honest.

    The convention is applied after admission, so it cannot change what was admitted or what an
    operation-count model sees -- only the depth charged to an admitted candidate.  Any figure
    that moves with the convention is a figure the report must publish under all three.
    """
    sensitivity = depth_convention_sensitivity(SUB_CORPUS, workers=1)
    assert set(sensitivity) == set(DEPTH_CONVENTIONS)
    reference = sensitivity["balanced"]
    for row in sensitivity.values():
        for key in ("candidates", "equivalent", "domain_violating", "unsound", "reduces_operations"):
            assert row[key] == reference[key]


def test_the_depth_convention_actually_reaches_the_sweep():
    """Invariance alone cannot show the parameter is wired through; this shows it moves figures.

    ``SUB_CORPUS`` flattens no node, so every depth-derived figure happens to agree across the
    three conventions there -- which means the invariance test above would still pass if
    ``axis_yield_report`` ignored its ``depth_convention`` argument entirely and returned three
    copies of ``balanced``.  These two formulas do flatten a node, so the depth-derived figures
    genuinely diverge and the wiring is pinned.
    """
    flattening = tuple(item for item in CORPUS if item.id in ("d_logistic_rhs", "q_completed_square"))
    assert len(flattening) == 2
    sensitivity = depth_convention_sensitivity(flattening, workers=1)

    # The admission side is still untouched by the convention.
    for key, expected in (("candidates", 25), ("equivalent", 24), ("domain_violating", 1), ("unsound", 0), ("reduces_operations", 1)):
        assert {row[key] for row in sensitivity.values()} == {expected}

    # The depth side moves, and these are the measured values.
    assert [sensitivity[name]["reduces_depth"] for name in DEPTH_CONVENTIONS] == [6, 4, 7]
    assert [sensitivity[name]["depth_reduced_without_operation_reduction"] for name in DEPTH_CONVENTIONS] == [6, 4, 7]
    correlations = [sensitivity[name]["operation_depth_correlation"] for name in DEPTH_CONVENTIONS]
    assert len(set(correlations)) == 3
    assert correlations[2] < correlations[0] < correlations[1]


@pytest.mark.parametrize("cores", [1, 2, 3, 4, 5, 8, 12, 13, 14, 15, 16, 32, 64, 256])
def test_worker_count_never_returns_zero_and_never_claims_the_whole_machine(cores):
    workers = worker_count_for(cores)
    assert 1 <= workers <= max(1, cores)
    assert workers <= WORKER_CAP
    if cores >= WORKER_HEADROOM_CORES + 1:
        assert cores - workers >= WORKER_HEADROOM_CORES


def test_worker_count_is_monotone_in_cores_and_saturates_at_the_cap():
    counts = [worker_count_for(cores) for cores in range(1, 129)]
    assert all(later >= earlier for earlier, later in zip(counts, counts[1:]))
    assert max(counts) == WORKER_CAP
    assert counts[-1] == WORKER_CAP


@pytest.mark.parametrize("observed,expected", [(None, 1), (1, 1), (4, 2), (16, 12), (128, 12)])
def test_default_worker_count_is_derived_from_the_observed_core_count(monkeypatch, observed, expected):
    """The project rule is that the count is derived, never a constant: two different observed
    machines must give two different answers, and an unreportable core count must not crash."""
    monkeypatch.setattr(transformation_axes.os, "cpu_count", lambda: observed)
    assert default_worker_count() == expected
