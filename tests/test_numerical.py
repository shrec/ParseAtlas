from parseatlas.numerical import validate_expression


def test_numerical_validation_confirms_canonical_equivalence():
    result = validate_expression("2*x + 1 - x/2", (-2, -1, 0, 1, 2))
    assert result["grammar_count"] == 25
    assert result["all_match"] is True
    assert result["mismatches"] == []
    assert result["checked"] == 125


def test_numerical_validation_skips_rational_pole():
    result = validate_expression("(x + 1)/(x - 2)", (-1, 0, 1, 2, 3))
    assert result["all_match"] is True
    assert result["skipped"] > 0
    assert result["checked"] > 0
