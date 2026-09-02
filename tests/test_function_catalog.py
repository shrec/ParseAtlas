from parseatlas.function_catalog import build_catalog
from parseatlas.ten_thousand import run_catalog


def test_function_catalog_contains_exactly_10000_specs():
    catalog = build_catalog()
    assert len(catalog) == 10_000
    assert len({spec.id for spec in catalog}) == 10_000
    assert {spec.family for spec in catalog} == {
        "absolute", "affine", "cosine", "exponential", "logarithm",
        "power", "reciprocal", "root", "scaled_power", "sine",
    }


def test_catalog_runner_uses_all_25_grammars():
    report = run_catalog(build_catalog()[:20])
    assert report["function_count"] == 20
    assert report["grammar_count"] == 25
    assert report["total_results"] == 500
