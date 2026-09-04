"""Validation of experiment 0038: what each world lets you see.

Every expectation here is a value that was measured before it was written down, and the ones that
carry a headline are pinned literally rather than recomputed from the module, so a change in the
result fails a test instead of quietly rewriting the finding.

Two assertions come before all the others, because without them nothing else means anything:

* the **correctness bridge** inherited from :mod:`parseatlas.notational_cost` - a rendering must
  re-parse under its own grammar to the tree it came from and carry no bracket that grammar does
  not require - plus the extra obligation this card adds, that the surface tree the shape rules
  read is the same string ``render`` produced;
* **manifest implies true** - a shape rule that ever claims something ``ground_truth`` denies is a
  defect in the rules, and the whole grid is swept for it in both regimes.
"""

from sympy import Integer, Rational

from parseatlas.domain_worlds import CORPUS as LAW_CORPUS
from parseatlas.manifest_properties import (
    CALIBRATION,
    CONTROL,
    CORPUS,
    GRAMMARS,
    PRINCIPAL_VARIABLES,
    PROPERTIES,
    PROPERTY_NAMES,
    REGIMES,
    bridge_audit,
    calibration_report,
    chosen_writing,
    corpus_audit,
    ground_truth,
    identity_truth_audit,
    manifest_set,
    null_model,
    object_tree,
    parallel_decision,
    read_off,
    should_parallelise,
    surface,
    surface_text,
    tradeoff_report,
    truth_audit,
    value_audit,
    visibility_table,
    visible_signs,
    worker_count_for,
    writing_costs,
)
from parseatlas.notational_cost import render
from parseatlas.parser import parse

# ---- measured once, then pinned; these are the numbers the report publishes --------------------

CALIBRATION_EXPANDED_WORLDS = 17
CALIBRATION_FACTORED_WORLDS = 8
CONTROL_MANIFEST_TOTAL = 77
CONTROL_MANIFEST_RANK = 1
BEST_MANIFEST_IDS = ("G0", "G17")
WORST_MANIFEST_TOTAL = 58
FACTOR_STRUCTURE_WORLD_COUNT = 20
FACTOR_STRUCTURE_BLIND_WORLDS = ("G0", "G15", "G16", "G18", "G24")
OBJECTS_WITH_NOTHING_MANIFEST = (
    "distance_components",
    "slope",
    "triangle_area",
    "chain_rule",
    "riemann_sum_term",
)
HIDDEN_PAIR_COUNT = 46
OBJECTS_FULLY_VISIBLE_SOMEWHERE = 7
HEADLINE_EXCLUSIVE_PAIR = ("constant_term", "roots")


# ---- the two things everything else rests on ---------------------------------------------------


def test_the_correctness_bridge_holds_over_the_whole_grid():
    """Round trip, minimality, and the surface mirror, before any manifest number is believed.

    A rendering that does not re-parse to its own tree is not a writing of the object.  A rendering
    carrying a bracket its grammar does not require would let a shape rule read punctuation the
    convention never forced.  And a surface tree that does not spell back to ``render``'s own string
    would mean the shape rules are inspecting something other than the priced rendering.
    """
    audit = bridge_audit()
    assert audit["round_trip"]["holds"] is True
    assert audit["round_trip"]["failures"] == 0
    assert audit["round_trip"]["checks"] == 1250
    assert audit["minimality"]["minimal"] is True
    assert audit["minimality"]["violations"] == 0
    assert audit["minimality"]["brackets_checked"] == 1811
    assert audit["surface_mirror"]["holds"] is True
    assert audit["surface_mirror"]["checks"] == 1250


def test_manifest_implies_true_over_every_object_every_world_and_both_regimes():
    """The control.  A manifest claim ground truth denies is a defect, not a finding.

    ``manifest_set`` decides by shape and never computes a root, a coefficient or a factorisation;
    ``ground_truth`` decides by actually solving and factoring with SymPy.  The sweep asserts that
    the first never outruns the second, over 34 objects x 25 grammars x 2 regimes.
    """
    audit = truth_audit()
    assert audit["sound"] is True
    assert audit["violations"] == ()
    assert audit["cells"] == len(CORPUS) * len(GRAMMARS) * len(REGIMES)
    assert audit["checks"] > 2000  # the sweep must actually be checking claims, not nothing


def test_the_value_a_reader_would_read_off_is_the_value_the_object_actually_has():
    """The strong control: not just 'the property exists' but 'the number on the page is right'.

    For every writing that makes the degree, the leading coefficient, the constant term or the roots
    manifest, the value a reader takes off the tokens is compared with what SymPy computes from the
    object.  A shape rule that fires on the wrong shape usually still satisfies the weak control and
    almost never survives this one.
    """
    audit = value_audit()
    assert audit["correct"] is True
    assert audit["mismatches"] == ()
    assert audit["checks"] > 2000


def test_the_calibration_roots_are_read_off_the_factored_writing_correctly():
    """``(2 * x + 5) * (x - 1)`` must hand the reader exactly ``-5/2`` and ``1``."""
    tree = object_tree(CALIBRATION.writings[1])
    values = read_off(surface(tree, CONTROL), False, CALIBRATION.variable)
    assert set(values["roots"]) == {Rational(-5, 2), Integer(1)}
    assert values["degree"] == 2
    assert "constant_term" not in values
    expanded = read_off(surface(object_tree(CALIBRATION.writings[0]), CONTROL), False, "x")
    assert expanded["leading_coefficient"] == 2
    assert expanded["constant_term"] == -5
    assert "roots" not in expanded


def test_the_visible_sign_pattern_is_what_sign_structure_claims():
    """``sign_structure`` says the term signs are on the page, so the page is asked what they are."""
    circle = next(item for item in CORPUS if item.name == "circle")
    general = object_tree(next(w for w in circle.writings if w.role == "general"))
    assert render(general, CONTROL) == "x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k"
    assert visible_signs(surface(general, CONTROL), False) == "+-++-+"
    centre = object_tree(next(w for w in circle.writings if w.role == "center_radius"))
    assert visible_signs(surface(centre, CONTROL), False) == ""  # bracketed squares, no chain


def test_ground_truth_is_a_property_of_the_object_not_of_the_writing():
    """Both sides of an identity are the same object, so ground truth must not tell them apart.

    If it ever did, the control would be reading the writing instead of the object and the whole
    'manifest implies true' argument would be circular.
    """
    audit = identity_truth_audit()
    assert audit["writing_independent"] is True
    assert audit["mismatched"] == ()
    assert audit["two_sided"] == 16


# ---- the calibration case, pinned exactly ------------------------------------------------------


def test_the_calibration_case_is_exactly_what_the_card_states():
    """``2x^2 + 3x - 5``: the expanded writing hides the roots, the factored one hides the constant.

    This is the case the card supplies as calibration, and it is pinned in both directions: what
    each writing DOES make manifest and, just as importantly, what it does NOT.
    """
    report = calibration_report()
    expanded = report["expanded_manifest"]
    factored = report["factored_manifest"]

    assert "degree" in expanded
    assert "leading_coefficient" in expanded
    assert "constant_term" in expanded
    assert "roots" not in expanded

    assert "roots" in factored
    assert "constant_term" not in factored
    assert "leading_coefficient" not in factored

    assert expanded == ("degree", "leading_coefficient", "constant_term", "sign_structure")
    assert factored == ("degree", "roots", "factor_structure")


def test_the_seventeen_eight_split_of_the_calibration_quadratic_reproduces():
    """The manager measured 17 worlds writing it expanded and 8 factored; both must come back."""
    report = calibration_report()
    assert report["expanded_count"] == CALIBRATION_EXPANDED_WORLDS
    assert report["factored_count"] == CALIBRATION_FACTORED_WORLDS
    assert report["expanded_count"] + report["factored_count"] == len(GRAMMARS)
    assert CONTROL.id in report["expanded_worlds"]
    assert "G01" in report["factored_worlds"]
    assert report["per_grammar"]["G0"]["text"] == "2 * x * x + 3 * x - 5"
    assert report["per_grammar"]["G01"]["text"] == "(2 * x) + 5 * x - 1"


def test_the_calibration_object_is_one_object_with_two_writings():
    """Both writings must denote the same thing, or the experiment is comparing two objects."""
    costs_control = writing_costs(CALIBRATION, CONTROL)
    assert costs_control == {"expanded": 0, "factored": 2}
    assert chosen_writing(CALIBRATION, CONTROL).role == "expanded"
    truths = {
        writing.role: ground_truth(object_tree(writing), CALIBRATION.variable)
        for writing in CALIBRATION.writings
    }
    assert truths["expanded"] == truths["factored"]
    assert "roots" in truths["expanded"]  # 2x^2+3x-5 really does split over the rationals


# ---- the corpus is the imported one -------------------------------------------------------------


def test_the_corpus_is_the_imported_named_law_corpus_plus_the_calibration_quadratic():
    """The corpus is reused, not reinvented: 0037's 33 laws, imported, plus one calibration object."""
    audit = corpus_audit()
    assert audit["imported_law_count"] == len(LAW_CORPUS) == 33
    assert audit["objects"] == 34
    assert audit["writings"] == 50
    assert audit["two_sided"] == 16
    assert audit["one_sided"] == 18
    assert audit["duplicate_names"] == ()
    assert audit["canonical_sources"] is True
    assert audit["identities_hold"] is True
    assert audit["undeclared_variables"] == ()
    assert audit["objects_with_variable"] == 21
    law_names = {law.name for law in LAW_CORPUS}
    assert law_names < {item.name for item in CORPUS}
    assert set(PRINCIPAL_VARIABLES) == law_names | {CALIBRATION.name}


def test_every_property_declares_a_shape_rule_and_an_algebraic_control():
    """The vocabulary is closed and documented, and prose and code are both required of it."""
    assert PROPERTY_NAMES == (
        "degree",
        "leading_coefficient",
        "constant_term",
        "roots",
        "factor_structure",
        "sign_structure",
        "even_parity",
    )
    for item in PROPERTIES:
        assert item.rule.strip()
        assert item.truth_rule.strip()
        assert callable(item.shape)
        assert callable(item.truth)
        assert item.shape is not item.truth


# ---- the headline questions ---------------------------------------------------------------------


def test_no_world_makes_every_true_property_of_a_real_object_manifest():
    """Question 4: the trade is unavoidable.

    Seven objects are fully visible somewhere - and every one of them has exactly ONE true property,
    so 'fully visible' is vacuous for them.  Among the 25 objects with two or more true properties,
    no world shows all of them at once, in either regime.

    The size of that group is pinned below.  An earlier revision of the report said 27, which is
    34 minus the 7 fully-visible objects - a different set, since triangle_area and chain_rule each
    have exactly one true property and belong to neither group.  Nothing asserted it, so the wrong
    number survived into the report's opening sentence; it is asserted now.
    """
    for opaque in (False, True):
        report = tradeoff_report(opaque=opaque)
        assert report["objects_fully_visible_somewhere"] == OBJECTS_FULLY_VISIBLE_SOMEWHERE
        complete = {row["object"] for row in report["per_object"] if row["fully_visible_somewhere"]}
        assert all(
            row["true_count"] == 1 for row in report["per_object"] if row["object"] in complete
        )
        assert not any(
            row["fully_visible_somewhere"]
            for row in report["per_object"]
            if row["true_count"] > 1
        )


def test_the_headline_pair_is_never_manifest_together_in_any_world():
    """Question 5: constant term and roots are never co-manifest, in 850 cells, in either regime.

    The pair is pinned because it is the calibration trade itself, and it is pinned as a
    MEASUREMENT rather than as a consequence of the rules: nothing in the shape rules forbids it -
    a writing like ``a * x`` would satisfy both - so its emptiness is a fact about how this corpus
    is written under these twenty-five conventions.
    """
    for opaque in (False, True):
        report = tradeoff_report(opaque=opaque)
        entry = next(row for row in report["pairs"] if row["pair"] == HEADLINE_EXCLUSIVE_PAIR)
        assert entry["co_manifest_cells"] == 0
        assert entry["both_manifest_somewhere"] is True
        assert entry["mutually_exclusive"] is True
        assert entry["excluded_by_rule"] is False
        assert HEADLINE_EXCLUSIVE_PAIR in report["mutually_exclusive_by_measurement"]


def test_the_exclusive_pair_set_is_the_same_under_both_rule_regimes():
    """The one conclusion that must survive a change of rules, asserted as surviving it."""
    transparent = set(tradeoff_report(opaque=False)["mutually_exclusive_pairs"])
    opaque = set(tradeoff_report(opaque=True)["mutually_exclusive_pairs"])
    assert transparent == opaque
    assert transparent == {
        ("leading_coefficient", "roots"),
        ("leading_coefficient", "factor_structure"),
        ("constant_term", "roots"),
        ("constant_term", "factor_structure"),
        ("roots", "sign_structure"),
        ("roots", "even_parity"),
        ("factor_structure", "sign_structure"),
        ("factor_structure", "even_parity"),
    }


def test_a_pair_excluded_by_the_rules_is_labelled_as_such_and_not_sold_as_a_finding():
    """``roots`` needs a multiplicative top node and ``sign_structure`` an additive one.

    That pair can never co-occur no matter what the corpus is, so reporting it as a discovery about
    mathematics would be circular.  It is reported, but in the by-rule bucket.
    """
    report = tradeoff_report()
    assert ("roots", "sign_structure") in report["mutually_exclusive_by_rule"]
    assert ("factor_structure", "sign_structure") in report["mutually_exclusive_by_rule"]
    assert ("roots", "sign_structure") not in report["mutually_exclusive_by_measurement"]


def test_a_property_manifest_in_no_world_is_reported_rather_than_omitted():
    """Question 2, and the reporting obligation that goes with it.

    No property is manifest in zero worlds when the whole corpus is pooled, and the table says so
    explicitly with an empty tuple rather than a missing key.  The interesting emptiness is one
    level down: 46 (object, property) facts are TRUE and manifest in no world at all, five objects
    have nothing manifest anywhere, and ``factor_structure`` is manifest in only 20 of 25 worlds -
    with the conventional ``G0`` among the five that never show it.
    """
    table = visibility_table()
    assert table["universally_hidden"] == ()
    assert set(table["worlds_without"]) == set(PROPERTY_NAMES)
    assert set(table["hidden_by_property"]) == set(PROPERTY_NAMES)
    assert table["hidden_by_property"]["even_parity"] == 0  # a zero is reported, not dropped

    assert table["hidden_pair_count"] == HIDDEN_PAIR_COUNT
    assert table["objects_with_nothing_manifest"] == OBJECTS_WITH_NOTHING_MANIFEST
    assert table["property_world_counts"]["factor_structure"] == FACTOR_STRUCTURE_WORLD_COUNT
    assert table["worlds_without"]["factor_structure"] == FACTOR_STRUCTURE_BLIND_WORLDS
    assert CONTROL.id in table["worlds_without"]["factor_structure"]


def test_which_properties_are_visible_in_every_world_and_which_are_not():
    """Question 1, in both regimes, because its answer is exactly the one that does not survive."""
    transparent = visibility_table(opaque=False)
    assert transparent["universally_visible"] == (
        "degree",
        "leading_coefficient",
        "constant_term",
        "roots",
        "sign_structure",
        "even_parity",
    )
    opaque = visibility_table(opaque=True)
    assert opaque["universally_visible"] == ("degree",)


def test_the_world_ranking_and_where_the_conventional_grammar_stands():
    """Question 3, pinned literally, with the caveat it must always be read with.

    ``G0`` is joint-first on the raw manifest count - but the vocabulary is not neutral between the
    two master shapes, and the shape counts pinned here are what shows that: the ranking tracks how
    many objects a world writes as a sum of monomials, which is the shape four of the seven
    properties live in.
    """
    table = visibility_table()
    assert table["control_total"] == CONTROL_MANIFEST_TOTAL
    assert table["control_rank"] == CONTROL_MANIFEST_RANK
    assert table["best_ids"] == BEST_MANIFEST_IDS
    assert table["worst"]["total"] == WORST_MANIFEST_TOTAL
    assert table["cells"] == len(CORPUS) * len(GRAMMARS) == 850

    best_shapes = table["shape_counts"][CONTROL.id]
    worst_shapes = table["shape_counts"][table["worst"]["id"]]
    assert best_shapes["monomial_sum"] == 27
    assert worst_shapes["monomial_sum"] == 14
    assert best_shapes["monomial_sum"] > worst_shapes["monomial_sum"]

    opaque = visibility_table(opaque=True)
    assert opaque["control_rank"] == 3  # the exact rank does NOT survive the rule change
    assert opaque["best_ids"] == ("G17",)


# ---- the null model -------------------------------------------------------------------------------


def test_objects_that_cannot_carry_a_conclusion_are_counted_and_removed():
    """18 of 34 objects have the same manifest set in all 25 worlds; removing them changes nothing.

    They are exactly the one-sided objects: with a single writing there is nothing for a convention
    to choose, so they add the same 28 manifest facts to every world's total.  The ranking with and
    without them is identical, symbol for symbol, which is what says the ranking measures
    conventions and not corpus bulk.
    """
    model = null_model()
    assert model["constant_manifest_count"] == 18
    assert model["movable_count"] == 16
    assert model["forced_total_under_control"] == 28
    assert model["constant_choice_count"] == 18
    assert model["constant_text"] == ("chain_rule",)
    assert model["ranking_order_identical"] is True
    assert model["full_control_rank"] == model["reduced_control_rank"] == CONTROL_MANIFEST_RANK
    assert model["full_spread"] == model["reduced_spread"] == 19


def test_a_single_writing_object_is_the_same_in_every_world():
    """The null model's mechanism, checked directly on one object rather than only in aggregate."""
    dot_product = next(item for item in CORPUS if item.name == "dot_product")
    assert len(dot_product.writings) == 1
    sets = {
        grammar.id: manifest_set(
            object_tree(dot_product.writings[0]), grammar, dot_product.variable
        )
        for grammar in GRAMMARS
    }
    assert len(set(sets.values())) == 1
    assert sets[CONTROL.id] == ("sign_structure",)


# ---- the shape rules themselves -----------------------------------------------------------------


def test_a_constant_term_split_across_two_summands_is_not_manifest():
    """The soundness fix to the card's suggested rule, pinned as its own case.

    ``fa - dfa * a + dfa * x`` has two variable-free summands and its constant term is their sum.
    Pointing at one of them would be wrong and combining them would be algebra, so the property is
    not manifest - even though the writing is otherwise a perfectly readable sum of monomials.
    """
    item = next(item for item in CORPUS if item.name == "linear_approximation")
    tree = object_tree(next(w for w in item.writings if w.role == "slope_intercept"))
    manifest = manifest_set(tree, CONTROL, item.variable)
    assert "degree" in manifest
    assert "leading_coefficient" in manifest
    assert "constant_term" not in manifest
    assert "constant_term" in ground_truth(tree, item.variable)


def test_a_leading_coefficient_needs_a_unique_leading_monomial():
    """Two monomials of the same top power means adding them, which is algebra, not reading."""
    item = next(item for item in CORPUS if item.name == "trapezoid_area")
    tree = object_tree(next(w for w in item.writings if w.role == "sum_of_halves"))
    manifest = manifest_set(tree, CONTROL, item.variable)  # a * h / 2 + b * h / 2, variable h
    assert "degree" in manifest
    assert "leading_coefficient" not in manifest


def test_a_quadratic_factor_is_not_a_readable_root():
    """``(a - b) * (a * a + a * b + b * b)`` is a visible factorisation but not visible roots."""
    item = next(item for item in CORPUS if item.name == "difference_of_cubes")
    tree = object_tree(next(w for w in item.writings if w.role == "factored"))
    manifest = manifest_set(tree, CONTROL, item.variable)
    assert "factor_structure" in manifest
    assert "roots" not in manifest
    assert "roots" in ground_truth(tree, item.variable)


def test_the_opaque_regime_hides_what_a_bracket_encloses():
    """The robustness regime does what it says: a bracketed factor stops being inspectable.

    Under the transparent rules ``(2 * x + 5) * (x - 1)`` shows its roots; under the opaque rules it
    does not, because deciding that each factor is linear would mean looking inside a bracket.  That
    the card's own calibration contradicts the opaque reading is exactly why it is the secondary
    regime and not the headline.
    """
    tree = object_tree(CALIBRATION.writings[1])
    transparent = manifest_set(tree, CONTROL, CALIBRATION.variable, opaque=False)
    opaque = manifest_set(tree, CONTROL, CALIBRATION.variable, opaque=True)
    assert "roots" in transparent
    assert "roots" not in opaque
    assert "factor_structure" in transparent
    assert "factor_structure" in opaque  # seeing THAT there are two factors needs no opening


def test_a_bracket_free_rendering_is_fully_visible_even_under_the_opaque_rules():
    """The opaque regime is where the grammar changes what a FIXED writing shows.

    ``a * (b + c)`` hides its sum behind a bracket under ``G0``.  Under ``G01``, where ``+`` binds
    tightest, the same tree is written ``a * b + c`` with no bracket at all, so nothing is enclosed
    and the opaque rules see everything the transparent ones do.
    """
    item = next(item for item in CORPUS if item.name == "distributive_law")
    tree = object_tree(next(w for w in item.writings if w.role == "factored"))
    control_grammar = next(g for g in GRAMMARS if g.id == "G0")
    plus_first = next(g for g in GRAMMARS if g.id == "G01")
    assert render(tree, control_grammar) == "a * (b + c)"
    assert render(tree, plus_first) == "a * b + c"
    assert manifest_set(tree, plus_first, item.variable, opaque=True) == manifest_set(
        tree, plus_first, item.variable, opaque=False
    )
    assert manifest_set(tree, control_grammar, item.variable, opaque=True) != manifest_set(
        tree, control_grammar, item.variable, opaque=False
    )


# ---- clauses the named-law corpus never exercises -----------------------------------------------
#
# Four clauses of the shape rules are load-bearing for SOUNDNESS but are never reached by the 34
# objects of the corpus, so mutation testing found them unprotected.  They are pinned here on
# synthetic writings.  These are probes, not corpus: nothing below contributes to a published
# number, and the corpus stays exactly the imported one.


def _probe(source: str, grammar_id: str = "G0"):
    """A synthetic written form, parsed under the control grammar and rendered under one world."""
    grammar = next(g for g in GRAMMARS if g.id == grammar_id)
    tree = parse(source, CONTROL)
    return tree, grammar


def test_a_variable_under_a_division_is_not_a_polynomial_writing():
    """``a / x + b * x`` is not a sum of monomials IN x, and none of the coefficient rules may fire.

    Without this clause the writing would look like a two-term chain of powers 0 and 1 and would
    report a degree, a leading coefficient and a constant term for an object that has none - the
    ground truth denies all three, because ``a/x + b*x`` is not a polynomial in ``x``.
    """
    tree, grammar = _probe("a / x + b * x")
    manifest = manifest_set(tree, grammar, "x")
    assert manifest == ("sign_structure",)  # the signs are visible; nothing about x is
    assert "degree" not in manifest
    assert "leading_coefficient" not in manifest
    assert "constant_term" not in manifest
    assert ground_truth(tree, "x") == ("factor_structure", "sign_structure")


def test_the_additive_chain_is_not_flattened_through_a_bracketed_right_operand():
    """``a - (b + c)`` is two addends, not three, whatever the world's brackets look like.

    Under ``G01``, where ``+`` binds tightest, the same tree is written ``a - b + c`` with no bracket
    at all.  Flattening that string left to right would read the signs as ``+ + +`` when the object's
    terms are ``a - b - c``, which is a sign the notation never showed.
    """
    tree, grammar = _probe("a - (b + c)", "G01")
    assert render(tree, grammar) == "a - b + c"
    assert visible_signs(surface(tree, grammar), False) == ""
    assert "sign_structure" not in manifest_set(tree, grammar, None)
    assert "sign_structure" in ground_truth(tree, None)  # the object HAS a sign pattern; it is hidden


def test_roots_require_the_object_to_be_presented_as_a_product():
    """``m * x + b`` is a coefficient list, not a factorisation, so it does not show a root.

    This is where the ``roots`` rule draws its line, and the line is a declared judgement: a product
    of linear factors is a presentation OF the roots, while a sum of monomials is a presentation of
    the coefficients from which a root would have to be derived.  Dropping the requirement would
    also collapse the headline exclusive pair, since ``m * x + b`` shows its constant term too.
    """
    tree, grammar = _probe("m * x + b")
    manifest = manifest_set(tree, grammar, "x")
    assert "constant_term" in manifest
    assert "leading_coefficient" in manifest
    assert "roots" not in manifest
    assert "roots" in ground_truth(tree, "x")


def test_a_factor_with_two_linear_terms_does_not_show_a_root():
    """``(a * x + b * x + c) * (x - 1)``: the first factor's slope is ``a + b``, which is algebra."""
    tree, grammar = _probe("(a * x + b * x + c) * (x - 1)")
    manifest = manifest_set(tree, grammar, "x")
    assert "factor_structure" in manifest
    assert "roots" not in manifest
    assert "roots" in ground_truth(tree, "x")


def test_the_surface_tree_spells_back_to_the_rendering_it_mirrors():
    """The shape rules read a surface tree; it must be the same string ``render`` produced."""
    for item in CORPUS:
        for writing in item.writings:
            tree = object_tree(writing)
            for grammar in GRAMMARS:
                assert surface_text(surface(tree, grammar)) == render(tree, grammar)


# ---- concurrency ----------------------------------------------------------------------------------


def test_sequential_and_parallel_agree_cell_for_cell():
    """Parallelism changes only how fast, never what is measured."""
    sequential = visibility_table(workers=1)
    parallel = visibility_table(workers=2)
    assert sequential == parallel


def test_the_parallel_decision_is_measured_and_comes_out_sequential():
    """Multicore by policy, sequential by measurement - and the measurement is the justification.

    850 cells of pure-Python rendering cost about a quarter of a second in total; a spawn-start pool
    whose workers each import SymPy costs about a second before any of that work starts.  The rule
    below is arithmetic on two measured numbers, not a constant carried over from another module.
    """
    assert should_parallelise(850, 2.4e-04, 12) is False
    assert should_parallelise(2_000_000, 2.4e-04, 12) is True  # the rule does flip when it should
    assert should_parallelise(850, 2.4e-04, 1) is False
    assert should_parallelise(1, 10.0, 12) is False


def test_the_worker_count_comes_from_the_observed_cores():
    """Never a hardcoded constant, and always with headroom for the interactive session."""
    assert worker_count_for(16, 850) == 12
    assert worker_count_for(4, 850) == 2
    assert worker_count_for(1, 850) == 1
    assert worker_count_for(16, 3) == 3


def test_both_paths_are_timed_and_produce_identical_records():
    """The measurement the report publishes, run end to end."""
    decision = parallel_decision()
    assert decision["identical"] is True
    assert decision["cells"] == 850
    assert decision["default_path"] == "sequential"


def test_the_multi_property_group_is_twenty_five_objects():
    """Pins the denominator of the headline claim, which nothing previously asserted.

    The report's opening sentence counts the objects the trade-off statement is ABOUT.  Getting it
    from 34 minus the fully-visible count is wrong, because an object with a single true property
    is fully visible everywhere and is in neither group.
    """
    report = tradeoff_report()
    counts = [row["true_count"] for row in report["per_object"]]
    assert len(counts) == 34
    assert sum(1 for c in counts if c >= 2) == 25
    assert sum(1 for c in counts if c == 1) == 9
    assert sum(1 for c in counts if c == 0) == 0

    from collections import Counter
    assert dict(sorted(Counter(counts).items())) == {1: 9, 2: 4, 5: 6, 6: 12, 7: 3}

    # 175 = the 7 single-property objects seen in all 25 worlds, and nothing else.
    assert report["complete_cells"] == 175
    assert report["objects_fully_visible_somewhere"] == 7
