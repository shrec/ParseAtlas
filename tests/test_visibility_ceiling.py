"""Validation of experiment 0039: what it would take to see the 46 invisible pairs.

Every number here was measured before it was written down, and every headline is pinned as a
literal rather than recomputed from the module, so a change in the result fails a test instead of
quietly rewriting the finding.

Three assertions come before the rest, because without them nothing else means anything:

* **the rules are imported, not restated** - the shape rules used to compute a ceiling are the very
  objects experiment 0038 declares, checked by identity;
* **a parenthesization is usually a different object** - the identity filter is what keeps a tree
  that exposes something else from being counted as a recovery;
* **manifest implies true over the full space** - the extension multiplies the number of written
  forms by four orders of magnitude, so 0038's soundness control is re-run over every tree of the
  new space that still denotes the object.

The file is ordered cheap-first on purpose: the plumbing and the identity filter are checked on a
handful of trees before anything sweeps 1.5 million of them, so a broken invariant fails in seconds
rather than after the whole space has been walked.
"""

import os
from functools import lru_cache

from parseatlas import manifest_properties as origin
from parseatlas.canonical import to_sympy
from parseatlas.manifest_properties import (
    CORPUS,
    GRAMMARS,
    OBJECT_BY_NAME,
    PROPERTIES,
    object_tree,
)
from parseatlas.parser import parse
from parseatlas.reachability import strict_reachable
from parseatlas.visibility_ceiling import (
    CONTROL,
    POOL_STARTUP_SECONDS,
    RULE_LIMIT_REASONS,
    TREE_SECONDS,
    WITNESSES,
    Witness,
    baseline,
    ceiling_table,
    default_worker_count,
    flat_source,
    grammar_independence,
    in_order,
    language_accounting,
    manifest_set,
    parallel_decision,
    rebuild,
    residue_report,
    rule_identity,
    same_object,
    should_parallelise,
    soundness_sweep,
    to_form,
    witness_audit,
    worker_count_for,
    writing_space,
    zero_bracket_readings,
)

# ---- measured once, then pinned; these are the numbers the report publishes --------------------

TRUE_PAIRS = 140
UNION_OVER_TWENTY_FIVE = 94
INVISIBLE_PAIRS = 46

#: The card states ``80`` for the best single world.  It is not reproducible from 0038's own table
#: under any reading we tried: the per-world total of true-and-manifest pairs peaks at ``77``, which
#: is also 0038's own published per-world manifest total for ``G0``.  The measured value is pinned
#: and the card's value is pinned as NOT reproducing, so the discrepancy cannot be lost.
BEST_SINGLE_WORLD = 77
BEST_SINGLE_WORLD_IDS = ("G0", "G17")
CARD_CLAIMED_BEST_SINGLE_WORLD = 80

FULL_SPACE_TREES = 1_510_820
SAME_OBJECT_TREES = 667
PRECEDENCE_REACHABLE_SAME_OBJECT_TREES = 52
CEILING_PAIRS = 95
CEILING_CLAIMS = 657
RECOVERED_PAIRS = (("taylor_second_term", "factor_structure"),)
STILL_HIDDEN = 45

BLOCKED_BY_THE_OPERATOR_SET = 8
BLOCKED_NEEDING_THE_IMAGINARY_UNIT = (
    ("difference_of_cubes", "roots"),
    ("sum_of_cubes", "roots"),
    ("circle", "roots"),
    ("ellipse", "roots"),
    ("ellipse", "factor_structure"),
    ("distance_components", "roots"),
    ("pythagorean_form", "roots"),
)
BLOCKED_NEEDING_A_RADICAL = (("parabola", "roots"),)
BLOCKED_OBJECTS = (
    "circle",
    "difference_of_cubes",
    "distance_components",
    "ellipse",
    "parabola",
    "pythagorean_form",
    "sum_of_cubes",
)

RESIDUE = 37
RESIDUE_DIFFERENT_WORD = (
    ("quadratic", "leading_coefficient"),
    ("quadratic", "constant_term"),
    ("quadratic", "sign_structure"),
    ("hyperbola", "roots"),
    ("hyperbola", "factor_structure"),
    ("distance_components", "degree"),
    ("distance_components", "leading_coefficient"),
    ("distance_components", "sign_structure"),
    ("midpoint", "leading_coefficient"),
    ("midpoint", "constant_term"),
    ("midpoint", "sign_structure"),
    ("taylor_first_term", "leading_coefficient"),
    ("taylor_first_term", "constant_term"),
    ("taylor_first_term", "sign_structure"),
    ("taylor_second_term", "leading_coefficient"),
    ("taylor_second_term", "constant_term"),
    ("taylor_second_term", "sign_structure"),
    ("riemann_sum_term", "sign_structure"),
)
RESIDUE_RULE_LIMIT = (
    ("distributive_law", "leading_coefficient"),
    ("distributive_law", "factor_structure"),
    ("line", "constant_term"),
    ("line", "roots"),
    ("circle", "constant_term"),
    ("parabola", "constant_term"),
    ("distance_components", "constant_term"),
    ("slope", "factor_structure"),
    ("slope", "sign_structure"),
    ("triangle_area", "factor_structure"),
    ("trapezoid_area", "leading_coefficient"),
    ("trapezoid_area", "factor_structure"),
    ("difference_quotient", "factor_structure"),
    ("quotient_rule", "factor_structure"),
    ("chain_rule", "factor_structure"),
    ("linear_approximation", "constant_term"),
    ("linear_approximation", "roots"),
    ("taylor_first_term", "factor_structure"),
    ("riemann_sum_term", "factor_structure"),
)

#: Objects that show NOTHING in any world in 0038, and still show nothing at the ceiling of the
#: full space.  The list is 0038's own and it survives the extension unchanged.
NOTHING_AT_THE_CEILING = (
    "distance_components",
    "slope",
    "triangle_area",
    "chain_rule",
    "riemann_sum_term",
)

ZERO_BRACKET_CELLS = 460
ZERO_BRACKET_CELLS_READING_ANOTHER_TREE = 36

#: Three named trees of the full space that denote their object and that NO precedence rule writes
#: bracket-free.  They are the concrete content of "our search space is precedence-shaped": each is
#: a legitimate written form of its object that 0038's grid could never contain.
UNREACHABLE_TREES = (
    (
        "taylor_second_term",
        "standard",
        "d2fa * ((x - a) * ((x - a) / 2))",
        ("degree", "roots", "factor_structure"),
    ),
    (
        "quadratic",
        "expanded",
        "a * (x * x) - a * (r + s) * x + a * r * s",
        (),
    ),
    (
        "difference_of_cubes",
        "expanded",
        "a * (a * a) - b * b * b",
        ("degree", "leading_coefficient", "constant_term", "sign_structure"),
    ),
)

#: The one recovered pair, its three exposing trees, and which of them a precedence rule can write.
#: The third is reachable, and that is the defect this experiment reports against 0038.
TAYLOR_SECOND_TERM_FLAT_WORD = "d2fa * x - a * x - a / 2"
TAYLOR_SECOND_TERM_EXPOSING_TREES = (
    ("d2fa * ((x - a) * ((x - a) / 2))", False, ()),
    ("d2fa * ((x - a) * (x - a) / 2)", False, ()),
    ("d2fa * (x - a) * ((x - a) / 2)", True, ("G02", "G08", "G11", "G12")),
)

#: A two-object corpus whose whole parenthesization space is 52 trees, so the pipeline can be
#: exercised end to end without walking the real one.
TINY_CORPUS_NAMES = ("difference_of_squares", "taylor_second_term")
TINY_SPACE = 52
TINY_SAME_OBJECT = 7

SMALL_CORPUS_NAMES = (
    "distributive_law",
    "difference_of_squares",
    "line",
    "midpoint",
    "taylor_first_term",
    "taylor_second_term",
)


def _corpus(names):
    return tuple(OBJECT_BY_NAME[name] for name in names)


@lru_cache(maxsize=1)
def _table():
    return ceiling_table()


@lru_cache(maxsize=1)
def _language():
    return language_accounting(table=_table())


@lru_cache(maxsize=1)
def _residue():
    return residue_report(table=_table(), language=_language())


# ---- cheap invariants, checked before anything sweeps the space --------------------------------


def test_the_rules_are_imported_and_not_redefined():
    identity = rule_identity()
    assert identity["properties_identical"]
    assert identity["manifest_set_identical"]
    assert identity["ground_truth_identical"]
    assert identity["corpus_identical"]
    assert identity["shape_rules_identical"]
    # identity, not equality: a copied rule set would pass an == check and fail this one
    assert PROPERTIES is origin.PROPERTIES
    assert manifest_set is origin.manifest_set
    assert CORPUS is origin.CORPUS
    for item in PROPERTIES:
        assert item.shape is origin.PROPERTY_BY_NAME[item.name].shape
        assert item.truth is origin.PROPERTY_BY_NAME[item.name].truth


def test_the_word_of_a_tree_round_trips_through_the_enumeration():
    for item in CORPUS:
        for writing in item.writings:
            tree = object_tree(writing)
            leaves, operators = in_order(tree)
            assert len(leaves) == len(operators) + 1
            form = to_form(tree)
            assert rebuild(form, leaves) == tree
            _leaves, space_operators, forms = writing_space(writing)
            assert space_operators == operators
            assert form in forms


def test_the_bracket_free_word_is_the_writing_with_its_brackets_removed():
    cases = {
        ("taylor_second_term", "standard"): "d2fa * x - a * x - a / 2",
        ("difference_of_squares", "factored"): "a + b * a - b",
        ("midpoint", "mean"): "x1 + x2 / 2",
        ("chain_rule", "standard"): "dfg * dg",
    }
    for (name, role), expected in cases.items():
        item = OBJECT_BY_NAME[name]
        writing = next(w for w in item.writings if w.role == role)
        leaves, operators = in_order(object_tree(writing))
        assert flat_source(leaves, operators) == expected


def test_a_parenthesization_of_the_same_word_is_usually_a_different_object():
    # the filter the whole experiment rests on, checked on five trees rather than 1.5 million
    item = OBJECT_BY_NAME["difference_of_squares"]
    writing = item.writings[1]
    leaves, operators, forms = writing_space(writing)
    declared = to_form(object_tree(writing))
    expression = to_sympy(object_tree(writing))
    agreeing = [form for form in forms if same_object(rebuild(form, leaves), expression)]
    assert operators == ("*", "-", "*")
    assert len(forms) == 5
    assert agreeing == [declared]

    other = OBJECT_BY_NAME["taylor_second_term"].writings[0]
    leaves, _operators, forms = writing_space(other)
    expression = to_sympy(object_tree(other))
    agreeing = [form for form in forms if same_object(rebuild(form, leaves), expression)]
    assert len(forms) == 42
    assert len(agreeing) == 5


def test_the_probe_narrows_the_space_before_sympy_confirms_it():
    # exercised on 52 trees: every tree the probe admits is confirmed, and it admits few
    table = ceiling_table(_corpus(TINY_CORPUS_NAMES), workers=1)
    assert table["space_total"] == TINY_SPACE
    assert table["trees_probed"] == TINY_SPACE
    assert table["probe_survivors"] == TINY_SAME_OBJECT
    assert table["same_object_trees"] == TINY_SAME_OBJECT
    assert table["soundness_violation_count"] == 0
    assert table["recovered_pairs"] == RECOVERED_PAIRS


def test_three_named_trees_of_the_space_are_precedence_unreachable():
    for name, role, text, expected in UNREACHABLE_TREES:
        item = OBJECT_BY_NAME[name]
        writing = next(w for w in item.writings if w.role == role)
        leaves, operators, forms = writing_space(writing)
        tree = parse(text, CONTROL)
        form = to_form(tree)
        assert form in forms, f"{text} is not a parenthesization of {name}.{role}"
        assert rebuild(form, leaves) == tree
        assert same_object(tree, to_sympy(object_tree(writing)))
        assert strict_reachable(form, operators) is False, text
        assert manifest_set(tree, CONTROL, item.variable) == expected


def test_the_parallel_decision_is_measured_and_comes_out_parallel():
    # the sweep is 1.5 million exact rational evaluations, which is the first workload in this
    # series large enough to pay for a spawn-start pool; 0038's own sweep was not
    assert should_parallelise(FULL_SPACE_TREES, TREE_SECONDS, 12) is True
    assert should_parallelise(1_000, TREE_SECONDS, 12) is False
    assert should_parallelise(FULL_SPACE_TREES, TREE_SECONDS, 1) is False
    sequential = FULL_SPACE_TREES * TREE_SECONDS
    assert POOL_STARTUP_SECONDS + sequential / 12 < sequential


def test_the_worker_count_comes_from_the_observed_cores():
    assert worker_count_for(16, 425) == 12
    assert worker_count_for(4, 425) == 2
    assert worker_count_for(1, 425) == 1
    assert worker_count_for(16, 1) == 1
    assert default_worker_count(425) == worker_count_for(os.cpu_count() or 1, 425)


# ---- the 0038 baseline ------------------------------------------------------------------------


def test_the_0038_baseline_reproduces_from_0038s_own_table():
    reference = baseline()
    assert reference["objects"] == 34
    assert reference["grammars"] == 25
    assert reference["true_pairs"] == TRUE_PAIRS
    assert reference["manifest_somewhere"] == UNION_OVER_TWENTY_FIVE
    assert reference["hidden_pair_count"] == INVISIBLE_PAIRS
    assert reference["hidden_by_property"] == {
        "degree": 1,
        "leading_coefficient": 7,
        "constant_term": 9,
        "roots": 10,
        "factor_structure": 12,
        "sign_structure": 7,
        "even_parity": 0,
    }


def test_the_best_single_world_is_seventy_seven_and_not_the_eighty_the_card_states():
    reference = baseline()
    assert reference["best_single_world"] == BEST_SINGLE_WORLD
    assert reference["best_single_world_ids"] == BEST_SINGLE_WORLD_IDS
    assert reference["best_single_world"] != CARD_CLAIMED_BEST_SINGLE_WORLD
    # 77 is also 0038's own published per-world manifest total for the control grammar, so the two
    # readings of "what one world shows" agree with each other and disagree with 80.
    table = origin.visibility_table()
    assert table["control_total"] == BEST_SINGLE_WORLD
    assert max(table["totals"].values()) == BEST_SINGLE_WORLD


# ---- Part 1: the full parenthesization space --------------------------------------------------


def test_manifest_implies_true_over_the_whole_parenthesization_space():
    sweep = soundness_sweep(table=_table())
    assert sweep["same_object_trees"] == SAME_OBJECT_TREES
    assert sweep["claims"] == CEILING_CLAIMS
    assert sweep["violation_count"] == 0
    assert sweep["violations"] == ()


def test_the_extension_costs_one_and_a_half_million_trees_and_none_of_it_was_bounded():
    table = _table()
    assert table["space_total"] == FULL_SPACE_TREES
    assert table["trees_probed"] == table["space_total"]  # nothing was bounded away
    assert table["probe_survivors"] == SAME_OBJECT_TREES
    assert table["same_object_trees"] == SAME_OBJECT_TREES
    sizes = {row["object"]: row["space_total"] for row in table["rows"]}
    assert sizes["binomial_cube"] == 742_942
    assert sizes["circle"] == 743_329
    assert sizes["chain_rule"] == 1
    assert max(sizes.values()) == 743_329


def test_the_full_space_recovers_exactly_one_of_the_forty_six():
    table = _table()
    assert table["recovered_pairs"] == RECOVERED_PAIRS
    assert table["recovered_count"] == 1
    assert table["still_hidden_count"] == STILL_HIDDEN
    assert table["ceiling_pairs"] == CEILING_PAIRS
    assert table["recovered_by_property"] == {
        "degree": 0,
        "leading_coefficient": 0,
        "constant_term": 0,
        "roots": 0,
        "factor_structure": 1,
        "sign_structure": 0,
        "even_parity": 0,
    }


def test_the_recovered_pair_has_three_exposing_trees_and_one_of_them_is_reachable():
    table = _table()
    row = next(r for r in table["rows"] if r["object"] == "taylor_second_term")
    exposure = row["exposing"]["factor_structure"]
    assert exposure["tree_count"] == 3
    found = tuple(
        (tree["text"], tree["strict_reachable"], tree["registry_grammars"])
        for tree in exposure["trees"]
    )
    assert found == TAYLOR_SECOND_TERM_EXPOSING_TREES
    assert all(tree["flat_source"] == TAYLOR_SECOND_TERM_FLAT_WORD for tree in exposure["trees"])
    assert exposure["precedence_reachable"] is True
    assert exposure["reachable_grammars"] == ("G02", "G08", "G11", "G12")
    # a reachable exposing tree is a DEFECT report against 0038, not a finding of this card
    assert table["precedence_reachable_recoveries"] == RECOVERED_PAIRS


def test_only_a_thirteenth_of_the_same_object_trees_are_precedence_reachable():
    table = _table()
    assert table["precedence_reachable_same_object_trees"] == (
        PRECEDENCE_REACHABLE_SAME_OBJECT_TREES
    )
    assert table["same_object_trees"] == SAME_OBJECT_TREES
    assert PRECEDENCE_REACHABLE_SAME_OBJECT_TREES < SAME_OBJECT_TREES // 10


def test_the_ceiling_leaves_five_objects_showing_nothing_at_all():
    table = _table()
    assert table["objects_with_nothing_manifest"] == NOTHING_AT_THE_CEILING
    assert table["objects_gaining"] == ("taylor_second_term",)


def test_the_transparent_manifest_set_of_a_tree_does_not_depend_on_the_world():
    check = grammar_independence(table=_table())
    assert check["checks"] == SAME_OBJECT_TREES * 25
    assert check["disagreement_count"] == 0
    assert check["disagreements"] == ()


# ---- the defect this card asked to be looked for ----------------------------------------------


def test_the_zero_bracket_reading_defect_is_measured_and_its_blast_radius_is_one_pair():
    defect = zero_bracket_readings(table=_table())
    assert defect["cells_with_a_zero_bracket_reading"] == ZERO_BRACKET_CELLS
    assert defect["cells_reading_a_different_tree"] == ZERO_BRACKET_CELLS_READING_ANOTHER_TREE
    assert defect["added_pairs"] == RECOVERED_PAIRS
    assert defect["added_pair_count"] == 1
    affected = {(cell["object"], cell["grammar"]) for cell in defect["differing_cells"]}
    assert ("taylor_second_term", "G12") in affected
    assert ("triangle_area", "G02") in affected


# ---- Part 2: the operator set, an accounting of requirements -----------------------------------


def test_part_two_is_labelled_as_an_accounting_and_not_as_a_measured_rendering():
    language = _language()
    assert language["analysis_only"] is True
    assert "not renderings" in language["note"]
    assert language["operator_set"] == ("+", "-", "*", "/")


def test_eight_pairs_over_seven_objects_have_no_written_form_in_this_operator_set():
    language = _language()
    assert language["blocked_count"] == BLOCKED_BY_THE_OPERATOR_SET
    assert language["blocked_object_count"] == 7
    assert language["blocked_objects"] == BLOCKED_OBJECTS
    assert language["by_requirement"]["imaginary_unit"] == BLOCKED_NEEDING_THE_IMAGINARY_UNIT
    assert language["by_requirement"]["radical"] == BLOCKED_NEEDING_A_RADICAL
    assert language["by_requirement"]["no_closed_form"] == ()


def test_the_hyperbola_splits_over_the_rationals_and_the_ellipse_does_not():
    language = _language()
    blocked = set(language["blocked_pairs"])
    assert ("ellipse", "roots") in blocked
    assert ("ellipse", "factor_structure") in blocked
    assert ("hyperbola", "roots") not in blocked
    assert ("hyperbola", "factor_structure") not in blocked


def test_the_compound_factor_count_is_the_number_the_rule_limit_reasons_rest_on():
    # the shape rule counts NUMERATOR factors that are not leaf tokens; the truth rule counts a
    # bare symbol as a factor too, and that gap is what makes ten pairs a rule_limit.  The count is
    # pinned here because the reasons quote it, and because nothing else in the corpus separates
    # "one compound factor and one bare symbol" from "two factors".
    language = _language()
    counts = {
        entry["object"]: entry["detail"]["compound_factors"]
        for entry in language["entries"]
        if entry["property"] == "factor_structure"
    }
    assert counts["chain_rule"] == 0  # dfg * dg - both factors are bare symbols
    assert counts["triangle_area"] == 0  # b * h / 2 - the same, with a constant divisor
    assert counts["distributive_law"] == 1  # a * (b + c) - one compound, one symbol
    assert counts["taylor_first_term"] == 1  # dfa * (x - a)
    assert counts["slope"] == 1  # the other compound factor is the denominator
    assert counts["ellipse"] == 1  # irreducible over the rationals
    assert counts["hyperbola"] == 2  # (b x - a y) (b x + a y) - and so it is NOT blocked
    extended = {
        entry["object"]: entry["detail"]["extended"]
        for entry in language["entries"]
        if entry["property"] == "factor_structure"
    }
    assert extended["ellipse"] == 2  # only the imaginary unit turns 1 into 2
    assert extended["chain_rule"] == 0


def test_the_two_cubic_identities_need_both_a_radical_and_the_imaginary_unit():
    language = _language()
    for name in ("difference_of_cubes", "sum_of_cubes"):
        entry = next(
            e for e in language["entries"] if e["object"] == name and e["property"] == "roots"
        )
        assert entry["requirement"] == "imaginary_unit"
        assert entry["detail"]["requirements"] == ("imaginary_unit", "radical")
        assert entry["detail"]["degrees"] == (1, 2)


# ---- Part 3: the residue ----------------------------------------------------------------------


def test_the_residue_is_thirty_seven_pairs_and_every_one_of_them_is_named():
    residue = _residue()
    assert residue["residue_count"] == RESIDUE
    assert residue["by_cause"]["different_word"] == RESIDUE_DIFFERENT_WORD
    assert residue["by_cause"]["rule_limit"] == RESIDUE_RULE_LIMIT
    assert set(residue["residue_pairs"]) == set(RESIDUE_DIFFERENT_WORD) | set(RESIDUE_RULE_LIMIT)
    assert len(RESIDUE_DIFFERENT_WORD) == 18
    assert len(RESIDUE_RULE_LIMIT) == 19


def test_the_three_way_accounting_adds_up_to_the_forty_six():
    table = _table()
    language = _language()
    residue = _residue()
    assert (
        table["recovered_count"]
        + language["blocked_count"]
        + residue["residue_count"]
        == INVISIBLE_PAIRS
    )
    assert table["still_hidden_count"] == language["blocked_count"] + residue["residue_count"]


def test_every_rule_limit_carries_a_reason_that_names_the_clause():
    residue = _residue()
    assert residue["rule_limits_without_a_reason"] == ()
    for entry in residue["entries"]:
        if entry["cause"] == "rule_limit":
            assert entry["reason"], entry
            assert RULE_LIMIT_REASONS[(entry["object"], entry["property"])] == entry["reason"]
    assert set(RULE_LIMIT_REASONS) == set(RESIDUE_RULE_LIMIT)


def test_every_witness_is_rendered_and_really_fires():
    audit = witness_audit()
    assert audit["witnesses"] == len(WITNESSES) == 18
    assert audit["failing"] == ()
    assert audit["not_same_object"] == ()
    assert audit["unsound"] == ()
    assert audit["holding_count"] == 18
    assert set(audit["holding"]) == set(RESIDUE_DIFFERENT_WORD)


def test_the_object_that_shows_nothing_anywhere_shows_three_things_in_one_other_word():
    audit = witness_audit()
    record = next(
        r
        for r in audit["records"]
        if r["object"] == "distance_components" and r["property"] == "degree"
    )
    assert record["same_object"] is True
    assert record["manifest"] == ("degree", "leading_coefficient", "sign_structure")
    assert record["rendered"] == (
        "x2 * x2 - 2 * x1 * x2 + x1 * x1 + y2 * y2 - 2 * y1 * y2 + y1 * y1"
    )
    # and the corpus's own writing shows none of them, in any of the 25 worlds
    row = next(r for r in _table()["rows"] if r["object"] == "distance_components")
    assert row["manifest_somewhere"] == ()
    assert row["ceiling_manifest"] == ()


def test_a_witness_that_does_not_fire_is_reported_as_failing_rather_than_dropped():
    # the root of the line is x1 - y1/m, a SUM of two monomials, so the linear factor carries two
    # constant terms and the roots rule refuses it - this is exactly why the pair is a rule_limit
    audit = witness_audit(
        (Witness("line", "roots", "m * (x - x1 + y1 / m)", "two constant terms in one factor"),)
    )
    assert audit["records"][0]["same_object"] is True
    assert audit["records"][0]["manifest"] == ()
    assert audit["failing"] == (("line", "roots"),)
    assert audit["holding"] == ()


# ---- concurrency -------------------------------------------------------------------------------


def test_sequential_and_parallel_agree_tree_for_tree():
    corpus = _corpus(SMALL_CORPUS_NAMES)
    sequential = ceiling_table(corpus, workers=1)
    parallel = ceiling_table(corpus, workers=4)
    assert sequential == parallel
    assert sequential["same_object_trees"] > 0


def test_both_paths_are_timed_and_produce_identical_chunks():
    decision = parallel_decision(_corpus(SMALL_CORPUS_NAMES))
    assert decision["identical"] is True
    assert decision["trees"] > 0
    assert decision["workers"] >= 1
    assert decision["sequential_seconds"] > 0
    assert decision["parallel_seconds"] > 0

# ---- two gaps closed after review: the inert filter, and the widened reachability ---------------


def test_the_sympy_filter_is_correct_in_both_directions_even_though_it_rejects_nothing_here():
    """The second-stage identity filter is currently INERT on this corpus, and that is pinned.

    ``ceiling_table`` filters twice: an exact-rational probe at two declared points, then a SymPy
    confirmation of every survivor.  On this corpus the second filter removes nothing --
    ``probe_survivors == same_object_trees`` -- so its rejection path is never taken by the scan and
    a review found that deleting it left the whole suite passing.

    That is a fact about the corpus, not a licence to drop the filter, so both halves are asserted
    here: the inertness itself, so a future corpus that does exercise the filter shows up as a
    changed number rather than silently; and that ``same_object`` really does decide correctly in
    both directions, on constructed input where the probe alone would be trusted blindly.
    """
    table = ceiling_table()
    assert table["probe_survivors"] == table["same_object_trees"] == 667

    reference = to_sympy(parse("a - b + c", CONTROL))

    # Accepted: the control's own reading of the word.
    assert same_object(parse("a - b + c", CONTROL), reference) is True

    # Rejected: G01 reads the same word as ``a - (b + c)``, a different function.  This is the
    # rejection path the scan never reaches, exercised directly.
    other = next(grammar for grammar in GRAMMARS if grammar.id == "G01")
    assert str(to_sympy(parse("a - b + c", other))) == "a - b - c"
    assert same_object(parse("a - b + c", other), reference) is False

    # Accepted although the tree differs.  No precedence rule can split ``a + b + c`` -- a single
    # repeated operator is invisible to precedence -- so the other association is written with an
    # explicit bracket.  The two trees differ and denote the same object, which is the case the
    # filter must NOT reject.
    left = parse("a + b + c", CONTROL)
    right = parse("a + (b + c)", CONTROL)
    assert to_form(left) != to_form(right)
    assert same_object(right, to_sympy(left)) is True


def test_precedence_reachability_is_deliberately_widened_past_strict_reachable():
    """``strict_reachable`` alone is not the right test, and the module's ``or`` is load-bearing.

    ``strict_reachable`` decides reachability for TIE-FREE precedence orderings.  Four of the
    twenty-five conventions here have ties -- the control ``G0`` most of all -- so a tree a real
    grammar in the registry actually writes can still be reported unreachable by the strict test.
    ``ceiling_table`` therefore counts ``strict_reachable(...) or form in registry``.

    The widening buys exactly one tree on this corpus, and it is the sharpest possible case: the
    general written form of the circle, which ``G0 ITSELF`` writes.  Calling that unreachable would
    have been plainly wrong, so the count, the difference and the identity of the case are all
    pinned -- a review found that flipping the ``or`` to ``and`` left every other test passing.
    """
    table = ceiling_table()
    strict_only = 0
    widened = 0
    registry_not_strict = []

    for row in table["rows"]:
        item = OBJECT_BY_NAME[row["object"]]
        for measured, declared in zip(row["writings"], item.writings):
            _leaves, operators, _forms = writing_space(declared)
            registry: dict = {}
            for grammar in GRAMMARS:
                registry.setdefault(to_form(parse(measured["flat_source"], grammar)), []).append(
                    grammar.id
                )
            for form in measured["same_object_forms"]:
                strict = strict_reachable(form, operators)
                in_registry = form in registry
                strict_only += strict
                widened += strict or in_registry
                if in_registry and not strict:
                    registry_not_strict.append((row["object"], registry[form]))

    assert strict_only == 51
    assert widened == 52 == table["precedence_reachable_same_object_trees"]
    assert registry_not_strict == [("circle", ["G0"])]
