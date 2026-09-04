"""Experiment 0044: the ceiling, and the criteria that fight each other.

Every ranking this project has published so far is a **cost** ranking.  Cost is continuous, total,
and mute about whether a thing can be done at all.  The owner set a different question on
2026-09-04, and it is the premise of this module:

    "Today we have a memory limit.  A task might need 2 TB and we technologically have 1.8.  If
     another representation brings the computation within 1.8, that means the task BECOMES
     COMPUTABLE."

Against a hard ceiling cost stops being continuous and becomes a **step**: a ten percent reduction
is worthless at 5 TB and decisive at 1.99 TB.  That is ROADMAP thesis T31 -- reachability outranks
cost -- restated in the currency of memory.

The trap this module is built to avoid
--------------------------------------

Peak memory is a property of a **tree**.  For one fixed tree it is the same in every world, because
:func:`parseatlas.notational_cost.render` round-trips: every world re-parses its own rendering back
to that same tree.  So "does the convention change the peak memory of a computation" is *not* a
question about one tree, and an experiment reporting it as one measures nothing.  The real question
is one level up:

    An object has many equivalent writings and they have DIFFERENT peak memory.  Every world can
    write all of them.  What differs is what each COSTS IN BRACKETS.  So: in which worlds is the
    cheapest writing of an object also its most memory-frugal one, and which worlds have to pay
    brackets to stay under a ceiling?

What is measured, and what is only counted
------------------------------------------

``peak_live`` counts **values, not bytes**.  It is the Sethi-Ullman register number: the maximum
number of simultaneously live intermediate results of an evaluation that is free to order its
subtrees.  Mapping it to the owner's terabytes assumes the live values are of comparable size.  It
is a **structural bound**, not a memory benchmark, and nothing here is a wall-clock or byte-count
measurement.

The null model, which is the main risk
--------------------------------------

Precedence cannot distinguish groupings of a single repeated operator.  For a pure chain like
``a + b + c + d`` every world writes the same tree, and no world writes the balanced form
bracket-free -- :func:`null_model` re-derives that rather than assuming it.  The chains are exactly
where the depth/memory trade is sharpest and exactly where the **convention cannot act**, so the
corpus is split into entries the convention can move and entries it cannot, and every ranking is
computed over the movable set only.  A frozen entry contributes the same constant to all 25 totals
and therefore cannot move any ranking; that is the precise sense in which it is inert.

What is imported and never restated
-----------------------------------

The 25 worlds are :data:`parseatlas.manifest_properties.GRAMMARS`; the corpus is 0038's corpus,
which is 0037's named-law corpus plus the calibration quadratic, imported whole; the bracket count
is :func:`parseatlas.notational_cost.parenthesis_cost`; the parenthesization space is
:func:`parseatlas.ast_space.enumerate_parenthesizations` reached through
:func:`parseatlas.visibility_ceiling.writing_space`; and the same-object filter -- exact rational
probe first, SymPy confirmation of every survivor -- is 0039's, imported by reference.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

from .canonical import to_sympy
from .grammar import Grammar
from .manifest_properties import (
    CONTROL,
    GRAMMARS,
    MathObject,
    Writing,
    object_tree,
)
from .manifest_properties import CORPUS as LAW_OBJECTS
from .notational_cost import (
    Formula,
    corpus_audit as source_corpus_audit,
    minimality_witnesses,
    parenthesis_cost,
    render,
)
from .parser import Binary, Node, parse
from .visibility_ceiling import (
    PROBE_SEED,
    evaluate,
    probe_values,
    rebuild,
    same_object,
    to_form,
    writing_space,
)

__all__ = [
    "CHAINS",
    "CHAIN_LEAVES",
    "CHAIN_LENGTHS",
    "CHAIN_OPERATOR",
    "CHUNK_TREES",
    "CHUNK_WRITINGS",
    "CONTROL",
    "CORPUS",
    "GRAMMARS",
    "GRID_CELL_SECONDS",
    "OBJECT_BY_NAME",
    "POOL_STARTUP_SECONDS",
    "PROBE_SEED",
    "TREE_SECONDS",
    "WORKER_CAP",
    "WORKER_HEADROOM_CORES",
    "Written",
    "as_formula_corpus",
    "ceiling_sweep",
    "chain_reference",
    "cheapest_is_hungriest",
    "conflict_report",
    "corpus_audit",
    "default_worker_count",
    "depth",
    "feasible",
    "frontier",
    "grid_audit",
    "identity_audit",
    "measure_pool_startup",
    "memory_ceiling_report",
    "minimality_audit",
    "movability",
    "null_model",
    "owner_scenario",
    "parallel_decision",
    "peak_live",
    "peak_live_invariance",
    "resolve_grammar",
    "resolve_object",
    "round_trip_audit",
    "scan",
    "should_parallelise",
    "worker_count_for",
    "writings_of",
]


# ------------------------------------------------------------------------------ the two objectives


def peak_live(tree: Node) -> int:
    """The maximum number of simultaneously live intermediate values when evaluating ``tree``.

    This is the **Sethi-Ullman register number**, and it is a classical result, not an invention of
    this project: Ravi Sethi and Jeffrey D. Ullman, *The Generation of Optimal Code for Arithmetic
    Expressions*, Journal of the ACM 17(4), 1970.  The rule is

    * a leaf needs ``1``;
    * for an internal node, if the two subtrees need different amounts the answer is the **larger**,
      and if they need the same it is that amount **plus one**.

    The reason the unequal case does not add: evaluate the heavier side first, hold its single
    result, then evaluate the lighter side -- while the lighter side is running, the one carried
    value plus the lighter side's own need is at most the heavier side's need, so the carried value
    never peaks against it.  When the two sides need the same, no ordering avoids the collision and
    the peak is one higher.

    The number counts VALUES, not bytes.  See the module docstring.
    """
    if not isinstance(tree, Binary):
        return 1
    left = peak_live(tree.left)
    right = peak_live(tree.right)
    return max(left, right) if left != right else left + 1


def depth(tree: Node) -> int:
    """The critical path of ``tree``: ``1 + max`` over the children, with a leaf at ``0``.

    A leaf costs nothing to "evaluate", so the number counts operator levels -- the length of the
    longest chain of dependent operations.  An eight-term sum written as a chain has ``depth`` 7,
    written balanced it has ``depth`` 3.

    Card 0041 also computes a critical path.  **The duplication is deliberate**: 0041 is running
    concurrently with this card and is not accepted, so importing it would make this experiment's
    numbers depend on unreviewed code.  It is also not the same convention as experiment 0021's
    ``depth``, which gives a leaf ``1`` and therefore reports one more than this function
    (``depth_0021 == depth + 1``); the offset is stated here so the two are never compared naively.
    """
    if not isinstance(tree, Binary):
        return 0
    return 1 + max(depth(tree.left), depth(tree.right))


# ------------------------------------------------------------------------------------- the corpus
#
# 0038's corpus is imported whole: 33 named laws from 0037 plus the calibration quadratic, 34
# objects and 50 declared writings.  To that are added associative chains over ONE operator, which
# is where the depth/memory trade is sharpest -- and, by the null model, where the convention cannot
# act.  They are in the corpus so the trade can be seen, and they are reported separately so no
# ranking is drawn from them.

#: Chain lengths, in terms.  Four, six and eight, as the card sets them.
CHAIN_LENGTHS: tuple[int, ...] = (4, 6, 8)

#: The single operator the chains are built from.  One operator, repeated: that is the whole point.
CHAIN_OPERATOR: str = "+"

#: Leaf names for the chains, in order.
CHAIN_LEAVES: str = "abcdefgh"


def _chain_object(length: int) -> MathObject:
    leaves = CHAIN_LEAVES[:length]
    if len(leaves) != length:
        raise ValueError(f"no leaf names for a chain of {length} terms")
    source = f" {CHAIN_OPERATOR} ".join(leaves)
    return MathObject(
        name=f"chain_{length}",
        field="associative_chain",
        variable=None,
        writings=(Writing("flat", source),),
        note=(
            f"{length} terms over a single repeated {CHAIN_OPERATOR!r}: the depth/memory trade is "
            "sharpest here and the convention cannot act on it"
        ),
    )


#: The associative chains, as objects of the same kind as the named laws.
CHAINS: tuple[MathObject, ...] = tuple(_chain_object(length) for length in CHAIN_LENGTHS)

#: The corpus: 0038's 34 objects, imported whole, plus the three chains.
CORPUS: tuple[MathObject, ...] = LAW_OBJECTS + CHAINS

OBJECT_BY_NAME: dict[str, MathObject] = {item.name: item for item in CORPUS}


def as_formula_corpus(corpus: Sequence[MathObject] | None = None) -> tuple[Formula, ...]:
    """The declared writings as 0034 ``Formula`` records, so 0034's audits run over them unchanged."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    return tuple(
        Formula(f"{item.name}.{writing.role}", item.field, writing.source)
        for item in corpus
        for writing in item.writings
    )


def resolve_object(item: MathObject | str) -> MathObject:
    """An object, by value or by name."""
    if isinstance(item, MathObject):
        return item
    return OBJECT_BY_NAME[item]


def resolve_grammar(world: Grammar | str) -> Grammar:
    """A world, by value or by id.  ``G0`` is the control; ``G01``..``G24`` are the strict orders."""
    if isinstance(world, Grammar):
        return world
    for grammar in GRAMMARS:
        if grammar.id == world:
            return grammar
    raise KeyError(f"no such grammar: {world!r}")


# --------------------------------------------------------------------------------- the scan
#
# One tree that denotes the object is one WRITING of it.  The space is every parenthesization of
# every declared token word of the object, filtered to those that still denote the object -- 0039's
# discipline, because a different parenthesization is usually a different object and a frugal tree
# for something else buys nothing.


@dataclass(frozen=True, eq=True, unsafe_hash=False)
class Written:
    """One tree that denotes the object, with its two objectives and its 25 bracket costs.

    ``costs`` is a mapping, so the record is comparable but not hashable; nothing here puts a
    :class:`Written` in a set, and the objective pairs are what get de-duplicated instead.
    """

    object: str
    role: str
    index: int
    tree: Node
    depth: int
    peak_live: int
    rendering: str
    costs: dict[str, int]

    @property
    def point(self) -> tuple[int, int]:
        """The objective pair ``(depth, peak_live)``, both to be minimised."""
        return (self.depth, self.peak_live)


def _probe_chunk(payload: tuple[str, int, int, int]) -> tuple[str, int, int, tuple[Any, ...]]:
    """One chunk of one writing's parenthesization space: which forms survive the exact probe.

    Module level on purpose -- a spawn-start pool can only pickle top-level functions.  This is a
    deliberate near-duplicate of :func:`parseatlas.visibility_ceiling._same_object_forms`: that one
    resolves an object name through 0038's registry, which does not contain the chains, so it cannot
    be reused for this corpus.  The probe logic itself is imported (:func:`probe_values`,
    :func:`evaluate`, :func:`to_form`), not restated.
    """
    name, index, low, high = payload
    item = OBJECT_BY_NAME[name]
    writing = item.writings[index]
    leaves, _operators, forms = writing_space(writing)
    points = [probe_values(leaves, point) for point in (0, 1)]
    reference = to_form(object_tree(writing))
    targets = [evaluate(reference, values) for values in points]
    survivors = []
    for form in forms[low:high]:
        keep = True
        for values, target in zip(points, targets):
            value = evaluate(form, values)
            if value is None or target is None:
                continue  # undefined here proves nothing; SymPy decides in the parent
            if value != target:
                keep = False
                break
        if keep:
            survivors.append(form)
    return name, index, high - low, tuple(survivors)


#: Trees per chunk.  Chosen so one chunk is a few tenths of a second, which keeps the pool fed
#: without making the result payload large.  0039's value, unchanged, on 0039's workload.
CHUNK_TREES: int = 4000

#: Cores kept free so a sweep cannot starve the interactive MCP session (0038/0039 policy).
WORKER_HEADROOM_CORES: int = 2

#: Upper bound on the spawn cost any one sweep has to amortise (0038/0039 policy).
WORKER_CAP: int = 12

#: Writings per chunk of the (writing x world) grid audit.  Small enough that 1143 writings make
#: two chunks per worker, large enough that the payload is one pickle rather than a thousand.
CHUNK_WRITINGS: int = 48

#: Measured cost of raising a spawn-start pool whose workers each import this module, and so SymPy.
#:
#: **Measured here, not inherited.**  :func:`measure_pool_startup` raises a pool of the default
#: worker count and runs one trivial chunk in each; the recorded run on 16 cores with 12 workers is
#: ``1.286`` s, minimum of three, and this constant rounds it up.  A minimum is the right statistic
#: because this repository's cards run concurrently on one machine, and other load can only push a
#: run time up.
POOL_STARTUP_SECONDS: float = 1.3

#: Measured seconds to probe one tree of the space: two exact rational evaluations.  Recorded run:
#: ``1511296`` trees in ``24.17`` s on the sequential path, minimum of three, i.e. ``1.599e-5`` s
#: each; this constant rounds it up.  See :func:`parallel_decision`.
TREE_SECONDS: float = 1.6e-05

#: Measured seconds for one cell of the (writing x world) grid audit -- one render, one reparse, one
#: minimality witness per bracket and one peak recomputation, all in a single shared pass.  Recorded
#: run: ``28575`` cells in ``9.09`` s sequential, minimum of three, i.e. ``3.182e-4`` s each; this
#: constant rounds it up.  See :func:`parallel_decision`.
GRID_CELL_SECONDS: float = 3.2e-04


def worker_count_for(cores: int, chunk_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``chunk_count`` independent chunks."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(chunk_count, 1)))


def default_worker_count(chunk_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, chunk_count)


def should_parallelise(tree_count: int, seconds_per_tree: float, workers: int) -> bool:
    """Whether a pool pays, from the measured per-tree cost and the measured spawn cost."""
    if workers <= 1 or tree_count <= 1:
        return False
    sequential = tree_count * seconds_per_tree
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _chunks(corpus: Sequence[MathObject]) -> tuple[tuple[str, int, int, int], ...]:
    payloads = []
    for item in corpus:
        for index, writing in enumerate(item.writings):
            _leaves, _operators, forms = writing_space(writing)
            for low in range(0, len(forms), CHUNK_TREES):
                payloads.append((item.name, index, low, min(low + CHUNK_TREES, len(forms))))
    return tuple(payloads)


def _map_chunks(
    payloads: Sequence[tuple[str, int, int, int]], workers: int | None
) -> list[tuple[str, int, int, tuple[Any, ...]]]:
    """Probe every chunk, across processes when the measurement says a pool pays for itself."""
    tree_count = sum(high - low for _n, _i, low, high in payloads)
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(tree_count, TREE_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_probe_chunk(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_probe_chunk, payloads, chunksize=1))


_SCAN_CACHE: dict[tuple[str, ...], dict[str, Any]] = {}


def _scan(corpus: Sequence[MathObject], workers: int | None) -> dict[str, Any]:
    payloads = _chunks(corpus)
    enumerated = sum(high - low for _n, _i, low, high in payloads)
    results = _map_chunks(payloads, workers)

    survivors: dict[tuple[str, int], list[Any]] = {}
    for name, index, _size, forms in results:
        survivors.setdefault((name, index), []).extend(forms)
    probe_survivors = sum(len(forms) for forms in survivors.values())

    objects: dict[str, tuple[Written, ...]] = {}
    rejected = 0
    for item in corpus:
        reference = to_sympy(object_tree(item.writings[0]))
        written: list[Written] = []
        for index, writing in enumerate(item.writings):
            leaves, _operators, _forms = writing_space(writing)
            for form in survivors.get((item.name, index), ()):
                tree = rebuild(form, leaves)
                if not same_object(tree, reference):
                    rejected += 1
                    continue
                written.append(
                    Written(
                        object=item.name,
                        role=writing.role,
                        index=index,
                        tree=tree,
                        depth=depth(tree),
                        peak_live=peak_live(tree),
                        rendering=render(tree, CONTROL),
                        costs={grammar.id: parenthesis_cost(tree, grammar) for grammar in GRAMMARS},
                    )
                )
        objects[item.name] = tuple(written)

    return {
        "objects": objects,
        "corpus_size": len(corpus),
        "declared_writings": sum(len(item.writings) for item in corpus),
        "chunks": len(payloads),
        "trees_enumerated": enumerated,
        "probe_survivors": probe_survivors,
        "probe_discarded": enumerated - probe_survivors,
        "sympy_rejected": rejected,
        "confirmed": sum(len(rows) for rows in objects.values()),
    }


def scan(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """Enumerate, probe and confirm the whole writing space of a corpus.

    The result is cached on the corpus's object names so the sweep, the frontier and the audits all
    read one scan.  ``use_cache=False`` forces a fresh run, which is what the sequential/parallel
    agreement check needs.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    key = tuple(item.name for item in corpus)
    if use_cache and key in _SCAN_CACHE:
        return _SCAN_CACHE[key]
    result = _scan(corpus, workers)
    if use_cache:
        _SCAN_CACHE[key] = result
    return result


def writings_of(item: MathObject | str) -> tuple[Written, ...]:
    """Every parenthesization of the object's declared token words that denotes the SAME object.

    An object may have more than one declared writing -- an identity has two named sides -- and they
    are different token words.  The space is the union over those words, tagged with the role it
    came from, because a representation change from ``factored`` to ``expanded`` is exactly the kind
    of move the owner's scenario is about.

    The filter is 0039's and it is exact in the only direction that matters: exact rational
    arithmetic at two declared probe points (seed :data:`PROBE_SEED`, fixed before any result was
    seen) can only rule a tree OUT, and every survivor is then confirmed by SymPy.
    """
    resolved = resolve_object(item)
    for key, cached in _SCAN_CACHE.items():
        if resolved.name in key:
            return cached["objects"][resolved.name]
    return scan((resolved,))["objects"][resolved.name]


# ------------------------------------------------------------------------------- the Pareto frontier


def _pareto(points: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """The minimal points of ``(depth, peak_live)`` under componentwise <=, duplicates collapsed."""
    unique = sorted(set(points))
    return tuple(
        point
        for point in unique
        if not any(
            other != point and other[0] <= point[0] and other[1] <= point[1] for other in unique
        )
    )


def frontier(item: MathObject | str) -> dict[str, Any]:
    """Over all same-object writings, the Pareto frontier of ``(depth, peak_live)``.

    A frontier with more than one point is a **conflict**: no single writing is simultaneously
    shortest on the critical path and cheapest in live values, so the two criteria fight and
    something has to choose between them.  A frontier with one point means the two objectives agree
    on this object and the ceiling costs nothing structurally.
    """
    resolved = resolve_object(item)
    written = writings_of(resolved)
    points = tuple(sorted({row.point for row in written}))
    front = _pareto(points)
    optimal = tuple(row for row in written if row.point in front)
    return {
        "object": resolved.name,
        "field": resolved.field,
        "writing_count": len(written),
        "distinct_points": len(points),
        "points": points,
        "frontier": front,
        "frontier_size": len(front),
        "pareto_writings": len(optimal),
        "pareto_roles": tuple(sorted({row.role for row in optimal})),
        "dominated": tuple(point for point in points if point not in front),
        "dominated_writings": len(written) - len(optimal),
        "conflict": len(front) > 1,
        "min_depth": min(point[0] for point in points),
        "min_peak_live": min(point[1] for point in points),
        "max_peak_live": max(point[1] for point in points),
    }


# ---------------------------------------------------------------------------------- feasibility


def _pick(rows: Sequence[Written], grammar_id: str) -> Written:
    """The cheapest writing for a world, ties broken deterministically and disclosed.

    The tie-break is ``(cost, peak_live, depth, rendering)``: among equally cheap writings the more
    memory-frugal one is preferred, then the shorter critical path, then the rendering text so the
    choice cannot depend on enumeration order.
    """
    return min(rows, key=lambda row: (row.costs[grammar_id], row.peak_live, row.depth, row.rendering))


def fits(row, ceiling: int) -> bool:
    """Whether one writing fits under a peak-memory ceiling.

    One definition, used everywhere the ceiling is applied.  Review found the predicate written out
    inline in six places and demonstrated the risk: mutating one copy left the sweep, the movability
    split and the cheapest-is-hungriest table using their own untouched copies.  Note that it takes
    no grammar -- that absence is the whole reason feasibility is world-invariant.
    """
    return row.peak_live <= ceiling


def feasible(item: MathObject | str, world: Grammar | str, ceiling: int) -> dict[str, Any]:
    """Can this world write this object within a peak-memory ceiling, and what does it cost?

    ``premium`` is the owner's question made exact: how many extra bracket pairs the ceiling costs
    this world compared with the writing it would have chosen with no ceiling at all.  A premium of
    zero means the world's natural writing already fits.

    Note what the ``feasible`` flag can and cannot depend on, because the distinction decides how
    this experiment's headline may be stated.

    ``writings_of`` returns a property of the OBJECT, and ``peak_live`` a property of a TREE.
    Neither consults a grammar, so the line below that filters by ``row.peak_live <= ceiling`` is
    world-independent and the flag is **world-invariant by construction**.  It is not a measured
    agreement and must never be reported as one: evaluating it once per grammar and observing that
    the answers match is a theorem about this function, not a search.

    The claim it rests on IS empirical, and it is checked elsewhere: every world must actually be
    able to render every tree, which :func:`round_trip_audit` verifies over the whole grid.  That
    audit is the load-bearing evidence; the per-world loop in :func:`owner_scenario` is only the
    shape of the answer.

    What is genuinely world-dependent is ``cost`` and ``premium``.
    """
    resolved = resolve_object(item)
    grammar = resolve_grammar(world)
    rows = writings_of(resolved)
    within = tuple(row for row in rows if fits(row, ceiling))
    unconstrained = _pick(rows, grammar.id)
    if not within:
        return {
            "object": resolved.name,
            "grammar": grammar.id,
            "ceiling": ceiling,
            "feasible": False,
            "cost": None,
            "premium": None,
            "writings_within": 0,
            "writings_total": len(rows),
            "unconstrained_cost": unconstrained.costs[grammar.id],
            "unconstrained_peak_live": unconstrained.peak_live,
            "writing": None,
        }
    chosen = _pick(within, grammar.id)
    return {
        "object": resolved.name,
        "grammar": grammar.id,
        "ceiling": ceiling,
        "feasible": True,
        "cost": chosen.costs[grammar.id],
        "premium": chosen.costs[grammar.id] - unconstrained.costs[grammar.id],
        "writings_within": len(within),
        "writings_total": len(rows),
        "unconstrained_cost": unconstrained.costs[grammar.id],
        "unconstrained_peak_live": unconstrained.peak_live,
        "writing": {
            "role": chosen.role,
            "depth": chosen.depth,
            "peak_live": chosen.peak_live,
            "rendering": render(chosen.tree, grammar),
        },
    }


# --------------------------------------------------------------------------------- the null model


def _ceiling_range(corpus: Sequence[MathObject]) -> tuple[int, ...]:
    scan(corpus)
    peaks = {row.peak_live for item in corpus for row in writings_of(item)}
    return tuple(range(min(peaks), max(peaks) + 1))


def movability(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Split the corpus into the entries the convention can move and the entries it cannot.

    Three classes, and the distinction between the first two matters:

    ``tree_frozen``
        every tree in the object's writing space costs the same in all 25 worlds.  The convention
        cannot act on it **at all** -- this is the single-repeated-operator null model.
    ``choice_frozen``
        worlds do disagree about individual trees, but the CHEAPEST feasible cost coincides across
        all 25 at every ceiling, so the object still adds the same constant to every total.
    ``movable``
        two worlds differ in cheapest feasible cost at some ceiling.  Only these can move a ranking.

    A frozen entry of either kind contributes an identical constant to all 25 world totals, so it
    cannot change any order; that is why the rankings are computed over ``movable`` only.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan(corpus)
    ceilings = _ceiling_range(corpus)
    tree_frozen, choice_frozen, movable = [], [], []
    for item in corpus:
        rows = writings_of(item)
        per_tree_constant = all(len(set(row.costs.values())) == 1 for row in rows)
        varies = False
        for ceiling in ceilings:
            within = [row for row in rows if fits(row, ceiling)]
            if not within:
                continue
            totals = {
                grammar.id: min(row.costs[grammar.id] for row in within) for grammar in GRAMMARS
            }
            if len(set(totals.values())) > 1:
                varies = True
                break
        if varies:
            movable.append(item.name)
        elif per_tree_constant:
            tree_frozen.append(item.name)
        else:
            choice_frozen.append(item.name)
    return {
        "corpus_size": len(corpus),
        "ceilings_considered": ceilings,
        "movable": tuple(movable),
        "movable_count": len(movable),
        "tree_frozen": tuple(tree_frozen),
        "tree_frozen_count": len(tree_frozen),
        "choice_frozen": tuple(choice_frozen),
        "choice_frozen_count": len(choice_frozen),
        "frozen_count": len(tree_frozen) + len(choice_frozen),
    }


def chain_reference(length: int = 8) -> dict[str, Any]:
    """Re-derive the chain-versus-balanced pair on a single repeated operator, from scratch.

    The manager measured the eight-term case by hand -- chain ``depth`` 7 / ``peak_live`` 2, balanced
    ``depth`` 3 / ``peak_live`` 4 -- and this function computes it rather than repeating it.  It also
    counts how many of the 25 worlds write the balanced form bracket-free, which is the null model's
    load-bearing fact.
    """
    leaves = CHAIN_LEAVES[:length]
    flat = f" {CHAIN_OPERATOR} ".join(leaves)
    chain = parse(flat, CONTROL)

    def balanced(names: Sequence[str]) -> str:
        if len(names) == 1:
            return names[0]
        half = len(names) // 2
        return f"({balanced(names[:half])} {CHAIN_OPERATOR} {balanced(names[half:])})"

    balanced_source = balanced(list(leaves))
    if balanced_source.startswith("("):
        balanced_source = balanced_source[1:-1]
    balanced_tree = parse(balanced_source, CONTROL)
    chain_costs = {grammar.id: parenthesis_cost(chain, grammar) for grammar in GRAMMARS}
    balanced_costs = {grammar.id: parenthesis_cost(balanced_tree, grammar) for grammar in GRAMMARS}
    return {
        "length": length,
        "operator": CHAIN_OPERATOR,
        "flat_source": flat,
        "chain": {
            "rendering": render(chain, CONTROL),
            "depth": depth(chain),
            "peak_live": peak_live(chain),
            "costs": tuple(sorted(set(chain_costs.values()))),
            "bracket_free_worlds": tuple(
                sorted(key for key, value in chain_costs.items() if value == 0)
            ),
        },
        "balanced": {
            "source": balanced_source,
            "rendering": render(balanced_tree, CONTROL),
            "depth": depth(balanced_tree),
            "peak_live": peak_live(balanced_tree),
            "costs": tuple(sorted(set(balanced_costs.values()))),
            "bracket_free_worlds": tuple(
                sorted(key for key, value in balanced_costs.items() if value == 0)
            ),
        },
        "halving_the_path_doubles_the_memory": (
            depth(chain) > depth(balanced_tree) and peak_live(balanced_tree) > peak_live(chain)
        ),
    }


def null_model(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """The null model in full: the split, and the chain fact that motivates it."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    split = movability(corpus)
    return {
        **split,
        "chain_reference": tuple(chain_reference(length) for length in CHAIN_LENGTHS),
        "chain_objects": tuple(item.name for item in CHAINS),
        "chains_are_frozen": all(
            item.name in split["tree_frozen"] + split["choice_frozen"] for item in CHAINS
        ),
    }


# --------------------------------------------------------------------------------- the sweep


def _totals(names: Sequence[str], ceiling: int) -> dict[str, int] | None:
    """Per-world total cheapest feasible bracket cost over ``names``, or ``None`` if any is infeasible."""
    totals = {grammar.id: 0 for grammar in GRAMMARS}
    for name in names:
        rows = [row for row in writings_of(name) if fits(row, ceiling)]
        if not rows:
            return None
        for grammar in GRAMMARS:
            totals[grammar.id] += min(row.costs[grammar.id] for row in rows)
    return totals


def _ranking(totals: dict[str, int]) -> tuple[str, ...]:
    """World ids ordered by total, ties broken by id so the order is a function of the numbers."""
    return tuple(key for key, _value in sorted(totals.items(), key=lambda pair: (pair[1], pair[0])))


def _tiers(totals: dict[str, int]) -> tuple[tuple[int, tuple[str, ...]], ...]:
    """The ranking with ties left as ties, so no claim rests on an alphabetical tie-break.

    ``ranking`` has to break ties somehow, and it breaks them by grammar id; that is a presentation
    choice and nothing may be concluded from it.  The tier list is the same information with the
    arbitrary part removed, and it is what the "did the ranking change" claim is checked against.
    """
    grouped: dict[int, list[str]] = {}
    for key, value in totals.items():
        grouped.setdefault(value, []).append(key)
    return tuple((total, tuple(sorted(names))) for total, names in sorted(grouped.items()))


def ceiling_sweep(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Sweep the ceiling across its whole useful range and report what moves.

    At each ceiling: how many objects any world can write at all, how many worlds can do the whole
    corpus, and the ranking of the worlds by bracket cost over the **movable** entries that are
    feasible there.

    Ranking comparisons across ceilings are only honest on a fixed set of objects, so the shifts are
    reported separately, each on the basis of the objects feasible at the tighter of the two
    ceilings.  ``first_change_ceiling`` is the loosest ceiling at which tightening by one changes
    the order.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan(corpus)
    ceilings = _ceiling_range(corpus)
    split = movability(corpus)
    movable = split["movable"]

    rows = []
    for ceiling in ceilings:
        feasible_objects = tuple(
            item.name for item in corpus if any(fits(row, ceiling) for row in writings_of(item))
        )
        whole_corpus = len(feasible_objects) == len(corpus)
        here = tuple(name for name in movable if name in feasible_objects)
        totals = _totals(here, ceiling) or {}
        ranking = _ranking(totals) if totals else ()
        rows.append(
            {
                "ceiling": ceiling,
                "feasible_objects": len(feasible_objects),
                "corpus_size": len(corpus),
                "infeasible_objects": tuple(
                    item.name for item in corpus if item.name not in feasible_objects
                ),
                "worlds_covering_corpus": len(GRAMMARS) if whole_corpus else 0,
                "movable_feasible": len(here),
                "movable_basis": here,
                "totals": totals,
                "ranking": ranking,
                "tiers": _tiers(totals) if totals else (),
                "control_rank": (ranking.index(CONTROL.id) + 1) if ranking else None,
                "control_total": totals.get(CONTROL.id),
                "cheapest": ranking[0] if ranking else None,
                "cheapest_total": totals[ranking[0]] if ranking else None,
            }
        )

    shifts = []
    for tight, loose in zip(ceilings, ceilings[1:]):
        basis = tuple(
            name
            for name in movable
            if any(fits(row, tight) for row in writings_of(name))
        )
        tight_totals = _totals(basis, tight)
        loose_totals = _totals(basis, loose)
        if tight_totals is None or loose_totals is None:
            continue
        tight_rank = _ranking(tight_totals)
        loose_rank = _ranking(loose_totals)
        shifts.append(
            {
                "loose": loose,
                "tight": tight,
                "basis_size": len(basis),
                "basis": basis,
                "loose_ranking": loose_rank,
                "tight_ranking": tight_rank,
                "loose_tiers": _tiers(loose_totals),
                "tight_tiers": _tiers(tight_totals),
                "loose_totals": loose_totals,
                "tight_totals": tight_totals,
                "changed": tight_rank != loose_rank,
                "tiers_changed": _tiers(tight_totals) != _tiers(loose_totals),
                "loose_cheapest": loose_rank[0],
                "tight_cheapest": tight_rank[0],
                "control_rank_loose": loose_rank.index(CONTROL.id) + 1,
                "control_rank_tight": tight_rank.index(CONTROL.id) + 1,
                "control_total_loose": loose_totals[CONTROL.id],
                "control_total_tight": tight_totals[CONTROL.id],
                "moved_worlds": tuple(
                    world
                    for world in loose_rank
                    if loose_rank.index(world) != tight_rank.index(world)
                ),
            }
        )

    changed = [shift for shift in shifts if shift["tiers_changed"]]
    return {
        "ceilings": ceilings,
        "unconstrained_ceiling": ceilings[-1],
        "movable_count": split["movable_count"],
        "frozen_count": split["frozen_count"],
        "rows": tuple(rows),
        "shifts": tuple(shifts),
        "ranking_changes": len(changed),
        "first_change_ceiling": max((shift["tight"] for shift in changed), default=None),
        "tie_break_only": tuple(
            shift["tight"] for shift in shifts if shift["changed"] and not shift["tiers_changed"]
        ),
    }


# ------------------------------------------------------------------------------ the owner's question


def owner_scenario(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """The owner's scenario, in both the strict and the measurable reading.

    **Strict reading.** "Is there an object and a ceiling where ``G0`` is infeasible and some other
    world is feasible?"  The answer is **no, and necessarily so.**

    Feasibility here is world-invariant BY CONSTRUCTION, not by measurement: ``writings_of`` is a
    property of the object, ``peak_live`` a property of a tree, and neither consults a grammar.  The
    per-grammar loop below therefore evaluates one world-independent expression twenty-five times,
    and ``disagreement_count == 0`` is a theorem about that expression rather than a search that
    could have come out otherwise.  It is reported because the shape of the answer is worth showing,
    and it is labelled here so that nobody reads an empty search as a strong one.

    The substantive claim underneath IS empirical and is checked in :func:`round_trip_audit`: every
    world really can render every tree, because :func:`parseatlas.notational_cost.render` brackets
    wherever the grammar would otherwise re-associate.  If that failed, the invariance would fail
    with it.  That audit, not this loop, is the evidence.

    The consequence is the finding: **changing the convention cannot bring a computation under a
    peak-memory ceiling.**  Memory is not a reachability axis under a change of notation; it is
    purely a cost axis.  The witness list is returned empty rather than omitted.

    **Measurable reading.**  What differs is the PRICE of staying under the ceiling.  For each object
    and ceiling this reports the worlds whose natural (cheapest unconstrained) writing already fits
    -- premium zero -- against the worlds that must buy their way under with extra brackets.  A world
    paying while another pays nothing is the owner's step function in the currency this project can
    actually measure.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan(corpus)
    ceilings = _ceiling_range(corpus)
    strict_witnesses = []
    disagreements = []
    invariance_checks = 0
    grammar_checks = 0
    premium_rows = []
    for ceiling in ceilings:
        for item in corpus:
            rows = writings_of(item)
            within = [row for row in rows if fits(row, ceiling)]
            invariance_checks += 1
            flags = {}
            for grammar in GRAMMARS:
                grammar_checks += 1
                flags[grammar.id] = feasible(item, grammar, ceiling)["feasible"]
            if len(set(flags.values())) > 1:
                disagreements.append({"object": item.name, "ceiling": ceiling, "flags": flags})
            control = flags[CONTROL.id]
            others = {key: value for key, value in flags.items() if key != CONTROL.id}
            if not control and any(others.values()):
                strict_witnesses.append(
                    {
                        "object": item.name,
                        "ceiling": ceiling,
                        "feasible_worlds": tuple(sorted(k for k, v in others.items() if v)),
                    }
                )
            if not within:
                continue
            premiums = {
                grammar.id: feasible(item, grammar, ceiling)["premium"] for grammar in GRAMMARS
            }
            if any(value > 0 for value in premiums.values()):
                premium_rows.append(
                    {
                        "object": item.name,
                        "ceiling": ceiling,
                        "free_worlds": tuple(
                            sorted(k for k, v in premiums.items() if v == 0)
                        ),
                        "paying_worlds": {k: v for k, v in sorted(premiums.items()) if v > 0},
                        "control_premium": premiums[CONTROL.id],
                        "max_premium": max(premiums.values()),
                    }
                )
    control_pays_others_free = tuple(
        row
        for row in premium_rows
        if row["control_premium"] > 0 and row["free_worlds"]
    )
    others_pay_control_free = tuple(
        row for row in premium_rows if row["control_premium"] == 0 and row["paying_worlds"]
    )
    return {
        "ceilings": ceilings,
        "strict_reading": {
            "feasibility_is_world_invariant": not disagreements,
            "witnesses": tuple(strict_witnesses),
            "witness_count": len(strict_witnesses),
            "disagreements": tuple(disagreements),
            "disagreement_count": len(disagreements),
            "object_ceiling_checks": invariance_checks,
            "grammar_checks": grammar_checks,
        },
        "premium_rows": tuple(premium_rows),
        "control_pays_while_others_are_free": control_pays_others_free,
        "control_pays_count": len(control_pays_others_free),
        "others_pay_while_control_is_free": others_pay_control_free,
        "others_pay_count": len(others_pay_control_free),
    }


def cheapest_is_hungriest(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Is a world's cheapest writing ever, exclusively, the object's most memory-hungry one?

    Only objects whose writings differ in ``peak_live`` can answer; the rest are excluded and
    counted.  A cell counts when EVERY cheapest writing for that world sits at the object's maximum
    ``peak_live`` -- if the world has an equally cheap frugal writing, the ceiling costs it nothing
    and the cell does not count.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan(corpus)
    split = movability(corpus)
    hits = []
    cells = 0
    considered = []
    for item in corpus:
        if item.name not in split["movable"]:
            continue
        rows = writings_of(item)
        peaks = {row.peak_live for row in rows}
        if len(peaks) == 1:
            continue
        considered.append(item.name)
        highest = max(peaks)
        for grammar in GRAMMARS:
            cells += 1
            best = min(row.costs[grammar.id] for row in rows)
            at_best = {row.peak_live for row in rows if row.costs[grammar.id] == best}
            if at_best == {highest}:
                hits.append({"object": item.name, "grammar": grammar.id, "peak_live": highest})
    by_object: dict[str, int] = {}
    for hit in hits:
        by_object[hit["object"]] = by_object.get(hit["object"], 0) + 1
    return {
        "objects_considered": tuple(considered),
        "objects_considered_count": len(considered),
        "cells": cells,
        "hits": len(hits),
        "by_object": dict(sorted(by_object.items())),
        "occurs": bool(hits),
    }


def conflict_report(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Where the two objectives fight: every object's frontier, split by the null model."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan(corpus)
    split = movability(corpus)
    frontiers = tuple(frontier(item) for item in corpus)
    conflicting = tuple(row for row in frontiers if row["conflict"])
    return {
        "frontiers": frontiers,
        "conflict_count": len(conflicting),
        "conflicting": tuple(row["object"] for row in conflicting),
        "conflicting_movable": tuple(
            row["object"] for row in conflicting if row["object"] in split["movable"]
        ),
        "conflicting_frozen": tuple(
            row["object"] for row in conflicting if row["object"] not in split["movable"]
        ),
        "multi_point_count": len(conflicting),
        "single_point_count": len(frontiers) - len(conflicting),
        "largest_frontier": max(row["frontier_size"] for row in frontiers),
        "objects_with_several_pareto_writings": tuple(
            row["object"] for row in frontiers if row["pareto_writings"] > 1
        ),
        "pareto_writings": sum(row["pareto_writings"] for row in frontiers),
        "dominated_writings": sum(row["dominated_writings"] for row in frontiers),
    }


# ------------------------------------------------------------------------------- correctness bridge


def corpus_audit(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """The declared sources are canonical under ``G0`` and the names are unique (0034's own audit)."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    return source_corpus_audit(as_formula_corpus(corpus))


def identity_audit(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Every declared writing of an object denotes the same object, decided by SymPy."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    failures = []
    checks = 0
    for item in corpus:
        reference = to_sympy(object_tree(item.writings[0]))
        for writing in item.writings:
            checks += 1
            if not same_object(object_tree(writing), reference):
                failures.append({"object": item.name, "role": writing.role})
    return {
        "checks": checks,
        "failures": len(failures),
        "failing": tuple(failures),
        "holds": not failures,
    }


def _grid_chunk(
    payload: tuple[tuple[tuple[str, Any], ...], tuple[Grammar, ...]]
) -> dict[str, Any]:
    """One chunk of the (writing x world) grid: round trip, minimality and peak invariance.

    Module level on purpose -- a spawn-start pool can only pickle top-level functions.  All three
    checks run in one pass because they share the expensive part, which is the render.
    """
    writings, grammars = payload
    checks = 0
    brackets = 0
    round_trip: list[dict[str, Any]] = []
    minimality: list[dict[str, Any]] = []
    invariance: list[dict[str, Any]] = []
    for name, tree in writings:
        expected_peak = peak_live(tree)
        expected_depth = depth(tree)
        for grammar in grammars:
            checks += 1
            text = render(tree, grammar, verify=False)
            reparsed = parse(text, grammar)
            if reparsed != tree:
                round_trip.append({"object": name, "grammar": grammar.id, "rendering": text})
                continue
            if peak_live(reparsed) != expected_peak or depth(reparsed) != expected_depth:
                invariance.append({"object": name, "grammar": grammar.id, "rendering": text})
            for witness in minimality_witnesses(tree, grammar):
                brackets += 1
                if not witness["required"]:
                    minimality.append({"object": name, "grammar": grammar.id, **witness})
    return {
        "checks": checks,
        "brackets": brackets,
        "round_trip": round_trip,
        "minimality": minimality,
        "invariance": invariance,
    }


_GRID_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}


def grid_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """The whole correctness bridge in one pass over the (writing x world) grid.

    Three checks share the render, so they share the pass:

    * **round trip** -- every counted writing, rendered in every world, reparses to the tree it came
      from.  This is what makes ``peak_live`` a property of the OBJECT's writing rather than of a
      string: if a rendering reparsed to a different tree, the peak it was credited with would
      belong to something else.
    * **minimality** -- every bracket the renderer emits is load-bearing; deleting it changes the
      tree or breaks the parse.  Without this a bracket count would be an upper bound, not a cost.
    * **peak invariance** -- for ONE fixed tree, ``peak_live`` and ``depth`` are the same in every
      world.  This is not a finding; it is the trap, checked, and the reason the experiment had to
      be posed one level up.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    key = (tuple(item.name for item in corpus), tuple(grammar.id for grammar in grammars))
    if use_cache and key in _GRID_CACHE:
        return _GRID_CACHE[key]

    scan(corpus)
    writings = tuple((item.name, row.tree) for item in corpus for row in writings_of(item))
    payloads = [
        (writings[low : low + CHUNK_WRITINGS], grammars)
        for low in range(0, len(writings), CHUNK_WRITINGS)
    ]
    cells = len(writings) * len(grammars)
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(cells, GRID_CELL_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        results = [_grid_chunk(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
            results = list(executor.map(_grid_chunk, payloads, chunksize=1))

    merged = {
        "writings": len(writings),
        "grammars": len(grammars),
        "chunks": len(payloads),
        "checks": sum(result["checks"] for result in results),
        "brackets_checked": sum(result["brackets"] for result in results),
        "round_trip_failures": tuple(entry for result in results for entry in result["round_trip"]),
        "minimality_violations": tuple(
            entry for result in results for entry in result["minimality"]
        ),
        "invariance_failures": tuple(entry for result in results for entry in result["invariance"]),
    }
    if use_cache:
        _GRID_CACHE[key] = merged
    return merged


def round_trip_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Every counted writing, rendered in every world, reparses to the tree it came from."""
    grid = grid_audit(corpus, grammars, workers=workers)
    return {
        "checks": grid["checks"],
        "failures": len(grid["round_trip_failures"]),
        "failing": grid["round_trip_failures"],
        "holds": not grid["round_trip_failures"],
    }


def minimality_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Every bracket in every counted writing is load-bearing: deleting it changes the tree."""
    grid = grid_audit(corpus, grammars, workers=workers)
    return {
        "brackets_checked": grid["brackets_checked"],
        "violations": len(grid["minimality_violations"]),
        "violating": grid["minimality_violations"],
        "minimal": not grid["minimality_violations"],
    }


def peak_live_invariance(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """For ONE fixed tree, ``peak_live`` is the same in every world -- the trap, stated as a check.

    This is not a finding, it is the reason the experiment had to be posed one level up: because
    the round trip holds, every world reads its own rendering back as the same tree, so no
    convention can change a fixed tree's peak.  What a convention changes is which tree is cheap to
    write.
    """
    grid = grid_audit(corpus, grammars, workers=workers)
    return {
        "checks": grid["checks"],
        "failures": len(grid["invariance_failures"]),
        "failing": grid["invariance_failures"],
        "holds": not grid["invariance_failures"],
    }


# ------------------------------------------------------------------------------------ multicore


def _trivial_chunk(payload: int) -> int:
    """A chunk that does nothing, so timing it times only the pool -- and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` feeds :func:`should_parallelise`, so it is measured here rather
    than carried over.  Minimum of ``repeats`` runs, because a startup time is a floor that
    background load can only push up.
    """
    resolved = default_worker_count(64) if workers is None else workers
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as executor:
            list(executor.map(_trivial_chunk, range(resolved), chunksize=1))
        best = min(best, time.perf_counter() - start)
    return {
        "workers": resolved,
        "cores": os.cpu_count(),
        "repeats": repeats,
        "seconds": best,
        "declared": POOL_STARTUP_SECONDS,
    }


def parallel_decision(
    corpus: Sequence[MathObject] | None = None, repeats: int = 3
) -> dict[str, Any]:
    """Time both paths over both workloads, check they agree, and record which one won.

    Repository policy is multicore by default and allows a sequential path only where a measurement
    justifies it.  This module has two independent workloads and each is decided on its own numbers:

    * the **probe** over the full parenthesization space -- 1.5 million exact rational evaluations,
      CPU-bound pure Python with no shared state;
    * the **grid** audit -- every counted writing rendered, reparsed and bracket-checked in every
      world.

    Both are CPU-bound, so processes rather than threads.  Each path is timed ``repeats`` times and
    the MINIMUM is reported, for the same reason :func:`measure_pool_startup` does: a run time is a
    floor that other load on the box can only push up, and this repository's cards run concurrently
    on one machine.  Parallelism changes only how fast: ``identical`` is asserted on both.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    rounds = max(1, repeats)

    payloads = _chunks(corpus)
    trees = sum(high - low for _n, _i, low, high in payloads)
    probe_workers = default_worker_count(len(payloads))

    probe_sequential = float("inf")
    probe_parallel = float("inf")
    sequential: list[Any] = []
    parallel: list[Any] = []
    for _ in range(rounds):
        moment = time.perf_counter()
        sequential = _map_chunks(payloads, workers=1)
        probe_sequential = min(probe_sequential, time.perf_counter() - moment)
        moment = time.perf_counter()
        parallel = _map_chunks(payloads, workers=probe_workers)
        probe_parallel = min(probe_parallel, time.perf_counter() - moment)

    probe_worth_it = should_parallelise(trees, TREE_SECONDS, probe_workers)

    scan(corpus)
    writing_count = sum(len(writings_of(item)) for item in corpus)
    cells = writing_count * len(GRAMMARS)
    grid_chunks = -(-writing_count // CHUNK_WRITINGS)
    grid_workers = default_worker_count(grid_chunks)

    grid_sequential = float("inf")
    grid_parallel = float("inf")
    grid_sequential_result: dict[str, Any] = {}
    grid_parallel_result: dict[str, Any] = {}
    for _ in range(rounds):
        moment = time.perf_counter()
        grid_sequential_result = grid_audit(corpus, workers=1, use_cache=False)
        grid_sequential = min(grid_sequential, time.perf_counter() - moment)
        moment = time.perf_counter()
        grid_parallel_result = grid_audit(corpus, workers=grid_workers, use_cache=False)
        grid_parallel = min(grid_parallel, time.perf_counter() - moment)

    grid_worth_it = should_parallelise(cells, GRID_CELL_SECONDS, grid_workers)

    return {
        "cores": os.cpu_count(),
        "repeats": rounds,
        "probe": {
            "chunks": len(payloads),
            "trees": trees,
            "workers": probe_workers,
            "sequential_seconds": probe_sequential,
            "parallel_seconds": probe_parallel,
            "speedup": probe_sequential / probe_parallel if probe_parallel else float("inf"),
            "identical": sequential == parallel,
            "seconds_per_tree": probe_sequential / trees if trees else 0.0,
            "declared_seconds_per_tree": TREE_SECONDS,
            "parallel_worth_it": probe_worth_it,
            "default_path": "parallel" if probe_worth_it else "sequential",
        },
        "grid": {
            "chunks": grid_chunks,
            "writings": writing_count,
            "cells": cells,
            "workers": grid_workers,
            "sequential_seconds": grid_sequential,
            "parallel_seconds": grid_parallel,
            "speedup": grid_sequential / grid_parallel if grid_parallel else float("inf"),
            "identical": grid_sequential_result == grid_parallel_result,
            "seconds_per_cell": grid_sequential / cells if cells else 0.0,
            "declared_seconds_per_cell": GRID_CELL_SECONDS,
            "parallel_worth_it": grid_worth_it,
            "default_path": "parallel" if grid_worth_it else "sequential",
        },
        "identical": sequential == parallel and grid_sequential_result == grid_parallel_result,
        "default_path": "parallel" if probe_worth_it and grid_worth_it else "mixed",
    }


# ---------------------------------------------------------------------------------- the report


def memory_ceiling_report(
    corpus: Sequence[MathObject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Everything the report prints, in one call."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scanned = scan(corpus, workers=workers)
    conflicts = conflict_report(corpus)
    nulls = null_model(corpus)
    sweep = ceiling_sweep(corpus)
    owner = owner_scenario(corpus)
    hungry = cheapest_is_hungriest(corpus)
    grid = grid_audit(corpus, workers=workers)
    return {
        "scan": {key: value for key, value in scanned.items() if key != "objects"},
        "corpus": corpus_audit(corpus),
        "identity": identity_audit(corpus),
        "round_trip": round_trip_audit(corpus, workers=workers),
        "minimality": minimality_audit(corpus, workers=workers),
        "peak_invariance": peak_live_invariance(corpus, workers=workers),
        "grid": {key: value for key, value in grid.items() if not isinstance(value, tuple)},
        "conflict": conflicts,
        "null_model": nulls,
        "sweep": sweep,
        "owner": owner,
        "cheapest_is_hungriest": hungry,
        "headline": {
            "objects": len(corpus),
            "confirmed_writings": scanned["confirmed"],
            "objects_where_the_objectives_conflict": conflicts["conflict_count"],
            "of_those_movable": len(conflicts["conflicting_movable"]),
            "movable": nulls["movable_count"],
            "frozen": nulls["frozen_count"],
            "first_ranking_change_at_ceiling": sweep["first_change_ceiling"],
            "control_infeasible_elsewhere_feasible": owner["strict_reading"]["witness_count"],
            "feasibility_disagreements": owner["strict_reading"]["disagreement_count"],
            "objects_with_several_pareto_points": conflicts["conflict_count"],
            "objects_with_several_pareto_writings": len(
                conflicts["objects_with_several_pareto_writings"]
            ),
            "control_pays_while_others_are_free": owner["control_pays_count"],
            "cheapest_is_hungriest_cells": hungry["hits"],
            "cheapest_is_hungriest_of": hungry["cells"],
        },
    }
