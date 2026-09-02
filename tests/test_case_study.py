"""Tests for the equivalence-preserving case-study intake engine.

Every synthetic record used here is constructed inside the test. No test writes anything into
``case_studies/``, and no test asserts the existence of a benchmark figure that ParseAtlas has not
measured; the two tests that touch shipped files assert the opposite, that those files carry no
measurement at all.
"""

from pathlib import Path

import pytest

from parseatlas.case_study import (
    MINIMUM_CORRELATION_SAMPLE_SIZE,
    MINIMUM_RATE_SAMPLE_SIZE,
    NUMERIC_FIELDS,
    PENDING,
    REQUIRED_FIELDS,
    ROADMAP_PHASE_13_DIMENSION_LABELS,
    TRANSFORMATION_VOCABULARY,
    load_records,
    parse_record,
    predictor_correlation,
    transformation_statistics,
    validate_record,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPOSITORY_ROOT / "case_studies" / "ultrafast_secp256k1"
RECORDS_DIR = STUDY_DIR / "records"
TEMPLATE_PATH = RECORDS_DIR / "EXAMPLE_TEMPLATE.md"
TABLE_BUILDING_PATH = STUDY_DIR / "table_building.md"

BASE_FIELDS = {
    "record_id": "synthetic-000",
    "primitive": "field multiplication",
    "baseline_representation": "baseline sequence",
    "candidate_representation": "candidate sequence",
    "invariant": "candidate == baseline",
    "transformation": "reassociation",
    "op_delta_mul": "-1",
    "op_delta_sqr": "0",
    "op_delta_add": "2",
    "op_delta_sub": "0",
    "op_delta_reduce": "0",
    "depth_before": "20",
    "depth_after": "19",
    "benchmark_baseline": "100.0",
    "benchmark_candidate": "95.0",
    "benchmark_delta": "-5.0",
    "benchmark_unit": "ns/op",
    "benchmark_machine": "synthetic test fixture",
    "benchmark_repetitions": "1000",
    "validation_random_differential": "pass",
    "validation_edge_cases": "pass",
    "validation_bitcoin_core_tests": "pass",
    "evidence_level": "benchmarked",
}


def build_record_text(**overrides) -> str:
    """Build one synthetic record document. A ``None`` override omits the key entirely."""
    values = dict(BASE_FIELDS)
    values.update(overrides)
    lines = ["---"]
    lines.extend(f"{key}: {value}" for key, value in values.items() if value is not None)
    lines.append("---")
    lines.append("")
    lines.append("# synthetic record built inside the test")
    return "\n".join(lines)


def build_record(**overrides) -> dict:
    return parse_record(build_record_text(**overrides), source=overrides.get("record_id", "synthetic"))


def measured_record(
    index: int,
    delta_percent: float,
    transformation: str = "reassociation",
    depth_before: int = 20,
    depth_after: int = 19,
) -> dict:
    """Build a complete, admissible record whose stated delta matches its baseline and candidate."""
    baseline = 100.0
    candidate = baseline * (1.0 + delta_percent / 100.0)
    return build_record(
        record_id=f"synthetic-{index:03d}",
        transformation=transformation,
        depth_before=str(depth_before),
        depth_after=str(depth_after),
        benchmark_baseline=f"{baseline:.10f}",
        benchmark_candidate=f"{candidate:.10f}",
        benchmark_delta=f"{delta_percent:.10f}",
    )


# --- parsing -------------------------------------------------------------------------------


def test_pending_import_parses_to_none_and_never_to_zero():
    record = build_record(op_delta_mul=PENDING, depth_after=PENDING, benchmark_delta=PENDING)

    for field in ("op_delta_mul", "depth_after", "benchmark_delta"):
        value = record["fields"][field]
        assert value is None
        assert value != 0
        assert not isinstance(value, (int, float))

    assert record["pending_fields"] == ["benchmark_delta", "depth_after", "op_delta_mul"]
    assert record["missing_fields"] == []
    assert record["complete"] is False
    assert record["derived"]["operation_count_delta"] is None
    assert record["derived"]["dependency_depth_delta"] is None
    assert record["derived"]["speedup_percent"] is None


def test_a_fully_populated_record_parses_to_typed_values_and_derived_quantities():
    record = build_record()

    assert record["complete"] is True
    assert record["pending_fields"] == []
    assert record["fields"]["op_delta_mul"] == -1
    assert record["fields"]["depth_before"] == 20
    assert record["fields"]["benchmark_delta"] == pytest.approx(-5.0)
    assert record["derived"]["operation_count_delta"] == 1
    assert record["derived"]["dependency_depth_delta"] == -1
    assert record["derived"]["speedup_percent"] == pytest.approx(5.0)
    assert record["derived"]["transformations"] == ("reassociation",)


def test_absent_and_empty_required_keys_are_missing_rather_than_pending():
    record = build_record(primitive=None, benchmark_unit="")

    assert record["missing_fields"] == ["benchmark_unit", "primitive"]
    assert "primitive" not in record["pending_fields"]
    assert record["complete"] is False


def test_a_document_without_front_matter_is_rejected_loudly():
    with pytest.raises(ValueError, match="front-matter"):
        parse_record("# just prose\n\nno block here\n")


# --- admission control ---------------------------------------------------------------------


def test_a_complete_validated_record_is_admissible():
    verdict = validate_record(build_record())
    assert verdict["admissible"] is True
    assert verdict["reasons"] == []


def test_a_record_missing_its_invariant_is_rejected():
    verdict = validate_record(build_record(invariant=None))
    assert verdict["admissible"] is False
    assert any("invariant" in reason for reason in verdict["reasons"])


def test_a_record_whose_invariant_is_pending_is_rejected():
    verdict = validate_record(build_record(invariant=PENDING))
    assert verdict["admissible"] is False
    assert any("equivalence claim is unproven" in reason for reason in verdict["reasons"])


def test_a_record_whose_invariant_states_no_equivalence_is_rejected():
    verdict = validate_record(build_record(invariant="candidate is faster than baseline"))
    assert verdict["admissible"] is False
    assert any("does not state an equivalence claim" in reason for reason in verdict["reasons"])


def test_a_record_missing_its_validation_fields_is_rejected():
    verdict = validate_record(
        build_record(validation_random_differential=None, validation_edge_cases=None)
    )
    assert verdict["admissible"] is False
    assert any("validation_random_differential" in reason for reason in verdict["reasons"])
    assert any("validation_edge_cases" in reason for reason in verdict["reasons"])


def test_a_record_whose_validation_is_pending_or_failing_is_rejected():
    pending = validate_record(build_record(validation_edge_cases=PENDING))
    assert pending["admissible"] is False
    assert any("validation is pending" in reason for reason in pending["reasons"])

    failing = validate_record(build_record(validation_random_differential="fail"))
    assert failing["admissible"] is False
    assert any("did not pass" in reason for reason in failing["reasons"])


def test_an_owner_reported_record_is_never_admissible():
    verdict = validate_record(build_record(evidence_level="owner-reported"))
    assert verdict["admissible"] is False
    assert any("ParseAtlas measured nothing here" in reason for reason in verdict["reasons"])


def test_a_record_whose_evidence_level_is_pending_is_rejected():
    """A benchmark number whose provenance is unknown must not be admitted.

    Every other field in this record is filled and every validation passes, so before the fix the
    record was admitted with no rejection reason at all: a real-looking speedup that ParseAtlas
    could not say it had measured.
    """
    record = build_record(evidence_level=PENDING)

    assert record["pending_fields"] == ["evidence_level"]
    assert record["missing_fields"] == []

    verdict = validate_record(record)

    assert verdict["admissible"] is False
    assert any("evidence level is pending" in reason for reason in verdict["reasons"])

    statistics = transformation_statistics([record])
    assert statistics["admissible_count"] == 0
    assert statistics["labels"]["reassociation"]["rejected_records"] == 1
    assert statistics["labels"]["reassociation"]["measured_records"] == 0


def test_a_record_whose_evidence_level_is_absent_is_rejected_as_missing():
    verdict = validate_record(build_record(evidence_level=None))
    assert verdict["admissible"] is False
    assert any("required field is missing: evidence_level" in reason for reason in verdict["reasons"])


def test_an_evidence_level_outside_the_vocabulary_is_rejected():
    verdict = validate_record(build_record(evidence_level="vibes"))
    assert verdict["admissible"] is False
    assert any("outside the vocabulary" in reason for reason in verdict["reasons"])


@pytest.mark.parametrize(
    "field",
    [
        "invariant",
        "transformation",
        "validation_random_differential",
        "validation_edge_cases",
        "validation_bitcoin_core_tests",
        "evidence_level",
    ],
)
def test_every_proof_obligation_field_is_rejected_when_pending(field):
    """The six fields carrying the proof obligation are rejected identically when pending.

    ``evidence_level`` used to be the exception; it is not one any more.
    """
    verdict = validate_record(build_record(**{field: PENDING}))

    assert verdict["admissible"] is False, f"pending {field} was admitted"
    assert verdict["reasons"], f"pending {field} produced an empty reason list"


def test_a_transformation_label_outside_the_vocabulary_is_rejected():
    verdict = validate_record(build_record(transformation="magic rewrite"))
    assert verdict["admissible"] is False
    assert any("controlled vocabulary" in reason for reason in verdict["reasons"])


def test_a_benchmark_delta_that_contradicts_its_own_baseline_is_rejected():
    verdict = validate_record(
        build_record(benchmark_baseline="100.0", benchmark_candidate="95.0", benchmark_delta="5.0")
    )
    assert verdict["admissible"] is False
    assert any("disagrees with" in reason for reason in verdict["reasons"])


# --- transformation statistics -------------------------------------------------------------


def test_rate_is_withheld_below_the_minimum_sample_but_raw_counts_are_still_reported():
    records = [measured_record(index, -5.0) for index in range(5)]

    bucket = transformation_statistics(records)["labels"]["reassociation"]

    assert bucket["measured_records"] == 5
    assert bucket["speedup_count"] == 5
    assert bucket["speedup_rate"] is None
    assert bucket["confidence_interval"] is None
    assert "below the minimum sample size" in bucket["rate_withheld_reason"]
    assert bucket["minimum_sample_size"] == MINIMUM_RATE_SAMPLE_SIZE


def test_synthetic_corpus_produces_arithmetically_correct_counts():
    records = (
        [measured_record(index, -8.0) for index in range(3)]
        + [measured_record(10, 6.0)]
        + [measured_record(20, 0.2)]
    )

    statistics = transformation_statistics(records)
    bucket = statistics["labels"]["reassociation"]

    assert statistics["record_count"] == 5
    assert statistics["admissible_count"] == 5
    assert statistics["rejected_count"] == 0
    assert bucket["total_records"] == 5
    assert bucket["admissible_records"] == 5
    assert bucket["measured_records"] == 5
    assert bucket["speedup_count"] == 3
    assert bucket["regression_count"] == 1
    assert bucket["no_change_count"] == 1
    assert (
        bucket["speedup_count"] + bucket["regression_count"] + bucket["no_change_count"]
        == bucket["measured_records"]
    )
    assert set(statistics["labels"]) == set(TRANSFORMATION_VOCABULARY)
    assert statistics["labels"]["lazy reduction"]["total_records"] == 0


def test_inadmissible_records_are_counted_but_never_measured():
    records = [measured_record(0, -9.0), build_record(record_id="x", validation_edge_cases=PENDING)]

    statistics = transformation_statistics(records)
    bucket = statistics["labels"]["reassociation"]

    assert statistics["admissible_count"] == 1
    assert statistics["rejected_count"] == 1
    assert bucket["total_records"] == 2
    assert bucket["admissible_records"] == 1
    assert bucket["rejected_records"] == 1
    assert bucket["measured_records"] == 1
    assert bucket["speedup_count"] == 1


def test_a_multi_label_record_is_counted_under_every_label_it_names():
    records = [measured_record(0, -4.0, transformation="reassociation, lazy reduction")]

    labels = transformation_statistics(records)["labels"]

    assert labels["reassociation"]["measured_records"] == 1
    assert labels["lazy reduction"]["measured_records"] == 1
    assert labels["factorization"]["measured_records"] == 0


def test_a_caller_cannot_lower_the_sample_size_floor_to_manufacture_a_rate():
    """A single record must never yield ``speedup_rate = 1.0``.

    ``MINIMUM_RATE_SAMPLE_SIZE`` is documented as enforced, so it is a floor, not a default. A
    request below it is clamped and the clamp is reported rather than applied silently.
    """
    records = [measured_record(0, -5.0)]

    statistics = transformation_statistics(records, minimum_sample_size=1)
    bucket = statistics["labels"]["reassociation"]

    assert bucket["measured_records"] == 1
    assert bucket["speedup_count"] == 1
    assert bucket["speedup_rate"] is None
    assert bucket["confidence_interval"] is None
    assert bucket["minimum_sample_size"] == MINIMUM_RATE_SAMPLE_SIZE
    assert bucket["requested_minimum_sample_size"] == 1
    assert bucket["sample_size_floor_applied"] is True
    assert statistics["minimum_sample_size"] == MINIMUM_RATE_SAMPLE_SIZE
    assert statistics["sample_size_floor_applied"] is True
    assert "below the documented floor" in statistics["sample_size_floor_note"]


def test_the_sample_size_floor_may_be_raised_but_is_not_flagged_when_it_is_not_applied():
    records = [measured_record(index, -5.0) for index in range(MINIMUM_RATE_SAMPLE_SIZE)]

    raised = transformation_statistics(records, minimum_sample_size=MINIMUM_RATE_SAMPLE_SIZE + 5)
    assert raised["minimum_sample_size"] == MINIMUM_RATE_SAMPLE_SIZE + 5
    assert raised["sample_size_floor_applied"] is False
    assert raised["sample_size_floor_note"] is None
    assert raised["labels"]["reassociation"]["speedup_rate"] is None

    default = transformation_statistics(records)
    assert default["sample_size_floor_applied"] is False
    assert default["labels"]["reassociation"]["speedup_rate"] == pytest.approx(1.0)


def test_a_zero_minimum_sample_size_withholds_the_rate_instead_of_dividing_by_zero():
    statistics = transformation_statistics([], minimum_sample_size=0)

    assert statistics["record_count"] == 0
    for bucket in statistics["labels"].values():
        assert bucket["measured_records"] == 0
        assert bucket["speedup_rate"] is None
        assert bucket["confidence_interval"] is None
        assert "below the minimum sample size" in bucket["rate_withheld_reason"]


def test_a_negative_minimum_sample_size_is_clamped_rather_than_honoured():
    statistics = transformation_statistics([measured_record(0, -5.0)], minimum_sample_size=-10)

    assert statistics["minimum_sample_size"] == MINIMUM_RATE_SAMPLE_SIZE
    assert statistics["sample_size_floor_applied"] is True
    assert statistics["labels"]["reassociation"]["speedup_rate"] is None


def test_rate_and_confidence_interval_appear_once_the_sample_reaches_the_minimum():
    records = [measured_record(index, -5.0) for index in range(15)]
    records += [measured_record(50 + index, 5.0) for index in range(5)]

    bucket = transformation_statistics(records)["labels"]["reassociation"]

    assert bucket["measured_records"] == MINIMUM_RATE_SAMPLE_SIZE
    assert bucket["speedup_count"] == 15
    assert bucket["regression_count"] == 5
    assert bucket["speedup_rate"] == pytest.approx(0.75)
    assert bucket["rate_withheld_reason"] is None
    low, high = bucket["confidence_interval"]
    assert 0.0 <= low < 0.75 < high <= 1.0


# --- predictor correlation -----------------------------------------------------------------


def test_predictor_correlation_returns_none_with_a_reason_on_insufficient_data():
    result = predictor_correlation([measured_record(index, -5.0) for index in range(3)])

    assert result["sample_size"] == 3
    assert result["minimum_sample_size"] == MINIMUM_CORRELATION_SAMPLE_SIZE
    assert "below the minimum sample size" in result["reason"]
    for name in ("operation_count_delta", "dependency_depth_delta"):
        assert result["predictors"][name]["correlation"] is None
        assert "below the minimum sample size" in result["predictors"][name]["reason"]


def test_predictor_correlation_ignores_pending_records_entirely():
    records = [measured_record(index, -5.0) for index in range(3)]
    records += [build_record(record_id=f"pending-{index}", benchmark_delta=PENDING) for index in range(9)]

    result = predictor_correlation(records)

    assert result["sample_size"] == 3
    assert result["predictors"]["dependency_depth_delta"]["correlation"] is None


def test_predictor_correlation_measures_a_real_relation_and_flags_a_constant_predictor():
    records = [
        measured_record(index, -(float(index) + 1.0), depth_before=20, depth_after=20 - (index + 1))
        for index in range(12)
    ]

    result = predictor_correlation(records)

    assert result["sample_size"] == 12
    assert result["reason"] is None

    depth = result["predictors"]["dependency_depth_delta"]
    assert depth["sample_size"] == 12
    assert depth["correlation"] == pytest.approx(-1.0)

    operations = result["predictors"]["operation_count_delta"]
    assert operations["correlation"] is None
    assert "no variance" in operations["reason"]


def test_a_zero_minimum_correlation_sample_withholds_instead_of_dividing_by_zero():
    result = predictor_correlation([], minimum_sample_size=0)

    assert result["sample_size"] == 0
    assert result["minimum_sample_size"] == MINIMUM_CORRELATION_SAMPLE_SIZE
    assert result["requested_minimum_sample_size"] == 0
    assert result["sample_size_floor_applied"] is True
    for predictor in result["predictors"].values():
        assert predictor["correlation"] is None
        assert "below the minimum sample size" in predictor["reason"]


def test_a_caller_cannot_lower_the_correlation_sample_floor():
    records = [measured_record(index, -(float(index) + 1.0), depth_after=20 - (index + 1)) for index in range(2)]

    result = predictor_correlation(records, minimum_sample_size=2)

    assert result["minimum_sample_size"] == MINIMUM_CORRELATION_SAMPLE_SIZE
    assert result["sample_size_floor_applied"] is True
    assert result["predictors"]["dependency_depth_delta"]["correlation"] is None


# --- controlled vocabulary provenance --------------------------------------------------------


def test_the_vocabulary_covers_every_roadmap_phase_13_representation_dimension():
    """The closed list is one label per ROADMAP Phase 13 representation dimension.

    The list is declared closed and extending it later requires re-labelling the whole corpus, so
    the mapping to its stated source is asserted rather than trusted. The ROADMAP wording is
    repeated literally here so a silent drop or a silent addition breaks this test.
    """
    roadmap_dimensions = (
        "limb layout",
        "projective scaling",
        "sign placement",
        "factorization",
        "associativity",
        "reduction placement",
        "lazy reduction",
        "coordinate systems",
        "addition chains",
        "common-subexpression reuse",
        "operation scheduling",
    )

    assert tuple(ROADMAP_PHASE_13_DIMENSION_LABELS) == roadmap_dimensions
    assert TRANSFORMATION_VOCABULARY == tuple(ROADMAP_PHASE_13_DIMENSION_LABELS.values())
    assert len(TRANSFORMATION_VOCABULARY) == len(roadmap_dimensions) == 11
    assert len(set(TRANSFORMATION_VOCABULARY)) == len(TRANSFORMATION_VOCABULARY)


def test_the_two_dropped_secp256k1_dimensions_are_labels_in_their_own_right():
    """``reduction placement`` and ``coordinate systems`` are distinct, in-scope classes."""
    for label in ("reduction placement", "coordinate systems"):
        assert label in TRANSFORMATION_VOCABULARY
        verdict = validate_record(build_record(transformation=label))
        assert verdict["admissible"] is True, verdict["reasons"]

    assert "reduction placement" != "lazy reduction"
    assert "coordinate systems" != "projective scaling"

    labels = transformation_statistics(
        [measured_record(0, -4.0, transformation="coordinate systems, reduction placement")]
    )["labels"]
    assert labels["coordinate systems"]["measured_records"] == 1
    assert labels["reduction placement"]["measured_records"] == 1
    assert labels["projective scaling"]["measured_records"] == 0
    assert labels["lazy reduction"]["measured_records"] == 0


def test_the_invented_regrouping_label_is_gone_and_is_now_a_rejection():
    assert "regrouping" not in TRANSFORMATION_VOCABULARY

    verdict = validate_record(build_record(transformation="regrouping"))

    assert verdict["admissible"] is False
    assert any("controlled vocabulary" in reason for reason in verdict["reasons"])


def test_the_record_schema_documents_the_vocabulary_it_actually_enforces():
    """Section 4 of the schema and ``TRANSFORMATION_VOCABULARY`` may not drift apart."""
    schema = (REPOSITORY_ROOT / "case_studies" / "RECORD_SCHEMA.md").read_text(encoding="utf-8")

    for roadmap_wording, label in ROADMAP_PHASE_13_DIMENSION_LABELS.items():
        assert f"`{label}`" in schema, f"schema does not define the label {label!r}"
        assert roadmap_wording in schema, f"schema does not name the ROADMAP dimension {roadmap_wording!r}"

    assert "One label was removed" in schema, "the schema does not record the removal of 'regrouping'"
    assert "are exactly the representation dimensions" not in schema

    renamed = [
        wording
        for wording, label in ROADMAP_PHASE_13_DIMENSION_LABELS.items()
        if wording != label
    ]
    assert renamed == ["sign placement", "associativity", "addition chains"]
    assert "three labels are" in schema, "the schema misstates how many labels were renamed"
    for wording in renamed:
        assert f"| {wording} | `{ROADMAP_PHASE_13_DIMENSION_LABELS[wording]}` | renamed" in schema


# --- directory loading ---------------------------------------------------------------------


def test_load_records_skips_the_example_template(tmp_path):
    (tmp_path / "EXAMPLE_TEMPLATE.md").write_text(
        TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "real-001.md").write_text(build_record_text(record_id="real-001"), encoding="utf-8")

    summary = load_records(tmp_path)

    assert summary["skipped"] == ["EXAMPLE_TEMPLATE.md"]
    assert summary["record_count"] == 1
    assert summary["records"][0]["fields"]["record_id"] == "real-001"
    assert summary["complete_count"] == 1
    assert summary["pending_count"] == 0


def test_load_records_reports_which_fields_are_still_pending(tmp_path):
    (tmp_path / "a.md").write_text(build_record_text(record_id="a", benchmark_delta=PENDING), encoding="utf-8")

    summary = load_records(tmp_path)

    assert summary["complete_count"] == 0
    assert summary["pending_count"] == 1
    assert summary["pending_fields_by_record"]["a.md"] == ["benchmark_delta"]


def test_load_records_raises_on_a_malformed_file_instead_of_dropping_it(tmp_path):
    (tmp_path / "broken.md").write_text("# no front matter\n", encoding="utf-8")

    with pytest.raises(ValueError, match="broken.md"):
        load_records(tmp_path)


# --- shipped documents carry no data -------------------------------------------------------


def test_shipped_example_template_parses_and_is_reported_as_fully_pending():
    record = parse_record(TEMPLATE_PATH.read_text(encoding="utf-8"), source=TEMPLATE_PATH.name)

    assert record["missing_fields"] == []
    assert record["unknown_fields"] == []
    assert sorted(record["pending_fields"]) == sorted(REQUIRED_FIELDS)
    assert record["complete"] is False
    assert all(record["fields"][field] is None for field in REQUIRED_FIELDS)
    assert validate_record(record)["admissible"] is False

    statistics = transformation_statistics([record])
    assert statistics["admissible_count"] == 0
    assert all(bucket["measured_records"] == 0 for bucket in statistics["labels"].values())
    assert all(bucket["speedup_rate"] is None for bucket in statistics["labels"].values())


def test_shipped_records_directory_currently_holds_no_records():
    summary = load_records(RECORDS_DIR)

    assert summary["skipped"] == ["EXAMPLE_TEMPLATE.md"]
    assert summary["record_count"] == 0
    assert summary["complete_count"] == 0


NARRATIVE_PATHS = (
    REPOSITORY_ROOT / "case_studies" / "README.md",
    STUDY_DIR / "benchmark_summary.md",
    TABLE_BUILDING_PATH,
)


def test_the_experiment_0021_operation_count_quoted_in_prose_matches_the_engine():
    """The narrative documents may only quote a number the engine actually produces.

    ``a/b + c*d - e/f + g`` has six operations and thirteen AST nodes. The prose previously said
    "nine operations", which was the *node* count of a different expression in the same table. The
    number is re-derived here so the two cannot drift apart again.
    """
    from parseatlas.critical_path import cost_invariance_report

    expression = "a/b + c*d - e/f + g"
    report = cost_invariance_report((expression,))["expressions"][0]
    signature = dict(report["raw_signature"])
    operation_count = sum(count for name, count in signature.items() if name != "nodes")
    depth_profile = report["depth_profile"]

    assert operation_count == 6
    assert signature["nodes"] == 13
    assert depth_profile["min_depth"] == 4
    assert depth_profile["max_depth"] == 6
    assert len(depth_profile["min_depth_grammars"]) == 4
    assert depth_profile["grammar_count"] == 25

    spelled = {6: "six", 13: "thirteen"}[operation_count]
    for path in NARRATIVE_PATHS:
        text = " ".join(path.read_text(encoding="utf-8").split())
        if expression not in text:
            continue
        assert "nine operations" not in text, f"{path.name} still quotes the fabricated count"
        assert f"{spelled} operations" in text or f"{operation_count} operations" in text, (
            f"{path.name} does not quote the re-derived operation count"
        )
        assert "node count" in text or "AST nodes" in text, (
            f"{path.name} does not distinguish the operation count from the node count"
        )


def test_shipped_table_building_document_carries_no_measured_number():
    record = parse_record(TABLE_BUILDING_PATH.read_text(encoding="utf-8"), source="table_building.md")

    for field in NUMERIC_FIELDS:
        assert record["fields"][field] is None, f"{field} must stay {PENDING}"

    assert record["fields"]["evidence_level"] == "owner-reported"
    assert record["raw_values"]["owner_claim_verified"] == "no"
    assert "34" in record["raw_values"]["owner_reported_claim"]
    assert record["missing_fields"] == []
    assert record["complete"] is False

    verdict = validate_record(record)
    assert verdict["admissible"] is False
    assert any("owner-reported" in reason for reason in verdict["reasons"])
