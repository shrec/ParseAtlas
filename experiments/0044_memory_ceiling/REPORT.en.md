# ParseAtlas experiment 0044: the ceiling, and the criteria that fight each other

## The answer to the owner's question, first

The owner set the premise: *a task might need 2 TB and we technologically have 1.8; if another representation
brings the computation within 1.8, the task becomes computable.* Asked strictly of the 25 worlds, the answer on
this corpus is **no, and it cannot be yes**:

> **Over `37` objects and `3` ceilings — `111` object/ceiling cells, `2775` world cells — there is no object and
> no ceiling at which `G0` is infeasible while another world is feasible. Feasibility under a peak-memory ceiling
> is world-INVARIANT in Generation 1 **by construction**, not by measurement.**

The reason is structural and it is worth stating plainly, because it bounds what this project can ever claim
about the owner's scenario. Every world can write every tree: `render` inserts a bracket wherever the grammar
would otherwise re-associate, and the round trip is verified on every one of the `28575` grid cells. So the set of
writings that fit under a ceiling is the same set in all 25 worlds, and a convention cannot make a computation
possible that another convention makes impossible. **A precedence convention is not a representation change of
the kind the owner's scenario needs.**

What a convention *does* change is the **price of staying under the ceiling**, and there the scenario reappears
in the currency this project can measure:

> **At ceiling `3`, `G0` must pay one extra bracket pair to write the ellipse and the hyperbola, while `16` of the
> other worlds get the frugal writing for free. At the same ceiling `3` the circle reverses it: `G0` pays `0` and
> `20` worlds pay, the maximum of `6` extra bracket pairs falling on `G01`, `G02`, `G05` and `G19`. The step exists; it is a step in cost, not
> a step in possibility.**

## Purpose

Every published ranking in this repository is a **cost** ranking: continuous, total, and mute about whether a
thing can be done at all. Against a hard ceiling cost stops being continuous and becomes a step — a ten percent
reduction is worthless at 5 TB and decisive at 1.99 TB. That is ROADMAP thesis T31, *reachability outranks cost*,
restated in the currency of memory, and this experiment is the first in the series to measure a **threshold**
rather than a total.

## The trap, and why the question had to be posed one level up

Peak memory is a property of a **tree**. For one fixed tree it is the same in every world, because the round trip
guarantees that every world re-parses its own rendering back to that same tree. This is checked, not assumed:
`peak_live_invariance` re-renders and re-parses every counted writing in every world and finds `0` failures over
`28575` cells. So "does the convention change the peak memory of a computation" is **not** a question about one
tree, and an experiment reporting it as one would be measuring nothing.

The real question is one level up:

```text
an object has many equivalent writings          -> they have DIFFERENT peak memory
every world can write all of them               -> feasibility is the same everywhere
what differs is what each COSTS IN BRACKETS     -> the ceiling has a per-world PRICE
```

## What is measured, and what `peak_live` is not

`peak_live` counts **values, not bytes**. It is the Sethi-Ullman register number — Ravi Sethi and Jeffrey D.
Ullman, *The Generation of Optimal Code for Arithmetic Expressions*, JACM 17(4), 1970 — and it is cited here as
the classical result it is, not as anything this project invented. The rule: a leaf needs `1`; for a node, if the
two subtrees need different amounts the answer is the larger, and if they need the same it is that plus one,
because the heavier side is evaluated first and the other side's single carried value never peaks against it.

Mapping `peak_live` to the owner's terabytes assumes the live values are of comparable size. **It is a structural
bound, not a memory benchmark.** No wall-clock and no byte count is measured anywhere in this experiment.

`depth(tree)` is the critical path: `1 + max` over the children, a leaf at `0`, so the number counts operator
levels. Experiment 0021's `depth` gives a leaf `1` and therefore reports exactly one more; the offset is pinned in
a test so the two are never compared naively. Card 0041 also computes a critical path; the duplication here is
deliberate, because 0041 is running concurrently and is not accepted, and importing it would make these numbers
depend on unreviewed code.

## Corpus

Experiment 0038's corpus imported whole — 0037's `33` named laws plus the calibration quadratic, so `34` objects —
plus associative chains of `4`, `6` and `8` terms over a single repeated `+`, which is where the depth/memory
trade is sharpest. `37` objects, `53` declared writings, sources canonical under `G0` and names unique:

```text
objects                                                37
declared writings                                      53
    algebra                                            18
    geometry                                           15
    calculus                                           11
    linear algebra                                      6
    associative chain                                   3
```

## The writing space, and the filter that keeps it honest

A **writing** of an object is a tree that denotes it. The space is every parenthesization of every declared token
word, filtered to the trees that still denote the object — 0039's discipline, because a different
parenthesization is usually a different object and a frugal tree for something else buys nothing.

```text
trees enumerated (Catalan over 53 words)          1511296
discarded by the exact rational probe             1510153
probe survivors                                      1143
rejected by SymPy                                       0
confirmed writings                                   1143
```

The probe is exact rational arithmetic at two declared points (seed `39`, fixed before any result was seen) and
can only ever rule a tree **out**. Every survivor is then confirmed by SymPy. On this corpus SymPy rejects `0` of
the `1143`, and that is pinned as a corpus fact rather than taken as licence to drop the confirmation.

## The correctness bridge

Nothing below means anything without this, so it is run first and over the whole grid of `1143` writings times
`25` worlds:

```text
round trip     28575 checks     0 failures
minimality    122571 brackets   0 violations
peak invariance 28575 checks    0 failures
object identity    53 checks    0 failures
```

Minimality is what makes a bracket count a **cost** rather than an upper bound: every bracket the renderer emits
is deleted in turn and must change the tree or break the parse.

## The null model, which is the main risk

Precedence cannot distinguish groupings of a single repeated operator. Re-derived here rather than assumed:

| terms | flat writing | depth | peak | brackets | balanced writing | depth | peak | brackets | bracket-free worlds |
|---|---|---|---|---|---|---|---|---|---|
| 4 | `a + b + c + d` | 3 | 2 | 0 | `a + b + (c + d)` | 2 | 3 | 1 | 0 |
| 6 | `a + b + c + d + e + f` | 5 | 2 | 0 | `a + (b + c) + (d + (e + f))` | 3 | 3 | 3 | 0 |
| 8 | `a + b + c + d + e + f + g + h` | 7 | 2 | 0 | `a + b + (c + d) + (e + f + (g + h))` | 3 | 4 | 3 | 0 |

The manager's hand measurement is confirmed on its own terms: an eight-term sum is depth `7` / memory `2` as a
chain and depth `3` / memory `4` balanced. **Halving the critical path doubles the memory.** And the bracket
column is the same integer in every world — the flat chain is free in all `25`, the balanced form costs `3` in
all `25`, and `0` of the `25` write it bracket-free. The chains are where the trade is visible and where the
convention **cannot act**.

So the corpus is split, and every ranking below is computed over the movable set only. A frozen entry adds the
same constant to all 25 totals and therefore cannot move any order; that is the precise sense in which it is
inert, and it is asserted in a test:

| class | count | entries |
|---|---|---|
| `tree_frozen` — every tree costs the same in all 25 worlds | 4 | `chain_rule` `chain_4` `chain_6` `chain_8` |
| `choice_frozen` — worlds differ per tree, but the cheapest cost coincides | 3 | `binomial_square` `binomial_cube` `triangle_area` |
| `movable` — two worlds differ in cheapest feasible cost | 30 | the remaining named laws |

## The Pareto frontier: where the two criteria fight

Over all same-object writings, the frontier of `(depth, peak_live)`. A frontier with more than one point is a
conflict: no writing is simultaneously shortest on the critical path and cheapest in live values.

| object | writings | Pareto points | dominated points | movable |
|---|---|---|---|---|
| `circle` | 37 | `(3, 4)` `(7, 3)` | `(5, 4)` `(6, 4)` | yes |
| `ellipse` | 4 | `(3, 4)` `(4, 3)` | none | yes |
| `hyperbola` | 4 | `(3, 4)` `(4, 3)` | none | yes |
| `chain_4` | 5 | `(2, 3)` `(3, 2)` | none | no |
| `chain_6` | 42 | `(3, 3)` `(5, 2)` | `(4, 3)` | no |
| `chain_8` | 429 | `(3, 4)` `(4, 3)` `(7, 2)` | `(5, 3)` `(6, 3)` | no |

Six of the `37` objects conflict and `31` do not. Three of the six are movable — the circle, the ellipse and the
hyperbola, all conic sections, all objects whose expanded and factored forms genuinely differ in how much has to
be held at once — and three are the chains, where the trade is real but the convention is powerless. Across the
whole space, `226` of the `1143` writings are Pareto-optimal and `917` are dominated; `18` objects have more than
one Pareto-optimal *writing*, while only `6` have more than one Pareto-optimal *point*.

## The ceiling sweep

`peak_live` on this corpus runs from `2` to `4`, so the useful range of the ceiling is exactly `2`, `3`, `4`, and
at `4` the constraint is inactive.

| ceiling | objects any world can write | worlds that can do the whole corpus | movable objects in the ranking | infeasible |
|---|---|---|---|---|
| 4 | 37 / 37 | 25 | 30 | none |
| 3 | 36 / 37 | 0 | 29 | `distance_components` |
| 2 | 13 / 37 | 0 | 8 | 24 objects |

The world count is `25` or `0` and never anything between. That is **the implementation showing up as a table,
not evidence**: the column is computed from `peak_live <= ceiling`, which never mentions a world, so it could not
have taken any other value. It is printed because the shape is worth seeing, not because it was in doubt.

The per-world totals. The first three columns are each computed over their own basis and are **not comparable
across columns**; the last four are the fixed-basis comparisons and are the ones the ranking claim rests on:

| world | C=4 (30) | C=3 (29) | C=2 (8) | 29 @ 4 | 29 @ 3 | 8 @ 3 | 8 @ 2 |
|---|---|---|---|---|---|---|---|
| `G16` | 12 | 10 | 8 | 8 | 10 | 3 | 8 |
| `G18` | 12 | 11 | 9 | 8 | 11 | 3 | 9 |
| `G15` | 14 | 11 | 6 | 10 | 11 | 3 | 6 |
| `G10` | 12 | 18 | 4 | 12 | 18 | 1 | 4 |
| `G0` | 17 | 15 | 8 | 13 | 15 | 3 | 8 |
| `G17` | 17 | 15 | 9 | 13 | 15 | 4 | 9 |
| `G24` | 17 | 14 | 8 | 13 | 14 | 3 | 8 |
| `G09` | 14 | 19 | 2 | 14 | 19 | 1 | 2 |
| `G13` | 19 | 15 | 6 | 15 | 15 | 4 | 6 |
| `G14` | 19 | 16 | 7 | 15 | 16 | 4 | 7 |
| `G12` | 17 | 21 | 3 | 17 | 21 | 1 | 3 |
| `G23` | 22 | 18 | 8 | 18 | 18 | 4 | 8 |
| `G22` | 20 | 24 | 5 | 20 | 24 | 2 | 5 |
| `G01` | 38 | 44 | 3 | 36 | 44 | 3 | 3 |
| `G07` | 38 | 43 | 3 | 36 | 43 | 3 | 3 |
| `G03` | 45 | 41 | 7 | 39 | 41 | 6 | 7 |
| `G04` | 45 | 42 | 8 | 39 | 42 | 6 | 8 |
| `G02` | 42 | 46 | 2 | 40 | 46 | 2 | 2 |
| `G08` | 42 | 45 | 2 | 40 | 45 | 2 | 2 |
| `G11` | 44 | 47 | 4 | 42 | 47 | 4 | 4 |
| `G05` | 45 | 49 | 4 | 43 | 49 | 3 | 4 |
| `G06` | 49 | 44 | 7 | 43 | 44 | 5 | 7 |
| `G19` | 47 | 51 | 6 | 45 | 51 | 5 | 6 |
| `G20` | 51 | 46 | 9 | 45 | 46 | 7 | 9 |
| `G21` | 47 | 50 | 6 | 45 | 50 | 5 | 6 |

**The ranking changes, and it first changes at ceiling `3`.** A ranking has to break ties somehow and this one
breaks them by grammar id, which is a presentation choice from which nothing may be concluded; so the claim is
checked against the **tier** structure, where ties stay ties. Both shifts change tiers, `0` of them are
tie-break-only.

```text
basis 29, ceiling 4      basis 29, ceiling 3
  8  G16 G18              10  G16
 10  G15                  11  G15 G18
 12  G10                  14  G24
 13  G0 G17 G24           15  G0 G13 G17
 14  G09                  16  G14
 15  G13 G14              18  G10 G23
 17  G12                  19  G09
 18  G23                  21  G12
 20  G22                  24  G22
 36  G01 G07              41  G03
 39  G03 G04              42  G04
 40  G02 G08              43  G07
 42  G11                  44  G01 G06
 43  G05 G06              45  G08
 45  G19 G20 G21          46  G02 G20
                          47  G11
                          49  G05
                          50  G21
                          51  G19
```

Tightening from `4` to `3` breaks the joint lead: `G16` and `G18` share first place at `8` with no ceiling, and at
ceiling `3` `G16` holds it alone at `10` while `G18` slips to `11`. The sharper move is `G10`, which pays `6` — it
falls from third tier at `12` to sixth tier at `18` — while `G0` pays only `2` and stays in the fourth tier, in a
three-way tie with `G17` and `G24`. **The cheap
world under no constraint is not the cheap world under a tight one.**

Tightening from `3` to `2` breaks it much harder, on the `8` objects that survive the tighter ceiling:

```text
basis 8, ceiling 3                              basis 8, ceiling 2
  1  G09 G10 G12                                  2  G02 G08 G09
  2  G02 G08 G22                                  3  G01 G07 G12
  3  G0 G01 G05 G07 G15 G16 G18 G24               4  G05 G10 G11
  4  G11 G13 G14 G17 G23                          5  G22
  5  G06 G19 G21                                  6  G13 G15 G19 G21
  6  G03 G04                                      7  G03 G06 G14
  7  G20                                          8  G0 G04 G16 G23 G24
                                                  9  G17 G18 G20
```

`G0` falls from the third tier of seven to the eighth of nine, its total rising from `3` to `8`; `G18` pays the
most, `6`. Tiers rather than ordinals, because the ordinals here come from an alphabetical tie-break this report
disclaims two paragraphs above. The numbers are small
because the basis is `8` objects, and that is stated rather than hidden — but the direction is unambiguous and it
is exactly T31: **a world's rank is a function of the constraint, not a property of the world.**

## The owner's scenario in the currency that can be measured

For every object and ceiling, the **premium** is how many extra bracket pairs the ceiling costs a world compared
with the writing it would have chosen with no ceiling at all. Eight cells carry a premium anywhere:

| object | ceiling | `G0` premium | worst premium | worlds paying nothing | worlds paying |
|---|---|---|---|---|---|
| `distributive_law` | 2 | 1 | 1 | 12 | 13 |
| `line` | 2 | 1 | 1 | 12 | 13 |
| `difference_quotient` | 2 | 1 | 1 | 12 | 13 |
| `trapezoid_area` | 2 | 1 | 2 | 16 | 9 |
| `linear_approximation` | 2 | 1 | 1 | 20 | 5 |
| `circle` | 3 | 0 | 6 | 5 | 20 |
| `ellipse` | 3 | 1 | 1 | 16 | 9 |
| `hyperbola` | 3 | 1 | 1 | 16 | 9 |

In `7` of the `8`, `G0` pays while some other world does not. In `1` — the circle — the reverse holds. Two cases
in full, because the mechanism is the whole point:

```text
ellipse, G0, no ceiling   x * x / (a * a) + y * y / (b * b)       depth 3  peak 4  brackets 2
ellipse, G0, ceiling 3    x * (x / (a * a)) + y * y / (b * b)     depth 4  peak 3  brackets 3

circle, G0,  ceiling 3    x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k
                                                                  depth 7  peak 3  brackets 0
circle, G01, ceiling 3    (((x * x) - (2 * h * x)) + (h * h) + (y * y) - (2 * k * y)) + (k * k)
                                                                  depth 7  peak 3  brackets 8
```

The ellipse under a ceiling of `3` has to be re-associated so that the two halves are no longer of equal weight,
and the re-association costs `G0` a bracket. The circle under the same ceiling has to be written in its general
(expanded) form at depth `7`; the control writes that form with `0` brackets, and `G01` needs `8`
for the identical tree. **That gap — `0` against `8` for the same computation under the same ceiling — is the
sharpest thing in this experiment.**

## The five headline questions

| # | question | answer |
|---|---|---|
| 1 | Do depth and peak memory conflict, and on how many objects? | Yes, on `6` of `37`; `3` of them movable and `3` frozen chains |
| 2 | Does the cost ranking change as the ceiling tightens? | Yes, first at ceiling `3`: `G16` and `G18` stop sharing first place and `G10` falls `6` |
| 3 | Is `G0` ever infeasible where another world is feasible? | No — `0` witnesses in `111` cells; feasibility is world-invariant |
| 4 | How many objects have more than one Pareto-optimal writing? | `18` objects by writing, `6` objects by point |
| 5 | Is the cheapest writing ever the most memory-hungry one? | Yes, in `91` of `200` cells, exclusively so |

Question 5 deserves its number spelled out. Only `8` objects have writings that differ in `peak_live` at all, so
the grid is `8` times `25` equals `200` cells; in `91` of them **every** cheapest writing that world has sits at
the object's maximum `peak_live`, so a ceiling at that maximum minus one costs that world real brackets. By
object: `circle` `20`, `distributive_law` `13`, `line` `13`, `difference_quotient` `13`, `ellipse` `9`,
`hyperbola` `9`, `trapezoid_area` `9`, `linear_approximation` `5`.

## Multicore, by measurement

Repository policy is multicore by default with a sequential path only where a measurement justifies it. This
module has two independent CPU-bound workloads and each was timed both ways on `16` cores with `12` workers
(headroom `2` cores, cap `12`, worker count derived from the observed core count):

| workload | units | chunks | sequential | parallel | speedup | identical | default |
|---|---|---|---|---|---|---|---|
| probe over the parenthesization space | 1511296 trees | 428 | 24.17 s | 8.38 s | 2.88 | yes | parallel |
| grid audit, writings times worlds | 28575 cells | 24 | 9.09 s | 3.35 s | 2.72 | yes | parallel |

Each path is timed `3` times and the **minimum** is reported, because this repository's cards run concurrently on
one machine and other load can only push a run time up. Pool startup measured at `1.286` s and declared as `1.3`.
Per-tree cost measured at `1.599e-5` s and declared as `1.6e-5`; per-cell cost measured at `3.182e-4` s and
declared as `3.2e-4`. Both workloads are processes rather than threads because both are CPU-bound pure Python;
parallelism changes only how fast, and `identical` is asserted on both paths in the test suite.

## Limits

- `peak_live` counts **values and not bytes**. Mapping it to terabytes assumes the live values are of comparable
  size, which for a corpus of scalar arithmetic is a strong assumption. It is a structural bound and not a memory
  benchmark; no wall-clock and no byte count is measured here.
- The writing space is the **parenthesizations of one token word**. Commutative reorderings are out of scope, and
  that is a real restriction: `a + b + c + d` regrouped is in the space, `b + a + d + c` is not, and a real
  compiler would use both. The published space is therefore a lower bound on what is reachable.
- The ceiling is a **declared threshold**, not a device limit. `2`, `3` and `4` are the whole useful range only
  because this corpus's peaks run from `2` to `4`; a corpus of deeper expressions would have a wider range and
  might change every ranking here.
- The corpus is **hand-chosen** — `34` named objects imported from 0038 plus `3` synthetic chains — and it is small
  enough that a single object moves a total. The `8`-object basis at ceiling `2` is the extreme case and its
  numbers are quoted with that caveat attached.
- The **null-model split** is why the chains are reported separately. On a single repeated operator no convention
  can act, so any ranking drawn from those entries would be a parsing artifact rather than a finding; `7` of the
  `37` entries are frozen and contribute the same constant to all `25` totals.
- `G0` ranking `6`th of `25` at the unconstrained ceiling does **not** contradict 0037's `3`rd of `25`. The basis
  differs: 0037 sums declared writings over `33` laws, this experiment minimises over the whole confirmed writing
  space of the `30` movable objects. The two numbers answer different questions and neither corrects the other.
- Feasibility being world-invariant is a statement about **Generation 1 with brackets**. A language without a
  bracket, or one whose worlds had different operator sets, could break it; nothing here rules that out, and
  0019's operator-support reduction is where such a case would come from.

## Evidence classification

- The Sethi-Ullman rule and the `depth` and `peak_live` values of any given tree: **classical result plus
  computation**, cited to Sethi and Ullman 1970 and not claimed as new.
- `1143` confirmed writings out of `1511296` trees, `0` SymPy rejections: **observation**, and the `0` is a
  property of this corpus rather than of the method.
- The round trip, minimality and peak-invariance grids: **observation**, `28575` and `122571` checks with `0`
  failures.
- The null-model split, `30` movable against `7` frozen: **observation**, with the frozen-entry constancy
  additionally asserted per object and per ceiling in the test suite.
- The ranking change at ceiling `3`: **observation** on a fixed basis of `29` objects, checked at tier level so it
  cannot be a tie-break artifact.
- World-invariance of feasibility: **structural argument**, and the `111`-cell sweep that accompanies it **is** an
  empty search — `feasible` filters on `peak_live <= ceiling`, which never consults a grammar, so evaluating it
  once per world and finding agreement is a theorem about the code. The load-bearing evidence is the separate
  round-trip grid, `28575` checks with `0` failures, which is what makes "every world renders every tree" true.
- That a smaller `peak_live` implies less real memory on real hardware: **hypothesis**, not measured here.

## Validation

```text
python -c "from parseatlas.memory_ceiling import memory_ceiling_report; r = memory_ceiling_report(); print(r['headline'])"
```

```text
python -c "from parseatlas.memory_ceiling import parallel_decision; d = parallel_decision(); print(d['probe']['speedup'], d['grid']['speedup'], d['identical'])"
```

```text
python -m pytest -q tests/test_memory_ceiling.py
47 passed
```
