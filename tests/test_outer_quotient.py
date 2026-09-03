"""Tests for experiment 0032: an outer function quotients the inner equivalence classes.

The load-bearing test is :func:`test_coarsening_holds_for_every_pair_in_the_corpus`, and it runs
the whole 24-source by 13-function sweep because that is the claim being made.  It is the one
expensive test here; everything else works on :data:`SUB_CORPUS`, on :data:`RESIDUE_SOURCES` or
on directly constructed arguments.

Two tests exist purely so that a green coarsening test cannot be mistaken for a check that never
fires.  :func:`test_the_coarsening_check_is_not_vacuous` fabricates a split and demands that it
be reported.  :func:`test_the_corpus_can_actually_break_the_coarsening_check` demands that the
corpus contain sources on which the outer key genuinely varies inside an inner class -- the first
version of this experiment reported 0 violations from a corpus where it could not, which is how
NF-2026-00004 survived 260 passing pairs.
"""

import os

import pytest
from sympy import Abs, cos, pi, simplify, sin, srepr, tan

from parseatlas import outer_quotient
from parseatlas.canonical import to_sympy
from parseatlas.functions import OUTER_FUNCTIONS, analyze_outer_functions, canonical_argument
from parseatlas.grammar import all_grammars
from parseatlas.parser import parse
from parseatlas.outer_quotient import (
    CORPUS,
    FOUNDING_SOURCE,
    FUNCTION_ALGEBRA,
    SINGULARITY_FUNCTIONS,
    SUB_CORPUS,
    VARIABLE,
    WORKER_CAP,
    WORKER_HEADROOM_CORES,
    argument_period,
    class_representative,
    default_worker_count,
    inner_partition,
    merge_mechanism,
    merge_report,
    outer_partition,
    outer_real_domain,
    quotient_check,
    singularity_and_domain_effects,
    worker_count_for,
)

T = VARIABLE

#: The corpus sources whose grammars denote one value through structurally different SymPy trees.
#: Only these exercise the coarsening check at all; see the module docstring of ``outer_quotient``.
RESIDUE_SOURCES = ("3 * 2 - t / 2 - t", "1 + t + t * 2 / t", "t * t - 3 / 2", "2*(t - 1)/(t - 1)")

EVEN_FUNCTIONS = ("cos", "abs", "square")
INJECTIVE_FUNCTIONS = ("exp", "log", "sqrt", "asin", "acos", "atan", "reciprocal", "cube")
PERIODIC_FUNCTIONS = ("sin", "cos", "tan")


@pytest.fixture(scope="module")
def full_report():
    """The whole corpus against every outer function; the coarsening claim is about all of it."""
    return merge_report()


@pytest.fixture(scope="module")
def inner_partitions():
    return {source: inner_partition(source) for source in CORPUS}


# ---------------------------------------------------------------------------
# The corpus itself
# ---------------------------------------------------------------------------


def test_corpus_is_the_founding_sequence_plus_at_least_fifteen_more():
    assert CORPUS[0] == FOUNDING_SOURCE == "2*t + 1 - t/2"
    assert len(CORPUS) == 24
    assert len(set(CORPUS)) == len(CORPUS)
    for source in RESIDUE_SOURCES:
        assert source in CORPUS, source
    for source in CORPUS:
        for grammar in all_grammars():
            assert to_sympy(parse(source, grammar)).free_symbols <= {VARIABLE}
        # Every source is written in ``t``: ``functions.py`` differentiates with respect to ``t``
        # when it reports frequency and period, so another variable would be misread as constant.
        assert "t" in source


def test_corpus_spans_affine_quadratic_and_rational_shapes(inner_partitions):
    canonicals = {source: [item["canonical"] for item in partition["classes"]] for source, partition in inner_partitions.items()}
    assert any("**2" in text for texts in canonicals.values() for text in texts)
    assert any(item["excluded_points"] for partition in inner_partitions.values() for item in partition["classes"])
    assert any(partition["class_count"] >= 12 for partition in inner_partitions.values())
    assert sum(partition["class_count"] for partition in inner_partitions.values()) == 127


# ---------------------------------------------------------------------------
# The owner's question
# ---------------------------------------------------------------------------


def test_founding_sequence_has_eight_inner_classes():
    partition = inner_partition(FOUNDING_SOURCE)
    assert partition["grammar_count"] == 25
    assert partition["class_count"] == 8
    assert sum(len(item["grammars"]) for item in partition["classes"]) == 25
    assert len(partition["class_by_grammar"]) == 25
    assert len({item["key"] for item in partition["classes"]}) == 8


def test_the_eight_belongs_to_the_inner_sequence_and_not_to_sin(full_report):
    """Every one of the thirteen outer functions returns the same 8 on the founding sequence."""
    founding = [pair for pair in full_report["pairs"] if pair["source"] == FOUNDING_SOURCE]
    assert {pair["function"] for pair in founding} == set(OUTER_FUNCTIONS)
    for pair in founding:
        assert pair["inner_class_count"] == 8, pair["function"]
        assert pair["outer_class_count"] == 8, pair["function"]
        assert pair["merge_count"] == 0, pair["function"]


def test_inner_and_outer_keys_use_the_same_triple_discipline():
    inner = inner_partition(FOUNDING_SOURCE)
    assert all(item["key"][1] == "R" for item in inner["classes"])
    assert all(len(item["key"]) == 3 for item in inner["classes"])
    logarithm = outer_partition(FOUNDING_SOURCE, "log")
    assert all(len(item["key"]) == 3 for item in logarithm["classes"])
    # The outer key's domain slot is the composed real domain, which is where log records its
    # boundary; the collapsed-argument class is the one that has no boundary left.
    domains = {item["canonical"]: item["key"][1] for item in logarithm["classes"]}
    assert domains["log(3*t/2 + 1)"] == "Interval.open(-2/3, oo)"
    assert domains["0"] == "Reals"


# ---------------------------------------------------------------------------
# The coarsening claim
# ---------------------------------------------------------------------------


def test_coarsening_holds_for_every_pair_in_the_corpus(full_report):
    assert full_report["pair_count"] == len(CORPUS) * len(OUTER_FUNCTIONS) == 312
    assert full_report["coarsening_failures"] == 0
    assert full_report["coarsening_holds_everywhere"] is True
    assert full_report["coarsening_pairs"] == 312
    assert full_report["split_pairs"] == 0
    for pair in full_report["pairs"]:
        assert pair["violations"] == [], (pair["source"], pair["function"])
        assert pair["split_count"] == 0, (pair["source"], pair["function"])
        assert pair["outer_class_count"] <= pair["inner_class_count"], (pair["source"], pair["function"])
        assert pair["class_count_delta"] == pair["inner_class_count"] - pair["outer_class_count"]
        # The structure-derived merge count and the class-count difference are two definitions of
        # the same number, and they agree exactly while the pair is a coarsening.  That agreement
        # is the whole justification for preferring the structural one, which stays honest when
        # the pair is not.
        assert pair["merge_count"] == pair["class_count_delta"]
        assert pair["merge_count"] >= 0


# ---------------------------------------------------------------------------
# The check has to be able to fail (NF-2026-00004)
# ---------------------------------------------------------------------------


def test_the_corpus_can_actually_break_the_coarsening_check(inner_partitions):
    """At least one inner class per residue source must hold structurally different parse trees.

    Without this the coarsening test is vacuous: if every grammar of an inner class leaves the
    same SymPy tree, the outer key is constant on that class for trivial reasons and no key
    defect can show.  That is precisely the state the first version of this experiment was in,
    and it reported 0 violations in 260 pairs from it.
    """
    grammars = all_grammars()
    residue_classes = {}
    for source in CORPUS:
        for item in inner_partitions[source]["classes"]:
            trees = {srepr(to_sympy(parse(source, g))) for g in grammars if g.id in item["grammars"]}
            if len(trees) > 1:
                residue_classes.setdefault(source, []).append((item["canonical"], len(trees)))
    assert set(residue_classes) == set(RESIDUE_SOURCES)

    # The minimal reproducer, spelled out: one value, two trees, one of them an uncancelled
    # removable singularity, and both readings carrying the same excluded point.
    partition = inner_partitions["3 * 2 - t / 2 - t"]
    victim = next(item for item in partition["classes"] if item["canonical"] == "3")
    forms = {str(to_sympy(parse("3 * 2 - t / 2 - t", g))) for g in grammars if g.id in victim["grammars"]}
    assert forms == {"3", "(6 - 3*t)/(2 - t)"}
    assert victim["excluded_points"] == ["2"]
    assert len(victim["grammars"]) == 8
    assert simplify("(6 - 3*t)/(2 - t)") == 3


def test_the_domain_slot_is_a_function_of_the_denoted_value(inner_partitions):
    """NF-2026-00004: the outer key must not vary inside an inner class.

    Pre-fix, ``functions.py`` composed the outer function on the raw parse tree before taking
    ``continuous_domain``, so ``log`` on ``3 * 2 - t / 2 - t`` split one inner class into two
    outer classes -- ``Reals`` against ``Union(Interval.open(-oo, 2), Interval.open(2, oo))`` --
    and reported ``C_inner 4, C_f 5, merge_count -1``.
    """
    grammars = all_grammars()
    for source in RESIDUE_SOURCES:
        for function_name in ("log", "sqrt", "tan", "abs", "reciprocal"):
            report = analyze_outer_functions(source, (function_name,), grammars)
            by_grammar = {item["grammar"]: item for item in report["results"]}
            for item in inner_partitions[source]["classes"]:
                keys = {
                    (
                        by_grammar[g]["canonical"],
                        by_grammar[g]["properties"]["real_domain"],
                        tuple(by_grammar[g]["inner_excluded_points"]),
                    )
                    for g in item["grammars"]
                }
                assert len(keys) == 1, (source, function_name, item["canonical"], sorted(keys))

    result = quotient_check("3 * 2 - t / 2 - t", "log")
    assert result["is_coarsening"] is True
    assert result["inner_class_count"] == 4
    assert result["outer_class_count"] == 4
    assert result["merge_count"] == 0
    assert result["class_count_delta"] == 0
    collapsed = next(item for item in result["outer_classes"] if item["canonical"] == "log(3)")
    # The removable singularity is not lost, it is where it belongs: in the excluded points, not
    # in a domain slot that disagrees between two spellings of the same value.
    assert collapsed["domain"] == "Reals"
    assert collapsed["excluded_points"] == ["2"]
    assert len(collapsed["grammars"]) == 8


def test_the_canonical_slot_is_composed_on_the_canonical_argument():
    """The same defect reached the canonical slot, not only the domain slot.

    ``simplify(f(raw_tree))`` and ``simplify(f(raw_tree'))`` can land on different fixed points
    for two spellings of one value: pre-fix, ``log`` on ``t * t - 3 / 2`` produced both
    ``log(t*(t - 3)) - log(2)`` and ``log(t*(t - 3)/2)``, and ``abs`` on ``1 + t + t * 2 / t``
    produced both ``2*Abs(2 + 1/t)`` and ``Abs(4 + 2/t)``.  Composing on the canonical argument
    fixes both, because there is then only one argument to compose on.
    """
    grammars = all_grammars()
    for source, inner_canonical, function_name, canonical, domain in (
        ("t * t - 3 / 2", "t*(t - 3)/2", "log", "log(t*(t - 3)/2)",
         "Union(Interval.open(-oo, 0), Interval.open(3, oo))"),
        ("1 + t + t * 2 / t", "4 + 2/t", "abs", "Abs(4 + 2/t)",
         "Union(Interval.open(-oo, 0), Interval.open(0, oo))"),
    ):
        partition = inner_partition(source)
        report = analyze_outer_functions(source, (function_name,))
        by_grammar = {item["grammar"]: item for item in report["results"]}
        victim = next(item for item in partition["classes"] if item["canonical"] == inner_canonical)
        # The class really does hold more than one parse tree, or the assertion below is vacuous.
        assert len({srepr(to_sympy(parse(source, g))) for g in grammars if g.id in victim["grammars"]}) > 1
        assert {by_grammar[g]["canonical"] for g in victim["grammars"]} == {canonical}
        assert {by_grammar[g]["properties"]["real_domain"] for g in victim["grammars"]} == {domain}

    # ``canonical_argument`` is the single place that decides what "the value" is, and every
    # consumer of a composed domain goes through it.
    assert str(canonical_argument(simplify("(6 - 3*t)/(2 - t)"))) == "3"


def test_the_coarsening_check_is_not_vacuous(monkeypatch):
    """A fabricated split must be reported as a violation, or the passing test above means nothing."""
    honest = outer_partition(FOUNDING_SOURCE, "sin")

    def splitting_partition(source, function_name, grammars=None):
        partition = dict(honest)
        classes = [{**item, "grammars": list(item["grammars"])} for item in honest["classes"]]
        victim = next(item for item in classes if len(item["grammars"]) > 1)
        moved = victim["grammars"].pop()
        classes.append({**victim, "id": "FXX", "canonical": victim["canonical"] + " (split)", "grammars": [moved]})
        partition["classes"] = classes
        partition["class_by_grammar"] = {gid: item["id"] for item in classes for gid in item["grammars"]}
        partition["class_count"] = len(classes)
        return partition

    monkeypatch.setattr(outer_quotient, "outer_partition", splitting_partition)
    result = quotient_check(FOUNDING_SOURCE, "sin")
    assert result["is_coarsening"] is False
    assert len(result["violations"]) == 1
    violation = result["violations"][0]
    assert len(violation["outer_classes"]) == 2
    assert violation["inner_canonical"]
    # A split pair has no merge count and no merges: the old ``C_inner - C_f`` is -1 here, and
    # that -1 is exactly what used to be summed into every aggregate downstream.
    assert result["merge_count"] is None
    assert result["merges"] == []
    assert result["class_count_delta"] == -1
    assert result["split_count"] == 1
    assert result["outer_class_count"] > result["inner_class_count"]


def test_aggregates_refuse_to_count_merges_from_a_violating_pair(monkeypatch):
    """A violation must be surfaced by the summary, never averaged into it.

    Measured on the pre-fix sweep of 34 residue sources: ``total_merges`` ``-130``, ``tan`` at a
    mean of ``-1.088`` merges per source, and ``merges_anywhere`` false for ``cos``, ``abs`` and
    ``square`` although each of the three had a genuine parity merge in that same run.  This test
    fabricates the same arithmetic in miniature and pins the guarded behaviour.
    """
    real_outer_partition = outer_quotient.outer_partition

    def splitting_partition(source, function_name, grammars=None):
        partition = real_outer_partition(source, function_name, grammars)
        if source != FOUNDING_SOURCE:
            return partition
        classes = [{**item, "grammars": list(item["grammars"])} for item in partition["classes"]]
        victim = next(item for item in classes if len(item["grammars"]) > 1)
        moved = victim["grammars"].pop()
        classes.append({**victim, "id": "FXX", "canonical": victim["canonical"] + " (split)", "grammars": [moved]})
        partition = dict(partition)
        partition["classes"] = classes
        partition["class_by_grammar"] = {gid: item["id"] for item in classes for gid in item["grammars"]}
        partition["class_count"] = len(classes)
        return partition

    monkeypatch.setattr(outer_quotient, "outer_partition", splitting_partition)
    # ``2 - 2 + t`` carries a real parity merge for ``cos``; the founding source is fabricated
    # into a split.  Unguarded, the -1 from the split cancels the +1 from the merge.
    report = merge_report((FOUNDING_SOURCE, "2 - 2 + t"), ("cos", "sin"), workers=1)

    assert report["coarsening_failures"] == 2
    assert report["coarsening_pairs"] == 2
    assert report["split_pairs"] == 2
    broken = next(pair for pair in report["pairs"] if pair["source"] == FOUNDING_SOURCE and pair["function"] == "cos")
    assert broken["is_coarsening"] is False
    assert broken["merge_count"] is None
    assert broken["merges"] == []
    assert broken["class_count_delta"] == -1
    assert broken["split_count"] == 1
    assert broken["violations"]

    genuine = next(pair for pair in report["pairs"] if pair["source"] == "2 - 2 + t" and pair["function"] == "cos")
    assert genuine["merge_count"] == 1
    assert genuine["merges"][0]["mechanisms"][0]["mechanism"] == "parity"

    assert report["total_merges"] == 1  # not 1 + (-1) == 0
    cosine = report["per_function"]["cos"]
    assert cosine["total_merges"] == 1
    assert cosine["merges_anywhere"] is True
    assert cosine["coarsening_pairs"] == 1
    assert cosine["mean_merge_count"] == 1.0  # a mean over the pairs that had a merge count
    assert cosine["mechanisms"] == {"parity": 1}
    assert cosine["merge_evidence_complete"] is False
    assert cosine["coarsening_failures"] == 1

    # ``sin`` merged nowhere, but with an unmeasurable pair in the sweep that is not a finding.
    sine = report["per_function"]["sin"]
    assert sine["total_merges"] == 0
    assert sine["merges_anywhere"] is False
    assert sine["predicted_can_merge"] is True
    assert sine["merge_evidence_complete"] is False
    assert sine["capability_unrealised"] is False


def test_every_inner_class_lands_in_exactly_one_outer_class():
    result = quotient_check(FOUNDING_SOURCE, "cos")
    outer_of = {item["id"]: item for item in result["outer_classes"]}
    for inner in result["inner_classes"]:
        reached = {
            next(oid for oid, item in outer_of.items() if grammar_id in item["grammars"])
            for grammar_id in inner["grammars"]
        }
        assert len(reached) == 1


# ---------------------------------------------------------------------------
# Injective functions merge nothing
# ---------------------------------------------------------------------------


def test_injective_outer_functions_merge_nothing_on_genuinely_distinct_classes(full_report):
    inner = inner_partition(FOUNDING_SOURCE)
    canonicals = [item["canonical"] for item in inner["classes"]]
    assert len(set(canonicals)) == 8, "the eight inner classes must be genuinely distinct"
    for function_name in INJECTIVE_FUNCTIONS:
        pair = next(
            item
            for item in full_report["pairs"]
            if item["source"] == FOUNDING_SOURCE and item["function"] == function_name
        )
        assert pair["merge_count"] == 0, function_name
        assert pair["merges"] == [], function_name
        assert pair["outer_class_count"] == pair["inner_class_count"] == 8


def test_no_injective_function_merges_anywhere_in_the_corpus(full_report):
    for function_name in INJECTIVE_FUNCTIONS:
        cell = full_report["per_function"][function_name]
        assert cell["predicted_can_merge"] is False
        assert cell["total_merges"] == 0, function_name
        assert cell["contradicts_algebra"] is False, function_name
        # "merged nowhere" is only a finding when every pair was measurable.
        assert cell["merge_evidence_complete"] is True, function_name


# ---------------------------------------------------------------------------
# Parity merges
# ---------------------------------------------------------------------------


def test_even_functions_merge_a_class_with_its_negation():
    for function_name in EVEN_FUNCTIONS:
        result = quotient_check("2 - 2 + t", function_name)
        assert result["inner_class_count"] == 2
        assert result["outer_class_count"] == 1
        assert result["merge_count"] == 1
        merge = result["merges"][0]
        assert sorted(merge["inner_canonicals"]) == ["-t", "t"]
        assert merge["mechanisms"][0]["mechanism"] == "parity"
    # The merged pair really is a negation, and the outer values really do coincide.
    assert simplify(T + (-T)) == 0
    assert simplify(cos(T) - cos(-T)) == 0
    assert simplify(Abs(T) - Abs(-T)) == 0
    assert simplify(T**2 - (-T) ** 2) == 0


def test_odd_functions_do_not_merge_a_class_with_its_negation():
    for function_name in ("sin", "tan", "cube"):
        result = quotient_check("2 - 2 + t", function_name)
        assert result["merge_count"] == 0, function_name
        assert result["outer_class_count"] == 2, function_name


def test_parity_is_the_only_mechanism_that_fires_on_this_corpus(full_report):
    mechanisms = {name: cell["mechanisms"] for name, cell in full_report["per_function"].items() if cell["mechanisms"]}
    assert set(mechanisms) == set(EVEN_FUNCTIONS)
    assert all(cell == {"parity": 4} for cell in mechanisms.values())
    assert full_report["total_merges"] == 12
    for function_name in EVEN_FUNCTIONS:
        cell = full_report["per_function"][function_name]
        assert cell["sources_with_merge"] == 4
        assert cell["total_merges"] == 4
        # The denominator is the measurable pairs, which on a clean sweep is the whole corpus.
        assert cell["coarsening_pairs"] == len(CORPUS)
        assert cell["merge_evidence_complete"] is True
        assert cell["mean_merge_count"] == pytest.approx(4 / len(CORPUS))


# ---------------------------------------------------------------------------
# Periodic merges
# ---------------------------------------------------------------------------


def test_a_periodic_function_merges_in_the_corpus_and_the_pair_is_explained(full_report):
    """``cos`` is the periodic function that does merge here, and it merges by its own identity."""
    merging = [pair for pair in full_report["pairs"] if pair["function"] == "cos" and pair["merge_count"]]
    assert merging
    for pair in merging:
        merge = pair["merges"][0]
        left, right = merge["inner_canonicals"][0], merge["inner_canonicals"][1]
        assert merge["mechanisms"][0]["mechanism"] == "parity"
        assert simplify(f"({left}) + ({right})") == 0
        assert simplify(cos(simplify(left)) - cos(simplify(right))) == 0


def test_period_merges_are_detected_when_the_arguments_do_differ_by_a_period():
    """Constructed directly, because the token language cannot produce such a pair (see below)."""
    sine = merge_mechanism("sin", T, T + 2 * pi)
    assert sine["mechanism"] == "period"
    assert sine["detail"] == "argument difference 2*pi = 1 * 2*pi"
    assert simplify(sin(T + 2 * pi) - sin(T)) == 0

    tangent = merge_mechanism("tan", 3 * T, 3 * T + pi)
    assert tangent["mechanism"] == "period"
    assert simplify(tan(3 * T + pi) - tan(3 * T)) == 0

    cosine = merge_mechanism("cos", T / 2 + 1, T / 2 + 1 - 4 * pi)
    assert cosine["mechanism"] == "period"
    assert simplify(cos(T / 2 + 1 - 4 * pi) - cos(T / 2 + 1)) == 0

    assert merge_mechanism("sin", T, pi - T)["mechanism"] == "reflection"
    assert merge_mechanism("cos", T + 1, -T - 1 + 2 * pi)["mechanism"] == "parity-period"
    assert merge_mechanism("exp", T, T + 1)["mechanism"] == "unclassified"


def test_no_period_merge_is_reachable_from_this_token_language(full_report, inner_partitions):
    """Two readings of one token sequence differ by a rational function over the rationals.

    Every period of ``sin``, ``cos`` and ``tan`` is an irrational multiple of ``pi``, so a nonzero
    ``pi``-free difference can never be one.  The measured absence of period merges is therefore a
    property of the language, not a gap in the corpus.
    """
    for source, partition in inner_partitions.items():
        representatives = [class_representative(source, item["grammars"][0]) for item in partition["classes"]]
        assert len({str(item) for item in representatives}) == len(representatives), source
        for index, left in enumerate(representatives):
            for right in representatives[index + 1 :]:
                assert not (right - left).has(pi), (source, str(right - left))
    for pair in full_report["pairs"]:
        for merge in pair["merges"]:
            for mechanism in merge["mechanisms"]:
                assert mechanism["mechanism"] != "period", (pair["source"], pair["function"])
    for function_name in ("sin", "tan"):
        cell = full_report["per_function"][function_name]
        assert cell["predicted_can_merge"] is True
        assert cell["merges_anywhere"] is False
        assert cell["merge_evidence_complete"] is True
        assert cell["capability_unrealised"] is True


# ---------------------------------------------------------------------------
# Periods reported by functions.py stay correct
# ---------------------------------------------------------------------------


def test_tangent_period_is_pi_over_slope_and_sine_is_two_pi_over_slope():
    """``functions.py`` must keep ``pi/|a|`` for tan and ``2*pi/|a|`` for sin and cos."""
    checked = 0
    for source in SUB_CORPUS:
        partition = inner_partition(source)
        for function_name in PERIODIC_FUNCTIONS:
            reported = analyze_outer_functions(source, (function_name,))
            by_grammar = {item["grammar"]: item["properties"] for item in reported["results"]}
            for item in partition["classes"]:
                expression = class_representative(source, item["grammars"][0])
                expected = argument_period(function_name, expression)
                properties = by_grammar[item["grammars"][0]]
                if expected is None:
                    assert properties.get("period") in (None, "undefined (constant argument)")
                    continue
                assert properties["period"] == str(expected), (source, function_name, item["canonical"])
                checked += 1
    assert checked > 0

    assert argument_period("tan", T / 2 + 1) == 2 * pi
    assert argument_period("sin", T / 2 + 1) == 4 * pi
    assert argument_period("cos", -2 * T) == pi
    assert argument_period("tan", 3 * T / 2) == 2 * pi / 3
    assert argument_period("sin", 3 * T / 2) == 4 * pi / 3
    assert argument_period("exp", T) is None
    assert argument_period("sin", T * 0 + 1) is None
    assert argument_period("sin", T**2) is None


def test_the_founding_periods_of_experiment_0002_are_unchanged():
    founding = analyze_outer_functions(FOUNDING_SOURCE, ("sin", "tan"))
    sine = next(item for item in founding["results"] if item["grammar"] == "G03" and item["function"] == "sin")
    tangent = next(item for item in founding["results"] if item["grammar"] == "G03" and item["function"] == "tan")
    assert sine["properties"]["frequency"] == "1/2"
    assert sine["properties"]["period"] == "4*pi"
    assert tangent["properties"]["period"] == "2*pi"
    assert str(argument_period("sin", class_representative(FOUNDING_SOURCE, "G03"))) == "4*pi"
    assert str(argument_period("tan", class_representative(FOUNDING_SOURCE, "G03"))) == "2*pi"
    assert str(class_representative(FOUNDING_SOURCE, "G03")) == "t/2 + 1"


# ---------------------------------------------------------------------------
# Singularities and domains
# ---------------------------------------------------------------------------


def test_tangent_poles_vanish_exactly_when_the_argument_collapses_to_a_constant():
    effects = singularity_and_domain_effects(("2*t + 1 - t/2",), ("tan",), workers=1)
    cell = effects["per_source"][0]
    for entry in cell["classes"]:
        assert entry["unrestricted"] == entry["constant_argument"], entry["canonical"]
    collapsed = [entry for entry in cell["classes"] if entry["constant_argument"]]
    assert len(collapsed) == 1
    assert collapsed[0]["canonical"] == "tan(1)"
    assert collapsed[0]["real_domain"] == "Reals"
    assert sorted(collapsed[0]["grammars"]) == ["G01", "G02", "G07", "G08"]
    assert effects["totals"]["tan_classes_without_poles"] == 1
    assert effects["totals"]["tan_classes_with_poles"] == 7


def test_log_and_sqrt_boundaries_move_across_grammars_of_one_token_sequence():
    effects = singularity_and_domain_effects(("2*t + 1 - t/2",), ("log", "sqrt"), workers=1)
    for cell in effects["per_source"]:
        assert cell["distinct_boundaries"] == 6
        assert len(cell["classes"]) == 8
        unrestricted = [entry for entry in cell["classes"] if entry["unrestricted"]]
        assert len(unrestricted) == 1
        assert unrestricted[0]["constant_argument"] is True
    assert effects["totals"]["log_boundary_moves"] == 1
    assert effects["totals"]["sqrt_boundary_moves"] == 1
    assert outer_real_domain(FOUNDING_SOURCE, "log", "G0") == "Interval.open(-2/3, oo)"
    assert outer_real_domain(FOUNDING_SOURCE, "log", "G03") == "Interval.open(-2, oo)"
    assert outer_real_domain(FOUNDING_SOURCE, "log", "G01") == "Reals"
    assert outer_real_domain(FOUNDING_SOURCE, "sqrt", "G11") == "Interval(-1, oo)"


def test_reciprocal_poles_move_and_vanish():
    effects = singularity_and_domain_effects(("2/t - 1/t + t", "5 - 5 + 1/t"), ("reciprocal",), workers=1)
    moving = next(cell for cell in effects["per_source"] if cell["source"] == "2/t - 1/t + t")
    assert moving["distinct_pole_sets"] > 1
    poles = {entry["canonical"]: entry["pole_set"] for entry in moving["classes"]}
    assert poles["-t/(t**2 - 1)"] == "{-1, 1}"
    assert poles["t*(t - 1)"] == "EmptySet"
    vanishing = next(cell for cell in effects["per_source"] if cell["source"] == "5 - 5 + 1/t")
    empty = [entry for entry in vanishing["classes"] if entry["pole_set"] == "EmptySet"]
    assert len(empty) == 2
    assert effects["totals"]["reciprocal_pole_moves"] == 2
    assert len(effects["totals"]["reciprocal_pole_vanishing_cases"]) >= 2


def test_singularity_report_rejects_functions_it_does_not_cover():
    with pytest.raises(ValueError):
        singularity_and_domain_effects(SUB_CORPUS, ("exp",), workers=1)
    assert set(SINGULARITY_FUNCTIONS) == {"tan", "log", "sqrt", "reciprocal"}


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------


def test_sequential_and_parallel_agree():
    functions = ("sin", "cos", "abs")
    sequential = merge_report(SUB_CORPUS, functions, workers=1)
    parallel = merge_report(SUB_CORPUS, functions, workers=2)
    sequential.pop("worker_count")
    parallel.pop("worker_count")
    assert sequential == parallel
    assert sequential["pair_count"] == len(SUB_CORPUS) * len(functions)


def test_worker_count_is_derived_from_cores_and_leaves_headroom():
    assert worker_count_for(8) == 8 - WORKER_HEADROOM_CORES
    assert worker_count_for(16) == WORKER_CAP
    assert worker_count_for(1) == 1
    assert worker_count_for(2) == 1
    assert worker_count_for(64) == WORKER_CAP
    assert 1 <= default_worker_count() <= max(1, os.cpu_count() or 1)


def test_reports_reject_empty_and_unknown_input():
    with pytest.raises(ValueError):
        merge_report((), ("sin",))
    with pytest.raises(ValueError):
        merge_report(SUB_CORPUS, ("tangent",))
    with pytest.raises(ValueError):
        outer_partition(FOUNDING_SOURCE, "tangent")


def test_function_algebra_covers_every_outer_function():
    assert set(FUNCTION_ALGEBRA) == set(OUTER_FUNCTIONS)
    assert {name for name, item in FUNCTION_ALGEBRA.items() if item["period"] is not None} == set(PERIODIC_FUNCTIONS)
    assert {name for name, item in FUNCTION_ALGEBRA.items() if item["even"]} == set(EVEN_FUNCTIONS)
    assert {name for name, item in FUNCTION_ALGEBRA.items() if item["injective_on_reals"]} == set(INJECTIVE_FUNCTIONS)
    assert FUNCTION_ALGEBRA["tan"]["period"] == pi
    assert FUNCTION_ALGEBRA["sin"]["period"] == FUNCTION_ALGEBRA["cos"]["period"] == 2 * pi
