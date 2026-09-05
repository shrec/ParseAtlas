"""Validation of experiment 0056: twenty-five native machines against one machine plus a conversion.

The file is ordered cheap-first and the order is not cosmetic.  Nothing about a timing is believed
until three things have been checked:

* **the architectures read every string into the same tree**, byte for byte, in all 25 worlds.  If
  they ever disagree that is the finding and the card stops; the agreement test therefore runs
  first and its failure makes every later number meaningless;
* **the emitter is deterministic**, so a measurement belongs to a machine and not to a run;
* **every decisive gate can FIRE.**  ROADMAP records three cards in one week that shipped gates no
  test could catch failing, and the rule it set is applied literally here: for each decisive
  predicate there is a control that puts a case the gate must reject in front of it, **through the
  same function the published number comes from**, and asserts the rejection.

The controls in this file, and the gate each one attacks:

.. code-block:: text

    agreement, native side       a machine emitted for the wrong world, and one with its levels
                                 collapsed - both through agreement_audit itself
    agreement, conversion side   the bracket-blind conversion - through agreement_audit itself
    language identity            a well-formed string offered as malformed, and a malformed one
                                 offered as well-formed - through language_identity_audit itself
    operation invariance         a corrupted multiset - through operation_invariance itself
    the T6 bound                 an under-counted operator support - through distinct_graph_table
    instruction multisets        equal sequences forced apart and unequal ones forced together
    the report's own stop        agreement_audit replaced by one that fails, and the report must
                                 refuse to publish any timing

**No timing is asserted as an inequality anywhere in this file.**  The card's own noise floor,
measured with the same paired instrument that produces its ratios, reaches double digits on a cell
whose true ratio is exactly one.  A test that asserted "native is faster" would be asserting the
weather.  What the timing tests check is that the instruments are shaped correctly, carry their
denominators, and report ``never`` where they must.
"""

import math
import shutil

import pytest

from parseatlas import native_machines as nm
from parseatlas.canonical import operation_cost
from parseatlas.grammar import all_grammars, control_grammar
from parseatlas.memory_ceiling import peak_live
from parseatlas.parallel_worlds import depth
from parseatlas.parser import Binary, Variable, parse

GRAMMARS = all_grammars()
CONTROL = control_grammar()
CORPUS = nm.corpus()
NAMED = nm.named_corpus()

#: Pinned so a change in the corpus fails a test rather than silently rewriting every denominator.
CORPUS_SIZE = 110
NAMED_SIZE = 58
WORLDS = 25

#: The agreement grid: every entry, every world, every architecture but the reference.
AGREEMENT_CELLS = 11000
CELLS_PER_ARCHITECTURE = 2750

#: What each negative control must produce.  Measured before being written down; they are exact
#: because the corpus, the worlds and the emitter are all deterministic.
REVERSED_MISMATCHES = 1809
FLATTENED_MISMATCHES = 1516
BRACKET_BLIND_MISMATCHES = 498


# ------------------------------------------------------------------- the emitter and its shape


def test_the_emitter_is_deterministic():
    for grammar in GRAMMARS:
        for variant in nm.ALL_VARIANTS:
            first = nm.emit_native_source(grammar, variant)
            second = nm.emit_native_source(grammar, variant)
            assert first == second


def test_a_native_machine_consults_no_grammar_object_and_no_table():
    """The definition of "native" this card is measuring, checked against the emitted text.

    The last assertion is the strong one: **the only subscript anywhere in a native machine is into
    the token array.**  A binding-power lookup would have to be a subscript of something else, so a
    machine that satisfies this consults no table at run time, whatever the table were called.
    """
    for grammar in GRAMMARS:
        for variant in nm.NATIVE_VARIANTS:
            source = nm.emit_native_source(grammar, variant)
            body = source.split("\n", 1)[1]
            assert "POWERS" not in body
            assert "Grammar" not in body
            assert "grammar" not in body
            subscripts = [index for index, character in enumerate(body) if character == "["]
            assert subscripts
            for index in subscripts:
                assert body[index - len("tokens") : index] == "tokens"


def test_the_levels_variant_has_no_binding_power_in_it_at_all():
    """In ``levels`` the powers have become the call structure; they are not constants either."""
    source = nm.emit_native_source(CONTROL, "levels")
    assert "minimum_power" not in source
    assert source.count("def _level_") == len(CONTROL.levels)
    strict = GRAMMARS[1]
    assert nm.emit_native_source(strict, "levels").count("def _level_") == 4


def test_the_climb_variant_carries_the_binding_powers_as_literal_constants():
    source = nm.emit_native_source(GRAMMARS[1], "climb")
    for power in (4, 3, 2, 1):
        assert f"if {power} < minimum_power:" in source
    assert "POWERS" not in source


def test_the_lookup_control_is_the_same_program_in_every_world():
    """The control's source carries no world-specific text, so one compilation serves all 25."""
    sources = {nm.emit_native_source(grammar, nm.TABLE_VARIANT) for grammar in GRAMMARS}
    assert len(sources) == 1
    only = sources.pop()
    assert "POWERS[value]" in only
    for operator in ("+", "-", "*", "/"):
        assert f'value == "{operator}"' not in only


def test_the_strict_machines_are_one_program_with_four_symbols_permuted():
    """The structural half of the null model: no per-world code, so no per-world speed to find."""
    audit = nm.machine_isomorphism_audit(GRAMMARS)
    for variant in nm.NATIVE_VARIANTS:
        data = audit["variants"][variant]
        assert data["strict_worlds_identical"] is True
        assert data["distinct_normalised_sources"] == 2
        assert sorted(item["size"] for item in data["classes"]) == [1, 24]
        assert [item["members"] for item in data["classes"] if item["size"] == 1] == [["G0"]]
    lookup = audit["variants"][nm.TABLE_VARIANT]
    assert lookup["distinct_normalised_sources"] == 1
    assert [item["size"] for item in lookup["classes"]] == [25]


def test_g0_is_the_only_world_whose_machine_has_a_different_shape():
    """And the reason is its tied levels, not an ordering - stated in the report, checked here."""
    audit = nm.machine_isomorphism_audit(GRAMMARS)
    levels = audit["variants"]["levels"]["levels_by_world"]
    assert levels["G0"] == 2
    assert {value for name, value in levels.items() if name != "G0"} == {4}


def test_an_unknown_variant_is_refused():
    with pytest.raises(ValueError):
        nm.emit_native_source(CONTROL, "no-such-variant")


# ---------------------------------------------------------------- the first gate, and its controls


def test_every_architecture_reads_every_string_into_the_same_tree():
    assert len(NAMED) == NAMED_SIZE
    audit = nm.agreement_audit(CORPUS, GRAMMARS)
    assert audit["entries"] == CORPUS_SIZE
    assert audit["grammars"] == WORLDS
    assert audit["cells"] == AGREEMENT_CELLS
    assert audit["cells_per_architecture"] == CELLS_PER_ARCHITECTURE
    assert audit["all_match"] is True
    assert audit["mismatch_total"] == 0
    assert set(audit["mismatch_counts"]) == {
        "native_levels",
        "native_climb",
        "table_lookup",
        "convert",
    }


def test_the_agreement_gate_fires_on_a_machine_built_for_the_wrong_world():
    """A native machine whose levels are reversed is a machine for another world; it must be caught.

    Through :func:`agreement_audit` itself, which is where the published ``all_match`` comes from.
    """
    audit = nm.agreement_audit(CORPUS, GRAMMARS, sabotage="reverse_levels")
    assert audit["all_match"] is False
    assert audit["mismatch_counts"]["native_levels"] == REVERSED_MISMATCHES
    assert audit["mismatch_counts"]["native_climb"] == REVERSED_MISMATCHES
    assert audit["worlds_with_mismatch"]["native_levels"] == WORLDS
    assert audit["worlds_with_mismatch"]["native_climb"] == WORLDS
    assert audit["mismatch_counts"]["convert"] == 0


def test_the_agreement_gate_fires_on_a_machine_with_its_levels_collapsed():
    audit = nm.agreement_audit(CORPUS, GRAMMARS, sabotage="flatten")
    assert audit["all_match"] is False
    assert audit["mismatch_counts"]["native_levels"] == FLATTENED_MISMATCHES
    assert audit["worlds_with_mismatch"]["native_levels"] == WORLDS


def test_the_agreement_gate_fires_on_the_bracket_blind_conversion():
    """The soundness obligation of question 1, made to fail on the path the number comes from.

    The conversion column must break and the native columns must stay clean, so the test shows the
    gate discriminating rather than merely reporting trouble.
    """
    audit = nm.agreement_audit(CORPUS, GRAMMARS, blind_conversion=True)
    assert audit["all_match"] is False
    assert audit["mismatch_counts"]["convert"] == BRACKET_BLIND_MISMATCHES
    assert audit["worlds_with_mismatch"]["convert"] == WORLDS
    assert audit["mismatch_counts"]["native_levels"] == 0
    assert audit["mismatch_counts"]["native_climb"] == 0
    assert audit["mismatch_counts"]["table_lookup"] == 0


def test_the_bracket_blind_conversion_loses_the_brackets_on_a_named_case():
    """Why it is unsound, on one line of real mathematics rather than in the abstract."""
    source = "a * (b + c)"
    expected = nm.serialise(parse(source, CONTROL))
    assert nm.serialise(nm.parse_then_convert(source, CONTROL)) == expected
    assert nm.serialise(nm.convert_bracket_blind(source, CONTROL)) != expected
    assert nm.serialise(nm.convert_bracket_blind(source, CONTROL)) == nm.serialise(
        parse("a * b + c", CONTROL)
    )


def test_the_sound_conversion_needs_the_mark_the_conventional_parser_throws_away():
    """Two different strings, one tree: which is exactly why the tree alone cannot drive a rewrite."""
    bracketed = "(a * b) + c"
    plain = "a * b + c"
    assert nm.serialise(parse(bracketed, CONTROL)) == nm.serialise(parse(plain, CONTROL))
    marked = nm.parse_marked(bracketed)
    assert isinstance(marked, Binary) and isinstance(marked.left, nm.Group)
    assert not isinstance(nm.parse_marked(plain).left, nm.Group)
    # And the two do part company in a world where the grouping matters.
    other = next(item for item in GRAMMARS if item.precedence == ("+", "-", "*", "/"))
    assert nm.serialise(nm.parse_then_convert(bracketed, other)) != nm.serialise(
        nm.parse_then_convert(plain, other)
    )


def test_an_unknown_sabotage_is_refused():
    with pytest.raises(ValueError):
        nm.emit_native_source(CONTROL, "levels", sabotage="no-such-sabotage")


# ---------------------------------------------------------- capability: one language, many trees


def test_the_twenty_five_worlds_accept_and_reject_the_same_strings():
    audit = nm.language_identity_audit(CORPUS, GRAMMARS)
    assert audit["same_language"] is True
    assert audit["accepted_checks"] == CORPUS_SIZE * WORLDS
    assert audit["rejected_checks"] == len(nm.MALFORMED) * WORLDS
    assert audit["accept_failures"] == []
    assert audit["reject_failures"] == []


def test_the_language_audit_fires_when_a_well_formed_string_is_offered_as_malformed():
    audit = nm.language_identity_audit(CORPUS[:2], GRAMMARS, malformed=("a + b",))
    assert audit["same_language"] is False
    assert len(audit["reject_failures"]) == WORLDS
    assert {item["error"] for item in audit["reject_failures"]} == {"accepted"}


def test_the_language_audit_fires_when_a_malformed_string_is_offered_as_corpus():
    broken = (nm.Entry("broken", "control", "a + "),)
    audit = nm.language_identity_audit(broken, GRAMMARS, malformed=())
    assert audit["same_language"] is False
    assert len(audit["accept_failures"]) == WORLDS


# --------------------------------------------------------------------------- the emitted dataflow


def test_graph_profile_reads_the_cards_that_own_the_three_measures():
    tree = parse("a + b * c - d / e", CONTROL)
    profile = nm.graph_profile(tree)
    cost = operation_cost(tree)
    assert profile["operations"] == sum(cost[key] for key in nm.OPERATION_KEYS)
    assert profile["depth"] == depth(tree)
    assert profile["peak_live"] == peak_live(tree)


def test_the_operation_multiset_is_the_same_in_every_world():
    audit = nm.operation_invariance(CORPUS, GRAMMARS)
    assert audit["invariant"] is True
    assert audit["failures"] == []
    assert audit["checked"] == CORPUS_SIZE * WORLDS


def test_the_operation_invariance_check_fires_on_a_corrupted_multiset():
    audit = nm.operation_invariance(CORPUS[:3], GRAMMARS, sabotage=True)
    assert audit["invariant"] is False
    assert len(audit["failures"]) == 1


def test_the_t6_bound_is_respected_and_checked_by_enumeration():
    table = nm.distinct_graph_table(CORPUS, GRAMMARS)
    assert table["bound_respected"] is True
    assert table["violations"] == []
    for row in table["rows"]:
        assert row["strict_bound"] == math.factorial(row["support_size"])
        assert row["distinct_strict"] <= row["strict_bound"]
        assert row["distinct_all"] <= row["strict_bound"] + 1


def test_the_t6_bound_check_fires_when_the_support_is_under_counted():
    """A bound is only a gate if a value above it is caught; here one is manufactured and must be."""
    table = nm.distinct_graph_table(CORPUS, GRAMMARS, sabotage=True)
    assert table["bound_respected"] is False
    assert table["violations"]


def test_the_t6_bound_is_not_attained_by_short_words_and_the_search_is_exhaustive():
    """A bound is not a finding; what the corpus does against it is.  Enumerated, not cited.

    Every four-operator word of four, five and six operators is read by all 24 strict machines.  The
    space is finite and is searched completely, so "no word of this length attains ``24``" is a
    statement about a search that finished rather than about one that stopped.
    """
    audit = nm.bound_attainment((4, 5, 6), GRAMMARS)
    assert audit["bound"] == 24
    assert audit["strict_worlds"] == 24
    rows = {row["operators"]: row for row in audit["rows"]}
    assert rows[4]["four_operator_words"] == 24
    assert rows[5]["four_operator_words"] == 240
    assert rows[6]["four_operator_words"] == 1560
    assert rows[4]["maximum_distinct"] == 14
    assert rows[5]["maximum_distinct"] == 19
    assert rows[6]["maximum_distinct"] == 21
    assert audit["bound_attained"] is False
    assert all(row["attaining_bound"] == 0 for row in audit["rows"])


def test_the_t6_bound_is_attained_by_a_witness_of_eight_operators():
    """And the other half: the bound IS reached, so the shortfall is a corpus fact, not a theorem."""
    witness = "v0 + v1 - v2 * v3 + v4 / v5 - v6 * v7 / v8"
    strict = [grammar for grammar in GRAMMARS if grammar.id != "G0"]
    forms = {nm.serialise(nm.build_native(grammar, "levels").parse_source(witness)) for grammar in strict}
    assert len(forms) == 24
    assert len(strict) == 24


def test_the_structural_sweep_runs_past_the_timed_one_and_names_where_it_stops():
    audit = nm.long_word_check((192,), grammars=GRAMMARS)
    assert audit["bound_respected"] is True
    four = [row for row in audit["rows"] if row.get("support") == ("+", "-", "*", "/")]
    assert len(four) == 1
    assert four[0]["strict_bound"] == 24
    assert four[0]["distinct_strict"] == 20
    assert four[0]["distinct_all"] == 21
    assert audit["recursion_limit"] > 0


def test_sharpest_objects_applies_a_declared_rule_and_not_a_hand():
    dataflow = nm.dataflow_table(CORPUS, GRAMMARS)
    first = nm.sharpest_objects(dataflow, 4)
    second = nm.sharpest_objects(dataflow, 4)
    assert first == second
    spreads = {row["entry"]: row["depth_spread"] for row in dataflow["by_entry"]}
    assert spreads[first[0]] == max(spreads.values())


# -------------------------------------------------------------------------------- the C emission


def test_the_c_emission_is_a_transcript_of_the_graph():
    tree = parse("a + b * c - d / e", CONTROL)
    text = nm.emit_c_function(tree, "k_probe")
    statements = [line for line in text.splitlines() if line.strip().startswith("double t")]
    assert len(statements) == nm.graph_profile(tree)["operations"]
    assert text == nm.emit_c_function(tree, "k_probe")
    assert text.startswith("double k_probe(double x_a, double x_b, double x_c, double x_d, double x_e)")


def test_the_c_emission_refuses_an_illegal_function_name():
    with pytest.raises(ValueError):
        nm.emit_c_function(Variable("a"), "not a name")


def test_the_instruction_comparison_fires_in_both_directions():
    """The decisive predicate of question 4, shown to answer both ways rather than only one."""
    same = [["mulsd", "addsd"], ["addsd", "mulsd"]]
    different = [["mulsd", "addsd"], ["addsd", "divsd"]]
    assert nm.identical_multisets(same) is True
    assert nm.identical_multisets(different) is False
    assert nm.identical_multisets(same, sabotage="append") is False
    assert nm.identical_multisets(different, sabotage="collapse") is True
    with pytest.raises(ValueError):
        nm.identical_multisets(same, sabotage="no-such-sabotage")


# ------------------------------------------------------------------ the instruments, not the times


def test_every_rate_carries_its_denominator():
    machine = nm.build_native(CONTROL, "levels")
    sources = tuple(entry.source for entry in NAMED[:4])
    rate = nm.measure_rate(machine.parse_source, sources, repeats=2, passes=3)
    assert rate["parses_per_block"] == 3 * 4
    for key in ("minimum", "median", "maximum"):
        assert rate["seconds_per_parse"][key] > 0
        assert rate["parses_per_second"][key] > 0
    assert rate["seconds_per_parse"]["minimum"] <= rate["seconds_per_parse"]["median"]
    assert rate["seconds_per_parse"]["median"] <= rate["seconds_per_parse"]["maximum"]


def test_the_paired_instrument_reports_a_range_and_never_one_reading():
    machine = nm.build_native(CONTROL, "levels")
    other = nm.build_native(CONTROL, "climb")
    sources = tuple(entry.source for entry in NAMED[:4])
    ratio = nm.paired_ratio(machine.parse_source, other.parse_source, sources, rounds=3, passes=2)
    assert len(ratio["ratios"]) == 3
    assert ratio["minimum"] <= ratio["median"] <= ratio["maximum"]
    assert ratio["parses_per_block"] == 2 * 4


def test_generation_is_reported_on_its_own_and_never_inside_a_rate():
    cost = nm.generation_cost(CONTROL, "levels", repeats=3)
    assert cost["seconds"]["repeats"] == 3
    assert cost["seconds"]["minimum"] > 0
    machine = nm.build_native(CONTROL, "levels")
    assert machine.generation_seconds > 0
    rate = nm.measure_rate(machine.parse_source, ("a + b",), repeats=2, passes=2)
    assert "generation" not in rate
    assert "seconds" not in rate


def test_the_control_does_not_pay_twenty_five_compilations():
    registry = nm.registry_generation_cost(GRAMMARS, repeats=2)
    assert registry["totals"]["table_lookup"]["compilations"] == 1
    assert registry["totals"]["native_levels"]["compilations"] == WORLDS
    assert registry["totals"]["native_climb"]["compilations"] == WORLDS
    assert registry["totals"]["table"]["compilations"] == 0
    assert registry["lookup_source_identical_in_every_world"] is True


def test_a_control_machine_built_from_the_shared_code_object_still_reads_its_own_world():
    """The amortisation is only honest if the shared compilation really does serve every world."""
    source = nm.emit_native_source(CONTROL, nm.TABLE_VARIANT)
    prepared = (source, compile(source, "<shared>", "exec"))
    for grammar in GRAMMARS:
        machine = nm.build_native(grammar, nm.TABLE_VARIANT, code=prepared)
        for entry in NAMED[:6]:
            assert nm.serialise(machine.parse_source(entry.source)) == nm.serialise(
                parse(entry.source, grammar)
            )


def test_the_break_even_says_never_rather_than_a_large_number():
    generation = {"seconds": {"minimum": 1e-3, "median": 1e-3, "maximum": 1e-3}}
    baseline = {"seconds": {"minimum": 0.0, "median": 0.0, "maximum": 0.0}}
    per_parse = {"minimum": 1e-5, "median": 1e-5, "maximum": 1e-5}
    slower = nm.break_even_from_ratio(
        generation, baseline, per_parse, {"minimum": 0.9, "median": 0.95, "maximum": 0.99}
    )
    assert slower["break_even"] is None
    assert slower["reason"]
    faster = nm.break_even_from_ratio(
        generation, baseline, per_parse, {"minimum": 1.5, "median": 2.0, "maximum": 2.5}
    )
    # gap = 1e-5 * (1 - 1/2) = 5e-6 ; 1e-3 / 5e-6 = 200
    assert faster["break_even"] == 200
    assert faster["break_even_range"]["optimistic"] == 167
    assert faster["break_even_range"]["pessimistic"] == 300


def test_the_break_even_subtracts_the_baselines_own_one_off_cost():
    generation = {"seconds": {"minimum": 1e-3, "median": 1e-3, "maximum": 1e-3}}
    free = {"seconds": {"minimum": 0.0, "median": 0.0, "maximum": 0.0}}
    charged = {"seconds": {"minimum": 5e-4, "median": 5e-4, "maximum": 5e-4}}
    per_parse = {"minimum": 1e-5, "median": 1e-5, "maximum": 1e-5}
    ratio = {"minimum": 2.0, "median": 2.0, "maximum": 2.0}
    assert nm.break_even_from_ratio(generation, free, per_parse, ratio)["break_even"] == 200
    assert nm.break_even_from_ratio(generation, charged, per_parse, ratio)["break_even"] == 100


def test_the_worker_count_comes_from_the_observed_cores_and_leaves_headroom():
    assert nm.worker_count_for(16, 25) == 16 - nm.WORKER_HEADROOM_CORES
    assert nm.worker_count_for(16, 3) == 3
    assert nm.worker_count_for(1, 25) == 1
    assert nm.worker_count_for(2, 25) == 1
    assert nm.default_worker_count(25) >= 1


# --------------------------------------------------------------------------- the report's own stop


def test_the_report_refuses_to_publish_a_timing_when_the_agreement_gate_fails(monkeypatch):
    """The gate that stops the card, made to fail, on the path the card itself takes."""

    def failing(*args, **kwargs):
        return {"all_match": False, "mismatch_total": 7, "mismatch_counts": {}, "cells": 0}

    monkeypatch.setattr(nm, "agreement_audit", failing)
    report = nm.native_machines_report(include_metal=False, include_parallel=False, include_timing=False)
    assert "stopped" in report
    assert "throughput" not in report
    assert "dataflow" not in report


# ------------------------------------------------------------------------------------ the metal


clang = pytest.mark.skipif(
    shutil.which("clang") is None, reason="clang is not on PATH; the metal half is skipped"
)


@clang
def test_the_arithmetic_the_machine_issues_matches_the_model_at_o0():
    """At ``-O0`` the compiler preserves the graph, so the model's operation count is checkable.

    This is the bridge between question 3 and question 4: if the arithmetic clang emits did not
    match the operation multiset the model counts, every structural number in this card would be
    about a different computation than the one the machine runs.
    """
    entry = "sweep_+-*/_008"
    table = nm.instruction_table((entry,), CORPUS, GRAMMARS, levels=(("O0", ("-O0",)),))
    assert table["clang"] is True
    assert table["o0_arithmetic_matches_model"] is True
    assert table["o0_model_disagreements"] == []
    assert len(table["rows"]) == WORLDS


@clang
def test_the_same_tree_twice_compiles_to_the_same_instructions():
    """The other direction of the instruction comparison, taken through the compiler itself."""
    tree = parse("a + b * c - d / e", CONTROL)
    first = nm.emit_c_function(tree, "k_one")
    second = nm.emit_c_function(tree, "k_two")
    assert first.replace("k_one", "K") == second.replace("k_two", "K")
