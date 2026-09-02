from os import cpu_count

from parseatlas.ast_space import (
    _resolve_workers,
    control_only_pattern_sweep,
    coverage_report,
    enumerate_parenthesizations,
    operator_pattern_sweep,
    reachable_asts,
)


def test_enumeration_matches_catalan_numbers():
    assert len(enumerate_parenthesizations("abcd", "+-*")) == 5
    assert len(enumerate_parenthesizations("abcde", "+-*/")) == 14
    assert len(set(enumerate_parenthesizations("abcde", "+-*/"))) == 14


def test_reachable_asts_are_enumerated_parenthesizations():
    reachable = reachable_asts("a + b*c - d/e")
    assert set(reachable["all"]).issubset(set(enumerate_parenthesizations("abcde", "+*-/")))
    assert reachable["control"] in set(reachable["all"])


def test_five_leaves_with_four_distinct_operators_reach_every_tree():
    record = coverage_report(("a + b*c - d/e",))["expressions"][0]
    assert record["catalan_total"] == 14
    assert record["strict_reachable"] == 14
    assert record["strict_coverage"] == 1.0


def test_control_grammar_reaches_a_tree_no_strict_ordering_reaches():
    record = coverage_report(("a - b*c + d/e - f",))["expressions"][0]
    assert record["catalan_total"] == 42
    assert record["strict_coverage"] < 1.0
    assert record["strict_reachable"] == 19
    assert record["all_reachable"] == 20
    control_only_tree = ("-", ("+", ("-", "a", ("*", "b", "c")), ("/", "d", "e")), "f")
    assert record["control_only_trees"] == (control_only_tree,)


def test_mean_coverage_decreases_from_two_to_three_operators():
    levels = operator_pattern_sweep(max_operators=3, workers=1)["levels"]
    assert [item["pattern_count"] for item in levels] == [16, 64]
    assert levels[1]["mean_coverage"] < levels[0]["mean_coverage"]
    assert levels[1]["full_coverage_fraction"] < levels[0]["full_coverage_fraction"]


def test_sequential_and_parallel_sweeps_are_identical():
    assert operator_pattern_sweep(max_operators=3, workers=1) == operator_pattern_sweep(max_operators=3, workers=2)


def test_default_worker_count_is_the_measured_faster_sequential_path():
    assert _resolve_workers(None) == 1
    assert _resolve_workers(0) == max((cpu_count() or 1) - 1, 1)
    assert _resolve_workers(4) == 4


def test_control_only_pattern_counts_grow_with_operator_count():
    levels = control_only_pattern_sweep(max_operators=4, workers=1)["levels"]
    assert [item["pattern_count"] for item in levels] == [16, 64, 256]
    assert [item["control_only_patterns"] for item in levels] == [0, 4, 40]
    assert [item["control_only_fraction"] for item in levels] == [0.0, 0.0625, 0.15625]


def test_control_only_sweep_agrees_with_the_coverage_sweep():
    control_only = control_only_pattern_sweep(max_operators=3, workers=1)["levels"]
    coverage = operator_pattern_sweep(max_operators=3, workers=1)["levels"]
    for control_level, coverage_level in zip(control_only, coverage, strict=True):
        gap = coverage_level["mean_coverage"] - coverage_level["mean_strict_coverage"]
        assert (gap > 0) == (control_level["control_only_patterns"] > 0)
