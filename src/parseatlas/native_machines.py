"""Experiment 0056: twenty-five native machines against one machine plus a conversion.

The owner set this card on 2026-09-05, having asked for it three times:

    "My aim is that you have 25 NATIVE parsers and not lookup tables - the state machine must
     translate the code straight into that dataflow and not do a conversion to G0.  The compiler
     translates once, and then you execute a million times."

    "When you parse a Python script every time, you learn nothing there, because you are performing
     a redundant operation every time."

Two architectures are on trial and this module builds both.

.. code-block:: text

    ONE MACHINE + CONVERSION   read the string with the conventional grammar, then rewrite the
                               tree into the world you meant
    TWENTY-FIVE NATIVE         each world is its own machine; it reads the string into its own
                               tree directly, with no intermediate in another world

What "native" means here, precisely
-----------------------------------

:mod:`parseatlas.parser` is table-driven: one loop that reads a binding power out of a ``Grammar``
object at run time (``self._powers[self._current.value]``).  That is the lookup-table architecture
the owner is rejecting.

A **native** machine is Python source **specialised to one grammar**, in which the binding powers
are constants of the emitted code and no grammar object is consulted at run time.  It is emitted by
:func:`emit_native_source`, compiled once with :func:`compile` and :func:`exec`, and then executed
as an ordinary function.  One generator emits all 25, so a world is *data to the generator* and a
*constant to the machine*.

**Two native variants are emitted and both are measured, in every world.**  Publishing one would
have made the result an artifact of how the specialisation happened to be written:

``levels``
    one function per precedence level, unrolled.  The binding powers do not appear at all - they
    have become the call structure.  This is the strongest form of the specialisation.

``climb``
    a literal partial evaluation of the table-driven loop: the same single recursive function, with
    the dictionary lookup replaced by a chain of comparisons against constant operator literals and
    constant integer powers.

A third variant, ``lookup``, is emitted by the same generator and is **not** native: it is the
control described under the null model below.

Whether either native variant is worth anything is exactly what this card measures, and the answer
may be no.

The null model, declared before any number
------------------------------------------

A specialised parser beating a table-driven one says **nothing** about the 25 worlds.  It is the
ordinary win of partial evaluation and it would appear with one world just as with twenty-five.  So
the control is

.. code-block:: text

    NATIVE G0  against  TABLE-DRIVEN G0        the SAME world; any gap is pure specialisation

and every claim about the 25 is stated against it.  :func:`specialisation_control` computes that
single ratio and :func:`throughput_table` reports every world's ratio beside it.

**Which table-driven machine, though, decides the answer, so both are measured.**
:func:`parseatlas.parser.parse` rebuilds its binding-power dictionary inside ``Parser.__init__``, so
the project's own machine pays for the table on every call.  A native machine that beat only that
would have been measuring a dictionary comprehension.  The ``lookup`` variant emitted by this
module's own generator is the strict control: the same functions, the same call protocol, the same
index passing, differing from ``climb`` **only** in that the power comes from a dictionary at run
time.  With everything else held byte-identical, their difference is partial evaluation and nothing
else, and that is the baseline the headline is stated against.

What the card found, so a reader of the code is not left to infer it
--------------------------------------------------------------------

Against the shipped parser the native machines win and pay back their generation in a few hundred
parses.  Against the ``lookup`` control the ``levels`` machine is measurably *slower* and the
``climb`` machine is indistinguishable.  The whole effect is the per-call dictionary, not the
architecture.  The half that survives is the emitted dataflow: :func:`dataflow_table`,
:func:`distinct_graph_table` and :func:`instruction_table` are where this card's real results are.

The null model has a second half that is stronger than a ratio, and it is structural rather than
timed.  :func:`machine_isomorphism_audit` normalises each emitted machine by replacing its operator
literals with their ``(level, slot)`` positions.  If the 24 strict machines are then **byte-identical
source**, there is no per-world code difference for a per-world speed difference to come from, and
any spread across the 24 belongs to the corpus's operator mix and not to the conventions.  That is
measured, not argued.

Capability, answered before it is measured
------------------------------------------

**There is no capability gap, and this card does not manufacture one.**  A conversion that may
rewrite a tree arbitrarily reaches every tree, so both architectures reach exactly the same set of
trees; the honest question is cost and soundness.  Three things are then measured rather than
asserted:

1. **the 25 worlds accept exactly the same string language.**  Every grammar in the Generation 1
   registry accepts ``primary (operator primary)*`` with parentheses; only the tree differs.
   :func:`language_identity_audit` checks acceptance and rejection over the corpus and a declared
   set of malformed strings;
2. **the conversion carries an obligation, and it is a real one.**  A conversion driven by the
   conventional parse *tree alone* is **unsound**: the tree does not record which sub-expressions
   were explicitly bracketed, and without that the rewrite cannot tell ``(a + b) * c`` from
   ``a + b * c``.  :func:`convert_bracket_blind` is that conversion, it is in the module for exactly
   this reason, and :func:`agreement_audit` measures how many corpus cells it gets wrong;
3. **the sound conversion needs a front end that is more than the conventional parser** - it must
   preserve the bracket structure (:func:`parse_marked`).  Having preserved it, the conversion then
   discards everything else the front end computed: :func:`convert` reads only the token order and
   the bracket boundaries.  The conventional parse's shaping work is thrown away.

Thesis T31 (reachability outranks cost) therefore does **not** separate these two architectures:
they reach the same trees from the same strings, so the criterion falls through to cost, which is
what questions 2, 3 and 4 measure.  Experiments 0043 and 0028 are about which trees a *convention*
can reach cheaply; nothing there distinguishes a native reader of a convention from a converted one.

Agreement is the first gate
---------------------------

Native, table-driven and parse-then-convert must produce **byte-identical serialised trees** on the
whole corpus in all 25 worlds, and that is checked before any timing is believed
(:func:`agreement_audit`, comparing ``json.dumps(ast_to_dict(tree), sort_keys=True)``).

Every decisive predicate here carries a negative control that breaks the thing and asserts the gate
reports failure, **through the same path the published number takes**:

.. code-block:: text

    emit_native_source(..., sabotage="reverse_levels")   a native machine for the wrong world
    emit_native_source(..., sabotage="flatten")          a native machine with one level collapsed
    convert_bracket_blind                                 the unsound conversion
    operation_invariance(..., sabotage=True)              a fabricated non-invariant reading
    distinct_graph_table(..., sabotage=True)              an under-counted support, so the T6 bound
                                                          check has a violation it must catch
    identical_multisets(..., sabotage=...)                the instruction comparison, made to differ
    language_identity_audit(..., malformed=...)           a well-formed string offered as malformed

The sabotage arguments exist **only** so the gates can be shown to fire.  Nothing in the reported
numbers uses them.

A bound is not a finding either, and the same discipline applies to it: :func:`bound_attainment`
searches the whole finite space of four-operator words at each declared length rather than citing
``s!``, so "the corpus falls short of the bound" and "the bound is attainable" are separate,
separately measured statements.

What is imported and never restated
-----------------------------------

* the table-driven machine is :func:`parseatlas.parser.parse`, unmodified - it is the baseline and
  this card does not get to tune it;
* the 25 worlds are :func:`parseatlas.grammar.all_grammars`;
* the corpus is 0034's named-law corpus, :data:`parseatlas.notational_cost.CORPUS`, imported whole,
  plus a declared generated family for the length sweep and the T6 enumeration;
* the three structural measures are the cards that own them - operation count from
  :func:`parseatlas.canonical.operation_cost` (0021), critical-path depth from
  :func:`parseatlas.parallel_worlds.depth` (0041), peak live values from
  :func:`parseatlas.memory_ceiling.peak_live` (0044).  None is re-implemented here;
* the T6 operator support is :func:`parseatlas.support_reduction.operator_support` (0019).

**The C emission and the instruction counting follow the method of experiment 0053 and deliberately
do not import it.**  Card 0053 is being edited concurrently with this one; a live import would make
this card's numbers depend on another card's in-flight edits.  The technique is 0053's - one
operation per statement into a named ``double`` temporary so the C source is a transcript of the
dataflow graph rather than something a C compiler's own precedence has to rebuild, then ``clang -S``
read back and the mnemonics inside each function counted - and the duplication is declared here
rather than hidden.

Timing discipline, inherited from 0053's rejection
---------------------------------------------------

0053 was returned once for publishing a timing as a single reading.  So: **every timing figure in
this module is a range over repeated runs**, generation cost is reported on its own and never folded
into a rate, and every rate carries its denominator.  Timing runs are strictly sequential; the
multicore decision applies to the structural sweep and to compilation, and it is made from a
measurement recorded in :func:`parallel_decision`.
"""

from __future__ import annotations

import itertools
import json
import math
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .canonical import ast_to_dict, operation_cost
from .grammar import OPERATORS, Grammar, all_grammars, control_grammar
from .memory_ceiling import peak_live  # 0044: Sethi-Ullman simultaneously live values
from .notational_cost import CORPUS as LAW_CORPUS  # 0034: the named-law corpus, imported whole
from .parallel_worlds import depth  # 0041: critical path, a leaf at 0
from .parser import Binary, Node, Number, Variable, parse
from .support_reduction import operator_support  # 0019 / T6
from .tokenizer import Token, tokenize

__all__ = [
    "ARCHITECTURES",
    "CLANG_LEVELS",
    "CONTROL",
    "DEFAULT_PASSES",
    "DEFAULT_REPEATS",
    "Entry",
    "Group",
    "MALFORMED",
    "NativeMachine",
    "ALL_VARIANTS",
    "NATIVE_VARIANTS",
    "OPERATION_KEYS",
    "OPERATOR_ALPHABET",
    "SWEEP_LENGTHS",
    "SWEEP_SUPPORTS",
    "TABLE_VARIANT",
    "Timing",
    "WORKER_HEADROOM_CORES",
    "agreement_audit",
    "architecture_callables",
    "break_even_executions",
    "bound_attainment",
    "break_even_from_ratio",
    "build_native",
    "clang_available",
    "convert",
    "convert_bracket_blind",
    "corpus",
    "dataflow_table",
    "default_worker_count",
    "distinct_graph_table",
    "emit_c_function",
    "emit_native_source",
    "environment",
    "generation_cost",
    "marginal_generation_cost",
    "graph_profile",
    "identical_multisets",
    "instruction_table",
    "language_identity_audit",
    "length_curve",
    "long_word_check",
    "machine_isomorphism_audit",
    "measure_rate",
    "paired_ratio",
    "named_corpus",
    "noise_floor",
    "native_machines_report",
    "operation_invariance",
    "parallel_decision",
    "parse_marked",
    "parse_then_convert",
    "registry_generation_cost",
    "serialise",
    "sharpest_objects",
    "specialisation_control",
    "sweep_corpus",
    "sweep_word",
    "throughput_repeatability",
    "tokenizer_share",
    "throughput_table",
    "worker_count_for",
]


CONTROL: Grammar = control_grammar()

#: The four operators of the Generation 1 language, in the registry's own order.  Named here so
#: the exhaustive enumeration in :func:`bound_attainment` searches the alphabet the worlds are
#: built over and not a hand-typed copy of it.
OPERATOR_ALPHABET: tuple[str, ...] = OPERATORS

#: The keys of :func:`parseatlas.canonical.operation_cost` that count issued arithmetic.
OPERATION_KEYS: tuple[str, ...] = ("add", "sub", "mul", "div")

#: The two native variants.  Both are emitted for every world and both are measured; see the module
#: docstring for why publishing one would have made the result an artifact of the emitter.
NATIVE_VARIANTS: tuple[str, ...] = ("levels", "climb")

#: The table-driven variant emitted by the SAME generator, and the reason it exists.
#:
#: ``lookup`` is the code the native ``climb`` machine would be if its constants were put back: the
#: same functions, the same call protocol, the same index passing, differing only in that the
#: binding power comes from a dictionary at run time (``POWERS[token.value]``) instead of being a
#: literal.  It is the strict control for the specialisation question, because with everything else
#: held byte-identical the difference between ``climb`` and ``lookup`` is partial evaluation and
#: nothing else.
#:
#: Its source is **world-independent** - the world enters only as the injected ``POWERS`` table - so
#: one compilation serves the whole registry, and each world costs one dictionary.  That asymmetry
#: is the architectural trade the break-even prices, and it is measured in
#: :func:`registry_generation_cost` rather than assumed.
TABLE_VARIANT: str = "lookup"

#: Every variant the generator emits.
ALL_VARIANTS: tuple[str, ...] = NATIVE_VARIANTS + (TABLE_VARIANT,)

#: The architectures compared, in the order the tables print them.
#:
#: ``table`` is :func:`parseatlas.parser.parse` exactly as the project ships it, which rebuilds its
#: binding-power dictionary on every call.  ``table_lookup`` is the generated ``lookup`` variant: the
#: strongest form of the architecture the owner is rejecting - a lookup table paid for once and
#: consulted at run time - in code shape identical to the native machine's.  Both are reported, and
#: the headline is stated against ``table_lookup``, because a native machine that only beat the
#: shipped parser would have been measuring a dictionary comprehension rather than an architecture.
ARCHITECTURES: tuple[str, ...] = (
    "native_levels",
    "native_climb",
    "table",
    "table_lookup",
    "convert",
)

#: Repeats of every timed block, and passes over the corpus inside one block.
#:
#: Both are declared here and both are swept rather than trusted: :func:`length_curve` varies the
#: work per pass by two orders of magnitude and every cell reports its own range, so a reader can
#: see whether a figure was still moving.  Nine repeats is what makes a min-median-max band
#: meaningful; a single reading is never published, and :func:`throughput_repeatability` re-runs the
#: whole table so the headline itself carries a range and not one reading of it.
DEFAULT_REPEATS: int = 9
DEFAULT_PASSES: int = 20

#: Cores held back so a sweep cannot starve the interactive session.
WORKER_HEADROOM_CORES: int = 2

#: Operand counts swept by :func:`length_curve` and :func:`sweep_corpus`.
#:
#: The range spans a two-token expression to a 128-operand one, which is far past anything in the
#: named corpus (whose widest entry has 9 operands).  Nothing is declared to be the interesting
#: length; the curve is published and read.
SWEEP_LENGTHS: tuple[int, ...] = (2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128)

#: Operator supports swept for the T6 bound.  Sizes 1, 2, 3 and 4, so the bound ``|support|!`` takes
#: the values 1, 2, 6 and 24 and the enumeration can be checked against all four.
SWEEP_SUPPORTS: tuple[tuple[str, ...], ...] = (
    ("+",),
    ("+", "*"),
    ("+", "-", "*"),
    ("+", "-", "*", "/"),
)

#: Strings no world may accept.  They exist so that :func:`language_identity_audit` checks agreement
#: in the rejecting direction too; an audit that only ever asks the question in the direction of its
#: expected answer is not evidence.
MALFORMED: tuple[str, ...] = (
    "",
    "a +",
    "* b",
    "(a + b",
    "a + b)",
    "a + + b",
    "a b",
    ")",
    "()",
    "a * (b + )",
)

#: The two optimisation levels the card names for the metal question.  ``-ffast-math`` is out of
#: scope and the reason is in the report's limits: it lets the compiler reassociate, and reassociation
#: is precisely the difference between the 25 worlds' readings, so measuring under it would be asking
#: whether the compiler can undo the conventions rather than what the conventions cost.
CLANG_LEVELS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("O0", ("-O0",)),
    ("O2", ("-O2",)),
)


# --------------------------------------------------------------------------------- the corpus


@dataclass(frozen=True)
class Entry:
    """One corpus string: a name, the family it came from, and the token word itself."""

    name: str
    family: str
    source: str


def named_corpus() -> tuple[Entry, ...]:
    """0034's named-law corpus, imported whole and not re-selected here.

    Fifty-eight formulas of real mathematics, each a string a mathematician would write.  They carry
    parentheses, which is what makes the conversion obligation of question 1 a live one rather than
    a hypothetical.
    """
    return tuple(
        Entry(formula.name, f"named:{formula.area}", formula.source) for formula in LAW_CORPUS
    )


def sweep_word(operand_count: int, support: Sequence[str]) -> str:
    """A word of ``operand_count`` distinct variables joined by ``support`` cycled in order.

    Deterministic, and the operator sequence is a cycle rather than a sample, so the word is a
    function of its two parameters and no seed enters this module.
    """
    if operand_count < 1:
        raise ValueError("operand_count must be at least 1")
    if not support:
        raise ValueError("support must not be empty")
    parts = ["v0"]
    for index in range(operand_count - 1):
        parts.append(support[index % len(support)])
        parts.append(f"v{index + 1}")
    return " ".join(parts)


def sweep_corpus(
    lengths: Sequence[int] = SWEEP_LENGTHS,
    supports: Sequence[Sequence[str]] = SWEEP_SUPPORTS,
) -> tuple[Entry, ...]:
    """The generated family: one word per (length, support), all of them parenthesis-free."""
    entries = []
    for support in supports:
        tag = "".join(support)
        for length in lengths:
            entries.append(
                Entry(f"sweep_{tag}_{length:03d}", f"sweep:{tag}", sweep_word(length, support))
            )
    return tuple(entries)


def corpus() -> tuple[Entry, ...]:
    """The whole corpus: the named laws first, then the generated sweep family."""
    return named_corpus() + sweep_corpus()


# ------------------------------------------------------------- architecture 1: native machines


_PRIMARY_TEMPLATE = '''\
def _primary(tokens, index):
    token = tokens[index]
    kind = token.kind
    if kind == "name":
        return Variable(token.value), index + 1
    if kind == "number":
        text = token.value
        if "/" in text:
            numerator, denominator = text.split("/", 1)
            return Number(Fraction(int(numerator), int(denominator))), index + 1
        return Number(Fraction(int(text))), index + 1
    if kind == "left":
        node, index = {entry}(tokens, index + 1)
        if tokens[index].kind != "right":
            raise ValueError("Expected closing parenthesis")
        return node, index + 1
    raise ValueError("Expected number, variable, or parenthesized expression; got "
                     + repr(token.value))
'''


#: The control machine's loop: the specialised ``climb`` loop with its constants put back into a
#: dictionary.  Identical in every world, which is the point.
_LOOKUP_TEMPLATE = '''\
def _expression(tokens, index, minimum_power):
    left, index = _primary(tokens, index)
    while True:
        token = tokens[index]
        if token.kind != "operator":
            return left, index
        value = token.value
        power = POWERS[value]
        if power < minimum_power:
            return left, index
        right, index = _expression(tokens, index + 1, power + 1)
        left = Binary(value, left, right)
'''


def _sabotaged_grammar(grammar: Grammar, sabotage: str | None) -> Grammar:
    """The world a sabotaged architecture is really built for.  Negative controls only."""
    if sabotage is None:
        return grammar
    levels = _sabotaged_levels(grammar.levels, sabotage)
    return Grammar(
        grammar.id,
        tuple(operator for group in levels for operator in group),
        levels,
    )


def _sabotaged_levels(levels: tuple[tuple[str, ...], ...], sabotage: str | None) -> tuple[tuple[str, ...], ...]:
    """The level structure a sabotaged emitter uses.  See the module docstring: controls only."""
    if sabotage is None:
        return levels
    if sabotage == "reverse_levels":
        return tuple(reversed(levels))
    if sabotage == "flatten":
        return (tuple(operator for group in levels for operator in group),)
    raise ValueError(f"unknown sabotage: {sabotage!r}")


def emit_native_source(
    grammar: Grammar,
    variant: str = "levels",
    *,
    symbolic: bool = False,
    sabotage: str | None = None,
) -> str:
    """The Python source of a machine for ``grammar``, emitted by one generator for all 25 worlds.

    Three variants, two of them specialised and one of them the control:

    ``levels``
        one function per precedence level.  No ``Grammar`` object, no dictionary, and the binding
        powers do not appear at all - they have become the call structure.
    ``climb``
        the table-driven loop with its lookup partially evaluated away: one recursive function, the
        operator literals and the integer powers all constants of the code.
    ``lookup``
        the same single recursive function with the powers read from an injected ``POWERS``
        dictionary at run time.  Its source contains **no world-specific text at all**, so one
        compilation serves the whole registry; this is the architecture the owner is rejecting, in
        code shape identical to ``climb``, which is what makes their difference pure specialisation
        and nothing else.

    The emission is a deterministic function of ``(grammar, variant)``; a test pins that.

    ``sabotage`` builds a machine for a world other than the one it will be compared against.  It
    exists only so the agreement gate can be shown to fire, and no reported number uses it.
    """
    if variant not in ALL_VARIANTS:
        raise ValueError(f"unknown variant: {variant!r}")
    levels = _sabotaged_levels(grammar.levels, sabotage)
    literals = {}
    for level_index, group in enumerate(levels):
        for slot, operator in enumerate(group):
            literals[operator] = f'"<L{level_index}.{slot}>"' if symbolic else json.dumps(operator)

    if variant == "levels":
        entry = f"_level_{len(levels) - 1}"
        blocks = [_PRIMARY_TEMPLATE.format(entry=entry)]
        for level_index, group in enumerate(levels):
            operand = "_primary" if level_index == 0 else f"_level_{level_index - 1}"
            lines = [f"def _level_{level_index}(tokens, index):"]
            lines.append(f"    left, index = {operand}(tokens, index)")
            lines.append("    while True:")
            lines.append("        token = tokens[index]")
            lines.append('        if token.kind != "operator":')
            lines.append("            return left, index")
            lines.append("        value = token.value")
            keyword = "if"
            for operator in group:
                literal = literals[operator]
                lines.append(f"        {keyword} value == {literal}:")
                lines.append(f"            right, index = {operand}(tokens, index + 1)")
                lines.append(f"            left = Binary({literal}, left, right)")
                keyword = "elif"
            lines.append("        else:")
            lines.append("            return left, index")
            blocks.append("\n".join(lines) + "\n")
    elif variant == TABLE_VARIANT:
        entry = "_expression"
        blocks = [_PRIMARY_TEMPLATE.format(entry="_lowest")]
        blocks.append(_LOOKUP_TEMPLATE)
        blocks.append("def _lowest(tokens, index):\n    return _expression(tokens, index, 0)\n")
    else:
        entry = "_expression"
        blocks = [_PRIMARY_TEMPLATE.format(entry="_lowest")]
        power_of = {
            operator: len(levels) - level_index
            for level_index, group in enumerate(levels)
            for operator in group
        }
        lines = ["def _expression(tokens, index, minimum_power):"]
        lines.append("    left, index = _primary(tokens, index)")
        lines.append("    while True:")
        lines.append("        token = tokens[index]")
        lines.append('        if token.kind != "operator":')
        lines.append("            return left, index")
        lines.append("        value = token.value")
        keyword = "if"
        for group in levels:
            for operator in group:
                literal = literals[operator]
                power = power_of[operator]
                lines.append(f"        {keyword} value == {literal}:")
                lines.append(f"            if {power} < minimum_power:")
                lines.append("                return left, index")
                lines.append(f"            right, index = _expression(tokens, index + 1, {power + 1})")
                lines.append(f"            left = Binary({literal}, left, right)")
                keyword = "elif"
        lines.append("        else:")
        lines.append("            return left, index")
        blocks.append("\n".join(lines) + "\n")
        blocks.append("def _lowest(tokens, index):\n    return _expression(tokens, index, 0)\n")

    tail = [
        "def parse_tokens(tokens):",
        f"    node, index = {entry}(tokens, 0)" if variant == "levels" else "    node, index = _expression(tokens, 0, 0)",
        "    token = tokens[index]",
        '    if token.kind != "eof":',
        '        raise ValueError("Unexpected token: " + repr(token.value))',
        "    return node",
        "",
        "def parse_source(source):",
        "    return parse_tokens(tokenize(source))",
        "",
    ]
    # Under ``symbolic`` the header carries no world name, because the point of the normalisation is
    # to ask whether two worlds' machines are the same program; a comment naming the world would
    # answer no for a reason that is not code.
    header = (
        f"# machine, variant {variant}, normalised\n"
        if symbolic or variant == TABLE_VARIANT
        else f"# native machine for {grammar.id}, variant {variant}, generated by parseatlas.native_machines\n"
    )
    return header + "\n".join(blocks) + "\n" + "\n".join(tail)


@dataclass(frozen=True)
class NativeMachine:
    """One compiled native machine and the cost of having produced it."""

    grammar_id: str
    variant: str
    source: str
    parse_source: Callable[[str], Node]
    parse_tokens: Callable[[tuple[Token, ...]], Node]
    generation_seconds: float


def build_native(
    grammar: Grammar,
    variant: str = "levels",
    *,
    sabotage: str | None = None,
    code: Any = None,
) -> NativeMachine:
    """Emit, compile and execute one machine, timing the whole generation.

    The generation cost is ``emit -> compile() -> exec()``, measured end to end and reported on its
    own line.  It is paid **once**; the returned callables are then executed as many times as the
    caller likes, which is the whole point of the architecture and the reason the break-even is
    stated in executions.

    The machine's globals are pre-populated with the node constructors, ``Fraction`` and the shared
    tokenizer, so the emitted source contains no import statements and the measured generation cost
    is the cost of the parser code and nothing else.  For the ``lookup`` control the binding-power
    table is injected as ``POWERS``: that table, and nothing else, is what makes it a machine for
    this world rather than for another.

    ``code`` accepts an already emitted-and-compiled ``(source, code object)`` pair.  It exists for
    the ``lookup`` control, whose source is world-independent and therefore emitted and compiled once
    for the whole registry; passing it is what makes :func:`registry_generation_cost` able to charge
    that architecture honestly instead of billing it twenty-five compilations it does not perform.
    """
    started = time.perf_counter()
    if code is None:
        source = emit_native_source(grammar, variant, sabotage=sabotage)
        code = compile(source, f"<native {grammar.id} {variant}>", "exec")
    else:
        source, code = code
    namespace: dict[str, Any] = {
        "Binary": Binary,
        "Number": Number,
        "Variable": Variable,
        "Fraction": Fraction,
        "tokenize": tokenize,
    }
    if variant == TABLE_VARIANT:
        namespace["POWERS"] = _powers_of(_sabotaged_grammar(grammar, sabotage))
    exec(code, namespace)
    elapsed = time.perf_counter() - started
    return NativeMachine(
        grammar_id=grammar.id,
        variant=variant,
        source=source,
        parse_source=namespace["parse_source"],
        parse_tokens=namespace["parse_tokens"],
        generation_seconds=elapsed,
    )


# ------------------------------------------------ architecture 2: one machine plus a conversion


@dataclass(frozen=True)
class Group:
    """An explicitly bracketed sub-expression, kept as a mark by the conversion's front end.

    The conventional parser throws this away - ``(a + b) * c`` and ``a + b * c`` produce the same
    tree under ``G0`` - and a conversion driven by that tree alone therefore cannot be sound.  The
    mark is what makes :func:`convert` correct, and its absence is what
    :func:`convert_bracket_blind` demonstrates.
    """

    inner: Any


def parse_marked(source: str, grammar: Grammar = CONTROL) -> Any:
    """The conventional parse, with every explicitly bracketed sub-expression wrapped in a mark.

    This is the front end of the conversion architecture.  It is deliberately **not**
    :func:`parseatlas.parser.parse`: the conversion needs strictly more than the conventional parser
    produces, and that extra requirement is one of this card's three answers to the capability
    question.
    """
    tokens = tokenize(source)
    powers = {
        operator: len(grammar.levels) - level
        for level, group in enumerate(grammar.levels)
        for operator in group
    }
    index = 0

    def primary() -> Any:
        nonlocal index
        token = tokens[index]
        index += 1
        if token.kind == "number":
            if "/" in token.value:
                numerator, denominator = token.value.split("/", 1)
                return Number(Fraction(int(numerator), int(denominator)))
            return Number(Fraction(int(token.value)))
        if token.kind == "name":
            return Variable(token.value)
        if token.kind == "left":
            inner = expression(0)
            if tokens[index].kind != "right":
                raise ValueError("Expected closing parenthesis")
            index += 1
            return Group(inner)
        raise ValueError(
            f"Expected number, variable, or parenthesized expression; got {token.value!r}"
        )

    def expression(minimum_power: int) -> Any:
        nonlocal index
        left = primary()
        while tokens[index].kind == "operator" and powers[tokens[index].value] >= minimum_power:
            operator = tokens[index].value
            index += 1
            left = Binary(operator, left, expression(powers[operator] + 1))
        return left

    result = expression(0)
    if tokens[index].kind != "eof":
        raise ValueError(f"Unexpected token: {tokens[index].value!r}")
    return result


def _shape(operands: list[Node], operators: list[str], powers: dict[str, int]) -> Node:
    """Rebuild a flat operand/operator sequence into the tree ``powers`` dictates."""
    position = 0

    def expression(minimum_power: int) -> Node:
        nonlocal position
        left = operands[position]
        position += 1
        while position <= len(operators):
            operator = operators[position - 1]
            power = powers[operator]
            if power < minimum_power:
                return left
            right = expression(power + 1)
            left = Binary(operator, left, right)
        return left

    return expression(0)


def _powers_of(grammar: Grammar) -> dict[str, int]:
    return {
        operator: len(grammar.levels) - level
        for level, group in enumerate(grammar.levels)
        for operator in group
    }


def convert(marked: Any, grammar: Grammar) -> Node:
    """Rewrite a bracket-marked conventional parse into the tree ``grammar`` would have read.

    The rewrite flattens each maximal unbracketed region into its operand and operator sequences,
    recurses into every mark, and reshapes by ``grammar``'s binding powers.

    **Note what it reads and what it ignores.**  It reads the token order and the bracket
    boundaries.  It ignores the shape the front end computed, entirely.  The conventional parse's
    work of deciding that ``a + b * c`` groups as ``a + (b * c)`` is thrown away by the flatten, and
    that is a property of the architecture rather than of this implementation: any sound conversion
    must be free to re-associate every unbracketed region, so it cannot inherit the front end's
    associations.
    """
    powers = _powers_of(grammar)
    operands: list[Node] = []
    operators: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, Group):
            operands.append(convert(node.inner, grammar))
        elif isinstance(node, Binary):
            walk(node.left)
            operators.append(node.operator)
            walk(node.right)
        else:
            operands.append(node)

    walk(marked)
    return _shape(operands, operators, powers)


def parse_then_convert(source: str, grammar: Grammar) -> Node:
    """The conversion architecture end to end: conventional front end, then the rewrite."""
    return convert(parse_marked(source), grammar)


def convert_bracket_blind(source: str, grammar: Grammar) -> Node:
    """The unsound conversion: the conventional parse **tree** alone, with no bracket marks.

    This is the architecture as it is usually imagined - parse once with the conventional grammar,
    then rewrite the tree - and it is wrong, because the tree does not record which sub-expressions
    were bracketed.  It is here as the negative control for the soundness gate and for no other
    reason; :func:`agreement_audit` counts the cells it gets wrong.
    """
    tree = parse(source, CONTROL)
    powers = _powers_of(grammar)
    operands: list[Node] = []
    operators: list[str] = []

    def walk(node: Node) -> None:
        if isinstance(node, Binary):
            walk(node.left)
            operators.append(node.operator)
            walk(node.right)
        else:
            operands.append(node)

    walk(tree)
    return _shape(operands, operators, powers)


# ------------------------------------------------------------------------------ agreement gate


def serialise(tree: Node) -> str:
    """The byte string two architectures must agree on: 0021's AST dictionary, key-sorted JSON."""
    return json.dumps(ast_to_dict(tree), sort_keys=True)


def architecture_callables(
    grammar: Grammar,
    *,
    sabotage: str | None = None,
    blind_conversion: bool = False,
) -> dict[str, Callable[[str], Node]]:
    """One callable per architecture, all taking a source string and returning a tree.

    ``sabotage`` and ``blind_conversion`` are the negative-control switches.  They are arguments of
    this function, and not of a separate test-only helper, precisely so that a control goes through
    the identical path the published numbers take.
    """
    levels_machine = build_native(grammar, "levels", sabotage=sabotage)
    climb_machine = build_native(grammar, "climb", sabotage=sabotage)
    lookup_machine = build_native(grammar, TABLE_VARIANT, sabotage=sabotage)
    conversion = convert_bracket_blind if blind_conversion else parse_then_convert
    return {
        "native_levels": levels_machine.parse_source,
        "native_climb": climb_machine.parse_source,
        "table": lambda source, grammar=grammar: parse(source, grammar),
        "table_lookup": lookup_machine.parse_source,
        "convert": lambda source, grammar=grammar: conversion(source, grammar),
    }


def agreement_audit(
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    *,
    sabotage: str | None = None,
    blind_conversion: bool = False,
) -> dict[str, Any]:
    """Do the architectures read every string into the same tree, in every world?

    The reference is the table-driven parser, which is the machine the project has always used and
    the one this card does not get to tune.  Every other architecture must produce a **byte-identical
    serialised tree** for every ``(world, string)`` cell.

    Returns per-architecture mismatch counts, the mismatching cells themselves (capped so a broken
    run stays readable, with the true total beside the sample), and ``all_match``.  If any cell
    disagrees, that is the finding and the caller must stop.
    """
    entries = tuple(entries) if entries is not None else corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    mismatches: dict[str, list[dict[str, str]]] = {name: [] for name in ARCHITECTURES if name != "table"}
    counts: dict[str, int] = {name: 0 for name in mismatches}
    worlds: dict[str, set[str]] = {name: set() for name in mismatches}
    cells = 0
    for grammar in grammars:
        callables = architecture_callables(
            grammar, sabotage=sabotage, blind_conversion=blind_conversion
        )
        reference = callables["table"]
        for entry in entries:
            expected = serialise(reference(entry.source))
            for name in mismatches:
                cells += 1
                try:
                    produced = serialise(callables[name](entry.source))
                except Exception as error:  # a machine that refuses a string it must accept
                    produced = f"<raised {type(error).__name__}: {error}>"
                if produced != expected:
                    counts[name] += 1
                    worlds[name].add(grammar.id)
                    if len(mismatches[name]) < 12:
                        mismatches[name].append(
                            {
                                "grammar": grammar.id,
                                "entry": entry.name,
                                "source": entry.source,
                                "expected": expected,
                                "produced": produced,
                            }
                        )
    total = sum(counts.values())
    return {
        "entries": len(entries),
        "grammars": len(grammars),
        "cells": cells,
        "cells_per_architecture": len(entries) * len(grammars),
        "mismatch_counts": counts,
        "mismatch_total": total,
        "mismatch_sample": mismatches,
        "worlds_with_mismatch": {name: len(worlds[name]) for name in mismatches},
        "all_match": total == 0,
        "sabotage": sabotage,
        "blind_conversion": blind_conversion,
    }


def language_identity_audit(
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    malformed: Sequence[str] = MALFORMED,
) -> dict[str, Any]:
    """Do the 25 worlds accept and reject exactly the same strings?

    This is the capability question at the level of the *language*, and it is measured rather than
    argued.  Every grammar in the Generation 1 registry describes the same set of strings - only the
    tree differs - so a world cannot express a string another world cannot read.  The audit checks
    both directions, because an audit that only asks in the direction of its expected answer is not
    evidence: the well-formed corpus must be accepted by all 25 native machines, and every declared
    malformed string must be rejected by all 25.
    """
    entries = tuple(entries) if entries is not None else corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    accept_failures = []
    reject_failures = []
    for grammar in grammars:
        machine = build_native(grammar, "levels")
        for entry in entries:
            try:
                machine.parse_source(entry.source)
            except Exception as error:
                accept_failures.append(
                    {"grammar": grammar.id, "entry": entry.name, "error": f"{type(error).__name__}: {error}"}
                )
        for text in malformed:
            try:
                machine.parse_source(text)
            except ValueError:
                continue
            except Exception as error:  # rejected, but not the declared way
                reject_failures.append(
                    {"grammar": grammar.id, "source": text, "error": type(error).__name__}
                )
                continue
            reject_failures.append({"grammar": grammar.id, "source": text, "error": "accepted"})
    return {
        "grammars": len(grammars),
        "accepted_checks": len(grammars) * len(entries),
        "rejected_checks": len(grammars) * len(malformed),
        "accept_failures": accept_failures,
        "reject_failures": reject_failures,
        "same_language": not accept_failures and not reject_failures,
    }


def machine_isomorphism_audit(
    grammars: Sequence[Grammar] | None = None,
    variants: Sequence[str] = ALL_VARIANTS,
) -> dict[str, Any]:
    """Are the emitted machines the same program with four symbols permuted?

    This is the structural half of the null model and it is stronger than any ratio.  Each machine
    is emitted **symbolically**: every operator literal is replaced by its ``(level, slot)``
    position.  Two worlds whose normalised sources are byte-identical differ only in *which symbol
    sits at which level* - there is no per-world code for a per-world speed difference to come from,
    and any spread across those worlds belongs to the corpus's operator mix.

    ``G0`` is expected to stand apart, and the reason is not an ordering: it is the only world in the
    registry with **tied** levels, so its machine has two levels where the strict worlds have four.
    That is reported, not hidden.
    """
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    report: dict[str, Any] = {"variants": {}}
    for variant in variants:
        classes: dict[str, list[str]] = {}
        for grammar in grammars:
            source = emit_native_source(grammar, variant, symbolic=True)
            classes.setdefault(source, []).append(grammar.id)
        groups = sorted(classes.values(), key=lambda members: (-len(members), members[0]))
        strict = [grammar.id for grammar in grammars if grammar.id != "G0"]
        strict_class = [members for members in groups if set(strict) <= set(members)]
        report["variants"][variant] = {
            "distinct_normalised_sources": len(groups),
            "classes": [{"size": len(members), "members": members} for members in groups],
            "strict_worlds_identical": bool(strict_class),
            "levels_by_world": {grammar.id: len(grammar.levels) for grammar in grammars},
            "source_lengths": {
                grammar.id: len(emit_native_source(grammar, variant)) for grammar in grammars
            },
        }
    return report


# ---------------------------------------------------------------------------------- throughput


@dataclass(frozen=True)
class Timing:
    """A timed quantity as a range over repeated runs.  A single reading is never published."""

    minimum: float
    median: float
    maximum: float
    repeats: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "minimum": self.minimum,
            "median": self.median,
            "maximum": self.maximum,
            "repeats": self.repeats,
        }


def _timing(seconds: Sequence[float]) -> Timing:
    values = sorted(seconds)
    return Timing(values[0], statistics.median(values), values[-1], len(values))


def measure_rate(
    call: Callable[[str], Node],
    sources: Sequence[str],
    *,
    repeats: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
) -> dict[str, Any]:
    """Seconds per string and strings per second, as a range over ``repeats`` timed blocks.

    Every rate carries its denominator: ``parses_per_block = passes * len(sources)`` is returned
    beside the figure.  The result of every parse is consumed by a branch that raises if it is
    ``None``, identically in every architecture, so no architecture is credited with work it did not
    do.

    Timed blocks are run one after another and never in parallel; concurrent load moves clock
    frequency and cache occupancy, which would change what is measured rather than how fast it is
    measured.
    """
    sources = tuple(sources)
    per_block = passes * len(sources)
    seconds: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        for _ in range(passes):
            for source in sources:
                if call(source) is None:
                    raise RuntimeError("a machine returned no tree")
        seconds.append(time.perf_counter() - started)
    block = _timing(seconds)
    return {
        "parses_per_block": per_block,
        "block_seconds": block.as_dict(),
        "seconds_per_parse": {
            "minimum": block.minimum / per_block,
            "median": block.median / per_block,
            "maximum": block.maximum / per_block,
            "repeats": block.repeats,
        },
        "parses_per_second": {
            "minimum": per_block / block.maximum,
            "median": per_block / block.median,
            "maximum": per_block / block.minimum,
            "repeats": block.repeats,
        },
    }


def _time_block(call: Callable[[Any], Any], payloads: Sequence[Any], passes: int) -> float:
    started = time.perf_counter()
    for _ in range(passes):
        for payload in payloads:
            if call(payload) is None:
                raise RuntimeError("a machine returned no tree")
    return time.perf_counter() - started


def paired_ratio(
    baseline: Callable[[Any], Any],
    candidate: Callable[[Any], Any],
    payloads: Sequence[Any],
    *,
    rounds: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
) -> dict[str, Any]:
    """How many times faster ``candidate`` is than ``baseline``, measured **in an ABBA design**.

    The first revision of this card compared two independently measured medians, and the effect it
    was looking for turned out to be the same size as the drift between one measurement and the
    next: the noise floor moved from ``1.7%`` to ``5.1%`` between two runs of the identical
    instrument, which is enough to reverse a ``4%`` result.

    So each round times **baseline, candidate, candidate, baseline** back to back and takes the ratio
    of the two averaged halves.  Any drift that is linear over the round - a clock-frequency step, a
    background process starting - enters both halves equally and cancels.  What is reported is the
    range of the per-round ratios, never one number: a quantity whose rounds disagree is reported as
    disagreeing.

    The same instrument measures the floor: :func:`noise_floor` passes it two byte-identical
    machines, whose true ratio is exactly ``1``, so whatever spread it returns there is what this
    harness cannot resolve.
    """
    ratios = []
    for _ in range(rounds):
        first_baseline = _time_block(baseline, payloads, passes)
        first_candidate = _time_block(candidate, payloads, passes)
        second_candidate = _time_block(candidate, payloads, passes)
        second_baseline = _time_block(baseline, payloads, passes)
        base = (first_baseline + second_baseline) / 2
        cand = (first_candidate + second_candidate) / 2
        ratios.append(base / cand)
    ordered = sorted(ratios)
    return {
        "rounds": rounds,
        "passes": passes,
        "payloads": len(payloads),
        "parses_per_block": passes * len(payloads),
        "minimum": ordered[0],
        "median": statistics.median(ordered),
        "maximum": ordered[-1],
        "spread": ordered[-1] - ordered[0],
        "ratios": ratios,
    }


def generation_cost(
    grammar: Grammar,
    variant: str = "levels",
    *,
    repeats: int = DEFAULT_REPEATS,
) -> dict[str, Any]:
    """The one-off cost of producing a native machine, reported on its own and never in a rate.

    ``emit -> compile() -> exec()``, timed end to end, as a range over ``repeats`` builds.
    """
    seconds = [build_native(grammar, variant).generation_seconds for _ in range(repeats)]
    timing = _timing(seconds)
    return {"grammar": grammar.id, "variant": variant, "seconds": timing.as_dict()}


def marginal_generation_cost(
    grammar: Grammar,
    variant: str = "levels",
    *,
    repeats: int = DEFAULT_REPEATS,
) -> dict[str, Any]:
    """What it costs to add **one more world** under this architecture, with sharing taken into account.

    The two architectures do not amortise the same way, and charging them as though they did would
    decide the break-even before it was measured:

    * a native machine's source is different in every world, so nothing can be shared and the
      marginal cost is the whole ``emit -> compile() -> exec()``;
    * the ``lookup`` control's source is **identical in every world** - the world enters only as the
      injected ``POWERS`` table - so the compilation is done once for the whole registry and the
      marginal cost is binding the table into a fresh namespace.

    The compilation the control does not repeat is therefore taken outside the timer here, and paid
    once in :func:`registry_generation_cost`.
    """
    if variant != TABLE_VARIANT:
        return generation_cost(grammar, variant, repeats=repeats)
    source = emit_native_source(grammar, variant)
    code = compile(source, "<lookup shared>", "exec")
    seconds = []
    for _ in range(repeats):
        started = time.perf_counter()
        namespace: dict[str, Any] = {
            "Binary": Binary,
            "Number": Number,
            "Variable": Variable,
            "Fraction": Fraction,
            "tokenize": tokenize,
            "POWERS": _powers_of(grammar),
        }
        exec(code, namespace)
        seconds.append(time.perf_counter() - started)
    return {"grammar": grammar.id, "variant": variant, "seconds": _timing(seconds).as_dict()}


def break_even_from_ratio(
    generation: dict[str, Any],
    baseline_generation: dict[str, Any],
    baseline_seconds_per_parse: dict[str, float],
    ratio: dict[str, Any],
) -> dict[str, Any]:
    """The break-even, computed from the **paired** ratio rather than from two separate medians.

    ``gap = baseline_seconds_per_parse * (1 - 1/ratio)`` turns a drift-cancelled ratio back into a
    per-parse saving; the one-off overhead is the native machine's generation minus the baseline's
    own, exactly as in :func:`break_even_executions`.  The range is taken over the round-to-round
    range of the ratio, so a ratio whose rounds straddle ``1`` reports ``never`` at one end and a
    finite number at the other, which is the honest shape of that answer.
    """
    overhead = max(generation["seconds"]["median"] - baseline_generation["seconds"]["median"], 0.0)
    base = baseline_seconds_per_parse["median"]

    def evens(value: float) -> int | None:
        if value <= 1.0:
            return None
        gap = base * (1.0 - 1.0 / value)
        return math.ceil(overhead / gap) if gap > 0 else None

    return {
        "break_even": evens(ratio["median"]),
        "break_even_range": {
            "optimistic": evens(ratio["maximum"]),
            "median": evens(ratio["median"]),
            "pessimistic": evens(ratio["minimum"]),
        },
        "ratio": {
            "minimum": ratio["minimum"],
            "median": ratio["median"],
            "maximum": ratio["maximum"],
        },
        "one_off_overhead_seconds": overhead,
        "reason": None if ratio["median"] > 1.0 else "native is not faster than the lookup control",
    }


def registry_generation_cost(
    grammars: Sequence[Grammar] | None = None,
    *,
    repeats: int = DEFAULT_REPEATS,
) -> dict[str, Any]:
    """The one-off cost of standing up the **whole registry** under each architecture.

    This is the figure the owner's question is really about.  Twenty-five native machines are
    twenty-five compilations; one machine plus a table is one compilation and twenty-five tables.
    The difference between those two totals is what the native architecture has to earn back, and
    the registry break-even divides it by the per-parse gap.

    The shipped table-driven parser generates nothing at all, so its registry cost is zero by
    construction; it is listed with that zero rather than omitted, because a reader comparing three
    architectures should see all three one-off costs on the same line.
    """
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    totals: dict[str, dict[str, Any]] = {}
    for variant in NATIVE_VARIANTS:
        seconds = []
        for _ in range(repeats):
            started = time.perf_counter()
            for grammar in grammars:
                build_native(grammar, variant)
            seconds.append(time.perf_counter() - started)
        totals[f"native_{variant}"] = {
            "compilations": len(grammars),
            "seconds": _timing(seconds).as_dict(),
        }
    seconds = []
    for _ in range(repeats):
        started = time.perf_counter()
        shared_source = emit_native_source(grammars[0], TABLE_VARIANT)
        prepared = (shared_source, compile(shared_source, "<lookup shared>", "exec"))
        for grammar in grammars:
            build_native(grammar, TABLE_VARIANT, code=prepared)
        seconds.append(time.perf_counter() - started)
    totals["table_lookup"] = {"compilations": 1, "seconds": _timing(seconds).as_dict()}
    totals["table"] = {
        "compilations": 0,
        "seconds": {"minimum": 0.0, "median": 0.0, "maximum": 0.0, "repeats": repeats},
    }
    return {
        "grammars": len(grammars),
        "repeats": repeats,
        "totals": totals,
        "native_levels_over_lookup": totals["native_levels"]["seconds"]["median"]
        - totals["table_lookup"]["seconds"]["median"],
        "native_climb_over_lookup": totals["native_climb"]["seconds"]["median"]
        - totals["table_lookup"]["seconds"]["median"],
        "lookup_source_identical_in_every_world": len(
            {emit_native_source(grammar, TABLE_VARIANT) for grammar in grammars}
        )
        == 1,
    }


def break_even_executions(
    generation: dict[str, Any],
    native: dict[str, Any],
    table: dict[str, Any],
    baseline_generation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """How many string parses before a native machine pays for its own generation.

    ``break_even = (native one-off - baseline one-off) / (baseline per parse - native per parse)``.

    The baseline's own one-off cost is subtracted rather than ignored, because the cached
    table-driven parser also builds something once - its binding-power dictionary - and charging the
    native machine for a set-up both architectures pay would overstate the break-even.

    Where the native machine is not faster the answer is **never**, and it is reported as ``None``
    with a reason rather than as a large number.  The figure is a range because both of its inputs
    are: the optimistic end pairs the cheapest generation with the widest gap, the pessimistic end
    the dearest generation with the narrowest.
    """
    base_min = baseline_generation["seconds"]["minimum"] if baseline_generation else 0.0
    base_med = baseline_generation["seconds"]["median"] if baseline_generation else 0.0
    base_max = baseline_generation["seconds"]["maximum"] if baseline_generation else 0.0
    gap_median = table["seconds_per_parse"]["median"] - native["seconds_per_parse"]["median"]
    gap_best = table["seconds_per_parse"]["maximum"] - native["seconds_per_parse"]["minimum"]
    gap_worst = table["seconds_per_parse"]["minimum"] - native["seconds_per_parse"]["maximum"]
    if gap_median <= 0:
        return {
            "break_even": None,
            "reason": "native is not faster than the baseline in this cell",
            "gap_seconds_per_parse": {"median": gap_median, "best": gap_best, "worst": gap_worst},
        }
    overhead_best = max(generation["seconds"]["minimum"] - base_max, 0.0)
    overhead_median = max(generation["seconds"]["median"] - base_med, 0.0)
    overhead_worst = max(generation["seconds"]["maximum"] - base_min, 0.0)
    best = math.ceil(overhead_best / gap_best) if gap_best > 0 else None
    median = math.ceil(overhead_median / gap_median)
    worst = math.ceil(overhead_worst / gap_worst) if gap_worst > 0 else None
    return {
        "break_even": median,
        "break_even_range": {"optimistic": best, "median": median, "pessimistic": worst},
        "gap_seconds_per_parse": {"median": gap_median, "best": gap_best, "worst": gap_worst},
        "one_off_overhead_seconds": overhead_median,
        "reason": None,
    }


def throughput_table(
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    *,
    repeats: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
) -> dict[str, Any]:
    """Question 2, per world: generation on its own line, execution rates, and the break-even.

    Five architectures per world - the two native variants, the shipped table-driven parser, the
    generated ``lookup`` control, and parse-then-convert - each measured over the same string list
    with the same denominator.  Generation is reported on its own and never folded into a rate.

    Two instruments, and the report reads them in this order.  The **absolute rates** come from
    :func:`measure_rate` and answer the owner's question in his own unit, strings per second.  The
    **ratios** come from :func:`paired_ratio`, which times the two machines alternately in one round
    so that drift cancels; where the two instruments disagree the paired one is believed, because the
    noise floor measured with the same paired instrument is what says whether a ratio is resolvable
    at all.
    """
    entries = tuple(entries) if entries is not None else named_corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    sources = tuple(entry.source for entry in entries)
    rows = []
    for grammar in grammars:
        machines = {
            variant: build_native(grammar, variant) for variant in NATIVE_VARIANTS
        }
        lookup_machine = build_native(grammar, TABLE_VARIANT)
        calls: dict[str, Callable[[str], Node]] = {
            "native_levels": machines["levels"].parse_source,
            "native_climb": machines["climb"].parse_source,
            "table": lambda source, grammar=grammar: parse(source, grammar),
            "table_lookup": lookup_machine.parse_source,
            "convert": lambda source, grammar=grammar: parse_then_convert(source, grammar),
        }
        rates = {
            name: measure_rate(call, sources, repeats=repeats, passes=passes)
            for name, call in calls.items()
        }
        generation = {
            variant: generation_cost(grammar, variant, repeats=repeats) for variant in NATIVE_VARIANTS
        }
        generation["table_lookup"] = marginal_generation_cost(grammar, TABLE_VARIANT, repeats=repeats)
        paired = {
            name: paired_ratio(
                calls["table_lookup"], calls[name], sources, rounds=repeats, passes=passes
            )
            for name in ("native_levels", "native_climb", "table", "convert")
        }
        row: dict[str, Any] = {
            "grammar": grammar.id,
            "levels": len(grammar.levels),
            "rates": rates,
            "paired_against_lookup": paired,
            "generation": generation,
            "break_even": {
                f"native_{variant}": break_even_from_ratio(
                    generation[variant],
                    generation["table_lookup"],
                    rates["table_lookup"]["seconds_per_parse"],
                    paired[f"native_{variant}"],
                )
                for variant in NATIVE_VARIANTS
            },
            # Composed from two paired measurements that share the lookup control, in the same rounds:
            # (shipped / lookup) x (lookup / native).  It is DERIVED and labelled as such; the
            # directly measured quantity is always the ratio against the lookup control.
            "derived_against_shipped_table": {
                f"native_{variant}": paired[f"native_{variant}"]["median"] / paired["table"]["median"]
                for variant in NATIVE_VARIANTS
            },
            "break_even_against_shipped_table_paired": {
                f"native_{variant}": break_even_from_ratio(
                    generation[variant],
                    {"seconds": {"minimum": 0.0, "median": 0.0, "maximum": 0.0}},
                    rates["table"]["seconds_per_parse"],
                    {
                        "minimum": paired[f"native_{variant}"]["minimum"] / paired["table"]["maximum"],
                        "median": paired[f"native_{variant}"]["median"] / paired["table"]["median"],
                        "maximum": paired[f"native_{variant}"]["maximum"] / paired["table"]["minimum"],
                    },
                )
                for variant in NATIVE_VARIANTS
            },
            "break_even_unpaired": {
                f"native_{variant}": break_even_executions(
                    generation[variant],
                    rates[f"native_{variant}"],
                    rates["table_lookup"],
                    generation["table_lookup"],
                )
                for variant in NATIVE_VARIANTS
            },
            "break_even_against_shipped_table": {
                f"native_{variant}": break_even_executions(
                    generation[variant], rates[f"native_{variant}"], rates["table"]
                )
                for variant in NATIVE_VARIANTS
            },
            "speedup_over_table": {
                f"native_{variant}": rates["table"]["seconds_per_parse"]["median"]
                / rates[f"native_{variant}"]["seconds_per_parse"]["median"]
                for variant in NATIVE_VARIANTS
            },
            "speedup_over_lookup": {
                f"native_{variant}": rates["table_lookup"]["seconds_per_parse"]["median"]
                / rates[f"native_{variant}"]["seconds_per_parse"]["median"]
                for variant in NATIVE_VARIANTS
            },
        }
        for name in ("table_lookup", "convert"):
            row["speedup_over_table"][name] = (
                rates["table"]["seconds_per_parse"]["median"]
                / rates[name]["seconds_per_parse"]["median"]
            )
        row["speedup_over_lookup"]["convert"] = (
            rates["table_lookup"]["seconds_per_parse"]["median"]
            / rates["convert"]["seconds_per_parse"]["median"]
        )
        rows.append(row)
    contaminated = [
        {"grammar": row["grammar"], "architecture": name,
         "block_spread": row["rates"][name]["seconds_per_parse"]["maximum"]
         / row["rates"][name]["seconds_per_parse"]["minimum"]}
        for row in rows
        for name in ARCHITECTURES
        if row["rates"][name]["seconds_per_parse"]["maximum"]
        > 1.5 * row["rates"][name]["seconds_per_parse"]["minimum"]
    ]
    return {
        "entries": len(entries),
        "strings": len(sources),
        "grammars": len(grammars),
        "repeats": repeats,
        "passes": passes,
        "rows": rows,
        # An absolute rate whose own repeats span more than a factor of 1.5 was measured through
        # interference and is not a resolvable reading of that cell.  The count is published rather
        # than the cells being dropped, because dropping them would be selecting on the answer.
        "contaminated_rate_cells": contaminated,
        "contaminated_rate_cell_count": len(contaminated),
        "rate_cells": len(rows) * len(ARCHITECTURES),
        "environment": environment(),
    }


def noise_floor(
    grammars: Sequence[Grammar] | None = None,
    entries: Sequence[Entry] | None = None,
    *,
    repeats: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
) -> dict[str, Any]:
    """The gap between two **byte-identical** machines timed in the same run.

    0053's discipline, applied to a Python stopwatch instead of a C one.  Two native machines are
    built from the same world; :func:`emit_native_source` is deterministic, so their sources are
    identical strings and the two compiled functions do exactly the same work.  Any measured gap
    between them is interference on the machine and nothing else.

    This is the band against which every per-world ratio in :func:`specialisation_control` must be
    read.  It is measured rather than declared, and it is measured in the same process, on the same
    corpus, **through the same paired instrument** as the numbers it bounds: whatever
    :func:`paired_ratio` returns for two machines whose true ratio is exactly ``1`` is what this
    harness cannot resolve.

    Both instruments are reported.  ``unpaired_relative_gap`` compares two independently measured
    medians, which is what the card's first revision did; ``paired_deviation`` is how far the ABBA
    ratio departs from ``1``.  Publishing both is the evidence for preferring the second.
    """
    entries = tuple(entries) if entries is not None else named_corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    sources = tuple(entry.source for entry in entries)
    rows = []
    for grammar in grammars:
        first = build_native(grammar, "levels")
        second = build_native(grammar, "levels")
        if first.source != second.source:
            raise RuntimeError("the emitter is not deterministic; the noise floor is meaningless")
        rate_first = measure_rate(first.parse_source, sources, repeats=repeats, passes=passes)
        rate_second = measure_rate(second.parse_source, sources, repeats=repeats, passes=passes)
        one = rate_first["seconds_per_parse"]["median"]
        two = rate_second["seconds_per_parse"]["median"]
        ratio = paired_ratio(
            first.parse_source, second.parse_source, sources, rounds=repeats, passes=passes
        )
        rows.append(
            {
                "grammar": grammar.id,
                "first_seconds_per_parse": one,
                "second_seconds_per_parse": two,
                "unpaired_relative_gap": abs(one - two) / min(one, two),
                "paired_ratio": {
                    "minimum": ratio["minimum"],
                    "median": ratio["median"],
                    "maximum": ratio["maximum"],
                },
                "paired_deviation": max(
                    abs(ratio["median"] - 1.0), abs(ratio["minimum"] - 1.0), abs(ratio["maximum"] - 1.0)
                ),
                "paired_median_deviation": abs(ratio["median"] - 1.0),
            }
        )
    gaps = [row["unpaired_relative_gap"] for row in rows]
    paired_medians = [row["paired_median_deviation"] for row in rows]
    paired_worst = [row["paired_deviation"] for row in rows]
    return {
        "grammars": len(grammars),
        "rows": rows,
        "median_relative_gap": statistics.median(gaps),
        "worst_relative_gap": max(gaps),
        "paired_median_deviation": statistics.median(paired_medians),
        "paired_worst_median_deviation": max(paired_medians),
        "paired_worst_round_deviation": max(paired_worst),
        "repeats": repeats,
        "passes": passes,
        "parses_per_block": passes * len(sources),
    }


def tokenizer_share(
    grammars: Sequence[Grammar] | None = None,
    entries: Sequence[Entry] | None = None,
    *,
    repeats: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
) -> dict[str, Any]:
    """How much of a string-to-tree parse is the **shared** tokenizer, and therefore not specialisable.

    Both architectures call the same :func:`parseatlas.tokenizer.tokenize`.  It is the same code in
    all 25 worlds and in both architectures, so it is a floor under the end-to-end figure: no amount
    of specialising the parser can remove it, and the largest end-to-end ratio any specialisation
    could ever reach is bounded by Amdahl's rule against that share.

    Reported here so the headline rate is read with its ceiling beside it, rather than leaving a
    reader to wonder why a 1.5x win on the specialised half shows up as a smaller one end to end.
    Three quantities per world, all as ranges: tokenizing alone, the native machine on **already
    tokenized** input, and the cached table-driven machine on the same tokens.
    """
    entries = tuple(entries) if entries is not None else named_corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    sources = tuple(entry.source for entry in entries)
    token_lists = tuple(tokenize(source) for source in sources)
    rows = []
    for grammar in grammars:
        machine = build_native(grammar, "levels")
        lookup_machine = build_native(grammar, TABLE_VARIANT)

        def time_tokens(call: Callable[[Any], Any], payloads: Sequence[Any]) -> dict[str, Any]:
            seconds = []
            for _ in range(repeats):
                started = time.perf_counter()
                for _ in range(passes):
                    for payload in payloads:
                        if call(payload) is None:
                            raise RuntimeError("no result")
                seconds.append(time.perf_counter() - started)
            block = _timing(seconds)
            per = passes * len(payloads)
            return {
                "minimum": block.minimum / per,
                "median": block.median / per,
                "maximum": block.maximum / per,
                "repeats": block.repeats,
            }

        tokenise_only = time_tokens(tokenize, sources)
        native_tokens = time_tokens(machine.parse_tokens, token_lists)
        table_tokens = time_tokens(lookup_machine.parse_tokens, token_lists)
        end_to_end = measure_rate(machine.parse_source, sources, repeats=repeats, passes=passes)
        rows.append(
            {
                "grammar": grammar.id,
                "tokenize_seconds": tokenise_only,
                "native_parse_only_seconds": native_tokens,
                "lookup_parse_only_seconds": table_tokens,
                "native_end_to_end_seconds": end_to_end["seconds_per_parse"],
                "tokenizer_share_of_native_end_to_end": tokenise_only["median"]
                / end_to_end["seconds_per_parse"]["median"],
                "parse_only_ratio": table_tokens["median"] / native_tokens["median"],
            }
        )
    shares = [row["tokenizer_share_of_native_end_to_end"] for row in rows]
    ratios = [row["parse_only_ratio"] for row in rows]
    return {
        "entries": len(entries),
        "grammars": len(grammars),
        "rows": rows,
        "share_minimum": min(shares),
        "share_median": statistics.median(shares),
        "share_maximum": max(shares),
        "parse_only_ratio_minimum": min(ratios),
        "parse_only_ratio_median": statistics.median(ratios),
        "parse_only_ratio_maximum": max(ratios),
        "amdahl_ceiling_at_median_share": 1.0 / statistics.median(shares),
    }


def throughput_repeatability(
    runs: int = 3,
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    *,
    repeats: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
) -> dict[str, Any]:
    """Re-run the whole throughput measurement and publish the range each headline moved over.

    0053 was returned once for publishing a survival count as a single reading that three
    independent re-runs did not reproduce.  The instrument that made that visible was a repeat of
    the entire measurement, and this is the same instrument: fresh machines, fresh timing, the whole
    table, ``runs`` times over.  What is reported is the smallest and largest value each headline
    took, never a midpoint of readings that disagree.
    """
    tables = [
        throughput_table(entries, grammars, repeats=repeats, passes=passes) for _ in range(runs)
    ]
    controls = [specialisation_control(table) for table in tables]
    per_world: dict[str, dict[str, Any]] = {}
    for row in tables[0]["rows"]:
        world = row["grammar"]
        for variant in NATIVE_VARIANTS:
            key = f"native_{variant}"
            ratios = [
                next(item for item in table["rows"] if item["grammar"] == world)["paired_against_lookup"][key]["median"]
                for table in tables
            ]
            evens = [
                next(item for item in table["rows"] if item["grammar"] == world)["break_even"][key]["break_even"]
                for table in tables
            ]
            per_world.setdefault(world, {})[key] = {
                "ratio_minimum": min(ratios),
                "ratio_maximum": max(ratios),
                "break_even_readings": evens,
                "break_even_minimum": min((value for value in evens if value is not None), default=None),
                "break_even_maximum": max((value for value in evens if value is not None), default=None),
                "never_readings": sum(1 for value in evens if value is None),
            }
    pooled: dict[str, Any] = {}
    for variant in NATIVE_VARIANTS:
        key = f"native_{variant}"
        ratios = [
            row["paired_against_lookup"][key]["median"] for table in tables for row in table["rows"]
        ]
        evens = [
            row["break_even"][key]["break_even"] for table in tables for row in table["rows"]
        ]
        finite = [value for value in evens if value is not None]
        pooled[key] = {
            "readings": len(evens),
            "ratio_minimum": min(ratios),
            "ratio_median": statistics.median(ratios),
            "ratio_maximum": max(ratios),
            "break_even_minimum": min(finite) if finite else None,
            "break_even_median": statistics.median(finite) if finite else None,
            "break_even_maximum": max(finite) if finite else None,
            "never_readings": len(evens) - len(finite),
        }
    return {
        "runs": runs,
        "per_world": per_world,
        "pooled": pooled,
        "control_ratio_range": {
            variant: {
                "minimum": min(control["control"][variant] for control in controls),
                "maximum": max(control["control"][variant] for control in controls),
            }
            for variant in NATIVE_VARIANTS
        },
        "strict_median_ratio_range": {
            variant: {
                "minimum": min(control["variants"][variant]["strict_median"] for control in controls),
                "maximum": max(control["variants"][variant]["strict_median"] for control in controls),
            }
            for variant in NATIVE_VARIANTS
        },
        "worlds_slower_than_lookup_readings": {
            variant: [
                sum(1 for row in table["rows"] if row["paired_against_lookup"][f"native_{variant}"]["median"] < 1.0)
                for table in tables
            ]
            for variant in NATIVE_VARIANTS
        },
    }


def specialisation_control(table: dict[str, Any]) -> dict[str, Any]:
    """The null model, read out of a throughput table.

    ``G0`` native against ``G0`` table-driven is the same world, so the ratio there is **pure
    partial evaluation** and carries no information about conventions at all.  Every other world's
    ratio is reported against it, and the spread of the 24 strict worlds' ratios is what would have
    to be large for any part of the effect to be about conventions rather than about specialisation.
    """
    rows = {row["grammar"]: row for row in table["rows"]}
    control = rows.get("G0")
    if control is None:
        raise ValueError("the throughput table has no G0 row; the null model cannot be read")
    out: dict[str, Any] = {"control": {}, "variants": {}, "baselines": {}}
    for baseline in ("speedup_over_lookup", "speedup_over_table"):
        out["baselines"][baseline] = {}
        for variant in NATIVE_VARIANTS:
            key = f"native_{variant}"
            control_ratio = control[baseline][key]
            values = sorted(
                row[baseline][key] for row in table["rows"] if row["grammar"] != "G0"
            )
            record = {
                "control_ratio": control_ratio,
                "strict_minimum": values[0],
                "strict_median": statistics.median(values),
                "strict_maximum": values[-1],
                "strict_spread": values[-1] - values[0],
                "strict_spread_relative_to_control": (values[-1] - values[0]) / control_ratio,
                "worlds_beating_control": sum(1 for value in values if value > control_ratio),
                "worlds_slower_than_baseline": sum(1 for value in values if value < 1.0),
            }
            out["baselines"][baseline][variant] = record
    out["paired"] = {}
    for variant in NATIVE_VARIANTS:
        key = f"native_{variant}"
        control_ratio = control["paired_against_lookup"][key]["median"]
        values = sorted(
            row["paired_against_lookup"][key]["median"]
            for row in table["rows"]
            if row["grammar"] != "G0"
        )
        record = {
            "control_ratio": control_ratio,
            "control_round_range": [
                control["paired_against_lookup"][key]["minimum"],
                control["paired_against_lookup"][key]["maximum"],
            ],
            "strict_minimum": values[0],
            "strict_median": statistics.median(values),
            "strict_maximum": values[-1],
            "strict_spread": values[-1] - values[0],
            "strict_spread_relative_to_control": (values[-1] - values[0]) / control_ratio,
            "worlds_beating_control": sum(1 for value in values if value > control_ratio),
            "worlds_slower_than_baseline": sum(1 for value in values if value < 1.0),
        }
        out["paired"][variant] = record
        out["control"][variant] = control_ratio
        out["variants"][variant] = record
    return out


def length_curve(
    lengths: Sequence[int] = SWEEP_LENGTHS,
    grammars: Sequence[Grammar] | None = None,
    *,
    support: Sequence[str] = ("+", "-", "*", "/"),
    rounds: int = DEFAULT_REPEATS,
    work_per_block: int = 3000,
) -> dict[str, Any]:
    """Sweep the expression length and publish the curve rather than a point.

    Nothing here declares an interesting length.  The sweep runs from a two-operand word to a
    128-operand one - far past anything in the named corpus, whose widest entry has nine operands -
    and reports at every length the per-parse cost of each architecture, the drift-cancelled ratio
    against the lookup control, and the break-even in executions.

    **The passes per block are scaled so that every point does comparable work**:
    ``passes = max(4, work_per_block // length)``.  Without that, the short end of the sweep is
    measured in blocks a hundred times shorter than the long end and the curve's shape is an artifact
    of the timer rather than of the expression.  An earlier revision of this function did exactly
    that and produced ratio readings of ``0.377`` and ``0.356`` at length three, which is not a
    property of a three-operand word.

    Turning points are reported in two forms - every sign change in the curve, and the subset that
    survives the measured round-to-round spread of the three points involved.  Reporting the first
    alone would publish noise as structure; reporting neither would hide a turn.
    """
    grammars = tuple(grammars) if grammars is not None else (CONTROL, all_grammars()[1])
    points = []
    for length in lengths:
        source = sweep_word(length, support)
        passes = max(4, work_per_block // max(length, 1))
        for grammar in grammars:
            machines = {variant: build_native(grammar, variant) for variant in NATIVE_VARIANTS}
            lookup_machine = build_native(grammar, TABLE_VARIANT)
            calls: dict[str, Callable[[str], Node]] = {
                "native_levels": machines["levels"].parse_source,
                "native_climb": machines["climb"].parse_source,
                "table": lambda text, grammar=grammar: parse(text, grammar),
                "table_lookup": lookup_machine.parse_source,
                "convert": lambda text, grammar=grammar: parse_then_convert(text, grammar),
            }
            rates = {
                name: measure_rate(call, (source,), repeats=rounds, passes=passes)
                for name, call in calls.items()
            }
            paired = {
                name: paired_ratio(
                    calls["table_lookup"], calls[name], (source,), rounds=rounds, passes=passes
                )
                for name in ("native_levels", "native_climb", "table", "convert")
            }
            generation = {
                variant: generation_cost(grammar, variant, repeats=rounds)
                for variant in NATIVE_VARIANTS
            }
            lookup_generation = marginal_generation_cost(grammar, TABLE_VARIANT, repeats=rounds)
            points.append(
                {
                    "length": length,
                    "grammar": grammar.id,
                    "operations": length - 1,
                    "passes": passes,
                    "parses_per_block": passes,
                    "seconds_per_parse": {name: rates[name]["seconds_per_parse"] for name in rates},
                    "paired_against_lookup": paired,
                    "break_even": {
                        f"native_{variant}": break_even_from_ratio(
                            generation[variant],
                            lookup_generation,
                            rates["table_lookup"]["seconds_per_parse"],
                            paired[f"native_{variant}"],
                        )
                        for variant in NATIVE_VARIANTS
                    },
                    "ratio_over_lookup": {
                        f"native_{variant}": paired[f"native_{variant}"]["median"]
                        for variant in NATIVE_VARIANTS
                    },
                    "conversion_over_lookup": 1.0 / paired["convert"]["median"],
                }
            )
    return {
        "support": tuple(support),
        "lengths": tuple(lengths),
        "grammars": [grammar.id for grammar in grammars],
        "rounds": rounds,
        "work_per_block": work_per_block,
        "points": points,
        "turning_points": _turning_points(points),
    }


def _turning_points(points: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Where a swept curve stops being monotone - and which of those turns is resolvable.

    A sign change in a noisy curve is not a turning point, and publishing it as one would be exactly
    the mistake the ROADMAP principle is aimed at from the other side.  A turn counts as **resolvable**
    only when the middle point's whole round-to-round range clears both neighbours' ranges, so a
    reader can tell a turn in the quantity from a turn in the machine's load.
    """
    found: dict[str, Any] = {}
    for grammar_id in sorted({point["grammar"] for point in points}):
        series = sorted(
            (point for point in points if point["grammar"] == grammar_id),
            key=lambda point: point["length"],
        )
        for key in ("native_levels", "native_climb", "convert"):
            band = [
                (
                    point["length"],
                    point["paired_against_lookup"][key]["minimum"],
                    point["paired_against_lookup"][key]["median"],
                    point["paired_against_lookup"][key]["maximum"],
                )
                for point in series
            ]
            turns = []
            resolvable = []
            for index in range(1, len(band) - 1):
                before, here, after = band[index - 1], band[index], band[index + 1]
                if (here[2] - before[2]) * (after[2] - here[2]) < 0:
                    turns.append({"length": here[0], "ratio": here[2]})
                    peak = here[1] > before[3] and here[1] > after[3]
                    trough = here[3] < before[1] and here[3] < after[1]
                    if peak or trough:
                        resolvable.append(
                            {"length": here[0], "ratio": here[2], "kind": "peak" if peak else "trough"}
                        )
            found[f"{grammar_id}:{key}"] = {
                "monotone": not turns,
                "turns": turns,
                "resolvable_turns": resolvable,
                "resolvable": bool(resolvable),
                "series": [
                    {"length": length, "minimum": low, "ratio": mid, "maximum": high}
                    for length, low, mid, high in band
                ],
            }
    return found


# ------------------------------------------------------------------------------ emitted dataflow


def graph_profile(tree: Node) -> dict[str, int]:
    """The emitted dataflow graph's three structural measures, all imported from their own cards.

    ``operations`` is 0021's operation multiset summed; ``depth`` is 0041's critical path with a
    leaf at ``0``; ``peak_live`` is 0044's Sethi-Ullman simultaneously live values.  Nothing is
    re-implemented here.
    """
    cost = operation_cost(tree)
    profile = {key: cost[key] for key in OPERATION_KEYS}
    profile["operations"] = sum(cost[key] for key in OPERATION_KEYS)
    profile["nodes"] = cost["nodes"]
    profile["depth"] = depth(tree)
    profile["peak_live"] = peak_live(tree)
    return profile


def dataflow_table(
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """Question 3: what each world's **native reading** of each string emits, measured on the graph.

    This is the half that survives even if the parser difference is zero, and it is the real subject
    of the card.  For every string and every world the tree is taken from that world's own native
    machine - not converted, not re-parsed - and profiled.
    """
    entries = tuple(entries) if entries is not None else corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    machines = {grammar.id: build_native(grammar, "levels") for grammar in grammars}
    cells = []
    for entry in entries:
        for grammar in grammars:
            tree = machines[grammar.id].parse_source(entry.source)
            profile = graph_profile(tree)
            cells.append(
                {
                    "entry": entry.name,
                    "family": entry.family,
                    "grammar": grammar.id,
                    "serialised": serialise(tree),
                    **profile,
                }
            )
    by_world: dict[str, dict[str, float]] = {}
    for grammar in grammars:
        rows = [cell for cell in cells if cell["grammar"] == grammar.id]
        by_world[grammar.id] = {
            "mean_operations": statistics.fmean(row["operations"] for row in rows),
            "mean_depth": statistics.fmean(row["depth"] for row in rows),
            "mean_peak_live": statistics.fmean(row["peak_live"] for row in rows),
            "max_depth": max(row["depth"] for row in rows),
            "max_peak_live": max(row["peak_live"] for row in rows),
        }
    spread = []
    for entry in entries:
        rows = [cell for cell in cells if cell["entry"] == entry.name]
        depths = [row["depth"] for row in rows]
        lives = [row["peak_live"] for row in rows]
        operations = {row["operations"] for row in rows}
        spread.append(
            {
                "entry": entry.name,
                "family": entry.family,
                "source": entry.source,
                "operations": sorted(operations),
                "operation_count_invariant": len(operations) == 1,
                "depth_minimum": min(depths),
                "depth_maximum": max(depths),
                "depth_spread": max(depths) - min(depths),
                "peak_live_minimum": min(lives),
                "peak_live_maximum": max(lives),
                "peak_live_spread": max(lives) - min(lives),
                "distinct_graphs": len({row["serialised"] for row in rows}),
            }
        )
    return {
        "entries": len(entries),
        "grammars": len(grammars),
        "cells": len(cells),
        "by_world": by_world,
        "by_entry": spread,
        "worlds_ranked_by_mean_depth": sorted(
            by_world, key=lambda name: (by_world[name]["mean_depth"], name)
        ),
        "worlds_ranked_by_mean_peak_live": sorted(
            by_world, key=lambda name: (by_world[name]["mean_peak_live"], name)
        ),
    }


def operation_invariance(
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    *,
    sabotage: bool = False,
) -> dict[str, Any]:
    """Is the emitted graph's operation multiset the same in all 25 worlds, for a fixed string?

    It should be: a convention re-associates a fixed sequence of operator tokens, and every token
    becomes exactly one node, so no world can issue an operation another world does not.  The point
    of checking is that it is the assumption every per-world *depth* and *peak live* comparison in
    question 3 rests on - if it failed, those comparisons would be between different computations.

    ``sabotage`` corrupts one cell's multiset before the check, so the check can be shown to fail.
    """
    entries = tuple(entries) if entries is not None else corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    machines = {grammar.id: build_native(grammar, "levels") for grammar in grammars}
    failures = []
    checked = 0
    for entry in entries:
        multisets = set()
        for grammar in grammars:
            tree = machines[grammar.id].parse_source(entry.source)
            cost = operation_cost(tree)
            multiset = tuple(cost[key] for key in OPERATION_KEYS)
            if sabotage and grammar.id == grammars[-1].id and entry.name == entries[0].name:
                multiset = tuple(value + 1 for value in multiset)
            multisets.add(multiset)
            checked += 1
        if len(multisets) != 1:
            failures.append({"entry": entry.name, "multisets": sorted(multisets)})
    return {
        "checked": checked,
        "entries": len(entries),
        "failures": failures,
        "invariant": not failures,
        "sabotage": sabotage,
    }


def distinct_graph_table(
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    *,
    sabotage: bool = False,
) -> dict[str, Any]:
    """How many distinct graphs the 25 worlds actually read a string into, against the T6 bound.

    **The bound is stated first.**  Theorem T6 (0019) says a grammar acts on an expression only
    through its restriction to the operators that expression uses, so over the 24 strict
    permutations a word with ``s`` distinct operators can be read into at most ``s!`` distinct
    trees.  ``G0`` is the twenty-fifth world and it is not a permutation - it has tied levels - so
    over all 25 the bound is ``s! + 1``.

    Then the corpus is enumerated against it.  Where the corpus falls below the bound, the shortfall
    is measured and reported, never inferred; and the bound is checked by enumeration rather than
    cited, because a computational bound is not a finding.
    """
    entries = tuple(entries) if entries is not None else corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    strict = tuple(grammar for grammar in grammars if grammar.id != "G0")
    machines = {grammar.id: build_native(grammar, "levels") for grammar in grammars}
    rows = []
    violations = []
    for entry in entries:
        support = operator_support(entry.source)
        # ``sabotage`` under-counts the operator support by one, which makes the T6 bound too small
        # and must therefore be caught as a violation.  It exists only so the bound check can be
        # shown to fire; no reported number uses it.
        counted = len(support) - 1 if sabotage and len(support) > 1 else len(support)
        bound = math.factorial(counted)
        strict_forms = {machines[grammar.id].parse_source(entry.source) for grammar in strict}
        strict_serial = {serialise(tree) for tree in strict_forms}
        all_serial = {
            serialise(machines[grammar.id].parse_source(entry.source)) for grammar in grammars
        }
        control_serial = serialise(machines["G0"].parse_source(entry.source))
        row = {
            "entry": entry.name,
            "family": entry.family,
            "source": entry.source,
            "support": support,
            "support_size": len(support),
            "strict_bound": bound,
            "distinct_strict": len(strict_serial),
            "distinct_all": len(all_serial),
            "all_bound": bound + 1,
            "shortfall_strict": bound - len(strict_serial),
            "control_is_distinct": control_serial not in strict_serial,
        }
        if row["distinct_strict"] > bound or row["distinct_all"] > bound + 1:
            violations.append(row)
        rows.append(row)
    return {
        "entries": len(entries),
        "rows": rows,
        "bound_respected": not violations,
        "violations": violations,
        "sabotage": sabotage,
        "entries_at_bound": sum(1 for row in rows if row["distinct_strict"] == row["strict_bound"]),
        "entries_below_bound": sum(1 for row in rows if row["distinct_strict"] < row["strict_bound"]),
        "control_distinct_entries": sorted(row["entry"] for row in rows if row["control_is_distinct"]),
        "by_support_size": {
            size: {
                "entries": sum(1 for row in rows if row["support_size"] == size),
                "bound": math.factorial(size),
                "mean_distinct_strict": statistics.fmean(
                    [row["distinct_strict"] for row in rows if row["support_size"] == size]
                )
                if any(row["support_size"] == size for row in rows)
                else 0.0,
                "maximum_distinct_strict": max(
                    [row["distinct_strict"] for row in rows if row["support_size"] == size],
                    default=0,
                ),
            }
            for size in sorted({row["support_size"] for row in rows})
        },
    }


def bound_attainment(
    operator_counts: Sequence[int] = (4, 5, 6, 7, 8),
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """Is the T6 bound of ``24`` ever attained?  Answered by **exhaustive enumeration**, not by citation.

    A bound is not a finding, and the corpus falling below one says nothing about the bound.  So this
    enumerates **every** word over the four operators, for each declared operator count, keeps the
    ones whose support is all four, and reads each with all 24 strict machines.  The space is finite
    and it is searched completely: ``4**k`` words for ``k`` operators, of which the four-operator ones
    are counted and reported.

    What is returned per ``k``: how many four-operator words there are, the largest number of distinct
    trees any of them produces, the full histogram of that count, how many words attain ``24``, and
    the first witness that does.  Where nothing attains it, that is a statement about words of that
    length and about nothing longer.
    """
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    strict = [grammar for grammar in grammars if grammar.id != "G0"]
    machines = {grammar.id: build_native(grammar, "levels") for grammar in strict}
    bound = math.factorial(len(OPERATOR_ALPHABET))
    rows = []
    for count in operator_counts:
        names = [f"v{index}" for index in range(count + 1)]
        histogram: dict[int, int] = {}
        words = 0
        best = 0
        best_word: str | None = None
        attaining = 0
        witness: str | None = None
        for combination in itertools.product(OPERATOR_ALPHABET, repeat=count):
            if len(set(combination)) != len(OPERATOR_ALPHABET):
                continue
            words += 1
            text = names[0] + "".join(
                f" {operator} {names[index + 1]}" for index, operator in enumerate(combination)
            )
            distinct = len(
                {serialise(machines[grammar.id].parse_source(text)) for grammar in strict}
            )
            histogram[distinct] = histogram.get(distinct, 0) + 1
            if distinct > best:
                best, best_word = distinct, text
            if distinct == bound:
                attaining += 1
                if witness is None:
                    witness = text
        rows.append(
            {
                "operators": count,
                "operands": count + 1,
                "four_operator_words": words,
                "maximum_distinct": best,
                "maximum_witness": best_word,
                "histogram": dict(sorted(histogram.items())),
                "attaining_bound": attaining,
                "bound_witness": witness,
            }
        )
    attained = [row for row in rows if row["attaining_bound"]]
    return {
        "bound": bound,
        "strict_worlds": len(strict),
        "rows": rows,
        "words_enumerated": sum(row["four_operator_words"] for row in rows),
        "bound_attained": bool(attained),
        "shortest_attaining_operators": attained[0]["operators"] if attained else None,
        "shortest_attaining_witness": attained[0]["bound_witness"] if attained else None,
        "counts_never_observed": sorted(
            value
            for value in range(1, bound + 1)
            if all(value not in row["histogram"] for row in rows)
        ),
    }


def long_word_check(
    lengths: Sequence[int] = (192, 256, 384, 512),
    supports: Sequence[Sequence[str]] = SWEEP_SUPPORTS,
    grammars: Sequence[Grammar] | None = None,
) -> dict[str, Any]:
    """The structural sweep continued past the timed one, and where it stops and why.

    The timed sweep ends at ``128`` operands because a timed block has to be run many times; the
    structural quantities cost one parse each, so they are carried further here.  The stopping point
    is a **computational** bound and is named as one: the AST serialiser recurses once per tree
    level, so a left chain longer than CPython's frame limit cannot be serialised.  What is reported
    is how far the check ran and what it found there, not a claim about what lies beyond.
    """
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    rows = []
    for length in lengths:
        entries = tuple(
            Entry(f"long_{''.join(support)}_{length}", f"long:{''.join(support)}", sweep_word(length, support))
            for support in supports
        )
        try:
            graphs = distinct_graph_table(entries, grammars)
            flow = dataflow_table(entries, grammars)
        except RecursionError as error:
            rows.append({"length": length, "stopped": f"RecursionError: {error}"})
            continue
        for graph_row, flow_row in zip(graphs["rows"], flow["by_entry"]):
            rows.append(
                {
                    "length": length,
                    "support": graph_row["support"],
                    "strict_bound": graph_row["strict_bound"],
                    "distinct_strict": graph_row["distinct_strict"],
                    "distinct_all": graph_row["distinct_all"],
                    "depth_minimum": flow_row["depth_minimum"],
                    "depth_maximum": flow_row["depth_maximum"],
                    "peak_live_minimum": flow_row["peak_live_minimum"],
                    "peak_live_maximum": flow_row["peak_live_maximum"],
                    "operations": flow_row["operations"],
                }
            )
    return {
        "lengths": tuple(lengths),
        "rows": rows,
        "recursion_limit": sys.getrecursionlimit(),
        "bound_respected": all(
            row.get("distinct_strict", 0) <= row.get("strict_bound", 0)
            for row in rows
            if "distinct_strict" in row
        ),
    }


def sharpest_objects(
    dataflow: dict[str, Any],
    count: int = 4,
    family_prefix: str | None = None,
) -> tuple[str, ...]:
    """The corpus entries where the 25 worlds' readings differ most, by depth spread then graph count.

    These are the objects question 4 takes to the compiler.  The selection rule is declared here and
    applied mechanically; nothing is hand-picked, and ties are broken by the entry name so the
    selection is a function of the corpus rather than of a dictionary ordering.

    ``family_prefix`` restricts the choice to one family, which is how the report takes its sharpest
    objects from the **named** corpus and from the generated **sweep** family separately: the widest
    spreads in the whole corpus all belong to the longest generated words, and taking only those
    would have sent no real mathematics to the compiler.
    """
    rows = [
        row
        for row in dataflow["by_entry"]
        if family_prefix is None or row["family"].startswith(family_prefix)
    ]
    rows.sort(key=lambda row: (-row["depth_spread"], -row["distinct_graphs"], row["entry"]))
    return tuple(row["entry"] for row in rows[:count])


# ----------------------------------------------------------------------------------- the metal


def _c_literal(value: Fraction) -> str:
    text = repr(float(value))
    if "." not in text and "e" not in text and "E" not in text and "inf" not in text:
        text += ".0"
    return text


def emit_c_function(tree: Node, name: str) -> str:
    """One world's reading of one string as a C function: the dataflow graph, transcribed.

    The method is experiment 0053's and is deliberately re-stated here rather than imported, because
    0053 is being edited concurrently with this card.  One operation per statement into a named
    ``double`` temporary, in the tree's own post-order, so the C source is a transcript of the graph
    and not a string a C compiler's precedence would have to re-parse; parameters in sorted variable
    order; emission deterministic from the tree.
    """
    if not name.isidentifier():
        raise ValueError(f"{name!r} is not a legal C function name")
    variables: list[str] = []

    def collect(node: Node) -> None:
        if isinstance(node, Binary):
            collect(node.left)
            collect(node.right)
        elif isinstance(node, Variable) and node.name not in variables:
            variables.append(node.name)

    collect(tree)
    variables.sort()
    lines: list[str] = []
    counter = 0

    def walk(node: Node) -> str:
        nonlocal counter
        if isinstance(node, Number):
            return _c_literal(node.value)
        if isinstance(node, Variable):
            return "x_" + node.name
        left = walk(node.left)
        right = walk(node.right)
        temporary = f"t{counter}"
        counter += 1
        lines.append(f"    double {temporary} = {left} {node.operator} {right};")
        return temporary

    result = walk(tree)
    parameters = ", ".join(f"double x_{item}" for item in variables) or "void"
    body = "".join(line + "\n" for line in lines)
    return f"double {name}({parameters}) {{\n{body}    return {result};\n}}\n"


_MNEMONIC = re.compile(r"^\s+([a-z][a-z0-9._]*)\b")
_LABEL = re.compile(r"^([A-Za-z_$.][\w$.]*):")


def _split_functions(assembly: str) -> dict[str, list[str]]:
    """Mnemonics per function, read out of clang's own assembly.  0053's reader, re-stated."""
    functions: dict[str, list[str]] = {}
    current: str | None = None
    for line in assembly.splitlines():
        label = _LABEL.match(line)
        if label:
            name = label.group(1)
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


def clang_available() -> bool:
    """Whether a working ``clang`` is on PATH.  Every compiled measurement skips on ``False``."""
    if shutil.which("clang") is None:
        return False
    try:
        subprocess.run(["clang", "--version"], capture_output=True, check=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def _clang_line(prefix: str) -> str:
    if not clang_available():
        return "clang not available"
    result = subprocess.run(["clang", "--version"], capture_output=True, text=True, check=True)
    if prefix == "version":
        return result.stdout.splitlines()[0].strip()
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
        "clang": _clang_line("version"),
        "clang_target": _clang_line("target"),
    }


def identical_multisets(mnemonics: Sequence[Sequence[str]], *, sabotage: str | None = None) -> bool:
    """Are all these instruction sequences the same multiset of mnemonics?

    The decisive predicate of question 4, isolated so it can be shown to fire in both directions.
    ``sabotage`` perturbs the comparison: ``"append"`` adds an instruction to the first sequence,
    ``"collapse"`` replaces every sequence by the first.  Controls only; no reported number uses it.
    """
    sequences = [list(item) for item in mnemonics]
    if sabotage == "append":
        sequences[0] = sequences[0] + ["nop"]
    elif sabotage == "collapse":
        sequences = [list(sequences[0]) for _ in sequences]
    elif sabotage is not None:
        raise ValueError(f"unknown sabotage: {sabotage!r}")
    signatures = {tuple(sorted(sequence)) for sequence in sequences}
    return len(signatures) == 1


def instruction_table(
    entry_names: Sequence[str],
    entries: Sequence[Entry] | None = None,
    grammars: Sequence[Grammar] | None = None,
    levels: Sequence[tuple[str, tuple[str, ...]]] = CLANG_LEVELS,
    workdir: Path | None = None,
) -> dict[str, Any]:
    """Question 4: does the choice of world reach the metal?

    For each named entry, all 25 worlds' native readings are emitted as C functions **into one
    translation unit**, compiled with ``clang -S`` at each level, and the mnemonics inside each
    function counted.  Two readings that compile to the same multiset of mnemonics have had their
    difference erased before the CPU ever saw it, and that comparison has **no noise floor**: two
    multisets are equal or they are not.

    **What is being compared here is not what 0053 compared, and the difference matters.**  0053's
    kernels were equivalent writings of one value, so an instruction difference was a difference in
    how the same computation was expressed.  Here the 25 readings of one string denote up to ``s!``
    *different* functions, so an instruction difference can be a difference in what the machine was
    asked to compute.  The operation multiset is world-invariant (:func:`operation_invariance`), so
    the arithmetic issued is the same in every world; what a difference in total instructions
    measures is therefore data movement and scheduling, not arithmetic.  That is stated before the
    numbers, not after.
    """
    if not clang_available():
        return {"clang": False}
    entries = tuple(entries) if entries is not None else corpus()
    grammars = tuple(grammars) if grammars is not None else all_grammars()
    by_name = {entry.name: entry for entry in entries}
    machines = {grammar.id: build_native(grammar, "levels") for grammar in grammars}
    owned = workdir is None
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_native_")) if owned else Path(workdir)
    rows: list[dict[str, Any]] = []
    try:
        directory.mkdir(parents=True, exist_ok=True)
        for name in entry_names:
            entry = by_name[name]
            kernels = {}
            parts = []
            for grammar in grammars:
                tree = machines[grammar.id].parse_source(entry.source)
                kernel = re.sub(r"[^0-9A-Za-z_]", "_", f"k_{grammar.id}_{name}")
                kernels[grammar.id] = (kernel, tree)
                parts.append(emit_c_function(tree, kernel))
            csource = directory / f"{re.sub(r'[^0-9A-Za-z_]', '_', name)}.c"
            csource.write_text("".join(parts), encoding="ascii")
            for level_name, flags in levels:
                target = directory / f"{csource.stem}_{level_name}.s"
                command = ["clang", *flags, "-S", "-o", str(target), str(csource)]
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"{' '.join(command)}\n{result.stderr}")
                functions = _split_functions(target.read_text(encoding="utf-8", errors="replace"))
                for grammar in grammars:
                    kernel, tree = kernels[grammar.id]
                    mnemonics = functions.get(kernel, [])
                    arithmetic = {
                        "addsd": sum(1 for item in mnemonics if item == "addsd"),
                        "subsd": sum(1 for item in mnemonics if item == "subsd"),
                        "mulsd": sum(1 for item in mnemonics if item == "mulsd"),
                        "divsd": sum(1 for item in mnemonics if item == "divsd"),
                    }
                    profile = graph_profile(tree)
                    rows.append(
                        {
                            "entry": name,
                            "level": level_name,
                            "grammar": grammar.id,
                            "instructions": len(mnemonics),
                            "arithmetic_instructions": sum(arithmetic.values()),
                            **arithmetic,
                            "model_operations": profile["operations"],
                            "model_depth": profile["depth"],
                            "model_peak_live": profile["peak_live"],
                            "serialised": serialise(tree),
                            "mnemonics": mnemonics,
                        }
                    )
    finally:
        if owned:
            shutil.rmtree(directory, ignore_errors=True)

    collapse = []
    for name in entry_names:
        for level_name, _ in levels:
            group = [row for row in rows if row["entry"] == name and row["level"] == level_name]
            signatures = {tuple(sorted(row["mnemonics"])) for row in group}
            trees = {row["serialised"] for row in group}
            arithmetic_signatures = {
                (row["addsd"], row["subsd"], row["mulsd"], row["divsd"]) for row in group
            }
            collapse.append(
                {
                    "entry": name,
                    "level": level_name,
                    "worlds": len(group),
                    "distinct_trees": len(trees),
                    "distinct_instruction_multisets": len(signatures),
                    "distinct_arithmetic_multisets": len(arithmetic_signatures),
                    "identical": identical_multisets([row["mnemonics"] for row in group]),
                    "arithmetic_identical": len(arithmetic_signatures) == 1,
                    "instruction_minimum": min(row["instructions"] for row in group),
                    "instruction_maximum": max(row["instructions"] for row in group),
                }
            )
    model_agreement = [
        {
            "entry": row["entry"],
            "level": row["level"],
            "grammar": row["grammar"],
            "model_operations": row["model_operations"],
            "arithmetic_instructions": row["arithmetic_instructions"],
        }
        for row in rows
        if row["level"] == "O0" and row["arithmetic_instructions"] != row["model_operations"]
    ]
    return {
        "clang": True,
        "entries": list(entry_names),
        "levels": [name for name, _ in levels],
        "rows": rows,
        "collapse": collapse,
        "o0_arithmetic_matches_model": not model_agreement,
        "o0_model_disagreements": model_agreement,
        "environment": environment(),
    }


# ------------------------------------------------------------------------------------ multicore


def worker_count_for(cores: int, jobs: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``jobs`` independent units of work."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, max(jobs, 1)))


def default_worker_count(jobs: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, jobs)


def _profile_chunk(payload: tuple[str, tuple[str, ...]]) -> tuple[str, int, int, int]:
    """One process-pool unit: parse a string in one world natively and profile the graph."""
    grammar_id, sources = payload
    grammar = next(item for item in all_grammars() if item.id == grammar_id)
    machine = build_native(grammar, "levels")
    operations = 0
    total_depth = 0
    total_live = 0
    for source in sources:
        profile = graph_profile(machine.parse_source(source))
        operations += profile["operations"]
        total_depth += profile["depth"]
        total_live += profile["peak_live"]
    return grammar_id, operations, total_depth, total_live


def parallel_decision(repeats: int = 3) -> dict[str, Any]:
    """Where this card uses many cores, where it refuses to, and the measurement behind each.

    Three paths, three separate measurements, and the decision in each case is the recorded number
    rather than a rule of thumb.

    **The structural sweep** (25 worlds x the whole corpus, parsed natively and profiled) is
    CPU-bound Python.  Sequential and process-pooled runs are both timed here, and the pool's
    startup is timed on its own so a reader can see how much of any difference is the pool coming
    up rather than the work going faster.

    **Compilation** is a set of independent external ``clang`` processes.  From Python's side that
    is IO-bound and a thread pool costs nothing, which is measured here rather than assumed.

    **Timing is strictly sequential and that is not an oversight.**  Concurrent load moves clock
    frequency, contends for cache and moves threads between cores.  A parallel timing run would
    change what is measured rather than how fast it is measured, which the repository's multicore
    policy forbids.
    """
    entries = corpus()
    sources = tuple(entry.source for entry in entries)
    grammars = all_grammars()
    jobs = [(grammar.id, sources) for grammar in grammars]
    workers = default_worker_count(len(jobs))

    sequential = []
    for _ in range(repeats):
        started = time.perf_counter()
        results_sequential = [_profile_chunk(job) for job in jobs]
        sequential.append(time.perf_counter() - started)

    pooled = []
    startup = []
    results_pooled: list[tuple[str, int, int, int]] = []
    pool_error: str | None = None
    try:
        for _ in range(repeats):
            started = time.perf_counter()
            with ProcessPoolExecutor(max_workers=workers) as pool:
                ready = time.perf_counter()
                results_pooled = list(pool.map(_profile_chunk, jobs))
            pooled.append(time.perf_counter() - started)
            startup.append(ready - started)
    except Exception as error:  # a caller without a __main__ guard, a sandbox that forbids spawn
        pool_error = f"{type(error).__name__}: {error}"
    if pool_error is not None:
        return {
            "cores_observed": os.cpu_count(),
            "headroom_cores": WORKER_HEADROOM_CORES,
            "structural_sweep": {
                "jobs": len(jobs),
                "workers": workers,
                "sequential_seconds": _timing(sequential).as_dict(),
                "pooled_seconds": None,
                "decision": "sequential",
                "reason": f"a process pool could not be started here: {pool_error}",
            },
            "compilation": {"clang": clang_available(), "skipped": "process pool unavailable"},
            "timing": {
                "decision": "sequential",
                "reason": "concurrent load changes what a stopwatch measures, not how fast it measures",
            },
            "environment": environment(),
        }

    sequential_timing = _timing(sequential)
    pooled_timing = _timing(pooled)
    startup_timing = _timing(startup)

    compilation: dict[str, Any] = {"clang": False}
    if clang_available():
        directory = Path(tempfile.mkdtemp(prefix="parseatlas_native_par_"))
        try:
            machine = build_native(CONTROL, "levels")
            unit = "".join(
                emit_c_function(machine.parse_source(entry.source), f"k_{index}")
                for index, entry in enumerate(entries[:24])
            )
            path = directory / "unit.c"
            path.write_text(unit, encoding="ascii")
            compile_jobs = [
                (name, flags, index)
                for index in range(8)
                for name, flags in CLANG_LEVELS
            ]

            def compile_one(job: tuple[str, tuple[str, ...], int]) -> float:
                name, flags, index = job
                started = time.perf_counter()
                subprocess.run(
                    ["clang", *flags, "-S", "-o", str(directory / f"u_{name}_{index}.s"), str(path)],
                    capture_output=True,
                    check=True,
                )
                return time.perf_counter() - started

            started = time.perf_counter()
            for job in compile_jobs:
                compile_one(job)
            sequential_compile = time.perf_counter() - started

            compile_workers = default_worker_count(len(compile_jobs))
            started = time.perf_counter()
            with ThreadPoolExecutor(max_workers=compile_workers) as pool:
                list(pool.map(compile_one, compile_jobs))
            threaded_compile = time.perf_counter() - started
            compilation = {
                "clang": True,
                "jobs": len(compile_jobs),
                "workers": compile_workers,
                "sequential_seconds": sequential_compile,
                "threaded_seconds": threaded_compile,
                "speedup": sequential_compile / threaded_compile if threaded_compile else None,
                "decision": "threads" if threaded_compile < sequential_compile else "sequential",
            }
        finally:
            shutil.rmtree(directory, ignore_errors=True)

    identical = sorted(results_sequential) == sorted(results_pooled)
    return {
        "cores_observed": os.cpu_count(),
        "headroom_cores": WORKER_HEADROOM_CORES,
        "structural_sweep": {
            "jobs": len(jobs),
            "workers": workers,
            "sequential_seconds": sequential_timing.as_dict(),
            "pooled_seconds": pooled_timing.as_dict(),
            "pool_startup_seconds": startup_timing.as_dict(),
            "seconds_per_cell_sequential": sequential_timing.median / (len(jobs) * len(sources)),
            "seconds_per_cell_pooled": pooled_timing.median / (len(jobs) * len(sources)),
            "results_identical": identical,
            "decision": "processes" if pooled_timing.median < sequential_timing.median else "sequential",
            "startup_share_of_pooled": startup_timing.median / pooled_timing.median
            if pooled_timing.median
            else None,
        },
        "compilation": compilation,
        "timing": {
            "decision": "sequential",
            "reason": "concurrent load changes what a stopwatch measures, not how fast it measures",
        },
        "environment": environment(),
    }


# -------------------------------------------------------------------------------------- report


def native_machines_report(
    *,
    repeats: int = DEFAULT_REPEATS,
    passes: int = DEFAULT_PASSES,
    include_metal: bool = True,
    include_parallel: bool = True,
    include_timing: bool = True,
    repeatability_runs: int = 3,
    sharpest: int = 4,
) -> dict[str, Any]:
    """Every measurement of card 0056, in the order the report reads them.

    Agreement first, because no timing is believed before it holds.  Then the null model - the
    structural half (:func:`machine_isomorphism_audit`) before the timed half - then the noise floor
    that says which timed differences are resolvable at all, then throughput with generation on its
    own line, then the emitted dataflow, then the metal.
    """
    entries = corpus()
    named = named_corpus()
    grammars = all_grammars()

    agreement = agreement_audit(entries, grammars)
    language = language_identity_audit(entries, grammars)
    isomorphism = machine_isomorphism_audit(grammars)
    if not agreement["all_match"]:
        return {
            "stopped": "architectures disagree; that is the finding and no timing follows",
            "agreement": agreement,
            "language_identity": language,
            "environment": environment(),
        }

    dataflow = dataflow_table(entries, grammars)
    invariance = operation_invariance(entries, grammars)
    graphs = distinct_graph_table(entries, grammars)
    # Declared before it is applied: half the objects taken to the compiler come from the named-law
    # corpus and half from the generated sweep family.  Ranking the whole corpus by spread would have
    # returned only the longest generated words and sent no real mathematics to clang.
    half = max(sharpest // 2, 1)
    sharp = sharpest_objects(dataflow, half, "named") + sharpest_objects(dataflow, half, "sweep")

    report: dict[str, Any] = {
        "agreement": agreement,
        "language_identity": language,
        "machine_isomorphism": isomorphism,
        "dataflow": dataflow,
        "operation_invariance": invariance,
        "distinct_graphs": graphs,
        "sharpest_objects": list(sharp),
        "environment": environment(),
    }
    if include_timing:
        report["registry_generation"] = registry_generation_cost(grammars, repeats=repeats)
        report["noise_floor"] = noise_floor(grammars, named, repeats=repeats, passes=passes)
        report["tokenizer_share"] = tokenizer_share(grammars, named, repeats=repeats, passes=passes)
        throughput = throughput_table(named, grammars, repeats=repeats, passes=passes)
        report["throughput"] = throughput
        report["specialisation_control"] = specialisation_control(throughput)
        report["repeatability"] = throughput_repeatability(
            repeatability_runs, named, grammars, repeats=repeats, passes=passes
        )
        report["length_curve"] = length_curve()
    report["bound_attainment"] = bound_attainment()
    report["long_words"] = long_word_check()
    if include_metal:
        report["metal"] = instruction_table(sharp, entries, grammars)
    if include_parallel:
        report["parallel"] = parallel_decision()
    return report
