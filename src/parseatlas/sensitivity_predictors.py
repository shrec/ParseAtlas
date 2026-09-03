"""What makes an expression grammar-sensitive? Structural predictors of ``S(E)``.

Experiment 0029. Thesis T4 named this the project's own central open question and T15 restated
it as unresolved: 0017 observed that some token sequences keep all 24 strict grammars in one
semantic class while others fragment, and 0024 measured the distribution at corpus scale without
explaining it. This module supplies the closed feature set, the association measurements, the
cell-collapse test and the deterministic hold-out that turn "explain" into something falsifiable.

The measured quantities being explained come from :mod:`parseatlas.corpus_matrix` and are never
recomputed here:

* ``S(E) = (strict semantic classes - 1) / 23``  (:func:`parseatlas.grammar_matrix.representation_sensitivity`)
* ``C(E) = strict semantic classes``

THE SUPPORT-SIZE TRAP
---------------------
Operator-support reduction (T6, experiment 0019) forces part of any answer mechanically: when the
distinct-operator set ``O(E)`` has size ``k``, the 24 strict grammars split into ``k!`` blocks and
every grammar inside a block builds a byte-identical AST, hence lands in the same semantic class.
An expression with ``|O(E)| == 1`` therefore *cannot* fragment, whatever its mathematics. A
predictor built on ``|O(E)|`` restates the parser instead of explaining the mathematics.

Four features in the closed set are marked ``restates_the_parser``:

``support_size``               the T6 block structure itself;
``parenthesis_pair_count``     a parenthesis fixes a split before any binding power is consulted,
                               so it forces agreement exactly the way a small support does;
``distinct_ast_count``         the parse outcome, not an input to it;
``strict_reachable_tree_count`` the symbolic decision procedure of 0023 predicting that outcome.

Every association is therefore reported twice: overall, and *within a fixed support size*. The
within-stratum figure is the result; the overall figure is context.

A NAMING NOTE
-------------
``operator_word_catalan_count`` and ``strict_reachable_tree_count`` are both computed on the
OPERATOR WORD with the parentheses invisible, and both names say so on purpose. Neither is the
number of trees the *token sequence* admits: an explicit parenthesis removes trees before any
binding power is read, so a parenthesized source admits strictly fewer. The rational family of the
published corpus scores 42 and 17 on these two features while only 4 distinct ASTs are measured
over the 24 strict grammars, and that gap is exactly what ``parenthesis_pair_count`` exists to
carry.
"""

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import sqrt
import os
import time
from typing import Any

from .ast_space import canonical_leaves, enumerate_parenthesizations
from .corpus_matrix import corpus_records, normalize_corpus, resolve_worker_count
from .grammar import strict_grammars
from .reachability import strict_reachable
from .support_reduction import operator_support, serialized_ast
from .tokenizer import Token, tokenize

#: The 24 strict orderings. ``G0`` is deliberately absent: ``S(E)`` and ``C(E)`` are strict-only
#: quantities, so every parse-derived feature must be counted over the same 24 grammars.
STRICT_GRAMMARS = strict_grammars()


# ------------------------------------------------------------------------------ feature catalog


@dataclass(frozen=True)
class Feature:
    """One structural feature, with the reason it is allowed into the closed set."""

    name: str
    kind: str  # "ordered" (rank-comparable) or "categorical" (label only)
    origin: str  # "token", "operator-word", "coefficient" or "parse"
    restates_the_parser: bool
    motivation: str


#: THE CLOSED SET. Nothing outside this tuple is measured, and every entry is cheap (one tokenize,
#: one Catalan enumeration cached per operator word, 24 parses) and independently motivated. The
#: set is closed on purpose: a feature invented after seeing which cells failed to collapse would
#: be fitted to the answer, not a prediction of it.
FEATURES: tuple[Feature, ...] = (
    Feature(
        "support_size",
        "ordered",
        "token",
        True,
        "|O(E)| - the T6 quantity; k! forced blocks, so |O(E)| == 1 cannot fragment at all",
    ),
    Feature(
        "operator_count",
        "ordered",
        "token",
        False,
        "total operator tokens; more operators means more places two grammars can disagree",
    ),
    Feature(
        "leaf_count",
        "ordered",
        "token",
        False,
        "number and name tokens; the operand side of the same size argument",
    ),
    Feature(
        "variable_leaf_count",
        "ordered",
        "token",
        False,
        "leaves that are variables; constant folding cannot remove them, so they carry the shape",
    ),
    Feature(
        "distinct_variable_count",
        "ordered",
        "token",
        False,
        "distinct variable names; a second variable blocks the collapses a single variable allows",
    ),
    Feature(
        "parenthesis_pair_count",
        "ordered",
        "token",
        True,
        "an explicit parenthesis fixes a split before any binding power is read - mechanical, like T6",
    ),
    Feature(
        "division_operator_count",
        "ordered",
        "token",
        False,
        "count of / as an OPERATOR; division is the only non-associative, non-commutative operator here",
    ),
    Feature(
        "has_division",
        "ordered",
        "token",
        False,
        "presence form of the same fact; 0024 showed 60% of that corpus has no / operator at all",
    ),
    Feature(
        "max_operator_multiplicity",
        "ordered",
        "token",
        False,
        "largest repetition in the operator occurrence multiset; a repeated operator re-associates with itself",
    ),
    Feature(
        "repeated_operator_count",
        "ordered",
        "token",
        False,
        "how many operator types occur more than once - the coarse form of the repetition pattern",
    ),
    Feature(
        "operator_profile",
        "categorical",
        "operator-word",
        False,
        "the operator occurrence multiset itself, e.g. '* x3, + x1, - x1'",
    ),
    Feature(
        "repetition_pattern",
        "categorical",
        "operator-word",
        False,
        "the multiset of multiplicities alone, e.g. '3+1+1' - shape without operator identity",
    ),
    Feature(
        "unit_literal_count",
        "ordered",
        "coefficient",
        False,
        "literals equal to 1; the multiplicative identity is the one coefficient that collapses subterms",
    ),
    Feature(
        "zero_literal_count",
        "ordered",
        "coefficient",
        False,
        "literals equal to 0; the additive identity, and the annihilator of any product it enters",
    ),
    Feature(
        "unit_multiplier_count",
        "ordered",
        "coefficient",
        False,
        "a literal 1 adjacent to a * token: 1*(u+v) == 1*u + v is false, but 1*(u) == u makes two ASTs equal",
    ),
    Feature(
        "unit_divisor_count",
        "ordered",
        "coefficient",
        False,
        "a literal 1 immediately after a / token: (u-v)/1 == u - v/1 collapses a re-association",
    ),
    Feature(
        "degenerate_coefficient",
        "ordered",
        "coefficient",
        False,
        "presence form: any literal 0 or 1 anywhere in the token sequence",
    ),
    Feature(
        "fractional_literal_count",
        "ordered",
        "coefficient",
        False,
        "literals the tokenizer read as a rational (denominator != 1) - a / that is NOT an operator",
    ),
    Feature(
        "distinct_ast_count",
        "ordered",
        "parse",
        True,
        "distinct serialized ASTs over the 24 strict grammars - the structural half of what S(E) counts",
    ),
    Feature(
        "operator_word_catalan_count",
        "ordered",
        "operator-word",
        False,
        "binary trees over the OPERATOR WORD; parentheses are invisible to it, so a parenthesized "
        "token sequence admits strictly fewer trees than this number counts",
    ),
    Feature(
        "strict_reachable_tree_count",
        "ordered",
        "operator-word",
        True,
        "Catalan trees some strict binding power builds (0023 decision procedure), parentheses ignored",
    ),
)

FEATURE_NAMES: tuple[str, ...] = tuple(feature.name for feature in FEATURES)
FEATURE_BY_NAME: dict[str, Feature] = {feature.name: feature for feature in FEATURES}
ORDERED_FEATURES: tuple[str, ...] = tuple(f.name for f in FEATURES if f.kind == "ordered")
CATEGORICAL_FEATURES: tuple[str, ...] = tuple(f.name for f in FEATURES if f.kind == "categorical")
PARSER_RESTATING_FEATURES: tuple[str, ...] = tuple(f.name for f in FEATURES if f.restates_the_parser)
INDEPENDENT_FEATURES: tuple[str, ...] = tuple(f.name for f in FEATURES if not f.restates_the_parser)

#: Feature name carrying the measured target, and the two targets themselves.
SENSITIVITY = "sensitivity"
CLASS_COUNT = "class_count"

#: Support size is the stratum the trap demands be held fixed.
TRAP_STRATUM: tuple[str, ...] = ("support_size",)


# --------------------------------------------------------------------------------- feature math


def literal_value(token: Token) -> Fraction:
    """Value of a number token. ``2/3`` is ONE token in this language, not a division."""
    if "/" in token.value:
        numerator, denominator = token.value.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(token.value))


@lru_cache(maxsize=None)
def _word_tree_counts(word: tuple[str, ...]) -> tuple[int, int]:
    """``(catalan trees, strict-reachable trees)`` for one operator word.

    Both numbers depend on the operator word alone, so they are cached by it: the published corpus
    has 3125 expressions but only five distinct operator words. The enumeration is reused from
    :mod:`parseatlas.ast_space` and the reachability decision from :mod:`parseatlas.reachability`;
    neither is reimplemented here. Parentheses are NOT visible to this pair - that is the point of
    keeping ``parenthesis_pair_count`` as a separate feature.
    """
    trees = enumerate_parenthesizations(canonical_leaves(len(word) + 1), word)
    return len(trees), sum(1 for tree in trees if strict_reachable(tree, word))


def expression_features(source: str) -> dict[str, Any]:
    """Compute the whole closed feature set for one token sequence. Deterministic and pure."""
    tokens = tokenize(source)
    operators = tuple(token.value for token in tokens if token.kind == "operator")
    numbers = tuple(token for token in tokens if token.kind == "number")
    names = tuple(token for token in tokens if token.kind == "name")
    multiplicity = Counter(operators)

    unit_multipliers = 0
    unit_divisors = 0
    for position, token in enumerate(tokens):
        if token.kind != "number" or literal_value(token) != 1:
            continue
        before = tokens[position - 1] if position else None
        after = tokens[position + 1] if position + 1 < len(tokens) else None
        if (before is not None and before.kind == "operator" and before.value == "*") or (
            after is not None and after.kind == "operator" and after.value == "*"
        ):
            unit_multipliers += 1
        if before is not None and before.kind == "operator" and before.value == "/":
            unit_divisors += 1

    unit_literals = sum(1 for token in numbers if literal_value(token) == 1)
    zero_literals = sum(1 for token in numbers if literal_value(token) == 0)
    catalan, reachable = _word_tree_counts(operators)
    return {
        "support_size": len(operator_support(source)),
        "operator_count": len(operators),
        "leaf_count": len(numbers) + len(names),
        "variable_leaf_count": len(names),
        "distinct_variable_count": len({token.value for token in names}),
        "parenthesis_pair_count": sum(1 for token in tokens if token.kind == "left"),
        "division_operator_count": multiplicity.get("/", 0),
        "has_division": 1 if multiplicity.get("/", 0) else 0,
        "max_operator_multiplicity": max(multiplicity.values()) if multiplicity else 0,
        "repeated_operator_count": sum(1 for count in multiplicity.values() if count > 1),
        "operator_profile": ", ".join(f"{name} x{multiplicity[name]}" for name in sorted(multiplicity)),
        "repetition_pattern": "+".join(str(count) for count in sorted(multiplicity.values(), reverse=True)),
        "unit_literal_count": unit_literals,
        "zero_literal_count": zero_literals,
        "unit_multiplier_count": unit_multipliers,
        "unit_divisor_count": unit_divisors,
        "degenerate_coefficient": 1 if unit_literals or zero_literals else 0,
        "fractional_literal_count": sum(1 for token in numbers if literal_value(token).denominator != 1),
        "distinct_ast_count": len({serialized_ast(source, grammar) for grammar in STRICT_GRAMMARS}),
        "operator_word_catalan_count": catalan,
        "strict_reachable_tree_count": reachable,
    }


def _feature_entry(item: dict[str, Any]) -> dict[str, Any]:
    """Module-level pool function: one corpus item in, one feature row out.

    It must stay module-level (not a closure or lambda) so the Windows ``spawn`` start method can
    pickle it by reference.
    """
    row = {"index": item["index"], "family": item["family"], "source": item["source"]}
    row.update(expression_features(item["source"]))
    return row


def resolve_feature_workers(item_count: int, workers: int | None = None) -> int:
    """Resolve the process count for feature extraction. Never a hardcoded constant.

    ``None`` and any value ``<= 0`` derive the count from the observed core count with one core of
    headroom; a positive value is honoured, and ``1`` forces the sequential path. The derivation is
    delegated to :func:`parseatlas.corpus_matrix.resolve_worker_count`, which also keeps corpora
    below :data:`parseatlas.corpus_matrix.PARALLEL_MINIMUM_ITEMS` sequential, rather than restated.
    """
    if workers is not None and workers > 0:
        return resolve_worker_count(item_count, workers)
    return resolve_worker_count(item_count, None)


def feature_rows(corpus: Any, workers: int | None = None) -> dict[str, Any]:
    """Feature rows for a corpus, across processes by default.

    MEASURED, this 16-core Windows host, published 3125-expression corpus, five paired runs each in
    a fresh interpreter (sequential first, then the parallel runs in the same process):

    ==========================  ===========  =============  =========  ==========
    machine state               sequential   15 workers     speedup    identical?
    ==========================  ===========  =============  =========  ==========
    idle, run A                 2.726 s      2.090 s        1.30x      True
    idle, run B                 2.777 s      2.066 s        1.34x      True
    idle, run C                 2.492 s      1.932 s        1.29x      True
    another worker on the box   12.536 s     15.871 s       0.79x      True
    several workers on the box  15.570 s     35.617 s       0.44x      True
    ==========================  ===========  =============  =========  ==========

    Feature extraction is one tokenize plus 24 parses per expression - roughly a millisecond - and
    the Catalan/reachability half is cached per operator word, of which the corpus has five, so the
    per-item work is small and the spawn cost (a fresh interpreter plus the sympy import chain that
    ``parseatlas`` pulls in through :mod:`parseatlas.canonical`) eats most of the gain. On an idle
    host it does not eat all of it - a consistent ``1.3x`` over three paired runs - so this path
    runs across processes by default, as independent per-item work in this repository does. Under
    contention the sign INVERTS: with another worker saturating the box the same code measured
    ``0.79x``, and with several of them ``0.44x``, because 15 spawned interpreters now compete for
    cores they do not have - the harder the box is loaded, the worse it gets. That is a
    measurement of the machine, not of the code, and it is recorded rather than hidden: on a busy
    host ``workers=1`` is the faster call, and it is available for exactly that reason. The
    sequential/parallel identity is pinned by a test - parallelism changes only how fast.

    The expensive half of :func:`feature_table` - canonicalization for ``S(E)`` and ``C(E)`` - is
    CPU-bound sympy work and runs across processes through
    :func:`parseatlas.corpus_matrix.corpus_records`, where 0024 measured ``3.08x-5.85x``.
    """
    items = normalize_corpus(corpus)
    worker_count = resolve_feature_workers(len(items), workers)
    started = time.perf_counter()
    if worker_count <= 1 or not items:
        rows = [_feature_entry(item) for item in items]
    else:
        chunk = max(1, len(items) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            rows = list(pool.map(_feature_entry, items, chunksize=chunk))
    return {
        "rows": tuple(rows),
        "expression_count": len(rows),
        "workers": worker_count,
        "wall_clock_seconds": time.perf_counter() - started,
        "cpu_count": os.cpu_count(),
    }


# ------------------------------------------------------------------------------------ the table


def feature_table(
    corpus: Any, workers: int | None = None, records: Sequence[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Closed feature set plus the measured ``S(E)`` and ``C(E)`` for every corpus expression.

    ``S(E)`` and ``C(E)`` are read from :func:`parseatlas.corpus_matrix.corpus_records`, so the
    numbers here are the same measurement 0024 published, not a second implementation of it. Pass
    ``records`` to reuse a run that already happened.
    """
    items = normalize_corpus(corpus)
    if records is None:
        run = corpus_records(corpus, workers)
        collected = run["records"]
        record_workers: int | None = run["workers"]
        record_seconds: float | None = run["wall_clock_seconds"]
    else:
        collected = tuple(records)
        record_workers = None
        record_seconds = None
    if len(collected) != len(items):
        raise ValueError(f"got {len(collected)} records for {len(items)} corpus items")
    features = feature_rows(items, workers)
    by_index = {record["index"]: record for record in collected}
    rows = []
    for row in features["rows"]:
        record = by_index[row["index"]]
        if record["source"] != row["source"]:
            raise ValueError(f"record/feature mismatch at index {row['index']}")
        merged = dict(row)
        merged[SENSITIVITY] = record["sensitivity"]
        merged[CLASS_COUNT] = record["strict_class_count"]
        rows.append(merged)
    rows.sort(key=lambda item: item["index"])
    return {
        "rows": tuple(rows),
        "expression_count": len(rows),
        "features": FEATURE_NAMES,
        "ordered_features": ORDERED_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "parser_restating_features": PARSER_RESTATING_FEATURES,
        "target": SENSITIVITY,
        "target_definition": "S(E) = (strict semantic classes - 1) / 23, from grammar_matrix.representation_sensitivity",
        "feature_workers": features["workers"],
        "feature_wall_clock_seconds": features["wall_clock_seconds"],
        "record_workers": record_workers,
        "record_wall_clock_seconds": record_seconds,
        "cpu_count": os.cpu_count(),
    }


def ground_truth(table: Mapping[str, Any]) -> dict[str, Any]:
    """Re-derive the 0024 headline numbers from this table, so the report never quotes 0024 blind."""
    rows = table["rows"]
    sensitivities = [row[SENSITIVITY] for row in rows]
    rigid = [row for row in rows if row[CLASS_COUNT] == 1]
    return {
        "expression_count": len(rows),
        "sensitivity_distribution": dict(sorted(Counter(round(value, 6) for value in sensitivities).items())),
        "class_count_distribution": dict(sorted(Counter(row[CLASS_COUNT] for row in rows).items())),
        "rigid": len(rigid),
        "sensitive": len(rows) - len(rigid),
        "rigid_families": dict(sorted(Counter(row["family"] for row in rigid).items())),
        "mean_sensitivity": sum(sensitivities) / max(len(sensitivities), 1),
        "min_sensitivity": min(sensitivities) if sensitivities else None,
        "max_sensitivity": max(sensitivities) if sensitivities else None,
        "support_size_counts": dict(sorted(Counter(row["support_size"] for row in rows).items())),
    }


# ------------------------------------------------------------------------------ association math


def _pearson(left: Sequence[float], right: Sequence[float]) -> float | None:
    """Pearson correlation, or ``None`` when either side is constant.

    Restated here rather than imported: ``corpus_matrix._pearson`` is private to that module, and
    this one is only ever fed RANKS, which is what makes :func:`spearman` a Spearman.
    """
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


def average_ranks(values: Sequence[float]) -> list[float]:
    """Ranks with ties resolved to their average - required, since every feature here is heavily tied."""
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while end + 1 < len(order) and values[order[end + 1]] == values[order[position]]:
            end += 1
        average = (position + end) / 2 + 1
        for slot in range(position, end + 1):
            ranks[order[slot]] = average
        position = end + 1
    return ranks


def spearman(left: Sequence[float], right: Sequence[float]) -> float | None:
    """Tie-corrected Spearman rank correlation. ``None`` when either side has no variation."""
    if len(left) != len(right):
        raise ValueError(f"length mismatch: {len(left)} vs {len(right)}")
    return _pearson(average_ranks(left), average_ranks(right))


def group_spread(labels: Sequence[Any], values: Sequence[float]) -> dict[str, Any]:
    """Between-group spread of ``values`` over ``labels``, WITH the group sizes.

    ``eta_squared`` is the fraction of the total sum of squares that lies between groups. It is
    reported next to the sizes and the per-group means on purpose: a coefficient alone hides that a
    group may hold five expressions, and a spread computed over five expressions is not a finding.
    """
    if len(labels) != len(values):
        raise ValueError(f"length mismatch: {len(labels)} vs {len(values)}")
    buckets: dict[Any, list[float]] = {}
    for label, value in zip(labels, values):
        buckets.setdefault(label, []).append(value)
    total = len(values)
    grand_mean = sum(values) / total if total else 0.0
    total_ss = sum((value - grand_mean) ** 2 for value in values)
    between_ss = sum(len(group) * (sum(group) / len(group) - grand_mean) ** 2 for group in buckets.values())
    groups = [
        {
            "value": label,
            "size": len(group),
            "mean": sum(group) / len(group),
            "min": min(group),
            "max": max(group),
            "range": max(group) - min(group),
        }
        for label, group in sorted(buckets.items(), key=lambda item: str(item[0]))
    ]
    means = [entry["mean"] for entry in groups]
    return {
        "group_count": len(groups),
        "groups": tuple(groups),
        "group_sizes": {entry["value"]: entry["size"] for entry in groups},
        "smallest_group": min((entry["size"] for entry in groups), default=0),
        "between_group_spread": (max(means) - min(means)) if means else 0.0,
        "largest_within_group_range": max((entry["range"] for entry in groups), default=0.0),
        "eta_squared": (between_ss / total_ss) if total_ss > 0 else None,
        "total_sum_of_squares": total_ss,
    }


def _association(rows: Sequence[Mapping[str, Any]], name: str, target: str = SENSITIVITY) -> dict[str, Any]:
    """Association of one feature with the target: rank correlation, group spread, group sizes."""
    feature = FEATURE_BY_NAME[name]
    labels = [row[name] for row in rows]
    values = [row[target] for row in rows]
    spread = group_spread(labels, values)
    rho = spearman([float(value) for value in labels], values) if feature.kind == "ordered" else None
    return {
        "feature": name,
        "kind": feature.kind,
        "origin": feature.origin,
        "restates_the_parser": feature.restates_the_parser,
        "size": len(rows),
        "constant": spread["group_count"] <= 1,
        "spearman": rho,
        "spearman_note": None if feature.kind == "ordered" else "categorical: rank correlation is undefined",
        **spread,
    }


def predictor_strength(
    table: Mapping[str, Any],
    strata: Sequence[str] = TRAP_STRATUM,
    features: Sequence[str] = FEATURE_NAMES,
    target: str = SENSITIVITY,
) -> dict[str, Any]:
    """Single-feature association with ``S(E)``, overall AND within a fixed support size.

    The stratified half is the result. ``strata`` defaults to ``("support_size",)`` because that is
    exactly what the T6 trap demands be held fixed; pass a finer key (for instance
    ``("operator_profile", "parenthesis_pair_count")``) to hold the whole token shape fixed and see
    what the coefficients alone still explain.

    Every entry carries ``group_sizes`` alongside its coefficient. ``within_strata`` adds
    ``strata_with_variation`` - a feature constant inside every stratum cannot explain anything
    there, and reporting an overall coefficient for it would be a straight category error.
    """
    rows = table["rows"] if isinstance(table, Mapping) and "rows" in table else tuple(table)
    strata = tuple(strata)
    features = tuple(features)
    buckets: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(tuple(row[key] for key in strata), []).append(row)
    stratum_blocks = {}
    for key, subset in sorted(buckets.items(), key=lambda item: str(item[0])):
        values = [row[target] for row in subset]
        stratum_blocks[key] = {
            "stratum": dict(zip(strata, key)),
            "size": len(subset),
            "sensitivity_min": min(values),
            "sensitivity_max": max(values),
            "sensitivity_mean": sum(values) / len(values),
            "features": {name: _association(subset, name, target) for name in features},
        }
    total = len(rows)
    summary = {}
    for name in features:
        entries = [(block["size"], block["features"][name]) for block in stratum_blocks.values()]
        varying = [(size, entry) for size, entry in entries if not entry["constant"]]
        varying_total = sum(size for size, _ in varying)
        rhos = [(size, entry["spearman"]) for size, entry in varying if entry["spearman"] is not None]
        rho_total = sum(size for size, _ in rhos)
        etas = [(size, entry["eta_squared"]) for size, entry in varying if entry["eta_squared"] is not None]
        eta_total = sum(size for size, _ in etas)
        summary[name] = {
            "feature": name,
            "restates_the_parser": FEATURE_BY_NAME[name].restates_the_parser,
            "strata_count": len(stratum_blocks),
            "strata_with_variation": len(varying),
            "expressions_in_varying_strata": varying_total,
            "constant_in_every_stratum": not varying,
            "weighted_spearman": (sum(size * rho for size, rho in rhos) / rho_total) if rho_total else None,
            "weighted_abs_spearman": (sum(size * abs(rho) for size, rho in rhos) / rho_total) if rho_total else None,
            "weighted_eta_squared": (sum(size * eta for size, eta in etas) / eta_total) if eta_total else None,
            "pooled_eta_squared": (sum(size * eta for size, eta in etas) / total) if total else None,
            "smallest_group_across_strata": min(
                (entry["smallest_group"] for _, entry in entries if entry["group_count"] > 1), default=0
            ),
        }
    return {
        "target": target,
        "strata_features": strata,
        "expression_count": total,
        "stratum_count": len(stratum_blocks),
        "stratum_sizes": {key: block["size"] for key, block in stratum_blocks.items()},
        "overall": {name: _association(rows, name, target) for name in features},
        "within_strata": stratum_blocks,
        "within_strata_summary": summary,
        "trap": (
            "T6 forces part of any answer: |O(E)| == 1 cannot fragment at all, so an association "
            "with support_size restates the parser. The within-strata block is the result; the "
            "overall block is context."
        ),
    }


# -------------------------------------------------------------------------- explanatory partition


def explained_partition(
    table: Mapping[str, Any], features: Sequence[str], target: str = SENSITIVITY
) -> dict[str, Any]:
    """Condition on ``features`` and ask whether ``S(E)`` is constant inside every cell.

    This is the practical form of the question. A feature set *explains* sensitivity exactly when
    the within-cell range collapses to zero everywhere; anything else is a partial explanation whose
    size is measured here as ``uncollapsed_expressions``. Every cell is reported with its size, so a
    cell of five expressions can never be mistaken for a law.
    """
    rows = table["rows"] if isinstance(table, Mapping) and "rows" in table else tuple(table)
    features = tuple(features)
    for name in features:
        if name not in FEATURE_BY_NAME:
            raise KeyError(f"unknown feature: {name!r}")
    buckets: dict[tuple[Any, ...], list[float]] = {}
    for row in rows:
        buckets.setdefault(tuple(row[name] for name in features), []).append(row[target])
    cells = []
    for key, values in sorted(buckets.items(), key=lambda item: str(item[0])):
        cells.append(
            {
                "key": dict(zip(features, key)),
                "size": len(values),
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
                "mean": sum(values) / len(values),
                "distinct_values": tuple(sorted({round(value, 6) for value in values})),
            }
        )
    total = len(rows)
    collapsed = [cell for cell in cells if cell["range"] == 0.0]
    uncollapsed = [cell for cell in cells if cell["range"] > 0.0]
    collapsed_expressions = sum(cell["size"] for cell in collapsed)
    all_values = [row[target] for row in rows]
    return {
        "features": features,
        "expression_count": total,
        "cell_count": len(cells),
        "cells": tuple(cells),
        "baseline_range": (max(all_values) - min(all_values)) if all_values else 0.0,
        "max_cell_range": max((cell["range"] for cell in cells), default=0.0),
        "size_weighted_mean_range": (
            sum(cell["size"] * cell["range"] for cell in cells) / total if total else 0.0
        ),
        "collapsed_cells": len(collapsed),
        "collapsed_expressions": collapsed_expressions,
        "collapsed_fraction": collapsed_expressions / total if total else 0.0,
        "uncollapsed_cells": tuple(sorted(uncollapsed, key=lambda cell: (-cell["size"], str(cell["key"])))),
        "uncollapsed_expressions": total - collapsed_expressions,
        "explains_sensitivity": not uncollapsed,
        "smallest_cell": min((cell["size"] for cell in cells), default=0),
        "criterion": "the feature set explains S(E) exactly when every cell has range 0.0",
    }


# ------------------------------------------------------------------------------------- hold-out


def _fold(
    fit_rows: Sequence[Mapping[str, Any]],
    evaluate_rows: Sequence[Mapping[str, Any]],
    features: Sequence[str],
    target: str,
) -> dict[str, Any]:
    """Fit cell means on ``fit_rows``, score them on ``evaluate_rows``. No randomness anywhere."""
    buckets: dict[tuple[Any, ...], list[float]] = {}
    for row in fit_rows:
        buckets.setdefault(tuple(row[name] for name in features), []).append(row[target])
    cell_mean = {key: sum(values) / len(values) for key, values in buckets.items()}
    fit_values = [row[target] for row in fit_rows]
    fallback = sum(fit_values) / len(fit_values) if fit_values else 0.0

    errors = []
    baseline_errors = []
    unseen = 0
    for row in evaluate_rows:
        key = tuple(row[name] for name in features)
        if key in cell_mean:
            prediction = cell_mean[key]
        else:
            prediction = fallback
            unseen += 1
        errors.append(row[target] - prediction)
        baseline_errors.append(row[target] - fallback)
    count = max(len(errors), 1)
    mean_absolute = sum(abs(value) for value in errors) / count
    baseline_absolute = sum(abs(value) for value in baseline_errors) / count
    root_mean_square = sqrt(sum(value * value for value in errors) / count)
    baseline_root = sqrt(sum(value * value for value in baseline_errors) / count)
    return {
        "fit_size": len(fit_rows),
        "evaluate_size": len(evaluate_rows),
        "cells_fitted": len(cell_mean),
        "unseen_cells": unseen,
        "mean_absolute_error": mean_absolute,
        "root_mean_square_error": root_mean_square,
        "max_absolute_error": max((abs(value) for value in errors), default=0.0),
        "exact_predictions": sum(1 for value in errors if abs(value) < 1e-12),
        "exact_fraction": sum(1 for value in errors if abs(value) < 1e-12) / count,
        "baseline_mean_absolute_error": baseline_absolute,
        "baseline_root_mean_square_error": baseline_root,
        "mean_absolute_error_reduction": (
            1 - mean_absolute / baseline_absolute if baseline_absolute > 0 else None
        ),
    }


def holdout_check(
    table: Mapping[str, Any], features: Sequence[str], target: str = SENSITIVITY
) -> dict[str, Any]:
    """Deterministic out-of-sample check of the cell-mean predictor built on ``features``.

    The split is index parity, exactly as 0024 splits its corpus: no randomness and no seed, so two
    runs of this function on the same table return byte-identical numbers. Both directions are
    scored - even-fit/odd-evaluate and its mirror - because a single direction can be lucky.

    An unpredicted cell (one that appears only in the evaluation half) falls back to the fit half's
    global mean and is counted in ``unseen_cells``; a predictor that only works because every cell
    was seen is not a predictor, and that count is what shows it.
    """
    rows = table["rows"] if isinstance(table, Mapping) and "rows" in table else tuple(table)
    features = tuple(features)
    for name in features:
        if name not in FEATURE_BY_NAME:
            raise KeyError(f"unknown feature: {name!r}")
    even = [row for row in rows if row["index"] % 2 == 0]
    odd = [row for row in rows if row["index"] % 2 == 1]
    folds = {
        "even_fit": _fold(even, odd, features, target),
        "odd_fit": _fold(odd, even, features, target),
    }
    absolute = [fold["mean_absolute_error"] for fold in folds.values()]
    square = [fold["root_mean_square_error"] for fold in folds.values()]
    baseline = [fold["baseline_mean_absolute_error"] for fold in folds.values()]
    return {
        "features": features,
        "split": "index parity - row['index'] % 2, the deterministic even/odd split 0024 uses",
        "expression_count": len(rows),
        "half_sizes": {"even": len(even), "odd": len(odd)},
        "folds": folds,
        "mean_absolute_error": sum(absolute) / len(absolute),
        "root_mean_square_error": sum(square) / len(square),
        "baseline_mean_absolute_error": sum(baseline) / len(baseline),
        "worst_fold_mean_absolute_error": max(absolute),
        "total_unseen_cells": sum(fold["unseen_cells"] for fold in folds.values()),
        "exact_fraction": sum(fold["exact_fraction"] for fold in folds.values()) / len(folds),
        "note": (
            "a predictor that is not checked out of sample is not a finding; this one is checked in "
            "both directions of the same deterministic split"
        ),
    }


def leave_one_group_out_check(
    table: Mapping[str, Any],
    features: Sequence[str],
    group: Sequence[str] = ("operator_profile", "parenthesis_pair_count"),
    target: str = SENSITIVITY,
) -> dict[str, Any]:
    """The harder deterministic hold-out: withhold a whole token shape, not every other index.

    :func:`holdout_check` splits by index parity, so both halves contain every token shape and the
    predictor is only ever asked about coefficients it has already seen in that shape. That is the
    check 0024's split protocol prescribes, and it is not enough on its own to claim the SHAPE half
    of a predictor generalizes. This function withholds one whole ``group`` at a time - by default
    the token shape ``(operator profile, parenthesis pairs)`` - and scores the predictor on it.

    There is still no randomness: the groups are the corpus's own distinct values, taken in sorted
    order. A predictor whose cells all name the withheld shape will miss every cell here and fall
    back to the fit mean; ``unseen_cells`` says exactly that, and the resulting error is the honest
    answer to "does this transfer to a token sequence shaped differently".
    """
    rows = table["rows"] if isinstance(table, Mapping) and "rows" in table else tuple(table)
    features = tuple(features)
    group = tuple(group)
    for name in (*features, *group):
        if name not in FEATURE_BY_NAME:
            raise KeyError(f"unknown feature: {name!r}")
    buckets: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(tuple(row[name] for name in group), []).append(row)
    folds = {}
    for key in sorted(buckets, key=str):
        held = buckets[key]
        rest = [row for other, subset in buckets.items() if other != key for row in subset]
        folds[key] = _fold(rest, held, features, target)
    scored = [(fold["evaluate_size"], fold) for fold in folds.values()]
    total = sum(size for size, _ in scored)
    return {
        "features": features,
        "group": group,
        "split": "leave one token shape out; groups are the corpus's own distinct values, sorted",
        "group_count": len(folds),
        "group_sizes": {key: len(subset) for key, subset in sorted(buckets.items(), key=lambda item: str(item[0]))},
        "folds": folds,
        "mean_absolute_error": sum(size * fold["mean_absolute_error"] for size, fold in scored) / total,
        "baseline_mean_absolute_error": sum(
            size * fold["baseline_mean_absolute_error"] for size, fold in scored
        )
        / total,
        "worst_fold_mean_absolute_error": max(fold["mean_absolute_error"] for fold in folds.values()),
        "exact_fraction": sum(size * fold["exact_fraction"] for size, fold in scored) / total,
        "total_unseen_cells": sum(fold["unseen_cells"] for fold in folds.values()),
    }


# ------------------------------------------------------------------------------------ narrative


def within_support_report(
    table: Mapping[str, Any], features: Sequence[str] = FEATURE_NAMES, target: str = SENSITIVITY
) -> dict[str, Any]:
    """The trap, answered in one object: which features keep an association once |O(E)| is fixed.

    ``retained`` lists the features that still vary and still move ``S(E)`` inside at least one
    support size; ``dead`` lists the features that are constant inside every support size and
    therefore explain nothing there, whatever their overall coefficient says.
    """
    strength = predictor_strength(table, TRAP_STRATUM, features, target)
    summary = strength["within_strata_summary"]
    retained = tuple(
        sorted(
            (name for name, entry in summary.items() if not entry["constant_in_every_stratum"]),
            key=lambda name: -abs(summary[name]["weighted_eta_squared"] or 0.0),
        )
    )
    dead = tuple(name for name, entry in summary.items() if entry["constant_in_every_stratum"])
    return {
        "strata_features": TRAP_STRATUM,
        "stratum_sizes": strength["stratum_sizes"],
        "retained_features": retained,
        "dead_features": dead,
        "retained_independent_features": tuple(
            name for name in retained if not FEATURE_BY_NAME[name].restates_the_parser
        ),
        "retained_parser_restating_features": tuple(
            name for name in retained if FEATURE_BY_NAME[name].restates_the_parser
        ),
        "weighted_eta_squared": {name: summary[name]["weighted_eta_squared"] for name in retained},
        "weighted_spearman": {name: summary[name]["weighted_spearman"] for name in retained},
        "strength": strength,
    }


def feature_catalog() -> tuple[dict[str, Any], ...]:
    """The closed feature set as data, so a report can never drift from the code."""
    return tuple(
        {
            "name": feature.name,
            "kind": feature.kind,
            "origin": feature.origin,
            "restates_the_parser": feature.restates_the_parser,
            "motivation": feature.motivation,
        }
        for feature in FEATURES
    )


def feature_values(table: Mapping[str, Any], name: str) -> dict[Any, int]:
    """Value histogram of one feature over a table - the cheapest way to see a constant feature."""
    rows = table["rows"] if isinstance(table, Mapping) and "rows" in table else tuple(table)
    return dict(sorted(Counter(row[name] for row in rows).items(), key=lambda item: str(item[0])))


def constant_features(table: Mapping[str, Any], features: Iterable[str] = FEATURE_NAMES) -> tuple[str, ...]:
    """Features that take exactly one value on this corpus and can therefore predict nothing."""
    rows = table["rows"] if isinstance(table, Mapping) and "rows" in table else tuple(table)
    return tuple(name for name in features if len({row[name] for row in rows}) <= 1)
