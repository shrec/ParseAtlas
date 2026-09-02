import pytest

from parseatlas.critical_path import cost_invariance_report, depth_profile, raw_cost_signature
from parseatlas.grammar import all_grammars

CORPUS = (
    "2*t + 1 - t/2",
    "a + b*c - d/e",
    "2*x*x + 1 - x/2",
    "a - b*c + d/e - f",
    "a/b + c*d - e/f + g",
    "(x + 1)/(x - 2)",
)


def test_raw_cost_signature_excludes_depth_and_counts_operator_tokens():
    signature = raw_cost_signature("2*t + 1 - t/2", all_grammars()[0])
    assert dict(signature) == {"add": 1, "sub": 1, "mul": 1, "div": 1, "nodes": 9}
    assert "depth" not in dict(signature)


def test_every_corpus_expression_shares_one_raw_signature_across_all_grammars():
    assert len(all_grammars()) == 25
    for source in CORPUS:
        signatures = {raw_cost_signature(source, grammar) for grammar in all_grammars()}
        assert len(signatures) == 1


def test_affine_baseline_depth_spread_is_positive():
    profile = depth_profile("2*t + 1 - t/2")
    assert profile["grammar_count"] == 25
    assert profile["depth_spread"] > 0
    assert profile["min_depth"] == 4
    assert profile["max_depth"] == 5


def test_min_depth_grammars_are_non_empty_and_reach_min_depth():
    for source in CORPUS:
        profile = depth_profile(source)
        depths = {entry["id"]: entry["depth"] for entry in profile["grammars"]}
        assert profile["min_depth_grammars"]
        assert all(depths[grammar_id] == profile["min_depth"] for grammar_id in profile["min_depth_grammars"])
        assert all(depths[grammar_id] == profile["max_depth"] for grammar_id in profile["max_depth_grammars"])


def test_control_grammar_is_non_minimal_on_three_of_the_six_corpus_expressions():
    measured = [depth_profile(source)["control_is_minimal"] for source in CORPUS]
    assert measured == [True, True, False, False, False, True]
    assert measured.count(False) == 3


def test_conventional_precedence_loses_by_one_level_on_the_four_operator_chain():
    profile = depth_profile("a/b + c*d - e/f + g")
    assert dict(profile["grammars"][0]["raw_signature"]) == {"add": 2, "sub": 1, "mul": 1, "div": 2, "nodes": 13}
    assert sorted({entry["depth"] for entry in profile["grammars"]}) == [4, 5, 6]
    assert profile["control_depth"] == 5
    assert profile["min_depth_grammars"] == ["G02", "G08", "G17", "G23"]


def test_raw_signature_invariance_holds_over_the_whole_corpus():
    result = cost_invariance_report(CORPUS)
    assert result["expression_count"] == 6
    assert result["grammar_count"] == 25
    assert result["all_raw_signatures_invariant"] is True
    assert all(item["distinct_raw_signatures"] == 1 for item in result["expressions"])


def test_empty_corpus_is_rejected_instead_of_reporting_vacuous_invariance():
    with pytest.raises(ValueError, match="at least one expression"):
        cost_invariance_report(())
    with pytest.raises(ValueError, match="at least one expression"):
        cost_invariance_report(iter([]))


def test_canonical_cost_is_not_invariant_although_the_raw_multiset_is():
    result = cost_invariance_report(CORPUS)
    varying = [item for item in result["expressions"] if item["canonical_cost"]["distinct"] > 1]
    assert varying
    assert any(item["expression"] == "2*t + 1 - t/2" for item in varying)
    assert result["max_depth_spread"] == 2
