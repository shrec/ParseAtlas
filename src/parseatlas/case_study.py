"""Intake, admission control, and statistics for equivalence-preserving case-study records.

ParseAtlas runs two research modes. In *semantic exploration* a different grammar yields a
different function, so the pair ``(tokens, grammar)`` is the research object. In
*equivalence-preserving representation search* the candidate and the baseline compute the same
value on the declared domain and only the measured cost differs. This module handles the second
mode only, because only the second mode transfers to cryptographic code.

The module is deliberately built to refuse invention:

* a field whose value reads ``PENDING IMPORT`` parses to ``None`` and is listed as pending; it
  never becomes ``0`` and never becomes a guess;
* a record without an equivalence claim or without validation results is rejected before it can
  reach any statistic, because an unproven equivalence claim must never enter the numbers;
* a conditional speedup rate is withheld, and the raw counts are returned instead, until the
  measured sample reaches :data:`MINIMUM_RATE_SAMPLE_SIZE`, which is a floor a caller may raise but
  never lower;
* a predictor correlation returns ``None`` together with an explicit reason instead of a
  spurious number when the complete-record sample is too small or has no variance.

The record format is normatively specified in ``case_studies/RECORD_SCHEMA.md``.
"""

import math
from collections.abc import Iterable
from pathlib import Path
from typing import Any

PENDING = "PENDING IMPORT"
"""The literal placeholder text. Any other spelling is a malformed record, not a placeholder."""

TEMPLATE_FILENAME = "EXAMPLE_TEMPLATE.md"
FRONT_MATTER_DELIMITER = "---"

MINIMUM_RATE_SAMPLE_SIZE = 20
"""Measured records per transformation label required before a speedup rate may be reported."""

MINIMUM_CORRELATION_SAMPLE_SIZE = 10
"""Complete records required before a predictor correlation may be reported."""

DEFAULT_NO_CHANGE_BAND_PERCENT = 1.0
"""Provisional dead band, in percentage points, inside which a measured delta counts as no change.

This is a stated convention, not a measurement. It exists so that ordinary benchmark noise is not
silently promoted to a speedup. It must be replaced by a variance-based test once records carry
the per-record variance the schema requires.
"""

CONFIDENCE_LEVEL = 0.95
_Z_SCORE = 1.959963984540054

ROADMAP_PHASE_13_DIMENSION_LABELS = {
    "limb layout": "limb layout",
    "projective scaling": "projective scaling",
    "sign placement": "sign relocation",
    "factorization": "factorization",
    "associativity": "reassociation",
    "reduction placement": "reduction placement",
    "lazy reduction": "lazy reduction",
    "coordinate systems": "coordinate systems",
    "addition chains": "addition chain",
    "common-subexpression reuse": "common-subexpression reuse",
    "operation scheduling": "operation scheduling",
}
"""Map from the ROADMAP Phase 13 "Representation dimensions" wording to the schema label.

The schema label is the normative spelling; the ROADMAP wording is the provenance. Three labels are
deliberate renames -- ``sign placement`` -> ``sign relocation``, ``associativity`` ->
``reassociation``, ``addition chains`` -> ``addition chain`` -- and the other eight are verbatim.
This
mapping exists so the relationship is checkable rather than asserted; ``RECORD_SCHEMA.md`` section
4 reproduces it, and ``tests/test_case_study.py`` asserts the two stay in step.
"""

TRANSFORMATION_VOCABULARY = tuple(ROADMAP_PHASE_13_DIMENSION_LABELS.values())
"""The closed controlled vocabulary for the ``transformation`` field.

One label per ROADMAP Phase 13 representation dimension, in ROADMAP order. The whole statistical
question -- which transformation classes actually yield speedups -- is only answerable if these
labels stay consistent, so an unlisted label is a rejection, not a new class. Extending the list is
a deliberate schema change that requires re-labelling the existing corpus.
"""

VALIDATION_STATUSES = ("pass", "fail", "not applicable")

EVIDENCE_LEVELS = (
    "owner-reported",
    "observed",
    "symbolically-justified",
    "numerically-validated",
    "hypothesized",
    "benchmarked",
)
"""Evidence levels from ``docs/research-methodology.md`` plus the intake level ``owner-reported``.

``owner-reported`` sits *below* level 1 of the methodology: it means an external party stated the
figure and ParseAtlas has not executed anything. It is never admissible into statistics.
"""

TEXT_FIELDS = (
    "record_id",
    "primitive",
    "baseline_representation",
    "candidate_representation",
    "invariant",
    "transformation",
    "benchmark_unit",
    "benchmark_machine",
    "evidence_level",
)

NUMERIC_FIELDS = (
    "op_delta_mul",
    "op_delta_sqr",
    "op_delta_add",
    "op_delta_sub",
    "op_delta_reduce",
    "depth_before",
    "depth_after",
    "benchmark_baseline",
    "benchmark_candidate",
    "benchmark_delta",
    "benchmark_repetitions",
)

VALIDATION_FIELDS = (
    "validation_random_differential",
    "validation_edge_cases",
    "validation_bitcoin_core_tests",
)

OPERATION_DELTA_FIELDS = (
    "op_delta_mul",
    "op_delta_sqr",
    "op_delta_add",
    "op_delta_sub",
    "op_delta_reduce",
)

REQUIRED_FIELDS = TEXT_FIELDS + NUMERIC_FIELDS + VALIDATION_FIELDS

OPTIONAL_FIELDS = ("owner_reported_claim", "owner_claim_verified", "notes")

KNOWN_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

BENCHMARK_DELTA_TOLERANCE_POINTS = 0.5
"""Allowed disagreement, in percentage points, between the stated delta and the recomputed one."""

MISSING_FRONT_MATTER_MESSAGE = (
    f"record has no front-matter block: the first non-empty line must be {FRONT_MATTER_DELIMITER!r}"
)
UNTERMINATED_FRONT_MATTER_MESSAGE = (
    f"record front-matter block is never closed by a second {FRONT_MATTER_DELIMITER!r} line"
)
NOT_A_DIRECTORY_MESSAGE = "load_records needs an existing directory of record files"


def _split_front_matter(text: str) -> tuple[list[str], str]:
    """Return the front-matter lines and the Markdown body, or raise if the block is malformed."""
    lines = text.splitlines()
    start = 0
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines) or lines[start].strip() != FRONT_MATTER_DELIMITER:
        raise ValueError(MISSING_FRONT_MATTER_MESSAGE)
    for end in range(start + 1, len(lines)):
        if lines[end].strip() == FRONT_MATTER_DELIMITER:
            return lines[start + 1 : end], "\n".join(lines[end + 1 :])
    raise ValueError(UNTERMINATED_FRONT_MATTER_MESSAGE)


def _read_key_values(front_matter: list[str]) -> dict[str, str]:
    """Read ``key: value`` lines into raw strings, rejecting duplicates and unparsable lines."""
    raw: dict[str, str] = {}
    for number, line in enumerate(front_matter, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"front-matter line {number} is not 'key: value': {line!r}")
        key, _, value = stripped.partition(":")
        key = key.strip()
        if key in raw:
            raise ValueError(f"front-matter key {key!r} appears more than once")
        raw[key] = value.strip()
    return raw


def _parse_number(raw: str, field: str) -> int | float:
    """Parse a numeric field. Only reached when the value is not the pending placeholder."""
    try:
        value: int | float = float(raw) if any(character in raw for character in ".eE") else int(raw)
    except ValueError as error:
        raise ValueError(f"field {field!r} is neither a number nor {PENDING!r}: {raw!r}") from error
    if not math.isfinite(value):
        raise ValueError(f"field {field!r} must be a finite number: {raw!r}")
    return value


def _parse_field(field: str, raw: str) -> Any:
    """Map one raw value to its typed value, mapping the pending placeholder to ``None`` first.

    The pending check happens before any conversion so a placeholder can never fall through into a
    numeric zero.
    """
    if raw == PENDING:
        return None
    if field in NUMERIC_FIELDS:
        return _parse_number(raw, field)
    if field in VALIDATION_FIELDS:
        return raw.strip().lower()
    return raw


def _derive(fields: dict[str, Any]) -> dict[str, Any]:
    """Compute the derived quantities, leaving each one ``None`` while any input is pending."""
    deltas = [fields.get(name) for name in OPERATION_DELTA_FIELDS]
    operation_count_delta = sum(deltas) if all(value is not None for value in deltas) else None

    before = fields.get("depth_before")
    after = fields.get("depth_after")
    dependency_depth_delta = after - before if before is not None and after is not None else None

    benchmark_delta = fields.get("benchmark_delta")
    speedup_percent = -benchmark_delta if benchmark_delta is not None else None

    transformation = fields.get("transformation")
    labels = ()
    if transformation:
        labels = tuple(part.strip().lower() for part in transformation.split(",") if part.strip())

    return {
        "operation_count_delta": operation_count_delta,
        "dependency_depth_delta": dependency_depth_delta,
        "speedup_percent": speedup_percent,
        "transformations": labels,
    }


def parse_record(text: str, source: str | None = None) -> dict[str, Any]:
    """Parse one record Markdown document into a structured record.

    Every field that reads ``PENDING IMPORT`` becomes ``None`` and is named in ``pending_fields``.
    A required key that is absent, or present with an empty value, is named in ``missing_fields``.
    ``complete`` is true only when no required field is missing and none is pending.
    """
    front_matter, body = _split_front_matter(text)
    raw = _read_key_values(front_matter)

    unknown_fields = sorted(key for key in raw if key not in KNOWN_FIELDS)

    fields: dict[str, Any] = {}
    pending_fields: list[str] = []
    missing_fields: list[str] = []

    for field in KNOWN_FIELDS:
        if field not in raw or not raw[field]:
            if field in REQUIRED_FIELDS:
                missing_fields.append(field)
            fields[field] = None
            continue
        value = _parse_field(field, raw[field])
        fields[field] = value
        if value is None and field in REQUIRED_FIELDS:
            pending_fields.append(field)

    return {
        "source": source,
        "fields": fields,
        "raw_values": raw,
        "derived": _derive(fields),
        "pending_fields": sorted(pending_fields),
        "missing_fields": sorted(missing_fields),
        "unknown_fields": unknown_fields,
        "complete": not pending_fields and not missing_fields,
        "body": body,
    }


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    """Decide whether a record may enter the statistics, and say exactly why when it may not.

    A record is admissible only with a stated equivalence invariant, a passing randomized
    differential test, passing edge cases, a resolved Bitcoin/Core test status, a label from the
    controlled vocabulary, and an evidence level that reflects a ParseAtlas execution. An
    owner-reported figure is never admissible: nothing was measured here. A *pending* evidence
    level is rejected on the same footing as a pending invariant, because a record whose
    provenance is unknown is exactly the "measured here or copied from a report?" case this
    module exists to catch.
    """
    fields = record["fields"]
    reasons: list[str] = []

    for field in record["missing_fields"]:
        reasons.append(f"required field is missing: {field}")

    invariant = fields.get("invariant")
    if invariant is None and "invariant" not in record["missing_fields"]:
        reasons.append("invariant is pending: the equivalence claim is unproven")
    elif invariant is not None and not any(token in invariant for token in ("==", "≡")):
        reasons.append(f"invariant does not state an equivalence claim: {invariant!r}")

    for field in ("validation_random_differential", "validation_edge_cases"):
        status = fields.get(field)
        if status is None:
            if field not in record["missing_fields"]:
                reasons.append(f"validation is pending: {field}")
        elif status not in VALIDATION_STATUSES:
            reasons.append(f"validation status is outside the vocabulary: {field}={status!r}")
        elif status != "pass":
            reasons.append(f"validation did not pass: {field}={status!r}")

    bitcoin = fields.get("validation_bitcoin_core_tests")
    if bitcoin is None:
        if "validation_bitcoin_core_tests" not in record["missing_fields"]:
            reasons.append("validation is pending: validation_bitcoin_core_tests")
    elif bitcoin not in VALIDATION_STATUSES:
        reasons.append(f"validation status is outside the vocabulary: validation_bitcoin_core_tests={bitcoin!r}")
    elif bitcoin == "fail":
        reasons.append("validation did not pass: validation_bitcoin_core_tests='fail'")

    labels = record["derived"]["transformations"]
    if not labels:
        if "transformation" not in record["missing_fields"]:
            reasons.append("transformation label is pending")
    else:
        for label in labels:
            if label not in TRANSFORMATION_VOCABULARY:
                reasons.append(f"transformation label is outside the controlled vocabulary: {label!r}")

    level = fields.get("evidence_level")
    if level is None:
        if "evidence_level" not in record["missing_fields"]:
            reasons.append(
                "evidence level is pending: the provenance of the benchmark is unknown, so the "
                "record cannot be distinguished from a copied figure"
            )
    elif level not in EVIDENCE_LEVELS:
        reasons.append(f"evidence level is outside the vocabulary: {level!r}")
    elif level == "owner-reported":
        reasons.append("evidence level is 'owner-reported': ParseAtlas measured nothing here")

    reasons.extend(_benchmark_consistency_reasons(fields))

    return {
        "source": record.get("source"),
        "record_id": fields.get("record_id"),
        "admissible": not reasons,
        "reasons": reasons,
    }


def _benchmark_consistency_reasons(fields: dict[str, Any]) -> list[str]:
    """Check that a stated delta agrees with the baseline and candidate it claims to summarize."""
    baseline = fields.get("benchmark_baseline")
    candidate = fields.get("benchmark_candidate")
    delta = fields.get("benchmark_delta")
    if baseline is None or candidate is None or delta is None:
        return []
    if baseline <= 0:
        return [f"benchmark_baseline must be positive to define a relative delta: {baseline!r}"]
    recomputed = (candidate - baseline) / baseline * 100.0
    if abs(recomputed - delta) > BENCHMARK_DELTA_TOLERANCE_POINTS:
        return [
            "benchmark_delta disagrees with benchmark_baseline and benchmark_candidate: "
            f"stated {delta!r}, recomputed {recomputed:.4f}"
        ]
    return []


def load_records(directory: str | Path) -> dict[str, Any]:
    """Load every record in a directory, skipping the blank template, with a completeness summary.

    ``EXAMPLE_TEMPLATE.md`` is skipped by name: it is a schema illustration and contributes no
    data. Every other ``.md`` file in the directory must be a well-formed record; a malformed one
    raises rather than being silently dropped.
    """
    base = Path(directory)
    if not base.is_dir():
        raise ValueError(f"{NOT_A_DIRECTORY_MESSAGE}: {base}")

    records: list[dict[str, Any]] = []
    skipped: list[str] = []
    for path in sorted(base.glob("*.md")):
        if path.name == TEMPLATE_FILENAME:
            skipped.append(path.name)
            continue
        try:
            records.append(parse_record(path.read_text(encoding="utf-8"), source=path.name))
        except ValueError as error:
            raise ValueError(f"{path.name}: {error}") from error

    complete = [record for record in records if record["complete"]]
    return {
        "directory": str(base),
        "records": records,
        "skipped": skipped,
        "record_count": len(records),
        "complete_count": len(complete),
        "pending_count": len(records) - len(complete),
        "pending_fields_by_record": {
            record["source"] or f"record[{index}]": record["pending_fields"] + record["missing_fields"]
            for index, record in enumerate(records)
            if not record["complete"]
        },
    }


def _wilson_interval(successes: int, total: int) -> tuple[float, float] | None:
    """Wilson score interval, which stays inside ``[0, 1]`` at the small samples this project has.

    Returns ``None`` for an empty sample. An interval over zero observations is not a wide
    interval, it is no interval at all, and returning one would be an invented number.
    """
    if total <= 0:
        return None
    proportion = successes / total
    denominator = 1.0 + _Z_SCORE**2 / total
    centre = (proportion + _Z_SCORE**2 / (2 * total)) / denominator
    margin = (
        _Z_SCORE
        * math.sqrt(proportion * (1.0 - proportion) / total + _Z_SCORE**2 / (4 * total**2))
        / denominator
    )
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def _classify_outcome(speedup_percent: float, band: float) -> str:
    if speedup_percent > band:
        return "speedup"
    if speedup_percent < -band:
        return "regression"
    return "no_change"


def transformation_statistics(
    records: Iterable[dict[str, Any]],
    no_change_band_percent: float = DEFAULT_NO_CHANGE_BAND_PERCENT,
    minimum_sample_size: int = MINIMUM_RATE_SAMPLE_SIZE,
) -> dict[str, Any]:
    """Count outcomes per transformation label and withhold the rate below the minimum sample.

    Labels are not mutually exclusive: a record naming several transformations is counted under
    each of them, so the per-label totals do not sum to the record count. ``speedup_rate`` is
    ``None`` whenever fewer than the effective minimum sample size backs it, and the raw counts are
    returned regardless so a reader can see exactly why it was withheld.

    ``minimum_sample_size`` may only be raised. :data:`MINIMUM_RATE_SAMPLE_SIZE` is a floor, not a
    default, because the documented sample-size honesty rule is worthless if a caller can lower it
    to 1 and quote ``speedup_rate = 1.0`` from a single record. A lower request is clamped, and the
    result reports ``requested_minimum_sample_size``, ``minimum_sample_size_floor`` and
    ``sample_size_floor_applied`` so the clamp is visible rather than silent.
    """
    materialized = list(records)
    requested_minimum = int(minimum_sample_size)
    effective_minimum = max(requested_minimum, MINIMUM_RATE_SAMPLE_SIZE)
    floor_applied = effective_minimum != requested_minimum

    labels: dict[str, dict[str, Any]] = {
        label: {
            "transformation": label,
            "total_records": 0,
            "admissible_records": 0,
            "rejected_records": 0,
            "measured_records": 0,
            "speedup_count": 0,
            "regression_count": 0,
            "no_change_count": 0,
        }
        for label in TRANSFORMATION_VOCABULARY
    }
    unknown_labels: dict[str, int] = {}

    admissible_total = 0
    for record in materialized:
        verdict = validate_record(record)
        admissible = verdict["admissible"]
        admissible_total += int(admissible)
        speedup_percent = record["derived"]["speedup_percent"]
        for label in record["derived"]["transformations"]:
            if label not in labels:
                unknown_labels[label] = unknown_labels.get(label, 0) + 1
                continue
            bucket = labels[label]
            bucket["total_records"] += 1
            bucket["admissible_records" if admissible else "rejected_records"] += 1
            if not admissible or speedup_percent is None:
                continue
            bucket["measured_records"] += 1
            bucket[f"{_classify_outcome(speedup_percent, no_change_band_percent)}_count"] += 1

    for bucket in labels.values():
        measured = bucket["measured_records"]
        if measured <= 0 or measured < effective_minimum:
            bucket["speedup_rate"] = None
            bucket["confidence_interval"] = None
            bucket["rate_withheld_reason"] = (
                f"{measured} measured record(s) is below the minimum sample size of "
                f"{effective_minimum}; only raw counts may be reported"
            )
        else:
            bucket["speedup_rate"] = bucket["speedup_count"] / measured
            bucket["confidence_interval"] = _wilson_interval(bucket["speedup_count"], measured)
            bucket["rate_withheld_reason"] = None
        bucket["minimum_sample_size"] = effective_minimum
        bucket["requested_minimum_sample_size"] = requested_minimum
        bucket["minimum_sample_size_floor"] = MINIMUM_RATE_SAMPLE_SIZE
        bucket["sample_size_floor_applied"] = floor_applied
        bucket["confidence_level"] = CONFIDENCE_LEVEL

    return {
        "record_count": len(materialized),
        "admissible_count": admissible_total,
        "rejected_count": len(materialized) - admissible_total,
        "minimum_sample_size": effective_minimum,
        "requested_minimum_sample_size": requested_minimum,
        "minimum_sample_size_floor": MINIMUM_RATE_SAMPLE_SIZE,
        "sample_size_floor_applied": floor_applied,
        "sample_size_floor_note": (
            None
            if not floor_applied
            else (
                f"requested minimum sample size {requested_minimum} is below the documented floor "
                f"MINIMUM_RATE_SAMPLE_SIZE = {MINIMUM_RATE_SAMPLE_SIZE}; the floor was applied so "
                "no rate is reported below it"
            )
        ),
        "no_change_band_percent": no_change_band_percent,
        "confidence_level": CONFIDENCE_LEVEL,
        "labels": labels,
        "unknown_labels": unknown_labels,
    }


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Return the Pearson correlation, or ``None`` when either series has no variance.

    Fewer than two paired points cannot have variance, so an empty or singleton sample returns
    ``None`` rather than dividing by zero.
    """
    count = len(xs)
    if count < 2:
        return None
    mean_x = sum(xs) / count
    mean_y = sum(ys) / count
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    variance_x = sum((x - mean_x) ** 2 for x in xs)
    variance_y = sum((y - mean_y) ** 2 for y in ys)
    if variance_x <= 0.0 or variance_y <= 0.0:
        return None
    return covariance / math.sqrt(variance_x * variance_y)


PREDICTOR_FIELDS = ("operation_count_delta", "dependency_depth_delta")


def predictor_correlation(
    records: Iterable[dict[str, Any]],
    minimum_sample_size: int = MINIMUM_CORRELATION_SAMPLE_SIZE,
) -> dict[str, Any]:
    """Correlate measured speedup against each candidate predictor over complete records only.

    The owner's stronger hypothesis is that raw operation count is a poor predictor of measured
    speedup while dependency depth predicts it better. That is a question for this function to
    answer from data, so every predictor returns ``correlation: None`` plus a stated reason until
    enough complete, admissible, measured records exist.

    As in :func:`transformation_statistics`, ``minimum_sample_size`` may only be raised:
    :data:`MINIMUM_CORRELATION_SAMPLE_SIZE` is a floor, and a lower request is clamped and reported
    in ``requested_minimum_sample_size`` / ``sample_size_floor_applied``.
    """
    requested_minimum = int(minimum_sample_size)
    minimum_sample_size = max(requested_minimum, MINIMUM_CORRELATION_SAMPLE_SIZE)
    floor_applied = minimum_sample_size != requested_minimum

    usable = [
        record
        for record in records
        if record["complete"]
        and validate_record(record)["admissible"]
        and record["derived"]["speedup_percent"] is not None
    ]
    speedups = [float(record["derived"]["speedup_percent"]) for record in usable]

    predictors: dict[str, Any] = {}
    for name in PREDICTOR_FIELDS:
        values = [record["derived"][name] for record in usable]
        paired = [(float(value), speedup) for value, speedup in zip(values, speedups) if value is not None]
        sample_size = len(paired)
        if sample_size < minimum_sample_size:
            predictors[name] = {
                "correlation": None,
                "sample_size": sample_size,
                "reason": (
                    f"{sample_size} complete record(s) is below the minimum sample size of "
                    f"{minimum_sample_size}; reporting a correlation here would be spurious"
                ),
            }
            continue
        correlation = _pearson([pair[0] for pair in paired], [pair[1] for pair in paired])
        predictors[name] = {
            "correlation": correlation,
            "sample_size": sample_size,
            "reason": None if correlation is not None else f"predictor {name!r} has no variance in this sample",
        }

    return {
        "sample_size": len(usable),
        "minimum_sample_size": minimum_sample_size,
        "requested_minimum_sample_size": requested_minimum,
        "minimum_sample_size_floor": MINIMUM_CORRELATION_SAMPLE_SIZE,
        "sample_size_floor_applied": floor_applied,
        "predictors": predictors,
        "reason": (
            None
            if len(usable) >= minimum_sample_size
            else (
                f"{len(usable)} complete, admissible, measured record(s) is below the minimum "
                f"sample size of {minimum_sample_size}"
            )
        ),
    }
