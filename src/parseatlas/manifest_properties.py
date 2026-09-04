"""Experiment 0038: what each world lets you SEE.

Experiment 0034 measured what a mathematical object COSTS to write under each of the twenty-five
precedence conventions, and experiment 0037 measured the same thing field by field.  This module
continues direction B with the second half of the owner's question:

    Changing the representation does not only change what a thing costs - it changes what you can
    SEE.  Two renderings of the same object make different properties visible, and a mathematician
    notices what is visible.

The calibration case is the whole card in one object.  Take ``2x^2 + 3x - 5``, whose roots are
``-5/2`` and ``1``.  It has two named writings, and every world writes it in whichever one is
cheaper *there*::

    2 * x * x + 3 * x - 5      degree, leading coefficient, constant term visible; roots are not
    (2 * x + 5) * (x - 1)      roots visible; constant term and leading coefficient are not

Neither writing shows everything.  A world that makes the first one cheap has mathematicians who
see coefficients first; a world that makes the second one cheap has mathematicians who see roots
first.  That trade - not the cost, the *trade* - is what this module measures.

What "manifest" means here, and what it does not
------------------------------------------------

**Manifestness is defined by the shape rules declared in this module, and the numbers are relative
to them.**  That sentence is the first thing the report says and it is repeated here because it is
the load-bearing caveat of the experiment.  A different, equally defensible rule set would move the
counts.  What the experiment can honestly claim is that *under these rules*, stated in advance and
applied uniformly, the visibility trade is real and measurable.

The rules obey one discipline, without exception:

* a rule is a **shape test on the written form**.  It may read tokens, count them, and see how they
  are grouped.  It may **never** perform algebra - no expansion, no factoring, no collecting of like
  terms, no solving.  If deciding a property requires rewriting the expression, the property is not
  manifest, full stop.
* :func:`ground_truth` computes the same properties **algebraically**, with SymPy, by actually
  factoring and solving.  It is the control.  A property may be manifest only if it is also true;
  a manifest claim that ground truth denies is a **defect in the rules**, reported as an error and
  never as a finding.  :func:`truth_audit` sweeps the whole grid for exactly that.

Two rule regimes, because the honest answer needs both
------------------------------------------------------

The card demands that the report say which conclusions survive a reasonable change of rules.  So
there are two regimes, both implemented, both measured:

``transparent`` (primary)
    Brackets are punctuation.  The native reader of a world parses the string with their own
    grammar, so they recover the tree for free; what they cannot do for free is algebra.  Under
    this regime the manifest set of a *written form* does not depend on the grammar - and the world
    still decides what is visible, because **the world decides which writing is cheapest**.  That
    is exactly the calibration case: 17 worlds choose the expanded writing, 8 choose the factored
    one, and the two writings show different things.

``opaque`` (robustness)
    A bracket is visual encapsulation: what is inside one is written as a unit, and a rule may not
    look through it.  Under this regime the grammar matters twice - it chooses the writing *and* it
    decides how much of that writing is behind brackets - and a world that renders an object
    bracket-free exposes more of it.  This regime is not the headline because it makes the roots of
    ``(2 * x + 5) * (x - 1)`` invisible, which contradicts the calibration the card supplies; it is
    reported alongside as the rule-change the conclusions are tested against.

The vocabulary
--------------

Seven properties, closed and documented, defined in :data:`PROPERTIES`.  Five of them are about a
declared **principal variable** (:data:`PRINCIPAL_VARIABLES`); ``factor_structure`` and
``sign_structure`` are not.  The principal variable is *declared* per object rather than inferred,
because inferring it would be a judgement dressed as a measurement.

What is reused
--------------

* :func:`parseatlas.notational_cost.render` writes a tree under a grammar with the minimum brackets
  that grammar requires, re-parses its own output, and raises
  :class:`~parseatlas.notational_cost.RoundTripError` on mismatch.  Nothing here reimplements the
  bracket rule or weakens that guarantee: :func:`surface` mirrors ``render``'s own bracket decisions
  through :func:`~parseatlas.notational_cost.needs_brackets`, and every surface is checked back
  against ``render``'s string.
* :data:`parseatlas.domain_worlds.CORPUS` supplies the named-law corpus.  It is imported, not
  copied.  The only addition is the calibration quadratic the card supplies.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from sympy import Add, Integer, Mul, Rational, Symbol, expand, factor, simplify
from sympy import roots as sympy_roots

from .canonical import to_sympy
from .domain_worlds import CORPUS as LAW_CORPUS
from .domain_worlds import Law
from .grammar import Grammar
from .notational_cost import (
    CONTROL,
    GRAMMARS,
    Formula,
    binding_powers,
    minimality_audit,
    needs_brackets,
    render,
    round_trip_audit,
)
from .parser import Binary, Node, Number, Variable, parse

__all__ = [
    "CALIBRATION",
    "CONTROL",
    "CORPUS",
    "GRAMMARS",
    "GRAMMAR_BY_ID",
    "OBJECT_BY_NAME",
    "PRINCIPAL_VARIABLES",
    "PROPERTIES",
    "PROPERTY_NAMES",
    "REGIMES",
    "Atom",
    "Group",
    "MathObject",
    "Op",
    "Property",
    "Writing",
    "as_notational_cost_corpus",
    "bracket_count",
    "bridge_audit",
    "calibration_report",
    "chosen_writing",
    "corpus_audit",
    "identity_truth_audit",
    "default_worker_count",
    "ground_truth",
    "manifest_properties_report",
    "manifest_set",
    "measure_pool_startup",
    "monomial_sum",
    "null_model",
    "object_tree",
    "parallel_decision",
    "read_off",
    "should_parallelise",
    "SHAPES",
    "factored_shape",
    "surface",
    "surface_text",
    "written_shape",
    "tradeoff_report",
    "truth_audit",
    "value_audit",
    "visibility_table",
    "visible_signs",
    "worker_count_for",
    "writing_costs",
]

#: Grammar lookup, so a report row can name a world by id.
GRAMMAR_BY_ID: dict[str, Grammar] = {grammar.id: grammar for grammar in GRAMMARS}

#: The two rule regimes.  ``transparent`` is primary; see the module docstring.
REGIMES: tuple[str, ...] = ("transparent", "opaque")


# ------------------------------------------------------------------------------- surface trees
#
# A rendering is a string.  A shape rule needs to talk about that string's structure without
# re-deriving the bracket rule, so the string is represented as a SURFACE tree: the intended tree,
# annotated with exactly the brackets ``render`` emits.  ``Group`` marks a bracketed subexpression.
# Under the transparent regime a rule looks through a ``Group``; under the opaque regime it may not.


@dataclass(frozen=True)
class Atom:
    """A leaf token of the written form: a numeral or a variable name."""

    text: str
    kind: str  # "number" | "variable"


@dataclass(frozen=True)
class Group:
    """A bracketed subexpression of the written form."""

    inner: "Surface"


@dataclass(frozen=True)
class Op:
    """A binary operator applied to two written operands."""

    operator: str
    left: "Surface"
    right: "Surface"


Surface = Atom | Group | Op


def _atom_text(node: Node) -> tuple[str, str]:
    if isinstance(node, Number):
        value = node.value
        text = (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        )
        return text, "number"
    if isinstance(node, Variable):
        return node.name, "variable"
    raise TypeError(f"not a leaf: {node!r}")


def surface(tree: Node, grammar: Grammar) -> Surface:
    """The written form of ``tree`` under ``grammar``, as a surface tree.

    The bracket decisions are taken by :func:`parseatlas.notational_cost.needs_brackets`, the same
    function :func:`~parseatlas.notational_cost.render` uses, so a ``Group`` appears here exactly
    where a bracket appears in the rendering.  :func:`manifest_set` checks that back against the
    rendered string rather than trusting the mirror.
    """
    powers = binding_powers(grammar)

    def walk(node: Node) -> Surface:
        if not isinstance(node, Binary):
            text, kind = _atom_text(node)
            return Atom(text, kind)
        left: Surface = walk(node.left)
        if needs_brackets(node.left, node.operator, "left", powers):
            left = Group(left)
        right: Surface = walk(node.right)
        if needs_brackets(node.right, node.operator, "right", powers):
            right = Group(right)
        return Op(node.operator, left, right)

    return walk(tree)


def surface_text(node: Surface) -> str:
    """Write a surface tree back out, so it can be compared with ``render``'s own string."""
    if isinstance(node, Atom):
        return node.text
    if isinstance(node, Group):
        return f"({surface_text(node.inner)})"
    return f"{surface_text(node.left)} {node.operator} {surface_text(node.right)}"


def bracket_count(node: Surface) -> int:
    """How many bracket pairs the written form carries."""
    if isinstance(node, Atom):
        return 0
    if isinstance(node, Group):
        return 1 + bracket_count(node.inner)
    return bracket_count(node.left) + bracket_count(node.right)


# ------------------------------------------------------------------------ reading a surface tree
#
# Everything below is pure surface reading.  No SymPy, no rewriting, no evaluation: the functions
# split a written form at its operators and report what tokens sit where.  ``opaque`` is the regime
# switch, and it enters in exactly one place - :func:`_look`.


@dataclass(frozen=True)
class Part:
    """One operand of a flattened chain: the surface node, plus whether it can be read.

    ``visible`` is ``False`` only under the opaque regime, and only for a bracketed operand.  A
    hidden part still *exists* - a reader sees that there is a factor - it just cannot be inspected.
    """

    node: Surface
    visible: bool
    sign: int = 1
    inverted: bool = False

    @property
    def is_atom(self) -> bool:
        return self.visible and isinstance(self.node, Atom)


def _look(node: Surface, opaque: bool) -> tuple[Surface, bool]:
    """See through brackets, unless the regime forbids it.

    Returns the node a rule is allowed to reason about and whether it is visible.  This is the ONLY
    place the two regimes differ, which is what makes the robustness comparison a controlled one.
    """
    if isinstance(node, Group):
        if opaque:
            return node, False
        return _look(node.inner, opaque)
    return node, True


def additive_parts(node: Surface, opaque: bool) -> list[Part]:
    """Split a written form at its top-level ``+``/``-``, keeping each addend's sign.

    Only the LEFT spine is flattened.  A right operand that is itself an additive node is returned
    whole, because ``a - (b + c)`` is not ``a - b + c`` and flattening it would invent a sign the
    written form does not show.
    """
    seen, visible = _look(node, opaque)
    if not visible:
        return [Part(seen, False)]
    if isinstance(seen, Op) and seen.operator in ("+", "-"):
        parts = additive_parts(seen.left, opaque)
        sign = 1 if seen.operator == "+" else -1
        right, right_visible = _look(seen.right, opaque)
        return [*parts, Part(right, right_visible, sign=sign)]
    return [Part(seen, True)]


def multiplicative_parts(node: Surface, opaque: bool, inverted: bool = False) -> list[Part]:
    """Split a written form at its top-level ``*``/``/`` into numerator and denominator factors.

    Both spines are flattened here, which is sound for a multiplicative chain: ``a * (b * c)`` and
    ``a / (b / c)`` are handled by carrying the inversion flag down the right branch.
    """
    seen, visible = _look(node, opaque)
    if not visible:
        return [Part(seen, False, inverted=inverted)]
    if isinstance(seen, Op) and seen.operator in ("*", "/"):
        flip = seen.operator == "/"
        return [
            *multiplicative_parts(seen.left, opaque, inverted),
            *multiplicative_parts(seen.right, opaque, inverted != flip),
        ]
    return [Part(seen, True, inverted=inverted)]


def _is_monomial(node: Surface, opaque: bool) -> list[Part] | None:
    """The factors of ``node`` if it is a written monomial, else ``None``.

    A *written monomial* is a chain of ``*`` and ``/`` over leaf tokens only.  Any bracketed sum
    inside it - and, under the opaque regime, any bracket at all - disqualifies it, because then the
    term is not a term you can read the coefficient off.
    """
    parts = multiplicative_parts(node, opaque)
    if all(part.is_atom for part in parts):
        return parts
    return None


def _occurrences(parts: Sequence[Part], variable: str) -> tuple[int, int]:
    """How often ``variable`` appears in the numerator and in the denominator of a monomial."""
    numerator = sum(
        1
        for part in parts
        if part.is_atom
        and isinstance(part.node, Atom)
        and part.node.kind == "variable"
        and part.node.text == variable
        and not part.inverted
    )
    denominator = sum(
        1
        for part in parts
        if part.is_atom
        and isinstance(part.node, Atom)
        and part.node.kind == "variable"
        and part.node.text == variable
        and part.inverted
    )
    return numerator, denominator


@dataclass(frozen=True)
class Term:
    """One addend of a monomial-sum written form."""

    sign: int
    power: int
    factors: tuple[Part, ...]


def monomial_sum(node: Surface, opaque: bool, variable: str | None) -> tuple[Term, ...] | None:
    """The written form as a sum of monomials in ``variable``, or ``None`` if it is not one.

    This is the shape the whole coefficient half of the vocabulary rests on.  It holds when the
    top level is an additive chain (possibly of length one) and **every** addend is a written
    monomial in which ``variable`` never appears in a denominator.  When it holds, the degree, the
    leading coefficient and the constant term are things you point at; when it does not, they are
    things you would have to compute.
    """
    terms: list[Term] = []
    for part in additive_parts(node, opaque):
        if not part.visible:
            return None
        factors = _is_monomial(part.node, opaque)
        if factors is None:
            return None
        power = 0
        if variable is not None:
            numerator, denominator = _occurrences(factors, variable)
            if denominator:
                return None  # the variable sits under a division: not a polynomial in it
            power = numerator
        terms.append(Term(part.sign, power, tuple(factors)))
    return tuple(terms)


def _mentions(node: Surface, variable: str, opaque: bool) -> bool:
    """Whether ``variable`` occurs in a written form - conservatively ``True`` when hidden."""
    seen, visible = _look(node, opaque)
    if not visible:
        return True  # cannot verify absence behind a bracket, so never claim it
    if isinstance(seen, Atom):
        return seen.kind == "variable" and seen.text == variable
    if isinstance(seen, Group):  # pragma: no cover - _look already unwrapped it
        return _mentions(seen.inner, variable, opaque)
    return _mentions(seen.left, variable, opaque) or _mentions(seen.right, variable, opaque)


@dataclass(frozen=True)
class Factored:
    """A written form presented as a product of factors that are linear in the variable.

    ``linear`` carries, for each factor that holds the variable, the pair of written terms a reader
    would take the root from: the degree-one term and the constant term of that factor, or ``None``
    when the factor is the bare variable (root zero).  It exists so :func:`read_off` can report the
    ROOTS a reader would come away with, and :func:`value_audit` can check them against SymPy.
    """

    degree: int
    factors: int
    linear: tuple[tuple[Term, Term | None], ...] = ()


def factored_shape(node: Surface, opaque: bool, variable: str | None) -> Factored | None:
    """The written form as a product of factors, each at most linear in ``variable``.

    This is the roots half of the vocabulary.  It holds when

    * the top-level operator is multiplicative (``*`` or ``/``) - the object is *presented* as a
      product, not as a sum that happens to factor;
    * every denominator factor is free of the variable;
    * every numerator factor is either a leaf, or a written sum of monomials of degree at most one
      in the variable, carrying exactly one degree-one term and at most one constant term;
    * at least one factor carries the variable.

    Then each root is read off one linear factor - one sign change and one division of visible
    tokens.  That is arithmetic on what is written, not algebra on the object, and the distinction
    is declared rather than assumed: it is the judgement that makes the card's calibration case come
    out the way the card states it.  The 'exactly one degree-one term' clause is the same
    pointability discipline the coefficient rules use: ``(a * x + b * x + c)`` would need its two
    linear terms combined before a root could be read, and combining them is algebra.
    """
    if variable is None:
        return None
    top, visible = _look(node, opaque)
    if not visible or not isinstance(top, Op) or top.operator not in ("*", "/"):
        return None
    parts = multiplicative_parts(node, opaque)
    if len(parts) < 2:
        return None
    linear: list[tuple[Term, Term | None]] = []
    for part in parts:
        if not part.visible:
            return None
        if part.inverted:
            if _mentions(part.node, variable, opaque):
                return None
            continue
        if isinstance(part.node, Atom):
            if part.node.kind == "variable" and part.node.text == variable:
                linear.append((Term(1, 1, (part,)), None))
            continue
        terms = monomial_sum(part.node, opaque, variable)
        if terms is None:
            return None
        degree = max(term.power for term in terms)
        if degree > 1:
            return None
        if degree == 0:
            continue
        carriers = [term for term in terms if term.power == 1]
        constants = [term for term in terms if term.power == 0]
        if len(carriers) != 1 or len(constants) > 1:
            return None
        linear.append((carriers[0], constants[0] if constants else None))
    if not linear:
        return None
    return Factored(degree=len(linear), factors=len(parts), linear=tuple(linear))


def visible_signs(node: Surface, opaque: bool) -> str:
    """The sign pattern a reader takes off the top-level additive chain, e.g. ``"+-+"``.

    Empty when the top level is not a readable chain of monomials.  It is what ``sign_structure``
    claims is visible, so it is published in every cell and pinned in the tests rather than being a
    field nothing ever looks at.
    """
    parts = additive_parts(node, opaque)
    if len(parts) < 2:
        return ""
    if not all(part.visible and _is_monomial(part.node, opaque) is not None for part in parts):
        return ""
    return "".join("+" if part.sign > 0 else "-" for part in parts)


# --------------------------------------------------------------------------- reading off a value
#
# The shape rules decide WHETHER a property is manifest.  These functions read the VALUE a reader
# would come away with, and :func:`value_audit` checks it against SymPy.  That is a much stronger
# control than "the property exists": a rule that fires on the wrong shape usually still meets the
# weak control, but it almost never reads the right number.


def _atom_expr(atom: Atom) -> Any:
    return Rational(atom.text) if atom.kind == "number" else Symbol(atom.text, real=True)


def _term_expr(term: Term, variable: str | None = None, strike: int = 0) -> Any:
    """The value of a written monomial, optionally with ``strike`` copies of the variable removed."""
    value: Any = Integer(term.sign)
    removed = 0
    for part in term.factors:
        atom = part.node
        assert isinstance(atom, Atom)  # monomial_sum guarantees this
        if (
            not part.inverted
            and variable is not None
            and atom.kind == "variable"
            and atom.text == variable
            and removed < strike
        ):
            removed += 1
            continue
        value = value / _atom_expr(atom) if part.inverted else value * _atom_expr(atom)
    return value


def read_off(node: Surface, opaque: bool, variable: str | None) -> dict[str, Any]:
    """The values a reader takes off the written form, for every property it makes manifest.

    Present keys mirror the manifest set exactly for the four value-carrying properties; the
    remaining three (``factor_structure``, ``sign_structure``, ``even_parity``) are yes/no and are
    reported by :func:`manifest_set` alone.
    """
    values: dict[str, Any] = {}
    terms = monomial_sum(node, opaque, variable) if variable is not None else None
    factored = factored_shape(node, opaque, variable)

    if terms is not None and max(term.power for term in terms) >= 1:
        top = max(term.power for term in terms)
        values["degree"] = top
        leading = [term for term in terms if term.power == top]
        if len(leading) == 1:
            values["leading_coefficient"] = _term_expr(leading[0], variable, strike=top)
        constants = [term for term in terms if term.power == 0]
        if len(constants) <= 1:
            values["constant_term"] = _term_expr(constants[0]) if constants else Integer(0)
    elif factored is not None:
        values["degree"] = factored.degree

    if factored is not None:
        roots = []
        for carrier, constant in factored.linear:
            coefficient = _term_expr(carrier, variable, strike=1)
            offset = Integer(0) if constant is None else _term_expr(constant)
            roots.append(-offset / coefficient)
        values["roots"] = tuple(roots)
    return values


def value_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    regimes: Sequence[str] = REGIMES,
) -> dict[str, Any]:
    """Every value a reader would take off a manifest writing, checked against SymPy.

    The weak control asks whether the property is true of the object.  This one asks whether the
    number the notation puts in front of the reader is the RIGHT number - the degree SymPy computes,
    the leading coefficient of the polynomial, the constant term at zero, the multiset of roots.
    ``mismatches`` must be empty.
    """
    from sympy import Poly

    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    mismatches = []
    checks = 0
    for item in corpus:
        if item.variable is None:
            continue
        symbol = Symbol(item.variable, real=True)
        for writing in item.writings:
            tree = object_tree(writing)
            expr = to_sympy(tree)
            polynomial = Poly(expr, symbol)
            expected = {
                "degree": polynomial.degree(),
                "leading_coefficient": polynomial.LC(),
                "constant_term": expr.subs(symbol, 0),
            }
            true_roots = sympy_roots(polynomial)
            for grammar in grammars:
                for regime in regimes:
                    values = read_off(
                        surface(tree, grammar), regime == "opaque", item.variable
                    )
                    for name, value in values.items():
                        checks += 1
                        if name == "roots":
                            found: dict[Any, int] = {}
                            for root in value:
                                key = simplify(root)
                                found[key] = found.get(key, 0) + 1
                            ok = len(value) == polynomial.degree() and all(
                                any(simplify(key - other) == 0 for other in true_roots)
                                for key in found
                            )
                        else:
                            ok = simplify(value - expected[name]) == 0
                        if not ok:
                            mismatches.append(
                                {
                                    "object": item.name,
                                    "writing": writing.role,
                                    "grammar": grammar.id,
                                    "regime": regime,
                                    "property": name,
                                    "read": str(value),
                                    "actual": str(
                                        true_roots if name == "roots" else expected[name]
                                    ),
                                }
                            )
    return {
        "checks": checks,
        "mismatches": tuple(mismatches),
        "correct": not mismatches,
    }


# ------------------------------------------------------------------------------- the vocabulary


ShapeRule = Callable[[Surface, bool, str | None], bool]
TruthRule = Callable[[Any, Symbol | None], bool]


@dataclass(frozen=True)
class Property:
    """One property, with its shape rule in prose and in code, and its algebraic control.

    ``shape`` decides the property from the written form alone.  ``truth`` decides it from the
    object, with SymPy.  The two are kept apart on purpose: ``shape`` may never call ``truth``, and
    :func:`truth_audit` asserts that whatever ``shape`` claims, ``truth`` confirms.
    """

    name: str
    rule: str
    truth_rule: str
    shape: ShapeRule
    truth: TruthRule
    needs_variable: bool
    note: str = ""


# ---- shape rules ------------------------------------------------------------------------------


def _shape_degree(node: Surface, opaque: bool, variable: str | None) -> bool:
    if variable is None:
        return False
    terms = monomial_sum(node, opaque, variable)
    if terms is not None and max(term.power for term in terms) >= 1:
        return True
    return factored_shape(node, opaque, variable) is not None


def _shape_leading_coefficient(node: Surface, opaque: bool, variable: str | None) -> bool:
    if variable is None:
        return False
    terms = monomial_sum(node, opaque, variable)
    if terms is None:
        return False
    top = max(term.power for term in terms)
    if top < 1:
        return False
    return sum(1 for term in terms if term.power == top) == 1


def _shape_constant_term(node: Surface, opaque: bool, variable: str | None) -> bool:
    if variable is None:
        return False
    terms = monomial_sum(node, opaque, variable)
    if terms is None:
        return False
    if max(term.power for term in terms) < 1:
        return False
    return sum(1 for term in terms if term.power == 0) <= 1


def _shape_roots(node: Surface, opaque: bool, variable: str | None) -> bool:
    return factored_shape(node, opaque, variable) is not None


def _shape_factor_structure(node: Surface, opaque: bool, variable: str | None) -> bool:
    top, visible = _look(node, opaque)
    if not visible or not isinstance(top, Op) or top.operator != "*":
        return False
    parts = multiplicative_parts(node, opaque)
    numerators = [part for part in parts if not part.inverted]
    return sum(1 for part in numerators if not part.is_atom) >= 2


def _shape_sign_structure(node: Surface, opaque: bool, variable: str | None) -> bool:
    parts = additive_parts(node, opaque)
    if len(parts) < 2:
        return False
    return all(part.visible and _is_monomial(part.node, opaque) is not None for part in parts)


def _shape_even_parity(node: Surface, opaque: bool, variable: str | None) -> bool:
    if variable is None:
        return False
    terms = monomial_sum(node, opaque, variable)
    if terms is None:
        return False
    if max(term.power for term in terms) < 1:
        return False
    return all(term.power % 2 == 0 for term in terms)


# ---- algebraic controls -------------------------------------------------------------------------


def _is_polynomial_in(expr: Any, symbol: Symbol | None) -> bool:
    if symbol is None:
        return False
    if symbol not in expr.free_symbols:
        return False
    return bool(expr.is_polynomial(symbol))


def _truth_polynomial(expr: Any, symbol: Symbol | None) -> bool:
    return _is_polynomial_in(expr, symbol)


def _truth_roots(expr: Any, symbol: Symbol | None) -> bool:
    if not _is_polynomial_in(expr, symbol):
        return False
    from sympy import Poly

    polynomial = Poly(expr, symbol)
    if polynomial.degree() < 1:
        return False
    found = sympy_roots(polynomial)
    return sum(found.values()) == polynomial.degree()


def _factor_count(expr: Any) -> int:
    """Non-constant factors of the object, counted with multiplicity."""
    total = 0
    for piece in Mul.make_args(factor(expr)):
        base, exponent = piece.as_base_exp()
        if base.is_number:
            continue
        total += abs(int(exponent)) if exponent.is_Integer else 1
    return total


def _truth_factor_structure(expr: Any, symbol: Symbol | None) -> bool:
    return _factor_count(expr) >= 2


def _truth_sign_structure(expr: Any, symbol: Symbol | None) -> bool:
    expanded = expand(expr)
    return len(Add.make_args(expanded)) >= 2


def _truth_even_parity(expr: Any, symbol: Symbol | None) -> bool:
    if symbol is None or symbol not in expr.free_symbols:
        return False
    return bool(simplify(expr.subs(symbol, -symbol) - expr) == 0)


PROPERTIES: tuple[Property, ...] = (
    Property(
        name="degree",
        rule=(
            "the written form is a sum of monomials in the principal variable and the variable "
            "occurs (the degree is the count of its occurrences in the longest monomial), OR the "
            "written form is a product whose factors are each at most linear in the variable (the "
            "degree is the number of factors that carry it)"
        ),
        truth_rule="the object is a polynomial in the principal variable, which therefore has one",
        shape=_shape_degree,
        truth=_truth_polynomial,
        needs_variable=True,
        note=(
            "the only property with two shape clauses, because both an expanded and a factored "
            "writing genuinely show the degree - the first by counting repeated multiplications, "
            "the second by counting linear factors"
        ),
    ),
    Property(
        name="leading_coefficient",
        rule=(
            "the written form is a sum of monomials in the principal variable, the variable "
            "occurs, and exactly ONE monomial attains the highest power - so the coefficient is "
            "that monomial with the variable struck out, a thing you point at"
        ),
        truth_rule="the object is a polynomial in the principal variable, which therefore has one",
        shape=_shape_leading_coefficient,
        truth=_truth_polynomial,
        needs_variable=True,
        note=(
            "uniqueness is the whole rule: 'a * x * x + b * x * x' has two leading monomials and "
            "reading the coefficient off it would mean adding a and b, which is algebra"
        ),
    ),
    Property(
        name="constant_term",
        rule=(
            "the written form is a sum of monomials in the principal variable, the variable "
            "occurs, and AT MOST ONE monomial is free of it - so the constant term is either that "
            "single visible summand or, if there is none, zero"
        ),
        truth_rule="the object is a polynomial in the principal variable, which therefore has one",
        shape=_shape_constant_term,
        truth=_truth_polynomial,
        needs_variable=True,
        note=(
            "the 'at most one' clause is the soundness fix for the card's suggested rule: "
            "'fa - dfa * a + dfa * x' has TWO variable-free summands and its constant term is "
            "their sum, which you would have to combine, so the property is NOT manifest there"
        ),
    ),
    Property(
        name="roots",
        rule=(
            "the top-level operator is multiplicative, every denominator factor is free of the "
            "principal variable, and every numerator factor is a leaf or a written sum of "
            "monomials of degree at most one in it - so each root is read off one linear factor"
        ),
        truth_rule=(
            "the object is a polynomial of degree at least one in the principal variable and its "
            "roots, found symbolically, account for the whole degree - i.e. it splits"
        ),
        shape=_shape_roots,
        truth=_truth_roots,
        needs_variable=True,
        note=(
            "reading -5/2 off '2 * x + 5' is one sign change and one division of visible tokens; "
            "counting that as reading rather than as algebra is a declared judgement, and it is "
            "the judgement that makes the card's calibration case come out as the card states it"
        ),
    ),
    Property(
        name="factor_structure",
        rule=(
            "the top-level operator is '*' and at least two of its numerator factors are not leaf "
            "tokens - the object is written as a product of compound pieces"
        ),
        truth_rule="the object has at least two non-constant factors, counted with multiplicity",
        shape=_shape_factor_structure,
        truth=_truth_factor_structure,
        needs_variable=False,
        note=(
            "the only rule that survives the opaque regime unchanged: seeing THAT there are two "
            "compound factors never requires looking inside either of them"
        ),
    ),
    Property(
        name="sign_structure",
        rule=(
            "the top level is an additive chain of at least two addends and every addend is a "
            "written monomial - so each term's sign is on the page, with no bracket to expand"
        ),
        truth_rule="the expanded object has at least two terms, so there is a sign pattern to see",
        shape=_shape_sign_structure,
        truth=_truth_sign_structure,
        needs_variable=False,
        note="the property a factored writing always destroys and an expanded writing always shows",
    ),
    Property(
        name="even_parity",
        rule=(
            "the written form is a sum of monomials in the principal variable, the variable "
            "occurs, and EVERY monomial carries an even number of its occurrences"
        ),
        truth_rule="substituting -v for v leaves the object unchanged",
        shape=_shape_even_parity,
        truth=_truth_even_parity,
        needs_variable=True,
        note=(
            "the card's 'parity / symmetry, if it does at all' slot; it is manifest only in a "
            "monomial-sum writing, never in a factored one, even when the object is even"
        ),
    ),
)

PROPERTY_NAMES: tuple[str, ...] = tuple(item.name for item in PROPERTIES)

PROPERTY_BY_NAME: dict[str, Property] = {item.name: item for item in PROPERTIES}


# ------------------------------------------------------------------------------------- the corpus


@dataclass(frozen=True)
class Writing:
    """One named written form of an object: the datum a shape rule is applied to."""

    role: str
    source: str


@dataclass(frozen=True)
class MathObject:
    """One mathematical object, with every named way this corpus writes it.

    A two-sided law contributes two writings of ONE object - that is what makes it an identity - so
    a world can pick whichever it writes more cheaply, and the manifest set follows the pick.  A
    one-sided law has a single writing, so its manifest set is the same in every world; those
    objects are the null model and are counted separately.
    """

    name: str
    field: str
    variable: str | None
    writings: tuple[Writing, ...]
    note: str = ""

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(writing.role for writing in self.writings)


#: The principal variable of each object, DECLARED rather than inferred.
#:
#: Five of the seven properties are properties *in a variable*, so something has to say which.
#: Inferring it (say, "the most frequent variable") would be a judgement dressed up as a
#: measurement, and it would silently change what is being asked of an object.  ``None`` means the
#: object is not naturally read as a polynomial in any one of its symbols - a dot product, a slope,
#: a difference quotient - and for those objects the five variable-borne properties are false, not
#: merely hidden.  ``ground_truth`` agrees, which is what keeps the audit honest.
PRINCIPAL_VARIABLES: dict[str, str | None] = {
    "calibration_quadratic": "x",
    # algebra
    "distributive_law": "a",
    "binomial_square": "a",
    "difference_of_squares": "a",
    "difference_of_cubes": "a",
    "sum_of_cubes": "a",
    "quadratic": "x",
    "binomial_cube": "a",
    "perfect_square_trinomial": "x",
    # geometry
    "line": "x",
    "circle": "x",
    "ellipse": "x",
    "hyperbola": "x",
    "parabola": "x",
    "distance_components": "x2",
    "slope": None,
    "midpoint": "x1",
    "triangle_area": None,
    "trapezoid_area": "h",
    "pythagorean_form": "a",
    # calculus
    "difference_quotient": None,
    "product_rule": None,
    "quotient_rule": None,
    "chain_rule": None,
    "linear_approximation": "x",
    "taylor_first_term": "x",
    "taylor_second_term": "x",
    "riemann_sum_term": None,
    # linear algebra
    "dot_product": None,
    "determinant_2x2": None,
    "linear_combination": None,
    "squared_norm": None,
    "matrix_vector_component": None,
    "cramer_numerator": None,
}

#: The card's calibration object: ``2x^2 + 3x - 5``, roots ``-5/2`` and ``1``, in its two writings.
CALIBRATION: MathObject = MathObject(
    name="calibration_quadratic",
    field="algebra",
    variable="x",
    writings=(
        Writing("expanded", "2 * x * x + 3 * x - 5"),
        Writing("factored", "(2 * x + 5) * (x - 1)"),
    ),
    note="the manager's calibration case: 17 worlds write it expanded, 8 write it factored",
)


def _objects_from_laws(laws: Sequence[Law]) -> tuple[MathObject, ...]:
    """Lift the imported named-law corpus into objects, attaching the declared variable."""
    objects = []
    for law in laws:
        if law.name not in PRINCIPAL_VARIABLES:
            raise KeyError(f"no principal variable declared for law {law.name!r}")
        objects.append(
            MathObject(
                name=law.name,
                field=law.field,
                variable=PRINCIPAL_VARIABLES[law.name],
                writings=tuple(Writing(role, source) for role, source in law.sides),
                note=law.note,
            )
        )
    return tuple(objects)


#: The corpus: experiment 0037's named laws, imported whole, plus the calibration quadratic.
CORPUS: tuple[MathObject, ...] = (CALIBRATION, *_objects_from_laws(LAW_CORPUS))

OBJECT_BY_NAME: dict[str, MathObject] = {item.name: item for item in CORPUS}


def object_tree(writing: Writing) -> Node:
    """The intended tree of a written form: its source parsed under the control grammar.

    ``G0`` is the control because it is how mathematics is written today, so parsing a conventional
    source under it recovers the intended object instead of imposing one.
    """
    return parse(writing.source, CONTROL)


def as_notational_cost_corpus(corpus: Sequence[MathObject] | None = None) -> tuple[Formula, ...]:
    """The corpus as 0034 ``Formula`` records, so its audits can be run over it unchanged."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    return tuple(
        Formula(f"{item.name}.{writing.role}", item.field, writing.source)
        for item in corpus
        for writing in item.writings
    )


# --------------------------------------------------------------------------------- the two halves


def manifest_set(
    tree: Node,
    grammar: Grammar,
    variable: str | None = None,
    opaque: bool = False,
) -> tuple[str, ...]:
    """Which properties the minimal rendering of ``tree`` under ``grammar`` makes manifest.

    The rendering comes from :func:`parseatlas.notational_cost.render`, which emits only the
    brackets the grammar requires and re-parses its own output; :func:`surface` mirrors those same
    bracket decisions, and the mirror is checked back against the rendered string here rather than
    assumed.  Every decision after that is a shape test - no algebra is performed and no root, no
    coefficient and no factorisation is ever computed.
    """
    text = render(tree, grammar)
    written = surface(tree, grammar)
    if surface_text(written) != text:  # pragma: no cover - guards the mirror, must never fire
        raise ValueError(
            f"surface/render disagreement under {grammar.id}: "
            f"{surface_text(written)!r} vs {text!r}"
        )
    return tuple(
        item.name for item in PROPERTIES if item.shape(written, opaque, variable)
    )


def ground_truth(tree: Node, variable: str | None = None) -> tuple[str, ...]:
    """Which properties are actually TRUE of the object, computed algebraically.

    This is the control, and it is deliberately the opposite kind of computation from
    :func:`manifest_set`: it converts the tree to a SymPy expression and then factors, expands,
    solves and substitutes.  A property that :func:`manifest_set` calls manifest but this function
    calls false is a defect in the shape rules; :func:`truth_audit` sweeps for it.
    """
    expr = to_sympy(tree)
    symbol = Symbol(variable, real=True) if variable is not None else None
    return tuple(item.name for item in PROPERTIES if item.truth(expr, symbol))


# ------------------------------------------------------------------------------ per-world choice


def writing_costs(item: MathObject, grammar: Grammar) -> dict[str, int]:
    """Bracket cost of each named writing of the object under one world."""
    return {
        writing.role: render(object_tree(writing), grammar).count("(")
        for writing in item.writings
    }


def chosen_writing(item: MathObject, grammar: Grammar) -> Writing:
    """The writing this world writes the object in: the cheapest, ties to the declared order.

    This is where a grammar changes what is visible under the primary regime.  The world does not
    reach into a written form and hide part of it; it decides which of the object's named forms is
    the one you write without thinking, and the forms differ in what they show.
    """
    costs = writing_costs(item, grammar)
    best = min(costs.values())
    for writing in item.writings:
        if costs[writing.role] == best:
            return writing
    raise AssertionError("unreachable")  # pragma: no cover


#: The two master shapes a written form can have, and the reason the vocabulary is not neutral
#: between them.  ``monomial_sum`` carries four of the seven properties (leading coefficient,
#: constant term, sign structure, even parity) plus a share of ``degree``; ``factored`` carries two
#: (roots, factor structure) plus the same share of ``degree``.  A world that prefers monomial-sum
#: writings therefore scores higher on the raw manifest count BY CONSTRUCTION OF THE VOCABULARY,
#: which is why the world ranking below is reported with that caveat attached rather than as a
#: statement about which convention reveals more mathematics.
SHAPES: tuple[str, ...] = ("monomial_sum", "factored", "neither")


def written_shape(written: Surface, opaque: bool, variable: str | None) -> str:
    """Which master shape a written form has, for the shape-bias accounting."""
    if monomial_sum(written, opaque, variable) is not None:
        return "monomial_sum"
    if factored_shape(written, opaque, variable) is not None:
        return "factored"
    top, visible = _look(written, opaque)
    if visible and isinstance(top, Op) and top.operator in ("*", "/"):
        parts = multiplicative_parts(written, opaque)
        if sum(1 for part in parts if not part.inverted and not part.is_atom) >= 1:
            return "factored"
    return "neither"


def _cell(payload: tuple[MathObject, str, bool]) -> dict[str, Any]:
    """One (object, world) cell: which writing wins there, and what it makes manifest."""
    item, grammar_id, opaque = payload
    grammar = GRAMMAR_BY_ID[grammar_id]
    costs = writing_costs(item, grammar)
    writing = chosen_writing(item, grammar)
    tree = object_tree(writing)
    written = surface(tree, grammar)
    return {
        "object": item.name,
        "grammar": grammar_id,
        "role": writing.role,
        "cost": costs[writing.role],
        "costs": costs,
        "text": render(tree, grammar),
        "shape": written_shape(written, opaque, item.variable),
        "signs": visible_signs(written, opaque),
        "manifest": manifest_set(tree, grammar, item.variable, opaque),
    }


# ------------------------------------------------------------------------------------ concurrency
#
# Repository policy is multicore by default, and it also says a sequential path is a valid outcome
# when a MEASUREMENT justifies it.  The numbers below were measured here, by
# :func:`parallel_decision` on this machine, and not carried over from 0034 or 0037.

#: Cores kept free so a sweep cannot starve the interactive session.
WORKER_HEADROOM_CORES: int = 2

#: An upper bound on the spawn cost any one sweep has to amortise.
WORKER_CAP: int = 12

#: Measured cost of raising a spawn-start pool whose workers each import this module, and so SymPy.
#:
#: **Measured here, not inherited.**  :func:`measure_pool_startup` raises a pool of the default
#: worker count and runs one trivial cell in each; the recorded run on 16 cores with 12 workers is
#: ``0.97`` s, minimum of three, and this constant rounds it up.  A pool whose task is a builtin
#: measures ``0.24`` s on the same machine, which is the trap: the cost that matters is the workers
#: importing this module, and therefore SymPy.
POOL_STARTUP_SECONDS: float = 1.2

#: Measured seconds for one visibility cell - one object rendered in each of its writings under one
#: world, plus the seven shape tests, all pure Python.  Recorded run: ``0.2046`` s for ``850``
#: cells, minimum of three, i.e. ``2.4e-4`` s each.  See :func:`parallel_decision`.
CELL_SECONDS: float = 2.4e-04


def worker_count_for(cores: int, cell_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``cell_count`` independent cells."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(cell_count, 1)))


def default_worker_count(cell_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, cell_count)


def should_parallelise(cell_count: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising, from the measured per-cell cost and the measured spawn cost."""
    if workers <= 1 or cell_count <= 1:
        return False
    sequential = cell_count * seconds_per_cell
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_cells(payloads: Sequence[Any], workers: int | None) -> list[dict[str, Any]]:
    """Run one independent cell per payload, across processes when the measurement says to.

    Every cell is a pure function of its payload and ``executor.map`` preserves order, so the two
    paths return identical records.  The test suite asserts that rather than assuming it.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(len(payloads), CELL_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_cell(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_cell, payloads, chunksize=1))


def _trivial_cell(payload: int) -> int:
    """A cell that does nothing, so that timing it times only the pool - and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` is the input to :func:`should_parallelise`, so it has to be a
    measurement and not a number carried over from another experiment.  Minimum of ``repeats`` runs,
    because a startup time is a floor that background load can only push up.
    """
    resolved = default_worker_count(64) if workers is None else workers
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as executor:
            list(executor.map(_trivial_cell, range(resolved), chunksize=1))
        best = min(best, time.perf_counter() - start)
    return {
        "workers": resolved,
        "cores": os.cpu_count(),
        "repeats": repeats,
        "seconds": best,
        "declared": POOL_STARTUP_SECONDS,
    }


def parallel_decision(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """Time both paths over the same work and check they agree, then record which one won."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [(item, grammar.id, False) for item in corpus for grammar in grammars]
    workers = default_worker_count(len(payloads))

    start = time.perf_counter()
    sequential = _map_cells(payloads, workers=1)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    parallel = _map_cells(payloads, workers=workers)
    parallel_seconds = time.perf_counter() - start

    speedup = sequential_seconds / parallel_seconds if parallel_seconds else float("inf")
    return {
        "cores": os.cpu_count(),
        "cells": len(payloads),
        "workers": workers,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": speedup,
        "identical": sequential == parallel,
        "seconds_per_cell": sequential_seconds / len(payloads) if payloads else 0.0,
        "declared_seconds_per_cell": CELL_SECONDS,
        "parallel_worth_it": should_parallelise(len(payloads), CELL_SECONDS, workers),
        "default_path": (
            "parallel" if should_parallelise(len(payloads), CELL_SECONDS, workers) else "sequential"
        ),
    }


# --------------------------------------------------------------------------------------- audits


def corpus_audit(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Check the corpus is what it claims before any number is computed from it."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    names = [item.name for item in corpus]
    duplicates = tuple(sorted({name for name in names if names.count(name) > 1}))

    non_canonical = []
    for item in corpus:
        for writing in item.writings:
            if render(object_tree(writing), CONTROL) != writing.source:
                non_canonical.append(f"{item.name}.{writing.role}")

    disagreeing = []
    for item in corpus:
        if len(item.writings) != 2:
            continue
        first, second = (to_sympy(object_tree(writing)) for writing in item.writings)
        if simplify(first - second) != 0:
            disagreeing.append(item.name)

    undeclared = tuple(
        sorted(
            {law.name for law in LAW_CORPUS} - set(PRINCIPAL_VARIABLES)
            | (set(PRINCIPAL_VARIABLES) - {law.name for law in LAW_CORPUS} - {CALIBRATION.name})
        )
    )
    with_variable = sum(1 for item in corpus if item.variable is not None)
    return {
        "objects": len(corpus),
        "writings": sum(len(item.writings) for item in corpus),
        "two_sided": sum(1 for item in corpus if len(item.writings) == 2),
        "one_sided": sum(1 for item in corpus if len(item.writings) == 1),
        "fields": tuple(sorted({item.field for item in corpus})),
        "duplicate_names": duplicates,
        "canonical_sources": not non_canonical,
        "non_canonical": tuple(non_canonical),
        "identities_hold": not disagreeing,
        "disagreeing_identities": tuple(disagreeing),
        "undeclared_variables": undeclared,
        "objects_with_variable": with_variable,
        "objects_without_variable": len(corpus) - with_variable,
        "imported_law_count": len(LAW_CORPUS),
    }


def bridge_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """The correctness bridge, inherited whole from 0034 and recounted over THIS corpus.

    Three things must hold before a manifest set means anything.  The rendering must re-parse under
    its own grammar to the tree it came from, or the string being inspected is not a writing of the
    object at all.  It must carry no bracket the grammar does not require, or the shape rules are
    reading punctuation the convention never forced.  And :func:`surface` must mirror ``render``
    exactly, or the shape rules are reading a different string from the one that was priced.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    formulas = as_notational_cost_corpus(corpus)
    mirror_failures = []
    mirrors = 0
    for item in corpus:
        for writing in item.writings:
            tree = object_tree(writing)
            for grammar in grammars:
                mirrors += 1
                if surface_text(surface(tree, grammar)) != render(tree, grammar):
                    mirror_failures.append(f"{item.name}.{writing.role}@{grammar.id}")
    return {
        "round_trip": round_trip_audit(formulas, grammars),
        "minimality": minimality_audit(formulas, grammars),
        "surface_mirror": {
            "checks": mirrors,
            "failures": len(mirror_failures),
            "failing": tuple(mirror_failures),
            "holds": not mirror_failures,
        },
    }


def truth_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    regimes: Sequence[str] = REGIMES,
) -> dict[str, Any]:
    """Manifest implies true, swept over every object, every world, every regime.

    A manifest set that ever claims something ground truth denies is a defect in the shape rules,
    not a finding, and this is the sweep that would catch it.  ``violations`` must be empty.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    truths = {
        item.name: set(ground_truth(object_tree(item.writings[0]), item.variable))
        for item in corpus
    }
    violations = []
    checks = 0
    for item in corpus:
        for grammar in grammars:
            for regime in regimes:
                cell = _cell((item, grammar.id, regime == "opaque"))
                checks += len(cell["manifest"])
                for name in cell["manifest"]:
                    if name not in truths[item.name]:
                        violations.append(
                            {
                                "object": item.name,
                                "grammar": grammar.id,
                                "regime": regime,
                                "property": name,
                                "text": cell["text"],
                            }
                        )
    return {
        "checks": checks,
        "cells": len(corpus) * len(grammars) * len(regimes),
        "violations": tuple(violations),
        "sound": not violations,
    }


def identity_truth_audit(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """The two writings of a two-sided law must agree on ground truth, since they are one object.

    They are the same object, so anything ground truth says of one it must say of the other.  If
    that ever fails, the ground-truth rules are reading the WRITING and not the OBJECT, which would
    void the control.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    mismatched = []
    for item in corpus:
        if len(item.writings) != 2:
            continue
        first, second = (
            ground_truth(object_tree(writing), item.variable) for writing in item.writings
        )
        if first != second:
            mismatched.append(
                {"object": item.name, "first": first, "second": second}
            )
    return {
        "two_sided": sum(1 for item in corpus if len(item.writings) == 2),
        "mismatched": tuple(mismatched),
        "writing_independent": not mismatched,
    }


# ------------------------------------------------------------------------------ the main table


def _ranked(totals: dict[str, int]) -> tuple[dict[str, Any], ...]:
    """Competition ranking (``1, 2, 2, 4``) over per-world totals, most manifest first."""
    order = sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
    ranking = []
    previous_total: int | None = None
    previous_rank = 0
    for position, (grammar_id, total) in enumerate(order, start=1):
        rank = previous_rank if total == previous_total else position
        ranking.append({"rank": rank, "id": grammar_id, "total": total})
        previous_total, previous_rank = total, rank
    return tuple(ranking)


def _precedence_label(grammar: Grammar) -> str:
    return " ".join("".join(level) for level in grammar.levels)


def visibility_table(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    opaque: bool = False,
    workers: int | None = None,
) -> dict[str, Any]:
    """Per object and per world, the manifest set - and the aggregates the card asks for.

    The aggregates are stated at two levels, because "manifest in every world" is ambiguous and
    both readings are interesting:

    * **per property**: in how many of the worlds is it manifest for at least one object?  A
      property manifest in every world is universally visible; one manifest in none is universally
      hidden, and that row is the one the card expects to be most interesting.
    * **per object**: which of its properties does every world make manifest, and which does no
      world make manifest even though they are true of it?
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [(item, grammar.id, opaque) for item in corpus for grammar in grammars]
    cells = _map_cells(payloads, workers)
    by_object: dict[str, dict[str, dict[str, Any]]] = {item.name: {} for item in corpus}
    for cell in cells:
        by_object[cell["object"]][cell["grammar"]] = cell

    rows = []
    for item in corpus:
        truth = ground_truth(object_tree(item.writings[0]), item.variable)
        per_grammar = by_object[item.name]
        sets = {gid: set(cell["manifest"]) for gid, cell in per_grammar.items()}
        everywhere = set.intersection(*sets.values()) if sets else set()
        somewhere = set.union(*sets.values()) if sets else set()
        rows.append(
            {
                "object": item.name,
                "field": item.field,
                "variable": item.variable,
                "roles": item.roles,
                "truth": truth,
                "per_grammar": per_grammar,
                "manifest_everywhere": tuple(n for n in PROPERTY_NAMES if n in everywhere),
                "manifest_somewhere": tuple(n for n in PROPERTY_NAMES if n in somewhere),
                "true_but_never_manifest": tuple(
                    n for n in PROPERTY_NAMES if n in truth and n not in somewhere
                ),
                "chosen_roles": {gid: cell["role"] for gid, cell in per_grammar.items()},
                "distinct_role_choices": len({cell["role"] for cell in per_grammar.values()}),
                "distinct_texts": len({cell["text"] for cell in per_grammar.values()}),
                "distinct_manifest_sets": len(
                    {tuple(cell["manifest"]) for cell in per_grammar.values()}
                ),
            }
        )

    property_worlds: dict[str, tuple[str, ...]] = {}
    property_objects: dict[str, tuple[str, ...]] = {}
    for name in PROPERTY_NAMES:
        worlds = tuple(
            grammar.id
            for grammar in grammars
            if any(name in by_object[item.name][grammar.id]["manifest"] for item in corpus)
        )
        objects = tuple(
            item.name
            for item in corpus
            if any(name in cell["manifest"] for cell in by_object[item.name].values())
        )
        property_worlds[name] = worlds
        property_objects[name] = objects

    totals = {
        grammar.id: sum(len(by_object[item.name][grammar.id]["manifest"]) for item in corpus)
        for grammar in grammars
    }
    ranking = _ranked(totals)
    rank_by_id = {row["id"]: row["rank"] for row in ranking}

    truth_totals = {
        name: sum(1 for row in rows if name in row["truth"]) for name in PROPERTY_NAMES
    }
    hidden_pairs = tuple(
        (row["object"], name) for row in rows for name in row["true_but_never_manifest"]
    )
    shape_counts = {
        grammar.id: {
            shape: sum(
                1 for item in corpus if by_object[item.name][grammar.id]["shape"] == shape
            )
            for shape in SHAPES
        }
        for grammar in grammars
    }
    return {
        "regime": "opaque" if opaque else "transparent",
        "objects": len(corpus),
        "grammars": len(grammars),
        "cells": len(cells),
        "rows": tuple(rows),
        "totals": totals,
        "ranking": ranking,
        "control_id": CONTROL.id,
        "control_total": totals[CONTROL.id],
        "control_rank": rank_by_id[CONTROL.id],
        "best": ranking[0],
        "worst": ranking[-1],
        "best_ids": tuple(row["id"] for row in ranking if row["rank"] == ranking[0]["rank"]),
        "precedence": {grammar.id: _precedence_label(grammar) for grammar in grammars},
        "property_worlds": property_worlds,
        "property_world_counts": {n: len(v) for n, v in property_worlds.items()},
        "property_objects": property_objects,
        "property_object_counts": {n: len(v) for n, v in property_objects.items()},
        "property_truth_counts": truth_totals,
        "universally_visible": tuple(
            n for n in PROPERTY_NAMES if len(property_worlds[n]) == len(grammars)
        ),
        "universally_hidden": tuple(n for n in PROPERTY_NAMES if not property_worlds[n]),
        "true_somewhere_but_manifest_nowhere": tuple(
            n for n in PROPERTY_NAMES if not property_worlds[n] and truth_totals[n] > 0
        ),
        "worlds_without": {
            name: tuple(g.id for g in grammars if g.id not in set(property_worlds[name]))
            for name in PROPERTY_NAMES
        },
        "hidden_pairs": hidden_pairs,
        "hidden_pair_count": len(hidden_pairs),
        "hidden_by_property": {
            name: sum(1 for _, prop in hidden_pairs if prop == name) for name in PROPERTY_NAMES
        },
        "objects_with_nothing_manifest": tuple(
            row["object"] for row in rows if not row["manifest_somewhere"]
        ),
        "shape_counts": shape_counts,
    }


# ------------------------------------------------------------------------------------ the trade


def tradeoff_report(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    opaque: bool = False,
    workers: int | None = None,
) -> dict[str, Any]:
    """Is there any world that makes EVERY true property of an object manifest at once?

    If not, the trade is unavoidable, and the report is then the maximum simultaneous set per
    object plus the pairs of properties no single world ever shows together.  A pair that is never
    co-manifest anywhere in the grid is a structural finding about the notation, so it is separated
    from the pairs that are excluded by the shape rules themselves - a pair the rules forbid is a
    fact about the rules, not about mathematics, and saying otherwise would be circular.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    table = visibility_table(corpus, grammars, opaque=opaque, workers=workers)

    per_object = []
    complete_cells = 0
    for row in table["rows"]:
        truth = set(row["truth"])
        best_size = -1
        best: tuple[str, ...] = ()
        best_worlds: list[str] = []
        for grammar in grammars:
            manifest = set(row["per_grammar"][grammar.id]["manifest"])
            if len(manifest) > best_size:
                best_size = len(manifest)
                best = tuple(n for n in PROPERTY_NAMES if n in manifest)
                best_worlds = [grammar.id]
            elif len(manifest) == best_size and tuple(
                n for n in PROPERTY_NAMES if n in manifest
            ) == best:
                best_worlds.append(grammar.id)
        complete = [
            grammar.id
            for grammar in grammars
            if set(row["per_grammar"][grammar.id]["manifest"]) == truth and truth
        ]
        complete_cells += len(complete)
        per_object.append(
            {
                "object": row["object"],
                "truth": row["truth"],
                "true_count": len(truth),
                "max_simultaneous": best,
                "max_simultaneous_count": best_size,
                "max_worlds": tuple(best_worlds),
                "complete_worlds": tuple(complete),
                "fully_visible_somewhere": bool(complete),
                "hidden_from_every_world": row["true_but_never_manifest"],
            }
        )

    co_manifest: dict[tuple[str, str], int] = {}
    seen_alone: dict[str, int] = {name: 0 for name in PROPERTY_NAMES}
    for row in table["rows"]:
        for grammar in grammars:
            manifest = set(row["per_grammar"][grammar.id]["manifest"])
            for name in manifest:
                seen_alone[name] += 1
            for first, second in combinations(PROPERTY_NAMES, 2):
                if first in manifest and second in manifest:
                    co_manifest[(first, second)] = co_manifest.get((first, second), 0) + 1

    pairs = []
    for first, second in combinations(PROPERTY_NAMES, 2):
        together = co_manifest.get((first, second), 0)
        both_possible = seen_alone[first] > 0 and seen_alone[second] > 0
        pairs.append(
            {
                "pair": (first, second),
                "co_manifest_cells": together,
                "both_manifest_somewhere": both_possible,
                "mutually_exclusive": both_possible and together == 0,
                "excluded_by_rule": _rule_level_exclusion(first, second),
            }
        )

    exclusive = tuple(p["pair"] for p in pairs if p["mutually_exclusive"])
    return {
        "regime": table["regime"],
        "per_object": tuple(per_object),
        "objects_fully_visible_somewhere": sum(
            1 for row in per_object if row["fully_visible_somewhere"]
        ),
        "objects_with_a_true_property": sum(1 for row in per_object if row["true_count"] > 0),
        "complete_cells": complete_cells,
        "any_world_shows_everything": complete_cells > 0,
        "pairs": tuple(pairs),
        "mutually_exclusive_pairs": exclusive,
        "mutually_exclusive_by_rule": tuple(
            p["pair"] for p in pairs if p["mutually_exclusive"] and p["excluded_by_rule"]
        ),
        "mutually_exclusive_by_measurement": tuple(
            p["pair"] for p in pairs if p["mutually_exclusive"] and not p["excluded_by_rule"]
        ),
        "table": table,
    }


#: Properties whose shape rule demands a multiplicative top-level operator, and those that demand an
#: additive one.  A tree's root operator is one or the other, so any pair drawn across the two lists
#: can never be co-manifest - and that is a fact about the RULES, reported separately from pairs the
#: corpus turns out never to show together.
_MULTIPLICATIVE_TOP: frozenset[str] = frozenset({"roots", "factor_structure"})
_ADDITIVE_TOP: frozenset[str] = frozenset({"sign_structure"})


def _rule_level_exclusion(first: str, second: str) -> bool:
    """Whether the two shape rules demand incompatible top-level operators."""
    pair = {first, second}
    return bool(pair & _MULTIPLICATIVE_TOP) and bool(pair & _ADDITIVE_TOP)


# ---------------------------------------------------------------------------------- null model


def null_model(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    opaque: bool = False,
    workers: int | None = None,
) -> dict[str, Any]:
    """Objects that cannot carry a conclusion, and the aggregates with and without them.

    An object whose manifest set is the same in every world says nothing about conventions; it only
    inflates every world's total by the same amount.  Three nested notions are counted, because
    they are not the same thing:

    * **constant text**: the rendered string is identical in all twenty-five worlds;
    * **constant choice**: every world picks the same writing (implied by a single-writing object);
    * **constant manifest set**: the manifest set is identical in all twenty-five worlds - the one
      that actually matters, and the one the movable subcorpus is defined by.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    full = visibility_table(corpus, grammars, opaque=opaque, workers=workers)

    constant_text = tuple(row["object"] for row in full["rows"] if row["distinct_texts"] == 1)
    constant_choice = tuple(
        row["object"] for row in full["rows"] if row["distinct_role_choices"] == 1
    )
    constant_manifest = tuple(
        row["object"] for row in full["rows"] if row["distinct_manifest_sets"] == 1
    )
    movable = tuple(item for item in corpus if item.name not in set(constant_manifest))
    forced_total = sum(
        len(row["per_grammar"][CONTROL.id]["manifest"])
        for row in full["rows"]
        if row["object"] in set(constant_manifest)
    )

    if movable:
        reduced = visibility_table(movable, grammars, opaque=opaque, workers=workers)
        reduced_ranking = reduced["ranking"]
        reduced_control_rank = reduced["control_rank"]
        reduced_spread = reduced["best"]["total"] - reduced["worst"]["total"]
    else:  # pragma: no cover - the corpus is never wholly null
        reduced_ranking = ()
        reduced_control_rank = None
        reduced_spread = 0

    full_order = tuple(row["id"] for row in full["ranking"])
    reduced_order = tuple(row["id"] for row in reduced_ranking)
    return {
        "regime": full["regime"],
        "objects": len(corpus),
        "constant_text": constant_text,
        "constant_text_count": len(constant_text),
        "constant_choice": constant_choice,
        "constant_choice_count": len(constant_choice),
        "constant_manifest": constant_manifest,
        "constant_manifest_count": len(constant_manifest),
        "movable_count": len(movable),
        "forced_total_under_control": forced_total,
        "full_spread": full["best"]["total"] - full["worst"]["total"],
        "reduced_spread": reduced_spread,
        "full_control_rank": full["control_rank"],
        "reduced_control_rank": reduced_control_rank,
        "ranking_order_identical": full_order == reduced_order,
        "full_ranking": full["ranking"],
        "reduced_ranking": reduced_ranking,
        "reduced_universally_visible": (
            visibility_table(movable, grammars, opaque=opaque, workers=workers)[
                "universally_visible"
            ]
            if movable
            else ()
        ),
    }


# ------------------------------------------------------------------------------------- the report


def calibration_report(grammars: Sequence[Grammar] | None = None) -> dict[str, Any]:
    """The manager's calibration case, reproduced in full.

    Seventeen worlds are said to write ``2x^2 + 3x - 5`` expanded and eight factored.  That split is
    the thing this module has to reproduce before any of its own numbers mean anything.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    per_grammar = {}
    for grammar in grammars:
        cell = _cell((CALIBRATION, grammar.id, False))
        per_grammar[grammar.id] = cell
    roles = [cell["role"] for cell in per_grammar.values()]
    expanded_tree = object_tree(CALIBRATION.writings[0])
    factored_tree = object_tree(CALIBRATION.writings[1])
    return {
        "object": CALIBRATION.name,
        "variable": CALIBRATION.variable,
        "truth": ground_truth(expanded_tree, CALIBRATION.variable),
        "expanded_manifest": manifest_set(expanded_tree, CONTROL, CALIBRATION.variable),
        "factored_manifest": manifest_set(factored_tree, CONTROL, CALIBRATION.variable),
        "expanded_worlds": tuple(
            gid for gid, cell in per_grammar.items() if cell["role"] == "expanded"
        ),
        "factored_worlds": tuple(
            gid for gid, cell in per_grammar.items() if cell["role"] == "factored"
        ),
        "expanded_count": roles.count("expanded"),
        "factored_count": roles.count("factored"),
        "per_grammar": per_grammar,
    }


def manifest_properties_report(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Everything experiment 0038 publishes, in both regimes."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    return {
        "corpus": corpus_audit(corpus),
        "bridge": bridge_audit(corpus, grammars),
        "soundness": truth_audit(corpus, grammars),
        "writing_independence": identity_truth_audit(corpus),
        "calibration": calibration_report(grammars),
        "transparent": {
            "visibility": visibility_table(corpus, grammars, opaque=False, workers=workers),
            "tradeoff": tradeoff_report(corpus, grammars, opaque=False, workers=workers),
            "null_model": null_model(corpus, grammars, opaque=False, workers=workers),
        },
        "opaque": {
            "visibility": visibility_table(corpus, grammars, opaque=True, workers=workers),
            "tradeoff": tradeoff_report(corpus, grammars, opaque=True, workers=workers),
            "null_model": null_model(corpus, grammars, opaque=True, workers=workers),
        },
        "properties": tuple(
            {
                "name": item.name,
                "rule": item.rule,
                "truth_rule": item.truth_rule,
                "needs_variable": item.needs_variable,
                "note": item.note,
            }
            for item in PROPERTIES
        ),
    }
