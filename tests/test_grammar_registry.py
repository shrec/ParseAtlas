from parseatlas.grammar import all_grammars, control_grammar, strict_grammars


def test_registry_has_control_and_24_strict_grammars():
    assert control_grammar().id == "G0"
    assert len(strict_grammars()) == 24
    assert len(all_grammars()) == 25
    assert [grammar.id for grammar in strict_grammars()] == [f"G{index:02d}" for index in range(1, 25)]


def test_control_grammar_groups_conventional_operator_levels():
    grammar = control_grammar()
    assert grammar.levels == (("*", "/"), ("+", "-"))
