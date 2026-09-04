"""Validation of experiment 0041: which worlds write parallel forms for free.

Every number here was measured before it was written down, and every headline is pinned as a
LITERAL rather than recomputed from the module, so a change in the result fails a test instead of
quietly rewriting the finding.

Four assertions come before the rest, because without them nothing else means anything:

* **the correctness bridge** - every rendering reparses to the tree it came from, over the whole
  (writing x world) grid, and every bracket counted is load-bearing.  Cost numbers computed
  alongside a broken round trip are void, and so are the depths, because "depth is a property of
  the tree and not of the world" IS the round-trip guarantee;
* **depth is computed right** - on hand-built trees whose critical path can be counted by eye;
* **every counted writing really denotes the object** - the identity filter is what stops a shallow
  tree for something else from being counted as a parallel form.  On this corpus SymPy rejects
  nothing, which is a fact about the corpus and is pinned as one; the filter is therefore also
  tested directly in both directions, on subtraction and division chains where it rejects four
  writings out of five;
* **the null-model split** - how many corpus entries can move between worlds and how many cannot.
  Question 3 of the card lives or dies here: if precedence cannot distinguish groupings of one
  repeated operator, then "no world parallelises a chain for free" is a parsing artifact and not a
  discovery, and it has to be reported as the former.

The file is ordered cheap-first on purpose: plumbing, depth, the filter, the ranking arithmetic and
the concurrency policy are checked on a handful of trees before anything sweeps 1.5 million of them,
so a broken invariant fails in seconds rather than after the whole space has been walked.
"""

import os
from functools import lru_cache

import pytest

from parseatlas import manifest_properties as origin
from parseatlas import notational_cost, visibility_ceiling
from parseatlas.canonical import operation_cost, to_sympy
from parseatlas.parallel_worlds import (
    CHAIN_LENGTHS,
    grid,
    CHAIN_OPERATORS,
    CONTROL,
    CORPUS,
    GRAMMARS,
    POOL_STARTUP_SECONDS,
    TREE_SECONDS,
    Subject,
    chain_subjects,
    competition_ranking,
    control_distinction,
    cost_depth_table,
    default_worker_count,
    depth,
    depth_invariance,
    filter_audit,
    law_subjects,
    minimality_audit,
    null_model,
    parallel_worlds_report,
    rank_correlation,
    round_trip_audit,
    should_parallelise,
    space_size,
    spearman,
    speedup_table,
    subject_tree,
    subject_word,
    support_invariance,
    tax_table,
    writings_of,
)
from parseatlas.parser import Binary, Variable, parse
from parseatlas.visibility_ceiling import same_object

# ---- corpus, measured then pinned ---------------------------------------------------------------

SUBJECTS = 58
LAW_SUBJECTS = 50
CHAIN_COUNT = 8

# ---- the identity filter, stage by stage --------------------------------------------------------
#
# The probe does all the discarding on this corpus and SymPy confirms every survivor.  A SymPy
# rejection count of ZERO is a property of THIS corpus, not evidence that the confirmation is
# unnecessary, so it is pinned as the corpus fact it is and the filter is exercised directly below.
SPACE_TOTAL = 1_511_800
PROBE_REJECTED = 1_510_153
PROBE_SURVIVORS = 1_647
SYMPY_CONFIRMED = 1_647
SYMPY_REJECTED = 0

# ---- the correctness bridge over the whole grid --------------------------------------------------
ROUND_TRIP_CHECKS = 41_175
MINIMALITY_BRACKETS = 158_021
DEPTH_INVARIANCE_CHECKS = 41_175

# ---- the headline tax numbers --------------------------------------------------------------------
BEST_TAX = 22
WORST_TAX = 25
TAX_SPREAD = 3
LEAST_TAXING_WORLDS = ("G03", "G09", "G10", "G13", "G15", "G16", "G19", "G21", "G22")
DISTINCT_TAX_TOTALS = (22, 23, 24, 25)

CONTROL_TAX_TOTAL = 25
CONTROL_TAX_RANK = 20
CONTROL_COST_RANK = 5
CONTROL_COST_TOTAL = 47
CONTROL_FREE_OBJECTS = 44

CHEAPEST_WORLD = "G18"
CHEAPEST_COST = 42
DEAREST_WORLD = "G19"
DEAREST_COST = 97

FREE_SOMEWHERE_TAXED_IN_CONTROL = (
    "calibration_quadratic.expanded",
    "circle.general",
    "taylor_second_term.standard",
)
FREE_EVERYWHERE_COUNT = 41
FREE_NOWHERE = (
    "binomial_cube.expanded",
    "perfect_square_trinomial.expanded",
    "parabola.standard",
    "chain_add_4",
    "chain_add_5",
    "chain_add_6",
    "chain_add_8",
    "chain_mul_4",
    "chain_mul_5",
    "chain_mul_6",
    "chain_mul_8",
)

RANK_CORRELATION = 0.16741799363331533

# ---- the null-model split --------------------------------------------------------------------------
MOVABLE = (
    "calibration_quadratic.expanded",
    "circle.general",
    "ellipse.standard",
    "hyperbola.standard",
    "quotient_rule.split",
    "taylor_second_term.standard",
)
MOVABLE_COUNT = 6
FORCED_COUNT = 52
FORCED_AT_ZERO = 41
FORCED_POSITIVE = 11
FORCED_FLOOR = 21
SINGLE_OPERATOR_FORCED = (
    "chain_rule.standard",
    "chain_add_4",
    "chain_add_5",
    "chain_add_6",
    "chain_add_8",
    "chain_mul_4",
    "chain_mul_5",
    "chain_mul_6",
    "chain_mul_8",
)
CHAIN_TAX_EVERY_WORLD = 16
SUPPORT_INVARIANCE_CHECKS = 24_525
MOVABLE_SPREAD = 3
BEST_MOVABLE = "G03"

# ---- what the tax buys ------------------------------------------------------------------------------
IMPROVABLE_COUNT = 14
MAX_DEPTH_SAVED = 4
TOTAL_SEQUENTIAL_DEPTH = 187
TOTAL_MIN_DEPTH = 162


@lru_cache(maxsize=None)
def table() -> dict:
    return tax_table()


@lru_cache(maxsize=None)
def nulls() -> dict:
    return null_model()


@lru_cache(maxsize=None)
def chain_table() -> dict:
    return tax_table(chain_subjects(), workers=1)


# ======================================================================== plumbing and declarations


def test_corpus_is_imported_not_reinvented() -> None:
    """The named-law half of the corpus is 0038/0039's own objects, by identity."""
    names = {item.name for item in origin.CORPUS}
    assert len(origin.CORPUS) == 34
    for subject in law_subjects():
        assert subject.name.split(".")[0] in names
    assert law_subjects() == law_subjects(origin.CORPUS)


def test_corpus_shape_is_declared() -> None:
    assert len(CORPUS) == SUBJECTS
    assert sum(1 for s in CORPUS if s.kind == "law") == LAW_SUBJECTS
    assert sum(1 for s in CORPUS if s.kind == "chain") == CHAIN_COUNT
    assert len({s.name for s in CORPUS}) == SUBJECTS


def test_chain_subjects_are_the_declared_chains() -> None:
    chains = chain_subjects()
    assert CHAIN_LENGTHS == (4, 5, 6, 8)
    assert CHAIN_OPERATORS == ("+", "*")
    assert [s.source for s in chains] == [
        "a + b + c + d",
        "a + b + c + d + e",
        "a + b + c + d + e + f",
        "a + b + c + d + e + f + g + h",
        "a * b * c * d",
        "a * b * c * d * e",
        "a * b * c * d * e * f",
        "a * b * c * d * e * f * g * h",
    ]
    assert [space_size(s) for s in chains] == [5, 14, 42, 429, 5, 14, 42, 429]


def test_the_bridge_functions_are_imported_by_identity() -> None:
    """Renderer, bracket rule and identity filter are 0034's and 0039's objects, not copies."""
    import parseatlas.parallel_worlds as module

    assert module.render is notational_cost.render
    assert module.parenthesis_cost is notational_cost.parenthesis_cost
    assert module.minimality_witnesses is notational_cost.minimality_witnesses
    assert module.same_object is visibility_ceiling.same_object
    assert module.probe_values is visibility_ceiling.probe_values
    assert module.evaluate is visibility_ceiling.evaluate


# ================================================================================== depth, by eye


def test_depth_of_hand_built_trees() -> None:
    """Leaves are 0, a node is 1 + max(children).  Counted by eye, not by the module."""
    assert depth(parse("a", CONTROL)) == 0
    assert depth(parse("a + b", CONTROL)) == 1
    assert depth(parse("a + b + c", CONTROL)) == 2
    assert depth(parse("a + b + c + d", CONTROL)) == 3
    assert depth(parse("(a + b) + (c + d)", CONTROL)) == 2
    assert depth(parse("a * (b + c * (d + e))", CONTROL)) == 4


def test_depth_of_a_tree_built_without_the_parser() -> None:
    """A tree assembled by hand, so the depth cannot come from a parse accident."""
    leaf = Variable("a")
    assert depth(leaf) == 0
    assert depth(Binary("+", leaf, leaf)) == 1
    assert depth(Binary("+", Binary("*", leaf, leaf), leaf)) == 2
    balanced = Binary("+", Binary("+", leaf, leaf), Binary("+", leaf, leaf))
    chained = Binary("+", Binary("+", Binary("+", leaf, leaf), leaf), leaf)
    assert depth(balanced) == 2
    assert depth(chained) == 3


def test_depth_is_the_imported_operation_cost_minus_one() -> None:
    """The off-by-one against canonical's convention is declared, so it is asserted here."""
    for source in ("a", "a + b", "a * b + c * d", "a + b + c + d + e"):
        tree = parse(source, CONTROL)
        assert depth(tree) == operation_cost(tree)["depth"] - 1


def test_balanced_is_shallower_than_the_chain_at_every_declared_length() -> None:
    """The premise of the whole card, checked before any world is priced."""
    for length in CHAIN_LENGTHS:
        word = " + ".join("abcdefgh"[:length])
        assert depth(parse(word, CONTROL)) == length - 1


# =============================================================== the identity filter, both ways


def test_identity_filter_accepts_a_reassociation_that_keeps_the_object() -> None:
    reference = to_sympy(parse("a + b + c", CONTROL))
    assert same_object(parse("a + (b + c)", CONTROL), reference) is True
    product = to_sympy(parse("a * b * c", CONTROL))
    assert same_object(parse("a * (b * c)", CONTROL), product) is True


def test_identity_filter_rejects_a_reassociation_that_changes_the_object() -> None:
    reference = to_sympy(parse("a - b - c", CONTROL))
    assert same_object(parse("a - (b - c)", CONTROL), reference) is False
    quotient = to_sympy(parse("a / b / c", CONTROL))
    assert same_object(parse("a / (b / c)", CONTROL), quotient) is False


def test_the_filter_is_load_bearing_on_non_associative_chains() -> None:
    """Four of five parenthesizations are a DIFFERENT object, and the filter removes exactly those.

    This is the direct, two-directional exercise of the filter that the corpus itself cannot give,
    because on the published corpus SymPy rejects nothing (pinned separately below).
    """
    minus = Subject("probe_minus", "chain", "control", "a - b - c - d")
    divide = Subject("probe_div", "chain", "control", "a / b / c / d")
    plus = Subject("probe_plus", "chain", "control", "a + b + c + d")
    assert space_size(minus) == 5
    assert len(writings_of(minus, workers=1)) == 1
    assert space_size(divide) == 5
    assert len(writings_of(divide, workers=1)) == 1
    assert space_size(plus) == 5
    assert len(writings_of(plus, workers=1)) == 5


def test_the_sympy_confirmation_is_load_bearing_where_the_probe_is_undefined() -> None:
    """A constructed word on which the probe cannot decide and SymPy must.

    On the published corpus SymPy rejects nothing, so nothing there shows the confirmation step
    doing work.  The word ``p / q - q`` does: one of its two parenthesizations is ``p / (q - q)``,
    which is undefined at BOTH declared probe points, so the probe passes it through - and it is not
    the object, so SymPy is the only thing that removes it.
    """
    subject = Subject("probe_undefined", "chain", "control", "p / q - q")
    audit = filter_audit((subject,), workers=1)
    assert audit["space_total"] == 2
    assert audit["probe_rejected"] == 0
    assert audit["probe_survivors"] == 2
    assert audit["sympy_confirmed"] == 1
    assert audit["sympy_rejected"] == 1
    assert writings_of(subject, workers=1) == (("-", ("/", "L0", "L1"), "L2"),)


def test_every_counted_writing_really_denotes_the_object() -> None:
    """Re-confirm the filter's verdict independently on a subject small enough to check whole."""
    subject = chain_subjects((5,), ("*",))[0]
    leaves, _operators = subject_word(subject)
    reference = to_sympy(subject_tree(subject))
    forms = writings_of(subject, workers=1)
    assert len(forms) == 14
    for form in forms:
        assert same_object(visibility_ceiling.rebuild(form, leaves), reference) is True


# ================================================================== ranking and correlation maths


def test_competition_ranking_shares_a_rank_and_skips_the_next() -> None:
    assert competition_ranking({"a": 3, "b": 1, "c": 1, "d": 5}) == (
        {"rank": 1, "id": "b", "total": 1},
        {"rank": 1, "id": "c", "total": 1},
        {"rank": 3, "id": "a", "total": 3},
        {"rank": 4, "id": "d", "total": 5},
    )


def test_spearman_endpoints_and_ties() -> None:
    assert spearman([1, 2, 3, 4], [1, 2, 3, 4]) == pytest.approx(1.0)
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert spearman([1, 1, 2, 2], [1, 2, 1, 2]) == pytest.approx(0.0)
    assert spearman([1, 2, 3], [7, 7, 7]) == 0.0
    with pytest.raises(ValueError):
        spearman([1, 2], [1])
    with pytest.raises(ValueError):
        spearman([1], [1])


def test_adding_a_constant_cannot_move_a_rank() -> None:
    """Why the forced floor cannot influence the ranking, asserted rather than argued."""
    base = {"a": 3, "b": 1, "c": 4}
    shifted = {key: value + 21 for key, value in base.items()}
    assert [e["id"] for e in competition_ranking(base)] == [
        e["id"] for e in competition_ranking(shifted)
    ]


# ============================================================== concurrency policy, both directions


def test_worker_count_comes_from_the_observed_cores() -> None:
    cores = os.cpu_count() or 1
    assert default_worker_count(433) == max(1, min(cores - 2, 12, 433))
    assert default_worker_count(3) == max(1, min(cores - 2, 12, 3))
    assert default_worker_count(0) >= 1


def test_the_parallel_decision_is_arithmetic_on_two_measurements() -> None:
    assert should_parallelise(SPACE_TOTAL, TREE_SECONDS, 12) is True
    assert should_parallelise(1000, TREE_SECONDS, 12) is False
    assert should_parallelise(SPACE_TOTAL, TREE_SECONDS, 1) is False
    assert should_parallelise(1, TREE_SECONDS, 12) is False
    assert POOL_STARTUP_SECONDS == 1.3
    assert TREE_SECONDS == 1.8e-05


def test_sequential_and_parallel_agree() -> None:
    """Parallelism changes only how fast, never what is measured."""
    assert tax_table(chain_subjects(), workers=1) == tax_table(chain_subjects(), workers=4)


# ============================================================ the null model, on the chains alone


def test_a_chain_is_free_only_as_the_sequential_writing_in_every_world() -> None:
    """Question 3, and the answer is FORCED: no world writes a balanced chain for free."""
    rows = {row["object"]: row for row in chain_table()["rows"]}
    for name, row in rows.items():
        assert row["free_world_count"] == 0, name
        assert set(row["min_cost"].values()) == {0}, name
        assert row["tax_range"] == 0, name
    assert set(chain_table()["tax_totals"].values()) == {CHAIN_TAX_EVERY_WORLD}
    assert set(chain_table()["cost_totals"].values()) == {0}


def test_chain_tax_is_the_parallel_prefix_gap() -> None:
    """``n - 1`` sequential against ``ceil(log2 n)`` balanced, per chain, identical in all 25."""
    expected = {
        "chain_add_4": (3, 2, 1),
        "chain_add_5": (4, 3, 1),
        "chain_add_6": (5, 3, 2),
        "chain_add_8": (7, 3, 4),
        "chain_mul_4": (3, 2, 1),
        "chain_mul_5": (4, 3, 1),
        "chain_mul_6": (5, 3, 2),
        "chain_mul_8": (7, 3, 4),
    }
    rows = {row["object"]: row for row in chain_table()["rows"]}
    for name, (written, minimum, tax) in expected.items():
        assert rows[name]["written_depth"] == written, name
        assert rows[name]["min_depth"] == minimum, name
        assert set(rows[name]["tax"].values()) == {tax}, name


def test_cost_depth_table_of_one_chain_is_the_whole_argument_in_five_rows() -> None:
    subject = chain_subjects((4,), ("+",))[0]
    cell = cost_depth_table(subject, CONTROL, workers=1)
    assert cell["writing_count"] == 5
    assert cell["min_cost"] == 0
    assert cell["free_depth"] == 3
    assert cell["min_depth"] == 2
    assert cell["cost_of_min_depth"] == 1
    assert cell["premium"] == 1
    assert cell["tax"] == 1
    assert cell["shallowest_is_free"] is False
    texts = {row["text"]: (row["cost"], row["depth"]) for row in cell["writings"]}
    assert texts["a + b + c + d"] == (0, 3)
    assert texts["a + b + (c + d)"] == (1, 2)


def test_support_reduction_forces_the_chain_result() -> None:
    """T6 verified on this corpus, not cited: one operator, one price, in all 25 worlds."""
    audit = support_invariance()
    assert audit["single_operator_subjects"] == SINGLE_OPERATOR_FORCED
    assert audit["single_operator_count"] == len(SINGLE_OPERATOR_FORCED)
    assert audit["checks"] == SUPPORT_INVARIANCE_CHECKS
    assert audit["mismatch_count"] == 0
    assert audit["holds"] is True


# ================================================================== the full grid: what it cost


def test_filter_audit_pins_both_stages() -> None:
    audit = filter_audit()
    assert audit["subjects"] == SUBJECTS
    assert audit["space_total"] == SPACE_TOTAL
    assert audit["trees_probed"] == SPACE_TOTAL
    assert audit["fully_enumerated"] is True
    assert audit["probe_rejected"] == PROBE_REJECTED
    assert audit["probe_survivors"] == PROBE_SURVIVORS
    assert audit["sympy_confirmed"] == SYMPY_CONFIRMED
    # A corpus fact, pinned as one: SymPy rejects NOTHING the exact probe let through here.
    assert audit["sympy_rejected"] == SYMPY_REJECTED


def test_round_trip_holds_over_the_whole_grid() -> None:
    audit = round_trip_audit()
    assert audit["checks"] == ROUND_TRIP_CHECKS
    assert audit["failures"] == 0
    assert audit["holds"] is True
    assert audit["depth_stable"] is True


def test_every_bracket_counted_is_load_bearing() -> None:
    audit = minimality_audit()
    assert audit["brackets_checked"] == MINIMALITY_BRACKETS
    assert audit["violations"] == 0
    assert audit["minimal"] is True


def test_depth_of_a_fixed_tree_is_the_same_in_all_twenty_five_worlds() -> None:
    """The premise that forces the question one level up, measured rather than assumed."""
    audit = depth_invariance()
    assert audit["checks"] == DEPTH_INVARIANCE_CHECKS
    assert audit["always_one_depth"] is True
    assert audit["distinct_depth_counts"] == (1,)


# ====================================================================== the headline tax numbers


def test_tax_totals_and_ranking() -> None:
    result = table()
    assert result["subjects"] == SUBJECTS
    assert result["worlds"] == 25
    assert tuple(sorted(set(result["tax_totals"].values()))) == DISTINCT_TAX_TOTALS
    assert result["best_tax"] == BEST_TAX
    assert result["best_worlds"] == LEAST_TAXING_WORLDS
    assert result["worst_tax"] == WORST_TAX
    assert result["tax_spread"] == TAX_SPREAD


def test_control_is_in_the_joint_worst_tax_group_and_the_cheap_cost_group() -> None:
    result = table()
    assert result["control_tax_total"] == CONTROL_TAX_TOTAL
    assert result["control_tax_rank"] == CONTROL_TAX_RANK
    assert result["control_cost_rank"] == CONTROL_COST_RANK
    assert result["cost_totals"]["G0"] == CONTROL_COST_TOTAL
    assert result["control_free_objects"] == CONTROL_FREE_OBJECTS
    assert result["cost_ranking"][0]["id"] == CHEAPEST_WORLD
    assert result["cost_ranking"][0]["total"] == CHEAPEST_COST
    assert result["cost_ranking"][-1]["id"] == DEAREST_WORLD
    assert result["cost_ranking"][-1]["total"] == DEAREST_COST


def test_objects_free_somewhere_but_taxed_in_the_conventional_world() -> None:
    """Question 1 of the card, pinned by name."""
    result = table()
    assert result["objects_free_somewhere_taxed_in_control"] == FREE_SOMEWHERE_TAXED_IN_CONTROL
    assert len(result["objects_free_everywhere"]) == FREE_EVERYWHERE_COUNT
    assert result["objects_free_nowhere"] == FREE_NOWHERE


def test_rank_correlation_between_cost_and_tax() -> None:
    """Question 4: cheap to write and parallel to write are all but unrelated here."""
    result = rank_correlation()
    assert result["full_corpus"] == pytest.approx(RANK_CORRELATION)
    # The forced floor is a constant, so it cannot move a rank: the two correlations must agree.
    assert result["movable_subcorpus"] == pytest.approx(RANK_CORRELATION)
    assert result["agree_exactly"] is False
    assert table()["rank_correlation"] == pytest.approx(RANK_CORRELATION)


def test_the_dearest_world_to_write_in_is_among_the_least_taxing() -> None:
    """The concrete shape of a near-zero correlation, pinned so it cannot be smoothed away."""
    result = table()
    assert result["cost_ranks"][DEAREST_WORLD] == 25
    assert result["tax_ranks"][DEAREST_WORLD] == 1
    assert result["cost_ranks"][CHEAPEST_WORLD] == 1
    assert result["tax_ranks"][CHEAPEST_WORLD] == 10


# ====================================================================== the null model, in full


def test_null_model_split() -> None:
    """How many corpus entries CAN move between worlds, and how many cannot."""
    result = nulls()
    assert result["movable_count"] == MOVABLE_COUNT
    assert result["movable_subjects"] == MOVABLE
    assert result["forced_count"] == FORCED_COUNT
    assert result["forced_at_zero_count"] == FORCED_AT_ZERO
    assert result["forced_positive_count"] == FORCED_POSITIVE
    assert result["single_operator_forced"] == SINGLE_OPERATOR_FORCED
    assert result["single_operator_forced_count"] == len(SINGLE_OPERATOR_FORCED)
    assert MOVABLE_COUNT + FORCED_COUNT == SUBJECTS


def test_most_of_the_tax_is_forced_and_the_ranking_rests_on_six_objects() -> None:
    result = nulls()
    assert result["forced_floor"] == FORCED_FLOOR
    assert set(result["chain_tax_per_world"].values()) == {CHAIN_TAX_EVERY_WORLD}
    assert tuple(sorted(set(result["movable_tax_totals"].values()))) == (1, 2, 3, 4)
    # every world's total is the forced floor plus its movable remainder
    for world in (g.id for g in GRAMMARS):
        assert table()["tax_totals"][world] == FORCED_FLOOR + result["movable_tax_totals"][world]


def test_the_ranking_survives_the_null_model_unchanged() -> None:
    result = nulls()
    assert result["movable_spread"] == MOVABLE_SPREAD
    assert result["full_spread"] == TAX_SPREAD
    assert result["spread_survival"] == 1.0
    assert result["ranking_identical"] is True
    assert result["best_full"] == BEST_MOVABLE
    assert result["best_movable"] == BEST_MOVABLE
    assert result["control_rank_full"] == CONTROL_TAX_RANK
    assert result["control_rank_movable"] == CONTROL_TAX_RANK
    assert result["control_rank_stable"] is True


# ============================================================================ what the tax buys


def test_speedup_table_is_a_bound_and_says_so() -> None:
    result = speedup_table()
    assert "not a measured runtime" in result["not_a_benchmark"]
    assert result["subjects"] == SUBJECTS
    assert result["improvable_count"] == IMPROVABLE_COUNT
    assert result["max_depth_saved"] == MAX_DEPTH_SAVED
    assert result["max_ratio"] == pytest.approx(7 / 3)
    assert result["total_sequential_depth"] == TOTAL_SEQUENTIAL_DEPTH
    assert result["total_min_depth"] == TOTAL_MIN_DEPTH
    assert result["deepest"] == "circle.general"


def test_the_deepest_object_and_its_movement() -> None:
    rows = {row["object"]: row for row in table()["rows"]}
    circle = rows["circle.general"]
    assert circle["space"] == 742_900
    assert circle["writing_count"] == 36
    assert circle["written_depth"] == 7
    assert circle["min_depth"] == 5
    assert circle["control_tax"] == 2
    assert circle["free_world_count"] == 12


def test_the_conventional_world_is_alone_at_the_top_of_the_deepest_object() -> None:
    """On ``circle.general`` no other world charges two; twelve charge nothing and twelve charge one."""
    circle = next(row for row in table()["rows"] if row["object"] == "circle.general")
    taxes = circle["tax"]
    assert taxes["G0"] == 2
    assert [w for w, t in taxes.items() if t == 2] == ["G0"]
    assert sum(1 for t in taxes.values() if t == 0) == 12
    assert sum(1 for t in taxes.values() if t == 1) == 12


def test_the_three_forced_positive_law_writings() -> None:
    """Multi-operator entries whose tax is positive and identical in all 25 worlds."""
    rows = {row["object"]: row for row in table()["rows"]}
    expected = {
        "binomial_cube.expanded": (6, 4, 2, 3),
        "perfect_square_trinomial.expanded": (4, 3, 1, 1),
        "parabola.standard": (6, 4, 2, 2),
    }
    for name, (written, minimum, tax, premium) in expected.items():
        row = rows[name]
        assert row["written_depth"] == written, name
        assert row["min_depth"] == minimum, name
        assert set(row["tax"].values()) == {tax}, name
        assert set(row["premium"].values()) == {premium}, name
        assert row["support_size"] > 1, name


def test_the_three_objects_the_conventional_world_gets_free_and_others_do_not() -> None:
    """The reverse direction of question 1: G0 free, eight worlds charged, premium named."""
    rows = {row["object"]: row for row in table()["rows"]}
    for name in ("ellipse.standard", "hyperbola.standard", "quotient_rule.split"):
        row = rows[name]
        assert row["tax"]["G0"] == 0, name
        assert row["free_world_count"] == 17, name
        assert sum(1 for t in row["tax"].values() if t == 1) == 8, name


# ================================================================ question 5: does G0 stand out


def test_control_holds_one_distinction_and_it_is_a_pair_not_a_coordinate() -> None:
    result = control_distinction()
    assert result["values"] == {"tax_total": 25, "cost_total": 47, "free_objects": 44}
    assert result["shared_counts"] == {"tax_total": 6, "cost_total": 2, "free_objects": 4}
    assert result["unique_coordinates"] == ()
    assert result["unique_pairs"] == ("tax_and_free",)
    assert result["pairs"]["tax_and_free"] == ("G0",)
    assert result["free_only_in_control"] == ()
    assert result["taxed_only_in_control"] == ()
    assert result["worst_tax_group"] is True


# =============================================================================== the whole report


def test_report_headline_agrees_with_the_pinned_numbers() -> None:
    report = parallel_worlds_report()
    headline = report["headline"]
    assert headline["free_somewhere_taxed_in_control"] == FREE_SOMEWHERE_TAXED_IN_CONTROL
    assert headline["least_taxing_worlds"] == LEAST_TAXING_WORLDS
    assert headline["least_tax"] == BEST_TAX
    assert headline["control_tax_total"] == CONTROL_TAX_TOTAL
    assert headline["control_tax_rank"] == CONTROL_TAX_RANK
    assert headline["chains_forced"] == len(SINGLE_OPERATOR_FORCED)
    assert headline["movable_subjects"] == MOVABLE_COUNT
    assert headline["rank_correlation_full"] == pytest.approx(RANK_CORRELATION)
    assert report["corpus"] == {
        "subjects": SUBJECTS,
        "laws": LAW_SUBJECTS,
        "chains": CHAIN_COUNT,
        "fields": tuple(sorted({s.field for s in CORPUS})),
    }
    assert report["round_trip"]["holds"] is True
    assert report["minimality"]["minimal"] is True
    assert report["filter"]["sympy_rejected"] == SYMPY_REJECTED


# ---- the tie-break, pinned after review found it undisclosed ------------------------------------

#: Cells whose tax depends on which of several equally cheap writings is taken.
TIEBREAK_SENSITIVE_CELLS = 52
#: The objects those cells belong to -- exactly the movable set the ranking rests on.
TIEBREAK_SENSITIVE_OBJECTS = (
    "calibration_quadratic.expanded",
    "circle.general",
    "ellipse.standard",
    "hyperbola.standard",
    "quotient_rule.split",
    "taylor_second_term.standard",
)
PESSIMISTIC_BEST_TAX = 23
PESSIMISTIC_BEST_WORLDS = ("G07", "G18")
#: The cost-versus-tax correlation under each tie-break.  The optimistic figure is the one
#: section 5 of the reports quotes; the pessimistic one is two and a half times larger, which
#: is why the choice is disclosed rather than left in the code.
CORRELATION_OPTIMISTIC = 0.167418
CORRELATION_PESSIMISTIC = 0.422211


def test_the_tax_tie_break_is_a_choice_and_its_sensitivity_is_pinned_not_latent():
    """``tax`` resolves a tie in the world's favour, and that choice alone moves the headline.

    When several writings tie for a world's minimum bracket count, ``free_depth`` takes the
    SHALLOWEST of them.  Taking the deepest instead is equally defensible and gives a different
    answer to the card's second headline question, so the module computes both and this test pins
    the gap between them.  A review found the choice documented only in the docstring and absent
    from both reports, where it was deciding the ranking silently; it is now stated in the formula
    block of each report and asserted here, so the sensitivity cannot go back to being latent.

    Under the optimistic tie-break the least-taxing total is ``22`` in nine worlds.  Under the
    pessimistic one it is ``23`` in two, and ``G18`` -- the cheapest world to write in -- becomes
    joint-best on tax, which cuts AGAINST the near-independence of cost and parallelism that this
    experiment reports.  ``G0`` is ``25`` either way.
    """
    cells = tuple(grid(CORPUS)["cells"].values())
    differing = [cell for cell in cells if cell["tax"] != cell["tax_pessimistic"]]

    assert len(differing) == TIEBREAK_SENSITIVE_CELLS
    assert tuple(sorted({cell["object"] for cell in differing})) == TIEBREAK_SENSITIVE_OBJECTS

    # Never negative, and never smaller than the optimistic reading: it is the same minimum
    # subtracted from a depth chosen over the same set, so this is a structural check, not a
    # restatement of the numbers above.
    for cell in cells:
        assert cell["tax_pessimistic"] >= cell["tax"] >= 0

    optimistic = {}
    pessimistic = {}
    for cell in cells:
        optimistic[cell["grammar"]] = optimistic.get(cell["grammar"], 0) + cell["tax"]
        pessimistic[cell["grammar"]] = pessimistic.get(cell["grammar"], 0) + cell["tax_pessimistic"]

    assert min(optimistic.values()) == BEST_TAX
    assert min(pessimistic.values()) == PESSIMISTIC_BEST_TAX
    assert tuple(sorted(w for w, v in pessimistic.items() if v == PESSIMISTIC_BEST_TAX)) == (
        PESSIMISTIC_BEST_WORLDS
    )

    # The conventional grammar is unmoved by the choice; the winner is not.
    assert optimistic[CONTROL.id] == pessimistic[CONTROL.id] == CONTROL_TAX_TOTAL
    assert optimistic["G18"] == pessimistic["G18"] == PESSIMISTIC_BEST_TAX


def test_the_tie_break_moves_the_cost_versus_parallelism_correlation_by_more_than_the_cells_suggest():
    """52 changed cells of 1450 sounds small; the headline correlation moves two and a half times.

    Section 5 of both reports says cost rank and tax rank barely agree, and quotes ``0.167``.  That
    figure assumes ties for a world's cheapest writing resolve toward the shallowest.  Resolved the
    other way the same correlation is ``0.422``, which is a modest but real positive relationship and
    is no longer fairly described as barely agreeing.

    The illustration inverts with it: ``G19`` is the most expensive world in the corpus to write in
    and is joint-first on tax under the optimistic reading -- the vivid case the section is built on
    -- and falls to twenty-second under the pessimistic one.  Both figures are asserted here so that
    a reader of section 5 cannot be given only the flattering one.
    """
    cells = tuple(grid(CORPUS)["cells"].values())
    worlds = sorted({cell["grammar"] for cell in cells})

    def totals(key):
        return [sum(c[key] for c in cells if c["grammar"] == w) for w in worlds]

    cost = totals("min_cost")
    assert spearman(cost, totals("tax")) == pytest.approx(CORRELATION_OPTIMISTIC, abs=5e-7)
    assert spearman(cost, totals("tax_pessimistic")) == pytest.approx(CORRELATION_PESSIMISTIC, abs=5e-7)

    # The correlation the reports quote must be the optimistic one, or section 5 is quoting a
    # number the module does not compute.
    assert rank_correlation()["full_corpus"] == pytest.approx(CORRELATION_OPTIMISTIC, abs=5e-7)

    # G19: joint-first on tax one way, near-last the other.
    optimistic = dict(zip(worlds, totals("tax")))
    pessimistic = dict(zip(worlds, totals("tax_pessimistic")))
    assert optimistic["G19"] == min(optimistic.values())
    assert pessimistic["G19"] > min(pessimistic.values())
