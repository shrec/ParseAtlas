import pytest

from parseatlas.grammar import Grammar, strict_grammars
from parseatlas.support_reduction import (
    operator_support,
    restriction,
    serialized_ast,
    support_reduction_report,
)

CORPUS = (
    "a - b - c",
    "a/b/c",
    "a + b - c",
    "a + b*c",
    "a + b - c*d",
    "a/b + c - d",
    "2*t + 1 - t/2",
    "a + b*c - d/e",
    "2*x*x + 1 - x/2",
    "a - b*c + d/e - f",
)

# Published table of experiments/0019_operator_support_reduction/REPORT.md, as
# (support size, block count, block size, distinct AST count, factorial bound).
# These are expectations written down by hand from the report, not values the
# module reports about itself.
PUBLISHED = {
    "a - b - c": (1, 1, 24, 1, 1),
    "a/b/c": (1, 1, 24, 1, 1),
    "a + b - c": (2, 2, 12, 2, 2),
    "a + b*c": (2, 2, 12, 2, 2),
    "a + b - c*d": (3, 6, 4, 5, 6),
    "a/b + c - d": (3, 6, 4, 5, 6),
    "2*t + 1 - t/2": (4, 24, 1, 14, 24),
    "a + b*c - d/e": (4, 24, 1, 14, 24),
    "2*x*x + 1 - x/2": (4, 24, 1, 14, 24),
    "a - b*c + d/e - f": (4, 24, 1, 19, 24),
}

_GRAMMARS_BY_ID = {grammar.id: grammar for grammar in strict_grammars()}


def _record(report: dict, source: str) -> dict:
    return next(item for item in report["expressions"] if item["source"] == source)


def _block_forms(record: dict) -> dict[str, set[str]]:
    """Re-serialize every grammar of every block instead of trusting the record."""
    return {
        key: {serialized_ast(record["source"], _GRAMMARS_BY_ID[grammar_id]) for grammar_id in block["grammar_ids"]}
        for key, block in record["blocks"].items()
    }


def _distinct_forms(record: dict) -> set[str]:
    return {form for forms in _block_forms(record).values() for form in forms}


def test_operator_support_ignores_rational_literals():
    assert operator_support("1/2 + x") == ("+",)
    assert operator_support("a - b - c") == ("-",)
    assert operator_support("2*t + 1 - t/2") == ("*", "+", "-", "/")


def test_restriction_keeps_grammar_order_of_supported_operators():
    grammar = Grammar("GX", ("*", "/", "+", "-"))
    assert restriction(grammar, ("+", "*")) == ("*", "+")
    assert restriction(grammar, ("-",)) == ("-",)
    assert len({restriction(grammar, ("+", "-", "*", "/")) for grammar in strict_grammars()}) == 24


def test_every_block_holds_exactly_one_distinct_serialized_ast():
    report = support_reduction_report(CORPUS)
    for record in report["expressions"]:
        forms = _block_forms(record)
        for key, block_forms in forms.items():
            assert len(block_forms) == 1, (record["source"], key)
            assert record["blocks"][key]["distinct_ast_count"] == 1, (record["source"], key)
            assert record["blocks"][key]["grammar_count"] == record["expected_block_size"]
        # The serializer must also separate blocks, otherwise "one AST per block"
        # would hold for a serializer that returns the same string for everything.
        distinct = _distinct_forms(record)
        assert len(distinct) == PUBLISHED[record["source"]][3], record["source"]
        if record["block_count"] > 1:
            assert len(distinct) >= 2, record["source"]


def test_single_operator_expression_collapses_all_twenty_four_grammars():
    record = _record(support_reduction_report(CORPUS), "a - b - c")
    assert record["support_size"] == 1
    assert record["block_count"] == 1
    assert record["expected_block_size"] == 24
    ids = record["blocks"]["-"]["grammar_ids"]
    assert len(ids) == 24
    assert set(ids) == {grammar.id for grammar in strict_grammars()}
    assert len(_distinct_forms(record)) == 1
    # bound 1, one observed AST: nothing collapses below the bound here.
    assert record["ast_forms_below_bound"] is False


def test_two_operator_expression_splits_into_two_blocks_of_twelve():
    record = _record(support_reduction_report(CORPUS), "a + b*c")
    assert record["support_size"] == 2
    assert record["block_count"] == 2
    assert record["upper_bound"] == 2
    assert sorted(block["grammar_count"] for block in record["blocks"].values()) == [12, 12]
    forms = _block_forms(record)
    assert forms["+ *"] != forms["* +"]
    assert len(_distinct_forms(record)) == 2


def test_full_support_expression_has_singleton_blocks_and_extra_collapse():
    record = _record(support_reduction_report(CORPUS), "2*t + 1 - t/2")
    assert record["support_size"] == 4
    assert record["block_count"] == 24
    assert record["expected_block_size"] == 1
    assert record["upper_bound"] == 24
    assert all(block["grammar_count"] == 1 for block in record["blocks"].values())
    assert record["distinct_ast_count"] == 14
    forms = _block_forms(record)
    # A concrete split and a concrete merge, both named by restriction key.
    assert forms["+ * / -"] != forms["+ / - *"]
    assert forms["+ * / -"] == forms["/ + * -"]
    assert len(_distinct_forms(record)) == 14
    assert record["ast_forms_below_bound"] is True


def test_support_reduction_holds_over_the_whole_corpus():
    report = support_reduction_report(CORPUS)
    assert report["expression_count"] == 10
    assert report["grammar_count"] == 24
    measured = {
        record["source"]: (
            record["support_size"],
            record["block_count"],
            record["expected_block_size"],
            record["distinct_ast_count"],
            record["upper_bound"],
        )
        for record in report["expressions"]
    }
    assert measured == PUBLISHED
    independently_holds = all(
        record["block_count"] == record["upper_bound"]
        and all(len(forms) == 1 for forms in _block_forms(record).values())
        and all(block["grammar_count"] == record["expected_block_size"] for block in record["blocks"].values())
        for record in report["expressions"]
    )
    assert independently_holds is True
    assert report["all_reductions_hold"] is independently_holds
    assert report["mean_enumeration_saving"] == pytest.approx(0.525)
