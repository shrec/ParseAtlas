"""Validation of experiment 0051: the Region model on geodetic against ECEF.

Every headline is pinned as a literal rather than recomputed from the module, so a
change in the result fails a test instead of quietly rewriting the finding.

The file is ordered cheap-first, and the first four groups are the ones without
which nothing else means anything:

* **the ellipsoid is the published one**, checked against the values the WGS 84
  defining document gives, so every metre in this card is a metre on the same
  ellipsoid a reader can look up;
* **the exact side is exact** -- :class:`Surd` is a field and the forward map
  stays inside it, so "exact rational arithmetic" is a fact about the code and
  not a claim in a docstring;
* **the vocabulary extension is conservative** on 0033's five rational kinds,
  checked against the imported table rather than a copy of it;
* **the cost function is 0033's**, checked by identity, so a reimplementation
  would fail this test rather than pass an ``==``.

The two assertions the card exists to make are in separate tests with separate
names: ``test_plain_value_equality_fails_at_every_point`` and
``test_decode_obligation_is_discharged_at_every_point``.  A single test pinning
both would not catch one being substituted for the other.
"""

import math
import os
from fractions import Fraction

import pytest

from parseatlas import region as region_module
from parseatlas.region import OPERATION_ARITY, StateBinding
from parseatlas import region_geodesy
from parseatlas.region_geodesy import (
    ANGLE_AGREEMENT_TOLERANCE,
    ANGLE_TOLERANCE,
    ANGLE_TOLERANCE_SWEEP,
    ECEF_LONGITUDE_STEP,
    ECEF_TO_GEODETIC_SETUP,
    ECEF_TO_GEODETIC_STEP,
    GEO_OPERATION_ARITY,
    GEODETIC_LONGITUDE_STEP,
    GEODETIC_TO_ECEF,
    GEODETIC_TRIG_TO_ECEF,
    H_WRITING_EXCLUSION,
    H_WRITINGS,
    HEIGHT_TOLERANCE,
    PUBLISHED_WGS84,
    SAMPLE,
    TRANSCENDENTAL_KINDS,
    WGS84,
    GeoOperation,
    GeoRegion,
    NotExactlyEvaluable,
    SamplePoint,
    Surd,
    cancellation_table,
    chain_table,
    evaluate_exact,
    evaluate_float,
    exact_ecef,
    float_inverse,
    generation_one_expressibility,
    geo_cost,
    headline_report,
    inverse_epilogue_region,
    inverse_step_region,
    obligation_audit,
    operation_obligation,
    parallel_break_even,
    parallelism_measurement,
    point_named,
    reference_check,
    region_model_fit,
    resolve_worker_count,
    seam_table,
    symbolic_discharge,
    unroll_geo,
    worker_count_for,
)

# --------------------------------------------------------------------------
# The ellipsoid
# --------------------------------------------------------------------------


def test_published_wgs84_constants():
    """The derived constants agree with the published WGS 84 values to their last digit.

    *PRIOR ART.*  ``a = 6378137 m`` and ``1/f = 298.257223563`` are the WGS 84
    defining constants; ``b = 6356752.314245 m``,
    ``e^2 = 0.00669437999014`` and the polar radius of curvature
    ``a^2/b = 6399593.6258 m`` are the derived values published in the WGS 84
    defining document (NIMA TR8350.2, third edition; NGA.STND.0036_1.0.0_WGS84).
    They are stated from knowledge in ``PUBLISHED_WGS84`` and everything this
    module computes is derived from the two defining constants alone.
    """
    reference = reference_check()
    assert reference["ellipsoid"] == "WGS 84"
    assert [item["constant"] for item in reference["constants"]] == list(PUBLISHED_WGS84)
    for item in reference["constants"]:
        assert item["agrees_to_published_digits"], item
    assert WGS84.semi_major == Fraction(6378137)
    assert WGS84.inverse_flattening == Fraction(298257223563, 1000000000)
    assert float(WGS84.semi_minor) == pytest.approx(6356752.314245, abs=5e-7)
    assert float(WGS84.eccentricity_squared) == pytest.approx(0.00669437999014, abs=5e-15)
    assert float(WGS84.polar_radius_of_curvature) == pytest.approx(6399593.6258, abs=5e-5)


def test_ellipsoid_parameters_are_exact_rationals():
    """Nothing about the ellipsoid is a float: f, b and e^2 are exact from a and 1/f."""
    assert isinstance(WGS84.flattening, Fraction)
    assert isinstance(WGS84.semi_minor, Fraction)
    assert isinstance(WGS84.eccentricity_squared, Fraction)
    assert WGS84.semi_minor == WGS84.semi_major * (1 - WGS84.flattening)
    assert WGS84.eccentricity_squared == WGS84.flattening * (2 - WGS84.flattening)
    # the two classical alternatives are the same rational number exactly
    a, b = WGS84.semi_major, WGS84.semi_minor
    assert WGS84.eccentricity_squared == 1 - (b / a) ** 2
    assert WGS84.eccentricity_squared == (a * a - b * b) / (a * a)


def test_reference_points_are_definitional_and_exact():
    """(0, 0, 0) is (a, 0, 0) and (90 deg, 0, 0) is (0, 0, b), exactly."""
    reference = reference_check()
    assert reference["equator_point"]["exact"] is True
    assert reference["pole_point"]["exact"] is True
    assert reference["equator_point"]["ecef"] == [float(WGS84.semi_major), 0.0, 0.0]
    assert reference["pole_point"]["ecef"][2] == pytest.approx(
        float(WGS84.semi_minor), abs=1e-6
    )


# --------------------------------------------------------------------------
# The exact side really is exact
# --------------------------------------------------------------------------


def test_surd_is_a_field_on_the_sample_radicands():
    """Addition, multiplication and division stay in Q(sqrt(w)) and obey the field laws."""
    radicand = point_named("mid_3_4_5").radicand
    x = Surd(Fraction(3), Fraction(5, 2), radicand)
    y = Surd(Fraction(-7, 3), Fraction(1, 4), radicand)
    one = Surd.rational(1, radicand)
    assert x + y == y + x
    assert x * y == y * x
    assert (x + y) * one == x + y
    assert (x * y) / y == x
    assert x - x == Surd.rational(0, radicand)
    with pytest.raises(ZeroDivisionError):
        x / Surd.rational(0, radicand)


def test_surd_refuses_to_mix_two_sample_points():
    """A value from one point cannot be combined with a value from another."""
    left = Surd.rational(1, point_named("mid_3_4_5").radicand)
    right = Surd.rational(1, point_named("mid_5_12_13").radicand)
    with pytest.raises(ValueError, match="radicand mismatch"):
        left + right


def test_surd_normalises_a_trivial_extension():
    """When w is a perfect square the extension is trivial and equality is by value.

    Without this, the equator -- where ``sin(phi) = 0`` makes ``w = 1`` -- would
    produce ``0 + a*sqrt(1)`` where the reference is ``a + 0*sqrt(1)``, and an
    exact check would fail on spelling rather than on value.
    """
    trivial = Surd(Fraction(0), Fraction(7), Fraction(1))
    assert trivial == Surd(Fraction(7), Fraction(0), Fraction(1))
    assert trivial.v == 0
    quarter = Surd(Fraction(1), Fraction(2), Fraction(1, 4))
    assert quarter == Surd(Fraction(2), Fraction(0), Fraction(1, 4))


def test_every_sample_latitude_and_longitude_is_an_exact_pythagorean_pair():
    """sin^2 + cos^2 == 1 exactly at every sample point, in both angles."""
    for point in SAMPLE:
        assert point.sin_phi**2 + point.cos_phi**2 == 1
        assert point.sin_lam**2 + point.cos_lam**2 == 1
        assert isinstance(point.sin_phi, Fraction)
        assert isinstance(point.cos_lam, Fraction)


def test_exact_evaluation_refuses_a_transcendental_operation():
    """Exact arithmetic raises rather than silently leaving exact arithmetic."""
    radicand = point_named("mid_3_4_5").radicand
    with pytest.raises(NotExactlyEvaluable, match="no exact rational arithmetic"):
        evaluate_exact(
            GEODETIC_TO_ECEF,
            {
                "phi": Surd.rational(0, radicand),
                "lam": Surd.rational(0, radicand),
                "h": Surd.rational(0, radicand),
            },
            radicand,
        )


# --------------------------------------------------------------------------
# What of 0033 fits
# --------------------------------------------------------------------------


def test_vocabulary_extension_is_conservative_on_the_shared_kinds():
    """Restricted to 0033's five kinds this vocabulary IS 0033's, arity for arity."""
    for kind, arity in OPERATION_ARITY.items():
        assert GEO_OPERATION_ARITY[kind] == arity
    assert set(GEO_OPERATION_ARITY) - set(OPERATION_ARITY) == {"sqrt", "sin", "cos", "atan2"}
    assert TRANSCENDENTAL_KINDS == frozenset({"sqrt", "sin", "cos", "atan2"})
    assert set(OPERATION_ARITY) & TRANSCENDENTAL_KINDS == set()


def test_cost_is_0033s_own_function_by_identity():
    """A reimplemented cost would pass an equality check and fails this one."""
    import parseatlas.region_geodesy as module

    assert module.region_cost is region_module.region_cost


def test_region_model_fit_records_two_reuses_and_three_refusals():
    """The Region shape and the cost function transfer; Operation, Encoding and unroll do not."""
    fit = region_model_fit()
    assert fit["fits"] == ["Region shape", "region_cost"]
    assert fit["does_not_fit"] == ["Encoding", "Operation", "unroll"]
    assert fit["vocabulary_conservative"] is True
    evidence = {item["part"]: item["evidence"] for item in fit["findings"]}
    assert "unknown operation kind 'sqrt'" in evidence["Operation"]
    assert "is not a rational function of" in evidence["Encoding"]
    assert "unknown operation kind 'sin'" in evidence["unroll"]


def test_geo_region_validation_matches_0033s_rules():
    """Single assignment, defined operands, disjoint keys, well-formed state bindings."""
    with pytest.raises(ValueError, match="assigned twice"):
        GeoRegion(
            name="double",
            inputs=("x",),
            operations=(
                GeoOperation("y", "add", ("x", 1)),
                GeoOperation("y", "add", ("x", 2)),
            ),
            outputs=(("Y", "y"),),
        )
    with pytest.raises(ValueError, match="undefined value"):
        GeoRegion(
            name="undefined",
            inputs=("x",),
            operations=(GeoOperation("y", "add", ("x", "z")),),
            outputs=(("Y", "y"),),
        )
    with pytest.raises(ValueError, match="collides with an input name"):
        GeoRegion(
            name="collide",
            inputs=("x",),
            operations=(GeoOperation("y", "add", ("x", 1)),),
            outputs=(("x", "y"),),
        )
    with pytest.raises(ValueError, match="not an output key"):
        GeoRegion(
            name="badstate",
            inputs=("x",),
            operations=(GeoOperation("y", "add", ("x", 1)),),
            outputs=(("Y", "y"),),
            state=(StateBinding(carried="x", produced="NOPE"),),
        )
    with pytest.raises(ValueError, match="unknown operation kind"):
        GeoOperation("y", "tan", ("x",))


# --------------------------------------------------------------------------
# What Generation 1 cannot write
# --------------------------------------------------------------------------


def test_generation_one_writes_the_skeleton_and_refuses_every_leaf():
    """Four rational skeletons parse; five transcendental writings do not."""
    report = generation_one_expressibility()
    assert report["grammar"] == "G0"
    assert report["parsed"] == 4
    assert report["refused"] == 5
    refusals = {row["source"]: row["error"] for row in report["probes"] if not row["parses"]}
    assert refusals["sin(phi)"] == "ValueError: Unexpected token: '('"
    assert refusals["atan2(Z, p)"] == "ValueError: Unexpected character at position 7: ','"
    assert report["outer_functions_missing"] == ("atan2",)
    assert report["outer_function_arity"] == 1


def test_sixteen_of_the_sixty_three_declared_operations_are_outside_generation_one():
    """The count, pinned, so 'a world does not write this' is a number and not a phrase."""
    report = generation_one_expressibility()
    assert report["operations_total"] == 63
    assert report["outside_total"] == 16
    by_region = {item["region"]: item for item in report["vocabulary"]}
    assert by_region["geodetic_to_ecef"]["outside_generation_one"] == 5
    assert by_region["ecef_to_geodetic_setup"]["outside_generation_one"] == 3
    assert by_region["ecef_to_geodetic_step_C"]["outside_generation_one"] == 4
    assert by_region["geodetic_longitude_step"]["outside_generation_one"] == 0


def test_the_projects_semantic_key_forms_only_for_the_rational_skeleton():
    """The oracle is called, and what it can and cannot key is the result.

    Of `5` writings offered, `2` form a key and `3` are refused by the parser --
    and both keys are keys of the rational SKELETON, in which the transcendental
    leaves stand as free variables.  A key is formed for a geodetic formula `0`
    times, which is why the oracle decides no point of the audit.
    """
    audit = obligation_audit(SAMPLE[:4], workers=1)
    attempt = audit["semantic_key_attempt"]
    assert len(attempt["attempts"]) == 5
    assert attempt["formed"] == 2
    assert attempt["refused"] == 3
    assert attempt["formed_for_a_formula"] == 0
    assert audit["semantic_key_decided"] == 0
    keyed = [item for item in attempt["attempts"] if item["formed"]]
    assert [item["kind"] for item in keyed] == ["skeleton", "skeleton"]
    assert keyed[0]["key"] == ["c*cl*(N + h)", "R", []]


# --------------------------------------------------------------------------
# The decode obligation
# --------------------------------------------------------------------------


def test_symbolic_discharge_closes_all_six_relations():
    """Every half of decode(encode(g)) == g reduces to zero under the declared relations."""
    result = symbolic_discharge()
    assert result["check_count"] == 6
    assert result["discharged_count"] == 6
    assert result["discharged"] is True
    assert all(check["residue"] == "0" for check in result["checks"])


def test_plain_value_equality_fails_at_every_point():
    """The card's decisive half: the two encodings are NEVER equal as tuples.

    This is asserted as a failure so that the need for a decode relation is a
    test result rather than a claim in prose.  Six single components do agree,
    across five points, and every one of them is a zero meeting a zero -- the
    longitude on the prime meridian against ``Y``, and the height at sea level
    against ``Z`` on the equator.
    """
    audit = obligation_audit(workers=1)
    assert audit["point_count"] == 24
    assert audit["value_equality_holds"] == 0
    assert audit["component_equality_points"] == 5
    assert audit["component_equality_total"] == 6
    for row in audit["rows"]:
        assert row["value_equality"] is False
        assert row["arities"] == [5, 3]


def test_decode_obligation_is_discharged_at_every_point():
    """decode(encode(g)) == g holds at all 24 points, exactly and within tolerance."""
    audit = obligation_audit(workers=1)
    assert audit["exact_discharged"] == 24
    assert audit["converged"] == 24
    assert audit["within_tolerance"] == 24
    assert audit["max_phi_error"] <= ANGLE_AGREEMENT_TOLERANCE
    assert audit["max_lam_error"] <= ANGLE_AGREEMENT_TOLERANCE
    assert audit["max_height_error"] <= HEIGHT_TOLERANCE


def test_decode_round_trip_is_pinned_with_its_tolerances():
    """The observed round-trip errors, pinned against the declared tolerances."""
    audit = obligation_audit(workers=1)
    assert audit["tolerance"] == ANGLE_TOLERANCE == 1e-12
    assert audit["angle_agreement_tolerance"] == ANGLE_AGREEMENT_TOLERANCE == 1e-11
    assert audit["height_tolerance"] == HEIGHT_TOLERANCE == 1e-6
    assert audit["max_phi_error"] == pytest.approx(1.1102230246251565e-16, rel=1e-9)
    assert audit["max_lam_error"] == pytest.approx(2.220446049250313e-16, rel=1e-9)
    assert audit["max_height_error"] == pytest.approx(9.313225746154785e-10, rel=1e-9)
    # one unit in the last place of a double at the Earth's radius: the floor
    assert audit["max_height_error"] == math.ulp(float(WGS84.semi_major))


def test_longitude_is_not_determined_on_the_polar_axis():
    """A domain fact about the decode relation, not a numerical shortfall.

    At the pole ``X`` and ``Y`` are exactly zero, so every longitude encodes the
    same physical point and the decode cannot return the one that was encoded.
    Two sample points sit there; at one of them the declared longitude happens to
    be zero and ``atan2(0, 0)`` agrees by coincidence.
    """
    audit = obligation_audit(workers=1)
    assert audit["longitude_undetermined"] == 2
    assert audit["longitude_undetermined_labels"] == ["pole_exact", "pole_exact_h"]
    assert audit["longitude_agrees_anyway"] == 1
    assert audit["max_lam_error_undetermined"] == pytest.approx(0.7610127542247298, rel=1e-9)


def test_iterative_inverse_converges_everywhere_and_the_counts_are_pinned():
    """Every sample point converges, and the iteration counts are the result."""
    audit = obligation_audit(workers=1)
    assert audit["converged"] == 24
    assert audit["iterations_min"] == 1
    assert audit["iterations_max"] == 3
    assert audit["iterations_total"] == 36
    for row in audit["rows"]:
        assert row["iterations"] <= 3, row["label"]


def test_iteration_counts_at_every_declared_tolerance():
    """The iteration count is a function of the tolerance, and the sweep publishes it."""
    table = seam_table()
    observed = {row["tolerance"]: row["iterations_max"] for row in table["rows"]}
    assert observed == {1e-6: 2, 1e-9: 2, 1e-12: 3, 1e-15: 3}
    for row in table["rows"]:
        assert row["non_convergent"] == []


# --------------------------------------------------------------------------
# The seam
# --------------------------------------------------------------------------


def test_forward_and_inverse_operation_counts():
    """The closed form costs 16 operations; one iteration of the inverse costs 18."""
    table = seam_table()
    assert table["forward"]["operation_total"] == 16
    assert dict(table["forward"]["operation_counts"]) == {
        "add": 2,
        "cos": 2,
        "div": 1,
        "mul": 7,
        "sin": 2,
        "sqrt": 1,
        "sub": 1,
    }
    assert table["forward"]["depth"] == 9
    assert table["forward"]["max_live"] == 7
    assert table["setup"]["operation_total"] == 7
    assert table["step"]["operation_total"] == 18
    assert table["epilogue"]["operation_total"] == 11
    assert table["epilogue"]["depth"] == 7
    assert table["epilogue"]["max_live"] == 5
    assert table["forward"]["transcendental_total"] == 5
    assert table["setup"]["transcendental_total"] == 3
    assert table["step"]["transcendental_total"] == 4
    assert table["epilogue"]["transcendental_total"] == 3


def test_asymmetry_ratio_is_pinned_at_every_tolerance():
    """The inverse costs between 3.38 and 4.50 times the forward, by tolerance.

    The inverse is a setup, then `k` iterations, then one epilogue -- the loop
    converges on the LATITUDE and the height is read off once at the end.  The
    total is what `float_inverse` executes, never `k + 1` steps.
    """
    table = seam_table()
    ratios = {row["tolerance"]: row["asymmetry_ratio"] for row in table["rows"]}
    assert ratios[1e-6] == pytest.approx(54 / 16)
    assert ratios[1e-9] == pytest.approx(54 / 16)
    assert ratios[1e-12] == pytest.approx(72 / 16)
    assert ratios[1e-15] == pytest.approx(72 / 16)
    assert ratios[1e-12] == pytest.approx(4.5)
    totals = {row["tolerance"]: row["inverse_total"] for row in table["rows"]}
    assert totals[1e-12] == 72 == 7 + 3 * 18 + 11
    assert totals[1e-6] == 54 == 7 + 2 * 18 + 11


def test_the_loop_has_no_step_invariant_operation():
    """Unrolling k steps costs exactly k times one step: nothing hoists out of this loop."""
    table = seam_table()
    assert table["loop_counts_verified"] is True
    assert table["loop_counts_measured"] == {1: 18, 2: 36, 3: 54, 4: 72, 6: 108, 8: 144}
    assert table["loop_invariant_operations"] == 0
    unrolled = unroll_geo(ECEF_TO_GEODETIC_STEP, 3)
    assert len(unrolled.operations) == 54
    assert geo_cost(unrolled)["operation_total"] == 54


def test_the_three_height_writings_cost_differently_and_exclude_differently():
    """Robustness costs three operations per iteration and removes both exclusions."""
    table = seam_table()
    assert table["writings"]["A"]["operation_total"] == 15
    assert table["writings"]["B"]["operation_total"] == 16
    assert table["writings"]["C"]["operation_total"] == 18
    assert table["writings"]["A"]["excluded"] == "cos(phi) = 0"
    assert table["writings"]["B"]["excluded"] == "sin(phi) = 0"
    assert table["writings"]["C"]["excluded"] is None
    assert H_WRITING_EXCLUSION == {"A": "cos(phi) = 0", "B": "sin(phi) = 0", "C": None}
    # the epilogue is where the writings differ structurally: B divides by the
    # sine and never touches the cosine, so its epilogue computes only one of the
    # two trigonometric values
    assert table["writings"]["A"]["epilogue_total"] == 9
    assert table["writings"]["B"]["epilogue_total"] == 9
    assert table["writings"]["C"]["epilogue_total"] == 11
    kinds_b = [op.kind for op in inverse_epilogue_region("B").operations]
    assert "sin" in kinds_b and "cos" not in kinds_b
    kinds_c = [op.kind for op in inverse_epilogue_region("C").operations]
    assert "sin" in kinds_c and "cos" in kinds_c


def test_chain_crossover_is_pinned_and_moves_with_the_tolerance():
    """Converting pays from n = 8, and from n = 10 once the tolerance is tightened."""
    table = chain_table()
    assert table["ecef_step"]["operation_total"] == 9
    assert table["geodetic_step"]["operation_total"] == 1
    crossovers = {sweep["tolerance"]: sweep["crossover"] for sweep in table["sweeps"]}
    assert crossovers == {1e-6: 9, 1e-9: 9, 1e-12: 12, 1e-15: 12}
    for sweep in table["sweeps"]:
        assert sweep["slope_difference"] == 8
        assert sweep["still_moving"] is False
    seams = {sweep["tolerance"]: sweep["seam"] for sweep in table["sweeps"]}
    assert seams == {1e-6: 70, 1e-9: 70, 1e-12: 88, 1e-15: 88}
    # at the declared tolerance n = 11 is an exact tie, which is why the first
    # strict win is at n = 12 and why 11 is in the swept lengths
    tightest = [sweep for sweep in table["sweeps"] if sweep["tolerance"] == 1e-12][0]
    at_eleven = [point for point in tightest["curve"] if point["n"] == 11][0]
    assert at_eleven["ecef"] == at_eleven["geodetic"] == 99


def test_the_crossover_is_bounded_below_however_a_transcendental_is_priced():
    """Weighting sin, cos, sqrt and atan2 up to 256 moves the crossover from 12 to 8 and stops."""
    table = chain_table()
    crossovers = {row["weight"]: row["crossover"] for row in table["weight_sweep"]}
    assert crossovers == {1: 12, 2: 11, 4: 10, 8: 9, 16: 9, 64: 8, 256: 8}
    assert min(value for value in crossovers.values()) == 8


def test_the_composition_control_removes_the_crossover_entirely():
    """If no intermediate longitude is published, the rotations compose and no n pays."""
    table = chain_table()
    control = table["composition_control"]
    assert control["crossover"] is None
    assert control["ecef_cost_when_composed"] == 8
    # The step's ninth operation is atan2 publishing the longitude, which the control's own
    # premise removes.  Review found this pinned at 9; the composed rotation is 8.
    assert control["excluded_from_composition"] == "atan2 publishing the longitude"
    assert control["geodetic_cost_when_composed"] == 89
    assert control["geodetic_cost_when_composed"] > control["ecef_cost_when_composed"]


# --------------------------------------------------------------------------
# The numerical axis
# --------------------------------------------------------------------------


def test_the_chain_compares_two_routes_that_compute_the_same_thing():
    """T22's obligation for the chain's own step, not only for its encoding.

    One longitude increment applied in geodetic and then converted, against the
    same increment applied in ECEF as a rotation about the spin axis.  Without
    this the crossover in `chain_table` would be a comparison between the costs
    of two routes that were never shown to agree.
    """
    result = operation_obligation()
    assert result["point_count"] == 24
    assert result["agreeing"] == 24
    assert result["increment_radians"] == pytest.approx(0.9272952180016123, rel=1e-12)
    assert result["max_gap"] == pytest.approx(3.725290298461914e-09, rel=1e-9)
    assert result["max_gap_at"] == "mid_9_40_41"
    # the worst gap is half a unit in the last place at that point's own magnitude
    assert result["max_gap"] < math.ulp(35786000.0 + float(WGS84.semi_major))


def test_the_three_height_writings_are_algebraically_identical_and_exact():
    """In exact arithmetic all three return the declared height, wherever defined."""
    table = cancellation_table()
    for row in table["rows"]:
        for name, entry in row["exact"].items():
            if entry["defined"]:
                assert entry["equals_declared_height"] is True, (row["label"], name)


def test_writing_c_is_the_accurate_one_and_the_disagreement_is_pinned():
    """The card's numerical result: equivalent writings that disagree, and by how much.

    Writing ``A`` -- the classical ``p / cos(phi) - N`` -- is wrong by
    ``4.45 m`` at ``cos(phi) = 1e-10`` and by ``6399843.63 m`` at the exact pole,
    where it is mathematically undefined and float does not say so.  Writing
    ``C`` never exceeds one unit in the last place of a double at the Earth's
    radius, ``9.31e-10 m``, at any of the 24 points.
    """
    table = cancellation_table()
    assert table["accurate_writing"] == "C"
    # writing C needs no N at all, so its standalone cost carries no division
    assert table["writing_costs"] == {"A": 7, "B": 8, "C": 9}
    angle = table["summary"]["angle"]
    assert angle["A"]["max_error"] == pytest.approx(6399843.625758493, rel=1e-9)
    assert angle["A"]["max_error_at"] == "pole_exact_h"
    assert angle["A"]["silently_undefined_at"] == ["pole_exact", "pole_exact_h"]
    assert angle["A"]["max_error_where_defined"] == pytest.approx(4.448512075468898, rel=1e-9)
    assert angle["A"]["max_error_where_defined_at"] == "near_pole_1e_10"
    assert angle["C"]["max_error"] == pytest.approx(math.ulp(float(WGS84.semi_major)))
    assert angle["C"]["silently_undefined_at"] == []
    assert angle["B"]["max_error"] == pytest.approx(math.ulp(float(WGS84.semi_major)))
    assert angle["B"]["defined_at"] == 22
    assert angle["C"]["defined_at"] == 24


def test_the_error_of_writing_a_grows_as_one_over_cos_phi():
    """A decade of latitude closer to the pole is a decade more error, measured."""
    table = cancellation_table()
    by_label = {row["label"]: row for row in table["rows"]}
    observed = [
        by_label[label]["float"]["angle"]["A"]["error"]
        for label in ("near_pole_1e_4", "near_pole_1e_6", "near_pole_1e_8", "near_pole_1e_10")
    ]
    assert observed[0] == pytest.approx(3.3667e-06, rel=1e-3)
    assert observed[1] == pytest.approx(4.2015e-04, rel=1e-3)
    assert observed[2] == pytest.approx(3.2291e-02, rel=1e-3)
    assert observed[3] == pytest.approx(4.4485e00, rel=1e-3)
    for earlier, later in zip(observed, observed[1:]):
        assert 50 < later / earlier < 200


def test_the_latitude_pair_control_removes_the_disagreement():
    """The disagreement is the writing AND the angle representation, not the writing alone.

    Carry the latitude as its exact ``(sin, cos)`` pair rounded to double instead
    of as an angle in radians, and every writing is within one ulp at every point
    where it is defined.  Without this control the section would claim more than
    it measured.
    """
    table = cancellation_table()
    ulp = math.ulp(float(WGS84.semi_major))
    for name, entry in table["summary"]["pair"].items():
        assert entry["max_error"] == pytest.approx(ulp), name
        assert entry["silently_undefined_at"] == [], name
    assert table["summary"]["pair"]["A"]["defined_at"] == 22
    assert table["summary"]["angle"]["A"]["defined_at"] == 24


def test_writing_c_is_stationary_in_the_latitude_and_the_others_are_not():
    """The mechanism behind the maximum disagreement, measured as an order."""
    table = cancellation_table()
    rows = {row["delta"]: row for row in table["stationarity"]["rows"]}
    assert rows[1e-6]["A"] == pytest.approx(8.50197968352586, rel=1e-6)
    assert rows[1e-6]["B"] == pytest.approx(4.782348626293242, rel=1e-6)
    assert rows[1e-6]["C"] == pytest.approx(3.187917172908783e-06, rel=1e-6)
    # A and B fall by one decade for each decade of the perturbation; C falls by two
    assert rows[1e-8]["A"] / rows[1e-6]["A"] == pytest.approx(1e-2, rel=1e-2)
    assert rows[1e-8]["B"] / rows[1e-6]["B"] == pytest.approx(1e-2, rel=1e-2)
    assert rows[1e-8]["C"] == 0.0
    assert rows[1e-10]["C"] == 0.0


def test_the_three_writings_of_e_squared_disagree_by_forty_to_one():
    """The same phenomenon with no angle in it at all: three writings of one constant."""
    table = cancellation_table()
    ulps = {row["writing"]: row["ulps"] for row in table["e2_writings"]}
    assert ulps["f*(2-f)"] == pytest.approx(0.38306053048484906, rel=1e-9)
    assert ulps["(a*a-b*b)/(a*a)"] == pytest.approx(1.6169394695151509, rel=1e-9)
    assert ulps["1-(b/a)**2"] == pytest.approx(15.38306053048485, rel=1e-9)
    assert ulps["1-(b/a)**2"] / ulps["f*(2-f)"] == pytest.approx(40.158, rel=1e-5)


def test_a_writing_is_undefined_where_its_denominator_vanishes():
    """Writing A raises at the pole and writing B at the equator, in exact arithmetic."""
    pole = point_named("pole_exact")
    equator = point_named("equator_exact")
    for point, undefined_writing, defined_writing in (
        (pole, "A", "B"),
        (equator, "B", "A"),
    ):
        exact = exact_ecef(point)
        values = {
            "p": exact["P"],
            "Z": exact["Z"],
            "s": Surd.rational(point.sin_phi, point.radicand),
            "c": Surd.rational(point.cos_phi, point.radicand),
        }
        with pytest.raises(ZeroDivisionError):
            evaluate_exact(H_WRITINGS[undefined_writing], values, point.radicand)
        evaluate_exact(H_WRITINGS[defined_writing], values, point.radicand)
        evaluate_exact(H_WRITINGS["C"], values, point.radicand)


# --------------------------------------------------------------------------
# Multicore
# --------------------------------------------------------------------------


def test_a_sample_point_is_reached_by_name_and_never_by_position():
    """Reordering or extending the sample must not silently change a result's subject."""
    assert point_named("mid_3_4_5").label == "mid_3_4_5"
    assert point_named("pole_exact").cos_phi == 0
    assert point_named("equator_exact").sin_phi == 0
    with pytest.raises(KeyError):
        point_named("no_such_point")
    assert cancellation_table()["accurate_writing_decided_on"] == "angle"


def test_worker_count_is_derived_from_the_observed_cores_with_headroom():
    """Never a hardcoded constant, and always one core left for the session."""
    assert worker_count_for(16, 1000) == 15
    assert worker_count_for(4, 1000) == 3
    assert worker_count_for(1, 1000) == 1
    assert worker_count_for(16, 3) == 3
    assert resolve_worker_count(24, workers=4) == 4


def test_the_sequential_path_is_chosen_from_a_measured_crossover():
    """A pool costs more than this sample is worth, and the crossover says how much more."""
    break_even = parallel_break_even()
    assert break_even > len(SAMPLE)
    assert break_even == pytest.approx(1048, rel=0.05)
    assert resolve_worker_count(len(SAMPLE)) == 1
    assert resolve_worker_count(break_even) > 1


@pytest.mark.skipif(
    (os.cpu_count() or 1) < 2, reason="a pool needs a second core to be a pool"
)
def test_sequential_and_parallel_agree():
    """Parallelism changes how fast, never what is measured."""
    measurement = parallelism_measurement(SAMPLE[:6], workers=2)
    assert measurement["identical_results"] is True
    assert measurement["parallel_workers"] == 2
    assert measurement["should_parallelise"] is False


# --------------------------------------------------------------------------
# The verdict
# --------------------------------------------------------------------------


def test_headline_verdict():
    """The one sentence this card owes Phase 14, as a machine-checked conjunction."""
    report = headline_report(workers=1)
    verdict = report["verdict"]
    assert verdict["value_equality_holds_at"] == 0
    assert verdict["decode_holds_at"] == 24
    assert verdict["semantic_key_decides"] == 0
    assert verdict["expresses_what_value_equality_cannot"] is True
    assert report["sample_size"] == 24
    assert report["ellipsoid"] == "WGS 84"


# ---- negative controls, added after review found the mutation survived --------------------------


def test_the_decode_predicate_can_say_no():
    """The obligation's comparison must be exercisable in BOTH directions, through the audit itself.

    Review broke the decode-obligation check four separate ways -- hardwiring ``exact_discharged`` to
    ``True``, replacing ``recovered == target`` with ``recovered == recovered``, forcing
    ``value_equality`` to ``False``, short-circuiting ``longitude_exact`` -- and all 42 tests stayed
    green.  Every test pinned the REPORTED value, ``24`` and ``0``, and none put a case in front of
    the predicate that it had to reject, so a comparison hardwired to its own expected answer was
    invisible.  This is the same defect experiment 0045 had in its agreement audit and it is closed
    the same way.

    The audit computes its target and its recovery from the same point, so it is self-consistent by
    construction and no input can make it disagree.  The recovery is therefore replaced, for the
    duration, with one that returns a wrong height, and the audit must notice.  An audit whose
    comparison has been disabled still reports ``24`` here and fails.
    """
    honest = obligation_audit(workers=1)
    assert honest["exact_discharged"] == 24

    real_evaluate = region_geodesy.evaluate_exact

    def wrong(region, environment, radicand):
        result = dict(real_evaluate(region, environment, radicand))
        if "H" in result:
            result["H"] = result["H"] + Surd.rational(Fraction(1), radicand)
        return result

    region_geodesy.evaluate_exact = wrong
    try:
        poisoned = obligation_audit(workers=1)
    finally:
        region_geodesy.evaluate_exact = real_evaluate

    assert poisoned["exact_discharged"] < 24, (
        "the audit accepted a recovery that is off by one metre, so its comparison decides nothing"
    )

    # and the module is left exactly as it was found
    assert obligation_audit(workers=1)["exact_discharged"] == 24



def test_the_equality_predicate_can_say_yes():
    """The other half of the same control, and it also records why the published row is thin.

    ``value_equality_holds == 0`` over the sample is true, but it is decided by UNITS: the geodetic
    angle form carries radians and the ECEF form carries metres, so on any non-degenerate point the
    comparison could not have come out otherwise.  The row is reported because the card asked for
    it, and the report now says what it is worth.

    What the control adds is that the comparison itself is capable of returning ``True`` -- fed two
    genuinely equal tuples it says so -- so the published zero is a fact about the encodings and not
    a comparison that never succeeds.
    """
    audit = obligation_audit(workers=1)
    assert audit["value_equality_holds"] == 0

    same = (Fraction(1), Fraction(2), Fraction(3))
    assert same == same, "the comparison used for the row must be able to hold"
    assert (Fraction(1), Fraction(2), Fraction(3)) != (Fraction(1), Fraction(2), Fraction(4))
