"""Cross-validation of the ParseAtlas oracle against an independent implementation.

Two implementations of the same idea are compared on the same token sequences.
They share no code and they decide semantic equality by different means:

ParseAtlas
    custom precedence parser -> SymPy ``simplify`` -> semantic key
    ``(canonical, domain, excluded_points)``.

repsearch
    an independent precedence-parametrised parser (the precedence table is an
    argument) -> exact multivariate rational function over Q -> equality by
    cross-multiplication, ``a/b == c/d  iff  a*d - c*b == 0``.  No SymPy, no
    floating point, no probabilistic identity test.

The repsearch engine is vendored verbatim under ``case_studies/`` as frozen
evidence, so it is not on the package import path.  It is loaded here through
an explicit, documented ``sys.path`` insertion plus :mod:`importlib`.

The grammar identifier correspondence is *derived*, never assumed: ParseAtlas
builds ``G01..G24`` from ``itertools.permutations(("+", "-", "*", "/"))`` and
repsearch builds ``PRECEDENCE_ORDERS`` from ``itertools.permutations`` over its
own ``BINARY_OPS``.  :func:`grammar_correspondence` re-derives both sequences
and fails loudly if they ever stop agreeing.

Because the two oracles answer different questions, they are expected to differ
on removable restrictions: repsearch compares rational functions and therefore
discards a restriction such as ``x != 0`` introduced by ``x/x``, while
ParseAtlas keeps it in the semantic key.  :func:`compare` reports whether one
partition is a strict refinement of the other, and which.

:func:`compare` decides agreement, so it must never fail open: an input on which
no comparison was actually possible is reported as *undecided*, never as
agreement.  Three such cases exist and each has its own relation value:

``incomparable_lexical_mismatch``
    the two tokenizers do not read the same token sequence, so the two oracles
    would be answering about different expressions (``1/2`` is one rational
    literal to ParseAtlas and ``1 / 2`` to repsearch);

``incomparable_unevaluable``
    one of the two implementations cannot analyse the source at all;

``incomparable_empty_universe``
    repsearch evaluated none of the 24 grammars, so the compared universe is
    empty and the two empty partitions would trivially match.
"""

from __future__ import annotations

import functools
import importlib
import itertools
import os
import sys
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from pathlib import Path
from typing import Any

from .grammar import OPERATORS, strict_grammars

# ---------------------------------------------------------------------------
# snapshot location and loading
# ---------------------------------------------------------------------------

#: ``src/parseatlas/cross_validation.py`` -> ``src/parseatlas`` -> ``src`` -> repo root.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

#: Vendored, frozen copy of the independent implementation.  ParseAtlas does not
#: maintain it and its own tests are not part of the ParseAtlas suite.
SNAPSHOT_ROOT = REPOSITORY_ROOT / "case_studies" / "ultrafast_secp256k1" / "repsearch_snapshot"

#: Modules of the snapshot this cross-validation depends on.
REQUIRED_SNAPSHOT_MODULES = ("repsearch.expr", "repsearch.grammar", "repsearch.poly")

#: The corpus on which the two oracles were first compared.
CROSS_VALIDATION_CORPUS = (
    "2*t + 1 - t/2",
    "3*x + 2 - x/3",
    "2*x*x + 1 - x/2",
    "a + b*c - d/e",
    "a - b*c + d/e - f",
    "x*x - 1",
    "2*x + 3",
    "a/b + c*d - e/f + g",
)

#: Token sequences that carry a removable restriction, where the two oracles
#: are expected to be able to disagree.
REMOVABLE_RESTRICTION_PROBES = (
    "x/x",
    "(x*x - 1)/(x - 1)",
    "x - x + x",
    "1/x - 1/x",
)


class SnapshotUnavailable(RuntimeError):
    """Raised when the vendored repsearch snapshot cannot be imported."""


def _snapshot_problem() -> str | None:
    """Return an actionable message describing why the snapshot is unusable."""
    if not SNAPSHOT_ROOT.is_dir():
        return (
            f"repsearch snapshot directory is missing: {SNAPSHOT_ROOT}. "
            "Restore the vendored snapshot from the UltrafastSecp256k1 repository, "
            "branch experiment/representation-search, or skip the cross-validation."
        )
    for relative in ("repsearch/__init__.py", "repsearch/expr.py", "repsearch/grammar.py", "repsearch/poly.py"):
        if not (SNAPSHOT_ROOT / relative).is_file():
            return (
                f"repsearch snapshot is incomplete: {SNAPSHOT_ROOT / relative} is missing. "
                "Restore the full vendored snapshot from the UltrafastSecp256k1 repository, "
                "branch experiment/representation-search."
            )
    return None


_LOADED: dict[str, Any] = {}


def load_repsearch() -> dict[str, Any]:
    """Import the vendored repsearch modules and return them by name.

    The snapshot lives under ``case_studies/`` and is deliberately not on the
    package path, so its directory is inserted at the front of ``sys.path``
    once.  The insertion is idempotent and is repeated inside worker processes
    because Windows uses the ``spawn`` start method.
    """
    if _LOADED:
        return _LOADED
    problem = _snapshot_problem()
    if problem is not None:
        raise SnapshotUnavailable(problem)
    location = str(SNAPSHOT_ROOT)
    if location not in sys.path:
        sys.path.insert(0, location)
    try:
        modules = {name: importlib.import_module(name) for name in REQUIRED_SNAPSHOT_MODULES}
    except ImportError as error:  # pragma: no cover - defensive
        raise SnapshotUnavailable(
            f"repsearch snapshot at {SNAPSHOT_ROOT} could not be imported: {error}"
        ) from error
    _LOADED.update(modules)
    return _LOADED


def snapshot_status() -> tuple[bool, str]:
    """Return ``(available, reason)`` without raising, for test skip decisions."""
    problem = _snapshot_problem()
    if problem is not None:
        return False, problem
    try:
        load_repsearch()
    except SnapshotUnavailable as error:
        return False, str(error)
    return True, f"repsearch snapshot present at {SNAPSHOT_ROOT}"


# ---------------------------------------------------------------------------
# derived grammar identifier correspondence
# ---------------------------------------------------------------------------


def grammar_correspondence() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Derive the ParseAtlas ``G01..G24`` <-> repsearch ordering correspondence.

    Nothing here is a hardcoded table.  Both projects enumerate the same
    ``itertools.permutations`` of the same four binary operators in the same
    order, and both map ``order[0]`` to the highest binding strength.  All three
    facts are asserted; a mismatch raises instead of producing a silent
    mislabelling of the partitions.
    """
    modules = load_repsearch()
    expr = modules["repsearch.expr"]
    grammar = modules["repsearch.grammar"]

    if tuple(expr.BINARY_OPS) != tuple(OPERATORS):
        raise AssertionError(
            f"operator alphabets differ: ParseAtlas {OPERATORS!r} vs repsearch {expr.BINARY_OPS!r}"
        )
    expected = tuple(itertools.permutations(OPERATORS))
    grammars = strict_grammars()
    parseatlas_orders = tuple(item.precedence for item in grammars)
    repsearch_orders = tuple(tuple(order) for order in grammar.PRECEDENCE_ORDERS)
    if parseatlas_orders != expected:
        raise AssertionError("ParseAtlas strict grammars are not itertools.permutations order")
    if repsearch_orders != expected:
        raise AssertionError("repsearch PRECEDENCE_ORDERS is not itertools.permutations order")

    for item, order in zip(grammars, expected, strict=True):
        if item.binding_power != grammar.precedence_map(order):
            raise AssertionError(
                f"binding powers differ for {item.id} {order!r}: "
                f"{item.binding_power!r} vs {grammar.precedence_map(order)!r}"
            )
    return tuple((item.id, order) for item, order in zip(grammars, expected, strict=True))


@functools.lru_cache(maxsize=1)
def _identifier_by_order() -> dict[tuple[str, ...], str]:
    return {order: identifier for identifier, order in grammar_correspondence()}


@functools.lru_cache(maxsize=1)
def _grammar_by_identifier() -> dict[str, Any]:
    return {item.id: item for item in strict_grammars()}


# ---------------------------------------------------------------------------
# the two partitions
# ---------------------------------------------------------------------------

Partition = tuple[tuple[str, ...], ...]


def _canonical_partition(blocks: Iterable[Iterable[str]]) -> Partition:
    """Sorted tuple of sorted tuples: two equal partitions compare equal."""
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


@functools.lru_cache(maxsize=256)
def _analysis(source: str) -> dict[str, Any]:
    """Cached, read-only ParseAtlas analysis of one token sequence.

    One SymPy canonicalisation pass over 24 grammars dominates the cost of the
    whole comparison, so it is computed once per source.  Callers only read the
    result; the cache is bounded so a long sweep cannot grow without limit.
    """
    from .analyze import analyze_expression

    return analyze_expression(source, strict_grammars())


@functools.lru_cache(maxsize=256)
def _variants(source: str) -> tuple[Any, ...]:
    """Cached repsearch parse-and-evaluate pass over the 24 strict orders."""
    grammar = load_repsearch()["repsearch.grammar"]
    return tuple(grammar.enumerate_grammars(source))


def parseatlas_partition(source: str) -> Partition:
    """Partition of ``G01..G24`` by the ParseAtlas semantic key.

    The key is ``(canonical, domain, excluded_points)`` as produced by
    :func:`parseatlas.analyze.analyze_expression` over the strict grammars.
    """
    return _canonical_partition(
        item["grammars"] for item in _analysis(source)["equivalence_classes"]
    )


def repsearch_partition(source: str) -> Partition:
    """Partition of ``G01..G24`` by exact rational-function equality.

    Grammars whose AST cannot be evaluated as a rational function -- repsearch
    raises ``ZeroDivisionError`` for a literally zero denominator, where SymPy
    instead yields ``zoo`` -- are absent from the partition.  Ask
    :func:`repsearch_unevaluated` for them.
    """
    grammar = load_repsearch()["repsearch.grammar"]
    identifier = _identifier_by_order()
    classes = grammar.collapse(_variants(source))
    return _canonical_partition(
        [identifier[tuple(member.order)] for member in item.members] for item in classes
    )


def repsearch_unevaluated(source: str) -> tuple[str, ...]:
    """Grammar identifiers repsearch could not evaluate to a rational function."""
    identifier = _identifier_by_order()
    return tuple(sorted(identifier[tuple(item.order)] for item in _variants(source) if not item.ok))


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------

#: Relation values that mean the two oracles were compared and disagreed.
DIVERGENT_RELATIONS = (
    "parseatlas_strictly_finer",
    "repsearch_strictly_finer",
    "incomparable",
)

#: Relation values that mean no comparison was possible at all.  They are never
#: agreement, and :func:`cross_validation_report` counts each of them
#: separately so an undecided input can never inflate the identical counter.
UNDECIDED_RELATIONS = (
    "incomparable_lexical_mismatch",
    "incomparable_unevaluable",
    "incomparable_empty_universe",
)

#: Failures that mean "this source is outside one implementation's language".
#: ``ValueError`` comes from either tokenizer or parser, ``ZeroDivisionError``
#: (an ``ArithmeticError``) from a literally zero denominator.  Anything else --
#: a ``KeyError`` from the grammar correspondence, say -- is a bug in this
#: module and must propagate.
_UNEVALUABLE_ERRORS = (ArithmeticError, ValueError)

#: repsearch token kinds, keyed by the ParseAtlas token kind they correspond to.
_TOKEN_KINDS = {"number": "num", "name": "name", "operator": "op", "left": "lp", "right": "rp"}


def _parseatlas_lexical_shape(source: str) -> tuple[tuple[str, str], ...]:
    """Normalised ParseAtlas token stream, comparable across implementations."""
    from .tokenizer import tokenize

    shape: list[tuple[str, str]] = []
    for token in tokenize(source):
        if token.kind == "eof":
            continue
        kind = _TOKEN_KINDS[token.kind]
        if kind == "num":
            shape.append((kind, str(Fraction(token.value))))
        elif kind in ("lp", "rp"):
            shape.append((kind, ""))
        else:
            shape.append((kind, token.value))
    return tuple(shape)


def _repsearch_lexical_shape(source: str) -> tuple[tuple[str, str], ...]:
    """Normalised repsearch token stream, comparable across implementations."""
    expr = load_repsearch()["repsearch.expr"]
    shape: list[tuple[str, str]] = []
    for token in expr.tokenize(source):
        if token.kind == "num":
            shape.append(("num", str(token.value)))
        elif token.kind in ("lp", "rp", "pow"):
            shape.append((token.kind, ""))
        else:
            shape.append((token.kind, token.value))
    return tuple(shape)


def _undecided(
    source: str,
    relation: str,
    reason: str,
    parseatlas: Partition = (),
    repsearch: Partition = (),
    unevaluated: tuple[str, ...] = (),
) -> dict[str, Any]:
    """A :func:`compare` result for an input on which nothing was compared.

    Same keys as a decided result, so no caller needs to special-case it, with
    ``identical`` false and ``reason`` carrying the measured explanation.
    """
    return {
        "expression": source,
        "parseatlas_partition": parseatlas,
        "repsearch_partition": repsearch,
        "parseatlas_class_count": len(parseatlas),
        "repsearch_class_count": len(repsearch),
        "compared_parseatlas_class_count": 0,
        "compared_repsearch_class_count": 0,
        "repsearch_unevaluated": unevaluated,
        "compared_universe": (),
        "identical": False,
        "relation": relation,
        "refinement": None,
        "reason": reason,
    }


def _restrict(partition: Partition, universe: frozenset[str]) -> Partition:
    return _canonical_partition(
        [block for block in (tuple(sorted(set(item) & universe)) for item in partition) if block]
    )


def _refines(finer: Partition, coarser: Partition) -> bool:
    """True when every block of ``finer`` sits inside one block of ``coarser``."""
    coarse_sets = [frozenset(block) for block in coarser]
    return all(any(frozenset(block) <= item for item in coarse_sets) for block in finer)


def compare(source: str) -> dict[str, Any]:
    """Compare both oracles on one token sequence.

    Returns the two partitions, whether they are identical *as partitions*
    (block membership, not merely block counts), and, when they differ, whether
    one is a strict refinement of the other and which one.

    The two class counts are counts over all 24 grammars.  The comparison itself
    runs on ``compared_universe``, the grammars repsearch could evaluate, so a
    sequence such as ``x/x - x/x`` can report unequal class counts and still be
    ``identical``: the extra ParseAtlas class covers grammars repsearch refused.
    ``compared_parseatlas_class_count`` and ``compared_repsearch_class_count``
    are the counts the identity decision actually used.

    Deciding agreement is this function's whole job, so it never fails open.
    When the two tokenizers disagree about the source, when either
    implementation cannot analyse it, or when the compared universe is empty,
    the result is one of :data:`UNDECIDED_RELATIONS` with ``identical`` false and
    a ``reason``.  Without the last guard ``x/0`` -- where repsearch evaluates
    none of the 24 grammars -- would restrict both sides to the empty partition,
    find the empty partition equal to itself, and report "no comparison was
    possible" as "the two oracles agree".
    """
    try:
        parseatlas_shape = _parseatlas_lexical_shape(source)
        repsearch_shape = _repsearch_lexical_shape(source)
        if parseatlas_shape != repsearch_shape:
            return _undecided(
                source,
                "incomparable_lexical_mismatch",
                "the two tokenizers read different token sequences: "
                f"ParseAtlas {parseatlas_shape!r} vs repsearch {repsearch_shape!r}",
            )
        parseatlas = parseatlas_partition(source)
        repsearch = repsearch_partition(source)
        unevaluated = repsearch_unevaluated(source)
    except _UNEVALUABLE_ERRORS as error:
        return _undecided(
            source,
            "incomparable_unevaluable",
            f"{type(error).__name__}: {error}",
        )
    universe = frozenset().union(*(frozenset(block) for block in repsearch)) if repsearch else frozenset()
    if not universe:
        return _undecided(
            source,
            "incomparable_empty_universe",
            f"repsearch evaluated none of the {len(unevaluated)} grammars, "
            "so there is no common universe to compare the partitions on",
            parseatlas,
            repsearch,
            unevaluated,
        )
    left = _restrict(parseatlas, universe)
    right = _restrict(repsearch, universe)
    identical = left == right
    parseatlas_finer = (not identical) and _refines(left, right)
    repsearch_finer = (not identical) and _refines(right, left)
    if identical:
        relation = "identical"
    elif parseatlas_finer:
        relation = "parseatlas_strictly_finer"
    elif repsearch_finer:
        relation = "repsearch_strictly_finer"
    else:
        relation = "incomparable"
    return {
        "expression": source,
        "parseatlas_partition": parseatlas,
        "repsearch_partition": repsearch,
        "parseatlas_class_count": len(parseatlas),
        "repsearch_class_count": len(repsearch),
        "compared_parseatlas_class_count": len(left),
        "compared_repsearch_class_count": len(right),
        "repsearch_unevaluated": unevaluated,
        "compared_universe": tuple(sorted(universe)),
        "identical": identical,
        "relation": relation,
        "refinement": (
            "parseatlas" if parseatlas_finer else ("repsearch" if repsearch_finer else None)
        ),
        "reason": None,
    }


def restriction_detail(source: str) -> tuple[dict[str, Any], ...]:
    """Per-class ParseAtlas detail, for reading a removable-restriction divergence.

    Each entry carries the canonical form, the excluded points and the grammars
    that produced it, which is what a coarser rational-function oracle throws
    away.
    """
    report = _analysis(source)
    return tuple(
        {
            "class": item["id"],
            "canonical": item["canonical"],
            "domain": item["domain"],
            "excluded_points": tuple(item["excluded_points"]),
            "grammars": tuple(sorted(item["grammars"])),
        }
        for item in report["equivalence_classes"]
    )


# ---------------------------------------------------------------------------
# parallel aggregate
# ---------------------------------------------------------------------------


def resolve_workers(item_count: int, workers: int | None = None) -> int:
    """Derive a worker count from the observed core count, leaving headroom.

    ``workers=1`` forces the sequential path.  ``workers=None`` derives the count
    from :func:`os.cpu_count` minus two cores of headroom, so a cross-validation
    sweep cannot starve an interactive session, and never exceeds the number of
    independent items.
    """
    if workers is not None:
        if workers < 1:
            raise ValueError("workers must be at least 1")
        return max(1, min(workers, max(item_count, 1)))
    return max(1, min((os.cpu_count() or 1) - 2, max(item_count, 1)))


def _compare_worker(source: str) -> dict[str, Any]:
    """Module-level entry point for the process pool (Windows uses spawn)."""
    load_repsearch()
    return compare(source)


def _map(function, items: Sequence[Any], workers: int) -> list[Any]:
    """Run ``function`` over ``items``.

    SymPy canonicalisation is CPU-bound and does not release the GIL, so the
    parallel path uses processes, not threads.  One worker means no pool at all,
    which keeps the sequential path measurable and keeps small runs free of the
    spawn cost.  Results are returned in input order either way: parallelism
    changes only how fast, never what is produced.
    """
    if workers <= 1 or len(items) <= 1:
        return [function(item) for item in items]
    chunk = max(1, len(items) // (workers * 4))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(function, items, chunksize=chunk))


def cross_validation_report(sources: Iterable[str], workers: int | None = None) -> dict[str, Any]:
    """Aggregate the two-oracle comparison over a corpus of token sequences.

    ``identical + refinement + divergent + undecided == total``.  The undecided
    inputs -- the ones on which no comparison was possible -- are counted on
    their own and are broken out per relation, so they can never be read as
    agreement.
    """
    sources = tuple(sources)
    load_repsearch()
    resolved = resolve_workers(len(sources), workers)
    details = _map(_compare_worker, sources, resolved)
    undecided = {
        relation: sum(1 for item in details if item["relation"] == relation)
        for relation in UNDECIDED_RELATIONS
    }
    return {
        "total": len(sources),
        "identical": sum(1 for item in details if item["identical"]),
        "refinement": sum(1 for item in details if item["refinement"] is not None),
        "divergent": sum(1 for item in details if item["relation"] == "incomparable"),
        "parseatlas_strictly_finer": sum(1 for item in details if item["refinement"] == "parseatlas"),
        "repsearch_strictly_finer": sum(1 for item in details if item["refinement"] == "repsearch"),
        "undecided": sum(undecided.values()),
        "lexical_mismatch": undecided["incomparable_lexical_mismatch"],
        "unevaluable": undecided["incomparable_unevaluable"],
        "empty_universe": undecided["incomparable_empty_universe"],
        "workers": resolved,
        "details": tuple(details),
    }


# ---------------------------------------------------------------------------
# divergence search over generated token sequences
# ---------------------------------------------------------------------------


def token_sequences(
    operator_count: int,
    atoms: Sequence[str] = ("x", "y", "1", "2"),
    operators: Sequence[str] = OPERATORS,
) -> tuple[str, ...]:
    """Every unparenthesised sequence ``atom (op atom)^operator_count``."""
    out: list[str] = []
    for chosen in itertools.product(atoms, repeat=operator_count + 1):
        for ops in itertools.product(operators, repeat=operator_count):
            parts = [chosen[0]]
            for index in range(operator_count):
                parts.append(ops[index])
                parts.append(chosen[index + 1])
            out.append(" ".join(parts))
    return tuple(out)


def _divisor_signature(node: Any) -> tuple[str, ...]:
    """Divisor sub-expressions that ParseAtlas can turn into excluded points."""
    from .canonical import _display
    from .parser import Binary, Number

    found: list[str] = []

    def walk(current: Any) -> None:
        if isinstance(current, Binary):
            if current.operator == "/" and (
                not isinstance(current.right, Number) or current.right.value == 0
            ):
                found.append(_display(current.right))
            walk(current.left)
            walk(current.right)

    walk(node)
    return tuple(sorted(found))


def _screen_worker(source: str) -> dict[str, Any]:
    """Cheap structural screen: no SymPy, no canonicalisation.

    A ParseAtlas class can only be finer than a repsearch class when two
    grammars in one rational-function class carry different divisor
    sub-expressions.  That is decided from the ASTs alone, which is roughly two
    orders of magnitude cheaper than the SymPy path and lets the full sweep run
    before the expensive confirmation.
    """
    from .parser import parse

    grammar = load_repsearch()["repsearch.grammar"]
    identifier = _identifier_by_order()
    registry = _grammar_by_identifier()
    try:
        variants = _variants(source)
        unevaluated = sum(1 for item in variants if not item.ok)
        classes = grammar.collapse(variants)
        buckets: dict[int, set[tuple[str, ...]]] = {}
        for index, item in enumerate(classes):
            for member in item.members:
                ast = parse(source, registry[identifier[tuple(member.order)]])
                buckets.setdefault(index, set()).add(_divisor_signature(ast))
    except _UNEVALUABLE_ERRORS:
        # Either implementation may refuse a source outside its language; the
        # screen records that instead of taking down the whole sweep.
        return {"expression": source, "candidate": False, "unevaluated": 0, "parse_error": True}
    candidate = any(len(value) > 1 for value in buckets.values())
    return {
        "expression": source,
        "candidate": candidate,
        "unevaluated": unevaluated,
        "parse_error": False,
    }


def screen_for_restriction_divergence(
    sources: Iterable[str], workers: int | None = None
) -> dict[str, Any]:
    """Structural pre-filter for the expensive two-oracle confirmation."""
    sources = tuple(sources)
    load_repsearch()
    resolved = resolve_workers(len(sources), workers)
    screened = _map(_screen_worker, sources, resolved)
    candidates = tuple(item["expression"] for item in screened if item["candidate"])
    with_unevaluated = tuple(item["expression"] for item in screened if item["unevaluated"])
    full_universe = tuple(
        item["expression"] for item in screened if item["candidate"] and not item["unevaluated"]
    )
    return {
        "screened": len(sources),
        "candidates": candidates,
        "candidates_with_full_universe": full_universe,
        "sequences_with_unevaluated_grammars": with_unevaluated,
        "parse_errors": tuple(item["expression"] for item in screened if item["parse_error"]),
        "workers": resolved,
    }


def divergence_search(
    sources: Iterable[str], workers: int | None = None
) -> dict[str, Any]:
    """Screen a corpus structurally, then confirm the survivors with both oracles."""
    screen = screen_for_restriction_divergence(sources, workers)
    confirmed = cross_validation_report(screen["candidates_with_full_universe"], workers)
    divergences = tuple(
        item for item in confirmed["details"] if item["relation"] in DIVERGENT_RELATIONS
    )
    return {
        "screened": screen["screened"],
        "structural_candidates": len(screen["candidates"]),
        "confirmed_candidates": len(screen["candidates_with_full_universe"]),
        "sequences_with_unevaluated_grammars": len(screen["sequences_with_unevaluated_grammars"]),
        "confirmed_divergences": len(divergences),
        "parseatlas_strictly_finer": confirmed["parseatlas_strictly_finer"],
        "repsearch_strictly_finer": confirmed["repsearch_strictly_finer"],
        "incomparable": confirmed["divergent"],
        "undecided": confirmed["undecided"],
        "parse_errors": len(screen["parse_errors"]),
        "divergences": divergences,
        "workers": confirmed["workers"],
    }
