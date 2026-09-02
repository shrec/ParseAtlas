"""Domain-aware symbolic conversion and reproducible AST helpers."""

from fractions import Fraction
from typing import Any

from sympy import Add, Integer, Mul, Rational, Symbol, simplify, solve

from .parser import Binary, Node, Number, Variable


def to_sympy(node: Node) -> Any:
    if isinstance(node, Number):
        if node.value.denominator == 1:
            return Integer(node.value.numerator)
        return Rational(node.value.numerator, node.value.denominator)
    if isinstance(node, Variable):
        return Symbol(node.name, real=True)
    left = to_sympy(node.left)
    right = to_sympy(node.right)
    if node.operator == "+":
        return Add(left, right)
    if node.operator == "-":
        return Add(left, -right)
    if node.operator == "*":
        return Mul(left, right)
    if node.operator == "/":
        return Mul(left, right**-1)
    raise ValueError(f"Unsupported operator: {node.operator}")


def _display(node: Node) -> str:
    if isinstance(node, Number):
        return str(node.value.numerator) if node.value.denominator == 1 else f"{node.value.numerator}/{node.value.denominator}"
    if isinstance(node, Variable):
        return node.name
    return f"({_display(node.left)} {node.operator} {_display(node.right)})"


def undefined_terms(node: Node) -> tuple[str, ...]:
    if isinstance(node, (Number, Variable)):
        return ()
    terms = undefined_terms(node.left) + undefined_terms(node.right)
    if node.operator == "/" and (not isinstance(node.right, Number) or node.right.value == 0):
        denominator = to_sympy(node.right)
        variables = sorted(denominator.free_symbols, key=str)
        if variables:
            terms += tuple(str(point) for point in solve(denominator, variables[0]))
        elif denominator == 0:
            terms += ("all",)
    return tuple(dict.fromkeys(terms))


def canonicalize(node: Node) -> dict[str, Any]:
    expression = to_sympy(node)
    simplified = simplify(expression)
    undefined = undefined_terms(node)
    return {
        "expression": str(simplified),
        "domain": "R",
        "excluded_points": list(undefined),
        "raw_sympy_expression": expression,
        "sympy_expression": simplified,
        "sympy_srepr": simplified.func.__name__ + "(" + ", ".join(str(arg) for arg in simplified.args) + ")",
    }


def ast_to_dict(node: Node) -> dict[str, Any]:
    if isinstance(node, Number):
        return {"type": "number", "value": str(node.value)}
    if isinstance(node, Variable):
        return {"type": "variable", "name": node.name}
    return {
        "type": "binary",
        "operator": node.operator,
        "left": ast_to_dict(node.left),
        "right": ast_to_dict(node.right),
    }


def operation_cost(node: Node) -> dict[str, int]:
    if isinstance(node, (Number, Variable)):
        return {"add": 0, "sub": 0, "mul": 0, "div": 0, "nodes": 1, "depth": 1}
    left = operation_cost(node.left)
    right = operation_cost(node.right)
    result = {key: left[key] + right[key] for key in ("add", "sub", "mul", "div")}
    result[node.operator.replace("+", "add").replace("-", "sub").replace("*", "mul").replace("/", "div")] += 1
    result["nodes"] = left["nodes"] + right["nodes"] + 1
    result["depth"] = max(left["depth"], right["depth"]) + 1
    return result
