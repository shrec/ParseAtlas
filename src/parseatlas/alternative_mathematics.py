"""The standard objects of mathematics in each of the 25 worlds.

Experiment 0035. This module answers the project's founding question directly.

Mathematicians write the simplest thing the notation lets them write. ``a*x*x + b*x + c`` is the
standard polynomial *because* it is cheap under the conventional precedence ``* /`` above ``+ -``.
Under a different convention the SAME written string denotes a DIFFERENT object, and that object -
not ours - is what that world's mathematicians would have factored, differentiated, named and built
on. So for every standard written form we can read off, per world, what the object actually is.

Nothing here reasons about what a grammar "should" do. Every field of every record is produced by
parsing the written form with :func:`parseatlas.parser.parse`, canonicalizing it with
:func:`parseatlas.canonical.canonicalize`, and extracting properties with
:mod:`parseatlas.properties`. Objects are compared on the project's own semantic key -
``(canonical expression, domain, excluded points)`` - the same triple
:func:`parseatlas.analyze.analyze_expression` and :func:`parseatlas.corpus_matrix.expression_classes`
use, so two worlds count as sharing an object only when they agree on all three, never on canonical
text alone. One disclosure about that key: :func:`parseatlas.canonical.canonicalize` writes the
literal string ``"R"`` into ``domain`` for every expression it ever produces, so the component that
actually discriminates is ``(canonical expression, excluded points)`` and ``domain`` is a fixed
declaration of the analysis setting rather than a measured field. The key is reused here exactly as
the project defines it; only the guarantee is stated at its true strength.

**Root convention: every root list in this module is the complete multiset of roots over C.**
This has to be said out loud because SymPy will silently do something else. The symbols
:func:`parseatlas.canonical.to_sympy` builds carry ``real=True``, and ``solve`` then returns only
the real roots whenever it can decide realness - which it can for numeric coefficients and cannot
for free symbolic ones. A textbook generated that way would print all three roots of
``a**3 + b**3`` and only one of the three roots of ``r**3 + r**2 + r + 1``, mixing two notions of
"root" inside a single page without saying so. Real-roots-only is not an available fix: with
symbolic coefficients the realness of a root is undecidable, so that convention cannot be applied
uniformly at all. So roots are solved over C: :func:`solving_symbol` strips the realness assumption
before solving, :func:`root_list_is_complete` checks the printed multiplicities against the degree,
and every printed root list carries ``root_domain`` and ``roots_complete`` alongside it.
:func:`requires_radical` counts ``I`` for the same reason it counts ``sqrt(2)`` - ``I`` is the
square root of ``-1``, and a world whose pages print it has left the rationals by taking a root.

Real-line statements are kept separate and named for it. :func:`function_profile` (parity,
boundedness, growth, periodicity, real poles) and the ``real_zeros`` / ``real_poles`` /
``real_removable_restrictions`` fields describe the reading as a function of a real variable, which
is a different question from where its roots live and is labelled as such wherever it appears.

A note that the module refuses to fudge: **a truncated series is a polynomial, and a polynomial is
not periodic - in every world, ours included.** :func:`function_profile` measures periodicity with
:func:`sympy.calculus.util.periodicity` and reports the raw answer. SymPy calls a constant function
periodic with period ``0``; a period of ``0`` is recorded but is NOT reported as periodic, because a
constant is degenerate rather than oscillating. The conventional reading of
``x - x*x*x/6 + x*x*x*x*x/120`` is a quintic. It is odd, it is unbounded, and it has no period. That
is the honest statement, and it is the same statement in G0 as anywhere else.
"""

import os
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sympy import (
    Dummy,
    Poly,
    Pow,
    Symbol,
    cancel,
    diff,
    expand,
    factor,
    fraction,
    limit,
    oo,
    preorder_traversal,
    roots,
    simplify,
    solve,
    together,
)
from sympy.calculus.util import periodicity
from sympy.core.numbers import ImaginaryUnit
from sympy.polys.polyerrors import PolynomialError
from sympy.polys.rootoftools import CRootOf

from .canonical import canonicalize
from .grammar import Grammar, all_grammars
from .parser import parse
from .properties import polynomial_properties, rational_properties


@dataclass(frozen=True)
class StandardForm:
    """One standard written form of mathematics, plus the variable a textbook would solve for."""

    name: str
    area: str
    source: str
    variable: str
    series: bool = False


#: The forms mathematics actually writes. Hand-chosen - see the limits section of the report.
#: ``series=True`` marks a truncated power series, where the interesting question is what FUNCTION
#: each world's reading is rather than what its roots are.
STANDARD_CATALOGUE: tuple[StandardForm, ...] = (
    StandardForm("linear", "algebra", "a*x + b", "x"),
    StandardForm("quadratic_standard", "algebra", "a*x*x + b*x + c", "x"),
    StandardForm("cubic_standard", "algebra", "a*x*x*x + b*x*x + c*x + d", "x"),
    StandardForm("monic_quadratic", "algebra", "x*x + b*x + c", "x"),
    StandardForm("vertex_form", "algebra", "a*(x - h)*(x - h) + k", "x"),
    StandardForm("difference_of_squares", "algebra", "a*a - b*b", "a"),
    StandardForm("binomial_square", "algebra", "a*a + 2*a*b + b*b", "a"),
    StandardForm("sum_of_cubes", "algebra", "a*a*a + b*b*b", "a"),
    StandardForm("distributive_law", "algebra", "a*(b + c)", "a"),
    StandardForm("linear_combination", "algebra", "a*x + b*y", "x"),
    StandardForm("pythagorean_form", "geometry", "a*a + b*b - c*c", "a"),
    StandardForm("law_of_cosines_form", "geometry", "a*a + b*b - 2*a*b*c", "a"),
    StandardForm("circle_form", "geometry", "x*x + y*y - r*r", "x"),
    StandardForm("slope_form", "geometry", "y - w/x - v", "x"),
    StandardForm("triangle_area", "geometry", "b*h/2", "b"),
    StandardForm("sine_series", "analysis", "x - x*x*x/6 + x*x*x*x*x/120", "x", series=True),
    StandardForm("cosine_series", "analysis", "1 - x*x/2 + x*x*x*x/24", "x", series=True),
    StandardForm("exponential_series", "analysis", "1 + x + x*x/2 + x*x*x/6", "x", series=True),
    StandardForm("geometric_sum", "analysis", "1 + r + r*r + r*r*r", "r", series=True),
    StandardForm("mean_of_two", "arithmetic", "a + b/2", "a"),
    StandardForm("mean_of_three", "arithmetic", "a + b + c/3", "a"),
    StandardForm("arithmetic_progression", "arithmetic", "a + n*d", "n"),
    StandardForm("compound_interest", "arithmetic", "p*r*t/100", "p"),
    StandardForm("fahrenheit_form", "arithmetic", "9*c/5 + 32", "c"),
    StandardForm("harmonic_form", "arithmetic", "1/a + 1/b", "a"),
    StandardForm("rate_form", "arithmetic", "d/t", "d"),
)

#: Below this many work items the automatic worker choice stays sequential: on the spawn start
#: method a process pays its whole SymPy import before it does any work. The threshold is a policy
#: floor, not the decision - :func:`parallelism_measurement` measures the real one.
PARALLEL_MINIMUM_ITEMS: int = 16


# ------------------------------------------------------------------------------ symbolic helpers


#: The domain every root list in this module is solved over. Stated as data so that the pages, the
#: solution records and the report all quote one value rather than three independent sentences.
ROOT_DOMAIN: str = "C"

#: The one-line statement of the convention, printed wherever a root list is rendered.
ROOT_CONVENTION_NOTE: str = (
    "Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical."
)


def principal_symbol(name: str) -> Symbol:
    """The symbol :func:`parseatlas.canonical.to_sympy` builds, so assumptions match exactly.

    ``real=True``, which is what makes it the right symbol for matching a canonical expression and
    for the real-line questions in :func:`function_profile`, and the wrong symbol for solving - see
    :func:`solving_symbol` and the module docstring.
    """
    return Symbol(name, real=True)


def solving_symbol(name: str) -> Dummy:
    """The same variable with the realness assumption stripped, so ``solve`` answers over C.

    With ``real=True`` SymPy returns only the real roots whenever it can decide realness, which
    silently makes "roots" mean one thing for numeric coefficients and another for symbolic ones.
    Substituting this symbol first is what makes :data:`ROOT_DOMAIN` true of every root list here.
    """
    return Dummy(name)


def semantic_key(canonical: dict[str, Any]) -> tuple[str, str, tuple[str, ...]]:
    """The project's semantic identity: canonical form, domain and excluded points together.

    ``domain`` is part of the project's triple but is not a measured component:
    :func:`parseatlas.canonical.canonicalize` sets it to ``"R"`` for every expression, so the
    operative discrimination is ``(canonical form, excluded points)``.
    """
    return (canonical["expression"], canonical["domain"], tuple(canonical["excluded_points"]))


def requires_radical(expressions: Sequence[Any]) -> bool:
    """True when writing these expressions needs more than the field operations on the coefficients.

    ``1/a`` is ``Pow(a, -1)`` and does NOT count; ``sqrt(b**2 - 4*a*c)`` is ``Pow(..., 1/2)`` and
    does. A :class:`~sympy.polys.rootoftools.CRootOf` counts too - it is a root that has no radical
    expression at all, which is a stronger form of the same answer. ``I`` counts for exactly the
    same reason ``sqrt(2)`` does: it *is* a square root, the one a world has to adjoin to write down
    a complex root at all. Under the module's over-C root convention this is what keeps the flag
    honest - dropping the complex roots is what used to make pages read ``radical: no``.
    """
    for expression in expressions:
        for node in preorder_traversal(expression):
            if isinstance(node, (CRootOf, ImaginaryUnit)):
                return True
            if isinstance(node, Pow) and not node.exp.is_Integer:
                return True
    return False


def root_list_is_complete(
    degree: int | None, roots_with_multiplicity: Sequence[dict[str, Any]]
) -> bool | None:
    """Do the multiplicities of the roots this module PRINTS add up to the degree?

    The comparison is deliberately against the reported list and not against SymPy's internal root
    table: a check against the internal table answers ``True`` in precisely the cases where the
    printed list is short, which is the failure it is supposed to detect.

    ``None`` means the question does not apply - a rational reading, or the zero reading, has no
    polynomial degree to account for. It is never silently reported as complete.
    """
    if degree is None:
        return None
    return sum(int(item["multiplicity"]) for item in roots_with_multiplicity) == degree


def _polynomial_degree(expression: Any, variable: Symbol) -> int | None:
    """Degree in ``variable``, or ``None`` when the reading is not a polynomial in it.

    The zero reading is the awkward case and it really occurs: several worlds read the truncated
    sine series as ``0``. SymPy 1.14 gives ``Poly(0, x).degree()`` the value ``-oo``, which
    :func:`parseatlas.properties.polynomial_properties` cannot convert to ``int``, so the degree is
    resolved here first and the zero polynomial is reported with degree ``None``.
    """
    try:
        degree = Poly(expression, variable).degree()
    except (TypeError, ValueError, PolynomialError):
        return None
    return int(degree) if isinstance(degree, int) else None  # the zero poly answers ``-oo`` here


def _polynomial_properties(expression: Any, variable: Symbol) -> dict[str, Any]:
    """:func:`parseatlas.properties.polynomial_properties`, guarded against the zero polynomial."""
    if _polynomial_degree(expression, variable) is None:
        try:
            Poly(expression, variable)
        except (TypeError, ValueError, PolynomialError):
            return {"is_polynomial": False}
        return {"is_polynomial": True, "degree": None, "coefficients": ["0"], "factorized": "0", "roots": []}
    return polynomial_properties(expression, variable)


def _solve_over_complexes(expression: Any, variable: Symbol) -> list[Any]:
    """``solve`` with the realness assumption stripped, so the answer is the full complex set.

    The substituted symbol is a :class:`~sympy.core.symbol.Dummy`, whose printed name is not the
    variable the reader knows, so any answer that still mentions it is dropped rather than printed:
    a root expressed in terms of the unknown is not a root a textbook page can state.
    """
    unconstrained = solving_symbol(variable.name)
    try:
        solved = solve(expression.subs(variable, unconstrained), unconstrained)
    except (TypeError, ValueError, NotImplementedError, PolynomialError):
        return []
    if not isinstance(solved, list):
        return []
    return [
        value
        for value in solved
        if not isinstance(value, dict) and unconstrained not in getattr(value, "free_symbols", set())
    ]


def _root_multiset(expression: Any, variable: Symbol) -> dict[str, Any]:
    """Roots over C in a deterministic order, with multiplicity where SymPy can supply it.

    ``roots_complete`` compares the multiplicities of the list built here - the one the pages print -
    against the degree, so a short list is detected rather than papered over.
    """
    ordered = _solve_over_complexes(expression, variable)
    multiplicity: dict[str, int] = {}
    degree = _polynomial_degree(expression, variable)
    try:
        table = roots(Poly(expression, variable)) if degree is not None else {}
    except (TypeError, ValueError, PolynomialError, NotImplementedError):
        table = {}
    if table:
        multiplicity = {str(root): int(count) for root, count in table.items()}
    with_multiplicity = [
        {"root": str(value), "multiplicity": multiplicity.get(str(value), 1)} for value in ordered
    ]
    return {
        "root_domain": ROOT_DOMAIN,
        "roots": [str(value) for value in ordered],
        "roots_with_multiplicity": with_multiplicity,
        "root_multiplicity_sum": sum(item["multiplicity"] for item in with_multiplicity),
        "roots_complete": root_list_is_complete(degree, with_multiplicity),
        "requires_radical": requires_radical(ordered),
        "sympy_roots": ordered,
    }


def _critical_points(expression: Any, variable: Symbol) -> list[str]:
    """Stationary points over C, so they follow the same convention as the roots.

    :func:`parseatlas.properties.polynomial_properties` solves for these with the real symbol, which
    would put a second, unstated root convention into the same record.
    """
    derivative = diff(expression, variable)
    if derivative == 0:
        return []
    return [str(value) for value in _solve_over_complexes(derivative, variable)]


def function_profile(expression: Any, variable: Symbol) -> dict[str, Any]:
    """Measure parity, boundedness, growth and periodicity of a univariate reading.

    Returns ``{"univariate": False}`` when the reading still carries other free symbols, because
    none of these questions has a single answer there.
    """
    if expression.free_symbols - {variable}:
        return {"univariate": False}
    constant = not expression.free_symbols
    reflected = expression.subs(variable, -variable)
    odd = bool(simplify(reflected + expression) == 0)
    even = bool(simplify(reflected - expression) == 0)
    _, denominator = fraction(cancel(together(expression)))
    try:
        pole_values = solve(denominator, variable) if denominator.free_symbols else []
    except (TypeError, ValueError, NotImplementedError):
        pole_values = []
    real_poles = [str(value) for value in pole_values if value.is_real]
    try:
        toward_plus = limit(expression, variable, oo)
        toward_minus = limit(expression, variable, -oo)
        finite_limits = bool(toward_plus.is_finite) and bool(toward_minus.is_finite)
    except (TypeError, ValueError, NotImplementedError):
        toward_plus = toward_minus = None
        finite_limits = False
    try:
        period = periodicity(expression, variable)
    except (TypeError, ValueError, NotImplementedError, PolynomialError):
        period = None
    return {
        "univariate": True,
        "constant": constant,
        # the zero reading really is both odd and even, and several worlds produce it, so the label
        # records that instead of silently preferring one of the two.
        "odd": odd,
        "even": even,
        "parity": "odd and even" if odd and even else "odd" if odd else "even" if even else "neither",
        "limit_at_plus_infinity": str(toward_plus),
        "limit_at_minus_infinity": str(toward_minus),
        "real_poles": real_poles,
        "bounded": bool(finite_limits and not real_poles),
        # SymPy calls a constant periodic with period 0; that is degeneracy, not oscillation, so a
        # zero period is recorded but never reported as periodic.
        "period": None if period is None else str(period),
        "periodic": bool(period is not None and period != 0),
    }


# -------------------------------------------------------------------------------- world objects


def world_object(source: str, grammar: Grammar, variable: str = "x") -> dict[str, Any]:
    """Everything a textbook of ``grammar``'s world would state about the form ``source``.

    Property extraction is delegated to :mod:`parseatlas.properties`; this function only chooses the
    principal variable, adds the expanded/factored pair, roots with multiplicity, and - for a
    univariate reading - the analytic profile.

    Two conventions meet in one record and both are named in it. ``roots``,
    ``roots_with_multiplicity``, ``critical_points`` and ``requires_radical`` are over
    :data:`ROOT_DOMAIN`, i.e. C. ``real_zeros``, ``real_poles``, ``real_removable_restrictions`` and
    everything under ``profile`` are statements about the reading as a function of a real variable.
    """
    node = parse(source, grammar)
    canonical = canonicalize(node)
    symbolic = canonical["sympy_expression"]
    symbol = principal_symbol(variable)
    polynomial = _polynomial_properties(symbolic, symbol)
    rational = rational_properties(canonical["raw_sympy_expression"], symbol)
    multiset = _root_multiset(symbolic, symbol)
    degree = polynomial.get("degree") if polynomial.get("is_polynomial") else None
    record: dict[str, Any] = {
        "source": source,
        "grammar_id": grammar.id,
        "precedence": [list(level) for level in grammar.levels],
        "variable": variable,
        "canonical": canonical["expression"],
        "domain": canonical["domain"],
        "excluded_points": list(canonical["excluded_points"]),
        "semantic_key": semantic_key(canonical),
        "expanded": str(expand(symbolic)),
        "factored": str(factor(symbolic)),
        "free_symbols": sorted(str(item) for item in symbolic.free_symbols),
        "is_polynomial": bool(polynomial.get("is_polynomial")),
        "is_rational": bool(rational.get("is_rational")),
        "degree": degree,
        "coefficients": polynomial.get("coefficients"),
        "root_domain": multiset["root_domain"],
        "roots": multiset["roots"],
        "roots_with_multiplicity": multiset["roots_with_multiplicity"],
        "root_count": len(multiset["roots"]),
        "root_multiplicity_sum": multiset["root_multiplicity_sum"],
        "roots_complete": multiset["roots_complete"],
        "requires_radical": multiset["requires_radical"],
        "discriminant": polynomial.get("discriminant"),
        "vertex": polynomial.get("vertex"),
        "critical_points": _critical_points(symbolic, symbol) if polynomial.get("is_polynomial") else None,
        # named for their convention: these three come from ``rational_properties``, which solves
        # with the real symbol, and they are the real-line reading rather than the over-C one.
        "real_zeros": rational.get("zeros"),
        "real_poles": rational.get("poles"),
        "real_removable_restrictions": rational.get("removable_restrictions"),
        "profile": function_profile(symbolic, symbol),
    }
    return record


def _solution_method(
    degree: int | None,
    radical: bool,
    root_count: int,
    polynomial: bool,
    complete: bool | None = True,
    multiplicity_sum: int = 0,
) -> str:
    """Name the procedure from measured facts only - never from what the form is called.

    An incomplete root list gets its own label rather than one of the confident ones: saying that
    ``n`` roots are read off a factorisation is a false statement about a list that is short of the
    degree, and that is exactly the sentence this module used to print.
    """
    if not polynomial:
        return "rational over C: solve the numerator, then discard the poles"
    if degree is None or degree == 0:
        return "no equation to solve: the reading carries no power of the variable"
    if complete is False:
        return (
            f"degree {degree}: INCOMPLETE - the reported roots account for {multiplicity_sum} "
            f"of {degree} with multiplicity"
        )
    if degree == 1:
        return "one linear step"
    if degree == 2 and radical:
        return "quadratic formula: discriminant, then a square root"
    if degree == 2:
        return "degree 2, radical-free: the roots are already rational in the coefficients"
    if radical:
        return f"degree {degree}: a radical or an unsolvable root object is required"
    return (
        f"degree {degree}: {root_count} distinct roots over C, multiplicities summing to "
        f"{degree}, read straight off the factorisation, no radical"
    )


def solution_formula(source: str, grammar: Grammar, variable: str = "x") -> dict[str, Any]:
    """How ``grammar``'s world would solve ``source = 0`` for ``variable``.

    This is the direct answer to "how would the quadratic equation be solved there": the root
    expressions, whether a radical is needed at all, whether a discriminant exists, and how many
    roots there are.

    ``root_domain`` is carried in the record and ``root_convention`` spells it out, because the
    answer to "what are the roots" is only meaningful once the domain they are solved over is on the
    page next to them. ``roots_complete`` says whether the printed multiplicities reach the degree.
    """
    obj = world_object(source, grammar, variable)
    degree = obj["degree"]
    has_discriminant = obj["is_polynomial"] and degree == 2
    return {
        "source": source,
        "grammar_id": grammar.id,
        "variable": variable,
        "denotes": obj["canonical"],
        "equation": f"{obj['canonical']} = 0",
        "degree": degree,
        "root_domain": obj["root_domain"],
        "root_convention": ROOT_CONVENTION_NOTE,
        "roots": obj["roots"],
        "roots_with_multiplicity": obj["roots_with_multiplicity"],
        "root_count": obj["root_count"],
        "root_multiplicity_sum": obj["root_multiplicity_sum"],
        "roots_complete": obj["roots_complete"],
        "requires_radical": obj["requires_radical"],
        "has_discriminant": has_discriminant,
        "discriminant": obj["discriminant"] if has_discriminant else None,
        "excluded_points": obj["excluded_points"],
        "method": _solution_method(
            degree,
            obj["requires_radical"],
            obj["root_count"],
            obj["is_polynomial"],
            obj["roots_complete"],
            obj["root_multiplicity_sum"],
        ),
    }


def world_keys(
    source: str, grammars: Sequence[Grammar] | None = None
) -> dict[str, tuple[str, str, tuple[str, ...]]]:
    """Every world's semantic key for one written form, without any property extraction.

    This is the cheap identity-only pass. It exists so the claim that the key is
    ``(canonical, domain, excluded points)`` and NOT canonical text can be checked directly.
    """
    grammars = tuple(grammars or all_grammars())
    return {grammar.id: semantic_key(canonicalize(parse(source, grammar))) for grammar in grammars}


def reading_profiles(
    source: str, grammars: Sequence[Grammar] | None = None, variable: str = "x"
) -> dict[str, dict[str, Any]]:
    """Every world's analytic profile for one written form, without solving for roots.

    Same :func:`function_profile` the atlas uses; it just skips the expensive root work, which is
    what makes a whole-catalogue periodicity check affordable.
    """
    grammars = tuple(grammars or all_grammars())
    symbol = principal_symbol(variable)
    return {
        grammar.id: function_profile(canonicalize(parse(source, grammar))["sympy_expression"], symbol)
        for grammar in grammars
    }


# --------------------------------------------------------------------------------------- atlas


def _entry_atlas(payload: tuple[StandardForm, tuple[Grammar, ...]]) -> dict[str, Any]:
    """One catalogue entry across every world, grammars collapsed onto the semantic key.

    Module level and picklable on purpose: this is the unit of work the process pool distributes.
    """
    entry, grammars = payload
    groups: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}
    order: list[tuple[str, str, tuple[str, ...]]] = []
    for grammar in grammars:
        record = world_object(entry.source, grammar, entry.variable)
        key = record["semantic_key"]
        if key not in groups:
            solution = solution_formula(entry.source, grammar, entry.variable)
            groups[key] = {
                "canonical": key[0],
                "domain": key[1],
                "excluded_points": list(key[2]),
                "expanded": record["expanded"],
                "factored": record["factored"],
                "degree": record["degree"],
                "is_polynomial": record["is_polynomial"],
                "is_rational": record["is_rational"],
                "root_domain": record["root_domain"],
                "roots": record["roots"],
                "roots_with_multiplicity": record["roots_with_multiplicity"],
                "root_count": record["root_count"],
                "roots_complete": record["roots_complete"],
                "requires_radical": record["requires_radical"],
                "discriminant": record["discriminant"],
                "vertex": record["vertex"],
                "profile": record["profile"],
                "solution": solution,
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
    texts = {item["canonical"] for item in objects}
    return {
        "name": entry.name,
        "area": entry.area,
        "written_form": entry.source,
        "variable": entry.variable,
        "series": entry.series,
        "grammar_count": len(grammars),
        "distinct_object_count": len(objects),
        # how much work the (domain, excluded points) half of the semantic key does here: objects
        # that share canonical TEXT but are different functions because their domains differ.
        "canonical_text_count": len(texts),
        "restriction_split_objects": len(objects) - len(texts),
        "objects": objects,
        "control_object_id": control["object_id"] if control else None,
        "control_group_size": control["grammar_count"] if control else 0,
        "control_grammars": list(control["grammars"]) if control else [],
        "radical_grammar_count": sum(
            item["grammar_count"] for item in objects if item["requires_radical"]
        ),
        # the REJECT-1 detector, aggregated: how many worlds would be handed a root list whose
        # multiplicities do not reach the degree. It is expected to be 0 and is reported, not assumed.
        "incomplete_root_grammar_count": sum(
            item["grammar_count"] for item in objects if item["roots_complete"] is False
        ),
    }


def resolve_worker_count(item_count: int, workers: int | None = None) -> int:
    """Derive the process count from the observed cores, never from a hardcoded constant."""
    if workers is not None:
        return max(1, min(int(workers), max(item_count, 1)))
    if item_count < PARALLEL_MINIMUM_ITEMS:
        return 1
    cores = os.cpu_count() or 1
    return max(1, min(cores - 1, item_count))  # one core of headroom for the interactive session


def world_atlas(
    catalogue: Sequence[StandardForm] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The whole cross product, with worlds that denote the SAME object collapsed into one entry.

    Catalogue entries are independent and every one of them is CPU-bound SymPy work, so the entries
    are the parallel unit. Parallelism changes only how fast the atlas is measured: the
    ``workers=1`` path and the pool path produce byte-identical records, which
    :func:`parallelism_measurement` checks rather than assumes.
    """
    catalogue = tuple(catalogue or STANDARD_CATALOGUE)
    grammars = tuple(grammars or all_grammars())
    payloads = [(entry, grammars) for entry in catalogue]
    worker_count = resolve_worker_count(len(payloads), workers)
    started = time.perf_counter()
    if worker_count <= 1 or not payloads:
        entries = [_entry_atlas(payload) for payload in payloads]
    else:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            entries = list(pool.map(_entry_atlas, payloads, chunksize=1))
    counts = [entry["distinct_object_count"] for entry in entries]
    return {
        "entries": entries,
        "entry_count": len(entries),
        "root_domain": ROOT_DOMAIN,
        "incomplete_root_page_count": sum(entry["incomplete_root_grammar_count"] for entry in entries),
        "grammar_count": len(grammars),
        "grammar_ids": [grammar.id for grammar in grammars],
        "distinct_object_counts": {entry["name"]: entry["distinct_object_count"] for entry in entries},
        "total_distinct_objects": sum(counts),
        "maximum_distinct_objects": max(counts) if counts else 0,
        "invariant_entry_count": sum(1 for value in counts if value == 1),
        "restriction_split_objects": sum(entry["restriction_split_objects"] for entry in entries),
        "workers": worker_count,
        "wall_clock_seconds": time.perf_counter() - started,
        "cpu_count": os.cpu_count(),
    }


# ------------------------------------------------------------------------------------ textbook


def textbook(grammar: Grammar, catalogue: Sequence[StandardForm] | None = None) -> dict[str, Any]:
    """One world's page set: for every standard form, what it denotes here and how it is solved.

    Every page states the convention its root list is under (``root_domain``, and the book-level
    ``root_convention``) and whether that list reaches the degree (``roots_complete``).
    ``incomplete_root_page_count`` is the book-level count of pages that do not; it is reported so
    that a silent regression to a mixed convention shows up as a number rather than as prose.
    """
    catalogue = tuple(catalogue or STANDARD_CATALOGUE)
    pages = []
    for entry in catalogue:
        record = world_object(entry.source, grammar, entry.variable)
        pages.append(
            {
                "name": entry.name,
                "area": entry.area,
                "series": entry.series,
                "written_form": entry.source,
                "variable": entry.variable,
                "denotes": record["canonical"],
                "expanded": record["expanded"],
                "factored": record["factored"],
                "degree": record["degree"],
                "is_polynomial": record["is_polynomial"],
                "is_rational": record["is_rational"],
                "excluded_points": record["excluded_points"],
                "root_domain": record["root_domain"],
                "roots": record["roots"],
                "roots_with_multiplicity": record["roots_with_multiplicity"],
                "root_multiplicity_sum": record["root_multiplicity_sum"],
                "roots_complete": record["roots_complete"],
                "requires_radical": record["requires_radical"],
                "discriminant": record["discriminant"],
                "vertex": record["vertex"],
                "profile": record["profile"],
                "solution": solution_formula(entry.source, grammar, entry.variable),
            }
        )
    return {
        "grammar_id": grammar.id,
        "precedence": [list(level) for level in grammar.levels],
        "precedence_text": " > ".join("=".join(level) for level in grammar.levels),
        "entry_count": len(pages),
        "pages": pages,
        "root_domain": ROOT_DOMAIN,
        "root_convention": ROOT_CONVENTION_NOTE,
        "radical_page_count": sum(1 for page in pages if page["requires_radical"]),
        "polynomial_page_count": sum(1 for page in pages if page["is_polynomial"]),
        "incomplete_root_page_count": sum(1 for page in pages if page["roots_complete"] is False),
    }


def render_textbook(book: dict[str, Any], root_width: int = 80) -> str:
    """Render one world's textbook as a Markdown table, for the experiment report.

    ``root_width`` only elides the printed root column - the general cubic formula runs to some
    `1500` characters and would make the table unreadable. An elided cell states the root count and
    says it is elided, so nothing is silently dropped.

    The convention line under the heading is not decoration: a root column and a ``radical`` column
    mean different things over R and over C, so the table says which one it is every time it is
    printed. A row whose printed multiplicities fall short of the degree is marked in place.
    """
    lines = [
        f"### World `{book['grammar_id']}` - precedence `{book['precedence_text']}`",
        "",
        book["root_convention"],
        "",
        "| standard form | denotes here | deg | roots over C | radical | how it is solved |",
        "|---|---|---|---|---|---|",
    ]
    for page in book["pages"]:
        roots_text = ", ".join(page["roots"])
        if not roots_text:
            cell = "none"
        elif len(roots_text) > root_width:
            cell = f"{len(page['roots'])} roots, {len(roots_text)} chars (elided)"
        else:
            cell = f"`{roots_text}`"
        if page["roots_complete"] is False:
            cell += f" **INCOMPLETE: {page['root_multiplicity_sum']}/{page['degree']}**"
        degree = "-" if page["degree"] is None else str(page["degree"])
        lines.append(
            f"| `{page['written_form']}` | `{page['denotes']}` | {degree} | "
            f"{cell} | {'yes' if page['requires_radical'] else 'no'} | {page['solution']['method']} |"
        )
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------------- divergence


def divergence_report(
    catalogue: Sequence[StandardForm] | None = None,
    grammars: Sequence[Grammar] | None = None,
    atlas: dict[str, Any] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Which standard objects are the same in every world, and which fracture.

    Both lists are reported explicitly. An entry with one distinct object is convention-independent
    on this catalogue; an entry with many is where the convention decided the mathematics.
    """
    atlas = atlas or world_atlas(catalogue, grammars, workers)
    entries = atlas["entries"]
    invariant = [entry["name"] for entry in entries if entry["distinct_object_count"] == 1]
    fractured = sorted(
        (
            {
                "name": entry["name"],
                "area": entry["area"],
                "written_form": entry["written_form"],
                "distinct_object_count": entry["distinct_object_count"],
            }
            for entry in entries
            if entry["distinct_object_count"] > 1
        ),
        key=lambda item: (-item["distinct_object_count"], item["name"]),
    )
    agreement = {grammar_id: 0 for grammar_id in atlas["grammar_ids"]}
    for entry in entries:
        for grammar_id in entry["control_grammars"]:
            agreement[grammar_id] += 1
    total = atlas["entry_count"]
    twins = [
        grammar_id
        for grammar_id, count in agreement.items()
        if count == total and grammar_id != "G0"
    ]
    # a worldview is a grammar's whole catalogue signature: which object it picks for every entry.
    signatures: dict[str, list[str]] = {grammar_id: [] for grammar_id in atlas["grammar_ids"]}
    for entry in entries:
        for item in entry["objects"]:
            for grammar_id in item["grammars"]:
                signatures[grammar_id].append(f"{entry['name']}:{item['object_id']}")
    worldviews: dict[tuple[str, ...], list[str]] = {}
    for grammar_id, signature in signatures.items():
        worldviews.setdefault(tuple(signature), []).append(grammar_id)
    return {
        "entry_count": total,
        "grammar_count": atlas["grammar_count"],
        "invariant_objects": invariant,
        "invariant_count": len(invariant),
        "fractured_objects": fractured,
        "fractured_count": len(fractured),
        "most_fractured": fractured[0] if fractured else None,
        "control_agreement": agreement,
        "control_group_sizes": {entry["name"]: entry["control_group_size"] for entry in entries},
        "control_grammars": {entry["name"]: list(entry["control_grammars"]) for entry in entries},
        "grammars_agreeing_with_control_everywhere": sorted(twins),
        "control_is_unique": not twins,
        "entries_where_control_is_alone": [
            entry["name"] for entry in entries if entry["control_group_size"] == 1
        ],
        "radical_grammar_counts": {entry["name"]: entry["radical_grammar_count"] for entry in entries},
        "distinct_worldviews": len(worldviews),
        "worldview_groups": sorted(
            (sorted(group) for group in worldviews.values()), key=lambda group: (-len(group), group[0])
        ),
    }


def series_report(atlas: dict[str, Any] | None = None, workers: int | None = None) -> dict[str, Any]:
    """What FUNCTION each world's reading of a truncated series actually is.

    The periodicity column exists to be reported honestly: a truncated series is a polynomial in
    every world, ours included, so no reading of it is periodic. A constant reading carries SymPy's
    period ``0``, which this module does not count as periodic.
    """
    atlas = atlas or world_atlas(workers=workers)
    entries = [entry for entry in atlas["entries"] if entry["series"]]
    readings = []
    for entry in entries:
        for item in entry["objects"]:
            profile = item["profile"]
            readings.append(
                {
                    "name": entry["name"],
                    "written_form": entry["written_form"],
                    "object_id": item["object_id"],
                    "canonical": item["canonical"],
                    "grammars": list(item["grammars"]),
                    "grammar_count": item["grammar_count"],
                    "degree": item["degree"],
                    "roots": item["roots"],
                    "parity": profile.get("parity"),
                    "bounded": profile.get("bounded"),
                    "periodic": profile.get("periodic"),
                    "period": profile.get("period"),
                    "constant": profile.get("constant"),
                    "growth_plus": profile.get("limit_at_plus_infinity"),
                    "growth_minus": profile.get("limit_at_minus_infinity"),
                    "real_poles": profile.get("real_poles"),
                }
            )
    return {
        "series_entry_count": len(entries),
        "reading_count": len(readings),
        "readings": readings,
        "periodic_reading_count": sum(1 for item in readings if item["periodic"]),
        "bounded_reading_count": sum(1 for item in readings if item["bounded"]),
        "bounded_grammar_count": sum(item["grammar_count"] for item in readings if item["bounded"]),
    }


# ------------------------------------------------------------------------------- measurement


def _comparable(atlas: dict[str, Any]) -> list[Any]:
    """The parts of an atlas that must not depend on how many processes computed it."""
    return [
        [
            entry["name"],
            entry["distinct_object_count"],
            [[item["object_id"], item["canonical"], item["grammars"], item["roots"]] for item in entry["objects"]],
        ]
        for entry in atlas["entries"]
    ]


def parallelism_measurement(
    catalogue: Sequence[StandardForm] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Run the atlas sequentially and in a pool, time both, and check they produce the same thing.

    The repository policy is multicore by default with a measured decision. This function IS the
    measurement: it returns both wall clocks, the speedup, and which path a run of this size should
    take. Sequential winning is a valid outcome and is recorded as such.
    """
    catalogue = tuple(catalogue or STANDARD_CATALOGUE)
    grammars = tuple(grammars or all_grammars())
    sequential = world_atlas(catalogue, grammars, workers=1)
    parallel_workers = workers if workers is not None else max(2, resolve_worker_count(len(catalogue)))
    parallel = world_atlas(catalogue, grammars, workers=parallel_workers)
    identical = _comparable(sequential) == _comparable(parallel)
    speedup = sequential["wall_clock_seconds"] / max(parallel["wall_clock_seconds"], 1e-12)
    return {
        "item_count": len(catalogue),
        "cpu_count": os.cpu_count(),
        "sequential_seconds": sequential["wall_clock_seconds"],
        "parallel_seconds": parallel["wall_clock_seconds"],
        "parallel_workers": parallel["workers"],
        "speedup": speedup,
        "identical_results": identical,
        "faster_path": "parallel" if parallel["wall_clock_seconds"] < sequential["wall_clock_seconds"] else "sequential",
        "automatic_worker_count": resolve_worker_count(len(catalogue)),
    }


def headline_report(workers: int | None = None) -> dict[str, Any]:
    """The five headline questions, each answered from a measured atlas."""
    atlas = world_atlas(workers=workers)
    divergence = divergence_report(atlas=atlas)
    quadratic = next(entry for entry in atlas["entries"] if entry["name"] == "quadratic_standard")
    radical_worlds = sum(
        item["grammar_count"] for item in quadratic["objects"] if item["solution"]["requires_radical"]
    )
    return {
        "atlas": atlas,
        "divergence": divergence,
        "series": series_report(atlas),
        "root_domain": ROOT_DOMAIN,
        "root_convention": ROOT_CONVENTION_NOTE,
        "incomplete_root_page_count": atlas["incomplete_root_page_count"],
        "quadratic": {
            "written_form": quadratic["written_form"],
            "distinct_object_count": quadratic["distinct_object_count"],
            "objects": [
                {
                    "object_id": item["object_id"],
                    "canonical": item["canonical"],
                    "factored": item["factored"],
                    "degree": item["degree"],
                    "root_domain": item["root_domain"],
                    "roots": item["roots"],
                    "roots_complete": item["roots_complete"],
                    "requires_radical": item["requires_radical"],
                    "discriminant": item["discriminant"],
                    "vertex": item["vertex"],
                    "grammars": list(item["grammars"]),
                    "grammar_count": item["grammar_count"],
                    "method": item["solution"]["method"],
                }
                for item in quadratic["objects"]
            ],
            "radical_world_count": radical_worlds,
            "radical_free_world_count": atlas["grammar_count"] - radical_worlds,
        },
    }
