# ParseAtlas Research Roadmap

This roadmap defines the staged research program for ParseAtlas. Each phase produces executable artifacts, tests, and a report before the next phase expands the search space.

---

## The founding question

Everything in this repository exists to answer one question, and it should be read first:

> **What mathematics would we have today if humans had agreed on different operator precedence?**

Today `*` and `/` bind tighter than `+` and `-`. That is a *convention*, adopted historically, not a theorem. It decides which expressions can be written without parentheses — and therefore which expressions are cheap to write, cheap to read, cheap to teach, and cheap to build on. Notation that is expensive to write tends not to get used, named, or generalised.

So the question is not abstract. It asks: **under a different convention, which mathematics would have been the natural, parenthesis-free mathematics?**

### The research object, stated correctly

There are two directions, and only the second answers the founding question.

```text
direction A   fixed token string  ->  what does it MEAN under each grammar?
direction B   fixed mathematical object  ->  what does it COST to WRITE under each grammar?
```

Experiments 0001 through 0033 run direction A. That work built the instruments — the grammar registry, the parser, domain-aware equivalence, the null model, reachability — and it established the structure of the Generation 1 space. But direction A asks what a *string* becomes, and the founding question asks what *mathematics* costs.

**Direction B is the primary programme from here.** Take a mathematical object as its intended tree, and measure, per grammar, the minimum parentheses needed to write it unambiguously.

### Why this is answerable, and a first indication that it is interesting

Minimal parenthesisation is exactly computable: given the intended tree and a grammar, a child needs brackets only where that grammar would otherwise reparse it. A manager probe over ten ordinary formulas — the distributive law both ways, the binomial square, a mean, a slope, a difference of squares — gives:

```text
conventional G0  ( * / + - )    7 parentheses
best observed    G10 ( - * / + ) 4 parentheses
worst observed   G06 ( + / * - ) 15 parentheses
```

Ten hand-picked formulas are a probe and not a result. But the conventional grammar was not the cheapest even here, and that is enough to make the question worth measuring properly.

### What direction B can actually decide

- **Is the convention we inherited any good?** Rank all 25 grammars by the notational cost of real mathematics. If `G0` is optimal, that is a real finding about a historical accident. If it is not, the gap is the price of the convention.
- **What becomes free under another rule?** Under `+` binding tighter than `*`, the string `a + b * c + d` denotes `(a+b)*(c+d)`: **factored form becomes the parenthesis-free default and expanded form becomes the expensive one.** The distributive law's natural direction reverses.
- **Which mathematics is convention-sensitive?** Some identities cost the same under every grammar; others swing wildly. The swing is a property of the mathematics, not of the notation.
- **Would a different convention have favoured a different mathematics?** If factoring were cheap to write and expansion expensive, which results would have been reached first, and which would have looked "obvious"?

### The main line: the domain-worlds series

Direction B proceeds field by field, and in each field the corpus is **fundamental identities, canonical objects and laws** — not random or generated formulas. What a convention does to `(a+b)(c+d) = ac+ad+bc+bd` is a historical question; what it does to a sampled template is not.

```text
algebra worlds       distributive law both ways, (a+b)^2, a^2-b^2, factored vs expanded
geometry worlds      line, circle, conics, distance, slope, area laws
trigonometry worlds  DONE - 0036: the Pythagorean identity survives in 13 of 25
calculus worlds      difference quotient, product and chain rule forms, Taylor terms
linear algebra       dot product, determinant, linear combination, norm
```

For each field and each world: which side of a law is parenthesis-free, which factorisation is visually obvious, which expansion becomes expensive, which identity stays true in the same textual form.

**The question the series is built to answer.** Two measurements already point the same way and neither was designed to. Experiment 0034 puts `G0` **11th of 25** on notational cost, 45.3 percent dearer than the cheapest. Experiment 0036 puts `G0` in the **top three of 25** at preserving trigonometric identities, holding all eight. So:

> Is there a grammar that beats `G0` across the **whole** mathematical workload — or did the conventional convention survive because it is a **good compromise across many fields** rather than an optimum in any one?

That is a historically meaningful question with a measurable answer, and it is the natural headline of the series. A convention that is mediocre everywhere and excellent at nothing would look exactly like `G0` does so far.

### How the existing work serves it

Nothing built so far is discarded; it is repointed.

| built | serves direction B as |
|---|---|
| grammar registry, parser | the 25 conventions being compared |
| domain-aware equivalence `(F, D, U)` | the guarantee that two writings denote the same object |
| operator-support reduction (T6) | the null model: cost differences a convention forces, not chooses |
| reachability control (0028) | which intended trees a convention can express at all |
| associativity space (0030) | the convention axis widened beyond precedence |
| the Region model (Phase 14) | representation change once notation alone is exhausted |

The equivalence-preserving search of Group F remains the long-range programme. The founding question above is the near-range one, and it comes first.

---

## Current implementation status

The first executable vertical slice is now available under `src/parseatlas/`. It implements the Generation 1 grammar registry, custom binary-expression parser, SymPy-backed canonical analysis, domain-aware undefined metadata, JSON/Markdown CLI output, and tests for the initial `24 -> 8` finding. The generated result is recorded in [experiments/0001_affine_functions/REPORT.md](experiments/0001_affine_functions/REPORT.md).

Completed: formal specification, `G0` control grammar, `G01..G24` strict registry, baseline parser, golden reproduction, and first experiment report.

Completed next: outer-function analysis for trigonometric, exponential, logarithmic, root, absolute-value, inverse-trigonometric, reciprocal, square, and cube families. Results are recorded in [experiments/0002_outer_function_atlas/REPORT.md](experiments/0002_outer_function_atlas/REPORT.md).

Completed next: quadratic property extraction and the degree-collapse experiment. Results are recorded in [experiments/0003_quadratic_properties/REPORT.md](experiments/0003_quadratic_properties/REPORT.md).

Completed next: controlled corpus generation and initial rational-function pole/removable-restriction analysis. Results are recorded in [experiments/0004_controlled_corpus/REPORT.md](experiments/0004_controlled_corpus/REPORT.md).

Completed next: deterministic coefficient sweep for a controlled linear template. Results are recorded in [experiments/0005_coefficient_sweep/REPORT.md](experiments/0005_coefficient_sweep/REPORT.md).

Next: expand coefficient families, add zero/rational coefficients, and benchmark raw parsing versus symbolic processing versus canonical evaluation cost.

### 5C. Large function and domain catalogs

- Maintain the exact 10,000-function parameterized catalog.
- Maintain a balanced cross-domain formula catalog.
- Use structural mode for exhaustive enumeration and symbolic mode for samples and exceptions.
- Never represent catalog size as proof coverage; report theorem coverage separately.

Completed extension: an initial 1,000-formula catalog across eight mathematical domains is recorded in [experiments/0006_mathematical_domains/REPORT.md](experiments/0006_mathematical_domains/REPORT.md).

Completed extension: first specialized analyzers for quadratic equations, geometry, algebra, calculus, trigonometry, and number theory are recorded in [experiments/0007_specialized_domain_analyzers/REPORT.md](experiments/0007_specialized_domain_analyzers/REPORT.md).

Completed extension: exponential differential-equation residual checks and Binomial PMF/moment analysis are recorded in [experiments/0008_ode_probability/REPORT.md](experiments/0008_ode_probability/REPORT.md).

Completed extension: Normal and Exponential distributions plus extended calculus properties are recorded in [experiments/0009_continuous_probability_calculus/REPORT.md](experiments/0009_continuous_probability_calculus/REPORT.md).

Completed extension: circle metrics, planar rotations, vector angles, and algebraic identity residual checks are recorded in [experiments/0010_geometry_algebra/REPORT.md](experiments/0010_geometry_algebra/REPORT.md).

Completed extension: logistic and harmonic ODE residuals, Normal CDF, z-confidence intervals, and sample statistics are recorded in [experiments/0011_advanced_ode_statistics/REPORT.md](experiments/0011_advanced_ode_statistics/REPORT.md).

Completed extension: safe-point numerical validation of raw versus canonical expressions is recorded in [experiments/0012_numerical_validation/REPORT.md](experiments/0012_numerical_validation/REPORT.md).

Completed extension: separate raw parsing and symbolic canonicalization benchmark measurements are recorded in [experiments/0013_cost_benchmark/REPORT.md](experiments/0013_cost_benchmark/REPORT.md).

Completed extension: cross-family cost comparison and calibration identity residual mining are recorded in [experiments/0014_cross_family_invariants/REPORT.md](experiments/0014_cross_family_invariants/REPORT.md).

Completed extension: domain-aware identity validation, original restriction preservation, and sampled counterexamples are recorded in [experiments/0015_domain_aware_invariant_mining/REPORT.md](experiments/0015_domain_aware_invariant_mining/REPORT.md).

Completed extension: multivariable gradient/Hessian analysis, complex branch metadata, and symbolic conjecture ranking are recorded in [experiments/0016_multivariable_complex_conjectures/REPORT.md](experiments/0016_multivariable_complex_conjectures/REPORT.md).

Completed extension: pairwise grammar agreement matrix and representation sensitivity metrics are recorded in [experiments/0017_grammar_equivalence_matrix/REPORT.md](experiments/0017_grammar_equivalence_matrix/REPORT.md).

Completed extension: strict precedence permutation graph and adjacent-swap semantic transitions are recorded in [experiments/0018_precedence_graph/REPORT.md](experiments/0018_precedence_graph/REPORT.md).

## Working Theses

These are the load-bearing claims the project currently stands on. Each is written to be falsifiable, carries an evidence level from the methodology document, and names the experiment that tests it. A thesis is promoted only by measurement, and is demoted or deleted the moment a controlled run contradicts it.

Evidence levels: **OBSERVED** (produced by a recorded execution), **JUSTIFIED** (observed plus an explicit symbolic argument), **HYPOTHESIS** (a pattern awaiting a controlled test), **OPEN** (a question with no result yet).

### Group A — Representation space has structure

**T1. The grammar space collapses into semantic equivalence classes.** For a fixed token sequence the 25 registered grammars do not produce 25 distinct mathematical objects; they partition into far fewer classes. *OBSERVED — 0001, 0017.*

**T2. The class count is not a universal constant.** `C(E)`, the number of semantic equivalence classes of `E`, depends on coefficient values and not only on the syntactic template. The same template `a*x + b - c*x/2` produced 6 classes for some coefficient triples and 8 for others. *OBSERVED — 0005.*

**T3. AST diversity and semantic diversity move independently.** A corpus slice can hold AST diversity fixed while `C(E)` varies. Syntactic parse diversity is therefore not a proxy for mathematical diversity, and neither quantity may be reported as a stand-in for the other. *OBSERVED — 0005; retested at corpus scale in 0024.*

**T4. Expressions separate into grammar-rigid and grammar-sensitive.** Some token sequences keep all 24 strict grammars in one semantic class; others fragment. *OBSERVED — 0017.* **The question of which structural property decides this is the central open question of the project.** *OPEN — 0024.*

**T5. Precedence acts through the algebraic core, not on the outer function.** The causal chain is `grammar -> canonical algebra -> domain-specific behavior`. Changing precedence does not act on `sin` or `log` directly; it changes the algebraic argument, and the outer domain then translates that change into frequency, phase, poles, growth rate, or a domain boundary. *OBSERVED — 0002.*

### Group B — Exact structure of the Generation 1 precedence space

**T6. Operator-support reduction.** Let `O(E)` be the set of operators actually occurring in `E`. Parsing depends only on the precedence order restricted to `O(E)`, so the 24 strict grammars partition into `|O(E)|!` blocks of size `24/|O(E)|!` that produce byte-identical ASTs. Grammar enumeration is therefore provably redundant by a known factor, and agreement inside a block is a parsing artifact rather than a finding. *JUSTIFIED — 0019.*

**T7. Rightmost-minimum characterization — this is the Cartesian tree, and it is not new.** For every registered grammar, the parse tree equals the tree built by recursively splitting at the rightmost occurrence of the minimum-binding-power operator in each range. This holds for all 24 strict grammars and for the tied control `G0`.

A literature check placed this precisely: it is the **Cartesian tree / treap** of the operator sequence keyed by binding power (Vuillemin, *A unifying look at data structures*, CACM 23(4), 1980), written from the parsing side instead of the data-structure side. Both halves are textbook — the Cartesian tree recursion is "root at the minimum, recurse left and right", and the expression-tree recursion is "root at the lowest-precedence operator, recurse left and right". Linear-time Cartesian tree construction is the monotone-stack algorithm, which *is* shunting-yard. The closest published prior art is LaLonde & des Rivières, *Handling Operator Precedence in Arithmetic Expressions with Tree Transformations*, TOPLAS 3(1), 1981 — local rotations with the Church–Rosser property, i.e. treap insertion by another name.

**Status: RESTATEMENT, not a result.** What appears unstated in the literature is only the explicit identity and the tie-breaking convention (rightmost minimum corresponds to left associativity; the usual Cartesian-tree convention is the opposite). That is a one-paragraph remark. Its real value here is operational: it is why 0023's decision procedure needs no parser. *OBSERVED — 0023; prior art Floyd 1963, Vuillemin 1980, LaLonde & des Rivières 1981.*

**T8. Reachability is decidable from a constraint graph.** A candidate parenthesization is reachable by some strict precedence grammar exactly when its induced order constraints contain no strict self-loop and no cycle between distinct operator types. Representation search over precedence space therefore does not require enumerating grammars.

**The method is textbook.** The Dragon Book's precedence-function construction already builds a digraph and concludes: *"If the constructed graph has a cycle then no precedence functions exist."* The mixed strict/weak refinement is the standard difference-constraint result. Recovering precedence from example trees is also an existing line of work (Aasa, TCS 1995; Afroozeh et al., SLE 2013; Crespi-Reghizzi et al., 1978).

**What appears unclaimed** is narrow: the *typed-priority* framing — Cartesian trees whose priorities are a function of the element's **type** rather than distinct per position — and a clean iff-theorem at the granularity of "one operator word plus one candidate tree, does a total order on the four types exist", including the strict-self-loop case. Nobody was found stating that exact decision problem. It remains a short exercise given the Dragon Book digraph. *OBSERVED — 0023; this is the project's single best novelty candidate, and it is a modest one.*

**T9. Precedence reaches a vanishing fraction of the parenthesization space.** Mean coverage of the Catalan tree space falls as expressions lengthen, and full coverage is possible only for short operator words.

**The headline is trivial by counting** and must not be presented as a theorem: at most `4! = 24` trees are reachable at any length while `Catalan(k) ~ 4^k / (k^1.5 √π)`, so the fraction vanishes by inspection. Qualitatively, "precedence cannot express some groupings" is already the subject of the deep-priority-conflict literature (Souza Amorim, Steindorfer & Visser, SLE 2017; *Programming* 2(3), 2018) and motivates partial-order precedence proposals. The only unclaimed content is the measured average curve, and the metric must be stated explicitly as *mean over operator words of reachable/Catalan*. **Status: OBSERVATION with a trivial explanation.** Its use is practical — it is the quantitative reason Phase 9 needs a parenthesization engine rather than a wider precedence registry. *OBSERVED — 0020, 0023.*

**T10. The tied control grammar is not redundant.** `G0` reaches parse trees that no strict total ordering reaches. Ties are an independent grammar dimension, not a convenience. *OBSERVED — 0020.*

### Group C — Cost and domain

**T11. Raw operation count is grammar-invariant; only dependency structure varies.** Every parse of a fixed token sequence consumes the same operator tokens, so the raw multiset of additions, subtractions, multiplications and divisions is identical across all 25 grammars, while the AST critical-path depth is not.

**Two corrections, both from review, both load-bearing.**

*First, the invariance half is a tautology.* The operator tokens are fixed by construction, so nothing is discovered by observing that they are still there after parsing. It is worth stating only as a **discipline rule**: a cost model built on operation count alone cannot express any difference that grammar makes, so it cannot be the project's cost model. It is not a finding.

*Second, the depth half must not be phrased as a performance claim.* Experiment 0021 measures structure and explicitly disclaims wall-clock results; depth is a structural upper bound on parallel evaluation, not a measured latency. Earlier wording here said depth changes "and therefore latency", which contradicted 0021's own limitations section and has been removed.

*Third, and most restrictive:* the classical tree-height-reduction results (Brent, JACM 21(2), 1974; Baer & Bovet, IFIP 1968; Muchnick ch. 12; LLVM's AArch64 MachineCombiner reassociation) assume **exact associativity and commutativity**. Generation 1 has left-associative `-` and `/`, so changing precedence changes the *function*, not the schedule. "Grammar choice is a latency question" is therefore true only inside the equivalence-preserving mode of Group E, and false in the semantic-exploration mode where every experiment 0001–0024 lives. *TAUTOLOGY plus a structural observation — 0021; prior art Brent 1974, Muchnick 1997.*

**T12. Computational collapse is real but belongs to semantic-variation mode.** Representation change can turn a variable-dependent expression into a constant, or a quadratic into a linear function. This measures the size of the algebraic collapse available in representation space; it is **not** yet a cheaper solution to the same problem, because the collapsed form is usually a different function. Only the equivalence-preserving subset transfers to the finite-field branch. *OBSERVED — 0001, 0003.*

**T13. Semantic equivalence is domain-relative.** Equivalence must be declared over `(F, D, U)` — function, domain, and undefined set — because canonical text equality alone manufactures false classes: `x/x` simplifies to `1` while remaining undefined at `x = 0`. The class structure further depends on the declared arithmetic domain, so it is a property of `(token sequence, grammar, domain)` and not of the first two alone. *JUSTIFIED — SPEC.md, 0015, 0022.*

### Group D — Open

**T14. Grammar space has no stable cluster structure beyond the null model. REFUTED on this corpus.** The question was whether specific grammar pairs or clusters systematically collapse together across thousands of controlled expressions, which would make grammar space algebraically or statistically structured rather than coincidental per expression.

Measured over a deterministic corpus of 3 125 expressions across five families:

```text
observed pairwise agreement   0.259307
support-forced (null model)   0.072000
AST-identity                  0.167333
excess over the null model    0.187307
```

The clustering computed from the excess matrix coincides **exactly** with the support-size-3 blocks: `set(excess clusters) == set(support-forced blocks)` is `True`, re-derived independently from `Grammar.levels` without calling the module under test. Once the parsing artifact of T6 is removed, **nothing remains**. Both halves of a deterministic split reproduce this at stability 1.0, so the null result is not a sampling accident.

The first draft of that experiment promoted the *observed*-matrix clustering as structure beyond the null; review established that two of its four clusters — `(G03,G04,G06,G20)` and `(G09,G10,G12,G22)` — are verbatim support-forced blocks. Half of the claimed discovery was the null model. That correction is the reason this thesis reads as it now does.

Scope: this refutes the hypothesis for controlled templates with small integer coefficients under the current semantic contract. It does not prove the absence of structure for arbitrary expressions. *OBSERVED, REFUTED — 0024.*

**T14a. What survives the null model: AST diversity and semantic diversity are decoupled.** Over the same 3 125 expressions the rank correlation between distinct-AST count and semantic class count is 0.7676, and **2 500 of 3 125 (80%)** hold AST diversity fixed while `C(E)` varies. Syntactic parse diversity is not a proxy for mathematical diversity, and neither may be reported in place of the other. This is the positive result of that experiment and it is independent of T14's refutation. *OBSERVED — 0024, confirming T3 at corpus scale.*

**T15. What makes an expression grammar-sensitive?** The unresolved form of T4. Candidate predictors to test: operator support size, operator repetition pattern, coefficient degeneracy, presence of division, and reachable-AST count.

**T16. Is representation-dependence of difficulty measurable rather than rhetorical?** The project's founding claim is that mathematical difficulty is partly a property of representation. T11 sharpens it into something testable: representation cannot change the operation count, only the dependency structure and the post-simplification form. The claim survives only if a measured, equivalence-preserving representation change reduces a real cost. *OPEN — Phases 11 and 12.*

### Group E — The equivalence-preserving mode

The project runs in two modes that must never be silently mixed. Every result must declare which one it belongs to.

```text
Semantic exploration                Equivalence-preserving search
(E, G1) != (E, G2)                  R1(x) == R2(x) on the declared domain
different function                  same function
study roots, domain, singularities  study cost: C(R2) < C(R1)
```

Experiments 0001 through 0024 are all semantic exploration. Group E is the second mode, and it is where the project acquires engineering value rather than only structural interest.

**T17. Equivalence-preserving representation change produces measurable engineering wins.** From the external UltrafastSecp256k1 project, branch [`experiment/representation-search`](https://github.com/shrec/UltrafastSecp256k1/tree/experiment/representation-search), now public.

The headline is the Meloni co-Z addition (`ZADDU`, 5M+2S) replacing the mixed addition (8M+3S) in odd-multiples table construction:

```text
zaddu   90.50 / 90.51 / 90.71 ns   [range 90.17 - 90.77]
madd   139.05 / 138.56 / 138.57 ns [range 131.81 - 139.05]
delta  -34.91% / -34.68% / -34.54%
i5-14400F, GCC 14.2.0, -O3 -march=native, P-core pinned, 11 passes, minimum taken
```

Two things make this more than a local win. The cost model **predicted 82.4 ns** from measured per-operation throughput and measured 90.5 ns, within 10 percent — a cost model that prices a formula before it is compiled. And the transformation came from the `coordinate_change` axis, which the project's own first assessment had ranked last: *point formulas at fixed coordinates are a local optimum, but changing the coordinate system is not.* That is this project's founding principle, confirmed against production code.

**End-to-end is far more modest, and the source says so plainly:** `build_glv52_table_zr` measured −7.19% on `dual_scalar_mul_gen_point` and −1.96% on `ecdsa_verify`, with zero regressions. A separate result, the constant-time SafeGCD inverse replacing the Fermat chain, measured 3847.5 ns → 1555.0 ns, a 2.47× improvement at equal timing guarantee.

*AUTHOR-MEASURED, source-verified by ParseAtlas from the public branch; NOT re-run here — the figures are specific to that machine. Intake at [case_studies/ultrafast_secp256k1/](case_studies/ultrafast_secp256k1/).* Promotion to BENCHMARKED requires an independent run on declared hardware, not merely a readable source.

**T17a. The axis ledger is now complete, and the negative results are most of it.** The x86-64 search is closed: **two axes confirmed, five refuted, one still open.** This is the denominator T18 needs — a corpus of wins alone yields a survivorship-biased `P(speedup | transformation)`.

Confirmed, both end-to-end with interleaved A/B and warm-up discarded:

```text
co-Z coordinate change (all 4 live sites)
    dual_scalar_mul_gen_point  -7.19%      ecdsa_verify  -1.96%
    0 regressions; controls inconclusive at -0.15% to -0.67%
CT SafeGCD inverse (both call sites)
    ElligatorSwift XDH  -8.23%             Session handshake  -4.35%
    predicted 7.87% from the primitive, measured 8.23%
    ecdh_compute correctly did NOT move (+0.18%) -- it does not use ecmult_const_xonly
```

Refuted, each by mechanism rather than by silence: **AVX2** — refuted at the multiply port, since a field multiply needs 25 limb-products in both the 5×52 scalar and the 10×26 AVX2 layouts, so the lane count is exactly cancelled by limb-count growth, and this part has no IFMA. **Strauss versus Pippenger** — already optimal at every `n` the engine reaches. **GLV decomposition** — 84.92 ns, 0.34% of a verify even if deleted outright. **sqrt/jacobi** — one jacobi per cold `lift_x` only, and the 1024-slot cache makes it 0.0% of `schnorr_verify`. **normalize_weak** — 0.60% of a BIP-352 scan and exactly 0.00% of `ecdsa_verify`, `schnorr_verify`, `dual_scalar_mul_gen_point`, `batch_verify` and ConnectBlock.

Earlier and equally load-bearing: co-Z is **exhausted** — the pattern it needs occurs in exactly four places, all four converted, *"there is no fifth"*, every caller enumerated. The co-Z Montgomery ladder is refuted at 4110 heavy operations against 1690, 2.43× more field work, surviving the most generous framing available.

Still open: the dual-mul G-table window width, 15 (1280 KB of a 2048 KB L2) against 13 and 12. All three builds exist and pass. **The decision needs ConnectBlock, not the micro-benchmark** — an isolated benchmark keeps the whole table resident and systematically flatters the large window. *OBSERVED — Ultrafast `b265ec2`, `e99ed29`.*

**T17b. The measured statement of this project's founding principle.** From the same source, as the recorded transferable result:

> Searching **within** a fixed representation found nothing: 5 894 generated equivalent programs moved 0.34%. **Changing** the representation found 7–8%.

**Correction, and it matters.** An earlier revision of this thesis called that "roughly a twentyfold gap". That was an overstatement: the two percentages do not share a baseline — the in-representation figure is against 123.37 ns on a shared, loaded machine and the representation-change micro-figure against 139.05 ns on a pinned i5-14400F, 12.7% apart — so dividing them is not legitimate. The defensible statement is weaker in form and stronger in substance:

> The in-representation search found **no improvement distinguishable from zero**, while the representation change delivered roughly 35%.

If the true in-representation optimum is zero, the ratio is unbounded rather than twentyfold, so this is a **lower bound**, not a measurement of a factor. The ~35% is independently reproduced three ways from the vendored snapshot alone — weighted model −34.69%/−35.75%, measured-throughput model 129.77 → 82.37 ns = −36.53% (which independently reproduces the 82.4 ns prediction recorded in T17), and loop heavy-operation count at T=16, 176 → 111 = −36.93%.

One further honesty note: the "local optimum" half is **beam-truncated** — depth 3, beam 40, where depth-1 branching alone is 188 and 54.8% of it is the `mul_square_trade` axis the engine's own S/M = 0.874 already refutes. That truncation weakens the local-optimum claim only. It does not touch T20a, which is by construction and independent of depth and beam. *OBSERVED — Ultrafast `b265ec2`; verification in [experiments/0027_rediscovery_feasibility/FINDINGS.md](experiments/0027_rediscovery_feasibility/FINDINGS.md).*

**T17c. A benchmark harness is part of the claim, not a detail beneath it.** The runner that produced these figures is worth adopting as the project standard, and the case-study schema should require its properties:

- **Six build variants from one source tree**, differing only in `-D` flags, so the tree is never a confounder.
- **Correctness gates the measurement**: the runner refuses to report a single timing until the audit is ALL PASSED on every variant.
- **One discarded warm-up per variant** — every arm's first invocation ran 30–70% slow, which alone turned real effects into "inconclusive".
- **Verdict by range separation**; overlapping ranges are inconclusive, and inconclusive is never a win.
- **Control metrics reported separately** — unmodified libsecp, OpenSSL, SHA-256, HKDF, AEAD. If a control separates, the run is untrustworthy and nothing below it means anything.

That control check earned itself immediately: it caught a **+12% cluster** across five hashing and AEAD operations containing no field inverse at all, landing within 0.16 points of each other — a loaded-machine artefact correctly named rather than published as a regression. *OBSERVED — Ultrafast `e99ed29`.*

**T17d. Representation search surfaced a P0 cryptographic vulnerability as a side effect.** While examining the batch-verification path, the search found that `schnorr_batch_verify` accepted batches containing individually-invalid signatures: a captured SHA-256 midstate discarded the 32 seed bytes still sitting in its buffer while the length counter kept counting them, so every randomiser weight collapsed to a public constant of the index alone, identical on every machine. With the weights fixed and public, defeating the check costs one modular inversion. Reproduced end to end on a 97-signature batch, fixed, and pinned with an exploit proof-of-concept that fails 6/8 before and passes 8/8 after.

The relevance here is methodological, not cryptographic: a systematic representation search reads code paths with a question no ordinary review asks — *what is this actually computing, and could it compute the same thing differently* — and that question found a soundness bug that the path's own dedicated audit module had passed through unchanged for the entire broken window. *OBSERVED — Ultrafast `3596a24`.*

**T18. Some transformation classes yield speedups far more often than others.** Once roughly 20 to 30 recorded optimizations exist, `P(speedup | transformation)` becomes estimable per transformation label — factorization, reassociation, sign relocation, projective rescaling, lazy reduction, addition chains, limb layout, operation scheduling. Below that sample size only raw counts may be reported. *HYPOTHESIS — case study intake.*

**T19. Operation count may be a poor predictor of measured speedup; dependency depth and register pressure may be better.** This is directly testable and connects to T11: experiment 0021 established that raw operation count is *invariant* under grammar change while dependency depth is not, so a cost model built on operation count alone cannot even express the difference that grammar makes. If the case-study records show speedup correlating with depth and register pressure rather than with operation-count delta, the project's cost model must be rebuilt around the dependency graph. *HYPOTHESIS — case study intake, 0021.*

**T19a. Sharpened by disassembly: the cost model can be answering the wrong question, not merely answering it imprecisely.** Ultrafast commit `fa14fcd` disassembled the hottest kernel, `fe52_mul_inner`, at GCC 14.2 `-O3 -march=native`: 228 instructions, of which 31 are multiplies (13.6%) and 98 are `mov`/`push`/`pop` (43.0%). The kernel is dominated by **data movement, not arithmetic**. 31 MULX at one per cycle is a 31-cycle floor; the measured 12.43 ns is about 58 cycles at 4.7 GHz, so roughly 27 cycles sit above the multiply floor and they are the **serial carry and fold chain**, not instruction count — at 228 instructions in 58 cycles the machine already retires near 4 IPC.

Two consequences, both recorded there:

- **Limb-level Karatsuba was refuted without being built.** It would remove 3 of 31 multiplies, about 1.3% of the kernel, while adding roughly 20 ALU operations and more live values — worsening the register pressure that already dominates. A structural argument closed an axis that an operation-count model would have ranked as promising.
- The weighted cost model prefers the production schedule 40.98 to 52.06, **but that model counts instructions and this kernel is not instruction-bound**, so the model is answering the wrong question and only a measurement settles it.

This is stronger than T19 as originally written. It is not that operation count is a noisy predictor; it is that for a kernel which is not instruction-bound, operation count is measuring a quantity that does not govern the outcome. *OBSERVED — Ultrafast `fa14fcd`; see [case_studies/ultrafast_secp256k1/](case_studies/ultrafast_secp256k1/).*

**T21. Three test classes that ordinary correctness testing does not provide.** Each was found the hard way in the Ultrafast work.

**Their status here is candidate practice, not law.** They come from a single external project on one problem domain and one machine, and ParseAtlas has not independently established that any of them is necessary in general — 0026 is a standing reminder of why that distinction matters, since the operation-count finding from that same source measurably did **not** transfer to the symbolic level. Adopt them as defaults for equivalence-preserving experiments here, and treat each as falsifiable in its own right rather than as a rule inherited from a successful project.

1. **Cost-regression tests.** The first co-Z chain passed every correctness check and delivered 10–18% instead of the measured 34.7%, because the operand order was wrong: `ZADDU` returns the sum together with its *first* operand on the new Z, so passing `(acc, d)` leaves the constant on the old Z and forces a 3M+1S rescale every step. That bug produces a **correct table, just a slower one** — no correctness test can ever find it. Pinned as `test_operand_order_is_load_bearing`.
2. **Uniform-error tests.** A windowed table stores pseudo-affine entries on one implied global Z. A build that lands on the wrong Z is **wrong in every entry by the same factor**, so spot-checking one entry proves nothing. This is exactly the failure mode a co-Z chain with drifting operands produces, and it requires walking all entries against an independent construction.
3. **Representation-invariant tests.** Assertions must be written against the canonical serialised form, never against internal coordinates — because changing the internals is precisely what the search does. A test pinned to internal representation breaks on every candidate and therefore gets deleted or weakened.

A fourth, from the same source: a **silent-wrong-answer window**. Changing a table-width constant while a separately written literal stayed at 15 gave a segfault at window 12 but, at window 13, **no crash and five silently wrong `dual_mul` results out of 89 checks**. A `static_assert` only helps while someone keeps the two constants syntactically linked; the behaviour itself must be asserted. *OBSERVED — Ultrafast `03245d99`, `422555c2`, `6f18bc1f`.*

**T20a. The co-Z form is unreachable by that search *by construction*, at any depth and any beam width.** Three lines of the vendored `repsearch/rewrite.py` fix the shape of every candidate it can ever produce: the input list is passed through literally at every level and no rule can introduce a free variable; the output key set is frozen by `set(candidate.outputs) != output_names`; and equivalence is raw coordinate **value** equality in `F_p`, deliberately stronger than projective equivalence.

ZADDU violates all three. Its inputs are `['X1','Y1','Z1','X2','Y2']` against the mixed add's `['X1','Y1','X2','Y2','Z']`, it has six output keys against three, and decisively **it is a different function of the same five numbers** — the two agree exactly only on the slice `Z = 1`. Two unequal maps cannot be joined by map-preserving rewrites.

So the recorded "local optimum at −0.34% over 5 894 rewrites" does not mean *nothing better exists*. It means **nothing better exists inside that space, and the answer was outside it.** *OBSERVED — 0027.*

**T20b. The distance to co-Z is one substitution on the inputs, and the engine is one level too low.** This is the useful half, and it was not obvious. Verified over 270 cases with `L = 1` uniformly:

```text
madd_production(X1, Y1, Z, X2*Z^-2, Y2*Z^-3)  ==  zaddu_sum_only(X1, Y1, X2, Y2, Z)
```

The substitution cancels symbolically inside the program — `u2 = (X2*Z^-2)*Z^2 = X2`, `s2 = (Y2*Z^-3)*Z^2*Z = Y2` — which kills exactly the 3M+1S Z-lifting prefix, taking 8M+3S to 5M+2S. Deleting those four instructions by hand and keeping every other instruction byte-for-byte yields a program raw-value identical to ZADDU on 396 of 396 cases.

**co-Z is therefore not a cleverer formula. It is the same program under a change of input encoding, with the now-dead prefix eliminated.** The rewriter rewrites programs; this happens at the input encoding, one level above it. *DERIVED — 0027.*

A second finding from the same analysis is immediately actionable: the co-Z copy of `P` in `dbl_z1_production` is **already computed** — `Xp = -t` from the first multiply, `Yp = s2` from the last square, `Z3 = Y`, verified 12/12. The DBLU half costs **zero extra operations** and is blocked solely by the frozen-output-set line. Relaxing that one line to a superset test is the cheapest real extension available to this engine.

**T20. The rediscovery gate — SUPERSEDED BY T24 as project direction; retained below as the record of experiment 0027.**

> **Read T20a, T20b and T20c as findings, not as a plan.** They are what 0027 measured on one external case study, and they are why the Region model exists. The forward direction is T24, which states the same two gates in general mathematical terms against targets drawn from ordinary mathematics. This project studies representation, not any one application area; the case study is evidence that the idea produces results, and is not a research agenda.

The staging below is kept because it correctly separates *generation* from *selection*, which T23 carries forward.

**T20 (as originally staged) — not well-posed as first written.** The original phrasing asked whether ParseAtlas could independently rediscover the co-Z rewrite. T20a shows that question is **unfair** in one direction — it asks an input-preserving rewriter for an input-representation change, which fails with probability 1 at every setting — and **too easy** in the other, since an axis with co-Z written into it makes the gate a tautology, and `tablebuild.py` already contains ZADDU and DBLU by name. It is also unsettleable here, being stated against a machine-specific figure ParseAtlas has verified nothing of.

Staged replacement:

- **T20.0 — golden case.** Preserve the baseline and candidate forms verbatim with their equivalence argument. *Attemptable now; near-done via the vendored snapshot.*
- **T20.1 — reachability negative control. DONE, and it is now a tested capability rather than a prose argument.** `src/parseatlas/reachability_control.py` decides reachability against a declared, closed set of structural commitments — `preserve_inputs`, `preserve_outputs`, `map_equality`, and a weaker `projective_equality` — and reports *which* commitment blocks a target, since "unreachable" alone is not actionable. It also reports the **agreement slice**: the constraint under which two unequal maps do coincide. That is what turned 0027's negative into the positive T20b finding, and it generalises — the structure is reproduced in ordinary polynomial algebra with no elliptic curves involved, so it is not a secp256k1 peculiarity.

Two properties matter more than the feature list. The control is **not sample-credulous**: review constructed an adversarial pair whose difference is a product vanishing on the entire sample pool, so all 11 samples agree, and the module still returns unequal via symbolic cancellation with an explicit sample-conflict flag. And it **classifies pairs it has never seen** — six independently constructed pairs, six correct verdicts, each naming exactly the blocking commitment.

Its own limit, stated: deciding these commitments is a **necessary** condition, not a sufficient one. A target passing all of them is not thereby reachable by any particular finite axis set. *OBSERVED — 0028.*
- **T20.2 — axis existence.** Define a coordinate-change axis **without naming Meloni, ZADDU or co-Z anywhere in its specification**, or the gate is circular. *Needs new machinery; specification in 0027 section C.*
- **T20.3 — rediscovery, split into generation and SELECTION.** Selection is the harder half: the wrong operand order yields a **correct** table that delivers 10–18% instead of 34.7%, and neither a correctness oracle nor a per-formula cost model can see the difference. A search that generates the right candidate and cannot rank it has not rediscovered anything.
- **T20.4 — transfer.** The same axis finds something on an unrelated target. *Needs a second case study.*

*OPEN, restaged — Phase 11 exit gate.*

**T20c. The sharp form of the thesis.** From 0027, and it is the most compact statement the project has produced:

> **The completeness of a representation search and its blindness to representation change are the same property.**

A search is complete precisely because it fixes a language — inputs, outputs, and an equivalence relation. Those same three commitments are what make the representation itself unreachable. Widening the axis set does not fix this; changing what the search is allowed to hold fixed does. *DERIVED — 0027.*

### Group F — The turn: from grammar statistics to a representation-axis engine

**CORRECTED 2026-09-03.** An earlier revision of this section declared the whole Generation 1 grammar branch frozen and moved the project's centre to the representation-axis engine. **That was premature and it is withdrawn.** What is sufficiently characterised is **Direction A on the grammar space** — asking what a fixed string means under each grammar. Direction B on that same space is the founding question and is barely begun.

The Direction A result stands and is what closes it: the space collapses into semantic classes (T1), the collapse is not universal (T2), there is no cluster structure beyond the parsing artifact (T14), no transferable structural predictor of sensitivity (T15), precedence reaches a vanishing fraction of the parenthesization space (T9), and widening the parameter hits diminishing returns fast — associativity multiplied the registry sixteenfold, recovered under twelve percent of the gap, and added **50 percent more syntax with zero new mathematics** on the template corpus (T30).

Phase 14 below remains a real long-range programme, strengthened by the external evidence. **It does not replace the founding question and must not be allowed to.** The ordering is: Direction B is the main line; Phase 14 runs behind it.

Two ways this project can lose its subject, both named so they can be avoided:

1. becoming an **operator-precedence grammar research project**. Cartesian trees, Catalan coverage, associativity matrices and reachability constraints were needed to understand the Generation 1 space. That work is done.
2. spending its energy adding **more domain property analyzers** — further `sin`, `log`, ODE and probability extractors. Those exercise the infrastructure and answer the central question less and less.

The subject is wider than either:

```text
Given a problem, search representations in which its structure or its cost changes radically.
```

**T22. Equivalence must generalise beyond value equality.** The equivalence-preserving mode has been written as `F1(x) = F2(x)`. Almost nothing interesting fits that shape. Ordinary mathematics is full of transformations where the two sides do not even take the same inputs:

```text
a rational value            <->  a (numerator, denominator) pair, divided once at the end
a polynomial in x^k         <->  the same polynomial in a Chebyshev or Bernstein basis
a closed form               <->  a recurrence, or a matrix power
a single rational function  <->  its partial-fraction decomposition
a product                   <->  a sum of logarithms
a linear map                <->  a factorisation of it
```

Each changes the input encoding, often the number of outputs, usually the carried state, and sometimes the preconditions — while denoting the same mathematical object **at the boundary**. That is the class of transformation this project exists to search, and value equality cannot express any of it. The obligation therefore becomes a decode relation

```text
decode(R2(x')) = R1(x)        or, generally,     R(s_baseline, s_candidate)
```

and the search object stops being an expression AST. It becomes a **Region**:

```text
Region = (inputs, state, operations, outputs, invariants)
candidate:  R : Region_A -> Region_B
```

This is exactly what 0028's reachability control was measuring the absence of: `preserve_inputs`, `preserve_outputs` and `map_equality` are the three commitments a Region transformation is allowed to break — and the decode relation is what must replace the equality it gives up. *OPEN — Phase 14.*

**T23. Generation is not the hard half; SELECTION is.** A real engine is `Generate + Prove + Rank + Measure`, not `Generate + Check equivalence`. Two candidates can be *both correct* and differ substantially in cost, in a way no correctness oracle sees and no per-formula operation count expresses — because the difference is a per-step overhead amortised across a loop, invisible until the region is priced as a whole. Experiment 0033 reproduces exactly this: two orderings of the same rational computation with identical single-step cost, `div 1, mul 1, total 2, depth 2`, and loop costs of `n+1` against `2n`. Ranking at region level rather than formula level is where the engine will actually be hard. *OPEN — Phase 14.*

**T24. The two acceptance gates, in order of increasing importance.**

1. **Rediscovery.** Given a transformation that is already known to be good in some area of mathematics, can the engine find it **without that transformation being named anywhere in the search specification**? This proves the engine finds independently what was previously found by hand. Note T20a: any transformation that changes the input encoding is unreachable to an input-preserving rewriter at every depth, so passing this gate requires the Region model, not a wider axis list.
2. **Generalisation, and this is the one that matters.** Does the same representation axis, unchanged, find something useful on an unrelated problem? Gate 1 proves the engine works once. Gate 2 proves the **method** transfers, and that is where the project stops being anecdotal.

**Candidate targets, all ordinary mathematics.** The engine is to be developed against these, not against any one application area:

```text
polynomial evaluation      monomial + Horner  vs  a different basis  vs  factored form
rational arithmetic        divide per step    vs  carry (num, den), divide once
sequences                  closed form        vs  recurrence  vs  matrix power
rational functions         one expression     vs  partial-fraction decomposition
products                   direct             vs  sum of logarithms
```

Each has a classical decode map, a real structural cost difference, and none of them requires anything outside general mathematics. *OPEN — Phase 14 exit gates.*

## A standing caveat on negative results

**A structure invisible in the representations we searched is not thereby absent.**

The measurements make this concrete rather than philosophical. The written form `x*x + y*y - r*r` is a circle in 9 of the 25 worlds; in the other 16 it is a cubic or a quartic curve. `y - m*x - c` is a straight line in 13 worlds and a hyperbola in 12. The circularity did not go anywhere — the representation simply stopped presenting it as a recognisable form. And symmetrically: in a world where our circle reads as a quartic, that world's natural objects would read as noise to us.

So perception of form is representation-relative. Form is not.

This applies directly to this project's own negative findings and must be read alongside every one of them:

- **T14** — "no residual cluster structure in grammar space beyond the null model" means *none that survives the excess-matrix measurement on that corpus*. It is not a proof that grammar space is unstructured.
- **T15** — "no transferable structural predictor of grammar sensitivity" means *none among the 21 features tested, on that corpus, across template shapes*. A predictor in a representation we did not construct would not have shown up.
- **0026** — "the operation-count finding does not transfer to the symbolic level" is a statement about what the symbolic level exposes, not about what the transformation is.
- **0020, 0023** — "92.159% of parenthesizations are unreachable" is exact, but it is a statement about *precedence* as a representation. 0027 then showed the interesting object was unreachable by construction rather than absent, and 0028 turned that into a control.

The discipline this imposes is not to weaken the negatives — they are measured and they stand as measured. It is to state their **scope** in the same breath as their content: what was searched, in what representation, and therefore what a null result can and cannot rule out. A negative reported without its representation is an overclaim in the same way an unqualified positive is.

## Research Principles

- Treat `(token sequence, grammar)` as the research object.
- Keep `G0` conventional control separate from `G01..G24` strict permutations.
- Preserve AST, canonical form, domain, undefined set, and cost as separate evidence.
- Distinguish observation, symbolic justification, numerical validation, hypothesis, and benchmark.
- Expand one controlled dimension at a time; do not infer general laws from one expression.
- Preserve an independent reference implementation before introducing a performance engine.

## Phase Gates

Every phase must provide:

1. an implementation or dataset change;
2. focused regression tests;
3. a generated report with commands and environment details;
4. a commit and pushed revision;
5. a short statement of what remains unproven.

## Phase 1: Grammar and Parsing Foundation [Complete]

- Define the binary Generation 1 language.
- Register `G0` and all 24 strict precedence permutations.
- Implement deterministic tokenization and left-associative parsing.
- Serialize reproducible ASTs.
- Reproduce the initial strict `24 -> 8` finding.

Exit gate: parser and golden tests pass.

## Phase 2: Domain-Aware Symbolic Analysis [Complete]

- Convert custom ASTs into symbolic objects only after parsing.
- Keep exact rational constants.
- Track denominator restrictions.
- Group by function, domain, and undefined/singularity set.
- Extract polynomial degree, coefficients, roots, discriminant, vertex, and critical points.

Exit gate: simplification cannot silently erase `x != 0` for `x/x`.

## Phase 3: Outer-Function Atlas [Complete]

- Evaluate trigonometric, exponential, logarithmic, root, absolute-value, inverse-trigonometric, reciprocal, square, and cube families.
- Measure constant collapse, frequency, period, and real-domain behavior.
- Propagate inner validity metadata into outer results.

Exit gate: outer-function results are derived from shared inner grammar results and are independently tested.

## Phase 4: Controlled Corpus [Complete]

- Start with linear, polynomial, rational, and removable-restriction families.
- Record `grammar count -> AST count -> semantic-class count`.
- Record degree distributions and pole distributions.
- Avoid uncontrolled random expressions until generation parameters are specified.

Exit gate: every corpus item is reproducible from an explicit expression list.

## Phase 5: Parameter Sweeps and Cost Model [In Progress]

### 5A. Coefficient sweep

- Sweep small integer coefficients over controlled linear and polynomial templates.
- Add rational coefficients with bounded numerator and denominator.
- Measure class count, AST diversity, degree collapse, roots, poles, and restrictions.
- Store aggregate distributions and exceptional cases.

### 5B. Cost model

- Separate raw AST operation count from canonical operation count.
- Add symbolic simplification time and serialized expression size.
- Add evaluation benchmarks at declared sample points.
- Report median, percentile, and variance; do not compare single timings.
- Record Python, SymPy, CPU, and operating-system versions.

Exit gate: a cost report must identify whether a cheaper representation is cheaper before or after symbolic preprocessing.

## Phase 6: Rational and Function Semantics

- Expand poles, zeros, removable singularities, asymptotes, and connected real-domain components.
- Add explicit domain conditions for `log`, `sqrt`, inverse functions, and reciprocal outer layers.
- Introduce branch conventions for complex analysis.
- Compare symbolic and numerical domain checks.

Exit gate: each semantic property includes its assumptions and failure modes.

## Phase 7: Invariant Mining

- Search for repeated relations across controlled families.
- Compare coefficient relations, root relations, symmetry, degree, domain topology, and class structure.
- Generate conjectures only from repeated measurements.
- Attempt symbolic proofs and adversarial counterexamples.

Exit gate: every claimed invariant has a tested scope and documented counterexample search.

## Phase 8: Precedence-Space Graph

- Represent each strict grammar as a node.
- Connect grammars differing by one adjacent precedence swap.
- Measure local changes in AST, degree, roots, domains, singularities, and cost.
- Search paths toward simpler canonical forms.

Exit gate: graph navigation agrees with exhaustive enumeration on small corpora.

## Phase 9: Associativity and Parenthesization

- Add right associativity and operator-specific associativity.
- Enumerate explicit parenthesizations independently of precedence.
- Compare precedence-generated ASTs with the wider binary-tree space.
- Identify duplicate grammar states and structurally unreachable trees.

Exit gate: associativity is a first-class grammar parameter and remains backward compatible with Generation 1.

## Phase 10: Numerical and Statistical Validation

- Evaluate canonical forms at exact-safe sample points.
- Exclude or explicitly test singular points.
- Compare symbolic equality with numerical disagreement detection.
- Add corpus seeds, parameter manifests, and result hashes.
- Use confidence intervals for corpus distributions where sampling is introduced.

Exit gate: numerical checks never replace symbolic/domain reasoning.

## Phase 11: Performance Engine

- Keep the Python reference oracle as the correctness authority.
- Benchmark parsing, canonicalization, property extraction, and evaluation separately.
- Add a compiled engine only after data-model and semantic contracts stabilize.
- Cross-check compiled results against the reference oracle.

Exit gate: performance improvements preserve serialized AST and semantic metadata on the validation corpus.

## Phase 12: Finite Fields and Cryptographic Representations

- Introduce finite-field domains only with explicit modulus metadata.
- Search only equivalence-preserving transformations.
- Verify `F1(x) == F2(x) mod p` or projective-point equivalence.
- Add secp256k1 experiments only after independent correctness tests.
- Never treat semantic reinterpretation as cryptographic optimization.

Exit gate: every optimization has a proof obligation and an adversarial test suite.

## Phase 13: Publication and Release

- Maintain English methodology and publication documents.
- Maintain Georgian experiment reports for project communication.
- Include exact commands, dependency versions, report hashes, and limitations.
- Freeze datasets and generate a reproducibility bundle.
- Tag releases only after all phase gates and full validation pass.

Exit gate: an external researcher can reproduce the reported tables from a clean checkout.

The project begins with operator-precedence permutations and then expands toward a broader search over mathematical representations, equivalence classes, invariants, and computational cost.

The roadmap is intentionally empirical:

> Generate representations, measure structure, classify equivalence, search for invariants, and only then generalize.

---

# Phase 0 — Research Baseline

## Goal

Establish a reproducible baseline so every later experiment can be compared against the same rules.

## Tasks

- Define the initial operator set:

```text
+ - * /
```

- Enumerate all strict precedence orders:

```text
4! = 24
```

- Fix associativity rules for the first generation:
  - binary operators only
  - left-to-right associativity for equal precedence
  - explicit parentheses override precedence
  - precedence is global within one grammar
  - symbolic simplification occurs only after parsing

- Define supported domains:
  - real numbers
  - complex numbers
  - integers
  - rational numbers
  - finite fields in later phases

- Define a canonical experiment record.

Suggested schema:

```text
experiment_id
token_string
grammar_id
precedence_order
AST
canonical_expression
domain
equivalence_class
roots
singularities
degree
extrema
period
operation_count
dependency_depth
notes
```

## Exit criteria

- All 24 grammars can parse the same token string deterministically.
- Every parsed expression can be serialized to a reproducible AST.
- Equivalent canonical expressions can be grouped automatically.

---

# Phase 1 — Precedence-24 Engine

## Goal

Build the core engine that maps one token sequence into all 24 precedence interpretations.

## Tasks

- Implement grammar enumeration.
- Implement parser generation for each precedence order.
- Produce ASTs for all 24 interpretations.
- Add canonical symbolic simplification.
- Deduplicate equivalent canonical expressions.
- Assign stable equivalence-class IDs.
- Export results as JSON and Markdown.

## Initial validation expressions

```text
2*t + 1 - t/2
2*x + 3
2*x*x + 1 - x/2
a + b*c - d/e
```

## Metrics

For every input expression record:

```text
24 raw grammar states
N unique AST forms
M unique canonical forms
equivalence class sizes
```

## Exit criteria

- Reproduces the first observed result:

```text
24 precedence states
        ↓
8 canonical forms
```

for the initial sine experiment's inner expression.

---

# Phase 2 — Function Atlas

## Goal

Study how grammar-induced changes propagate through common mathematical functions.

## Function families

Start with:

```text
sin(E)
cos(E)
tan(E)
exp(E)
log(E)
sqrt(E)
abs(E)
1/E
E^2
E^3
```

Then extend to:

```text
sinh(E)
cosh(E)
tanh(E)
asin(E)
acos(E)
atan(E)
floor(E)
ceil(E)
sign(E)
```

## Properties to extract

### Trigonometric functions

- period
- frequency
- phase
- amplitude changes caused by surrounding structure
- singularities
- constant collapse

### Polynomial functions

- degree
- coefficients
- roots
- discriminant
- extrema
- factorization
- repeated roots

### Rational functions

- poles
- zeros
- removable singularities
- asymptotic behavior

### Logarithmic / root functions

- domain boundaries
- branch behavior
- singularities
- collapse to constants

### Exponential functions

- growth rate
- decay rate
- constant collapse

## Exit criteria

Create the first searchable atlas of:

```text
token sequence
×
precedence grammar
×
outer function
→
mathematical behavior
```

---

# Phase 3 — Equivalence Classes

## Goal

Treat different grammars as elements of a structured representation space instead of isolated cases.

Define:

```text
Gi ~ Gj
```

when:

```text
canonical(E(Gi)) = canonical(E(Gj))
```

## Tasks

- Compute equivalence classes for every expression.
- Measure class sizes.
- Compare class structure across expression families.
- Detect recurring grammar pairings.
- Search for precedence permutations that often collapse together.
- Build an equivalence graph.

## Questions

- Do some grammar permutations behave similarly across many expressions?
- Are there stable clusters inside the 24-state space?
- Is the 24-state space reducible to a smaller effective basis for some expression families?
- What determines the number of unique canonical forms?
- Are there expression classes where all 24 remain distinct?
- Are there expression classes where most collapse to one or two forms?

## Exit criteria

Produce a first classification of precedence-space behavior across a large expression corpus.

---

# Phase 4 — Invariant Search

## Goal

Find mathematical quantities that remain stable while precedence changes.

For a property `I`, search for:

```text
I(E(G1)) = I(E(G2)) = ... = I(E(Gk))
```

for non-trivial subsets or the entire grammar space.

## Candidate invariants

- common roots
- common factors
- conserved coefficient combinations
- root sums
- root products
- parity
- sign structure
- symmetry classes
- domain topology
- number of connected domain components
- singularity count
- extrema count
- asymptotic class
- periodicity class
- equivalence-class structure itself
- computational-cost class

## Important rule

Do not assume what should be invariant.

The workflow is:

```text
generate
→ measure
→ cluster
→ detect repeated relations
→ formulate conjecture
→ prove or falsify
```

## Exit criteria

At least one non-trivial invariant or stable relation discovered across a meaningful expression family.

---

# Phase 5 — Representation Cost Atlas

## Goal

Measure when a representation becomes computationally cheaper after parsing and simplification.

Distinguish three costs:

```text
raw parse cost
symbolic simplification cost
canonical evaluation cost
```

## Initial operation metrics

```text
additions
subtractions
multiplications
divisions
powers
roots
transcendental calls
temporary values
dependency depth
```

## Extended implementation metrics

Later add:

```text
instruction count
latency
throughput
branch count
branch mispredictions
register pressure
spills
memory traffic
cache behavior
vectorization potential
GPU occupancy
```

## Key research target

Detect cases such as:

```text
variable-dependent expression
→
constant
```

or:

```text
quadratic
→
linear
```

or:

```text
division-heavy form
→
multiplication/addition form
```

## Exit criteria

A cost model that can rank representations and identify computational collapse automatically.

---

# Phase 6 — Expression Corpus Generation

## Goal

Move beyond hand-selected examples.

## Corpus families

Generate expressions from controlled grammars:

### Linear

```text
a*x + b
a*x + b - c*x/d
```

### Polynomial

```text
a*x*x + b*x + c
a*x*x*x + b*x*x + c*x + d
```

### Rational

```text
(a*x+b)/(c*x+d)
```

### Mixed operator chains

```text
a*x + b - c*x/d
a/b + c*x - d/e
```

### Nested functions

```text
sin(a*x+b-c/d)
log(a*x+b-c*x/d)
sqrt(a*x+b-c)
```

## Dataset controls

Record:

```text
expression depth
operator count
operator diversity
variable count
constant count
nesting depth
```

## Exit criteria

A reproducible corpus large enough to statistically analyze grammar behavior.

---

# Phase 7 — Precedence Graph

## Goal

Exploit the fact that the 24 precedence orders form a permutation space.

Treat each grammar as a node.

Connect grammars that differ by one adjacent precedence swap.

Example:

```text
+ > - > * > /
```

to:

```text
- > + > * > /
```

## Study

- local changes in roots
- local changes in degree
- local changes in domain
- local changes in singularities
- local changes in computational cost
- paths toward simpler representations
- stable regions
- abrupt structural transitions

## Research question

Can representation search be treated as navigation over a graph rather than brute-force enumeration?

## Exit criteria

A graph model of the 24-state precedence space with measurable transition effects.

---

# Phase 8 — Associativity Expansion

## Goal

Relax the initial fixed associativity rule.

Add:

- left associativity
- right associativity
- operator-specific associativity
- explicit non-associative handling

## Example

```text
a-b-c
```

can become:

```text
(a-b)-c
```

or:

```text
a-(b-c)
```

## Research question

How much new semantic diversity comes from associativity compared with precedence alone?

## Exit criteria

A combined:

```text
precedence × associativity
```

representation atlas.

---

# Phase 9 — Full Parenthesization Space

## Goal

Move beyond global precedence orderings into arbitrary valid AST structures.

For a token sequence with binary operators, enumerate structurally valid parenthesizations.

This expands the search space from precedence permutations toward Catalan-style AST spaces.

## Compare

```text
precedence-generated ASTs
vs
all possible ASTs
```

## Questions

- What fraction of all ASTs can be generated by a global precedence rule?
- Which useful representations are inaccessible through precedence alone?
- Do computationally cheap forms frequently lie outside the precedence-generated subset?

## Exit criteria

A general expression-representation search engine.

---

# Phase 10 — Representation Transformations

## Goal

Add transformations that preserve mathematical meaning.

Examples:

- associativity
- commutativity
- distributivity
- factorization
- expansion
- common-subexpression elimination
- constant folding
- substitution
- basis changes
- coordinate transforms

## Important distinction

At this phase there are two separate research modes:

### Semantic variation mode

Different parses may represent different mathematical functions.

### Equivalence-preserving optimization mode

Only transformations that preserve the final mathematical object are allowed.

These modes must never be mixed silently.

## Exit criteria

A transformation engine that explicitly labels whether a candidate is:

```text
semantic variant
```

or:

```text
provably equivalent representation
```

---

# Phase 11 — Automated Representation Search

## Goal

Search representation space automatically.

Given a problem:

```text
P
```

generate candidate representations:

```text
R1(P), R2(P), ..., Rn(P)
```

then rank them by:

```text
mathematical simplicity
computational cost
proof status
numerical stability
```

## Basic objective

```text
R* = argmin Cost(Ri(P))
```

subject to the required semantic constraints.

## Search strategies

- exhaustive search
- graph search
- beam search
- heuristic search
- evolutionary search
- learned ranking
- symbolic superoptimization

## Exit criteria

The system can discover a cheaper representation without being told the transformation manually.

---

# Phase 12 — Finite Fields

## Goal

Move the methodology into modular arithmetic.

Study expressions under:

```text
mod p
```

where identities can produce collapses unavailable over the reals.

## Research areas

- modular reduction identities
- special-prime structure
- limb representations
- carry strategies
- multiplication decomposition
- squaring decomposition
- inversion chains
- exponentiation chains

## Constraint

Every optimization candidate must satisfy:

```text
F1(x) ≡ F2(x) mod p
```

for the required domain.

## Exit criteria

Verified equivalent transformations that reduce measured finite-field cost.

---

# Phase 13 — secp256k1 Research Branch

## Goal

Apply ParseAtlas ideas to real elliptic-curve primitives.

Target field:

```text
p = 2^256 - 2^32 - 977
```

## Primitive targets

- field addition
- field subtraction
- field multiplication
- field squaring
- field reduction
- field inversion
- square root
- affine point addition
- Jacobian point addition
- mixed Jacobian-affine addition
- point doubling
- scalar multiplication

## Representation dimensions

- limb layout
- projective scaling
- sign placement
- factorization
- associativity
- reduction placement
- lazy reduction
- coordinate systems
- addition chains
- common-subexpression reuse
- operation scheduling

## Correctness rule

For finite-field expressions:

```text
candidate ≡ baseline mod p
```

For projective points:

```text
candidate and baseline
must represent the same affine point
```

## Validation pipeline

```text
symbolic equivalence
→
randomized numerical validation
→
edge-case validation
→
differential testing
→
benchmark
```

## Performance metrics

```text
ns/op
cycles/op
instructions/op
dependency depth
register pressure
spills
branches
cache behavior
```

## Exit criteria

At least one verified representation-derived improvement in a real primitive.

---

# Phase 14 — Invariant and Constant Discovery

## Goal

Search the accumulated atlas for repeated quantities and structures that were not explicitly encoded.

## Targets

- representation-invariant values
- fixed points under grammar transformations
- repeated root relations
- stable coefficient relations
- recurrent ratios
- symmetry groups
- transition invariants
- universal equivalence classes
- cost invariants

## Discipline

Any candidate constant or invariant must pass:

```text
large-scale empirical recurrence
→
independent validation
→
symbolic explanation or proof attempt
```

No pattern is promoted to a mathematical claim from a small sample.

---

# Phase 15 — Visualization

## Goal

Make representation space visually inspectable.

## Visualizations

- 24-panel function grids
- precedence permutation graph
- equivalence-class maps
- root migration plots
- singularity migration plots
- domain-boundary maps
- computational-cost heatmaps
- AST comparison views
- transformation paths

## Exit criteria

A researcher can visually identify clusters, collapses, and transitions before inspecting raw symbolic data.

---

# Phase 16 — Reproducible Research Package

## Goal

Make every result independently reproducible.

Every published experiment should contain:

```text
input expressions
grammar rules
parser version
canonicalizer version
domain
generated ASTs
raw results
simplified results
analysis script
plots
benchmark environment
commit hash
```

## Required result labels

Every conclusion must be tagged as one of:

```text
OBSERVED
PROVEN
NUMERICALLY_VALIDATED
HYPOTHESIS
BENCHMARKED
FALSIFIED
```

## Exit criteria

No major result exists only as prose.

---

# Suggested Repository Structure

```text
ParseAtlas/
├── README.md
├── ROADMAP.md
├── RESEARCH.md
├── docs/
│   ├── terminology.md
│   ├── methodology.md
│   ├── hypotheses.md
│   └── literature.md
├── src/
│   ├── parser/
│   ├── grammar/
│   ├── canonicalizer/
│   ├── analyzer/
│   ├── invariants/
│   ├── cost_model/
│   └── search/
├── experiments/
│   ├── precedence24/
│   ├── functions/
│   ├── polynomials/
│   ├── rational/
│   ├── associativity/
│   ├── ast_space/
│   ├── finite_fields/
│   └── secp256k1/
├── datasets/
├── results/
│   ├── raw/
│   ├── canonical/
│   ├── equivalence_classes/
│   ├── invariants/
│   ├── plots/
│   └── benchmarks/
└── tests/
```

---

# Near-Term Milestones

## M1 — Precedence-24 prototype

Deliver:

```text
expression
→
24 ASTs
→
canonical forms
→
equivalence classes
```

## M2 — First function atlas

Cover:

```text
sin
cos
tan
exp
log
sqrt
reciprocal
polynomials
```

## M3 — Corpus-scale run

Run thousands of generated expressions and identify recurring equivalence structures.

## M4 — Cost model

Rank canonical forms by operation count and dependency depth.

## M5 — Invariant miner

Automatically search for repeated mathematical relations across grammar states.

## M6 — AST-space expansion

Move beyond precedence into full parenthesization space.

## M7 — Finite-field prototype

Introduce modular arithmetic and proof-preserving transformations.

## M8 — secp256k1 primitive experiment

Run the first real benchmark comparing equivalent representations of a cryptographic primitive.

---

# Long-Term Research Direction

The long-term objective is broader than operator precedence.

ParseAtlas starts from:

```text
same tokens
+
different grammar
```

but evolves toward:

```text
same problem
+
many representations
+
measured mathematical structure
+
measured computational cost
```

The central hypothesis is:

> A significant part of mathematical and computational difficulty may be representation-dependent.

The project therefore searches not only for better algorithms inside a fixed representation, but for representations in which the problem itself becomes structurally simpler.

---

# Working Principle

> **Do not optimize the current representation before asking whether another valid representation makes the problem simpler, cheaper, or disappear entirely.**

