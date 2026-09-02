# Case Study: Ultrafast (secp256k1)

> **Verification status: NOTHING IN THIS DIRECTORY HAS BEEN VERIFIED BY ParseAtlas.**
> Every figure below is owner-reported. No benchmark artifact, no source file, and no test result
> from the Ultrafast project has been imported into this repository. ParseAtlas has executed
> nothing against that codebase.

---

## 1. What Ultrafast is

Ultrafast is an **external** secp256k1 implementation project maintained by the same owner as
ParseAtlas. It is a separate repository with its own source, its own benchmark harness, and its
own test suite. ParseAtlas has no access to any of it.

It is relevant here because it is the first place where the project's second research mode --
equivalence-preserving representation search, described in [`../README.md`](../README.md) -- has
been applied to real code rather than to symbolic expressions. Ultrafast rewrites are constrained
in exactly the way ROADMAP Phase 12 and Phase 13 require: the candidate must compute the same
field element or the same curve point as the baseline, and only the cost may change.

The target field is:

```text
p = 2^256 - 2^32 - 977
```

## 2. What is claimed

Two claims have been reported by the owner. Both are recorded here verbatim, and both are
**unverified**.

| # | Claim as reported | Status |
| --- | --- | --- |
| 1 | Approximately **34 percent** improvement on table construction. | Owner-reported. Unverified. Awaiting import of primary artifacts. |
| 2 | Repeated improvements in the **7 to 10 percent** range across assorted field primitives and hot paths. | Owner-reported. Unverified. Awaiting import of primary artifacts. |

Neither figure appears in any measurement field of any record in this directory. Both live in the
`owner_reported_claim` front-matter field, which exists precisely so that an external figure has a
place that is not a measurement. Every measured field in
[`table_building.md`](table_building.md) and [`field_primitives.md`](field_primitives.md) reads
`PENDING IMPORT`.

The reported figures are not doubted. They are simply not yet evidence *in this repository*, and
this repository's rules do not permit a figure to be treated as evidence on the strength of having
been mentioned.

## 3. What ParseAtlas has verified

Nothing.

That is the complete and accurate answer. Specifically, ParseAtlas has **not**:

* read any Ultrafast source file, in either its baseline or its candidate form;
* run, or observed the output of, any Ultrafast benchmark;
* reproduced any timing measurement on any machine;
* confirmed that any candidate representation is equivalent to its baseline;
* run any differential test, edge-case test, or upstream test suite;
* determined the operation counts, dependency depths, register pressure, or instruction-level
  parallelism of any rewrite;
* established that the rewrites are attributable to representation search rather than to unrelated
  changes made in the same period.

What ParseAtlas *has* done is build the intake structure: the record schema
([`../RECORD_SCHEMA.md`](../RECORD_SCHEMA.md)), the admission gate and statistics engine
([`../../src/parseatlas/case_study.py`](../../src/parseatlas/case_study.py)), and the empty
record slots in this directory.

## 4. Required primary artifacts

The following artifacts must be imported before **any** figure in this directory is promoted from
`owner-reported` to `benchmarked`. This is a checklist, not a wish list: a record's
`evidence_level` stays at `owner-reported`, and `validate_record` keeps rejecting it from every
statistic, until the corresponding items land.

### 4.1 Benchmark harness

* [ ] The benchmark source itself, so the timed region can be inspected. **PENDING IMPORT**
* [ ] The exact command lines used to build and to run it. **PENDING IMPORT**
* [ ] The warm-up policy and how the timed region is isolated from setup. **PENDING IMPORT**
* [ ] Whether the timer measures wall-clock nanoseconds or cycle counts, and which counter.
  **PENDING IMPORT**

### 4.2 Environment

* [ ] CPU model and microarchitecture. **PENDING IMPORT**
* [ ] Clock policy during measurement: turbo, frequency scaling, thermal state, core pinning.
  **PENDING IMPORT**
* [ ] Operating system and kernel version. **PENDING IMPORT**
* [ ] Compiler and exact version. **PENDING IMPORT**
* [ ] Optimization flags, target architecture flags, and link-time settings. **PENDING IMPORT**
* [ ] Whether assembly, intrinsics, or a compiler-chosen code path is involved. **PENDING IMPORT**

### 4.3 Repetition counts and variance

* [ ] Repetition count per timed measurement. **PENDING IMPORT**
* [ ] Number of independent runs. **PENDING IMPORT**
* [ ] Dispersion of the measurements: standard deviation, or median with interquartile range.
  **PENDING IMPORT**
* [ ] Whether baseline and candidate were measured in the same session on the same binary and the
  same machine. **PENDING IMPORT**

A delta without dispersion cannot be distinguished from noise, so section 4.3 is not optional
detail. It is the difference between a measurement and an anecdote.

### 4.4 Before/after source of each rewrite

* [ ] The baseline representation of each primitive, as source. **PENDING IMPORT**
* [ ] The candidate representation of each primitive, as source. **PENDING IMPORT**
* [ ] The diff, so it can be confirmed that the rewrite is the only change between the two
  measured builds. **PENDING IMPORT**
* [ ] The equivalence argument for each rewrite. **PENDING IMPORT**

### 4.5 Differential-test results

* [ ] Randomized differential test of candidate against baseline: sample count and random seed.
  **PENDING IMPORT**
* [ ] Edge-case results: zero, one, `p-1`, values straddling the reduction boundary,
  non-canonical limb states, carry boundaries, and the point at infinity. **PENDING IMPORT**
* [ ] Upstream Bitcoin/Core test-suite results for the candidate build. **PENDING IMPORT**

### 4.6 INTAKE CHECKLIST -- copy this, fill it in, paste it back

Section 4 above says what is required and why. This section is the same list flattened into
something the owner can act on **without reading the schema**. Copy the block below into a file or
a message, replace each `>>` line with the real value, and paste it back. A `>>` line left
untouched is a field that stays `PENDING IMPORT`; do not delete a line to make the list look
finished, and do not fill one from memory.

Nothing here needs to be complete before something is sent. Item 1 alone is worth more than the
rest of this directory, because a harness that can be run is a claim that can be checked.

```text
ULTRAFAST -> ParseAtlas INTAKE, claim 1 (34 percent on table construction)

 1. BENCHMARK HARNESS
    >> path/name of the benchmark source file:
    >> paste the timed region verbatim (the loop that is measured):
    >> exact BUILD command line:
    >> exact RUN command line:
    >> warm-up policy (iterations discarded before timing, if any):
    >> what the timer reads (wall-clock ns / rdtsc / perf counter -- name it):

 2. MACHINE AND TOOLCHAIN
    >> CPU model, exactly as reported by the OS:
    >> microarchitecture:
    >> turbo / frequency scaling state during the run (on, off, pinned to N GHz):
    >> core pinning (yes/no, which core):
    >> OS and kernel version:
    >> compiler and exact version (e.g. gcc 13.2.0, clang 17.0.6):
    >> optimization flags, verbatim:
    >> target/arch flags, verbatim:
    >> assembly or intrinsics involved (yes/no; if yes, which):

 3. REPETITIONS AND DISPERSION
    >> repetitions per timed measurement:
    >> number of independent runs:
    >> dispersion: standard deviation, OR median + interquartile range:
    >> baseline and candidate measured in the same session, same machine (yes/no):
    >> raw baseline figure and unit (ns/op or cycles/op):
    >> raw candidate figure and the SAME unit:
    (ParseAtlas recomputes the percentage from these two numbers. Do not send the percentage
     on its own: a delta that cannot be recomputed cannot be admitted.)

 4. THE REWRITE ITSELF
    >> BEFORE source, verbatim (the baseline representation, not a description):
    >> AFTER source, verbatim (the candidate representation, not a description):
    >> the diff between the two measured builds, so it is visible that the rewrite is the
       only change:
    >> the equivalence argument: why AFTER computes the same value as BEFORE:

 5. RANDOMIZED DIFFERENTIAL TEST
    >> test source or command line:
    >> number of random iterations:
    >> random seed (an unreproducible test result is not a test result):
    >> input distribution / domain sampled:
    >> result: pass / fail

 6. EDGE CASES -- list each one and its result, do not summarize as "edge cases pass"
    >> zero:
    >> one:
    >> p-1:
    >> values straddling the reduction boundary:
    >> non-canonical limb states:
    >> carry boundaries:
    >> point at infinity (if the primitive touches points):
    >> every table index, enumerated not sampled (table construction only):
    >> any primitive-specific boundary not listed above:

 7. UPSTREAM TEST SUITE
    >> Bitcoin Core / libsecp256k1 test suite result for the candidate build:
    >> command line used:
    >> if not applicable, state why the primitive is unreachable from that suite:
```

Once items 1 through 7 are filled, everything ParseAtlas needs to promote the record from
`owner-reported` to `benchmarked` is present. Section 5 is then a mechanical transcription.

## 5. Promotion procedure

1. Import the artifacts of section 4 into this directory, unmodified and attributed.
2. Fill the corresponding front-matter fields in the record, replacing `PENDING IMPORT` with the
   imported values and nothing else.
3. Re-derive `benchmark_delta` from the imported baseline and candidate figures rather than
   copying a percentage from prose. `validate_record` recomputes it and rejects a disagreement
   greater than 0.5 percentage points.
4. Set `evidence_level` to `benchmarked` only once the validation fields all read `pass`.
5. Move the record into [`records/`](records/) so `load_records` picks it up.
6. Re-run `python -m pytest -q`.

Until step 5 is done for at least one record, `load_records` on this study's `records/` directory
returns zero records, `transformation_statistics` reports zero measured records for every label
with the rate withheld, and `predictor_correlation` returns `None` with an explicit
insufficient-data reason. That is the correct output for the current state of evidence.

## 6. Contents

| File | What it is |
| --- | --- |
| [`table_building.md`](table_building.md) | The record slot for claim 1, plus the hypothesis about why a gain of that size is scientifically interesting. |
| [`field_primitives.md`](field_primitives.md) | The intake table for claim 2, one row per ROADMAP Phase 13 primitive. |
| [`benchmark_summary.md`](benchmark_summary.md) | The aggregate view and the statistical question to answer once 20-30 records exist. |
| [`records/EXAMPLE_TEMPLATE.md`](records/EXAMPLE_TEMPLATE.md) | Blank schema template. Skipped by `load_records`. Contains no data. |
