"""Specialized symbolic analyzers for the first mathematical domains."""

from math import gcd
from typing import Any

from sympy import (
    E, Matrix, Rational, Symbol, acos, binomial, diff, expand, factor, integrate, limit, log,
    cos, lcm, oo, pi, simplify, sin, solve, sqrt, sympify,
)
from sympy.ntheory import factorint, isprime


def analyze_quadratic(a: int, b: int, c: int) -> dict[str, Any]:
    discriminant = b * b - 4 * a * c
    x = Symbol("x")
    roots = solve(a * x**2 + b * x + c, x)
    return {
        "domain": "quadratic_equations",
        "equation": f"{a}*x**2 + {b}*x + {c} = 0",
        "discriminant": discriminant,
        "root_count": len(roots),
        "roots": [str(root) for root in roots],
        "vertex": {"x": str(Rational(-b, 2 * a)), "y": str(Rational(-discriminant, 4 * a))},
    }


def analyze_geometry(base: Any, height: Any, x1: Any, y1: Any, x2: Any, y2: Any) -> dict[str, Any]:
    base, height = sympify(base), sympify(height)
    dx, dy = sympify(x2) - sympify(x1), sympify(y2) - sympify(y1)
    return {
        "domain": "geometry",
        "triangle_area": str(simplify(base * height / 2)),
        "distance": str(simplify(sqrt(dx**2 + dy**2))),
        "midpoint": [str(simplify((sympify(x1) + sympify(x2)) / 2)), str(simplify((sympify(y1) + sympify(y2)) / 2))],
    }


def analyze_geometry_extended(radius: Any, angle: Any, point: tuple[Any, Any] = (1, 0)) -> dict[str, Any]:
    """Analyze circle metrics and a planar rotation of one point."""
    radius, angle = sympify(radius), sympify(angle)
    x, y = map(sympify, point)
    rotation = Matrix([[sympify(cos(angle)), -sympify(sin(angle))], [sympify(sin(angle)), sympify(cos(angle))]])
    rotated = rotation * Matrix([x, y])
    return {
        "domain": "geometry",
        "circle_area": str(simplify(pi * radius**2)),
        "circle_circumference": str(simplify(2 * pi * radius)),
        "rotated_point": [str(simplify(value)) for value in rotated],
        "rotation_preserves_distance": str(simplify(rotated.dot(rotated) - (x**2 + y**2))),
    }


def analyze_vector_angle(first: tuple[Any, Any], second: tuple[Any, Any]) -> dict[str, Any]:
    """Analyze dot product, determinant, and angle between two planar vectors."""
    vector_a = Matrix([sympify(value) for value in first])
    vector_b = Matrix([sympify(value) for value in second])
    dot_product = simplify(vector_a.dot(vector_b))
    determinant = simplify(vector_a[0] * vector_b[1] - vector_a[1] * vector_b[0])
    return {
        "domain": "geometry",
        "dot_product": str(dot_product),
        "determinant": str(determinant),
        "angle": str(simplify(acos(dot_product / sqrt(vector_a.dot(vector_a) * vector_b.dot(vector_b))))),
    }


def analyze_algebra(expression: str, variable: str = "x") -> dict[str, Any]:
    symbol = Symbol(variable)
    parsed = sympify(expression)
    return {
        "domain": "algebra",
        "expanded": str(expand(parsed)),
        "factored": str(factor(parsed)),
        "simplified": str(simplify(parsed)),
        "zeros": [str(root) for root in solve(parsed, symbol)],
    }


def analyze_identity(left: str, right: str, variable: str = "x") -> dict[str, Any]:
    """Check an algebraic identity through a symbolic residual."""
    symbol = Symbol(variable)
    residual = simplify(sympify(left) - sympify(right))
    return {
        "domain": "algebra",
        "left": left,
        "right": right,
        "residual": str(residual),
        "is_identity": residual == 0,
        "variables": sorted(str(item) for item in residual.free_symbols if item != symbol) or [variable],
    }


def analyze_calculus(expression: str, variable: str = "x", point: Any = 0) -> dict[str, Any]:
    symbol = Symbol(variable)
    parsed = sympify(expression)
    return {
        "domain": "calculus",
        "derivative": str(simplify(diff(parsed, symbol))),
        "integral": str(integrate(parsed, symbol)),
        "limit_at_point": str(limit(parsed, symbol, point)),
        "critical_points": [str(item) for item in solve(diff(parsed, symbol), symbol)],
    }


def analyze_number_theory(n: int) -> dict[str, Any]:
    return {
        "domain": "number_theory",
        "value": n,
        "is_prime": bool(isprime(n)),
        "factorization": {str(key): value for key, value in factorint(n).items()},
        "gcd_with_12": int(gcd(n, 12)),
        "lcm_with_12": int(lcm(n, 12)),
    }


def analyze_trigonometry(angle: str = "x") -> dict[str, Any]:
    symbol = Symbol(angle)
    identity = sin(symbol) ** 2 + (1 - sin(symbol) ** 2)
    return {
        "domain": "trigonometry",
        "identity_simplified": str(simplify(identity)),
        "sin_derivative": str(diff(sin(symbol), symbol)),
        "cos_at_zero": str(simplify(sin(symbol + pi / 2).subs(symbol, 0))),
        "inverse_check": str(simplify(acos(1))),
    }


def analyze_exponential_ode(rate: int, initial_value: Any = 1) -> dict[str, Any]:
    """Analyze the closed-form solution of y' = rate*y with y(0)=initial_value."""
    time = Symbol("t", real=True)
    initial = sympify(initial_value)
    solution = simplify(initial * E ** (rate * time))
    return {
        "domain": "differential_equations",
        "equation": f"y' = {rate}*y",
        "initial_condition": f"y(0) = {initial}",
        "solution": str(solution),
        "derivative_check": str(simplify(diff(solution, time) - rate * solution)),
    }


def analyze_binomial_probability(trials: int, successes: int, probability: Any) -> dict[str, Any]:
    """Analyze one outcome and moments of Binomial(n, p)."""
    if trials < 0 or successes < 0 or successes > trials:
        raise ValueError("successes must be between 0 and trials")
    p = sympify(probability)
    if not (0 <= p <= 1):
        raise ValueError("probability must be between 0 and 1")
    q = 1 - p
    pmf = simplify(binomial(trials, successes) * p**successes * q ** (trials - successes))
    return {
        "domain": "probability_statistics",
        "distribution": f"Binomial({trials}, {p})",
        "outcome": successes,
        "pmf": str(pmf),
        "expected_value": str(simplify(trials * p)),
        "variance": str(simplify(trials * p * q)),
    }


def analyze_normal_distribution(mean: Any, standard_deviation: Any, point: Any) -> dict[str, Any]:
    """Analyze the Normal(mu, sigma) PDF and standardized point."""
    mu, sigma, value = map(sympify, (mean, standard_deviation, point))
    if sigma <= 0:
        raise ValueError("standard_deviation must be positive")
    z_score = simplify((value - mu) / sigma)
    density = simplify(1 / (sigma * sqrt(2 * pi)) * E ** (-z_score**2 / 2))
    return {
        "domain": "probability_statistics",
        "distribution": f"Normal({mu}, {sigma})",
        "point": str(value),
        "z_score": str(z_score),
        "pdf": str(density),
        "expected_value": str(mu),
        "variance": str(sigma**2),
    }


def analyze_exponential_distribution(rate: Any, point: Any) -> dict[str, Any]:
    """Analyze the Exponential(lambda) PDF and survival function."""
    lam, value = map(sympify, (rate, point))
    if lam <= 0 or value < 0:
        raise ValueError("rate must be positive and point must be nonnegative")
    return {
        "domain": "probability_statistics",
        "distribution": f"Exponential({lam})",
        "point": str(value),
        "pdf": str(simplify(lam * E ** (-lam * value))),
        "survival": str(simplify(E ** (-lam * value))),
        "expected_value": str(simplify(1 / lam)),
        "variance": str(simplify(1 / lam**2)),
    }


def analyze_calculus_extended(expression: str, variable: str = "x", point: Any = 0, order: int = 4) -> dict[str, Any]:
    """Compute limit, definite integral, Taylor polynomial, and extrema candidates."""
    symbol = Symbol(variable)
    parsed = sympify(expression)
    derivative = diff(parsed, symbol)
    critical_points = solve(derivative, symbol)
    return {
        "domain": "calculus",
        "expression": str(parsed),
        "limit_at_infinity": str(limit(parsed, symbol, oo)),
        "definite_integral_0_to_1": str(integrate(parsed, (symbol, 0, 1))),
        "taylor_at_point": str(parsed.series(symbol, point, order).removeO()),
        "critical_points": [str(item) for item in critical_points],
        "critical_values": [str(simplify(parsed.subs(symbol, item))) for item in critical_points],
    }
