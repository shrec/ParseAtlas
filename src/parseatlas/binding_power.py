"""Binding power as a vector: the 2D and 3D generalisations of precedence (experiment 0052).

``parseatlas.grammar.Grammar.binding_power`` returns ``dict[str, int]`` -- one
integer per operator.  That single integer is the flatness of Generation 1:
every result in the repository, all 25 worlds, is a slice of a richer space
through the plane where that number is scalar.

The generalisation is the one Pratt parsing already uses::

    1D    binding_power[op] = n                 the Generation 1 model
    2D    binding_power[op] = (left, right)     precedence and associativity, unified
    3D    plus a prefix binding power           unary operators integrated

Nothing here modifies :mod:`parseatlas.grammar` or :mod:`parseatlas.parser`.
The vector-parametrised parser is built alongside them, and
:func:`agreement_audit` proves it a conservative extension: each of the 25
Generation 1 grammars has an explicit 2D image whose parse equals
``parseatlas.parser.parse`` cell by cell.

Four facts carry the module and each is established rather than assumed.

**Fact 1 (the 2D image of a 1D grammar).**  The Generation 1 parser loops on
``power >= minimum`` and recurses at ``power + 1``; the 2D parser loops on
``left > minimum`` and recurses at ``right``.  Substituting ``left = 2p`` and
``right = 2p + 1`` turns the first into the second exactly, because
``p >= m`` is ``2p > 2m - 1``.  So :func:`from_grammar` is not a fit, it is a
change of variables, and the audit is the check that no arithmetic slipped.

**Fact 2 (associativity is the order within the pair).**  ``a - b - c`` parses
left when ``left(-) <= right(-)`` and right when ``left(-) > right(-)``: after
consuming an operator the parser continues with a minimum taken from the right
component, so the equal-power operator is left for the loop or swallowed by the
recursion according to that single comparison.  Associativity is therefore a
*derived* parameter of the 2D model, exactly as experiment 0030's registry
suggested but did not state.

**Fact 3 (behaviour is a boolean matrix).**  The recursion is entered only with
``0`` (top level and after ``(``) or with ``right(o)`` for some operator ``o``.
With every ``left`` at least ``1`` the top-level test is always true, so the
whole parser is decided by the matrix ``M[a][b] = left(a) > right(b)``.  Every
cell of that matrix is observed by the two-operator word ``x b y a z``, so
*distinct matrix* and *distinct parser* are the same thing and the behavioural
quotient is exact rather than a sampling.

**Fact 4 (the enumeration bound saturates).**  ``M`` is realisable exactly when
the sets ``S(a) = {b : left(a) > right(b)}`` form a chain under inclusion, and a
chain of ``m`` subsets of an ``m``-set is realised by ``left`` values in
``2..m+1`` and ``right`` values in ``1..m+1``.  So ``bound = m + 1`` reaches
every parser there is, and any larger bound adds assignments without adding
behaviour.  :func:`saturation_scan` observes this rather than asserting it.

The counts these facts produce, for reference, are pinned by the tests::

    operators m          1       2       3       4
    parsers, 2D          2      14     230    6902
    parsers, 3D          4      46    1066   41506

The module also carries the **other** non-flat direction, which is not a vector
at all.  :class:`PartialOrderGrammar` ranks the operators by a preorder in which
some pairs may be *incomparable*, and refuses a source whose reading would turn
on a missing comparison instead of choosing one; :func:`partial_orders` prices
that refusal against the brackets it costs.  :func:`null_model` asks the only
question that decides whether any of this found anything: how many distinct
*mathematical objects*, not syntax trees, the second component reaches that the
``precedence x associativity`` registry does not.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import product
from typing import Any

from .associativity import (
    LEFT,
    RIGHT,
    SIDES,
    AssociativeGrammar,
    associative_tree,
    associativity_space,
    control_associativity_space,
)
from .canonical import canonicalize
from .grammar import OPERATORS, Grammar, all_grammars, control_grammar, strict_grammars
from .parser import Binary, Node, Parser, parse
from .reachability import (
    Tree,
    canonical_leaves,
    canonical_tree,
    catalan_trees,
    flat_source,
    grammar_binding_power,
    resolve_workers,
)
from .tokenizer import Token, tokenize

# --------------------------------------------------------------------------
# Corpora
# --------------------------------------------------------------------------

#: Experiment 0020's six expressions, reused unchanged so the coverage tables
#: of 0020, 0030 and this experiment stand in the same column.
COVERAGE_CORPUS: tuple[str, ...] = (
    "a + b*c",
    "a + b + c",
    "2*t + 1 - t/2",
    "a + b*c - d/e",
    "a - b*c + d/e - f",
    "2*x*x + 1 - x/2 + x",
)

#: Experiment 0030's split-rule corpus, which carries hand-written parentheses.
SPLIT_CORPUS: tuple[str, ...] = (
    "2*t + 1 - t/2",
    "a - b*c + d/e - f",
    "a/b + c*d - e/f + g",
    "a - b - c",
    "(x + 1)/(x - 2)",
)

#: Experiment 0030's chain probe: repeated non-associative operators, the one
#: corpus family where associativity was observed to add semantic classes.
CHAIN_CORPUS: tuple[str, ...] = (
    "a - b - c",
    "a - b - c - d",
    "a / b / c",
    "a / b / c / d",
    "a - b + c - d",
    "a * b / c / d",
    "2*x - 1 - x",
    "a - b*c - d",
    "a/b - c/d - e",
    "x - 1 - x - 1",
)

#: Experiment 0024's restriction probe, the corpus built so the ``excluded
#: points`` half of the class key is load-bearing.  Held as literals rather than
#: regenerated so this module does not import the 3125-expression generator; the
#: tests assert the two agree.
PROBE_CORPUS: tuple[str, ...] = (
    "1 - x / x - 1",
    "2 - x / x - 2",
    "x - y / y - x",
    "x / 1 - x - 1",
    "x - 1 / 1 - x",
    "x - 2 / 2 - x",
    "x / x - 1 - x",
    "x / x - x + 1",
    "x / x",
    "(x * x - 1) / (x - 1)",
)

#: Experiment 0017's five expressions.
TEMPLATE_CORPUS: tuple[str, ...] = (
    "2*t + 1 - t/2",
    "3*x + 2 - x/3",
    "2*x*x + 1 - x/2",
    "(x + 1)/(x - 2)",
    "(x*x - 1)/(x - 1)",
)

#: The audit corpus: every source above plus deeper nesting, fractions and
#: numeric leaves, so the conservative-extension claim is not tested only on
#: flat words.
AUDIT_CORPUS: tuple[str, ...] = tuple(
    dict.fromkeys(
        COVERAGE_CORPUS
        + SPLIT_CORPUS
        + CHAIN_CORPUS
        + TEMPLATE_CORPUS
        + (
            "a",
            "7",
            "1/2",
            "a + b",
            "a - b",
            "a * b",
            "a / b",
            "(a + b) * (c - d)",
            "((a + b) * c) / d",
            "a * (b + c) / (d - e)",
            "1/2 * x + 3/4 - x/5",
            "a + b - c * d / e + f - g",
            "(a - (b - (c - d)))",
            "a/(b/(c/d))",
            "2 * (x + 1) * (x - 1) - x*x",
        )
    )
)


class AmbiguousParse(ValueError):
    """A partial-order grammar refused a source instead of choosing a reading."""


# --------------------------------------------------------------------------
# Multicore
# --------------------------------------------------------------------------

#: Below this many independent tasks the automatic worker choice stays sequential.
#:
#: Observations on this 16-core Windows host.  Three repetitions per
#: configuration, each repetition in a **fresh interpreter** so both columns pay
#: the cold sympy import chain that ``parseatlas`` pulls in; medians below,
#: ``workers=15`` being ``cpu_count - 1``.
#:
#:   reach_2d, tasks = operator-word patterns
#:      k <= 5     73 tasks   sequential   4.01 s   parallel   6.95 s   0.58x
#:      k <= 6    260 tasks   sequential  24.74 s   parallel   8.73 s   2.83x
#:
#:   enumerate_2d, tasks = left vectors
#:      bound 4   256 tasks   sequential  11.27 s   parallel   4.91 s   2.30x
#:      bound 5   625 tasks   sequential  62.25 s   parallel  20.35 s   3.06x
#:
#:   null_model, tasks = sources
#:                 31 tasks   sequential   9.36 s   parallel   9.57 s   0.98x
#:
#: The crossover for those three sits between 73 and 256 tasks, so the constant
#: is put at 128 -- the same place :data:`parseatlas.associativity.PARALLEL_MINIMUM_ITEMS`
#: sits, observed independently on the same host.  Two workloads here are priced
#: differently per task and say so at their own call site through ``minimum``:
#: :func:`three_d`, where one task is 41506 parses, and :func:`partial_orders`,
#: where one task is about 4 ms.  An explicit ``workers=N`` overrides all of it,
#: so the parallel branch stays reachable at any size.
PARALLEL_MINIMUM_TASKS: int = 128

#: :func:`three_d` threshold, in tasks.  One task parses a source under all
#: 41506 three-component parsers, so the fixed cost of a spawned worker is paid
#: back far earlier than the general constant assumes:
#:
#:      k <= 3     20 tasks   sequential  38.83 s   parallel  57.06 s   0.68x
#:      k <= 4     71 tasks   sequential  78.10 s   parallel  35.94 s   2.17x
#:
#: The crossover is therefore between 20 and 71 tasks and the constant is put at
#: 32, which keeps ``k <= 3`` sequential and ``k <= 4`` parallel.
THREE_D_MINIMUM_TASKS: int = 32


def resolve_task_workers(
    task_count: int, workers: int | None = None, minimum: int | None = PARALLEL_MINIMUM_TASKS
) -> int:
    """Worker count from the observed core count, with an observed floor.

    ``minimum`` is the call site's own threshold in its own unit, and
    ``minimum=None`` means *never parallel by default*.  Neither is a guess: the
    call site that departs from :data:`PARALLEL_MINIMUM_TASKS` carries the
    timings that make it depart.
    """
    if workers is None and (minimum is None or task_count < minimum):
        return 1
    return resolve_workers(task_count, workers)


# --------------------------------------------------------------------------
# The vector-parametrised grammar and parser
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class VectorGrammar:
    """A binding-power *vector* per operator.

    ``powers`` holds ``(operator, left, right)`` triples and ``prefix`` holds
    ``(operator, power)`` pairs for the operators usable in prefix position.
    Both are sorted tuples so the dataclass stays hashable and two grammars
    written in a different order compare equal.

    ``left`` must be at least ``1``: the parser enters its loop with minimum
    ``0`` at top level and after ``(``, and a ``left`` of ``0`` would make an
    operator unconsumable there, turning a grammar into a partial function on
    sources.  That is a different object -- see :class:`PartialOrderGrammar` --
    and is kept out of the vector space deliberately.
    """

    id: str
    powers: tuple[tuple[str, int, int], ...]
    prefix: tuple[tuple[str, int], ...] = ()

    def __post_init__(self) -> None:
        operators = [operator for operator, _, _ in self.powers]
        if len(set(operators)) != len(operators):
            raise ValueError("an operator is given a binding power twice")
        if not operators:
            raise ValueError("a vector grammar needs at least one operator")
        for operator, left, right in self.powers:
            if left < 1:
                raise ValueError(f"left binding power of {operator!r} must be at least 1; got {left}")
            if right < 0:
                raise ValueError(f"right binding power of {operator!r} must be at least 0; got {right}")
        known = set(operators)
        for operator, power in self.prefix:
            if operator not in known:
                raise ValueError(f"prefix power for unranked operator {operator!r}")
            if power < 0:
                raise ValueError(f"prefix power of {operator!r} must be at least 0; got {power}")
        prefixed = [operator for operator, _ in self.prefix]
        if len(set(prefixed)) != len(prefixed):
            raise ValueError("an operator is given a prefix power twice")
        object.__setattr__(self, "powers", tuple(sorted(self.powers)))
        object.__setattr__(self, "prefix", tuple(sorted(self.prefix)))

    @property
    def operators(self) -> tuple[str, ...]:
        return tuple(operator for operator, _, _ in self.powers)

    @property
    def left(self) -> dict[str, int]:
        return {operator: left for operator, left, _ in self.powers}

    @property
    def right(self) -> dict[str, int]:
        return {operator: right for operator, _, right in self.powers}

    @property
    def prefix_power(self) -> dict[str, int]:
        return dict(self.prefix)

    @property
    def dimension(self) -> int:
        """``2`` for a binary-only vector grammar, ``3`` once a prefix power is carried."""
        return 3 if self.prefix else 2

    @property
    def sides(self) -> dict[str, str]:
        """The associativity each operator *derives* from the order within its pair.

        This is Fact 2 read off the numbers, not a stored parameter.
        """
        return {
            operator: RIGHT if left > right else LEFT for operator, left, right in self.powers
        }

    def comparison_matrix(
        self, operators: Sequence[str] | None = None
    ) -> tuple[tuple[bool, ...], ...]:
        """``M[a][b] = left(a) > right(b)``, the whole behaviour of the binary part."""
        names = tuple(operators) if operators is not None else self.operators
        left = self.left
        right = self.right
        return tuple(tuple(left[a] > right[b] for b in names) for a in names)

    def prefix_vector(self, operators: Sequence[str] | None = None) -> tuple[bool, ...]:
        """``left(a) > prefix(o)`` for the single prefix operator, or ``()``."""
        if not self.prefix:
            return ()
        names = tuple(operators) if operators is not None else self.operators
        left = self.left
        power = min(power for _, power in self.prefix)
        return tuple(left[a] > power for a in names)


@dataclass(frozen=True)
class Unary:
    """A prefix application.  Only the 3D parser ever builds one."""

    operator: str
    operand: Any


class VectorParser(Parser):
    """Pratt parsing on binding-power vectors.

    Only ``_expression`` and ``_primary`` change relative to
    :class:`parseatlas.parser.Parser`.  ``_expression`` loops on
    ``left(op) > minimum`` and recurses at ``right(op)`` -- the textbook Pratt
    loop -- and ``_primary`` gains the prefix case, delegating to the inherited
    number / variable / parenthesis handling for everything else.

    ``Parser.__init__`` is not called because it takes a
    :class:`parseatlas.grammar.Grammar`; the attributes it would set are set
    here from the vector grammar instead.
    """

    def __init__(self, tokens: tuple[Token, ...], grammar: VectorGrammar) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.index = 0
        self._left = grammar.left
        self._right = grammar.right
        self._prefix = grammar.prefix_power

    def _expression(self, minimum_power: int) -> Node:
        left = self._primary()
        while (
            self._current.kind == "operator"
            and self._left[self._current.value] > minimum_power
        ):
            operator = self._advance().value
            left = Binary(operator, left, self._expression(self._right[operator]))
        return left

    def _primary(self) -> Node:
        token = self._current
        if token.kind == "operator" and token.value in self._prefix:
            self._advance()
            return Unary(token.value, self._expression(self._prefix[token.value]))
        return super()._primary()


def vector_parse(source: str, grammar: VectorGrammar) -> Node:
    """Parse ``source`` under a binding-power vector grammar."""
    return VectorParser(tokenize(source), grammar).parse()


def vector_tree(source: str, grammar: VectorGrammar) -> Tree:
    """Canonical hashable tree form of :func:`vector_parse`."""
    return vector_canonical_tree(vector_parse(source, grammar))


def vector_canonical_tree(node: Any) -> Tree:
    """:func:`parseatlas.reachability.canonical_tree` widened to prefix nodes.

    A prefix application becomes the one-child tuple ``(operator, child)``, so
    it can never be confused with the two-child binary tuple.
    """
    if isinstance(node, Unary):
        return (node.operator, vector_canonical_tree(node.operand))  # type: ignore[return-value]
    if isinstance(node, Binary):
        return (node.operator, vector_canonical_tree(node.left), vector_canonical_tree(node.right))
    return canonical_tree(node)


# --------------------------------------------------------------------------
# The 2D image of a Generation 1 grammar
# --------------------------------------------------------------------------


def from_grammar(grammar: Grammar) -> VectorGrammar:
    """The 2D image of a Generation 1 grammar: ``p`` becomes ``(2p, 2p + 1)``.

    Fact 1.  The Generation 1 parser reads levels, so the tied control grammar
    ``G0`` gets equal powers for ``*``/``/`` and for ``+``/``-``;
    :func:`parseatlas.reachability.grammar_binding_power` is the authoritative
    level view and is used rather than ``Grammar.binding_power``, which
    flattens the ordering and would silently break the tie.
    """
    powers = grammar_binding_power(grammar)
    return VectorGrammar(
        f"{grammar.id}-2D",
        tuple((operator, 2 * power, 2 * power + 1) for operator, power in sorted(powers.items())),
    )


def from_associative_grammar(grammar: AssociativeGrammar) -> VectorGrammar:
    """The 2D image of an experiment 0030 grammar.

    Left-associative ``o`` becomes ``(2p, 2p + 1)`` and right-associative ``o``
    becomes ``(2p + 1, 2p)``: same two numbers, opposite order.  That is Fact 2
    stated as a construction, and it is what makes 0030's second axis a
    coordinate of this one rather than a parameter beside it.
    """
    powers = grammar.binding_power
    sides = grammar.sides
    entries = []
    for operator, power in sorted(powers.items()):
        if sides[operator] == LEFT:
            entries.append((operator, 2 * power, 2 * power + 1))
        else:
            entries.append((operator, 2 * power + 1, 2 * power))
    return VectorGrammar(f"{grammar.id}-2D", tuple(entries))


def generation_one_images() -> tuple[tuple[Grammar, VectorGrammar], ...]:
    """Each of the 25 Generation 1 grammars beside its explicit 2D image."""
    return tuple((grammar, from_grammar(grammar)) for grammar in all_grammars())


def agreement_audit(
    sources: Iterable[str] = AUDIT_CORPUS,
    image_of: Any = from_grammar,
) -> dict[str, Any]:
    """Prove the vector parser a conservative extension of the Generation 1 standard.

    For every one of the 25 Generation 1 grammars and every corpus source, the
    2D image's parse must equal ``parseatlas.parser.parse`` exactly.  The
    comparison is cell by cell on the canonical tree, and every cell is
    counted, agreeing or not.  A grammar with no 2D image would stop the
    experiment, so the per-grammar verdict is reported and not only the total.

    ``image_of`` is the map from a Generation 1 grammar to its vector image.
    It is a parameter so a *wrong* map can be handed to the audit and the audit
    made to report the divergence; a check nobody has seen fail is not a check.

    Sequential by measurement, not by omission: the whole audit is 25 grammars
    times 36 sources of parsing, ``0.09`` s on this 16-core host, while a single
    spawned worker pays about ``1.5`` s for the interpreter and the sympy import
    chain that ``parseatlas`` pulls in.  There is no size at which distributing
    this can win, so it stays on one core and the reason is the number.
    """
    corpus = tuple(sources)
    records = []
    total = 0
    agreements = 0
    for grammar in all_grammars():
        image = image_of(grammar)
        cells = 0
        matches = 0
        divergences = []
        for source in corpus:
            expected = canonical_tree(parse(source, grammar))
            actual = vector_tree(source, image)
            cells += 1
            if expected == actual:
                matches += 1
            elif len(divergences) < 5:
                divergences.append(
                    {"source": source, "expected": expected, "actual": actual}
                )
        total += cells
        agreements += matches
        records.append(
            {
                "grammar_id": grammar.id,
                "precedence": list(grammar.precedence),
                "levels": [list(level) for level in grammar.levels],
                "image_id": image.id,
                "image": {
                    operator: [left, right] for operator, left, right in image.powers
                },
                "cell_count": cells,
                "agreement_count": matches,
                "divergence_count": cells - matches,
                "has_2d_image": cells == matches,
                "divergences": divergences,
            }
        )
    return {
        "workers": 1,
        "source_count": len(corpus),
        "sources": list(corpus),
        "grammar_count": len(records),
        "cell_count": total,
        "agreement_count": agreements,
        "divergence_count": total - agreements,
        "grammars_without_image": [
            record["grammar_id"] for record in records if not record["has_2d_image"]
        ],
        "conservative_extension": total == agreements,
        "grammars": records,
    }


def associativity_image_audit(sources: Iterable[str] = SPLIT_CORPUS) -> dict[str, Any]:
    """The same audit one level up: every 0030 grammar has a 2D image too.

    This is the claim the card asks to verify rather than assume.  If the whole
    ``precedence x associativity`` registry embeds, then associativity is a
    coordinate of the pair and not a separate axis; whether the embedding is
    *onto* is a different question and is answered by :func:`reach_2d`.
    """
    corpus = tuple(sources)
    space = associativity_space() + control_associativity_space()
    cells = 0
    matches = 0
    divergences = []
    images = set()
    for grammar in space:
        image = from_associative_grammar(grammar)
        images.add(image.comparison_matrix(OPERATORS))
        for source in corpus:
            expected = associative_tree(source, grammar)
            actual = vector_tree(source, image)
            cells += 1
            if expected == actual:
                matches += 1
            elif len(divergences) < 5:
                divergences.append(
                    {"grammar": grammar.id, "source": source, "expected": expected, "actual": actual}
                )
    return {
        "grammar_count": len(space),
        "source_count": len(corpus),
        "cell_count": cells,
        "agreement_count": matches,
        "divergence_count": cells - matches,
        "distinct_images": len(images),
        "embeds": cells == matches,
        "divergences": divergences,
    }


# --------------------------------------------------------------------------
# The space of distinct parsers
# --------------------------------------------------------------------------


def witness_words(operators: Sequence[str] = OPERATORS) -> tuple[tuple[str, ...], ...]:
    """The two-operator words that observe every cell of the comparison matrix.

    Fact 3: parsing ``x b y a z`` splits at ``a`` exactly when
    ``left(a) > right(b)``, so the ``m^2`` words of length two read the matrix
    off the parser.  This family is what :func:`behaviour_key` uses, and it is
    why the behavioural quotient is exact.
    """
    names = tuple(operators)
    return tuple((first, second) for first in names for second in names)


_WITNESS_TOKENS: dict[tuple[str, ...], tuple[tuple[Token, ...], ...]] = {}


def _witness_tokens(operators: tuple[str, ...]) -> tuple[tuple[Token, ...], ...]:
    if operators not in _WITNESS_TOKENS:
        leaves = canonical_leaves(3)
        _WITNESS_TOKENS[operators] = tuple(
            tokenize(flat_source(leaves, word)) for word in witness_words(operators)
        )
    return _WITNESS_TOKENS[operators]


def behaviour_key(
    grammar: VectorGrammar, operators: Sequence[str] = OPERATORS
) -> tuple[Tree, ...]:
    """The parse of every witness word: the declared equality of the quotient.

    Two vector grammars are the *same parser* when this tuple is equal.  The
    key is built by parsing, never by inspecting the numbers, so the quotient
    is defined on behaviour; that it coincides with the comparison matrix is an
    observation about it (:func:`witness_reads_matrix`) and not its definition.
    """
    names = tuple(operators)
    return tuple(
        vector_canonical_tree(VectorParser(tokens, grammar).parse())
        for tokens in _witness_tokens(names)
    )


def witness_reads_matrix(
    grammar: VectorGrammar, operators: Sequence[str] = OPERATORS
) -> bool:
    """Does the witness family really read the comparison matrix off the parser?

    Fact 3 in executable form.  For every ordered pair ``(a, b)`` the word
    ``x b y a z`` parses right-leaning -- ``a`` inside ``b``'s right operand --
    exactly when ``left(a) > right(b)``.  If this holds for a grammar, the
    behavioural key of that grammar determines its matrix and conversely.
    """
    names = tuple(operators)
    matrix = grammar.comparison_matrix(names)
    leaves = canonical_leaves(3)
    for row, first in enumerate(names):
        for column, second in enumerate(names):
            source = flat_source(leaves, (second, first))
            tree = vector_tree(source, grammar)
            right_leaning = (second, leaves[0], (first, leaves[1], leaves[2]))
            if (tree == right_leaning) != matrix[row][column]:
                return False
    return True


def _vector_from_vectors(
    operators: Sequence[str], left: Sequence[int], right: Sequence[int]
) -> VectorGrammar:
    names = tuple(operators)
    return VectorGrammar(
        "V" + "-".join(f"{l}{r}" for l, r in zip(left, right)),
        tuple((operator, l, r) for operator, l, r in zip(names, left, right)),
    )


def _enumerate_chunk(
    payload: tuple[tuple[str, ...], tuple[int, ...], int]
) -> list[tuple[tuple[Tree, ...], tuple[tuple[bool, ...], ...], tuple[int, ...], tuple[int, ...]]]:
    """Behaviour keys for one left-vector against every right-vector.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    names, left, limit = payload
    out = []
    for right in product(range(1, limit + 1), repeat=len(names)):
        grammar = _vector_from_vectors(names, left, right)
        out.append(
            (behaviour_key(grammar, names), grammar.comparison_matrix(names), left, right)
        )
    return out


def enumerate_2d(
    operators: Sequence[str] = OPERATORS,
    bound: int | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Enumerate the 2D space and quotient it by behaviour.

    ``bound`` is the largest binding power an assignment may use; components
    range over ``1..bound``.  It defaults to ``len(operators) + 1``, which
    Fact 4 says is saturating, and :func:`saturation_scan` observes that larger
    bounds add assignments without adding parsers.

    Two assignments are the same point when :func:`behaviour_key` agrees, i.e.
    when they parse every two-operator witness word identically.  The raw
    assignment count and the behavioural count are both reported: the gap
    between them is the redundancy of the coordinates, not of the space.
    """
    names = tuple(operators)
    size = len(names)
    limit = size + 1 if bound is None else bound
    if limit < 1:
        raise ValueError("bound must be at least 1")
    tasks = [(names, left, limit) for left in product(range(1, limit + 1), repeat=size)]
    worker_count = resolve_task_workers(len(tasks), workers)
    if worker_count == 1:
        chunks = [_enumerate_chunk(task) for task in tasks]
    else:
        chunk = max(1, len(tasks) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            chunks = list(pool.map(_enumerate_chunk, tasks, chunksize=chunk))

    classes: dict[tuple[Tree, ...], VectorGrammar] = {}
    matrices: dict[tuple[tuple[bool, ...], ...], tuple[Tree, ...]] = {}
    matrix_of_key: dict[tuple[Tree, ...], set[Any]] = {}
    raw = 0
    for rows in chunks:
        for key, matrix, left, right in rows:
            raw += 1
            classes.setdefault(key, _vector_from_vectors(names, left, right))
            matrices.setdefault(matrix, key)
            matrix_of_key.setdefault(key, set()).add(matrix)
    return {
        "operators": list(names),
        "bound": limit,
        "workers": worker_count,
        "raw_assignment_count": raw,
        "behavioural_count": len(classes),
        "matrix_count": len(matrices),
        "matrix_equals_behaviour": len(matrices) == len(classes)
        and all(len(value) == 1 for value in matrix_of_key.values()),
        "collapse_factor": raw / len(classes),
        "representatives": tuple(classes.values()),
    }


def representatives(
    operators: Sequence[str] = OPERATORS, bound: int | None = None
) -> tuple[VectorGrammar, ...]:
    """One vector grammar per distinct parser, built from the comparison matrix.

    Same partition as :func:`enumerate_2d` and far cheaper, because it groups
    by the matrix rather than by a parse.  ``matrix_equals_behaviour`` in
    :func:`enumerate_2d` is the observation that licenses the shortcut, and the
    tests assert the two agree.
    """
    names = tuple(operators)
    size = len(names)
    limit = size + 1 if bound is None else bound
    seen: dict[tuple[tuple[bool, ...], ...], VectorGrammar] = {}
    vectors = list(product(range(1, limit + 1), repeat=size))
    for left in vectors:
        for right in vectors:
            matrix = tuple(tuple(l > r for r in right) for l in left)
            if matrix not in seen:
                seen[matrix] = _vector_from_vectors(names, left, right)
    return tuple(seen.values())


def three_d_representatives(
    operators: Sequence[str] = OPERATORS,
    prefix_operator: str = "-",
    bound: int | None = None,
) -> tuple[VectorGrammar, ...]:
    """One vector grammar per distinct parser once a free prefix power is added.

    The third component is observed by the vector ``left(a) > prefix``, so the
    behaviour of the 3D parser is the pair ``(matrix, prefix vector)``.
    """
    names = tuple(operators)
    size = len(names)
    limit = size + 1 if bound is None else bound
    seen: dict[Any, VectorGrammar] = {}
    vectors = list(product(range(1, limit + 1), repeat=size))
    for left in vectors:
        for right in vectors:
            matrix = tuple(tuple(l > r for r in right) for l in left)
            for power in range(1, limit + 1):
                key = (matrix, tuple(l > power for l in left))
                if key not in seen:
                    grammar = VectorGrammar(
                        "W" + "-".join(f"{l}{r}" for l, r in zip(left, right)) + f"-p{power}",
                        tuple((operator, l, r) for operator, l, r in zip(names, left, right)),
                        ((prefix_operator, power),),
                    )
                    seen[key] = grammar
    return tuple(seen.values())


def flat_slice(operators: Sequence[str] = OPERATORS) -> dict[str, Any]:
    """The parsers a *scalar* binding power can express, associativity included.

    A flat grammar is an ordered partition of the operators into levels -- the
    shape ``parseatlas.grammar.Grammar`` already has -- plus one side per level,
    which is what experiment 0030 added.  Lifting a level ``l`` to ``(2l, 2l+1)``
    or ``(2l+1, 2l)`` puts every such grammar inside the vector space, so the
    two spaces can be counted in the same units: how many of the vector space's
    parsers does the flat model reach at all?
    """
    names = tuple(operators)
    size = len(names)
    seen: dict[tuple[tuple[bool, ...], ...], VectorGrammar] = {}
    raw = 0
    for assignment in product(range(size), repeat=size):
        blocks = sorted(set(assignment))
        if blocks != list(range(len(blocks))):
            continue  # not an ordered partition in canonical form
        for sides in product((LEFT, RIGHT), repeat=len(blocks)):
            raw += 1
            entries = []
            for operator, level in zip(names, assignment):
                power = len(blocks) - level
                if sides[level] == LEFT:
                    entries.append((operator, 2 * power, 2 * power + 1))
                else:
                    entries.append((operator, 2 * power + 1, 2 * power))
            grammar = VectorGrammar("flat", tuple(entries))
            seen.setdefault(grammar.comparison_matrix(names), grammar)
    total = len(representatives(names))
    return {
        "operators": list(names),
        "raw_flat_grammar_count": raw,
        "flat_parser_count": len(seen),
        "vector_parser_count": total,
        "flat_fraction": len(seen) / total,
        "vector_only_parser_count": total - len(seen),
    }


def saturation_scan(
    operators: Sequence[str] = OPERATORS, bounds: Sequence[int] = (2, 3, 4, 5, 6, 7)
) -> dict[str, Any]:
    """Where the enumeration bound stops mattering, observed rather than declared.

    This is the answer to *what lies past the bound*: past ``len(operators) + 1``
    the raw assignment count keeps growing and the behavioural count does not
    move at all, because there is no further parser to find.
    """
    names = tuple(operators)
    rows = []
    for bound in bounds:
        binary = representatives(names, bound)
        rows.append(
            {
                "bound": bound,
                "raw_assignment_count": bound ** (2 * len(names)),
                "behavioural_count": len(binary),
            }
        )
    saturating = None
    for index in range(1, len(rows)):
        if rows[index]["behavioural_count"] == rows[index - 1]["behavioural_count"]:
            saturating = rows[index - 1]["bound"]
            break
    return {
        "operators": list(names),
        "levels": rows,
        "saturating_bound": saturating,
        "predicted_saturating_bound": len(names) + 1,
        "saturated": saturating == len(names) + 1,
    }


# --------------------------------------------------------------------------
# Reach: how much of the parenthesization space the 2D space touches
# --------------------------------------------------------------------------


def _pattern_words(size: int, blocks: int) -> tuple[tuple[int, ...], ...]:
    """Restricted growth strings: one representative per operator-word pattern.

    The 2D space is invariant under renaming operators, so two words that
    differ only by a permutation of the alphabet reach the same *number* of
    trees.  Enumerating patterns instead of words is therefore exact, not a
    sample, and :func:`reach_2d` cross-checks it against the unreduced walk.
    """
    out: list[tuple[int, ...]] = []

    def walk(prefix: list[int], used: int) -> None:
        if len(prefix) == size:
            out.append(tuple(prefix))
            return
        for symbol in range(min(used + 1, blocks)):
            walk(prefix + [symbol], max(used, symbol + 1))

    walk([], 0)
    return tuple(out)


def _falling(total: int, taken: int) -> int:
    value = 1
    for step in range(taken):
        value *= total - step
    return value


_SPACE_CACHE: dict[int, tuple[VectorGrammar, ...]] = {}


def _cached_representatives(size: int) -> tuple[VectorGrammar, ...]:
    if size not in _SPACE_CACHE:
        _SPACE_CACHE[size] = representatives(OPERATORS[:size])
    return _SPACE_CACHE[size]


_ASSOC_CACHE: tuple[AssociativeGrammar, ...] | None = None


def _cached_associativity_space() -> tuple[AssociativeGrammar, ...]:
    global _ASSOC_CACHE
    if _ASSOC_CACHE is None:
        _ASSOC_CACHE = associativity_space()
    return _ASSOC_CACHE


_STRICT_CACHE: tuple[Grammar, ...] | None = None


def _cached_strict() -> tuple[Grammar, ...]:
    global _STRICT_CACHE
    if _STRICT_CACHE is None:
        _STRICT_CACHE = strict_grammars()
    return _STRICT_CACHE


def _reach_pattern(payload: tuple[int, tuple[int, ...]]) -> tuple[int, int, int, int, int]:
    """Reachable tree counts for one operator-word pattern, three spaces at once.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    size, pattern = payload
    blocks = max(pattern) + 1
    word = tuple(OPERATORS[symbol] for symbol in pattern)
    leaves = canonical_leaves(size + 1)
    source = flat_source(leaves, word)
    tokens = tokenize(source)
    vector: set[Tree] = set()
    for grammar in _cached_representatives(blocks):
        parser = VectorParser(tokens, grammar)
        vector.add(vector_canonical_tree(parser.parse()))
    precedence = {canonical_tree(parse(source, grammar)) for grammar in _cached_strict()}
    associative = {associative_tree(source, grammar) for grammar in _cached_associativity_space()}
    multiplicity = _falling(len(OPERATORS), blocks)
    return size, multiplicity, len(precedence), len(associative), len(vector)


def reach_2d(
    max_operators: int = 6, workers: int | None = None, reduce_by_pattern: bool = True
) -> dict[str, Any]:
    """The headline: what fraction of the parenthesization space each space reaches.

    Same ``k = 2..max_operators`` range and the same word family as experiments
    0020 and 0030 -- every word of length ``k`` over ``(+ - * /)``, canonical
    leaves ``a, b, c, ...``, and the full Catalan set of parenthesizations as
    the denominator -- so the three columns stand in one table.

    Ground truth is real parsing in all three columns.  The 2D column is exact
    and not a sample: :func:`representatives` enumerates every parser the space
    contains, and Fact 4 says the bound behind it is saturating.

    ``reduce_by_pattern`` walks one word per renaming-orbit and multiplies by
    the orbit size.  Set it to ``False`` to walk all ``4**k`` words; the tests
    assert the two agree.
    """
    if max_operators < 2:
        raise ValueError("max_operators must be at least 2")
    tasks: list[tuple[int, tuple[int, ...]]] = []
    if reduce_by_pattern:
        for size in range(2, max_operators + 1):
            tasks.extend((size, pattern) for pattern in _pattern_words(size, len(OPERATORS)))
    else:
        index = {operator: position for position, operator in enumerate(OPERATORS)}
        for size in range(2, max_operators + 1):
            for word in product(OPERATORS, repeat=size):
                tasks.append((size, tuple(index[operator] for operator in word)))
    worker_count = resolve_task_workers(len(tasks), workers)
    if worker_count == 1:
        results = [_reach_pattern(task) for task in tasks]
    else:
        chunk = max(1, len(tasks) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            results = list(pool.map(_reach_pattern, tasks, chunksize=chunk))

    buckets: dict[int, dict[str, Any]] = {
        size: {
            "operator_count": size,
            "pattern_count": 0,
            "word_count": 0,
            "precedence_reachable": 0,
            "associativity_reachable": 0,
            "vector_reachable": 0,
        }
        for size in range(2, max_operators + 1)
    }
    for size, multiplicity, precedence, associative, vector in results:
        bucket = buckets[size]
        bucket["pattern_count"] += 1
        weight = multiplicity if reduce_by_pattern else 1
        bucket["word_count"] += weight
        bucket["precedence_reachable"] += weight * precedence
        bucket["associativity_reachable"] += weight * associative
        bucket["vector_reachable"] += weight * vector

    per_k = []
    for size in range(2, max_operators + 1):
        bucket = buckets[size]
        catalan = len(catalan_trees(canonical_leaves(size + 1), ("+",) * size))
        trees = bucket["word_count"] * catalan
        bucket["catalan"] = catalan
        bucket["tree_count"] = trees
        bucket["precedence_coverage"] = bucket["precedence_reachable"] / trees
        bucket["associativity_coverage"] = bucket["associativity_reachable"] / trees
        bucket["vector_coverage"] = bucket["vector_reachable"] / trees
        gap = trees - bucket["precedence_reachable"]
        bucket["unreachable_before"] = gap
        bucket["unreachable_after_associativity"] = trees - bucket["associativity_reachable"]
        bucket["unreachable_after_vector"] = trees - bucket["vector_reachable"]
        bucket["associativity_recovered"] = (
            bucket["associativity_reachable"] - bucket["precedence_reachable"]
        )
        bucket["vector_recovered"] = bucket["vector_reachable"] - bucket["precedence_reachable"]
        bucket["associativity_recovered_fraction"] = (
            bucket["associativity_recovered"] / gap if gap else 0.0
        )
        bucket["vector_recovered_fraction"] = bucket["vector_recovered"] / gap if gap else 0.0
        per_k.append(bucket)

    trees = sum(bucket["tree_count"] for bucket in per_k)
    precedence = sum(bucket["precedence_reachable"] for bucket in per_k)
    associative = sum(bucket["associativity_reachable"] for bucket in per_k)
    vector = sum(bucket["vector_reachable"] for bucket in per_k)
    gap = trees - precedence
    return {
        "max_operators": max_operators,
        "workers": worker_count,
        "reduce_by_pattern": reduce_by_pattern,
        "task_count": len(tasks),
        "per_k": per_k,
        "total_words": sum(bucket["word_count"] for bucket in per_k),
        "total_trees": trees,
        "precedence_reachable": precedence,
        "associativity_reachable": associative,
        "vector_reachable": vector,
        "unreachable_before": gap,
        "unreachable_after_associativity": trees - associative,
        "unreachable_after_vector": trees - vector,
        "associativity_recovered": associative - precedence,
        "vector_recovered": vector - precedence,
        "associativity_recovered_fraction": (associative - precedence) / gap if gap else 0.0,
        "vector_recovered_fraction": (vector - precedence) / gap if gap else 0.0,
        "vector_beats_associativity": vector > associative,
        "vector_contains_associativity": vector >= associative,
    }


def structural_ceiling(sizes: Sequence[int] = (6, 7, 8, 9, 10, 11, 12)) -> dict[str, Any]:
    """Where each space's grammar count stops being able to cover the space.

    A single source can reach at most one tree per distinct parser, so coverage
    is bounded above by ``parsers / C(k)`` whatever the parsers are.  This is
    where the ``k <= 6`` enumeration's blindness is priced: past the walked
    range the ceiling is arithmetic and needs no run.
    """
    rows = []
    for size in sizes:
        catalan = len(catalan_trees(canonical_leaves(size + 1), ("+",) * size))
        rows.append(
            {
                "operator_count": size,
                "catalan": catalan,
                "precedence_ceiling": 24 / catalan,
                "associativity_ceiling": 384 / catalan,
                "vector_ceiling": 6902 / catalan,
                "three_d_ceiling": 41506 / catalan,
            }
        )
    return {"levels": rows}


def coverage_table(sources: Iterable[str] = COVERAGE_CORPUS) -> dict[str, Any]:
    """Per-expression coverage on 0020's corpus, three spaces in one row."""
    space = representatives(OPERATORS)
    strict = strict_grammars()
    extended = associativity_space()
    records = []
    for source in sources:
        precedence = {canonical_tree(parse(source, grammar)) for grammar in strict}
        associative = {associative_tree(source, grammar) for grammar in extended}
        vector = {vector_tree(source, grammar) for grammar in space}
        control = canonical_tree(parse(source, control_grammar()))
        leaves, operators = _in_order_tree(control)
        total = len(catalan_trees(leaves, operators))
        records.append(
            {
                "source": source,
                "leaf_count": len(leaves),
                "operator_count": len(operators),
                "catalan_total": total,
                "precedence_reachable": len(precedence),
                "associativity_reachable": len(associative),
                "vector_reachable": len(vector),
                "precedence_coverage": len(precedence) / total,
                "associativity_coverage": len(associative) / total,
                "vector_coverage": len(vector) / total,
                "gained_over_associativity": len(vector - associative),
                "vector_contains_associativity": associative <= vector,
            }
        )
    denominator = max(len(records), 1)
    return {
        "expression_count": len(records),
        "mean_precedence_coverage": sum(r["precedence_coverage"] for r in records) / denominator,
        "mean_associativity_coverage": sum(r["associativity_coverage"] for r in records)
        / denominator,
        "mean_vector_coverage": sum(r["vector_coverage"] for r in records) / denominator,
        "expressions": records,
    }


def _in_order_tree(tree: Tree) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if isinstance(tree, str):
        return (tree,), ()
    left_leaves, left_operators = _in_order_tree(tree[1])
    right_leaves, right_operators = _in_order_tree(tree[2])
    return left_leaves + right_leaves, left_operators + (tree[0],) + right_operators


# --------------------------------------------------------------------------
# The third component
# --------------------------------------------------------------------------


def prefix_source(leaves: Sequence[str], operators: Sequence[str], prefix: str = "-") -> str:
    """``- x0 w1 x1 ... wk xk``: a flat word carrying one leading prefix operator."""
    return f"{prefix} " + flat_source(leaves, operators)


def prefix_trees(
    leaves: Sequence[str], operators: Sequence[str], prefix: str = "-"
) -> tuple[Tree, ...]:
    """Every tree the prefixed word admits.

    The prefix node's operand is a contiguous run starting at the first leaf,
    so the count is ``sum_j C(j) * C(k - j) = C(k + 1)``: the Catalan
    convolution, and the honest denominator for the 3D reach question.
    """
    leaves = tuple(leaves)
    operators = tuple(operators)
    out: list[Tree] = []
    for split in range(len(operators) + 1):
        inner = catalan_trees(leaves[: split + 1], operators[:split])
        outer_operators = operators[split:]
        for head in inner:
            negated: Tree = (prefix, head)  # type: ignore[assignment]
            outer = catalan_trees((negated,) + leaves[split + 1 :], outer_operators)
            out.extend(outer)
    return tuple(out)


def derived_prefix(grammar: VectorGrammar, prefix: str = "-") -> VectorGrammar:
    """The 2D reading of a prefix operator: its power is its own right component.

    A prefix operator has only a right operand, so with no third component
    there is exactly one power available to it.  This is the baseline the third
    component is measured against.
    """
    return VectorGrammar(
        grammar.id + "-derived",
        grammar.powers,
        ((prefix, grammar.right[prefix]),),
    )


def _prefix_orbit_words(
    size: int, prefix_index: int = 1
) -> tuple[tuple[tuple[int, ...], int], ...]:
    """One word per orbit under the permutations that fix the prefix operator.

    The 3D space is invariant under renaming the operators, but ``-`` is
    distinguished by carrying the prefix power, so only the ``3! = 6``
    permutations of the other three symbols act.  Orbit representatives are the
    lexicographic minima, and each is returned with its orbit size so the
    reduced walk reproduces the unreduced total exactly.
    """
    from itertools import permutations as _perm

    others = [index for index in range(len(OPERATORS)) if index != prefix_index]
    maps = []
    for arrangement in _perm(others):
        mapping = dict(zip(others, arrangement))
        mapping[prefix_index] = prefix_index
        maps.append(mapping)
    seen: dict[tuple[int, ...], int] = {}
    for word in product(range(len(OPERATORS)), repeat=size):
        orbit = min(tuple(mapping[symbol] for symbol in word) for mapping in maps)
        seen[orbit] = seen.get(orbit, 0) + 1
    return tuple(sorted(seen.items()))


_THREE_D_CACHE: dict[int, tuple[VectorGrammar, ...]] = {}


def _cached_three_d(size: int) -> tuple[VectorGrammar, ...]:
    if size not in _THREE_D_CACHE:
        _THREE_D_CACHE[size] = three_d_representatives(OPERATORS[:size])
    return _THREE_D_CACHE[size]


def _reach_prefix_word(payload: tuple[int, tuple[int, ...], int]) -> tuple[int, int, int, int]:
    """Reachable prefixed trees for one word: derived prefix vs. free prefix.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    size, word_indices, multiplicity = payload
    word = tuple(OPERATORS[symbol] for symbol in word_indices)
    leaves = canonical_leaves(size + 1)
    source = prefix_source(leaves, word)
    tokens = tokenize(source)
    two_d: set[Tree] = set()
    three_d: set[Tree] = set()
    for grammar in _cached_three_d(len(OPERATORS)):
        three_d.add(vector_canonical_tree(VectorParser(tokens, grammar).parse()))
    for grammar in _cached_representatives(len(OPERATORS)):
        derived = derived_prefix(grammar)
        two_d.add(vector_canonical_tree(VectorParser(tokens, derived).parse()))
    return size, multiplicity, len(two_d), len(three_d)


#: Sources carrying a prefix ``-`` somewhere other than the head.  The 3D reach
#: sweep enumerates head-prefixed words only, because those have a closed tree
#: count (``C(k + 1)``); this probe is the answer to *would the words the sweep
#: does not produce change the direction of the result?*
INTERIOR_PREFIX_PROBE: tuple[str, ...] = (
    "a + - b",
    "a * - b + c",
    "a - - b",
    "a + - b * c",
    "a / - b - c",
    "- a + - b",
    "a - - b - - c",
    "a * - b / - c",
)


def interior_prefix_probe(
    sources: Iterable[str] = INTERIOR_PREFIX_PROBE,
) -> dict[str, Any]:
    """Derived versus free prefix power on words the head-prefix sweep omits.

    Reports distinct trees reached, not coverage, because the tree space of an
    arbitrarily placed prefix has no closed form here.  The question it settles
    is only the direction: does freeing the third component still buy trees when
    the prefix sits inside the word?
    """
    space = _cached_representatives(len(OPERATORS))
    free = _cached_three_d(len(OPERATORS))
    records = []
    for source in sources:
        tokens = tokenize(source)
        derived = {
            vector_canonical_tree(VectorParser(tokens, derived_prefix(grammar)).parse())
            for grammar in space
        }
        loose = {
            vector_canonical_tree(VectorParser(tokens, grammar).parse()) for grammar in free
        }
        records.append(
            {
                "source": source,
                "two_d_trees": len(derived),
                "three_d_trees": len(loose),
                "gained": len(loose - derived),
                "two_d_subset_of_three_d": derived <= loose,
            }
        )
    return {
        "source_count": len(records),
        "two_d_trees": sum(record["two_d_trees"] for record in records),
        "three_d_trees": sum(record["three_d_trees"] for record in records),
        "gained": sum(record["gained"] for record in records),
        "sources_with_a_gain": sum(1 for record in records if record["gained"]),
        "containment_holds": all(record["two_d_subset_of_three_d"] for record in records),
        "expressions": records,
    }


def three_d(
    max_operators: int = 5, workers: int | None = None
) -> dict[str, Any]:
    """What a third component buys over the second, in trees reached.

    The family is the same ``4**k`` operator words, each carrying one leading
    prefix ``-``.  The denominator is ``C(k + 1)``, the number of trees such a
    word admits.  The baseline is the 2D space with the prefix power *derived*
    from the operator's own right component -- the only reading available when
    there is no third number -- and the treatment is the same space with the
    prefix power free.
    """
    if max_operators < 2:
        raise ValueError("max_operators must be at least 2")
    tasks: list[tuple[int, tuple[int, ...], int]] = []
    for size in range(2, max_operators + 1):
        for word, multiplicity in _prefix_orbit_words(size):
            tasks.append((size, word, multiplicity))
    worker_count = resolve_task_workers(len(tasks), workers, THREE_D_MINIMUM_TASKS)
    if worker_count == 1:
        results = [_reach_prefix_word(task) for task in tasks]
    else:
        chunk = max(1, len(tasks) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            results = list(pool.map(_reach_prefix_word, tasks, chunksize=chunk))

    buckets: dict[int, dict[str, Any]] = {
        size: {
            "operator_count": size,
            "orbit_count": 0,
            "word_count": 0,
            "two_d_reachable": 0,
            "three_d_reachable": 0,
        }
        for size in range(2, max_operators + 1)
    }
    for size, multiplicity, two, three in results:
        bucket = buckets[size]
        bucket["orbit_count"] += 1
        bucket["word_count"] += multiplicity
        bucket["two_d_reachable"] += multiplicity * two
        bucket["three_d_reachable"] += multiplicity * three

    per_k = []
    for size in range(2, max_operators + 1):
        bucket = buckets[size]
        leaves = canonical_leaves(size + 1)
        total_per_word = len(prefix_trees(leaves, ("+",) * size))
        trees = bucket["word_count"] * total_per_word
        bucket["trees_per_word"] = total_per_word
        bucket["tree_count"] = trees
        bucket["two_d_coverage"] = bucket["two_d_reachable"] / trees
        bucket["three_d_coverage"] = bucket["three_d_reachable"] / trees
        bucket["gained"] = bucket["three_d_reachable"] - bucket["two_d_reachable"]
        bucket["gain_fraction_of_gap"] = (
            bucket["gained"] / (trees - bucket["two_d_reachable"])
            if trees - bucket["two_d_reachable"]
            else 0.0
        )
        bucket["gain_ratio"] = bucket["three_d_reachable"] / bucket["two_d_reachable"]
        per_k.append(bucket)

    trees = sum(bucket["tree_count"] for bucket in per_k)
    two = sum(bucket["two_d_reachable"] for bucket in per_k)
    three = sum(bucket["three_d_reachable"] for bucket in per_k)
    ratios = [bucket["gain_ratio"] for bucket in per_k]
    return {
        "max_operators": max_operators,
        "workers": worker_count,
        "task_count": len(tasks),
        "per_k": per_k,
        "total_trees": trees,
        "two_d_reachable": two,
        "three_d_reachable": three,
        "gained": three - two,
        "gain_fraction_of_gap": (three - two) / (trees - two) if trees - two else 0.0,
        "two_d_coverage": two / trees,
        "three_d_coverage": three / trees,
        "gain_ratio_by_k": ratios,
        "gain_ratio_still_rising": all(
            ratios[index] < ratios[index + 1] for index in range(len(ratios) - 1)
        ),
    }


# --------------------------------------------------------------------------
# The other non-flat direction: partial orders
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PartialOrderGrammar:
    """A preorder on the operators plus a side per equivalence class.

    ``relation`` is the reflexive, transitive set of pairs ``(a, b)`` read as
    *a binds at least as tightly as b*.  Two operators may be **incomparable**:
    neither pair present.  A mixed expression whose reading would depend on
    that missing comparison is then *refused* rather than resolved by an
    arbitrary rule, which is what real languages do when they leave an operator
    pair unranked.

    ``sides`` is consulted only for operators that are equivalent under the
    relation, so it decides associativity and nothing else.
    """

    id: str
    relation: tuple[tuple[str, str], ...]
    sides: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        pairs = set(self.relation)
        operators = sorted({operator for pair in pairs for operator in pair})
        for operator in operators:
            if (operator, operator) not in pairs:
                raise ValueError(f"relation is not reflexive at {operator!r}")
        for left, middle in pairs:
            for other, right in pairs:
                if middle == other and (left, right) not in pairs:
                    raise ValueError("relation is not transitive")
        assigned = dict(self.sides)
        for operator in operators:
            if assigned.get(operator) not in SIDES:
                raise ValueError(f"side missing or invalid for {operator!r}")
        object.__setattr__(self, "relation", tuple(sorted(pairs)))
        object.__setattr__(self, "sides", tuple(sorted(self.sides)))

    @property
    def operators(self) -> tuple[str, ...]:
        return tuple(sorted({operator for pair in self.relation for operator in pair}))

    def compare(self, first: str, second: str) -> str:
        """``tighter`` / ``looser`` / ``equivalent`` / ``incomparable``."""
        pairs = set(self.relation)
        forward = (first, second) in pairs
        backward = (second, first) in pairs
        if forward and backward:
            return "equivalent"
        if forward:
            return "tighter"
        if backward:
            return "looser"
        return "incomparable"

    @property
    def comparable_pair_count(self) -> int:
        """Unordered operator pairs that are ranked at all."""
        names = self.operators
        return sum(
            1
            for index, first in enumerate(names)
            for second in names[index + 1 :]
            if self.compare(first, second) != "incomparable"
        )

    @property
    def incomparable_pair_count(self) -> int:
        names = self.operators
        total = len(names) * (len(names) - 1) // 2
        return total - self.comparable_pair_count


class PartialOrderParser(Parser):
    """Precedence climbing where the minimum is an *operator*, not a number.

    Inside the right operand of ``context`` the parser must decide whether the
    operator it now sees binds more tightly.  With a total order that is a
    numeric comparison; with a preorder it can come back ``incomparable``, and
    then the parser raises :class:`AmbiguousParse` instead of picking a side.
    """

    def __init__(self, tokens: tuple[Token, ...], grammar: PartialOrderGrammar) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.index = 0
        self._sides = dict(grammar.sides)

    def parse(self) -> Node:
        result = self._level(None)
        if self._current.kind != "eof":
            raise ValueError(f"Unexpected token: {self._current.value!r}")
        return result

    def _expression(self, minimum_power: int) -> Node:
        # The inherited ``_primary`` calls ``_expression(0)`` for a parenthesized
        # group, and a group starts a fresh context.
        del minimum_power
        return self._level(None)

    def _level(self, context: str | None) -> Node:
        left = self._primary()
        while self._current.kind == "operator":
            operator = self._current.value
            if context is None:
                consume = True
            else:
                verdict = self.grammar.compare(operator, context)
                if verdict == "incomparable":
                    raise AmbiguousParse(
                        f"{operator!r} and {context!r} are unranked; the reading is not determined"
                    )
                if verdict == "tighter":
                    consume = True
                elif verdict == "looser":
                    consume = False
                else:
                    consume = self._sides[operator] == RIGHT
            if not consume:
                break
            self._advance()
            left = Binary(operator, left, self._level(operator))
        return left


def partial_order_parse(source: str, grammar: PartialOrderGrammar) -> Node:
    return PartialOrderParser(tokenize(source), grammar).parse()


def partial_order_tree(source: str, grammar: PartialOrderGrammar) -> Tree:
    return canonical_tree(partial_order_parse(source, grammar))


def preorders(
    operators: Sequence[str] = OPERATORS, side: str = LEFT
) -> tuple[PartialOrderGrammar, ...]:
    """Every preorder on the operator set, with one fixed side.

    The **declared subset**: this enumerates all reflexive transitive relations
    on the four operators -- ties and incomparabilities both -- but fixes
    associativity at ``left`` for every operator, matching the Generation 1
    convention.  Letting the side vary per equivalence class multiplies the
    space without touching the refusal question, which is what this function is
    for; :func:`partial_orders` reports the side-varying count beside the fixed
    one so the restriction is visible where the answer is read.
    """
    names = tuple(operators)
    size = len(names)
    off_diagonal = [
        (first, second)
        for first in range(size)
        for second in range(size)
        if first != second
    ]
    out = []
    for mask in range(1 << len(off_diagonal)):
        pairs = {(index, index) for index in range(size)}
        for position, pair in enumerate(off_diagonal):
            if mask >> position & 1:
                pairs.add(pair)
        transitive = True
        for left, middle in pairs:
            for other, right in pairs:
                if middle == other and (left, right) not in pairs:
                    transitive = False
                    break
            if not transitive:
                break
        if not transitive:
            continue
        relation = tuple(sorted((names[a], names[b]) for a, b in pairs))
        out.append(
            PartialOrderGrammar(
                f"P{mask:04d}",
                relation,
                tuple((operator, side) for operator in names),
            )
        )
    return tuple(out)


def from_grammar_preorder(grammar: Grammar, side: str = LEFT) -> PartialOrderGrammar:
    """The preorder a Generation 1 grammar already is: a total preorder on levels."""
    powers = grammar_binding_power(grammar)
    names = sorted(powers)
    relation = tuple(
        (first, second)
        for first in names
        for second in names
        if powers[first] >= powers[second]
    )
    return PartialOrderGrammar(
        f"{grammar.id}-PO", relation, tuple((operator, side) for operator in names)
    )


def _render(tree: Tree, bracketed: frozenset[tuple[int, ...]], path: tuple[int, ...] = ()) -> str:
    if isinstance(tree, str):
        return tree
    operator, left, right = tree  # type: ignore[misc]
    text = (
        f"{_render(left, bracketed, path + (0,))} "
        f"{operator} "
        f"{_render(right, bracketed, path + (1,))}"
    )
    return f"({text})" if path in bracketed else text


def _internal_paths(tree: Tree, path: tuple[int, ...] = ()) -> list[tuple[int, ...]]:
    if isinstance(tree, str):
        return []
    return (
        [path]
        + _internal_paths(tree[1], path + (0,))
        + _internal_paths(tree[2], path + (1,))
    )


def minimum_brackets(tree: Tree, grammar: PartialOrderGrammar) -> int | None:
    """Fewest bracket pairs that write ``tree`` under ``grammar``, or ``None``.

    A writing is the tree rendered with parentheses at a chosen set of internal
    nodes; it counts only if it re-parses under ``grammar`` to the very same
    tree, so an accepted writing that means something else is not a writing of
    this tree.  The search is exhaustive over subsets of internal nodes, so the
    number is a genuine minimum and not the first success found.
    """
    paths = _internal_paths(tree)
    for count in range(len(paths) + 1):
        for chosen in _combinations(paths, count):
            source = _render(tree, frozenset(chosen))
            try:
                if partial_order_tree(source, grammar) == tree:
                    return count
            except (AmbiguousParse, ValueError):
                continue
    return None


def _combinations(items: Sequence[Any], count: int) -> list[tuple[Any, ...]]:
    from itertools import combinations as _comb

    return list(_comb(items, count))


def partial_orders(
    sources: Iterable[str] = COVERAGE_CORPUS, workers: int | None = None
) -> dict[str, Any]:
    """Price both sides of refusing instead of choosing.

    The **buy** is freedom from an arbitrary reading.  A source is
    *choice-bearing* when the 24 strict Generation 1 grammars do not agree on
    it: there the reading a total order supplies is a convention, not a
    deduction.  A refusal on a choice-bearing source withholds a real
    arbitrariness; a refusal on a source every grammar reads the same way
    withholds nothing and is counted separately as an over-refusal.

    The **pay** is brackets.  For every conventional reading -- each of the 25
    Generation 1 grammars on each source -- the minimum number of bracket pairs
    that still writes that reading under the partial order is computed
    exhaustively, and the mean is the price in notation.
    """
    corpus = tuple(sources)
    space = preorders(OPERATORS)
    strict = strict_grammars()
    registry = all_grammars()
    conventional: dict[str, dict[str, Tree]] = {}
    choice_bearing: dict[str, bool] = {}
    for source in corpus:
        readings = {grammar.id: canonical_tree(parse(source, grammar)) for grammar in registry}
        conventional[source] = readings
        choice_bearing[source] = (
            len({canonical_tree(parse(source, grammar)) for grammar in strict}) > 1
        )

    # Sequential whatever the task count: one preorder over the corpus is about
    # 4 ms of parsing, so all 355 of them are 1.30 s in total while 15 spawned
    # interpreters take 2.26 s to do the same work.  The general constant is a
    # task count and this workload is priced per task, so the call site says so.
    worker_count = resolve_task_workers(len(space), workers, minimum=None)
    bearing_flags = tuple(choice_bearing[source] for source in corpus)
    payload = [(grammar, corpus, bearing_flags) for grammar in space]
    if worker_count == 1:
        rows = [_score_preorder(item) for item in payload]
    else:
        chunk = max(1, len(payload) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            rows = list(pool.map(_score_preorder, payload, chunksize=chunk))

    by_incomparable: dict[int, dict[str, Any]] = {}
    total_cells = 0
    total_refusals = 0
    total_true = 0
    total_over = 0
    total_silent = 0
    for row in rows:
        bucket = by_incomparable.setdefault(
            row["incomparable_pairs"],
            {
                "incomparable_pairs": row["incomparable_pairs"],
                "grammar_count": 0,
                "cell_count": 0,
                "refusal_count": 0,
                "true_refusal_count": 0,
                "over_refusal_count": 0,
                "silent_choice_count": 0,
            },
        )
        bucket["grammar_count"] += 1
        bucket["cell_count"] += len(corpus)
        bucket["refusal_count"] += row["refusal_count"]
        bucket["true_refusal_count"] += row["true_refusal_count"]
        bucket["over_refusal_count"] += row["over_refusal_count"]
        bucket["silent_choice_count"] += row["silent_choice_count"]
        total_cells += len(corpus)
        total_refusals += row["refusal_count"]
        total_true += row["true_refusal_count"]
        total_over += row["over_refusal_count"]
        total_silent += row["silent_choice_count"]

    unranked = len(OPERATORS) * (len(OPERATORS) - 1) // 2
    antichain = next(
        grammar for grammar in space if grammar.incomparable_pair_count == unranked
    )
    antichain_refusals = []
    for source in corpus:
        try:
            partial_order_tree(source, antichain)
            antichain_refusals.append(False)
        except AmbiguousParse:
            antichain_refusals.append(True)

    conventional_cells = 0
    withdrawn = 0
    bracket_costs: list[int] = []
    unwritable = 0
    for source, readings in conventional.items():
        for tree in readings.values():
            conventional_cells += 1
            cost = minimum_brackets(tree, antichain)
            if cost is None:
                unwritable += 1
                continue
            if cost > 0:
                withdrawn += 1
            bracket_costs.append(cost)

    levels = [by_incomparable[key] for key in sorted(by_incomparable)]
    for bucket in levels:
        bucket["refusal_rate"] = bucket["refusal_count"] / bucket["cell_count"]
        bucket["over_refusal_rate"] = bucket["over_refusal_count"] / bucket["cell_count"]
        bucket["silent_choice_rate"] = bucket["silent_choice_count"] / bucket["cell_count"]

    return {
        "workers": worker_count,
        "source_count": len(corpus),
        "sources": list(corpus),
        "preorder_count": len(space),
        "total_preorder_count": sum(
            1 for grammar in space if grammar.incomparable_pair_count == 0
        ),
        "strict_total_order_count": sum(
            1
            for grammar in space
            if grammar.incomparable_pair_count == 0
            and all(
                grammar.compare(first, second) != "equivalent"
                for index, first in enumerate(OPERATORS)
                for second in OPERATORS[index + 1 :]
            )
        ),
        "conventional_preorders_present": all(
            any(
                grammar.relation == from_grammar_preorder(registered).relation
                for grammar in space
            )
            for registered in all_grammars()
        ),
        "side_varying_space_size": len(space) * 2 ** len(OPERATORS),
        "choice_bearing_sources": sum(1 for value in choice_bearing.values() if value),
        "cell_count": total_cells,
        "refusal_count": total_refusals,
        "refusal_rate": total_refusals / total_cells,
        "true_refusal_count": total_true,
        "over_refusal_count": total_over,
        "silent_choice_count": total_silent,
        "refusal_precision": total_true / total_refusals if total_refusals else 0.0,
        "levels": levels,
        "antichain_id": antichain.id,
        "antichain_refused_sources": sum(1 for value in antichain_refusals if value),
        "antichain_refusal_flags": antichain_refusals,
        "conventional_reading_count": conventional_cells,
        "conventional_readings_needing_brackets": withdrawn,
        "conventional_readings_unwritable": unwritable,
        "mean_minimum_brackets": sum(bracket_costs) / len(bracket_costs)
        if bracket_costs
        else 0.0,
        "max_minimum_brackets": max(bracket_costs) if bracket_costs else 0,
    }


def _score_preorder(
    payload: tuple[PartialOrderGrammar, tuple[str, ...], tuple[bool, ...]]
) -> dict[str, Any]:
    """Refusal accounting for one preorder over the corpus.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    grammar, corpus, bearing_flags = payload
    refusals = 0
    true_refusals = 0
    over_refusals = 0
    silent = 0
    for source, bearing in zip(corpus, bearing_flags):
        try:
            partial_order_tree(source, grammar)
            if bearing:
                silent += 1
        except AmbiguousParse:
            refusals += 1
            if bearing:
                true_refusals += 1
            else:
                over_refusals += 1
    return {
        "grammar_id": grammar.id,
        "incomparable_pairs": grammar.incomparable_pair_count,
        "refusal_count": refusals,
        "true_refusal_count": true_refusals,
        "over_refusal_count": over_refusals,
        "silent_choice_count": silent,
    }


def partial_order_sweep(max_operators: int = 4, side: str = LEFT) -> dict[str, Any]:
    """The same refusal accounting over every operator word, not only a corpus.

    Words are the canonical ones of experiments 0020, 0023 and 0030: every word
    of length ``k`` over ``(+ - * /)`` with leaves ``a, b, c, ...``.

    ``side`` exists so the fixed-associativity restriction can be *observed*
    rather than argued about.  A refusal is raised only when two incomparable
    operators meet, and the side is consulted only when two operators are
    equivalent -- that is, on a branch where the parser is already going to
    accept.  So the refusal counts should not move when the side flips, and the
    tests check that they do not.
    """
    space = preorders(OPERATORS, side)
    strict = _cached_strict()
    rows = []
    for size in range(2, max_operators + 1):
        words = list(product(OPERATORS, repeat=size))
        leaves = canonical_leaves(size + 1)
        sources = [flat_source(leaves, word) for word in words]
        bearing = [
            len({canonical_tree(parse(source, grammar)) for grammar in strict}) > 1
            for source in sources
        ]
        cells = 0
        refusals = 0
        true_refusals = 0
        over_refusals = 0
        silent = 0
        for grammar in space:
            for source, choice in zip(sources, bearing):
                cells += 1
                try:
                    partial_order_tree(source, grammar)
                    if choice:
                        silent += 1
                except AmbiguousParse:
                    refusals += 1
                    if choice:
                        true_refusals += 1
                    else:
                        over_refusals += 1
        rows.append(
            {
                "operator_count": size,
                "word_count": len(words),
                "choice_bearing_words": sum(1 for flag in bearing if flag),
                "cell_count": cells,
                "refusal_count": refusals,
                "refusal_rate": refusals / cells,
                "true_refusal_count": true_refusals,
                "over_refusal_count": over_refusals,
                "silent_choice_count": silent,
                "refusal_precision": true_refusals / refusals if refusals else 0.0,
            }
        )
    cells = sum(row["cell_count"] for row in rows)
    refusals = sum(row["refusal_count"] for row in rows)
    true_refusals = sum(row["true_refusal_count"] for row in rows)
    return {
        "max_operators": max_operators,
        "side": side,
        "preorder_count": len(space),
        "levels": rows,
        "cell_count": cells,
        "refusal_count": refusals,
        "refusal_rate": refusals / cells,
        "true_refusal_count": true_refusals,
        "over_refusal_count": sum(row["over_refusal_count"] for row in rows),
        "silent_choice_count": sum(row["silent_choice_count"] for row in rows),
        "refusal_precision": true_refusals / refusals if refusals else 0.0,
    }


# --------------------------------------------------------------------------
# The null model
# --------------------------------------------------------------------------

_KEY_CACHE: dict[Tree, tuple[str, str, tuple[str, ...]]] = {}


def semantic_key(tree: Tree) -> tuple[str, str, tuple[str, ...]]:
    """The project's ``(canonical, domain, excluded points)`` key, keyed by tree.

    ``domain`` is carried unchanged because the project's key carries it, and
    it is **inert**: ``parseatlas.canonical.canonicalize`` writes the literal
    ``"R"`` for every expression (``NF-2026-00005``), so the operative
    discrimination is ``(canonical form, excluded points)``.
    """
    if tree in _KEY_CACHE:
        return _KEY_CACHE[tree]
    node = _tree_to_node(tree)
    canonical = canonicalize(node)
    key = (canonical["expression"], canonical["domain"], tuple(canonical["excluded_points"]))
    _KEY_CACHE[tree] = key
    return key


def _tree_to_node(tree: Tree) -> Node:
    from fractions import Fraction

    from .parser import Number, Variable

    if isinstance(tree, str):
        try:
            return Number(Fraction(tree))
        except ValueError:
            return Variable(tree)
    operator, left, right = tree  # type: ignore[misc]
    return Binary(operator, _tree_to_node(left), _tree_to_node(right))


def _support(source: str) -> tuple[str, ...]:
    return tuple(sorted({token.value for token in tokenize(source) if token.kind == "operator"}))


def _null_model_source(source: str) -> dict[str, Any]:
    """Class counts for one source in all three spaces.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    strict = _cached_strict()
    extended = _cached_associativity_space()
    space = _cached_representatives(len(OPERATORS))
    precedence = {canonical_tree(parse(source, grammar)) for grammar in strict}
    associative = {associative_tree(source, grammar) for grammar in extended}
    vector = {vector_tree(source, grammar) for grammar in space}
    precedence_classes = {semantic_key(tree) for tree in precedence}
    associative_classes = {semantic_key(tree) for tree in associative}
    vector_classes = {semantic_key(tree) for tree in vector}
    return {
        "source": source,
        "support": list(_support(source)),
        "support_size": len(_support(source)),
        "precedence_forms": len(precedence),
        "associativity_forms": len(associative),
        "vector_forms": len(vector),
        "precedence_classes": len(precedence_classes),
        "associativity_classes": len(associative_classes),
        "vector_classes": len(vector_classes),
        "new_classes_over_associativity": len(vector_classes - associative_classes),
        "new_classes_over_precedence": len(vector_classes - precedence_classes),
        "vector_contains_associativity_classes": associative_classes <= vector_classes,
    }


def new_object_witnesses(
    sources: Iterable[str], limit: int = 3
) -> tuple[dict[str, Any], ...]:
    """Name the objects the second dimension buys, with the vector that buys them.

    A negative or a positive count is only as good as the witness behind it, so
    each record carries the source, the vector grammar, the tree it produces and
    the canonical form of the class that the ``precedence x associativity``
    registry never reaches.
    """
    extended = _cached_associativity_space()
    space = _cached_representatives(len(OPERATORS))
    out = []
    for source in sources:
        associative = {associative_tree(source, grammar) for grammar in extended}
        known = {semantic_key(tree) for tree in associative}
        found: list[dict[str, Any]] = []
        for grammar in space:
            tree = vector_tree(source, grammar)
            key = semantic_key(tree)
            if key in known:
                continue
            known.add(key)
            found.append(
                {
                    "source": source,
                    "vector": {
                        operator: [left, right] for operator, left, right in grammar.powers
                    },
                    "tree": tree,
                    "canonical": key[0],
                    "excluded_points": list(key[2]),
                }
            )
            if len(found) >= limit:
                break
        out.extend(found)
    return tuple(out)


def null_model(
    corpora: Mapping[str, Sequence[str]] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """How many distinct mathematical objects does the second dimension buy?

    The object is the project's semantic class, not the AST.  Counts are
    reported per corpus and **stratified by operator support**, because a
    larger space makes a null model easier to pass by accident: a count that
    rises with the space is the space until the stratification shows it rising
    inside a fixed support.
    """
    families: Mapping[str, Sequence[str]] = corpora or {
        "0017 corpus": TEMPLATE_CORPUS,
        "0020 corpus": COVERAGE_CORPUS,
        "0024 restriction probe": PROBE_CORPUS,
        "chain probe": CHAIN_CORPUS,
    }
    tasks = [(name, source) for name, sources in families.items() for source in sources]
    worker_count = resolve_task_workers(len(tasks), workers)
    if worker_count == 1:
        records = [(name, _null_model_source(source)) for name, source in tasks]
    else:
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            computed = list(pool.map(_null_model_source, [source for _, source in tasks]))
        records = [(name, record) for (name, _), record in zip(tasks, computed)]

    by_corpus: dict[str, dict[str, Any]] = {}
    by_support: dict[tuple[str, ...], dict[str, Any]] = {}
    for name, record in records:
        bucket = by_corpus.setdefault(
            name,
            {
                "corpus": name,
                "expression_count": 0,
                "precedence_forms": 0,
                "associativity_forms": 0,
                "vector_forms": 0,
                "precedence_classes": 0,
                "associativity_classes": 0,
                "vector_classes": 0,
                "sources_with_new_class": 0,
                "new_classes": 0,
            },
        )
        bucket["expression_count"] += 1
        for field in (
            "precedence_forms",
            "associativity_forms",
            "vector_forms",
            "precedence_classes",
            "associativity_classes",
            "vector_classes",
        ):
            bucket[field] += record[field]
        bucket["new_classes"] += record["new_classes_over_associativity"]
        if record["new_classes_over_associativity"]:
            bucket["sources_with_new_class"] += 1

        support = tuple(record["support"])
        stratum = by_support.setdefault(
            support,
            {
                "support": list(support),
                "support_size": len(support),
                "expression_count": 0,
                "precedence_classes": 0,
                "associativity_classes": 0,
                "vector_classes": 0,
                "new_classes": 0,
            },
        )
        stratum["expression_count"] += 1
        stratum["precedence_classes"] += record["precedence_classes"]
        stratum["associativity_classes"] += record["associativity_classes"]
        stratum["vector_classes"] += record["vector_classes"]
        stratum["new_classes"] += record["new_classes_over_associativity"]

    total_new = sum(record["new_classes_over_associativity"] for _, record in records)
    total_new_over_precedence = sum(
        record["new_classes_over_precedence"] for _, record in records
    )
    return {
        "workers": worker_count,
        "expression_count": len(records),
        "corpora": [by_corpus[name] for name in families if name in by_corpus],
        "strata": [by_support[key] for key in sorted(by_support)],
        "new_classes_over_associativity": total_new,
        "new_classes_over_precedence": total_new_over_precedence,
        "sources_with_new_class": sum(
            1 for _, record in records if record["new_classes_over_associativity"]
        ),
        "second_dimension_buys_nothing": total_new == 0,
        "expressions": [record for _, record in records],
    }


def core_count() -> int:
    """The observed core count, never a hardcoded constant."""
    return os.cpu_count() or 1
