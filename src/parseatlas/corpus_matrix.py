"""Corpus-scale grammar agreement matrix, support-reduction null model and cluster structure.

Experiment 0024. Three things separate this module from :mod:`parseatlas.grammar_matrix`:

* it runs a deterministic parameterized corpus of thousands of expressions instead of a handful;
* it never calls :func:`parseatlas.analyze.analyze_expression` in the hot loop - the 25 grammars are
  first grouped by *serialized AST* and each DISTINCT AST is canonicalized exactly once;
* it reports a support-reduction NULL matrix next to the observed matrix, so that agreement which is
  mechanically forced by :mod:`parseatlas.support_reduction` is never mistaken for structure.
"""

import json
import os
import time
from collections import Counter
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from math import sqrt
from typing import Any

from .canonical import ast_to_dict, canonicalize
from .grammar import Grammar, all_grammars
from .grammar_matrix import representation_sensitivity
from .parser import parse
from .support_reduction import operator_support

#: The 25 registered grammars: the tied-level control ``G0`` plus the 24 strict orderings.
GRAMMARS: tuple[Grammar, ...] = all_grammars()
GRAMMAR_IDS: tuple[str, ...] = tuple(grammar.id for grammar in GRAMMARS)

#: Small integer coefficient set. ``0`` and negative integers are excluded on purpose: the
#: Generation 1 tokenizer has no unary minus, and ``0`` would make the ``{d}``/``{b}``/``{a}``
#: denominators of the rational and mixed_chain templates undefined.
COEFFICIENT_VALUES: tuple[int, ...] = (1, 2, 3, 4, 5)
PARAMETER_NAMES: tuple[str, ...] = ("a", "b", "c", "d")

FAMILY_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("linear", "{a}*x + {b} - {c}*x/{d}"),
    ("quadratic", "{a}*x*x + {b}*x - {c}/{d}"),
    ("cubic", "{a}*x*x*x + {b}*x*x - {c}*x + {d}"),
    ("rational", "({a}*x + {b})/({c}*x - {d})"),
    ("mixed_chain", "{a}/{b} + {c}*x - {d}/{a}"),
)

#: Probe expressions whose parses carry *removable restrictions*: the canonical text alone would
#: merge semantic classes that are genuinely different functions. They exist so that the
#: ``(canonical, domain, excluded points)`` key is load-bearing somewhere in this experiment - the
#: main template corpus never exercises it (measured, see :func:`key_discrimination_report`).
#:
#: ``point_pair``          both parses are restricted, at DIFFERENT points;
#: ``restricted_vs_free``  one parse is restricted and the other is not;
#: ``control_no_split``    a removable restriction is present but every class has the same one, so
#:                         the extra key components do no work - the split is not automatic.
RESTRICTION_PROBE_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("point_pair", "1 - x / x - 1"),
    ("point_pair", "2 - x / x - 2"),
    ("point_pair", "x - y / y - x"),
    ("restricted_vs_free", "x / 1 - x - 1"),
    ("restricted_vs_free", "x - 1 / 1 - x"),
    ("restricted_vs_free", "x - 2 / 2 - x"),
    ("restricted_vs_free", "x / x - 1 - x"),
    ("restricted_vs_free", "x / x - x + 1"),
    ("control_no_split", "x / x"),
    ("control_no_split", "(x * x - 1) / (x - 1)"),
)

#: Complete-linkage cut is placed at this fraction of the largest observed pairwise distance.
DEFAULT_THRESHOLD_FACTOR: float = 0.25

#: Two agreement profiles closer than this are treated as identical before agglomeration starts.
IDENTICAL_PROFILE_TOLERANCE: float = 1e-12

#: Below this many expressions the automatic worker choice stays sequential: on the spawn start
#: method process startup would cost more than the work itself.
PARALLEL_MINIMUM_ITEMS: int = 64


# --------------------------------------------------------------------------------------- corpus


def generate_corpus(
    values: Sequence[int] = COEFFICIENT_VALUES,
    templates: Sequence[tuple[str, str]] = FAMILY_TEMPLATES,
) -> dict[str, Any]:
    """Build the deterministic template corpus. No randomness and no seed is involved."""
    values = tuple(values)
    templates = tuple(templates)
    expressions: list[dict[str, Any]] = []
    for tuple_index, (a, b, c, d) in enumerate(product(values, repeat=4)):
        for family, template in templates:
            expressions.append(
                {
                    "index": len(expressions),
                    "family": family,
                    "source": template.format(a=a, b=b, c=c, d=d),
                    "parameters": {"a": a, "b": b, "c": c, "d": d},
                    "tuple_index": tuple_index,
                }
            )
    counts = Counter(item["family"] for item in expressions)
    return {
        "expressions": tuple(expressions),
        "size": len(expressions),
        "families": tuple(family for family, _ in templates),
        "family_counts": {family: counts[family] for family, _ in templates},
        "generation": {
            "coefficient_values": values,
            "parameter_names": PARAMETER_NAMES,
            "templates": {family: template for family, template in templates},
            "tuple_order": "itertools.product(coefficient_values, repeat=4) bound to (a, b, c, d)",
            "family_order": "the families are interleaved inside every coefficient tuple",
            "expressions_per_family": len(values) ** len(PARAMETER_NAMES),
            "excluded_values": "0 and negative integers - the tokenizer has no unary minus and 0 denominators are undefined",
            "randomness": "none; the corpus is a Cartesian product and is regenerable from these fields alone",
        },
    }


def restriction_probe_corpus(
    templates: Sequence[tuple[str, str]] = RESTRICTION_PROBE_TEMPLATES,
) -> dict[str, Any]:
    """Small hand-built corpus of expressions with removable restrictions.

    It is deliberately NOT part of :func:`generate_corpus`: the published `3125`-expression corpus
    is a Cartesian product of five templates and must stay exactly that. This probe is a separate,
    equally deterministic corpus whose only job is to exercise the ``excluded points`` component of
    the semantic-class key, which the template corpus never does.
    """
    templates = tuple(templates)
    expressions = [
        {"index": index, "family": family, "source": source, "parameters": {}, "tuple_index": index}
        for index, (family, source) in enumerate(templates)
    ]
    counts = Counter(item["family"] for item in expressions)
    return {
        "expressions": tuple(expressions),
        "size": len(expressions),
        "families": tuple(dict.fromkeys(family for family, _ in templates)),
        "family_counts": dict(counts),
        "generation": {
            "kind": "hand-built restriction probe",
            "randomness": "none; the sources are literals listed in RESTRICTION_PROBE_TEMPLATES",
            "purpose": "make the (canonical, domain, excluded points) class key load-bearing",
        },
    }


def normalize_corpus(corpus: Any) -> tuple[dict[str, Any], ...]:
    """Accept a :func:`generate_corpus` result, an item sequence, ``(family, source)`` pairs or strings."""
    entries = corpus["expressions"] if isinstance(corpus, dict) and "expressions" in corpus else corpus
    items: list[dict[str, Any]] = []
    for position, entry in enumerate(entries):
        if isinstance(entry, str):
            items.append({"index": position, "family": "unlabelled", "source": entry})
        elif isinstance(entry, dict):
            items.append(
                {
                    "index": entry.get("index", position),
                    "family": entry.get("family", "unlabelled"),
                    "source": entry["source"],
                }
            )
        else:
            family, source = entry
            items.append({"index": position, "family": family, "source": source})
    return tuple(items)


# ----------------------------------------------------------------------- deduplicated pipeline


def restricted_levels(grammar: Grammar, support: Iterable[str]) -> tuple[tuple[str, ...], ...]:
    """Precedence levels restricted to the operators that actually occur in the token sequence."""
    supported = frozenset(support)
    levels = []
    for level in grammar.levels:
        kept = tuple(sorted(operator for operator in level if operator in supported))
        if kept:
            levels.append(kept)
    return tuple(levels)


def support_block_key(grammar: Grammar, support: Iterable[str]) -> str:
    """Hashable name of the support-reduction block a grammar falls into for one expression."""
    return " > ".join("=".join(level) for level in restricted_levels(grammar, support)) or "(none)"


def support_forced_blocks(source: str, grammars: Sequence[Grammar] | None = None) -> dict[str, str]:
    """Map every grammar to its support-reduction block for ``source``."""
    grammars = grammars or GRAMMARS
    support = operator_support(source)
    return {grammar.id: support_block_key(grammar, support) for grammar in grammars}


def expression_classes(source: str, grammars: Sequence[Grammar] | None = None) -> dict[str, Any]:
    """Deduplicated semantic-class pipeline for one expression.

    Parses ``source`` under every grammar, groups the grammars by *serialized AST*, canonicalizes
    each DISTINCT AST exactly once, and keys the semantic class on
    ``(canonical expression, domain, excluded points)`` - the same key
    :func:`parseatlas.analyze.analyze_expression` uses. Domain and excluded points stay in the key
    because canonical text alone would merge ``x/x`` with ``1`` although ``x/x`` is undefined at 0.
    """
    grammars = grammars or GRAMMARS
    serialized: dict[str, str] = {}
    representatives: dict[str, Any] = {}
    ast_ids: dict[str, str] = {}
    for grammar in grammars:
        node = parse(source, grammar)
        blob = json.dumps(ast_to_dict(node), sort_keys=True)
        serialized[grammar.id] = blob
        if blob not in representatives:
            representatives[blob] = node
            ast_ids[blob] = f"A{len(ast_ids) + 1:02d}"
    keys = {}
    for blob, node in representatives.items():  # one canonicalize() per DISTINCT AST, not per grammar
        canonical = canonicalize(node)
        keys[blob] = (canonical["expression"], canonical["domain"], tuple(canonical["excluded_points"]))
    class_ids: dict[tuple[str, str, tuple[str, ...]], str] = {}
    classes: dict[str, str] = {}
    for grammar in grammars:
        key = keys[serialized[grammar.id]]
        if key not in class_ids:
            class_ids[key] = f"C{len(class_ids) + 1:02d}"
        classes[grammar.id] = class_ids[key]
    return {
        "source": source,
        "grammar_ids": tuple(grammar.id for grammar in grammars),
        "classes": classes,
        "ast_groups": {grammar_id: ast_ids[blob] for grammar_id, blob in serialized.items()},
        "class_keys": {
            class_id: {"canonical": key[0], "domain": key[1], "excluded_points": list(key[2])}
            for key, class_id in class_ids.items()
        },
        "distinct_ast_count": len(representatives),
        "distinct_class_count": len(class_ids),
        "canonicalizations": len(representatives),
    }


def _sensitivity_report(classes: dict[str, str]) -> dict[str, Any]:
    """Minimal report shape so grammar_matrix.representation_sensitivity is reused, not re-defined."""
    return {
        "grammars": [
            {"id": grammar_id, "equivalence_class": class_id} for grammar_id, class_id in classes.items()
        ]
    }


def _expression_record(item: dict[str, Any]) -> dict[str, Any]:
    """Module-level pool function: one corpus item in, one compact record out.

    It must stay module-level (not a closure or a lambda) so the Windows ``spawn`` start method can
    pickle it by reference.
    """
    source = item["source"]
    result = expression_classes(source)
    support = operator_support(source)
    classes = result["classes"]
    strict_classes = {class_id for grammar_id, class_id in classes.items() if grammar_id != "G0"}
    keys = result["class_keys"]
    canonical_texts = {entry["canonical"] for entry in keys.values()}
    return {
        "index": item["index"],
        "family": item["family"],
        "source": source,
        "classes": classes,
        "ast_groups": result["ast_groups"],
        "support_blocks": {grammar.id: support_block_key(grammar, support) for grammar in GRAMMARS},
        "support": support,
        "support_size": len(support),
        "distinct_ast_count": result["distinct_ast_count"],
        "distinct_class_count": result["distinct_class_count"],
        "strict_class_count": len(strict_classes),
        "sensitivity": representation_sensitivity(_sensitivity_report(classes)),
        # how much work the (domain, excluded points) half of the class key actually does here
        "canonical_text_count": len(canonical_texts),
        "restriction_split_classes": result["distinct_class_count"] - len(canonical_texts),
        "restricted_classes": sum(1 for entry in keys.values() if entry["excluded_points"]),
        "domains": tuple(sorted({entry["domain"] for entry in keys.values()})),
    }


# ------------------------------------------------------------------------------------ execution


def resolve_worker_count(item_count: int, workers: int | None = None) -> int:
    """Derive the process count from the observed cores, never from a hardcoded constant."""
    if workers is not None:
        return max(1, min(int(workers), max(item_count, 1)))
    if item_count < PARALLEL_MINIMUM_ITEMS:
        return 1
    cores = os.cpu_count() or 1
    return max(1, min(cores - 1, item_count))  # one core of headroom for the interactive session


def corpus_records(corpus: Any, workers: int | None = None) -> dict[str, Any]:
    """Compute one record per corpus expression, across processes by default.

    Expressions are independent and canonicalization is CPU-bound, so the corpus is split over
    processes. Parallelism changes only how fast the corpus is measured - every record, matrix and
    cluster is identical to the sequential (``workers=1``) path.
    """
    items = normalize_corpus(corpus)
    worker_count = resolve_worker_count(len(items), workers)
    started = time.perf_counter()
    if worker_count <= 1 or not items:
        records = [_expression_record(item) for item in items]
    else:
        chunk = max(1, len(items) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            records = list(pool.map(_expression_record, items, chunksize=chunk))
    return {
        "records": tuple(records),
        "expression_count": len(records),
        "workers": worker_count,
        "wall_clock_seconds": time.perf_counter() - started,
        "cpu_count": os.cpu_count(),
    }


def _resolve_records(
    corpus: Any, workers: int | None, records: Sequence[dict[str, Any]] | None
) -> dict[str, Any]:
    if records is not None:
        return {
            "records": tuple(records),
            "expression_count": len(records),
            "workers": None,
            "wall_clock_seconds": None,
            "cpu_count": os.cpu_count(),
        }
    return corpus_records(corpus, workers)


# -------------------------------------------------------------------------------------- matrix


def _agreement_counts(
    records: Sequence[dict[str, Any]], field: str, grammar_ids: Sequence[str]
) -> list[list[int]]:
    size = len(grammar_ids)
    counts = [[0] * size for _ in range(size)]
    for record in records:
        labels = [record[field][grammar_id] for grammar_id in grammar_ids]
        for left in range(size):
            label = labels[left]
            counts[left][left] += 1
            for right in range(left + 1, size):
                if label == labels[right]:
                    counts[left][right] += 1
                    counts[right][left] += 1
    return counts


def _as_matrix(counts: list[list[int]], total: int, grammar_ids: Sequence[str]) -> dict[str, dict[str, float]]:
    divisor = max(total, 1)
    return {
        grammar_ids[left]: {
            grammar_ids[right]: counts[left][right] / divisor for right in range(len(grammar_ids))
        }
        for left in range(len(grammar_ids))
    }


def _as_counts(counts: list[list[int]], grammar_ids: Sequence[str]) -> dict[str, dict[str, int]]:
    return {
        grammar_ids[left]: {grammar_ids[right]: counts[left][right] for right in range(len(grammar_ids))}
        for left in range(len(grammar_ids))
    }


def _difference(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[a - b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def _matrix_block(records: Sequence[dict[str, Any]], grammar_ids: Sequence[str]) -> dict[str, Any]:
    total = len(records)
    observed = _agreement_counts(records, "classes", grammar_ids)
    forced = _agreement_counts(records, "support_blocks", grammar_ids)
    identical = _agreement_counts(records, "ast_groups", grammar_ids)
    excess = _difference(observed, forced)
    semantic_excess = _difference(observed, identical)
    observed_matrix = _as_matrix(observed, total, grammar_ids)
    return {
        "always_agree_partition": always_agree_partition(observed_matrix),
        "expression_count": total,
        "grammar_count": len(grammar_ids),
        "grammar_ids": tuple(grammar_ids),
        "matrix": observed_matrix,
        "equal_counts": _as_counts(observed, grammar_ids),
        "support_forced_matrix": _as_matrix(forced, total, grammar_ids),
        "support_forced_counts": _as_counts(forced, grammar_ids),
        "excess_matrix": _as_matrix(excess, total, grammar_ids),
        "excess_counts": _as_counts(excess, grammar_ids),
        "ast_identity_matrix": _as_matrix(identical, total, grammar_ids),
        "semantic_excess_matrix": _as_matrix(semantic_excess, total, grammar_ids),
    }


def corpus_matrix(
    corpus: Any, workers: int | None = None, records: Sequence[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Aggregated 25x25 agreement matrix, its support-reduction null and the excess above it."""
    run = _resolve_records(corpus, workers, records)
    collected = run["records"]
    grammar_ids = GRAMMAR_IDS
    result = _matrix_block(collected, grammar_ids)
    families: dict[str, dict[str, Any]] = {}
    for family in dict.fromkeys(record["family"] for record in collected):
        subset = [record for record in collected if record["family"] == family]
        families[family] = _matrix_block(subset, grammar_ids)
    result.update(
        {
            "families": families,
            "family_counts": {family: block["expression_count"] for family, block in families.items()},
            "support_size_counts": dict(sorted(Counter(record["support_size"] for record in collected).items())),
            "workers": run["workers"],
            "wall_clock_seconds": run["wall_clock_seconds"],
            "cpu_count": run["cpu_count"],
            "records": collected,
            "null_model": (
                "two grammars are support-forced to agree when their precedence levels restricted to O(E) "
                "are identical; that forces a byte-identical AST and therefore the same semantic class"
            ),
        }
    )
    return result


def extreme_pairs(
    matrix: dict[str, Any], key: str = "excess_matrix", count: int = 5
) -> dict[str, list[tuple[str, str, float]]]:
    """Highest and lowest off-diagonal pairs of one matrix, ordered deterministically."""
    values = matrix[key] if key in matrix else matrix
    grammar_ids = tuple(values)
    pairs = [
        (grammar_ids[left], grammar_ids[right], values[grammar_ids[left]][grammar_ids[right]])
        for left in range(len(grammar_ids))
        for right in range(left + 1, len(grammar_ids))
    ]
    ordered = sorted(pairs, key=lambda item: (item[2], item[0], item[1]))
    return {"lowest": ordered[:count], "highest": list(reversed(ordered[-count:]))}


# ------------------------------------------------------------------------------------ clusters


def comparable_signature(
    values: dict[str, dict[str, float]], grammar_ids: Sequence[str], left: str, right: str
) -> tuple[float, ...]:
    """``left``'s agreement row restricted to the coordinates that are comparable with ``right``.

    The coordinates are ``grammar_ids`` with BOTH ``left`` and ``right`` removed, kept in
    ``grammar_ids`` order, so ``comparable_signature(v, ids, a, b)`` and
    ``comparable_signature(v, ids, b, a)`` are two vectors on the SAME axes and
    :func:`profile_distance` is nothing but their plain L2 distance.

    The vector is indexed by a PAIR on purpose: no per-grammar vector can induce this distance.
    Suppose every grammar ``g`` published one full-width vector ``u_g`` with ``u_g[j] = values[g][j]``
    for ``j != g`` and some filler ``u_g[g]``. Then

        ``||u_a - u_b||^2 = (comparable distance)^2 + (u_a[a] - values[b][a])^2 + (values[a][b] - u_b[b])^2``

    and the two extra terms vanish only when each filler equals ``values[a][b]`` - a value that
    depends on the OTHER grammar. A grammar therefore has no single signature here; it has one per
    partner. That is why ``matrix_rows_without_self`` is only a display row, while these vectors are
    what the clustering measures and what reproduces ``identical_signature_groups``.
    """
    return tuple(values[left][other] for other in grammar_ids if other != left and other != right)


def profile_distance(
    values: dict[str, dict[str, float]], grammar_ids: Sequence[str], left: str, right: str
) -> float:
    """L2 distance between two agreement profiles with BOTH self-agreement columns dropped.

    The diagonal of an agreement matrix is not a measurement, it is a definition: every grammar
    agrees with itself on every expression. In the observed matrix that constant is ``1.0``; in the
    EXCESS matrix ``observed - forced`` it is ``1.0 - 1.0 = 0.0``. Feeding a raw row into a distance
    therefore makes a grammar look maximally UNLIKE itself along its own axis, and it pushes exactly
    the strongly agreeing pairs apart: including columns ``left`` and ``right`` adds
    ``2 * X[left][right] ** 2`` to the squared excess distance.

    Both self columns are dropped so the two profiles are compared on the same `23` coordinates and
    the result stays symmetric. The two compared vectors are exactly
    :func:`comparable_signature` of ``(left, right)`` and of ``(right, left)``; the distance is
    defined from them rather than inlined, so the vector this module PUBLISHES can never drift from
    the vector it measures.
    """
    return sqrt(
        sum(
            (a - b) * (a - b)
            for a, b in zip(
                comparable_signature(values, grammar_ids, left, right),
                comparable_signature(values, grammar_ids, right, left),
            )
        )
    )


def always_agree_partition(matrix: dict[str, Any], key: str = "matrix", level: float = 1.0) -> tuple[tuple[str, ...], ...]:
    """Group grammars that share a semantic class on EVERY expression of the corpus.

    ``matrix[key][left][right] >= level`` is an equivalence relation when ``level`` is ``1.0``:
    per-expression class identity is transitive, so corpus-wide identity is too. The result is the
    sharpest corpus-relative statement available - two grammars in one group are indistinguishable
    by this corpus, whatever the reason.
    """
    values = matrix[key] if isinstance(matrix, dict) and key in matrix else matrix
    grammar_ids = tuple(values)
    seen: dict[tuple[int, ...], int] = {}
    groups: list[list[str]] = []
    for grammar_id in grammar_ids:
        signature = tuple(1 if values[grammar_id][other] >= level else 0 for other in grammar_ids)
        if signature in seen:
            groups[seen[signature]].append(grammar_id)
        else:
            seen[signature] = len(groups)
            groups.append([grammar_id])
    return tuple(tuple(group) for group in groups)


def grammar_clusters(
    matrix: dict[str, Any],
    threshold: float | None = None,
    threshold_factor: float = DEFAULT_THRESHOLD_FACTOR,
    signature_key: str = "excess_matrix",
) -> dict[str, Any]:
    """Cluster the grammars from their EXCESS-matrix agreement profiles.

    Deterministic two-stage method, no external clustering library:

    1. grammars whose profiles are identical (:data:`IDENTICAL_PROFILE_TOLERANCE`) form the initial
       groups;
    2. those groups are merged by complete linkage on :func:`profile_distance` while the smallest
       linkage distance stays at or below ``threshold``; the default threshold is
       ``threshold_factor * max pairwise distance``.

    The distance drops both self-agreement columns: see :func:`profile_distance` for why a raw row
    is not a usable signature vector. Because that distance is pair-relative, the reproducible
    vector is published as ``comparable_signatures[left][right]`` (:func:`comparable_signature`);
    ``matrix_rows_without_self`` is kept next to it under a name that says what it is - a display
    row, not the clustering input.

    ``signature_key`` selects which matrix the rows come from. It stays ``excess_matrix`` by
    default; ``matrix`` re-runs the identical procedure on the raw observed agreement, which is what
    the report uses to show how much of the excess clustering is an image of the null model.
    """
    values = matrix[signature_key] if isinstance(matrix, dict) and signature_key in matrix else matrix
    grammar_ids = tuple(values)
    position = {grammar_id: index for index, grammar_id in enumerate(grammar_ids)}
    rows_without_self = {
        grammar_id: tuple(values[grammar_id][other] for other in grammar_ids if other != grammar_id)
        for grammar_id in grammar_ids
    }
    comparable_signatures = {
        left: {
            right: comparable_signature(values, grammar_ids, left, right)
            for right in grammar_ids
            if right != left
        }
        for left in grammar_ids
    }
    distance = {
        left: {right: profile_distance(values, grammar_ids, left, right) for right in grammar_ids}
        for left in grammar_ids
    }
    pairwise = [
        distance[grammar_ids[left]][grammar_ids[right]]
        for left in range(len(grammar_ids))
        for right in range(left + 1, len(grammar_ids))
    ]
    max_distance = max(pairwise) if pairwise else 0.0
    if threshold is None:
        threshold = threshold_factor * max_distance

    initial: list[list[str]] = []
    for grammar_id in grammar_ids:
        for group in initial:
            if distance[group[0]][grammar_id] <= IDENTICAL_PROFILE_TOLERANCE:
                group.append(grammar_id)
                break
        else:
            initial.append([grammar_id])
    clusters = [list(members) for members in initial]

    while len(clusters) > 1:
        best: tuple[float, int, int] | None = None
        for left in range(len(clusters)):
            for right in range(left + 1, len(clusters)):
                linkage = max(distance[a][b] for a in clusters[left] for b in clusters[right])
                if best is None or linkage < best[0]:
                    best = (linkage, left, right)
        if best is None or best[0] > threshold + 1e-12:
            break
        _, left, right = best
        clusters[left] = sorted(clusters[left] + clusters[right], key=lambda item: position[item])
        del clusters[right]
        clusters.sort(key=lambda members: position[members[0]])

    return {
        "method": (
            "identical-profile grouping, then complete-linkage agglomeration on the L2 distance of "
            "agreement-matrix rows with both self-agreement columns dropped"
        ),
        "diagonal_policy": (
            "excluded: the distance between two grammars ignores both of their own columns, because "
            "the diagonal is a definition (self-agreement is total) and not a measurement - keeping "
            "it adds 2 * value[left][right] ** 2 to the squared distance and pushes the most "
            "strongly agreeing pairs apart"
        ),
        "signature_note": (
            f"matrix_rows_without_self[g] is the agreement row with g's OWN column dropped "
            f"({len(grammar_ids) - 1} coordinates). It is a display row, NOT the vector the "
            "clustering measures: it still carries the partner's column, so two grammars in one "
            "identical-profile group can and do differ there. comparable_signatures[left][right] is "
            f"the vector profile_distance actually consumes - grammar_ids without left and without "
            f"right, in grammar_ids order ({len(grammar_ids) - 2} coordinates) - and "
            "comparable_signatures[left][right] == comparable_signatures[right][left] exactly when "
            "the two profiles are identical, which is how identical_signature_groups is built"
        ),
        "signature_source": signature_key,
        "grammar_ids": grammar_ids,
        "matrix_rows_without_self": rows_without_self,
        "matrix_row_columns": {
            grammar_id: tuple(other for other in grammar_ids if other != grammar_id)
            for grammar_id in grammar_ids
        },
        "comparable_signatures": comparable_signatures,
        "matrix_rows": {
            grammar_id: dict(values[grammar_id]) for grammar_id in grammar_ids
        },
        "distance_matrix": distance,
        "max_distance": max_distance,
        "threshold": threshold,
        "threshold_factor": threshold_factor,
        "identical_signature_groups": tuple(tuple(members) for members in initial),
        "clusters": tuple(tuple(members) for members in clusters),
        "cluster_count": len(clusters),
        "cluster_sizes": tuple(len(members) for members in clusters),
    }


def _pair_verdicts(clusters: dict[str, Any], grammar_ids: Sequence[str]) -> dict[tuple[str, str], bool]:
    label = {grammar_id: index for index, members in enumerate(clusters["clusters"]) for grammar_id in members}
    return {
        (grammar_ids[left], grammar_ids[right]): label[grammar_ids[left]] == label[grammar_ids[right]]
        for left in range(len(grammar_ids))
        for right in range(left + 1, len(grammar_ids))
    }


def cluster_stability(
    corpus: Any,
    workers: int | None = None,
    records: Sequence[dict[str, Any]] | None = None,
    threshold_factor: float = DEFAULT_THRESHOLD_FACTOR,
    signature_key: str = "excess_matrix",
) -> dict[str, Any]:
    """Split the corpus deterministically into even/odd halves and compare the two clusterings."""
    run = _resolve_records(corpus, workers, records)
    collected = run["records"]
    halves = {
        "even": [record for position, record in enumerate(collected) if position % 2 == 0],
        "odd": [record for position, record in enumerate(collected) if position % 2 == 1],
    }
    outcome = {}
    for name, subset in halves.items():
        block = _matrix_block(subset, GRAMMAR_IDS)
        outcome[name] = {
            "matrix": block,
            "clusters": grammar_clusters(block, threshold_factor=threshold_factor, signature_key=signature_key),
        }
    left_verdicts = _pair_verdicts(outcome["even"]["clusters"], GRAMMAR_IDS)
    right_verdicts = _pair_verdicts(outcome["odd"]["clusters"], GRAMMAR_IDS)
    pairs = tuple(left_verdicts)
    matching = sum(left_verdicts[pair] == right_verdicts[pair] for pair in pairs)
    together_both = sum(left_verdicts[pair] and right_verdicts[pair] for pair in pairs)
    together_either = sum(left_verdicts[pair] or right_verdicts[pair] for pair in pairs)
    return {
        "signature_key": signature_key,
        "pair_count": len(pairs),
        "matching_pairs": matching,
        "pair_agreement": matching / max(len(pairs), 1),
        "together_in_both": together_both,
        "together_in_either": together_either,
        "together_agreement": together_both / together_either if together_either else 1.0,
        "halves": {
            name: {
                "expression_count": len(halves[name]),
                "cluster_count": outcome[name]["clusters"]["cluster_count"],
                "cluster_sizes": outcome[name]["clusters"]["cluster_sizes"],
                "clusters": outcome[name]["clusters"]["clusters"],
                "threshold": outcome[name]["clusters"]["threshold"],
                "max_distance": outcome[name]["clusters"]["max_distance"],
                "always_agree_partition": always_agree_partition(outcome[name]["matrix"]),
            }
            for name in halves
        },
        "workers": run["workers"],
        "wall_clock_seconds": run["wall_clock_seconds"],
    }


# ------------------------------------------------------------------------------------ diversity


def _pearson(left: Sequence[float], right: Sequence[float]) -> float | None:
    count = len(left)
    if count < 2:
        return None
    mean_left = sum(left) / count
    mean_right = sum(right) / count
    deviation_left = [value - mean_left for value in left]
    deviation_right = [value - mean_right for value in right]
    variance_left = sum(value * value for value in deviation_left)
    variance_right = sum(value * value for value in deviation_right)
    if variance_left == 0 or variance_right == 0:
        return None
    return sum(a * b for a, b in zip(deviation_left, deviation_right)) / sqrt(variance_left * variance_right)


def _diversity_block(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    ast_values = [record["distinct_ast_count"] for record in records]
    class_values = [record["distinct_class_count"] for record in records]
    cross: dict[int, Counter] = {}
    for ast_count, class_count in zip(ast_values, class_values):
        cross.setdefault(ast_count, Counter())[class_count] += 1
    decoupled = sum(sum(histogram.values()) for histogram in cross.values() if len(histogram) > 1)
    return {
        "expression_count": len(records),
        "ast_diversity_distribution": dict(sorted(Counter(ast_values).items())),
        "class_count_distribution": dict(sorted(Counter(class_values).items())),
        "ast_diversity_values": tuple(sorted(set(ast_values))),
        "class_count_values": tuple(sorted(set(class_values))),
        "cross_tab": {ast_count: dict(sorted(histogram.items())) for ast_count, histogram in sorted(cross.items())},
        "correlation": _pearson(ast_values, class_values),
        "constant_ast_varying_class_count": decoupled,
        "constant_ast_varying_class_fraction": decoupled / max(len(records), 1),
    }


def diversity_report(
    corpus: Any, workers: int | None = None, records: Sequence[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """AST diversity against semantic class count, per family and overall."""
    run = _resolve_records(corpus, workers, records)
    collected = run["records"]
    families = {
        family: _diversity_block([record for record in collected if record["family"] == family])
        for family in dict.fromkeys(record["family"] for record in collected)
    }
    return {
        "overall": _diversity_block(collected),
        "families": families,
        "workers": run["workers"],
        "wall_clock_seconds": run["wall_clock_seconds"],
    }


# ----------------------------------------------------------------------------- class-key audit


def _key_discrimination_block(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    classes = sum(record["distinct_class_count"] for record in records)
    texts = sum(record["canonical_text_count"] for record in records)
    split = [record for record in records if record["restriction_split_classes"] > 0]
    return {
        "expression_count": len(records),
        "classes": classes,
        "canonical_texts": texts,
        "classes_lost_without_the_restriction_key": classes - texts,
        "expressions_where_the_restriction_key_splits_a_class": len(split),
        "expressions_with_a_restricted_class": sum(1 for record in records if record["restricted_classes"]),
        "domain_values": tuple(sorted({domain for record in records for domain in record["domains"]})),
        "split_sources": tuple(record["source"] for record in split),
    }


def key_discrimination_report(
    corpus: Any, workers: int | None = None, records: Sequence[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Measure how much work ``domain`` and ``excluded points`` do beyond the canonical text.

    The semantic class key is ``(canonical expression, domain, excluded points)``. This report
    answers the only honest question about the last two components: on THIS corpus, do they ever
    separate two classes that share a canonical text? ``classes_lost_without_the_restriction_key``
    counts exactly the classes that would collapse if the key were the canonical text alone.
    """
    run = _resolve_records(corpus, workers, records)
    collected = run["records"]
    families = {
        family: _key_discrimination_block([record for record in collected if record["family"] == family])
        for family in dict.fromkeys(record["family"] for record in collected)
    }
    return {
        "key": "(canonical expression, domain, excluded points)",
        "note": (
            "canonicalize() currently returns domain 'R' unconditionally, so the domain component "
            "cannot discriminate anywhere; only excluded points can, and this report measures whether "
            "they do"
        ),
        "overall": _key_discrimination_block(collected),
        "families": families,
        "workers": run["workers"],
        "wall_clock_seconds": run["wall_clock_seconds"],
    }


# ------------------------------------------------------------------------------------ rigidity


def _rigidity_block(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    sensitivities = [record["sensitivity"] for record in records]
    rigid = sum(record["strict_class_count"] == 1 for record in records)
    return {
        "expression_count": len(records),
        "rigid": rigid,
        "sensitive": len(records) - rigid,
        "rigid_fraction": rigid / max(len(records), 1),
        "sensitivity_distribution": dict(sorted(Counter(round(value, 6) for value in sensitivities).items())),
        "strict_class_distribution": dict(sorted(Counter(record["strict_class_count"] for record in records).items())),
        "mean_sensitivity": sum(sensitivities) / max(len(sensitivities), 1),
        "min_sensitivity": min(sensitivities) if sensitivities else None,
        "max_sensitivity": max(sensitivities) if sensitivities else None,
    }


def rigidity_classification(
    corpus: Any, workers: int | None = None, records: Sequence[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Grammar-rigid versus grammar-sensitive split, using grammar_matrix.representation_sensitivity."""
    run = _resolve_records(corpus, workers, records)
    collected = run["records"]
    families = {
        family: _rigidity_block([record for record in collected if record["family"] == family])
        for family in dict.fromkeys(record["family"] for record in collected)
    }
    return {
        "definition": "S(E) = (strict semantic classes - 1) / 23; rigid means S(E) == 0.0",
        "overall": _rigidity_block(collected),
        "families": families,
        "workers": run["workers"],
        "wall_clock_seconds": run["wall_clock_seconds"],
    }
