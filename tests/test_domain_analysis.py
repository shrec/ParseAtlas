from parseatlas.domain_analysis import (
    analyze_algebra,
    analyze_calculus,
    analyze_geometry,
    analyze_exponential_ode,
    analyze_binomial_probability,
    analyze_number_theory,
    analyze_quadratic,
    analyze_trigonometry,
)


def test_quadratic_analysis_reports_roots_discriminant_and_vertex():
    result = analyze_quadratic(1, -3, 2)
    assert result["discriminant"] == 1
    assert result["root_count"] == 2
    assert result["roots"] == ["1", "2"]
    assert result["vertex"] == {"x": "3/2", "y": "-1/4"}


def test_geometry_analysis_reports_area_distance_and_midpoint():
    result = analyze_geometry(6, 4, 0, 0, 3, 4)
    assert result["triangle_area"] == "12"
    assert result["distance"] == "5"
    assert result["midpoint"] == ["3/2", "2"]


def test_algebra_and_calculus_analysis_are_symbolic():
    assert analyze_algebra("x**2 - 1")["factored"] == "(x - 1)*(x + 1)"
    calculus = analyze_calculus("x**2")
    assert calculus["derivative"] == "2*x"
    assert calculus["integral"] == "x**3/3"


def test_trigonometry_and_number_theory_properties():
    assert analyze_trigonometry()["identity_simplified"] == "1"
    number = analyze_number_theory(60)
    assert number["is_prime"] is False
    assert number["factorization"] == {"2": 2, "3": 1, "5": 1}
    assert number["gcd_with_12"] == 12


def test_exponential_ode_has_zero_residual():
    result = analyze_exponential_ode(2, 3)
    assert result["solution"] == "3*exp(2*t)"
    assert result["derivative_check"] == "0"


def test_binomial_probability_reports_pmf_and_moments():
    result = analyze_binomial_probability(4, 2, "1/2")
    assert result["pmf"] == "3/8"
    assert result["expected_value"] == "2"
    assert result["variance"] == "1"
