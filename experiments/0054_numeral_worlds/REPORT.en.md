# ParseAtlas experiment 0054: the base a number is written in

## The question that started this, answered

The owner asked it first, a week before the vocabulary for it existed: compare computing `2**50` in decimal against computing it in binary. Here is the answer as a **multiplication count**, taken on the emitted graph with translation excluded.

```text
base  2    1125899906842624   51 digits,   1 nonzero    0 multiplications
base 10    1125899906842624   16 digits,  15 nonzero    7 multiplications
```

In base 2 the value has exactly one nonzero digit, so scaling by it is a shift and **no multiplication is issued at all** — the numeral *is* the answer, and writing it down is the whole computation. In base 10 it has no such structure, so the value has to be built, and the cheapest way to build it is an addition chain. Exhaustive iterative deepening puts the minimum at **7** multiplications, along `1, 2, 4, 8, 16, 32, 48, 50`; no chain of length `6` exists, and that was searched rather than quoted.

Swept over the bases `2` to `120`, the cost is `0` in exactly `6` of them — `2, 4, 8, 16, 32, 64`, the powers of two — and `7` in the remaining `113`. The curve is not a trend. It is a partition, and which side of it a number falls on is decided by the numeral world and by nothing else.

Module: `src/parseatlas/numeral_worlds.py`. Tests: `tests/test_numeral_worlds.py`.

## Purpose

There are three representation axes and this project had charted two.

```text
syntax        which tree a string becomes             the 25 worlds   0001-0053
expression    which equivalent writing is chosen      direction B     0034, 0037
NUMERAL       how the numbers themselves are written  this card       0054
```

**Which cost each figure is.** A shift count, an operation count and a multiplication count are costs of *computation*: taken on the emitted graph, with translation excluded. A bracket total and a numeral length are costs of *notation*: what a reader pays on every read. The two are never summed here, and every number below carries its label in the sentence that states it.

A numeral world is a **base**. It changes no tree and no grammar. It changes what a literal *is*, what an exact value is, and what a multiplication by a constant costs. Everything in this repository charges `+ - * /` as abstract operations on abstract numbers; a machine does not, and this card is the first to say by how much that matters.

## What was taken from where

Nothing in the constant corpus was invented for this card. Three existing sources supply it.

- `0034` — `parseatlas.notational_cost.CORPUS`, the `58` named formulas of the first direction B experiment.
- `0037` — `parseatlas.domain_worlds.CORPUS`, the `33` named laws in four fields, flattened to their `48` written sides.
- `0051` — `parseatlas.region_geodesy`, the WGS 84 defining constants and the declared rotation increment, the only place in the repository where a constant arrives from outside mathematics.

A literal on the right of `/` is recorded as its reciprocal, because dividing by `k` is scaling by `1/k` and it is `1/k` whose expansion a base either terminates or does not. That is the only transformation any literal undergoes here and it is disclosed rather than folded in.

## Corpus

```text
constant occurrences                49      0034: 26   0037: 19   0051: 4
distinct constants                  14
  inert stratum, the integers        8      1  2  3  4  9  12  100  6378137
  informative stratum                6      1/100  1/3  1/2  3/5  4/5  298257223563/1000000000
occurrences by stratum                      inert 27   informative 22
roles                                       divisor 19   multiplier 19   addend 5   dividend 4   defining 2
```

**The null model, stated before any rate.** An integer terminates in every base. It therefore ranks no base above any other and it is inert for the exactness question, while remaining perfectly real for the cost question, where a power of the base is a shift and a non-power is not. `27` of the `49` occurrences are inert. Every exactness rate below is computed **inside the informative stratum** for that reason.

**And the informative stratum has its own imbalance, which is reported rather than smoothed.** `1/2` alone accounts for `16` of the `22` informative occurrences. So the occurrence-weighted rate and the distinct-constant rate say different things about base 2, and both are published; quoting only the first would be reporting the shape of the corpus as a fact about the base.

## Observed results

### 1. Exactness is a property of the base, not of the number

`1/2` terminates in base 2 and base 10 and repeats in base 3; `1/3` repeats in 2 and 10 and terminates in 3; `1/10` terminates in 10 and repeats in 2. The predicate is the classical one — every prime of the reduced denominator must divide the base — and it is checked against hand-worked cases in bases `2`, `3`, `10` and `16`, in both directions.

| base | distinct exact | of | occurrence exact | of | what stays inexact |
|---|---|---|---|---|---|
| `2` | 1 | 6 | 16 | 22 | `1/100` `1/3` `3/5` `4/5` `298257223563/1000000000` |
| `3` | 1 | 6 | 2 | 22 | `1/100` `1/2` `3/5` `4/5` `298257223563/1000000000` |
| `6` | 2 | 6 | 18 | 22 | `1/100` `3/5` `4/5` `298257223563/1000000000` |
| `10` | 5 | 6 | 20 | 22 | `1/3` |
| `16` | 1 | 6 | 16 | 22 | `1/100` `1/3` `3/5` `4/5` `298257223563/1000000000` |
| `30` | 6 | 6 | 22 | 22 | nothing |
| `60` | 6 | 6 | 22 | 22 | nothing |

**The card's question A, answered: base 2 is worse than base 10 for the project's own constants**, `1` of `6` against `5` of `6` on distinct constants and `16` of `22` against `20` of `22` on occurrences. Base 10 misses exactly one constant, `1/3`, and base 2 misses five.

**And there is a base in which more of them are exact than in base 10: base `30`, where all `6` are.** This half of the answer needs no sweep at all and carries no bound. A base makes `p/q` exact exactly when every prime of `q` divides it, so a base makes *every* corpus constant exact exactly when it is a multiple of the radical of the least common multiple of the denominators. That least common multiple is `3000000000` and its radical is `30`, so the answer is **`30`, and the complete set of such bases is every multiple of `30`.** The sweep confirms it; it does not produce it.

**The WGS 84 defining constant decides this on its own.** The standard publishes the inverse flattening as `298.257223563`, that is `298257223563/1000000000`. It is exact in base 10 and in base 30, and inexact in base 2 and in base 16. Every binary machine on Earth therefore begins a geodetic computation with a rounded ellipsoid, before a single operation of experiment 0051 runs.

**The curve over the bases is not monotone, and the reason is exact.** Over the band `2` to `120` the exact count falls `43` times as the base rises by one — most vividly from `6` at base `30` to `0` at base `31`. More base does not buy more exactness; more *primes* does. The observation is that the count is a function of the radical alone, `count(b) == count(radical(b))`, and it holds in every one of the `119` bases swept.

**What lies beyond the band is enumerated, not left open.** Only the primes dividing some corpus denominator can matter, and that set is `{2, 3, 5}`. Two bases whose signature over that set agrees make exactly the same corpus constants exact, so there are exactly `8` behaviours in total and no base of any size can exhibit a ninth. The band already holds a representative of each.

| signature | smallest base | distinct exact | occurrence exact |
|---|---|---|---|
| none | `7` | 0 | 0 |
| `2` | `2` | 1 | 16 |
| `3` | `3` | 1 | 2 |
| `5` | `5` | 2 | 2 |
| `2 3` | `6` | 2 | 18 |
| `2 5` | `10` | 5 | 20 |
| `3 5` | `15` | 3 | 4 |
| `2 3 5` | `30` | 6 | 22 |

The band `2` to `120` is a **computational limit and never a finding**. The table above is what was checked beyond it, and the check is an enumeration rather than a longer sweep: bases as large as `2**20`, `10**7`, `3**15` and `7**9` were each confirmed to behave exactly as their class representative does.

### 2. The operation count is wrong in a way the base decides

The project charges `x * 2` and `x * 3` the same one multiplication. On a binary machine the first is a shift and the second is not. The classification is the three-way one the card asks for, plus the identity, which emits nothing at all.

```text
identity        the constant is 1                              0 operations
shift           the constant is a power of the base            1 shift
shift_and_add   every base digit is 0 or 1, t of them nonzero  t-1 shifts and t-1 additions
general         anything else                                  1 multiplication
```

Applied to the multiplicative and dividing constants of the corpus itself — the multipliers `2 3 4 12 100` and the divisors `2 3 100`:

| base | identity | shift | shift_and_add | general |
|---|---|---|---|---|
| `2` | 0 | 2 | 3 | 0 |
| `3` | 0 | 1 | 2 | 2 |
| `6` | 0 | 0 | 0 | 5 |
| `10` | 0 | 1 | 0 | 4 |
| `16` | 0 | 0 | 0 | 5 |
| `30` | 0 | 0 | 0 | 5 |
| `60` | 0 | 0 | 0 | 5 |

**Base 2 is the only base in the probe set with no general multiplication at all**, and it is also the base that was worst on exactness. The two halves of the numeral axis pull in opposite directions, and that tension is the central observation of this card rather than an inconvenience in it. Base 16 — the base a programmer actually writes constants in — makes none of them a shift, because the constants of the corpus are small and `16` is coarse.

Two hand-workable rows carry the whole effect:

```text
(a + b) / 2     blind 1 addition and 1 division        base  2   2 cheap operations, no division
p * x / 100     blind 1 multiplication and 1 division  base 10   1 shift, 1 multiplication, no division
```

Dividing by `100` costs a division on a binary machine and a shift on a decimal one; halving costs a shift on a binary machine and a division on a decimal one. Neither is visible to a cost model that only counts operators.

### 3. Which ranking moves, and which does not

Both answers are stated with the same weight, because the card asks for that and because they are the same observation seen from two sides.

**The ranking that does NOT move: the 25 syntax worlds by notational cost.** Direction B fixes the intended tree and lets only the brackets vary, so the multiset of numeric literals is identical in all 25 worlds, and a base-aware arithmetic price is therefore the same additive constant in every column. It cannot reorder them, and it does not.

```text
before, and after base-aware pricing at base 2 and at base 10, identically
G18  42     G16  44     G0  45 at rank 3, tied with G10     G10  45
```

This reproduces 0037 exactly and it is a **structural** result, not an accident of the corpus: a cost of notation and a cost of computation are separate orderings of the same objects, which is what the standing rule of the roadmap asserts and what this is the observation of. A router that reweights the 25 worlds for the base of the machine is reweighting nothing.

**The ranking that DOES move: the corpus by computation cost.** The `106` written forms of 0034 and 0037 give `5565` unordered pairs. Pricing a shift apart from a multiply reverses the strict order of many of them, and how many depends on the base. Division is priced at a fixed ratio to multiplication so that every cost stays affine in one parameter; the table is at ratio `2`, and the multiply price is not declared but **solved**.

| base | reversals against the blind cost of the project, at most | curve segments | reversals constant above | curve monotone |
|---|---|---|---|---|
| `2` | 515 | 13 | `6` | no |
| `3` | 117 | 11 | `6` | no |
| `4` | 19 | 3 | `3` | yes |
| `5` | 0 | 0 | never any | yes |
| `6` | 0 | 0 | never any | yes |
| `8` | 0 | 0 | never any | yes |
| `10` | 58 | 5 | `5` | yes |
| `12` | 19 | 3 | `3` | yes |
| `16` | 0 | 0 | never any | yes |
| `30` | 0 | 0 | never any | yes |
| `60` | 0 | 0 | never any | yes |

**Read the zeros first.** For bases `5`, `6`, `8`, `16`, `30` and `60` the base-aware cost is *identical* to the base-blind cost of the project on this corpus, because no constant of the corpus is a power of any of them **and** none of them writes a corpus constant with all-`0`-or-`1` digits. Both halves are needed, and the second is not decoration: base `11` satisfies the first — no corpus constant is a power of `11` — and still reverses `19` pairs, because `12` is `(1, 1)` in base `11` and is therefore a shift-and-add. The existing operation count of the project is therefore exactly right for six of the eleven bases and wrong for the one every machine uses, where it misprices `515` of `5565` pairs. That is the shape of the error: not a uniform bias but a base-specific one.

**For bases `4` and `12` the curve does not start at `1`.** Below multiply price `3/2` those two agree with the blind model on every pair; the first reversal appears exactly there, which the solved crossing set locates without a sweep.

**No threshold was declared for the multiply price.** The cost of each entry is affine in it, so two entries swap at most once, at a price solved exactly in rationals. Collecting those solutions over all `5565` pairs gives the complete set of prices at which anything changes anywhere on the ray from `1` upward, and above the largest of them the ranking is constant for ever. For base 2 that largest crossing is `6`, and there are `13` crossings in all: `1, 6/5, 5/4, 4/3, 3/2, 5/3, 2, 5/2, 3, 7/2, 4, 5, 6`.

**And the curve turns.** The count of reversals is not monotone in the multiply price:

```text
price in (1, 6/5)      314        price in (2, 5/2)      406
price in (6/5, 5/4)    316        price in (5/2, 3)      413
price in (5/4, 4/3)    315   down price in (3, 7/2)      460
price in (4/3, 3/2)    308   down price in (7/2, 4)      461
price in (3/2, 5/3)    328        price in (4, 5)        495
price in (5/3, 2)      330        price in (5, 6)        510
                                  price above 6          515
```

Between the multiply prices `6/5` and `3/2` a **dearer** multiplication makes the base-aware ranking agree with the base-blind one on `8` more pairs, from `316` down to `308`, before the trend resumes. That is the turning point the roadmap asks every card to look for, and no threshold chosen in advance would have found it.

**The sensitivity to the divide ratio is on the page.** At ratio `1` the maximum for base 2 is `210` and for base 10 it is `16`; at ratio `2` they are `515` and `58`; at ratio `4` they are `710` and `67`. The direction of every statement above is the same at all three ratios and only the magnitude moves.

**The two numeral worlds disagree with each other more than either disagrees with the blind model.** Base 2 against base 10, at multiply price `3` and ratio `2`, reverses `462` pairs, and its curve reaches `569`.

**One concrete change, both ways.** At multiply price `3` with ratio `2`, the blind cost of the project puts `ohm_series_resistance`, that is `r1 + r2 + r3`, alone at the front of the corpus at cost `2`. Under base 2 the front is shared by `5` objects at the same cost `2`: `mean_of_two`, `midpoint.mean`, `midpoint_coordinate`, `ohm_series_resistance` and `rectangle_perimeter`. `(a + b) / 2` costs `7` under the blind model and `2` on a binary machine, and that single reclassification is the card in one line.

**Orientation: which side of a law is cheaper to compute.** Of the `15` two-sided laws, exactly **one** has its cheaper side decided by the base — `perfect_square_trinomial`.

```text
(2 * x + 3) * (2 * x + 3)   against   4 * x * x + 12 * x + 9

base  2   factored is cheaper at every price               4 + M   against   5 + M
base  3   factored below multiply price 2, expanded above  2 + 3M  against   6 + M
base 10   the two sides tie at every price                 2 + 3M  against   2 + 3M
base 16   the two sides tie at every price                 2 + 3M  against   2 + 3M
```

Fourteen of fifteen laws keep their orientation in every base. The one that does not, changes it twice: once with the base, and once within base 3 with the multiply price, at the crossing `2`.

### 4. Where the numerical-equivalence line bites

`0.1 + 0.2 != 0.3` in binary64 while the same statement is true over exact rationals. The disagreement is **not algebra**: `1/10` has no finite binary expansion, so the literal is already a different number before an operation runs.

```text
exact      1/10 + 2/10 == 3/10                                    True
binary64   0.1 + 0.2 == 0.3                                       False
           0.1 + 0.2 = 0.30000000000000004, gap 5.551115123125783e-17
```

The same `15` two-sided laws are evaluated in exact rationals and in binary64 at `120` points each, over two strata of inputs. The **dyadic** stratum is `2, -1, 3, 1/2, 5, 1/4, -2, 7` — every value a binary64 number exactly. The **decimal** stratum is `1/10, 3/10, 7/10, 9/10, 3/5, 4/5, 11/10, 13/10` — every value exact in base 10 and rounded in base 2, where `3/5` and `4/5` are the declared rotation increment of 0051 itself. Assignment is mechanical: names sorted, values rotated through every offset.

| stratum | checked | undefined | algebra failures | disagreements | laws affected | worst relative gap |
|---|---|---|---|---|---|---|
| dyadic | 120 | 0 | 0 | 2 | 2 | 1.7377403863698103e-16 |
| decimal | 120 | 0 | 0 | 65 | 14 | 7.062802723619858e-15 |

**Same pairs, same algebra, and a factor of more than thirty between them.** The disagreement is a property of the base of the inputs and not of the writing, which is exactly what section 1 predicts and what a cost model that never looks at literals cannot see. The worst relative gap is `7.062802723619858e-15`, on `quadratic` at a point where every input is a tenth.

**The negative control.** Restricted to the division-free laws on the dyadic stratum, every literal and every intermediate is a binary64 number exactly, so no rounding can occur and the counter must return zero. It does: `0` disagreements in `96` checks. The same `96` checks on the decimal stratum return `52`. A predicate only ever asked in the direction of its expected answer is not evidence, and this counter is asked in both.

**Which writing is the accurate one.** Accuracy is against the exact rational, which is the authority. Of the `16` law-and-stratum cells that disagree at all, `8` are decided — one writing is nearer the exact value at every point where the two differ — and `8` are split.

| law | stratum | accurate writing | wins |
|---|---|---|---|
| `difference_of_cubes` | decimal | `factored` | 6 of 6 |
| `binomial_square` | decimal | `expanded` | 5 of 5 |
| `line` | decimal | `point_slope` | 3 of 3 |
| `sum_of_cubes` | decimal | `expanded` | 2 of 2 |
| `parabola` | decimal | `vertex` | 1 of 1 |
| `trapezoid_area` | decimal | `sum_of_halves` | 1 of 1 |
| `difference_quotient` | dyadic | `closed` | 1 of 1 |
| `quotient_rule` | dyadic | `closed` | 1 of 1 |

**No side always wins**, and the split cells say so plainly: `quadratic` favours `factored` `7` times to `1`, `binomial_cube` favours `expanded` `4` times to `3`, `circle` favours `center_radius` `5` times to `2`, and `quotient_rule` on the decimal stratum favours `split` `4` times to `1`. The sentence "factored is more accurate" is false as a rule and true as a fact about `difference_of_cubes`. The rankings of the project by brackets, by depth and by peak memory are all silent about which of these is right, and so is the cost ranking of this card.

### 5. A seam at the numeral level, and how it compares with the seam of 0042

Montgomery form makes modular multiplication cheap and pays for it at conversion, which is the shape experiment 0042 observed for notation one level up. Modelled as operation counts in full-width multiplications, with the reduction price `r` swept rather than declared:

```text
classical modular multiplication    1 multiplication and 1 division-based reduction   =  1 + r
Montgomery modular multiplication   2 multiplications, and no division at all         =  2
conversion in                       1 Montgomery multiplication per operand           =  2 each
conversion out                      1 reduction step                                  =  1
```

So the saving is `r - 1` per operation and the toll is `2` per operand entering plus `1` leaving, that is `5` for a binary operation. The crossover is the ratio of the two.

| reduction price | saving per operation | crossover in operations per crossing | first integer chain that pays | asymptotic ratio |
|---|---|---|---|---|
| `1` | 0 | none | never | 1 |
| `2` | 1 | `5` | 6 | 3/2 |
| `3` | 2 | `5/2` | 3 | 2 |
| `4` | 3 | `5/3` | 2 | 5/2 |
| `6` | 5 | `1` | 2 | 7/2 |
| `8` | 7 | `5/7` | 1 | 9/2 |
| `12` | 11 | `5/11` | 1 | 13/2 |
| `16` | 15 | `1/3` | 1 | 17/2 |
| `24` | 23 | `5/23` | 1 | 25/2 |
| `32` | 31 | `5/31` | 1 | 33/2 |

**Where the claim stops is stated with it.** At a reduction price of `1` — a division costing no more than a multiplication — the saving is `0` and there is no crossover at any chain length whatever. The whole motive for Montgomery form is the price of division, and the model says so instead of assuming it. At a price of `8` the form pays even at a single modular multiplication per crossing.

The word-level instantiation changes the units and not the crossover: with `k`-word operands the toll is `5` times `k**2` word multiplications, which at `k` of `64` is `20480`, and the crossover is a ratio that does not know how wide the modulus is.

**Now the comparison the card asks for, and it is the part worth more than either number.** All three seams this project has priced fit one model:

```text
gain(n) = n * saving - toll          crossover at   n* = toll / saving
```

| seam | saving per operation | toll per crossing | crossover | operations per crossing available |
|---|---|---|---|---|
| Montgomery form, reduction price `6` | 5 | 5 | `1` | free |
| Cartesian to polar, the corrected figure of the roadmap | 3 | 4 | `4/3` | free |
| 0042 Model II, named intermediates | `11/29` | 1 | `29/11` | `1`, pinned by the splitting rule |

**The two seams do not behave the same way, and the algebra is not the reason — it is identical.** In Montgomery form and in the polar conversion, the operations per crossing are a free parameter of the program: raise the chain and the toll amortises, which is exactly the correction of the roadmap that the deciding quantity is operations per boundary crossing rather than chain length. In 0042 Model II that parameter is **pinned at `1` by the splitting rule**: every fragment is crossed exactly once and delivers exactly its own interior brackets, so the architecture cannot walk up the curve however long the document grows. Its break-even reproduces from its own published figures as `11/29`, that is `0.3793103448275862` of a bracket pair per naming unit, and the crossover it would need is `29/11` fragments' worth of prize per crossing.

So the verdict of 0042 was never a number that a bigger corpus could have moved. **A seam is payable when the prize scales with something the program controls and the toll does not.** For Montgomery form it does; for fragment routing it does not.

## Multicore observation and the default path

Repository policy is multicore by default and it also allows a sequential path where an observation justifies it. This module has three workloads whose per-cell profiles span more than four orders of magnitude, so the decision is taken three times from figures observed here rather than carried over. Recorded run: `16` cores, `12` workers, `2` cores kept free, pool startup observed at `1.0994` s and at `1.3273` s and declared at `1.3` s.

| workload | cells | seconds per cell | sequential | parallel | speedup | default | records identical |
|---|---|---|---|---|---|---|---|
| exactness sweep | 119 | 6.4e-06 | 0.0025 s | 1.3913 s | 0.0018 | sequential | yes |
| ranking sweep | 33 | 0.102 | 3.9108 s | 2.4326 s | 1.6077 | parallel | yes |
| disagreement sweep | 30 | 2.04e-04 | 0.0053 s | 1.4260 s | 0.0037 | sequential | yes |

A cell count cannot decide this, and assuming it can is how a sweep ends up slower in parallel than in sequence: the exactness sweep has nearly four times as many cells as the ranking sweep and a tiny fraction of the work per cell. The two sequential defaults are an outcome of the observation and not an omission, and the ranking sweep is genuinely parallel by default. All three produce identical records on both paths, and the test suite asserts that rather than assuming it.

## Interpretation

**The numeral axis is real and it is not a refinement of the other two.** It leaves the 25-world ranking untouched — provably, not accidentally — and it reorders the corpus by computation cost in a way that depends on which base the machine uses. Those are two different orderings of the same objects and this card is where the project first holds both.

**The operation count of the project has a base baked into it, and it is not base 2.** Charging every `*` one multiplication and every `/` one division is exactly right for the bases `5`, `6`, `8`, `16`, `30` and `60` on this corpus and misprices `515` of `5565` pairs for base 2. Nothing was wrong with the count as notation; it was quoted as computation.

**Exactness and cheapness point in opposite directions.** Base 2 is the worst numeral world in the probe set for representing the constants of this project and the best for multiplying by them. Base 30 represents all of them exactly and makes none of them a shift. A recommendation that optimises one is choosing against the other, and no single number expresses that trade.

**The equivalence line has a location.** Algebraic equivalence and numerical equivalence come apart at the literal and not at the operation. On inputs a binary machine holds exactly, `15` algebraically identical pairs disagree `2` times in `120`; on inputs it rounds, the same pairs disagree `65` times. The third standard of the roadmap is therefore not a tolerance to be chosen — it is a question about which numeral world the inputs came from.

## Limits

- **The base set is declared.** The sweep band is `2` to `120` and it is a computational limit, never a finding. What lies beyond it is enumerated rather than assumed: the exactness answer for a base of any size is fixed by which of `{2, 3, 5}` divide it, there are `8` such classes, the band holds a representative of each, and bases as large as `7**9` were confirmed against their representative. **The ranking half is enumerable in the same way, and is enumerated here rather than left declared.** The base enters the ranking only through the classification of the five cost-bearing constants `2`, `3`, `4`, `12` and `100`, so the profiles are finite: over the bases `2` to `1000` there are exactly `14`, and every base above `100` falls into the all-general profile that reverses nothing. The `11` swept bases cover `9` of the `14`. Each of the `5` uncovered profiles was run against a representative: base `7` reverses `0` pairs, base `11` reverses `19`, base `20` reverses `0` and stands for `903` of the bases in the band, base `99` reverses `9`, and base `100` reverses `58`. No unswept base beats base `2`'s `515`, and no statement above moves.
- **The constant corpus is taken from existing corpora and inherits their hand-chosen nature.** `49` occurrences and `14` distinct values is a small corpus, its informative stratum holds `6` values, and `1/2` is `16` of the `22` informative occurrences. Every rate here is a rate over that corpus and over no other. A different named-law corpus would move every figure in section 1, while the shape of the answer — that the base decides exactness and that the decision is by the radical — would not move, because it is arithmetic.
- **The two source corpora overlap, and the overlap is disclosed rather than deduplicated.** The `106` written forms hold only `90` distinct intended trees: `16` objects appear once under a 0034 name and once under a 0037 name. A duplicated pair is identical in every cost model, so it is never a strict order and can never be counted as a reversal; it only enlarges the `5565` denominator. Every reversal count here is therefore a count over pairs and a conservative rate over that denominator.
- **The binary64 side is the one of this machine and the exact-rational side is the authority.** Every float figure was produced by the IEEE 754 double arithmetic of this machine under CPython on Windows. The exact rationals are exact everywhere; the doubles are not a portable claim, and a platform with extended intermediate precision or a fused multiply-add would give different disagreement counts. The `120` sample points per stratum are a declared mechanical assignment and not a random sample, so the counts are counts and not estimates.
- **The Montgomery figure is a model and not an implementation that was run.** No modular arithmetic was executed. The operation counts are the textbook ones, the reduction price is swept because it is the modelling choice that decides the answer, and the word-level row is an instantiation of the same model rather than a second source of evidence. The comparison with 0042 uses the published figures of 0042, quoted and not recomputed.
- **The shift-and-add model prices only what a compiler actually does.** Multiplying by a constant whose base digits are all `0` or `1` is charged `t-1` shifts and `t-1` additions; dividing by a non-power of the base is charged a full division, with no cheap analogue, because there is none. A constant with a digit above `1` is charged a general multiplication even where a machine could use a digit table, which is the one place the model could be accused of flattering base 2, and it is disclosed rather than tuned.
- **A negative result carries the scope of what was searched.** That the 25-world ranking does not move is a statement about base-aware *arithmetic* pricing over a fixed intended tree. That six of eleven bases show `0` reversals is a statement about the constants of this corpus, which are small. Neither rules out a numeral effect in a representation this card did not construct.
- **The domain component of the semantic key is inert**, recorded as `NF-2026-00005`. This card does not use the semantic key — pair equivalence is established by exact rational arithmetic at every sample point, which is stronger for this purpose — but the corpora it imports were built under a key whose domain component does not currently discriminate, and that is inherited.

## Evidence classification

- **OBSERVED** — every number in this report, produced by a recorded execution of `parseatlas.numeral_worlds` on this machine.
- **OBSERVED and bound-free** — the minimal exact base `30`, the complete set of exact bases as the multiples of `30`, the `8` signature classes, the complete crossing sets of the ranking sweep, and the shortest addition chain of length `7`. Each is solved rather than sampled and none depends on where a sweep stopped.
- **MODEL** — the Montgomery operation counts and the three-row seam comparison. A model whose parameter is swept, not an implementation that was run.
- **INHERITED** — the 25-world totals of 0037, that is `G18` at `42` and `G0` at `45` in rank `3`; the Model II figures of 0042; and the WGS 84 defining constants. Recomputed where the module could, quoted where it could not.

## Validation

```text
python -m pytest tests/test_numeral_worlds.py -q          89 passed
```

The test file pins the termination predicate against hand-worked cases in bases `2`, `3`, `10` and `16` with `9` of the `22` cases expecting a negative answer; the calibration case in both arithmetics; the shift classification for powers, for shift-and-add constants and for neither; the ranking that changes, both before and after; the ranking that does not change, with its published values; the null-model stratification; the negative controls in both directions; and the agreement of the sequential and parallel paths on all three workloads.

**Mutation observation, on an isolated copy of the tree and never on the working tree.** Ten targeted mutations were applied one at a time to a scratch copy of `src` and `tests`, and the test file of this card was run against it: a termination predicate that always says yes, a classifier that calls every constant shift-and-add, a cheap division by a non-power, free additions, a seam that crosses over with no saving, a binary64 evaluator that is secretly exact, a shift-and-add priced as one operation, an addition-chain search that starts one level too deep, a reversal curve that keeps only its last segment, and an exactness sweep that drops the stratification. **`10` of `10` were killed.**
