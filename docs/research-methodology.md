# ParseAtlas Research Methodology

## Purpose

ParseAtlas studies how a fixed symbolic token sequence behaves when interpreted under explicitly varied expression grammars. The research object is the pair:

```text
(token sequence, grammar)
```

A result therefore describes an interpretation under a specified grammar. It must not be presented as a correction to conventional arithmetic or as evidence that unrelated expressions are mathematically equivalent.

## Terminology

- **Token sequence**: the source symbols supplied to the experiment.
- **Grammar**: the complete interpretation rule set, including precedence, associativity, operators, and parenthesis behavior.
- **Control grammar (`G0`)**: the conventional arithmetic grammar used as a comparison baseline.
- **Strict grammar (`G01`-`G24`)**: one of the 24 total orderings of `+`, `-`, `*`, and `/`.
- **AST**: the parser-produced abstract syntax tree before symbolic simplification.
- **Canonical form**: a normalized symbolic representation produced from the AST under a declared symbolic-analysis policy.
- **Semantic equivalence**: agreement of function, domain, and undefined or singularity information under the declared analysis contract.
- **Representation collapse**: a measured reduction in distinct AST or semantic forms; it is not automatically a general law.

## Experimental Pipeline

Every experiment follows this pipeline:

```text
token sequence
    -> grammar registry
    -> custom tokenizer
    -> grammar-specific AST
    -> symbolic conversion
    -> canonical form
    -> domain and singularity analysis
    -> equivalence classes
    -> structural and cost metrics
    -> report
```

The parser must construct the AST before symbolic conversion. A general-purpose symbolic library must not parse the raw source string because that would silently substitute its own precedence rules for the grammar under study.

## Required Experiment Record

Each grammar result should retain:

- experiment identifier
- source token sequence
- grammar identifier
- precedence levels
- associativity policy
- serialized AST
- canonical expression
- analysis domain
- undefined values or singularity conditions
- equivalence-class identifier
- raw operation cost
- canonical operation cost
- software version and execution date

## Semantic Contract

For grammar interpretations `Gi` and `Gj`, define equivalence only when:

```text
Gi ~ Gj iff Fi = Fj, Di = Dj, and Ui = Uj
```

where `F` is the represented function, `D` is the declared domain, and `U` is the undefined or singularity set within that domain.

Canonical string equality is an implementation aid, not a sufficient proof. For example, `x/x` can simplify textually to `1` while remaining undefined at `x = 0`. Domain restrictions must survive canonicalization.

For complex-valued experiments, branch conventions must be recorded for logarithms, roots, inverse trigonometric functions, and any other multivalued operation.

## Evidence Levels

Reports must label claims using the following levels:

1. **Observed**: directly produced by a recorded execution.
2. **Symbolically justified**: supported by an explicit rewrite, identity, or proof.
3. **Numerically validated**: checked at declared sample points without singularities.
4. **Hypothesized**: proposed as a pattern requiring broader testing.
5. **Benchmarked**: supported by a documented performance measurement and environment.

A result must not be promoted from observation to invariant without testing a controlled expression family and stating the failure conditions that were checked.

## Reproducibility Protocol

A report is reproducible when another researcher can:

1. obtain the repository at a known revision;
2. install the declared dependencies in an isolated environment;
3. identify the exact source token sequence;
4. identify the grammar registry and analysis domain;
5. run the documented command;
6. regenerate the serialized result and report;
7. compare class membership and metadata, not only a screenshot or prose summary.

When symbolic-library output may vary between versions, the report must record the library version and should compare structured metadata or semantic checks rather than relying only on printed expression text.

## Baseline Gates

The Generation 1 baseline is complete only when:

- `G0` and all 24 strict grammars are registered with stable identifiers;
- the parser handles binary `+`, `-`, `*`, `/` and parentheses deterministically;
- the initial expression reproduces the documented strict `24 -> 8` grouping;
- domain restrictions are retained through simplification;
- JSON and Markdown reports can be regenerated;
- tests distinguish parser behavior, canonicalization, and report grouping.

## Interpretation Discipline

The initial affine experiment is a calibration case, not a universal theorem. Later experiments should include controlled linear, polynomial, rational, and nested-function families. For each family, record the input-generation constraints and report distributions such as:

```text
number of grammars -> number of AST forms -> number of semantic classes
```

Invariant mining should follow:

```text
generate -> measure -> cluster -> detect repeated relations -> conjecture -> prove or falsify
```

Performance claims should remain separate from semantic claims. Measure parsing, symbolic processing, and canonical evaluation independently.
