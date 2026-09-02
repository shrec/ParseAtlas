"""Mathematical property extraction for canonical expressions."""

from typing import Any

from sympy import Poly, Symbol, cancel, diff, factor, fraction, solve, simplify, together
from sympy.polys.polyerrors import PolynomialError


def polynomial_properties(expression: Any, variable: Symbol) -> dict[str, Any]:
    try:
        polynomial = Poly(expression, variable)
    except (TypeError, ValueError, PolynomialError):
        return {"is_polynomial": False}
    degree = polynomial.degree()
    result: dict[str, Any] = {
        "is_polynomial": True,
        "degree": None if degree == -1 else int(degree),
        "coefficients": [str(value) for value in polynomial.all_coeffs()],
        "factorized": str(factor(expression)),
        "roots": [str(root) for root in solve(expression, variable)],
    }
    if degree == 2:
        coefficients = polynomial.all_coeffs()
        discriminant = simplify(coefficients[1] ** 2 - 4 * coefficients[0] * coefficients[2])
        vertex_x = simplify(-coefficients[1] / (2 * coefficients[0]))
        result["discriminant"] = str(discriminant)
        result["vertex"] = {"x": str(vertex_x), "y": str(simplify(expression.subs(variable, vertex_x)))}
    if degree >= 1:
        result["critical_points"] = [str(point) for point in solve(diff(expression, variable), variable)]
    return result


def rational_properties(expression: Any, variable: Symbol) -> dict[str, Any]:
    """Return zeros, poles, and removable restrictions for a rational expression."""
    original_numerator, original_denominator = fraction(together(expression))
    numerator, denominator = fraction(cancel(together(expression)))
    try:
        numerator_poly = Poly(numerator, variable)
        denominator_poly = Poly(denominator, variable)
    except (TypeError, ValueError, PolynomialError):
        return {"is_rational": False}
    denominator_roots = solve(denominator_poly.as_expr(), variable)
    numerator_roots = solve(numerator_poly.as_expr(), variable)
    return {
        "is_rational": True,
        "numerator": str(numerator),
        "denominator": str(denominator),
        "zeros": [str(root) for root in solve(numerator_poly.as_expr(), variable)],
        "poles": [str(root) for root in denominator_roots if root not in numerator_roots],
        "removable_restrictions": [str(root) for root in solve(original_denominator, variable) if simplify(original_numerator.subs(variable, root)) == 0],
    }
