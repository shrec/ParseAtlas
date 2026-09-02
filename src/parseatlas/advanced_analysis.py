"""Multivariable, complex, and conjecture-candidate analysis."""

from collections.abc import Iterable
from typing import Any

from sympy import I, Matrix, Symbol, cos, diff, exp, expand, log, pi, simplify, sin, sqrt, sympify
from sympy.parsing.sympy_parser import parse_expr


def analyze_multivariable(expression: str, variables: tuple[str, ...] = ("x", "y")) -> dict[str, Any]:
    symbols = tuple(Symbol(name, real=True) for name in variables)
    parsed = parse_expr(expression, local_dict=dict(zip(variables, symbols)), evaluate=False)
    gradient = [simplify(diff(parsed, symbol)) for symbol in symbols]
    hessian = Matrix([[simplify(diff(parsed, first, second)) for second in symbols] for first in symbols])
    return {
        "domain": "multivariable_calculus",
        "expression": str(parsed),
        "variables": list(variables),
        "gradient": [str(item) for item in gradient],
        "hessian": [[str(item) for item in row] for row in hessian.tolist()],
        "hessian_determinant": str(simplify(hessian.det())),
    }


def classify_hessian(expression: str, point: tuple[Any, Any] = (0, 0)) -> dict[str, Any]:
    """Classify a two-variable Hessian at a point using its eigenvalues."""
    variables = ("x", "y")
    symbols = tuple(Symbol(name, real=True) for name in variables)
    parsed = parse_expr(expression, local_dict=dict(zip(variables, symbols)), evaluate=False)
    hessian = Matrix([[diff(parsed, first, second) for second in symbols] for first in symbols])
    evaluated = hessian.subs(dict(zip(symbols, map(sympify, point))))
    eigenvalues = [simplify(value) for value in evaluated.eigenvals().keys()]
    if all(value.is_positive for value in eigenvalues):
        classification = "positive_definite"
    elif all(value.is_negative for value in eigenvalues):
        classification = "negative_definite"
    elif any(value.is_positive for value in eigenvalues) and any(value.is_negative for value in eigenvalues):
        classification = "indefinite"
    else:
        classification = "inconclusive"
    return {"expression": str(parsed), "point": list(point), "eigenvalues": [str(value) for value in eigenvalues], "classification": classification}


def analyze_complex_identity() -> dict[str, Any]:
    """Check Euler's identity while recording the complex branch convention."""
    angle = Symbol("theta", real=True)
    residual = simplify(exp(I * pi) + 1)
    return {
        "domain": "complex",
        "identity": "exp(I*pi) + 1 = 0",
        "residual": str(residual),
        "is_identity": residual == 0,
        "branch_convention": "principal complex exponential; real theta parameter",
        "sample_parameter": str(angle),
    }


def analyze_complex_trigonometry() -> dict[str, Any]:
    """Check the complex sine/cosine identity symbolically."""
    z = Symbol("z")
    residual = simplify(sin(z) ** 2 + cos(z) ** 2 - 1)
    return {
        "domain": "complex",
        "identity": "sin(z)**2 + cos(z)**2 = 1",
        "residual": str(residual),
        "is_identity": residual == 0,
        "branch_convention": "entire complex sine and cosine functions",
    }


def analyze_complex_branches() -> dict[str, Any]:
    """Record principal-branch behavior at the negative real axis."""
    negative_one = -1
    return {
        "domain": "complex",
        "branch_convention": "principal branch for complex log and sqrt",
        "log_negative_one": str(log(negative_one).rewrite(exp)),
        "sqrt_negative_one": str(sqrt(negative_one)),
        "log_branch_cut_reference": "negative real axis",
        "sqrt_branch_cut_reference": "negative real axis",
    }


def rank_conjectures(candidates: Iterable[tuple[str, str]]) -> dict[str, Any]:
    """Rank candidates using symbolic residual evidence, without claiming proof scope."""
    results = []
    for left, right in candidates:
        residual = simplify(sympify(left) - sympify(right))
        results.append({
            "left": left,
            "right": right,
            "residual": str(residual),
            "candidate_status": "supported_symbolically" if residual == 0 else "rejected_symbolically",
            "proof_scope": "symbolic residual only",
        })
    return {
        "candidate_count": len(results),
        "supported_count": sum(item["candidate_status"] == "supported_symbolically" for item in results),
        "results": results,
    }
