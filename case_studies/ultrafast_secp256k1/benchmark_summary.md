# Aggregate Summary and the Statistical Question

> **This document contains no ParseAtlas measurement.** The record corpus is empty. Every
> aggregate below is reported as zero or `PENDING IMPORT`, which is the correct output for the
> current state of evidence, not a formatting placeholder.

---

## 1. Current corpus state

| Quantity | Value |
| --- | --- |
| Records in [`records/`](records/) | 0 |
| Files skipped by `load_records` | `EXAMPLE_TEMPLATE.md` |
| Complete records | 0 |
| Admissible records (equivalence proven, validation passing) | 0 |
| Records with a measured benchmark | 0 |
| Owner-reported claims awaiting import | 2 (see [`README.md`](README.md) section 2) |
| Records needed before any conditional probability may be reported | 20 per transformation label |

Running the engine against this directory today produces: zero records, a withheld rate for every
one of the eleven transformation labels, and `None` with an insufficient-data reason from
`predictor_correlation`. That output is a faithful description of what is known.

## 2. The question the corpus is being built to answer

Once 20-30 records exist, the primary question is:

```text
P(speedup | transformation)
```

For each label in the controlled vocabulary of
[`../RECORD_SCHEMA.md`](../RECORD_SCHEMA.md) section 4: of the records that applied this
transformation and were measured, what fraction produced a real speedup?

The purpose is to turn representation search from a matter of taste into a ranked search order. If
`lazy reduction` yields a measured speedup four times out of five and `sign relocation` one time
out of five, the search should try lazy reduction first. That is a decision procedure, and it is
worth having only if the numbers behind it are real.

| Transformation label | Total records | Measured | Speedups | Regressions | No change | Rate |
| --- | --- | --- | --- | --- | --- | --- |
| limb layout | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| projective scaling | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| sign relocation | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| factorization | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| reassociation | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| reduction placement | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| lazy reduction | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| coordinate systems | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| addition chain | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| common-subexpression reuse | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |
| operation scheduling | 0 | 0 | 0 | 0 | 0 | withheld -- sample below minimum |

This table is regenerated from `transformation_statistics(load_records("records")["records"])`. It
is not maintained by hand.

## 3. Sample-size honesty rule

**Below roughly 20 measured records in a transformation class, no conditional probability may be
reported as anything other than a raw count.**

Stated precisely, and enforced by `transformation_statistics`:

1. While a label has fewer than `MINIMUM_RATE_SAMPLE_SIZE = 20` measured records, `speedup_rate`
   is `None`. The function returns `rate_withheld_reason` naming the actual count and the
   threshold. The constant is a **floor, not a default**: `transformation_statistics` accepts a
   `minimum_sample_size` argument, and a caller may raise it but not lower it. A request below the
   floor is clamped, and the returned structure says so in `requested_minimum_sample_size`,
   `sample_size_floor_applied` and `sample_size_floor_note`, so a rate can never be produced below
   the documented threshold and then quoted as though it had met it. `predictor_correlation`
   clamps to `MINIMUM_CORRELATION_SAMPLE_SIZE` the same way.
2. The raw counts -- total, admissible, rejected, measured, speedups, regressions, no-change --
   are returned **regardless**, so a reader can see exactly what the corpus contains and why the
   rate was withheld. Withholding a rate is not withholding data.
3. Once the threshold is met and a rate is reported, a **95 percent confidence interval is
   required and is returned with it**. The engine computes a Wilson score interval, which does not
   run outside `[0, 1]` at the small samples this project will have for a long time. A rate
   without an interval is not a permitted output of this document.
4. Only **admissible** records count toward the denominator. A record whose equivalence is
   unproven, whose differential test is pending, or whose evidence level is `owner-reported` **or
   still pending** is excluded from every numerator and every denominator, and is counted
   separately as `rejected_records`. A pending evidence level is a benchmark number with unknown
   provenance, which is exactly what this denominator must not contain.
5. Labels are **not mutually exclusive**. A record naming both `reassociation` and
   `common-subexpression reuse` is counted under both, so the per-label totals do not sum to the
   record count. Any narrative built on this table must say so.

Three records showing a speedup is the sentence "three records showed a speedup". It is not
"this transformation works 100 percent of the time", and the engine will not print the second
sentence.

## 4. The stronger hypothesis to test

**Evidence level: hypothesized.** Stated by the project owner, not yet tested against any data.

> Raw operation count may be a **poor** predictor of measured speedup, while dependency depth and
> register pressure predict it better.

If true, this matters more than the per-label rates, because it says the cost model the field
conventionally uses -- count multiplications and squarings -- is measuring the wrong thing when the
question is which *representation* to choose.

### 4.1 Why experiment 0021 makes this the obvious hypothesis

Experiment 0021 measured, over a six-expression corpus and 25 grammars, that:

* the raw operation multiset (`add`, `sub`, `mul`, `div`, node count) is **invariant** across every
  grammar for a fixed token sequence -- each parse consumes exactly the same operator tokens;
* the AST critical-path depth is **not** invariant -- on `a/b + c*d - e/f + g` the same six
  operations (`add` 2, `sub` 1, `mul` 1, `div` 2) arrange into dependency chains of depth 4 to 6,
  and only 4 grammars of 25 reach the minimum depth of 4;
* six is the *operation* count. The same parse has 13 AST nodes, and the node count is a different
  quantity that must not be quoted in its place;
* the conventional control grammar `G0` is not always the minimum-depth choice: it failed to be
  minimal on 3 of the 6 corpus expressions.

Experiment 0021 measured structure only and made no timing claim whatsoever. But the structural
result generates the prediction directly: **the quantity that does not move when representation
changes cannot be the quantity that explains what happens when representation changes.** Operation
count is that quantity. Dependency depth is not.

The Ultrafast setting is not the precedence setting -- the transformations there are real rewrites,
not reparses, and can genuinely change the operation multiset. That is why this is a prediction to
test rather than a conclusion to carry over. It also makes the test sharper: in a setting where
operation count *can* move, does it move in step with the measured speedup, or not?

### 4.2 What would confirm it

`predictor_correlation(records)` computes, over complete and admissible records only, the Pearson
correlation between measured speedup percent and each predictor:

| Predictor | Definition | Correlation | Sample |
| --- | --- | --- | --- |
| `operation_count_delta` | sum of the five signed operation deltas, `candidate - baseline` | PENDING IMPORT | 0 |
| `dependency_depth_delta` | `depth_after - depth_before` | PENDING IMPORT | 0 |

The hypothesis is **supported** if `dependency_depth_delta` correlates substantially more strongly
with measured speedup than `operation_count_delta` does, over a sample large enough to distinguish
them. It is **refuted** if operation count correlates at least as well.

Register pressure is named in the hypothesis and in ROADMAP Phase 13's metric list, but it is
**not yet a schema field**: there is no agreed way to extract a comparable figure across the
rewrites, and adding a field that records cannot fill honestly would be worse than leaving it out.
Adding it is a deliberate schema change, and it requires a stated extraction method first.

### 4.3 Guards against a spurious answer

* `predictor_correlation` returns `correlation: None` plus a stated reason while fewer than
  `MINIMUM_CORRELATION_SAMPLE_SIZE = 10` complete records back a predictor. It never returns a
  number computed from two or three points.
* It returns `None` with a no-variance reason when a predictor is constant across the sample -- for
  example if every record happens to have the same depth delta.
* Correlation is not causation, and the records are not a random sample: they are the rewrites
  someone chose to attempt and chose to report. A positive result is evidence about *this* search
  process, not a law about representation in general. Any published version of this table must
  carry that caveat.
* Both predictors are computed from fields that are `None` while pending, so a pending record
  contributes to neither correlation rather than contributing a zero.

## 5. Promotion of this document

Every `PENDING IMPORT` and every zero above is replaced only by regenerating the tables from the
engine after real records land in [`records/`](records/). None of these tables is hand-edited, and
no figure enters them from prose, from recollection, or from an owner report.
