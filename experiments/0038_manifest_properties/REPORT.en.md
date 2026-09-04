# ParseAtlas experiment 0038: what each world shows us

## Purpose

**No convention shows everything.** Of the 34 objects, **25** have more than one true property
(distribution: `{1: 9, 2: 4, 5: 6, 6: 12, 7: 3}`), and of the 25 worlds **not one** makes
all the properties of any of them manifest at once — **0 cells of the 625 that concern those 25 objects**.

(The remaining `9` objects have exactly one true property, so they are trivially "fully visible"
in all 25 worlds — and this is where `complete_cells = 175` comes from. They can establish nothing and are excluded.
An earlier edition of the report wrote `27` here, and `0 cells of 850`; `27` was `34 - 7`, a different set -
`triangle_area` and `chain_rule` were in it, although each has one property. The qualitative conclusion
does not change, the number was corrected.) And two properties — `constant_term` and `roots` — are **never, in any world, on any
object, visible together**; this is not a pair forbidden by the rules, it is a measurement.

That is the content of this card: changing the representation changes not only the **cost** (0034, 0037) but also what can
be **seen**. Two writings of one and the same object bring different properties to the surface, and
a mathematician notices what is visible. The calibration case says it in one line: `2x^2 + 3x - 5`, with roots
`-5/2` and `1`, is written most cheaply in **17 of the 25 worlds** as `2 * x * x + 3 * x - 5` (the
degree, the leading coefficient and the constant term are visible; the roots are **not**), and in **8 worlds** as
`(2 * x + 5) * (x - 1)` (the roots are visible; the constant term and the leading coefficient are **not**).

### Rule-relativity: this belongs in the first section and not in the limits

**"Manifest" here means exactly what the shape rules declared in this module say, and every
number is relative to them.** Another, equally conservative set of rules would shift the numbers. Two
regimes were therefore measured and both are published:

```text
transparent (main)      a parenthesis is punctuation: a native of the world reads the string with its
                        own grammar and so has the tree for free; algebra it does not have for free.
                        The world still decides what you see - because it decides which writing is cheap.
opaque (robustness)     a parenthesis is a visual capsule: what is written inside it is one unit and the rule
                        cannot look inside. Here the grammar acts twice - it chooses the writing
                        and it decides how much sits inside parentheses.
```

What survived and what did not, in one table:

| conclusion | transparent | opaque | survived? |
|---|---|---|---|
| no world shows all the properties of an object | 0/25 | 0/25 | **yes** |
| `constant_term` x `roots` never together | 0 cells | 0 cells | **yes** |
| the full set of mutually exclusive pairs | 8 pairs | the same 8 | **yes** |
| "6 properties are visible in every world" | 6/7 | **1/7** | **no** |
| the exact position of `G0` in the ranking | 1 (joint) | 3 | **no** |

So **the conclusions about the trade are robust, while the countable accounting is not.**

## The rules of manifestness

The rules obey one discipline without exception: a rule is a **shape test on the written form**. It
may read the tokens, count them, and see how they are grouped. It may **not** do
algebra — no expansion, no factoring, no collecting like terms, no solving. If deciding a property
requires rewriting the expression, the property is not manifest.

The vocabulary is closed and has seven members. Five of them concern the **principal variable**, which is **declared**
and not computed (`PRINCIPAL_VARIABLES`): determining it ("the most frequent variable") would be a judgement
dressed up as a measurement.

| property | shape rule (on the written form) | algebraic control |
|---|---|---|
| `degree` | it is a sum of monomials and the variable occurs (degree = its repetitions in the longest monomial), **or** it is a product whose factors are at most linear in the variable (degree = the number of factors carrying the variable) | the object is a polynomial in that variable |
| `leading_coefficient` | it is a sum of monomials and **exactly one** monomial attains the highest degree | polynomial in that variable |
| `constant_term` | it is a sum of monomials and **at most one** monomial is free of the variable | polynomial in that variable |
| `roots` | the top operator is multiplicative, every denominator is free of the variable, and every numerator is a leaf or a monomial sum linear in the variable (with exactly one linear term) | a polynomial of degree >= 1 whose roots cover the full degree |
| `factor_structure` | the top operator is `*` and **at least two** of its numerator factors are not leaves | the object has at least two non-constant factors |
| `sign_structure` | the top level is an additive chain of >=2 summands and every summand is a monomial | the expanded object has >=2 terms |
| `even_parity` | it is a sum of monomials and **every** monomial carries the variable an even number of times | `v -> -v` does not change the object |

### Three decisions that are declared and not tacit

**1. Reading a root off a linear factor counts as reading and not as algebra.** Taking `-5/2` from
`2 * x + 5` is one sign change and one division on visible tokens. The rule proposed by the card ("top level is a
product of factors each linear in the principal variable") means exactly this, and it is the judgement
that, under the card's own formulation, would throw the calibration case out.

**2. `roots` requires the object to be presented as a product.** `m * x + b` is a list of coefficients
and not a factorisation; a root must be derived from it. For a product, by contrast, this presentation
is itself the presentation of the roots. This line is declared, is pinned by a test and is checked by mutation.

**3. The `constant_term` rule proposed by the card was corrected.** "top level is a sum with a leaf constant
addend" is **wrong**: `fa - dfa * a + dfa * x` has two variable-free summands and its
constant term is their sum. Pointing at one of them is false, and adding two of them is algebra. So the rule is
"**at most one** variable-free summand".

### Control: manifest => true, and more — the value read off is correct

`ground_truth` computes the same properties **algebraically** (SymPy: factor, expand, solve, subs). This is the
control, and it is deliberately a computation of the opposite kind. But a weak control ("the property holds") is not
enough, so `value_audit` goes further: for every manifest writing it extracts the
**value** a reader would take away — the degree, the leading coefficient, the constant term, the
multiset of roots — and compares it with SymPy.

```text
manifest => true       1700 cells (34 x 25 x 2 regimes),  2573 claims,   0 violations
value read off         2156 checks,                                      0 mismatches
```

## Corpus

**The corpus is imported and not recreated.** It is the corpus of named laws of 0037
(`parseatlas.domain_worlds.CORPUS`, 33 laws, 4 fields) plus the calibration quadratic of the card.

```text
objects            34        writings           50        two-sided   16
imported laws      33        one-sided          18        fields       4
canonical sources   OK       identities hold    OK        principal variable declared for 21
```

`canonical_sources` means that every source string is already the minimal rendering in the control grammar.
`identities_hold` means that both sides of a two-sided law are, according to SymPy, **one and the same
object** — which is necessary, because this is what makes the world's choice a choice and not a comparison
between two different things.

An object with a single writing gives the world nothing to choose; the 16 two-sided objects do, and
**all 16 really do bend** — for each of them, across the 25 worlds, each writing wins at least once.

## Null model

An object whose manifest set is the same in every world **can carry no conclusion**: it adds the same thing
to every world.

```text
constant manifest set (one and the same in all 25 worlds)   18 / 34   -- exactly the one-writing objects
constant rendered text (one and the same in all 25 worlds)   1 / 34   -- chain_rule (dfg * dg)
forced total (their contribution in every world)                  28
movable subcorpus                                                 16
```

After removing them: **the ranking order is identical symbol for symbol**, the rank of `G0` is unchanged (`1`), the spread
is unchanged (`19`). So the ranking measures conventions and not the size of the corpus. In the opaque regime the
objects with a constant manifest set number only `5` (there, the placement of parentheses itself changes visibility), the forced
total is `0`, and the conclusion is the same.

## Observed results

### 1. Is any property visible in every world

**Six** of the seven are manifest in all 25 worlds (taken as a union over the corpus); `factor_structure` — in only
**20**.

| property | worlds (of 25) | objects (of 34) | true on objects |
|---|---|---|---|
| `degree` | 25 | 20 | 21 |
| `leading_coefficient` | 25 | 14 | 21 |
| `constant_term` | 25 | 12 | 21 |
| `roots` | 25 | 11 | 21 |
| `sign_structure` | 25 | 25 | 32 |
| `even_parity` | 25 | 4 | 4 |
| **`factor_structure`** | **20** | 8 | 20 |

And the five worlds in which factor structure is **never** visible are:

```text
G0   */ +-        <-- our convention
G15  * - + /
G16  * - / +
G18  * / - +      <-- the overall winner of 0037
G24  / * - +
```

**In our convention, none of these 34 objects is written most cheaply as a product of two compound
factors.** In `G0` the expanded side is always cheaper or equal, so a factorisation never
appears on the surface. This is the direct visual consequence of the roadmap's prediction.

### 2. Is there a property visible in no world

Taken as a union over the corpus — **no**: `universally_hidden` is an empty tuple and is printed as such
rather than omitted. But one level down the picture is different:

```text
(object, property) pairs that are true                      140
of those, manifest somewhere                                 94
of those, manifest nowhere, in no world                      46   (32.9%)
objects on which nothing is visible in any world              5
```

The five objects that expose nothing in any world:

```text
distance_components  (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)   5 true properties, 0 visible
slope                (y2 - y1) / (x2 - x1)                           2 true, 0 visible
triangle_area        b * h / 2                                       1 true, 0 visible
chain_rule           dfg * dg                                        1 true, 0 visible
riemann_sum_term     fxi * (b - a) / n                               2 true, 0 visible
```

Per-property breakdown of on how many objects a property is true but nowhere visible:
`factor_structure` 12, `roots` 10, `constant_term` 9, `leading_coefficient` 7, `sign_structure` 7,
`degree` 1, `even_parity` 0.

### 3. Which world exposes the most, and where `G0` stands

`G0` is **joint-first** of the 25, together with `G17`, at `77` manifest facts over 850 cells.

| rank | id | precedence | manifest total | monomial-sum writings | factored writings |
|---|---|---|---|---|---|
| **1** | **`G0`** | `*/ +-` | **77** | 27 | 5 |
| 1 | `G17` | `* / + -` | 77 | 26 | 6 |
| 3 | `G14` | `* + / -` | 76 | 25 | 7 |
| 4 | `G23` | `/ * + -` | 75 | 24 | 8 |
| 5 | `G13` | `* + - /` | 74 | 23 | 9 |
| 5 | `G18` | `* / - +` | 74 | 26 | 5 |
| 7 | `G16` | `* - / +` | 72 | 24 | 7 |
| 7 | `G24` | `/ * - +` | 72 | 24 | 7 |
| 9 | `G15` | `* - + /` | 71 | 23 | 8 |
| 10 | `G04` | `+ * / -` | 69 | 20 | 12 |
| 11 | `G06` | `+ / * -` | 68 | 19 | 13 |
| 11 | `G20` | `/ + * -` | 68 | 19 | 13 |
| 13 | `G03` | `+ * - /` | 67 | 18 | 14 |
| 14 | `G22` | `/ - * +` | 62 | 20 | 9 |
| 15 | `G10` | `- * / +` | 61 | 19 | 10 |
| 16 | `G05` | `+ / - *` | 60 | 16 | 13 |
| 16 | `G09` | `- * + /` | 60 | 18 | 11 |
| 16 | `G12` | `- / * +` | 60 | 18 | 11 |
| 16 | `G19` | `/ + - *` | 60 | 16 | 13 |
| 16 | `G21` | `/ - + *` | 60 | 16 | 13 |
| 21 | `G01` | `+ - * /` | 58 | 14 | 15 |
| 21 | `G02` | `+ - / *` | 58 | 14 | 15 |
| 21 | `G07` | `- + * /` | 58 | 14 | 15 |
| 21 | `G08` | `- + / *` | 58 | 14 | 15 |
| 21 | `G11` | `- / + *` | 58 | 14 | 15 |

**This ranking must be read together with the following sentence.** The vocabulary **is not neutral**
between the two principal shapes: the monomial-sum shape carries four properties (`leading_coefficient`,
`constant_term`, `sign_structure`, `even_parity`), the factored shape carries two (`roots`, `factor_structure`),
and `degree` belongs to both. So a world that prefers the expanded writing scores higher
**by the construction of the vocabulary and not by any fact about mathematics**. The numbers confirm this
directly:

```text
Pearson r (number of monomial-sum writings  vs  manifest total)   +0.948
Pearson r (number of factored writings      vs  manifest total)   -0.831
```

That is, "`G0` exposes the most" **means** "`G0` most often chooses the expanded writing, and in this vocabulary
the expanded side has more properties written on it". A balanced 3:3 vocabulary would invert the ranking. In the opaque
regime, where a parenthesis hides, the same `G0` drops to 3rd (`60`), first is `G17` (`63`), second `G18` (`61`).

### 4. Is there a world that exposes all the properties of an object at once

**No.** This is the main question of the card and the answer is categorical.

```text
objects with >=2 true properties                                 25
of those, fully visible somewhere                                 0
objects that are "fully visible" somewhere                        7   -- each has exactly 1 property
largest simultaneous set anywhere in the grid                   5/7
```

Those seven "fully visible" objects are `product_rule`, `dot_product`, `determinant_2x2`,
`linear_combination`, `squared_norm`, `matrix_vector_component`, `cramer_numerator` — and the sole true
property of every one of them is `sign_structure`. So completeness here is in a vacuum.

A few characteristic cases (`D` degree, `L` leading coefficient, `C` constant term, `R` roots,
`F` factor structure, `S` sign structure, `P` even parity):

| object | true | max at once | in `G0` |
|---|---|---|---|
| `calibration_quadratic` | `DLCRFS` | `DLCS` (4/6) | `DLCS` |
| `quadratic` (`a*(x-r)*(x-s)`) | `DLCRFS` | `DRF` (3/6) | **nothing** |
| `difference_of_squares` | `DLCRFSP` | `DLCSP` (5/7) | `DLCSP` |
| `ellipse` | `DLCRFSP` | `DLCSP` (5/7) | `DLCSP` |
| `taylor_second_term` | `DLCRFS` | `DR` (2/6) | `DR` |
| `distance_components` | `DLCRS` | - (0/5) | **nothing** |

`quadratic` is especially clear: the general quadratic `a * x * x - a * (r + s) * x + a * r * s` **exposes
nothing in our convention** — the parenthesis `(r + s)` spoils the monomial-sum shape — while its factored
side, which is expensive in `G0`, wins in other worlds, and there the roots are on the surface.

### 5. The pair that no world exposes together

**`constant_term` and `roots`: 0 cells of 850, in both regimes.** (Here 850 is the right denominator — the pair is nowhere visible together, on any object, including the single-property ones.)

This is exactly the calibration trade and it is **a measurement and not a consequence of the rules**: nothing in the shape rules
forbids this pair — a writing of the `a * x` kind would satisfy both (it is a monomial sum with a zero constant
term and at the same time a product of linear factors). In writing these 34 objects under these 25
conventions, such a writing simply never wins.

The full list, split into two groups, because the distinction matters:

```text
mutually exclusive by measurement (the rules do not forbid it):
  leading_coefficient x roots                0 cells
  leading_coefficient x factor_structure     0
  constant_term       x roots                0      <-- headline
  constant_term       x factor_structure     0
  roots               x even_parity          0
  factor_structure    x even_parity          0

excluded by the rules (reading this as a discovery would be circular):
  roots            x sign_structure          roots requires a multiplicative top node,
  factor_structure x sign_structure          sign_structure an additive one; a tree has one root
```

For comparison, frequently co-occurring pairs: `degree x sign_structure` 244 cells,
`degree x leading_coefficient` 226, `degree x roots` 183, `roots x factor_structure` 76.

### The calibration case in full

```text
grammar   writing           rendering                    cost   manifest
G0        expanded          2 * x * x + 3 * x - 5          0     D L C S
G17       expanded          2 * x * x + 3 * x - 5          0     D L C S
G09       expanded          (2 * x * x + 3 * x) - 5        1     D L C S
G18       expanded          (2 * x * x + 3 * x) - 5        1     D L C S
G01       factored          (2 * x) + 5 * x - 1            1     D   R F
```

The `G01` row is the picture of the whole card. To our eye `(2 * x) + 5 * x - 1` looks like a sum; to a
native of `G01` it is a **product**, it is the cheapest writing of their quadratic, and in it the roots are written on the
paper. In our convention the cheapest writing of the same object puts the coefficients on the paper and hides
the roots.

## Interpretation

**1. The trade is real and it is determined by the identity of the properties, not by accident.** The two principal shapes -
a sum of monomials and a product of linear factors — are mutually exclusive at the root of the tree. Reading the
coefficients requires the surface of a sum, reading the roots requires the surface of a product. One object cannot be
both at once (except in a degenerate case, which does not occur in this corpus). Therefore **a convention that
makes one shape cheap removes the other from the field of view.**

**2. Our convention cannot see factorisation.** `G0` is among the five worlds in which no
object of this corpus is written most cheaply as a product of two compound factors. If we accept the hypothesis of the card,
that a mathematician notices what is visible, then this is a **prediction about what should have arrived more slowly
in our history**: Vieta-type results, the discriminant and symmetric functions are on the side of the coefficients
and in our notation they are visible for free; the structure of the roots is always one step further away. This is a
**hypothesis** and not a measurement — what is measured is only how visibility is distributed.

**3. The first place of `G0` in the ranking does not mean that our convention shows us more.** It means
that it more often chooses the shape on which this vocabulary has written more properties (`r = +0.948`).
Under the opaque rules the same `G0` becomes 3rd. The ranking is the weakest result here and the most
rule-dependent one — unlike the trade results, which are unchanged in both regimes.

**4. 0034 -> 0037 -> 0038 do not contradict one another.** `G0` was 11th by cost on mixed practical
formulas (0034), 3rd on named laws (0037), and joint-first by visibility on those same laws (0038).
All three say the same thing on different axes: **`G0` is the grammar that makes the expanded, monomial-sum
writing cheap** — and that single decision explains at once why it is cheap on laws and why it
exposes coefficients and hides factorisation.

## Limits

- **Manifestness is relative to the declared shape rules.** This is the central limitation
  of this experiment and it is in the first section, not here. A property that is invisible under these rules is **not**
  thereby invisible under all rules. The standing caveat of the ROADMAP about the scale of negative results applies
  more sharply here than anywhere else in the project.
- **The corpus is hand-picked.** It is the imported corpus of 0037 plus one calibration object; it
  reflects a judgement about which laws are fundamental and is not a sample from any population.
- **The principal variable is declared.** 13 objects have none at all (`None`), and for them the five
  variable-dependent properties are false rather than merely hidden. A different declaration would give different numbers.
- **Syntactic visibility is a model of what a reader notices, and not a claim about
  cognition.** Nothing here measures human attention, teaching order or historical discovery.
- **The vocabulary is not neutral between the shapes** (4 : 2 : 1). This bears directly on the ranking and is
  accounted for numerically above; it does not bear on the trade results, since those concern pairs and not totals.
- **Generation 1 has no exponentiation and no function call**, so squares are written as products
  (`x * x`) and several entries use stand-in leaves. This raises the share of `*` and therefore the frequency of the
  monomial-sum shape.
- **Associativity is fixed to left** for every operator, and there is no unary minus.
- **A cheaper or more "visible" convention is not an argument that mathematics should have adopted it.**

## Classification of evidence

- The calibration split (`17`/`8`), the manifest totals, the ranking, the per-property counts, the `46` hidden pairs,
  `0` fully visible objects of the 25, `0` cells for `constant_term` x `roots` — **OBSERVED**, on this
  corpus, on these 25 grammars, under these rules.
- Round trip (`1250/1250`), minimality (`1811` parentheses, `0` violations), surface mirror (`1250/1250`),
  `manifest => true` (`2573` claims, `0` violations) and the correctness of the values read off (`2156`
  checks, `0` mismatches) — **VERIFIED PROPERTIES** on this grid, not a proof over all trees.
- `roots x sign_structure` and `factor_structure x sign_structure` - **RULE CONSEQUENCE** and not a
  discovery; that is precisely why they are in a separate bucket.
- Stability across regimes (the trade survived, the counting did not) - **OBSERVED** robustness against one
  alternative, equally conservative set of rules; this is not a claim about all possible rules.
- "A convention that hides factorisation slowed its mathematicians down" - **HYPOTHESIS**. Only
  visibility was measured.
- The interpretation of the ranking through the asymmetry of the vocabulary - **OBSERVED** correlation (`r = +0.948`), which
  suggests causation and does not establish it.

## Validation

```text
python -m pytest -q tests/test_manifest_properties.py     34 passed
python -m pytest -q                                      688 passed
```

The headline numbers are **pinned literally** in the tests rather than recomputed from the module, so
a change in the result will fail a test and will not pass silently.

### Concurrency: sequential by measurement

```text
cells                                850   (34 objects x 25 grammars)
sequential                        0.2046 s  (min of 3)  ->  2.4e-4 s / cell
process pool startup (12 workers) 0.9733 s  (min of 3)  <- the workers import SymPy
parallel (12 workers)             1.0991 s
speedup                             0.23x   ->  sequential 4.4x faster
identical results                    True
```

`should_parallelise` does arithmetic on two **measured** numbers and not on the cell count; the same rule
returns `True` when the work is large enough (both directions are pinned in the tests). The worker count
is derived from the observed cores (`16 -> 12`, two cores in headroom) and not from a hardcoded constant.
**Pool startup required a separate measurement**: with a builtin task the same pool comes up in `0.24`
seconds, but with this module imported — in `0.97` seconds; the second is the one that matters.

### Mutation testing

On an isolated copy (tree copied into the scratchpad; canonical repository untouched; a preflight
checks that the tests import the **copy**), `20` mutants at the decisive points:

```text
left child rendered with the right bracket rule            KILLED
leaves are bracketed too                                   KILLED
opacity disabled: a bracket never hides anything           KILLED
constant term tolerates two variable-free summands         KILLED
leading coefficient drops the uniqueness clause            KILLED
roots accept a quadratic factor                            KILLED
degree loses its factored clause                           KILLED
factor structure accepts a single compound factor          KILLED
even parity needs only one even term                       KILLED
the world writes the object in its DEAREST form            KILLED
cost ties break to the last declared writing               KILLED
competition ranking becomes positional                     KILLED
the variable is allowed to sit under a division            KILLED
the additive chain is flattened through its right spine    KILLED
a read-off term forgets its sign                           KILLED
division does not flip the numerator/denominator flag      KILLED
the soundness sweep skips the opaque regime                KILLED
a factored reading no longer needs a multiplicative top    KILLED
a linear factor may carry two degree-one terms             KILLED
the null model keeps the objects that cannot move          KILLED

killed 20/20
```

On the first run four mutants survived — `variable under a division`, `flatten the right spine`,
`multiplicative top`, `two degree-one terms`. All four concerned a clause that **no object of the corpus
reaches**, although they are load-bearing for soundness. Four tests on synthetic writings were added
(`a / x + b * x`, `a - (b + c)`, `m * x + b`, `(a * x + b * x + c) * (x - 1)`) and all four mutants died.
Those writings are **probes and not corpus** — none of them takes part in any published number.
