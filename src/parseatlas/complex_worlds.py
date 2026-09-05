"""Experiment 0048: the complex domain, and the branch cut as a second convention.

Three questions, and they are not the same question.

**Half A - does the declared domain change the partition?**  The project semantic key is
``(canonical form, domain, excluded points)`` and :mod:`parseatlas.canonical` writes the literal
``"domain": "R"`` for every expression it has ever canonicalised (line 59, NF-2026-00005).  The
middle component has been inert for the whole history of the repository, which means the project
has been silently answering "the domain does not matter" without ever asking.  Experiment 0022
already refuted the general form of that answer over ``F_p``; nobody varied the domain again.
This module varies it to ``C`` and measures whether the 25 grammars partition differently.

**Half B - the branch cut as a second convention.**  Where a complex square root or logarithm is
taken the branch must be chosen, and that choice is *adopted*, not derived: it is the same kind of
object as operator precedence.  So the founding question has a second instance - *what mathematics
would we have if the cut had been placed somewhere else?* - and the two axes can be crossed.

**Half C - reducibility over C.**  Over ``C`` every quadratic factors.  The "roots on the page"
advantage this project measured is bounded over ``R`` by reducibility; half C re-derives the
measurement and separates what the wider domain buys for the EQUIVALENCE from what it does not buy
for the NOTATION.

What this module does NOT do
----------------------------

It does not fix NF-2026-00005.  ``canonical.py`` is untouched; the domain-aware key lives here and
is proved to agree with the existing key cell by cell wherever the domain is ``R``
(:func:`agreement_audit`).  That audit is the load-bearing check of the whole experiment: if the
two keys disagreed over ``R``, the R column and the C column would be measuring different things
and no comparison between them would mean anything.

The agreement audit is a real check and not a delegation
--------------------------------------------------------

:func:`to_symbolic` and :func:`excluded_points` are written out here rather than imported from
:mod:`parseatlas.canonical`, so that the ``R`` branch is an independent re-derivation of the
existing key rather than a call to it.  Only :func:`parseatlas.parser.parse` is shared, because the
parse tree is the datum both keys are keyed on and re-implementing the parser would be measuring a
different language.

Generation 1 cannot DENOTE ``i``
--------------------------------

The language is binary ``+ - * /``, integer and rational literals, named variables and brackets.
There is no radical and no exponentiation, and - this is the subtle part, measured in
:func:`notation_audit` rather than asserted - the token ``i`` IS legal, as a *variable name*.
``(x - i) * (x + i)`` parses, and canonicalises to ``-i**2 + x**2``, not to ``x**2 + 1``.  So the
complex domain is reachable for the EQUIVALENCE - a key may carry ``-I`` as an excluded point - and
not reachable for the NOTATION: no source string in this language denotes the imaginary unit.
Every claim below keeps the two apart, and half C is where they are separated deliberately.
"""

import itertools
import json
import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from sympy import Add, I, Integer, Mul, Rational, Symbol, conjugate, im, log, pi, re, simplify, solve, sqrt

from .canonical import ast_to_dict, canonicalize
from .grammar import Grammar, all_grammars
from .notational_cost import parenthesis_cost, render
from .parser import Node, Number, Variable, parse
from .support_reduction import operator_support

#: The 25 registered grammars: the tied-level control ``G0`` plus the 24 strict orderings.
GRAMMARS: tuple[Grammar, ...] = all_grammars()

#: The conventional grammar.  ``G0`` is how mathematics is written today, so it is the baseline.
CONTROL: Grammar = GRAMMARS[0]

#: The two declared analysis domains.  ``"R"`` must reproduce ``canonical.canonicalize`` exactly.
DOMAINS: tuple[str, str] = ("R", "C")


# =============================================================================== the semantic key


def domain_symbol(name: str, domain: str) -> Symbol:
    """The free symbol a variable denotes under a declared domain.

    ``R`` declares ``real=True``, which is what :func:`parseatlas.canonical.to_sympy` does and is
    therefore what the agreement audit has to reproduce.  ``C`` declares nothing, which is SymPy's
    default assumption set and means "a complex number".
    """
    if domain == "R":
        return Symbol(name, real=True)
    if domain == "C":
        return Symbol(name)
    raise ValueError(f"domain must be one of {DOMAINS}; got {domain!r}")


def to_symbolic(node: Node, domain: str) -> Any:
    """The parse tree as a SymPy expression over the declared domain.

    Deliberately NOT :func:`parseatlas.canonical.to_sympy` with a swapped symbol factory: the
    ``R`` path has to be an independent re-derivation or :func:`agreement_audit` proves nothing.
    """
    if isinstance(node, Number):
        value = node.value
        if value.denominator == 1:
            return Integer(value.numerator)
        return Rational(value.numerator, value.denominator)
    if isinstance(node, Variable):
        return domain_symbol(node.name, domain)
    left = to_symbolic(node.left, domain)
    right = to_symbolic(node.right, domain)
    if node.operator == "+":
        return Add(left, right)
    if node.operator == "-":
        return Add(left, -right)
    if node.operator == "*":
        return Mul(left, right)
    if node.operator == "/":
        return Mul(left, right**-1)
    raise ValueError(f"Unsupported operator: {node.operator}")


def excluded_points(node: Node, domain: str) -> tuple[str, ...]:
    """Where this PARSE TREE is undefined, solved over the declared domain.

    The tree is read, not the simplified value, and that is on purpose: ``(x*x - 1)/(x - 1)``
    denotes ``x + 1`` and is still undefined at ``1``.  Post-order, then the node's own divisor,
    then order-preserving de-duplication - the same traversal the existing key uses, because the
    excluded component is an ORDERED tuple and a different order is a different key.
    """
    if isinstance(node, (Number, Variable)):
        return ()
    terms = excluded_points(node.left, domain) + excluded_points(node.right, domain)
    if node.operator == "/" and (not isinstance(node.right, Number) or node.right.value == 0):
        denominator = to_symbolic(node.right, domain)
        variables = sorted(denominator.free_symbols, key=str)
        if variables:
            terms += tuple(str(point) for point in solve(denominator, variables[0]))
        elif denominator == 0:
            terms += ("all",)
    return tuple(dict.fromkeys(terms))


def semantic_key(node: Node, domain: str) -> tuple[str, str, tuple[str, ...]]:
    """``(canonical form, domain, excluded points)`` over a DECLARED domain.

    This is the project key with its middle component finally carrying information instead of the
    constant ``"R"`` that :mod:`parseatlas.canonical` hard-codes.
    """
    return (str(simplify(to_symbolic(node, domain))), domain, excluded_points(node, domain))


def existing_key(node: Node) -> tuple[str, str, tuple[str, ...]]:
    """The key the repository already computes, assembled exactly as :mod:`parseatlas.analyze` does."""
    canonical = canonicalize(node)
    return (canonical["expression"], canonical["domain"], tuple(canonical["excluded_points"]))


def is_constant_reading(node: Node) -> bool:
    """Does this reading denote a value that does not depend on the variable?

    Read off ``free_symbols`` of the simplified expression rather than off the printed string: a
    string test would call ``x/x + 1`` variable because the source mentions ``x``.
    """
    return not simplify(to_symbolic(node, "C")).free_symbols


# ------------------------------------------------------------------------------------- the corpus


@dataclass(frozen=True)
class Entry:
    """One hand-chosen corpus source and why it is in the corpus."""

    name: str
    source: str
    reason: str


#: Hand-chosen, and the choice is disclosed rather than defended as representative.  The corpus is
#: built to populate every T6 operator-support stratum from 1 to 4 and to contain both kinds of
#: denominator: one with real poles and one whose poles are complex only.
CORPUS: tuple[Entry, ...] = (
    Entry("support_one_sum", "2 + x + 1", "support 1: one operator, so precedence cannot act at all"),
    Entry("support_two_quadratic", "x * x + 1", "support 2, no division: the excluded set is empty in both domains"),
    Entry("support_two_ratio", "x / x + 1", "support 2: some readings are CONSTANT, which half B needs"),
    Entry("complex_pole_reciprocal", "1 / (x*x + 1)", "the card's named case: no real pole, two complex ones"),
    Entry("complex_pole_product", "1 / (x*x + 1) * x", "the same denominator with a second operator to move"),
    Entry("complex_pole_sum", "x / (x*x + 1) + 1", "the same denominator reached through a different top level"),
    Entry("real_pole", "(x + 1)/(x - 2)", "a real pole: R and C see the same excluded set"),
    Entry("removable", "(x*x - 1)/(x - 1)", "a removable restriction: the value hides what the tree records"),
    Entry("reciprocal_sweep", "1 / x * x + 1", "division against multiplication, five classes over R"),
    Entry("standing_linear", "2*t + 1 - t/2", "the repository's standing linear source since 0001"),
    Entry("standing_quadratic", "2*x*x + 1 - x/2", "the repository's standing quadratic source since 0003"),
    Entry("refinement_witness", "(x * x + 1) / 1 - (x * x + 2)", "found by the sweep: the C partition strictly refines the R partition here"),
)


def corpus_sources(corpus: Sequence[Entry] | None = None) -> tuple[str, ...]:
    return tuple(entry.source for entry in (corpus if corpus is not None else CORPUS))


# ------------------------------------------------------------------------------ the audit that binds


def agreement_audit(
    corpus: Sequence[Entry] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Cell by cell, ``semantic_key(tree, "R")`` equals the key the repository already computes.

    Everything else in this module is void if this fails, so it is counted rather than asserted:
    the report carries the number of cells checked and the number of disagreements.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    cells = 0
    failures: list[dict[str, Any]] = []
    for entry in corpus:
        for grammar in grammars:
            tree = parse(entry.source, grammar)
            mine = semantic_key(tree, "R")
            theirs = existing_key(tree)
            cells += 1
            if mine != theirs:
                failures.append(
                    {"source": entry.source, "grammar": grammar.id, "mine": mine, "existing": theirs}
                )
    return {
        "cells": cells,
        "failures": len(failures),
        "failing": tuple(failures),
        "holds": not failures,
    }


#: A source whose divisor has no real root but whose ``solve`` call returns non-real roots anyway.
#: Found by this card; see :func:`real_solve_leak_audit`.  It is deliberately NOT in :data:`CORPUS`,
#: because putting it there would change every half A number for a reason unrelated to half A.
LEAK_WITNESS: str = "1 / (x*x*x*x + 3*x*x + 3)"


def real_solve_leak_audit(
    corpus: Sequence[Entry] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """How often the existing ``"R"`` key carries an excluded point that is not real.

    A separate defect from NF-2026-00005 and found by this card rather than assumed.  The existing
    key calls ``solve`` on a symbol declared ``real=True`` and trusts the result to be real.  With
    the installed SymPy that holds for ``x**2 + 1`` (which returns ``[]``) and fails for
    ``x**4 + 3*x**2 + 3`` (which returns four non-real roots).  The consequence is that the ``"R"``
    label on the existing key is not a domain restriction, only a symbol assumption.

    Direction matters: a leak makes the ``R`` key carry points that only exist over ``C``, so it can
    only make the domain look MORE inert than it is.  Half A's answer is therefore a lower bound on
    the effect, never an inflated one.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    cells = 0
    leaking: list[dict[str, Any]] = []
    for entry in corpus:
        for grammar in grammars:
            tree = parse(entry.source, grammar)
            points = excluded_points(tree, "R")
            cells += 1
            non_real = tuple(point for point in points if "I" in point)
            if non_real:
                leaking.append({"source": entry.source, "grammar": grammar.id, "non_real": non_real})
    witness_tree = parse(LEAK_WITNESS, CONTROL)
    witness_real = excluded_points(witness_tree, "R")
    witness_complex = excluded_points(witness_tree, "C")
    return {
        "cells": cells,
        "leaking_cells": len(leaking),
        "leaking": tuple(leaking),
        "clean_on_corpus": not leaking,
        "witness": LEAK_WITNESS,
        "witness_real_points": len(witness_real),
        "witness_complex_points": len(witness_complex),
        "witness_non_real_under_R": sum(1 for point in witness_real if "I" in point),
        "witness_leaks": any("I" in point for point in witness_real),
    }


# ================================================================================ R against C


def partition(
    source: str, domain: str, grammars: Sequence[Grammar] | None = None
) -> dict[tuple[str, str, tuple[str, ...]], tuple[str, ...]]:
    """The 25 grammars grouped by their semantic key over one declared domain."""
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    grouped: dict[tuple[str, str, tuple[str, ...]], list[str]] = {}
    for grammar in grammars:
        grouped.setdefault(semantic_key(parse(source, grammar), domain), []).append(grammar.id)
    return {key: tuple(members) for key, members in grouped.items()}


def _blocks(assignment: dict[str, Any]) -> frozenset[frozenset[str]]:
    grouped: dict[Any, set[str]] = {}
    for grammar_id, key in assignment.items():
        grouped.setdefault(key, set()).add(grammar_id)
    return frozenset(frozenset(block) for block in grouped.values())


def _refines(finer: frozenset[frozenset[str]], coarser: frozenset[frozenset[str]]) -> bool:
    """Every block of ``finer`` sits inside some block of ``coarser``."""
    return all(any(block <= outer for outer in coarser) for block in finer)


def _sorted_partition(assignment: dict[str, Any]) -> dict[Any, tuple[str, ...]]:
    grouped: dict[Any, list[str]] = {}
    for grammar_id, key in assignment.items():
        grouped.setdefault(key, []).append(grammar_id)
    return {key: tuple(members) for key, members in grouped.items()}


def domain_shift(source: str, grammars: Sequence[Grammar] | None = None) -> dict[str, Any]:
    """One source: its R partition, its C partition, and exactly how the two are related.

    The verdict is computed from containment in both directions, so ``equal``, ``refinement``,
    ``coarsening`` and ``neither`` are all reachable outcomes rather than a single tested guess.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    trees = {grammar.id: parse(source, grammar) for grammar in grammars}
    real = {grammar_id: semantic_key(tree, "R") for grammar_id, tree in trees.items()}
    complex_ = {grammar_id: semantic_key(tree, "C") for grammar_id, tree in trees.items()}
    real_blocks = _blocks(real)
    complex_blocks = _blocks(complex_)
    refines = _refines(complex_blocks, real_blocks)
    coarsens = _refines(real_blocks, complex_blocks)
    if refines and coarsens:
        verdict = "equal"
    elif refines:
        verdict = "refinement"
    elif coarsens:
        verdict = "coarsening"
    else:
        verdict = "neither"
    moved = tuple(
        sorted(
            grammar_id
            for grammar_id in trees
            if {other for other in trees if real[other] == real[grammar_id]}
            != {other for other in trees if complex_[other] == complex_[grammar_id]}
        )
    )
    differing = tuple(
        sorted(
            grammar_id
            for grammar_id, tree in trees.items()
            if excluded_points(tree, "R") != excluded_points(tree, "C")
        )
    )
    canonical_disagreements = tuple(
        sorted(grammar_id for grammar_id in trees if real[grammar_id][0] != complex_[grammar_id][0])
    )
    return {
        "source": source,
        "support": operator_support(source),
        "support_size": len(operator_support(source)),
        "real_classes": len(real_blocks),
        "complex_classes": len(complex_blocks),
        "class_delta": len(complex_blocks) - len(real_blocks),
        "verdict": verdict,
        "strict": verdict in {"refinement", "coarsening"},
        "moved_grammars": moved,
        "excluded_differs": differing,
        "excluded_differs_count": len(differing),
        "canonical_disagreements": canonical_disagreements,
        "real_partition": {str(key): members for key, members in _sorted_partition(real).items()},
        "complex_partition": {str(key): members for key, members in _sorted_partition(complex_).items()},
    }


def _shift_worker(payload: tuple[str, tuple[Grammar, ...]]) -> dict[str, Any]:
    """Module-level entry point so a row is picklable for a spawned process."""
    return domain_shift(*payload)


def domain_shift_table(
    corpus: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Half A over the declared corpus, with the null model applied by support stratum."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [(entry.source, grammars) for entry in corpus]
    resolved = resolve_worker_count(len(payloads), workers, minimum=SECONDS_SCALE_MINIMUM)
    if resolved <= 1 or len(payloads) < 2:
        rows = [domain_shift(*payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=resolved) as pool:
            rows = list(pool.map(_shift_worker, payloads))
    named = tuple({**row, "name": entry.name, "reason": entry.reason} for row, entry in zip(rows, corpus))
    verdicts: dict[str, int] = {}
    for row in named:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    return {
        "rows": named,
        "verdicts": dict(sorted(verdicts.items())),
        "sources": len(named),
        "strict_count": sum(1 for row in named if row["strict"]),
        "excluded_differs_sources": sum(1 for row in named if row["excluded_differs_count"]),
        "excluded_differs_cells": sum(row["excluded_differs_count"] for row in named),
        "invisible_excluded_cells": sum(
            row["excluded_differs_count"] for row in named if row["verdict"] == "equal"
        ),
        "cells": len(named) * len(grammars),
        "partition_unchanged": all(row["verdict"] == "equal" for row in named),
        "no_coarsening": all(row["verdict"] != "coarsening" for row in named),
        "no_crossing": all(row["verdict"] != "neither" for row in named),
        "canonical_disagreement_cells": sum(len(row["canonical_disagreements"]) for row in named),
        "strata": stratify(named, ("real_classes", "complex_classes")),
    }


def stratify(rows: Sequence[dict[str, Any]], means: Sequence[str] = ()) -> tuple[dict[str, Any], ...]:
    """The T6 null model: rates are only meaningful inside one operator-support stratum.

    By the operator-support reduction of experiment 0019 a source distinguishes only the orderings
    of the operators it actually contains, so a support-``s`` source has at most ``s!`` readings and
    therefore at most ``s!`` classes.  A support-1 source cannot move under ANY axis, and counting
    it in a rate hides that the denominator was never free.

    ``means`` names the row fields to average inside each stratum, so the same stratifier serves
    half A (class counts) and half B (product against measured) without either half owning it.
    """
    strata: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        strata.setdefault(row["support_size"], []).append(row)
    out = []
    for size in sorted(strata):
        members = strata[size]
        ceiling = 1
        for factor in range(2, size + 1):
            ceiling *= factor
        record: dict[str, Any] = {
            "support_size": size,
            "reading_ceiling": ceiling,
            "sources": len(members),
            "names": tuple(row.get("name", row["source"]) for row in members),
            "can_move": ceiling > 1,
        }
        if any("strict" in row for row in members):
            strict = sum(1 for row in members if row.get("strict"))
            record["strict_count"] = strict
            record["strict_rate"] = strict / len(members)
        if any("difference" in row for row in members):
            record["product"] = sum(row["product"] for row in members)
            record["measured"] = sum(row["measured"] for row in members)
            record["difference"] = sum(row["difference"] for row in members)
            record["independent_sources"] = sum(1 for row in members if row["independent"])
        for field in means:
            record[f"mean_{field}"] = sum(row[field] for row in members) / len(members)
        if any("excluded_differs_count" in row for row in members):
            record["excluded_differs_cells"] = sum(row.get("excluded_differs_count", 0) for row in members)
        out.append(record)
    return tuple(out)


# ================================================================= the sweep: let it find the wall


#: The atoms the sweep builds sources from.  Two of them carry a denominator that has no real root,
#: which is the only structure that can make the ``R`` and ``C`` excluded sets differ at all.
SWEEP_ATOMS: tuple[str, ...] = ("x", "1", "2", "(x * x + 1)", "(x * x + 2)")

#: The operators the sweep places between atoms.
SWEEP_OPERATORS: tuple[str, ...] = ("+", "-", "*", "/")


def sweep_sources(operator_count: int) -> tuple[str, ...]:
    """Every ``atom (op atom)^n`` source over the declared alphabet, in a fixed order."""
    out = []
    for atoms in itertools.product(SWEEP_ATOMS, repeat=operator_count + 1):
        for operators in itertools.product(SWEEP_OPERATORS, repeat=operator_count):
            parts = [atoms[0]]
            for index, operator in enumerate(operators):
                parts.append(operator)
                parts.append(atoms[index + 1])
            out.append(" ".join(parts))
    return tuple(out)


def divisor_signature(node: Node) -> tuple[str, ...]:
    """The ordered divisor subtrees this tree's excluded set is computed from.

    Two trees with the same signature have the same excluded tuple over EVERY domain, because
    :func:`excluded_points` reads nothing else.
    """
    if isinstance(node, (Number, Variable)):
        return ()
    found = divisor_signature(node.left) + divisor_signature(node.right)
    if node.operator == "/" and (not isinstance(node.right, Number) or node.right.value == 0):
        found += (json.dumps(ast_to_dict(node.right), sort_keys=True),)
    return found


def _prunable(source: str, grammars: Sequence[Grammar]) -> bool:
    """All 25 grammars share one divisor signature, so both domains give one constant excluded tuple.

    The partition is then decided by the canonical form alone.  This is a screen, not a theorem:
    it is sound only if ``simplify`` groups the 25 readings the same way under ``real=True`` and
    under no assumption, which is a property of SymPy rather than of this experiment.
    :func:`prune_control` therefore runs the FULL verdict on every pruned source at the two lengths
    where that is affordable, and the count it checks is published beside the pruned count.
    """
    signatures = {divisor_signature(parse(source, grammar)) for grammar in grammars}
    return len(signatures) == 1


def _sweep_worker(payload: tuple[str, tuple[Grammar, ...]]) -> dict[str, Any]:
    source, grammars = payload
    row = domain_shift(source, grammars)
    return {
        "source": source,
        "verdict": row["verdict"],
        "support_size": row["support_size"],
        "real_classes": row["real_classes"],
        "complex_classes": row["complex_classes"],
        "moved_grammars": row["moved_grammars"],
    }


def _prune_worker(payload: tuple[str, tuple[Grammar, ...]]) -> tuple[str, bool, int]:
    source, grammars = payload
    return source, _prunable(source, grammars), len(operator_support(source))


def _screen(space: Sequence[str], grammars: Sequence[Grammar], workers: int | None):
    payloads = [(source, tuple(grammars)) for source in space]
    resolved = resolve_worker_count(len(payloads), workers, minimum=MICROSECONDS_SCALE_MINIMUM)
    if resolved <= 1:
        return [_prune_worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=resolved) as pool:
        return list(pool.map(_prune_worker, payloads, chunksize=64))


def _verdicts(sources: Sequence[str], grammars: Sequence[Grammar], workers: int | None):
    payloads = [(source, tuple(grammars)) for source in sources]
    resolved = resolve_worker_count(len(payloads), workers, minimum=SECONDS_SCALE_MINIMUM)
    if resolved <= 1 or len(payloads) < 2:
        return [_sweep_worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=resolved) as pool:
        return list(pool.map(_sweep_worker, payloads, chunksize=8))


def prune_control(
    operator_count: int,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Run the FULL verdict on every source the screen pruned, and count the disagreements.

    This is what makes :func:`_prunable` reportable.  A pruned source is claimed to be ``equal``;
    this recomputes it the expensive way and says how many claims were wrong.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    space = sweep_sources(operator_count)
    screened = _screen(space, grammars, workers)
    pruned = [source for source, prunable, _size in screened if prunable]
    rows = _verdicts(pruned, grammars, workers)
    wrong = tuple(row for row in rows if row["verdict"] != "equal")
    return {
        "operator_count": operator_count,
        "space": len(space),
        "pruned": len(pruned),
        "checked": len(rows),
        "wrong": len(wrong),
        "wrong_rows": wrong,
        "holds": not wrong,
    }


def refinement_sweep(
    operator_count: int,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Classify every source of one length, and report the split by support stratum.

    ``operator_count`` is a **computational limit**, not a threshold: the space is
    ``5^(n+1) * 4^n`` sources and the report publishes the curve over every ``n`` that was run
    rather than a single chosen ``n``.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    space = sweep_sources(operator_count)
    screened = _screen(space, grammars, workers)
    pruned = tuple(source for source, prunable, _size in screened if prunable)
    live = tuple(source for source, prunable, _size in screened if not prunable)
    support_of = {source: size for source, _prunable, size in screened}
    rows = _verdicts(live, grammars, workers)
    verdicts: dict[str, int] = {"equal": len(pruned)}
    for row in rows:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    witnesses = tuple(row for row in rows if row["verdict"] != "equal")
    strata: dict[int, dict[str, int]] = {}
    for source in space:
        strata.setdefault(support_of[source], {"sources": 0, "live": 0, "strict": 0})["sources"] += 1
    for source in live:
        strata[support_of[source]]["live"] += 1
    for row in witnesses:
        strata[row["support_size"]]["strict"] += 1
    return {
        "operator_count": operator_count,
        "space": len(space),
        "pruned": len(pruned),
        "live": len(live),
        "verdicts": dict(sorted(verdicts.items())),
        "strict_count": len(witnesses),
        "witnesses": witnesses,
        "coarsening_count": sum(1 for row in rows if row["verdict"] == "coarsening"),
        "crossing_count": sum(1 for row in rows if row["verdict"] == "neither"),
        "strata": tuple(
            {
                "support_size": size,
                "reading_ceiling": _factorial(size),
                "sources": bucket["sources"],
                "live": bucket["live"],
                "strict": bucket["strict"],
                "strict_rate": bucket["strict"] / bucket["live"] if bucket["live"] else 0.0,
            }
            for size, bucket in sorted(strata.items())
        ),
    }


def _factorial(size: int) -> int:
    value = 1
    for factor in range(2, size + 1):
        value *= factor
    return value


def refinement_curve(
    max_operators: int = 2,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The sweep at every length up to ``max_operators``, published as a curve."""
    runs = tuple(refinement_sweep(count, grammars, workers) for count in range(1, max_operators + 1))
    return {
        "max_operators": max_operators,
        "runs": runs,
        "space": sum(run["space"] for run in runs),
        "live": sum(run["live"] for run in runs),
        "strict_count": sum(run["strict_count"] for run in runs),
        "coarsening_count": sum(run["coarsening_count"] for run in runs),
        "crossing_count": sum(run["crossing_count"] for run in runs),
        "witnesses": tuple(witness for run in runs for witness in run["witnesses"]),
        "monotone": all(
            runs[index]["strict_count"] <= runs[index + 1]["strict_count"]
            for index in range(len(runs) - 1)
        ),
    }


# ======================================================================== half B: the branch cut


@dataclass(frozen=True)
class BranchConvention:
    """One adopted choice of where the branch cut lies.

    A convention is a ray from the origin.  ``arg`` is taken in the half-open interval
    ``(cut, cut + 2*pi]``, so the cut ray itself belongs to the branch approached
    counter-clockwise, and every point off the ray gets exactly one angle.

    ``cut_diamond`` is the cut angle in *diamond* units - see :func:`diamond_angle` - which is what
    makes the sheet test an exact rational comparison instead of a floating-point angle.
    ``ray`` is the exact Gaussian-rational direction of the cut, used by :func:`straddle_audit` to
    build the two points that pin where the cut lies.
    """

    name: str
    cut_angle: str
    cut_diamond: Fraction
    ray: tuple[int, int]
    cut_ray: str
    arg_interval: str
    is_sympy_default: bool = False


def diamond_angle(real_part: Fraction, imaginary_part: Fraction) -> Fraction:
    """A strictly increasing rational surrogate for the principal argument.

    Maps ``arg`` in ``(-pi, pi]`` onto ``(-2, 2]`` with ``k*pi/4 -> k/2``, exactly, for any
    Gaussian rational.  The point of it is that ``arg(w) <= c`` becomes a comparison of two exact
    rationals, so no branch decision in this module is ever taken by a float.
    """
    if real_part == 0 and imaginary_part == 0:
        raise ValueError("the origin is a branch point and has no argument")
    value = Fraction(imaginary_part, abs(real_part) + abs(imaginary_part))
    if real_part < 0:
        value = 2 - value if imaginary_part >= 0 else -2 - value
    return value


#: The four declared conventions.  The cut is placed on a coordinate axis so that the sheet test is
#: a sign test on exact Gaussian rationals.  ``principal`` is SymPy's default and it is NAMED as a
#: convention here rather than assumed: an unnamed default is an accident, not a choice.
CONVENTIONS: tuple[BranchConvention, ...] = (
    BranchConvention(
        "principal",
        "-pi",
        Fraction(-2),
        (-1, 0),
        "the negative real axis, arg = pi",
        "(-pi, pi]",
        is_sympy_default=True,
    ),
    BranchConvention(
        "negative_imaginary",
        "-pi/2",
        Fraction(-1),
        (0, -1),
        "the negative imaginary axis, arg = -pi/2",
        "(-pi/2, 3*pi/2]",
    ),
    BranchConvention(
        "positive_axis",
        "0",
        Fraction(0),
        (1, 0),
        "the positive real axis, arg = 0",
        "(0, 2*pi]",
    ),
    BranchConvention(
        "positive_imaginary",
        "pi/2",
        Fraction(1),
        (0, 1),
        "the positive imaginary axis, arg = pi/2",
        "(pi/2, 5*pi/2]",
    ),
)

#: Eight conventions, adding the four diagonal cuts.  Used by :func:`convention_sweep`, so that the
#: NUMBER of conventions is a swept parameter rather than a number chosen in advance.
CONVENTIONS_EIGHT: tuple[BranchConvention, ...] = (
    CONVENTIONS[0],
    BranchConvention("cut_minus_3pi_4", "-3*pi/4", Fraction(-3, 2), (-1, -1), "the ray at arg = -3*pi/4", "(-3*pi/4, 5*pi/4]"),
    CONVENTIONS[1],
    BranchConvention("cut_minus_pi_4", "-pi/4", Fraction(-1, 2), (1, -1), "the ray at arg = -pi/4", "(-pi/4, 7*pi/4]"),
    CONVENTIONS[2],
    BranchConvention("cut_pi_4", "pi/4", Fraction(1, 2), (1, 1), "the ray at arg = pi/4", "(pi/4, 9*pi/4]"),
    CONVENTIONS[3],
    BranchConvention("cut_3pi_4", "3*pi/4", Fraction(3, 2), (-1, 1), "the ray at arg = 3*pi/4", "(3*pi/4, 11*pi/4]"),
)

CONVENTIONS_BY_NAME: dict[str, BranchConvention] = {item.name: item for item in CONVENTIONS_EIGHT}


def sheet_index(value: tuple[Fraction, Fraction], convention: BranchConvention) -> int:
    """``0`` or ``1``: how many turns of ``2*pi`` this convention adds to the principal argument.

    ``arg_c(w) = arg_principal(w) + 2*pi*sheet``, so the whole content of a convention, for any
    single-valued branch, is this one bit per point.
    """
    return 1 if diamond_angle(*value) <= convention.cut_diamond else 0


def to_sympy_value(value: tuple[Fraction, Fraction]) -> Any:
    return Rational(value[0]) + Rational(value[1]) * I


def branch_sqrt(value: tuple[Fraction, Fraction], convention: BranchConvention) -> Any:
    """``sqrt`` under a declared convention: the principal root, flipped on the far sheet."""
    if value == (0, 0):
        return Integer(0)
    return simplify(sqrt(to_sympy_value(value)) * (-1) ** sheet_index(value, convention))


def branch_log(value: tuple[Fraction, Fraction], convention: BranchConvention) -> Any:
    """``log`` under a declared convention: the principal log, plus a full turn on the far sheet."""
    if value == (0, 0):
        raise ValueError("log has no value at the branch point 0")
    return simplify(log(to_sympy_value(value)) + 2 * pi * I * sheet_index(value, convention))


def sympy_default_audit() -> dict[str, Any]:
    """``principal`` reproduces SymPy's own ``sqrt`` and ``log``, so the default is named, not assumed."""
    probes = (
        (Fraction(1), Fraction(0)),
        (Fraction(-1), Fraction(0)),
        (Fraction(0), Fraction(1)),
        (Fraction(0), Fraction(-1)),
        (Fraction(4), Fraction(0)),
        (Fraction(-4), Fraction(0)),
        (Fraction(2), Fraction(3)),
        (Fraction(-2), Fraction(-3)),
        (Fraction(1, 2), Fraction(-5, 7)),
    )
    principal = CONVENTIONS_BY_NAME["principal"]
    failures = []
    for value in probes:
        target = to_sympy_value(value)
        if simplify(branch_sqrt(value, principal) - sqrt(target)) != 0:
            failures.append({"value": str(target), "function": "sqrt"})
        if simplify(branch_log(value, principal) - log(target)) != 0:
            failures.append({"value": str(target), "function": "log"})
    return {
        "probes": len(probes),
        "checks": 2 * len(probes),
        "failures": len(failures),
        "failing": tuple(failures),
        "holds": not failures,
    }


#: Radius at which a cut is straddled.  Any positive radius works; ``4`` is used so the probe values
#: print as small exact rationals.
STRADDLE_RADIUS: Fraction = Fraction(4)

#: The offsets the straddle audit is run at.  Swept rather than declared once, because "how close is
#: close enough to a cut" is exactly the kind of number that would otherwise be a hidden threshold.
STRADDLE_OFFSETS: tuple[Fraction, ...] = (
    Fraction(1, 10),
    Fraction(1, 100),
    Fraction(1, 1000),
    Fraction(1, 100000),
)


def straddle_pair(
    convention: BranchConvention, offset: Fraction = STRADDLE_OFFSETS[2]
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    """Two points a hair either side of this convention's cut ray, counter-clockwise first.

    Built from the convention's own exact ray direction and the perpendicular ``i * ray``, so the
    same code serves the axis cuts and the diagonal ones.
    """
    direction = convention.ray
    perpendicular = (-direction[1], direction[0])
    base = (STRADDLE_RADIUS * direction[0], STRADDLE_RADIUS * direction[1])
    above = (base[0] + offset * perpendicular[0], base[1] + offset * perpendicular[1])
    below = (base[0] - offset * perpendicular[0], base[1] - offset * perpendicular[1])
    return above, below


def sqrt_jumps(
    above: tuple[Fraction, Fraction], below: tuple[Fraction, Fraction], convention: BranchConvention
) -> bool:
    """Does ``sqrt`` under this convention change SHEET between two nearby points?

    Exact and threshold-free.  The two possible values at a point are ``+-`` the principal root, so
    the branch either keeps the same sheet across the pair or flips it.  ``Re(f(a) * conj(f(b)))``
    is ``|f(a)| |f(b)| cos(angle between them)``, which is positive when the sheet is kept and
    negative when it flips; its SIGN decides, and no magnitude is compared against anything.
    """
    left = branch_sqrt(above, convention)
    right = branch_sqrt(below, convention)
    return bool(re(left * conjugate(right)).is_negative)


def log_jumps(
    above: tuple[Fraction, Fraction], below: tuple[Fraction, Fraction], convention: BranchConvention
) -> bool:
    """Does ``log`` under this convention change SHEET between two nearby points?

    The difference of two branch logarithms is ``2*pi*i*k`` plus the small genuine change, so the
    only two possible limits are ``0`` and ``+-2*pi*i``.  ``pi`` is their exact midpoint - it is
    the structure of the multivalued logarithm, not a tuned constant.
    """
    difference = branch_log(above, convention) - branch_log(below, convention)
    return bool((abs(im(difference)) - pi).is_positive)


def straddle_audit(
    conventions: Sequence[BranchConvention] | None = None,
    offset: Fraction = STRADDLE_OFFSETS[2],
) -> dict[str, Any]:
    """Each convention jumps across its OWN cut and is continuous across every other one.

    This is what pins where a cut lies: a convention is not identified by its name but by the ray
    on which its ``sqrt`` and its ``log`` are discontinuous.  Both functions are checked, because a
    convention that moved only one of them would not be a branch convention at all.
    """
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    rows = []
    for owner in conventions:
        above, below = straddle_pair(owner, offset)
        for convention in conventions:
            expected = owner.name == convention.name
            sqrt_jump = sqrt_jumps(above, below, convention)
            log_jump = log_jumps(above, below, convention)
            rows.append(
                {
                    "cut_of": owner.name,
                    "cut_ray": owner.cut_ray,
                    "measured_under": convention.name,
                    "above": str(to_sympy_value(above)),
                    "below": str(to_sympy_value(below)),
                    "sqrt_above": str(branch_sqrt(above, convention)),
                    "sqrt_below": str(branch_sqrt(below, convention)),
                    "sqrt_jumps": sqrt_jump,
                    "log_jumps": log_jump,
                    "expected": expected,
                    "agrees": sqrt_jump == expected and log_jump == expected,
                }
            )
    return {
        "offset": str(offset),
        "checks": 2 * len(rows),
        "rows": tuple(rows),
        "violations": tuple(row for row in rows if not row["agrees"]),
        "holds": all(row["agrees"] for row in rows),
    }


def straddle_offset_sweep(
    conventions: Sequence[BranchConvention] | None = None,
    offsets: Sequence[Fraction] = STRADDLE_OFFSETS,
) -> dict[str, Any]:
    """The straddle audit at every declared offset, so the classification is shown to be stable."""
    rows = tuple(
        {
            "offset": str(offset),
            "checks": (audit := straddle_audit(conventions, offset))["checks"],
            "violations": len(audit["violations"]),
            "holds": audit["holds"],
        }
        for offset in offsets
    )
    return {
        "rows": rows,
        "offsets": len(rows),
        "stable": all(row["holds"] for row in rows),
        "total_checks": sum(row["checks"] for row in rows),
    }


# ------------------------------------------------------------------- exact Gaussian-rational values


class PoleReached(ZeroDivisionError):
    """The sample point is a pole of this reading: the composite has no value there."""


def gaussian_eval(node: Node, point: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    """Evaluate a parse tree at a Gaussian-rational point, exactly.

    Exactness matters here for one reason: the sheet index is a comparison against a cut, and a
    rounded value near a cut would decide a branch by rounding error.
    """
    if isinstance(node, Number):
        return (Fraction(node.value), Fraction(0))
    if isinstance(node, Variable):
        return point
    left = gaussian_eval(node.left, point)
    right = gaussian_eval(node.right, point)
    if node.operator == "+":
        return (left[0] + right[0], left[1] + right[1])
    if node.operator == "-":
        return (left[0] - right[0], left[1] - right[1])
    if node.operator == "*":
        return (left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0])
    if node.operator == "/":
        norm = right[0] * right[0] + right[1] * right[1]
        if norm == 0:
            raise PoleReached
        return (
            (left[0] * right[0] + left[1] * right[1]) / norm,
            (left[1] * right[0] - left[0] * right[1]) / norm,
        )
    raise ValueError(f"Unsupported operator: {node.operator}")


#: Radius of the declared sample square.  A **computational limit**: :func:`grid_sweep` publishes the
#: curve over both grid parameters and shows where the measured count stops moving.
GRID_RADIUS: int = 4

#: Denominator of the declared lattice spacing.  The SECOND computational limit, and the one that
#: mattered: a coarse mesh misses the small-modulus points where a reading's image reaches the
#: sector between two cuts, and reports a collapse that is a sampling artefact.
GRID_MESH: int = 3


def sample_grid(radius: int = GRID_RADIUS, mesh: int = GRID_MESH) -> tuple[tuple[Fraction, Fraction], ...]:
    """The lattice of Gaussian rationals ``a/mesh + b/mesh i`` with both parts in ``[-radius, radius]``."""
    extent = radius * mesh
    return tuple(
        (Fraction(a, mesh), Fraction(b, mesh))
        for a in range(-extent, extent + 1)
        for b in range(-extent, extent + 1)
    )


def composite_signature(
    node: Node, convention: BranchConvention, grid: Sequence[tuple[Fraction, Fraction]]
) -> tuple[Any, ...]:
    """The composite ``outer_c(inner)`` as a value, sampled exactly on the grid.

    A cell is recorded as ``(value of the inner reading, sheet)`` at each point, and ``None`` at a
    pole.  That pair IS the composite: ``sqrt_c(w)`` determines ``w`` because ``sqrt_c(w)**2 == w``,
    and ``log_c(w)`` determines ``w`` because ``exp(log_c(w)) == w``; conversely ``(w, sheet)``
    determines the value under either outer function.  So this encoding neither adds nor loses
    information - :func:`encoding_faithfulness_audit` checks that claim against the actual SymPy
    values rather than leaving it as an argument - and, this is the point, it never mentions the
    inner canonical form, so the partition it induces is a measurement about the composite rather
    than a restatement of the key.

    The branch point ``0`` is recorded as its own label: ``sqrt`` maps it to ``0`` under every
    convention and ``log`` is undefined there under every convention, so no convention is
    distinguished by it either way.
    """
    signature: list[Any] = []
    for point in grid:
        try:
            value = gaussian_eval(node, point)
        except PoleReached:
            signature.append(None)
            continue
        if value == (0, 0):
            signature.append("branch_point")
            continue
        signature.append((value[0], value[1], sheet_index(value, convention)))
    return tuple(signature)


def encoding_faithfulness_audit(
    source: str = "1 / x * x + 1",
    conventions: Sequence[BranchConvention] | None = None,
    grammars: Sequence[Grammar] | None = None,
    radius: int = 1,
    mesh: int = 1,
) -> dict[str, Any]:
    """The ``(value, sheet)`` encoding counts the same composites the actual functions do.

    Run on a small grid with real SymPy ``sqrt`` and ``log`` values, because the whole of half B is
    counted through the encoding and an encoding that merged two composites would understate the
    measured count silently.
    """
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    grid = sample_grid(radius, mesh)
    trees = {grammar.id: parse(source, grammar) for grammar in grammars}
    encoded: dict[tuple[str, str], Any] = {}
    as_sqrt: dict[tuple[str, str], Any] = {}
    as_log: dict[tuple[str, str], Any] = {}
    for grammar_id, tree in trees.items():
        for convention in conventions:
            cell = (grammar_id, convention.name)
            encoded[cell] = composite_signature(tree, convention, grid)
            sqrt_row: list[Any] = []
            log_row: list[Any] = []
            for point in grid:
                try:
                    value = gaussian_eval(tree, point)
                except PoleReached:
                    sqrt_row.append(None)
                    log_row.append(None)
                    continue
                if value == (0, 0):
                    sqrt_row.append("branch_point")
                    log_row.append("branch_point")
                    continue
                sqrt_row.append(str(branch_sqrt(value, convention)))
                log_row.append(str(branch_log(value, convention)))
            as_sqrt[cell] = tuple(sqrt_row)
            as_log[cell] = tuple(log_row)
    return {
        "source": source,
        "grid_points": len(grid),
        "cells": len(encoded),
        "encoded_distinct": len(set(encoded.values())),
        "sqrt_distinct": len(set(as_sqrt.values())),
        "log_distinct": len(set(as_log.values())),
        "sqrt_agrees": _blocks(encoded) == _blocks(as_sqrt),
        "log_agrees": _blocks(encoded) == _blocks(as_log),
        "holds": _blocks(encoded) == _blocks(as_sqrt) == _blocks(as_log),
    }


def axis_cross(
    source: str,
    conventions: Sequence[BranchConvention] | None = None,
    grammars: Sequence[Grammar] | None = None,
    radius: int = GRID_RADIUS,
    mesh: int = GRID_MESH,
) -> dict[str, Any]:
    """Cross the precedence axis with the branch axis and count what actually comes out.

    If the axes were independent the count would be the product of the two axis sizes.  It is not,
    and the difference is reported rather than the ratio, because the interaction is carried by a
    nameable subset of the readings rather than spread evenly.

    Two facts are separated here and the report keeps them apart:

    * the branch axis can never SPLIT a precedence class, and that is forced rather than found -
      two grammars in the same class have the same value at every point, hence the same sheet at
      every point, hence the same composite under every convention.  It is reported as a
      confirmation of the implementation, not as a discovery.
    * the branch axis can COLLAPSE - two conventions can give the same composite - and that is what
      the deficit counts.
    """
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    grid = sample_grid(radius, mesh)
    trees = {grammar.id: parse(source, grammar) for grammar in grammars}
    inner = {grammar_id: semantic_key(tree, "C") for grammar_id, tree in trees.items()}
    inner_blocks = _blocks(inner)
    cells = {
        (grammar_id, convention.name): composite_signature(tree, convention, grid)
        for grammar_id, tree in trees.items()
        for convention in conventions
    }
    measured = len({signature for signature in cells.values()})
    per_convention_blocks = {
        convention.name: _blocks({grammar_id: cells[(grammar_id, convention.name)] for grammar_id in trees})
        for convention in conventions
    }
    stable = len(set(per_convention_blocks.values())) == 1
    matches_inner = all(blocks == inner_blocks for blocks in per_convention_blocks.values())
    per_class = []
    for block in sorted(inner_blocks, key=lambda item: sorted(item)):
        representative = sorted(block)[0]
        behaviours = {cells[(representative, convention.name)] for convention in conventions}
        constant = is_constant_reading(trees[representative])
        per_class.append(
            {
                "grammars": tuple(sorted(block)),
                "canonical": inner[representative][0],
                "constant": constant,
                "distinct_conventions": len(behaviours),
                "collapse": len(conventions) - len(behaviours),
            }
        )
    non_constant_collapse = tuple(
        item for item in per_class if item["collapse"] and not item["constant"]
    )
    return {
        "source": source,
        "support_size": len(operator_support(source)),
        "grid_radius": radius,
        "grid_mesh": mesh,
        "grid_points": len(grid),
        "conventions": tuple(convention.name for convention in conventions),
        "inner_classes": len(inner_blocks),
        "branch_conventions": len(conventions),
        "product": len(inner_blocks) * len(conventions),
        "measured": measured,
        "difference": len(inner_blocks) * len(conventions) - measured,
        "independent": measured == len(inner_blocks) * len(conventions),
        "partition_stable_across_conventions": stable,
        "partition_equals_inner_partition": matches_inner,
        "classes": tuple(per_class),
        "constant_classes": sum(1 for item in per_class if item["constant"]),
        "constant_collapse": sum(item["collapse"] for item in per_class if item["constant"]),
        "non_constant_collapse": non_constant_collapse,
        "interaction_carried_by_constants": not non_constant_collapse,
    }


def constant_class_deficit(
    corpus: Sequence[Entry] | None = None,
    conventions: Sequence[BranchConvention] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """The deficit a constant reading FORCES, computed without any grid at all.

    A reading whose value does not depend on the variable takes one point of the plane, so two
    conventions that put that point on the same sheet give literally the same composite.  This is
    the number the grid sweep should converge to from below, and it is derived rather than sampled,
    so the sweep has something to be checked against instead of only a plateau.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    probe = (Fraction(1, 3), Fraction(1, 7))
    rows = []
    for entry in corpus:
        trees = {grammar.id: parse(entry.source, grammar) for grammar in grammars}
        inner = {grammar_id: semantic_key(tree, "C") for grammar_id, tree in trees.items()}
        for block in sorted(_blocks(inner), key=lambda item: sorted(item)):
            representative = sorted(block)[0]
            if not is_constant_reading(trees[representative]):
                continue
            value = gaussian_eval(trees[representative], probe)
            sheets = {sheet_index(value, convention) for convention in conventions}
            rows.append(
                {
                    "name": entry.name,
                    "representative": representative,
                    "value": f"{value[0]}+{value[1]}i",
                    "distinct_sheets": len(sheets),
                    "collapse": len(conventions) - len(sheets),
                }
            )
    return {
        "rows": tuple(rows),
        "constant_classes": len(rows),
        "predicted_deficit": sum(row["collapse"] for row in rows),
    }


def _cross_worker(
    payload: tuple[str, tuple[BranchConvention, ...], tuple[Grammar, ...], int, int]
) -> dict[str, Any]:
    return axis_cross(*payload)


def axis_cross_table(
    corpus: Sequence[Entry] | None = None,
    conventions: Sequence[BranchConvention] | None = None,
    grammars: Sequence[Grammar] | None = None,
    radius: int = GRID_RADIUS,
    mesh: int = GRID_MESH,
    workers: int | None = None,
) -> dict[str, Any]:
    """Half B over the declared corpus."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [(entry.source, conventions, grammars, radius, mesh) for entry in corpus]
    resolved = resolve_worker_count(len(payloads), workers, minimum=SECONDS_SCALE_MINIMUM)
    if resolved <= 1 or len(payloads) < 2:
        rows = [axis_cross(*payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=resolved) as pool:
            rows = list(pool.map(_cross_worker, payloads))
    named = tuple({**row, "name": entry.name} for row, entry in zip(rows, corpus))
    return {
        "rows": named,
        "conventions": tuple(convention.name for convention in conventions),
        "convention_count": len(conventions),
        "grid_radius": radius,
        "grid_mesh": mesh,
        "grid_points": len(sample_grid(radius, mesh)),
        "product": sum(row["product"] for row in named),
        "measured": sum(row["measured"] for row in named),
        "difference": sum(row["difference"] for row in named),
        "independent_sources": sum(1 for row in named if row["independent"]),
        "interacting_sources": sum(1 for row in named if not row["independent"]),
        "partition_stable_everywhere": all(row["partition_stable_across_conventions"] for row in named),
        "partition_equals_inner_everywhere": all(row["partition_equals_inner_partition"] for row in named),
        "constant_classes": sum(row["constant_classes"] for row in named),
        "constant_collapse": sum(row["constant_collapse"] for row in named),
        "non_constant_collapse": tuple(
            (row["name"], item["grammars"][0], item["collapse"])
            for row in named
            for item in row["non_constant_collapse"]
        ),
        "interaction_carried_by_constants": all(row["interaction_carried_by_constants"] for row in named),
        "strata": stratify(named, ()),
    }


def grid_sweep(
    corpus: Sequence[Entry] | None = None,
    settings: Sequence[tuple[int, int]] = ((1, 1), (2, 1), (3, 1), (4, 1), (6, 1), (2, 2), (3, 2), (6, 2), (2, 3), (4, 3), (3, 4), (4, 5)),
    conventions: Sequence[BranchConvention] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Sweep BOTH grid parameters and show where the measured count stops moving.

    The grid is a **computational limit** in two directions, and the second one is the one that
    caught this experiment out: a coarse mesh can miss the small-modulus points at which a
    reading's image reaches the sector between two cuts, and then reports a collapse that is a
    sampling artefact rather than a property of the composite.  So the sweep varies radius and mesh
    independently, and the target it converges to is :func:`constant_class_deficit`, which is
    derived without any grid.
    """
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    predicted = constant_class_deficit(corpus, conventions, grammars)["predicted_deficit"]
    rows = []
    for radius, mesh in settings:
        table = axis_cross_table(corpus, conventions, grammars, radius, mesh, workers)
        rows.append(
            {
                "radius": radius,
                "mesh": mesh,
                "points": table["grid_points"],
                "product": table["product"],
                "measured": table["measured"],
                "difference": table["difference"],
                "non_constant_collapse": len(table["non_constant_collapse"]),
                "matches_prediction": table["difference"] == predicted,
            }
        )
    settled = tuple(row for row in rows if row["matches_prediction"])
    return {
        "rows": tuple(rows),
        "predicted_deficit": predicted,
        "settings_checked": len(rows),
        "settings_matching_prediction": len(settled),
        "first_matching": (settled[0]["radius"], settled[0]["mesh"]) if settled else None,
        "largest_points_checked": max(row["points"] for row in rows),
        "never_below_prediction": all(row["difference"] >= predicted for row in rows),
    }


def convention_sweep(
    corpus: Sequence[Entry] | None = None,
    counts: Sequence[int] = (1, 2, 4, 8),
    grammars: Sequence[Grammar] | None = None,
    radius: int = GRID_RADIUS,
    mesh: int = GRID_MESH,
    workers: int | None = None,
) -> dict[str, Any]:
    """Sweep the NUMBER of branch conventions and publish the curve.

    The number of conventions is exactly the kind of parameter that could have been declared once
    and never questioned, so it is swept: ``1, 2, 4, 8`` evenly spaced cuts, taken from
    :data:`CONVENTIONS_EIGHT` at a fixed stride so that each set contains the previous one.
    """
    rows = []
    for count in counts:
        stride = len(CONVENTIONS_EIGHT) // count
        chosen = CONVENTIONS_EIGHT[::stride][:count]
        table = axis_cross_table(corpus, chosen, grammars, radius, mesh, workers)
        rows.append(
            {
                "conventions": count,
                "names": tuple(convention.name for convention in chosen),
                "product": table["product"],
                "measured": table["measured"],
                "difference": table["difference"],
                "constant_collapse": table["constant_collapse"],
                "carried_by_constants": table["interaction_carried_by_constants"],
                "ratio": table["measured"] / table["product"] if table["product"] else 0.0,
            }
        )
    return {
        "rows": tuple(rows),
        "monotone_difference": all(
            rows[index]["difference"] <= rows[index + 1]["difference"] for index in range(len(rows) - 1)
        ),
        "monotone_ratio": all(
            rows[index]["ratio"] >= rows[index + 1]["ratio"] for index in range(len(rows) - 1)
        ),
        "carried_by_constants_everywhere": all(row["carried_by_constants"] for row in rows),
    }


def agreeing_pairs_audit(
    corpus: Sequence[Entry] | None = None,
    conventions: Sequence[BranchConvention] | None = None,
    grammars: Sequence[Grammar] | None = None,
    radius: int = GRID_RADIUS,
    mesh: int = GRID_MESH,
) -> dict[str, Any]:
    """Does any grammar pair that agrees under one convention disagree under another?

    Counted rather than argued, and reported with the count of pairs examined, because the card
    asks for the cases by name and "none" is only worth reading beside the size of the search.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    conventions = tuple(conventions) if conventions is not None else CONVENTIONS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    grid = sample_grid(radius, mesh)
    pairs = 0
    splitting = []
    for entry in corpus:
        trees = {grammar.id: parse(entry.source, grammar) for grammar in grammars}
        cells = {
            (grammar_id, convention.name): composite_signature(tree, convention, grid)
            for grammar_id, tree in trees.items()
            for convention in conventions
        }
        identifiers = sorted(trees)
        for index, left in enumerate(identifiers):
            for right in identifiers[index + 1 :]:
                pairs += 1
                agreement = {
                    convention.name: cells[(left, convention.name)] == cells[(right, convention.name)]
                    for convention in conventions
                }
                if len(set(agreement.values())) > 1:
                    splitting.append({"source": entry.source, "pair": (left, right), "agreement": agreement})
    return {
        "pairs_examined": pairs,
        "conventions": len(conventions),
        "splitting_pairs": len(splitting),
        "splitting": tuple(splitting),
        "holds": not splitting,
    }


# ================================================================= half C: reducibility over C


@dataclass(frozen=True)
class Quadratic:
    """One quadratic, its expanded writing, and a factored writing if the language has one."""

    name: str
    expanded: str
    factored: str | None
    shape: str
    stand_ins: tuple[str, ...]
    note: str


#: The three quadratics the manager measured for the owner's mathematician, plus their factored
#: writings.  ``factored`` is ``None`` where Generation 1 cannot spell the factors; ``shape`` is the
#: same factorisation with a NAMED LEAF standing in for the number the language cannot write, which
#: measures the cost of the SHAPE and is not a writing of the object.
QUADRATICS: tuple[Quadratic, ...] = (
    Quadratic(
        "reducible_over_Q",
        "2 * x * x + 3 * x - 5",
        "(2 * x + 5) * (x - 1)",
        "(2 * x + 5) * (x - 1)",
        (),
        "both roots rational, so the factored writing is in the language",
    ),
    Quadratic(
        "reducible_over_R_only",
        "x * x - 2",
        None,
        "(x - r) * (x + r)",
        ("r",),
        "roots are real and irrational; `r` stands in for a radical the language cannot write",
    ),
    Quadratic(
        "reducible_over_C_only",
        "x * x + 1",
        None,
        "(x - u) * (x + u)",
        ("u",),
        "roots are non-real; `u` stands in for `i`, which the language cannot denote",
    ),
)


def root_report(source: str) -> dict[str, Any]:
    """Where a quadratic's roots live, and therefore over which field it factors."""
    tree = parse(source, CONTROL)
    expression = to_symbolic(tree, "C")
    variables = sorted(expression.free_symbols, key=str)
    roots = solve(expression, variables[0]) if variables else []
    classified = [
        {"root": str(root), "rational": bool(root.is_rational), "real": bool(root.is_real)}
        for root in roots
    ]
    return {
        "source": source,
        "roots": tuple(classified),
        "root_count": len(classified),
        "factors_over_Q": bool(classified) and all(item["rational"] for item in classified),
        "factors_over_R": bool(classified) and all(item["real"] for item in classified),
        "factors_over_C": len(classified) == 2,
    }


def notation_audit() -> dict[str, Any]:
    """Generation 1 can WRITE the string `(x - i) * (x + i)`; it does not DENOTE `x*x + 1`.

    This is the measurement that keeps half C honest.  `i` is a legal variable name in this
    language, so "the language cannot write `i`" is false as stated and true as meant: the tokeniser
    accepts it, the parser builds a tree, and the canonical form that comes out carries a free
    symbol `i` rather than the imaginary unit.  Asserting the limitation would have been wrong;
    measuring it says exactly where the limitation lies.
    """
    attempts = (
        ("factored_with_i", "(x - i) * (x + i)", "x**2 + 1"),
        ("factored_with_r", "(x - r) * (x + r)", "x**2 - 2"),
        ("bare_i_squared", "i * i", "-1"),
    )
    rows = []
    for name, source, intended in attempts:
        tree = parse(source, CONTROL)
        key = semantic_key(tree, "C")
        rows.append(
            {
                "name": name,
                "source": source,
                "parses": True,
                "canonical": key[0],
                "intended": intended,
                "denotes_intended": key[0] == str(simplify(intended)),
                "free_symbols": tuple(sorted(str(symbol) for symbol in simplify(to_symbolic(tree, "C")).free_symbols)),
            }
        )
    return {
        "rows": tuple(rows),
        "attempts": len(rows),
        "parse_successes": sum(1 for row in rows if row["parses"]),
        "denote_successes": sum(1 for row in rows if row["denotes_intended"]),
    }


def writing_comparison(
    expanded: str, factored: str, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Per grammar, which of two writings of the same object costs fewer bracket pairs.

    Both writings are parsed under ``G0`` - today's notation - to get their intended trees, then
    priced under every grammar with :func:`parseatlas.notational_cost.parenthesis_cost`, which
    verifies its own round trip on every rendering.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    expanded_tree = parse(expanded, CONTROL)
    factored_tree = parse(factored, CONTROL)
    rows = []
    for grammar in grammars:
        left = parenthesis_cost(expanded_tree, grammar)
        right = parenthesis_cost(factored_tree, grammar)
        rows.append(
            {
                "grammar": grammar.id,
                "expanded_cost": left,
                "factored_cost": right,
                "cheaper": "expanded" if left < right else ("factored" if right < left else "tie"),
                "expanded_rendering": render(expanded_tree, grammar),
                "factored_rendering": render(factored_tree, grammar),
            }
        )
    counts = {"expanded": 0, "factored": 0, "tie": 0}
    for row in rows:
        counts[row["cheaper"]] += 1
    return {
        "expanded": expanded,
        "factored": factored,
        "rows": tuple(rows),
        "expanded_cheaper": counts["expanded"],
        "factored_cheaper": counts["factored"],
        "tie": counts["tie"],
        "grammar_count": len(grammars),
    }


def reducibility_table(
    quadratics: Sequence[Quadratic] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Half C: what the wider domain buys for the equivalence, and what it does not buy for the notation."""
    quadratics = tuple(quadratics) if quadratics is not None else QUADRATICS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = []
    for item in quadratics:
        roots = root_report(item.expanded)
        writable = writing_comparison(item.expanded, item.factored, grammars) if item.factored else None
        shape = writing_comparison(item.expanded, item.shape, grammars)
        reciprocal = f"1 / ({item.expanded})"
        reciprocal_tree = parse(reciprocal, CONTROL)
        rows.append(
            {
                "name": item.name,
                "expanded": item.expanded,
                "factored": item.factored,
                "shape": item.shape,
                "stand_ins": item.stand_ins,
                "note": item.note,
                "writable_in_generation_one": item.factored is not None,
                **{key: roots[key] for key in ("roots", "factors_over_Q", "factors_over_R", "factors_over_C")},
                "writing": writable,
                "shape_writing": shape,
                "shape_factored_cheaper": shape["factored_cheaper"],
                "reciprocal": reciprocal,
                "reciprocal_excluded_R": excluded_points(reciprocal_tree, "R"),
                "reciprocal_excluded_C": excluded_points(reciprocal_tree, "C"),
            }
        )
    notation = notation_audit()
    return {
        "rows": tuple(rows),
        "count": len(rows),
        "factor_over_Q": sum(1 for row in rows if row["factors_over_Q"]),
        "factor_over_R": sum(1 for row in rows if row["factors_over_R"]),
        "factor_over_C": sum(1 for row in rows if row["factors_over_C"]),
        "writable_in_generation_one": sum(1 for row in rows if row["writable_in_generation_one"]),
        "notation": notation,
        "domain_buys_equivalence": sum(1 for row in rows if row["factors_over_C"])
        - sum(1 for row in rows if row["factors_over_Q"]),
        "domain_buys_notation": notation["denote_successes"],
        "shape_factored_cheaper": tuple(row["shape_factored_cheaper"] for row in rows),
        "shape_factored_cheaper_constant": len({row["shape_factored_cheaper"] for row in rows}) == 1,
        "reciprocal_gains": sum(
            1 for row in rows if len(row["reciprocal_excluded_C"]) > len(row["reciprocal_excluded_R"])
        ),
    }


# ============================================================================ execution and multicore


#: Item-count floor for a workload whose items cost SECONDS each (a ``simplify`` and a ``solve`` on
#: 25 grammars, or a lattice of exact evaluations).  Two items already pay for a pool.
SECONDS_SCALE_MINIMUM: int = 2

#: Item-count floor for a workload whose items cost MICROSECONDS each (the divisor-signature screen
#: is 25 parses and no SymPy).  Below this a pool costs more than the work it distributes.  The
#: number is not chosen: :func:`screen_crossover` times both paths at a range of item counts and
#: reports the smallest count at which the pool wins, and this constant is the next power of two at
#: or above the measured crossover on this machine.
MICROSECONDS_SCALE_MINIMUM: int = 4096


def resolve_worker_count(
    item_count: int, workers: int | None = None, minimum: int = SECONDS_SCALE_MINIMUM
) -> int:
    """Derive the process count from the observed cores, never from a hardcoded constant."""
    if workers is not None:
        return max(1, min(int(workers), max(item_count, 1)))
    if item_count < minimum:
        return 1
    cores = os.cpu_count() or 1
    return max(1, min(cores - 1, item_count))  # one core of headroom for the interactive session


def screen_crossover(
    counts: Sequence[int] = (500, 1000, 2000, 4000, 8000, 16000),
    operator_count: int = 3,
) -> dict[str, Any]:
    """Where does a process pool start paying for itself on the cheapest workload?

    The screen is `25` parses per source and no SymPy, so a pool's fixed spawn cost dominates until
    the item count is large.  Rather than declaring a floor, the crossing point is measured: both
    paths are timed at a range of item counts and the smallest count at which the pool wins is
    reported.  :data:`MICROSECONDS_SCALE_MINIMUM` is then the next power of two at or above it.
    """
    space = sweep_sources(operator_count)
    cores = os.cpu_count() or 1
    rows = []
    for count in counts:
        subset = space[:count]
        moment = time.perf_counter()
        sequential = _screen(subset, GRAMMARS, 1)
        sequential_seconds = time.perf_counter() - moment
        moment = time.perf_counter()
        parallel = _screen(subset, GRAMMARS, max(1, cores - 1))
        parallel_seconds = time.perf_counter() - moment
        rows.append(
            {
                "items": count,
                "sequential_seconds": sequential_seconds,
                "parallel_seconds": parallel_seconds,
                "speedup": sequential_seconds / parallel_seconds if parallel_seconds else 0.0,
                "parallel_wins": parallel_seconds < sequential_seconds,
                "identical": sequential == parallel,
            }
        )
    winning = [row["items"] for row in rows if row["parallel_wins"]]
    return {
        "rows": tuple(rows),
        "cores": cores,
        "crossover": min(winning) if winning else None,
        "declared_floor": MICROSECONDS_SCALE_MINIMUM,
        "floor_at_or_above_crossover": bool(winning) and MICROSECONDS_SCALE_MINIMUM >= min(winning),
        "identical_everywhere": all(row["identical"] for row in rows),
    }


def parallel_decision(
    corpus: Sequence[Entry] | None = None,
    operator_count: int = 2,
    radius: int = GRID_RADIUS,
    mesh: int = GRID_MESH,
) -> dict[str, Any]:
    """Time both paths over three workloads, check they agree, and record which one won.

    Three workloads that differ by orders of magnitude in per-item cost, each decided on its own
    numbers rather than on one rule:

    * the **half A table** - twelve sources, twenty-five grammars, two domains, each cell a SymPy
      ``simplify`` and a ``solve``;
    * the **half B table** - twelve sources, twenty-five grammars, four conventions, each cell a
      lattice of exact Gaussian-rational evaluations;
    * the **screen** - the divisor-signature pass over the whole sweep space, 25 parses per source
      and no SymPy at all, which is where a process pool can lose.

    All three are CPU-bound pure Python, so processes rather than threads.  Parallelism changes only
    how fast: ``identical`` is asserted on all three.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    cores = os.cpu_count() or 1

    moment = time.perf_counter()
    shift_sequential = domain_shift_table(corpus, workers=1)
    shift_sequential_seconds = time.perf_counter() - moment
    moment = time.perf_counter()
    shift_parallel = domain_shift_table(corpus, workers=max(1, min(cores - 1, len(corpus))))
    shift_parallel_seconds = time.perf_counter() - moment

    moment = time.perf_counter()
    cross_sequential = axis_cross_table(corpus, radius=radius, mesh=mesh, workers=1)
    cross_sequential_seconds = time.perf_counter() - moment
    moment = time.perf_counter()
    cross_parallel = axis_cross_table(
        corpus, radius=radius, mesh=mesh, workers=max(1, min(cores - 1, len(corpus)))
    )
    cross_parallel_seconds = time.perf_counter() - moment

    space = sweep_sources(operator_count)
    moment = time.perf_counter()
    screen_sequential = _screen(space, GRAMMARS, 1)
    screen_sequential_seconds = time.perf_counter() - moment
    moment = time.perf_counter()
    screen_parallel = _screen(space, GRAMMARS, max(1, cores - 1))
    screen_parallel_seconds = time.perf_counter() - moment

    def report(name, items, sequential, parallel, identical, minimum):
        return {
            "workload": name,
            "items": items,
            "sequential_seconds": sequential,
            "parallel_seconds": parallel,
            "speedup": sequential / parallel if parallel else 0.0,
            "parallel_wins": parallel < sequential,
            "declared_minimum": minimum,
            "default_workers": resolve_worker_count(items, minimum=minimum),
            "identical": identical,
        }

    return {
        "cores": cores,
        "workloads": (
            report(
                "half_A_table",
                len(corpus),
                shift_sequential_seconds,
                shift_parallel_seconds,
                shift_sequential["rows"] == shift_parallel["rows"],
                SECONDS_SCALE_MINIMUM,
            ),
            report(
                "half_B_table",
                len(corpus),
                cross_sequential_seconds,
                cross_parallel_seconds,
                cross_sequential["rows"] == cross_parallel["rows"],
                SECONDS_SCALE_MINIMUM,
            ),
            report(
                "sweep_screen",
                len(space),
                screen_sequential_seconds,
                screen_parallel_seconds,
                screen_sequential == screen_parallel,
                MICROSECONDS_SCALE_MINIMUM,
            ),
        ),
    }


def complex_worlds_report(
    corpus: Sequence[Entry] | None = None,
    max_operators: int = 2,
    radius: int = GRID_RADIUS,
    mesh: int = GRID_MESH,
    workers: int | None = None,
) -> dict[str, Any]:
    """Everything this experiment measures, in one structure."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    agreement = agreement_audit(corpus)
    shift = domain_shift_table(corpus, workers=workers)
    sweep = refinement_curve(max_operators, workers=workers)
    cross = axis_cross_table(corpus, radius=radius, mesh=mesh, workers=workers)
    reducibility = reducibility_table()
    constants = constant_class_deficit(corpus)
    return {
        "agreement": agreement,
        "real_solve_leak": real_solve_leak_audit(corpus),
        "domain_shift": shift,
        "sweep": sweep,
        "sympy_default": sympy_default_audit(),
        "straddle": straddle_audit(),
        "straddle_offsets": straddle_offset_sweep(),
        "encoding": encoding_faithfulness_audit(),
        "axis_cross": cross,
        "constant_deficit": constants,
        "agreeing_pairs": agreeing_pairs_audit(corpus, radius=radius, mesh=mesh),
        "reducibility": reducibility,
        "headline": {
            "agreement_cells": agreement["cells"],
            "agreement_failures": agreement["failures"],
            "corpus_partition_unchanged": shift["partition_unchanged"],
            "corpus_strict_sources": shift["strict_count"],
            "corpus_excluded_differs_cells": shift["excluded_differs_cells"],
            "corpus_invisible_excluded_cells": shift["invisible_excluded_cells"],
            "sweep_space": sweep["space"],
            "sweep_strict": sweep["strict_count"],
            "sweep_coarsening": sweep["coarsening_count"],
            "sweep_crossing": sweep["crossing_count"],
            "branch_product": cross["product"],
            "branch_measured": cross["measured"],
            "branch_difference": cross["difference"],
            "branch_predicted_deficit": constants["predicted_deficit"],
            "branch_partition_stable": cross["partition_stable_everywhere"],
            "quadratics_factoring_over_Q": reducibility["factor_over_Q"],
            "quadratics_factoring_over_C": reducibility["factor_over_C"],
            "quadratics_writable_in_generation_one": reducibility["writable_in_generation_one"],
            "domain_buys_notation": reducibility["domain_buys_notation"],
        },
    }
