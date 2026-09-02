"""Equivalence-preserving transformation axes measured outside field arithmetic.

This module runs ParseAtlas in **equivalence-preserving mode**, which is not the mode of
experiments 0001-0025.  In semantic-exploration mode a different grammar yields a *different*
function and the interesting quantity is how the meaning moved.  Here the meaning is fixed:
every admitted candidate satisfies ``R1(x) == R2(x)`` on the declared domain, and the
interesting quantity is how the *representation* moved.  The two modes must never be mixed,
so nothing in this module reads the grammar registry and nothing in the grammar experiments
reads this module.

The five axes below are the rewrite vocabulary of the external UltrafastSecp256k1
representation search (branch ``experiment/representation-search``).  On production
secp256k1 field arithmetic that search reported a local optimum: the best measured
improvement was -0.34 percent, inside noise.  The question this module answers is narrower
and entirely internal: applied to ordinary mathematical formulas from the domains ParseAtlas
already covers in experiments 0006-0011, how many *structurally* cheaper equivalent
representations does each axis reach, and do operation count and critical-path depth agree
about which candidates are cheaper.

The measured answer is a **negative transfer** result and is reported as one.  On this corpus
the operation-count model is a *good* predictor of depth on average -- Spearman rho 0.843 over
227 admitted candidates -- so the external finding that an operation-count model can be wrong by
an order of magnitude against hardware does not reproduce here.  What does survive is narrower:
the model is blind to a specific non-empty subset, the candidates that reduce depth without
reducing operation count, and that subset is non-empty under every depth convention tested.

**This module measures structure only.**  A SymPy operation count is not a machine cost and a
Python-level timing of a symbolic rewrite says nothing about a compiled implementation.  No
function here produces, or may be read as producing, a speedup claim.
"""

from __future__ import annotations

import os
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from math import ceil, log2
from typing import Any

from sympy import (
    Add,
    Expr,
    Integer,
    Mul,
    Pow,
    Rational,
    Symbol,
    cancel,
    cse,
    expand,
    factor,
    factor_terms,
    simplify,
    solve,
    srepr,
    sympify,
    together,
    zoo,
)
from sympy import collect as sympy_collect

# ---------------------------------------------------------------------------
# 1. The closed axis vocabulary
# ---------------------------------------------------------------------------

AXES: tuple[str, ...] = (
    "mul_square_trade",
    "sign_placement",
    "algebraic_rewrite",
    "operation_fusion",
    "common_subexpression_reuse",
)

AXIS_DEFINITIONS: dict[str, str] = {
    "mul_square_trade": (
        "Trade multiplications against squares in either direction, including "
        "2*a*b = (a+b)**2 - a**2 - b**2, a*b = ((a+b)**2 - (a-b)**2)/4, and the "
        "difference-of-squares trade a**2 - b**2 = (a-b)*(a+b)."
    ),
    "sign_placement": (
        "Move a negation without changing the value: flip the sign of an additive factor "
        "and compensate on the surrounding product, or hoist a negation out of a sum. "
        "Subtraction-versus-add-plus-negate is part of this axis in a machine representation "
        "but is NOT representable in SymPy, whose canonical form for a-b is already "
        "Add(a, Mul(-1, b)); that unreachable half is reported, never silently dropped."
    ),
    "algebraic_rewrite": (
        "Factorisation and distribution through SymPy's structural rewriters: factor, expand, "
        "factor_terms, together, cancel and collect on the whole expression and on bounded-depth "
        "subexpressions.  This is the axis that can silently delete a domain restriction, which "
        "is exactly why verify_equivalence checks the excluded points and not only the residual."
    ),
    "operation_fusion": (
        "a + a <-> 2*a and constant-multiple decomposition (n*a -> a + (n-1)*a, "
        "n*a -> p*(q*a) for n = p*q).  SymPy's Add.flatten performs the fusing direction "
        "automatically, so the decomposing direction is only expressible through unevaluated "
        "construction; this module builds it with evaluate=False and says so."
    ),
    "common_subexpression_reuse": (
        "Compute a repeated subexpression once and reuse it.  The result is a straight-line "
        "program, not a single expression, so this axis is the reason a candidate is a Program "
        "and not an Expr."
    ),
}

UNKNOWN_AXIS_MESSAGE = "unknown transformation axis: {axis!r}; the vocabulary is closed and is " + ", ".join(AXES)

VERDICTS: tuple[str, ...] = ("equivalent", "domain_violating", "unsound")

DEFAULT_MAX_DEPTH = 4
DEFAULT_CANDIDATE_LIMIT = 16
NUMERIC_TOLERANCE = 1e-18
NUMERIC_SAMPLE_COUNT = 3

# Deterministic, non-integer, non-symmetric probe values with **both signs**.  Integers are
# avoided because an integer probe point makes accidental agreement far more likely on
# polynomial identities.  Signs alternate because a one-signed sample set cannot refute a
# sign-dependent claim at all: on positive points ``sqrt(x*x)`` and ``x`` agree, so a positive-only
# probe would contradict the (correct) symbolic ``unsound`` verdict instead of confirming it.
_SAMPLE_BASE: tuple[Rational, ...] = (
    Rational(3, 2), Rational(-5, 3), Rational(7, 4), Rational(-9, 5),
    Rational(11, 6), Rational(-13, 7), Rational(4, 3), Rational(-8, 5),
    Rational(6, 5), Rational(-12, 7), Rational(5, 4), Rational(-7, 3),
)

# The depth charge for a k-argument node is a **convention**, not a measurement, so it is a
# named parameter and the report publishes the sensitivity of its headline to all three.
DEPTH_CONVENTIONS: tuple[str, ...] = ("balanced", "left_chain", "flat")
DEFAULT_DEPTH_CONVENTION = "balanced"

UNKNOWN_CONVENTION_MESSAGE = (
    "unknown depth convention: {convention!r}; the choices are " + ", ".join(DEPTH_CONVENTIONS)
)


# ---------------------------------------------------------------------------
# 2. Programs: a candidate is straight-line code, not necessarily one expression
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Program:
    """A straight-line program: ordered temporary assignments followed by one result.

    Four of the five axes produce a single expression and therefore a program with no
    assignments.  ``common_subexpression_reuse`` cannot be expressed that way at all: reuse is
    a DAG, and writing the DAG back out as a tree is precisely the thing reuse avoids.
    """

    assignments: tuple[tuple[Symbol, Expr], ...]
    result: Expr

    @property
    def components(self) -> tuple[Expr, ...]:
        return tuple(rhs for _, rhs in self.assignments) + (self.result,)

    def key(self) -> str:
        """Structural identity, from ``srepr`` so an unevaluated form is never confused with
        its canonical twin: ``Add(a, a, evaluate=False)`` and ``2*a`` print alike under ``str``
        but are different representations, which is the whole subject of this module."""
        return " ; ".join([f"{name}={srepr(rhs)}" for name, rhs in self.assignments] + [srepr(self.result)])

    def render(self) -> str:
        """Human-readable straight-line form, so a reuse candidate is not printed as the tree
        it was written to avoid."""
        return "; ".join([f"{name} = {rhs}" for name, rhs in self.assignments] + [str(self.result)])


def as_program(expression: Program | Expr) -> Program:
    """Accept either a bare expression or a program and return a program."""
    if isinstance(expression, Program):
        return expression
    return Program((), expression)


def inline(expression: Program | Expr) -> Expr:
    """Back-substitute every temporary so the program becomes one mathematical expression."""
    program = as_program(expression)
    result = program.result
    for name, rhs in reversed(program.assignments):
        result = result.xreplace({name: rhs})
    return result


def _inline_into(expression: Expr, assignments: tuple[tuple[Symbol, Expr], ...]) -> Expr:
    for name, rhs in reversed(assignments):
        expression = expression.xreplace({name: rhs})
    return expression


# ---------------------------------------------------------------------------
# 3. Structural cost: operation kinds, total operations, critical-path depth
# ---------------------------------------------------------------------------

COST_KINDS: tuple[str, ...] = ("add", "mul", "div", "pow", "neg", "func")


def _levels_for_arity(count: int, convention: str = DEFAULT_DEPTH_CONVENTION) -> int:
    """Levels charged to a k-argument node under one named convention.

    ``critical_path.operation_cost`` walks a **binary** parser tree and adds exactly one level
    per internal node.  SymPy flattens associative operators, so ``a + b + c + d`` is a single
    four-argument ``Add``, and no rule recovers the binary tree that was flattened away.  The
    charge for k > 2 is therefore an assumption about the schedule, and this module makes all
    three assumptions available instead of hiding one of them:

    * ``balanced``   -- ``ceil(log2(k))``, a balanced reduction tree (the default);
    * ``left_chain`` -- ``k - 1``, a fully serial left-leaning chain;
    * ``flat``       -- ``1``, a single k-input operation with no internal levels.

    All three agree at k <= 2, so on any node SymPy keeps binary they coincide with
    ``critical_path`` by construction, and the choice is invisible.  It is only visible on
    flattened nodes, which is exactly where the report measures its sensitivity.
    """
    if convention not in DEPTH_CONVENTIONS:
        raise ValueError(UNKNOWN_CONVENTION_MESSAGE.format(convention=convention))
    if count <= 1:
        return 1
    if convention == "flat":
        return 1
    if convention == "left_chain":
        return count - 1
    return int(ceil(log2(count)))


def _arity_levels(expression: Expr, convention: str = DEFAULT_DEPTH_CONVENTION) -> int:
    """Dependency levels contributed by one node under ``convention``."""
    return _levels_for_arity(len(expression.args), convention)


def _node_kind_counts(expression: Expr) -> dict[str, int]:
    """Operation counts contributed by one node, excluding its children."""
    counts = {kind: 0 for kind in COST_KINDS}
    if not expression.args:
        return counts
    if isinstance(expression, Add):
        counts["add"] += len(expression.args) - 1
        return counts
    if isinstance(expression, Mul):
        arguments = expression.args
        negated = any(argument == Integer(-1) for argument in arguments)
        factors = len(arguments) - 1 if negated else len(arguments)
        if negated:
            counts["neg"] += 1
        counts["mul"] += max(factors - 1, 0)
        return counts
    if isinstance(expression, Pow):
        exponent = expression.exp
        if exponent == Integer(-1):
            counts["div"] += 1
        elif exponent.is_number and exponent.is_negative:
            counts["div"] += 1
            counts["pow"] += 1
        else:
            counts["pow"] += 1
        return counts
    counts["func"] += 1
    return counts


def structural_cost(
    expression: Program | Expr,
    depth_convention: str = DEFAULT_DEPTH_CONVENTION,
) -> dict[str, int]:
    """Operation counts by kind, total operation count, and critical-path depth.

    Depth follows ``critical_path.operation_cost``: a leaf sits at depth 1, so **depth counts
    the leaf level**, and a binary internal node adds one.  A temporary defined by an
    assignment is not a leaf; its depth is the depth of its defining right-hand side, which is
    what makes the reuse axis measurable at all.

    ``depth_convention`` selects the charge for a node SymPy flattened past arity two; see
    ``_levels_for_arity``.  Operation counts do not depend on it, only ``depth`` does.
    """
    if depth_convention not in DEPTH_CONVENTIONS:
        raise ValueError(UNKNOWN_CONVENTION_MESSAGE.format(convention=depth_convention))
    program = as_program(expression)
    environment = dict(program.assignments)
    counts = {kind: 0 for kind in COST_KINDS}
    depth_cache: dict[Symbol, int] = {}

    def walk(node: Expr, accumulate: bool) -> int:
        if isinstance(node, Symbol) and node in environment:
            if node not in depth_cache:
                depth_cache[node] = walk(environment[node], False)
            return depth_cache[node]
        if not node.args:
            return 1
        if accumulate:
            node_counts = _node_kind_counts(node)
            for kind, value in node_counts.items():
                counts[kind] += value
        return max(walk(argument, accumulate) for argument in node.args) + _arity_levels(
            node, depth_convention
        )

    for _, right_hand_side in program.assignments:
        walk(right_hand_side, True)
    depth = walk(program.result, True)
    total = sum(counts.values())
    return {**counts, "total_operations": total, "depth": depth, "assignments": len(program.assignments)}


# ---------------------------------------------------------------------------
# 4. Excluded points, computed the way the project already computes them
# ---------------------------------------------------------------------------


def _denominator_bases(expression: Expr) -> tuple[Expr, ...]:
    """Bases of every ``Pow`` whose exponent is a **numeric negative** number, and nothing else.

    This is the whole recognition rule.  A ``Pow`` with a symbolic exponent is not inspected
    even when that exponent is a division in disguise, and no non-``Pow`` node is inspected at
    all.  ``excluded_points`` documents what that costs.
    """
    bases: list[Expr] = []
    for node in expression.atoms(Pow):
        exponent = node.exp
        if exponent.is_number and exponent.is_negative:
            bases.append(node.base)
    return tuple(sorted(bases, key=lambda item: repr(item)))


def excluded_points(expression: Program | Expr) -> tuple[str, ...]:
    """Points removed from the real domain **by an explicit numeric-exponent division**.

    ``canonical.undefined_terms`` walks the parser tree, finds every division whose divisor is
    not a non-zero literal, and solves that divisor for its first free symbol in name order.
    This is the same rule transposed onto a SymPy tree, where such a division is a ``Pow`` with
    a negative numeric exponent.  A temporary is inlined into the divisor before solving, so a
    reuse candidate is not accused of moving the domain merely because it named a
    subexpression.

    **This is narrower than "the domain", and the difference is not academic.**  Only
    ``Pow(base, negative number)`` is inspected, so the following are invisible to it:

    * radical branch restrictions -- ``Pow(sqrt(x), 2)`` needs ``x >= 0`` and ``x`` does not,
      yet both report no excluded points;
    * logarithmic branch restrictions -- ``log(x)`` needs ``x > 0`` and contributes nothing;
    * symbolic-exponent divisions -- in ``Pow(x, n) * Pow(x, -n)`` the exponent ``-n`` is not a
      number, so ``x = 0`` is never recorded.

    It is also **over-strict** in the opposite direction, because a pole that is not spelled as
    a ``Pow`` is not recognised as a shared restriction: ``sin(x)/cos(x)`` reports the poles of
    ``cos`` and ``tan(x)`` reports none, so that pair is scored as a domain change when the two
    functions in fact have the same domain.

    The corpus of this experiment contains no radical, no logarithm and no symbolic exponent,
    and every division in it is an explicit numeric-exponent ``Pow``, so no reported number
    depends on any of these gaps.  They are recorded because the next corpus may not be so
    convenient; ``tests/test_transformation_axes.py`` pins all three so they cannot drift
    silently.
    """
    program = as_program(expression)
    assignments = program.assignments
    points: list[str] = []
    for component in program.components:
        for base in _denominator_bases(component):
            base = _inline_into(base, assignments)
            if base.is_number:
                if base == 0:
                    points.append("all")
                continue
            variables = sorted(base.free_symbols, key=str)
            if not variables:
                continue
            try:
                solutions = solve(base, variables[0])
            except Exception:  # noqa: BLE001 - an unsolvable divisor is recorded, never hidden
                points.append(f"unsolved:{base}")
                continue
            points.extend(str(solution) for solution in solutions)
    return tuple(dict.fromkeys(points))


# ---------------------------------------------------------------------------
# 5. The proof obligation
# ---------------------------------------------------------------------------


def safe_sample_points(
    variables: Sequence[str] | Sequence[Symbol],
    count: int = NUMERIC_SAMPLE_COUNT,
) -> tuple[dict[Symbol, Rational], ...]:
    """Deterministic non-integer probe assignments of both signs, distinct across variables.

    "Safe" means away from the excluded points of this corpus, not safe for every expression:
    a rational point can still land outside the real domain of a radical or a logarithm, in
    which case ``_numeric_value`` declines that point rather than inventing a value.
    """
    symbols = [item if isinstance(item, Symbol) else Symbol(str(item), real=True) for item in variables]
    samples: list[dict[Symbol, Rational]] = []
    for sample_index in range(count):
        assignment = {}
        for position, symbol in enumerate(symbols):
            assignment[symbol] = _SAMPLE_BASE[(position + sample_index * 5) % len(_SAMPLE_BASE)]
        samples.append(assignment)
    return tuple(samples)


def _numeric_value(expression: Expr, assignment: dict[Symbol, Rational]) -> complex | None:
    try:
        substituted = expression.subs(assignment)
        if substituted.has(zoo) or substituted in (zoo, -zoo):
            return None
        value = complex(substituted.evalf(30))
    except (TypeError, ValueError, ZeroDivisionError, AttributeError):
        return None
    if value != value or abs(value) == float("inf"):  # NaN or infinity
        return None
    return value


def verify_equivalence(
    original: Program | Expr,
    candidate: Program | Expr,
    variables: Sequence[str] | Sequence[Symbol],
) -> dict[str, Any]:
    """Discharge the proof obligation for one candidate rewrite.

    A candidate is admitted as ``equivalent`` only when **both** hold:

    1. ``simplify(original - candidate) == 0``; and
    2. the two representations have the same ``excluded_points`` -- that is, the same set of
       points removed by an **explicit division with a numeric negative exponent**.

    Condition (2) is deliberately not called "the domain is preserved", because it is not.  It
    inspects divisions of that one shape and nothing else, so a rewrite that changes a radical,
    logarithmic or symbolic-exponent restriction passes it while genuinely changing the
    function; conversely a pair that shares a non-``Pow`` pole, such as ``sin(x)/cos(x)``
    against ``tan(x)``, fails it while genuinely being equal.  ``excluded_points`` names all
    three gaps and the test suite pins them.  What this function guarantees is exactly (1) and
    (2), and the report states its results in those terms.

    A rewrite that satisfies (1) but not (2) has removed a division restriction -- the
    ``x/x -> 1`` failure mode -- and is classified ``domain_violating``.  That is a rejection
    and is counted separately; it is never a win and never folded into the equivalent count.

    ``unsound`` means the residual was not proven zero.  That covers both a refuted candidate
    and one whose residual SymPy could not discharge; the two are distinguished by the
    ``unprovable`` flag rather than by silently dropping the second case, because a candidate
    that cannot be proven equal must not be admitted either way.

    A numeric probe at deterministic sample points of **both signs** runs as an independent
    check.  It cannot see a domain violation -- ``x/x`` and ``1`` agree at every point where
    both are defined, which is the whole reason condition (2) exists -- so its verdict is
    recorded, and any disagreement with the symbolic verdict is flagged, not used to overrule
    it.  The signs matter: on a positive-only sample set the probe would report ``sqrt(x*x)``
    and ``x`` as agreeing and so contradict the correct symbolic verdict.
    """
    original_program = as_program(original)
    candidate_program = as_program(candidate)
    original_expression = inline(original_program)
    candidate_expression = inline(candidate_program)

    unprovable = False
    try:
        residual = simplify(original_expression - candidate_expression)
        symbolic_equal = residual == 0
    except Exception as error:  # noqa: BLE001 - an undischargeable residual is not an admission
        residual = f"unprovable: {type(error).__name__}"
        symbolic_equal = False
        unprovable = True

    original_excluded = excluded_points(original_program)
    candidate_excluded = excluded_points(candidate_program)
    domain_preserved = set(original_excluded) == set(candidate_excluded)

    samples = safe_sample_points(variables)
    checked = 0
    deviation = 0.0
    for assignment in samples:
        left = _numeric_value(original_expression, assignment)
        right = _numeric_value(candidate_expression, assignment)
        if left is None or right is None:
            continue
        checked += 1
        deviation = max(deviation, abs(left - right))
    numeric_equal = None if checked == 0 else deviation <= NUMERIC_TOLERANCE

    if not symbolic_equal:
        verdict = "unsound"
    elif not domain_preserved:
        verdict = "domain_violating"
    else:
        verdict = "equivalent"

    return {
        "verdict": verdict,
        "symbolic_equal": symbolic_equal,
        "unprovable": unprovable,
        "residual": str(residual),
        "domain_preserved": domain_preserved,
        "excluded_original": list(original_excluded),
        "excluded_candidate": list(candidate_excluded),
        "numeric_points_checked": checked,
        "numeric_equal": numeric_equal,
        "max_numeric_deviation": deviation if checked else None,
        "symbolic_numeric_disagreement": bool(numeric_equal is not None and numeric_equal != symbolic_equal),
    }


# ---------------------------------------------------------------------------
# 6. Candidate generation, one axis at a time
# ---------------------------------------------------------------------------


def _bounded_sites(expression: Expr, max_depth: int) -> tuple[tuple[tuple[int, ...], Expr], ...]:
    """Every distinct non-atomic subexpression at position depth <= ``max_depth``, with its path.

    The path is kept because a rewrite is not always allowed to survive ``xreplace``: SymPy
    re-evaluates the parent, and ``Add.flatten`` will happily collapse ``a + a`` back to ``2*a``
    on the way out.  Keeping the path lets the caller rebuild only the ancestor chain when that
    happens, instead of losing the candidate.
    """
    seen: dict[str, tuple[tuple[int, ...], Expr]] = {}

    def walk(node: Expr, level: int, path: tuple[int, ...]) -> None:
        if level > max_depth or not node.args:
            return
        seen.setdefault(srepr(node), (path, node))
        for index, argument in enumerate(node.args):
            walk(argument, level + 1, path + (index,))

    walk(expression, 0, ())
    return tuple(seen.values())


def _bounded_subexpressions(expression: Expr, max_depth: int) -> tuple[Expr, ...]:
    """Every distinct non-atomic subexpression whose position depth is at most ``max_depth``."""
    return tuple(node for _, node in _bounded_sites(expression, max_depth))


def _rebuild_along_path(node: Expr, path: tuple[int, ...], rewrite: Expr) -> Expr:
    """Replace the subexpression at ``path``, rebuilding only the ancestors, unevaluated.

    This is the escape hatch for rewrites SymPy's canonicalisation would otherwise undo.  Only
    the nodes on the path are reconstructed and each keeps its own arguments in their own
    order, so nothing outside the rewrite site changes shape.
    """
    if not path:
        return rewrite
    arguments = list(node.args)
    arguments[path[0]] = _rebuild_along_path(arguments[path[0]], path[1:], rewrite)
    try:
        return node.func(*arguments, evaluate=False)
    except TypeError:
        return node.func(*arguments)


def _flip_sum(expression: Add) -> Expr:
    return Add(*[-term for term in expression.args])


def _split_two_factors(expression: Mul) -> tuple[Integer | Rational, Expr, Expr] | None:
    coefficient, factors = expression.as_coeff_mul()
    if len(factors) < 2:
        return None
    first = factors[0]
    second = Mul(*factors[1:]) if len(factors) > 2 else factors[1]
    return coefficient, first, second


def _square_trade_rewrites(node: Expr) -> list[Expr]:
    rewrites: list[Expr] = []
    if isinstance(node, Mul):
        split = _split_two_factors(node)
        if split is not None:
            coefficient, first, second = split
            product_free = (first + second) ** 2 - first**2 - second**2
            if coefficient == 2:
                rewrites.append(product_free)
            else:
                rewrites.append(coefficient * product_free / 2)
                rewrites.append(coefficient * ((first + second) ** 2 - (first - second) ** 2) / 4)
    if isinstance(node, Add) and len(node.args) == 2:
        left, right = node.args
        for positive, negative in ((left, right), (right, left)):
            if not (isinstance(positive, Pow) and positive.exp == 2):
                continue
            negated = -negative
            if isinstance(negated, Pow) and negated.exp == 2:
                rewrites.append((positive.base - negated.base) * (positive.base + negated.base))
    if isinstance(node, Add):
        factored = factor(node)
        if isinstance(factored, Pow) and factored.exp == 2:
            rewrites.append(factored)
    return rewrites


def _sign_placement_rewrites(node: Expr) -> list[Expr]:
    rewrites: list[Expr] = []
    if isinstance(node, Mul):
        arguments = list(node.args)
        for index, argument in enumerate(arguments):
            if isinstance(argument, Add):
                replacement, sign = _flip_sum(argument), Integer(-1)
            elif isinstance(argument, Pow) and isinstance(argument.base, Add) and argument.exp.is_Integer:
                replacement = Pow(_flip_sum(argument.base), argument.exp)
                sign = Integer(-1) if int(argument.exp) % 2 else Integer(1)
            else:
                continue
            rebuilt = list(arguments)
            rebuilt[index] = replacement
            evaluated = Mul(sign, *rebuilt)
            if evaluated != node:
                rewrites.append(evaluated)
                continue
            unevaluated = Mul(sign, *rebuilt, evaluate=False)
            if unevaluated != node:
                rewrites.append(unevaluated)
    if isinstance(node, Add):
        hoisted = Mul(Integer(-1), _flip_sum(node), evaluate=False)
        if hoisted != node:
            rewrites.append(hoisted)
    return rewrites


def _algebraic_rewrites(node: Expr) -> list[Expr]:
    rewrites: list[Expr] = []
    for rewriter in (factor, expand, factor_terms, together, cancel):
        try:
            rewrites.append(rewriter(node))
        except Exception:  # noqa: BLE001 - a rewriter that does not apply contributes nothing
            continue
    for symbol in sorted(node.free_symbols, key=str):
        try:
            rewrites.append(sympy_collect(expand(node), symbol))
        except Exception:  # noqa: BLE001
            continue
    return rewrites


def _operation_fusion_rewrites(node: Expr) -> list[Expr]:
    rewrites: list[Expr] = []
    if not isinstance(node, Mul):
        return rewrites
    coefficient, factors = node.as_coeff_mul()
    if not (coefficient.is_Integer and abs(coefficient) > 1 and factors):
        return rewrites
    # A negative integer multiple decomposes exactly like its magnitude, with the sign carried
    # into the repeated term: -4*a*c becomes (-a*c) + (-a*c) + (-a*c) + (-a*c).
    rest = Mul(*factors) if coefficient > 0 else -Mul(*factors)
    multiple = int(abs(coefficient))
    if multiple <= 4:
        rewrites.append(Add(*([rest] * multiple), evaluate=False))
    if multiple >= 3:
        rewrites.append(Add(Mul(Integer(multiple - 1), rest), rest, evaluate=False))
    for divisor in range(2, multiple):
        if multiple % divisor == 0:
            rewrites.append(
                Mul(Integer(divisor), Mul(Integer(multiple // divisor), rest, evaluate=False), evaluate=False)
            )
            break
    return rewrites


_SUBEXPRESSION_RULES = {
    "mul_square_trade": _square_trade_rewrites,
    "sign_placement": _sign_placement_rewrites,
    "algebraic_rewrite": _algebraic_rewrites,
    "operation_fusion": _operation_fusion_rewrites,
}


def _normalize_temporaries(program: Program) -> Program:
    """Rename temporaries to ``_t0, _t1, ...`` so two spellings of one program dedup as one.

    ``cse`` names its temporaries ``x0``; the frequency-based hoist names its own.  Without
    this the same reuse program would be counted twice, and a candidate count that
    double-counts is not a measurement.
    """
    if not program.assignments:
        return program
    mapping: dict[Symbol, Symbol] = {}
    assignments: list[tuple[Symbol, Expr]] = []
    for index, (name, right_hand_side) in enumerate(program.assignments):
        fresh = Symbol(f"_t{index}")
        assignments.append((fresh, right_hand_side.xreplace(mapping)))
        mapping[name] = fresh
    return Program(tuple(assignments), program.result.xreplace(mapping))


def _reuse_candidates(expression: Expr, max_depth: int) -> list[Program]:
    programs: list[Program] = []
    try:
        replacements, reduced = cse([expression])
    except Exception:  # noqa: BLE001
        replacements, reduced = [], [expression]
    if replacements:
        programs.append(Program(tuple((symbol, value) for symbol, value in replacements), reduced[0]))
    repeated: list[tuple[int, str, Expr]] = []
    for node in _bounded_subexpressions(expression, max_depth + 2):
        if node == expression or not node.args:
            continue
        occurrences = expression.count(node)
        if occurrences >= 2:
            repeated.append((occurrences, srepr(node), node))
    for _, _, node in sorted(repeated, key=lambda item: (-item[0], item[1])):
        temporary = Symbol("t0")
        reduced_result = expression.xreplace({node: temporary})
        if temporary in reduced_result.free_symbols:
            programs.append(Program(((temporary, node),), reduced_result))
    return programs


def generate_candidates(
    expression: Program | Expr,
    axis: str,
    max_depth: int = DEFAULT_MAX_DEPTH,
    limit: int = DEFAULT_CANDIDATE_LIMIT,
) -> tuple[Program, ...]:
    """Apply one axis exhaustively at bounded depth and return the distinct rewrites.

    Every candidate is a ``Program`` and every candidate differs structurally from the input.
    An axis that has no applicable site returns an empty tuple; that is a measurement, not an
    error, and it is exactly how an inert axis is recorded.
    """
    if axis not in AXIS_DEFINITIONS:
        raise ValueError(UNKNOWN_AXIS_MESSAGE.format(axis=axis))
    source = inline(expression)
    original_key = as_program(expression).key()
    collected: dict[str, Program] = {}

    if axis == "common_subexpression_reuse":
        produced = _reuse_candidates(source, max_depth)
    else:
        rule = _SUBEXPRESSION_RULES[axis]
        produced = []
        source_key = srepr(source)
        for path, node in _bounded_sites(source, max_depth):
            try:
                rewrites = rule(node)
            except Exception:  # noqa: BLE001 - a rule that fails on a node yields nothing there
                continue
            for rewrite in rewrites:
                if rewrite == node:
                    continue
                try:
                    replaced = rewrite if not path else source.xreplace({node: rewrite})
                    if srepr(replaced) == source_key:
                        # SymPy re-evaluated the parent and undid the rewrite; keep the
                        # candidate by rebuilding only the ancestor chain.
                        replaced = _rebuild_along_path(source, path, rewrite)
                except Exception:  # noqa: BLE001
                    continue
                produced.append(Program((), replaced))

    for program in produced:
        program = _normalize_temporaries(program)
        key = program.key()
        if key == original_key or key in collected:
            continue
        collected[key] = program
        if len(collected) >= limit:
            break
    return tuple(collected.values())


# ---------------------------------------------------------------------------
# 7. The corpus, reproducible from the report alone
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AxisFormula:
    id: str
    domain: str
    name: str
    expression: str
    variables: tuple[str, ...]


CORPUS: tuple[AxisFormula, ...] = (
    # quadratic_equations
    AxisFormula("q_discriminant", "quadratic_equations", "discriminant", "b**2 - 4*a*c", ("a", "b", "c")),
    AxisFormula("q_vertex_x", "quadratic_equations", "vertex abscissa", "-b/(2*a)", ("a", "b")),
    AxisFormula("q_vertex_y", "quadratic_equations", "vertex ordinate", "c - b**2/(4*a)", ("a", "b", "c")),
    AxisFormula("q_standard_form", "quadratic_equations", "standard form", "a*x**2 + b*x + c", ("a", "b", "c", "x")),
    AxisFormula(
        "q_completed_square", "quadratic_equations", "completed square",
        "a*(x + b/(2*a))**2 + c - b**2/(4*a)", ("a", "b", "c", "x"),
    ),
    # geometry
    AxisFormula(
        "g_squared_distance", "geometry", "squared planar distance",
        "(x2 - x1)**2 + (y2 - y1)**2", ("x1", "x2", "y1", "y2"),
    ),
    AxisFormula(
        "g_shoelace_area", "geometry", "shoelace triangle area",
        "(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))/2", ("x1", "x2", "x3", "y1", "y2", "y3"),
    ),
    AxisFormula("g_rotation_x", "geometry", "rotation abscissa", "x*cos(t) - y*sin(t)", ("x", "y", "t")),
    AxisFormula("g_rotation_y", "geometry", "rotation ordinate", "x*sin(t) + y*cos(t)", ("x", "y", "t")),
    AxisFormula("g_dot_product", "geometry", "planar dot product", "x1*x2 + y1*y2", ("x1", "x2", "y1", "y2")),
    # algebra
    AxisFormula("a_binomial_square", "algebra", "binomial square", "(a + b)**2", ("a", "b")),
    AxisFormula("a_binomial_cube", "algebra", "binomial cube", "(a + b)**3", ("a", "b")),
    AxisFormula("a_difference_of_squares", "algebra", "difference of squares", "a**2 - b**2", ("a", "b")),
    AxisFormula("a_common_factor", "algebra", "common factor", "a*b + a*c", ("a", "b", "c")),
    AxisFormula(
        "a_cancelling_quotient", "algebra", "cancelling quotient",
        "(a**2 - b**2)/(a - b)", ("a", "b"),
    ),
    # calculus
    AxisFormula(
        "c_cubic_derivative", "calculus", "cubic derivative",
        "3*a*x**2 + 2*b*x + c", ("a", "b", "c", "x"),
    ),
    AxisFormula("c_product_rule", "calculus", "product rule", "u*dv + v*du", ("u", "v", "du", "dv")),
    AxisFormula(
        "c_quotient_rule", "calculus", "quotient rule",
        "(v*du - u*dv)/v**2", ("u", "v", "du", "dv"),
    ),
    AxisFormula(
        "c_taylor_second_order", "calculus", "second-order Taylor coefficients",
        "f0 + f1*h + f2*h**2/2", ("f0", "f1", "f2", "h"),
    ),
    AxisFormula("c_chain_rule", "calculus", "chain rule", "2*x*cos(x**2)", ("x",)),
    # trigonometry
    AxisFormula(
        "t_angle_sum_sin", "trigonometry", "sine angle sum",
        "sin(a)*cos(b) + cos(a)*sin(b)", ("a", "b"),
    ),
    AxisFormula("t_double_angle_cos", "trigonometry", "cosine double angle", "cos(x)**2 - sin(x)**2", ("x",)),
    AxisFormula("t_double_angle_sin", "trigonometry", "sine double angle", "2*sin(x)*cos(x)", ("x",)),
    AxisFormula("t_pythagorean", "trigonometry", "Pythagorean identity", "sin(x)**2 + cos(x)**2", ("x",)),
    AxisFormula("t_tangent_quotient", "trigonometry", "tangent as a quotient", "sin(x)/cos(x)", ("x",)),
    # number_theory
    AxisFormula("n_triangular", "number_theory", "triangular number", "n*(n + 1)/2", ("n",)),
    AxisFormula("n_cubic_minus_linear", "number_theory", "n**3 - n", "n**3 - n", ("n",)),
    AxisFormula("n_odd_gap", "number_theory", "consecutive square gap", "(n + 1)**2 - n**2", ("n",)),
    AxisFormula(
        "n_consecutive_product", "number_theory", "product of three consecutive integers",
        "n*(n + 1)*(n + 2)", ("n",),
    ),
    AxisFormula(
        "n_two_squares_product", "number_theory", "Brahmagupta-Fibonacci left side",
        "(a**2 + b**2)*(c**2 + d**2)", ("a", "b", "c", "d"),
    ),
    # differential_equations
    AxisFormula(
        "d_harmonic_solution", "differential_equations", "harmonic solution",
        "A*cos(w*t) + B*sin(w*t)", ("A", "B", "w", "t"),
    ),
    AxisFormula(
        "d_harmonic_energy", "differential_equations", "harmonic energy",
        "(v**2 + w**2*x**2)/2", ("v", "w", "x"),
    ),
    AxisFormula(
        "d_logistic_rhs", "differential_equations", "logistic right-hand side",
        "r*y*(1 - y/K)", ("r", "y", "K"),
    ),
    AxisFormula(
        "d_logistic_solution", "differential_equations", "logistic closed form",
        "K/(1 + ((K - y0)/y0)*exp(-r*t))", ("K", "y0", "r", "t"),
    ),
    AxisFormula(
        "d_damped_oscillator", "differential_equations", "damped oscillator",
        "A*exp(-c*t)*cos(w*t)", ("A", "c", "t", "w"),
    ),
    # probability_statistics
    AxisFormula(
        "p_binomial_pmf", "probability_statistics", "Binomial(3, p) two-success PMF",
        "3*p**2*(1 - p)", ("p",),
    ),
    AxisFormula(
        "p_binomial_variance", "probability_statistics", "binomial variance",
        "n*p*(1 - p)", ("n", "p"),
    ),
    AxisFormula(
        "p_normal_exponent", "probability_statistics", "normal density exponent",
        "-(x - m)**2/(2*s**2)", ("x", "m", "s"),
    ),
    AxisFormula(
        "p_variance_identity", "probability_statistics", "variance from raw moments",
        "e2 - e1**2", ("e1", "e2"),
    ),
    AxisFormula("p_z_score", "probability_statistics", "z score", "(x - m)/s", ("x", "m", "s")),
)

DOMAINS: tuple[str, ...] = tuple(dict.fromkeys(formula.domain for formula in CORPUS))


def parse_formula(formula: AxisFormula) -> Expr:
    """Parse one corpus entry with real symbols, matching ``canonical.to_sympy``."""
    locals_map = {name: Symbol(name, real=True) for name in formula.variables}
    return sympify(formula.expression, locals=locals_map)


# ---------------------------------------------------------------------------
# 8. Rank correlation, implemented here because the project has no SciPy dependency
# ---------------------------------------------------------------------------


def _sign(value: int) -> int:
    return (value > 0) - (value < 0)


def _average_ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while end + 1 < len(order) and values[order[end + 1]] == values[order[position]]:
            end += 1
        shared = (position + end) / 2 + 1
        for index in range(position, end + 1):
            ranks[order[index]] = shared
        position = end + 1
    return ranks


def spearman_rank_correlation(left: Sequence[float], right: Sequence[float]) -> float | None:
    """Spearman rho with average ranks for ties; ``None`` when it is undefined."""
    if len(left) != len(right) or len(left) < 2:
        return None
    left_ranks, right_ranks = _average_ranks(left), _average_ranks(right)
    count = len(left_ranks)
    mean_left = sum(left_ranks) / count
    mean_right = sum(right_ranks) / count
    covariance = sum((a - mean_left) * (b - mean_right) for a, b in zip(left_ranks, right_ranks))
    variance_left = sum((a - mean_left) ** 2 for a in left_ranks)
    variance_right = sum((b - mean_right) ** 2 for b in right_ranks)
    if variance_left == 0 or variance_right == 0:
        return None
    return covariance / (variance_left * variance_right) ** 0.5


# ---------------------------------------------------------------------------
# 9. The per-formula unit of work, and the pool that runs it
# ---------------------------------------------------------------------------


def _empty_cell() -> dict[str, Any]:
    """One counter cell.  The three verdict counters come from ``VERDICTS`` so that adding a
    verdict without adding its counter is impossible: ``candidates`` must always equal their
    sum, and the test suite asserts exactly that."""
    return {
        "candidates": 0,
        **{verdict: 0 for verdict in VERDICTS},
        "unprovable": 0,
        "reduces_operations": 0,
        "reduces_depth": 0,
        "reduces_both": 0,
        "reduces_depth_only": 0,
        "symbolic_numeric_disagreements": 0,
        "kind_deltas": {kind: 0 for kind in COST_KINDS},
    }


def _merge_cell(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key, value in source.items():
        if key == "kind_deltas":
            for kind, amount in value.items():
                target["kind_deltas"][kind] += amount
        elif key in target and isinstance(value, int):
            target[key] += value


def evaluate_formula_axis(
    formula: AxisFormula,
    axis: str,
    depth_convention: str = DEFAULT_DEPTH_CONVENTION,
) -> dict[str, Any]:
    """Generate, verify and cost every candidate for one (formula, axis) pair.

    ``depth_convention`` reaches only ``structural_cost``.  Candidate generation and the proof
    obligation do not read it, so the candidate and verdict counts are identical under every
    convention and only the depth deltas move.
    """
    expression = parse_formula(formula)
    baseline = structural_cost(expression, depth_convention)
    cell = _empty_cell()
    deltas: list[tuple[int, int]] = []
    examples: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []
    for candidate in generate_candidates(expression, axis):
        cell["candidates"] += 1
        verdict = verify_equivalence(expression, candidate, formula.variables)
        cell[verdict["verdict"]] += 1
        if verdict["unprovable"]:
            cell["unprovable"] += 1
        if verdict["symbolic_numeric_disagreement"]:
            cell["symbolic_numeric_disagreements"] += 1
            examples.append(
                {
                    "kind": "symbolic_numeric_disagreement",
                    "formula": formula.id,
                    "axis": axis,
                    "candidate": as_program(candidate).render(),
                    "residual": verdict["residual"],
                }
            )
        if verdict["verdict"] == "domain_violating":
            examples.append(
                {
                    "kind": "domain_violating",
                    "formula": formula.id,
                    "axis": axis,
                    "original": str(expression),
                    "candidate": as_program(candidate).render(),
                    "excluded_original": verdict["excluded_original"],
                    "excluded_candidate": verdict["excluded_candidate"],
                }
            )
            continue
        if verdict["verdict"] != "equivalent":
            continue
        cost = structural_cost(candidate, depth_convention)
        operation_delta = cost["total_operations"] - baseline["total_operations"]
        depth_delta = cost["depth"] - baseline["depth"]
        deltas.append((operation_delta, depth_delta))
        for kind in COST_KINDS:
            cell["kind_deltas"][kind] += cost[kind] - baseline[kind]
        if operation_delta < 0:
            cell["reduces_operations"] += 1
        if depth_delta < 0:
            cell["reduces_depth"] += 1
        if operation_delta < 0 and depth_delta < 0:
            cell["reduces_both"] += 1
        if depth_delta < 0 <= operation_delta:
            cell["reduces_depth_only"] += 1
        if operation_delta < 0 or depth_delta < 0:
            improvements.append(
                {
                    "formula": formula.id,
                    "domain": formula.domain,
                    "axis": axis,
                    "before": str(expression),
                    "after": as_program(candidate).render(),
                    "operation_delta": operation_delta,
                    "depth_delta": depth_delta,
                    "operations_before": baseline["total_operations"],
                    "operations_after": cost["total_operations"],
                    "depth_before": baseline["depth"],
                    "depth_after": cost["depth"],
                }
            )
    return {
        "formula": formula.id,
        "domain": formula.domain,
        "axis": axis,
        "baseline_cost": baseline,
        "cell": cell,
        "deltas": deltas,
        "examples": examples,
        "improvements": improvements,
    }


def _pool_task(payload: tuple[str, str, str, str, tuple[str, ...], str, str]) -> dict[str, Any]:
    """Module-level pool entry point: required by the Windows ``spawn`` start method."""
    identifier, domain, name, expression, variables, axis, depth_convention = payload
    return evaluate_formula_axis(
        AxisFormula(identifier, domain, name, expression, variables), axis, depth_convention
    )


WORKER_HEADROOM_CORES = 2
WORKER_CAP = 12


def worker_count_for(cores: int) -> int:
    """Worker count for a machine with ``cores`` cores.

    ``WORKER_HEADROOM_CORES`` cores are left free so a full corpus sweep cannot starve an
    interactive session, and ``WORKER_CAP`` bounds the count so an unusually wide machine does
    not pay more spawn cost than a 200-task corpus can amortise.  The result is never zero and
    never exceeds the core count, which is what makes it safe to call on any machine.
    """
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP))


def default_worker_count() -> int:
    """Worker count derived from the **observed** core count, never a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1)


def axis_yield_report(
    corpus: Iterable[AxisFormula] | None = None,
    workers: int | None = None,
    depth_convention: str = DEFAULT_DEPTH_CONVENTION,
) -> dict[str, Any]:
    """Per-domain and per-axis yield of the five equivalence-preserving axes.

    ``workers=1`` forces the sequential path.  ``workers=None`` uses ``DEFAULT_WORKERS``, whose
    value is set from the measurement recorded in the experiment report rather than from a
    rule of thumb.  Parallelism changes only how fast the sweep runs: ``executor.map``
    preserves input order, every task is a pure function of its payload, and the sequential and
    parallel reports are asserted identical by the test suite.

    ``depth_convention`` selects the depth charge for flattened n-ary nodes.  Re-running the
    sweep under each of ``DEPTH_CONVENTIONS`` is how the report measures how much of its
    headline is convention and how much is corpus; the candidate and verdict counts are
    invariant under that choice and only the depth-derived figures move.
    """
    formulas = tuple(corpus) if corpus is not None else CORPUS
    if not formulas:
        raise ValueError("axis_yield_report needs at least one formula: an empty corpus measures nothing")
    if depth_convention not in DEPTH_CONVENTIONS:
        raise ValueError(UNKNOWN_CONVENTION_MESSAGE.format(convention=depth_convention))
    resolved = DEFAULT_WORKERS if workers is None else workers
    payloads = [
        (
            formula.id, formula.domain, formula.name, formula.expression, formula.variables,
            axis, depth_convention,
        )
        for formula in formulas
        for axis in AXES
    ]
    if resolved <= 1:
        execution = "sequential"
        results = [_pool_task(payload) for payload in payloads]
    else:
        execution = "parallel"
        with ProcessPoolExecutor(max_workers=resolved) as executor:
            results = list(executor.map(_pool_task, payloads, chunksize=1))

    domains = tuple(dict.fromkeys(formula.domain for formula in formulas))
    per_pair: dict[str, dict[str, Any]] = {}
    per_axis = {axis: _empty_cell() for axis in AXES}
    per_domain = {domain: _empty_cell() for domain in domains}
    totals = _empty_cell()
    operation_deltas: list[int] = []
    depth_deltas: list[int] = []
    axis_deltas: dict[str, list[tuple[int, int]]] = {axis: [] for axis in AXES}
    examples: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []
    agreement: dict[str, int] = {}

    for result in results:
        key = f"{result['domain']}|{result['axis']}"
        cell = per_pair.setdefault(key, _empty_cell())
        _merge_cell(cell, result["cell"])
        _merge_cell(per_axis[result["axis"]], result["cell"])
        _merge_cell(per_domain[result["domain"]], result["cell"])
        _merge_cell(totals, result["cell"])
        for operation_delta, depth_delta in result["deltas"]:
            operation_deltas.append(operation_delta)
            depth_deltas.append(depth_delta)
            axis_deltas[result["axis"]].append((operation_delta, depth_delta))
            bucket = f"{_sign(operation_delta):+d}/{_sign(depth_delta):+d}"
            agreement[bucket] = agreement.get(bucket, 0) + 1
        examples.extend(result["examples"])
        improvements.extend(result["improvements"])

    correlation = spearman_rank_correlation(operation_deltas, depth_deltas)
    disagreements = sum(
        count for bucket, count in agreement.items()
        if bucket.split("/")[0] != bucket.split("/")[1]
    )
    return {
        "formula_count": len(formulas),
        "axis_count": len(AXES),
        "domains": list(domains),
        "axes": list(AXES),
        "depth_convention": depth_convention,
        "execution": execution,
        "workers": resolved,
        "per_formula_axis": [
            {"formula": item["formula"], "domain": item["domain"], "axis": item["axis"], **item["cell"]}
            for item in results
        ],
        "per_domain_axis": {key: value for key, value in sorted(per_pair.items())},
        "per_axis": per_axis,
        "per_domain": per_domain,
        "totals": totals,
        "operation_depth_correlation": correlation,
        "per_axis_correlation": {
            axis: spearman_rank_correlation([item[0] for item in pairs], [item[1] for item in pairs])
            for axis, pairs in axis_deltas.items()
        },
        "correlated_pairs": len(operation_deltas),
        "delta_agreement": dict(sorted(agreement.items())),
        "metric_disagreements": disagreements,
        "depth_reduced_without_operation_reduction": totals["reduces_depth_only"],
        "inert_axes": sorted(axis for axis in AXES if per_axis[axis]["candidates"] == 0),
        "zero_yield_axes": sorted(axis for axis in AXES if per_axis[axis]["equivalent"] == 0),
        "examples": examples,
        "improvements": sorted(
            improvements, key=lambda item: (item["operation_delta"] + item["depth_delta"], item["formula"])
        ),
    }


def depth_convention_sensitivity(
    corpus: Iterable[AxisFormula] | None = None,
    workers: int | None = None,
) -> dict[str, dict[str, Any]]:
    """Re-run the whole sweep once per depth convention and report which figures move.

    The headline of this experiment is a count of depth-reducing candidates that an
    operation-count model cannot see.  That count is stated in units the n-ary depth charge
    partly sets, so publishing one value of it without this table would present a convention as
    a measurement.  What this function shows is which conclusions are invariant: the candidate
    and verdict counts do not move at all, the invisible set is non-empty under every
    convention, and the rank correlation is far from 1 under every convention -- while the
    specific count is convention-dependent to within about a factor of three.
    """
    sensitivity: dict[str, dict[str, Any]] = {}
    for convention in DEPTH_CONVENTIONS:
        report = axis_yield_report(corpus, workers=workers, depth_convention=convention)
        totals = report["totals"]
        sensitivity[convention] = {
            "candidates": totals["candidates"],
            "equivalent": totals["equivalent"],
            "domain_violating": totals["domain_violating"],
            "unsound": totals["unsound"],
            "reduces_operations": totals["reduces_operations"],
            "reduces_depth": totals["reduces_depth"],
            "reduces_both": totals["reduces_both"],
            "depth_reduced_without_operation_reduction": totals["reduces_depth_only"],
            "operation_depth_correlation": report["operation_depth_correlation"],
            "metric_disagreements": report["metric_disagreements"],
        }
    return sensitivity


# Measured on the 16-core machine of experiment 0026 over the 40-formula corpus, seven
# alternating runs each: sequential median 6.26 s against 3.43 s with 12 workers, a 1.83x
# reduction, so the parallel path is the default.  ``workers=1`` reproduces the sequential path
# exactly: the test suite asserts that the two reports are identical apart from the two fields
# that name the execution mode.  This is a measurement of the analysis harness and of nothing
# else; it is not, and must never be read as, a cost measurement of the formulas themselves.
DEFAULT_WORKERS = default_worker_count()
