from fractions import Fraction

import pytest

from parseatlas.finite_field import (
    CONSTANT_CORPUS,
    DEFAULT_PRIMES,
    UndefinedOverFiniteField,
    UndefinedOverRationals,
    evaluate_modular,
    evaluate_rational,
    modular_class_report,
    reduce_modulo,
)
from parseatlas.grammar import all_grammars
from parseatlas.parser import parse


def _rational_distribution(source):
    counts = {}
    for grammar in all_grammars():
        value = str(evaluate_rational(parse(source, grammar)))
        counts[value] = counts.get(value, 0) + 1
    return counts


def test_declared_corpus_freeze_pins_the_sources_primes_and_rational_values():
    """Corpus freeze: this test only pins the declared inputs and their measured Q values.

    The literal corpus and prime tuple are echoes of the module constants on purpose --
    they exist so that silently editing the published corpus breaks a test. The
    expectations that carry real content are the rational value distributions below,
    which are computed by the evaluator and not restated anywhere in the module.
    """
    assert CONSTANT_CORPUS == (
        "2*3 + 4 - 6/2",
        "1 + 2*3 - 4/2",
        "8/4 + 3*2 - 1",
        "5 - 2*3 + 9/3",
        "7 + 6/3 - 2*4",
    )
    assert DEFAULT_PRIMES == (5, 7, 11, 13, 97)
    assert {source: _rational_distribution(source) for source in CONSTANT_CORPUS} == {
        "2*3 + 4 - 6/2": {"7": 13, "8": 8, "11": 4},
        "1 + 2*3 - 4/2": {"3": 12, "5": 9, "7": 4},
        "8/4 + 3*2 - 1": {"5": 12, "7": 9, "9": 4},
        "5 - 2*3 + 9/3": {"-7": 4, "-4": 4, "2": 5, "12": 4, "18": 8},
        "7 + 6/3 - 2*4": {"1": 13, "7": 4, "28": 8},
    }


def test_rational_and_modular_class_counts_match_the_measured_table():
    report = modular_class_report()
    assert report["grammar_count"] == 25
    assert report["source_count"] == 5
    observed = {
        source["source"]: (source["rational_class_count"], tuple(source["primes"][prime]["modular_class_count"] for prime in DEFAULT_PRIMES))
        for source in report["sources"]
    }
    assert observed == {
        "2*3 + 4 - 6/2": (3, (3, 3, 3, 3, 3)),
        "1 + 2*3 - 4/2": (3, (3, 3, 3, 3, 3)),
        "8/4 + 3*2 - 1": (3, (3, 3, 3, 3, 3)),
        "5 - 2*3 + 9/3": (5, (3, 5, 4, 5, 5)),
        "7 + 6/3 - 2*4": (3, (3, 2, 3, 3, 3)),
    }


def test_correctness_bridge_holds_for_every_grammar_source_and_prime():
    report = modular_class_report()
    assert report["bridge_checks"] == 625
    assert report["bridge_failures"] == []
    assert report["bridge_holds"] is True
    assert report["total_domain_restrictions"] == 0
    for source in CONSTANT_CORPUS:
        for grammar in all_grammars():
            node = parse(source, grammar)
            exact = evaluate_rational(node)
            # The declared corpus is denominator-free (REPORT.md, tokenizer observation):
            # its 625 bridge checks all reduce an integer, so they cannot exercise a
            # non-trivial modular inverse. That degeneracy is asserted here rather than
            # disclosed only in prose, and the real inverse is exercised by the probe
            # in test_bridge_exercises_a_non_trivial_modular_inverse below.
            assert exact.denominator == 1
            for prime in DEFAULT_PRIMES:
                assert evaluate_modular(node, prime) == exact.numerator * pow(exact.denominator, -1, prime) % prime


def test_bridge_exercises_a_non_trivial_modular_inverse():
    report = modular_class_report(("6 / 5 + 1",), (7,))
    prime_report = report["sources"][0]["primes"][7]
    assert prime_report["bridge_checks"] == 25
    assert prime_report["domain_restriction_count"] == 0
    assert report["bridge_holds"] is True
    denominators = {}
    for grammar in all_grammars():
        exact = evaluate_rational(parse("6 / 5 + 1", grammar))
        denominators[exact.denominator] = denominators.get(exact.denominator, 0) + 1
    assert denominators == {5: 13, 1: 12}
    assert pow(5, -1, 7) == 3 != 1
    assert reduce_modulo(Fraction(11, 5), 7) == 5
    assert {label: len(ids) for label, ids in prime_report["modular_classes"].items()} == {"1": 12, "5": 13}

    second = modular_class_report(("10 / 5 - 3 / 4",), (5,))["sources"][0]
    assert {label: len(ids) for label, ids in second["rational_classes"].items()} == {"5/4": 25}
    assert pow(4, -1, 5) == 4 != 1
    assert reduce_modulo(Fraction(5, 4), 5) == 0
    assert second["primes"][5]["bridge_checks"] == 12


def test_rational_defined_but_modular_undefined_is_a_domain_restriction_not_a_bridge_failure():
    report = modular_class_report(("10 / 5 + 1",), (5,))
    prime_report = report["sources"][0]["primes"][5]
    # Over Q every grammar reading is defined; 13 of them have the integer value 3,
    # whose denominator 1 is invertible mod 5. They are undefined in F_5 only because
    # the intermediate divisor 5 is 0 there. That is a domain restriction, and the
    # bridge must not report it as a disagreement.
    assert report["sources"][0]["rational_undefined"] == []
    assert {label: len(ids) for label, ids in report["sources"][0]["rational_classes"].items()} == {"3": 13, "5/3": 12}
    assert report["bridge_holds"] is True
    assert report["bridge_failures"] == []
    assert prime_report["bridge_checks"] == 12
    assert prime_report["domain_restriction_count"] == 13
    assert len(prime_report["undefined_grammars"]) == 13
    assert {entry["reason"] for entry in prime_report["domain_restrictions"]} == {"intermediate_divisor_not_invertible"}
    assert {entry["rational"] for entry in prime_report["domain_restrictions"]} == {"3"}
    for source in ("6 / 5 * 5", "5 * 6 / 5", "2 / 5 * 5 + 1"):
        other = modular_class_report((source,), (5,))
        assert other["bridge_holds"] is True
        assert other["bridge_failures"] == []
        assert other["total_domain_restrictions"] > 0


def test_non_invertible_value_denominator_is_a_separately_labelled_restriction():
    report = modular_class_report(("6 / 5 + 1",), (5,))
    prime_report = report["sources"][0]["primes"][5]
    assert prime_report["bridge_checks"] == 12
    assert prime_report["domain_restriction_count"] == 13
    assert {entry["reason"] for entry in prime_report["domain_restrictions"]} == {"value_denominator_not_invertible"}
    assert {entry["rational"] for entry in prime_report["domain_restrictions"]} == {"11/5"}
    assert report["bridge_holds"] is True


def test_collapse_separates_modular_coincidence_from_domain_restriction():
    # Two distinct defined rational values that both leave F_5 merge into one
    # "undefined" class. That is erasure, not coincidence, and there is no pair witness.
    erased = modular_class_report(("6 / 5 + 6 / 5",), (5,))["sources"][0]["primes"][5]
    assert erased["collapse"] == 1
    assert erased["coincidence_collapse"] == 0
    assert erased["restriction_collapse"] == 1
    assert erased["collapsed_pair_count"] == 0

    wider = modular_class_report(("2 / 5 * 5 + 1",), (5,))["sources"][0]["primes"][5]
    assert wider["collapse"] == 3
    assert wider["coincidence_collapse"] == 0
    assert wider["restriction_collapse"] == 3
    assert wider["collapsed_pair_count"] == 0

    # The published corpus is pure coincidence: no value ever leaves the domain.
    corpus = modular_class_report()
    assert corpus["total_collapse_events"] == 4
    assert corpus["total_coincidence_collapse"] == 4
    assert corpus["total_restriction_collapse"] == 0
    assert corpus["total_domain_restrictions"] == 0
    assert corpus["coincidence_collapse_by_prime"] == {5: 2, 7: 1, 11: 1, 13: 0, 97: 0}
    assert corpus["restriction_collapse_by_prime"] == {5: 0, 7: 0, 11: 0, 13: 0, 97: 0}
    assert corpus["coincidence_collapsing_primes"] == [5, 7, 11]


def test_collapse_components_sum_to_the_class_count_change():
    probes = (
        *CONSTANT_CORPUS,
        "6 / 0",
        "6 / 3 - 3",
        "6 / 5 + 1",
        "10 / 5 + 1",
        "6 / 5 + 6 / 5",
        "2 / 5 * 5 + 1",
        "10 / 5 - 3 / 4",
        "2 / 7 + 3 / 5",
    )
    report = modular_class_report(probes, (2, 3, 5, 7, 11, 13, 97))
    for source in report["sources"]:
        for prime in report["primes"]:
            prime_report = source["primes"][prime]
            assert prime_report["coincidence_collapse"] + prime_report["restriction_collapse"] == prime_report["collapse"]
            assert prime_report["coincidence_collapse"] >= 0
    assert report["bridge_holds"] is True
    # A restriction can also split one Q class into a defined and an undefined part,
    # which raises the class count; the restriction component then goes negative.
    split = modular_class_report(("10 / 5 - 3 / 4",), (5,))["sources"][0]["primes"][5]
    assert split["collapse"] == -1
    assert split["coincidence_collapse"] == 0
    assert split["restriction_collapse"] == -1
    assert {label: len(ids) for label, ids in split["modular_classes"].items()} == {"0": 12, "undefined": 13}


def test_collapse_is_strictly_positive_and_collapsed_pairs_differ_over_Q():
    report = modular_class_report()
    assert report["total_collapse_events"] == 4
    assert report["total_collapsed_pairs"] == 116
    assert report["collapsing_primes"] == [5, 7, 11]
    positive = [(source["source"], prime) for source in report["sources"] for prime in DEFAULT_PRIMES if source["primes"][prime]["collapse"] > 0]
    assert positive == [("5 - 2*3 + 9/3", 5), ("5 - 2*3 + 9/3", 11), ("7 + 6/3 - 2*4", 7)]
    for source in report["sources"]:
        for prime in DEFAULT_PRIMES:
            for pair in source["primes"][prime]["collapsed_pairs"]:
                left = evaluate_rational(parse(source["source"], next(item for item in all_grammars() if item.id == pair["left"])))
                right = evaluate_rational(parse(source["source"], next(item for item in all_grammars() if item.id == pair["right"])))
                assert left != right
                assert str(left) == pair["rational_left"] and str(right) == pair["rational_right"]
                assert evaluate_modular(parse(source["source"], next(item for item in all_grammars() if item.id == pair["left"])), prime) == pair["modular"]
                assert reduce_modulo(left, prime) == reduce_modulo(right, prime) == pair["modular"]


def test_witness_pair_28_and_7_agree_modulo_7():
    report = modular_class_report(("7 + 6/3 - 2*4",), (7,))
    pairs = report["sources"][0]["primes"][7]["collapsed_pairs"]
    witness = next(pair for pair in pairs if pair["left"] == "G01" and pair["right"] == "G09")
    assert witness["rational_left"] == "28"
    assert witness["rational_right"] == "7"
    assert witness["modular"] == 0
    assert report["sources"][0]["rational_class_count"] == 3
    assert report["sources"][0]["primes"][7]["modular_class_count"] == 2
    assert report["sources"][0]["primes"][7]["coincidence_collapse"] == 1
    assert report["sources"][0]["primes"][7]["restriction_collapse"] == 0


def test_division_by_zero_is_recorded_as_undefined_not_raised():
    report = modular_class_report(("6 / 0",), (5, 7))
    source = report["sources"][0]
    assert source["rational_classes"] == {"undefined": sorted(grammar.id for grammar in all_grammars())}
    assert len(source["rational_undefined"]) == 25
    assert source["primes"][5]["modular_classes"] == {"undefined": sorted(grammar.id for grammar in all_grammars())}
    assert source["primes"][5]["bridge_checks"] == 0
    assert source["primes"][5]["domain_restriction_count"] == 0
    assert report["bridge_holds"] is True
    with pytest.raises(UndefinedOverRationals):
        evaluate_rational(parse("6 / 0", all_grammars()[0]))


def test_grammar_choice_decides_whether_the_rational_value_is_undefined():
    report = modular_class_report(("6 / 3 - 3",), (5, 7))
    source = report["sources"][0]
    assert {label: len(ids) for label, ids in source["rational_classes"].items()} == {"-1": 13, "undefined": 12}
    assert {label: len(ids) for label, ids in source["primes"][5]["modular_classes"].items()} == {"4": 13, "undefined": 12}
    assert {label: len(ids) for label, ids in source["primes"][7]["modular_classes"].items()} == {"6": 13, "undefined": 12}
    assert source["primes"][7]["bridge_checks"] == 13
    assert source["primes"][7]["domain_restriction_count"] == 0
    assert report["bridge_holds"] is True


def test_non_invertible_denominator_is_undefined_only_in_the_field_that_kills_it():
    report = modular_class_report(("6 / 5 + 1",), (5, 7))
    source = report["sources"][0]
    assert {label: len(ids) for label, ids in source["rational_classes"].items()} == {"1": 12, "11/5": 13}
    assert source["rational_undefined"] == []
    assert len(source["primes"][5]["undefined_grammars"]) == 13
    assert source["primes"][7]["undefined_grammars"] == []
    assert source["primes"][5]["bridge_checks"] == 12
    assert source["primes"][7]["bridge_checks"] == 25
    assert report["bridge_holds"] is True
    with pytest.raises(UndefinedOverFiniteField):
        reduce_modulo(Fraction(11, 5), 5)
    assert reduce_modulo(Fraction(11, 5), 7) == 5


def test_measured_collapse_relation_between_prime_5_and_prime_97():
    report = modular_class_report()
    by_prime = report["collapse_by_prime"]
    assert by_prime == {5: 2, 7: 1, 11: 1, 13: 0, 97: 0}
    assert by_prime[5] > by_prime[97]
    assert by_prime[97] == 0
    per_source = {source["source"]: {prime: source["primes"][prime]["collapse"] for prime in DEFAULT_PRIMES} for source in report["sources"]}
    assert per_source["7 + 6/3 - 2*4"][5] == 0
    assert per_source["7 + 6/3 - 2*4"][7] == 1
    assert per_source["5 - 2*3 + 9/3"][7] == 0
    assert per_source["5 - 2*3 + 9/3"][11] == 1


def test_evaluate_modular_rejects_variables_and_non_prime_moduli():
    node = parse("2*x + 1", all_grammars()[0])
    with pytest.raises(ValueError):
        evaluate_rational(node)
    with pytest.raises(ValueError):
        evaluate_modular(node, 7)
    with pytest.raises(ValueError):
        evaluate_modular(parse("1 + 1", all_grammars()[0]), 1)


def test_composite_modulus_is_rejected_explicitly_instead_of_raising_a_bare_inverse_error():
    # Denominator 2 is not invertible modulo 4. Before the modulus was validated this
    # reached pow(2, -1, 4) and escaped as an unlabelled ValueError from the stdlib.
    assert not issubclass(UndefinedOverFiniteField, ValueError)
    with pytest.raises(ValueError, match="Modulus must be prime"):
        reduce_modulo(Fraction(1, 2), 4)
    with pytest.raises(ValueError, match="Modulus must be prime"):
        reduce_modulo(Fraction(3, 1), 9)
    with pytest.raises(ValueError, match="Modulus must be prime"):
        evaluate_modular(parse("1 / 2", all_grammars()[0]), 4)
    with pytest.raises(ValueError, match="Modulus must be prime"):
        evaluate_modular(parse("1 + 1", all_grammars()[0]), 0)
    # The same denominator is fine over a genuine prime field.
    assert reduce_modulo(Fraction(1, 2), 5) == 3
    assert evaluate_modular(parse("1 / 2", all_grammars()[0]), 5) == 3
