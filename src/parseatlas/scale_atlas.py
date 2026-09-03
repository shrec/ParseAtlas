"""Two-tier scale sweep: is the founding ``24 -> 8`` collapse special, or one point in a distribution?

Experiment 0031. The founding observation of this project is that ``2*t + 1 - t/2`` produces `24`
grammar states and `8` semantic classes. Experiment 0024 already showed on `3125` controlled
expressions that `8` is *not* the typical outcome - the mode there is `4` - but it did so on a single
group of five templates. This module answers the same question at a scale and family spread where
the answer can no longer be an accident of one template group.

Two tiers, because the two questions cost three orders of magnitude apart:

* :func:`structural_sweep` counts distinct ASTs, operator support and depth. It executes **no SymPy
  call at all** (``sympy`` is still imported, because :mod:`parseatlas.canonical` imports it for
  :func:`~parseatlas.canonical.ast_to_dict`'s neighbours - but nothing on this path evaluates a
  SymPy expression). That last sentence is an ASSERTION about the code path and not a counted
  quantity - nothing here is instrumented, so there is no number to count; its evidence is
  ``test_structural_path_calls_no_sympy``, which replaces ``canonical.to_sympy``,
  ``canonical.simplify`` and ``canonical.solve`` with a function that raises and runs the whole
  sweep through unharmed. Measured sequentially on this 16-core host at `1.20 ms` per expression
  (`1296` expressions in `1.56 s`), so it runs at millions.
* :func:`semantic_sweep` computes ``C(E)`` with the project's own semantic-class key by reusing
  :func:`parseatlas.corpus_matrix.expression_classes`, which canonicalizes each DISTINCT AST once.
  Measured sequentially at `84.6 ms` per expression on a stratified sample of the published corpus
  (`106` expressions in `8.97 s`), so it runs at `1e5`.

The NULL MODEL is mandatory here and is carried in every report. Operator-support reduction
(experiment 0019) bounds the distinct ASTs of the `24` strict grammars by ``factorial(|O(E)|)``,
so part of every distribution is forced by the parser and is not a finding. Both reports therefore
publish the support-size distribution next to the headline and condition ``C(E)`` on support size.

Conditioning on the null model is not a way out of the corpus, though, and :func:`distribution_report`
says so with a measurement rather than a caveat: ``family_mix_ablation`` recomputes the same
conditional distribution with :data:`SATURATING_DIV_FAMILIES` removed, so a conditional mode that
only exists because three families supply it cannot be read as a property of the stratum.

The corpus is a Cartesian product with no randomness and no seed. :class:`CorpusSpec` is index
addressable, so a worker process regenerates its own slice from the spec instead of receiving a
million pickled dictionaries; that is what keeps the structural tier's memory flat at `1e6`.
"""

import json
import os
import time
from collections import Counter
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
from math import factorial
from typing import Any

from sympy import Poly, Pow, nan, sympify, zoo
from sympy.polys.polyerrors import PolynomialError

from .canonical import ast_to_dict, operation_cost
from .corpus_matrix import expression_classes, resolve_worker_count, support_block_key
from .critical_path import depth_profile
from .grammar import Grammar, all_grammars
from .parser import parse
from .support_reduction import operator_support

#: The 25 registered grammars: the tied-level control ``G0`` plus the 24 strict orderings.
GRAMMARS: tuple[Grammar, ...] = all_grammars()
STRICT_GRAMMARS: tuple[Grammar, ...] = tuple(grammar for grammar in GRAMMARS if grammar.id != "G0")

PARAMETER_NAMES: tuple[str, ...] = ("a", "b", "c", "d")

#: Coefficient values for ``free`` slots. ``0`` and ``1`` are IN on purpose: 0024 showed that the
#: coefficients move ``C(E)`` while the template is held fixed, and the degenerate coefficients are
#: exactly where a term can vanish and the collapse can reach a constant.
DEFAULT_FREE_VALUES: tuple[int, ...] = tuple(range(16))

#: Coefficient values for ``nonzero`` slots, position-matched to :data:`DEFAULT_FREE_VALUES` and of
#: the same length, so every family has exactly ``values_count ** 4`` expressions. A slot is marked
#: ``nonzero`` when a ``0`` there would be a *tokenizer* error rather than a measurement: the
#: Generation 1 number token is ``\d+(?:/\d+)?``, so an unspaced ``3/0`` is one literal
#: ``Fraction(3, 0)`` and raises before any grammar is involved.
DEFAULT_NONZERO_VALUES: tuple[int, ...] = tuple(range(1, 17))

#: ``(family, template, slot kinds for (a, b, c, d))``.
#:
#: Sixteen families spanning the shapes the card names: affine, linear-with-division, quadratic,
#: cubic, rational, mixed operator chains, repeated-variable forms and degenerate coefficients.
#: Three deliberate pairs isolate one variable each:
#:
#: * ``linear_ratio_literal`` / ``linear_ratio_spaced`` - the SAME shape where ``{c}/{d}`` is one
#:   rational literal versus ``{c} / {d}`` where ``/`` is a real operator. Spacing alone moves
#:   ``|O(E)|`` from `3` to `4` and therefore moves the null model.
#: * ``mixed_chain`` / ``mixed_chain_spaced`` - the same contrast on 0024's mixed chain.
#: * ``affine`` / ``affine_div`` - ``affine_div`` is the founding shape ``a*x + b - c*x/d``.
FAMILY_TEMPLATES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("affine", "{a}*x + {b} - {c}*x + {d}", ("free", "free", "free", "free")),
    ("affine_div", "{a}*x + {b} - {c}*x/{d}", ("free", "free", "free", "nonzero")),
    ("linear_ratio_literal", "{a}*x + {b} - {c}/{d}*x", ("free", "free", "free", "nonzero")),
    ("linear_ratio_spaced", "{a}*x + {b} - {c} / {d}*x", ("free", "free", "free", "nonzero")),
    ("quadratic", "{a}*x*x + {b}*x - {c}/{d}", ("free", "free", "free", "nonzero")),
    ("quadratic_div", "{a}*x*x + {b}*x - {c}*x/{d}", ("free", "free", "free", "nonzero")),
    ("cubic", "{a}*x*x*x + {b}*x*x - {c}*x + {d}", ("free", "free", "free", "free")),
    ("cubic_div", "{a}*x*x*x + {b}*x*x - {c}*x/{d}", ("free", "free", "free", "nonzero")),
    ("rational", "({a}*x + {b})/({c}*x - {d})", ("free", "free", "free", "free")),
    ("rational_nested", "{a}/({b}*x + {c}) - {d}", ("free", "free", "free", "free")),
    ("mixed_chain", "{a}/{b} + {c}*x - {d}/{a}", ("nonzero", "nonzero", "free", "free")),
    ("mixed_chain_spaced", "{a} / {b} + {c}*x - {d} / {a}", ("nonzero", "nonzero", "free", "free")),
    ("chain_long", "{a}*x + {b}/x - {c}*x + {d}/x", ("free", "free", "free", "free")),
    ("repeated_variable", "{a}*x/x + {b}*x - {c}*x/{d}", ("free", "free", "free", "nonzero")),
    ("repeated_var_square", "x*x - {a}*x + x/{b} - {c}*x*x + {d}", ("free", "nonzero", "free", "free")),
    ("unit_scaled", "1*{a}*x + {b}*1 - {c}*x/1 + {d}", ("free", "free", "free", "free")),
)

#: ``16 families * 16 ** 4 = 1_048_576`` expressions - the structural tier's published scale.
STRUCTURAL_VALUES_COUNT: int = 16

#: ``16 families * 9 ** 4 = 104_976`` expressions - the semantic tier's published scale.
SEMANTIC_VALUES_COUNT: int = 9

#: Upper bound on the derived chunk size in both tiers. One chunk is one pickled task, so a
#: per-item task at `1e6` would spend more time in the queue than in the parser; capping the other
#: way keeps a single slow chunk from becoming the whole tail of the run.
DEFAULT_CHUNK_SIZE: int = 4096

#: Ceiling on the examples kept per phenomenon in :func:`collapse_report`.
DEFAULT_EXAMPLE_LIMIT: int = 6


# --------------------------------------------------------------------------------------- corpus


@dataclass(frozen=True)
class CorpusSpec:
    """Index-addressable deterministic corpus. No randomness and no seed is involved.

    Expression ``index`` decomposes as ``index = tuple_index * family_count + family_position``, so
    the families are interleaved inside every coefficient tuple exactly as in 0024. ``tuple_index``
    is read as a ``values_count``-base number with four big-endian digits bound to ``(a, b, c, d)``,
    which is precisely ``itertools.product(range(values_count), repeat=4)`` order.

    Being addressable is not a convenience: :func:`structural_sweep` hands a worker an index RANGE
    and the worker rebuilds its own slice, so a `1e6` sweep never materializes `1e6` dictionaries.
    """

    values_count: int = SEMANTIC_VALUES_COUNT
    templates: tuple[tuple[str, str, tuple[str, ...]], ...] = FAMILY_TEMPLATES
    free_values: tuple[int, ...] = DEFAULT_FREE_VALUES
    nonzero_values: tuple[int, ...] = DEFAULT_NONZERO_VALUES

    def __post_init__(self) -> None:
        if self.values_count < 1:
            raise ValueError(f"values_count must be at least 1; got {self.values_count}")
        if self.values_count > min(len(self.free_values), len(self.nonzero_values)):
            raise ValueError(
                f"values_count {self.values_count} exceeds the available value sequences "
                f"({len(self.free_values)} free, {len(self.nonzero_values)} nonzero)"
            )
        if not self.templates:
            raise ValueError("a corpus spec needs at least one family template")

    @property
    def family_count(self) -> int:
        return len(self.templates)

    @property
    def expressions_per_family(self) -> int:
        return self.values_count ** len(PARAMETER_NAMES)

    @property
    def size(self) -> int:
        return self.family_count * self.expressions_per_family

    @property
    def families(self) -> tuple[str, ...]:
        return tuple(family for family, _, _ in self.templates)

    def expression(self, index: int) -> dict[str, Any]:
        """Return the corpus item at ``index`` without materializing its neighbours."""
        if not 0 <= index < self.size:
            raise IndexError(f"index {index} outside corpus of size {self.size}")
        tuple_index, family_position = divmod(index, self.family_count)
        family, template, kinds = self.templates[family_position]
        base = self.values_count
        parameters: dict[str, int] = {}
        for position, (name, kind) in enumerate(zip(PARAMETER_NAMES, kinds)):
            digit = tuple_index // base ** (len(PARAMETER_NAMES) - 1 - position) % base
            sequence = self.nonzero_values if kind == "nonzero" else self.free_values
            parameters[name] = sequence[digit]
        return {
            "index": index,
            "family": family,
            "source": template.format(**parameters),
            "parameters": parameters,
            "tuple_index": tuple_index,
        }

    def items(self, start: int = 0, stop: int | None = None) -> Iterator[dict[str, Any]]:
        return (self.expression(index) for index in range(start, self.size if stop is None else stop))

    def generation(self) -> dict[str, Any]:
        """Everything needed to rebuild this corpus from the published report alone."""
        return {
            "values_count": self.values_count,
            "free_values": list(self.free_values[: self.values_count]),
            "nonzero_values": list(self.nonzero_values[: self.values_count]),
            "parameter_names": list(PARAMETER_NAMES),
            "templates": {family: template for family, template, _ in self.templates},
            "slot_kinds": {family: list(kinds) for family, _, kinds in self.templates},
            "family_count": self.family_count,
            "expressions_per_family": self.expressions_per_family,
            "size": self.size,
            "index_order": (
                "index = tuple_index * family_count + family_position; tuple_index is a "
                "values_count-base number with four big-endian digits bound to (a, b, c, d), which "
                "is itertools.product(range(values_count), repeat=4) order"
            ),
            "slot_rule": (
                "a 'free' slot reads position i of free_values, a 'nonzero' slot reads position i "
                "of nonzero_values; both sequences have the same length so every family has exactly "
                "values_count ** 4 expressions"
            ),
            "nonzero_reason": (
                "the Generation 1 number token is \\d+(?:/\\d+)? so an unspaced '3/0' is one literal "
                "Fraction(3, 0) and raises in the tokenizer; only those slots are constrained"
            ),
            "randomness": "none; the corpus is a Cartesian product and is regenerable from these fields alone",
        }


def structural_spec() -> CorpusSpec:
    """The published structural corpus: ``16 * 16 ** 4 = 1_048_576`` expressions."""
    return CorpusSpec(values_count=STRUCTURAL_VALUES_COUNT)


def semantic_spec() -> CorpusSpec:
    """The published semantic corpus: ``16 * 9 ** 4 = 104_976`` expressions."""
    return CorpusSpec(values_count=SEMANTIC_VALUES_COUNT)


def generate_corpus(spec: CorpusSpec | None = None) -> dict[str, Any]:
    """Materialize a spec. Used by the semantic tier and the tests; the structural tier streams."""
    spec = spec or semantic_spec()
    expressions = tuple(spec.items())
    counts = Counter(item["family"] for item in expressions)
    return {
        "expressions": expressions,
        "size": len(expressions),
        "families": spec.families,
        "family_counts": {family: counts[family] for family in spec.families},
        "generation": spec.generation(),
    }


# ---------------------------------------------------------------------------- execution helpers


def _plan(spec: "CorpusSpec", workers: int | None, chunk_size: int | None) -> tuple[tuple[tuple[int, int], ...], int]:
    """Resolve the worker count from the EXPRESSION count, then size the chunks to fit it.

    The worker count is derived from :func:`parseatlas.corpus_matrix.resolve_worker_count`, which
    reads the observed core count and leaves one core of headroom - never a hardcoded constant. It
    is resolved from ``spec.size`` and not from the number of chunks, because sizing the chunks is
    the step that comes AFTER the decision; resolving from chunks would let a coarse chunking talk
    the sweep into running sequentially.
    """
    resolved = resolve_worker_count(spec.size, workers)
    if chunk_size is None:
        # four chunks per worker: enough slices to even out a loaded machine, few enough that the
        # per-task pickling of the spec stays negligible next to the work in the slice.
        chunk_size = min(DEFAULT_CHUNK_SIZE, max(1, spec.size // (resolved * 4)))
    chunk_size = max(1, chunk_size)
    ranges = tuple((start, min(start + chunk_size, spec.size)) for start in range(0, spec.size, chunk_size))
    return ranges, max(1, min(resolved, len(ranges)))


def _run_chunks(
    function: Callable[[Any], Any], payloads: Sequence[Any], workers: int
) -> tuple[list[Any], int, float]:
    """Map ``function`` over ``payloads``, sequentially or across processes.

    Expressions are independent and both tiers are CPU-bound, so processes are the right primitive
    (threads would sit behind the GIL in the parser and in SymPy). Parallelism changes only how fast
    the sweep is measured: ``pool.map`` preserves input order, every accumulator merge is
    commutative, and the sequential==parallel tests pin that the outputs are identical.
    """
    started = time.perf_counter()
    if workers <= 1 or len(payloads) <= 1:
        return [function(payload) for payload in payloads], 1, time.perf_counter() - started
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(function, payloads))
    return results, workers, time.perf_counter() - started


def _as_distribution(counter: Counter) -> dict[int, int]:
    return dict(sorted(counter.items()))


def _mode(counter: Counter) -> int | None:
    """Most frequent value; ties broken toward the SMALLEST value so the mode is deterministic."""
    if not counter:
        return None
    return min(counter, key=lambda value: (-counter[value], value))


# ------------------------------------------------------------------------- structural tier (1e6)


def structural_record(item: dict[str, Any]) -> dict[str, Any]:
    """Parse one expression under all 25 grammars and read structure off the ASTs. No SymPy call.

    ``distinct_ast_count`` covers all 25 grammars; ``strict_distinct_ast_count`` covers the 24
    strict orderings only, because ``factorial(|O(E)|)`` is a bound on the STRICT grammars
    (experiment 0019). ``G0`` restricted to ``O(E)`` keeps its tied level and therefore forms a
    26th support block of its own, so the all-25 count is bounded by ``factorial(|O(E)|) + 1``.
    """
    source = item["source"]
    support = operator_support(source)
    blocks: dict[str, set[str]] = {}
    strict_forms: set[str] = set()
    forms: set[str] = set()
    depths: list[int] = []
    for grammar in GRAMMARS:
        node = parse(source, grammar)
        blob = json.dumps(ast_to_dict(node), sort_keys=True)
        forms.add(blob)
        depths.append(operation_cost(node)["depth"])
        if grammar.id != "G0":
            strict_forms.add(blob)
            blocks.setdefault(support_block_key(grammar, support), set()).add(blob)
    bound = factorial(len(support))
    return {
        "index": item["index"],
        "family": item["family"],
        "source": source,
        "support": support,
        "support_size": len(support),
        "ast_bound": bound,
        "distinct_ast_count": len(forms),
        "strict_distinct_ast_count": len(strict_forms),
        "support_block_count": len(blocks),
        "max_asts_in_a_block": max(len(members) for members in blocks.values()),
        "saturates_bound": len(strict_forms) == bound,
        "exceeds_bound": len(strict_forms) > bound,
        "min_depth": min(depths),
        "max_depth": max(depths),
        "depth_spread": max(depths) - min(depths),
    }


def _new_structural_block() -> dict[str, Any]:
    return {
        "count": 0,
        "distinct_ast": Counter(),
        "strict_distinct_ast": Counter(),
        "support_size": Counter(),
        "depth_spread": Counter(),
        "min_depth": Counter(),
        "max_depth": Counter(),
        "support_block_count": Counter(),
        "strict_distinct_ast_by_support": {},
        "saturated": 0,
        "bound_violations": 0,
        "block_violations": 0,
    }


_STRUCTURAL_COUNTERS = (
    "distinct_ast",
    "strict_distinct_ast",
    "support_size",
    "depth_spread",
    "min_depth",
    "max_depth",
    "support_block_count",
)
_STRUCTURAL_TOTALS = ("saturated", "bound_violations", "block_violations")


def _accumulate_structural(block: dict[str, Any], record: dict[str, Any]) -> None:
    block["count"] += 1
    block["distinct_ast"][record["distinct_ast_count"]] += 1
    block["strict_distinct_ast"][record["strict_distinct_ast_count"]] += 1
    block["support_size"][record["support_size"]] += 1
    block["depth_spread"][record["depth_spread"]] += 1
    block["min_depth"][record["min_depth"]] += 1
    block["max_depth"][record["max_depth"]] += 1
    block["support_block_count"][record["support_block_count"]] += 1
    conditioned = block["strict_distinct_ast_by_support"].setdefault(record["support_size"], Counter())
    conditioned[record["strict_distinct_ast_count"]] += 1
    block["saturated"] += record["saturates_bound"]
    block["bound_violations"] += record["exceeds_bound"]
    block["block_violations"] += record["max_asts_in_a_block"] > 1


def _merge_structural(into: dict[str, Any], other: dict[str, Any]) -> None:
    into["count"] += other["count"]
    for key in _STRUCTURAL_COUNTERS:
        into[key].update(other[key])
    for size, counter in other["strict_distinct_ast_by_support"].items():
        into["strict_distinct_ast_by_support"].setdefault(size, Counter()).update(counter)
    for key in _STRUCTURAL_TOTALS:
        into[key] += other[key]


def _structural_slice(payload: tuple[CorpusSpec, int, int]) -> dict[str, Any]:
    """Module-level pool function: rebuild an index range and return only the aggregates.

    It must stay module-level (not a closure) so the Windows ``spawn`` start method can pickle it by
    reference, and it must return aggregates rather than records so a `1e6` sweep stays memory flat.
    """
    spec, start, stop = payload
    overall = _new_structural_block()
    families: dict[str, dict[str, Any]] = {}
    examples: dict[int, tuple[int, str, str]] = {}
    for item in spec.items(start, stop):
        record = structural_record(item)
        _accumulate_structural(overall, record)
        _accumulate_structural(families.setdefault(record["family"], _new_structural_block()), record)
        value = record["strict_distinct_ast_count"]
        if value not in examples:
            examples[value] = (record["index"], record["family"], record["source"])
    return {"overall": overall, "families": families, "examples": examples}


#: Structural quantities that a coefficient substitution cannot move, if the parser really only
#: reads token KINDS and operator binding powers. Checked, not assumed - see
#: :func:`_coefficient_invariance`.
_INVARIANT_CANDIDATES = (
    "distinct_ast",
    "strict_distinct_ast",
    "support_size",
    "support_block_count",
    "min_depth",
    "max_depth",
    "depth_spread",
)


def _coefficient_invariance(families: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Does any structural quantity move when only the coefficients change?

    The parser compares binding powers and token kinds; a coefficient is neither. If that reasoning
    is right, every structural distribution inside one family is a single value repeated
    ``values_count ** 4`` times, and a million-expression structural sweep carries exactly as much
    information as one expression per family. This function measures that instead of asserting it.
    """
    per_family = {
        family: {key: sorted(block[key]) for key in _INVARIANT_CANDIDATES}
        for family, block in families.items()
    }
    varying = {
        family: [key for key, values in entry.items() if len(values) > 1]
        for family, entry in per_family.items()
    }
    return {
        "quantities": list(_INVARIANT_CANDIDATES),
        "values_per_family": {
            family: {key: values[0] if len(values) == 1 else values for key, values in entry.items()}
            for family, entry in per_family.items()
        },
        "families_with_a_varying_quantity": {family: keys for family, keys in varying.items() if keys},
        "invariant": not any(varying.values()),
        "claim": (
            "the parser reads token kinds and binding powers, and a coefficient is neither, so every "
            "structural quantity is constant inside one template family"
        ),
    }


def _structural_summary(block: dict[str, Any]) -> dict[str, Any]:
    count = max(block["count"], 1)
    strict = block["strict_distinct_ast"]
    return {
        "expression_count": block["count"],
        "distinct_ast_distribution": _as_distribution(block["distinct_ast"]),
        "strict_distinct_ast_distribution": _as_distribution(strict),
        "strict_distinct_ast_mode": _mode(strict),
        "strict_distinct_ast_mode_share": strict[_mode(strict)] / count if strict else 0.0,
        "mean_strict_distinct_ast": sum(value * n for value, n in strict.items()) / count,
        "support_size_distribution": _as_distribution(block["support_size"]),
        "support_block_count_distribution": _as_distribution(block["support_block_count"]),
        "depth_spread_distribution": _as_distribution(block["depth_spread"]),
        "min_depth_distribution": _as_distribution(block["min_depth"]),
        "max_depth_distribution": _as_distribution(block["max_depth"]),
        "strict_distinct_ast_by_support_size": {
            size: {
                "distribution": _as_distribution(counter),
                "expression_count": sum(counter.values()),
                "bound": factorial(size),
                "mode": _mode(counter),
                "saturated_share": counter[factorial(size)] / max(sum(counter.values()), 1),
            }
            for size, counter in sorted(block["strict_distinct_ast_by_support"].items())
        },
        "saturating_the_bound": block["saturated"],
        "saturating_share": block["saturated"] / count,
        "bound_violations": block["bound_violations"],
        "support_block_violations": block["block_violations"],
        "depth_varies": block["count"] - block["depth_spread"][0],
        "depth_varies_share": (block["count"] - block["depth_spread"][0]) / count,
    }


def structural_sweep(
    spec: CorpusSpec | None = None,
    workers: int | None = None,
    chunk_size: int | None = None,
) -> dict[str, Any]:
    """Distinct-AST count, operator support, support-block structure and depth spread, at millions.

    Every number here is read off ASTs alone; no SymPy expression is ever evaluated on this path.
    ``bound_violations`` and ``support_block_violations`` are the mechanical audit of experiment
    0019 re-run at this scale: both must stay ``0``.
    """
    spec = spec or structural_spec()
    ranges, resolved = _plan(spec, workers, chunk_size)
    payloads = [(spec, start, stop) for start, stop in ranges]
    chunks, used, elapsed = _run_chunks(_structural_slice, payloads, resolved)

    overall = _new_structural_block()
    families: dict[str, dict[str, Any]] = {}
    examples: dict[int, tuple[int, str, str]] = {}
    for chunk in chunks:
        _merge_structural(overall, chunk["overall"])
        for family, block in chunk["families"].items():
            _merge_structural(families.setdefault(family, _new_structural_block()), block)
        for value, example in chunk["examples"].items():
            if value not in examples or example[0] < examples[value][0]:
                examples[value] = example
    return {
        "tier": "structural",
        # NOT a counter. Nothing on this path is instrumented, so a "sympy_calls: 0" field would be
        # a literal wearing a measurement's clothes. The claim is an assertion about the code path
        # and it is published as one, with the test that actually establishes it named in place.
        "sympy_call_claim": {
            "claim": "no SymPy expression is evaluated on the structural path",
            "kind": "assertion, not a counted quantity",
            "evidence": (
                "test_structural_path_calls_no_sympy replaces canonical.to_sympy, canonical.simplify "
                "and canonical.solve with a function that raises, then runs this sweep to completion"
            ),
        },
        "expression_count": overall["count"],
        "grammar_count": len(GRAMMARS),
        "strict_grammar_count": len(STRICT_GRAMMARS),
        "generation": spec.generation(),
        "overall": _structural_summary(overall),
        "families": {family: _structural_summary(block) for family, block in families.items()},
        "coefficient_invariance": _coefficient_invariance(families),
        "examples_by_strict_distinct_ast": {
            value: {"index": example[0], "family": example[1], "source": example[2]}
            for value, example in sorted(examples.items())
        },
        "null_model": (
            "the 24 strict grammars split into factorial(|O(E)|) support-reduction blocks and every "
            "grammar inside one block yields a byte-identical AST, so strict distinct ASTs are "
            "bounded by factorial(|O(E)|); G0 keeps its tied level and forms a block of its own, so "
            "the all-25 count is bounded by factorial(|O(E)|) + 1"
        ),
        "chunk_count": len(ranges),
        "chunk_size": ranges[0][1] - ranges[0][0] if ranges else 0,
        "workers": used,
        "cpu_count": os.cpu_count(),
        "wall_clock_seconds": elapsed,
    }


# --------------------------------------------------------------------------- semantic tier (1e5)


def _degree(expression: Any, variable: Any) -> int | None:
    """Polynomial degree, or ``None`` when the canonical form is not a polynomial in ``variable``.

    This is the degree half of :func:`parseatlas.properties.polynomial_properties`. That function is
    not reused here because it also runs ``factor``, ``solve`` and a discriminant, and those would
    dominate a `1e5` sweep by an order of magnitude while contributing nothing this report reads.
    """
    try:
        polynomial = Poly(expression, variable)
    except (TypeError, ValueError, PolynomialError):
        return None
    degree = polynomial.degree()
    return None if degree < 0 else int(degree)


def _division_count(expression: Any) -> int:
    """Number of distinct negative-integer powers in the canonical form.

    ``a/b`` reaches SymPy as ``Mul(a, Pow(b, -1))``, so a division survives canonicalization exactly
    as a ``Pow`` with a negative exponent. Counting distinct such subexpressions is what "the
    division count of the canonical form" means throughout this experiment.
    """
    return sum(1 for power in expression.atoms(Pow) if power.exp.is_number and power.exp.is_negative)


def _class_metrics(text: str) -> dict[str, Any]:
    """Constant / degree / division metrics for one semantic class, from its canonical text.

    The class key itself is never recomputed here: :func:`expression_classes` owns it, and this
    function only re-reads its published canonical text. ``sympify`` round-trips SymPy's own string
    printer, and ``sympify_failed`` counts any case where it did not, so a silent metric is
    impossible.
    """
    try:
        expression = sympify(text)
    except Exception:  # pragma: no cover - measured to be 0 on every published corpus
        return {"constant": False, "degenerate": False, "degree": None, "division_count": None, "sympify_failed": True}
    symbols = sorted(expression.free_symbols, key=str)
    degenerate = bool(expression.has(zoo) or expression.has(nan))
    return {
        "constant": not symbols and not degenerate,
        "degenerate": degenerate,
        "degree": _degree(expression, symbols[0]) if symbols else (None if degenerate else 0),
        "division_count": _division_count(expression),
        "sympify_failed": False,
    }


def _spread(values: Sequence[int]) -> int:
    return max(values) - min(values) if values else 0


def semantic_record(item: dict[str, Any]) -> dict[str, Any]:
    """One expression's semantic record: ``C(E)``, the AST count and the collapse metrics.

    The partition comes from :func:`parseatlas.corpus_matrix.expression_classes`, which uses the
    project's own key ``(canonical expression, domain, excluded points)`` and canonicalizes each
    DISTINCT AST exactly once. Depths come from
    :func:`parseatlas.critical_path.depth_profile`. Nothing about the class key is redefined here;
    ``test_scale_atlas`` pins that this record's partition MEMBERSHIP equals
    :func:`parseatlas.analyze.analyze_expression`'s.
    """
    source = item["source"]
    result = expression_classes(source)
    classes = result["classes"]
    support = operator_support(source)
    profile = depth_profile(source)
    depth_by_grammar = {entry["id"]: entry["depth"] for entry in profile["grammars"]}

    metrics = {class_id: _class_metrics(key["canonical"]) for class_id, key in result["class_keys"].items()}
    degrees = sorted({entry["degree"] for entry in metrics.values() if entry["degree"] is not None})
    divisions = sorted({entry["division_count"] for entry in metrics.values() if entry["division_count"] is not None})
    # constant / degenerate / variable partition the classes exactly: degenerate first (a class
    # carrying zoo or nan is neither a value nor a function), then symbol-free, then the rest.
    degenerate_classes = sum(entry["degenerate"] for entry in metrics.values())
    constant_classes = sum(entry["constant"] for entry in metrics.values())
    variable_classes = len(metrics) - degenerate_classes - constant_classes
    non_polynomial_classes = sum(
        1 for entry in metrics.values() if entry["degree"] is None and not entry["degenerate"]
    )

    depths_per_class: dict[str, list[int]] = {}
    for grammar_id, class_id in classes.items():
        depths_per_class.setdefault(class_id, []).append(depth_by_grammar[grammar_id])
    control_class = classes["G0"]
    strict_classes = {class_id for grammar_id, class_id in classes.items() if grammar_id != "G0"}
    strict_forms = {form for grammar_id, form in result["ast_groups"].items() if grammar_id != "G0"}

    return {
        "index": item["index"],
        "family": item["family"],
        "source": source,
        "support": support,
        "support_size": len(support),
        "ast_bound": factorial(len(support)),
        "distinct_ast_count": result["distinct_ast_count"],
        "strict_distinct_ast_count": len(strict_forms),
        "class_count": result["distinct_class_count"],
        "strict_class_count": len(strict_classes),
        # the tied-level control as a control: does G0 reach a tree, or an answer, that no strict
        # ordering reaches? These two are measured separately because they are not the same event.
        "control_adds_an_ast": result["distinct_ast_count"] > len(strict_forms),
        "control_adds_a_class": result["distinct_class_count"] > len(strict_classes),
        "class_canonicals": tuple(key["canonical"] for key in result["class_keys"].values()),
        "constant_classes": constant_classes,
        "degenerate_classes": degenerate_classes,
        "variable_classes": variable_classes,
        "non_polynomial_classes": non_polynomial_classes,
        "degrees": tuple(degrees),
        "degree_spread": _spread(degrees),
        "division_counts": tuple(divisions),
        "division_spread": _spread(divisions),
        "min_depth": profile["min_depth"],
        "max_depth": profile["max_depth"],
        "depth_spread": profile["depth_spread"],
        # depth that a different grammar buys at ZERO semantic cost: the widest depth range inside
        # one semantic class, i.e. two grammars that agree on the answer and disagree on the cost.
        "free_depth_saving": max(_spread(values) for values in depths_per_class.values()),
        # what the tied-level control grammar pays over the cheapest grammar with the SAME semantics
        "control_depth": depth_by_grammar["G0"],
        "control_depth_saving": depth_by_grammar["G0"] - min(depths_per_class[control_class]),
        "sympify_failures": sum(entry["sympify_failed"] for entry in metrics.values()),
    }


def _semantic_slice(payload: tuple[CorpusSpec, int, int]) -> list[dict[str, Any]]:
    """Module-level pool function: rebuild an index range and return its semantic records."""
    spec, start, stop = payload
    return [semantic_record(item) for item in spec.items(start, stop)]


def semantic_sweep(
    spec: CorpusSpec | None = None,
    workers: int | None = None,
    chunk_size: int | None = None,
) -> dict[str, Any]:
    """``C(E)`` over the corpus with the project's semantic-class key, at `1e5` scale."""
    spec = spec or semantic_spec()
    ranges, resolved = _plan(spec, workers, chunk_size)
    payloads = [(spec, start, stop) for start, stop in ranges]
    chunks, used, elapsed = _run_chunks(_semantic_slice, payloads, resolved)
    records = [record for chunk in chunks for record in chunk]
    return {
        "tier": "semantic",
        "expression_count": len(records),
        "grammar_count": len(GRAMMARS),
        "generation": spec.generation(),
        "records": tuple(records),
        "class_key": "(canonical expression, domain, excluded points) - parseatlas.analyze's own key",
        "canonicalizations": sum(record["distinct_ast_count"] for record in records),
        "canonicalizations_without_dedup": len(records) * len(GRAMMARS),
        "sympify_failures": sum(record["sympify_failures"] for record in records),
        "chunk_count": len(ranges),
        "chunk_size": ranges[0][1] - ranges[0][0] if ranges else 0,
        "workers": used,
        "cpu_count": os.cpu_count(),
        "wall_clock_seconds": elapsed,
    }


def _resolve_records(
    spec: CorpusSpec | None, workers: int | None, records: Sequence[dict[str, Any]] | None
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    if records is not None:
        return tuple(records), {"workers": None, "wall_clock_seconds": None, "reused_records": True}
    run = semantic_sweep(spec, workers)
    return run["records"], {
        "workers": run["workers"],
        "wall_clock_seconds": run["wall_clock_seconds"],
        "reused_records": False,
    }


# ----------------------------------------------------------------------------- distributions


def _distribution_block(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    count = max(len(records), 1)
    classes = Counter(record["class_count"] for record in records)
    strict_classes = Counter(record["strict_class_count"] for record in records)
    asts = Counter(record["distinct_ast_count"] for record in records)
    strict_asts = Counter(record["strict_distinct_ast_count"] for record in records)
    supports = Counter(record["support_size"] for record in records)
    mode = _mode(classes)
    strict_mode = _mode(strict_classes)
    return {
        "expression_count": len(records),
        "class_count_distribution": _as_distribution(classes),
        "strict_class_count_distribution": _as_distribution(strict_classes),
        "distinct_ast_distribution": _as_distribution(asts),
        "strict_distinct_ast_distribution": _as_distribution(strict_asts),
        "support_size_distribution": _as_distribution(supports),
        "mode": mode,
        "mode_count": classes[mode] if mode is not None else 0,
        "mode_share": (classes[mode] / count) if mode is not None else 0.0,
        "count_at_8": classes[8],
        "share_at_8": classes[8] / count,
        "strict_mode": strict_mode,
        "strict_mode_share": (strict_classes[strict_mode] / count) if strict_mode is not None else 0.0,
        "strict_count_at_8": strict_classes[8],
        "strict_share_at_8": strict_classes[8] / count,
        "mean_class_count": sum(record["class_count"] for record in records) / count,
        "max_class_count": max((record["class_count"] for record in records), default=None),
        "rigid_share": sum(record["strict_class_count"] == 1 for record in records) / count,
        "control_adds_an_ast": sum(record["control_adds_an_ast"] for record in records),
        "control_adds_a_class": sum(record["control_adds_a_class"] for record in records),
        "control_adds_an_ast_share": sum(record["control_adds_an_ast"] for record in records) / count,
        "control_adds_a_class_share": sum(record["control_adds_a_class"] for record in records) / count,
    }


#: The three families whose template ends in the founding ``- {c}*x/{d}`` tail. They are cut out in
#: :func:`distribution_report`'s ablation for one measured reason: they supply almost every ``C = 8``
#: in the corpus, so a conditional distribution that keeps them is as family-mix-relative as the
#: global one. Naming them here rather than inside the function keeps the ablation auditable.
SATURATING_DIV_FAMILIES: tuple[str, ...] = ("affine_div", "quadratic_div", "cubic_div")


def _support_size_blocks(records: Sequence[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {
        size: _distribution_block([record for record in records if record["support_size"] == size])
        for size in sorted({record["support_size"] for record in records})
    }


def distribution_report(
    spec: CorpusSpec | None = None,
    workers: int | None = None,
    records: Sequence[dict[str, Any]] | None = None,
    ablate_families: Sequence[str] = SATURATING_DIV_FAMILIES,
) -> dict[str, Any]:
    """The headline: the full ``C(E)`` and distinct-AST distributions, overall and per family.

    ``by_support_size`` is not decoration. Operator-support reduction bounds the strict distinct
    ASTs by ``factorial(|O(E)|)``, so a ``C(E)`` distribution that merely tracks the support-size
    distribution is the null model wearing a hat. Conditioning on support size is what separates the
    two, and both are published side by side.

    Conditioning is NOT a way out of the corpus, though, and ``family_mix_ablation`` measures
    exactly that: it recomputes the same conditional distribution with ``ablate_families`` removed.
    A conditional mode that survives the ablation is a property of the stratum; one that does not is
    a property of this family mix, published with its dependence visible instead of implied.
    """
    collected, run = _resolve_records(spec, workers, records)
    removed = tuple(ablate_families)
    kept = [record for record in collected if record["family"] not in set(removed)]
    families = {
        family: _distribution_block([record for record in collected if record["family"] == family])
        for family in dict.fromkeys(record["family"] for record in collected)
    }
    return {
        "expression_count": len(collected),
        "overall": _distribution_block(collected),
        "families": families,
        "by_support_size": _support_size_blocks(collected),
        "family_mix_ablation": {
            "removed_families": list(removed),
            "expression_count": len(kept),
            "overall": _distribution_block(kept),
            "by_support_size": _support_size_blocks(kept),
            "why": (
                "the support-conditioned distribution is not automatically transferable: it is "
                "computed over the same designed family mix as the global one. Removing the "
                "families that supply the conditional mode is the measurement that shows how much "
                "of that mode is the stratum and how much is the mix"
            ),
        },
        "support_size_distribution": _as_distribution(Counter(record["support_size"] for record in collected)),
        "founding_value": 8,
        "null_model": (
            "part of every distribution is forced. What the 0019 reduction DERIVES is this: the 24 "
            "strict grammars split into factorial(|O(E)|) support-reduction blocks with a "
            "byte-identical AST inside each, and G0 keeps its tied level and falls outside those "
            "blocks, so C(E) <= all-25 distinct ASTs <= factorial(|O(E)|) + 1. The tighter chain "
            "C(E) <= strict distinct ASTs <= factorial(|O(E)|) is NOT a consequence of the "
            "reduction: its first step needs control_adds_a_class == 0, which is measured here "
            "(and is 0 on every published corpus) rather than derived. by_support_size reports "
            "C(E) with the mechanical part held fixed; family_mix_ablation reports what is left of "
            "it when the families that supply the conditional mode are removed"
        ),
        **run,
    }


# --------------------------------------------------------------------------------- collapse


def _rate(hits: int, total: int) -> float:
    return hits / total if total else 0.0


def _examples(
    records: Sequence[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    fields: Sequence[str],
    limit: int = DEFAULT_EXAMPLE_LIMIT,
) -> list[dict[str, Any]]:
    """The MIDDLE matching expression of each family, in corpus index order.

    Two choices, both for the same reason - an example has to be representative of the phenomenon,
    not of the corpus enumeration:

    * one example per family rather than the first ``limit`` records, because the families are
      interleaved and the first ``limit`` records are all the same coefficient tuple;
    * the MIDDLE match of a family rather than its first, because the Cartesian product starts at
      the all-zero coefficient corner and "the first match" would report a degenerate expression
      every single time, reading as if the phenomenon only happened there. The middle match is
      equally deterministic and is a typical member of that family's matches.
    """
    matches: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if predicate(record):
            matches.setdefault(record["family"], []).append(record)
    chosen = []
    for family in list(matches)[:limit]:
        members = matches[family]
        record = members[len(members) // 2]
        chosen.append({key: record[key] for key in ("family", "source", *fields)})
    return chosen


def collapse_report(
    spec: CorpusSpec | None = None,
    workers: int | None = None,
    records: Sequence[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """What the grammar choice actually buys, measured rather than asserted.

    Four phenomena, each with a count, a rate and concrete named examples that really occurred:

    * ``constant_collapse`` - some grammar makes the variable disappear entirely;
    * ``degree_difference`` - the polynomial degree of the canonical form differs across grammars;
    * ``division_difference`` - the division count of the canonical form differs across grammars;
    * ``depth_difference`` - the critical-path depth differs across grammars, and separately the
      part of that difference that is FREE, i.e. available inside one semantic class.
    """
    collected, run = _resolve_records(spec, workers, records)
    total = len(collected)

    constant_any = [record for record in collected if record["constant_classes"] > 0]
    constant_mixed = [record for record in constant_any if record["variable_classes"] > 0]
    constant_all = [record for record in constant_any if record["class_count"] == record["constant_classes"]]
    degree = [record for record in collected if record["degree_spread"] > 0]
    division = [record for record in collected if record["division_spread"] > 0]
    depth = [record for record in collected if record["depth_spread"] > 0]
    free_depth = [record for record in collected if record["free_depth_saving"] > 0]
    control_waste = [record for record in collected if record["control_depth_saving"] > 0]
    degenerate = [record for record in collected if record["degenerate_classes"] > 0]

    return {
        "expression_count": total,
        "constant_collapse": {
            "definition": "at least one semantic class has no free symbols and is a finite number",
            "expressions": len(constant_any),
            "rate": _rate(len(constant_any), total),
            "grammar_dependent": len(constant_mixed),
            "grammar_dependent_rate": _rate(len(constant_mixed), total),
            "every_class_constant": len(constant_all),
            "examples": _examples(
                collected,
                lambda record: record["constant_classes"] > 0 and record["variable_classes"] > 0,
                ("class_count", "constant_classes", "variable_classes", "class_canonicals"),
            ),
        },
        "degree_difference": {
            "definition": "max - min polynomial degree over the semantic classes of one expression",
            "expressions": len(degree),
            "rate": _rate(len(degree), total),
            "spread_distribution": _as_distribution(Counter(record["degree_spread"] for record in collected)),
            "max_spread": max((record["degree_spread"] for record in collected), default=0),
            "examples": _examples(
                collected,
                lambda record: record["degree_spread"] > 0,
                ("degrees", "degree_spread", "class_count"),
            ),
        },
        "division_difference": {
            "definition": "max - min count of negative-exponent powers in the canonical form",
            "expressions": len(division),
            "rate": _rate(len(division), total),
            "spread_distribution": _as_distribution(Counter(record["division_spread"] for record in collected)),
            "max_spread": max((record["division_spread"] for record in collected), default=0),
            "examples": _examples(
                collected,
                lambda record: record["division_spread"] > 0,
                ("division_counts", "division_spread", "class_canonicals"),
            ),
        },
        "depth_difference": {
            "definition": "max - min critical-path depth of the parse trees over the 25 grammars",
            "expressions": len(depth),
            "rate": _rate(len(depth), total),
            "spread_distribution": _as_distribution(Counter(record["depth_spread"] for record in collected)),
            "max_spread": max((record["depth_spread"] for record in collected), default=0),
            "free_saving_expressions": len(free_depth),
            "free_saving_rate": _rate(len(free_depth), total),
            "free_saving_distribution": _as_distribution(
                Counter(record["free_depth_saving"] for record in collected)
            ),
            "control_pays_more_expressions": len(control_waste),
            "control_pays_more_rate": _rate(len(control_waste), total),
            "control_saving_distribution": _as_distribution(
                Counter(record["control_depth_saving"] for record in collected)
            ),
            "examples": _examples(
                collected,
                lambda record: record["free_depth_saving"] > 0,
                ("min_depth", "max_depth", "depth_spread", "free_depth_saving", "control_depth_saving"),
            ),
        },
        "degenerate_classes": {
            "definition": "a canonical class containing zoo or nan, produced by a zero denominator",
            "expressions": len(degenerate),
            "rate": _rate(len(degenerate), total),
            "examples": _examples(
                collected,
                lambda record: record["degenerate_classes"] > 0,
                ("class_count", "degenerate_classes", "class_canonicals"),
            ),
        },
        "sympify_failures": sum(record["sympify_failures"] for record in collected),
        **run,
    }


# ------------------------------------------------------------------------------- calibration


#: 0024's published ``C(E)`` distribution over its own `3125`-expression corpus.
CALIBRATION_CLASS_DISTRIBUTION: dict[int, int] = {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}


def calibration_report(workers: int | None = None) -> dict[str, Any]:
    """Re-derive 0024's ``C(E)`` distribution on 0024's own corpus before trusting anything here.

    This runs the 0024 corpus through THIS module's semantic record, not through 0024's code path,
    so agreement is evidence that the two pipelines compute the same ``C(E)`` and not that one
    module called the other.
    """
    from .corpus_matrix import COEFFICIENT_VALUES, FAMILY_TEMPLATES as CORPUS_2024_TEMPLATES

    spec = CorpusSpec(
        values_count=len(COEFFICIENT_VALUES),
        templates=tuple((family, template, ("free", "free", "free", "free")) for family, template in CORPUS_2024_TEMPLATES),
        free_values=COEFFICIENT_VALUES,
        nonzero_values=COEFFICIENT_VALUES,
    )
    run = semantic_sweep(spec, workers)
    observed = _as_distribution(Counter(record["class_count"] for record in run["records"]))
    return {
        "corpus_size": run["expression_count"],
        "expected": dict(CALIBRATION_CLASS_DISTRIBUTION),
        "observed": observed,
        "reproduces": observed == CALIBRATION_CLASS_DISTRIBUTION,
        "mode": _mode(Counter(record["class_count"] for record in run["records"])),
        "workers": run["workers"],
        "wall_clock_seconds": run["wall_clock_seconds"],
    }
