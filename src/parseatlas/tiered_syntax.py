"""Where the flat precedence model ends - unary minus, juxtaposition, and thesis T26.

Experiment 0050, and the first executable test of ROADMAP thesis **T26**.

The thesis, and what it actually claims
---------------------------------------

T26 says:

    In real mathematical practice, implicit multiplication (juxtaposition, e.g. ``2x``, ``1/2x``)
    binds tighter than explicit ``*`` or ``/``, while unary minus (``-x^2``) conflicts with binary
    ``-``. These interactions cannot be captured by a single flat binary operator precedence and
    require tiered syntax layers.

It carries the evidence level *JUSTIFIED* and has never been run. It is a claim about the reach of
this project's own model, which makes it exactly the kind of claim that has to be measured rather
than argued, and the measurement is the whole of this module.

The claim splits into two readings and they do not have the same answer:

.. code-block:: text

    reading 1   "a flat BINARY precedence"  - the project's Generation 1/2 model literally, four or
                five infix operators and nothing else.  Under it `2x` and `-x` are not strings of
                the language at all, so the thesis is true and empty: it says a language without
                juxtaposition cannot juxtapose.

    reading 2   "a flat precedence over the same operator set" - one binding power per role, where
                juxtaposition is a role and prefix minus is a role.  This is the reading with
                content, because it asks whether the tiers buy anything that two more rows in the
                precedence table do not.

:func:`flat_equivalence` answers reading 2 by exhaustive search over every flat model, and
:func:`null_model` then asks the only question that decides whether the answer matters: how many
distinct mathematical OBJECTS does the tiered space reach that the flat space does not.

The shared parser is not touched
--------------------------------

:mod:`parseatlas.parser`, :mod:`parseatlas.grammar` and :mod:`parseatlas.generation_two` are left
exactly as they are. This module carries its own tokenizer, its own layered parser and its own flat
parser, which raises the obligation it discharges before anything else: **restricted to Generation
1, does the layered parser parse exactly what Generation 1 parses?** :func:`agreement_audit` is
first in the module, first in the tests and first in both reports, because if it fails no other
number here means anything.

The node types are Generation 1's own :class:`parseatlas.parser.Binary`,
:class:`~parseatlas.parser.Number` and :class:`~parseatlas.parser.Variable`, plus exactly one new
node, :class:`Negate`, which a Generation 1 tree can never contain. So the audit's comparison is
dataclass equality and not a translation between two tree formats.

What a convention IS here
-------------------------

A precedence permutation is an ordering of operators. A tier assignment is not that, and saying so
is half the experiment. In this module:

* the **base** is one of the 121 Generation 2 grammars - a stack of levels over ``^ * / + -``;
* a **placement** puts a new syntactic layer either in a *gap* between two levels (or above all, or
  below all) or *tied* to an existing level; a base with ``L`` levels has ``2L + 1`` placements;
* **juxtaposition** takes a placement. The "alias for ``*``" reading is not a separate axis - it is
  exactly the tie placement at the level that holds ``*``, which :func:`alias_equals_tie` measures
  rather than asserts;
* **unary minus** takes a placement;
* either placement may be **split** into a general placement and a different one used inside the
  right operand of ``^``. A split is the only thing in the space that is not a stack of layers, and
  it is deliberately there so the flat test is not decided by the enumeration;
* **exponent_prefix** admits a prefix minus at the head of ``^``'s right operand whatever the minus
  placement says. This is Python's ``factor: '-' factor | power`` rule and it is what lets ``-x^2``
  read ``-(x^2)`` while ``x^-2`` still parses.

That gives ``(2L+1) + (2L+1)(2L)`` slots for each of juxtaposition and minus, times ``2``. Over the
conventional base ``H0`` (``L = 3``) that is ``49 * 49 * 2 = 4802`` conventions; over the whole
Generation 2 registry the same definition gives ``3 518 642``. :data:`CONVENTIONS` is the swept
union and :data:`CONVENTION_SPACE_SIZE` is the whole space; the difference is a computational limit
and is named as one at the point the answer is read, not in a limits section.

The tokenizer decides more than the grammar does
------------------------------------------------

Juxtaposition only exists where the tokenizer can see it. Generation 1's name pattern is maximal
munch, so ``xy`` is ONE variable and ``ax^2 + bx + c`` is a polynomial in the variables ``ax`` and
``bx``. Every juxtaposition in the corpus is therefore written with a space or a bracket, and
:func:`juxtaposition_sites` is what the reports quote rather than an assurance.

Generation 1's number pattern is ``\\d+(?:/\\d+)?``, so an unspaced ``1/2`` is one rational literal.
Kept unchanged, that rule *destroys the very ambiguity this card is about*: ``1/2x`` would be
``Number(1/2)`` juxtaposed with ``x`` under every convention, and the published disagreement over
``1/2x`` would be resolved by the lexer before any precedence rule ran. :data:`LITERAL_POLICIES`
makes the rule an explicit axis with three values, the default splits a composite literal only when
a juxtaposable primary follows it immediately, and :func:`agreement_audit` proves the default is
still conservative over Generation 1 - because no Generation 1 string can have a literal followed
by a name, that being juxtaposition, which Generation 1 cannot write.

The null model
--------------

Experiment 0030 widened the convention axis with associativity, recovered under 12 percent of the
gap, and added 50 percent more syntax for zero new mathematics (T30). :func:`null_model` asks the
same question of the tiered axis and it is the function that decides whether this card found
anything. It is also where the registry warning bites: a corpus entry using ``j`` of the ``k``
roles distinguishes only the orderings restricted to those ``j``, so every count here is reported
next to its role support.
"""

import os
import re
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Any

from sympy import Add, Integer, Mul, Pow, Rational, Symbol, simplify, solve

from .alternative_mathematics import semantic_key
from .generation_two import GRAMMARS_2, control_grammar_2, generation_one_sources
from .grammar import Grammar, all_grammars
from .parser import Binary, Number, Variable, parse

# ------------------------------------------------------------------------------- the language

#: The five binary operators, inherited from Generation 2 unchanged.
BINARY_OPERATORS: tuple[str, ...] = ("^", "*", "/", "+", "-")

#: The two roles Generation 2 does not have. ``JUX`` is an infix operator with no written symbol;
#: ``NEG`` is a prefix operator that shares its symbol with binary ``-``.
JUX: str = "JUX"
NEG: str = "NEG"

#: Every role a precedence model in this module has to place. Seven, not five, and the whole
#: content of T26's second reading is whether seven rows in one flat table suffice.
ROLES: tuple[str, ...] = BINARY_OPERATORS + (JUX, NEG)

#: Associativity of the infix roles. ``^`` is right-associative exactly as in Generation 2;
#: juxtaposition is left-associative, as ``2 x y`` is ``(2x)y``.
ASSOCIATIVITY_3: dict[str, str] = {
    "^": "right",
    "*": "left",
    "/": "left",
    "+": "left",
    "-": "left",
    JUX: "left",
}

#: How a composite rational literal is tokenized. The axis exists because the choice decides the
#: answer to one of the two named real-world ambiguities before any grammar sees the string.
#:
#: ``gen1``   Generation 1's rule verbatim: ``1/2`` is always one literal, so ``1/2x`` is always
#:            ``(1/2)x`` and the published disagreement is invisible.
#: ``split``  a composite literal is split back into ``int / int`` when a juxtaposable primary
#:            follows it with no space, so ``1/2x`` is ambiguous and ``1/2 x`` is not. DEFAULT.
#: ``none``   there is no composite literal at all. NOT conservative over Generation 1, and it is
#:            the divergence :func:`agreement_audit` is tested against.
LITERAL_POLICIES: tuple[str, ...] = ("gen1", "split", "none")

#: The default policy. See :data:`LITERAL_POLICIES` for why it is not ``gen1``.
LITERAL_POLICY: str = "split"

_TOKEN_3 = re.compile(
    r"\s*(?:(?P<number>\d+(?:/\d+)?)|(?P<name>[A-Za-z_]\w*)"
    r"|(?P<operator>[\^+\-*/])|(?P<left>\()|(?P<right>\)))"
)

_WORD = re.compile(r"\w")
_TRAILING_RATIONAL = re.compile(r"\d+/\d+$")


@dataclass(frozen=True)
class Token3:
    kind: str
    value: str


@dataclass(frozen=True)
class Negate:
    """Prefix minus. The only node type this module adds to Generation 1's three.

    A Generation 1 tree can never contain one, which is what keeps :func:`agreement_audit`'s
    comparison honest: a spurious ``Negate`` anywhere in a Generation 1 cell is a disagreement.
    """

    operand: Any


@lru_cache(maxsize=4096)
def tokenize_tiered(source: str, literal_policy: str = LITERAL_POLICY) -> tuple[Token3, ...]:
    """Generation 2's tokenizer with the composite-literal rule made an explicit axis.

    Cached because a sweep tokenizes the same few dozen sources under a hundred thousand models,
    and tokenization is a third of a parse. The result is a tuple of frozen dataclasses and no
    caller can mutate it.

    Nothing else changes: the name pattern is Generation 1's maximal-munch ``[A-Za-z_]\\w*``, so
    ``xy`` is one variable and juxtaposition between two names must be written with a space.
    Juxtaposition itself produces no token - it is adjacency, and the parser reads it off the
    stream.
    """
    if literal_policy not in LITERAL_POLICIES:
        raise ValueError(f"literal_policy must be one of {LITERAL_POLICIES}; got {literal_policy!r}")
    tokens: list[Token3] = []
    position = 0
    while position < len(source):
        match = _TOKEN_3.match(source, position)
        if not match:
            raise ValueError(f"Unexpected character at position {position}: {source[position]!r}")
        kind = match.lastgroup
        assert kind is not None
        value = match.group(kind)
        end = match.end()
        if kind == "number" and "/" in value and _splits_literal(source, end, literal_policy):
            numerator, denominator = value.split("/", 1)
            tokens.append(Token3("number", numerator))
            tokens.append(Token3("operator", "/"))
            tokens.append(Token3("number", denominator))
            position = end
            continue
        tokens.append(Token3(kind, value))
        position = end
    tokens.append(Token3("eof", ""))
    return tuple(tokens)


def _splits_literal(source: str, end: int, literal_policy: str) -> bool:
    if literal_policy == "gen1":
        return False
    if literal_policy == "none":
        return True
    following = source[end] if end < len(source) else ""
    return bool(following) and (following.isalpha() or following == "_" or following == "(")


def starts_primary(token: Token3) -> bool:
    """Can this token open an operand? That, and only that, is what makes a juxtaposition site."""
    return token.kind in ("number", "name", "left")


def juxtaposition_sites(source: str, literal_policy: str = LITERAL_POLICY) -> int:
    """How many juxtaposition sites the tokenizer sees in ``source``.

    A site is a token that can open an operand standing immediately after a token that can close
    one. This is what the reports quote when they say a Generation 1 corpus contains no
    juxtaposition: it is counted, not assumed.
    """
    tokens = tokenize_tiered(source, literal_policy)
    sites = 0
    for previous, token in zip(tokens, tokens[1:]):
        if previous.kind in ("number", "name", "right") and starts_primary(token):
            sites += 1
    return sites


def prefix_minus_sites(source: str, literal_policy: str = LITERAL_POLICY) -> int:
    """How many ``-`` tokens stand in prefix position - at the start, or after an operator or ``(``."""
    tokens = tokenize_tiered(source, literal_policy)
    sites = 0
    previous: Token3 | None = None
    for token in tokens:
        if token.kind == "operator" and token.value == "-":
            if previous is None or previous.kind in ("operator", "left"):
                sites += 1
        previous = token
    return sites


# ------------------------------------------------------------------------------- the conventions

#: A placement is ``("gap", k)`` - a new layer strictly between level ``k-1`` and level ``k``,
#: counting levels tightest-first, with ``k = 0`` above every level and ``k = L`` below every one -
#: or ``("tie", i)`` - sharing level ``i``.
Placement = tuple[str, int]

#: A slot is a placement, or a pair ``(general, exponent)`` when the layer sits somewhere else
#: inside the right operand of ``^``. The pair is the only non-layered object in the space.
Slot = Any

#: The three structures a convention can have, tightest first. Every headline count is reported per
#: kind, because they do not have the same answer and an aggregate over them would hide that.
CONVENTION_KINDS: tuple[str, ...] = ("linear", "exponent_prefix", "split")


def placements(level_count: int) -> tuple[Placement, ...]:
    """The ``2L + 1`` placements available in a stack of ``L`` levels, tightest first."""
    result: list[Placement] = []
    for index in range(level_count):
        result.append(("gap", index))
        result.append(("tie", index))
    result.append(("gap", level_count))
    return tuple(result)


def slots(level_count: int) -> tuple[Slot, ...]:
    """Every slot: each placement, then every ordered pair of distinct placements as a split."""
    base = placements(level_count)
    split = tuple(
        (general, exponent) for general in base for exponent in base if general != exponent
    )
    return base + split


def is_split(slot: Slot) -> bool:
    """A slot is split when it is a pair of placements rather than one."""
    return isinstance(slot[0], tuple)


def slot_parts(slot: Slot) -> tuple[Placement, Placement]:
    """``(general placement, exponent-position placement)`` for any slot."""
    if is_split(slot):
        return slot[0], slot[1]
    return slot, slot


@dataclass(frozen=True)
class Convention:
    """One tiered convention: a base, a slot for juxtaposition, a slot for minus, one flag."""

    base_id: str
    jux: Slot
    neg: Slot
    exponent_prefix: bool

    @property
    def id(self) -> str:
        return f"{self.base_id}|jux={_slot_id(self.jux)}|neg={_slot_id(self.neg)}|xp={int(self.exponent_prefix)}"

    @property
    def kind(self) -> str:
        """Which of the three structures this convention has. The headline is read per kind.

        ``linear``           a totally ordered stack of layers, and nothing else. This is what
                             "tiered syntax layers" most naturally means.
        ``exponent_prefix``  a linear stack plus Python's ``factor: '-' factor | power`` - a
                             layered CFG, but not a linear one, because ``^``'s right operand
                             re-enters the chain above the minus layer rather than below it.
        ``split``            a second layer chain used inside the right operand of ``^``.
        """
        if is_split(self.jux) or is_split(self.neg):
            return "split"
        return "exponent_prefix" if self.exponent_prefix else "linear"

    @property
    def layered(self) -> bool:
        """True when the convention is a plain linear stack of layers."""
        return self.kind == "linear"


def _slot_id(slot: Slot) -> str:
    if is_split(slot):
        return f"{slot[0][0]}{slot[0][1]}>{slot[1][0]}{slot[1][1]}"
    return f"{slot[0]}{slot[1]}"


_BASES: dict[str, Grammar] = {grammar.id: grammar for grammar in GRAMMARS_2}

#: The conventional Generation 2 base: ``^`` tightest, then ``* /`` tied, then ``+ -`` tied.
CONTROL_BASE: Grammar = control_grammar_2()

#: The bases whose FULL slot space - splits included - is swept. The conventional one, plus two
#: strict orderings from the ends of the registry so the split verdict is not read off one base.
FULL_SWEEP_BASE_IDS: tuple[str, ...] = ("H0", "H001", "H120")


def conventions_over(base: Grammar, splits: bool = True) -> tuple[Convention, ...]:
    """Every convention over one base: all slots for both roles, both exponent-prefix values."""
    level_count = len(base.levels)
    available = slots(level_count) if splits else placements(level_count)
    return tuple(
        Convention(base.id, jux, neg, exponent_prefix)
        for jux in available
        for neg in available
        for exponent_prefix in (False, True)
    )


def _convention_space() -> tuple[tuple[Convention, ...], int]:
    swept: dict[Convention, None] = {}
    total = 0
    for base in GRAMMARS_2:
        level_count = len(base.levels)
        total += (len(slots(level_count)) ** 2) * 2
        for convention in conventions_over(base, splits=False):
            swept.setdefault(convention, None)
    for base_id in FULL_SWEEP_BASE_IDS:
        for convention in conventions_over(_BASES[base_id], splits=True):
            swept.setdefault(convention, None)
    return tuple(swept), total


#: The conventions this experiment sweeps, and the size of the space they are drawn from. The
#: difference between the two is a computational limit; :func:`flat_equivalence` reports both.
CONVENTIONS: tuple[Convention, ...]
CONVENTION_SPACE_SIZE: int
CONVENTIONS, CONVENTION_SPACE_SIZE = _convention_space()


#: The reading in which juxtaposition binds tighter than ``/`` - printed mathematics and physics,
#: where ``1/2x`` is ``1/(2x)``. ``^`` tightest, then juxtaposition, then minus, then ``* /``.
TIGHT_JUXTAPOSITION: Convention = Convention("H0", ("gap", 1), ("gap", 1), True)

#: The reading in which juxtaposition is an alias for ``*`` - programming languages and the strict
#: left-to-right convention, where ``1/2x`` is ``(1/2)x``.
ALIAS_JUXTAPOSITION: Convention = Convention("H0", ("tie", 1), ("gap", 1), True)

#: The control this module renders against. It is the printed-mathematics reading, and the choice is
#: a declaration rather than an observation - the other reading is one line above. It is also, as it
#: happens, one of the conventions :func:`flat_equivalence` finds NO flat table for; its sibling with
#: ``exponent_prefix`` off has one, which is what isolates the feature responsible.
CONTROL_CONVENTION: Convention = TIGHT_JUXTAPOSITION


# ---------------------------------------------------------------------------- compiling a stack


@dataclass(frozen=True)
class Layer:
    """One syntactic layer: the infix operators it holds, whether it juxtaposes, whether it negates."""

    ops: frozenset
    assoc: str
    jux: bool
    neg: bool


@dataclass(frozen=True)
class Compiled:
    """A convention turned into two layer stacks, each ordered LOOSEST first."""

    general: tuple[Layer, ...]
    exponent: tuple[Layer, ...]
    exponent_entry: int
    exponent_prefix: bool


def _stack(levels: tuple[tuple[str, ...], ...], jux: Placement, neg: Placement) -> tuple[Layer, ...]:
    """Build one layer stack, tightest first, then reverse it.

    At a shared gap the minus layer is the LOOSER of the two, so ``-2x`` reads ``-(2x)``. That is a
    declaration; both readings denote the same object, so nothing in the results turns on it.
    """
    tight_first: list[Layer] = []
    for index in range(len(levels) + 1):
        if jux == ("gap", index):
            tight_first.append(Layer(frozenset(), "left", True, False))
        if neg == ("gap", index):
            tight_first.append(Layer(frozenset(), "left", False, True))
        if index < len(levels):
            ops = frozenset(levels[index])
            has_jux = jux == ("tie", index)
            has_neg = neg == ("tie", index)
            assoc = "right" if ops == frozenset({"^"}) and not has_jux else "left"
            tight_first.append(Layer(ops, assoc, has_jux, has_neg))
    return tuple(reversed(tight_first))


def _caret_index(stack: tuple[Layer, ...]) -> int:
    for index, layer in enumerate(stack):
        if "^" in layer.ops:
            return index
    raise ValueError("no layer holds '^'")


@lru_cache(maxsize=None)
def compile_convention(convention: Convention) -> Compiled:
    """Turn a convention into the two stacks the parser walks. Cached: this is the hot path."""
    levels = _BASES[convention.base_id].levels
    jux_general, jux_exponent = slot_parts(convention.jux)
    neg_general, neg_exponent = slot_parts(convention.neg)
    general = _stack(levels, jux_general, neg_general)
    exponent = _stack(levels, jux_exponent, neg_exponent)
    caret = _caret_index(exponent)
    entry = caret if exponent[caret].assoc == "right" else caret + 1
    return Compiled(general, exponent, entry, convention.exponent_prefix)


# --------------------------------------------------------------------------- the layered parser


class TieredParser:
    """A genuine tiered recursive-descent parser: one function call per syntactic layer.

    This is T26's "tiered syntax layers" written as such - not a precedence table with two extra
    rows. The distinction is the whole experiment, which is why the flat model in this module is a
    SEPARATE implementation rather than the same code with different numbers.
    """

    def __init__(self, tokens: tuple[Token3, ...], compiled: Compiled) -> None:
        self.tokens = tokens
        self.compiled = compiled
        self.index = 0

    def parse(self) -> Any:
        result = self._layer(0, False)
        if self._current.kind != "eof":
            raise ValueError(f"Unexpected token: {self._current.value!r}")
        return result

    @property
    def _current(self) -> Token3:
        return self.tokens[self.index]

    def _advance(self) -> Token3:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def _layer(self, position: int, in_exponent: bool) -> Any:
        stack = self.compiled.exponent if in_exponent else self.compiled.general
        if position >= len(stack):
            return self._primary()
        layer = stack[position]
        token = self._current
        if layer.neg and token.kind == "operator" and token.value == "-":
            self._advance()
            return Negate(self._layer(position, in_exponent))
        left = self._layer(position + 1, in_exponent)
        while True:
            token = self._current
            if token.kind == "operator" and token.value in layer.ops:
                self._advance()
                if token.value == "^":
                    right = self._exponent_operand()
                elif layer.assoc == "right":
                    right = self._layer(position, in_exponent)
                else:
                    right = self._layer(position + 1, in_exponent)
                left = Binary(token.value, left, right)
                if layer.assoc == "right":
                    return left
                continue
            if layer.jux and starts_primary(token):
                left = Binary("*", left, self._layer(position + 1, in_exponent))
                continue
            return left

    def _exponent_operand(self) -> Any:
        """``^``'s right operand: the exponent stack, optionally behind a prefix-minus chain.

        ``exponent_prefix`` is Python's ``factor: '-' factor | power`` and it is what lets a
        convention read ``-x^2`` as ``-(x^2)`` and still parse ``x^-2``.
        """
        if self.compiled.exponent_prefix:
            token = self._current
            if token.kind == "operator" and token.value == "-":
                self._advance()
                return Negate(self._exponent_operand())
        return self._layer(self.compiled.exponent_entry, True)

    def _primary(self) -> Any:
        token = self._advance()
        if token.kind == "number":
            if "/" in token.value:
                numerator, denominator = token.value.split("/", 1)
                return Number(_fraction(int(numerator), int(denominator)))
            return Number(_fraction(int(token.value), 1))
        if token.kind == "name":
            return Variable(token.value)
        if token.kind == "left":
            result = self._layer(0, False)
            if self._advance().kind != "right":
                raise ValueError("Expected closing parenthesis")
            return result
        raise ValueError(f"Expected number, variable, or parenthesized expression; got {token.value!r}")


def _fraction(numerator: int, denominator: int) -> Fraction:
    return Fraction(numerator, denominator)


def parse_tiered(source: str, convention: Convention, literal_policy: str = LITERAL_POLICY) -> Any:
    """Parse ``source`` under a tiered convention. Raises ``ValueError`` when the convention rejects it."""
    return TieredParser(tokenize_tiered(source, literal_policy), compile_convention(convention)).parse()


# ------------------------------------------------------------- FIRST: the conservative extension


#: Generation 1 strings added to the audit corpus for this module specifically: the composite
#: rational literal in every position the tokenizer axis could disturb.
AGREEMENT_EXTRA_SOURCES_3: tuple[str, ...] = (
    "1/2",
    "1/2 * a",
    "a * 1/2",
    "(1/2 + a) * b",
)


def agreement_sources() -> tuple[str, ...]:
    """The Generation 1 corpus the audit runs over, deduplicated in first-seen order."""
    seen: dict[str, None] = {}
    for source in generation_one_sources():
        seen.setdefault(source, None)
    for source in AGREEMENT_EXTRA_SOURCES_3:
        seen.setdefault(source, None)
    return tuple(seen)


def embed_caret(grammar: Grammar, position: int) -> Grammar:
    """Insert ``^`` as its own level at ``position`` into a Generation 1 grammar."""
    levels = list(grammar.levels)
    if not 0 <= position <= len(levels):
        raise ValueError(f"position must be in 0..{len(levels)}; got {position}")
    levels.insert(position, ("^",))
    ordered = tuple(tuple(level) for level in levels)
    flattened = tuple(operator for level in ordered for operator in level)
    return Grammar(f"{grammar.id}+^@{position}", flattened, ordered)


def caret_embeddings(grammar: Grammar) -> tuple[Grammar, ...]:
    return tuple(embed_caret(grammar, position) for position in range(len(grammar.levels) + 1))


def _audit_conventions(embedded: Grammar) -> tuple[Convention, ...]:
    """The split-free conventions over one embedding, both exponent-prefix values.

    Splits are excluded from THIS grid and audited separately over the conventional base; the
    reason they cannot matter here is not an argument but the site census in the audit's result,
    which reports zero juxtaposition sites and zero prefix-minus sites over every source. A slot
    the parser never reaches cannot change a tree.
    """
    available = placements(len(embedded.levels))
    return tuple(
        Convention(embedded.id, jux, neg, exponent_prefix)
        for jux in available
        for neg in available
        for exponent_prefix in (False, True)
    )


def audit_cell(
    source: str,
    convention: Convention,
    literal_policy: str,
    expected: Any,
    tiered_parse: Any = None,
) -> dict[str, Any] | None:
    """One audit cell: ``None`` when the tiered parse equals ``expected``, else the disagreement.

    Both audit paths go through this one function so there is one place where a **rejection** is
    turned into a disagreement rather than swallowed. That branch never fires on the Generation 1
    corpus - the site census is zero - so nothing in a passing run exercises it, and an audit that
    quietly treated a rejection as agreement would look identical. Mutation testing found exactly
    that hole, which is why the branch is reachable from a test with a convention that really does
    reject its input.
    """
    parse_one = parse_tiered if tiered_parse is None else tiered_parse
    try:
        produced = parse_one(source, convention, literal_policy)
    except ValueError as error:
        produced = f"REJECTED: {error}"
    if produced == expected:
        return None
    return {
        "source": source,
        "convention": convention.id,
        "expected": str(expected),
        "produced": str(produced),
    }


def _audit_payload(payload: tuple[str, int, tuple[str, ...], str]) -> dict[str, Any]:
    grammar_id, position, sources, literal_policy = payload
    grammar = {item.id: item for item in all_grammars()}[grammar_id]
    embedded = embed_caret(grammar, position)
    _BASES.setdefault(embedded.id, embedded)
    disagreements: list[dict[str, Any]] = []
    cells = 0
    conventions = _audit_conventions(embedded)
    expected_by_source = {source: parse(source, grammar) for source in sources}
    for convention in conventions:
        for source in sources:
            cells += 1
            cell = audit_cell(source, convention, literal_policy, expected_by_source[source])
            if cell is not None:
                disagreements.append(dict(cell, generation_one_grammar=grammar_id))
    return {"cells": cells, "conventions": len(conventions), "disagreements": disagreements}


def agreement_audit(
    sources: Sequence[str] | None = None,
    grammars: Sequence[Grammar] | None = None,
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
    tiered_parse: Any = None,
) -> dict[str, Any]:
    """Is the tiered language a conservative extension of Generation 1? Checked cell by cell.

    For every Generation 1 grammar, every position ``^`` can be embedded at, every split-free
    tier convention over that embedding, both exponent-prefix values, and every Generation 1
    source, :func:`parse_tiered` must return the tree :func:`parseatlas.parser.parse` returns -
    equal as dataclasses. A rejection counts as a disagreement.

    ``tiered_parse`` exists so the audit can be tested against a real divergence rather than only
    against itself; when it is given, the sequential path is used and the injected callable is
    asked for every cell.
    """
    sources = tuple(sources) if sources is not None else agreement_sources()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    census = {
        "juxtaposition_sites": sum(juxtaposition_sites(source, literal_policy) for source in sources),
        "prefix_minus_sites": sum(prefix_minus_sites(source, literal_policy) for source in sources),
    }
    if tiered_parse is not None:
        return _agreement_sequential(sources, grammars, literal_policy, tiered_parse, census)
    payloads = [
        (grammar.id, position, sources, literal_policy)
        for grammar in grammars
        for position in range(len(grammar.levels) + 1)
    ]
    results = _map_cells(_audit_payload, payloads, workers=workers, seconds_per_cell=AUDIT_PAYLOAD_SECONDS)
    disagreements = [item for result in results for item in result["disagreements"]]
    return {
        "sources": len(sources),
        "generation_one_grammars": len(grammars),
        "embeddings": len(payloads),
        "conventions_per_embedding": tuple(sorted({result["conventions"] for result in results})),
        "cells": sum(result["cells"] for result in results),
        "disagreements": len(disagreements),
        "disagreeing": tuple(disagreements[:20]),
        "conservative": not disagreements,
        "literal_policy": literal_policy,
        "site_census": census,
    }


def _agreement_sequential(
    sources: tuple[str, ...],
    grammars: tuple[Grammar, ...],
    literal_policy: str,
    tiered_parse: Any,
    census: dict[str, Any],
) -> dict[str, Any]:
    disagreements: list[dict[str, Any]] = []
    cells = 0
    embeddings = 0
    convention_counts: set[int] = set()
    for grammar in grammars:
        for embedded in caret_embeddings(grammar):
            embeddings += 1
            _BASES.setdefault(embedded.id, embedded)
            conventions = _audit_conventions(embedded)
            convention_counts.add(len(conventions))
            for convention in conventions:
                for source in sources:
                    cells += 1
                    cell = audit_cell(
                        source, convention, literal_policy, parse(source, grammar), tiered_parse
                    )
                    if cell is not None:
                        disagreements.append(dict(cell, generation_one_grammar=grammar.id))
    return {
        "sources": len(sources),
        "generation_one_grammars": len(grammars),
        "embeddings": embeddings,
        "conventions_per_embedding": tuple(sorted(convention_counts)),
        "cells": cells,
        "disagreements": len(disagreements),
        "disagreeing": tuple(disagreements[:20]),
        "conservative": not disagreements,
        "literal_policy": literal_policy,
        "site_census": census,
    }


# ------------------------------------------------------------------------------ the flat model


@dataclass(frozen=True)
class FlatConvention:
    """One binding power per role, and one rule for where a prefix operator may appear.

    ``ranks`` is aligned with :data:`ROLES`; a higher rank binds tighter. Equal ranks are a tied
    level, which is what ``G0`` and ``H0`` have and what a strict permutation cannot express.

    ``prefix_rule`` is ``level`` when a prefix minus is admitted only where its own power is at
    least the level being parsed, and ``anywhere`` when it is admitted in any operand position -
    the classic Pratt behaviour. Both are in the search space because handicapping the flat model
    would manufacture a confirmation of T26.
    """

    ranks: tuple[int, ...]
    prefix_rule: str

    @property
    def id(self) -> str:
        order = ",".join(f"{role}{rank}" for role, rank in zip(ROLES, self.ranks))
        return f"{order}|{self.prefix_rule}"

    @property
    def powers(self) -> dict[str, int]:
        return dict(zip(ROLES, self.ranks))


@lru_cache(maxsize=None)
def _flat_tables(convention: FlatConvention) -> tuple[dict[str, int], int, int, str, dict[str, str]]:
    powers = convention.powers
    caret = powers["^"]
    shared = any(powers[role] == caret for role in ("*", "/", "+", "-", JUX))
    assoc = dict(ASSOCIATIVITY_3)
    assoc["^"] = "left" if shared else "right"
    binary = {role: powers[role] for role in BINARY_OPERATORS}
    return binary, powers[JUX], powers[NEG], convention.prefix_rule, assoc


class FlatParser:
    """Precedence climbing over one table - the model T26 says is not enough.

    Deliberately a separate implementation from :class:`TieredParser`. If the two agreed only
    because they shared code, the headline would be a tautology instead of a measurement.
    """

    def __init__(self, tokens: tuple[Token3, ...], convention: FlatConvention) -> None:
        self.tokens = tokens
        self.index = 0
        self.powers, self.jux_power, self.neg_power, self.prefix_rule, self.assoc = _flat_tables(convention)

    def parse(self) -> Any:
        result = self._expression(0)
        if self._current.kind != "eof":
            raise ValueError(f"Unexpected token: {self._current.value!r}")
        return result

    @property
    def _current(self) -> Token3:
        return self.tokens[self.index]

    def _advance(self) -> Token3:
        token = self.tokens[self.index]
        self.index += 1
        return token

    def _expression(self, minimum_power: int) -> Any:
        token = self._current
        if token.kind == "operator" and token.value == "-" and (
            self.prefix_rule == "anywhere" or self.neg_power >= minimum_power
        ):
            self._advance()
            left: Any = Negate(self._expression(self.neg_power))
        else:
            left = self._primary()
        while True:
            token = self._current
            if token.kind == "operator" and token.value in self.powers and self.powers[token.value] >= minimum_power:
                self._advance()
                power = self.powers[token.value]
                right_minimum = power if self.assoc[token.value] == "right" else power + 1
                left = Binary(token.value, left, self._expression(right_minimum))
                continue
            if starts_primary(token) and self.jux_power >= minimum_power:
                left = Binary("*", left, self._expression(self.jux_power + 1))
                continue
            return left

    def _primary(self) -> Any:
        token = self._advance()
        if token.kind == "number":
            if "/" in token.value:
                numerator, denominator = token.value.split("/", 1)
                return Number(_fraction(int(numerator), int(denominator)))
            return Number(_fraction(int(token.value), 1))
        if token.kind == "name":
            return Variable(token.value)
        if token.kind == "left":
            result = self._expression(0)
            if self._advance().kind != "right":
                raise ValueError("Expected closing parenthesis")
            return result
        raise ValueError(f"Expected number, variable, or parenthesized expression; got {token.value!r}")


def parse_flat(source: str, convention: FlatConvention, literal_policy: str = LITERAL_POLICY) -> Any:
    return FlatParser(tokenize_tiered(source, literal_policy), convention).parse()


def _ordered_set_partitions(items: tuple[str, ...]) -> list[tuple[tuple[str, ...], ...]]:
    if not items:
        return [()]
    result: list[tuple[tuple[str, ...], ...]] = []
    for size in range(1, len(items) + 1):
        for block in combinations(items, size):
            remaining = tuple(item for item in items if item not in block)
            for tail in _ordered_set_partitions(remaining):
                result.append((block,) + tail)
    return result


@lru_cache(maxsize=1)
def flat_conventions() -> tuple[FlatConvention, ...]:
    """Every flat model: every weak order on the seven roles, times both prefix rules.

    A weak order rather than a permutation, because tied levels are what the conventional grammar
    has - ``* /`` together and ``+ -`` together - and a search over strict orders alone would
    exclude the very convention the corpus is written in. The count is the ordered Bell number
    ``a(7) = 47293``, doubled by the prefix rule.
    """
    orders = _ordered_set_partitions(ROLES)
    result: list[FlatConvention] = []
    for order in orders:
        ranks_by_role: dict[str, int] = {}
        for level, block in enumerate(order):
            for role in block:
                ranks_by_role[role] = len(order) - level
        ranks = tuple(ranks_by_role[role] for role in ROLES)
        for prefix_rule in ("level", "anywhere"):
            result.append(FlatConvention(ranks, prefix_rule))
    return tuple(result)


def flat_twin_of(convention: Convention) -> FlatConvention | None:
    """The flat model a LINEAR tier stack translates to, read straight off the stack.

    A layer's binding power is its depth in the stack, which is the whole content of the claim that
    a linear stack of tiers is a precedence table: the translation writes down no rule that the
    stack does not already carry, and the prefix rule is ``level`` because a layer is only entered
    from a looser one. ``None`` for a convention that is not a linear stack, because there is then
    nothing to translate.

    :func:`layered_translation_audit` checks the translation produces the SAME parse, source by
    source. It is the difference between "some flat model happens to agree" and "this one is that
    flat model", and the second is what T26 is actually about.
    """
    if not convention.layered:
        return None
    compiled = compile_convention(convention)
    stack = compiled.general
    powers: dict[str, int] = {}
    for index, layer in enumerate(stack):
        # the stack is ordered LOOSEST first, so depth in it IS binding power
        power = index + 1
        for operator in layer.ops:
            powers[operator] = power
        if layer.jux:
            powers[JUX] = power
        if layer.neg:
            powers[NEG] = power
    return FlatConvention(tuple(powers[role] for role in ROLES), "level")


def _translation_payload(
    payload: tuple[tuple[Convention, ...], tuple[str, ...], str]
) -> dict[str, Any]:
    conventions, sources, literal_policy = payload
    disagreements: list[dict[str, str]] = []
    cells = 0
    for convention in conventions:
        twin = flat_twin_of(convention)
        assert twin is not None
        tiered, _ = _readings(parse_tiered, sources, convention, literal_policy)
        flat, _ = _readings(parse_flat, sources, twin, literal_policy)
        for index, source in enumerate(sources):
            cells += 1
            if tiered[index] != flat[index]:
                disagreements.append(
                    {"convention": convention.id, "flat": twin.id, "source": source,
                     "tiered": tiered[index], "flat_reading": flat[index]}
                )
    return {"cells": cells, "disagreements": disagreements}


def layered_translation_audit(
    conventions: Sequence[Convention] | None = None,
    sources: Sequence[str] | None = None,
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
) -> dict[str, Any]:
    """Does every linear tier stack parse exactly as its translated flat table does?

    This is the first half of the answer to T26 and it is stated as an identity rather than as an
    existence claim: for a linear stack the flat model is not merely findable, it is the stack's own
    depths written as numbers.
    """
    conventions = tuple(conventions) if conventions is not None else tuple(
        convention for convention in CONVENTIONS if convention.layered
    )
    sources = tuple(sources) if sources is not None else CORPUS_SOURCES
    payloads = [(chunk, sources, literal_policy) for chunk in _chunks(conventions, _sweep_chunks())]
    results = _map_cells(
        _translation_payload, payloads, workers=workers, seconds_per_cell=SWEEP_PAYLOAD_SECONDS
    )
    disagreements = [item for result in results for item in result["disagreements"]]
    return {
        "conventions": len(conventions),
        "sources": len(sources),
        "cells": sum(result["cells"] for result in results),
        "disagreements": len(disagreements),
        "disagreeing": tuple(disagreements[:10]),
        "translation_is_exact": not disagreements,
    }


# ------------------------------------------------------------------------------------ the corpus


@dataclass(frozen=True)
class Formula3:
    """One corpus entry: a name, an area, and the source as it is written."""

    name: str
    area: str
    source: str


#: The corpus. Named mathematics that uses the new syntax, plus the ambiguities the card names.
#:
#: Every juxtaposition is written with a space or a bracket, because the tokenizer's name pattern
#: is Generation 1's maximal munch and ``ax`` is therefore ONE variable. That is a limit of the
#: language and it is visible in every source here rather than hidden behind a helper.
CORPUS_3: tuple[Formula3, ...] = (
    # ---- the named ambiguities ---------------------------------------------------------------
    Formula3("minus_square", "ambiguity", "-x^2"),
    Formula3("minus_literal_square", "ambiguity", "-2^2"),
    Formula3("half_x", "ambiguity", "1/2x"),
    Formula3("viral_division", "ambiguity", "6/2(1 + 2)"),
    Formula3("coefficient_square", "ambiguity", "2x^2"),
    Formula3("exponent_juxtaposition", "ambiguity", "x^2y"),
    Formula3("harmonic_denominator", "ambiguity", "1/n(n + 1)"),
    Formula3("vertex_abscissa", "ambiguity", "-b/2a"),
    Formula3("minus_after_minus", "ambiguity", "a - -b"),
    Formula3("negative_exponent", "ambiguity", "x^-2"),
    # ---- algebra ------------------------------------------------------------------------------
    Formula3("quadratic_standard", "algebra", "a x^2 + b x + c"),
    Formula3("discriminant", "algebra", "b^2 - 4 a c"),
    Formula3("difference_of_squares_factored", "algebra", "(a + b)(a - b)"),
    Formula3("binomial_square_factored", "algebra", "(a + b)^2"),
    Formula3("cubic_factored", "algebra", "x(x - 1)(x - 2)"),
    Formula3("distributive_factored", "algebra", "a(b + c)"),
    Formula3("linear_form", "algebra", "a x + b y - c"),
    Formula3("negative_slope_line", "algebra", "-m x + c"),
    Formula3("negative_reciprocal", "algebra", "-1/x"),
    Formula3("triangular_number", "algebra", "n(n + 1)/2"),
    # ---- geometry -----------------------------------------------------------------------------
    Formula3("circumference", "geometry", "2 pi r"),
    Formula3("circle_area", "geometry", "pi r^2"),
    Formula3("sphere_volume", "geometry", "4/3 pi r^3"),
    Formula3("trapezoid_area", "geometry", "1/2 (a + b) h"),
    Formula3("negated_slope", "geometry", "-(y2 - y1)/(x2 - x1)"),
    # ---- physics ------------------------------------------------------------------------------
    Formula3("kinetic_energy", "physics", "1/2 m v^2"),
    Formula3("mass_energy", "physics", "m c^2"),
    Formula3("inverse_square", "physics", "1/r^2"),
    Formula3("coulomb", "physics", "k q1 q2/r^2"),
    Formula3("exponential_decay", "physics", "e^-x"),
    Formula3("exponential_decay_rate", "physics", "e^-k t"),
    Formula3("gaussian_exponent", "physics", "-x^2/2"),
    Formula3("compound_interest", "physics", "p(1 + r)^n"),
    Formula3("harmonic_mean", "physics", "2 a b/(a + b)"),
    # ---- analysis -----------------------------------------------------------------------------
    Formula3("cosine_series", "analysis", "1 - x^2/2 + x^4/24"),
    Formula3("sine_series", "analysis", "x - x^3/6"),
    Formula3("half_square", "analysis", "1/2 x^2"),
    Formula3("root_numerator", "analysis", "-b + d"),
    # ---- syntax probes ------------------------------------------------------------------------
    Formula3("explicit_times_negative", "probe", "a * -b"),
    Formula3("negated_sum", "probe", "-x - y"),
    Formula3("literal_negative_power", "probe", "2^-3"),
    Formula3("doubly_negative_power", "probe", "-2^-3"),
    Formula3("bare_juxtaposition", "probe", "x y"),
    Formula3("coefficient_chain", "probe", "2 x y"),
    Formula3("plain_product_sum", "probe", "a * b + c"),
    Formula3("plain_left_chain", "probe", "a - b - c"),
)

#: Corpus sources ordered shortest first, ties broken lexicographically. This is the order in which
#: a separating source is looked for, and the tie-break is declared because the answer names one.
CORPUS_SOURCES: tuple[str, ...] = tuple(
    sorted({formula.source for formula in CORPUS_3}, key=lambda text: (len(text), text))
)

#: A reading that no convention produces, used as the vector entry for a rejected source.
REJECTED: str = "REJECTED"


def role_support(source: str, literal_policy: str = LITERAL_POLICY) -> tuple[str, ...]:
    """The roles a source can actually exercise - its T6 support, widened to seven roles.

    A source using ``j`` of the seven roles cannot separate two models that agree on those ``j``,
    so every count in this module is reported next to this.
    """
    tokens = tokenize_tiered(source, literal_policy)
    present: dict[str, None] = {}
    if juxtaposition_sites(source, literal_policy):
        present.setdefault(JUX, None)
    if prefix_minus_sites(source, literal_policy):
        present.setdefault(NEG, None)
    previous: Token3 | None = None
    for token in tokens:
        if token.kind == "operator":
            prefix = previous is None or previous.kind in ("operator", "left")
            if not (token.value == "-" and prefix):
                present.setdefault(token.value, None)
        previous = token
    return tuple(role for role in ROLES if role in present)


# --------------------------------------------------------------------------------- the renderer


def _tree_nodes(tree: Any) -> tuple[Any, ...]:
    """Every node of a tree in a fixed pre-order. Bracketable positions are exactly these."""
    collected: list[Any] = []

    def walk(node: Any) -> None:
        collected.append(node)
        if isinstance(node, Binary):
            walk(node.left)
            walk(node.right)
        elif isinstance(node, Negate):
            walk(node.operand)

    walk(tree)
    return tuple(collected)


def _multiplication_nodes(tree: Any) -> tuple[Any, ...]:
    return tuple(node for node in _tree_nodes(tree) if isinstance(node, Binary) and node.operator == "*")


def _needs_space(left: str, right: str) -> bool:
    """Does a juxtaposition boundary need a space to survive the tokenizer?

    ``2x`` is safe - the number pattern stops at the letter. ``x y`` is not, because maximal munch
    would read ``xy`` as one name; nor is ``2 3``; nor is a composite rational literal followed by
    a name, because the default literal policy would split it back into a division.
    """
    if not left or not right:
        return False
    last, first = left[-1], right[0]
    if not _WORD.match(last) or not _WORD.match(first):
        return False
    if last.isdigit() and not first.isdigit():
        return bool(_TRAILING_RATIONAL.search(left))
    return True


def _write(node: Any, bracketed: frozenset, juxtaposed: frozenset) -> str:
    text = _write_bare(node, bracketed, juxtaposed)
    return f"({text})" if id(node) in bracketed else text


def _write_bare(node: Any, bracketed: frozenset, juxtaposed: frozenset) -> str:
    if isinstance(node, Number):
        value = node.value
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(node, Variable):
        return node.name
    if isinstance(node, Negate):
        return "-" + _write(node.operand, bracketed, juxtaposed)
    left = _write(node.left, bracketed, juxtaposed)
    right = _write(node.right, bracketed, juxtaposed)
    if node.operator == "*" and id(node) in juxtaposed:
        return f"{left} {right}" if _needs_space(left, right) else f"{left}{right}"
    return f"{left} {node.operator} {right}"


def render_tiered(
    tree: Any,
    convention: Convention,
    literal_policy: str = LITERAL_POLICY,
) -> str:
    """Write ``tree`` under ``convention`` with the fewest bracket pairs that denote it.

    The renderer is a SEARCH, not a bracket rule, and that is deliberate. A rule derived from the
    parser would have to be re-derived for every context-dependent slot in the space, and its
    minimality would then be an argument. Searching bracket counts upward makes minimality a
    property of the algorithm: the first writing that reparses to ``tree`` is by construction one
    with the fewest pairs, and :func:`minimality_witness` reports how many cheaper writings were
    refuted to get there.
    """
    return minimality_witness(tree, convention, literal_policy)["rendering"]


def minimality_witness(
    tree: Any,
    convention: Convention,
    literal_policy: str = LITERAL_POLICY,
    leaf_brackets: bool = False,
) -> dict[str, Any]:
    """The minimal writing of ``tree``, with the exhaustive search that proves it minimal.

    The writing space is complete for the question asked. A writing that reparses to ``tree`` may
    place a bracket only around a node of ``tree`` - any other span would not be a subtree of the
    parse - and each ``*`` node is written either explicitly or as juxtaposition. So the space is
    ``subset of nodes`` x ``choice per multiplication``, and the search visits all of it below the
    answer.

    **One restriction, declared here because it is a restriction on an enumeration.** Only compound
    nodes are bracketable by default. A bracket around a LEAF is inert for parsing - ``(x)`` and
    ``x`` are the same primary in every context - so a writing that brackets a leaf has a strictly
    cheaper writing with the same parse, and cannot be a minimum. That is an argument, so
    ``leaf_brackets=True`` runs the wider search and the test suite checks the two agree rather
    than taking the argument on trust. Experiment 0047 is why.

    What the space does NOT contain: writings that reorder commutative operands, repeated brackets
    around one node, and spacings other than the one :func:`_needs_space` picks. None can lower a
    bracket count.
    """
    nodes = _tree_nodes(tree)
    sites = nodes if leaf_brackets else tuple(
        node for node in nodes if isinstance(node, (Binary, Negate))
    )
    multiplications = _multiplication_nodes(tree)
    identities = [id(node) for node in sites]
    multiplication_ids = [id(node) for node in multiplications]
    checked = 0
    for count in range(len(identities) + 1):
        for chosen in combinations(identities, count):
            bracketed = frozenset(chosen)
            for mask in range(1 << len(multiplication_ids)):
                juxtaposed = frozenset(
                    identity for index, identity in enumerate(multiplication_ids) if mask >> index & 1
                )
                text = _write(tree, bracketed, juxtaposed)
                checked += 1
                try:
                    if parse_tiered(text, convention, literal_policy) == tree:
                        return {
                            "rendering": text,
                            "pairs": count,
                            "writings_checked": checked,
                            "cheaper_writings_refuted": checked - 1,
                            "round_trip": True,
                            "minimal": True,
                        }
                except ValueError:
                    continue
    raise RoundTripError(f"no writing of the tree round-trips under {convention.id}")


class RoundTripError(ValueError):
    """No writing of a tree reparses to it. If raised, every cost number beside it is void."""


def parenthesis_cost(tree: Any, convention: Convention, literal_policy: str = LITERAL_POLICY) -> int:
    """The bracket pairs a convention forces on a tree - direction B's cost, with juxtaposition.

    Juxtaposition is not only a parsing question: where it binds tighter than the solidus it also
    makes a writing cheaper. ``1/(2*x)`` costs `1` pair under the alias reading and `0` under the
    printed one, where it is simply ``1 / 2x``.
    """
    return minimality_witness(tree, convention, literal_policy)["pairs"]


def formula_tree(formula: Formula3, convention: Convention = CONTROL_CONVENTION) -> Any:
    return parse_tiered(formula.source, convention)


# ------------------------------------------------------------------------------------- semantics


def to_sympy3(node: Any) -> Any:
    """The project's conversion, with ``^`` and prefix minus added and nothing else changed."""
    if isinstance(node, Number):
        if node.value.denominator == 1:
            return Integer(node.value.numerator)
        return Rational(node.value.numerator, node.value.denominator)
    if isinstance(node, Variable):
        return Symbol(node.name, real=True)
    if isinstance(node, Negate):
        return -to_sympy3(node.operand)
    left = to_sympy3(node.left)
    right = to_sympy3(node.right)
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


def undefined_terms3(node: Any) -> tuple[str, ...]:
    """Excluded points from ``/`` nodes, exactly as Generation 1 computes them.

    A pole written as a negative exponent - ``x^-2`` - is NOT detected, which is Generation 2's
    disclosed limit inherited unchanged, and the corpus does contain such entries.
    """
    if isinstance(node, (Number, Variable)):
        return ()
    if isinstance(node, Negate):
        return undefined_terms3(node.operand)
    terms = undefined_terms3(node.left) + undefined_terms3(node.right)
    if node.operator == "/" and (not isinstance(node.right, Number) or node.right.value == 0):
        denominator = to_sympy3(node.right)
        variables = sorted(denominator.free_symbols, key=str)
        if variables:
            terms += tuple(str(point) for point in solve(denominator, variables[0]))
        elif denominator == 0:
            terms += ("all",)
    return tuple(dict.fromkeys(terms))


def canonicalize3(node: Any) -> dict[str, Any]:
    """The project's canonical record. ``domain`` is the inert component of the key (NF-2026-00005)."""
    expression = to_sympy3(node)
    simplified = simplify(expression)
    return {
        "expression": str(simplified),
        "domain": "R",
        "excluded_points": list(undefined_terms3(node)),
        "sympy_expression": simplified,
    }


def object_key(node: Any) -> tuple[str, str, tuple[str, ...]]:
    """The project's semantic identity for a tiered tree."""
    return semantic_key(canonicalize3(node))


# ---------------------------------------------------------------------------------- multicore


#: Cores left free so a sweep cannot starve an interactive session. Policy, not measurement.
WORKER_HEADROOM_CORES: int = 1

#: Seconds to raise a spawn-start pool whose workers import this module, and so SymPy. MEASURED on
#: this host by :func:`measure_pool_startup`, and an order of magnitude above every per-payload cost
#: below, which is why the chunking is coarse.
POOL_STARTUP_SECONDS: float = 7.2

#: Seconds for one audit payload - one ``(grammar, ^ position)`` pair over every split-free
#: convention and every source. MEASURED by :func:`measure_cell_seconds`.
AUDIT_PAYLOAD_SECONDS: float = 1.7

#: Seconds for one sweep payload - one chunk of conventions parsed over the whole corpus.
#: MEASURED by :func:`measure_cell_seconds`.
SWEEP_PAYLOAD_SECONDS: float = 2.4

#: Seconds for one render payload - one chunk of ``(tree, convention)`` cells rendered minimally.
#: MEASURED by :func:`measure_cell_seconds`.
RENDER_PAYLOAD_SECONDS: float = 0.43


def worker_count_for(cores: int, payload_count: int) -> int:
    return max(1, min(cores - WORKER_HEADROOM_CORES, max(payload_count, 1)))


def default_worker_count(payload_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, payload_count)


def should_parallelise(payload_count: int, seconds_per_payload: float, workers: int) -> bool:
    """Is a pool worth raising for this much work? Decided from measured costs, not a rule of thumb."""
    if workers <= 1 or payload_count <= 1:
        return False
    sequential = payload_count * seconds_per_payload
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_cells(
    worker: Any,
    payloads: Sequence[Any],
    workers: int | None = None,
    seconds_per_cell: float = SWEEP_PAYLOAD_SECONDS,
) -> tuple[Any, ...]:
    """Map ``worker`` over ``payloads``, on a process pool when the measurement says to.

    Every payload is a pure function of its input and ``map`` preserves order, so the two paths
    return equal structures - which the test suite checks rather than assumes.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else max(1, int(workers))
    if workers is None and not should_parallelise(len(payloads), seconds_per_cell, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) < 2:
        return tuple(worker(payload) for payload in payloads)
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as pool:
        return tuple(pool.map(worker, payloads, chunksize=1))


def _trivial_cell(payload: int) -> int:
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising the pool, so :data:`POOL_STARTUP_SECONDS` is evidence rather than a guess."""
    resolved = default_worker_count(64) if workers is None else workers
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as pool:
            list(pool.map(_trivial_cell, range(resolved), chunksize=1))
        best = min(best, time.perf_counter() - start)
    return {"workers": resolved, "cores": os.cpu_count(), "repeats": repeats, "seconds": best,
            "declared": POOL_STARTUP_SECONDS}


def measure_cell_seconds() -> dict[str, Any]:
    """Time one payload of each workload, so the routing constants are measurements."""
    start = time.perf_counter()
    _audit_payload((all_grammars()[1].id, 0, agreement_sources(), LITERAL_POLICY))
    audit = time.perf_counter() - start
    sample = 200
    chunk = CONVENTIONS[:sample]
    start = time.perf_counter()
    empty_tables = tuple({} for _ in CORPUS_SOURCES)
    _tiered_payload((chunk, CORPUS_SOURCES, LITERAL_POLICY, empty_tables, frozenset()))
    measured = time.perf_counter() - start
    per_convention = measured / sample
    trees = [formula_tree(formula) for formula in CORPUS_3[:6]]
    render_conventions = conventions_over(CONTROL_BASE, splits=False)[:12]
    start = time.perf_counter()
    _render_payload((tuple(trees), render_conventions, LITERAL_POLICY))
    render = time.perf_counter() - start
    per_render_cell = render / (len(trees) * len(render_conventions))
    return {
        "audit_payload_seconds": audit,
        "sweep_seconds_per_convention": per_convention,
        "sweep_payload_seconds": per_convention * len(CONVENTIONS) / _sweep_chunks(),
        "render_seconds_per_cell": per_render_cell,
        "render_payload_seconds": per_render_cell * len(CORPUS_3) * len(conventions_over(CONTROL_BASE))
        / _sweep_chunks(),
        "declared_audit_payload_seconds": AUDIT_PAYLOAD_SECONDS,
        "declared_sweep_payload_seconds": SWEEP_PAYLOAD_SECONDS,
        "declared_render_payload_seconds": RENDER_PAYLOAD_SECONDS,
    }


def _sweep_chunks() -> int:
    """Chunks a sweep is cut into: four per worker, so a slow chunk cannot stall the tail."""
    return max(1, (os.cpu_count() or 1) - WORKER_HEADROOM_CORES) * 4


# ---------------------------------------------------------------------------------- the sweeps


def _readings(
    parse_one: Any, sources: Sequence[str], model: Any, literal_policy: str
) -> tuple[tuple[str, ...], list[Any]]:
    """One model's reading of every source: the vector of tree spellings, and the trees.

    A source the model REJECTS gets :data:`REJECTED` in the vector. A rejection is a reading like
    any other for the purposes of comparison - two models that reject different sources are not the
    same model - and it is counted separately wherever it could inflate an object count.
    """
    readings: list[str] = []
    trees: list[Any] = []
    for source in sources:
        try:
            tree = parse_one(source, model, literal_policy)
        except ValueError:
            readings.append(REJECTED)
            trees.append(None)
            continue
        readings.append(str(tree))
        trees.append(tree)
    return tuple(readings), trees


def _flat_payload(payload: tuple[tuple[FlatConvention, ...], tuple[str, ...], str]) -> dict[str, Any]:
    conventions, sources, literal_policy = payload
    vectors: dict[tuple[str, ...], str] = {}
    trees: list[dict[str, Any]] = [{} for _ in sources]
    for convention in conventions:
        vector, produced = _readings(parse_flat, sources, convention, literal_policy)
        vectors.setdefault(vector, convention.id)
        for index, tree in enumerate(produced):
            if tree is not None:
                trees[index].setdefault(vector[index], tree)
    return {"vectors": vectors, "trees": trees}


def reading_tables(
    flat_vectors: Sequence[tuple[str, ...]], source_count: int
) -> tuple[dict[str, int], ...]:
    """Per-source code for every reading any flat model produces.

    A flat model's reading VECTOR is one of tens of thousands, but the distinct readings of a single
    source are a handful, so a vector compresses to one byte per source. That compression is the
    difference between shipping the flat answer to each worker and shipping it to each worker
    tens of thousands of times over; it changes no number, only how much of the run is pickling.
    """
    tables: list[dict[str, int]] = []
    for index in range(source_count):
        seen: dict[str, int] = {}
        for vector in flat_vectors:
            reading = vector[index]
            if reading not in seen:
                seen[reading] = len(seen)
        if len(seen) > 255:
            raise ValueError(f"source {index} has {len(seen)} distinct flat readings; recode needed")
        tables.append(seen)
    return tuple(tables)


def _encode(vector: Sequence[str], tables: Sequence[dict[str, int]]) -> bytes | None:
    """A vector's code, or ``None`` when it contains a reading no flat model produces."""
    codes = bytearray()
    for index, reading in enumerate(vector):
        code = tables[index].get(reading)
        if code is None:
            return None
        codes.append(code)
    return bytes(codes)


def _tiered_payload(
    payload: tuple[tuple[Convention, ...], tuple[str, ...], str, tuple[dict[str, int], ...], frozenset]
) -> dict[str, Any]:
    conventions, sources, literal_policy, tables, flat_codes = payload
    matched: dict[bytes, str] = {}
    unmatched: dict[tuple[str, ...], tuple[str, str]] = {}
    trees: list[dict[str, Any]] = [{} for _ in sources]
    counts = {"with_twin": 0, "without_twin": 0}
    by_kind: dict[str, list[set]] = {}
    for kind in CONVENTION_KINDS:
        counts[kind] = 0
        counts[f"{kind}_without_twin"] = 0
        by_kind[kind] = [set() for _ in sources]
    for convention in conventions:
        vector, produced = _readings(parse_tiered, sources, convention, literal_policy)
        for index, tree in enumerate(produced):
            if tree is not None:
                trees[index].setdefault(vector[index], tree)
        code = _encode(vector, tables)
        has_twin = code is not None and code in flat_codes
        counts["with_twin" if has_twin else "without_twin"] += 1
        kind = convention.kind
        counts[kind] += 1
        counts[f"{kind}_without_twin"] += not has_twin
        readings_by_kind = by_kind[kind]
        for index, reading in enumerate(vector):
            readings_by_kind[index].add(reading)
        if has_twin:
            matched.setdefault(code, convention.id)
        else:
            unmatched.setdefault(vector, (convention.id, kind))
    return {"matched": matched, "unmatched": unmatched, "trees": trees, "counts": counts,
            "by_kind": by_kind}


def _chunks(items: Sequence[Any], count: int) -> list[tuple[Any, ...]]:
    if count <= 1 or len(items) <= count:
        return [tuple(items)]
    size = (len(items) + count - 1) // count
    return [tuple(items[start:start + size]) for start in range(0, len(items), size)]


def _merge_trees(target: list[dict[str, Any]], source: list[dict[str, Any]]) -> None:
    for index, table in enumerate(source):
        for text, tree in table.items():
            target[index].setdefault(text, tree)


_SWEEP_MEMO: dict[Any, dict[str, Any]] = {}
_FLAT_MEMO: dict[Any, tuple[dict[tuple[str, ...], str], list[dict[str, Any]]]] = {}


def flat_sweep(
    sources: Sequence[str],
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
) -> tuple[dict[tuple[str, ...], str], list[dict[str, Any]]]:
    """Every flat model's reading of every source, memoized on the source list.

    Memoized separately from the tiered half because the flat half is the expensive one and it does
    not depend on which tiered conventions are being asked about.
    """
    sources = tuple(sources)
    key = (sources, literal_policy)
    cached = _FLAT_MEMO.get(key)
    if cached is not None:
        return cached
    payloads = [
        (chunk, sources, literal_policy) for chunk in _chunks(flat_conventions(), _sweep_chunks())
    ]
    results = _map_cells(
        _flat_payload, payloads, workers=workers, seconds_per_cell=SWEEP_PAYLOAD_SECONDS
    )
    vectors: dict[tuple[str, ...], str] = {}
    trees: list[dict[str, Any]] = [{} for _ in sources]
    for result in results:
        for vector, identifier in result["vectors"].items():
            vectors.setdefault(vector, identifier)
        _merge_trees(trees, result["trees"])
    _FLAT_MEMO[key] = (vectors, trees)
    return vectors, trees


def sweep(
    conventions: Sequence[Convention] | None = None,
    sources: Sequence[str] | None = None,
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
) -> dict[str, Any]:
    """Parse every corpus source under every model in both spaces, once.

    The flat side runs first because its distinct reading vectors are the set the tiered side is
    tested against, and passing that set into the tiered workers is what keeps the whole comparison
    to one pass over each space instead of one pass per question asked of it.
    """
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    sources = tuple(sources) if sources is not None else CORPUS_SOURCES
    key = (conventions, sources, literal_policy)
    cached = _SWEEP_MEMO.get(key)
    if cached is not None:
        return cached
    flat_vectors, flat_trees = flat_sweep(sources, literal_policy, workers)
    trees: list[dict[str, Any]] = [{} for _ in sources]
    _merge_trees(trees, flat_trees)
    tables = reading_tables(tuple(flat_vectors), len(sources))
    flat_codes = frozenset(_encode(vector, tables) for vector in flat_vectors)
    chunk_count = max(1, _sweep_chunks() // 4)
    tiered_payloads = [
        (chunk, sources, literal_policy, tables, flat_codes)
        for chunk in _chunks(conventions, chunk_count)
    ]
    tiered_results = _map_cells(
        _tiered_payload, tiered_payloads, workers=workers, seconds_per_cell=SWEEP_PAYLOAD_SECONDS
    )
    matched_codes: dict[bytes, str] = {}
    unmatched: dict[tuple[str, ...], tuple[str, str]] = {}
    counts = {"with_twin": 0, "without_twin": 0}
    for kind in CONVENTION_KINDS:
        counts[kind] = 0
        counts[f"{kind}_without_twin"] = 0
    by_kind: dict[str, list[set]] = {kind: [set() for _ in sources] for kind in CONVENTION_KINDS}
    for result in tiered_results:
        for code, identifier in result["matched"].items():
            matched_codes.setdefault(code, identifier)
        for vector, identifier in result["unmatched"].items():
            unmatched.setdefault(vector, identifier)
        for name, value in result["counts"].items():
            counts[name] += value
        for kind, readings in result["by_kind"].items():
            for index, entries in enumerate(readings):
                by_kind[kind][index].update(entries)
        _merge_trees(trees, result["trees"])
    outcome = {
        "conventions": conventions,
        "sources": sources,
        "literal_policy": literal_policy,
        "flat_vectors": flat_vectors,
        "matched_codes": matched_codes,
        "distinct_tiered_vectors": len(matched_codes) + len(unmatched),
        "unmatched": unmatched,
        "counts": counts,
        "trees": trees,
        "readings_by_kind": by_kind,
    }
    _SWEEP_MEMO[key] = outcome
    return outcome


def alias_equals_tie(literal_policy: str = LITERAL_POLICY) -> dict[str, Any]:
    """Is "juxtaposition is an alias for ``*``" a separate axis, or is it the tie placement at ``*``?

    Measured rather than asserted: the alias reading rewrites every juxtaposition site to an
    explicit ``*`` and parses the rewritten string under the base grammar with no juxtaposition
    layer at all; the tie reading parses the original under a convention tying juxtaposition to
    ``*``'s level. If they agree on every source, the alias is not an axis.
    """
    base = CONTROL_BASE
    star_level = next(index for index, level in enumerate(base.levels) if "*" in level)
    tie = Convention(base.id, ("tie", star_level), ("gap", 1), True)
    disagreements: list[dict[str, str]] = []
    for source in CORPUS_SOURCES:
        rewritten = _rewrite_juxtaposition(source, literal_policy)
        try:
            aliased = str(parse_tiered(rewritten, tie, literal_policy))
        except ValueError as error:
            aliased = f"REJECTED: {error}"
        try:
            tied = str(parse_tiered(source, tie, literal_policy))
        except ValueError as error:
            tied = f"REJECTED: {error}"
        if aliased != tied:
            disagreements.append({"source": source, "alias": aliased, "tie": tied})
    return {
        "sources": len(CORPUS_SOURCES),
        "star_level": star_level,
        "tie_placement": ("tie", star_level),
        "disagreements": len(disagreements),
        "disagreeing": tuple(disagreements),
        "alias_is_the_tie": not disagreements,
    }


def _rewrite_juxtaposition(source: str, literal_policy: str = LITERAL_POLICY) -> str:
    tokens = tokenize_tiered(source, literal_policy)
    pieces: list[str] = []
    previous: Token3 | None = None
    for token in tokens:
        if token.kind == "eof":
            break
        if previous is not None and previous.kind in ("number", "name", "right") and starts_primary(token):
            pieces.append("*")
        pieces.append("(" if token.kind == "left" else ")" if token.kind == "right" else token.value)
        previous = token
    return " ".join(pieces)


# -------------------------------------------------------------------------------- THE HEADLINE


def flat_equivalence(
    conventions: Sequence[Convention] | None = None,
    sources: Sequence[str] | None = None,
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
    separators: bool = True,
) -> dict[str, Any]:
    """Can a flat precedence do it? The test of T26, and the card.

    For every tiered convention, is there ANY flat model - any weak order on the seven roles, under
    either prefix rule - that produces the same reading on every corpus source? The search over
    flat models is exhaustive, so a "cannot" is a statement about all ``94586`` of them and not
    about the ones that were tried.

    For each convention that cannot, the shortest source that separates it is reported: sources are
    walked shortest-first, the surviving flat models are narrowed at each one, and the separator is
    the source at which the last survivor dies.
    """
    outcome = sweep(conventions, sources, literal_policy, workers)
    conventions = outcome["conventions"]
    sources = outcome["sources"]
    flat = outcome["flat_vectors"]
    counts = outcome["counts"]
    flat_vectors = tuple(flat)
    matched = outcome["matched_codes"]
    unmatched = list(outcome["unmatched"])
    found: dict[str, dict[str, Any]] = {}
    shortest: dict[str, dict[str, Any]] = {}
    shortest_tree: dict[str, dict[str, Any]] = {}
    rejection_counts: dict[str, int] = {kind: 0 for kind in CONVENTION_KINDS}
    tree_counts: dict[str, int] = {kind: 0 for kind in CONVENTION_KINDS}
    for vector in unmatched if separators else ():
        identifier, kind = outcome["unmatched"][vector]
        record = _separating_source(vector, flat_vectors, sources)
        record["kind"] = kind
        found[identifier] = record
        by_rejection = record["tiered_reading"] == REJECTED
        rejection_counts[kind] += by_rejection
        tree_counts[kind] += not by_rejection
        for target in (shortest, shortest_tree) if not by_rejection else (shortest,):
            best = target.get(kind)
            if best is None or (len(record["source"] or ""), record["source"] or "") < (
                len(best["source"] or ""),
                best["source"] or "",
            ):
                target[kind] = dict(record, convention=identifier)
    return {
        "conventions_swept": len(conventions),
        "convention_space_size": CONVENTION_SPACE_SIZE,
        "unswept_conventions": CONVENTION_SPACE_SIZE - len(conventions),
        "sources": len(sources),
        "flat_models": len(flat_conventions()),
        "distinct_tiered_vectors": outcome["distinct_tiered_vectors"],
        "distinct_flat_vectors": len(flat),
        "tiered_vectors_with_flat_twin": len(matched),
        "tiered_vectors_without_flat_twin": len(unmatched),
        "conventions_with_flat_twin": counts["with_twin"],
        "conventions_without_flat_twin": counts["without_twin"],
        "by_kind": {
            kind: {
                "conventions": counts[kind],
                "without_flat_twin": counts[f"{kind}_without_twin"],
                "separated_by_rejection": rejection_counts[kind],
                "separated_by_tree": tree_counts[kind],
                "shortest_separator": shortest.get(kind),
                "shortest_tree_separator": shortest_tree.get(kind),
            }
            for kind in CONVENTION_KINDS
        },
        "separators": found,
        "separating_sources": tuple(
            sorted({record["source"] for record in found.values() if record["source"]})
        ),
    }


def _separating_source(
    vector: tuple[str, ...],
    flat_vectors: Sequence[tuple[str, ...]],
    sources: Sequence[str],
) -> dict[str, Any]:
    survivors = list(range(len(flat_vectors)))
    for index, source in enumerate(sources):
        survivors = [item for item in survivors if flat_vectors[item][index] == vector[index]]
        if not survivors:
            return {
                "source": source,
                "position": index + 1,
                "tiered_reading": vector[index],
                "roles": role_support(source),
            }
    return {"source": None, "position": None, "tiered_reading": None, "roles": ()}


# ------------------------------------------------------------------------------ ambiguity atlas


@dataclass(frozen=True)
class NamedAmbiguity:
    """One place where real mathematics disagrees with itself, and the readings in print."""

    source: str
    question: str
    readings: tuple[tuple[str, str], ...]


#: The ambiguities the card names, plus the two that travel with them. ``published`` strings say
#: which practice a reading belongs to and are attributions, not measurements; the trees and the
#: objects beside them are measured.
NAMED_AMBIGUITIES: tuple[NamedAmbiguity, ...] = (
    NamedAmbiguity(
        "-x^2",
        "is it -(x^2) or (-x)^2 ?",
        (
            ("-x**2", "the mathematical convention: the exponent binds before the sign"),
            ("x**2", "the spreadsheet convention: unary minus binds before the exponent"),
        ),
    ),
    NamedAmbiguity(
        "-2^2",
        "is it -4 or 4 ?",
        (
            ("-4", "the mathematical convention"),
            ("4", "the spreadsheet convention"),
        ),
    ),
    NamedAmbiguity(
        "1/2x",
        "is it (1/2)*x or 1/(2*x) ?",
        (
            ("x/2", "strict left-to-right: implicit multiplication ranks with explicit"),
            ("1/(2*x)", "printed mathematics and physics: juxtaposition binds tighter than the solidus"),
        ),
    ),
    NamedAmbiguity(
        "6/2(1 + 2)",
        "is it 9 or 1 ?",
        (
            ("9", "strict left-to-right"),
            ("1", "juxtaposition binds tighter than the solidus"),
        ),
    ),
    NamedAmbiguity(
        "2x^2",
        "does juxtaposition bind tighter than ^, or looser ?",
        (
            ("2*x**2", "universal reading: the exponent binds first"),
            ("4*x**2", "juxtaposition tighter than the exponent - no published practice"),
        ),
    ),
    NamedAmbiguity(
        "x^2y",
        "is the exponent 2 or 2y ?",
        (
            ("x**2*y", "the exponent is the single token that follows"),
            ("x**(2*y)", "the exponent is the whole juxtaposed group"),
        ),
    ),
)


def ambiguity_atlas(
    conventions: Sequence[Convention] | None = None,
    literal_policy: str = LITERAL_POLICY,
) -> dict[str, Any]:
    """For each named ambiguity: what each convention reads, what the object is, whose reading it is.

    The readings are grouped by object, not by tree, because two trees that denote the same object
    are not a disagreement about mathematics - and separating those two cases is what the null
    model then does at corpus scale.
    """
    conventions = tuple(conventions) if conventions is not None else conventions_over(CONTROL_BASE)
    rows: list[dict[str, Any]] = []
    for ambiguity in NAMED_AMBIGUITIES:
        readings: dict[str, dict[str, Any]] = {}
        rejected = 0
        for convention in conventions:
            try:
                tree = parse_tiered(ambiguity.source, convention, literal_policy)
            except ValueError:
                rejected += 1
                continue
            key = cached_object_key(tree)
            record = readings.setdefault(
                key[0],
                {"object": key[0], "excluded_points": key[2], "conventions": 0, "trees": set(),
                 "example": convention.id},
            )
            record["conventions"] += 1
            record["trees"].add(str(tree))
        published = {reading: note for reading, note in ambiguity.readings}
        rows.append(
            {
                "source": ambiguity.source,
                "question": ambiguity.question,
                "roles": role_support(ambiguity.source, literal_policy),
                "rejected_by": rejected,
                "objects": tuple(
                    {
                        "object": record["object"],
                        "conventions": record["conventions"],
                        "distinct_trees": len(record["trees"]),
                        "example_convention": record["example"],
                        "published_reading": published.get(record["object"], "not a published reading"),
                    }
                    for record in sorted(readings.values(), key=lambda item: -item["conventions"])
                ),
                "published_readings_reached": tuple(
                    reading for reading in published if reading in readings
                ),
                "published_readings_missing": tuple(
                    reading for reading in published if reading not in readings
                ),
            }
        )
    return {"conventions": len(conventions), "literal_policy": literal_policy, "rows": tuple(rows)}


# --------------------------------------------------------------------------------- the null model


def null_model(
    conventions: Sequence[Convention] | None = None,
    sources: Sequence[str] | None = None,
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
) -> dict[str, Any]:
    """How many distinct mathematical OBJECTS does the tiered space reach that the flat space does not?

    This is the question that decides whether the card found anything, and it is asked the way 0030
    asked it of associativity: more syntax is only a result if it reaches mathematics the smaller
    space could not. Objects are the project's semantic key, whose domain component is inert
    (NF-2026-00005), so the operative identity is ``(canonical form, excluded points)``.

    Everything is stratified by role support, because a source using ``j`` of the seven roles
    cannot distinguish models that agree on those ``j`` and would otherwise inflate every count.
    """
    outcome = sweep(conventions, sources, literal_policy, workers)
    conventions = outcome["conventions"]
    sources = outcome["sources"]
    flat = outcome["flat_vectors"]
    rows: list[dict[str, Any]] = []
    tiered_only_total: set[tuple[str, Any]] = set()
    flat_only_total: set[tuple[str, Any]] = set()
    kind_excess = {kind: set() for kind in CONVENTION_KINDS}
    for index, source in enumerate(sources):
        table = outcome["trees"][index]
        support = role_support(source, literal_policy)
        tiered_trees = set()
        for kind in CONVENTION_KINDS:
            tiered_trees |= outcome["readings_by_kind"][kind][index]
        tiered_trees -= {REJECTED}
        flat_trees = {vector[index] for vector in flat} - {REJECTED}
        tiered_objects = {cached_object_key(table[text]) for text in tiered_trees}
        flat_objects = {cached_object_key(table[text]) for text in flat_trees}
        excess = tiered_objects - flat_objects
        deficit = flat_objects - tiered_objects
        for item in excess:
            tiered_only_total.add((source, item))
        for item in deficit:
            flat_only_total.add((source, item))
        per_kind: dict[str, dict[str, int]] = {}
        for kind in CONVENTION_KINDS:
            readings = outcome["readings_by_kind"][kind][index] - {REJECTED}
            objects = {cached_object_key(table[text]) for text in readings}
            new_here = objects - flat_objects
            for item in new_here:
                kind_excess[kind].add((source, item))
            per_kind[kind] = {"objects": len(objects), "objects_only_tiered": len(new_here)}
        rows.append(
            {
                "source": source,
                "roles": support,
                "role_count": len(support),
                "tiered_trees": len(tiered_trees),
                "flat_trees": len(flat_trees),
                "tiered_objects": len(tiered_objects),
                "flat_objects": len(flat_objects),
                "objects_only_tiered": len(excess),
                "objects_only_flat": len(deficit),
                "objects_only_tiered_list": tuple(sorted(item[0] for item in excess)),
                "objects_only_flat_list": tuple(sorted(item[0] for item in deficit)),
                "by_kind": per_kind,
            }
        )
    by_support: dict[int, dict[str, int]] = {}
    for row in rows:
        bucket = by_support.setdefault(
            row["role_count"],
            {"sources": 0, "tiered_objects": 0, "flat_objects": 0, "excess": 0, "deficit": 0},
        )
        bucket["sources"] += 1
        bucket["tiered_objects"] += row["tiered_objects"]
        bucket["flat_objects"] += row["flat_objects"]
        bucket["excess"] += row["objects_only_tiered"]
        bucket["deficit"] += row["objects_only_flat"]
    return {
        "conventions": len(conventions),
        "flat_models": len(flat_conventions()),
        "sources": len(sources),
        "rows": tuple(rows),
        "objects_only_tiered": len(tiered_only_total),
        "objects_only_flat": len(flat_only_total),
        "sources_with_excess": sum(1 for row in rows if row["objects_only_tiered"]),
        "sources_with_deficit": sum(1 for row in rows if row["objects_only_flat"]),
        "total_tiered_objects": sum(row["tiered_objects"] for row in rows),
        "total_flat_objects": sum(row["flat_objects"] for row in rows),
        "excess_by_kind": {kind: len(items) for kind, items in kind_excess.items()},
        "stratified_by_role_support": {
            support: dict(bucket) for support, bucket in sorted(by_support.items())
        },
    }


_OBJECT_MEMO: dict[str, tuple[str, str, tuple[str, ...]]] = {}


def cached_object_key(tree: Any) -> tuple[str, str, tuple[str, ...]]:
    """:func:`object_key` memoized on the tree's spelling.

    Distinct conventions overwhelmingly produce the same few trees per source, and a SymPy
    ``simplify`` per convention rather than per tree would dominate every run here without
    changing a single number.
    """
    text = str(tree)
    cached = _OBJECT_MEMO.get(text)
    if cached is None:
        cached = object_key(tree)
        _OBJECT_MEMO[text] = cached
    return cached


# --------------------------------------------------------------------------------- render audits


def _render_payload(
    payload: tuple[tuple[Any, ...], tuple[Convention, ...], str]
) -> dict[str, Any]:
    trees, conventions, literal_policy = payload
    cells = 0
    failures: list[str] = []
    refuted = 0
    checked = 0
    pairs = 0
    for tree in trees:
        for convention in conventions:
            cells += 1
            try:
                witness = minimality_witness(tree, convention, literal_policy)
            except RoundTripError as error:
                failures.append(str(error))
                continue
            refuted += witness["cheaper_writings_refuted"]
            checked += witness["writings_checked"]
            pairs += witness["pairs"]
    return {"cells": cells, "failures": failures, "cheaper_writings_refuted": refuted,
            "writings_checked": checked, "pairs": pairs}


def render_audit(
    conventions: Sequence[Convention] | None = None,
    corpus: Sequence[Formula3] | None = None,
    literal_policy: str = LITERAL_POLICY,
    workers: int | None = None,
) -> dict[str, Any]:
    """Round trip and minimality over the whole grid, both by exhaustive search.

    Round trip is not a separate pass: :func:`minimality_witness` returns a writing only when that
    writing reparses to the tree, so a cell that produces a rendering has round-tripped, and a cell
    that cannot raises. Minimality is the same search, one bracket count lower.
    """
    conventions = tuple(conventions) if conventions is not None else conventions_over(CONTROL_BASE)
    corpus = tuple(corpus) if corpus is not None else CORPUS_3
    trees = tuple(formula_tree(formula) for formula in corpus)
    payloads = [
        (trees, chunk, literal_policy) for chunk in _chunks(conventions, _sweep_chunks())
    ]
    # the declared per-payload cost is for the FULL grid; a smaller grid must not inherit it, or a
    # check that takes six seconds sequentially would pay a pool it does not need
    scale = (len(trees) * len(conventions)) / (len(CORPUS_3) * len(conventions_over(CONTROL_BASE)))
    results = _map_cells(
        _render_payload, payloads, workers=workers,
        seconds_per_cell=RENDER_PAYLOAD_SECONDS * max(scale, 0.0),
    )
    failures = [item for result in results for item in result["failures"]]
    return {
        "trees": len(trees),
        "conventions": len(conventions),
        "cells": sum(result["cells"] for result in results),
        "round_trip_failures": len(failures),
        "failing": tuple(failures[:10]),
        "writings_checked": sum(result["writings_checked"] for result in results),
        "cheaper_writings_refuted": sum(result["cheaper_writings_refuted"] for result in results),
        "bracket_pairs": sum(result["pairs"] for result in results),
        "minimal": not failures,
    }


def literal_policy_sensitivity(
    conventions: Sequence[Convention] | None = None,
) -> dict[str, Any]:
    """What the composite-literal rule decides, reported beside the number it moves.

    ``1/2x`` is the named ambiguity that the tokenizer, not the grammar, can settle. Under the
    ``gen1`` rule the string has ONE reading in every convention in the space, and the published
    disagreement is invisible; under the default it has two. The conservative-extension verdict is
    reported for each rule in the same table, because the rule that makes the ambiguity visible has
    to keep the extension conservative or it is not available.
    """
    conventions = tuple(conventions) if conventions is not None else conventions_over(CONTROL_BASE)
    rows: list[dict[str, Any]] = []
    for policy in LITERAL_POLICIES:
        readings: dict[str, int] = {}
        for convention in conventions:
            try:
                tree = parse_tiered("1/2x", convention, policy)
            except ValueError:
                continue
            readings[cached_object_key(tree)[0]] = readings.get(cached_object_key(tree)[0], 0) + 1
        audit = agreement_audit(
            grammars=all_grammars()[:1], literal_policy=policy, workers=1
        )
        rows.append(
            {
                "literal_policy": policy,
                "readings_of_half_x": len(readings),
                "objects": tuple(sorted(readings)),
                "conservative_over_generation_one": audit["conservative"],
                "audit_cells": audit["cells"],
                "audit_disagreements": audit["disagreements"],
            }
        )
    return {"conventions": len(conventions), "default": LITERAL_POLICY, "rows": tuple(rows)}


def render_extension_check(workers: int | None = None) -> dict[str, Any]:
    """What was checked beyond the render grid's bound.

    :func:`render_audit` runs over the conventional base's whole slot space because the full space
    would be `1.5` million cells of exhaustive search. That bound exists so the run terminates, so
    it is disclosed rather than reported as a finding, and this is what lies beyond it: the same
    round trip and the same exhaustive minimality over the split-free conventions of the two other
    fully swept bases.
    """
    conventions = tuple(
        convention
        for base_id in FULL_SWEEP_BASE_IDS[1:]
        for convention in conventions_over(_BASES[base_id], splits=False)
    )
    return render_audit(conventions=conventions, workers=workers)


# ------------------------------------------------------------------------- what is not enumerated


def restricted_juxtaposition_check(literal_policy: str = LITERAL_POLICY) -> dict[str, Any]:
    """One writing the convention space does NOT produce, checked rather than waved away.

    The space treats every adjacency as a juxtaposition site. Real notation does not: ``2x`` is
    written and ``x y`` is not. A convention that admitted juxtaposition only after a numeral is
    not a tier placement at all, so it is outside the space by construction - and the question the
    report has to answer is whether it would change the answer. It is checked here by parsing every
    corpus source with the sites the restriction would forbid removed, and asking whether any
    reading appears that the full space does not already reach.
    """
    restricted = tuple(_forbid_name_name(source, literal_policy) for source in CORPUS_SOURCES)
    changed = sum(1 for before, after in zip(CORPUS_SOURCES, restricted) if before != after)
    ordered = tuple(sorted(set(restricted), key=lambda text: (len(text), text)))
    headline = flat_equivalence(
        conventions=conventions_over(CONTROL_BASE),
        sources=ordered,
        literal_policy=literal_policy,
        separators=False,
    )
    reference = flat_equivalence(
        conventions=conventions_over(CONTROL_BASE), literal_policy=literal_policy, separators=False
    )
    verdict_moves = {
        kind: {
            "unrestricted": reference["by_kind"][kind]["without_flat_twin"],
            "restricted": headline["by_kind"][kind]["without_flat_twin"],
        }
        for kind in CONVENTION_KINDS
    }
    return {
        "sources_rewritten": changed,
        "restricted_sources": len(ordered),
        "linear_without_flat_twin": headline["by_kind"]["linear"]["without_flat_twin"],
        "verdict_by_kind": verdict_moves,
        "verdict_shape_unchanged": all(
            (moves["unrestricted"] == 0) == (moves["restricted"] == 0)
            for moves in verdict_moves.values()
        ),
    }


def _forbid_name_name(source: str, literal_policy: str = LITERAL_POLICY) -> str:
    """Rewrite a source so no juxtaposition stands between two NAMES, using explicit ``*`` instead.

    That adjacency is the one real notation never writes in linear text - ``xy`` would be one
    identifier - so a convention forbidding it is a plausible one, and it is not a tier placement,
    which is why the declared space does not contain it. Rewriting the corpus is how the check is
    run without a second parser: under such a convention ``x y`` simply has to be written ``x * y``.
    """
    tokens = tokenize_tiered(source, literal_policy)
    pieces: list[str] = []
    previous: Token3 | None = None
    for token in tokens:
        if token.kind == "eof":
            break
        if previous is not None and previous.kind == "name" and token.kind == "name":
            pieces.append("*")
        pieces.append("(" if token.kind == "left" else ")" if token.kind == "right" else token.value)
        previous = token
    return " ".join(pieces)


# --------------------------------------------------------------- the observed routing decision


def parallel_decision(repeats: int = 3, workers: int | None = None) -> dict[str, Any]:
    """The multicore decision, taken from measurements on this host rather than from a rule."""
    startup = measure_pool_startup(workers=workers, repeats=repeats)
    cells = measure_cell_seconds()
    audit_payloads = sum(len(grammar.levels) + 1 for grammar in all_grammars())
    sweep_payloads = _sweep_chunks()
    # an explicit worker count has to reach the DECISION and not only the startup timing, or the
    # two halves of this record would describe different machines
    resolved = default_worker_count(audit_payloads) if workers is None else max(1, int(workers))
    return {
        "cores": os.cpu_count(),
        "workers": resolved,
        "pool_startup_seconds": startup["seconds"],
        "audit_payloads": audit_payloads,
        "audit_payload_seconds": cells["audit_payload_seconds"],
        "audit_sequential_seconds": audit_payloads * cells["audit_payload_seconds"],
        "audit_parallel": should_parallelise(audit_payloads, cells["audit_payload_seconds"], resolved),
        "sweep_payloads": sweep_payloads,
        "sweep_payload_seconds": cells["sweep_payload_seconds"],
        "sweep_sequential_seconds": sweep_payloads * cells["sweep_payload_seconds"],
        "sweep_parallel": should_parallelise(sweep_payloads, cells["sweep_payload_seconds"], resolved),
        "render_payload_seconds": cells["render_payload_seconds"],
        "render_sequential_seconds": sweep_payloads * cells["render_payload_seconds"],
        "render_parallel": should_parallelise(sweep_payloads, cells["render_payload_seconds"], resolved),
    }


def tiered_syntax_report(workers: int | None = None) -> dict[str, Any]:
    """Every number this experiment publishes, in the order the report reads them."""
    audit = agreement_audit(workers=workers)
    headline = flat_equivalence(workers=workers)
    return {
        "agreement": audit,
        "alias": alias_equals_tie(),
        "translation": layered_translation_audit(),
        "headline": headline,
        "render": render_audit(workers=workers),
        "render_extension": render_extension_check(workers=workers),
        "atlas": ambiguity_atlas(),
        "null_model": null_model(workers=workers),
        "literal_policy": literal_policy_sensitivity(),
        "restricted_juxtaposition": restricted_juxtaposition_check(),
        "convention_space_size": CONVENTION_SPACE_SIZE,
        "conventions_swept": len(CONVENTIONS),
        "flat_models": len(flat_conventions()),
        "corpus": len(CORPUS_3),
        "sources": len(CORPUS_SOURCES),
    }
