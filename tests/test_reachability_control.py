"""Validation of the 0028 reachability negative control.

The corpus is built so that every answer is known independently, from the
algebra, before the module is run.  These tests assert the known answer
literally as well as through the module's own bookkeeping, so a corpus entry
cannot quietly redefine what "correct" means.
"""

import itertools
from dataclasses import replace
from fractions import Fraction

import pytest

from parseatlas.reachability_control import (
    CORPUS,
    COMMITMENTS,
    DEFAULT_COMMITMENTS,
    PAIRS_BY_ID,
    PARALLEL_THRESHOLD_PAIRS,
    RELAXED_COMMITMENTS,
    Assignment,
    CorpusPair,
    Program,
    UndefinedAtPoint,
    corpus_pair,
    evaluate_corpus_pair,
    evaluate_pair,
    gather_evidence,
    input_signature,
    map_equal,
    normalise_commitments,
    output_signature,
    projective_equal,
    reachability_sweep,
    reachability_verdict,
    relaxation_analysis,
    resolve_workers,
    sample_points,
    slice_of_agreement,
    worker_count_for,
)

EXPECTED_VIOLATIONS = {
    "rewriteable_polynomial": (),
    "output_extension": ("preserve_outputs",),
    "input_recoding": ("preserve_inputs",),
    "erased_prefix": ("map_equality",),
    "scaled_representative": ("map_equality",),
    "specialised_input": ("map_equality",),
    "coz_analogue": ("preserve_inputs", "preserve_outputs", "map_equality"),
}

#: A pair the module has never seen, built the way a caller with their own two
#: programs would build one.  Its id is deliberately absent from the built-in
#: corpus: a sweep must be able to run it without any lookup succeeding.
CALLER_REFERENCE = Program(
    name="caller_reference",
    inputs=("u", "v"),
    body=(Assignment("t", "u*v"), Assignment("w", "u + v")),
    outputs=(("T", "t"), ("W", "w")),
)

CALLER_TARGET = Program(
    name="caller_target",
    inputs=("u", "v"),
    body=(Assignment("t", "u*v"), Assignment("w", "u + v"), Assignment("d", "u - v")),
    outputs=(("T", "t"), ("W", "w"), ("D", "d")),
)

CALLER_PAIR = CorpusPair(
    id="callers_own_output_extension",
    reference=CALLER_REFERENCE,
    target=CALLER_TARGET,
    commitments=DEFAULT_COMMITMENTS,
    expected_violations=("preserve_outputs",),
    expected_slice=None,
    note="a caller's own pair: same map on the shared keys, one extra published value",
)


def verdict_for(identifier):
    pair = corpus_pair(identifier)
    return reachability_verdict(pair.reference, pair.target, pair.commitments)


def relaxation_for(identifier):
    pair = corpus_pair(identifier)
    return relaxation_analysis(pair.reference, pair.target, pair.commitments)


# --------------------------------------------------------------------------
# Program representation
# --------------------------------------------------------------------------


def test_program_refuses_a_free_variable():
    """No rule may introduce a free variable: the representation enforces it."""
    with pytest.raises(ValueError, match="uses undefined value 'q'"):
        Program(
            name="leaky",
            inputs=("x",),
            body=(Assignment("t", "x + q"),),
            outputs=(("T", "t"),),
        )


def test_program_refuses_reassignment_and_unknown_output():
    with pytest.raises(ValueError, match="assigned twice"):
        Program(
            name="reassigned",
            inputs=("x",),
            body=(Assignment("t", "x"), Assignment("t", "x + 1")),
            outputs=(("T", "t"),),
        )
    with pytest.raises(ValueError, match="output T uses undefined value 'missing'"):
        Program(
            name="dangling",
            inputs=("x",),
            body=(Assignment("t", "x"),),
            outputs=(("T", "missing"),),
        )


def test_program_refuses_a_non_rational_expression():
    with pytest.raises(ValueError, match="not a rational function"):
        Program(
            name="irrational",
            inputs=("x",),
            body=(Assignment("t", "sqrt(x)"),),
            outputs=(("T", "t"),),
        )


def test_evaluation_is_exact_and_reports_undefined_points():
    program = Program(
        name="reciprocal_sum",
        inputs=("x", "y"),
        body=(Assignment("d", "x - y"), Assignment("t", "(x + y)/d")),
        outputs=(("T", "t"),),
    )
    assert program.evaluate((Fraction(1, 3), Fraction(1, 2))) == {"T": Fraction(-5)}
    with pytest.raises(UndefinedAtPoint):
        program.evaluate((Fraction(2), Fraction(2)))


def test_signatures_are_ordered_inputs_and_unordered_output_keys():
    pair = corpus_pair("coz_analogue")
    assert input_signature(pair.reference) == ("x", "y", "z")
    assert input_signature(pair.target) == ("x", "y", "w")
    assert output_signature(pair.reference) == frozenset({"P", "Q"})
    assert output_signature(pair.target) == frozenset({"P", "Q", "R"})


def test_sample_points_are_deterministic_and_visit_the_unit_slice():
    first = sample_points(3)
    second = sample_points(3)
    assert first == second
    assert len(first) == len(set(first)) == 240
    assert tuple([Fraction(1)] * 3) in first
    on_slice = [point for point in first if point[2] == 1]
    assert 0 < len(on_slice) < len(first)


# --------------------------------------------------------------------------
# Commitment vocabulary
# --------------------------------------------------------------------------


def test_commitment_vocabulary_is_closed():
    assert COMMITMENTS == (
        "preserve_inputs",
        "preserve_outputs",
        "map_equality",
        "projective_equality",
    )
    assert normalise_commitments(["map_equality", "preserve_inputs", "map_equality"]) == (
        "preserve_inputs",
        "map_equality",
    )
    with pytest.raises(ValueError, match="unknown commitments"):
        normalise_commitments(["preserve_inputs", "budget"])


# --------------------------------------------------------------------------
# The reachable pair
# --------------------------------------------------------------------------


def test_reachable_pair_is_reachable_under_every_commitment():
    pair = corpus_pair("rewriteable_polynomial")
    for commitments in (
        DEFAULT_COMMITMENTS,
        RELAXED_COMMITMENTS,
        COMMITMENTS,
    ):
        verdict = reachability_verdict(pair.reference, pair.target, commitments)
        assert verdict.reachable is True
        assert verdict.violated == ()
        assert verdict.satisfied == normalise_commitments(commitments)
    verdict = verdict_for("rewriteable_polynomial")
    assert verdict.agreement_fraction == 1
    assert verdict.map_comparison.symbolic_equal is True
    assert verdict.map_comparison.agreement_count == verdict.map_comparison.defined_count
    assert verdict.agreement_slice is None


# --------------------------------------------------------------------------
# Each blocked pair names exactly one commitment
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "identifier",
    [
        "output_extension",
        "input_recoding",
        "erased_prefix",
        "scaled_representative",
        "specialised_input",
    ],
)
def test_single_blocked_pair_names_exactly_its_own_commitment(identifier):
    verdict = verdict_for(identifier)
    assert verdict.reachable is False
    assert verdict.violated == EXPECTED_VIOLATIONS[identifier]
    assert len(verdict.violated) == 1
    blocker = verdict.violated[0]
    assert set(verdict.satisfied) == set(DEFAULT_COMMITMENTS) - {blocker}
    assert verdict.reason_for(blocker)


def test_output_extension_leaves_the_shared_map_untouched():
    pair = corpus_pair("output_extension")
    comparison = map_equal(pair.reference, pair.target)
    assert comparison.shared_keys == ("V",)
    assert comparison.candidate_only_keys == ("C",)
    assert comparison.equal is True
    assert comparison.agreement_fraction == 1
    verdict = verdict_for("output_extension")
    assert "adds ['C']" in verdict.reason_for("preserve_outputs")


def test_input_recoding_is_the_same_map_on_the_same_tuple():
    pair = corpus_pair("input_recoding")
    comparison = map_equal(pair.reference, pair.target)
    assert comparison.positional_rename == (("y_bar", "y"),)
    assert comparison.equal is True
    assert comparison.agreement_fraction == 1
    verdict = verdict_for("input_recoding")
    assert "input list differs" in verdict.reason_for("preserve_inputs")


# --------------------------------------------------------------------------
# The slice case
# --------------------------------------------------------------------------


def test_erased_prefix_agreement_fraction_is_strictly_between_zero_and_one():
    verdict = verdict_for("erased_prefix")
    fraction = verdict.agreement_fraction
    assert fraction is not None
    assert Fraction(0) < fraction < Fraction(1)
    comparison = verdict.map_comparison
    assert comparison.defined_count == 240
    assert 0 < comparison.agreement_count < comparison.defined_count
    assert fraction == Fraction(comparison.agreement_count, comparison.defined_count)
    assert comparison.symbolic_equal is False
    assert comparison.disagreement_examples


def test_slice_of_agreement_finds_the_constructed_constraint():
    pair = corpus_pair("erased_prefix")
    found = slice_of_agreement(pair.reference, pair.target)
    assert found is not None
    assert found.common_factors == ("z - 1",)
    assert len(found.constraints) == 1
    constraint = found.constraints[0]
    assert constraint.symbol == "z"
    assert constraint.solution == "z = 1"
    assert constraint.equation == "z - 1 = 0"
    assert constraint.verified_symbolically is True
    assert constraint.slice_sample_count > 0
    assert constraint.slice_agreement_fraction == 1


def test_scaled_representative_slice_is_the_point_where_the_scale_is_one():
    pair = corpus_pair("scaled_representative")
    found = slice_of_agreement(pair.reference, pair.target)
    assert found is not None
    assert found.constraints[0].solution == "x = 0"
    assert found.constraints[0].slice_agreement_fraction == 1


# --------------------------------------------------------------------------
# Which of several true slices is the primary one
# --------------------------------------------------------------------------


def test_primary_slice_is_the_informative_one_not_the_alphabetical_one():
    """The one-output pair that pins the choice of primary constraint.

    ``F = a*c`` against ``F = 2*a`` differ by ``a*(c - 2)``, so *both* ``a = 0``
    and ``c = 2`` are genuine, symbolically verified slices of agreement.  They
    are not equally useful.  On ``c = 2`` the two programs are the same
    non-constant map ``2*a`` and the constraint names the missing
    transformation; on ``a = 0`` both collapse to the constant ``0`` and agree
    only by saying nothing.  A caller reading ``.primary`` alone must get the
    first one, and a lexicographic rule over the factors would hand them the
    second.
    """
    pair = corpus_pair("specialised_input")
    found = slice_of_agreement(pair.reference, pair.target)
    assert found is not None

    # Two common factors, and the degenerate one sorts first alphabetically:
    # this is exactly the case a lexicographic primary gets wrong.
    assert found.common_factors == ("a", "c - 2")
    assert sorted(found.common_factors)[0] == "a"

    # Both are reported and both are true; ranking decides which one leads.
    assert [constraint.equation for constraint in found.constraints] == [
        "c - 2 = 0",
        "a = 0",
    ]
    for constraint in found.constraints:
        assert constraint.verified_symbolically is True
        assert constraint.slice_agreement_fraction == 1

    primary = found.primary
    assert primary is not None
    assert primary.solution == "c = 2"
    assert primary.non_constant_keys == ("F",)

    degenerate = found.constraints[1]
    assert degenerate.solution == "a = 0"
    assert degenerate.non_constant_keys == ()
    assert "the primary is c - 2 = 0" in found.reason


def test_the_verdict_reports_the_informative_slice_to_the_caller():
    """`.primary` is what the verdict text and the sweep both read."""
    verdict = verdict_for("specialised_input")
    assert verdict.violated == ("map_equality",)
    assert verdict.agreement_slice is not None
    assert verdict.agreement_slice.primary is not None
    assert verdict.agreement_slice.primary.solution == "c = 2"
    assert "they agree exactly where c = 2" in verdict.reason_for("map_equality")
    assert evaluate_pair("specialised_input")["observed_slice"] == "c = 2"


def test_ranking_happens_before_the_report_is_truncated():
    """`max_constraints` bounds what is reported, never what is considered.

    Three common factors, two of them degenerate and both sorting ahead of the
    informative one.  Truncating first and ranking second would report ``a = 0``
    and hide ``c = 2`` entirely.
    """
    reference = Program(
        name="triple_product",
        inputs=("a", "b", "c"),
        body=(Assignment("v", "a*b*c"),),
        outputs=(("F", "v"),),
    )
    target = Program(
        name="triple_frozen",
        inputs=("a", "b", "c"),
        body=(Assignment("v", "2*a*b"),),
        outputs=(("F", "v"),),
    )
    full = slice_of_agreement(reference, target)
    assert full is not None
    assert full.common_factors == ("a", "b", "c - 2")
    assert [constraint.equation for constraint in full.constraints] == [
        "c - 2 = 0",
        "a = 0",
        "b = 0",
    ]

    capped = slice_of_agreement(reference, target, max_constraints=1)
    assert capped is not None
    assert [constraint.equation for constraint in capped.constraints] == ["c - 2 = 0"]
    assert capped.primary is not None and capped.primary.solution == "c = 2"
    assert "2 further slice(s) not reported" in capped.reason


def test_a_lower_degree_constraint_wins_a_tie_on_retained_structure():
    """Second ranking key, exercised with the first one tied.

    The difference is ``(b - a**2)*(c - 1)`` added to a map that survives both
    slices, so both constraints leave ``F`` varying and the first key decides
    nothing.  Degree then picks ``c = 1``, the substitution a caller can carry
    out, over the quadratic ``b = a**2``.  Note that a lexicographic rule would
    pick the other one: ``a**2 - b = 0`` sorts first.
    """
    reference = Program(
        name="two_factor_reference",
        inputs=("a", "b", "c"),
        body=(Assignment("v", "(b - a*a)*(c - 1) + a + b + c"),),
        outputs=(("F", "v"),),
    )
    target = Program(
        name="two_factor_target",
        inputs=("a", "b", "c"),
        body=(Assignment("v", "a + b + c"),),
        outputs=(("F", "v"),),
    )
    found = slice_of_agreement(reference, target)
    assert found is not None
    assert found.common_factors == ("a**2 - b", "c - 1")
    ranked = [
        (constraint.equation, constraint.non_constant_keys, constraint.factor_degree)
        for constraint in found.constraints
    ]
    # First key ties: both slices leave the shared key varying.
    assert [entry[1] for entry in ranked] == [("F",), ("F",)]
    assert ranked == [("c - 1 = 0", ("F",), 1), ("a**2 - b = 0", ("F",), 2)]
    assert found.primary is not None and found.primary.solution == "c = 1"
    assert sorted(found.common_factors)[0] == "a**2 - b"


def test_a_factor_without_a_single_solution_is_never_reported():
    """A common factor that cannot be solved for one input yields no constraint.

    ``x**2 - 2`` has no rational root, so the module reports it among the common
    factors and does not turn it into a slice.  The two constraints it does
    report are ranked as usual: ``y = 1`` leaves ``F`` varying, ``x = 0``
    collapses it.
    """
    reference = Program(
        name="quadratic_pair",
        inputs=("x", "y"),
        body=(Assignment("v", "(x*x - 2)*(y - 1)*x + x"),),
        outputs=(("F", "v"),),
    )
    target = Program(
        name="quadratic_pair_reduced",
        inputs=("x", "y"),
        body=(Assignment("v", "x"),),
        outputs=(("F", "v"),),
    )
    found = slice_of_agreement(reference, target)
    assert found is not None
    assert set(found.common_factors) == {"x", "x**2 - 2", "y - 1"}
    assert [constraint.equation for constraint in found.constraints] == [
        "y - 1 = 0",
        "x = 0",
    ]
    assert found.primary is not None and found.primary.solution == "y = 1"
    assert found.constraints[-1].non_constant_keys == ()


def test_no_slice_is_reported_for_an_equal_pair():
    pair = corpus_pair("rewriteable_polynomial")
    assert slice_of_agreement(pair.reference, pair.target) is None


def test_a_pair_with_no_common_factor_reports_no_constraint():
    reference = Program(
        name="pair_reference",
        inputs=("x", "y"),
        body=(Assignment("p", "x"), Assignment("q", "y")),
        outputs=(("P", "p"), ("Q", "q")),
    )
    target = Program(
        name="pair_target",
        inputs=("x", "y"),
        body=(Assignment("p", "x + 1"), Assignment("q", "y + 2"),),
        outputs=(("P", "p"), ("Q", "q")),
    )
    found = slice_of_agreement(reference, target)
    assert found is not None
    assert found.common_factors == ()
    assert found.constraints == ()
    assert found.primary is None
    assert "no common factor" in found.reason


# --------------------------------------------------------------------------
# The projective relaxation
# --------------------------------------------------------------------------


def test_scaled_representative_is_projectively_equal_but_not_raw_equal():
    pair = corpus_pair("scaled_representative")
    raw = map_equal(pair.reference, pair.target)
    assert raw.equal is False
    projective = projective_equal(pair.reference, pair.target)
    assert projective.equal is True
    assert projective.scale_expression == "x**2 + 1"
    assert projective.scale_is_constant is False
    assert projective.agreement_fraction == 1
    relaxed = reachability_verdict(pair.reference, pair.target, RELAXED_COMMITMENTS)
    assert relaxed.reachable is True
    assert relaxed.violated == ()


def test_projective_equality_does_not_rescue_a_genuinely_different_map():
    pair = corpus_pair("erased_prefix")
    projective = projective_equal(pair.reference, pair.target)
    assert projective.equal is False
    relaxed = reachability_verdict(pair.reference, pair.target, RELAXED_COMMITMENTS)
    assert relaxed.reachable is False
    assert relaxed.violated == ("projective_equality",)


def test_weighted_grading_is_honoured():
    """A weighted scaling convention is expressed by the declared weights alone."""
    reference = Program(
        name="graded_reference",
        inputs=("x", "y"),
        body=(Assignment("a", "x + y"), Assignment("b", "x - y")),
        outputs=(("A", "a"), ("B", "b")),
    )
    target = Program(
        name="graded_target",
        inputs=("x", "y"),
        body=(
            Assignment("k", "x*x + 1"),
            Assignment("a", "(x + y)*k"),
            Assignment("b", "(x - y)*k*k"),
        ),
        outputs=(("A", "a"), ("B", "b")),
    )
    assert projective_equal(reference, target).equal is False
    weighted = projective_equal(reference, target, weights={"A": 1, "B": 2})
    assert weighted.equal is True
    assert weighted.scale_key == "A"
    assert weighted.scale_expression == "x**2 + 1"
    # Points where the weight-one key vanishes fix no scale; they are counted as
    # undetermined rather than scored as failures.
    assert weighted.undetermined_count > 0
    assert weighted.agreement_count == weighted.defined_count - weighted.undetermined_count


# --------------------------------------------------------------------------
# Relaxation analysis
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "identifier",
    [
        "output_extension",
        "input_recoding",
        "erased_prefix",
        "scaled_representative",
        "specialised_input",
    ],
)
def test_relaxation_analysis_identifies_the_single_blocking_commitment(identifier):
    report = relaxation_for(identifier)
    expected = EXPECTED_VIOLATIONS[identifier][0]
    assert report.baseline_reachable is False
    assert report.sole_blocker == expected
    assert report.unblocking == (expected,)
    for drop in report.drops:
        assert drop.reachable is (drop.commitment == expected)
    assert report.drop_for(expected).remaining_violations == ()


def test_relaxation_analysis_reports_the_projective_weakening():
    scaled = relaxation_for("scaled_representative")
    assert scaled.weakening is not None
    assert scaled.weakening.replacement == "projective_equality"
    assert scaled.weakening.reachable is True

    erased = relaxation_for("erased_prefix")
    assert erased.weakening is not None
    assert erased.weakening.reachable is False
    assert erased.weakening.remaining_violations == ("projective_equality",)


def test_each_commitment_is_decided_independently_of_the_declared_set():
    """The premise every drop row rests on, asserted directly.

    A commitment's verdict is a function of the two programs and the shared
    evidence and of nothing else: no branch in ``reachability_verdict`` consults
    which *other* commitments were declared alongside it.  ``map_equal``
    comparing shared output keys only is the load-bearing half of that -- were
    it to compare all keys, the map verdict would move with what
    ``preserve_outputs`` is doing.

    Checked exhaustively: every corpus pair against all sixteen subsets of the
    four-name vocabulary.  If a future change made one commitment's decision
    depend on the declared set, this fails, and the set-subtraction identity
    below stops being a theorem.
    """
    for pair in CORPUS:
        evidence = gather_evidence(pair.reference, pair.target)
        alone = {
            name: name
            in reachability_verdict(
                pair.reference, pair.target, (name,), evidence=evidence
            ).violated
            for name in COMMITMENTS
        }
        for size in range(len(COMMITMENTS) + 1):
            for declared in itertools.combinations(COMMITMENTS, size):
                verdict = reachability_verdict(
                    pair.reference, pair.target, declared, evidence=evidence
                )
                assert verdict.violated == tuple(
                    name for name in declared if alone[name]
                )
                assert verdict.reachable is not any(alone[name] for name in declared)


def test_drop_rows_are_set_subtraction_by_construction():
    """An honest statement of a limit in this suite's power, pinned as a test.

    Because each commitment is decided independently of the declared set (the
    test above proves it), removing one commitment can only remove that one from
    the violation set.  ``drop.remaining_violations`` therefore *equals*
    ``baseline.violated`` minus the dropped name for every pair of programs that
    can exist -- it is a theorem about independently decided commitments, not a
    coincidence of this corpus.

    The consequence is stated plainly rather than papered over: a fake that
    replaced the drop re-decision with set subtraction would pass every drop
    assertion, and no reference/target pair can be constructed that separates
    the two.  Constructing one would require a commitment whose decision depends
    on the declared set, which is precisely what the module is built not to
    have.  The un-fakeable row is the weakening, tested next.
    """
    for pair in CORPUS:
        report = relaxation_analysis(pair.reference, pair.target, pair.commitments)
        baseline = reachability_verdict(pair.reference, pair.target, pair.commitments)
        assert tuple(drop.commitment for drop in report.drops) == pair.commitments
        for drop in report.drops:
            expected = tuple(
                name for name in baseline.violated if name != drop.commitment
            )
            assert drop.remaining_violations == expected
            assert drop.reachable is (expected == ())
            assert drop.remaining == tuple(
                name for name in pair.commitments if name != drop.commitment
            )


def test_the_weakening_row_is_not_derivable_from_the_baseline_violations():
    """The load-bearing counterfactual: the one no set subtraction can produce.

    Weakening *adds* ``projective_equality`` to the declared set, and that
    commitment was never decided at baseline.  Its verdict is therefore not a
    function of ``baseline.violated`` at all, and two corpus pairs prove it
    carries information: ``scaled_representative`` and ``erased_prefix`` have
    identical baseline violations and identical drop rows, yet their weakening
    rows disagree.
    """
    scaled = relaxation_for("scaled_representative")
    erased = relaxation_for("erased_prefix")

    # Identical everywhere set subtraction can see.
    assert scaled.baseline_violations == erased.baseline_violations == ("map_equality",)
    assert [drop.remaining_violations for drop in scaled.drops] == [
        drop.remaining_violations for drop in erased.drops
    ]
    assert scaled.sole_blocker == erased.sole_blocker == "map_equality"

    # And different exactly on the row that re-decides a commitment the baseline
    # never touched.
    for report in (scaled, erased):
        assert report.weakening is not None
        assert "projective_equality" not in report.commitments
        assert "projective_equality" in report.weakening.remaining
        assert "map_equality" not in report.weakening.remaining
    assert scaled.weakening.reachable is True
    assert scaled.weakening.remaining_violations == ()
    assert erased.weakening.reachable is False
    assert erased.weakening.remaining_violations == ("projective_equality",)

    # Each weakening row agrees with an independently computed verdict over the
    # set it declares -- the check that would catch a fabricated row.
    for identifier, report in (
        ("scaled_representative", scaled),
        ("erased_prefix", erased),
        ("specialised_input", relaxation_for("specialised_input")),
        ("coz_analogue", relaxation_for("coz_analogue")),
    ):
        pair = corpus_pair(identifier)
        independent = reachability_verdict(
            pair.reference, pair.target, report.weakening.remaining
        )
        assert report.weakening.remaining_violations == independent.violated
        assert report.weakening.reachable is independent.reachable


def test_relaxation_analysis_of_a_reachable_pair_reports_nothing_in_the_way():
    report = relaxation_for("rewriteable_polynomial")
    assert report.baseline_reachable is True
    assert report.baseline_violations == ()
    assert all(drop.reachable for drop in report.drops)
    assert "already reachable" in report.summary


# --------------------------------------------------------------------------
# Regression guard on the 0027 conclusion
# --------------------------------------------------------------------------


def test_coz_analogue_is_blocked_by_all_three_commitments():
    """0027 restated in neutral algebra and pinned here.

    The target has a different input list, a larger output key set, and is a
    different function of the same three numbers, agreeing with the reference
    only where the third input equals 1.  That is the structural content of the
    finding; it should be a test, not only a prose document.
    """
    verdict = verdict_for("coz_analogue")
    assert verdict.reachable is False
    assert verdict.violated == (
        "preserve_inputs",
        "preserve_outputs",
        "map_equality",
    )
    assert verdict.satisfied == ()
    fraction = verdict.agreement_fraction
    assert fraction is not None and Fraction(0) < fraction < Fraction(1)
    assert verdict.agreement_slice is not None
    assert verdict.agreement_slice.primary is not None
    assert verdict.agreement_slice.primary.solution == "z = 1"
    assert verdict.agreement_slice.primary.slice_agreement_fraction == 1


def test_no_single_relaxation_makes_the_coz_analogue_reachable():
    report = relaxation_for("coz_analogue")
    assert report.baseline_reachable is False
    assert report.unblocking == ()
    assert report.sole_blocker is None
    assert [drop.reachable for drop in report.drops] == [False, False, False]
    assert report.weakening is not None and report.weakening.reachable is False
    for drop in report.drops:
        assert len(drop.remaining_violations) == 2
    assert "no single relaxation helps" in report.summary


def test_dropping_every_commitment_is_the_degenerate_case():
    """With no commitment declared there is no language, so nothing is excluded."""
    pair = corpus_pair("coz_analogue")
    verdict = reachability_verdict(pair.reference, pair.target, ())
    assert verdict.commitments == ()
    assert verdict.reachable is True
    assert verdict.detail == ()


# --------------------------------------------------------------------------
# Determinism and the corpus sweep
# --------------------------------------------------------------------------


@pytest.mark.parametrize("identifier", sorted(EXPECTED_VIOLATIONS))
def test_verdict_is_deterministic_across_repeated_runs(identifier):
    first = verdict_for(identifier)
    second = verdict_for(identifier)
    assert first == second
    assert first.as_dict() == second.as_dict()
    assert relaxation_for(identifier).as_dict() == relaxation_for(identifier).as_dict()


def test_evidence_is_shared_across_the_counterfactuals():
    pair = corpus_pair("erased_prefix")
    evidence = gather_evidence(pair.reference, pair.target)
    direct = reachability_verdict(pair.reference, pair.target, DEFAULT_COMMITMENTS)
    reused = reachability_verdict(
        pair.reference, pair.target, DEFAULT_COMMITMENTS, evidence=evidence
    )
    assert direct == reused


def test_corpus_covers_every_required_shape():
    assert [pair.id for pair in CORPUS] == list(EXPECTED_VIOLATIONS)
    for pair in CORPUS:
        assert pair.expected_violations == EXPECTED_VIOLATIONS[pair.id]
        assert pair.commitments == DEFAULT_COMMITMENTS
    blocked_by = [pair.expected_violations for pair in CORPUS]
    assert () in blocked_by
    assert ("preserve_inputs",) in blocked_by
    assert ("preserve_outputs",) in blocked_by
    assert ("map_equality",) in blocked_by
    assert ("preserve_inputs", "preserve_outputs", "map_equality") in blocked_by


def test_sweep_matches_the_independently_known_answers():
    report = reachability_sweep(workers=1)
    assert report["pair_count"] == 7
    assert report["execution"] == "sequential"
    assert report["worker_count"] == 1
    assert report["all_match_known_answers"] is True
    assert report["mismatched"] == []
    assert report["reachable"] == ["rewriteable_polynomial"]
    assert report["blocked"] == [
        "output_extension",
        "input_recoding",
        "erased_prefix",
        "scaled_representative",
        "specialised_input",
        "coz_analogue",
    ]
    for entry in report["pairs"]:
        assert entry["verdict"]["violated"] == list(EXPECTED_VIOLATIONS[entry["id"]])
        assert entry["violations_match_expected"] is True
        assert entry["slice_matches_expected"] is True


def test_sweep_is_deterministic():
    assert reachability_sweep(workers=1) == reachability_sweep(workers=1)


def test_measured_agreement_counts_are_pinned():
    """The reported numbers themselves, so a silent drift in them is a failure."""
    expected = {
        "rewriteable_polynomial": (121, 121),
        "output_extension": (121, 121),
        "input_recoding": (121, 121),
        "erased_prefix": (25, 240),
        "scaled_representative": (11, 121),
        "specialised_input": (21, 121),
        "coz_analogue": (25, 240),
    }
    for entry in reachability_sweep(workers=1)["pairs"]:
        comparison = entry["verdict"]["map_comparison"]
        agreed, defined = expected[entry["id"]]
        assert (comparison["agreement_count"], comparison["defined_count"]) == (
            agreed,
            defined,
        )
    assert len(sample_points(2)) == 121
    assert len(sample_points(3)) == 240


def test_parallel_sweep_reproduces_the_sequential_report():
    """Parallelism changes only how fast, never what is measured."""
    sequential = reachability_sweep(workers=1)
    parallel = reachability_sweep(workers=3)
    assert parallel["execution"] == "parallel"
    assert parallel["worker_count"] == 3
    for key in ("execution", "worker_count"):
        sequential.pop(key)
        parallel.pop(key)
    assert sequential == parallel


def test_worker_resolution_is_derived_from_the_observed_cores():
    assert worker_count_for(16, 100) == 12
    assert worker_count_for(4, 100) == 2
    assert worker_count_for(1, 100) == 1
    assert worker_count_for(16, 3) == 3
    # Below the measured crossover the sweep stays sequential on its own.
    assert resolve_workers(len(CORPUS)) == 1
    assert resolve_workers(PARALLEL_THRESHOLD_PAIRS - 1) == 1
    assert resolve_workers(PARALLEL_THRESHOLD_PAIRS) > 1
    assert resolve_workers(100, 5) == 5
    with pytest.raises(ValueError, match="workers must be at least 1"):
        resolve_workers(6, 0)


def test_evaluate_pair_is_plain_data_and_rejects_unknown_ids():
    entry = evaluate_pair("erased_prefix")
    assert entry["observed_slice"] == "z = 1"
    assert entry["expected_slice"] == "z = 1"
    assert entry["verdict"]["agreement_fraction"] is not None
    with pytest.raises(KeyError, match="unknown corpus pair"):
        evaluate_pair("no_such_pair")


# --------------------------------------------------------------------------
# A caller's own corpus
# --------------------------------------------------------------------------


def test_the_callers_pair_is_not_in_the_built_in_corpus():
    """The precondition the next tests depend on: no lookup can resolve it."""
    assert CALLER_PAIR.id not in PAIRS_BY_ID
    assert CALLER_PAIR not in CORPUS
    with pytest.raises(KeyError, match="unknown corpus pair"):
        corpus_pair(CALLER_PAIR.id)


def test_evaluate_corpus_pair_takes_the_pair_itself():
    entry = evaluate_corpus_pair(CALLER_PAIR)
    assert entry["id"] == CALLER_PAIR.id
    assert entry["reference"] == "caller_reference"
    assert entry["verdict"]["violated"] == ["preserve_outputs"]
    assert entry["violations_match_expected"] is True
    assert entry["slice_matches_expected"] is True
    # The id-keyed entry point still answers for the built-in corpus.
    assert evaluate_pair("erased_prefix") == evaluate_corpus_pair(
        corpus_pair("erased_prefix")
    )


def test_sweep_runs_a_callers_own_corpus():
    """The module is usable by a caller who has their own reference/target pairs."""
    report = reachability_sweep([CALLER_PAIR], workers=1)
    assert report["pair_count"] == 1
    assert report["reachable"] == []
    assert report["blocked"] == [CALLER_PAIR.id]
    assert report["all_match_known_answers"] is True
    assert report["mismatched"] == []
    entry = report["pairs"][0]
    assert entry["verdict"]["violated"] == ["preserve_outputs"]
    assert entry["relaxation"]["sole_blocker"] == "preserve_outputs"


def test_a_callers_corpus_may_mix_in_built_in_pairs():
    mixed = reachability_sweep([CALLER_PAIR, corpus_pair("erased_prefix")], workers=1)
    assert [entry["id"] for entry in mixed["pairs"]] == [
        CALLER_PAIR.id,
        "erased_prefix",
    ]
    assert mixed["all_match_known_answers"] is True
    assert mixed["blocked"] == [CALLER_PAIR.id, "erased_prefix"]


def test_the_built_in_corpus_is_still_the_default():
    default = reachability_sweep(workers=1)
    explicit = reachability_sweep(CORPUS, workers=1)
    assert default == explicit
    assert default["pair_count"] == len(CORPUS) == 7


def test_a_callers_wrong_expectation_is_reported_as_a_mismatch():
    """The known answer is the caller's to declare, and the sweep grades it."""
    wrong = replace(CALLER_PAIR, expected_violations=())
    report = reachability_sweep([wrong], workers=1)
    assert report["all_match_known_answers"] is False
    assert report["mismatched"] == [wrong.id]
    assert report["pairs"][0]["violations_match_expected"] is False
    assert report["pairs"][0]["verdict"]["violated"] == ["preserve_outputs"]


def test_a_callers_corpus_takes_the_parallel_path_unchanged():
    """The pair travels to a worker process, so the caller path is not sequential-only."""
    pairs = (CALLER_PAIR, corpus_pair("erased_prefix")) * 2
    sequential = reachability_sweep(pairs, workers=1)
    parallel = reachability_sweep(pairs, workers=3)
    assert parallel["execution"] == "parallel"
    assert parallel["worker_count"] == 3
    assert parallel["pair_count"] == 4
    for key in ("execution", "worker_count"):
        sequential.pop(key)
        parallel.pop(key)
    assert sequential == parallel


def test_an_empty_corpus_is_refused():
    with pytest.raises(ValueError, match="needs at least one pair"):
        reachability_sweep([], workers=1)
