from parseatlas.precedence_graph import adjacent_swap_edges, analyze_precedence_graph


def test_strict_precedence_graph_has_permutation_edge_count():
    edges = adjacent_swap_edges()
    assert len(edges) == 36
    assert len({(left, right) for left, right, _ in edges}) == 36


def test_precedence_graph_reports_signatures_and_edge_changes():
    result = analyze_precedence_graph(("2*t + 1 - t/2", "(x + 1)/(x - 2)"))
    assert result["grammar_count"] == 24
    assert result["edge_count"] == 36
    assert len(result["grammar_signatures"]) == 24
    assert any(item["changed_expressions"] > 0 for item in result["edges"])
