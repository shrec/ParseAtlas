"""Experiment 0043: reachability outranks cost.

Every ranking this project has published is a **cost** ranking.  Experiment 0034 priced mixed
practical formulas, 0037 priced named laws field by field, 0038 counted what each world makes
visible.  All three are total orders, and a total order over cost says nothing about the question
the owner asked on 2026-09-04:

    The criterion is not always speed.  Sometimes a task is UNREACHABLE in representation A and
    becomes REACHABLE in B - even if B is slow.

This module builds the ranking that was missing.  A **task** is a declared ``(object,
requirement)`` pair; :func:`reachable` answers whether a world can do it **at all**, and every
report keeps the two questions in separate columns:

``reachable``
    is there a writing of this object that this world can render within the declared bracket
    budget and that makes the requirement true?
``free``
    does the requirement already hold in the writing this world would reach for anyway - the
    cheapest one, which is what experiment 0038 measured?
``premium``
    when a task is reachable but not free, how many extra bracket pairs does the witness cost in
    that world?  That number is the price of seeing something your convention does not show you,
    and it is never allowed to masquerade as impossibility.

The three requirement kinds, and the rule for each
--------------------------------------------------

The kinds are declared in :data:`REQUIREMENTS`, each with the name of its rule:

===================  ===========================  =======================================================
kind                 rule                         what it demands
===================  ===========================  =======================================================
``property``         ``manifest_in_some_writing``  one writing, within budget, whose imported 0038 shape
                                                   rules make the named property manifest
``property_pair``    ``simultaneous_in_one_writing`` ONE writing, within budget, that makes BOTH named
                                                   properties manifest at the same time - two writings
                                                   each showing one is not enough, and this is where 0038
                                                   found the hard limits
``writable``         ``within_bracket_budget``     one writing this world renders with no more bracket
                                                   pairs than the budget, with no visibility demand at all
===================  ===========================  =======================================================

The bracket budget, and why it is the load-bearing declaration
--------------------------------------------------------------

A form that needs more brackets than a reader will tolerate is unreachable in practice.
:data:`BRACKET_BUDGET` makes that judgement **explicit and adjustable** instead of hidden, and it
is a declaration, not a measurement: nothing here measures a reader.

It is also load-bearing in a way that has to be said in the first section rather than the limits.
Under the primary ``transparent`` regime the manifest set of a *written form* does not depend on
the grammar - 0038 declares this and 0039 verified it over 16675 checks - so with **no** budget at
all, "is this property manifest in some writing of this object" has the same answer in all
twenty-five worlds.  :func:`budget_sweep` reports that as the null it is: at budget ``8`` the
routable set is empty.  **The budget is what turns cost into reachability**, and therefore the
reach ranking is not independent of the cost ranking; :func:`cost_vs_reach` measures how much they
still disagree rather than pretending they are unrelated.

Two things stop that from being circular.  First, the ``opaque`` regime of 0038 - where a bracket
hides what is inside it - makes the manifest set genuinely world-dependent, so its routable set
survives an unbounded budget; it is computed here as the robustness check, exactly as 0038 uses it.
Second, :func:`budget_sweep` publishes every budget from ``0`` to ``8`` in both regimes, so a reader
who disagrees with the declared threshold can read their own answer off the table.

What is imported and never recomputed
-------------------------------------

* the corpus, the seven properties, their shape rules, ``ground_truth`` and ``manifest_set`` come
  from :mod:`parseatlas.manifest_properties` **by identity**, not by copy;
* the bracket rule and the round-trip guarantee come from
  :func:`parseatlas.notational_cost.render`;
* the 0037 cost ranking comes from :func:`parseatlas.domain_worlds.field_table`.  It is read, not
  re-derived, so a rank in this experiment means what a rank in 0037 means.

The null model
--------------

A task reachable in all twenty-five worlds, or in none of them, carries no ranking information: the
first adds the same constant to every world, the second subtracts nothing from any.  Only the
**routable set** - reachable in some and not all - can order conventions.  :func:`reachability_table`
reports the three-way split first and every ranking in this module is computed over the routable set
alone, which is stated at each call site rather than left implicit.
"""

from __future__ import annotations

import math
import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import combinations
from statistics import fmean
from typing import Any

from .domain_worlds import field_table
from .grammar import Grammar
from .manifest_properties import (
    CONTROL,
    CORPUS,
    GRAMMARS,
    OBJECT_BY_NAME,
    PROPERTIES,
    PROPERTY_NAMES,
    MathObject,
    bridge_audit,
    chosen_writing,
    ground_truth,
    manifest_set,
    object_tree,
    visibility_table,
)
from .notational_cost import render

__all__ = [
    "BRACKET_BUDGET",
    "BUDGET_SWEEP",
    "CELL_SECONDS",
    "CONTROL",
    "CORPUS",
    "FACTOR_BLIND_EXPECTED",
    "GRAMMARS",
    "OBJECT_BY_NAME",
    "POOL_STARTUP_SECONDS",
    "PROPERTIES",
    "PROPERTY_NAMES",
    "RANK_GAP",
    "REGIMES",
    "REQUIREMENTS",
    "TASK_KINDS",
    "MathObject",
    "Reach",
    "Requirement",
    "Task",
    "bridge",
    "budget_sweep",
    "ceiling_crosscheck",
    "cost_ranking",
    "cost_vs_reach",
    "default_worker_count",
    "dominance",
    "factor_blindness",
    "grid_index",
    "ground_truth",
    "manifest_set",
    "measure_cell_seconds",
    "measure_pool_startup",
    "object_tree",
    "parallel_decision",
    "reachability_first_report",
    "reachability_table",
    "reachable",
    "should_parallelise",
    "slow_but_possible",
    "tasks",
    "witness_audit",
    "worker_count_for",
]


#: The declared bracket budget: a written form may carry at most this many bracket pairs before a
#: reader is taken to reject it, and a task whose only witness exceeds it is unreachable in that
#: world.
#:
#: **This is a declaration and not a fact about readers.**  It is set to ``2`` because two bracket
#: pairs is what the conventional grammar ``G0`` already demands of thirty-three of this corpus's
#: thirty-four objects when each is written in the form ``G0`` prefers - so the threshold is
#: calibrated to what today's convention itself requires, which makes it *generous to ``G0``* and
#: therefore makes every finding against ``G0`` conservative.  The one object it does not cover is
#: ``distance_components``, which ``G0`` cannot write in fewer than four brackets; that object turns
#: up in the results as unreachable in ``G0``, which is the threshold doing its job rather than an
#: accident.  :func:`budget_sweep` publishes budgets ``0`` through ``8`` so the threshold can be
#: argued with by reading a different row.
BRACKET_BUDGET: int = 2

#: Every budget worth reporting: ``0`` forbids brackets outright, ``8`` is the largest bracket count
#: any writing in this corpus reaches in any world and therefore excludes nothing.
BUDGET_SWEEP: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7, 8)

#: The two rule regimes of experiment 0038.  ``transparent`` is primary.
REGIMES: tuple[str, ...] = ("transparent", "opaque")

#: The five worlds experiment 0038 reports as never showing ``factor_structure``.  It is written
#: down here so :func:`factor_blindness` can re-derive it independently and say whether it agrees,
#: rather than importing the answer it is supposed to be checking.
FACTOR_BLIND_EXPECTED: tuple[str, ...] = ("G0", "G15", "G16", "G18", "G24")

#: Rank displacement (reach rank minus cost rank) at which a world is called cheap-and-weak or
#: dear-and-strong.  Declared, and equal to one third of the twenty-five worlds rounded down.
RANK_GAP: int = 8


# ------------------------------------------------------------------------------- the requirements


@dataclass(frozen=True)
class Requirement:
    """One kind of thing a task can ask a world for, with the name of its rule and the rule itself."""

    kind: str
    rule: str
    prose: str

    def holds(self, manifest: frozenset[str], properties: tuple[str, ...]) -> bool:
        """Whether one writing's manifest set satisfies this requirement."""
        if self.kind == "writable":
            return True
        return all(name in manifest for name in properties)


REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement(
        kind="property",
        rule="manifest_in_some_writing",
        prose=(
            "the world can write the object in at least one of its declared writings, within the "
            "bracket budget, whose written form the imported 0038 shape rules make the named "
            "property manifest in"
        ),
    ),
    Requirement(
        kind="property_pair",
        rule="simultaneous_in_one_writing",
        prose=(
            "ONE writing, within the bracket budget, makes BOTH named properties manifest at the "
            "same time; two writings each showing one of them does not satisfy this requirement, "
            "and that is precisely where experiment 0038 found the hard limits"
        ),
    ),
    Requirement(
        kind="writable",
        rule="within_bracket_budget",
        prose=(
            "the object has at least one writing this world renders with no more bracket pairs "
            "than the declared budget - no visibility is demanded, only that the object can be put "
            "on the page at a price a reader tolerates"
        ),
    ),
)

REQUIREMENT_BY_KIND: dict[str, Requirement] = {item.kind: item for item in REQUIREMENTS}

TASK_KINDS: tuple[str, ...] = tuple(item.kind for item in REQUIREMENTS)


# -------------------------------------------------------------------------------------- the tasks


@dataclass(frozen=True)
class Task:
    """A declared ``(object, requirement)`` pair.

    ``properties`` is empty for a ``writable`` task, holds one name for a ``property`` task and two
    for a ``property_pair`` task.  Every property named here is one ``ground_truth`` says is TRUE of
    the object, so a task never asks a world to show something that is not there.
    """

    object: str
    kind: str
    properties: tuple[str, ...]

    @property
    def requirement(self) -> Requirement:
        return REQUIREMENT_BY_KIND[self.kind]

    @property
    def name(self) -> str:
        if not self.properties:
            return f"{self.object}:writable"
        return f"{self.object}:{'+'.join(self.properties)}"


def tasks(corpus: Sequence[MathObject] | None = None) -> tuple[Task, ...]:
    """Every task, built from the imported corpus and the properties ground truth calls TRUE.

    No object is invented: the corpus is :data:`parseatlas.manifest_properties.CORPUS`, which is
    experiment 0037's thirty-three named laws plus the calibration quadratic.  For each object the
    tasks are every true property, every unordered pair of true properties, and one ``writable``
    task.  Asking a world to show a property the object does not have would be a defect, not a
    finding, so ground truth - the SymPy control, not the shape rules - decides what is asked.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    built: list[Task] = []
    for item in corpus:
        truth = set(ground_truth(object_tree(item.writings[0]), item.variable))
        present = tuple(name for name in PROPERTY_NAMES if name in truth)
        for name in present:
            built.append(Task(item.name, "property", (name,)))
        for first, second in combinations(present, 2):
            built.append(Task(item.name, "property_pair", (first, second)))
        built.append(Task(item.name, "writable", ()))
    return tuple(built)


# ------------------------------------------------------------------------------------- the grid
#
# One cell is one (writing, world): what the world's rendering of that writing costs in brackets,
# and what the imported shape rules make manifest in it under each regime.  Everything downstream is
# dictionary lookup, so this is the only part worth spending time - or processes - on.


def _cell(payload: tuple[str, str, str]) -> dict[str, Any]:
    """One ``(object, writing role, world)`` cell, computed from imported functions only."""
    object_name, role, grammar_id = payload
    item = OBJECT_BY_NAME[object_name]
    writing = next(entry for entry in item.writings if entry.role == role)
    grammar = next(entry for entry in GRAMMARS if entry.id == grammar_id)
    tree = object_tree(writing)
    text = render(tree, grammar)
    return {
        "object": object_name,
        "role": role,
        "grammar": grammar_id,
        "text": text,
        "cost": text.count("("),
        "transparent": tuple(manifest_set(tree, grammar, item.variable, False)),
        "opaque": tuple(manifest_set(tree, grammar, item.variable, True)),
    }


def grid_index(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Cost and manifest set for every ``(writing, world)``, plus each world's default writing.

    The ``default`` map is 0038's own choice - the cheapest writing, ties to the declared order -
    and it is what the ``free`` column is measured against.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [
        (item.name, writing.role, grammar.id)
        for item in corpus
        for writing in item.writings
        for grammar in grammars
    ]
    cells = _map_cells(payloads, workers)
    cost: dict[tuple[str, str, str], int] = {}
    text: dict[tuple[str, str, str], str] = {}
    manifest: dict[str, dict[tuple[str, str, str], frozenset[str]]] = {
        "transparent": {},
        "opaque": {},
    }
    for cell in cells:
        key = (cell["object"], cell["role"], cell["grammar"])
        cost[key] = cell["cost"]
        text[key] = cell["text"]
        manifest["transparent"][key] = frozenset(cell["transparent"])
        manifest["opaque"][key] = frozenset(cell["opaque"])
    default = {
        (item.name, grammar.id): chosen_writing(item, grammar).role
        for item in corpus
        for grammar in grammars
    }
    return {
        "objects": tuple(item.name for item in corpus),
        "grammars": tuple(grammar.id for grammar in grammars),
        "roles": {item.name: item.roles for item in corpus},
        "cells": len(cells),
        "cost": cost,
        "text": text,
        "manifest": manifest,
        "default": default,
    }


# ---------------------------------------------------------------------------------- reachability


@dataclass(frozen=True)
class Reach:
    """What one world can do with one task, with expense and impossibility kept apart.

    ``blocked_by`` is the whole point of the record.  ``"no_witness"`` means **no writing of this
    object satisfies the requirement at any price** - impossible under our declared shape rules.
    ``"budget"`` means a witness exists and this world writes it too expensively - expensive, not
    impossible.  The two are never summed.
    """

    reachable: bool
    witness: str | None
    cost: int | None
    free: bool
    default_role: str
    default_cost: int
    premium: int | None
    blocked_by: str | None

    @property
    def paid(self) -> bool:
        """Reachable, but not in the writing this world would have reached for anyway."""
        return self.reachable and not self.free


def reachable(
    task: Task,
    world: Grammar | str,
    budget: int = BRACKET_BUDGET,
    regime: str = "transparent",
    index: dict[str, Any] | None = None,
) -> Reach:
    """Can ``world`` do ``task`` AT ALL, independent of what it costs?

    The rule is the one :data:`REQUIREMENTS` names for the task's kind, applied to every declared
    writing of the object: a writing is a **witness** when the world renders it within ``budget``
    and the requirement holds of that rendering.  The cheapest witness is reported, together with
    what the world's default writing would have cost and whether the requirement already held there.

    ``index`` is an optional precomputed :func:`grid_index`; without it the cell is computed on the
    spot, which is what makes this function usable on its own.
    """
    grammar_id = world if isinstance(world, str) else world.id
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r}; expected one of {REGIMES}")
    item = OBJECT_BY_NAME[task.object]
    requirement = task.requirement

    def cell(role: str) -> tuple[int, frozenset[str]]:
        if index is not None:
            key = (task.object, role, grammar_id)
            return index["cost"][key], index["manifest"][regime][key]
        computed = _cell((task.object, role, grammar_id))
        return computed["cost"], frozenset(computed[regime])

    if index is not None:
        default_role = index["default"][(task.object, grammar_id)]
    else:
        grammar = next(entry for entry in GRAMMARS if entry.id == grammar_id)
        default_role = chosen_writing(item, grammar).role
    default_cost, default_manifest = cell(default_role)

    witnesses: list[tuple[int, str]] = []
    any_witness = False
    for writing in item.writings:
        cost, manifest = cell(writing.role)
        if not requirement.holds(manifest, task.properties):
            continue
        any_witness = True
        if cost <= budget:
            witnesses.append((cost, writing.role))

    if not witnesses:
        return Reach(
            reachable=False,
            witness=None,
            cost=None,
            free=False,
            default_role=default_role,
            default_cost=default_cost,
            premium=None,
            blocked_by="budget" if any_witness else "no_witness",
        )
    # ``free`` is asked only of a reachable task, because "the writing this world would have
    # reached for anyway" means nothing when the world cannot write the object at all.  No budget
    # clause is needed here: the default writing is the CHEAPEST one, so the existence of a witness
    # within budget already implies ``default_cost <= budget``.  That implication is pinned by a
    # test over the whole grid rather than left as a redundant guard nobody could falsify.
    cost, role = min(witnesses)
    return Reach(
        reachable=True,
        witness=role,
        cost=cost,
        free=requirement.holds(default_manifest, task.properties),
        default_role=default_role,
        default_cost=default_cost,
        premium=cost - default_cost,
        blocked_by=None,
    )


# ------------------------------------------------------------------------------ the main table


def reachability_table(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    budget: int = BRACKET_BUDGET,
    regime: str = "transparent",
    workers: int | None = None,
    index: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Tasks x worlds, boolean - and the three-way split that says which part can carry a ranking.

    The split comes first because the null model bites here harder than anywhere:

    * **reachable everywhere** - convention-independent, nothing to route;
    * **reachable nowhere** - the ceiling, cross-checked against 0038's forty-six hidden pairs;
    * **routable** - reachable in some worlds and not others, and the only part that orders
      conventions.  Every count this module ranks worlds by is taken over this set alone.

    The list of tasks unreachable in the control ``G0`` but reachable elsewhere is the direct answer
    to the owner's correction and is reported by name with the worlds that can do them.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    if index is None:
        index = grid_index(corpus, grammars, workers=workers)
    grammar_ids = tuple(grammar.id for grammar in grammars)
    task_list = tasks(corpus)

    rows: list[dict[str, Any]] = []
    for task in task_list:
        per_world = {
            grammar_id: reachable(task, grammar_id, budget, regime, index)
            for grammar_id in grammar_ids
        }
        reached = tuple(gid for gid in grammar_ids if per_world[gid].reachable)
        rows.append(
            {
                "task": task,
                "name": task.name,
                "object": task.object,
                "kind": task.kind,
                "rule": task.requirement.rule,
                "properties": task.properties,
                "per_world": per_world,
                "reached": reached,
                "reach_count": len(reached),
                "blocked_by": tuple(
                    sorted({r.blocked_by for r in per_world.values() if r.blocked_by})
                ),
            }
        )

    everywhere = tuple(row for row in rows if row["reach_count"] == len(grammar_ids))
    nowhere = tuple(row for row in rows if row["reach_count"] == 0)
    routable = tuple(row for row in rows if 0 < row["reach_count"] < len(grammar_ids))

    control_gap = tuple(
        {
            "name": row["name"],
            "object": row["object"],
            "kind": row["kind"],
            "properties": row["properties"],
            "worlds": row["reached"],
            "world_count": row["reach_count"],
            "witness": row["per_world"][row["reached"][0]].witness,
            "cheapest_world": min(
                row["reached"], key=lambda gid: (row["per_world"][gid].cost, gid)
            ),
            "cheapest_cost": min(row["per_world"][gid].cost for gid in row["reached"]),
            "control_blocked_by": row["per_world"][CONTROL.id].blocked_by,
        }
        for row in routable
        if not row["per_world"][CONTROL.id].reachable
    )

    reach_all = {
        gid: sum(1 for row in rows if row["per_world"][gid].reachable) for gid in grammar_ids
    }
    reach_routable = {
        gid: sum(1 for row in routable if row["per_world"][gid].reachable)
        for gid in grammar_ids
    }
    free_counts = {
        gid: sum(1 for row in rows if row["per_world"][gid].free) for gid in grammar_ids
    }
    paid_counts = {
        gid: sum(1 for row in rows if row["per_world"][gid].paid) for gid in grammar_ids
    }
    premiums = [
        row["per_world"][gid].premium
        for row in rows
        for gid in grammar_ids
        if row["per_world"][gid].paid
    ]
    blocked = {
        "no_witness": sum(
            1
            for row in rows
            for gid in grammar_ids
            if row["per_world"][gid].blocked_by == "no_witness"
        ),
        "budget": sum(
            1
            for row in rows
            for gid in grammar_ids
            if row["per_world"][gid].blocked_by == "budget"
        ),
    }
    nowhere_blocked = {
        "no_witness": sum(1 for row in nowhere if row["blocked_by"] == ("no_witness",)),
        "budget": sum(1 for row in nowhere if row["blocked_by"] == ("budget",)),
        "mixed": sum(1 for row in nowhere if len(row["blocked_by"]) > 1),
    }
    return {
        "regime": regime,
        "budget": budget,
        "tasks": len(rows),
        "task_kind_counts": {
            kind: sum(1 for row in rows if row["kind"] == kind) for kind in TASK_KINDS
        },
        "rows": tuple(rows),
        "reachable_everywhere": len(everywhere),
        "reachable_nowhere": len(nowhere),
        "routable": len(routable),
        "routable_rows": routable,
        "nowhere_rows": nowhere,
        "split_by_kind": {
            kind: {
                "everywhere": sum(1 for row in everywhere if row["kind"] == kind),
                "nowhere": sum(1 for row in nowhere if row["kind"] == kind),
                "routable": sum(1 for row in routable if row["kind"] == kind),
            }
            for kind in TASK_KINDS
        },
        "control_gap": control_gap,
        "control_gap_count": len(control_gap),
        "reach_all": reach_all,
        "reach_routable": reach_routable,
        "control_reach_routable": reach_routable[CONTROL.id],
        "control_reach_rank": 1
        + sum(1 for gid in grammar_ids if reach_routable[gid] > reach_routable[CONTROL.id]),
        "free_counts": free_counts,
        "paid_counts": paid_counts,
        "free_total": sum(free_counts.values()),
        "paid_total": sum(paid_counts.values()),
        "mean_premium": fmean(premiums) if premiums else 0.0,
        "premium_distribution": {
            value: premiums.count(value) for value in sorted(set(premiums))
        },
        "blocked_cells": blocked,
        "nowhere_blocked": nowhere_blocked,
        "grammars": grammar_ids,
    }


# ---------------------------------------------------------------------------- the partial order


def dominance(
    table: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """The PARTIAL order: ``A`` dominates ``B`` when ``A`` reaches every task ``B`` does, and more.

    A total ranking would be a lie about this structure, so incomparability is reported as such and
    never broken by a tiebreak.  The relation is computed over the **routable set alone**, because a
    task everyone reaches or nobody reaches cannot separate two worlds.
    """
    if table is None:
        table = reachability_table(**kwargs)
    grammar_ids = table["grammars"]
    reach_sets = {
        gid: frozenset(
            row["name"] for row in table["routable_rows"] if row["per_world"][gid].reachable
        )
        for gid in grammar_ids
    }
    relation = tuple(
        (a, b)
        for a in grammar_ids
        for b in grammar_ids
        if a != b and reach_sets[b] < reach_sets[a]
    )
    dominated = {b for _, b in relation}
    maximal = tuple(gid for gid in grammar_ids if gid not in dominated)
    minimal = tuple(gid for gid in grammar_ids if not any(a == gid for a, _ in relation))
    incomparable = tuple(
        (a, b)
        for a, b in combinations(grammar_ids, 2)
        if (a, b) not in set(relation)
        and (b, a) not in set(relation)
        and reach_sets[a] != reach_sets[b]
    )
    equal = tuple(
        (a, b) for a, b in combinations(grammar_ids, 2) if reach_sets[a] == reach_sets[b]
    )
    groups: dict[frozenset[str], list[str]] = {}
    for gid in grammar_ids:
        groups.setdefault(reach_sets[gid], []).append(gid)
    return {
        "regime": table["regime"],
        "budget": table["budget"],
        "routable": table["routable"],
        "reach_sets": {gid: len(reach_sets[gid]) for gid in grammar_ids},
        "relation": relation,
        "comparable_pairs": len(relation),
        "incomparable_pairs": len(incomparable),
        "equal_pairs": len(equal),
        "total_pairs": len(grammar_ids) * (len(grammar_ids) - 1) // 2,
        "maximal": maximal,
        "minimal": minimal,
        "control_is_maximal": CONTROL.id in maximal,
        "control_dominated_by": tuple(a for a, b in relation if b == CONTROL.id),
        "control_dominates": tuple(b for a, b in relation if a == CONTROL.id),
        "distinct_reach_sets": len(groups),
        "reach_set_groups": tuple(
            (len(members), tuple(sorted(names)))
            for members, names in sorted(
                ((key, tuple(value)) for key, value in groups.items()),
                key=lambda pair: (-len(pair[0]), sorted(pair[1])),
            )
        ),
    }


# -------------------------------------------------------------------------------- the collision


def cost_ranking() -> dict[str, Any]:
    """Experiment 0037's cost ranking, IMPORTED and not recomputed."""
    table = field_table()
    return {
        "ranks": dict(table["summed_ranks"]),
        "totals": dict(table["summed_totals"]),
        "ranking": table["summed_ranking"],
        "control_rank": table["control_summed_rank"],
        "control_total": table["control_summed_total"],
        "best": table["best_summed_grammars"],
        "best_total": table["best_summed_total"],
    }


def _spearman(first: Sequence[float], second: Sequence[float]) -> float:
    """Spearman rank correlation with midranks for ties."""
    count = len(first)
    if count < 2:
        return float("nan")

    def ranks(values: Sequence[float]) -> list[float]:
        order = sorted(range(count), key=lambda i: values[i])
        out = [0.0] * count
        position = 0
        while position < count:
            stop = position
            while stop + 1 < count and values[order[stop + 1]] == values[order[position]]:
                stop += 1
            midrank = (position + stop) / 2 + 1
            for index in range(position, stop + 1):
                out[order[index]] = midrank
            position = stop + 1
        return out

    left, right = ranks(first), ranks(second)
    mean_left, mean_right = sum(left) / count, sum(right) / count
    numerator = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    denominator = math.sqrt(
        sum((a - mean_left) ** 2 for a in left) * sum((b - mean_right) ** 2 for b in right)
    )
    return numerator / denominator if denominator else float("nan")


def _competition_rank(values: dict[str, int], descending: bool) -> dict[str, int]:
    """Competition ranking (``1, 2, 2, 4``) over per-world numbers."""
    order = sorted(values.items(), key=lambda pair: (-pair[1] if descending else pair[1], pair[0]))
    out: dict[str, int] = {}
    previous_value: int | None = None
    previous_rank = 0
    for position, (key, value) in enumerate(order, start=1):
        rank = previous_rank if value == previous_value else position
        out[key] = rank
        previous_value, previous_rank = value, rank
    return out


def cost_vs_reach(
    table: dict[str, Any] | None = None,
    costs: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """0037's cost rank against reachability count, world by world - and where they disagree.

    Both ranks are over the same twenty-five worlds; the reach count is over the **routable set**
    only.  A world whose reach rank is much worse than its cost rank is *cheap and weak*; the
    reverse is *dear and strong*, and both lists are reported by name.
    """
    if table is None:
        table = reachability_table(**kwargs)
    if costs is None:
        costs = cost_ranking()
    grammar_ids = table["grammars"]
    reach = table["reach_routable"]
    reach_rank = _competition_rank(reach, descending=True)
    cost_rank = {gid: costs["ranks"][gid] for gid in grammar_ids}
    rows = tuple(
        {
            "id": gid,
            "cost_rank": cost_rank[gid],
            "cost_total": costs["totals"][gid],
            "reach": reach[gid],
            "reach_rank": reach_rank[gid],
            "displacement": reach_rank[gid] - cost_rank[gid],
        }
        for gid in sorted(grammar_ids, key=lambda g: (cost_rank[g], g))
    )
    correlation = _spearman(
        [cost_rank[gid] for gid in grammar_ids], [reach_rank[gid] for gid in grammar_ids]
    )
    cheap_and_weak = tuple(row["id"] for row in rows if row["displacement"] >= RANK_GAP)
    dear_and_strong = tuple(row["id"] for row in rows if row["displacement"] <= -RANK_GAP)
    worst = max(row["displacement"] for row in rows)
    best = min(row["displacement"] for row in rows)

    # The card's fifth headline question, made a computation rather than a judgement: is there a
    # world that is dear to write in and yet reaches strictly more than every cheap one?  "Cheap"
    # is 0037's podium - every world at cost rank three or better - and the answer has two halves,
    # because a world can fail to dominate the podium and still reach tasks the podium cannot.
    podium = tuple(gid for gid in grammar_ids if cost_rank[gid] <= 3)
    reach_sets = {
        gid: frozenset(
            row["name"] for row in table["routable_rows"] if row["per_world"][gid].reachable
        )
        for gid in grammar_ids
    }
    podium_union = frozenset().union(*(reach_sets[gid] for gid in podium)) if podium else frozenset()
    beyond = {gid: len(reach_sets[gid] - podium_union) for gid in grammar_ids}
    return {
        "regime": table["regime"],
        "budget": table["budget"],
        "rows": rows,
        "spearman": correlation,
        "agree": all(row["displacement"] == 0 for row in rows),
        "max_displacement": max(abs(row["displacement"]) for row in rows),
        "mean_absolute_displacement": fmean(abs(row["displacement"]) for row in rows),
        "cheap_and_weak": cheap_and_weak,
        "dear_and_strong": dear_and_strong,
        "rank_gap": RANK_GAP,
        "cheapest_relative_to_reach": tuple(
            row["id"] for row in rows if row["displacement"] == worst
        ),
        "largest_positive_displacement": worst,
        "strongest_relative_to_cost": tuple(
            row["id"] for row in rows if row["displacement"] == best
        ),
        "largest_negative_displacement": best,
        "podium": podium,
        "podium_union_size": len(podium_union),
        "strictly_out_reaching_podium": tuple(
            gid
            for gid in grammar_ids
            if gid not in set(podium)
            and all(reach_sets[other] < reach_sets[gid] for other in podium)
        ),
        "beyond_podium": {gid: count for gid, count in beyond.items() if count},
        "beyond_podium_worlds": tuple(sorted(gid for gid, count in beyond.items() if count)),
        "beyond_podium_max": max(beyond.values()),
        "beyond_podium_cost_ranks": tuple(
            sorted({cost_rank[gid] for gid, count in beyond.items() if count})
        ),
        "control": next(row for row in rows if row["id"] == CONTROL.id),
    }


# ------------------------------------------------------------------------ the owner's scenario


def slow_but_possible(
    table: dict[str, Any] | None = None,
    costs: dict[str, Any] | None = None,
    index: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """For every task ``G0`` cannot reach: the cheapest world that can, and what it costs there.

    The comparison the owner asked for is against what ``G0`` pays for the tasks it CAN do, so that
    is the baseline: the mean bracket cost of ``G0``'s witness over its reachable tasks.  The
    premium is the difference, and it is reported per task rather than only in aggregate.

    ``control_cost_if_budget_lifted`` is what ``G0`` would have had to pay for the same task with
    the budget removed.  It is the number that says *why* the task is out of reach - and it is
    reported separately, because it is a cost and the reachability verdict is not.
    """
    if table is None:
        table = reachability_table(index=index, **kwargs)
    if costs is None:
        costs = cost_ranking()
    control_costs = [
        row["per_world"][CONTROL.id].cost
        for row in table["rows"]
        if row["per_world"][CONTROL.id].reachable
    ]
    baseline = fmean(control_costs) if control_costs else 0.0

    entries = []
    for row in table["routable_rows"]:
        if row["per_world"][CONTROL.id].reachable:
            continue
        reached = row["reached"]
        cheapest = min(reached, key=lambda gid: (row["per_world"][gid].cost, gid))
        reach = row["per_world"][cheapest]
        item = OBJECT_BY_NAME[row["object"]]
        lifted = None
        for writing in item.writings:
            key = (row["object"], writing.role, CONTROL.id)
            manifest = (
                index["manifest"][table["regime"]][key]
                if index is not None
                else frozenset(_cell(key)[table["regime"]])
            )
            if not row["task"].requirement.holds(manifest, row["properties"]):
                continue
            cost = index["cost"][key] if index is not None else _cell(key)["cost"]
            lifted = cost if lifted is None else min(lifted, cost)
        entries.append(
            {
                "name": row["name"],
                "object": row["object"],
                "kind": row["kind"],
                "properties": row["properties"],
                "worlds": reached,
                "world_count": len(reached),
                "cheapest_world": cheapest,
                "cheapest_world_cost_rank": costs["ranks"][cheapest],
                "cost_there": reach.cost,
                "witness": reach.witness,
                "witness_text": (
                    index["text"][(row["object"], reach.witness, cheapest)]
                    if index is not None
                    else _cell((row["object"], reach.witness, cheapest))["text"]
                ),
                "premium_vs_control_baseline": reach.cost - baseline,
                "control_blocked_by": row["per_world"][CONTROL.id].blocked_by,
                "control_cost_if_budget_lifted": lifted,
                "best_cost_rank_that_reaches": min(costs["ranks"][gid] for gid in reached),
            }
        )
    return {
        "regime": table["regime"],
        "budget": table["budget"],
        "control": CONTROL.id,
        "control_reachable_tasks": len(control_costs),
        "control_mean_cost": baseline,
        "control_cost_distribution": {
            value: control_costs.count(value) for value in sorted(set(control_costs))
        },
        "entries": tuple(entries),
        "count": len(entries),
        "mean_cost_elsewhere": fmean(entry["cost_there"] for entry in entries)
        if entries
        else 0.0,
        "mean_premium": fmean(entry["premium_vs_control_baseline"] for entry in entries)
        if entries
        else 0.0,
        "all_cheaper_elsewhere": all(entry["cost_there"] < baseline for entry in entries)
        if entries
        else False,
    }


# --------------------------------------------------------------------- the cost podium and blindness


def factor_blindness(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    index: dict[str, Any] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Re-derive both halves of the card's claim independently, and say whether they really overlap.

    The claim under test is that experiment 0037's cost podium consists entirely of worlds that
    experiment 0038 finds blind to ``factor_structure``.  Both halves are derived here rather than
    quoted: the blind set by asking, for every world, whether any object's **default** writing there
    makes ``factor_structure`` manifest, and the podium by reading 0037's ranking.  The overlap is
    then a computed fact, reported as ``total`` or not.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    if index is None:
        index = grid_index(corpus, grammars, workers=workers)
    blind = []
    for grammar in grammars:
        seen = False
        for item in corpus:
            role = index["default"][(item.name, grammar.id)]
            if "factor_structure" in index["manifest"]["transparent"][
                (item.name, role, grammar.id)
            ]:
                seen = True
                break
        if not seen:
            blind.append(grammar.id)
    blind_tuple = tuple(blind)

    costs = cost_ranking()
    podium = tuple(row["id"] for row in costs["ranking"] if row["rank"] <= 3)
    overlap = tuple(gid for gid in podium if gid in set(blind_tuple))
    outside = tuple(gid for gid in podium if gid not in set(blind_tuple))
    sighted = tuple(gid for gid in costs["ranks"] if gid not in set(blind_tuple))
    return {
        "blind": blind_tuple,
        "blind_count": len(blind_tuple),
        "matches_0038": blind_tuple == FACTOR_BLIND_EXPECTED,
        "podium": podium,
        "podium_size": len(podium),
        "podium_note": (
            "rank 3 is a tie between G0 and G10 at 45 brackets, so the podium holds four worlds and "
            "'the three cheapest' is not a well-defined set without inventing a tiebreak"
        ),
        "overlap": overlap,
        "overlap_count": len(overlap),
        "podium_outside_blind": outside,
        "overlap_total": set(podium) <= set(blind_tuple),
        "blind_cost_ranks": {gid: costs["ranks"][gid] for gid in blind_tuple},
        "blind_cost_totals": {gid: costs["totals"][gid] for gid in blind_tuple},
        "mean_cost_rank_blind": fmean(costs["ranks"][gid] for gid in blind_tuple),
        "mean_cost_rank_sighted": fmean(costs["ranks"][gid] for gid in sighted),
        "mean_cost_total_blind": fmean(costs["totals"][gid] for gid in blind_tuple),
        "mean_cost_total_sighted": fmean(costs["totals"][gid] for gid in sighted),
        "sighted_count": len(sighted),
    }


# ---------------------------------------------------------------------------------- the sweep


def budget_sweep(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    budgets: Sequence[int] = BUDGET_SWEEP,
    regimes: Sequence[str] = REGIMES,
    index: dict[str, Any] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Every budget in every regime, so the declared threshold can be argued with, not just trusted.

    The row at the top budget is the null the module has to publish: with nothing excluded, the
    transparent routable set is **empty**, because a written form's manifest set does not depend on
    the grammar.  Everything the transparent regime finds routable is created by the threshold.  The
    opaque regime, where a bracket hides what is inside it, keeps a large routable set at every
    budget - which is the robustness check.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    if index is None:
        index = grid_index(corpus, grammars, workers=workers)
    costs = cost_ranking()
    rows = []
    for regime in regimes:
        for budget in budgets:
            table = reachability_table(
                corpus, grammars, budget=budget, regime=regime, index=index
            )
            order = dominance(table)
            collision = cost_vs_reach(table, costs)
            rows.append(
                {
                    "regime": regime,
                    "budget": budget,
                    "everywhere": table["reachable_everywhere"],
                    "nowhere": table["reachable_nowhere"],
                    "routable": table["routable"],
                    "control_gap": table["control_gap_count"],
                    "control_reach": table["control_reach_routable"],
                    "control_reach_rank": table["control_reach_rank"],
                    "maximal": len(order["maximal"]),
                    "control_is_maximal": order["control_is_maximal"],
                    "distinct_reach_sets": order["distinct_reach_sets"],
                    "spearman": collision["spearman"],
                }
            )
    transparent = [row for row in rows if row["regime"] == "transparent"]
    return {
        "rows": tuple(rows),
        "budgets": tuple(budgets),
        "regimes": tuple(regimes),
        "control_gap_range": (
            min(row["control_gap"] for row in rows),
            max(row["control_gap"] for row in rows),
        ),
        "transparent_unbounded_routable": transparent[-1]["routable"] if transparent else None,
        "transparent_routable_is_budget_made": (
            transparent[-1]["routable"] == 0 if transparent else None
        ),
    }


# --------------------------------------------------------------------------------------- audits


def witness_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    budgets: Sequence[int] = BUDGET_SWEEP,
    regimes: Sequence[str] = REGIMES,
    index: dict[str, Any] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Soundness: a task is never reported reachable on a witness that does not satisfy it.

    Two things are checked for every reachable cell, in every regime and at every budget.  The
    witness writing must actually make the requirement hold under the imported shape rules - and
    every property the witness claims must be one ``ground_truth`` confirms, which is 0038's
    ``manifest implies true`` sweep recounted here on the witnesses this module selects.  A single
    violation would mean the reachability verdicts are fiction; ``violations`` must be empty.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    if index is None:
        index = grid_index(corpus, grammars, workers=workers)
    truth = {
        item.name: set(ground_truth(object_tree(item.writings[0]), item.variable))
        for item in corpus
    }
    violations: list[dict[str, Any]] = []
    checks = 0
    claims = 0
    for regime in regimes:
        for budget in budgets:
            for task in tasks(corpus):
                for grammar in grammars:
                    verdict = reachable(task, grammar.id, budget, regime, index)
                    if not verdict.reachable:
                        continue
                    checks += 1
                    key = (task.object, verdict.witness, grammar.id)
                    manifest = index["manifest"][regime][key]
                    if not task.requirement.holds(manifest, task.properties):
                        violations.append(
                            {
                                "task": task.name,
                                "grammar": grammar.id,
                                "regime": regime,
                                "budget": budget,
                                "reason": "witness does not satisfy the requirement",
                                "text": index["text"][key],
                            }
                        )
                    if index["cost"][key] > budget:
                        violations.append(
                            {
                                "task": task.name,
                                "grammar": grammar.id,
                                "regime": regime,
                                "budget": budget,
                                "reason": "witness exceeds the bracket budget",
                                "text": index["text"][key],
                            }
                        )
                    for name in manifest:
                        claims += 1
                        if name not in truth[task.object]:
                            violations.append(
                                {
                                    "task": task.name,
                                    "grammar": grammar.id,
                                    "regime": regime,
                                    "budget": budget,
                                    "reason": f"witness claims {name}, ground truth denies it",
                                    "text": index["text"][key],
                                }
                            )
    return {
        "checks": checks,
        "claims": claims,
        "violations": tuple(violations),
        "sound": not violations,
    }


def ceiling_crosscheck(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    index: dict[str, Any] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The tasks reachable in NO world, cross-checked against experiment 0039's forty-six.

    0038 counts forty-six ``(object, property)`` pairs that are true and manifest in no world.  A
    ``property`` task here is exactly such a pair, so the two counts must agree - and they are
    computed by different routes: 0038 looks only at each world's chosen writing, this module looks
    at every writing within budget.  Agreement is the check; disagreement would be a defect.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    if index is None:
        index = grid_index(corpus, grammars, workers=workers)
    table = reachability_table(corpus, grammars, index=index)
    ours = tuple(
        sorted(
            (row["object"], row["properties"][0])
            for row in table["nowhere_rows"]
            if row["kind"] == "property"
        )
    )
    theirs = tuple(sorted(visibility_table(corpus, grammars, workers=1)["hidden_pairs"]))
    return {
        "ours": ours,
        "ours_count": len(ours),
        "theirs": theirs,
        "theirs_count": len(theirs),
        "agree": ours == theirs,
        "pair_tasks_nowhere": sum(
            1 for row in table["nowhere_rows"] if row["kind"] == "property_pair"
        ),
        "writable_tasks_nowhere": sum(
            1 for row in table["nowhere_rows"] if row["kind"] == "writable"
        ),
    }


def bridge(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """The correctness bridge, imported whole from 0034 via 0038 and recounted over this grid.

    A rendering that does not re-parse to its own tree is not a writing of the object, and a
    rendering carrying a bracket its grammar does not require inflates the cost the budget is
    compared against.  Both would invalidate every reachability verdict, so both are checked before
    any number in this module is believed.
    """
    return bridge_audit(corpus, grammars)


# ------------------------------------------------------------------------------------ concurrency
#
# Repository policy is multicore by default and it also says a sequential path is a valid outcome
# when a measurement justifies it.  The numbers below were measured on this machine by
# :func:`parallel_decision` and :func:`measure_pool_startup`, not carried over from 0037 or 0038.

#: Cores kept free so a sweep cannot starve the interactive session.
WORKER_HEADROOM_CORES: int = 2

#: An upper bound on the spawn cost any one sweep has to amortise.
WORKER_CAP: int = 12

#: Measured cost of raising a spawn-start pool whose workers each import this module - and so
#: :mod:`parseatlas.manifest_properties`, :mod:`parseatlas.domain_worlds` and SymPy.
#:
#: **Measured here, not inherited.**  :func:`measure_pool_startup` raises a pool of the default
#: worker count and runs one trivial cell in each; the floor recorded on 16 cores with 12 workers is
#: ``1.32`` s, and this constant rounds it up.  A startup time is a floor that background load can
#: only push up, so the minimum is the honest figure; the same measurement taken while the rest of
#: the suite was running read ``3.74`` s, and :func:`should_parallelise` returns the same verdict at
#: both ends of that range, which is pinned by a test.
POOL_STARTUP_SECONDS: float = 1.4

#: Measured seconds for one ``(writing, world)`` cell - parsing the writing, rendering it under the
#: world, and running the seven imported shape rules once per regime.  Floor recorded: ``0.2810`` s
#: for ``1250`` cells, i.e. ``2.25e-4`` s each; under concurrent load the same sweep read ``5.2e-4``
#: s per cell.  See :func:`parallel_decision`.
CELL_SECONDS: float = 2.3e-04


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
    paths return identical records; the test suite asserts that rather than assuming it.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(len(payloads), CELL_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_cell(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_cell, payloads, chunksize=8))


def _trivial_cell(payload: int) -> int:
    """A cell that does nothing, so timing it times only the pool - and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and therefore SymPy."""
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


def measure_cell_seconds(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    repeats: int = 3,
) -> dict[str, Any]:
    """Measure the per-cell cost :data:`CELL_SECONDS` declares, minimum of ``repeats`` runs."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [
        (item.name, writing.role, grammar.id)
        for item in corpus
        for writing in item.writings
        for grammar in grammars
    ]
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        for payload in payloads:
            _cell(payload)
        best = min(best, time.perf_counter() - start)
    return {
        "cells": len(payloads),
        "seconds": best,
        "seconds_per_cell": best / len(payloads) if payloads else 0.0,
        "declared": CELL_SECONDS,
    }


def parallel_decision(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """Time both paths over the same work, check they agree, and record which one won."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [
        (item.name, writing.role, grammar.id)
        for item in corpus
        for writing in item.writings
        for grammar in grammars
    ]
    workers = default_worker_count(len(payloads))

    start = time.perf_counter()
    sequential = _map_cells(payloads, workers=1)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    parallel = _map_cells(payloads, workers=workers)
    parallel_seconds = time.perf_counter() - start

    speedup = sequential_seconds / parallel_seconds if parallel_seconds else float("inf")
    worth_it = should_parallelise(len(payloads), CELL_SECONDS, workers)
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
        "parallel_worth_it": worth_it,
        "default_path": "parallel" if worth_it else "sequential",
    }


# ------------------------------------------------------------------------------------- the report


def reachability_first_report(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Everything experiment 0043 publishes."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    index = grid_index(corpus, grammars, workers=workers)
    costs = cost_ranking()
    primary = reachability_table(corpus, grammars, index=index)
    secondary = reachability_table(corpus, grammars, regime="opaque", index=index)
    return {
        "bridge": bridge(corpus, grammars),
        "soundness": witness_audit(corpus, grammars, index=index),
        "ceiling": ceiling_crosscheck(corpus, grammars, index=index),
        "tasks": {
            "total": len(tasks(corpus)),
            "by_kind": {
                kind: sum(1 for task in tasks(corpus) if task.kind == kind)
                for kind in TASK_KINDS
            },
            "objects": len(corpus),
            "writings": sum(len(item.writings) for item in corpus),
        },
        "requirements": tuple(
            {"kind": item.kind, "rule": item.rule, "prose": item.prose}
            for item in REQUIREMENTS
        ),
        "budget": BRACKET_BUDGET,
        "cost": costs,
        "factor_blindness": factor_blindness(corpus, grammars, index=index),
        "transparent": {
            "table": primary,
            "dominance": dominance(primary),
            "collision": cost_vs_reach(primary, costs),
            "slow_but_possible": slow_but_possible(primary, costs, index=index),
        },
        "opaque": {
            "table": secondary,
            "dominance": dominance(secondary),
            "collision": cost_vs_reach(secondary, costs),
            "slow_but_possible": slow_but_possible(secondary, costs, index=index),
        },
        "sweep": budget_sweep(corpus, grammars, index=index),
    }
