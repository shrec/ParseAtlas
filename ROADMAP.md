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

