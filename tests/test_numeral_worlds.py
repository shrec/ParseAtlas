"""Validation of experiment 0054, the numeral axis: the base a number is written in.

Every expectation here was measured before it was written down, and the ones that carry a headline
are pinned literally rather than recomputed from the module, so a change cannot pass silently.

Three things this file is careful about, because reviews of earlier cards found each of them
missing somewhere:

* **Every predicate is asked in both directions.**  :func:`~parseatlas.numeral_worlds.terminates`
  is asserted to answer ``False`` on hand-worked cases as often as it answers ``True``, and the
  binary64 disagreement counter is asserted to report exactly ``0`` on the stratum where it must.
* **A ranking that changes is pinned BOTH ways.**  The base-blind order and the base-aware order
  are both literal, so a regression in either is a failure rather than a silent agreement.
* **A ranking that does not change is pinned too.**  The 25-world notational ranking is asserted
  identical before and after base-aware arithmetic pricing, with its published 0037 values, so the
  negative result is as load-bearing as the positive one.
"""

from fractions import Fraction

import pytest

from parseatlas.numeral_worlds import (
    BASE_BAND,
    DECIMAL_STRATUM,
    DYADIC_STRATUM,
    PROBE_BASES,
    RANKING_BASES,
    base_digits,
    base_signature,
    blind_terms,
    calibration_case,
    classify_constant,
    constant_corpus,
    corpus_entries_for_cost,
    cost_terms,
    crossing_points,
    disagreement_table,
    entry_cost,
    evaluate_binary64,
    evaluate_exact,
    exactness_table,
    minimal_exact_base,
    montgomery_table,
    numeral_length,
    orientation_by_computation,
    power_headline,
    radical,
    ranking_change_report,
    reversal_curve,
    seam_comparison,
    seam_crossover,
    shift_classification_table,
    shortest_addition_chain,
    should_parallelise,
    signature_classes,
    stratify,
    terminates,
    world_ranking_invariance,
    worker_count_for,
    _pair_differences,
    _ranking_cell,
    _reversals_at,
)
from parseatlas.notational_cost import CONTROL
from parseatlas.parser import parse

# Measured once, then pinned.  These are the numbers the report publishes.
CORPUS_OCCURRENCES = 49
CORPUS_INERT_OCCURRENCES = 27
CORPUS_INFORMATIVE_OCCURRENCES = 22
CORPUS_DISTINCT_INERT = 8
CORPUS_DISTINCT_INFORMATIVE = 6
MINIMAL_EXACT_BASE = 30
BASE_TWO_DISTINCT_EXACT = 1
BASE_TEN_DISTINCT_EXACT = 5
DECIMAL_DISAGREEMENTS = 65
DYADIC_DISAGREEMENTS = 2
SAMPLE_POINTS_PER_STRATUM = 120
CONTROL_WORLD_RANK = 3
CONTROL_WORLD_TOTAL = 45
BEST_WORLD = "G18"
BEST_WORLD_TOTAL = 42


# ------------------------------------------------------------ A. the termination predicate itself


@pytest.mark.parametrize(
    ("value", "base", "expected"),
    [
        # Base 2: halves and quarters terminate, thirds and tenths do not.
        (Fraction(1, 2), 2, True),
        (Fraction(3, 4), 2, True),
        (Fraction(1, 3), 2, False),
        (Fraction(1, 10), 2, False),
        (Fraction(1, 100), 2, False),
        # Base 3: exactly the reverse for halves and thirds.
        (Fraction(1, 3), 3, True),
        (Fraction(4, 9), 3, True),
        (Fraction(1, 2), 3, False),
        (Fraction(1, 10), 3, False),
        # Base 10: halves and tenths terminate, thirds do not.
        (Fraction(1, 2), 10, True),
        (Fraction(1, 10), 10, True),
        (Fraction(1, 100), 10, True),
        (Fraction(1, 3), 10, False),
        (Fraction(1, 6), 10, False),
        # Base 16: the same primes as base 2 and therefore the same answers.
        (Fraction(1, 16), 16, True),
        (Fraction(3, 4), 16, True),
        (Fraction(1, 10), 16, False),
        (Fraction(1, 3), 16, False),
        # Integers terminate everywhere, which is exactly why they are the inert stratum.
        (Fraction(5), 2, True),
        (Fraction(5), 3, True),
        (Fraction(5), 10, True),
        (Fraction(5), 16, True),
    ],
)
def test_the_termination_predicate_matches_the_hand_worked_cases(value, base, expected):
    """The predicate every number in measurement A rests on, checked in both directions.

    Nine of these ``22`` cases expect ``False`` and thirteen expect ``True``.  A predicate only ever
    asked in the direction of its expected answer proves nothing, and this file refuses to add a
    third such case to the project.
    """
    assert terminates(value, base) is expected


def test_the_termination_predicate_answers_no_at_least_as_often_as_yes_here():
    """The negative control, stated as a property of the corpus rather than of a chosen case."""
    values = sorted({c.value for c in constant_corpus() if not c.is_integer})
    answers = [terminates(value, 2) for value in values]
    assert any(answers) is True
    assert not all(answers)
    assert answers.count(False) == 5
    assert answers.count(True) == 1


def test_a_base_below_two_is_rejected_rather_than_silently_answered():
    with pytest.raises(ValueError):
        terminates(Fraction(1, 2), 1)
    with pytest.raises(ValueError):
        base_digits(10, 0)


def test_the_radical_and_the_digits_are_what_they_are_claimed_to_be():
    assert radical(1) == 1
    assert radical(2) == 2
    assert radical(8) == 2
    assert radical(3000000000) == 30
    assert radical(87903691) == 87903691
    assert base_digits(0, 2) == (0,)
    assert base_digits(2**50, 2) == (1,) + (0,) * 50
    assert base_digits(100, 10) == (1, 0, 0)
    assert base_digits(100, 2) == (1, 1, 0, 0, 1, 0, 0)
    assert numeral_length(2**50, 2) == 51
    assert numeral_length(2**50, 10) == 16


# ------------------------------------------------------------------- the null-model stratification


def test_the_null_model_stratification_is_the_measured_one():
    """A constant that terminates in every base ranks no base above another and is reported apart.

    More than half the corpus occurrences are in the inert stratum, so a rate computed over the
    whole corpus would be measuring the integers.  Every rate in the report is inside a stratum for
    this reason, and the split is pinned here so it cannot drift.
    """
    summary = stratify()
    assert summary["occurrences"] == CORPUS_OCCURRENCES
    assert summary["inert_occurrences"] == CORPUS_INERT_OCCURRENCES
    assert summary["informative_occurrences"] == CORPUS_INFORMATIVE_OCCURRENCES
    assert summary["distinct_inert_count"] == CORPUS_DISTINCT_INERT
    assert summary["distinct_informative_count"] == CORPUS_DISTINCT_INFORMATIVE
    assert summary["distinct_inert"] == ("1", "2", "3", "4", "9", "12", "100", "6378137")
    assert summary["distinct_informative"] == (
        "1/100",
        "1/3",
        "1/2",
        "3/5",
        "4/5",
        "298257223563/1000000000",
    )
    assert summary["sources"] == {"0034": 26, "0037": 19, "0051": 4}
    assert summary["roles"]["divisor"] == 19
    assert summary["roles"]["multiplier"] == 19


def test_one_constant_dominates_the_informative_occurrences_and_that_is_disclosed():
    """``1/2`` is 16 of the 22 informative occurrences, which is why both rates are published.

    The occurrence-weighted rate flatters base 2 for one reason only: a single constant it happens
    to represent exactly appears sixteen times.  Reporting only that rate would be reporting the
    corpus's shape as a fact about the base.
    """
    halves = [c for c in constant_corpus() if c.value == Fraction(1, 2)]
    assert len(halves) == 16
    table = exactness_table(workers=1)
    base_two = next(row for row in table["probe"] if row["base"] == 2)
    assert base_two["distinct_exact"] == 1
    assert base_two["of"] == 6
    assert base_two["occurrence_exact"] == 16
    assert base_two["of_occurrences"] == 22


# --------------------------------------------------------------------- A. the exactness sweep


def test_base_two_is_worse_than_base_ten_for_the_projects_own_constants():
    """The card's question A, answered inside the informative stratum."""
    table = exactness_table(workers=1)
    assert table["base_two_vs_base_ten"]["base_2"] == BASE_TWO_DISTINCT_EXACT
    assert table["base_two_vs_base_ten"]["base_10"] == BASE_TEN_DISTINCT_EXACT
    assert table["base_two_vs_base_ten"]["verdict"] == "base 10 is better for this corpus"
    probe = {row["base"]: row for row in table["probe"]}
    assert tuple(probe) == PROBE_BASES
    assert probe[2]["inexact"] == (
        "1/100",
        "1/3",
        "3/5",
        "4/5",
        "298257223563/1000000000",
    )
    assert probe[10]["inexact"] == ("1/3",)
    assert probe[30]["inexact"] == ()
    assert probe[3]["distinct_exact"] == 1
    assert probe[6]["distinct_exact"] == 2
    assert probe[16]["distinct_exact"] == 1
    assert probe[60]["distinct_exact"] == 6


def test_the_wgs84_defining_constant_is_exact_in_base_ten_and_not_in_base_two():
    """The one constant in the corpus that arrives from outside mathematics."""
    inverse_flattening = Fraction(298257223563, 1000000000)
    assert terminates(inverse_flattening, 10) is True
    assert terminates(inverse_flattening, 2) is False
    assert terminates(inverse_flattening, 16) is False
    assert terminates(inverse_flattening, 30) is True
    assert inverse_flattening in {c.value for c in constant_corpus()}


def test_the_minimal_exact_base_is_solved_rather_than_swept():
    """Bound-free: the answer is a radical, and the sweep only confirms it."""
    minimal = minimal_exact_base()
    assert minimal["lcm"] == 3000000000
    assert minimal["minimal_base"] == MINIMAL_EXACT_BASE
    assert minimal["primes"] == (2, 3, 5)
    assert minimal["all_bases"] == "every multiple of 30"
    table = exactness_table(workers=1)
    assert table["first_base_achieving_best"] == MINIMAL_EXACT_BASE
    assert table["best_distinct_exact"] == CORPUS_DISTINCT_INFORMATIVE
    for multiple in (30, 60, 90, 120):
        assert all(terminates(c.value, multiple) for c in constant_corpus())
    for near_miss in (15, 20, 24, 29, 31):
        assert not all(terminates(c.value, near_miss) for c in constant_corpus())


def test_the_class_enumeration_covers_every_base_of_any_size():
    """What was checked beyond the band, stated as an enumeration rather than as a bound."""
    classes = signature_classes()
    assert classes["primes"] == (2, 3, 5)
    assert classes["class_count"] == 8
    assert classes["expected_class_count"] == 8
    assert classes["complete"] is True
    smallest = {row["signature"]: row["smallest_base"] for row in classes["classes"]}
    assert smallest[()] == 7
    assert smallest[(2,)] == 2
    assert smallest[(2, 5)] == 10
    assert smallest[(2, 3, 5)] == 30
    # A base far outside the band behaves exactly as its class representative does.
    by_signature = {row["signature"]: row["distinct_exact"] for row in classes["classes"]}
    for big in (2**20, 10**7, 3**15, 30 * 10**6, 7**9):
        signature = tuple(sorted(base_signature(big, (2, 3, 5))))
        observed = sum(
            1
            for value in sorted({c.value for c in constant_corpus() if not c.is_integer})
            if terminates(value, big)
        )
        assert observed == by_signature[signature]


def test_the_exactness_curve_is_not_monotone_and_depends_only_on_the_radical():
    """More base does not give more exactness; only more primes does."""
    table = exactness_table(workers=1)
    assert table["band"] == (2, 120)
    assert table["band_is_a_computational_limit"] is True
    assert table["monotone"] is False
    assert table["descent_count"] == 43
    assert table["count_depends_only_on_radical"] is True
    rows = {row["base"]: row for row in table["rows"]}
    assert rows[30]["distinct_exact"] == 6
    assert rows[31]["distinct_exact"] == 0
    assert rows[16]["distinct_exact"] == rows[2]["distinct_exact"]


# ------------------------------------------------------------ B. the shift classification


@pytest.mark.parametrize(
    ("constant", "base", "expected"),
    [
        # powers of the base: a shift
        (2, 2, ("shift", 1)),
        (4, 2, ("shift", 1)),
        (1024, 2, ("shift", 1)),
        (9, 3, ("shift", 1)),
        (100, 10, ("shift", 1)),
        (16, 16, ("shift", 1)),
        # sums of distinct powers of the base: shift-and-add
        (3, 2, ("shift_and_add", 2)),
        (5, 2, ("shift_and_add", 2)),
        (12, 2, ("shift_and_add", 2)),
        (100, 2, ("shift_and_add", 3)),
        (4, 3, ("shift_and_add", 2)),
        (17, 16, ("shift_and_add", 2)),
        (110, 10, ("shift_and_add", 2)),
        # neither: a real multiplication
        (3, 10, ("general", 1)),
        (12, 10, ("general", 2)),
        (2, 3, ("general", 1)),
        (100, 3, ("general", 3)),
        (255, 16, ("general", 2)),
        (7, 10, ("general", 1)),
        # the identity, which emits nothing at all
        (1, 2, ("identity", 1)),
        (1, 10, ("identity", 1)),
    ],
)
def test_the_shift_classification_is_pinned_in_all_three_directions(constant, base, expected):
    assert classify_constant(constant, base) == expected


def test_every_positive_integer_is_shift_and_add_in_base_two_and_that_is_the_asymmetry():
    """In base 2 the ``general`` class is empty; in base 10 it is the common case."""
    assert all(
        classify_constant(k, 2)[0] in ("identity", "shift", "shift_and_add")
        for k in range(1, 200)
    )
    assert sum(1 for k in range(2, 200) if classify_constant(k, 10)[0] == "general") == 192


def test_the_classification_of_the_corpus_constants_is_the_measured_one():
    table = shift_classification_table()
    assert table["multipliers"] == (2, 3, 4, 12, 100)
    assert table["divisors"] == (2, 3, 100)
    assert table["counts"][2] == {"identity": 0, "shift": 2, "shift_and_add": 3, "general": 0}
    assert table["counts"][10] == {"identity": 0, "shift": 1, "shift_and_add": 0, "general": 4}
    assert table["counts"][3] == {"identity": 0, "shift": 1, "shift_and_add": 2, "general": 2}
    for base in (6, 16, 30, 60):
        assert table["counts"][base]["shift"] == 0
        assert table["counts"][base]["general"] == 5
    assert table["shift_and_add_widths"] == (2, 3)


@pytest.mark.parametrize(
    ("source", "blind", "base_two", "base_three", "base_ten"),
    [
        ("(a + b) / 2", (1, 0, 1), (2, 0, 0), (1, 0, 1), (1, 0, 1)),
        ("p * x / 100", (0, 1, 1), (0, 1, 1), (0, 1, 1), (1, 1, 0)),
        ("(b - a) / a * 100", (1, 1, 1), (5, 0, 1), (1, 1, 1), (2, 0, 1)),
        ("4 * x * x + 12 * x + 9", (2, 3, 0), (5, 1, 0), (6, 1, 0), (2, 3, 0)),
        ("(2 * x + 3) * (2 * x + 3)", (2, 3, 0), (4, 1, 0), (2, 3, 0), (2, 3, 0)),
    ],
)
def test_the_base_aware_operation_count_is_the_hand_worked_one(
    source, blind, base_two, base_three, base_ten
):
    """A cost of computation, taken on the intended tree, checked term by term."""
    tree = parse(source, CONTROL)
    assert blind_terms(tree).as_tuple() == blind
    assert cost_terms(tree, 2).as_tuple() == base_two
    assert cost_terms(tree, 3).as_tuple() == base_three
    assert cost_terms(tree, 10).as_tuple() == base_ten


# ------------------------------------------- B. the rankings, pinned both before and after


def test_the_corpus_cost_ranking_changes_under_base_aware_pricing_and_is_pinned_both_ways():
    """The ranking that DOES change, with the base-blind order and the base-aware order both pinned.

    At a multiply price of ``3`` with division at twice that, the project's own base-blind cost puts
    ``ohm_series_resistance`` (``r1 + r2 + r3``, two additions) alone at the front.  Pricing a shift
    apart from a multiply puts ``mean_of_two`` (``(a + b) / 2``) level with it, because on a binary
    machine the halving is a shift and not a division.  That single change is the whole card in one
    line, and both sides of it are literal here.
    """
    cell = _ranking_cell((2, 2, "cell"))
    sample = next(row for row in cell["samples"] if row["multiply_price"] == "3")
    assert sample["cheapest_blind"] == "ohm_series_resistance"
    assert sample["cheapest_blind_cost"] == "2"
    assert sample["cheapest_blind_ties"] == 1
    assert sample["cheapest_aware"] == "mean_of_two"
    assert sample["cheapest_aware_cost"] == "2"
    assert sample["cheapest_aware_ties"] == 5
    assert sample["reversals_against_blind"] == 401
    assert cell["pairs"] == 5565
    assert cell["against_blind"]["maximum"] == 515


def test_the_two_source_corpora_overlap_and_the_overlap_can_never_inflate_a_reversal():
    """The `106` written forms hold `90` distinct trees, and the duplicates are inert.

    Sixteen objects appear once under a 0034 name and once under a 0037 name.  A duplicated pair has
    identical costs in every model, so it is never a strict order and can never be counted as a
    reversal; it only enlarges the pair denominator.  The report discloses this instead of
    deduplicating, and this test is what makes the disclosure checkable.
    """
    entries = corpus_entries_for_cost()
    trees = [str(entry.tree) for entry in entries]
    assert len(entries) == 106
    assert len({entry.name for entry in entries}) == 106
    assert len(set(trees)) == 90
    assert sum(1 for tree in set(trees) if trees.count(tree) > 1) == 16
    names = [entry.name for entry in entries]
    aware = {entry.name: cost_terms(entry.tree, 2) for entry in entries}
    blind = {entry.name: blind_terms(entry.tree) for entry in entries}
    by_tree = {}
    for entry in entries:
        by_tree.setdefault(str(entry.tree), []).append(entry.name)
    for shared in (group for group in by_tree.values() if len(group) > 1):
        first, second = shared[0], shared[1]
        assert aware[first] == aware[second]
        assert blind[first] == blind[second]
    differences = _pair_differences(names, blind, aware, 2)
    identical = sum(1 for before, after in differences if before == (0, 0) and after == (0, 0))
    assert identical >= 16
    for price in (Fraction(1), Fraction(3), Fraction(8)):
        assert _reversals_at(
            tuple(pair for pair in differences if pair[0] == (0, 0) and pair[1] == (0, 0)), price
        ) == 0


def test_the_reversal_curve_is_exact_over_the_whole_price_ray_and_saturates():
    """No grid and no upper bound: the curve is solved, and its last segment runs to infinity."""
    cell = _ranking_cell((2, 2, "cell"))
    curve = cell["against_blind"]["curve"]
    assert curve[0]["from"] == "1"
    assert curve[-1]["to"] == "infinity"
    assert curve[-1]["reversals"] == 515
    assert cell["crossings"]["ranking_constant_above"] == "6"
    assert cell["crossings"]["crossing_count"] == 13
    assert cell["crossings"]["pairs_examined"] == 5565


def test_the_reversal_curve_has_a_turning_point_where_more_price_gives_fewer_reversals():
    """The non-monotonicity the roadmap asks every card to look for, named with its value."""
    cell = _ranking_cell((2, 2, "cell"))
    assert cell["against_blind"]["monotone"] is False
    descents = cell["against_blind"]["descents"]
    assert descents == (
        {"at": "5/4", "from": 316, "to": 315},
        {"at": "4/3", "from": 315, "to": 308},
    )
    assert cell["against_blind"]["minimum"] == 308


def test_the_bases_where_the_projects_base_blind_cost_is_already_right():
    """A negative result with an exact scope: for six bases the base-aware cost is the blind one."""
    for base in (5, 6, 8, 16, 30, 60):
        cell = _ranking_cell((base, 2, "cell"))
        assert cell["against_blind"]["maximum"] == 0
        assert cell["against_blind"]["curve"] == ()
        assert cell["against_blind"]["segments"] == 0
    # The published table, pinned row by row: maximum reversals, curve segments, and the price
    # above which the count never changes again.
    published = {
        2: (515, 13, "6", False),
        3: (117, 11, "6", False),
        4: (19, 3, "3", True),
        10: (58, 5, "5", True),
        12: (19, 3, "3", True),
    }
    for base, (maximum, segments, last_from, monotone) in published.items():
        summary = _ranking_cell((base, 2, "cell"))["against_blind"]
        assert summary["maximum"] == maximum
        assert summary["segments"] == segments
        assert summary["curve"][-1]["from"] == last_from
        assert summary["curve"][-1]["to"] == "infinity"
        assert summary["monotone"] is monotone
    # Bases 4 and 12 have no reversal at all below multiply price 3/2.
    for base in (4, 12):
        assert _ranking_cell((base, 2, "cell"))["against_blind"]["curve"][0]["from"] == "3/2"


def test_the_twenty_five_world_notational_ranking_does_not_move_and_is_pinned_both_ways():
    """The ranking that does NOT change, stated as plainly as the one that does.

    Direction B fixes the intended tree, so the multiset of literals is the same in all 25 worlds
    and a base-aware arithmetic price is the same additive constant in every column.  A cost of
    notation and a cost of computation are separate orderings of the same objects.  The published
    0037 values are asserted on the "before" side so that this test also guards the import.
    """
    invariance = world_ranking_invariance()
    assert invariance["worlds"] == 25
    assert invariance["entries"] == 48
    assert invariance["best_world"] == BEST_WORLD
    assert invariance["best_total"] == BEST_WORLD_TOTAL
    assert invariance["control_rank"] == CONTROL_WORLD_RANK
    assert invariance["control_total"] == CONTROL_WORLD_TOTAL
    assert invariance["before_order"][:4] == ("G18", "G16", "G0", "G10")
    assert invariance["order_unchanged"] is True
    assert invariance["after_order"][2] == invariance["before_order"]
    assert invariance["after_order"][10] == invariance["before_order"]


def test_exactly_one_law_has_its_cheaper_side_decided_by_the_base():
    """The orientation question, asked of the emitted graph instead of the brackets."""
    orientation = orientation_by_computation()
    assert orientation["laws"] == 15
    assert orientation["flip_count"] == 1
    assert orientation["laws_whose_cheap_side_the_base_decides"] == ("perfect_square_trinomial",)
    row = next(r for r in orientation["rows"] if r["law"] == "perfect_square_trinomial")
    assert row["base_2"] == ("factored", "factored", "factored")
    assert row["base_3"] == ("factored", "expanded", "expanded")
    assert row["base_10"] == ("tie", "tie", "tie")
    assert row["base_16"] == ("tie", "tie", "tie")


def test_the_crossing_enumeration_is_complete_and_the_ranking_is_constant_above_it():
    """Above the largest crossing nothing can change again, because every cost is affine."""
    entries = corpus_entries_for_cost()
    crossings = crossing_points(entries, base=2, divide_ratio=2)
    assert crossings["crossings"][0] == "1"
    assert crossings["largest"] == "6"
    names = [entry.name for entry in entries]
    aware = {entry.name: cost_terms(entry.tree, 2) for entry in entries}
    blind = {entry.name: blind_terms(entry.tree) for entry in entries}
    differences = _pair_differences(names, blind, aware, 2)
    curve = reversal_curve(differences)
    assert curve[-1]["reversals"] == 515
    for price in (Fraction(7), Fraction(100), Fraction(10**6)):
        scored = {
            name: entry_cost(aware[name], price, 2) for name in names
        }
        order = sorted(names, key=lambda name: (scored[name], name))
        reference = {name: entry_cost(aware[name], Fraction(10**9), 2) for name in names}
        assert order == sorted(names, key=lambda name: (reference[name], name))


# ------------------------------------------------------- C. exact rationals against binary64


def test_the_calibration_case_is_the_one_everybody_knows():
    """``0.1 + 0.2 != 0.3`` in binary64 and ``==`` over exact rationals."""
    case = calibration_case()
    assert case["exact_equal"] is True
    assert case["exact_left"] == "3/10"
    assert case["exact_right"] == "3/10"
    assert case["float_equal"] is False
    assert case["float_left"] == 0.30000000000000004
    assert case["float_right"] == 0.3
    assert case["one_tenth_is_exact_in_base_10"] is True
    assert case["one_tenth_is_exact_in_base_2"] is False
    assert case["accurate_side"] == "the exact rationals"
    # Stated directly as well, so the assertion does not depend on the module's own record.
    assert Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10)
    assert 0.1 + 0.2 != 0.3


def test_the_disagreement_count_is_a_property_of_the_inputs_base():
    """Same pairs, same algebra, two strata of inputs, and a factor of more than thirty between."""
    table = disagreement_table(workers=1)
    assert table["laws"] == 15
    assert table["summary"]["dyadic"]["checked"] == SAMPLE_POINTS_PER_STRATUM
    assert table["summary"]["decimal"]["checked"] == SAMPLE_POINTS_PER_STRATUM
    assert table["summary"]["dyadic"]["disagreements"] == DYADIC_DISAGREEMENTS
    assert table["summary"]["decimal"]["disagreements"] == DECIMAL_DISAGREEMENTS
    assert table["summary"]["dyadic"]["laws_with_a_disagreement"] == 2
    assert table["summary"]["decimal"]["laws_with_a_disagreement"] == 14
    assert table["summary"]["dyadic"]["algebra_failures"] == 0
    assert table["summary"]["decimal"]["algebra_failures"] == 0
    assert table["summary"]["decimal"]["worst_relative"] == pytest.approx(7.062802723619858e-15)
    assert table["summary"]["dyadic"]["worst_relative"] == pytest.approx(1.7377403863698103e-16)


def test_the_disagreement_counter_can_report_zero():
    """The negative control the card demands, on the stratum where zero is the correct answer.

    Dyadic inputs, no division: every literal and every intermediate is a binary64 number exactly,
    so no rounding can occur and the counter must return ``0``.  Ninety-six points is not a small
    sample for a counter that returns ``52`` on the same laws with decimal inputs.
    """
    table = disagreement_table(workers=1)
    control = table["negative_control"]
    assert control["stratum"] == "dyadic"
    assert control["checked"] == 96
    assert control["disagreements"] == 0
    assert control["counter_can_report_zero"] is True
    assert table["summary"]["decimal"]["division_free_checked"] == 96
    assert table["summary"]["decimal"]["division_free_disagreements"] == 52


def test_every_sample_value_belongs_to_the_stratum_it_claims():
    """The strata are what they say they are, which is the whole basis of the comparison."""
    for value in DYADIC_STRATUM:
        assert terminates(value, 2) is True
        assert float(value) == value
    for value in DECIMAL_STRATUM:
        assert terminates(value, 10) is True
        assert terminates(value, 2) is False
        assert Fraction(float(value)) != value


def test_which_writing_is_the_accurate_one_is_a_per_law_answer_and_not_a_rule():
    """"They differ" is not a result.  This says which one is right, and refuses to over-generalise."""
    table = disagreement_table(workers=1)
    accuracy = table["accuracy"]
    assert accuracy["decided_count"] == 8
    assert accuracy["split_count"] == 8
    assert accuracy["one_side_always_wins"] is False
    decided = {(row["law"], row["stratum"]): row["accurate_writing"] for row in accuracy["decided"]}
    assert decided[("difference_of_cubes", "decimal")] == "factored"
    assert decided[("binomial_square", "decimal")] == "expanded"
    assert decided[("line", "decimal")] == "point_slope"
    assert decided[("quotient_rule", "dyadic")] == "closed"
    assert accuracy["winning_roles"]["factored"] == 1
    assert accuracy["winning_roles"]["expanded"] == 2


def test_the_exact_side_is_the_authority_and_the_evaluators_agree_where_they_can():
    """Exact rational evaluation is the reference; binary64 is what is being measured against it."""
    tree = parse("(a + b) * (a + b)", CONTROL)
    dyadic = {"a": Fraction(1, 2), "b": Fraction(1, 4)}
    assert evaluate_exact(tree, dyadic) == Fraction(9, 16)
    assert evaluate_binary64(tree, dyadic) == 0.5625
    decimal = {"a": Fraction(1, 10), "b": Fraction(2, 10)}
    assert evaluate_exact(tree, decimal) == Fraction(9, 100)
    assert evaluate_binary64(tree, decimal) != 0.09


# ------------------------------------------------- D. the seam, and the founding question


def test_the_founding_question_for_this_axis_is_answered_as_an_operation_count():
    """``2 ** 50``: no multiplication at all in base 2, and a seven-step chain in base 10."""
    headline = power_headline()
    assert headline["value"] == 1125899906842624
    assert headline["cost_label"] == "computation"
    assert headline["multiplications_binary"] == 0
    assert headline["multiplications_decimal"] == 7
    assert headline["binary"]["nonzero_digits"] == 1
    assert headline["binary"]["digits"] == 51
    assert headline["decimal"]["nonzero_digits"] == 15
    assert headline["decimal"]["digits"] == 16
    assert headline["bases_where_it_is_free"] == (2, 4, 8, 16, 32, 64)
    assert headline["free_bases_are_powers_of_two"] is True
    assert headline["addition_chain"]["chain"] == (1, 2, 4, 8, 16, 32, 48, 50)


@pytest.mark.parametrize(
    ("target", "length"),
    [(1, 0), (2, 1), (3, 2), (4, 2), (7, 4), (15, 5), (31, 7), (50, 7)],
)
def test_the_addition_chain_search_is_exhaustive_and_therefore_minimal(target, length):
    result = shortest_addition_chain(target)
    assert result["length"] == length
    assert result["chain"][0] == 1
    assert result["chain"][-1] == target
    assert len(result["chain"]) == length + 1


def test_a_seam_with_no_saving_has_no_crossover_at_any_chain_length():
    """The predicate answering NO, which is where the Montgomery claim actually stops."""
    assert seam_crossover(Fraction(0), Fraction(5))["pays_at_any_n"] is False
    assert seam_crossover(Fraction(0), Fraction(5))["crossover"] is None
    assert seam_crossover(Fraction(-1), Fraction(5))["pays_at_any_n"] is False
    assert seam_crossover(Fraction(1), Fraction(5))["crossover"] == "5"


def test_the_montgomery_model_has_a_crossover_and_it_is_a_ratio():
    table = montgomery_table()
    rows = {row["reduction_price"]: row for row in table["rows"]}
    assert rows[1]["pays_at_any_n"] is False
    assert rows[2]["crossover"] == "5"
    assert rows[2]["smallest_integer_n_that_pays"] == 6
    assert rows[4]["crossover"] == "5/3"
    assert rows[6]["crossover"] == "1"
    assert rows[8]["smallest_integer_n_that_pays"] == 1
    assert table["never_pays_below_or_at"] == 1
    assert table["smallest_price_that_ever_pays"] == 2
    assert table["price_at_which_one_operation_per_crossing_pays"] == 8
    assert rows[6]["asymptotic_ratio"] == "7/2"
    assert all(row["crossover_unchanged"] for row in table["word_level"])
    assert table["word_level"][-1]["toll_word_operations"] == 20480


def test_the_two_seams_share_an_algebra_and_differ_in_whether_n_is_free():
    """0042's break-even reproduces from its own published figures, and cannot be reached."""
    comparison = seam_comparison()
    rows = {row["seam"]: row for row in comparison["rows"]}
    assert rows["montgomery_form"]["crossover"] == "1"
    assert rows["cartesian_to_polar"]["crossover"] == "4/3"
    assert rows["fragment_routing_model_ii"]["crossover"] == "29/11"
    assert rows["fragment_routing_model_ii"]["reachable"] is False
    assert rows["montgomery_form"]["reachable"] is True
    assert comparison["routing_break_even_naming_price"] == "11/29"
    assert float(Fraction(11, 29)) == pytest.approx(0.3793103448275862)
    assert comparison["routing_operations_per_crossing"] == 1
    assert comparison["seams_behave_the_same"] is False


# ---------------------------------------------------------------------------- concurrency


def test_the_worker_count_comes_from_the_observed_core_count():
    assert worker_count_for(16, 1000) == 12
    assert worker_count_for(4, 1000) == 2
    assert worker_count_for(1, 1000) == 1
    assert worker_count_for(16, 3) == 3


def test_the_parallel_decision_is_taken_from_measured_costs_and_not_from_a_cell_count():
    """The two sweeps with the same order of magnitude of cells take opposite decisions."""
    assert should_parallelise(len(BASE_BAND), 7.0e-06, 12) is False
    assert should_parallelise(len(RANKING_BASES) * 3, 0.10, 12) is True
    assert should_parallelise(10**6, 0.10, 1) is False
    assert should_parallelise(1, 10.0, 12) is False


def test_sequential_and_parallel_produce_identical_records():
    """Parallelism changes only how fast, never what is measured."""
    assert exactness_table(workers=1)["rows"] == exactness_table(workers=2)["rows"]
    assert disagreement_table(workers=1)["rows"] == disagreement_table(workers=2)["rows"]
    sequential = ranking_change_report(bases=(2, 10), ratios=(2,), workers=1)
    parallel = ranking_change_report(bases=(2, 10), ratios=(2,), workers=2)
    assert sequential["cells"] == parallel["cells"]
    assert sequential["base_against_reference"] == parallel["base_against_reference"]
