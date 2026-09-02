"""Deterministic catalog of 10,000 parameterized mathematical functions."""

from dataclasses import dataclass
from typing import Any, Callable

from sympy import Abs, Symbol, cos, exp, log, sin, sqrt


@dataclass(frozen=True)
class FunctionSpec:
    id: str
    family: str
    formula: str
    apply: Callable[[Any], Any]


def build_catalog() -> tuple[FunctionSpec, ...]:
    variable = Symbol("u", real=True)
    catalog: list[FunctionSpec] = []

    def add(family: str, index: int, formula: str, operation: Callable[[Any], Any]) -> None:
        catalog.append(FunctionSpec(f"{family}_{index:04d}", family, formula, operation))

    for index in range(1, 1001):
        add("affine", index, f"{index}*u + {index - 1}", lambda value, n=index: n * value + n - 1)
        add("power", index, f"u**{index}", lambda value, n=index: value**n)
        add("scaled_power", index, f"{index}*u**{index}", lambda value, n=index: n * value**n)
        add("sine", index, f"sin({index}*u)", lambda value, n=index: sin(n * value))
        add("cosine", index, f"cos({index}*u)", lambda value, n=index: cos(n * value))
        add("exponential", index, f"exp({index}*u)", lambda value, n=index: exp(n * value))
        add("logarithm", index, f"log(u + {index})", lambda value, n=index: log(value + n))
        add("root", index, f"sqrt(u + {index})", lambda value, n=index: sqrt(value + n))
        add("absolute", index, f"abs(u - {index})", lambda value, n=index: Abs(value - n))
        add("reciprocal", index, f"1/(u - {index})", lambda value, n=index: 1 / (value - n))

    assert len(catalog) == 10_000
    return tuple(catalog)
