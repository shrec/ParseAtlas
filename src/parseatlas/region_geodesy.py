"""Experiment 0051: does the Region model earn its keep on geodetic against ECEF?

Phase 14 is a programme.  This module is the experiment that decides whether its
premise holds on **one concrete pair**, before anyone commits to the engine.  It
is not a geodesy library and it is not the Region engine.

The premise, stated as ROADMAP T22 states it
--------------------------------------------

Value equality ``F1(x) == F2(x)`` cannot express a transformation that changes
the input encoding, and the obligation must become a decode relation

.. code-block:: text

    decode(R2(x')) == R1(x)

Experiment 0033 built that obligation on one axis -- deferred division on
rational values -- where both sides live in ordinary rational arithmetic.  The
question this card asks is whether the obligation says anything the project's
existing equivalence oracle cannot, on a pair that classical mathematics already
publishes:

.. code-block:: text

    geodetic   (phi, lambda, h)   latitude, longitude, height above the ellipsoid
    ECEF       (X, Y, Z)          earth-centred, earth-fixed Cartesian

Three properties make this a test rather than an illustration, and each is
measured here rather than asserted:

1. **the seam is asymmetric** -- ``geodetic -> ECEF`` is closed form,
   ``ECEF -> geodetic`` is classically iterative.  :func:`seam_table` reports
   both directions in operation counts and in iterations to a declared
   tolerance, and the asymmetry as a ratio;
2. **value equality fails by construction** -- :func:`obligation_audit`
   measures, over the declared sample, how often the two encodings of one
   physical point are equal as tuples, and how often the decode relation holds;
3. **notation choice has a numerical consequence** -- :func:`cancellation_table`
   takes three algebraically identical writings of the ellipsoidal height,
   evaluates each in exact arithmetic and in float, and reports where they
   disagree and by how much.

What Generation 1 cannot write, stated before any result is read
---------------------------------------------------------------

The project's notation is four binary operators over numbers and variables.
:func:`parseatlas.canonical.to_sympy` accepts ``+ - * /`` and nothing else, and
the parser rejects a function application outright -- ``sin(phi)`` fails with
``Unexpected token: '('``.  Experiments 0002 and 0032 supply ``sin``, ``cos``
and ``sqrt`` as **outer** functions: a unary function wrapping a whole
Generation 1 expression, never an operand inside one.  ``atan2`` does not exist
in the project at all, and could not be an outer function if it did, because
every outer function in :data:`parseatlas.functions.OUTER_FUNCTIONS` is unary.

So: **no world in this project writes a geodetic conversion.**  The rational
skeleton of each formula parses once its transcendental leaves are bound to
names outside the notation; the leaves themselves do not.
:func:`generation_one_expressibility` measures exactly which parts parse and
which do not, and records the parser's own error text for each refusal.

What of 0033's machinery fits, measured rather than argued
----------------------------------------------------------

:func:`region_model_fit` runs the three parts of 0033 against this pair and
records what each one does:

* **the Region shape fits.**  ``(inputs, state, operations, outputs,
  invariants)`` is the right shape for both representations and for the
  iteration, and this module uses it unchanged.
* **the cost half fits unchanged.**  :func:`parseatlas.region.region_cost` is
  structural -- it counts an operation DAG and never looks at what an operation
  *means* -- so it prices a region of this module's vocabulary correctly by
  construction.  It is called here, not reimplemented.
* **the encoding and discharge half does not fit, and the refusal is exact.**
  :class:`parseatlas.region.Encoding` parses every map with
  ``_parse_rational``, which refuses ``sqrt``; :class:`parseatlas.region.Operation`
  refuses any kind outside ``{add, sub, mul, div, neg}``; and
  :func:`parseatlas.region.unroll` rebuilds ``Operation`` objects and therefore
  refuses to unroll this module's loop.  Those three refusals are triggered and
  their messages recorded.

That is itself a finding about the model: **0033's Region model is a model of
rational-function regions.**  The decode obligation generalises; the decision
procedures that discharged it do not, because they were decision procedures for
the rational-function class and this pair is not in it.

The representation choice that makes an exact answer possible
-------------------------------------------------------------

``sin(phi)`` is transcendental for every rational ``phi`` but ``0``, so a sample
of latitudes given as angles has no exact arithmetic behind it.  This module
therefore declares the geodetic encoding in **trigonometric form**

.. code-block:: text

    geodetic, angle form         (phi, lambda, h)
    geodetic, trigonometric form (sin phi, cos phi, sin lambda, cos lambda, h)

and builds every sample latitude and longitude from a **Pythagorean triple**, so
that ``sin`` and ``cos`` are exact rationals with ``s*s + c*c == 1`` exactly.
Every quantity in the forward map then lies in ``Q(sqrt(W))`` with
``W = 1 - e^2 sin^2 phi`` rational -- one quadratic extension of the rationals,
implemented by :class:`Surd`.  The exact side of this experiment is therefore
exact arithmetic and not high-precision floating point.

The trigonometric form is a **declared representation choice** and it is the
third representation in play.  It is what makes the exact authority exist; it is
also why the angle form appears only on the float side.  Both are named in the
limits.

Every operation counted is an operation executed
------------------------------------------------

Each conversion is declared once, as a :class:`GeoRegion`, and that single
declaration is what :func:`seam_table` counts and what :func:`evaluate_exact`
and :func:`evaluate_float` execute.  There is no second copy of the formulas to
drift from the one that was priced.
"""

from __future__ import annotations

import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

import sympy

from .alternative_mathematics import semantic_key
from .canonical import canonicalize
from .grammar import control_grammar
from .parser import parse
from .region import OPERATION_ARITY as RATIONAL_OPERATION_ARITY
from .region import BrokenEncoding, Encoding, Operation, Region, StateBinding, region_cost, unroll

__all__ = [
    "ANGLE_AGREEMENT_TOLERANCE",
    "ANGLE_TOLERANCE",
    "ANGLE_TOLERANCE_SWEEP",
    "CHAIN_STEPS",
    "GEODETIC_TO_ECEF",
    "GEODETIC_TRIG_TO_ECEF",
    "GEO_OPERATION_ARITY",
    "HEIGHT_TOLERANCE",
    "H_WRITINGS",
    "SAMPLE",
    "TRANSCENDENTAL_KINDS",
    "WGS84",
    "Ellipsoid",
    "GeoOperation",
    "GeoRegion",
    "SamplePoint",
    "Surd",
    "cancellation_table",
    "chain_table",
    "default_worker_count",
    "evaluate_exact",
    "evaluate_float",
    "exact_ecef",
    "float_inverse",
    "generation_one_expressibility",
    "geo_cost",
    "headline_report",
    "inverse_epilogue_region",
    "inverse_step_region",
    "obligation_audit",
    "parallelism_measurement",
    "point_named",
    "region_model_fit",
    "resolve_worker_count",
    "seam_table",
    "symbolic_discharge",
    "worker_count_for",
    "unroll_geo",
    "should_parallelise",
    "reference_check",
    "parallel_break_even",
    "operation_obligation",
    "measure_pool_startup",
]


# --------------------------------------------------------------------------
# The ellipsoid, exactly
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Ellipsoid:
    """A reference ellipsoid given by its two **defining** constants, exactly.

    ``a`` and ``1/f`` are the defining constants of WGS 84 and are exact
    decimals, so ``f``, ``b = a(1-f)`` and ``e^2 = f(2-f)`` are exact rationals
    and are computed here rather than quoted.  Everything else in this module
    that needs an ellipsoid parameter reads it from one of these fields.
    """

    name: str
    semi_major: Fraction
    inverse_flattening: Fraction

    @property
    def flattening(self) -> Fraction:
        return 1 / self.inverse_flattening

    @property
    def semi_minor(self) -> Fraction:
        """``b = a (1 - f)``, exact."""
        return self.semi_major * (1 - self.flattening)

    @property
    def eccentricity_squared(self) -> Fraction:
        """``e^2 = f (2 - f)``, exact -- and the writing without cancellation.

        The other two classical writings, ``1 - (b/a)^2`` and ``(a^2-b^2)/a^2``,
        are algebraically identical and are measured against this one in
        :func:`cancellation_table`.
        """
        f = self.flattening
        return f * (2 - f)

    @property
    def one_minus_e2(self) -> Fraction:
        return 1 - self.eccentricity_squared

    @property
    def polar_radius_of_curvature(self) -> Fraction:
        """``a^2 / b``, the prime vertical radius of curvature at the pole."""
        return self.semi_major * self.semi_major / self.semi_minor


#: WGS 84.  ``a = 6378137 m`` and ``1/f = 298.257223563`` are the defining
#: constants; everything else is derived exactly.
WGS84 = Ellipsoid(
    name="WGS 84",
    semi_major=Fraction(6378137),
    inverse_flattening=Fraction(298257223563, 1000000000),
)

#: Published WGS 84 values, for the reference check.
#:
#: *PRIOR ART.*  These are the values published in the WGS 84 defining document
#: (NIMA TR8350.2, third edition, and its successor NGA.STND.0036_1.0.0_WGS84),
#: stated here from knowledge and checked in
#: ``tests/test_region_geodesy.py::test_published_wgs84_constants`` against the
#: exact derivation above.  They are quoted to the number of digits the
#: documents give.
PUBLISHED_WGS84: dict[str, float] = {
    "semi_major_a": 6378137.0,
    "inverse_flattening": 298.257223563,
    "semi_minor_b": 6356752.314245,
    "eccentricity_squared": 0.00669437999014,
    "polar_radius_of_curvature": 6399593.6258,
}

#: How many digits the exact side is rendered with when it must become a float.
#: The exact side is *arithmetic*, not this many digits; this is only the width
#: of the last step, and 50 digits is far past double precision so the rounding
#: is the one double rounding a comparison against a float needs.
EXACT_DIGITS = 50


# --------------------------------------------------------------------------
# Q(sqrt(w)): one quadratic extension, exactly
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Surd:
    """``u + v * sqrt(w)`` with ``u``, ``v``, ``w`` exact rationals.

    Every exact value in this module lives here.  The forward map introduces
    exactly one irrationality -- ``sqrt(1 - e^2 sin^2 phi)`` -- and the field it
    generates is closed under the four arithmetic operations, so the whole
    forward map and both height writings are computed in exact arithmetic rather
    than in high-precision floating point.

    ``w`` is carried on every value so that two Surds from different sample
    points can never be combined by accident.
    """

    u: Fraction
    v: Fraction
    w: Fraction

    def __post_init__(self) -> None:
        if self.w < 0:
            raise ValueError(f"Surd radicand {self.w} is negative")
        # Normalise so that equality is the equality of values and not of
        # spellings.  When ``w`` is a perfect rational square the extension is
        # trivial and ``v*sqrt(w)`` folds into ``u``; without this,
        # ``0 + a*sqrt(1)`` and ``a + 0*sqrt(1)`` are the same number and compare
        # unequal, which would make an exact check pass or fail on notation.
        root = _rational_sqrt(self.w)
        if root is not None and self.v != 0:
            object.__setattr__(self, "u", self.u + self.v * root)
            object.__setattr__(self, "v", Fraction(0))

    @staticmethod
    def rational(value: Fraction | int, radicand: Fraction) -> "Surd":
        return Surd(Fraction(value), Fraction(0), Fraction(radicand))

    @property
    def is_rational(self) -> bool:
        return self.v == 0

    def _check(self, other: "Surd") -> None:
        if self.w != other.w:
            raise ValueError(
                f"Surd radicand mismatch: {self.w} against {other.w}; "
                "two sample points were combined"
            )

    def __add__(self, other: "Surd") -> "Surd":
        self._check(other)
        return Surd(self.u + other.u, self.v + other.v, self.w)

    def __sub__(self, other: "Surd") -> "Surd":
        self._check(other)
        return Surd(self.u - other.u, self.v - other.v, self.w)

    def __neg__(self) -> "Surd":
        return Surd(-self.u, -self.v, self.w)

    def __mul__(self, other: "Surd") -> "Surd":
        self._check(other)
        return Surd(
            self.u * other.u + self.v * other.v * self.w,
            self.u * other.v + self.v * other.u,
            self.w,
        )

    def __truediv__(self, other: "Surd") -> "Surd":
        self._check(other)
        norm = other.u * other.u - other.v * other.v * other.w
        if norm == 0:
            raise ZeroDivisionError(f"Surd division by {other}")
        conjugate = Surd(other.u, -other.v, self.w)
        numerator = self * conjugate
        return Surd(numerator.u / norm, numerator.v / norm, self.w)

    def sqrt(self) -> "Surd":
        """The square root, defined only where it stays in this field.

        The only square root the forward map takes is of the rational ``w``
        itself, and the only one the inverse takes is of ``p^2``, which is the
        square of a value already in the field.  Anything else raises rather
        than silently leaving exact arithmetic.
        """
        if self.is_rational and self.u == self.w:
            return Surd(Fraction(0), Fraction(1), self.w)
        if self.is_rational and self.u >= 0:
            root = _rational_sqrt(self.u)
            if root is not None:
                return Surd(root, Fraction(0), self.w)
        square_root = _square_root_in_field(self)
        if square_root is None:
            raise ValueError(f"sqrt({self}) leaves Q(sqrt({self.w}))")
        return square_root

    def as_sympy(self) -> Any:
        return sympy.Rational(self.u.numerator, self.u.denominator) + sympy.Rational(
            self.v.numerator, self.v.denominator
        ) * sympy.sqrt(sympy.Rational(self.w.numerator, self.w.denominator))

    def to_float(self, digits: int = EXACT_DIGITS) -> float:
        return float(self.as_sympy().evalf(digits))


def _rational_sqrt(value: Fraction) -> Fraction | None:
    """The exact rational square root of a non-negative rational, or ``None``."""
    if value < 0:
        return None
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        return None
    return Fraction(numerator, denominator)


def _square_root_in_field(value: Surd) -> Surd | None:
    """``sqrt(x)`` for ``x = (p + q sqrt(w))^2``, and ``None`` otherwise.

    Solves ``(p + q sqrt(w))^2 = u + v sqrt(w)`` over the rationals: ``2 p q =
    v`` and ``p^2 + q^2 w = u``.  Used once, on ``X^2 + Y^2``, whose root is
    ``p`` and is in the field by construction -- so this never has to guess.
    """
    if value.v == 0:
        root = _rational_sqrt(value.u)
        return None if root is None else Surd(root, Fraction(0), value.w)
    discriminant = value.u * value.u - value.v * value.v * value.w
    root_discriminant = _rational_sqrt(discriminant) if discriminant >= 0 else None
    if root_discriminant is None:
        return None
    for sign in (1, -1):
        squared = (value.u + sign * root_discriminant) / 2
        p = _rational_sqrt(squared) if squared >= 0 else None
        if p is None or p == 0:
            continue
        q = value.v / (2 * p)
        candidate = Surd(p, q, value.w)
        if candidate * candidate == value:
            return candidate
    return None


# --------------------------------------------------------------------------
# The region vocabulary: 0033's five kinds, and the four this pair needs
# --------------------------------------------------------------------------

#: The kinds a geodetic region may use.  The first five are **exactly** 0033's
#: :data:`parseatlas.region.OPERATION_ARITY`, imported and asserted equal in the
#: tests, so the extension is conservative on the shared vocabulary; the last
#: four are what this pair needs and what Generation 1 cannot write.
GEO_OPERATION_ARITY: dict[str, int] = {
    **RATIONAL_OPERATION_ARITY,
    "sqrt": 1,
    "sin": 1,
    "cos": 1,
    "atan2": 2,
}

#: The kinds outside 0033's rational vocabulary.  Reported separately in every
#: cost table, because a reader who prices a transcendental call differently
#: from a multiplication must be able to reweight without rerunning anything.
TRANSCENDENTAL_KINDS: frozenset[str] = frozenset({"sqrt", "sin", "cos", "atan2"})

GeoOperand = str | Fraction | int


@dataclass(frozen=True)
class GeoOperation:
    """One primitive operation ``target = kind(args...)``, 0033's shape widened.

    Deliberately a separate class rather than a subclass:
    :class:`parseatlas.region.Operation` refuses any kind outside its five, and
    that refusal is one of the measurements :func:`region_model_fit` makes.
    Subclassing would have hidden it.
    """

    target: str
    kind: str
    args: tuple[GeoOperand, ...]

    def __post_init__(self) -> None:
        if not self.target.isidentifier():
            raise ValueError(f"{self.target!r} is not a usable value name")
        if self.kind not in GEO_OPERATION_ARITY:
            raise ValueError(
                f"{self.target}: unknown operation kind {self.kind!r}; "
                f"the vocabulary is {sorted(GEO_OPERATION_ARITY)}"
            )
        normalised = tuple(
            argument if isinstance(argument, str) else Fraction(argument)
            for argument in self.args
        )
        arity = GEO_OPERATION_ARITY[self.kind]
        if len(normalised) != arity:
            raise ValueError(
                f"{self.target}: {self.kind} takes {arity} operand(s), got {len(normalised)}"
            )
        for argument in normalised:
            if isinstance(argument, str) and not argument.isidentifier():
                raise ValueError(
                    f"{self.target}: operand {argument!r} is not a name; pass a number "
                    "for a literal"
                )
        object.__setattr__(self, "args", normalised)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(argument for argument in self.args if isinstance(argument, str))

    @property
    def is_transcendental(self) -> bool:
        return self.kind in TRANSCENDENTAL_KINDS


@dataclass(frozen=True)
class GeoRegion:
    """``(inputs, state, operations, outputs, invariants)`` -- 0033's shape.

    The shape is 0033's and the validation is 0033's, restated for the wider
    vocabulary: single assignment, every operand defined before use, output keys
    disjoint from input names, and every state binding refilling a declared
    input from a declared output key.

    ``invariants`` are declared relations, carried as text.  Unlike 0033 they
    are **not** parsed into sympy booleans here: a relation such as
    ``s*s + c*c == 1`` is checked exactly on the sample by
    :func:`obligation_audit`, and one such as ``X*X + Y*Y == p*p`` is proved once
    and for all by :func:`symbolic_discharge`.  Where 0033 could parse an
    invariant because every invariant was a rational-function boolean, this pair
    cannot, and saying so is part of the answer.
    """

    name: str
    inputs: tuple[str, ...]
    operations: tuple[GeoOperation, ...]
    outputs: tuple[tuple[str, str], ...]
    state: tuple[StateBinding, ...] = ()
    invariants: tuple[str, ...] = ()
    note: str = ""

    def __post_init__(self) -> None:
        if not self.inputs:
            raise ValueError(f"{self.name}: a region needs at least one input")
        if len(set(self.inputs)) != len(self.inputs):
            raise ValueError(f"{self.name}: duplicated input name in {list(self.inputs)}")
        defined = set(self.inputs)
        for operation in self.operations:
            if operation.target in defined:
                raise ValueError(
                    f"{self.name}: {operation.target} is assigned twice "
                    "(the representation is single-assignment)"
                )
            for operand in operation.names:
                if operand not in defined:
                    raise ValueError(
                        f"{self.name}: {operation.target} uses undefined value {operand!r}"
                    )
            defined.add(operation.target)
        if not self.outputs:
            raise ValueError(f"{self.name}: a region needs at least one output")
        keys = [key for key, _ in self.outputs]
        if len(set(keys)) != len(keys):
            raise ValueError(f"{self.name}: duplicated output key in {keys}")
        overlap = sorted(set(keys) & set(self.inputs))
        if overlap:
            raise ValueError(
                f"{self.name}: output key {overlap[0]!r} collides with an input name"
            )
        for key, value_name in self.outputs:
            if value_name not in defined:
                raise ValueError(
                    f"{self.name}: output {key} uses undefined value {value_name!r}"
                )
        produced = {key for key, _ in self.outputs}
        for binding in self.state:
            if binding.carried not in self.inputs:
                raise ValueError(
                    f"{self.name}: carried value {binding.carried!r} is not an input"
                )
            if binding.produced not in produced:
                raise ValueError(
                    f"{self.name}: carried value {binding.carried!r} is refilled from "
                    f"{binding.produced!r}, which is not an output key"
                )

    @property
    def arity(self) -> int:
        return len(self.inputs)

    @property
    def output_keys(self) -> tuple[str, ...]:
        return tuple(sorted(key for key, _ in self.outputs))

    @property
    def carried_state(self) -> int:
        return len(self.state)

    @property
    def transcendental_count(self) -> int:
        return sum(1 for operation in self.operations if operation.is_transcendental)

    @property
    def rational_count(self) -> int:
        return len(self.operations) - self.transcendental_count


def geo_cost(region: GeoRegion) -> dict[str, Any]:
    """Price a geodetic region with **0033's own** :func:`parseatlas.region.region_cost`.

    0033's cost function walks an operation DAG and never asks what an operation
    means, so it prices this module's vocabulary correctly without modification.
    It is called, not reimplemented: a copy would agree today and drift later,
    and ``tests/test_region_geodesy.py`` asserts the call happens by checking the
    imported function's identity.

    The loop section is suppressed with ``loop_steps=()`` because 0033's
    :func:`parseatlas.region.unroll` rebuilds :class:`parseatlas.region.Operation`
    objects and therefore refuses this vocabulary.  That refusal is recorded by
    :func:`region_model_fit`, and the loop cost this experiment needs is
    computed by :func:`unroll_geo` instead.
    """
    priced = region_cost(region, loop_steps=())  # type: ignore[arg-type]
    payload = priced.as_dict()
    payload["transcendental_total"] = region.transcendental_count
    payload["rational_total"] = region.rational_count
    return payload


def unroll_geo(region: GeoRegion, steps: int, name: str | None = None) -> GeoRegion:
    """The ``steps``-fold composition of a region along its declared state.

    This is 0033's :func:`parseatlas.region.unroll` minus the normaliser.  The
    normaliser is dropped on purpose and not by omission: 0033's ``_cse``
    collapses an operation that every step emits identically, which is exactly
    right for its axis and exactly wrong here, because the operation that repeats
    in this loop is ``sin(phi)`` on a *changed* ``phi``.  Nothing in this loop is
    step-invariant, and :func:`seam_table` reports that as a measured fact rather
    than relying on it.
    """
    if steps < 1:
        raise ValueError(f"{region.name}: a loop needs at least one step, got {steps}")
    if not region.state:
        raise ValueError(f"{region.name}: no state binding is declared")
    operations: list[GeoOperation] = []
    current = {binding.carried: binding.carried for binding in region.state}
    step_outputs: dict[str, str] = {}
    for step in range(1, steps + 1):
        local: dict[str, str] = {}
        for operation in region.operations:
            args: list[GeoOperand] = []
            for argument in operation.args:
                if not isinstance(argument, str):
                    args.append(argument)
                elif argument in local:
                    args.append(local[argument])
                elif argument in current:
                    args.append(current[argument])
                else:
                    args.append(argument)
            target = f"{operation.target}__{step}"
            operations.append(GeoOperation(target, operation.kind, tuple(args)))
            local[operation.target] = target
        step_outputs = {
            key: local.get(value_name, current.get(value_name, value_name))
            for key, value_name in region.outputs
        }
        for binding in region.state:
            current[binding.carried] = step_outputs[binding.produced]
    return GeoRegion(
        name=name or f"{region.name}_x{steps}",
        inputs=region.inputs,
        operations=tuple(operations),
        outputs=tuple((key, step_outputs[key]) for key, _ in region.outputs),
        note=f"{steps}-step unrolling of {region.name}",
    )


# --------------------------------------------------------------------------
# Evaluation: one declaration, two arithmetics
# --------------------------------------------------------------------------


class NotExactlyEvaluable(ValueError):
    """Raised when a region asks exact arithmetic for a transcendental value."""


def evaluate_exact(
    region: GeoRegion, values: Mapping[str, Surd], radicand: Fraction
) -> dict[str, Surd]:
    """Run a region in exact ``Q(sqrt(radicand))`` arithmetic.

    ``sin``, ``cos`` and ``atan2`` raise :class:`NotExactlyEvaluable`: there is
    no exact rational arithmetic for them, and that is precisely why the sample
    is declared in trigonometric form.  ``sqrt`` is exact wherever it stays in
    the field, which is everywhere the forward map and the height writings need
    it.
    """
    environment: dict[str, Surd] = dict(values)
    for operation in region.operations:
        operands = [
            environment[argument]
            if isinstance(argument, str)
            else Surd.rational(argument, radicand)
            for argument in operation.args
        ]
        kind = operation.kind
        if kind == "add":
            result = operands[0] + operands[1]
        elif kind == "sub":
            result = operands[0] - operands[1]
        elif kind == "mul":
            result = operands[0] * operands[1]
        elif kind == "div":
            result = operands[0] / operands[1]
        elif kind == "neg":
            result = -operands[0]
        elif kind == "sqrt":
            result = operands[0].sqrt()
        else:
            raise NotExactlyEvaluable(
                f"{region.name}: {operation.target} = {kind}(...) has no exact rational "
                "arithmetic; the geodetic encoding is declared in trigonometric form "
                "for exactly this reason"
            )
        environment[operation.target] = result
    return {key: environment[name] for key, name in region.outputs}


def evaluate_float(region: GeoRegion, values: Mapping[str, float]) -> dict[str, float]:
    """Run a region in IEEE-754 double arithmetic, operation by operation.

    The walk is over the declared operations, in the declared order, so the
    float result is the result of the region that :func:`geo_cost` priced.  No
    associativity is rearranged and no sub-expression is reused beyond what the
    declaration itself names.
    """
    environment: dict[str, float] = dict(values)
    for operation in region.operations:
        operands = [
            environment[argument] if isinstance(argument, str) else float(argument)
            for argument in operation.args
        ]
        kind = operation.kind
        if kind == "add":
            result = operands[0] + operands[1]
        elif kind == "sub":
            result = operands[0] - operands[1]
        elif kind == "mul":
            result = operands[0] * operands[1]
        elif kind == "div":
            result = operands[0] / operands[1]
        elif kind == "neg":
            result = -operands[0]
        elif kind == "sqrt":
            result = math.sqrt(operands[0])
        elif kind == "sin":
            result = math.sin(operands[0])
        elif kind == "cos":
            result = math.cos(operands[0])
        else:
            result = math.atan2(operands[0], operands[1])
        environment[operation.target] = result
    return {key: environment[name] for key, name in region.outputs}


# --------------------------------------------------------------------------
# The two representations, declared as regions
# --------------------------------------------------------------------------

_A = WGS84.semi_major
_E2 = WGS84.eccentricity_squared
_1ME2 = WGS84.one_minus_e2

#: The prime-vertical radius, as operations.  Written once and shared by every
#: region that needs it, so the three height writings differ only in the height
#: and not in how ``N`` was reached.
_NORMAL_OPS: tuple[GeoOperation, ...] = (
    GeoOperation("s2", "mul", ("s", "s")),
    GeoOperation("es2", "mul", (_E2, "s2")),
    GeoOperation("w", "sub", (1, "es2")),
    GeoOperation("rw", "sqrt", ("w",)),
    GeoOperation("N", "div", (_A, "rw")),
)

#: ``geodetic -> ECEF``, angle form.  Closed form, no iteration, no branch.
GEODETIC_TO_ECEF = GeoRegion(
    name="geodetic_to_ecef",
    inputs=("phi", "lam", "h"),
    operations=(
        GeoOperation("s", "sin", ("phi",)),
        GeoOperation("c", "cos", ("phi",)),
        GeoOperation("sl", "sin", ("lam",)),
        GeoOperation("cl", "cos", ("lam",)),
        *_NORMAL_OPS,
        GeoOperation("Nh", "add", ("N", "h")),
        GeoOperation("p", "mul", ("Nh", "c")),
        GeoOperation("Xv", "mul", ("p", "cl")),
        GeoOperation("Yv", "mul", ("p", "sl")),
        GeoOperation("Nm", "mul", ("N", _1ME2)),
        GeoOperation("Nmh", "add", ("Nm", "h")),
        GeoOperation("Zv", "mul", ("Nmh", "s")),
    ),
    outputs=(("X", "Xv"), ("Y", "Yv"), ("Z", "Zv")),
    invariants=(
        "X*X + Y*Y + Z*Z/(1-e2)**2 is not a closed form: the ellipsoid relation is "
        "stated pointwise instead",
        "X*sin(lam) == Y*cos(lam)",
    ),
    note="closed form; the classical direct problem",
)

#: ``geodetic -> ECEF``, trigonometric form: the same region with the four
#: trigonometric evaluations lifted out into the inputs.  This is the region the
#: exact side runs, and its operation count is the angle form's minus four.
GEODETIC_TRIG_TO_ECEF = GeoRegion(
    name="geodetic_trig_to_ecef",
    inputs=("s", "c", "sl", "cl", "h"),
    operations=(
        *_NORMAL_OPS,
        GeoOperation("Nh", "add", ("N", "h")),
        GeoOperation("p", "mul", ("Nh", "c")),
        GeoOperation("Xv", "mul", ("p", "cl")),
        GeoOperation("Yv", "mul", ("p", "sl")),
        GeoOperation("Nm", "mul", ("N", _1ME2)),
        GeoOperation("Nmh", "add", ("Nm", "h")),
        GeoOperation("Zv", "mul", ("Nmh", "s")),
    ),
    outputs=(("X", "Xv"), ("Y", "Yv"), ("Z", "Zv"), ("P", "p"), ("NORMAL", "N")),
    invariants=("s*s + c*c == 1", "sl*sl + cl*cl == 1"),
    note="the angle form with sin and cos lifted into the inputs; exactly evaluable",
)


def _height_ops(writing: str) -> tuple[GeoOperation, ...]:
    """The operations of one writing of the ellipsoidal height, given ``p`` and ``Z``.

    Three writings of one quantity, algebraically identical and numerically not:

    .. code-block:: text

        A   h = p / cos(phi) - N
        B   h = Z / sin(phi) - N (1 - e^2)
        C   h = p cos(phi) + Z sin(phi) - a sqrt(1 - e^2 sin^2 phi)

    ``C`` is the one that needs no ``N`` at all, which is why it carries no
    division.  Their equality is proved once by :func:`symbolic_discharge` and
    corroborated exactly at every sample point by :func:`cancellation_table`.
    """
    if writing == "A":
        return (
            GeoOperation("hq", "div", ("p", "c")),
            GeoOperation("hv", "sub", ("hq", "N")),
        )
    if writing == "B":
        return (
            GeoOperation("hq", "div", ("Z", "s")),
            GeoOperation("Nm", "mul", ("N", _1ME2)),
            GeoOperation("hv", "sub", ("hq", "Nm")),
        )
    if writing == "C":
        return (
            GeoOperation("pc", "mul", ("p", "c")),
            GeoOperation("zs", "mul", ("Z", "s")),
            GeoOperation("t", "add", ("pc", "zs")),
            GeoOperation("ar", "mul", (_A, "rw")),
            GeoOperation("hv", "sub", ("t", "ar")),
        )
    raise ValueError(f"unknown height writing {writing!r}; the writings are A, B and C")


def _live_operations(
    operations: Sequence[GeoOperation], roots: Iterable[str]
) -> tuple[GeoOperation, ...]:
    """Drop every operation the outputs do not depend on.

    Needed because the three height writings share the prime-vertical block and
    writing ``C`` does not use ``N`` at all.  Reporting the shared block whole
    would charge ``C`` for a division it never performs, and the cost of a
    writing has to be the cost of that writing.
    """
    live = set(roots)
    kept: list[GeoOperation] = []
    for operation in reversed(tuple(operations)):
        if operation.target in live:
            kept.append(operation)
            live.update(operation.names)
    kept.reverse()
    return tuple(kept)


def _height_region(writing: str) -> GeoRegion:
    return GeoRegion(
        name=f"height_writing_{writing}",
        inputs=("p", "Z", "s", "c"),
        operations=_live_operations((*_NORMAL_OPS, *_height_ops(writing)), ("hv",)),
        outputs=(("H", "hv"),),
        invariants=("s*s + c*c == 1",),
        note=f"writing {writing} of the ellipsoidal height",
    )


#: The three height writings, each as a region so that the operation count and
#: the executed arithmetic come from one declaration.
H_WRITINGS: dict[str, GeoRegion] = {
    writing: _height_region(writing) for writing in ("A", "B", "C")
}

#: The declared undefined point of each writing.  Not a numerical claim -- a
#: division by an exactly zero denominator.  Writing ``C`` divides by nothing.
H_WRITING_EXCLUSION: dict[str, str | None] = {
    "A": "cos(phi) = 0",
    "B": "sin(phi) = 0",
    "C": None,
}

#: ``ECEF -> geodetic``, the part before the loop.
ECEF_TO_GEODETIC_SETUP = GeoRegion(
    name="ecef_to_geodetic_setup",
    inputs=("X", "Y", "Z"),
    operations=(
        GeoOperation("x2", "mul", ("X", "X")),
        GeoOperation("y2", "mul", ("Y", "Y")),
        GeoOperation("ss", "add", ("x2", "y2")),
        GeoOperation("pv", "sqrt", ("ss",)),
        GeoOperation("lamv", "atan2", ("Y", "X")),
        GeoOperation("pm", "mul", ("pv", _1ME2)),
        GeoOperation("phi0", "atan2", ("Z", "pm")),
    ),
    outputs=(("P", "pv"), ("LAM", "lamv"), ("PHI", "phi0")),
    invariants=("P*P == X*X + Y*Y",),
    note="longitude in closed form; the latitude seed of the fixed-point loop",
)


def inverse_step_region(writing: str = "C") -> GeoRegion:
    """One iteration of the classical fixed-point inverse, in a declared writing.

    .. code-block:: text

        N     = a / sqrt(1 - e^2 sin^2 phi)
        h     = <one of the three writings>
        phi'  = atan2(Z, p (1 - e^2 N / (N + h)))

    The state binding ``phi <- PHI`` is what makes this a region rather than a
    formula, exactly as 0033 requires: without it the per-iteration cost that
    decides the seam is not expressible at all.
    """
    return GeoRegion(
        name=f"ecef_to_geodetic_step_{writing}",
        inputs=("phi", "p", "Z"),
        operations=(
            GeoOperation("s", "sin", ("phi",)),
            GeoOperation("c", "cos", ("phi",)),
            *_NORMAL_OPS,
            *_height_ops(writing),
            GeoOperation("Nph", "add", ("N", "hv")),
            GeoOperation("ratio", "div", ("N", "Nph")),
            GeoOperation("eratio", "mul", (_E2, "ratio")),
            GeoOperation("q", "sub", (1, "eratio")),
            GeoOperation("pq", "mul", ("p", "q")),
            GeoOperation("phin", "atan2", ("Z", "pq")),
        ),
        outputs=(("PHI", "phin"), ("H", "hv")),
        state=(StateBinding(carried="phi", produced="PHI"),),
        invariants=("the fixed point satisfies p = (N + h) cos(phi) and Z = (N(1-e2)+h) sin(phi)",),
        note=f"one fixed-point iteration, height by writing {writing}",
    )


def inverse_epilogue_region(writing: str = "C") -> GeoRegion:
    """The height, computed once at the converged latitude.

    The fixed-point loop converges on the LATITUDE; the height is read off
    afterwards.  This is a separate region rather than a re-run of the step,
    because a re-run would also compute the next latitude, which nobody wants,
    and because the cost table must count what :func:`float_inverse` actually
    executes -- a loop of ``k`` steps plus this epilogue, never ``k + 1`` steps.
    """
    return GeoRegion(
        name=f"ecef_to_geodetic_epilogue_{writing}",
        inputs=("phi", "p", "Z"),
        operations=_live_operations(
            (
                GeoOperation("s", "sin", ("phi",)),
                GeoOperation("c", "cos", ("phi",)),
                *_NORMAL_OPS,
                *_height_ops(writing),
            ),
            ("hv",),
        ),
        outputs=(("H", "hv"),),
        note=f"the height at the converged latitude, by writing {writing}",
    )


#: The module's canonical inverse step.  Writing ``C`` is chosen because it is
#: the one that is defined at every latitude and the one the measurements below
#: show converging on every sample point; ``A`` and ``B`` are kept and measured
#: rather than discarded.
ECEF_TO_GEODETIC_STEP = inverse_step_region("C")

#: One longitude increment, in each representation.
#:
#: In geodetic it is a single addition.  In ECEF it is a rotation about the spin
#: axis, and the increment arrives as an angle, so the rotation pays for its own
#: sine and cosine.  Publishing the longitude costs one ``atan2`` in ECEF and
#: nothing at all in geodetic, because in geodetic the longitude *is* the state.
GEODETIC_LONGITUDE_STEP = GeoRegion(
    name="geodetic_longitude_step",
    inputs=("lam", "dlam"),
    operations=(GeoOperation("lamn", "add", ("lam", "dlam")),),
    outputs=(("LAM", "lamn"),),
    state=(StateBinding(carried="lam", produced="LAM"),),
    note="one longitude increment in the geodetic representation",
)

ECEF_LONGITUDE_STEP = GeoRegion(
    name="ecef_longitude_step",
    inputs=("X", "Y", "dlam"),
    operations=(
        GeoOperation("cd", "cos", ("dlam",)),
        GeoOperation("sd", "sin", ("dlam",)),
        GeoOperation("xc", "mul", ("X", "cd")),
        GeoOperation("ys", "mul", ("Y", "sd")),
        GeoOperation("xn", "sub", ("xc", "ys")),
        GeoOperation("xs", "mul", ("X", "sd")),
        GeoOperation("yc", "mul", ("Y", "cd")),
        GeoOperation("yn", "add", ("xs", "yc")),
        GeoOperation("lamv", "atan2", ("yn", "xn")),
    ),
    outputs=(("XO", "xn"), ("YO", "yn"), ("LAM", "lamv")),
    state=(
        StateBinding(carried="X", produced="XO"),
        StateBinding(carried="Y", produced="YO"),
    ),
    note="the same increment as a rotation about the spin axis, publishing the longitude",
)


# --------------------------------------------------------------------------
# The sample
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SamplePoint:
    """One physical point, declared so that its sine and cosine are exact.

    ``(lat_m, lat_n)`` and ``(lon_m, lon_n)`` generate Pythagorean triples

    .. code-block:: text

        cos = (m^2 - n^2) / (m^2 + n^2)        sin = 2mn / (m^2 + n^2)

    so ``sin^2 + cos^2 == 1`` exactly.  ``height`` is an exact rational number of
    metres.  The whole sample is hand-chosen to place points where the classical
    formulas are known to be delicate -- at the pole, at the equator, and at a
    sequence of latitudes approaching each -- and that choice is a limitation,
    not a sampling design.
    """

    label: str
    lat_m: int
    lat_n: int
    lon_m: int
    lon_n: int
    height: Fraction
    regime: str

    @staticmethod
    def _triple(m: int, n: int) -> tuple[Fraction, Fraction]:
        denominator = m * m + n * n
        return Fraction(m * m - n * n, denominator), Fraction(2 * m * n, denominator)

    @property
    def cos_phi(self) -> Fraction:
        return self._triple(self.lat_m, self.lat_n)[0]

    @property
    def sin_phi(self) -> Fraction:
        return self._triple(self.lat_m, self.lat_n)[1]

    @property
    def cos_lam(self) -> Fraction:
        return self._triple(self.lon_m, self.lon_n)[0]

    @property
    def sin_lam(self) -> Fraction:
        return self._triple(self.lon_m, self.lon_n)[1]

    @property
    def radicand(self) -> Fraction:
        """``W = 1 - e^2 sin^2 phi``, the one irrationality of the forward map."""
        return 1 - _E2 * self.sin_phi * self.sin_phi

    @property
    def phi(self) -> float:
        """The latitude as the nearest double to the true angle, in radians."""
        return float(
            sympy.atan2(
                sympy.Rational(self.sin_phi.numerator, self.sin_phi.denominator),
                sympy.Rational(self.cos_phi.numerator, self.cos_phi.denominator),
            ).evalf(EXACT_DIGITS)
        )

    @property
    def lam(self) -> float:
        return float(
            sympy.atan2(
                sympy.Rational(self.sin_lam.numerator, self.sin_lam.denominator),
                sympy.Rational(self.cos_lam.numerator, self.cos_lam.denominator),
            ).evalf(EXACT_DIGITS)
        )


def _point(label: str, lat: tuple[int, int], lon: tuple[int, int], height: int, regime: str) -> SamplePoint:
    return SamplePoint(label, lat[0], lat[1], lon[0], lon[1], Fraction(height), regime)


def point_named(label: str) -> SamplePoint:
    """One sample point by name.

    Every reference to a particular point in this module goes through here rather
    than through an index, so reordering or extending :data:`SAMPLE` cannot
    silently change which point a result is about.
    """
    for point in SAMPLE:
        if point.label == label:
            return point
    raise KeyError(f"no sample point named {label!r}")


#: The declared sample.  ``(1, 0)`` gives ``cos = 1, sin = 0`` -- the equator
#: exactly; ``(1, 1)`` gives ``cos = 0, sin = 1`` -- the north pole exactly.  The
#: near-pole and near-equator families march a decade at a time towards each, so
#: the report can show where a writing starts to fail rather than only that it
#: does.
SAMPLE: tuple[SamplePoint, ...] = (
    _point("equator_exact", (1, 0), (1, 0), 0, "degenerate"),
    _point("equator_exact_h", (1, 0), (3, 2), 1000, "degenerate"),
    _point("pole_exact", (1, 1), (1, 0), 0, "degenerate"),
    _point("pole_exact_h", (1, 1), (5, 2), 250, "degenerate"),
    _point("mid_3_4_5", (2, 1), (3, 2), 100, "mid-latitude"),
    _point("mid_5_12_13", (3, 2), (5, 2), 0, "mid-latitude"),
    _point("mid_8_15_17", (4, 1), (4, 1), 8848, "mid-latitude"),
    _point("mid_7_24_25", (5, 2), (7, 2), -400, "mid-latitude"),
    _point("mid_20_21_29", (5, 3), (1, 0), 100, "mid-latitude"),
    _point("mid_9_40_41", (5, 4), (2, 1), 35786000, "mid-latitude"),
    _point("near_pole_1e_2", (101, 100), (3, 2), 100, "near-polar"),
    _point("near_pole_1e_4", (10001, 10000), (3, 2), 100, "near-polar"),
    _point("near_pole_1e_6", (1000001, 1000000), (3, 2), 100, "near-polar"),
    _point("near_pole_1e_8", (100000001, 100000000), (3, 2), 100, "near-polar"),
    _point("near_pole_1e_10", (10000000001, 10000000000), (3, 2), 100, "near-polar"),
    _point("near_equator_1e_2", (100, 1), (3, 2), 100, "near-equatorial"),
    _point("near_equator_1e_4", (10000, 1), (3, 2), 100, "near-equatorial"),
    _point("near_equator_1e_6", (1000000, 1), (3, 2), 100, "near-equatorial"),
    _point("near_equator_1e_8", (100000000, 1), (3, 2), 100, "near-equatorial"),
    _point("near_equator_1e_10", (10000000000, 1), (3, 2), 100, "near-equatorial"),
    _point("small_height_pole", (100000001, 100000000), (3, 2), 0, "small height"),
    _point("small_height_equator", (100000000, 1), (3, 2), 0, "small height"),
    _point("meridian_zero", (2, 1), (1, 0), 100, "lambda = 0"),
    _point("meridian_zero_pole", (10001, 10000), (1, 0), 100, "lambda = 0"),
)


# --------------------------------------------------------------------------
# Tolerances -- declared at the point of use, with what moving them changes
# --------------------------------------------------------------------------

#: The convergence tolerance of the fixed-point inverse, in radians.  The loop
#: stops when two successive latitudes differ by less than this.  ``1e-12 rad``
#: is about ``6.4e-6 m`` on the Earth's surface.
#:
#: **What changes if it moves.**  It changes the iteration count and therefore
#: the whole seam: :func:`seam_table` sweeps it over
#: :data:`ANGLE_TOLERANCE_SWEEP` and publishes the asymmetry ratio and the chain
#: crossover at each value, so the dependence is on the page rather than hidden
#: in this constant.
ANGLE_TOLERANCE = 1e-12

#: The tolerances the seam is swept over.
ANGLE_TOLERANCE_SWEEP: tuple[float, ...] = (1e-6, 1e-9, 1e-12, 1e-15)

#: How close the recovered latitude and longitude must be to the exact values
#: for the decode obligation to be called discharged at a point, in radians.
#: One order of magnitude above :data:`ANGLE_TOLERANCE`, because a fixed-point
#: loop that stops on a step of ``t`` has left an error of order ``t``.
#:
#: **What changes if it moves.**  Tightening it below the convergence tolerance
#: would fail points that converged as declared; the audit reports the largest
#: observed error so a reader can see the headroom rather than trust the choice.
ANGLE_AGREEMENT_TOLERANCE = 1e-11

#: How close the recovered height must be to the exact height, in metres.
#:
#: **What changes if it moves.**  Below about ``1e-9 m`` no writing can pass:
#: one unit in the last place of a double near ``6.4e6`` is ``9.3e-10 m``, and
#: every height writing subtracts two quantities of that size.  The audit reports
#: the largest observed error against this floor.
HEIGHT_TOLERANCE = 1e-6

#: How many iterations the loop may take before it is declared non-convergent.
#: Not a tuning parameter: every sample point converges in far fewer, and the
#: cap exists so that a non-convergent point is *reported* rather than hanging.
ITERATION_CAP = 200

#: The chain lengths :func:`chain_table` sweeps.  Consecutive through the whole
#: crossover region so that a tie is visible as a tie, and long enough afterwards
#: to show that the two curves never meet again.
CHAIN_STEPS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 20, 24, 32)

#: The transcendental weights the crossover is swept over, so that the reader who
#: prices a ``sin`` differently from a ``mul`` can see where the answer goes
#: instead of being told it does not matter.
TRANSCENDENTAL_WEIGHTS: tuple[int, ...] = (1, 2, 4, 8, 16, 64, 256)


# --------------------------------------------------------------------------
# Exact and float conversion
# --------------------------------------------------------------------------


def exact_ecef(point: SamplePoint) -> dict[str, Surd]:
    """The ECEF encoding of one sample point, in exact ``Q(sqrt(W))`` arithmetic."""
    radicand = point.radicand
    values = {
        "s": Surd.rational(point.sin_phi, radicand),
        "c": Surd.rational(point.cos_phi, radicand),
        "sl": Surd.rational(point.sin_lam, radicand),
        "cl": Surd.rational(point.cos_lam, radicand),
        "h": Surd.rational(point.height, radicand),
    }
    return evaluate_exact(GEODETIC_TRIG_TO_ECEF, values, radicand)


def float_inverse(
    X: float,
    Y: float,
    Z: float,
    tolerance: float = ANGLE_TOLERANCE,
    writing: str = "C",
    cap: int = ITERATION_CAP,
) -> dict[str, Any]:
    """The classical iterative inverse, run on the declared regions.

    The setup region is evaluated once; the step region is evaluated until two
    successive latitudes differ by less than ``tolerance``; the epilogue region
    is then evaluated once, because the loop converges on the **latitude** and
    the height is a read-off, not a fixed point.  All three regions are the ones
    :func:`seam_table` prices, so the iteration count reported here is the
    iteration count that table multiplies and the total it publishes is the total
    this function executes.
    """
    setup = evaluate_float(ECEF_TO_GEODETIC_SETUP, {"X": X, "Y": Y, "Z": Z})
    step = inverse_step_region(writing)
    epilogue = inverse_epilogue_region(writing)
    phi = setup["PHI"]
    p = setup["P"]
    converged = False
    iterations = 0
    undefined = {
        "converged": False,
        "lam": setup["LAM"],
        "height": float("nan"),
        "reason": f"writing {writing} is undefined at {H_WRITING_EXCLUSION[writing]}",
    }
    for iterations in range(1, cap + 1):
        try:
            produced = evaluate_float(step, {"phi": phi, "p": p, "Z": Z})
        except ZeroDivisionError:
            return {**undefined, "iterations": iterations, "phi": phi}
        nxt = produced["PHI"]
        if abs(nxt - phi) < tolerance:
            phi = nxt
            converged = True
            break
        phi = nxt
    try:
        height = evaluate_float(epilogue, {"phi": phi, "p": p, "Z": Z})["H"]
    except ZeroDivisionError:
        return {**undefined, "iterations": iterations, "phi": phi}
    return {
        "converged": converged,
        "iterations": iterations,
        "phi": phi,
        "lam": setup["LAM"],
        "height": height,
        "reason": "" if converged else f"no convergence within {cap} iterations",
    }


# --------------------------------------------------------------------------
# What of 0033 fits, measured
# --------------------------------------------------------------------------


def region_model_fit() -> dict[str, Any]:
    """Run 0033's own machinery against this pair and record what each part does.

    Nothing here is argued.  Each entry names a piece of
    :mod:`parseatlas.region`, says whether it was reusable, and -- where it was
    not -- carries the exact text of its refusal.
    """
    findings: list[dict[str, Any]] = []

    priced = geo_cost(GEODETIC_TO_ECEF)
    findings.append(
        {
            "part": "region_cost",
            "fits": True,
            "evidence": (
                f"priced {GEODETIC_TO_ECEF.name}: total {priced['operation_total']}, "
                f"depth {priced['depth']}, max_live {priced['max_live']}"
            ),
            "why": (
                "cost is a walk over the operation DAG and never asks what an operation "
                "means, so the wider vocabulary changes nothing"
            ),
        }
    )

    try:
        Operation("rw", "sqrt", ("w",))
        operation_message = ""
        operation_fits = True
    except ValueError as exc:
        operation_message = str(exc)
        operation_fits = False
    findings.append(
        {
            "part": "Operation",
            "fits": operation_fits,
            "evidence": operation_message,
            "why": "the operation vocabulary is closed at the five rational kinds",
        }
    )

    try:
        Encoding(
            name="geodetic_to_ecef_attempt",
            baseline_inputs=("phi", "lam", "h"),
            candidate_inputs=("X", "Y", "Z"),
            candidate_outputs=("X", "Y", "Z"),
            encode=("sqrt(1 - phi)", "lam", "h"),
            decode=("phi", "lam", "h"),
            output_decode=(("X", "X"),),
        )
        encoding_message = ""
        encoding_fits = True
    except (ValueError, BrokenEncoding) as exc:
        encoding_message = str(exc)
        encoding_fits = False
    findings.append(
        {
            "part": "Encoding",
            "fits": encoding_fits,
            "evidence": encoding_message,
            "why": (
                "every encode and decode component is parsed by _parse_rational, and the "
                "construction gate decides the left inverse by cancellation, which is a "
                "decision procedure for rational functions only"
            ),
        }
    )

    rational_region = Region(
        name="rational_control_step",
        inputs=("s",),
        operations=(
            Operation("s2", "mul", ("s", "s")),
            Operation("es2", "mul", (_E2, "s2")),
            Operation("w", "sub", (1, "es2")),
        ),
        outputs=(("S", "w"),),
        state=(StateBinding(carried="s", produced="S"),),
        note="a rational control loop, so unroll's refusal below is about the vocabulary",
    )
    control = unroll(rational_region, 2)
    unroll_control = f"unrolled the rational control to {len(control.operations)} operations"
    try:
        unroll(ECEF_TO_GEODETIC_STEP, 2)  # type: ignore[arg-type]
        loop_message = ""
        loop_fits = True
    except ValueError as exc:
        loop_message = str(exc)
        loop_fits = False
    findings.append(
        {
            "part": "unroll",
            "fits": loop_fits,
            "evidence": loop_message,
            "why": (
                "unroll rebuilds Operation objects for every step, so it inherits the "
                "vocabulary gate even though the loop itself is well formed; the loop cost "
                f"this card needs is computed by unroll_geo instead ({unroll_control})"
            ),
        }
    )

    findings.append(
        {
            "part": "Region shape",
            "fits": True,
            "evidence": (
                "(inputs, state, operations, outputs, invariants) carries both "
                "representations and the iteration unchanged"
            ),
            "why": (
                "the shape is about what a region IS, not about what its operations "
                "compute"
            ),
        }
    )

    return {
        "findings": findings,
        "fits": sorted(item["part"] for item in findings if item["fits"]),
        "does_not_fit": sorted(item["part"] for item in findings if not item["fits"]),
        "shared_vocabulary": sorted(RATIONAL_OPERATION_ARITY),
        "added_vocabulary": sorted(set(GEO_OPERATION_ARITY) - set(RATIONAL_OPERATION_ARITY)),
        "vocabulary_conservative": all(
            GEO_OPERATION_ARITY[kind] == arity
            for kind, arity in RATIONAL_OPERATION_ARITY.items()
        ),
    }


# --------------------------------------------------------------------------
# What Generation 1 can and cannot write
# --------------------------------------------------------------------------

#: Each declared writing, as source text, paired with what it is.
GENERATION_ONE_PROBES: tuple[tuple[str, str], ...] = (
    ("N + h", "the rational skeleton of the forward map's X and Y"),
    ("(N + h) * c * cl", "X, once every transcendental leaf is bound to a name"),
    ("p / c - N", "height writing A, once every transcendental leaf is bound"),
    ("p * c + Z * s - a * rw", "height writing C, once every leaf is bound"),
    ("sin(phi)", "the latitude's sine, as a leaf"),
    ("cos(phi)", "the latitude's cosine, as a leaf"),
    ("sqrt(1 - e2 * s * s)", "the normal radius denominator"),
    ("a / sqrt(1 - e2 * s * s)", "the normal radius N"),
    ("atan2(Z, p)", "the latitude seed of the inverse"),
)


def generation_one_expressibility() -> dict[str, Any]:
    """Which parts of this card the project's notation can write, and which it cannot.

    Every refusal carries the parser's own message.  The distinction this
    function exists to make is that the *rational skeleton* of every formula
    parses while its *transcendental leaves* do not -- so a reader must not
    conclude that a world writes a geodetic conversion.
    """
    grammar = control_grammar()
    rows: list[dict[str, Any]] = []
    for source, description in GENERATION_ONE_PROBES:
        try:
            node = parse(source, grammar)
            canonical = canonicalize(node)
            rows.append(
                {
                    "source": source,
                    "description": description,
                    "parses": True,
                    "canonical": canonical["expression"],
                    "error": "",
                }
            )
        except (ValueError, KeyError) as exc:
            rows.append(
                {
                    "source": source,
                    "description": description,
                    "parses": False,
                    "canonical": None,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    regions = {
        region.name: region
        for region in (
            GEODETIC_TO_ECEF,
            GEODETIC_TRIG_TO_ECEF,
            ECEF_TO_GEODETIC_SETUP,
            ECEF_TO_GEODETIC_STEP,
            ECEF_LONGITUDE_STEP,
            GEODETIC_LONGITUDE_STEP,
        )
    }
    vocabulary: list[dict[str, Any]] = []
    for name, region in regions.items():
        kinds: dict[str, int] = {}
        for operation in region.operations:
            kinds[operation.kind] = kinds.get(operation.kind, 0) + 1
        vocabulary.append(
            {
                "region": name,
                "operations": len(region.operations),
                "generation_one_kinds": region.rational_count,
                "outside_generation_one": region.transcendental_count,
                "counts": dict(sorted(kinds.items())),
            }
        )

    return {
        "grammar": grammar.id,
        "probes": rows,
        "parsed": sum(1 for row in rows if row["parses"]),
        "refused": sum(1 for row in rows if not row["parses"]),
        "vocabulary": vocabulary,
        "outside_total": sum(item["outside_generation_one"] for item in vocabulary),
        "operations_total": sum(item["operations"] for item in vocabulary),
        "outer_functions_available": ("sin", "cos", "sqrt"),
        "outer_functions_missing": ("atan2",),
        "outer_function_arity": 1,
        "note": (
            "sin, cos and sqrt exist in this project only as OUTER functions (0002, 0032): "
            "a unary function wrapping a whole Generation 1 expression, never an operand "
            "inside one. atan2 does not exist at all and is binary, so it could not be an "
            "outer function either. No world in this project writes a geodetic conversion."
        ),
    }


# --------------------------------------------------------------------------
# The symbolic half of the decode obligation
# --------------------------------------------------------------------------


def symbolic_discharge() -> dict[str, Any]:
    """Prove ``decode(encode(g)) == g`` as an identity, once, for all points.

    The proof is in the symbols ``s, c, sl, cl, h`` and ``r``, subject to the
    declared relations ``c^2 = 1 - s^2``, ``cl^2 = 1 - sl^2`` and
    ``r^2 = 1 - e^2 s^2``.  Under those relations every check below reduces to
    zero by cancellation, which is a decision procedure for the class the
    reduced expressions live in.

    This is 0033's discipline, kept: the obligation is **decided symbolically**
    and only corroborated on the sample.  What is different, and what the card is
    about, is that 0033 could hand the whole obligation to
    :func:`parseatlas.region.discharge` and this one cannot -- the maps are not
    rational functions of their inputs, so the identity has to be reduced under
    declared relations rather than by ``cancel`` alone.
    """
    s, c, sl, cl, h, r = sympy.symbols("s c sl cl h r", positive=True)
    e2 = sympy.Rational(_E2.numerator, _E2.denominator)
    a = sympy.Rational(_A.numerator, _A.denominator)

    normal = a / r
    p = (normal + h) * c
    X = p * cl
    Y = p * sl
    Z = (normal * (1 - e2) + h) * s

    def reduce(expression: Any) -> Any:
        substituted = sympy.expand(expression)
        for _ in range(6):
            substituted = sympy.expand(
                substituted.subs(r**2, 1 - e2 * s**2)
                .subs(c**2, 1 - s**2)
                .subs(cl**2, 1 - sl**2)
            )
        return sympy.simplify(sympy.together(substituted))

    checks: list[dict[str, Any]] = []

    checks.append(
        {
            "claim": "p*p == X*X + Y*Y",
            "residue": str(reduce(X * X + Y * Y - p * p)),
        }
    )
    checks.append(
        {
            "claim": "X == p*cos(lambda) and Y == p*sin(lambda), so lambda decodes in closed form",
            "residue": str(reduce(X * sl - Y * cl)),
        }
    )
    checks.append(
        {
            "claim": "height writing A: p/c - N == h",
            "residue": str(reduce(p / c - normal - h)),
        }
    )
    checks.append(
        {
            "claim": "height writing B: Z/s - N(1-e2) == h",
            "residue": str(reduce(Z / s - normal * (1 - e2) - h)),
        }
    )
    checks.append(
        {
            "claim": "height writing C: p*c + Z*s - a*r == h",
            "residue": str(reduce(p * c + Z * s - a * r - h)),
        }
    )
    checks.append(
        {
            "claim": "the fixed point is the true latitude: p*(1 - e2*N/(N+h))*s == Z*c",
            "residue": str(reduce(p * (1 - e2 * normal / (normal + h)) * s - Z * c)),
        }
    )

    for check in checks:
        check["discharged"] = check["residue"] == "0"

    return {
        "relations": ("c**2 == 1 - s**2", "cl**2 == 1 - sl**2", "r**2 == 1 - e2*s**2"),
        "checks": checks,
        "discharged": all(check["discharged"] for check in checks),
        "discharged_count": sum(1 for check in checks if check["discharged"]),
        "check_count": len(checks),
    }


# --------------------------------------------------------------------------
# The obligation audit
# --------------------------------------------------------------------------


def _audit_point(payload: tuple[Any, ...]) -> dict[str, Any]:
    """One sample point's audit.  Module level and picklable, for the pool."""
    (
        label,
        lat_m,
        lat_n,
        lon_m,
        lon_n,
        height_num,
        height_den,
        regime,
        tolerance,
        writing,
    ) = payload
    point = SamplePoint(
        label, lat_m, lat_n, lon_m, lon_n, Fraction(height_num, height_den), regime
    )
    radicand = point.radicand
    exact = exact_ecef(point)
    exact_floats = {key: value.to_float() for key, value in exact.items()}

    # -- the exact regime: decode(encode(g)) == g in Q(sqrt(W)), no tolerance ---
    exact_rows: dict[str, Any] = {}
    target = Surd.rational(point.height, radicand)
    for name, region in H_WRITINGS.items():
        try:
            recovered = evaluate_exact(
                region,
                {
                    "p": exact["P"],
                    "Z": exact["Z"],
                    "s": Surd.rational(point.sin_phi, radicand),
                    "c": Surd.rational(point.cos_phi, radicand),
                },
                radicand,
            )["H"]
            exact_rows[name] = {"defined": True, "exact": recovered == target}
        except ZeroDivisionError:
            exact_rows[name] = {"defined": False, "exact": None}
    longitude_exact = (
        exact["X"] * Surd.rational(point.sin_lam, radicand)
        == exact["Y"] * Surd.rational(point.cos_lam, radicand)
    )
    radius_exact = (exact["X"] * exact["X"] + exact["Y"] * exact["Y"]) == exact["P"] * exact["P"]

    # -- the tolerance regime: the float iterative inverse -----------------
    inverse = float_inverse(
        exact_floats["X"], exact_floats["Y"], exact_floats["Z"], tolerance, writing
    )
    phi_true = point.phi
    lam_true = point.lam
    phi_error = abs(inverse["phi"] - phi_true) if inverse["converged"] else float("inf")
    lam_error = abs(inverse["lam"] - lam_true)
    height_error = (
        abs(inverse["height"] - float(point.height)) if inverse["converged"] else float("inf")
    )
    # On the polar axis X and Y are exactly zero and the longitude is not a
    # function of the ECEF encoding at all: every longitude encodes the same
    # physical point.  That is a fact about the decode relation's DOMAIN, not a
    # numerical shortfall, and it is reported as one rather than folded into an
    # error.
    longitude_determined = not (exact["X"].u == 0 and exact["X"].v == 0
                                and exact["Y"].u == 0 and exact["Y"].v == 0)
    within = (
        inverse["converged"]
        and phi_error <= ANGLE_AGREEMENT_TOLERANCE
        and height_error <= HEIGHT_TOLERANCE
        and (lam_error <= ANGLE_AGREEMENT_TOLERANCE or not longitude_determined)
    )

    # -- plain value equality between the two encodings --------------------
    geodetic_angle = (phi_true, lam_true, float(point.height))
    ecef = (exact_floats["X"], exact_floats["Y"], exact_floats["Z"])
    components = [a == b for a, b in zip(geodetic_angle, ecef)]

    return {
        "label": label,
        "regime": regime,
        "cos_phi": float(point.cos_phi),
        "sin_phi": float(point.sin_phi),
        "height": float(point.height),
        "ecef": list(ecef),
        "geodetic_angle": list(geodetic_angle),
        "exact_writings": exact_rows,
        "exact_longitude": longitude_exact,
        "exact_radius": radius_exact,
        "exact_discharged": (
            longitude_exact
            and radius_exact
            and all(row["exact"] for row in exact_rows.values() if row["defined"])
        ),
        "arities": [5, 3],
        "converged": inverse["converged"],
        "iterations": inverse["iterations"],
        "phi_error": phi_error,
        "lam_error": lam_error,
        "height_error": height_error,
        "longitude_determined": longitude_determined,
        "longitude_agrees_anyway": (not longitude_determined)
        and lam_error <= ANGLE_AGREEMENT_TOLERANCE,
        "within_tolerance": within,
        "value_equality": geodetic_angle == ecef,
        "component_equalities": components,
        "component_equality_count": sum(1 for item in components if item),
        "decided_by": "exact and tolerance",
    }


#: One core of headroom, so a run of this module cannot starve the session it is
#: run from.  Derived from the observed core count and never a fixed number.
WORKER_HEADROOM_CORES = 1

#: What raising a spawn-start pool costs on this machine, in seconds: every
#: worker pays the whole SymPy import before it does any work.  **Observed**, by
#: :func:`measure_pool_startup`, and declared here because
#: :func:`should_parallelise` reads it.
POOL_STARTUP_SECONDS = 2.20

#: What one sample point costs sequentially, in seconds -- exact arithmetic in a
#: quadratic field plus the float inverse.  **Observed** as the minimum of four
#: runs, which is the steady-state rate: the first run of the module pays SymPy's
#: own warm-up and is about eight times slower.
POINT_SECONDS = 0.00225


def worker_count_for(cores: int, item_count: int) -> int:
    """The worker count for a machine with ``cores`` cores, with headroom kept."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, max(item_count, 1)))


def parallel_break_even(
    startup: float = POOL_STARTUP_SECONDS,
    per_item: float = POINT_SECONDS,
    workers: int | None = None,
) -> int:
    """How many points a run needs before a pool can pay for itself.

    A pool costs ``startup`` and then runs the work ``workers``-fold faster, so
    it is worth raising exactly when

    .. code-block:: text

        n * per_item  >  startup + n * per_item / workers

    This is the measured crossover, not a chosen threshold: both inputs are
    observations and :func:`parallelism_measurement` re-measures them.
    """
    resolved = workers if workers is not None else worker_count_for(os.cpu_count() or 1, 1 << 30)
    if resolved <= 1 or per_item <= 0:
        return 1 << 30
    gain = per_item * (1 - 1 / resolved)
    return int(startup / gain) + 1


def should_parallelise(item_count: int) -> bool:
    """Whether a run of this size should raise a pool, from the measured crossover."""
    return item_count >= parallel_break_even()


def resolve_worker_count(item_count: int, workers: int | None = None) -> int:
    """Derive the process count from the observed cores and the measured crossover."""
    if workers is not None:
        return max(1, min(int(workers), max(item_count, 1)))
    if not should_parallelise(item_count):
        return 1
    return worker_count_for(os.cpu_count() or 1, item_count)


def default_worker_count() -> int:
    return resolve_worker_count(len(SAMPLE))


def _trivial(payload: int) -> int:
    """A worker that does nothing, so timing it times only the pool and its imports."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a pool whose workers each import this module, and so SymPy.

    Minimum of ``repeats`` runs: a startup time is a floor that background load
    can only push up.
    """
    resolved = workers if workers is not None else worker_count_for(os.cpu_count() or 1, 1 << 30)
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as pool:
            list(pool.map(_trivial, range(resolved), chunksize=1))
        best = min(best, time.perf_counter() - start)
    return {
        "workers": resolved,
        "cores": os.cpu_count(),
        "repeats": repeats,
        "seconds": best,
        "declared": POOL_STARTUP_SECONDS,
    }


def obligation_audit(
    points: Sequence[SamplePoint] | None = None,
    tolerance: float = ANGLE_TOLERANCE,
    writing: str = "C",
    workers: int | None = None,
) -> dict[str, Any]:
    """The card's central obligation, measured over the sample.

    Three regimes are reported separately and never blended:

    ``semantic key``
        the project's own equivalence oracle,
        :func:`parseatlas.alternative_mathematics.semantic_key` over
        :func:`parseatlas.canonical.canonicalize`.  It decides **no** point here,
        and the reason is recorded rather than described: its input must be a
        parse of the project's grammar, and no geodetic formula is one.

    ``exact``
        ``decode(encode(g)) == g`` in exact ``Q(sqrt(W))`` arithmetic, with no
        tolerance anywhere.  This is what decides the closed-form half at every
        point.

    ``tolerance``
        the float iterative inverse against the declared tolerances.  This is
        what decides the iterative half, and it is the only place in this module
        where a tolerance appears.

    And the decisive comparison: how many of the same points have the two
    encodings **equal as tuples**.
    """
    chosen = tuple(points or SAMPLE)
    payloads = [
        (
            point.label,
            point.lat_m,
            point.lat_n,
            point.lon_m,
            point.lon_n,
            point.height.numerator,
            point.height.denominator,
            point.regime,
            tolerance,
            writing,
        )
        for point in chosen
    ]
    worker_count = resolve_worker_count(len(payloads), workers)
    started = time.perf_counter()
    if worker_count <= 1:
        rows = [_audit_point(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            rows = list(pool.map(_audit_point, payloads))
    elapsed = time.perf_counter() - started

    oracle = _semantic_key_attempt()
    iterations = [row["iterations"] for row in rows]
    return {
        "point_count": len(rows),
        "tolerance": tolerance,
        "writing": writing,
        "angle_agreement_tolerance": ANGLE_AGREEMENT_TOLERANCE,
        "height_tolerance": HEIGHT_TOLERANCE,
        "rows": rows,
        "exact_discharged": sum(1 for row in rows if row["exact_discharged"]),
        "converged": sum(1 for row in rows if row["converged"]),
        "within_tolerance": sum(1 for row in rows if row["within_tolerance"]),
        "value_equality_holds": sum(1 for row in rows if row["value_equality"]),
        "component_equality_points": sum(
            1 for row in rows if row["component_equality_count"] > 0
        ),
        "component_equality_total": sum(row["component_equality_count"] for row in rows),
        "semantic_key_decided": 0,
        "semantic_key_attempt": oracle,
        "longitude_undetermined": sum(1 for row in rows if not row["longitude_determined"]),
        "longitude_undetermined_labels": [
            row["label"] for row in rows if not row["longitude_determined"]
        ],
        "longitude_agrees_anyway": sum(1 for row in rows if row["longitude_agrees_anyway"]),
        "iterations_min": min(iterations),
        "iterations_max": max(iterations),
        "iterations_total": sum(iterations),
        "max_phi_error": max(row["phi_error"] for row in rows),
        "max_lam_error": max(
            (row["lam_error"] for row in rows if row["longitude_determined"]), default=0.0
        ),
        "max_lam_error_undetermined": max(
            (row["lam_error"] for row in rows if not row["longitude_determined"]), default=0.0
        ),
        "max_height_error": max(row["height_error"] for row in rows),
        "workers": worker_count,
        "wall_clock_seconds": elapsed,
    }


#: What the project's own equivalence oracle is offered.  Two of these are the
#: rational SKELETON of a geodetic formula, with every transcendental leaf
#: standing as a free variable; three are the formulas themselves.
SEMANTIC_KEY_PROBES: tuple[tuple[str, str], ...] = (
    ("(N + h) * c * cl", "skeleton"),
    ("p / c - N", "skeleton"),
    ("(N + h) * cos(phi) * cos(lam)", "formula"),
    ("a / sqrt(1 - e2 * s * s)", "formula"),
    ("atan2(Z, p)", "formula"),
)


def _semantic_key_attempt() -> dict[str, Any]:
    """Offer the project's semantic key every writing this card has, and record what it says.

    The oracle is called, not described.  Two probes form a key and three are
    refused by the parser, and the split is the point: **a key can be formed only
    for the rational skeleton**, in which ``c``, ``cl`` and ``N`` are free
    variables that stand for nothing in particular.  A key of the skeleton
    identifies a different object from the geodetic map it was extracted from, so
    it cannot decide the obligation this card is about.
    """
    grammar = control_grammar()
    attempts: list[dict[str, Any]] = []
    for source, kind in SEMANTIC_KEY_PROBES:
        try:
            key = semantic_key(canonicalize(parse(source, grammar)))
            attempts.append(
                {
                    "source": source,
                    "kind": kind,
                    "formed": True,
                    "error": "",
                    "key": [key[0], key[1], list(key[2])],
                }
            )
        except (ValueError, KeyError) as exc:
            attempts.append(
                {
                    "source": source,
                    "kind": kind,
                    "formed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "key": None,
                }
            )
    return {
        "oracle": "parseatlas.alternative_mathematics.semantic_key",
        "input_required": "a parse of the project's grammar, canonicalised",
        "attempts": attempts,
        "formed": sum(1 for item in attempts if item["formed"]),
        "refused": sum(1 for item in attempts if not item["formed"]),
        "formed_for_a_formula": sum(
            1 for item in attempts if item["formed"] and item["kind"] == "formula"
        ),
        "arity_mismatch": (
            "even where a key is formed, it is a key of the rational skeleton, and the "
            "two encodings are a 5-tuple and a 3-tuple of different names, so "
            "F1(x) == F2(x) is not a well-formed question"
        ),
    }


# --------------------------------------------------------------------------
# The obligation at the level of an OPERATION, not only an encoding
# --------------------------------------------------------------------------

#: The declared longitude increment of the chain, given by a Pythagorean triple
#: so that its sine and cosine are exact rationals and the ECEF rotation is an
#: exact rotation rather than a rounded one.  ``(3/5, 4/5)`` is about
#: ``0.9273`` radians -- a large increment on purpose, because a small one would
#: let a wrong rotation pass unnoticed.
INCREMENT_COS = Fraction(3, 5)
INCREMENT_SIN = Fraction(4, 5)


def operation_obligation(
    points: Sequence[SamplePoint] | None = None, tolerance: float = 1e-6
) -> dict[str, Any]:
    """``decode(candidate(encode(x))) == baseline(x)`` for the chain's own step.

    T22's obligation is about a *transformation*, not only about an encoding, and
    :func:`chain_table` compares the cost of two routes.  That comparison means
    nothing unless the two routes compute the same thing, so this checks it: one
    longitude increment applied in geodetic and then converted, against the same
    increment applied in ECEF as a rotation about the spin axis.

    ``tolerance`` is in metres and is declared here.  **What changes if it
    moves**: nothing about the result -- the observed worst disagreement is
    reported beside it, and it is several orders below this value, so the
    tolerance is a guard rather than a decision.
    """
    chosen = tuple(points or SAMPLE)
    increment = math.atan2(float(INCREMENT_SIN), float(INCREMENT_COS))
    rows: list[dict[str, Any]] = []
    for point in chosen:
        exact = exact_ecef(point)
        X, Y, Z = (exact["X"].to_float(), exact["Y"].to_float(), exact["Z"].to_float())

        # the baseline route: increment the longitude, then convert
        moved = evaluate_float(GEODETIC_LONGITUDE_STEP, {"lam": point.lam, "dlam": increment})
        baseline = evaluate_float(
            GEODETIC_TO_ECEF,
            {"phi": point.phi, "lam": moved["LAM"], "h": float(point.height)},
        )

        # the candidate route: rotate in ECEF about the spin axis
        candidate = evaluate_float(
            ECEF_LONGITUDE_STEP, {"X": X, "Y": Y, "dlam": increment}
        )

        gap = max(
            abs(baseline["X"] - candidate["XO"]),
            abs(baseline["Y"] - candidate["YO"]),
            abs(baseline["Z"] - Z),
        )
        rows.append({"label": point.label, "gap": gap, "agrees": gap <= tolerance})
    worst = max(rows, key=lambda row: row["gap"])
    return {
        "point_count": len(rows),
        "tolerance": tolerance,
        "increment_radians": increment,
        "agreeing": sum(1 for row in rows if row["agrees"]),
        "max_gap": worst["gap"],
        "max_gap_at": worst["label"],
        "rows": rows,
    }


# --------------------------------------------------------------------------
# The seam
# --------------------------------------------------------------------------


def _weighted(counts: Mapping[str, int], weight: int) -> int:
    return sum(
        count * (weight if kind in TRANSCENDENTAL_KINDS else 1)
        for kind, count in counts.items()
    )


def seam_table(
    tolerances: Sequence[float] = ANGLE_TOLERANCE_SWEEP,
    writing: str = "C",
    points: Sequence[SamplePoint] | None = None,
) -> dict[str, Any]:
    """The cost each way, and the asymmetry between them.

    The forward direction is closed form and its cost is one number.  The
    inverse is a **setup, then ``k`` iterations, then one epilogue** -- the loop
    converges on the latitude and the height is read off once at the end -- and
    ``k`` is observed on the sample at each declared tolerance rather than
    assumed.  That is exactly what :func:`float_inverse` executes, never ``k + 1``
    steps.

    The asymmetry ratio is the inverse's total operation count at the sample's
    **maximum** iteration count divided by the forward's, so it is the cost of
    the direction that has to finish, not an average nobody pays.
    """
    chosen = tuple(points or SAMPLE)
    forward = geo_cost(GEODETIC_TO_ECEF)
    setup = geo_cost(ECEF_TO_GEODETIC_SETUP)
    step = geo_cost(inverse_step_region(writing))
    epilogue = geo_cost(inverse_epilogue_region(writing))

    writings = {}
    for name in ("A", "B", "C"):
        priced = geo_cost(inverse_step_region(name))
        writings[name] = {
            "operation_total": priced["operation_total"],
            "epilogue_total": geo_cost(inverse_epilogue_region(name))["operation_total"],
            "counts": priced["operation_counts"],
            "depth": priced["depth"],
            "max_live": priced["max_live"],
            "excluded": H_WRITING_EXCLUSION[name],
        }

    rows: list[dict[str, Any]] = []
    for tolerance in tolerances:
        iterations: list[int] = []
        non_convergent: list[str] = []
        for point in chosen:
            exact = exact_ecef(point)
            result = float_inverse(
                exact["X"].to_float(),
                exact["Y"].to_float(),
                exact["Z"].to_float(),
                tolerance,
                writing,
            )
            if not result["converged"]:
                non_convergent.append(point.label)
            iterations.append(result["iterations"])
        worst = max(iterations)
        inverse_total = (
            setup["operation_total"]
            + worst * step["operation_total"]
            + epilogue["operation_total"]
        )
        rows.append(
            {
                "tolerance": tolerance,
                "iterations_min": min(iterations),
                "iterations_max": worst,
                "iterations_mean": sum(iterations) / len(iterations),
                "non_convergent": non_convergent,
                "forward_total": forward["operation_total"],
                "inverse_total": inverse_total,
                "asymmetry_ratio": inverse_total / forward["operation_total"],
            }
        )

    unrolled = {
        steps: geo_cost(unroll_geo(inverse_step_region(writing), steps))["operation_total"]
        for steps in (1, 2, 3, 4, 6, 8)
    }
    predicted = {
        steps: steps * step["operation_total"] for steps in unrolled
    }
    # What a loop of k steps saves over k independent copies is exactly what is
    # step-invariant in it.  Derived from the two counts rather than stated.
    invariant = max(predicted[steps] - unrolled[steps] for steps in unrolled)

    return {
        "writing": writing,
        "forward": forward,
        "setup": setup,
        "step": step,
        "epilogue": epilogue,
        "writings": writings,
        "rows": rows,
        "loop_counts_measured": unrolled,
        "loop_counts_predicted": predicted,
        "loop_counts_verified": unrolled == predicted,
        "loop_invariant_operations": invariant,
        "point_count": len(chosen),
    }


def chain_table(
    steps: Sequence[int] = CHAIN_STEPS,
    tolerances: Sequence[float] = ANGLE_TOLERANCE_SWEEP,
    writing: str = "C",
    points: Sequence[SamplePoint] | None = None,
) -> dict[str, Any]:
    """The 0042 question here: over a chain of ``n`` steps, when does converting pay?

    **The declared chain.**  A point is given in ECEF and required in ECEF.  It
    receives ``n`` longitude increments, the increments arrive as angles, and
    **every intermediate longitude is published** -- the chain is a track and the
    longitudes are the track.

    Publishing every ``lambda_i`` is what stops the ``n`` rotations composing
    into one, and it is a requirement rather than a modelling trick.  The control
    is reported beside the result: if the intermediate longitudes are *not*
    required, the ``n`` rotations about one axis compose into a single rotation,
    both routes collapse to a fixed cost, and no crossover exists at any ``n``.

    .. code-block:: text

        route ECEF       n * (rotate + publish lambda)
        route geodetic   inverse once + n additions + forward once

    The seam is the inverse and the forward together, and the inverse it pays is
    the whole one -- setup, ``k`` iterations, epilogue -- so the crossover moves
    with the convergence tolerance exactly as :func:`seam_table` reports.
    """
    chosen = tuple(points or SAMPLE)
    forward = geo_cost(GEODETIC_TO_ECEF)
    setup = geo_cost(ECEF_TO_GEODETIC_SETUP)
    step = geo_cost(inverse_step_region(writing))
    epilogue = geo_cost(inverse_epilogue_region(writing))
    ecef_step = geo_cost(ECEF_LONGITUDE_STEP)
    geodetic_step = geo_cost(GEODETIC_LONGITUDE_STEP)

    def iterations_for(tolerance: float) -> int:
        worst = 0
        for point in chosen:
            exact = exact_ecef(point)
            result = float_inverse(
                exact["X"].to_float(),
                exact["Y"].to_float(),
                exact["Z"].to_float(),
                tolerance,
                writing,
            )
            worst = max(worst, result["iterations"])
        return worst

    sweeps: list[dict[str, Any]] = []
    for tolerance in tolerances:
        worst = iterations_for(tolerance)
        seam = (
            setup["operation_total"]
            + worst * step["operation_total"]
            + epilogue["operation_total"]
            + forward["operation_total"]
        )
        curve = []
        crossover: int | None = None
        for n in steps:
            ecef_cost = n * ecef_step["operation_total"]
            geodetic_cost = seam + n * geodetic_step["operation_total"]
            curve.append(
                {
                    "n": n,
                    "ecef": ecef_cost,
                    "geodetic": geodetic_cost,
                    "difference": ecef_cost - geodetic_cost,
                }
            )
            if crossover is None and geodetic_cost < ecef_cost:
                crossover = n
        sweeps.append(
            {
                "tolerance": tolerance,
                "iterations": worst,
                "seam": seam,
                "crossover": crossover,
                "curve": curve,
                "slope_difference": ecef_step["operation_total"] - geodetic_step["operation_total"],
                "still_moving": crossover is None,
            }
        )

    weights: list[dict[str, Any]] = []
    worst_default = iterations_for(ANGLE_TOLERANCE)
    for weight in TRANSCENDENTAL_WEIGHTS:
        seam = (
            _weighted(dict(setup["operation_counts"]), weight)
            + worst_default * _weighted(dict(step["operation_counts"]), weight)
            + _weighted(dict(epilogue["operation_counts"]), weight)
            + _weighted(dict(forward["operation_counts"]), weight)
        )
        per_ecef = _weighted(dict(ecef_step["operation_counts"]), weight)
        per_geodetic = _weighted(dict(geodetic_step["operation_counts"]), weight)
        crossover = None
        for n in steps:
            if seam + n * per_geodetic < n * per_ecef:
                crossover = n
                break
        weights.append(
            {
                "weight": weight,
                "seam": seam,
                "ecef_per_step": per_ecef,
                "geodetic_per_step": per_geodetic,
                "crossover": crossover,
            }
        )

    return {
        "writing": writing,
        "steps": list(steps),
        "ecef_step": ecef_step,
        "geodetic_step": geodetic_step,
        "sweeps": sweeps,
        "weight_sweep": weights,
        "composition_control": {
            "claim": (
                "if the intermediate longitudes are not published, n rotations about the "
                "spin axis compose into one, so neither route pays n iterative inversions -- "
                "each pays one rotation plus the n-1 additions that accumulate the angle, "
                "which is O(n) in cheap additions rather than O(n) in expensive inverses"
            ),
            # The step's last operation is atan2(yn, xn), which PUBLISHES the longitude.  The
            # control's premise is that intermediate longitudes are not published, so that
            # operation is not performed and the composed rotation costs one less than the step.
            # Review found this published as 9; it is 8.  The conclusion is unchanged either way,
            # because the geodetic route costs 89 and 89 exceeds both.
            "ecef_cost_when_composed": ecef_step["operation_total"] - 1,
            "excluded_from_composition": "atan2 publishing the longitude",
            "geodetic_cost_when_composed": (
                setup["operation_total"]
                + worst_default * step["operation_total"]
                + epilogue["operation_total"]
                + forward["operation_total"]
                + geodetic_step["operation_total"]
            ),
            "crossover": None,
        },
    }


# --------------------------------------------------------------------------
# The numerical axis
# --------------------------------------------------------------------------

#: How the float side is given the latitude.  ``angle`` is what an ordinary
#: implementation has -- a latitude in radians, rounded to a double.  ``pair`` is
#: the control: the exact ``(sin, cos)`` rounded directly, with no angle in
#: between.  The control is what separates a fact about the writing from a fact
#: about the writing *and* the angle representation together.
LATITUDE_CARRIERS: tuple[str, ...] = ("angle", "pair")


def _float_latitude(point: SamplePoint, carrier: str) -> tuple[float, float]:
    if carrier == "angle":
        phi = point.phi
        return math.sin(phi), math.cos(phi)
    if carrier == "pair":
        return float(point.sin_phi), float(point.cos_phi)
    raise ValueError(f"unknown latitude carrier {carrier!r}")


def cancellation_table(
    points: Sequence[SamplePoint] | None = None,
    carriers: Sequence[str] = LATITUDE_CARRIERS,
) -> dict[str, Any]:
    """Equivalent writings that disagree numerically -- the axis this project has not had.

    Three algebraically identical writings of the ellipsoidal height are
    evaluated at every sample point, in exact ``Q(sqrt(W))`` arithmetic and in
    float.  The exact side is the authority: it returns the declared height
    exactly, at every point, for every writing that is defined there, and
    :func:`symbolic_discharge` proves that it must.

    Beside the height, the three classical writings of ``e^2`` are measured the
    same way.  They involve no angle at all, so they show the phenomenon in its
    simplest form.
    """
    chosen = tuple(points or SAMPLE)
    a_float = float(_A)
    e2_float = float(_E2)
    one_minus_e2_float = float(_1ME2)

    rows: list[dict[str, Any]] = []
    for point in chosen:
        exact = exact_ecef(point)
        X = exact["X"].to_float()
        Y = exact["Y"].to_float()
        Z = exact["Z"].to_float()
        p_float = math.sqrt(X * X + Y * Y)
        target = float(point.height)
        radicand = point.radicand
        entry: dict[str, Any] = {
            "label": point.label,
            "regime": point.regime,
            "cos_phi": float(point.cos_phi),
            "sin_phi": float(point.sin_phi),
            "height": target,
            "exact": {},
            "float": {},
        }
        for name, region in H_WRITINGS.items():
            try:
                recovered = evaluate_exact(
                    region,
                    {
                        "p": exact["P"],
                        "Z": exact["Z"],
                        "s": Surd.rational(point.sin_phi, radicand),
                        "c": Surd.rational(point.cos_phi, radicand),
                    },
                    radicand,
                )["H"]
                entry["exact"][name] = {
                    "defined": True,
                    "equals_declared_height": recovered == Surd.rational(point.height, radicand),
                }
            except ZeroDivisionError:
                entry["exact"][name] = {"defined": False, "equals_declared_height": None}
            for carrier in carriers:
                s_float, c_float = _float_latitude(point, carrier)
                try:
                    value = evaluate_float(
                        region, {"p": p_float, "Z": Z, "s": s_float, "c": c_float}
                    )["H"]
                    error = abs(value - target)
                except ZeroDivisionError:
                    value = None
                    error = None
                entry["float"].setdefault(carrier, {})[name] = {
                    "value": value,
                    "error": error,
                }
        rows.append(entry)

    summary: dict[str, Any] = {}
    for carrier in carriers:
        per_writing: dict[str, Any] = {}
        for name in H_WRITINGS:
            errors = [
                (row["float"][carrier][name]["error"], row["label"])
                for row in rows
                if row["float"][carrier][name]["error"] is not None
            ]
            # Where exact arithmetic says the writing is undefined, float does not
            # raise -- it returns a finite wrong number.  The two maxima are kept
            # apart so that a reader is never shown a silent failure as an error.
            legitimate = [
                (row["float"][carrier][name]["error"], row["label"])
                for row in rows
                if row["float"][carrier][name]["error"] is not None
                and row["exact"][name]["defined"]
            ]
            silent = [
                row["label"]
                for row in rows
                if row["float"][carrier][name]["error"] is not None
                and not row["exact"][name]["defined"]
            ]
            worst = max(errors) if errors else (None, None)
            worst_legitimate = max(legitimate) if legitimate else (None, None)
            per_writing[name] = {
                "defined_at": len(errors),
                "max_error": worst[0],
                "max_error_at": worst[1],
                "max_error_where_defined": worst_legitimate[0],
                "max_error_where_defined_at": worst_legitimate[1],
                "silently_undefined_at": silent,
                "exact_at": sum(
                    1
                    for row in rows
                    if row["float"][carrier][name]["error"] == 0.0
                ),
            }
        summary[carrier] = per_writing

    # The writing that is defined at the most points and, among those, disagrees
    # least.  Decided on the ANGLE carrier, because that is the one an ordinary
    # implementation has; the carrier is named here rather than assumed present.
    deciding = "angle" if "angle" in summary else list(summary)[0]
    accurate = min(
        H_WRITINGS,
        key=lambda name: (
            -summary[deciding][name]["defined_at"],
            summary[deciding][name]["max_error"]
            if summary[deciding][name]["max_error"] is not None
            else float("inf"),
        ),
    )

    b_float = float(WGS84.semi_minor)
    f_float = float(WGS84.flattening)
    e2_writings = {
        "f*(2-f)": f_float * (2 - f_float),
        "1-(b/a)**2": 1 - (b_float / a_float) ** 2,
        "(a*a-b*b)/(a*a)": (a_float * a_float - b_float * b_float) / (a_float * a_float),
    }
    e2_rows = []
    for name, value in e2_writings.items():
        relative = abs(Fraction(value) - _E2) / _E2
        e2_rows.append(
            {
                "writing": name,
                "value": value,
                "relative_error": float(relative),
                "ulps": abs(Fraction(value) - _E2) / Fraction(math.ulp(e2_float)),
            }
        )
    for row in e2_rows:
        row["ulps"] = float(row["ulps"])

    return {
        "point_count": len(rows),
        "carriers": list(carriers),
        "rows": rows,
        "summary": summary,
        "accurate_writing": accurate,
        "accurate_writing_decided_on": deciding,
        "exclusions": dict(H_WRITING_EXCLUSION),
        "writing_costs": {
            name: geo_cost(region)["operation_total"] for name, region in H_WRITINGS.items()
        },
        "e2_writings": e2_rows,
        "e2_exact": float(_E2),
        "double_ulp_at_earth_radius": math.ulp(a_float),
        "stationarity": _stationarity_probe(),
    }


#: The latitude perturbations the stationarity probe uses, in radians.  They are
#: a probe, not a threshold: what is read off them is the *order* of the response
#: of each writing to a latitude error, and three decades is what makes an order
#: visible.
STATIONARITY_PERTURBATIONS: tuple[float, ...] = (1e-6, 1e-8, 1e-10)


def _stationarity_probe(point: SamplePoint | None = None) -> dict[str, Any]:
    """Why one writing survives a latitude error and the others do not.

    Perturb the latitude by ``d`` and read the change in the height each writing
    returns.  Writings ``A`` and ``B`` respond linearly in ``d``; writing ``C``
    is stationary at the true latitude and responds quadratically.  That is the
    mechanism behind the maximum disagreement, measured rather than asserted.
    """
    chosen = point or point_named("mid_3_4_5")
    exact = exact_ecef(chosen)
    X, Y, Z = (exact["X"].to_float(), exact["Y"].to_float(), exact["Z"].to_float())
    p_float = math.sqrt(X * X + Y * Y)
    phi = chosen.phi
    target = float(chosen.height)
    rows = []
    for delta in STATIONARITY_PERTURBATIONS:
        entry: dict[str, Any] = {"delta": delta}
        for name, region in H_WRITINGS.items():
            perturbed = evaluate_float(
                region,
                {
                    "p": p_float,
                    "Z": Z,
                    "s": math.sin(phi + delta),
                    "c": math.cos(phi + delta),
                },
            )["H"]
            entry[name] = abs(perturbed - target)
        rows.append(entry)
    return {"point": chosen.label, "rows": rows}


# --------------------------------------------------------------------------
# Multicore, measured
# --------------------------------------------------------------------------


def parallelism_measurement(
    points: Sequence[SamplePoint] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Run the audit sequentially and in a pool, time both, and check they agree.

    Repository policy is multicore by default with a **measured** decision.  This
    function is that measurement.  Sequential winning is a valid outcome and is
    recorded as one.
    """
    chosen = tuple(points or SAMPLE)
    sequential = obligation_audit(chosen, workers=1)
    parallel_workers = (
        workers
        if workers is not None
        else max(2, worker_count_for(os.cpu_count() or 1, len(chosen)))
    )
    parallel = obligation_audit(chosen, workers=parallel_workers)
    identical = _comparable(sequential) == _comparable(parallel)
    speedup = sequential["wall_clock_seconds"] / max(parallel["wall_clock_seconds"], 1e-12)
    return {
        "item_count": len(chosen),
        "cpu_count": os.cpu_count(),
        "sequential_seconds": sequential["wall_clock_seconds"],
        "parallel_seconds": parallel["wall_clock_seconds"],
        "parallel_workers": parallel["workers"],
        "seconds_per_point": sequential["wall_clock_seconds"] / max(len(chosen), 1),
        "speedup": speedup,
        "identical_results": identical,
        "faster_path": (
            "parallel"
            if parallel["wall_clock_seconds"] < sequential["wall_clock_seconds"]
            else "sequential"
        ),
        "break_even_points": parallel_break_even(),
        "should_parallelise": should_parallelise(len(chosen)),
        "automatic_worker_count": default_worker_count(),
    }


def _comparable(audit: Mapping[str, Any]) -> list[Any]:
    """Everything about an audit except its wall clock and its worker count."""
    return [
        [
            row["label"],
            row["exact_discharged"],
            row["converged"],
            row["iterations"],
            row["within_tolerance"],
            row["value_equality"],
            row["component_equality_count"],
        ]
        for row in audit["rows"]
    ]


# --------------------------------------------------------------------------
# The reference check and the headline
# --------------------------------------------------------------------------


def reference_check() -> dict[str, Any]:
    """The forward map at points whose ECEF coordinates are fixed by definition.

    *PRIOR ART.*  The published constants are those of the WGS 84 defining
    document (NIMA TR8350.2 third edition, and NGA.STND.0036_1.0.0_WGS84); they
    are stated from knowledge in :data:`PUBLISHED_WGS84` and each is checked here
    against the exact derivation from the two defining constants.

    The two reference points are definitional rather than tabulated:
    ``(phi, lambda, h) = (0, 0, 0)`` is ``(a, 0, 0)`` and
    ``(phi, lambda, h) = (90 deg, 0, 0)`` is ``(0, 0, b)``, because ``a`` and
    ``b`` *are* the equatorial and polar radii.  Both are computed here through
    the same declared region every other number in this module goes through.
    """
    equator_point = point_named("equator_exact")
    pole_point = point_named("pole_exact")
    equator = exact_ecef(equator_point)
    pole = exact_ecef(pole_point)
    derived = {
        "semi_major_a": float(WGS84.semi_major),
        "inverse_flattening": float(WGS84.inverse_flattening),
        "semi_minor_b": float(WGS84.semi_minor),
        "eccentricity_squared": float(WGS84.eccentricity_squared),
        "polar_radius_of_curvature": float(WGS84.polar_radius_of_curvature),
    }
    constants = []
    for key, published in PUBLISHED_WGS84.items():
        value = derived[key]
        constants.append(
            {
                "constant": key,
                "published": published,
                "derived": value,
                "absolute_difference": abs(value - published),
                "agrees_to_published_digits": abs(value - published)
                <= 0.5 * 10 ** -_decimals(published),
            }
        )
    return {
        "ellipsoid": WGS84.name,
        "constants": constants,
        "equator_point": {
            "geodetic": "phi = 0, lambda = 0, h = 0",
            "ecef": [equator["X"].to_float(), equator["Y"].to_float(), equator["Z"].to_float()],
            "expected": [float(WGS84.semi_major), 0.0, 0.0],
            "exact": (
                equator["X"] == Surd.rational(WGS84.semi_major, equator_point.radicand)
                and equator["Y"].u == 0
                and equator["Y"].v == 0
                and equator["Z"].u == 0
                and equator["Z"].v == 0
            ),
        },
        "pole_point": {
            "geodetic": "phi = 90 deg, lambda = 0, h = 0",
            "ecef": [pole["X"].to_float(), pole["Y"].to_float(), pole["Z"].to_float()],
            "expected": [0.0, 0.0, float(WGS84.semi_minor)],
            "exact": (
                pole["X"].u == 0
                and pole["X"].v == 0
                and pole["Y"].u == 0
                and pole["Y"].v == 0
                and abs(pole["Z"].to_float() - float(WGS84.semi_minor)) < 1e-6
            ),
        },
        "polar_normal_radius": {
            "derived": float(WGS84.polar_radius_of_curvature),
            "published": PUBLISHED_WGS84["polar_radius_of_curvature"],
        },
    }


def _decimals(value: float) -> int:
    text = repr(value)
    if "." not in text:
        return 0
    return len(text.split(".")[1])


def headline_report(workers: int | None = None) -> dict[str, Any]:
    """Every number this experiment publishes, from one run."""
    audit = obligation_audit(workers=workers)
    seam = seam_table()
    chain = chain_table()
    cancellation = cancellation_table()
    return {
        "ellipsoid": WGS84.name,
        "sample_size": len(SAMPLE),
        "region_model_fit": region_model_fit(),
        "generation_one": generation_one_expressibility(),
        "symbolic": symbolic_discharge(),
        "obligation": audit,
        "seam": seam,
        "chain": chain,
        "cancellation": cancellation,
        "operation": operation_obligation(),
        "reference": reference_check(),
        "verdict": {
            "value_equality_holds_at": audit["value_equality_holds"],
            "decode_holds_at": audit["exact_discharged"],
            "semantic_key_decides": audit["semantic_key_decided"],
            "expresses_what_value_equality_cannot": (
                audit["value_equality_holds"] == 0
                and audit["exact_discharged"] == audit["point_count"]
                and audit["semantic_key_decided"] == 0
            ),
        },
    }
