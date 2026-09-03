"""Negative control for representation search: what a declared axis set *cannot* reach.

Experiment 0027 established, by hand and for a single pair of programs, that a
target was outside the reach of a rewrite search not because the budget was too
small but because the *language* forbade it.  Three structural commitments did
the forbidding:

``preserve_inputs``
    the candidate is built with the reference's input list passed through
    literally, and no rule may introduce a free variable;
``preserve_outputs``
    a candidate is rejected unless its output key set equals the reference's
    exactly;
``map_equality``
    equivalence is raw value equality of the computed map, strictly stronger
    than equivalence up to a representation convention.

This module turns that one-off argument into a reusable decision procedure.
Given a reference program, a candidate target and an explicitly declared set of
commitments, :func:`reachability_verdict` decides reachability and -- the part
that matters -- names *which* commitment blocks it.  "Unreachable" on its own is
not actionable; "unreachable, and here is the single restriction standing in the
way, and here is the substitution under which the two programs do agree" is.

The decision is a **necessary** condition only.  A target that satisfies every
declared commitment is not thereby proven reachable by any particular finite
axis set; that is a separate and harder question this module does not answer.

Nothing here imports the vendored snapshot under ``case_studies/``.  The program
representation below is a deliberately small one of our own: a straight-line
sequence of assignments over named inputs, producing named outputs, evaluated
exactly over :class:`fractions.Fraction` and compared symbolically with sympy.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

import sympy
from sympy.parsing.sympy_parser import parse_expr

# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

#: The closed vocabulary of structural commitments a caller may declare.
COMMITMENTS: tuple[str, ...] = (
    "preserve_inputs",
    "preserve_outputs",
    "map_equality",
    "projective_equality",
)

#: The three commitments 0027 found in force in the vendored engine.
DEFAULT_COMMITMENTS: tuple[str, ...] = (
    "preserve_inputs",
    "preserve_outputs",
    "map_equality",
)

#: ``map_equality`` relaxed to equality up to a representation convention.
RELAXED_COMMITMENTS: tuple[str, ...] = (
    "preserve_inputs",
    "preserve_outputs",
    "projective_equality",
)

_COMMITMENT_RANK = {name: index for index, name in enumerate(COMMITMENTS)}


def normalise_commitments(commitments: Iterable[str]) -> tuple[str, ...]:
    """Validate a declared commitment set and return it in vocabulary order.

    Duplicates collapse; unknown names raise.  The closed vocabulary is the
    point: a caller asking "what if I relaxed this one?" must be asking about a
    restriction the module actually decides, not about a free-form string.
    """
    declared = tuple(commitments)
    unknown = sorted({name for name in declared if name not in _COMMITMENT_RANK})
    if unknown:
        raise ValueError(
            f"unknown commitments {unknown}; the vocabulary is {list(COMMITMENTS)}"
        )
    return tuple(sorted(set(declared), key=_COMMITMENT_RANK.__getitem__))


class UndefinedAtPoint(Exception):
    """Raised when a program's value is undefined at a sample point."""


# --------------------------------------------------------------------------
# Program representation
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Assignment:
    """One straight-line assignment ``target = expression``.

    ``expression`` is source text over the program's inputs and the targets
    assigned before it.  It must denote a rational function of those names:
    that is exactly the class the 0027 argument lives in, and it is the class
    for which equality is decidable by cancellation.
    """

    target: str
    expression: str


@dataclass(frozen=True)
class _Compiled:
    """Both forms of a compiled program: per-instruction and fully substituted."""

    input_symbols: tuple[sympy.Symbol, ...]
    local_symbols: tuple[sympy.Symbol, ...]
    local_exprs: tuple[Any, ...]
    outputs: tuple[tuple[str, Any], ...]


@dataclass(frozen=True)
class Program:
    """A straight-line program: ordered assignments over named inputs.

    ``outputs`` maps an *output key* to the name of the value it publishes.  The
    distinction matters: the output key set is what the 0027 gate compares,
    while the value name is an internal detail two equivalent programs need not
    share.

    Construction validates the property that 0027 proves about the vendored
    rewriter: every name a program mentions is either one of its declared inputs
    or a target assigned earlier.  A program cannot carry a free variable, so no
    rewrite over programs can introduce one.
    """

    name: str
    inputs: tuple[str, ...]
    body: tuple[Assignment, ...]
    outputs: tuple[tuple[str, str], ...]
    note: str = ""
    _compiled: _Compiled | None = field(
        init=False, default=None, compare=False, repr=False
    )

    def __post_init__(self) -> None:
        if not self.inputs:
            raise ValueError(f"{self.name}: a program needs at least one input")
        if len(set(self.inputs)) != len(self.inputs):
            raise ValueError(f"{self.name}: duplicated input name in {list(self.inputs)}")
        object.__setattr__(self, "_compiled", self._compile())

    # -- compilation -------------------------------------------------------

    def _compile(self) -> _Compiled:
        input_symbols = tuple(sympy.Symbol(name) for name in self.inputs)
        env: dict[str, sympy.Symbol] = dict(zip(self.inputs, input_symbols))
        substituted: dict[str, Any] = dict(zip(self.inputs, input_symbols))
        local_symbols: list[sympy.Symbol] = []
        local_exprs: list[Any] = []
        allowed = set(input_symbols)

        for assignment in self.body:
            if assignment.target in env:
                raise ValueError(
                    f"{self.name}: {assignment.target} is assigned twice "
                    "(the representation is single-assignment)"
                )
            local = parse_expr(assignment.expression, local_dict=dict(env), evaluate=True)
            bound = set(env.values())
            unbound = sorted(
                str(symbol) for symbol in local.free_symbols if symbol not in bound
            )
            if unbound:
                raise ValueError(
                    f"{self.name}: {assignment.target} uses undefined value '{unbound[0]}'"
                )
            if not local.is_rational_function(*bound):
                raise ValueError(
                    f"{self.name}: {assignment.target} is not a rational function "
                    f"of its inputs: {assignment.expression!r}"
                )
            whole = local.xreplace(
                {symbol: substituted[str(symbol)] for symbol in local.free_symbols}
            )
            if not set(whole.free_symbols) <= allowed:
                raise ValueError(f"{self.name}: {assignment.target} escaped the input scope")
            target_symbol = sympy.Symbol(assignment.target)
            env[assignment.target] = target_symbol
            substituted[assignment.target] = sympy.cancel(sympy.together(whole))
            local_symbols.append(target_symbol)
            local_exprs.append(local)

        if not self.outputs:
            raise ValueError(f"{self.name}: a program needs at least one output")
        keys = [key for key, _ in self.outputs]
        if len(set(keys)) != len(keys):
            raise ValueError(f"{self.name}: duplicated output key in {keys}")
        outputs: list[tuple[str, Any]] = []
        for key, value_name in self.outputs:
            if value_name not in substituted:
                raise ValueError(
                    f"{self.name}: output {key} uses undefined value '{value_name}'"
                )
            outputs.append((key, substituted[value_name]))

        return _Compiled(
            input_symbols=input_symbols,
            local_symbols=tuple(local_symbols),
            local_exprs=tuple(local_exprs),
            outputs=tuple(sorted(outputs, key=lambda item: item[0])),
        )

    @property
    def compiled(self) -> _Compiled:
        compiled = self._compiled
        if compiled is None:  # pragma: no cover - __post_init__ always sets it
            raise RuntimeError(f"{self.name}: program was not compiled")
        return compiled

    # -- views -------------------------------------------------------------

    @property
    def arity(self) -> int:
        return len(self.inputs)

    @property
    def output_keys(self) -> tuple[str, ...]:
        return tuple(sorted(key for key, _ in self.outputs))

    @property
    def input_symbols(self) -> tuple[sympy.Symbol, ...]:
        return self.compiled.input_symbols

    def symbolic_outputs(self) -> dict[str, Any]:
        """Each output key as a rational function of this program's own inputs."""
        return dict(self.compiled.outputs)

    def symbolic_outputs_in(self, symbols: Sequence[sympy.Symbol]) -> dict[str, Any]:
        """The same outputs, rewritten *positionally* over ``symbols``.

        Two programs with different input *names* are still two functions of the
        same ordered tuple of numbers.  Comparing them positionally is exactly
        what 0027 did when it evaluated both programs on identical tuples; the
        name difference is then decided by ``preserve_inputs``, not smuggled
        into the equivalence test.
        """
        if len(symbols) != self.arity:
            raise ValueError(
                f"{self.name}: expected {self.arity} symbols, got {len(symbols)}"
            )
        rename = dict(zip(self.compiled.input_symbols, symbols))
        return {key: expr.xreplace(rename) for key, expr in self.compiled.outputs}

    # -- exact evaluation --------------------------------------------------

    def evaluate(self, values: Sequence[Fraction]) -> dict[str, Fraction]:
        """Evaluate exactly at one point, positionally.

        Evaluation walks the assignments in order rather than substituting into
        the collapsed symbolic form, so a division that would be undefined at
        this point is reported as undefined even when it cancels symbolically.
        """
        if len(values) != self.arity:
            raise ValueError(f"{self.name}: expected {self.arity} values, got {len(values)}")
        env: dict[sympy.Symbol, Any] = {
            symbol: sympy.Rational(Fraction(value))
            for symbol, value in zip(self.compiled.input_symbols, values)
        }
        for symbol, expr in zip(self.compiled.local_symbols, self.compiled.local_exprs):
            value = expr.xreplace(env)
            if not value.is_Rational:
                raise UndefinedAtPoint(f"{self.name}: {symbol} undefined at {tuple(values)}")
            env[symbol] = value
        result: dict[str, Fraction] = {}
        for key, value_name in self.outputs:
            value = env[sympy.Symbol(value_name)]
            result[key] = Fraction(int(value.p), int(value.q))
        return result


def input_signature(program: Program) -> tuple[str, ...]:
    """The frozen input list: names **in order**, so arity and position are part of it.

    Order is significant because position carries meaning: 0027's ``Z1`` against
    ``Z`` was not a cosmetic rename, the fourth and fifth slots denoted
    different objects.  A search that passes the reference's input list through
    literally cannot change this tuple at all.
    """
    return tuple(program.inputs)


def output_signature(program: Program) -> frozenset[str]:
    """The frozen output key **set**.

    Unordered on purpose: the gate 0027 read out of the vendored engine is
    ``set(candidate.outputs) != output_names``, a set comparison.  That single
    line is what forbids a candidate from publishing values it already computes.
    """
    return frozenset(key for key, _ in program.outputs)


# --------------------------------------------------------------------------
# Deterministic sample set
# --------------------------------------------------------------------------

#: Values a sample coordinate may take.  ``1`` is present so that a slice of the
#: form "one input equals 1" is actually visited by the default sample set.
VALUE_POOL: tuple[Fraction, ...] = (
    Fraction(-3),
    Fraction(-2),
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(0),
    Fraction(1, 3),
    Fraction(1),
    Fraction(3, 2),
    Fraction(2),
    Fraction(3),
    Fraction(5),
)

DEFAULT_SAMPLE_COUNT = 240
DEFAULT_SEED = 0x0028

_LCG_MULTIPLIER = 6364136223846793005
_LCG_INCREMENT = 1442695040888963407
_LCG_MODULUS = 1 << 64


def _corner_points(arity: int) -> list[tuple[Fraction, ...]]:
    """Fixed points that must be in every sample set, whatever the count."""
    zero, one, two, three = Fraction(0), Fraction(1), Fraction(2), Fraction(3)
    points = [
        tuple([zero] * arity),
        tuple([one] * arity),
        tuple([two] * arity),
    ]
    for index in range(arity):
        points.append(tuple(one if slot == index else two for slot in range(arity)))
        points.append(tuple(zero if slot == index else three for slot in range(arity)))
    return points


def sample_points(
    arity: int, count: int = DEFAULT_SAMPLE_COUNT, seed: int = DEFAULT_SEED
) -> tuple[tuple[Fraction, ...], ...]:
    """A declared, deterministic sample set of exact rational points.

    Deterministic twice over: a fixed corner block first -- the all-ones point
    and the points where a single coordinate is pinned to ``1`` or ``0``, so a
    single-input slice is always visited -- then points drawn from
    :data:`VALUE_POOL` by a fixed linear congruential sequence.  No global RNG
    is touched, so the same ``(arity, count, seed)`` yields the same set in every
    process and on every platform.

    Points are distinct, so the set cannot be larger than ``len(VALUE_POOL) **
    arity``; at arity 2 that ceiling is 121 and the sample set saturates the
    whole grid rather than reaching the requested 240.
    """
    if arity < 1:
        raise ValueError("arity must be at least 1")
    if count < 1:
        raise ValueError("count must be at least 1")
    wanted = min(count, len(VALUE_POOL) ** arity)
    seen: dict[tuple[Fraction, ...], None] = {}
    for point in _corner_points(arity):
        seen.setdefault(point, None)
        if len(seen) >= wanted:
            return tuple(seen)
    state = seed % _LCG_MODULUS
    guard = 0
    limit = 400 * wanted
    while len(seen) < wanted and guard < limit:
        coordinates = []
        for _ in range(arity):
            state = (_LCG_MULTIPLIER * state + _LCG_INCREMENT) % _LCG_MODULUS
            coordinates.append(VALUE_POOL[(state >> 17) % len(VALUE_POOL)])
        seen.setdefault(tuple(coordinates), None)
        guard += 1
    return tuple(seen)


def _resolve_samples(
    arity: int, samples: Sequence[Sequence[Fraction]] | None
) -> tuple[tuple[Fraction, ...], ...]:
    if samples is None:
        return sample_points(arity)
    return tuple(tuple(Fraction(value) for value in point) for point in samples)


# --------------------------------------------------------------------------
# Map comparison
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class MapComparison:
    """Result of comparing two programs as maps on the same ordered tuple.

    ``agreement_fraction`` is the point of the dataclass.  A target that agrees
    with the reference only on a lower-dimensional slice is not merely
    "rejected"; it is rejected *with a number* that says how much of the sample
    set it survives, which is what distinguishes a near miss from an unrelated
    program.
    """

    reference: str
    candidate: str
    comparable: bool
    shared_keys: tuple[str, ...]
    reference_only_keys: tuple[str, ...]
    candidate_only_keys: tuple[str, ...]
    positional_rename: tuple[tuple[str, str], ...]
    sample_count: int
    defined_count: int
    agreement_count: int
    agreement_fraction: Fraction | None
    symbolic_equal: bool | None
    equal: bool
    symbolic_sample_conflict: bool
    disagreement_examples: tuple[tuple[tuple[str, ...], str, str, str], ...]
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "candidate": self.candidate,
            "comparable": self.comparable,
            "shared_keys": list(self.shared_keys),
            "reference_only_keys": list(self.reference_only_keys),
            "candidate_only_keys": list(self.candidate_only_keys),
            "positional_rename": [list(pair) for pair in self.positional_rename],
            "sample_count": self.sample_count,
            "defined_count": self.defined_count,
            "agreement_count": self.agreement_count,
            "agreement_fraction": _fraction_text(self.agreement_fraction),
            "symbolic_equal": self.symbolic_equal,
            "equal": self.equal,
            "symbolic_sample_conflict": self.symbolic_sample_conflict,
            "disagreement_examples": [
                {"point": list(point), "key": key, "reference": want, "candidate": got}
                for point, key, want, got in self.disagreement_examples
            ],
            "reason": self.reason,
        }


def _fraction_text(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return f"{value.numerator}/{value.denominator}"


def _shared_keys(reference: Program, candidate: Program) -> tuple[str, ...]:
    return tuple(sorted(set(reference.output_keys) & set(candidate.output_keys)))


def _is_zero(expr: Any) -> bool:
    return sympy.cancel(sympy.together(expr)) == 0


def map_equal(
    reference: Program,
    candidate: Program,
    samples: Sequence[Sequence[Fraction]] | None = None,
    max_examples: int = 3,
) -> MapComparison:
    """Exact equality of the computed maps, on the sample set and symbolically.

    Two decisions are baked in, and both are what make "blocked by exactly one
    commitment" a meaningful statement.

    First, the comparison runs over the **shared** output keys only.  Whether
    the candidate publishes extra keys is the business of ``preserve_outputs``;
    folding it in here would make every output extension look like a map failure
    as well.

    Second, the comparison is **positional**.  Programs whose input lists differ
    only in naming are still compared as functions of the same ordered tuple of
    numbers; the naming difference is decided by ``preserve_inputs``.

    Sample agreement and the symbolic verdict are computed independently and
    cross-checked: if the samples all agree while cancellation says the two
    rational functions differ, ``symbolic_sample_conflict`` is set and ``equal``
    stays false.  Raw value equality is the strongest of the equivalence notions
    in play; see :func:`projective_equal` for the weaker one.
    """
    shared = _shared_keys(reference, candidate)
    reference_only = tuple(sorted(set(reference.output_keys) - set(candidate.output_keys)))
    candidate_only = tuple(sorted(set(candidate.output_keys) - set(reference.output_keys)))
    rename = (
        tuple(
            (theirs, ours)
            for ours, theirs in zip(reference.inputs, candidate.inputs)
            if ours != theirs
        )
        if reference.arity == candidate.arity
        else ()
    )

    if reference.arity != candidate.arity:
        return MapComparison(
            reference=reference.name,
            candidate=candidate.name,
            comparable=False,
            shared_keys=shared,
            reference_only_keys=reference_only,
            candidate_only_keys=candidate_only,
            positional_rename=(),
            sample_count=0,
            defined_count=0,
            agreement_count=0,
            agreement_fraction=None,
            symbolic_equal=None,
            equal=False,
            symbolic_sample_conflict=False,
            disagreement_examples=(),
            reason=(
                f"arity differs: {reference.name} takes {reference.arity} inputs, "
                f"{candidate.name} takes {candidate.arity}; the two are not maps on "
                "the same tuple and cannot be compared pointwise"
            ),
        )
    if not shared:
        return MapComparison(
            reference=reference.name,
            candidate=candidate.name,
            comparable=False,
            shared_keys=(),
            reference_only_keys=reference_only,
            candidate_only_keys=candidate_only,
            positional_rename=rename,
            sample_count=0,
            defined_count=0,
            agreement_count=0,
            agreement_fraction=None,
            symbolic_equal=None,
            equal=False,
            symbolic_sample_conflict=False,
            disagreement_examples=(),
            reason="no shared output key: there is nothing to compare",
        )

    points = _resolve_samples(reference.arity, samples)

    defined = 0
    agreed = 0
    examples: list[tuple[tuple[str, ...], str, str, str]] = []
    for point in points:
        try:
            want = reference.evaluate(point)
            got = candidate.evaluate(point)
        except UndefinedAtPoint:
            continue
        defined += 1
        mismatch = [key for key in shared if want[key] != got[key]]
        if not mismatch:
            agreed += 1
        elif len(examples) < max_examples:
            key = mismatch[0]
            examples.append(
                (tuple(str(value) for value in point), key, str(want[key]), str(got[key]))
            )

    fraction = Fraction(agreed, defined) if defined else None

    reference_outputs = reference.symbolic_outputs()
    candidate_outputs = candidate.symbolic_outputs_in(reference.input_symbols)
    symbolic_equal = all(
        _is_zero(reference_outputs[key] - candidate_outputs[key]) for key in shared
    )

    sample_equal = fraction == 1
    conflict = bool(sample_equal and not symbolic_equal)
    equal = bool(symbolic_equal and sample_equal)

    if equal:
        reason = (
            f"maps agree on all {len(shared)} shared output key(s): "
            f"{agreed}/{defined} sample points and exact cancellation"
        )
    elif conflict:
        reason = (
            "sample agreement is total but cancellation refutes equality: the sample "
            "set does not separate these two rational functions"
        )
    else:
        reason = (
            f"maps differ: agreement {agreed}/{defined} on the sample set, "
            f"symbolic equality {symbolic_equal}"
        )

    return MapComparison(
        reference=reference.name,
        candidate=candidate.name,
        comparable=True,
        shared_keys=shared,
        reference_only_keys=reference_only,
        candidate_only_keys=candidate_only,
        positional_rename=rename,
        sample_count=len(points),
        defined_count=defined,
        agreement_count=agreed,
        agreement_fraction=fraction,
        symbolic_equal=symbolic_equal,
        equal=equal,
        symbolic_sample_conflict=conflict,
        disagreement_examples=tuple(examples),
        reason=reason,
    )


# --------------------------------------------------------------------------
# Projective (scaling-convention) comparison
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ProjectiveComparison:
    """Equality up to a single nonzero scale per point, under declared weights."""

    reference: str
    candidate: str
    comparable: bool
    shared_keys: tuple[str, ...]
    weights: tuple[tuple[str, int], ...]
    scale_key: str | None
    scale_expression: str | None
    scale_is_constant: bool | None
    sample_count: int
    defined_count: int
    undetermined_count: int
    agreement_count: int
    agreement_fraction: Fraction | None
    symbolic_equal: bool | None
    equal: bool
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "candidate": self.candidate,
            "comparable": self.comparable,
            "shared_keys": list(self.shared_keys),
            "weights": dict(self.weights),
            "scale_key": self.scale_key,
            "scale_expression": self.scale_expression,
            "scale_is_constant": self.scale_is_constant,
            "sample_count": self.sample_count,
            "defined_count": self.defined_count,
            "undetermined_count": self.undetermined_count,
            "agreement_count": self.agreement_count,
            "agreement_fraction": _fraction_text(self.agreement_fraction),
            "symbolic_equal": self.symbolic_equal,
            "equal": self.equal,
            "reason": self.reason,
        }


def projective_equal(
    reference: Program,
    candidate: Program,
    samples: Sequence[Sequence[Fraction]] | None = None,
    weights: Mapping[str, int] | None = None,
) -> ProjectiveComparison:
    """Equality up to a representation convention: the declared weaker relation.

    The candidate is accepted when there is a single nonzero scale ``L``, one per
    point, with ``candidate[k] == L**w_k * reference[k]`` for every shared key
    ``k``.  ``weights`` declares ``w_k`` and defaults to ``1`` everywhere, which
    is plain homogeneous scaling; a weighted grading such as the Jacobian
    ``(L**2 X : L**3 Y : L Z)`` of 0027 is expressed by passing those exponents.

    ``L`` is read off one shared key of weight ``1`` and then verified against
    every other key.  When no shared key has weight ``1`` the scale cannot be
    extracted by division alone; the comparison then falls back to the
    cross-multiplied weighted test, which is necessary but not sufficient, and
    ``scale_key`` is reported as ``None`` so a caller can see which test ran.

    A sample point at which no scale can be read off -- every weight-one key has
    a vanishing reference value -- is counted as *undetermined* rather than as a
    disagreement, and is excluded from the agreement fraction.  Silently scoring
    those points as failures would understate a genuinely equal pair.
    """
    shared = _shared_keys(reference, candidate)
    weight_map = {key: 1 for key in shared}
    if weights is not None:
        for key, weight in weights.items():
            if key in weight_map:
                if weight < 1:
                    raise ValueError(f"weight for {key} must be at least 1")
                weight_map[key] = int(weight)
    weight_pairs = tuple(sorted(weight_map.items()))

    if reference.arity != candidate.arity or not shared:
        return ProjectiveComparison(
            reference=reference.name,
            candidate=candidate.name,
            comparable=False,
            shared_keys=shared,
            weights=weight_pairs,
            scale_key=None,
            scale_expression=None,
            scale_is_constant=None,
            sample_count=0,
            defined_count=0,
            undetermined_count=0,
            agreement_count=0,
            agreement_fraction=None,
            symbolic_equal=None,
            equal=False,
            reason=(
                "not comparable: arity or shared output keys differ, so no single "
                "scale relation can be stated"
            ),
        )

    want = reference.symbolic_outputs()
    got = candidate.symbolic_outputs_in(reference.input_symbols)

    scale_key = next(
        (key for key in shared if weight_map[key] == 1 and not _is_zero(want[key])), None
    )
    if scale_key is not None:
        scale = sympy.cancel(sympy.together(got[scale_key] / want[scale_key]))
        symbolic_equal = bool(
            not _is_zero(scale)
            and all(
                _is_zero(got[key] - scale ** weight_map[key] * want[key]) for key in shared
            )
        )
        scale_text: str | None = str(scale)
        scale_constant: bool | None = not scale.free_symbols
    else:
        scale_text = None
        scale_constant = None
        symbolic_equal = all(
            _is_zero(
                got[left] ** weight_map[right] * want[right] ** weight_map[left]
                - got[right] ** weight_map[left] * want[left] ** weight_map[right]
            )
            for index, left in enumerate(shared)
            for right in shared[index + 1 :]
        )

    points = _resolve_samples(reference.arity, samples)
    defined = 0
    undetermined = 0
    agreed = 0
    for point in points:
        try:
            reference_values = reference.evaluate(point)
            candidate_values = candidate.evaluate(point)
        except UndefinedAtPoint:
            continue
        defined += 1
        status = _point_projective_status(
            reference_values, candidate_values, shared, weight_map
        )
        if status == "undetermined":
            undetermined += 1
        elif status == "agree":
            agreed += 1

    decided = defined - undetermined
    fraction = Fraction(agreed, decided) if decided else None
    equal = bool(symbolic_equal and (fraction is None or fraction == 1))
    if equal and fraction is None:
        reason = (
            "cancellation says the two are equal up to scale, but no sample point "
            "could fix a scale, so the sample set adds nothing here"
        )
    elif equal and scale_text is not None:
        reason = f"equal up to the scale L = {scale_text}"
    elif equal:
        reason = "equal under the cross-multiplied weighted test (necessary, not sufficient)"
    else:
        reason = (
            f"no single scale relates the two: agreement {agreed}/{decided} "
            f"on the decided sample points, symbolic {symbolic_equal}"
        )

    return ProjectiveComparison(
        reference=reference.name,
        candidate=candidate.name,
        comparable=True,
        shared_keys=shared,
        weights=weight_pairs,
        scale_key=scale_key,
        scale_expression=scale_text,
        scale_is_constant=scale_constant,
        sample_count=len(points),
        defined_count=defined,
        undetermined_count=undetermined,
        agreement_count=agreed,
        agreement_fraction=fraction,
        symbolic_equal=symbolic_equal,
        equal=equal,
        reason=reason,
    )


def _point_projective_status(
    reference_values: Mapping[str, Fraction],
    candidate_values: Mapping[str, Fraction],
    shared: Sequence[str],
    weight_map: Mapping[str, int],
) -> str:
    """One point's verdict: ``agree``, ``disagree`` or ``undetermined``."""
    scale: Fraction | None = None
    for key in shared:
        if weight_map[key] == 1 and reference_values[key] != 0:
            scale = candidate_values[key] / reference_values[key]
            break
    if scale is not None:
        if scale == 0:
            # The candidate vanishes where the reference does not: no nonzero
            # scale can relate them here.
            return "disagree"
        agrees = all(
            candidate_values[key] == scale ** weight_map[key] * reference_values[key]
            for key in shared
        )
        return "agree" if agrees else "disagree"
    # No weight-one key carries a nonzero reference value, so no scale can be
    # divided out.  Every weight-one key must still vanish on both sides.
    if any(
        weight_map[key] == 1 and candidate_values[key] != 0 for key in shared
    ):
        return "disagree"
    if all(reference_values[key] == 0 for key in shared):
        return "agree" if all(candidate_values[key] == 0 for key in shared) else "disagree"
    return "undetermined"


# --------------------------------------------------------------------------
# Slice of agreement
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class SliceConstraint:
    """One constraint under which two unequal maps do agree.

    ``non_constant_keys`` and ``factor_degree`` are what rank one constraint
    against another; see :func:`slice_of_agreement` for the rule they feed.

    ``non_constant_keys`` are the shared output keys on which the two programs,
    restricted to this slice, still *vary*.  Because the constraint is reported
    only when every difference cancels on it, the two restricted maps are the
    same rational function there, so measuring the reference alone measures both.
    A slice with no non-constant key is one where both programs collapse to
    constants: they agree because neither says anything, which is the least
    informative way two maps can coincide.
    """

    equation: str
    symbol: str
    solution: str
    non_constant_keys: tuple[str, ...]
    factor_degree: int
    verified_symbolically: bool
    slice_sample_count: int
    slice_agreement_count: int
    slice_agreement_fraction: Fraction | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "equation": self.equation,
            "symbol": self.symbol,
            "solution": self.solution,
            "non_constant_keys": list(self.non_constant_keys),
            "factor_degree": self.factor_degree,
            "verified_symbolically": self.verified_symbolically,
            "slice_sample_count": self.slice_sample_count,
            "slice_agreement_count": self.slice_agreement_count,
            "slice_agreement_fraction": _fraction_text(self.slice_agreement_fraction),
        }


def _informativeness_key(constraint: SliceConstraint) -> tuple[int, int, str]:
    """Sort key that puts the most informative constraint first.

    Three components, in order, each a total order on its own and the last one a
    tie-break that leaves nothing to chance:

    1. ``-len(non_constant_keys)`` -- prefer the slice on which the agreeing map
       still varies on as many shared output keys as possible.  A slice that
       flattens every output to a constant reports an agreement of collapse.
    2. ``factor_degree`` ascending -- among equally non-degenerate slices prefer
       the algebraically simpler constraint, because a linear one names a
       substitution a caller can carry out directly.
    3. ``equation`` ascending -- deterministic on ties, so repeated runs and
       separate processes report the same primary.
    """
    return (
        -len(constraint.non_constant_keys),
        constraint.factor_degree,
        constraint.equation,
    )


@dataclass(frozen=True)
class AgreementSlice:
    """The constraints under which an unequal pair of maps agrees, if any exist.

    ``constraints`` is ordered most-informative-first by
    :func:`_informativeness_key`, and ``primary`` is its head; ``common_factors``
    keeps plain canonical string order, since it lists the raw factors including
    any that could not be solved and verified.
    """

    reference: str
    candidate: str
    shared_keys: tuple[str, ...]
    common_factors: tuple[str, ...]
    constraints: tuple[SliceConstraint, ...]
    primary: SliceConstraint | None
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "candidate": self.candidate,
            "shared_keys": list(self.shared_keys),
            "common_factors": list(self.common_factors),
            "constraints": [constraint.as_dict() for constraint in self.constraints],
            "primary": self.primary.as_dict() if self.primary else None,
            "reason": self.reason,
        }


def _canonical_factor(expr: Any) -> Any:
    """Sign-normalised irreducible factor, so ``z - 1`` and ``1 - z`` are one factor."""
    expanded = sympy.expand(expr)
    symbols = sorted(expanded.free_symbols, key=str)
    if not symbols:
        return expanded
    poly = sympy.Poly(expanded, *symbols)
    return -expanded if poly.LC() < 0 else expanded


def slice_of_agreement(
    reference: Program,
    candidate: Program,
    samples: Sequence[Sequence[Fraction]] | None = None,
    max_constraints: int = 4,
) -> AgreementSlice | None:
    """Find the constraint under which two unequal maps *do* agree, if one exists.

    This is the most useful output of the module: it turns "unreachable" into
    "unreachable, and here is the substitution that would bridge it".  In the
    0027 case the two programs agreed exactly where one input equalled ``1``, and
    that single fact is what identified the missing transformation as a change of
    input encoding rather than a cleverer formula.

    Method: take the difference of the two maps on each shared output key, clear
    denominators, factor each numerator, and keep the irreducible factors common
    to *every* nonzero difference.  Each such factor is solved for one of its
    symbols and the resulting substitution is put back through all the
    differences; only constraints that make every difference cancel exactly are
    reported.

    **Which constraint is primary.**  A difference can factor into more than one
    common factor, and then more than one slice is reported, each verified and
    each true.  ``F = a*c`` against ``F = 2*a`` is the smallest example: the
    difference is ``a*(c - 2)``, so both ``a = 0`` and ``c = 2`` are genuine
    slices of agreement, but only the second one says anything.  On ``c = 2`` the
    two programs are the same non-constant map ``2*a``, and the constraint names
    the missing transformation -- freeze the second input at 2.  On ``a = 0``
    both sides collapse to the constant ``0``: they agree because neither
    computes anything.

    So ``constraints`` is ordered by :func:`_informativeness_key` -- most
    non-constant shared keys first, then lower factor degree, then equation text
    -- and ``primary`` is the head of that order rather than the alphabetically
    first factor.  All constraints found are ranked before ``max_constraints``
    truncates the list, so the cap can never discard the informative one in
    favour of a degenerate one.

    The result is a **sufficient** condition for agreement, not the full
    agreement locus.  A pair may also agree on components that no single common
    factor describes; those show up in the agreement fraction and not here.
    """
    if reference.arity != candidate.arity:
        return None
    shared = _shared_keys(reference, candidate)
    if not shared:
        return None

    want = reference.symbolic_outputs()
    got = candidate.symbolic_outputs_in(reference.input_symbols)
    differences = {
        key: sympy.cancel(sympy.together(want[key] - got[key])) for key in shared
    }
    nonzero = {key: value for key, value in differences.items() if value != 0}
    if not nonzero:
        return None

    factor_sets: list[dict[str, Any]] = []
    for value in nonzero.values():
        numerator, _ = sympy.fraction(value)
        _, factors = sympy.factor_list(sympy.expand(numerator))
        bucket: dict[str, Any] = {}
        for factor, _multiplicity in factors:
            canonical = _canonical_factor(factor)
            if not canonical.free_symbols:
                continue
            bucket[sympy.srepr(canonical)] = canonical
        factor_sets.append(bucket)

    common_keys = set(factor_sets[0])
    for bucket in factor_sets[1:]:
        common_keys &= set(bucket)
    common = sorted((factor_sets[0][key] for key in common_keys), key=str)

    restricted_source = {key: want[key] for key in shared}
    found: list[SliceConstraint] = []
    for factor in common:
        constraint = _constraint_from_factor(
            reference, candidate, factor, differences, restricted_source, samples
        )
        if constraint is not None:
            found.append(constraint)
    # Rank before truncating: the cap bounds what is reported, never which
    # constraints were considered, so it cannot drop the informative one.
    constraints = sorted(found, key=_informativeness_key)[:max_constraints]

    if not common:
        reason = (
            "the per-output differences share no common factor: there is no single "
            "constraint on the inputs that makes the two maps agree"
        )
    elif not constraints:
        reason = (
            "common factors exist but none could be solved for a single input and "
            "verified across every output"
        )
    elif len(found) == 1:
        reason = f"the maps agree exactly on the slice {constraints[0].equation}"
    else:
        omitted = len(found) - len(constraints)
        tail = f", {omitted} further slice(s) not reported" if omitted else ""
        reason = (
            f"the maps agree on each of {len(found)} slices; the primary is "
            f"{constraints[0].equation}, which leaves "
            f"{list(constraints[0].non_constant_keys)} still varying{tail}"
        )

    return AgreementSlice(
        reference=reference.name,
        candidate=candidate.name,
        shared_keys=shared,
        common_factors=tuple(str(factor) for factor in common),
        constraints=tuple(constraints),
        primary=constraints[0] if constraints else None,
        reason=reason,
    )


def _factor_degree(factor: Any) -> int:
    """Total degree of a common factor, used to rank two equally useful slices."""
    expanded = sympy.expand(factor)
    symbols = sorted(expanded.free_symbols, key=str)
    return int(sympy.Poly(expanded, *symbols).total_degree())


def _constraint_from_factor(
    reference: Program,
    candidate: Program,
    factor: Any,
    differences: Mapping[str, Any],
    restricted_source: Mapping[str, Any],
    samples: Sequence[Sequence[Fraction]] | None,
) -> SliceConstraint | None:
    for symbol in sorted(factor.free_symbols, key=str):
        try:
            solutions = sympy.solve(sympy.Eq(factor, 0), symbol, dict=False)
        except (NotImplementedError, ValueError):  # pragma: no cover - defensive
            continue
        if len(solutions) != 1:
            continue
        solution = sympy.simplify(solutions[0])
        if symbol in solution.free_symbols:  # pragma: no cover - defensive
            continue
        verified = all(
            _is_zero(value.xreplace({symbol: solution})) for value in differences.values()
        )
        if not verified:
            continue
        # Verified means both restricted maps are the same rational function on
        # this slice, so the reference alone says whether anything still varies.
        non_constant = tuple(
            key
            for key, expr in sorted(restricted_source.items())
            if sympy.cancel(
                sympy.together(expr.xreplace({symbol: solution}))
            ).free_symbols
        )
        count, agreed = _slice_agreement(reference, candidate, symbol, solution, samples)
        return SliceConstraint(
            equation=f"{factor} = 0",
            symbol=str(symbol),
            solution=f"{symbol} = {solution}",
            non_constant_keys=non_constant,
            factor_degree=_factor_degree(factor),
            verified_symbolically=True,
            slice_sample_count=count,
            slice_agreement_count=agreed,
            slice_agreement_fraction=Fraction(agreed, count) if count else None,
        )
    return None


def _slice_agreement(
    reference: Program,
    candidate: Program,
    symbol: sympy.Symbol,
    solution: Any,
    samples: Sequence[Sequence[Fraction]] | None,
) -> tuple[int, int]:
    """Empirical cross-check: project the sample set onto the slice and recompare."""
    points = _resolve_samples(reference.arity, samples)
    index = reference.input_symbols.index(symbol)
    shared = _shared_keys(reference, candidate)
    projected: dict[tuple[Fraction, ...], None] = {}
    for point in points:
        environment = {
            other: sympy.Rational(value)
            for other, value in zip(reference.input_symbols, point)
            if other != symbol
        }
        value = solution.xreplace(environment)
        if not value.is_Rational:  # pragma: no cover - defensive
            continue
        moved = list(point)
        moved[index] = Fraction(int(value.p), int(value.q))
        projected.setdefault(tuple(moved), None)
    count = 0
    agreed = 0
    for point in projected:
        try:
            want = reference.evaluate(point)
            got = candidate.evaluate(point)
        except UndefinedAtPoint:  # pragma: no cover - defensive
            continue
        count += 1
        if all(want[key] == got[key] for key in shared):
            agreed += 1
    return count, agreed


# --------------------------------------------------------------------------
# The verdict
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Evidence:
    """The three comparisons a verdict is read off, measured once.

    Separating the measurement from the verdict is what makes
    :func:`relaxation_analysis` honest as well as fast: every counterfactual is
    decided against the *same* comparison, so a difference between two verdicts
    can only come from the commitment set that was dropped and never from a
    re-measurement.
    """

    reference: str
    target: str
    map_comparison: MapComparison
    projective_comparison: ProjectiveComparison
    agreement_slice: AgreementSlice | None


def gather_evidence(
    reference: Program,
    target: Program,
    samples: Sequence[Sequence[Fraction]] | None = None,
    weights: Mapping[str, int] | None = None,
) -> Evidence:
    """Measure the two equivalence relations and the agreement slice, once."""
    comparison = map_equal(reference, target, samples)
    projective = projective_equal(reference, target, samples, weights)
    agreement = (
        slice_of_agreement(reference, target, samples)
        if comparison.comparable and not comparison.equal
        else None
    )
    return Evidence(
        reference=reference.name,
        target=target.name,
        map_comparison=comparison,
        projective_comparison=projective,
        agreement_slice=agreement,
    )


@dataclass(frozen=True)
class Verdict:
    """Structured answer to "can this axis set reach that target?"."""

    reference: str
    target: str
    commitments: tuple[str, ...]
    reachable: bool
    violated: tuple[str, ...]
    satisfied: tuple[str, ...]
    agreement_fraction: Fraction | None
    map_comparison: MapComparison
    projective_comparison: ProjectiveComparison
    agreement_slice: AgreementSlice | None
    detail: tuple[tuple[str, str], ...]

    @property
    def blocked(self) -> bool:
        return not self.reachable

    def reason_for(self, commitment: str) -> str:
        for name, text in self.detail:
            if name == commitment:
                return text
        raise KeyError(commitment)

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "target": self.target,
            "commitments": list(self.commitments),
            "reachable": self.reachable,
            "violated": list(self.violated),
            "satisfied": list(self.satisfied),
            "agreement_fraction": _fraction_text(self.agreement_fraction),
            "map_comparison": self.map_comparison.as_dict(),
            "projective_comparison": self.projective_comparison.as_dict(),
            "agreement_slice": (
                self.agreement_slice.as_dict() if self.agreement_slice else None
            ),
            "detail": dict(self.detail),
        }


def reachability_verdict(
    reference: Program,
    target: Program,
    commitments: Iterable[str] = DEFAULT_COMMITMENTS,
    samples: Sequence[Sequence[Fraction]] | None = None,
    weights: Mapping[str, int] | None = None,
    evidence: Evidence | None = None,
) -> Verdict:
    """Decide reachability against an explicitly declared commitment set.

    A target is *reachable* when it violates none of the declared commitments.
    That is a necessary condition and nothing more: it says the target is not
    excluded by the language the search fixes, not that some finite set of
    rewrite axes actually connects the two programs.

    When the target is blocked, the verdict names every violated commitment and
    carries the agreement fraction and -- when the maps are unequal but agree
    somewhere -- the slice on which they coincide.  Naming the blocking
    commitment is the whole purpose: a bare "unreachable" tells a searcher
    nothing about what to change.

    Declaring no equivalence commitment at all is legal and degenerate: the
    caller has then declared no equivalence relation, so the control has nothing
    to decide beyond the two signatures, and says so.

    ``evidence`` supplies a previously measured :class:`Evidence` and makes
    ``samples`` and ``weights`` inert; that is how :func:`relaxation_analysis`
    holds the measurement fixed while varying only the commitment set.
    """
    declared = normalise_commitments(commitments)

    if evidence is None:
        evidence = gather_evidence(reference, target, samples, weights)
    comparison = evidence.map_comparison
    projective = evidence.projective_comparison
    agreement = evidence.agreement_slice

    violated: list[str] = []
    detail: list[tuple[str, str]] = []

    for commitment in declared:
        if commitment == "preserve_inputs":
            ours = input_signature(reference)
            theirs = input_signature(target)
            if ours == theirs:
                detail.append((commitment, f"input list identical: {list(ours)}"))
            else:
                violated.append(commitment)
                detail.append(
                    (
                        commitment,
                        f"input list differs: reference {list(ours)} against target "
                        f"{list(theirs)}; the search passes the reference's list "
                        "through literally and cannot change it",
                    )
                )
        elif commitment == "preserve_outputs":
            ours_keys = output_signature(reference)
            theirs_keys = output_signature(target)
            if ours_keys == theirs_keys:
                detail.append(
                    (commitment, f"output key set identical: {sorted(ours_keys)}")
                )
            else:
                violated.append(commitment)
                detail.append(
                    (
                        commitment,
                        "output key set differs: target adds "
                        f"{sorted(theirs_keys - ours_keys)} and drops "
                        f"{sorted(ours_keys - theirs_keys)}",
                    )
                )
        elif commitment == "map_equality":
            if comparison.equal:
                detail.append((commitment, comparison.reason))
            else:
                violated.append(commitment)
                text = comparison.reason
                if agreement is not None and agreement.primary is not None:
                    text = f"{text}; they agree exactly where {agreement.primary.solution}"
                detail.append((commitment, text))
        else:  # projective_equality
            if projective.equal:
                detail.append((commitment, projective.reason))
            else:
                violated.append(commitment)
                detail.append((commitment, projective.reason))

    satisfied = tuple(name for name in declared if name not in violated)
    return Verdict(
        reference=reference.name,
        target=target.name,
        commitments=declared,
        reachable=not violated,
        violated=tuple(violated),
        satisfied=satisfied,
        agreement_fraction=comparison.agreement_fraction,
        map_comparison=comparison,
        projective_comparison=projective,
        agreement_slice=agreement,
        detail=tuple(detail),
    )


# --------------------------------------------------------------------------
# Relaxation analysis
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Relaxation:
    """One counterfactual: what happens if this commitment is dropped or weakened."""

    change: str
    commitment: str
    replacement: str | None
    remaining: tuple[str, ...]
    reachable: bool
    remaining_violations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "change": self.change,
            "commitment": self.commitment,
            "replacement": self.replacement,
            "remaining": list(self.remaining),
            "reachable": self.reachable,
            "remaining_violations": list(self.remaining_violations),
        }


@dataclass(frozen=True)
class RelaxationReport:
    """Per-commitment counterfactuals: which single restriction stands in the way."""

    reference: str
    target: str
    commitments: tuple[str, ...]
    baseline_reachable: bool
    baseline_violations: tuple[str, ...]
    drops: tuple[Relaxation, ...]
    weakening: Relaxation | None
    unblocking: tuple[str, ...]
    sole_blocker: str | None
    summary: str

    def drop_for(self, commitment: str) -> Relaxation:
        for drop in self.drops:
            if drop.commitment == commitment:
                return drop
        raise KeyError(commitment)

    def as_dict(self) -> dict[str, Any]:
        return {
            "reference": self.reference,
            "target": self.target,
            "commitments": list(self.commitments),
            "baseline_reachable": self.baseline_reachable,
            "baseline_violations": list(self.baseline_violations),
            "drops": [drop.as_dict() for drop in self.drops],
            "weakening": self.weakening.as_dict() if self.weakening else None,
            "unblocking": list(self.unblocking),
            "sole_blocker": self.sole_blocker,
            "summary": self.summary,
        }


def relaxation_analysis(
    reference: Program,
    target: Program,
    commitments: Iterable[str] = DEFAULT_COMMITMENTS,
    samples: Sequence[Sequence[Fraction]] | None = None,
    weights: Mapping[str, int] | None = None,
    evidence: Evidence | None = None,
) -> RelaxationReport:
    """For each declared commitment, report whether dropping just that one unblocks.

    This answers the question a searcher actually has.  A blocked target with a
    single unblocking commitment is one design decision away from reachable; a
    blocked target where no single drop helps -- the 0027 situation -- is not a
    tuning problem at all, and no amount of extra axes or budget will change it.

    When ``map_equality`` is declared and ``projective_equality`` is not, one
    further counterfactual is reported: replacing the strong relation with the
    weaker one, which is the concrete relaxation available to a caller who does
    not want to abandon equivalence checking altogether.

    Every counterfactual is decided against one shared :class:`Evidence`, so the
    only thing that varies between rows is the commitment set.
    """
    declared = normalise_commitments(commitments)
    if evidence is None:
        evidence = gather_evidence(reference, target, samples, weights)
    baseline = reachability_verdict(reference, target, declared, evidence=evidence)

    drops: list[Relaxation] = []
    for commitment in declared:
        remaining = tuple(name for name in declared if name != commitment)
        verdict = reachability_verdict(reference, target, remaining, evidence=evidence)
        drops.append(
            Relaxation(
                change="drop",
                commitment=commitment,
                replacement=None,
                remaining=remaining,
                reachable=verdict.reachable,
                remaining_violations=verdict.violated,
            )
        )

    weakening: Relaxation | None = None
    if "map_equality" in declared and "projective_equality" not in declared:
        remaining = normalise_commitments(
            [name for name in declared if name != "map_equality"] + ["projective_equality"]
        )
        verdict = reachability_verdict(reference, target, remaining, evidence=evidence)
        weakening = Relaxation(
            change="weaken",
            commitment="map_equality",
            replacement="projective_equality",
            remaining=remaining,
            reachable=verdict.reachable,
            remaining_violations=verdict.violated,
        )

    unblocking = tuple(drop.commitment for drop in drops if drop.reachable)
    sole = unblocking[0] if len(unblocking) == 1 else None

    if baseline.reachable:
        summary = "the target is already reachable: nothing is standing in the way"
    elif sole is not None:
        summary = f"a single commitment blocks the target: {sole}"
    elif unblocking:
        summary = f"any one of {list(unblocking)} unblocks the target on its own"
    else:
        summary = (
            f"no single relaxation helps: the target violates {list(baseline.violated)} "
            "and every one of them must go"
        )

    return RelaxationReport(
        reference=reference.name,
        target=target.name,
        commitments=declared,
        baseline_reachable=baseline.reachable,
        baseline_violations=baseline.violated,
        drops=tuple(drops),
        weakening=weakening,
        unblocking=unblocking,
        sole_blocker=sole,
        summary=summary,
    )


# --------------------------------------------------------------------------
# The validation corpus
# --------------------------------------------------------------------------

SQUARE_OF_SUM = Program(
    name="square_of_sum",
    inputs=("x", "y"),
    body=(Assignment("s", "x + y"), Assignment("v", "s*s")),
    outputs=(("V", "v"),),
    note="factored form of (x + y)**2",
)

EXPANDED_SQUARE = Program(
    name="expanded_square",
    inputs=("x", "y"),
    body=(
        Assignment("xx", "x*x"),
        Assignment("cross", "2*x*y"),
        Assignment("yy", "y*y"),
        Assignment("v", "xx + cross + yy"),
    ),
    outputs=(("V", "v"),),
    note="expanded form of the same polynomial; pure rewriting reaches it",
)

SQUARE_OF_SUM_WITH_CROSS = Program(
    name="square_of_sum_with_cross",
    inputs=("x", "y"),
    body=(Assignment("s", "x + y"), Assignment("v", "s*s"), Assignment("c", "x*y")),
    outputs=(("V", "v"), ("C", "c")),
    note="same map on V, plus one extra published value: the output-extension move",
)

SQUARE_OF_SUM_RECODED = Program(
    name="square_of_sum_recoded",
    inputs=("x", "y_bar"),
    body=(Assignment("s", "x + y_bar"), Assignment("v", "s*s")),
    outputs=(("V", "v"),),
    note="same map on the same ordered tuple, declared over a differently named input",
)

GRADED_FORM = Program(
    name="graded_form",
    inputs=("x", "y", "z"),
    body=(
        Assignment("zz", "z*z"),
        Assignment("zzz", "zz*z"),
        Assignment("u", "x*zz"),
        Assignment("s", "y*zzz"),
        Assignment("p", "u + s"),
        Assignment("q", "u - s"),
    ),
    outputs=(("P", "p"), ("Q", "q")),
    note="reference: the two inputs x, y are lifted onto the grading carried by z",
)

ERASED_PREFIX_FORM = Program(
    name="erased_prefix_form",
    inputs=("x", "y", "z"),
    body=(
        Assignment("u", "x"),
        Assignment("s", "y"),
        Assignment("p", "u + s"),
        Assignment("q", "u - s"),
    ),
    outputs=(("P", "p"), ("Q", "q")),
    note="graded_form with the lifting prefix erased; agrees with it exactly at z = 1",
)

COZ_ANALOGUE = Program(
    name="coz_analogue",
    inputs=("x", "y", "w"),
    body=(
        Assignment("u", "x"),
        Assignment("s", "y"),
        Assignment("p", "u + s"),
        Assignment("q", "u - s"),
        Assignment("r", "u*s"),
    ),
    outputs=(("P", "p"), ("Q", "q"), ("R", "r")),
    note=(
        "the 0027 target restated in ordinary algebra: different input list, "
        "larger output key set, and a different map agreeing only on a slice"
    ),
)

RATIO_REDUCED = Program(
    name="ratio_reduced",
    inputs=("x", "y"),
    body=(Assignment("num", "x + y"), Assignment("den", "x - y")),
    outputs=(("N", "num"), ("D", "den")),
    note="a pair (N : D) read up to a common scale",
)

RATIO_SCALED = Program(
    name="ratio_scaled",
    inputs=("x", "y"),
    body=(
        Assignment("k", "x*x + 1"),
        Assignment("num", "(x + y)*k"),
        Assignment("den", "(x - y)*k"),
    ),
    outputs=(("N", "num"), ("D", "den")),
    note=(
        "the same pair on a different representative: scaled by x**2 + 1, which "
        "never vanishes over the rationals"
    ),
)

PRODUCT_OF_INPUTS = Program(
    name="product_of_inputs",
    inputs=("a", "c"),
    body=(Assignment("v", "a*c"),),
    outputs=(("F", "v"),),
    note="single-output reference: the product of both inputs",
)

SECOND_INPUT_FROZEN = Program(
    name="second_input_frozen",
    inputs=("a", "c"),
    body=(Assignment("v", "2*a"),),
    outputs=(("F", "v"),),
    note=(
        "the reference specialised at c = 2: same input list, same output key, "
        "and the second input declared but never read"
    ),
)


@dataclass(frozen=True)
class CorpusPair:
    """A reference/target pair whose answer is known independently of this module.

    ``expected_violations`` is the independently known answer, written down from
    the algebra rather than read off a run.  The sweep re-derives it and reports
    agreement, so the corpus validates the control instead of merely exercising
    it.
    """

    id: str
    reference: Program
    target: Program
    commitments: tuple[str, ...]
    expected_violations: tuple[str, ...]
    expected_slice: str | None
    note: str


CORPUS: tuple[CorpusPair, ...] = (
    CorpusPair(
        id="rewriteable_polynomial",
        reference=SQUARE_OF_SUM,
        target=EXPANDED_SQUARE,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=(),
        expected_slice=None,
        note=(
            "factored against expanded form of one polynomial: same inputs, same "
            "output key, same map, so nothing in the language excludes it"
        ),
    ),
    CorpusPair(
        id="output_extension",
        reference=SQUARE_OF_SUM,
        target=SQUARE_OF_SUM_WITH_CROSS,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=("preserve_outputs",),
        expected_slice=None,
        note=(
            "the target publishes one extra value it already computes; the map on "
            "the shared key is untouched, so only the frozen output set blocks it"
        ),
    ),
    CorpusPair(
        id="input_recoding",
        reference=SQUARE_OF_SUM,
        target=SQUARE_OF_SUM_RECODED,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=("preserve_inputs",),
        expected_slice=None,
        note=(
            "the target declares a differently encoded input; as a function of the "
            "same ordered tuple it is the same map, so only the input list blocks it"
        ),
    ),
    CorpusPair(
        id="erased_prefix",
        reference=GRADED_FORM,
        target=ERASED_PREFIX_FORM,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=("map_equality",),
        expected_slice="z = 1",
        note=(
            "the structural analogue of 0027 in ordinary algebra: deleting the "
            "lifting prefix leaves a different function of the same three numbers, "
            "agreeing with the reference exactly where z = 1"
        ),
    ),
    CorpusPair(
        id="scaled_representative",
        reference=RATIO_REDUCED,
        target=RATIO_SCALED,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=("map_equality",),
        expected_slice="x = 0",
        note=(
            "genuinely the same object under a scaling convention but not the same "
            "raw map; reachable once map_equality is weakened to projective_equality"
        ),
    ),
    CorpusPair(
        id="specialised_input",
        reference=PRODUCT_OF_INPUTS,
        target=SECOND_INPUT_FROZEN,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=("map_equality",),
        expected_slice="c = 2",
        note=(
            "the one-output pair that forces a choice of primary slice: the "
            "difference a*c - 2*a factors as a*(c - 2), so both a = 0 and c = 2 "
            "are verified slices of agreement, and only c = 2 is informative -- "
            "on a = 0 both programs collapse to the constant 0"
        ),
    ),
    CorpusPair(
        id="coz_analogue",
        reference=GRADED_FORM,
        target=COZ_ANALOGUE,
        commitments=DEFAULT_COMMITMENTS,
        expected_violations=("preserve_inputs", "preserve_outputs", "map_equality"),
        expected_slice="z = 1",
        note=(
            "0027's conclusion pinned as a regression guard: all three commitments "
            "are violated at once and no single relaxation unblocks the target"
        ),
    ),
)

PAIRS_BY_ID: dict[str, CorpusPair] = {pair.id: pair for pair in CORPUS}


def corpus_pair(identifier: str) -> CorpusPair:
    """Look up one corpus pair by id."""
    try:
        return PAIRS_BY_ID[identifier]
    except KeyError:
        raise KeyError(
            f"unknown corpus pair {identifier!r}; known ids are {sorted(PAIRS_BY_ID)}"
        ) from None


def evaluate_corpus_pair(pair: CorpusPair) -> dict[str, Any]:
    """Verdict plus relaxation analysis for one pair, as plain data.

    Takes the pair itself rather than a corpus id, so a caller can evaluate a
    :class:`CorpusPair` they built from their own two programs.  Nothing here
    consults :data:`PAIRS_BY_ID`; the built-in corpus is one input among others.
    """
    evidence = gather_evidence(pair.reference, pair.target)
    verdict = reachability_verdict(
        pair.reference, pair.target, pair.commitments, evidence=evidence
    )
    relaxation = relaxation_analysis(
        pair.reference, pair.target, pair.commitments, evidence=evidence
    )
    slice_primary = (
        verdict.agreement_slice.primary if verdict.agreement_slice is not None else None
    )
    observed_slice = slice_primary.solution if slice_primary else None
    return {
        "id": pair.id,
        "note": pair.note,
        "reference": pair.reference.name,
        "target": pair.target.name,
        "commitments": list(pair.commitments),
        "expected_violations": list(pair.expected_violations),
        "expected_slice": pair.expected_slice,
        "observed_slice": observed_slice,
        "violations_match_expected": verdict.violated == pair.expected_violations,
        "slice_matches_expected": observed_slice == pair.expected_slice,
        "verdict": verdict.as_dict(),
        "relaxation": relaxation.as_dict(),
    }


def evaluate_pair(identifier: str) -> dict[str, Any]:
    """The same, for one pair of the built-in corpus looked up by id."""
    return evaluate_corpus_pair(corpus_pair(identifier))


# --------------------------------------------------------------------------
# Corpus sweep
# --------------------------------------------------------------------------


def _pool_task(pair: CorpusPair) -> dict[str, Any]:
    """Module-level pool entry point: required by the Windows ``spawn`` start method.

    The pair travels to the child by pickle rather than by id, which is what
    lets a caller's own corpus take the parallel path too: a child that only
    received an id could resolve nothing outside :data:`PAIRS_BY_ID`.
    """
    return evaluate_corpus_pair(pair)


WORKER_HEADROOM_CORES = 2
WORKER_CAP = 12

#: Pair count from which a process pool pays for itself, measured rather than
#: assumed.  Sequential against a six-worker pool on the 16-core development
#: machine, best of six runs per cell, warm parent process:
#:
#: ===========  ============  ==========  =======
#: pairs        sequential    pool of 6   speedup
#: ===========  ============  ==========  =======
#: 7             0.171 s       0.793 s      0.22x
#: 28            0.772 s       0.875 s      0.88x
#: 36            0.966 s       0.850 s      1.14x
#: 48            1.190 s       1.007 s      1.18x
#: 96            2.424 s       1.401 s      1.73x
#: 384          10.408 s       2.991 s      3.48x
#: ===========  ============  ==========  =======
#:
#: One pair is about 27 ms of sympy cancellation, while a Windows ``spawn`` child
#: pays 0.41 s to import this module before it can start any of it.  Fitting both
#: columns puts break-even at 37 pairs; the margin is still under 1.2x at 48 and
#: only opens up beyond it, so the threshold stays at 48 rather than at the
#: crossing itself.  The seven-pair corpus of this module therefore runs
#: sequentially -- a measured decision, not a habit -- and the same code takes
#: the pool unchanged as soon as a caller sweeps a corpus large enough to earn it.
PARALLEL_THRESHOLD_PAIRS = 48


def worker_count_for(cores: int, task_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``task_count`` items.

    ``WORKER_HEADROOM_CORES`` cores are left free so a sweep cannot starve an
    interactive session, ``WORKER_CAP`` bounds the spawn cost on a wide machine,
    and the count never exceeds the number of tasks there are to run.  Derived
    from the observed core count, never a hardcoded constant.
    """
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(task_count, 1)))


def resolve_workers(task_count: int, workers: int | None = None) -> int:
    """Resolve the worker count: explicit request, else the measured threshold rule."""
    if workers is not None:
        if workers < 1:
            raise ValueError("workers must be at least 1")
        return max(1, min(workers, max(task_count, 1)))
    if task_count < PARALLEL_THRESHOLD_PAIRS:
        return 1
    return worker_count_for(os.cpu_count() or 1, task_count)


def reachability_sweep(
    pairs: Iterable[CorpusPair] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Run the negative control over a corpus and check it against the known answers.

    ``pairs`` is the caller's own corpus: any iterable of :class:`CorpusPair`,
    each carrying two programs, the commitments to decide against, and the
    answer the caller already knows from the algebra.  It defaults to
    :data:`CORPUS`, the module's own validation set, so the built-in sweep is
    the no-argument call and nothing about the module has to be edited to sweep
    something else.  Ids need not be unique and need not appear in
    :data:`PAIRS_BY_ID`; ``expected_violations`` and ``expected_slice`` are what
    ``mismatched`` and ``all_match_known_answers`` are checked against, so a
    caller who does not yet know the answer writes down their conjecture and
    reads whether the module agrees.

    Work is independent per pair and CPU-bound, so the parallel path exists;
    ``workers=1`` forces the sequential one.  Parallelism changes only how fast
    the sweep runs: ``executor.map`` preserves input order and every task is a
    pure function of its pair id, so the two paths produce identical reports and
    the test suite asserts as much.

    The default follows :data:`PARALLEL_THRESHOLD_PAIRS`, whose value is a
    measurement: at the seven pairs of :data:`CORPUS` a pool is four and a half
    times slower than running them one after another, and it only starts winning
    in the high thirties.  A caller sweeping a bigger corpus gets the pool
    without changing anything.

    Caller guard: Windows uses the ``spawn`` start method, so every child
    re-imports the caller's ``__main__``.  Drive a parallel sweep from inside an
    ``if __name__ == "__main__":`` block, or pass ``workers=1``.
    """
    selected = tuple(pairs) if pairs is not None else CORPUS
    if not selected:
        raise ValueError("reachability_sweep needs at least one pair")
    resolved = resolve_workers(len(selected), workers)
    if resolved <= 1:
        execution = "sequential"
        results = [_pool_task(pair) for pair in selected]
    else:
        execution = "parallel"
        with ProcessPoolExecutor(max_workers=resolved) as executor:
            results = list(executor.map(_pool_task, selected, chunksize=1))

    reachable = [result["id"] for result in results if result["verdict"]["reachable"]]
    blocked = [result["id"] for result in results if not result["verdict"]["reachable"]]
    mismatches = [
        result["id"]
        for result in results
        if not (result["violations_match_expected"] and result["slice_matches_expected"])
    ]
    return {
        "pair_count": len(results),
        "execution": execution,
        "worker_count": resolved,
        "cpu_count": os.cpu_count(),
        "sample_count": DEFAULT_SAMPLE_COUNT,
        "commitment_vocabulary": list(COMMITMENTS),
        "reachable": reachable,
        "blocked": blocked,
        "mismatched": mismatches,
        "all_match_known_answers": not mismatches,
        "pairs": results,
    }
