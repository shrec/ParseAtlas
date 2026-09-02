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

## Structural theory

- [Structure of the Generation 1 precedence space](grammar-space-structure.md): the consolidated structural results with their prior art, and an explicit statement of which are restatements, which are trivial, and which are measurements.

## Case studies

Case studies record the **equivalence-preserving** mode, where `R1(x) == R2(x)` on the declared domain but the representations cost differently. Experiments record the **semantic-exploration** mode, where a different grammar yields a different function. The two are never mixed.

- [Case study index and the two-mode distinction](../case_studies/README.md)
- [Record schema and admission gate](../case_studies/RECORD_SCHEMA.md)
- [UltrafastSecp256k1 intake](../case_studies/ultrafast_secp256k1/README.md)

## Reading order

For an external reader, the shortest honest path through this repository is:

1. [README.md](../README.md) for the research object and the two modes;
2. the **Working Theses** section of [ROADMAP.md](../ROADMAP.md), which states what each result is worth and names the prior art — several striking-looking results are marked there as folklore, tautology, or trivial-by-counting;
3. [grammar-space-structure.md](grammar-space-structure.md) for the structural picture in one place;
4. the individual experiment reports for the measurements.

Experiment reports are written in Georgian for project communication; the methodology, structural theory, publication, and case-study documents are in English. That split is deliberate and is recorded in ROADMAP Phase 13.

The normative Generation 1 language and semantic rules are defined in [SPEC.md](../SPEC.md). The project overview remains in [README.md](../README.md).
