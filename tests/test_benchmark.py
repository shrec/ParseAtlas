from parseatlas.benchmark import benchmark_expression


def test_benchmark_reports_separate_parse_and_canonicalization_stages():
    result = benchmark_expression("2*x + 1 - x/2", repetitions=2)
    assert result["grammar_count"] == 25
    assert result["repetitions"] == 2
    assert result["raw_ast_nodes_median"] > 0
    assert result["canonical_expression_size_median"] > 0
    assert result["parse_seconds_median"] >= 0
    assert result["canonicalization_seconds_median"] >= 0
