"""The geometry of the 25 worlds: what a standard curve equation denotes under each precedence.

Experiment 0040. This is the geometric arm of the programme that :mod:`parseatlas.alternative_mathematics`
(experiment 0035) runs on algebra. Geometry is the sharper instrument, because a curve carries a
*classification* - line, circle, ellipse, parabola, hyperbola, cubic, quartic - and a classification
is a coarse, robust, human-legible label. Two worlds can disagree about a polynomial's coefficients
and still be studying the same kind of object; when they disagree about the classification they are
studying different geometry.

The headline this module measures: **in `12` of the `25` worlds the standard written form of a
straight line, ``y - m*x - c``, does not denote a line.** It denotes ``(x - c)*(y - m)``, a
degenerate conic - the pair of axis-parallel lines ``x = c`` and ``y = m`` - which is not the locus a
geometer writing that string intended and is not even a single curve.

Nothing here decides what a grammar "should" do. Every field is produced by parsing the written form
with :func:`parseatlas.parser.parse`, canonicalising it with
:func:`parseatlas.canonical.canonicalize`, and classifying the result from its own coefficients.
Worlds are collapsed onto the project's semantic key -
``(canonical expression, domain, excluded points)`` - the same triple
:func:`parseatlas.analyze.analyze_expression`, :func:`parseatlas.corpus_matrix.expression_classes`
and :mod:`parseatlas.alternative_mathematics` use, imported from there rather than re-implemented.
One standing disclosure about that key (repository-wide ``NF-2026-00005``):
:func:`parseatlas.canonical.canonicalize` writes the literal string ``"R"`` into ``domain`` for every
expression it ever produces, so the component that actually discriminates is
``(canonical expression, excluded points)`` and ``domain`` is a fixed declaration of the analysis
setting rather than a measured field.

**Rational readings.** Under a permuted precedence a written form that is a polynomial in our world
is often a rational function of the coordinates: ``x*x/4 + y*y/9 - 1`` acquires a denominator
containing ``y`` in `12` of the `25` worlds, and ``y - w/x - v`` has one in all `25`. ``Poly``
refuses those outright, which is where a naive probe dies. So every expression is first put over a
common denominator with :func:`sympy.together` and split with :func:`sympy.fraction`, and the
**numerator** is classified. That is the geometrically right move as well as the mechanically safe
one: the zero set of ``N/D`` is the zero set of ``N`` with the poles of ``D`` removed, so the
numerator carries the curve and the denominator carries the punctures. The denominator is never
discarded silently - :func:`classify` records it in ``denominator``, ``denominator_set_aside``,
``denominator_punctures`` and ``excluded_locus``, the report prints it, and the figures draw its own
zero set as a dashed line. A constant denominator is recorded but punctures nothing.

**Degree convention.** The degree of a plane curve is its degree in the *coordinates*. ``r`` in
``x*x + y*y - r*r`` names a family of curves, it is not a direction in the plane, so
``total_degree`` counts only the declared curve variables. The degree over every free symbol is a
different number and is reported separately as ``ambient_total_degree``; the two disagree, and where
they disagree the report says so rather than picking whichever is more striking.
"""

import os
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from sympy import (
    Basic,
    Matrix,
    Poly,
    Symbol,
    expand,
    factor_list,
    fraction,
    lambdify,
    linsolve,
    simplify,
    sympify,
    together,
)
from sympy.polys.polytools import sqf_part
from sympy.polys.polyerrors import GeneratorsNeeded, PolynomialError

from .canonical import canonicalize
from .grammar import Grammar, all_grammars
from .parser import parse

# the semantic key is the project's, imported rather than re-implemented, so that "same object"
# means here exactly what it means in analyze_expression and in experiment 0035.
from .alternative_mathematics import semantic_key


# ------------------------------------------------------------------------------------- catalogue


@dataclass(frozen=True)
class StandardCurve:
    """One curve as geometry actually writes it, plus what is a coordinate and what is a parameter.

    ``source`` is the written form. ``variables`` are the two coordinates of the plane the curve
    lives in; every other free symbol is a parameter naming a member of a family. ``parameters``
    are the values the figures are drawn at - they never enter the classification, which is done on
    the symbolic form, and where a symbolic classification is conditional on a parameter's sign the
    record carries the resolved label at these values alongside, marked as such.
    """

    name: str
    area: str
    source: str
    variables: tuple[str, str]
    parameters: tuple[tuple[str, int], ...]
    window: tuple[float, float, float, float]
    note: str

    @property
    def parameter_map(self) -> dict[str, int]:
        return dict(self.parameters)


#: The named curves, written as Generation 1 can write them. Hand-chosen - see the report's limits.
#: Generation 1 has no exponentiation operator, so every square is written out as a product:
#: ``x*x`` and not ``x**2``. That is a property of the grammar under study, not a stylistic choice,
#: and it is exactly the property that makes the squares vulnerable to a precedence permutation.
CURVE_CATALOGUE: tuple[StandardCurve, ...] = (
    StandardCurve(
        "line", "linear", "y - m*x - c", ("x", "y"),
        (("m", 1), ("c", 1)), (-6.0, 6.0, -6.0, 6.0),
        "slope-intercept form, the first equation of a curve anyone is taught",
    ),
    StandardCurve(
        "circle", "conic", "x*x + y*y - r*r", ("x", "y"),
        (("r", 2),), (-6.0, 6.0, -6.0, 6.0),
        "the circle of radius r about the origin",
    ),
    StandardCurve(
        # a wider window than the rest of the catalogue: one of this entry's thirteen readings is a
        # hyperbola whose vertices sit at x = +-6, and a [-6, 6] window would show two dots.
        "ellipse", "conic", "x*x/4 + y*y/9 - 1", ("x", "y"),
        (), (-9.0, 9.0, -9.0, 9.0),
        "semi-axes 2 and 3, written with numeric denominators as a textbook writes it",
    ),
    StandardCurve(
        "hyperbola", "conic", "x*x/4 - y*y/9 - 1", ("x", "y"),
        (), (-6.0, 6.0, -6.0, 6.0),
        "the same axes with the sign of the y term reversed",
    ),
    StandardCurve(
        "parabola", "conic", "y - a*x*x - b*x - c", ("x", "y"),
        (("a", 1), ("b", 2), ("c", 3)), (-6.0, 6.0, -6.0, 6.0),
        "the graph of a quadratic, read as a curve in the plane",
    ),
    StandardCurve(
        "distance_components", "metric", "(x - p)*(x - p) + (y - q)*(y - q) - d*d", ("x", "y"),
        (("p", 1), ("q", -1), ("d", 2)), (-6.0, 6.0, -6.0, 6.0),
        "the distance formula squared: the locus at distance d from (p, q)",
    ),
    StandardCurve(
        "midpoint_component", "metric", "x + y/2 - m", ("x", "y"),
        (("m", 3),), (-6.0, 6.0, -6.0, 6.0),
        "one coordinate of a midpoint, held fixed; a halving written the way a mean is written",
    ),
    StandardCurve(
        "slope_form", "metric", "y - w/x - v", ("x", "y"),
        (("w", 2), ("v", 1)), (-6.0, 6.0, -6.0, 6.0),
        "the slope relation, the one written form in the catalogue with a genuine division by x",
    ),
    StandardCurve(
        "pythagorean_form", "metric", "a*a + b*b - c*c", ("a", "b"),
        (("c", 2),), (-6.0, 6.0, -6.0, 6.0),
        "the Pythagorean relation read as a curve in the (a, b) plane",
    ),
    StandardCurve(
        "trapezoid_area", "metric", "(x + y)*h/2 - s", ("x", "y"),
        (("h", 2), ("s", 3)), (-6.0, 6.0, -6.0, 6.0),
        "a trapezoid of height h and area s, as a relation between its two parallel sides",
    ),
    StandardCurve(
        "circle_through_origin", "conic", "x*x + y*y - a*x - b*y", ("x", "y"),
        (("a", 2), ("b", 2)), (-6.0, 6.0, -6.0, 6.0),
        "a circle with no constant term, so that it passes through the origin in every world",
    ),
    StandardCurve(
        "degenerate_pair", "degenerate", "(x - y)*(x + y)", ("x", "y"),
        (), (-6.0, 6.0, -6.0, 6.0),
        "two lines written as a product; fully parenthesised on purpose, as a control",
    ),
)


#: Below this many work items the automatic worker choice stays sequential: on the spawn start
#: method every worker process pays a full SymPy import before it does any work. This is a policy
#: floor and not the decision - :func:`parallelism_measurement` measures the real one on the host.
PARALLEL_MINIMUM_ITEMS: int = 32


# --------------------------------------------------------------------------- symbolic classifier


def curve_symbols(variables: Sequence[str | Symbol]) -> tuple[Symbol, ...]:
    """The symbols :func:`parseatlas.canonical.to_sympy` builds, so assumptions match exactly."""
    return tuple(
        variable if isinstance(variable, Symbol) else Symbol(str(variable), real=True)
        for variable in variables
    )


def _symbols_in(expression: Any, variables: Sequence[str | Symbol]) -> tuple[Symbol, ...]:
    """The coordinate symbols *as they occur in this expression*, by name.

    A symbol's assumptions are part of its identity in SymPy, so ``Symbol("x", real=True)`` and the
    ``Symbol("x")`` a bare :func:`sympy.sympify` builds are different generators and ``Poly`` would
    silently treat one of them as a constant. Matching by name is what lets :func:`classify` accept
    both a canonical expression from the parser and a hand-written string in a test.
    """
    present = {str(symbol): symbol for symbol in expression.free_symbols}
    return tuple(
        present.get(str(variable), variable)
        if isinstance(variable, Symbol)
        else present.get(str(variable), Symbol(str(variable), real=True))
        for variable in variables
    )


def _sign_of(expression: Any) -> str:
    """``"positive"`` / ``"negative"`` / ``"zero"`` / ``"unknown"`` for a possibly symbolic value.

    ``"unknown"`` is a real answer and is never rounded to one of the others: with a free real
    parameter, ``-4*r`` genuinely has no sign until ``r`` does.
    """
    value = simplify(expression)
    if value.is_zero:
        return "zero"
    if value.is_positive:
        return "positive"
    if value.is_negative:
        return "negative"
    return "unknown"


def _factor_components(numerator: Any, variables: tuple[Symbol, ...]) -> list[dict[str, Any]]:
    """The irreducible factors of the numerator that actually involve the coordinates."""
    try:
        _, factors = factor_list(numerator)
    except (PolynomialError, GeneratorsNeeded, TypeError, ValueError):
        return []
    components: list[dict[str, Any]] = []
    for factor, multiplicity in factors:
        if not factor.has(*variables):
            continue
        try:
            degree = int(Poly(factor, *variables).total_degree())
        except (PolynomialError, GeneratorsNeeded, TypeError, ValueError):
            degree = -1
        components.append({"factor": str(factor), "multiplicity": int(multiplicity), "degree": degree})
    return components


def _conic_coefficients(poly: Poly, x: Symbol, y: Symbol) -> dict[str, Any]:
    """``A x^2 + B x y + C y^2 + D x + E y + F`` read straight off the polynomial."""
    return {
        "A": poly.coeff_monomial(x**2),
        "B": poly.coeff_monomial(x * y),
        "C": poly.coeff_monomial(y**2),
        "D": poly.coeff_monomial(x),
        "E": poly.coeff_monomial(y),
        "F": poly.coeff_monomial(1),
    }


def _degree_label(degree: int) -> str:
    return {3: "cubic curve", 4: "quartic curve"}.get(degree, f"degree {degree} curve")


def classify(expression: Any, variables: Sequence[str | Symbol]) -> dict[str, Any]:
    """Classify the plane curve an expression denotes, from its coefficients and nothing else.

    The expression is first put over a common denominator (:func:`sympy.together`) and split
    (:func:`sympy.fraction`); the **numerator** is what is classified, and the denominator is
    recorded in ``denominator`` / ``denominator_set_aside`` / ``excluded_locus`` rather than
    dropped. The zero set of ``N/D`` is the zero set of ``N`` minus the poles of ``D``, so this is
    the geometrically faithful split as well as the one that keeps ``Poly`` from refusing the input.

    ``variables`` are the coordinates of the plane. Every other free symbol is a parameter. Degrees
    are counted in the coordinates (``total_degree``, ``variable_degrees``); the degree over all
    free symbols is reported separately as ``ambient_total_degree``.

    **The rule for every label this function can return:**

    ``whole plane (identically zero)``
        the numerator is ``0``: every point satisfies the equation.
    ``empty locus (constant in the coordinates)``
        the numerator has coordinate-degree ``0`` and is not ``0``: no point satisfies it.
    ``line``
        coordinate-degree ``1``. A degree-one equation in two coordinates is a straight line, and
        that includes the axis-parallel cases where one coordinate is absent.
    ``conic: circle``
        coordinate-degree ``2``, ``B = 0``, ``A = C``, and the ``3x3`` discriminant determinant
        ``det [[A, B/2, D/2], [B/2, C, E/2], [D/2, E/2, F]]`` is not identically zero.
    ``conic: ellipse`` / ``conic: parabola`` / ``conic: hyperbola``
        coordinate-degree ``2``, non-degenerate, and the standard discriminant ``B^2 - 4*A*C`` is
        negative / zero / positive respectively.
    ``degenerate conic: two intersecting lines`` / ``... two parallel lines`` /
    ``... a double line`` / ``... a single point``
        coordinate-degree ``2`` with the ``3x3`` determinant **identically** zero. Which of the four
        is decided by the same discriminant: positive gives two intersecting real lines, zero gives
        parallel lines - a double line when the factorisation carries a repeated linear factor -
        and negative gives the single real point of two conjugate imaginary lines.
    ``cubic curve`` / ``quartic curve`` / ``degree N curve``
        coordinate-degree ``3`` / ``4`` / ``N``. ``reducible`` and ``factors`` say whether the
        curve splits, and ``component_of_lines`` is true when every factor is linear, i.e. when the
        "curve" is a finite union of straight lines.
    ``conic (type set by the sign of B^2-4AC = ...)`` and
    ``degenerate conic (kind set by the sign of B^2-4AC = ...)``
        coordinate-degree ``2`` with a symbolic discriminant whose sign does not follow from the
        real-parameter assumptions alone. This is a refusal, not a label: the branch expressions are
        listed in ``conditional_branches`` and the caller may resolve them at chosen parameter
        values. A label that cannot be justified from the coefficients is not issued.
    ``not polynomial in the coordinates after clearing denominators``
        the numerator is not a polynomial in ``variables`` at all. It cannot occur for Generation 1
        readings, which are always rational, and is reported rather than raised so that a sweep
        never dies on one cell.

    Degeneracy is decided on *identical* vanishing of the determinant. A determinant that merely
    *can* vanish for special parameter values - ``-r**2`` for the circle - leaves the curve
    non-degenerate generically, and the vanishing locus is recorded in ``degeneracy_locus``.
    """
    expr = expression if isinstance(expression, Basic) else sympify(expression)
    symbols = _symbols_in(expr, variables)
    togethered = together(expr)
    numerator, denominator = fraction(togethered)
    numerator = expand(numerator)
    denominator = expand(denominator)

    record: dict[str, Any] = {
        "variables": [str(symbol) for symbol in symbols],
        "expression": str(expr),
        "numerator": str(numerator),
        "denominator": str(denominator),
        "denominator_set_aside": bool(denominator != 1),
        # a constant denominator such as the 36 of x*x/4 + y*y/9 - 1 sets nothing aside: it removes
        # no point of the plane. Only a denominator that involves a coordinate punctures the curve.
        "denominator_punctures": False,
        "excluded_locus": None,
        "label": None,
        "family": None,
        "total_degree": None,
        "ambient_total_degree": None,
        "variable_degrees": {},
        "has_cross_term": False,
        "has_mixed_monomial": False,
        "conic_coefficients": None,
        "discriminant": None,
        "discriminant_sign": None,
        "determinant": None,
        "degenerate": None,
        "degeneracy_locus": None,
        "conditional": False,
        "conditional_branches": None,
        "factors": [],
        "reducible": None,
        "component_of_lines": None,
        "notes": [],
    }

    record["denominator_punctures"] = bool(denominator.has(*symbols))
    if record["denominator_punctures"]:
        record["excluded_locus"] = f"{denominator} = 0"

    if numerator == 0:
        record["label"] = "whole plane (identically zero)"
        record["family"] = "degenerate"
        record["total_degree"] = 0
        record["ambient_total_degree"] = 0
        record["variable_degrees"] = {str(symbol): 0 for symbol in symbols}
        return record

    try:
        poly = Poly(numerator, *symbols)
    except (PolynomialError, GeneratorsNeeded, TypeError, ValueError):
        record["label"] = "not polynomial in the coordinates after clearing denominators"
        record["family"] = "non-polynomial"
        return record

    total_degree = int(poly.total_degree())
    record["total_degree"] = total_degree
    record["variable_degrees"] = {
        str(symbol): int(Poly(numerator, symbol).degree()) if numerator.has(symbol) else 0
        for symbol in symbols
    }
    free = sorted(numerator.free_symbols, key=str)
    try:
        record["ambient_total_degree"] = int(Poly(numerator, *free).total_degree()) if free else 0
    except (PolynomialError, GeneratorsNeeded, TypeError, ValueError):
        record["ambient_total_degree"] = None

    if len(symbols) == 2:
        x, y = symbols
        record["has_cross_term"] = bool(poly.coeff_monomial(x * y) != 0)
        record["has_mixed_monomial"] = any(
            monomial[0] >= 1 and monomial[1] >= 1 for monomial in poly.monoms()
        )

    components = _factor_components(numerator, symbols)
    record["factors"] = components
    record["reducible"] = sum(item["multiplicity"] for item in components) > 1
    record["component_of_lines"] = bool(components) and all(item["degree"] == 1 for item in components)

    if total_degree == 0:
        record["label"] = "empty locus (constant in the coordinates)"
        record["family"] = "degenerate"
        return record

    if total_degree == 1:
        record["label"] = "line"
        record["family"] = "line"
        return record

    if total_degree == 2 and len(symbols) == 2:
        return _classify_conic(record, poly, symbols)

    record["label"] = _degree_label(total_degree)
    record["family"] = {3: "cubic", 4: "quartic"}.get(total_degree, "higher")
    if record["component_of_lines"]:
        count = sum(item["multiplicity"] for item in components)
        record["notes"].append(f"reducible: a union of {count} straight lines")
    return record


def _classify_conic(record: dict[str, Any], poly: Poly, symbols: tuple[Symbol, ...]) -> dict[str, Any]:
    """The degree-two branch of :func:`classify`; see that docstring for the rule of every label."""
    x, y = symbols
    coefficients = _conic_coefficients(poly, x, y)
    A, B, C, D, E, F = (coefficients[key] for key in ("A", "B", "C", "D", "E", "F"))
    discriminant = simplify(B**2 - 4 * A * C)
    determinant = simplify(
        Matrix([[A, B / 2, D / 2], [B / 2, C, E / 2], [D / 2, E / 2, F]]).det()
    )
    discriminant_sign = _sign_of(discriminant)
    determinant_sign = _sign_of(determinant)

    record["family"] = "conic"
    record["conic_coefficients"] = {key: str(value) for key, value in coefficients.items()}
    record["discriminant"] = str(discriminant)
    record["discriminant_sign"] = discriminant_sign
    record["determinant"] = str(determinant)
    record["degenerate"] = determinant_sign == "zero"
    if determinant_sign == "unknown":
        record["degeneracy_locus"] = f"{determinant} = 0"
        record["notes"].append(
            "non-degenerate for generic parameters; the determinant vanishes only on "
            f"{determinant} = 0"
        )

    if discriminant_sign == "unknown":
        record["conditional"] = True
        kind = "degenerate conic" if record["degenerate"] else "conic"
        record["label"] = f"{kind} (type set by the sign of B^2-4AC = {discriminant})"
        record["conditional_branches"] = (
            {
                "negative": "degenerate conic: a single point",
                "zero": "degenerate conic: two parallel lines",
                "positive": "degenerate conic: two intersecting lines",
            }
            if record["degenerate"]
            else {
                "negative": "conic: ellipse",
                "zero": "conic: parabola",
                "positive": "conic: hyperbola",
            }
        )
        return record

    if record["degenerate"]:
        record["family"] = "degenerate conic"
        if discriminant_sign == "positive":
            record["label"] = "degenerate conic: two intersecting lines"
        elif discriminant_sign == "negative":
            record["label"] = "degenerate conic: a single point"
        else:
            repeated = any(
                item["degree"] == 1 and item["multiplicity"] > 1 for item in record["factors"]
            )
            record["label"] = (
                "degenerate conic: a double line" if repeated else "degenerate conic: two parallel lines"
            )
        return record

    if discriminant_sign == "negative":
        circular = _sign_of(B) == "zero" and _sign_of(A - C) == "zero"
        record["label"] = "conic: circle" if circular else "conic: ellipse"
    elif discriminant_sign == "zero":
        record["label"] = "conic: parabola"
    else:
        record["label"] = "conic: hyperbola"
    return record


# ------------------------------------------------------------------------------ one world's read


def curve_in_world(
    source: str,
    grammar: Grammar,
    variables: Sequence[str] = ("x", "y"),
    parameters: Sequence[tuple[str, Any]] | dict[str, Any] = (),
) -> dict[str, Any]:
    """What the standard written form ``source`` denotes as a curve in the world ``grammar``.

    Returns the expanded polynomial, the total degree, the degree in each coordinate, whether an
    ``x*y`` cross term is present, and the classification - plus the project's semantic key, so the
    record can be grouped without a second parse.

    ``parameters`` are optional values for the non-coordinate symbols. They never affect
    ``classification``, which is symbolic. They produce ``classification_at_parameters``, which is
    what resolves a conditional label such as *"type set by the sign of ``-4*r``"* into a definite
    one, and what the figures are drawn from.
    """
    node = parse(source, grammar)
    canonical = canonicalize(node)
    expression = canonical["sympy_expression"]
    classification = classify(expression, variables)
    substitutions = dict(parameters)

    resolved: dict[str, Any] | None = None
    if substitutions:
        symbols = {Symbol(name, real=True): value for name, value in substitutions.items()}
        resolved = classify(expression.subs(symbols), variables)

    numerator = classification["numerator"]
    denominator = classification["denominator"]
    if resolved is not None:
        drawn_numerator, drawn_denominator = resolved["numerator"], resolved["denominator"]
    else:
        drawn_numerator, drawn_denominator = numerator, denominator

    return {
        "source": source,
        "grammar": grammar.id,
        "precedence": " > ".join("=".join(level) for level in grammar.levels),
        "variables": list(variables),
        "canonical": canonical["expression"],
        "expanded": str(expand(expression)),
        "excluded_points": list(canonical["excluded_points"]),
        "semantic_key": semantic_key(canonical),
        "total_degree": classification["total_degree"],
        "ambient_total_degree": classification["ambient_total_degree"],
        "variable_degrees": classification["variable_degrees"],
        "has_cross_term": classification["has_cross_term"],
        "denominator_set_aside": classification["denominator_set_aside"],
        "denominator_punctures": classification["denominator_punctures"],
        "denominator": denominator,
        "numerator": numerator,
        "classification": classification,
        "classification_at_parameters": resolved,
        "label": classification["label"],
        "resolved_label": (resolved or classification)["label"],
        "label_source": (
            "coefficients at the declared parameter values"
            if classification["conditional"] and resolved is not None
            else "coefficients"
        ),
        "drawn_numerator": drawn_numerator,
        "drawn_denominator": drawn_denominator,
    }


# ------------------------------------------------------------------------------------- the atlas


def _cell(payload: tuple[StandardCurve, Grammar]) -> dict[str, Any]:
    """One (curve, world) pair. Module level and picklable: this is the unit the pool distributes."""
    entry, grammar = payload
    record = curve_in_world(entry.source, grammar, entry.variables, entry.parameters)
    record["curve"] = entry.name
    return record


def resolve_worker_count(item_count: int, workers: int | None = None) -> int:
    """Derive the process count from the observed cores, never from a hardcoded constant."""
    if workers is not None:
        return max(1, min(int(workers), max(item_count, 1)))
    if item_count < PARALLEL_MINIMUM_ITEMS:
        return 1
    cores = os.cpu_count() or 1
    return max(1, min(cores - 1, item_count))  # one core of headroom for the interactive session


def _group_cells(
    entry: StandardCurve, grammars: Sequence[Grammar], cells: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    """Collapse one curve's worlds onto the semantic key, largest group first."""
    by_grammar = {cell["grammar"]: cell for cell in cells}
    groups: dict[Any, dict[str, Any]] = {}
    order: list[Any] = []
    for grammar in grammars:
        cell = by_grammar[grammar.id]
        key = cell["semantic_key"]
        if key not in groups:
            groups[key] = {
                "canonical": key[0],
                "domain": key[1],
                "excluded_points": list(key[2]),
                "expanded": cell["expanded"],
                "numerator": cell["numerator"],
                "denominator": cell["denominator"],
                "denominator_set_aside": cell["denominator_set_aside"],
                "denominator_punctures": cell["denominator_punctures"],
                "excluded_locus": cell["classification"]["excluded_locus"],
                "total_degree": cell["total_degree"],
                "ambient_total_degree": cell["ambient_total_degree"],
                "variable_degrees": cell["variable_degrees"],
                "has_cross_term": cell["has_cross_term"],
                "label": cell["label"],
                "resolved_label": cell["resolved_label"],
                "label_source": cell["label_source"],
                "conditional": cell["classification"]["conditional"],
                "family": cell["classification"]["family"],
                "discriminant": cell["classification"]["discriminant"],
                "determinant": cell["classification"]["determinant"],
                "factors": cell["classification"]["factors"],
                "component_of_lines": cell["classification"]["component_of_lines"],
                "notes": cell["classification"]["notes"],
                "drawn_numerator": cell["drawn_numerator"],
                "drawn_denominator": cell["drawn_denominator"],
                "grammars": [],
            }
            order.append(key)
        groups[key]["grammars"].append(grammar.id)

    ranked = sorted(order, key=lambda key: (-len(groups[key]["grammars"]), groups[key]["grammars"][0]))
    objects = []
    for index, key in enumerate(ranked, start=1):
        item = dict(groups[key])
        item["object_id"] = f"O{index:02d}"
        item["grammar_count"] = len(item["grammars"])
        objects.append(item)

    control = next((item for item in objects if "G0" in item["grammars"]), None)
    labels = {item["resolved_label"] for item in objects}
    texts = {item["canonical"] for item in objects}
    return {
        "name": entry.name,
        "area": entry.area,
        "written_form": entry.source,
        "variables": list(entry.variables),
        "parameters": dict(entry.parameters),
        "note": entry.note,
        "window": list(entry.window),
        "grammar_count": len(grammars),
        "distinct_object_count": len(objects),
        "canonical_text_count": len(texts),
        "restriction_split_objects": len(objects) - len(texts),
        "distinct_label_count": len(labels),
        "objects": objects,
        "control_object_id": control["object_id"] if control else None,
        "control_group_size": control["grammar_count"] if control else 0,
        "control_label": control["resolved_label"] if control else None,
        "control_grammars": list(control["grammars"]) if control else [],
        "label_agreement_with_control": sum(
            item["grammar_count"] for item in objects
            if control is not None and item["resolved_label"] == control["resolved_label"]
        ),
        "cross_term_grammar_count": sum(
            item["grammar_count"] for item in objects if item["has_cross_term"]
        ),
        "rational_grammar_count": sum(
            item["grammar_count"] for item in objects if item["denominator_punctures"]
        ),
    }


def atlas(
    catalogue: Sequence[StandardCurve] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The full cross product, with worlds that denote the SAME curve collapsed into one entry.

    Every ``(curve, world)`` cell is independent CPU-bound SymPy work, so the cell - not the curve -
    is the parallel unit: ``12 x 25 = 300`` items balance across the pool far better than ``12``
    would. Parallelism changes only how fast the atlas is measured; the ``workers=1`` path and the
    pool path produce identical records, which :func:`parallelism_measurement` checks rather than
    assumes.
    """
    catalogue = tuple(catalogue or CURVE_CATALOGUE)
    grammars = tuple(grammars or all_grammars())
    payloads = [(entry, grammar) for entry in catalogue for grammar in grammars]
    worker_count = resolve_worker_count(len(payloads), workers)
    started = time.perf_counter()
    if worker_count <= 1 or not payloads:
        cells = [_cell(payload) for payload in payloads]
    else:
        from concurrent.futures import ProcessPoolExecutor

        chunk = max(1, len(payloads) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            cells = list(pool.map(_cell, payloads, chunksize=chunk))

    by_curve: dict[str, list[dict[str, Any]]] = {entry.name: [] for entry in catalogue}
    for cell in cells:
        by_curve[cell["curve"]].append(cell)
    entries = [_group_cells(entry, grammars, by_curve[entry.name]) for entry in catalogue]
    counts = [entry["distinct_object_count"] for entry in entries]

    return {
        "entries": entries,
        "entry_count": len(entries),
        "grammar_count": len(grammars),
        "grammar_ids": [grammar.id for grammar in grammars],
        "cell_count": len(payloads),
        "distinct_object_counts": {entry["name"]: entry["distinct_object_count"] for entry in entries},
        "total_distinct_objects": sum(counts),
        "maximum_distinct_objects": max(counts) if counts else 0,
        "invariant_entry_count": sum(1 for value in counts if value == 1),
        "restriction_split_objects": sum(entry["restriction_split_objects"] for entry in entries),
        "workers": worker_count,
        "wall_clock_seconds": time.perf_counter() - started,
        "cpu_count": os.cpu_count(),
    }


# ------------------------------------------------------------------------------------- survival


def survival_report(
    catalogue: Sequence[StandardCurve] | None = None,
    grammars: Sequence[Grammar] | None = None,
    atlas_result: dict[str, Any] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Which curves keep their own classification in every world, and which keep it in the fewest.

    The geometry analogue of experiment 0036's identity survival. The reference classification is
    the control world's - what a geometer here means by the written form - and a world *survives*
    when its own reading carries the same label. Conditional labels are resolved at the catalogue's
    declared parameter values before comparison, and which entries needed that is reported.
    """
    result = atlas_result or atlas(catalogue, grammars, workers)
    rows = []
    for entry in result["entries"]:
        labels: dict[str, int] = {}
        for item in entry["objects"]:
            labels[item["resolved_label"]] = labels.get(item["resolved_label"], 0) + item["grammar_count"]
        survivors = entry["label_agreement_with_control"]
        rows.append(
            {
                "name": entry["name"],
                "area": entry["area"],
                "written_form": entry["written_form"],
                "control_label": entry["control_label"],
                "surviving_grammar_count": survivors,
                "grammar_count": entry["grammar_count"],
                "distinct_object_count": entry["distinct_object_count"],
                "distinct_label_count": entry["distinct_label_count"],
                "label_counts": dict(sorted(labels.items(), key=lambda kv: (-kv[1], kv[0]))),
                "conditional_objects": sum(1 for item in entry["objects"] if item["conditional"]),
                "surviving_grammars": sorted(
                    grammar
                    for item in entry["objects"]
                    if item["resolved_label"] == entry["control_label"]
                    for grammar in item["grammars"]
                ),
            }
        )
    ranked = sorted(rows, key=lambda row: (-row["surviving_grammar_count"], row["name"]))
    total = result["grammar_count"]
    return {
        "grammar_count": total,
        "rows": rows,
        "ranked": ranked,
        "fully_stable": [row["name"] for row in rows if row["surviving_grammar_count"] == total],
        "identical_in_every_world": [
            entry["name"] for entry in result["entries"] if entry["distinct_object_count"] == 1
        ],
        "least_stable": [row["name"] for row in ranked if row["surviving_grammar_count"] == ranked[-1]["surviving_grammar_count"]],
        "most_fractured": [
            entry["name"]
            for entry in result["entries"]
            if entry["distinct_object_count"] == result["maximum_distinct_objects"]
        ],
        "control_group_sizes": {
            entry["name"]: entry["control_group_size"] for entry in result["entries"]
        },
        "control_alone_on": [
            entry["name"] for entry in result["entries"] if entry["control_group_size"] == 1
        ],
        "control_twins": _control_twins(result),
    }


def _control_twins(result: dict[str, Any]) -> dict[str, int]:
    """How many of the catalogue's curves each world reads exactly as the control world does."""
    agreement: dict[str, int] = {identifier: 0 for identifier in result["grammar_ids"]}
    for entry in result["entries"]:
        control = next((item for item in entry["objects"] if "G0" in item["grammars"]), None)
        if control is None:
            continue
        for identifier in control["grammars"]:
            agreement[identifier] += 1
    return agreement


# ------------------------------------------------------------------------------ SVG: the drawing


BACKGROUND = "#ffffff"
PANEL_FILL = "#fbfaf7"
PANEL_EDGE = "#c9c6bd"
GRID = "#e4e1d9"
AXIS = "#8d8a80"
CURVE = "#b3261e"
POLE = "#7b8794"
TEXT = "#1b1b18"
MUTED = "#6b6860"
CONTROL = "#1a4a8a"

PLOT = 230
PAD = 12
HEADER = 54
FOOTER = 30
CELL_W = PLOT + 2 * PAD
CELL_H = HEADER + PLOT + FOOTER
MARGIN = 18
TITLE_H = 92
NOTE_H = 46
GRID_STEPS = 145


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


#: Conservative advance widths, as a fraction of the font size, for the two families the figures
#: use. They are estimates on purpose: an SVG has no text metrics, so the only way to guarantee that
#: nothing escapes the viewBox is to over-reserve. Measured against the widest glyphs of each family.
SANS_ADVANCE = 0.58
MONO_ADVANCE = 0.62


def _text_width(text: str, size: float, mono: bool = False) -> float:
    """An upper bound on the rendered width of a string, in pixels."""
    return len(str(text)) * size * (MONO_ADVANCE if mono else SANS_ADVANCE)


def _fit(text: str, pixels: float, size: float, mono: bool = False) -> str:
    """Truncate a string so that it cannot escape ``pixels`` of horizontal room."""
    text = str(text)
    advance = size * (MONO_ADVANCE if mono else SANS_ADVANCE)
    limit = max(4, int(pixels / advance))
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _number(value: float) -> str:
    rounded = round(float(value), 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:g}"


def zero_set_segments(
    function: Callable[[float, float], float | None],
    window: tuple[float, float, float, float],
    steps: int = GRID_STEPS,
) -> list[tuple[float, float, float, float]]:
    """Marching squares at level ``0``, in plain Python: no numpy, no matplotlib, no plotting stack.

    The grid is sampled, each cell's four corners are given a sign (a value of exactly ``0`` counts
    as negative so that a node on the curve still produces crossings on its edges), and each edge
    whose endpoints disagree contributes one linearly interpolated crossing point. Two crossings
    give one segment; the four-crossing saddle is resolved by the standard centre-value rule. A
    cell with any undefined corner is skipped, which is what leaves a visible gap rather than a
    fabricated line. Callers pass the **numerator**, which is a polynomial and therefore continuous,
    so this never has to guess its way across a pole.
    """
    xmin, xmax, ymin, ymax = window
    dx = (xmax - xmin) / (steps - 1)
    dy = (ymax - ymin) / (steps - 1)
    xs = [xmin + index * dx for index in range(steps)]
    ys = [ymin + index * dy for index in range(steps)]
    values: list[list[float | None]] = []
    for x in xs:
        column: list[float | None] = []
        for y in ys:
            try:
                value = function(x, y)
                column.append(float(value) if value == value and abs(value) != float("inf") else None)
            except (ZeroDivisionError, ValueError, TypeError, OverflowError):
                column.append(None)
        values.append(column)

    segments: list[tuple[float, float, float, float]] = []
    for i in range(steps - 1):
        for j in range(steps - 1):
            corners = (values[i][j], values[i + 1][j], values[i + 1][j + 1], values[i][j + 1])
            if any(corner is None for corner in corners):
                continue
            points = ((xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1]))
            crossings: list[tuple[float, float]] = []
            for edge in range(4):
                a, b = corners[edge], corners[(edge + 1) % 4]
                if (a > 0) == (b > 0):
                    continue
                t = a / (a - b) if a != b else 0.5
                pa, pb = points[edge], points[(edge + 1) % 4]
                crossings.append((pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1])))
            if len(crossings) == 2:
                segments.append((*crossings[0], *crossings[1]))
            elif len(crossings) == 4:
                centre = sum(corners) / 4.0
                pairs = ((0, 1), (2, 3)) if (centre > 0) == (corners[0] > 0) else ((0, 3), (1, 2))
                for first, second in pairs:
                    segments.append((*crossings[first], *crossings[second]))
    return segments


def _plane_callable(text: str, variables: Sequence[str], radical: bool = True):
    """A plain-Python ``f(x, y)`` for the two declared coordinates, plus the grid it is sampled on.

    ``modules=["math"]`` is deliberate and is the whole reason the figures exist as generated text:
    this repository depends on SymPy alone, numpy and matplotlib are not installed, and an SVG
    written from Python is dependency-free, diffs in git, renders on GitHub and is regenerable.

    ``radical`` replaces the polynomial by its square-free part before sampling. The zero *set* is
    unchanged by that - the radical of an ideal has the same variety - but a repeated factor makes
    the function touch zero without changing sign, and a contour tracer that only watches for sign
    changes would draw nothing at all. ``x*x`` is a double line and must be drawn as a line.
    """
    expression = sympify(text)
    symbols = tuple(Symbol(name) for name in variables)
    if radical:
        try:
            expression = sqf_part(expression, *symbols)
        except (PolynomialError, GeneratorsNeeded, TypeError, ValueError):
            pass
    return lambdify(symbols, expression, modules=["math"])


def single_point(expression: Any, variables: Sequence[str]) -> tuple[float, float] | None:
    """The one real point of a zero set that *is* a single point, solved exactly - not sampled.

    A positive-definite form such as ``x*x/4 + y*y/8`` vanishes at the origin and nowhere else, and
    no cell edge in a sampling grid ever changes sign there, so marching squares reports nothing.
    Sampling cannot fix that: whether the tracer sees the point at all would depend on whether the
    grid happens to land on it, which is not a property of the curve. So this case is not sampled.
    :func:`classify` has already named it - ``degenerate conic: a single point`` - and for a conic
    that point is the centre, the simultaneous zero of the two partial derivatives
    ``2*A*x + B*y + D`` and ``B*x + 2*C*y + E``, which is one exact linear solve.

    ``None`` for anything that is not that case, so the caller falls back to the contour tracer.
    """
    record = classify(expression, variables)
    if record["label"] != "degenerate conic: a single point":
        return None
    coefficients = {key: sympify(value) for key, value in record["conic_coefficients"].items()}
    x, y = curve_symbols(variables)
    solution = linsolve(
        [
            2 * coefficients["A"] * x + coefficients["B"] * y + coefficients["D"],
            coefficients["B"] * x + 2 * coefficients["C"] * y + coefficients["E"],
        ],
        [x, y],
    )
    if not solution:
        return None
    centre = next(iter(solution))
    if any(value.free_symbols for value in centre):
        return None  # a symbolic centre is not a point that can be drawn
    return (float(centre[0]), float(centre[1]))


def _panel(
    item: dict[str, Any],
    entry: dict[str, Any],
    origin: tuple[float, float],
    steps: int,
) -> tuple[str, dict[str, Any]]:
    """One reading, drawn and labelled. Returns the SVG fragment and a small provenance record."""
    left, top = origin
    xmin, xmax, ymin, ymax = entry["window"]
    plot_left, plot_top = left + PAD, top + HEADER
    scale_x = PLOT / (xmax - xmin)
    scale_y = PLOT / (ymax - ymin)

    def to_px(x: float, y: float) -> tuple[float, float]:
        return plot_left + (x - xmin) * scale_x, plot_top + (ymax - y) * scale_y

    parts: list[str] = []
    is_control = "G0" in item["grammars"]
    edge = CONTROL if is_control else PANEL_EDGE
    width = 2 if is_control else 1
    parts.append(
        f'<rect x="{_number(plot_left)}" y="{_number(plot_top)}" width="{PLOT}" height="{PLOT}" '
        f'fill="{PANEL_FILL}" stroke="{edge}" stroke-width="{width}"/>'
    )

    for tick in range(int(xmin), int(xmax) + 1, 2):
        px, _ = to_px(tick, 0)
        parts.append(
            f'<line x1="{_number(px)}" y1="{_number(plot_top)}" x2="{_number(px)}" '
            f'y2="{_number(plot_top + PLOT)}" stroke="{GRID}" stroke-width="1"/>'
        )
    for tick in range(int(ymin), int(ymax) + 1, 2):
        _, py = to_px(0, tick)
        parts.append(
            f'<line x1="{_number(plot_left)}" y1="{_number(py)}" x2="{_number(plot_left + PLOT)}" '
            f'y2="{_number(py)}" stroke="{GRID}" stroke-width="1"/>'
        )
    ax, ay = to_px(0, 0)
    parts.append(
        f'<line x1="{_number(plot_left)}" y1="{_number(ay)}" x2="{_number(plot_left + PLOT)}" '
        f'y2="{_number(ay)}" stroke="{AXIS}" stroke-width="1.2"/>'
    )
    parts.append(
        f'<line x1="{_number(ax)}" y1="{_number(plot_top)}" x2="{_number(ax)}" '
        f'y2="{_number(plot_top + PLOT)}" stroke="{AXIS}" stroke-width="1.2"/>'
    )

    provenance = {"object_id": item["object_id"], "segments": 0, "pole_segments": 0, "points": 0}

    denominator = item["drawn_denominator"]
    if str(denominator) != "1":
        pole_function = _plane_callable(denominator, entry["variables"])
        pole_segments = zero_set_segments(pole_function, tuple(entry["window"]), steps)
        provenance["pole_segments"] = len(pole_segments)
        path = " ".join(
            "M {} {} L {} {}".format(*(_number(value) for value in (*to_px(x1, y1), *to_px(x2, y2))))
            for x1, y1, x2, y2 in pole_segments
        )
        if path:
            parts.append(
                f'<path d="{path}" fill="none" stroke="{POLE}" stroke-width="1.4" '
                f'stroke-dasharray="5 4"/>'
            )

    # a zero set that is one point is solved, not traced; everything else is traced.
    point = single_point(item["drawn_numerator"], entry["variables"])
    if point is not None and xmin <= point[0] <= xmax and ymin <= point[1] <= ymax:
        provenance["points"] = 1
        px, py = to_px(*point)
        parts.append(
            f'<circle cx="{_number(px)}" cy="{_number(py)}" r="3.6" fill="{CURVE}" '
            f'stroke="{CURVE}" stroke-width="1"/>'
        )
        path = ""
    else:
        curve_function = _plane_callable(item["drawn_numerator"], entry["variables"])
        segments = zero_set_segments(curve_function, tuple(entry["window"]), steps)
        provenance["segments"] = len(segments)
        path = " ".join(
            "M {} {} L {} {}".format(*(_number(value) for value in (*to_px(x1, y1), *to_px(x2, y2))))
            for x1, y1, x2, y2 in segments
        )
        if path:
            parts.append(
                f'<path d="{path}" fill="none" stroke="{CURVE}" stroke-width="2.1" '
                f'stroke-linecap="round"/>'
            )
    if not path and not provenance["points"]:
        parts.append(
            f'<text x="{_number(plot_left + PLOT / 2)}" y="{_number(plot_top + PLOT / 2)}" '
            f'text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12" '
            f'fill="{MUTED}">no real points in this window</text>'
        )

    badge = " [G0]" if is_control else ""
    heading = f'{item["object_id"]}{badge}  {item["grammar_count"]} of {entry["grammar_count"]} worlds'
    parts.append(
        f'<text x="{_number(left + PAD)}" y="{_number(top + 16)}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="bold" '
        f'fill="{CONTROL if is_control else TEXT}">{_escape(_fit(heading, PLOT, 12))}</text>'
    )
    parts.append(
        f'<text x="{_number(left + PAD)}" y="{_number(top + 32)}" '
        f'font-family="Helvetica, Arial, sans-serif" font-size="12" fill="{TEXT}">'
        f'{_escape(_fit(item["resolved_label"], PLOT, 12))}</text>'
    )
    parts.append(
        f'<text x="{_number(left + PAD)}" y="{_number(top + 47)}" '
        f'font-family="Consolas, Menlo, monospace" font-size="10.5" fill="{MUTED}">'
        f'{_escape(_fit(item["canonical"], PLOT, 10.5, mono=True))}</text>'
    )
    parts.append(
        f'<text x="{_number(left + PAD)}" y="{_number(plot_top + PLOT + 15)}" '
        f'font-family="Consolas, Menlo, monospace" font-size="10" fill="{MUTED}">'
        f'{_escape(_fit(", ".join(item["grammars"]), PLOT, 10, mono=True))}</text>'
    )
    tail = f'0 = {item["numerator"]}'
    if item["denominator_punctures"]:
        tail += f'  /  {item["denominator"]}'
    parts.append(
        f'<text x="{_number(left + PAD)}" y="{_number(plot_top + PLOT + 26)}" '
        f'font-family="Consolas, Menlo, monospace" font-size="10" fill="{MUTED}">'
        f'{_escape(_fit(tail, PLOT, 10, mono=True))}</text>'
    )
    return "\n".join(parts), provenance


def curve_figure(entry: dict[str, Any], steps: int = GRID_STEPS) -> tuple[str, dict[str, Any]]:
    """One SVG holding every distinct reading of one catalogue curve, side by side."""
    objects = entry["objects"]
    columns = min(len(objects), 4)
    rows = (len(objects) + columns - 1) // columns
    xmin, xmax, ymin, ymax = entry["window"]
    parameters = ", ".join(f"{name} = {value}" for name, value in entry["parameters"].items())
    drawn = f"drawn at {parameters}" if parameters else "no free parameters"

    # every line of running text, with the font it is set in, so the width can be chosen to hold
    # the longest of them; nothing is allowed to escape the viewBox.
    title = f'{entry["name"]} in the {entry["grammar_count"]} worlds'
    form = f'0 = {entry["written_form"]}   [{", ".join(entry["variables"])}]'
    subtitle = (
        f'{entry["distinct_object_count"]} distinct objects, '
        f'{entry["distinct_label_count"]} distinct classifications; '
        f'here it is {entry["control_label"]} in {entry["control_group_size"]} of '
        f'{entry["grammar_count"]} worlds'
    )
    window_note = (
        f"window [{_number(xmin)}, {_number(xmax)}] x [{_number(ymin)}, {_number(ymax)}], {drawn}; "
        f"solid = the curve, dashed = the denominator that was set aside"
    )
    footer_one = (
        "ParseAtlas experiment 0040. The blue border marks the world we live in (G0). "
        "Long expressions are truncated here; the report carries them in full."
    )
    footer_two = (
        "Regenerate: python -m parseatlas.geometry_atlas figures "
        "experiments/0040_geometry_atlas/figures"
    )
    lines = (
        (title, 19, False),
        (form, 13, True),
        (subtitle, 12.5, False),
        (window_note, 11.5, False),
        (footer_one, 11, False),
        (footer_two, 11, False),
    )
    width = int(
        max(
            2 * MARGIN + columns * CELL_W,
            max(2 * MARGIN + _text_width(text, size, mono) for text, size, mono in lines),
        )
        + 0.999
    )
    height = 2 * MARGIN + TITLE_H + rows * CELL_H + NOTE_H

    parts: list[str] = []
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{BACKGROUND}"/>')
    parts.append(
        f'<text x="{MARGIN}" y="{MARGIN + 22}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="19" font-weight="bold" fill="{TEXT}">{_escape(title)}</text>'
    )
    parts.append(
        f'<text x="{MARGIN}" y="{MARGIN + 43}" font-family="Consolas, Menlo, monospace" '
        f'font-size="13" fill="{TEXT}">{_escape(form)}</text>'
    )
    parts.append(
        f'<text x="{MARGIN}" y="{MARGIN + 62}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="12.5" fill="{TEXT}">{_escape(subtitle)}</text>'
    )
    parts.append(
        f'<text x="{MARGIN}" y="{MARGIN + 80}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="11.5" fill="{MUTED}">{_escape(window_note)}</text>'
    )

    provenance = []
    for index, item in enumerate(objects):
        column, row = index % columns, index // columns
        origin = (MARGIN + column * CELL_W, MARGIN + TITLE_H + row * CELL_H)
        fragment, record = _panel(item, entry, origin, steps)
        parts.append(fragment)
        provenance.append(record)

    footer_y = MARGIN + TITLE_H + rows * CELL_H + 18
    parts.append(
        f'<text x="{MARGIN}" y="{_number(footer_y)}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="11" fill="{MUTED}">{_escape(footer_one)}</text>'
    )
    parts.append(
        f'<text x="{MARGIN}" y="{_number(footer_y + 16)}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="11" fill="{MUTED}">{_escape(footer_two)}</text>'
    )

    body = "\n".join(parts)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n{body}\n</svg>\n'
    )
    return svg, {
        "name": entry["name"],
        "width": width,
        "height": height,
        "panels": provenance,
        "object_count": len(objects),
    }


def write_figures(
    directory: str,
    atlas_result: dict[str, Any] | None = None,
    steps: int = GRID_STEPS,
    workers: int | None = None,
) -> list[dict[str, Any]]:
    """Write one SVG per catalogue curve into ``directory`` and report what was written."""
    result = atlas_result or atlas(workers=workers)
    os.makedirs(directory, exist_ok=True)
    written = []
    for entry in result["entries"]:
        svg, record = curve_figure(entry, steps)
        path = os.path.join(directory, f'{entry["name"]}.svg')
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(svg)
        record["path"] = path
        record["bytes"] = len(svg.encode("utf-8"))
        written.append(record)
    return written


# ---------------------------------------------------------------------------------- measurement


def _comparable(result: dict[str, Any]) -> list[Any]:
    """Everything the atlas asserts, with the timing fields - which are not results - removed."""
    return [
        [
            entry["name"],
            entry["distinct_object_count"],
            [
                [
                    item["object_id"],
                    item["canonical"],
                    item["excluded_points"],
                    item["resolved_label"],
                    item["total_degree"],
                    item["has_cross_term"],
                    item["grammars"],
                ]
                for item in entry["objects"]
            ],
        ]
        for entry in result["entries"]
    ]


def parallelism_measurement(
    catalogue: Sequence[StandardCurve] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Time the sequential and pooled paths on this host and check they produce the same atlas.

    Repository policy is multicore by default *with a measured decision*. This is the measurement.
    ``identical_results`` is a comparison of the two atlases, not an assumption about them.
    """
    catalogue = tuple(catalogue or CURVE_CATALOGUE)
    grammars = tuple(grammars or all_grammars())
    started = time.perf_counter()
    sequential = atlas(catalogue, grammars, workers=1)
    sequential_seconds = time.perf_counter() - started
    resolved = resolve_worker_count(len(catalogue) * len(grammars), workers)
    started = time.perf_counter()
    parallel = atlas(catalogue, grammars, workers=resolved)
    parallel_seconds = time.perf_counter() - started
    return {
        "item_count": len(catalogue) * len(grammars),
        "cpu_count": os.cpu_count(),
        "automatic_worker_count": resolve_worker_count(len(catalogue) * len(grammars)),
        "workers": resolved,
        "sequential_seconds": sequential_seconds,
        "parallel_seconds": parallel_seconds,
        "speedup": sequential_seconds / parallel_seconds if parallel_seconds else None,
        "faster_path": "parallel" if parallel_seconds < sequential_seconds else "sequential",
        "identical_results": _comparable(sequential) == _comparable(parallel),
    }


def headline_report(workers: int | None = None) -> dict[str, Any]:
    """The five headline questions, each answered with a number from this run."""
    result = atlas(workers=workers)
    survival = survival_report(atlas_result=result)
    entries = {entry["name"]: entry for entry in result["entries"]}
    circle, line = entries["circle"], entries["line"]
    non_line = [item for item in line["objects"] if item["resolved_label"] != "line"]
    return {
        "atlas": result,
        "survival": survival,
        "q1_circle": {
            "distinct_objects": circle["distinct_object_count"],
            "control_group_size": circle["control_group_size"],
            "control_label": circle["control_label"],
            "labels": {
                item["object_id"]: [item["resolved_label"], item["grammar_count"]]
                for item in circle["objects"]
            },
        },
        "q2_line": {
            "distinct_objects": line["distinct_object_count"],
            "still_a_line": line["control_group_size"],
            "not_a_line": sum(item["grammar_count"] for item in non_line),
            "dissenting_labels": {
                item["object_id"]: [item["resolved_label"], item["grammar_count"], item["has_cross_term"]]
                for item in non_line
            },
        },
        "q3_stability": {
            "most_stable": survival["ranked"][0]["name"],
            "most_stable_survivors": survival["ranked"][0]["surviving_grammar_count"],
            "least_stable": survival["least_stable"],
            "most_fractured": survival["most_fractured"],
            "maximum_distinct_objects": result["maximum_distinct_objects"],
        },
        "q4_invariant": survival["identical_in_every_world"],
        "q5_control": {
            "alone_on": survival["control_alone_on"],
            "group_sizes": survival["control_group_sizes"],
            "twins": [
                identifier
                for identifier, count in survival["control_twins"].items()
                if identifier != "G0" and count == result["entry_count"]
            ],
            "agreement": survival["control_twins"],
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    """``python -m parseatlas.geometry_atlas figures [directory]`` regenerates every figure."""
    import json
    import sys

    argv = list(argv if argv is not None else sys.argv[1:])
    command = argv[0] if argv else "headline"
    if command == "figures":
        directory = argv[1] if len(argv) > 1 else os.path.join(
            "experiments", "0040_geometry_atlas", "figures"
        )
        written = write_figures(directory)
        for record in written:
            print(f'{record["path"]}  {record["bytes"]} bytes  {record["object_count"]} panels')
        return 0
    if command == "headline":
        report = headline_report()
        report.pop("atlas")
        report["survival"] = {
            key: value for key, value in report["survival"].items() if key != "rows"
        }
        print(json.dumps(report, indent=2, default=str))
        return 0
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":  # pragma: no cover - exercised through the documented command
    raise SystemExit(main())
