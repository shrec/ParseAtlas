"""Validation of experiment 0053: the model against the metal.

Every number here was measured before it was written down, and the headlines are pinned as literals
rather than recomputed from the module, so a change in the result fails a test instead of quietly
rewriting the finding.

The file is ordered cheap-first, and the order is not cosmetic.  Three things are checked before any
stopwatch is believed:

* **every emitted function computes what the project's evaluator computes**, over the whole corpus,
  at every optimisation level.  A faster function that computes something else is the failure mode
  the repository exists to prevent, so this test runs before the timing tests and its failure makes
  them meaningless;
* **the emitter is deterministic**, so a timing belongs to a tree and not to a run;
* **the anti-elimination guard works**, measured by compiling the same kernels with the guard removed
  and showing that the loop disappears.  A benchmark that measures an empty loop is the classic
  failure of this kind of work and it is checked here rather than asserted in a docstring.

**The floors declared in this file are not results.**  ``PIN_FLOOR``, ``DECISIVE_CELLS``,
``INDISTINGUISHABLE_CEILING`` and ``AGREEMENT_PIN_FLOOR`` exist only so that a pinned ORDER is
reproducible on a machine that is doing other work, and each was chosen from a repeated run rather
than picked.  The reported results use the measured noise floor and publish a sweep beside it; these
numbers govern the tests and nothing else.

**Several were coin flips and were repaired**, because a bound fitted just past the largest value a
noisy quantity happened to produce fails the next time the machine is busy: the repetition sweep
asserted that its drift curve flattens monotonically, the indistinguishable cells carried seven
per-cell bounds at about 1.5 times their own maxima, and the register cells carried absolute lower
bounds on a gap.  Each is now either a single declared threshold placed between two measured
populations, or a comparison against noise measured in the same run.  Where a quantity is not
resolvable at all, the test asserts nothing about it.

**The rule that came out of this, and it generalises past this file: do not gate on a statistic you
cannot bound -- publish it with its spread.**  The repetition sweep took two attempts to learn it.
Its first repair replaced the monotonicity claim with ``min(tail) < 0.08``, a threshold set just
past the largest value 17 sweeps had produced; review watched that fail one run in five, because
the statistic is heavy-tailed and the "margin" was a sample maximum.  A sample maximum is not a
bound however many samples it is taken over, and the drift now appears in the reports as measured
data with its range and median instead of as an assertion.  A constant that IS defensible -- like
``ticks[-1] > 100 * ticks[0]``, where the step count between those two points differs by a factor
of 1024 -- states its argument from the input and not from the sample.

Every test that needs a compiler is skipped with a readable reason when ``clang`` is absent, and the
skip names the compiler so the skip is visible in the run rather than looking like a pass.
"""

import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

import pytest
from sympy import Symbol, simplify

from parseatlas import canonical as origin_operations
from parseatlas import memory_ceiling as origin_peak_live
from parseatlas import parallel_worlds as origin_depth
from parseatlas import metal
from parseatlas.canonical import to_sympy
from parseatlas.grammar import control_grammar
from parseatlas.metal import (
    CALIBRATION_LEAVES,
    CORPUS,
    DEFAULT_ITERATIONS,
    DEFAULT_TRIALS,
    FLOOR_SWEEP,
    LEVELS,
    LEVEL_BY_NAME,
    MIN_BLOCK_TICKS,
    MODE_AXIS,
    MODEL_AXES,
    MODES,
    PARAMETER_PREFIX,
    PIN_CORE,
    PROBE_PREDICTIONS,
    PUBLISHED_FLOOR,
    REPETITION_SWEEP,
    TABLE_SIZE,
    TOLERANCE,
    Writing,
    _classify,
    _kernel_name,
    _relative_gap,
    _shape_catalogue,
    agreement_table,
    asap_width,
    benchmark,
    clang_available,
    correctness_audit,
    deepest_variable,
    divergence_probes,
    emit_c,
    emit_program,
    emit_statements,
    environment,
    evaluate,
    flag_isolation_audit,
    fma_sites,
    guard_audit,
    harness_calibration,
    input_row,
    instruction_audit,
    latency_path_audit,
    loop_instruction_audit,
    noise_floor,
    parallel_decision,
    peak_live_bound_table,
    probe_repeatability,
    probe_subjects,
    repetition_curve,
    slot_map,
    structural_profile,
    survival_repeatability,
    survival_table,
    tree_of,
    variables_of,
    worker_count_for,
)
from parseatlas.parser import parse

NEEDS_CLANG = pytest.mark.skipif(
    not clang_available(),
    reason="experiment 0053 compiles and runs C: no clang on PATH, so nothing can be measured",
)

#: The floor the probes' MEASURED table is pinned at.
#:
#: **Chosen from the repeatability study, and the study's result is why it is this large.**
#: :func:`parseatlas.metal.probe_repeatability` runs the whole probe set several times and records
#: the smallest and largest relative gap each of the thirty-two cells produced.  Those intervals
#: OVERLAP -- ``probe_division`` in the throughput regime at ``O0`` covers ``30.53%`` to ``36.81%``
#: while ``probe_latency`` in the same regime at ``O2`` covers ``23.85%`` to ``33.11%`` -- so **no
#: single threshold between one and a hundred percent classifies all thirty-two cells the same way
#: twice.**  That is a fact about this machine, and it is reported as one rather than hidden by
#: choosing a threshold and running once.
#:
#: The floor is therefore set high enough that only the three deep-chain latency cells resolve, and
#: it is placed between the two populations rather than just past one of them.
#:
#: **It was ``1.10`` and that was the third coin flip in this file.**  When it was chosen the
#: division probe was measuring about half of what it measures now; re-measurement puts that probe at
#: up to ``106.02%`` in the throughput regime, four points under the old floor, and a contended run
#: duly pushed it over and changed the pinned table.  The two populations either side are now
#: division at no more than ``106.02%`` and the deep-chain latency cells at no less than ``160.83%``,
#: so the floor sits at their geometric mean: ``1.30``, with a margin of about ``1.23`` times above
#: the one and ``1.24`` times below the other.
PIN_FLOOR = 1.30

#: Cells the machine resolved the same way in every run of the repeatability study, with a lower
#: bound on the gap set to roughly six tenths of the smallest gap observed across those runs.
#: Pinning the direction AND a size means a change in either fails.
#:
#: **Re-derived in this revision, because the gaps moved and the margins had quietly closed.**  The
#: rule was always six tenths of the smallest observed gap, but the bounds had been left at values
#: that were only ``1.2`` to ``1.5`` times under the smallest gap now measured -- ``0.25`` against a
#: smallest observed ``30.62%`` in the tightest case.  Each bound below is six tenths of the smallest
#: gap its cell produced over five fresh runs of the whole probe set, restoring the margin the rule
#: was written to give.
#:
#: The two ``probe_fma`` cells are the exception and are held at ``0.08`` rather than lowered to
#: ``0.06``: they are the decisive cells nearest the never-separated population, and the bound must
#: not drop below :data:`INDISTINGUISHABLE_CEILING` or the two sets would no longer be separable by a
#: constant at all.  What keeps that pair honest is the within-run comparison in
#: :func:`test_every_probe_cell_the_machine_never_separated_is_pinned_as_an_upper_bound`, not this
#: number.
#: **Re-derived a second time in this revision, over 30 runs rather than five.**  The tightest of
#: them had closed to ``0.18`` against a smallest observed ``18.48%`` -- a margin of ``1.03`` times,
#: which is a failure waiting for the next busy afternoon.  Each bound below is again six tenths of
#: the smallest gap its cell produced, now over 30 runs of the whole probe set for the cells the
#: longer study covered and 16 for the rest, and the tightest margin left is ``1.30``.  The two
#: ``probe_fma`` bounds stay at ``0.08``: the rule would give ``0.06``, and
#: :func:`test_every_probe_cell_the_machine_never_separated_is_pinned_as_an_upper_bound` requires
#: every decisive bound to sit at or above :data:`INDISTINGUISHABLE_CEILING`.
DECISIVE_CELLS = {
    ("probe_division", "throughput", "O0"): ("separate", 0.11),
    ("probe_division", "throughput", "O2"): ("common_denominator", 0.32),
    ("probe_division", "throughput", "O2nativefma"): ("common_denominator", 0.56),
    ("probe_division", "throughput", "O3fast"): ("common_denominator", 0.57),
    ("probe_fma", "throughput", "O3fast"): ("factored", 0.08),
    ("probe_fma", "latency", "O3fast"): ("expanded", 0.08),
    ("probe_latency", "throughput", "O0"): ("balanced", 0.16),
    ("probe_latency", "latency", "O0"): ("balanced", 0.74),
    ("probe_latency", "latency", "O2"): ("balanced", 0.90),
    ("probe_latency", "latency", "O2nativefma"): ("balanced", 1.28),
}

#: The cells the machine never separated, over the repeatability study.
#:
#: **These were seven per-cell bounds and they were a coin flip; this is the repair.** Each bound was
#: set at about one and a half times the largest gap that cell had produced, which is no margin at
#: all for a quantity that moves with what else the machine is doing: the test failed inside a full
#: suite run and passed on its own minutes later. There is now ONE declared ceiling for all seven,
#: and it is placed in the gap between two measured populations rather than fitted to each cell:
#: over five runs of the whole probe set these cells reached at most ``2.15%`` while the smallest gap
#: any DECISIVE cell produced was ``10.91%``. A ceiling of ``8%`` separates them with a margin of
#: about 3.7 times below and still sits under every decisive cell.
INDISTINGUISHABLE_CEILING = 0.08

INDISTINGUISHABLE_CELLS = (
    ("probe_division", "latency", "O3fast"),
    ("probe_fma", "throughput", "O0"),
    ("probe_fma", "latency", "O0"),
    ("probe_latency", "throughput", "O3fast"),
    ("probe_latency", "latency", "O3fast"),
    ("probe_registers", "throughput", "O3fast"),
    ("probe_registers", "latency", "O3fast"),
)

#: The floor the agreement table's inversion count is pinned at.  Three independent runs gave ``2``
#: at ``0.03``, ``0.05``, ``0.10`` and ``0.20`` and ``3`` at ``0.02``; the largest of those is taken
#: so that the two inversions the count refers to -- both above ``77%`` in every run -- keep the
#: widest margin over anything that might join them.
AGREEMENT_PIN_FLOOR = 0.20

#: **There is deliberately no repetition-sweep drift bound in this file any more.**
#:
#: One stood here at ``0.08``, declared from the largest value 17 sweeps of the curve happened to
#: produce.  Review then watched it fail one run in five, at ``0.08531096563011455 < 0.08``, on a
#: run that was the second-fastest of the five.  Re-measured over 48 sweeps here, the statistic it
#: bounded ranges from ``0.06%`` to ``11.43%`` with a median of ``1.82%`` and crosses ``0.08`` in
#: ``3`` of the ``48``: it is heavy-tailed, so every "bound" ever quoted for it was a sample
#: maximum, and a sample maximum cannot gate a test.
#: The drift figures are published in section 2 of both reports with their range and median, and
#: :func:`test_the_repetition_count_is_read_off_a_swept_curve` asserts only what is deterministic
#: about the choice.  **Do not gate on a statistic you cannot bound; publish it with its spread.**


@pytest.fixture(scope="module")
def probe_result():
    """One probe run, shared by every test that reads it: eight compiled programs and eight runs."""
    if not clang_available():
        pytest.skip("experiment 0053 compiles and runs C: no clang on PATH")
    return divergence_probes(floor=PIN_FLOOR)


@pytest.fixture(scope="module")
def agreement_result():
    """One agreement run, shared by every test that reads it."""
    if not clang_available():
        pytest.skip("experiment 0053 compiles and runs C: no clang on PATH")
    return agreement_table(floor=AGREEMENT_PIN_FLOOR)


ALL_WRITINGS = tuple(item for subject in CORPUS for item in subject.writings)
PROBE_WRITINGS = tuple(item for subject in probe_subjects() for item in subject.writings)


# --------------------------------------------------------------------------- the imported measures


def test_the_three_structural_measures_are_the_imported_objects_not_copies():
    """Identity, not equality: a re-implemented measure must fail this rather than pass an ``==``."""
    import parseatlas.metal as metal

    assert metal.peak_live is origin_peak_live.peak_live
    assert metal.depth is origin_depth.depth
    assert metal.operation_cost is origin_operations.operation_cost


def test_structural_profile_reads_operations_as_the_project_counts_them():
    """``operations`` is the sum of the four operator counts, with ``/`` weighted exactly as ``*``.

    That equal weighting is the premise the first divergence attacks, so it is pinned rather than
    left implicit in a sum.
    """
    tree = tree_of("a / b + c * d")
    cost = origin_operations.operation_cost(tree)
    profile = structural_profile(tree)
    assert profile["operations"] == cost["add"] + cost["sub"] + cost["mul"] + cost["div"]
    assert profile["operations"] == 3
    assert profile["div"] == 1 and profile["mul"] == 1


def test_asap_width_and_fma_sites_are_this_cards_own_and_not_project_measures():
    """The two extra measures exist to explain a disagreement, and their values are pinned."""
    chained = tree_of("a + b + c + d")
    balanced = tree_of("(a + b) + (c + d)")
    assert (asap_width(chained), asap_width(balanced)) == (1, 2)
    assert structural_profile(chained)["operations"] == structural_profile(balanced)["operations"]
    assert fma_sites(tree_of("a * b + c")) == 1
    assert fma_sites(tree_of("(a + b) * c")) == 0


# ------------------------------------------------------------------------------- the corpus itself


def test_every_writing_of_a_subject_denotes_the_same_object():
    """The corpus claims equivalence; SymPy checks it rather than the claim being trusted."""
    for subject in CORPUS + probe_subjects():
        expressions = [simplify(to_sympy(tree_of(item.source))) for item in subject.writings]
        for other in expressions[1:]:
            assert simplify(expressions[0] - other) == 0, subject.name


def test_the_corpus_is_the_declared_size():
    assert len(CORPUS) == 16
    assert len(ALL_WRITINGS) == 34


def test_the_probe_set_is_four_pairs():
    subjects = probe_subjects()
    assert len(subjects) == 4
    assert tuple(item.name for item in subjects) == (
        "probe_division",
        "probe_fma",
        "probe_latency",
        "probe_registers",
    )
    assert all(len(item.writings) == 2 for item in subjects)


def test_each_probe_holds_fixed_what_it_claims_to_hold_fixed():
    """The probes are designed pairs, so what each pair controls for is pinned."""
    profiles = {
        subject.name: [structural_profile(tree_of(item.source)) for item in subject.writings]
        for subject in probe_subjects()
    }

    division = profiles["probe_division"]
    assert [item["operations"] for item in division] == [3, 5]
    assert [item["div"] for item in division] == [2, 1]

    fusion = profiles["probe_fma"]
    assert [item["operations"] for item in fusion] == [31, 31]
    assert [item["depth"] for item in fusion] == [5, 5]
    assert [item["peak_live"] for item in fusion] == [6, 6]
    assert [item["asap_width"] for item in fusion] == [16, 16]
    assert [item["fma_sites"] for item in fusion] == [8, 16]

    latency = profiles["probe_latency"]
    assert [item["operations"] for item in latency] == [15, 15]
    assert [item["depth"] for item in latency] == [15, 4]

    registers = profiles["probe_registers"]
    assert [item["operations"] for item in registers] == [39, 39]
    assert [item["depth"] for item in registers] == [9, 9]
    assert [item["peak_live"] for item in registers] == [3, 6]
    assert [item["asap_width"] for item in registers] == [9, 17]


# ------------------------------------------------------------------------------------ the emitter


def test_the_emitter_is_deterministic_byte_for_byte():
    """The same tree gives byte-identical source, twice, and through two independent parses."""
    for writing in ALL_WRITINGS + PROBE_WRITINGS:
        first = emit_c(parse(writing.source, control_grammar()), "kernel")
        second = emit_c(parse(writing.source, control_grammar()), "kernel")
        assert first == second
        assert first == emit_c(tree_of(writing.source), "kernel")


def test_the_emitted_signature_depends_on_the_tree_and_not_on_the_writing_order():
    """Two sources with the same variables in different order emit the same parameter list."""
    first = emit_c(tree_of("b * a + c"), "kernel")
    second = emit_c(tree_of("c + a * b"), "kernel")
    head = f"static double kernel(double {PARAMETER_PREFIX}a, double {PARAMETER_PREFIX}b, double {PARAMETER_PREFIX}c)"
    assert first.startswith(head)
    assert second.startswith(head)


def test_the_emitter_writes_one_operation_per_statement():
    """One C statement per internal tree node: the operation count is countable from the source."""
    for writing in ALL_WRITINGS:
        tree = tree_of(writing.source)
        lines, result = emit_statements(tree)
        assert len(lines) == structural_profile(tree)["operations"]
        assert all(line.count(" = ") == 1 for line in lines)
        assert result == f"t{len(lines) - 1}" if lines else True


def test_the_emitter_refuses_an_illegal_function_name():
    with pytest.raises(ValueError, match="legal C function name"):
        emit_c(tree_of("a + b"), "not a name")


def test_a_leafless_tree_still_emits_a_legal_function():
    """A degenerate dataflow graph is emitted rather than silently excluded from the corpus."""
    assert emit_c(tree_of("a"), "kernel").splitlines()[-2].strip() == f"return {PARAMETER_PREFIX}a;"


def test_the_program_carries_one_duplicate_kernel_per_subject_when_asked():
    source, names = emit_program(ALL_WRITINGS, "throughput", duplicate=True)
    assert sum(1 for name in names if name.endswith("__dup")) == len(CORPUS)
    assert len(names) == len(ALL_WRITINGS) + len(CORPUS)
    assert "volatile double PA_SINK" in source


def test_the_latency_kernel_feeds_exactly_one_variable():
    """The feedback goes into one deep leaf.  Feeding all of them let ``-ffast-math`` cancel it."""
    source, _ = emit_program((Writing("t", "r", "(x - h) * (x - h)"),), "latency")
    assert source.count("+ fb;") == 1
    assert "double fb = acc * 1e-18;" in source


def test_the_fed_leaf_sits_at_the_full_depth_of_every_tree_in_the_corpus():
    audit = latency_path_audit()
    assert audit["writing_count"] == 42
    assert audit["all_full_depth"] is True
    assert audit["at_full_depth"] == 42


def test_deepest_variable_ignores_a_constant_leaf():
    """The fed leaf must be a variable; a literal cannot carry a loop-carried dependency."""
    name, leaf_depth, tree_depth = deepest_variable(tree_of("2 * x * x + 3 * x - 5"))
    assert name == "x"
    assert leaf_depth == tree_depth


def test_the_latency_regime_refuses_a_tree_with_no_variable():
    with pytest.raises(ValueError, match="at least one variable"):
        emit_program((Writing("t", "r", "2 + 3"),), "latency")


# ------------------------------------------------------------------------------------- the oracle


def test_the_oracle_is_exact_and_uses_the_double_a_constant_rounds_to():
    """No rounding on the oracle's side, so the whole deviation reported is the machine's."""
    inputs = {"x": Fraction(5, 4)}
    assert evaluate(tree_of("x * x + 1/2"), inputs) == Fraction(33, 16)
    assert isinstance(evaluate(tree_of("x / 3"), inputs), Fraction)


def test_the_oracle_refuses_a_missing_input_and_a_zero_denominator():
    with pytest.raises(KeyError, match="no declared input"):
        evaluate(tree_of("a + b"), {"a": Fraction(1)})
    with pytest.raises(ZeroDivisionError, match="denominator zero"):
        evaluate(tree_of("a / b"), {"a": Fraction(1), "b": Fraction(0)})


def test_every_declared_input_is_an_exact_double_and_no_two_variables_share_a_base():
    slots = slot_map(ALL_WRITINGS + PROBE_WRITINGS)
    row = input_row(slots, 0)
    assert len(set(row.values())) == len(row)
    for value in input_row(slots, TABLE_SIZE - 1).values():
        assert Fraction(float(value)) == value
        assert value >= 1


def test_no_declared_input_makes_a_denominator_zero_anywhere_in_the_corpus():
    slots = slot_map(ALL_WRITINGS + PROBE_WRITINGS)
    for row in range(TABLE_SIZE):
        inputs = input_row(slots, row)
        for writing in ALL_WRITINGS + PROBE_WRITINGS:
            evaluate(tree_of(writing.source), inputs)


# ------------------------------------------------------------------- the shape catalogue and bound


def test_the_shape_catalogue_agrees_with_the_imported_measures_on_every_witness():
    """Each witness is checked against 0041's depth and 0044's peak live, never against the table."""
    from parseatlas.metal import _balanced_source, _leaf_names, _shape_source

    assert _balanced_source(("a", "b"), "+") == "(a + b)"
    for leaves in (4, 8, 12):
        names = _leaf_names(leaves)
        for (table_depth, table_peak), shape in _shape_catalogue(leaves).items():
            tree = tree_of(_shape_source(shape, names))
            assert origin_depth.depth(tree) == table_depth
            assert origin_peak_live.peak_live(tree) == table_peak


def test_peak_live_cannot_reach_the_register_file_at_any_practical_size():
    """The fourth axis is bounded by ``floor(log2(leaves)) + 1``, swept rather than assumed."""
    table = peak_live_bound_table()
    assert table["bound_holds"] is True
    assert table["architectural_xmm_registers"] == 16
    assert table["leaves_needed_to_exceed_registers"] == 65536
    assert [row["spread"] for row in table["rows"]] == [0, 1, 1, 2, 2, 2, 3, 3]
    assert [row["max_peak_live_any_depth"] for row in table["rows"]] == [4, 4, 5, 5, 5, 6, 6, 6]


# --------------------------------------------------------------------------------- the environment


@NEEDS_CLANG
def test_the_environment_is_recorded_with_every_number():
    recorded = environment()
    assert recorded["clang"].startswith("clang version")
    assert recorded["machine"] == "AMD64"
    assert recorded["logical_cores"] and recorded["logical_cores"] >= 1


def test_worker_counts_come_from_the_observed_core_count_with_headroom():
    assert worker_count_for(16, 8) == 8
    assert worker_count_for(16, 64) == 12
    assert worker_count_for(2, 8) == 1


# ------------------------------------------------------------- correctness, before any timing


@NEEDS_CLANG
def test_every_emitted_function_agrees_with_the_project_evaluator_at_every_level():
    """The whole corpus, the probes included, at all four optimisation levels."""
    audit = correctness_audit(writings=ALL_WRITINGS + PROBE_WRITINGS)
    assert audit["all_match"] is True
    assert audit["writing_count"] == 42
    assert audit["rows"] == 8
    assert len(audit["levels"]) == len(LEVELS)
    assert all(entry["checked"] == 42 * 8 for entry in audit["levels"])
    assert audit["max_relative_deviation"] < float(TOLERANCE)
    # The observed deviation is rounding and nothing else: six orders of magnitude of margin.
    assert audit["max_relative_deviation"] < 1e-13


@NEEDS_CLANG
def test_a_deliberately_wrong_emission_is_caught_by_the_correctness_audit(monkeypatch):
    """The audit must be able to FAIL, and it must fail AT EVERY LEVEL, not only at the first.

    **This test is a repair, and the defect it repairs is a recorded project rule.** The version
    review first found was named exactly as it is now and its docstring already said "a check that
    cannot fail proves nothing" -- and then it built a CORRECT writing and asserted ``all_match is
    True``. On an isolated copy the reviewer replaced one line of :func:`correctness_audit` so that
    it compared the C output against itself, and all 65 tests passed; changing ``if deviation >
    TOLERANCE:`` to ``if False:`` also left 65 passing. ROADMAP.md carries the rule under "Every
    gate needs a test that it can FIRE", and 0053 is the third card listed there.

    **The first repair was still one level deep, and review caught that too.** It ran the control at
    ``levels=(LEVEL_BY_NAME["O0"],)`` only, so it could not see a gate that silently dropped the
    other three: mutating ``all_match``'s ``per_level`` to ``per_level[:1]`` -- which blinds the gate
    to ``-O2``, ``-O2 -march=native -ffp-contract=fast`` and ``-O3 -ffast-math``, the last of them
    the ``-ffast-math`` rung the report says the audit exists to check -- left all 71 tests passing.
    **That is the same failure twice inside one card: a control that could not see the failure.**
    The control now runs at all four ``LEVELS`` and asserts each level's own failure list, and
    :func:`test_the_correctness_gate_fires_when_only_one_level_is_wrong` makes exactly one level
    wrong at a time so that dropping any level from the aggregate is fatal.

    The corpus cannot supply a wrong emission, because the audit computes both sides from the same
    ``Writing.source``: whatever that string says, the oracle evaluates it and the emitter writes
    it, so they agree by construction. That is the case ROADMAP.md's rule anticipates -- *"where a
    corrupted input cannot be constructed because the check is self-consistent by design, the
    dependency is replaced for the duration of the test instead"* -- so the emitter is replaced with
    one that writes ``b - a`` where the writing says ``a - b``.

    Everything else is the published path: the same :func:`correctness_audit`, the same clang, the
    same comparison against the exact-rational oracle, the same ``all_match`` and ``failures`` the
    report quotes and :func:`metal_report` gates on.
    """
    honest = (Writing("control", "honest", "a - b"),)

    # The two functions really are different on the inputs the audit uses, so a failure below is
    # the corruption and cannot be rounding.
    inputs = input_row(slot_map(honest), 0)
    assert evaluate(tree_of("b - a"), inputs) != evaluate(tree_of("a - b"), inputs)

    # 1. The audit PASSES on the honest emission, AT EVERY LEVEL.  Without this half, a broken
    #    audit that failed everything would also satisfy the half below.
    clean = correctness_audit(writings=honest, rows=2)
    assert clean["all_match"] is True
    assert [entry["level"] for entry in clean["levels"]] == [level.name for level in LEVELS]
    assert [entry["failures"] for entry in clean["levels"]] == [[] for _ in LEVELS]
    assert [entry["checked"] for entry in clean["levels"]] == [2 for _ in LEVELS]

    # 2. The emitter now writes a DIFFERENT function while the oracle keeps evaluating the declared
    #    source.  The variables are the same two, so the input table, the slot map, the kernel name
    #    and the call site are all unchanged -- only the value computed moves.
    real_emitter = metal.emit_check_program

    def emit_something_else(writings, rows):
        return real_emitter(
            tuple(Writing(item.subject, item.role, "b - a") for item in writings), rows
        )

    monkeypatch.setattr(metal, "emit_check_program", emit_something_else)
    caught = correctness_audit(writings=honest, rows=2)

    assert caught["all_match"] is False, "the correctness gate did not fire on a wrong emission"
    assert [entry["level"] for entry in caught["levels"]] == [level.name for level in LEVELS]
    # Asserted PER LEVEL and not only on the aggregate: each of the four compiled a wrong function,
    # checked both rows and reported both as failures naming the kernel they came from.
    for entry in caught["levels"]:
        assert entry["checked"] == 2, entry["level"]
        assert len(entry["failures"]) == 2, entry["level"]
        assert {item["kernel"] for item in entry["failures"]} == {"k_control__honest"}, entry["level"]
        assert sorted(item["row"] for item in entry["failures"]) == [0, 1], entry["level"]
        # a - b against b - a is a relative deviation of exactly 2 -- nine orders of magnitude above
        # the declared tolerance, so no plausible loosening of TOLERANCE hides it.
        assert entry["failures"][0]["deviation"] == pytest.approx(2.0), entry["level"]
    assert caught["max_relative_deviation"] > 1e9 * float(TOLERANCE)


@NEEDS_CLANG
@pytest.mark.parametrize("wrong_level", [level.name for level in LEVELS])
def test_the_correctness_gate_fires_when_only_one_level_is_wrong(monkeypatch, wrong_level):
    """One level wrong at a time, so that dropping ANY level from the gate is fatal.

    **This is the test that kills ``per_level[:1]``**, and it exists because review applied exactly
    that mutation to :func:`correctness_audit`'s ``all_match`` on an isolated copy and the whole
    file still passed. A control in which every level is wrong cannot see a truncated aggregate,
    because the level that survives the truncation is wrong too -- which is why the test above,
    correct as far as it goes, is not sufficient on its own.

    So the corruption is made level-specific. The honest program is emitted once, as always, and
    :func:`parseatlas.metal.compile_program` is replaced for the duration of the test with one that
    substitutes a program computing ``b - a`` for exactly one level's binary. The audit names each
    binary ``check_<level>``, so the substitution keys on the name the audit itself chose and no
    other machinery is touched: the same emitter, the same clang, the same flags, the same
    exact-rational oracle, the same ``all_match`` the report gates on.

    With the corruption at ``O2``, ``O2nativefma`` or ``O3fast``, an aggregate computed over
    ``per_level[:1]`` reports ``all_match is True`` while a level is failing, and this test fails.
    """
    honest = (Writing("control", "honest", "a - b"),)
    corrupt_source = metal.emit_check_program((Writing("control", "honest", "b - a"),), 2)
    real_compile = metal.compile_program
    compiled = []

    def compile_one_level_wrong(source, flags, workdir, stem):
        compiled.append(stem)
        substitute = stem == f"check_{wrong_level}"
        return real_compile(corrupt_source if substitute else source, flags, workdir, stem)

    monkeypatch.setattr(metal, "compile_program", compile_one_level_wrong)
    audit = correctness_audit(writings=honest, rows=2)

    # All four levels were compiled, in order, and exactly one of them got the substitute.
    assert compiled == [f"check_{level.name}" for level in LEVELS]

    failing = [entry for entry in audit["levels"] if entry["failures"]]
    assert [entry["level"] for entry in failing] == [wrong_level]
    assert len(failing[0]["failures"]) == 2
    assert {item["kernel"] for item in failing[0]["failures"]} == {"k_control__honest"}
    assert failing[0]["failures"][0]["deviation"] == pytest.approx(2.0)
    # Every other level is clean, so what fires below is the substituted level and nothing else.
    assert [entry["failures"] for entry in audit["levels"] if entry["level"] != wrong_level] == [
        [] for _ in LEVELS[1:]
    ]
    # And the aggregate the report gates on sees it.  A gate that reads only some of the levels
    # returns True here for three of the four parameters.
    assert (
        audit["all_match"] is False
    ), f"the correctness gate did not fire when only {wrong_level} was wrong"


@NEEDS_CLANG
def test_the_report_refuses_to_publish_a_timing_when_the_correctness_gate_fires(monkeypatch):
    """The gate is wired to the published number, not merely capable of returning False.

    ROADMAP.md's rule has a second half -- the control must go through the same path the published
    number goes through, and 0051 needed two attempts because its first control tested the function
    underneath the audit rather than the audit the report reads. Here the audit is made to fail and
    :func:`metal_report` must raise **before** any benchmark runs, which is checked by making the
    benchmark itself explode if it is ever reached.
    """
    monkeypatch.setattr(
        metal,
        "correctness_audit",
        lambda **_: {"all_match": False, "levels": [{"level": "O0", "failures": [{"kernel": "x"}]}]},
    )

    def must_not_run(*_args, **_kwargs):
        raise AssertionError("a timing was started after the correctness gate had already failed")

    monkeypatch.setattr(metal, "benchmark", must_not_run)
    with pytest.raises(RuntimeError, match="disagrees with the oracle"):
        metal.metal_report()


# ------------------------------------------------------------------------ the anti-elimination guard


@NEEDS_CLANG
def test_the_guard_is_what_keeps_the_loop_alive():
    """Without the guard the loop is deleted; with it, it runs.  Measured, not asserted."""
    audit = guard_audit(writings=ALL_WRITINGS, level="O2", iterations=262144, trials=9)
    assert audit["kernel_count"] == len(ALL_WRITINGS)
    assert audit["guard_works"] is True
    # The dead variant is not merely faster: its loop is gone, so it costs no measurable time.
    assert audit["max_ratio"] < 0.01
    assert all(row["guarded_seconds_per_step"] > 0 for row in audit["rows"])


@NEEDS_CLANG
def test_a_kernel_whose_loop_was_eliminated_is_refused_rather_than_ranked():
    """The alarm for the failure this harness exists to avoid, checked on a dead program."""
    run = benchmark(ALL_WRITINGS, "O2", iterations=262144, trials=5, guard=False)
    assert len(run["eliminated"]) == len(ALL_WRITINGS)
    with pytest.raises(RuntimeError, match="loop was eliminated"):
        noise_floor([run])


@NEEDS_CLANG
def test_min_block_ticks_is_read_from_the_timer_and_not_invented():
    run = benchmark(ALL_WRITINGS[:2], "O2", iterations=262144, trials=5)
    assert run["timer_frequency_hz"] > 0
    assert run["eliminated"] == []
    assert all(run["results"][name]["median_ticks"] > MIN_BLOCK_TICKS for name in run["kernels"])
    assert run["affinity_set"] is True
    assert run["priority_raised"] is True
    assert run["pinned_core"] == PIN_CORE


# --------------------------------------------------------------------------- the benchmark itself


@NEEDS_CLANG
def test_a_benchmark_reports_a_median_with_a_band_and_never_one_timing():
    run = benchmark(ALL_WRITINGS[:4], "O2", iterations=65536, trials=9)
    for name in run["kernels"]:
        entry = run["results"][name]
        assert entry["trials"] == 9
        assert entry["p10"] <= entry["median"] <= entry["p90"]
        assert entry["minimum"] <= entry["median"] <= entry["maximum"]
        assert entry["checksum_stable"] is True


@NEEDS_CLANG
def test_the_throughput_loop_advances_four_independent_steps_so_the_count_is_rounded_up():
    run = benchmark(ALL_WRITINGS[:2], "O2", mode="throughput", iterations=65535, trials=3)
    assert run["iterations"] == 65536
    run = benchmark(ALL_WRITINGS[:2], "O2", mode="latency", iterations=65535, trials=3)
    assert run["iterations"] == 65535


def test_a_benchmark_refuses_an_unknown_mode_and_an_empty_corpus():
    with pytest.raises(ValueError, match="unknown mode"):
        emit_program(ALL_WRITINGS[:1], "sideways")
    with pytest.raises(ValueError, match="at least one writing"):
        emit_program((), "throughput")


@NEEDS_CLANG
def test_the_repetition_count_is_read_off_a_swept_curve():
    """No declared repetition count: the sweep is run and the count is a point on it.

    **This test is a repair, and it is the SECOND repair of the same test.** The first version
    asserted ``consecutive_drift[-1] < consecutive_drift[0]``, a comparison of two noise-dominated
    quantities, and failed 3 of 5 standalone re-runs. The second replaced it with
    ``min(tail) < 0.08`` -- a bound taken from the largest value 17 sweeps happened to produce --
    and review then watched it FAIL one run in five, at ``0.08531096563011455 < 0.08``, on a run
    that was the second-FASTEST of the five and so was not contention.

    **The reason is that the statistic is heavy-tailed, so the quoted margin was a sample maximum
    and not a bound.** Over 48 sweeps of this curve run here, that minimum ranged from 0.06% to
    11.43% with a median of 1.82%, it crossed the retired 8% threshold in 3 of the 48, and
    individual drifts inside a sweep reached 73.13%. A sample maximum cannot gate a test, however
    many samples it is taken over.

    **So the drift is published rather than asserted**, in section 2 of both reports, with its
    observed range and its median beside it. What this test asserts is only what is deterministic
    about the choice, and each of the three holds every run or the code is broken:

    * the chosen count is a point ON the swept curve and is not its last point, so the points past
      it had every opportunity to contradict the choice -- this costs no measurement at all;
    * the sweep visits exactly the declared counts;
    * the timed block grows with the repetition count. That is a monotone relationship in the
      INPUT, not in the noise: the step count quadruples between consecutive points, so a
      violation would need the per-step cost to rise fourfold as the block gets longer, which is
      the opposite of the fixed per-block overhead the sweep exists to amortise.

    The one inequality with a constant in it, ``ticks[-1] > 100 * ticks[0]``, is a bound and not a
    sample maximum: the last block runs 1024 times as many steps as the first, so crossing it needs
    the per-step cost at 4194304 steps to exceed ten times the per-step cost at 4096 steps. The
    ratio came back between 551 and 1191 over 48 sweeps, but the argument for the constant is the
    step counts and not that range.
    """
    # The discipline claim itself, and it costs no measurement: the chosen count is a point ON the
    # swept curve rather than a number someone typed, and the sweep continues past it.
    assert DEFAULT_ITERATIONS in REPETITION_SWEEP
    assert DEFAULT_ITERATIONS != REPETITION_SWEEP[-1]

    curve = repetition_curve(writings=ALL_WRITINGS[:6], level="O2", trials=15)
    assert [point["iterations"] for point in curve["points"]] == list(REPETITION_SWEEP)

    # The block length grows with the repetition count.  Arithmetic, not noise: see the docstring.
    ticks = [point["ticks_per_block"] for point in curve["points"]]
    assert ticks == sorted(ticks)
    assert ticks[-1] > 100 * ticks[0]

    # The drift vector is produced and has the shape the report reads, and NOTHING is asserted
    # about its values.  ``consecutive_drift[i]`` compares points ``i`` and ``i+1``; the drifts at
    # or past the chosen count start at ``chosen - 1`` and there are three of them.  Their sizes
    # are published data, measured over 48 sweeps, and are not a gate.
    chosen = list(REPETITION_SWEEP).index(DEFAULT_ITERATIONS)
    assert len(curve["consecutive_drift"]) == len(REPETITION_SWEEP) - 1
    assert len(curve["consecutive_drift"][chosen - 1 :]) == 3
    assert all(value >= 0 for value in curve["consecutive_drift"])


@NEEDS_CLANG
def test_the_harness_floor_is_measured_so_that_the_dilution_is_a_number():
    """A kernel with no arithmetic at all gives the loop's own cost."""
    calibration = harness_calibration(level="O2", mode="throughput", iterations=262144, trials=15)
    assert [point["operations"] for point in calibration["points"]] == [
        count - 1 for count in CALIBRATION_LEAVES
    ]
    assert calibration["points"][0]["operations"] == 0
    assert calibration["fitted_against"] == MODE_AXIS["throughput"]
    assert calibration["slope_seconds_per_unit"] > 0
    assert calibration["zero_operation_seconds"] > 0


# ---------------------------------------------------------------------------- the noise floor


@NEEDS_CLANG
def test_the_noise_floor_is_measured_between_kernels_that_are_byte_identical_c():
    run = benchmark(ALL_WRITINGS, "O2", iterations=262144, trials=21, duplicate=True)
    floor = noise_floor([run])
    assert floor["pair_count"] == len(CORPUS)
    assert floor["median"] <= floor["p90"] <= floor["p95"] <= floor["maximum"]
    assert floor["floor"] == floor["p95"]
    # A quiet run separates two identical kernels by well under a tenth of the smallest effect the
    # probes report; the p95 is the declared floor and the maximum is reported beside it.
    assert floor["median"] < 0.05


@NEEDS_CLANG
def test_the_noise_floor_needs_duplicates_and_says_so():
    run = benchmark(ALL_WRITINGS[:2], "O2", iterations=65536, trials=3, duplicate=False)
    with pytest.raises(ValueError, match="duplicate=True"):
        noise_floor([run])


# ---------------------------------------------------------------------------- flag isolation


@NEEDS_CLANG
def test_the_o2nativefma_rung_varies_two_things_and_the_isolation_audit_names_them():
    """The rung's flags, measured one at a time.

    **This test exists because the module used to lie about this rung.** It was called ``O2fma``
    and its docstring said "The ONLY difference from ``O2`` is fusion", while it carried
    ``-march=native`` as well. Review measured the two flags separately and the module now reports
    what each one does.
    """
    audit = flag_isolation_audit(mode="throughput")
    assert audit["kernels"] == 34
    rows = audit["by_combination"]

    # The fusion flag on its own is INERT: every kernel keeps the -O2 instruction multiset, and not
    # one fused multiply-add appears.  There is no noise floor here -- two multisets are equal or
    # they are not.
    assert rows["O2contract"]["changed_from_baseline"] == 0
    assert rows["O2contract"]["fma"] == 0
    assert rows["O2contract"]["instructions"] == rows["O2"]["instructions"]
    assert audit["contract_alone_changes_nothing"] is True

    # The ISA flag on its own fuses NOTHING, and yet rewrites every kernel: VEX encodings appear
    # and the packed count moves.  This is the confound the old name hid.
    assert rows["O2native"]["changed_from_baseline"] == 34
    assert rows["O2native"]["fma"] == 0
    assert rows["O2native"]["vex"] == 1542
    assert rows["O2"]["packed"] == 1072
    assert rows["O2native"]["packed"] == 1246
    assert audit["isa_alone_fuses_nothing"] is True

    # Only both together fuse.
    assert rows["O2nativefma"]["fma"] == 191
    assert rows["O2nativefma"]["changed_from_baseline"] == 34

    # And the split the review offered as an alternative is not available: -mfma is the narrowest
    # switch that makes an FMA instruction reachable at all, and it already changes all 34 kernels
    # while emitting zero FMAs.  There is no flag that adds fusion and changes nothing else.
    assert rows["O2mfma"]["fma"] == 0
    assert rows["O2mfma"]["changed_from_baseline"] == 34
    assert rows["O2mfmacontract"]["fma"] > 0
    assert audit["separable"] is False


@NEEDS_CLANG
def test_the_separability_verdict_is_a_predicate_that_can_return_true():
    """The negative control for ``separable``: a case it must accept, so ``False`` means something.

    ``separable`` is ``False`` on every real flag combination, and a predicate that is False on
    everything it is ever shown is indistinguishable from ``return False``. So it is handed a
    baseline that ALREADY fuses -- the rung's own flags in the baseline slot -- against a
    combination identical to it. That combination adds no change and carries FMAs, which is exactly
    the shape ``separable`` is looking for, and it must say so.
    """
    fused = ("-O2", "-march=native", "-ffp-contract=fast")
    audit = flag_isolation_audit(
        mode="throughput", combinations={"O2": fused, "same": fused}
    )
    assert audit["by_combination"]["same"]["changed_from_baseline"] == 0
    assert audit["by_combination"]["same"]["identical_to_baseline"] == audit["kernels"]
    assert audit["by_combination"]["same"]["fma"] > 0
    assert audit["separable"] is True
    # The two named verdicts are absent rather than fabricated when their combinations are not run.
    assert audit["contract_alone_changes_nothing"] is None
    assert audit["isa_alone_fuses_nothing"] is None


def test_the_isolation_audit_refuses_to_run_without_its_baseline():
    with pytest.raises(ValueError, match="baseline"):
        flag_isolation_audit(combinations={"O3fast": ("-O3",)})


# ------------------------------------------------------------------ the survival count as a range


@NEEDS_CLANG
def test_the_survival_count_is_reported_as_a_range_over_repeated_runs():
    """The timing half is re-measured rather than read once, and the range is what is published.

    **This test exists because review could not reproduce this card's headline.** The first
    revision opened with ``54`` of ``64`` cells reaching the metal; three quiet re-runs returned
    ``46``, ``47`` and ``49``. A count that moves by that much between runs is reported as a range
    or not at all.
    """
    study = survival_repeatability(
        repeats=3,
        levels=(LEVEL_BY_NAME["O2"],),
        modes=("throughput",),
        floor=PUBLISHED_FLOOR,
        iterations=65536,
        trials=15,
    )
    assert study["repeats"] == 3
    assert len(study["total_reaching_per_repeat"]) == 3
    (row,) = study["rows"]
    assert row["level"] == "O2" and row["mode"] == "throughput"
    assert row["subjects"] == len(CORPUS)
    assert row["floor"] == PUBLISHED_FLOOR
    assert len(row["reaching_every_run"]) == 3
    # The range is a range: the summary statistics bracket every reading rather than replacing them.
    assert row["reaching_min"] <= row["reaching_median"] <= row["reaching_max"]
    assert row["reaching_min"] == min(row["reaching_every_run"])
    assert row["reaching_max"] == max(row["reaching_every_run"])
    assert row["collapsed_min"] + row["reaching_max"] == row["subjects"]
    # ``stable`` is read off the readings and is not a declared property of the cell.
    assert row["stable"] == (len(set(row["reaching_every_run"])) == 1)
    # How quiet the machine was is measured in the same runs, by kernels that are byte-identical C.
    assert study["quietness"]["identical_kernel_worst_gap"] >= study["quietness"][
        "identical_kernel_median_gap"
    ]
    assert len(study["quietness"]["runs"]) == 3


def test_the_survival_range_refuses_a_single_run():
    with pytest.raises(ValueError, match="at least two runs"):
        survival_repeatability(repeats=1)


# ------------------------------------------------------------------------- the instruction audit


@NEEDS_CLANG
def test_the_instruction_audit_pins_how_much_the_compiler_erases():
    """Noise-free evidence: two writings that compile to the same instructions are the same code."""
    audit = instruction_audit()
    assert audit["subjects_compared"] == 16
    assert audit["identical_by_level"] == {"O0": 3, "O2": 0, "O2nativefma": 0, "O3fast": 8}
    identical = {item["subject"] for item in audit["collapse"] if item["level"] == "O3fast" and item["identical"]}
    assert identical == {
        "binomial_square",
        "difference_quotient",
        "distributive_law",
        "line",
        "linear_approximation",
        "product_chain_8",
        "sum_chain_8",
        "trapezoid_area",
    }



@NEEDS_CLANG
def test_the_multiply_column_the_report_prints_is_split_into_scalar_and_packed():
    """The headline table's column was labelled ``mulsd`` and counted ``mulpd`` too.

    **This test is a repair.** ``instruction_audit``'s ``multiply`` field has always matched
    ``v?mul[sp]d``, so it counted packed multiplies beside scalar ones; both reports printed it in
    the opening table under the heading ``mulsd`` and the sentence above the table called it "the
    scalar multiplies among them". Two of the six rows were wrong under their own header. Review
    recompiled ``circle/center_radius`` at ``-O2`` and got zero ``mulsd`` and one ``mulpd`` against
    the table's ``1``, and ``parabola/standard`` came back ``2`` scalar and ``2`` packed against the
    table's ``4``.

    The six rows are pinned here as ``(instructions, mulsd, mulpd)`` so the table and the number
    cannot drift apart again, and the invariant that ``multiply`` is exactly their sum is checked at
    every level rather than assumed from the regex.
    """
    audit = instruction_audit()
    assert audit["writings_compared"] == 34

    at_o2 = {(row["subject"], row["role"]): row for row in audit["rows"] if row["level"] == "O2"}
    headline = {
        key: (row["instructions"], row["multiply_scalar"], row["multiply_packed"])
        for key, row in at_o2.items()
        if key[0] in {"circle", "parabola", "binomial_square"}
    }
    assert headline == {
        ("circle", "center_radius"): (8, 0, 1),
        ("circle", "general"): (16, 6, 0),
        ("parabola", "vertex"): (5, 2, 0),
        ("parabola", "standard"): (15, 2, 2),
        ("binomial_square", "factored"): (3, 1, 0),
        ("binomial_square", "expanded"): (8, 3, 0),
    }

    # The old column was the sum of the two new ones, at every level and for every writing, which
    # is why it could be printed as either without the arithmetic ever complaining.
    assert all(
        row["multiply"] == row["multiply_scalar"] + row["multiply_packed"] for row in audit["rows"]
    )
    assert audit["multiply_scalar_by_level"] == {"O0": 93, "O2": 66, "O2nativefma": 54, "O3fast": 46}
    assert audit["multiply_packed_by_level"] == {"O0": 0, "O2": 10, "O2nativefma": 0, "O3fast": 0}


@NEEDS_CLANG
def test_ordinary_o2_is_where_the_compiler_vectorises_this_corpus():
    """What the mislabelled column was hiding: clang puts some writings in a vector register.

    ``center_radius`` is not merely the shorter writing of the circle -- ``8`` instructions against
    ``16`` -- it is the one clang vectorised, and the ``mulpd`` the table printed as ``mulsd`` was
    the evidence. Counted over the whole corpus, ``packed_arithmetic`` (packed ADD, SUB, MUL and
    DIV, as opposed to the ``movapd`` and ``unpcklpd`` shuffling around them) is non-zero in ``8``
    of the ``34`` writings at ``-O2``, in ``2`` at ``-O2nativefma`` and in ``1`` at ``-O3fast``.

    That ordering is the surprise and it is pinned rather than narrated: ORDINARY ``-O2``
    vectorises more of this corpus than either of the rungs above it, because from
    ``-march=native`` upwards the surviving packed arithmetic is a single ``vdivpd`` and the rest
    has been rewritten into scalar fused multiply-adds. These are assembly counts and carry no
    noise floor.
    """
    audit = instruction_audit()
    assert audit["vectorised_by_level"] == {"O0": 0, "O2": 8, "O2nativefma": 2, "O3fast": 1}

    at_o2 = [row for row in audit["rows"] if row["level"] == "O2"]
    vectorised = {(row["subject"], row["role"]) for row in at_o2 if row["packed_arithmetic"]}
    assert vectorised == {
        ("circle", "center_radius"),
        ("difference_of_cubes", "expanded"),
        ("difference_quotient", "split"),
        ("parabola", "standard"),
        ("product_chain_8", "balanced"),
        ("quotient_rule", "split"),
        ("sum_chain_8", "balanced"),
        ("trapezoid_area", "sum_of_halves"),
    }
    # Eight writings, and no two of them belong to the same object: the compiler vectorised one
    # side of eight different pairs and never both sides of one.
    assert len({subject for subject, _ in vectorised}) == 8
    # Five of the thirty-four carry a packed MULTIPLY specifically, which is the column that was
    # mislabelled; the other three vectorised an add, a subtract or a divide.
    assert sum(1 for row in at_o2 if row["multiply_packed"]) == 5

    # Above -O2 the only packed arithmetic left is a DIVIDE, which is why the counts fall to 2 and
    # 1: the report says so and this pins it.
    for level, expected in (
        ("O2nativefma", {("difference_quotient", "split"), ("quotient_rule", "split")}),
        ("O3fast", {("quotient_rule", "split")}),
    ):
        rows = [
            row for row in audit["rows"] if row["level"] == level and row["packed_arithmetic"]
        ]
        assert {(row["subject"], row["role"]) for row in rows} == expected, level
        assert all(row["multiply_packed"] == 0 for row in rows), level
        assert all(row["divide"] > 0 for row in rows), level


@NEEDS_CLANG
def test_fusion_is_off_below_o2fma_and_on_above_it_in_the_code_that_was_timed():
    """The optimisation ladder is a controlled variable, checked in the emitted assembly."""
    audit = loop_instruction_audit(mode="throughput")
    assert audit["all_found"] is True
    assert audit["missing"] == []
    assert audit["fma_by_level"]["O0"] == 0
    assert audit["fma_by_level"]["O2"] == 0
    assert audit["fma_by_level"]["O2nativefma"] > 0
    assert audit["fma_by_level"]["O3fast"] > 0


@NEEDS_CLANG
def test_a_kernel_the_compiler_inlined_is_reported_missing_and_not_reported_as_zero():
    """At ``O3fast`` clang inlines the smallest probe kernels into ``main``; that is disclosed."""
    writings = tuple(
        item
        for subject in probe_subjects()
        if subject.name == "probe_division"
        for item in subject.writings
    )
    audit = loop_instruction_audit(writings=writings, mode="throughput")
    missing = {(row["level"], row["kernel"]) for row in audit["missing"]}
    assert audit["all_found"] is False
    assert ("O3fast", _kernel_name(writings[0])) in missing
    # Which optimised levels inline depends on how much else is in the program, but ``-O0`` inlines
    # nothing, so a kernel missing there would be a parser fault rather than the compiler's doing.
    assert all(level != "O0" for level, _ in missing)
    assert all(row["found"] for row in audit["rows"] if row["level"] == "O0")
    # A missing kernel is reported as missing and never as a row of zero instructions.
    assert all(row["instructions"] == 0 for row in audit["rows"] if not row["found"])


@NEEDS_CLANG
def test_a_division_by_a_power_of_two_is_not_a_division_on_the_machine():
    """A limitation of the corpus, pinned: ``/ 2`` is a multiply, so it cannot probe divergence 1."""
    audit = instruction_audit(
        writings=tuple(item for item in ALL_WRITINGS if item.subject == "trapezoid_area")
    )
    at_o2 = [row for row in audit["rows"] if row["level"] == "O2"]
    assert all(row["divide"] == 0 for row in at_o2)


# ------------------------------------------------------------------------------ the four probes


def test_the_probe_predictions_are_pinned_and_were_written_before_the_measurement():
    """The prediction table is data, and it is pinned separately from what the machine did."""
    assert PROBE_PREDICTIONS == {
        "probe_division": {
            "throughput": {
                "O0": "common_denominator",
                "O2": "common_denominator",
                "O2nativefma": "common_denominator",
                "O3fast": "common_denominator",
            },
            "latency": {"O0": "separate", "O2": "separate", "O2nativefma": "separate", "O3fast": "separate"},
        },
        "probe_fma": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": "expanded", "O3fast": "expanded"},
            "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        },
        "probe_latency": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
            "latency": {"O0": "balanced", "O2": "balanced", "O2nativefma": "balanced", "O3fast": None},
        },
        "probe_registers": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
            "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        },
    }
    assert set(PROBE_PREDICTIONS) == {item.name for item in probe_subjects()}
    for subject in probe_subjects():
        roles = set(subject.roles) | {None}
        for mode in MODES:
            assert set(PROBE_PREDICTIONS[subject.name][mode]) == {item.name for item in LEVELS}
            assert set(PROBE_PREDICTIONS[subject.name][mode].values()) <= roles


@NEEDS_CLANG
def test_the_probes_measured_order_is_pinned_separately_from_the_prediction(probe_result):
    """What the machine did -- for the cells whose classification at this floor is stable.

    **One cell is deliberately not pinned to a value, and that is a repair.**
    ``probe_latency/latency/O0`` produced gaps from ``124.63%`` to ``171.15%`` over 30 runs, and
    :data:`PIN_FLOOR` is ``1.30``: its range STRADDLES the floor, so it resolved in ``25`` of the
    ``30`` and did not in ``5``. Pinning it to ``"balanced"`` was a gate on a statistic that cannot
    be bounded, and it duly failed inside a full suite run here.

    No constant floor repairs that. The floor has to stay above the division cells, whose largest
    observed gap is ``111.89%``, and below this cell's smallest, ``124.63%``; anything between them
    carries a margin of about ``1.06`` times on quantities that move by tens of percent. **That is
    a fact about this machine and it is reported as one** -- an extension of what
    :data:`PIN_FLOOR`'s own note already says about thresholds and these thirty-two cells.

    So this cell is asserted to be either resolved in the direction the machine always gives, or
    unresolved -- never the other direction -- and its size is checked against the noise floor
    measured in the SAME run by
    :func:`test_fast_math_erases_the_depth_difference_the_latency_probe_was_built_to_show`. Every
    other cell is pinned exactly.
    """
    observed = {}
    for cell in probe_result["cells"]:
        observed.setdefault(cell["probe"], {}).setdefault(cell["mode"], {})[cell["level"]] = cell["observed"]

    # The unpinnable cell, removed from the equality below and stated as what it actually is.
    straddling = observed["probe_latency"]["latency"].pop("O0")
    assert straddling in {"balanced", None}, straddling

    assert observed == {
        "probe_division": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
            "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        },
        "probe_fma": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
            "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        },
        "probe_latency": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
            # "O0" was popped above: its gap straddles PIN_FLOOR and is not a resolvable
            # classification at this floor.
            "latency": {"O2": "balanced", "O2nativefma": "balanced", "O3fast": None},
        },
        "probe_registers": {
            "throughput": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
            "latency": {"O0": None, "O2": None, "O2nativefma": None, "O3fast": None},
        },
    }
    assert probe_result["cell_count"] == len(LEVELS) * len(MODES) * 4


@NEEDS_CLANG
def test_every_probe_cell_the_machine_resolves_the_same_way_every_time_is_pinned(probe_result):
    """Direction AND size, for the ten cells eight runs agreed on.  A change in either fails."""
    cells = {(cell["probe"], cell["mode"], cell["level"]): cell for cell in probe_result["cells"]}
    for key, (role, bound) in DECISIVE_CELLS.items():
        cell = cells[key]
        faster = cell["roles"][0] if cell["seconds"][0] < cell["seconds"][1] else cell["roles"][1]
        assert faster == role, key
        assert cell["relative_gap"] > bound, (key, cell["relative_gap"])


@NEEDS_CLANG
def test_every_probe_cell_the_machine_never_separated_is_pinned_as_an_upper_bound(probe_result):
    """The other half of the measured order: where the machine says nothing, it keeps saying it.

    One declared ceiling for all seven cells rather than seven fitted bounds -- see
    :data:`INDISTINGUISHABLE_CEILING` for why the per-cell version was a coin flip. The ceiling has
    to stay below every decisive gap or it would stop distinguishing the two populations, so that is
    asserted here rather than left to the comment.
    """
    cells = {(cell["probe"], cell["mode"], cell["level"]): cell for cell in probe_result["cells"]}
    quiet = [cells[key]["relative_gap"] for key in INDISTINGUISHABLE_CELLS]
    loud = [cells[key]["relative_gap"] for key in DECISIVE_CELLS]

    # The claim, stated as a comparison INSIDE one run: every cell the machine never separated is
    # separated by less than every cell it did.  A contended run inflates both sides together, so
    # this survives a busy machine where a fixed threshold between the two does not -- and the two
    # populations are only about five times apart, which is too close to place a constant between.
    assert max(quiet) < min(loud), (max(quiet), min(loud))

    # A coarse absolute sanity bound as well, so a run in which everything collapsed to noise cannot
    # satisfy the comparison above by making both sides tiny.
    for key in INDISTINGUISHABLE_CELLS:
        assert cells[key]["relative_gap"] < INDISTINGUISHABLE_CEILING, (
            key,
            cells[key]["relative_gap"],
        )
    assert INDISTINGUISHABLE_CEILING <= min(bound for _, bound in DECISIVE_CELLS.values())


def test_no_probe_cell_is_both_decisive_and_indistinguishable():
    """The two pinned sets are disjoint, so no cell is pinned twice in opposite directions."""
    assert not set(DECISIVE_CELLS) & set(INDISTINGUISHABLE_CELLS)
    keys = {
        (subject.name, mode, level.name)
        for subject in probe_subjects()
        for mode in MODES
        for level in LEVELS
    }
    assert set(DECISIVE_CELLS) <= keys
    assert set(INDISTINGUISHABLE_CELLS) <= keys


@NEEDS_CLANG
def test_the_division_probe_separates_by_far_more_than_the_noise_floor(probe_result):
    """The largest single divergence: the model prefers the writing the machine does not."""
    cells = {
        (cell["level"], cell["mode"]): cell
        for cell in probe_result["cells"]
        if cell["probe"] == "probe_division"
    }
    for level in ("O2nativefma", "O3fast"):
        cell = cells[(level, "throughput")]
        faster = cell["roles"][0] if cell["seconds"][0] < cell["seconds"][1] else cell["roles"][1]
        assert faster == "common_denominator"
        assert cell["relative_gap"] > 0.70
    division = {
        item.role: structural_profile(tree_of(item.source))
        for subject in probe_subjects()
        if subject.name == "probe_division"
        for item in subject.writings
    }
    assert division["separate"]["operations"] < division["common_denominator"]["operations"]


@NEEDS_CLANG
def test_fast_math_erases_the_depth_difference_the_latency_probe_was_built_to_show(probe_result):
    """Depth 15 against depth 4 costs an order of magnitude over the noise until ``-ffast-math``.

    The size is stated against the noise floor measured in the SAME run rather than against a
    constant. Over 30 runs the ratio of this gap to that run's floor never fell below ``15.29``, so
    ``10`` times carries a margin of about ``1.5``; a contended run inflates the gap and the floor
    together, which is what a fixed threshold does not survive. The two cells whose gap is clear of
    :data:`PIN_FLOOR` in every run keep their pinned classification; ``O0``'s does not, for the
    reason :func:`test_the_probes_measured_order_is_pinned_separately_from_the_prediction` gives.
    """
    cells = {
        (cell["level"], cell["mode"]): cell
        for cell in probe_result["cells"]
        if cell["probe"] == "probe_latency"
    }
    floor = probe_result["noise_floor"]["floor"]
    for level in ("O0", "O2", "O2nativefma"):
        cell = cells[(level, "latency")]
        faster = cell["roles"][0] if cell["seconds"][0] < cell["seconds"][1] else cell["roles"][1]
        assert faster == "balanced", level
        assert cell["relative_gap"] > 10 * floor, (level, cell["relative_gap"], floor)
    for level in ("O2", "O2nativefma"):
        assert cells[(level, "latency")]["observed"] == "balanced", level
    # The same declared ceiling the other never-separated cells use, rather than a bound of its own
    # fitted just past what this cell happened to produce.
    assert cells[("O3fast", "latency")]["relative_gap"] < INDISTINGUISHABLE_CEILING


#: The three register-probe cells whose direction agreed in every repeat.  The direction is the one
#: the model does NOT predict, and the direction is the finding.
#:
#: **These carried absolute lower bounds, then a comparison against the same-run noise floor, and
#: both were gates on a statistic that cannot be bounded.** The absolute bounds were set just under
#: the smallest gap observed -- ``0.030`` against ``4.62%`` in the tightest case -- and a contended
#: run pushed a gap under its bound. The replacement compared each gap with the noise floor measured
#: in the same run, which failed here too: over 30 runs the ratio of gap to same-run floor fell as
#: low as ``0.37`` for ``latency/O2`` and ``0.23`` for ``throughput/O0``, and a full suite run duly
#: failed at ``2.39%`` against a floor of ``4.33%``.
#:
#: **So neither the size nor the DIRECTION is asserted for this probe.** The direction was the third
#: attempt and it broke the same way as the first two. It was justified as a sign rather than a
#: magnitude -- the writing with the larger peak live was the faster one in ``30`` of ``30`` runs --
#: and review then saw ``latency/O2`` resolve the other way, in one of five runs of this file.
#:
#: **A sample unanimity is a sample maximum wearing a different hat.** ``30`` of ``30`` bounds
#: nothing, and the exemption this file granted signs, having applied the rule to every magnitude,
#: is exactly what failed. Worse, the ``30`` runs were collected by calling the probe standalone,
#: while the assertion is evaluated from a module-scoped fixture partway through a file that has
#: already compiled and timed the whole corpus. Review measured the standalone direction at ``12`` of
#: ``12`` for all three cells -- including the ``throughput/O0`` cell this tuple had dropped for
#: flipping -- so the standalone evidence does not even separate the cells it was used to select.
#: **Evidence for a test's stability has to be collected the way the test runs.**
#:
#: These are therefore the cells whose gap repeats, kept as the pointer into section 9 of the
#: reports, where the direction and its spread are published. Nothing here asserts either.
REGISTER_CELLS_THAT_MOVE = (
    ("probe_registers", "latency", "O0"),
    ("probe_registers", "latency", "O2"),
)


@NEEDS_CLANG
def test_the_register_probe_finds_nothing_and_the_direction_it_hints_at_is_the_wrong_one(probe_result):
    """Peak live below the register file costs nothing decisive; where it moves, it moves wrong.

    **No size is asserted for this probe, and that is a repair.** See
    :data:`REGISTER_CELLS_THAT_MOVE`: both an absolute lower bound and a comparison against the
    same-run noise floor were tried, and both were gates on a quantity whose range covers them. The
    gaps are published in section 9 of the reports instead.

    What is left is what the probe is for and one comparison that carries a margin. The probe is for
    the negative: every register cell reports ``observed is None``, which is structural rather than
    timed. The comparison is WITHIN-RUN, with a factor of about ``6.75`` behind it over 30 runs:
    every register cell is separated by less than the smallest of the deep-chain latency cells in
    the same run, so a contended run inflates both sides together.

    **The direction is no longer asserted either**, for the reason recorded at
    :data:`REGISTER_CELLS_THAT_MOVE`. It is published with its spread in section 9 instead.
    """
    cells = {(cell["probe"], cell["mode"], cell["level"]): cell for cell in probe_result["cells"]}
    register = [cell for key, cell in cells.items() if key[0] == "probe_registers"]
    assert all(cell["observed"] is None for cell in register)

    # Nothing anywhere near the size of the depth effect, stated inside one run.  The largest
    # register gap over 30 runs was 20.94% and the smallest deep-chain gap 124.63%.
    deep = min(
        cells[("probe_latency", "latency", level)]["relative_gap"]
        for level in ("O0", "O2", "O2nativefma")
    )
    assert max(cell["relative_gap"] for cell in register) < deep

    # Where the gap repeats, the writing with the LARGER peak live is USUALLY the faster one, which
    # is the opposite of the direction 0044 and 0049 give the axis.  That is published in section 9
    # with the runs it held in and the run it did not; it is not asserted here, because a direction
    # is a sign and a sign read off a noise-dominated pair is not a bounded quantity.  What this
    # loop still checks is that the cells named as the ones that move do carry a gap at all, so the
    # pointer into section 9 cannot silently go stale.
    for key in REGISTER_CELLS_THAT_MOVE:
        cell = cells[key]
        assert cell["relative_gap"] > 0.0, key
        assert set(cell["roles"]) == {"high_peak", "low_peak"}, key


@NEEDS_CLANG
def test_the_probe_floor_sweep_is_carried_on_every_cell(probe_result):
    for cell in probe_result["cells"]:
        floors = [entry["floor"] for entry in cell["floor_sensitivity"]]
        assert floors == sorted(set(floors))
        assert cell["floors_swept"] == len(floors)
        resolved = [entry for entry in cell["floor_sensitivity"] if entry["observed"] is not None]
        assert resolved == cell["floor_sensitivity"][: len(resolved)]


@NEEDS_CLANG
def test_the_repeatability_study_is_what_says_which_cells_have_a_measured_order():
    """Two runs of the whole probe set, so a cell that cannot agree with itself is visible."""
    study = probe_repeatability(repeats=2)
    assert study["repeats"] == 2
    assert study["cells"] == len(LEVELS) * len(MODES) * 4
    assert study["cells_agreeing_on_direction"] <= study["cells"]
    for row in study["rows"]:
        assert row["minimum_gap"] <= row["median_gap"] <= row["maximum_gap"]
        assert row["resolved_agrees"] == (len(row["directions"]) == 1)


def test_the_repeatability_study_refuses_a_single_run():
    with pytest.raises(ValueError, match="at least two runs"):
        probe_repeatability(repeats=1)


# ---------------------------------------------------------------------------- the agreement table


@NEEDS_CLANG
def test_the_agreement_tables_disagreement_count_is_pinned(agreement_result):
    """Two inversions, both at ``-O3 -ffast-math``, and both of them are the same two every run."""
    table = agreement_result
    assert table["subject_count"] == 16
    assert table["writing_count"] == 34
    assert table["headline_inversions"] == 2
    inversions = [
        (cell["level"], cell["mode"], cell["subject"])
        for cell in table["cells"]
        if cell["axis"] == MODE_AXIS[cell["mode"]] and cell["inversion_count"]
    ]
    assert sorted(inversions) == [
        ("O3fast", "latency", "parabola"),
        ("O3fast", "throughput", "difference_of_cubes"),
    ]


@NEEDS_CLANG
def test_the_agreement_table_reports_a_full_axis_by_regime_matrix(agreement_result):
    table = agreement_result
    assert len(table["matrix"]) == len(LEVELS) * len(MODES) * len(MODEL_AXES)
    operations = {
        (row["level"], row["mode"]): row["inversions"]
        for row in table["matrix"]
        if row["axis"] == "operations"
    }
    # Nothing the model orders by operation count is contradicted below ``-O2nativefma``.
    assert operations[("O0", "throughput")] == 0
    assert operations[("O2", "throughput")] == 0


@NEEDS_CLANG
def test_the_floor_is_swept_rather_than_declared_and_the_count_is_read_off_the_curve(agreement_result):
    table = agreement_result
    sweep = table["floor_sensitivity"]
    assert [entry["floor"] for entry in sweep] == sorted({*FLOOR_SWEEP, AGREEMENT_PIN_FLOOR})
    assert sum(1 for entry in sweep if entry["is_working_floor"]) == 1
    # Raising the floor can only turn a resolved pair into an unresolved one, never the reverse.
    counts = [entry["inversions"] + entry["concordant"] for entry in sweep]
    assert counts == sorted(counts, reverse=True)
    assert [entry["collapsed_subject_cells"] for entry in sweep] == sorted(
        entry["collapsed_subject_cells"] for entry in sweep
    )


@NEEDS_CLANG
def test_the_survival_table_counts_the_same_subjects_at_every_level(agreement_result):
    survival = survival_table(agreement_result)
    assert len(survival["rows"]) == len(LEVELS) * len(MODES)
    assert all(row["subjects"] == 16 for row in survival["rows"])
    assert survival["floor"] == AGREEMENT_PIN_FLOOR


def test_an_unresolved_pair_is_not_counted_as_agreement():
    """The floor may never manufacture a result, so a pair inside it is unresolved, not concordant."""
    blank = {"depth": 0, "div": 0, "fma_sites": 0, "peak_live": 0}
    profiles = {"a": {"operations": 2, **blank}, "b": {"operations": 3, **blank}}
    timings = {"a": 1.0, "b": 1.001}
    inversions, unresolved, concordant = _classify(["a", "b"], timings, profiles, "operations", 0.01)
    assert (len(inversions), len(unresolved), len(concordant)) == (0, 1, 0)
    inversions, unresolved, concordant = _classify(["a", "b"], timings, profiles, "operations", 0.0)
    assert (len(inversions), len(unresolved), len(concordant)) == (0, 0, 1)
    timings = {"a": 2.0, "b": 1.0}
    inversions, _, _ = _classify(["a", "b"], timings, profiles, "operations", 0.0)
    assert inversions and inversions[0]["model_better"] == "a"


def test_a_pair_the_model_calls_equal_is_never_counted_at_all():
    """A tie is not a prediction and cannot be contradicted."""
    blank = {"depth": 0, "div": 0, "fma_sites": 0, "peak_live": 0}
    profiles = {"a": {"operations": 3, **blank}, "b": {"operations": 3, **blank}}
    assert _classify(["a", "b"], {"a": 1.0, "b": 5.0}, profiles, "operations", 0.0) == ([], [], [])


def test_relative_gap_is_symmetric_and_measured_against_the_smaller_side():
    assert _relative_gap(1.0, 2.0) == _relative_gap(2.0, 1.0) == 1.0
    assert _relative_gap(1.0, 1.0) == 0.0


def test_the_report_refuses_to_run_without_a_compiler(monkeypatch):
    """``metal_report`` names the missing tool rather than failing somewhere deeper."""
    import parseatlas.metal as metal

    monkeypatch.setattr(metal, "clang_available", lambda: False)
    with pytest.raises(RuntimeError, match="needs clang on PATH"):
        metal.metal_report()


def test_the_report_checks_the_probes_correctness_and_not_only_the_corpus():
    """The probes carry the card's sharpest claims, so their values are checked in the report run."""
    import inspect

    import parseatlas.metal as metal

    source = inspect.getsource(metal.metal_report)
    assert "probe_subjects()" in source
    assert source.index("correctness_audit") < source.index("agreement_table")


# ------------------------------------------------------------------------------ multicore policy


@NEEDS_CLANG
def test_compilation_is_parallel_and_timing_is_not():
    decision = parallel_decision(repeats=2)
    assert decision["clang"] is True
    assert decision["compilation_parallel"] is True
    assert decision["speedup"] > 1.5
    assert decision["timing_parallel"] is False
    assert "0041" in decision["timing_note"]


# ----------------------------------------------------------------------------- nothing is left behind


@NEEDS_CLANG
def test_no_generated_c_or_binary_survives_a_run():
    """Generated sources and binaries live in a temporary directory that the run removes."""
    before = set(Path("src/parseatlas").glob("*")) | set(Path("tests").glob("*"))
    benchmark(ALL_WRITINGS[:2], "O2", iterations=65536, trials=3)
    after = set(Path("src/parseatlas").glob("*")) | set(Path("tests").glob("*"))
    assert before == after
    assert not list(Path(".").glob("*.exe"))
    assert not list(Path(".").glob("*.c"))


@NEEDS_CLANG
def test_a_caller_supplied_working_directory_is_left_for_the_caller_to_clean():
    directory = Path(tempfile.mkdtemp(prefix="parseatlas_metal_test_"))
    try:
        benchmark(ALL_WRITINGS[:2], "O2", iterations=65536, trials=3, workdir=directory)
        assert list(directory.glob("*.c"))
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_the_skip_reason_names_the_compiler_so_the_skip_is_visible():
    assert "clang" in NEEDS_CLANG.kwargs["reason"]
    assert clang_available() == (shutil.which("clang") is not None)
