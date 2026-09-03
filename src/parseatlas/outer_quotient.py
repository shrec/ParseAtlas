"""What an outer function does to the inner semantic equivalence classes.

The founding experiment applied ``sin`` to the token sequence ``2*t + 1 - t/2`` and reported
that the 25 grammars fall into 8 semantic classes.  The owner's question is whether the 8
belongs to ``sin``.  It does not, and the reason is structural rather than empirical.

Two claims, and only one of them is measurable
----------------------------------------------
This module makes a mathematical claim and a measured claim.  They are different claims, they
had different fates, and conflating them is what made the first version of this experiment
wrong.  They are therefore stated apart, here and in the report.

**The mathematical claim.**  Fix a token sequence ``S``.  Every grammar ``g`` parses ``S`` into
an AST ``A_g`` whose denotation ``v_g`` is a partial function on the reals.  The **inner
partition** is the kernel of ``g -> v_g``: two grammars share an inner class exactly when they
denote the same function.  Now let ``f`` be any outer function.  Function application is, by
definition, a function of its argument::

    v_g == v_h   =>   f . v_g == f . v_h

so grammars that already agreed still agree after ``f``.  The relation "same value after ``f``"
therefore *contains* the relation "same value", which is to say the inner partition **refines**
the outer one and the outer partition is a **coarsening** -- a quotient -- of the inner one.
Two consequences follow immediately:

* ``C_f(S) <= C_inner(S)`` for every ``f`` and every ``S``.  An outer function can merge inner
  classes; it can never split one.
* equality holds exactly when ``f`` is injective on the finite set of values ``{v_g}``.  Which
  classes merge is decided by the identities of ``f`` on that set and by nothing else.

So the 8 is a property of ``2*t + 1 - t/2``, and each outer function contributes its own
quotient of that 8.  The mechanisms available to ``f`` are few and are named per merged pair by
:func:`merge_mechanism`: a *period* (``sin``/``cos`` at ``2*pi``, ``tan`` at ``pi``), an
*even parity* identity (``cos``, ``abs``, ``square`` all identify ``a`` with ``-a``), a
*constant collapse* of the argument, or -- for the injective functions -- nothing at all.
That is a one-line proof and this module does not pretend to add to it.

**The measured claim.**  ParseAtlas never compares denotations directly.  It compares a
canonical triple ``(canonical form, domain, excluded points)``, and the mathematics above
transfers to the *measured* partitions only if that triple is a function of the denoted value
rather than of the parse tree.  What :func:`quotient_check` tests is the key, not the theorem.
A coarsening violation does not refute the mathematics; it shows that the canonical key --
inner, outer, or both -- carries syntax it should not.

The measured claim was false, and the direction it fails in
-----------------------------------------------------------
It fails by **splitting**.  This is worth stating flatly, because the earlier reading of the
result had it backwards.  The outer key's domain slot is finer-grained than the inner key's
constant ``"R"``, and a strictly finer slot is not a stronger test of a coarsening -- it is the
only thing that can break one.  Splitting is the failure mode a finer key makes available, so
``C_f(S) > C_inner(S)`` and a negative class-count delta are the shapes to watch for.

The concrete defect, recorded as **NF-2026-00004**, was in
:func:`parseatlas.functions._property_summary`: it composed the outer function on the **raw**
``to_sympy(parse(source, grammar))`` before taking ``continuous_domain``, while the canonical
slot beside it and the whole inner key used ``simplify``.  Two grammars denoting the same value
but leaving different SymPy trees -- ``(6 - 3*t)/(2 - t)`` against ``Integer(3)``, a removable
singularity one reading cancels at construction and the other does not -- got the same canonical
string and *different* domains, so one inner class landed in two outer classes.  Minimal
reproducer, still in :data:`CORPUS` so that it is measured on every run::

    quotient_check("3 * 2 - t / 2 - t", "log")   # pre-fix: is_coarsening False, C_inner 4, C_f 5

Both readings carry the identical excluded point ``2``, so the parse-tree-level validity
restriction was never in dispute; only the slot that was supposed to describe the value
disagreed.  The fix composes the domain on the canonicalised argument, leaving the removable
singularity where it belongs, in the excluded-points slot.

The first version of this experiment reported 0 violations in 260 corpus pairs and read that as
support for the claim.  It was not: every inner class in that corpus happened to have
srepr-identical raw expressions across its grammars, so the outer key was trivially constant on
each inner class and the decisive check could not fire.  A zero from a check that cannot fire is
a fact about the corpus, not about the key.  :data:`CORPUS` now contains residue sources chosen
so that it can.

The converse failure mode is silent and cannot be detected from inside: if SymPy fails to
canonicalise a genuine identity, two classes that *are* equal after ``f`` keep distinct keys and
the merge is simply missed.  Every merge count here is therefore a lower bound.

Corpus
------
:data:`CORPUS` is the founding sequence plus twenty-three more, spanning affine, quadratic,
rational and mixed-chain shapes, and -- since NF-2026-00004 -- four **residue sources** whose
grammars denote one value through structurally different SymPy trees.  The residue sources are
the only ones that exercise the coarsening check non-vacuously, so they are not optional
colour; without them the load-bearing test asserts nothing.  Every source uses the variable
``t`` because :func:`parseatlas.functions.analyze_outer_functions` differentiates with respect
to ``t`` when it reports frequency and period; a source in another variable would be reported as
having a constant argument.

A structural remark that the corpus makes unavoidable: the token language admits only rational
literals, so any two readings of one token sequence differ by a rational function over the
rationals, while every period of ``sin``, ``cos`` and ``tan`` is an irrational multiple of ``pi``.
The *period* mechanism is consequently unreachable from precedence variation alone, and the
measurement confirms it.  :func:`merge_mechanism` still detects periods -- it is exercised on
directly constructed arguments -- because the absence has to be measured rather than assumed.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from typing import Any

from sympy import Expr, S, Symbol, pi, simplify, solveset
from sympy.calculus.util import continuous_domain

from .analyze import analyze_expression
from .canonical import to_sympy
from .functions import OUTER_FUNCTIONS, analyze_outer_functions, canonical_argument
from .grammar import Grammar, all_grammars
from .parser import parse

VARIABLE = Symbol("t", real=True)

#: The founding inner token sequence of experiment 0002.
FOUNDING_SOURCE = "2*t + 1 - t/2"

#: Twenty-four inner token sequences: the founding one plus twenty-three more.
#:
#: ``affine`` covers the shapes the founding experiment used; the ``c - c + ...`` sources are
#: chosen deliberately because they are the only shape in this language that produces a class and
#: its exact negation (``(c - c) + u == u`` against ``c - (c + u) == -u``), which is what makes
#: the even-parity mechanism observable at all.  ``rational`` and ``mixed`` sources bring
#: excluded points and moving real-domain boundaries into the corpus.
#:
#: The ``residue`` block is the one that makes the coarsening check non-vacuous, and it was added
#: only after NF-2026-00004.  In each of these sources at least two grammars denote the *same*
#: value through structurally different SymPy trees -- one reading cancels a removable
#: singularity at construction, another does not -- so the outer key is genuinely varying inside
#: an inner class and a key that reads syntax will split it.  The first three are paren-free
#: (the residue comes from precedence alone, not from bracketing); the fourth is an uncancelled
#: quotient whose numerator and denominator share a factor.
CORPUS: tuple[str, ...] = (
    # affine
    "2*t + 1 - t/2",
    "1 - 2 + t",
    "3*t - 2 + 1",
    "t/2 + 1 - 2*t",
    "1 + 2*t - 3",
    # affine, negation-producing
    "2 - 2 + t",
    "4 - 4 + 3*t",
    # quadratic
    "2*t*t + 1 - t/2",
    "t*t - 3*t + 2",
    "t*t*2 - t - 1",
    # quadratic, negation-producing
    "3 - 3 + t*t",
    # rational
    "(t + 1)/(t - 2)",
    "1/t + 2 - t",
    "t/t + 2*t - 1",
    "2/t - 1/t + t",
    "t/(t + 1) - 2",
    # rational, negation-producing
    "5 - 5 + 1/t",
    # mixed chains
    "1 - 2*t/4 + 3*t",
    "2*t*3 - 4/t + 1",
    "1 - t/2*2 + t",
    # residue: one denoted value, structurally different parse trees (NF-2026-00004)
    "3 * 2 - t / 2 - t",
    "1 + t + t * 2 / t",
    "t * t - 3 / 2",
    "2*(t - 1)/(t - 1)",
)

#: A cheap slice of :data:`CORPUS` for tests that do not need the whole sweep.
SUB_CORPUS: tuple[str, ...] = ("2*t + 1 - t/2", "2 - 2 + t", "1 - 2 + t", "5 - 5 + 1/t")

#: The declared algebra of each outer function, used to *predict* whether it can merge.
#:
#: These are claims about the function on the reals, written down before the sweep so that the
#: measurement can agree or disagree with them.  ``period`` is the period of ``f`` itself, which
#: is the quantity a merge needs: ``f(u) == f(u + period)``.  The period of the *composition*
#: ``t -> f(a*t + b)`` is ``period / |a|`` and is computed by :func:`argument_period`.
FUNCTION_ALGEBRA: dict[str, dict[str, Any]] = {
    "sin": {"period": 2 * pi, "even": False, "odd": True, "injective_on_reals": False},
    "cos": {"period": 2 * pi, "even": True, "odd": False, "injective_on_reals": False},
    "tan": {"period": pi, "even": False, "odd": True, "injective_on_reals": False},
    "exp": {"period": None, "even": False, "odd": False, "injective_on_reals": True},
    "log": {"period": None, "even": False, "odd": False, "injective_on_reals": True},
    "sqrt": {"period": None, "even": False, "odd": False, "injective_on_reals": True},
    "abs": {"period": None, "even": True, "odd": False, "injective_on_reals": False},
    "asin": {"period": None, "even": False, "odd": True, "injective_on_reals": True},
    "acos": {"period": None, "even": False, "odd": False, "injective_on_reals": True},
    "atan": {"period": None, "even": False, "odd": True, "injective_on_reals": True},
    "reciprocal": {"period": None, "even": False, "odd": True, "injective_on_reals": True},
    "square": {"period": None, "even": True, "odd": False, "injective_on_reals": False},
    "cube": {"period": None, "even": False, "odd": True, "injective_on_reals": True},
}

#: Functions whose singular behaviour experiment 0002 reported qualitatively.
SINGULARITY_FUNCTIONS: tuple[str, ...] = ("tan", "log", "sqrt", "reciprocal")

WORKER_HEADROOM_CORES = 2
WORKER_CAP = 12


def worker_count_for(cores: int) -> int:
    """Worker count for a machine with ``cores`` cores.

    ``WORKER_HEADROOM_CORES`` cores stay free so a corpus sweep cannot starve an interactive
    session, and ``WORKER_CAP`` bounds the spawn cost a 312-pair sweep can amortise.  The result
    is never zero and never exceeds the core count, so it is safe on any machine.
    """
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP))


def default_worker_count() -> int:
    """Worker count derived from the **observed** core count, never a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1)


# ---------------------------------------------------------------------------
# Keys
# ---------------------------------------------------------------------------


def _inner_key(canonical: str, domain: str, excluded: Sequence[str]) -> tuple[str, str, tuple[str, ...]]:
    return (canonical, domain, tuple(excluded))


def _outer_key(canonical: str, domain: str, excluded: Sequence[str]) -> tuple[str, str, tuple[str, ...]]:
    """The outer key uses the same triple discipline as the inner one.

    ``domain`` is the only slot that changes meaning.  Inner canonicalisation stamps the constant
    ``"R"`` there; after an outer function the real domain is genuinely informative -- it is where
    ``log`` and ``sqrt`` record their boundary and where ``tan`` records its poles -- so the
    outer key carries ``continuous_domain`` of the composed expression instead.

    That makes the outer key strictly **finer** than the inner one, and finer is not safer.  An
    earlier version of this docstring called it "stricter ... which is the direction that
    matters: a coarsening that survives a stricter key is the stronger result".  That is exactly
    backwards, and NF-2026-00004 is the counterexample.  A coarsening can only fail by splitting,
    splitting can only be caused by a key that separates grammars the inner key joined, and the
    domain slot is the *only* slot with that power here.  A finer outer key is therefore the sole
    hazard to the claim, not extra evidence for it.

    Which is why the slot has one hard requirement: it must be a function of the denoted value.
    ``functions.py`` composes the outer function on the canonicalised argument so that it is.  If
    it ever again reads the raw parse tree, this key manufactures splits and
    :func:`quotient_check` reports them.
    """
    return (canonical, domain, tuple(excluded))


def class_representative(source: str, grammar_id: str, grammars: tuple[Grammar, ...] | None = None) -> Expr:
    """The denoted value of one grammar, as a SymPy expression over the **real** symbol ``t``.

    Public because the canonical strings this module reports round-trip through ``sympify`` as a
    plain symbol, and a plain ``t`` is not the ``t`` that :func:`argument_period` differentiates
    against.  Callers that need the value, rather than its printed form, come through here.
    """
    grammars = grammars or all_grammars()
    grammar = next(item for item in grammars if item.id == grammar_id)
    return simplify(to_sympy(parse(source, grammar)))


# ---------------------------------------------------------------------------
# Partitions
# ---------------------------------------------------------------------------


def inner_partition(source: str, grammars: tuple[Grammar, ...] | None = None) -> dict[str, Any]:
    """The partition of the 25 grammars by inner semantic class.

    This is exactly the ``equivalence_classes`` of :func:`parseatlas.analyze.analyze_expression`,
    re-presented as a partition with a SymPy representative and a constant-argument flag per
    class.  Reusing that function rather than regrouping by hand is deliberate: the inner class
    must be the same object the rest of ParseAtlas means by "inner class", or the comparison with
    the outer partition measures two different things.
    """
    grammars = grammars or all_grammars()
    report = analyze_expression(source, grammars)
    classes = []
    for item in report["equivalence_classes"]:
        representative = class_representative(source, item["grammars"][0], grammars)
        classes.append(
            {
                "id": item["id"],
                "key": _inner_key(item["canonical"], item["domain"], item["excluded_points"]),
                "canonical": item["canonical"],
                "domain": item["domain"],
                "excluded_points": list(item["excluded_points"]),
                "grammars": list(item["grammars"]),
                "representative": str(representative),
                "constant_argument": bool(simplify(representative.diff(VARIABLE)) == 0),
            }
        )
    class_by_grammar = {grammar_id: item["id"] for item in classes for grammar_id in item["grammars"]}
    return {
        "source": source,
        "grammar_count": len(grammars),
        "class_count": len(classes),
        "classes": classes,
        "class_by_grammar": class_by_grammar,
    }


def outer_partition(source: str, function_name: str, grammars: tuple[Grammar, ...] | None = None) -> dict[str, Any]:
    """The partition of the same grammars after applying ``function_name``.

    The outer layer is not reimplemented here: :func:`parseatlas.functions.analyze_outer_functions`
    produces the composed canonical form and the domain facts, and this function only groups its
    per-grammar rows by the outer key.  Every domain and period figure reported downstream is
    therefore the one ``functions.py`` computes, not a second opinion.
    """
    if function_name not in OUTER_FUNCTIONS:
        raise ValueError(f"Unknown outer function: {function_name}")
    grammars = grammars or all_grammars()
    report = analyze_outer_functions(source, (function_name,), grammars)
    grouped: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    for item in report["results"]:
        properties = item["properties"]
        key = _outer_key(item["canonical"], properties["real_domain"], item["inner_excluded_points"])
        cell = grouped.setdefault(
            key,
            {
                "key": key,
                "canonical": item["canonical"],
                "domain": properties["real_domain"],
                "excluded_points": list(item["inner_excluded_points"]),
                "inner_real_domain": properties["inner_real_domain"],
                "constant_argument": bool(properties["constant_argument"]),
                "frequency": properties.get("frequency"),
                "period": properties.get("period"),
                "grammars": [],
            },
        )
        cell["grammars"].append(item["grammar"])
    classes = []
    for index, cell in enumerate(grouped.values(), start=1):
        classes.append({"id": f"F{index:02d}", **cell})
    class_by_grammar = {grammar_id: item["id"] for item in classes for grammar_id in item["grammars"]}
    return {
        "source": source,
        "function": function_name,
        "grammar_count": len(grammars),
        "class_count": len(classes),
        "classes": classes,
        "class_by_grammar": class_by_grammar,
    }


# ---------------------------------------------------------------------------
# Mechanisms
# ---------------------------------------------------------------------------


def argument_period(function_name: str, expression: Expr, variable: Symbol = VARIABLE) -> Expr | None:
    """Period in ``t`` of ``t -> f(expression(t))`` when ``expression`` is affine and non-constant.

    ``2*pi/|a|`` for ``sin`` and ``cos``, ``pi/|a|`` for ``tan``, where ``a`` is the slope.  This
    is the independent restatement of the rule ``functions.py`` implements, and the test suite
    holds the two against each other so the tangent case cannot silently regress to ``2*pi/|a|``.
    Returns ``None`` for an aperiodic ``f``, a constant argument, or a non-affine argument.
    """
    base = FUNCTION_ALGEBRA[function_name]["period"]
    if base is None:
        return None
    slope = simplify(expression.diff(variable))
    if slope == 0 or not slope.free_symbols.isdisjoint({variable}):
        return None
    return simplify(base / abs(slope))


def _integer_multiple(difference: Expr, base: Expr, allow_zero: bool = False) -> Expr | None:
    """``k`` when ``difference == k * base`` for an integer ``k``, else ``None``.

    ``k == 0`` is rejected by default because a zero difference is not a period merge; the sine
    reflection identity ``sin(a) == sin(pi - a + 2*pi*k)`` is the one caller that needs ``k == 0``
    to count, since ``pi - a`` on its own is already a merge.
    """
    ratio = simplify(difference / base)
    if ratio.is_Integer and (allow_zero or ratio != 0):
        return ratio
    return None


def merge_mechanism(function_name: str, left: Expr, right: Expr, variable: Symbol = VARIABLE) -> dict[str, Any]:
    """Name the identity of ``f`` that makes ``f(left)`` and ``f(right)`` the same function.

    The checks run in the order period, even parity, sine reflection, cosine parity-period,
    constant collapse, because that is the order of decreasing specificity: a pair that differs by
    a period is reported as a period merge even when ``f`` also happens to be even, and a plain
    negation is reported as parity rather than as the ``k = 0`` case of the shifted cosine
    identity.  A pair the classifier cannot explain is
    returned as ``"unclassified"`` with the raw difference and sum, which is the honest outcome and
    a signal that :data:`FUNCTION_ALGEBRA` is missing an identity.
    """
    algebra = FUNCTION_ALGEBRA[function_name]
    difference = simplify(right - left)
    total = simplify(right + left)
    if difference == 0:
        return {"mechanism": "identical", "detail": "the two arguments are the same function"}
    if algebra["period"] is not None:
        multiple = _integer_multiple(difference, algebra["period"])
        if multiple is not None:
            return {
                "mechanism": "period",
                "detail": f"argument difference {difference} = {multiple} * {algebra['period']}",
            }
    if algebra["even"] and total == 0:
        return {"mechanism": "parity", "detail": f"{function_name} is even and {right} = -({left})"}
    if function_name == "sin":
        multiple = _integer_multiple(simplify(total - pi), 2 * pi, allow_zero=True)
        if multiple is not None:
            return {"mechanism": "reflection", "detail": f"sin identity: {right} = pi - ({left}) + {multiple}*2*pi"}
    if function_name == "cos" and algebra["period"] is not None:
        multiple = _integer_multiple(total, algebra["period"])
        if multiple is not None:
            return {"mechanism": "parity-period", "detail": f"cos identity: {right} = -({left}) + {multiple}*2*pi"}
    constant_left = variable not in left.free_symbols
    constant_right = variable not in right.free_symbols
    if constant_left and constant_right:
        return {
            "mechanism": "constant collapse",
            "detail": f"both arguments collapsed to constants ({left}, {right}) and {function_name} identifies them",
        }
    return {"mechanism": "unclassified", "detail": f"difference {difference}, sum {total}"}


# ---------------------------------------------------------------------------
# The coarsening check
# ---------------------------------------------------------------------------


def quotient_check(source: str, function_name: str, grammars: tuple[Grammar, ...] | None = None) -> dict[str, Any]:
    """Verify directly that the ``f``-partition is a coarsening of the inner partition.

    Every inner class must land inside exactly one outer class.  An inner class whose grammars
    reach two or more outer classes is a **violation** and is reported in full -- the inner key,
    the grammars, and each outer key they reached -- rather than being smoothed over.  A violation
    means one of the two canonical keys depends on the parse tree and not on the denoted value;
    it is the finding this experiment most wants to hear about, and NF-2026-00004 is one it found.

    Merge accounting on a violating pair
    ------------------------------------
    ``merge_count`` is ``None`` when ``is_coarsening`` is false, and ``merges`` is empty.  This is
    deliberate and it is the second half of the NF-2026-00004 fix.  The obvious definition,
    ``C_inner - C_f``, is only a merge count while the inner-to-outer map is a function: on a
    split it goes *negative* and the negative then flows into every aggregate downstream, where it
    cancels genuine merges and turns the summary silently wrong exactly when the most important
    finding has fired.  Measured on the pre-fix sweep: ``total_merges`` ``-130``, ``tan`` at a mean
    of ``-1.088``, and ``merges_anywhere`` false for ``cos``, ``abs`` and ``square`` although each
    of the three had a real parity merge in the same run.

    So ``merge_count`` is derived from the merge structure instead -- the number of inner classes
    absorbed into shared outer classes -- and it is reported only for a pair whose partition
    actually is a quotient.  Where the two definitions are both meaningful they agree, and the
    test suite pins that.  The raw difference stays available as ``class_count_delta``, which is
    a diagnostic and not a merge count: it is negative precisely on a split, and ``split_count``
    says how many inner classes were torn apart.
    """
    grammars = grammars or all_grammars()
    inner = inner_partition(source, grammars)
    outer = outer_partition(source, function_name, grammars)

    reached: dict[str, dict[str, list[str]]] = {}
    for item in inner["classes"]:
        buckets: dict[str, list[str]] = {}
        for grammar_id in item["grammars"]:
            buckets.setdefault(outer["class_by_grammar"][grammar_id], []).append(grammar_id)
        reached[item["id"]] = buckets

    inner_by_id = {item["id"]: item for item in inner["classes"]}
    outer_by_id = {item["id"]: item for item in outer["classes"]}

    violations = [
        {
            "inner_class": inner_id,
            "inner_canonical": inner_by_id[inner_id]["canonical"],
            "inner_key": list(inner_by_id[inner_id]["key"]),
            "outer_classes": [
                {"outer_class": outer_id, "outer_key": list(outer_by_id[outer_id]["key"]), "grammars": grammar_ids}
                for outer_id, grammar_ids in buckets.items()
            ],
        }
        for inner_id, buckets in reached.items()
        if len(buckets) > 1
    ]

    contents: dict[str, list[str]] = {}
    for inner_id, buckets in reached.items():
        for outer_id in buckets:
            contents.setdefault(outer_id, []).append(inner_id)

    is_coarsening = not violations

    # A violating pair has no trustworthy merge structure: an inner class that reaches two outer
    # classes appears under both, so "outer class holding two inner classes" no longer means the
    # two were identified.  Refusing to name merges here is what keeps the aggregates honest.
    merges = []
    for outer_id, inner_ids in (contents.items() if is_coarsening else ()):
        if len(inner_ids) < 2:
            continue
        representatives = [class_representative(source, inner_by_id[i]["grammars"][0], grammars) for i in inner_ids]
        mechanisms = [
            {
                "from": inner_ids[index],
                "into": inner_ids[0],
                "from_canonical": inner_by_id[inner_ids[index]]["canonical"],
                "into_canonical": inner_by_id[inner_ids[0]]["canonical"],
                **merge_mechanism(function_name, representatives[0], representatives[index]),
            }
            for index in range(1, len(inner_ids))
        ]
        merges.append(
            {
                "outer_class": outer_id,
                "outer_canonical": outer_by_id[outer_id]["canonical"],
                "outer_domain": outer_by_id[outer_id]["domain"],
                "inner_classes": inner_ids,
                "inner_canonicals": [inner_by_id[i]["canonical"] for i in inner_ids],
                "mechanisms": mechanisms,
            }
        )

    return {
        "source": source,
        "function": function_name,
        "inner_class_count": inner["class_count"],
        "outer_class_count": outer["class_count"],
        "merge_count": sum(len(item["inner_classes"]) - 1 for item in merges) if is_coarsening else None,
        "class_count_delta": inner["class_count"] - outer["class_count"],
        "split_count": len(violations),
        "is_coarsening": is_coarsening,
        "violations": violations,
        "merges": merges,
        "inner_classes": inner["classes"],
        "outer_classes": outer["classes"],
    }


def _pair_task(payload: tuple[str, str]) -> dict[str, Any]:
    """Module-level pool entry point: required by the Windows ``spawn`` start method."""
    source, function_name = payload
    record = quotient_check(source, function_name)
    # The per-class representative is a SymPy object only inside the worker; strings cross back.
    for item in record["inner_classes"]:
        item["key"] = list(item["key"])
    for item in record["outer_classes"]:
        item["key"] = list(item["key"])
    return record


def _run_pairs(sources: Sequence[str], functions: Sequence[str], workers: int | None) -> list[dict[str, Any]]:
    """Evaluate every ``(source, function)`` pair, sequentially or across processes.

    Every pair is an independent pure computation, so the sweep is parallel by default; the
    sequential path exists only for tests and for ``workers=1``.  ``executor.map`` preserves input
    order and the tasks share no state, so the two paths return identical records -- which the
    test suite asserts rather than assumes.
    """
    payloads = [(source, function_name) for source in sources for function_name in functions]
    resolved = default_worker_count() if workers is None else workers
    if resolved <= 1 or len(payloads) == 1:
        return [_pair_task(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=resolved) as executor:
        return list(executor.map(_pair_task, payloads, chunksize=1))


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def merge_report(
    sources: Iterable[str] | None = None,
    functions: Iterable[str] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Per-pair and per-function record of what each outer function does to the inner classes.

    Per ``(source, function)``: ``C_inner``, ``C_outer``, the merge count, which inner classes
    merged and into what, and the mechanism where one is identifiable.  Per function: how often it
    merges, the mean merge count over the corpus, the mechanism histogram, and -- the load-bearing
    field -- ``coarsening_failures``, the number of pairs where an inner class did *not* stay
    inside a single outer class.

    Every merge aggregate here is taken over the pairs that are coarsenings, and only those.  A
    violating pair contributes to ``coarsening_failures`` and to nothing else, because a pair
    whose partition is not a quotient has no merge count to contribute (see
    :func:`quotient_check`).  ``mean_merge_count`` is consequently a mean over
    ``coarsening_pairs``, not over ``sources``, and the two differ exactly when something broke.
    ``merge_evidence_complete`` says whether a function's merge figures were measured on a clean
    sweep; ``capability_unrealised`` requires it, because "never merged anywhere" is not a
    conclusion you may draw from a sweep with pairs you could not measure.
    """
    sources = tuple(sources) if sources is not None else CORPUS
    functions = tuple(functions) if functions is not None else tuple(OUTER_FUNCTIONS)
    if not sources:
        raise ValueError("merge_report needs at least one source: an empty corpus measures nothing")
    unknown = set(functions) - set(OUTER_FUNCTIONS)
    if unknown:
        raise ValueError(f"Unknown outer functions: {', '.join(sorted(unknown))}")

    records = _run_pairs(sources, functions, workers)

    pairs = []
    per_function: dict[str, dict[str, Any]] = {
        name: {
            "function": name,
            "sources": 0,
            "coarsening_pairs": 0,
            "sources_with_merge": 0,
            "total_inner_classes": 0,
            "total_outer_classes": 0,
            "total_merges": 0,
            "max_merge_count": 0,
            "coarsening_failures": 0,
            "mechanisms": {},
            "predicted_can_merge": not FUNCTION_ALGEBRA[name]["injective_on_reals"],
        }
        for name in functions
    }
    for record in records:
        cell = per_function[record["function"]]
        cell["sources"] += 1
        cell["total_inner_classes"] += record["inner_class_count"]
        cell["total_outer_classes"] += record["outer_class_count"]
        cell["coarsening_failures"] += 0 if record["is_coarsening"] else 1
        if record["is_coarsening"]:
            cell["coarsening_pairs"] += 1
            cell["total_merges"] += record["merge_count"]
            cell["max_merge_count"] = max(cell["max_merge_count"], record["merge_count"])
            cell["sources_with_merge"] += 1 if record["merge_count"] else 0
            for merge in record["merges"]:
                for mechanism in merge["mechanisms"]:
                    name = mechanism["mechanism"]
                    cell["mechanisms"][name] = cell["mechanisms"].get(name, 0) + 1
        pairs.append(
            {
                "source": record["source"],
                "function": record["function"],
                "inner_class_count": record["inner_class_count"],
                "outer_class_count": record["outer_class_count"],
                "merge_count": record["merge_count"],
                "class_count_delta": record["class_count_delta"],
                "split_count": record["split_count"],
                "is_coarsening": record["is_coarsening"],
                "violations": record["violations"],
                "merges": record["merges"],
            }
        )
    for cell in per_function.values():
        # Denominator is the measurable pairs, not every pair: averaging a merge count over pairs
        # that have no merge count is how the pre-fix summary produced -1.088 merges per source.
        cell["mean_merge_count"] = cell["total_merges"] / cell["coarsening_pairs"] if cell["coarsening_pairs"] else 0.0
        cell["merges_anywhere"] = cell["total_merges"] > 0
        # Whether the merge figures above rest on a sweep with nothing unmeasurable in it.
        cell["merge_evidence_complete"] = cell["coarsening_failures"] == 0
        # A function that owns a merging identity but never fires it on this corpus.  For the
        # periodic functions this is not a gap in the corpus: the language has only rational
        # literals, so no two readings can differ by an irrational period.  The claim needs
        # complete evidence: with unmeasurable pairs in the sweep, "never merged" is not known.
        cell["capability_unrealised"] = cell["predicted_can_merge"] and not cell["merges_anywhere"] and cell["merge_evidence_complete"]
        # An injective function that merged would contradict :data:`FUNCTION_ALGEBRA`.
        cell["contradicts_algebra"] = cell["merges_anywhere"] and not cell["predicted_can_merge"]

    return {
        "sources": list(sources),
        "functions": list(functions),
        "pair_count": len(pairs),
        "pairs": pairs,
        "per_function": per_function,
        "coarsening_holds_everywhere": all(pair["is_coarsening"] for pair in pairs),
        "coarsening_failures": sum(0 if pair["is_coarsening"] else 1 for pair in pairs),
        "coarsening_pairs": sum(1 if pair["is_coarsening"] else 0 for pair in pairs),
        # The shape a broken key produces: the outer partition is finer than the inner one.
        "split_pairs": sum(1 for pair in pairs if pair["outer_class_count"] > pair["inner_class_count"]),
        "total_merges": sum(pair["merge_count"] for pair in pairs if pair["is_coarsening"]),
        "worker_count": default_worker_count() if workers is None else workers,
    }


# ---------------------------------------------------------------------------
# Singularities and domains
# ---------------------------------------------------------------------------


def _real_zero_set(expression: Expr, variable: Symbol = VARIABLE) -> str:
    try:
        return str(solveset(expression, variable, S.Reals))
    except (NotImplementedError, ValueError, TypeError):
        return "undetermined"


def singularity_and_domain_effects(
    sources: Iterable[str] | None = None,
    functions: Iterable[str] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The qualitative half of the founding experiment, counted.

    ``tan``
        whether the variable-dependent poles disappear when the argument collapses to a constant.
        A constant argument makes ``tan`` of it a constant, so ``continuous_domain`` returns the
        whole line; a non-constant affine argument leaves an infinite pole family.
    ``log`` and ``sqrt``
        how far the real-domain boundary moves across grammars of one token sequence: the number
        of distinct boundaries observed, and which classes sit at them.
    ``reciprocal``
        whether poles move or vanish: the real zero set of each inner class is the pole set of the
        reciprocal, so a class with a non-vanishing constant argument has none at all.
    """
    sources = tuple(sources) if sources is not None else CORPUS
    functions = tuple(functions) if functions is not None else SINGULARITY_FUNCTIONS
    requested = tuple(name for name in functions if name in SINGULARITY_FUNCTIONS)
    if not requested:
        raise ValueError(f"singularity_and_domain_effects needs at least one of {SINGULARITY_FUNCTIONS}")

    records = _run_pairs(sources, requested, workers)
    grammars = all_grammars()

    per_source = []
    totals = {
        "tan_classes_with_poles": 0,
        "tan_classes_without_poles": 0,
        "tan_pole_vanishing_cases": [],
        "log_boundary_moves": 0,
        "sqrt_boundary_moves": 0,
        "reciprocal_pole_moves": 0,
        "reciprocal_pole_vanishing_cases": [],
        "domain_undetermined": 0,
    }
    for record in records:
        source, function_name = record["source"], record["function"]
        cell: dict[str, Any] = {"source": source, "function": function_name, "classes": []}
        boundaries: list[str] = []
        pole_sets: list[str] = []
        for item in record["outer_classes"]:
            entry = {
                "outer_class": item["id"],
                "canonical": item["canonical"],
                "real_domain": item["domain"],
                "constant_argument": item["constant_argument"],
                "grammars": item["grammars"],
                "unrestricted": item["domain"] == "Reals",
            }
            if item["domain"] == "undetermined":
                totals["domain_undetermined"] += 1
            if function_name == "tan":
                if entry["unrestricted"]:
                    totals["tan_classes_without_poles"] += 1
                    totals["tan_pole_vanishing_cases"].append(
                        {"source": source, "outer_class": item["id"], "canonical": item["canonical"], "grammars": item["grammars"]}
                    )
                else:
                    totals["tan_classes_with_poles"] += 1
            if function_name == "reciprocal":
                inner = class_representative(source, item["grammars"][0], grammars)
                zeros = _real_zero_set(inner, VARIABLE)
                entry["pole_set"] = zeros
                pole_sets.append(zeros)
                if zeros in {"EmptySet", "{}"}:
                    totals["reciprocal_pole_vanishing_cases"].append(
                        {"source": source, "outer_class": item["id"], "canonical": item["canonical"], "grammars": item["grammars"]}
                    )
            if function_name in {"log", "sqrt"}:
                boundaries.append(item["domain"])
            cell["classes"].append(entry)
        cell["distinct_real_domains"] = len(dict.fromkeys(item["domain"] for item in record["outer_classes"]))
        if function_name in {"log", "sqrt"}:
            cell["distinct_boundaries"] = len(dict.fromkeys(boundaries))
            if cell["distinct_boundaries"] > 1:
                totals[f"{function_name}_boundary_moves"] += 1
        if function_name == "reciprocal":
            cell["distinct_pole_sets"] = len(dict.fromkeys(pole_sets))
            if cell["distinct_pole_sets"] > 1:
                totals["reciprocal_pole_moves"] += 1
        per_source.append(cell)

    return {
        "sources": list(sources),
        "functions": list(requested),
        "per_source": per_source,
        "totals": totals,
        "worker_count": default_worker_count() if workers is None else workers,
    }


def outer_real_domain(source: str, function_name: str, grammar_id: str) -> str:
    """Real domain of ``f`` applied to one grammar's reading, straight from ``functions.py``.

    A small named accessor so the report and the tests can quote a single concrete case without
    re-deriving the composed domain by hand.  It composes on
    :func:`parseatlas.functions.canonical_argument` for the same reason ``functions.py`` does: an
    accessor that read the raw parse tree would quote a different number from the one the atlas
    publishes, which is how NF-2026-00004 stayed invisible in the first place.
    """
    grammars = all_grammars()
    grammar = next(item for item in grammars if item.id == grammar_id)
    argument = canonical_argument(to_sympy(parse(source, grammar)))
    try:
        return str(continuous_domain(OUTER_FUNCTIONS[function_name](argument), VARIABLE, S.Reals))
    except (NotImplementedError, ValueError):
        return "undetermined"
