"""The Region model: break a commitment, discharge a decode obligation in its place.

Experiment 0028 built a negative control that decides *which* of three structural
commitments blocks a target: ``preserve_inputs``, ``preserve_outputs`` and
``map_equality``.  Experiment 0027 established that the transformation actually
worth having broke all three at once, so the control's verdict on it is
"unreachable, and no single relaxation helps".  That verdict is correct and it is
a dead end: a search that keeps all three commitments is complete inside its own
space and blind to representation change, while a search that simply drops them
is unsound.

This module implements the third option named by ROADMAP T22.  A **Region** is
``(inputs, state, operations, outputs, invariants)``.  A candidate is a map from
one Region to another, and it buys the right to break the three commitments by
carrying a **decode relation** and discharging it:

.. code-block:: text

    decode(candidate(encode(x))) == baseline(x)

The candidate may take a different input encoding, publish extra outputs, carry
different internal state and demand preconditions the baseline did not.  What it
may not do is denote a different object at the boundary.

Scope of this first increment, stated so nothing here is read as more than it is:

* **one axis** -- deferred division on rational values, in ordinary algebra.  One
  axis is not an engine.
* **every half of discharge is decided symbolically and corroborated on the
  samples**, reported separately exactly as 0028 reports them.  Equality is
  decided by cancellation, definedness by comparing the zero sets of the
  divisors each side actually divides by, and the candidate's own precondition
  by composing it with the encode.  All three are decision procedures for the
  rational-function class this model lives in and none of them is a proof
  outside it.  The sampled half can contradict a symbolic verdict -- and says so
  when it does -- but it can never admit on its own: a definedness check decided
  by sampling admits any candidate whose extra pole sits off the sample grid,
  which is the fail-open ``NF-2026-00004`` recorded one level down in
  ``functions.py`` and the reason this module does not repeat it.
* **nothing here ranks candidates.**  :func:`region_cost` measures; it does not
  choose.  T23 names ranking as the harder half and this module does not touch
  it.

No wall-clock claim is made or supported anywhere in this module.  An operation
is one operation here; what a division costs on a machine is outside the model.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

import sympy
from sympy.parsing.sympy_parser import parse_expr

from .reachability_control import (
    VALUE_POOL,
    Assignment,
    Program,
    UndefinedAtPoint,
    reachability_verdict,
    relaxation_analysis,
    sample_points,
)

__all__ = [
    "ADVERSARIAL_SAMPLES",
    "ADVERSARIAL_STEP",
    "AXIS_CHAIN_STEPS",
    "COMMUTATIVE_KINDS",
    "DECODE_TAIL",
    "DEFAULT_LOOP_STEPS",
    "DEFERRED_ENCODING",
    "DEFERRED_STEP",
    "DISCHARGE_STEPS",
    "EAGER_STEP",
    "ENCODING_SAMPLE_COUNT",
    "IDENTITY_ENCODING",
    "IMPOSSIBLE_STEP",
    "LOOP_SYMBOL",
    "OFF_GRID_POLE_STEP",
    "OFF_GRID_PRECONDITION_STEP",
    "OBLIGATION",
    "ON_GRID_POLE_STEP",
    "OPERATION_ARITY",
    "PRODUCT_HOISTED",
    "PRODUCT_SEQUENTIAL",
    "BrokenEncoding",
    "Discharge",
    "DomainComparison",
    "Encoding",
    "EncodingCheck",
    "InvariantReport",
    "LoopCost",
    "LoopPoint",
    "Operation",
    "PreconditionReport",
    "Region",
    "RegionCost",
    "StateBinding",
    "UndefinedAtPoint",
    "adversarial_chain",
    "as_program",
    "axis_report",
    "commitment_contrast",
    "deferred_chain",
    "deferred_chain_decoded",
    "discharge",
    "domain_comparison",
    "eager_chain",
    "invariant_check",
    "precondition_check",
    "region_cost",
    "unroll",
]


#: The closed operation vocabulary.  Small on purpose: this is a research model,
#: not a compiler IR, and every kind here is one node of the operation DAG, so
#: the multiset of kinds is unambiguous rather than a function of how an
#: expression happened to be written.
OPERATION_ARITY: dict[str, int] = {"add": 2, "sub": 2, "mul": 2, "div": 2, "neg": 1}

#: Kinds whose operands may be reordered without changing the value.  Used only
#: by the loop normaliser, where two steps that compute the same thing under a
#: different operand order must collapse to one.
COMMUTATIVE_KINDS: frozenset[str] = frozenset({"add", "mul"})

Operand = str | Fraction | int


class BrokenEncoding(ValueError):
    """Raised at construction when an encoding's decode is not a left inverse.

    Deliberately a construction-time failure and not a use-time one.  An
    encoding that cannot be undone is not a weaker encoding, it is not an
    encoding, and letting one exist long enough to be passed to
    :func:`discharge` would make the obligation decidable only by accident.
    """


def _fraction_text(value: Fraction | None) -> str | None:
    if value is None:
        return None
    return f"{value.numerator}/{value.denominator}"


def _literal(value: Operand) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _literal_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"({value.numerator}/{value.denominator})"


# --------------------------------------------------------------------------
# Exact evaluation of a sympy rational function over Fraction
# --------------------------------------------------------------------------


def _exact_eval(expr: Any, environment: Mapping[str, Fraction]) -> Fraction:
    """Evaluate a rational-function sympy expression exactly over ``Fraction``.

    Written out rather than delegated to ``subs`` because every value that
    crosses a boundary in this module must be an exact rational and must fail
    loudly rather than silently becoming ``zoo`` or a float.  A negative power
    of a vanishing base raises :class:`UndefinedAtPoint`, which is what makes a
    zero denominator a *reported* point rather than a swallowed one.
    """
    if expr.is_Symbol:
        try:
            return environment[str(expr)]
        except KeyError:  # pragma: no cover - defensive
            raise ValueError(f"no value for free symbol {expr}") from None
    if expr.is_Rational:
        return Fraction(int(expr.p), int(expr.q))
    if expr.is_Add:
        total = Fraction(0)
        for term in expr.args:
            total += _exact_eval(term, environment)
        return total
    if expr.is_Mul:
        product = Fraction(1)
        for factor in expr.args:
            product *= _exact_eval(factor, environment)
        return product
    if expr.is_Pow:
        base, exponent = expr.args
        if not exponent.is_Integer:
            raise ValueError(f"non-integer exponent in {expr}")
        power = int(exponent)
        value = _exact_eval(base, environment)
        if power < 0 and value == 0:
            raise UndefinedAtPoint(f"{expr} undefined: zero base under exponent {power}")
        return value**power
    raise ValueError(f"{expr} is not a rational function of its symbols")


def _condition_holds(condition: Any, environment: Mapping[str, Fraction]) -> bool | None:
    """Decide one declared boolean condition at an exact rational point.

    ``None`` means sympy did not reduce the substituted condition to a truth
    value.  Reported rather than coerced: a condition the model cannot decide at
    a point is not a condition that failed there.
    """
    substituted = condition.xreplace(
        {sympy.Symbol(name): sympy.Rational(value) for name, value in environment.items()}
    )
    reduced = sympy.simplify(substituted)
    if reduced is sympy.true:
        return True
    if reduced is sympy.false:
        return False
    return None


def _parse_condition(text: str, names: Sequence[str], owner: str) -> Any:
    """Parse a declared condition, refusing anything but a boolean over ``names``.

    Python's ``!=`` collapses to a plain ``bool`` inside ``parse_expr``, so the
    functional forms are required: ``Ne(b, 0)``, ``Eq(x, y)``, ``And(...)``,
    ``Implies(...)``.  The restriction is worth the small inconvenience -- a
    condition that silently became ``True`` at parse time would be a declared
    precondition that is never checked.
    """
    local = {name: sympy.Symbol(name) for name in names}
    parsed = parse_expr(text, local_dict=local, evaluate=True)
    if not isinstance(parsed, sympy.logic.boolalg.Boolean):
        raise ValueError(
            f"{owner}: condition {text!r} is not a boolean; use the functional forms "
            "Eq(...), Ne(...), And(...), Implies(...)"
        )
    unknown = sorted(str(symbol) for symbol in parsed.free_symbols if str(symbol) not in local)
    if unknown:
        raise ValueError(f"{owner}: condition {text!r} mentions unknown name {unknown[0]!r}")
    return parsed


def _parse_rational(text: str, names: Sequence[str], owner: str) -> Any:
    """Parse a declared map expression, refusing free variables and non-rationals."""
    local = {name: sympy.Symbol(name) for name in names}
    parsed = parse_expr(text, local_dict=local, evaluate=True)
    unknown = sorted(str(symbol) for symbol in parsed.free_symbols if str(symbol) not in local)
    if unknown:
        raise ValueError(f"{owner}: {text!r} mentions unknown name {unknown[0]!r}")
    symbols = tuple(local.values())
    if symbols and not parsed.is_rational_function(*symbols):
        raise ValueError(f"{owner}: {text!r} is not a rational function of {list(names)}")
    return parsed


# --------------------------------------------------------------------------
# Operations and regions
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Operation:
    """One primitive operation ``target = kind(args...)``.

    An argument is either a **name** -- an input of the region or the target of
    an earlier operation -- or a **rational literal**.  Strings are always names
    and numbers are always literals, so ``"3"`` is a malformed name rather than
    an ambiguous constant.

    One operation is one DAG node of one declared kind.  That is the whole
    reason the model does not take free-form expression text: the operation
    multiset must be a property of the region, not of how somebody wrote it
    down.
    """

    target: str
    kind: str
    args: tuple[Operand, ...]

    def __post_init__(self) -> None:
        if not self.target.isidentifier():
            raise ValueError(f"{self.target!r} is not a usable value name")
        if self.kind not in OPERATION_ARITY:
            raise ValueError(
                f"{self.target}: unknown operation kind {self.kind!r}; "
                f"the vocabulary is {sorted(OPERATION_ARITY)}"
            )
        normalised = tuple(
            argument if isinstance(argument, str) else _literal(argument)
            for argument in self.args
        )
        arity = OPERATION_ARITY[self.kind]
        if len(normalised) != arity:
            raise ValueError(
                f"{self.target}: {self.kind} takes {arity} operand(s), got {len(normalised)}"
            )
        for argument in normalised:
            if isinstance(argument, str) and not argument.isidentifier():
                raise ValueError(
                    f"{self.target}: operand {argument!r} is not a name; "
                    "pass a number for a literal"
                )
        object.__setattr__(self, "args", normalised)

    @property
    def names(self) -> tuple[str, ...]:
        """The operand names, literals dropped."""
        return tuple(argument for argument in self.args if isinstance(argument, str))

    def canonical_args(self) -> tuple[Operand, ...]:
        """Operands in a canonical order for commutative kinds, as written otherwise."""
        if self.kind not in COMMUTATIVE_KINDS:
            return self.args
        return tuple(
            sorted(self.args, key=lambda item: (isinstance(item, Fraction), str(item)))
        )

    def expression_text(self) -> str:
        """This operation as source text, for the bridge to the 0028 control."""
        parts = [
            argument if isinstance(argument, str) else _literal_text(argument)
            for argument in self.args
        ]
        if self.kind == "neg":
            return f"-({parts[0]})"
        symbol = {"add": "+", "sub": "-", "mul": "*", "div": "/"}[self.kind]
        return f"({parts[0]}){symbol}({parts[1]})"


@dataclass(frozen=True)
class StateBinding:
    """One loop-carried value: input ``carried`` is refilled from output ``produced``.

    This is what makes a Region a *region* rather than one formula.  Without it
    there is no declared loop, and without a declared loop the per-step overhead
    that T23 says decides the real question is not expressible at all.
    """

    carried: str
    produced: str


@dataclass(frozen=True)
class Region:
    """``(inputs, state, operations, outputs, invariants)``.

    ``outputs`` maps an **output key** to the name of the value it publishes,
    following 0028: the key set is the boundary object's shape, while the value
    name is an internal detail two equivalent regions need not share.  Output
    keys and input names are required to be disjoint so that a declared
    invariant, which speaks about both, is never ambiguous.

    ``precondition`` is the entry condition the region demands of its inputs;
    ``invariants`` are declared relations between inputs and outputs.  Both are
    boolean sympy expressions in functional form.  Nothing is checked at
    construction beyond well-formedness -- a precondition is a claim about the
    region, and claims are measured by :func:`precondition_check` and
    :func:`invariant_check`, not asserted by a constructor.
    """

    name: str
    inputs: tuple[str, ...]
    operations: tuple[Operation, ...]
    outputs: tuple[tuple[str, str], ...]
    state: tuple[StateBinding, ...] = ()
    precondition: tuple[str, ...] = ()
    invariants: tuple[str, ...] = ()
    note: str = ""
    _cache: dict[str, Any] = field(
        default_factory=dict, compare=False, repr=False, hash=False
    )

    def __post_init__(self) -> None:
        if not self.inputs:
            raise ValueError(f"{self.name}: a region needs at least one input")
        if len(set(self.inputs)) != len(self.inputs):
            raise ValueError(f"{self.name}: duplicated input name in {list(self.inputs)}")
        for name in self.inputs:
            if not name.isidentifier():
                raise ValueError(f"{self.name}: {name!r} is not a usable input name")

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
                f"{self.name}: output key {overlap[0]!r} collides with an input name; "
                "keys and input names must be disjoint so an invariant is unambiguous"
            )
        for key, value_name in self.outputs:
            if value_name not in defined:
                raise ValueError(
                    f"{self.name}: output {key} uses undefined value {value_name!r}"
                )

        produced = {key for key, _ in self.outputs}
        seen_carried: set[str] = set()
        seen_produced: set[str] = set()
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
            if binding.carried in seen_carried or binding.produced in seen_produced:
                raise ValueError(f"{self.name}: state binding {binding} is declared twice")
            seen_carried.add(binding.carried)
            seen_produced.add(binding.produced)

        for text in self.precondition:
            _parse_condition(text, self.inputs, f"{self.name} precondition")
        for text in self.invariants:
            _parse_condition(
                text, tuple(self.inputs) + tuple(keys), f"{self.name} invariant"
            )

    # -- views -------------------------------------------------------------

    @property
    def arity(self) -> int:
        return len(self.inputs)

    @property
    def output_keys(self) -> tuple[str, ...]:
        return tuple(sorted(key for key, _ in self.outputs))

    @property
    def carried_state(self) -> int:
        """How many values the loop carries from one step to the next."""
        return len(self.state)

    @property
    def input_symbols(self) -> tuple[sympy.Symbol, ...]:
        return tuple(sympy.Symbol(name) for name in self.inputs)

    def parsed_precondition(self) -> tuple[Any, ...]:
        return tuple(
            _parse_condition(text, self.inputs, f"{self.name} precondition")
            for text in self.precondition
        )

    def parsed_invariants(self) -> tuple[tuple[str, Any], ...]:
        names = tuple(self.inputs) + tuple(key for key, _ in self.outputs)
        return tuple(
            (text, _parse_condition(text, names, f"{self.name} invariant"))
            for text in self.invariants
        )

    # -- symbolic form -----------------------------------------------------

    def symbolic_values(self) -> dict[str, Any]:
        """Every value of the region as a rational function of its own inputs."""
        cached = self._cache.get("symbolic_values")
        if cached is not None:
            return dict(cached)
        values: dict[str, Any] = {name: sympy.Symbol(name) for name in self.inputs}
        for operation in self.operations:
            operands = [
                values[argument] if isinstance(argument, str) else sympy.Rational(argument)
                for argument in operation.args
            ]
            if operation.kind == "add":
                raw = operands[0] + operands[1]
            elif operation.kind == "sub":
                raw = operands[0] - operands[1]
            elif operation.kind == "mul":
                raw = operands[0] * operands[1]
            elif operation.kind == "div":
                raw = operands[0] / operands[1]
            else:
                raw = -operands[0]
            values[operation.target] = sympy.cancel(sympy.together(raw))
        self._cache["symbolic_values"] = dict(values)
        return dict(values)

    def symbolic_outputs(self) -> dict[str, Any]:
        """Each output key as a rational function of this region's inputs."""
        values = self.symbolic_values()
        return {key: values[name] for key, name in self.outputs}

    # -- exact evaluation --------------------------------------------------

    def evaluate(self, values: Sequence[Fraction]) -> dict[str, Fraction]:
        """Evaluate exactly at one point, positionally over ``inputs``.

        The walk is over the declared operations, not over the collapsed
        symbolic form, so a division that is undefined at this point is reported
        as undefined even where it cancels symbolically.  That distinction is
        the whole content of the precondition story below: the deferred form
        does not merely postpone a division, it postpones the *failure*.
        """
        if len(values) != self.arity:
            raise ValueError(f"{self.name}: expected {self.arity} values, got {len(values)}")
        environment: dict[str, Fraction] = {
            name: Fraction(value) for name, value in zip(self.inputs, values)
        }
        for operation in self.operations:
            operands = [
                environment[argument] if isinstance(argument, str) else _literal(argument)
                for argument in operation.args
            ]
            if operation.kind == "add":
                result = operands[0] + operands[1]
            elif operation.kind == "sub":
                result = operands[0] - operands[1]
            elif operation.kind == "mul":
                result = operands[0] * operands[1]
            elif operation.kind == "div":
                if operands[1] == 0:
                    raise UndefinedAtPoint(
                        f"{self.name}: {operation.target} divides by zero at {tuple(values)}"
                    )
                result = operands[0] / operands[1]
            else:
                result = -operands[0]
            environment[operation.target] = result
        return {key: environment[name] for key, name in self.outputs}


def as_program(region: Region) -> Program:
    """Bridge a Region to the 0028 straight-line ``Program``.

    The bridge exists so the contrast this experiment is about is a *measured*
    one rather than an argued one: the very same pair is handed to
    :func:`~parseatlas.reachability_control.reachability_verdict`, which
    correctly calls it unreachable, and to :func:`discharge`, which admits it.
    """
    return Program(
        name=region.name,
        inputs=region.inputs,
        body=tuple(
            Assignment(operation.target, operation.expression_text())
            for operation in region.operations
        ),
        outputs=region.outputs,
        note=region.note,
    )


# --------------------------------------------------------------------------
# Encoding: the pair of maps, and the left-inverse gate
# --------------------------------------------------------------------------

#: Sample budget for the construction-time left-inverse check.  Declared rather
#: than inherited from 0028's 240 because every ``Encoding`` in this module is
#: built at import time, and the symbolic half of the check -- not the sampled
#: half -- is what decides acceptance.
ENCODING_SAMPLE_COUNT = 96


@dataclass(frozen=True)
class EncodingCheck:
    """What the construction-time gate measured, kept so a report can quote it."""

    left_inverse_symbolic: bool
    sample_count: int
    admissible_count: int
    agreement_count: int
    agreement_fraction: Fraction | None
    codomain_hits: int
    codomain_misses: int
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "left_inverse_symbolic": self.left_inverse_symbolic,
            "sample_count": self.sample_count,
            "admissible_count": self.admissible_count,
            "agreement_count": self.agreement_count,
            "agreement_fraction": _fraction_text(self.agreement_fraction),
            "codomain_hits": self.codomain_hits,
            "codomain_misses": self.codomain_misses,
            "failures": list(self.failures),
        }


@dataclass(frozen=True)
class Encoding:
    """A named pair of maps between a baseline input tuple and a candidate input tuple.

    ``encode`` carries a baseline tuple into the candidate's representation and
    ``decode`` carries it back.  ``output_decode`` states the same relation on
    the **boundary object**, over the candidate's output keys, because that is
    where the obligation is actually discharged: inputs and outputs of a region
    need not have the same shape, and writing one map for both would silently
    assume they do.

    Each direction carries its own declared domain.  ``domain`` restricts the
    baseline tuples the encoding claims to handle; ``codomain`` restricts the
    candidate tuples on which ``decode`` is defined.

    **The gate, applied at construction.**  A :class:`BrokenEncoding` is raised
    unless

    1. ``decode(encode(x)) == x`` holds as a rational-function identity, decided
       by cancellation;
    2. it also holds pointwise and exactly on every admissible sample point; and
    3. ``encode`` lands inside ``codomain`` on every admissible sample point --
       an encode that leaves the decode's own domain is not a usable encoding
       even where the algebra cancels.

    Condition 1 is the accept condition; conditions 2 and 3 can only reject.  A
    left inverse that holds on a proper subset of the declared domain and is
    therefore *not* a rational-function identity is refused rather than carried
    around as a conditional fact.  That is a real limit of this first increment
    and it is recorded here rather than discovered later.
    """

    name: str
    baseline_inputs: tuple[str, ...]
    candidate_inputs: tuple[str, ...]
    candidate_outputs: tuple[str, ...]
    encode: tuple[str, ...]
    decode: tuple[str, ...]
    output_decode: tuple[tuple[str, str], ...]
    domain: tuple[str, ...] = ()
    codomain: tuple[str, ...] = ()
    note: str = ""
    verification: EncodingCheck = field(init=False, compare=False, repr=False)
    _parsed: dict[str, Any] = field(
        init=False, default_factory=dict, compare=False, repr=False, hash=False
    )

    def __post_init__(self) -> None:
        if len(self.encode) != len(self.candidate_inputs):
            raise ValueError(
                f"{self.name}: encode has {len(self.encode)} component(s) for "
                f"{len(self.candidate_inputs)} candidate input(s)"
            )
        if len(self.decode) != len(self.baseline_inputs):
            raise ValueError(
                f"{self.name}: decode has {len(self.decode)} component(s) for "
                f"{len(self.baseline_inputs)} baseline input(s)"
            )
        for label, names in (
            ("baseline input", self.baseline_inputs),
            ("candidate input", self.candidate_inputs),
            ("candidate output", self.candidate_outputs),
        ):
            if len(set(names)) != len(names):
                raise ValueError(f"{self.name}: duplicated {label} name in {list(names)}")
        keys = [key for key, _ in self.output_decode]
        if len(set(keys)) != len(keys):
            raise ValueError(f"{self.name}: duplicated output_decode key in {keys}")
        if not keys:
            raise ValueError(f"{self.name}: output_decode must cover at least one key")

        parsed = {
            "encode": tuple(
                _parse_rational(text, self.baseline_inputs, f"{self.name} encode")
                for text in self.encode
            ),
            "decode": tuple(
                _parse_rational(text, self.candidate_inputs, f"{self.name} decode")
                for text in self.decode
            ),
            "output_decode": tuple(
                (
                    key,
                    _parse_rational(
                        text, self.candidate_outputs, f"{self.name} output_decode"
                    ),
                )
                for key, text in self.output_decode
            ),
            "domain": tuple(
                _parse_condition(text, self.baseline_inputs, f"{self.name} domain")
                for text in self.domain
            ),
            "codomain": tuple(
                _parse_condition(text, self.candidate_inputs, f"{self.name} codomain")
                for text in self.codomain
            ),
        }
        self._parsed.update(parsed)
        object.__setattr__(self, "verification", self._verify())
        if self.verification.failures:
            raise BrokenEncoding(f"{self.name}: " + "; ".join(self.verification.failures))

    # -- views -------------------------------------------------------------

    @property
    def baseline_output_keys(self) -> tuple[str, ...]:
        """The baseline output keys this encoding knows how to reconstruct."""
        return tuple(key for key, _ in self.output_decode)

    def encode_expressions(self) -> tuple[Any, ...]:
        return self._parsed["encode"]

    def decode_expressions(self) -> tuple[Any, ...]:
        return self._parsed["decode"]

    def output_decode_expressions(self) -> dict[str, Any]:
        return dict(self._parsed["output_decode"])

    def domain_conditions(self) -> tuple[Any, ...]:
        return self._parsed["domain"]

    def codomain_conditions(self) -> tuple[Any, ...]:
        return self._parsed["codomain"]

    def in_domain(self, point: Sequence[Fraction]) -> bool:
        environment = dict(zip(self.baseline_inputs, (Fraction(v) for v in point)))
        return all(
            _condition_holds(condition, environment) is True
            for condition in self.domain_conditions()
        )

    def in_codomain(self, point: Sequence[Fraction]) -> bool:
        environment = dict(zip(self.candidate_inputs, (Fraction(v) for v in point)))
        return all(
            _condition_holds(condition, environment) is True
            for condition in self.codomain_conditions()
        )

    def encode_point(self, point: Sequence[Fraction]) -> tuple[Fraction, ...]:
        """Carry one exact baseline tuple into the candidate representation."""
        environment = dict(zip(self.baseline_inputs, (Fraction(v) for v in point)))
        return tuple(_exact_eval(expr, environment) for expr in self.encode_expressions())

    def decode_point(self, point: Sequence[Fraction]) -> tuple[Fraction, ...]:
        """Carry one exact candidate tuple back to the baseline representation."""
        environment = dict(zip(self.candidate_inputs, (Fraction(v) for v in point)))
        return tuple(_exact_eval(expr, environment) for expr in self.decode_expressions())

    def decode_outputs(self, values: Mapping[str, Fraction]) -> dict[str, Fraction]:
        """Decode one exact candidate output record into baseline output keys."""
        environment = {name: Fraction(values[name]) for name in self.candidate_outputs}
        return {
            key: _exact_eval(expr, environment)
            for key, expr in self.output_decode_expressions().items()
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "baseline_inputs": list(self.baseline_inputs),
            "candidate_inputs": list(self.candidate_inputs),
            "candidate_outputs": list(self.candidate_outputs),
            "encode": list(self.encode),
            "decode": list(self.decode),
            "output_decode": [list(pair) for pair in self.output_decode],
            "domain": list(self.domain),
            "codomain": list(self.codomain),
            "verification": self.verification.as_dict(),
            "note": self.note,
        }

    # -- the gate ----------------------------------------------------------

    def _verify(self) -> EncodingCheck:
        failures: list[str] = []
        encode_exprs = self._parsed["encode"]
        decode_exprs = self._parsed["decode"]
        domain = self._parsed["domain"]
        codomain = self._parsed["codomain"]

        substitution = {
            sympy.Symbol(name): expr
            for name, expr in zip(self.candidate_inputs, encode_exprs)
        }
        symbolic = True
        for name, expr in zip(self.baseline_inputs, decode_exprs):
            round_trip = sympy.cancel(sympy.together(expr.xreplace(substitution)))
            if sympy.cancel(sympy.together(round_trip - sympy.Symbol(name))) != 0:
                symbolic = False
                failures.append(
                    f"decode is not a left inverse of encode: component {name!r} comes "
                    f"back as {round_trip} rather than {name}"
                )

        points = sample_points(len(self.baseline_inputs), count=ENCODING_SAMPLE_COUNT)
        admissible = 0
        agreed = 0
        codomain_hits = 0
        codomain_misses = 0
        for point in points:
            environment = dict(zip(self.baseline_inputs, point))
            if any(
                _condition_holds(condition, environment) is not True for condition in domain
            ):
                continue
            admissible += 1
            try:
                encoded = tuple(_exact_eval(expr, environment) for expr in encode_exprs)
            except UndefinedAtPoint:
                failures.append(f"encode is undefined at the admissible point {point}")
                continue
            candidate_environment = dict(zip(self.candidate_inputs, encoded))
            if all(
                _condition_holds(condition, candidate_environment) is True
                for condition in codomain
            ):
                codomain_hits += 1
            else:
                codomain_misses += 1
            try:
                back = tuple(
                    _exact_eval(expr, candidate_environment) for expr in decode_exprs
                )
            except UndefinedAtPoint:
                continue
            if back == tuple(environment[name] for name in self.baseline_inputs):
                agreed += 1

        fraction = Fraction(agreed, admissible) if admissible else None
        if admissible and fraction != 1:
            failures.append(
                f"decode(encode(x)) == x fails on the declared domain: only "
                f"{agreed}/{admissible} sample points survive"
            )
        if codomain_misses:
            failures.append(
                f"encode leaves the decode's declared domain at {codomain_misses} of "
                f"{admissible} admissible sample points"
            )

        return EncodingCheck(
            left_inverse_symbolic=symbolic,
            sample_count=len(points),
            admissible_count=admissible,
            agreement_count=agreed,
            agreement_fraction=fraction,
            codomain_hits=codomain_hits,
            codomain_misses=codomain_misses,
            failures=tuple(dict.fromkeys(failures)),
        )


# --------------------------------------------------------------------------
# Definedness, decided symbolically
# --------------------------------------------------------------------------


def _negative_power_bases(expression: Any) -> tuple[Any, ...]:
    """Bases of every ``Pow`` with a numeric negative exponent, and nothing else.

    This is exactly the condition under which :func:`_exact_eval` raises
    :class:`UndefinedAtPoint`, so the symbolic collection below and the exact
    evaluator recognise the same divisions and cannot drift apart.  It is the
    rule :func:`~parseatlas.transformation_axes._denominator_bases` already
    applies to a sympy tree, transposed rather than reinvented.
    """
    return tuple(
        sorted(
            (
                node.base
                for node in expression.atoms(sympy.Pow)
                if node.exp.is_number and node.exp.is_negative
            ),
            key=sympy.srepr,
        )
    )


def _declared_divisors(region: Region) -> tuple[Any, ...]:
    """The symbolic value of every divisor the region's **declared walk** divides by.

    Read off the operation list and never off the collapsed output, for the same
    reason :meth:`Region.evaluate` walks the operations: a division that cancels
    in the output still divides, and the point where it divides by zero is a
    point the region is not defined at.  Reading the collapsed form instead is
    precisely the hole this function exists to close.
    """
    values = region.symbolic_values()
    divisors: list[Any] = []
    for operation in region.operations:
        if operation.kind != "div":
            continue
        argument = operation.args[1]
        divisors.append(
            values[argument] if isinstance(argument, str) else sympy.Rational(argument)
        )
    return tuple(divisors)


def _zero_set_factors(
    polynomials: Sequence[Any], symbols: Sequence[Any]
) -> tuple[frozenset[str], bool, tuple[str, ...]]:
    """Canonical irreducible factors whose zero sets union to the excluded set.

    The union of the zero sets of ``d1 ... dk`` is the zero set of their product,
    and -- over an algebraically closed field, by the Nullstellensatz applied to
    an irreducible factor -- two products have the same zero set exactly when
    they have the same set of irreducible factors.  Multiplicity and a nonzero
    scalar are invisible to a zero set, so the **monic irreducible factor set**
    is a canonical name for the excluded set and comparing two such sets decides
    the comparison outright.  Nothing here samples.

    Returns the factor set, a flag saying some divisor vanishes identically (the
    side is defined nowhere), and the reasons sympy could not decide.  A reason
    is never swallowed: an undecided divisor makes the whole comparison
    undecided, and an undecided comparison is not a discharge.
    """
    keys: set[str] = set()
    everywhere = False
    undecided: list[str] = []
    for polynomial in polynomials:
        try:
            numerator, _ = sympy.fraction(sympy.cancel(sympy.together(polynomial)))
            numerator = sympy.expand(numerator)
        except Exception as exc:  # noqa: BLE001 - reported, never hidden
            undecided.append(f"{polynomial}: {exc}")
            continue
        if numerator.has(sympy.zoo, sympy.nan, sympy.oo):
            undecided.append(f"{polynomial}: the divisor reduces to {numerator}")
            continue
        if numerator.is_number:
            if numerator == 0:
                everywhere = True
            continue
        if not numerator.free_symbols:
            undecided.append(
                f"{numerator}: neither a number nor a function of the inputs"
            )
            continue
        try:
            _, factored = sympy.factor_list(numerator)
        except Exception as exc:  # noqa: BLE001 - reported, never hidden
            undecided.append(f"{numerator}: {exc}")
            continue
        for factor, _multiplicity in factored:
            if factor.is_number:
                continue
            try:
                keys.add(str(sympy.Poly(factor, *symbols).monic().as_expr()))
            except Exception as exc:  # noqa: BLE001 - reported, never hidden
                undecided.append(f"{factor}: {exc}")
    return frozenset(keys), everywhere, tuple(dict.fromkeys(undecided))


def _zero_set_text(key: str) -> str:
    """One excluded factor rendered as the point set it names.

    A univariate factor is solved, following ``canonical.undefined_terms`` and
    ``transformation_axes.excluded_points``; anything else is quoted as the
    equation it is.  Rendering only: the comparison is decided on the canonical
    factor, so a divisor sympy declines to solve still counts.
    """
    expression = sympy.sympify(key)
    free = sorted(expression.free_symbols, key=str)
    if len(free) == 1:
        try:
            roots = sympy.solve(expression, free[0])
        except Exception:  # noqa: BLE001 - an unsolved factor is shown, never dropped
            return f"unsolved:{key} = 0"
        if roots:
            return " or ".join(f"{free[0]} = {root}" for root in roots)
    return f"{key} = 0"


@dataclass(frozen=True)
class DomainComparison:
    """Where each side of the obligation is undefined, decided by cancellation.

    The two sides are ``baseline(x)`` and ``decode(candidate(encode(x)))``, both
    read as functions of the baseline's inputs.  Each contributes an excluded
    set: the baseline from its own declared divisions, the candidate side from
    the encode's poles, from its own declared divisions with the encode
    substituted, and from the output decode's poles with the candidate's outputs
    substituted.

    ``candidate_extra_exclusions`` are the points the candidate loses and the
    baseline keeps -- the candidate **narrows** the domain, and those are the
    points where the sampled half reports "baseline only defined".
    ``baseline_extra_exclusions`` are the opposite: the candidate **widens** it.
    Both directions are decided here, over the whole space, and neither depends
    on a point happening to sit on the sample grid.
    """

    baseline: str
    candidate: str
    encoding: str
    baseline_excluded: tuple[str, ...]
    candidate_excluded: tuple[str, ...]
    candidate_extra_exclusions: tuple[str, ...]
    baseline_extra_exclusions: tuple[str, ...]
    baseline_excluded_everywhere: bool
    candidate_excluded_everywhere: bool
    decided: bool
    equal: bool
    undecided_reasons: tuple[str, ...]
    reason: str

    @property
    def matched(self) -> bool:
        """Decided *and* equal.  An undecided comparison is never a match."""
        return bool(self.decided and self.equal)

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline": self.baseline,
            "candidate": self.candidate,
            "encoding": self.encoding,
            "baseline_excluded": list(self.baseline_excluded),
            "candidate_excluded": list(self.candidate_excluded),
            "candidate_extra_exclusions": list(self.candidate_extra_exclusions),
            "baseline_extra_exclusions": list(self.baseline_extra_exclusions),
            "baseline_excluded_everywhere": self.baseline_excluded_everywhere,
            "candidate_excluded_everywhere": self.candidate_excluded_everywhere,
            "decided": self.decided,
            "equal": self.equal,
            "matched": self.matched,
            "undecided_reasons": list(self.undecided_reasons),
            "reason": self.reason,
        }


def domain_comparison(
    baseline: Region, candidate: Region, encoding: Encoding
) -> DomainComparison:
    """Decide symbolically whether the two sides of the obligation are defined alike.

    A sampled definedness check can only ever say "the two agreed at the points
    somebody listed".  Off that list it says nothing, and a candidate carrying a
    pole at a value the sample grid does not contain is admitted by it.  That is
    the same shape of failure ``NF-2026-00004`` found one level down in
    ``functions.py`` -- the function half decided symbolically while the domain
    half was decided by sampling -- and it is not repeated here.

    The decision is by zero sets: collect the divisors each side actually
    divides by, factor them, and compare the resulting sets.  Equality of the
    factor sets is equality of the excluded sets over an algebraically closed
    field, which is *stricter* than equality over the rationals this model
    samples -- a factor with no rational root, ``b**2 + 1``, is counted as
    excluded even though no rational point ever meets it.  That strictness can
    only ever reject, so it fails closed.

    Where sympy cannot decide -- an unfactorable divisor, a divisor that reduces
    to ``zoo``, or an encoding that declares a ``domain`` while the two excluded
    sets differ, so the difference might lie entirely outside it -- the
    comparison is reported ``decided=False`` and
    :attr:`DomainComparison.matched` is false.  An undecidable domain comparison
    is not a discharge.
    """
    symbols = baseline.input_symbols
    substitution = {
        sympy.Symbol(name): expression
        for name, expression in zip(
            encoding.candidate_inputs, encoding.encode_expressions()
        )
    }
    composed_outputs = {
        key: sympy.cancel(sympy.together(expression.xreplace(substitution)))
        for key, expression in candidate.symbolic_outputs().items()
    }
    output_substitution = {
        sympy.Symbol(key): expression for key, expression in composed_outputs.items()
    }

    baseline_side = list(_declared_divisors(baseline))
    candidate_side: list[Any] = []
    for expression in encoding.encode_expressions():
        candidate_side.extend(_negative_power_bases(expression))
    for divisor in _declared_divisors(candidate):
        candidate_side.append(divisor.xreplace(substitution))
    for expression in encoding.output_decode_expressions().values():
        for base in _negative_power_bases(expression):
            candidate_side.append(base.xreplace(output_substitution))

    baseline_keys, baseline_all, baseline_undecided = _zero_set_factors(
        baseline_side, symbols
    )
    candidate_keys, candidate_all, candidate_undecided = _zero_set_factors(
        candidate_side, symbols
    )
    undecided = tuple(dict.fromkeys(baseline_undecided + candidate_undecided))

    if baseline_all or candidate_all:
        equal = bool(baseline_all and candidate_all)
        extra_candidate: tuple[str, ...] = (
            ("everywhere",) if candidate_all and not baseline_all else ()
        )
        extra_baseline: tuple[str, ...] = (
            ("everywhere",) if baseline_all and not candidate_all else ()
        )
    else:
        equal = baseline_keys == candidate_keys
        extra_candidate = tuple(
            sorted(_zero_set_text(key) for key in candidate_keys - baseline_keys)
        )
        extra_baseline = tuple(
            sorted(_zero_set_text(key) for key in baseline_keys - candidate_keys)
        )

    decided = not undecided
    if decided and not equal and encoding.domain_conditions():
        decided = False
        undecided = undecided + (
            f"{encoding.name} declares the domain {list(encoding.domain)} and the two "
            "excluded sets differ; this model does not decide whether the difference "
            "lies outside that domain",
        )

    baseline_excluded = (
        ("everywhere",)
        if baseline_all
        else tuple(sorted(_zero_set_text(key) for key in baseline_keys))
    )
    candidate_excluded = (
        ("everywhere",)
        if candidate_all
        else tuple(sorted(_zero_set_text(key) for key in candidate_keys))
    )

    if not decided:
        reason = "the domain comparison is undecided and fails closed: " + "; ".join(
            undecided
        )
    elif equal:
        reason = (
            "both sides are excluded on exactly "
            f"{list(baseline_excluded) or 'no point'}, decided by factoring the "
            "divisors rather than by sampling them"
        )
    else:
        parts = []
        if extra_candidate:
            parts.append(f"the candidate additionally loses {list(extra_candidate)}")
        if extra_baseline:
            parts.append(f"the candidate additionally keeps {list(extra_baseline)}")
        reason = "the excluded sets differ: " + " and ".join(parts)

    return DomainComparison(
        baseline=baseline.name,
        candidate=candidate.name,
        encoding=encoding.name,
        baseline_excluded=baseline_excluded,
        candidate_excluded=candidate_excluded,
        candidate_extra_exclusions=extra_candidate,
        baseline_extra_exclusions=extra_baseline,
        baseline_excluded_everywhere=baseline_all,
        candidate_excluded_everywhere=candidate_all,
        decided=decided,
        equal=equal,
        undecided_reasons=undecided,
        reason=reason,
    )


# --------------------------------------------------------------------------
# The proof obligation
# --------------------------------------------------------------------------

OBLIGATION = "decode(candidate(encode(x))) == baseline(x)"


@dataclass(frozen=True)
class Discharge:
    """The result of the decode obligation: three halves, each reported twice.

    Equality, definedness and admissibility are independent claims and each one
    is decided **symbolically** and corroborated **on the declared sample set**,
    with both numbers kept.  A candidate that agrees only on a slice of the
    sample set is then visible as a *number* rather than as a bare rejection,
    and a candidate that saturates the sample set while cancellation refutes it
    sets a conflict flag instead of slipping through.

    * equality -- ``symbolic_verdict`` beside ``agreement_fraction``, with
      ``symbolic_sample_conflict`` when they disagree;
    * definedness -- ``symbolic_domain_match`` beside ``sample_domain_match``,
      with ``symbolic_domain_conflict`` when they disagree, and the excluded
      sets themselves in ``baseline_excluded`` / ``candidate_excluded``;
    * admissibility -- ``encoded_precondition_symbolic`` beside the encoded-point
      counts, so a candidate that demands more than the baseline says so inside
      this record instead of only in a separate ``precondition_check`` call.

    ``domain_match`` is the definedness conjunct and it is the symbolic verdict
    **and** the sample corroboration.  The two sides must be defined at the same
    points: a candidate defined where the baseline is not has not proved
    equality, it has changed the object's domain, and that is a different claim.
    Deciding that by sampling alone is a fail-open -- an off-grid pole is
    invisible to any finite point set -- so the sampled half here can only
    corroborate or contradict, never admit.
    """

    baseline: str
    candidate: str
    encoding: str
    obligation: str
    keys: tuple[str, ...]
    sample_count: int
    outside_domain_count: int
    both_defined_count: int
    baseline_only_defined_count: int
    candidate_only_defined_count: int
    sample_domain_match: bool
    symbolic_domain_match: bool
    symbolic_domain_decided: bool
    symbolic_domain_conflict: bool
    baseline_excluded: tuple[str, ...]
    candidate_excluded: tuple[str, ...]
    candidate_extra_exclusions: tuple[str, ...]
    baseline_extra_exclusions: tuple[str, ...]
    domain_undecided_reasons: tuple[str, ...]
    domain_match: bool
    agreement_count: int
    agreement_fraction: Fraction | None
    symbolic_verdict: bool
    symbolic_sample_conflict: bool
    candidate_precondition: tuple[str, ...]
    candidate_precondition_verdict: str
    encoded_precondition_symbolic: bool | None
    encoded_precondition_holds_count: int
    encoded_precondition_failed_count: int
    encoded_precondition_undecided_count: int
    precondition_admissible: bool
    precondition_qualified: bool
    disagreement_examples: tuple[tuple[tuple[str, ...], str, str, str], ...]
    definedness_examples: tuple[tuple[tuple[str, ...], str], ...]
    precondition_examples: tuple[tuple[str, ...], ...]
    discharged: bool
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "baseline": self.baseline,
            "candidate": self.candidate,
            "encoding": self.encoding,
            "obligation": self.obligation,
            "keys": list(self.keys),
            "sample_count": self.sample_count,
            "outside_domain_count": self.outside_domain_count,
            "both_defined_count": self.both_defined_count,
            "baseline_only_defined_count": self.baseline_only_defined_count,
            "candidate_only_defined_count": self.candidate_only_defined_count,
            "sample_domain_match": self.sample_domain_match,
            "symbolic_domain_match": self.symbolic_domain_match,
            "symbolic_domain_decided": self.symbolic_domain_decided,
            "symbolic_domain_conflict": self.symbolic_domain_conflict,
            "baseline_excluded": list(self.baseline_excluded),
            "candidate_excluded": list(self.candidate_excluded),
            "candidate_extra_exclusions": list(self.candidate_extra_exclusions),
            "baseline_extra_exclusions": list(self.baseline_extra_exclusions),
            "domain_undecided_reasons": list(self.domain_undecided_reasons),
            "domain_match": self.domain_match,
            "agreement_count": self.agreement_count,
            "agreement_fraction": _fraction_text(self.agreement_fraction),
            "symbolic_verdict": self.symbolic_verdict,
            "symbolic_sample_conflict": self.symbolic_sample_conflict,
            "candidate_precondition": list(self.candidate_precondition),
            "candidate_precondition_verdict": self.candidate_precondition_verdict,
            "encoded_precondition_symbolic": self.encoded_precondition_symbolic,
            "encoded_precondition_holds_count": self.encoded_precondition_holds_count,
            "encoded_precondition_failed_count": self.encoded_precondition_failed_count,
            "encoded_precondition_undecided_count": (
                self.encoded_precondition_undecided_count
            ),
            "precondition_admissible": self.precondition_admissible,
            "precondition_qualified": self.precondition_qualified,
            "disagreement_examples": [
                {"point": list(point), "key": key, "baseline": want, "decoded": got}
                for point, key, want, got in self.disagreement_examples
            ],
            "definedness_examples": [
                {"point": list(point), "side": side}
                for point, side in self.definedness_examples
            ],
            "precondition_examples": [
                list(point) for point in self.precondition_examples
            ],
            "discharged": self.discharged,
            "reason": self.reason,
        }


def discharge(
    baseline: Region,
    candidate: Region,
    encoding: Encoding,
    samples: Sequence[Sequence[Fraction]] | None = None,
    max_examples: int = 3,
) -> Discharge:
    """Verify ``decode(candidate(encode(x))) == baseline(x)`` exactly, symbolically first.

    Four conditions have to hold and every one of them is reported whether or
    not it passes:

    * **equality, symbolic.** The candidate's outputs are composed with the
      encode substitution and the output decode and compared to the baseline's
      by cancellation, which decides equality outright for the rational-function
      class this model lives in.
    * **equality, sampled.** Over a declared deterministic sample set, every
      value is an exact ``Fraction`` and a division by zero is a reported point
      rather than a swallowed one.  Corroboration: an empty or vacuous sample
      set leaves ``agreement_fraction`` at ``None`` and does not discharge.
    * **definedness.** :func:`domain_comparison` decides, by factoring the
      divisors each side actually divides by, whether the two are undefined on
      exactly the same set; the sample counts corroborate.  This half is
      symbolic on purpose.  Deciding it by sampling admits any candidate whose
      extra pole sits off the sample grid, which is a fail-open of exactly the
      shape ``NF-2026-00004`` recorded for ``functions.py``.
    * **admissibility.** The candidate's own declared precondition, composed
      with the encode, must hold at every point the obligation is discharged at.
      A candidate that declares a precondition the baseline does not is
      *conditional*, never equivalent, and this record says so rather than
      leaving a reader to join two separate outputs.

    A candidate that fails only the definedness half has not been shown wrong at
    the boundary -- it has been shown to denote its object on a different domain,
    which is what :func:`precondition_check` is for.
    """
    if tuple(baseline.inputs) != tuple(encoding.baseline_inputs):
        raise ValueError(
            f"{encoding.name}: declared baseline inputs {list(encoding.baseline_inputs)} "
            f"do not match {baseline.name}'s {list(baseline.inputs)}"
        )
    if tuple(candidate.inputs) != tuple(encoding.candidate_inputs):
        raise ValueError(
            f"{encoding.name}: declared candidate inputs {list(encoding.candidate_inputs)} "
            f"do not match {candidate.name}'s {list(candidate.inputs)}"
        )
    if tuple(sorted(encoding.candidate_outputs)) != candidate.output_keys:
        raise ValueError(
            f"{encoding.name}: declared candidate outputs "
            f"{sorted(encoding.candidate_outputs)} do not match {candidate.name}'s "
            f"{list(candidate.output_keys)}"
        )
    keys = encoding.baseline_output_keys
    missing = sorted(set(baseline.output_keys) - set(keys))
    if missing:
        raise ValueError(
            f"{encoding.name}: no decode for baseline output key {missing[0]!r}; the "
            "obligation would be discharged on a proper subset of the boundary"
        )
    unknown = sorted(set(keys) - set(baseline.output_keys))
    if unknown:
        raise ValueError(
            f"{encoding.name}: output_decode names {unknown[0]!r}, which "
            f"{baseline.name} does not publish"
        )

    # -- symbolic half: equality ------------------------------------------
    substitution = {
        sympy.Symbol(name): expr
        for name, expr in zip(encoding.candidate_inputs, encoding.encode_expressions())
    }
    composed = {
        key: sympy.cancel(sympy.together(expr.xreplace(substitution)))
        for key, expr in candidate.symbolic_outputs().items()
    }
    decoded_symbolic = {
        key: sympy.cancel(
            sympy.together(
                expr.xreplace({sympy.Symbol(name): composed[name] for name in composed})
            )
        )
        for key, expr in encoding.output_decode_expressions().items()
    }
    wanted = baseline.symbolic_outputs()
    symbolic_verdict = all(
        sympy.cancel(sympy.together(wanted[key] - decoded_symbolic[key])) == 0
        for key in keys
    )

    # -- symbolic half: definedness ---------------------------------------
    domain = domain_comparison(baseline, candidate, encoding)

    # -- symbolic half: the candidate's own precondition, under the encode --
    candidate_conditions = candidate.parsed_precondition()
    if candidate_conditions:
        reduced = sympy.simplify(
            sympy.And(*(item.xreplace(substitution) for item in candidate_conditions))
        )
        if reduced is sympy.true:
            encoded_precondition_symbolic: bool | None = True
        elif reduced is sympy.false:
            encoded_precondition_symbolic = False
        else:
            encoded_precondition_symbolic = None
        candidate_precondition_verdict = precondition_check(candidate).verdict
    else:
        encoded_precondition_symbolic = True
        candidate_precondition_verdict = "unconditional"

    # -- sampled half ------------------------------------------------------
    points = _resolve_samples(baseline.arity, samples)
    outside_domain = 0
    both_defined = 0
    baseline_only = 0
    candidate_only = 0
    agreed = 0
    precondition_holds = 0
    precondition_failed = 0
    precondition_undecided = 0
    disagreements: list[tuple[tuple[str, ...], str, str, str]] = []
    definedness: list[tuple[tuple[str, ...], str]] = []
    precondition_examples: list[tuple[str, ...]] = []

    for point in points:
        if not encoding.in_domain(point):
            outside_domain += 1
            continue
        text = tuple(str(value) for value in point)
        try:
            want = baseline.evaluate(point)
        except UndefinedAtPoint:
            want = None
        try:
            encoded: tuple[Fraction, ...] | None = encoding.encode_point(point)
        except UndefinedAtPoint:
            encoded = None
        if encoded is None:
            got = None
        else:
            if candidate_conditions:
                verdicts = [
                    _condition_holds(condition, dict(zip(candidate.inputs, encoded)))
                    for condition in candidate_conditions
                ]
                if any(verdict is None for verdict in verdicts):
                    precondition_undecided += 1
                    if len(precondition_examples) < max_examples:
                        precondition_examples.append(text)
                elif all(verdicts):
                    precondition_holds += 1
                else:
                    precondition_failed += 1
                    if len(precondition_examples) < max_examples:
                        precondition_examples.append(text)
            try:
                got = encoding.decode_outputs(candidate.evaluate(encoded))
            except UndefinedAtPoint:
                got = None
        if want is None and got is None:
            continue
        if want is None:
            candidate_only += 1
            if len(definedness) < max_examples:
                definedness.append((text, "candidate only"))
            continue
        if got is None:
            baseline_only += 1
            if len(definedness) < max_examples:
                definedness.append((text, "baseline only"))
            continue
        both_defined += 1
        mismatch = [key for key in keys if want[key] != got[key]]
        if not mismatch:
            agreed += 1
        elif len(disagreements) < max_examples:
            key = mismatch[0]
            disagreements.append((text, key, str(want[key]), str(got[key])))

    fraction = Fraction(agreed, both_defined) if both_defined else None
    sample_total = fraction == 1
    conflict = bool(sample_total and not symbolic_verdict) or bool(
        symbolic_verdict and fraction is not None and fraction != 1
    )

    sample_domain_match = baseline_only == 0 and candidate_only == 0
    symbolic_domain_match = domain.matched
    symbolic_domain_conflict = bool(
        domain.decided and (domain.equal != sample_domain_match)
    )
    domain_match = bool(symbolic_domain_match and sample_domain_match)

    precondition_admissible = bool(
        encoded_precondition_symbolic is True
        and precondition_failed == 0
        and precondition_undecided == 0
    )
    precondition_qualified = bool(
        candidate.precondition and candidate_precondition_verdict != "unconditional"
    )

    discharged = bool(
        symbolic_verdict and sample_total and domain_match and precondition_admissible
    )

    if discharged:
        reason = (
            f"obligation discharged on {len(keys)} boundary key(s): {agreed}/{both_defined} "
            "admissible sample points and exact cancellation, with both sides excluded on "
            f"exactly {list(domain.baseline_excluded) or 'no point'} by factoring"
        )
        if precondition_qualified:
            reason += (
                f"; conditional and never equivalent -- {candidate.name} declares "
                f"{list(candidate.precondition)}, which is "
                f"{candidate_precondition_verdict} on its own input tuple and is "
                "discharged at every encoded point by the encode"
            )
    elif conflict and sample_total:
        reason = (
            "sample agreement is total but cancellation refutes the obligation: the "
            "declared sample set does not separate these two boundary objects"
        )
    elif conflict:
        reason = (
            "cancellation accepts the obligation while a sample point refutes it: the "
            "symbolic form hides a point where the two differ"
        )
    elif not domain_match:
        reason = "the two sides are not defined at the same points: " + domain.reason
        if symbolic_domain_conflict and domain.equal is False:
            reason += (
                f"; the declared sample set of {len(points)} point(s) does not see this "
                f"at all -- {baseline_only} baseline-only and {candidate_only} "
                "candidate-only admissible point(s)"
            )
        else:
            reason += (
                f"; the sample set reports {baseline_only} baseline-only and "
                f"{candidate_only} candidate-only admissible point(s)"
            )
    elif not precondition_admissible:
        reason = (
            f"the candidate's declared precondition {list(candidate.precondition)} is not "
            f"discharged by the encode: symbolic verdict {encoded_precondition_symbolic}, "
            f"{precondition_failed} failing and {precondition_undecided} undecided encoded "
            "sample point(s); the obligation would be discharged at points the candidate "
            "itself declares inadmissible"
        )
    else:
        reason = (
            f"obligation not discharged: agreement {agreed}/{both_defined} on the "
            f"admissible sample points, symbolic verdict {symbolic_verdict}"
        )

    return Discharge(
        baseline=baseline.name,
        candidate=candidate.name,
        encoding=encoding.name,
        obligation=OBLIGATION,
        keys=tuple(keys),
        sample_count=len(points),
        outside_domain_count=outside_domain,
        both_defined_count=both_defined,
        baseline_only_defined_count=baseline_only,
        candidate_only_defined_count=candidate_only,
        sample_domain_match=sample_domain_match,
        symbolic_domain_match=symbolic_domain_match,
        symbolic_domain_decided=domain.decided,
        symbolic_domain_conflict=symbolic_domain_conflict,
        baseline_excluded=domain.baseline_excluded,
        candidate_excluded=domain.candidate_excluded,
        candidate_extra_exclusions=domain.candidate_extra_exclusions,
        baseline_extra_exclusions=domain.baseline_extra_exclusions,
        domain_undecided_reasons=domain.undecided_reasons,
        domain_match=domain_match,
        agreement_count=agreed,
        agreement_fraction=fraction,
        symbolic_verdict=symbolic_verdict,
        symbolic_sample_conflict=conflict,
        candidate_precondition=tuple(candidate.precondition),
        candidate_precondition_verdict=candidate_precondition_verdict,
        encoded_precondition_symbolic=encoded_precondition_symbolic,
        encoded_precondition_holds_count=precondition_holds,
        encoded_precondition_failed_count=precondition_failed,
        encoded_precondition_undecided_count=precondition_undecided,
        precondition_admissible=precondition_admissible,
        precondition_qualified=precondition_qualified,
        disagreement_examples=tuple(disagreements),
        definedness_examples=tuple(definedness),
        precondition_examples=tuple(precondition_examples),
        discharged=discharged,
        reason=reason,
    )


def _resolve_samples(
    arity: int, samples: Sequence[Sequence[Fraction]] | None
) -> tuple[tuple[Fraction, ...], ...]:
    if samples is None:
        return sample_points(arity)
    return tuple(tuple(Fraction(value) for value in point) for point in samples)


# --------------------------------------------------------------------------
# Preconditions and invariants
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PreconditionReport:
    """Where a region's declared entry condition holds, and where it does not.

    Five verdicts and they are not interchangeable.  ``unconditional`` means the
    condition held at every sample point (or none is declared); ``conditional``
    means it held at some and failed at others, and such a candidate must be
    reported as conditional and never as equivalent; ``unsatisfied on the sample
    set`` means it held at no sample point while sympy did **not** reduce it to
    false, which is a fact about the declared 240-point grid and not about the
    region; ``unsatisfiable`` is the absolute claim and comes only from the
    symbolic half, so a candidate carrying it is not a candidate at all;
    ``undetermined`` means a precondition was declared and the sample set was
    empty, which measures nothing and therefore concludes nothing.

    The split between the last three is not pedantry.  A precondition such as
    ``Eq(v, 7)`` is satisfiable and holds nowhere on a grid that does not contain
    ``7``; calling it unsatisfiable would let a finite sample set decide a
    statement about the whole space, which is precisely the failure the
    definedness half of :func:`discharge` was rewritten to avoid.

    ``satisfied_but_undefined`` is the interesting failure: points where the
    declared precondition holds and the region's own arithmetic still divides by
    zero.  A precondition that admits such a point is too weak, and saying so
    needs both measurements, not one.
    """

    region: str
    conditions: tuple[str, ...]
    sample_count: int
    satisfied_count: int
    satisfied_fraction: Fraction | None
    defined_count: int
    satisfied_and_defined_count: int
    satisfied_but_undefined: tuple[tuple[str, ...], ...]
    unsatisfied_but_defined_count: int
    failing_examples: tuple[tuple[str, ...], ...]
    undecided_count: int
    symbolically_unsatisfiable: bool
    verdict: str
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "conditions": list(self.conditions),
            "sample_count": self.sample_count,
            "satisfied_count": self.satisfied_count,
            "satisfied_fraction": _fraction_text(self.satisfied_fraction),
            "defined_count": self.defined_count,
            "satisfied_and_defined_count": self.satisfied_and_defined_count,
            "satisfied_but_undefined": [list(point) for point in self.satisfied_but_undefined],
            "unsatisfied_but_defined_count": self.unsatisfied_but_defined_count,
            "failing_examples": [list(point) for point in self.failing_examples],
            "undecided_count": self.undecided_count,
            "symbolically_unsatisfiable": self.symbolically_unsatisfiable,
            "verdict": self.verdict,
            "reason": self.reason,
        }


def precondition_check(
    region: Region,
    samples: Sequence[Sequence[Fraction]] | None = None,
    max_examples: int = 3,
) -> PreconditionReport:
    """Report which sample points satisfy a region's declared precondition.

    Two independent facts are measured at each point: whether the *declared*
    precondition holds, and whether the region's own arithmetic is *defined*.
    They are not the same fact and conflating them is how a candidate acquires a
    precondition nobody wrote down.  The deferred-division candidate is the case
    in point -- its arithmetic is total, and its precondition is nonetheless
    strictly stronger than the baseline's, because its output pair only *denotes*
    a rational where the carried denominator is nonzero.
    """
    conditions = region.parsed_precondition()
    points = _resolve_samples(region.arity, samples)

    satisfied = 0
    undecided = 0
    defined = 0
    satisfied_and_defined = 0
    unsatisfied_but_defined = 0
    satisfied_but_undefined: list[tuple[str, ...]] = []
    failing: list[tuple[str, ...]] = []

    for point in points:
        environment = dict(zip(region.inputs, point))
        verdicts = [_condition_holds(condition, environment) for condition in conditions]
        if any(verdict is None for verdict in verdicts):
            undecided += 1
            holds: bool | None = None
        else:
            holds = all(verdicts)
        try:
            region.evaluate(point)
            is_defined = True
        except UndefinedAtPoint:
            is_defined = False
        if is_defined:
            defined += 1
        if holds is True:
            satisfied += 1
            if is_defined:
                satisfied_and_defined += 1
            elif len(satisfied_but_undefined) < max_examples:
                satisfied_but_undefined.append(tuple(str(value) for value in point))
        elif holds is False:
            if is_defined:
                unsatisfied_but_defined += 1
            if len(failing) < max_examples:
                failing.append(tuple(str(value) for value in point))

    fraction = Fraction(satisfied, len(points)) if points else None
    unsatisfiable = bool(
        conditions and sympy.simplify(sympy.And(*conditions)) is sympy.false
    )
    # "Unsatisfiable" is an absolute claim about the region and it may only come
    # from the symbolic half.  A precondition such as ``Eq(v, 7)`` is perfectly
    # satisfiable and holds at no point of a 240-point grid that does not contain
    # 7, and calling that "unsatisfiable" would be the same kind of overclaim the
    # definedness half was rejected for: a finite sample set deciding a statement
    # about the whole space.
    if unsatisfiable:
        verdict = "unsatisfiable"
    elif not conditions:
        verdict = "unconditional"
    elif not points:
        verdict = "undetermined"
    elif satisfied == len(points):
        verdict = "unconditional"
    elif satisfied == 0:
        verdict = "unsatisfied on the sample set"
    else:
        verdict = "conditional"

    if verdict == "unsatisfiable":
        reason = (
            "the declared precondition holds nowhere: sympy reduces it to false, so this "
            "is not a candidate, it is a region with no admissible input"
        )
    elif verdict == "undetermined":
        reason = (
            "the sample set is empty, so nothing was measured; a declared precondition "
            "with no point to check it at is undetermined, not satisfied"
        )
    elif verdict == "unsatisfied on the sample set":
        reason = (
            f"the declared precondition holds at none of the {len(points)} declared sample "
            "points, and sympy does not reduce it to false: it is unsatisfied ON THIS "
            "SAMPLE SET, which is a fact about the sample set and not about the region. "
            "symbolically_unsatisfiable is False, and a region whose precondition simply "
            "misses the sample grid still has admissible inputs"
        )
    elif verdict == "unconditional":
        reason = (
            f"the declared precondition holds at all {len(points)} sample points"
            if conditions
            else "no precondition is declared: the region is total on its input tuple"
        )
    else:
        reason = (
            f"conditional: the precondition holds at {satisfied}/{len(points)} sample "
            "points, so the region is admissible there and nowhere else"
        )
    if satisfied_but_undefined:
        reason += (
            f"; the precondition is too weak at {len(satisfied_but_undefined)} reported "
            "point(s), where it holds and the arithmetic is still undefined"
        )

    return PreconditionReport(
        region=region.name,
        conditions=tuple(region.precondition),
        sample_count=len(points),
        satisfied_count=satisfied,
        satisfied_fraction=fraction,
        defined_count=defined,
        satisfied_and_defined_count=satisfied_and_defined,
        satisfied_but_undefined=tuple(satisfied_but_undefined),
        unsatisfied_but_defined_count=unsatisfied_but_defined,
        failing_examples=tuple(failing),
        undecided_count=undecided,
        symbolically_unsatisfiable=unsatisfiable,
        verdict=verdict,
        reason=reason,
    )


@dataclass(frozen=True)
class InvariantReport:
    """One declared invariant, checked over the samples and symbolically."""

    region: str
    invariant: str
    checked_count: int
    holding_count: int
    holding_fraction: Fraction | None
    undecided_count: int
    symbolic_verdict: bool | None
    holds: bool
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "invariant": self.invariant,
            "checked_count": self.checked_count,
            "holding_count": self.holding_count,
            "holding_fraction": _fraction_text(self.holding_fraction),
            "undecided_count": self.undecided_count,
            "symbolic_verdict": self.symbolic_verdict,
            "holds": self.holds,
            "reason": self.reason,
        }


def invariant_check(
    region: Region, samples: Sequence[Sequence[Fraction]] | None = None
) -> tuple[InvariantReport, ...]:
    """Check every declared invariant of a region, sampled and symbolically.

    Declared invariants that are never checked are decoration.  The symbolic
    half substitutes each output key by its rational function of the inputs and
    asks sympy to reduce the result; ``None`` is reported when it cannot, which
    is a statement about the decision procedure and not about the invariant.
    """
    points = _resolve_samples(region.arity, samples)
    symbolic_outputs = region.symbolic_outputs()
    reports: list[InvariantReport] = []

    for text, condition in region.parsed_invariants():
        substitution = {
            sympy.Symbol(key): expr for key, expr in symbolic_outputs.items()
        }
        reduced = sympy.simplify(condition.xreplace(substitution))
        if reduced is sympy.true:
            symbolic: bool | None = True
        elif reduced is sympy.false:
            symbolic = False
        else:
            symbolic = None

        checked = 0
        holding = 0
        undecided = 0
        for point in points:
            try:
                outputs = region.evaluate(point)
            except UndefinedAtPoint:
                continue
            environment = dict(zip(region.inputs, point))
            environment.update(outputs)
            verdict = _condition_holds(condition, environment)
            checked += 1
            if verdict is True:
                holding += 1
            elif verdict is None:
                undecided += 1
        fraction = Fraction(holding, checked) if checked else None
        holds = bool(symbolic is not False and fraction == 1)
        reports.append(
            InvariantReport(
                region=region.name,
                invariant=text,
                checked_count=checked,
                holding_count=holding,
                holding_fraction=fraction,
                undecided_count=undecided,
                symbolic_verdict=symbolic,
                holds=holds,
                reason=(
                    f"holds at {holding}/{checked} defined sample points, symbolic verdict "
                    f"{symbolic}"
                ),
            )
        )
    return tuple(reports)


# --------------------------------------------------------------------------
# Structural cost at region level
# --------------------------------------------------------------------------

#: Loop lengths at which the symbolic-in-``n`` cost is checked against an actual
#: unrolling.  Three consecutive values are enough to fit an affine depth and the
#: rest are the verification; the largest is kept small because the whole point
#: of the symbolic form is that nobody has to unroll far.
DEFAULT_LOOP_STEPS: tuple[int, ...] = (1, 2, 3, 4, 6, 8)

LOOP_SYMBOL = sympy.Symbol("n", integer=True, positive=True)


def _counts(operations: Sequence[Operation]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for operation in operations:
        counts[operation.kind] = counts.get(operation.kind, 0) + 1
    return counts


def _sorted_counts(counts: Mapping[str, int]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(counts.items()))


def _value_depths(region: Region) -> dict[str, int]:
    """Depth of every value over the operation DAG; inputs and literals sit at 0."""
    depths: dict[str, int] = {name: 0 for name in region.inputs}
    for operation in region.operations:
        operand_depths = [depths[name] for name in operation.names]
        depths[operation.target] = 1 + max(operand_depths, default=0)
    return depths


def _critical_path(region: Region) -> int:
    depths = _value_depths(region)
    return max((depths[name] for _, name in region.outputs), default=0)


def _liveness(region: Region) -> tuple[int, tuple[int, ...]]:
    """Maximum live-value pressure and the profile it is the maximum of.

    A value is live from the point it is defined until its last use; an output
    lives to the end of the region.  Inputs are counted, because an input that
    has not been consumed yet occupies exactly the same pressure as a computed
    intermediate does.  The profile is read at the region entry and after each
    operation, so a region of ``k`` operations yields ``k + 1`` readings.
    """
    published = {name for _, name in region.outputs}
    end = len(region.operations)
    last_use: dict[str, int] = {}
    for name in region.inputs:
        last_use[name] = -1
    for index, operation in enumerate(region.operations):
        last_use[operation.target] = index
        for name in operation.names:
            last_use[name] = index
    for name in published:
        last_use[name] = end
    defined_at: dict[str, int] = {name: -1 for name in region.inputs}
    for index, operation in enumerate(region.operations):
        defined_at[operation.target] = index

    profile: list[int] = []
    for point in range(-1, end):
        live = sum(
            1
            for name, definition in defined_at.items()
            if definition <= point < last_use[name]
        )
        profile.append(live)
    return (max(profile) if profile else 0), tuple(profile)


def _cse(operations: Sequence[Operation]) -> tuple[list[Operation], dict[str, str]]:
    """Common-subexpression elimination, commutativity-aware.

    This is the normaliser 0027 observed in the vendored engine -- it never
    branches a search, it only collapses one.  In the loop model it is what
    hoists a loop-invariant operation out of the body: the identical operation
    emitted by every step collapses to the one copy the loop actually needs.
    """
    canonical: dict[str, str] = {}
    seen: dict[tuple[str, tuple[Operand, ...]], str] = {}
    kept: list[Operation] = []
    for operation in operations:
        args = tuple(
            canonical.get(argument, argument) if isinstance(argument, str) else argument
            for argument in operation.args
        )
        rebuilt = Operation(operation.target, operation.kind, args)
        key = (rebuilt.kind, rebuilt.canonical_args())
        existing = seen.get(key)
        if existing is not None:
            canonical[operation.target] = existing
            continue
        seen[key] = operation.target
        canonical[operation.target] = operation.target
        kept.append(rebuilt)
    return kept, canonical


def _dce(operations: Sequence[Operation], roots: Iterable[str]) -> list[Operation]:
    """Drop every operation no output depends on."""
    live = set(roots)
    kept: list[Operation] = []
    for operation in reversed(operations):
        if operation.target in live:
            kept.append(operation)
            live.update(operation.names)
    kept.reverse()
    return kept


def unroll(
    region: Region, steps: int, tail: Sequence[Operation] = (), name: str | None = None
) -> Region:
    """The ``steps``-fold composition of a region with itself along its declared state.

    Every step is emitted with fresh names, the produced outputs are fed back
    into the carried inputs, and the result is normalised by :func:`_cse` and
    :func:`_dce`.  The normalisation is the reason this is a loop model and not
    a copy-paste: an operation that depends on no carried value is emitted once
    per step and collapses to a single operation, which is precisely the
    per-step overhead a per-formula operation count cannot see.

    ``tail`` appends operations after the loop -- the decode, in the case this
    experiment is about.  Its operands may name the loop's **output keys**.  A
    region with a tail no longer composes with itself, so its state bindings are
    dropped and its outputs become the tail's targets: the tail is an epilogue,
    not another step.
    """
    if steps < 1:
        raise ValueError(f"{region.name}: a loop needs at least one step, got {steps}")
    if not region.state:
        raise ValueError(
            f"{region.name}: no state binding is declared, so the region names no loop"
        )

    operations: list[Operation] = []
    current = {binding.carried: binding.carried for binding in region.state}
    step_outputs: dict[str, str] = {}

    for step in range(1, steps + 1):
        local: dict[str, str] = {}
        for operation in region.operations:
            args: list[Operand] = []
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
            operations.append(Operation(target, operation.kind, tuple(args)))
            local[operation.target] = target
        step_outputs = {
            key: local.get(value_name, current.get(value_name, value_name))
            for key, value_name in region.outputs
        }
        for binding in region.state:
            current[binding.carried] = step_outputs[binding.produced]

    if tail:
        defined = {operation.target for operation in operations}
        for operation in tail:
            args = []
            for argument in operation.args:
                if not isinstance(argument, str):
                    args.append(argument)
                elif argument in step_outputs:
                    args.append(step_outputs[argument])
                elif argument in defined or argument in region.inputs:
                    args.append(argument)
                else:
                    raise ValueError(
                        f"{region.name}: tail operation {operation.target} uses "
                        f"{argument!r}, which is neither an output key nor a value"
                    )
            operations.append(Operation(operation.target, operation.kind, tuple(args)))
            defined.add(operation.target)
        outputs = tuple((operation.target, operation.target) for operation in tail)
        state: tuple[StateBinding, ...] = ()
    else:
        outputs = tuple((key, step_outputs[key]) for key, _ in region.outputs)
        state = region.state

    normalised, canonical = _cse(operations)
    outputs = tuple((key, canonical.get(value, value)) for key, value in outputs)
    normalised = _dce(normalised, (value for _, value in outputs))

    suffix = f"_x{steps}" + ("_decoded" if tail else "")
    return Region(
        name=name or f"{region.name}{suffix}",
        inputs=region.inputs,
        operations=tuple(normalised),
        outputs=outputs,
        state=state,
        precondition=region.precondition if not tail else (),
        note=f"{steps}-step unrolling of {region.name}",
    )


def _loop_invariant_split(region: Region) -> tuple[dict[str, int], dict[str, int]]:
    """Split the operation multiset into the part a loop computes once and per step.

    An operation is loop-invariant when no carried value appears anywhere in its
    transitive operand closure.  Every other operation has to be recomputed at
    every step because at least one of its operands changed.
    """
    carried = {binding.carried for binding in region.state}
    varying = set(carried)
    invariant: dict[str, int] = {}
    per_step: dict[str, int] = {}
    for operation in region.operations:
        if any(name in varying for name in operation.names):
            varying.add(operation.target)
            per_step[operation.kind] = per_step.get(operation.kind, 0) + 1
        else:
            invariant[operation.kind] = invariant.get(operation.kind, 0) + 1
    return invariant, per_step


@dataclass(frozen=True)
class LoopPoint:
    """One measured unrolling: the cost of the loop at a concrete length."""

    steps: int
    counts: tuple[tuple[str, int], ...]
    total: int
    depth: int
    max_live: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "steps": self.steps,
            "counts": dict(self.counts),
            "total": self.total,
            "depth": self.depth,
            "max_live": self.max_live,
        }


@dataclass(frozen=True)
class LoopCost:
    """The cost of a declared loop over a region, symbolically in ``n``.

    This is the load-bearing half of :func:`region_cost`.  A per-formula count
    reports the body and stops; the loop reports what the body costs when it is
    the body of something, which is where a per-step overhead becomes visible
    and where -- per T23 -- the difference between two correct candidates
    actually lives.

    ``counts_verified`` and ``depth_affine_verified`` are not decoration.  The
    symbolic forms are *derived* from the invariant/varying split and then
    *checked* against real unrollings at every length in ``steps_measured``; a
    false flag means the closed form and the machine disagree and the closed
    form must not be quoted.
    """

    region: str
    carried_state: int
    invariant_counts: tuple[tuple[str, int], ...]
    per_step_counts: tuple[tuple[str, int], ...]
    symbolic_counts: tuple[tuple[str, str], ...]
    symbolic_total: str
    counts_verified: bool
    depth_intercept: int | None
    depth_per_step: int | None
    symbolic_depth: str | None
    depth_affine_verified: bool
    steps_measured: tuple[int, ...]
    measured: tuple[LoopPoint, ...]

    def count_expression(self, kind: str) -> Any:
        """The closed form for one operation kind, as a sympy expression in ``n``."""
        invariant = dict(self.invariant_counts).get(kind, 0)
        per_step = dict(self.per_step_counts).get(kind, 0)
        return sympy.Integer(invariant) + sympy.Integer(per_step) * LOOP_SYMBOL

    def count_at(self, kind: str, steps: int) -> int:
        return int(self.count_expression(kind).subs(LOOP_SYMBOL, steps))

    def as_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "carried_state": self.carried_state,
            "invariant_counts": dict(self.invariant_counts),
            "per_step_counts": dict(self.per_step_counts),
            "symbolic_counts": dict(self.symbolic_counts),
            "symbolic_total": self.symbolic_total,
            "counts_verified": self.counts_verified,
            "depth_intercept": self.depth_intercept,
            "depth_per_step": self.depth_per_step,
            "symbolic_depth": self.symbolic_depth,
            "depth_affine_verified": self.depth_affine_verified,
            "steps_measured": list(self.steps_measured),
            "measured": [point.as_dict() for point in self.measured],
        }


@dataclass(frozen=True)
class RegionCost:
    """Structural cost at region level: multiset, depth, pressure, and the loop.

    Every number here is a count over the operation DAG.  None of them is a
    time.  A division is one operation in this model and that says nothing at
    all about what a division costs on a machine; see the report's limitations.
    """

    region: str
    input_count: int
    output_count: int
    carried_state: int
    operation_counts: tuple[tuple[str, int], ...]
    operation_total: int
    depth: int
    max_live: int
    live_profile: tuple[int, ...]
    loop: LoopCost | None

    def count(self, kind: str) -> int:
        return dict(self.operation_counts).get(kind, 0)

    def as_dict(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "carried_state": self.carried_state,
            "operation_counts": dict(self.operation_counts),
            "operation_total": self.operation_total,
            "depth": self.depth,
            "max_live": self.max_live,
            "live_profile": list(self.live_profile),
            "loop": self.loop.as_dict() if self.loop else None,
        }


def region_cost(
    region: Region, loop_steps: Sequence[int] = DEFAULT_LOOP_STEPS
) -> RegionCost:
    """Structural cost of a region, and of the loop the region declares.

    Reported: the operation multiset by kind and its total; the critical-path
    depth over the operation DAG; the number of live values at the point of
    maximum pressure; and, when the region declares state, the cost of a loop
    over it -- symbolically in ``n`` and verified against real unrollings.

    Passing an empty ``loop_steps`` suppresses the loop section, which is what a
    caller wants for a region that is already an unrolling.
    """
    counts = _counts(region.operations)
    max_live, profile = _liveness(region)
    loop: LoopCost | None = None

    if region.state and tuple(loop_steps):
        steps = tuple(sorted({int(value) for value in loop_steps}))
        if steps[0] < 1:
            raise ValueError(f"{region.name}: loop steps must be at least 1")
        invariant, per_step = _loop_invariant_split(region)

        measured: list[LoopPoint] = []
        counts_verified = True
        for length in steps:
            unrolled = unroll(region, length)
            actual = _counts(unrolled.operations)
            live, _ = _liveness(unrolled)
            measured.append(
                LoopPoint(
                    steps=length,
                    counts=_sorted_counts(actual),
                    total=len(unrolled.operations),
                    depth=_critical_path(unrolled),
                    max_live=live,
                )
            )
            for kind in set(actual) | set(invariant) | set(per_step):
                predicted = invariant.get(kind, 0) + per_step.get(kind, 0) * length
                if actual.get(kind, 0) != predicted:
                    counts_verified = False

        symbolic = {
            kind: sympy.Integer(invariant.get(kind, 0))
            + sympy.Integer(per_step.get(kind, 0)) * LOOP_SYMBOL
            for kind in sorted(set(invariant) | set(per_step))
        }
        total_expression = sympy.expand(sum(symbolic.values(), sympy.Integer(0)))

        intercept: int | None = None
        slope: int | None = None
        depth_verified = False
        if len(measured) >= 2:
            first, second = measured[0], measured[1]
            span = second.steps - first.steps
            difference = second.depth - first.depth
            if span and difference % span == 0:
                slope = difference // span
                intercept = first.depth - slope * first.steps
                depth_verified = all(
                    point.depth == intercept + slope * point.steps for point in measured
                )
                if not depth_verified:
                    intercept = slope = None

        loop = LoopCost(
            region=region.name,
            carried_state=region.carried_state,
            invariant_counts=_sorted_counts(invariant),
            per_step_counts=_sorted_counts(per_step),
            symbolic_counts=tuple(
                (kind, str(expression)) for kind, expression in sorted(symbolic.items())
            ),
            symbolic_total=str(total_expression),
            counts_verified=counts_verified,
            depth_intercept=intercept,
            depth_per_step=slope,
            symbolic_depth=(
                str(sympy.Integer(intercept) + sympy.Integer(slope) * LOOP_SYMBOL)
                if depth_verified and slope is not None
                else None
            ),
            depth_affine_verified=depth_verified,
            steps_measured=steps,
            measured=tuple(measured),
        )

    return RegionCost(
        region=region.name,
        input_count=region.arity,
        output_count=len(region.outputs),
        carried_state=region.carried_state,
        operation_counts=_sorted_counts(counts),
        operation_total=len(region.operations),
        depth=_critical_path(region),
        max_live=max_live,
        live_profile=profile,
        loop=loop,
    )


# --------------------------------------------------------------------------
# The first axis: deferred division on rational values
# --------------------------------------------------------------------------

#: The baseline region.  One step of a chain that carries a rational value and
#: divides at every step: ``v <- v * a / b``.
EAGER_STEP = Region(
    name="eager_division_step",
    inputs=("v", "a", "b"),
    operations=(
        Operation("t", "mul", ("v", "a")),
        Operation("u", "div", ("t", "b")),
    ),
    outputs=(("VALUE", "u"),),
    state=(StateBinding("v", "VALUE"),),
    precondition=("Ne(b, 0)",),
    invariants=("Eq(VALUE*b, v*a)",),
    note="carries the value itself and pays one division per step",
)

#: The candidate region.  The same chain with the value carried as a **pair**
#: ``(num, den)`` and no division at all; the single division is the decode.
DEFERRED_STEP = Region(
    name="deferred_division_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("p", "mul", ("num", "a")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "p"), ("DEN", "q")),
    state=(StateBinding("num", "NUM"), StateBinding("den", "DEN")),
    precondition=("Ne(den, 0)",),
    invariants=("Eq(NUM*den*b, DEN*num*a)",),
    note="carries a numerator/denominator pair and pays no division per step",
)

#: The encoding that connects them: a value becomes the pair ``(v, 1)`` and the
#: pair becomes a value by the one division the whole axis exists to defer.
DEFERRED_ENCODING = Encoding(
    name="deferred_division",
    baseline_inputs=("v", "a", "b"),
    candidate_inputs=("num", "den", "a", "b"),
    candidate_outputs=("DEN", "NUM"),
    encode=("v", "1", "a", "b"),
    decode=("num/den", "a", "b"),
    output_decode=(("VALUE", "NUM/DEN"),),
    codomain=("Ne(den, 0)",),
    note=(
        "the decode is one division; the encode discharges the candidate's extra "
        "precondition by construction, because it sets the denominator to 1"
    ),
)

#: A candidate that agrees with the baseline on a declared sample set and is a
#: different boundary object anyway.  The extra term carries the factor
#: ``(b - 1)(b - 2)``, which vanishes on :data:`ADVERSARIAL_SAMPLES` and nowhere
#: else.  This is 0028's adversarial shape restated for the decode obligation.
ADVERSARIAL_STEP = Region(
    name="adversarial_deferred_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("p0", "mul", ("num", "a")),
        Operation("k1", "sub", ("b", 1)),
        Operation("k2", "sub", ("b", 2)),
        Operation("k3", "mul", ("k1", "k2")),
        Operation("k4", "mul", ("k3", "num")),
        Operation("p", "add", ("p0", "k4")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "p"), ("DEN", "q")),
    state=(StateBinding("num", "NUM"), StateBinding("den", "DEN")),
    precondition=("Ne(den, 0)",),
    note="agrees with the deferred candidate exactly where (b - 1)(b - 2) = 0",
)

#: A candidate whose declared precondition holds nowhere.  Not a candidate.
IMPOSSIBLE_STEP = Region(
    name="impossible_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("p", "mul", ("num", "a")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "p"), ("DEN", "q")),
    state=(StateBinding("num", "NUM"), StateBinding("den", "DEN")),
    precondition=("Ne(den, 0)", "Eq(den, 0)"),
    note="declares a precondition no input satisfies",
)

#: A candidate that is the right boundary object and the wrong *function*: it
#: reaches ``num*a`` through a division by ``b - 3`` that cancels again a step
#: later.  Cancellation therefore accepts it and the sampled definedness check
#: rejects it, because ``3`` is in ``VALUE_POOL`` and 20 sample points land on
#: the pole.
ON_GRID_POLE_STEP = Region(
    name="on_grid_pole_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("s", "sub", ("b", 3)),
        Operation("h", "div", ("num", "s")),
        Operation("p", "mul", ("h", "a")),
        Operation("pp", "mul", ("p", "s")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "pp"), ("DEN", "q")),
    note="cancels back to num*a through a pole at b = 3, which the sample grid contains",
)

#: The identical construction with the pole moved to ``b = 7``, which
#: :data:`~parseatlas.reachability_control.VALUE_POOL` does not contain.  Every
#: sampled number is then indistinguishable from the real candidate's --
#: ``217/217`` agreement, zero baseline-only points -- and the candidate is a
#: different object anyway: ``baseline.evaluate([1, 1, 7])`` is ``1/7`` while the
#: candidate raises :class:`UndefinedAtPoint` at the encoded image of that point.
#: This region is the reason the definedness half is decided by factoring rather
#: than by sampling; a finite grid cannot see it, and moving the pole to any
#: other unsampled value would rebuild it.
OFF_GRID_POLE_STEP = Region(
    name="off_grid_pole_step",
    inputs=("num", "den", "a", "b"),
    operations=(
        Operation("s", "sub", ("b", 7)),
        Operation("h", "div", ("num", "s")),
        Operation("p", "mul", ("h", "a")),
        Operation("pp", "mul", ("p", "s")),
        Operation("q", "mul", ("den", "b")),
    ),
    outputs=(("NUM", "pp"), ("DEN", "q")),
    note="cancels back to num*a through a pole at b = 7, which the sample grid misses",
)

#: A region whose declared precondition is perfectly satisfiable and holds at no
#: point of the declared sample set, because ``VALUE_POOL`` does not contain
#: ``7``.  The counterpart of :data:`OFF_GRID_POLE_STEP` for
#: :func:`precondition_check`: "holds nowhere on this grid" is not
#: "unsatisfiable", and the two must not share a verdict.
OFF_GRID_PRECONDITION_STEP = Region(
    name="off_grid_precondition_step",
    inputs=("v", "a", "b"),
    operations=(Operation("t", "mul", ("v", "a")),),
    outputs=(("VALUE", "t"),),
    precondition=("Eq(b, 7)",),
    note="satisfiable, and satisfied at no point of the declared sample set",
)

#: The sample set on which the adversarial candidate is indistinguishable from
#: the real one.  Declared, deterministic, and deliberately blind: ``b`` takes
#: only the two values at which the planted factor vanishes.
ADVERSARIAL_SAMPLES: tuple[tuple[Fraction, ...], ...] = tuple(
    (Fraction(v), Fraction(a), Fraction(b))
    for v in (1, 2, 3, -1)
    for a in (1, 2, 3, -2)
    for b in (1, 2)
)

#: Two regions with the same operation multiset, the same depth, the same
#: pressure and the same map, whose loops cost different amounts.  The only
#: difference is whether the loop-invariant product ``a*b`` is formed inside the
#: carried chain or outside it.  A per-formula count cannot tell them apart.
PRODUCT_HOISTED = Region(
    name="product_hoisted",
    inputs=("v", "a", "b"),
    operations=(
        Operation("t", "mul", ("a", "b")),
        Operation("w", "mul", ("v", "t")),
    ),
    outputs=(("VALUE", "w"),),
    state=(StateBinding("v", "VALUE"),),
    invariants=("Eq(VALUE, v*a*b)",),
    note="forms a*b outside the carried chain, so a loop forms it once",
)

PRODUCT_SEQUENTIAL = Region(
    name="product_sequential",
    inputs=("v", "a", "b"),
    operations=(
        Operation("t", "mul", ("v", "a")),
        Operation("w", "mul", ("t", "b")),
    ),
    outputs=(("VALUE", "w"),),
    state=(StateBinding("v", "VALUE"),),
    invariants=("Eq(VALUE, v*a*b)",),
    note="forms v*a inside the carried chain, so a loop forms both products every step",
)

#: The trivial encoding: same inputs, same outputs, decode is the identity.  Two
#: regions related by it are compared with no representation change at all,
#: which is how the model says "these are the same object" for the pair whose
#: only difference is cost.
IDENTITY_ENCODING = Encoding(
    name="identity",
    baseline_inputs=("v", "a", "b"),
    candidate_inputs=("v", "a", "b"),
    candidate_outputs=("VALUE",),
    encode=("v", "a", "b"),
    decode=("v", "a", "b"),
    output_decode=(("VALUE", "VALUE"),),
    note="no representation change: the obligation reduces to plain map equality",
)

#: The decode as an epilogue operation, so a chain that ends in one division can
#: be priced as a single region.
DECODE_TAIL: tuple[Operation, ...] = (Operation("value", "div", ("NUM", "DEN")),)


def eager_chain(steps: int) -> Region:
    """``steps`` iterations of the baseline: one multiplication and one division each."""
    return unroll(EAGER_STEP, steps, name=f"eager_chain_{steps}")


def deferred_chain(steps: int) -> Region:
    """``steps`` iterations of the candidate, still carrying the pair at the boundary."""
    return unroll(DEFERRED_STEP, steps, name=f"deferred_chain_{steps}")


def deferred_chain_decoded(steps: int) -> Region:
    """The same, with the single decode division appended as an epilogue."""
    return unroll(
        DEFERRED_STEP, steps, tail=DECODE_TAIL, name=f"deferred_chain_{steps}_decoded"
    )


def adversarial_chain(steps: int) -> Region:
    return unroll(ADVERSARIAL_STEP, steps, name=f"adversarial_chain_{steps}")


# --------------------------------------------------------------------------
# The contrast with the 0028 control
# --------------------------------------------------------------------------


def commitment_contrast(
    baseline: Region,
    candidate: Region,
    encoding: Encoding,
    samples: Sequence[Sequence[Fraction]] | None = None,
) -> dict[str, Any]:
    """Run the 0028 control and the decode obligation on the same pair.

    This is the measured form of what this experiment claims.  The control is
    handed the identical pair of programs and reports which of its three
    structural commitments the candidate violates; the obligation is handed the
    same pair plus a decode relation and reports whether the boundary object
    survived.  The two answers are produced by separate machinery from the same
    input, so the contrast is a measurement rather than a paraphrase.
    """
    reference = as_program(baseline)
    target = as_program(candidate)
    verdict = reachability_verdict(reference, target)
    relaxation = relaxation_analysis(reference, target)
    obligation = discharge(baseline, candidate, encoding, samples)
    return {
        "baseline": baseline.name,
        "candidate": candidate.name,
        "encoding": encoding.name,
        "control_reachable": verdict.reachable,
        "control_violated": list(verdict.violated),
        "control_summary": relaxation.summary,
        "control_sole_blocker": relaxation.sole_blocker,
        "control_unblocking": list(relaxation.unblocking),
        "obligation_discharged": obligation.discharged,
        "verdict": verdict.as_dict(),
        "relaxation": relaxation.as_dict(),
        "discharge": obligation.as_dict(),
        "summary": (
            f"the control reports {list(verdict.violated) or 'no'} violated commitment(s) "
            f"and the decode obligation is "
            f"{'discharged' if obligation.discharged else 'not discharged'}"
        ),
    }


# --------------------------------------------------------------------------
# The experiment
# --------------------------------------------------------------------------

#: Chain lengths the axis is measured at.  Small: the point of the symbolic form
#: is that the answer does not depend on how far anybody unrolled.
AXIS_CHAIN_STEPS: tuple[int, ...] = (1, 2, 3, 4, 6, 8)

#: Chain lengths at which the full decode obligation is discharged.  Discharge
#: is the expensive measurement and it is a statement about the map, not about
#: the length, so a few lengths establish it and the rest would only repeat it.
DISCHARGE_STEPS: tuple[int, ...] = (1, 2, 3)


def _chain_row(steps: int) -> dict[str, Any]:
    eager = region_cost(eager_chain(steps), loop_steps=())
    deferred = region_cost(deferred_chain_decoded(steps), loop_steps=())
    pair_only = region_cost(deferred_chain(steps), loop_steps=())
    return {
        "steps": steps,
        "eager": eager.as_dict(),
        "deferred_decoded": deferred.as_dict(),
        "deferred_pair_only": pair_only.as_dict(),
        "eager_div": eager.count("div"),
        "deferred_div": deferred.count("div"),
        "eager_mul": eager.count("mul"),
        "deferred_mul": deferred.count("mul"),
        "division_saving": eager.count("div") - deferred.count("div"),
        "operation_difference": deferred.operation_total - eager.operation_total,
        "depth_difference": deferred.depth - eager.depth,
    }


def axis_report() -> dict[str, Any]:
    """Every measurement this experiment reports, as plain data.

    Deliberately one function returning one dictionary: the report's numbers and
    the test suite's assertions then come from the same call, so a figure cannot
    drift from what is pinned.

    Sequential by design and by arithmetic rather than by habit.  The whole
    report is a fixed handful of regions -- fewer than a dozen sympy
    cancellations and a few thousand exact rational evaluations -- and 0028
    measured the process-pool break-even for this style of work at 48
    independent pairs on this machine, with a Windows ``spawn`` child paying
    about 0.4 s to import the module before doing anything.  This corpus is two
    orders of magnitude below that threshold, so a pool would be pure loss; the
    parallel path lives in :func:`~parseatlas.reachability_control.reachability_sweep`
    and takes over as soon as a corpus is large enough to earn it.
    """
    chain_rows = [_chain_row(steps) for steps in AXIS_CHAIN_STEPS]
    crossover = next(
        (row["steps"] for row in chain_rows if row["deferred_div"] < row["eager_div"]),
        None,
    )

    eager_loop = region_cost(EAGER_STEP)
    deferred_loop = region_cost(DEFERRED_STEP)
    hoisted = region_cost(PRODUCT_HOISTED)
    sequential = region_cost(PRODUCT_SEQUENTIAL)

    discharges = [
        discharge(eager_chain(steps), deferred_chain(steps), DEFERRED_ENCODING).as_dict()
        for steps in DISCHARGE_STEPS
    ]

    adversarial_declared = discharge(
        EAGER_STEP, ADVERSARIAL_STEP, DEFERRED_ENCODING, ADVERSARIAL_SAMPLES
    )
    adversarial_default = discharge(EAGER_STEP, ADVERSARIAL_STEP, DEFERRED_ENCODING)

    contrast_step = commitment_contrast(EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING)
    contrast_chain = commitment_contrast(
        eager_chain(4), deferred_chain(4), DEFERRED_ENCODING
    )
    contrast_cost_only = commitment_contrast(
        PRODUCT_HOISTED, PRODUCT_SEQUENTIAL, IDENTITY_ENCODING
    )

    return {
        "axis": "deferred division on rational values",
        "obligation": OBLIGATION,
        "encoding": DEFERRED_ENCODING.as_dict(),
        "regions": {
            "eager_step": eager_loop.as_dict(),
            "deferred_step": deferred_loop.as_dict(),
            "product_hoisted": hoisted.as_dict(),
            "product_sequential": sequential.as_dict(),
        },
        "chain": chain_rows,
        "crossover": {
            "kind": "div",
            "first_step_count_with_fewer_divisions": crossover,
            "eager_divisions": str(eager_loop.loop.count_expression("div")),
            "deferred_divisions": "1",
            "saving": str(sympy.expand(eager_loop.loop.count_expression("div") - 1)),
            "operation_total_difference": "1",
            "note": (
                "the deferred form trades n - 1 divisions for n extra multiplications "
                "and one extra operation overall; it never performs fewer operations"
            ),
        },
        "discharge": discharges,
        "adversarial": {
            "declared_samples": adversarial_declared.as_dict(),
            "default_samples": adversarial_default.as_dict(),
            "sample_count": len(ADVERSARIAL_SAMPLES),
        },
        "precondition": {
            "eager_step": precondition_check(EAGER_STEP).as_dict(),
            "deferred_step": precondition_check(DEFERRED_STEP).as_dict(),
            "eager_chain_4": precondition_check(eager_chain(4)).as_dict(),
            "deferred_chain_4": precondition_check(deferred_chain(4)).as_dict(),
            "impossible_step": precondition_check(IMPOSSIBLE_STEP).as_dict(),
            "off_grid_precondition_step": precondition_check(
                OFF_GRID_PRECONDITION_STEP
            ).as_dict(),
        },
        "definedness": {
            "sample_pool": [str(value) for value in VALUE_POOL],
            "matched_pair": domain_comparison(
                EAGER_STEP, DEFERRED_STEP, DEFERRED_ENCODING
            ).as_dict(),
            "on_grid_pole": discharge(
                EAGER_STEP, ON_GRID_POLE_STEP, DEFERRED_ENCODING
            ).as_dict(),
            "off_grid_pole": discharge(
                EAGER_STEP, OFF_GRID_POLE_STEP, DEFERRED_ENCODING
            ).as_dict(),
        },
        "invariants": {
            "eager_step": [report.as_dict() for report in invariant_check(EAGER_STEP)],
            "deferred_step": [
                report.as_dict() for report in invariant_check(DEFERRED_STEP)
            ],
        },
        "loop_versus_formula": {
            "single_step_identical": (
                hoisted.operation_counts == sequential.operation_counts
                and hoisted.operation_total == sequential.operation_total
                and hoisted.depth == sequential.depth
                and hoisted.max_live == sequential.max_live
            ),
            "hoisted_loop": hoisted.loop.as_dict() if hoisted.loop else None,
            "sequential_loop": sequential.loop.as_dict() if sequential.loop else None,
            "discharge": contrast_cost_only["discharge"],
        },
        "commitment_contrast": {
            "step_pair": contrast_step,
            "chain_pair": contrast_chain,
            "cost_only_pair": contrast_cost_only,
        },
    }
