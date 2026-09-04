"""Experiment 0042: can a problem be split, each fragment written in its own world, and rejoined?

The owner's question, in his words: *can a problem be split into fragments, each fragment solved in
the representation where it solves best, and the results then rejoined into the final answer?*

Half of that is already measured and is NOT re-derived here.  Experiment 0034 computed the
per-formula oracle on its own 58-formula corpus: if every formula could pick its own convention the
corpus costs ``3`` parentheses, while the best SINGLE grammar pays ``29``.  That ``26``-parenthesis
gap is the price of one global convention -- and it **ignores the seams entirely**.  It is an upper
bound on the prize, not a result about rejoining anything.  :func:`oracle_bound` recomputes the same
quantity on THIS corpus and reports it beside the published one, in both cases as a bound.

Experiment 0038 makes the case for decomposition stronger still, and it is worth stating because it
turns routing from an optimisation into a necessity: across ``850`` cells the constant term and the
roots are never manifest together, though nothing in the shape rules forbids it.  If a problem needs
both, no single world supplies both, and the problem has to be split.

**What nobody has measured is the seam.  That is this module.**

The two architectures
---------------------

They are the two real ways an SDK could be built and they have completely different seam costs.

.. code-block:: text

    MODEL I   inline    one document, one host world; a fragment written in its own world is a
                        SUBEXPRESSION of it, and pays whatever the host charges to keep the tree
    MODEL II  named     each fragment is written and evaluated in its OWN world, bound to a name;
                        the name -- a leaf -- is what the next fragment uses

Model I's seam is brackets.  Model II's seam is definition lines, and a definition line is not free:
:data:`NAMING_UNIT_COST` charges one, on the same scale as one bracket pair, and
:func:`naming_break_even` reports the rate at which Model II stops winning, so the modelling choice
is a measured sensitivity rather than a thumb on the scale.

The obligation at every seam
----------------------------

A fragment written for one world means something else when read by another, so a join is only valid
if the value crossing it is preserved.  :func:`verify_routing` decodes every routed document back to
a tree and compares it to the single-world composite on the **project semantic key** --
``(canonical form, domain, excluded points)``, imported from
:func:`parseatlas.alternative_mathematics.semantic_key` -- not on the rendered string.  A routing
that produced a different function would not have solved the problem faster; it would have solved a
different problem.  The ``domain`` slot of that key is inert (``NF-2026-00005``): ``canonical.py``
writes ``"R"`` for every expression, so the operative discrimination is
``(canonical form, excluded points)``.  That is restated in the report's limits and pinned by a test.

The splitting rule is DECLARED, not discovered
----------------------------------------------

.. code-block:: text

    Let L be the control grammar's level containing the root operator ({*, /} or {+, -}).
    Descend from the root through every node whose operator lies in L.
    Every operand hanging off that chain which is itself a Binary node is a FRAGMENT.
    Leaves are not fragments: a leaf is one token and no convention can charge it anything.
    The SKELETON is that chain with each fragment replaced by a hole.

One rule, applied to every object, stated before any number was looked at.  A different rule would
move the numbers and the report says so.  The rule reads the control grammar's levels because the
intended tree is by definition a ``G0`` parse of conventional notation; nothing downstream of the
split consults ``G0`` again.
"""

import os
import re
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

from .alternative_mathematics import semantic_key
from .canonical import canonicalize
from .grammar import Grammar
from .manifest_properties import CORPUS as OBJECT_CORPUS
from .manifest_properties import manifest_set, object_tree
from .notational_cost import CONTROL, GRAMMARS, Formula, binding_powers, needs_brackets, render
from .notational_cost import minimality_audit as _minimality_audit
from .notational_cost import round_trip_audit as _round_trip_audit
from .parallel_worlds import depth
from .parser import Binary, Node, Variable, parse

__all__ = [
    "CORPUS",
    "EXCLUDED",
    "MODELS",
    "NAMING_UNIT_COST",
    "OBJECTIVES",
    "Composite",
    "Split",
    "best_world",
    "best_worlds",
    "composite_tree",
    "decode_routing",
    "decomposition_table",
    "depth_discrimination",
    "fragment_routing_report",
    "fragment_table",
    "fragments",
    "global_host_verdict",
    "host_table",
    "minimality_audit",
    "naming_break_even",
    "objective_agreement",
    "oracle_bound",
    "parallel_decision",
    "readable_routing_audit",
    "round_trip_audit",
    "route",
    "seam_profile",
    "split",
    "verdict_table",
    "verify_routing",
    "visibility_regime_audit",
]

GRAMMAR_BY_ID: dict[str, Grammar] = {grammar.id: grammar for grammar in GRAMMARS}

#: Binding powers per world, computed once.  Read from :attr:`Grammar.levels` by
#: :func:`parseatlas.notational_cost.binding_powers`; nothing here names an operator order.
POWERS: dict[str, dict[str, int]] = {grammar.id: binding_powers(grammar) for grammar in GRAMMARS}

#: Hole names are underscore-prefixed and zero padded so that no corpus variable can collide with
#: one and so that ``_f01`` can never be found inside ``_f010``.  :func:`corpus_audit` checks the
#: first half rather than assuming it.
HOLE_PREFIX: str = "_f"

_HOLE_PATTERN = re.compile(rf"{HOLE_PREFIX}\d\d")

#: An object with fewer than two fragments has nothing to route: there is no seam to pay for.
MINIMUM_FRAGMENTS: int = 2

#: The objectives, because the project has measured different things and they do not agree.
#: ``brackets`` is 0034/0037's notational cost; ``visibility`` is 0038's manifest-property count
#: under its PRIMARY transparent regime; ``visibility_opaque`` is the same count under 0038's second
#: regime, where a bracket hides what is inside it; ``depth`` is the critical path imported from
#: :mod:`parseatlas.parallel_worlds`.
#:
#: The two visibility regimes are carried separately because they answer differently, and the reason
#: is structural rather than empirical: under the transparent regime a shape rule looks THROUGH a
#: bracket, so the manifest set of a fixed tree is a function of the tree and not of the world.
#: :func:`visibility_regime_audit` measures both.
OBJECTIVES: tuple[str, ...] = ("brackets", "visibility", "visibility_opaque", "depth")

#: Which way each objective points.  Kept as data so :func:`best_worlds` has one code path.
OBJECTIVE_DIRECTION: dict[str, str] = {
    "brackets": "min",
    "visibility": "max",
    "visibility_opaque": "max",
    "depth": "min",
}

#: Which 0038 regime each visibility objective reads.
OBJECTIVE_REGIME: dict[str, bool] = {"visibility": False, "visibility_opaque": True}

#: The two architectures.
MODELS: tuple[str, ...] = ("inline", "named")

#: What one named intermediate costs, on the same scale as one bracket pair.
#:
#: **This is a modelling choice and it is named as one.**  A definition line is plainly MORE than
#: one bracket pair in characters -- it carries a name, a binder and a line break -- so ``1`` is the
#: most generous honest rate for Model II.  If Model II loses at this rate the conclusion is robust;
#: if it wins, the win is rate-dependent, and :func:`naming_break_even` reports the exact rate at
#: which it stops winning so the reader can price the choice himself.
NAMING_UNIT_COST: int = 1


# ------------------------------------------------------------------------------- the splitting rule


def control_level(operator: str) -> tuple[str, ...]:
    """The control grammar's level containing ``operator``: ``('*', '/')`` or ``('+', '-')``.

    The split reads the CONTROL grammar and only the control grammar, because the intended tree is
    by definition the ``G0`` parse of conventional notation.  Under a strict world every level is a
    singleton and the same rule would cut a chain of ``a - b + c`` into two; that would make the
    splitting rule a function of the world being routed to, which is exactly the circularity this
    card has to avoid.
    """
    for level in CONTROL.levels:
        if operator in level:
            return level
    raise ValueError(f"operator {operator!r} is not in any level of {CONTROL.id}")


def hole_name(index: int) -> str:
    """The placeholder standing for fragment ``index`` in the skeleton."""
    return f"{HOLE_PREFIX}{index:02d}"


def hole_index(name: str) -> int:
    """Inverse of :func:`hole_name`."""
    return int(name[len(HOLE_PREFIX) :])


@dataclass(frozen=True)
class Split:
    """One composite object cut into fragments and a skeleton.

    ``skeleton`` is the original tree with every fragment replaced by a hole variable, so it keeps
    the exact shape of the chain -- no reassociation, no reordering, no token added or dropped.
    ``positions`` records, per fragment, the operator and the side it hangs off, which is what
    decides whether a host world has to bracket it.
    """

    fragments: tuple[Node, ...]
    skeleton: Node
    positions: tuple[tuple[str, str], ...]
    join_operator: str
    chain_nodes: int

    @property
    def count(self) -> int:
        return len(self.fragments)


def split(tree: Node) -> Split:
    """Apply the declared splitting rule to an intended tree.

    Deterministic: the recursion visits the tree in one fixed order and the rule consults nothing
    but the node operators and the control grammar's levels.  No object is special-cased.
    """
    if not isinstance(tree, Binary):
        return Split((), tree, (), "", 0)
    level = control_level(tree.operator)
    collected: list[Node] = []
    positions: list[tuple[str, str]] = []
    chain = 0

    def walk(node: Node, parent_operator: str, side: str) -> Node:
        nonlocal chain
        if isinstance(node, Binary) and node.operator in level:
            chain += 1
            return Binary(
                node.operator,
                walk(node.left, node.operator, "left"),
                walk(node.right, node.operator, "right"),
            )
        if isinstance(node, Binary):
            collected.append(node)
            positions.append((parent_operator, side))
            return Variable(hole_name(len(collected) - 1))
        return node

    skeleton = walk(tree, "", "")
    return Split(tuple(collected), skeleton, tuple(positions), tree.operator, chain)


def substitute(tree: Node, mapping: dict[str, Node]) -> Node:
    """Replace hole variables by trees.  Used to rebuild a composite from a decoded document."""
    if isinstance(tree, Variable):
        return mapping.get(tree.name, tree)
    if isinstance(tree, Binary):
        return Binary(tree.operator, substitute(tree.left, mapping), substitute(tree.right, mapping))
    return tree


# ------------------------------------------------------------------------------------- the corpus


@dataclass(frozen=True)
class Composite:
    """One composite writing of one named object: the unit this experiment routes."""

    name: str
    field: str
    object_name: str
    role: str
    variable: str | None
    source: str


def composite_tree(item: Composite) -> Node:
    """The intended tree of a composite: its conventional source parsed under the control grammar."""
    return parse(item.source, CONTROL)


def _build_corpus() -> tuple[tuple[Composite, ...], tuple[dict[str, Any], ...]]:
    kept: list[Composite] = []
    excluded: list[dict[str, Any]] = []
    for item in OBJECT_CORPUS:
        for writing in item.writings:
            tree = object_tree(writing)
            parts = split(tree)
            record = Composite(
                name=f"{item.name}.{writing.role}",
                field=item.field,
                object_name=item.name,
                role=writing.role,
                variable=item.variable,
                source=writing.source,
            )
            if parts.count >= MINIMUM_FRAGMENTS:
                kept.append(record)
            else:
                excluded.append(
                    {"name": record.name, "source": record.source, "fragments": parts.count}
                )
    return tuple(kept), tuple(excluded)


#: The corpus: every written form in :data:`parseatlas.manifest_properties.CORPUS` -- experiment
#: 0037's named laws plus 0038's calibration quadratic -- that the splitting rule cuts into at least
#: two fragments.  The filter IS the definition of "composite"; no writing was chosen or dropped by
#: hand, and the ones the rule rejects are published in :data:`EXCLUDED` with their counts.
CORPUS: tuple[Composite, ...]

#: The writings the rule rejects, with the fragment count that rejected them.
EXCLUDED: tuple[dict[str, Any], ...]

CORPUS, EXCLUDED = _build_corpus()

COMPOSITE_BY_NAME: dict[str, Composite] = {item.name: item for item in CORPUS}


def fragments(item: Composite | Node) -> tuple[Node, ...]:
    """The fragments of a composite object, in left-to-right order.

    Accepts either a corpus record or a raw tree, so the rule can be exercised on anything.
    """
    tree = composite_tree(item) if isinstance(item, Composite) else item
    return split(tree).fragments


def as_notational_cost_corpus(
    corpus: Sequence[Composite] | None = None,
) -> tuple[Formula, ...]:
    """Composites AND their fragments as 0034 ``Formula`` records, for the correctness bridge.

    The bridge has to cover what this module actually renders, and this module renders fragments in
    one world and skeletons in another, so both go into the grid rather than the composites alone.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    records: list[Formula] = []
    seen: set[str] = set()
    for item in corpus:
        records.append(Formula(item.name, item.field, item.source))
        seen.add(item.name)
        for index, fragment in enumerate(split(composite_tree(item)).fragments):
            name = f"{item.name}#{index}"
            if name not in seen:
                records.append(Formula(name, item.field, render(fragment, CONTROL)))
                seen.add(name)
    return tuple(records)


def round_trip_audit(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """0034's round-trip bridge, re-run over the composites and every fragment of them."""
    return _round_trip_audit(as_notational_cost_corpus(corpus), GRAMMARS)


def minimality_audit(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """0034's minimality bridge, re-run over the composites and every fragment of them."""
    return _minimality_audit(as_notational_cost_corpus(corpus), GRAMMARS)


def corpus_audit(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Check the corpus is what it claims and that the hole names cannot collide with it."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    names = [item.name for item in corpus]
    counts = [split(composite_tree(item)).count for item in corpus]
    histogram: dict[int, int] = {}
    for value in counts:
        histogram[value] = histogram.get(value, 0) + 1
    fields: dict[str, int] = {}
    for item in corpus:
        fields[item.field] = fields.get(item.field, 0) + 1
    return {
        "size": len(corpus),
        "fields": dict(sorted(fields.items())),
        "excluded": EXCLUDED,
        "excluded_count": len(EXCLUDED),
        "fragment_total": sum(counts),
        "fragment_histogram": dict(sorted(histogram.items())),
        "min_fragments": min(counts) if counts else 0,
        "max_fragments": max(counts) if counts else 0,
        "duplicate_names": tuple(sorted({name for name in names if names.count(name) > 1})),
        "hole_prefix_free": all(HOLE_PREFIX not in item.source for item in corpus),
        "sources_canonical": all(
            render(composite_tree(item), CONTROL) == item.source for item in corpus
        ),
    }


# ------------------------------------------------------------------------------- the three objectives


def fragment_cost(fragment: Node, grammar: Grammar) -> int:
    """Bracket pairs the world forces on this fragment."""
    return render(fragment, grammar).count("(")


def world_scores(fragment: Node, objective: str, variable: str | None = None) -> dict[str, int]:
    """The score of every world on one fragment under one objective.

    ``brackets`` is minimised, both visibility objectives maximised, ``depth`` minimised.  ``depth`` is the
    critical path of the intended tree, imported from :mod:`parseatlas.parallel_worlds` rather than
    redefined, and it does not depend on the world: a world chooses how to WRITE a fixed tree, and
    writing does not change a critical path.  :func:`depth_discrimination` measures that rather than
    asserting it.
    """
    if objective == "brackets":
        return {grammar.id: fragment_cost(fragment, grammar) for grammar in GRAMMARS}
    if objective in OBJECTIVE_REGIME:
        opaque = OBJECTIVE_REGIME[objective]
        return {
            grammar.id: len(manifest_set(fragment, grammar, variable, opaque=opaque))
            for grammar in GRAMMARS
        }
    if objective == "depth":
        value = depth(fragment)
        return {grammar.id: value for grammar in GRAMMARS}
    raise ValueError(f"unknown objective {objective!r}; expected one of {OBJECTIVES}")


def best_worlds(fragment: Node, objective: str, variable: str | None = None) -> tuple[str, ...]:
    """Every world tied for best on this fragment under this objective, in registry order."""
    scores = world_scores(fragment, objective, variable)
    target = (
        min(scores.values()) if OBJECTIVE_DIRECTION[objective] == "min" else max(scores.values())
    )
    return tuple(grammar.id for grammar in GRAMMARS if scores[grammar.id] == target)


def best_world(fragment: Node, objective: str, variable: str | None = None) -> Grammar:
    """The world that writes this fragment best under this objective.

    Ties break to registry order, which puts ``G0`` first.  That is the CONSERVATIVE tie-break -- it
    hands every undecided fragment to the conventional world rather than to a world that would make
    routing look better -- and every count of "how often is ``G0`` chosen" is reported twice, once
    as the unique winner and once as a member of the tied set, so the tie-break cannot be mistaken
    for a finding.
    """
    return GRAMMAR_BY_ID[best_worlds(fragment, objective, variable)[0]]


def objective_agreement(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Do the three objectives route a fragment to the same world, or to different ones?"""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    rows = []
    for item in corpus:
        parts = split(composite_tree(item))
        for index, fragment in enumerate(parts.fragments):
            choice = {
                objective: best_world(fragment, objective, item.variable).id
                for objective in OBJECTIVES
            }
            ties = {
                objective: best_worlds(fragment, objective, item.variable)
                for objective in OBJECTIVES
            }
            rows.append(
                {
                    "composite": item.name,
                    "index": index,
                    "source": render(fragment, CONTROL),
                    "chosen": choice,
                    "tied": ties,
                    "all_agree": len(set(choice.values())) == 1,
                    "brackets_visibility_agree": choice["brackets"] == choice["visibility"],
                    "any_common_world": bool(
                        set.intersection(*(set(ties[objective]) for objective in OBJECTIVES))
                    ),
                }
            )
    pairs = {
        f"{first}_vs_{second}": sum(
            1 for row in rows if row["chosen"][first] == row["chosen"][second]
        )
        for index, first in enumerate(OBJECTIVES)
        for second in OBJECTIVES[index + 1 :]
    }
    # The tie structure, because otherwise "objective X sends everything to G0" cannot be told
    # apart from "the tie-break sends everything to G0", and only the first is a finding.
    ties = {
        objective: {
            "control_unique_best": sum(
                1 for row in rows if row["tied"][objective] == (CONTROL.id,)
            ),
            "control_among_best": sum(1 for row in rows if CONTROL.id in row["tied"][objective]),
            "all_worlds_tied": sum(
                1 for row in rows if len(row["tied"][objective]) == len(GRAMMARS)
            ),
            "mean_tie_size": (
                sum(len(row["tied"][objective]) for row in rows) / len(rows) if rows else 0.0
            ),
        }
        for objective in OBJECTIVES
    }
    return {
        "fragments": len(rows),
        "rows": tuple(rows),
        "all_objectives_agree": sum(1 for row in rows if row["all_agree"]),
        "pairwise_agreement": pairs,
        "reconcilable": sum(1 for row in rows if row["any_common_world"]),
        "distinct_choice_patterns": len({tuple(row["chosen"].values()) for row in rows}),
        "choice_patterns": tuple(
            sorted({tuple(row["chosen"][objective] for objective in OBJECTIVES) for row in rows})
        ),
        "ties": ties,
    }


def depth_discrimination(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Can the depth objective separate two worlds at all, on this corpus?

    The intended tree is the datum and a world only chooses how to write it, so the critical path is
    world-invariant by construction.  The interesting question is the one level up: among a
    fragment's SAME-OBJECT reassociations -- the ones a world might write instead -- is any world's
    minimum-cost writing shallower than the intended tree?  If none is, the depth objective ranks
    all 25 worlds equally on every fragment and routes everything to the tie-break world, and that
    is a measured degeneracy rather than an omission.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    rows = []
    for item in corpus:
        for index, fragment in enumerate(split(composite_tree(item)).fragments):
            forms = reassociations(fragment)
            intended = depth(fragment)
            per_world = {}
            for grammar in GRAMMARS:
                costs = [fragment_cost(form, grammar) for form in forms]
                floor = min(costs)
                per_world[grammar.id] = min(
                    depth(form) for form, cost in zip(forms, costs) if cost == floor
                )
            rows.append(
                {
                    "composite": item.name,
                    "index": index,
                    "writings": len(forms),
                    "intended_depth": intended,
                    "cheapest_depths": per_world,
                    "world_invariant": len(set(per_world.values())) == 1,
                    "shallower_available": any(value < intended for value in per_world.values()),
                }
            )
    return {
        "fragments": len(rows),
        "rows": tuple(rows),
        "world_invariant": sum(1 for row in rows if row["world_invariant"]),
        "shallower_available": sum(1 for row in rows if row["shallower_available"]),
        "reassociable": sum(1 for row in rows if row["writings"] > 1),
        "degenerate": all(row["world_invariant"] for row in rows),
    }


#: A chain longer than this is not enumerated; the Catalan count would stop being evidence and start
#: being a stress test.  No fragment in this corpus reaches it, which :func:`depth_discrimination`
#: reports through ``writings``.
REASSOCIATION_CHAIN_CAP: int = 7


def reassociations(tree: Node) -> tuple[Node, ...]:
    """Same-object rewritings of a tree: reassociations of maximal ``+`` and ``*`` chains.

    The token word is fixed and the operand ORDER is fixed, so this is exactly the scope restriction
    :mod:`parseatlas.parallel_worlds` works under: no commutative reordering, no distribution, no
    token added or removed.  ``-`` and ``/`` are excluded because ``a - (b - c)`` is a different
    object, not a different writing of the same one.
    """
    if not isinstance(tree, Binary):
        return (tree,)
    if tree.operator not in ("+", "*"):
        return tuple(
            Binary(tree.operator, left, right)
            for left in reassociations(tree.left)
            for right in reassociations(tree.right)
        )
    operator = tree.operator
    operands: list[Node] = []

    def peel(node: Node) -> None:
        if isinstance(node, Binary) and node.operator == operator:
            peel(node.left)
            peel(node.right)
        else:
            operands.append(node)

    peel(tree)
    if len(operands) > REASSOCIATION_CHAIN_CAP:
        return (tree,)
    parts = [reassociations(operand) for operand in operands]

    def shapes(items: Sequence[tuple[Node, ...]]) -> list[Node]:
        if len(items) == 1:
            return list(items[0])
        out: list[Node] = []
        for cut in range(1, len(items)):
            for left in shapes(items[:cut]):
                for right in shapes(items[cut:]):
                    out.append(Binary(operator, left, right))
        return out

    return tuple(shapes(parts))


# ------------------------------------------------------------------------------------- the routing


def _wrap_needed(
    fragment: Node, piece: str, parent_operator: str, side: str, host: Grammar
) -> dict[str, bool]:
    """Why the host has to bracket this fragment, if it does.  Two independent reasons.

    ``precedence`` -- the host would re-associate the fragment into its neighbours.  That is the
    seam the card asks for by name and it is the parser's own rule, read off
    :func:`parseatlas.notational_cost.needs_brackets`.

    ``unreadable`` -- the fragment's OWN-world rendering does not reparse to the fragment when read
    in the host world.  This is the seam nobody budgets for: routing a fragment to another world
    changes what its characters mean, and an inline document has no other place to say so.
    """
    precedence = needs_brackets(fragment, parent_operator, side, POWERS[host.id])
    try:
        unreadable = parse(piece, host) != fragment
    except ValueError:
        unreadable = True
    return {
        "precedence": bool(precedence),
        "unreadable": bool(unreadable),
        "wrap": bool(precedence or unreadable),
    }


def _fill(skeleton_text: str, pieces: Sequence[str]) -> str:
    return _HOLE_PATTERN.sub(lambda match: pieces[hole_index(match.group(0))], skeleton_text)


def route(
    item: Composite,
    objective: str,
    model: str,
    host: str | None = None,
    naming_unit_cost: int = NAMING_UNIT_COST,
) -> dict[str, Any]:
    """Write one composite by routing every fragment to its best world, under one architecture.

    The returned record NEVER blends the costs.  ``interior_cost`` is what the fragments cost inside
    their own worlds, ``skeleton_cost`` is what the chain costs in the host world, ``seam_cost`` is
    what the join costs, and ``total_cost`` is their sum -- checked against the bracket count of the
    assembled document, so the accounting cannot silently drift.
    """
    if objective not in OBJECTIVES:
        raise ValueError(f"unknown objective {objective!r}; expected one of {OBJECTIVES}")
    if model not in MODELS:
        raise ValueError(f"unknown model {model!r}; expected one of {MODELS}")
    tree = composite_tree(item)
    parts = split(tree)
    if parts.count < MINIMUM_FRAGMENTS:
        raise ValueError(f"{item.name!r} has {parts.count} fragments; nothing to route")
    worlds = tuple(best_world(fragment, objective, item.variable).id for fragment in parts.fragments)
    pieces = tuple(
        render(fragment, GRAMMAR_BY_ID[world])
        for fragment, world in zip(parts.fragments, worlds)
    )
    interior = sum(piece.count("(") for piece in pieces)

    def inline_seam(candidate: Grammar) -> tuple[int, tuple[dict[str, bool], ...]]:
        reasons = tuple(
            _wrap_needed(fragment, piece, parent, side, candidate)
            for fragment, piece, (parent, side) in zip(parts.fragments, pieces, parts.positions)
        )
        return sum(1 for reason in reasons if reason["wrap"]), reasons

    candidates: list[tuple[int, int, int, str]] = []
    for candidate in GRAMMARS:
        skeleton_cost = render(parts.skeleton, candidate).count("(")
        if model == "inline":
            seam = inline_seam(candidate)[0]
        else:
            seam = naming_unit_cost * parts.count
        candidates.append((interior + skeleton_cost + seam, skeleton_cost, seam, candidate.id))
    floor = min(record[0] for record in candidates)
    optimal_hosts = tuple(record[3] for record in candidates if record[0] == floor)
    if host is None:
        best = min(candidates, key=lambda entry: (entry[0], GRAMMARS.index(GRAMMAR_BY_ID[entry[3]])))
        chosen = GRAMMAR_BY_ID[best[3]]
    else:
        chosen = GRAMMAR_BY_ID[host]
    skeleton_text = render(parts.skeleton, chosen)
    skeleton_cost = skeleton_text.count("(")

    if model == "inline":
        seam_count, reasons = inline_seam(chosen)
        rendered_pieces = tuple(
            f"({piece})" if reason["wrap"] else piece
            for piece, reason in zip(pieces, reasons)
        )
        document = _fill(skeleton_text, rendered_pieces)
        lines: tuple[str, ...] = (document,)
        seam_cost = seam_count
        naming_units = 0
        self_describing = False
        host_readable = _reads_in_host(document, chosen, tree)
    else:
        reasons = tuple(
            {"precedence": False, "unreadable": False, "wrap": False} for _ in parts.fragments
        )
        lines = tuple(
            f"{hole_name(index)} := {piece}    [{world}]"
            for index, (piece, world) in enumerate(zip(pieces, worlds))
        ) + (f"result := {skeleton_text}    [{chosen.id}]",)
        document = "\n".join(lines)
        naming_units = parts.count
        seam_cost = naming_unit_cost * naming_units
        self_describing = True
        host_readable = True

    total = interior + skeleton_cost + seam_cost
    per_fragment = tuple(
        {
            "index": index,
            "source": render(fragment, CONTROL),
            "world": world,
            "own_cost": fragment_cost(fragment, GRAMMAR_BY_ID[world]),
            "host_cost": fragment_cost(fragment, chosen),
            "difference": fragment_cost(fragment, chosen) - fragment_cost(fragment, GRAMMAR_BY_ID[world]),
            "piece": piece,
            "position": position,
            "wrap": reason["wrap"],
            "wrap_precedence": reason["precedence"],
            "wrap_unreadable": reason["unreadable"],
        }
        for index, (fragment, world, piece, position, reason) in enumerate(
            zip(parts.fragments, worlds, pieces, parts.positions, reasons)
        )
    )
    record: dict[str, Any] = {
        "composite": item.name,
        "field": item.field,
        "objective": objective,
        "model": model,
        "host": chosen.id,
        "optimal_hosts": optimal_hosts,
        "host_is_optimal": chosen.id in optimal_hosts,
        "fragment_count": parts.count,
        "worlds": worlds,
        "distinct_worlds": len(set(worlds)),
        "pieces": pieces,
        "skeleton_text": skeleton_text,
        "document": document,
        "lines": lines,
        "interior_cost": interior,
        "skeleton_cost": skeleton_cost,
        "seam_cost": seam_cost,
        "naming_units": naming_units,
        "total_cost": total,
        "fragments": per_fragment,
        "forfeited_by_one_convention": sum(row["difference"] for row in per_fragment),
        "self_describing": self_describing,
        "host_readable": host_readable,
        "wraps": sum(1 for row in per_fragment if row["wrap"]),
        "wraps_precedence": sum(1 for row in per_fragment if row["wrap_precedence"]),
        "wraps_unreadable": sum(1 for row in per_fragment if row["wrap_unreadable"]),
    }
    if model == "inline":
        record["accounting_closes"] = document.count("(") == total
    else:
        record["accounting_closes"] = (
            sum(piece.count("(") for piece in pieces) + skeleton_text.count("(")
            == interior + skeleton_cost
        )
    return record


def _reads_in_host(document: str, host: Grammar, tree: Node) -> bool:
    """Would a reader who knows only the host convention recover the intended object?

    For an inline document this is the honest question, and its answer is the measurement that says
    whether Model I's brackets are doing the whole job.  A bracket delimits a scope; it does not
    carry a convention.
    """
    try:
        return parse(document, host) == tree
    except ValueError:
        return False


def decode_routing(record: dict[str, Any]) -> Node:
    """Rebuild the composite from the routed document, reading each part in its declared world.

    This is the decode half of the seam obligation.  It uses only what the document carries: the
    skeleton read in the host world, each piece read in the world it was routed to, and the holes.
    Nothing is copied back from the split record, so a mis-declared world shows up here as a
    different tree rather than as a silent pass.
    """
    skeleton_tree = parse(record["skeleton_text"], GRAMMAR_BY_ID[record["host"]])
    mapping = {
        hole_name(index): parse(piece, GRAMMAR_BY_ID[world])
        for index, (piece, world) in enumerate(zip(record["pieces"], record["worlds"]))
    }
    return substitute(skeleton_tree, mapping)


def single_world_writing(item: Composite, grammar: Grammar) -> Node:
    """The composite as ONE world writes it, read back by that same world."""
    return parse(render(composite_tree(item), grammar), grammar)


def best_single_world(item: Composite) -> dict[str, Any]:
    """The cheapest single world for this composite, and what it costs there."""
    costs = {grammar.id: fragment_cost(composite_tree(item), grammar) for grammar in GRAMMARS}
    floor = min(costs.values())
    return {
        "costs": costs,
        "cost": floor,
        "worlds": tuple(grammar.id for grammar in GRAMMARS if costs[grammar.id] == floor),
        "control_cost": costs[CONTROL.id],
    }


def verify_routing(record: dict[str, Any], item: Composite | None = None) -> dict[str, Any]:
    """The obligation at the seam: does the routed composite denote the single-world composite?

    Compared on the project semantic key ``(canonical form, domain, excluded points)`` and NOT on
    the rendered string.  A routing that fails this has not solved the problem faster; it has solved
    a different problem, and this is the single most likely way this card could be wrong.
    """
    item = item if item is not None else COMPOSITE_BY_NAME[record["composite"]]
    routed = decode_routing(record)
    baseline_world = GRAMMAR_BY_ID[best_single_world(item)["worlds"][0]]
    single = single_world_writing(item, baseline_world)
    routed_key = semantic_key(canonicalize(routed))
    single_key = semantic_key(canonicalize(single))
    return {
        "composite": item.name,
        "objective": record["objective"],
        "model": record["model"],
        "baseline_world": baseline_world.id,
        "routed_key": routed_key,
        "single_key": single_key,
        "preserved": routed_key == single_key,
        "tree_identical": routed == composite_tree(item),
    }


# ---------------------------------------------------------------------------------- the verdict


def _verdict_cell(payload: tuple[Composite, str, str, int]) -> dict[str, Any]:
    """One (composite, objective, model) cell, picklable so the sweep can cross processes."""
    item, objective, model, naming_unit_cost = payload
    record = route(item, objective, model, naming_unit_cost=naming_unit_cost)
    check = verify_routing(record, item)
    baseline = best_single_world(item)
    return {
        "composite": item.name,
        "field": item.field,
        "objective": objective,
        "model": model,
        "fragment_count": record["fragment_count"],
        "best_single_cost": baseline["cost"],
        "best_single_worlds": baseline["worlds"],
        "control_cost": baseline["control_cost"],
        "routed_cost": record["total_cost"],
        "interior_cost": record["interior_cost"],
        "skeleton_cost": record["skeleton_cost"],
        "seam_cost": record["seam_cost"],
        "host": record["host"],
        "optimal_hosts": record["optimal_hosts"],
        "worlds": record["worlds"],
        "distinct_worlds": record["distinct_worlds"],
        "wraps": record["wraps"],
        "wraps_unreadable": record["wraps_unreadable"],
        "host_readable": record["host_readable"],
        "self_describing": record["self_describing"],
        "accounting_closes": record["accounting_closes"],
        "forfeited_by_one_convention": record["forfeited_by_one_convention"],
        "wins": record["total_cost"] < baseline["cost"],
        "ties": record["total_cost"] == baseline["cost"],
        "loses": record["total_cost"] > baseline["cost"],
        "preserved": check["preserved"],
        "tree_identical": check["tree_identical"],
        "document": record["document"],
    }


def verdict_table(
    corpus: Sequence[Composite] | None = None,
    objectives: Sequence[str] | None = None,
    models: Sequence[str] | None = None,
    workers: int | None = None,
    naming_unit_cost: int = NAMING_UNIT_COST,
) -> dict[str, Any]:
    """The comparison that decides the card, per object and per objective, for both architectures.

    Columns, never blended: best single world cost, routed cost, seam cost, and whether routing
    still wins.  The corpus totals carry two baselines, because they answer different questions --
    the sum of per-object bests is what an oracle that could switch convention per OBJECT would pay,
    and the best single world over the whole corpus is what one global convention pays.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    objectives = tuple(objectives) if objectives is not None else OBJECTIVES
    models = tuple(models) if models is not None else MODELS
    payloads = [
        (item, objective, model, naming_unit_cost)
        for objective in objectives
        for model in models
        for item in corpus
    ]
    rows = _map_cells(_verdict_cell, payloads, workers, VERDICT_CELL_SECONDS)
    totals = {}
    for objective in objectives:
        for model in models:
            subset = [row for row in rows if row["objective"] == objective and row["model"] == model]
            totals[f"{objective}/{model}"] = {
                "objective": objective,
                "model": model,
                "objects": len(subset),
                "best_single_total": sum(row["best_single_cost"] for row in subset),
                "routed_total": sum(row["routed_cost"] for row in subset),
                "interior_total": sum(row["interior_cost"] for row in subset),
                "skeleton_total": sum(row["skeleton_cost"] for row in subset),
                "seam_total": sum(row["seam_cost"] for row in subset),
                "wins": sum(1 for row in subset if row["wins"]),
                "ties": sum(1 for row in subset if row["ties"]),
                "loses": sum(1 for row in subset if row["loses"]),
                "preserved": sum(1 for row in subset if row["preserved"]),
                "host_readable": sum(1 for row in subset if row["host_readable"]),
                "seam_zero_rows": sum(1 for row in subset if row["seam_cost"] == 0),
                "accounting_closes": all(row["accounting_closes"] for row in subset),
            }
    grid = corpus_costs(corpus)
    for key, entry in totals.items():
        entry["global_single_total"] = grid["best_total"]
        entry["global_single_world"] = grid["best_world"]
        entry["beats_global_single"] = entry["routed_total"] < grid["best_total"]
        entry["margin_vs_global_single"] = grid["best_total"] - entry["routed_total"]
        entry["margin_vs_control"] = grid["control_total"] - entry["routed_total"]
    return {
        "rows": tuple(rows),
        "totals": totals,
        "objectives": objectives,
        "models": models,
        "naming_unit_cost": naming_unit_cost,
        "corpus_costs": grid,
        "all_preserved": all(row["preserved"] for row in rows),
        "cells": len(rows),
    }


def corpus_costs(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """What one global convention costs on this corpus, per world."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    totals = {
        grammar.id: sum(fragment_cost(composite_tree(item), grammar) for item in corpus)
        for grammar in GRAMMARS
    }
    floor = min(totals.values())
    ordered = sorted(totals.items(), key=lambda entry: (entry[1], entry[0]))
    return {
        "totals": totals,
        "ranking": tuple({"id": key, "total": value} for key, value in ordered),
        "best_total": floor,
        "best_world": next(grammar.id for grammar in GRAMMARS if totals[grammar.id] == floor),
        "best_worlds": tuple(grammar.id for grammar in GRAMMARS if totals[grammar.id] == floor),
        "control_total": totals[CONTROL.id],
        "worst_total": max(totals.values()),
    }


def decomposition_table(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Where the brackets of a single-world document actually sit: inside, on the chain, or at the joins.

    This is the structural fact the verdict rests on.  A bracket inside a fragment is one routing can
    move; a bracket at a JOIN is one routing cannot touch, because it belongs to the seam and not to
    any fragment.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    splits = [(item, split(composite_tree(item))) for item in corpus]
    rows = []
    for grammar in GRAMMARS:
        interior = sum(
            fragment_cost(fragment, grammar) for _, parts in splits for fragment in parts.fragments
        )
        skeleton = sum(render(parts.skeleton, grammar).count("(") for _, parts in splits)
        whole = sum(fragment_cost(composite_tree(item), grammar) for item, _ in splits)
        rows.append(
            {
                "id": grammar.id,
                "whole": whole,
                "interior": interior,
                "skeleton": skeleton,
                "joins": whole - interior - skeleton,
            }
        )
    by_id = {row["id"]: row for row in rows}
    floor = min(row["whole"] for row in rows)
    return {
        "rows": tuple(rows),
        "by_id": by_id,
        "control": by_id[CONTROL.id],
        "best": next(row for row in rows if row["whole"] == floor),
        "interior_floor": sum(
            min(fragment_cost(fragment, grammar) for grammar in GRAMMARS)
            for _, parts in splits
            for fragment in parts.fragments
        ),
        "skeleton_floor": sum(
            min(render(parts.skeleton, grammar).count("(") for grammar in GRAMMARS)
            for _, parts in splits
        ),
        "join_floor": min(row["joins"] for row in rows),
    }


def oracle_bound(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """The prize, the seamless bound and the published one, as separate numbers.

    Three quantities, and confusing them is how a routing result gets overclaimed:

    * ``single_world`` -- what the best ONE global convention pays on this corpus;
    * ``per_object_oracle`` -- what an oracle switching convention per OBJECT would pay (0034's
      quantity, recomputed on this corpus);
    * ``fragment_oracle`` -- what an oracle switching per FRAGMENT would pay **with no seam at all**.

    The third is the upper bound on what routing could ever deliver.  It is a bound and not a
    result: it prices every fragment in its own world and charges nothing whatever for putting them
    back together.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grid = corpus_costs(corpus)
    per_object = sum(best_single_world(item)["cost"] for item in corpus)
    interior = 0
    skeleton = 0
    for item in corpus:
        parts = split(composite_tree(item))
        interior += sum(
            min(fragment_cost(fragment, grammar) for grammar in GRAMMARS)
            for fragment in parts.fragments
        )
        skeleton += min(render(parts.skeleton, grammar).count("(") for grammar in GRAMMARS)
    fragment_oracle = interior + skeleton
    return {
        "objects": len(corpus),
        "single_world": grid["best_total"],
        "single_world_id": grid["best_world"],
        "control_total": grid["control_total"],
        "per_object_oracle": per_object,
        "per_object_gap": grid["best_total"] - per_object,
        "fragment_oracle": fragment_oracle,
        "fragment_interior_oracle": interior,
        "fragment_skeleton_oracle": skeleton,
        "prize": grid["best_total"] - fragment_oracle,
        "published_0034": {
            "corpus": "0034, 58 named formulas",
            "per_formula_oracle": 3,
            "best_single_world": 29,
            "gap": 26,
            "status": "seamless upper bound, not an achieved result",
        },
    }


def global_host_verdict(
    corpus: Sequence[Composite] | None = None,
    objectives: Sequence[str] | None = None,
    models: Sequence[str] | None = None,
    naming_unit_cost: int = NAMING_UNIT_COST,
) -> dict[str, Any]:
    """Routing under ONE host convention for the whole corpus, against ONE convention with no routing.

    :func:`verdict_table` lets every document pick its own host, which is a second kind of routing --
    0034's per-OBJECT oracle -- riding on top of the fragment routing this card is about.  That is
    the right comparison against a per-object baseline and the wrong one against a global baseline.
    This function fixes one host for all 38 documents, which is what "an SDK with a house
    convention" actually means, and prices it against the best single world with no routing at all.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    objectives = tuple(objectives) if objectives is not None else OBJECTIVES
    models = tuple(models) if models is not None else MODELS
    grid = corpus_costs(corpus)
    out: dict[str, Any] = {}
    for objective in objectives:
        for model in models:
            per_host = {}
            for grammar in GRAMMARS:
                records = [
                    route(item, objective, model, host=grammar.id, naming_unit_cost=naming_unit_cost)
                    for item in corpus
                ]
                per_host[grammar.id] = {
                    "total": sum(record["total_cost"] for record in records),
                    "interior": sum(record["interior_cost"] for record in records),
                    "skeleton": sum(record["skeleton_cost"] for record in records),
                    "seam": sum(record["seam_cost"] for record in records),
                    "host_readable": sum(1 for record in records if record["host_readable"]),
                }
            floor = min(entry["total"] for entry in per_host.values())
            best = next(
                grammar.id for grammar in GRAMMARS if per_host[grammar.id]["total"] == floor
            )
            out[f"{objective}/{model}"] = {
                "objective": objective,
                "model": model,
                "per_host": per_host,
                "best_host": best,
                "best_hosts": tuple(
                    grammar.id for grammar in GRAMMARS if per_host[grammar.id]["total"] == floor
                ),
                "routed_total": floor,
                "routed_breakdown": per_host[best],
                "control_host_total": per_host[CONTROL.id]["total"],
                "single_world_total": grid["best_total"],
                "single_world_id": grid["best_world"],
                "control_single_total": grid["control_total"],
                "margin": grid["best_total"] - floor,
                "wins": floor < grid["best_total"],
            }
    return {"per_case": out, "single_world": grid["best_total"], "single_world_id": grid["best_world"]}


def visibility_regime_audit(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Why the two visibility objectives answer differently, measured on every fragment.

    Under 0038's PRIMARY transparent regime a shape rule looks through a bracket, so the manifest
    set of a fixed tree does not depend on which world wrote it: the count is world-invariant on
    every fragment, and the objective can express no preference at all.  Under the opaque regime a
    bracket hides what is inside it, the count moves, and the objective becomes a real one.

    This is a property of the REGIME, not a shortage of corpus, and the report says so rather than
    presenting a structural constant as an empirical finding.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    out = {}
    for objective, opaque in OBJECTIVE_REGIME.items():
        rows = []
        for item in corpus:
            for index, fragment in enumerate(split(composite_tree(item)).fragments):
                scores = {
                    grammar.id: len(manifest_set(fragment, grammar, item.variable, opaque=opaque))
                    for grammar in GRAMMARS
                }
                rows.append(
                    {
                        "composite": item.name,
                        "index": index,
                        "source": render(fragment, CONTROL),
                        "min": min(scores.values()),
                        "max": max(scores.values()),
                        "range": max(scores.values()) - min(scores.values()),
                        "varies": len(set(scores.values())) > 1,
                        "control_score": scores[CONTROL.id],
                        "control_is_best": scores[CONTROL.id] == max(scores.values()),
                    }
                )
        out[objective] = {
            "regime": "opaque" if opaque else "transparent",
            "fragments": len(rows),
            "varying": sum(1 for row in rows if row["varies"]),
            "max_range": max((row["range"] for row in rows), default=0),
            "control_is_best": sum(1 for row in rows if row["control_is_best"]),
            "world_invariant": all(not row["varies"] for row in rows),
            "rows": tuple(rows),
        }
    return out


def readable_routing_audit(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """The sharpest question this card can ask: what does inline routing give up if the document
    must stay READABLE in its host convention?

    A bracket delimits a scope; it does not carry a convention.  So an inline document that a host
    reader can decode with no side channel is one in which every fragment's own-world rendering
    reparses, under the host, to that fragment.  Restrict the routing to those worlds and the answer
    is forced rather than empirical:

    * the token word of a fragment is fixed, so an h-writing of it differs only in bracket placement;
    * :func:`parseatlas.notational_cost.render` emits a bracket exactly where ``h`` would otherwise
      re-associate, and 0034's minimality audit verifies that every one of them is load-bearing, so
      ``render(F, h)`` is THE minimum-bracket h-writing of ``F``;
    * therefore any world whose rendering the host reads correctly costs at least as much as the
      host itself, with equality exactly when the two renderings coincide.

    **Host-readable inline routing therefore delivers exactly zero.**  This function checks that
    over the whole 25-host x fragment x 25-world grid rather than leaving it as an argument, and
    reports any counter-example it finds.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    frags = [
        fragment for item in corpus for fragment in split(composite_tree(item)).fragments
    ]
    cheaper: list[dict[str, Any]] = []
    checks = 0
    per_host = {}
    for host in GRAMMARS:
        readable_total = 0
        host_total = 0
        alternatives = 0
        for fragment in frags:
            options = []
            for world in GRAMMARS:
                checks += 1
                piece = render(fragment, world)
                try:
                    readable = parse(piece, host) == fragment
                except ValueError:
                    readable = False
                if readable:
                    options.append((fragment_cost(fragment, world), world.id))
            floor = min(cost for cost, _ in options)
            native = fragment_cost(fragment, host)
            readable_total += floor
            host_total += native
            alternatives += len({world for _, world in options})
            if floor < native:
                cheaper.append(
                    {
                        "host": host.id,
                        "fragment": render(fragment, CONTROL),
                        "host_cost": native,
                        "readable_floor": floor,
                    }
                )
        per_host[host.id] = {
            "readable_interior": readable_total,
            "native_interior": host_total,
            "gain": host_total - readable_total,
            "mean_readable_worlds": alternatives / len(frags) if frags else 0.0,
        }
    return {
        "fragments": len(frags),
        "hosts": len(GRAMMARS),
        "checks": checks,
        "cheaper_readable_alternatives": len(cheaper),
        "counterexamples": tuple(cheaper),
        "per_host": per_host,
        "total_gain": sum(entry["gain"] for entry in per_host.values()),
        "holds": not cheaper,
    }


def naming_break_even(
    corpus: Sequence[Composite] | None = None,
    objectives: Sequence[str] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """At what price per named intermediate does Model II stop winning?

    The naming unit is a modelling choice, so its consequence is measured rather than argued.  The
    break-even rate is ``(baseline - interior - skeleton) / names``: below it Model II is cheaper
    than one global convention, above it dearer.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    objectives = tuple(objectives) if objectives is not None else OBJECTIVES
    grid = corpus_costs(corpus)
    table = verdict_table(corpus, objectives, ("named",), workers, naming_unit_cost=1)
    out = {}
    for objective in objectives:
        subset = [
            row for row in table["rows"] if row["objective"] == objective and row["model"] == "named"
        ]
        names = sum(row["fragment_count"] for row in subset)
        fixed = sum(row["interior_cost"] + row["skeleton_cost"] for row in subset)
        per_object_baseline = sum(row["best_single_cost"] for row in subset)
        entry = {"names": names, "fixed_cost": fixed}
        for label, baseline in (
            ("global", grid["best_total"]),
            ("per_object", per_object_baseline),
        ):
            headroom = baseline - fixed
            entry[label] = {
                "baseline": baseline,
                "headroom": headroom,
                "break_even_rate": headroom / names if names else None,
                "largest_winning_integer_rate": (headroom - 1) // names if names else None,
            }
        out[objective] = entry
    return {"per_objective": out, "baseline_world": grid["best_world"]}


def host_table(
    corpus: Sequence[Composite] | None = None,
    objectives: Sequence[str] | None = None,
    models: Sequence[str] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """How often is ``G0`` the right host world for the recombined document?

    Reported twice, because the tie-break would otherwise do the reporting: once as the world that
    is UNIQUELY optimal, and once as a member of the tied-optimal set.
    """
    table = verdict_table(corpus, objectives, models, workers)
    out = {}
    for key, _ in table["totals"].items():
        objective, model = key.split("/")
        subset = [
            row for row in table["rows"] if row["objective"] == objective and row["model"] == model
        ]
        out[key] = {
            "objects": len(subset),
            "control_chosen": sum(1 for row in subset if row["host"] == CONTROL.id),
            "control_among_optimal": sum(
                1 for row in subset if CONTROL.id in row["optimal_hosts"]
            ),
            "control_uniquely_optimal": sum(
                1 for row in subset if row["optimal_hosts"] == (CONTROL.id,)
            ),
            "all_worlds_tied": sum(1 for row in subset if len(row["optimal_hosts"]) == len(GRAMMARS)),
            "distinct_hosts": len({row["host"] for row in subset}),
        }
    return {"per_case": out, "control": CONTROL.id, "worlds": len(GRAMMARS)}


def seam_profile(
    corpus: Sequence[Composite] | None = None,
    objectives: Sequence[str] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The seam, on its own, never blended into a total.

    For Model I it also splits the two independent reasons a fragment has to be bracketed: the host
    would re-associate it (``precedence``), or the host would misread its interior (``unreadable``).
    The second is the seam an SDK design would not think to budget for.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    objectives = tuple(objectives) if objectives is not None else OBJECTIVES
    out = {}
    for objective in objectives:
        for model in MODELS:
            records = [route(item, objective, model) for item in corpus]
            rows = [row for record in records for row in record["fragments"]]
            out[f"{objective}/{model}"] = {
                "fragments": len(rows),
                "seam_total": sum(record["seam_cost"] for record in records),
                "interior_total": sum(record["interior_cost"] for record in records),
                "skeleton_total": sum(record["skeleton_cost"] for record in records),
                "wraps": sum(1 for row in rows if row["wrap"]),
                "wraps_precedence_only": sum(
                    1 for row in rows if row["wrap_precedence"] and not row["wrap_unreadable"]
                ),
                "wraps_unreadable_only": sum(
                    1 for row in rows if row["wrap_unreadable"] and not row["wrap_precedence"]
                ),
                "wraps_both": sum(
                    1 for row in rows if row["wrap_precedence"] and row["wrap_unreadable"]
                ),
                "documents_host_readable": sum(1 for record in records if record["host_readable"]),
                "documents": len(records),
                "forfeited_by_one_convention": sum(
                    record["forfeited_by_one_convention"] for record in records
                ),
                "fragments_routed_off_control": sum(
                    1 for record in records for world in record["worlds"] if world != CONTROL.id
                ),
            }
    return out


def fragment_table(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Every fragment, its cost floor, and where each objective sends it."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    rows = []
    for item in corpus:
        parts = split(composite_tree(item))
        for index, fragment in enumerate(parts.fragments):
            costs = {grammar.id: fragment_cost(fragment, grammar) for grammar in GRAMMARS}
            rows.append(
                {
                    "composite": item.name,
                    "index": index,
                    "source": render(fragment, CONTROL),
                    "position": parts.positions[index],
                    "control_cost": costs[CONTROL.id],
                    "min_cost": min(costs.values()),
                    "max_cost": max(costs.values()),
                    "free_worlds": sum(1 for value in costs.values() if value == 0),
                    "depth": depth(fragment),
                    "chosen": {
                        objective: best_world(fragment, objective, item.variable).id
                        for objective in OBJECTIVES
                    },
                }
            )
    return {
        "rows": tuple(rows),
        "fragments": len(rows),
        "distinct_sources": len({row["source"] for row in rows}),
        "free_in_control": sum(1 for row in rows if row["control_cost"] == 0),
        "free_in_every_world": sum(1 for row in rows if row["max_cost"] == 0),
        "free_in_some_world": sum(1 for row in rows if row["min_cost"] == 0),
        "interior_floor": sum(row["min_cost"] for row in rows),
        "interior_under_control": sum(row["control_cost"] for row in rows),
    }


# ------------------------------------------------------------------------------------ concurrency
#
# Repository policy is multicore by default and it also says a sequential path is a valid outcome
# when a measurement justifies it.  The two workloads here have profiles two orders of magnitude
# apart -- a bracket cell is string work, a verdict cell is two SymPy ``simplify`` calls -- so the
# decision is taken from measured per-cell seconds and not from a cell count.

#: Cores kept free so a sweep cannot starve the interactive session.
WORKER_HEADROOM_CORES: int = 2

#: An upper bound on the spawn cost one sweep has to amortise.
WORKER_CAP: int = 12

#: What it costs to raise a spawn-start pool whose workers each import this module, and so SymPy.
#:
#: **Measured on this machine, not carried over from another experiment.**
#: :func:`measure_pool_startup` records ``1.75`` s on 16 cores with 12 workers, minimum of three,
#: and this constant rounds it UP so that :func:`should_parallelise` is never optimistic about the
#: overhead it has to amortise.  0037 declares ``1.2`` s for the same quantity and that figure is not
#: reused: this module's import graph is larger.
POOL_STARTUP_SECONDS: float = 1.8

#: Measured seconds per cell, and the reason the two workloads take opposite decisions.
#:
#: A verdict cell routes one composite and then canonicalises the routed and the single-world tree --
#: two SymPy ``simplify`` calls.  A bracket cell renders one fragment under all 25 worlds in pure
#: Python.  They differ by nearly two orders of magnitude, which is exactly why a cell COUNT cannot
#: decide this.  Recorded run: ``1.21`` s for 38 verdict cells (``3.2e-2`` s each) and ``0.037`` s
#: for 87 bracket cells (``4.3e-4`` s each).
VERDICT_CELL_SECONDS: float = 3.2e-02
BRACKET_CELL_SECONDS: float = 4.3e-04


def worker_count_for(cores: int, cell_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``cell_count`` independent cells."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(cell_count, 1)))


def default_worker_count(cell_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, cell_count)


def should_parallelise(cell_count: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising for this much work, from measured costs."""
    if workers <= 1 or cell_count <= 1:
        return False
    sequential = cell_count * seconds_per_cell
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_cells(
    task: Any, payloads: Sequence[Any], workers: int | None, seconds_per_cell: float
) -> list[Any]:
    """Run one independent cell per payload, across processes when the measurement says to.

    Every cell is a pure function of its payload and the cells share no state, so the two paths
    return identical records; the test suite asserts that rather than assuming it.
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
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy."""
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


def measure_cell_seconds(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Time one cell of each workload, so the routing constants above are evidence and not a guess."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    payloads = [(item, "brackets", "inline", NAMING_UNIT_COST) for item in corpus]
    start = time.perf_counter()
    for payload in payloads:
        _verdict_cell(payload)
    verdict_elapsed = time.perf_counter() - start

    frags = [fragment for item in corpus for fragment in split(composite_tree(item)).fragments]
    start = time.perf_counter()
    for fragment in frags:
        world_scores(fragment, "brackets")
    bracket_elapsed = time.perf_counter() - start
    return {
        "verdict_cells": len(payloads),
        "verdict_seconds": verdict_elapsed,
        "verdict_seconds_per_cell": verdict_elapsed / len(payloads) if payloads else 0.0,
        "bracket_cells": len(frags),
        "bracket_seconds": bracket_elapsed,
        "bracket_seconds_per_cell": bracket_elapsed / len(frags) if frags else 0.0,
        "declared_verdict_seconds_per_cell": VERDICT_CELL_SECONDS,
        "declared_bracket_seconds_per_cell": BRACKET_CELL_SECONDS,
    }


def parallel_decision(corpus: Sequence[Composite] | None = None) -> dict[str, Any]:
    """Time both paths of the verdict sweep and check they agree, then record which one won."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    cells = len(corpus) * len(OBJECTIVES) * len(MODELS)
    workers = default_worker_count(cells)

    start = time.perf_counter()
    sequential = verdict_table(corpus, workers=1)
    sequential_seconds = time.perf_counter() - start

    start = time.perf_counter()
    parallel = verdict_table(corpus, workers=workers)
    parallel_seconds = time.perf_counter() - start

    return {
        "cores": os.cpu_count(),
        "cells": cells,
        "workers": workers,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": sequential_seconds / parallel_seconds if parallel_seconds else None,
        "faster": "parallel" if parallel_seconds < sequential_seconds else "sequential",
        "records_identical": sequential["rows"] == parallel["rows"],
        "default_decision": "parallel"
        if should_parallelise(cells, VERDICT_CELL_SECONDS, workers)
        else "sequential",
    }


# --------------------------------------------------------------------------------------- report


def fragment_routing_report(
    corpus: Sequence[Composite] | None = None,
    workers: int | None = None,
    timing: bool = False,
) -> dict[str, Any]:
    """The whole experiment as one structure: bridge, split, objectives, seam, verdict, oracle."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    report = {
        "corpus": corpus_audit(corpus),
        "round_trip": round_trip_audit(corpus),
        "minimality": minimality_audit(corpus),
        "fragments": fragment_table(corpus),
        "decomposition": decomposition_table(corpus),
        "objectives": objective_agreement(corpus),
        "depth": depth_discrimination(corpus),
        "visibility_regimes": visibility_regime_audit(corpus),
        "verdict": verdict_table(corpus, workers=workers),
        "global_host": global_host_verdict(corpus),
        "seam": seam_profile(corpus),
        "readable": readable_routing_audit(corpus),
        "hosts": host_table(corpus, workers=workers),
        "oracle": oracle_bound(corpus),
        "naming": naming_break_even(corpus, workers=workers),
    }
    if timing:
        report["parallel_decision"] = parallel_decision(corpus)
        report["cell_seconds"] = measure_cell_seconds(corpus)
        report["pool_startup"] = measure_pool_startup()
    return report
