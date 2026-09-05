"""Experiment 0047: sweep the parameter, publish the SHAPE, and do not declare the wall.

**Two withdrawals, recorded at the top because together they are the result.**  This module has
made the same mistake twice, at two different levels, and the second time inside the repair of the
first.  Both times an enumeration was restricted for a good reason and the restricted answer was
read as a property of the RULES.  :data:`WITHDRAWN` carries both as data.

*Round 1.*  The enumeration stopped at one bracket pair per site.  The module published a witness
block reading ``attainable 0 1 0`` and concluded that the 0038 rules *admit* the tax curve.  The
bound was defended in prose -- a writing past it "continues the curve of its cell FLAT" -- which is
a true statement about ONE writing and a false statement about the cell's curve, because that curve
is the MAXIMUM over all writings at each bracket count.  Any writing that already carries a bracket
can be padded, ``(X)`` rewritten as ``((X))``, to any higher count without changing what a shape
rule sees.  So the curve past the bound is the RUNNING MAXIMUM of the enumerated one, a running
maximum cannot fall, and a peak with a drop after it is impossible in principle.
``((a * b)) * (c * d)`` carries three brackets, reparses under ``G0`` to the same tree, and still
makes ``factor_structure`` manifest: attainable at three is ``1`` and not ``0``.

*Round 2.*  The repair admitted nesting and correctly withdrew the turn -- and then enumerated
bracket sites by walking only :class:`~parseatlas.parser.Binary` nodes, so **a bracket around a
LEAF was never produced**, while the docstring said "every bracketable position" and
:class:`BracketCell` said ``attainable`` was the largest count *any* writing reaches at all.  It
was not.  Under the opaque regime a bracketed operand has ``visible = False``, so ``Part.is_atom``
is ``False`` for it, and wrapping a leaf turns it into a non-atom numerator factor::

    a * (b + c)     1 bracket    opaque manifest: nothing
    (a) * (b + c)   2 brackets   opaque manifest: factor_structure  -- and it reparses the same

``distributive_law / factored / G0 / opaque``, published as ``bracket_counts [1, 2]``,
``attainable [0, 0]``, ``constant``, RISES.  Over the corpus, 72 opaque cells rise where 0 were
published.  See :func:`leaf_bracket_witness`.

**What survives, and it is the important half.**  No peak exists anywhere -- in the corpus, in the
witnesses, or in the rules.  Every within-cell verdict is ``constant``, ``non-increasing`` or
``non-decreasing`` and never ``non-monotone``, so the round 1 withdrawal stands and the
impossibility of a peak stands.  What is gone is the corpus negative result "no cell ever rises".

**The general lesson, which is worth more than the curves.**  An enumeration is a claim about what
exists.  Every restriction on it must be declared at the point where the answer is read, not
defended in prose somewhere else -- because a defence is about the writings the restriction drops,
while the answer is about an aggregate over the writings it keeps.  Both rejections came down to
one question, and every sweep here now answers it in the report, by construction: *what writings
does this enumeration NOT produce, and would any of them change the answer?*

The owner set this card twice over: once as a methodological correction to every card that
published a number at a threshold it had chosen in advance, and once as a research subject in its
own right.  The ROADMAP subsection *Let the system find the wall* (2026-09-05) is the rule; this
module is its first application and its test case, and it is the repository's clearest worked
example of why the rule exists.

The shape being hunted is the owner's tax curve::

    raise the rate and revenue rises -- UP TO A POINT -- past which raising it further makes
    revenue FALL.  The turning point is not derivable from the first half of the curve.

So every quantity here is swept across its whole range and reported as a curve: the table, the
first difference so a sign change is visible, a monotonicity verdict, the argmax, and the sample
size behind every point.  A monotone curve is a result and is reported as one.  What this module
must never produce is a single point presented as though the curve had stopped moving.

Three parameters are swept.

**A. Brackets against what a writing makes visible.**  Experiment 0038 measured what each of the
25 precedence worlds makes *manifest* in the writing it chooses.  Its rules come in two regimes:
``transparent``, where a shape rule may look inside a bracket, and ``opaque``, where it may not,
and 0038 observed that under the opaque rules "a bracketed factor stops being inspectable".  That
is one end of a curve.  The other end is the ordinary intuition that brackets make structure
explicit.  So: fix an object and a world, sweep the number of brackets in the writing from the
world's minimum upward over every writing of that same object, and watch the manifest set.

**B. Expression length against semantic diversity.**  Longer operator words have more parses, so
the 25 grammars should produce more distinct meanings -- but sympy collapses parses back together,
and the collapse may grow faster than the divergence.  Sweep word length and count distinct
semantic keys.  T6 is the null model and it is the single most likely way this card could
manufacture a fake turn: a word whose operator support is ``s`` can only distinguish orderings of
those ``s`` operators, so diversity is bounded by support and not by length.  Every count here is
therefore reported inside a support stratum and never pooled across strata.

**C. The width of the convention axis against semantic yield.**  Experiment 0030 widened the axis
from precedence to precedence-plus-associativity and reported a *decay*: 100 per cent of the
reachability gap recovered at ``k = 2``, 10.946 per cent at ``k = 6``.  A decay is not a turn.  The
card asks whether any widening ever gives strictly LESS than a narrower one, which would be a
genuine turn.  This module sweeps the axis width as the number of operators whose associativity is
freed -- ``w = 0, 1, 2, 3, 4``, that is ``24, 48, 96, 192, 384`` grammars -- and reports both the
raw class counts and the yield per grammar added.

What is *not* here, deliberately
--------------------------------

No threshold is declared anywhere, and every sweep answers *what writings does this not produce*:

* **Curve A** enumerates every bracket PATTERN of the intended tree -- every antichain of
  positions, leaves and root included -- which is a census of every writing the object has, up to
  the one equivalence no rule can see through.  The writings it does not produce are exactly those
  with a bracket inside a bracket; :func:`enumeration_audit` checks, over a census of every bracket
  subset of every small enough writing and a seeded sample of arbitrarily nested ones, that such a
  writing has the manifest set of its pattern and at least its pattern's bracket count.  So no
  manifest set and no attainable value is missing.  Padding is what makes the curve past a
  pattern's own count a running maximum (:func:`attainable_with_padding`), and the consequence is
  that no cell's attainable curve can fall after it has risen: curve A can report a rise, and can
  never report a peak.
* **Curves B and C** sweep word length exhaustively as far as the run is affordable and then
  sample beyond it with a declared, seeded sample.  Both the exhaustive limit and the samples past
  it are reported, with the answer to the only question that matters: was the curve still moving
  when the exhaustive sweep stopped.  What they do not produce is words of length past the sample,
  and words with repeated operands, both declared where the numbers are read.

Multicore
---------

Per repository policy the decision is measured, not assumed.  :func:`parallel_decision` times the
sequential and parallel paths of each sweep at a declared size and reports the crossover; the
sweeps take ``workers`` and produce identical output on either path, which
``test_turning_points.py`` asserts rather than assumes.  The two payloads sit on opposite sides of
one constant, so there are two measured floors -- :data:`PATTERN_MINIMUM_ITEMS` for curve A's
per-writing pattern census and :data:`PARALLEL_MINIMUM_ITEMS` for the word records.
"""

from __future__ import annotations

import os
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from itertools import combinations, permutations, product
from math import comb, factorial
from random import Random
from typing import Any

from .associativity import AssociativeGrammar, associative_parse, side_tag
from .canonical import canonicalize
from .grammar import OPERATORS, Grammar, all_grammars
from .manifest_properties import (
    CORPUS as MANIFEST_CORPUS,
)
from .manifest_properties import (
    PROPERTIES,
    PROPERTY_NAMES,
    REGIMES,
    Atom,
    Group,
    MathObject,
    Op,
    Surface,
    Writing,
    ground_truth,
    object_tree,
    surface,
    surface_text,
)
from .notational_cost import GRAMMARS, binding_powers, needs_brackets
from .parser import Binary, Node, Number, Variable, parse
from .reachability import canonical_tree, resolve_workers

__all__ = [
    "AXIS_CHAIN",
    "AXIS_OPERATOR_ORDER",
    "BRACKET_WITNESS",
    "EPSILON",
    "OPERAND_NAMES",
    "PARALLEL_MINIMUM_ITEMS",
    "PATTERN_MINIMUM_ITEMS",
    "SAMPLE_SEED",
    "WITHDRAWN",
    "argmax_point",
    "attainable_with_padding",
    "axis_grammars",
    "axis_record",
    "axis_width_sweep",
    "bracket_cell",
    "bracket_patterns",
    "bracket_sweep",
    "bracketed_surface",
    "bracket_sites",
    "catalan",
    "curve_summary",
    "enumeration_audit",
    "first_differences",
    "leaf_bracket_witness",
    "length_sweep",
    "maximal_positions",
    "monotonicity",
    "operator_word",
    "padding_witness",
    "parallel_decision",
    "pooling_audit",
    "resolve_sweep_workers",
    "support_ceiling",
    "turning_points",
    "turning_points_report",
    "witness_sweep",
    "word_record",
    "writing_audit",
    "writing_cells",
]


#: Float comparisons in the curve verdicts.  Every value here is a mean of small integers, so the
#: only role of a tolerance is to keep an exact zero from being read as a sign.
EPSILON: float = 1e-12

#: Operands of a generated operator word: distinct names, so that no *coincidence between operands*
#: can collapse two parses.  The collapse measured by curve B is then the collapse the operators
#: themselves force -- ``a * b / c`` against ``a * (b / c)`` -- and not an artefact of writing the
#: same variable twice.
OPERAND_NAMES: tuple[str, ...] = tuple(chr(ord("a") + index) for index in range(20))

#: The order in which operators are freed as the convention axis widens in curve C.  Declared, not
#: inferred: the result depends on it and hiding that would be a judgement dressed as a
#: measurement.  Every single-operator widening is also reported on its own, so a reader can see
#: what each operator contributes independently of this order.
AXIS_OPERATOR_ORDER: tuple[str, ...] = ("+", "-", "*", "/")

#: Seed for every sample drawn past an exhaustive limit.  One seed, declared, so the samples are
#: reproducible and a reader can re-draw them.
SAMPLE_SEED: int = 47


# ----------------------------------------------------------------------------- curve vocabulary
#
# Everything a swept curve must publish, in one place, so that no sweep can quietly report an
# argmax without the sequence it came from.


def first_differences(values: Sequence[float]) -> tuple[float, ...]:
    """``v[i+1] - v[i]``: the sequence in which a turn shows up as a sign change."""
    return tuple(values[index + 1] - values[index] for index in range(len(values) - 1))


def monotonicity(values: Sequence[float], epsilon: float = EPSILON) -> str:
    """The verdict on one curve: ``constant``, ``non-decreasing``, ``non-increasing`` or
    ``non-monotone``.

    A single-point curve is ``undefined`` rather than trivially monotone, because calling a curve
    with one observation monotone is exactly the overclaim this card exists to prevent.
    """
    if len(values) < 2:
        return "undefined"
    diffs = first_differences(values)
    ups = sum(1 for diff in diffs if diff > epsilon)
    downs = sum(1 for diff in diffs if diff < -epsilon)
    if ups == 0 and downs == 0:
        return "constant"
    if downs == 0:
        return "non-decreasing"
    if ups == 0:
        return "non-increasing"
    return "non-monotone"


def turning_points(
    parameters: Sequence[Any], values: Sequence[float], epsilon: float = EPSILON
) -> tuple[dict[str, Any], ...]:
    """Every interior sign change of the first difference, with the fall or rise that follows it.

    A ``peak`` is a rise followed by a fall -- the owner's tax curve -- and it carries ``drop_after``,
    the distance from the peak down to the lowest value at any larger parameter.  A ``trough`` is
    the mirror image and carries ``rise_after``.  Flat stretches do not break a run: the sign is
    carried across them, so ``1 2 2 1`` turns once and not twice, and a flat top is reported at its
    right-hand end -- the last parameter before the fall begins.
    """
    if len(values) < 3:
        return ()
    found: list[dict[str, Any]] = []
    diffs = first_differences(values)
    previous_sign = 0
    for index, diff in enumerate(diffs):
        sign = 1 if diff > epsilon else (-1 if diff < -epsilon else 0)
        if sign == 0:
            continue
        if previous_sign > 0 and sign < 0:
            found.append(
                {
                    "kind": "peak",
                    "parameter": parameters[index],
                    "value": values[index],
                    "drop_after": values[index] - min(values[index + 1 :]),
                }
            )
        elif previous_sign < 0 and sign > 0:
            found.append(
                {
                    "kind": "trough",
                    "parameter": parameters[index],
                    "value": values[index],
                    "rise_after": max(values[index + 1 :]) - values[index],
                }
            )
        previous_sign = sign
    return tuple(found)


def argmax_point(
    parameters: Sequence[Any], values: Sequence[float]
) -> dict[str, Any]:
    """The parameter at which the curve is highest, with its value; first wins on a tie."""
    best = max(range(len(values)), key=lambda index: values[index])
    return {"parameter": parameters[best], "value": values[best]}


def curve_summary(
    parameters: Sequence[Any],
    values: Sequence[float],
    sample_sizes: Sequence[int],
    stratum: str,
    measurement: str,
    objects: Sequence[int] | None = None,
) -> dict[str, Any]:
    """One swept curve, published whole.

    ``stratum`` is mandatory and may not be empty: a rate without a named stratum is the defect
    :func:`pooling_audit` looks for, and refusing to build one is cheaper than finding it later.

    ``objects`` is the count of *distinct objects* behind each point, which is a different number
    from ``sample_sizes`` whenever a cell is an ``object x writing x world`` product: a 25-fold
    world multiplier makes a two-object tail look like a fifty-item one.  Both columns are
    published, and :func:`pooling_audit` reads its thin-point verdict off ``objects`` when a curve
    carries one, because a point resting on two objects is thin however many cells it holds.
    """
    if not stratum:
        raise ValueError("every curve must name the stratum it was computed inside")
    if not (len(parameters) == len(values) == len(sample_sizes)):
        raise ValueError("parameters, values and sample sizes must have the same length")
    if objects is not None and len(objects) != len(values):
        raise ValueError("object counts must have the same length as the curve")
    diffs = first_differences(values)
    verdict = monotonicity(values)
    return {
        "stratum": stratum,
        "measurement": measurement,
        "parameter": list(parameters),
        "value": [float(value) for value in values],
        "sample_size": list(sample_sizes),
        "objects": list(objects) if objects is not None else None,
        "first_difference": [float(diff) for diff in diffs],
        "monotone": verdict,
        "is_monotone": verdict in ("constant", "non-decreasing", "non-increasing"),
        "argmax": argmax_point(parameters, values) if values else None,
        "turning_points": list(turning_points(parameters, values)),
        "final_difference": float(diffs[-1]) if diffs else None,
        "still_moving_at_end": bool(diffs) and abs(diffs[-1]) > EPSILON,
        "minimum_sample_size": min(sample_sizes) if sample_sizes else 0,
        "minimum_objects": min(objects) if objects else None,
    }


# ------------------------------------------------------------ curve A: brackets against visibility
#
# A writing of an object is its intended tree plus a set of bracketed positions.  The grammar fixes
# a MINIMUM set -- the brackets without which the string reparses into a different tree -- and every
# superset of that minimum is another writing of the same object.  Sweeping the superset is
# sweeping the bracket count with everything else held fixed, which is the only form of this sweep
# in which "more brackets" is the cause of whatever the observation does.
#
# This section has been rejected twice, both times for the same reason, and the second time by the
# repair of the first.  The two rejections are recorded in :data:`WITHDRAWN`, and the machinery
# below is built so that neither can recur silently: the enumeration is a CENSUS of every writing
# the object has, up to an equivalence :func:`enumeration_audit` checks rather than argues.


#: A path to a node of the intended tree: ``()`` is the root, ``("l", "r")`` its left child's right
#: child.  Paths, not node identities, because two structurally equal subtrees must stay distinct
#: bracket sites.
Path = tuple[str, ...]


#: The two findings this module has published and withdrawn, recorded as data so a test can pin the
#: withdrawals and not only the replacements.  Both were one mistake at two different levels: a
#: restriction on the ENUMERATION was read as a property of the RULES.
WITHDRAWN: dict[str, Any] = {
    "lesson": (
        "an enumeration is a claim about what exists; every restriction on it must be declared at "
        "the point where the answer is read, and not defended in prose somewhere else"
    ),
    "rounds": [
        {
            "round": 1,
            "restriction": "at most one bracket pair per site, so nesting was never enumerated",
            "claim": "The rules admit the tax curve.",
            "published_as": {"brackets": [1, 2, 3], "attainable": [0, 1, 0]},
            "corrected_to": {"brackets": [1, 2, 3], "attainable": [0, 1, 1]},
            "cause": (
                "the enumeration bound of one bracket pair per site was read as a bound on the "
                "cell's curve; the cell's curve is the maximum over all writings at each bracket "
                "count, and padding an existing bracket carries every value forward, so the curve "
                "past the bound is the running maximum of the enumerated one and not a flat "
                "continuation of it"
            ),
            "witness": "((a * b)) * (c * d)",
            "consequence": (
                "an attainable curve cannot fall after it has risen, so a peak is impossible in "
                "principle and no genuine turn exists anywhere in this experiment"
            ),
        },
        {
            "round": 2,
            "restriction": (
                "bracket_sites walked only Binary nodes, so a bracket around a LEAF was never "
                "enumerated, while the docstring said 'every bracketable position' and BracketCell "
                "said 'attainable' was the largest count any writing reaches at all"
            ),
            "claim": "No cell of the 34-object corpus ever rises.",
            "published_as": {"brackets": [1, 2], "attainable": [0, 0], "verdict": "constant"},
            "corrected_to": {"brackets": [1, 2], "attainable": [0, 1], "verdict": "non-decreasing"},
            "cause": (
                "under the opaque regime a bracketed operand has visible=False, so Part.is_atom is "
                "False for it; wrapping a LEAF therefore turns it into a non-atom numerator factor "
                "and _shape_factor_structure, which asks for at least two of those, fires -- the "
                "mechanism the report described and then never enumerated"
            ),
            "witness": "(a) * (b + c)",
            "consequence": (
                "72 of the 1250 opaque corpus cells rise where 0 were published, every one of them "
                "by factor_structure switching on; no peak appears anywhere, so the round 1 "
                "withdrawal and the impossibility of a peak both stand"
            ),
        },
    ],
}


def attainable_with_padding(
    bracket_counts: Sequence[int], enumerated: Sequence[int]
) -> tuple[int, ...]:
    """The attainable curve of a cell once padding is admitted: a running maximum.

    ``enumerated`` is the largest manifest count reached by a writing whose *minimum* bracket count
    is exactly that one -- the unpadded reading of :func:`bracket_patterns`.  A writing that already
    carries at least one bracket can have that bracket doubled, which raises the bracket count by
    exactly one and leaves the manifest set untouched: 0038's ``_look`` recurses through the inner
    ``Group`` under the transparent regime and stops at the outer one under the opaque regime,
    either way seeing what it saw before.  So whatever is attainable at a count that carries a
    bracket stays attainable at every higher count, and the honest curve is the running maximum.

    The one place the carry does not apply is a step out of a bracket-free writing: at zero
    brackets there is nothing to double, so ``attainable(0)`` is not carried into ``attainable(1)``.
    That is why the collapse at the first bracket under the opaque regime survives this correction
    while the round 1 witness peak does not.
    """
    if len(bracket_counts) != len(enumerated):
        raise ValueError("bracket counts and enumerated values must have the same length")
    carried: list[int] = []
    for index, value in enumerate(enumerated):
        if index and bracket_counts[index - 1] >= 1:
            carried.append(max(value, carried[-1]))
        else:
            carried.append(value)
    return tuple(carried)


def _reachable_with_padding(
    bracket_counts: Sequence[int], shown: Sequence[Sequence[str]]
) -> tuple[tuple[str, ...], ...]:
    """The same carry applied to the property sets: once a property is manifest it stays manifest.

    The manifest COUNT and the manifest SET are two different aggregates of the same cell and both
    are published, because a flat count can hide one property switching on as another switches off.
    """
    carried: list[frozenset[str]] = []
    for index, names in enumerate(shown):
        here = frozenset(names)
        if index and bracket_counts[index - 1] >= 1:
            here = here | carried[-1]
        carried.append(here)
    return tuple(
        tuple(name for name in PROPERTY_NAMES if name in entry) for entry in carried
    )


def bracket_sites(tree: Node, grammar: Grammar) -> tuple[tuple[Path, ...], frozenset[Path]]:
    """Every bracketable position of ``tree``, and the subset the grammar forces.

    **Every position means every node, leaves included.**  An earlier revision walked only
    :class:`~parseatlas.parser.Binary` nodes while its docstring promised every bracketable
    position, and that restriction was then read as a property of the rules.  It is not one.
    ``(a)`` is a legal writing of ``a``, it reparses to the same leaf, and under 0038's opaque
    regime it is the difference between a manifest ``factor_structure`` and nothing at all: a
    bracketed operand has ``visible = False`` and therefore ``Part.is_atom = False``, so
    ``a * (b + c)`` shows nothing and ``(a) * (b + c)`` shows ``factor_structure``.  See
    :func:`leaf_bracket_witness`, which builds both.

    The forced set is decided by :func:`parseatlas.notational_cost.needs_brackets`, the same
    function ``render`` uses, so the minimum here is the minimum 0034 and 0038 measure.  Only a
    compound operand can be forced; a leaf never is.  The root is a bracketable position and is
    never forced: writing the whole expression inside a bracket is a legal writing of the object,
    it is what 0038's opaque rules react to most strongly, and leaving it out would be choosing the
    answer.

    Positions come back in pre-order, which is the order :func:`bracket_patterns` indexes its
    bitmasks in.
    """
    powers = binding_powers(grammar)
    sites: list[Path] = []
    forced: set[Path] = set()

    def walk(node: Node, path: Path) -> None:
        sites.append(path)
        if not isinstance(node, Binary):
            return
        for side, child in (("left", node.left), ("right", node.right)):
            child_path = path + (side[0],)
            if isinstance(child, Binary) and needs_brackets(child, node.operator, side, powers):
                forced.add(child_path)
            walk(child, child_path)

    walk(tree, ())
    return tuple(sites), frozenset(forced)


def _leaf_surface(node: Node) -> Surface:
    if isinstance(node, Number):
        value = node.value
        text = (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        )
        return Atom(text, "number")
    if isinstance(node, Variable):
        return Atom(node.name, "variable")
    raise TypeError(f"not a leaf: {node!r}")


def bracketed_surface(
    tree: Node,
    grammar: Grammar,
    extra: Iterable[Path],
    doubled: Iterable[Path] = (),
) -> Surface:
    """The written form of ``tree`` under ``grammar`` with ``extra`` optional brackets added.

    ``extra`` may name any position :func:`bracket_sites` returns, a leaf included.

    With ``extra`` empty this reproduces :func:`parseatlas.manifest_properties.surface` exactly,
    which :func:`writing_audit` asserts rather than assumes; every other value of ``extra`` is
    another writing of the same object, which the same audit checks by reparsing the string.

    ``doubled`` wraps an already-bracketed position a second time.  That is what padding is, and it
    is how :func:`enumeration_audit` builds the writings no bracket-set enumeration can reach.
    """
    powers = binding_powers(grammar)
    chosen = frozenset(extra)
    twice = frozenset(doubled)

    def wrap(written: Surface, path: Path) -> Surface:
        wrapped = Group(written)
        return Group(wrapped) if path in twice else wrapped

    def walk(node: Node, path: Path) -> Surface:
        if not isinstance(node, Binary):
            written = _leaf_surface(node)
            return wrap(written, path) if path in chosen else written
        rendered: list[Surface] = []
        for side, child in (("left", node.left), ("right", node.right)):
            child_path = path + (side[0],)
            written = walk(child, child_path)
            if isinstance(child, Binary) and (
                needs_brackets(child, node.operator, side, powers) or child_path in chosen
            ):
                written = wrap(written, child_path)
            rendered.append(written)
        node_surface: Surface = Op(node.operator, rendered[0], rendered[1])
        if path == () and () in chosen:
            return wrap(node_surface, ())
        return node_surface

    return walk(tree, ())


def _pattern_surface(tree: Node, chosen: frozenset[Path]) -> Surface:
    """The written form carrying brackets at EXACTLY ``chosen`` and nowhere else.

    Grammar-free on purpose.  A pattern is evaluated once and reused under all 25 worlds, because
    the worlds differ only in which brackets they *force*, and a forced bracket a pattern already
    covers sits inside an opaque blob where no rule can see it.
    """

    def walk(node: Node, path: Path) -> Surface:
        if not isinstance(node, Binary):
            written = _leaf_surface(node)
        else:
            left = walk(node.left, path + ("l",))
            right = walk(node.right, path + ("r",))
            written = Op(node.operator, left, right)
        return Group(written) if path in chosen else written

    return walk(tree, ())


def _bracket_count(node: Surface) -> int:
    if isinstance(node, Atom):
        return 0
    if isinstance(node, Group):
        return 1 + _bracket_count(node.inner)
    return _bracket_count(node.left) + _bracket_count(node.right)


def maximal_positions(paths: Iterable[Path]) -> frozenset[Path]:
    """The outermost members of a bracket set: those with no bracketed ancestor.

    This is the reduction the whole of curve A rests on.  Under the opaque regime a rule stops at
    the outermost ``Group`` it meets, so a bracket strictly inside another bracket is invisible;
    under the transparent regime every bracket is invisible.  Two writings with the same outermost
    set therefore have the same manifest set in both regimes, whatever else they do -- which
    :func:`enumeration_audit` checks over a census and a sample rather than asserting.
    """
    chosen = set(paths)
    return frozenset(
        path
        for path in chosen
        if not any(other != path and path[: len(other)] == other for other in chosen)
    )


def bracket_patterns(
    tree: Node, sites: Sequence[Path]
) -> tuple[tuple[frozenset[Path], int, int, int], ...]:
    """Every bracket PATTERN of ``tree``: every antichain of positions, with its bitmasks.

    A pattern is a set of positions no one of which lies inside another -- the outermost brackets
    of a writing.  Each entry is ``(paths, size, covers, own)``, where ``covers`` is the bitmask of
    every position at or below a member and ``own`` the bitmask of the members themselves, both
    indexed by position in ``sites``.

    Patterns and not bracket *subsets* are the unit of the census, and that is the point.  The
    subsets of the corpus's largest writing number ``2 ** 27``, and with nesting the writings are
    infinite; their manifest sets take only as many distinct values as there are patterns, because
    everything below an outermost bracket is invisible to every rule.  The census is therefore
    complete and finite at once: ``77336`` patterns for that writing, ``156475`` over the 50
    writings of the corpus.
    """
    index = {path: position for position, path in enumerate(sites)}
    subtree: dict[Path, int] = {}

    def masks(node: Node, path: Path) -> int:
        mask = 1 << index[path]
        if isinstance(node, Binary):
            mask |= masks(node.left, path + ("l",))
            mask |= masks(node.right, path + ("r",))
        subtree[path] = mask
        return mask

    masks(tree, ())

    def walk(node: Node, path: Path) -> list[tuple[frozenset[Path], int, int, int]]:
        here = (frozenset({path}), 1, subtree[path], 1 << index[path])
        if not isinstance(node, Binary):
            return [here, (frozenset(), 0, 0, 0)]
        out = [here]
        for left in walk(node.left, path + ("l",)):
            for right in walk(node.right, path + ("r",)):
                out.append(
                    (
                        left[0] | right[0],
                        left[1] + right[1],
                        left[2] | right[2],
                        left[3] | right[3],
                    )
                )
        return out

    return tuple(walk(tree, ()))


def padding_witness(grammar_id: str = "G0") -> dict[str, Any]:
    """The writing that refutes the ROUND 1 finding, built and checked here.

    The withdrawn block said ``attainable 0 1 0``: nothing at one bracket, ``factor_structure`` at
    two, nothing at three.  ``((a * b)) * (c * d)`` carries three brackets, reparses to the same
    tree, and still makes ``factor_structure`` manifest under the opaque regime.  One writing is
    enough to withdraw the block, so it is constructed rather than argued.
    """
    item = next(entry for entry in BRACKET_WITNESS if entry.name == "witness_product_of_pairs")
    grammar = next(entry for entry in GRAMMARS if entry.id == grammar_id)
    tree = object_tree(item.writings[0])
    left: Path = ("l",)
    plain = bracketed_surface(tree, grammar, (left,))
    padded = bracketed_surface(tree, grammar, (left,), (left,))

    def manifest_of(written: Surface) -> tuple[str, ...]:
        return tuple(rule.name for rule in PROPERTIES if rule.shape(written, True, item.variable))

    return {
        "round": 1,
        "object": item.name,
        "grammar": grammar.id,
        "regime": "opaque",
        "two_brackets": {
            "writing": surface_text(plain),
            "brackets": _bracket_count(plain),
            "manifest": list(manifest_of(plain)),
        },
        "three_brackets": {
            "writing": surface_text(padded),
            "brackets": _bracket_count(padded),
            "manifest": list(manifest_of(padded)),
            "reparses_to_the_same_tree": parse(surface_text(padded), grammar) == tree,
        },
        "withdrawn_attainable_at_three": 0,
        "attainable_at_three": len(manifest_of(padded)),
    }


def leaf_bracket_witness(grammar_id: str = "G0") -> dict[str, Any]:
    """The writing that refutes the ROUND 2 finding, built and checked here.

    ``distributive_law`` in its ``factored`` writing was published as ``bracket_counts [1, 2]``,
    ``attainable [0, 0]``, verdict ``constant``.  A bracket around the LEAF ``a`` was never
    enumerated.  It costs one bracket, reparses under ``G0`` to the same tree, and makes
    ``factor_structure`` manifest under the opaque regime, because a bracketed operand is not
    ``visible`` and therefore not an atom, and ``_shape_factor_structure`` asks for two numerator
    factors that are not atoms.
    """
    item = next(entry for entry in MANIFEST_CORPUS if entry.name == "distributive_law")
    writing = next(entry for entry in item.writings if entry.role == "factored")
    grammar = next(entry for entry in GRAMMARS if entry.id == grammar_id)
    tree = object_tree(writing)
    leaf: Path = ("l",)
    plain = bracketed_surface(tree, grammar, ())
    with_leaf = bracketed_surface(tree, grammar, (leaf,))

    def manifest_of(written: Surface) -> tuple[str, ...]:
        return tuple(rule.name for rule in PROPERTIES if rule.shape(written, True, item.variable))

    sites, forced = bracket_sites(tree, grammar)
    return {
        "round": 2,
        "object": item.name,
        "role": writing.role,
        "grammar": grammar.id,
        "regime": "opaque",
        "sites": [list(path) for path in sites],
        "sites_an_earlier_revision_enumerated": [
            list(path) for path in sites if _is_compound(tree, path)
        ],
        "one_bracket": {
            "writing": surface_text(plain),
            "brackets": _bracket_count(plain),
            "manifest": list(manifest_of(plain)),
        },
        "two_brackets": {
            "writing": surface_text(with_leaf),
            "brackets": _bracket_count(with_leaf),
            "manifest": list(manifest_of(with_leaf)),
            "reparses_to_the_same_tree": parse(surface_text(with_leaf), grammar) == tree,
        },
        "forced": [list(path) for path in sorted(forced)],
        "withdrawn_attainable": [0, 0],
        "attainable": [len(manifest_of(plain)), len(manifest_of(with_leaf))],
    }


def _is_compound(tree: Node, path: Path) -> bool:
    node = tree
    for step in path:
        assert isinstance(node, Binary)
        node = node.left if step == "l" else node.right
    return isinstance(node, Binary)


# ------------------------------------------------------------------- what the census leaves out
#
# The question both rejections came down to, asked of this enumeration and answered by
# construction: what writings does it NOT produce, and would any of them change the answer?
#
# It produces one representative of every bracket PATTERN.  The writings it does not produce are
# exactly those whose brackets are not all outermost -- a bracket inside a bracket, at any depth,
# in any number.  Two facts make that omission answerable rather than arguable, and
# enumeration_audit checks both:
#
#   1. a writing's manifest set is its pattern's, in both regimes.  Under the opaque regime a rule
#      stops at the outermost Group; under the transparent regime it sees through every Group.
#   2. a writing's bracket count is at least its pattern's minimum, and every count above that
#      minimum is reached by padding, which leaves the manifest set alone.
#
# Together those say the census misses no manifest set and no attainable value.  Neither is
# asserted: (1) is checked exhaustively over every bracket subset of every writing small enough to
# enumerate them all, and both are checked on a seeded sample of arbitrarily nested writings drawn
# from the whole grid.


def enumeration_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    exhaustive_sites: int = 11,
    sample: int = 4000,
    seed: int = SAMPLE_SEED,
) -> dict[str, Any]:
    """Check, rather than argue, that the pattern census stands for every writing there is.

    Three parts, each declared with its own scale:

    ``sites``
        every node of every intended tree is a bracket site, and no leaf is ever forced.
        Exhaustive over the grid.  This is the round 2 defect in its mechanical form: an earlier
        revision returned ``binary`` sites where ``total`` was promised.

    ``reduction``
        for every writing whose site count is at most ``exhaustive_sites``, over **all**
        ``2 ** sites`` bracket subsets: the manifest set of the subset equals the manifest set of
        its outermost members, in both regimes.  A census, not a sample, on the writings where a
        census is affordable, and the covered fraction is reported.

    ``nesting``
        a seeded sample over the whole grid of writings that no bracket-set enumeration can reach:
        a random subset of *all* positions, with random extra nesting on random brackets.  Each is
        checked three ways -- its manifest set is its pattern's, its bracket count is at least its
        pattern's minimum, and it still reparses to the intended tree.

    The sampled part is a sample and is labelled as one: nesting depth is unbounded, so no census
    of writings exists to take.  What makes the sample sufficient is that part ``reduction`` is a
    census over the axis that is finite.
    """
    corpus = tuple(corpus) if corpus is not None else MANIFEST_CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    random = Random(seed)

    site_rows = 0
    site_failures: list[str] = []
    for item in corpus:
        for writing in item.writings:
            tree = object_tree(writing)
            expected = _node_count(tree)
            for grammar in grammars:
                sites, forced = bracket_sites(tree, grammar)
                site_rows += 1
                if len(sites) != expected or len(set(sites)) != expected:
                    site_failures.append(f"sites {item.name}.{writing.role}/{grammar.id}")
                if () in forced:
                    site_failures.append(f"root forced {item.name}.{writing.role}/{grammar.id}")
                if any(not _is_compound(tree, path) for path in forced):
                    site_failures.append(f"leaf forced {item.name}.{writing.role}/{grammar.id}")

    writings_total = sum(len(item.writings) for item in corpus)
    covered = 0
    subsets_checked = 0
    reduction_failures: list[str] = []
    for item in corpus:
        for writing in item.writings:
            tree = object_tree(writing)
            sites, _ = bracket_sites(tree, grammars[0])
            if len(sites) > exhaustive_sites:
                continue
            covered += 1
            cache: dict[frozenset[Path], tuple[tuple[str, ...], ...]] = {}
            for size in range(len(sites) + 1):
                for chosen in combinations(sites, size):
                    subsets_checked += 1
                    here = _manifest_pair(_pattern_surface(tree, frozenset(chosen)), item.variable)
                    outermost = maximal_positions(chosen)
                    reference = cache.get(outermost)
                    if reference is None:
                        reference = _manifest_pair(
                            _pattern_surface(tree, outermost), item.variable
                        )
                        cache[outermost] = reference
                    if here != reference:
                        reduction_failures.append(
                            f"reduction {item.name}.{writing.role}: {sorted(chosen)}"
                        )

    candidates = [
        (item, writing, grammar)
        for item in corpus
        for writing in item.writings
        for grammar in grammars
    ]
    nesting_checked = 0
    manifest_agrees = 0
    count_at_least_minimum = 0
    reparses = 0
    nested_writings = 0
    nesting_failures: list[str] = []
    for index in range(sample):
        item, writing, grammar = candidates[random.randrange(len(candidates))]
        tree = object_tree(writing)
        sites, forced = bracket_sites(tree, grammar)
        chosen = frozenset(random.sample(sites, random.randint(0, len(sites))))
        bracketed = sorted(chosen | forced)
        doubled = frozenset(
            path for path in bracketed if random.random() < 0.3
        )
        written = bracketed_surface(tree, grammar, chosen, doubled)
        text = surface_text(written)
        pattern = maximal_positions(chosen | forced)
        nesting_checked += 1
        if doubled or len(pattern) < len(chosen | forced):
            nested_writings += 1
        if _manifest_pair(written, item.variable) == _manifest_pair(
            _pattern_surface(tree, pattern), item.variable
        ):
            manifest_agrees += 1
        else:
            nesting_failures.append(f"manifest {item.name}.{writing.role}/{grammar.id}: {text}")
        if _bracket_count(written) >= len(pattern | forced):
            count_at_least_minimum += 1
        else:
            nesting_failures.append(f"count {item.name}.{writing.role}/{grammar.id}: {text}")
        if parse(text, grammar) == tree:
            reparses += 1
        else:
            nesting_failures.append(f"reparse {item.name}.{writing.role}/{grammar.id}: {text}")

    failures = site_failures + reduction_failures + nesting_failures
    return {
        "sites": {
            "rows": site_rows,
            "every_node_is_a_site": not site_failures,
            "failures": site_failures[:10],
        },
        "reduction": {
            "exhaustive_sites": exhaustive_sites,
            "writings_covered": covered,
            "writings_total": writings_total,
            "bracket_subsets_checked": subsets_checked,
            "manifest_set_is_the_pattern_s": not reduction_failures,
            "failures": reduction_failures[:10],
        },
        "nesting": {
            "sample": nesting_checked,
            "seed": seed,
            "writings_no_subset_enumeration_reaches": nested_writings,
            "manifest_set_is_the_pattern_s": manifest_agrees,
            "bracket_count_at_least_the_pattern_minimum": count_at_least_minimum,
            "reparses_to_the_intended_tree": reparses,
            "failures": nesting_failures[:10],
        },
        "census_stands_for_every_writing": not failures,
        "failure_count": len(failures),
        "reading": (
            "the census enumerates one writing per bracket pattern; every other writing has the "
            "manifest set of its pattern and at least its pattern's bracket count, so no manifest "
            "set and no attainable value is missing from the reported curve"
        ),
    }


def _node_count(tree: Node) -> int:
    if isinstance(tree, Binary):
        return 1 + _node_count(tree.left) + _node_count(tree.right)
    return 1


def _manifest_pair(written: Surface, variable: str | None) -> tuple[tuple[str, ...], ...]:
    """The manifest set under both regimes, which is what the reduction claim is about."""
    return tuple(
        tuple(
            rule.name
            for rule in PROPERTIES
            if rule.shape(written, regime == "opaque", variable)
        )
        for regime in REGIMES
    )


def writing_audit(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Two checks that make curve A a sweep of writings of ONE object rather than of many objects.

    1. With no optional brackets the builder agrees with 0038's own ``surface``.
    2. **Every** writing the census enumerates reparses, under its own grammar, to the intended
       tree.  If that ever failed, the sweep would be comparing different mathematics at different
       bracket counts.

    The second check is a census over the whole grid -- every pattern of every writing under every
    world -- and not a sample, which is why it is worth the process pool it takes.
    """
    corpus = tuple(corpus) if corpus is not None else MANIFEST_CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    payloads = [
        (item.name, writing.role, grammar.id)
        for item in corpus
        for writing in item.writings
        for grammar in grammars
    ]
    results = _map_payloads(
        _writing_audit_cell, payloads, workers, minimum_items=PATTERN_MINIMUM_ITEMS
    )
    failures = [failure for entry in results for failure in entry["failures"]]
    return {
        "cells": len(payloads),
        "minimum_agrees_with_0038_surface": not any(
            failure.startswith("minimum") for failure in failures
        ),
        "writings_checked": sum(entry["writings"] for entry in results),
        "all_writings_denote_the_same_tree": not any(
            failure.startswith("reparse") for failure in failures
        ),
        "workers": resolve_sweep_workers(
            len(payloads), workers, minimum_items=PATTERN_MINIMUM_ITEMS
        ),
        "failures": failures[:20],
        "failure_count": len(failures),
    }


def _writing_audit_cell(payload: tuple[str, str, str]) -> dict[str, Any]:
    """One ``(object, writing, world)`` cell of :func:`writing_audit`.  Module level for the pool."""
    object_name, role, grammar_id = payload
    item = _object_registry()[object_name]
    writing = next(entry for entry in item.writings if entry.role == role)
    grammar = _grammar_registry_by_id()[grammar_id]
    tree = object_tree(writing)
    failures: list[str] = []
    if bracketed_surface(tree, grammar, ()) != surface(tree, grammar):
        failures.append(f"minimum mismatch {object_name}.{role}/{grammar_id}")
    sites, forced = bracket_sites(tree, grammar)
    forced_bits = _forced_mask(forced, sites)
    checked = 0
    for paths, _size, covers, _own in bracket_patterns(tree, sites):
        if forced_bits & ~covers:
            continue
        text = surface_text(bracketed_surface(tree, grammar, paths))
        checked += 1
        if parse(text, grammar) != tree:
            failures.append(f"reparse mismatch {object_name}.{role}/{grammar_id}: {text}")
    return {"writings": checked, "failures": failures}


def _forced_mask(forced: Iterable[Path], sites: Sequence[Path]) -> int:
    """The bitmask of the forced positions, in the index order :func:`bracket_sites` returns."""
    index = {path: position for position, path in enumerate(sites)}
    mask = 0
    for path in forced:
        mask |= 1 << index[path]
    return mask


@dataclass(frozen=True)
class BracketCell:
    """One ``(object, writing, world, regime)`` cell of curve A, as a curve in its own right.

    Three readings of the same cell, and the difference between the second and the third is this
    card's round 1 correction.

    * ``mean`` is the average manifest count over the bracket PATTERNS whose minimum bracket count
      is this one.  It is a mean over a declared population -- writings up to what no rule can see
      -- and it is labelled as one wherever it is published.
    * ``unpadded_attainable`` is the largest manifest count any pattern reaches at that count
      before padding is admitted.  It is published only to be compared with the next one.
    * ``attainable`` is the largest manifest count any writing at that count reaches at all, which
      is :func:`attainable_with_padding` applied to the unpadded one.  This is the honest reading
      of "what a writing with ``b`` brackets can show", and every verdict is taken from it.

    ``shown`` records, per bracket count, which properties a pattern at that count makes manifest;
    ``reachable`` carries the same sets forward under padding.  ``patterns`` is the population
    behind each point.

    Past ``bracket_counts[-1]`` the curve continues **constant** and is not tabulated: the largest
    pattern is the most brackets a writing can carry with all of them visible, and every writing
    past it repeats a pattern already counted, at a higher count, where the running maximum has
    already carried the value.
    """

    object_name: str
    role: str
    grammar_id: str
    regime: str
    variable: str | None
    truth: tuple[str, ...]
    bracket_counts: tuple[int, ...]
    mean: tuple[float, ...]
    unpadded_attainable: tuple[int, ...]
    attainable: tuple[int, ...]
    shown: tuple[tuple[str, ...], ...]
    reachable: tuple[tuple[str, ...], ...]
    patterns: tuple[int, ...]


_OBJECTS: dict[str, MathObject] | None = None
_GRAMMARS_BY_ID: dict[str, Grammar] | None = None


def _object_registry() -> dict[str, MathObject]:
    """Every object curve A can be asked about: 0038's corpus plus the declared witnesses.

    A single registry keyed by name is what lets the pool payloads be plain strings, which is what
    the Windows ``spawn`` pool needs them to be.
    """
    global _OBJECTS
    if _OBJECTS is None:
        _OBJECTS = {item.name: item for item in (*MANIFEST_CORPUS, *BRACKET_WITNESS)}
    return _OBJECTS


def _grammar_registry_by_id() -> dict[str, Grammar]:
    global _GRAMMARS_BY_ID
    if _GRAMMARS_BY_ID is None:
        _GRAMMARS_BY_ID = {grammar.id: grammar for grammar in GRAMMARS}
    return _GRAMMARS_BY_ID


def writing_cells(payload: tuple[str, str, tuple[str, ...]]) -> list[dict[str, Any]]:
    """Curve A for one ``(object, writing)`` under every world and both regimes.

    The unit of work is the writing and not the cell, because the expensive half -- evaluating the
    0038 shape rules on every bracket pattern of the tree -- does not depend on the world.  A world
    enters only through which brackets it *forces*, which decides which patterns are legal and what
    each one costs; that part is integer arithmetic on bitmasks.  Module level so the Windows
    ``spawn`` pool can pickle it.
    """
    object_name, role, grammar_ids = payload
    item = _object_registry()[object_name]
    writing = next(entry for entry in item.writings if entry.role == role)
    registry = _grammar_registry_by_id()
    grammars = [registry[grammar_id] for grammar_id in grammar_ids]
    tree = object_tree(writing)
    truth = ground_truth(tree, item.variable)
    sites, _ = bracket_sites(tree, grammars[0])
    evaluated = []
    for paths, size, covers, own in bracket_patterns(tree, sites):
        written = _pattern_surface(tree, paths)
        manifests = _manifest_pair(written, item.variable)
        evaluated.append((size, covers, own, manifests))

    records: list[dict[str, Any]] = []
    for grammar in grammars:
        _, forced = bracket_sites(tree, grammar)
        forced_bits = _forced_mask(forced, sites)
        for position, regime in enumerate(REGIMES):
            buckets: dict[int, list[Any]] = {}
            for size, covers, own, manifests in evaluated:
                if forced_bits & ~covers:
                    continue
                count = size + (forced_bits & ~own).bit_count()
                names = manifests[position]
                bucket = buckets.get(count)
                if bucket is None:
                    bucket = [0, set(), 0, 0]
                    buckets[count] = bucket
                bucket[0] = max(bucket[0], len(names))
                bucket[1].update(names)
                bucket[2] += 1
                bucket[3] += len(names)
            counts = tuple(sorted(buckets))
            unpadded = tuple(buckets[count][0] for count in counts)
            shown = tuple(
                tuple(name for name in PROPERTY_NAMES if name in buckets[count][1])
                for count in counts
            )
            cell = BracketCell(
                object_name=object_name,
                role=role,
                grammar_id=grammar.id,
                regime=regime,
                variable=item.variable,
                truth=truth,
                bracket_counts=counts,
                mean=tuple(buckets[count][3] / buckets[count][2] for count in counts),
                unpadded_attainable=unpadded,
                attainable=attainable_with_padding(counts, unpadded),
                shown=shown,
                reachable=_reachable_with_padding(counts, shown),
                patterns=tuple(buckets[count][2] for count in counts),
            )
            records.append(_cell_record(cell))
    return records


def bracket_cell(payload: tuple[str, str, str, str]) -> dict[str, Any]:
    """Curve A for one cell.  Module level so the Windows ``spawn`` pool can pickle it."""
    object_name, role, grammar_id, regime = payload
    for record in writing_cells((object_name, role, (grammar_id,))):
        if record["regime"] == regime:
            return record
    raise ValueError(f"no such regime: {regime}")


def _cell_record(cell: BracketCell) -> dict[str, Any]:
    return {
        "object": cell.object_name,
        "role": cell.role,
        "grammar": cell.grammar_id,
        "regime": cell.regime,
        "variable": cell.variable,
        "truth": list(cell.truth),
        "bracket_counts": list(cell.bracket_counts),
        "mean": list(cell.mean),
        "unpadded_attainable": list(cell.unpadded_attainable),
        "attainable": list(cell.attainable),
        "shown": [list(names) for names in cell.shown],
        "reachable": [list(names) for names in cell.reachable],
        "patterns": list(cell.patterns),
        "minimum_brackets": cell.bracket_counts[0],
        "maximum_brackets": cell.bracket_counts[-1],
        "axis_has_no_gap": list(cell.bracket_counts)
        == list(range(cell.bracket_counts[0], cell.bracket_counts[-1] + 1)),
        "monotone_mean": monotonicity(cell.mean),
        "monotone_unpadded_attainable": monotonicity(cell.unpadded_attainable),
        "monotone_attainable": monotonicity(cell.attainable),
        "padding_changed_the_curve": list(cell.unpadded_attainable) != list(cell.attainable),
    }


#: Below this many independent items a sweep of *word records* stays sequential.  Measured, not
#: assumed: see :func:`parallel_decision`, whose recorded run on the experiment host is quoted in
#: the report.  An explicit ``workers=N`` always overrides it, so the parallel path stays reachable
#: at any size.
PARALLEL_MINIMUM_ITEMS: int = 256

#: The same floor for curve A's payloads, which are a different shape.  A payload is now a whole
#: writing's pattern census -- up to ``77336`` patterns, seconds of pure Python each -- so the
#: crossover sits far lower than the word sweep's.  The number is where the observed crossover
#: fell: sequential still won at ``16`` corpus writings and the pool won at ``24``.  The two
#: constants differ because the two payloads do, and neither is a tidy round number chosen in
#: advance; both are quoted in the report with the run that produced them.
PATTERN_MINIMUM_ITEMS: int = 24


def resolve_sweep_workers(
    item_count: int,
    workers: int | None = None,
    minimum_items: int = PARALLEL_MINIMUM_ITEMS,
) -> int:
    """Workers from the observed core count, with the crossover measured by :func:`parallel_decision`.

    The floor is not a constant chosen for tidiness and it is not one constant: below it a spawned
    interpreter plus the sympy import chain costs more than the work handed to it, and how much
    work that is depends on the payload, which is why each sweep passes its own measured floor.
    """
    if workers is None and item_count < minimum_items:
        return 1
    return resolve_workers(item_count, workers)


def _map_payloads(
    function: Any,
    payloads: Sequence[Any],
    workers: int | None,
    minimum_items: int = PARALLEL_MINIMUM_ITEMS,
) -> list[Any]:
    """Run ``function`` over ``payloads``, sequentially or across processes; same result either way."""
    count = resolve_sweep_workers(len(payloads), workers, minimum_items=minimum_items)
    if count == 1:
        return [function(payload) for payload in payloads]
    chunk = max(1, len(payloads) // (count * 4))
    with ProcessPoolExecutor(max_workers=count) as pool:
        return list(pool.map(function, payloads, chunksize=chunk))


def bracket_sweep(
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Curve A: manifest properties against bracket count, in both of 0038's rule regimes.

    Three readings of the same cells are published, and they do not agree, which is the point:

    * the **pooled** curve, the mean over every cell defined at that bracket count.  It is the
      curve a card would publish if it did not think about the null model, and it is reported here
      to be refuted rather than to be believed: the population changes with the parameter, because
      a small tree has no writing with eight brackets.
    * the **paired** first difference, over the cells defined at *both* ends of each step.  The
      population is then identical on the two sides of the difference, so the sign is a property of
      the brackets and not of which objects happened to reach that far.
    * the **within-cell** verdict: how many of the cells rise anywhere at all.
    """
    corpus = tuple(corpus) if corpus is not None else MANIFEST_CORPUS
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    grammar_ids = tuple(grammar.id for grammar in grammars)
    payloads = [
        (item.name, writing.role, grammar_ids)
        for item in corpus
        for writing in item.writings
    ]
    grouped = _map_payloads(
        writing_cells, payloads, workers, minimum_items=PATTERN_MINIMUM_ITEMS
    )
    records = [record for group in grouped for record in group]
    census = 0
    for item in corpus:
        for writing in item.writings:
            tree = object_tree(writing)
            census += len(bracket_patterns(tree, bracket_sites(tree, grammars[0])[0]))
    return {
        "corpus_objects": len(corpus),
        "writings": sum(len(item.writings) for item in corpus),
        "worlds": len(grammars),
        "regimes": list(REGIMES),
        "cells": len(records),
        "patterns": census,
        "patterns_legal_per_cell": sum(sum(record["patterns"]) for record in records),
        "workers": resolve_sweep_workers(
            len(payloads), workers, minimum_items=PATTERN_MINIMUM_ITEMS
        ),
        "every_axis_is_gap_free": all(record["axis_has_no_gap"] for record in records),
        "regime_results": {
            regime: _bracket_regime(
                [record for record in records if record["regime"] == regime], regime
            )
            for regime in REGIMES
        },
        "cell_records": records,
    }


def _within_cell(records: Sequence[dict[str, Any]], key: str) -> dict[str, Any]:
    """How many cells are constant, fall, rise or turn, in the reading named by ``key``."""
    verdicts = [monotonicity(record[key]) for record in records]
    peaks = sum(
        1
        for record in records
        if any(
            entry["kind"] == "peak"
            for entry in turning_points(record["bracket_counts"], record[key])
        )
    )
    rises = verdicts.count("non-decreasing")
    non_monotone = verdicts.count("non-monotone")
    return {
        "reading": key,
        "cells": len(records),
        "constant": verdicts.count("constant"),
        "non_decreasing": rises,
        "non_increasing": verdicts.count("non-increasing"),
        "non_monotone": non_monotone,
        "cells_that_ever_rise": rises + non_monotone,
        "cells_with_a_peak": peaks,
    }


def _rising_cells(records: Sequence[dict[str, Any]], key: str = "attainable") -> dict[str, Any]:
    """Which cells rise, and which property switches on when they do.

    The round 2 correction lives here.  A rise was reported as impossible on the corpus; it is not,
    and naming the objects and the property is what makes the correction checkable rather than a
    changed number.
    """
    by_object: dict[str, int] = {}
    by_property: dict[str, int] = {}
    for record in records:
        if monotonicity(record[key]) not in ("non-decreasing", "non-monotone"):
            continue
        name = f"{record['object']}/{record['role']}"
        by_object[name] = by_object.get(name, 0) + 1
        reached = record["reachable"]
        for index in range(len(reached) - 1):
            for switched in set(reached[index + 1]) - set(reached[index]):
                by_property[switched] = by_property.get(switched, 0) + 1
    return {
        "cells": sum(by_object.values()),
        "by_object": dict(sorted(by_object.items(), key=lambda entry: (-entry[1], entry[0]))),
        "by_property": dict(sorted(by_property.items(), key=lambda entry: (-entry[1], entry[0]))),
    }


def _objects_at(records: Sequence[dict[str, Any]], counts: Sequence[int]) -> list[int]:
    """Distinct objects behind each bracket count, which is not the cell count.

    A cell is ``object x writing x world``, so a two-object tail carries fifty cells under the 25
    worlds and two writings each.  Publishing only the cell column is how a two-object tail is made
    to look like a fifty-item one, and this is the column that stops that.
    """
    seen: dict[int, set[str]] = {count: set() for count in counts}
    for record in records:
        for count in record["bracket_counts"]:
            if count in seen:
                seen[count].add(record["object"])
    return [len(seen[count]) for count in counts]


def _bracket_regime(records: Sequence[dict[str, Any]], regime: str) -> dict[str, Any]:
    pooled_values: dict[int, list[float]] = {}
    attainable_values: dict[int, list[int]] = {}
    unpadded_values: dict[int, list[int]] = {}
    for record in records:
        for index, count in enumerate(record["bracket_counts"]):
            pooled_values.setdefault(count, []).append(record["mean"][index])
            attainable_values.setdefault(count, []).append(record["attainable"][index])
            unpadded_values.setdefault(count, []).append(record["unpadded_attainable"][index])
    counts = sorted(pooled_values)
    objects = _objects_at(records, counts)
    stratum = f"regime={regime}; all cells defined at that bracket count"
    pooled = curve_summary(
        counts,
        [sum(pooled_values[count]) / len(pooled_values[count]) for count in counts],
        [len(pooled_values[count]) for count in counts],
        stratum=stratum,
        measurement=(
            "mean manifest properties per writing, over the bracket patterns whose minimum "
            "bracket count is that one"
        ),
        objects=objects,
    )
    pooled_attainable = curve_summary(
        counts,
        [sum(attainable_values[count]) / len(attainable_values[count]) for count in counts],
        [len(attainable_values[count]) for count in counts],
        stratum=stratum,
        measurement=(
            "mean of the best manifest count attainable at that bracket count, padding admitted"
        ),
        objects=objects,
    )
    pooled_unpadded = curve_summary(
        counts,
        [sum(unpadded_values[count]) / len(unpadded_values[count]) for count in counts],
        [len(unpadded_values[count]) for count in counts],
        stratum=stratum,
        measurement=(
            "mean of the best manifest count a pattern reaches at that bracket count before "
            "padding is admitted, published only to be compared with the curve above"
        ),
        objects=objects,
    )
    return {
        "pooled_mean_curve": pooled,
        "pooled_attainable_curve": pooled_attainable,
        "pooled_unpadded_attainable_curve": pooled_unpadded,
        "paired_first_difference_mean": _paired_differences(records, "mean"),
        "paired_first_difference_attainable": _paired_differences(records, "attainable"),
        "within_cell": _within_cell(records, "attainable"),
        "within_cell_unpadded_attainable": _within_cell(records, "unpadded_attainable"),
        "within_cell_pattern_mean": _within_cell(records, "mean"),
        "rising_cells": _rising_cells(records),
        "cells_padding_changed": sum(
            1 for record in records if record["padding_changed_the_curve"]
        ),
        "property_strata": _bracket_property_strata(records, regime),
        "per_property_within_cell": _per_property_within_cell(records),
    }


def _per_property_within_cell(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Does any single property ever become manifest at a HIGHER bracket count inside one cell?

    The manifest-count curve of a cell could stay flat while one property switched on and another
    switched off, so the count alone does not settle the question this card asks.  This looks at
    each property separately, inside each cell, and counts the cells whose curve for that property
    ever rises.  It reads ``reachable`` and not ``shown``, so padding is admitted here too; the
    carry can only remove a rise and never create one, because a property already carried forward
    is already on.
    """
    out: dict[str, Any] = {}
    for name in PROPERTY_NAMES:
        rising = 0
        for record in records:
            seen = [1 if name in reached else 0 for reached in record["reachable"]]
            if any(seen[index + 1] > seen[index] for index in range(len(seen) - 1)):
                rising += 1
        out[name] = {"cells": len(records), "cells_that_ever_rise": rising}
    return out


def _paired_differences(records: Sequence[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    """First differences taken inside a cell and only then averaged.

    A pooled first difference mixes two populations; this one does not, because a cell enters the
    step only when it is defined at both ends of it.
    """
    steps: dict[int, list[float]] = {}
    for record in records:
        counts = record["bracket_counts"]
        values = record[key]
        for index in range(len(counts) - 1):
            steps.setdefault(counts[index], []).append(values[index + 1] - values[index])
    out = []
    for start in sorted(steps):
        deltas = steps[start]
        out.append(
            {
                "from": start,
                "to": start + 1,
                "cells": len(deltas),
                "mean_delta": sum(deltas) / len(deltas),
                "rises": sum(1 for delta in deltas if delta > EPSILON),
                "falls": sum(1 for delta in deltas if delta < -EPSILON),
                "flat": sum(1 for delta in deltas if abs(delta) <= EPSILON),
            }
        )
    return out


def _bracket_property_strata(records: Sequence[dict[str, Any]], regime: str) -> dict[str, Any]:
    """One curve per property, computed only over the cells where the property is TRUE.

    A shape rule can only be manifest where the property holds -- 0038's ``truth_audit`` is what
    licenses that -- so pooling the rate over objects that do not have the property would mix a
    visibility observation with a corpus composition observation.  The stratum is the truth set.

    The indicator is read off ``reachable`` and not ``shown``, so a property manifest at some
    bracket count stays counted at every higher one the padding carry reaches.  Every curve also
    carries its distinct-object column beside its cell column.
    """
    out: dict[str, Any] = {}
    for name in PROPERTY_NAMES:
        stratum = [record for record in records if name in record["truth"]]
        if not stratum:
            out[name] = {
                "stratum": f"regime={regime}; {name} true of the object",
                "cells": 0,
                "curve": None,
            }
            continue
        buckets: dict[int, list[int]] = {}
        for record in stratum:
            for index, count in enumerate(record["bracket_counts"]):
                buckets.setdefault(count, []).append(
                    1 if name in record["reachable"][index] else 0
                )
        counts = sorted(buckets)
        out[name] = {
            "stratum": f"regime={regime}; {name} true of the object",
            "cells": len(stratum),
            "objects": len({record["object"] for record in stratum}),
            "curve": curve_summary(
                counts,
                [sum(buckets[count]) / len(buckets[count]) for count in counts],
                [len(buckets[count]) for count in counts],
                stratum=f"regime={regime}; {name} true of the object",
                measurement=(
                    f"fraction of cells where some writing makes {name} manifest, "
                    "padding admitted"
                ),
                objects=_objects_at(stratum, counts),
            ),
        }
    return out


# ------------------------------------------------------------------ curve A's existence witness
#
# The corpus is 0038's, which is hand-chosen from named identities, so a monotone answer over it is
# a statement about that mathematics and not about the rules.  These four objects are declared
# OUTSIDE the corpus and exist only to answer the separate question: do the opaque rules ADMIT a
# rise at all?  They are not evidence about mathematics and are never pooled with the corpus.
#
# An earlier revision asked these witnesses a second question -- do the rules admit a rise FOLLOWED
# BY A FALL -- and answered yes on a curve computed under an enumeration bound.  That answer is
# withdrawn.  The witnesses still show a rise; they cannot show a peak, and neither can anything
# else, because an attainable curve is a running maximum once a bracket exists to pad.
#
# The corpus answers the existence question too, now that leaf positions are enumerated: 72 of its
# opaque cells rise.  The witnesses are kept because they are declared and because the comparison
# between the two grids is what shows the round 2 defect was in the enumeration and not in the
# mathematics.

BRACKET_WITNESS: tuple[MathObject, ...] = (
    MathObject(
        name="witness_product_of_pairs",
        field="witness",
        variable=None,
        writings=(Writing("paired", "(a * b) * (c * d)"),),
        note=(
            "a product whose two factors are themselves products: under the opaque regime the "
            "bracket is what makes the two compound factors countable, so factor_structure is "
            "invisible at one bracket and visible at two -- and, padding admitted, at every "
            "count above two as well, which is what withdraws the peak this object was declared "
            "to demonstrate"
        ),
    ),
    MathObject(
        name="witness_product_of_sums",
        field="witness",
        variable=None,
        writings=(Writing("paired", "(a + b) * (c + d)"),),
        note="the same shape with additive factors, where the brackets are already forced",
    ),
    MathObject(
        name="witness_triple_product",
        field="witness",
        variable=None,
        writings=(Writing("paired", "(a * b) * (c * d) * e"),),
        note="one factor longer, so the rise and the fall are separated by more than one step",
    ),
    MathObject(
        name="witness_quotient_of_pairs",
        field="witness",
        variable=None,
        writings=(Writing("paired", "(a * b) * (c * d) / f"),),
        note="a denominator, so the numerator-only clause of the factor_structure rule is exercised",
    ),
)


def witness_sweep(workers: int | None = None) -> dict[str, Any]:
    """Curve A over the declared witness objects: does the rule set admit a rise at all?

    This answers a question a monotone corpus could not: a monotone corpus result could mean either
    that the mathematics has no such object or that the rules forbid one.  The witnesses separate
    the two, and the answer is that the rules admit a **rise**.

    They do not admit a **peak**, and this function reports both readings side by side so the round
    1 withdrawal is visible in the output and not only in prose.  ``peaks`` is computed on the
    attainable curve with padding admitted and is empty; ``peaks_before_padding`` is the same
    computation on the unpadded curve, which is what that revision published.
    """
    result = bracket_sweep(BRACKET_WITNESS, GRAMMARS, workers)

    def collect(key: str) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        for record in result["cell_records"]:
            for entry in turning_points(record["bracket_counts"], record[key]):
                if entry["kind"] != "peak":
                    continue
                found.append(
                    {
                        "object": record["object"],
                        "grammar": record["grammar"],
                        "regime": record["regime"],
                        "bracket_counts": record["bracket_counts"],
                        "attainable": record[key],
                        "peak_at": entry["parameter"],
                        "peak_value": entry["value"],
                        "drop_after": entry["drop_after"],
                    }
                )
        return found

    rising = [
        record
        for record in result["cell_records"]
        if monotonicity(record["attainable"]) in ("non-decreasing", "non-monotone")
    ]
    peaks = collect("attainable")
    before_padding = collect("unpadded_attainable")
    return {
        "objects": [item.name for item in BRACKET_WITNESS],
        "cells": result["cells"],
        "cells_that_rise": len(rising),
        "cells_with_a_peak": len(peaks),
        "peaks": peaks,
        "cells_with_a_peak_before_padding": len(before_padding),
        "peaks_before_padding": before_padding,
        "padding_witness": padding_witness(),
        "a_peak_is_impossible": (
            "an attainable curve is a running maximum wherever a bracket exists to double, so it "
            "cannot fall after it has risen; the only fall it admits is the step out of a "
            "bracket-free writing, which no rise can precede"
        ),
        "regime_results": result["regime_results"],
    }


# ------------------------------------------------- curve B: word length against semantic diversity


def operator_word(operators: Sequence[str]) -> str:
    """``a + b * c`` for ``("+", "*")``: distinct operands, one per operator plus one."""
    if len(operators) + 1 > len(OPERAND_NAMES):
        raise ValueError(f"word of {len(operators)} operators needs more operand names")
    names = OPERAND_NAMES[: len(operators) + 1]
    text = names[0]
    for operator, name in zip(operators, names[1:]):
        text += f" {operator} {name}"
    return text


def catalan(index: int) -> int:
    """``C(k)``: the number of parenthesizations of a ``k``-operator word."""
    return comb(2 * index, index) // (index + 1) if index >= 0 else 0


def support_ceiling(support: int, length: int) -> int:
    """The T6 ceiling on distinct parses of a word of that support and length.

    T6 says parsing depends only on the precedence order restricted to the operators that occur, so
    the 24 strict grammars can produce at most ``support!`` distinct trees; the tied control ``G0``
    contributes at most one more.  The Catalan number binds instead whenever the word is too short
    for that many trees to exist.  Every count in curve B is read against this ceiling, because a
    count that merely walks up toward it is the null model and not a finding.
    """
    return min(factorial(support) + 1, catalan(length))


def word_record(operators: tuple[str, ...]) -> dict[str, Any]:
    """Distinct ASTs and distinct semantic classes of one word over the 25 grammars.

    Module level for the ``spawn`` pool.  The semantic key is the project-wide
    ``(canonical, domain, excluded points)`` triple; ``domain`` is inert (NF-2026-00005) and the
    operative discrimination is the other two components.
    """
    source = operator_word(operators)
    trees: dict[Any, Node] = {}
    per_grammar: list[Any] = []
    for grammar in _grammar_registry():
        node = parse(source, grammar)
        key = canonical_tree(node)
        trees.setdefault(key, node)
        per_grammar.append(key)
    classes: dict[Any, tuple[str, str, tuple[str, ...]]] = {}
    for key, node in trees.items():
        canonical = canonicalize(node)
        classes[key] = (
            canonical["expression"],
            canonical["domain"],
            tuple(canonical["excluded_points"]),
        )
    distinct_classes = {classes[key] for key in per_grammar}
    return {
        "source": source,
        "length": len(operators),
        "support": len(set(operators)),
        "distinct_asts": len(trees),
        "distinct_classes": len(distinct_classes),
        "ceiling": support_ceiling(len(set(operators)), len(operators)),
    }


_REGISTRY: tuple[Grammar, ...] | None = None


def _grammar_registry() -> tuple[Grammar, ...]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = all_grammars()
    return _REGISTRY


def _words_of_length(length: int) -> list[tuple[str, ...]]:
    return [tuple(word) for word in product(OPERATORS, repeat=length)]


def _sample_words(length: int, size: int, seed: int) -> list[tuple[str, ...]]:
    """A seeded sample of words of that length, used only past an exhaustive limit."""
    random = Random(seed + length)
    total = len(OPERATORS) ** length
    if total <= size:
        return _words_of_length(length)
    chosen: set[tuple[str, ...]] = set()
    while len(chosen) < size:
        chosen.add(tuple(random.choice(OPERATORS) for _ in range(length)))
    return sorted(chosen)


def length_sweep(
    exhaustive_to: int = 6,
    sampled_to: int = 0,
    sample_size: int = 256,
    seed: int = SAMPLE_SEED,
    workers: int | None = None,
) -> dict[str, Any]:
    """Curve B: distinct semantic classes against word length, inside operator-support strata.

    ``exhaustive_to`` is a computational limit and is labelled as one wherever it is reported: the
    word count is ``4 ** length`` and the per-word cost is a sympy ``simplify`` per distinct parse,
    so the sweep stops being affordable, not stops being interesting.  ``sampled_to`` continues past
    it on a seeded sample so the shape beyond the limit is checked rather than assumed.

    Nothing is pooled across support strata.  T6 fixes a per-stratum ceiling that does not grow with
    length, so a count rising inside a stratum is a fact about meaning; a count rising across the
    pooled corpus would be, mostly, a fact about how many operators the longer words happen to use.
    """
    payloads: list[tuple[str, ...]] = []
    coverage: dict[int, str] = {}
    for length in range(1, exhaustive_to + 1):
        payloads.extend(_words_of_length(length))
        coverage[length] = "exhaustive"
    for length in range(exhaustive_to + 1, sampled_to + 1):
        payloads.extend(_sample_words(length, sample_size, seed))
        coverage[length] = f"sampled {sample_size} of {len(OPERATORS) ** length}"
    records = _map_payloads(word_record, payloads, workers)
    return _length_tables(records, coverage, exhaustive_to, sampled_to, sample_size, seed, workers, len(payloads))


def _sampled_continuation(
    swept: Sequence[dict[str, Any]], beyond: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    """The rows past the exhaustive limit, kept out of the swept curve and reported beside it.

    Two reasons they are not folded into the curve.  They are a *sample* while everything before
    them is a census, so the two are not the same kind of observation; and a uniform sample of long
    words lands almost entirely in the large-support strata, so the small-support rows past the
    limit are thin -- which is exactly the shape that manufactures a turn out of nothing.  The rows
    are published with their word counts and the direction they continue in, and no verdict is
    taken from them.
    """
    if not beyond or not swept:
        return {"rows": [], "thinnest": None, "continues_in_the_same_direction": None}
    if len(swept) >= 2:
        last_step = swept[-1]["mean_distinct_classes"] - swept[-2]["mean_distinct_classes"]
    else:
        last_step = 0.0
    values = [swept[-1]["mean_distinct_classes"]] + [
        row["mean_distinct_classes"] for row in beyond
    ]
    steps = first_differences(values)
    same = all(
        (step >= -EPSILON) if last_step >= -EPSILON else (step <= EPSILON) for step in steps
    )
    return {
        "rows": [
            {
                "length": row["length"],
                "words": row["words"],
                "coverage": row["coverage"],
                "mean_distinct_classes": row["mean_distinct_classes"],
                "mean_distinct_asts": row["mean_distinct_asts"],
                "mean_collapse_ratio": row["mean_collapse_ratio"],
            }
            for row in beyond
        ],
        "thinnest": min(row["words"] for row in beyond),
        "continues_in_the_same_direction": same,
    }


def _length_tables(
    records: Sequence[dict[str, Any]],
    coverage: dict[int, str],
    exhaustive_to: int,
    sampled_to: int,
    sample_size: int,
    seed: int,
    workers: int | None,
    payload_count: int,
) -> dict[str, Any]:
    supports = sorted({record["support"] for record in records})
    strata: dict[str, Any] = {}
    for support in supports:
        rows = [record for record in records if record["support"] == support]
        lengths = sorted({record["length"] for record in rows})
        table = []
        for length in lengths:
            here = [record for record in rows if record["length"] == length]
            table.append(
                {
                    "length": length,
                    "words": len(here),
                    "coverage": coverage[length],
                    "exhaustive": coverage[length] == "exhaustive",
                    "mean_distinct_asts": sum(r["distinct_asts"] for r in here) / len(here),
                    "mean_distinct_classes": sum(r["distinct_classes"] for r in here) / len(here),
                    "max_distinct_classes": max(r["distinct_classes"] for r in here),
                    "ceiling": here[0]["ceiling"],
                    "mean_collapse_ratio": sum(
                        r["distinct_classes"] / r["distinct_asts"] for r in here
                    )
                    / len(here),
                    "mean_ceiling_fraction": sum(
                        r["distinct_classes"] / r["ceiling"] for r in here
                    )
                    / len(here),
                }
            )
        stratum = f"operator support = {support}"
        swept = [row for row in table if row["exhaustive"]]
        beyond = [row for row in table if not row["exhaustive"]]

        def curve(
            field: str, what: str, rows: list[dict[str, Any]] = swept
        ) -> dict[str, Any] | None:
            """A stratum that the exhaustive part of the sweep never reached publishes no curve.

            Building one from the sample alone would put a census and a sample on the same axis.

            The object column equals the cell column here, and that is a fact and not an omission:
            a cell of curve B *is* one word, with no world or writing multiplier behind it, which
            is exactly what makes curve A's two columns differ and these two agree.
            """
            if not rows:
                return None
            return curve_summary(
                [row["length"] for row in rows],
                [row[field] for row in rows],
                [row["words"] for row in rows],
                stratum=stratum,
                measurement=what,
                objects=[row["words"] for row in rows],
            )

        strata[str(support)] = {
            "stratum": stratum,
            "support": support,
            "table": table,
            "exhaustive_lengths": [row["length"] for row in swept],
            "classes_curve": curve("mean_distinct_classes", "mean distinct semantic classes per word"),
            "asts_curve": curve("mean_distinct_asts", "mean distinct ASTs per word"),
            "collapse_curve": curve(
                "mean_collapse_ratio", "mean classes / distinct ASTs (1.0 = no collapse)"
            ),
            "ceiling_curve": curve("mean_ceiling_fraction", "mean classes / T6 ceiling"),
            "sampled_continuation": _sampled_continuation(swept, beyond),
        }
    return {
        "words": payload_count,
        "exhaustive_to": exhaustive_to,
        "exhaustive_limit_is_computational": True,
        "sampled_to": sampled_to,
        "sample_size": sample_size,
        "seed": seed,
        "workers": resolve_sweep_workers(payload_count, workers),
        "coverage": coverage,
        "strata": strata,
        "strata_partition_the_corpus": sum(
            row["words"] for entry in strata.values() for row in entry["table"]
        )
        == payload_count,
        "pooled_warning": (
            "a curve pooled across support strata measures how many operators the longer words "
            "happen to use, which by T6 is the null model; no verdict in this report is taken "
            "from a pooled curve"
        ),
    }


# ------------------------------------------- curve C: convention-axis width against semantic yield


_AXIS_CACHE: dict[tuple[str, ...], tuple[AssociativeGrammar, ...]] = {}


def axis_grammars(freed: Sequence[str]) -> tuple[AssociativeGrammar, ...]:
    """The 24 strict precedence orders, with the operators in ``freed`` taking either side.

    ``freed`` empty gives the Generation 1 registry lifted with every operator left-associative --
    ``24`` grammars, the narrowest axis.  ``freed`` the whole alphabet gives 0030's ``384``.  Every
    intermediate width is a genuine convention axis: it says which operators a culture had made up
    its mind about.
    """
    freed_set = tuple(operator for operator in OPERATORS if operator in set(freed))
    cached = _AXIS_CACHE.get(freed_set)
    if cached is not None:
        return cached
    sides_per_operator = [
        ("left", "right") if operator in freed_set else ("left",) for operator in OPERATORS
    ]
    grammars: list[AssociativeGrammar] = []
    for index, ordering in enumerate(permutations(OPERATORS), start=1):
        levels = tuple((operator,) for operator in ordering)
        for choice in product(*sides_per_operator):
            assignment = dict(zip(OPERATORS, choice))
            grammars.append(
                AssociativeGrammar(
                    f"G{index:02d}-{side_tag(assignment, OPERATORS)}",
                    levels,
                    tuple(assignment.items()),
                )
            )
    _AXIS_CACHE[freed_set] = tuple(grammars)
    return _AXIS_CACHE[freed_set]


#: The nested chain of widenings curve C sweeps, in :data:`AXIS_OPERATOR_ORDER`.
AXIS_CHAIN: tuple[tuple[str, ...], ...] = tuple(
    tuple(AXIS_OPERATOR_ORDER[:width]) for width in range(len(AXIS_OPERATOR_ORDER) + 1)
)


def axis_record(operators: tuple[str, ...]) -> dict[str, Any]:
    """Semantic classes of one word at every axis width, plus the single-operator widenings.

    Module level for the ``spawn`` pool.  The class sets themselves are compared, not just their
    sizes, so the subset claim behind curve C's monotonicity is checked and not assumed.
    """
    source = operator_word(operators)
    cache: dict[Any, tuple[str, str, tuple[str, ...]]] = {}

    def key_of(node: Node) -> tuple[str, str, tuple[str, ...]]:
        tree = canonical_tree(node)
        found = cache.get(tree)
        if found is None:
            canonical = canonicalize(node)
            found = (
                canonical["expression"],
                canonical["domain"],
                tuple(canonical["excluded_points"]),
            )
            cache[tree] = found
        return found

    def classes_for(freed: Sequence[str]) -> set[tuple[str, str, tuple[str, ...]]]:
        return {key_of(associative_parse(source, grammar)) for grammar in axis_grammars(freed)}

    chain = [classes_for(freed) for freed in AXIS_CHAIN]
    singles = {operator: classes_for((operator,)) for operator in OPERATORS}
    base = chain[0]
    nested_ok = all(chain[index] <= chain[index + 1] for index in range(len(chain) - 1))
    singles_ok = all(base <= value for value in singles.values())
    return {
        "source": source,
        "length": len(operators),
        "support": len(set(operators)),
        "chain_sizes": [len(entry) for entry in chain],
        "chain_grammar_counts": [len(axis_grammars(freed)) for freed in AXIS_CHAIN],
        "single_widening_new": {
            operator: len(value - base) for operator, value in singles.items()
        },
        "single_widening_lost": {
            operator: len(base - value) for operator, value in singles.items()
        },
        "nested_widening_never_loses": nested_ok,
        "single_widening_never_loses": singles_ok,
    }


def axis_width_sweep(
    exhaustive_to: int = 5,
    sampled_to: int = 0,
    sample_size: int = 256,
    seed: int = SAMPLE_SEED,
    workers: int | None = None,
) -> dict[str, Any]:
    """Curve C: semantic classes against the width of the convention axis.

    Two things are separated that 0030's headline ratio held together.  The **raw** class count can
    only be non-decreasing in the width, because a wider axis is a superset of grammars and a
    superset of grammars produces a superset of meanings; this is checked on every word, as a set
    inclusion and not as a comparison of counts, so a "decay" in a normalised figure can never be
    read here as a turn.  The **yield** -- new meanings per grammar added -- is the quantity that
    is free to fall, and it does.
    """
    payloads: list[tuple[str, ...]] = []
    coverage: dict[int, str] = {}
    for length in range(1, exhaustive_to + 1):
        payloads.extend(_words_of_length(length))
        coverage[length] = "exhaustive"
    for length in range(exhaustive_to + 1, sampled_to + 1):
        payloads.extend(_sample_words(length, sample_size, seed))
        coverage[length] = f"sampled {sample_size} of {len(OPERATORS) ** length}"
    records = _map_payloads(axis_record, payloads, workers)
    widths = list(range(len(AXIS_CHAIN)))
    grammar_counts = records[0]["chain_grammar_counts"]
    swept_records = [record for record in records if record["length"] <= exhaustive_to]
    beyond_records = [record for record in records if record["length"] > exhaustive_to]
    supports = sorted({record["support"] for record in swept_records})
    strata: dict[str, Any] = {}
    for support in supports:
        rows = [record for record in swept_records if record["support"] == support]
        beyond = [record for record in beyond_records if record["support"] == support]
        means = [sum(row["chain_sizes"][width] for row in rows) / len(rows) for width in widths]
        stratum = f"operator support = {support}"
        strata[str(support)] = {
            "stratum": stratum,
            "support": support,
            "words": len(rows),
            "sampled_continuation": {
                "words": len(beyond),
                "mean_classes_by_width": [
                    sum(row["chain_sizes"][width] for row in beyond) / len(beyond)
                    for width in widths
                ]
                if beyond
                else [],
            },
            "mean_classes_by_width": means,
            "grammars_by_width": grammar_counts,
            "yield_per_grammar_added": [
                (means[index + 1] - means[index]) / (grammar_counts[index + 1] - grammar_counts[index])
                for index in range(len(widths) - 1)
            ],
            "width_curve": curve_summary(
                widths,
                means,
                [len(rows)] * len(widths),
                stratum=stratum,
                measurement="mean distinct semantic classes per word",
                objects=[len(rows)] * len(widths),
            ),
            "single_widening": {
                operator: {
                    "mean_new_classes": sum(
                        row["single_widening_new"][operator] for row in rows
                    )
                    / len(rows),
                    "mean_lost_classes": sum(
                        row["single_widening_lost"][operator] for row in rows
                    )
                    / len(rows),
                    "words_gaining": sum(
                        1 for row in rows if row["single_widening_new"][operator] > 0
                    ),
                }
                for operator in OPERATORS
            },
        }
    return {
        "words": len(payloads),
        "exhaustive_to": exhaustive_to,
        "exhaustive_limit_is_computational": True,
        "sampled_to": sampled_to,
        "sample_size": sample_size,
        "seed": seed,
        "workers": resolve_sweep_workers(len(payloads), workers),
        "coverage": coverage,
        "widths": widths,
        "chain": [list(freed) for freed in AXIS_CHAIN],
        "grammars_by_width": grammar_counts,
        "nested_widening_never_loses": all(record["nested_widening_never_loses"] for record in records),
        "single_widening_never_loses": all(record["single_widening_never_loses"] for record in records),
        "widenings_checked": len(records) * (len(AXIS_CHAIN) - 1 + len(OPERATORS)),
        "words_where_a_widening_lost_a_meaning": sum(
            1
            for record in records
            if not (record["nested_widening_never_loses"] and record["single_widening_never_loses"])
        ),
        "exhaustive_words": len(swept_records),
        "sampled_words": len(beyond_records),
        "strata": strata,
        "strata_partition_the_corpus": sum(entry["words"] for entry in strata.values())
        == len(swept_records),
    }


# ------------------------------------------------------------------------------- pooling discipline


def _argmax_by_curve(report: dict[str, Any]) -> list[dict[str, Any]]:
    """The argmax of every curve the report publishes, gathered in one place.

    The methods paragraph promises an argmax for every curve, so it is produced for every curve
    rather than for the one the prose happened to discuss.  The walk is the same one
    :func:`pooling_audit` performs, so the two lists have the same length by construction.
    """
    found: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "measurement" in node and "monotone" in node and "sample_size" in node:
                found.append(
                    {
                        "stratum": node.get("stratum"),
                        "measurement": node["measurement"],
                        "argmax": node.get("argmax"),
                        "monotone": node.get("monotone"),
                        "still_moving_at_end": node.get("still_moving_at_end"),
                        "argmax_is_the_last_point": bool(node.get("parameter"))
                        and node.get("argmax", {}).get("parameter") == node["parameter"][-1],
                    }
                )
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(report)
    return found


def pooling_audit(report: dict[str, Any]) -> dict[str, Any]:
    """Every rate in the report carries a stratum, and no stratum's sample is a pooled one.

    This is the mechanical form of the card's rule.  It walks the whole report, finds every curve
    record, and checks two things: the curve names a stratum, and its per-point sample sizes are
    present.  A curve whose stratum is missing or empty is a defect and is listed.

    The thin-point verdict counts **objects** wherever a curve carries an object column, and cells
    only where it does not.  A curve A point at thirteen brackets holds fifty cells and two
    objects; reading its thickness off the cell column would hide exactly the tail this card is
    about.
    """
    curves: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "measurement" in node and "monotone" in node and "sample_size" in node:
                curves.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(report)
    without_stratum = [
        curve["measurement"] for curve in curves if not curve.get("stratum")
    ]
    without_samples = [
        curve["measurement"] for curve in curves if not curve.get("sample_size")
    ]
    def thickness(curve: dict[str, Any]) -> tuple[int, str]:
        if curve.get("minimum_objects") is not None:
            return int(curve["minimum_objects"]), "objects"
        return int(curve.get("minimum_sample_size", 0)), "cells"

    thin = []
    for curve in curves:
        smallest, counted = thickness(curve)
        if smallest >= 3:
            continue
        thin.append(
            {
                "stratum": curve.get("stratum"),
                "measurement": curve["measurement"],
                "counted": counted,
                "thinnest_point": smallest,
                "minimum_sample_size": curve.get("minimum_sample_size", 0),
                "minimum_objects": curve.get("minimum_objects"),
            }
        )
    return {
        "curves": len(curves),
        "curves_without_stratum": without_stratum,
        "curves_without_sample_sizes": without_samples,
        "curves_with_an_object_column": sum(
            1 for curve in curves if curve.get("minimum_objects") is not None
        ),
        "every_curve_is_stratified": not without_stratum and not without_samples,
        "curves_with_a_thin_point": thin,
        "thin_point_threshold": 3,
        "thin_point_counts": "objects where the curve has an object column, cells otherwise",
    }


# ---------------------------------------------------------------------------------- multicore


def parallel_decision(
    word_length: int = 4,
    workers: int | None = None,
) -> dict[str, Any]:
    """Measure, rather than assume, whether each sweep should run across processes.

    The two sweeps have different shapes and the observation says so, which is why one constant
    cannot serve both.  Curve A's unit of work is a whole writing's bracket-pattern census -- up to
    ``77336`` patterns, each one seven shape rules over a surface tree -- and it is skewed: two of
    the fifty writings hold more than half the patterns in the corpus.  Curve B's word record is a
    sympy ``simplify`` per distinct parse.  Both are CPU-bound Python that holds the GIL, so
    threads are not in the comparison.
    """
    detected = os.cpu_count() or 1
    grammar_ids = tuple(grammar.id for grammar in GRAMMARS)
    payloads = [
        (item.name, writing.role, grammar_ids)
        for item in MANIFEST_CORPUS
        for writing in item.writings
    ]
    count = resolve_workers(len(payloads), workers)
    start = time.perf_counter()
    sequential_cells = [writing_cells(payload) for payload in payloads]
    cells_sequential = time.perf_counter() - start
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=count) as pool:
        parallel_cells = list(pool.map(writing_cells, payloads, chunksize=1))
    cells_parallel = time.perf_counter() - start

    words = _words_of_length(word_length)
    word_workers = resolve_workers(len(words), workers)
    start = time.perf_counter()
    sequential_words = [word_record(word) for word in words]
    words_sequential = time.perf_counter() - start
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=word_workers) as pool:
        parallel_words = list(
            pool.map(word_record, words, chunksize=max(1, len(words) // (word_workers * 4)))
        )
    words_parallel = time.perf_counter() - start
    return {
        "detected_cores": detected,
        "workers": count,
        "writing_pattern_censuses": {
            "items": len(payloads),
            "sequential_seconds": cells_sequential,
            "parallel_seconds": cells_parallel,
            "speedup": cells_sequential / cells_parallel if cells_parallel else None,
            "identical": sequential_cells == parallel_cells,
            "decision": "parallel" if cells_parallel < cells_sequential else "sequential",
            "floor_in_use": PATTERN_MINIMUM_ITEMS,
        },
        "word_records": {
            "items": len(words),
            "sequential_seconds": words_sequential,
            "parallel_seconds": words_parallel,
            "speedup": words_sequential / words_parallel if words_parallel else None,
            "identical": sequential_words == parallel_words,
            "decision": "parallel" if words_parallel < words_sequential else "sequential",
            "floor_in_use": PARALLEL_MINIMUM_ITEMS,
        },
        "note": (
            "the two payloads sit on opposite sides of any single crossover, which is why one "
            "constant cannot serve both and why the sweeps take an explicit worker count"
        ),
    }


# ------------------------------------------------------------------------------------- the report


def turning_points_report(
    length_exhaustive_to: int = 6,
    length_sampled_to: int = 0,
    axis_exhaustive_to: int = 5,
    axis_sampled_to: int = 0,
    sample_size: int = 256,
    workers: int | None = None,
    include_parallel_decision: bool = False,
    corpus: Sequence[MathObject] | None = None,
    grammars: Sequence[Grammar] | None = None,
    enumeration_sample: int = 4000,
) -> dict[str, Any]:
    """Every swept curve of experiment 0047, with its shape and never only its extremum.

    ``corpus`` and ``grammars`` narrow curve A and its audits together, so a caller that wants the
    report's shape without its cost gets a *consistent* smaller report rather than a full sweep
    beside a partial audit.
    """
    brackets = bracket_sweep(corpus, grammars, workers=workers)
    witness = witness_sweep(workers=workers)
    audit = writing_audit(corpus, grammars, workers=workers)
    completeness = enumeration_audit(corpus, grammars, sample=enumeration_sample)
    lengths = length_sweep(
        exhaustive_to=length_exhaustive_to,
        sampled_to=length_sampled_to,
        sample_size=sample_size,
        workers=workers,
    )
    axis = axis_width_sweep(
        exhaustive_to=axis_exhaustive_to,
        sampled_to=axis_sampled_to,
        sample_size=sample_size,
        workers=workers,
    )
    report: dict[str, Any] = {
        "withdrawn": WITHDRAWN,
        "witnesses": {
            "round_1_padding": padding_witness(),
            "round_2_leaf_bracket": leaf_bracket_witness(),
        },
        "curves": {
            "brackets": {
                key: value for key, value in brackets.items() if key != "cell_records"
            },
            "brackets_witness": witness,
            "length": lengths,
            "axis_width": axis,
        },
        "audits": {
            "writings_denote_one_object": audit,
            "enumeration_completeness": completeness,
        },
        "what_each_sweep_does_not_produce": [
            {
                "curve": "A",
                "not_produced": "writings with a bracket inside a bracket",
                "why_it_cannot_change_the_answer": (
                    "such a writing has the manifest set of its outermost-bracket pattern, which "
                    "the census already holds, and at least that pattern's bracket count, where "
                    "the running maximum has already carried the value"
                ),
                "checked": completeness,
            },
            {
                "curve": "B",
                "not_produced": (
                    f"words longer than {length_sampled_to or length_exhaustive_to}, and words "
                    "that repeat an operand"
                ),
                "why_it_cannot_change_the_answer": (
                    "the T6 ceiling of a support stratum does not grow with length, so the curve "
                    "can only saturate; repeated operands would add collapse the operators did "
                    "not force, which is a different question and is declared as one"
                ),
                "checked": lengths["coverage"],
            },
            {
                "curve": "C",
                "not_produced": (
                    f"words longer than {axis_sampled_to or axis_exhaustive_to}, and orders of "
                    "freeing operators other than the declared one"
                ),
                "why_it_cannot_change_the_answer": (
                    "a wider axis is a superset of grammars, checked as a set inclusion on every "
                    "word, and every single-operator widening is reported on its own beside the "
                    "declared chain"
                ),
                "checked": axis["coverage"],
            },
        ],
        "computational_limits": [
            {
                "name": f"word length <= {length_exhaustive_to} exhaustive (curve B)",
                "curve": "B",
                "why": "4**length words, each costing a sympy simplify per distinct parse",
                "beyond": lengths["coverage"],
                "checked": length_sampled_to > length_exhaustive_to,
            },
            {
                "name": f"word length <= {axis_exhaustive_to} exhaustive (curve C)",
                "curve": "C",
                "why": "each word is parsed under up to 384 grammars before the sympy step",
                "beyond": axis["coverage"],
                "checked": axis_sampled_to > axis_exhaustive_to,
            },
        ],
    }
    report["pooling_audit"] = pooling_audit(report)
    report["argmax_by_curve"] = _argmax_by_curve(report)
    if include_parallel_decision:
        report["parallel_decision"] = parallel_decision(workers=workers)
    return report
