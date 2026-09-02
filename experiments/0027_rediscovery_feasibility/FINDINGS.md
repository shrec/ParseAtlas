# 0027 — Is the T20 rediscovery gate reachable by the search machinery that exists?

**Type:** analysis card. No new module, no new measurement on hardware.
**Target of analysis:** the vendored engine at `case_studies/ultrafast_secp256k1/repsearch_snapshot/`, read only.
**Written in English** because this is an analysis document, not an experiment report.

Every claim below carries one of four labels:

| label | meaning |
|---|---|
| **OBSERVED** | read directly out of the vendored source, or produced by running the vendored source unmodified |
| **GIVEN** | supplied by the card from the source project's own record; not re-derived here |
| **DERIVED** | my own argument or my own computation from OBSERVED and GIVEN material |
| **HYPOTHESIS** | not established; stated as something that would have to be tested |

No figure appears here that is not one of those. Nothing was run on hardware; nothing in the vendored snapshot was modified (all runs used `PYTHONDONTWRITEBYTECODE=1`).

---

## Answer, in one paragraph

**The co-Z form is not reachable from the mixed-addition starting program by any composition of the axes implemented in `repsearch/rewrite.py`, at any depth and any beam width.** The search's reachable set is, by construction, the set of straight-line programs over *the reference's own input list*, producing *the reference's own output key set*, and agreeing with the reference *on raw coordinate values* at every corpus point. `ZADDU` fails all three conditions simultaneously: it has a different input list, a different (larger) output key set, and — decisively — it is a **different function of the same five numbers**, agreeing with `madd_production` only on the measure-zero slice `Z = 1`. The 5894-rewrite run could not have found it, and neither could a run a thousand times larger. T20 as currently written therefore does not measure search quality; it measures whether an axis exists, and that axis does not.

The finding is not purely negative. The distance between the two programs turns out to be **exactly one substitution on the inputs followed by ordinary dead-code elimination**, both of which are within reach — the substitution is the piece that is missing, and section C specifies it precisely.

---

## 0. What was read, and what was run

**OBSERVED.** Files read in full: `README.md`, `PROVENANCE.md`, `repsearch/rewrite.py`, `repsearch/slp.py`, `repsearch/pointforms.py`, `repsearch/tablebuild.py`, `repsearch/equiv.py`, `tools/run_search.py`, plus the head of `repsearch/fieldkernels.py`. Also read: `ROADMAP.md` sections T17–T21, `case_studies/ultrafast_secp256k1/README.md`, `experiments/0026_transformation_axes/REPORT.md`.

Five short scripts were run against the unmodified snapshot to turn readings into observations. Each is reproduced in the appendix so the numbers can be re-obtained.

---

## A. The rewrite axes actually implemented

**OBSERVED.** `repsearch/rewrite.py` carries exactly **four** axis labels, and they are the only values the `Rewrite.kind` field ever takes:

```
['algebraic_rewrite', 'mul_square_trade', 'operation_fusion', 'sign_placement']
```

They are realised by **12 rewrite rules**, all emitted from `single_step_rewrites`. Each rule matches one instruction (occasionally an instruction and its single-use producer) and returns a replacement instruction list. Precisely:

| # | rule name | axis | transformation |
|---|---|---|---|
| 1 | `sqr@` | `mul_square_trade` | `mul(a,a)` -> `sqr(a)` |
| 2 | `unsqr@` | `mul_square_trade` | `sqr(a)` -> `mul(a,a)` |
| 3 | `karatsuba@` | `mul_square_trade` | `2ab = (a+b)^2 - a^2 - b^2`: 1M -> 3S+3A |
| 4 | `dbl2int@` | `operation_fusion` | `add(a,a)` -> `mulint(a,2)` |
| 5 | `int2dbl@` | `operation_fusion` | `mulint(a,2)` -> `add(a,a)` |
| 6 | `intsplit@` | `operation_fusion` | `mulint(a,k)` -> `mulint(a,k-1) + a`, for `k > 2` |
| 7 | `sub2neg@` | `sign_placement` | `a - b` -> `a + (-b)` |
| 8 | `neg2sub@` | `sign_placement` | `a + (-b)` -> `a - b` (single-use producer only) |
| 9 | `pushneg0/1@` | `sign_placement` | `-(a*b)` -> `(-a)*b` or `a*(-b)` |
| 10 | `hoistneg0/1@` | `sign_placement` | `(-a)*b` -> `-(a*b)` |
| 11 | `factor@` | `algebraic_rewrite` | `a*b + a*c` -> `a*(b+c)` |
| 12 | `distribute@` | `algebraic_rewrite` | `a*(b+c)` -> `a*b + a*c` |

Two further transformations exist but are **not** search axes:

**OBSERVED.** `cse` (common-subexpression elimination, commutativity-aware via sorted argument keys) and `dce` (dead-code elimination) are applied as a *canonicalisation pass* — `normalise = dce . cse` — to every candidate. They never branch the search; they only collapse it. So the README's advertised `common_subexpression` axis is present as a normaliser, not as a generator.

**OBSERVED.** The snapshot's own `README.md` advertises twelve axes in prose: `ast_precedence_permutation`, `algebraic_rewrite`, `sign_placement`, `common_subexpression`, `mul_square_trade`, `coordinate_change`, `limb_representation`, `normalization_schedule`, `operation_fusion`, `table_layout`, `algorithm_substitution`, `loop_structure`. Of these, **four are implemented in `rewrite.py`**, one (`common_subexpression`) is a normaliser, `ast_precedence_permutation` is implemented separately in `grammar.py`/`expr.py` for the toy-grammar layer and is not wired into the SLP search, `limb_representation` and `normalization_schedule` are the subject of `fieldkernels.py`/`modarith.py` at the limb layer, and **`coordinate_change`, `table_layout`, `algorithm_substitution` and `loop_structure` have no implementation anywhere in the snapshot.** The prose list is a research programme, not an inventory.

**OBSERVED.** Branching profile of the implemented axes, at depth 1, summed over the 12 formulas that `tools/run_search.py` actually searches:

```
188 one-step rewrites total
  mul_square_trade     103   54.8%
  sign_placement        51   27.1%
  operation_fusion      29   15.4%
  algebraic_rewrite      5    2.7%
```

**DERIVED.** More than half the branching factor is `mul_square_trade`, an axis the snapshot's own measurements already refute on this engine (`S/M = 0.874`, so an M-for-S swap buys 12.6% of one operation out of seven to eleven). The search spends the majority of its budget on the axis with the smallest possible payoff. That is a search-efficiency observation, not a correctness one, and it is independent of everything below.

---

## B. The central question: can the axes reach co-Z?

### B.1 The reachable set, stated precisely

**OBSERVED.** Three lines of `rewrite.py` fix the shape of every candidate the search can ever produce.

Candidate construction, in `search()`:

```python
raw = SLP(reference.name, reference.inputs, rw.instrs, cand.slp.outputs, reference.note)
new = normalise(raw)
```

Output-set gate, in `equivalent()`:

```python
if set(candidate.outputs) != output_names:
    return False
```

Value gate, in `equivalent()` — and its docstring says outright that it is deliberately stronger than projective equivalence:

```python
if want != got:
    return False
```

**DERIVED (reachability theorem).** Let `R` be the reference SLP with ordered input list `I` and output key set `O`. Every candidate `C` the search adds to `found` satisfies all four of:

1. `C.inputs == I` — same names, same order, same arity;
2. `keys(C.outputs) == O`;
3. `C(v) == R(v)` **as raw field values, on every coordinate**, at every corpus point `v` where `R(v)` is defined;
4. `C` passes the FE52 magnitude gate.

*Proof of (1).* The base candidate is `normalise(reference)`, and `cse`/`dce` both reconstruct the SLP with `slp.inputs` unchanged. Every successor is constructed with the literal argument `reference.inputs`. Any rewrite whose instruction list mentions a name that is neither in `I` nor defined earlier is rejected by `SLP._validate`, whose `ValueError` is swallowed by the `except Exception: continue` in the search loop. Rules only ever introduce *fresh SSA temporaries*, via `_fresh`, each of which is immediately defined by an emitted instruction. No rule can introduce a free variable. QED

(2) and (3) are enforced verbatim by `equivalent`; (4) by `magnitude_ok`.

Condition (1) is the important one. **The axes are input-preserving local rewrites of a fixed straight-line program over fixed inputs.** The function signature is not a search variable. It is an argument passed in unchanged at every level.

### B.2 ZADDU fails all three of (1), (2), (3)

**OBSERVED.** Signatures, printed from the snapshot:

```
madd_production  inputs=[X1,Y1,Z1,X2,Y2]  outputs=[X,Y,Z]           8M+3S+7A+3N  w=11.330 depth=5.260 live=8
zaddu            inputs=[X1,Y1,X2,Y2,Z]   outputs=[X,Xp,Y,Yp,Z,Zp]  5M+2S+7A-    w= 7.280 depth=3.230 live=8
zaddu_sum_only   inputs=[X1,Y1,X2,Y2,Z]   outputs=[X,Y,Z]           5M+2S+7A-    w= 7.280 depth=3.230 live=8
```

- **(1) fails.** `Z1` versus `Z` is not a cosmetic rename: the fourth and fifth positions mean different things. In `madd_production`, `(X2, Y2)` are the affine coordinates of `Q` (`Z2 = 1` implicitly). In `zaddu`, `(X2, Y2)` are the coordinates of `Q` *already expressed on the shared `Z`*.
- **(2) fails for `zaddu`.** Six output keys against three. The two extra pairs are the whole point of the formula: `ZADDU` returns `P + Q` **and** `P` re-expressed on the new `Z`. Dropping them (`zaddu_sum_only`) makes the arithmetic pointless — a chain of them then needs a rescale at every step.
- **(3) fails, and this is decisive.**

**OBSERVED.** Constructing `zaddu`'s body under `madd_production`'s input list is refused by the IR itself:

```
SLP refuses: madd_production: m14 uses undefined value 'Z'
```

**OBSERVED.** Even setting the naming aside, the two programs are **different maps on the same five numbers**. Evaluating both on identical tuples, over curve points from the snapshot's own `curve_points` generator, at three Jacobian representatives of `P`:

```
Z = 1                               madd == P+Q: True   zaddu == P+Q: True    raw values equal: True
Z = 915970441258488035130510979...  madd == P+Q: True   zaddu == P+Q: False   raw values equal: False
Z = 883244009719365854108467761...  madd == P+Q: True   zaddu == P+Q: False   raw values equal: False
```

At `Z = 1` they are not merely projectively equal, they are **the same map on raw values**: 132/132 agreement over all admissible ordered pairs from 12 curve points. For `Z != 1` they are not even the same point.

**DERIVED.** `madd_production` and `zaddu_sum_only`, viewed as maps `F_p^5 -> F_p^3`, coincide exactly on the hypersurface `Z = 1` and differ everywhere else. Two maps that are not equal cannot be connected by a chain of transformations each of which preserves the map. Therefore **no composition of the four implemented axes, at any depth and any beam, can transform `madd_production` into `ZADDU`.** The result is independent of `depth`, of `beam`, of `corpus_size`, and of the cost weights. It is a statement about the language, not about the search.

### B.3 Three further, independent barriers

Any one of these alone would suffice; they are listed because a partial relaxation of the design would have to clear all of them.

**OBSERVED (barrier alpha — the co-Z family is not even in the search's formula list).** `tools/run_search.py` builds its target set from `pointforms.DOUBLING`, `pointforms.DOUBLING_Z1` and `pointforms.MIXED_ADD`. `pointforms.CO_Z` — which contains `zaddu` and `zaddu_sum_only` — is **not** included. The 5894-rewrite run never had the co-Z form as a start point, and never as a target.

**OBSERVED (barrier beta — raw-value equality forbids representative change).** `equivalent()` demands exact coordinate values, explicitly rejecting the weaker projective test that `equiv.py` implements for hand-written candidates. `ZADDU` lands on a different projective representative than `madd` in general. Even a hypothetical relaxation to projective equality would not save it — B.2 shows the two disagree *as points* for `Z != 1` — but this barrier means the search cannot reach *any* representative-changing candidate, which is a strictly larger class than co-Z.

**OBSERVED (barrier gamma — the output set is frozen).** One line, `if set(candidate.outputs) != output_names: return False`, forbids a candidate from returning **more** than the reference returns. Section C.4 shows this single line is what blocks the *doubling* half of the co-Z table build, which is otherwise already sitting inside the production formula for free.

### B.4 The positive result: what the distance actually is

Having established that co-Z is unreachable, it is worth measuring *how far away* it is. The answer is the most useful thing in this document.

**OBSERVED / DERIVED.** Take `madd_production` and delete its `Z`-lifting prefix — the four instructions that raise the affine `Q` onto `P`'s `Z`:

```
zz = sqr(Z1)                 (1S)      deleted
u2 = mul(X2, zz)             (1M)      deleted, u2 := X2
s2 = mul(mul(Y2, zz), Z1)    (2M)      deleted, s2 := Y2
```

and rename `Z1 -> Z`. Keep every remaining instruction of `madd_production` byte-for-byte. The result costs **5M+2S** — the count drops from 8M+3S to 5M+2S exactly, because the deleted prefix is exactly 3M+1S.

That program is **raw-value identical to `ZADDU`'s sum output**: 396/396 agreement over 12 curve points x admissible pairs x three shared-`Z` values, with every result equal to `P + Q` under the affine group law.

**OBSERVED / DERIVED.** The same fact stated at specification level, and verified independently:

```
madd_production(X1, Y1, Z, X2*Z^-2, Y2*Z^-3)  ==  zaddu_sum_only(X1, Y1, X2, Y2, Z)
```

exactly, on raw coordinate values, 270/270 cases, with the projective scaling factor `L = 1` uniformly (checked with `equiv.py`'s own `scaling_factor`).

**DERIVED — this is the crux.** `ZADDU` is `madd_production` **precomposed with a substitution on the inputs**. The substitution `sigma: (X2, Y2) -> (X2*Z^-2, Y2*Z^-3)` contains a field inversion and is therefore *not implementable as a program transformation on this engine* — but it never needs to be implemented, because it **cancels symbolically inside the program**: `u2 = (X2*Z^-2)*Z^2 = X2` and `s2 = (Y2*Z^-3)*Z^2*Z = Y2`. Once the cancellation is performed, the three multiplies and one squaring that computed the lifting become dead, and ordinary DCE — which the engine already has — removes them.

So the entire 34.7% is: **one change of variables on the inputs, one symbolic cancellation, and the dead-code eliminator the engine already runs on every candidate.**

The rewriter is operating exactly one level too low. It rewrites *programs*; this transformation happens at the level of the *input encoding*. Nothing about depth, beam, corpus size or cost weighting could ever bridge one level of abstraction.

---

## C. Specification for the missing coordinate-change axis

This is the specification for the piece that does not exist. It is written to be implementable, and written so that the acceptance test cannot be passed by an engine that was told the answer.

### C.1 What it takes as input

A **regrading** `sigma`, consisting of:

1. **A partition of the reference's inputs into typed objects.** For point formulas: `madd_production`'s five inputs are two objects, `P = (X1, Y1, Z1)` (Jacobian) and `Q = (X2, Y2)` (affine, i.e. Jacobian with `Z2 = 1` elided). This typing must be declared alongside the formula; it is not recoverable from the instruction list. *This is new metadata that `pointforms.py` does not currently carry.*
2. **A target encoding for each object**, drawn from the curve's own projective grading `(X : Y : Z) ~ (L^2 X : L^3 Y : L Z)`. The admissible moves are: leave an object as it is; place it on a scale shared with another object; place it on a fresh shared scale.
3. **The induced symbolic substitution** on the input tuple. For "place `Q` on `P`'s scale": `(X2, Y2) -> (X2*Z^-2, Y2*Z^-3)`, `Z1 -> Z`. Written symbolically, over the rational-function field — *inversions are permitted here because this expression is never compiled.*

### C.2 The invariant that must be preserved

Not the raw coordinate values, and not even the projective class of the output for a fixed input tuple — those are the wrong invariants once the inputs no longer mean the same thing. The invariant is:

> **The candidate computes the same abstract object — the same curve point — from inputs that denote the same abstract objects.**

Formally: for all `v'` in the new representation's admissible domain, `decode(C(v'))` is projectively equal to `decode(R(sigma(v')))`, where `decode` maps a coordinate triple to the curve point it denotes.

Note that if `sigma` is a bijection on the admissible domain, **this holds by construction** and does not need to be re-proved by sampling. That is a significant simplification: the axis does not require a new equivalence oracle for the transformation itself. It requires an oracle for the *normalisation* that follows.

### C.3 How equivalence is checked when the representations differ

Three obligations, in increasing order of difficulty:

1. **The cancellation must be verified, not assumed.** After substituting `sigma`, the program's values are rational functions in the new inputs. The claim `(X2*Z^-2)*Z^2 = X2` is a rational-function identity and must be decided exactly. **OBSERVED: the snapshot already contains the right tool and does not use it.** `repsearch/poly.py` implements exact multivariate rational functions over Q with equality by cross-multiplication; `rewrite.py` imports only `field` and `slp` and never touches it. Wiring `poly.py` into the composed-program normaliser is the concrete first implementation step.
2. **The candidate must then be re-verified as a program**, by the existing machinery, against a corpus drawn from the **new** admissible domain — i.e. sampling only tuples that satisfy the shared-`Z` precondition. The existing `make_corpus` samples inputs independently and would generate mostly inadmissible points; it needs a domain argument.
3. **Representative drift must be tracked, not merely tolerated.** Projective equality permits the output `Z` to differ by a factor `L`. For a single call that is harmless. For a *chain*, `L` propagates, and the caller depends on it. **OBSERVED:** `tablebuild.py` is entirely about this — its `_zaddu` returns the z-ratio `dx` explicitly, and `rescale_to_common_z` consumes it. The axis must emit the `L`-relation as part of the candidate, not discard it.

### C.4 The other half of the move: output extension

**OBSERVED / DERIVED.** The doubling half of the co-Z table build (`DBLU`: double `P` *and* return `P` re-expressed on the new `Z`) requires a different and much smaller move — **enlarging the output set with values the program already computes**.

Concretely, in `dbl_z1_production` (the in-tree `Z = 1` doubling, 2M+4S, `Z3 = Y`), the co-Z copy of `P` is already sitting in two temporaries:

```
t  = mul(neg(Y^2), X) = -X*Y^2   ->   X*Z3^2 = -t
s2 = sqr(Y^2)         =  Y^4     ->   Y*Z3^3 =  s2
```

verified 12/12 over `curve_points(12, seed=0x1234)`: `(-t, s2, Y)` is exactly `P` on the new `Z`. **The co-Z doubling costs the production formula nothing at all** — it is two extra output bindings to existing temporaries, with zero additional operations. (The snapshot's own literature `DBLU` in `tablebuild.py` is a different formula at 1M+5S with `Z = 2Y`; the production-derived version is 2M+4S with `Z = Y`. Both hand back `P` for free.)

**DERIVED.** The single line `if set(candidate.outputs) != output_names: return False` is the entire reason the search cannot find this. Relaxing it to a superset test — allow extra outputs, require the original keys to still match exactly — is a **one-line change** that opens the output-extension move, with a straightforward cost consequence (extra outputs raise `max_live` and may extend the live range of a temporary, so `_max_live` already prices it). This is by far the cheapest real extension available.

### C.5 The acceptance test

**The unit of measurement must be the enclosing loop, not the primitive.** This is not a preference; it is forced by three facts already in the record:

- **GIVEN (ROADMAP T21.1).** The first co-Z chain was *correct* and delivered 10-18% instead of 34.7%, because the operand order was wrong: `ZADDU` returns the sum with its **first** operand on the new `Z`, so passing `(acc, d)` strands the constant on the old `Z` and forces a 3M+1S rescale every step. **No correctness test can find this.** A per-formula cost model cannot see it either, because the formula is identical in both cases — only the call site differs.
- **OBSERVED.** `tablebuild.py`'s `heavy_op_counts` prices exactly this, and marks `coz_extra_rescale: 0` as *contingent on the operand order*. Its accounting for a table of `T` entries: current `11 + 11(T-1)`, co-Z `6 + 7(T-1)`. **DERIVED:** at `T = 16` that is 176 against 111, `-36.93%`; at `T = 8`, 88 against 55, `-37.50%`.
- **GIVEN (ROADMAP T21.2).** A windowed table is wrong in every entry by the same factor when the chain drifts, so spot-checking one entry proves nothing. The correctness gate is `verify_table`-grade: walk **all** entries against an independent construction. The snapshot implements exactly that.

Therefore the acceptance test is:

> A candidate produced by the coordinate-change axis is **accepted** when (i) the enclosing loop's output is verified entry-by-entry against an independent construction; (ii) the loop's total modelled heavy-operation cost, **including setup and including every rescale the precondition forces**, is lower than the baseline loop's; and (iii) the precondition is discharged at every call site by construction rather than by assumption.

Condition (iii) is what makes `coordinate_change` genuinely harder than the four implemented axes: `ZADDU`'s precondition ("both operands already share a `Z`") is not a property of the formula at all. It is a property of the loop. A formula-level search cannot even state it.

### C.6 Why the axis was rankable last, and why that ranking was still wrong

**DERIVED.** The honest reason `coordinate_change` was deprioritised is that it has no obvious finite generator set. The four implemented axes are *local*: each matches a pattern at one instruction, so the branching factor is bounded by the program length (OBSERVED: 16 for `madd_production`, 188 across all twelve formulas at depth 1). A substitution `sigma` ranges over an unbounded space of symbolic changes of variable, with no natural enumeration.

**DERIVED.** But the curve's own grading supplies the bound for free. Restrict `sigma` to regradings induced by `(X : Y : Z) ~ (L^2 X : L^3 Y : L Z)`, applied to the declared point-valued arguments. For a two-argument formula the family is essentially four elements: `Q` affine (the baseline), `Q` on `P`'s scale (**this is co-Z**), `P` on `Q`'s scale, both on a fresh scale. For a one-argument formula the family degenerates to the output-extension move of C.4, which generates `DBLU`.

**DERIVED.** So the axis is enumerable after all, at roughly *four* candidates per formula against the 188 the current axes generate at depth 1 — and one of those four is the transformation worth 34.7%. The ranking was not merely wrong about the yield; it was wrong about the cost of looking.

---

## D. T20, reformulated

### D.1 Why T20 as written is not a well-posed test

**DERIVED.** Three distinct defects, and they do not all point the same way.

**Unfair to the search.** T20 asks a straight-line-program rewriter to produce a change of input representation. Section B proves that is outside its language. A gate an engine fails with probability 1 at every parameter setting measures nothing about the engine. Reporting "the search failed T20" would be reporting a category error as a result.

**Too easy in the other direction.** If a `coordinate_change` axis is implemented with the co-Z relation written into it — and note that `tablebuild.py` already contains `ZADDU` and `DBLU` by name and by formula — then "the search finds co-Z" is a tautology. The engine would be finding the thing it was told. The gate must therefore constrain how the axis may be *defined*, not only what the search *returns*.

**Not settleable in this repository as phrased.** T20 is stated against "the 34 percent". That is a loop-level, machine-specific measurement (i5-14400F, GCC 14.2.0, P-core pinned, 11 passes). **OBSERVED:** `case_studies/ultrafast_secp256k1/README.md` states in its own words that ParseAtlas has verified nothing from that project and has run nothing against it. A gate whose pass condition is a percentage ParseAtlas cannot reproduce cannot be closed here at all. The gate must be restated against something ParseAtlas can compute — the modelled heavy-operation cost of the enclosing loop, which `tablebuild.py` already provides.

### D.2 The staged reformulation

| stage | claim | attemptable now? |
|---|---|---|
| **T20.0 Golden case** | The baseline and candidate forms, *and the enclosing loop for both*, and the acceptance metric, are preserved verbatim and pinned by a test. | **Yes — essentially already satisfied.** `pointforms.py` holds `madd_production` and `zaddu`; `tablebuild.py` holds both loops and `verify_table`. Needs only to be pinned as a ParseAtlas golden case. |
| **T20.1 Reachability (negative control)** | Co-Z is *not* in the input-preserving rewrite closure of `madd_production`, at any depth and beam — a proof, not a search. | **Yes. This document does it** (section B). Should be pinned as a regression test, so that a future axis addition is visibly what changes the answer. |
| **T20.2 Axis existence** | A `coordinate_change` axis exists, built to section C, whose substitution family is generated by the curve's projective grading and whose definition **does not mention Meloni, ZADDU, co-Z, or any specific formula**. | **No — needs new machinery.** Requires: input typing metadata on formulas; `poly.py` wired into a composed-program normaliser; domain-aware corpus generation; loop-level cost accounting. |
| **T20.3 Rediscovery (the real gate)** | With T20.2's axis present and **no hint**, the search returns the co-Z program for the table-build objective. Two conditions, which fail for different reasons: **(a) generation** — the program is produced at all; **(b) selection** — it is ranked top-k by a cost model that charges setup and rescale, so the wrong operand order is *priced* below the right one. | **No — requires T20.2.** (b) is the harder half: **GIVEN**, the wrong operand order yields a fully correct table at 10-18% instead of 34.7%, a difference no correctness oracle can see and no per-formula cost model can express. |
| **T20.4 Transfer** | The same axis, unchanged, finds a representation change on a target it was not designed for. | **No — requires a second case study.** Without it, T20.3 remains passable by an axis engineered backwards from the known answer. |

**DERIVED.** The project can attempt **T20.0 and T20.1 today**, and both are cheap. T20.1 in particular converts an open gate into a settled negative with a proof — a better outcome than leaving it open, because it names the missing machinery instead of leaving the failure ambiguous.

**DERIVED.** There is also a cheap partial win available before T20.2: the **one-line superset relaxation of the output-set gate** (section C.4). That alone lets the existing search reach the co-Z *doubling* — which, in the production `Z = 1` formula, is free. That would be a genuine, unhinted rediscovery of one of the two halves of the co-Z table build, by the existing machinery, at the cost of one line plus a cost-model check. **HYPOTHESIS:** it would be found, since the two required temporaries already exist and DCE would keep them once they are outputs; this has not been run and should be.

---

## E. What this means for the ParseAtlas thesis

The founding principle is: *do not optimize the current representation before asking whether a different representation makes the problem disappear.* The card asks whether the numbers support reading this case as a quantified instance of it. **They do, with one caveat that must be stated rather than buried.**

### E.1 What the numbers say

| quantity | value | label |
|---|---|---|
| best result of the in-representation search (5894 rewrites, 1494 kept, 0 unsound, 48 magnitude-rejected) | **-0.34%** (123.37 -> 122.95 ns), described by the source as inside noise | GIVEN |
| the representation change | **-34.9%** (139.05 -> 90.50 ns); the source reports the range as -34.91 / -34.68 / -34.54% | GIVEN |
| ratio of the two percentages | approximately **102x** | DERIVED |
| ratio of the two *absolute* savings | 48.55 ns against 0.42 ns = **115.6x** | DERIVED |

### E.2 Three independent corroborations that the ~35% is structural, not a machine artefact

**DERIVED**, all computed here from the snapshot's own material:

- **Weighted cost model.** `madd_production` `w = 11.330`; the prefix-erased 5M+2S program `w = 7.400`; `zaddu` `w = 7.280`. That is **-34.69%** and **-35.75%** respectively. (The snapshot warns that these weights are ranking placeholders and must never be quoted as measurements; the agreement with the measured -34.9% is close enough to be coincidental, and I flag it as such rather than as a validated predictor.)
- **Measured per-operation throughput.** Using the snapshot's own measured ILP table (`mul` 12.43 ns, `sqr` 10.11 ns at two or more independent chains): 8M+3S = 129.77 ns, 5M+2S = **82.37 ns**, **-36.53%**. The latency bound (one chain: `mul` 21.62, `sqr` 19.10) gives 230.26 -> 146.30 ns, **-36.46%** — the two bounds agree to within 0.1 percentage points, so the prediction is insensitive to where the formula sits between them. *The 82.37 ns figure independently reproduces the "cost model predicted 82.4 ns" recorded in ROADMAP T17.*
- **Loop-level heavy-operation count.** `tablebuild.heavy_op_counts` at `T = 16`: 176 -> 111 heavy operations, **-36.93%**.

Three unrelated models — a placeholder weighting, a measured-throughput model, and a raw heavy-operation count — all land between -34.7% and -36.9%. The effect is structural: **four fewer heavy operations out of eleven.** It is not an M-for-S trade and it is not a scheduling accident.

### E.3 The reading is supported, with a stated caveat

**DERIVED.** The two percentages are **not measured on the same baseline in the same harness.** The -0.34% baseline is `madd_production_generated` at **123.37 ns** (x86-64, GCC 14.2.0, *shared and loaded* machine, best-of-5). The -34.9% baseline is `madd` at **139.05 ns** (i5-14400F, P-core pinned, 11 passes). Those are different machines and different conditions, and the same nominal formula differs by 12.7% between them. A strict reading forbids dividing one percentage by the other.

**DERIVED.** The qualitative conclusion survives that objection comfortably, for three reasons: the gap (~100x) is an order of magnitude larger than the 12.7% baseline discrepancy; the ~35% is independently reproduced by three models computed from the snapshot itself (E.2), none of which depends on either machine; and the -0.34% is described by its own author as inside noise, meaning the true in-representation optimum may be **0%**, in which case the ratio is not 100x but unbounded.

**DERIVED — conclusion.** The reading is supported. The precise defensible statement is:

> On this primitive, a search over four local rewrite axes — complete enough within its own space to be trusted — found **no improvement distinguishable from zero**, while a single change to the input representation delivered **approximately 35%**, confirmed by three independent cost models. The gap is roughly two orders of magnitude, and it is a lower bound rather than a point estimate.

That is the founding principle instantiated on production code, and it is the strongest empirical support the thesis currently has.

### E.4 Two qualifications that keep the claim honest

**OBSERVED.** "Local optimum" is a *beam-truncated* result. `search()` bounds breadth by `beam` and depth by `depth`, and its own docstring says the bounds are reported "so a truncated search is never mistaken for an exhaustive one." At depth 3, beam 40 the run explored 5894 rewrites out of a space whose depth-1 branching alone is 188. So "local optimum in that rewrite space" is a well-supported empirical claim, not a proof of exhaustion.

**DERIVED.** This cuts in only one direction, and it matters. It slightly weakens the *local optimum* claim — a deeper search might find another few tenths of a percent. It does **not** weaken the unreachability result at all, because unreachability is established by construction (section B.1) and is independent of `depth` and `beam` entirely. The two halves of section E rest on evidence of different strength, and only the weaker half is truncation-sensitive.

**DERIVED — the sharper form of the thesis.** The founding principle is usually stated as advice about where to look. This case supports a stronger and more useful version: the two searches were not competing on the same ground. The in-representation search found nothing precisely *because* its space was closed under an invariant — fixed inputs, fixed outputs, fixed values — that the winning transformation violates. **The completeness of a representation search and its blindness to representation change are the same property.** A search that could reach co-Z would necessarily be one whose candidates are not guaranteed to be drop-in replacements, which is exactly why the extra obligations of section C.5 (precondition discharge, loop-level accounting, chain-wide verification) are not optional extras but the price of the yield.

---

## F. What I could not determine

Stated explicitly, with what would settle each.

1. **Whether the -0.34% run would still find nothing at greater depth or beam.** The snapshot has no recorded sweep over `depth`/`beam`. *Settled by:* re-running `tools/run_search.py` at several settings and reporting whether the best result moves — cheap, pure Python, no hardware claim needed.
2. **Whether the one-line output-set relaxation (C.4) actually causes the search to surface the free co-Z doubling.** The temporaries exist (OBSERVED, 12/12); whether the search *ranks* the extended-output program well is a cost-model question I did not test. *Settled by:* the experiment described at the end of D.2.
3. **Whether the regrading family of C.6 is really four elements for a two-point-argument formula.** I argued it from the grading, not from an implementation. *Settled by:* implementing the enumeration and counting what it generates.
4. **The measured cost of the extra outputs.** Extra outputs extend live ranges; `_max_live` prices that structurally, but the snapshot's own measurements show the model can be answering the wrong question for a kernel that is not instruction-bound (ROADMAP T19a). *Settled by:* a benchmark, which ParseAtlas cannot currently run against that engine.
5. **Whether any of this transfers off elliptic curves.** The regrading family of C.6 exists because the curve supplies a grading. Whether an analogous finite family exists for a general expression domain is open. **HYPOTHESIS:** it does wherever the domain has a scaling symmetry, and does not otherwise — which would make `coordinate_change` a *domain-specific* axis, unlike the four implemented ones. Experiment 0026's negative-transfer result on symbolic corpora is weak evidence in the same direction.

---

## Appendix: reproducing the observations

All commands run from `case_studies/ultrafast_secp256k1/repsearch_snapshot/` with `PYTHONDONTWRITEBYTECODE=1`, against the unmodified snapshot. Nothing in the snapshot was written to.

| observation | how |
|---|---|
| four axis labels, twelve rules | scan `repsearch/rewrite.py` for the `emit(name, kind, ...)` call sites |
| 188 depth-1 rewrites, 54.8% `mul_square_trade` | `single_step_rewrites(f())` for each `f` in `DOUBLING` + `DOUBLING_Z1` + `MIXED_ADD` |
| signatures and costs of the three formulas | `SLP.inputs`, `SLP.outputs`, `SLP.cost().summary()` |
| `SLP` refuses `zaddu`'s body under `madd`'s inputs | `SLP(m.name, m.inputs, z.instrs, z.outputs, "")` raises `ValueError: m14 uses undefined value 'Z'` |
| the two maps differ for `Z != 1`, agree 132/132 at `Z = 1` | evaluate both on identical tuples from `curve_points`, compare raw dicts and `Jacobian.to_affine()` |
| prefix-erased `madd` equals `ZADDU`, 396/396 | rebuild `madd_production` with `u2 := X2`, `s2 := Y2`, `Z1 -> Z`; compare against `zaddu_sum_only` |
| the specification-level substitution, 270/270, `L = 1` | evaluate `madd` at `(X1, Y1, Z, X2*inv(Z^2), Y2*inv(Z^3))` using `field.inv`; compare raw values and `Jacobian.scaling_factor` |
| `P` on the new `Z` already inside `dbl_z1_production`, 12/12 | bind extra outputs `T` (first `mul`) and `S2` (last `sqr`); check `-T == X*Z3^2` and `S2 == Y*Z3^3` with `Z3 = Y` |
| loop-level counts | `tablebuild.heavy_op_counts(8)` and `heavy_op_counts(16)` |
| throughput and latency bounds | the snapshot `README.md` ILP table multiplied by the operation counts |
