"""Experiment 0031 tests.

Every test that can runs on a small explicit sub-corpus: the published `1_048_576`-expression
structural corpus and the `104_976`-expression semantic corpus are report artefacts, not unit-test
fixtures. Two deliberate exceptions: the 0024 calibration, which has to run on 0024's own
`3125`-expression corpus because a subset would compare against a distribution nobody published;
and ``test_the_founding_token_stream_is_not_in_the_corpus``, because "this string is not in the
corpus" is a claim about all `104_976` of them (it only formats sources and parses nothing).
"""

import os
from collections import Counter
from math import factorial

import pytest
from sympy import sympify

from parseatlas.analyze import analyze_expression
from parseatlas.corpus_matrix import COEFFICIENT_VALUES, expression_classes
from parseatlas.grammar import all_grammars
from parseatlas.parser import parse
from parseatlas.scale_atlas import (
    CALIBRATION_CLASS_DISTRIBUTION,
    FAMILY_TEMPLATES,
    PARAMETER_NAMES,
    SATURATING_DIV_FAMILIES,
    CorpusSpec,
    _division_count,
    _mode,
    _plan,
    calibration_report,
    collapse_report,
    distribution_report,
    generate_corpus,
    semantic_record,
    semantic_spec,
    semantic_sweep,
    structural_record,
    structural_spec,
    structural_sweep,
)

#: 64 expressions over four families - enough for every structural claim, small enough to stay fast.
SMALL_SPEC = CorpusSpec(values_count=2, templates=FAMILY_TEMPLATES[:4])

#: 32 expressions - used only where a process pool has to be started.
TINY_SPEC = CorpusSpec(values_count=2, templates=FAMILY_TEMPLATES[:2])

#: One representative of each of the sixteen families, at (a, b, c, d) = (2, 3, 4, 5).
FAMILY_REPRESENTATIVES = tuple(
    {
        "index": position,
        "family": family,
        "source": template.format(**dict(zip(PARAMETER_NAMES, (2, 3, 4, 5)))),
    }
    for position, (family, template, _) in enumerate(FAMILY_TEMPLATES)
)

#: Families whose representative is cross-checked against ``analyze_expression`` itself. Six rather
#: than sixteen because ``analyze_expression`` runs ``factor``/``solve`` for all 25 grammars, which
#: costs seconds per expression on the long chains; the partition it verifies is the same one.
CROSS_CHECKED_FAMILIES = (
    "affine",
    "affine_div",
    "quadratic",
    "rational",
    "mixed_chain_spaced",
    "repeated_variable",
)

#: The founding observation of the project, pinned so the headline of the report cannot drift.
FOUNDING_EXPRESSION = "2*t + 1 - t/2"

#: The nearest ``affine_div`` member to the founding token stream: the SAME shape, with the implicit
#: unit coefficient of ``t/2`` written out as ``1*x/2``. The corpus contains this one and not the
#: founding one, and the two are structurally different - see the two tests below.
NEAREST_FAMILY_MEMBER = "2*x + 1 - 1*x/2"


@pytest.fixture(scope="module")
def small_semantic_records():
    return semantic_sweep(SMALL_SPEC, workers=1)["records"]


@pytest.fixture(scope="module")
def family_records():
    return tuple(semantic_record(item) for item in FAMILY_REPRESENTATIVES)


def _partition(classes):
    """Membership only: which grammars share a class, with the class LABELS thrown away."""
    groups = {}
    for grammar_id, class_id in classes.items():
        groups.setdefault(class_id, set()).add(grammar_id)
    return frozenset(frozenset(members) for members in groups.values())


# ---------------------------------------------------------------------------------- generation


def test_generator_is_deterministic_across_two_calls():
    first = generate_corpus(SMALL_SPEC)
    second = generate_corpus(SMALL_SPEC)
    assert first["expressions"] == second["expressions"]
    assert first["generation"] == second["generation"]


def test_index_addressing_matches_the_materialized_corpus():
    corpus = generate_corpus(SMALL_SPEC)
    assert tuple(SMALL_SPEC.expression(index) for index in range(SMALL_SPEC.size)) == corpus["expressions"]


def test_families_are_interleaved_inside_every_coefficient_tuple():
    corpus = generate_corpus(SMALL_SPEC)
    families = [item["family"] for item in corpus["expressions"][: SMALL_SPEC.family_count]]
    assert tuple(families) == SMALL_SPEC.families
    assert corpus["family_counts"] == {family: SMALL_SPEC.expressions_per_family for family in SMALL_SPEC.families}


def test_generation_block_rebuilds_the_same_sources():
    """The corpus must regenerate from the published report alone."""
    generation = SMALL_SPEC.generation()
    rebuilt = CorpusSpec(
        values_count=generation["values_count"],
        templates=tuple(
            (family, generation["templates"][family], tuple(generation["slot_kinds"][family]))
            for family in generation["templates"]
        ),
        free_values=tuple(generation["free_values"]),
        nonzero_values=tuple(generation["nonzero_values"]),
    )
    assert generate_corpus(rebuilt)["expressions"] == generate_corpus(SMALL_SPEC)["expressions"]


def test_spec_rejects_a_values_count_beyond_the_value_sequences():
    with pytest.raises(ValueError):
        CorpusSpec(values_count=99)
    with pytest.raises(ValueError):
        CorpusSpec(values_count=0)


def test_every_generated_source_parses_under_every_grammar():
    """A zero in a ``nonzero`` slot would be a tokenizer error, not a measurement."""
    grammars = all_grammars()
    for item in generate_corpus(SMALL_SPEC)["expressions"]:
        for grammar in grammars:
            parse(item["source"], grammar)


def test_published_specs_have_the_scale_the_report_claims():
    assert structural_spec().size == 1_048_576
    assert semantic_spec().size == 104_976


# --------------------------------------------------------------------------- structural tier


def test_structural_tier_never_exceeds_the_factorial_bound():
    for item in generate_corpus(SMALL_SPEC)["expressions"]:
        record = structural_record(item)
        bound = factorial(record["support_size"])
        assert record["ast_bound"] == bound
        assert record["strict_distinct_ast_count"] <= bound
        assert not record["exceeds_bound"]
        # G0 keeps its tied level, so it is the one grammar that can add a 25th form.
        assert record["distinct_ast_count"] <= bound + 1


def test_structural_sweep_reports_zero_bound_violations():
    sweep = structural_sweep(SMALL_SPEC, workers=1)
    assert sweep["overall"]["bound_violations"] == 0
    assert sweep["overall"]["support_block_violations"] == 0
    assert sweep["expression_count"] == SMALL_SPEC.size
    assert sum(sweep["overall"]["strict_distinct_ast_distribution"].values()) == SMALL_SPEC.size


def test_every_support_block_carries_exactly_one_ast():
    """Experiment 0019's reduction, re-checked on this corpus rather than assumed."""
    for item in generate_corpus(SMALL_SPEC)["expressions"]:
        record = structural_record(item)
        assert record["max_asts_in_a_block"] == 1
        assert record["support_block_count"] == factorial(record["support_size"])


def test_structural_path_calls_no_sympy(monkeypatch):
    """Make the SymPy entry points of ``canonical`` explode; the structural tier must not notice."""
    import parseatlas.canonical as canonical

    def explode(*_args, **_kwargs):
        raise AssertionError("the structural tier must not evaluate a SymPy expression")

    monkeypatch.setattr(canonical, "to_sympy", explode)
    monkeypatch.setattr(canonical, "simplify", explode)
    monkeypatch.setattr(canonical, "solve", explode)
    sweep = structural_sweep(SMALL_SPEC, workers=1)
    assert sweep["expression_count"] == SMALL_SPEC.size
    # THIS test is the evidence for the claim; the sweep must publish it as an assertion and must
    # not publish a hardcoded 0 dressed up as a counted quantity.
    assert sweep["sympy_call_claim"]["kind"].startswith("assertion")
    assert "sympy_calls" not in sweep


def test_structure_is_invariant_under_coefficient_substitution():
    """A coefficient is neither a token kind nor a binding power, so it cannot move the AST count."""
    invariance = structural_sweep(SMALL_SPEC, workers=1)["coefficient_invariance"]
    assert invariance["invariant"]
    assert invariance["families_with_a_varying_quantity"] == {}
    assert set(invariance["values_per_family"]) == set(SMALL_SPEC.families)
    # a single structural value per family means the whole family collapses to one measurement
    for entry in invariance["values_per_family"].values():
        assert all(isinstance(value, int) for value in entry.values())


def test_semantics_is_not_invariant_under_coefficient_substitution(small_semantic_records):
    """The contrast that makes the semantic tier necessary: C(E) does move with the coefficients."""
    per_family = {}
    for record in small_semantic_records:
        per_family.setdefault(record["family"], set()).add(record["class_count"])
    assert any(len(values) > 1 for values in per_family.values())


def test_structural_conditioning_respects_the_bound_per_support_size():
    sweep = structural_sweep(SMALL_SPEC, workers=1)
    for size, block in sweep["overall"]["strict_distinct_ast_by_support_size"].items():
        assert block["bound"] == factorial(size)
        assert max(block["distribution"]) <= block["bound"]


def test_structural_sequential_and_parallel_agree():
    sequential = structural_sweep(TINY_SPEC, workers=1)
    parallel = structural_sweep(TINY_SPEC, workers=2, chunk_size=8)
    assert parallel["workers"] == 2
    for key in (
        "overall",
        "families",
        "coefficient_invariance",
        "examples_by_strict_distinct_ast",
        "expression_count",
    ):
        assert sequential[key] == parallel[key]


def test_chunking_does_not_change_the_structural_result():
    assert structural_sweep(SMALL_SPEC, workers=1, chunk_size=7)["overall"] == structural_sweep(
        SMALL_SPEC, workers=1, chunk_size=64
    )["overall"]


# ----------------------------------------------------------------------------- semantic tier


def test_semantic_tier_agrees_with_analyze_expression_on_partition_membership(family_records):
    """The class key is not redefined here - this pins that it is the same partition."""
    checked = 0
    for item, record in zip(FAMILY_REPRESENTATIVES, family_records):
        if item["family"] not in CROSS_CHECKED_FAMILIES:
            continue
        checked += 1
        report = analyze_expression(item["source"])
        reference = {entry["id"]: entry["equivalence_class"] for entry in report["grammars"]}
        assert _partition(expression_classes(item["source"])["classes"]) == _partition(reference)
        assert record["class_count"] == len(report["equivalence_classes"])
    assert checked == len(CROSS_CHECKED_FAMILIES)


def test_every_family_representative_has_a_consistent_record(family_records):
    """The cheap half of the same check, run over all sixteen families."""
    for item, record in zip(FAMILY_REPRESENTATIVES, family_records):
        classes = expression_classes(item["source"])
        assert record["class_count"] == classes["distinct_class_count"]
        assert record["distinct_ast_count"] == classes["distinct_ast_count"]
        assert record["family"] == item["family"]


def test_semantic_class_count_is_bounded_by_the_ast_count(small_semantic_records):
    for record in small_semantic_records:
        assert record["class_count"] <= record["distinct_ast_count"]
        assert record["strict_class_count"] <= record["strict_distinct_ast_count"]
        assert record["strict_distinct_ast_count"] <= record["ast_bound"]


def test_class_kinds_partition_the_classes(small_semantic_records):
    for record in small_semantic_records:
        assert (
            record["constant_classes"] + record["degenerate_classes"] + record["variable_classes"]
            == record["class_count"]
        )


def test_no_canonical_text_fails_to_round_trip(small_semantic_records):
    assert sum(record["sympify_failures"] for record in small_semantic_records) == 0


def test_semantic_sequential_and_parallel_agree():
    sequential = semantic_sweep(TINY_SPEC, workers=1)
    parallel = semantic_sweep(TINY_SPEC, workers=2, chunk_size=8)
    assert parallel["workers"] == 2
    assert sequential["records"] == parallel["records"]


def test_deduplication_saves_canonicalizations(small_semantic_records):
    sweep = semantic_sweep(SMALL_SPEC, workers=1, chunk_size=64)
    assert sweep["canonicalizations"] < sweep["canonicalizations_without_dedup"]


def test_founding_expression_still_collapses_to_eight():
    record = semantic_record({"index": 0, "family": "founding", "source": FOUNDING_EXPRESSION})
    assert record["strict_class_count"] == 8
    assert record["class_count"] == 8
    assert record["strict_distinct_ast_count"] == 14
    assert record["ast_bound"] == 24


def test_the_founding_token_stream_is_not_in_the_corpus():
    """``affine_div`` has the founding SHAPE; it does not contain the founding token stream.

    The template is ``{a}*x + {b} - {c}*x/{d}`` and always emits an explicit ``{c}*x``, so the bare
    ``x/{d}`` tail of ``2*t + 1 - t/2`` is not generated anywhere in the corpus. The report may
    therefore say "same shape modulo an implicit unit coefficient" and may not say "member".
    """
    templates = {family: template for family, template, _ in FAMILY_TEMPLATES}
    assert templates["affine_div"] == "{a}*x + {b} - {c}*x/{d}"
    sources = {item["source"] for item in semantic_spec().items()}
    assert FOUNDING_EXPRESSION not in sources
    assert NEAREST_FAMILY_MEMBER in sources
    assert not any("- x/" in source for source in sources)


def test_the_founding_stream_and_its_nearest_family_member_differ_structurally():
    """Both reach ``8``, and they reach it from different token streams - which is the point.

    Interpretation 4 of the report says ``C(E)`` is a property of the token stream rather than of
    the mathematics. A token-stream difference is therefore exactly what disqualifies a membership
    claim: the founding stream has `14` strict ASTs and every ``affine_div`` member has `17`.
    """
    founding = semantic_record({"index": 0, "family": "founding", "source": FOUNDING_EXPRESSION})
    member = semantic_record({"index": 1, "family": "affine_div", "source": NEAREST_FAMILY_MEMBER})
    assert founding["class_count"] == member["class_count"] == 8
    assert founding["support_size"] == member["support_size"] == 4
    assert founding["strict_distinct_ast_count"] == 14
    assert member["strict_distinct_ast_count"] == 17
    # `17` is the family's value and not this member's: 256 affine_div coefficient tuples, one value.
    affine_div_only = CorpusSpec(values_count=4, templates=FAMILY_TEMPLATES[1:2])
    assert affine_div_only.families == ("affine_div",)
    counts = {structural_record(item)["strict_distinct_ast_count"] for item in affine_div_only.items()}
    assert counts == {17}


# ------------------------------------------------------------------------------ distributions


def test_distribution_report_accounts_for_every_expression(small_semantic_records):
    report = distribution_report(records=small_semantic_records)
    overall = report["overall"]
    assert overall["expression_count"] == SMALL_SPEC.size
    assert sum(overall["class_count_distribution"].values()) == SMALL_SPEC.size
    assert sum(overall["distinct_ast_distribution"].values()) == SMALL_SPEC.size
    assert sum(block["expression_count"] for block in report["families"].values()) == SMALL_SPEC.size
    assert sum(block["expression_count"] for block in report["by_support_size"].values()) == SMALL_SPEC.size


def test_distribution_report_mode_and_shares_are_consistent(small_semantic_records):
    overall = distribution_report(records=small_semantic_records)["overall"]
    distribution = overall["class_count_distribution"]
    assert distribution[overall["mode"]] == overall["mode_count"] == max(distribution.values())
    assert overall["mode_share"] == pytest.approx(overall["mode_count"] / SMALL_SPEC.size)
    assert overall["count_at_8"] == distribution.get(8, 0)
    assert overall["share_at_8"] == pytest.approx(overall["count_at_8"] / SMALL_SPEC.size)


def test_conditioning_on_support_size_keeps_the_null_bound(small_semantic_records):
    report = distribution_report(records=small_semantic_records)
    for size, block in report["by_support_size"].items():
        assert max(block["class_count_distribution"]) <= factorial(size) + 1
        assert max(block["strict_class_count_distribution"]) <= factorial(size)


def test_family_mix_ablation_publishes_the_conditional_distribution_without_its_biggest_families(
    small_semantic_records,
):
    """The support-conditioned distribution is corpus-relative too, so it ships with the ablation.

    This pins that ``family_mix_ablation`` really is the same conditioning over the same records
    with the named families removed - not a second, differently computed table.
    """
    report = distribution_report(records=small_semantic_records)
    ablation = report["family_mix_ablation"]
    assert ablation["removed_families"] == list(SATURATING_DIV_FAMILIES)

    dropped = [record for record in small_semantic_records if record["family"] in SATURATING_DIV_FAMILIES]
    assert dropped, "the sub-corpus must contain a removed family or this test proves nothing"
    assert ablation["expression_count"] == SMALL_SPEC.size - len(dropped)
    assert sum(block["expression_count"] for block in ablation["by_support_size"].values()) == len(
        small_semantic_records
    ) - len(dropped)

    for size, block in ablation["by_support_size"].items():
        kept = [
            record
            for record in small_semantic_records
            if record["support_size"] == size and record["family"] not in SATURATING_DIV_FAMILIES
        ]
        assert block["class_count_distribution"] == dict(sorted(Counter(r["class_count"] for r in kept).items()))
        assert block["count_at_8"] <= report["by_support_size"][size]["count_at_8"]


def test_mode_ties_break_toward_the_smaller_value():
    assert _mode(Counter({4: 3, 2: 3, 9: 1})) == 2
    assert _mode(Counter()) is None


# ---------------------------------------------------------------------------------- collapse


def test_collapse_examples_actually_exhibit_the_phenomenon(small_semantic_records):
    report = collapse_report(records=small_semantic_records)
    for example in report["constant_collapse"]["examples"]:
        assert example["constant_classes"] > 0 and example["variable_classes"] > 0
    for example in report["degree_difference"]["examples"]:
        assert example["degree_spread"] > 0
    for example in report["division_difference"]["examples"]:
        assert example["division_spread"] > 0
    for example in report["depth_difference"]["examples"]:
        assert example["free_depth_saving"] > 0


def test_collapse_counts_match_the_records(small_semantic_records):
    report = collapse_report(records=small_semantic_records)
    assert report["depth_difference"]["expressions"] == sum(
        record["depth_spread"] > 0 for record in small_semantic_records
    )
    assert report["degree_difference"]["expressions"] == sum(
        record["degree_spread"] > 0 for record in small_semantic_records
    )
    assert report["constant_collapse"]["expressions"] == sum(
        record["constant_classes"] > 0 for record in small_semantic_records
    )
    assert report["expression_count"] == SMALL_SPEC.size


def test_examples_are_drawn_from_distinct_families(small_semantic_records):
    report = collapse_report(records=small_semantic_records)
    for phenomenon in ("constant_collapse", "degree_difference", "division_difference", "depth_difference"):
        families = [example["family"] for example in report[phenomenon]["examples"]]
        assert len(families) == len(set(families))


def test_examples_are_the_middle_match_not_the_first(small_semantic_records):
    """The corpus starts at the all-zero corner, so the first match is never representative."""
    report = collapse_report(records=small_semantic_records)
    for example in report["depth_difference"]["examples"]:
        matches = [
            record
            for record in small_semantic_records
            if record["family"] == example["family"] and record["free_depth_saving"] > 0
        ]
        assert example["source"] == matches[len(matches) // 2]["source"]


def test_control_columns_are_measured_not_assumed(small_semantic_records):
    for record in small_semantic_records:
        assert record["control_adds_an_ast"] == (
            record["distinct_ast_count"] > record["strict_distinct_ast_count"]
        )
        assert record["control_adds_a_class"] == (record["class_count"] > record["strict_class_count"])
    block = distribution_report(records=small_semantic_records)["overall"]
    assert block["control_adds_a_class"] == sum(
        record["control_adds_a_class"] for record in small_semantic_records
    )


def test_free_depth_saving_never_exceeds_the_total_depth_spread(small_semantic_records):
    for record in small_semantic_records:
        assert 0 <= record["free_depth_saving"] <= record["depth_spread"]
        assert 0 <= record["control_depth_saving"] <= record["depth_spread"]


def test_division_count_counts_negative_powers():
    assert _division_count(sympify("x + 1")) == 0
    assert _division_count(sympify("1/x")) == 1
    assert _division_count(sympify("1/x + 1/(x + 1)")) == 2
    assert _division_count(sympify("x**2")) == 0


def test_founding_expression_shows_a_constant_collapse_and_a_degree_difference():
    """The founding expression is itself an example of both phenomena the report names."""
    record = semantic_record({"index": 0, "family": "founding", "source": FOUNDING_EXPRESSION})
    assert record["constant_classes"] == 1
    assert record["variable_classes"] == 7
    assert record["degrees"] == (0, 1)
    assert record["degree_spread"] == 1


# -------------------------------------------------------------------------------- multicore


def test_worker_count_is_derived_from_the_observed_cores(monkeypatch):
    """The ``workers=None`` path: derived from the OBSERVED cores, with one core of headroom.

    Four different observed core counts give four different worker counts, so the number cannot be
    a hardcoded constant, and every one of them is strictly below the core count, so a sweep cannot
    starve the interactive session.
    """
    import parseatlas.corpus_matrix as corpus_matrix

    derived = {}
    for cores in (2, 4, 16, 64):
        monkeypatch.setattr(corpus_matrix.os, "cpu_count", lambda cores=cores: cores)
        _, resolved = _plan(SMALL_SPEC, None, None)
        derived[cores] = resolved
        assert resolved == cores - 1, "one core of headroom, derived from the observed count"
        assert resolved < cores
    assert len(set(derived.values())) == len(derived), "a constant would give the same count for all"


def test_a_sweep_records_the_plan_it_actually_ran():
    """The reported plan is the executed plan: the requested workers, the observed cores, chunks
    that cover the corpus exactly once."""
    sweep = structural_sweep(SMALL_SPEC, workers=1)
    assert sweep["cpu_count"] == os.cpu_count()
    assert sweep["workers"] == 1
    assert sweep["chunk_count"] * sweep["chunk_size"] >= SMALL_SPEC.size
    assert (sweep["chunk_count"] - 1) * sweep["chunk_size"] < SMALL_SPEC.size
    assert sweep["expression_count"] == SMALL_SPEC.size


# ------------------------------------------------------------------------------- calibration


def test_calibration_reproduces_the_0024_distribution():
    """0024's corpus, 0024's published numbers, this module's pipeline.

    This is the one test that is allowed to be slow: the calibration is only meaningful on the
    exact `3125`-expression corpus 0024 published, and a subset would be compared against a
    distribution that nobody wrote down.
    """
    report = calibration_report()
    assert report["corpus_size"] == len(COEFFICIENT_VALUES) ** 4 * 5 == 3125
    assert report["observed"] == CALIBRATION_CLASS_DISTRIBUTION
    assert report["reproduces"]
    assert report["mode"] == 4
