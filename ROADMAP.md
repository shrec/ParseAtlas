# ParseAtlas Research Roadmap

This roadmap defines the staged research program for ParseAtlas. Each phase produces executable artifacts, tests, and a report before the next phase expands the search space.

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

**T14. Does grammar space have stable cluster structure?** If specific grammar pairs or clusters systematically collapse together across thousands of controlled expressions, grammar space has measurable algebraic or statistical structure rather than per-example coincidence. Any such claim must be stated against the T6 null model — agreement forced by operator-support reduction is not a discovery — and must survive a corpus half-split stability check. *HYPOTHESIS — 0024.*

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

**T17a. Negative results are the more valuable half, and they exist.** The co-Z transformation is recorded as **exhausted**: the pattern it needs — a chain accumulating P, 3P, 5P by repeatedly adding a constant 2P — occurs in exactly four places on the x86-64 FE52 build, all four are converted, and *"there is no fifth"*, with every caller enumerated and each rejected site refuted by mechanism rather than by silence. The co-Z Montgomery ladder is refuted decisively: 4110 heavy operations against 1690, i.e. 2.43× more field work, and the gap survives the most generous framing available. An automatic search over point formulas kept 1494 distinct equivalent programs from 5894 rewrites with 0 unsound, and found nothing better than −0.34%, inside noise — the production formulas are a local optimum in that rewrite space.

This matters for T18: a corpus of wins alone yields a survivorship-biased `P(speedup | transformation)`. These refutations are the denominator. *OBSERVED — same source.*

**T18. Some transformation classes yield speedups far more often than others.** Once roughly 20 to 30 recorded optimizations exist, `P(speedup | transformation)` becomes estimable per transformation label — factorization, reassociation, sign relocation, projective rescaling, lazy reduction, addition chains, limb layout, operation scheduling. Below that sample size only raw counts may be reported. *HYPOTHESIS — case study intake.*

**T19. Operation count may be a poor predictor of measured speedup; dependency depth and register pressure may be better.** This is directly testable and connects to T11: experiment 0021 established that raw operation count is *invariant* under grammar change while dependency depth is not, so a cost model built on operation count alone cannot even express the difference that grammar makes. If the case-study records show speedup correlating with depth and register pressure rather than with operation-count delta, the project's cost model must be rebuilt around the dependency graph. *HYPOTHESIS — case study intake, 0021.*

**T19a. Sharpened by disassembly: the cost model can be answering the wrong question, not merely answering it imprecisely.** Ultrafast commit `fa14fcd` disassembled the hottest kernel, `fe52_mul_inner`, at GCC 14.2 `-O3 -march=native`: 228 instructions, of which 31 are multiplies (13.6%) and 98 are `mov`/`push`/`pop` (43.0%). The kernel is dominated by **data movement, not arithmetic**. 31 MULX at one per cycle is a 31-cycle floor; the measured 12.43 ns is about 58 cycles at 4.7 GHz, so roughly 27 cycles sit above the multiply floor and they are the **serial carry and fold chain**, not instruction count — at 228 instructions in 58 cycles the machine already retires near 4 IPC.

Two consequences, both recorded there:

- **Limb-level Karatsuba was refuted without being built.** It would remove 3 of 31 multiplies, about 1.3% of the kernel, while adding roughly 20 ALU operations and more live values — worsening the register pressure that already dominates. A structural argument closed an axis that an operation-count model would have ranked as promising.
- The weighted cost model prefers the production schedule 40.98 to 52.06, **but that model counts instructions and this kernel is not instruction-bound**, so the model is answering the wrong question and only a measurement settles it.

This is stronger than T19 as originally written. It is not that operation count is a noisy predictor; it is that for a kernel which is not instruction-bound, operation count is measuring a quantity that does not govern the outcome. *OBSERVED — Ultrafast `fa14fcd`; see [case_studies/ultrafast_secp256k1/](case_studies/ultrafast_secp256k1/).*

**T21. Representation search needs three test classes that ordinary correctness testing does not provide.** Each was found the hard way in the Ultrafast work, and each is now a standing requirement for any ParseAtlas equivalence-preserving experiment.

1. **Cost-regression tests.** The first co-Z chain passed every correctness check and delivered 10–18% instead of the measured 34.7%, because the operand order was wrong: `ZADDU` returns the sum together with its *first* operand on the new Z, so passing `(acc, d)` leaves the constant on the old Z and forces a 3M+1S rescale every step. That bug produces a **correct table, just a slower one** — no correctness test can ever find it. Pinned as `test_operand_order_is_load_bearing`.
2. **Uniform-error tests.** A windowed table stores pseudo-affine entries on one implied global Z. A build that lands on the wrong Z is **wrong in every entry by the same factor**, so spot-checking one entry proves nothing. This is exactly the failure mode a co-Z chain with drifting operands produces, and it requires walking all entries against an independent construction.
3. **Representation-invariant tests.** Assertions must be written against the canonical serialised form, never against internal coordinates — because changing the internals is precisely what the search does. A test pinned to internal representation breaks on every candidate and therefore gets deleted or weakened.

A fourth, from the same source: a **silent-wrong-answer window**. Changing a table-width constant while a separately written literal stayed at 15 gave a segfault at window 12 but, at window 13, **no crash and five silently wrong `dual_mul` results out of 89 checks**. A `static_assert` only helps while someone keeps the two constants syntactically linked; the behaviour itself must be asserted. *OBSERVED — Ultrafast `03245d99`, `422555c2`, `6f18bc1f`.*

**T20. The rediscovery gate.** The first real test of an automated representation-search engine is not a new optimization but an old one: *can ParseAtlas independently rediscover the 34 percent Ultrafast rewrite that was found by hand?* Until a search finds, without being told the transformation, a representation a human already found, the system is a description of intuition rather than a search procedure. This is the acceptance gate for Phase 11 and it requires the baseline and candidate forms of that rewrite to be preserved verbatim as a golden case. *OPEN — Phase 11 exit gate.*

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

