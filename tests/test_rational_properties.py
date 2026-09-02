from parseatlas.analyze import analyze_expression


def test_rational_properties_identify_poles_and_zeros():
    report = analyze_expression("(x + 1)/(x - 2)")
    control = report["control"]["properties"]
    assert control["is_rational"] is True
    assert control["zeros"] == ["-1"]
    assert control["poles"] == ["2"]
    assert control["removable_restrictions"] == []


def test_rational_properties_preserve_removable_restrictions():
    report = analyze_expression("(x*x - 1)/(x - 1)")
    control = report["control"]["properties"]
    assert control["denominator"] == "1"
    assert control["removable_restrictions"] == ["1"]
    assert control["poles"] == []
