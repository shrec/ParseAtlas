"""Tests for the outer-function atlas of experiment 0002.

Everything this module reports about a grammar's reading must be a function of the denoted
value.  :func:`test_a_removable_singularity_does_not_move_the_composed_domain` is the regression
test for NF-2026-00004, where it was not.
"""

from sympy import Symbol, simplify

from parseatlas.canonical import to_sympy
from parseatlas.functions import analyze_outer_functions, canonical_argument
from parseatlas.grammar import all_grammars
from parseatlas.parser import parse


def test_outer_atlas_reuses_all_grammar_results():
    report = analyze_outer_functions("2*t + 1 - t/2", ("sin", "exp", "log", "sqrt", "reciprocal"))
    assert report["functions"] == ["sin", "exp", "log", "sqrt", "reciprocal"]
    assert len(report["results"]) == 25 * 5


def test_sine_reports_constant_collapse_and_period():
    report = analyze_outer_functions("2*t + 1 - t/2", ("sin",))
    constant = next(item for item in report["results"] if item["grammar"] == "G01")
    oscillating = next(item for item in report["results"] if item["grammar"] == "G03")
    assert constant["canonical"] == "sin(1)"
    assert constant["properties"]["constant_argument"] is True
    assert oscillating["properties"]["frequency"] == "1/2"
    assert oscillating["properties"]["period"] == "4*pi"
    tangent = next(item for item in analyze_outer_functions("2*t + 1 - t/2", ("tan",))["results"] if item["grammar"] == "G03")
    assert tangent["properties"]["period"] == "2*pi"


def test_log_and_reciprocal_keep_real_domain_information():
    report = analyze_outer_functions("x/x", ("log", "reciprocal"))
    assert all(item["inner_excluded_points"] == ["0"] for item in report["results"])
    assert all(item["properties"]["inner_real_domain"] == "Reals" for item in report["results"])
    assert all(item["canonical"] in {"0", "1"} for item in report["results"])


def test_a_removable_singularity_does_not_move_the_composed_domain():
    """NF-2026-00004: the domain slot must describe the value, not the parse tree.

    ``3 * 2 - t / 2 - t`` is read by eight of the twenty-five grammars as the constant ``3``.
    Four of them leave the SymPy tree ``(6 - 3*t)/(2 - t)`` -- an uncancelled removable
    singularity -- and four leave ``Integer(3)``, because SymPy cancels at construction for one
    shape and not the other.  Composing ``log`` on the raw tree gave the first four
    ``Union(Interval.open(-oo, 2), Interval.open(2, oo))`` and the second four ``Reals``, which
    split one semantic class in two.  Both readings carry the excluded point ``2`` either way,
    so the validity restriction was never the thing in dispute.
    """
    source = "3 * 2 - t / 2 - t"
    variable = Symbol("t", real=True)
    grammars = all_grammars()
    raw = {grammar.id: to_sympy(parse(source, grammar)) for grammar in grammars}
    collapsing = [gid for gid, expression in raw.items() if simplify(expression) == 3]
    assert len(collapsing) == 8
    assert {str(raw[gid]) for gid in collapsing} == {"3", "(6 - 3*t)/(2 - t)"}

    report = analyze_outer_functions(source, ("log",), grammars)
    rows = {item["grammar"]: item for item in report["results"] if item["grammar"] in collapsing}
    assert {item["canonical"] for item in rows.values()} == {"log(3)"}
    assert {item["properties"]["real_domain"] for item in rows.values()} == {"Reals"}
    assert {item["properties"]["inner_real_domain"] for item in rows.values()} == {"Reals"}
    assert {tuple(item["inner_excluded_points"]) for item in rows.values()} == {("2",)}
    assert all(item["properties"]["constant_argument"] is True for item in rows.values())
    assert str(canonical_argument(raw["G01"])) == "3"
    assert canonical_argument(raw["G01"]).diff(variable) == 0


def test_the_domain_slots_are_computed_on_one_shared_canonical_argument():
    """Two spellings of one value must not reach two composed canonical forms either.

    Pre-fix, ``simplify(log(raw))`` landed on ``log(t*(t - 3)) - log(2)`` for one tree and
    ``log(t*(t - 3)/2)`` for another tree of the same value.  Composing on the canonical argument
    leaves one argument, hence one composed form.
    """
    source = "t * t - 3 / 2"
    grammars = all_grammars()
    raw = {grammar.id: to_sympy(parse(source, grammar)) for grammar in grammars}
    target = simplify(raw["G01"])
    family = [gid for gid, expression in raw.items() if simplify(expression) == target]
    assert len({str(raw[gid]) for gid in family}) > 1, "the source must actually carry residue"

    report = analyze_outer_functions(source, ("log",), grammars)
    rows = {item["grammar"]: item for item in report["results"] if item["grammar"] in family}
    assert {item["canonical"] for item in rows.values()} == {"log(t*(t - 3)/2)"}
    assert {item["properties"]["real_domain"] for item in rows.values()} == {
        "Union(Interval.open(-oo, 0), Interval.open(3, oo))"
    }
