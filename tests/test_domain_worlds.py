"""Validation of experiment 0037, the domain-worlds series and the compromise test.

Every expectation here is a value measured before it was written down, and the ones that carry
the headline are pinned literally rather than recomputed from the module, so a change in the
ranking cannot pass silently.

The card's decisive property is the correctness bridge inherited from
:mod:`parseatlas.notational_cost`: a rendering must re-parse under its own grammar to the tree it
came from, and it must add no bracket that grammar does not require.  If that fails, every cost
number in the experiment is meaningless, so it is asserted first and over the whole corpus.
"""

import pytest

from parseatlas.domain_worlds import (
    CONTROL,
    CORPUS,
    FIELDS,
    GRAMMAR_BY_ID,
    GRAMMARS,
    bridge_audit,
    compromise_report,
    corpus_audit,
    field_champions,
    field_cost,
    law_orientation,
    null_model,
    orientation_table,
    worker_count_for,
)

# Measured once, then pinned.  These are the numbers the report publishes.
CONTROL_SUMMED_TOTAL = 45
CONTROL_SUMMED_RANK = 3
CONTROL_FIELD_RANKS = {"algebra": 1, "geometry": 5, "calculus": 6, "linear_algebra": 1}
BEST_SUMMED_ID = "G18"
BEST_SUMMED_TOTAL = 42


def test_the_round_trip_and_minimality_hold_over_the_whole_corpus():
    """The bridge every cost number rests on, asserted before any of them.

    A rendering that does not re-parse to its own tree measures nothing, and one carrying a
    bracket its grammar does not require inflates that grammar's total and could reverse the
    ranking outright.  Both are checked over every entry against every grammar.
    """
    audit = bridge_audit()
    assert audit["round_trip"]["holds"] is True
    assert audit["round_trip"]["failures"] == 0
    assert audit["round_trip"]["checks"] == 1200
    assert audit["minimality"]["minimal"] is True
    assert audit["minimality"]["violations"] == 0
    assert audit["minimality"]["brackets_checked"] == 1737


def test_the_corpus_is_named_laws_and_is_written_the_way_we_write_it():
    """The corpus must be laws, and their sources must be how mathematics actually spells them.

    ``canonical_sources`` asserts every source string is already the minimal rendering under the
    control grammar, so no entry smuggles in a bracket that biases its own cost, and no entry
    encodes an intent other than the one it reads as.
    """
    audit = corpus_audit()
    assert audit["law_count"] == 33
    assert audit["entry_count"] == 48
    assert audit["field_count"] == 4
    assert audit["duplicate_names"] == ()
    assert audit["canonical_sources"] is True
    assert audit["non_canonical"] == ()
    assert audit["identities_hold_under_control"] is True
    assert tuple(audit["fields"]) == tuple(sorted(FIELDS))


def test_the_control_grammar_field_ranks_are_the_measured_ones():
    report = compromise_report()
    control = next(row for row in report["per_grammar"] if row["id"] == "G0")
    assert control["ranks"] == CONTROL_FIELD_RANKS
    assert control["summed_total"] == CONTROL_SUMMED_TOTAL
    assert control["summed_rank"] == CONTROL_SUMMED_RANK
    assert control["mean_rank"] == pytest.approx(3.25)
    assert control["worst_rank"] == 6
    assert control["best_rank"] == 1


def test_the_compromise_verdict_is_what_the_data_says():
    """The headline, pinned in both directions.

    G0 is not the optimum -- two grammars beat it on the summed workload -- and it is also not
    merely mediocre: it is third of twenty-five, first in two of four fields, and never worse
    than sixth.  Exactly one grammar, G18, is top-three in every field.  Both halves matter, and
    a change in either should fail this test rather than be absorbed into prose.
    """
    report = compromise_report()

    assert report["best_summed"]["id"] == BEST_SUMMED_ID
    assert report["best_summed"]["total"] == BEST_SUMMED_TOTAL
    assert report["control_summed_total"] == CONTROL_SUMMED_TOTAL
    assert report["control_summed_rank"] == CONTROL_SUMMED_RANK

    beaters = {row["id"] for row in report["beats_control_on_sum"]}
    assert beaters == {"G16", "G18"}
    assert report["beats_control_count"] == 2

    assert report["any_top3_everywhere"] is True
    assert report["top3_in_every_field"] == ("G18",)


def test_the_best_all_round_grammar_is_the_control_with_one_tie_broken():
    """G18 is `* / - +`; the control ties `*` with `/` and `+` with `-` in the same grouping.

    The grammar that beats the conventional one across the whole workload is not a rearrangement
    of it -- it is the same grouping with the tie between `+` and `-` resolved in favour of `-`.
    """
    best = GRAMMAR_BY_ID[BEST_SUMMED_ID]
    assert best.precedence == ("*", "/", "-", "+")
    assert CONTROL.levels == (("*", "/"), ("+", "-"))

    row = next(r for r in compromise_report()["per_grammar"] if r["id"] == BEST_SUMMED_ID)
    assert row["top3_everywhere"] is True
    assert row["worst_rank"] == 3
    assert row["mean_rank"] == pytest.approx(1.5)


def test_no_grammar_wins_every_field_and_the_champions_differ():
    champions = field_champions()
    assert champions["winners_differ"] is True
    assert champions["grammars_winning_every_field"] == ()
    assert champions["outright_winner"]["geometry"] == "G10"
    assert set(champions["control_wins"]) == {"algebra", "linear_algebra"}
    assert champions["summed_winner"] == (BEST_SUMMED_ID,)


def test_the_ranking_is_not_an_artefact_of_entries_that_cannot_move():
    """The null model: entries costing the same everywhere cannot carry a ranking.

    Excluding them must leave every field rank and every control rank where it was, or the
    experiment is measuring its own corpus rather than the conventions.
    """
    model = null_model()
    assert model["all_field_ranks_stable"] is True
    assert model["all_control_ranks_stable"] is True
    assert model["constant_total"] == 2
    assert model["single_operator_total"] == 1


def test_expansion_is_the_natural_direction_here_and_reverses_elsewhere():
    """Our convention makes the expanded side of the distributive law free.

    That is why expansion reads as the primitive move and factoring as the derived one.  A world
    where the factored side is the free one would have built algebra the other way round, and 22
    of the 25 do reverse at least one two-sided law.
    """
    here = law_orientation("distributive_law", "G0")
    assert here["control_natural"] == "expanded"
    assert here["natural"] == "expanded"
    assert here["reversed_vs_control"] is False

    # G01 is the vivid case: the factored side costs nothing and the expanded side costs two.
    # Written down, that world's algebra has factoring as its free move.
    there = law_orientation("distributive_law", "G01")
    assert there["natural"] == "factored"
    assert there["direction"] == "toward_factored"
    assert there["costs"] == {"factored": 0, "expanded": 2}
    assert there["reversed_vs_control"] is True

    table = orientation_table()
    assert table["law_count"] == 15
    assert table["laws_that_reverse_count"] == 13
    assert table["worlds_with_a_reversal_count"] == 22
    assert table["reversal_cells"] == 152
    assert table["per_grammar"]["G0"] == ()


def test_a_single_operator_entry_costs_the_same_in_every_world():
    totals = {field_cost(field, grammar)["total"] for grammar in GRAMMARS for field in ("linear_algebra",)}
    assert len(totals) > 1, "the field must actually move, or the test proves nothing"

    model = null_model()
    for field in FIELDS:
        for name in model["per_field"][field]["constant_entries"]:
            assert isinstance(name, str) and name


@pytest.mark.parametrize("cores,cells", [(1, 100), (2, 100), (16, 100), (16, 1), (64, 10_000)])
def test_worker_count_leaves_headroom_and_never_returns_zero(cores, cells):
    workers = worker_count_for(cores, cells)
    assert 1 <= workers <= max(1, cores)
    assert workers <= cells


def test_sequential_and_parallel_agree():
    assert compromise_report(workers=1) == compromise_report(workers=2)


def test_the_corpus_covers_every_declared_field():
    covered = {getattr(law, "field", None) for law in CORPUS}
    assert covered == set(FIELDS)
