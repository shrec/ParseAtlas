"""Validation of the 0028 reachability negative control.

The corpus is built so that every answer is known independently, from the
algebra, before the module is run.  These tests assert the known answer
literally as well as through the module's own bookkeeping, so a corpus entry
cannot quietly redefine what "correct" means.
"""

from fractions import Fraction

import pytest

from parseatlas.reachability_control import (
    CORPUS,
    COMMITMENTS,
    DEFAULT_COMMITMENTS,
    PARALLEL_THRESHOLD_PAIRS,
    RELAXED_COMMITMENTS,
    Assignment,
    Program,
    UndefinedAtPoint,
    corpus_pair,
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
    "coz_analogue": ("preserve_inputs", "preserve_outputs", "map_equality"),
}


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
    ["output_extension", "input_recoding", "erased_prefix", "scaled_representative"],
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
    ["output_extension", "input_recoding", "erased_prefix", "scaled_representative"],
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
    assert report["pair_count"] == 6
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
