"""Experiment 0046: what survives all 25 worlds, and what it costs to survive.

The README has asked one question since the first day -- *find the quantities that stay unchanged
while the grammar changes* -- and the repository has never answered it as a question in its own
right.  This module answers it, and it keeps two different questions apart, because mixing them is
the way this question is usually got wrong.

``axis 1``  fix the 25 worlds, vary the WRITING.  Which source strings are read identically by
            every world?
``axis 2``  fix the writing, vary the WORLD.  Which measured quantities do not move even when the
            denoted object does?
``axis 3``  fix the OBJECT.  What does a writing all 25 worlds agree on cost, and what does that
            cost buy away?

Axis 1 is about strings.  Axis 2 is about numbers taken off a string.  A statement true on one axis
says nothing about the other, and every function, field and report key below carries its axis in
its name or its docstring.

Axis 1, and the shape of the answer
-----------------------------------

A *word* here is a bracket-free source over the four operators with distinct leaves --
``a + b * c`` is the word ``"+*"``.  Distinct leaves are what make the word and the parse the same
object: with the leaves all different, two parses are equal exactly when the operator sequences
were bracketed the same way.

Thesis T6 gives the obvious sufficient condition: parsing depends only on the precedence order
restricted to the operators that actually occur, so a word using ONE operator is read the same
everywhere.  The question this module exists to settle is whether anything else survives.  Nothing
does, and the reason is constructive:

    Take any position where two adjacent operators differ, ``... a_k  x  a_{k+1}  y  a_{k+2} ...``
    with ``x != y``.  The leaf between them ends up as the right child of the ``x`` node when ``x``
    binds tighter, and as the left child of the ``y`` node when ``y`` does.  Both orders are
    realised among the 24 strict grammars, and the leaves are distinct, so the two trees differ.

So a word is world-invariant **iff its operator support has size at most one**, and every word that
fails the condition comes with an explicit pair of worlds that disagree, computable in one pass.
:func:`witness_pair` builds that pair and :func:`axis1_report` checks it on every word it
enumerates rather than trusting the argument.

The null model, which is the main risk on axis 1
------------------------------------------------

Most short words have small operator support and are invariant for that reason alone.  A pooled
"``n`` percent of words are invariant" is therefore a statement about the length bound, not about
precedence: raise the bound and the number falls, with nothing about the worlds having changed.
Every rate this module reports is computed **inside a support stratum**, and the stratum sizes are
cross-checked against the closed form ``C(4, k) * surj(n, k)`` so that the enumeration is known to
be complete rather than assumed to be.

Axis 2, and what "invariant by construction" costs
--------------------------------------------------

Experiment 0021 found that the raw operation multiset is the same in all 25 worlds while
critical-path depth is not.  That is reproduced here as the calibration case -- and it is also the
warning.  The operation multiset cannot change, because the tokenizer never sees the grammar and
the parser makes exactly one ``Binary`` per operator token.  It is a restatement of how parsing
works, and a restatement is worth nothing as a discovery.  :data:`QUANTITIES` therefore labels
every quantity ``by_construction`` or ``measured`` **in advance**, and
:func:`axis2_report` reports the two groups separately and never pools them.

Axis 3: the hypothesis this card exists to test
-----------------------------------------------

Experiment 0040 found exactly one of twelve named curves invariant across all 25, ``(x - y) *
(x + y)``, and observed that it is invariant because it is already factored.  The manager's
hypothesis from that single case:

    invariance is bought with brackets, and the price is the structure you give up choosing

The first half is exact and this module computes the price.  :func:`invariant_surface` writes a
tree with the brackets EVERY world requires -- a right child that is a ``Binary`` always needs one,
a left child needs one exactly when its operator differs from its parent's -- and
:func:`invariant_minimality_witnesses` proves each of those brackets load-bearing by deleting it
and finding a world that then reads a different tree.

The second half is where the hypothesis has to be tested rather than assumed, and the answer
depends on a regime that experiment 0038 declared and this module imports rather than reinvents.
Under 0038's primary ``transparent`` regime a bracket is punctuation -- the native reader parses
with their own grammar and recovers the tree for free -- so the manifest set of a fixed tree does
not depend on how much of it is bracketed.  Under the ``opaque`` robustness regime a bracket hides
what is inside it.  Both are measured here, and they do not agree.

What is imported and never restated
-----------------------------------

* the 25 worlds are :func:`parseatlas.grammar.all_grammars` -- the tied control ``G0`` plus the 24
  strict orderings, the same registry the whole repository uses;
* the parse is :func:`parseatlas.parser.parse` and the semantic key is
  :func:`parseatlas.alternative_mathematics.semantic_key`, used unchanged;
* the corpus of objects is :data:`parseatlas.manifest_properties.CORPUS` -- 0037's named laws plus
  0038's calibration quadratic -- imported whole, with its declared principal variables;
* the bracket rule and the round trip are :func:`parseatlas.notational_cost.parenthesis_cost`,
  which renders through :func:`~parseatlas.notational_cost.render` and reparses its own output, and
  the per-world rule :func:`~parseatlas.notational_cost.needs_brackets` that this module quantifies
  over all 25 worlds;
* ``peak_live`` is :func:`parseatlas.memory_ceiling.peak_live`, the Sethi-Ullman register number;
* the manifest vocabulary is :data:`parseatlas.manifest_properties.PROPERTIES` with its two
  regimes, applied to a surface tree this module builds under a different bracket rule.

Standing disclosure carried from the repository: the ``domain`` component of the project's semantic
key is inert (``NF-2026-00005``) -- :func:`parseatlas.canonical.canonicalize` writes ``"R"`` for
every expression -- so the operative discrimination is ``(canonical form, excluded points)``.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from math import comb, factorial
from typing import Any

from sympy import Add, Poly, Symbol, cancel, expand, fraction, together
from sympy.polys.polyerrors import PolynomialError

from .alternative_mathematics import semantic_key
from .canonical import canonicalize, operation_cost
from .grammar import OPERATORS, Grammar, all_grammars, control_grammar, strict_grammars
from .manifest_properties import (
    CORPUS as OBJECT_CORPUS,
)
from .manifest_properties import (
    PROPERTIES,
    Atom,
    Group,
    MathObject,
    Op,
    Surface,
    Writing,
    bracket_count,
    chosen_writing,
    manifest_set,
    object_tree,
    surface_text,
)
from .memory_ceiling import peak_live
from .notational_cost import bracket_pairs, parenthesis_cost
from .parser import Binary, Node, Number, Variable, parse
from .tokenizer import tokenize

__all__ = [
    "AXIS2_CORPUS",
    "CELL_SECONDS",
    "CHAIN_SOURCES",
    "CONTROL",
    "CRITICAL_PATH_SOURCES",
    "Entry",
    "FIRST_ABOVE",
    "GRAMMARS",
    "KINDS",
    "LEAVES",
    "OBJECT_CORPUS",
    "OPERATORS",
    "POOL_STARTUP_SECONDS",
    "PRICE_SECONDS",
    "QUANTITIES",
    "QUANTITY_NAMES",
    "Quantity",
    "REGIMES",
    "STRICT",
    "WORD_CHUNK",
    "WORD_SECONDS",
    "WORKER_CAP",
    "WORKER_HEADROOM_CORES",
    "axis1_report",
    "axis2_report",
    "chain_supports",
    "cell_values",
    "default_worker_count",
    "enumerate_words",
    "invariant_cost",
    "invariant_minimality_witnesses",
    "invariant_surface",
    "invariant_writing",
    "invariants_report",
    "is_invariant",
    "leaf_parent",
    "measure_pool_startup",
    "parallel_decision",
    "predicted_invariant",
    "predicted_invariant_source",
    "price_report",
    "should_parallelise",
    "source_invariance_audit",
    "source_is_invariant",
    "stratum_sizes",
    "surjections",
    "tree_key",
    "witness_pair",
    "word_at",
    "word_count",
    "word_source",
    "words_of_length",
    "worker_count_for",
    "world_trees",
]

#: The 25 worlds: the tied control ``G0`` plus the 24 strict orderings, imported unchanged.
GRAMMARS: tuple[Grammar, ...] = all_grammars()

#: The 24 strict orderings alone, so that "``G0`` reaches a tree no strict grammar reaches" can be
#: asked as a question instead of assumed either way.
STRICT: tuple[Grammar, ...] = strict_grammars()

#: The conventional tied grammar.  It is the control everywhere in this repository.
CONTROL: Grammar = control_grammar()

GRAMMAR_BY_ID: dict[str, Grammar] = {grammar.id: grammar for grammar in GRAMMARS}

#: Leaf names for the enumerated words.  They are DISTINCT on purpose: with distinct leaves a word
#: and its parse determine each other, so "the 25 worlds read this word identically" is a statement
#: about the bracketing and about nothing else.  Repeating a leaf would let two different
#: bracketings produce equal trees for a reason that has nothing to do with precedence.
LEAVES: str = "abcdefghijklmnopqrstuvwxyz"

#: The two rule regimes of experiment 0038, imported by name so the two experiments cannot drift.
REGIMES: tuple[str, ...] = ("transparent", "opaque")


# =================================================================================== axis 1
#
# Which WRITINGS are read identically by all 25 worlds?


def word_source(word: str) -> str:
    """The bracket-free source string of a word: ``"+*"`` becomes ``"a + b * c"``.

    A word of length ``n`` uses ``n + 1`` distinct leaves, so the empty word is the bare leaf
    ``"a"`` -- a writing with no operators at all, which every world reads identically for a reason
    even weaker than T6's and which is counted in its own support-0 stratum rather than pooled.
    """
    if len(word) + 1 > len(LEAVES):
        raise ValueError(f"word of length {len(word)} needs more leaves than {len(LEAVES)!r} has")
    parts = [LEAVES[0]]
    for index, operator in enumerate(word):
        parts.append(operator)
        parts.append(LEAVES[index + 1])
    return " ".join(parts)


def tree_key(node: Node) -> Any:
    """A hashable identity for a parse tree.

    Invariance on axis 1 is decided by **tree identity**, not by value: ``a - b - c`` is read the
    same way by all 25 worlds and is still not value-associative.  This function is the identity
    that decision uses, and it descends into structure rather than comparing rendered text, so two
    trees are equal here exactly when the parser built the same nodes.
    """
    if isinstance(node, Binary):
        return (node.operator, tree_key(node.left), tree_key(node.right))
    if isinstance(node, Number):
        value = node.value
        return (
            str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
        )
    return node.name


def world_trees(word: str) -> dict[str, Any]:
    """The tree each of the 25 worlds reads out of ``word``, keyed by grammar id."""
    source = word_source(word)
    return {grammar.id: tree_key(parse(source, grammar)) for grammar in GRAMMARS}


def is_invariant(word: str) -> bool:
    """OBSERVED: do all 25 worlds read ``word`` as the same tree?

    This is the measurement.  :func:`predicted_invariant` is the characterisation being tested
    against it, and the two are kept in separate functions so that neither can be written in terms
    of the other.
    """
    return len(set(world_trees(word).values())) == 1


def predicted_invariant(word: str) -> bool:
    """The CHARACTERISATION: a word is world-invariant iff its operator support has size <= 1.

    Sufficiency is thesis T6 -- with one operator every grammar's restriction is the same one-element
    order, so every world builds the same left-associated chain.  Necessity is
    :func:`witness_pair`'s construction.  Nothing about this function may consult a parser; it is a
    predicate on the word.
    """
    return len(set(word)) <= 1


def leaf_parent(node: Node, leaf: str) -> tuple[str, str] | None:
    """Which operator node ``leaf`` hangs from, and on which side -- ``("*", "right")``.

    This is the quantity the necessity argument moves.  Naming it, and letting a test pin it on a
    hand-worked pair, is what keeps "the trees differ" from being a claim nobody checked the reason
    for.  Returns ``None`` when the leaf is the whole tree.
    """

    def walk(current: Node) -> tuple[str, str] | None:
        if not isinstance(current, Binary):
            return None
        if isinstance(current.left, Variable) and current.left.name == leaf:
            return (current.operator, "left")
        if isinstance(current.right, Variable) and current.right.name == leaf:
            return (current.operator, "right")
        return walk(current.left) or walk(current.right)

    return walk(node)


#: For each ordered pair of distinct operators, the first strict grammar in registry order that
#: puts the first above the second.  Precomputed because :func:`witness_pair` runs once per
#: enumerated word and a scan of 24 orderings there is the difference between a minute and ten.
FIRST_ABOVE: dict[tuple[str, str], str] = {
    (above, below): next(
        grammar.id
        for grammar in STRICT
        if grammar.precedence.index(above) < grammar.precedence.index(below)
    )
    for above in OPERATORS
    for below in OPERATORS
    if above != below
}


def witness_pair(word: str) -> tuple[str, str] | None:
    """Two worlds that provably disagree about ``word``, or ``None`` when none can exist.

    The construction is the necessity half of the characterisation.  Find the first position where
    two adjacent operators differ -- it exists exactly when the support has size at least two.  Call
    them ``x`` then ``y``.  The leaf between them attaches to whichever binds tighter, so a world
    with ``x`` above ``y`` makes it the right child of an ``x`` node and a world with ``y`` above
    ``x`` makes it the left child of a ``y`` node.  The leaves are distinct, so those are different
    trees.  ANY strict grammar on each side of the order will do -- the relative order of ``x`` and
    ``y`` is the whole argument and the rest of the ordering never enters it -- so the first of each
    in registry order is returned and the witness is deterministic.
    """
    for index in range(len(word) - 1):
        left, right = word[index], word[index + 1]
        if left == right:
            continue
        return (FIRST_ABOVE[(left, right)], FIRST_ABOVE[(right, left)])
    return None


def chain_supports(source: str) -> tuple[frozenset[str], ...]:
    """The operator support of every maximal bracket-free chain in ``source``, outermost last.

    A bracket group is a primary: the parser recurses into it and the operators inside it never meet
    the operators outside it.  So a source decomposes into independent chains -- one per bracket
    group plus one for the top level -- and each chain is a bracket-free word over primaries rather
    than over leaves.  This function reads that decomposition straight off the token stream, without
    parsing, because the decomposition is a property of the writing and must not be taken from any
    one world's tree.
    """
    stack: list[set[str]] = [set()]
    closed: list[frozenset[str]] = []
    for token in tokenize(source):
        if token.kind == "left":
            stack.append(set())
        elif token.kind == "right":
            if len(stack) == 1:
                raise ValueError(f"unbalanced brackets in {source!r}")
            closed.append(frozenset(stack.pop()))
        elif token.kind == "operator":
            stack[-1].add(token.value)
    if len(stack) != 1:
        raise ValueError(f"unbalanced brackets in {source!r}")
    closed.append(frozenset(stack.pop()))
    return tuple(closed)


def predicted_invariant_source(source: str) -> bool:
    """The characterisation, generalised from bracket-free words to any writing.

    A writing is world-invariant iff **every maximal bracket-free chain in it uses at most one
    distinct operator**.  For a bracket-free source this is :func:`predicted_invariant` exactly; the
    brackets add nothing but more chains, each of which has to pass the same test.

    The proof of necessity in :func:`witness_pair` assumes the operands of a chain are pairwise
    distinct, which holds for the enumerated words by construction and does NOT hold for a corpus
    that writes ``a * a + b * b``.  So on real writings this is a prediction that has to be checked
    against a parse, and :func:`source_invariance_audit` checks it.
    """
    return all(len(support) <= 1 for support in chain_supports(source))


def source_is_invariant(source: str) -> bool:
    """OBSERVED: do all 25 worlds parse ``source`` to the same tree?"""
    return len({tree_key(parse(source, grammar)) for grammar in GRAMMARS}) == 1


def source_invariance_audit(sources: Sequence[str]) -> dict[str, Any]:
    """Check the generalised characterisation against the parser on real, bracketed writings.

    ``disagreements`` must be empty.  If it is not, the sources in it are the finding and the
    characterisation is wrong for bracketed writings -- which is a result about repeated operands,
    not a reason to weaken the statement.
    """
    unique = tuple(dict.fromkeys(sources))
    disagreements = tuple(
        (source, predicted_invariant_source(source), source_is_invariant(source))
        for source in unique
        if predicted_invariant_source(source) != source_is_invariant(source)
    )
    invariant = sum(1 for source in unique if source_is_invariant(source))
    return {
        "sources": len(unique),
        "checks": len(unique) * len(GRAMMARS),
        "invariant": invariant,
        "not_invariant": len(unique) - invariant,
        "disagreements": disagreements,
        "holds": not disagreements,
    }


def words_of_length(length: int) -> Iterable[str]:
    """Every word of exactly ``length`` operators, in base-4 index order."""
    for index in range(4**length):
        yield word_at(length, index)


def word_at(length: int, index: int) -> str:
    """The ``index``-th word of ``length`` operators, base-4 with ``OPERATORS`` as digits.

    Indexing rather than :func:`itertools.product` is what lets a worker process take a contiguous
    slice of the enumeration without receiving the words themselves, so the payload a pool ships is
    three integers instead of half a megabyte of strings.
    """
    digits = []
    for _ in range(length):
        digits.append(OPERATORS[index % 4])
        index //= 4
    return "".join(reversed(digits))


def enumerate_words(max_length: int) -> Iterable[str]:
    """Every word from the empty word up to ``max_length`` operators."""
    for length in range(max_length + 1):
        yield from words_of_length(length)


def word_count(max_length: int) -> int:
    """How many words the enumeration up to ``max_length`` contains: ``(4**(n+1) - 1) / 3``."""
    return (4 ** (max_length + 1) - 1) // 3


def surjections(length: int, size: int) -> int:
    """Sequences of ``length`` symbols using each of ``size`` given symbols at least once."""
    return sum((-1) ** i * comb(size, i) * (size - i) ** length for i in range(size + 1))


def stratum_sizes(max_length: int) -> dict[int, int]:
    """Closed-form stratum sizes: ``C(4, k) * surj(n, k)`` summed over ``n <= max_length``.

    The enumeration is checked against this rather than against itself.  A count that agrees with an
    independent formula is a count that is complete; a count that only agrees with the loop that
    produced it is a count of whatever that loop happened to visit.
    """
    sizes: dict[int, int] = {}
    for length in range(max_length + 1):
        for size in range(5):
            total = comb(4, size) * surjections(length, size)
            if total:
                sizes[size] = sizes.get(size, 0) + total
    return sizes


def _has_tied_pair(support: frozenset[str]) -> bool:
    """Does the support contain a whole ``G0`` level -- both of ``+ -`` or both of ``* /``?

    ``G0`` ties inside a level.  If the support avoids both tied pairs, ``G0``'s restriction to it
    is a strict total order, so by T6 ``G0`` reads the word exactly as some strict grammar does and
    the control cannot be reaching anything new.  That is a proof, and the enumeration checks it.
    """
    return frozenset("+-") <= support or frozenset("*/") <= support


def _word_record(word: str) -> dict[str, Any]:
    """Everything axis 1 asks of one word.  Pure, so a chunk of them parallelises trivially."""
    trees = world_trees(word)
    strict_trees = {trees[grammar.id] for grammar in STRICT}
    support = frozenset(word)
    blocks: dict[Any, int] = {}
    for value in trees.values():
        blocks[value] = blocks.get(value, 0) + 1
    witness = witness_pair(word)
    witness_holds = True
    if witness is not None:
        witness_holds = trees[witness[0]] != trees[witness[1]]
    return {
        "word": word,
        "support": support,
        "support_size": len(support),
        "invariant": len(set(trees.values())) == 1,
        "predicted": predicted_invariant(word),
        "distinct_strict_trees": len(strict_trees),
        "distinct_world_trees": len(set(trees.values())),
        "largest_block": max(blocks.values()),
        "control_is_new": trees["G0"] not in strict_trees,
        "has_tied_pair": _has_tied_pair(support),
        "witness": witness,
        "witness_holds": witness_holds,
    }


def _blank_totals() -> dict[str, Any]:
    return {
        "words": 0,
        "disagreements": [],
        "witness_failures": [],
        "by_support": {},
        "control_new_without_tied_pair": [],
    }


def _blank_stratum() -> dict[str, Any]:
    return {
        "words": 0,
        "invariant": 0,
        "control_new": 0,
        "bound_attained": 0,
        "distinct_strict": {},
        "distinct_world": {},
        "largest_block": {},
    }


def _accumulate(totals: dict[str, Any], record: dict[str, Any]) -> None:
    totals["words"] += 1
    size = record["support_size"]
    stratum = totals["by_support"].setdefault(size, _blank_stratum())
    stratum["words"] += 1
    stratum["invariant"] += int(record["invariant"])
    stratum["control_new"] += int(record["control_is_new"])
    bound = factorial(size) if size else 1
    stratum["bound_attained"] += int(record["distinct_strict_trees"] == bound)
    for field, value in (
        ("distinct_strict", record["distinct_strict_trees"]),
        ("distinct_world", record["distinct_world_trees"]),
        ("largest_block", record["largest_block"]),
    ):
        stratum[field][value] = stratum[field].get(value, 0) + 1
    if record["invariant"] != record["predicted"]:
        totals["disagreements"].append((record["word"], size, record["distinct_world_trees"]))
    if not record["witness_holds"]:
        totals["witness_failures"].append((record["word"], record["witness"]))
    if record["control_is_new"] and not record["has_tied_pair"]:
        totals["control_new_without_tied_pair"].append(record["word"])


def _merge(into: dict[str, Any], other: dict[str, Any]) -> None:
    into["words"] += other["words"]
    into["disagreements"].extend(other["disagreements"])
    into["witness_failures"].extend(other["witness_failures"])
    into["control_new_without_tied_pair"].extend(other["control_new_without_tied_pair"])
    for size, stratum in other["by_support"].items():
        target = into["by_support"].setdefault(size, _blank_stratum())
        for scalar in ("words", "invariant", "control_new", "bound_attained"):
            target[scalar] += stratum[scalar]
        for field in ("distinct_strict", "distinct_world", "largest_block"):
            for value, count in stratum[field].items():
                target[field][value] = target[field].get(value, 0) + count


#: Words per parallel chunk.  Sized from the measured per-word cost so a chunk is a few tenths of a
#: second: small enough that the tail of the map does not idle the pool, large enough that the
#: payload -- three integers -- is negligible against the work it names.
WORD_CHUNK: int = 512


def _word_chunk(payload: tuple[int, int, int]) -> dict[str, Any]:
    """One contiguous slice of the enumeration, reduced to counters that merge associatively."""
    length, start, stop = payload
    totals = _blank_totals()
    for index in range(start, stop):
        _accumulate(totals, _word_record(word_at(length, index)))
    return totals


def _word_payloads(max_length: int) -> tuple[tuple[int, int, int], ...]:
    payloads = []
    for length in range(max_length + 1):
        total = 4**length
        for start in range(0, total, WORD_CHUNK):
            payloads.append((length, start, min(start + WORD_CHUNK, total)))
    return tuple(payloads)


def axis1_report(max_length: int = 8, workers: int | None = None) -> dict[str, Any]:
    """AXIS 1: which writings are read identically by all 25 worlds, up to ``max_length``.

    The headline is the characterisation, and it is reported as a disagreement count rather than as
    a rate: ``disagreements`` lists every word where ``support <= 1`` and the 25 worlds disagree, or
    where the support is larger and they agree.  It must be empty, and if it is not, the words in it
    are the finding.

    Everything else is stratified by support size.  A pooled invariance rate over this enumeration
    would be a statement about ``max_length`` -- lengthen the words and it falls, with nothing about
    the worlds having changed.
    """
    payloads = _word_payloads(max_length)
    chunks = _map_word_chunks(payloads, workers)
    totals = _blank_totals()
    for chunk in chunks:
        _merge(totals, chunk)

    expected = stratum_sizes(max_length)
    strata = {}
    for size in sorted(totals["by_support"]):
        stratum = totals["by_support"][size]
        strata[size] = {
            "words": stratum["words"],
            "invariant": stratum["invariant"],
            "invariance_rate": stratum["invariant"] / stratum["words"],
            "expected_words": expected.get(size, 0),
            "size_matches_closed_form": stratum["words"] == expected.get(size, 0),
            "t6_upper_bound": factorial(size) if size else 1,
            "bound_attained": stratum["bound_attained"],
            "bound_attainment_rate": stratum["bound_attained"] / stratum["words"],
            "distinct_strict_trees": dict(sorted(stratum["distinct_strict"].items())),
            "distinct_world_trees": dict(sorted(stratum["distinct_world"].items())),
            "largest_block": dict(sorted(stratum["largest_block"].items())),
            "control_reaches_new_tree": stratum["control_new"],
        }
    invariant_total = sum(item["invariant"] for item in strata.values())
    return {
        "max_length": max_length,
        "word_count": totals["words"],
        "expected_word_count": word_count(max_length),
        "world_count": len(GRAMMARS),
        "parse_count": totals["words"] * len(GRAMMARS),
        "characterisation": "world-invariant iff the operator support has size at most 1",
        "disagreements": tuple(totals["disagreements"]),
        "disagreement_count": len(totals["disagreements"]),
        "characterisation_holds": not totals["disagreements"],
        "witness_failures": tuple(totals["witness_failures"]),
        "witness_failure_count": len(totals["witness_failures"]),
        "witnesses_hold": not totals["witness_failures"],
        "strata": strata,
        "invariant_words": invariant_total,
        "pooled_invariance_rate": invariant_total / totals["words"],
        "control_reaches_new_tree": sum(
            item["control_reaches_new_tree"] for item in strata.values()
        ),
        "control_new_without_tied_pair": tuple(totals["control_new_without_tied_pair"]),
        "control_new_needs_tied_pair": not totals["control_new_without_tied_pair"],
        "strata_match_closed_form": all(item["size_matches_closed_form"] for item in strata.values()),
    }


# =================================================================================== axis 2
#
# Which measurable QUANTITIES are constant across the worlds, with the writing held fixed?


#: The two kinds of invariance, declared before anything is measured.
#:
#: ``by_construction``  the quantity CANNOT move, and the reason is the shape of the parser rather
#:                      than anything about precedence.  Reporting one of these as a discovery is
#:                      reporting that parsing consumes each token once.
#: ``measured``         the quantity could move for all the parser's shape says, so whether it does
#:                      is an observation.
KINDS: tuple[str, ...] = ("by_construction", "measured")


@dataclass(frozen=True)
class Quantity:
    """One measurable property of a parse, with its kind declared in advance.

    ``measure`` is handed the source, the tree, the canonical record and the declared principal
    variable, and returns something hashable or ``None`` for "does not apply to this entry".  A
    ``None`` is never counted as agreement: :func:`axis2_report` drops non-applicable entries from
    the denominator instead of scoring them as invariant.
    """

    name: str
    kind: str
    note: str
    reason: str
    measure: Any


@dataclass(frozen=True)
class Entry:
    """One axis-2 corpus entry: a fixed source, its declared principal variable, and its origin."""

    name: str
    source: str
    variable: str | None
    origin: str


def _leaf_text(node: Node) -> str:
    if isinstance(node, Number):
        value = node.value
        return (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        )
    if isinstance(node, Variable):
        return node.name
    raise TypeError(f"not a leaf: {node!r}")


def _leaves(node: Node) -> tuple[str, ...]:
    if not isinstance(node, Binary):
        return (_leaf_text(node),)
    return _leaves(node.left) + _leaves(node.right)


def _q_token_count(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return len(tokenize(source)) - 1  # the trailing eof token is not part of the writing


def _q_leaf_multiset(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return tuple(sorted(_leaves(tree)))


def _q_operator_multiset(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    cost = operation_cost(tree)
    return tuple((key, cost[key]) for key in ("add", "sub", "mul", "div"))


def _q_node_count(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return operation_cost(tree)["nodes"]


def _q_parse_tree(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return tree_key(tree)


def _q_critical_path_depth(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return operation_cost(tree)["depth"]


def _q_peak_live(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return peak_live(tree)


def _q_canonical_form(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return semantic_key(canonical)


def _q_excluded_points(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return tuple(canonical["excluded_points"])


def _q_defined_everywhere(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return not canonical["excluded_points"]


def _q_free_symbols(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return tuple(sorted(str(symbol) for symbol in canonical["sympy_expression"].free_symbols))


def _q_total_degree(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    expression = canonical["sympy_expression"]
    symbols = sorted(expression.free_symbols, key=str)
    if not symbols:
        return 0
    try:
        polynomial = Poly(expression, *symbols)
    except (PolynomialError, TypeError, ValueError):
        return None
    return int(polynomial.total_degree())


def _q_polynomial_degree(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    if variable is None:
        return None
    expression = canonical["sympy_expression"]
    symbol = Symbol(variable, real=True)
    if symbol not in expression.free_symbols:
        return None
    try:
        polynomial = Poly(expression, symbol)
    except (PolynomialError, TypeError, ValueError):
        return None
    return int(polynomial.degree())


def _numerator_denominator(expression: Any) -> tuple[Any, Any]:
    return fraction(cancel(together(expression)))


def _q_root_count(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    """Zeros over ``C`` in the principal variable, counted with multiplicity.

    Defined as the degree of the cancelled numerator rather than as the length of a solver's answer:
    over ``C`` the two agree by the fundamental theorem of algebra, and the degree is exact for
    symbolic coefficients where a solver is not.
    """
    if variable is None:
        return None
    expression = canonical["sympy_expression"]
    symbol = Symbol(variable, real=True)
    if symbol not in expression.free_symbols:
        return None
    numerator, _denominator = _numerator_denominator(expression)
    try:
        return int(Poly(numerator, symbol).degree())
    except (PolynomialError, TypeError, ValueError):
        return None


def _q_pole_count(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    """Poles in the principal variable, counted with multiplicity, after cancellation."""
    if variable is None:
        return None
    expression = canonical["sympy_expression"]
    symbol = Symbol(variable, real=True)
    _numerator, denominator = _numerator_denominator(expression)
    try:
        return int(Poly(denominator, symbol).degree())
    except (PolynomialError, TypeError, ValueError):
        return None


def _q_expanded_term_count(source: str, tree: Node, canonical: dict[str, Any], variable: str | None) -> Any:
    return len(Add.make_args(expand(canonical["sympy_expression"])))


QUANTITIES: tuple[Quantity, ...] = (
    Quantity(
        name="token_count",
        kind="by_construction",
        note="how many tokens the writing has",
        reason=(
            "the tokenizer never receives a grammar, so this number is a property of the string "
            "and the parse does not enter it at all"
        ),
        measure=_q_token_count,
    ),
    Quantity(
        name="leaf_multiset",
        kind="by_construction",
        note="the multiset of leaf tokens in the tree",
        reason=(
            "the parser emits exactly one leaf node per number or name token and never invents or "
            "drops one, so the multiset is fixed by the writing"
        ),
        measure=_q_leaf_multiset,
    ),
    Quantity(
        name="operator_multiset",
        kind="by_construction",
        note="0021's raw operation multiset: add, sub, mul, div",
        reason=(
            "one Binary node per operator token, labelled by that token; precedence chooses the "
            "node's children and never its label, so the counts are fixed by the writing"
        ),
        measure=_q_operator_multiset,
    ),
    Quantity(
        name="node_count",
        kind="by_construction",
        note="tree size, leaves included",
        reason=(
            "a binary tree with k operator nodes has k+1 leaves, so node_count = 2k+1 is a function "
            "of the operator count and carries no information that quantity does not"
        ),
        measure=_q_node_count,
    ),
    Quantity(
        name="parse_tree",
        kind="measured",
        note="the tree itself, by tree identity -- this is axis 1 asked of one writing",
        reason="",
        measure=_q_parse_tree,
    ),
    Quantity(
        name="critical_path_depth",
        kind="measured",
        note="0021's depth: a leaf is 1, a Binary is max(children) + 1",
        reason="",
        measure=_q_critical_path_depth,
    ),
    Quantity(
        name="peak_live",
        kind="measured",
        note="Sethi-Ullman register number: simultaneously live intermediate values",
        reason="",
        measure=_q_peak_live,
    ),
    Quantity(
        name="semantic_key",
        kind="measured",
        note="the project's (canonical form, domain, excluded points); domain is inert",
        reason="",
        measure=_q_canonical_form,
    ),
    Quantity(
        name="excluded_points",
        kind="measured",
        note="the points at which the writing is undefined",
        reason="",
        measure=_q_excluded_points,
    ),
    Quantity(
        name="defined_everywhere",
        kind="measured",
        note="whether the expression has no excluded points at all",
        reason="",
        measure=_q_defined_everywhere,
    ),
    Quantity(
        name="free_symbols",
        kind="measured",
        note="the variables surviving in the canonical form",
        reason="",
        measure=_q_free_symbols,
    ),
    Quantity(
        name="total_degree",
        kind="measured",
        note="total degree of the canonical form over all its symbols, None when not polynomial",
        reason="",
        measure=_q_total_degree,
    ),
    Quantity(
        name="polynomial_degree",
        kind="measured",
        note="degree in the declared principal variable, None when not polynomial in it",
        reason="",
        measure=_q_polynomial_degree,
    ),
    Quantity(
        name="root_count",
        kind="measured",
        note="zeros over C in the principal variable, with multiplicity",
        reason="",
        measure=_q_root_count,
    ),
    Quantity(
        name="pole_count",
        kind="measured",
        note="poles in the principal variable, with multiplicity, after cancellation",
        reason="",
        measure=_q_pole_count,
    ),
    Quantity(
        name="expanded_term_count",
        kind="measured",
        note="how many terms the expanded canonical form has",
        reason="",
        measure=_q_expanded_term_count,
    ),
)

QUANTITY_NAMES: tuple[str, ...] = tuple(item.name for item in QUANTITIES)

QUANTITY_BY_NAME: dict[str, Quantity] = {item.name: item for item in QUANTITIES}


#: Experiment 0021's six expressions, restated here because 0021 left them in its report and its
#: tests rather than in an importable constant.  They are the calibration case: the raw operation
#: multiset was invariant over them and critical-path depth was not, and this module has to
#: reproduce that before it is allowed to sweep anything wider.
CRITICAL_PATH_SOURCES: tuple[tuple[str, str, str | None], ...] = (
    ("cp_linear", "2*t + 1 - t/2", "t"),
    ("cp_mixed", "a + b*c - d/e", "a"),
    ("cp_quadratic", "2*x*x + 1 - x/2", "x"),
    ("cp_four_term", "a - b*c + d/e - f", "a"),
    ("cp_five_term", "a/b + c*d - e/f + g", "a"),
    ("cp_rational", "(x + 1)/(x - 2)", "x"),
)

#: Single-operator chains: the null model on axis 2.  Their support has size one, so axis 1 already
#: says every world reads them identically, and therefore EVERY quantity is constant on them.  They
#: are in the corpus so the report can show what a frozen entry does to a pooled rate, and they are
#: excluded from every rate computed over the movable entries.
CHAIN_SOURCES: tuple[tuple[str, str, str | None], ...] = (
    ("chain_add", "a + b + c + d", "a"),
    ("chain_sub", "a - b - c - d", "a"),
    ("chain_mul", "a * b * c * d", "a"),
    ("chain_div", "a / b / c / d", "a"),
)


def _axis2_corpus() -> tuple[Entry, ...]:
    entries = [
        Entry(name, source, variable, "0021")
        for name, source, variable in CRITICAL_PATH_SOURCES
    ]
    entries.extend(
        Entry(f"{item.name}.{writing.role}", writing.source, item.variable, "0038")
        for item in OBJECT_CORPUS
        for writing in item.writings
    )
    entries.extend(
        Entry(name, source, variable, "0046") for name, source, variable in CHAIN_SOURCES
    )
    return tuple(entries)


#: The axis-2 corpus: 0021's six, 0038's fifty declared writings, and four single-operator chains.
AXIS2_CORPUS: tuple[Entry, ...] = _axis2_corpus()

ENTRY_BY_NAME: dict[str, Entry] = {entry.name: entry for entry in AXIS2_CORPUS}


def _support_of(source: str) -> frozenset[str]:
    return frozenset(token.value for token in tokenize(source) if token.kind == "operator")


def cell_values(entry: Entry, grammar: Grammar) -> dict[str, Any]:
    """Every quantity of one (writing, world) cell.

    The canonical record is computed once and shared by the quantities that need it; the parse is
    computed once and shared by all of them.  Nothing is cached across cells: every cell is parsed
    and canonicalised on its own, so the grid is an OBSERVATION of 25 worlds rather than a
    derivation from the smaller number of distinct trees they produce.  A T6 dedup would be exact --
    every quantity here is a function of the tree -- and it is deliberately not taken.
    """
    tree = parse(entry.source, grammar)
    canonical = canonicalize(tree)
    return {
        item.name: item.measure(entry.source, tree, canonical, entry.variable)
        for item in QUANTITIES
    }


def _cell(payload: tuple[str, str]) -> tuple[str, str, dict[str, Any]]:
    entry_name, grammar_id = payload
    values = cell_values(ENTRY_BY_NAME[entry_name], GRAMMAR_BY_ID[grammar_id])
    return (entry_name, grammar_id, {name: repr(value) for name, value in values.items()})


def axis2_report(
    corpus: Sequence[Entry] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """AXIS 2: which quantities stay constant over the 25 worlds with the writing held fixed.

    Every entry is classified ``frozen`` (operator support of size at most one, so axis 1 already
    guarantees one tree and therefore one value of everything) or ``movable``.  Rates are computed
    over the movable entries only.  A quantity that is constant on a frozen entry has told you
    about the entry, not about the quantity.

    The three groups the card asks for are ``always``, ``sometimes`` and ``never``: constant on
    every movable entry where it applies, on some, on none.  They are reported inside each kind,
    never pooled across the two, because a ``by_construction`` quantity is in ``always`` by
    definition and would otherwise inflate the group that matters.
    """
    corpus = tuple(corpus) if corpus is not None else AXIS2_CORPUS
    payloads = tuple(
        (entry.name, grammar.id) for entry in corpus for grammar in GRAMMARS
    )
    cells = _map_cells(payloads, workers)

    grid: dict[str, dict[str, dict[str, Any]]] = {}
    for entry_name, grammar_id, values in cells:
        grid.setdefault(entry_name, {})[grammar_id] = values

    movable = {entry.name: len(_support_of(entry.source)) > 1 for entry in corpus}
    entries: dict[str, Any] = {}
    per_quantity: dict[str, dict[str, Any]] = {
        name: {"constant": [], "varies": [], "not_applicable": []} for name in QUANTITY_NAMES
    }
    for entry in corpus:
        row = grid[entry.name]
        record: dict[str, Any] = {
            "source": entry.source,
            "origin": entry.origin,
            "variable": entry.variable,
            "support": tuple(sorted(_support_of(entry.source))),
            "movable": movable[entry.name],
            "quantities": {},
        }
        for name in QUANTITY_NAMES:
            values = [row[grammar.id][name] for grammar in GRAMMARS]
            applicable = any(value != repr(None) for value in values)
            distinct = len(set(values))
            record["quantities"][name] = {
                "distinct": distinct,
                "constant": distinct == 1,
                "applicable": applicable,
            }
            bucket = per_quantity[name]
            if not applicable:
                bucket["not_applicable"].append(entry.name)
            elif distinct == 1:
                bucket["constant"].append(entry.name)
            else:
                bucket["varies"].append(entry.name)
        entries[entry.name] = record

    summary: dict[str, Any] = {}
    for name in QUANTITY_NAMES:
        bucket = per_quantity[name]
        movable_constant = [item for item in bucket["constant"] if movable[item]]
        movable_varies = [item for item in bucket["varies"] if movable[item]]
        denominator = len(movable_constant) + len(movable_varies)
        if denominator == 0:
            group = "not_applicable"
        elif not movable_varies:
            group = "always"
        elif not movable_constant:
            group = "never"
        else:
            group = "sometimes"
        summary[name] = {
            "kind": QUANTITY_BY_NAME[name].kind,
            "group": group,
            "movable_entries": denominator,
            "movable_constant": len(movable_constant),
            "movable_varies": len(movable_varies),
            "constant_rate": (len(movable_constant) / denominator) if denominator else None,
            "not_applicable": len(bucket["not_applicable"]),
            "frozen_constant": len([item for item in bucket["constant"] if not movable[item]]),
            "varying_entries": tuple(sorted(movable_varies)),
        }

    groups: dict[str, dict[str, tuple[str, ...]]] = {
        kind: {
            group: tuple(
                name
                for name in QUANTITY_NAMES
                if summary[name]["kind"] == kind and summary[name]["group"] == group
            )
            for group in ("always", "sometimes", "never", "not_applicable")
        }
        for kind in KINDS
    }
    frozen_names = tuple(sorted(name for name, flag in movable.items() if not flag))
    return {
        "entry_count": len(corpus),
        "world_count": len(GRAMMARS),
        "cell_count": len(payloads),
        "movable_entries": sum(1 for flag in movable.values() if flag),
        "frozen_entries": len(frozen_names),
        "frozen_names": frozen_names,
        "entries": entries,
        "quantities": summary,
        "groups": groups,
        "calibration_0021": {
            name: {
                "operator_multiset_constant": entries[name]["quantities"]["operator_multiset"][
                    "constant"
                ],
                "critical_path_depth_distinct": entries[name]["quantities"][
                    "critical_path_depth"
                ]["distinct"],
            }
            for name, _source, _variable in CRITICAL_PATH_SOURCES
            if name in entries
        },
    }


# =================================================================================== axis 3
#
# The hypothesis: invariance is bought with brackets, and the price is the structure you give up
# choosing.


def invariant_surface(node: Node) -> Surface:
    """The writing of ``node`` that EVERY world reads back as ``node``, with the fewest brackets.

    The rule follows from :func:`parseatlas.notational_cost.needs_brackets` quantified over all 25
    worlds rather than applied to one:

    * a leaf never needs a bracket -- no precedence rule can split a single token;
    * a ``Binary`` **right** child always needs one.  Staying unbracketed there requires the child
      to bind strictly tighter than its parent, which is impossible when the operators are equal and
      fails in half the orderings when they differ;
    * a ``Binary`` **left** child needs one exactly when its operator differs from its parent's.
      Equal operators bind equally, which is enough on the left; different operators are ordered the
      wrong way round by some world.

    The result is a :class:`~parseatlas.manifest_properties.Surface`, the same structure 0038 reads
    its shape rules off, so the visibility half of the hypothesis can be asked of this writing with
    0038's vocabulary unchanged.
    """
    if not isinstance(node, Binary):
        return Atom(_leaf_text(node), "number" if isinstance(node, Number) else "variable")
    left: Surface = invariant_surface(node.left)
    if isinstance(node.left, Binary) and node.left.operator != node.operator:
        left = Group(left)
    right: Surface = invariant_surface(node.right)
    if isinstance(node.right, Binary):
        right = Group(right)
    return Op(node.operator, left, right)


def invariant_writing(node: Node) -> str:
    """The invariant writing as a string."""
    return surface_text(invariant_surface(node))


def invariant_cost(node: Node) -> int:
    """How many bracket pairs the invariant writing carries."""
    return bracket_count(invariant_surface(node))


def invariant_minimality_witnesses(node: Node) -> tuple[dict[str, Any], ...]:
    """For each bracket in the invariant writing, the world that needs it.

    Deleting the pair must make at least one of the 25 worlds read a different tree, or fail to
    parse at all.  A pair that survives deletion in every world is a bracket the invariant writing
    did not require, i.e. a defect in :func:`invariant_surface` -- so this is the check that turns
    "the fewest brackets" from a claim into a measurement.
    """
    text = invariant_writing(node)
    target = tree_key(node)
    witnesses = []
    for opening, closing in bracket_pairs(text):
        stripped = text[:opening] + text[opening + 1 : closing] + text[closing + 1 :]
        breaker = None
        for grammar in GRAMMARS:
            try:
                changed = tree_key(parse(stripped, grammar)) != target
            except ValueError:
                changed = True
            if changed:
                breaker = grammar.id
                break
        witnesses.append(
            {
                "pair": (opening, closing),
                "stripped": stripped,
                "required_by": breaker,
                "required": breaker is not None,
            }
        )
    return tuple(witnesses)


def _manifest_of_surface(written: Surface, opaque: bool, variable: str | None) -> tuple[str, ...]:
    """0038's vocabulary applied to a surface this module built, with no rule rewritten."""
    return tuple(item.name for item in PROPERTIES if item.shape(written, opaque, variable))


def _invariant_choice(item: MathObject) -> tuple[Writing, int]:
    """The writing an invariance-requiring world uses, and what it costs.

    The invariant cost of a tree does not depend on the grammar, so every one of the 25 worlds makes
    the same choice here.  Ties break on the object's declared writing order, which is exactly
    :func:`parseatlas.manifest_properties.chosen_writing`'s rule, so the two regimes are compared
    under one tie-break rather than two.
    """
    costs = {writing.role: invariant_cost(object_tree(writing)) for writing in item.writings}
    best = min(costs.values())
    for writing in item.writings:
        if costs[writing.role] == best:
            return writing, best
    raise AssertionError("unreachable")  # pragma: no cover


def _price_cell(item: MathObject) -> dict[str, Any]:
    """The whole hypothesis for one object.  Pure, so a pool could take it -- see the measurement."""
    free_roles: set[str] = set()
    free_sets: dict[str, set[tuple[str, ...]]] = {regime: set() for regime in REGIMES}
    free_sizes: dict[str, list[int]] = {regime: [] for regime in REGIMES}
    free_costs: list[int] = []
    control_cost = 0
    for grammar in GRAMMARS:
        writing = chosen_writing(item, grammar)
        tree = object_tree(writing)
        free_roles.add(writing.role)
        cost = parenthesis_cost(tree, grammar)
        free_costs.append(cost)
        if grammar.id == CONTROL.id:
            control_cost = cost
        for regime in REGIMES:
            found = manifest_set(tree, grammar, item.variable, regime == "opaque")
            free_sets[regime].add(found)
            free_sizes[regime].append(len(found))

    writing, cost = _invariant_choice(item)
    invariant_tree = object_tree(writing)
    written = invariant_surface(invariant_tree)
    invariant_sets = {
        regime: _manifest_of_surface(written, regime == "opaque", item.variable)
        for regime in REGIMES
    }

    # The per-WRITING comparison: same tree, cheapest world's rendering against the invariant one.
    per_writing = []
    for candidate in item.writings:
        tree = object_tree(candidate)
        costs = {grammar.id: parenthesis_cost(tree, grammar) for grammar in GRAMMARS}
        cheapest_id = min(costs, key=lambda key: (costs[key], key))
        cheap_surface_sets = {
            regime: manifest_set(
                tree, GRAMMAR_BY_ID[cheapest_id], item.variable, regime == "opaque"
            )
            for regime in REGIMES
        }
        invariant_surface_sets = {
            regime: _manifest_of_surface(
                invariant_surface(tree), regime == "opaque", item.variable
            )
            for regime in REGIMES
        }
        per_writing.append(
            {
                "role": candidate.role,
                "source": candidate.source,
                "invariant_writing": invariant_writing(tree),
                "invariant_cost": invariant_cost(tree),
                "cheapest_cost": min(costs.values()),
                "cheapest_world": cheapest_id,
                "control_cost": costs["G0"],
                "price": invariant_cost(tree) - min(costs.values()),
                "cheap_manifest": {
                    regime: cheap_surface_sets[regime] for regime in REGIMES
                },
                "invariant_manifest": {
                    regime: invariant_surface_sets[regime] for regime in REGIMES
                },
                "manifest_loss": {
                    regime: len(cheap_surface_sets[regime])
                    - len(invariant_surface_sets[regime])
                    for regime in REGIMES
                },
            }
        )

    return {
        "object": item.name,
        "field": item.field,
        "variable": item.variable,
        "writing_count": len(item.writings),
        "free_roles": len(free_roles),
        "free_role_names": tuple(sorted(free_roles)),
        "free_manifest_variants": {regime: len(free_sets[regime]) for regime in REGIMES},
        "free_manifest_mean": {
            regime: sum(free_sizes[regime]) / len(free_sizes[regime]) for regime in REGIMES
        },
        "free_cost_min": min(free_costs),
        "free_cost_control": control_cost,
        "invariant_role": writing.role,
        "invariant_cost": cost,
        "invariant_writing": invariant_writing(invariant_tree),
        "invariant_manifest": {regime: invariant_sets[regime] for regime in REGIMES},
        "invariant_manifest_size": {regime: len(invariant_sets[regime]) for regime in REGIMES},
        "price": cost - min(free_costs),
        "writings": tuple(per_writing),
    }


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Pearson correlation, or ``None`` when a side does not vary and a correlation is undefined."""
    count = len(xs)
    if count < 2:
        return None
    mean_x = sum(xs) / count
    mean_y = sum(ys) / count
    dev_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    dev_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    if dev_x == 0 or dev_y == 0:
        return None
    return sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / (dev_x * dev_y)


def price_report(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """AXIS 3: what invariance costs, and whether it costs the visibility the hypothesis predicts.

    The hypothesis has two halves and they are reported separately, because they do not come out
    the same way.

    * **bought with brackets** -- the invariant writing against the cheapest writing any world has,
      per object and per writing;
    * **the structure you give up choosing** -- read two ways, both measured.  Reading one: under
      free choice a world picks whichever writing is cheapest THERE, and the pick varies; under an
      invariance requirement the invariant cost does not depend on the world, so every world picks
      the same writing and the variety is gone.  Reading two: the invariant writing of a fixed tree
      makes fewer properties manifest than the cheap writing of that same tree.
    """
    corpus = tuple(corpus) if corpus is not None else OBJECT_CORPUS
    rows = [_price_cell(item) for item in corpus]

    writings = [writing for row in rows for writing in row["writings"]]
    prices = [row["price"] for row in rows]
    writing_prices = [writing["price"] for writing in writings]

    losses = {
        regime: [
            row["free_manifest_mean"][regime] - row["invariant_manifest_size"][regime]
            for row in rows
        ]
        for regime in REGIMES
    }
    writing_losses = {
        regime: [writing["manifest_loss"][regime] for writing in writings] for regime in REGIMES
    }

    # The correctness bridge, computed over the corpus itself rather than over the rows: every
    # invariant writing must reparse to its own tree in all 25 worlds, and every bracket in it must
    # be one that some world would otherwise re-associate.
    minimality_failures = []
    round_trip_failures = []
    brackets_checked = 0
    for item in corpus:
        for writing in item.writings:
            tree = object_tree(writing)
            text = invariant_writing(tree)
            for grammar in GRAMMARS:
                if tree_key(parse(text, grammar)) != tree_key(tree):
                    round_trip_failures.append((item.name, writing.role, grammar.id))
            for witness in invariant_minimality_witnesses(tree):
                brackets_checked += 1
                if not witness["required"]:
                    minimality_failures.append(
                        (item.name, writing.role, witness["pair"])
                    )

    return {
        "object_count": len(rows),
        "writing_count": len(writings),
        "world_count": len(GRAMMARS),
        "objects": tuple(rows),
        "round_trip_checks": len(writings) * len(GRAMMARS),
        "round_trip_failures": tuple(round_trip_failures),
        "invariant_writing_holds": not round_trip_failures,
        "brackets_checked": brackets_checked,
        "minimality_failures": tuple(minimality_failures),
        "invariant_writing_minimal": not minimality_failures,
        "bracket_total_invariant": sum(row["invariant_cost"] for row in rows),
        "bracket_total_cheapest": sum(row["free_cost_min"] for row in rows),
        "bracket_total_control": sum(row["free_cost_control"] for row in rows),
        "writing_total_invariant": sum(writing["invariant_cost"] for writing in writings),
        "writing_total_cheapest": sum(writing["cheapest_cost"] for writing in writings),
        "writing_total_control": sum(writing["control_cost"] for writing in writings),
        "objects_paying": sum(1 for price in prices if price > 0),
        "objects_free": sum(1 for price in prices if price == 0),
        "mean_price": sum(prices) / len(prices),
        "max_price": max(prices),
        "writings_paying": sum(1 for price in writing_prices if price > 0),
        "writings_free": sum(1 for price in writing_prices if price == 0),
        "objects_with_world_dependent_writing": sum(1 for row in rows if row["free_roles"] > 1),
        "objects_with_world_dependent_manifest": {
            regime: sum(1 for row in rows if row["free_manifest_variants"][regime] > 1)
            for regime in REGIMES
        },
        "objects_with_world_dependent_writing_under_invariance": 0,
        "manifest_loss_mean": {
            regime: sum(losses[regime]) / len(losses[regime]) for regime in REGIMES
        },
        "objects_losing": {
            regime: sum(1 for value in losses[regime] if value > 0) for regime in REGIMES
        },
        "objects_gaining": {
            regime: sum(1 for value in losses[regime] if value < 0) for regime in REGIMES
        },
        "writing_loss_mean": {
            regime: sum(writing_losses[regime]) / len(writing_losses[regime])
            for regime in REGIMES
        },
        "writings_losing": {
            regime: sum(1 for value in writing_losses[regime] if value > 0) for regime in REGIMES
        },
        "writings_gaining": {
            regime: sum(1 for value in writing_losses[regime] if value < 0) for regime in REGIMES
        },
        "price_loss_correlation": {
            regime: _pearson(prices, losses[regime]) for regime in REGIMES
        },
        "writing_price_loss_correlation": {
            regime: _pearson(writing_prices, writing_losses[regime]) for regime in REGIMES
        },
    }


# ================================================================================ concurrency
#
# Repository policy is multicore by default, and it allows a sequential path only where a
# MEASUREMENT says so.  This module has three independent workloads with very different shapes, and
# each is decided on its own numbers by :func:`parallel_decision` -- none of these constants is
# carried over from another experiment.
#
# The machine is shared with a concurrently running card, so the per-unit costs move between runs.
# Each constant below is therefore set to the value LEAST FAVOURABLE to the conclusion it supports:
# the lowest observed per-unit cost and the highest observed startup where the answer is parallel,
# and the highest observed per-unit cost where the answer is sequential.  All three decisions then
# hold across the whole observed range rather than at one lucky point in it.

#: Cores kept free so a sweep cannot starve the interactive session.
WORKER_HEADROOM_CORES: int = 2

#: An upper bound on the spawn cost any one sweep has to amortise.
WORKER_CAP: int = 12

#: Measured seconds to raise a spawn-start pool whose workers each import this module, and so SymPy.
#:
#: **Measured here, not inherited.**  :func:`measure_pool_startup` raises a pool of the default
#: worker count and runs one trivial unit in each.  On 16 cores with 12 workers the minimum of three
#: landed between ``1.29`` and ``1.81`` s across recorded runs, and individual raises reached
#: ``2.43`` s; this constant rounds up past the top of that band so the decision can never
#: over-predict a win.  The cost being paid is the workers importing this module, and so SymPy.
POOL_STARTUP_SECONDS: float = 2.5

#: Measured seconds for one axis-1 word: 25 parses plus the witness construction.  Observed between
#: ``5.4e-4`` and ``9.0e-4`` s across recorded runs, minimum of three within each; the LOWEST is
#: declared, because a lower per-unit cost is the estimate least favourable to going parallel.
WORD_SECONDS: float = 5.4e-04

#: Measured seconds for one axis-2 cell: one parse, one canonicalize, sixteen quantities.  Observed
#: between ``1.06e-2`` and ``1.34e-2`` s across recorded runs; the LOWEST is declared, for the same
#: reason as :data:`WORD_SECONDS`.
CELL_SECONDS: float = 1.06e-02

#: Measured seconds for one axis-3 object: 25 renderings, the invariant writing, both regimes, and
#: the minimality witness of every bracket.  Observed between ``1.0e-2`` and ``2.2e-2`` s across
#: recorded runs; the HIGHEST is declared, because here the conclusion is sequential and a higher
#: per-unit cost is the estimate least favourable to it.  The answer is sequential even so.
PRICE_SECONDS: float = 2.2e-02


def worker_count_for(cores: int, unit_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``unit_count`` independent units."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(unit_count, 1)))


def default_worker_count(unit_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, unit_count)


def should_parallelise(unit_count: int, seconds_per_unit: float, workers: int) -> bool:
    """Whether a pool is worth raising, from the measured per-unit cost and the measured spawn cost."""
    if workers <= 1 or unit_count <= 1:
        return False
    sequential = unit_count * seconds_per_unit
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_word_chunks(
    payloads: Sequence[tuple[int, int, int]], workers: int | None
) -> list[dict[str, Any]]:
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(
        sum(stop - start for _length, start, stop in payloads), WORD_SECONDS, resolved
    ):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_word_chunk(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_word_chunk, payloads, chunksize=1))


def _map_cells(
    payloads: Sequence[tuple[str, str]], workers: int | None
) -> list[tuple[str, str, dict[str, Any]]]:
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(len(payloads), CELL_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_cell(payload) for payload in payloads]
    chunk = max(1, len(payloads) // (resolved * 4))
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_cell, payloads, chunksize=chunk))


def _trivial(payload: int) -> int:
    """A unit that does nothing, so timing it times only the pool -- and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` is the input to :func:`should_parallelise`, so it has to be a
    measurement rather than a number copied from another experiment.  Minimum of ``repeats`` runs: a
    startup time is a floor that other load on the box can only push up.
    """
    resolved = default_worker_count(64) if workers is None else workers
    best = float("inf")
    for _ in range(max(1, repeats)):
        moment = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as executor:
            list(executor.map(_trivial, range(resolved)))
        best = min(best, time.perf_counter() - moment)
    return {"workers": resolved, "seconds": best, "declared": POOL_STARTUP_SECONDS}


def parallel_decision(
    max_length: int = 6, repeats: int = 3, corpus: Sequence[Entry] | None = None
) -> dict[str, Any]:
    """Time both paths over all three workloads, check they agree, and record which one won.

    Parallelism may change how fast and never what is produced, so ``identical`` is asserted on
    every workload rather than assumed.  Each workload is timed ``repeats`` times and the MINIMUM is
    kept, for the same reason :func:`measure_pool_startup` does: this repository's cards run
    concurrently on one machine and a run time is a floor.

    ``max_length`` is deliberately smaller than the reported enumeration.  The decision only needs
    the per-unit cost, and timing the full sweep twice, three times over, would cost more than the
    parallelism saves.
    """
    rounds = max(1, repeats)

    word_payloads = _word_payloads(max_length)
    words = sum(stop - start for _length, start, stop in word_payloads)
    word_workers = default_worker_count(len(word_payloads))
    word_sequential = float("inf")
    word_parallel = float("inf")
    sequential_words: list[Any] = []
    parallel_words: list[Any] = []
    for _ in range(rounds):
        moment = time.perf_counter()
        sequential_words = _map_word_chunks(word_payloads, workers=1)
        word_sequential = min(word_sequential, time.perf_counter() - moment)
        moment = time.perf_counter()
        parallel_words = _map_word_chunks(word_payloads, workers=word_workers)
        word_parallel = min(word_parallel, time.perf_counter() - moment)

    corpus = tuple(corpus) if corpus is not None else AXIS2_CORPUS
    cell_payloads = tuple((entry.name, grammar.id) for entry in corpus for grammar in GRAMMARS)
    cell_workers = default_worker_count(len(cell_payloads))
    cell_sequential = float("inf")
    cell_parallel = float("inf")
    sequential_cells: list[Any] = []
    parallel_cells: list[Any] = []
    for _ in range(rounds):
        moment = time.perf_counter()
        sequential_cells = _map_cells(cell_payloads, workers=1)
        cell_sequential = min(cell_sequential, time.perf_counter() - moment)
        moment = time.perf_counter()
        parallel_cells = _map_cells(cell_payloads, workers=cell_workers)
        cell_parallel = min(cell_parallel, time.perf_counter() - moment)

    price_sequential = float("inf")
    price_result: dict[str, Any] = {}
    for _ in range(rounds):
        moment = time.perf_counter()
        price_result = price_report()
        price_sequential = min(price_sequential, time.perf_counter() - moment)
    price_workers = default_worker_count(len(OBJECT_CORPUS))

    return {
        "cores": os.cpu_count(),
        "words": {
            "units": words,
            "workers": word_workers,
            "sequential_seconds": word_sequential,
            "parallel_seconds": word_parallel,
            "seconds_per_unit": word_sequential / words,
            "declared_seconds_per_unit": WORD_SECONDS,
            "identical": sequential_words == parallel_words,
            "parallel_wins": word_parallel < word_sequential,
            "predicted_parallel": should_parallelise(words, WORD_SECONDS, word_workers),
        },
        "cells": {
            "units": len(cell_payloads),
            "workers": cell_workers,
            "sequential_seconds": cell_sequential,
            "parallel_seconds": cell_parallel,
            "seconds_per_unit": cell_sequential / len(cell_payloads),
            "declared_seconds_per_unit": CELL_SECONDS,
            "identical": sequential_cells == parallel_cells,
            "parallel_wins": cell_parallel < cell_sequential,
            "predicted_parallel": should_parallelise(
                len(cell_payloads), CELL_SECONDS, cell_workers
            ),
        },
        "price": {
            "units": len(OBJECT_CORPUS),
            "workers": price_workers,
            "sequential_seconds": price_sequential,
            "seconds_per_unit": price_sequential / len(OBJECT_CORPUS),
            "declared_seconds_per_unit": PRICE_SECONDS,
            "predicted_parallel": should_parallelise(
                len(OBJECT_CORPUS), PRICE_SECONDS, price_workers
            ),
            "objects": price_result["object_count"],
        },
        "startup": measure_pool_startup(repeats=rounds),
    }


# ==================================================================================== the report


def invariants_report(max_length: int = 8, workers: int | None = None) -> dict[str, Any]:
    """The whole experiment: the three axes together, with their answers kept apart."""
    axis1 = axis1_report(max_length, workers)
    axis2 = axis2_report(workers=workers)
    axis3 = price_report()
    return {
        "axis1": axis1,
        "axis2": axis2,
        "axis3": axis3,
        "headline": {
            "characterisation": axis1["characterisation"],
            "characterisation_holds": axis1["characterisation_holds"],
            "disagreements": axis1["disagreement_count"],
            "invariant_by_construction": axis2["groups"]["by_construction"]["always"],
            "invariant_as_measured_fact": axis2["groups"]["measured"]["always"],
            "bought_with_brackets": axis3["bracket_total_invariant"]
            > axis3["bracket_total_cheapest"],
            "shows_less_transparent": axis3["writings_losing"]["transparent"] > 0,
            "shows_less_opaque": axis3["writings_losing"]["opaque"] > 0,
        },
    }
