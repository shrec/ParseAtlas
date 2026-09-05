"""Experiment 0049: the Pareto atlas of equivalent writings.

The owner set this card after reading 0037 through 0044, and the sentence that governs every
decision in this module is his:

    "There is no abstractly better until we know the objective."

Four criteria have been measured separately by four earlier cards, and each one produced its own
ranking of the same 25 worlds.  This card refuses to rank at all.  For each mathematical object it
builds the **Pareto frontier of its equivalent writings** under a *declared* axis set, and reports
what a frontier can say that a ranking cannot: how many writings are dominated, how many survive,
whether the conventional world's own habit lands on the frontier, and how many frontier points
another world's habit produces that the conventional world would never write.

What is imported and never restated
-----------------------------------

Every criterion is imported from the module that owns it, and the comment beside each import says
which card that is.  No measure is reimplemented here, and no measure is redefined:

``brackets``
    :func:`parseatlas.notational_cost.parenthesis_cost` -- experiment 0034.  The minimum number of
    bracket pairs the world forces on the tree.  ``render`` re-parses its own output, so the round
    trip is enforced in the path that produces every number and not only in the tests.

``depth``
    :func:`parseatlas.parallel_worlds.depth` -- experiment 0041.  The critical path: a leaf is ``0``,
    an internal node is ``1 + max(children)``.  A structural bound on parallel evaluation, never a
    runtime.

``peak_live``
    :func:`parseatlas.memory_ceiling.peak_live` -- experiment 0044.  The Sethi-Ullman register
    number: how many values are simultaneously live.  A count of values, not of bytes.

``visibility``
    :func:`parseatlas.manifest_properties.manifest_set` -- experiment 0038.  How many of the seven
    declared properties the written form makes manifest.

The writing space itself is 0039's, imported whole: :func:`parseatlas.visibility_ceiling.ceiling_table`
enumerates every parenthesization of every declared writing with no bound at all, discards with an
exact-rational probe at two declared points, and confirms every survivor with SymPy.  This module
reads that table's ``same_object_forms`` and adds nothing to the discipline.

Three costs and one benefit
---------------------------

**``brackets``, ``depth`` and ``peak_live`` are COSTS to MINIMISE.  ``visibility`` is a BENEFIT to
MAXIMISE.**  A sign error here does not crash and does not look wrong; it silently inverts the atlas.
:data:`BENEFIT_AXES` names the exception in one place, :func:`dominates` is the only function that
reads it, and :func:`sign_control` re-runs the whole atlas with the exception removed so the size of
the error is on the page rather than in a comment.

What a frontier is, and what it is not
--------------------------------------

The frontier is the result.  Nothing here compresses the four numbers into one: there is no weighted
sum, no score and no "best representation" column, because choosing the weights *is* choosing the
objective, and the owner's premise is that the objective is not yet known.

One axis is world-relative and three are not.  ``depth``, ``peak_live`` and ``visibility`` are
properties of the tree; only ``brackets`` depends on which world writes it.  So a frontier is drawn
in a **declared reference world**, and the default is ``G0`` -- not because ``G0`` is right, but
because the sharpest question the card asks ("what does the conventional world leave on the table?")
is a question asked in the conventional world's own coordinates.  :func:`reference_world_sweep` runs
the same atlas in all 25 worlds so that the choice is visible as a spread rather than hidden as a
default.
"""

from __future__ import annotations

import itertools
import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from statistics import fmean
from typing import Any

from .grammar import Grammar

# --- the four criteria, each imported from the card that owns it --------------------------------
from .manifest_properties import (  # 0038: visibility, the corpus, and the per-world choice
    CONTROL,
    CORPUS,
    GRAMMARS,
    OBJECT_BY_NAME,
    PROPERTY_NAMES,
    MathObject,
    chosen_writing,
    manifest_set,
    object_tree,
)
from .memory_ceiling import peak_live  # 0044: simultaneously live values (Sethi-Ullman)
from .notational_cost import (  # 0034: minimal bracket count
    minimality_witnesses,
    parenthesis_cost,
    render,
)
from .parallel_worlds import depth  # 0041: critical path
from .parser import Node
from .visibility_ceiling import (  # 0039: the same-object writing space, imported whole
    ceiling_table,
    in_order,
    rebuild,
    to_form,
)

__all__ = [
    "AXES",
    "AXES_3",
    "AXES_4",
    "BENEFIT_AXES",
    "CELL_SECONDS",
    "CHUNK_REPRESENTATIONS",
    "COST_AXES",
    "POOL_STARTUP_SECONDS",
    "WORKER_CAP",
    "WORKER_HEADROOM_CORES",
    "Profile",
    "Representation",
    "atlas",
    "axis_lattice",
    "cell_count",
    "containment_audit",
    "control_bracket_minimum",
    "default_worker_count",
    "dominates",
    "frontier",
    "frontier_audit",
    "incomparability",
    "measure_pool_startup",
    "natural_writing",
    "null_model",
    "order_audit",
    "parallel_decision",
    "pareto_atlas_report",
    "profile",
    "reference_world_sweep",
    "representation_text",
    "representation_tree",
    "round_trip_audit",
    "should_parallelise",
    "sign_control",
    "size_curve",
    "vector",
    "worker_count_for",
    "writings_of",
]


# ------------------------------------------------------------------------------------- the axes

#: The four criteria, in the one canonical order every vector in this module is emitted in.  An axis
#: set given in any order is normalised to this order before a vector is built, so two callers that
#: name the same axes always compare the same tuples.
AXES: tuple[str, ...] = ("brackets", "depth", "peak_live", "visibility")

#: The axes to MINIMISE.  Fewer brackets is better, a shorter critical path is better, fewer
#: simultaneously live values is better.
COST_AXES: frozenset[str] = frozenset({"brackets", "depth", "peak_live"})

#: The axis to MAXIMISE.  More manifest properties is better.  This is the only place in the module
#: where the direction of an axis is declared; :func:`dominates` is the only function that reads it.
BENEFIT_AXES: frozenset[str] = frozenset({"visibility"})

#: The first axis set the owner named.
AXES_3: tuple[str, ...] = ("brackets", "depth", "visibility")

#: The second axis set the owner named: the first, plus peak live values.
AXES_4: tuple[str, ...] = ("brackets", "depth", "peak_live", "visibility")


_NORMALISE_CACHE: dict[tuple[str, ...], tuple[str, ...]] = {}


def _normalise(axes: Sequence[str]) -> tuple[str, ...]:
    """The axis set in canonical order, with unknown or repeated axes refused."""
    seen = tuple(axes)
    cached = _NORMALISE_CACHE.get(seen)
    if cached is not None:
        return cached
    unknown = [axis for axis in seen if axis not in AXES]
    if unknown:
        raise ValueError(f"unknown axes: {unknown!r}")
    if len(set(seen)) != len(seen):
        raise ValueError(f"repeated axis in {seen!r}")
    if not seen:
        raise ValueError("an axis set must name at least one axis")
    order = tuple(axis for axis in AXES if axis in set(seen))
    _NORMALISE_CACHE[seen] = order
    return order


# --------------------------------------------------------------------------- writings and profiles


@dataclass(frozen=True)
class Representation:
    """One written form of one object: a parenthesization that still denotes the same object.

    ``index`` is the position of the declared writing whose token word this parenthesizes, and
    ``form`` is 0039's enumeration form over positional leaf names.  Together with ``object`` the
    pair identifies the tree uniquely, and it is hashable, which is what lets a frontier be a set.
    """

    object: str
    index: int
    role: str
    form: Any


@dataclass(frozen=True)
class Profile:
    """The criteria vector of one representation in one world.

    Three costs and one benefit.  The class carries no total, no score and no ordering: turning four
    numbers into one is exactly the step this experiment refuses to take.
    """

    brackets: int
    depth: int
    peak_live: int
    visibility: int

    def value(self, axis: str) -> int:
        if axis == "brackets":
            return self.brackets
        if axis == "depth":
            return self.depth
        if axis == "peak_live":
            return self.peak_live
        if axis == "visibility":
            return self.visibility
        raise ValueError(f"unknown axis: {axis!r}")


def vector(item: Profile, axes: Sequence[str] = AXES) -> tuple[int, ...]:
    """The profile as a tuple over the named axes, in canonical axis order."""
    return tuple(item.value(axis) for axis in _normalise(axes))


def dominates(left: tuple[int, ...], right: tuple[int, ...], axes: Sequence[str]) -> bool:
    """Whether ``left`` Pareto-dominates ``right`` over ``axes``.

    Strict dominance: at least as good on every axis and strictly better on at least one.  The
    direction of "better" is read from :data:`BENEFIT_AXES` -- **lower is better on a cost axis and
    higher is better on the benefit axis** -- and getting that backwards inverts the whole atlas
    without raising anything, which is why :func:`sign_control` measures the size of the inversion.
    """
    order = _normalise(axes)
    if len(left) != len(order) or len(right) != len(order):
        raise ValueError(f"vectors of length {len(order)} expected for axes {order!r}")
    better = False
    for position, axis in enumerate(order):
        first, second = left[position], right[position]
        if axis in BENEFIT_AXES:
            if first < second:
                return False
            if first > second:
                better = True
        else:
            if first > second:
                return False
            if first < second:
                better = True
    return better


# ------------------------------------------------------------------------------- the writing space
#
# 0039's table is the writing space, imported whole and never recomputed here: the full
# parenthesization space of every declared writing with NO BOUND, an exact-rational probe at two
# declared points that can only discard, and SymPy confirming every survivor.

_SPACE_CACHE: dict[tuple[str, ...], dict[str, Any]] = {}
_LEAF_CACHE: dict[tuple[str, int], tuple[Node, ...]] = {}


def _space(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """0039's ceiling table for this corpus, computed once per process."""
    resolved = tuple(corpus) if corpus is not None else CORPUS
    key = tuple(item.name for item in resolved)
    if key not in _SPACE_CACHE:
        _SPACE_CACHE[key] = ceiling_table(resolved)
    return _SPACE_CACHE[key]


def _leaves(name: str, index: int) -> tuple[Node, ...]:
    """The leaves of one declared writing's token word, cached.

    Read with 0039's :func:`in_order`, which is the same call ``writing_space`` makes before it
    enumerates.  Calling ``writing_space`` here would re-enumerate the whole Catalan space -- 742900
    trees for the longest word in the corpus -- every time a leaf list was wanted.
    """
    key = (name, index)
    if key not in _LEAF_CACHE:
        leaves, _operators = in_order(object_tree(OBJECT_BY_NAME[name].writings[index]))
        _LEAF_CACHE[key] = leaves
    return _LEAF_CACHE[key]


def writings_of(
    item: MathObject | str, corpus: Sequence[MathObject] | None = None
) -> tuple[Representation, ...]:
    """Every parenthesization of every declared writing that denotes the SAME object.

    This is 0039's ``same_object_forms``, read from 0039's own table.  The discipline is not restated
    here: the space is enumerated in full with no bound, an exact rational probe at two declared
    points discards, and SymPy confirms every survivor.
    """
    name = item if isinstance(item, str) else item.name
    row = next(row for row in _space(corpus)["rows"] if row["object"] == name)
    return tuple(
        Representation(name, index, entry["role"], form)
        for index, entry in enumerate(row["writings"])
        for form in entry["same_object_forms"]
    )


def representation_tree(rep: Representation) -> Node:
    """The parser tree of a representation, rebuilt over the word's own leaves."""
    return rebuild(rep.form, _leaves(rep.object, rep.index))


def representation_text(rep: Representation, world: Grammar = CONTROL) -> str:
    """The representation as ``world`` writes it, with the brackets that world requires."""
    return render(representation_tree(rep), world)


def profile(rep: Representation, world: Grammar = CONTROL) -> Profile:
    """The criteria vector of one representation in one world.

    Only ``brackets`` depends on the world; ``depth``, ``peak_live`` and ``visibility`` are
    properties of the tree.  The manifest set is world-independent under 0038's transparent regime,
    which 0039 checked over all 667 same-object trees against all 25 worlds with zero mismatches;
    it is passed ``world`` anyway so that no caller can accidentally read a different regime.
    """
    tree = representation_tree(rep)
    variable = OBJECT_BY_NAME[rep.object].variable
    return Profile(
        brackets=parenthesis_cost(tree, world),  # 0034
        depth=depth(tree),  # 0041
        peak_live=peak_live(tree),  # 0044
        visibility=len(manifest_set(tree, world, variable)),  # 0038
    )


# ----------------------------------------------------------------------------------- the grid
#
# The profile grid is (representation x world).  It is computed once and reused by every question,
# because a frontier, an incomparability count and a world sweep all read the same numbers.

#: Representations per chunk; each carries 25 cells, one per world.  Chosen so the whole corpus
#: splits into more chunks (``44``) than there are workers (``12``) while a chunk still holds enough
#: work to hide its own dispatch.
CHUNK_REPRESENTATIONS: int = 48

#: Cores kept free so a sweep cannot starve the interactive session (0038/0039/0044 policy).
WORKER_HEADROOM_CORES: int = 2

#: Upper bound on the spawn cost any one sweep has to amortise (0038/0039/0044 policy).
WORKER_CAP: int = 12

#: Measured cost of raising a spawn-start pool whose workers each import this module, and so SymPy.
#:
#: **Measured here, not inherited.**  :func:`measure_pool_startup` raises a pool of the default
#: worker count and runs one trivial chunk in each.  Observed minima on 16 cores with 12 workers,
#: while two other cards were running on the same machine: ``0.897``, ``1.075``, ``1.107``,
#: ``1.232``.  The FLOOR is declared, not the typical value, because a smaller startup cost is the
#: reading that FAVOURS the pool, and the pool still loses on this corpus at the floor.  The margin
#: is thin -- ``16675`` cells against a crossover of ``17225`` -- and :func:`parallel_decision`
#: reports it rather than hiding it: the pool lost eight of the nine recorded runs and won the
#: ninth, on the least loaded one, by ``1.269``.
POOL_STARTUP_SECONDS: float = 0.9

#: Measured seconds for one ``(representation, world)`` cell: one render with its verifying reparse,
#: plus one depth, one peak-live and one manifest set per representation.  Recorded run: ``16675``
#: cells in ``0.9427`` s on the sequential path, minimum of three, i.e. ``5.653e-5`` s each; this
#: constant rounds it up.  See :func:`parallel_decision`.
CELL_SECONDS: float = 5.7e-05


def worker_count_for(cores: int, chunk_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``chunk_count`` independent chunks."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(chunk_count, 1)))


def default_worker_count(chunk_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, chunk_count)


def should_parallelise(cells: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising, from the measured per-cell cost and the measured spawn cost."""
    if workers <= 1 or cells <= 1:
        return False
    sequential = cells * seconds_per_cell
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _profile_chunk(
    payload: tuple[str, tuple[tuple[int, str, Any], ...]],
) -> tuple[tuple[tuple[str, int, Any], dict[str, Any]], ...]:
    """Profile one chunk of representations in every world.

    Module level on purpose: a spawn-start pool can only pickle top-level functions.  The chunk
    returns plain integers so the payload crossing the process boundary stays small.
    """
    name, entries = payload
    item = OBJECT_BY_NAME[name]
    out = []
    for index, role, form in entries:
        rep = Representation(name, index, role, form)
        tree = representation_tree(rep)
        out.append(
            (
                (name, index, form),
                {
                    "depth": depth(tree),
                    "peak_live": peak_live(tree),
                    "visibility": len(manifest_set(tree, CONTROL, item.variable)),
                    "brackets": {
                        grammar.id: parenthesis_cost(tree, grammar) for grammar in GRAMMARS
                    },
                },
            )
        )
    return tuple(out)


def _chunks(
    reps: Sequence[Representation],
) -> tuple[tuple[str, tuple[tuple[int, str, Any], ...]], ...]:
    by_object: dict[str, list[tuple[int, str, Any]]] = {}
    for rep in reps:
        by_object.setdefault(rep.object, []).append((rep.index, rep.role, rep.form))
    payloads = []
    for name, entries in by_object.items():
        for low in range(0, len(entries), CHUNK_REPRESENTATIONS):
            payloads.append((name, tuple(entries[low : low + CHUNK_REPRESENTATIONS])))
    return tuple(payloads)


def _map_chunks(payloads: Sequence[Any], workers: int | None) -> list[Any]:
    """Profile every chunk, across processes when the measurement says a pool pays for itself."""
    cells = sum(len(entries) for _name, entries in payloads) * len(GRAMMARS)
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(cells, CELL_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_profile_chunk(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_profile_chunk, payloads, chunksize=1))


_GRID_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}


def _grid(
    corpus: Sequence[MathObject] | None = None, workers: int | None = None
) -> dict[str, Any]:
    """The whole ``(representation x world)`` profile grid, computed once per process."""
    resolved = tuple(corpus) if corpus is not None else CORPUS
    key = (tuple(item.name for item in resolved), workers)
    if key in _GRID_CACHE:
        return _GRID_CACHE[key]
    reps = tuple(rep for item in resolved for rep in writings_of(item, resolved))
    payloads = _chunks(reps)
    raw: dict[tuple[str, int, Any], dict[str, Any]] = {}
    for chunk in _map_chunks(payloads, workers):
        for cell_key, values in chunk:
            raw[cell_key] = values
    profiles = {
        rep: {
            grammar.id: Profile(
                brackets=raw[(rep.object, rep.index, rep.form)]["brackets"][grammar.id],
                depth=raw[(rep.object, rep.index, rep.form)]["depth"],
                peak_live=raw[(rep.object, rep.index, rep.form)]["peak_live"],
                visibility=raw[(rep.object, rep.index, rep.form)]["visibility"],
            )
            for grammar in GRAMMARS
        }
        for rep in reps
    }
    result = {
        "corpus": resolved,
        "representations": reps,
        "by_object": {
            item.name: tuple(rep for rep in reps if rep.object == item.name)
            for item in resolved
        },
        "profiles": profiles,
        "chunks": len(payloads),
    }
    _GRID_CACHE[key] = result
    return result


def cell_count(corpus: Sequence[MathObject] | None = None) -> dict[str, int]:
    """Objects, representations and cells, counted separately so they cannot be confused.

    An OBJECT is one mathematical object; a REPRESENTATION is one same-object parenthesization of
    one of its declared writings; a CELL is one ``(representation, world)`` pair.  Experiment 0047
    was rejected for reporting cell counts where object counts were asked for, so all three are
    reported side by side and never interchanged.
    """
    grid = _grid(corpus)
    return {
        "objects": len(grid["corpus"]),
        "declared_writings": sum(len(item.writings) for item in grid["corpus"]),
        "representations": len(grid["representations"]),
        "worlds": len(GRAMMARS),
        "cells": len(grid["representations"]) * len(GRAMMARS),
    }


# ------------------------------------------------------------------------------------ frontiers


def _vectors(
    name: str, axes: Sequence[str], world: Grammar, grid: dict[str, Any]
) -> dict[Representation, tuple[int, ...]]:
    order = _normalise(axes)
    return {
        rep: vector(grid["profiles"][rep][world.id], order) for rep in grid["by_object"][name]
    }


def _optimal_vectors(
    values: Sequence[tuple[int, ...]], axes: tuple[str, ...]
) -> frozenset[tuple[int, ...]]:
    """The non-dominated members of a set of criteria vectors.

    Dominance is a function of the VECTOR alone, so the frontier is computed over the distinct
    vectors and then mapped back to the writings that carry them.  This is a reduction in work and
    not in meaning: two writings with the same vector are dominated by exactly the same others.  One
    object in this corpus has ``502`` writings and ``50`` distinct 4-axis vectors, so the reduction
    is what makes every sweep in this module finish.
    """
    distinct = sorted(set(values))
    return frozenset(
        candidate
        for candidate in distinct
        if not any(
            dominates(other, candidate, axes) for other in distinct if other != candidate
        )
    )


_FRONTIER_CACHE: dict[tuple[str, tuple[str, ...], str], tuple[Representation, ...]] = {}


def frontier(
    item: MathObject | str,
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> tuple[Representation, ...]:
    """The Pareto-optimal writings of one object under a DECLARED axis set and reference world.

    A writing is on the frontier when no other writing of the same object dominates it.  The axis
    set is a parameter and never a default in disguise: the two sets the owner named are
    :data:`AXES_3` and :data:`AXES_4`, and :func:`axis_lattice` runs all fifteen.
    """
    name = item if isinstance(item, str) else item.name
    grid = _grid(corpus)
    order = _normalise(axes)
    key = (name, order, world.id)
    if corpus is None and key in _FRONTIER_CACHE:
        return _FRONTIER_CACHE[key]
    values = _vectors(name, order, world, grid)
    optimal = _optimal_vectors(tuple(values.values()), order)
    result = tuple(rep for rep in grid["by_object"][name] if values[rep] in optimal)
    if corpus is None:
        _FRONTIER_CACHE[key] = result
    return result


#: Keyed by (object name, world id) only.  Unlike _FRONTIER_CACHE this carries no corpus guard, and
#: `natural_writing` resolves through the module-global OBJECT_BY_NAME rather than through its own
#: `corpus` argument, so a second corpus redefining a same-named object would silently receive the
#: first one's cached answer.  Every call in this module and in its tests passes the default corpus,
#: so no published number is affected -- but the parameter is not honoured here, and review flagged
#: it rather than leave it for whoever first passes a second corpus.
_NATURAL_CACHE: dict[tuple[str, str], Representation] = {}


def natural_writing(
    item: MathObject | str, world: Grammar, corpus: Sequence[MathObject] | None = None
) -> Representation:
    """The writing this world would produce unprompted: 0038's own per-world choice.

    Imported, not restated: :func:`parseatlas.manifest_properties.chosen_writing` picks the declared
    writing this world writes most cheaply in brackets, ties resolved to the declared order, and
    0038's whole visibility table is built on that definition.  The tree is the control parse of
    that writing, which is 0038's model of a written form.
    """
    name = item if isinstance(item, str) else item.name
    key = (name, world.id)
    if key in _NATURAL_CACHE:
        return _NATURAL_CACHE[key]
    resolved = OBJECT_BY_NAME[name]
    writing = chosen_writing(resolved, world)
    index = resolved.writings.index(writing)
    result = Representation(name, index, writing.role, to_form(object_tree(writing)))
    _NATURAL_CACHE[key] = result
    return result


def control_bracket_minimum(
    world: Grammar = CONTROL, corpus: Sequence[MathObject] | None = None
) -> dict[str, Any]:
    """Is the control's natural writing the minimum of the bracket axis over the WHOLE space?

    This is the null model for question 3, and it has to be read before that answer is.  Nothing can
    dominate a writing that is the strict minimum on one axis, so wherever this holds the control
    lands on the frontier **with no information contributed by the other three axes**.  It is an
    observation and not a tautology -- the control chooses among the object's DECLARED writings while
    the space also holds every other parenthesization -- but where it holds, question 3 is answered
    by the bracket axis alone and must not be read as evidence about depth, memory or visibility.
    """
    grid = _grid(corpus)
    rows = []
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        # the CONTROL's writing, priced in the REFERENCE world's brackets: that is the pair the
        # atlas's question 3 asks about, and ``world`` moves only the coordinate, never the habit
        brackets = {rep: grid["profiles"][rep][world.id].brackets for rep in reps}
        natural = natural_writing(item, CONTROL, corpus)
        lowest = min(brackets.values())
        holders = sum(1 for value in brackets.values() if value == lowest)
        rows.append(
            {
                "object": item.name,
                "role": natural.role,
                "natural_brackets": brackets[natural],
                "minimum_brackets": lowest,
                "holders_of_the_minimum": holders,
                "unique_minimum": brackets[natural] == lowest and holders == 1,
                "attains_minimum": brackets[natural] == lowest,
            }
        )
    return {
        "reference_world": world.id,
        "rows": tuple(rows),
        "objects": len(rows),
        "unique_minimum": sum(1 for row in rows if row["unique_minimum"]),
        "attains_minimum": sum(1 for row in rows if row["attains_minimum"]),
        "tied_at_the_minimum": sum(
            1 for row in rows if row["attains_minimum"] and not row["unique_minimum"]
        ),
        "above_the_minimum": sum(1 for row in rows if not row["attains_minimum"]),
        "forced_on_the_frontier": sum(1 for row in rows if row["unique_minimum"]),
    }


# ------------------------------------------------------------------------------- the null model


def null_model(
    world: Grammar = CONTROL, corpus: Sequence[MathObject] | None = None
) -> dict[str, Any]:
    """Which objects can move at all, per axis, so no rate is computed over a fixed point.

    An object whose writings all share one criteria vector carries **no frontier information**: its
    frontier is everything, nothing is dominated, and including it in a rate silently drags that
    rate toward the answer the null model would give.  Every rate this module publishes over a
    "movable" set uses one of the denominators computed here, and says which.
    """
    grid = _grid(corpus)
    rows = []
    per_axis: dict[str, int] = {axis: 0 for axis in AXES}
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        moves = {
            axis: len({grid["profiles"][rep][world.id].value(axis) for rep in reps}) > 1
            for axis in AXES
        }
        for axis, moved in moves.items():
            per_axis[axis] += int(moved)
        distinct4 = len({vector(grid["profiles"][rep][world.id], AXES_4) for rep in reps})
        distinct3 = len({vector(grid["profiles"][rep][world.id], AXES_3) for rep in reps})
        rows.append(
            {
                "object": item.name,
                "representations": len(reps),
                "moves": tuple(axis for axis in AXES if moves[axis]),
                "distinct_vectors_3": distinct3,
                "distinct_vectors_4": distinct4,
                "movable": len(reps) > 1 and distinct4 > 1,
            }
        )
    movable = tuple(row["object"] for row in rows if row["movable"])
    single = tuple(row["object"] for row in rows if row["representations"] == 1)
    return {
        "reference_world": world.id,
        "objects": len(rows),
        "rows": tuple(rows),
        "movable_objects": movable,
        "movable_object_count": len(movable),
        "single_representation_objects": single,
        "single_representation_object_count": len(single),
        "one_vector_objects": tuple(
            row["object"] for row in rows if row["distinct_vectors_4"] == 1
        ),
        "one_vector_object_count": sum(1 for row in rows if row["distinct_vectors_4"] == 1),
        "movable_by_axis": per_axis,
        "movable_representations": sum(
            row["representations"] for row in rows if row["movable"]
        ),
    }


# ---------------------------------------------------------------------------------- the atlas


def atlas(
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """The card's four questions, answered with numbers and never with a ranking.

    1. how many writings are DOMINATED, per object and in total;
    2. how many remain Pareto-OPTIMAL;
    3. how often the control's own default writing is ON the frontier, and how often it is dominated;
    4. how many frontier points another world's natural writing creates that the control would not
       choose -- the owner's sharpest question, and the headline.

    Question 4 has its own denominator and it is reported with the answer: an object where every
    world writes the same form cannot possibly contribute, so the rate is taken over the objects
    where at least one world's natural writing DIFFERS from the control's.
    """
    grid = _grid(corpus)
    order = _normalise(axes)
    control = CONTROL

    rows = []
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        values = _vectors(item.name, order, world, grid)
        optimal = frozenset(frontier(item, order, world, corpus))
        control_rep = natural_writing(item, control, corpus)
        alternatives = {
            natural_writing(item, other, corpus): other.id
            for other in GRAMMARS
            if other.id != control.id
        }
        distinct = {rep: gid for rep, gid in alternatives.items() if rep != control_rep}
        created = tuple(sorted((rep for rep in distinct if rep in optimal), key=repr))
        worlds_creating = tuple(
            sorted(
                {
                    other.id
                    for other in GRAMMARS
                    if other.id != control.id
                    and natural_writing(item, other, corpus) in created
                }
            )
        )
        rows.append(
            {
                "object": item.name,
                "field": item.field,
                "variable": item.variable,
                "representations": len(reps),
                "optimal": len(optimal),
                "dominated": len(reps) - len(optimal),
                "frontier": tuple(
                    {"role": rep.role, "form": rep.form, "vector": values[rep]}
                    for rep in reps
                    if rep in optimal
                ),
                "control_writing": {
                    "role": control_rep.role,
                    "form": control_rep.form,
                    "vector": values[control_rep],
                    "text": representation_text(control_rep, world),
                },
                "control_on_frontier": control_rep in optimal,
                "distinct_natural_alternatives": len(set(distinct)),
                "created": tuple(
                    {
                        "role": rep.role,
                        "form": rep.form,
                        "vector": values[rep],
                        "text": representation_text(rep, world),
                    }
                    for rep in created
                ),
                "created_count": len(created),
                "worlds_creating": worlds_creating,
                "alternatives_dominated": len(set(distinct)) - len(created),
            }
        )

    movable = null_model(world, corpus)
    movable_names = set(movable["movable_objects"])
    with_alternative = tuple(
        row["object"] for row in rows if row["distinct_natural_alternatives"] > 0
    )
    created_total = sum(row["created_count"] for row in rows)
    created_objects = tuple(row["object"] for row in rows if row["created_count"])
    representations = sum(row["representations"] for row in rows)
    optimal_total = sum(row["optimal"] for row in rows)
    movable_reps = sum(row["representations"] for row in rows if row["object"] in movable_names)
    movable_optimal = sum(row["optimal"] for row in rows if row["object"] in movable_names)
    created_by_world: dict[str, int] = {}
    for row in rows:
        for gid in row["worlds_creating"]:
            created_by_world[gid] = created_by_world.get(gid, 0) + 1

    return {
        "axes": order,
        "reference_world": world.id,
        "control": control.id,
        "counts": cell_count(corpus),
        "rows": tuple(rows),
        # 1 and 2
        "representations": representations,
        "optimal": optimal_total,
        "dominated": representations - optimal_total,
        "dominated_fraction": (representations - optimal_total) / representations,
        "movable_objects": len(movable_names),
        "movable_representations": movable_reps,
        "movable_optimal": movable_optimal,
        "movable_dominated": movable_reps - movable_optimal,
        "movable_dominated_fraction": (movable_reps - movable_optimal) / movable_reps,
        "largest_object": max(rows, key=lambda row: row["representations"])["object"],
        "largest_object_share": max(row["representations"] for row in rows) / representations,
        # 3
        "control_on_frontier": sum(1 for row in rows if row["control_on_frontier"]),
        "control_dominated": sum(1 for row in rows if not row["control_on_frontier"]),
        "control_on_frontier_movable": sum(
            1 for row in rows if row["control_on_frontier"] and row["object"] in movable_names
        ),
        # 4
        "created_points": created_total,
        "created_objects": created_objects,
        "created_object_count": len(created_objects),
        "objects_with_a_distinct_natural_alternative": with_alternative,
        "objects_with_a_distinct_natural_alternative_count": len(with_alternative),
        "created_rate_over_objects_with_an_alternative": (
            len(created_objects) / len(with_alternative) if with_alternative else 0.0
        ),
        "alternatives_dominated": sum(row["alternatives_dominated"] for row in rows),
        "created_by_world": created_by_world,
    }


# --------------------------------------------------------------------------- the partial order


def incomparability(
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """The partial order over writings, as 0043 reported one over worlds.

    Every unordered pair of writings of one object is ORDERED (one dominates the other), EQUAL (the
    same criteria vector) or INCOMPARABLE (different vectors, neither dominates).  The three sum to
    ``C(n, 2)`` per object, which is asserted rather than assumed.

    A total ranking has to put every pair in some order.  For an ordered pair the data supplies one;
    for an equal or an incomparable pair it does not, so their sum is the fraction of the landscape a
    total ranking would have to **invent**.  Both a pooled rate and a per-object mean are reported,
    because one object contributes almost all the pairs and the pooled number is its number.
    """
    grid = _grid(corpus)
    order = _normalise(axes)
    rows = []
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        values = _vectors(item.name, order, world, grid)
        # Grouped by criteria vector: dominance depends on the vector alone, so a pair's class is
        # decided once per vector pair and multiplied by how many writings carry each vector.  This
        # is the same count as the pairwise walk, and one object here would otherwise be 125751
        # comparisons of 50 distinct four-axis vectors (32 at three axes).  Review found 31 here
        # and it reproduces from neither axis set.
        counts: dict[tuple[int, ...], int] = {}
        for value in values.values():
            counts[value] = counts.get(value, 0) + 1
        distinct = sorted(counts)
        ordered = incomparable = 0
        equal = sum(count * (count - 1) // 2 for count in counts.values())
        for first, second in itertools.combinations(distinct, 2):
            product = counts[first] * counts[second]
            if dominates(first, second, order) or dominates(second, first, order):
                ordered += product
            else:
                incomparable += product
        pairs = len(reps) * (len(reps) - 1) // 2
        rows.append(
            {
                "object": item.name,
                "representations": len(reps),
                "pairs": pairs,
                "ordered": ordered,
                "incomparable": incomparable,
                "equal": equal,
                "sums": ordered + incomparable + equal == pairs,
            }
        )
    pairs = sum(row["pairs"] for row in rows)
    ordered = sum(row["ordered"] for row in rows)
    incomparable = sum(row["incomparable"] for row in rows)
    equal = sum(row["equal"] for row in rows)
    with_pairs = [row for row in rows if row["pairs"]]
    largest = max(rows, key=lambda row: row["pairs"])
    return {
        "axes": order,
        "reference_world": world.id,
        "rows": tuple(rows),
        "objects": len(rows),
        "objects_with_a_pair": len(with_pairs),
        "pairs": pairs,
        "ordered": ordered,
        "incomparable": incomparable,
        "equal": equal,
        "sums": ordered + incomparable + equal == pairs,
        "all_rows_sum": all(row["sums"] for row in rows),
        "ordered_fraction": ordered / pairs,
        "incomparable_fraction": incomparable / pairs,
        "equal_fraction": equal / pairs,
        "invented_fraction": (incomparable + equal) / pairs,
        "largest_object": largest["object"],
        "largest_object_pair_share": largest["pairs"] / pairs,
        "per_object_mean_ordered": fmean(row["ordered"] / row["pairs"] for row in with_pairs),
        "per_object_mean_incomparable": fmean(
            row["incomparable"] / row["pairs"] for row in with_pairs
        ),
        "per_object_mean_equal": fmean(row["equal"] / row["pairs"] for row in with_pairs),
        "per_object_mean_invented": fmean(
            (row["incomparable"] + row["equal"]) / row["pairs"] for row in with_pairs
        ),
    }


def order_audit(
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """Check on the COMPUTED relation that dominance is a strict partial order.

    Irreflexive, antisymmetric and transitive, checked and not assumed.  Transitivity is checked over
    the DISTINCT criteria vectors of each object rather than over its representations: dominance is a
    function of the vectors alone, so the two quantifications are equivalent, and one object has 502
    representations, whose triples would be 126 million comparisons of the same handful of vectors.
    The number of distinct vectors is reported so the reduction is auditable.
    """
    grid = _grid(corpus)
    order = _normalise(axes)
    reflexive: list[Any] = []
    antisymmetric: list[Any] = []
    transitive: list[Any] = []
    pairs = triples = 0
    distinct_total = 0
    for item in grid["corpus"]:
        values = _vectors(item.name, order, world, grid)
        for rep, value in values.items():
            if dominates(value, value, order):
                reflexive.append((rep.object, rep.role, value))
        for left, right in itertools.combinations(values.values(), 2):
            pairs += 1
            if dominates(left, right, order) and dominates(right, left, order):
                antisymmetric.append((item.name, left, right))
        distinct = sorted(set(values.values()))
        distinct_total += len(distinct)
        for first, second, third in itertools.product(distinct, repeat=3):
            triples += 1
            if (
                dominates(first, second, order)
                and dominates(second, third, order)
                and not dominates(first, third, order)
            ):
                transitive.append((item.name, first, second, third))
    return {
        "axes": order,
        "reference_world": world.id,
        "pairs_checked": pairs,
        "triples_checked": triples,
        "distinct_vectors": distinct_total,
        "irreflexive": not reflexive,
        "antisymmetric": not antisymmetric,
        "transitive": not transitive,
        "reflexive_violations": tuple(reflexive),
        "antisymmetric_violations": tuple(antisymmetric),
        "transitive_violations": tuple(transitive),
    }


def frontier_audit(
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """No reported frontier point is dominated, and no dominated writing is reported optimal."""
    grid = _grid(corpus)
    order = _normalise(axes)
    dominated_on_frontier: list[Any] = []
    optimal_off_frontier: list[Any] = []
    checked = 0
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        values = _vectors(item.name, order, world, grid)
        optimal = frozenset(frontier(item, order, world, corpus))
        for rep in reps:
            checked += 1
            beaten = any(
                dominates(values[other], values[rep], order) for other in reps if other != rep
            )
            if beaten and rep in optimal:
                dominated_on_frontier.append((item.name, rep.role, values[rep]))
            if not beaten and rep not in optimal:
                optimal_off_frontier.append((item.name, rep.role, values[rep]))
    return {
        "axes": order,
        "reference_world": world.id,
        "checked": checked,
        "dominated_on_frontier": tuple(dominated_on_frontier),
        "optimal_off_frontier": tuple(optimal_off_frontier),
        "clean": not dominated_on_frontier and not optimal_off_frontier,
    }


def containment_audit(
    world: Grammar = CONTROL, corpus: Sequence[MathObject] | None = None
) -> dict[str, Any]:
    """Does the 4-axis frontier contain the 3-axis frontier, per object?

    The card asks for this check on the ground that adding an axis can only enlarge a frontier.  That
    reasoning is **not valid in general**, and the reason is ties: if two writings agree on every
    axis of the smaller set and differ on the added one, the loser is dominated in the larger set and
    was not in the smaller.  The containment is therefore a MEASUREMENT here and not a theorem.  The
    number of pairs at risk -- tied on the three axes, different in peak live -- is reported beside
    the result, so a reader can see how close the corpus came to breaking it.
    """
    grid = _grid(corpus)
    rows = []
    at_risk = 0
    risk_on_frontier = 0
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        three = frozenset(frontier(item, AXES_3, world, corpus))
        four = frozenset(frontier(item, AXES_4, world, corpus))
        values3 = _vectors(item.name, AXES_3, world, grid)
        for left, right in itertools.combinations(reps, 2):
            if values3[left] != values3[right]:
                continue
            first = grid["profiles"][left][world.id].peak_live
            second = grid["profiles"][right][world.id].peak_live
            if first == second:
                continue
            at_risk += 1
            loser = left if first > second else right
            if loser in three:
                risk_on_frontier += 1
        rows.append(
            {
                "object": item.name,
                "three": len(three),
                "four": len(four),
                "contained": three <= four,
                "enlargement": len(four) - len(three),
            }
        )
    return {
        "reference_world": world.id,
        "rows": tuple(rows),
        "contained_everywhere": all(row["contained"] for row in rows),
        "failures": tuple(row["object"] for row in rows if not row["contained"]),
        "three_total": sum(row["three"] for row in rows),
        "four_total": sum(row["four"] for row in rows),
        "enlargement_total": sum(row["enlargement"] for row in rows),
        "objects_enlarged": sum(1 for row in rows if row["enlargement"] > 0),
        "objects_unchanged": sum(1 for row in rows if row["enlargement"] == 0),
        "objects_shrunk": sum(1 for row in rows if row["enlargement"] < 0),
        "pairs_at_risk": at_risk,
        "pairs_at_risk_on_the_three_axis_frontier": risk_on_frontier,
    }


# --------------------------------------------------------------------------------- the sweeps


def axis_lattice(
    world: Grammar = CONTROL, corpus: Sequence[MathObject] | None = None
) -> dict[str, Any]:
    """The frontier size for every one of the fifteen non-empty axis sets.

    The ROADMAP asks for the whole range of any parameter that could have been a threshold, and the
    axis set is exactly such a parameter: naming three axes rather than four is a choice that decides
    the answer.  So all fifteen are run and the lattice is published rather than the two the card
    names.  Non-monotone edges -- a SUPERSET with a SMALLER frontier -- are counted and named,
    because they are the shape the ROADMAP tells this project to look for and they are real.
    """
    grid = _grid(corpus)
    sizes: dict[tuple[str, ...], int] = {}
    for size in range(1, len(AXES) + 1):
        for subset in itertools.combinations(AXES, size):
            sizes[subset] = sum(
                len(frontier(item, subset, world, corpus)) for item in grid["corpus"]
            )
    shrinking = tuple(
        {
            "subset": smaller,
            "superset": larger,
            "subset_frontier": sizes[smaller],
            "superset_frontier": sizes[larger],
            "loss": sizes[smaller] - sizes[larger],
        }
        for smaller in sizes
        for larger in sizes
        if set(smaller) < set(larger) and sizes[smaller] > sizes[larger]
    )
    return {
        "reference_world": world.id,
        "sizes": {"+".join(subset): value for subset, value in sizes.items()},
        "edges": sum(
            1 for a in sizes for b in sizes if set(a) < set(b) and len(b) == len(a) + 1
        ),
        "non_monotone_pairs": len(shrinking),
        "non_monotone": shrinking,
        "sharpest_loss": max(shrinking, key=lambda row: row["loss"]) if shrinking else None,
        "three_axis": sizes[tuple(AXES_3)],
        "four_axis": sizes[tuple(AXES_4)],
    }


def reference_world_sweep(
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """The same atlas drawn in all 25 worlds' bracket coordinates.

    Only ``brackets`` is world-relative, so the reference world is the one modelling choice this card
    makes that a reader could disagree with.  It is therefore swept rather than defended: every
    headline is recomputed in every world and the spread is published.
    """
    rows = []
    for world in GRAMMARS:
        entry: dict[str, Any] = {"world": world.id}
        for label, axes in (("three", AXES_3), ("four", AXES_4)):
            result = atlas(axes, world, corpus)
            entry[f"{label}_optimal"] = result["optimal"]
            entry[f"{label}_control_on_frontier"] = result["control_on_frontier"]
            entry[f"{label}_created"] = result["created_points"]
        rows.append(entry)
    return {
        "rows": tuple(rows),
        "worlds": len(rows),
        "four_optimal_range": (
            min(row["four_optimal"] for row in rows),
            max(row["four_optimal"] for row in rows),
        ),
        "four_created_range": (
            min(row["four_created"] for row in rows),
            max(row["four_created"] for row in rows),
        ),
        "four_control_on_frontier_range": (
            min(row["four_control_on_frontier"] for row in rows),
            max(row["four_control_on_frontier"] for row in rows),
        ),
        "three_optimal_range": (
            min(row["three_optimal"] for row in rows),
            max(row["three_optimal"] for row in rows),
        ),
        "three_created_range": (
            min(row["three_created"] for row in rows),
            max(row["three_created"] for row in rows),
        ),
    }


def size_curve(
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """Frontier size against the number of equivalent writings an object has.

    The writing count is the other parameter that could have been a threshold -- an experiment that
    capped it would have decided the answer -- so the whole observed range is published as a curve
    rather than a point, and it is stated whether the curve turns.
    """
    grid = _grid(corpus)
    buckets: dict[int, list[tuple[str, int]]] = {}
    for item in grid["corpus"]:
        size = len(grid["by_object"][item.name])
        buckets.setdefault(size, []).append(
            (item.name, len(frontier(item, axes, world, corpus)))
        )
    rows = tuple(
        {
            "representations": size,
            "objects": len(entries),
            "mean_frontier": fmean(count for _name, count in entries),
            "mean_optimal_fraction": fmean(count / size for _name, count in entries),
            "members": tuple(name for name, _count in entries),
        }
        for size, entries in sorted(buckets.items())
    )
    turns = tuple(
        {
            "from": rows[index - 1]["representations"],
            "to": rows[index]["representations"],
            "from_fraction": rows[index - 1]["mean_optimal_fraction"],
            "to_fraction": rows[index]["mean_optimal_fraction"],
        }
        for index in range(1, len(rows))
        if rows[index]["mean_optimal_fraction"] > rows[index - 1]["mean_optimal_fraction"]
    )
    return {
        "axes": _normalise(axes),
        "reference_world": world.id,
        "rows": rows,
        "monotone": not turns,
        "rises": turns,
        "rise_count": len(turns),
    }


def sign_control(
    axes: Sequence[str] = AXES_4,
    world: Grammar = CONTROL,
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """What the atlas would say if the benefit axis were handled as a cost.

    A sign error on ``visibility`` raises nothing and changes no shape; it changes the answer.  This
    function computes the atlas with :data:`BENEFIT_AXES` emptied, so that the size of the error is a
    published number rather than a warning in a docstring.
    """
    grid = _grid(corpus)
    order = _normalise(axes)

    def wrong(left: tuple[int, ...], right: tuple[int, ...]) -> bool:
        better = False
        for first, second in zip(left, right):
            if first > second:
                return False
            if first < second:
                better = True
        return better

    optimal = 0
    control_on = 0
    for item in grid["corpus"]:
        reps = grid["by_object"][item.name]
        values = _vectors(item.name, order, world, grid)
        surviving = [
            rep
            for rep in reps
            if not any(wrong(values[other], values[rep]) for other in reps if other != rep)
        ]
        optimal += len(surviving)
        if natural_writing(item, CONTROL, corpus) in set(surviving):
            control_on += 1
    correct = atlas(order, world, corpus)
    return {
        "axes": order,
        "reference_world": world.id,
        "correct_optimal": correct["optimal"],
        "inverted_optimal": optimal,
        "difference": optimal - correct["optimal"],
        "correct_control_on_frontier": correct["control_on_frontier"],
        "inverted_control_on_frontier": control_on,
        "note": (
            "the control headline is unchanged by the inversion and the frontier size is not; "
            "a sign error would have been invisible in question 3 alone"
        ),
    }


# ------------------------------------------------------------------------- correctness bridges


def round_trip_audit(
    world: Grammar | None = None, corpus: Sequence[MathObject] | None = None
) -> dict[str, Any]:
    """Every representation, rendered in every world and re-parsed back to the same tree.

    ``render`` already verifies its own output, so this sweep is a second, explicit pass over the
    whole grid: the bracket axis is only meaningful if the string the world writes reads back as the
    tree that was measured.
    """
    from .parser import parse

    grid = _grid(corpus)
    worlds = GRAMMARS if world is None else (world,)
    failures = []
    checked = 0
    verified = 0
    for rep in grid["representations"]:
        tree = representation_tree(rep)
        for grammar in worlds:
            checked += 1
            text = render(tree, grammar)
            if parse(text, grammar) == tree:
                verified += 1
            else:  # pragma: no cover - render already raises before reaching here
                failures.append({"object": rep.object, "world": grammar.id, "text": text})
    return {
        "cells": checked,
        # counted forwards, so the audit reports how many round trips were WITNESSED and not merely
        # how many counterexamples were missed
        "verified": verified,
        "failures": tuple(failures),
        "failure_count": checked - verified,
    }


def minimality_audit(
    world: Grammar | None = None, corpus: Sequence[MathObject] | None = None
) -> dict[str, Any]:
    """Every bracket in every rendering is required: deleting it changes the tree or breaks the parse.

    Without this the bracket axis would be an upper bound rather than a cost, and a frontier drawn on
    an upper bound is not a frontier.
    """
    grid = _grid(corpus)
    worlds = GRAMMARS if world is None else (world,)
    surplus = []
    brackets = 0
    required = 0
    cells = 0
    for rep in grid["representations"]:
        tree = representation_tree(rep)
        for grammar in worlds:
            cells += 1
            for witness in minimality_witnesses(tree, grammar):
                brackets += 1
                if witness["required"]:
                    required += 1
                else:
                    surplus.append(
                        {
                            "object": rep.object,
                            "world": grammar.id,
                            "rendering": witness["rendering"],
                        }
                    )
    return {
        "cells": cells,
        "brackets_checked": brackets,
        # ``brackets_required`` is counted forwards: it is the number of brackets for which a
        # witness was PRODUCED -- deleting the pair changed the tree or broke the parse.  Reporting
        # only the surplus would let an audit that never fires read exactly like a clean one.
        "brackets_required": required,
        "surplus": tuple(surplus),
        "surplus_count": brackets - required,
    }


def space_provenance(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Assert that the writing space IS 0039's, and that no bound was applied to it."""
    table = _space(corpus)
    grid = _grid(corpus)
    return {
        "space_total": table["space_total"],
        "trees_probed": table["trees_probed"],
        "no_bound_applied": table["trees_probed"] == table["space_total"],
        "probe_survivors": table["probe_survivors"],
        "same_object_trees": table["same_object_trees"],
        "probe_discarded_nothing_sympy_would_keep": (
            table["probe_survivors"] == table["same_object_trees"]
        ),
        "representations": len(grid["representations"]),
        "representations_match_0039": (
            len(grid["representations"]) == table["same_object_trees"]
        ),
        "properties": PROPERTY_NAMES,
    }


# ------------------------------------------------------------------------------- the parallel path


def _trivial_chunk(payload: int) -> int:
    """A chunk that does nothing, so that timing it times only the pool -- and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` is an input to :func:`should_parallelise`, so it is measured here
    rather than inherited from an earlier card.  Minimum of ``repeats`` runs: a startup time is a
    floor that background load can only push up.
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


def parallel_decision(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Time both paths over the same grid, check they agree, and record which one the policy picks.

    The heavy stage of this card is not this grid: it is 0039's enumeration of ``1510820`` trees,
    which is imported and which runs across processes under 0039's own measured decision.  What is
    measured here is the stage this card adds, and the honest outcome is reported whichever way it
    falls -- the repository's policy is that a sequential path is valid when the measurement says so.
    """
    resolved = tuple(corpus) if corpus is not None else CORPUS
    reps = tuple(rep for item in resolved for rep in writings_of(item, resolved))
    payloads = _chunks(reps)
    cells = len(reps) * len(GRAMMARS)
    workers = default_worker_count(len(payloads))

    start = time.perf_counter()
    sequential = _map_chunks(payloads, workers=1)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    parallel = _map_chunks(payloads, workers=workers)
    parallel_seconds = time.perf_counter() - start

    return {
        "cores": os.cpu_count(),
        "chunks": len(payloads),
        "representations": len(reps),
        "cells": cells,
        "workers": workers,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": sequential_seconds / parallel_seconds if parallel_seconds else float("inf"),
        "identical": sequential == parallel,
        "seconds_per_cell": sequential_seconds / cells if cells else 0.0,
        "declared_seconds_per_cell": CELL_SECONDS,
        "parallel_worth_it": should_parallelise(cells, CELL_SECONDS, workers),
        "default_path": (
            "parallel" if should_parallelise(cells, CELL_SECONDS, workers) else "sequential"
        ),
        "note": (
            "the dominant stage of this card is 0039's enumeration, imported, which runs in "
            "parallel under 0039's own measured decision"
        ),
    }


# ------------------------------------------------------------------------------------- the report


def pareto_atlas_report(corpus: Sequence[MathObject] | None = None) -> dict[str, Any]:
    """Everything the report prints, in one call."""
    three = atlas(AXES_3, CONTROL, corpus)
    four = atlas(AXES_4, CONTROL, corpus)
    return {
        "provenance": space_provenance(corpus),
        "counts": cell_count(corpus),
        "null_model": null_model(CONTROL, corpus),
        "control_bracket_minimum": control_bracket_minimum(CONTROL, corpus),
        "three_axis": three,
        "four_axis": four,
        "containment": containment_audit(CONTROL, corpus),
        "incomparability_three": incomparability(AXES_3, CONTROL, corpus),
        "incomparability_four": incomparability(AXES_4, CONTROL, corpus),
        "order_three": order_audit(AXES_3, CONTROL, corpus),
        "order_four": order_audit(AXES_4, CONTROL, corpus),
        "frontier_audit_three": frontier_audit(AXES_3, CONTROL, corpus),
        "frontier_audit_four": frontier_audit(AXES_4, CONTROL, corpus),
        "axis_lattice": axis_lattice(CONTROL, corpus),
        "reference_world_sweep": reference_world_sweep(corpus),
        "size_curve": size_curve(AXES_4, CONTROL, corpus),
        "sign_control_three": sign_control(AXES_3, CONTROL, corpus),
        "sign_control_four": sign_control(AXES_4, CONTROL, corpus),
        "headline": {
            "created_points_four": four["created_points"],
            "created_points_three": three["created_points"],
            "created_objects_four": four["created_object_count"],
            "created_denominator": four["objects_with_a_distinct_natural_alternative_count"],
            "control_on_frontier": four["control_on_frontier"],
            "control_dominated": four["control_dominated"],
            "control_forced_on_the_frontier": control_bracket_minimum(CONTROL, corpus)[
                "forced_on_the_frontier"
            ],
            "optimal_four": four["optimal"],
            "dominated_four": four["dominated"],
            "optimal_three": three["optimal"],
            "dominated_three": three["dominated"],
        },
    }
