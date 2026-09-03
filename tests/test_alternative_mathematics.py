"""Experiment 0035: the standard objects of mathematics in each of the 25 worlds.

Every assertion here is a pin on measured output. The expensive whole-catalogue atlas is never run
in the suite; one module-scoped atlas over a five-entry catalogue carries most of the claims, and
each remaining test builds the smallest input that can carry its own.
"""

import pytest

from parseatlas.alternative_mathematics import (
    STANDARD_CATALOGUE,
    StandardForm,
    divergence_report,
    parallelism_measurement,
    reading_profiles,
    resolve_worker_count,
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
    assert other["method"] == "degree 3: 3 roots read straight off the factorisation, no radical"


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


# ------------------------------------------------------- the semantic key, not the canonical text


def test_objects_are_separated_by_the_full_semantic_key_not_canonical_text_alone():
    keys = world_keys(SINE_SERIES.source)
    texts = {key[0] for key in keys.values()}
    assert len(set(keys.values())) == 14
    assert len(texts) < 14  # readings that print the same but have different domains


# ------------------------------------------------------------------------- multicore measurement


def test_worker_count_is_derived_from_the_observed_cores():
    assert resolve_worker_count(4) == 1  # below the floor, process startup would dominate
    assert resolve_worker_count(64) > 1
    assert resolve_worker_count(64, workers=3) == 3


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
