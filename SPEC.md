# ParseAtlas Experimental Specification

This document defines the first executable research contract for ParseAtlas.

## Research Object

The primary object is the pair:

```text
(token sequence, grammar)
```

A grammar is part of the interpretation. Changing a grammar is allowed to change the mathematical function represented by an otherwise identical token sequence.

## Scope: Generation 1

- Operators are binary: `+`, `-`, `*`, `/`.
- Unary operators, including unary minus, are out of scope.
- Implicit multiplication is out of scope; multiplication must use `*`.
- Parentheses may be used and override precedence.
- Equal-precedence operators associate left-to-right.
- One precedence grammar applies globally to an expression.
- Symbolic simplification happens only after parsing.
- Exact rational constants are preferred over floating-point constants.

## Grammar Registry

`G0` is the conventional control grammar:

```text
* and / share the higher precedence level
+ and - share the lower precedence level
both levels associate left-to-right
```

`G01` through `G24` are the strict precedence permutations of the four operators. Their IDs are stable and use the ordering listed in [INITIAL_FINDINGS.md](INITIAL_FINDINGS.md).

The strict permutation space is an experimental representation space, not a claim that conventional arithmetic is incorrect. The control grammar is included separately so every result can be compared with the conventional interpretation.

## Parsing and Results

For expression `E` and grammar `G`:

```text
parse(E, G) -> AST
AST -> canonical symbolic form
canonical form -> domain-aware properties and cost metrics
```

Every result must retain:

- source token string
- grammar ID and precedence levels
- reproducible AST
- canonical expression
- domain
- undefined or singularity set
- equivalence-class ID
- raw and canonical cost metrics

## Domain and Undefined Values

The initial default analysis domain is the real numbers, with exact rational constants. Division by zero is undefined. Simplification must not silently erase restrictions from the original expression.

For example, `x/x` may simplify to `1` only together with the restriction `x != 0`; it is not automatically equivalent to the unrestricted constant function `1`.

Future complex-valued analysis must record branch conventions for functions such as `log`, roots, and inverse trigonometric functions.

## Semantic Equivalence

Two grammar interpretations are semantically equivalent only when their analyzed functions and validity information agree over the declared analysis contract:

```text
Gi ~ Gj iff Fi = Fj, Di = Dj, and Ui = Uj
```

where:

- `Fi` is the function represented by the canonical expression
- `Di` is its declared domain
- `Ui` is its undefined/singularity set within that domain

Canonical text equality alone is not sufficient. If branch conventions or additional semantic metadata are active, those must also agree.

## Evidence Discipline

Each result must distinguish:

1. observed output
2. symbolic proof or rewrite justification
3. numerical validation
4. performance hypothesis
5. measured benchmark result

The first executable gate is reproduction of the documented `24 -> 8` result and exact equivalence-class membership for `2*t + 1 - t/2`. New generalizations require new measurements.
