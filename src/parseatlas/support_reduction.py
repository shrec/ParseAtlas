"""Operator-support reduction of the strict precedence grammar space."""

import json
from collections.abc import Iterable
from math import factorial
from typing import Any

from .canonical import ast_to_dict
from .grammar import Grammar, strict_grammars
from .parser import parse
from .tokenizer import tokenize


def operator_support(source: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(token.value for token in tokenize(source) if token.kind == "operator"))


def restriction(grammar: Grammar, support: Iterable[str]) -> tuple[str, ...]:
    supported = frozenset(support)
    return tuple(operator for operator in grammar.precedence if operator in supported)


def serialized_ast(source: str, grammar: Grammar) -> str:
    return json.dumps(ast_to_dict(parse(source, grammar)), sort_keys=True)


def _expression_record(source: str, grammars: tuple[Grammar, ...]) -> dict[str, Any]:
    support = operator_support(source)
    upper_bound = factorial(len(support))
    expected_block_size = len(grammars) // upper_bound
    grouped: dict[str, list[tuple[str, str]]] = {}
    for grammar in grammars:
        key = " ".join(restriction(grammar, support))
        grouped.setdefault(key, []).append((grammar.id, serialized_ast(source, grammar)))
    blocks = {
        key: {
            "grammar_ids": tuple(grammar_id for grammar_id, _ in members),
            "grammar_count": len(members),
            "distinct_ast_count": len({form for _, form in members}),
        }
        for key, members in grouped.items()
    }
    distinct_ast_count = len({form for members in grouped.values() for _, form in members})
    reduction_holds = (
        len(blocks) == upper_bound
        and all(block["grammar_count"] == expected_block_size for block in blocks.values())
        and all(block["distinct_ast_count"] == 1 for block in blocks.values())
    )
    return {
        "source": source,
        "support": support,
        "support_size": len(support),
        "expected_block_size": expected_block_size,
        "block_count": len(blocks),
        "blocks": blocks,
        "distinct_ast_count": distinct_ast_count,
        "upper_bound": upper_bound,
        "reduction_holds": reduction_holds,
        "ast_forms_below_bound": distinct_ast_count < upper_bound,
    }


def support_reduction_report(expressions: Iterable[str]) -> dict[str, Any]:
    grammars = strict_grammars()
    records = [_expression_record(source, grammars) for source in expressions]
    savings = [1 - record["upper_bound"] / len(grammars) for record in records]
    return {
        "grammar_count": len(grammars),
        "expression_count": len(records),
        "expressions": records,
        "all_reductions_hold": all(record["reduction_holds"] for record in records),
        "mean_enumeration_saving": sum(savings) / len(savings) if savings else 0.0,
    }
