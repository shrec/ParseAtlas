"""Associativity as a first-class grammar parameter (ROADMAP Phase 9).

Everything before this module fixed associativity at ``left`` and varied only
precedence.  Experiment 0020 measured the consequence: the Generation 1
registry can reach at most 24 distinct trees (25 with the tied control
grammar) for any single source, while the number of parenthesizations of a
``k``-operator word is the Catalan number ``C(k)``.  Experiment 0023 sharpened
that into an exact decision procedure and a number: of the ``587616``
``(operator word, tree)`` pairs for ``k = 2..6``, ``541540`` -- ``92.159`` per
cent -- are unreachable by *any* strict precedence grammar.

This module asks the Phase 9 question directly: how much of that gap does
associativity close?

Nothing here modifies :mod:`parseatlas.grammar` or :mod:`parseatlas.parser`.
The extension is built alongside them so every earlier experiment stays
byte-reproducible, and the all-left slice of this space is asserted to
reproduce the Generation 1 registry exactly.

Three claims are implemented and cross-validated.

Claim A' (generalized Cartesian split).  For an associativity-aware grammar
with binding-power map ``p`` and side map ``A``, the parse of a flat operator
word splits at the minimum-binding-power position of the range: the *rightmost*
such position when that operator is left-associative, the *leftmost* when it is
right-associative.  0023's rightmost-minimum rule is the all-left case.

Claim B' (generalized reachability constraints).  At a node splitting range
``[lo, hi)`` at position ``s`` with root ``o = w[s]``::

    left-associative o:   p(o) <= p(w[t]) for t in [lo, s)    weak
                          p(o) <  p(w[t]) for t in (s, hi)    strict
    right-associative o:  p(o) <  p(w[t]) for t in [lo, s)    strict
                          p(o) <= p(w[t]) for t in (s, hi)    weak

Associativity flips which side carries the strict constraint and which the
weak one, so 0023's procedure generalizes rather than being replaced.

Claim C (decomposition).  Because a strict precedence order gives distinct
types distinct powers, ``<=`` and ``<`` coincide on *distinct* types, so the
distinct-type constraint digraph -- and therefore its acyclicity -- does not
depend on the associativity assignment at all.  The assignment can only change
the *self-loop* constraints, and each operator type's self-loops are
independent of every other type's.  Hence::

    reachable-with-associativity(T, w)
        <=> the distinct-type digraph is acyclic
            and no operator type is forbidden on both sides

and the ``2**m`` search over assignments collapses to a single pass.  Claim C
is what keeps the extended decision procedure at 0023's cost.

Sibling private helpers (``_is_acyclic``, ``_leaf_text``, ``_in_order``) are
imported rather than re-implemented; this module is an extension of the
Generation 1 stack, never a fork of it.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import permutations, product
from typing import Any

from .ast_space import _in_order
from .canonical import canonicalize
from .grammar import OPERATORS, Grammar, all_grammars, control_grammar, strict_grammars
from .parser import Binary, Node, Parser, parse
from .reachability import (
    Tree,
    _is_acyclic,
    _leaf_text,
    canonical_leaves,
    canonical_tree,
    catalan_trees,
    flat_source,
    operator_count,
    resolve_workers,
)
from .tokenizer import Token, tokenize

LEFT = "left"
RIGHT = "right"
SIDES: tuple[str, str] = (LEFT, RIGHT)

#: Below this many independent items the automatic worker choice stays sequential.
#: Three repetitions per path, medians, on this 16-core Windows host.  Both
#: harnesses force the parallel column with an explicit ``workers = cpu_count -
#: 1``: ``workers=None`` resolves to 1 below this very constant, so it cannot
#: measure the parallel branch at the sizes the constant is about.
#:
#:   verify_associativity_characterization, tasks = operator words.  Re-measured
#:   while 42 to 59 python processes were resident on the host (several agents
#:   sharing the box), so these are contended-machine numbers:
#:      k<=2   16 tasks   sequential   0.38 s   parallel 13.47 s   speedup 0.03
#:      k<=3   80 tasks   sequential   7.33 s   parallel 20.19 s   speedup 0.36
#:      k<=4  336 tasks   sequential   9.95 s   parallel 11.35 s   speedup 0.88
#:      k<=5 1360 tasks   sequential  39.55 s   parallel 21.25 s   speedup 1.86
#:      k<=6 5456 tasks   sequential 213.49 s   parallel 61.07 s   speedup 3.50
#:
#:   semantic_diversity, tasks = sources (deterministic prefixes of the 0024
#:   corpus).  Measured in the initial session on the same host under lighter
#:   load; not re-measured, see the report:
#:        5 sources  sequential  0.66 s   parallel  6.99 s   speedup 0.09
#:       16 sources  sequential  2.48 s   parallel 30.09 s   speedup 0.08
#:       64 sources  sequential 11.04 s   parallel 13.66 s   speedup 0.81
#:       96 sources  sequential 15.79 s   parallel 19.54 s   speedup 0.81
#:      128 sources  sequential 22.57 s   parallel 13.09 s   speedup 1.72
#:      250 sources  sequential 44.55 s   parallel 24.13 s   speedup 1.85
#:      500 sources  sequential 89.67 s   parallel 39.34 s   speedup 2.28
#:
#: Below the crossover a spawned interpreter plus the sympy import chain costs
#: more than the work it is handed; above it the parallel path wins.  The
#: crossover itself is load-dependent: the lighter semantic_diversity run puts
#: it between 96 and 128 items, the contended verify run between 336 and 1360,
#: so 128 is not a universal constant.  It is kept because the cost of being wrong near it is small in
#: both directions (at 336 items the contended parallel path lost by only 1.14x,
#: at 1360 it won by 1.86x) while below it the loss is catastrophic (35x at 16
#: items).  An explicit ``workers=N`` always overrides this.
PARALLEL_MINIMUM_ITEMS: int = 128


# --------------------------------------------------------------------------
# The associativity-aware grammar
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class AssociativeGrammar:
    """A precedence order plus a per-operator associativity assignment.

    ``levels`` lists operator groups from highest to lowest binding power,
    exactly as :class:`parseatlas.grammar.Grammar` does, so the tied control
    grammar ``G0`` fits the same shape.  ``associativity`` is a sorted tuple of
    ``(operator, side)`` pairs, which keeps the dataclass hashable.

    Operators sharing a level must share a side.  A level that mixed ``left``
    and ``right`` would make ``a + b - c`` genuinely ambiguous, so it is
    rejected at construction rather than resolved by an arbitrary rule.
    """

    id: str
    levels: tuple[tuple[str, ...], ...]
    associativity: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.levels:
            raise ValueError("an associativity-aware grammar needs at least one level")
        sides = dict(self.associativity)
        if len(sides) != len(self.associativity):
            raise ValueError("associativity assigns the same operator twice")
        bad = sorted(operator for operator, side in self.associativity if side not in SIDES)
        if bad:
            raise ValueError(f"associativity must be {LEFT!r} or {RIGHT!r}; bad entries for {bad}")
        operators = [operator for level in self.levels for operator in level]
        if len(set(operators)) != len(operators):
            raise ValueError("an operator appears on more than one level")
        missing = sorted(operator for operator in operators if operator not in sides)
        if missing:
            raise ValueError(f"associativity missing for operators: {missing}")
        for level in self.levels:
            distinct = {sides[operator] for operator in level}
            if len(distinct) > 1:
                raise ValueError(f"level {level} mixes associativity {sorted(distinct)}")
        object.__setattr__(self, "associativity", tuple(sorted(self.associativity)))

    @property
    def precedence(self) -> tuple[str, ...]:
        """Flat highest-to-lowest ordering, matching ``Grammar.precedence``."""
        return tuple(operator for level in self.levels for operator in level)

    @property
    def binding_power(self) -> dict[str, int]:
        """Binding powers exactly as :class:`parseatlas.parser.Parser` derives them."""
        return {
            operator: len(self.levels) - level
            for level, group in enumerate(self.levels)
            for operator in group
        }

    @property
    def sides(self) -> dict[str, str]:
        return dict(self.associativity)

    @property
    def is_all_left(self) -> bool:
        return all(side == LEFT for _, side in self.associativity)

    def base_grammar(self) -> Grammar:
        """The Generation 1 grammar this one extends, associativity dropped."""
        return Grammar(self.id.split("-", 1)[0], self.precedence, self.levels)


def side_tag(assignment: Mapping[str, str], operators: Sequence[str] = OPERATORS) -> str:
    """``L``/``R`` per operator in the given alphabet order, e.g. ``LRLL``."""
    return "".join(assignment[operator][0].upper() for operator in operators)


def from_grammar(
    grammar: Grammar,
    assignment: Mapping[str, str] | None = None,
    operators: Sequence[str] = OPERATORS,
) -> AssociativeGrammar:
    """Lift a Generation 1 grammar; ``assignment=None`` gives the all-left slice."""
    present = tuple(operator for level in grammar.levels for operator in level)
    if assignment is None:
        sides = {operator: LEFT for operator in present}
    else:
        missing = sorted(operator for operator in present if operator not in assignment)
        if missing:
            raise ValueError(f"assignment missing for operators: {missing}")
        sides = {operator: assignment[operator] for operator in present}
    tag_order = tuple(operator for operator in operators if operator in sides)
    return AssociativeGrammar(
        f"{grammar.id}-{side_tag(sides, tag_order)}",
        grammar.levels,
        tuple(sides.items()),
    )


def associativity_space(operators: Sequence[str] = OPERATORS) -> tuple[AssociativeGrammar, ...]:
    """The extended strict registry: every precedence order x every side assignment.

    For ``n`` operators this builds ``n! * 2**n`` grammars -- ``24 * 16 = 384``
    for the Generation 1 alphabet ``+ - * /``.  ``n!`` is the number of strict
    total precedence orders, unchanged from
    :func:`parseatlas.grammar.strict_grammars`; ``2**n`` is the free,
    independent left/right choice per operator, free because in a strict order
    every operator sits alone on its own level, so no level can mix sides.
    Grammar ``G{i:02d}-LLLL`` is the lift of Generation 1's ``G{i:02d}``, and
    the ``LLLL`` slice is the whole of the old strict registry.
    """
    operators = tuple(operators)
    grammars: list[AssociativeGrammar] = []
    for index, ordering in enumerate(permutations(operators), start=1):
        levels = tuple((operator,) for operator in ordering)
        for choice in product(SIDES, repeat=len(operators)):
            assignment = dict(zip(operators, choice))
            grammars.append(
                AssociativeGrammar(
                    f"G{index:02d}-{side_tag(assignment, operators)}",
                    levels,
                    tuple(assignment.items()),
                )
            )
    return tuple(grammars)


def control_associativity_space(
    operators: Sequence[str] = OPERATORS,
) -> tuple[AssociativeGrammar, ...]:
    """Side assignments of the tied control grammar ``G0``: one choice per level.

    ``G0`` has two levels, so the choice is per level and not per operator --
    ``2**2 = 4`` grammars, not ``2**4``.  A level mixing sides is rejected by
    :class:`AssociativeGrammar`.
    """
    base = control_grammar()
    grammars: list[AssociativeGrammar] = []
    for choice in product(SIDES, repeat=len(base.levels)):
        assignment = {
            operator: side for level, side in zip(base.levels, choice) for operator in level
        }
        tag_order = tuple(operator for operator in operators if operator in assignment)
        grammars.append(
            AssociativeGrammar(
                f"{base.id}-{side_tag(assignment, tag_order)}",
                base.levels,
                tuple(assignment.items()),
            )
        )
    return tuple(grammars)


def all_associativity_grammars(
    operators: Sequence[str] = OPERATORS,
) -> tuple[AssociativeGrammar, ...]:
    """Control variants followed by the strict extended space: ``4 + 384 = 388``."""
    return control_associativity_space(operators) + associativity_space(operators)


_SPACE: tuple[AssociativeGrammar, ...] | None = None
_STRICT: tuple[Grammar, ...] | None = None


def _cached_space() -> tuple[AssociativeGrammar, ...]:
    """The 384 extended grammars, built once per process."""
    global _SPACE
    if _SPACE is None:
        _SPACE = associativity_space()
    return _SPACE


def _cached_strict() -> tuple[Grammar, ...]:
    """The 24 Generation 1 strict grammars, built once per process."""
    global _STRICT
    if _STRICT is None:
        _STRICT = strict_grammars()
    return _STRICT


def resolve_item_workers(item_count: int, workers: int | None = None) -> int:
    """Worker count derived from the observed core count, with a measured floor.

    ``workers=None`` asks for the measured-best path: sequential below
    :data:`PARALLEL_MINIMUM_ITEMS` independent items, otherwise
    :func:`parseatlas.reachability.resolve_workers`, which takes the observed
    core count minus one core of headroom.  An explicit ``workers=N`` is obeyed
    as given, so the parallel branch stays reachable at any size.
    """
    if workers is None and item_count < PARALLEL_MINIMUM_ITEMS:
        return 1
    return resolve_workers(item_count, workers)


# --------------------------------------------------------------------------
# The parser
# --------------------------------------------------------------------------


class AssociativeParser(Parser):
    """Precedence climbing with a per-operator side.

    Only ``_expression`` changes relative to :class:`parseatlas.parser.Parser`:
    a left-associative operator recurses at ``power + 1`` so an equal-power
    operator is left behind for the loop, a right-associative one recurses at
    ``power`` so the equal-power operator is swallowed by the right operand.
    ``_primary`` -- numbers, variables, parentheses -- is inherited unchanged,
    which is what keeps the two parsers from drifting apart.

    ``Parser.__init__`` is not called because it takes a
    :class:`parseatlas.grammar.Grammar`; the attributes it would set are set
    here from the associativity-aware grammar instead.
    """

    def __init__(self, tokens: tuple[Token, ...], grammar: AssociativeGrammar) -> None:
        self.tokens = tokens
        self.grammar = grammar
        self.index = 0
        self._powers = grammar.binding_power
        self._sides = grammar.sides

    def _expression(self, minimum_power: int) -> Node:
        left = self._primary()
        while (
            self._current.kind == "operator"
            and self._powers[self._current.value] >= minimum_power
        ):
            operator = self._advance().value
            power = self._powers[operator]
            following = power + 1 if self._sides[operator] == LEFT else power
            left = Binary(operator, left, self._expression(following))
        return left


def associative_parse(source: str, grammar: AssociativeGrammar) -> Node:
    """Parse ``source`` under an associativity-aware grammar into a parser AST."""
    return AssociativeParser(tokenize(source), grammar).parse()


def associative_tree(source: str, grammar: AssociativeGrammar) -> Tree:
    """Canonical hashable tree form of :func:`associative_parse`."""
    return canonical_tree(associative_parse(source, grammar))


# --------------------------------------------------------------------------
# Claim A': the generalized Cartesian split
# --------------------------------------------------------------------------


def split_tree(
    leaves: Sequence[Any], operators: Sequence[str], grammar: AssociativeGrammar
) -> Tree:
    """Build the parse tree of a flat word by minimum-binding-power split.

    Rightmost minimum for a left-associative operator, leftmost for a
    right-associative one.  With ``grammar`` all-left this is exactly
    :func:`parseatlas.reachability.rightmost_minimum_tree`.
    """
    leaves = tuple(leaves)
    operators = tuple(operators)
    if len(leaves) != len(operators) + 1:
        raise ValueError(
            f"expected {len(operators) + 1} leaves for {len(operators)} operators, got {len(leaves)}"
        )
    powers = grammar.binding_power
    sides = grammar.sides
    missing = sorted({operator for operator in operators if operator not in powers})
    if missing:
        raise ValueError(f"grammar does not rank operators: {missing}")
    return _split(leaves, operators, powers, sides, 0, len(operators))


def _split(
    leaves: tuple[Any, ...],
    operators: tuple[str, ...],
    powers: Mapping[str, int],
    sides: Mapping[str, str],
    low: int,
    high: int,
) -> Tree:
    if low == high:
        return leaves[low]
    minimum = min(powers[operators[index]] for index in range(low, high))
    candidates = [index for index in range(low, high) if powers[operators[index]] == minimum]
    # Every minimum-power position in the range holds an operator of the same
    # level, and AssociativeGrammar forbids a level from mixing sides, so the
    # first candidate's side speaks for all of them.
    side = sides[operators[candidates[0]]]
    split = candidates[-1] if side == LEFT else candidates[0]
    return (
        operators[split],
        _split(leaves, operators, powers, sides, low, split),
        _split(leaves, operators, powers, sides, split + 1, high),
    )


def _split_primary(
    tokens: tuple[Token, ...], index: int, grammar: AssociativeGrammar
) -> tuple[Tree, int]:
    token = tokens[index]
    if token.kind in ("number", "name"):
        return _leaf_text(token), index + 1
    if token.kind == "left":
        tree, index = _split_level(tokens, index + 1, grammar)
        if tokens[index].kind != "right":
            raise ValueError("Expected closing parenthesis")
        return tree, index + 1
    raise ValueError(f"Expected a primary; got {token.value!r}")


def _split_level(
    tokens: tuple[Token, ...], index: int, grammar: AssociativeGrammar
) -> tuple[Tree, int]:
    leaf, index = _split_primary(tokens, index, grammar)
    leaves: list[Any] = [leaf]
    operators: list[str] = []
    while tokens[index].kind == "operator":
        operators.append(tokens[index].value)
        leaf, index = _split_primary(tokens, index + 1, grammar)
        leaves.append(leaf)
    return split_tree(leaves, operators, grammar), index


def split_parse(source: str, grammar: AssociativeGrammar) -> Tree:
    """Parse ``source`` using only the Claim A' recursion, independent of any parser."""
    tokens = tokenize(source)
    tree, index = _split_level(tokens, 0, grammar)
    if tokens[index].kind != "eof":
        raise ValueError(f"Unexpected token: {tokens[index].value!r}")
    return tree


def all_left_agreement(sources: Iterable[str]) -> dict[str, Any]:
    """Assert the Generation 1 registry is exactly the all-left slice of this space.

    For every source and every registered grammar (``G0`` plus ``G01..G24``),
    the associativity-aware parser under the all-left lift must return the very
    same AST as :func:`parseatlas.parser.parse`, and the Claim A' split
    recursion must return its canonical tree.
    """
    sources = tuple(sources)
    grammars = all_grammars()
    parser_agreement = 0
    split_agreement = 0
    disagreements: list[dict[str, Any]] = []
    for source in sources:
        for grammar in grammars:
            lifted = from_grammar(grammar)
            expected = parse(source, grammar)
            actual = associative_parse(source, lifted)
            if actual == expected:
                parser_agreement += 1
            else:
                disagreements.append({"source": source, "grammar": lifted.id, "kind": "parser"})
            predicted = split_parse(source, lifted)
            if predicted == canonical_tree(expected):
                split_agreement += 1
            else:
                disagreements.append(
                    {
                        "source": source,
                        "grammar": lifted.id,
                        "kind": "split",
                        "predicted": predicted,
                        "actual": canonical_tree(expected),
                    }
                )
    comparisons = len(sources) * len(grammars)
    return {
        "source_count": len(sources),
        "grammar_count": len(grammars),
        "comparison_count": comparisons,
        "parser_agreement_count": parser_agreement,
        "split_agreement_count": split_agreement,
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
        "all_left_slice_reproduces_generation_1": parser_agreement == comparisons,
        "claim_a_prime_holds": split_agreement == comparisons,
    }


def split_rule_agreement(sources: Iterable[str]) -> dict[str, Any]:
    """Claim A' over the whole extended space, including right-associative grammars."""
    sources = tuple(sources)
    grammars = all_associativity_grammars()
    agreement = 0
    disagreements: list[dict[str, Any]] = []
    for source in sources:
        for grammar in grammars:
            predicted = split_parse(source, grammar)
            actual = associative_tree(source, grammar)
            if predicted == actual:
                agreement += 1
            else:
                disagreements.append(
                    {
                        "source": source,
                        "grammar": grammar.id,
                        "predicted": predicted,
                        "actual": actual,
                    }
                )
    return {
        "source_count": len(sources),
        "grammar_count": len(grammars),
        "comparison_count": len(sources) * len(grammars),
        "agreement_count": agreement,
        "disagreement_count": len(disagreements),
        "disagreements": disagreements[:10],
        "claim_a_prime_holds": not disagreements,
    }


# --------------------------------------------------------------------------
# Claim B' / Claim C: reachability with associativity
# --------------------------------------------------------------------------


def node_profiles(
    tree: Tree, operators: Sequence[str]
) -> tuple[tuple[str, frozenset[str], frozenset[str]], ...]:
    """``(root, left operator types, right operator types)`` for every internal node."""
    operators = tuple(operators)
    if operator_count(tree) != len(operators):
        raise ValueError(f"tree has {operator_count(tree)} operators, word has {len(operators)}")
    profiles: list[tuple[str, frozenset[str], frozenset[str]]] = []
    _collect_profiles(tree, operators, 0, len(operators), profiles)
    return tuple(profiles)


def _collect_profiles(
    tree: Tree,
    operators: tuple[str, ...],
    low: int,
    high: int,
    out: list[tuple[str, frozenset[str], frozenset[str]]],
) -> None:
    if not isinstance(tree, tuple):
        return
    split = low + operator_count(tree[1])
    root = operators[split]
    if tree[0] != root:
        raise ValueError(
            f"tree root {tree[0]!r} at position {split} does not match word operator {root!r}"
        )
    out.append((root, frozenset(operators[low:split]), frozenset(operators[split + 1 : high])))
    _collect_profiles(tree[1], operators, low, split, out)
    _collect_profiles(tree[2], operators, split + 1, high, out)


def tree_constraints_with_associativity(
    tree: Tree, operators: Sequence[str], assignment: Mapping[str, str]
) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    """Claim B' constraints under a fixed associativity assignment.

    Returns ``(strict_edges, weak_edges)`` over operator types.  A
    left-associative root takes the weak side on its left and the strict side
    on its right; a right-associative root takes the mirror image.  With every
    operator left-associative this reproduces
    :func:`parseatlas.reachability.tree_constraints` exactly.
    """
    profiles = node_profiles(tree, operators)
    missing = sorted({root for root, _, _ in profiles} - set(assignment))
    if missing:
        raise ValueError(f"assignment missing for operators: {missing}")
    strict: set[tuple[str, str]] = set()
    weak: set[tuple[str, str]] = set()
    for root, left, right in profiles:
        if assignment[root] == LEFT:
            weak |= {(root, other) for other in left}
            strict |= {(root, other) for other in right}
        else:
            strict |= {(root, other) for other in left}
            weak |= {(root, other) for other in right}
    return strict, weak


def assignment_reachable(
    tree: Tree, operators: Sequence[str], assignment: Mapping[str, str]
) -> bool:
    """Is ``tree`` produced by some strict precedence order under this fixed assignment?

    The direct, unoptimized form of 0023's test: no strict self-loop, and the
    distinct-type constraint digraph acyclic.
    """
    strict, weak = tree_constraints_with_associativity(tree, operators, assignment)
    if any(source == target for source, target in strict):
        return False
    return _is_acyclic({(a, b) for a, b in strict | weak if a != b})


def reachability_with_associativity(tree: Tree, operators: Sequence[str]) -> dict[str, Any]:
    """Decide reachability over the extended space from the constraint graph alone.

    No grammar is enumerated and, by Claim C, no associativity assignment is
    enumerated either.  The union of strict and weak edges restricted to
    distinct operator types is the same for every assignment, so acyclicity is
    tested once; the assignment can only decide self-loops, and it does so
    independently per operator type.
    """
    operators = tuple(operators)
    profiles = node_profiles(tree, operators)
    types = sorted(set(operators))
    edges = {
        (root, other)
        for root, left, right in profiles
        for other in (left | right)
        if other != root
    }
    acyclic = _is_acyclic(edges)
    forbidden: dict[str, set[str]] = {operator: set() for operator in types}
    for root, left, right in profiles:
        # A left-associative root may not see its own type on its right, and a
        # right-associative root may not see its own type on its left: either
        # would demand the impossible strict self-loop p(o) < p(o).
        if root in right:
            forbidden[root].add(LEFT)
        if root in left:
            forbidden[root].add(RIGHT)
    allowed = {
        operator: tuple(side for side in SIDES if side not in forbidden[operator])
        for operator in types
    }
    reachable = acyclic and all(allowed[operator] for operator in types)
    count = 0
    if reachable:
        count = 1
        for operator in types:
            count *= len(allowed[operator])
    return {
        "reachable": reachable,
        "acyclic": acyclic,
        "operator_types": types,
        "allowed_sides": {operator: list(allowed[operator]) for operator in types},
        "witness": {operator: allowed[operator][0] for operator in types} if reachable else None,
        "feasible_assignments": count,
        "assignment_space": 2 ** len(types),
        # The all-left slice is exactly 0023's predicate; the tests assert that.
        "precedence_only_reachable": acyclic
        and all(LEFT in allowed[operator] for operator in types),
    }


# --------------------------------------------------------------------------
# Coverage against the full Catalan space
# --------------------------------------------------------------------------


def coverage_with_associativity(source: str) -> dict[str, Any]:
    """Reachable trees for one source: precedence only vs precedence plus associativity.

    The denominator is the number of parenthesizations of the source's own
    in-order leaf/operator sequence, i.e. the Catalan number ``C(k)`` -- the
    same denominator experiment 0020 used, so the two reports compare directly.
    """
    strict = strict_grammars()
    precedence = {canonical_tree(parse(source, grammar)) for grammar in strict}
    control = canonical_tree(parse(source, control_grammar()))
    extended = associativity_space()
    associative = {associative_tree(source, grammar) for grammar in extended}
    control_extended = {
        associative_tree(source, grammar) for grammar in control_associativity_space()
    }
    leaves, operators = _in_order(control)
    total = len(catalan_trees(leaves, operators))
    return {
        "source": source,
        "leaf_count": len(leaves),
        "operator_count": len(operators),
        "catalan_total": total,
        "precedence_grammar_count": len(strict),
        "associativity_grammar_count": len(extended),
        "precedence_reachable": len(precedence),
        "associativity_reachable": len(associative),
        "precedence_coverage": len(precedence) / total,
        "associativity_coverage": len(associative) / total,
        "gained_trees": len(associative - precedence),
        "coverage_gain": (len(associative) - len(precedence)) / total,
        "unreachable_before": total - len(precedence),
        "unreachable_after": total - len(associative),
        "recovered_fraction_of_gap": (
            (len(associative) - len(precedence)) / (total - len(precedence))
            if total - len(precedence)
            else 0.0
        ),
        "with_control_precedence_reachable": len(precedence | {control}),
        "with_control_associativity_reachable": len(associative | control_extended),
        "precedence_subset_of_associativity": precedence <= associative,
    }


def coverage_report_with_associativity(sources: Iterable[str]) -> dict[str, Any]:
    """Per-expression coverage table, mirroring :func:`parseatlas.ast_space.coverage_report`."""
    records = [coverage_with_associativity(source) for source in sources]
    denominator = max(len(records), 1)
    return {
        "expression_count": len(records),
        "mean_precedence_coverage": sum(r["precedence_coverage"] for r in records) / denominator,
        "mean_associativity_coverage": sum(r["associativity_coverage"] for r in records)
        / denominator,
        "expressions": records,
    }


# --------------------------------------------------------------------------
# Exhaustive cross-validation
# --------------------------------------------------------------------------


def _verify_associativity_word(
    payload: tuple[int, tuple[str, ...]],
) -> tuple[int, int, int, int, int, int, int, int, int, list[dict[str, Any]]]:
    """Ground truth vs. predicate for one operator word.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    size, word = payload
    leaves = canonical_leaves(size + 1)
    source = flat_source(leaves, word)
    truth: set[Tree] = set()
    split_checks = 0
    split_disagreements = 0
    for grammar in _cached_space():
        actual = canonical_tree(associative_parse(source, grammar))
        predicted = split_tree(leaves, word, grammar)
        split_checks += 1
        if predicted != actual:
            split_disagreements += 1
        truth.add(actual)
    precedence_truth = {canonical_tree(parse(source, grammar)) for grammar in _cached_strict()}
    trees = catalan_trees(leaves, word)
    reachable_precedence = 0
    reachable_associativity = 0
    precedence_mismatches = 0
    mismatches: list[dict[str, Any]] = []
    for tree in trees:
        decision = reachability_with_associativity(tree, word)
        associativity_truth = tree in truth
        precedence_truth_flag = tree in precedence_truth
        reachable_associativity += associativity_truth
        reachable_precedence += precedence_truth_flag
        if decision["reachable"] != associativity_truth:
            mismatches.append(
                {
                    "operators": list(word),
                    "tree": tree,
                    "predicted": decision["reachable"],
                    "actual": associativity_truth,
                }
            )
        if decision["precedence_only_reachable"] != precedence_truth_flag:
            precedence_mismatches += 1
    return (
        size,
        len(trees),
        reachable_precedence,
        reachable_associativity,
        split_checks,
        split_disagreements,
        len(mismatches),
        precedence_mismatches,
        0 if precedence_truth <= truth else 1,
        mismatches[:5],
    )


def verify_associativity_characterization(
    max_operators: int = 6, workers: int | None = None
) -> dict[str, Any]:
    """Cross-validate the extended procedure against exhaustive parsing, ``k = 2..max_operators``.

    For every operator word over ``+ - * /`` the ground truth is built by really
    parsing the flat source with all ``384`` extended grammars, and the same
    loop checks Claim A' against that parser.  Every Catalan tree of the word is
    then scored by :func:`reachability_with_associativity` -- both its extended
    verdict and its all-left verdict -- and compared with the two truth sets.

    Work is independent per operator word and CPU-bound, so it is distributed
    across processes once the sweep has at least :data:`PARALLEL_MINIMUM_ITEMS`
    words -- ``max_operators >= 4`` -- and stays sequential below that, both
    from the measurement recorded on that constant.  Parallelism changes only
    speed: every word is scored in isolation and the aggregate is identical to
    ``workers=1``.

    Caller guard: the default path builds a :class:`ProcessPoolExecutor` and
    Windows uses the ``spawn`` start method, so each child re-imports the
    caller's ``__main__``.  Drive this from inside ``if __name__ == "__main__":``
    (or pass ``workers=1``) when calling it from a script file; ``python -c``
    and pytest are unaffected.
    """
    if max_operators < 2:
        raise ValueError("max_operators must be at least 2")
    tasks = [
        (size, word)
        for size in range(2, max_operators + 1)
        for word in product(OPERATORS, repeat=size)
    ]
    worker_count = resolve_item_workers(len(tasks), workers)
    if worker_count == 1:
        results = [_verify_associativity_word(task) for task in tasks]
    else:
        chunk = max(1, len(tasks) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            results = list(pool.map(_verify_associativity_word, tasks, chunksize=chunk))

    buckets: dict[int, dict[str, Any]] = {
        size: {
            "operator_count": size,
            "pattern_count": 0,
            "tree_count": 0,
            "precedence_reachable": 0,
            "associativity_reachable": 0,
            "split_checks": 0,
            "split_disagreements": 0,
            "mismatch_count": 0,
            "precedence_mismatch_count": 0,
            "nesting_violations": 0,
        }
        for size in range(2, max_operators + 1)
    }
    examples: list[dict[str, Any]] = []
    for (
        size,
        tree_count,
        reachable_precedence,
        reachable_associativity,
        split_checks,
        split_disagreements,
        mismatch_count,
        precedence_mismatches,
        nesting_violation,
        word_examples,
    ) in results:
        bucket = buckets[size]
        bucket["pattern_count"] += 1
        bucket["tree_count"] += tree_count
        bucket["precedence_reachable"] += reachable_precedence
        bucket["associativity_reachable"] += reachable_associativity
        bucket["split_checks"] += split_checks
        bucket["split_disagreements"] += split_disagreements
        bucket["mismatch_count"] += mismatch_count
        bucket["precedence_mismatch_count"] += precedence_mismatches
        bucket["nesting_violations"] += nesting_violation
        if word_examples and len(examples) < 10:
            examples.extend(word_examples[: 10 - len(examples)])

    per_k = []
    for size in range(2, max_operators + 1):
        bucket = buckets[size]
        trees = bucket["tree_count"]
        patterns = bucket["pattern_count"]
        bucket["catalan_per_pattern"] = trees // patterns if patterns else 0
        bucket["precedence_coverage"] = bucket["precedence_reachable"] / trees if trees else 0.0
        bucket["associativity_coverage"] = (
            bucket["associativity_reachable"] / trees if trees else 0.0
        )
        bucket["unreachable_before"] = trees - bucket["precedence_reachable"]
        bucket["unreachable_after"] = trees - bucket["associativity_reachable"]
        bucket["recovered_count"] = (
            bucket["associativity_reachable"] - bucket["precedence_reachable"]
        )
        bucket["recovered_fraction_of_gap"] = (
            bucket["recovered_count"] / bucket["unreachable_before"]
            if bucket["unreachable_before"]
            else 0.0
        )
        per_k.append(bucket)

    total_trees = sum(bucket["tree_count"] for bucket in per_k)
    total_precedence = sum(bucket["precedence_reachable"] for bucket in per_k)
    total_associativity = sum(bucket["associativity_reachable"] for bucket in per_k)
    unreachable_before = total_trees - total_precedence
    unreachable_after = total_trees - total_associativity
    total_split_bad = sum(bucket["split_disagreements"] for bucket in per_k)
    total_mismatches = sum(bucket["mismatch_count"] for bucket in per_k)
    total_precedence_mismatches = sum(bucket["precedence_mismatch_count"] for bucket in per_k)
    total_nesting = sum(bucket["nesting_violations"] for bucket in per_k)
    return {
        "max_operators": max_operators,
        "workers": worker_count,
        "grammar_count": len(_cached_space()),
        "per_k": per_k,
        "total_patterns": sum(bucket["pattern_count"] for bucket in per_k),
        "total_trees": total_trees,
        "total_precedence_reachable": total_precedence,
        "total_associativity_reachable": total_associativity,
        "total_unreachable_before": unreachable_before,
        "total_unreachable_after": unreachable_after,
        "unreachable_fraction_before": unreachable_before / total_trees if total_trees else 0.0,
        "unreachable_fraction_after": unreachable_after / total_trees if total_trees else 0.0,
        "recovered_count": total_associativity - total_precedence,
        "recovered_fraction_of_gap": (
            (total_associativity - total_precedence) / unreachable_before
            if unreachable_before
            else 0.0
        ),
        "total_mismatches": total_mismatches,
        "characterization_holds": total_mismatches == 0,
        "precedence_mismatch_count": total_precedence_mismatches,
        "agrees_with_0023": total_precedence_mismatches == 0,
        "split_checks": sum(bucket["split_checks"] for bucket in per_k),
        "split_disagreements": total_split_bad,
        "claim_a_prime_holds": total_split_bad == 0,
        "nesting_violations": total_nesting,
        "precedence_subset_of_associativity": total_nesting == 0,
        "mismatch_examples": examples,
    }


# --------------------------------------------------------------------------
# Semantic diversity
# --------------------------------------------------------------------------


def _semantic_key(
    node: Node, cache: dict[Tree, tuple[str, str, tuple[str, ...]]]
) -> tuple[str, str, tuple[str, ...]]:
    """The project-wide class key ``(canonical, domain, excluded points)``.

    Keyed by canonical tree form so the expensive sympy ``simplify`` runs once
    per distinct AST rather than once per grammar; many of the 384 grammars
    produce byte-identical trees.
    """
    tree = canonical_tree(node)
    cached = cache.get(tree)
    if cached is None:
        canonical = canonicalize(node)
        cached = (
            canonical["expression"],
            canonical["domain"],
            tuple(canonical["excluded_points"]),
        )
        cache[tree] = cached
    return cached


def _semantic_record(source: str) -> dict[str, Any]:
    """Semantic class counts for one source under both registries.

    Module level on purpose: the process pool uses the Windows ``spawn`` start
    method, which can only pickle top-level functions.
    """
    cache: dict[Tree, tuple[str, str, tuple[str, ...]]] = {}
    strict = _cached_strict()
    extended = _cached_space()
    precedence_asts: set[Tree] = set()
    precedence_classes: set[tuple[str, str, tuple[str, ...]]] = set()
    for grammar in strict:
        node = parse(source, grammar)
        precedence_asts.add(canonical_tree(node))
        precedence_classes.add(_semantic_key(node, cache))
    associativity_asts: set[Tree] = set()
    associativity_classes: set[tuple[str, str, tuple[str, ...]]] = set()
    for grammar in extended:
        node = associative_parse(source, grammar)
        associativity_asts.add(canonical_tree(node))
        associativity_classes.add(_semantic_key(node, cache))
    control_classes: set[tuple[str, str, tuple[str, ...]]] = set()
    for grammar in control_associativity_space():
        control_classes.add(_semantic_key(associative_parse(source, grammar), cache))
    precedence_with_control = precedence_classes | {
        _semantic_key(parse(source, control_grammar()), cache)
    }
    return {
        "source": source,
        "precedence_grammar_count": len(strict),
        "associativity_grammar_count": len(extended),
        "precedence_ast_forms": len(precedence_asts),
        "associativity_ast_forms": len(associativity_asts),
        "precedence_classes": len(precedence_classes),
        "associativity_classes": len(associativity_classes),
        "new_classes": len(associativity_classes - precedence_classes),
        "class_ratio": len(associativity_classes) / max(len(precedence_classes), 1),
        "precedence_sensitivity": (len(precedence_classes) - 1) / (len(strict) - 1),
        "associativity_sensitivity": (len(associativity_classes) - 1) / (len(extended) - 1),
        "with_control_precedence_classes": len(precedence_with_control),
        "with_control_associativity_classes": len(associativity_classes | control_classes),
        "precedence_subset_of_associativity": precedence_classes <= associativity_classes,
    }


def semantic_diversity(sources: Iterable[str], workers: int | None = None) -> dict[str, Any]:
    """Semantic class counts under precedence only vs the extended space.

    The class key is the project-wide ``(canonical, domain, excluded_points)``
    triple from :mod:`parseatlas.analyze`, so ``precedence_sensitivity`` is
    exactly the ``S(E) = (classes - 1) / 23`` of experiment 0017 and the numbers
    here compare directly with 0017 and 0024.  ``associativity_sensitivity``
    applies the same definition over the larger registry and therefore
    normalizes by ``383``; the two live on different scales by construction, so
    the raw class counts are the honest comparison.

    Work is independent per source and dominated by sympy ``simplify``, so it
    is distributed across processes once there are at least
    :data:`PARALLEL_MINIMUM_ITEMS` sources and stays sequential below that.
    Parallelism changes only speed: the aggregate is identical to ``workers=1``.

    Caller guard: the parallel path builds a :class:`ProcessPoolExecutor` and
    Windows uses the ``spawn`` start method, so each child re-imports the
    caller's ``__main__``.  Drive a large corpus from inside
    ``if __name__ == "__main__":`` (or pass ``workers=1``) when calling from a
    script file; ``python -c`` and pytest are unaffected.
    """
    sources = tuple(sources)
    if not sources:
        raise ValueError("semantic_diversity needs at least one source")
    worker_count = resolve_item_workers(len(sources), workers)
    if worker_count == 1:
        records = [_semantic_record(source) for source in sources]
    else:
        chunk = max(1, len(sources) // (worker_count * 4))
        with ProcessPoolExecutor(max_workers=worker_count) as pool:
            records = list(pool.map(_semantic_record, sources, chunksize=chunk))
    denominator = len(records)
    total_precedence = sum(record["precedence_classes"] for record in records)
    total_associativity = sum(record["associativity_classes"] for record in records)
    return {
        "source_count": denominator,
        "workers": worker_count,
        "precedence_grammar_count": len(_cached_strict()),
        "associativity_grammar_count": len(_cached_space()),
        "total_precedence_classes": total_precedence,
        "total_associativity_classes": total_associativity,
        "mean_precedence_classes": total_precedence / denominator,
        "mean_associativity_classes": total_associativity / denominator,
        "class_ratio": total_associativity / max(total_precedence, 1),
        "mean_precedence_sensitivity": sum(r["precedence_sensitivity"] for r in records)
        / denominator,
        "mean_associativity_sensitivity": sum(r["associativity_sensitivity"] for r in records)
        / denominator,
        "sources_with_new_classes": sum(record["new_classes"] > 0 for record in records),
        "expressions": records,
    }
