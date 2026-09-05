# ParseAtlas: research, prior-art and project-potential audit

**Audit date:** 2026-09-05. **Georgian:** [full Georgian report](novelty-audit-2026-09-05.ka.md).

## 1. Decision and evidence boundary

**Continue the project as a reproducible research atlas, with a narrower next experiment. Historical novelty of a general theorem, superiority for human reasoning, and a deployable speed advantage are not yet established.** The useful asset is the connection between explicit grammar families, reachable trees, semantic classes, writing costs, representations and reproducible negative results. A collection of individually familiar mechanisms can still support a valuable dataset, a careful comparative study or a new theorem about their interaction.

This audit accounts for all **111 claims** in the existing derivability audit, covering the recorded research through 0052, and adds separate reviews of **0053 and 0054**. Earlier families 0001–0033 are assessed through their consolidated claims, roadmap context and targeted evidence, not a fresh execution of every historical experiment. Every original claim is copied below in its original order, including claims subsequently refuted or qualified. Copying is preservation of the record, not endorsement.

Evidence comes from the project reports, targeted code inspection, primary publications and official technical documentation. The review included the binding-power comparison/representative code and the numeral cost rule. Independently recomputed checks include the 4×4 and 4×5 nested-row matrix counts, the signed ordered-partition formula, percentage denominators and an exact-input floating-point counterexample. **The full 54-family experiment suite, external co-Z benchmark, 0053 timing experiment and 0054's reported 89 tests/10 mutation kills were not rerun for this audit.** Reported measurements remain attributed measurements.

Primary local sources: [original claim register](derivability-audit.md), [README](../README.md), [ROADMAP](../ROADMAP.md), [0050 tiered syntax](../experiments/0050_tiered_syntax/REPORT.en.md), [0051 region geodesy](../experiments/0051_region_geodesy/REPORT.en.md), [0052 binding power](../experiments/0052_binding_power/REPORT.en.md), [0053 metal](../experiments/0053_metal/REPORT.en.md), [0054 numeral worlds](../experiments/0054_numeral_worlds/REPORT.en.md).

### Classification is not a novelty percentage

| Original evidence label, preserved | Claims |
|---|---:|
| DERIVABLE | 46 |
| MEASURED | 48 |
| METHODOLOGICAL | 10 |
| UNCLASSIFIED | 7 |
| Total | 111 |

| Audit disposition | Meaning | Claims |
|---|---|---:|
| K | Established mechanism or directly matched prior art | 10 |
| D | Consequence of the declared model or elementary deduction | 36 |
| E | Scoped empirical result; possible contribution, novelty unconfirmed | 46 |
| H | Open, incomplete or materially qualified hypothesis | 6 |
| R | Refuted, superseded, ill-posed or missing statement | 3 |
| M | Methodological policy or evidence discipline | 10 |

These are dispositions of compound claim rows. **They do not mean “10 known, 46 new.”** A measured row can contain a familiar mechanism; a derived row can contain an interesting application; an elementary proof is not historical evidence that somebody published it before. Conversely, a failed exact-phrase search does not establish priority.

The literature search covered parser/binding-power algorithms, lonesum and poly-Bernoulli enumeration, precedence-aware unparsing, representation and cognition, refinement, symbolic domains, floating-point optimization and benchmarking. Exact combinations including “Pratt lonesum”, “binding power poly-Bernoulli”, “operator precedence Ferrers” and “parser 6902” did not identify a direct matching parsing paper. That is an unresolved attribution question, not a novelty certificate. The 2026 sources below predate this audit; priority relative to ParseAtlas itself still requires dated project records.

## 2. What is established, and what remains valuable

### Parsing and syntax

Pratt's left/right binding powers are established machinery [S01](#s01). The minimum-operator split has the classical Cartesian-tree connection [S06](#s06). Feasibility via acyclic order constraints is established machinery too [S35](#s35). A plausible new theorem would have to isolate **constraints caused by repeated operator labels in a target AST**, minimal obstruction families, or exact recurrences for the number of realizable trees.

Precedence-aware unparsing has prior art [S02](#s02); the abstract alone does not prove ParseAtlas's exact minimum-bracket theorem. That theorem needs the project's grammar and cost contract. Incomplete precedence and refusal of incompatible combinations also have older formal treatment [S30](#s30) and a direct 2026 design account [S31](#s31). Asymmetric binding powers appear in current language-design research [S32](#s32). These sources do not supply ParseAtlas's corpus counts or prove a globally minimum renderer.

0050 makes a useful distinction: a plain stack of syntax layers flattens to scalar precedence, while position-sensitive rules can defeat that flattening. The original T26 “requires layers” statement must be marked refuted as written. The 94-versus-94 totals do not mean equal expressiveness: each family has three exclusive objects on the tested sources. Cyclic Floyd precedence relations [S33](#s33) concern another formalism; they are not a license to satisfy contradictory numerical inequalities.

### Semantic classes and domain contracts

The coefficient-dependent class counts, the difference between AST and semantic diversity, and the newly reached object inventory are useful empirical results. Their strongest defensible form is a **dataset plus specified equivalence procedure**, not “all grammar space behaves this way.” Excluded points, branch conventions and canonicalization determine what equality means [S15](#s15), [S16](#s16).

Domain expansion refines equality only when the extended observations restrict faithfully to the original observations. Merely enlarging a set does not validate an arbitrary changed canonicalization pipeline. Keep mathematical functions, partial domains and implementation keys distinct.

0051's typed decode relation is the right comparison for different encodings, but it belongs to established refinement theory [S18](#s18). Different tuple arities already force raw tuple inequality. The substantive evidence is the 24 decoded tests and six symbolic obligations, with domains and exceptional cases stated. Existing geodesy work already studies accuracy and speed of related formulas [S23](#s23).

### Writing cost, visibility and cognition

The 58-formula corpus gives G0 a bracket cost of 53 versus a best fixed cost of 29, rank 11/25. The relative premium is **(53−29)/29 = 82.7586%**; the saving from 53 to 29 is **45.2830%**. The separate 33-law corpus gives G0 45 versus best 42, rank 3/25. Mixing these corpora produces a false headline. Oracle routing cost 3 versus fixed 29 is an opportunity bound until selection, signaling and switching are priced.

“Manifest” means visible under declared read-off rules. It is not a human observation. The roots/constant-term zero is forced by a root-exclusive rule. The 4:2:1 property vocabulary biases totals; the reported correlation 0.948 is a reason to publish property-wise, family-balanced scores. G0's 34/34 Pareto membership can follow from its own unique bracket minimum. Thirteen frontier writings being nobody's default does not mean they are unexpressible.

Notation affecting reasoning has extensive prior art [S09](#s09), [S10](#s10), [S11](#s11), [S12](#s12). Controlled work relates spatial presentation and brackets to specific tasks [S13](#s13), [S14](#s14). These results do not validate ParseAtlas's proxy automatically. Jones's 2006 precedence study analyzed 17 volunteers and 2,100 repeated answers, 66.7% correct, under a concurrent memory task [S34](#s34). It measures a particular binding task, not a general programming-error rate.

## 3. The important count correction: 6,902, 41,506 and 730

The inspected code uses **M[a,b] = [L_a > R_b]**. Its row supports are nested: increasing L can only add columns. Conversely, any labeled binary matrix with nested row supports can be realized. Order its n rows by inclusion, use **L_i = i+1** for i=1,…,n, and for a column with t leading zeros use **R_j = t+1**. Then L_i > R_j exactly when i > t. Identical rows cause no problem, and every power lies in 1,…,n+1.

These are **lonesum matrices**, equivalently matrices permutable into Ferrers form. Rows and columns remain labeled in the count. Their enumeration is established [S03](#s03), [S04](#s04):

`B(r,c) = Σ(j=0…min(r,c)) (j!)² S(r+1,j+1) S(c+1,j+1)`.

For n=1,2,3,4, the square sequence is **2, 14, 230, 6902**. In the inspected one-prefix extension, the signature is `(M, (L_a > p)_a)`: one extra threshold column. Its n×(n+1) sequence is **4, 46, 1066, 41506**. This assertion is about **one free prefix threshold**, not arbitrary “three-dimensional syntax.”

Why this is a behavioral quotient: in `x op_b y op_a z`, the matrix bit decides between `x op_b (y op_a z)` and `(x op_b y) op_a z`. In `U x op_a y`, the extra bit decides whether U captures the binary expression. Equal signatures make identical power-dependent decisions; distinct bits have these distinguishing words. This assumes the inspected comparison rules, an initial threshold below every left power and unrestricted valid syntax, including repeated operator labels. It establishes AST behavior, not semantic inequality on a restricted corpus.

The flat family is an ordered partition of operator labels with a left/right choice per level. Its count is **Σ 2^k k! S(4,k) = 730**, matching signed ordered-partition/packed-word enumeration [S05](#s05). Thus 6172 and 10.577% are consequences of known counts.

**Independent check performed:** all 65,536 binary 4×4 matrices and all 1,048,576 binary 4×5 matrices were filtered by pairwise row-set comparability, yielding 6,902 and 41,506. This does not rerun the parser; it independently checks the combinatorial class. The code comparison contract supplies the bridge.

Potential value remains in a clear parsing interpretation, finite distinguishing witnesses, reachable-tree structure with repeated labels, and the empirical image **206668/587616** together with **17131 new class occurrences / 12302 distinct objects**. Historical novelty of the exact parsing bridge remains unconfirmed. Permutation/tree and Tamari literature [S07](#s07), [S08](#s08) is relevant context, but does not automatically prove that the project's repeated-label or semantic fibres are intervals or lattice congruences.

## 4. Separate supplement: 0053 execution and 0054 numerals

| Item | Defensible finding | Qualification / disposition |
|---|---|---|
| S53-1 | 16 objects, 34 writings, one Clang 21.1.0 Windows x86 configuration family and one CPU | Small, selected compiler case study; no portability result |
| S53-2 | Mnemonic-multiset agreement in 3/16 at O0, 0/16 at O2, 0/16 at O2 native/FMA, 8/16 at O3 fast | A multiset drops operands, order and dependencies; it is not code identity |
| S53-3 | The 54/64 timing headline was withdrawn; repeats gave 46–51 | Keep withdrawn; nominal win counts are not stable effects |
| S53-4 | Chain/balanced 16-term sum retained a 160–169% O2 gap, versus 0–2% with fast math | Selected robust case; reassociation changes the permitted semantics |
| S54-1 | Finite radix expansion depends on denominator prime factors | Classical arithmetic; a rational terminates iff its reduced denominator divides some power of the base |
| S54-2 | Six informative constants: base2 exact1/6, base10 exact5/6, base30 exact6/6 | Corpus denominators use primes2,3,5; no universally best radix |
| S54-3 | The cost rule assigns zero multiplications to a numeral with one nonzero digit | A modeled primitive, not demonstrated processor cost |
| S54-4 | For value2^50, the implemented chain routine uses exponent50, whose shortest chain has length7 | The known quantity is l(50)=7, not l(2^50)=7 |
| S54-5 | Rounding cannot be attributed only to input literals | Exact-input counterexample below refutes that broad claim |
| S54-6 | Representation conversion can pay off when repeated savings exceed setup/conversion cost | Classical amortization model; complete-path measurement is still required |

0053 reports a timing floor p95 of 2.062% and a worst identical-kernel comparison of 14.398%; QPC measures elapsed time, not processor cycles. Standalone assembly and loop binaries differ. All eight survival cells varied across seven runs. These are reasons to use paired randomized runs, independent process sessions, full binary provenance and uncertainty, consistent with LLVM's distinction between noise and bias [S27](#s27). Strict and fast-math results need separate contracts [S24](#s24), [S29](#s29).

0054's inspected rule in [numeral_worlds.py](../src/parseatlas/numeral_worlds.py) computes `value=2**exponent`, `shortest_addition_chain(exponent)`, and sets multiplication cost to zero whenever the digit vector has one nonzero entry. The display radix alone cannot establish hardware savings: a fixed constant can be precomputed in any radix, and “one nonzero digit” need not mean its coefficient is one. The chain value l(50)=7 is established [S25](#s25); the problem is the backend cost interpretation, not that chain value.

The 14 distinct constants include six informative ones; among 22 occurrences, 16 are 1/2. This strongly weights the corpus. A binary computer can execute exact rational arithmetic [S26](#s26); it does not necessarily round every represented ellipsoid. Separately, with exactly representable binary64 inputs **a=2^53, b=1, c=−2^53**, direct evaluation gives **(a+b)+c=0** and **a+(b+c)=1**. Evaluation rounding exists even when input conversion is exact.

The external co-Z improvements and 5894-candidate negative remain attributed case studies, not reproduced benchmark results. Shared co-Z coordinates already have prior art [S28](#s28). Equality saturation [S17](#s17) is bounded by its language, rewrite set and extraction objective; failure to express an adapter cannot be fixed by increasing beam width.

## 5. Project decisions and the next stage

| Track | Potential now | Evidence needed before a stronger claim |
|---|---|---|
| Reproducible atlas / benchmark dataset | Strongest immediate deliverable | Stable generators, identities, domains, exclusions, manifests and independent reproduction |
| Parsing combinatorics paper | Plausible, narrower than the original headlines | A precise new repeated-label obstruction/count theorem, or a carefully attributed bridge with demonstrably useful consequences |
| Representation optimizer | Unproven practical opportunity | Held-out improvement in complete encode–compute–decode cost under an unchanged contract |
| Cognitive / educational tool | Exploratory | Controlled comprehension and learning results; proxy scores are insufficient |
| General hardware or historical superiority claim | Unsupported | Multiple platforms or appropriate historical evidence; current experiments do not provide either |

**Phase A — establish the publishable baseline.** The manager owns the claim ledger and attribution; workers should make bounded documentation corrections. Correct the known-count attribution, percentage denominator, numeral-cost overclaims, missing T29/T30 and withdrawn timing status. Keep original measurements with scopes. Freeze generator versions, source hashes, input domains, seeds, output identities and counterexamples. Acceptance: every headline points to a specific claim, artifact and applicable domain; no known model consequence is advertised as a measured human or hardware effect.

**Phase B — choose one primary research result.** Prefer the parsing/reachability track first. State an all-length theorem about the actual comparison language and repeated labels; derive minimal obstructions or recurrences and test them with an independently implemented small-case enumerator. Separately test semantic quotients with domain-aware keys on held-out formula families. Acceptance: a precise theorem with proof or a minimized counterexample, reproducible counts, and a documented comparison against the closest prior work. Merely rediscovering acyclic constraint feasibility does not pass.

**Phase C — test practical value under three separate contracts.** Distinguish exact mathematical equivalence, bitwise preservation of a specified binary64 program, and approximation under an error budget. Compare compiler baselines and a disclosed egg configuration where applicable [S17](#s17). Herbie [S19](#s19), Daisy/Herbie [S20](#s20) and performance-aware Herbie work [S21](#s21) belong in the approximation comparison when contracts match; a tighter error bound is not proof that actual worst-case error improved. Include runtime inputs, exceptional cases, encoding/decoding, setup, batch-size amortization and invariant maintenance. Record optimizer time separately. Acceptance: a reproducible full-path benefit with uncertainty, or a measured accuracy–time tradeoff, on held-out families. Portability claims require another compiler and CPU family.

**Phase D — run cognition only as a separate study.** Separate precedence knowledge, legend-assisted comprehension and fully parenthesized controls. Compare minimal versus full parentheses, and blocked versus explicitly cued mixed conventions. Randomize training order, require a stated mastery criterion, measure training time and use fresh coefficients/held-out templates. Balance operator pairs and directions. Avoid an incidental memory task unless it is a separate experimental factor. Use participant/item effects, prespecified primary accuracy and secondary correct-response time, and power planning for a meaningful effect. Acceptance: improved comprehension or learning under declared conditions, with switching/training costs included. It would still not explain historical adoption of arithmetic notation.

Do not expand all tracks simultaneously. The immediate managerial decision is to freeze the corrected baseline and select the parsing theorem/dataset question as the main line; keep execution as a bounded falsification benchmark and cognition as a later independently designed study. No defensible revenue forecast or market size follows from the current research archive.

## 6. Complete source-faithful claim register

The text in “Original claim” is copied verbatim from the original local register. Its original category remains historical metadata. The adjacent audit note is the current judgment. Each source link identifies the exact original line; group-level discussions above supply additional context. K/D/E/H/R/M are defined in §1.

### C001

> **T6.** Parsing depends only on the precedence order restricted to the operators that occur, so the `24` strict grammars partition into blocks of size `24` divided by the factorial of the support, producing byte-identical ASTs.

**Original category:** DERIVABLE · **Audit:** D · [source L55](derivability-audit.md#L55)

Restriction to occurring labels proves the factorial block size; not a historical priority claim.

### C002

> **T7.** The parse tree of every registered grammar is the tree built by splitting at the rightmost occurrence of the minimum-binding-power operator.

**Original category:** DERIVABLE · **Audit:** K · [source L56](derivability-audit.md#L56)

Classical Cartesian-tree mechanism under the registered tie/associativity convention; scope is not every possible parser. [S06](#s06)

### C003

> **T8.** A candidate parenthesization is reachable by some strict precedence grammar exactly when its induced order constraints contain no strict self-loop and no cycle between distinct operator types.

**Original category:** DERIVABLE · **Audit:** K · [source L57](derivability-audit.md#L57)

Generic constraint feasibility is established; a new contribution would need AST-specific repeated-label obstruction results. [S35](#s35)

### C004

> **T9.** Precedence reaches a vanishing fraction of the parenthesization space.

**Original category:** DERIVABLE · **Audit:** D · [source L58](derivability-audit.md#L58)

Finite grammar count divided by a growing Catalan count gives the asymptotic limit.

### C005

> **T9 measured half.** The mean coverage curve falls `0.8750`, `0.6250`, `0.3605`, `0.1735`, `0.0722` for k = `2` to `6`, and `92.159` percent of the `587616` word-and-tree pairs are unreachable.

**Original category:** MEASURED · **Audit:** E · [source L59](derivability-audit.md#L59)

Retain the measured curve for this enumerator; do not transfer its percentages to other word distributions.

### C006

> **T10.** The tied control grammar G0 reaches parse trees that no strict total ordering reaches.

**Original category:** DERIVABLE · **Audit:** D · [source L60](derivability-audit.md#L60)

A concrete tied-precedence witness establishes existence; the population frequency is a separate result.

### C007

> **0046.** G0 reaches a tree no strict grammar reaches on `51296` of `87381` enumerated words, `58.7` percent.

**Original category:** MEASURED · **Audit:** E · [source L61](derivability-audit.md#L61)

51296/87381 is a corpus frequency, not a universal probability of improvement.

### C008

> **T11.** The raw multiset of operations is identical across all `25` grammars.

**Original category:** DERIVABLE · **Audit:** D · [source L62](derivability-audit.md#L62)

Reassociation preserves token occurrences, so the raw operation multiset cannot measure dependency changes.

### C009

> **T5.** Precedence acts through the algebraic core and not on the outer function.

**Original category:** DERIVABLE · **Audit:** D · [source L63](derivability-audit.md#L63)

This follows from the implemented core/outer-function pipeline, not an unrestricted statement about notation.

### C010

> **T13.** Semantic equivalence must be declared over function, domain and undefined set.

**Original category:** DERIVABLE · **Audit:** K · [source L64](derivability-audit.md#L64)

Domain-sensitive equality and excluded points are established symbolic-algebra obligations. [S15](#s15)

### C011

> **T12.** Representation change can turn a variable-dependent expression into a constant, or a quadratic into a linear function, and the collapsed form is a different function rather than a cheaper writing of the same one.

**Original category:** DERIVABLE · **Audit:** D · [source L65](derivability-audit.md#L65)

Changing the parsed function is not a semantics-preserving optimization; label the object change explicitly.

### C012

> **T1.** For a fixed token sequence the `25` grammars do not produce `25` distinct objects; they partition into far fewer classes.

**Original category:** DERIVABLE · **Audit:** D · [source L66](derivability-audit.md#L66)

An upper bound follows from support and tree counts; particular class multiplicities require measurement.

### C013

> **T2.** The class count depends on coefficient values and not only on the syntactic template: one and the same template gave `6` classes for some coefficient triples and `8` for others.

**Original category:** MEASURED · **Audit:** E · [source L67](derivability-audit.md#L67)

The 6-versus-8 witness demonstrates coefficient sensitivity; generalize only after stratified coefficient sampling.

### C014

> **T3.** AST diversity and semantic diversity move independently, so neither may stand in for the other.

**Original category:** MEASURED · **Audit:** E · [source L68](derivability-audit.md#L68)

Non-equivalence of the two diversity measures is useful; 'independently' must not mean statistical independence.

### C015

> **T4.** Expressions separate into grammar-rigid and grammar-sensitive: some token sequences keep all `24` strict grammars in one semantic class and others fragment.

**Original category:** MEASURED · **Audit:** E · [source L69](derivability-audit.md#L69)

Keep rigidity as a corpus classification tied to the declared semantic key and domain.

### C016

> **T14.** Grammar space has no cluster structure beyond the support-forced null model; the excess-matrix clustering coincides exactly with the support blocks over `3125` expressions.

**Original category:** MEASURED · **Audit:** E · [source L70](derivability-audit.md#L70)

The negative clustering finding is bounded by these 3125 expressions, features and null model.

### C017

> **T14a.** AST diversity and semantic diversity are decoupled: `2500` of `3125` expressions hold AST diversity fixed while the class count varies, at rank correlation `0.7676`.

**Original category:** MEASURED · **Audit:** E · [source L71](derivability-audit.md#L71)

2500/3125 and correlation 0.7676 support non-interchangeability, not independence of random variables.

### C018

> **T15.** No transferable structural predictor of grammar sensitivity was found among the `21` features tested.

**Original category:** MEASURED · **Audit:** E · [source L72](derivability-audit.md#L72)

Failure of 21 features is a bounded negative; use held-out template families before claiming transferability.

### C019

> **T16.** Is representation-dependence of difficulty measurable rather than rhetorical?

**Original category:** UNCLASSIFIED · **Audit:** H · [source L73](derivability-audit.md#L73)

A research question, requiring operational definitions and an experiment; no novelty verdict on an answer yet. [S09](#s09), [S10](#s10)

### C020

> **0034.** Minimal parenthesisation is exactly computable: a child needs brackets exactly where the grammar would otherwise reparse it.

**Original category:** DERIVABLE · **Audit:** K · [source L74](derivability-audit.md#L74)

Precedence-aware unparsing is established. Exact minimality still depends on this grammar and bracket cost contract. [S02](#s02)

### C021

> **0034.** Over `58` named formulas G0 pays `53` bracket pairs and ranks `11`th of `25`; the cheapest is G09 at `29`, the dearest G20 at `83`, and the spread is `54`.

**Original category:** MEASURED · **Audit:** E · [source L75](derivability-audit.md#L75)

Keep 58 formulas,53 versus 29 and rank 11. Premium is 82.7586%; saving relative to 53 is 45.2830%.

### C022

> **0034.** Per-formula routing would cost `3` bracket pairs where the best single grammar pays `29`.

**Original category:** MEASURED · **Audit:** E · [source L76](derivability-audit.md#L76)

Oracle routing is an opportunity bound; include selection, signaling and switching before claiming deployable savings.

### C023

> **ROADMAP and 0034.** Under a convention where `+` binds tighter than `*`, factored form is the parenthesis-free default and expanded form becomes the expensive one.

**Original category:** DERIVABLE · **Audit:** D · [source L77](derivability-audit.md#L77)

The reversal is an immediate convention consequence; it does not show better human comprehension. [S09](#s09)

### C024

> **0035.** `a*x*x + b*x + c` denotes exactly `2` objects across the `25` worlds, in `13` worlds and `12` worlds respectively.

**Original category:** DERIVABLE · **Audit:** D · [source L78](derivability-audit.md#L78)

The 13/12 split is a finite operator-order deduction for this template and parameter assumptions.

### C025

> **0035.** In the other `12` worlds the same string is `a*x*(b + x)*(c + x)`, degree `3`, roots `0`, `-b` and `-c`, and free of radicals.

**Original category:** DERIVABLE · **Audit:** D · [source L79](derivability-audit.md#L79)

For generic nondegenerate parameters the factorization gives these roots; handle zero/degenerate coefficients separately.

### C026

> **0036.** The Pythagorean identity written as `s*s + c*c` still denotes `1` in `13` of the `25` worlds.

**Original category:** DERIVABLE · **Audit:** D · [source L80](derivability-audit.md#L80)

Elementary precedence-case counting for this identity; not evidence of universal superiority of 13 worlds.

### C027

> **0036.** Across `8` identities the most are preserved by `3` worlds — G0, G23 and G24 — each holding `8` of `8`, so G0 is among the best and is not uniquely best.

**Original category:** MEASURED · **Audit:** E · [source L81](derivability-audit.md#L81)

Eight selected identities support this local ranking, not optimality over mathematical identities in general.

### C028

> **0036.** In our convention `1 + s/c*s/c` is protected by the tie between `*` and `/` and not by their order, because G17 has G0's order strictly and loses the identity.

**Original category:** DERIVABLE · **Audit:** D · [source L82](derivability-audit.md#L82)

The witness isolates a tie/associativity effect; naming the mechanism is stronger than a novelty claim.

### C029

> **0037.** Over `33` named laws in `4` fields, G0 totals `45` bracket pairs and ranks `3`rd of `25`, is first in algebra and in linear algebra, and is never worse than `6`th; only G18 at `42` and G16 at `44` beat it.

**Original category:** MEASURED · **Audit:** E · [source L83](derivability-audit.md#L83)

This 33-law corpus differs from 0034's 58 formulas; never combine its 45/42 with 53/29.

### C030

> **0037.** Of `15` two-sided laws, `13` reverse their natural direction somewhere, and `22` of the `25` worlds carry at least one reversal, over `152` reversal cells.

**Original category:** MEASURED · **Audit:** E · [source L84](derivability-audit.md#L84)

Direction is defined by the selected syntax-cost measure; it is not human reasoning direction.

### C031

> **0040.** `y - m*x - c` is a straight line in `13` of the `25` worlds and `2` intersecting lines in the other `12`.

**Original category:** DERIVABLE · **Audit:** D · [source L85](derivability-audit.md#L85)

Algebraic expansion under the two parses establishes the geometric split, subject to degeneracies.

### C032

> **0040.** `x*x + y*y - r*r` is a circle in `9` of the `25` worlds.

**Original category:** DERIVABLE · **Audit:** D · [source L86](derivability-audit.md#L86)

The 9/25 count is a finite precedence deduction; a circle also needs the stated real-parameter conditions.

### C033

> **0040.** The remaining classification atlas — an ellipse in `4` worlds, a cubic in `12` of which `8` are a union of `3` lines, and the ellipse form fracturing into `13` objects under `5` classifications.

**Original category:** MEASURED · **Audit:** E · [source L87](derivability-audit.md#L87)

Useful classification dataset; expose assumptions about reducible, degenerate and real versus complex curves.

### C034

> **0040 and 0046.** `(x - y) * (x + y)` denotes one and the same object in all `25` worlds.

**Original category:** DERIVABLE · **Audit:** D · [source L88](derivability-audit.md#L88)

Explicit grouping fixes the tree across these conventions; semantic invariance then follows in the fixed algebra.

### C035

> **0038.** No world makes all the true properties of any multi-property object manifest at once, `0` cells of the `625` that concern those `25` objects.

**Original category:** MEASURED · **Audit:** E · [source L89](derivability-audit.md#L89)

A negative under declared read-off rules; it is not a study of what people can notice or infer. [S10](#s10), [S11](#s11)

### C036

> **0038.** `constant_term` and `roots` are never manifest together, `0` cells of `850`, in both regimes.

**Original category:** MEASURED · **Audit:** D · [source L90](derivability-audit.md#L90)

The root-exclusive visibility rule forces zero. These 850 cells are not 850 independent cognitive observations.

### C037

> **0038.** G0 is joint-first on manifest total at `77` of `850` cells, and the ranking tracks the vocabulary's `4` to `2` to `1` asymmetry at Pearson r of `+0.948`.

**Original category:** MEASURED · **Audit:** E · [source L91](derivability-audit.md#L91)

The 4:2:1 property vocabulary biases the aggregate; publish property-wise and family-balanced scores.

### C038

> **0038.** `factor_structure` is never manifest in `5` worlds — G0, G15, G16, G18 and G24 — while the other `6` properties are manifest in all `25`.

**Original category:** MEASURED · **Audit:** E · [source L92](derivability-audit.md#L92)

'Never' concerns selected default writings and read-off rules; explicit factorization is a different search space.

### C039

> **0039.** The full parenthesization space of `1510820` trees makes exactly `1` of 0038's `46` invisible pairs manifest, and that one is precedence-reachable, so `0` of the `46` require a tree precedence cannot write.

**Original category:** MEASURED · **Audit:** E · [source L93](derivability-audit.md#L93)

A valuable bounded negative over 1510820 trees; excluded forms or other visibility rules could change it.

### C040

> **0041.** For a fixed tree the critical-path depth is identical in all `25` worlds.

**Original category:** DERIVABLE · **Audit:** D · [source L94](derivability-audit.md#L94)

With a fixed tree and latency model, critical-path depth is definitionally independent of its spelling convention.

### C041

> **0041.** The parallelism tax: only `6` of `58` entries move at all, the least-taxing worlds charge `22` and G0 charges `25` for rank `20` of `25` while being `5`th cheapest to write in, and `21` of the tax units are forced by the corpus.

**Original category:** MEASURED · **Audit:** E · [source L95](derivability-audit.md#L95)

The tax ranking is empirical and corpus-dependent; operation count does not substitute for dependency depth. [S22](#s22)

### C042

> **0042.** Restricted to documents a host-convention reader can decode, inline fragment routing delivers exactly `0`, over `54375` cells with `0` counterexamples.

**Original category:** DERIVABLE · **Audit:** D · [source L96](derivability-audit.md#L96)

A zero forced by the host-decodability contract is a model theorem, not failed evidence of all possible routing.

### C043

> **0042.** Model II needs `87` named intermediates to remove at most `7` bracket pairs, and a definition line would have to cost less than `0.3793` of a bracket pair to break even.

**Original category:** MEASURED · **Audit:** E · [source L97](derivability-audit.md#L97)

The break-even price depends on the chosen definition/bracket accounting; reader switching remains unmeasured.

### C044

> **0043.** Under the transparent regime and an unbounded bracket budget the routable task set is `0`.

**Original category:** DERIVABLE · **Audit:** D · [source L98](derivability-audit.md#L98)

Unbounded explicit brackets remove this reachability distinction under transparent decoding.

### C045

> **0043.** At the declared budget of `2`, exactly `6` tasks are unreachable in G0 and reachable elsewhere, each at a bracket premium of `0`.

**Original category:** MEASURED · **Audit:** E · [source L99](derivability-audit.md#L99)

The six wins exist at budget 2; publish sensitivity to budgets and task-family weighting.

### C046

> **0043.** `243` of `300` world pairs are incomparable.

**Original category:** MEASURED · **Audit:** E · [source L100](derivability-audit.md#L100)

243/300 is a partial-order comparison in this atlas; a total ranking would add external preferences.

### C047

> **0044.** Feasibility under a peak-memory ceiling is world-invariant in Generation 1 by construction.

**Original category:** DERIVABLE · **Audit:** D · [source L101](derivability-audit.md#L101)

World invariance follows from retaining the same trees and register model; Sethi-Ullman is prior art. [S22](#s22)

### C048

> **0044.** At ceiling `3` the price is asymmetric: G0 pays `1` extra bracket pair for the ellipse and the hyperbola where `16` worlds get the frugal writing free, while on the circle G0 pays `0` and `20` worlds pay, the maximum of `6` falling on `4` named worlds.

**Original category:** MEASURED · **Audit:** E · [source L102](derivability-audit.md#L102)

Keep the ceiling 3 corpus result; validate against an actual allocator before a hardware memory claim. [S22](#s22)

### C049

> **0045.** Generation 2 is a conservative extension: restricted to the Generation 1 operator set it reproduces the old parser cell by cell over `1294698` cells.

**Original category:** DERIVABLE · **Audit:** D · [source L103](derivability-audit.md#L103)

A design invariant supported by 1294698 checked cells; the general conservative-extension claim needs the parser argument too.

### C050

> **0045.** `a * x^2 + b * x + c` is the conventional quadratic in `21` of the `121` Generation 2 grammars.

**Original category:** DERIVABLE · **Audit:** D · [source L104](derivability-audit.md#L104)

Finite case reasoning for the expanded operator family; keep the tokenization and exponent contract explicit.

### C051

> **0045.** The same string denotes `6` distinct objects across the `121` grammars, and no world that writes the square as `x^2` denotes the radical-free cubic.

**Original category:** MEASURED · **Audit:** E · [source L105](derivability-audit.md#L105)

Six objects and absence of the cubic belong to these 121 grammars and this exponent spelling.

### C052

> **0046.** A bracket-free word is read identically by all `25` worlds if and only if its operator support has size at most `1`, and a bracketed writing if and only if every maximal bracket-free chain uses at most `1` distinct operator.

**Original category:** DERIVABLE · **Audit:** D · [source L106](derivability-audit.md#L106)

An exact AST invariance criterion for this registered family; semantic coincidences can be broader.

### C053

> **0046.** The `4` quantities that cannot move are constant across all `25` worlds on every corpus entry.

**Original category:** DERIVABLE · **Audit:** D · [source L107](derivability-audit.md#L107)

Token-level invariants follow from the fixed input and permitted transformations.

### C054

> **0046.** Not one of the `12` measured quantities is constant across all `25` worlds on every movable corpus entry, over `1500` cells.

**Original category:** MEASURED · **Audit:** E · [source L108](derivability-audit.md#L108)

Non-invariance is established by witnesses in these 1500 cells; no claim about every individual expression follows.

### C055

> **0046.** Writing the `50` corpus writings so that all `25` worlds read them identically costs `147` bracket pairs against the `7` the cheapest world pays and the `47` G0 pays.

**Original category:** MEASURED · **Audit:** E · [source L109](derivability-audit.md#L109)

147 versus 7 versus 47 prices full cross-world invariance on 50 writings, not readability.

### C056

> **0046.** An invariance requirement collapses the per-world writing choice from `16` of `34` objects to `0` of `34`.

**Original category:** DERIVABLE · **Audit:** D · [source L110](derivability-audit.md#L110)

The zero follows from requiring a common invariant tree, within the available writing set.

### C057

> **0046.** Under 0038's transparent regime the manifest loss caused by invariant bracketing is identically `0` on all `50` writings.

**Original category:** DERIVABLE · **Audit:** D · [source L111](derivability-audit.md#L111)

Transparent visibility deliberately ignores these brackets; zero loss is forced by the observation rule.

### C058

> **0048.** Where the declared analysis domain changes the partition at all, it strictly refines and never coarsens: `0` coarsenings and `0` crossings over `42112` sources.

**Original category:** MEASURED · **Audit:** E · [source L112](derivability-audit.md#L112)

Refinement is expected only when larger-domain observations restrict faithfully to the old domain; set growth alone is insufficient. [S15](#s15)

### C059

> **0048.** The rate: the domain changes the partition on `1` of `12` corpus sources and `316` of `40000` swept sources at length `3`, `51` of `57` excluded-set differences are invisible to the partition, and `0` of `300` cells differ in canonical form.

**Original category:** MEASURED · **Audit:** E · [source L113](derivability-audit.md#L113)

Keep the low rates and canonical-form negative with their separate denominators; equality keys need independent checks. [S15](#s15)

### C060

> **0048.** Support `3` is empty at lengths `1` and `2` and first moves at length `3`, with `12` sources of `9790`.

**Original category:** MEASURED · **Audit:** E · [source L114](derivability-audit.md#L114)

Support 3 cannot occur before three operator positions; the 12 moving sources are the empirical part.

### C061

> **0048.** A branch convention can neither split nor merge two distinct readings; the composite partition equals the inner partition under every convention, over `3600` pairs.

**Original category:** DERIVABLE · **Audit:** D · [source L115](derivability-audit.md#L115)

Keeping branch/sheet information makes the map injective by contract; dropping it changes the theorem. [S16](#s16)

### C062

> **0048.** The deficit of `12` between the `172` the axes would give if independent and the `160` observed is exactly what the `5` constant classes force.

**Original category:** DERIVABLE · **Audit:** D · [source L116](derivability-audit.md#L116)

The deficit is explained by forced identifications of constant classes, rather than a new independent axis effect.

### C063

> **0049.** G0's own writing lies on the Pareto frontier for `34` of `34` objects.

**Original category:** MEASURED · **Audit:** E · [source L117](derivability-audit.md#L117)

A unique G 0-priced bracket minimum already guarantees Pareto membership;34/34 does not establish neutral superiority.

### C064

> **0049.** Of the `59` four-axis frontier points, `25` are ones G0 would never write, `12` are another world's natural writing and `13` are written naturally by no world in the atlas.

**Original category:** MEASURED · **Audit:** E · [source L118](derivability-audit.md#L118)

The 59/25/12/13 frontier inventory is useful. No default world writes 13 points naturally, but they remain expressible.

### C065

> **0049.** Adding an axis need not enlarge a frontier.

**Original category:** DERIVABLE · **Audit:** D · [source L119](derivability-audit.md#L119)

An added objective can break ties among previously identical projected cost vectors; state the frontier/tie convention.

### C066

> **0049.** The axis lattice is non-monotone in `26` subset pairs, sharpest at `peak_live` alone giving `475` frontier writings against `43` for `brackets` with `peak_live`.

**Original category:** MEASURED · **Audit:** E · [source L120](derivability-audit.md#L120)

The 26 non-monotone subset pairs are a measurement under that tie convention, not a universal Pareto law.

### C067

> **0049.** At `4` axes a total ranking must invent an order for more than half the landscape: `0.502390` pooled and `0.431728` as a per-object mean.

**Original category:** MEASURED · **Audit:** E · [source L121](derivability-audit.md#L121)

Pooled 0.502390 and mean 0.431728 answer different weighting questions; publish both, without selecting the larger headline.

### C068

> **0050.** A tiered convention that is a plain stack of layers is translated into a flat precedence table by reading each layer's depth as its binding power.

**Original category:** DERIVABLE · **Audit:** D · [source L122](derivability-audit.md#L122)

Plain layer stacks encode scalar precedence; layering alone does not enlarge expressive power. [S01](#s01)

### C069

> **T26.** Juxtaposition and unary minus cannot be captured by a single flat binary precedence and require tiered syntax layers.

**Original category:** DERIVABLE · **Audit:** R · [source L123](derivability-audit.md#L123)

Refuted as stated by 0050's separation of layering from position-sensitive rules; preserve its original category only as history.

### C070

> **0050.** `47951` of `91922` swept conventions have no flat equivalent on the corpus, and not one of them is a stack of layers; what defeats a flat table is a rule applying in one syntactic position and not another.

**Original category:** MEASURED · **Audit:** E · [source L124](derivability-audit.md#L124)

The 47951/91922 non-flat cases depend on the enumerated positional rules and comparison corpus.

### C071

> **0050.** Across `46` corpus sources the tiered space reaches `94` distinct objects and the flat space reaches `94`; exactly `3` objects on `1` source are tiered-only and `3` objects on `2` sources are flat-only.

**Original category:** MEASURED · **Audit:** E · [source L125](derivability-audit.md#L125)

Equal totals 94/94 hide different images; retain the 3-versus 3 exclusive objects and source counts.

### C072

> **0051.** For two encodings of different arity, `F1(x) == F2(x)` is not a question one can ask.

**Original category:** DERIVABLE · **Audit:** K · [source L126](derivability-audit.md#L126)

Raw tuples can be compared and differ, but that is not the appropriate observable-equivalence contract. [S18](#s18)

### C073

> **0051.** Over `24` sampled points the two encodings are equal as tuples at `0` of them while the decode relation holds at `24` of `24`, with `6` of `6` halves discharged symbolically.

**Original category:** MEASURED · **Audit:** E · [source L127](derivability-audit.md#L127)

Different arities force raw tuple inequality;24 decoded tests and 6 symbolic obligations are the substantive checks. [S18](#s18)

### C074

> **0052.** The binding-power pair is the standard Pratt formulation, and associativity is the order within the pair rather than a separate axis.

**Original category:** DERIVABLE · **Audit:** K · [source L128](derivability-audit.md#L128)

Left/right binding powers are classical Pratt machinery; their use is not a new parsing invention. [S01](#s01), [S32](#s32)

### C075

> **0052.** The behavioural quotient is exact and the enumeration saturates: distinct comparison matrix and distinct parser are the same thing, and the parser count stops at `6902` from bound `5` upward.

**Original category:** DERIVABLE · **Audit:** K · [source L129](derivability-audit.md#L129)

6902 is the known labeled 4×4 lonesum count. The parser correspondence is explained in§3, with its exact scope. [S03](#s03), [S04](#s04)

### C076

> **0052.** The pair reaches `206668` of `587616` trees and recovers `29.655` percent of the precedence gap where associativity recovered `11.617` percent.

**Original category:** MEASURED · **Audit:** E · [source L130](derivability-audit.md#L130)

206668/587616 is the enumerated reachability image, distinct from the known number of parsers.

### C077

> **0052.** The whole flat family — every ordering of levels with a side per level — has exactly `730` members.

**Original category:** DERIVABLE · **Audit:** K · [source L131](derivability-audit.md#L131)

730 is the signed ordered-partition count; cite the combinatorial family rather than claiming a new integer. [S05](#s05)

### C078

> **0052.** Those `730` are `10.577` percent of the `6902` parsers a binding-power pair induces, leaving `6172` with no scalar description.

**Original category:** MEASURED · **Audit:** D · [source L132](derivability-audit.md#L132)

6172 and 10.577%are arithmetic from 6902 and 730, not independent empirical discoveries. [S03](#s03), [S05](#s05)

### C079

> **0052.** On the `3125`-expression corpus the pair buys `17131` new class occurrences, `12302` of them distinct as objects, where the associativity widening bought `0`.

**Original category:** MEASURED · **Audit:** E · [source L133](derivability-audit.md#L133)

17131 class occurrences and 12302 distinct objects are promising dataset results, subject to domain-key and held-out validation.

### C080

> **0052.** Every single-operator stratum gains `0` from the second component, in all `3` of them.

**Original category:** DERIVABLE · **Audit:** D · [source L134](derivability-audit.md#L134)

Zero gain applies relative to the stated baseline strata, not to every possible single-operator semantics.

### C081

> **0052.** A partial order never over-refuses: `0` over-refusals in `121410` cells.

**Original category:** DERIVABLE · **Audit:** D · [source L135](derivability-audit.md#L135)

Sound refusal follows from the admitted partial-order contract; incomplete precedence and rejection have prior art. [S30](#s30), [S31](#s31)

### C082

> **0052.** The price of a partial order is `2.407` bracket pairs on average per conventional reading, with `125` of `150` readings needing at least `1` pair and `0` becoming unwritable.

**Original category:** MEASURED · **Audit:** E · [source L136](derivability-audit.md#L136)

2.407 pairs is a corpus rendering cost. Minimum brackets and human readability require separate evidence. [S02](#s02), [S30](#s30)

### C083

> **0052.** Each extra binding-power component buys about `2` more operators of expression length and then meets the same Catalan wall.

**Original category:** DERIVABLE · **Audit:** H · [source L137](derivability-audit.md#L137)

The eventual Catalan limit is derived; 'about two' is a model-specific crossover heuristic, not a uniform theorem.

### C084

> **T17.** The co-Z coordinate change measured minus `34.91` percent on the primitive and minus `7.19` percent and minus `1.96` percent end to end, on one machine, in an external project.

**Original category:** MEASURED · **Audit:** E · [source L138](derivability-audit.md#L138)

External, single-machine measurements not rerun here; primitive and complete-workload percentages are separate cases. Co-Z is established. [S28](#s28)

### C085

> **T17a.** The axis ledger closes at `2` axes confirmed, `5` refuted and `1` open, with each refutation given a mechanism rather than a silence.

**Original category:** MEASURED · **Audit:** E · [source L139](derivability-audit.md#L139)

An internal ledger of these tests; confirmed/refuted labels inherit each test's model and scope.

### C086

> **T17b.** Searching within a fixed representation found no improvement distinguishable from `0` over `5894` candidates, while changing the representation delivered roughly `35` percent.

**Original category:** MEASURED · **Audit:** E · [source L140](derivability-audit.md#L140)

5894 failures bound this search language and objective; they do not establish optimality of the representation. [S17](#s17)

### C087

> **T18.** Some transformation classes yield speedups far more often than others, so the probability of a speedup given a transformation label is estimable per label.

**Original category:** UNCLASSIFIED · **Audit:** H · [source L141](derivability-audit.md#L141)

Estimating transformation success needs a prespecified workload distribution and unbiased candidate selection.

### C088

> **T19.** A cost model built on operation count alone cannot express the difference a grammar makes.

**Original category:** DERIVABLE · **Audit:** D · [source L142](derivability-audit.md#L142)

True for the fixed operation-multiset grammar model; representation-changing algorithms may alter counts.

### C089

> **T19 hypothesis half.** Dependency depth and register pressure predict measured speedup better than operation-count delta does.

**Original category:** UNCLASSIFIED · **Audit:** H · [source L143](derivability-audit.md#L143)

Open predictive hypothesis; compare out-of-sample models and include compiler/backend features.

### C090

> **T19a.** The hottest kernel is `228` instructions of which `31` are multiplies and `98` are data movement, so the cost model counts instructions for a kernel that is not instruction-bound.

**Original category:** MEASURED · **Audit:** E · [source L144](derivability-audit.md#L144)

228/31/98 is an instruction inventory. It cannot by itself establish whether execution is instruction-bound. [S27](#s27)

### C091

> **T20.** The rediscovery gate: could this project independently rediscover the co-Z rewrite?

**Original category:** UNCLASSIFIED · **Audit:** R · [source L145](derivability-audit.md#L145)

Ill-posed until the allowed language, adapters, observations and target rewrite are specified. [S17](#s17)

### C092

> **T20a.** The co-Z form is unreachable by that search by construction, at any depth and any beam width.

**Original category:** DERIVABLE · **Audit:** D · [source L146](derivability-audit.md#L146)

Unreachability follows from an excluded representation construct; beam width cannot repair the language. [S17](#s17)

### C093

> **T20b.** The distance to co-Z is `1` substitution on the inputs, verified over `270` cases with `396` of `396` raw-value matches after deleting the dead prefix.

**Original category:** MEASURED · **Audit:** E · [source L147](derivability-audit.md#L147)

The 270 cases/396 matches verify these substitutions; they do not prove all-domain or floating-point equivalence.

### C094

> **T20c.** The completeness of a representation search and its blindness to representation change are the same property.

**Original category:** DERIVABLE · **Audit:** D · [source L148](derivability-audit.md#L148)

Completeness is relative to a search language; the broad rhetorical equivalence needs this qualification. [S17](#s17)

### C095

> **T22.** Equivalence must generalise beyond value equality to a decode relation.

**Original category:** DERIVABLE · **Audit:** K · [source L149](derivability-audit.md#L149)

Decode relations and representation invariants are established data-refinement machinery. [S18](#s18)

### C096

> **Owner's third standard.** Algebraic equivalence does not imply numerical equivalence, so every result about equivalent writings carries an unstated assumption that the reader evaluates exactly.

**Original category:** DERIVABLE · **Audit:** K · [source L150](derivability-audit.md#L150)

Algebraic equality differs from floating-point program equality; exact arithmetic must be explicitly scoped. [S19](#s19), [S29](#s29)

### C097

> **T31.** Reachability outranks cost, and cost is used only to break ties among the worlds that can do the job at all.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L151](derivability-audit.md#L151)

An objective policy, not a discovered natural law; disclose the task predicate before applying it.

### C098

> **T31 supporting half.** The factor-blind worlds have mean cost rank `4.20` against the sighted worlds' `15.05` and bracket totals of `46.80` against `75.15`, which is `60.6` percent more brackets.

**Original category:** MEASURED · **Audit:** E · [source L152](derivability-audit.md#L152)

Ranks and 60.6%premium inherit the chosen visibility vocabulary and corpus; no cognitive benefit follows.

### C099

> **T32.** Cost does not determine parallelism; the rank correlation is `0.167418` under one tie-break and `0.422211` under the other, and the modelling choice is open.

**Original category:** MEASURED · **Audit:** E · [source L153](derivability-audit.md#L153)

The two correlations expose tie-break sensitivity; predictive or causal claims remain open.

### C100

> **T33.** The numeral axis is a third representation axis, and it moves a different ranking from the other two.

**Original category:** UNCLASSIFIED · **Audit:** H · [source L154](derivability-audit.md#L154)

The original row predates 0054's completed report; retain that history and use the separate numeral supplement. [S25](#s25), [S26](#s26)

### C101

> **T17c, T21.** The benchmark harness properties and the `3` test classes that ordinary correctness testing does not provide.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L155](derivability-audit.md#L155)

Good benchmark requirements; compliance must be evidenced per harness rather than inferred from a checklist. [S27](#s27)

### C102

> **T17d.** A systematic representation search surfaced a soundness bug an audit module had passed through, and the relevance is methodological rather than cryptographic.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L156](derivability-audit.md#L156)

A useful testing lesson; the external bug claim needs its own reproducible provenance.

### C103

> **T23, T24.** Selection is the hard half of an engine, and the two acceptance gates are rediscovery and then generalisation.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L157](derivability-audit.md#L157)

Rediscovery and held-out generalization are sensible gates; both need frozen tasks and baselines.

### C104

> **0047.** An enumeration is a claim about what exists, so every restriction on it must be declared where the answer is read and not defended in prose elsewhere.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L158](derivability-audit.md#L158)

Enumeration scope is part of the result; archive generator, exclusions, version and deduplication policy.

### C105

> **ROADMAP.** Every decisive gate needs a test that can fire, and a test that a gate holds is not a test of the gate.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L159](derivability-audit.md#L159)

Mutation or adversarial witnesses must demonstrate that a decisive gate can fail.

### C106

> **ROADMAP.** Let the system find the wall: sweep any parameter that could have been a threshold and publish the curve, looking explicitly for non-monotonicity.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L160](derivability-audit.md#L160)

Threshold sweeps and non-monotonicity checks are methods, not novelty evidence by themselves.

### C107

> **ROADMAP.** Measure the emitted flow and not the translation; a notation cost includes everything a reader pays and a computation cost excludes compilation.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L161](derivability-audit.md#L161)

Separate optimizer/compilation cost from runtime, but include setup and conversions in the deployment total. [S27](#s27)

### C108

> **ROADMAP.** A structure invisible in the representations we searched is not thereby absent, so every negative result is reported with its scope.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L162](derivability-audit.md#L162)

Preserve the declared search scope for every negative result; absence in the atlas is not general impossibility.

### C109

> **0051.** 0033's Region model is a model of rational-function regions: `2` of its `5` parts were reused unchanged and `3` refused this pair by construction.

**Original category:** METHODOLOGICAL · **Audit:** M · [source L163](derivability-audit.md#L163)

The 2/5 reuse and 3 refusals are architecture boundary evidence, not universal failure of region optimization. [S18](#s18)

### C110

> **T29 and T30.** T30 is cited in ROADMAP.md as the source of "50 percent more syntax with zero new mathematics", and neither T29 nor T30 is stated anywhere in the file.

**Original category:** UNCLASSIFIED · **Audit:** R · [source L164](derivability-audit.md#L164)

Missing T 29/T 30 is a document-traceability defect; it is not an unresolved mathematical theorem.

### C111

> **T25, T27, T28.** Generation 2 dynamics, cognitive cost governed by parse-stack depth, and non-commutative algebras inverting classical precedence invariants.

**Original category:** UNCLASSIFIED · **Audit:** H · [source L165](derivability-audit.md#L165)

This composite row contains separate unfinished projects; split dynamics, human cognition and noncommutative algebra before testing. [S10](#s10), [S13](#s13)

## 7. Sources and access limits

Sources were checked during the 2026-09-05 audit. Some publisher records, abstracts and indexed primary text were accessible while direct full text was restricted; those limits are identified below. Descriptive labels are used where a page title is not reproduced. No exhaustive search or historical priority guarantee is claimed.

<a id="s01"></a>

**S01.** [Vaughan R. Pratt (1973), Top Down Operator Precedence](https://tdop.github.io/). Primary paper transcription; binding powers.

<a id="s02"></a>

**S02.** [Norman Ramsey (1998), Unparsing Expressions with Prefix and Postfix Operators](https://www.cs.tufts.edu/~nr/pubs/unparse-abstract.html). Author abstract checked; no exact global-minimality theorem attributed from it.

<a id="s03"></a>

**S03.** [Chad Brewbaker (2008), A Combinatorial Interpretation of the Poly-Bernoulli Numbers and Two Fermat Analogues](https://math.colgate.edu/~integers/i2/i2.pdf). Primary paper, Theorem 2 and formula 2; lonesum enumeration.

<a id="s04"></a>

**S04.** [Donald E. Knuth (2024, revised August25), Parades and Poly-Bernoulli Bijections](https://www-cs-faculty.stanford.edu/~knuth/papers/poly-Bernoulli.pdf). Author paper; general formula and count table.

<a id="s05"></a>

**S05.** [Jean-Christophe Novelli and Jean-Yves Thibon (2009), Superization and (q,t)-specialization in Combinatorial Hopf Algebras](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v16i2r21/pdf/). Primary paper, §7.1, equation 158; signed packed-word enumeration, not a parser paper.

<a id="s06"></a>

**S06.** [Luc Devroye (1994), On Random Cartesian Trees](https://luc.devroye.org/devroye_1994_on_random_cartesian_trees.pdf). Primary paper on the classical structure; credits Vuillemin.

<a id="s07"></a>

**S07.** [Jean-Louis Loday (2004; preprint2002), Realization of the Stasheff Polytope](https://arxiv.org/abs/math/0212126). Permutation/tree context; not a theorem about ParseAtlas semantic fibres.

<a id="s08"></a>

**S08.** [Nathan Reading (2006; preprint2004), Cambrian Lattices](https://arxiv.org/abs/math/0402086). Relevant lattice framework; project applicability requires proof.

<a id="s09"></a>

**S09.** [Kenneth E. Iverson (1980), Notation as a Tool of Thought](https://www.sigapl.org/Articles/Notation%20as%20a%20Tool%20of%20Thought_a1979-iverson.pdf). Primary account of notation and reasoning.

<a id="s10"></a>

**S10.** [Thomas R. G. Green and Alan F. Blackwell (1998), Cognitive Dimensions of Information Artefacts](https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf). Author tutorial; dimensions of notation usability.

<a id="s11"></a>

**S11.** [Jiajie Zhang and Donald A. Norman (1994), Representations in Distributed Cognitive Tasks](https://onlinelibrary.wiley.com/doi/abs/10.1207/s15516709cog1801_3). Publisher abstract; distributed representations.

<a id="s12"></a>

**S12.** [Jiajie Zhang (1997), The Nature of External Representations in Problem Solving](https://doi.org/10.1207/s15516709cog2102_3). Primary publication record; external representations.

<a id="s13"></a>

**S13.** [David Landy and Robert L. Goldstone (2007), How Abstract Is Symbolic Thought?](https://doi.org/10.1037/0278-7393.33.4.720). Experimental primary source on spatial arrangement and algebra.

<a id="s14"></a>

**S14.** [Ngo et al. (2023), bracket and arithmetic-precedence study](https://jnc.psychopen.eu/index.php/jnc/article/view/9535). 528 students, six conditions; task-specific bracket effects, not general faster comprehension.

<a id="s15"></a>

**S15.** [SymPy documentation, solveset.domain_check](https://docs.sympy.org/latest/modules/solvers/solveset.html#sympy.solvers.solveset.domain_check). Official documentation; excluded points can be lost by simplification.

<a id="s16"></a>

**S16.** [NIST Digital Library of Mathematical Functions, §4.2](https://dlmf.nist.gov/4.2). Official reference; logarithms, branches and principal values.

<a id="s17"></a>

**S17.** [Max Willsey et al. (2021), egg: Fast and Extensible Equality Saturation](https://homes.cs.washington.edu/~cnandi/docs/popl21-cr.pdf). Primary paper; equality saturation and extraction.

<a id="s18"></a>

**S18.** [Banerjee et al. (2019–2022), A Relational Program Logic with Data Abstraction and Dynamic Framing](https://arxiv.org/abs/1910.14560). Primary work; relational contracts and representation invariants.

<a id="s19"></a>

**S19.** [Pavel Panchekha et al. (2015), Automatically Improving Accuracy for Floating Point Expressions (Herbie)](https://herbie.uwplse.org/pldi15-paper.pdf). Primary paper; accuracy-oriented expression transformation.

<a id="s20"></a>

**S20.** [Heiko Becker et al. (2018), Combining Tools for Optimization and Verification of Floating-Point Computations](https://homes.cs.washington.edu/~ztatlock/pubs/fpbench-becker-fm18.pdf). Primary Daisy/Herbie paper; verified bounds versus measured errors.

<a id="s21"></a>

**S21.** [Performance-aware Herbie / Pherbie (ARITH2021)](https://ztatlock.net/pubs/2021-arith-herbie/). Author publication page; speed/accuracy tradeoffs.

<a id="s22"></a>

**S22.** [Ravi Sethi and Jeffrey D. Ullman (1970), The Generation of Optimal Code for Arithmetic Expressions](https://doi.org/10.1145/321607.321620). Publisher abstract; full-text retrieval restricted. Classical register scheduling attribution only.

<a id="s23"></a>

**S23.** [Sten J. Claessens (2019), Efficient Transformation from Cartesian to Geodetic Coordinates](https://espace.curtin.edu.au/handle/20.500.11937/76507). Institutional primary publication record; related geodesy comparisons.

<a id="s24"></a>

**S24.** [Clang Users Manual, -ffast-math](https://clang.llvm.org/docs/UsersManual.html#cmdoption-ffast-math). Official documentation of enabled floating-point assumptions.

<a id="s25"></a>

**S25.** [OEIS A003313, length of shortest addition chain](https://oeis.org/A003313). Sequence data checked at index 50:7; exponent 50, not exponent 2^50.

<a id="s26"></a>

**S26.** [Python documentation, fractions — Rational numbers](https://docs.python.org/3/library/fractions.html). Official exact-rational implementation documentation.

<a id="s27"></a>

**S27.** [LLVM, Benchmarking tips](https://llvm.org/docs/Benchmarking.html). Official guidance distinguishing noise from bias.

<a id="s28"></a>

**S28.** [Goundar, Joye and Miyaji (2010), Co-Z Addition Formulae and Binary Ladders on Elliptic Curves](https://eprint.iacr.org/2010/309.pdf). Primary paper; shared-coordinate formulas.

<a id="s29"></a>

**S29.** [LLVM Language Reference, Floating-Point Semantics](https://llvm.org/docs/LangRef.html#floating-point-semantics). Official contract for floating-point transformations.

<a id="s30"></a>

**S30.** [Nils Anders Danielsson and Ulf Norell, Parsing Mixfix Operators (IFL2008; revised proceedings2011)](https://www.cse.chalmers.se/~nad/publications/danielsson-norell-mixfix.pdf). Indexed primary-paper text, Table 1; direct PDF returned 403. Incomplete precedence and refusal.

<a id="s31"></a>

**S31.** [Alastair Reid (Intel, 29June2026), Designing language syntax for readability](https://intellabs.github.io/isa-tools/2026/06/29/designing-syntax-for-readability.html). Primary practitioner account; partial precedence, not a controlled human study.

<a id="s32"></a>

**S32.** [Cheng and Parreaux (ECOOP, 25 June 2026), A Simple Recipe for Writing Decent Recursive Descent Parsers](https://drops.dagstuhl.de/storage/00lipics/lipics-vol372-ecoop2026/LIPIcs.ECOOP.2026.30/LIPIcs.ECOOP.2026.30.pdf). Primary paper §2.3; asymmetric powers. Syntax diagrams differ from minimum expression rendering.

<a id="s33"></a>

**S33.** [Chiari, Mandrioli and Pradella (2023), Cyclic Operator Precedence Grammars](https://arxiv.org/pdf/2309.04200). Primary paper; Floyd equality cycles, not contradictory numeric precedence.

<a id="s34"></a>

**S34.** [Derek M. Jones (4August2006), developer operator-precedence experiment](https://www.open-std.org/jtc1/sc22/wg23/docs/ISO-IECJTC1-SC22-WG23_N0036-parenart.pdf). Primary study §§5–8; use document date, not recent search-index metadata.

<a id="s35"></a>

**S35.** [Lecture Notes SPM, §6.1, p.149 — precedence functions](https://art.torvergata.it/retrieve/e291c0d4-b8ca-cddb-e053-3a05fe0aa144/LectureNotesSPM.pdf). Indexed primary lecture text; full retrieval unavailable. Acyclic constraint graph/longest paths; not sole support for a new theorem.

## 8. Audit provenance and remaining corrections

This is the manager-authored research assessment. The earlier worker candidate was rejected for invented claim mapping; it was not accepted into the canonical tree. The worker task was returned for rework. This report preserves all original statements and adds judgments; it does not silently rewrite historical reports or certify their complete reproduction. Source-report corrections are tracked separately (NF-2026-00010 through NF-2026-00015 include attribution, numeral interpretation, percentage, workflow and source-fidelity findings).

- derivability-audit.md SHA-256: `3ea05caa12345744d0332f336e7f819bf9844a8a81421eb2aef490684db428ab`
- derivability-audit.ka.md SHA-256: `a8fc463fba890144f23eb2fe8f6210ffe6b3754c67fd1fc092f8328cfe71008a`
