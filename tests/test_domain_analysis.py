from parseatlas.domain_analysis import (
    analyze_algebra,
    analyze_calculus,
    analyze_geometry,
    analyze_geometry_extended,
    analyze_identity,
    analyze_vector_angle,
    analyze_exponential_ode,
    analyze_binomial_probability,
    analyze_calculus_extended,
    analyze_exponential_distribution,
    analyze_normal_distribution,
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


def test_extended_geometry_reports_circle_and_rotation_invariants():
    result = analyze_geometry_extended(2, "pi/2")
    assert result["circle_area"] == "4*pi"
    assert result["circle_circumference"] == "4*pi"
    assert result["rotated_point"] == ["0", "1"]
    assert result["rotation_preserves_distance"] == "0"


def test_vector_angle_reports_right_angle():
    result = analyze_vector_angle((1, 0), (0, 1))
    assert result["dot_product"] == "0"
    assert result["determinant"] == "1"
    assert result["angle"] == "pi/2"


def test_algebra_and_calculus_analysis_are_symbolic():
    assert analyze_algebra("x**2 - 1")["factored"] == "(x - 1)*(x + 1)"
    calculus = analyze_calculus("x**2")
    assert calculus["derivative"] == "2*x"
    assert calculus["integral"] == "x**3/3"


def test_identity_checker_returns_zero_residual_only_for_identities():
    identity = analyze_identity("(x + 1)**2", "x**2 + 2*x + 1")
    non_identity = analyze_identity("x**2", "x + 1")
    assert identity["is_identity"] is True
    assert identity["residual"] == "0"
    assert non_identity["is_identity"] is False


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


def test_continuous_distributions_report_density_and_moments():
    normal = analyze_normal_distribution(0, 1, 0)
    assert normal["z_score"] == "0"
    assert normal["expected_value"] == "0"
    assert normal["variance"] == "1"
    exponential = analyze_exponential_distribution(2, 1)
    assert exponential["pdf"] == "2*exp(-2)"
    assert exponential["survival"] == "exp(-2)"
    assert exponential["expected_value"] == "1/2"


def test_extended_calculus_reports_limit_integral_series_and_extrema():
    result = analyze_calculus_extended("x**2", order=4)
    assert result["limit_at_infinity"] == "oo"
    assert result["definite_integral_0_to_1"] == "1/3"
    assert result["taylor_at_point"] == "x**2"
    assert result["critical_points"] == ["0"]
    assert result["critical_values"] == ["0"]
