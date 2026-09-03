"""Tests for experiment 0036: sine in the twenty-five worlds.

The load-bearing assertions here are the pinned *sets*, not the pinned counts.  A count can be
right by accident when two worlds swap sides; naming the grammars cannot.

Two tests exist because a measurement in this module was wrong before they were written:

* :func:`test_the_domain_slot_is_a_function_of_the_value_not_of_the_process` pins the fix for the
  set-printing instability described in :func:`parseatlas.trigonometry_worlds._set_text`;
* :func:`test_the_sequential_and_parallel_paths_agree` is what exposed it, because the defect is
  invisible until the same work runs in two processes.
"""

import os
import subprocess
import sys

from sympy import Symbol, cos, simplify, sin, sympify

from parseatlas.functions import analyze_outer_functions
from parseatlas.trigonometry_worlds import (
    CONTROL_ID,
    GRAMMARS,
    IDENTITIES,
    IDENTITY_CELL_SECONDS,
    OUTER_ROW_SECONDS,
    SERIES_CELL_SECONDS,
    SERIES_SOURCE,
    _set_text,
    identity_atlas,
    outer_atlas,
    series_atlas,
    should_parallelise,
    worker_count_for,
)

FOUNDING_SOURCE = "2*t + 1 - t/2"

#: The thirteen worlds in which ``s*s + c*c`` still denotes ``sin(x)**2 + cos(x)**2``.
PYTHAGOREAN_WORLDS = [
    "G0",
    "G09",
    "G10",
    "G12",
    "G13",
    "G14",
    "G15",
    "G16",
    "G17",
    "G18",
    "G22",
    "G23",
    "G24",
]

#: The four worlds experiment 0002 found reading ``2*t + 1 - t/2`` as the constant ``1``.
FOUNDING_CONSTANT_WORLDS = ["G01", "G02", "G07", "G08"]


# --------------------------------------------------------------------------------- route 1: series


def test_the_series_is_odd_in_the_conventional_world_and_the_odd_count_is_pinned():
    """Sine is odd; the truncated series is odd in ``G0`` and in eighteen other worlds.

    Two counts are pinned because they are two different questions.  ``odd_as_value`` asks whether
    the expression satisfies ``f(-x) == -f(x)``; ``odd_as_partial_function`` additionally requires
    the domain to be symmetric, and six worlds fail it -- they read the series as the constant zero
    but carry a validity restriction at ``-6`` (or at a fifth root of ``-6``) with no matching
    restriction at ``+6``.  Reporting only the first number would call a function odd on a domain
    that is not closed under negation.
    """
    atlas = series_atlas()
    control = next(row for row in atlas["readings"] if row["grammar"] == CONTROL_ID)

    assert control["canonical"] == "x**5/120 - x**3/6 + x"
    assert control["odd_as_value"] is True
    assert control["odd_as_partial_function"] is True
    assert control["domain_symmetric"] is True

    assert atlas["odd_as_value_count"] == 19
    assert atlas["odd_as_partial_function_count"] == 13
    assert sorted(row["grammar"] for row in atlas["readings"] if row["odd_as_partial_function"]) == [
        "G0",
        "G10",
        "G11",
        "G12",
        "G16",
        "G17",
        "G18",
        "G19",
        "G20",
        "G21",
        "G22",
        "G23",
        "G24",
    ]


def test_the_truncated_series_is_not_periodic_in_any_world_including_the_conventional_one():
    """A truncated series is a polynomial everywhere, and a polynomial has no period anywhere.

    The claim is measured, not assumed: every reading's ``sympy_periodicity`` is either ``None``
    (no period) or the constant sentinel ``0``, and the nine worlds that read the series as the
    constant zero are the only ones that return the sentinel.  ``G0`` is included in the assertion
    on purpose -- the conventional world's reading is exactly as aperiodic as the others.
    """
    atlas = series_atlas()
    assert atlas["periodic_count"] == 0
    assert all(row["is_periodic"] is False for row in atlas["readings"])

    sentinel = {row["grammar"] for row in atlas["readings"] if row["sympy_periodicity"] == "0"}
    assert sentinel == set(atlas["constant_zero_grammars"])
    assert sorted(sentinel) == ["G01", "G02", "G05", "G07", "G08", "G09", "G11", "G19", "G21"]

    assert all(row["is_polynomial"] or row["denominator_degree"] > 0 for row in atlas["readings"])


def test_the_conventional_world_gets_no_discount_on_truncation_error():
    """``G0``'s reading is the true truncated series, and the truncated series is not sine.

    The point of the assertion is the direction of the inequality at the far sample points: the
    conventional reading's error there is enormous, so no table in the report may present ``G0`` as
    if the series route recovered sine.
    """
    atlas = series_atlas()
    control = next(row for row in atlas["readings"] if row["grammar"] == CONTROL_ID)
    samples = {row["point"]: row for row in control["samples"]}

    assert samples["pi/6"]["absolute_error"] < 1e-3
    assert samples["pi"]["absolute_error"] > 0.5
    assert samples["10"]["absolute_error"] > 600
    assert control["max_absolute_error"] == atlas["control_max_absolute_error"]
    assert control["unbounded_on_reals"] is True


def test_the_series_readings_are_grouped_by_the_project_semantic_key():
    """Fourteen semantic classes over eleven distinct canonical values.

    The gap is the whole reason the key is a triple.  Four classes denote the *same* function --
    the constant zero -- and differ only in the validity restrictions their parse trees carry, so
    grouping by canonical text alone would report eleven classes and lose three distinctions that
    the project's own domain discipline says are real -- four classes collapsing into one loses
    three, and 14 - 11 = 3 confirms it.  (An earlier revision of this docstring said four; the
    assertions below were always correct, only the prose count was wrong.)
    """
    atlas = series_atlas()
    assert atlas["distinct_semantic_classes"] == 14
    assert atlas["distinct_canonical_values"] == 11

    zero_classes = [item for item in atlas["classes"] if item["canonical"] == "0"]
    assert len(zero_classes) == 4
    assert sorted(len(item["excluded_points"]) for item in zero_classes) == [0, 1, 2, 4]
    assert sum(len(item["grammars"]) for item in atlas["classes"]) == len(GRAMMARS)


# ----------------------------------------------------------------------------- route 3: identities


def test_the_pythagorean_identity_holds_in_the_conventional_world_and_in_twelve_others():
    """``s*s + c*c`` still denotes ``1`` in thirteen of the twenty-five worlds.

    The surviving set is exactly the worlds in which ``*`` binds tighter than ``+``; the other
    twelve read the string as ``s*(s + c)*c`` and denote a wave rather than a constant.
    """
    atlas = identity_atlas(["pythagorean"])
    rows = {row["grammar"]: row for row in atlas["readings"]}

    control = rows[CONTROL_ID]
    assert control["canonical"] == "c**2 + s**2"
    assert control["substituted"] == "1"
    assert control["holds"] is True

    record = atlas["per_identity"][0]
    assert record["holds_in"] == PYTHAGOREAN_WORLDS
    assert record["holds_count"] == 13
    assert record["semantic_classes"] == 2

    dissenting = next(item for item in record["classes"] if not item["holds"])
    assert dissenting["canonical"] == "c*s*(c + s)"
    assert len(dissenting["grammars"]) == 12
    assert set(dissenting["grammars"]).isdisjoint(PYTHAGOREAN_WORLDS)


def test_the_conventional_world_ties_for_the_most_surviving_identities():
    """``G0`` keeps all eight, and so do ``G23`` and ``G24``; it is best but not uniquely best.

    ``G17`` is the assertion worth reading twice.  It is ``G0``'s ordering made strict -- the same
    four operators in the same order, with ``*`` and ``/`` on separate levels instead of one -- and
    it loses ``1 + s/c*s/c``.  So what saves that identity in our world is not the precedence
    *order* at all, it is the tie that puts ``*`` and ``/`` on one level and makes the chain
    left-associative.
    """
    atlas = identity_atlas()
    assert atlas["best_count"] == len(IDENTITIES) == 8
    assert atlas["best_grammars"] == ["G0", "G23", "G24"]
    assert atlas["control_count"] == 8
    assert atlas["survival"]["G17"]["count"] == 7
    assert "pythagorean_tangent" not in atlas["survival"]["G17"]["kept"]
    assert atlas["convention_free_identities"] == ["double_angle_sine", "tangent"]

    per_identity = {item["identity"]: item for item in atlas["per_identity"]}
    assert per_identity["double_angle_sine"]["holds_count"] == 25
    assert per_identity["tangent"]["holds_count"] == 25
    assert per_identity["pythagorean_tangent"]["holds_in"] == ["G0", "G12", "G22", "G23", "G24"]
    assert per_identity["cofunction_zero"]["holds_count"] == 9


def test_every_identity_reading_is_what_substituting_the_placeholders_actually_gives():
    """The survival verdict is recomputed here from the parse, independently of the atlas."""
    angle = Symbol("x", real=True)
    substitution = {Symbol("s", real=True): sin(angle), Symbol("c", real=True): cos(angle)}
    atlas = identity_atlas(["pythagorean", "double_angle_cosine"])
    for row in atlas["readings"]:
        denoted = sympify(row["canonical"], locals={"s": Symbol("s", real=True), "c": Symbol("c", real=True)})
        target = sympify(row["target"], locals={"x": angle})
        assert row["holds"] is bool(simplify(denoted.subs(substitution) - target) == 0)


# ------------------------------------------------------------------------- route 2: outer function


def test_the_outer_route_reproduces_the_0002_result_for_the_founding_inner_string():
    """Experiment 0002's numbers, reached through this module's pipeline.

    0002 reported eight distinct canonical forms per outer-function family over the founding token
    sequence, and four worlds whose inner argument collapses to the constant ``1``.  Both are
    re-measured here rather than cited.
    """
    atlas = outer_atlas((FOUNDING_SOURCE,), ("sin",))
    sine = atlas["per_source"][0]["functions"]["sin"]

    assert sine["inner_classes"] == 8
    assert sine["semantic_classes"] == 8
    assert sine["constant_argument_grammars"] == FOUNDING_CONSTANT_WORLDS
    assert len(sine["constant_argument_grammars"]) == 4

    rows = {row["grammar"]: row for row in sine["rows"]}
    assert rows["G01"]["canonical"] == "sin(1)"
    assert rows["G01"]["inner"] == "1"
    assert rows["G01"]["is_periodic"] is False
    assert rows[CONTROL_ID]["inner"] == "3*t/2 + 1"
    assert rows[CONTROL_ID]["frequency"] == "3/2"
    assert rows[CONTROL_ID]["declared_period"] == "4*pi/3"
    assert rows["G03"]["declared_period"] == "4*pi"


def test_sine_and_cosine_keep_period_two_pi_over_a_and_tangent_keeps_pi_over_a():
    """The existing pinned relation, re-measured against an independent SymPy periodicity.

    ``tests/test_outer_functions.py::test_sine_reports_constant_collapse_and_period`` pins the
    declared figures; this test additionally requires SymPy's own
    :func:`~sympy.calculus.util.periodicity` to agree with them on every non-constant reading, so a
    declared period that drifted away from the composition it describes would fail here.
    """
    atlas = outer_atlas((FOUNDING_SOURCE,), ("sin", "cos", "tan"))
    functions = atlas["per_source"][0]["functions"]

    assert atlas["period_disagreements"] == []

    sine = {row["grammar"]: row for row in functions["sin"]["rows"]}
    cosine = {row["grammar"]: row for row in functions["cos"]["rows"]}
    tangent = {row["grammar"]: row for row in functions["tan"]["rows"]}

    assert sine["G03"]["frequency"] == cosine["G03"]["frequency"] == tangent["G03"]["frequency"] == "1/2"
    assert sine["G03"]["declared_period"] == "4*pi"
    assert cosine["G03"]["declared_period"] == "4*pi"
    assert tangent["G03"]["declared_period"] == "2*pi"

    assert sine[CONTROL_ID]["declared_period"] == "4*pi/3"
    assert tangent[CONTROL_ID]["declared_period"] == "2*pi/3"
    assert sine["G05"]["declared_period"] == "2*pi"
    assert tangent["G05"]["declared_period"] == "pi"

    # The existing test in tests/test_outer_functions.py must keep passing unchanged.
    report = analyze_outer_functions(FOUNDING_SOURCE, ("tan",))
    assert next(item for item in report["results"] if item["grammar"] == "G03")["properties"]["period"] == "2*pi"


def test_a_quadratic_argument_is_not_a_wave_in_any_world():
    """``sin`` of a non-affine argument has no period, so no world may be told it has one.

    ``t*t - 3*t + 2`` is quadratic under every grammar, so this is the case where the periodicity
    guard has to hold for all twenty-five readings at once.
    """
    atlas = outer_atlas(("t*t - 3*t + 2",), ("sin",))
    sine = atlas["per_source"][0]["functions"]["sin"]
    assert sine["wave_grammars"] == []
    assert len(sine["non_wave_grammars"]) == len(GRAMMARS)
    assert all(row["declared_period"] is None for row in sine["rows"])
    assert all(row["constant_argument"] is False for row in sine["rows"])


def test_the_constant_collapse_count_moves_with_the_inner_string():
    """How often "sine of this" is a fixed number rather than a wave is a property of the string."""
    atlas = outer_atlas(("t/2 + 1 - 2*t", "1 - 2*t/4 + 3*t", "3*t - 2 + 1"), ("sin",))
    collapsed = {
        bucket["source"]: bucket["functions"]["sin"]["constant_argument_grammars"]
        for bucket in atlas["per_source"]
    }
    assert collapsed["t/2 + 1 - 2*t"] == ["G01", "G07"]
    assert collapsed["1 - 2*t/4 + 3*t"] == ["G01", "G04", "G07"]
    assert collapsed["3*t - 2 + 1"] == []


# ------------------------------------------------------------------------------------ concurrency


def test_the_sequential_and_parallel_paths_agree():
    """Parallelism changes only how fast, never what is measured.

    This is the test that found the set-printing defect: the two paths disagreed on the ``domain``
    slot of eight readings of ``1 + s/c*s/c``, because a pool worker is a different process with a
    different string hash seed and SymPy prints a ``Union`` in hash order.
    """
    names = ["pythagorean", "pythagorean_tangent"]
    assert identity_atlas(names, workers=1)["readings"] == identity_atlas(names, workers=4)["readings"]

    subset = ["G0", "G03", "G09", "G13", "G17", "G20", "G22", "G24"]
    assert series_atlas(subset, workers=1) == series_atlas(subset, workers=4)
    assert outer_atlas((FOUNDING_SOURCE,), ("tan",), subset, workers=1) == outer_atlas((FOUNDING_SOURCE,), ("tan",), subset, workers=4)


def test_the_parallel_decision_is_taken_from_the_measured_costs():
    """Cell count alone does not decide it; the measured per-cell cost does.

    The series atlas runs sequentially at 25 cells while the identity atlas runs across a pool at
    200, and no cell-count threshold placed between them would survive a change in per-cell cost:
    what actually decides it is that 25 cells at 0.14 s is less work than a pool costs to raise.
    Pinning both sides of that comparison is what stops the rule from quietly becoming "parallel if
    there are enough cells".
    """
    assert should_parallelise(25, SERIES_CELL_SECONDS, 12) is False
    assert should_parallelise(200, IDENTITY_CELL_SECONDS, 12) is True
    assert should_parallelise(375, OUTER_ROW_SECONDS, 12) is True
    assert should_parallelise(1000, IDENTITY_CELL_SECONDS, 1) is False
    assert should_parallelise(1, IDENTITY_CELL_SECONDS, 12) is False


def test_the_domain_slot_is_a_function_of_the_value_not_of_the_process():
    """A set must render identically in interpreters that hash strings differently.

    ``Union`` holds its members in an order derived from object hashes, and CPython randomises
    string hashing per process, so ``str(continuous_domain(...))`` of the tangent-like domain below
    genuinely comes out in different member orders under different ``PYTHONHASHSEED`` values.  A
    semantic key built on that string would be a function of the process rather than of the value.

    Forcing the seed is what makes the check deterministic; asserting it in one process cannot work,
    because ``Union`` canonicalises its arguments on construction, so two orderings of the *same*
    members collapse to one object before ``str`` ever sees them.
    """
    script = (
        "from sympy import S, Symbol, cos, sin\n"
        "from sympy.calculus.util import continuous_domain\n"
        "from parseatlas.trigonometry_worlds import _set_text\n"
        "x = Symbol('x', real=True)\n"
        "for expression in [(1 + 1/sin(x))/cos(x)**2, sin(x)/cos(x), (1 - x**2)/(120*x**3*(x + 6))]:\n"
        "    print(_set_text(continuous_domain(expression, x, S.Reals)))\n"
    )
    renderings = set()
    for seed in ("0", "1", "12345"):
        completed = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONHASHSEED": seed},
            check=True,
        )
        renderings.add(completed.stdout)
    assert len(renderings) == 1, "the canonical rendering moved with the interpreter's hash seed"

    from sympy import Interval, S, Union

    intervals = [Interval.open(-S.Infinity, -6), Interval.open(-6, 0), Interval.open(0, S.Infinity)]
    assert _set_text(Union(*intervals)) == "Union(Interval.open(-oo, -6), Interval.open(-6, 0), Interval.open(0, oo))"


def test_worker_count_is_derived_from_the_observed_core_count():
    """Never a hardcoded constant, always headroom, never more workers than cells."""
    assert worker_count_for(16, 200) == 12
    assert worker_count_for(4, 200) == 2
    assert worker_count_for(1, 200) == 1
    assert worker_count_for(16, 3) == 3
    assert worker_count_for(16, 0) == 1


def test_the_series_source_is_the_standard_truncation():
    """The datum of route 1, spelled out so a silent edit to it fails a test."""
    assert SERIES_SOURCE == "x - x*x*x/6 + x*x*x*x*x/120"
    assert [item.name for item in IDENTITIES][:2] == ["pythagorean", "cofunction_zero"]
