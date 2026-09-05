"""The third representation axis: the base a number is written in.

Experiment 0054.  The project has measured two representation axes and this module opens the third::

    syntax        which tree a string becomes                  the 25 worlds  (0001-0053)
    expression    which equivalent writing is chosen            direction B   (0034, 0037)
    NUMERAL       how the numbers themselves are written        this module

The owner's founding question for this axis was asked long before the vocabulary for it existed:
*compare computing* ``2**50`` *in decimal against computing it in binary.*  Nothing in the
repository answers it, because everything here charges ``+ - * /`` as abstract operations on
abstract numbers.  A machine does not.  :func:`power_headline` answers it as an operation count.

What a "numeral world" is
-------------------------

A numeral world is a **base**.  It is not a grammar and it does not change any tree: it changes
what a *literal* is, what an exact value is, and what a multiplication by a constant costs.  The 25
syntax worlds and the numeral worlds are orthogonal by construction, and
:func:`world_ranking_invariance` measures that orthogonality rather than asserting it.

The four measurements
---------------------

``A`` **Exactness is a property of the base, not of the number.**  ``1/2`` terminates in base 2 and
base 10 and repeats in base 3; ``1/3`` repeats in 2 and 10 and terminates in 3.  :func:`terminates`
is the predicate, :func:`exactness_table` sweeps it, and :func:`minimal_exact_base` answers the
question **bound-free**: a base makes every corpus constant exact exactly when it is a multiple of
the radical of the least common multiple of their denominators.

``B`` **The operation count is wrong in a way the base decides.**  The project charges ``x * 2``
and ``x * 3`` the same one multiplication.  On a binary machine the first is a shift and the second
is not.  :func:`classify_constant` is the three-way classification the card asks for -- a power of
the base, a sum of distinct powers, or neither -- and :func:`ranking_change_report` recomputes the
project's own cost rankings under it.

``C`` **Where the numerical-equivalence line actually bites.**  ``0.1 + 0.2 != 0.3`` in binary64
while the same statement is true over exact rationals.  That is not algebra: ``1/10`` has no finite
binary expansion, so the literal is already a different number before an operation runs.
:func:`disagreement_table` takes the equivalent writings the project already owns, evaluates them
in exact rationals and in binary64, and counts the pairs that disagree.

``D`` **A representation with a seam, at the numeral level.**  Montgomery form makes modular
multiplication cheap and pays for it at conversion.  :func:`seam_comparison` puts it in the same
``(saving per operation, toll per crossing, crossover)`` shape as 0042's fragment-routing seam and
as the roadmap's Cartesian-against-polar correction, so the three can be compared as one model.

Which cost is being quoted
--------------------------

The roadmap's standing rule is that a figure offered as a cost of *computation* excludes
translation and is taken on the emitted graph, and a figure offered as a cost of *notation*
includes everything a reader pays on every read.  Every function here carries the label in its
docstring, and the two are never summed:

``computation``  :func:`cost_terms`, :func:`entry_cost`, :func:`power_headline`,
:func:`montgomery_table` -- shift counts, multiplication counts, taken on the intended tree, which
IS the dataflow graph.

``notation``  :func:`numeral_length`, and the 25-world bracket totals imported from 0034/0037 --
what a reader pays every time.

No declared threshold
---------------------

The base band :data:`BASE_BAND` exists so a run terminates and is named as a computational limit,
never as a finding.  What is checked beyond it is stated by construction:
:func:`base_signature` shows that the exactness answer for a base depends only on which of the
corpus's denominator primes divide it, so the band already contains one representative of every
class and :func:`signature_classes` enumerates all of them.  The multiply price of ``B`` is not
declared either: :func:`crossing_points` solves for every price at which the ranking changes,
exactly, over the whole ray, because each cost is affine in that price.

The null model
--------------

An integer terminates in every base, so an integer-valued constant carries no information about any
base and a corpus dominated by them will show whatever the integers show.  :func:`stratify`
separates the corpus into that inert stratum and the informative one, and every rate in the report
is computed inside a stratum.
"""

import os
import time
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from typing import Any

from .canonical import operation_cost
from .domain_worlds import CORPUS as LAW_CORPUS
from .domain_worlds import corpus_entries, two_sided_laws
from .grammar import Grammar
from .notational_cost import CONTROL, GRAMMARS
from .notational_cost import CORPUS as FORMULA_CORPUS
from .notational_cost import formula_tree, parenthesis_cost
from .parser import Binary, Node, Number, Variable, parse
from .region_geodesy import INCREMENT_COS, INCREMENT_SIN, WGS84

__all__ = [
    "BASE_BAND",
    "CLASS_NAMES",
    "Constant",
    "CostTerms",
    "DECIMAL_STRATUM",
    "DIVIDE_RATIOS",
    "DYADIC_STRATUM",
    "Entry",
    "HEADLINE_EXPONENT",
    "PROBE_BASES",
    "accuracy_attribution",
    "base_digits",
    "base_signature",
    "blind_terms",
    "calibration_case",
    "classify_constant",
    "constant_corpus",
    "corpus_entries_for_cost",
    "cost_terms",
    "crossing_points",
    "default_worker_count",
    "disagreement_table",
    "entry_cost",
    "evaluate_binary64",
    "evaluate_exact",
    "exactness_table",
    "measure_cell_seconds",
    "measure_pool_startup",
    "minimal_exact_base",
    "montgomery_table",
    "numeral_length",
    "numeral_worlds_report",
    "orientation_by_computation",
    "parallel_decision",
    "power_headline",
    "radical",
    "ranking_change_report",
    "sample_environments",
    "seam_comparison",
    "seam_crossover",
    "shift_classification_table",
    "shortest_addition_chain",
    "should_parallelise",
    "signature_classes",
    "stratify",
    "terminates",
    "worker_count_for",
    "world_ranking_invariance",
]


class UndefinedHere(ZeroDivisionError):
    """A sample point divides by an exact zero.

    A real domain restriction, counted in its own category and never folded into a disagreement,
    which is the discipline experiment 0022 set for the same situation over ``F_p``.
    """


#: The band of bases every sweep runs over.  **A computational limit, not a finding.**  It exists
#: so that a run terminates.  What lies beyond it is not unchecked: :func:`base_signature` reduces
#: every base to the subset of the corpus's denominator primes that divide it, there are finitely
#: many such subsets, and :func:`signature_classes` shows the band already contains a representative
#: of each -- so the exactness answer for a base of any size is determined by a class inside the
#: band.  :func:`exactness_table` reports both the band and the class enumeration.
BASE_BAND: tuple[int, ...] = tuple(range(2, 121))

#: The bases the report tabulates in full.  A presentation choice over :data:`BASE_BAND`, and the
#: only place a base is singled out.  ``2`` is the machine, ``10`` is the human, ``3`` and ``16``
#: are the two hand-worked controls of the termination predicate, ``30`` is the answer
#: :func:`minimal_exact_base` returns, and ``60`` is the historical numeral world that already made
#: the same choice.
PROBE_BASES: tuple[int, ...] = (2, 3, 6, 10, 16, 30, 60)

#: The bases measurement ``B`` recomputes the ranking in.  A sweep rather than a pair: it holds the
#: machine (``2``), the reader (``10``), every base below ``10`` so the curve has a left half, the
#: two the termination predicate is hand-checked in (``3``, ``16``), the answer measurement ``A``
#: returns (``30``) and the historical numeral world that made the same choice (``60``).
RANKING_BASES: tuple[int, ...] = (2, 3, 4, 5, 6, 8, 10, 12, 16, 30, 60)

#: The exponent of the owner's founding question for this axis: ``2 ** 50``.
HEADLINE_EXPONENT: int = 50

#: Names of the three-way classification of a constant multiplier or divisor in a base, plus the
#: identity case which emits no operation at all.
CLASS_NAMES: tuple[str, ...] = ("identity", "shift", "shift_and_add", "general")

#: The divide-to-multiply price ratios the ``B`` sweep runs on.  Division is priced as a multiple
#: of multiplication rather than independently, so the whole cost stays affine in ONE parameter and
#: :func:`crossing_points` can enumerate every ranking change exactly instead of sampling a grid.
#: Three rays, so the sensitivity to that modelling choice is on the page.
DIVIDE_RATIOS: tuple[int, ...] = (1, 2, 4)

#: Sample values whose binary64 image is exact: every one is a dyadic rational, so no literal is
#: rounded on the way in.  Taken from :func:`parseatlas.numerical.validate_expression`'s declared
#: sample points ``(-2, -1, 0, 1, 2)`` with ``0`` dropped -- it makes most denominators vanish --
#: and extended with the halves and quarters that the corpus's own ``/ 2`` produces.
DYADIC_STRATUM: tuple[Fraction, ...] = (
    Fraction(2),
    Fraction(-1),
    Fraction(3),
    Fraction(1, 2),
    Fraction(5),
    Fraction(1, 4),
    Fraction(-2),
    Fraction(7),
)

#: Sample values that are exact in base 10 and inexact in base 2.  The tenths are the calibration
#: case ``0.1 + 0.2 != 0.3`` generalised; ``3/5`` and ``4/5`` are experiment 0051's declared
#: rotation increment, taken from that module rather than invented here.
DECIMAL_STRATUM: tuple[Fraction, ...] = (
    Fraction(1, 10),
    Fraction(3, 10),
    Fraction(7, 10),
    Fraction(9, 10),
    Fraction(3, 5),
    Fraction(4, 5),
    Fraction(11, 10),
    Fraction(13, 10),
)

STRATA: dict[str, tuple[Fraction, ...]] = {
    "dyadic": DYADIC_STRATUM,
    "decimal": DECIMAL_STRATUM,
}


# --------------------------------------------------------------------------- number theory of bases


def radical(n: int) -> int:
    """The product of the distinct primes dividing ``n``; ``radical(1) == 1``.

    The whole of measurement ``A`` turns on this function: a base and its radical make exactly the
    same rationals exact, so the exactness curve over the bases is a function of the radical alone.
    """
    if n < 1:
        raise ValueError(f"radical is defined on positive integers; got {n}")
    result, divisor, remaining = 1, 2, n
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            result *= divisor
            while remaining % divisor == 0:
                remaining //= divisor
        divisor += 1
    if remaining > 1:
        result *= remaining
    return result


def terminates(value: Fraction, base: int) -> bool:
    """Does ``value`` have a finite expansion in ``base``?

    True exactly when every prime dividing the reduced denominator also divides the base, which is
    the classical criterion.  Implemented by repeatedly stripping the greatest common divisor
    rather than by factoring, so it is exact for denominators of any size -- ``10 ** 9`` in the
    WGS 84 constant is not a size this has to think about.

    Hand-worked cases, pinned by the test suite: ``1/2`` terminates in 2 and 10 and not in 3;
    ``1/3`` terminates in 3 and not in 2 or 10; ``1/10`` terminates in 10 and not in 2 or 16;
    ``3/4`` terminates in 16.
    """
    if base < 2:
        raise ValueError(f"a base must be at least 2; got {base}")
    denominator = value.denominator
    while denominator > 1:
        common = gcd(denominator, base)
        if common == 1:
            return False
        while common > 1:
            denominator //= common
            common = gcd(denominator, base)
    return True


def base_digits(number: int, base: int) -> tuple[int, ...]:
    """The base-``base`` digits of a non-negative integer, most significant first."""
    if base < 2:
        raise ValueError(f"a base must be at least 2; got {base}")
    if number < 0:
        raise ValueError(f"base_digits is defined on non-negative integers; got {number}")
    if number == 0:
        return (0,)
    digits: list[int] = []
    while number:
        digits.append(number % base)
        number //= base
    return tuple(reversed(digits))


def numeral_length(number: int, base: int) -> int:
    """How many digits the numeral takes.

    **A cost of notation**: it is what a reader, or a memory, pays for the literal every time.  It
    is never added to any operation count in this module.
    """
    return len(base_digits(abs(number), base))


def base_signature(base: int, primes: Sequence[int]) -> frozenset[int]:
    """Which of ``primes`` divide ``base``.

    This is the whole of a base as far as measurement ``A`` is concerned, and it is why
    :data:`BASE_BAND` is a presentation band rather than a bound on the answer.
    """
    return frozenset(p for p in primes if base % p == 0)


# ---------------------------------------------------------------------------- the constant corpus


@dataclass(frozen=True)
class Constant:
    """One numeric constant the project actually uses, and where it came from.

    ``value`` is the rational the machine has to represent.  A literal on the right of ``/`` is
    recorded as its reciprocal, because dividing by ``k`` is scaling by ``1/k`` and it is ``1/k``
    whose expansion the base either terminates or does not -- that is the only place in this module
    where a literal is transformed, and it is disclosed rather than folded in silently.
    """

    value: Fraction
    source: str
    holder: str
    role: str

    @property
    def is_integer(self) -> bool:
        return self.value.denominator == 1


def _numeric_occurrences(tree: Node) -> tuple[tuple[Fraction, str], ...]:
    """Every numeric literal in a tree, with the role its parent gives it."""
    found: list[tuple[Fraction, str]] = []

    def walk(node: Node, parent: Binary | None, side: str | None) -> None:
        if isinstance(node, Number):
            if parent is None:
                found.append((node.value, "whole"))
            elif parent.operator == "/" and side == "right":
                found.append((node.value, "divisor"))
            elif parent.operator == "/":
                found.append((node.value, "dividend"))
            elif parent.operator == "*":
                found.append((node.value, "multiplier"))
            else:
                found.append((node.value, "addend"))
        elif isinstance(node, Binary):
            walk(node.left, node, "left")
            walk(node.right, node, "right")

    walk(tree, None, None)
    return tuple(found)


def constant_corpus() -> tuple[Constant, ...]:
    """Every numeric constant in the project's named-law corpora, with no constant invented here.

    Three sources, all existing:

    ``0034``  :data:`parseatlas.notational_cost.CORPUS` -- 58 named formulas.
    ``0037``  :data:`parseatlas.domain_worlds.CORPUS` -- 33 named laws in four fields, flattened to
    their written sides.
    ``0051``  :data:`parseatlas.region_geodesy.WGS84` and its declared rotation increment -- the
    only place in the repository where a constant arrives from outside mathematics, and the one
    that decides whether base 2 or base 10 is the better numeral world for real work.

    The corpus therefore inherits those corpora's hand-chosen nature, which the report states as a
    limit rather than a footnote.
    """
    constants: list[Constant] = []
    for formula in FORMULA_CORPUS:
        for value, role in _numeric_occurrences(formula_tree(formula)):
            recorded = 1 / value if role == "divisor" else value
            constants.append(Constant(recorded, "0034", formula.name, role))
    for entry in corpus_entries():
        for value, role in _numeric_occurrences(parse(entry.source, CONTROL)):
            recorded = 1 / value if role == "divisor" else value
            constants.append(Constant(recorded, "0037", entry.name, role))
    constants.extend(
        (
            Constant(WGS84.semi_major, "0051", "wgs84.semi_major", "defining"),
            # The DEFINING constant, taken exactly as WGS 84 publishes it: ``1/f = 298.257223563``.
            # The flattening itself is derived from it, and recording the derived value instead
            # would substitute a number the standard does not state for one it does.
            Constant(WGS84.inverse_flattening, "0051", "wgs84.inverse_flattening", "defining"),
            Constant(INCREMENT_COS, "0051", "rotation_increment.cos", "multiplier"),
            Constant(INCREMENT_SIN, "0051", "rotation_increment.sin", "multiplier"),
        )
    )
    return tuple(constants)


def stratify(constants: Sequence[Constant] | None = None) -> dict[str, Any]:
    """The null model: split the constants into the stratum that cannot inform and the one that can.

    An integer terminates in every base.  It therefore ranks no base above any other and it is
    inert for measurement ``A``, while still being perfectly real for measurement ``B``, where a
    power of the base is a shift and a non-power is not.  Every rate in the report is computed
    inside a stratum for this reason.
    """
    constants = tuple(constants) if constants is not None else constant_corpus()
    inert = tuple(c for c in constants if c.is_integer)
    informative = tuple(c for c in constants if not c.is_integer)
    distinct_inert = sorted({c.value for c in inert})
    distinct_informative = sorted({c.value for c in informative})
    return {
        "occurrences": len(constants),
        "inert_occurrences": len(inert),
        "informative_occurrences": len(informative),
        "distinct": len(set(c.value for c in constants)),
        "distinct_inert": tuple(str(v) for v in distinct_inert),
        "distinct_informative": tuple(str(v) for v in distinct_informative),
        "distinct_inert_count": len(distinct_inert),
        "distinct_informative_count": len(distinct_informative),
        "sources": {
            source: sum(1 for c in constants if c.source == source)
            for source in sorted({c.source for c in constants})
        },
        "roles": {
            role: sum(1 for c in constants if c.role == role)
            for role in sorted({c.role for c in constants})
        },
    }


# ---------------------------------------------------------------------- A. exactness across bases


def _exact_count(values: Sequence[Fraction], base: int) -> int:
    return sum(1 for value in values if terminates(value, base))


def _exact_cell(payload: tuple[int, tuple[Fraction, ...], tuple[Fraction, ...]]) -> dict[str, Any]:
    """One base of the exactness sweep.  A pure function of its payload, so both paths agree."""
    base, informative, occurrences = payload
    return {
        "base": base,
        "radical": radical(base),
        "distinct_exact": _exact_count(informative, base),
        "occurrence_exact": _exact_count(occurrences, base),
    }


def minimal_exact_base(constants: Sequence[Constant] | None = None) -> dict[str, Any]:
    """The smallest base in which EVERY corpus constant is exact, computed without a sweep.

    A base makes ``p/q`` exact exactly when every prime of ``q`` divides it, so a base makes every
    corpus constant exact exactly when it is a multiple of ``radical(lcm of the denominators))``.
    The smallest such base is that radical itself, and the set of ALL such bases is its multiples.
    This is the bound-free half of measurement ``A``: the sweep confirms it, it does not produce it.
    """
    constants = tuple(constants) if constants is not None else constant_corpus()
    denominators = sorted({c.value.denominator for c in constants})
    common = 1
    for denominator in denominators:
        common = common * denominator // gcd(common, denominator)
    minimal = radical(common)
    return {
        "denominators": tuple(denominators),
        "lcm": common,
        "minimal_base": minimal,
        "all_bases": f"every multiple of {minimal}",
        "primes": tuple(sorted(_prime_factors(minimal))),
    }


def _prime_factors(n: int) -> set[int]:
    factors: set[int] = set()
    divisor, remaining = 2, n
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.add(divisor)
            remaining //= divisor
        divisor += 1
    if remaining > 1:
        factors.add(remaining)
    return factors


def signature_classes(constants: Sequence[Constant] | None = None) -> dict[str, Any]:
    """Every base, of any size, classified into finitely many classes -- the bound-free enumeration.

    Only the primes dividing some corpus denominator can matter to exactness.  Call that set ``P``.
    Two bases with the same ``base_signature`` make exactly the same corpus constants exact, so
    there are exactly ``2 ** len(P)`` behaviours and no base outside :data:`BASE_BAND` can exhibit a
    new one.  This function lists them with their smallest representative, which is what the report
    quotes instead of a claim about how far the sweep went.
    """
    constants = tuple(constants) if constants is not None else constant_corpus()
    occurrences = tuple(c.value for c in constants if not c.is_integer)
    distinct = tuple(sorted(set(occurrences)))
    primes = sorted({p for c in constants for p in _prime_factors(c.value.denominator)})
    classes: list[dict[str, Any]] = []
    for mask in range(1 << len(primes)):
        subset = tuple(prime for index, prime in enumerate(primes) if mask >> index & 1)
        product = 1
        for prime in subset:
            product *= prime
        if product >= 2:
            smallest = product
        else:
            smallest = 2
            while base_signature(smallest, primes):
                smallest += 1
        classes.append(
            {
                "signature": subset,
                "smallest_base": smallest,
                "distinct_exact": _exact_count(distinct, smallest),
                "occurrence_exact": _exact_count(occurrences, smallest),
            }
        )
    rows = tuple(sorted(classes, key=lambda row: (len(row["signature"]), row["signature"])))
    return {
        "primes": tuple(primes),
        "class_count": len(rows),
        "expected_class_count": 2 ** len(primes),
        "complete": len(rows) == 2 ** len(primes),
        "classes": rows,
        "informative_distinct": len(distinct),
        "informative_occurrences": len(occurrences),
    }


def exactness_table(
    constants: Sequence[Constant] | None = None,
    bases: Sequence[int] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """The exactness sweep over the base band, with the null stratification applied throughout.

    Reported inside the informative stratum, because the integer stratum is exact in every base and
    would otherwise add the same constant to every column and flatter every base equally.
    """
    constants = tuple(constants) if constants is not None else constant_corpus()
    bases = tuple(bases) if bases is not None else BASE_BAND
    informative_distinct = tuple(sorted({c.value for c in constants if not c.is_integer}))
    informative_occurrences = tuple(c.value for c in constants if not c.is_integer)
    payloads = [(base, informative_distinct, informative_occurrences) for base in bases]
    rows = tuple(_map_cells(_exact_cell, payloads, workers, EXACT_CELL_SECONDS))

    by_base = {row["base"]: row for row in rows}
    total = len(informative_distinct)
    best = max((row["distinct_exact"] for row in rows), default=0)
    monotone = all(
        by_base[a]["distinct_exact"] <= by_base[b]["distinct_exact"]
        for a, b in zip(bases, bases[1:])
    )
    drops = tuple(
        {"from": a, "to": b, "at": by_base[a]["distinct_exact"], "then": by_base[b]["distinct_exact"]}
        for a, b in zip(bases, bases[1:])
        if by_base[a]["distinct_exact"] > by_base[b]["distinct_exact"]
    )
    radical_invariant = all(
        by_base[row["base"]]["distinct_exact"] == by_base[row["radical"]]["distinct_exact"]
        for row in rows
        if row["radical"] in by_base
    )
    return {
        "band": (bases[0], bases[-1]),
        "band_is_a_computational_limit": True,
        "informative_distinct": total,
        "rows": rows,
        "probe": tuple(
            {
                "base": base,
                "distinct_exact": by_base[base]["distinct_exact"],
                "of": total,
                "occurrence_exact": by_base[base]["occurrence_exact"],
                "of_occurrences": len(informative_occurrences),
                "inexact": tuple(
                    str(value) for value in informative_distinct if not terminates(value, base)
                ),
            }
            for base in PROBE_BASES
            if base in by_base
        ),
        "best_distinct_exact": best,
        "first_base_achieving_best": min(
            (row["base"] for row in rows if row["distinct_exact"] == best), default=None
        ),
        "monotone": monotone,
        "descents": drops,
        "descent_count": len(drops),
        "count_depends_only_on_radical": radical_invariant,
        "minimal": minimal_exact_base(constants),
        "classes": signature_classes(constants),
        "base_two_vs_base_ten": {
            "base_2": by_base[2]["distinct_exact"] if 2 in by_base else None,
            "base_10": by_base[10]["distinct_exact"] if 10 in by_base else None,
            "verdict": "base 10 is better for this corpus"
            if 2 in by_base and 10 in by_base and by_base[10]["distinct_exact"] > by_base[2]["distinct_exact"]
            else "base 2 is at least as good for this corpus",
        },
    }


# ------------------------------------------------------ B. the base-aware cost of computation


@dataclass(frozen=True)
class CostTerms:
    """An operation count split by price class.

    **A cost of computation**: taken on the intended tree, which is the emitted dataflow graph, and
    excluding every translation.  ``cheap`` counts shifts and additions, which a machine issues at
    the same unit price; ``multiply`` and ``divide`` count the operations whose price the model
    sweeps.
    """

    cheap: int
    multiply: int
    divide: int

    def total(self, multiply_price: int | Fraction, divide_price: int | Fraction) -> Fraction:
        return Fraction(self.cheap) + self.multiply * multiply_price + self.divide * divide_price

    def as_tuple(self) -> tuple[int, int, int]:
        return (self.cheap, self.multiply, self.divide)


def classify_constant(constant: int, base: int) -> tuple[str, int]:
    """Classify a constant multiplier in a base: a shift, a shift-and-add, or neither.

    Returns ``(class name, nonzero digit count)``.

    ``identity``  ``constant == 1``.  No operation is emitted at all.
    ``shift``  the constant is a power of the base -- one nonzero digit, and that digit is ``1``.
    Scaling by it moves the point and issues no multiplication.
    ``shift_and_add``  every base-``base`` digit is ``0`` or ``1`` and at least two are ``1``.  The
    product is a sum of shifted copies: ``t`` nonzero digits cost ``t - 1`` shifts and ``t - 1``
    additions.  ``x * 5`` in base 2 is ``(x << 2) + x`` -- two cheap operations.
    ``general``  anything else, which is a real multiplication.

    In base 2 the ``general`` class is empty for positive integers, because every one of them is a
    sum of distinct powers of two.  In base 10 it is the common case: ``3`` is the single digit
    ``3``, not a sum of distinct powers of ten, so ``x * 3`` is a multiplication in a decimal
    machine and two cheap operations in a binary one.
    """
    if constant <= 0:
        raise ValueError(f"classify_constant is defined on positive integers; got {constant}")
    digits = base_digits(constant, base)
    nonzero = tuple(digit for digit in digits if digit)
    if constant == 1:
        return "identity", 1
    if len(nonzero) == 1 and nonzero[0] == 1:
        return "shift", 1
    if all(digit in (0, 1) for digit in digits):
        return "shift_and_add", len(nonzero)
    return "general", len(nonzero)


def _constant_multiply_terms(constant: Fraction, base: int) -> CostTerms:
    """What multiplying by a constant costs, in the three price classes."""
    if constant.denominator != 1 or constant.numerator <= 0:
        return CostTerms(0, 1, 0)
    kind, nonzero = classify_constant(constant.numerator, base)
    if kind == "identity":
        return CostTerms(0, 0, 0)
    if kind == "shift":
        return CostTerms(1, 0, 0)
    if kind == "shift_and_add":
        return CostTerms(2 * (nonzero - 1), 0, 0)
    return CostTerms(0, 1, 0)


def _constant_divide_terms(constant: Fraction, base: int) -> CostTerms:
    """What dividing by a constant costs.

    Only a power of the base is cheap.  There is no shift-and-add analogue on the dividing side:
    dividing by ``3`` in base 2 is a division, not two cheap operations, and pretending otherwise
    would be the one place this model could flatter binary.
    """
    if constant.denominator != 1 or constant.numerator <= 0:
        return CostTerms(0, 0, 1)
    kind, _ = classify_constant(constant.numerator, base)
    if kind == "identity":
        return CostTerms(0, 0, 0)
    if kind == "shift":
        return CostTerms(1, 0, 0)
    return CostTerms(0, 0, 1)


def _add(*terms: CostTerms) -> CostTerms:
    return CostTerms(
        sum(t.cheap for t in terms),
        sum(t.multiply for t in terms),
        sum(t.divide for t in terms),
    )


def cost_terms(tree: Node, base: int) -> CostTerms:
    """The base-aware operation count of an intended tree.

    **A cost of computation.**  Every ``+`` and ``-`` is one cheap operation.  A ``*`` with a
    constant operand is priced by :func:`classify_constant`; any other ``*`` is a multiplication.
    A ``/`` by a constant power of the base is a shift; every other ``/`` is a division.

    A node whose BOTH operands are constants would be folded at translation time and never emitted,
    so charging it nothing would be the flow-correct answer.  It is charged as an ordinary constant
    operation here anyway, because :func:`blind_terms` charges it too and the whole point of the
    comparison is that the two models differ only in what the BASE decides.  The corpus contains no
    such node, so the choice moves no number in the report; it is stated rather than left implicit.
    """
    if not isinstance(tree, Binary):
        return CostTerms(0, 0, 0)
    below = _add(cost_terms(tree.left, base), cost_terms(tree.right, base))
    if tree.operator in ("+", "-"):
        return _add(below, CostTerms(1, 0, 0))
    if tree.operator == "*":
        constant = None
        for side in (tree.left, tree.right):
            if isinstance(side, Number):
                constant = side.value
        if constant is None:
            return _add(below, CostTerms(0, 1, 0))
        return _add(below, _constant_multiply_terms(constant, base))
    if isinstance(tree.right, Number):
        return _add(below, _constant_divide_terms(tree.right.value, base))
    return _add(below, CostTerms(0, 0, 1))


def blind_terms(tree: Node) -> CostTerms:
    """The project's own base-blind operation count, from :func:`parseatlas.canonical.operation_cost`.

    This is the "before" of measurement ``B``: every ``*`` is one multiplication and every ``/`` is
    one division, whatever the constant.  It is imported rather than reimplemented so that the
    comparison is against what the project actually charges.
    """
    counts = operation_cost(tree)
    return CostTerms(counts["add"] + counts["sub"], counts["mul"], counts["div"])


@dataclass(frozen=True)
class Entry:
    """One written form of the cost corpus: a name, its source experiment, and its intended tree."""

    name: str
    source: str
    field: str
    tree: Node


def corpus_entries_for_cost() -> tuple[Entry, ...]:
    """The written forms measurement ``B`` ranks: 0034's formulas and 0037's law sides.

    Both are named mathematics and both are already in the repository; nothing is generated.  The
    intended tree of each is its control-grammar parse, which is what direction B means by an
    object.
    """
    entries = [
        Entry(formula.name, "0034", formula.area, formula_tree(formula))
        for formula in FORMULA_CORPUS
    ]
    entries.extend(
        Entry(entry.name, "0037", entry.field, parse(entry.source, CONTROL))
        for entry in corpus_entries()
    )
    return tuple(entries)


def entry_cost(
    terms: CostTerms, multiply_price: int | Fraction, divide_ratio: int | Fraction
) -> Fraction:
    """Total cost at a multiply price, with division priced as ``divide_ratio`` multiplies.

    Affine in ``multiply_price``, which is what makes :func:`crossing_points` exact.
    """
    return terms.total(multiply_price, Fraction(divide_ratio) * multiply_price)


def shift_classification_table(base: Sequence[int] | None = None) -> dict[str, Any]:
    """The three-way classification of every multiplicative and dividing constant in the corpus."""
    bases = tuple(base) if base is not None else PROBE_BASES
    constants = constant_corpus()
    multipliers = sorted(
        {c.value.numerator for c in constants if c.role == "multiplier" and c.is_integer}
    )
    divisors = sorted(
        {(1 / c.value).numerator for c in constants if c.role == "divisor" and c.value.numerator == 1}
    )
    rows = []
    for constant in sorted(set(multipliers) | set(divisors)):
        row: dict[str, Any] = {"constant": constant}
        for b in bases:
            kind, nonzero = classify_constant(constant, b)
            row[f"base_{b}"] = kind
            row[f"nonzero_{b}"] = nonzero
        rows.append(row)
    counts = {
        b: {
            name: sum(1 for row in rows if row[f"base_{b}"] == name) for name in CLASS_NAMES
        }
        for b in bases
    }
    weights = sorted(
        {row[f"nonzero_{b}"] for row in rows for b in bases if row[f"base_{b}"] == "shift_and_add"}
    )
    return {
        "bases": bases,
        "multipliers": tuple(multipliers),
        "divisors": tuple(divisors),
        "rows": tuple(rows),
        "counts": counts,
        "shift_and_add_widths": tuple(weights),
        "widths_are_complete": True,
    }


def _line(terms: CostTerms, divide_ratio: int) -> tuple[int, int]:
    """An entry's cost as the affine line ``(intercept, slope)`` in the multiply price.

    Integers throughout, so every comparison below is an integer comparison and the sweep stays
    exact without paying for rational arithmetic.
    """
    return (terms.cheap, terms.multiply + divide_ratio * terms.divide)


def _sign_at(line: tuple[int, int], numerator: int, denominator: int) -> int:
    """The sign of an affine line at the rational price ``numerator / denominator``."""
    value = line[0] * denominator + line[1] * numerator
    return (value > 0) - (value < 0)


def _ranking(
    entries: Sequence[Entry],
    terms_by_name: dict[str, CostTerms],
    multiply_price: Fraction,
    divide_ratio: int,
) -> tuple[tuple[str, Fraction], ...]:
    scored = [
        (entry.name, entry_cost(terms_by_name[entry.name], multiply_price, divide_ratio))
        for entry in entries
    ]
    scored.sort(key=lambda row: (row[1], row[0]))
    return tuple(scored)


def _reversals_at(
    differences: Sequence[tuple[tuple[int, int], tuple[int, int]]], price: Fraction
) -> int:
    """Ordered pairs whose STRICT order reverses between two cost models, at one price.

    Robust to ties, which a position-by-position comparison of two rankings is not, and it is the
    statistic the report quotes for "did the ranking change".
    """
    numerator, denominator = price.numerator, price.denominator
    count = 0
    for before, after in differences:
        if _sign_at(before, numerator, denominator) * _sign_at(after, numerator, denominator) == -1:
            count += 1
    return count


def _pair_differences(
    names: Sequence[str],
    left: dict[str, CostTerms],
    right: dict[str, CostTerms],
    divide_ratio: int,
) -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    """For every unordered pair, the two cost DIFFERENCES as affine lines in the multiply price."""
    lines_left = {name: _line(left[name], divide_ratio) for name in names}
    lines_right = {name: _line(right[name], divide_ratio) for name in names}
    out = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            la, lb = lines_left[a], lines_left[b]
            ra, rb = lines_right[a], lines_right[b]
            out.append(((la[0] - lb[0], la[1] - lb[1]), (ra[0] - rb[0], ra[1] - rb[1])))
    return tuple(out)


def _line_root(line: tuple[int, int]) -> Fraction | None:
    """Where an affine line crosses zero, or ``None`` when it is constant."""
    intercept, slope = line
    if slope == 0:
        return None
    return Fraction(-intercept, slope)


def reversal_curve(
    differences: Sequence[tuple[tuple[int, int], tuple[int, int]]],
) -> tuple[dict[str, Any], ...]:
    """The reversal count as an exact function of the multiply price over the whole ray ``[1, inf)``.

    Not a sample and not a grid.  Each pair's two cost differences are affine, so each changes sign
    at most once, and the pair contributes a reversal on a union of at most two intervals whose
    endpoints this function solves for exactly.  Accumulating the endpoints as events and sweeping
    them once gives the complete curve: every price at which the answer changes is a breakpoint
    below, and between two breakpoints the count is constant for ever.

    This is what "sweep the parameter until the measurement shows where the limit is" means when
    the curve can be solved rather than sampled.  The last segment runs to infinity, so there is no
    upper bound to disclose.

    Each segment is the OPEN interval between two breakpoints, and its count is the count at every
    generic price inside it. At a breakpoint price itself one of the two differences is zero, so
    that pair ties instead of reversing; the count exactly on a breakpoint is therefore never larger
    than on the segments beside it, and :func:`_reversals_at` is what answers for a named price.
    """
    events: dict[Fraction, int] = {}
    for before, after in differences:
        roots = sorted(
            {root for root in (_line_root(before), _line_root(after)) if root is not None and root > 1}
        )
        edges = [Fraction(1), *roots, None]
        for index in range(len(edges) - 1):
            low, high = edges[index], edges[index + 1]
            probe = low + 1 if high is None else (low + high) / 2
            if (
                _sign_at(before, probe.numerator, probe.denominator)
                * _sign_at(after, probe.numerator, probe.denominator)
                == -1
            ):
                events[low] = events.get(low, 0) + 1
                if high is not None:
                    events[high] = events.get(high, 0) - 1
    running = 0
    breakpoints = sorted(events)
    segments: list[dict[str, Any]] = []
    for index, price in enumerate(breakpoints):
        running += events[price]
        upper = breakpoints[index + 1] if index + 1 < len(breakpoints) else None
        if segments and segments[-1]["reversals"] == running:
            segments[-1]["to"] = "infinity" if upper is None else str(upper)
            continue
        segments.append(
            {
                "from": str(price),
                "to": "infinity" if upper is None else str(upper),
                "reversals": running,
            }
        )
    return tuple(segments)


def crossing_points(
    entries: Sequence[Entry] | None = None,
    base: int = 2,
    divide_ratio: int = 1,
) -> dict[str, Any]:
    """Every multiply price at which the corpus ranking changes, solved exactly -- no grid, no bound.

    Each entry's cost is ``cheap + (multiply + ratio * divide) * price``: affine in the price.  Two
    entries therefore swap at most once, at a price this function solves for in exact rationals.
    Collecting those solutions over every pair gives the COMPLETE set of prices at which the
    ranking changes anywhere on the ray ``price >= 1``, and above the largest of them the ranking is
    constant for ever.  That is what "sweep the parameter until the measurement shows where the
    limit is" means when the curve can be solved instead of sampled.
    """
    entries = tuple(entries) if entries is not None else corpus_entries_for_cost()
    terms = {entry.name: cost_terms(entry.tree, base) for entry in entries}
    names = [entry.name for entry in entries]
    crossings: set[Fraction] = set()
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = terms[names[i]], terms[names[j]]
            slope = (a.multiply - b.multiply) + divide_ratio * (a.divide - b.divide)
            intercept = a.cheap - b.cheap
            if slope == 0:
                continue
            price = Fraction(-intercept, slope)
            if price >= 1:
                crossings.add(price)
    ordered = tuple(sorted(crossings))
    return {
        "base": base,
        "divide_ratio": divide_ratio,
        "crossing_count": len(ordered),
        "crossings": tuple(str(price) for price in ordered),
        "smallest": str(ordered[0]) if ordered else None,
        "largest": str(ordered[-1]) if ordered else None,
        "ranking_constant_above": str(ordered[-1]) if ordered else "1",
        "pairs_examined": len(names) * (len(names) - 1) // 2,
    }


#: The two reference numeral worlds every base in the ``B`` sweep is compared against: the machine's
#: and the reader's.
REFERENCE_BASES: tuple[int, ...] = (2, 10)


def _curve_summary(curve: Sequence[dict[str, Any]]) -> dict[str, Any]:
    counts = [segment["reversals"] for segment in curve] or [0]
    descents = tuple(
        {"at": curve[index + 1]["from"], "from": counts[index], "to": counts[index + 1]}
        for index in range(len(counts) - 1)
        if counts[index] > counts[index + 1]
    )
    return {
        "curve": tuple(curve),
        "segments": len(curve),
        "maximum": max(counts),
        "minimum": min(counts),
        "at_the_far_end": counts[-1],
        "monotone": not descents,
        "descents": descents,
    }


def _ranking_cell(payload: tuple[int, int, str]) -> dict[str, Any]:
    """One (base, divide ratio) cell of the ``B`` sweep, solved over the whole price ray.

    Three curves come out of it: against the project's own base-blind cost, and against each of the
    two reference numeral worlds.  All three are exact over ``[1, infinity)``.
    """
    base, divide_ratio, _ = payload
    entries = corpus_entries_for_cost()
    names = [entry.name for entry in entries]
    aware = {entry.name: cost_terms(entry.tree, base) for entry in entries}
    blind = {entry.name: blind_terms(entry.tree) for entry in entries}
    differences = _pair_differences(names, blind, aware, divide_ratio)
    named_prices = (Fraction(1), Fraction(2), Fraction(3), Fraction(8), Fraction(32))
    samples = []
    for price in named_prices:
        blind_rank = _ranking(entries, blind, price, divide_ratio)
        aware_rank = _ranking(entries, aware, price, divide_ratio)
        samples.append(
            {
                "multiply_price": str(price),
                "reversals_against_blind": _reversals_at(differences, price),
                "cheapest_blind": blind_rank[0][0],
                "cheapest_blind_cost": str(blind_rank[0][1]),
                "cheapest_blind_ties": sum(1 for _, c in blind_rank if c == blind_rank[0][1]),
                "cheapest_aware": aware_rank[0][0],
                "cheapest_aware_cost": str(aware_rank[0][1]),
                "cheapest_aware_ties": sum(1 for _, c in aware_rank if c == aware_rank[0][1]),
            }
        )
    samples = tuple(samples)
    against_reference = {}
    for reference in REFERENCE_BASES:
        other = {entry.name: cost_terms(entry.tree, reference) for entry in entries}
        reference_differences = _pair_differences(names, other, aware, divide_ratio)
        against_reference[reference] = {
            **_curve_summary(reversal_curve(reference_differences)),
            "at_price_3": _reversals_at(reference_differences, Fraction(3)),
        }
    return {
        "base": base,
        "divide_ratio": divide_ratio,
        "crossings": crossing_points(entries, base, divide_ratio),
        "against_blind": _curve_summary(reversal_curve(differences)),
        "against_reference_base": against_reference,
        "samples": samples,
        "pairs": len(names) * (len(names) - 1) // 2,
    }


def ranking_change_report(
    bases: Sequence[int] | None = None,
    ratios: Sequence[int] | None = None,
    workers: int | None = None,
) -> dict[str, Any]:
    """Recompute the project's own cost ranking with shifts priced apart from multiplies.

    Two rankings are recomputed and they answer in opposite directions, which is the point:

    ``changes``  the corpus ranked by COMPUTATION cost.  Pricing a shift apart from a multiply
    reverses strictly ordered pairs of it, and how many depends on the base.  Reported as reversal
    counts over every pair, at every multiply price where anything changes.

    ``does not change``  the 25 syntax worlds ranked by NOTATIONAL cost, which is 0034's and 0037's
    headline.  See :func:`world_ranking_invariance`.  It cannot change, and the reason is structural
    rather than empirical, so the measurement is a confirmation and is reported as plainly as the
    change is.
    """
    bases = tuple(bases) if bases is not None else RANKING_BASES
    ratios = tuple(ratios) if ratios is not None else DIVIDE_RATIOS
    payloads = [(base, ratio, "cell") for base in bases for ratio in ratios]
    rows = tuple(_map_cells(_ranking_cell, payloads, workers, RANKING_CELL_SECONDS))
    entries = corpus_entries_for_cost()
    pairs = len(entries) * (len(entries) - 1) // 2
    cross_base = tuple(
        {
            "divide_ratio": row["divide_ratio"],
            "base": row["base"],
            "reference": reference,
            "reversals_at_price_3": summary["at_price_3"],
            "curve_maximum": summary["maximum"],
        }
        for row in rows
        for reference, summary in row["against_reference_base"].items()
        if reference != row["base"]
    )
    return {
        "entries": len(entries),
        "pairs": pairs,
        "bases": bases,
        "divide_ratios": ratios,
        "cells": rows,
        "base_against_reference": cross_base,
        "max_cross_base_reversals": max(row["curve_maximum"] for row in cross_base),
        "base_two_against_base_ten": tuple(
            row for row in cross_base if row["base"] == 10 and row["reference"] == 2
        ),
        "non_monotone_cells": tuple(
            {"base": row["base"], "divide_ratio": row["divide_ratio"], "descents": row["against_blind"]["descents"]}
            for row in rows
            if not row["against_blind"]["monotone"]
        ),
        "world_ranking": world_ranking_invariance(),
    }


def world_ranking_invariance(grammars: Sequence[Grammar] | None = None) -> dict[str, Any]:
    """The 25-world NOTATIONAL ranking, before and after base-aware arithmetic pricing.

    It does not move, and the reason is structural.  Direction B fixes the intended tree and lets
    only the brackets vary, so the multiset of numeric literals is the same in every world; a
    base-aware arithmetic price is therefore the same additive constant in all 25 columns and
    cannot reorder them.  A cost of notation and a cost of computation are separate orderings of the
    same objects, which is exactly what the roadmap's standing rule says, and this is the
    measurement of it rather than the assertion.

    Both rankings are returned so the test suite can pin them BOTH ways.
    """
    grammars = tuple(grammars) if grammars is not None else GRAMMARS
    entries = corpus_entries_for_cost()
    law_entries = tuple(e for e in entries if e.source == "0037")

    def totals(offsets: dict[str, Fraction]) -> tuple[tuple[str, Fraction], ...]:
        scored = [
            (
                grammar.id,
                sum(
                    (Fraction(parenthesis_cost(entry.tree, grammar)) + offsets[entry.name])
                    for entry in law_entries
                ),
            )
            for grammar in grammars
        ]
        scored.sort(key=lambda row: (row[1], row[0]))
        return tuple(scored)

    zero = {entry.name: Fraction(0) for entry in law_entries}
    before = totals(zero)
    after_by_base = {}
    for base in (2, 10):
        offsets = {
            entry.name: entry_cost(cost_terms(entry.tree, base), Fraction(3), 2)
            for entry in law_entries
        }
        after_by_base[base] = totals(offsets)
    order_before = tuple(name for name, _ in before)
    return {
        "worlds": len(grammars),
        "entries": len(law_entries),
        "before_order": order_before,
        "before_totals": {name: int(total) for name, total in before},
        "after_order": {base: tuple(n for n, _ in rows) for base, rows in after_by_base.items()},
        "order_unchanged": all(
            tuple(n for n, _ in rows) == order_before for rows in after_by_base.values()
        ),
        "control_rank": order_before.index("G0") + 1,
        "control_total": dict(before)["G0"],
        "best_world": order_before[0],
        "best_total": before[0][1],
    }


def orientation_by_computation(bases: Sequence[int] | None = None) -> dict[str, Any]:
    """Which side of a two-sided law is cheaper to COMPUTE, and whether the base decides it.

    0037 asks the same question of notation and answers it in brackets.  This asks it of the
    emitted graph and answers it in operations, at three multiply prices, so that a flip driven by
    the price is visible as such.
    """
    bases = tuple(bases) if bases is not None else (2, 3, 10, 16)
    laws = two_sided_laws()
    rows = []
    flips = []
    for law in laws:
        (role_a, source_a), (role_b, source_b) = law.sides
        tree_a, tree_b = parse(source_a, CONTROL), parse(source_b, CONTROL)
        record: dict[str, Any] = {"law": law.name, "field": law.field, "roles": (role_a, role_b)}
        winners: dict[int, str] = {}
        for base in bases:
            ta, tb = cost_terms(tree_a, base), cost_terms(tree_b, base)
            at_prices = []
            for price in (Fraction(1), Fraction(3), Fraction(8)):
                ca = entry_cost(ta, price, 2)
                cb = entry_cost(tb, price, 2)
                at_prices.append(role_a if ca < cb else role_b if cb < ca else "tie")
            record[f"base_{base}"] = tuple(at_prices)
            winners[base] = at_prices[1]
        record["winner_by_base"] = winners
        decided = {w for w in winners.values() if w != "tie"}
        record["base_decides"] = len(decided) > 1
        if record["base_decides"]:
            flips.append(record["law"])
        rows.append(record)
    return {
        "laws": len(laws),
        "bases": bases,
        "rows": tuple(rows),
        "laws_whose_cheap_side_the_base_decides": tuple(flips),
        "flip_count": len(flips),
    }


# ---------------------------------------------------------- the founding question for this axis


def shortest_addition_chain(target: int) -> dict[str, Any]:
    """The shortest addition chain for ``target``, by exhaustive iterative deepening.

    Exact, not a heuristic: the search deepens by one until it succeeds, so the length it returns is
    the minimum and no bound was chosen in advance.  The chain is taken ascending, which is without
    loss of generality for addition chains.

    An addition chain is what an exponentiation actually costs: each step is one multiplication, so
    ``l(n)`` multiplications is the true price of ``x ** n`` when the base gives no shortcut.
    """
    if target < 1:
        raise ValueError(f"an addition chain is defined for positive targets; got {target}")
    if target == 1:
        return {"target": 1, "length": 0, "chain": (1,)}
    for length in range(1, 64):
        found: list[tuple[int, ...]] = []

        def descend(chain: tuple[int, ...]) -> bool:
            used = len(chain) - 1
            if used == length:
                return chain[-1] == target
            if chain[-1] << (length - used) < target:
                return False
            for i in range(len(chain) - 1, -1, -1):
                for j in range(i, -1, -1):
                    step = chain[i] + chain[j]
                    if step > target or step <= chain[-1]:
                        continue
                    if descend(chain + (step,)):
                        found.append(chain + (step,))
                        return True
            return False

        if descend((1,)):
            return {"target": target, "length": length, "chain": found[0]}
    raise RuntimeError(f"no addition chain found for {target}")


def power_headline(
    exponent: int = HEADLINE_EXPONENT,
    bases: Sequence[int] | None = None,
) -> dict[str, Any]:
    """``2 ** exponent`` in binary against decimal, as an operation count.

    **A cost of computation**, on the emitted graph, translation excluded.

    In base 2 the value has exactly one nonzero digit, so it is a shift: the numeral IS the answer
    and **no multiplication is issued at all**.  In base 10 it has no such structure, so the value
    must be built, and the cheapest way to build it is the shortest addition chain -- whose length
    :func:`shortest_addition_chain` computes exactly.

    The sweep over the band is the point rather than the two numbers: the cost is ``0`` in every
    base that is a power of two and the full chain in every other, so the curve is not a trend, it
    is a partition.
    """
    bases = tuple(bases) if bases is not None else BASE_BAND
    value = 2**exponent
    chain = shortest_addition_chain(exponent)
    rows = []
    for base in bases:
        digits = base_digits(value, base)
        nonzero = sum(1 for digit in digits if digit)
        is_shift = nonzero == 1
        rows.append(
            {
                "base": base,
                "digits": len(digits),
                "nonzero_digits": nonzero,
                "multiplications": 0 if is_shift else chain["length"],
                "is_shift": is_shift,
            }
        )
    free = tuple(row["base"] for row in rows if row["is_shift"])
    by_base = {row["base"]: row for row in rows}
    return {
        "expression": f"2 ** {exponent}",
        "value": value,
        "cost_label": "computation",
        "binary": by_base[2],
        "decimal": by_base[10],
        "multiplications_binary": by_base[2]["multiplications"],
        "multiplications_decimal": by_base[10]["multiplications"],
        "addition_chain": chain,
        "bases_where_it_is_free": free,
        "free_base_count": len(free),
        "free_bases_are_powers_of_two": all(
            base & (base - 1) == 0 for base in free
        ),
        "band": (bases[0], bases[-1]),
        "rows": tuple(rows),
    }


# ------------------------------------------------------------- C. exact against binary64


def evaluate_exact(tree: Node, environment: dict[str, Fraction]) -> Fraction:
    """Evaluate over the exact rationals.  This side is the authority."""
    if isinstance(tree, Number):
        return tree.value
    if isinstance(tree, Variable):
        return environment[tree.name]
    left = evaluate_exact(tree.left, environment)
    right = evaluate_exact(tree.right, environment)
    if tree.operator == "+":
        return left + right
    if tree.operator == "-":
        return left - right
    if tree.operator == "*":
        return left * right
    if right == 0:
        raise UndefinedHere(f"exact division by zero in {tree!r}")
    return left / right


def evaluate_binary64(tree: Node, environment: dict[str, Fraction]) -> float:
    """Evaluate in this machine's binary64, rounding every literal on the way in.

    The rounding of the literals is not incidental -- it is the measurement.  ``1/10`` becomes a
    different number before a single operation runs, which is why a disagreement between two
    algebraically identical writings is a fact about the numeral world and not about the algebra.
    """
    if isinstance(tree, Number):
        return tree.value.numerator / tree.value.denominator
    if isinstance(tree, Variable):
        value = environment[tree.name]
        return value.numerator / value.denominator
    left = evaluate_binary64(tree.left, environment)
    right = evaluate_binary64(tree.right, environment)
    if tree.operator == "+":
        return left + right
    if tree.operator == "-":
        return left - right
    if tree.operator == "*":
        return left * right
    if right == 0.0:
        raise UndefinedHere(f"binary64 division by zero in {tree!r}")
    return left / right


def _free_names(tree: Node) -> tuple[str, ...]:
    names: list[str] = []

    def walk(node: Node) -> None:
        if isinstance(node, Variable):
            names.append(node.name)
        elif isinstance(node, Binary):
            walk(node.left)
            walk(node.right)

    walk(tree)
    return tuple(sorted(set(names)))


def sample_environments(
    names: Sequence[str], stratum: str
) -> tuple[dict[str, Fraction], ...]:
    """Assign the stratum's values to the free names, cyclically, at every offset.

    Deterministic and mechanical: names sorted, values rotated.  No point was chosen because of
    what it produced, which is the only defence a sample of this size has.
    """
    values = STRATA[stratum]
    return tuple(
        {name: values[(index + offset) % len(values)] for index, name in enumerate(names)}
        for offset in range(len(values))
    )


def _has_division(tree: Node) -> bool:
    if isinstance(tree, Binary):
        return tree.operator == "/" or _has_division(tree.left) or _has_division(tree.right)
    return False


def calibration_case() -> dict[str, Any]:
    """``0.1 + 0.2 != 0.3`` in binary64, and ``== `` over exact rationals.

    The one case the whole of measurement ``C`` is calibrated against, and the clearest statement
    of what this axis is: the disagreement is present before any operation runs, because ``1/10``
    is not a binary64 number.
    """
    tenth, fifth, threetenths = Fraction(1, 10), Fraction(2, 10), Fraction(3, 10)
    float_sum = (1 / 10) + (2 / 10)
    float_target = 3 / 10
    return {
        "exact_left": str(tenth + fifth),
        "exact_right": str(threetenths),
        "exact_equal": (tenth + fifth) == threetenths,
        "float_left": float_sum,
        "float_right": float_target,
        "float_equal": float_sum == float_target,
        "float_gap": abs(float_sum - float_target),
        "one_tenth_is_exact_in_base_10": terminates(tenth, 10),
        "one_tenth_is_exact_in_base_2": terminates(tenth, 2),
        "accurate_side": "the exact rationals",
    }


def _disagreement_cell(payload: tuple[str, str]) -> dict[str, Any]:
    """One (law, stratum) cell.  Pure function of its payload, so both paths agree."""
    law_name, stratum = payload
    law = next(item for item in LAW_CORPUS if item.name == law_name)
    (role_a, source_a), (role_b, source_b) = law.sides
    tree_a, tree_b = parse(source_a, CONTROL), parse(source_b, CONTROL)
    names = sorted(set(_free_names(tree_a)) | set(_free_names(tree_b)))
    division_free = not (_has_division(tree_a) or _has_division(tree_b))
    checked = undefined = disagreements = algebra_failures = 0
    accuracy: dict[str, int] = {role_a: 0, role_b: 0, "tie": 0}
    worst: dict[str, Any] | None = None
    for environment in sample_environments(names, stratum):
        try:
            exact_a = evaluate_exact(tree_a, environment)
            exact_b = evaluate_exact(tree_b, environment)
            float_a = evaluate_binary64(tree_a, environment)
            float_b = evaluate_binary64(tree_b, environment)
        except UndefinedHere:
            undefined += 1
            continue
        checked += 1
        if exact_a != exact_b:
            algebra_failures += 1
            continue
        if float_a == float_b:
            continue
        disagreements += 1
        gap_a = abs(Fraction(float_a) - exact_a)
        gap_b = abs(Fraction(float_b) - exact_a)
        if gap_a < gap_b:
            accuracy[role_a] += 1
        elif gap_b < gap_a:
            accuracy[role_b] += 1
        else:
            accuracy["tie"] += 1
        relative = (
            abs(Fraction(float_a) - Fraction(float_b)) / abs(exact_a)
            if exact_a != 0
            else abs(Fraction(float_a) - Fraction(float_b))
        )
        if worst is None or relative > worst["relative"]:
            worst = {
                "relative": relative,
                "law": law_name,
                "environment": {k: str(v) for k, v in environment.items()},
                "float_left": float_a,
                "float_right": float_b,
                "exact": str(exact_a),
            }
    return {
        "law": law_name,
        "field": law.field,
        "stratum": stratum,
        "roles": (role_a, role_b),
        "division_free": division_free,
        "checked": checked,
        "undefined": undefined,
        "algebra_failures": algebra_failures,
        "disagreements": disagreements,
        "accuracy": accuracy,
        "worst": None
        if worst is None
        else {**worst, "relative": float(worst["relative"])},
        "worst_relative": 0.0 if worst is None else float(worst["relative"]),
    }


def disagreement_table(workers: int | None = None) -> dict[str, Any]:
    """How many algebraically identical pairs disagree in binary64, stratified by the input base.

    The stratification is the finding.  Every value of the ``dyadic`` stratum is a binary64 number
    exactly; every value of the ``decimal`` stratum is exact in base 10 and rounded in base 2.  The
    pairs are the same pairs and the algebra is the same algebra.

    The ``division_free`` sub-stratum is the **negative control**: with dyadic inputs and no
    division, no rounding can occur, so the counter must report exactly zero.  A predicate only ever
    asked in the direction of its expected answer is not evidence, and reviews of 0045 and 0051 both
    found one.
    """
    laws = two_sided_laws()
    payloads = [(law.name, stratum) for stratum in sorted(STRATA) for law in laws]
    rows = tuple(_map_cells(_disagreement_cell, payloads, workers, DISAGREEMENT_CELL_SECONDS))
    summary = {}
    for stratum in sorted(STRATA):
        subset = [row for row in rows if row["stratum"] == stratum]
        division_free = [row for row in subset if row["division_free"]]
        summary[stratum] = {
            "laws": len(subset),
            "checked": sum(row["checked"] for row in subset),
            "undefined": sum(row["undefined"] for row in subset),
            "algebra_failures": sum(row["algebra_failures"] for row in subset),
            "disagreements": sum(row["disagreements"] for row in subset),
            "laws_with_a_disagreement": sum(1 for row in subset if row["disagreements"]),
            "division_free_checked": sum(row["checked"] for row in division_free),
            "division_free_disagreements": sum(row["disagreements"] for row in division_free),
            "worst_relative": max((row["worst_relative"] for row in subset), default=0.0),
        }
    return {
        "laws": len(laws),
        "strata": tuple(sorted(STRATA)),
        "rows": rows,
        "summary": summary,
        "calibration": calibration_case(),
        "negative_control": {
            "stratum": "dyadic",
            "restricted_to": "division-free laws",
            "checked": summary["dyadic"]["division_free_checked"],
            "disagreements": summary["dyadic"]["division_free_disagreements"],
            "counter_can_report_zero": summary["dyadic"]["division_free_disagreements"] == 0,
        },
        "accuracy": accuracy_attribution(rows),
    }


def accuracy_attribution(rows: Sequence[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Which writing is the accurate one, per law -- not merely that the two differ.

    Accuracy is measured against the exact rational, which is the authority.  A law is called
    ``decided`` when one of its two writings is nearer the exact value at every point where they
    disagree at all; otherwise the corpus has no verdict for it and the report says so.
    """
    if rows is None:
        rows = disagreement_table()["rows"]
    decided: list[dict[str, Any]] = []
    split: list[dict[str, Any]] = []
    for row in rows:
        if not row["disagreements"]:
            continue
        role_a, role_b = row["roles"]
        wins_a, wins_b = row["accuracy"][role_a], row["accuracy"][role_b]
        record = {
            "law": row["law"],
            "stratum": row["stratum"],
            "roles": row["roles"],
            "wins": (wins_a, wins_b),
            "disagreements": row["disagreements"],
        }
        if wins_a and not wins_b:
            decided.append({**record, "accurate_writing": role_a})
        elif wins_b and not wins_a:
            decided.append({**record, "accurate_writing": role_b})
        else:
            split.append(record)
    winners = [row["accurate_writing"] for row in decided]
    return {
        "decided": tuple(decided),
        "decided_count": len(decided),
        "split": tuple(split),
        "split_count": len(split),
        "winning_roles": {role: winners.count(role) for role in sorted(set(winners))},
        "one_side_always_wins": len(set(winners)) <= 1 and not split,
    }


# ------------------------------------------------------------- D. a seam at the numeral level


def seam_crossover(
    saving_per_operation: Fraction, toll_per_crossing: Fraction
) -> dict[str, Any]:
    """The one model all three seams in this project share.

    A representation with a seam pays a fixed toll each time a value crosses the boundary and saves
    a fixed amount on each operation done inside.  Over ``n`` operations per crossing::

        gain(n) = n * saving  -  toll                crossover at  n* = toll / saving

    So the quantity that decides is **operations per boundary crossing**, which is exactly the
    correction the roadmap records for the Cartesian-against-polar probe.  When ``saving <= 0``
    there is no crossover at any ``n`` and the seam is never worth paying.
    """
    if saving_per_operation <= 0:
        return {
            "saving_per_operation": str(saving_per_operation),
            "toll_per_crossing": str(toll_per_crossing),
            "crossover": None,
            "pays_at_any_n": False,
        }
    crossover = Fraction(toll_per_crossing) / Fraction(saving_per_operation)
    return {
        "saving_per_operation": str(saving_per_operation),
        "toll_per_crossing": str(toll_per_crossing),
        "crossover": str(crossover),
        "crossover_float": float(crossover),
        "smallest_integer_n_that_pays": int(crossover) + 1,
        "pays_at_any_n": True,
    }


def montgomery_table(
    ratios: Sequence[int] | None = None,
    operands: int = 2,
    words: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Montgomery form as an operation count, in and out, per crossing, with the crossover swept.

    **A model, not a measured implementation**, and the report says so.  The units are
    multiplications of full-width operands.

    ``classical modular multiplication``  one multiplication plus one division-based reduction.
    With a reduction priced at ``r`` multiplications, that is ``1 + r``.
    ``Montgomery modular multiplication``  two multiplications and no division at all: ``2``.
    ``conversion in``  one Montgomery multiplication by the precomputed ``R ** 2 mod n``: ``2`` per
    operand entering the form.
    ``conversion out``  one reduction step: ``1``.

    So the saving is ``r - 1`` multiplications per modular multiplication and the toll is
    ``2 * operands + 1`` multiplications per crossing, and the crossover follows from
    :func:`seam_crossover`.  The reduction price ``r`` is **swept, not declared**: at ``r <= 1``
    there is no crossover at any chain length, and that is the honest boundary of the claim.

    ``words`` instantiates the same model at word level, where a schoolbook product of ``k``-word
    operands is ``k ** 2`` word multiplications, so the toll in word multiplications is
    ``(2 * operands + 1) * k ** 2``.  It changes the units and not the crossover, which is itself
    the observation: the crossover is a ratio and the ratio does not know how wide the modulus is.
    """
    ratios = tuple(ratios) if ratios is not None else (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
    words = tuple(words) if words is not None else (1, 2, 4, 8, 16, 32, 64)
    rows = []
    for ratio in ratios:
        saving = Fraction(ratio - 1)
        toll = Fraction(2 * operands + 1)
        crossing = seam_crossover(saving, toll)
        rows.append(
            {
                "reduction_price": ratio,
                "classical_per_operation": str(Fraction(1 + ratio)),
                "montgomery_per_operation": "2",
                "saving_per_operation": str(saving),
                "toll_per_crossing": str(toll),
                **{k: v for k, v in crossing.items() if k not in ("saving_per_operation", "toll_per_crossing")},
                "asymptotic_ratio": str(Fraction(1 + ratio, 2)),
                "asymptotic_ratio_float": float(Fraction(1 + ratio, 2)),
            }
        )
    word_rows = tuple(
        {
            "words": k,
            "multiply_word_operations": k * k,
            "toll_word_operations": (2 * operands + 1) * k * k,
            "crossover_unchanged": True,
        }
        for k in words
    )
    paying = tuple(row["reduction_price"] for row in rows if row["pays_at_any_n"])
    return {
        "model": "operation counts, full-width multiplications",
        "cost_label": "computation",
        "operands_per_crossing": operands,
        "reduction_prices": ratios,
        "rows": tuple(rows),
        "never_pays_below_or_at": max(
            (row["reduction_price"] for row in rows if not row["pays_at_any_n"]), default=None
        ),
        "smallest_price_that_ever_pays": min(paying, default=None),
        "price_at_which_one_operation_per_crossing_pays": min(
            (
                row["reduction_price"]
                for row in rows
                if row["pays_at_any_n"] and row["smallest_integer_n_that_pays"] <= 1
            ),
            default=None,
        ),
        "asymptotic_ratio_is_bounded": True,
        "word_level": word_rows,
    }


#: Experiment 0042's published Model II figures, quoted and not recomputed: 87 named intermediates
#: bought at most 7 brackets of interior cost against a 33-bracket single-convention baseline, and
#: the report states the break-even naming price as ``33/87``.
FRAGMENT_ROUTING_FIGURES: dict[str, int] = {
    "fragments": 87,
    "crossings": 87,
    "single_convention_brackets": 33,
    "interior_brackets_removable": 7,
    "naming_units": 87,
}


def seam_comparison(reduction_price: int = 6) -> dict[str, Any]:
    """Montgomery's seam against 0042's, in one shape, with the roadmap's polar probe beside them.

    The three rows share an algebra and differ in one thing, and that difference is worth more than
    any of the three numbers.

    ``Montgomery``  the operations per crossing are a free parameter of the program.  Raise the
    chain and the toll amortises.
    ``Cartesian to polar``  the same, and the roadmap's corrected figure -- ``4n`` against ``n + 4``
    -- puts its crossover at ``4/3``, so polar wins from two operations per crossing.
    ``0042 Model II``  the operations per crossing are **pinned at one by the splitting rule**.
    Every fragment is crossed exactly once and delivers exactly its own interior brackets, so the
    architecture cannot walk up the curve however long the document gets.  0042's break-even is
    therefore reported as a naming price rather than as a chain length, and the crossover it would
    need -- ``87 / 33`` fragments' worth of prize per crossing -- is unreachable by construction.

    So the two seams do **not** behave the same way, and the reason is not that the arithmetic
    differs.  It is that one of them has a free ``n`` and the other does not.
    """
    montgomery = seam_crossover(Fraction(reduction_price - 1), Fraction(5))
    polar = seam_crossover(Fraction(3), Fraction(4))
    prize = Fraction(FRAGMENT_ROUTING_FIGURES["single_convention_brackets"])
    names = Fraction(FRAGMENT_ROUTING_FIGURES["naming_units"])
    routing = seam_crossover(prize / names, Fraction(1))
    return {
        "rows": (
            {
                "seam": "montgomery_form",
                "unit": "full-width multiplications",
                "saving_per_operation": montgomery["saving_per_operation"],
                "toll_per_crossing": montgomery["toll_per_crossing"],
                "crossover": montgomery["crossover"],
                "operations_per_crossing_available": "free",
                "reachable": True,
            },
            {
                "seam": "cartesian_to_polar",
                "unit": "multiplications",
                "saving_per_operation": polar["saving_per_operation"],
                "toll_per_crossing": polar["toll_per_crossing"],
                "crossover": polar["crossover"],
                "operations_per_crossing_available": "free",
                "reachable": True,
            },
            {
                "seam": "fragment_routing_model_ii",
                "unit": "bracket pairs against naming units",
                "saving_per_operation": routing["saving_per_operation"],
                "toll_per_crossing": routing["toll_per_crossing"],
                "crossover": routing["crossover"],
                "operations_per_crossing_available": "1, pinned by the splitting rule",
                "reachable": False,
            },
        ),
        "montgomery_reduction_price": reduction_price,
        "routing_break_even_naming_price": str(prize / names),
        "routing_crossover_needed": routing["crossover"],
        "routing_operations_per_crossing": 1,
        "seams_behave_the_same": False,
        "difference": "the operations per crossing is a free parameter in one seam and fixed at one in the other",
    }


# ------------------------------------------------------------------------------------ concurrency
#
# Repository policy is multicore by default and it also says a sequential path is a valid outcome
# when a measurement justifies it.  Every workload here is a pure function of its payload, so the
# two paths return identical records and the test suite asserts that rather than assuming it.  The
# decision constants below are measured on this machine by :func:`measure_cell_seconds` and
# :func:`measure_pool_startup`, never inherited from another module: 0037's cells carry SymPy and
# these do not.

#: Cores kept free so a sweep cannot starve the interactive session it is run from.
WORKER_HEADROOM_CORES: int = 2

#: An upper bound on the spawn cost any one sweep has to amortise.
WORKER_CAP: int = 12

#: What raising a spawn-start pool costs on this machine, in seconds.  **Observed** by
#: :func:`measure_pool_startup` as the minimum of three runs -- ``1.0994`` s and ``1.3273`` s on two runs with 12
#: workers on 16 cores -- and this constant is declared at ``1.3`` s, which is neither reading: it is a round
#: number between them, and the routing decision is unchanged at ``1.0994``, at ``1.3`` and at ``1.3273``.  Every worker re-imports this module and therefore SymPy, which is
#: where the second goes.  Experiment 0037 declares ``1.2`` s and 0051 declares ``2.20`` s for the
#: same quantity; neither is reused, because each was measured on a different import graph.
POOL_STARTUP_SECONDS: float = 1.3

#: Measured seconds per cell for the four workloads.  They are what decides the sequential-against-
#: parallel question, and a cell COUNT cannot decide it: an exactness cell is a handful of integer
#: gcds and a ranking cell is a full pairwise crossing enumeration over the corpus, and the two are
#: orders of magnitude apart.
EXACT_CELL_SECONDS: float = 7.0e-06
RANKING_CELL_SECONDS: float = 0.10
DISAGREEMENT_CELL_SECONDS: float = 2.2e-04


def worker_count_for(cores: int, cell_count: int) -> int:
    """Worker count for a machine with ``cores`` cores and ``cell_count`` independent cells."""
    return max(1, min(cores - WORKER_HEADROOM_CORES, WORKER_CAP, max(cell_count, 1)))


def default_worker_count(cell_count: int) -> int:
    """Worker count derived from the OBSERVED core count, never from a hardcoded constant."""
    return worker_count_for(os.cpu_count() or 1, cell_count)


def should_parallelise(cell_count: int, seconds_per_cell: float, workers: int) -> bool:
    """Whether a pool is worth raising for this much work, from measured costs."""
    if workers <= 1 or cell_count <= 1:
        return False
    sequential = cell_count * seconds_per_cell
    return POOL_STARTUP_SECONDS + sequential / workers < sequential


def _map_cells(
    task: Any,
    payloads: Sequence[Any],
    workers: int | None,
    seconds_per_cell: float,
) -> list[Any]:
    """Run one independent cell per payload, across processes when the measurement says to.

    ``executor.map`` preserves input order and the cells share no state, so the two paths return
    identical records.  ``workers=None`` takes the measured decision; an explicit ``workers`` forces
    a path, which is what lets a test run both over the same work.
    """
    resolved = default_worker_count(len(payloads)) if workers is None else workers
    if workers is None and not should_parallelise(len(payloads), seconds_per_cell, resolved):
        resolved = 1
    if resolved <= 1 or len(payloads) <= 1:
        return [task(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=min(resolved, len(payloads))) as executor:
        return list(executor.map(task, payloads, chunksize=1))


def _trivial_cell(payload: int) -> int:
    """A cell that does nothing, so that timing it times only the pool."""
    return payload


def measure_pool_startup(workers: int | None = None, repeats: int = 3) -> dict[str, Any]:
    """Time raising a spawn-start pool whose workers each import this module."""
    resolved = default_worker_count(64) if workers is None else workers
    best = float("inf")
    for _ in range(max(1, repeats)):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=resolved) as executor:
            list(executor.map(_trivial_cell, range(resolved), chunksize=1))
        best = min(best, time.perf_counter() - start)
    return {
        "workers": resolved,
        "cores": os.cpu_count(),
        "repeats": repeats,
        "seconds": best,
        "declared": POOL_STARTUP_SECONDS,
    }


def measure_cell_seconds() -> dict[str, Any]:
    """Time one cell of each workload, so the routing constants are evidence and not a guess."""
    constants = constant_corpus()
    informative = tuple(sorted({c.value for c in constants if not c.is_integer}))
    occurrences = tuple(c.value for c in constants if not c.is_integer)

    start = time.perf_counter()
    for base in BASE_BAND:
        _exact_cell((base, informative, occurrences))
    exact_elapsed = time.perf_counter() - start

    start = time.perf_counter()
    _ranking_cell((2, 1, "cell"))
    ranking_elapsed = time.perf_counter() - start

    laws = two_sided_laws()
    start = time.perf_counter()
    for law in laws:
        _disagreement_cell((law.name, "decimal"))
    disagreement_elapsed = time.perf_counter() - start

    return {
        "exact_cells": len(BASE_BAND),
        "exact_seconds": exact_elapsed,
        "exact_seconds_per_cell": exact_elapsed / len(BASE_BAND),
        "declared_exact_seconds_per_cell": EXACT_CELL_SECONDS,
        "ranking_cells": 1,
        "ranking_seconds": ranking_elapsed,
        "ranking_seconds_per_cell": ranking_elapsed,
        "declared_ranking_seconds_per_cell": RANKING_CELL_SECONDS,
        "disagreement_cells": len(laws),
        "disagreement_seconds": disagreement_elapsed,
        "disagreement_seconds_per_cell": disagreement_elapsed / len(laws),
        "declared_disagreement_seconds_per_cell": DISAGREEMENT_CELL_SECONDS,
    }


def parallel_decision() -> dict[str, Any]:
    """Time both paths of each sweep, check they agree, and record which one the measurement picks."""
    out: dict[str, Any] = {"cores": os.cpu_count()}

    exact_cells = len(BASE_BAND)
    exact_workers = default_worker_count(exact_cells)
    start = time.perf_counter()
    exact_sequential = exactness_table(workers=1)
    exact_sequential_seconds = time.perf_counter() - start
    start = time.perf_counter()
    exact_parallel = exactness_table(workers=exact_workers)
    exact_parallel_seconds = time.perf_counter() - start
    out["exactness"] = {
        "cells": exact_cells,
        "workers": exact_workers,
        "sequential_seconds": exact_sequential_seconds,
        "parallel_seconds": exact_parallel_seconds,
        "speedup": exact_sequential_seconds / exact_parallel_seconds
        if exact_parallel_seconds
        else None,
        "records_identical": exact_sequential["rows"] == exact_parallel["rows"],
        "default_decision": "parallel"
        if should_parallelise(exact_cells, EXACT_CELL_SECONDS, exact_workers)
        else "sequential",
    }

    ranking_cells = len(RANKING_BASES) * len(DIVIDE_RATIOS)
    ranking_workers = default_worker_count(ranking_cells)
    start = time.perf_counter()
    ranking_sequential = ranking_change_report(workers=1)
    ranking_sequential_seconds = time.perf_counter() - start
    start = time.perf_counter()
    ranking_parallel = ranking_change_report(workers=ranking_workers)
    ranking_parallel_seconds = time.perf_counter() - start
    out["ranking"] = {
        "cells": ranking_cells,
        "workers": ranking_workers,
        "sequential_seconds": ranking_sequential_seconds,
        "parallel_seconds": ranking_parallel_seconds,
        "speedup": ranking_sequential_seconds / ranking_parallel_seconds
        if ranking_parallel_seconds
        else None,
        "records_identical": ranking_sequential["cells"] == ranking_parallel["cells"],
        "default_decision": "parallel"
        if should_parallelise(ranking_cells, RANKING_CELL_SECONDS, ranking_workers)
        else "sequential",
    }

    disagreement_cells = len(two_sided_laws()) * len(STRATA)
    disagreement_workers = default_worker_count(disagreement_cells)
    start = time.perf_counter()
    disagreement_sequential = disagreement_table(workers=1)
    disagreement_sequential_seconds = time.perf_counter() - start
    start = time.perf_counter()
    disagreement_parallel = disagreement_table(workers=disagreement_workers)
    disagreement_parallel_seconds = time.perf_counter() - start
    out["disagreement"] = {
        "cells": disagreement_cells,
        "workers": disagreement_workers,
        "sequential_seconds": disagreement_sequential_seconds,
        "parallel_seconds": disagreement_parallel_seconds,
        "speedup": disagreement_sequential_seconds / disagreement_parallel_seconds
        if disagreement_parallel_seconds
        else None,
        "records_identical": disagreement_sequential["rows"] == disagreement_parallel["rows"],
        "default_decision": "parallel"
        if should_parallelise(disagreement_cells, DISAGREEMENT_CELL_SECONDS, disagreement_workers)
        else "sequential",
    }
    return out


# ----------------------------------------------------------------------------------------- report


def numeral_worlds_report(timing: bool = False) -> dict[str, Any]:
    """Everything experiment 0054 measures, in one record."""
    constants = constant_corpus()
    report: dict[str, Any] = {
        "experiment": "0054_numeral_worlds",
        "headline": power_headline(),
        "corpus": stratify(constants),
        "exactness": exactness_table(constants),
        "classification": shift_classification_table(),
        "ranking": ranking_change_report(),
        "orientation": orientation_by_computation(),
        "numerical": disagreement_table(),
        "montgomery": montgomery_table(),
        "seams": seam_comparison(),
    }
    if timing:
        report["parallel_decision"] = parallel_decision()
    return report
