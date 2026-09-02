from parseatlas.functions import analyze_outer_functions


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
