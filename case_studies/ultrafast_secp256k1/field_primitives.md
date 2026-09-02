# Intake Table: Field and Curve Primitives

> **This document contains no ParseAtlas measurement.** Every cell in every table below reads
> `PENDING IMPORT`. It is an empty intake grid, sized to the primitive list in ROADMAP Phase 13,
> waiting for the artifacts listed in [`README.md`](README.md) section 4.

---

## 1. The claim this grid is waiting on

| | |
| --- | --- |
| Claim as reported | Repeated improvements in the **7 to 10 percent** range across assorted field primitives and hot paths. |
| Source | Project owner, reporting results from the external Ultrafast secp256k1 project. |
| Evidence level | `owner-reported` -- below level 1 of [`docs/research-methodology.md`](../../docs/research-methodology.md). |
| Verified by ParseAtlas | No. |
| Admissible into statistics | No. |

The claim says **"assorted"**. It does not say which primitives were rewritten, how many were,
or which of them carried which figure. Assigning the 7-10 percent range to any specific row below
would therefore invent a mapping that was never reported, so no row carries a number and no row is
marked as improved. The `Rewrite reported` column exists to hold that answer once it is imported;
until then it too is pending.

The rows are the twelve primitive targets of ROADMAP Phase 13. Their presence in this grid means
"this primitive is in scope for the case study", not "this primitive was rewritten" and certainly
not "this primitive got faster".

## 2. Rewrite identification

| # | Primitive | Rewrite reported | Record id | Transformation |
| --- | --- | --- | --- | --- |
| 1 | field addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 2 | field subtraction | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 3 | field multiplication | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 4 | field squaring | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 5 | field reduction | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 6 | field inversion | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 7 | square root | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 8 | affine point addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 9 | Jacobian point addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 10 | mixed Jacobian-affine addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 11 | point doubling | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 12 | scalar multiplication | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |

## 3. Structural cost

Signed deltas, `candidate - baseline`. Negative means the candidate does less of that operation.
Dependency depth is the longest chain of data-dependent operations, measured the way experiment
0021 measures critical-path depth.

| # | Primitive | mul | sqr | add | sub | reduce | depth before | depth after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | field addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 2 | field subtraction | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 3 | field multiplication | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 4 | field squaring | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 5 | field reduction | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 6 | field inversion | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 7 | square root | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 8 | affine point addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 9 | Jacobian point addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 10 | mixed Jacobian-affine addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 11 | point doubling | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 12 | scalar multiplication | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |

## 4. Measured cost

`Delta` is the signed relative change `(candidate - baseline) / baseline * 100`; negative is a
speedup. `Dispersion` is the standard deviation of the timed runs, or the interquartile range
around the median. A delta without dispersion is not a measurement.

| # | Primitive | Unit | Baseline | Candidate | Delta % | Repetitions | Dispersion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | field addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 2 | field subtraction | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 3 | field multiplication | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 4 | field squaring | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 5 | field reduction | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 6 | field inversion | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 7 | square root | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 8 | affine point addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 9 | Jacobian point addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 10 | mixed Jacobian-affine addition | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 11 | point doubling | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 12 | scalar multiplication | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |

The measurement machine is a single environment shared by every row and is recorded once, in
[`README.md`](README.md) section 4.2. It is **PENDING IMPORT**.

## 5. Equivalence and validation

No row may leave this document for [`records/`](records/) until its whole row here reads `pass`.
`validate_record` enforces the same rule in code.

| # | Primitive | Invariant form | Equivalence argument | Random differential | Edge cases | Bitcoin/Core tests |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | field addition | `candidate ≡ baseline mod p` | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 2 | field subtraction | `candidate ≡ baseline mod p` | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 3 | field multiplication | `candidate ≡ baseline mod p` | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 4 | field squaring | `candidate ≡ baseline mod p` | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 5 | field reduction | `candidate ≡ baseline mod p` | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 6 | field inversion | `candidate ≡ baseline mod p` | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 7 | square root | `candidate ≡ baseline mod p`, with the branch convention declared | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 8 | affine point addition | same affine point | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 9 | Jacobian point addition | same affine point | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 10 | mixed Jacobian-affine addition | same affine point | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 11 | point doubling | same affine point | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |
| 12 | scalar multiplication | same affine point | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT | PENDING IMPORT |

The invariant forms in column 3 are the **required shape** of the claim for each primitive class,
fixed by [`../RECORD_SCHEMA.md`](../RECORD_SCHEMA.md) section 3.2. They are obligations, not
discharged proofs. Nothing in this column asserts that any rewrite has been shown equivalent.

### 5.1 Primitive-specific edge cases

These are the boundaries the edge-case obligation must cover. They are listed here so the
obligation is concrete before the data arrives, not so that any of them can be reported as passing.

| Primitive class | Required boundaries |
| --- | --- |
| addition, subtraction | zero, `p-1`, operands that straddle the reduction boundary, non-canonical limb states, maximum carry propagation |
| multiplication, squaring | zero, one, `p-1`, operands with maximal limb magnitude, the squaring/multiplication aliasing case |
| reduction | already-reduced input, maximal unreduced input, inputs one below and one above `p` |
| inversion, square root | zero input, one, quadratic non-residues, the branch choice for the root |
| point operations | point at infinity as either operand, `P + P`, `P + (-P)`, the identity, small-order and low-Hamming-weight scalars |
| scalar multiplication | scalar zero, one, `n-1`, `n`, `n+1`, and every table index reachable by the window scheme |

## 6. Promotion

A row is promoted by writing a record file conforming to
[`../RECORD_SCHEMA.md`](../RECORD_SCHEMA.md), placing it in [`records/`](records/), and filling
the front matter from imported artifacts only. Until then `load_records` on this study returns
zero records and every aggregate in [`benchmark_summary.md`](benchmark_summary.md) reports zero.
