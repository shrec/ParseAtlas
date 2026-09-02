from parseatlas.analyze import analyze_expression
from parseatlas.grammar_matrix import equivalence_matrix, representation_sensitivity


def test_representation_sensitivity_matches_affine_baseline():
    report = analyze_expression("2*t + 1 - t/2")
    assert representation_sensitivity(report) == 7 / 23


def test_grammar_equivalence_matrix_has_25_by_25_shape():
    result = equivalence_matrix(("2*t + 1 - t/2", "(x + 1)/(x - 2)"))
    assert result["expression_count"] == 2
    assert result["grammar_count"] == 25
    assert len(result["matrix"]) == 25
    assert all(len(row) == 25 for row in result["matrix"].values())
    assert result["matrix"]["G0"]["G0"] == 1.0
    assert result["matrix"]["G0"]["G01"] == 0.5
