# ParseAtlas

**Exploring mathematical behavior across alternative expression grammars and representations.**

ParseAtlas is an experimental mathematics and computational research project.

The starting question is simple:

> What changes when the same symbolic token sequence is interpreted under different operator-precedence rules?

The project begins with the four basic binary arithmetic operators:

```text
+  -  *  /
```

There are:

```text
4! = 24
```

strict total precedence orderings.

Instead of treating one precedence convention as mathematically privileged, ParseAtlas treats precedence as a **representation / grammar parameter**.

For a fixed token sequence `E`, we study the family:

```text
E(G1), E(G2), ..., E(G24)
```

where each `Gi` is one of the 24 precedence permutations.

---

## Important distinction

Changing precedence does **not** preserve the semantic meaning of an unparenthesized expression.

For example:

```text
2*x + 3
```

under the conventional rule

```text
* > +
```

means:

```text
(2*x) + 3
```

while under:

```text
+ > *
```

it may mean:

```text
2 * (x + 3)
```

These are different mathematical functions.

This is intentional.

ParseAtlas does not claim that these expressions are equivalent.

The research object is:

```text
(token sequence, grammar)
```

rather than the token sequence alone.

---

# Core research question

Given one symbolic token sequence, what mathematical structures appear when its grammar is varied?

We are interested in:

- resulting ASTs
- canonical simplified forms
- equivalence classes between grammars
- roots
- polynomial degree
- extrema
- domains
- singularities
- periods and frequencies
- symmetries
- invariants across representations
- computational complexity
- operation counts
- dependency depth
- algebraic collapse
- representation-specific simplifications

The long-term question is whether some representations expose structures or computationally cheap forms that remain hidden under the conventional representation.

---

# Initial precedence space

The initial experiment uses all 24 permutations of:

```text
+ - * /
```

Example:

```text
+ > - > * > /
+ > - > / > *
+ > * > - > /
...
/ > * > - > +
```

For the initial research phase:

- all four operators are binary
- explicit `*` is preferred
- associativity at equal precedence is left-to-right
- parentheses override precedence
- precedence order is global for an experiment
- standard precedence is included only as one baseline
- symbolic simplification is performed only after parsing
- domains are explicitly recorded (`R`, `C`, finite field, etc.)

These rules must remain explicit in every experiment.

---

# First experiment

The initial token sequence was:

```text
2*t + 1 - t/2
```

It was evaluated under all 24 precedence permutations.

After symbolic simplification, the 24 parses collapsed into only 8 unique canonical forms:

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
8 semantic equivalence classes
```

This immediately exposed two phenomena.

## 1. Representation equivalence

Different precedence grammars can produce the same final mathematical function.

Define:

```text
Gi ~ Gj
```

when:

```text
canonical(E(Gi)) = canonical(E(Gj))
```

The 24-state precedence space can therefore be partitioned into equivalence classes.

## 2. Computational collapse

Some parses simplify dramatically.

For example, a token sequence containing a variable may collapse to:

```text
1
```

and therefore:

```text
sin(E(t)) -> sin(1)
```

The variable disappears entirely.

This changes the computational problem from evaluating a function for every `t` to evaluating one constant once.

---

# Initial function families

The same inner token sequence has been examined under several outer functions.

## Sine

```text
sin(E(t))
```

Different grammars changed:

- effective frequency
- phase
- constant vs oscillating behavior

## Cosine

```text
cos(E(t))
```

showed the same grammar-induced changes in frequency and phase.

## Tangent

```text
tan(E(t))
```

additionally changed:

- pole locations
- singularity density
- intervals of continuity

Some representations removed all variable-dependent singularities by collapsing the argument to a constant.

## Exponential

```text
exp(E(t))
```

changed the effective exponential growth rate.

## Logarithm

```text
log(E(t))
```

changed the domain boundary.

## Square root

```text
sqrt(E(t))
```

changed where the real-valued function begins to exist.

## Reciprocal

```text
1 / E(t)
```

changed pole positions or removed them entirely.

---

# Polynomial experiment

A quadratic-like token sequence was also evaluated across the 24 precedence grammars.

The important observation was that changing grammar could alter:

- coefficients
- roots
- discriminant
- vertex
- number of real roots
- and even polynomial degree

A token sequence that represents a quadratic under one grammar may simplify to a linear function under another.

This is a central research target:

```text
representation change
        ↓
structural change
        ↓
possible computational collapse
```

---

# What ParseAtlas is NOT

ParseAtlas is not an attempt to replace conventional mathematical notation.

It is not claiming that conventional precedence is incorrect.

It is not treating arbitrary alternative parses as equivalent solutions to the same already-defined equation.

It is not numerology.

The project studies a precisely defined mathematical object:

```text
Expression Token Sequence × Grammar
```

and measures how mathematical properties vary over that space.

---

# Research model

For an expression `E` and grammar `G`:

```text
parse(E, G) -> AST
AST -> canonical symbolic form
canonical form -> mathematical properties
canonical form -> computational cost model
```

A basic experiment should record:

```text
token_string
grammar
AST
canonical_expression
equivalence_class
domain
roots
singularities
degree
operation_count
dependency_depth
notes
```

---

# Invariants

One of the main research goals is to find quantities that remain unchanged while grammar changes.

For a property `I`, search for:

```text
I(E(G1)) = I(E(G2)) = ... = I(E(Gn))
```

Possible invariant candidates include:

- common roots
- root relations
- symmetry classes
- conserved combinations of coefficients
- topology of domains
- relationships between singularities
- equivalence-class structure
- transformation relations between solutions
- computational-complexity classes

Do not assume in advance what the invariant should be.

Measure first.

---

# Representation cost

Two grammars producing equivalent canonical expressions may still differ before simplification.

Therefore ParseAtlas distinguishes:

```text
raw parse cost
symbolic simplification cost
canonical evaluation cost
```

For computational experiments, possible metrics include:

```text
number of additions
number of subtractions
number of multiplications
number of divisions
number of transcendental operations
dependency depth
temporary values
memory traffic
register pressure
```

For low-level domains these costs may be weighted differently.

---

# Cryptographic / finite-field extension

A later research branch will test the same general idea on finite-field and elliptic-curve arithmetic, including secp256k1.

This branch has a stricter requirement.

Alternative representations are allowed only when the final mathematical result is provably identical:

```text
F1(x) ≡ F2(x) mod p
```

or when projective coordinates represent the same elliptic-curve point.

In cryptographic code, semantic reinterpretation that changes the result is not an optimization.

The research target there is:

```text
same mathematical result
+
different valid representation
+
lower computational cost
```

Possible search dimensions include:

- associativity
- factorization
- distributivity
- sign placement
- projective scaling
- coordinate systems
- modulus-specific identities
- reduction strategy
- addition chains
- field representation
- operation scheduling

---

# Research discipline

Every result should distinguish between:

1. observed behavior
2. symbolic proof
3. numerical validation
4. performance hypothesis
5. measured benchmark result

Do not convert an interesting coincidence into a claimed law.

Do not assume a pattern discovered on one token sequence generalizes.

Generate data, classify it, then search for laws.

---

# Initial roadmap

## Phase 1 — 24 precedence permutations

Generate a large corpus of expressions and classify their semantic equivalence classes.

## Phase 2 — Precedence + associativity

Expand the grammar space.

## Phase 3 — General parenthesization / AST space

Compare precedence-generated trees against the wider parse-tree space.

## Phase 4 — Functions and equations

Study roots, domains, singularities, periods, extrema and invariants.

## Phase 5 — Computational complexity

Search for representation-induced simplification and collapse.

## Phase 6 — Finite fields / secp256k1

Search only among provably equivalent representations and benchmark real implementations.

---

# Guiding principle

> **Do not optimize the current representation before asking whether a different valid representation makes the problem disappear.**

A mathematical problem may appear difficult not only because of the problem itself, but because of the representation in which it is expressed.

ParseAtlas investigates the space of alternative representations instead of assuming the historically standard one is optimal for every problem.
