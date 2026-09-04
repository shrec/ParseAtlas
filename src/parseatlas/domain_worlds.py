"""Experiment 0037: the domain-worlds series, and the compromise test.

Two earlier measurements point the same way and neither was designed to.  Experiment 0034 puts the
conventional grammar ``G0`` **eleventh of twenty-five** on the notational cost of named mathematics,
``45.3`` percent dearer than the cheapest.  Experiment 0036 puts the same ``G0`` in the **top three
of twenty-five** at preserving trigonometric identities, holding all eight.  A convention that is
mediocre everywhere and excellent at nothing would look exactly like that, so the question this
module exists to settle is:

    Is there a grammar that beats ``G0`` across the WHOLE mathematical workload, or did the
    conventional convention survive because it is a good COMPROMISE across many fields rather than
    an optimum in any one?

The instrument is a per-field measurement.  Four fields - algebra, geometry, calculus, linear
algebra - each with a corpus of **named laws, identities and canonical objects**, are priced under
all twenty-five grammars; every grammar then has four ranks instead of one, and "compromise" stops
being a metaphor and becomes a shape in the rank table: a good mean rank, no field where the grammar
is uniquely best, and no field where it is terrible.  Trigonometry is not redone here; experiment
0036 measured it and :func:`trigonometry_survival_reference` reads that measurement back.

What is reused, and why nothing is reimplemented
-----------------------------------------------

* Rendering and bracket counting come from :mod:`parseatlas.notational_cost`.  The bracket rule
  there is *derived* from :class:`parseatlas.parser.Parser` rather than restated as a table, and
  :func:`~parseatlas.notational_cost.render` reparses its own output and raises
  :class:`~parseatlas.notational_cost.RoundTripError` on mismatch.  That guarantee is inherited
  whole; this module never writes a bracket rule of its own.
* Competition ranking is :func:`parseatlas.notational_cost._ranked`, imported rather than copied so
  that a rank in this experiment means exactly what a rank in 0034 means (``1, 2, 2, 4``).
* Identity survival is the experiment 0036 method: read the identity **as the string it is written
  as today**, under each grammar, and ask whether the two sides still denote the same object.  The
  comparison is the project semantic key, imported from
  :func:`parseatlas.trigonometry_worlds.semantic_key`.

The corpus: fundamental laws, not sampled formulas
--------------------------------------------------

Every entry is a named law, identity or canonical object that mathematicians actually state.  What
a convention does to the distributive law is a historical question; what it does to a generated
template is not.  A law with two sides is entered as *both* sides, because which side is cheap is
the historically interesting quantity: under our convention the expanded side of the distributive
law is free and the factored side needs a bracket, so **expansion is the natural direction** - and a
world where that reverses would have built algebra differently.

Stand-ins, disclosed here and in the report
-------------------------------------------

The Generation 1 language has only binary ``+ - * /``, parentheses, integer literals and named
variables.  It has no exponentiation, no function application and no unary minus.  Three
consequences shape the corpus and none of them is hidden:

* **Powers are written as repeated products.**  ``x**2`` is ``x * x`` and ``x**3`` is
  ``x * x * x``.  This is the same choice 0034 made.  It raises the share of ``*`` in every tree,
  so a grammar that binds ``*`` tightly is flattered relative to a language that had ``^``.
* **Function values and derivatives are stand-in leaves.**  :data:`STAND_INS` lists every one of
  them with what it stands for: ``fx`` is *f(x)*, ``fxh`` is *f(x + h)*, ``dfa`` is *f'(a)*, ``dfg``
  is *f'(g(x))*, and so on.  A leaf is a single token that no precedence rule can split, so a
  stand-in never changes a bracket decision *within* the entry - but it does decide how many
  operators the entry has.  The chain rule is the sharp case: written with stand-ins it is
  ``dfg * dg``, a single-operator tree, and it is therefore convention-free by construction.  That
  is called out in the null model rather than left to look like a finding.
* **Halves are explicit divisions.**  The number token is ``\\d+(?:/\\d+)?``, so an unspaced ``1/2``
  would be one literal rather than a division; ``b * h / 2`` is written as a division.

Discipline
----------

Objects are grouped by the project semantic key ``(canonical form, domain, excluded points)``.  The
``domain`` component is inert - :func:`parseatlas.canonical.canonicalize` writes the literal ``"R"``
for every expression - so the operative key here is ``(canonical form, excluded points)``.  That is
repository-wide ``NF-2026-00005``; it is restated in the report's limits and pinned by a test.

The null model is mandatory.  An entry whose cost is identical under all twenty-five grammars adds
the same constant to every total and cannot move any ranking.  :func:`null_model` counts them per
field and re-ranks each field on the movable remainder alone, so a field ranking driven by immovable
entries is visible as such rather than published as a result.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from statistics import fmean, median
from typing import Any

from sympy import simplify

from .canonical import canonicalize
from .grammar import Grammar, all_grammars
from .notational_cost import (
    CONTROL,
    GRAMMARS,
    Formula,
    minimality_audit,
    parenthesis_cost,
    render,
    round_trip_audit,
    tree_operators,
)
from .notational_cost import _ranked as competition_ranking
from .parser import Node, parse
from .trigonometry_worlds import semantic_key

__all__ = [
    "CORPUS",
    "FIELDS",
    "GRAMMARS",
    "CONTROL",
    "Law",
    "Entry",
    "STAND_INS",
    "as_notational_cost_corpus",
    "bridge_audit",
    "compromise_report",
    "corpus_audit",
    "entry_tree",
    "measure_cell_seconds",
    "measure_pool_startup",
    "should_parallelise",
    "default_worker_count",
    "worker_count_for",
    "corpus_entries",
    "domain_worlds_report",
    "dominance_report",
    "entry_rows",
    "field_champions",
    "field_cost",
    "field_table",
    "identity_survival",
    "law_orientation",
    "law_reading",
    "null_model",
    "orientation_table",
    "parallel_decision",
    "survival_table",
    "trigonometry_survival_reference",
    "two_sided_laws",
]

#: The four fields of this card.  Trigonometry is deliberately absent: experiment 0036 measured it
#: and :func:`trigonometry_survival_reference` reads that measurement back rather than redoing it.
FIELDS: tuple[str, ...] = ("algebra", "geometry", "calculus", "linear_algebra")

#: Every stand-in leaf in the corpus and what it stands for.  Disclosed because a stand-in that
#: silently changed the operator mix of an entry would change what is being measured.
STAND_INS: dict[str, str] = {
    "fx": "f(x)",
    "fxh": "f(x + h)",
    "fxi": "f(x_i), the sample height of a Riemann rectangle",
    "fa": "f(a)",
    "dfa": "f'(a)",
    "d2fa": "f''(a), the second Taylor coefficient before the 1/2",
    "dfg": "f'(g(x)), the outer factor of the chain rule",
    "dg": "g'(x), the inner factor of the chain rule",
    "du": "u'(x)",
    "dv": "v'(x)",
}


# ------------------------------------------------------------------------------------ corpus data


@dataclass(frozen=True)
class Law:
    """One named piece of mathematics, with one or two written sides.

    A *two-sided* law is an identity: both sides denote the same object in our world, and the
    question the experiment asks of it is which side a given convention makes cheaper to write.  A
    *one-sided* law is a canonical object - the slope, the squared norm, a Riemann-sum term - which
    has a cost but no direction.

    ``sides`` is ``((role, source), ...)``.  The roles are the names mathematics gives the two
    forms (``factored``/``expanded``, ``point_slope``/``slope_intercept``, ``vertex``/``standard``),
    not generic labels, because "which side is cheap" is only interesting when the sides are named.
    """

    name: str
    field: str
    sides: tuple[tuple[str, str], ...]
    note: str = ""

    @property
    def two_sided(self) -> bool:
        return len(self.sides) == 2

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(role for role, _ in self.sides)


@dataclass(frozen=True)
class Entry:
    """One written form: a single side of a law, and the atom the cost measurement ranges over."""

    name: str
    field: str
    law: str
    role: str
    source: str


CORPUS: tuple[Law, ...] = (
    # ------------------------------------------------------------------------------------ algebra
    #
    # Every algebra entry on the card is a two-sided law, which is why algebra is the field where
    # the orientation question has the most to say.
    Law(
        "distributive_law",
        "algebra",
        (("factored", "a * (b + c)"), ("expanded", "a * b + a * c")),
        "the law the roadmap names: under G0 the expanded side is free",
    ),
    Law(
        "binomial_square",
        "algebra",
        (("factored", "(a + b) * (a + b)"), ("expanded", "a * a + 2 * a * b + b * b")),
        "(a+b)^2 written as a product because Generation 1 has no exponentiation",
    ),
    Law(
        "difference_of_squares",
        "algebra",
        (("factored", "(a + b) * (a - b)"), ("expanded", "a * a - b * b")),
    ),
    Law(
        "difference_of_cubes",
        "algebra",
        (
            ("factored", "(a - b) * (a * a + a * b + b * b)"),
            ("expanded", "a * a * a - b * b * b"),
        ),
    ),
    Law(
        "sum_of_cubes",
        "algebra",
        (
            ("factored", "(a + b) * (a * a - a * b + b * b)"),
            ("expanded", "a * a * a + b * b * b"),
        ),
    ),
    Law(
        "quadratic",
        "algebra",
        (
            ("factored", "a * (x - r) * (x - s)"),
            ("expanded", "a * x * x - a * (r + s) * x + a * r * s"),
        ),
        "the expanded side carries the roots explicitly so that both sides denote one object",
    ),
    Law(
        "binomial_cube",
        "algebra",
        (
            ("factored", "(a + b) * (a + b) * (a + b)"),
            ("expanded", "a * a * a + 3 * a * a * b + 3 * a * b * b + b * b * b"),
        ),
    ),
    Law(
        "perfect_square_trinomial",
        "algebra",
        (("factored", "(2 * x + 3) * (2 * x + 3)"), ("expanded", "4 * x * x + 12 * x + 9")),
        "a concrete perfect square, distinct from the general binomial square",
    ),
    # ----------------------------------------------------------------------------------- geometry
    Law(
        "line",
        "geometry",
        (("point_slope", "y1 + m * (x - x1)"), ("slope_intercept", "m * x + y1 - m * x1")),
    ),
    Law(
        "circle",
        "geometry",
        (
            ("center_radius", "(x - h) * (x - h) + (y - k) * (y - k)"),
            ("general", "x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k"),
        ),
        "completing the square, as a direction question",
    ),
    Law("ellipse", "geometry", (("standard", "x * x / (a * a) + y * y / (b * b)"),)),
    Law("hyperbola", "geometry", (("standard", "x * x / (a * a) - y * y / (b * b)"),)),
    Law(
        "parabola",
        "geometry",
        (
            ("vertex", "a * (x - h) * (x - h) + k"),
            ("standard", "a * x * x - 2 * a * h * x + a * h * h + k"),
        ),
    ),
    Law(
        "distance_components",
        "geometry",
        (("squared", "(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)"),),
    ),
    Law("slope", "geometry", (("difference_quotient", "(y2 - y1) / (x2 - x1)"),)),
    Law("midpoint", "geometry", (("mean", "(x1 + x2) / 2"),)),
    Law("triangle_area", "geometry", (("half_base_height", "b * h / 2"),)),
    Law(
        "trapezoid_area",
        "geometry",
        (("mean_times_height", "(a + b) / 2 * h"), ("sum_of_halves", "a * h / 2 + b * h / 2")),
    ),
    Law("pythagorean_form", "geometry", (("sum_of_squares", "a * a + b * b"),)),
    # ----------------------------------------------------------------------------------- calculus
    Law(
        "difference_quotient",
        "calculus",
        (("closed", "(fxh - fx) / h"), ("split", "fxh / h - fx / h")),
    ),
    Law("product_rule", "calculus", (("standard", "du * v + u * dv"),)),
    Law(
        "quotient_rule",
        "calculus",
        (
            ("closed", "(du * v - u * dv) / (v * v)"),
            ("split", "du / v - u * dv / (v * v)"),
        ),
    ),
    Law(
        "chain_rule",
        "calculus",
        (("standard", "dfg * dg"),),
        "single operator type by construction of the stand-ins; a declared null entry",
    ),
    Law(
        "linear_approximation",
        "calculus",
        (("point_form", "fa + dfa * (x - a)"), ("slope_intercept", "fa - dfa * a + dfa * x")),
    ),
    Law("taylor_first_term", "calculus", (("standard", "dfa * (x - a)"),)),
    Law("taylor_second_term", "calculus", (("standard", "d2fa * (x - a) * (x - a) / 2"),)),
    Law("riemann_sum_term", "calculus", (("standard", "fxi * (b - a) / n"),)),
    # ----------------------------------------------------------------------------- linear algebra
    #
    # The card's six linear-algebra items are canonical OBJECTS, not two-sided laws, so this field
    # contributes nothing to the orientation and survival axes.  That is a property of the field as
    # mathematics states it, and it is reported rather than patched over.
    Law("dot_product", "linear_algebra", (("standard", "u1 * v1 + u2 * v2"),)),
    Law("determinant_2x2", "linear_algebra", (("standard", "a * d - b * c"),)),
    Law("linear_combination", "linear_algebra", (("standard", "c1 * u1 + c2 * v1"),)),
    Law("squared_norm", "linear_algebra", (("standard", "v1 * v1 + v2 * v2 + v3 * v3"),)),
    Law("matrix_vector_component", "linear_algebra", (("standard", "a11 * x1 + a12 * x2"),)),
    Law("cramer_numerator", "linear_algebra", (("standard", "c1 * b22 - b12 * c2"),)),
)

LAW_BY_NAME: dict[str, Law] = {law.name: law for law in CORPUS}

GRAMMAR_BY_ID: dict[str, Grammar] = {grammar.id: grammar for grammar in GRAMMARS}


def corpus_entries(corpus: Sequence[Law] | None = None) -> tuple[Entry, ...]:
    """Flatten the laws into the written forms the cost measurement ranges over."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    return tuple(
        Entry(f"{law.name}.{role}", law.field, law.name, role, source)
        for law in corpus
        for role, source in law.sides
    )


def two_sided_laws(corpus: Sequence[Law] | None = None) -> tuple[Law, ...]:
    """The laws that have two sides, i.e. the ones that are identities and have a direction."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    return tuple(law for law in corpus if law.two_sided)


def entry_tree(entry: Entry) -> Node:
    """The intended tree of a written form: its source parsed under the control grammar.

    ``G0`` is the control precisely because it IS how mathematics is written today, so parsing the
    conventional source under it recovers the intended object rather than imposing one.
    """
    return parse(entry.source, CONTROL)


def corpus_audit(corpus: Sequence[Law] | None = None) -> dict[str, Any]:
    """Check the corpus is what it claims before any number is computed from it.

    Three properties, all of them auditable from the published sources:

    * names are unique, and every field on the card is present;
    * every source is *minimal under G0*: ``render(parse(source, G0), G0) == source``, so no source
      carries a redundant bracket or a hidden intent;
    * every two-sided law is a genuine identity **in our world**: both sides read under ``G0``
      land on the same semantic key.  A "law" whose sides did not agree today would make the whole
      survival axis meaningless.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    entries = corpus_entries(corpus)
    non_canonical = tuple(
        {"entry": entry.name, "source": entry.source, "rendered": render(entry_tree(entry), CONTROL)}
        for entry in entries
        if render(entry_tree(entry), CONTROL) != entry.source
    )
    names = [entry.name for entry in entries]
    per_field: dict[str, dict[str, int]] = {}
    for entry in entries:
        bucket = per_field.setdefault(entry.field, {"entries": 0, "laws": 0, "two_sided": 0})
        bucket["entries"] += 1
    for law in corpus:
        bucket = per_field.setdefault(law.field, {"entries": 0, "laws": 0, "two_sided": 0})
        bucket["laws"] += 1
        bucket["two_sided"] += 1 if law.two_sided else 0
    broken = tuple(
        law.name for law in two_sided_laws(corpus) if not law_reading(law, CONTROL.id)["holds"]
    )
    used_stand_ins = sorted({name for name in STAND_INS if _mentions(name, entries)})
    return {
        "law_count": len(corpus),
        "entry_count": len(entries),
        "two_sided_count": len(two_sided_laws(corpus)),
        "fields": dict(sorted(per_field.items())),
        "field_count": len(per_field),
        "duplicate_names": tuple(sorted({name for name in names if names.count(name) > 1})),
        "canonical_sources": not non_canonical,
        "non_canonical": non_canonical,
        "identities_hold_under_control": not broken,
        "broken_identities": broken,
        "stand_ins_used": tuple(used_stand_ins),
        "stand_ins_declared": tuple(sorted(STAND_INS)),
        "stand_ins_all_declared": set(used_stand_ins) == set(STAND_INS),
    }


def as_notational_cost_corpus(corpus: Sequence[Law] | None = None) -> tuple[Formula, ...]:
    """This corpus in the 0034 record type, so 0034's own audits can be run over it unchanged.

    :func:`parseatlas.notational_cost.round_trip_audit` and
    :func:`~parseatlas.notational_cost.minimality_audit` are the correctness bridge of direction B.
    Re-running them here rather than writing a second pair is the difference between inheriting a
    guarantee and claiming one.
    """
    return tuple(
        Formula(entry.name, entry.field, entry.source) for entry in corpus_entries(corpus)
    )


def bridge_audit(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """Re-run 0034's round-trip and minimality audits over this corpus.

    Round trip: ``parse(render(tree, g), g) == tree`` for every (entry, grammar) pair.  Minimality:
    every bracket the renderer emits is deleted in turn and the result must reparse differently or
    fail.  Both are recounted independently of the production path that already enforces them.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    formulas = as_notational_cost_corpus(corpus)
    return {
        "round_trip": round_trip_audit(formulas, grammars),
        "minimality": minimality_audit(formulas, grammars),
    }


def _mentions(name: str, entries: Sequence[Entry]) -> bool:
    return any(name in entry.source.replace("(", " ").replace(")", " ").split() for entry in entries)


# ------------------------------------------------------------------------------------- cost layer


def _cost_cell(payload: tuple[Entry, tuple[Grammar, ...]]) -> dict[str, Any]:
    """One written form priced under every grammar; module-level so it is picklable for a pool.

    Every rendering goes through :func:`parseatlas.notational_cost.render` with its round-trip
    verification on, so a cost that reaches this table has already been proved to denote the tree it
    was priced from.
    """
    entry, grammars = payload
    tree = entry_tree(entry)
    renderings = {grammar.id: render(tree, grammar) for grammar in grammars}
    operators = tree_operators(tree)
    return {
        "name": entry.name,
        "field": entry.field,
        "law": entry.law,
        "role": entry.role,
        "source": entry.source,
        "operators": operators,
        "support_size": len(operators),
        "renderings": renderings,
        "costs": {key: text.count("(") for key, text in renderings.items()},
    }


def entry_rows(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> tuple[dict[str, Any], ...]:
    """One record per written form: its rendering and bracket cost under every grammar.

    The rows are independent, so the workload is divisible; it nevertheless runs SEQUENTIALLY by
    default, because :func:`should_parallelise` was given a per-cell cost measured on this workload
    (:data:`COST_CELL_SECONDS`) and that cost is four orders of magnitude below the pool startup.
    The parallel path exists, is tested, and returns identical rows - parallelism changes only how
    fast, never what is produced.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [(entry, grammars) for entry in corpus_entries(corpus)]
    return tuple(_map_cells(_cost_cell, payloads, workers, COST_CELL_SECONDS))


def field_cost(
    field: str,
    grammar: Grammar,
    corpus: Sequence[Law] | None = None,
) -> dict[str, Any]:
    """Total minimal brackets for one field's corpus under one grammar, and how much is free.

    ``free_count`` is the direct form of the founding question's second half: the parenthesis-free
    entries of a convention are the mathematics that convention would have made natural to write.
    """
    entries = [entry for entry in corpus_entries(corpus) if entry.field == field]
    if not entries:
        raise ValueError(f"no corpus entries in field {field!r}")
    costs = {entry.name: parenthesis_cost(entry_tree(entry), grammar) for entry in entries}
    free = tuple(name for name, cost in costs.items() if cost == 0)
    return {
        "field": field,
        "grammar": grammar.id,
        "entry_count": len(entries),
        "total": sum(costs.values()),
        "costs": costs,
        "free_count": len(free),
        "free_entries": free,
    }


def _field_ranking(
    rows: Sequence[dict[str, Any]],
    field: str,
    grammars: Sequence[Grammar],
) -> dict[str, Any]:
    subset = [row for row in rows if row["field"] == field]
    totals = {grammar.id: sum(row["costs"][grammar.id] for row in subset) for grammar in grammars}
    ranking = competition_ranking(totals)
    ranks = {entry["id"]: entry["rank"] for entry in ranking}
    free_counts = {
        grammar.id: sum(1 for row in subset if row["costs"][grammar.id] == 0) for grammar in grammars
    }
    best_total = ranking[0]["total"]
    return {
        "field": field,
        "entry_count": len(subset),
        "totals": totals,
        "ranking": tuple(
            {**entry, "free_entries": free_counts[entry["id"]]} for entry in ranking
        ),
        "ranks": ranks,
        "free_counts": free_counts,
        "best_total": best_total,
        "best_grammars": tuple(entry["id"] for entry in ranking if entry["total"] == best_total),
        "worst_total": ranking[-1]["total"],
        "control_total": totals[CONTROL.id],
        "control_rank": ranks[CONTROL.id],
        "control_free": free_counts[CONTROL.id],
        "control_minus_best": totals[CONTROL.id] - best_total,
    }


def field_table(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Cost and rank of every grammar within every field, plus the summed workload."""
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = entry_rows(corpus, grammars, workers)
    fields = tuple(field for field in FIELDS if any(row["field"] == field for row in rows))
    per_field = {field: _field_ranking(rows, field, grammars) for field in fields}
    summed_totals = {
        grammar.id: sum(per_field[field]["totals"][grammar.id] for field in fields)
        for grammar in grammars
    }
    summed_ranking = competition_ranking(summed_totals)
    summed_ranks = {entry["id"]: entry["rank"] for entry in summed_ranking}
    labels = {
        grammar.id: " ".join("".join(level) for level in grammar.levels) for grammar in grammars
    }
    return {
        "fields": fields,
        "rows": rows,
        "labels": labels,
        "per_field": per_field,
        "summed_totals": summed_totals,
        "summed_ranking": summed_ranking,
        "summed_ranks": summed_ranks,
        "control_summed_total": summed_totals[CONTROL.id],
        "control_summed_rank": summed_ranks[CONTROL.id],
        "best_summed_total": summed_ranking[0]["total"],
        "best_summed_grammars": tuple(
            entry["id"] for entry in summed_ranking if entry["total"] == summed_ranking[0]["total"]
        ),
    }


def field_champions(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Which grammar wins each field outright, and whether the winners differ between fields.

    If the winners differ, notation has produced the same routing result the earlier experiments
    found from the semantic side: a field can prefer its own convention.
    """
    table = field_table(corpus, grammars, workers)
    winners = {field: table["per_field"][field]["best_grammars"] for field in table["fields"]}
    unique = {
        field: (ids[0] if len(ids) == 1 else None) for field, ids in winners.items()
    }
    distinct_winner_sets = {frozenset(ids) for ids in winners.values()}
    common = set.intersection(*(set(ids) for ids in winners.values())) if winners else set()
    return {
        "fields": table["fields"],
        "winners": winners,
        "outright_winner": unique,
        "winners_differ": len(distinct_winner_sets) > 1,
        "grammars_winning_every_field": tuple(sorted(common)),
        "distinct_winner_sets": len(distinct_winner_sets),
        "control_wins": tuple(field for field, ids in winners.items() if CONTROL.id in ids),
        "control_wins_outright": tuple(
            field for field, winner in unique.items() if winner == CONTROL.id
        ),
        "summed_winner": table["best_summed_grammars"],
    }


# ------------------------------------------------------------------------------------ orientation


def law_orientation(
    law: Law | str,
    grammar: Grammar | str,
) -> dict[str, Any]:
    """For a two-sided law, which side is cheaper to write under this grammar.

    This is the historically interesting quantity.  Under our convention the expanded side of the
    distributive law is free and the factored side needs a bracket, so expansion is the natural
    direction and algebra was built in that direction.  A world in which factorisation is the free
    direction would have built it the other way.

    ``natural`` is the role of the cheaper side, or ``None`` when the two sides cost the same.
    ``reversed_vs_control`` is ``True`` only when both this world and ``G0`` have a strict
    preference and the preferences disagree; a tie is reported as a tie, not as a reversal.
    """
    law = LAW_BY_NAME[law] if isinstance(law, str) else law
    grammar = GRAMMAR_BY_ID[grammar] if isinstance(grammar, str) else grammar
    if not law.two_sided:
        raise ValueError(f"{law.name!r} has one side; orientation is undefined for it")
    costs = {role: parenthesis_cost(parse(source, CONTROL), grammar) for role, source in law.sides}
    control_costs = {
        role: parenthesis_cost(parse(source, CONTROL), CONTROL) for role, source in law.sides
    }
    natural = _cheaper(costs)
    control_natural = _cheaper(control_costs)
    first, second = law.roles
    return {
        "law": law.name,
        "field": law.field,
        "grammar": grammar.id,
        "roles": law.roles,
        "costs": costs,
        "natural": natural,
        "tie": natural is None,
        "direction": "none" if natural is None else f"toward_{natural}",
        "margin": abs(costs[first] - costs[second]),
        "control_natural": control_natural,
        "reversed_vs_control": (
            natural is not None and control_natural is not None and natural != control_natural
        ),
    }


def _cheaper(costs: dict[str, int]) -> str | None:
    values = sorted(costs.items(), key=lambda item: item[1])
    if values[0][1] == values[1][1]:
        return None
    return values[0][0]


def orientation_table(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """The natural direction of every two-sided law in every world, and where it reverses."""
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    laws = two_sided_laws(corpus)
    cells = {
        (law.name, grammar.id): law_orientation(law, grammar) for law in laws for grammar in grammars
    }
    per_law = []
    for law in laws:
        rows = [cells[(law.name, grammar.id)] for grammar in grammars]
        control = cells[(law.name, CONTROL.id)]
        reversing = tuple(row["grammar"] for row in rows if row["reversed_vs_control"])
        per_law.append(
            {
                "law": law.name,
                "field": law.field,
                "roles": law.roles,
                "control_natural": control["natural"],
                "control_costs": control["costs"],
                "natural_by_grammar": {row["grammar"]: row["natural"] for row in rows},
                "reversing_worlds": reversing,
                "reversing_count": len(reversing),
                "tie_worlds": tuple(row["grammar"] for row in rows if row["tie"]),
                "reverses_somewhere": bool(reversing),
            }
        )
    per_grammar = {
        grammar.id: tuple(
            law.name for law in laws if cells[(law.name, grammar.id)]["reversed_vs_control"]
        )
        for grammar in grammars
    }
    reversal_cells = sum(len(names) for names in per_grammar.values())
    worlds_with_a_reversal = tuple(
        sorted(grammar_id for grammar_id, names in per_grammar.items() if names)
    )
    return {
        "law_count": len(laws),
        "grammar_count": len(grammars),
        "per_law": tuple(per_law),
        "per_grammar": per_grammar,
        "laws_that_reverse_somewhere": tuple(
            item["law"] for item in per_law if item["reverses_somewhere"]
        ),
        "laws_that_reverse_count": sum(1 for item in per_law if item["reverses_somewhere"]),
        "worlds_with_a_reversal": worlds_with_a_reversal,
        "worlds_with_a_reversal_count": len(worlds_with_a_reversal),
        "reversal_cells": reversal_cells,
        "total_cells": len(laws) * len(grammars),
        "control_directions": {
            item["law"]: item["control_natural"] for item in per_law
        },
    }


# --------------------------------------------------------------------------- survival (0036 reuse)


def _side_record(source: str, grammar: Grammar) -> dict[str, Any]:
    """One written side, read under one grammar, with its canonical form and its semantic key.

    The identity is read as the STRING it is written as today, which is the experiment 0036 method:
    a bracketed side is grammar-invariant, an unbracketed side re-associates, and the question is
    whether the two still denote one object.  The key is the project triple ``(canonical form,
    domain, excluded points)``; the ``domain`` slot is inert (``NF-2026-00005``), so the operative
    discrimination is ``(canonical form, excluded points)``.
    """
    canonical = canonicalize(parse(source, grammar))
    return {
        "source": source,
        "canonical": canonical["expression"],
        "domain": canonical["domain"],
        "excluded_points": tuple(canonical["excluded_points"]),
        "key": semantic_key(
            canonical["expression"], canonical["domain"], canonical["excluded_points"]
        ),
        "sympy": canonical["sympy_expression"],
    }


def _sides_agree(record_a: dict[str, Any], record_b: dict[str, Any]) -> dict[str, bool]:
    """Do two readings denote the same partial function?

    Two conditions, and both are needed.  The first is the experiment 0036 test verbatim - the
    difference simplifies to zero - and it is used instead of comparing canonical TEXT because
    :func:`sympy.simplify` is not a normal form for polynomial identities: it leaves
    ``(a + b)**2`` and ``a**2 + 2*a*b + b**2`` as different strings for one function.  The second is
    the project's triple discipline: two expressions that agree everywhere they are both defined
    are still different partial functions when their validity restrictions differ, so the excluded
    points must match as sets.
    """
    same_expression = bool(simplify(record_a["sympy"] - record_b["sympy"]) == 0)
    same_excluded = set(record_a["excluded_points"]) == set(record_b["excluded_points"])
    return {
        "same_expression": same_expression,
        "same_excluded_points": same_excluded,
        "same_key": record_a["key"] == record_b["key"],
        "holds": same_expression and same_excluded,
    }


def law_reading(law: Law | str, grammar_id: str) -> dict[str, Any]:
    """Read both sides of one two-sided law under one world and say whether it still holds.

    This is the cell of the survival atlas, and it is a pure function of its payload, which is what
    makes the atlas divisible across processes.  Only primitives are returned, so the sequential and
    parallel record sets compare equal without depending on SymPy object identity.
    """
    law = LAW_BY_NAME[law] if isinstance(law, str) else law
    grammar = GRAMMAR_BY_ID[grammar_id]
    if not law.two_sided:
        raise ValueError(f"{law.name!r} has one side; it is not an identity")
    records = [_side_record(source, grammar) for _, source in law.sides]
    agreement = _sides_agree(records[0], records[1])
    return {
        "law": law.name,
        "field": law.field,
        "grammar": grammar_id,
        "sides": tuple(
            {
                "role": role,
                "source": record["source"],
                "canonical": record["canonical"],
                "domain": record["domain"],
                "excluded_points": record["excluded_points"],
                "key": record["key"],
            }
            for (role, _), record in zip(law.sides, records)
        ),
        **agreement,
    }


def _reading_cell(payload: tuple[Law, str]) -> dict[str, Any]:
    """Module-level entry point so a survival cell is picklable for a spawned process.

    The payload carries the :class:`Law` itself rather than its name, so a sub-corpus assembled by a
    caller - a test running a fast subset, for instance - never has to be registered globally.
    """
    return law_reading(payload[0], payload[1])


def survival_table(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Which identities remain true in the same textual form, world by world and field by field."""
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    laws = two_sided_laws(corpus)
    payloads = [(law, grammar.id) for law in laws for grammar in grammars]
    rows = _map_cells(_reading_cell, payloads, workers, SURVIVAL_CELL_SECONDS)
    cells = {(row["law"], row["grammar"]): row for row in rows}
    fields = tuple(field for field in FIELDS if any(law.field == field for law in laws))
    per_field: dict[str, dict[str, Any]] = {}
    for field in fields:
        field_laws = [law for law in laws if law.field == field]
        kept = {
            grammar.id: tuple(
                law.name for law in field_laws if cells[(law.name, grammar.id)]["holds"]
            )
            for grammar in grammars
        }
        counts = {grammar_id: len(names) for grammar_id, names in kept.items()}
        best = max(counts.values())
        per_field[field] = {
            "identity_count": len(field_laws),
            "identities": tuple(law.name for law in field_laws),
            "kept": kept,
            "counts": counts,
            "best_count": best,
            "best_grammars": tuple(sorted(key for key, value in counts.items() if value == best)),
            "control_count": counts[CONTROL.id],
        }
    overall = {
        grammar.id: sum(1 for law in laws if cells[(law.name, grammar.id)]["holds"])
        for grammar in grammars
    }
    best_overall = max(overall.values())
    per_law = tuple(
        {
            "law": law.name,
            "field": law.field,
            "holds_in": tuple(
                grammar.id for grammar in grammars if cells[(law.name, grammar.id)]["holds"]
            ),
            "holds_count": sum(
                1 for grammar in grammars if cells[(law.name, grammar.id)]["holds"]
            ),
        }
        for law in laws
    )
    return {
        "fields": fields,
        "identity_count": len(laws),
        "readings": tuple(rows),
        "per_field": per_field,
        "per_law": per_law,
        "overall_counts": overall,
        "best_overall": best_overall,
        "best_overall_grammars": tuple(
            sorted(key for key, value in overall.items() if value == best_overall)
        ),
        "control_overall": overall[CONTROL.id],
        "convention_free_identities": tuple(
            item["law"] for item in per_law if item["holds_count"] == len(grammars)
        ),
    }


def identity_survival(
    field: str,
    grammar: Grammar | str,
    corpus: Sequence[Law] | None = None,
) -> dict[str, Any]:
    """How many of one field's identities remain true in the same textual form under one grammar.

    Only two-sided laws are identities; the field's one-sided canonical objects are excluded, which
    is why ``identity_count`` can be smaller than the field's entry count - and, for the card's
    linear-algebra list, zero.
    """
    grammar = GRAMMAR_BY_ID[grammar] if isinstance(grammar, str) else grammar
    laws = [law for law in two_sided_laws(corpus) if law.field == field]
    readings = [law_reading(law, grammar.id) for law in laws]
    surviving = tuple(row["law"] for row in readings if row["holds"])
    return {
        "field": field,
        "grammar": grammar.id,
        "identity_count": len(laws),
        "surviving_count": len(surviving),
        "surviving": surviving,
        "broken": tuple(row["law"] for row in readings if not row["holds"]),
        "fraction": (len(surviving) / len(laws)) if laws else None,
    }


def trigonometry_survival_reference(workers: int | None = None) -> dict[str, Any]:
    """Read experiment 0036's identity survival back, rather than measuring trigonometry again.

    The card's four fields are algebra, geometry, calculus and linear algebra precisely because
    trigonometry is done.  This function calls :func:`parseatlas.trigonometry_worlds.identity_atlas`
    and returns its per-world survival counts in the shape this module's tables use, so the fifth
    field can enter the compromise discussion on the survival axis without being recomputed.  It is
    NOT part of the cost ranking: experiment 0036 has no cost corpus.
    """
    from .trigonometry_worlds import identity_atlas

    atlas = identity_atlas(workers=workers)
    counts = {key: value["count"] for key, value in atlas["survival"].items()}
    return {
        "source_experiment": "0036",
        "identity_count": len(atlas["identities"]),
        "counts": counts,
        "best_count": atlas["best_count"],
        "best_grammars": tuple(atlas["best_grammars"]),
        "control_count": atlas["control_count"],
        "control_is_among_best": CONTROL.id in atlas["best_grammars"],
    }


# -------------------------------------------------------------------------------------- null model


def null_model(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Separate the forced part of each field's cost from the part a convention actually chooses.

    An entry whose cost is identical under all twenty-five grammars adds the same constant to every
    total.  It cannot move a ranking; it can only make a field look expensive.  Each field is
    therefore re-ranked on its movable entries alone, and if a field's ranking changes when they are
    removed, the published ranking was measuring the corpus rather than the conventions.

    Single-operator support is reported separately from constant cost, because they are not the same
    predicate: a single-operator tree is always constant (no reordering can touch it), but a
    constant-cost entry need not be single-operator, and a constant cost need not be zero.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = entry_rows(corpus, grammars, workers)
    fields = tuple(field for field in FIELDS if any(row["field"] == field for row in rows))
    per_field: dict[str, dict[str, Any]] = {}
    for field in fields:
        subset = [row for row in rows if row["field"] == field]
        constant = [row for row in subset if len(set(row["costs"].values())) == 1]
        movable = [row for row in subset if len(set(row["costs"].values())) > 1]
        full_totals = {
            grammar.id: sum(row["costs"][grammar.id] for row in subset) for grammar in grammars
        }
        movable_totals = {
            grammar.id: sum(row["costs"][grammar.id] for row in movable) for grammar in grammars
        }
        full_ranking = competition_ranking(full_totals)
        movable_ranking = competition_ranking(movable_totals)
        full_ranks = {entry["id"]: entry["rank"] for entry in full_ranking}
        movable_ranks = {entry["id"]: entry["rank"] for entry in movable_ranking}
        full_spread = max(full_totals.values()) - min(full_totals.values())
        movable_spread = max(movable_totals.values()) - min(movable_totals.values())
        per_field[field] = {
            "entry_count": len(subset),
            "constant_entries": tuple(row["name"] for row in constant),
            "constant_count": len(constant),
            "constant_at_zero": sum(
                1 for row in constant if next(iter(row["costs"].values())) == 0
            ),
            "single_operator_entries": tuple(
                row["name"] for row in subset if row["support_size"] <= 1
            ),
            "single_operator_count": sum(1 for row in subset if row["support_size"] <= 1),
            "forced_total": sum(next(iter(row["costs"].values())) for row in constant),
            "movable_count": len(movable),
            "full_ranks": full_ranks,
            "movable_ranks": movable_ranks,
            "full_spread": full_spread,
            "movable_spread": movable_spread,
            "spread_survival": 1.0 if full_spread == 0 else movable_spread / full_spread,
            "ranking_identical": tuple(entry["id"] for entry in full_ranking)
            == tuple(entry["id"] for entry in movable_ranking),
            "ranks_identical": full_ranks == movable_ranks,
            "control_rank_full": full_ranks[CONTROL.id],
            "control_rank_movable": movable_ranks[CONTROL.id],
            "control_rank_stable": full_ranks[CONTROL.id] == movable_ranks[CONTROL.id],
            "oracle_total": sum(min(row["costs"].values()) for row in subset),
            "best_total": min(full_totals.values()),
        }
    return {
        "fields": fields,
        "per_field": per_field,
        "constant_total": sum(per_field[field]["constant_count"] for field in fields),
        "single_operator_total": sum(per_field[field]["single_operator_count"] for field in fields),
        "all_field_ranks_stable": all(per_field[field]["ranks_identical"] for field in fields),
        "all_control_ranks_stable": all(
            per_field[field]["control_rank_stable"] for field in fields
        ),
    }


# ---------------------------------------------------------------------------- the headline answers


def compromise_report(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """THE headline: is any grammar good everywhere, or is ``G0`` a compromise?

    A compromise has a shape, and the shape is measurable.  Its mean rank is good, its worst rank is
    not disastrous, and it is not uniquely best anywhere.  A dominant grammar has the opposite
    profile: it is first, or nearly first, in every field.  This function computes both profiles for
    all twenty-five grammars and reports where ``G0`` falls, without deciding in advance which
    answer the data is allowed to give.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    table = field_table(corpus, grammars, workers)
    fields = table["fields"]
    per_field = table["per_field"]
    per_grammar = []
    for grammar in grammars:
        ranks = {field: per_field[field]["ranks"][grammar.id] for field in fields}
        firsts = tuple(field for field in fields if ranks[field] == 1)
        outright = tuple(
            field
            for field in fields
            if per_field[field]["best_grammars"] == (grammar.id,)
        )
        per_grammar.append(
            {
                "id": grammar.id,
                "precedence": table["labels"][grammar.id],
                "ranks": ranks,
                "mean_rank": fmean(ranks.values()),
                "worst_rank": max(ranks.values()),
                "best_rank": min(ranks.values()),
                "rank_spread": max(ranks.values()) - min(ranks.values()),
                "ever_first": bool(firsts),
                "first_in": firsts,
                "ever_uniquely_first": bool(outright),
                "uniquely_first_in": outright,
                "top3_everywhere": all(rank <= 3 for rank in ranks.values()),
                "summed_total": table["summed_totals"][grammar.id],
                "summed_rank": table["summed_ranks"][grammar.id],
            }
        )
    by_id = {item["id"]: item for item in per_grammar}
    control = by_id[CONTROL.id]
    top3 = tuple(item["id"] for item in per_grammar if item["top3_everywhere"])
    control_total = control["summed_total"]
    beats_control = tuple(
        {
            "id": item["id"],
            "precedence": item["precedence"],
            "total": item["summed_total"],
            "margin": control_total - item["summed_total"],
            "percent": (
                100.0 * (control_total - item["summed_total"]) / control_total
                if control_total
                else 0.0
            ),
        }
        for item in sorted(per_grammar, key=lambda item: (item["summed_total"], item["id"]))
        if item["summed_total"] < control_total
    )
    mean_ranks = sorted(item["mean_rank"] for item in per_grammar)
    worst_ranks = sorted(item["worst_rank"] for item in per_grammar)
    mean_rank_position = 1 + sum(
        1 for item in per_grammar if item["mean_rank"] < control["mean_rank"]
    )
    # The compromise signature, stated as a conjunction so that the verdict is a measurement and not
    # a reading of the numbers: a good mean rank, never uniquely best, and a worst rank that is not
    # the worst available.
    signature = {
        "mean_rank_better_than_median": control["mean_rank"] < median(mean_ranks),
        "never_uniquely_first": not control["ever_uniquely_first"],
        "worst_rank_below_maximum": control["worst_rank"] < max(worst_ranks),
    }
    return {
        "fields": fields,
        "per_grammar": tuple(
            sorted(per_grammar, key=lambda item: (item["mean_rank"], item["id"]))
        ),
        "by_id": by_id,
        "control": control,
        "top3_in_every_field": top3,
        "any_top3_everywhere": bool(top3),
        "beats_control_on_sum": beats_control,
        "beats_control_count": len(beats_control),
        "best_summed": table["summed_ranking"][0],
        "control_summed_total": control_total,
        "control_summed_rank": table["control_summed_rank"],
        "control_mean_rank": control["mean_rank"],
        "control_worst_rank": control["worst_rank"],
        "control_best_rank": control["best_rank"],
        "control_mean_rank_position": mean_rank_position,
        "median_mean_rank": median(mean_ranks),
        "best_mean_rank": mean_ranks[0],
        "best_mean_rank_grammars": tuple(
            sorted(item["id"] for item in per_grammar if item["mean_rank"] == mean_ranks[0])
        ),
        "signature": signature,
        "verdict": "compromise" if all(signature.values()) else "not_a_compromise",
    }


def dominance_report(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
    trigonometry: dict[str, Any] | None = None,
    table: dict[str, Any] | None = None,
    survival: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Does any grammar beat ``G0`` on the whole workload, cost AND identity survival together?

    The summed cost answers only half the headline.  A convention that writes the corpus in fewer
    brackets but breaks identities the conventional one keeps has not beaten it; it has traded.  So
    the two measured axes are put side by side and the question becomes a dominance question: is
    there a grammar at least as good as ``G0`` on both, and strictly better on one?

    ``trigonometry`` optionally adds experiment 0036's survival count as a third axis - the fifth
    field, on the axis it was measured on - so the dominance test can be run over the whole series
    rather than over this card's four fields alone.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    table = field_table(corpus, grammars, workers) if table is None else table
    survival = survival_table(corpus, grammars, workers) if survival is None else survival
    axes = []
    for grammar in grammars:
        row = {
            "id": grammar.id,
            "precedence": table["labels"][grammar.id],
            "cost": table["summed_totals"][grammar.id],
            "kept": survival["overall_counts"][grammar.id],
        }
        if trigonometry is not None:
            row["trigonometry_kept"] = trigonometry["counts"][grammar.id]
        axes.append(row)
    by_id = {row["id"]: row for row in axes}
    control = by_id[CONTROL.id]

    def _at_least_as_good(row: dict[str, Any]) -> bool:
        good = row["cost"] <= control["cost"] and row["kept"] >= control["kept"]
        if trigonometry is not None:
            good = good and row["trigonometry_kept"] >= control["trigonometry_kept"]
        return good

    def _strictly_better(row: dict[str, Any]) -> bool:
        better = row["cost"] < control["cost"] or row["kept"] > control["kept"]
        if trigonometry is not None:
            better = better or row["trigonometry_kept"] > control["trigonometry_kept"]
        return better

    dominating = tuple(
        row["id"]
        for row in axes
        if row["id"] != CONTROL.id and _at_least_as_good(row) and _strictly_better(row)
    )
    cheaper = tuple(row["id"] for row in axes if row["cost"] < control["cost"])
    keeps_more = tuple(row["id"] for row in axes if row["kept"] > control["kept"])
    # The grammars that lose NOTHING on the survival axis (both axes of it, when trigonometry is
    # supplied).  Among those, cost is the only thing left to compare, and where the control falls
    # in that short list is the sharpest form of the compromise answer.
    lossless = tuple(
        row
        for row in axes
        if row["kept"] == survival["identity_count"]
        and (trigonometry is None or row["trigonometry_kept"] == trigonometry["identity_count"])
    )
    lossless_sorted = tuple(sorted(lossless, key=lambda row: (row["cost"], row["id"])))
    return {
        "axes": tuple(axes),
        "control": control,
        "dominating_grammars": dominating,
        "any_dominates_control": bool(dominating),
        "cheaper_than_control": cheaper,
        "cheaper_than_control_count": len(cheaper),
        "keeps_more_than_control": keeps_more,
        "keeps_more_than_control_count": len(keeps_more),
        "cheaper_but_loses_identities": tuple(
            row["id"] for row in axes if row["cost"] < control["cost"] and row["kept"] < control["kept"]
        ),
        "lossless_grammars": tuple(row["id"] for row in lossless_sorted),
        "lossless_count": len(lossless_sorted),
        "cheapest_lossless": lossless_sorted[0] if lossless_sorted else None,
        "control_is_cheapest_lossless": bool(lossless_sorted)
        and lossless_sorted[0]["id"] == CONTROL.id,
        "lossless_runner_up_margin": (
            lossless_sorted[1]["cost"] - lossless_sorted[0]["cost"]
            if len(lossless_sorted) > 1
            else None
        ),
        "includes_trigonometry": trigonometry is not None,
    }


def domain_worlds_report(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
    include_survival: bool = True,
    include_trigonometry: bool = False,
    timing: bool = False,
) -> dict[str, Any]:
    """The whole experiment as one structure, with the five headline answers on top."""
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    audit = corpus_audit(corpus)
    bridge = bridge_audit(corpus, grammars)
    table = field_table(corpus, grammars, workers)
    champions = field_champions(corpus, grammars, workers)
    compromise = compromise_report(corpus, grammars, workers)
    orientation = orientation_table(corpus, grammars)
    nulls = null_model(corpus, grammars, workers)
    survival = survival_table(corpus, grammars, workers) if include_survival else None
    trigonometry = trigonometry_survival_reference(workers) if include_trigonometry else None
    dominance = (
        dominance_report(corpus, grammars, workers, trigonometry, table, survival)
        if include_survival
        else None
    )
    report: dict[str, Any] = {
        "corpus": audit,
        "bridge": bridge,
        "field_table": table,
        "field_champions": champions,
        "compromise": compromise,
        "orientation": orientation,
        "null_model": nulls,
        "survival": survival,
        "dominance": dominance,
        "answers": {
            "q1_top3_in_all_fields": {
                "grammars": compromise["top3_in_every_field"],
                "any": compromise["any_top3_everywhere"],
            },
            "q2_beats_control_on_sum": {
                "count": compromise["beats_control_count"],
                "best": compromise["beats_control_on_sum"][0]
                if compromise["beats_control_on_sum"]
                else None,
                "control_total": compromise["control_summed_total"],
                "control_rank": compromise["control_summed_rank"],
                "dominates_on_both_axes": None if dominance is None else dominance["dominating_grammars"],
            },
            "q3_control_profile": {
                "mean_rank": compromise["control_mean_rank"],
                "worst_rank": compromise["control_worst_rank"],
                "best_rank": compromise["control_best_rank"],
                "signature": compromise["signature"],
                "verdict": compromise["verdict"],
            },
            "q4_field_champions": {
                "winners": champions["winners"],
                "differ": champions["winners_differ"],
            },
            "q5_reversed_directions": {
                "laws": orientation["laws_that_reverse_somewhere"],
                "law_count": orientation["laws_that_reverse_count"],
                "world_count": orientation["worlds_with_a_reversal_count"],
                "cells": orientation["reversal_cells"],
                "of_cells": orientation["total_cells"],
            },
        },
    }
    if include_trigonometry:
        report["trigonometry_reference"] = trigonometry
    if timing:
        report["parallel_decision"] = parallel_decision(corpus, grammars)
    return report


# ------------------------------------------------------------------------------------ concurrency
#
# Repository policy is multicore by default, and it also says a sequential path is a valid outcome
# when a measurement justifies it.  This module has two workloads with very different profiles, so
# it takes the decision twice, from numbers measured HERE rather than carried over from another
# module.  See :func:`parallel_decision` and :func:`measure_cell_seconds`.

#: Cores kept free so a sweep cannot starve the interactive MCP session.
WORKER_HEADROOM_CORES: int = 2

#: An upper bound on the spawn cost any one atlas has to amortise.
WORKER_CAP: int = 12

#: What it costs to raise a spawn-start process pool whose workers each import this module, and so
#: SymPy.
#:
#: **Measured on this machine, not inherited from another experiment.**
#: :func:`measure_pool_startup` raises a pool of the default worker count and runs one trivial cell
#: in each; the recorded run on 16 cores with 12 workers is ``1.17`` s, minimum of three, and this
#: constant rounds it up.  Experiment 0036 declares ``4.0`` s for the same quantity; that figure is
#: NOT reused, because it was measured on a different import graph.
POOL_STARTUP_SECONDS: float = 1.2

#: Measured seconds per cell for the two workloads, and the reason they take opposite decisions.
#:
#: A cost cell is one written form rendered under all 25 grammars in pure Python; a survival cell is
#: two SymPy ``simplify`` calls on each side, a third on their difference, and a ``solve`` over each
#: denominator.  They differ by nearly two orders of magnitude, which is exactly why a cell COUNT
#: cannot decide this and a measured per-cell cost can.  Recorded run: ``0.033`` s for 48 cost cells
#: (``6.8e-4`` s each) and ``15.2`` s for 375 survival cells (``0.041`` s each).
COST_CELL_SECONDS: float = 6.8e-04
SURVIVAL_CELL_SECONDS: float = 0.041


def worker_count_for(cores: int, cell_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``cell_count`` independent cells."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(cell_count, 1)))


def default_worker_count(cell_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, cell_count)


def should_parallelise(cell_count: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising for this much work, from measured costs.

    The rule compares the sequential estimate against ``POOL_STARTUP_SECONDS`` plus the divided
    work.  A cell count alone cannot answer this, and assuming it can is how a sweep ends up slower
    in parallel than in sequence - which is what 0034 measured for the rendering workload and what
    this module re-measures instead of copying.
    """
    if workers <= 1 or cell_count <= 1:
        return False
    sequential = cell_count * seconds_per_cell
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_cells(
    task: Any,
    payloads: Sequence[Any],
    workers: int | None,
    seconds_per_cell: float,
) -> list[Any]:
    """Run one independent cell per payload, across processes when the measurement says to.

    Every cell is a pure function of its payload, ``executor.map`` preserves input order, and the
    cells share no state, so the two paths return identical records.  The test suite asserts that
    rather than assuming it.  ``workers=None`` takes the measured decision; an explicit ``workers``
    overrides it, which is what lets a test force both paths over the same work.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(len(payloads), seconds_per_cell, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [task(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(task, payloads, chunksize=1))


def _trivial_cell(payload: int) -> int:
    """A cell that does nothing, so that timing it times only the pool."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` is the input to :func:`should_parallelise`, so it has to be a
    measurement rather than a number carried over from another experiment.  Minimum of ``repeats``
    runs, because a startup time is a floor that background load can only push up.
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


def measure_cell_seconds(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
    survival_sample: int = 12,
) -> dict[str, Any]:
    """Time one cell of each workload, so the routing constants above are evidence and not a guess."""
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    entries = corpus_entries(corpus)
    start = time.perf_counter()
    for entry in entries:
        _cost_cell((entry, grammars))
    cost_elapsed = time.perf_counter() - start
    cost_cells = len(entries)

    laws = two_sided_laws(corpus)
    payloads = [(law, grammar.id) for law in laws for grammar in grammars][:survival_sample]
    start = time.perf_counter()
    for payload in payloads:
        _reading_cell(payload)
    survival_elapsed = time.perf_counter() - start
    return {
        "cost_cells": cost_cells,
        "renders": cost_cells * len(grammars),
        "cost_seconds": cost_elapsed,
        "cost_seconds_per_cell": cost_elapsed / cost_cells if cost_cells else 0.0,
        "survival_cells_sampled": len(payloads),
        "survival_seconds": survival_elapsed,
        "survival_seconds_per_cell": survival_elapsed / len(payloads) if payloads else 0.0,
        "declared_cost_seconds_per_cell": COST_CELL_SECONDS,
        "declared_survival_seconds_per_cell": SURVIVAL_CELL_SECONDS,
    }


def parallel_decision(
    corpus: Sequence[Law] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """Time both paths of the survival atlas and check they agree, then record which one won.

    Parallelism changes only how fast, never what is measured, so the equality of the two record
    sets is part of the measurement rather than an afterthought.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    laws = two_sided_laws(corpus)
    survival_cells = len(laws) * len(grammars)
    cost_cells = len(corpus_entries(corpus))
    survival_workers = default_worker_count(survival_cells)
    cost_workers = default_worker_count(cost_cells)

    start = time.perf_counter()
    sequential = survival_table(corpus, grammars, workers=1)
    survival_sequential = time.perf_counter() - start

    start = time.perf_counter()
    parallel = survival_table(corpus, grammars, workers=survival_workers)
    survival_parallel = time.perf_counter() - start

    start = time.perf_counter()
    cost_sequential_rows = entry_rows(corpus, grammars, workers=1)
    cost_sequential = time.perf_counter() - start

    start = time.perf_counter()
    cost_parallel_rows = entry_rows(corpus, grammars, workers=cost_workers)
    cost_parallel = time.perf_counter() - start

    return {
        "cores": os.cpu_count(),
        "survival": {
            "cells": survival_cells,
            "workers": survival_workers,
            "sequential_seconds": survival_sequential,
            "parallel_seconds": survival_parallel,
            "speedup": survival_sequential / survival_parallel if survival_parallel else None,
            "faster": "parallel" if survival_parallel < survival_sequential else "sequential",
            "records_identical": sequential["readings"] == parallel["readings"],
            "default_decision": "parallel"
            if should_parallelise(survival_cells, SURVIVAL_CELL_SECONDS, survival_workers)
            else "sequential",
        },
        "cost": {
            "cells": cost_cells,
            "renders": cost_cells * len(grammars),
            "workers": cost_workers,
            "sequential_seconds": cost_sequential,
            "parallel_seconds": cost_parallel,
            "speedup": cost_sequential / cost_parallel if cost_parallel else None,
            "faster": "parallel" if cost_parallel < cost_sequential else "sequential",
            "records_identical": cost_sequential_rows == cost_parallel_rows,
            "default_decision": "parallel"
            if should_parallelise(cost_cells, COST_CELL_SECONDS, cost_workers)
            else "sequential",
        },
    }
