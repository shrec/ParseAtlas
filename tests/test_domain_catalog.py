from parseatlas.domain_catalog import DOMAINS, build_formula_catalog, catalog_summary


def test_mathematical_domain_catalog_is_balanced():
    catalog = build_formula_catalog()
    assert len(catalog) == 1_000
    assert len({item.id for item in catalog}) == 1_000
    assert {item.domain for item in catalog} == set(DOMAINS)
    assert all(count == 125 for count in catalog_summary()["counts"].values())


def test_catalog_can_scale_without_changing_domain_schema():
    summary = catalog_summary(2)
    assert summary["formula_count"] == 16
    assert summary["domain_count"] == 8
