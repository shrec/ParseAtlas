"""Cross-validation of ParseAtlas against the vendored independent implementation.

The whole module is skipped, with the actionable reason, when the frozen
repsearch snapshot under ``case_studies/`` is absent.
"""

import itertools
import os

import pytest

from parseatlas import cross_validation
from parseatlas.cross_validation import (
    CROSS_VALIDATION_CORPUS,
    REMOVABLE_RESTRICTION_PROBES,
    UNDECIDED_RELATIONS,
    SnapshotUnavailable,
    _refines,
    compare,
    cross_validation_report,
    divergence_search,
    grammar_correspondence,
    parseatlas_partition,
    repsearch_partition,
    repsearch_unevaluated,
    resolve_workers,
    restriction_detail,
    screen_for_restriction_divergence,
    snapshot_status,
    token_sequences,
)
from parseatlas.grammar import OPERATORS, strict_grammars

_available, _reason = snapshot_status()
if not _available:
    pytest.skip(_reason, allow_module_level=True)

#: A small generated slice of the divergence-search space.  The published sweep
#: is ``token_sequences(3)`` over ``{x, y, 1, 2}`` and ``{+, -, *, /}`` -- 16384
#: sequences and roughly a minute and a half of wall time, which does not belong
#: in the suite.  This slice is 128 sequences, runs in a couple of seconds, and
#: still contains ``x / x - x - 1``, one of the two divergences the report reads
#: out in full.
SLICE_ATOMS = ("x", "1")
SLICE_OPERATORS = ("-", "/")


@pytest.fixture(scope="module")
def corpus_report():
    return cross_validation_report(CROSS_VALIDATION_CORPUS)


@pytest.fixture(scope="module")
def probe_report():
    return cross_validation_report(REMOVABLE_RESTRICTION_PROBES)


@pytest.fixture(scope="module")
def search_slice():
    return token_sequences(3, atoms=SLICE_ATOMS, operators=SLICE_OPERATORS)


@pytest.fixture(scope="module")
def slice_screen(search_slice):
    return screen_for_restriction_divergence(search_slice, workers=1)


@pytest.fixture(scope="module")
def slice_search(search_slice):
    return divergence_search(search_slice, workers=1)


# -- snapshot loading -------------------------------------------------------


def test_snapshot_is_loaded_by_path_not_from_the_package_path():
    modules = cross_validation.load_repsearch()
    assert set(modules) == set(cross_validation.REQUIRED_SNAPSHOT_MODULES)
    assert cross_validation.SNAPSHOT_ROOT.name == "repsearch_snapshot"
    assert "case_studies" in cross_validation.SNAPSHOT_ROOT.parts
    assert modules["repsearch.grammar"].__file__.startswith(str(cross_validation.SNAPSHOT_ROOT))


def test_missing_snapshot_produces_an_actionable_reason(tmp_path, monkeypatch):
    monkeypatch.setattr(cross_validation, "SNAPSHOT_ROOT", tmp_path / "absent")
    available, reason = snapshot_status()
    assert available is False
    assert "missing" in reason
    assert "experiment/representation-search" in reason
    monkeypatch.setattr(cross_validation, "_LOADED", {})
    with pytest.raises(SnapshotUnavailable) as error:
        cross_validation.load_repsearch()
    assert str(tmp_path / "absent") in str(error.value)


# -- the grammar identifier correspondence is derived, not assumed ----------


def test_grammar_correspondence_is_derived_from_itertools_permutations():
    modules = cross_validation.load_repsearch()
    assert tuple(modules["repsearch.expr"].BINARY_OPS) == tuple(OPERATORS)

    expected = tuple(itertools.permutations(OPERATORS))
    correspondence = grammar_correspondence()
    assert len(correspondence) == 24
    assert tuple(order for _, order in correspondence) == expected
    assert tuple(identifier for identifier, _ in correspondence) == tuple(
        item.id for item in strict_grammars()
    )
    assert tuple(tuple(order) for order in modules["repsearch.grammar"].PRECEDENCE_ORDERS) == expected
    assert correspondence[0] == ("G01", ("+", "-", "*", "/"))
    assert correspondence[-1] == ("G24", ("/", "*", "-", "+"))


def test_correspondence_agrees_on_binding_power_for_every_grammar():
    precedence_map = cross_validation.load_repsearch()["repsearch.grammar"].precedence_map
    registry = {item.id: item for item in strict_grammars()}
    for identifier, order in grammar_correspondence():
        assert registry[identifier].binding_power == precedence_map(order)


def test_correspondence_fails_loudly_when_the_orders_stop_agreeing(monkeypatch):
    grammar = cross_validation.load_repsearch()["repsearch.grammar"]
    monkeypatch.setattr(grammar, "PRECEDENCE_ORDERS", list(reversed(grammar.PRECEDENCE_ORDERS)))
    with pytest.raises(AssertionError):
        grammar_correspondence()


# -- the eight-expression identity result -----------------------------------


def test_eight_expression_corpus_gives_identical_partitions(corpus_report):
    assert corpus_report["total"] == 8
    assert corpus_report["identical"] == 8
    assert corpus_report["refinement"] == 0
    assert corpus_report["divergent"] == 0
    assert corpus_report["undecided"] == 0
    for detail in corpus_report["details"]:
        assert detail["identical"] is True
        assert detail["relation"] == "identical"
        assert detail["repsearch_unevaluated"] == ()


def test_corpus_identity_is_partition_membership_not_class_counts(corpus_report):
    for detail in corpus_report["details"]:
        assert detail["parseatlas_partition"] == detail["repsearch_partition"]
        union = sorted(item for block in detail["parseatlas_partition"] for item in block)
        assert union == [f"G{index:02d}" for index in range(1, 25)]


def test_corpus_class_counts(corpus_report):
    counts = {detail["expression"]: detail["parseatlas_class_count"] for detail in corpus_report["details"]}
    assert counts == {
        "2*t + 1 - t/2": 8,
        "3*x + 2 - x/3": 8,
        "2*x*x + 1 - x/2": 8,
        "a + b*c - d/e": 10,
        "a - b*c + d/e - f": 16,
        "x*x - 1": 2,
        "2*x + 3": 2,
        "a/b + c*d - e/f + g": 18,
    }


def test_equal_class_counts_alone_do_not_make_partitions_identical():
    """Membership, not counts: two partitions of equal shape can still differ."""
    left = (("G01", "G02"), ("G03", "G04"))
    right = (("G01", "G03"), ("G02", "G04"))
    assert len(left) == len(right)
    assert left != right
    assert not _refines(left, right)
    assert not _refines(right, left)


def _equal_sized_but_different_partitions():
    """Two real oracle partitions of the same 24 grammars with two classes each.

    Both are produced by the production code -- ``2*x + 3`` through ParseAtlas
    and ``x*x - 1`` through repsearch -- over the same universe, both have
    exactly two classes, and their classes hold different grammars.  Neither
    refines the other, so the pair is exactly what separates "same number of
    classes" from "same partition".
    """
    left = parseatlas_partition("2*x + 3")
    right = repsearch_partition("x*x - 1")
    assert len(left) == len(right) == 2
    assert left != right
    assert sorted(item for block in left for item in block) == sorted(
        item for block in right for item in block
    )
    return left, right


def test_compare_decides_on_membership_not_on_class_counts(monkeypatch):
    """The decision inside ``compare`` must be partition equality, not counting.

    This drives the production path: ``compare`` is called, and the second
    oracle really returns a repsearch partition -- just the one for a different
    source, so the two partitions have the same size and different membership.
    Replacing ``left == right`` with ``len(left) == len(right)`` makes this fail.
    """
    left, right = _equal_sized_but_different_partitions()
    monkeypatch.setattr(cross_validation, "repsearch_partition", lambda source: right)
    result = compare("2*x + 3")
    assert result["parseatlas_partition"] == left
    assert result["repsearch_partition"] == right
    assert result["compared_universe"] == tuple(f"G{index:02d}" for index in range(1, 25))
    assert result["compared_parseatlas_class_count"] == 2
    assert result["compared_repsearch_class_count"] == 2
    assert result["identical"] is False
    assert result["relation"] == "incomparable"
    assert result["refinement"] is None


def test_report_identical_counter_decides_on_membership_not_on_class_counts(monkeypatch):
    """The aggregate 8/8 counter inherits the same discrimination.

    ``workers=1`` keeps the comparison in this process so the substituted oracle
    is the one the counter actually sees.
    """
    _, right = _equal_sized_but_different_partitions()
    monkeypatch.setattr(cross_validation, "repsearch_partition", lambda source: right)
    report = cross_validation_report(("2*x + 3",), workers=1)
    assert report["total"] == 1
    assert report["identical"] == 0
    assert report["divergent"] == 1
    assert report["undecided"] == 0


# -- compare() must never fail open ------------------------------------------


def test_an_empty_compared_universe_is_not_agreement():
    """``x/0``: repsearch evaluates nothing, so nothing was compared.

    Both partitions restrict to the empty partition, and the empty partition
    equals itself.  Reporting that as ``identical`` would turn "no comparison
    was possible" into "the two oracles agree".
    """
    result = compare("x/0")
    assert result["repsearch_unevaluated"] == tuple(f"G{index:02d}" for index in range(1, 25))
    assert result["compared_universe"] == ()
    assert result["identical"] is False
    assert result["relation"] == "incomparable_empty_universe"
    assert result["refinement"] is None
    assert "no common universe" in result["reason"]


def test_report_counts_an_empty_universe_separately_from_agreement():
    report = cross_validation_report(("x/0",), workers=1)
    assert report["total"] == 1
    assert report["identical"] == 0
    assert report["refinement"] == 0
    assert report["divergent"] == 0
    assert report["undecided"] == 1
    assert report["empty_universe"] == 1


def test_a_zero_denominator_literal_is_classified_not_raised():
    """``1/0`` is a rational literal to ParseAtlas; ``Fraction(1, 0)`` raises.

    The vendored snapshot must never be edited, so the failure is caught at this
    module's boundary and classified instead of escaping ``compare``.
    """
    result = compare("1/0")
    assert result["identical"] is False
    assert result["relation"] == "incomparable_unevaluable"
    assert result["reason"].startswith("ZeroDivisionError")


@pytest.mark.parametrize("source", ["x @ y", "x +", "(x"])
def test_sources_outside_the_language_are_classified_not_raised(source):
    result = compare(source)
    assert result["identical"] is False
    assert result["relation"] == "incomparable_unevaluable"
    assert result["reason"].startswith("ValueError")


def test_a_tokenizer_disagreement_is_not_an_oracle_disagreement():
    """``1/2`` is one rational literal to ParseAtlas and ``1 / 2`` to repsearch.

    The two oracles would then be answering about different expressions, and the
    comparison reads as ``repsearch_strictly_finer`` -- a false counterexample to
    the measured asymmetry.  It is refused instead.
    """
    assert cross_validation._parseatlas_lexical_shape("1/2 + x") == (
        ("num", "1/2"),
        ("op", "+"),
        ("name", "x"),
    )
    assert cross_validation._repsearch_lexical_shape("1/2 + x") == (
        ("num", "1"),
        ("op", "/"),
        ("num", "2"),
        ("op", "+"),
        ("name", "x"),
    )
    result = compare("1/2 + x")
    assert result["identical"] is False
    assert result["relation"] == "incomparable_lexical_mismatch"
    assert result["refinement"] is None


def test_the_two_tokenizers_agree_on_every_published_source():
    """No published number rests on an undecided input."""
    for source in CROSS_VALIDATION_CORPUS + REMOVABLE_RESTRICTION_PROBES:
        assert cross_validation._parseatlas_lexical_shape(
            source
        ) == cross_validation._repsearch_lexical_shape(source)


def test_the_aggregate_accounting_is_exhaustive():
    sources = ("x*x - 1", "2*x + 3", "x / x - x - 1", "x/0", "1/0", "1/2 + x")
    report = cross_validation_report(sources, workers=1)
    assert report["total"] == 6
    assert (
        report["identical"] + report["refinement"] + report["divergent"] + report["undecided"]
        == report["total"]
    )
    assert report["identical"] == 2
    assert report["refinement"] == 1
    assert report["parseatlas_strictly_finer"] == 1
    assert report["repsearch_strictly_finer"] == 0
    assert report["divergent"] == 0
    assert report["undecided"] == 3
    assert (report["empty_universe"], report["unevaluable"], report["lexical_mismatch"]) == (1, 1, 1)
    relations = {item["relation"] for item in report["details"]}
    assert relations == {
        "identical",
        "parseatlas_strictly_finer",
        *UNDECIDED_RELATIONS,
    }


def test_refinement_predicate_recognises_a_strict_refinement():
    finer = (("G01",), ("G02",), ("G03", "G04"))
    coarser = (("G01", "G02"), ("G03", "G04"))
    assert _refines(finer, coarser)
    assert not _refines(coarser, finer)


# -- removable-restriction probes -------------------------------------------


def test_removable_restriction_probes_agree_on_all_four(probe_report):
    assert probe_report["total"] == 4
    assert probe_report["identical"] == 4
    assert probe_report["undecided"] == 0
    relations = {item["expression"]: item["relation"] for item in probe_report["details"]}
    assert set(relations.values()) == {"identical"}


def test_x_over_x_keeps_the_restriction_in_the_parseatlas_key():
    detail = restriction_detail("x/x")
    assert len(detail) == 1
    assert detail[0]["canonical"] == "1"
    assert detail[0]["excluded_points"] == ("0",)
    assert len(detail[0]["grammars"]) == 24
    assert parseatlas_partition("x/x") == repsearch_partition("x/x")


@pytest.mark.parametrize(
    ("source", "canonical", "excluded"),
    [
        ("x/x - x - 1", "-x", {(), ("0",)}),
        ("x - y/y - x", "-1", {("y",), ("0",)}),
    ],
)
def test_parseatlas_is_strictly_finer_where_a_restriction_differs(source, canonical, excluded):
    result = compare(source)
    assert result["identical"] is False
    assert result["relation"] == "parseatlas_strictly_finer"
    assert result["refinement"] == "parseatlas"
    assert result["repsearch_class_count"] == 1
    assert result["parseatlas_class_count"] == 2
    assert result["repsearch_unevaluated"] == ()
    detail = restriction_detail(source)
    assert {item["canonical"] for item in detail} == {canonical}
    assert {item["excluded_points"] for item in detail} == excluded


def test_zero_denominator_is_representable_for_only_one_oracle():
    """repsearch raises on a literally zero denominator; SymPy yields ``zoo``."""
    source = "x/x - x/x"
    unevaluated = repsearch_unevaluated(source)
    assert len(unevaluated) == 12
    assert len(repsearch_partition(source)) == 1
    detail = restriction_detail(source)
    assert {item["canonical"] for item in detail} == {"zoo", "0"}
    result = compare(source)
    assert len(result["compared_universe"]) == 12
    assert result["identical"] is True
    assert result["parseatlas_class_count"] == 2
    assert result["repsearch_class_count"] == 1
    assert result["compared_parseatlas_class_count"] == 1
    assert result["compared_repsearch_class_count"] == 1


# -- the generated corpus and the divergence search --------------------------


def test_token_sequences_counts_are_exact():
    """The sizes the sweep quotes are a property of the generator, not a memory."""
    assert len(token_sequences(1)) == 64
    assert len(token_sequences(2)) == 1024
    assert len(token_sequences(3)) == 16384
    assert len(set(token_sequences(2))) == 1024
    assert len(token_sequences(3, atoms=SLICE_ATOMS, operators=SLICE_OPERATORS)) == 128


def test_token_sequences_enumerates_atoms_then_operators():
    assert token_sequences(1, atoms=("x", "1"), operators=("+", "/")) == (
        "x + x",
        "x / x",
        "x + 1",
        "x / 1",
        "1 + x",
        "1 / x",
        "1 + 1",
        "1 / 1",
    )
    for sequence in token_sequences(3, atoms=SLICE_ATOMS, operators=SLICE_OPERATORS):
        parts = sequence.split(" ")
        assert len(parts) == 7
        assert set(parts[0::2]) <= set(SLICE_ATOMS)
        assert set(parts[1::2]) <= set(SLICE_OPERATORS)


def test_structural_screen_narrows_the_slice_without_discarding_the_known_divergence(
    search_slice, slice_screen
):
    assert slice_screen["screened"] == 128
    assert slice_screen["parse_errors"] == ()
    assert set(slice_screen["candidates"]) <= set(search_slice)
    assert len(slice_screen["candidates"]) == 7
    assert len(slice_screen["candidates_with_full_universe"]) == 7
    assert len(slice_screen["sequences_with_unevaluated_grammars"]) == 24
    assert "x / x - x - 1" in slice_screen["candidates_with_full_universe"]


def test_divergence_direction_on_a_generated_slice(slice_search):
    """The second headline in miniature: every divergence points the same way.

    The published sweep is 16384 sequences; this is a 128-sequence slice of the
    same generator run end to end -- screen, confirmation, direction.
    """
    assert slice_search["screened"] == 128
    assert slice_search["structural_candidates"] == 7
    assert slice_search["confirmed_candidates"] == 7
    assert slice_search["sequences_with_unevaluated_grammars"] == 24
    assert slice_search["confirmed_divergences"] == 6
    assert slice_search["parseatlas_strictly_finer"] == 6
    assert slice_search["repsearch_strictly_finer"] == 0
    assert slice_search["incomparable"] == 0
    assert slice_search["undecided"] == 0
    assert slice_search["parse_errors"] == 0


def test_every_confirmed_divergence_is_parseatlas_strictly_finer(slice_search):
    expressions = {item["expression"] for item in slice_search["divergences"]}
    assert "x / x - x - 1" in expressions
    assert len(slice_search["divergences"]) == 6
    for detail in slice_search["divergences"]:
        assert detail["relation"] == "parseatlas_strictly_finer"
        assert detail["refinement"] == "parseatlas"
        assert detail["identical"] is False
        assert detail["repsearch_unevaluated"] == ()
        finer = detail["parseatlas_partition"]
        coarser = detail["repsearch_partition"]
        assert len(finer) > len(coarser)
        assert _refines(finer, coarser)
        assert not _refines(coarser, finer)


def test_the_divergences_differ_only_in_the_excluded_points(slice_search):
    """Same canonical form on both sides of the split; only the domain differs."""
    for detail in slice_search["divergences"]:
        classes = restriction_detail(detail["expression"])
        assert len({item["canonical"] for item in classes}) == 1
        assert len({item["excluded_points"] for item in classes}) == len(classes) > 1


# -- worker derivation and the sequential path ------------------------------


def test_worker_count_is_derived_from_the_core_count_with_headroom():
    cores = os.cpu_count() or 1
    assert resolve_workers(1024) == max(1, cores - 2)
    assert resolve_workers(1024) <= cores
    assert resolve_workers(3) == min(3, max(1, cores - 2))
    assert resolve_workers(1024, 1) == 1
    with pytest.raises(ValueError):
        resolve_workers(4, 0)


def test_sequential_path_produces_the_same_result_as_the_parallel_path():
    sources = ("x*x - 1", "2*x + 3")
    sequential = cross_validation_report(sources, workers=1)
    parallel = cross_validation_report(sources)
    assert sequential["workers"] == 1
    assert parallel["workers"] == min(2, max(1, (os.cpu_count() or 1) - 2))
    assert sequential["details"] == parallel["details"]
    assert sequential["identical"] == parallel["identical"] == 2
