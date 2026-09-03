"""Experiment 0036: what IS the sine function in each of the twenty-five worlds?

Experiment 0035 asks the same question of the algebraic objects.  This module asks it of
trigonometry, and trigonometry is the harder case for one reason: **sine is not defined once.**
Mathematics characterises it by at least three different written forms, and a written form is
exactly the thing that reads differently under a different precedence convention.  So the three
characterisations that agree in our world need not agree anywhere else, and the *divergence
between the routes* is the measurement this experiment exists to take.

The three routes
----------------

.. code-block:: text

    route 1   the series      "x - x*x*x/6 + x*x*x*x*x/120"   -> what polynomial is that here?
    route 2   the composition sin(<inner token string>)       -> what wave is that here?
    route 3   the identities  "s*s + c*c"  with s,c formal    -> is that still 1 here?

Route 1 reads the truncated Maclaurin series as a token string.  Route 2 is experiment 0002's
question, sharpened: fix an *inner* token string, let each world read it, and apply a real ``sin``
to whatever it denotes -- so the outer function is genuinely ``sin`` in every world and only its
argument moves.  Route 3 is the one that carries the headline.

Why route 3 uses placeholders, and what that models
---------------------------------------------------

The Generation 1 language has no function-call syntax: ``sin(x)`` cannot be tokenised as an
application, only as the variable ``sin`` multiplied by nothing.  The Pythagorean identity is
nevertheless a *written string*, and its convention-sensitivity lives entirely at the
argument level -- in how ``s*s + c*c`` associates, not in what ``sin`` means.  So this module
parses the argument-level string with formal placeholders ``s`` and ``c``, reads it under each
grammar, and only then substitutes ``s -> sin(x)``, ``c -> cos(x)``.

That is a model and it is stated as one.  It answers "would this identity still have been written
this way?" and it does **not** answer "what would trigonometric semantics have been?".  The limits
section of the report says so again.

Discipline
----------

Every object here is grouped by the project semantic key -- ``(canonical form, domain, excluded
points)`` -- and never by canonical text alone.  Two readings that denote the same partial
function land in the same class even when their parse trees differ, which is the rule
:mod:`parseatlas.functions` was corrected to obey under NF-2026-00004.

Periodicity is claimed only where a genuine trigonometric composition was built.  A truncated
series is a **polynomial**, in our world exactly as much as in any other: it is not periodic and
not bounded anywhere, and :func:`series_reading` reports ``is_periodic`` as a measured
:func:`sympy.calculus.util.periodicity` result rather than as an assumption.  A constant reading
returns period ``0`` from SymPy, which is "constant", not "periodic with a fundamental period";
:data:`CONSTANT_PERIOD` names that sentinel so the distinction is in the code and not in prose.

``G0`` is given no discount anywhere.  Its truncation error against the true ``sin`` is measured at
the same declared sample points as every other world's reading and reported in the same table.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

from sympy import (
    Complement,
    Expr,
    FiniteSet,
    Intersection,
    Interval,
    Poly,
    S,
    Set,
    Symbol,
    Union,
    cos,
    fraction,
    limit,
    oo,
    pi,
    simplify,
    sin,
    singularities,
    solveset,
    sympify,
    tan,
    together,
    trigsimp,
)
from sympy.calculus.util import continuous_domain, periodicity

from .canonical import to_sympy, undefined_terms
from .functions import analyze_outer_functions
from .grammar import Grammar, all_grammars
from .parser import parse

# --------------------------------------------------------------------------------------- symbols

#: The variable of the series route and of the single-angle identities.
ANGLE: Symbol = Symbol("x", real=True)

#: The two angles of the addition formulas.
ANGLE_A: Symbol = Symbol("a", real=True)
ANGLE_B: Symbol = Symbol("b", real=True)

#: The variable of the outer-function route, matching :mod:`parseatlas.functions`.
INNER_VARIABLE: Symbol = Symbol("t", real=True)

#: The 25 worlds: the tied-level control ``G0`` and the 24 strict orderings.
GRAMMARS: tuple[Grammar, ...] = all_grammars()

GRAMMAR_BY_ID: dict[str, Grammar] = {grammar.id: grammar for grammar in GRAMMARS}

#: The conventional world.  Named, because every route is reported against it.
CONTROL_ID: str = "G0"

#: SymPy's :func:`~sympy.calculus.util.periodicity` returns ``0`` for a constant function.  A
#: constant is periodic with *every* period and therefore has no fundamental one; the sentinel is
#: named so that "constant" is never silently upgraded to "periodic".
CONSTANT_PERIOD = S.Zero


# ---------------------------------------------------------------------------------- route 1 data

#: The standard truncated Maclaurin series of sine, written in the Generation 1 language.
#:
#: There is no ``^``, so the powers are spelled as products.  That is not a workaround -- it is
#: what makes the string convention-sensitive at all, because every ``*`` in it is a place where a
#: different precedence order can re-associate the expression.
SERIES_SOURCE: str = "x - x*x*x/6 + x*x*x*x*x/120"

#: Declared before the sweep, so no world can be scored at points chosen after seeing its reading.
#:
#: The first six are inside or near the interval where the truncation is meant to be good; the last
#: three are outside it, and they are what make ``G0``'s own error visible.
SAMPLE_POINTS: tuple[Expr, ...] = (
    S.Zero,
    pi / 6,
    pi / 4,
    pi / 3,
    pi / 2,
    pi,
    2 * pi,
    S(3),
    S(10),
)


# ---------------------------------------------------------------------------------- route 2 data

#: Inner token strings for the outer-function route.  The first is the project's founding sequence.
#:
#: ``2*t + 1 - t/2`` reproduces experiment 0002 exactly and is the continuity check.  The other
#: four are chosen so that the route is not measured on affine arguments alone: ``t/2 + 1 - 2*t``
#: and ``1 - 2*t/4 + 3*t`` produce quadratic and rational arguments in some worlds, and
#: ``t*t - 3*t + 2`` is quadratic in *every* world, so ``sin`` of it is nowhere a wave.
INNER_SOURCES: tuple[str, ...] = (
    "2*t + 1 - t/2",
    "t/2 + 1 - 2*t",
    "3*t - 2 + 1",
    "1 - 2*t/4 + 3*t",
    "t*t - 3*t + 2",
)

#: The trigonometric outer functions.  ``tan`` is kept because its period is ``pi/|a|`` where
#: ``sin`` and ``cos`` have ``2*pi/|a|``, and that difference is an existing pinned result.
TRIGONOMETRIC_FUNCTIONS: tuple[str, ...] = ("sin", "cos", "tan")


# ---------------------------------------------------------------------------------- route 3 data


@dataclass(frozen=True)
class Identity:
    """One trigonometric identity, as the argument-level string it is written as.

    ``source`` is in formal placeholders: ``s`` for ``sin`` of the angle, ``c`` for ``cos`` of it,
    and ``sa``/``ca``/``sb``/``cb`` for the two-angle formulas.  ``target`` is the conventional
    right-hand side, i.e. what the string denotes in our world.
    """

    name: str
    source: str
    target: str
    two_angle: bool = False


#: What each placeholder stands for once the string has been read.
PLACEHOLDER_MEANING: dict[str, Expr] = {
    "s": sin(ANGLE),
    "c": cos(ANGLE),
    "sa": sin(ANGLE_A),
    "ca": cos(ANGLE_A),
    "sb": sin(ANGLE_B),
    "cb": cos(ANGLE_B),
}

_SUBSTITUTION: dict[Symbol, Expr] = {
    Symbol(name, real=True): value for name, value in PLACEHOLDER_MEANING.items()
}

#: The identities under test.
#:
#: The set deliberately spans the operator mixtures, because the mixture is what decides whether a
#: precedence change can touch the string at all.  ``double_angle_sine`` and ``tangent`` use a
#: single operator kind and are therefore *predicted* to be convention-free; they are included so
#: that the prediction is measured rather than assumed, and so that the survival counts contain a
#: control that cannot move.
IDENTITIES: tuple[Identity, ...] = (
    Identity("pythagorean", "s*s + c*c", "1"),
    Identity("cofunction_zero", "s*s + c*c - 1", "0"),
    Identity("double_angle_sine", "2*s*c", "sin(2*x)"),
    Identity("double_angle_cosine", "c*c - s*s", "cos(2*x)"),
    Identity("tangent", "s/c", "tan(x)"),
    Identity("pythagorean_tangent", "1 + s/c*s/c", "1/cos(x)**2"),
    Identity("angle_addition_sine", "sa*cb + ca*sb", "sin(a + b)", two_angle=True),
    Identity("angle_addition_cosine", "ca*cb - sa*sb", "cos(a + b)", two_angle=True),
)

IDENTITY_BY_NAME: dict[str, Identity] = {item.name: item for item in IDENTITIES}

#: The domain slot for a two-angle identity.  :func:`~sympy.calculus.util.continuous_domain` is a
#: single-variable instrument, so the two-angle rows carry a constant here exactly as
#: :func:`parseatlas.canonical.canonicalize` carries the constant ``"R"`` for an inner reading.
PLANE_DOMAIN: str = "R**2"


# ------------------------------------------------------------------------------------ concurrency

WORKER_HEADROOM_CORES: int = 2
WORKER_CAP: int = 12

#: What it costs to raise a spawn-start process pool that imports SymPy in every worker.
#:
#: **Measured, not assumed.**  On the recorded machine (16 cores, CPython 3.14, SymPy 1.14) a pool
#: of 8 or 12 workers that runs one trivial cell each returns in 3.1 s and 3.5 s once the import is
#: warm in the filesystem cache, and in about 15 s the first time.  The warm figure is the one used
#: here, rounded up, because an atlas is normally not the first pool of a session.
POOL_STARTUP_SECONDS: float = 4.0

#: Measured mean seconds per cell, per kind of work.  These are the inputs to
#: :func:`should_parallelise`, and they are the *reason* the routes do not all take the same path.
#:
#: Re-measured during review.  ``IDENTITY_CELL_SECONDS`` was published as ``0.25`` and did not
#: reproduce: three cold runs of ``identity_atlas(workers=1)`` gave 23.11 s, 19.37 s and 18.26 s
#: over 200 cells, a median of 0.097 s per cell.  The old figure was 2.6x high.  Correcting it
#: changes no routing decision -- ``should_parallelise(200, 0.097, 12)`` is still True, as it was
#: at 0.25 -- which is why no published result moves.  ``SERIES_CELL_SECONDS`` reproduces cleanly.
#: These are wall-clock figures on a loaded developer machine and are inputs to a threshold, not
#: results; treat them as an order of magnitude.
SERIES_CELL_SECONDS: float = 0.14
IDENTITY_CELL_SECONDS: float = 0.097
OUTER_ROW_SECONDS: float = 0.065
COMPOSITION_CELL_SECONDS: float = 0.07


def worker_count_for(cores: int, cell_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``cell_count`` independent cells.

    ``WORKER_HEADROOM_CORES`` cores stay free so a sweep cannot starve an interactive session,
    ``WORKER_CAP`` bounds the spawn cost any single atlas has to amortise, and no atlas ever raises
    more workers than it has cells.  The result is never zero and never exceeds the core count, so
    it is safe on a one-core machine.
    """
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(cell_count, 1)))


def default_worker_count(cell_count: int) -> int:
    """Worker count derived from the **observed** core count, never a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, cell_count)


def should_parallelise(cell_count: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising for this much work, from measured costs.

    A cell count on its own cannot answer this, and assuming it can is how a sweep ends up slower
    in parallel than in sequence.  The series atlas and the identity atlas are within a factor of
    eight in cell count and a factor of two in per-cell cost, and yet the measurement puts them on
    opposite sides: 25 cells at 0.14 s run in 3.5 s sequentially and 9.0 s across a pool, while 200
    cells at 0.25 s run in 49 s sequentially and 7.7 s across a pool.  What separates them is
    :data:`POOL_STARTUP_SECONDS`, so that is what the rule compares against.
    """
    if workers <= 1 or cell_count <= 1:
        return False
    sequential = cell_count * seconds_per_cell
    parallel = POOL_STARTUP_SECONDS + sequential / workers
    return parallel < sequential


def _map_cells(task: Any, payloads: Sequence[Any], workers: int | None, seconds_per_cell: float) -> list[Any]:
    """Run one independent cell per payload, across processes when the measurement says to.

    Every cell in this module is a pure function of its payload -- it parses a string, canonicalises
    it, and measures the result -- so any subset of them may run anywhere.  ``executor.map``
    preserves input order and the cells share no state, so the two paths return identical records;
    :mod:`tests.test_trigonometry_worlds` asserts that rather than assuming it.

    ``workers=None`` takes the measured decision.  An explicit ``workers`` overrides it, which is
    what lets a test force both paths over the same work and compare.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(len(payloads), seconds_per_cell, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [task(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(task, payloads, chunksize=1))


# ------------------------------------------------------------------------------ shared measurement


def semantic_key(canonical: str, domain: str, excluded: Sequence[str]) -> tuple[str, str, tuple[str, ...]]:
    """The project semantic key: ``(canonical form, domain, excluded points)``.

    Grouping by canonical text alone would split classes that denote one partial function and merge
    classes that denote two, which is the failure the triple exists to prevent.
    """
    return (canonical, domain, tuple(excluded))


def _real_points(points: Iterable[str]) -> tuple[str, ...]:
    """The real members of an excluded-point set.

    :func:`parseatlas.canonical.undefined_terms` solves denominators over the complex numbers, so a
    reading whose denominator is ``x**5 + 6`` carries four complex points alongside one real one.
    Only the real ones restrict a real function's domain, and only they can break the symmetry that
    oddness needs.
    """
    real: list[str] = []
    for text in points:
        if text == "all":
            real.append(text)
            continue
        try:
            value = sympify(text)
        except (SyntaxError, TypeError, ValueError):
            continue
        if value.is_real:
            real.append(text)
    return tuple(real)


#: Sentinel for a set slot SymPy declined to compute.
UNDETERMINED: str = "undetermined"


def _set_sort_key(text: str, member: Any) -> tuple[int, float, float, str]:
    """Order the members of a commutative set constructor deterministically.

    Intervals sort by their endpoints so that a domain reads left to right; everything else sorts by
    its own rendered text.  The tie-break on ``text`` is what makes the order a function of the
    *value* rather than of anything the process happens to know.
    """
    if isinstance(member, Interval):
        try:
            return (0, float(member.start), float(member.end), text)
        except (TypeError, ValueError, OverflowError):
            pass
    return (1, 0.0, 0.0, text)


def _set_text(value: Any) -> str:
    """A canonical rendering of a SymPy set, stable across processes.

    This exists because ``str(...)`` of a set is **not** stable.  ``Union`` and ``FiniteSet`` hold
    their members in an order derived from object hashes, and Python randomises string hashes per
    process, so the same real domain prints its ``ImageSet`` members in different orders in a parent
    process and in a pool worker.  A key built on that string would therefore be a function of the
    process rather than of the denoted value -- the same class of defect as NF-2026-00004, arriving
    through the printer instead of through the parse tree, and it splits one semantic class into two
    only when the sweep happens to run in parallel.

    :func:`sympy.core.sorting.default_sort_key` does not fix it: it returns equal keys for the
    ``ImageSet`` members of a tangent domain, so ``sorted`` merely preserves the hash order it was
    given.  Sorting on the members' own rendered text does fix it, and was verified by running the
    rendering in eight fresh interpreters.
    """
    if isinstance(value, (Union, Intersection)):
        parts = [_set_text(argument) for argument in value.args]
        ordered = [text for _, text in sorted(zip((_set_sort_key(text, argument) for text, argument in zip(parts, value.args)), parts))]
        return f"{type(value).__name__}({', '.join(ordered)})"
    if isinstance(value, Complement):
        return f"Complement({_set_text(value.args[0])}, {_set_text(value.args[1])})"
    if isinstance(value, FiniteSet):
        return "{" + ", ".join(sorted(str(member) for member in value.args)) + "}"
    return str(value)


def _canonical_set_text(text: str) -> str:
    """Re-render a set that reached us as a string, e.g. from :mod:`parseatlas.functions`.

    ``analyze_outer_functions`` reports its domain slots as ``str(...)`` and is outside this
    experiment's write scope, so the instability described in :func:`_set_text` is normalised here
    instead of there.  Only the argument order of commutative constructors changes; the set does not.
    """
    if text in {UNDETERMINED, ""}:
        return text
    try:
        parsed = sympify(text)
    except (SyntaxError, TypeError, ValueError, AttributeError):
        return text
    if isinstance(parsed, (set, frozenset)):
        parsed = FiniteSet(*parsed)
    if not isinstance(parsed, Set):
        return text
    return _set_text(parsed)


def _domain_of(value: Expr, variable: Symbol) -> str:
    try:
        return _set_text(continuous_domain(value, variable, S.Reals))
    except (NotImplementedError, ValueError, TypeError):
        return UNDETERMINED


def _periodicity_of(value: Expr, variable: Symbol) -> Any:
    try:
        return periodicity(value, variable)
    except (NotImplementedError, ValueError, TypeError, RecursionError):
        return None


def _is_periodic(period: Any) -> bool:
    """A measured period counts only when it exists and is not the constant sentinel."""
    return period is not None and period != CONSTANT_PERIOD


def _solution_set(value: Expr, variable: Symbol) -> str:
    try:
        return _set_text(solveset(value, variable, S.Reals))
    except (NotImplementedError, ValueError, TypeError, RecursionError):
        return UNDETERMINED


# --------------------------------------------------------------------------- route 1: the series


def _degrees(value: Expr) -> dict[str, Any]:
    """Degree data for a reading, which is a rational function in every world.

    A polynomial reading gets a ``degree``; a genuinely rational one gets the numerator and
    denominator degrees instead, because "the degree" of ``(1 - x**2)/(120*x**3*(x + 6))`` is not a
    number and must not be reported as one.
    """
    if value.is_zero:
        return {"is_polynomial": True, "degree": None, "numerator_degree": None, "denominator_degree": None}
    if value.is_polynomial(ANGLE):
        return {
            "is_polynomial": True,
            "degree": int(Poly(value, ANGLE).degree()),
            "numerator_degree": int(Poly(value, ANGLE).degree()),
            "denominator_degree": 0,
        }
    numerator, denominator = fraction(together(value))
    return {
        "is_polynomial": False,
        "degree": None,
        "numerator_degree": int(Poly(numerator, ANGLE).degree()),
        "denominator_degree": int(Poly(denominator, ANGLE).degree()),
    }


def _real_singularities(value: Expr) -> tuple[str, ...]:
    try:
        found = singularities(value, ANGLE, S.Reals)
    except (NotImplementedError, ValueError, TypeError):
        return ()
    if found is S.EmptySet:
        return ()
    try:
        return tuple(sorted((str(point) for point in found), key=str))
    except TypeError:
        return (str(found),)


def _sample_value(value: Expr, point: Expr) -> float | None:
    """The reading's value at one declared point, or ``None`` where it is undefined.

    A pole is not an error to be swallowed: several worlds read the series as a function that is
    undefined at ``0``, and ``None`` records exactly that.
    """
    substituted = value.subs(ANGLE, point)
    if substituted.has(S.ComplexInfinity) or substituted.has(S.NaN):
        return None
    numeric = substituted.evalf()
    if numeric.is_number and numeric.is_real and numeric.is_finite:
        return float(numeric)
    return None


def series_reading(grammar_id: str) -> dict[str, Any]:
    """Everything route 1 measures about one world's reading of :data:`SERIES_SOURCE`."""
    grammar = GRAMMAR_BY_ID[grammar_id]
    node = parse(SERIES_SOURCE, grammar)
    value = simplify(to_sympy(node))
    excluded = list(undefined_terms(node))
    real_excluded = _real_points(excluded)
    domain = _domain_of(value, ANGLE)

    reflected = simplify(value.subs(ANGLE, -ANGLE))
    odd_as_value = bool(simplify(reflected + value) == 0)
    even_as_value = bool(simplify(reflected - value) == 0)

    # The domain of the reading *as written* is the value's real poles together with the parse
    # tree's own validity restrictions.  A function is odd only if that set is symmetric under
    # negation, so a world that reads the series as the constant zero but excludes -6 and not +6
    # is not odd as a partial function even though it is odd as an expression.
    poles = set(_real_singularities(value)) | {point for point in real_excluded if point != "all"}
    reflected_poles = {str(simplify(-sympify(point))) for point in poles}
    domain_symmetric = poles == reflected_poles

    period = _periodicity_of(value, ANGLE)
    limit_plus = limit(value, ANGLE, oo)
    limit_minus = limit(value, ANGLE, -oo)
    unbounded_at_infinity = not (limit_plus.is_finite and limit_minus.is_finite)

    samples = []
    # None, not 0.0: a reading undefined at every sample point has NO measured error, and 0.0
    # would read as a perfect match for sine.  No world triggers this today -- every world is
    # defined at at least one sample -- but the trap opens if SAMPLE_POINTS or the corpus changes.
    worst: float | None = None
    for point in SAMPLE_POINTS:
        observed = _sample_value(value, point)
        truth = float(sin(point).evalf())
        error = None if observed is None else abs(observed - truth)
        if error is not None:
            worst = error if worst is None else max(worst, error)
        samples.append(
            {
                "point": str(point),
                "value": observed,
                "true_sine": truth,
                "absolute_error": error,
            }
        )

    return {
        "grammar": grammar_id,
        "precedence": [list(level) for level in grammar.levels],
        "canonical": str(value),
        "domain": domain,
        "excluded_points": excluded,
        "real_excluded_points": list(real_excluded),
        "key": list(semantic_key(str(value), domain, excluded)),
        **_degrees(value),
        "real_roots": _solution_set(value, ANGLE),
        "real_poles": list(sorted(poles, key=str)),
        "odd_as_value": odd_as_value,
        "even_as_value": even_as_value,
        "domain_symmetric": domain_symmetric,
        "odd_as_partial_function": odd_as_value and domain_symmetric,
        "sympy_periodicity": None if period is None else str(period),
        "is_periodic": _is_periodic(period),
        "limit_at_plus_infinity": str(limit_plus),
        "limit_at_minus_infinity": str(limit_minus),
        "unbounded_on_reals": bool(unbounded_at_infinity or poles),
        "samples": samples,
        "max_absolute_error": worst,
    }


def series_atlas(grammar_ids: Sequence[str] | None = None, workers: int | None = None) -> dict[str, Any]:
    """Route 1 over the worlds: what polynomial is the sine series, world by world."""
    ids = tuple(grammar_ids) if grammar_ids is not None else tuple(grammar.id for grammar in GRAMMARS)
    rows = _map_cells(series_reading, ids, workers, SERIES_CELL_SECONDS)

    classes: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
    for row in rows:
        classes.setdefault(semantic_key(row["canonical"], row["domain"], row["excluded_points"]), []).append(row["grammar"])

    control = next((row for row in rows if row["grammar"] == CONTROL_ID), None)
    return {
        "source": SERIES_SOURCE,
        "sample_points": [str(point) for point in SAMPLE_POINTS],
        "readings": rows,
        "classes": [
            {"id": f"S{index:02d}", "canonical": key[0], "domain": key[1], "excluded_points": list(key[2]), "grammars": members}
            for index, (key, members) in enumerate(classes.items(), start=1)
        ],
        "distinct_semantic_classes": len(classes),
        "distinct_canonical_values": len({row["canonical"] for row in rows}),
        "odd_as_value_count": sum(1 for row in rows if row["odd_as_value"]),
        "odd_as_partial_function_count": sum(1 for row in rows if row["odd_as_partial_function"]),
        "periodic_count": sum(1 for row in rows if row["is_periodic"]),
        "constant_zero_grammars": sorted(row["grammar"] for row in rows if row["canonical"] == "0"),
        "control_max_absolute_error": None if control is None else control["max_absolute_error"],
        "worst_max_absolute_error": max(row["max_absolute_error"] for row in rows),
    }


# ------------------------------------------------------------- route 2: sine as an outer function


def _outer_row(payload: tuple[str, str, str]) -> dict[str, Any]:
    """One ``(inner source, trigonometric function, world)`` cell of route 2.

    The inner reading and every property of the composition come from
    :func:`parseatlas.functions.analyze_outer_functions`, which is the instrument experiment 0002
    used and the one NF-2026-00004 corrected.  It is called here for a single grammar because the
    per-grammar cell is what makes the route's work divisible: composing ``tan`` on a rational
    argument dominates the cost and does so grammar by grammar, so a cell per ``(source, function)``
    leaves one 19-second cell that the whole sweep waits on, while a cell per world leaves 375 cells
    whose slowest is 2.35 s.

    Only the domain slots are touched on the way out, and only to re-render them: see
    :func:`_canonical_set_text`.
    """
    source, function_name, grammar_id = payload
    report = analyze_outer_functions(source, (function_name,), (GRAMMAR_BY_ID[grammar_id],))
    item = report["results"][0]
    properties = dict(item["properties"])
    return {
        "grammar": item["grammar"],
        "function": function_name,
        "source": source,
        "inner": item["inner"],
        "inner_excluded_points": list(item["inner_excluded_points"]),
        "canonical": item["canonical"],
        "constant_argument": bool(properties.get("constant_argument")),
        "frequency": properties.get("frequency"),
        "declared_period": properties.get("period"),
        "inner_real_domain": _canonical_set_text(properties.get("inner_real_domain", UNDETERMINED)),
        "real_domain": _canonical_set_text(properties.get("real_domain", UNDETERMINED)),
    }


def _composition_measure(payload: tuple[str, str]) -> dict[str, Any]:
    """The two things ``analyze_outer_functions`` does not carry: the zero set and a second period.

    The second period is not decoration.  :mod:`parseatlas.functions` derives ``2*pi/|a|`` and
    ``pi/|a|`` from the argument's derivative; this recomputes the period of the composed function
    with :func:`sympy.calculus.util.periodicity`, which knows nothing about that derivation, so the
    two figures can disagree and :func:`outer_atlas` reports it when they do.

    Keyed on the inner canonical text rather than on the grammar, because every world that denotes
    the same argument composes to the same function -- that is the semantic key doing its job.
    """
    inner_text, function_name = payload
    argument = sympify(inner_text, locals={"t": INNER_VARIABLE})
    composed = {"sin": sin, "cos": cos, "tan": tan}[function_name](argument)
    period = _periodicity_of(composed, INNER_VARIABLE)
    return {
        "inner": inner_text,
        "function": function_name,
        "zeros": _solution_set(composed, INNER_VARIABLE),
        "sympy_periodicity": None if period is None else str(period),
        "is_periodic": _is_periodic(period),
    }


def outer_atlas(
    sources: Sequence[str] | None = None,
    functions: Sequence[str] | None = None,
    grammar_ids: Sequence[str] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Route 2 over the worlds: what wave is ``sin`` of this token string, world by world."""
    sources = tuple(sources) if sources is not None else INNER_SOURCES
    functions = tuple(functions) if functions is not None else TRIGONOMETRIC_FUNCTIONS
    ids = tuple(grammar_ids) if grammar_ids is not None else tuple(grammar.id for grammar in GRAMMARS)

    rows = _map_cells(
        _outer_row,
        [(source, function_name, grammar_id) for source in sources for function_name in functions for grammar_id in ids],
        workers,
        OUTER_ROW_SECONDS,
    )
    pairs = list(dict.fromkeys((row["inner"], row["function"]) for row in rows))
    measures = {(item["inner"], item["function"]): item for item in _map_cells(_composition_measure, pairs, workers, COMPOSITION_CELL_SECONDS)}

    per_source: dict[str, dict[str, Any]] = {source: {"source": source, "functions": {}} for source in sources}
    period_disagreements: list[dict[str, Any]] = []
    for source in sources:
        for function_name in functions:
            cell = [
                {**row, **{key: value for key, value in measures[(row["inner"], row["function"])].items() if key not in {"inner", "function"}}}
                for row in rows
                if row["source"] == source and row["function"] == function_name
            ]
            classes: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
            for row in cell:
                classes.setdefault(semantic_key(row["canonical"], row["real_domain"], row["inner_excluded_points"]), []).append(row["grammar"])
                declared = row["declared_period"]
                if declared is not None and not row["constant_argument"] and declared != row["sympy_periodicity"]:
                    period_disagreements.append(
                        {"source": source, "function": function_name, "grammar": row["grammar"], "declared": declared, "measured": row["sympy_periodicity"]}
                    )
            per_source[source]["functions"][function_name] = {
                "rows": cell,
                "semantic_classes": len(classes),
                "inner_classes": len({row["inner"] for row in cell}),
                "constant_argument_grammars": sorted(row["grammar"] for row in cell if row["constant_argument"]),
                "wave_grammars": sorted(row["grammar"] for row in cell if row["is_periodic"]),
                "non_wave_grammars": sorted(row["grammar"] for row in cell if not row["is_periodic"]),
                "classes": [
                    {
                        "id": f"O{index:02d}",
                        "canonical": key[0],
                        "real_domain": key[1],
                        "inner_excluded_points": list(key[2]),
                        "inner": next(row["inner"] for row in cell if row["grammar"] == members[0]),
                        "grammars": members,
                    }
                    for index, (key, members) in enumerate(classes.items(), start=1)
                ],
            }

    return {
        "sources": list(sources),
        "functions": list(functions),
        "per_source": [per_source[source] for source in sources],
        "period_disagreements": period_disagreements,
    }


# ------------------------------------------------------------------------- route 3: the identities


def identity_reading(identity_name: str, grammar_id: str) -> dict[str, Any]:
    """What one world's reading of one identity string denotes, and whether it is still the identity."""
    identity = IDENTITY_BY_NAME[identity_name]
    grammar = GRAMMAR_BY_ID[grammar_id]

    node = parse(identity.source, grammar)
    placeholder_value = simplify(to_sympy(node))
    excluded = list(undefined_terms(node))

    substituted = trigsimp(simplify(placeholder_value.subs(_SUBSTITUTION)))
    target = sympify(identity.target, locals={"x": ANGLE, "a": ANGLE_A, "b": ANGLE_B})
    holds = bool(simplify(substituted - target) == 0)

    if identity.two_angle:
        domain = PLANE_DOMAIN
        period = None
    else:
        domain = _domain_of(substituted, ANGLE)
        period = _periodicity_of(substituted, ANGLE)

    return {
        "identity": identity_name,
        "grammar": grammar_id,
        "precedence": [list(level) for level in grammar.levels],
        "source": identity.source,
        "canonical": str(placeholder_value),
        "domain": domain,
        "excluded_points": excluded,
        "key": list(semantic_key(str(placeholder_value), domain, excluded)),
        "substituted": str(substituted),
        "target": str(target),
        "holds": holds,
        "sympy_periodicity": None if period is None else str(period),
        "is_periodic": _is_periodic(period),
    }


def _identity_cell(payload: tuple[str, str]) -> dict[str, Any]:
    return identity_reading(payload[0], payload[1])


def identity_atlas(identity_names: Sequence[str] | None = None, grammar_ids: Sequence[str] | None = None, workers: int | None = None) -> dict[str, Any]:
    """Route 3 over the worlds: which trigonometric identities survive the change of convention."""
    names = tuple(identity_names) if identity_names is not None else tuple(item.name for item in IDENTITIES)
    ids = tuple(grammar_ids) if grammar_ids is not None else tuple(grammar.id for grammar in GRAMMARS)
    payloads = [(name, grammar_id) for name in names for grammar_id in ids]
    rows = _map_cells(_identity_cell, payloads, workers, IDENTITY_CELL_SECONDS)

    per_identity: list[dict[str, Any]] = []
    for name in names:
        subset = [row for row in rows if row["identity"] == name]
        classes: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
        for row in subset:
            classes.setdefault(semantic_key(row["canonical"], row["domain"], row["excluded_points"]), []).append(row["grammar"])
        holding = sorted(row["grammar"] for row in subset if row["holds"])
        per_identity.append(
            {
                "identity": name,
                "source": IDENTITY_BY_NAME[name].source,
                "target": IDENTITY_BY_NAME[name].target,
                "holds_in": holding,
                "holds_count": len(holding),
                "convention_free": len(classes) == 1,
                "semantic_classes": len(classes),
                "classes": [
                    {
                        "id": f"I{index:02d}",
                        "canonical": key[0],
                        "domain": key[1],
                        "excluded_points": list(key[2]),
                        "grammars": members,
                        "substituted": next(row["substituted"] for row in subset if row["grammar"] == members[0]),
                        "holds": next(row["holds"] for row in subset if row["grammar"] == members[0]),
                    }
                    for index, (key, members) in enumerate(classes.items(), start=1)
                ],
            }
        )

    survival = {
        grammar_id: sorted(row["identity"] for row in rows if row["grammar"] == grammar_id and row["holds"])
        for grammar_id in ids
    }
    best = max((len(kept) for kept in survival.values()), default=0)
    return {
        "identities": list(names),
        "readings": rows,
        "per_identity": per_identity,
        "survival": {grammar_id: {"kept": kept, "count": len(kept)} for grammar_id, kept in survival.items()},
        "best_count": best,
        "best_grammars": sorted(grammar_id for grammar_id, kept in survival.items() if len(kept) == best),
        "control_count": len(survival.get(CONTROL_ID, [])),
        "convention_free_identities": [item["identity"] for item in per_identity if item["convention_free"]],
    }


# ---------------------------------------------------------------------------- the headline answers


def trigonometry_report(workers: int | None = None) -> dict[str, Any]:
    """All three routes plus the five headline answers, each backed by the measurement above."""
    series = series_atlas(workers=workers)
    outer = outer_atlas(workers=workers)
    identities = identity_atlas(workers=workers)

    pythagorean = next(item for item in identities["per_identity"] if item["identity"] == "pythagorean")
    other_worlds = [grammar_id for grammar_id in pythagorean["holds_in"] if grammar_id != CONTROL_ID]

    collapse = {}
    for bucket in outer["per_source"]:
        sine = bucket["functions"].get("sin")
        if sine is not None:
            collapse[bucket["source"]] = sine["constant_argument_grammars"]

    answers = {
        "q1_distinct_series_readings": {
            "semantic_classes": series["distinct_semantic_classes"],
            "distinct_canonical_values": series["distinct_canonical_values"],
        },
        "q2_odd_worlds": {
            "as_value": series["odd_as_value_count"],
            "as_partial_function": series["odd_as_partial_function_count"],
        },
        "q3_pythagorean_survives_elsewhere": {
            "holds_in": pythagorean["holds_in"],
            "other_than_control": other_worlds,
            "count": pythagorean["holds_count"],
        },
        "q4_most_identities_kept": {
            "best_count": identities["best_count"],
            "best_grammars": identities["best_grammars"],
            "control_count": identities["control_count"],
            "control_is_among_best": CONTROL_ID in identities["best_grammars"],
            "control_is_uniquely_best": identities["best_grammars"] == [CONTROL_ID],
        },
        "q5_constant_collapse": {
            "per_source": {source: {"grammars": members, "count": len(members)} for source, members in collapse.items()},
        },
    }
    return {"series": series, "outer": outer, "identities": identities, "answers": answers}


# ----------------------------------------------------------------------------- the multicore proof


def measure_parallel_decision(identity_names: Sequence[str] | None = None, workers: int | None = None) -> dict[str, Any]:
    """Time the sequential and parallel paths of the identity atlas and check they agree.

    Repository policy is that a parallel path changes only how fast, never what is produced, and
    that the choice between the two is a *measurement*.  This function is that measurement: it runs
    the same atlas twice and returns both elapsed times together with an equality check on the
    records, so :func:`should_parallelise` and the per-cell constants it reads can be justified from
    numbers rather than asserted.
    """
    names = tuple(identity_names) if identity_names is not None else tuple(item.name for item in IDENTITIES)

    start = time.perf_counter()
    sequential = identity_atlas(names, workers=1)
    sequential_seconds = time.perf_counter() - start

    resolved = workers if workers is not None else default_worker_count(len(names) * len(GRAMMARS))
    start = time.perf_counter()
    parallel = identity_atlas(names, workers=resolved)
    parallel_seconds = time.perf_counter() - start

    return {
        "cells": len(names) * len(GRAMMARS),
        "cpu_count": os.cpu_count(),
        "workers": resolved,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": sequential_seconds / parallel_seconds if parallel_seconds else None,
        "records_identical": sequential["readings"] == parallel["readings"],
        "decision": "parallel" if parallel_seconds < sequential_seconds else "sequential",
    }
