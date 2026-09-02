from parseatlas.sweep import linear_sweep, run_sweep


def test_linear_sweep_is_deterministic_and_bounded():
    expressions = linear_sweep((-1, 1))
    assert len(expressions) == 8
    first = run_sweep(expressions)
    second = run_sweep(expressions)
    assert first["expression_count"] == 8
    assert first["class_count_distribution"] == second["class_count_distribution"]
    assert first["ast_count_distribution"] == second["ast_count_distribution"]
    assert all(record["grammar_count"] == 25 for record in first["records"])
