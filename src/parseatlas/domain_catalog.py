"""Deterministic cross-domain mathematical formula catalog."""

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class FormulaSpec:
    id: str
    domain: str
    name: str
    formula: str
    variables: tuple[str, ...]


DOMAINS = (
    "quadratic_equations",
    "geometry",
    "algebra",
    "calculus",
    "trigonometry",
    "differential_equations",
    "probability_statistics",
    "number_theory",
)


def build_formula_catalog(per_domain: int = 125) -> tuple[FormulaSpec, ...]:
    if per_domain < 1:
        raise ValueError("per_domain must be positive")
    formulas: list[FormulaSpec] = []
    for domain, index in product(DOMAINS, range(1, per_domain + 1)):
        n = index
        if domain == "quadratic_equations":
            formula, name, variables = f"{n}*x**2 + {n + 1}*x + {n + 2} = 0", "quadratic equation", ("x",)
        elif domain == "geometry":
            formula, name, variables = f"area={n}*base*height/2; perimeter=2*({n}+width)", "triangle and rectangle measures", ("base", "height", "width")
        elif domain == "algebra":
            formula, name, variables = f"(x + {n})*(x - {n})", "difference of squares", ("x",)
        elif domain == "calculus":
            formula, name, variables = f"d/dx(x**{n})={n}*x**{n - 1}", "power-rule derivative", ("x",)
        elif domain == "trigonometry":
            formula, name, variables = f"sin({n}*x)**2 + cos({n}*x)**2 = 1", "Pythagorean identity", ("x",)
        elif domain == "differential_equations":
            formula, name, variables = f"y'={n}*y", "exponential-growth ODE", ("t", "y")
        elif domain == "probability_statistics":
            formula, name, variables = f"E[X]={n}; Var(X)={n}**2", "moment specification", ("X",)
        else:
            formula, name, variables = f"gcd(x,{n})", "greatest common divisor", ("x",)
        formulas.append(FormulaSpec(f"{domain}_{n:04d}", domain, name, formula, variables))
    return tuple(formulas)


def catalog_summary(per_domain: int = 125) -> dict[str, object]:
    catalog = build_formula_catalog(per_domain)
    return {
        "formula_count": len(catalog),
        "domain_count": len(DOMAINS),
        "per_domain": per_domain,
        "domains": list(DOMAINS),
        "counts": {domain: sum(item.domain == domain for item in catalog) for domain in DOMAINS},
    }
