"""Experiment 0053: the model against the metal.

The owner set this card on 2026-09-05, and the sentence that governs every decision in this module
is his:

    "The point is to arrange the dataflow for the processor according to different representations
     so you can SEE which is more efficient.  And formulas are good, but hardware often has hidden
     parts that do not match the formulas, and sometimes on real hardware a different representation
     becomes the profitable one."

This project measures three structural quantities on the emitted tree -- operation count
(:func:`parseatlas.canonical.operation_cost`, card 0021), critical-path depth
(:func:`parseatlas.parallel_worlds.depth`, card 0041) and peak live values
(:func:`parseatlas.memory_ceiling.peak_live`, card 0044).  **They are a model, and hardware does not
implement that model literally.**  This module measures where the model and the machine disagree, by
emitting C, compiling it and running it.

Nothing here re-implements a structural measure.  All three are imported from the card that owns
them, and :func:`structural_profile` is the only place they are read.

The four divergences, each with a reason to expect one
------------------------------------------------------

``division``
    The project counts ``/`` exactly as it counts ``*``.  On hardware a division has many times the
    latency of a multiplication and is not fully pipelined, so a writing that trades one division
    for several multiplications LOSES in the project's count and should WIN on the machine.

``fma``
    ``a*b + c`` is two operations at depth 2 in the model and one instruction at depth 1 on the
    machine, with one rounding instead of two.

``latency``
    Independent operations pipeline; dependent ones do not.  Depth is supposed to capture this.

``registers``
    The model counts architectural pressure; the machine has far more physical registers.

What is measured, and what is not
---------------------------------

Two regimes are timed, because the model makes two different predictions and one loop cannot test
both:

``throughput``
    Four independent copies of the expression per loop step, four accumulators, inputs read from a
    table.  Successive loop steps are independent, so the machine may overlap them and what binds is
    the number of operations issued.  This is the regime **operation count** is supposed to predict.

``latency``
    One accumulator, and the previous result is fed back into ONE input -- a variable occurring at
    the greatest depth in the tree -- through ``acc * FEEDBACK_SCALE``.  Successive loop steps
    cannot overlap, so what binds is the longest chain of dependent operations.  This is the regime
    **depth** is supposed to predict.

**The feedback goes into one input and not into all of them, and the reason is a defect this card
found in its own first harness.**  With the same perturbation added to every input, a subtraction of
two variables cancels it exactly -- ``(x + fb) - (h + fb)`` is ``x - h`` -- and at ``-ffast-math``
clang performs that cancellation, after which nothing in the loop depends on the accumulator, only
the last loop step's value is observable, and the compiler deletes the loop.  It did: the circle's
centre-radius writing timed at ``0.00`` seconds per step at ``O3fast`` before the harness was
changed.  Feeding one deep variable leaves no term to cancel against, and
:func:`latency_path_audit` reports, for every writing, whether the fed leaf really does sit at the
tree's full depth -- because where it does not, the regime measures a shorter path than ``depth``
and the comparison must say so.

Preventing the optimiser from deleting the work
-----------------------------------------------

A benchmark that measures an empty loop is the classic failure of this kind of work, so the guard is
stated here and it is tested, not asserted:

1. every input is read from a table indexed by the loop counter, so no part of the expression is
   loop-invariant and none of it can be hoisted out;
2. every loop step's result is accumulated;
3. the accumulator is written through a pointer the caller owns, added into a checksum, stored into
   a ``volatile double`` and **printed**, so it is observable behaviour that the standard forbids the
   compiler to discard.

:func:`guard_audit` compiles the same kernels a second time with step 2 and 3 removed -- the
accumulator computed and then dropped -- and reports the ratio of the two timings.  Without the
guard the loop is dead and clang deletes it; the measured ratio is the evidence.

Two halves, and only one of them reproduces
-------------------------------------------

**This is the most important thing to know before reading any number out of this module, and it was
established by review re-running the card rather than by the card noticing it.**

The *instruction-level* half -- :func:`instruction_audit`, :func:`loop_instruction_audit` and
:func:`flag_isolation_audit` -- reads mnemonics out of clang's own assembly.  It has no stopwatch in
it, no noise floor, and no dependence on what else the machine is doing.  It reproduced to the digit
on a different machine state with an independently written harness: identical-instruction counts of
``3/16`` at ``O0``, ``0/16`` at ``O2``, ``0/16`` at ``O2nativefma`` and ``8/16`` at ``O3fast``, the
same eight objects named at ``O3fast`` and the same three at ``O0``.

The *time* half does not reproduce at this precision.  The card's first revision published ``54`` of
``64`` cells in which the choice between two writings reaches the metal; three independent quiet
re-runs by review returned ``46``, ``47`` and ``49``, and seven repeats here returned ``49`` to
``51``.  :func:`survival_repeatability` is the instrument that makes this visible, and on this
machine it reports **zero of the eight ``(level, mode)`` cells returning the same count in every
repeat.**  Timing figures from this module are therefore to be published as ranges over repeated
runs, or reported as unresolvable -- never as a single reading, and never as a midpoint of readings
that disagree.

So: open with the instruction count, which is exact, and read the timings as a range beneath it.

This machine, this compiler, this version
-----------------------------------------

Every number this module produces is labelled with :func:`environment`, and a different CPU or a
different compiler could reorder every finding in it.  Nothing here generalises beyond the box it
ran on.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

from .canonical import operation_cost  # 0021: the operation multiset and the tree depth
from .grammar import Grammar, control_grammar
from .memory_ceiling import peak_live  # 0044: Sethi-Ullman simultaneously live values
from .parallel_worlds import depth  # 0041: critical path, a leaf at 0
from .parser import Binary, Node, Number, Variable, parse

__all__ = [
    "BASE_START",
    "BASE_STEP",
    "CALIBRATION_LEAVES",
    "CORPUS",
    "CompilationError",
    "DEFAULT_ITERATIONS",
    "DEFAULT_TRIALS",
    "FEEDBACK_SCALE",
    "FLAG_COMBINATIONS",
    "FLOOR_SWEEP",
    "LEVELS",
    "LEVEL_BY_NAME",
    "Level",
    "MIN_BLOCK_TICKS",
    "MODEL_AXES",
    "MODES",
    "MODE_AXIS",
    "OPERATION_KEYS",
    "PARAMETER_PREFIX",
    "PIN_CORE",
    "PROBE_PREDICTIONS",
    "PUBLISHED_FLOOR",
    "REPETITION_SWEEP",
    "Subject",
    "TABLE_SIZE",
    "TOLERANCE",
    "WORKER_CAP",
    "WORKER_HEADROOM_CORES",
    "Writing",
    "agreement_table",
    "asap_width",
    "base_values",
    "benchmark",
    "clang_available",
    "clang_target",
    "clang_version",
    "compile_program",
    "correctness_audit",
    "deepest_variable",
    "default_worker_count",
    "divergence_probes",
    "emit_c",
    "emit_check_program",
    "emit_program",
    "emit_statements",
    "environment",
    "evaluate",
    "flag_isolation_audit",
    "fma_sites",
    "guard_audit",
    "harness_calibration",
    "input_row",
    "instruction_audit",
    "latency_path_audit",
    "loop_instruction_audit",
    "metal_report",
    "noise_floor",
    "parallel_decision",
    "peak_live_bound_table",
    "probe_repeatability",
    "probe_subjects",
    "repetition_curve",
    "slot_map",
    "structural_profile",
    "survival_repeatability",
    "survival_table",
    "tree_of",
    "variables_of",
    "worker_count_for",
]


CONTROL: Grammar = control_grammar()

#: The operation keys of :func:`parseatlas.canonical.operation_cost` that count issued work.
OPERATION_KEYS: tuple[str, ...] = ("add", "sub", "mul", "div")

#: Prefix given to every emitted C parameter, so no corpus variable name can collide with a C
#: keyword, with a temporary, or with anything in the driver.
PARAMETER_PREFIX: str = "x_"

#: Rows in the per-variable input table.  Sixty-four doubles per variable keeps the whole table in
#: L1 for every corpus in this module (the widest is 40 variables, 20 KB) so the timings are about
#: arithmetic and not about the memory hierarchy.
TABLE_SIZE: int = 64

#: First base value, and the step between consecutive variables' base values.  Every base is
#: distinct and at least ``1``, which is what keeps denominators away from zero and keeps
#: differences such as ``x2 - x1`` away from catastrophic cancellation.  Both are dyadic, and the
#: table fill multiplies by ``(256 + j) / 256``, so **every input is an exact double** and the
#: reference oracle can reproduce it exactly as a rational.
BASE_START: Fraction = Fraction(1)
BASE_STEP: Fraction = Fraction(1, 16)

#: The scale by which the previous loop step's result is folded back into ONE input in latency
#: mode -- the variable leaf furthest from the root.  Small enough that the input is unchanged to
#: fifteen significant figures, large enough that the value is a normal double and the dependency is
#: real.  See the module docstring for why one input and not all of them.
FEEDBACK_SCALE: float = 1e-18

#: Relative tolerance for the correctness check against the exact-rational oracle.  Declared once,
#: uniformly, and deliberately far looser than the rounding error a straight-line double evaluation
#: can accumulate: the check exists to catch a function that computes something ELSE, and
#: :func:`correctness_audit` reports the observed maximum so the margin is on the page.
TOLERANCE: Fraction = Fraction(1, 10**9)

#: Loop steps per timed block, and timed blocks per kernel.
#:
#: **Both chosen from the sweep in :func:`repetition_curve`, not declared and trusted.**  Over
#: ``4096`` to ``4194304`` loop steps the seconds-per-step figure falls and then stops moving, while
#: the measured noise floor (:func:`noise_floor`, the gap between two byte-identical kernels) sits
#: near ``2%`` across that whole range.  The floor is therefore set by interference on the machine
#: and not by the timer, so a longer block buys nothing after the flattening; ``262144`` steps is
#: the shortest point past it.  More timed blocks do help, because the statistic reported is a
#: median.
#:
#: **"Stops moving" is not "stops moving monotonically", and an earlier revision of this module
#: implied that it was.**  Over ``48`` sweeps recorded here the drift between two consecutive points
#: ranged from ``0.00%`` to ``73.13%`` with a median of ``5.56%``, and the largest drift landed on
#: the LAST point in several of them.
#:
#: **Nor is there a bound on it, and a second revision implied THAT.**  It said that some pair of
#: consecutive points at or past ``262144`` always agrees to within ``2.82%``; that was the largest
#: value seventeen sweeps had produced, not a bound.  The same statistic over ``48`` sweeps ranges
#: from ``0.06%`` to ``11.43%`` with a median of ``1.82%`` and exceeds ``2.82%`` in ``17`` of them,
#: and review watched the test built on it fail one run in five.  The drift is heavy-tailed; it is
#: now published with its spread in section 2 of the reports and nothing asserts a bound on it.
#: What the sweep is read for is unchanged: the seconds-per-step figure falls steeply to ``262144``
#: and the timer stops binding there, at ``1080`` ticks per block.
DEFAULT_ITERATIONS: int = 262144
DEFAULT_TRIALS: int = 41

#: The repetition counts :func:`repetition_curve` sweeps.  Powers of four from a block far shorter
#: than the timer's tick to one of several milliseconds, so both ends of the curve are visible.
REPETITION_SWEEP: tuple[int, ...] = (4096, 16384, 65536, 262144, 1048576, 4194304)

#: The shortest timed block, in timer ticks, that is allowed to count as a measurement.
#:
#: The timer on this machine runs at ``10`` MHz, so one tick is ``100`` ns.  A block that comes back
#: under ten of them is not a fast kernel, it is a kernel whose loop the compiler removed -- which is
#: exactly what happened to the circle's centre-radius writing at ``O3fast`` before the latency
#: harness was fixed.  Every function that draws an order refuses to run on a benchmark that reports
#: one.
MIN_BLOCK_TICKS: int = 10

#: The two regimes.  See the module docstring.
MODES: tuple[str, ...] = ("throughput", "latency")

#: The logical core every timed program pins itself to.
#:
#: Two things are done to the timed process and both are declared rather than hidden: it is pinned
#: to ONE core, and it is raised to ``HIGH_PRIORITY_CLASS``.  Neither makes a writing faster than
#: another -- both writings are timed inside the same pinned, raised process, in the same round --
#: but without them the operating system moves the thread between cores mid-block and the observed
#: p10-p90 band on this machine reached ``132%``, which is not a band a ranking can be read out of.
#: Core ``2`` rather than core ``0`` because core ``0`` is where Windows services interrupts.
PIN_CORE: int = 2


@dataclass(frozen=True)
class Level:
    """One optimisation level: a name, the exact clang flags, and what it is here to answer."""

    name: str
    flags: tuple[str, ...]
    note: str


#: The optimisation ladder.  Four rungs, and the reason for each is the sub-question the card says
#: may decide it: how much of a representation choice survives the compiler.
#:
#: ``O0`` preserves the emitted graph literally -- one machine operation per tree node, nothing
#: reassociated, nothing fused.  It is the closest a real compiler comes to executing the model.
#:
#: ``O2`` is ordinary optimisation with IEEE semantics.  clang's default is ``-ffp-contract=on``,
#: which fuses only WITHIN one statement; this module emits one operation per statement, so at this
#: rung there is no fusion.  That is not an accident of the emitter, it is the control for ``O2nativefma``.
#:
#: ``O2nativefma`` adds ``-march=native`` AND ``-ffp-contract=fast``.  **It varies two things, and
#: the name says both, because an earlier revision of this module called this rung ``O2fma`` and
#: claimed "the ONLY difference from O2 is fusion".  That was false, and review caught it.**
#: :func:`flag_isolation_audit` measures each flag on its own and the result is decisive:
#:
#: .. code-block:: text
#:
#:     -O2 -ffp-contract=fast     34 of 34 kernels byte-identical to -O2, 0 FMAs
#:     -O2 -march=native          34 of 34 kernels CHANGED, 1542 VEX instructions, 0 FMAs
#:     both                       34 of 34 changed, 191 FMAs
#:
#: So the contract flag alone does nothing and the ISA flag alone fuses nothing.  **The two effects
#: cannot be separated into two rungs**, and that is measured rather than assumed: the narrowest ISA
#: switch that makes fusion possible at all, ``-mfma``, already changes every one of the 34 kernels
#: by itself while still emitting zero FMAs, because it also switches the encoding to VEX.  There is
#: no flag that adds fusion and changes nothing else, so this rung is reported as what it is -- an
#: ISA change and a fusion change together -- rather than split into a difference the compiler does
#: not offer.
#:
#: ``O3fast`` is ``-ffast-math``: the compiler may reassociate, may replace a division by a
#: reciprocal multiplication, and may vectorise freely.  This is the rung that can erase a
#: representation difference before the CPU ever sees it.
LEVELS: tuple[Level, ...] = (
    Level("O0", ("-O0",), "structure preserved literally"),
    Level("O2", ("-O2",), "ordinary optimisation, IEEE semantics, no cross-statement fusion"),
    Level(
        "O2nativefma",
        ("-O2", "-march=native", "-ffp-contract=fast"),
        "TWO changes: the native ISA and cross-statement multiply-add fusion, which flag "
        "isolation shows cannot be varied one at a time",
    ),
    Level(
        "O3fast",
        ("-O3", "-march=native", "-ffast-math"),
        "the compiler may reassociate, reciprocate and vectorise",
    ),
)

LEVEL_BY_NAME: dict[str, Level] = {level.name: level for level in LEVELS}


# ------------------------------------------------------------------------------------ the corpus


@dataclass(frozen=True)
class Writing:
    """One written form of one object: the role it plays and the source that spells it."""

    subject: str
    role: str
    source: str

    @property
    def key(self) -> str:
        return f"{self.subject}__{self.role}"


@dataclass(frozen=True)
class Subject:
    """One mathematical object together with every equivalent writing this card compiles.

    Every writing of a subject denotes the SAME value.  That is checked and not assumed:
    :func:`correctness_audit` evaluates every emitted function against the exact-rational oracle on
    declared inputs, so two writings that disagree fail before any timing is believed.
    """

    name: str
    field: str
    note: str
    writings: tuple[Writing, ...]

    @property
    def roles(self) -> tuple[str, ...]:
        return tuple(writing.role for writing in self.writings)


def _subject(name: str, field: str, note: str, *pairs: tuple[str, str]) -> Subject:
    return Subject(name, field, note, tuple(Writing(name, role, source) for role, source in pairs))


#: The agreement corpus: hand-chosen, and the hand is declared.
#:
#: Sixteen objects.  Fourteen take both writings verbatim from the project's own named-law corpus
#: (:data:`parseatlas.manifest_properties.CORPUS`, which is 0037's law corpus), so the ranking this
#: card measures is a ranking of writings the project already publishes.  Two of those objects get
#: a third writing added here, a Horner form in each case, because the divergences the card names are
#: about shapes the project's corpus does not happen to contain.  The last two objects are pure
#: association chains, where operation count is held fixed and only the shape moves.
#:
#: It is hand-chosen and that is a limitation, stated in both reports: a different sixteen objects
#: could give a different disagreement count.
CORPUS: tuple[Subject, ...] = (
    _subject(
        "distributive_law",
        "algebra",
        "one multiplication against two, the smallest expanded/factored pair in the corpus",
        ("factored", "a * (b + c)"),
        ("expanded", "a * b + a * c"),
    ),
    _subject(
        "binomial_square",
        "algebra",
        "two operations against six",
        ("factored", "(a + b) * (a + b)"),
        ("expanded", "a * a + 2 * a * b + b * b"),
    ),
    _subject(
        "difference_of_squares",
        "algebra",
        "equal operation counts, different shapes",
        ("factored", "(a + b) * (a - b)"),
        ("expanded", "a * a - b * b"),
    ),
    _subject(
        "difference_of_cubes",
        "algebra",
        "the expanded side is CHEAPER in the model, which is the reverse of the usual pair",
        ("factored", "(a - b) * (a * a + a * b + b * b)"),
        ("expanded", "a * a * a - b * b * b"),
    ),
    _subject(
        "quadratic",
        "algebra",
        "three writings of one quadratic, including the Horner form the corpus does not carry",
        ("factored", "a * (x - r) * (x - s)"),
        ("expanded", "a * x * x - a * (r + s) * x + a * r * s"),
        ("horner", "(a * x - a * r - a * s) * x + a * r * s"),
    ),
    _subject(
        "calibration_quadratic",
        "algebra",
        "0038's calibration object, plus its Horner form",
        ("expanded", "2 * x * x + 3 * x - 5"),
        ("factored", "(2 * x + 5) * (x - 1)"),
        ("horner", "(2 * x + 3) * x - 5"),
    ),
    _subject(
        "perfect_square_trinomial",
        "algebra",
        "a squared binomial against its expansion",
        ("factored", "(2 * x + 3) * (2 * x + 3)"),
        ("expanded", "4 * x * x + 12 * x + 9"),
    ),
    _subject(
        "line",
        "geometry",
        "point-slope against slope-intercept",
        ("point_slope", "y1 + m * (x - x1)"),
        ("slope_intercept", "m * x + y1 - m * x1"),
    ),
    _subject(
        "circle",
        "geometry",
        "centre-radius against the general form, the widest operation gap in the corpus",
        ("center_radius", "(x - h) * (x - h) + (y - k) * (y - k)"),
        ("general", "x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k"),
    ),
    _subject(
        "parabola",
        "geometry",
        "vertex form against standard form",
        ("vertex", "a * (x - h) * (x - h) + k"),
        ("standard", "a * x * x - 2 * a * h * x + a * h * h + k"),
    ),
    _subject(
        "trapezoid_area",
        "geometry",
        "one division against two",
        ("mean_times_height", "(a + b) / 2 * h"),
        ("sum_of_halves", "a * h / 2 + b * h / 2"),
    ),
    _subject(
        "difference_quotient",
        "calculus",
        "one division against two, at equal-looking cost",
        ("closed", "(fxh - fx) / h"),
        ("split", "fxh / h - fx / h"),
    ),
    _subject(
        "quotient_rule",
        "calculus",
        "EQUAL operation counts, one division against two: the division divergence in the wild",
        ("closed", "(du * v - u * dv) / (v * v)"),
        ("split", "du / v - u * dv / (v * v)"),
    ),
    _subject(
        "linear_approximation",
        "calculus",
        "point form against slope-intercept form",
        ("point_form", "fa + dfa * (x - a)"),
        ("slope_intercept", "fa - dfa * a + dfa * x"),
    ),
    _subject(
        "sum_chain_8",
        "association",
        "eight terms, seven additions, chained against balanced: operation count held fixed",
        ("chained", "a + b + c + d + e + f + g + h"),
        ("balanced", "((a + b) + (c + d)) + ((e + f) + (g + h))"),
    ),
    _subject(
        "product_chain_8",
        "association",
        "eight factors, seven multiplications, chained against balanced",
        ("chained", "a * b * c * d * e * f * g * h"),
        ("balanced", "((a * b) * (c * d)) * ((e * f) * (g * h))"),
    ),
)


@lru_cache(maxsize=None)
def tree_of(source: str) -> Node:
    """The parser tree of a source string, under the control grammar ``G0``.

    ``G0`` is the control because it is how mathematics is written today, so parsing a conventional
    source under it recovers the intended object rather than imposing one.  Cached because every
    structural profile, every emission and every oracle evaluation asks for the same trees.
    """
    return parse(source, CONTROL)


def variables_of(tree: Node) -> tuple[str, ...]:
    """The distinct variable names of a tree, in sorted order.

    Sorted rather than in order of appearance, so that the emitted signature of a tree depends on
    the tree alone and never on how it was written down.
    """
    names: set[str] = set()
    stack = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, Variable):
            names.add(node.name)
        elif isinstance(node, Binary):
            stack.append(node.left)
            stack.append(node.right)
    return tuple(sorted(names))


# ------------------------------------------------------------------------------ structural model


def fma_sites(tree: Node) -> int:
    """How many multiply-add fusion opportunities the tree contains.

    A site is an ``+`` or ``-`` node with a ``*`` child: exactly the ``a*b + c`` shape an FMA
    instruction implements in one operation with one rounding.  This counts a property of the tree,
    not of any compilation of it; :func:`instruction_audit` counts what clang actually emitted.
    """
    if not isinstance(tree, Binary):
        return 0
    here = 0
    if tree.operator in ("+", "-"):
        for child in (tree.left, tree.right):
            if isinstance(child, Binary) and child.operator == "*":
                here += 1
    return here + fma_sites(tree.left) + fma_sites(tree.right)


def asap_width(tree: Node) -> int:
    """The widest level of the as-soon-as-possible schedule of the tree.

    Every operation is placed at the earliest step its operands allow -- one plus the height of its
    deepest child -- and this is the largest number of operations that land on one step.  It is how
    many operations are ready to issue at once at the busiest moment, so it is the quantity that
    decides whether a machine with several execution units can use them.

    **This is not a project measure.**  0021 counts operations, 0041 measures the critical path and
    0044 measures live values; none of the three sees this.  It is computed here for one purpose: to
    say what an inversion the four declared divergences cannot explain is made of.  Two trees can
    agree on all three project axes and still differ in it, and this card's fourth probe is exactly
    such a pair.
    """
    levels: dict[int, int] = {}

    def walk(node: Node) -> int:
        if not isinstance(node, Binary):
            return 0
        height = 1 + max(walk(node.left), walk(node.right))
        levels[height] = levels.get(height, 0) + 1
        return height

    walk(tree)
    return max(levels.values(), default=0)


def structural_profile(tree: Node) -> dict[str, int]:
    """The model's numbers for one tree, each read from the card that owns it.

    ``operations`` is the sum of ``add``, ``sub``, ``mul`` and ``div`` from 0021's
    :func:`parseatlas.canonical.operation_cost` -- **the four counted alike**, which is the premise
    divergence 1 attacks.  ``depth`` is 0041's, ``peak_live`` is 0044's.  ``fma_sites`` is this
    card's own and is not a project measure; it is here only to explain a disagreement.
    """
    cost = operation_cost(tree)
    return {
        "operations": sum(cost[key] for key in OPERATION_KEYS),
        "add": cost["add"],
        "sub": cost["sub"],
        "mul": cost["mul"],
        "div": cost["div"],
        "depth": depth(tree),
        "peak_live": peak_live(tree),
        "fma_sites": fma_sites(tree),
        "asap_width": asap_width(tree),
        "leaves": (cost["nodes"] + 1) // 2,
    }


# ----------------------------------------------------------------------------------- the oracle


def _constant(value: Fraction) -> Fraction:
    """The exact rational the C program will actually hold for a literal constant.

    A tree constant is an exact rational; a ``double`` is not.  The oracle must compare against what
    the machine was GIVEN, so the constant is rounded to the nearest double once, here, and the
    rounded value is what both the emitter and the oracle use.  Every constant in this card's corpus
    is already exact in binary, so the rounding is the identity on it -- but a corpus that added
    ``x / 3`` would otherwise fail the check for a reason that is not an error.
    """
    return Fraction(float(value))


def evaluate(tree: Node, inputs: dict[str, Fraction]) -> Fraction:
    """Evaluate a tree exactly, in rational arithmetic, as the reference oracle.

    This is the correctness authority Phase 11 requires and the emitted C is checked against it.  It
    is exact: no rounding happens anywhere in it, so the whole of any difference from the C result
    is the machine's floating-point rounding and none of it is the oracle's.
    """
    if isinstance(tree, Number):
        return _constant(tree.value)
    if isinstance(tree, Variable):
        try:
            return inputs[tree.name]
        except KeyError:
            raise KeyError(f"no declared input for variable {tree.name!r}") from None
    left = evaluate(tree.left, inputs)
    right = evaluate(tree.right, inputs)
    if tree.operator == "+":
        return left + right
    if tree.operator == "-":
        return left - right
    if tree.operator == "*":
        return left * right
    if tree.operator == "/":
        if right == 0:
            raise ZeroDivisionError(f"the declared inputs make a denominator zero in {tree!r}")
        return left / right
    raise ValueError(f"unsupported operator: {tree.operator!r}")


def slot_map(writings: Sequence[Writing]) -> dict[str, int]:
    """The input-table slot of every variable used by any of ``writings``, in sorted order.

    One table for the whole program, one slot per NAME.  Two writings of the same object therefore
    read the same values from the same slots, which is what makes their timings comparable: whatever
    the loads cost, they cost both of them the same.
    """
    names: set[str] = set()
    for writing in writings:
        names.update(variables_of(tree_of(writing.source)))
    return {name: index for index, name in enumerate(sorted(names))}


def base_values(slots: dict[str, int]) -> dict[str, Fraction]:
    """The declared base input of every variable: ``BASE_START + slot * BASE_STEP``.

    Distinct per variable, all at least ``1``.  Distinctness is what keeps ``x2 - x1`` from being
    zero, and the lower bound is what keeps every denominator in the corpus away from zero.
    """
    return {name: BASE_START + slot * BASE_STEP for name, slot in slots.items()}


def input_row(slots: dict[str, int], row: int) -> dict[str, Fraction]:
    """The exact rational inputs the C table holds in table row ``row``.

    The fill rule is ``BASE[v] * (256 + j) / 256``.  Both factors are dyadic and small, so the
    product is an exact double and this rational is exactly the number the C program computes with.
    """
    if not 0 <= row < TABLE_SIZE:
        raise ValueError(f"row {row} outside the table of {TABLE_SIZE} rows")
    scale = Fraction(256 + row, 256)
    return {name: value * scale for name, value in base_values(slots).items()}


# ---------------------------------------------------------------------------------- the emitter


def _literal(value: Fraction) -> str:
    """A tree constant as a C double literal that round-trips exactly."""
    text = repr(float(value))
    if "." not in text and "e" not in text and "E" not in text and "inf" not in text:
        text += ".0"
    return text


def emit_statements(tree: Node, temporary: str = "t") -> tuple[tuple[str, ...], str]:
    """The dataflow graph as a sequence of single-operation C statements.

    Returns the statement lines and the name holding the result.

    **Named temporaries, one operation per statement, and not a single nested expression.**  Three
    reasons, and the third is the one that decides it:

    1. the correspondence to the model is auditable -- one statement per internal tree node, so a
       reader can count the model's ``operations`` by counting lines rather than by trusting a
       parenthesisation;
    2. the emitted order is the tree's own post-order, so the C source is a transcript of the
       dataflow graph and not a re-parse of a string that a C compiler's own precedence would have
       to rebuild;
    3. clang's default in C is ``-ffp-contract=on``, which fuses a multiply and an add only when
       they are in the SAME statement.  One operation per statement therefore leaves fusion off by
       default, and ``-ffp-contract=fast`` is the single flag that turns it on.  That makes fusion a
       declared axis of this experiment instead of a property of how the expression was written out.

    Temporaries are numbered in post-order, so the emission is a deterministic function of the tree.
    """
    lines: list[str] = []
    counter = 0

    def walk(node: Node) -> str:
        nonlocal counter
        if isinstance(node, Number):
            return _literal(node.value)
        if isinstance(node, Variable):
            return PARAMETER_PREFIX + node.name
        left = walk(node.left)
        right = walk(node.right)
        name = f"{temporary}{counter}"
        counter += 1
        lines.append(f"double {name} = {left} {node.operator} {right};")
        return name

    result = walk(tree)
    return tuple(lines), result


def emit_c(tree: Node, name: str) -> str:
    """The dataflow graph as a C function.

    Straight-line, ``double`` throughout, one operation per named temporary, parameters in sorted
    variable order.  Deterministic from the tree: the same tree gives byte-identical source, which
    a test pins.

    A tree with no operations emits a function that returns its single leaf; that is a degenerate
    but legal dataflow graph and refusing it here would be a silent corpus restriction.
    """
    if not name.isidentifier():
        raise ValueError(f"{name!r} is not a legal C function name")
    names = variables_of(tree)
    parameters = ", ".join(f"double {PARAMETER_PREFIX}{item}" for item in names) or "void"
    lines, result = emit_statements(tree)
    body = "".join(f"    {line}\n" for line in lines)
    return f"static double {name}({parameters}) {{\n{body}    return {result};\n}}\n"


def _kernel_name(writing: Writing, suffix: str = "") -> str:
    text = re.sub(r"[^0-9A-Za-z_]", "_", f"k_{writing.subject}__{writing.role}{suffix}")
    return text


def _table_header(slots: dict[str, int]) -> str:
    bases = base_values(slots)
    order = sorted(slots, key=lambda name: slots[name])
    literals = ", ".join(_literal(bases[name]) for name in order)
    return (
        "#include <stdio.h>\n"
        "#include <stdlib.h>\n"
        "#include <windows.h>\n"
        "\n"
        f"#define PA_TABLE {TABLE_SIZE}\n"
        f"#define PA_MASK {TABLE_SIZE - 1}\n"
        f"#define PA_SLOTS {max(len(slots), 1)}\n"
        "\n"
        "static double PA_IN[PA_SLOTS][PA_TABLE];\n"
        f"static const double PA_BASE[PA_SLOTS] = {{ {literals or '0.0'} }};\n"
        "static volatile double PA_SINK;\n"
        "\n"
        "static void fill_inputs(void) {\n"
        "    for (int v = 0; v < PA_SLOTS; v++)\n"
        "        for (int j = 0; j < PA_TABLE; j++)\n"
        "            PA_IN[v][j] = PA_BASE[v] * ((256.0 + (double)j) * (1.0 / 256.0));\n"
        "}\n"
    )


def deepest_variable(tree: Node) -> tuple[str | None, int, int]:
    """The variable leaf furthest from the root: its name, its depth, and the tree's depth.

    Ties are broken by name, so the choice is a deterministic function of the tree.  The third
    number is 0041's ``depth`` of the whole tree; when the first two disagree with it the fed leaf
    does not sit on a longest path and the latency regime is measuring a shorter chain than the
    model's ``depth``.  That never happens on this card's corpus, and :func:`latency_path_audit`
    checks it rather than assuming it.
    """
    best: tuple[int, str] | None = None

    def walk(node: Node, level: int) -> None:
        nonlocal best
        if isinstance(node, Variable):
            candidate = (level, node.name)
            if best is None or candidate[0] > best[0] or (candidate[0] == best[0] and candidate[1] < best[1]):
                best = candidate
        elif isinstance(node, Binary):
            walk(node.left, level + 1)
            walk(node.right, level + 1)

    walk(tree, 0)
    if best is None:
        return None, 0, depth(tree)
    return best[1], best[0], depth(tree)


def _kernel_body(tree: Node, slots: dict[str, int], index_expression: str, feedback: bool) -> list[str]:
    """The load statements and the graph statements of one loop step."""
    lines = [f"long j = {index_expression};"]
    fed = deepest_variable(tree)[0] if feedback else None
    if feedback:
        if fed is None:
            raise ValueError("the latency regime needs a tree with at least one variable to feed")
        lines.append(f"double fb = acc * {FEEDBACK_SCALE!r};")
    for name in variables_of(tree):
        load = f"PA_IN[{slots[name]}][j]"
        if name == fed:
            lines.append(f"double {PARAMETER_PREFIX}{name} = {load} + fb;")
        else:
            lines.append(f"double {PARAMETER_PREFIX}{name} = {load};")
    statements, result = emit_statements(tree)
    lines.extend(statements)
    lines.append(f"__RESULT__ = {result};")
    return lines


def _emit_kernel(name: str, tree: Node, slots: dict[str, int], mode: str, guard: bool) -> str:
    """One timed kernel: the loop, the guard, and nothing else."""
    if mode == "throughput":
        head = "    double a0 = 0.0, a1 = 0.0, a2 = 0.0, a3 = 0.0;\n    for (long i = 0; i < iters; i += 4) {\n"
        blocks = []
        for step in range(4):
            body = _kernel_body(tree, slots, f"(i + {step}) & PA_MASK", feedback=False)
            body = [line.replace("__RESULT__ =", f"a{step} +=") for line in body]
            blocks.append("        {\n" + "".join(f"            {line}\n" for line in body) + "        }\n")
        tail = "    }\n"
        if guard:
            tail += "    *out = a0 + a1 + a2 + a3;\n    return *out;\n"
        else:
            tail += "    (void)a0; (void)a1; (void)a2; (void)a3;\n    *out = 0.0;\n    return 0.0;\n"
        return f"static double {name}(long iters, double *out) {{\n{head}{''.join(blocks)}{tail}}}\n"
    if mode == "latency":
        body = _kernel_body(tree, slots, "i & PA_MASK", feedback=True)
        body = [line.replace("__RESULT__ =", "acc =") for line in body]
        inner = "".join(f"        {line}\n" for line in body)
        head = "    double acc = 0.0;\n    for (long i = 0; i < iters; i++) {\n"
        tail = "    }\n"
        if guard:
            tail += "    *out = acc;\n    return acc;\n"
        else:
            tail += "    (void)acc;\n    *out = 0.0;\n    return 0.0;\n"
        return f"static double {name}(long iters, double *out) {{\n{head}{inner}{tail}}}\n"
    raise ValueError(f"unknown mode: {mode!r}")


def _emit_main(names: Sequence[str]) -> str:
    table = ",\n".join(f"    {name}" for name in names)
    labels = ",\n".join(f'    "{name}"' for name in names)
    return (
        "typedef double (*kernel_fn)(long, double *);\n"
        f"static kernel_fn KERNELS[] = {{\n{table}\n}};\n"
        f"static const char *NAMES[] = {{\n{labels}\n}};\n"
        "#define NK ((int)(sizeof(KERNELS) / sizeof(KERNELS[0])))\n"
        "\n"
        "int main(int argc, char **argv) {\n"
        "    long iters = (argc > 1) ? atol(argv[1]) : 4096;\n"
        "    int trials = (argc > 2) ? atoi(argv[2]) : 9;\n"
        "    int warmup = (argc > 3) ? atoi(argv[3]) : 2;\n"
        "    LARGE_INTEGER freq, before, after;\n"
        "    double check = 0.0, one = 0.0;\n"
        f"    int pinned = SetProcessAffinityMask(GetCurrentProcess(), (DWORD_PTR)1 << {PIN_CORE}) != 0;\n"
        "    int raised = SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS) != 0;\n"
        "    raised = SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST) && raised;\n"
        "    printf(\"PIN %d %d\\n\", pinned, raised);\n"
        "    QueryPerformanceFrequency(&freq);\n"
        "    fill_inputs();\n"
        "    for (int w = 0; w < warmup; w++)\n"
        "        for (int k = 0; k < NK; k++) { KERNELS[k](iters, &one); check += one; }\n"
        "    printf(\"FREQ %lld\\n\", (long long)freq.QuadPart);\n"
        "    for (int r = 0; r < trials; r++) {\n"
        "        for (int k = 0; k < NK; k++) {\n"
        "            one = 0.0;\n"
        "            QueryPerformanceCounter(&before);\n"
        "            KERNELS[k](iters, &one);\n"
        "            QueryPerformanceCounter(&after);\n"
        "            printf(\"R %s %d %lld %a\\n\", NAMES[k], r,\n"
        "                   (long long)(after.QuadPart - before.QuadPart), one);\n"
        "            check += one;\n"
        "        }\n"
        "    }\n"
        "    PA_SINK = check;\n"
        "    printf(\"SINK %a\\n\", (double)PA_SINK);\n"
        "    return 0;\n"
        "}\n"
    )


def emit_program(writings: Sequence[Writing], mode: str, guard: bool = True, duplicate: bool = False) -> tuple[str, tuple[str, ...]]:
    """The whole benchmark program: input table, one kernel per writing, and the driver.

    When ``duplicate`` is set, the FIRST writing of every subject is emitted a second time under a
    ``__dup`` name.  The two copies are byte-identical C, so any difference between their timings is
    noise and nothing else -- that is how :func:`noise_floor` gets its number, measured in exactly
    the conditions of the comparisons it governs rather than in a separate calm run.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode!r}")
    if not writings:
        raise ValueError("a benchmark program needs at least one writing")
    slots = slot_map(writings)
    ordered: list[tuple[str, Writing]] = []
    seen_subjects: set[str] = set()
    for writing in writings:
        ordered.append((_kernel_name(writing), writing))
        if duplicate and writing.subject not in seen_subjects:
            seen_subjects.add(writing.subject)
            ordered.append((_kernel_name(writing, "__dup"), writing))
    parts = [_table_header(slots)]
    for name, writing in ordered:
        parts.append("\n" + _emit_kernel(name, tree_of(writing.source), slots, mode, guard))
    parts.append("\n" + _emit_main([name for name, _ in ordered]))
    return "".join(parts), tuple(name for name, _ in ordered)


def emit_check_program(writings: Sequence[Writing], rows: int) -> str:
    """A program that prints every writing's value on the first ``rows`` table rows.

    Separate from the benchmark program on purpose: the benchmark's kernels are loops with
    accumulators, and a value printed out of one of those would be a sum of many evaluations rather
    than the function's value.  Here each writing is compiled as the plain function
    :func:`emit_c` produces and called once per row.
    """
    if not 0 < rows <= TABLE_SIZE:
        raise ValueError(f"rows must be between 1 and {TABLE_SIZE}")
    slots = slot_map(writings)
    parts = [_table_header(slots)]
    calls = []
    for writing in writings:
        tree = tree_of(writing.source)
        name = _kernel_name(writing)
        parts.append("\n" + emit_c(tree, name))
        arguments = ", ".join(f"PA_IN[{slots[item]}][j]" for item in variables_of(tree))
        calls.append(f'        printf("V %s %d %a\\n", "{name}", j, {name}({arguments}));')
    body = "\n".join(calls)
    parts.append(
        "\nint main(void) {\n"
        "    fill_inputs();\n"
        f"    for (int j = 0; j < {rows}; j++) {{\n"
        f"{body}\n"
        "    }\n"
        "    return 0;\n"
        "}\n"
    )
    return "".join(parts)


# ------------------------------------------------------------------------- compiling and running


@lru_cache(maxsize=1)
def clang_available() -> bool:
    """Whether a working ``clang`` is on PATH.  Every compiled test skips on ``False``."""
    if shutil.which("clang") is None:
        return False
    try:
        subprocess.run(["clang", "--version"], capture_output=True, check=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return True


@lru_cache(maxsize=1)
def clang_version() -> str:
    """The first line of ``clang --version``, recorded with every number this module reports."""
    if not clang_available():
        return "clang not available"
    result = subprocess.run(["clang", "--version"], capture_output=True, text=True, check=True)
    return result.stdout.splitlines()[0].strip()


@lru_cache(maxsize=1)
def clang_target() -> str:
    """The clang target triple, recorded because it decides the ABI the timings were taken under."""
    if not clang_available():
        return "clang not available"
    result = subprocess.run(["clang", "--version"], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        if line.strip().startswith("Target:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def environment() -> dict[str, Any]:
    """The machine, the compiler and the interpreter every number in this module belongs to."""
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cores": os.cpu_count(),
        "python": sys.version.split()[0],
        "clang": clang_version(),
        "clang_target": clang_target(),
    }


class CompilationError(RuntimeError):
    """clang refused the emitted program.  The command and its output are on the exception."""


def compile_program(source: str, flags: Sequence[str], workdir: Path, stem: str) -> Path:
    """Write ``source`` to ``workdir`` and compile it with ``flags``; return the executable path.

    Nothing is written outside ``workdir``, and ``workdir`` is a temporary directory the caller
    created and removes: no generated C and no binary ever reaches the working tree.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    csource = workdir / f"{stem}.c"
    binary = workdir / f"{stem}.exe"
    csource.write_text(source, encoding="ascii")
    command = ["clang", *flags, str(csource), "-o", str(binary)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise CompilationError(f"{' '.join(command)}\n{result.stdout}\n{result.stderr}")
    return binary


def _run(binary: Path, arguments: Sequence[str]) -> str:
    result = subprocess.run([str(binary), *arguments], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{binary} exited {result.returncode}: {result.stderr}")
    return result.stdout


def _statistics(seconds: Sequence[float]) -> dict[str, float]:
    ordered = sorted(seconds)
    return {
        "trials": len(ordered),
        "median": statistics.median(ordered),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "p10": ordered[max(0, round(0.10 * (len(ordered) - 1)))],
        "p90": ordered[min(len(ordered) - 1, round(0.90 * (len(ordered) - 1)))],
    }


def benchmark(
    writings: Sequence[Writing],
    optimisation: str | Level,
    mode: str = "throughput",
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
    warmup: int = 2,
    guard: bool = True,
    duplicate: bool = False,
    workdir: Path | None = None,
) -> dict[str, Any]:
    """Compile ``writings`` at one optimisation level and time every one of them.

    The discipline Phase 11 requires, and every part of it is a parameter rather than a constant so
    that :func:`repetition_curve` can sweep it:

    * ``warmup`` full passes over every kernel before anything is timed;
    * ``trials`` timed blocks per kernel, each of ``iterations`` loop steps;
    * the blocks are taken **round robin** -- every kernel is timed once, then every kernel again --
      so a kernel's trials are spread across the whole run and a drift in clock or temperature is
      shared out rather than landing on whichever kernel happened to run last;
    * the report is a median with a p10/p90 band and a minimum.  **Never a single timing.**

    ``iterations`` is rounded UP to a multiple of four in throughput mode, because that mode's loop
    advances four independent steps at a time.
    """
    level = optimisation if isinstance(optimisation, Level) else LEVEL_BY_NAME[str(optimisation)]
    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode!r}")
    if iterations < 1 or trials < 1:
        raise ValueError("iterations and trials must both be positive")
    steps = iterations + (-iterations % 4) if mode == "throughput" else iterations
    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_")) if owned else Path(workdir)
    try:
        source, kernel_names = emit_program(writings, mode, guard=guard, duplicate=duplicate)
        stem = f"bench_{mode}_{level.name}_{'guarded' if guard else 'dead'}"
        binary = compile_program(source, level.flags, directory, stem)
        started = time.perf_counter()
        output = _run(binary, [str(steps), str(trials), str(warmup)])
        elapsed = time.perf_counter() - started
    finally:
        if owned:
            shutil.rmtree(directory, ignore_errors=True)

    frequency = None
    samples: dict[str, list[float]] = {name: [] for name in kernel_names}
    checksums: dict[str, set[float]] = {name: set() for name in kernel_names}
    sink = None
    pinned = raised = None
    for line in output.splitlines():
        parts = line.split()
        if parts[:1] == ["PIN"]:
            pinned, raised = bool(int(parts[1])), bool(int(parts[2]))
        elif parts[:1] == ["FREQ"]:
            frequency = int(parts[1])
        elif parts[:1] == ["SINK"]:
            sink = float.fromhex(parts[1])
        elif parts[:1] == ["R"]:
            name, _trial, ticks, value = parts[1], int(parts[2]), int(parts[3]), float.fromhex(parts[4])
            samples[name].append(ticks / frequency / steps)
            checksums[name].add(value)
    if frequency is None:
        raise RuntimeError("the benchmark program printed no timer frequency")
    missing = [name for name, values in samples.items() if len(values) != trials]
    if missing:
        raise RuntimeError(f"kernels with the wrong number of trials: {missing}")

    results = {
        name: {
            **_statistics(values),
            "median_ticks": statistics.median(values) * steps * frequency,
            "checksums": sorted(checksums[name]),
            "checksum_stable": len(checksums[name]) == 1,
        }
        for name, values in samples.items()
    }
    # The alarm for the failure this whole harness exists to avoid.  A kernel whose timed block is
    # shorter than a handful of timer ticks did not run fast; its loop was deleted.  It is reported
    # rather than silently ranked, and every caller that draws an order refuses to proceed on it.
    eliminated = [name for name, entry in results.items() if entry["median_ticks"] < MIN_BLOCK_TICKS]
    return {
        "level": level.name,
        "flags": list(level.flags),
        "mode": mode,
        "iterations": steps,
        "trials": trials,
        "warmup": warmup,
        "guard": guard,
        "timer_frequency_hz": frequency,
        "timer_tick_seconds": 1.0 / frequency,
        "pinned_core": PIN_CORE,
        "affinity_set": pinned,
        "priority_raised": raised,
        "wall_seconds": elapsed,
        "kernels": tuple(kernel_names),
        "results": results,
        "eliminated": eliminated,
        "sink": sink,
        "writings": {_kernel_name(item): item for item in writings},
    }


# --------------------------------------------------------------------------------- correctness


def correctness_audit(
    writings: Sequence[Writing] = (),
    levels: Sequence[Level] = LEVELS,
    rows: int = 8,
    workdir: Path | None = None,
) -> dict[str, Any]:
    """Every emitted function against the exact-rational oracle, at every optimisation level.

    **This runs before any timing is believed.**  A faster function that computes something else is
    the failure mode this repository exists to prevent, so the comparison is exact on the oracle's
    side: :func:`evaluate` uses ``Fraction`` throughout and the C result is converted to the exact
    rational it equals, so the reported deviation is entirely the machine's rounding.

    Reports the observed maximum relative deviation per level.  ``TOLERANCE`` is the declared bound;
    the observed maximum is what tells a reader how much margin there was.
    """
    writings = tuple(writings) or tuple(item for subject in CORPUS for item in subject.writings)
    slots = slot_map(writings)
    expected: dict[tuple[str, int], Fraction] = {}
    for row in range(rows):
        inputs = input_row(slots, row)
        for writing in writings:
            expected[(_kernel_name(writing), row)] = evaluate(tree_of(writing.source), inputs)

    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_")) if owned else Path(workdir)
    per_level = []
    try:
        source = emit_check_program(writings, rows)
        for level in levels:
            binary = compile_program(source, level.flags, directory, f"check_{level.name}")
            output = _run(binary, [])
            worst = Fraction(0)
            worst_at = None
            checked = 0
            failures = []
            for line in output.splitlines():
                parts = line.split()
                if parts[:1] != ["V"]:
                    continue
                name, row, value = parts[1], int(parts[2]), float.fromhex(parts[3])
                truth = expected[(name, row)]
                deviation = abs(Fraction(value) - truth) / (abs(truth) if truth != 0 else 1)
                checked += 1
                if deviation > worst:
                    worst, worst_at = deviation, (name, row)
                if deviation > TOLERANCE:
                    failures.append({"kernel": name, "row": row, "deviation": float(deviation)})
            per_level.append(
                {
                    "level": level.name,
                    "checked": checked,
                    "failures": failures,
                    "max_relative_deviation": float(worst),
                    "max_at": worst_at,
                }
            )
    finally:
        if owned:
            shutil.rmtree(directory, ignore_errors=True)
    return {
        "writing_count": len(writings),
        "rows": rows,
        "tolerance": float(TOLERANCE),
        "levels": per_level,
        "all_match": all(not entry["failures"] for entry in per_level),
        "max_relative_deviation": max(entry["max_relative_deviation"] for entry in per_level),
    }


# ------------------------------------------------------------------------------ the anti-guard


def guard_audit(
    writings: Sequence[Writing] = (),
    level: str = "O2",
    mode: str = "throughput",
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
) -> dict[str, Any]:
    """The anti-elimination guard, measured rather than asserted.

    The same kernels are compiled twice at the same level: once with the accumulator stored, summed
    into a checksum and printed, and once with the accumulator computed and then dropped.  In the
    second the whole loop body is dead and the compiler is entitled to delete it.  The ratio of the
    two medians is the evidence that the guard is doing something.
    """
    writings = tuple(writings) or tuple(item for subject in CORPUS for item in subject.writings)
    guarded = benchmark(writings, level, mode=mode, iterations=iterations, trials=trials, guard=True)
    dead = benchmark(writings, level, mode=mode, iterations=iterations, trials=trials, guard=False)
    rows = []
    for name in guarded["kernels"]:
        alive = guarded["results"][name]["median"]
        gone = dead["results"][name]["median"]
        rows.append(
            {
                "kernel": name,
                "guarded_seconds_per_step": alive,
                "dead_seconds_per_step": gone,
                "ratio": gone / alive if alive > 0 else float("inf"),
            }
        )
    ratios = [row["ratio"] for row in rows]
    return {
        "level": level,
        "mode": mode,
        "iterations": guarded["iterations"],
        "trials": trials,
        "kernel_count": len(rows),
        "rows": rows,
        "max_ratio": max(ratios),
        "median_ratio": statistics.median(ratios),
        "guard_works": max(ratios) < 0.2,
    }


# ------------------------------------------------------------------------------- the noise floor


def _relative_gap(first: float, second: float) -> float:
    low = min(first, second)
    return abs(first - second) / low if low > 0 else float("inf")


def _refuse_eliminated(runs: Sequence[dict[str, Any]]) -> None:
    """Refuse to draw an order from a run in which a kernel's loop was optimised away."""
    broken = [
        (run["level"], run["mode"], name)
        for run in runs
        for name in run["eliminated"]
    ]
    if broken:
        raise RuntimeError(
            "timed blocks shorter than "
            f"{MIN_BLOCK_TICKS} timer ticks -- the loop was eliminated, not executed: {broken}"
        )


def latency_path_audit(writings: Sequence[Writing] = ()) -> dict[str, Any]:
    """Whether the leaf the latency regime feeds really sits at the tree's full depth.

    The regime folds the previous loop step's result into one variable leaf, so what it times is the
    chain from THAT leaf to the root.  When the chosen leaf is at the tree's full depth that chain is
    the model's ``depth``; when it is not, the regime measures something shorter and no comparison
    against ``depth`` is legitimate.  This audit says which, for every writing, and it is a test
    rather than an assumption.
    """
    writings = tuple(writings) or (
        tuple(item for subject in CORPUS for item in subject.writings)
        + tuple(item for subject in probe_subjects() for item in subject.writings)
    )
    rows = []
    for writing in writings:
        name, leaf_depth, tree_depth = deepest_variable(tree_of(writing.source))
        rows.append(
            {
                "kernel": _kernel_name(writing),
                "fed_variable": name,
                "fed_leaf_depth": leaf_depth,
                "tree_depth": tree_depth,
                "full_depth": leaf_depth == tree_depth,
            }
        )
    return {
        "rows": rows,
        "writing_count": len(rows),
        "at_full_depth": sum(1 for row in rows if row["full_depth"]),
        "all_full_depth": all(row["full_depth"] for row in rows),
    }


def noise_floor(runs: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The measured noise floor: the spread between kernels that are byte-identical C.

    Every benchmark run made with ``duplicate=True`` carries, for each subject, a second copy of one
    of its writings under a ``__dup`` name.  The two copies compile to the same code, so the
    relative difference between their medians is noise by construction.

    **The reported ``floor`` is the 95th percentile of that distribution and not its maximum, and
    the reason is measured.**  The distribution is strongly skewed: on this machine the median gap
    between two identical kernels is a few tenths of a percent and the 90th percentile is about one
    percent, but a single run taken while three other jobs were compiling on the same box produced
    one gap of ``19.04%``.  Re-running that same level and regime three times with the machine quiet
    gave maxima of ``1.17%``, ``2.39%`` and ``1.75%``, so the outlier was interference and not a
    property of the kernels.  Taking the maximum would let one preempted block set the resolution of
    the entire experiment.

    The maximum is reported anyway, in ``maximum``, and no result in this card rests on the choice:
    :func:`agreement_table` publishes a sweep of the floor from far below the median gap to far above
    the largest, so a reader can see the whole curve rather than one point on it.
    """
    gaps = []
    for run in runs:
        for name in run["kernels"]:
            if not name.endswith("__dup"):
                continue
            original = name[: -len("__dup")]
            if original not in run["results"]:
                continue
            gap = _relative_gap(run["results"][original]["median"], run["results"][name]["median"])
            gaps.append(
                {
                    "level": run["level"],
                    "mode": run["mode"],
                    "kernel": original,
                    "relative_gap": gap,
                }
            )
    _refuse_eliminated(runs)
    if not gaps:
        raise ValueError("noise_floor needs runs made with duplicate=True")
    values = sorted(item["relative_gap"] for item in gaps)

    def quantile(fraction: float) -> float:
        return values[min(len(values) - 1, round(fraction * (len(values) - 1)))]

    return {
        "pair_count": len(values),
        "floor": quantile(0.95),
        "median": statistics.median(values),
        "p90": quantile(0.90),
        "p95": quantile(0.95),
        "maximum": values[-1],
        "pairs": gaps,
    }


# ------------------------------------------------------------------------- the repetition sweep


def repetition_curve(
    writings: Sequence[Writing] = (),
    level: str = "O2",
    mode: str = "throughput",
    iterations: Sequence[int] = REPETITION_SWEEP,
    trials: int = DEFAULT_TRIALS,
) -> dict[str, Any]:
    """Sweep the repetition count and report the curve, rather than declaring a count and trusting it.

    For each ``iterations`` value the whole kernel set is timed and two numbers are read off: the
    median seconds per loop step, which should flatten once the fixed cost of a timed block is
    amortised, and the relative p10-p90 band, which should narrow as the block grows past the timer's
    tick.  Where both stop moving is where the count is large enough; the curve is published so a
    reader can see whether the answer was still moving when the sweep stopped.
    """
    writings = tuple(writings) or tuple(item for subject in CORPUS for item in subject.writings)
    points = []
    for count in iterations:
        run = benchmark(writings, level, mode=mode, iterations=count, trials=trials)
        medians = [run["results"][name]["median"] for name in run["kernels"]]
        bands = [
            (run["results"][name]["p90"] - run["results"][name]["p10"]) / run["results"][name]["median"]
            for name in run["kernels"]
        ]
        points.append(
            {
                "iterations": run["iterations"],
                "median_seconds_per_step": statistics.median(medians),
                "median_relative_band": statistics.median(bands),
                "max_relative_band": max(bands),
                "block_seconds": statistics.median(medians) * run["iterations"],
                "ticks_per_block": statistics.median(medians) * run["iterations"] * run["timer_frequency_hz"],
            }
        )
    drifts = [
        abs(points[index]["median_seconds_per_step"] - points[index - 1]["median_seconds_per_step"])
        / points[index - 1]["median_seconds_per_step"]
        for index in range(1, len(points))
    ]
    return {
        "level": level,
        "mode": mode,
        "trials": trials,
        "points": points,
        "consecutive_drift": drifts,
        "final_drift": drifts[-1] if drifts else None,
    }


# ---------------------------------------------------------------------------- the agreement table


def _order(values: dict[str, float], floor: float) -> tuple[tuple[str, ...], ...]:
    """Group keys into tiers, two keys sharing a tier when their gap is within ``floor``."""
    ordered = sorted(values, key=lambda name: values[name])
    tiers: list[list[str]] = []
    for name in ordered:
        if tiers and _relative_gap(values[tiers[-1][-1]], values[name]) <= floor:
            tiers[-1].append(name)
        else:
            tiers.append([name])
    return tuple(tuple(tier) for tier in tiers)


def _model_order(values: dict[str, int]) -> tuple[tuple[str, ...], ...]:
    tiers: dict[int, list[str]] = {}
    for name, value in values.items():
        tiers.setdefault(value, []).append(name)
    return tuple(tuple(sorted(tiers[key])) for key in sorted(tiers))


def _explain(first: dict[str, int], second: dict[str, int]) -> tuple[str, ...]:
    """Which of the four declared divergences is consistent with ``second`` beating ``first``.

    All consistent explanations are returned, never one.  Two writings usually differ on more than
    one of the four, and picking a single cause would be a story rather than an observation.
    """
    reasons = []
    if second["div"] < first["div"]:
        reasons.append("division")
    if second["fma_sites"] > first["fma_sites"]:
        reasons.append("fma")
    if second["depth"] < first["depth"]:
        reasons.append("latency")
    if second["peak_live"] < first["peak_live"]:
        reasons.append("registers")
    return tuple(reasons)


#: The model axis each regime is supposed to predict, declared here rather than chosen per table.
MODE_AXIS: dict[str, str] = {"throughput": "operations", "latency": "depth"}

#: Every model axis the agreement table crosses against every regime.
MODEL_AXES: tuple[str, ...] = ("operations", "depth", "peak_live")

#: The floors :func:`agreement_table` re-reads its own answer at, from far below the median gap
#: between two identical kernels to far above the largest ever observed between two.  Published as a
#: curve so that no single choice of floor decides a count.
FLOOR_SWEEP: tuple[float, ...] = (0.0, 0.0025, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10, 0.20)

#: The noise floor this card's FIRST revision measured and read every survival count at.
#:
#: It is kept as a named constant for one reason: :func:`survival_repeatability` re-measures those
#: counts, and a re-measurement taken at a different resolution is a different question rather than
#: a check on the old answer.  Re-reading at the published floor is what makes the new count and the
#: old count comparable.  It is **not** a declared property of this machine -- the measured floor
#: moves from run to run and every function here reports the floor it actually used.
PUBLISHED_FLOOR: float = 0.02062


def _classify(
    names: Sequence[str],
    timings: dict[str, float],
    profiles: dict[str, dict[str, int]],
    axis: str,
    floor: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Split a subject's writing pairs into inversions, unresolved pairs and concordant pairs.

    Only pairs the model orders STRICTLY are classified; a pair the model calls equal is not a
    prediction and cannot be contradicted.  A pair whose measured gap does not exceed ``floor`` is
    unresolved rather than concordant, because calling it agreement would let the noise floor
    manufacture the result.
    """
    inversions: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    concordant: list[dict[str, Any]] = []
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            gap = profiles[first][axis] - profiles[second][axis]
            if gap == 0:
                continue
            better, worse = (second, first) if gap > 0 else (first, second)
            spread = _relative_gap(timings[better], timings[worse])
            pair = {
                "model_better": better,
                "model_worse": worse,
                "seconds_better": timings[better],
                "seconds_worse": timings[worse],
                "relative_gap": spread,
            }
            if spread <= floor:
                unresolved.append(pair)
            elif timings[worse] < timings[better]:
                pair["explanations"] = list(_explain(profiles[better], profiles[worse]))
                inversions.append(pair)
            else:
                concordant.append(pair)
    return inversions, unresolved, concordant


def agreement_table(
    corpus: Sequence[Subject] = CORPUS,
    levels: Sequence[Level] = LEVELS,
    modes: Sequence[str] = MODES,
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
    floor: float | None = None,
) -> dict[str, Any]:
    """The structural ranking of each object's writings against the measured ranking.

    One program per ``(level, mode)``, containing every writing in the corpus plus one duplicate per
    subject; the duplicates give the noise floor in the same run as the comparisons it governs.

    **The finding is the disagreements.**  An *inversion* is a pair of writings the model orders
    strictly one way and the machine orders strictly the other way by more than the noise floor.  A
    pair the model orders strictly and the machine cannot separate is *unresolved*, not agreement:
    calling it agreement would let the noise floor manufacture a result.
    """
    corpus = tuple(corpus)
    writings = tuple(item for subject in corpus for item in subject.writings)
    profiles = {_kernel_name(item): structural_profile(tree_of(item.source)) for item in writings}

    runs = []
    for level in levels:
        for mode in modes:
            runs.append(
                benchmark(
                    writings,
                    level,
                    mode=mode,
                    iterations=iterations,
                    trials=trials,
                    duplicate=True,
                )
            )
    _refuse_eliminated(runs)
    measured_floor = noise_floor(runs)
    working_floor = measured_floor["floor"] if floor is None else floor

    cells = []
    for run in runs:
        for subject in corpus:
            names = [_kernel_name(item) for item in subject.writings]
            timings = {name: run["results"][name]["median"] for name in names}
            machine = _order(timings, working_floor)
            for axis in MODEL_AXES:
                model = _model_order({name: profiles[name][axis] for name in names})
                inversions, unresolved, concordant = _classify(
                    names, timings, profiles, axis, working_floor
                )
                cells.append(
                    {
                        "level": run["level"],
                        "mode": run["mode"],
                        "axis": axis,
                        "subject": subject.name,
                        "timings": dict(timings),
                        "model_order": [list(tier) for tier in model],
                        "machine_order": [list(tier) for tier in machine],
                        "inversions": inversions,
                        "unresolved": unresolved,
                        "concordant": concordant,
                        "inversion_count": len(inversions),
                    }
                )

    def _count(predicate) -> int:
        return sum(cell["inversion_count"] for cell in cells if predicate(cell))

    headline = [
        {
            "level": level.name,
            "mode": mode,
            "axis": MODE_AXIS[mode],
            "inversions": _count(
                lambda cell, level=level, mode=mode: cell["level"] == level.name
                and cell["mode"] == mode
                and cell["axis"] == MODE_AXIS[mode]
            ),
            "subjects_with_inversion": len(
                {
                    cell["subject"]
                    for cell in cells
                    if cell["level"] == level.name
                    and cell["mode"] == mode
                    and cell["axis"] == MODE_AXIS[mode]
                    and cell["inversion_count"]
                }
            ),
            "unresolved": sum(
                len(cell["unresolved"])
                for cell in cells
                if cell["level"] == level.name and cell["mode"] == mode and cell["axis"] == MODE_AXIS[mode]
            ),
            "concordant": sum(
                len(cell["concordant"])
                for cell in cells
                if cell["level"] == level.name and cell["mode"] == mode and cell["axis"] == MODE_AXIS[mode]
            ),
        }
        for level in levels
        for mode in modes
    ]

    explanations: dict[str, int] = {}
    for cell in cells:
        for pair in cell["inversions"]:
            for reason in pair.get("explanations", ()) or ("unexplained",):
                explanations[reason] = explanations.get(reason, 0) + 1

    matrix = [
        {
            "level": level.name,
            "mode": mode,
            "axis": axis,
            "inversions": _count(
                lambda cell, level=level, mode=mode, axis=axis: cell["level"] == level.name
                and cell["mode"] == mode
                and cell["axis"] == axis
            ),
            "unresolved": sum(
                len(cell["unresolved"])
                for cell in cells
                if cell["level"] == level.name and cell["mode"] == mode and cell["axis"] == axis
            ),
            "concordant": sum(
                len(cell["concordant"])
                for cell in cells
                if cell["level"] == level.name and cell["mode"] == mode and cell["axis"] == axis
            ),
        }
        for level in levels
        for mode in modes
        for axis in MODEL_AXES
    ]

    sensitivity = []
    for candidate in sorted({*FLOOR_SWEEP, working_floor}):
        headline_inversions = 0
        headline_unresolved = 0
        headline_concordant = 0
        collapsed = 0
        subjects = 0
        for run in runs:
            for subject in corpus:
                names = [_kernel_name(item) for item in subject.writings]
                timings = {name: run["results"][name]["median"] for name in names}
                inversions, unresolved, concordant = _classify(
                    names, timings, profiles, MODE_AXIS[run["mode"]], candidate
                )
                headline_inversions += len(inversions)
                headline_unresolved += len(unresolved)
                headline_concordant += len(concordant)
                subjects += 1
                if _relative_gap(min(timings.values()), max(timings.values())) <= candidate:
                    collapsed += 1
        sensitivity.append(
            {
                "floor": candidate,
                "is_working_floor": candidate == working_floor,
                "inversions": headline_inversions,
                "unresolved": headline_unresolved,
                "concordant": headline_concordant,
                "collapsed_subject_cells": collapsed,
                "subject_cells": subjects,
            }
        )

    return {
        "matrix": matrix,
        "floor_sensitivity": sensitivity,
        "environment": environment(),
        "subject_count": len(corpus),
        "writing_count": len(writings),
        "iterations": iterations,
        "trials": trials,
        "noise_floor": measured_floor,
        "working_floor": working_floor,
        "profiles": profiles,
        "cells": cells,
        "headline": headline,
        "total_inversions": sum(cell["inversion_count"] for cell in cells),
        "headline_inversions": sum(entry["inversions"] for entry in headline),
        "explanation_counts": dict(sorted(explanations.items())),
        "runs": [
            {
                "level": run["level"],
                "mode": run["mode"],
                "wall_seconds": run["wall_seconds"],
                "iterations": run["iterations"],
            }
            for run in runs
        ],
        "_runs": runs,
    }


def survival_table(agreement: dict[str, Any]) -> dict[str, Any]:
    """How much of a representation choice survives the compiler, per level and per regime.

    For each subject the spread between its fastest and its slowest writing is read off; a subject
    whose spread is within the noise floor has **collapsed** -- at that optimisation level, in that
    regime, the choice between its writings does not reach the metal.  The count of collapsed
    subjects per level is the answer to the card's opening question, and it is a count of the same
    subjects at every level, so the levels are directly comparable.
    """
    floor = agreement["working_floor"]
    by_cell: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for cell in agreement["cells"]:
        if cell["axis"] != MODE_AXIS[cell["mode"]]:
            continue
        key = (cell["level"], cell["mode"])
        timings = cell["timings"]
        if len(timings) < 2:
            continue
        spread = _relative_gap(min(timings.values()), max(timings.values()))
        by_cell.setdefault(key, []).append(
            {"subject": cell["subject"], "spread": spread, "collapsed": spread <= floor}
        )
    rows = []
    for (level, mode), entries in sorted(by_cell.items()):
        spreads = sorted(entry["spread"] for entry in entries)
        rows.append(
            {
                "level": level,
                "mode": mode,
                "subjects": len(entries),
                "collapsed": sum(1 for entry in entries if entry["collapsed"]),
                "median_spread": statistics.median(spreads),
                "max_spread": spreads[-1],
                "entries": entries,
            }
        )
    return {"floor": floor, "rows": rows}


def survival_repeatability(
    repeats: int = 3,
    corpus: Sequence[Subject] = CORPUS,
    levels: Sequence[Level] = LEVELS,
    modes: Sequence[str] = MODES,
    floor: float | None = None,
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
) -> dict[str, Any]:
    """The survival count measured several times over, reported as a RANGE and never as a midpoint.

    **This function exists because review re-ran this card's timing half and did not get its
    numbers.**  The published report opened with ``54`` of ``64`` cells in which the choice between
    two writings of an object reaches the metal; three independent quiet re-runs returned ``46``,
    ``47`` and ``49``, and the reporting run was uniformly ``12-29%`` slower than a quiet re-run,
    which is contention and not a property of the writings.  A single reading of a
    contention-sensitive quantity is not a measurement of it.

    So the count is taken ``repeats`` times -- fresh compilation, fresh process, fresh timing each
    time -- and what is reported per ``(level, mode)`` is the smallest, the largest and the median
    count, together with ``stable``, which is ``True`` only when every repeat returned the SAME
    count.  A cell whose ``stable`` is ``False`` has no resolvable survival count on this machine at
    this precision, and both reports are required to say so rather than to publish the median as
    though it were the answer.

    ``floor`` is the resolution the count is read at.  Passing it explicitly is how the report's own
    published floor is re-used, so that a new count is comparable with the old one rather than being
    a different question; passing ``None`` uses each run's own measured noise floor, which moves
    between runs and is reported per repeat in ``quietness``.

    **How quiet the machine was is measured, not asserted.**  Every run carries one byte-identical
    duplicate per subject, so the gap between two copies of the same code is noise by construction.
    ``quietness`` reports the median and the worst such gap over every repeat; a run in which two
    identical kernels differ by more than the effects being ranked is a run that cannot rank them.
    """
    if repeats < 2:
        raise ValueError("repeatability needs at least two runs; one run cannot disagree with itself")
    corpus = tuple(corpus)
    writings = tuple(item for subject in corpus for item in subject.writings)
    per_cell: dict[tuple[str, str], list[dict[str, Any]]] = {}
    quiet: list[dict[str, Any]] = []
    for repeat in range(repeats):
        for level in levels:
            for mode in modes:
                run = benchmark(
                    writings,
                    level,
                    mode=mode,
                    iterations=iterations,
                    trials=trials,
                    duplicate=True,
                )
                _refuse_eliminated([run])
                measured = noise_floor([run])
                working = measured["floor"] if floor is None else floor
                spreads = []
                for subject in corpus:
                    names = [_kernel_name(item) for item in subject.writings]
                    timings = [run["results"][name]["median"] for name in names]
                    spreads.append(_relative_gap(min(timings), max(timings)))
                collapsed = sum(1 for spread in spreads if spread <= working)
                per_cell.setdefault((level.name, mode), []).append(
                    {
                        "repeat": repeat,
                        "floor": working,
                        "subjects": len(spreads),
                        "collapsed": collapsed,
                        "reaching": len(spreads) - collapsed,
                        "median_spread": statistics.median(spreads),
                        "max_spread": max(spreads),
                        "wall_seconds": run["wall_seconds"],
                    }
                )
                quiet.append(
                    {
                        "repeat": repeat,
                        "level": level.name,
                        "mode": mode,
                        "identical_kernel_median_gap": measured["median"],
                        "identical_kernel_worst_gap": measured["maximum"],
                        "measured_floor": measured["floor"],
                    }
                )

    rows = []
    for (level_name, mode), entries in sorted(per_cell.items()):
        reaching = [entry["reaching"] for entry in entries]
        medians = [entry["median_spread"] for entry in entries]
        rows.append(
            {
                "level": level_name,
                "mode": mode,
                "repeats": len(entries),
                "subjects": entries[0]["subjects"],
                "floor": entries[0]["floor"] if floor is not None else None,
                "reaching_min": min(reaching),
                "reaching_max": max(reaching),
                "reaching_median": statistics.median(reaching),
                "reaching_every_run": sorted(reaching),
                "collapsed_min": entries[0]["subjects"] - max(reaching),
                "collapsed_max": entries[0]["subjects"] - min(reaching),
                "median_spread_min": min(medians),
                "median_spread_max": max(medians),
                "stable": len(set(reaching)) == 1,
                "runs": entries,
            }
        )
    totals = []
    for repeat in range(repeats):
        totals.append(
            sum(
                entry["reaching"]
                for entries in per_cell.values()
                for entry in entries
                if entry["repeat"] == repeat
            )
        )
    worst_gaps = [item["identical_kernel_worst_gap"] for item in quiet]
    median_gaps = [item["identical_kernel_median_gap"] for item in quiet]
    return {
        "repeats": repeats,
        "floor": floor,
        "iterations": iterations,
        "trials": trials,
        "rows": rows,
        "cells": len(rows),
        "stable_cells": sum(1 for row in rows if row["stable"]),
        "total_reaching_per_repeat": totals,
        "total_reaching_min": min(totals),
        "total_reaching_max": max(totals),
        "total_subject_cells": sum(row["subjects"] for row in rows),
        "quietness": {
            "runs": quiet,
            "identical_kernel_median_gap": statistics.median(median_gaps),
            "identical_kernel_worst_gap": max(worst_gaps),
        },
        "environment": environment(),
    }


# ------------------------------------------------------------------------------ instruction audit

_MNEMONIC = re.compile(r"^\s+([a-z][a-z0-9._]*)\b")
_LABEL = re.compile(r"^([A-Za-z_$.][\w$.]*):")


def _split_functions(assembly: str) -> dict[str, list[str]]:
    functions: dict[str, list[str]] = {}
    current: str | None = None
    for line in assembly.splitlines():
        label = _LABEL.match(line)
        if label:
            name = label.group(1)
            # A local label (``.LBB0_1``) is inside the function that is already open, so it must
            # not close it; only a real symbol starts a new one.
            if not name.startswith("."):
                current = name
                functions.setdefault(current, [])
            continue
        if current is None:
            continue
        match = _MNEMONIC.match(line)
        if match:
            mnemonic = match.group(1)
            if not mnemonic.startswith("."):
                functions[current].append(mnemonic)
    return functions


def instruction_audit(
    writings: Sequence[Writing] = (),
    levels: Sequence[Level] = LEVELS,
    workdir: Path | None = None,
) -> dict[str, Any]:
    """What clang actually emitted for each writing, counted from the assembly.

    A timing is a noisy estimate of what the machine did; an instruction count is not.  Each writing
    is compiled as the standalone function :func:`emit_c` produces, ``-S`` is read back, and the
    mnemonics inside that function are counted.  Two writings of one object that compile to the same
    multiset of instructions have had their difference erased by the compiler, and that is visible
    here with no noise floor at all.

    ``fma`` counts scalar and packed fused multiply-add forms; ``divide`` counts scalar and packed
    divides; ``packed`` counts any instruction whose suffix says it operated on more than one
    double at a time, which is how vectorisation shows up.

    **The multiply count is reported three ways, and that is a repair.**  ``multiply`` matches
    ``v?mul[sp]d``, so it has always counted ``mulpd`` and ``vmulpd`` beside ``mulsd`` and
    ``vmulsd``.  The reports printed that single column under the heading ``mulsd`` and called it
    "the scalar multiplies", which was false for two of the six rows they showed; review caught it
    by recompiling one of them.  ``multiply_scalar`` and ``multiply_packed`` now exist so a table
    can print the number under a name that matches it, and ``multiply`` is kept as their sum with
    its meaning written down rather than assumed.

    ``packed_arithmetic`` counts only packed ADD, SUB, MUL and DIV -- the instructions that do
    arithmetic on two doubles at once -- as opposed to ``packed``, which also counts ``movapd``,
    ``unpcklpd`` and the rest of the shuffling that surrounds them.  A writing with a non-zero
    ``packed_arithmetic`` is one the compiler put in a vector register, and that turned out to be
    the fact the mislabelled column was hiding.
    """
    writings = tuple(writings) or tuple(item for subject in CORPUS for item in subject.writings)
    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_")) if owned else Path(workdir)
    rows = []
    try:
        # The ``static`` is dropped so the function has external linkage and survives at every
        # level.  A wrapper would not do: at ``-O0`` nothing is inlined, so the wrapper would
        # contain a call and none of the arithmetic being counted.
        parts = [
            emit_c(tree_of(writing.source), _kernel_name(writing)).replace("static double", "double", 1)
            for writing in writings
        ]
        source = "".join(parts)
        directory.mkdir(parents=True, exist_ok=True)
        csource = directory / "audit.c"
        csource.write_text(source, encoding="ascii")
        for level in levels:
            target = directory / f"audit_{level.name}.s"
            command = ["clang", *level.flags, "-S", "-o", str(target), str(csource)]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise CompilationError(f"{' '.join(command)}\n{result.stderr}")
            functions = _split_functions(target.read_text(encoding="utf-8", errors="replace"))
            for writing in writings:
                name = _kernel_name(writing)
                mnemonics = functions.get(name, [])
                arithmetic = [item for item in mnemonics if re.search(r"(sd|pd)$", item)]
                rows.append(
                    {
                        "level": level.name,
                        "kernel": _kernel_name(writing),
                        "subject": writing.subject,
                        "role": writing.role,
                        "instructions": len(mnemonics),
                        "arithmetic": len(arithmetic),
                        "fma": sum(1 for item in mnemonics if "fmadd" in item or "fmsub" in item or "fnmadd" in item or "fnmsub" in item),
                        "divide": sum(1 for item in mnemonics if re.match(r"v?div[sp]d$", item)),
                        # Scalar and packed multiplies apart, and their sum.  See the docstring:
                        # ``multiply`` counted both from the start and was printed under a scalar
                        # heading, which is the mislabel this split repairs.
                        "multiply": sum(1 for item in mnemonics if re.match(r"v?mul[sp]d$", item)),
                        "multiply_scalar": sum(1 for item in mnemonics if re.match(r"v?mulsd$", item)),
                        "multiply_packed": sum(1 for item in mnemonics if re.match(r"v?mulpd$", item)),
                        "packed_arithmetic": sum(
                            1 for item in mnemonics if re.match(r"v?(add|sub|mul|div)pd$", item)
                        ),
                        "packed": sum(1 for item in mnemonics if item.endswith("pd")),
                        "mnemonics": mnemonics,
                    }
                )
    finally:
        if owned:
            shutil.rmtree(directory, ignore_errors=True)

    collapse = []
    for level in levels:
        for subject in {item.subject for item in writings}:
            group = [row for row in rows if row["level"] == level.name and row["subject"] == subject]
            if len(group) < 2:
                continue
            signatures = {tuple(sorted(row["mnemonics"])) for row in group}
            collapse.append(
                {
                    "level": level.name,
                    "subject": subject,
                    "writings": len(group),
                    "distinct_instruction_multisets": len(signatures),
                    "identical": len(signatures) == 1,
                }
            )
    return {
        "rows": rows,
        "collapse": sorted(collapse, key=lambda item: (item["level"], item["subject"])),
        "identical_by_level": {
            level.name: sum(
                1 for item in collapse if item["level"] == level.name and item["identical"]
            )
            for level in levels
        },
        "subjects_compared": len({item["subject"] for item in collapse}),
        "writings_compared": len(writings),
        # How many writings the compiler put in a vector register at each level, and the multiply
        # totals split the way the reports must print them.  All three are counts read off the
        # assembly and carry no noise floor.
        "vectorised_by_level": {
            level.name: sum(
                1
                for row in rows
                if row["level"] == level.name and row["packed_arithmetic"] > 0
            )
            for level in levels
        },
        "multiply_scalar_by_level": {
            level.name: sum(row["multiply_scalar"] for row in rows if row["level"] == level.name)
            for level in levels
        },
        "multiply_packed_by_level": {
            level.name: sum(row["multiply_packed"] for row in rows if row["level"] == level.name)
            for level in levels
        },
    }


def loop_instruction_audit(
    writings: Sequence[Writing] = (),
    mode: str = "throughput",
    levels: Sequence[Level] = LEVELS,
    workdir: Path | None = None,
) -> dict[str, Any]:
    """What clang emitted for the kernels that were actually TIMED, not for the bare functions.

    :func:`instruction_audit` compiles each writing as a standalone function, which is the cleanest
    view of what the compiler does to the dataflow graph but is not the code the stopwatch ran on.
    This audit compiles the benchmark program itself with ``-S`` and counts the mnemonics inside each
    timed kernel, loop and loads included.  Where the two disagree, this one is the one a timing
    belongs to.
    """
    writings = tuple(writings) or tuple(item for subject in CORPUS for item in subject.writings)
    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_")) if owned else Path(workdir)
    rows = []
    try:
        source, kernel_names = emit_program(writings, mode, guard=True, duplicate=False)
        directory.mkdir(parents=True, exist_ok=True)
        csource = directory / f"loops_{mode}.c"
        csource.write_text(source, encoding="ascii")
        for level in levels:
            target = directory / f"loops_{mode}_{level.name}.s"
            command = ["clang", *level.flags, "-S", "-o", str(target), str(csource)]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise CompilationError(f"{' '.join(command)}\n{result.stderr}")
            functions = _split_functions(target.read_text(encoding="utf-8", errors="replace"))
            for writing, name in zip(writings, kernel_names, strict=True):
                mnemonics = functions.get(name, [])
                rows.append(
                    {
                        "level": level.name,
                        "mode": mode,
                        "kernel": name,
                        "subject": writing.subject,
                        "role": writing.role,
                        "instructions": len(mnemonics),
                        "fma": sum(
                            1
                            for item in mnemonics
                            if "fmadd" in item or "fmsub" in item or "fnmadd" in item or "fnmsub" in item
                        ),
                        "divide": sum(1 for item in mnemonics if re.match(r"v?div[sp]d$", item)),
                        "packed": sum(1 for item in mnemonics if item.endswith("pd")),
                        "found": bool(mnemonics),
                    }
                )
    finally:
        if owned:
            shutil.rmtree(directory, ignore_errors=True)
    return {
        "mode": mode,
        "rows": rows,
        "all_found": all(row["found"] for row in rows),
        # A kernel with no symbol of its own was inlined into ``main``: at ``O3fast`` clang can see
        # through the static dispatch table and does exactly that to the smallest kernels.  Its
        # timing is unaffected -- the work still happens inside the timed block -- but its
        # instructions cannot be attributed, and that is reported rather than reported as zero.
        "missing": [
            {"level": row["level"], "kernel": row["kernel"]} for row in rows if not row["found"]
        ],
        "fma_by_level": {
            level.name: sum(row["fma"] for row in rows if row["level"] == level.name)
            for level in levels
        },
        "packed_by_level": {
            level.name: sum(row["packed"] for row in rows if row["level"] == level.name)
            for level in levels
        },
        "divide_by_level": {
            level.name: sum(row["divide"] for row in rows if row["level"] == level.name)
            for level in levels
        },
    }


# ---------------------------------------------------------------------------- flag isolation


#: The flag combinations :func:`flag_isolation_audit` compiles, to answer one question: **which of
#: the two flags on the ``O2nativefma`` rung is responsible for what?**
#:
#: ``O2`` is the baseline.  ``O2contract`` adds only the fusion flag.  ``O2native`` adds only the
#: ISA flag.  ``O2nativefma`` is the rung itself.  The last two are the mechanism test: ``-mfma`` is
#: the narrowest switch that makes an FMA instruction available at all, so if fusion could be varied
#: without changing anything else, ``-mfma`` alone against ``-mfma -ffp-contract=fast`` is where it
#: would show.
FLAG_COMBINATIONS: dict[str, tuple[str, ...]] = {
    "O2": ("-O2",),
    "O2contract": ("-O2", "-ffp-contract=fast"),
    "O2native": ("-O2", "-march=native"),
    "O2nativefma": ("-O2", "-march=native", "-ffp-contract=fast"),
    "O2mfma": ("-O2", "-mfma"),
    "O2mfmacontract": ("-O2", "-mfma", "-ffp-contract=fast"),
}

_FMA_MNEMONIC = re.compile(r"fn?m(add|sub)")


def flag_isolation_audit(
    writings: Sequence[Writing] = (),
    mode: str = "throughput",
    combinations: dict[str, tuple[str, ...]] | None = None,
    workdir: Path | None = None,
) -> dict[str, Any]:
    """What each flag of the ``O2nativefma`` rung does on its own, counted from the assembly.

    **This function exists because review found the module lying about its own ladder.**  An earlier
    revision described that rung as "as O2 plus cross-statement multiply-add fusion" and said in the
    docstring that "the ONLY difference from ``O2`` is fusion".  Both flags were on it, and nobody
    had measured which one mattered.

    Each combination is compiled to assembly and every timed kernel's instruction multiset is
    compared against the ``-O2`` baseline's, exactly as :func:`instruction_audit` compares two
    writings.  There is no timing here and therefore no noise floor: two multisets are equal or they
    are not.

    The conclusion the numbers force is reported in ``separable``: whether ANY combination adds a
    fused multiply-add while leaving every kernel's instruction multiset otherwise equal to the
    baseline's.  On this machine it is ``False``, and the reason is structural rather than a clang
    quirk -- enabling the FMA instruction also switches the encoding to VEX, so the smallest step
    that makes fusion reachable has already rewritten every kernel.
    """
    writings = tuple(writings) or tuple(item for subject in CORPUS for item in subject.writings)
    combinations = dict(combinations or FLAG_COMBINATIONS)
    if "O2" not in combinations:
        raise ValueError("the isolation audit needs the plain -O2 baseline to compare against")
    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_")) if owned else Path(workdir)
    per_combination: dict[str, dict[str, list[str]]] = {}
    try:
        source, kernel_names = emit_program(writings, mode, guard=True, duplicate=False)
        directory.mkdir(parents=True, exist_ok=True)
        csource = directory / f"isolation_{mode}.c"
        csource.write_text(source, encoding="ascii")
        for name, flags in combinations.items():
            target = directory / f"isolation_{mode}_{name}.s"
            command = ["clang", *flags, "-S", "-o", str(target), str(csource)]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise CompilationError(f"{' '.join(command)}\n{result.stderr}")
            functions = _split_functions(target.read_text(encoding="utf-8", errors="replace"))
            per_combination[name] = {kernel: functions.get(kernel, []) for kernel in kernel_names}
    finally:
        if owned:
            shutil.rmtree(directory, ignore_errors=True)

    baseline = per_combination["O2"]
    rows = []
    for name, flags in combinations.items():
        current = per_combination[name]
        identical = sum(
            1 for kernel in baseline if sorted(baseline[kernel]) == sorted(current[kernel])
        )
        fma = sum(sum(1 for item in body if _FMA_MNEMONIC.search(item)) for body in current.values())
        rows.append(
            {
                "combination": name,
                "flags": list(flags),
                "kernels": len(baseline),
                "identical_to_baseline": identical,
                "changed_from_baseline": len(baseline) - identical,
                "fma": fma,
                # A VEX-encoded instruction is how ``-march=native`` shows up even where the
                # arithmetic is unchanged: the same operation, a different encoding.
                "vex": sum(
                    sum(1 for item in body if item.startswith("v")) for body in current.values()
                ),
                "packed": sum(
                    sum(1 for item in body if item.endswith("pd")) for body in current.values()
                ),
                "instructions": sum(len(body) for body in current.values()),
            }
        )
    by_name = {row["combination"]: row for row in rows}
    return {
        "mode": mode,
        "kernels": len(baseline),
        "rows": rows,
        "by_combination": by_name,
        # The two headline facts, named so a test can pin each on its own.
        "contract_alone_changes_nothing": (
            by_name["O2contract"]["changed_from_baseline"] == 0 and by_name["O2contract"]["fma"] == 0
        )
        if "O2contract" in by_name
        else None,
        "isa_alone_fuses_nothing": (
            by_name["O2native"]["changed_from_baseline"] == by_name["O2native"]["kernels"]
            and by_name["O2native"]["fma"] == 0
        )
        if "O2native" in by_name
        else None,
        # Is there any combination that adds fusion and changes nothing else?  If there were, the
        # rung could honestly be split in two.  There is not.
        "separable": any(
            row["fma"] > 0 and row["changed_from_baseline"] == 0
            for row in rows
            if row["combination"] != "O2"
        ),
    }


# ------------------------------------------------------------------------- the harness floor


#: Leaf counts the harness calibration times: from a kernel with no arithmetic at all to one with
#: thirty-one operations, so the loop's own cost and the cost of one operation are separated.
CALIBRATION_LEAVES: tuple[int, ...] = (1, 2, 4, 8, 16, 32)


def harness_calibration(
    level: str = "O2",
    mode: str = "throughput",
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
) -> dict[str, Any]:
    """What the loop costs before any arithmetic, and what one operation costs on top of it.

    Balanced sums over ``1, 2, 4, ... 32`` distinct variables are timed in one program.  The
    one-leaf kernel has **no operations at all** -- it loads a value and accumulates it -- so its
    time is the harness itself: the loop, the index, the load and the accumulate.  A least-squares
    line through seconds-per-step gives that overhead as the intercept and the marginal cost of one
    unit as the slope.

    The line is fitted against the axis the regime is supposed to answer to -- ``operations`` in the
    throughput regime, ``depth`` in the latency regime -- because these are balanced sums, whose
    depth grows as the logarithm of their operation count.  Fitting latency against operation count
    would be fitting the wrong variable and the slope would mean nothing.

    This matters because the overhead is added to every writing of an object equally.  It cannot
    change which writing is faster, but it **compresses** every relative gap this card reports, so a
    reader who wants the gap between two dataflow graphs rather than between two loops should read
    the reported gaps as a lower bound.
    """
    writings = tuple(
        Writing("calibration", f"leaves_{count:02d}", _balanced_source(_leaf_names(count), "+"))
        for count in CALIBRATION_LEAVES
    )
    run = benchmark(writings, level, mode=mode, iterations=iterations, trials=trials)
    points = []
    for writing in writings:
        profile = structural_profile(tree_of(writing.source))
        points.append(
            {
                "role": writing.role,
                "leaves": profile["leaves"],
                "operations": profile["operations"],
                "depth": profile["depth"],
                "seconds_per_step": run["results"][_kernel_name(writing)]["median"],
            }
        )
    axis = MODE_AXIS[mode]
    xs = [point[axis] for point in points]
    ys = [point["seconds_per_step"] for point in points]
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    variance = sum((x - mean_x) ** 2 for x in xs)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True)) / variance
    intercept = mean_y - slope * mean_x
    return {
        "level": level,
        "mode": mode,
        "iterations": run["iterations"],
        "trials": trials,
        "points": points,
        "fitted_against": axis,
        "zero_operation_seconds": points[0]["seconds_per_step"],
        "intercept_seconds": intercept,
        "slope_seconds_per_unit": slope,
    }


# ------------------------------------------------------------------------------- shape catalogue


@lru_cache(maxsize=None)
def _shape_catalogue(leaves: int) -> dict[tuple[int, int], Any]:
    """One witness shape per achievable ``(depth, peak_live)`` over ``leaves`` leaves.

    A shape is a nested pair of leaf counts.  The recursion is the same pair of rules the two
    imported measures use -- ``depth`` is ``1 + max`` and ``peak_live`` is Sethi-Ullman -- so the
    catalogue cannot drift from them; the tests check every witness against the imported functions
    rather than against this table.
    """
    if leaves < 1:
        raise ValueError("a shape needs at least one leaf")
    if leaves == 1:
        return {(0, 1): 1}
    table: dict[tuple[int, int], Any] = {}
    for left_size in range(1, leaves):
        right_size = leaves - left_size
        for (left_depth, left_peak), left_shape in _shape_catalogue(left_size).items():
            for (right_depth, right_peak), right_shape in _shape_catalogue(right_size).items():
                node_depth = 1 + max(left_depth, right_depth)
                node_peak = max(left_peak, right_peak) if left_peak != right_peak else left_peak + 1
                table.setdefault((node_depth, node_peak), (left_shape, right_shape))
    return table


def _shape_source(shape: Any, names: Iterable[str], operator: str = "+") -> str:
    stream = iter(names)

    def build(node: Any) -> str:
        if node == 1:
            return next(stream)
        return f"({build(node[0])} {operator} {build(node[1])})"

    return build(shape)


def peak_live_bound_table(sizes: Sequence[int] = (8, 12, 16, 20, 24, 32, 40, 48)) -> dict[str, Any]:
    """The largest peak-live spread constructible at a FIXED operation count and a FIXED depth.

    Swept rather than assumed, because the card forbids reading a bound as a result.  Two facts come
    off the sweep and both matter for divergence 4:

    * within a fixed operation count and a fixed depth the peak-live spread is small, and the sweep
      shows how it grows;
    * the largest peak live any tree of ``n`` leaves can have is ``floor(log2(n)) + 1``, so a straight
      line expression would need ``2 ** 16 == 65536`` leaves before it could ask for more than the
      sixteen architectural ``xmm`` registers of this instruction set.
    """
    rows = []
    for size in sizes:
        catalogue = _shape_catalogue(size)
        by_depth: dict[int, list[int]] = {}
        for node_depth, node_peak in catalogue:
            by_depth.setdefault(node_depth, []).append(node_peak)
        best_depth = max(by_depth, key=lambda key: (max(by_depth[key]) - min(by_depth[key]), -key))
        peaks = sorted(by_depth[best_depth])
        rows.append(
            {
                "leaves": size,
                "operations": size - 1,
                "depth": best_depth,
                "min_peak_live": peaks[0],
                "max_peak_live": peaks[-1],
                "spread": peaks[-1] - peaks[0],
                "max_peak_live_any_depth": max(peak for _, peak in catalogue),
                "log2_bound": size.bit_length() - 1 + 1,
            }
        )
    return {
        "rows": rows,
        "architectural_xmm_registers": 16,
        "leaves_needed_to_exceed_registers": 2**16,
        "bound_holds": all(row["max_peak_live_any_depth"] <= row["log2_bound"] for row in rows),
    }


# ------------------------------------------------------------------------------ divergence probes


def _chain_source(names: Sequence[str], operator: str) -> str:
    return f" {operator} ".join(names)


def _balanced_source(names: Sequence[str], operator: str) -> str:
    if len(names) == 1:
        return names[0]
    half = len(names) // 2
    return f"({_balanced_source(names[:half], operator)} {operator} {_balanced_source(names[half:], operator)})"


#: Leaf names for the constructed probes: ``v0``, ``v1``, ... , distinct so that no subtree of one
#: probe writing can be common-subexpression-eliminated against another, which would silently change
#: the operation count the probe is holding fixed.
def _leaf_names(count: int) -> tuple[str, ...]:
    return tuple(f"v{index}" for index in range(count))


#: The number of leaves each constructed probe uses.  Chosen so the arithmetic dominates the loads:
#: the loop reads one table entry per distinct variable and then issues ``leaves - 1`` operations.
PROBE_CHAIN_LEAVES: int = 16
PROBE_REGISTER_LEAVES: int = 40

#: How many differences of squares the fusion probe sums.  Eight, because one difference of squares
#: is three operations and the loop's own input loads would swamp it; eight of them summed in a
#: balanced tree is ``31`` operations against ``16`` loads.
PROBE_FMA_TERMS: int = 8


def _fma_probe_sources() -> tuple[str, str]:
    """The fusion probe's two writings: the same object, differing only in fusion sites.

    ``sum of (p + q) * (p - q)`` against ``sum of p*p - q*q``, over eight independent pairs, each sum
    written as a balanced tree.  The two are **equal**, and 0021's operation count, 0041's depth and
    0044's peak live are IDENTICAL on them -- the model has no way to tell them apart on any of its
    three axes.  What differs is that a difference of squares is a multiply-add site and a product of
    a sum and a difference is not.
    """
    factored = [f"(p{index} + q{index}) * (p{index} - q{index})" for index in range(PROBE_FMA_TERMS)]
    expanded = [f"(p{index} * p{index} - q{index} * q{index})" for index in range(PROBE_FMA_TERMS)]
    return _balanced_source(factored, "+"), _balanced_source(expanded, "+")


def probe_subjects() -> tuple[Subject, ...]:
    """The four divergences as designed pairs, constructed here rather than hoped for.

    Every pair holds something fixed and moves one thing:

    ``probe_division``
        Two fractions added, against the same two put over a common denominator -- the schoolbook
        move, and the only way a TREE can trade a division for multiplications.  A tree cannot share
        a subexpression, so the reciprocal trick (``1/d`` computed once and multiplied four times) is
        not expressible in this project's representation at all; the common denominator is.  The
        model counts ``3`` operations against ``5``, so it prefers the separate fractions; the
        machine gets one division instead of two.

    ``probe_fma``
        Eight differences of squares summed, factored against expanded.  The two are EQUAL, and the
        model's three axes are identical on them -- same operation count, same depth, same peak live.
        A difference of squares is a multiply-add site; a product of a sum and a difference is not.

    ``probe_latency``
        Sixteen terms added as a chain against the same sixteen added as a balanced tree.  Equal
        operation count; depth ``15`` against depth ``4``.

    ``probe_registers``
        Forty terms in two shapes with the SAME operation count and the SAME depth, chosen from
        :func:`_shape_catalogue` as the pair with the largest peak-live spread constructible under
        those two constraints.
    """
    chain = _leaf_names(PROBE_CHAIN_LEAVES)
    catalogue = _shape_catalogue(PROBE_REGISTER_LEAVES)
    by_depth: dict[int, list[int]] = {}
    for node_depth, node_peak in catalogue:
        by_depth.setdefault(node_depth, []).append(node_peak)
    target_depth = max(by_depth, key=lambda key: (max(by_depth[key]) - min(by_depth[key]), -key))
    low = min(by_depth[target_depth])
    high = max(by_depth[target_depth])
    register_names = _leaf_names(PROBE_REGISTER_LEAVES)
    return (
        _subject(
            "probe_division",
            "probe",
            "the schoolbook common denominator: 3 model operations with two divisions against 5 with one",
            ("separate", "a / d + b / e"),
            ("common_denominator", "(a * e + b * d) / (d * e)"),
        ),
        _subject(
            "probe_fma",
            "probe",
            f"{PROBE_FMA_TERMS} differences of squares summed, factored against expanded: equal operations, "
            "equal depth, equal peak live, and the expanded side is entirely multiply-add shaped",
            ("factored", _fma_probe_sources()[0]),
            ("expanded", _fma_probe_sources()[1]),
        ),
        _subject(
            "probe_latency",
            "probe",
            f"{PROBE_CHAIN_LEAVES} terms, {PROBE_CHAIN_LEAVES - 1} additions, depth {PROBE_CHAIN_LEAVES - 1} against depth {(PROBE_CHAIN_LEAVES - 1).bit_length()}",
            ("chained", _chain_source(chain, "+")),
            ("balanced", _balanced_source(chain, "+")),
        ),
        _subject(
            "probe_registers",
            "probe",
            f"{PROBE_REGISTER_LEAVES - 1} additions and depth {target_depth} in both, peak live {low} against {high}",
            ("low_peak", _shape_source(catalogue[(target_depth, low)], register_names)),
            ("high_peak", _shape_source(catalogue[(target_depth, high)], register_names)),
        ),
    )


#: The predictions, **declared before the measurement** and pinned by a test independently of the
#: measured order, so that a change in either fails.
#:
#: Each entry maps ``(probe, mode, level)`` to the role the machine is predicted to favour, or to
#: ``None`` where the prediction is that the two are indistinguishable.
PROBE_PREDICTIONS: dict[str, dict[str, dict[str, str | None]]] = {
    "probe_division": {
        # A division is not pipelined the way a multiplication is, so in the regime where issue
        # slots bind, one division and three multiplications should beat two divisions even though
        # the model counts five operations against three.  In the regime where the dependent chain
        # binds the trade reverses: the common denominator puts a multiply and an add IN FRONT of
        # its division, so its critical path is longer than the separate fractions' single division.
        "throughput": {
            "O0": "common_denominator",
            "O2": "common_denominator",
            "O2nativefma": "common_denominator",
            "O3fast": "common_denominator",
        },
        "latency": {"O0": "separate", "O2": "separate", "O2nativefma": "separate", "O3fast": "separate"},
    },
    "probe_fma": {
        # The model cannot tell these apart on any of its three axes.  Neither should the machine
        # until fusion is enabled; from O2nativefma the multiply-add shape turns seven operations into
        # five instructions and should win where issue slots bind.  It should NOT win in the latency
        # regime: fusing a multiply and an add saves an issue slot, not a level of the critical
        # path, and both writings have three dependent levels either way.
        "throughput": {"O0": None, "O2": None, "O2nativefma": "expanded", "O3fast": "expanded"},
        "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
    },
    "probe_latency": {
        # Equal operation counts.  Independent loop steps hide the chain, so throughput should not
        # separate them; the latency regime should, decisively.  At O3fast -ffast-math lets LLVM
        # reassociate a long floating-point sum into a tree, which would erase even that.
        "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        "latency": {"O0": "balanced", "O2": "balanced", "O2nativefma": "balanced", "O3fast": None},
    },
    "probe_registers": {
        # Equal operations, equal depth, peak live far below the register file.  The prediction is
        # that the fourth axis costs nothing measurable anywhere.
        "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
    },
}


def divergence_probes(
    levels: Sequence[Level] = LEVELS,
    modes: Sequence[str] = MODES,
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
    floor: float | None = None,
) -> dict[str, Any]:
    """The four divergences as measured experiments, each against its declared prediction.

    The prediction for every ``(probe, regime, level)`` cell is in :data:`PROBE_PREDICTIONS` and was
    written before any of these numbers existed.  This function reports what the machine did and
    whether it matched, and it never edits the prediction to fit.
    """
    subjects = probe_subjects()
    wrong = [subject.name for subject in subjects if len(subject.writings) != 2]
    if wrong:
        raise ValueError(f"a probe is a PAIR; these do not have exactly two writings: {wrong}")
    writings = tuple(item for subject in subjects for item in subject.writings)
    profiles = {_kernel_name(item): structural_profile(tree_of(item.source)) for item in writings}

    runs = []
    for level in levels:
        for mode in modes:
            runs.append(
                benchmark(writings, level, mode=mode, iterations=iterations, trials=trials, duplicate=True)
            )
    _refuse_eliminated(runs)
    measured_floor = noise_floor(runs)
    working_floor = measured_floor["floor"] if floor is None else floor

    cells = []
    for run in runs:
        for subject in subjects:
            first, second = subject.writings[0], subject.writings[1]
            left, right = _kernel_name(first), _kernel_name(second)
            timings = {left: run["results"][left]["median"], right: run["results"][right]["median"]}
            spread = _relative_gap(timings[left], timings[right])
            if spread <= working_floor:
                observed: str | None = None
            else:
                observed = first.role if timings[left] < timings[right] else second.role
            predicted = PROBE_PREDICTIONS[subject.name][run["mode"]][run["level"]]
            sensitivity = [
                {
                    "floor": candidate,
                    "observed": (
                        None
                        if spread <= candidate
                        else (first.role if timings[left] < timings[right] else second.role)
                    ),
                }
                for candidate in sorted({*FLOOR_SWEEP, working_floor})
            ]
            cells.append(
                {
                    "probe": subject.name,
                    "level": run["level"],
                    "mode": run["mode"],
                    "predicted": predicted,
                    "observed": observed,
                    "held": predicted == observed,
                    "relative_gap": spread,
                    "roles": [first.role, second.role],
                    "seconds": [timings[left], timings[right]],
                    "floor_sensitivity": sensitivity,
                    "held_over_floors": sum(
                        1 for entry in sensitivity if entry["observed"] == predicted
                    ),
                    "floors_swept": len(sensitivity),
                }
            )
    return {
        "environment": environment(),
        "iterations": iterations,
        "trials": trials,
        "noise_floor": measured_floor,
        "working_floor": working_floor,
        "subjects": [
            {
                "probe": subject.name,
                "note": subject.note,
                "writings": [
                    {
                        "role": item.role,
                        "source": item.source,
                        "profile": profiles[_kernel_name(item)],
                    }
                    for item in subject.writings
                ],
            }
            for subject in subjects
        ],
        "cells": cells,
        "held": sum(1 for cell in cells if cell["held"]),
        "cell_count": len(cells),
        "failed": [cell for cell in cells if not cell["held"]],
        "_runs": runs,
    }


def probe_repeatability(repeats: int = 3, **options: Any) -> dict[str, Any]:
    """Run the whole probe set several times and report, per cell, how far its answer moved.

    **This is the part of the method that decides how much of the probe table can be believed.**  A
    single run gives one relative gap per cell and says nothing about whether that gap would come
    back.  Repeating the whole set -- fresh compilation, fresh process, fresh timing -- and recording
    the smallest and largest gap each cell produced says exactly which cells the machine answers the
    same way every time and which it does not.

    ``resolved_agrees`` is whether the faster writing was the same one in every repeat.  A cell where
    it is ``False`` has no measured order on this machine, however small its p-value would look.
    """
    if repeats < 2:
        raise ValueError("repeatability needs at least two runs; one run cannot disagree with itself")
    runs = [divergence_probes(**options) for _ in range(repeats)]
    cells: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for run in runs:
        for cell in run["cells"]:
            key = (cell["probe"], cell["mode"], cell["level"])
            faster = cell["roles"][0] if cell["seconds"][0] < cell["seconds"][1] else cell["roles"][1]
            cells.setdefault(key, []).append({"gap": cell["relative_gap"], "faster": faster})
    rows = []
    for (probe, mode, level), samples in cells.items():
        gaps = [item["gap"] for item in samples]
        directions = {item["faster"] for item in samples}
        rows.append(
            {
                "probe": probe,
                "mode": mode,
                "level": level,
                "minimum_gap": min(gaps),
                "maximum_gap": max(gaps),
                "median_gap": statistics.median(gaps),
                "directions": sorted(directions),
                "resolved_agrees": len(directions) == 1,
            }
        )
    return {
        "repeats": repeats,
        "rows": rows,
        "cells": len(rows),
        "cells_agreeing_on_direction": sum(1 for row in rows if row["resolved_agrees"]),
        "widest_relative_range": max(row["maximum_gap"] - row["minimum_gap"] for row in rows),
    }


# ------------------------------------------------------------------------------ parallel decision

#: Cores kept free so a compile sweep cannot starve the interactive session (0038/0044/0049 policy).
WORKER_HEADROOM_CORES: int = 2

#: Upper bound on the spawn cost any one sweep has to amortise (0038/0044/0049 policy).
WORKER_CAP: int = 12


def worker_count_for(cores: int, jobs: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``jobs`` independent compilations."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(jobs, 1)))


def default_worker_count(jobs: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, jobs)


def parallel_decision(repeats: int = 3) -> dict[str, Any]:
    """Where this card uses many cores, where it refuses to, and the measurement behind each.

    **Compilation is parallel.**  Each ``clang`` invocation is an independent external process, so
    the work is IO-bound from Python's side and a thread pool costs nothing but is limited by how
    many processes the machine will run at once.  The speedup is measured here, not assumed.

    **Timing is strictly sequential, and that is not an oversight.**  Concurrent load moves clock
    frequency, contends for last-level cache and moves threads between cores; experiment 0041's
    timings were irreproducible for exactly that reason.  A parallel timing run would change what is
    measured, not how fast it is measured, which the repository's multicore policy forbids.
    """
    if not clang_available():
        return {"clang": False}
    subjects = CORPUS
    writings = tuple(item for subject in subjects for item in subject.writings)
    jobs = [(level, mode) for level in LEVELS for mode in MODES]
    workers = default_worker_count(len(jobs))
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_"))
    try:
        sources = {
            (level.name, mode): emit_program(writings, mode, duplicate=True)[0]
            for level, mode in jobs
        }

        def compile_one(job: tuple[Level, str]) -> float:
            level, mode = job
            started = time.perf_counter()
            compile_program(
                sources[(level.name, mode)], level.flags, directory, f"seq_{level.name}_{mode}"
            )
            return time.perf_counter() - started

        sequential = []
        for _ in range(repeats):
            started = time.perf_counter()
            for job in jobs:
                compile_one(job)
            sequential.append(time.perf_counter() - started)

        def compile_parallel(job: tuple[Level, str]) -> float:
            level, mode = job
            started = time.perf_counter()
            compile_program(
                sources[(level.name, mode)], level.flags, directory, f"par_{level.name}_{mode}"
            )
            return time.perf_counter() - started

        parallel = []
        for _ in range(repeats):
            started = time.perf_counter()
            with ThreadPoolExecutor(max_workers=workers) as pool:
                list(pool.map(compile_parallel, jobs))
            parallel.append(time.perf_counter() - started)
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    best_sequential = min(sequential)
    best_parallel = min(parallel)
    return {
        "clang": True,
        "cores": os.cpu_count(),
        "workers": workers,
        "jobs": len(jobs),
        "repeats": repeats,
        "sequential_seconds": sequential,
        "parallel_seconds": parallel,
        "best_sequential": best_sequential,
        "best_parallel": best_parallel,
        "speedup": best_sequential / best_parallel,
        "compilation_parallel": best_parallel < best_sequential,
        "timing_parallel": False,
        "timing_note": (
            "timing runs are sequential by design: concurrent load changes the measurement itself, "
            "which is what made experiment 0041's timings irreproducible"
        ),
    }


# ----------------------------------------------------------------------------------- the report


def metal_report(
    iterations: int = DEFAULT_ITERATIONS,
    trials: int = DEFAULT_TRIALS,
    levels: Sequence[Level] = LEVELS,
    modes: Sequence[str] = MODES,
    survival_repeats: int = 5,
    survival_floor: float | None = PUBLISHED_FLOOR,
) -> dict[str, Any]:
    """Everything this card measured, in the order the reports read it.

    Correctness first, unconditionally: if any emitted function disagrees with the oracle the
    function raises before a single timing is reported.

    The instruction-level audits come next and the timing follows them, which is the order the
    reports read the result in and the order review established is the defensible one: the
    instruction-level half reproduces exactly on a different machine state with an independently
    written harness, and the timing half does not.  ``survival_repeats`` is why -- the survival
    count is taken that many times and published as a range.
    """
    if not clang_available():
        raise RuntimeError("experiment 0053 needs clang on PATH; none was found")
    # Every function this card compiles, the probes' included -- a probe whose value is wrong is as
    # useless as a corpus writing whose value is wrong, and the probes are where the card's sharpest
    # claims come from.
    correctness = correctness_audit(
        writings=tuple(item for subject in CORPUS for item in subject.writings)
        + tuple(item for subject in probe_subjects() for item in subject.writings),
        levels=levels,
    )
    if not correctness["all_match"]:
        raise RuntimeError(f"emitted C disagrees with the oracle: {correctness['levels']}")
    agreement = agreement_table(levels=levels, modes=modes, iterations=iterations, trials=trials)
    probes = divergence_probes(levels=levels, modes=modes, iterations=iterations, trials=trials)
    return {
        "environment": environment(),
        "correctness": correctness,
        "guard": guard_audit(iterations=iterations),
        "repetition_curve": repetition_curve(),
        "agreement": {key: value for key, value in agreement.items() if key != "_runs"},
        "survival": survival_table(agreement),
        "probes": {key: value for key, value in probes.items() if key != "_runs"},
        "instructions": instruction_audit(),
        "loop_instructions": {mode: loop_instruction_audit(mode=mode) for mode in modes},
        # What each flag of the O2nativefma rung does on its own.  Deterministic, so it needs no
        # repeats and carries no noise floor.
        "flag_isolation": {mode: flag_isolation_audit(mode=mode) for mode in modes},
        # The timing half's survival count, taken several times and published as a range.  A single
        # reading of this quantity is not a measurement of it: see the docstring.
        "survival_repeatability": survival_repeatability(
            repeats=survival_repeats, floor=survival_floor, iterations=iterations, trials=trials
        ),
        "harness": {
            f"{level.name}/{mode}": harness_calibration(
                level=level.name, mode=mode, iterations=iterations, trials=trials
            )
            for level in levels
            for mode in modes
        },
        "latency_paths": latency_path_audit(),
        "peak_live_bound": peak_live_bound_table(),
        "parallel": parallel_decision(),
    }
