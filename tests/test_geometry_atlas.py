"""Experiment 0040: the geometry of the 25 worlds.

Every assertion here is a pin on measured output. The whole-catalogue atlas is built once, at module
scope, because it is what the headline numbers are read from; every other test builds the smallest
input that can carry its own claim.
"""

import os
import re
import xml.etree.ElementTree as ElementTree

import pytest

from parseatlas.alternative_mathematics import semantic_key as project_semantic_key
from parseatlas.canonical import canonicalize
from parseatlas.geometry_atlas import (
    CURVE_CATALOGUE,
    GRID_STEPS,
    PARALLEL_MINIMUM_ITEMS,
    StandardCurve,
    _comparable,
    _plane_callable,
    _text_width,
    atlas,
    classify,
    curve_figure,
    curve_in_world,
    headline_report,
    single_point,
    parallelism_measurement,
    resolve_worker_count,
    semantic_key,
    survival_report,
    zero_set_segments,
)
from parseatlas.grammar import all_grammars, control_grammar
from parseatlas.parser import parse

#: Both language sides, because the documentation policy makes them equally normative: a figure
#: referenced by one report and missing from disk is a defect no matter which language names it.
#: The Georgian side was renamed from REPORT.md to REPORT.ka.md when 0040 was found to postdate the
#: policy's cutover, which is why this is a tuple rather than a path.
_EXPERIMENT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "experiments",
    "0040_geometry_atlas",
)
REPORTS = (
    os.path.join(_EXPERIMENT, "REPORT.ka.md"),
    os.path.join(_EXPERIMENT, "REPORT.en.md"),
)
FIGURES = os.path.join(_EXPERIMENT, "figures")
SVG = "{http://www.w3.org/2000/svg}"

# A four-curve slice that still crosses the parallel threshold: 4 * 25 = 100 cells.
SLICE = tuple(
    entry
    for entry in CURVE_CATALOGUE
    if entry.name in {"line", "circle", "slope_form", "degenerate_pair"}
)


@pytest.fixture(scope="module")
def full_atlas():
    """The whole cross product, once. This is what the report's numbers are read from."""
    return atlas()


@pytest.fixture(scope="module")
def entries(full_atlas):
    return {entry["name"]: entry for entry in full_atlas["entries"]}


@pytest.fixture(scope="module")
def survival(full_atlas):
    return survival_report(atlas_result=full_atlas)


# ------------------------------------------------------------------ the two headline results


def test_the_circle_is_four_different_objects_and_ours_is_the_nine_world_group(entries):
    """`x*x + y*y - r*r` denotes exactly 4 objects; the group holding G0 has 9 worlds in it."""
    circle = entries["circle"]
    assert circle["distinct_object_count"] == 4
    assert circle["control_group_size"] == 9
    assert circle["control_label"] == "conic: circle"
    assert [item["grammar_count"] for item in circle["objects"]] == [9, 8, 4, 4]
    assert [item["resolved_label"] for item in circle["objects"]] == [
        "conic: circle",
        "cubic curve",
        "cubic curve",
        "conic: ellipse",
    ]
    assert circle["objects"][0]["grammars"] == [
        "G0", "G13", "G14", "G15", "G16", "G17", "G18", "G23", "G24",
    ]
    # the eight-world reading is not merely a cubic: it is three straight lines.
    assert circle["objects"][1]["canonical"] == "-r*x*(r - y)*(x + y)"
    assert circle["objects"][1]["component_of_lines"] is True
    assert circle["objects"][1]["total_degree"] == 3


def test_in_twelve_of_twenty_five_worlds_the_equation_of_a_line_is_not_a_line(entries):
    """The headline: 13 worlds read `y - m*x - c` as a line, 12 read a curve with an x*y term."""
    line = entries["line"]
    assert line["distinct_object_count"] == 2
    assert [item["grammar_count"] for item in line["objects"]] == [13, 12]
    assert line["control_group_size"] == 13
    assert line["control_label"] == "line"

    straight, dissenting = line["objects"]
    assert straight["resolved_label"] == "line"
    assert straight["has_cross_term"] is False
    assert straight["total_degree"] == 1

    assert dissenting["grammar_count"] == 12
    assert dissenting["has_cross_term"] is True, "the dissenting group carries an x*y term"
    assert dissenting["total_degree"] == 2
    assert dissenting["resolved_label"] == "degenerate conic: two intersecting lines"
    assert dissenting["canonical"] == "(c - x)*(m - y)"
    assert dissenting["grammars"] == [
        "G01", "G02", "G05", "G07", "G08", "G09", "G10", "G11", "G12", "G19", "G21", "G22",
    ]


# ---------------------------------------------------------------------- the classifier itself


def test_classify_names_a_circle_an_ellipse_and_a_hyperbola_by_hand_checked_discriminants():
    """Each label is checked against the discriminant computed by hand from the coefficients."""
    circle = classify("x*x + y*y - 4", ("x", "y"))
    # A = 1, B = 0, C = 1 -> B*B - 4*A*C = -4 < 0, and A == C with B == 0, so it is a circle.
    assert circle["discriminant"] == "-4"
    assert circle["discriminant_sign"] == "negative"
    assert circle["label"] == "conic: circle"
    assert circle["conic_coefficients"] == {
        "A": "1", "B": "0", "C": "1", "D": "0", "E": "0", "F": "-4",
    }

    ellipse = classify("x*x/4 + y*y/9 - 1", ("x", "y"))
    # cleared over 36 the numerator is 9*x*x + 4*y*y - 36, so A = 9, B = 0, C = 4 and
    # B*B - 4*A*C = -144 < 0 with A != C: an ellipse and not a circle.
    assert ellipse["numerator"] == "9*x**2 + 4*y**2 - 36"
    assert ellipse["denominator"] == "36"
    assert ellipse["discriminant"] == "-144"
    assert ellipse["label"] == "conic: ellipse"

    hyperbola = classify("x*x/4 - y*y/9 - 1", ("x", "y"))
    # numerator 9*x*x - 4*y*y - 36: A = 9, C = -4, so B*B - 4*A*C = +144 > 0.
    assert hyperbola["discriminant"] == "144"
    assert hyperbola["discriminant_sign"] == "positive"
    assert hyperbola["label"] == "conic: hyperbola"


def test_classify_names_the_parabola_and_the_four_degenerate_conics():
    """The remaining conic labels, each from its own discriminant and 3x3 determinant."""
    parabola = classify("y - x*x", ("x", "y"))
    assert parabola["discriminant"] == "0" and parabola["degenerate"] is False
    assert parabola["label"] == "conic: parabola"

    crossing = classify("x*y", ("x", "y"))  # B*B - 4*A*C = 1 > 0, determinant 0
    assert crossing["determinant"] == "0"
    assert crossing["label"] == "degenerate conic: two intersecting lines"

    parallel = classify("x*x - 1", ("x", "y"))  # discriminant 0, determinant 0, distinct factors
    assert parallel["label"] == "degenerate conic: two parallel lines"

    double = classify("x*x", ("x", "y"))  # the same, but with a repeated linear factor
    assert double["label"] == "degenerate conic: a double line"

    point = classify("x*x/4 + y*y/8", ("x", "y"))  # discriminant < 0, determinant 0
    assert point["label"] == "degenerate conic: a single point"


def test_classify_refuses_a_label_it_cannot_justify_and_says_which_sign_decides_it():
    """A symbolic discriminant with no decidable sign gets a refusal plus its branches, not a guess."""
    conditional = classify("x*x + r*y*y - 1", ("x", "y"))
    assert conditional["conditional"] is True
    assert conditional["discriminant"] == "-4*r"
    assert conditional["discriminant_sign"] == "unknown"
    assert conditional["determinant"] == "-r" and conditional["degenerate"] is False
    assert conditional["label"] == "conic (type set by the sign of B^2-4AC = -4*r)"
    assert conditional["conditional_branches"] == {
        "negative": "conic: ellipse",
        "zero": "conic: parabola",
        "positive": "conic: hyperbola",
    }
    # the same refusal on the degenerate side, where the three branches are different objects
    degenerate = classify("x*x + r*y*y", ("x", "y"))
    assert degenerate["degenerate"] is True
    assert degenerate["label"] == "degenerate conic (type set by the sign of B^2-4AC = -4*r)"
    assert degenerate["conditional_branches"]["negative"] == "degenerate conic: a single point"


def test_a_determinant_that_can_vanish_is_not_the_same_as_one_that_does():
    """Degeneracy is identical vanishing; a determinant that vanishes only on a locus is recorded."""
    circle = classify("x*x + y*y - r*r", ("x", "y"))
    assert circle["determinant"] == "-r**2"
    assert circle["degenerate"] is False
    assert circle["degeneracy_locus"] == "-r**2 = 0"
    assert circle["label"] == "conic: circle"


def test_classify_counts_degree_in_the_coordinates_and_reports_the_ambient_degree_separately():
    """`r` names a family, not a direction in the plane, so it does not raise the curve's degree."""
    record = classify("-r**2*x**2 - r**2*x*y + r*x**2*y + r*x*y**2", ("x", "y"))
    assert record["total_degree"] == 3
    assert record["ambient_total_degree"] == 4
    assert record["label"] == "cubic curve"
    assert record["component_of_lines"] is True
    assert record["notes"] == ["reducible: a union of 3 straight lines"]
    assert record["variable_degrees"] == {"x": 2, "y": 2}


def test_classify_sets_the_denominator_aside_instead_of_dying_on_it():
    """The rational readings are the ones an earlier probe died on; the denominator is recorded."""
    record = classify("x**2/(8*y*(y + 4))", ("x", "y"))
    assert record["denominator_set_aside"] is True
    assert record["numerator"] == "x**2"
    assert record["denominator"] == "8*y**2 + 32*y"
    assert record["excluded_locus"] == "8*y**2 + 32*y = 0"
    assert record["label"] == "degenerate conic: a double line"

    whole = classify("0", ("x", "y"))
    assert whole["label"] == "whole plane (identically zero)"
    empty = classify("r**2", ("x", "y"))
    assert empty["label"] == "empty locus (constant in the coordinates)"


def test_classify_never_crashes_anywhere_in_the_full_sweep():
    """Every catalogue entry under every one of the 25 grammars, classified without an exception."""
    grammars = all_grammars()
    assert len(grammars) == 25
    checked = 0
    for entry in CURVE_CATALOGUE:
        for grammar in grammars:
            expression = canonicalize(parse(entry.source, grammar))["sympy_expression"]
            record = classify(expression, entry.variables)
            assert record["label"], f"{entry.name} under {grammar.id} produced no label"
            assert record["family"], f"{entry.name} under {grammar.id} produced no family"
            assert isinstance(record["denominator_set_aside"], bool)
            checked += 1
    assert checked == len(CURVE_CATALOGUE) * 25 == 300


def test_the_conditional_labels_are_the_only_ones_resolved_at_parameter_values(full_atlas):
    """Exactly three readings need a parameter value to be labelled, and each says so."""
    conditional = [
        (entry["name"], item["object_id"], item["label"], item["resolved_label"])
        for entry in full_atlas["entries"]
        for item in entry["objects"]
        if item["conditional"]
    ]
    assert conditional == [
        ("circle", "O04", "conic (type set by the sign of B^2-4AC = -4*r)", "conic: ellipse"),
        (
            "distance_components",
            "O04",
            "conic (type set by the sign of B^2-4AC = -4*d)",
            "conic: ellipse",
        ),
        ("pythagorean_form", "O04", "conic (type set by the sign of B^2-4AC = -4*c)", "conic: ellipse"),
    ]
    for entry in full_atlas["entries"]:
        for item in entry["objects"]:
            expected = (
                "coefficients at the declared parameter values" if item["conditional"] else "coefficients"
            )
            assert item["label_source"] == expected


# ------------------------------------------------------------------------ the rest of the atlas


def test_the_catalogue_is_the_twelve_named_curves_written_without_exponentiation():
    """Generation 1 has no `**`, so every square in the catalogue is written out as a product."""
    assert [entry.name for entry in CURVE_CATALOGUE] == [
        "line",
        "circle",
        "ellipse",
        "hyperbola",
        "parabola",
        "distance_components",
        "midpoint_component",
        "slope_form",
        "pythagorean_form",
        "trapezoid_area",
        "circle_through_origin",
        "degenerate_pair",
    ]
    for entry in CURVE_CATALOGUE:
        assert "**" not in entry.source, f"{entry.name} uses exponentiation, which Generation 1 lacks"
        assert "^" not in entry.source
        assert len(entry.variables) == 2
        assert not set(entry.parameter_map) & set(entry.variables), (
            f"{entry.name} uses one name as both a coordinate and a parameter"
        )


def test_every_curve_is_grouped_on_the_projects_own_semantic_key(entries):
    """The grouping key is the project's triple, imported from experiment 0035, not a local copy."""
    assert semantic_key is project_semantic_key
    circle = entries["circle"]
    control = curve_in_world("x*x + y*y - r*r", control_grammar(), ("x", "y"), (("r", 2),))
    assert control["semantic_key"] == (control["canonical"], "R", ())
    assert control["canonical"] == circle["objects"][0]["canonical"]


def test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement(full_atlas):
    """NF-2026-00005, restated here: `domain` is always "R", so it discriminates nothing."""
    domains = {
        item["domain"] for entry in full_atlas["entries"] for item in entry["objects"]
    }
    assert domains == {"R"}


def test_the_key_still_carries_excluded_points_even_though_they_split_nothing_here(full_atlas):
    """The third component is read; on this catalogue it happens to separate no two objects."""
    record = curve_in_world("y - w/x - v", control_grammar(), ("x", "y"))
    assert record["excluded_points"] == ["0"]
    assert record["semantic_key"] == (record["canonical"], "R", ("0",))
    # and the measured reason it cannot be observed doing any work here: every object already has
    # its own canonical text, so no group is held apart by its excluded points alone.
    assert full_atlas["restriction_split_objects"] == 0
    assert all(
        entry["canonical_text_count"] == entry["distinct_object_count"]
        for entry in full_atlas["entries"]
    )


def test_one_curve_is_the_same_object_in_all_twenty_five_worlds(entries, survival):
    """The fully parenthesised pair of lines is the only object no permutation can touch."""
    assert survival["identical_in_every_world"] == ["degenerate_pair"]
    pair = entries["degenerate_pair"]
    assert pair["distinct_object_count"] == 1
    assert pair["control_group_size"] == 25
    assert pair["objects"][0]["resolved_label"] == "degenerate conic: two intersecting lines"


def test_the_ellipse_fractures_furthest_and_the_survival_ranking_is_pinned(survival, full_atlas):
    """Classification survival per curve, and the count of distinct objects behind it."""
    assert full_atlas["maximum_distinct_objects"] == 13
    assert full_atlas["total_distinct_objects"] == 48
    assert full_atlas["invariant_entry_count"] == 1
    assert survival["most_fractured"] == ["ellipse"]
    assert survival["least_stable"] == ["ellipse"]
    assert sorted(survival["fully_stable"]) == [
        "degenerate_pair",
        "midpoint_component",
        "trapezoid_area",
    ]
    assert {row["name"]: row["surviving_grammar_count"] for row in survival["rows"]} == {
        "line": 13,
        "circle": 9,
        "ellipse": 6,
        "hyperbola": 9,
        "parabola": 13,
        "distance_components": 9,
        "midpoint_component": 25,
        "slope_form": 13,
        "pythagorean_form": 9,
        "trapezoid_area": 25,
        "circle_through_origin": 9,
        "degenerate_pair": 25,
    }


def test_a_surviving_classification_is_not_a_surviving_object(entries):
    """`midpoint_component` is a line in all 25 worlds and four different lines while being one."""
    midpoint = entries["midpoint_component"]
    assert midpoint["distinct_object_count"] == 4
    assert midpoint["distinct_label_count"] == 1
    assert {item["resolved_label"] for item in midpoint["objects"]} == {"line"}
    assert [item["canonical"] for item in midpoint["objects"]] == [
        "-m + x + y/2",
        "(-x - y)/(m - 2)",
        "-m + x/2 + y/2",
        "(x*(m - 2) - y)/(m - 2)",
    ]


def test_the_slope_form_runs_the_other_way(entries):
    """Not every world loses geometry: here the slope form is a hyperbola, and 12 worlds read a line."""
    slope = entries["slope_form"]
    assert slope["control_label"] == "conic: hyperbola"
    assert slope["objects"][0]["grammar_count"] == 13
    assert slope["objects"][1]["resolved_label"] == "line"
    assert slope["objects"][1]["grammar_count"] == 12


def test_the_control_world_is_an_ordinary_member_of_its_groups(survival, full_atlas):
    """G0 is never alone on any curve, and four other worlds read the whole catalogue exactly as it does."""
    assert survival["control_alone_on"] == []
    assert min(survival["control_group_sizes"].values()) == 5
    twins = [
        identifier
        for identifier, count in survival["control_twins"].items()
        if identifier != "G0" and count == full_atlas["entry_count"]
    ]
    assert twins == ["G17", "G18", "G23", "G24"]


def test_the_headline_report_answers_the_five_questions_with_numbers():
    """The documented entry point, checked to answer each of the five questions with a number."""
    report = headline_report()
    assert report["q1_circle"]["distinct_objects"] == 4
    assert report["q1_circle"]["control_group_size"] == 9
    assert report["q2_line"]["still_a_line"] == 13
    assert report["q2_line"]["not_a_line"] == 12
    assert report["q3_stability"]["most_fractured"] == ["ellipse"]
    assert report["q4_invariant"] == ["degenerate_pair"]
    assert report["q5_control"]["alone_on"] == []


# ------------------------------------------------------------------------------- the drawings


# NOTE (review finding F2): the width used below is the module's OWN estimator - the same
# function that chose the SVG width - so this asserts the layout is SELF-CONSISTENT, not that
# the text fits a real font.  An estimator set too low would satisfy both sides at once.  The
# gap was closed once by hand with Adobe Helvetica AFM metrics: all 312 text runs fit with at
# least 56.5px to spare.  Re-run that check by hand if the estimator or the fonts change.
def _assert_text_stays_inside(root, name):
    """Every text run fits inside the viewBox. Shared by the on-disk and freshly-rendered checks."""
    width, height = float(root.get("width")), float(root.get("height"))
    for text in root.iter(f"{SVG}text"):
        size = float(text.get("font-size"))
        mono = "Consolas" in (text.get("font-family") or "")
        span = _text_width(text.text or "", size, mono)
        left = float(text.get("x")) - (span / 2 if text.get("text-anchor") == "middle" else 0)
        assert left >= 0, f"{name}: text starts left of the viewBox"
        assert left + span <= width, f"{name}: {text.text!r} runs past the right edge"
        assert 0 <= float(text.get("y")) <= height, f"{name}: text sits outside the viewBox"


def _referenced_figures(path=None):
    """Figures referenced by one report, or by both when no path is given.

    Both sides must reference the same set: a figure dropped from one language is a divergence
    the bilingual rule forbids, and asserting the union alone would hide it.
    """
    paths = (path,) if path else REPORTS
    seen = []
    for candidate in paths:
        with open(candidate, encoding="utf-8") as handle:
            seen.append(sorted(set(re.findall(r"figures/([A-Za-z0-9_]+\.svg)", handle.read()))))
    assert len(set(map(tuple, seen))) == 1, "the two reports reference different figures"
    return seen[0]


def test_every_svg_the_report_references_exists_and_is_not_empty():
    """A figure that is not on disk is not evidence, and neither is an empty one."""
    referenced = _referenced_figures()
    assert referenced, "the report references no figures"
    assert len(referenced) == len(CURVE_CATALOGUE)
    for name in referenced:
        path = os.path.join(FIGURES, name)
        assert os.path.isfile(path), f"{path} is referenced by the report but does not exist"
        assert os.path.getsize(path) > 0, f"{path} is empty"


def test_every_figure_is_well_formed_paints_its_own_ground_and_stays_inside_the_viewbox():
    """An unpainted SVG is invisible on one of the two grounds, and stray text is a rendering bug."""
    for name in _referenced_figures():
        root = ElementTree.parse(os.path.join(FIGURES, name)).getroot()
        width, height = float(root.get("width")), float(root.get("height"))
        assert root.get("viewBox") == f"0 0 {int(width)} {int(height)}"

        background = root.find(f"{SVG}rect")
        assert background.get("fill") == "#ffffff"
        assert (float(background.get("width")), float(background.get("height"))) == (width, height)

        for element in root.iter():
            if element.tag in (f"{SVG}path", f"{SVG}line", f"{SVG}circle"):
                assert element.get("stroke"), f"{name}: an unstroked mark"
            if element.tag in (f"{SVG}rect", f"{SVG}circle"):
                assert element.get("fill"), f"{name}: an unfilled shape"

        _assert_text_stays_inside(root, name)


def test_every_panel_of_every_figure_actually_draws_something(full_atlas):
    """A blank panel means a parameter landed on a singular locus; nothing may fail silently.

    Both grid parities are checked, because a panel that only draws when the grid happens to land
    on the curve is not drawn, it is lucky.
    """
    for steps in (60, 61):
        for entry in full_atlas["entries"]:
            svg, record = curve_figure(entry, steps=steps)
            assert record["object_count"] == entry["distinct_object_count"]
            for panel in record["panels"]:
                assert panel["segments"] or panel["points"], (
                    f'{entry["name"]} {panel["object_id"]} drew nothing at steps={steps}'
                )
            assert "no real points in this window" not in svg
            _assert_text_stays_inside(
                ElementTree.fromstring(svg), f'{entry["name"]} (freshly rendered)'
            )


def test_the_single_point_panel_draws_its_point_at_either_grid_parity(entries):
    """The one reading in the catalogue whose zero set is a point: `x*x/4 + y*y/8`, ellipse O04."""
    for steps in (60, 61):
        svg, record = curve_figure(entries["ellipse"], steps=steps)
        panel = next(item for item in record["panels"] if item["object_id"] == "O04")
        assert panel["points"] == 1 and panel["segments"] == 0
        assert "<circle" in svg


def test_the_contour_tracer_finds_a_circle_and_a_double_line_in_plain_python():
    """Marching squares with no numpy: a sign-changing curve and a curve that only touches zero."""
    window = (-6.0, 6.0, -6.0, 6.0)
    circle = zero_set_segments(lambda x, y: x * x + y * y - 4.0, window, GRID_STEPS)
    assert len(circle) > 100
    for x1, y1, x2, y2 in circle:
        for x, y in ((x1, y1), (x2, y2)):
            assert abs((x * x + y * y) ** 0.5 - 2.0) < 0.1

    # x*x never changes sign, so on a grid whose nodes miss the line x = 0 the tracer reports
    # nothing at all. The square-free part is the fix: it has the same zero set and does change sign.
    assert zero_set_segments(lambda x, y: x * x, window, 40) == []
    radical = _plane_callable("x**2", ("x", "y"))
    assert len(zero_set_segments(radical, window, 40)) == 39
    raw = _plane_callable("x**2", ("x", "y"), radical=False)
    assert zero_set_segments(raw, window, 40) == []


def test_the_saddle_cell_pairs_its_four_crossings_by_the_centre_value():
    """A cell with four crossings has two possible pairings and only one matches the curve."""
    # f = x*y - 1/4 on the single cell [-1, 1]^2: the branches run through quadrants I and III, so
    # the bottom crossing must join the left one and the right crossing must join the top one.
    segments = zero_set_segments(lambda x, y: x * y - 0.25, (-1.0, 1.0, -1.0, 1.0), 2)
    rounded = sorted(tuple(round(value, 4) for value in segment) for segment in segments)
    assert rounded == [
        (-0.25, -1.0, -1.0, -0.25),
        (1.0, 0.25, 0.25, 1.0),
    ]


def test_a_zero_set_that_is_one_point_is_solved_and_not_sampled():
    """Whether a grid lands on a point is not a property of the curve, so the point is solved for."""
    assert single_point("x**2/4 + y**2/8", ("x", "y")) == (0.0, 0.0)
    assert single_point("2*(x - 3)*(x - 3) + (y + 1)*(y + 1)", ("x", "y")) == (3.0, -1.0)
    assert single_point("x**2 + y**2 - 4", ("x", "y")) is None
    assert single_point("x*y", ("x", "y")) is None


def test_the_figure_of_the_circle_shows_four_panels_and_marks_the_control_world(entries):
    """One SVG per curve, holding every distinct reading side by side."""
    svg, record = curve_figure(entries["circle"], steps=61)
    assert record["object_count"] == 4
    assert svg.startswith("<svg xmlns=") and svg.rstrip().endswith("</svg>")
    assert svg.count("<rect") == 1 + 4  # the background plus one plot ground per panel
    assert "O01 [G0]  9 of 25 worlds" in svg
    assert "conic: circle" in svg and "cubic curve" in svg and "conic: ellipse" in svg
    assert "python -m parseatlas.geometry_atlas figures" in svg


# -------------------------------------------------------------------------------- multicore


def test_the_worker_count_comes_from_the_observed_cores_with_headroom():
    """Never a hardcoded constant, and never all of them."""
    cores = os.cpu_count() or 1
    assert resolve_worker_count(PARALLEL_MINIMUM_ITEMS - 1) == 1
    assert resolve_worker_count(300) == max(1, min(cores - 1, 300))
    assert resolve_worker_count(300) < cores or cores == 1
    assert resolve_worker_count(300, workers=4) == 4


def test_the_sequential_and_parallel_paths_produce_the_same_atlas():
    """Parallelism changes only how fast; this compares the two atlases rather than assuming."""
    measurement = parallelism_measurement(catalogue=SLICE)
    assert measurement["item_count"] == 100
    assert measurement["workers"] > 1, "the slice must be large enough to take the pool path"
    assert measurement["identical_results"] is True
    assert measurement["sequential_seconds"] > 0 and measurement["parallel_seconds"] > 0


def test_the_comparison_used_for_that_check_ignores_timing_but_not_results():
    """The guard on the guard: `_comparable` must not be able to hide a real difference."""
    sequential = atlas(catalogue=SLICE[:1], workers=1)
    parallel = atlas(catalogue=SLICE[:1], workers=1)
    assert _comparable(sequential) == _comparable(parallel)
    parallel["entries"][0]["objects"][0]["resolved_label"] = "conic: parabola"
    assert _comparable(sequential) != _comparable(parallel)


def test_a_grammar_subset_still_produces_a_coherent_atlas():
    """The atlas is not hardwired to 25 worlds; a subset groups and counts the same way."""
    grammars = all_grammars()[:3]
    result = atlas(catalogue=SLICE[:2], grammars=grammars, workers=1)
    assert result["grammar_count"] == 3
    assert result["cell_count"] == 6
    for entry in result["entries"]:
        assert sum(item["grammar_count"] for item in entry["objects"]) == 3


def test_a_curve_declared_outside_the_catalogue_is_read_the_same_way():
    """`curve_in_world` is a public entry point and does not depend on the catalogue."""
    entry = StandardCurve(
        "test_line", "linear", "y - m*x - c", ("x", "y"), (("m", 1), ("c", 1)),
        (-6.0, 6.0, -6.0, 6.0), "a duplicate of the catalogue's line, declared here",
    )
    record = curve_in_world(entry.source, control_grammar(), entry.variables, entry.parameters)
    assert record["label"] == "line"
    assert record["total_degree"] == 1
    assert record["has_cross_term"] is False
    assert record["precedence"] == "*=/ > +=-"
