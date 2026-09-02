from parseatlas.research_benchmark import benchmark_corpus, mine_identities


def test_cross_family_benchmark_reports_all_families():
    result = benchmark_corpus(repetitions=2)
    assert result["expression_count"] == 4
    assert {item["family"] for item in result["results"]} == {"affine", "quadratic", "rational", "nested"}
    assert all(item["canonicalization_to_parse_ratio"] >= 0 for item in result["results"])


def test_identity_miner_finds_all_calibration_identities():
    result = mine_identities()
    assert result["identity_count"] == 4
    assert result["valid_count"] == 4
    assert all(item["residual"] == "0" for item in result["results"])
