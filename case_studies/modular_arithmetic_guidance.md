# Modular arithmetic and carry chains: what this project's results say

**Georgian version:** [modular_arithmetic_guidance.ka.md](modular_arithmetic_guidance.ka.md)

**This document is guidance, not a record.** It carries no measurement of any external system and is not admissible as evidence about one. Case-study *records* are governed by [RECORD_SCHEMA.md](RECORD_SCHEMA.md) and have a strict format; this is orientation for work happening elsewhere, written so that whoever picks it up knows which statements are load-bearing and which are not.

**Read the provenance labels.** Everything below is marked as one of three things, and they are not interchangeable:

```text
MEASURED HERE      an experiment in this repository, named, reproducible from a clean clone
PRIOR ART          established published work, stated from knowledge — VERIFY BEFORE CITING
NOT ESTABLISHED    a hypothesis, explicitly not a result
```

---

## 1. The shape of the problem

A `k`-limb addition is a dependency chain of depth `k`: limb `i+1` cannot start until limb `i`'s carry is known. This is not a question of how many operations are performed — the operation count is fixed. It is a question of **critical path**, and it is the reason multi-limb modular arithmetic does not parallelise the way its operation count suggests it should.

*MEASURED HERE.* The distinction between an invariant operation multiset and a variable critical-path depth is [experiment 0021](../experiments/0021_critical_path_cost/REPORT.md). The same computation, written differently, keeps its operation count and changes its depth. That is the axis a carry chain sits on.

---

## 2. What is already known, so that nothing here is rediscovered

*PRIOR ART — every item in this section is established published work, stated from knowledge. Verify each before citing it in a write-up; none of it was measured in this repository.*

- **Unsaturated limbs.** libsecp256k1 represents field elements as 5 limbs of 52 bits inside 64-bit words (and 10 limbs of 26 bits on 32-bit targets) rather than 4 saturated 64-bit limbs. The spare bits absorb carries so that they do not propagate, and reduction is deferred.
- **Redundant number systems / carry-save.** Avizienis. A redundant representation makes addition constant-depth instead of linear in the number of limbs. This is the classical form of the result and it long predates any of this.
- **Lazy or delayed reduction.** Several products are accumulated before a single reduction, amortising the reduction cost and shortening the dependency chain between multiplications.
- **Montgomery versus Barrett reduction.** Two representations of the same modular map, with different cost structure and different preconditions.
- **ADCX / ADOX (x86 BMI2).** Two independent carry flags, allowing two carry chains to advance simultaneously. This is the hardware-level answer to the same problem, and where it is available it is usually the first thing to check.

A result that reproduces any of the above is a *reimplementation*, not a discovery, and should be written up as one.

---

## 3. The structural result this project actually contributes

This is the part that is ours, and it is not obvious.

### 3.1 A redundant representation breaks value equality by construction

A redundant representation exists precisely so that **one field element has many encodings**. That is the whole mechanism: the spare bits let a limb hold a value that has not yet been normalised.

So the obligation

```text
R1(x) == R2(x)
```

is not merely hard to discharge for such a transformation — it is **false**, and it is false on purpose. The correct obligation is the decode relation

```text
decode(R2(x')) = R1(x)
```

*MEASURED HERE.* This is thesis T22 and the Region model of [experiment 0033](../experiments/0033_region_model/REPORT.md), where the search object stops being an expression tree and becomes `(inputs, state, operations, outputs, invariants)`, with the decode relation replacing the equality it gives up.

### 3.2 Therefore a value-equality search engine cannot find these transformations, at any depth

*MEASURED HERE.* Thesis **T20a** established that the co-Z form is unreachable by the vendored `repsearch` rewriter **by construction, at every depth and every beam width** — because its input list is passed through literally, its output key set is frozen, and its equivalence test is raw coordinate value equality in `F_p`.

**A redundant limb representation fails the same three tests, for the same reason.** It changes the encoding of the inputs, it changes what the intermediate state carries, and it deliberately breaks value equality. So:

> A search whose oracle is value equality is blind to carry-chain representation changes in exactly the way it was blind to co-Z. This is not a defect in the search. It is the boundary of its equivalence oracle.

*NOT ESTABLISHED:* that the Region model, once implemented, would in fact find any particular carry-chain transformation. The negative result above is proved; the positive one is not, and must not be stated as though it were.

---

## 4. The frontier this trade sits on

Unsaturated limbs buy shallow carry depth and pay in register pressure: five limbs instead of four is 25% more live values, against a fixed budget of 16 general-purpose registers on x86-64.

*MEASURED HERE, structurally.* This is the depth-versus-memory Pareto frontier. On an eight-term sum, the sequential chain is depth 7 with 2 simultaneously live values; the balanced tree is depth 3 with 4. **Halving the critical path doubles the peak live values.** They are not the same criterion and one cannot be optimised as a proxy for the other. Experiments 0041 and 0044 measure this frontier over a corpus; both were in review when this document was written, so treat the eight-term figure as the manager's hand calculation, which is what it is.

*MEASURED HERE.* Thesis **T31**: reachability outranks cost. Against a hard ceiling — a register budget, a memory limit — cost stops being continuous and becomes a step. A 10% reduction is worth nothing at 5 registers of headroom and decisive at half a register. Rank candidates by **whether they fit first**, and use cost only to break ties among those that do.

*MEASURED HERE.* Thesis **T23**: selection is the hard half, not generation. Two candidates can both be correct and differ substantially in cost in a way that no correctness oracle sees and no per-operation count expresses, because the difference is a per-step overhead amortised across a loop. Experiment 0033 reproduces exactly this: identical single-step cost, loop costs of `n+1` against `2n`. **Price the region, not the formula.**

---

## 5. What to record while working

So that results are admissible without rework, capture per candidate, in the form [RECORD_SCHEMA.md](RECORD_SCHEMA.md) requires:

```text
Primitive:                  as the upstream project names it
Baseline representation:    precise enough to reimplement
Candidate representation:   at the same precision
Before / After:             the actual expression or instruction sequence, never a prose summary

Operation delta:            mul  sqr  add  sub  reduce
Dependency depth:           before <n>  after <n>        <- the carry chain length
Peak live values:           before <n>  after <n>        <- the register pressure

Benchmark:                  baseline <v>  candidate <v>  delta <p>   + which harness
Validation:                 random differential · edge cases · Bitcoin/Core tests
```

Two rules that are not negotiable:

1. **Anything not yet known is written exactly `PENDING IMPORT`.** Never `0`, never an estimate, never a number from anywhere but the primary artifact. The schema is normative and this is enforced by tests.
2. **The invariant is `candidate == baseline` under the declared decode.** In cryptographic code a different result is not an optimisation. If the transformation changes the encoding, the decode map must be written down explicitly and checked, not assumed.

**If depth falls while operation count rises, that is a real point on the frontier and it is worth recording even when the benchmark does not move.** It is evidence about the structure; the benchmark is evidence about one machine.

---

## 6. What this project has not established

Stated plainly so that nothing here is over-read:

- The 25 precedence conventions **do not transfer to this problem.** Field arithmetic is written in C and assembly; the precedence of `+ - * /` in written notation is not the lever there. The Direction B cost numbers in this repository are about **notation**, not about machine code. Do not spend effort mapping the precedence atlas onto limb arithmetic.
- **No measurement in this repository was taken on any external engine.** Nothing here supports a claim about the performance of any implementation.
- Whether any specific carry-chain transformation is profitable on a given target is **not established here** and can only be settled by benchmark with disclosed provenance: which variant pair, which harness, which machine.

The transferable content of this project for this problem is three things and no more: **the decode obligation**, **the proof that a value-equality search cannot cross it**, and **the frontier that says depth, memory and cost are separate criteria that must be ranked against a ceiling rather than blended into one number.**
