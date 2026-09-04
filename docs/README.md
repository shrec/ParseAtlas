# ParseAtlas Documentation

This directory contains the publication-facing documentation for ParseAtlas.

## Documents

- [Research methodology](research-methodology.md): experimental protocol, evidence levels, and reproducibility requirements.
- [Publication outline](publication-outline.md): a proposed structure for a future research paper.
- [Experiment 0001 report](../experiments/0001_affine_functions/REPORT.md): the first executable result.
- [Experiment 0002 report](../experiments/0002_outer_function_atlas/REPORT.md): outer-function behavior, periods, and domain metadata.
- [Experiment 0003 report](../experiments/0003_quadratic_properties/REPORT.md): degree, roots, discriminant, vertex, and critical-point analysis.
- [Experiment 0004 report](../experiments/0004_controlled_corpus/REPORT.md): controlled linear, polynomial, and rational corpus distributions.
- [Experiment 0005 report](../experiments/0005_coefficient_sweep/REPORT.md): deterministic coefficient sweep and class-count distribution.
- [Experiment 0006 report](../experiments/0006_mathematical_domains/REPORT.md): quadratic equations, geometry, algebra, calculus, and related mathematical domains.
- [Experiment 0007 report](../experiments/0007_specialized_domain_analyzers/REPORT.md): specialized symbolic analyzers for the first mathematical domains.
- [Experiment 0008 report](../experiments/0008_ode_probability/REPORT.md): exponential differential equations and binomial probability moments.
- [Experiment 0009 report](../experiments/0009_continuous_probability_calculus/REPORT.md): continuous distributions and extended calculus properties.
- [Experiment 0010 report](../experiments/0010_geometry_algebra/REPORT.md): geometric transformations, vector angles, and algebraic identity residuals.
- [Experiment 0011 report](../experiments/0011_advanced_ode_statistics/REPORT.md): nonlinear/second-order ODE checks and statistical inference primitives.
- [Experiment 0012 report](../experiments/0012_numerical_validation/REPORT.md): numerical cross-checks of symbolic canonicalization.
- [Experiment 0013 report](../experiments/0013_cost_benchmark/REPORT.md): separate parsing and symbolic-processing cost measurements.
- [Experiment 0014 report](../experiments/0014_cross_family_invariants/REPORT.md): cross-family cost comparison and symbolic identity mining.
- [Experiment 0015 report](../experiments/0015_domain_aware_invariant_mining/REPORT.md): domain-aware identity validation and counterexamples.
- [Experiment 0016 report](../experiments/0016_multivariable_complex_conjectures/REPORT.md): multivariable derivatives, complex identities, and conjecture evidence.
- [Experiment 0017 report](../experiments/0017_grammar_equivalence_matrix/REPORT.md): grammar-space agreement matrix and representation sensitivity.
- [Experiment 0018 report](../experiments/0018_precedence_graph/REPORT.md): adjacent-swap precedence graph and semantic transitions.
- [Experiment 0019 report](../experiments/0019_operator_support_reduction/REPORT.md): operator-support reduction and the exact redundancy of grammar enumeration.
- [Experiment 0020 report](../experiments/0020_ast_space_coverage/REPORT.md): precedence-reachable fraction of the parenthesization space, and the non-redundancy of the tied control grammar.
- [Experiment 0021 report](../experiments/0021_critical_path_cost/REPORT.md): invariant raw operation multiset versus variable critical-path depth.
- [Experiment 0022 report](../experiments/0022_modular_collapse/REPORT.md): domain-dependent equivalence, grammar classes over Q versus modulo p.
- [Experiment 0023 report](../experiments/0023_reachability_theorem/REPORT.md): order-feasibility characterization of precedence-reachable parse trees.
- [Experiment 0024 report](../experiments/0024_corpus_grammar_clusters/REPORT.md): corpus-scale agreement matrix against the support-reduction null model — a measured negative result on grammar-space cluster structure, and the AST/semantic decoupling that survives it.
- [Experiment 0025 report](../experiments/0025_independent_oracle_crossvalidation/REPORT.md): cross-validation against an independent implementation with a different equivalence oracle, and the 38-case asymmetry showing domain tracking is load-bearing.
- [Experiment 0026 report](../experiments/0026_transformation_axes/REPORT.md): equivalence-preserving transformation axes across eight mathematical domains — measured negative transfer from the field-arithmetic result.

## Structural theory

- [Structure of the Generation 1 precedence space](grammar-space-structure.md): the consolidated structural results with their prior art, and an explicit statement of which are restatements, which are trivial, and which are measurements.

## Case studies

Case studies record the **equivalence-preserving** mode, where `R1(x) == R2(x)` on the declared domain but the representations cost differently. Experiments record the **semantic-exploration** mode, where a different grammar yields a different function. The two are never mixed.

- [Case study index and the two-mode distinction](../case_studies/README.md)
- [Record schema and admission gate](../case_studies/RECORD_SCHEMA.md)
- [UltrafastSecp256k1 intake](../case_studies/ultrafast_secp256k1/README.md)

## Direction A and Direction B — the distinction that organises everything here

```text
Direction A   fixed token string        ->  what does it MEAN under each grammar?     0001-0033
Direction B   fixed mathematical object ->  what does it COST to WRITE there?         0034 onward
```

Only Direction B answers the founding question. Direction A built the instruments — parser, grammar registry, domain-aware equivalence, null model, reachability, associativity — and its results are sound, but it asks what a *string* becomes rather than what *mathematics* costs. **New work belongs in Direction B unless there is a stated reason otherwise.**

- Experiment 0034 — [English](../experiments/0034_notational_cost/REPORT.en.md) · [ქართული](../experiments/0034_notational_cost/REPORT.md): the notational cost of 58 named formulas — conventional `G0` ranks 11th of 25, 45.3% dearer than the cheapest, and per-formula routing would cost 3 brackets against a single convention's 29.
- Experiment 0035 — [English](../experiments/0035_alternative_mathematics/REPORT.en.md) · [ქართული](../experiments/0035_alternative_mathematics/REPORT.md): the standard objects in each world — `a*x*x + b*x + c` is our quadratic in 13 worlds and a factored cubic with roots `0, −b, −c` in the other 12.
- Experiment 0036 — [English](../experiments/0036_trigonometry_worlds/REPORT.en.md) · [ქართული](../experiments/0036_trigonometry_worlds/REPORT.md): sine and the trigonometric identities — the Pythagorean identity survives in exactly the 13 worlds where `*` precedes `+`, and `G0` is top-three across eight identities.
- Experiment 0037 — [English](../experiments/0037_domain_worlds/REPORT.en.md) · [ქართული](../experiments/0037_domain_worlds/REPORT.md): the compromise test over 33 named laws in four fields — `G0` is **3rd of 25** on the summed workload, 1st in algebra and linear algebra, never worse than 6th; only `G16` and `G18` beat it, and `G18` is our own grouping with the `+`/`-` tie broken. Also: 13 of 15 two-sided laws reverse their natural direction somewhere, and 22 of the 25 worlds reverse at least one.
- Experiment 0038 — [English](../experiments/0038_manifest_properties/REPORT.en.md) · [ქართული](../experiments/0038_manifest_properties/REPORT.md): what a writing lets you *read off* versus what is merely true — of the 25 corpus objects with more than one true property, **no world makes them all manifest at once**, and the constant term and the roots are never co-manifest in 850 cells despite nothing in the rules forbidding it. `G0` ties `G17` for the most manifest properties overall.
- Experiment 0039 — [English](../experiments/0039_visibility_ceiling/REPORT.en.md) · [ქართული](../experiments/0039_visibility_ceiling/REPORT.md): what it would take to see the 46 invisible pairs. Opening the **full** parenthesization space — 1,510,820 trees — recovers exactly one, and that one is precedence-reachable, so **0 of the 46 are blocked by precedence**; 8 need a language with radicals and `i`, and 37 are the shape rules themselves.
- Experiment 0040 — [English](../experiments/0040_geometry_atlas/REPORT.en.md) · [ქართული](../experiments/0040_geometry_atlas/REPORT.ka.md): the geometry atlas. **In 12 of the 25 worlds the standard written form of a straight line is not a line** but a degenerate conic carrying an `x*y` term. The circle splits four ways, the ellipse fractures into 13 distinct objects, and exactly one curve is invariant across all 25 — because it is already factored. Twelve generated SVG figures, regenerable byte-identically.

Direction A's later instrument work, kept because Direction B depends on it:

- [Experiment 0033 report](../experiments/0033_region_model/REPORT.md): the Region model and the decode obligation, for transformations that change the input encoding.
- [Experiment 0027 findings](../experiments/0027_rediscovery_feasibility/FINDINGS.md): why a search complete under one set of rewrite rules is blind to representation change.

## Reading order

For an external reader, the shortest honest path through this repository is:

1. [README.md](../README.md) — **the founding question first**, then the Direction A / Direction B split. Skipping this is how a reader ends up extending the finished direction;
2. the **Working Theses** section of [ROADMAP.md](../ROADMAP.md), which states what each result is worth and names the prior art — several striking-looking results are marked there as folklore, tautology, or trivial-by-counting — followed by the standing caveat that every negative result carries the scope of the representation it was measured in;
3. the Direction B reports above (0034 onward) for what the founding question has actually produced — 0035 for what the standard objects become, 0037 for how good the convention we inherited actually is, 0038 for the visibility trade it forces;
4. [grammar-space-structure.md](grammar-space-structure.md) for the Direction A structural picture in one place;
5. the individual experiment reports for the measurements.

## Language

**Every document here exists in both English and Georgian, and both are normative** — see [DOCUMENTATION_POLICY.md](DOCUMENTATION_POLICY.md) / [DOCUMENTATION_POLICY.ka.md](DOCUMENTATION_POLICY.ka.md). In force from 2026-09-04.

This replaces the earlier split, which kept methodology in English and experiment reports in Georgian. That split let each language fall behind the other and eventually disagree with it; requiring both at write time is cheaper than reconciling two drifted documents later.

```text
docs/X.md                            English
docs/X.ka.md                         ქართული
experiments/NNNN_name/REPORT.en.md   English
experiments/NNNN_name/REPORT.ka.md   ქართული
```

Experiments 0001–0039 still carry `REPORT.md` in Georgian and keep that name until their English counterparts exist; a single migration then renames them to `REPORT.ka.md`. Experiment 0040 was the first created after the rule came into force and is already in the new shape. Technical terms stay in Latin script inside Georgian text, so that a Georgian reader can search for the same word the code uses.

## Cross-experiment documents

- [The quadratic in 25 conventions](quadratic-in-25-conventions.en.md) · [კვადრატული განტოლება 25 კონვენციაში](quadratic-in-25-conventions.ka.md) — what the standard quadratic string denotes in each world, what the fixed problem costs to write, what each writing lets you read off, and how good the inherited convention actually is. Written for a mathematician from outside the project; draws on 0035, 0037, 0038 and 0039.

The normative Generation 1 language and semantic rules are defined in [SPEC.md](../SPEC.md). The project overview remains in [README.md](../README.md).
