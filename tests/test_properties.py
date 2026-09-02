from parseatlas.analyze import analyze_expression


def test_quadratic_properties_are_extracted_from_canonical_form():
    report = analyze_expression("2*x*x + 1 - x/2")
    control = report["control"]["properties"]
    assert control["is_polynomial"] is True
    assert control["degree"] == 2
    assert control["discriminant"] == "-31/4"
    assert control["vertex"] == {"x": "1/8", "y": "31/32"}


def test_grammar_can_collapse_quadratic_token_sequence_to_linear_form():
    report = analyze_expression("2*x*x + 1 - x/2")
    collapsed = next(item for item in report["grammars"] if item["id"] == "G01")
    assert collapsed["canonical"] == "x"
    assert collapsed["properties"]["degree"] == 1
