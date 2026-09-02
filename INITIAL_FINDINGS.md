# ParseAtlas — Initial Experimental Findings

This document records the first exploratory results that motivated the ParseAtlas project.

The purpose is to preserve the exact starting point of the research so that future contributors and AI models can reproduce the experiments, distinguish observations from hypotheses, and continue from the same baseline.

---

# 1. Experimental Setup

The first experiments used the four binary arithmetic operators:

```text
+  -  *  /
```

All strict precedence orderings were considered.

Because there are four distinct operators:

```text
4! = 24
```

there are 24 precedence grammars.

The precedence order is written from highest to lowest.

The 24 grammars are:

```text
 1. + > - > * > /
 2. + > - > / > *
 3. + > * > - > /
 4. + > * > / > -
 5. + > / > - > *
 6. + > / > * > -

 7. - > + > * > /
 8. - > + > / > *
 9. - > * > + > /
10. - > * > / > +
11. - > / > + > *
12. - > / > * > +

13. * > + > - > /
14. * > + > / > -
15. * > - > + > /
16. * > - > / > +
17. * > / > + > -
18. * > / > - > +

19. / > + > - > *
20. / > + > * > -
21. / > - > + > *
22. / > - > * > +
23. / > * > + > -
24. / > * > - > +
```

For these initial experiments:

- operators are binary
- equal-precedence associativity is left-to-right
- explicit parentheses override precedence
- symbolic simplification is performed only after parsing
- changing precedence is allowed to change semantic meaning
- the research object is `(token sequence, grammar)`

---

# 2. First Token Sequence

The first token sequence was:

```text
2*t + 1 - t/2
```

The same token sequence was parsed under all 24 precedence grammars.

After symbolic simplification, the 24 parses collapsed into only 8 unique canonical expressions.

## 2.1 Canonical forms

```text
1
t/2 + 1
3*t/2 + 2
t + 2
t/2 + 1/2
3*t/2 + 1/2
t + 1
3*t/2 + 1
```

Therefore:

```text
24 grammar states
        ↓
8 unique canonical expressions
```

This was the first observed example of **representation equivalence**.

---

# 3. Equivalence Classes for the First Expression

The exact grouping was:

| Precedence IDs | Canonical expression |
|---|---|
| 1, 2, 7, 8 | `1` |
| 3 | `t/2 + 1` |
| 4, 6, 20 | `3*t/2 + 2` |
| 5, 19, 21 | `t + 2` |
| 9, 13, 15 | `t/2 + 1/2` |
| 10, 12, 16 | `3*t/2 + 1/2` |
| 11 | `t + 1` |
| 14, 17, 18, 22, 23, 24 | `3*t/2 + 1` |

This motivates the relation:

```text
Gi ~ Gj
```

when:

```text
canonical(E(Gi)) = canonical(E(Gj))
```

The 24 precedence states therefore form semantic equivalence classes for a fixed token sequence.

Important:

> The observed number `8` is not assumed to be universal.

It is only the result for this particular expression structure.

---

# 4. Computational Collapse

The most dramatic class was:

```text
1, 2, 7, 8
```

which simplified to:

```text
1
```

A variable-dependent token sequence therefore became a constant.

For example:

```text
sin(2*t + 1 - t/2)
```

under those grammars becomes:

```text
sin(1)
```

The variable `t` disappears entirely.

This is an example of **computational collapse**:

```text
variable-dependent computation
        ↓
constant
```

In a repeated-evaluation setting, a constant can be computed once instead of for every input value.

This observation motivated the distinction between:

```text
raw parse cost
symbolic simplification cost
canonical evaluation cost
```

---

# 5. Sine Experiment

The outer function was:

```text
y = sin(E(t))
```

where:

```text
E(t) = 2*t + 1 - t/2
```

was interpreted under all 24 precedence grammars.

Because the 24 inner parses collapsed to 8 affine canonical forms, the sine family became:

```text
sin(1)
sin(t/2 + 1)
sin(3*t/2 + 2)
sin(t + 2)
sin(t/2 + 1/2)
sin(3*t/2 + 1/2)
sin(t + 1)
sin(3*t/2 + 1)
```

## Observed effects

The representation changed:

- whether the result was constant or oscillating
- effective frequency
- phase
- period
- computational cost of the inner expression

The effective coefficient of `t` was restricted to:

```text
a ∈ { 0, 1/2, 1, 3/2 }
```

for canonical forms of:

```text
a*t + b
```

For:

```text
sin(a*t + b)
```

the period is:

```text
T = 2*pi / |a|
```

when `a != 0`.

Therefore the non-constant cases included periods:

```text
a = 1/2  ->  T = 4*pi
a = 1    ->  T = 2*pi
a = 3/2  ->  T = 4*pi/3
```

When:

```text
a = 0
```

the function became constant:

```text
sin(1)
```

---

# 6. Cosine Experiment

The same inner expression was wrapped with:

```text
y = cos(E(t))
```

The same 8 canonical arguments appeared.

Therefore the main grammar-induced effects were again:

- constant versus oscillating behavior
- frequency
- phase
- period

The periods followed:

```text
T = 2*pi / |a|
```

for:

```text
cos(a*t + b)
```

The grammar class:

```text
1, 2, 7, 8
```

again collapsed to:

```text
cos(1)
```

which is constant.

This showed that the computational collapse belonged to the inner grammar structure, not specifically to `sin`.

---

# 7. Tangent Experiment

The outer function was:

```text
y = tan(E(t))
```

The same 8 canonical arguments appeared.

For:

```text
tan(a*t + b)
```

the period is:

```text
T = pi / |a|
```

and poles occur where:

```text
a*t + b = pi/2 + k*pi
```

therefore:

```text
t = (pi/2 + k*pi - b) / a
```

for non-zero `a`.

## Observed effects

Changing grammar changed:

- tangent period
- phase
- pole locations
- singularity density
- intervals of continuity

For the constant-collapse grammars:

```text
E(t) -> 1
```

therefore:

```text
tan(E(t)) -> tan(1)
```

The variable-dependent pole structure disappears completely.

This was an important observation:

> A change in representation can change not only the shape of a graph, but also the location or existence of singularities.

---

# 8. Exponential Experiment

The outer function was:

```text
y = exp(E(t))
```

The canonical family included:

```text
exp(1)
exp(t/2 + 1)
exp(3*t/2 + 2)
exp(t + 2)
exp(t/2 + 1/2)
exp(3*t/2 + 1/2)
exp(t + 1)
exp(3*t/2 + 1)
```

The effective coefficient:

```text
a ∈ { 0, 1/2, 1, 3/2 }
```

became the effective growth-rate coefficient.

Observed behavior:

```text
a = 0     -> constant
a = 1/2   -> slower exponential growth
a = 1     -> baseline exponential growth
a = 3/2   -> faster exponential growth
```

Again, grammars 1, 2, 7, and 8 produced:

```text
exp(1)
```

---

# 9. Logarithm Experiment

The outer function was:

```text
y = log(E(t))
```

Here the representation changed the **domain boundary**.

For real-valued logarithms:

```text
E(t) > 0
```

Examples:

```text
log(t/2 + 1)
```

requires:

```text
t > -2
```

while:

```text
log(t + 1)
```

requires:

```text
t > -1
```

and:

```text
log(3*t/2 + 1/2)
```

requires:

```text
t > -1/3
```

The constant-collapse grammars give:

```text
log(1) = 0
```

which is defined for every `t` because the variable has disappeared.

Important observation:

> Grammar variation can alter the domain of the resulting real-valued function.

---

# 10. Square-Root Experiment

The outer function was:

```text
y = sqrt(E(t))
```

For real-valued square roots:

```text
E(t) >= 0
```

Examples:

```text
sqrt(t + 2)
```

requires:

```text
t >= -2
```

while:

```text
sqrt(3*t/2 + 1/2)
```

requires:

```text
t >= -1/3
```

and the constant-collapse grammars produce:

```text
sqrt(1) = 1
```

for every `t`.

Observed effect:

> Different grammars changed where the real-valued function begins to exist.

---

# 11. Reciprocal Experiment

The outer function was:

```text
y = 1 / E(t)
```

Representation changed the position of poles.

Examples:

```text
1 / (t + 2)
```

has a pole at:

```text
t = -2
```

while:

```text
1 / (t + 1)
```

has a pole at:

```text
t = -1
```

and:

```text
1 / (3*t/2 + 1/2)
```

has a pole at:

```text
t = -1/3
```

The constant-collapse grammars produce:

```text
1 / 1 = 1
```

and therefore remove variable-dependent singularities.

---

# 12. Absolute-Value Experiment

The outer function was:

```text
y = abs(E(t))
```

For affine forms:

```text
abs(a*t + b)
```

the vertex occurs where:

```text
a*t + b = 0
```

therefore:

```text
t = -b/a
```

when `a != 0`.

Different grammar states therefore moved the vertex.

The constant-collapse grammars produced:

```text
abs(1) = 1
```

which is a horizontal line.

---

# 13. Shared Structure Across Function Families

The first set of experiments revealed an important separation:

```text
precedence grammar
        ↓
inner canonical form
        ↓
outer function converts that form into domain-specific behavior
```

For the initial token sequence, precedence produced affine forms:

```text
a*t + b
```

with:

```text
a ∈ { 0, 1/2, 1, 3/2 }
```

The outer function then translated changes in `a` and `b` into different observable properties.

| Outer function | Grammar-induced property changes |
|---|---|
| `sin(a*t+b)` | frequency, phase, period, constant collapse |
| `cos(a*t+b)` | frequency, phase, period, constant collapse |
| `tan(a*t+b)` | frequency, phase, poles, singularity density |
| `exp(a*t+b)` | growth rate |
| `log(a*t+b)` | domain boundary |
| `sqrt(a*t+b)` | domain boundary |
| `1/(a*t+b)` | pole location |
| `abs(a*t+b)` | vertex location |
| `(a*t+b)^2` | parabola location and scaling |

This suggests a useful research decomposition:

```text
grammar layer
→ canonical algebra layer
→ function-family behavior layer
```

---

# 14. Polynomial / Parabola Experiment

A second token sequence was chosen so that the conventional grammar produced a quadratic:

```text
2*x*x + 1 - x/2
```

Under the 24 precedence grammars, this expression again collapsed to 8 unique canonical functions.

## Canonical forms and grammar classes

| Precedence IDs | Canonical function |
|---|---|
| 1, 2, 7, 8 | `x` |
| 3 | `x*(x + 1/2)` |
| 4, 6, 20 | `x*(4*x + 3)/2` |
| 5, 19, 21 | `x*(x + 2)` |
| 9, 13, 15 | `x^2 - x/2 + 1/2` |
| 10, 12, 16 | `2*x^2 - x/2 + 1/2` |
| 11 | `x*(x + 1)` |
| 14, 17, 18, 22, 23, 24 | `2*x^2 - x/2 + 1` |

Again:

```text
24 grammar states
        ↓
8 canonical functions
```

This repeated `24 -> 8` observation is interesting but must not be treated as a universal law.

Both test expressions have related token/operator structure, so broader experiments are required.

---

# 15. Polynomial Roots

For:

```text
y = 0
```

the canonical forms produced different solution sets.

## Real-root cases

```text
x
```

has:

```text
x = 0
```

---

```text
x*(x + 1/2)
```

has:

```text
x = 0
x = -1/2
```

---

```text
x*(4*x + 3)/2
```

has:

```text
x = 0
x = -3/4
```

---

```text
x*(x + 2)
```

has:

```text
x = 0
x = -2
```

---

```text
x*(x + 1)
```

has:

```text
x = 0
x = -1
```

## No-real-root cases

```text
x^2 - x/2 + 1/2
```

has discriminant:

```text
-7/4
```

and therefore no real roots.

---

```text
2*x^2 - x/2 + 1/2
```

has discriminant:

```text
-15/4
```

and therefore no real roots.

---

```text
2*x^2 - x/2 + 1
```

has discriminant:

```text
-31/4
```

and therefore no real roots.

---

# 16. Polynomial Structural Changes

The same token sequence produced:

- a linear function
- several different quadratics
- different root sets
- different discriminants
- different vertices
- different numbers of real roots

The most dramatic collapse was:

```text
2*x*x + 1 - x/2
        ↓
x
```

under precedence grammars:

```text
1, 2, 7, 8
```

Thus the polynomial degree changed from:

```text
2
```

to:

```text
1
```

This is stronger than ordinary operation-count reduction.

It is a **structural collapse**.

---

# 17. Real-Root Split in the Polynomial Experiment

For the 24 precedence states:

```text
12
```

produced at least one real root, while:

```text
12
```

produced no real root.

Among the representations with real roots, `x = 0` was always present.

This is an observed property of this particular token sequence.

It is not yet claimed as a general invariant.

---

# 18. Representation Equivalence

The experiments introduced two distinct concepts.

## 18.1 Grammar equivalence for a fixed token sequence

Two grammars are equivalent when they produce the same canonical function:

```text
Gi ~ Gj
```

if:

```text
canonical(E(Gi)) = canonical(E(Gj))
```

## 18.2 Structural equivalence across function families

If several grammars collapse the inner expression to the same form, then any deterministic unary outer function preserves that grouping.

For example:

```text
E(G1) = E(G2) = E(G7) = E(G8) = 1
```

therefore for any unary function `F`:

```text
F(E(G1)) = F(E(G2)) = F(E(G7)) = F(E(G8)) = F(1)
```

This is not a sine-specific phenomenon.

It is a grammar-induced equivalence class.

---

# 19. Candidate Invariant Directions

The first experiments suggest several categories worth testing.

These are **research targets**, not established laws.

## Candidate directions

- roots shared by several grammar states
- repeated equivalence-class sizes
- stable coefficient sets
- stable effective slopes `a`
- relationships among phase shifts `b`
- transitions caused by adjacent precedence swaps
- common domain boundaries
- conserved symmetry types
- common singularity structures
- degree preservation or collapse classes
- cost-class invariants
- fixed points under grammar transformations

A future invariant miner should measure these automatically.

---

# 20. Computational Cost Findings

The initial experiments showed that representation can change computational cost in several qualitatively different ways.

## 20.1 Constant collapse

Example:

```text
E(t) -> 1
```

then:

```text
sin(E(t)) -> sin(1)
```

Repeated evaluation no longer depends on `t`.

## 20.2 Degree collapse

Example:

```text
quadratic token sequence
        ↓
linear canonical form
```

This can eliminate multiplication and reduce solving complexity.

## 20.3 Domain simplification

A function such as:

```text
log(a*t+b)
```

may have a restricted real domain, while another grammar collapses the argument to:

```text
1
```

and removes the domain boundary.

## 20.4 Singularity removal

A reciprocal or tangent form can contain variable-dependent poles under one grammar and become constant under another.

---

# 21. Important Interpretation Rule

These experiments do **not** mean that all precedence interpretations are equivalent solutions to one already-defined equation.

They are not.

For an unparenthesized token sequence:

```text
E
```

the complete research object is:

```text
(E, G)
```

where:

```text
G = grammar / precedence system
```

Changing `G` may change the mathematical function itself.

This semantic variation is intentional in the exploratory branch of ParseAtlas.

---

# 22. Difference From Equivalence-Preserving Optimization

ParseAtlas will later have a separate research mode for optimization.

In that mode:

```text
different representation
```

is useful only if:

```text
same mathematical result
```

is preserved.

This is especially important for:

- finite fields
- cryptography
- numerical kernels
- secp256k1
- exact symbolic computation

For example:

```text
F1(x) ≡ F2(x) mod p
```

must be proved or strongly validated before a finite-field rewrite is considered an optimization.

The exploratory precedence experiments and equivalence-preserving optimization experiments must remain clearly separated.

---

# 23. Main Initial Findings

The first ParseAtlas experiments currently support the following observations.

## Observation A

Operator precedence is not only an evaluation-order convention.

For an unparenthesized expression it participates in defining the AST and therefore the mathematical object.

## Observation B

One token sequence can produce a family of mathematical functions when grammar is varied.

## Observation C

Different precedence grammars can collapse to the same canonical function.

## Observation D

Representation changes can alter:

- roots
- degree
- period
- frequency
- phase
- domain
- singularities
- pole locations
- growth rate
- computational cost

## Observation E

Some representations can cause dramatic computational collapse:

```text
variable -> constant
quadratic -> linear
singular function -> constant
```

## Observation F

The useful search space is not only:

```text
find a better algorithm for the current expression
```

but also:

```text
find a representation in which the mathematical structure is simpler
```

---

# 24. Open Questions

The initial experiments raise the following questions.

1. How many unique canonical functions are typically produced by 24 precedence states?

2. What properties of the token sequence determine the number and size of equivalence classes?

3. Are some precedence permutations repeatedly equivalent across broad expression families?

4. Can the 24-state precedence space be decomposed into stable structural classes?

5. Which mathematical quantities remain invariant across grammar changes?

6. Can grammar transitions be modeled as a graph with predictable local effects?

7. How often does representation produce computational collapse?

8. Can representation search automatically discover cheaper exact formulations?

9. How much additional structure appears when associativity is also varied?

10. What is gained by moving from precedence permutations to the full parenthesization / AST space?

11. Do similar representation effects exist in finite fields?

12. Can equivalent-representation search produce measurable improvements in real cryptographic primitives?

---

# 25. Reproducibility Requirement

Future experiments should preserve:

```text
token string
all grammar definitions
AST for every grammar
canonical form
equivalence class
domain
roots
singularities
cost metrics
plots
code version
```

Every reported result should be labeled as one of:

```text
OBSERVED
PROVEN
NUMERICALLY_VALIDATED
HYPOTHESIS
BENCHMARKED
FALSIFIED
```

The initial results in this document should be treated primarily as:

```text
OBSERVED
```

with exact symbolic simplification where explicitly shown.

---

# 26. Starting Research Principle

> **Do not assume the historically standard representation is optimal for every mathematical or computational problem.**

The first experiments demonstrate that changing representation can expose:

- different mathematical structure
- different equivalence classes
- different domains
- different singularities
- different roots
- and sometimes dramatically simpler computation

ParseAtlas exists to turn that observation into a systematic, reproducible research program.
