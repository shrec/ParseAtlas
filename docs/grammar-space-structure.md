# Structure of the Generation 1 Precedence Space

This document consolidates what is currently known about the structure of the ParseAtlas Generation 1 grammar space, and — equally important — states what each result is actually worth.

Several results in this repository look striking and are not. A literature check placed them precisely: one is a restatement of a classical data structure, one is a textbook construction, one follows from counting, and one is a tautology. They are kept because they are load-bearing for the search program, not because they are discoveries. Each is labelled below.

Evidence labels follow [research-methodology.md](research-methodology.md): **OBSERVED**, **JUSTIFIED**, **HYPOTHESIS**, **RESTATEMENT** (correct, but already known in another form), **TRIVIAL** (follows in one step from definitions or counting), **TAUTOLOGY** (true by construction, carries no information).

---

## The setting

The research object is the pair `(token sequence, grammar)`. Generation 1 fixes:

- four binary operators `+ - * /`;
- left associativity at equal precedence;
- parentheses override precedence;
- precedence is global within one grammar;
- symbolic simplification happens strictly after parsing.

The registry holds `4! = 24` strict total precedence orders `G01..G24`, plus one tied control grammar `G0` in which `*` and `/` share a level above `+` and `-`. `G0` is separate because no strict total order expresses conventional arithmetic.

Throughout, let `w = w[0..k-1]` be the sequence of operator **occurrences** in a token sequence, and let `O(E)` be the **set** of distinct operator types occurring in it.

---

## R1. Operator-support reduction

**Statement.** Parsing depends only on the restriction of the precedence order to `O(E)`. Two strict grammars whose orders restrict to the same relative ordering of `O(E)` produce a **byte-identical** serialized AST. The 24 strict grammars therefore partition into exactly `|O(E)|!` blocks of equal size `24 / |O(E)|!`.

**Justification.** The parser compares binding powers only for operators it actually encounters. An operator absent from the token stream is never a comparison operand, so its position in the order cannot influence the tree.

**Consequence.** Grammar enumeration is redundant by a known factor. For a token sequence over three operator types, 24 parses collapse to 6 distinct ASTs, each produced four times. For a single operator type, all 24 parses are identical.

**What it is worth.** Elementary once stated — any compiler engineer would accept it on sight. Its value here is entirely operational, and it is twofold:

1. It bounds AST diversity: `#distinct ASTs ≤ |O(E)|!`.
2. **It is the null model.** Agreement between two grammars inside one support block is a parsing artifact, not evidence about grammar space. Any claim that two grammars "behave alike" must be measured against this baseline, or it is measuring the parser rather than the mathematics. Experiment 0024 exists largely to enforce this.

*JUSTIFIED — experiment 0019.*

---

## R2. The parse tree is the Cartesian tree of the binding-power sequence

**Statement.** For every registered grammar with binding-power map `p`, the parse tree equals the tree built by this recursion: if the operator range is empty, return the leaf; otherwise take the minimum binding power in the range, split at the **rightmost** occurrence of an operator holding that power, and recurse on both sides. Verified for all 24 strict grammars and for the tied control `G0`, with 130 944 checks and zero disagreements.

**This is a restatement of a classical structure.** It is the **Cartesian tree** (equivalently a treap) of the operator sequence keyed by binding power, written from the parsing side rather than the data-structure side:

- Cartesian tree: *root at the minimum of the sequence, recurse on the subsequences before and after* — Vuillemin, *A unifying look at data structures*, CACM 23(4), 1980.
- Expression tree: *root at the lowest-precedence operator, recurse left and right* — standard textbook material.

The two definitions are the same recursion. Linear-time Cartesian tree construction is the monotone-stack algorithm, which is shunting-yard. The nearest published prior art is LaLonde & des Rivières, *Handling Operator Precedence in Arithmetic Expressions with Tree Transformations*, TOPLAS 3(1), 1981, which converts a precedence-free tree into the precedence-correct one by local rotations with the Church–Rosser property — treap insertion under another name, and 45 years old.

What appears unstated in the literature is only the explicit identity, plus the tie-breaking convention: **rightmost minimum corresponds to left associativity**, whereas the usual Cartesian-tree convention breaks ties the other way. That is a remark, not a result.

**What it is worth.** It is why R3 works: reachability becomes a question about priority assignments, and the decision procedure never needs a parser.

*RESTATEMENT — experiment 0023; prior art Floyd 1963, Vuillemin 1980, LaLonde & des Rivières 1981.*

---

## R3. Reachability is decidable from a constraint graph

**Statement.** Let `T` be a candidate binary tree over the fixed leaf sequence and operator word `w`. Walk `T`; at each internal node splitting the operator range `[lo, hi)` at position `s`, the root operator `w[s]` must satisfy

```text
p(w[s]) <= p(w[t])   for every t in [lo, s)     weak   — equality allowed, the split takes the RIGHTMOST minimum
p(w[s]) <  p(w[t])   for every t in (s, hi)     strict
```

Collect these as edges between operator **types**. Then `T` is reachable by some strict precedence grammar **iff**

1. no strict constraint is a self-loop `p(o) < p(o)`, and
2. the constraint digraph restricted to edges between **distinct** types is acyclic.

Condition (2) is required because a cycle among distinct types forces their binding powers equal, which no strict total order permits.

**Verification.** Checked against exhaustive enumeration — ground truth taken by actually parsing under all 24 strict grammars — over every operator word of length `k = 2..6` over `{+,-,*,/}` and every Catalan parenthesization:

| k | trees | unreachable | unreachable fraction | mismatches |
|---|---|---|---|---|
| 2 | 32 | 4 | 12.500% | 0 |
| 3 | 320 | 124 | 38.750% | 0 |
| 4 | 3 584 | 2 332 | 65.067% | 0 |
| 5 | 43 008 | 35 828 | 83.305% | 0 |
| 6 | 540 672 | 503 252 | 93.079% | 0 |
| **total** | **587 616** | **541 540** | **92.159%** | **0** |

The decision procedure was confirmed non-circular under adversarial isolation: with every parser symbol in its module namespace rebound to a raising stub, it still returned correct verdicts, touching none of them.

**Prior art, and it is substantial.** The "build a constraint digraph, solvable iff acyclic" move is **textbook**. The Dragon Book's precedence-function construction states it directly: *if the constructed graph has a cycle then no precedence functions exist.* The mixed strict/weak refinement is the standard difference-constraint result. Recovering precedence from example trees is an existing line of work — Aasa, TCS 142(1), 1995; Afroozeh et al., SLE 2013; Crespi-Reghizzi, Mandrioli & Martin, 1978.

**What appears unclaimed** is narrow: the **typed-priority** framing — Cartesian trees whose priorities are a function of an element's *type* rather than distinct per position — and a clean iff-theorem at the granularity of "one operator word plus one candidate tree, does a total order on the four types exist", including the strict-self-loop case. No source stating that exact decision problem was found. Given the Dragon Book digraph, it remains a short exercise.

**What it is worth.** This is the project's best novelty candidate, and it is a modest one. Operationally it matters more than that: representation search over precedence space does not require enumerating grammars, and reachability is decidable in polynomial time from the tree alone.

*OBSERVED — experiment 0023.*

---

## R4. Precedence reaches a vanishing fraction of the parenthesization space

**Measured.** Mean coverage of the Catalan tree space, averaged over all `4^k` operator words of length `k`:

| k | mean coverage | full-coverage fraction |
|---|---|---|
| 2 | 0.8750 | 0.7500 |
| 3 | 0.6250 | 0.3750 |
| 4 | 0.3605 | 0.0938 |
| 5 | 0.1735 | 0.0000 |
| 6 | 0.0722 | 0.0000 |

Full coverage becomes impossible from `k = 5` onward; the maximum observed at `k = 5` is 0.4762.

**The headline is trivial.** At most `4! = 24` trees are reachable at any length, while `Catalan(k) ~ 4^k / (k^1.5 √π)`. The fraction vanishes by inspection. This must never be presented as a theorem.

Qualitatively, "precedence cannot express some groupings" is the subject of an existing literature — Souza Amorim, Steindorfer & Visser, *Deep Priority Conflicts in the Wild*, SLE 2017, and *Programming* 2(3), 2018 — and motivates partial-order precedence proposals. The only unclaimed content is the measured average curve, and the metric must be stated explicitly as *mean over operator words of reachable ÷ Catalan*.

**A genuine structural note.** The tied control grammar `G0` reaches trees that **no** strict total order reaches. Ties are an independent grammar dimension, not a notational convenience.

**What it is worth.** It is the quantitative reason the roadmap's parenthesization phase needs a real AST-space engine rather than a wider precedence registry. Widening precedence cannot close a gap this large.

*TRIVIAL, with useful measurements — experiments 0020, 0023.*

---

## R5. Raw operation count is invariant; only dependency structure varies

**Statement.** For a fixed token sequence, the raw multiset of additions, subtractions, multiplications and divisions is identical across all 25 grammars. The AST critical-path depth is not.

**The invariance half is a tautology.** The operator tokens are fixed by construction and every parse consumes each exactly once. Nothing is discovered by observing that they are still there afterwards.

It is kept only as a **discipline rule**, and in that role it is sharp: *a cost model built on operation count alone cannot express any difference that grammar makes, so it cannot be this project's cost model.*

**The depth half is not a performance claim.** Depth is a structural upper bound on parallel evaluation, not a measured latency, and experiment 0021 explicitly disclaims wall-clock results.

**A restriction that must not be skipped.** The classical tree-height-reduction results — Brent, JACM 21(2), 1974; Baer & Bovet, IFIP 1968; Muchnick ch. 12; LLVM's AArch64 MachineCombiner reassociation — assume **exact associativity and commutativity**. Generation 1 has left-associative `-` and `/`, so changing precedence changes the *function*, not the schedule. "Grammar choice is a latency question" is therefore true only inside the equivalence-preserving mode, and false in the semantic-exploration mode where experiments 0001–0026 live.

*TAUTOLOGY plus a structural observation — experiment 0021.*

---

## R6. Semantic equivalence is domain-relative

Equivalence is declared over `(F, D, U)` — function, domain, and undefined set — because canonical text equality alone manufactures false classes. `x/x` simplifies to `1` while remaining undefined at `x = 0`; a canonicalizer that forgets the restriction merges two different objects.

The class structure further depends on the declared **arithmetic domain**. For constant-only token sequences, grammars producing different rational values can produce the same value in `F_p`: collapse was observed at `p = 5, 7, 11` and not at `13, 97`.

This is semantic-variation mode. A modular coincidence between two different rational values is **not** a licence to substitute one representation for another in cryptographic code.

*JUSTIFIED — SPEC.md, experiments 0015, 0022.*

---

## R7. What corpus-scale measurement did and did not find

Over a deterministic corpus of 3 125 controlled expressions across five families:

```text
observed pairwise agreement   0.2593
support-forced (null model)   0.0720
AST-identity                  0.1673
excess over the null model    0.1873
```

**The negative result.** The clustering computed from the excess matrix coincides **exactly** with the support-size-3 blocks. Once the null model is removed, no residual cluster structure remains on this corpus. The hypothesis that grammar space has stable algebraic or statistical cluster structure beyond the parsing artifact is **not supported here**.

This is reported as the headline of that experiment. Promoting the raw observed-matrix clustering instead would have been a presentation of the null model as a discovery — two of its four clusters are verbatim support-forced blocks.

**The positive result that survives.** AST diversity and semantic diversity move independently. Rank correlation between them is 0.7676, and **2 500 of 3 125 expressions (80%)** hold AST diversity fixed while the semantic class count varies. Syntactic parse diversity is therefore not a proxy for mathematical diversity, and neither may stand in for the other.

Also measured: 25 grammar-rigid expressions against 3 100 grammar-sensitive; mean representation sensitivity 0.1537. **Which structural property makes an expression grammar-sensitive remains open**, and is the most substantive unanswered question in the semantic-exploration mode.

*OBSERVED — experiment 0024.*

---

## R8. Independent-implementation cross-validation

ParseAtlas has been checked against a second, fully independent implementation written for an external project: a different parser whose precedence table is a parameter, and a different equivalence oracle — exact multivariate rational functions over `Q` with equality decided by cross-multiplication, using no computer-algebra library, no floating point, and no probabilistic identity test.

On eight expressions the two produced **identical partitions** of the 24 strict grammars — identical membership, not merely equal class counts.

Two implementations sharing no code and using different equivalence oracles is stronger evidence than either alone. It is not proof of correctness of either, and eight expressions is a small corpus.

One asymmetry is worth recording: the rational-function oracle discards removable restrictions, while the `(F, D, U)` key retains them. Where all grammars happen to share one restriction the partitions still agree, but ParseAtlas carries strictly more information.

*OBSERVED — experiment 0025.*

---

## Summary: what the structure is for

The structural results above are not the project's contribution. R2 is a restatement, R4 is trivial, R5 is a tautology, and R3's method is textbook. They are here because together they turn representation search over precedence space from an enumeration problem into a decision problem, and because R1 supplies the null model without which every agreement measurement is meaningless.

The open questions that matter are elsewhere:

- **What makes an expression grammar-sensitive?** (R7, unanswered)
- **Do equivalence-preserving transformation axes generalise beyond field arithmetic?** (experiment 0026)
- **Can a search rediscover, unaided, a representation a human expert already found?** (the roadmap's rediscovery gate — the acceptance test for calling this a search procedure rather than a description of intuition)

A reader citing this repository should read the Working Theses section of [ROADMAP.md](../ROADMAP.md) first. It states, claim by claim, which results are measurements and which are restatements.
