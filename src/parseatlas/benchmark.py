"""Small reproducible measurements for ParseAtlas computation stages."""

from statistics import median
from time import perf_counter
from typing import Any

from .canonical import canonicalize, operation_cost
from .grammar import all_grammars
from .parser import parse


def benchmark_expression(source: str, repetitions: int = 5) -> dict[str, Any]:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    grammars = all_grammars()
    parse_timings: list[float] = []
    canonical_timings: list[float] = []
    raw_nodes: list[int] = []
    canonical_sizes: list[int] = []
    for _ in range(repetitions):
        started = perf_counter()
        nodes = [parse(source, grammar) for grammar in grammars]
        parse_timings.append(perf_counter() - started)
        raw_nodes.extend(operation_cost(node)["nodes"] for node in nodes)
        started = perf_counter()
        canonical_results = [canonicalize(node) for node in nodes]
        canonical_timings.append(perf_counter() - started)
        canonical_sizes.extend(len(result["expression"]) for result in canonical_results)
    return {
        "expression": source,
        "grammar_count": len(grammars),
        "repetitions": repetitions,
        "raw_ast_nodes_median": int(median(raw_nodes)),
        "canonical_expression_size_median": int(median(canonical_sizes)),
        "parse_seconds_median": median(parse_timings),
        "canonicalization_seconds_median": median(canonical_timings),
    }
