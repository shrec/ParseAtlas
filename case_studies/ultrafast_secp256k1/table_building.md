---
record_id: ultrafast-table-building-001
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
evidence_level: owner-reported
owner_reported_claim: approximately 34 percent improvement on table construction
owner_claim_verified: no
---

# Record: Table Construction

> **This record contains no ParseAtlas measurement.** Every measured field above reads
> `PENDING IMPORT`. The 34 percent figure is owner-reported and unverified; it is recorded in
> `owner_reported_claim`, which is not a measurement field, and it is deliberately **not** written
> into `benchmark_delta`. `validate_record` rejects this record from every statistic, and will
> keep rejecting it until the artifacts listed in [`README.md`](README.md) section 4 are imported.

---

## 1. The claim

| | |
| --- | --- |
| Claim as reported | Approximately **34 percent** improvement on table construction. |
| Source | Project owner, reporting results from the external Ultrafast secp256k1 project. |
| Evidence level | `owner-reported` -- below level 1 of [`docs/research-methodology.md`](../../docs/research-methodology.md). |
| Verified by ParseAtlas | No. |
| Reproduced by ParseAtlas | No. |
| Admissible into statistics | No. |

## 2. Record fields

Every field in this table is a ParseAtlas measurement slot. All of them are pending.

| Field | Value |
| --- | --- |
| Primitive | PENDING IMPORT |
| Baseline representation | PENDING IMPORT |
| Candidate representation | PENDING IMPORT |
| Invariant | `candidate == baseline` -- stated as the obligation; **not yet discharged** |
| Transformation | PENDING IMPORT |
| Before | PENDING IMPORT |
| After | PENDING IMPORT |
| Operation delta -- mul | PENDING IMPORT |
| Operation delta -- sqr | PENDING IMPORT |
| Operation delta -- add | PENDING IMPORT |
| Operation delta -- sub | PENDING IMPORT |
| Operation delta -- reduce | PENDING IMPORT |
| Dependency depth -- before | PENDING IMPORT |
| Dependency depth -- after | PENDING IMPORT |
| Benchmark -- baseline | PENDING IMPORT |
| Benchmark -- candidate | PENDING IMPORT |
| Benchmark -- delta | PENDING IMPORT |
| Benchmark -- unit | PENDING IMPORT |
| Benchmark -- machine | PENDING IMPORT |
| Benchmark -- repetitions | PENDING IMPORT |
| Benchmark -- dispersion | PENDING IMPORT |
| Validation -- random differential | PENDING IMPORT |
| Validation -- edge cases | PENDING IMPORT |
| Validation -- Bitcoin/Core tests | PENDING IMPORT |

The `Transformation` field is pending rather than filled in because assigning a label from the
controlled vocabulary would be a statement about the mechanism, and the mechanism is exactly what
is not yet known. Section 4 is a hypothesis about that mechanism; a hypothesis does not get to
populate a label that the statistics will later condition on.

## 3. Equivalence obligation

The invariant a table-construction rewrite must satisfy is that the constructed table is
**element-for-element identical** to the baseline table, or -- if the candidate stores points in a
different coordinate system or scaling -- that every stored entry represents the same curve point
as the corresponding baseline entry:

```text
candidate[i] == baseline[i]                      for every table index i
```

or, for a projective representation,

```text
candidate[i] and baseline[i] represent the same affine point
```

Neither form has been checked by ParseAtlas. The derivation that would make it true is
**PENDING IMPORT**, and the differential test that would provide evidence for it is
**PENDING IMPORT**.

A table-construction rewrite has a specific hazard that a single-primitive rewrite does not: the
table is consumed later by scalar multiplication, so an error in one rarely used entry can survive
ordinary testing and surface only for particular scalars. The edge-case obligation therefore
includes full enumeration of the table's index space, not sampling of it.

## 4. HYPOTHESIS: why a gain of this size would be scientifically interesting

**Evidence level: hypothesized.** This section proposes a mechanism to test. It is not a finding,
it does not report a measurement, and nothing in it should be cited as evidence that the 34
percent figure is correct, or that any particular cost dimension moved.

A reported improvement of roughly one third is interesting precisely because of its *size*.
Removing a single instruction from a hot loop does not usually produce that. On a primitive whose
cost is dominated by field multiplications, deleting one multiplication out of, say, a dozen buys
single-digit percent. A gain approaching a third suggests the rewrite moved **several cost
dimensions at once**, and that the dimensions interacted.

The candidate dimensions are:

| Dimension | Why it could contribute | ParseAtlas measurement |
| --- | --- | --- |
| Operation count | Fewer field multiplications, squarings, or reductions per table entry. | PENDING IMPORT |
| Dependency graph | A shorter critical path lets the out-of-order engine overlap more work per cycle even at constant operation count. | PENDING IMPORT |
| Reduction frequency | Deferred or merged modular reductions remove work that is invisible in a naive operation count. | PENDING IMPORT |
| Temporary lifetime | Shorter-lived temporaries reduce live ranges and the spill traffic they cause. | PENDING IMPORT |
| Register pressure | Fewer simultaneously live values means fewer spills and reloads on a register-starved target. | PENDING IMPORT |
| Instruction-level parallelism | More independent chains means more useful work issued per cycle. | PENDING IMPORT |

Two things make this worth stating as a hypothesis rather than leaving implicit.

**First, these are exactly the dimensions ParseAtlas was built to measure.** The root README lists
operation counts, dependency depth, temporary values, memory traffic, and register pressure as the
representation-cost metrics; ROADMAP Phase 13 lists dependency depth, register pressure, and
spills among the performance metrics for this branch. If the mechanism really is multi-dimensional,
then a single-number benchmark cannot distinguish the contributions, and the decomposition is the
contribution ParseAtlas can make that a stopwatch cannot.

**Second, it is a falsifiable prediction.** The hypothesis predicts that the operation-count delta
alone will *under-explain* the measured gain -- that is, that a cost model counting only
multiplications and squarings will predict substantially less than the measured improvement. The
prediction fails if the imported operation counts turn out to account for the gain on their own.
Either outcome is informative, and the second would be the more surprising one given experiment
0021.

### 4.1 Connection to experiment 0021

Experiment 0021 measured, over a six-expression corpus and 25 grammars, that the raw operation
multiset is invariant under grammar change while critical-path depth is not: the same six
operations of `a/b + c*d - e/f + g` -- `add` 2, `sub` 1, `mul` 1, `div` 2, across 13 AST nodes --
arrange into dependency chains of depth 4 to 6, and only 4 of 25 grammars reach the minimum depth
of 4. Six is the operation count and thirteen is the node count; they are different quantities and
neither may be quoted for the other. That experiment measured structure and made no timing claim.

The bridge to this record is a prediction, not a result: if the quantity that *does not move* when
representation changes is operation count, then operation count is a poor candidate for explaining
what happens when representation changes, and dependency structure is a better one. This record is
one of the places that prediction can be tested against a real measurement --
see [`benchmark_summary.md`](benchmark_summary.md) section 4.

### 4.2 Competing explanations that must be excluded

Before the mechanism above can be considered supported, the import must rule out explanations that
have nothing to do with representation:

* the two measured builds differ in more than the rewrite (**PENDING IMPORT**: the diff);
* the compiler chose a different code path, vectorization, or inlining decision for reasons
  incidental to the rewrite (**PENDING IMPORT**: the compiler and flags);
* the baseline was measured cold, or on a different clock state, or in a different session
  (**PENDING IMPORT**: the harness and environment);
* the gain is a memory-layout or cache effect of the table itself rather than an arithmetic effect
  (**PENDING IMPORT**: the table layout, before and after);
* the improvement is within run-to-run dispersion (**PENDING IMPORT**: the dispersion).

## 5. Next action

Import the artifacts in [`README.md`](README.md) section 4, fill the fields of section 2, move the
record into [`records/`](records/), and re-run `python -m pytest -q`. Do not fill any field from
memory, from prose, or from a recollected figure.
