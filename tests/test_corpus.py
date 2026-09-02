from parseatlas.corpus import DEFAULT_CORPUS, run_corpus


def test_controlled_corpus_reports_all_expressions():
    report = run_corpus()
    assert report["experiment_count"] == len(DEFAULT_CORPUS)
    assert all(item["grammar_count"] == 25 for item in report["experiments"])
    assert all(item["ast_form_count"] >= item["semantic_class_count"] for item in report["experiments"])


def test_corpus_exposes_rational_poles():
    report = run_corpus((("rational", "(x + 1)/(x - 2)"),))
    assert report["experiments"][0]["poles"] == ["2"]
