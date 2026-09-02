"""Experiment 0024 tests.

Every test runs on a small explicit sub-corpus: the published 3125-expression corpus is a report
artefact, not a unit-test fixture.
"""

import os

import pytest

from parseatlas.analyze import analyze_expression
from parseatlas.corpus_matrix import (
    COEFFICIENT_VALUES,
    FAMILY_TEMPLATES,
    GRAMMAR_IDS,
    PARALLEL_MINIMUM_ITEMS,
    RESTRICTION_PROBE_TEMPLATES,
    always_agree_partition,
    cluster_stability,
    corpus_matrix,
    corpus_records,
    diversity_report,
    expression_classes,
    generate_corpus,
    grammar_clusters,
    key_discrimination_report,
    profile_distance,
    resolve_worker_count,
    restricted_levels,
    restriction_probe_corpus,
    rigidity_classification,
    support_forced_blocks,
)
from parseatlas.grammar import all_grammars, control_grammar

# One representative of every family, taken from the published corpus with (a, b, c, d) = (2, 3, 4, 5).
SUB_CORPUS = (
    {"index": 0, "family": "linear", "source": "2*x + 3 - 4*x/5"},
    {"index": 1, "family": "quadratic", "source": "2*x*x + 3*x - 4/5"},
    {"index": 2, "family": "cubic", "source": "2*x*x*x + 3*x*x - 4*x + 5"},
    {"index": 3, "family": "rational", "source": "(2*x + 3)/(4*x - 5)"},
    {"index": 4, "family": "mixed_chain", "source": "2/3 + 4*x - 5/2"},
)

RIGID_RATIONAL = "(x + 1)/(x - 2)"
AFFINE = "2*t + 1 - t/2"


@pytest.fixture(scope="module")
def sub_corpus_records():
    return corpus_records(SUB_CORPUS, workers=1)["records"]


@pytest.fixture(scope="module")
def sub_corpus_matrix(sub_corpus_records):
    return corpus_matrix(SUB_CORPUS, records=sub_corpus_records)


# ---------------------------------------------------------------------------------- generation


def test_generate_corpus_is_deterministic():
    first = generate_corpus()
    second = generate_corpus()
    assert first == second
    assert first["expressions"] == second["expressions"]


def test_generated_corpus_size_and_family_balance_match_the_documented_parameters():
    corpus = generate_corpus()
    per_family = len(COEFFICIENT_VALUES) ** 4
    assert per_family == 625
    assert corpus["size"] == per_family * len(FAMILY_TEMPLATES) == 3125
    assert corpus["family_counts"] == {family: per_family for family, _ in FAMILY_TEMPLATES}
    assert corpus["families"] == tuple(family for family, _ in FAMILY_TEMPLATES)
    assert corpus["generation"]["coefficient_values"] == COEFFICIENT_VALUES
    assert corpus["generation"]["randomness"].startswith("none")
    assert len({item["source"] for item in corpus["expressions"]}) == 3125


def test_generated_sources_come_from_the_declared_templates():
    corpus = generate_corpus()
    templates = dict(FAMILY_TEMPLATES)
    for item in corpus["expressions"][:50]:
        assert item["source"] == templates[item["family"]].format(**item["parameters"])


# ------------------------------------------------------------------ correctness bridge to analyze


@pytest.mark.parametrize(
    "source",
    ["2*x + 3 - 4*x/5", "2*x*x + 3*x - 4/5", "(2*x + 3)/(4*x - 5)", RIGID_RATIONAL],
)
def test_deduplicated_pipeline_reproduces_analyze_expression(source):
    fast = expression_classes(source)
    reference = analyze_expression(source)
    expected = {item["id"]: item["equivalence_class"] for item in reference["grammars"]}
    assert fast["classes"] == expected
    assert fast["distinct_class_count"] == len(reference["equivalence_classes"])
    assert fast["distinct_ast_count"] == len({str(item["ast"]) for item in reference["grammars"]})


def test_deduplication_canonicalizes_fewer_asts_than_grammars():
    fast = expression_classes("2*x + 3 - 4*x/5")
    assert fast["canonicalizations"] == fast["distinct_ast_count"] < len(GRAMMAR_IDS)
    assert fast["distinct_class_count"] <= fast["distinct_ast_count"]


def test_semantic_class_key_keeps_domain_and_excluded_points():
    fast = expression_classes("x/x")
    keys = fast["class_keys"]
    assert all(entry["domain"] == "R" for entry in keys.values())
    assert any(entry["excluded_points"] for entry in keys.values())


# ------------------------------------------------------------------------- restriction probe


def test_restriction_probe_corpus_is_deterministic_and_labelled():
    first = restriction_probe_corpus()
    second = restriction_probe_corpus()
    assert first == second
    assert first["size"] == len(RESTRICTION_PROBE_TEMPLATES) == 10
    assert set(first["families"]) == {"point_pair", "restricted_vs_free", "control_no_split"}
    assert first["generation"]["randomness"].startswith("none")
    assert len({item["source"] for item in first["expressions"]}) == first["size"]


@pytest.mark.parametrize(
    ("source", "excluded"),
    [
        ("1 - x / x - 1", {("0",), ("1",)}),  # both parses restricted, at different points
        ("2 - x / x - 2", {("0",), ("2",)}),
        ("x - 1 / 1 - x", {(), ("1",)}),  # one parse restricted, the other not
        ("x / x - 1 - x", {(), ("0",)}),
    ],
)
def test_excluded_points_split_classes_that_share_one_canonical_text(source, excluded):
    """Without the excluded points in the key these classes would be merged into one."""
    fast = expression_classes(source)
    keys = fast["class_keys"]
    assert fast["distinct_class_count"] == 2
    assert len({entry["canonical"] for entry in keys.values()}) == 1
    assert {tuple(entry["excluded_points"]) for entry in keys.values()} == excluded


def test_the_restriction_key_does_real_work_on_the_probe_and_none_on_the_template_corpus():
    probe = key_discrimination_report(restriction_probe_corpus(), workers=1)["overall"]
    assert probe["expression_count"] == 10
    assert probe["expressions_where_the_restriction_key_splits_a_class"] == 8
    assert probe["classes_lost_without_the_restriction_key"] == 8
    assert probe["classes"] - probe["canonical_texts"] == 8
    template = key_discrimination_report(SUB_CORPUS, workers=1)["overall"]
    assert template["classes_lost_without_the_restriction_key"] == 0


def test_the_two_control_probe_items_carry_a_restriction_without_splitting_anything():
    report = key_discrimination_report(restriction_probe_corpus(), workers=1)
    control = report["families"]["control_no_split"]
    assert control["expression_count"] == 2
    assert control["expressions_with_a_restricted_class"] == 2
    assert control["expressions_where_the_restriction_key_splits_a_class"] == 0
    assert control["classes_lost_without_the_restriction_key"] == 0


def test_the_domain_component_of_the_key_can_never_discriminate_today():
    """canonicalize() returns domain 'R' unconditionally, so only excluded points can split."""
    report = key_discrimination_report(restriction_probe_corpus(), workers=1)
    assert report["overall"]["domain_values"] == ("R",)


# ------------------------------------------------------------------------------------- matrices


def test_matrix_is_25_by_25_with_unit_diagonal_and_symmetry(sub_corpus_matrix):
    matrix = sub_corpus_matrix["matrix"]
    assert sub_corpus_matrix["expression_count"] == len(SUB_CORPUS)
    assert sub_corpus_matrix["grammar_count"] == 25
    assert len(matrix) == 25
    assert all(len(row) == 25 for row in matrix.values())
    assert all(matrix[grammar][grammar] == 1.0 for grammar in GRAMMAR_IDS)
    assert all(matrix[left][right] == matrix[right][left] for left in GRAMMAR_IDS for right in GRAMMAR_IDS)


def test_per_family_matrices_cover_the_corpus(sub_corpus_matrix):
    assert set(sub_corpus_matrix["families"]) == {item["family"] for item in SUB_CORPUS}
    assert sum(sub_corpus_matrix["family_counts"].values()) == len(SUB_CORPUS)
    for block in sub_corpus_matrix["families"].values():
        assert all(block["matrix"][grammar][grammar] == 1.0 for grammar in GRAMMAR_IDS)


def test_rigid_rational_puts_every_grammar_pair_in_one_class():
    matrix = corpus_matrix([RIGID_RATIONAL], workers=1)
    assert all(
        matrix["matrix"][left][right] == 1.0 for left in GRAMMAR_IDS for right in GRAMMAR_IDS
    )
    assert matrix["records"][0]["distinct_class_count"] == 1


def test_affine_expression_makes_at_least_one_grammar_pair_disagree():
    matrix = corpus_matrix([AFFINE], workers=1)
    disagreeing = [
        (left, right)
        for left in GRAMMAR_IDS
        for right in GRAMMAR_IDS
        if matrix["matrix"][left][right] < 1.0
    ]
    assert disagreeing
    assert matrix["records"][0]["distinct_class_count"] > 1


# ------------------------------------------------------------------------------ null model gate


def test_support_forced_blocks_agree_with_the_restricted_precedence_levels():
    blocks = support_forced_blocks(AFFINE)
    assert len(blocks) == 25
    assert len(set(blocks.values())) == 25  # full support: 24 singleton strict blocks plus G0
    control_blocks = support_forced_blocks("2*x*x + 3*x - 4/5")
    assert restricted_levels(control_grammar(), ("*", "+", "-")) == (("*",), ("+", "-"))
    assert len(set(control_blocks.values())) == 7  # 3! strict blocks plus the tied control level


def test_support_forced_null_never_exceeds_the_observed_matrix(sub_corpus_matrix):
    for left in GRAMMAR_IDS:
        for right in GRAMMAR_IDS:
            forced = sub_corpus_matrix["support_forced_counts"][left][right]
            observed = sub_corpus_matrix["equal_counts"][left][right]
            assert forced <= observed, (left, right, forced, observed)


def test_excess_matrix_is_non_negative_and_equals_observed_minus_null(sub_corpus_matrix):
    for left in GRAMMAR_IDS:
        for right in GRAMMAR_IDS:
            excess = sub_corpus_matrix["excess_matrix"][left][right]
            assert excess >= 0.0, (left, right, excess)
            assert excess == pytest.approx(
                sub_corpus_matrix["matrix"][left][right]
                - sub_corpus_matrix["support_forced_matrix"][left][right]
            )


def test_ast_identity_null_sits_between_the_support_null_and_the_observed_matrix(sub_corpus_matrix):
    for left in GRAMMAR_IDS:
        for right in GRAMMAR_IDS:
            forced = sub_corpus_matrix["support_forced_matrix"][left][right]
            identical = sub_corpus_matrix["ast_identity_matrix"][left][right]
            observed = sub_corpus_matrix["matrix"][left][right]
            assert forced <= identical <= observed, (left, right)


# -------------------------------------------------------------------------------------- clusters


def test_profile_distance_drops_both_self_agreement_columns():
    values = {
        "A": {"A": 1.0, "B": 0.5, "C": 0.25},
        "B": {"A": 0.5, "B": 1.0, "C": 0.75},
        "C": {"A": 0.25, "B": 0.75, "C": 1.0},
    }
    ids = ("A", "B", "C")
    # only column C survives, so the distance is exactly |0.25 - 0.75|
    assert profile_distance(values, ids, "A", "B") == pytest.approx(0.5)
    assert profile_distance(values, ids, "A", "B") == profile_distance(values, ids, "B", "A")
    assert profile_distance(values, ids, "A", "A") == 0.0


def test_identical_off_diagonal_profiles_group_together_despite_the_diagonal():
    """Regression: the excess diagonal is 0.0 while every other cell is an agreement fraction.

    ``A`` and ``B`` have the same agreement with everything outside the pair, so they must be one
    group. Comparing the raw rows instead would put them at L2 distance ``sqrt(2)`` and split them.
    """
    values = {
        "A": {"A": 0.0, "B": 1.0, "C": 0.5},
        "B": {"A": 1.0, "B": 0.0, "C": 0.5},
        "C": {"A": 0.5, "B": 0.5, "C": 0.0},
    }
    clusters = grammar_clusters(values, threshold=0.0)
    assert clusters["clusters"] == (("A", "B"), ("C",))
    assert clusters["identical_signature_groups"] == (("A", "B"), ("C",))


def test_cluster_signatures_exclude_the_grammar_s_own_column(sub_corpus_matrix):
    assert all(sub_corpus_matrix["matrix"][g][g] == 1.0 for g in GRAMMAR_IDS)
    assert all(sub_corpus_matrix["excess_matrix"][g][g] == 0.0 for g in GRAMMAR_IDS)
    clusters = grammar_clusters(sub_corpus_matrix)
    assert clusters["diagonal_policy"].startswith("excluded")
    for grammar_id in GRAMMAR_IDS:
        assert grammar_id not in clusters["matrix_row_columns"][grammar_id]
        assert len(clusters["matrix_row_columns"][grammar_id]) == 24
        # the display row drops ONE column, the grammar's own
        assert len(clusters["matrix_rows_without_self"][grammar_id]) == 24
        assert clusters["matrix_rows"][grammar_id] == sub_corpus_matrix["excess_matrix"][grammar_id]
        assert clusters["distance_matrix"][grammar_id][grammar_id] == 0.0
        # the measured vector drops TWO columns, the grammar's own and its partner's
        for other in GRAMMAR_IDS:
            if other != grammar_id:
                assert len(clusters["comparable_signatures"][grammar_id][other]) == 23


def test_published_comparable_signatures_reproduce_the_identical_profile_groups(sub_corpus_matrix):
    """The published vector must be the vector the distance uses, or the groups are unverifiable.

    ``matrix_rows_without_self`` drops only the grammar's own column, so a member of an
    identical-profile group still carries its partner's column and the two rows are not equal - for
    some groups here they genuinely differ. ``comparable_signatures[left][right]`` is the
    `23`-coordinate vector ``profile_distance`` consumes; equality of the two orderings is exactly
    the grouping rule, so a consumer can rebuild ``identical_signature_groups`` from what is
    published and get the published answer back.
    """
    clusters = grammar_clusters(sub_corpus_matrix)
    comparable = clusters["comparable_signatures"]
    groups = clusters["identical_signature_groups"]

    multi = [group for group in groups if len(group) > 1]
    assert multi, "the fixture must have a non-singleton group or this test asserts nothing"
    for group in multi:
        for left in group:
            for right in group:
                if left != right:
                    assert comparable[left][right] == comparable[right][left]

    # the defect this locks out: the 24-coordinate display row does NOT have that property
    assert any(
        clusters["matrix_rows_without_self"][group[0]] != clusters["matrix_rows_without_self"][group[1]]
        for group in multi
    )

    rebuilt: list[list[str]] = []
    for grammar_id in clusters["grammar_ids"]:
        for group in rebuilt:
            if comparable[group[0]][grammar_id] == comparable[grammar_id][group[0]]:
                group.append(grammar_id)
                break
        else:
            rebuilt.append([grammar_id])
    assert tuple(tuple(group) for group in rebuilt) == groups
    # sizes of THIS fixture, and the invariant a hand-written group-size list must satisfy: the
    # groups are a partition of the 25 grammars, so the sizes sum to 25 and never to more
    assert sorted((len(group) for group in groups), reverse=True) == [4, 4, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1]
    assert sum(len(group) for group in groups) == len(GRAMMAR_IDS) == 25


def test_grammars_that_agree_on_every_expression_are_never_split_by_their_own_columns():
    """A pair with observed agreement 1.0 everywhere has profile distance 0 and cannot be separated."""
    matrix = corpus_matrix([RIGID_RATIONAL], workers=1)
    clusters = grammar_clusters(matrix, signature_key="matrix")
    assert clusters["clusters"] == (tuple(GRAMMAR_IDS),)
    assert clusters["max_distance"] == 0.0


def test_clusters_are_deterministic_across_repeated_runs(sub_corpus_matrix):
    first = grammar_clusters(sub_corpus_matrix)
    second = grammar_clusters(sub_corpus_matrix)
    assert first["clusters"] == second["clusters"]
    assert first["threshold"] == second["threshold"]
    assert sorted(grammar for cluster in first["clusters"] for grammar in cluster) == sorted(GRAMMAR_IDS)


def test_clusters_partition_every_grammar_exactly_once(sub_corpus_matrix):
    clusters = grammar_clusters(sub_corpus_matrix)
    flattened = [grammar for cluster in clusters["clusters"] for grammar in cluster]
    assert len(flattened) == len(set(flattened)) == 25
    assert clusters["cluster_count"] == len(clusters["clusters"])
    assert sum(clusters["cluster_sizes"]) == 25


def test_zero_threshold_keeps_only_identical_signature_groups(sub_corpus_matrix):
    clusters = grammar_clusters(sub_corpus_matrix, threshold=0.0)
    assert clusters["clusters"] == clusters["identical_signature_groups"]


def test_always_agree_partition_is_a_partition_and_follows_the_matrix(sub_corpus_matrix):
    partition = sub_corpus_matrix["always_agree_partition"]
    flattened = [grammar for group in partition for grammar in group]
    assert sorted(flattened) == sorted(GRAMMAR_IDS)
    for group in partition:
        for left in group:
            for right in group:
                assert sub_corpus_matrix["matrix"][left][right] == 1.0
    for left_group in partition:
        for right_group in partition:
            if left_group is not right_group:
                assert sub_corpus_matrix["matrix"][left_group[0]][right_group[0]] < 1.0


def test_rigid_rational_puts_all_grammars_in_one_always_agree_group():
    matrix = corpus_matrix([RIGID_RATIONAL], workers=1)
    assert matrix["always_agree_partition"] == (tuple(GRAMMAR_IDS),)


def test_clusters_can_be_recomputed_from_the_observed_matrix(sub_corpus_matrix):
    excess = grammar_clusters(sub_corpus_matrix)
    observed = grammar_clusters(sub_corpus_matrix, signature_key="matrix")
    assert excess["signature_source"] == "excess_matrix"
    assert observed["signature_source"] == "matrix"
    assert sorted(g for c in observed["clusters"] for g in c) == sorted(GRAMMAR_IDS)


def test_cluster_stability_reports_a_pair_agreement_score(sub_corpus_records):
    stability = cluster_stability(SUB_CORPUS, records=sub_corpus_records)
    assert stability["pair_count"] == 300
    assert 0.0 <= stability["pair_agreement"] <= 1.0
    assert stability["matching_pairs"] == pytest.approx(stability["pair_agreement"] * 300)
    assert stability["halves"]["even"]["expression_count"] == 3
    assert stability["halves"]["odd"]["expression_count"] == 2
    assert stability["signature_key"] == "excess_matrix"


def test_cluster_stability_can_run_on_the_observed_matrix(sub_corpus_records):
    stability = cluster_stability(SUB_CORPUS, records=sub_corpus_records, signature_key="matrix")
    assert stability["signature_key"] == "matrix"
    assert stability["pair_count"] == 300
    assert 0.0 <= stability["pair_agreement"] <= 1.0


# ------------------------------------------------------------------------- diversity / rigidity


def test_diversity_report_separates_ast_diversity_from_semantic_diversity(sub_corpus_records):
    report = diversity_report(SUB_CORPUS, records=sub_corpus_records)
    assert report["overall"]["expression_count"] == 5
    assert set(report["families"]) == {item["family"] for item in SUB_CORPUS}
    assert sum(report["overall"]["ast_diversity_distribution"].values()) == 5
    assert sum(report["overall"]["class_count_distribution"].values()) == 5
    assert report["overall"]["cross_tab"]


def test_rigidity_classification_reuses_representation_sensitivity():
    report = rigidity_classification([("affine", AFFINE), ("rational", RIGID_RATIONAL)], workers=1)
    assert report["overall"]["expression_count"] == 2
    assert report["families"]["affine"]["sensitive"] == 1
    assert report["families"]["affine"]["mean_sensitivity"] == pytest.approx(7 / 23)
    assert report["families"]["rational"]["rigid"] == 1
    assert report["families"]["rational"]["mean_sensitivity"] == 0.0
    assert report["overall"]["rigid"] + report["overall"]["sensitive"] == 2


# ---------------------------------------------------------------------------------- parallelism


def test_worker_count_is_derived_from_the_core_count_with_headroom(monkeypatch):
    monkeypatch.setattr("parseatlas.corpus_matrix.os.cpu_count", lambda: 16)
    assert resolve_worker_count(4096) == 15
    assert resolve_worker_count(4) == 1  # below PARALLEL_MINIMUM_ITEMS the auto path stays sequential
    assert resolve_worker_count(4096, workers=1) == 1
    assert resolve_worker_count(4096, workers=3) == 3


def test_sequential_and_parallel_runs_produce_identical_results():
    """The comparison corpus is large enough that the AUTOMATIC worker choice goes parallel.

    ``5`` expressions would only ever exercise a forced ``workers=2``; the report's claim is about
    the default path, so the corpus here clears ``PARALLEL_MINIMUM_ITEMS``. The rational template is
    used because it is the cheapest of the five (4 distinct ASTs per expression).
    """
    if (os.cpu_count() or 1) < 2:
        pytest.skip("a single-core machine has no parallel branch to take")
    corpus = generate_corpus(values=(1, 2, 3), templates=FAMILY_TEMPLATES[3:4])
    assert corpus["size"] == 81 >= PARALLEL_MINIMUM_ITEMS
    parallel = corpus_matrix(corpus)
    sequential = corpus_matrix(corpus, workers=1)
    assert sequential["workers"] == 1
    assert parallel["workers"] == resolve_worker_count(corpus["size"]) > 1
    assert parallel["records"] == sequential["records"]
    assert parallel["matrix"] == sequential["matrix"]
    assert parallel["excess_matrix"] == sequential["excess_matrix"]
    assert parallel["always_agree_partition"] == sequential["always_agree_partition"]
    assert grammar_clusters(parallel)["clusters"] == grammar_clusters(sequential)["clusters"]
    assert (
        grammar_clusters(parallel)["distance_matrix"] == grammar_clusters(sequential)["distance_matrix"]
    )


def test_grammar_ids_cover_the_control_and_the_twenty_four_strict_grammars():
    assert GRAMMAR_IDS == tuple(grammar.id for grammar in all_grammars())
    assert GRAMMAR_IDS[0] == "G0"
    assert len(GRAMMAR_IDS) == 25
