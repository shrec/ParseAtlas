"""Experiment 0041: which worlds write parallel forms for free.

Direction B, applied to computation instead of to legibility.

The question this module answers, and the one it is careful NOT to ask
-----------------------------------------------------------------------

Depth is a property of a TREE.  For one fixed tree the depth is the same in every one of the 25
worlds, because :func:`parseatlas.notational_cost.render` reparses its own output and every world
therefore recovers exactly the tree it was handed.  "Does the convention change the critical path
of this expression?" is consequently **not a question about one tree at all**, and an experiment
that reported it as one would be measuring the round-trip guarantee rather than the conventions.

The real question is one level up.  An object has many equivalent *writings*.  They have different
depths - the left-leaning chain ``a + b + c + d`` has depth ``3``, the balanced ``(a + b) + (c + d)``
has depth ``2``, and depth is exactly parallel evaluation time - and every world can write every one
of them.  What differs between worlds is **what each writing costs in brackets**.  So:

    In which worlds is the CHEAPEST writing of an object also its SHALLOWEST?

Where the two coincide, the world writes parallel-ready mathematics by default.  Where they diverge,
its natural notation is a sequential chain and the parallel form has to be bought with brackets.
The gap is the quantity this module measures and calls the **parallelism tax**:

.. code-block:: text

    tax(object, world) = depth(cheapest writing in that world) - min depth over all writings

Both halves are needed.  ``min_depth`` alone is a property of the mathematics; ``free_depth`` alone
is a property of the notation; only their difference is a property of the *pairing*, which is what
the founding question is about.

The null model, which is the main risk in this experiment
----------------------------------------------------------

A pure associative chain over ONE repeated operator is invisible to precedence.  Theorem T6
(:mod:`parseatlas.support_reduction`) says a grammar acts on an expression only through its
restriction to the operators the expression actually uses; a one-operator word has exactly one such
restriction, so all 25 worlds price every tree over that word identically.  The consequence is
forced rather than discovered: on those words the cheapest writing is the left-leaning chain in
every world, the balanced form costs the same brackets in every world, and the tax is a constant of
the word.  Reporting that as "no world parallelises for free" would be publishing a parsing artifact.

:func:`null_model` therefore splits the corpus into the entries whose tax CAN move between worlds
and the entries whose tax cannot, verifies the T6 claim by measurement rather than by citation
(:func:`support_invariance`), re-ranks the worlds on the movable subcorpus alone, and reports both.

What is imported and never restated
------------------------------------

* the same-object filter is experiment 0039's, imported by reference:
  :func:`parseatlas.visibility_ceiling.probe_values`, :func:`~parseatlas.visibility_ceiling.evaluate`
  and :func:`~parseatlas.visibility_ceiling.same_object`.  An exact-rational probe at two declared
  points (seed :data:`parseatlas.visibility_ceiling.PROBE_SEED`) can only ever rule a tree OUT, and
  every survivor is confirmed with SymPy.  A different parenthesization is usually a different
  object, and a shallow tree for something else is worth nothing;
* the bracket rule and the correctness bridge are experiment 0034's:
  :func:`parseatlas.notational_cost.render`, :func:`~parseatlas.notational_cost.parenthesis_cost`
  and :func:`~parseatlas.notational_cost.minimality_witnesses`;
* the space enumeration is :func:`parseatlas.ast_space.enumerate_parenthesizations`;
* the corpus is :data:`parseatlas.manifest_properties.CORPUS`, imported whole, plus the associative
  chains this experiment adds and declares.

**Depth is NOT re-implemented here.**  :mod:`parseatlas.critical_path` does not export a tree-level
``depth``; it reads ``canonical.operation_cost(tree)["depth"]``, whose convention counts a LEAF as
``1``.  This card's convention counts a leaf as ``0``.  :func:`depth` is therefore that imported
number minus one - stated here rather than duplicated silently, so the off-by-one is a declaration
and not a discrepancy.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from .ast_space import enumerate_parenthesizations
from .canonical import operation_cost, to_sympy
from .grammar import Grammar, all_grammars
from .manifest_properties import CORPUS as LAW_CORPUS
from .notational_cost import minimality_witnesses, parenthesis_cost, render, tree_operators
from .parser import Node, parse
from .visibility_ceiling import (
    Form,
    evaluate,
    in_order,
    placeholder_leaves,
    probe_values,
    rebuild,
    same_object,
    to_form,
)

__all__ = [
    "CHAIN_LENGTHS",
    "CHAIN_OPERATORS",
    "CHUNK_TREES",
    "CONTROL",
    "CORPUS",
    "GRAMMARS",
    "LEAF_NAMES",
    "POOL_STARTUP_SECONDS",
    "TREE_SECONDS",
    "WORKER_CAP",
    "WORKER_HEADROOM_CORES",
    "Subject",
    "chain_subjects",
    "competition_ranking",
    "control_distinction",
    "cost_depth_table",
    "default_worker_count",
    "depth",
    "depth_invariance",
    "filter_audit",
    "grid",
    "law_subjects",
    "measure_pool_startup",
    "minimality_audit",
    "null_model",
    "parallel_decision",
    "parallel_worlds_report",
    "rank_correlation",
    "round_trip_audit",
    "should_parallelise",
    "space_forms",
    "space_size",
    "spearman",
    "speedup_table",
    "subject_tree",
    "subject_word",
    "support_invariance",
    "tax_table",
    "writings_of",
]

#: The 25 worlds: the tied-level control ``G0`` plus the 24 strict orderings.
GRAMMARS: tuple[Grammar, ...] = all_grammars()

#: ``G0`` is not "one of the 25" for direction B - it is the notation mathematics is written in
#: today, and the baseline every other world is priced against.
CONTROL: Grammar = GRAMMARS[0]


# --------------------------------------------------------------------------------------- depth


def depth(tree: Node) -> int:
    """The critical path of a tree: a leaf is ``0``, an internal node is ``1 + max(children)``.

    Derived from :func:`parseatlas.canonical.operation_cost`, which is what
    :mod:`parseatlas.critical_path` itself uses.  That function does not expose a tree-level
    ``depth`` of its own and it counts a LEAF as ``1``; this card's convention counts a leaf as
    ``0``, so the value here is the imported one minus one.  The subtraction is declared rather
    than a second recursion, so there is exactly one depth definition in the repository.
    """
    return operation_cost(tree)["depth"] - 1


# --------------------------------------------------------------------------------------- corpus


@dataclass(frozen=True)
class Subject:
    """One corpus entry: a mathematical object together with the ONE token word that spells it.

    The writing space of a subject is the parenthesizations of that word which still denote the
    object.  Keeping the word fixed is the scope restriction this experiment inherits from 0039 and
    it is a real one: a commutative reordering (``a + b`` for ``b + a``) is a different word and is
    therefore out of scope, as is any rewriting that changes the token multiset.
    """

    name: str
    kind: str
    field: str
    source: str
    note: str = ""


#: Chain lengths.  Four is the shortest length at which balanced and sequential differ, and eight
#: is the length at which the classical parallel-prefix gap (``n - 1`` against ``ceil(log2 n)``) is
#: unmistakable while the space (``429`` trees) stays exhaustively enumerable.
CHAIN_LENGTHS: tuple[int, ...] = (4, 5, 6, 8)

#: The two operators whose reassociation preserves the object.  ``-`` and ``/`` are deliberately
#: absent: ``a - (b - c)`` is a different object, so a subtraction chain would have exactly one
#: same-object writing and could not exhibit a depth choice at all.
CHAIN_OPERATORS: tuple[str, ...] = ("+", "*")

#: Distinct leaf names, so that no two leaves of a chain can be confused by the probe.
LEAF_NAMES: tuple[str, ...] = ("a", "b", "c", "d", "e", "f", "g", "h")


def law_subjects(corpus: Sequence[Any] | None = None) -> tuple[Subject, ...]:
    """0038/0039's named-law corpus, one subject per declared writing.

    ``manifest_properties.CORPUS`` gives an object several named writings with DIFFERENT token
    words; the writing space of this experiment is the parenthesizations of ONE word, so each
    declared writing becomes its own subject and its own row.
    """
    corpus = tuple(corpus) if corpus is not None else LAW_CORPUS
    return tuple(
        Subject(
            name=f"{item.name}.{writing.role}",
            kind="law",
            field=item.field,
            source=writing.source,
            note=item.note,
        )
        for item in corpus
        for writing in item.writings
    )


def chain_subjects(
    lengths: Sequence[int] | None = None, operators: Sequence[str] | None = None
) -> tuple[Subject, ...]:
    """Pure associative chains ``a op b op c ...`` - the null model, added on purpose.

    These are where sequential and balanced writings differ most sharply and where the classical
    parallel-prefix result lives.  They are also exactly the words a precedence grammar cannot see
    into, which is why :func:`null_model` reports them separately instead of averaging them in.
    """
    lengths = tuple(lengths) if lengths is not None else CHAIN_LENGTHS
    operators = tuple(operators) if operators is not None else CHAIN_OPERATORS
    label = {"+": "add", "*": "mul"}
    return tuple(
        Subject(
            name=f"chain_{label.get(operator, operator)}_{length}",
            kind="chain",
            field="associative_chain",
            source=f" {operator} ".join(LEAF_NAMES[:length]),
            note=f"{length} leaves, one repeated operator: sequential depth {length - 1}",
        )
        for operator in operators
        for length in lengths
    )


#: The exact corpus: 0038/0039's 34 named objects as their 50 declared writings, plus 8 associative
#: chains.  Stated as data so the reader can check it rather than take it on trust.
CORPUS: tuple[Subject, ...] = law_subjects() + chain_subjects()


# ------------------------------------------------------------------------------- the writing space


def subject_tree(subject: Subject) -> Node:
    """The intended tree of a subject: its source parsed under the control grammar.

    ``G0`` is the control because it IS how mathematics is written today, so parsing a conventional
    source under it recovers the intended object instead of imposing one.
    """
    return parse(subject.source, CONTROL)


def subject_word(subject: Subject) -> tuple[tuple[Node, ...], tuple[str, ...]]:
    """The token word of a subject: its leaf sequence and its operator sequence, left to right."""
    return in_order(subject_tree(subject))


def space_forms(subject: Subject) -> tuple[Form, ...]:
    """Every parenthesization of the subject's token word, with no bound applied."""
    leaves, operators = subject_word(subject)
    return enumerate_parenthesizations(placeholder_leaves(len(leaves)), operators)


def space_size(subject: Subject) -> int:
    """The Catalan size of the subject's parenthesization space."""
    return len(space_forms(subject))


# ---------------------------------------------------------------------------- the identity filter
#
# Imported from 0039 and not restated.  The probe is exact rational arithmetic at two declared
# points, so a disagreement is a PROOF of difference and the probe can only ever discard; an
# undefined value (division by zero) proves nothing and is escalated to SymPy rather than guessed.
# Every survivor is then confirmed with SymPy before it is allowed to contribute a depth.


def _probe_chunk(payload: tuple[Subject, int, int]) -> tuple[str, int, tuple[Form, ...]]:
    """One slice of one subject's space: which forms survive the exact probe.

    Module level on purpose - a spawn-start pool can only pickle top-level functions.  The chunk
    returns candidates only; SymPy confirmation happens once, in the parent, on the survivors.
    """
    subject, low, high = payload
    leaves, _operators = subject_word(subject)
    forms = space_forms(subject)
    points = [probe_values(leaves, point) for point in (0, 1)]
    reference = to_form(subject_tree(subject))
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
    return subject.name, high - low, tuple(survivors)


#: Trees per chunk, so one chunk is a few tenths of a second: enough work to hide the dispatch and
#: little enough that the returned payload stays small.  0039's value, unchanged.
CHUNK_TREES: int = 4000

#: Cores kept free so a sweep cannot starve the interactive MCP session (0038/0039 policy).
WORKER_HEADROOM_CORES: int = 2

#: Upper bound on the spawn cost any one sweep has to amortise (0038/0039 policy).
WORKER_CAP: int = 12

#: Measured cost of raising a spawn-start pool whose workers each import this module, and so SymPy.
#: Measured here by :func:`measure_pool_startup`, not inherited: the recorded run on 16 cores with
#: 12 workers is ``1.251`` s, minimum of five, and this constant rounds it up.
POOL_STARTUP_SECONDS: float = 1.3

#: Measured seconds to probe one tree: two exact rational evaluations of a word of up to 13
#: operators.  Recorded run: ``1511800`` trees in ``26.20`` s sequential, i.e. ``1.733e-5`` s each;
#: this constant rounds it up.  See :func:`parallel_decision`.
#:
#: With these two numbers the pool pays for itself above roughly ``79000`` trees, so the full corpus
#: (``1511800``) runs parallel and a single small subject runs sequential - both directions pinned
#: in the test suite, so a change to either constant that silently flipped the policy would fail.
TREE_SECONDS: float = 1.8e-05


def default_worker_count(chunk_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    cores = os.cpu_count() or 1
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(chunk_count, 1)))


def should_parallelise(tree_count: int, seconds_per_tree: float, workers: int) -> bool:
    """Whether a pool is worth raising, from the MEASURED per-tree cost and MEASURED spawn cost.

    Arithmetic on two measurements, not a tree-count threshold: a pool pays for itself exactly when
    the spawn cost is smaller than the sequential time it removes.
    """
    if workers <= 1 or tree_count <= 1:
        return False
    sequential = tree_count * seconds_per_tree
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _chunks(corpus: tuple[Subject, ...]) -> tuple[tuple[Subject, int, int], ...]:
    payloads = []
    for subject in corpus:
        total = space_size(subject)
        for low in range(0, total, CHUNK_TREES):
            payloads.append((subject, low, min(low + CHUNK_TREES, total)))
    return tuple(payloads)


def _map_chunks(
    payloads: Sequence[tuple[Subject, int, int]], workers: int | None
) -> list[tuple[str, int, tuple[Form, ...]]]:
    """Probe every chunk, across processes when the measurement says a pool pays for itself."""
    tree_count = sum(high - low for _s, low, high in payloads)
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(tree_count, TREE_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_probe_chunk(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_probe_chunk, payloads, chunksize=1))


@lru_cache(maxsize=None)
def _scan(corpus: tuple[Subject, ...], workers: int | None) -> dict[str, Any]:
    """Probe the whole space, confirm the survivors with SymPy, and record what each stage cost."""
    payloads = _chunks(corpus)
    results = _map_chunks(payloads, workers)
    candidates: dict[str, list[Form]] = {subject.name: [] for subject in corpus}
    probed = 0
    for name, count, forms in results:
        probed += count
        candidates[name].extend(forms)

    confirmed: dict[str, tuple[Form, ...]] = {}
    rejected: dict[str, tuple[Form, ...]] = {}
    for subject in corpus:
        leaves, _operators = subject_word(subject)
        expression = to_sympy(subject_tree(subject))
        kept: list[Form] = []
        dropped: list[Form] = []
        for form in candidates[subject.name]:
            (kept if same_object(rebuild(form, leaves), expression) else dropped).append(form)
        confirmed[subject.name] = tuple(kept)
        rejected[subject.name] = tuple(dropped)
    return {
        "space_total": sum(space_size(subject) for subject in corpus),
        "trees_probed": probed,
        "probe_survivors": sum(len(v) for v in candidates.values()),
        "same_object": confirmed,
        "sympy_rejected": rejected,
        "same_object_total": sum(len(v) for v in confirmed.values()),
        "sympy_rejected_total": sum(len(v) for v in rejected.values()),
        "chunks": len(payloads),
    }


def writings_of(subject: Subject, workers: int | None = None) -> tuple[Form, ...]:
    """Every parenthesization of the subject's token word that DENOTES THE SAME OBJECT.

    This is the writing space the whole experiment is about.  It is not the parenthesization space:
    on the named-law corpus the space is ``1510820`` trees and only ``667`` of them are still the
    object, because reassociation almost always changes what is written rather than how it is
    written.  A shallow tree for a different object has bought nothing, so it is discarded here.
    """
    return _scan((subject,), workers)["same_object"][subject.name]


def filter_audit(corpus: Sequence[Subject] | None = None, workers: int | None = None) -> dict[str, Any]:
    """What the identity filter actually did, stage by stage.

    Reported because the two stages do very different amounts of work on this corpus and the split
    is a fact about the corpus, not about the filter: the exact-rational probe discards almost
    everything, and SymPy then confirms every survivor.  A SymPy rejection count of zero is a
    property of THIS corpus and is pinned as one; it is not evidence that the confirmation step is
    unnecessary, which is why the direct two-directional test of :func:`same_object` lives in the
    test suite alongside it.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan = _scan(corpus, workers)
    return {
        "subjects": len(corpus),
        "space_total": scan["space_total"],
        "trees_probed": scan["trees_probed"],
        "probe_rejected": scan["space_total"] - scan["probe_survivors"],
        "probe_survivors": scan["probe_survivors"],
        "sympy_confirmed": scan["same_object_total"],
        "sympy_rejected": scan["sympy_rejected_total"],
        "fully_enumerated": scan["trees_probed"] == scan["space_total"],
        "same_object_fraction": scan["same_object_total"] / scan["space_total"]
        if scan["space_total"]
        else 0.0,
    }


# ------------------------------------------------------------------------------ cost against depth


def _writing_records(subject: Subject, forms: Sequence[Form]) -> tuple[dict[str, Any], ...]:
    leaves, _operators = subject_word(subject)
    declared = to_form(subject_tree(subject))
    records = []
    for form in forms:
        node = rebuild(form, leaves)
        records.append(
            {
                "form": form,
                "node": node,
                "depth": depth(node),
                "is_declared": form == declared,
            }
        )
    return tuple(records)


def cost_depth_table(
    subject: Subject, grammar: Grammar, workers: int | None = None, forms: Sequence[Form] | None = None
) -> dict[str, Any]:
    """For one (object, world): every same-object writing with its bracket count and its depth.

    Two numbers carry the experiment.  ``free_depth`` is the depth of the writing this world writes
    for free - the shallowest among the writings that attain the world's minimum bracket count, so
    that a tie is resolved IN THE WORLD'S FAVOUR and the tax is never inflated by an arbitrary
    choice.  ``min_depth`` is the shallowest writing available at any price, and is the same in
    every world because depth is a property of a tree.  Their difference is the PARALLELISM TAX.

    ``premium`` is the same fact read from the other side: the extra brackets this world charges to
    buy a shallowest writing at all.
    """
    resolved = tuple(forms) if forms is not None else writings_of(subject, workers)
    records = _writing_records(subject, resolved)
    if not records:  # pragma: no cover - the declared tree is always its own writing
        raise ValueError(f"{subject.name} has no same-object writing, not even the declared one")
    rows = tuple(
        {
            "form": record["form"],
            "cost": parenthesis_cost(record["node"], grammar),
            "depth": record["depth"],
            "text": render(record["node"], grammar),
            "is_declared": record["is_declared"],
        }
        for record in records
    )
    min_cost = min(row["cost"] for row in rows)
    cheapest = tuple(row for row in rows if row["cost"] == min_cost)
    depths = [row["depth"] for row in rows]
    min_depth = min(depths)
    shallowest = tuple(row for row in rows if row["depth"] == min_depth)
    free_depth = min(row["depth"] for row in cheapest)
    cost_of_min_depth = min(row["cost"] for row in shallowest)
    written = next(row for row in rows if row["is_declared"])
    return {
        "object": subject.name,
        "kind": subject.kind,
        "grammar": grammar.id,
        "writings": rows,
        "writing_count": len(rows),
        "min_cost": min_cost,
        "max_cost": max(row["cost"] for row in rows),
        "cheapest_forms": tuple(row["form"] for row in cheapest),
        "free_depth": free_depth,
        "free_depth_pessimistic": max(row["depth"] for row in cheapest),
        "min_depth": min_depth,
        "max_depth": max(depths),
        "written_depth": written["depth"],
        "written_cost": written["cost"],
        "cost_of_min_depth": cost_of_min_depth,
        "premium": cost_of_min_depth - min_cost,
        "tax": free_depth - min_depth,
        "tax_pessimistic": max(row["depth"] for row in cheapest) - min_depth,
        "shallowest_is_free": free_depth == min_depth,
    }


@lru_cache(maxsize=None)
def grid(corpus: tuple[Subject, ...], workers: int | None = None) -> dict[str, Any]:
    """The whole (object x world) grid of cost-against-depth cells, computed once."""
    scan = _scan(corpus, workers)
    cells: dict[tuple[str, str], dict[str, Any]] = {}
    for subject in corpus:
        forms = scan["same_object"][subject.name]
        for grammar in GRAMMARS:
            cells[(subject.name, grammar.id)] = cost_depth_table(
                subject, grammar, forms=forms
            )
    return {"cells": cells, "scan": scan, "corpus": corpus}


# -------------------------------------------------------------------------------------- ranking


def competition_ranking(totals: dict[str, float]) -> tuple[dict[str, Any], ...]:
    """Competition ranking (``1, 2, 2, 4``) over per-world totals, smallest first."""
    order = sorted(totals.items(), key=lambda item: (item[1], item[0]))
    ranking = []
    previous_total: float | None = None
    previous_rank = 0
    for position, (world, total) in enumerate(order, start=1):
        rank = previous_rank if total == previous_total else position
        ranking.append({"rank": rank, "id": world, "total": total})
        previous_total, previous_rank = total, rank
    return tuple(ranking)


def _average_ranks(values: Sequence[float]) -> list[float]:
    """Ascending ranks with ties averaged, which is what a tie-corrected Spearman needs."""
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while end + 1 < len(order) and values[order[end + 1]] == values[order[position]]:
            end += 1
        shared = (position + end) / 2 + 1
        for index in order[position : end + 1]:
            ranks[index] = shared
        position = end + 1
    return ranks


def spearman(left: Sequence[float], right: Sequence[float]) -> float:
    """Spearman rank correlation with ties averaged, i.e. Pearson on the average ranks.

    Written out rather than imported: SciPy is not a dependency of this repository, and the tie
    handling matters here because whole blocks of worlds share a total.
    """
    if len(left) != len(right):
        raise ValueError("spearman needs two sequences of the same length")
    if len(left) < 2:
        raise ValueError("spearman needs at least two observations")
    a = _average_ranks(left)
    b = _average_ranks(right)
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    covariance = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    spread_a = sum((x - mean_a) ** 2 for x in a) ** 0.5
    spread_b = sum((y - mean_b) ** 2 for y in b) ** 0.5
    if spread_a == 0 or spread_b == 0:
        return 0.0
    return covariance / (spread_a * spread_b)


# ------------------------------------------------------------------------------------- tax table


def tax_table(corpus: Sequence[Subject] | None = None, workers: int | None = None) -> dict[str, Any]:
    """The full grid: what parallelism tax each world charges, per object and in total.

    Per world: the total tax over the corpus, how many objects it charges nothing for, and its rank.
    Per object: which worlds get its shallowest writing for free.

    The per-world **cost** total is carried alongside, computed from the same cells - it is the
    number of brackets that world spends writing the corpus at its own cheapest - so the two
    rankings the card asks to compare are built from one measurement and cannot drift apart.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    cells = grid(corpus, workers)["cells"]

    rows = []
    for subject in corpus:
        per_world = {g.id: cells[(subject.name, g.id)]["tax"] for g in GRAMMARS}
        premiums = {g.id: cells[(subject.name, g.id)]["premium"] for g in GRAMMARS}
        costs = {g.id: cells[(subject.name, g.id)]["min_cost"] for g in GRAMMARS}
        sample = cells[(subject.name, CONTROL.id)]
        free_worlds = tuple(sorted(gid for gid, tax in per_world.items() if tax == 0))
        rows.append(
            {
                "object": subject.name,
                "kind": subject.kind,
                "field": subject.field,
                "source": subject.source,
                "writing_count": sample["writing_count"],
                "space": space_size(subject),
                "support": tree_operators(subject_tree(subject)),
                "support_size": len(tree_operators(subject_tree(subject))),
                "min_depth": sample["min_depth"],
                "max_depth": sample["max_depth"],
                "written_depth": sample["written_depth"],
                "tax": per_world,
                "premium": premiums,
                "min_cost": costs,
                "control_tax": per_world[CONTROL.id],
                "free_worlds": free_worlds,
                "free_world_count": len(free_worlds),
                "tax_min": min(per_world.values()),
                "tax_max": max(per_world.values()),
                "tax_range": max(per_world.values()) - min(per_world.values()),
                "movable": max(per_world.values()) != min(per_world.values()),
            }
        )

    tax_totals = {g.id: sum(row["tax"][g.id] for row in rows) for g in GRAMMARS}
    cost_totals = {g.id: sum(row["min_cost"][g.id] for row in rows) for g in GRAMMARS}
    free_counts = {g.id: sum(1 for row in rows if row["tax"][g.id] == 0) for g in GRAMMARS}
    tax_ranking = competition_ranking(tax_totals)
    cost_ranking = competition_ranking(cost_totals)
    tax_ranks = {entry["id"]: entry["rank"] for entry in tax_ranking}
    cost_ranks = {entry["id"]: entry["rank"] for entry in cost_ranking}
    best_tax = tax_ranking[0]["total"]
    worlds = [g.id for g in GRAMMARS]
    correlation = spearman([cost_totals[w] for w in worlds], [tax_totals[w] for w in worlds])

    free_in_some_dear_in_control = tuple(
        row["object"]
        for row in rows
        if row["control_tax"] > 0 and row["free_world_count"] > 0
    )
    return {
        "subjects": len(rows),
        "worlds": len(GRAMMARS),
        "rows": tuple(rows),
        "tax_totals": tax_totals,
        "cost_totals": cost_totals,
        "free_counts": free_counts,
        "tax_ranking": tuple(
            {
                **entry,
                "free_objects": free_counts[entry["id"]],
                "cost_total": cost_totals[entry["id"]],
                "cost_rank": cost_ranks[entry["id"]],
                "versus_control": entry["total"] - tax_totals[CONTROL.id],
            }
            for entry in tax_ranking
        ),
        "cost_ranking": cost_ranking,
        "tax_ranks": tax_ranks,
        "cost_ranks": cost_ranks,
        "best_tax": best_tax,
        "best_worlds": tuple(entry["id"] for entry in tax_ranking if entry["total"] == best_tax),
        "worst_tax": tax_ranking[-1]["total"],
        "tax_spread": tax_ranking[-1]["total"] - best_tax,
        "control_tax_total": tax_totals[CONTROL.id],
        "control_tax_rank": tax_ranks[CONTROL.id],
        "control_cost_rank": cost_ranks[CONTROL.id],
        "control_free_objects": free_counts[CONTROL.id],
        "rank_correlation": correlation,
        "objects_free_somewhere_taxed_in_control": free_in_some_dear_in_control,
        "objects_free_everywhere": tuple(
            row["object"] for row in rows if row["free_world_count"] == len(GRAMMARS)
        ),
        "objects_free_nowhere": tuple(row["object"] for row in rows if row["free_world_count"] == 0),
    }


def control_distinction(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Does ``G0`` - the notation mathematics actually settled on - hold any distinction here?

    Asked as a question about uniqueness, because that is the only form in which it has an answer:
    for each measured coordinate, how many of the 25 worlds share ``G0``'s value.  A coordinate
    ``G0`` shares with nobody is a distinction; a coordinate it shares is not, however flattering
    the number looks in isolation.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = tax_table(corpus, workers)
    worlds = tuple(g.id for g in GRAMMARS)
    coordinates = {
        "tax_total": table["tax_totals"],
        "cost_total": table["cost_totals"],
        "free_objects": table["free_counts"],
    }
    shared = {
        key: tuple(sorted(w for w in worlds if values[w] == values[CONTROL.id]))
        for key, values in coordinates.items()
    }
    pairs = {
        "tax_and_free": tuple(
            sorted(
                w
                for w in worlds
                if table["tax_totals"][w] == table["tax_totals"][CONTROL.id]
                and table["free_counts"][w] == table["free_counts"][CONTROL.id]
            )
        ),
        "tax_and_cost": tuple(
            sorted(
                w
                for w in worlds
                if table["tax_totals"][w] == table["tax_totals"][CONTROL.id]
                and table["cost_totals"][w] == table["cost_totals"][CONTROL.id]
            )
        ),
    }
    rows = {row["object"]: row for row in table["rows"]}
    free_only_in_control = tuple(
        name for name, row in rows.items() if row["free_worlds"] == (CONTROL.id,)
    )
    taxed_only_in_control = tuple(
        name
        for name, row in rows.items()
        if row["tax"][CONTROL.id] > 0
        and all(row["tax"][w] == 0 for w in worlds if w != CONTROL.id)
    )
    return {
        "control": CONTROL.id,
        "values": {key: values[CONTROL.id] for key, values in coordinates.items()},
        "shared_with": shared,
        "shared_counts": {key: len(value) for key, value in shared.items()},
        "unique_coordinates": tuple(sorted(key for key, value in shared.items() if len(value) == 1)),
        "pairs": pairs,
        "pair_counts": {key: len(value) for key, value in pairs.items()},
        "unique_pairs": tuple(sorted(key for key, value in pairs.items() if len(value) == 1)),
        "free_only_in_control": free_only_in_control,
        "taxed_only_in_control": taxed_only_in_control,
        "tax_rank": table["control_tax_rank"],
        "cost_rank": table["control_cost_rank"],
        "worst_tax_group": table["tax_totals"][CONTROL.id] == table["worst_tax"],
    }


def rank_correlation(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Do cost rank and parallelism-tax rank agree across the 25 worlds?

    A positive correlation says the cheap worlds are also the parallel ones; a negative one says
    cheapness is bought with sequential notation.  The correlation is reported on the full corpus
    and on the movable subcorpus, because the forced entries add the same constant to every world's
    tax and therefore cannot influence a ranking - only a total.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = tax_table(corpus, workers)
    nulls = null_model(corpus, workers)
    worlds = [g.id for g in GRAMMARS]
    full = spearman(
        [table["cost_totals"][w] for w in worlds], [table["tax_totals"][w] for w in worlds]
    )
    movable = spearman(
        [table["cost_totals"][w] for w in worlds], [nulls["movable_tax_totals"][w] for w in worlds]
    )
    return {
        "worlds": len(worlds),
        "full_corpus": full,
        "movable_subcorpus": movable,
        "cost_ranks": table["cost_ranks"],
        "tax_ranks": table["tax_ranks"],
        "agree_exactly": all(
            table["cost_ranks"][w] == table["tax_ranks"][w] for w in worlds
        ),
    }


# ------------------------------------------------------------------------------- speedup table


def speedup_table(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """What the tax actually buys, per object: sequential depth against minimum depth.

    **This is a critical-path BOUND, not a measured runtime.**  ``written_depth / min_depth`` is the
    ratio of two tree depths under the standard unit-cost parallel model in which every operation
    takes one step and unlimited processors are free.  No expression here was executed, nothing was
    timed, and no scheduler, memory system or vectoriser was modelled.  Reading the ratio as a
    speedup would be dressing a depth quotient up as a benchmark, which it is not.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    cells = grid(corpus, workers)["cells"]
    rows = []
    for subject in corpus:
        cell = cells[(subject.name, CONTROL.id)]
        sequential = cell["written_depth"]
        minimum = cell["min_depth"]
        rows.append(
            {
                "object": subject.name,
                "kind": subject.kind,
                "leaves": len(subject_word(subject)[0]),
                "operators": len(subject_word(subject)[1]),
                "sequential_depth": sequential,
                "min_depth": minimum,
                "depth_saved": sequential - minimum,
                "ratio": sequential / minimum if minimum else 1.0,
                "control_free_depth": cell["free_depth"],
                "control_tax": cell["tax"],
                "control_premium": cell["premium"],
            }
        )
    improvable = tuple(row for row in rows if row["depth_saved"] > 0)
    return {
        "measure": "critical-path depth under the unit-cost parallel model",
        "not_a_benchmark": (
            "a bound on parallel evaluation time, not a measured runtime: nothing here was executed"
        ),
        "rows": tuple(rows),
        "subjects": len(rows),
        "improvable_count": len(improvable),
        "improvable": tuple(row["object"] for row in improvable),
        "max_ratio": max((row["ratio"] for row in rows), default=1.0),
        "max_depth_saved": max((row["depth_saved"] for row in rows), default=0),
        "deepest": max(rows, key=lambda row: row["sequential_depth"])["object"] if rows else None,
        "total_sequential_depth": sum(row["sequential_depth"] for row in rows),
        "total_min_depth": sum(row["min_depth"] for row in rows),
    }


# --------------------------------------------------------------------------------- the null model


def support_invariance(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Verify T6 on this corpus instead of citing it.

    Theorem T6 (:mod:`parseatlas.support_reduction`) says a grammar acts on an expression only
    through its restriction to the operators the expression uses.  A word over ONE operator has one
    such restriction, so every world must price every tree over that word identically.  That is the
    claim the null model rests on, so it is checked cell by cell: for each single-operator subject,
    every same-object writing is rendered under all 25 worlds and the 25 bracket counts must be one
    value.  A mismatch would mean the null model is wrong, not that a world had been found.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan = _scan(tuple(corpus), workers)
    checks = 0
    mismatches = []
    single = tuple(s for s in corpus if len(tree_operators(subject_tree(s))) <= 1)
    for subject in single:
        leaves, _operators = subject_word(subject)
        for form in scan["same_object"][subject.name]:
            node = rebuild(form, leaves)
            costs = {g.id: parenthesis_cost(node, g) for g in GRAMMARS}
            checks += len(costs)
            if len(set(costs.values())) != 1:
                mismatches.append({"object": subject.name, "form": form, "costs": costs})
    return {
        "single_operator_subjects": tuple(s.name for s in single),
        "single_operator_count": len(single),
        "checks": checks,
        "mismatches": tuple(mismatches),
        "mismatch_count": len(mismatches),
        "holds": not mismatches,
    }


def null_model(corpus: Sequence[Subject] | None = None, workers: int | None = None) -> dict[str, Any]:
    """Separate the tax a world CHOOSES from the tax the word FORCES on every world.

    An entry whose tax is the same in all 25 worlds contributes the same constant to every total.
    It cannot rank the worlds; it can only make the corpus look expensive or look parallel.  The
    single-operator chains are forced this way by construction (T6), and some multi-operator entries
    turn out to be forced too - which is a measurement, not a prediction, and is reported as one.

    The ranking is then rebuilt on the movable subcorpus alone.  If it does not survive, the headline
    ranking was measuring the corpus rather than the conventions.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = tax_table(corpus, workers)
    rows = table["rows"]
    movable = tuple(row for row in rows if row["movable"])
    forced = tuple(row for row in rows if not row["movable"])
    forced_zero = tuple(row for row in forced if row["tax_min"] == 0)
    forced_positive = tuple(row for row in forced if row["tax_min"] > 0)
    single_operator_forced = tuple(row for row in forced if row["support_size"] <= 1)
    multi_operator_forced = tuple(row for row in forced if row["support_size"] > 1)

    movable_totals = {
        g.id: sum(row["tax"][g.id] for row in movable) for g in GRAMMARS
    }
    forced_floor = sum(row["tax_min"] for row in forced)
    full_ranking = table["tax_ranking"]
    movable_ranking = competition_ranking(movable_totals)
    full_ranks = table["tax_ranks"]
    movable_ranks = {entry["id"]: entry["rank"] for entry in movable_ranking}
    full_spread = table["tax_spread"]
    movable_spread = movable_ranking[-1]["total"] - movable_ranking[0]["total"]
    return {
        "movable_subjects": tuple(row["object"] for row in movable),
        "movable_count": len(movable),
        "forced_subjects": tuple(row["object"] for row in forced),
        "forced_count": len(forced),
        "forced_at_zero": tuple(row["object"] for row in forced_zero),
        "forced_at_zero_count": len(forced_zero),
        "forced_positive": tuple(row["object"] for row in forced_positive),
        "forced_positive_count": len(forced_positive),
        "single_operator_forced": tuple(row["object"] for row in single_operator_forced),
        "single_operator_forced_count": len(single_operator_forced),
        "multi_operator_forced_count": len(multi_operator_forced),
        "forced_floor": forced_floor,
        "movable_tax_totals": movable_totals,
        "movable_ranking": movable_ranking,
        "movable_ranks": movable_ranks,
        "full_spread": full_spread,
        "movable_spread": movable_spread,
        "spread_survival": 1.0 if full_spread == 0 else movable_spread / full_spread,
        "best_full": full_ranking[0]["id"],
        "best_movable": movable_ranking[0]["id"],
        "best_agrees": full_ranking[0]["id"] == movable_ranking[0]["id"],
        "control_rank_full": full_ranks[CONTROL.id],
        "control_rank_movable": movable_ranks[CONTROL.id],
        "control_rank_stable": full_ranks[CONTROL.id] == movable_ranks[CONTROL.id],
        "ranking_identical": tuple(entry["id"] for entry in full_ranking)
        == tuple(entry["id"] for entry in movable_ranking),
        "chain_tax_per_world": {
            g.id: sum(row["tax"][g.id] for row in rows if row["kind"] == "chain")
            for g in GRAMMARS
        },
        "support_invariance": support_invariance(corpus, workers),
    }


# ------------------------------------------------------------------------------ correctness bridge


def round_trip_audit(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """``parse(render(tree, g), g) == tree`` over every same-object writing and all 25 worlds.

    Every cost number is void without it, and so is every depth number: the claim that depth is a
    property of the TREE rather than of the world is exactly the claim that each world recovers the
    tree it was handed.  ``depth_stable`` records that second half explicitly.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan = _scan(tuple(corpus), workers)
    checks = 0
    failures = []
    depth_failures = []
    for subject in corpus:
        leaves, _operators = subject_word(subject)
        for form in scan["same_object"][subject.name]:
            node = rebuild(form, leaves)
            expected = depth(node)
            for grammar in GRAMMARS:
                checks += 1
                text = render(node, grammar, verify=False)
                reparsed = parse(text, grammar)
                if reparsed != node:
                    failures.append(
                        {"object": subject.name, "grammar": grammar.id, "rendering": text}
                    )
                elif depth(reparsed) != expected:  # pragma: no cover - implied by the equality
                    depth_failures.append({"object": subject.name, "grammar": grammar.id})
    return {
        "checks": checks,
        "failures": len(failures),
        "failing": tuple(failures),
        "holds": not failures,
        "depth_failures": len(depth_failures),
        "depth_stable": not depth_failures,
    }


def minimality_audit(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Every bracket counted must be load-bearing: deleting it must change the reparse.

    A rendering carrying one bracket the grammar did not require would inflate exactly the quantity
    the tax is computed from, so minimality is verified by construction rather than argued.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan = _scan(tuple(corpus), workers)
    brackets = 0
    violations = []
    for subject in corpus:
        leaves, _operators = subject_word(subject)
        for form in scan["same_object"][subject.name]:
            node = rebuild(form, leaves)
            for grammar in GRAMMARS:
                for witness in minimality_witnesses(node, grammar):
                    brackets += 1
                    if not witness["required"]:
                        violations.append(
                            {"object": subject.name, "grammar": grammar.id, **witness}
                        )
    return {
        "brackets_checked": brackets,
        "violations": len(violations),
        "violating": tuple(violations),
        "minimal": not violations,
    }


def depth_invariance(
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """The premise, measured: for a FIXED tree the depth is the same in all 25 worlds.

    This is why the naive form of the question ("does the convention change the critical path of
    this expression?") is empty, and why the experiment had to move one level up to the choice of
    writing.  It is checked here rather than assumed.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    scan = _scan(tuple(corpus), workers)
    checks = 0
    distinct = set()
    for subject in corpus:
        leaves, _operators = subject_word(subject)
        for form in scan["same_object"][subject.name]:
            node = rebuild(form, leaves)
            depths = {depth(parse(render(node, g), g)) for g in GRAMMARS}
            checks += len(GRAMMARS)
            distinct.add(len(depths))
    return {
        "checks": checks,
        "always_one_depth": distinct == {1} or not distinct,
        "distinct_depth_counts": tuple(sorted(distinct)),
    }


# ---------------------------------------------------------------------------------- measured pool


def _trivial_chunk(payload: int) -> int:
    """A chunk that does nothing, so timing it times only the pool - and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` is an input to :func:`should_parallelise`, so it is measured here
    rather than carried over.  Minimum of ``repeats`` runs, because a startup time is a floor that
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
    corpus: Sequence[Subject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """Time both paths over the same probe work, check they agree, and record which one wins.

    Repository policy is multicore by default and allows a sequential path only when a measurement
    justifies it.  The probe is the dominant cost of this experiment - over a million exact rational
    evaluations - and the decision is arithmetic on two measured numbers, not on a tree count.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    payloads = _chunks(corpus)
    trees = sum(high - low for _s, low, high in payloads)
    resolved = default_worker_count(len(payloads)) if workers is None else workers

    start = time.perf_counter()
    sequential = _map_chunks(payloads, workers=1)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    parallel = _map_chunks(payloads, workers=resolved)
    parallel_seconds = time.perf_counter() - start

    verdict = should_parallelise(trees, TREE_SECONDS, resolved)
    return {
        "cores": os.cpu_count(),
        "chunks": len(payloads),
        "trees": trees,
        "workers": resolved,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": sequential_seconds / parallel_seconds if parallel_seconds else float("inf"),
        "identical": sequential == parallel,
        "seconds_per_tree": sequential_seconds / trees if trees else 0.0,
        "declared_seconds_per_tree": TREE_SECONDS,
        "parallel_worth_it": verdict,
        "default_path": "parallel" if verdict else "sequential",
    }


# --------------------------------------------------------------------------------------- report


def parallel_worlds_report(
    corpus: Sequence[Subject] | None = None, workers: int | None = None, timing: bool = False
) -> dict[str, Any]:
    """Everything the report prints, in one call."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = tax_table(corpus, workers)
    nulls = null_model(corpus, workers)
    speeds = speedup_table(corpus, workers)
    correlation = rank_correlation(corpus, workers)
    report = {
        "corpus": {
            "subjects": len(corpus),
            "laws": sum(1 for s in corpus if s.kind == "law"),
            "chains": sum(1 for s in corpus if s.kind == "chain"),
            "fields": tuple(sorted({s.field for s in corpus})),
        },
        "filter": filter_audit(corpus, workers),
        "round_trip": round_trip_audit(corpus, workers),
        "minimality": minimality_audit(corpus, workers),
        "depth_invariance": depth_invariance(corpus, workers),
        "tax": table,
        "null_model": nulls,
        "speedup": speeds,
        "rank_correlation": correlation,
        "control_distinction": control_distinction(corpus, workers),
        "headline": {
            "free_somewhere_taxed_in_control": table["objects_free_somewhere_taxed_in_control"],
            "least_taxing_worlds": table["best_worlds"],
            "least_tax": table["best_tax"],
            "control_tax_total": table["control_tax_total"],
            "control_tax_rank": table["control_tax_rank"],
            "chains_forced": nulls["single_operator_forced_count"],
            "movable_subjects": nulls["movable_count"],
            "rank_correlation_full": correlation["full_corpus"],
            "rank_correlation_movable": correlation["movable_subcorpus"],
        },
    }
    if timing:
        report["parallel_decision"] = parallel_decision(corpus, workers)
    return report
