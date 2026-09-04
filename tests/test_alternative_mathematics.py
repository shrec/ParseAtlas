"""Experiment 0035: the standard objects of mathematics in each of the 25 worlds.

Every assertion here is a pin on measured output. The expensive whole-catalogue atlas is never run
in the suite; one module-scoped atlas over a five-entry catalogue carries most of the claims, and
each remaining test builds the smallest input that can carry its own.
"""

import os

import pytest
from sympy import I, Rational, Symbol, sqrt

from parseatlas.alternative_mathematics import (
    ROOT_CONVENTION_NOTE,
    ROOT_DOMAIN,
    STANDARD_CATALOGUE,
    StandardForm,
    divergence_report,
    parallelism_measurement,
    reading_profiles,
    render_textbook,
    requires_radical,
    resolve_worker_count,
    root_list_is_complete,
    solution_formula,
    textbook,
    world_atlas,
    world_keys,
    world_object,
)
from parseatlas.grammar import all_grammars, control_grammar, strict_grammars

QUADRATIC = StandardForm("quadratic_standard", "algebra", "a*x*x + b*x + c", "x")
SINE_SERIES = StandardForm("sine_series", "analysis", "x - x*x*x/6 + x*x*x*x*x/120", "x", series=True)
INVARIANT_CANDIDATES = (
    StandardForm("compound_interest", "arithmetic", "p*r*t/100", "p"),
    StandardForm("triangle_area", "geometry", "b*h/2", "b"),
    StandardForm("distributive_law", "algebra", "a*(b + c)", "a"),
    StandardForm("rate_form", "arithmetic", "d/t", "d"),
)
MIXED = INVARIANT_CANDIDATES + (QUADRATIC,)
TAUGHT = (
    StandardForm("quadratic_standard", "algebra", "a*x*x + b*x + c", "x"),
    StandardForm("difference_of_squares", "algebra", "a*a - b*b", "a"),
    StandardForm("circle_form", "geometry", "x*x + y*y - r*r", "x"),
)


@pytest.fixture(scope="module")
def mixed_atlas():
    """Four convention-independent candidates plus the standard quadratic, over all 25 worlds."""
    return world_atlas(catalogue=MIXED, workers=1)


@pytest.fixture(scope="module")
def quadratic_entry(mixed_atlas):
    return mixed_atlas["entries"][4]


# --------------------------------------------------------------- the founding question, pinned


def test_standard_quadratic_produces_exactly_two_objects(quadratic_entry):
    assert quadratic_entry["written_form"] == "a*x*x + b*x + c"
    assert quadratic_entry["grammar_count"] == 25
    assert quadratic_entry["distinct_object_count"] == 2


def test_thirteen_worlds_read_the_quadratic_as_a_quadratic_needing_a_radical(quadratic_entry):
    group = quadratic_entry["objects"][0]
    assert group["grammar_count"] == 13
    assert group["canonical"] == "a*x**2 + b*x + c"
    assert group["degree"] == 2
    assert group["requires_radical"] is True
    assert group["discriminant"] == "-4*a*c + b**2"
    assert group["vertex"] == {"x": "-b/(2*a)", "y": "c - b**2/(4*a)"}
    assert group["roots"] == [
        "(-b - sqrt(-4*a*c + b**2))/(2*a)",
        "(-b + sqrt(-4*a*c + b**2))/(2*a)",
    ]
    assert group["grammars"] == [
        "G0", "G09", "G10", "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G22", "G23", "G24",
    ]


def test_twelve_worlds_read_the_quadratic_as_a_factored_cubic_with_no_radical(quadratic_entry):
    group = quadratic_entry["objects"][1]
    assert group["grammar_count"] == 12
    assert group["canonical"] == "a*x*(b + x)*(c + x)"
    assert group["degree"] == 3
    assert group["requires_radical"] is False
    assert group["discriminant"] is None
    assert group["roots"] == ["0", "-b", "-c"]
    assert [item["multiplicity"] for item in group["roots_with_multiplicity"]] == [1, 1, 1]
    assert group["grammars"] == [
        "G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G11", "G19", "G20", "G21",
    ]


def test_control_grammar_belongs_to_the_degree_two_group(quadratic_entry):
    assert quadratic_entry["control_object_id"] == "O01"
    assert quadratic_entry["control_group_size"] == 13
    assert "G0" in quadratic_entry["objects"][0]["grammars"]
    assert "G0" not in quadratic_entry["objects"][1]["grammars"]


def test_thirteen_of_twenty_five_worlds_need_a_radical_for_the_standard_quadratic(quadratic_entry):
    assert quadratic_entry["radical_grammar_count"] == 13


def test_solution_formula_names_the_procedure_of_each_world():
    control = solution_formula("a*x*x + b*x + c", control_grammar(), "x")
    assert control["degree"] == 2
    assert control["has_discriminant"] is True
    assert control["requires_radical"] is True
    assert control["root_count"] == 2
    assert control["method"] == "quadratic formula: discriminant, then a square root"

    other = solution_formula("a*x*x + b*x + c", strict_grammars()[0], "x")
    assert other["grammar_id"] == "G01"
    assert other["degree"] == 3
    assert other["has_discriminant"] is False
    assert other["discriminant"] is None
    assert other["requires_radical"] is False
    assert other["roots"] == ["0", "-b", "-c"]
    assert other["method"] == (
        "degree 3: 3 distinct roots over C, multiplicities summing to 3, "
        "read straight off the factorisation, no radical"
    )


def test_a_radical_free_degree_two_object_is_not_called_a_quadratic_formula():
    """A degree-2 reading whose roots are rational must not be labelled as needing a radical."""
    difference = solution_formula("a*a - b*b", control_grammar(), "a")
    assert difference["degree"] == 2
    assert difference["has_discriminant"] is True
    assert difference["requires_radical"] is False
    assert difference["roots"] == ["-b", "b"]
    assert difference["method"] == (
        "degree 2, radical-free: the roots are already rational in the coefficients"
    )


def test_radical_detection_separates_fractional_powers_from_reciprocals():
    """``1/a`` is ``Pow(a, -1)`` and must not count; ``sqrt`` and cube roots must."""
    a = Symbol("a", real=True)
    assert requires_radical([sqrt(a)]) is True
    assert requires_radical([a ** Rational(1, 3)]) is True
    assert requires_radical([(1 + sqrt(5)) / 2]) is True
    assert requires_radical([1 / a]) is False
    assert requires_radical([a**2, -a, a**-3, Rational(3, 4)]) is False
    assert requires_radical([]) is False


# ------------------------------------------------------------------------- the root convention
#
# These pin the fix for a defect that made the generated pages state something untrue: the roots
# were solved with a ``real=True`` symbol, so SymPy returned every complex root when the
# coefficients were free symbols and only the real ones when they were numeric. Two notions of
# "root" then appeared on one page without either being named. The convention is now over C
# everywhere, and the incompleteness that used to hide it is a measured flag rather than prose.


def test_every_root_list_declares_the_domain_it_was_solved_over():
    assert ROOT_DOMAIN == "C"
    solution = solution_formula("a*x*x + b*x + c", control_grammar(), "x")
    assert solution["root_domain"] == "C"
    assert solution["root_convention"] == ROOT_CONVENTION_NOTE
    assert "over `C`" in ROOT_CONVENTION_NOTE
    book = textbook(control_grammar(), catalogue=TAUGHT)
    assert book["root_domain"] == "C"
    assert book["root_convention"] == ROOT_CONVENTION_NOTE
    assert all(page["root_domain"] == "C" for page in book["pages"])
    # the convention is printed with the table, not only carried in the record
    assert ROOT_CONVENTION_NOTE in render_textbook(book)
    assert "roots over C" in render_textbook(book)


def test_control_geometric_sum_page_reports_all_three_roots():
    """``1 + r + r*r + r*r*r`` under G0: the page used to print one root of three and no radical."""
    solution = solution_formula("1 + r + r*r + r*r*r", control_grammar(), "r")
    assert solution["denotes"] == "r**3 + r**2 + r + 1"
    assert solution["degree"] == 3
    assert solution["roots"] == ["-1", "-I", "I"]
    assert solution["root_multiplicity_sum"] == 3
    assert solution["roots_complete"] is True
    # ``I`` is a square root, so the honest answer here is that a radical IS required
    assert solution["requires_radical"] is True
    assert solution["method"] == "degree 3: a radical or an unsolvable root object is required"
    assert "factorisation" not in solution["method"]


def test_control_sine_series_page_reports_all_five_roots():
    """The quintic reading under G0: one real root printed before, five roots with radicals now."""
    solution = solution_formula("x - x*x*x/6 + x*x*x*x*x/120", control_grammar(), "x")
    assert solution["degree"] == 5
    assert solution["root_count"] == 5
    assert solution["root_multiplicity_sum"] == 5
    assert solution["roots_complete"] is True
    assert solution["roots"][0] == "0"
    assert sum(1 for root in solution["roots"] if "I" in root) == 4
    assert solution["requires_radical"] is True
    assert solution["method"] == "degree 5: a radical or an unsolvable root object is required"


def test_no_world_reports_a_root_list_short_of_its_degree():
    """Swept over every world for the entry that broke in the most of them.

    ``geometric_sum`` is the cheap member of the group the old convention truncated (it was short in
    `13` of `25` worlds), and every one of its `25` readings has a polynomial degree, so the
    multiplicity sum has something to be compared against in all of them.
    """
    records = [world_object("1 + r + r*r + r*r*r", grammar, "r") for grammar in all_grammars()]
    assert len(records) == 25
    assert all(record["degree"] is not None for record in records)
    assert all(record["roots_complete"] is True for record in records)
    for record in records:
        assert record["root_multiplicity_sum"] == record["degree"]
    atlas = world_atlas(
        catalogue=(StandardForm("geometric_sum", "analysis", "1 + r + r*r + r*r*r", "r", True),),
        workers=1,
    )
    assert atlas["incomplete_root_page_count"] == 0
    assert atlas["root_domain"] == "C"


def test_the_series_pages_of_the_control_world_are_complete_and_all_need_a_radical():
    series = tuple(entry for entry in STANDARD_CATALOGUE if entry.series)
    assert len(series) == 4
    book = textbook(control_grammar(), catalogue=series)
    assert book["incomplete_root_page_count"] == 0
    assert book["radical_page_count"] == 4
    assert all(page["roots_complete"] is True for page in book["pages"])


def test_the_completeness_check_compares_the_printed_list_not_sympys_table():
    """The check that used to be a false assurance, pinned as a function of the REPORTED list.

    The predecessor compared SymPy's internal root table against the degree, so it answered ``True``
    in exactly the cases where the printed list was short. Passing a short list must give ``False``.
    """
    short = [{"root": "-1", "multiplicity": 1}]
    assert root_list_is_complete(3, short) is False
    assert root_list_is_complete(3, short + [{"root": "-I", "multiplicity": 1}]) is False
    assert root_list_is_complete(3, [{"root": "-1", "multiplicity": 3}]) is True
    assert root_list_is_complete(2, [{"root": "-b", "multiplicity": 2}]) is True
    # a rational reading or the zero reading has no degree to account for: not silently "complete"
    assert root_list_is_complete(None, []) is None
    assert root_list_is_complete(None, short) is None


def test_an_incomplete_root_list_is_flagged_wherever_it_would_be_printed():
    """No measured page is short any more, so the flag is proved on a constructed short page."""
    page = {
        "name": "constructed",
        "written_form": "q",
        "denotes": "q**3 + 1",
        "degree": 3,
        "roots": ["-1"],
        "root_multiplicity_sum": 1,
        "roots_complete": False,
        "requires_radical": False,
        "solution": {"method": "irrelevant"},
    }
    book = {
        "grammar_id": "GX",
        "precedence_text": "x",
        "root_convention": ROOT_CONVENTION_NOTE,
        "pages": [page],
    }
    rendered = render_textbook(book)
    assert "INCOMPLETE: 1/3" in rendered

    solution = solution_formula("1 + r + r*r + r*r*r", control_grammar(), "r")
    assert solution["roots_complete"] is True  # the real page is complete
    from parseatlas.alternative_mathematics import _solution_method

    assert _solution_method(3, False, 1, True, complete=False, multiplicity_sum=1) == (
        "degree 3: INCOMPLETE - the reported roots account for 1 of 3 with multiplicity"
    )


def test_radical_detection_counts_the_imaginary_unit():
    """``I`` is ``sqrt(-1)``; dropping it from the radical test is what made short pages read "no"."""
    b = Symbol("b", real=True)
    assert requires_radical([I]) is True
    assert requires_radical([-I, I]) is True
    assert requires_radical([b * (Rational(1, 2) - sqrt(3) * I / 2)]) is True
    assert requires_radical([-1, b, -b]) is False


# ---------------------------------------------------------------- the convention-independent core


def test_compound_interest_is_identical_in_every_world(mixed_atlas):
    interest = mixed_atlas["entries"][0]
    assert interest["written_form"] == "p*r*t/100"
    assert interest["distinct_object_count"] == 1
    assert interest["objects"][0]["grammar_count"] == 25
    assert interest["objects"][0]["canonical"] == "p*r*t/100"
    assert len(set(world_keys("p*r*t/100").values())) == 1


def test_divergence_report_lists_invariant_and_fractured_sides(mixed_atlas):
    report = divergence_report(atlas=mixed_atlas)
    assert report["invariant_objects"] == [
        "compound_interest", "triangle_area", "distributive_law", "rate_form",
    ]
    assert report["invariant_count"] == 4
    assert report["fractured_objects"] == [
        {
            "name": "quadratic_standard",
            "area": "algebra",
            "written_form": "a*x*x + b*x + c",
            "distinct_object_count": 2,
        }
    ]
    assert report["most_fractured"]["name"] == "quadratic_standard"


def test_control_is_not_the_only_world_that_reads_this_catalogue_its_way(mixed_atlas):
    report = divergence_report(atlas=mixed_atlas)
    assert report["control_agreement"]["G0"] == 5
    assert report["control_is_unique"] is False
    # the twelve worlds that also read the quadratic as a quadratic; the other four entries are
    # convention-independent, so they cannot separate anyone from G0.
    assert report["grammars_agreeing_with_control_everywhere"] == [
        "G09", "G10", "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G22", "G23", "G24",
    ]


# ------------------------------------------------------------------- the world we actually live in


def test_control_textbook_reproduces_the_mathematics_we_teach():
    book = textbook(control_grammar(), catalogue=TAUGHT)
    assert book["grammar_id"] == "G0"
    assert book["precedence_text"] == "*=/ > +=-"
    pages = {page["name"]: page for page in book["pages"]}
    assert len(pages) == 3

    quadratic = pages["quadratic_standard"]
    assert quadratic["denotes"] == "a*x**2 + b*x + c"
    assert quadratic["degree"] == 2
    assert quadratic["discriminant"] == "-4*a*c + b**2"
    assert quadratic["vertex"]["x"] == "-b/(2*a)"
    assert quadratic["roots"] == [
        "(-b - sqrt(-4*a*c + b**2))/(2*a)",
        "(-b + sqrt(-4*a*c + b**2))/(2*a)",
    ]

    difference = pages["difference_of_squares"]
    assert difference["denotes"] == "a**2 - b**2"
    assert difference["factored"] == "(a - b)*(a + b)"
    assert difference["roots"] == ["-b", "b"]
    assert difference["requires_radical"] is False

    circle = pages["circle_form"]
    assert circle["denotes"] == "-r**2 + x**2 + y**2"
    assert circle["degree"] == 2
    assert circle["roots"] == ["-sqrt((r - y)*(r + y))", "sqrt((r - y)*(r + y))"]


# ------------------------------------------------------------------------- truncated series honesty


def test_truncated_sine_series_is_never_periodic_in_any_world():
    profiles = reading_profiles(SINE_SERIES.source, variable="x")
    assert len(profiles) == 25
    assert all(profile["univariate"] for profile in profiles.values())
    assert [grammar_id for grammar_id, item in profiles.items() if item["periodic"]] == []
    # the only non-``None`` period in the sweep is SymPy's degenerate ``0`` for a constant reading
    assert {item["period"] for item in profiles.values()} <= {None, "0"}
    assert all(item["constant"] for item in profiles.values() if item["period"] == "0")


def test_control_reading_of_the_sine_series_is_an_unbounded_aperiodic_quintic():
    record = world_object(SINE_SERIES.source, control_grammar(), "x")
    assert record["canonical"] == "x**5/120 - x**3/6 + x"
    assert record["degree"] == 5
    profile = record["profile"]
    assert profile["parity"] == "odd"
    assert profile["periodic"] is False
    assert profile["period"] is None
    assert profile["bounded"] is False
    assert profile["limit_at_plus_infinity"] == "oo"


def test_some_worlds_read_the_cosine_series_as_a_bounded_function():
    profiles = reading_profiles("1 - x*x/2 + x*x*x*x/24", variable="x")
    assert profiles["G0"]["bounded"] is False
    assert [grammar_id for grammar_id, item in profiles.items() if item["bounded"]]
    assert not any(item["periodic"] for item in profiles.values())

    # G14 reads it as a rational function with limit 1 either way and no real pole: bounded.
    assert profiles["G14"]["real_poles"] == []
    assert profiles["G14"]["limit_at_plus_infinity"] == "1"
    assert profiles["G14"]["bounded"] is True

    # G01 also has finite limits at both infinities, but it has real poles, so it is NOT bounded.
    assert profiles["G01"]["limit_at_plus_infinity"] == "0"
    assert profiles["G01"]["limit_at_minus_infinity"] == "0"
    assert profiles["G01"]["real_poles"] == ["-2", "0"]
    assert profiles["G01"]["bounded"] is False


# ------------------------------------------------------- the semantic key, not the canonical text


def test_objects_are_separated_by_the_full_semantic_key_not_canonical_text_alone():
    keys = world_keys(SINE_SERIES.source)
    texts = {key[0] for key in keys.values()}
    assert len(set(keys.values())) == 14
    assert len(texts) < 14  # readings that print the same but have different excluded points


def test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement():
    """The triple is `(canonical, domain, excluded points)` but `domain` never varies.

    `parseatlas.canonical.canonicalize` writes the literal `"R"` for every expression, so the
    component that actually separates objects is `(canonical, excluded points)`. This is pinned
    rather than described, so the report's guarantee is stated at its true strength.
    """
    keys = list(world_keys(SINE_SERIES.source).values()) + list(world_keys("1/a + 1/b").values())
    assert {key[1] for key in keys} == {"R"}
    two_component = {(key[0], key[2]) for key in keys}
    assert len(two_component) == len({key for key in keys})


# ------------------------------------------------------------------------- multicore measurement


def test_worker_count_is_derived_from_the_observed_cores():
    cores = os.cpu_count() or 1
    assert resolve_worker_count(4) == 1  # below the floor, process startup would dominate
    # derived from the observed cores, with one core of headroom for the interactive session
    assert resolve_worker_count(1000) == max(1, cores - 1)
    assert resolve_worker_count(1000) < cores or cores == 1
    assert resolve_worker_count(64, workers=3) == 3
    assert resolve_worker_count(2, workers=9) == 2  # never more workers than items


def test_sequential_and_parallel_atlas_agree():
    measurement = parallelism_measurement(catalogue=INVARIANT_CANDIDATES, workers=2)
    assert measurement["identical_results"] is True
    assert measurement["parallel_workers"] == 2
    assert measurement["sequential_seconds"] > 0
    assert measurement["parallel_seconds"] > 0


def test_catalogue_is_well_formed():
    names = [entry.name for entry in STANDARD_CATALOGUE]
    assert len(names) == len(set(names))
    assert len(STANDARD_CATALOGUE) == 26
    assert sum(1 for entry in STANDARD_CATALOGUE if entry.series) == 4
    assert len(all_grammars()) == 25
    for entry in STANDARD_CATALOGUE:
        assert entry.variable in entry.source
