"""Domain-dependent equivalence of grammar readings over Q and over F_p."""

from collections.abc import Iterable
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from typing import Any

from .grammar import all_grammars
from .parser import Node, Number, Variable, parse

CONSTANT_CORPUS: tuple[str, ...] = (
    "2*3 + 4 - 6/2",
    "1 + 2*3 - 4/2",
    "8/4 + 3*2 - 1",
    "5 - 2*3 + 9/3",
    "7 + 6/3 - 2*4",
)

DEFAULT_PRIMES: tuple[int, ...] = (5, 7, 11, 13, 97)

UNDEFINED = "undefined"


class UndefinedOverRationals(Exception):
    """A constant AST divides by zero over Q."""


class UndefinedOverFiniteField(Exception):
    """A constant AST divides by a non-invertible residue in F_p."""


@lru_cache(maxsize=None)
def _is_prime(candidate: int) -> bool:
    if candidate < 2:
        return False
    if candidate % 2 == 0:
        return candidate == 2
    factor = 3
    while factor * factor <= candidate:
        if candidate % factor == 0:
            return False
        factor += 2
    return True


def _require_prime(prime: int) -> None:
    """Enforce the declared domain: every modular routine here works inside a field F_p."""
    if not _is_prime(prime):
        raise ValueError(f"Modulus must be prime for F_p arithmetic; got {prime}")


def evaluate_rational(node: Node) -> Fraction:
    """Evaluate a constant AST exactly over Q."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        raise ValueError(f"Rational evaluation requires a constant AST; got variable {node.name!r}")
    left = evaluate_rational(node.left)
    right = evaluate_rational(node.right)
    if node.operator == "+":
        return left + right
    if node.operator == "-":
        return left - right
    if node.operator == "*":
        return left * right
    if node.operator == "/":
        if right == 0:
            raise UndefinedOverRationals("Division by zero over Q")
        return left / right
    raise ValueError(f"Unsupported operator: {node.operator}")


def reduce_modulo(value: Fraction, prime: int) -> int:
    """Reduce an exact rational into F_p, refusing a denominator that is not invertible.

    The modulus is required to be prime, so "not invertible" is exactly "divisible by
    the modulus"; a composite modulus is rejected up front with an explicit ValueError
    instead of letting a bare inverse failure escape from pow().
    """
    _require_prime(prime)
    if value.denominator % prime == 0:
        raise UndefinedOverFiniteField(f"Denominator {value.denominator} is not invertible modulo {prime}")
    return value.numerator * pow(value.denominator, -1, prime) % prime


def evaluate_modular(node: Node, prime: int) -> int:
    """Evaluate a constant AST inside F_p, with division by modular inverse."""
    _require_prime(prime)
    if isinstance(node, Number):
        return reduce_modulo(node.value, prime)
    if isinstance(node, Variable):
        raise ValueError(f"Modular evaluation requires a constant AST; got variable {node.name!r}")
    left = evaluate_modular(node.left, prime)
    right = evaluate_modular(node.right, prime)
    if node.operator == "+":
        return (left + right) % prime
    if node.operator == "-":
        return (left - right) % prime
    if node.operator == "*":
        return left * right % prime
    if node.operator == "/":
        if right % prime == 0:
            raise UndefinedOverFiniteField(f"Denominator is congruent to 0 modulo {prime}")
        return left * pow(right, -1, prime) % prime
    raise ValueError(f"Unsupported operator: {node.operator}")


def _group(labels: dict[str, str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for grammar_id, label in labels.items():
        groups.setdefault(label, []).append(grammar_id)
    return {label: sorted(groups[label]) for label in sorted(groups)}


def _labels(values: dict[str, Any]) -> dict[str, str]:
    return {grammar_id: UNDEFINED if value is None else str(value) for grammar_id, value in values.items()}


def _rational_values(nodes: dict[str, Node]) -> dict[str, Fraction | None]:
    values: dict[str, Fraction | None] = {}
    for grammar_id, node in nodes.items():
        try:
            values[grammar_id] = evaluate_rational(node)
        except UndefinedOverRationals:
            values[grammar_id] = None
    return values


def _modular_values(nodes: dict[str, Node], prime: int) -> dict[str, int | None]:
    values: dict[str, int | None] = {}
    for grammar_id, node in nodes.items():
        try:
            values[grammar_id] = evaluate_modular(node, prime)
        except UndefinedOverFiniteField:
            values[grammar_id] = None
    return values


def _bridge(rational: dict[str, Fraction | None], modular: dict[str, int | None], prime: int) -> dict[str, Any]:
    """Compare the two evaluations only where both of them are defined.

    A grammar whose exact rational value exists while its F_p value does not is a real
    domain restriction, not a disagreement: it is recorded in its own counted category
    and never touches ``bridge_holds``. That happens both when the value's own
    denominator dies mod p and when an intermediate divisor does. ``bridge_holds``
    therefore means exactly "the two evaluations never disagree where both are defined".
    """
    checked = 0
    failures: list[dict[str, Any]] = []
    restrictions: list[dict[str, Any]] = []
    for grammar_id, exact in rational.items():
        observed = modular[grammar_id]
        if exact is None:
            if observed is not None:
                failures.append({"grammar_id": grammar_id, "reason": "rational_undefined_but_modular_defined", "modular": observed})
            continue
        if exact.denominator % prime == 0:
            if observed is not None:
                failures.append({"grammar_id": grammar_id, "reason": "non_invertible_denominator_but_modular_defined", "modular": observed})
            else:
                restrictions.append({"grammar_id": grammar_id, "reason": "value_denominator_not_invertible", "rational": str(exact)})
            continue
        if observed is None:
            restrictions.append({"grammar_id": grammar_id, "reason": "intermediate_divisor_not_invertible", "rational": str(exact)})
            continue
        checked += 1
        expected = reduce_modulo(exact, prime)
        if observed != expected:
            failures.append({"grammar_id": grammar_id, "reason": "reduction_mismatch", "expected": expected, "modular": observed, "rational": str(exact)})
    return {
        "bridge_checks": checked,
        "bridge_failures": failures,
        "bridge_holds": not failures,
        "domain_restrictions": restrictions,
        "domain_restriction_count": len(restrictions),
    }


def _collapsed_pairs(rational: dict[str, Fraction | None], modular: dict[str, int | None]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for left, right in combinations(sorted(rational), 2):
        exact_left, exact_right = rational[left], rational[right]
        if exact_left is None or exact_right is None or exact_left == exact_right:
            continue
        if modular[left] is None or modular[left] != modular[right]:
            continue
        pairs.append(
            {
                "left": left,
                "right": right,
                "rational_left": str(exact_left),
                "rational_right": str(exact_right),
                "modular": modular[left],
            }
        )
    return pairs


def _collapse_mechanisms(rational: dict[str, Fraction | None], modular: dict[str, int | None]) -> dict[str, int]:
    """Split the class-count change into modular coincidence and domain-restriction erasure.

    coincidence_collapse: distinct *defined* rational values that land on one *defined*
    F_p value. This is the only mechanism the collapsed-pair witnesses can exhibit.

    restriction_collapse: classes that merge only because their grammars left the domain
    and all landed in the single ``undefined`` label. It is derived from the undefined
    side alone rather than as the total minus coincidence, so the identity
    ``coincidence + restriction == collapse`` is a real cross-check. It is negative when a
    restriction *splits* one Q class into a defined part and an undefined part.
    """
    rational_labels = _labels(rational)
    defined = [grammar_id for grammar_id, value in modular.items() if value is not None]
    undefined = [grammar_id for grammar_id, value in modular.items() if value is None]
    defined_rational = {rational_labels[grammar_id] for grammar_id in defined}
    defined_modular = {modular[grammar_id] for grammar_id in defined}
    undefined_rational = {rational_labels[grammar_id] for grammar_id in undefined}
    coincidence = len(defined_rational) - len(defined_modular)
    restriction = len(undefined_rational - defined_rational) - (1 if undefined else 0)
    return {"coincidence_collapse": coincidence, "restriction_collapse": restriction}


def _prime_report(rational: dict[str, Fraction | None], nodes: dict[str, Node], prime: int, rational_class_count: int) -> dict[str, Any]:
    modular = _modular_values(nodes, prime)
    classes = _group(_labels(modular))
    pairs = _collapsed_pairs(rational, modular)
    report = {
        "prime": prime,
        "modular_classes": classes,
        "modular_class_count": len(classes),
        "collapse": rational_class_count - len(classes),
        "collapsed_pairs": pairs,
        "collapsed_pair_count": len(pairs),
        "undefined_grammars": sorted(grammar_id for grammar_id, value in modular.items() if value is None),
    }
    report.update(_collapse_mechanisms(rational, modular))
    report.update(_bridge(rational, modular, prime))
    return report


def _source_report(source: str, primes: tuple[int, ...]) -> dict[str, Any]:
    nodes = {grammar.id: parse(source, grammar) for grammar in all_grammars()}
    rational = _rational_values(nodes)
    rational_classes = _group(_labels(rational))
    return {
        "source": source,
        "grammar_count": len(nodes),
        "rational_classes": rational_classes,
        "rational_class_count": len(rational_classes),
        "rational_undefined": sorted(grammar_id for grammar_id, value in rational.items() if value is None),
        "primes": {prime: _prime_report(rational, nodes, prime, len(rational_classes)) for prime in primes},
    }


def modular_class_report(sources: Iterable[str] = CONSTANT_CORPUS, primes: Iterable[int] = DEFAULT_PRIMES) -> dict[str, Any]:
    """Compare Q-equivalence classes with F_p-equivalence classes across a constant corpus."""
    sources = tuple(sources)
    primes = tuple(primes)
    reports = [_source_report(source, primes) for source in sources]

    def total(key: str) -> int:
        return sum(report["primes"][prime][key] for report in reports for prime in primes)

    def by_prime(key: str) -> dict[int, int]:
        return {prime: sum(report["primes"][prime][key] for report in reports) for prime in primes}

    collapsing = sorted({prime for report in reports for prime in primes if report["primes"][prime]["collapse"] > 0})
    coincidence_primes = sorted({prime for report in reports for prime in primes if report["primes"][prime]["coincidence_collapse"] > 0})
    return {
        "source_count": len(sources),
        "primes": list(primes),
        "grammar_count": len(all_grammars()),
        "sources": reports,
        "total_collapse_events": total("collapse"),
        "total_coincidence_collapse": total("coincidence_collapse"),
        "total_restriction_collapse": total("restriction_collapse"),
        "total_collapsed_pairs": total("collapsed_pair_count"),
        "total_domain_restrictions": total("domain_restriction_count"),
        "collapsing_primes": collapsing,
        "coincidence_collapsing_primes": coincidence_primes,
        "collapse_by_prime": by_prime("collapse"),
        "coincidence_collapse_by_prime": by_prime("coincidence_collapse"),
        "restriction_collapse_by_prime": by_prime("restriction_collapse"),
        "bridge_checks": total("bridge_checks"),
        "bridge_failures": [failure for report in reports for prime in primes for failure in report["primes"][prime]["bridge_failures"]],
        "bridge_holds": all(report["primes"][prime]["bridge_holds"] for report in reports for prime in primes),
    }
