"""Generation 2: what the flagship result does once the language can spell a power.

Experiment 0045, and the first executable work on ROADMAP thesis **T25**.

Why this module exists
----------------------

Experiment 0035 is the result this repository is known for::

    a*x*x + b*x + c    is our quadratic in 13 of the 25 worlds,
                       and the cubic a*x*(b + x)*(c + x), roots 0, -b, -c, in the other 12.

That sentence is true of Generation 1. It is also, possibly, an artifact of a missing operator:
Generation 1 has no exponentiation, so a square has to be written as a product, and it is the
``x * x`` chain - not the quadratic - that carries the whole finding. A language with ``^`` writes
the same object ``a * x^2 + b * x + c``, the chain is gone, and the question is whether anything
survives. **The honest answer is the deliverable here, and it is a negative one.** See
:func:`quadratic_worlds`.

The language
------------

Generation 2 is Generation 1 plus exactly one binary operator, ``^``, and nothing else. T26 -
juxtaposition and unary minus - is explicitly out of scope; ``2x`` and ``-x`` are still unwritable.

Five operators give ``5! = 120`` strict precedence orderings. The registry adds the conventional
tied-level control - ``^`` alone at the top, then ``* /``, then ``+ -`` - for **121** grammars in
all, exactly as Generation 1 is ``4! = 24`` strict orderings plus one control for 25.

``^`` is RIGHT-associative, and this is not optional
----------------------------------------------------

``2^3^2`` is ``2^9 = 512``, not ``(2^3)^2 = 64``. Every other operator in this project is
left-associative, so Generation 2 is the first grammar family here whose associativity is not
uniform. A Generation 2 that quietly made ``^`` left-associative would be measuring a language
nobody uses, so the asymmetry is implemented in :class:`Parser2`, disclosed in the reports, and
pinned by test on the hand-worked example above and on a tree comparison.

The asymmetry is a single term in the parser, and the whole renderer follows from it::

    right operand parsed at   power(op) + 1   for a left-associative operator
                              power(op)       for a right-associative one

Read the bracket thresholds off those two lines and nothing else is needed - see
:func:`child_threshold2`, whose left-hand rule depends on the CHILD's associativity and whose
right-hand rule depends on the PARENT's.

The shared parser is not touched
--------------------------------

:mod:`parseatlas.parser` and :mod:`parseatlas.grammar` are Generation 1 and stay Generation 1.
Generation 2 gets its own tokenizer and its own parser here, which raises the obligation this
module discharges first: **is Generation 2 a conservative extension?** :func:`agreement_audit`
parses a corpus of Generation 1 source strings with the Generation 2 parser under every embedding
of every Generation 1 grammar, and requires the tree to be byte-identical to
:func:`parseatlas.parser.parse`'s, cell by cell. If that fails nothing else in this module means
anything, which is why it is first in the module, first in the tests and first in the report.

The node types are Generation 1's own :class:`parseatlas.parser.Binary`, :class:`~parseatlas.parser.Number`
and :class:`~parseatlas.parser.Variable`, so the comparison is dataclass equality and not a
translation between two tree formats.

The null model, which bites harder here than in Generation 1
-------------------------------------------------------------

T6 (operator-support reduction) says a parse depends only on the precedence order restricted to the
operators actually present. With five operators that is a much larger discount: an entry using
three operators partitions the 120 strict orderings into ``3! = 6`` blocks of 20 and cannot tell
grammars inside a block apart at all. So "13 of 25" and "61 of 121" can be the SAME measurement
reported against two registries, and the difference between those numbers is arithmetic about the
registry rather than anything about mathematics. Every count in this module is therefore reported
next to its block structure - see :func:`distinguishing_power` - and every ranking is recomputed
over the entries that can actually move.
"""

import os
import re
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from math import factorial
from typing import Any

from sympy import (
    Add,
    Integer,
    Mul,
    Poly,
    Pow,
    Rational,
    Symbol,
    cos,
    factor,
    roots,
    simplify,
    sin,
    solve,
)
from sympy.polys.polyerrors import PolynomialError

from .alternative_mathematics import (
    ROOT_DOMAIN,
    STANDARD_CATALOGUE,
    principal_symbol,
    requires_radical,
    root_list_is_complete,
    semantic_key,
    solving_symbol,
)
from .canonical import canonicalize as canonicalize1
from .grammar import Grammar, all_grammars
from .notational_cost import (
    CORPUS as GENERATION_ONE_CORPUS,
    RoundTripError,
    binding_powers,
    bracket_pairs,
)
from .notational_cost import parenthesis_cost as parenthesis_cost1
from .notational_cost import render as render1
from .parser import Binary, Node, Number, Variable, parse

# --------------------------------------------------------------------------------- the language

#: The five operators of Generation 2. ``^`` is the only addition to Generation 1's four.
OPERATORS_2: tuple[str, ...] = ("^", "*", "/", "+", "-")

#: Associativity per operator. ``^`` is the only right-associative operator in this project, and
#: the only reason Generation 2 needs a parser of its own rather than a wider grammar registry.
ASSOCIATIVITY: dict[str, str] = {"^": "right", "*": "left", "/": "left", "+": "left", "-": "left"}

#: The hand-worked example the associativity is pinned on: ``2^3^2`` is ``2^9``, not ``8^2``.
RIGHT_ASSOCIATIVE_WITNESS: str = "2^3^2"

_TOKEN_2 = re.compile(
    r"\s*(?:(?P<number>\d+(?:/\d+)?)|(?P<name>[A-Za-z_]\w*)"
    r"|(?P<operator>[\^+\-*/])|(?P<left>\()|(?P<right>\)))"
)


@dataclass(frozen=True)
class Token2:
    kind: str
    value: str


def tokenize2(source: str) -> tuple[Token2, ...]:
    """Generation 1's tokenizer with ``^`` added to the operator class and nothing else changed.

    The number pattern is copied verbatim, including the fact that an unspaced ``1/2`` is ONE
    rational literal rather than a division. Changing it would break the conservative-extension
    audit on any Generation 1 string containing such a literal, which is exactly the kind of silent
    divergence :func:`agreement_audit` exists to catch.
    """
    tokens: list[Token2] = []
    position = 0
    while position < len(source):
        match = _TOKEN_2.match(source, position)
        if not match:
            raise ValueError(f"Unexpected character at position {position}: {source[position]!r}")
        kind = match.lastgroup
        assert kind is not None
        tokens.append(Token2(kind, match.group(kind)))
        position = match.end()
    tokens.append(Token2("eof", ""))
    return tuple(tokens)


class Parser2:
    """Precedence-climbing over five operators, with per-operator associativity.

    This is :class:`parseatlas.parser.Parser` with one term changed: the minimum power the right
    operand is parsed at is ``power(op) + 1`` for a left-associative operator and ``power(op)`` for
    a right-associative one. Equal power on the right is what lets ``^`` re-enter its own loop and
    nest to the right; the ``+ 1`` is what stops every other operator from doing so.
    """

    def __init__(self, tokens: tuple[Token2, ...], grammar: Grammar) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.index = 0
        self._powers = binding_powers(grammar)

    def parse(self) -> Node:
        result = self._expression(0)
        if self._current.kind != "eof":
            raise ValueError(f"Unexpected token: {self._current.value!r}")
        return result

    @property
    def _current(self) -> Token2:
        return self.tokens[self.index]

    def _advance(self) -> Token2:
        token = self._current
        self.index += 1
        return token

    def _expression(self, minimum_power: int) -> Node:
        left = self._primary()
        while self._current.kind == "operator" and self._powers[self._current.value] >= minimum_power:
            operator = self._advance().value
            power = self._powers[operator]
            right_minimum = power if ASSOCIATIVITY[operator] == "right" else power + 1
            left = Binary(operator, left, self._expression(right_minimum))
        return left

    def _primary(self) -> Node:
        token = self._advance()
        if token.kind == "number":
            if "/" in token.value:
                numerator, denominator = token.value.split("/", 1)
                return Number(Fraction(int(numerator), int(denominator)))
            return Number(Fraction(int(token.value)))
        if token.kind == "name":
            return Variable(token.value)
        if token.kind == "left":
            result = self._expression(0)
            if self._advance().kind != "right":
                raise ValueError("Expected closing parenthesis")
            return result
        raise ValueError(f"Expected number, variable, or parenthesized expression; got {token.value!r}")


def parse2(source: str, grammar: Grammar) -> Node:
    """Parse ``source`` under a Generation 2 grammar into Generation 1's own node types."""
    return Parser2(tokenize2(source), grammar).parse()


# --------------------------------------------------------------------------------- the registry


def strict_grammars_2() -> tuple[Grammar, ...]:
    """The ``5! = 120`` strict orderings of the five operators, ``H001`` .. ``H120``.

    The ``H`` prefix keeps every Generation 2 identifier distinct from every Generation 1 ``G``
    identifier, so no table in this project can quietly compare a ``G12`` with an ``H12``.
    """
    from itertools import permutations

    return tuple(
        Grammar(f"H{index:03d}", ordering)
        for index, ordering in enumerate(permutations(OPERATORS_2), start=1)
    )


def control_grammar_2() -> Grammar:
    """The conventional Generation 2 control: ``^`` tightest, then ``* /`` tied, then ``+ -`` tied.

    This is how mathematics is written today, and it is the only grammar in the registry with tied
    levels, exactly as ``G0`` is in Generation 1.
    """
    return Grammar("H0", ("^", "*", "/", "+", "-"), (("^",), ("*", "/"), ("+", "-")))


#: The Generation 2 registry: the control first, then the 120 strict orderings. Size ``121``.
GRAMMARS_2: tuple[Grammar, ...] = (control_grammar_2(), *strict_grammars_2())

#: The conventional grammar, and the baseline every other grammar is read against.
CONTROL_2: Grammar = GRAMMARS_2[0]

#: The Generation 1 registry, for the side-by-side halves of every table here.
GRAMMARS_1: tuple[Grammar, ...] = all_grammars()

#: The Generation 1 control.
CONTROL_1: Grammar = GRAMMARS_1[0]


def embed_generation_one(grammar: Grammar, position: int) -> Grammar:
    """Insert ``^`` into a Generation 1 grammar as its own level at ``position``.

    Every such embedding restricts to ``grammar`` on ``+ - * /``, so by T6 all of them must parse a
    ``^``-free string identically to Generation 1. :func:`agreement_audit` checks every position of
    every grammar rather than only the natural ``position=0``, because "``^`` happens to be at the
    top" would be a much weaker statement than the one this module needs.
    """
    levels = list(grammar.levels)
    if not 0 <= position <= len(levels):
        raise ValueError(f"position must be in 0..{len(levels)}; got {position}")
    levels.insert(position, ("^",))
    ordered = tuple(tuple(level) for level in levels)
    flattened = tuple(operator for level in ordered for operator in level)
    return Grammar(f"{grammar.id}+^@{position}", flattened, ordered)


def embeddings_of(grammar: Grammar) -> tuple[Grammar, ...]:
    """Every position ``^`` can occupy in a Generation 1 grammar: ``len(levels) + 1`` of them."""
    return tuple(embed_generation_one(grammar, position) for position in range(len(grammar.levels) + 1))


# ------------------------------------------------------------------- the conservative extension

#: Hand-written Generation 1 strings that stress the parts of the parser the named corpora do not:
#: left-associative chains, nested brackets, a redundant bracket, and a bare literal.
AGREEMENT_EXTRA_SOURCES: tuple[str, ...] = (
    "a - b - c",
    "a / b / c",
    "a - (b - c)",
    "a / (b / c)",
    "1 - 2 - 3",
    "((a))",
    "a + b * c - d / e",
    "a * (b + c) / (d - e) + f",
    "1/2 + a",
    "a",
)


def generation_one_sources() -> tuple[str, ...]:
    """The Generation 1 corpus the agreement audit runs over, deduplicated in first-seen order.

    Three sources, all of them already published in this repository: experiment 0034's named-cost
    corpus, experiment 0035's standard-form catalogue, and :data:`AGREEMENT_EXTRA_SOURCES`.
    """
    seen: dict[str, None] = {}
    for formula in GENERATION_ONE_CORPUS:
        seen.setdefault(formula.source, None)
    for entry in STANDARD_CATALOGUE:
        seen.setdefault(entry.source, None)
    for source in AGREEMENT_EXTRA_SOURCES:
        seen.setdefault(source, None)
    return tuple(seen)


def agreement_audit(
    sources: Sequence[str] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Is Generation 2 a conservative extension of Generation 1? Checked cell by cell.

    For every Generation 1 grammar, every position ``^`` can be embedded at, and every Generation 1
    source string, :func:`parse2` must return the tree :func:`parseatlas.parser.parse` returns -
    equal as dataclasses, not merely equivalent. Any disagreement is reported with its cell.
    """
    sources = tuple(sources) if sources is not None else generation_one_sources()
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_1
    disagreements: list[dict[str, Any]] = []
    cells = 0
    embeddings = 0
    for grammar in grammars:
        for embedded in embeddings_of(grammar):
            embeddings += 1
            for source in sources:
                cells += 1
                expected = parse(source, grammar)
                produced = parse2(source, embedded)
                if produced != expected:
                    disagreements.append(
                        {
                            "source": source,
                            "generation_one_grammar": grammar.id,
                            "generation_two_grammar": embedded.id,
                            "expected": expected,
                            "produced": produced,
                        }
                    )
    return {
        "sources": len(sources),
        "generation_one_grammars": len(grammars),
        "embeddings": embeddings,
        "cells": cells,
        "disagreements": len(disagreements),
        "disagreeing": tuple(disagreements),
        "conservative": not disagreements,
    }


# --------------------------------------------------------------------------------- the renderer


def child_threshold2(
    parent_power: int, side: str, parent_associativity: str, child_associativity: str
) -> int:
    """The minimum power a child operator needs to stay unbracketed, derived from :class:`Parser2`.

    Both rules fall out of the loop in :meth:`Parser2._expression`, and they are not symmetric:

    * a LEFT child is the accumulated ``left`` of the same call, so it survives only if its own
      right recursion did not swallow the parent's operator - that recursion runs at
      ``power(child) + 1`` for a left-associative child and ``power(child)`` for a right-associative
      one, giving thresholds ``parent_power`` and ``parent_power + 1``. The threshold therefore
      depends on the CHILD's associativity;
    * a RIGHT child is produced by the recursion itself, at ``power(parent) + 1`` for a
      left-associative parent and ``power(parent)`` for a right-associative one. That threshold
      depends on the PARENT's associativity.

    The right-hand rule is why ``a^b^c`` needs no brackets and the left-hand rule is why
    ``(a^b)^c`` needs one.
    """
    if side == "left":
        return parent_power + (1 if child_associativity == "right" else 0)
    if side == "right":
        return parent_power + (0 if parent_associativity == "right" else 1)
    raise ValueError(f"side must be 'left' or 'right'; got {side!r}")


def needs_brackets2(child: Node, parent_operator: str, side: str, powers: dict[str, int]) -> bool:
    """Does ``child`` require brackets in this position? Leaves never do."""
    if not isinstance(child, Binary):
        return False
    threshold = child_threshold2(
        powers[parent_operator],
        side,
        ASSOCIATIVITY[parent_operator],
        ASSOCIATIVITY[child.operator],
    )
    return powers[child.operator] < threshold


def _render_node2(node: Node, powers: dict[str, int]) -> str:
    if isinstance(node, Number):
        value = node.value
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(node, Variable):
        return node.name
    left = _render_node2(node.left, powers)
    if needs_brackets2(node.left, node.operator, "left", powers):
        left = f"({left})"
    right = _render_node2(node.right, powers)
    if needs_brackets2(node.right, node.operator, "right", powers):
        right = f"({right})"
    # ``^`` is set tight and every other operator spaced, which is how mathematics is typeset and
    # how the corpus of this experiment is written. Whitespace is skipped by the tokenizer, so the
    # choice carries no semantic content whatever; it only has to be applied consistently for
    # ``render2(source) == source`` to be a meaningful corpus audit.
    if node.operator == "^":
        return f"{left}^{right}"
    return f"{left} {node.operator} {right}"


def render2(tree: Node, grammar: Grammar, verify: bool = True) -> str:
    """Write ``tree`` under a Generation 2 grammar with the minimum brackets that grammar requires.

    ``verify`` reparses the result and raises :class:`~parseatlas.notational_cost.RoundTripError`
    on mismatch, on by default for the same reason Generation 1 does it: the round trip is the
    property every number here rests on, so it is enforced in the path that produces the numbers.
    """
    text = _render_node2(tree, binding_powers(grammar))
    if verify:
        reparsed = parse2(text, grammar)
        if reparsed != tree:
            raise RoundTripError(
                f"render2/parse2 mismatch under {grammar.id}: {text!r} reparses to a different tree"
            )
    return text


def parenthesis_cost2(tree: Node, grammar: Grammar) -> int:
    """The number of bracket PAIRS a Generation 2 grammar forces on this tree."""
    return render2(tree, grammar).count("(")


def tree_operators2(tree: Node) -> tuple[str, ...]:
    """The distinct operators in ``tree``, in first-encounter order: its T6 support."""
    seen: dict[str, None] = {}
    stack: list[Node] = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, Binary):
            seen.setdefault(node.operator, None)
            stack.append(node.right)
            stack.append(node.left)
    return tuple(seen)


def _without_pair(text: str, pair: tuple[int, int]) -> str:
    open_index, close_index = pair
    return text[:open_index] + text[open_index + 1 : close_index] + text[close_index + 1 :]


def pair_is_required(text: str, pair: tuple[int, int], tree: Node, grammar: Grammar) -> dict[str, Any]:
    """Is one bracket pair of ``text`` load-bearing? Answered by deleting it and reparsing.

    Separated from :func:`minimality_witnesses2` so the check can be exercised on a writing that
    really does carry a redundant bracket. A renderer that never emits one cannot demonstrate that
    its own minimality check works, and a check that cannot fail is not evidence.
    """
    stripped = _without_pair(text, pair)
    try:
        reparsed: Node | None = parse2(stripped, grammar)
    except ValueError:
        reparsed = None
    return {
        "pair": pair,
        "rendering": text,
        "without_pair": stripped,
        "reparse_failed": reparsed is None,
        "required": reparsed != tree,
    }


def minimality_witnesses2(tree: Node, grammar: Grammar) -> tuple[dict[str, Any], ...]:
    """For each bracket pair in a rendering, the evidence that the grammar required it.

    Deleting the pair must make the string reparse to a different tree or fail to parse. This is an
    exhaustive search over the writing, not an argument about the renderer.
    """
    text = render2(tree, grammar)
    return tuple(pair_is_required(text, pair, tree, grammar) for pair in bracket_pairs(text))


# ------------------------------------------------------------------------------------ the corpus


@dataclass(frozen=True)
class Formula2:
    """One named piece of mathematics, in Generation 2 notation and - where it exists - in
    Generation 1 notation.

    ``generation_one_source`` is ``None`` exactly when the object cannot be written without ``^``:
    a symbolic exponent (``x^n``), or a base that is not the variable (``2^k``). Those entries are
    the mathematics Generation 1 could not express at all, and they are excluded by construction
    from every side-by-side ranking rather than silently compared against nothing.
    """

    name: str
    area: str
    source: str
    generation_one_source: str | None = None


#: Named mathematics that actually uses a power, written the way it is written today. Every source
#: is the minimal writing under :data:`CONTROL_2` - :func:`corpus_audit2` pins that, which is what
#: makes the published list an audit trail rather than a decoration.
CORPUS_2: tuple[Formula2, ...] = (
    # ---- algebra --------------------------------------------------------------------------------
    Formula2("quadratic_expanded", "algebra", "a * x^2 + b * x + c", "a * x * x + b * x + c"),
    Formula2("binomial_square_expanded", "algebra", "a^2 + 2 * a * b + b^2", "a * a + 2 * a * b + b * b"),
    Formula2("binomial_square_factored", "algebra", "(a + b)^2", "(a + b) * (a + b)"),
    Formula2("binomial_cube_factored", "algebra", "(a + b)^3", "(a + b) * (a + b) * (a + b)"),
    Formula2("difference_of_squares_expanded", "algebra", "a^2 - b^2", "a * a - b * b"),
    Formula2("difference_of_squares_factored", "algebra", "(a + b) * (a - b)", "(a + b) * (a - b)"),
    Formula2("discriminant", "algebra", "b^2 - 4 * a * c", "b * b - 4 * a * c"),
    Formula2("power_product_rule", "algebra", "x^m * x^n", None),
    Formula2("power_of_power_rule", "algebra", "(x^m)^n", None),
    Formula2("power_of_quotient_rule", "algebra", "(a / b)^n", None),
    Formula2("iterated_power", "algebra", "a^b^c", None),
    Formula2("geometric_term", "algebra", "a * r^n", None),
    Formula2("binary_place_value", "algebra", "2^k", None),
    # ---- geometry -------------------------------------------------------------------------------
    Formula2("pythagorean_form", "geometry", "a^2 + b^2 - c^2", "a * a + b * b - c * c"),
    Formula2("circle_form", "geometry", "x^2 + y^2 - r^2", "x * x + y * y - r * r"),
    Formula2(
        "law_of_cosines_form",
        "geometry",
        "a^2 + b^2 - 2 * a * b * costheta",
        "a * a + b * b - 2 * a * b * costheta",
    ),
    Formula2("cylinder_volume", "geometry", "pi * r^2 * h", "pi * r * r * h"),
    Formula2("sphere_volume", "geometry", "4 * pi * r^3 / 3", "4 * pi * r * r * r / 3"),
    Formula2(
        "squared_distance",
        "geometry",
        "(x2 - x1)^2 + (y2 - y1)^2",
        "(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)",
    ),
    # ---- calculus-adjacent -----------------------------------------------------------------------
    Formula2("power_rule_derivative", "calculus", "n * x^(n - 1)", None),
    Formula2("taylor_second_term", "calculus", "c2 * (x - a)^2 / 2", "c2 * (x - a) * (x - a) / 2"),
    Formula2(
        "taylor_second_order",
        "calculus",
        "f0 + d1 * (x - a) + d2 * (x - a)^2 / 2",
        "f0 + d1 * (x - a) + d2 * (x - a) * (x - a) / 2",
    ),
    Formula2("exponential_growth", "calculus", "a * e^(k * t)", None),
    Formula2("gaussian_exponent", "calculus", "(x - m)^2 / (2 * s^2)", "(x - m) * (x - m) / (2 * s * s)"),
    # ---- statistics ------------------------------------------------------------------------------
    Formula2("variance_shortcut", "statistics", "q / n - m^2", "q / n - m * m"),
    Formula2("standard_error_squared", "statistics", "s^2 / n", "s * s / n"),
    Formula2("squared_z_score", "statistics", "(x - m)^2 / s^2", "(x - m) * (x - m) / (s * s)"),
    Formula2("sample_variance", "statistics", "(q - n * m^2) / (n - 1)", "(q - n * m * m) / (n - 1)"),
    Formula2("binomial_term", "statistics", "c * p^k * (1 - p)^(n - k)", None),
    # ---- physics and finance -----------------------------------------------------------------------
    Formula2("kinetic_energy", "physics", "m * v^2 / 2", "m * v * v / 2"),
    Formula2("rest_energy", "physics", "m * c^2", "m * c * c"),
    Formula2("free_fall_distance", "physics", "g * t^2 / 2", "g * t * t / 2"),
    Formula2("gravitation", "physics", "g * m1 * m2 / r^2", "g * m1 * m2 / (r * r)"),
    Formula2("coulomb_force", "physics", "k * q1 * q2 / r^2", "k * q1 * q2 / (r * r)"),
    Formula2(
        "projectile_height",
        "physics",
        "h0 + v * t - g * t^2 / 2",
        "h0 + v * t - g * t * t / 2",
    ),
    Formula2("compound_interest", "finance", "p * (1 + r)^n", None),
    Formula2("compound_interest_periodic", "finance", "p * (1 + r / n)^(n * t)", None),
    Formula2("annuity_future_value", "finance", "p * ((1 + r)^n - 1) / r", None),
)


def formula_tree2(formula: Formula2) -> Node:
    """The intended tree of a Generation 2 formula: its source parsed under the control grammar."""
    return parse2(formula.source, CONTROL_2)


def corpus_audit2(corpus: Sequence[Formula2] | None = None) -> dict[str, Any]:
    """Check the corpus is what it claims: unique names, minimal sources in both generations.

    ``render2(parse2(source, H0), H0) == source`` says the Generation 2 source carries no redundant
    bracket, and the same equality under ``G0`` says it of every Generation 1 counterpart.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS_2
    non_canonical: list[dict[str, Any]] = []
    for formula in corpus:
        rendered = render2(formula_tree2(formula), CONTROL_2)
        if rendered != formula.source:
            non_canonical.append(
                {"formula": formula.name, "generation": 2, "source": formula.source, "rendered": rendered}
            )
        if formula.generation_one_source is not None:
            rendered1 = render1(parse(formula.generation_one_source, CONTROL_1), CONTROL_1)
            if rendered1 != formula.generation_one_source:
                non_canonical.append(
                    {
                        "formula": formula.name,
                        "generation": 1,
                        "source": formula.generation_one_source,
                        "rendered": rendered1,
                    }
                )
    names = [formula.name for formula in corpus]
    areas: dict[str, int] = {}
    for formula in corpus:
        areas[formula.area] = areas.get(formula.area, 0) + 1
    both = tuple(formula.name for formula in corpus if formula.generation_one_source is not None)
    return {
        "size": len(corpus),
        "areas": dict(sorted(areas.items())),
        "area_count": len(areas),
        "duplicate_names": tuple(sorted({name for name in names if names.count(name) > 1})),
        "expressible_in_generation_one": len(both),
        "generation_two_only": tuple(
            formula.name for formula in corpus if formula.generation_one_source is None
        ),
        "canonical_sources": not non_canonical,
        "non_canonical": tuple(non_canonical),
    }


def round_trip_audit2(
    corpus: Sequence[Formula2] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Recount the round trip over the whole (corpus x 121 grammars) grid, independently."""
    corpus = tuple(corpus) if corpus is not None else CORPUS_2
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_2
    failures = []
    checks = 0
    for formula in corpus:
        tree = formula_tree2(formula)
        for grammar in grammars:
            checks += 1
            text = render2(tree, grammar, verify=False)
            if parse2(text, grammar) != tree:
                failures.append({"formula": formula.name, "grammar": grammar.id, "rendering": text})
    return {
        "checks": checks,
        "failures": len(failures),
        "failing": tuple(failures),
        "holds": not failures,
    }


def minimality_audit2(
    corpus: Sequence[Formula2] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Recount minimality by exhaustive deletion over the whole grid: every bracket load-bearing."""
    corpus = tuple(corpus) if corpus is not None else CORPUS_2
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_2
    violations = []
    brackets = 0
    for formula in corpus:
        tree = formula_tree2(formula)
        for grammar in grammars:
            for witness in minimality_witnesses2(tree, grammar):
                brackets += 1
                if not witness["required"]:
                    violations.append({"formula": formula.name, "grammar": grammar.id, **witness})
    return {
        "brackets_checked": brackets,
        "violations": len(violations),
        "violating": tuple(violations),
        "minimal": not violations,
    }


# ------------------------------------------------------------------------------------- semantics


def to_sympy2(node: Node) -> Any:
    """:func:`parseatlas.canonical.to_sympy` with the one case Generation 1 cannot have.

    Reimplemented rather than wrapped because the Generation 1 function recurses into its own
    children and would raise on a ``^`` at any depth. Every other case is identical, symbol
    assumptions included (``real=True``), so a ``^``-free tree converts to exactly the same
    expression Generation 1 builds.
    """
    if isinstance(node, Number):
        if node.value.denominator == 1:
            return Integer(node.value.numerator)
        return Rational(node.value.numerator, node.value.denominator)
    if isinstance(node, Variable):
        return Symbol(node.name, real=True)
    left = to_sympy2(node.left)
    right = to_sympy2(node.right)
    if node.operator == "+":
        return Add(left, right)
    if node.operator == "-":
        return Add(left, -right)
    if node.operator == "*":
        return Mul(left, right)
    if node.operator == "/":
        return Mul(left, right**-1)
    if node.operator == "^":
        return Pow(left, right)
    raise ValueError(f"Unsupported operator: {node.operator}")


def undefined_terms2(node: Node) -> tuple[str, ...]:
    """Excluded points, computed from ``/`` nodes exactly as Generation 1 computes them.

    The rule is deliberately unchanged: a division whose denominator is not a non-zero literal
    contributes the solutions of ``denominator = 0``. A negative exponent written as ``x^(0 - 2)``
    would also exclude a point and is NOT detected, which is a real limit of this module and is
    disclosed in the report; no corpus entry here writes one.
    """
    if isinstance(node, (Number, Variable)):
        return ()
    terms = undefined_terms2(node.left) + undefined_terms2(node.right)
    if node.operator == "/" and (not isinstance(node.right, Number) or node.right.value == 0):
        denominator = to_sympy2(node.right)
        variables = sorted(denominator.free_symbols, key=str)
        if variables:
            terms += tuple(str(point) for point in solve(denominator, variables[0]))
        elif denominator == 0:
            terms += ("all",)
    return tuple(dict.fromkeys(terms))


def canonicalize2(node: Node) -> dict[str, Any]:
    """:func:`parseatlas.canonical.canonicalize` for Generation 2 trees, field for field.

    ``domain`` is the literal ``"R"`` here for the same reason it is there: the project's semantic
    key is ``(canonical form, domain, excluded points)`` and its domain component is a fixed
    declaration rather than a measured field (``NF-2026-00005``). The key is reused exactly as the
    project defines it; only the guarantee is stated at its true strength.
    """
    expression = to_sympy2(node)
    simplified = simplify(expression)
    return {
        "expression": str(simplified),
        "domain": "R",
        "excluded_points": list(undefined_terms2(node)),
        "raw_sympy_expression": expression,
        "sympy_expression": simplified,
    }


def _degree_in(expression: Any, variable: Symbol) -> int | None:
    try:
        degree = Poly(expression, variable).degree()
    except (TypeError, ValueError, PolynomialError):
        return None
    return int(degree) if isinstance(degree, int) else None


def roots_over_c(expression: Any, variable_name: str) -> dict[str, Any]:
    """The complete root multiset over ``C``, or an explicit refusal with its reason.

    The convention is experiment 0035's, unchanged and re-imported rather than restated: solving
    happens on a :func:`~parseatlas.alternative_mathematics.solving_symbol` so the answer is over
    ``C`` and not silently over ``R``, and ``I`` counts as a radical because it is one.

    Generation 2 forces one addition. A reading such as ``(a*x)^(b*x + c + 2)`` is neither a
    polynomial nor a rational function in ``x``, and asking ``solve`` for its roots produces either
    nothing or an answer no textbook page could state. Those readings are reported as
    ``attempted: False`` with the reason, never as a root list of length zero, because an empty
    list would read as "no roots" and that is a different claim.
    """
    symbol = principal_symbol(variable_name)
    if symbol not in expression.free_symbols:
        return {
            "root_domain": ROOT_DOMAIN,
            "attempted": False,
            "reason": "the reading does not contain the variable",
            "degree": None,
            "roots": [],
            "roots_complete": None,
            "requires_radical": None,
        }
    degree = _degree_in(expression, symbol)
    polynomial = degree is not None
    if not polynomial and not expression.is_rational_function(symbol):
        return {
            "root_domain": ROOT_DOMAIN,
            "attempted": False,
            "reason": "the reading is neither a polynomial nor a rational function in the variable",
            "degree": None,
            "roots": [],
            "roots_complete": None,
            "requires_radical": None,
        }
    unconstrained = solving_symbol(variable_name)
    try:
        solved = solve(expression.subs(symbol, unconstrained), unconstrained)
    except (TypeError, ValueError, NotImplementedError, PolynomialError):
        solved = []
    if not isinstance(solved, list):
        solved = []
    ordered = [
        value
        for value in solved
        if not isinstance(value, dict) and unconstrained not in getattr(value, "free_symbols", set())
    ]
    multiplicity: dict[str, int] = {}
    if polynomial:
        try:
            table = roots(Poly(expression, symbol))
        except (TypeError, ValueError, PolynomialError, NotImplementedError):
            table = {}
        multiplicity = {str(root): int(count) for root, count in table.items()}
    with_multiplicity = [
        {"root": str(value), "multiplicity": multiplicity.get(str(value), 1)} for value in ordered
    ]
    return {
        "root_domain": ROOT_DOMAIN,
        "attempted": True,
        "reason": None,
        "degree": degree,
        "roots": [str(value) for value in ordered],
        "roots_with_multiplicity": with_multiplicity,
        "roots_complete": root_list_is_complete(degree, with_multiplicity),
        "requires_radical": requires_radical(ordered),
    }


def _key_cell(payload: tuple[str, Grammar]) -> dict[str, Any]:
    """One (source, grammar) semantic cell. Module level and picklable: the unit the pool maps."""
    source, grammar = payload
    canonical = canonicalize2(parse2(source, grammar))
    return {
        "source": source,
        "grammar_id": grammar.id,
        "key": semantic_key(canonical),
        "canonical": canonical["expression"],
    }


def _generation_one_key_cell(payload: tuple[str, Grammar]) -> dict[str, Any]:
    """One (source, grammar) cell read by the GENERATION 1 pipeline, for the side-by-side halves."""
    source, grammar = payload
    canonical = canonicalize1(parse(source, grammar))
    return {
        "source": source,
        "grammar_id": grammar.id,
        "key": semantic_key(canonical),
        "canonical": canonical["expression"],
    }


# ---------------------------------------------------------------------------------- multicore


#: Cores left free so a sweep cannot starve the interactive MCP session. Policy, not measurement.
WORKER_HEADROOM_CORES: int = 1

#: Seconds to raise a spawn-start pool whose workers each import this module, and so SymPy.
#: MEASURED on this host by :func:`measure_pool_startup`; it is the fixed cost every parallel run
#: pays before any work happens, and it is what the two workloads here are compared against.
POOL_STARTUP_SECONDS: float = 1.2

#: Seconds for one cost cell - one corpus entry rendered under all 121 grammars. MEASURED by
#: :func:`measure_cell_seconds`. Pure string work, four orders of magnitude below pool startup.
COST_CELL_SECONDS: float = 3.0e-03

#: Seconds for one semantic cell - one (source, grammar) pair parsed, canonicalized and simplified.
#: MEASURED by :func:`measure_cell_seconds`. Two orders of magnitude below pool startup, which is
#: why a 121-cell sweep still loses to the sequential path and a 250-cell one would not.
SEMANTIC_CELL_SECONDS: float = 6.3e-03


def worker_count_for(cores: int, cell_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``cell_count`` independent cells."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, max(cell_count, 1)))


def default_worker_count(cell_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, cell_count)


def should_parallelise(cell_count: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising for this much work, from measured costs.

    A cell count on its own cannot answer this. The rule compares the sequential estimate against
    :data:`POOL_STARTUP_SECONDS` plus the divided work, and both inputs are measurements taken on
    this host rather than numbers carried over from another experiment.
    """
    if workers <= 1 or cell_count <= 1:
        return False
    sequential = cell_count * seconds_per_cell
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_cells(
    worker: Any,
    payloads: Sequence[Any],
    workers: int | None = None,
    seconds_per_cell: float = SEMANTIC_CELL_SECONDS,
) -> tuple[Any, ...]:
    """Map ``worker`` over ``payloads``, on a process pool when the measurement says to.

    Every cell is a pure function of its payload and ``map`` preserves order, so the two paths
    return equal structures. ``workers=None`` takes the measured decision; an explicit ``workers``
    overrides it, which is what lets a test force both paths over the same work.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else max(1, int(workers))
    if workers is None and not should_parallelise(len(payloads), seconds_per_cell, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) < 2:
        return tuple(worker(payload) for payload in payloads)
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as pool:
        return tuple(pool.map(worker, payloads, chunksize=1))


def _trivial_cell(payload: int) -> int:
    """A cell that does nothing, so that timing it times only the pool."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising the pool, since :data:`POOL_STARTUP_SECONDS` has to be evidence, not a guess.

    Minimum of ``repeats`` runs: a startup time is a floor that background load can only push up.
    """
    resolved = default_worker_count(64) if workers is None else workers
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as pool:
            list(pool.map(_trivial_cell, range(resolved), chunksize=1))
        best = min(best, time.perf_counter() - start)
    return {
        "workers": resolved,
        "cores": os.cpu_count(),
        "repeats": repeats,
        "seconds": best,
        "declared": POOL_STARTUP_SECONDS,
    }


def measure_cell_seconds(semantic_sample: int | None = None) -> dict[str, Any]:
    """Time one cell of each workload, so the routing constants above are evidence and not a guess."""
    start = time.perf_counter()
    for formula in CORPUS_2:
        _cost_row2((formula, GRAMMARS_2))
    cost_elapsed = time.perf_counter() - start
    payloads = [(QUADRATIC_GENERATION_TWO, grammar) for grammar in GRAMMARS_2]
    if semantic_sample is not None:
        payloads = payloads[:semantic_sample]
    start = time.perf_counter()
    for payload in payloads:
        _key_cell(payload)
    semantic_elapsed = time.perf_counter() - start
    return {
        "cost_cells": len(CORPUS_2),
        "renders": len(CORPUS_2) * len(GRAMMARS_2),
        "cost_seconds": cost_elapsed,
        "cost_seconds_per_cell": cost_elapsed / len(CORPUS_2),
        "semantic_cells_sampled": len(payloads),
        "semantic_seconds": semantic_elapsed,
        "semantic_seconds_per_cell": semantic_elapsed / len(payloads) if payloads else 0.0,
        "declared_cost_seconds_per_cell": COST_CELL_SECONDS,
        "declared_semantic_seconds_per_cell": SEMANTIC_CELL_SECONDS,
    }


# ---------------------------------------------------------------------------------- object groups


def restricted_order(grammar: Grammar, support: Sequence[str]) -> str:
    """The grammar's precedence RESTRICTED to the operators an expression actually contains.

    This is the T6 block label, and it is what a group of worlds should be named by: a list of 20
    grammar identifiers says nothing a reader can check, whereas ``^ > * > +`` says exactly which
    conventions read the string that way and why. Operators sharing a level are joined with ``=``,
    so the control appears as ``* = /`` wherever both are present.
    """
    powers = binding_powers(grammar)
    levels: dict[int, list[str]] = {}
    for operator in support:
        levels.setdefault(powers[operator], []).append(operator)
    index = {operator: position for position, operator in enumerate(OPERATORS_2)}
    return " > ".join(
        " = ".join(sorted(operators, key=lambda item: index[item]))
        for _, operators in sorted(levels.items(), reverse=True)
    )


def reading_expression(source: str, grammar: Grammar, generation: int) -> Any:
    """The simplified SymPy expression one world reads out of one written form.

    Both generations are routed through the same two steps their own pipeline uses, so a group's
    representative is recomputed from ITS source and ITS grammar. Recovering an expression by
    re-parsing the printed canonical text would be a second, undeclared reading of a string, and
    that is exactly the kind of shortcut this project treats as a defect.
    """
    if generation == 2:
        return canonicalize2(parse2(source, grammar))["sympy_expression"]
    return canonicalize1(parse(source, grammar))["sympy_expression"]


def _group_records(
    cells: Sequence[dict[str, Any]],
    grammars: Sequence[Grammar],
    control_id: str,
    variable: str,
    with_roots: bool,
    generation: int,
    support: Sequence[str] = (),
) -> tuple[dict[str, Any], ...]:
    """Collapse (grammar -> semantic key) cells into objects, largest group first.

    Ordering is largest first and then by canonical text, so an object id is stable across runs and
    the reader meets the majority reading before the exotic ones.
    """
    groups: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
    canonical_of: dict[tuple[str, str, tuple[str, ...]], str] = {}
    representative: dict[tuple[str, str, tuple[str, ...]], tuple[str, str]] = {}
    for cell in cells:
        groups.setdefault(cell["key"], []).append(cell["grammar_id"])
        canonical_of[cell["key"]] = cell["canonical"]
        representative.setdefault(cell["key"], (cell["source"], cell["grammar_id"]))
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0][0]))
    records = []
    order = {grammar.id: index for index, grammar in enumerate(grammars)}
    by_id = {grammar.id: grammar for grammar in grammars}
    for index, (key, ids) in enumerate(ordered, start=1):
        source, grammar_id = representative[key]
        ordered_ids = sorted(ids, key=lambda name: order.get(name, 10**6))
        orders: dict[str, None] = {}
        for member in ordered_ids:
            orders.setdefault(restricted_order(by_id[member], support), None)
        record: dict[str, Any] = {
            "object_id": f"O{index:02d}",
            "canonical": canonical_of[key],
            "domain": key[1],
            "excluded_points": list(key[2]),
            "grammars": ordered_ids,
            "count": len(ids),
            "share": 100.0 * len(ids) / len(cells) if cells else 0.0,
            "contains_control": control_id in ids,
            "representative_grammar": grammar_id,
            "restricted_orders": tuple(orders),
            "block_count": len(orders),
        }
        if with_roots:
            symbolic = reading_expression(source, by_id[grammar_id], generation)
            record["factored"] = str(factor(symbolic))
            record.update({f"root_{name}": value for name, value in roots_over_c(symbolic, variable).items()})
        records.append(record)
    return tuple(records)


def object_groups(
    source: str,
    generation: int = 2,
    variable: str = "x",
    with_roots: bool = True,
    workers: int | None = None,
) -> dict[str, Any]:
    """What ``source`` denotes across a whole registry, grouped on the project's semantic key.

    ``generation`` selects the registry AND the parser: ``2`` is the 121 Generation 2 grammars read
    by :func:`parse2`, ``1`` is the 25 Generation 1 grammars read by
    :func:`parseatlas.parser.parse`. A ``^``-free string can be run through either, and the pair of
    answers is exactly what separates a registry-size effect from a language effect.
    """
    if generation == 2:
        grammars = GRAMMARS_2
        control_id = CONTROL_2.id
        worker = _key_cell
        tree = parse2(source, CONTROL_2)
    elif generation == 1:
        grammars = GRAMMARS_1
        control_id = CONTROL_1.id
        worker = _generation_one_key_cell
        tree = parse(source, CONTROL_1)
    else:
        raise ValueError(f"generation must be 1 or 2; got {generation}")
    payloads = [(source, grammar) for grammar in grammars]
    cells = _map_cells(worker, payloads, workers)
    support = tree_operators2(tree)
    records = _group_records(cells, grammars, control_id, variable, with_roots, generation, support)
    control_group = next(record["object_id"] for record in records if record["contains_control"])
    strict_count = len(grammars) - 1
    blocks = min(factorial(len(support)), strict_count)
    return {
        "source": source,
        "generation": generation,
        "variable": variable,
        "registry_size": len(grammars),
        "strict_count": strict_count,
        "support": support,
        "support_size": len(support),
        "blocks": blocks,
        "grammars_per_block": strict_count // blocks,
        "objects": len(records),
        "groups": records,
        "control_object": control_group,
        "control_canonical": _control_canonical(records),
        "control_count": next(record["count"] for record in records if record["contains_control"]),
        "canonical_forms": tuple(record["canonical"] for record in records),
    }


# ------------------------------------------------------------------------------- the headline


#: The flagship object of experiment 0035, in the three writings that separate the two effects.
QUADRATIC_GENERATION_ONE: str = "a * x * x + b * x + c"
QUADRATIC_GENERATION_TWO: str = "a * x^2 + b * x + c"

#: The object experiment 0035 is known for: the radical-free cubic the quadratic string denotes in
#: the worlds where ``+`` binds tighter than ``*``.
FLAGSHIP_CUBIC: str = "a*x*(b + x)*(c + x)"

#: The quadratic itself, as the canonical form the project prints for it.
FLAGSHIP_QUADRATIC: str = "a*x**2 + b*x + c"


def quadratic_worlds(workers: int | None = None) -> dict[str, Any]:
    """THE HEADLINE. What ``a * x^2 + b * x + c`` denotes across the 121 Generation 2 grammars.

    Three readings of the same mathematics are computed side by side, because two different effects
    are in play and reporting either alone would misstate the result:

    ``generation_one``
        the Generation 1 string in the 25 Generation 1 worlds - experiment 0035's own measurement,
        re-derived here rather than quoted;
    ``generation_two_old_writing``
        the SAME string in the 121 Generation 2 worlds. Its support is ``{*, +}`` either way, so
        T6 gives two blocks either way and only the block SIZES change. This isolates the
        registry-size effect, and it is why "13 of 25" and "61 of 121" are one measurement;
    ``generation_two``
        the string a world with ``^`` would actually write. Its support is ``{*, ^, +}``, so T6
        gives six blocks, and the question is what happens to the two objects of 0035.
    """
    generation_one = object_groups(QUADRATIC_GENERATION_ONE, 1, "x", True, workers)
    old_writing = object_groups(QUADRATIC_GENERATION_ONE, 2, "x", True, workers)
    generation_two = object_groups(QUADRATIC_GENERATION_TWO, 2, "x", True, workers)
    forms_two = set(generation_two["canonical_forms"])
    cubic_survives = FLAGSHIP_CUBIC in forms_two
    quadratic_survives = FLAGSHIP_QUADRATIC in forms_two
    same_object_count = generation_one["objects"] == generation_two["objects"]
    if not same_object_count and not cubic_survives:
        verdict = "does not survive"
    elif same_object_count and cubic_survives:
        verdict = "survives"
    else:
        verdict = "changes shape"
    return {
        "generation_one": generation_one,
        "generation_two_old_writing": old_writing,
        "generation_two": generation_two,
        "flagship_cubic": FLAGSHIP_CUBIC,
        "flagship_quadratic": FLAGSHIP_QUADRATIC,
        "cubic_survives": cubic_survives,
        "quadratic_survives": quadratic_survives,
        "quadratic_worlds_generation_one": next(
            record["count"]
            for record in generation_one["groups"]
            if record["canonical"] == FLAGSHIP_QUADRATIC
        ),
        "quadratic_worlds_generation_two": next(
            (
                record["count"]
                for record in generation_two["groups"]
                if record["canonical"] == FLAGSHIP_QUADRATIC
            ),
            0,
        ),
        "objects_generation_one": generation_one["objects"],
        "objects_generation_two": generation_two["objects"],
        "blocks_generation_one": generation_one["blocks"],
        "blocks_generation_two": generation_two["blocks"],
        "registry_effect_only": (
            old_writing["objects"] == generation_one["objects"]
            and set(old_writing["canonical_forms"]) == set(generation_one["canonical_forms"])
        ),
        "verdict": verdict,
        "survives": verdict == "survives",
    }


# ---------------------------------------------------------------------------- the survival table


@dataclass(frozen=True)
class PublishedClaim:
    """One published claim of experiment 0035 or 0036, with the object it is a claim about.

    ``kind`` says how the claim is checked, and each kind is decided by measurement alone:

    ``object_count``
        the written form denotes exactly ``expected`` distinct objects;
    ``object_present``
        some world denotes the object whose canonical form is ``target``;
    ``radical_free_worlds``
        the reading can be solved without adjoining a radical, in ``expected`` worlds. Counted only
        over readings whose roots were actually solved; a reading that is neither a polynomial nor
        a rational function in the variable is reported as unattempted and is never silently
        counted as radical-free;
    ``identity_holds``
        after ``substitution`` the reading equals ``target`` - experiment 0036's route 3.
    """

    claim_id: str
    published_in: str
    name: str
    area: str
    generation_one_source: str
    generation_two_source: str
    variable: str
    kind: str
    claim: str
    expected: int | None = None
    target: str | None = None
    substitution: tuple[tuple[str, str], ...] = ()


#: The claims 0035 and 0036 made about objects a Generation 2 world would write with a power. Each
#: is quoted as published and each is re-measured here in both generations.
PUBLISHED_CLAIMS: tuple[PublishedClaim, ...] = (
    PublishedClaim(
        "0035_quadratic_object_count",
        "0035",
        "quadratic",
        "algebra",
        QUADRATIC_GENERATION_ONE,
        QUADRATIC_GENERATION_TWO,
        "x",
        "object_count",
        "the standard quadratic produces exactly 2 genuinely distinct objects across the worlds",
        expected=2,
    ),
    PublishedClaim(
        "0035_quadratic_radical_free_cubic",
        "0035",
        "quadratic",
        "algebra",
        QUADRATIC_GENERATION_ONE,
        QUADRATIC_GENERATION_TWO,
        "x",
        "object_present",
        "in the other worlds the quadratic is the cubic a*x*(b + x)*(c + x), roots 0, -b, -c",
        target=FLAGSHIP_CUBIC,
    ),
    PublishedClaim(
        "0035_quadratic_radical_free_worlds",
        "0035",
        "quadratic",
        "algebra",
        QUADRATIC_GENERATION_ONE,
        QUADRATIC_GENERATION_TWO,
        "x",
        "radical_free_worlds",
        "solving the standard quadratic needs no radical at all in 12 of the 25 worlds",
        expected=12,
    ),
    PublishedClaim(
        "0035_binomial_square_object_count",
        "0035",
        "binomial_square",
        "algebra",
        "a * a + 2 * a * b + b * b",
        "a^2 + 2 * a * b + b^2",
        "a",
        "object_count",
        "a*a + 2*a*b + b*b produces 2 distinct objects: the binomial square and 2*a**2*b**2*(a + 2)",
        expected=2,
    ),
    PublishedClaim(
        "0035_binomial_square_present",
        "0035",
        "binomial_square",
        "algebra",
        "a * a + 2 * a * b + b * b",
        "a^2 + 2 * a * b + b^2",
        "a",
        "object_present",
        "the binomial square a**2 + 2*a*b + b**2 is denoted in the worlds where the power binds tighter",
        target="a**2 + 2*a*b + b**2",
    ),
    PublishedClaim(
        "0035_difference_of_squares_object_count",
        "0035",
        "difference_of_squares",
        "algebra",
        "a * a - b * b",
        "a^2 - b^2",
        "a",
        "object_count",
        "a*a - b*b produces 2 distinct objects",
        expected=2,
    ),
    PublishedClaim(
        "0035_circle_object_count",
        "0035",
        "circle",
        "geometry",
        "x * x + y * y - r * r",
        "x^2 + y^2 - r^2",
        "x",
        "object_count",
        "x*x + y*y - r*r produces 4 distinct objects",
        expected=4,
    ),
    PublishedClaim(
        "0035_circle_present",
        "0035",
        "circle",
        "geometry",
        "x * x + y * y - r * r",
        "x^2 + y^2 - r^2",
        "x",
        "object_present",
        "the circle -r**2 + x**2 + y**2 is denoted in the worlds where the power binds tighter",
        target="-r**2 + x**2 + y**2",
    ),
    PublishedClaim(
        "0036_pythagorean_identity",
        "0036",
        "pythagorean_identity",
        "trigonometry",
        "s * s + c * c",
        "s^2 + c^2",
        "s",
        "identity_holds",
        "s*s + c*c is still 1 in 13 of the 25 worlds",
        target="1",
        substitution=(("s", "sin"), ("c", "cos")),
    ),
)


def _identity_worlds(
    source: str, generation: int, substitution: tuple[tuple[str, str], ...], target: str, workers: int | None
) -> dict[str, Any]:
    """How many worlds read ``source`` as ``target`` after the substitution - 0036's route 3.

    The placeholders are substituted AFTER the reading, exactly as experiment 0036 does it: the
    convention sensitivity of an identity lives in how the string associates, not in what ``sin``
    means.
    """
    groups = object_groups(source, generation, "x", False, workers)
    registry = GRAMMARS_2 if generation == 2 else GRAMMARS_1
    argument = Symbol("x", real=True)
    functions = {"sin": sin(argument), "cos": cos(argument)}
    holding: list[str] = []
    per_object: list[dict[str, Any]] = []
    for record in groups["groups"]:
        grammar = next(item for item in registry if item.id == record["representative_grammar"])
        substituted = reading_expression(source, grammar, generation)
        for placeholder, function in substitution:
            substituted = substituted.subs(Symbol(placeholder, real=True), functions[function])
        value = simplify(substituted)
        holds = str(value) == target
        per_object.append({"object_id": record["object_id"], "value": str(value), "holds": holds})
        if holds:
            holding.extend(record["grammars"])
    return {
        "groups": groups,
        "per_object": tuple(per_object),
        "worlds": len(holding),
        "holding": tuple(holding),
        "share": 100.0 * len(holding) / groups["registry_size"],
    }


def _control_canonical(records: Sequence[dict[str, Any]]) -> str:
    """The canonical form the CONTROL world of that registry reads out of the written form.

    Found by the control flag and never by position. The control is usually in the largest group,
    which is exactly why taking ``records[0]`` would pass almost everywhere and be wrong: on
    ``m * v^2 / 2`` the control's object holds 41 worlds while another holds 60.
    """
    return next(record["canonical"] for record in records if record["contains_control"])


def _radical_free_worlds(groups: dict[str, Any]) -> int:
    """Worlds whose reading was solved AND needed no radical to state its roots."""
    return sum(
        record["count"]
        for record in groups["groups"]
        if record["root_attempted"] and record["root_requires_radical"] is False
    )


def _unattempted_worlds(groups: dict[str, Any]) -> int:
    """Worlds whose reading has no root list here, and is therefore counted as neither."""
    return sum(record["count"] for record in groups["groups"] if not record["root_attempted"])


def _claim_row(claim: PublishedClaim, workers: int | None = None) -> dict[str, Any]:
    if claim.kind == "identity_holds":
        assert claim.target is not None
        one = _identity_worlds(claim.generation_one_source, 1, claim.substitution, claim.target, workers)
        two = _identity_worlds(claim.generation_two_source, 2, claim.substitution, claim.target, workers)
        measured_one: Any = one["worlds"]
        measured_two: Any = two["worlds"]
        groups_one, groups_two = one["groups"], two["groups"]
        holds_one = measured_one > 0
        holds_two = measured_two > 0
        detail: dict[str, Any] = {
            "generation_one_share": one["share"],
            "generation_two_share": two["share"],
            "generation_one_per_object": one["per_object"],
            "generation_two_per_object": two["per_object"],
        }
    else:
        with_roots = claim.kind == "radical_free_worlds"
        groups_one = object_groups(claim.generation_one_source, 1, claim.variable, with_roots, workers)
        groups_two = object_groups(claim.generation_two_source, 2, claim.variable, with_roots, workers)
        if claim.kind == "radical_free_worlds":
            measured_one = _radical_free_worlds(groups_one)
            measured_two = _radical_free_worlds(groups_two)
            holds_one = measured_one == claim.expected
            holds_two = measured_two > 0
        elif claim.kind == "object_count":
            measured_one = groups_one["objects"]
            measured_two = groups_two["objects"]
            holds_one = measured_one == claim.expected
            holds_two = measured_two == claim.expected
        elif claim.kind == "object_present":
            assert claim.target is not None
            measured_one = sum(
                record["count"] for record in groups_one["groups"] if record["canonical"] == claim.target
            )
            measured_two = sum(
                record["count"] for record in groups_two["groups"] if record["canonical"] == claim.target
            )
            holds_one = measured_one > 0
            holds_two = measured_two > 0
        else:
            raise ValueError(f"unknown claim kind: {claim.kind!r}")
        counts_worlds = claim.kind in ("object_present", "radical_free_worlds")
        detail = {
            "generation_one_share": 100.0 * measured_one / groups_one["registry_size"]
            if counts_worlds
            else None,
            "generation_two_share": 100.0 * measured_two / groups_two["registry_size"]
            if counts_worlds
            else None,
        }
        if claim.kind == "radical_free_worlds":
            detail["generation_one_unattempted_worlds"] = _unattempted_worlds(groups_one)
            detail["generation_two_unattempted_worlds"] = _unattempted_worlds(groups_two)
    if not holds_two:
        verdict = "does not survive"
    elif holds_one and measured_one == measured_two:
        verdict = "survives"
    else:
        verdict = "survives with different numbers"
    return {
        "claim_id": claim.claim_id,
        "published_in": claim.published_in,
        "name": claim.name,
        "area": claim.area,
        "kind": claim.kind,
        "claim": claim.claim,
        "generation_one_source": claim.generation_one_source,
        "generation_two_source": claim.generation_two_source,
        "generation_one_objects": groups_one["objects"],
        "generation_two_objects": groups_two["objects"],
        "generation_one_blocks": groups_one["blocks"],
        "generation_two_blocks": groups_two["blocks"],
        "generation_one_group_sizes": tuple(record["count"] for record in groups_one["groups"]),
        "generation_two_group_sizes": tuple(record["count"] for record in groups_two["groups"]),
        "generation_one_canonical_forms": groups_one["canonical_forms"],
        "generation_two_canonical_forms": groups_two["canonical_forms"],
        "generation_one_control_object": groups_one["control_object"],
        "generation_two_control_object": groups_two["control_object"],
        "generation_one_control_canonical": groups_one["control_canonical"],
        "generation_two_control_canonical": groups_two["control_canonical"],
        "control_object_unchanged": groups_one["control_canonical"] == groups_two["control_canonical"],
        # An object COUNT can survive while the objects themselves are replaced wholesale - the
        # circle does exactly that - so the set equality is measured separately and never inferred
        # from the count.
        "same_object_set": set(groups_one["canonical_forms"]) == set(groups_two["canonical_forms"]),
        "shared_objects": tuple(
            sorted(set(groups_one["canonical_forms"]) & set(groups_two["canonical_forms"]))
        ),
        "measured_generation_one": measured_one,
        "measured_generation_two": measured_two,
        "holds_generation_one": holds_one,
        "holds_generation_two": holds_two,
        "verdict": verdict,
        "survives": verdict != "does not survive",
        **detail,
    }


def survival_table(
    claims: Sequence[PublishedClaim] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Every published claim of 0035 and 0036 that a power rewrites, re-measured in both generations.

    Each row carries the distinct-object count in Generation 1 against Generation 2, the T6 block
    structure of both, and a verdict decided by the rule stated on :class:`PublishedClaim`: a claim
    that is false in Generation 2 does not survive; one that is true but with different world counts
    survives with different numbers; one that is true with the same counts survives outright.
    """
    claims = tuple(claims) if claims is not None else PUBLISHED_CLAIMS
    rows = tuple(_claim_row(claim, workers) for claim in claims)
    failed = tuple(row["claim_id"] for row in rows if not row["survives"])
    renumbered = tuple(row["claim_id"] for row in rows if row["verdict"] == "survives with different numbers")
    intact = tuple(row["claim_id"] for row in rows if row["verdict"] == "survives")
    return {
        "rows": rows,
        "claims": len(rows),
        "does_not_survive": failed,
        "survives_with_different_numbers": renumbered,
        "survives": intact,
        # The aggregate that decides how the report opens: in every row, is the ONLY object the two
        # generations share the one the conventional world reads? If so, no alternative object of
        # 0035 or 0036 is denoted by any Generation 2 world.
        "shared_object_counts": tuple(len(row["shared_objects"]) for row in rows),
        "only_the_control_object_is_shared": all(
            row["shared_objects"] == (row["generation_two_control_canonical"],)
            for row in rows
        ),
        "control_objects_unchanged": all(row["control_object_unchanged"] for row in rows),
        "objects_grew": tuple(
            row["name"] for row in rows if row["generation_two_objects"] > row["generation_one_objects"]
        ),
        "objects_unchanged": tuple(
            row["name"] for row in rows if row["generation_two_objects"] == row["generation_one_objects"]
        ),
    }


# --------------------------------------------------------------------------------- cost ranking


def _ranked(totals: dict[str, int]) -> tuple[dict[str, Any], ...]:
    """Competition ranking (``1, 2, 2, 4``) over per-grammar totals, cheapest first."""
    order = sorted(totals.items(), key=lambda item: (item[1], item[0]))
    ranking = []
    previous_total: int | None = None
    previous_rank = 0
    for position, (grammar_id, total) in enumerate(order, start=1):
        rank = previous_rank if total == previous_total else position
        ranking.append({"rank": rank, "id": grammar_id, "total": total})
        previous_total, previous_rank = total, rank
    return tuple(ranking)


def rank_percentile(rank: int, registry_size: int) -> float:
    """``100 * rank / registry_size``: the percentage of the registry the rank sits inside.

    Stated as a formula because the whole point of the figure is that ordinals are not comparable
    across registries of different sizes. ``3rd of 25`` is ``12.0``; a rank of ``15`` among ``121``
    is ``12.4``, and only the percentile says those are the same standing.
    """
    return 100.0 * rank / registry_size


def _cost_row2(payload: tuple[Formula2, tuple[Grammar, ...]]) -> dict[str, Any]:
    """One corpus entry priced under every Generation 2 grammar. Picklable by design."""
    formula, grammars = payload
    tree = formula_tree2(formula)
    renderings = {grammar.id: render2(tree, grammar) for grammar in grammars}
    costs = {grammar_id: text.count("(") for grammar_id, text in renderings.items()}
    support = tree_operators2(tree)
    return {
        "name": formula.name,
        "area": formula.area,
        "source": formula.source,
        "generation_one_source": formula.generation_one_source,
        "support": support,
        "support_size": len(support),
        "renderings": renderings,
        "costs": costs,
    }


def cost_rows2(
    corpus: Sequence[Formula2] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> tuple[dict[str, Any], ...]:
    """One record per corpus entry: its rendering and bracket cost under every grammar."""
    corpus = tuple(corpus) if corpus is not None else CORPUS_2
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_2
    payloads = [(formula, grammars) for formula in corpus]
    return _map_cells(_cost_row2, payloads, workers, COST_CELL_SECONDS)


def distinguishing_power(
    corpus: Sequence[Formula2] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """How much of the 120 can each corpus entry actually see? The null model, per entry.

    T6 says a parse depends only on the precedence restricted to the operators present, so an entry
    with support size ``k`` sees ``k!`` blocks of ``120 / k!`` strict orderings and is blind inside
    a block by construction. ``blocks`` is that upper bound; ``distinct_renderings`` is what the
    entry actually achieves, which can be smaller when two orders happen to write it the same way.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS_2
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_2
    rows = cost_rows2(corpus, grammars, workers)
    strict = tuple(grammar.id for grammar in grammars if grammar.id != CONTROL_2.id)
    entries = []
    for row in rows:
        blocks = min(factorial(row["support_size"]), len(strict))
        strict_renderings = {row["renderings"][grammar_id] for grammar_id in strict}
        strict_costs = {row["costs"][grammar_id] for grammar_id in strict}
        entries.append(
            {
                "name": row["name"],
                "area": row["area"],
                "source": row["source"],
                "support": row["support"],
                "support_size": row["support_size"],
                "blocks": blocks,
                "grammars_per_block": len(strict) // blocks,
                "distinct_renderings": len(strict_renderings),
                "distinct_costs": len(strict_costs),
                "separates_all": blocks == len(strict),
                "movable": len(strict_costs) > 1,
                "control_cost": row["costs"][CONTROL_2.id],
                "min_cost": min(row["costs"].values()),
                "max_cost": max(row["costs"].values()),
                "range": max(row["costs"].values()) - min(row["costs"].values()),
            }
        )
    separating = tuple(entry["name"] for entry in entries if entry["separates_all"])
    movable = tuple(entry["name"] for entry in entries if entry["movable"])
    by_support: dict[int, int] = {}
    for entry in entries:
        by_support[entry["support_size"]] = by_support.get(entry["support_size"], 0) + 1
    return {
        "entries": tuple(entries),
        "corpus_size": len(entries),
        "strict_count": len(strict),
        "separating_all": separating,
        "separating_all_count": len(separating),
        "not_separating_all": tuple(entry["name"] for entry in entries if not entry["separates_all"]),
        "not_separating_all_count": len(entries) - len(separating),
        "movable": movable,
        "movable_count": len(movable),
        "constant": tuple(entry["name"] for entry in entries if not entry["movable"]),
        "constant_count": len(entries) - len(movable),
        "support_histogram": dict(sorted(by_support.items())),
        "max_blocks": max((entry["blocks"] for entry in entries), default=0),
    }


def _ranking_block(
    rows: Sequence[dict[str, Any]], grammars: Sequence[Grammar], control: Grammar
) -> dict[str, Any]:
    totals = {grammar.id: sum(row["costs"][grammar.id] for row in rows) for grammar in grammars}
    ranking = _ranked(totals)
    ranks = {entry["id"]: entry["rank"] for entry in ranking}
    strict_totals = {key: value for key, value in totals.items() if key != control.id}
    cheaper = sum(1 for value in totals.values() if value < totals[control.id])
    # Where the control would stand if it were inserted into a ranking of the STRICT orderings
    # alone: one plus the number of strict grammars strictly cheaper than it. Reported because
    # "of 120" and "of 121" are two different populations and the card asks for the former.
    strict_cheaper = sum(1 for value in strict_totals.values() if value < totals[control.id])
    ties = sum(1 for key, value in totals.items() if value == totals[control.id] and key != control.id)
    # How much of the registry this corpus can actually resolve. Two grammars with the same total
    # are indistinguishable BY COST here whatever their precedence, and two with the same rendering
    # profile are indistinguishable outright - the second is the corpus-level form of T6.
    profiles = {
        grammar.id: tuple(row["costs"][grammar.id] for row in rows) for grammar in grammars
    }
    renderings = {
        grammar.id: tuple(row.get("renderings", {}).get(grammar.id, "") for row in rows)
        for grammar in grammars
    }
    return {
        "entries": len(rows),
        "registry_size": len(grammars),
        "totals": totals,
        "ranking": ranking,
        "control_id": control.id,
        "control_total": totals[control.id],
        "control_rank": ranks[control.id],
        "control_percentile": rank_percentile(ranks[control.id], len(grammars)),
        "control_rank_among_strict": strict_cheaper + 1,
        "control_percentile_among_strict": rank_percentile(strict_cheaper + 1, len(strict_totals)),
        "strictly_cheaper_count": cheaper,
        "tied_with_control": ties,
        "distinct_totals": len(set(totals.values())),
        "distinct_cost_profiles": len(set(profiles.values())),
        "distinct_rendering_profiles": len(set(renderings.values())),
        "best": ranking[0],
        "worst": ranking[-1],
        "spread": ranking[-1]["total"] - ranking[0]["total"],
        "best_alternative": next(entry for entry in ranking if entry["id"] != control.id),
    }


def power_position_table(
    rows: Sequence[dict[str, Any]], grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Cost by where ``^`` sits in the ordering: T25's question, asked directly.

    T25 asks whether the conventional grammar keeps its standing "when ``^`` binds tighter than
    ``*`` versus looser". The 120 strict orderings answer it as a whole rather than a pair: each of
    the five positions ``^`` can occupy holds exactly 24 of them, so the five means are directly
    comparable and no grammar is counted twice.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_2
    totals = {grammar.id: sum(row["costs"][grammar.id] for row in rows) for grammar in grammars}
    by_position: dict[int, list[int]] = {}
    for grammar in grammars:
        if grammar.id == CONTROL_2.id:
            continue
        by_position.setdefault(grammar.precedence.index("^") + 1, []).append(totals[grammar.id])
    positions = {
        position: {
            "grammars": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
        for position, values in sorted(by_position.items())
    }
    means = [positions[position]["mean"] for position in sorted(positions)]
    steps = [round(second - first, 6) for first, second in zip(means, means[1:])]
    return {
        "positions": positions,
        "means": means,
        "steps": steps,
        "monotone": all(step > 0 for step in steps),
        "constant_step": len(set(steps)) == 1,
        "tightest_mean": means[0],
        "loosest_mean": means[-1],
        "gap": means[-1] - means[0],
        "control_total": totals[CONTROL_2.id],
    }


def _generation_one_rows(corpus: Sequence[Formula2]) -> tuple[dict[str, Any], ...]:
    rows = []
    for formula in corpus:
        if formula.generation_one_source is None:
            continue
        tree = parse(formula.generation_one_source, CONTROL_1)
        renderings = {grammar.id: render1(tree, grammar) for grammar in GRAMMARS_1}
        costs = {grammar.id: parenthesis_cost1(tree, grammar) for grammar in GRAMMARS_1}
        rows.append(
            {
                "name": formula.name,
                "area": formula.area,
                "source": formula.generation_one_source,
                "renderings": renderings,
                "costs": costs,
            }
        )
    return tuple(rows)


def control_ranking(
    corpus: Sequence[Formula2] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Where the conventional Generation 2 grammar sits on notational cost, and against what.

    Four rankings, because an ordinal is only meaningful against a stated population:

    ``full``
        the whole Generation 2 corpus over all 121 grammars;
    ``movable``
        the same over the entries whose cost is not constant across the registry - the entries that
        can actually move a ranking. An entry with a cost of ``0`` everywhere adds the same constant
        to every total and only makes the corpus look expensive;
    ``shared_generation_two`` / ``shared_generation_one``
        the sub-corpus expressible in BOTH languages, priced in each. Same mathematics, one written
        with powers and one with product chains, so the two control ranks are a comparison of
        conventions rather than of corpora - subject to the ordinal caveat, which is why the
        percentile is carried next to every rank.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS_2
    grammars = tuple(grammars) if grammars is not None else GRAMMARS_2
    rows = cost_rows2(corpus, grammars, workers)
    power = distinguishing_power(corpus, grammars, workers)
    movable_names = set(power["movable"])
    movable_rows = tuple(row for row in rows if row["name"] in movable_names)
    shared_names = {formula.name for formula in corpus if formula.generation_one_source is not None}
    shared_rows = tuple(row for row in rows if row["name"] in shared_names)
    full = _ranking_block(rows, grammars, CONTROL_2)
    movable = _ranking_block(movable_rows, grammars, CONTROL_2)
    shared_two = _ranking_block(shared_rows, grammars, CONTROL_2)
    shared_one = _ranking_block(_generation_one_rows(corpus), GRAMMARS_1, CONTROL_1)
    return {
        "corpus_size": len(rows),
        "registry_size": len(grammars),
        "full": full,
        "movable": movable,
        "movable_entries": tuple(row["name"] for row in movable_rows),
        "constant_entries": power["constant"],
        "shared_generation_two": shared_two,
        "shared_generation_one": shared_one,
        "shared_corpus_size": len(shared_rows),
        "power_position": power_position_table(rows, grammars),
        "power_position_shared": power_position_table(shared_rows, grammars),
        "shared_control_saving": shared_one["control_total"] - shared_two["control_total"],
        "shared_control_saving_percent": (
            100.0
            * (shared_one["control_total"] - shared_two["control_total"])
            / shared_one["control_total"]
            if shared_one["control_total"]
            else 0.0
        ),
        "distinguishing": power,
        "control_rank_stable": full["control_rank"] == movable["control_rank"],
        "ranking_identical": tuple(entry["id"] for entry in full["ranking"])
        == tuple(entry["id"] for entry in movable["ranking"]),
    }


# ------------------------------------------------------------------------------- the measurement


def parallel_decision(repeats: int = 3, workers: int | None = None) -> dict[str, Any]:
    """Time the two workloads of this experiment sequentially and on a pool, and record the winner.

    Repository policy is multicore by default and allows a sequential path when a measurement
    justifies it. The two workloads here are not alike, which is the whole reason to measure rather
    than assume: the cost grid is pure string rendering, and the semantic grid is one SymPy
    ``simplify`` per cell. The numbers this function returns are the evidence, not the expectation.
    """
    cost_cells = len(CORPUS_2)
    semantic_cells = len(GRAMMARS_2)
    cost_workers = workers if workers is not None else default_worker_count(cost_cells)
    semantic_workers = workers if workers is not None else default_worker_count(semantic_cells)

    def _time(function: Any, count: int) -> float:
        best = float("inf")
        for _ in range(max(1, repeats)):
            start = time.perf_counter()
            function(count)
            best = min(best, time.perf_counter() - start)
        return best

    def _cost(count: int) -> Any:
        return cost_rows2(CORPUS_2, GRAMMARS_2, workers=count)

    def _semantic(count: int) -> Any:
        payloads = [(QUADRATIC_GENERATION_TWO, grammar) for grammar in GRAMMARS_2]
        return _map_cells(_key_cell, payloads, count, SEMANTIC_CELL_SECONDS)

    cost_sequential = _time(_cost, 1)
    cost_parallel = _time(_cost, cost_workers)
    semantic_sequential = _time(_semantic, 1)
    semantic_parallel = _time(_semantic, semantic_workers)
    return {
        "cores": os.cpu_count(),
        "repeats": repeats,
        "cost": {
            "cells": cost_cells,
            "renders": cost_cells * len(GRAMMARS_2),
            "workers": cost_workers,
            "sequential_seconds": cost_sequential,
            "parallel_seconds": cost_parallel,
            "speedup": cost_sequential / cost_parallel if cost_parallel else None,
            "faster": "parallel" if cost_parallel < cost_sequential else "sequential",
            "records_identical": _cost(1) == _cost(cost_workers),
            "default_decision": "parallel"
            if should_parallelise(cost_cells, COST_CELL_SECONDS, cost_workers)
            else "sequential",
        },
        "semantic": {
            "cells": semantic_cells,
            "workers": semantic_workers,
            "sequential_seconds": semantic_sequential,
            "parallel_seconds": semantic_parallel,
            "speedup": semantic_sequential / semantic_parallel if semantic_parallel else None,
            "faster": "parallel" if semantic_parallel < semantic_sequential else "sequential",
            "records_identical": _semantic(1) == _semantic(semantic_workers),
            "default_decision": "parallel"
            if should_parallelise(semantic_cells, SEMANTIC_CELL_SECONDS, semantic_workers)
            else "sequential",
            "cells_to_cross_over": _cells_to_cross_over(SEMANTIC_CELL_SECONDS, semantic_workers),
        },
    }


def _cells_to_cross_over(seconds_per_cell: float, workers: int) -> int | None:
    """The smallest cell count at which a pool would start to pay for itself, from the constants.

    Reported because "sequential won" is only useful next to how far away the crossover is: this
    experiment's semantic grid loses to the pool by a factor, not by a hair, and the number says at
    what size the same code would switch.
    """
    if workers <= 1 or seconds_per_cell <= 0:
        return None
    saving_per_cell = seconds_per_cell * (1 - 1 / workers)
    return int(POOL_STARTUP_SECONDS / saving_per_cell) + 1


def generation_two_report(workers: int | None = None, timing: bool = False) -> dict[str, Any]:
    """The whole experiment as one structure, in the order the report states it."""
    report = {
        "registry_size": len(GRAMMARS_2),
        "strict_count": len(GRAMMARS_2) - 1,
        "control": CONTROL_2.id,
        "agreement": agreement_audit(),
        "corpus": corpus_audit2(),
        "round_trip": round_trip_audit2(),
        "minimality": minimality_audit2(),
        "quadratic": quadratic_worlds(workers),
        "survival": survival_table(None, workers),
        "ranking": control_ranking(None, None, workers),
    }
    if timing:
        report["parallel_decision"] = parallel_decision()
    return report
