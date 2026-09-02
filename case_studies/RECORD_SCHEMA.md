# ParseAtlas Case-Study Record Schema

This document is **normative**. It defines the record format for the equivalence-preserving
representation-search mode, the proof obligation a record must discharge before it is admitted,
the controlled vocabulary for the `Transformation` field, and the machine-readable front-matter
block parsed by [`src/parseatlas/case_study.py`](../src/parseatlas/case_study.py).

A record that does not conform is not a weaker record. It is not a record.

---

## 1. The placeholder rule

Any field whose value is not yet known must read exactly:

```text
PENDING IMPORT
```

Uppercase, two words, no punctuation, no decoration. This exact string is the only accepted
placeholder, and `parse_record` maps it to `None`.

Three things are therefore forbidden, and each of them is forbidden because a reader must never be
able to mistake a placeholder for a measurement:

1. writing `0`, `-`, `n/a`, `TBD`, `?`, or an empty value where a number is not yet known;
2. writing an estimated, interpolated, or "reasonable" number;
3. writing a number obtained from anywhere other than the imported primary artifact.

`PENDING IMPORT` never becomes `0` anywhere in the pipeline. This is asserted by
`tests/test_case_study.py`.

---

## 2. Field layout

A record is one Markdown file. It begins with the front-matter block of section 5 and continues
with prose. The human-readable field layout, which the prose section reproduces, is:

```text
Primitive:                  <name of the primitive being rewritten>
Baseline representation:    <the representation being replaced>
Candidate representation:   <the proposed replacement>

Invariant:                  candidate == baseline

Transformation:             <one or more labels from the closed vocabulary in section 4>

Before:                     <the baseline expression, sequence, or code>
After:                      <the candidate expression, sequence, or code>

Operation delta:            mul <n>  sqr <n>  add <n>  sub <n>  reduce <n>
Dependency depth:           before <n>  after <n>

Benchmark:                  baseline <v>  candidate <v>  delta <p>
Validation:                 random differential <status>
                            edge cases <status>
                            Bitcoin/Core tests <status>
```

---

## 3. Field definitions

### 3.1 Identity and representations

| Field | Meaning |
| --- | --- |
| `record_id` | Stable, unique, lowercase-hyphenated identifier. Never reused, never renumbered. |
| `primitive` | The primitive being rewritten, named as the upstream project names it. |
| `baseline_representation` | The representation being replaced, precisely enough to be reimplemented. |
| `candidate_representation` | The proposed replacement, at the same level of precision. |

`Before` and `After` in the prose body carry the actual two representations: expression,
instruction sequence, or source extract. A record whose `Before`/`After` are prose summaries
rather than the real thing cannot be independently rechecked and is not publishable.

### 3.2 Invariant

`invariant` states the equivalence claim that makes the rewrite legitimate. The normative forms
are:

```text
candidate == baseline                      # exact equality of the computed value
candidate ≡ baseline mod p                 # finite-field equality, p declared in the body
candidate and baseline represent the same affine point
```

The field must contain `==` or `≡`. This is the load-bearing field of the entire schema: without
it, a "faster" candidate is simply a different function, which is the semantic-exploration mode
and does not belong in this directory. See [`README.md`](README.md).

The prose body must also carry the **equivalence argument**: the algebraic derivation, identity
chain, or coordinate argument that makes the invariant true. A test result is evidence; it is not
the argument.

### 3.3 Transformation

`transformation` names one or more labels from the closed vocabulary of section 4, separated by
commas. Labels are **not mutually exclusive**: a rewrite that both reassociates and reuses a
common subexpression names both. Consequently the per-label totals in
`transformation_statistics` do not sum to the record count, and the summary reports that.

### 3.4 Operation delta

`op_delta_mul`, `op_delta_sqr`, `op_delta_add`, `op_delta_sub`, `op_delta_reduce`.

Signed integer counts, `candidate - baseline`. Negative means the candidate performs fewer of
that operation. Counted at the field-operation level of the primitive under study, not at machine
instruction level; if the project counts them differently, the body states how.

`operation_count_delta` is derived as the sum of the five fields, and is `None` while any one of
them is pending.

### 3.5 Dependency depth

`depth_before`, `depth_after`. The longest chain of data-dependent operations in each
representation, measured the same way experiment 0021 measures critical-path depth: the length of
the dependency chain, not a latency. `dependency_depth_delta` is derived as
`depth_after - depth_before`; negative means a shorter critical path.

### 3.6 Benchmark

| Field | Meaning |
| --- | --- |
| `benchmark_baseline` | Measured cost of the baseline, in `benchmark_unit`. |
| `benchmark_candidate` | Measured cost of the candidate, in the same unit. |
| `benchmark_delta` | Signed relative change in percent: `(candidate - baseline) / baseline * 100`. |
| `benchmark_unit` | The unit. One of `ns/op` or `cycles/op`. Stated, never assumed. |
| `benchmark_machine` | CPU model, frequency policy, OS, compiler and version, optimization flags. |
| `benchmark_repetitions` | Repetition count of the timed measurement. |

**Sign convention.** `benchmark_delta` is negative when the candidate is cheaper. A 34 percent
improvement is `-34.0`, not `34.0`. `speedup_percent` is derived as `-benchmark_delta`, so a
speedup is positive there. `validate_record` recomputes the delta from baseline and candidate and
rejects a record whose stated delta disagrees by more than 0.5 percentage points, which catches a
flipped sign before it reaches a statistic.

**Variance is mandatory.** The prose body must report the dispersion of the timed runs (standard
deviation, or median with interquartile range) alongside the repetition count. A delta without
dispersion cannot be distinguished from noise. Until every record carries dispersion, the engine
uses a stated dead band, `DEFAULT_NO_CHANGE_BAND_PERCENT = 1.0` percentage points, inside which a
measured delta counts as no change. That band is a convention, not a measurement, and it is to be
replaced by a variance-based test as soon as the records support one.

### 3.7 Validation

| Field | Meaning |
| --- | --- |
| `validation_random_differential` | Randomized differential test of candidate against baseline. |
| `validation_edge_cases` | Structured edge cases: zero, one, `p-1`, the point at infinity, non-canonical limb states, carry boundaries, and any primitive-specific boundary. |
| `validation_bitcoin_core_tests` | The upstream project's own test suite. |

Each takes one of `pass`, `fail`, `not applicable`, or `PENDING IMPORT`. `not applicable` is
permitted only for `validation_bitcoin_core_tests`, and only when the primitive is not reachable
from that suite; the body must say why.

The prose body must state the differential test's sample count and its random seed, because an
unreproducible test result is not a test result.

### 3.8 Evidence level

`evidence_level` takes one of the levels from
[`docs/research-methodology.md`](../docs/research-methodology.md) --
`observed`, `symbolically-justified`, `numerically-validated`, `hypothesized`, `benchmarked` --
or the intake level `owner-reported`.

`owner-reported` sits **below** level 1 of the methodology. It means an external party stated the
figure and ParseAtlas has executed nothing. It is never admissible into statistics, and
`validate_record` rejects it explicitly with that reason.

`PENDING IMPORT` is rejected on exactly the same footing, and for the same reason as a pending
invariant: a record whose evidence level is unknown is a benchmark number whose provenance is
unknown, which is precisely the "measured here, or copied from a report?" case this schema exists
to make impossible. A pending evidence level is therefore never admissible either.

---

## 4. Controlled vocabulary for `Transformation`

This is a **closed list**. An unlisted label is a rejection, not a new class. The entire
statistical question -- which transformation classes actually yield speedups -- is only answerable
if these labels stay consistent across every record, so extending the list is a deliberate schema
change that requires re-labelling the existing corpus, not an ad-hoc addition inside one record.

| Label | Meaning |
| --- | --- |
| `limb layout` | Changing the number, width, or packing of limbs in the field representation. |
| `projective scaling` | Choosing a different representative of a projective point, or a different scaling of the coordinates, **within one coordinate system**. |
| `sign relocation` | Moving a negation across an expression, including negating a constant instead of a variable. |
| `factorization` | Extracting a shared factor so a product is computed once instead of repeatedly. |
| `reassociation` | Applying associativity to reorder the evaluation of an associative chain, which is the same thing as regrouping its operands. |
| `reduction placement` | Moving a modular reduction to a different point in the computation while performing the **same number** of reductions. |
| `lazy reduction` | Deferring, merging, or **eliminating** modular reductions while staying inside the representation's bound, so the reduction count falls. |
| `coordinate systems` | Computing the same curve point through a different point representation: affine, Jacobian, Chudnovsky, or a mixed form. |
| `addition chain` | Replacing an exponentiation or scalar chain with a different addition/doubling chain. |
| `common-subexpression reuse` | Computing a repeated subexpression once and reusing the result. |
| `operation scheduling` | Reordering independent operations to change the dependency structure or register lifetime, without changing the operation multiset. |

### 4.1 Provenance: relation to the ROADMAP Phase 13 dimension list

This vocabulary is **derived from, and in one-to-one correspondence with**, the eleven
"Representation dimensions" of ROADMAP Phase 13. It is not a verbatim copy: three labels are
deliberate renames, adopted so the label names the *transformation* rather than the *property*, and
the renames are recorded here rather than left to be inferred.

| ROADMAP Phase 13 dimension | Schema label | Relation |
| --- | --- | --- |
| limb layout | `limb layout` | verbatim |
| projective scaling | `projective scaling` | verbatim |
| sign placement | `sign relocation` | renamed -- the label names the act of moving the sign, not where it sits |
| factorization | `factorization` | verbatim |
| associativity | `reassociation` | renamed -- associativity is the algebraic property; reassociation is the transformation that uses it |
| reduction placement | `reduction placement` | verbatim |
| lazy reduction | `lazy reduction` | verbatim |
| coordinate systems | `coordinate systems` | verbatim |
| addition chains | `addition chain` | renamed -- singular, because one record names the one chain it substituted |
| common-subexpression reuse | `common-subexpression reuse` | verbatim |
| operation scheduling | `operation scheduling` | verbatim |

The mapping is encoded as `ROADMAP_PHASE_13_DIMENSION_LABELS` in
[`src/parseatlas/case_study.py`](../src/parseatlas/case_study.py), `TRANSFORMATION_VOCABULARY` is
derived from it, and `tests/test_case_study.py` asserts the ROADMAP wording, the code and this
table stay in step. A dimension cannot be dropped without the test failing.

**Two pairs are deliberately distinct and must not be collapsed.**

* `reduction placement` versus `lazy reduction`. Moving a reduction is not removing one. A rewrite
  that performs the same number of reductions at different points changes the dependency structure
  and the operand bounds but not the reduction count; a rewrite that defers or merges reductions
  changes the count. Those are different mechanisms with different proof obligations -- lazy
  reduction requires a bound argument that reduction placement does not -- so they are different
  labels, and the statistics must be able to tell them apart.
* `coordinate systems` versus `projective scaling`. Rescaling `(X : Y : Z)` to `(λ²X : λ³Y : λZ)`
  chooses a different representative inside Jacobian coordinates. Switching Jacobian to affine, or
  to Chudnovsky, changes the system itself, and with it the operation counts of every subsequent
  point operation. For secp256k1 the second is a first-class transformation, not a special case of
  the first.

**One label was removed.** An earlier draft of this list carried `regrouping`, defined as "changing
which operands are grouped together". That has no counterpart in the ROADMAP list and no content
that `reassociation` does not already have: regrouping the operands of an associative chain *is*
applying associativity. It was removed rather than kept, because a label that overlaps another
label silently splits the same mechanism across two buckets and makes both rates wrong. There is no
corpus to re-label: the removal happened while `records/` was still empty, which is the only point
at which a closed vocabulary can be corrected cheaply.

---

## 5. Machine-readable front-matter block

Every record file begins with this block. The first non-empty line must be `---`, and the block is
closed by a second `---`. Lines are `key: value`. A line whose first non-space character is `#` is
a comment. A duplicated key is an error, not a last-wins overwrite.

```text
---
record_id: PENDING IMPORT
primitive: PENDING IMPORT
baseline_representation: PENDING IMPORT
candidate_representation: PENDING IMPORT
invariant: candidate == baseline
transformation: PENDING IMPORT
op_delta_mul: PENDING IMPORT
op_delta_sqr: PENDING IMPORT
op_delta_add: PENDING IMPORT
op_delta_sub: PENDING IMPORT
op_delta_reduce: PENDING IMPORT
depth_before: PENDING IMPORT
depth_after: PENDING IMPORT
benchmark_baseline: PENDING IMPORT
benchmark_candidate: PENDING IMPORT
benchmark_delta: PENDING IMPORT
benchmark_unit: PENDING IMPORT
benchmark_machine: PENDING IMPORT
benchmark_repetitions: PENDING IMPORT
validation_random_differential: PENDING IMPORT
validation_edge_cases: PENDING IMPORT
validation_bitcoin_core_tests: PENDING IMPORT
evidence_level: PENDING IMPORT
---
```

### 5.1 Required keys

All twenty-three keys above are required. A key that is absent, or present with an empty value, is
reported in `missing_fields`, which is a different condition from `PENDING IMPORT`: pending means
"known to be unknown", missing means "the record does not conform".

### 5.2 Optional keys

| Key | Meaning |
| --- | --- |
| `owner_reported_claim` | A figure stated by an external party, recorded verbatim. Never a measurement. |
| `owner_claim_verified` | `yes` or `no`. Whether ParseAtlas has imported artifacts that confirm the claim. |
| `notes` | Free text. |

`owner_reported_claim` exists precisely so that an unverified external figure has a place to live
that is not a measurement field. Putting such a figure into `benchmark_delta` is a fabrication.

### 5.3 Parsed shape

`parse_record(text, source=None)` returns:

| Key | Meaning |
| --- | --- |
| `fields` | Typed values. `None` wherever the value was `PENDING IMPORT` or missing. |
| `raw_values` | The unparsed strings, so the original text is always recoverable. |
| `derived` | `operation_count_delta`, `dependency_depth_delta`, `speedup_percent`, `transformations`. Each is `None` (or empty) while any input is pending. |
| `pending_fields` | Required fields present with the placeholder. |
| `missing_fields` | Required fields absent or empty. |
| `unknown_fields` | Keys outside the schema. |
| `complete` | True only when both `pending_fields` and `missing_fields` are empty. |
| `body` | The Markdown after the front matter. |

---

## 6. The proof obligation

**A record may not be admitted to any statistic without all three of the following.** This is not
a style preference. A speedup on a rewrite that is not actually equivalent is not a result; in
cryptographic code it is a vulnerability.

1. **An equivalence argument.** A stated `invariant` plus, in the body, the algebraic or geometric
   derivation that makes it true.
2. **A randomized differential test.** Candidate and baseline evaluated on random inputs across
   the declared domain and compared, with the sample count and the seed recorded.
3. **Edge cases.** The structured boundaries of section 3.7, enumerated explicitly, not summarized
   as "edge cases pass".

`validate_record(record)` enforces this and returns `{"admissible": bool, "reasons": [...]}`. It
rejects a record when the invariant is missing or pending, when it does not state an equivalence
claim, when either the differential test or the edge cases is missing, pending, failing, or
outside the status vocabulary, when the Bitcoin/Core status is unresolved, when the transformation
label is missing or pending or outside the vocabulary, when the evidence level is missing, pending,
outside the vocabulary, or `owner-reported`, and when the stated benchmark delta contradicts the
baseline and candidate it claims to summarize.

The six fields carrying the proof obligation -- `invariant`, `transformation`, the three
`validation_*` fields, and `evidence_level` -- are treated identically when pending. None of them
has a tolerated pending state, because each of them individually is enough to turn a plausible
record into an unfalsifiable one.

Rejection is never silent: `transformation_statistics` reports `rejected_records` per label
alongside `admissible_records`, so a directory full of unproven records is visible as such rather
than invisible.

---

## 7. File placement

```text
case_studies/
  README.md                        the two research modes and the boundary between them
  RECORD_SCHEMA.md                 this document
  <study>/README.md                what the study is, and what has and has not been verified
  <study>/records/                 one file per record; load_records reads this directory
  <study>/records/EXAMPLE_TEMPLATE.md   blank template, skipped by name, contributes no data
```

`load_records(directory)` reads every `.md` file in a records directory, skips
`EXAMPLE_TEMPLATE.md` by name, and raises on any other malformed file rather than dropping it
silently. Narrative documents belong beside `records/`, not inside it.
