from parseatlas.advanced_analysis import (
    analyze_complex_identity,
    analyze_complex_branches,
    analyze_complex_trigonometry,
    classify_hessian,
    analyze_multivariable,
    rank_conjectures,
)


def test_multivariable_analysis_reports_gradient_and_hessian():
    result = analyze_multivariable("x**2 + x*y + y**2")
    assert result["gradient"] == ["2*x + y", "x + 2*y"]
    assert result["hessian"] == [["2", "1"], ["1", "2"]]
    assert result["hessian_determinant"] == "3"


def test_hessian_classification_distinguishes_minimum_maximum_and_saddle():
    assert classify_hessian("x**2 + y**2")["classification"] == "positive_definite"
    assert classify_hessian("-x**2 - y**2")["classification"] == "negative_definite"
    assert classify_hessian("x**2 - y**2")["classification"] == "indefinite"


def test_complex_identities_include_branch_metadata():
    assert analyze_complex_identity()["is_identity"] is True
    result = analyze_complex_trigonometry()
    assert result["residual"] == "0"
    assert "entire complex" in result["branch_convention"]
    branches = analyze_complex_branches()
    assert branches["sqrt_negative_one"] == "I"
    assert "principal branch" in branches["branch_convention"]


def test_conjecture_ranking_separates_supported_and_rejected_candidates():
    result = rank_conjectures((("(x+1)**2", "x**2+2*x+1"), ("x**2", "x+1")))
    assert result["candidate_count"] == 2
    assert result["supported_count"] == 1
    assert result["results"][1]["candidate_status"] == "rejected_symbolically"
