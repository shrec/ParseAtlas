from parseatlas.analyze import analyze_expression


EXPECTED_CLASSES = {
    "1": ["G01", "G02", "G07", "G08"],
    "t/2 + 1": ["G03"],
    "3*t/2 + 2": ["G04", "G06", "G20"],
    "t + 2": ["G05", "G19", "G21"],
    "t/2 + 1/2": ["G09", "G13", "G15"],
    "3*t/2 + 1/2": ["G10", "G12", "G16"],
    "t + 1": ["G11"],
    "3*t/2 + 1": ["G14", "G17", "G18", "G22", "G23", "G24"],
}


def test_initial_findings_reproduce_strict_24_to_8_result():
    report = analyze_expression("2*t + 1 - t/2")
    strict_results = [item for item in report["grammars"] if item["id"] != "G0"]
    assert len(strict_results) == 24
    assert len(report["equivalence_classes"]) == 8

    actual = {
        item["canonical"]: [grammar for grammar in item["grammars"] if grammar != "G0"]
        for item in report["equivalence_classes"]
    }
    assert actual == EXPECTED_CLASSES


def test_control_result_is_reported_separately():
    report = analyze_expression("2*t + 1 - t/2")
    assert report["control"]["id"] == "G0"
    assert report["control"]["canonical"] == "3*t/2 + 1"
