# Concepts

[Home](README.md) · [ქართული](Concepts.ka.md)

Source links: [Generation `1` specification](../../SPEC.md); [historical structural theory](../grammar-space-structure.md).

## Short glossary

- **Grammar**: the interpretation rules applied to a token sequence.
- **Precedence**: grouping, not evaluation order; it decides which binary operator groups its operands more tightly when parentheses do not decide.
- **Syntactic associativity**: the grouping rule for equal-precedence chains; Generation `1` uses left-to-right grouping. This differs from algebraic associativity such as `(a+b)+c = a+(b+c)`.
- **Parse / AST**: `parse(E, G) -> AST`; the tree is the reproducible object before simplification.
- **Domain**: the explicitly chosen set of inputs for comparison. Definedness must be tracked separately within that set: `x/x` is undefined at `0`, so replacing it with `1` must preserve that restriction.
- **Equivalence**: analyzed writings agree on contract-required values, definedness, and applicable branch or observable metadata, not on every possible metadata field.
- **Cost model**: a declaration of counts, representation, and included overheads, such as parenthesis count and parse-tree depth; it is not a machine-speed benchmark.

## Two directions

Direction A is **fixed string / changing grammar**: keep the token string and vary the grammar. For `a+b*c`, the conventional choice groups as `a+(b*c)` because `*` binds above `+`. A different precedence can group the same string as `(a+b)*c`. This illustrates grouping only; it is not a measured corpus result.

Direction B is **fixed object / equivalent writings**. In a parenthesis-rendering task, the target AST is fixed and the writing changes. Broader representation studies may instead fix a function under an explicit equivalence contract.

## Limits

Generation `1` concerns binary `+`, `-`, `*`, `/`, explicit `*`, parentheses, global precedence, and post-parse simplification. It does not forbid later syntax in future generations. Domain tracking is required evidence, not a claim of full correctness. Algebraic equality does not promise equal floating-point behavior or equal machine speed.
