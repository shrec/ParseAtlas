"""Validation of the 0033 Region model and the decode obligation.

The corpus is built so that every answer is known from the algebra before the
module is run: the deferred-division candidate is the same map at the boundary,
the adversarial candidate is a different map that the declared sample set cannot
see, and the loop-invariant pair is the same map at a different loop cost.  Each
test asserts the known answer literally as well as through the module's own
bookkeeping.
"""

from dataclasses import replace
from fractions import Fraction
from functools import lru_cache

import pytest

from parseatlas import region as region_module
from parseatlas.reachability_control import reachability_verdict, relaxation_analysis
from parseatlas.region import (
    ADVERSARIAL_SAMPLES,
    ADVERSARIAL_STEP,
    DEFERRED_ENCODING,
    DEFERRED_STEP,
    EAGER_STEP,
    IDENTITY_ENCODING,
    IMPOSSIBLE_STEP,
    OFF_GRID_POLE_STEP,
    OFF_GRID_PRECONDITION_STEP,
    ON_GRID_POLE_STEP,
    PRODUCT_HOISTED,
    PRODUCT_SEQUENTIAL,
    BrokenEncoding,
    DomainComparison,
    Encoding,
    Operation,
    Region,
    StateBinding,
    UndefinedAtPoint,
    as_program,
    axis_report,
    commitment_contrast,
    deferred_chain,
    deferred_chain_decoded,
    discharge,
    domain_comparison,
    eager_chain,
    invariant_check,
    precondition_check,
    region_cost,
    unroll,
)


@lru_cache(maxsize=1)
def report():
    """The whole experiment, measured once and shared by every test that pins it."""
    return axis_report()


# --------------------------------------------------------------------------
# The representation
# --------------------------------------------------------------------------


def test_operation_vocabulary_is_closed_and_arity_checked():
    with pytest.raises(ValueError, match="unknown operation kind"):
        Operation("t", "sqrt", ("x",))
    with pytest.raises(ValueError, match="takes 2 operand"):
        Operation("t", "mul", ("x",))
    with pytest.raises(ValueError, match="is not a name"):
        Operation("t", "mul", ("x", "3"))
    assert Operation("t", "mul", ("x", 3)).args == ("x", Fraction(3))


def test_region_refuses_free_variables_reassignment_and_key_collisions():
    with pytest.raises(ValueError, match="uses undefined value 'q'"):
        Region(
            name="leaky",
            inputs=("x",),
            operations=(Operation("t", "add", ("x", "q")),),
            outputs=(("T", "t"),),
        )
    with pytest.raises(ValueError, match="assigned twice"):
        Region(
            name="reassigned",
            inputs=("x",),
            operations=(Operation("t", "neg", ("x",)), Operation("t", "neg", ("x",))),
            outputs=(("T", "t"),),
        )
    with pytest.raises(ValueError, match="collides with an input name"):
        Region(
            name="collision",
            inputs=("x",),
            operations=(Operation("t", "neg", ("x",)),),
            outputs=(("x", "t"),),
        )
    with pytest.raises(ValueError, match="is not an output key"):
        Region(
            name="dangling_state",
            inputs=("x",),
            operations=(Operation("t", "neg", ("x",)),),
            outputs=(("T", "t"),),
            state=(StateBinding("x", "MISSING"),),
        )


def test_evaluation_is_exact_and_reports_the_undefined_point():
    assert EAGER_STEP.evaluate((Fraction(1, 3), Fraction(3), Fraction(2))) == {
        "VALUE": Fraction(1, 2)
    }
    with pytest.raises(UndefinedAtPoint):
        EAGER_STEP.evaluate((Fraction(1), Fraction(1), Fraction(0)))
    # The candidate's arithmetic is total: nothing divides, so nothing fails.
    assert DEFERRED_STEP.evaluate(
        (Fraction(1), Fraction(0), Fraction(3), Fraction(0))
    ) == {"NUM": Fraction(3), "DEN": Fraction(0)}


def test_declared_invariants_hold_symbolically_and_on_the_samples():
    for region in (EAGER_STEP, DEFERRED_STEP, PRODUCT_HOISTED, PRODUCT_SEQUENTIAL):
        checks = invariant_check(region)
        assert checks, f"{region.name} declares no invariant"
        for check in checks:
            assert check.symbolic_verdict is True, (region.name, check.invariant)
            assert check.holding_fraction == 1
            assert check.holds is True


# --------------------------------------------------------------------------
# The encoding gate
# --------------------------------------------------------------------------


def test_encoding_without_a_left_inverse_is_rejected_at_construction():
    """The gate is a constructor, not a use-time check: the object never exists."""
    with pytest.raises(BrokenEncoding, match="not a left inverse"):
        Encoding(
            name="broken_left_inverse",
            baseline_inputs=("v", "a", "b"),
            candidate_inputs=("num", "den", "a", "b"),
            candidate_outputs=("DEN", "NUM"),
            encode=("v", "1", "a", "b"),
            decode=("num + den", "a", "b"),
            output_decode=(("VALUE", "NUM/DEN"),),
        )
    with pytest.raises(BrokenEncoding, match="comes back as v/2"):
        Encoding(
            name="halved",
            baseline_inputs=("v",),
            candidate_inputs=("num", "den"),
            candidate_outputs=("DEN", "NUM"),
            encode=("v", "2"),
            decode=("num/den",),
            output_decode=(("VALUE", "NUM/DEN"),),
        )


def test_encoding_that_leaves_the_decode_domain_is_rejected():
    """A left inverse that lands outside the decode's own domain is still broken."""
    with pytest.raises(BrokenEncoding, match="leaves the decode's declared domain"):
        Encoding(
            name="escapes_codomain",
            baseline_inputs=("v",),
            candidate_inputs=("num", "den"),
            candidate_outputs=("DEN", "NUM"),
            encode=("v", "v"),
            decode=("num*den/(den*den)*den",),
            output_decode=(("VALUE", "NUM/DEN"),),
            codomain=("Ne(den, 0)",),
        )


def test_the_axis_encoding_verifies_and_records_its_own_gate():
    check = DEFERRED_ENCODING.verification
    assert check.left_inverse_symbolic is True
    assert check.failures == ()
    assert check.agreement_fraction == 1
    assert check.codomain_misses == 0
    assert check.codomain_hits == check.admissible_count == check.sample_count
    assert DEFERRED_ENCODING.encode_point((Fraction(5), Fraction(2), Fraction(3))) == (
        Fraction(5),
        Fraction(1),
        Fraction(2),
        Fraction(3),
    )
    assert DEFERRED_ENCODING.decode_outputs(
        {"NUM": Fraction(6), "DEN": Fraction(4)}
    ) == {"VALUE": Fraction(3, 2)}


# --------------------------------------------------------------------------
# The obligation: accepted
# --------------------------------------------------------------------------


def test_discharge_accepts_the_deferred_division_candidate():
    result = discharge(EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING)
    assert result.discharged is True
    assert result.symbolic_verdict is True
    assert result.agreement_fraction == 1
    assert (result.agreement_count, result.both_defined_count) == (217, 217)
    assert result.sample_count == 240
    assert result.outside_domain_count == 0
    assert result.domain_match is True
    assert result.symbolic_sample_conflict is False
    assert result.obligation == "decode(candidate(encode(x))) == baseline(x)"
    # Definedness is decided by factoring the divisors, not by counting points:
    # both sides divide by exactly b, and the sample counts only corroborate.
    assert result.symbolic_domain_decided is True
    assert result.symbolic_domain_match is True
    assert result.symbolic_domain_conflict is False
    assert result.baseline_excluded == result.candidate_excluded == ("b = 0",)
    assert result.sample_domain_match is True
    assert result.domain_undecided_reasons == ()


@pytest.mark.parametrize("steps", [1, 2, 3, 5])
def test_discharge_holds_for_the_whole_chain_not_only_one_step(steps):
    result = discharge(eager_chain(steps), deferred_chain(steps), DEFERRED_ENCODING)
    assert result.discharged is True
    assert result.symbolic_verdict is True
    assert result.agreement_fraction == 1
    assert result.both_defined_count == 217
    assert (result.baseline_only_defined_count, result.candidate_only_defined_count) == (0, 0)
    assert result.symbolic_domain_match is True
    assert result.baseline_excluded == result.candidate_excluded == ("b = 0",)


def test_discharge_refuses_an_encoding_that_does_not_fit_the_pair():
    with pytest.raises(ValueError, match="do not match"):
        discharge(EAGER_STEP, EAGER_STEP, DEFERRED_ENCODING)


# --------------------------------------------------------------------------
# The obligation: rejected, including the adversarial case
# --------------------------------------------------------------------------


def test_discharge_rejects_a_candidate_that_saturates_the_declared_sample_set():
    """The 0028 adversarial shape, restated for the decode obligation.

    The planted factor ``(b - 1)(b - 2)`` vanishes at every point of
    ``ADVERSARIAL_SAMPLES``, so the sampled half of the obligation is total and
    says nothing; cancellation refutes the pair anyway and the candidate is
    rejected with the conflict recorded rather than swallowed.
    """
    declared = discharge(
        EAGER_STEP, ADVERSARIAL_STEP, DEFERRED_ENCODING, ADVERSARIAL_SAMPLES
    )
    assert declared.agreement_fraction == 1
    assert declared.agreement_count == declared.both_defined_count == 32
    assert declared.symbolic_verdict is False
    assert declared.symbolic_sample_conflict is True
    assert declared.discharged is False
    assert "does not separate" in declared.reason

    wider = discharge(EAGER_STEP, ADVERSARIAL_STEP, DEFERRED_ENCODING)
    assert wider.discharged is False
    assert wider.symbolic_verdict is False
    assert wider.agreement_fraction == Fraction(59, 217)
    assert wider.disagreement_examples


def test_the_adversarial_sample_set_is_exactly_the_blind_slice():
    assert len(ADVERSARIAL_SAMPLES) == 32
    assert {point[2] for point in ADVERSARIAL_SAMPLES} == {Fraction(1), Fraction(2)}


# --------------------------------------------------------------------------
# Preconditions
# --------------------------------------------------------------------------


def test_precondition_of_the_baseline_exactly_characterises_definedness():
    check = precondition_check(EAGER_STEP)
    assert check.conditions == ("Ne(b, 0)",)
    assert check.verdict == "conditional"
    assert (check.satisfied_count, check.sample_count) == (217, 240)
    assert check.defined_count == 217
    assert check.satisfied_and_defined_count == 217
    assert check.unsatisfied_but_defined_count == 0
    assert check.satisfied_but_undefined == ()


def test_candidate_precondition_is_strictly_stronger_and_reported_conditional():
    """A zero denominator anywhere in the chain: the candidate computes, and means nothing."""
    check = precondition_check(DEFERRED_STEP)
    assert check.conditions == ("Ne(den, 0)",)
    assert check.verdict == "conditional"
    assert (check.satisfied_count, check.sample_count) == (221, 240)
    # The arithmetic is total -- the precondition is not about definedness at all.
    assert check.defined_count == 240
    assert check.unsatisfied_but_defined_count == 19
    assert check.failing_examples
    for point in check.failing_examples:
        assert point[1] == "0"

    chain = precondition_check(deferred_chain(4))
    assert chain.verdict == "conditional"
    assert (chain.satisfied_count, chain.defined_count) == (221, 240)
    assert chain.unsatisfied_but_defined_count == 19


def test_an_unsatisfiable_precondition_is_named_as_such():
    check = precondition_check(IMPOSSIBLE_STEP)
    assert check.verdict == "unsatisfiable"
    assert check.symbolically_unsatisfiable is True
    assert check.satisfied_count == 0
    assert "not a candidate" in check.reason


def test_the_encode_discharges_the_extra_precondition_by_construction():
    """Every encoded point satisfies the precondition the candidate added."""
    conditions = DEFERRED_STEP.parsed_precondition()
    assert conditions
    for point in ADVERSARIAL_SAMPLES:
        encoded = DEFERRED_ENCODING.encode_point(point)
        assert dict(zip(DEFERRED_STEP.inputs, encoded))["den"] == 1


# --------------------------------------------------------------------------
# Cost at region level, and the loop a per-formula count cannot see
# --------------------------------------------------------------------------


def test_single_step_costs_are_pinned():
    eager = region_cost(EAGER_STEP)
    assert eager.operation_counts == (("div", 1), ("mul", 1))
    assert (eager.operation_total, eager.depth, eager.max_live) == (2, 2, 3)
    assert eager.carried_state == 1

    deferred = region_cost(DEFERRED_STEP)
    assert deferred.operation_counts == (("mul", 2),)
    assert (deferred.operation_total, deferred.depth, deferred.max_live) == (2, 1, 4)
    assert deferred.carried_state == 2


def test_loop_cost_is_symbolic_in_n_and_verified_against_real_unrollings():
    eager = region_cost(EAGER_STEP).loop
    assert dict(eager.symbolic_counts) == {"div": "n", "mul": "n"}
    assert eager.symbolic_total == "2*n"
    assert eager.symbolic_depth == "2*n"
    assert eager.counts_verified is True
    assert eager.depth_affine_verified is True

    deferred = region_cost(DEFERRED_STEP).loop
    assert dict(deferred.symbolic_counts) == {"mul": "2*n"}
    assert deferred.symbolic_total == "2*n"
    assert deferred.symbolic_depth == "n"
    assert deferred.counts_verified is True
    assert deferred.carried_state == 2


def test_loop_cost_separates_a_per_step_overhead_that_a_per_formula_count_misses():
    """Same multiset, same total, same depth, same pressure -- and different loops.

    ``product_hoisted`` forms ``a*b`` outside the carried chain and
    ``product_sequential`` forms ``v*a`` inside it.  Per formula the two are
    indistinguishable on every structural number this model reports.  Over a
    loop one costs ``n + 1`` operations and the other ``2*n``, and the gap grows
    without bound.  This is the measurement T23 says selection actually needs.
    """
    hoisted = region_cost(PRODUCT_HOISTED)
    sequential = region_cost(PRODUCT_SEQUENTIAL)

    assert hoisted.operation_counts == sequential.operation_counts == (("mul", 2),)
    assert hoisted.operation_total == sequential.operation_total == 2
    assert hoisted.depth == sequential.depth == 2
    assert hoisted.max_live == sequential.max_live == 3
    assert hoisted.carried_state == sequential.carried_state == 1

    assert hoisted.loop.symbolic_total == "n + 1"
    assert sequential.loop.symbolic_total == "2*n"
    assert hoisted.loop.symbolic_depth == "n + 1"
    assert sequential.loop.symbolic_depth == "2*n"
    assert hoisted.loop.symbolic_total != sequential.loop.symbolic_total

    for length in (1, 2, 4, 8):
        assert hoisted.loop.count_at("mul", length) == length + 1
        assert sequential.loop.count_at("mul", length) == 2 * length

    # And they are the same boundary object, so equivalence cannot rank them.
    obligation = discharge(PRODUCT_HOISTED, PRODUCT_SEQUENTIAL, IDENTITY_ENCODING)
    assert obligation.discharged is True


def test_unrolling_normalises_and_at_one_step_reproduces_the_region():
    once = unroll(PRODUCT_HOISTED, 1)
    assert region_cost(once, loop_steps=()).operation_counts == (("mul", 2),)
    twice = unroll(PRODUCT_HOISTED, 2)
    # Common-subexpression elimination hoists the loop-invariant product.
    assert region_cost(twice, loop_steps=()).operation_counts == (("mul", 3),)
    with pytest.raises(ValueError, match="at least one step"):
        unroll(PRODUCT_HOISTED, 0)
    with pytest.raises(ValueError, match="names no loop"):
        unroll(
            Region(
                name="stateless",
                inputs=("x",),
                operations=(Operation("t", "neg", ("x",)),),
                outputs=(("T", "t"),),
            ),
            2,
        )


@pytest.mark.parametrize(
    "steps,eager_mul,eager_div,deferred_mul,deferred_div,eager_depth,deferred_depth",
    [
        (1, 1, 1, 2, 1, 2, 2),
        (2, 2, 2, 4, 1, 4, 3),
        (4, 4, 4, 8, 1, 8, 5),
        (8, 8, 8, 16, 1, 16, 9),
    ],
)
def test_chain_costs_and_the_division_crossover(
    steps, eager_mul, eager_div, deferred_mul, deferred_div, eager_depth, deferred_depth
):
    eager = region_cost(eager_chain(steps), loop_steps=())
    deferred = region_cost(deferred_chain_decoded(steps), loop_steps=())

    assert (eager.count("mul"), eager.count("div")) == (eager_mul, eager_div)
    assert (deferred.count("mul"), deferred.count("div")) == (deferred_mul, deferred_div)
    assert (eager.depth, deferred.depth) == (eager_depth, deferred_depth)
    # One extra operation, always: the deferred form is never cheaper in total.
    assert deferred.operation_total == eager.operation_total + 1
    assert eager.count("div") - deferred.count("div") == steps - 1


def test_the_crossover_is_at_two_steps_and_is_only_about_divisions():
    crossover = report()["crossover"]
    assert crossover["first_step_count_with_fewer_divisions"] == 2
    assert crossover["eager_divisions"] == "n"
    assert crossover["deferred_divisions"] == "1"
    assert crossover["saving"] == "n - 1"
    assert crossover["operation_total_difference"] == "1"


# --------------------------------------------------------------------------
# The contrast with the 0028 control
# --------------------------------------------------------------------------


def test_the_0028_control_reports_all_three_commitments_violated():
    """Pinned exactly: this pair is unreachable and no single relaxation helps."""
    reference = as_program(EAGER_STEP)
    target = as_program(DEFERRED_STEP)
    verdict = reachability_verdict(reference, target)

    assert verdict.reachable is False
    assert verdict.violated == ("preserve_inputs", "preserve_outputs", "map_equality")
    assert verdict.satisfied == ()
    assert "input list differs" in verdict.reason_for("preserve_inputs")
    assert "output key set differs" in verdict.reason_for("preserve_outputs")
    assert "arity differs" in verdict.reason_for("map_equality")

    relaxation = relaxation_analysis(reference, target)
    assert relaxation.unblocking == ()
    assert relaxation.sole_blocker is None
    assert "no single relaxation helps" in relaxation.summary


def test_the_same_pair_is_admissible_once_a_decode_is_supplied():
    """The whole point of the card, as one measured comparison."""
    contrast = commitment_contrast(EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING)
    assert contrast["control_reachable"] is False
    assert contrast["control_violated"] == [
        "preserve_inputs",
        "preserve_outputs",
        "map_equality",
    ]
    assert contrast["control_unblocking"] == []
    assert contrast["obligation_discharged"] is True


def test_the_chain_pair_gets_the_same_verdict_as_the_step_pair():
    contrast = commitment_contrast(eager_chain(4), deferred_chain(4), DEFERRED_ENCODING)
    assert contrast["control_violated"] == [
        "preserve_inputs",
        "preserve_outputs",
        "map_equality",
    ]
    assert contrast["obligation_discharged"] is True


def test_a_cost_only_pair_passes_the_control_and_the_obligation_alike():
    """Equivalence separates nothing here; only the loop cost does."""
    contrast = commitment_contrast(
        PRODUCT_HOISTED, PRODUCT_SEQUENTIAL, IDENTITY_ENCODING
    )
    assert contrast["control_reachable"] is True
    assert contrast["control_violated"] == []
    assert contrast["obligation_discharged"] is True


# --------------------------------------------------------------------------
# Definedness, decided symbolically -- and the conjuncts of the obligation
# --------------------------------------------------------------------------


def _widening_baseline(pole):
    """A baseline that reaches ``v*a`` through a division that cancels again.

    The map is ``v*a`` and the domain is not: this region is undefined at
    ``b = pole`` and a candidate that simply multiplies is defined there.  The
    candidate **widens** the domain, which is the direction the sampled check
    can also see only when ``pole`` happens to sit on the grid.
    """
    return Region(
        name=f"widening_baseline_{pole}",
        inputs=("v", "a", "b"),
        operations=(
            Operation("s", "sub", ("b", pole)),
            Operation("w", "div", ("v", "s")),
            Operation("x", "mul", ("w", "s")),
            Operation("y", "mul", ("x", "a")),
        ),
        outputs=(("VALUE", "y"),),
    )


TOTAL_PRODUCT = Region(
    name="total_product",
    inputs=("v", "a", "b"),
    operations=(Operation("y", "mul", ("v", "a")),),
    outputs=(("VALUE", "y"),),
    note="the same map with no division at all, so no point is excluded",
)

DEMANDING_STEP = Region(
    name="demanding_deferred_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("p", "mul", ("num", "a")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "p"), ("DEN", "q")),
    precondition=("Ne(a, 0)",),
    note="the real candidate with a precondition the encode does not discharge",
)


def test_a_pole_off_the_sample_grid_is_rejected_by_the_symbolic_domain_check():
    """The fail-open that got a non-equivalent candidate through, closed.

    ``off_grid_pole_step`` divides by ``b - 7`` and multiplies the factor back,
    so cancellation accepts the boundary map and every one of the 240 declared
    sample points agrees -- ``7`` is not in ``VALUE_POOL``, so no point ever
    lands on the pole.  A definedness check that only counts sample points
    admits it.  The ground truth is that the two are different objects:
    ``baseline.evaluate([1, 1, 7])`` is ``1/7`` and the candidate is undefined
    at the encoded image of that point.
    """
    result = discharge(EAGER_STEP, OFF_GRID_POLE_STEP, DEFERRED_ENCODING)

    # The sampled halves are exactly as blind as they were before the fix.
    assert result.symbolic_verdict is True
    assert result.agreement_fraction == 1
    assert (result.agreement_count, result.both_defined_count) == (217, 217)
    assert result.sample_domain_match is True
    assert (result.baseline_only_defined_count, result.candidate_only_defined_count) == (0, 0)

    # And the symbolic half decides it anyway.
    assert result.symbolic_domain_decided is True
    assert result.symbolic_domain_match is False
    assert result.symbolic_domain_conflict is True
    assert result.baseline_excluded == ("b = 0",)
    assert result.candidate_excluded == ("b = 0", "b = 7")
    assert result.candidate_extra_exclusions == ("b = 7",)
    assert result.baseline_extra_exclusions == ()
    assert result.domain_match is False
    assert result.discharged is False
    assert "b = 7" in result.reason
    assert "does not see this" in result.reason

    # The ground truth the sample grid cannot reach.
    point = (Fraction(1), Fraction(1), Fraction(7))
    assert EAGER_STEP.evaluate(point) == {"VALUE": Fraction(1, 7)}
    with pytest.raises(UndefinedAtPoint):
        OFF_GRID_POLE_STEP.evaluate(DEFERRED_ENCODING.encode_point(point))


def test_a_domain_mismatched_candidate_does_not_discharge():
    """The control for the test above: the identical pole, moved onto the grid.

    ``3`` is in ``VALUE_POOL``, so 20 sample points land on the pole and the
    sampled half sees the mismatch too.  Both halves agree here, which is what
    makes the off-grid case a measurement of the symbolic half rather than a
    coincidence.  This test also pins the ``domain_match`` conjunct: without it
    the candidate below is discharged, because every other conjunct passes.
    """
    result = discharge(EAGER_STEP, ON_GRID_POLE_STEP, DEFERRED_ENCODING)

    assert result.symbolic_verdict is True
    assert result.agreement_fraction == 1
    assert result.precondition_admissible is True
    assert result.sample_domain_match is False
    assert result.baseline_only_defined_count == 20
    assert result.candidate_only_defined_count == 0
    assert result.symbolic_domain_match is False
    assert result.symbolic_domain_conflict is False
    assert result.candidate_extra_exclusions == ("b = 3",)
    assert result.domain_match is False
    assert result.discharged is False


def test_a_vacuous_sample_set_does_not_discharge():
    """No point measured is no evidence, and it must not read as agreement.

    Both cases pin the ``sample_total`` conjunct: the symbolic verdict, the
    domain comparison and the precondition are all satisfied for this pair, so
    without that conjunct an empty sample set discharges the obligation.
    """
    empty = discharge(EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING, [])
    assert empty.sample_count == 0
    assert empty.both_defined_count == 0
    assert empty.agreement_fraction is None
    assert empty.symbolic_verdict is True
    assert empty.domain_match is True
    assert empty.precondition_admissible is True
    assert empty.discharged is False

    # Vacuous in the other way: a sample set on which neither side is defined.
    blind = discharge(
        EAGER_STEP,
        DEFERRED_STEP,
        DEFERRED_ENCODING,
        [(Fraction(1), Fraction(1), Fraction(0)), (Fraction(2), Fraction(3), Fraction(0))],
    )
    assert blind.sample_count == 2
    assert blind.both_defined_count == 0
    assert blind.agreement_fraction is None
    assert blind.discharged is False


def test_the_symbolic_domain_check_reports_the_widening_direction_too():
    """Narrowing is not the only way to move a domain, and both are decided.

    Here the *baseline* carries the cancelling pole and the candidate is total,
    so the candidate is defined where the baseline is not.  With the pole at
    ``b = 3`` the sample set sees it; with the pole at ``b = 7`` only the
    symbolic half does, and the verdict is the same either way.
    """
    on_grid = discharge(_widening_baseline(3), TOTAL_PRODUCT, IDENTITY_ENCODING)
    assert on_grid.symbolic_verdict is True
    assert on_grid.baseline_extra_exclusions == ("b = 3",)
    assert on_grid.candidate_extra_exclusions == ()
    assert on_grid.candidate_only_defined_count == 20
    assert on_grid.discharged is False

    off_grid = discharge(_widening_baseline(7), TOTAL_PRODUCT, IDENTITY_ENCODING)
    assert off_grid.symbolic_verdict is True
    assert off_grid.agreement_fraction == 1
    assert off_grid.sample_domain_match is True
    assert off_grid.candidate_only_defined_count == 0
    assert off_grid.baseline_extra_exclusions == ("b = 7",)
    assert off_grid.symbolic_domain_conflict is True
    assert off_grid.discharged is False
    assert "additionally keeps" in off_grid.reason


def test_domain_comparison_names_the_excluded_sets_of_the_accepted_pair():
    comparison = domain_comparison(EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING)
    assert comparison.decided is True
    assert comparison.equal is True
    assert comparison.matched is True
    # The baseline divides by b; the candidate divides nowhere and the decode
    # divides by DEN = den*b, which the encode sends to b.  Same set.
    assert comparison.baseline_excluded == ("b = 0",)
    assert comparison.candidate_excluded == ("b = 0",)
    assert comparison.undecided_reasons == ()

    # A pair with no division anywhere excludes nothing at all.
    empty = domain_comparison(PRODUCT_HOISTED, PRODUCT_SEQUENTIAL, IDENTITY_ENCODING)
    assert (empty.baseline_excluded, empty.candidate_excluded) == ((), ())
    assert empty.matched is True


def test_an_undecidable_domain_comparison_fails_closed():
    """A declared encoding domain the model cannot reason inside is not a discharge.

    ``Ne(b, 7)`` would in fact excuse ``off_grid_pole_step``: its only extra
    pole sits at the one point the encoding refuses to handle.  The model does
    not decide set differences against a declared domain, so it says so and
    rejects, rather than guessing in the direction that admits.
    """
    restricted = Encoding(
        name="deferred_division_off_seven",
        baseline_inputs=("v", "a", "b"),
        candidate_inputs=("num", "den", "a", "b"),
        candidate_outputs=("DEN", "NUM"),
        encode=("v", "1", "a", "b"),
        decode=("num/den", "a", "b"),
        output_decode=(("VALUE", "NUM/DEN"),),
        domain=("Ne(b, 7)",),
        codomain=("Ne(den, 0)",),
    )
    comparison = domain_comparison(EAGER_STEP, OFF_GRID_POLE_STEP, restricted)
    assert comparison.decided is False
    assert comparison.matched is False
    assert comparison.undecided_reasons
    assert "does not decide" in comparison.reason

    result = discharge(EAGER_STEP, OFF_GRID_POLE_STEP, restricted)
    assert result.symbolic_verdict is True
    assert result.symbolic_domain_decided is False
    assert result.domain_match is False
    assert result.discharged is False

    # The same declared domain over a pair whose excluded sets are equal is
    # decided normally: undecidability is a property of the difference, not of
    # declaring a domain.
    accepted = discharge(EAGER_STEP, DEFERRED_STEP, restricted)
    assert accepted.symbolic_domain_decided is True
    assert accepted.discharged is True


POISONED_STEP = Region(
    name="poisoned_divisor_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("z0", "sub", ("b", "b")),
        Operation("z", "div", ("num", "z0")),
        Operation("y", "div", ("a", "z")),
        Operation("p", "mul", ("num", "a")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "p"), ("DEN", "q")),
    note="divides by zero and then by the result, so a divisor reduces to zoo",
)

OFF_GRID_DEMAND_STEP = Region(
    name="off_grid_demand_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("p", "mul", ("num", "a")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "p"), ("DEN", "q")),
    precondition=("Ne(b, 7)",),
    note="demands b != 7, which no sample point violates and the encode cannot supply",
)


def test_an_undecided_divisor_makes_the_comparison_undecided():
    """A divisor sympy reduces to ``zoo`` is reported, never skipped.

    Skipping it would quietly shrink the excluded set, which is the direction
    that admits.  ``decided`` goes false on the spot and drags
    :attr:`DomainComparison.matched` down with it.
    """
    comparison = domain_comparison(EAGER_STEP, POISONED_STEP, DEFERRED_ENCODING)
    assert comparison.undecided_reasons
    assert any("zoo" in reason for reason in comparison.undecided_reasons)
    assert comparison.decided is False
    assert comparison.matched is False
    assert discharge(EAGER_STEP, POISONED_STEP, DEFERRED_ENCODING).discharged is False


def test_an_undecided_comparison_is_not_a_match_even_when_the_sets_look_equal():
    """``matched`` is ``decided and equal``, and the first half is not decoration.

    Stated directly on the record because the two ways the model reaches
    ``decided=False`` today both also make ``equal`` false, so no end-to-end
    pair separates the conjunction from its second half.
    """
    undecided = DomainComparison(
        baseline="b",
        candidate="c",
        encoding="e",
        baseline_excluded=(),
        candidate_excluded=(),
        candidate_extra_exclusions=(),
        baseline_extra_exclusions=(),
        baseline_excluded_everywhere=False,
        candidate_excluded_everywhere=False,
        decided=False,
        equal=True,
        undecided_reasons=("sympy declined",),
        reason="undecided",
    )
    assert undecided.equal is True
    assert undecided.matched is False


def test_the_symbolic_domain_verdict_cannot_admit_over_a_sample_contradiction(monkeypatch):
    """``domain_match`` is the symbolic verdict **and** the sample corroboration.

    While both halves are correct they cannot disagree in this direction -- the
    factor sets are compared over an algebraically closed field, which contains
    the rationals the sample points come from -- so the only way to pin that the
    corroboration is wired into the conjunct is to make the symbolic half lie.
    ``on_grid_pole_step`` really does lose 20 sample points the baseline keeps;
    a symbolic verdict claiming otherwise must not be enough to discharge.
    """
    truthful = region_module.domain_comparison(
        EAGER_STEP, ON_GRID_POLE_STEP, DEFERRED_ENCODING
    )
    assert truthful.matched is False

    lying = replace(
        truthful,
        equal=True,
        decided=True,
        candidate_extra_exclusions=(),
        candidate_excluded=truthful.baseline_excluded,
    )
    assert lying.matched is True
    monkeypatch.setattr(region_module, "domain_comparison", lambda *args: lying)

    result = discharge(EAGER_STEP, ON_GRID_POLE_STEP, DEFERRED_ENCODING)
    assert result.symbolic_domain_match is True
    assert result.sample_domain_match is False
    assert result.baseline_only_defined_count == 20
    assert result.symbolic_domain_conflict is True
    assert result.domain_match is False
    assert result.discharged is False


def test_an_extra_precondition_the_sample_set_never_violates_still_blocks():
    """The precondition half fails closed for exactly the same reason as the domain half.

    ``Ne(b, 7)`` survives the encode unchanged, so the candidate is admissible
    only away from ``b = 7`` while the baseline is admissible there.  No sample
    point has ``b = 7``, so every sampled number -- including
    ``precondition_check``'s own standalone verdict, which reads
    ``unconditional`` -- says the demand costs nothing.  The symbolic
    composition does not reduce to true, and an undecided admissibility claim is
    not a discharge.
    """
    result = discharge(EAGER_STEP, OFF_GRID_DEMAND_STEP, DEFERRED_ENCODING)
    assert result.symbolic_verdict is True
    assert result.agreement_fraction == 1
    assert result.domain_match is True
    assert result.candidate_precondition_verdict == "unconditional"
    assert result.encoded_precondition_failed_count == 0
    assert result.encoded_precondition_undecided_count == 0
    assert result.encoded_precondition_symbolic is None
    assert result.precondition_admissible is False
    assert result.discharged is False
    assert "symbolic verdict None" in result.reason


# --------------------------------------------------------------------------
# The candidate's own precondition, inside the obligation
# --------------------------------------------------------------------------


def test_the_discharge_record_carries_the_candidate_precondition_verdict():
    """"Conditional, never equivalent" is stated by the model, not by a reader.

    The candidate demands ``Ne(den, 0)`` and the baseline demands nothing of
    ``den``; the encode sets ``den = 1`` and so discharges that demand at every
    encoded point.  All of that is now inside the ``Discharge`` record, so the
    qualifier does not depend on somebody also running ``precondition_check``.
    """
    result = discharge(EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING)
    assert result.candidate_precondition == ("Ne(den, 0)",)
    assert result.candidate_precondition_verdict == "conditional"
    assert result.precondition_qualified is True
    assert result.encoded_precondition_symbolic is True
    assert result.encoded_precondition_failed_count == 0
    assert result.encoded_precondition_undecided_count == 0
    assert result.encoded_precondition_holds_count == 240
    assert result.precondition_admissible is True
    assert result.discharged is True
    assert "conditional and never equivalent" in result.reason

    # The cost-only pair declares nothing, so nothing is qualified.
    plain = discharge(PRODUCT_HOISTED, PRODUCT_SEQUENTIAL, IDENTITY_ENCODING)
    assert plain.candidate_precondition == ()
    assert plain.precondition_qualified is False
    assert "conditional" not in plain.reason


def test_a_precondition_the_encode_does_not_discharge_blocks_the_obligation():
    """The same boundary map, demanding something the encode cannot supply.

    ``Ne(a, 0)`` survives the encode untouched, so the obligation would be
    discharged at 23 encoded points the candidate itself declares inadmissible.
    Every other conjunct passes, which is exactly why this has to be a conjunct.
    """
    result = discharge(EAGER_STEP, DEMANDING_STEP, DEFERRED_ENCODING)
    assert result.symbolic_verdict is True
    assert result.agreement_fraction == 1
    assert result.domain_match is True
    assert result.encoded_precondition_symbolic is None
    assert result.encoded_precondition_failed_count > 0
    assert result.precondition_examples
    assert result.precondition_admissible is False
    assert result.discharged is False
    assert "declares inadmissible" in result.reason


def test_a_precondition_that_misses_the_sample_grid_is_not_called_unsatisfiable():
    """An absolute claim may not come from a 240-point grid.

    ``Eq(b, 7)`` is satisfiable at every point with ``b = 7`` and
    ``VALUE_POOL`` contains no ``7``, so the declared sample set finds nothing.
    That is a fact about the sample set.  ``impossible_step`` is the contrast:
    sympy reduces its precondition to false and the absolute verdict is earned.
    """
    check = precondition_check(OFF_GRID_PRECONDITION_STEP)
    assert check.satisfied_count == 0
    assert check.sample_count == 240
    assert check.symbolically_unsatisfiable is False
    assert check.verdict == "unsatisfied on the sample set"
    assert "not about the region" in check.reason
    assert "not a candidate" not in check.reason
    # And it really is satisfiable: a point off the grid satisfies it.
    assert OFF_GRID_PRECONDITION_STEP.evaluate(
        (Fraction(2), Fraction(3), Fraction(7))
    ) == {"VALUE": Fraction(6)}

    absolute = precondition_check(IMPOSSIBLE_STEP)
    assert absolute.verdict == "unsatisfiable"
    assert absolute.symbolically_unsatisfiable is True

    vacuous = precondition_check(EAGER_STEP, [])
    assert vacuous.verdict == "undetermined"
    assert vacuous.satisfied_fraction is None


def test_the_report_pins_the_definedness_measurement():
    definedness = report()["definedness"]
    assert "7" not in definedness["sample_pool"]
    assert "3" in definedness["sample_pool"]
    assert definedness["matched_pair"]["equal"] is True
    assert definedness["matched_pair"]["baseline_excluded"] == ["b = 0"]

    off_grid = definedness["off_grid_pole"]
    assert off_grid["discharged"] is False
    assert off_grid["agreement_fraction"] == "1/1"
    assert off_grid["baseline_only_defined_count"] == 0
    assert off_grid["candidate_extra_exclusions"] == ["b = 7"]
    assert off_grid["symbolic_domain_conflict"] is True

    on_grid = definedness["on_grid_pole"]
    assert on_grid["discharged"] is False
    assert on_grid["baseline_only_defined_count"] == 20
    assert on_grid["candidate_extra_exclusions"] == ["b = 3"]
    assert on_grid["symbolic_domain_conflict"] is False

    assert (
        report()["precondition"]["off_grid_precondition_step"]["verdict"]
        == "unsatisfied on the sample set"
    )


# --------------------------------------------------------------------------
# The report itself
# --------------------------------------------------------------------------


def test_axis_report_is_deterministic_and_carries_the_headline_numbers():
    first = report()
    second = axis_report()
    assert first == second

    assert first["axis"] == "deferred division on rational values"
    assert first["loop_versus_formula"]["single_step_identical"] is True
    assert first["loop_versus_formula"]["hoisted_loop"]["symbolic_total"] == "n + 1"
    assert first["loop_versus_formula"]["sequential_loop"]["symbolic_total"] == "2*n"
    assert all(entry["discharged"] for entry in first["discharge"])
    assert first["adversarial"]["declared_samples"]["discharged"] is False
    assert first["adversarial"]["declared_samples"]["agreement_fraction"] == "1/1"
    assert first["adversarial"]["declared_samples"]["symbolic_sample_conflict"] is True
    assert first["precondition"]["impossible_step"]["verdict"] == "unsatisfiable"
    assert first["commitment_contrast"]["step_pair"]["control_violated"] == [
        "preserve_inputs",
        "preserve_outputs",
        "map_equality",
    ]
    assert first["commitment_contrast"]["step_pair"]["obligation_discharged"] is True


def test_a_pole_introduced_by_the_encode_itself_is_not_discharged():
    """The encode's own poles must enter the candidate's excluded set (region.py:1075).

    Review's 31-mutant sweep found this line unpinned and proved the gap reachable: with
    ``candidate_side.extend(_negative_power_bases(expression))`` replaced by ``pass``, the
    construction below comes back ``discharged=True`` even though the encode is undefined at
    ``b = 7`` where the baseline is perfectly defined and returns ``1/7``.

    The construction is deliberately built so that nothing else can catch it.  The boundary map
    is unchanged -- ``num/den`` recovers ``v`` exactly, since ``num = v/(b-7)`` and
    ``den = 1/(b-7)`` share the factor -- so the equality half discharges.  The pole sits at
    ``b = 7``, which is outside ``VALUE_POOL``, so the sampled half is blind: 0 baseline-only and
    0 candidate-only admissible points out of 240.  And the candidate declares NO precondition,
    so ``DEFERRED_STEP``'s ``Ne(den, 0)`` cannot mask the gap either.  Only the symbolic
    collection of the encode's divisors rejects it.
    """
    candidate = replace(DEFERRED_STEP, name="deferred_no_precondition", precondition=(), _cache={})
    assert candidate.precondition == ()

    encoding = Encoding(
        name="encode_pole_b7",
        baseline_inputs=("v", "a", "b"),
        candidate_inputs=("num", "den", "a", "b"),
        candidate_outputs=("NUM", "DEN"),
        encode=("v/(b - 7)", "1/(b - 7)", "a", "b"),
        decode=("num/den", "a", "b"),
        output_decode=(("VALUE", "NUM/DEN"),),
    )

    result = discharge(EAGER_STEP, candidate, encoding)
    assert result.discharged is False
    assert result.symbolic_domain_match is False
    assert result.candidate_extra_exclusions == ("b = 7",)
    assert result.symbolic_domain_conflict is True
