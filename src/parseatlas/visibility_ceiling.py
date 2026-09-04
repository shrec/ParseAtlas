"""Experiment 0039: what it would take to see the 46 invisible (object, property) pairs.

Experiment 0038 measured, over 34 objects and seven properties, that 140 (object, property) pairs
are TRUE, that the best single world makes 77 of them manifest, that all 25 worlds together make
94, and that **46 are true but manifest in no world at all**.  This module asks what each of the
three plausible causes of that 46 is actually worth, and it keeps the three apart:

``search space``
    A world writes an object as one tree - the control parse of the writing it finds cheapest - and
    experiment 0023 showed that precedence reaches at most 24 trees while ``92.159 %`` of
    ``(word, tree)`` pairs are unreachable.  So the tree that would expose a property may simply be
    outside anything a precedence rule can write.  **Part 1** enumerates the whole parenthesization
    space of every declared writing, keeps the trees that still denote the same object, and applies
    the SAME imported shape rules.  This part is a measurement end to end.

``language``
    Generation 1 has only binary ``+ - * /`` and brackets.  It has no exponentiation, no radical and
    no function application, so a property whose written form needs one of those has no rendering in
    ANY world under ANY parenthesization.  **Part 2** is an ACCOUNTING OF REQUIREMENTS, not a
    measurement of a rendering: it decides, algebraically, what the missing written form would need,
    and counts the requirements.  Nothing in Part 2 claims a recovered visibility.

``rules``
    What is left after the first two is neither a limit of the search space nor of the language.  It
    is either a place where the declared shape rule asks for more than the truth rule does, or a
    place where the exposing form exists in Generation 1 but needs a token sequence no declared
    writing supplies.  **Part 3** enumerates that residue pair by pair and says which it is; where a
    Generation-1 form exists, the form is written out, rendered and checked, so the claim is a
    measurement and not an assertion.

What is imported and never restated
-----------------------------------

The manifestness rules are :data:`parseatlas.manifest_properties.PROPERTIES` and the decision is
:func:`parseatlas.manifest_properties.manifest_set`, imported here by reference.  No rule is copied,
relaxed or added; :func:`rule_identity` asserts the identity so a future edit cannot quietly fork
them.  The corpus is 0038's corpus, imported whole.  The enumeration is
:func:`parseatlas.ast_space.enumerate_parenthesizations` and the reachability decision is
:func:`parseatlas.reachability.strict_reachable`, both imported.

The one thing this module adds is a filter that 0038 did not need: **a parenthesization of a token
word is usually a different object**.  ``a - (b + c)`` is not ``a - b + c``.  A tree that exposes a
property but denotes something else has recovered nothing, so every tree in the space is tested for
identity with the object before it is allowed to contribute to a ceiling.  The test is exact: the
tree is evaluated with exact rational arithmetic at two declared probe points, which can only rule a
tree OUT (a point where two expressions differ is a proof that they differ), and every survivor is
then confirmed with SymPy.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from random import Random
from typing import Any

from sympy import I, Mul, Poly, Pow, Symbol, cancel, expand, factor, fraction, together
from sympy import roots as sympy_roots

from .ast_space import enumerate_parenthesizations
from .canonical import to_sympy
from .manifest_properties import (
    CONTROL,
    CORPUS,
    GRAMMARS,
    OBJECT_BY_NAME,
    PROPERTIES,
    PROPERTY_NAMES,
    MathObject,
    Writing,
    ground_truth,
    manifest_set,
    object_tree,
    visibility_table,
)
from .notational_cost import render
from .parser import Binary, Node, Number, Variable, parse
from .reachability import strict_reachable

__all__ = [
    "CONTROL",
    "CORPUS",
    "GRAMMARS",
    "OPERATOR_SET",
    "POOL_STARTUP_SECONDS",
    "PROBE_SEED",
    "PROPERTIES",
    "PROPERTY_NAMES",
    "REQUIREMENTS",
    "RESIDUE_CAUSES",
    "RULE_LIMIT_REASONS",
    "TREE_SECONDS",
    "WITNESSES",
    "Witness",
    "baseline",
    "ceiling_table",
    "default_worker_count",
    "evaluate",
    "factor_requirement",
    "flat_source",
    "grammar_independence",
    "ground_truth",
    "in_order",
    "language_accounting",
    "leaf_text",
    "manifest_set",
    "measure_pool_startup",
    "object_tree",
    "parallel_decision",
    "placeholder_leaves",
    "probe_values",
    "rebuild",
    "residue_report",
    "roots_requirement",
    "rule_identity",
    "same_object",
    "should_parallelise",
    "soundness_sweep",
    "space_size",
    "to_form",
    "visibility_ceiling_report",
    "witness_audit",
    "worker_count_for",
    "writing_space",
    "zero_bracket_readings",
]

#: Generation 1's whole vocabulary of operators.  Everything Part 2 calls "missing" is missing from
#: exactly this list, and the list is stated so the bound is checkable rather than asserted.
OPERATOR_SET: tuple[str, ...] = ("+", "-", "*", "/")

#: Seed of the declared probe points.  The points are pseudo-random so that no assignment was chosen
#: after seeing a result, and the seed is fixed so the filter is reproducible.
PROBE_SEED: int = 39


Form = str | tuple[str, Any, Any]


# --------------------------------------------------------------------------------- tree plumbing


def in_order(node: Node) -> tuple[tuple[Node, ...], tuple[str, ...]]:
    """The leaf sequence and the operator sequence of a tree, left to right.

    This is the token word the tree is one parenthesization of; the whole parenthesization space is
    the set of trees over exactly this pair.
    """
    if not isinstance(node, Binary):
        return (node,), ()
    left_leaves, left_operators = in_order(node.left)
    right_leaves, right_operators = in_order(node.right)
    return (
        left_leaves + right_leaves,
        left_operators + (node.operator,) + right_operators,
    )


def placeholder_leaves(count: int) -> tuple[str, ...]:
    """Positional leaf names, so the enumeration is over positions and not over repeated tokens.

    ``(x - h) * (x - h)`` writes ``x`` twice; the two occurrences are different leaves of the word
    and must stay distinguishable, which ``enumerate_parenthesizations`` guarantees only if the leaf
    names are distinct.
    """
    return tuple(f"L{index}" for index in range(count))


def to_form(node: Node) -> Form:
    """The tree as an enumeration form over positional leaf names."""
    counter = [0]

    def walk(inner: Node) -> Form:
        if not isinstance(inner, Binary):
            name = f"L{counter[0]}"
            counter[0] += 1
            return name
        left = walk(inner.left)
        right = walk(inner.right)
        return (inner.operator, left, right)

    return walk(node)


def rebuild(form: Form, leaves: Sequence[Node]) -> Node:
    """Turn an enumeration form back into a parser tree over the word's own leaves."""
    if isinstance(form, str):
        return leaves[int(form[1:])]
    return Binary(form[0], rebuild(form[1], leaves), rebuild(form[2], leaves))


def leaf_text(leaf: Node) -> str:
    """The token text of a leaf, in the tokenizer's own spelling."""
    if isinstance(leaf, Number):
        value = leaf.value
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"
    if isinstance(leaf, Variable):
        return leaf.name
    raise TypeError(f"not a leaf: {leaf!r}")


def flat_source(leaves: Sequence[Node], operators: Sequence[str]) -> str:
    """The bracket-free source of the word, which is what a world would actually be handed."""
    parts = [leaf_text(leaves[0])]
    for operator, leaf in zip(operators, leaves[1:]):
        parts += [operator, leaf_text(leaf)]
    return " ".join(parts)


def writing_space(writing: Writing) -> tuple[tuple[Node, ...], tuple[str, ...], tuple[Form, ...]]:
    """The full parenthesization space of one declared writing.

    No bound is applied.  The largest word in the corpus has 13 operators and therefore ``742900``
    trees, and the enumeration of the whole corpus is reported in
    :func:`visibility_ceiling_report` so the reader sees what the extension costs.
    """
    leaves, operators = in_order(object_tree(writing))
    forms = enumerate_parenthesizations(placeholder_leaves(len(leaves)), operators)
    return leaves, operators, forms


def space_size(item: MathObject) -> dict[str, int]:
    """Catalan size of each declared writing's parenthesization space."""
    sizes = {}
    for writing in item.writings:
        leaves, operators = in_order(object_tree(writing))
        sizes[writing.role] = len(
            enumerate_parenthesizations(placeholder_leaves(len(leaves)), operators)
        )
    return sizes


# ------------------------------------------------------------------------------ object identity
#
# A parenthesization of a fixed token word is a DIFFERENT OBJECT in general, and a tree that exposes
# a property of something else has recovered nothing.  The filter below is exact in the only
# direction that matters: exact rational arithmetic at a point where two expressions disagree is a
# proof that they disagree, so the probe can only ever discard a tree wrongly if the evaluation was
# undefined there - and that case is detected and escalated to SymPy rather than guessed.


def probe_values(leaves: Sequence[Node], point: int) -> dict[str, Fraction]:
    """Exact rational values for the word's leaves at one declared probe point.

    Numerals keep their own value; each distinct variable name gets one pseudo-random rational drawn
    from :data:`PROBE_SEED`, so no assignment was picked after seeing a result.
    """
    generator = Random(PROBE_SEED * 1000 + point)
    assigned: dict[str, Fraction] = {}
    values: dict[str, Fraction] = {}
    for index, leaf in enumerate(leaves):
        name = f"L{index}"
        if isinstance(leaf, Number):
            values[name] = Fraction(leaf.value)
            continue
        if not isinstance(leaf, Variable):  # pragma: no cover - guarded by leaf_text
            raise TypeError(f"not a leaf: {leaf!r}")
        if leaf.name not in assigned:
            while True:
                candidate = Fraction(generator.randint(11, 997), generator.randint(3, 97))
                if candidate not in assigned.values():
                    break
            assigned[leaf.name] = candidate
        values[name] = assigned[leaf.name]
    return values


def evaluate(form: Form, values: dict[str, Fraction]) -> Fraction | None:
    """Exact value of a form at a probe point, or ``None`` where it is undefined."""
    if isinstance(form, str):
        return values[form]
    left = evaluate(form[1], values)
    if left is None:
        return None
    right = evaluate(form[2], values)
    if right is None:
        return None
    operator = form[0]
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if right == 0:
        return None
    return left / right


def same_object(node: Node, reference: Any) -> bool:
    """Whether a tree denotes the object, decided by SymPy and not by the probe."""
    difference = cancel(together(to_sympy(node) - reference))
    return bool(expand(difference) == 0)


# ------------------------------------------------------------------------------------- the scan


def _same_object_forms(payload: tuple[str, int, int, int]) -> tuple[str, int, int, tuple[Form, ...]]:
    """One chunk of one writing's space: which forms survive the exact probe.

    Module level on purpose - a spawn-start pool can only pickle top-level functions.  The chunk
    returns candidates only; SymPy confirmation happens once, in the parent, on the survivors.
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
#: without making the result payload large.
CHUNK_TREES: int = 4000

#: Cores kept free so a sweep cannot starve the interactive session (0038's policy, unchanged).
WORKER_HEADROOM_CORES: int = 2

#: Upper bound on the spawn cost any one sweep has to amortise (0038's policy, unchanged).
WORKER_CAP: int = 12

#: Measured cost of raising a spawn-start pool whose workers each import this module, and so SymPy.
#:
#: **Measured here, not inherited.**  :func:`measure_pool_startup` raises a pool of the default
#: worker count and runs one trivial chunk in each; the recorded run on 16 cores with 12 workers is
#: ``1.27`` s, minimum of three, and this constant rounds it up.
POOL_STARTUP_SECONDS: float = 1.3

#: Measured seconds to probe one tree of the space: two exact rational evaluations of a word of up
#: to 13 operators.  Recorded run: ``1510820`` trees in ``23.98`` s sequential, minimum path, i.e.
#: ``1.587e-5`` s each; this constant rounds it up.  See :func:`parallel_decision`.
TREE_SECONDS: float = 1.6e-05


def worker_count_for(cores: int, chunk_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``chunk_count`` independent chunks."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(chunk_count, 1)))


def default_worker_count(chunk_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, chunk_count)


def should_parallelise(tree_count: int, seconds_per_tree: float, workers: int) -> bool:
    """Whether a pool is worth raising, from the measured per-tree cost and the measured spawn cost."""
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
) -> list[tuple[str, int, int, tuple[Form, ...]]]:
    """Probe every chunk, across processes when the measurement says a pool pays for itself."""
    tree_count = sum(high - low for _n, _i, low, high in payloads)
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(tree_count, TREE_SECONDS, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [_same_object_forms(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(_same_object_forms, payloads, chunksize=1))


def baseline(opaque: bool = False) -> dict[str, Any]:
    """Experiment 0038's numbers, recomputed from 0038's own table and not copied from its report."""
    table = visibility_table(opaque=opaque)
    per_world = {
        grammar.id: sum(
            len([name for name in row["per_grammar"][grammar.id]["manifest"] if name in row["truth"]])
            for row in table["rows"]
        )
        for grammar in GRAMMARS
    }
    best_id = max(per_world, key=lambda gid: (per_world[gid], gid == CONTROL.id))
    return {
        "regime": table["regime"],
        "objects": table["objects"],
        "grammars": table["grammars"],
        "true_pairs": sum(len(row["truth"]) for row in table["rows"]),
        "best_single_world": per_world[best_id],
        "best_single_world_ids": tuple(
            gid for gid, total in per_world.items() if total == per_world[best_id]
        ),
        "manifest_somewhere": sum(
            len([name for name in row["manifest_somewhere"] if name in row["truth"]])
            for row in table["rows"]
        ),
        "hidden_pairs": table["hidden_pairs"],
        "hidden_pair_count": table["hidden_pair_count"],
        "hidden_by_property": table["hidden_by_property"],
        "table": table,
    }


def ceiling_table(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The ceiling of the FULL parenthesization space, per object and in total.

    For every declared writing of every object, every tree over its token word is enumerated; the
    trees that still denote the object are kept; and the imported shape rules are applied to each.
    ``ceiling_manifest`` is the union over all of them - the most any reader could see if the choice
    of tree were free instead of precedence-shaped.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    reference = baseline()
    rows_by_name = {row["object"]: row for row in reference["table"]["rows"]}

    payloads = _chunks(corpus)
    chunk_results = _map_chunks(payloads, workers)
    candidates: dict[tuple[str, int], list[Form]] = {}
    probed = 0
    for name, index, count, forms in chunk_results:
        probed += count
        candidates.setdefault((name, index), []).extend(forms)

    rows = []
    violations: list[dict[str, Any]] = []
    confirmed_total = 0
    candidate_total = 0
    reachable_total = 0
    for item in corpus:
        truth = set(rows_by_name[item.name]["truth"])
        somewhere = set(rows_by_name[item.name]["manifest_somewhere"])
        ceiling: set[str] = set()
        per_writing = []
        same_total = 0
        records: list[dict[str, Any]] = []
        for index, writing in enumerate(item.writings):
            leaves, operators, forms = writing_space(writing)
            expression = to_sympy(object_tree(writing))
            source = flat_source(leaves, operators)
            declared = to_form(object_tree(writing))
            registry: dict[Form, list[str]] = {}
            for grammar in GRAMMARS:
                registry.setdefault(to_form(parse(source, grammar)), []).append(grammar.id)
            kept = []
            for form in candidates.get((item.name, index), ()):
                candidate_total += 1
                node = rebuild(form, leaves)
                if not same_object(node, expression):
                    continue
                kept.append((form, node))
            confirmed_total += len(kept)
            same_total += len(kept)
            reachable_here = sum(
                1
                for form, _node in kept
                if form in registry or strict_reachable(form, operators)
            )
            reachable_total += reachable_here
            for form, node in kept:
                found = manifest_set(node, CONTROL, item.variable)
                untrue = [name for name in found if name not in truth]
                if untrue:
                    violations.append(
                        {
                            "object": item.name,
                            "role": writing.role,
                            "form": form,
                            "text": render(node, CONTROL),
                            "claimed": tuple(untrue),
                        }
                    )
                ceiling |= set(found)
                records.append(
                    {
                        "role": writing.role,
                        "form": form,
                        "text": render(node, CONTROL),
                        "flat_source": source,
                        "manifest": found,
                        "strict_reachable": strict_reachable(form, operators),
                        "registry_grammars": tuple(registry.get(form, ())),
                        "is_declared_tree": form == declared,
                    }
                )
            per_writing.append(
                {
                    "role": writing.role,
                    "source": writing.source,
                    "operators": len(operators),
                    "space": len(forms),
                    "probe_survivors": len(candidates.get((item.name, index), ())),
                    "same_object_trees": len(kept),
                    "same_object_forms": tuple(form for form, _node in kept),
                    "precedence_reachable_same_object_trees": reachable_here,
                    "flat_source": source,
                }
            )
        recovered = tuple(
            name
            for name in PROPERTY_NAMES
            if name in truth and name in ceiling and name not in somewhere
        )
        exposing = {name: _exposure(name, records) for name in recovered}
        rows.append(
            {
                "object": item.name,
                "variable": item.variable,
                "truth": rows_by_name[item.name]["truth"],
                "manifest_somewhere": rows_by_name[item.name]["manifest_somewhere"],
                "ceiling_manifest": tuple(n for n in PROPERTY_NAMES if n in ceiling),
                "recovered": recovered,
                "still_hidden": tuple(
                    name
                    for name in PROPERTY_NAMES
                    if name in truth and name not in ceiling
                ),
                "exposing": exposing,
                "writings": tuple(per_writing),
                "space_total": sum(entry["space"] for entry in per_writing),
                "same_object_trees": same_total,
            }
        )

    recovered_pairs = tuple(
        (row["object"], name) for row in rows for name in row["recovered"]
    )
    still_hidden = tuple(
        (row["object"], name) for row in rows for name in row["still_hidden"]
    )
    reachable_recoveries = tuple(
        pair
        for pair in recovered_pairs
        if _row(rows, pair[0])["exposing"][pair[1]]["precedence_reachable"]
    )
    return {
        "objects": len(corpus),
        "space_total": sum(row["space_total"] for row in rows),
        "trees_probed": probed,
        "probe_survivors": candidate_total,
        "same_object_trees": confirmed_total,
        "precedence_reachable_same_object_trees": reachable_total,
        "ceiling_pairs": sum(
            len([n for n in row["ceiling_manifest"] if n in row["truth"]]) for row in rows
        ),
        "objects_with_nothing_manifest": tuple(
            row["object"] for row in rows if not row["ceiling_manifest"]
        ),
        "objects_gaining": tuple(row["object"] for row in rows if row["recovered"]),
        "rows": tuple(rows),
        "baseline": {
            key: value for key, value in reference.items() if key != "table"
        },
        "recovered_pairs": recovered_pairs,
        "recovered_count": len(recovered_pairs),
        "recovered_by_property": {
            name: sum(1 for _o, p in recovered_pairs if p == name) for name in PROPERTY_NAMES
        },
        "still_hidden_pairs": still_hidden,
        "still_hidden_count": len(still_hidden),
        "still_hidden_by_property": {
            name: sum(1 for _o, p in still_hidden if p == name) for name in PROPERTY_NAMES
        },
        "precedence_reachable_recoveries": reachable_recoveries,
        "soundness_violations": tuple(violations),
        "soundness_violation_count": len(violations),
    }


def _row(rows: Sequence[dict[str, Any]], name: str) -> dict[str, Any]:
    for row in rows:
        if row["object"] == name:
            return row
    raise KeyError(name)  # pragma: no cover


def zero_bracket_readings(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
    table: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The DEFECT this card asked to be looked for, measured rather than argued.

    Experiment 0038 fixes one tree per writing - the control parse of the source string - and lets
    the world change only the brackets.  It therefore never asks the question its own transparent
    regime implies: *is there a bracket-free string that this world reads as this object?*  When
    there is, that world writes the object with no brackets at all and reads whatever tree its own
    precedence gives it, which may not be the tree 0038 gave it.

    This function sweeps every (object, world) cell for exactly that: the world's own parse of the
    declared writing's bracket-free word, kept only when it still denotes the object.  It reports
    which cells differ from 0038's tree and which (object, property) pairs the difference adds.  The
    answer is small, and it is reported whatever its size.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = table if table is not None else ceiling_table(corpus, workers=workers)
    cells = []
    added: set[tuple[str, str]] = set()
    for row in table["rows"]:
        item = OBJECT_BY_NAME[row["object"]]
        truth = set(row["truth"])
        somewhere = set(row["manifest_somewhere"])
        for index, entry in enumerate(row["writings"]):
            writing = item.writings[index]
            leaves, _operators, _forms = writing_space(writing)
            declared = to_form(object_tree(writing))
            same = set(entry["same_object_forms"])
            for grammar in GRAMMARS:
                form = to_form(parse(entry["flat_source"], grammar))
                if form not in same:
                    continue
                node = rebuild(form, leaves)
                found = manifest_set(node, CONTROL, item.variable)
                gained = tuple(
                    name for name in found if name in truth and name not in somewhere
                )
                cells.append(
                    {
                        "object": item.name,
                        "grammar": grammar.id,
                        "role": writing.role,
                        "flat_source": entry["flat_source"],
                        "text": render(node, CONTROL),
                        "is_declared_tree": form == declared,
                        "manifest": found,
                        "gained": gained,
                    }
                )
                for name in gained:
                    added.add((item.name, name))
    differing = tuple(cell for cell in cells if not cell["is_declared_tree"])
    return {
        "cells_with_a_zero_bracket_reading": len(cells),
        "cells_reading_a_different_tree": len(differing),
        "differing_cells": differing,
        "added_pairs": tuple(sorted(added)),
        "added_pair_count": len(added),
    }


def _exposure(name: str, records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Every tree that shows a recovered property, and whether any precedence rule could write it.

    ALL exposing trees are collected, not the first one found.  The distinction decides the card's
    second question, and taking the first tree would have answered it wrongly: one recovered
    property here is exposed by three different trees, only one of which is precedence-reachable.
    """
    exposing = tuple(record for record in records if name in record["manifest"])
    reachable = tuple(
        record
        for record in exposing
        if record["strict_reachable"] or record["registry_grammars"]
    )
    return {
        "trees": exposing,
        "tree_count": len(exposing),
        "precedence_reachable": bool(reachable),
        "reachable_trees": reachable,
        "reachable_grammars": tuple(
            sorted({gid for record in reachable for gid in record["registry_grammars"]})
        ),
    }


# ------------------------------------------------------------------------------------- controls


def rule_identity() -> dict[str, Any]:
    """Assert that the rules used here ARE 0038's objects, not copies of them."""
    from . import manifest_properties as origin

    return {
        "properties_identical": PROPERTIES is origin.PROPERTIES,
        "manifest_set_identical": manifest_set is origin.manifest_set,
        "ground_truth_identical": ground_truth is origin.ground_truth,
        "corpus_identical": CORPUS is origin.CORPUS,
        "shape_rules_identical": all(
            item.shape is origin.PROPERTY_BY_NAME[item.name].shape for item in PROPERTIES
        ),
        "property_names": PROPERTY_NAMES,
    }


def soundness_sweep(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
    table: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """``manifest => true`` over the full parenthesization space.

    Every tree of the space that still denotes the object is a written form of that object, so every
    property it makes manifest must be one the object actually has.  The sweep counts the claims -
    one per (tree, property) the imported rules fire on - and the violations; the violation count
    must be zero.
    """
    table = table if table is not None else ceiling_table(corpus, workers=workers)
    corpus = tuple(corpus) if corpus is not None else CORPUS
    claims = 0
    trees = 0
    for row in table["rows"]:
        item = OBJECT_BY_NAME[row["object"]]
        for index, entry in enumerate(row["writings"]):
            leaves, _operators, _forms = writing_space(item.writings[index])
            for form in entry["same_object_forms"]:
                trees += 1
                claims += len(manifest_set(rebuild(form, leaves), CONTROL, item.variable))
    return {
        "same_object_trees": trees,
        "objects": table["objects"],
        "claims": claims,
        "violations": table["soundness_violations"],
        "violation_count": table["soundness_violation_count"],
    }


def grammar_independence(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
    table: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check that under the transparent regime the manifest set of a TREE does not depend on the world.

    0038's module docstring states this; the ceiling rests on it, because a ceiling computed under
    one grammar would otherwise be a ceiling for that grammar only.  Here it is checked on every
    same-object tree of the full space, against all 25 worlds.
    """
    table = table if table is not None else ceiling_table(corpus, workers=workers)
    checked = 0
    disagreements = []
    for row in table["rows"]:
        item = OBJECT_BY_NAME[row["object"]]
        for index, entry in enumerate(row["writings"]):
            leaves, _operators, _forms = writing_space(item.writings[index])
            for form in entry["same_object_forms"]:
                node = rebuild(form, leaves)
                sets = {
                    grammar.id: manifest_set(node, grammar, item.variable) for grammar in GRAMMARS
                }
                checked += len(sets)
                if len(set(sets.values())) != 1:
                    disagreements.append({"object": item.name, "form": form, "sets": sets})
    return {
        "checks": checked,
        "disagreements": tuple(disagreements),
        "disagreement_count": len(disagreements),
    }


# ------------------------------------------------------------------- Part 2: the language bound
#
# READ THIS BEFORE READING A NUMBER FROM THIS SECTION.  Nothing here renders anything.  These
# functions decide, algebraically, what a written form that satisfied the shape rule WOULD have to
# contain, and then report which of those things Generation 1 does not have.  A requirement is not a
# recovered visibility and is never counted as one.

#: The requirements a missing written form can carry.  ``none`` means Generation 1 already suffices
#: and the obstruction is elsewhere.
REQUIREMENTS: tuple[str, ...] = (
    "none",
    "imaginary_unit",
    "radical",
    "no_closed_form",
    "not_applicable",
)


def _numerator_polynomial(expression: Any, symbol: Symbol) -> Any:
    numerator, _denominator = fraction(cancel(together(expression)))
    return Poly(numerator, symbol)


def roots_requirement(item: MathObject) -> dict[str, Any]:
    """What a written form exposing ``roots`` would need beyond ``+ - * /``.

    The shape rule wants a product of factors each at most linear in the principal variable.  Such a
    written form exists in Generation 1 exactly when the object's numerator splits into factors of
    degree at most one over the rational function field of the remaining symbols.  When it does not,
    the roots themselves say what is missing.
    """
    if item.variable is None:
        return {"requirement": "not_applicable", "degrees": (), "roots": ()}
    symbol = Symbol(item.variable, real=True)
    expression = to_sympy(object_tree(item.writings[0]))
    polynomial = _numerator_polynomial(expression, symbol)
    _coefficient, factors = polynomial.factor_list()
    degrees = tuple(sorted(piece.degree() for piece, _power in factors))
    if all(degree <= 1 for degree in degrees):
        return {"requirement": "none", "degrees": degrees, "roots": ()}
    found = sympy_roots(polynomial)
    needs: set[str] = set()
    for root in found:
        if root.has(I):
            needs.add("imaginary_unit")
        for piece in root.atoms(Pow):
            if piece.exp.is_Rational and not piece.exp.is_Integer:
                needs.add("radical")
    if sum(found.values()) < polynomial.degree():
        needs.add("no_closed_form")
    requirement = (
        "no_closed_form"
        if "no_closed_form" in needs
        else "imaginary_unit"
        if "imaginary_unit" in needs
        else "radical"
        if "radical" in needs
        else "none"
    )
    return {
        "requirement": requirement,
        "requirements": tuple(sorted(needs)),
        "degrees": degrees,
        "roots": tuple(str(root) for root in sorted(found, key=str)),
    }


def _compound_numerator_factors(expression: Any) -> int:
    """Non-constant, non-symbol numerator factors of the object, counted with multiplicity."""
    numerator, _denominator = fraction(cancel(together(expression)))
    total = 0
    for piece in Mul.make_args(factor(numerator)):
        base, exponent = piece.as_base_exp()
        if base.is_number or base.is_Symbol:
            continue
        total += abs(int(exponent)) if exponent.is_Integer else 1
    return total


def factor_requirement(item: MathObject) -> dict[str, Any]:
    """What a written form exposing ``factor_structure`` would need beyond ``+ - * /``.

    The shape rule wants at least two compound numerator factors.  Over the rationals the object may
    have fewer; the question this answers is whether extending the constants would produce them.
    """
    expression = to_sympy(object_tree(item.writings[0]))
    rational = _compound_numerator_factors(expression)
    if rational >= 2:
        return {"requirement": "none", "compound_factors": rational, "extended": rational}
    numerator, _denominator = fraction(cancel(together(expression)))
    extended_expression = factor(numerator, extension=[I])
    extended = 0
    for piece in Mul.make_args(extended_expression):
        base, exponent = piece.as_base_exp()
        if base.is_number or base.is_Symbol:
            continue
        extended += abs(int(exponent)) if exponent.is_Integer else 1
    if extended >= 2:
        return {
            "requirement": "imaginary_unit",
            "compound_factors": rational,
            "extended": extended,
        }
    return {"requirement": "none", "compound_factors": rational, "extended": extended}


def language_accounting(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
    table: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Part 2: for every pair still hidden after Part 1, what the missing form would require.

    **This is an accounting of requirements, not a measurement of a rendering.**  A pair whose
    requirement is anything but ``none`` has no written form in this operator set at all, so no
    parenthesization and no world could ever expose it; a pair whose requirement is ``none`` has a
    Generation-1 written form and is therefore Part 3's business, not Part 2's.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = table if table is not None else ceiling_table(corpus, workers=workers)
    entries = []
    for name, prop in table["still_hidden_pairs"]:
        item = OBJECT_BY_NAME[name]
        if prop == "roots":
            verdict = roots_requirement(item)
        elif prop == "factor_structure":
            verdict = factor_requirement(item)
        else:
            verdict = {"requirement": "none"}
        entries.append(
            {
                "object": name,
                "property": prop,
                "requirement": verdict["requirement"],
                "detail": verdict,
            }
        )
    blocked = tuple(entry for entry in entries if entry["requirement"] != "none")
    return {
        "analysis_only": True,
        "note": "requirements, not renderings: nothing in this section claims a visible property",
        "operator_set": OPERATOR_SET,
        "entries": tuple(entries),
        "blocked_pairs": tuple((entry["object"], entry["property"]) for entry in blocked),
        "blocked_count": len(blocked),
        "by_requirement": {
            requirement: tuple(
                (entry["object"], entry["property"])
                for entry in entries
                if entry["requirement"] == requirement
            )
            for requirement in REQUIREMENTS
        },
        "blocked_objects": tuple(sorted({entry["object"] for entry in blocked})),
        "blocked_object_count": len({entry["object"] for entry in blocked}),
    }


# ------------------------------------------------------------------------- Part 3: the residue


@dataclass(frozen=True)
class Witness:
    """A Generation-1 written form OUTSIDE the declared corpus that exposes a residue pair.

    A witness is rendered and checked, never asserted: :func:`witness_audit` confirms that it is the
    same object and that the imported shape rule really does fire on it.  Witnesses do NOT count
    towards the Part 1 recovery number - they are the evidence that a residue pair is blocked by the
    corpus's choice of token word rather than by the operator set or by the rules.
    """

    object: str
    property: str
    source: str
    note: str


#: The residue causes, declared before the pairs are sorted into them.
RESIDUE_CAUSES: tuple[str, ...] = ("different_word", "rule_limit")


#: One witness per residue pair for which a Generation-1 written form exists.  Each is a token word
#: the corpus does not name; each is rendered and checked in :func:`witness_audit`, and a witness
#: that does not fire is a failure of the witness, never a licence to claim the pair.
WITNESSES: tuple[Witness, ...] = (
    Witness(
        "quadratic",
        "leading_coefficient",
        "a * x * x - a * r * x - a * s * x + a * r * s",
        "the general quadratic with the (r + s) bracket distributed: four written monomials",
    ),
    Witness(
        "quadratic",
        "constant_term",
        "a * x * x - a * r * x - a * s * x + a * r * s",
        "same writing; exactly one summand is free of x, and it is the monomial a * r * s",
    ),
    Witness(
        "quadratic",
        "sign_structure",
        "a * x * x - a * r * x - a * s * x + a * r * s",
        "same writing; four signs on the page and no bracket to expand",
    ),
    Witness(
        "hyperbola",
        "roots",
        "(x - a * y / b) * (x + a * y / b) / (a * a)",
        "a difference of two squares splits over the rationals - this is the pair the ellipse "
        "cannot have, and the difference between the two is the whole of Part 2",
    ),
    Witness(
        "hyperbola",
        "factor_structure",
        "(b * x - a * y) * ((b * x + a * y) / (a * a * b * b))",
        "two compound numerator factors under a multiplicative top",
    ),
    Witness(
        "distance_components",
        "degree",
        "x2 * x2 - 2 * x1 * x2 + x1 * x1 + y2 * y2 - 2 * y1 * y2 + y1 * y1",
        "the expanded writing the corpus does not name: the only object in 0038 that shows nothing "
        "in any world shows three of its five properties as soon as the word changes",
    ),
    Witness(
        "distance_components",
        "leading_coefficient",
        "x2 * x2 - 2 * x1 * x2 + x1 * x1 + y2 * y2 - 2 * y1 * y2 + y1 * y1",
        "same expanded writing; one monomial attains degree two in x2",
    ),
    Witness(
        "distance_components",
        "sign_structure",
        "x2 * x2 - 2 * x1 * x2 + x1 * x1 + y2 * y2 - 2 * y1 * y2 + y1 * y1",
        "same expanded writing; six monomials, six visible signs",
    ),
    Witness(
        "midpoint",
        "leading_coefficient",
        "x1 / 2 + x2 / 2",
        "the split writing, which the corpus does not name",
    ),
    Witness(
        "midpoint",
        "constant_term",
        "x1 / 2 + x2 / 2",
        "same writing; the constant term x2 / 2 is a single monomial",
    ),
    Witness(
        "midpoint",
        "sign_structure",
        "x1 / 2 + x2 / 2",
        "same writing",
    ),
    Witness(
        "taylor_first_term",
        "leading_coefficient",
        "dfa * x - dfa * a",
        "the distributed writing: two monomials in x, one of them alone at degree one",
    ),
    Witness(
        "taylor_first_term",
        "constant_term",
        "dfa * x - dfa * a",
        "same writing; the constant term is the monomial dfa * a",
    ),
    Witness(
        "taylor_first_term",
        "sign_structure",
        "dfa * x - dfa * a",
        "same writing",
    ),
    Witness(
        "taylor_second_term",
        "leading_coefficient",
        "d2fa * x * x / 2 - d2fa * a * x + d2fa * a * a / 2",
        "the expanded second Taylor term: three monomials, one at degree two",
    ),
    Witness(
        "taylor_second_term",
        "constant_term",
        "d2fa * x * x / 2 - d2fa * a * x + d2fa * a * a / 2",
        "same writing; one x-free summand, and it is a monomial",
    ),
    Witness(
        "taylor_second_term",
        "sign_structure",
        "d2fa * x * x / 2 - d2fa * a * x + d2fa * a * a / 2",
        "same writing",
    ),
    Witness(
        "riemann_sum_term",
        "sign_structure",
        "fxi * b / n - fxi * a / n",
        "the split writing: the denominator n is a single token, so each addend stays a monomial - "
        "which is exactly what the slope, whose denominator is (x2 - x1), cannot do",
    ),
)


#: Why a residue pair has no Generation-1 written form at all.  Declared per pair, because a
#: ``rule_limit`` is a claim about EVERY writing of the object and therefore needs a reason that can
#: be checked by reading the imported rule, not a shrug.  Every pair the classifier calls
#: ``rule_limit`` must appear here; :func:`residue_report` reports any that does not.
RULE_LIMIT_REASONS: dict[tuple[str, str], str] = {
    ("distributive_law", "leading_coefficient"): (
        "the coefficient of a is b + c, which is not a written monomial, so no monomial-sum writing "
        "can have a single summand at degree one"
    ),
    ("distributive_law", "factor_structure"): (
        "the factorisation a * (b + c) has one compound factor and one bare symbol; the shape rule "
        "wants two compound factors while the truth rule counts the symbol as a factor"
    ),
    ("line", "constant_term"): (
        "the constant term y1 - m * x1 is a sum of two monomials, and the rule allows at most one "
        "variable-free summand because adding two of them is algebra"
    ),
    ("line", "roots"): (
        "the root x1 - y1 / m is a sum of two monomials, and a linear factor may carry at most one "
        "constant term for the same reason"
    ),
    ("circle", "constant_term"): (
        "the constant term h * h + (y - k) * (y - k) is not a monomial"
    ),
    ("parabola", "constant_term"): (
        "the constant term a * h * h + k is a sum of two monomials"
    ),
    ("distance_components", "constant_term"): (
        "the constant term x1 * x1 + (y2 - y1) * (y2 - y1) is not a monomial"
    ),
    ("slope", "factor_structure"): (
        "only one compound factor sits in the numerator; the rule counts numerator factors, and the "
        "other compound factor (x2 - x1) is the denominator"
    ),
    ("slope", "sign_structure"): (
        "every addend of a sign-readable chain must be a monomial over leaf tokens, and the "
        "denominator x2 - x1 is compound and irreducible, so no split writing keeps its addends "
        "monomial"
    ),
    ("triangle_area", "factor_structure"): (
        "both non-constant factors, b and h, are single symbols"
    ),
    ("trapezoid_area", "leading_coefficient"): (
        "the coefficient of h is (a + b) / 2, which is not a monomial; the split writing "
        "a * h / 2 + b * h / 2 has two summands at degree one instead"
    ),
    ("trapezoid_area", "factor_structure"): (
        "the factorisation h * (a + b) / 2 has one compound factor and one bare symbol"
    ),
    ("difference_quotient", "factor_structure"): (
        "the numerator has one compound factor, fxh - fx"
    ),
    ("quotient_rule", "factor_structure"): (
        "the numerator has one compound factor, du * v - u * dv"
    ),
    ("chain_rule", "factor_structure"): (
        "both factors, dfg and dg, are single symbols; no writing of a product of two symbols has "
        "two compound factors"
    ),
    ("linear_approximation", "constant_term"): (
        "the constant term fa - dfa * a is a sum of two monomials"
    ),
    ("linear_approximation", "roots"): (
        "the root a - fa / dfa is a sum of two monomials"
    ),
    ("taylor_first_term", "factor_structure"): (
        "the factorisation dfa * (x - a) has one compound factor and one bare symbol"
    ),
    ("riemann_sum_term", "factor_structure"): (
        "the numerator has one compound factor, b - a"
    ),
}


def witness_audit(witnesses: Sequence[Witness] | None = None) -> dict[str, Any]:
    """Render every witness and check it: same object, and the shape rule really fires.

    A witness that does not survive both checks is reported as failing, never quietly dropped - a
    claimed visibility that was not rendered is the failure mode this experiment exists to avoid.
    """
    witnesses = tuple(witnesses) if witnesses is not None else WITNESSES
    records = []
    for witness in witnesses:
        item = OBJECT_BY_NAME[witness.object]
        tree = parse(witness.source, CONTROL)
        expression = to_sympy(object_tree(item.writings[0]))
        identical = same_object(tree, expression)
        found = manifest_set(tree, CONTROL, item.variable)
        truth = ground_truth(tree, item.variable)
        records.append(
            {
                "object": witness.object,
                "property": witness.property,
                "source": witness.source,
                "rendered": render(tree, CONTROL),
                "same_object": identical,
                "manifest": found,
                "exposes": witness.property in found,
                "sound": all(name in truth for name in found),
                "note": witness.note,
            }
        )
    holding = tuple(r for r in records if r["same_object"] and r["exposes"])
    return {
        "records": tuple(records),
        "witnesses": len(records),
        "holding": tuple((r["object"], r["property"]) for r in holding),
        "holding_count": len(holding),
        "failing": tuple(
            (r["object"], r["property"]) for r in records if not (r["same_object"] and r["exposes"])
        ),
        "not_same_object": tuple(
            (r["object"], r["property"]) for r in records if not r["same_object"]
        ),
        "unsound": tuple((r["object"], r["property"]) for r in records if not r["sound"]),
    }


def residue_report(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
    table: dict[str, Any] | None = None,
    language: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Part 3: what is left after the search space and the language have been accounted for.

    A residue pair is true, has a written form in this operator set, and is still not manifest under
    the declared rules.  Each is classified as ``different_word`` - a Generation-1 written form
    exists and is exhibited, but its token sequence is not one the corpus declares - or as
    ``rule_limit`` - no such form exists, because the shape rule asks for something the truth rule
    does not.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = table if table is not None else ceiling_table(corpus, workers=workers)
    language = (
        language
        if language is not None
        else language_accounting(corpus, workers=workers, table=table)
    )
    audit = witness_audit()
    blocked = set(language["blocked_pairs"])
    holding = set(audit["holding"])

    entries = []
    for pair in table["still_hidden_pairs"]:
        if pair in blocked:
            continue
        cause = "different_word" if pair in holding else "rule_limit"
        entries.append(
            {
                "object": pair[0],
                "property": pair[1],
                "cause": cause,
                "reason": RULE_LIMIT_REASONS.get(pair) if cause == "rule_limit" else None,
                "witness": next(
                    (
                        record
                        for record in audit["records"]
                        if (record["object"], record["property"]) == pair and record["exposes"]
                    ),
                    None,
                ),
            }
        )
    unexplained = tuple(
        (e["object"], e["property"])
        for e in entries
        if e["cause"] == "rule_limit" and not e["reason"]
    )
    return {
        "residue_pairs": tuple((e["object"], e["property"]) for e in entries),
        "residue_count": len(entries),
        "entries": tuple(entries),
        "by_cause": {
            cause: tuple(
                (e["object"], e["property"]) for e in entries if e["cause"] == cause
            )
            for cause in RESIDUE_CAUSES
        },
        "by_property": {
            name: sum(1 for e in entries if e["property"] == name) for name in PROPERTY_NAMES
        },
        "rule_limits_without_a_reason": unexplained,
        "witness_audit": audit,
    }


# ------------------------------------------------------------------------------------ the sweep


def _trivial_chunk(payload: int) -> int:
    """A chunk that does nothing, so that timing it times only the pool - and the module import."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module, and so SymPy.

    :data:`POOL_STARTUP_SECONDS` is the input to :func:`should_parallelise`, so it is measured here
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
    corpus: Sequence[MathObject] | None = None,
) -> dict[str, Any]:
    """Time both paths over the same probe work and check they agree, then record which one won."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    payloads = _chunks(corpus)
    trees = sum(high - low for _n, _i, low, high in payloads)
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
        "trees": trees,
        "workers": workers,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": sequential_seconds / parallel_seconds if parallel_seconds else float("inf"),
        "identical": sequential == parallel,
        "seconds_per_tree": sequential_seconds / trees if trees else 0.0,
        "declared_seconds_per_tree": TREE_SECONDS,
        "parallel_worth_it": should_parallelise(trees, TREE_SECONDS, workers),
        "default_path": (
            "parallel" if should_parallelise(trees, TREE_SECONDS, workers) else "sequential"
        ),
    }


def visibility_ceiling_report(
    corpus: Sequence[MathObject] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Everything the report prints, in one call."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    table = ceiling_table(corpus, workers=workers)
    language = language_accounting(corpus, workers=workers, table=table)
    residue = residue_report(corpus, workers=workers, table=table, language=language)
    return {
        "rules": rule_identity(),
        "ceiling": table,
        "language": language,
        "residue": residue,
        "soundness": soundness_sweep(corpus, workers=workers, table=table),
        "grammar_independence": grammar_independence(corpus, workers=workers, table=table),
        "defect": zero_bracket_readings(corpus, workers=workers, table=table),
        "headline": {
            "hidden": table["baseline"]["hidden_pair_count"],
            "recovered_in_full_space": table["recovered_count"],
            "recovered_needing_an_unreachable_tree": table["recovered_count"]
            - len(table["precedence_reachable_recoveries"]),
            "recovered_but_precedence_reachable": len(table["precedence_reachable_recoveries"]),
            "blocked_by_the_operator_set": language["blocked_count"],
            "residue": residue["residue_count"],
        },
    }
