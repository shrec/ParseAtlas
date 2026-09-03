"""Direction B: what does a fixed mathematical object COST to WRITE under each grammar?

Experiment 0034, and the first experiment of the programme the roadmap calls *direction B*.

Experiments 0001-0033 all run direction A: they fix a token STRING and ask what it MEANS under
each of the 25 grammars. That is not the founding question. The founding question - *what
mathematics would we have today if humans had agreed on different operator precedence?* - fixes a
mathematical OBJECT and asks what it costs to WRITE. This module inverts the pipeline:

.. code-block:: text

    direction A   source string  --parse(g)-->   tree_g            (0001..0033)
    direction B   intended tree  --render(g)-->  string, cost_g    (this module)

The intended tree is the datum. :func:`render` writes it under a grammar inserting ONLY the
brackets that grammar requires, :func:`parenthesis_cost` counts them, and everything else in the
file is bookkeeping over those two functions.

The bracket rule is DERIVED from the parser, not restated as a table
--------------------------------------------------------------------

:class:`parseatlas.parser.Parser` is a precedence-climbing parser. Its entire associativity
behaviour is two lines of :meth:`~parseatlas.parser.Parser._expression`::

    while self._current.kind == "operator" and self._powers[self._current.value] >= minimum_power:
        left = Binary(operator, left, self._expression(self._powers[operator] + 1))

Read off the two thresholds directly:

* the loop continues at ``>= minimum_power``, so an operator is absorbed at the CURRENT level when
  its power is at least the level's threshold;
* the right operand is parsed at ``power(operator) + 1``, so the right recursion refuses anything
  binding as loosely as the operator itself.

:func:`child_threshold` is those two numbers and nothing else: ``parent_power`` on the left,
``parent_power + 1`` on the right. A child needs brackets exactly when its own power falls below
its threshold. Nothing in this file names ``*`` or ``+`` or hardcodes a precedence order; the
powers come from :attr:`parseatlas.grammar.Grammar.levels` via :func:`binding_powers`, which is why
the rule also holds for the tied control grammar ``G0`` where ``*`` and ``/`` share a level and
``power("*") == power("/")`` makes ``a * b / c`` free while ``a / (b * c)`` is not.

The left threshold deserves one line of justification, because ``parent_power`` (rather than the
level's own inherited minimum) looks too strong at first sight. A left child ``Binary(lop, ...)``
is the accumulated ``left`` of the same ``_expression`` call, so it must survive two conditions:
``power(lop) >= minimum_power`` to be absorbed at all, and ``power(op) < power(lop) + 1`` so that
the child's OWN right recursion does not swallow the parent's operator. The second is the binding
one - it says ``power(lop) >= power(op)`` - and it implies the first, because a node only sits at a
level with ``power(op) >= minimum_power``. So ``parent_power`` is the correct left threshold and
the inherited minimum never has to be threaded through the recursion.

The correctness bridge
----------------------

Every cost number in this file is meaningless unless the rendering actually denotes the tree it
came from. :func:`render` therefore reparses its own output and raises :class:`RoundTripError`
when ``parse(render(tree, g), g) != tree``. That check is ON by default and is not test-only;
:func:`round_trip_audit` re-runs it as an independent count for the report.

Minimality is the second half of the contract: a rendering that adds a bracket the grammar does not
require would inflate exactly the quantity being measured. :func:`minimality_audit` verifies it by
construction rather than by argument - it deletes each bracket pair in turn and requires the result
to reparse differently (or fail to parse).

The corpus
----------

:data:`CORPUS` is named mathematics - the distributive law, the binomial square, a slope, a z-score,
kinetic energy - not a coefficient sweep. Each formula is recorded as its conventional-notation
source string and its intended tree is obtained by parsing that string under ``G0``, since ``G0``
IS, by definition, how mathematics is written today. ``render(tree, G0) == source`` for every entry
(pinned by :func:`corpus_audit` and by the test suite), which is what makes the corpus auditable:
the source strings carry no redundant brackets and no hidden intent.

The null model
--------------

Part of every cost difference is forced rather than chosen. A formula whose cost is the same under
all 25 grammars cannot rank them; it only adds a constant to every total. :func:`null_model`
separates the forced floor from the movable remainder and re-ranks on the movable subcorpus alone,
so a ranking driven by immovable formulas is visible as such rather than reported as a finding.
"""

import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

from .grammar import Grammar, all_grammars
from .parser import Binary, Node, Number, Variable, parse

#: The 25 registered grammars: the tied-level control ``G0`` plus the 24 strict orderings.
GRAMMARS: tuple[Grammar, ...] = all_grammars()

#: The conventional grammar. ``G0`` is not "one of the 25" for this experiment's purposes - it is
#: the notation the corpus is written in, and the baseline every other grammar is priced against.
CONTROL: Grammar = GRAMMARS[0]

#: Below this many formulas a process pool costs more than the work it distributes. The value is a
#: floor for the *decision*, not a hardcoded worker count; see :func:`resolve_worker_count`.
PARALLEL_MINIMUM_ITEMS: int = 256


class RoundTripError(ValueError):
    """A rendering did not reparse to the tree it was rendered from.

    This is the load-bearing failure of the experiment: if it is ever raised, every cost number
    computed alongside it is void.
    """


@dataclass(frozen=True)
class Formula:
    """One named piece of mathematics.

    ``source`` is the formula as it is conventionally written, in the Generation 1 language
    (binary ``+ - * /``, integer literals, named variables). The intended tree is
    ``parse(source, G0)``; ``G0`` is the control grammar precisely because it is today's notation.
    """

    name: str
    area: str
    source: str


# --------------------------------------------------------------------------------------- corpus
#
# Real mathematics, entered as it is written. Sources are in the canonical spacing this module
# renders in (single spaces around binary operators, none inside brackets) so that
# ``render(tree, G0) == source`` is a meaningful equality and not a formatting accident.
#
# Language limits that shaped a few of the entries, stated here rather than hidden:
#   * there is no ``^``, so squares are written as products (``v * v``);
#   * there is no unary minus, so no formula opens with a negation;
#   * the number token is ``\\d+(?:/\\d+)?``, so an unspaced ``1/2`` would be ONE literal rather
#     than a division - halves are therefore written as explicit divisions (``m * v * v / 2``);
#   * ``pi``, ``rootn``, ``costheta`` are named variables standing for values this language cannot
#     spell. They are leaves either way, so they do not affect any bracket decision.

CORPUS: tuple[Formula, ...] = (
    # ---- algebra: the identities whose two sides are the whole point of direction B ----------
    Formula("distributive_law_factored", "algebra", "a * (b + c)"),
    Formula("distributive_law_expanded", "algebra", "a * b + a * c"),
    Formula("binomial_square_factored", "algebra", "(a + b) * (a + b)"),
    Formula("binomial_square_expanded", "algebra", "a * a + 2 * a * b + b * b"),
    Formula("difference_of_squares_factored", "algebra", "(a + b) * (a - b)"),
    Formula("difference_of_squares_expanded", "algebra", "a * a - b * b"),
    Formula("difference_of_cubes_factored", "algebra", "(a - b) * (a * a + a * b + b * b)"),
    Formula("quadratic_factored", "algebra", "a * (x - r) * (x - s)"),
    Formula("quadratic_expanded", "algebra", "a * x * x + b * x + c"),
    Formula("fraction_sum_common_denominator", "algebra", "(a * d + b * c) / (b * d)"),
    # ---- arithmetic ---------------------------------------------------------------------------
    Formula("mean_of_two", "arithmetic", "(a + b) / 2"),
    Formula("mean_of_three", "arithmetic", "(a + b + c) / 3"),
    Formula("weighted_mean", "arithmetic", "(w1 * x1 + w2 * x2) / (w1 + w2)"),
    Formula("harmonic_sum", "arithmetic", "1 / a + 1 / b"),
    Formula("harmonic_mean_of_two", "arithmetic", "2 * a * b / (a + b)"),
    Formula("percentage_change", "arithmetic", "(b - a) / a * 100"),
    Formula("percentage_of", "arithmetic", "p * x / 100"),
    Formula("compound_interest_two_periods", "arithmetic", "p * (1 + r) * (1 + r)"),
    Formula("simple_interest_total", "arithmetic", "p + p * r * t"),
    Formula("mixed_number", "arithmetic", "a + b / c"),
    # ---- geometry -------------------------------------------------------------------------------
    Formula("slope_through_two_points", "geometry", "(y2 - y1) / (x2 - x1)"),
    Formula("distance_component_sum", "geometry", "(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)"),
    Formula("midpoint_coordinate", "geometry", "(x1 + x2) / 2"),
    Formula("trapezoid_area", "geometry", "(a + b) / 2 * h"),
    Formula("triangle_area", "geometry", "b * h / 2"),
    Formula("rectangle_perimeter", "geometry", "2 * (w + h)"),
    Formula("circumference_over_diameter", "geometry", "2 * pi * r / (2 * r)"),
    Formula("cylinder_volume", "geometry", "pi * r * r * h"),
    Formula("cone_volume", "geometry", "pi * r * r * h / 3"),
    # ---- calculus-adjacent ------------------------------------------------------------------------
    Formula("difference_quotient", "calculus", "(fxh - fx) / h"),
    Formula("linear_approximation", "calculus", "fa + m * (x - a)"),
    Formula("taylor_second_term", "calculus", "c2 * (x - a) * (x - a) / 2"),
    Formula("product_rule", "calculus", "du * v + u * dv"),
    Formula("quotient_rule", "calculus", "(du * v - u * dv) / (v * v)"),
    Formula("newton_step", "calculus", "x - fx / dfx"),
    Formula("derivative_of_quadratic", "calculus", "2 * a * x + b"),
    Formula("riemann_rectangle_width", "calculus", "(b - a) / n"),
    Formula("trapezoid_rule_term", "calculus", "(f1 + f2) * h / 2"),
    # ---- statistics -------------------------------------------------------------------------------
    Formula("variance_shortcut", "statistics", "q / n - m * m"),
    Formula(
        "variance_of_two_points",
        "statistics",
        "(x1 * x1 + x2 * x2) / 2 - (x1 + x2) / 2 * ((x1 + x2) / 2)",
    ),
    Formula("z_score", "statistics", "(x - m) / s"),
    Formula("standard_error", "statistics", "s / rootn"),
    Formula("confidence_interval_upper", "statistics", "m + z * s / rootn"),
    Formula("covariance_term", "statistics", "(x - mx) * (y - my) / n"),
    Formula("correlation_coefficient", "statistics", "sxy / (sx * sy)"),
    Formula("regression_slope", "statistics", "sxy / (sx * sx)"),
    Formula("pooled_mean", "statistics", "(n1 * m1 + n2 * m2) / (n1 + n2)"),
    # ---- physics-adjacent ---------------------------------------------------------------------------
    Formula("kinetic_energy", "physics", "m * v * v / 2"),
    Formula("density", "physics", "m / v"),
    Formula("average_velocity", "physics", "(x2 - x1) / (t2 - t1)"),
    Formula("total_momentum", "physics", "m1 * v1 + m2 * v2"),
    Formula("work_done", "physics", "f * d * costheta"),
    Formula("ohm_series_resistance", "physics", "r1 + r2 + r3"),
    Formula("ohm_parallel_two", "physics", "r1 * r2 / (r1 + r2)"),
    Formula("ohm_parallel_reciprocal", "physics", "1 / r1 + 1 / r2"),
    Formula("lens_equation_focal", "physics", "u * v / (u + v)"),
    Formula("voltage_divider", "physics", "vin * r2 / (r1 + r2)"),
    Formula("terminal_voltage", "physics", "emf - i * r"),
)


# ------------------------------------------------------------------------------- rendering core


def binding_powers(grammar: Grammar) -> dict[str, int]:
    """Operator -> binding power, read off :attr:`Grammar.levels`, highest level binding tightest.

    This is the same expression :class:`parseatlas.parser.Parser` builds for ``self._powers``, and
    it is the ONLY place this module learns anything about a grammar. Two operators sharing a level
    (``G0``'s ``* /`` and ``+ -``) get equal power, which is what makes the tied control grammar
    fall out of the same code path as the 24 strict orderings.
    """
    return {
        operator: len(grammar.levels) - level
        for level, group in enumerate(grammar.levels)
        for operator in group
    }


def child_threshold(parent_power: int, side: str) -> int:
    """The minimum power a child operator needs to stay unbracketed, derived from the parser.

    ``Parser._expression`` absorbs an operator into the current level at ``>= minimum_power`` and
    parses the right operand at ``power(operator) + 1``. Left children therefore need ``>=
    parent_power``, right children ``>= parent_power + 1``; anything below its threshold has to be
    bracketed or the parser would re-associate it.
    """
    if side == "left":
        return parent_power
    if side == "right":
        return parent_power + 1
    raise ValueError(f"side must be 'left' or 'right'; got {side!r}")


def needs_brackets(child: Node, parent_operator: str, side: str, powers: dict[str, int]) -> bool:
    """Does ``child`` require brackets under ``powers`` in this position?

    Leaves never do: a number or a variable is a single token that no precedence rule can split.
    """
    if not isinstance(child, Binary):
        return False
    return powers[child.operator] < child_threshold(powers[parent_operator], side)


def _render_node(node: Node, powers: dict[str, int]) -> str:
    if isinstance(node, Number):
        value = node.value
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if isinstance(node, Variable):
        return node.name
    left = _render_node(node.left, powers)
    if needs_brackets(node.left, node.operator, "left", powers):
        left = f"({left})"
    right = _render_node(node.right, powers)
    if needs_brackets(node.right, node.operator, "right", powers):
        right = f"({right})"
    return f"{left} {node.operator} {right}"


def render(tree: Node, grammar: Grammar, verify: bool = True) -> str:
    """Write ``tree`` under ``grammar`` with the minimum brackets that grammar requires.

    ``verify`` reparses the result and raises :class:`RoundTripError` on mismatch. It defaults to
    ``True`` on purpose: the round trip is the property the whole experiment rests on, so it is
    enforced in the code path that produces every number, not only in the test suite.
    """
    text = _render_node(tree, binding_powers(grammar))
    if verify:
        reparsed = parse(text, grammar)
        if reparsed != tree:
            raise RoundTripError(
                f"render/parse mismatch under {grammar.id}: {text!r} reparses to a different tree"
            )
    return text


def parenthesis_cost(tree: Node, grammar: Grammar) -> int:
    """The number of bracket PAIRS the grammar forces on this tree.

    One pair is one unit of notational cost. Counting pairs rather than characters is a choice, and
    a fully symmetric one here - every bracket this renderer emits is emitted as a matched pair.
    """
    return render(tree, grammar).count("(")


def tree_operators(tree: Node) -> tuple[str, ...]:
    """The distinct operators occurring in ``tree``, in first-encounter order (its T6 support)."""
    seen: dict[str, None] = {}
    stack: list[Node] = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, Binary):
            seen.setdefault(node.operator, None)
            stack.append(node.right)
            stack.append(node.left)
    return tuple(seen)


def formula_tree(formula: Formula) -> Node:
    """The intended tree of a formula: its conventional source parsed under the control grammar."""
    return parse(formula.source, CONTROL)


# ------------------------------------------------------------------------------------- auditing


def bracket_pairs(text: str) -> tuple[tuple[int, int], ...]:
    """Index of every matched bracket pair in a rendering, outermost-first by opening position."""
    stack: list[int] = []
    pairs: list[tuple[int, int]] = []
    for index, character in enumerate(text):
        if character == "(":
            stack.append(index)
        elif character == ")":
            pairs.append((stack.pop(), index))
    return tuple(sorted(pairs))


def _without_pair(text: str, pair: tuple[int, int]) -> str:
    open_index, close_index = pair
    return text[:open_index] + text[open_index + 1 : close_index] + text[close_index + 1 :]


def minimality_witnesses(tree: Node, grammar: Grammar) -> tuple[dict[str, Any], ...]:
    """For each bracket pair in the rendering, the evidence that it is required.

    Deleting the pair must make the string reparse to a DIFFERENT tree (or fail to parse). Any pair
    that survives deletion is a bracket the grammar did not require, i.e. a minimality defect.
    """
    text = render(tree, grammar)
    witnesses = []
    for pair in bracket_pairs(text):
        stripped = _without_pair(text, pair)
        try:
            reparsed: Node | None = parse(stripped, grammar)
        except ValueError:
            reparsed = None
        witnesses.append(
            {
                "pair": pair,
                "rendering": text,
                "without_pair": stripped,
                "reparse_failed": reparsed is None,
                "required": reparsed != tree,
            }
        )
    return tuple(witnesses)


def round_trip_audit(
    corpus: Sequence[Formula] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Independently recount the correctness bridge over the whole (corpus x grammar) grid."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    failures = []
    checks = 0
    for formula in corpus:
        tree = formula_tree(formula)
        for grammar in grammars:
            checks += 1
            text = render(tree, grammar, verify=False)
            if parse(text, grammar) != tree:
                failures.append({"formula": formula.name, "grammar": grammar.id, "rendering": text})
    return {
        "checks": checks,
        "failures": len(failures),
        "failing": tuple(failures),
        "holds": not failures,
    }


def minimality_audit(
    corpus: Sequence[Formula] | None = None, grammars: Sequence[Grammar] | None = None
) -> dict[str, Any]:
    """Recount minimality by construction over the whole grid: every bracket must be load-bearing."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    violations = []
    brackets = 0
    for formula in corpus:
        tree = formula_tree(formula)
        for grammar in grammars:
            for witness in minimality_witnesses(tree, grammar):
                brackets += 1
                if not witness["required"]:
                    violations.append({"formula": formula.name, "grammar": grammar.id, **witness})
    return {
        "brackets_checked": brackets,
        "violations": len(violations),
        "violating": tuple(violations),
        "minimal": not violations,
    }


def corpus_audit(corpus: Sequence[Formula] | None = None) -> dict[str, Any]:
    """Check the corpus is what it claims: unique names, and sources written minimally under G0.

    ``render(parse(source, G0), G0) == source`` says the source string carries no redundant bracket
    and no formatting the renderer would not itself produce, which is what makes the published
    corpus list an audit trail rather than a decoration.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    mismatched = tuple(
        {"formula": formula.name, "source": formula.source, "rendered": render(formula_tree(formula), CONTROL)}
        for formula in corpus
        if render(formula_tree(formula), CONTROL) != formula.source
    )
    names = [formula.name for formula in corpus]
    areas: dict[str, int] = {}
    for formula in corpus:
        areas[formula.area] = areas.get(formula.area, 0) + 1
    return {
        "size": len(corpus),
        "areas": dict(sorted(areas.items())),
        "area_count": len(areas),
        "duplicate_names": tuple(sorted({name for name in names if names.count(name) > 1})),
        "canonical_sources": not mismatched,
        "non_canonical": mismatched,
    }


# ------------------------------------------------------------------------------------ execution


def resolve_worker_count(item_count: int, workers: int | None = None) -> int:
    """Derive the process count from the observed cores, never from a hardcoded constant."""
    if workers is not None:
        return max(1, min(int(workers), max(item_count, 1)))
    if item_count < PARALLEL_MINIMUM_ITEMS:
        return 1
    cores = os.cpu_count() or 1
    return max(1, min(cores - 1, item_count))  # one core of headroom for the interactive session


def _formula_row(formula: Formula, grammars: tuple[Grammar, ...]) -> dict[str, Any]:
    tree = formula_tree(formula)
    renderings = {grammar.id: render(tree, grammar) for grammar in grammars}
    costs = {grammar_id: text.count("(") for grammar_id, text in renderings.items()}
    return {
        "name": formula.name,
        "area": formula.area,
        "source": formula.source,
        "operators": tree_operators(tree),
        "support_size": len(tree_operators(tree)),
        "renderings": renderings,
        "costs": costs,
    }


def _row_worker(payload: tuple[Formula, tuple[Grammar, ...]]) -> dict[str, Any]:
    """Module-level entry point so the row computation is picklable for a spawned process."""
    return _formula_row(*payload)


def cost_rows(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> tuple[dict[str, Any], ...]:
    """One record per formula: its rendering and bracket cost under every grammar.

    Formulas are independent, so the row computation parallelises trivially. It is nevertheless
    SEQUENTIAL by default here: :func:`resolve_worker_count` returns ``1`` below
    :data:`PARALLEL_MINIMUM_ITEMS` items, and the published corpus is far below it. That is a
    measured decision, not an assumption - :func:`parallel_decision` times both paths and the
    numbers are carried in the report. Parallelism changes only how fast; ``workers=1`` and
    ``workers=n`` return equal structures, which the test suite pins.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    resolved = resolve_worker_count(len(corpus), workers)
    if resolved <= 1 or len(corpus) < 2:
        return tuple(_formula_row(formula, grammars) for formula in corpus)
    payloads = [(formula, grammars) for formula in corpus]
    with ProcessPoolExecutor(max_workers=resolved) as pool:
        return tuple(pool.map(_row_worker, payloads))


def _ranked(totals: dict[str, int]) -> tuple[dict[str, Any], ...]:
    """Competition ranking (``1, 2, 2, 4``) over per-grammar totals, cheapest first."""
    order = sorted(totals.items(), key=lambda item: (item[1], item[0]))
    ranking = []
    previous_total: int | None = None
    previous_rank = 0
    for position, (grammar_id, total) in enumerate(order, start=1):
        rank = previous_rank if total == previous_total else position
        ranking.append({"rank": rank, "id": grammar_id, "total": total})
        previous_total, previous_rank = total, rank
    return tuple(ranking)


def _precedence_label(grammar: Grammar) -> str:
    return " ".join("".join(level) for level in grammar.levels)


def cost_table(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Cost per (formula, grammar), per-grammar totals, and the rank of every grammar.

    The rank of the conventional ``G0`` among all 25 is the experiment's first headline, so it is
    surfaced as ``control_rank`` rather than left to be looked up in the table.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = cost_rows(corpus, grammars, workers)
    labels = {grammar.id: _precedence_label(grammar) for grammar in grammars}
    totals = {grammar.id: sum(row["costs"][grammar.id] for row in rows) for grammar in grammars}
    ranking = _ranked(totals)
    ranks = {entry["id"]: entry["rank"] for entry in ranking}
    free_counts = {
        grammar.id: sum(1 for row in rows if row["costs"][grammar.id] == 0) for grammar in grammars
    }
    detailed = tuple(
        {
            **entry,
            "precedence": labels[entry["id"]],
            "free_formulas": free_counts[entry["id"]],
            "versus_control": entry["total"] - totals[CONTROL.id],
        }
        for entry in ranking
    )
    best = detailed[0]
    worst = detailed[-1]
    best_alternative = next(entry for entry in detailed if entry["id"] != CONTROL.id)
    control_total = totals[CONTROL.id]
    return {
        "formula_count": len(rows),
        "grammar_count": len(grammars),
        "rows": rows,
        "totals": totals,
        "labels": labels,
        "ranks": ranks,
        "ranking": detailed,
        "free_counts": free_counts,
        "control_id": CONTROL.id,
        "control_total": control_total,
        "control_rank": ranks[CONTROL.id],
        "best": best,
        "worst": worst,
        "best_alternative": best_alternative,
        "control_minus_best": control_total - best["total"],
        "control_minus_best_percent": (
            100.0 * (control_total - best["total"]) / control_total if control_total else 0.0
        ),
        "spread": worst["total"] - best["total"],
    }


def convention_sensitivity(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Per formula, how far its cost travels across the 25 conventions.

    A formula whose ``range`` is ``0`` is convention-INSENSITIVE: no precedence order can make it
    cheaper or dearer, so it says nothing about conventions and everything about itself. A formula
    with a wide range is where notation actually decides something. The quantity is a property of
    the mathematics, not of any one convention, which is why it is reported per formula and not per
    grammar.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = cost_rows(corpus, grammars, workers)
    entries = []
    for row in rows:
        costs = row["costs"]
        minimum = min(costs.values())
        maximum = max(costs.values())
        entries.append(
            {
                "name": row["name"],
                "area": row["area"],
                "source": row["source"],
                "support_size": row["support_size"],
                "control_cost": costs[CONTROL.id],
                "min": minimum,
                "max": maximum,
                "range": maximum - minimum,
                "cheapest_grammars": tuple(sorted(key for key, value in costs.items() if value == minimum)),
                "dearest_grammars": tuple(sorted(key for key, value in costs.items() if value == maximum)),
                "constant": minimum == maximum,
                "control_is_cheapest": costs[CONTROL.id] == minimum,
            }
        )
    ordered = sorted(entries, key=lambda entry: (-entry["range"], entry["name"]))
    constant = tuple(entry["name"] for entry in entries if entry["constant"])
    return {
        "formulas": tuple(entries),
        "by_range": tuple(ordered),
        "constant_formulas": constant,
        "constant_count": len(constant),
        "variable_count": len(entries) - len(constant),
        "max_range": max((entry["range"] for entry in entries), default=0),
        "most_sensitive": tuple(
            entry["name"] for entry in ordered if entry["range"] == ordered[0]["range"]
        )
        if ordered
        else (),
        "control_optimal_count": sum(1 for entry in entries if entry["control_is_cheapest"]),
    }


def free_under(
    grammar: Grammar,
    corpus: Sequence[Formula] | None = None,
) -> tuple[str, ...]:
    """Which formulas need ZERO brackets under this grammar.

    This is the direct form of the founding question's second half: the parenthesis-free formulas
    of a convention are the mathematics that convention would have made natural to write.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    return tuple(
        formula.name for formula in corpus if parenthesis_cost(formula_tree(formula), grammar) == 0
    )


def free_transition(
    from_grammar: Grammar,
    to_grammar: Grammar,
    corpus: Sequence[Formula] | None = None,
) -> dict[str, Any]:
    """Which formulas gain and which lose parenthesis-free status when the convention changes."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    before = set(free_under(from_grammar, corpus))
    after = set(free_under(to_grammar, corpus))
    return {
        "from": from_grammar.id,
        "to": to_grammar.id,
        "free_before": tuple(sorted(before)),
        "free_after": tuple(sorted(after)),
        "gained": tuple(sorted(after - before)),
        "lost": tuple(sorted(before - after)),
        "kept": tuple(sorted(before & after)),
    }


def area_table(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Does the ranking hold per area, or does each area prefer its own convention?"""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = cost_rows(corpus, grammars, workers)
    global_table = cost_table(corpus, grammars, workers)
    areas = sorted({row["area"] for row in rows})
    per_area = {}
    for area in areas:
        subset = [row for row in rows if row["area"] == area]
        totals = {grammar.id: sum(row["costs"][grammar.id] for row in subset) for grammar in grammars}
        ranking = _ranked(totals)
        ranks = {entry["id"]: entry["rank"] for entry in ranking}
        best_total = ranking[0]["total"]
        per_area[area] = {
            "formula_count": len(subset),
            "totals": totals,
            "ranking": ranking,
            "ranks": ranks,
            "control_total": totals[CONTROL.id],
            "control_rank": ranks[CONTROL.id],
            "best_total": best_total,
            "best_grammars": tuple(entry["id"] for entry in ranking if entry["total"] == best_total),
            "worst_total": ranking[-1]["total"],
        }
    winners = {area: report["best_grammars"] for area, report in per_area.items()}
    global_best = global_table["best"]["id"]
    return {
        "areas": areas,
        "per_area": per_area,
        "area_winners": winners,
        "global_best": global_best,
        "areas_won_by_global_best": tuple(
            area for area, ids in winners.items() if global_best in ids
        ),
        "unanimous": len({frozenset(ids) for ids in winners.values()}) == 1,
        "control_ranks": {area: report["control_rank"] for area, report in per_area.items()},
    }


def null_model(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Separate the forced part of the cost from the part a convention actually chooses.

    A formula whose cost is identical under all 25 grammars contributes the SAME constant to every
    total. It cannot move a ranking; it can only make the corpus look expensive. The accounting
    here splits every total into a forced floor and a movable remainder, re-ranks on the movable
    subcorpus alone, and reports whether the headline ranking survives. If it does not, the
    ranking was measuring the corpus rather than the conventions.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    rows = cost_rows(corpus, grammars, workers)
    constant_rows = [row for row in rows if len(set(row["costs"].values())) == 1]
    movable_rows = [row for row in rows if len(set(row["costs"].values())) > 1]
    forced_total = sum(next(iter(row["costs"].values())) for row in constant_rows)
    full_totals = {grammar.id: sum(row["costs"][grammar.id] for row in rows) for grammar in grammars}
    movable_totals = {
        grammar.id: sum(row["costs"][grammar.id] for row in movable_rows) for grammar in grammars
    }
    full_ranking = _ranked(full_totals)
    movable_ranking = _ranked(movable_totals)
    full_ranks = {entry["id"]: entry["rank"] for entry in full_ranking}
    movable_ranks = {entry["id"]: entry["rank"] for entry in movable_ranking}
    support_sizes: dict[int, int] = {}
    for row in constant_rows:
        support_sizes[row["support_size"]] = support_sizes.get(row["support_size"], 0) + 1
    full_spread = max(full_totals.values()) - min(full_totals.values())
    movable_spread = max(movable_totals.values()) - min(movable_totals.values())
    # The per-formula oracle: what the corpus would cost if a DIFFERENT convention could be chosen
    # for every formula. No single grammar can reach it, so the gap between it and the cheapest
    # grammar is the price of having ONE global convention at all - a second null quantity, and the
    # one that says how much of a grammar's total is unavoidable rather than characteristic.
    oracle_total = sum(min(row["costs"].values()) for row in rows)
    best_total = min(full_totals.values())
    return {
        "constant_formulas": tuple(row["name"] for row in constant_rows),
        "constant_count": len(constant_rows),
        "constant_at_zero": sum(1 for row in constant_rows if next(iter(row["costs"].values())) == 0),
        "oracle_total": oracle_total,
        "best_total": best_total,
        "oracle_gap": best_total - oracle_total,
        "movable_formulas": tuple(row["name"] for row in movable_rows),
        "movable_count": len(movable_rows),
        "forced_total": forced_total,
        "constant_support_sizes": dict(sorted(support_sizes.items())),
        "single_operator_constant": sum(1 for row in constant_rows if row["support_size"] <= 1),
        "full_totals": full_totals,
        "movable_totals": movable_totals,
        "full_ranking": full_ranking,
        "movable_ranking": movable_ranking,
        "full_spread": full_spread,
        "movable_spread": movable_spread,
        "spread_survival": 1.0 if full_spread == 0 else movable_spread / full_spread,
        "control_rank_full": full_ranks[CONTROL.id],
        "control_rank_movable": movable_ranks[CONTROL.id],
        "control_rank_stable": full_ranks[CONTROL.id] == movable_ranks[CONTROL.id],
        "ranking_identical": tuple(entry["id"] for entry in full_ranking)
        == tuple(entry["id"] for entry in movable_ranking),
        "best_full": full_ranking[0]["id"],
        "best_movable": movable_ranking[0]["id"],
        "best_agrees": full_ranking[0]["id"] == movable_ranking[0]["id"],
    }


def parallel_decision(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    repeats: int = 3,
    workers: int | None = None,
) -> dict[str, Any]:
    """Measure sequential against parallel on THIS workload and record which one wins.

    Repository policy is multicore by default; policy also says a sequential path is allowed when a
    measurement justifies it. This workload is a few thousand string renders of pure Python, so the
    process-pool spawn is expected to dominate - but the expectation is not the evidence, the
    numbers this function returns are.
    """
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    pool_workers = workers if workers is not None else max(2, min(os.cpu_count() or 2, len(corpus)))

    def _time(count: int) -> float:
        best = float("inf")
        for _ in range(max(1, repeats)):
            start = time.perf_counter()
            cost_rows(corpus, grammars, workers=count)
            best = min(best, time.perf_counter() - start)
        return best

    sequential = _time(1)
    parallel = _time(pool_workers)
    return {
        "items": len(corpus),
        "grammars": len(grammars),
        "cores": os.cpu_count(),
        "repeats": repeats,
        "pool_workers": pool_workers,
        "sequential_seconds": sequential,
        "parallel_seconds": parallel,
        "speedup": sequential / parallel if parallel else float("inf"),
        "faster": "sequential" if sequential <= parallel else "parallel",
        "resolved_default_workers": resolve_worker_count(len(corpus)),
        "identical_results": cost_rows(corpus, grammars, workers=1)
        == cost_rows(corpus, grammars, workers=pool_workers),
    }


def notational_cost_report(
    corpus: Sequence[Formula] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
    timing: bool = False,
) -> dict[str, Any]:
    """The whole experiment as one structure: bridge, table, sensitivity, areas, null model."""
    corpus = tuple(corpus) if corpus is not None else CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    table = cost_table(corpus, grammars, workers)
    best_alternative_id = table["best_alternative"]["id"]
    best_alternative = next(grammar for grammar in grammars if grammar.id == best_alternative_id)
    report = {
        "corpus": corpus_audit(corpus),
        "round_trip": round_trip_audit(corpus, grammars),
        "minimality": minimality_audit(corpus, grammars),
        "cost_table": table,
        "sensitivity": convention_sensitivity(corpus, grammars, workers),
        "areas": area_table(corpus, grammars, workers),
        "null_model": null_model(corpus, grammars, workers),
        "free_under_control": free_under(CONTROL, corpus),
        "free_under_best_alternative": free_under(best_alternative, corpus),
        "free_transition": free_transition(CONTROL, best_alternative, corpus),
    }
    if timing:
        report["parallel_decision"] = parallel_decision(corpus, grammars)
    return report
