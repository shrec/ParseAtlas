from parseatlas.canonical import canonicalize
from parseatlas.grammar import control_grammar, strict_grammars
from parseatlas.parser import Binary, parse


def test_parentheses_override_precedence():
    node = parse("2*(t + 1)", strict_grammars()[0])
    assert isinstance(node, Binary)
    assert node.operator == "*"
    assert canonicalize(node)["expression"] == "2*t + 2"


def test_control_grammar_uses_conventional_shared_levels():
    result = canonicalize(parse("2*t + 1 - t/2", control_grammar()))
    assert result["expression"] == "3*t/2 + 1"


def test_division_restriction_is_retained():
    result = canonicalize(parse("x/x", control_grammar()))
    assert result["expression"] == "1"
    assert result["excluded_points"] == ["0"]
