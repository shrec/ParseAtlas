# ParseAtlas experiment 0043: reachability outranks cost

## The owner's question, answered first

On 2026-09-04 the owner corrected the whole ranking programme:

> The criterion is not always speed. Sometimes a task is UNREACHABLE in representation A and becomes
> REACHABLE in B - even if B is slow.

**Six tasks are unreachable in our convention `G0` and reachable elsewhere. Here they are, with the
worlds that can do them and what they cost there.**

| task | worlds that reach it | cheapest world | cost there | witness writing | why `G0` cannot |
|---|---|---|---|---|---|
| `binomial_cube` x `roots` | 12 | `G01` | `0` | `a + b * a + b * a + b` | needs `3` brackets in `G0` |
| `binomial_cube` x `factor_structure` | 12 | `G01` | `0` | `a + b * a + b * a + b` | needs `3` brackets in `G0` |
| `binomial_cube` x `degree` + `roots` | 12 | `G01` | `0` | `a + b * a + b * a + b` | needs `3` brackets in `G0` |
| `binomial_cube` x `degree` + `factor_structure` | 12 | `G01` | `0` | `a + b * a + b * a + b` | needs `3` brackets in `G0` |
| `binomial_cube` x `roots` + `factor_structure` | 12 | `G01` | `0` | `a + b * a + b * a + b` | needs `3` brackets in `G0` |
| `distance_components` writable at all | 12 | `G09` | `0` | `x2 - x1 * x2 - x1 + y2 - y1 * y2 - y1` | needs `4` brackets in `G0` |

The line to read twice is the fourth column. **The premium for reaching what `G0` cannot reach is
zero.** Every one of the six is written with **no brackets at all** in its cheapest world, while
`G0` pays an average of `0.6109` brackets for the `239` tasks it *can* do. The "even if it is slow"
scenario turns out not to cost brackets here: what it costs is the convention.

In our convention the cube of a binomial is `(a + b) * (a + b) * (a + b)`, three bracket pairs, and
its expanded side is free - so `G0` writes the expanded side, and the roots and the factor structure
are off the page. In `G01` (`+ - * /`) the same object's factored side is `a + b * a + b * a + b`,
bracket-free, and the roots are on the paper.

---

## What is being measured

A **task** is a declared `(object, requirement)` pair. `reachable(task, world)` asks whether a world
can do it **at all**, and every table keeps three things in separate columns:

```text
reachable   is there a writing of this object that this world renders within the bracket budget
            and that satisfies the requirement?
free        does the requirement already hold in the writing this world reaches for anyway - the
            cheapest one, which is what 0038 measured?
premium     when reachable but not free, how many extra bracket pairs the witness costs there
```

**Expensive is never reported as impossible.** An unreachable cell carries a reason, and the two
reasons are never summed:

```text
no_witness   no writing of this object satisfies the requirement at any price - impossible under
             our declared shape rules
budget       a witness exists and this world writes it too expensively - expensive, not impossible
```

### The three requirement kinds, and the rule for each

| kind | rule | what it demands |
|---|---|---|
| `property` | `manifest_in_some_writing` | one writing, within budget, whose written form the imported 0038 shape rules make the named property manifest in |
| `property_pair` | `simultaneous_in_one_writing` | ONE writing, within budget, making BOTH properties manifest at once; two writings each showing one is not enough |
| `writable` | `within_bracket_budget` | one writing this world renders within the budget, with no visibility demanded at all |

### The bracket budget, and why it is in this section and not in the limits

`BRACKET_BUDGET = 2`. A written form may carry at most two bracket pairs before a reader is taken to
reject it. **This is a declaration, not a measurement**; nothing here measures a reader.

It is set to `2` because two bracket pairs is what `G0` already demands of `33` of this corpus's
`34` objects when each is written in the form `G0` prefers. The threshold is therefore calibrated to
what today's convention itself requires, which makes it **generous to `G0`** and every finding
against `G0` conservative. The one object it does not cover is `distance_components`, which `G0`
cannot write in fewer than `4` brackets - and that object duly appears in the six above.

The budget is also load-bearing in a way that has to be admitted here rather than buried. Under the
primary `transparent` regime the manifest set of a *written form* does not depend on the grammar
(0038 declares this; 0039 verified it over `16675` checks). So with **no** budget at all, "is this
property manifest in some writing of this object" has the same answer in all `25` worlds:

```text
transparent, budget 8 (nothing excluded)   routable set = 0 tasks
```

**The budget is what turns cost into reachability.** The reach ranking is therefore not independent
of the cost ranking, and this report measures how much they still disagree instead of pretending
they are unrelated. Two things stop it from being circular: the `opaque` regime of 0038, where a
bracket hides what is inside it, makes the manifest set genuinely world-dependent and keeps a
routable set of `192` tasks at an unbounded budget; and the full budget sweep `0`..`8` is published
in both regimes, so a reader who disagrees with the threshold can read their own answer off the
table.

## Corpus and tasks

The corpus is **imported, not rebuilt**: `parseatlas.manifest_properties.CORPUS`, which is 0037's
`33` named laws plus 0038's calibration quadratic.

```text
objects        34        writings       50        grammars   25
tasks         481   =   140 property  +  307 property_pair  +  34 writable
```

Every property named in a task is one `ground_truth` - the SymPy control, not the shape rules -
calls TRUE of the object. Asking a world to show something that is not there would be a defect, not
a finding.

## Correctness bridge

Every reachability verdict rests on a rendering, so the rendering is checked first.

```text
round trip       1250 checks         0 failures
minimality       1811 brackets       0 violations
surface mirror   1250 checks         0 failures
```

A rendering that does not re-parse to its own tree is not a writing of the object; a rendering
carrying a bracket its grammar does not require inflates the cost the budget is compared against.

**Soundness of `reachable` itself**, swept over both regimes and all nine budgets:

```text
reachable cells checked                            71246
properties claimed by the selected witnesses      229493
violations                                             0
```

A violation would be a witness that does not satisfy its requirement, a witness over budget, or a
witness claiming a property ground truth denies.

## Null model

A task reachable in all `25` worlds adds the same constant to every world; a task reachable in none
subtracts nothing from any. **Only the routable set can order conventions**, so the split is
reported first and every ranking below is computed over the routable set alone.

```text
                             all 25    none      routable    total
transparent, budget 2           140       236          105      481
  property                       53        46           41      140
  property_pair                  60       190           57      307
  writable                       27         0            7       34
```

**The `236` tasks reachable nowhere are all blocked by `no_witness`, and `0` by the budget.** The
ceiling is a fact about the shape rules; the budget only ever separates one world from another.

The `46` property tasks reachable nowhere are exactly experiment 0038's `46` true-but-never-manifest
pairs and experiment 0039's ceiling, computed here by a different route - 0038 looks only at each
world's chosen writing, this module looks at every writing within budget - and required to agree.
They do.

## Observed results

### 1. The routable set, world by world

Reach counts over the `105` routable tasks. Worlds with identical reach sets are grouped, because a
tie here is a fact and not something to break.

| reach | worlds | 0037 cost ranks |
|---|---|---|
| **99** | `G0` `G15` `G16` `G18` | 3, 5, 2, 1 |
| 98 | `G13` `G14` `G17` | 9, 8, 5 |
| 93 | `G09` `G10` | 7, 3 |
| 76 | `G03` `G04` | 16, 15 |
| 65 | `G01` | 17 |
| 63 | `G24` | 10 |
| 62 | `G23` | 13 |
| 61 | `G22` | 11 |
| 59 | `G12` | 12 |
| 56 | `G07` | 14 |
| 40 | `G20` | 20 |
| 35 | `G06` | 23 |
| 33 | `G19` | 21 |
| 28 | `G05` | 24 |
| 26 | `G02` | 25 |
| 24 | `G21` | 18 |
| 22 | `G11` | 19 |
| 17 | `G08` | 21 |

`G0` reaches `99` of `105` and is **joint-first** with `G15`, `G16` and `G18`, which are three of the
five worlds 0038 calls blind to `factor_structure`.

**That is not the irony it looks like, and the two measures must not be conflated.** 0038's
"blind" quantifies over the writing a world would *choose* — its cheapest one. `reachable` here
quantifies over *every* writing within the budget. On this experiment's own measure the five
so-called blind worlds are not handicapped at all: of the `20` objects whose `factor_structure` is
true, `G0`, `G15`, `G16`, `G18` and `G24` each reach `7` — the maximum in the table — while most
sighted worlds reach `6`. At an unbounded budget **no world is factor-blind**. The blindness is
entirely a statement about the free column: the blind five write it at `0`, the sighted worlds
between `1` and `6`. So a cheap convention does not fail to express factorisation; it fails to
choose it.

### 2. The partial order

`A` dominates `B` when `A` reaches every task `B` reaches and at least one more. This is a partial
order and a total ranking would be a lie about it.

```text
world pairs                300
comparable (one dominates)  46
incomparable               243
equal reach sets            11
distinct reach sets         18
```

**`243` of `300` pairs are incomparable.** Ten worlds are maximal:

```text
G0  G01  G03  G04  G07  G09  G10  G15  G16  G18
```

`G0` **is** maximal: nothing dominates it. It dominates `G13`, `G14`, `G17`, `G23` and `G24`. But
maximality is cheap here - four of the ten maximal worlds (`G01`, `G03`, `G04`, `G07`) sit at cost
ranks `17`, `16`, `15` and `14`, and they are maximal precisely because they reach tasks the cheap
worlds cannot.

### 3. Cost against reach - the collision

0037's cost rank is **imported, not recomputed**. Reach is over the routable set.

| id | cost rank | cost total | reach | reach rank | displacement |
|---|---|---|---|---|---|
| `G18` | 1 | 42 | 99 | 1 | `0` |
| `G16` | 2 | 44 | 99 | 1 | `-1` |
| **`G0`** | **3** | **45** | **99** | **1** | **`-2`** |
| `G10` | 3 | 45 | 93 | 8 | `+5` |
| `G15` | 5 | 46 | 99 | 1 | `-4` |
| `G17` | 5 | 46 | 98 | 5 | `0` |
| `G09` | 7 | 47 | 93 | 8 | `+1` |
| `G14` | 8 | 48 | 98 | 5 | `-3` |
| `G13` | 9 | 50 | 98 | 5 | `-4` |
| `G24` | 10 | 57 | 63 | 13 | `+3` |
| `G22` | 11 | 58 | 61 | 15 | `+4` |
| `G12` | 12 | 60 | 59 | 16 | `+4` |
| `G23` | 13 | 61 | 62 | 14 | `+1` |
| `G07` | 14 | 80 | 56 | 17 | `+3` |
| `G04` | 15 | 81 | 76 | 10 | `-5` |
| `G03` | 16 | 83 | 76 | 10 | `-6` |
| `G01` | 17 | 84 | 65 | 12 | `-5` |
| `G21` | 18 | 91 | 24 | 23 | `+5` |
| `G11` | 19 | 93 | 22 | 24 | `+5` |
| `G20` | 20 | 94 | 40 | 18 | `-2` |
| `G08` | 21 | 95 | 17 | 25 | `+4` |
| `G19` | 21 | 95 | 33 | 20 | `-1` |
| `G06` | 23 | 96 | 35 | 19 | `-4` |
| `G05` | 24 | 97 | 28 | 21 | `-3` |
| `G02` | 25 | 99 | 26 | 22 | `-3` |

```text
Spearman rank correlation (cost rank vs reach rank)   +0.8911
maximum displacement                                        6
mean absolute displacement                               3.12
```

At the declared gap of `8` ranks, **no world is cheap-and-weak and none is dear-and-strong**. The
extremes are named anyway: `G10`, `G21` and `G11` are cheaper than their reach deserves by `5` ranks;
`G03` is stronger than its cost suggests by `6`.

**No world strictly out-reaches every world on the cost podium.** But `12` worlds each reach `5`
tasks that **no** podium world reaches - the five `binomial_cube` tasks - and every one of those
twelve has cost rank `14` or worse:

```text
worlds       G01 G02 G03 G04 G05 G06 G07 G08 G11 G19 G20 G21
cost ranks    17  25  16  15  24  23  14  21  19  21  20  18
podium (G0 G10 G16 G18) reaches       100 of the 105 routable tasks
```

That is the routing result. Not domination - **complementarity**, and the complement is expensive.

### 4. The premium, both kinds

The owner's scenario, per task, is the table at the top of this report: mean cost elsewhere `0.0`
against `G0`'s mean of `0.6109`, a premium of `-0.6109` brackets.

There is a second, within-world premium that must not be confused with it: a task can be reachable
in a world without being free there, because the witness is not the writing that world would have
reached for.

```text
reachable cells                                  5119
  of them free (the world's default writing)     4011
  of them paid (a costlier witness)              1108
mean extra brackets on a paid cell             1.1715
distribution of the extra brackets      0: 268   1: 382   2: 458
```

So `1108` of `5119` reachable cells - `21.6` percent - are things a world can see only by writing
the object in a form it would not otherwise choose. That is the honest measure of "expensive but
possible", and it is reported separately from "impossible".

### 5. Is the cost podium factor-blind? A correction

The card's premise was that 0037's three cheapest grammars are `G18`, `G16`, `G0` and that the
entire cost podium is therefore blind to `factor_structure`. Both halves were re-derived here
independently. **The overlap is not total.**

```text
factor-blind (re-derived here, agrees with 0038)   G0  G15  G16  G18  G24
0037 cost podium (rank <= 3)                       G18 G16 G0  G10
overlap                                            G18 G16 G0             3 of 4
on the podium and NOT blind                        G10
```

Rank `3` is a **tie**: `G0` and `G10` both cost `45` brackets. "The three cheapest grammars" is
therefore not a well-defined set without inventing a tiebreak, and the podium holds four worlds. Of
those four, three are factor-blind and `G10` (`- * / +`) is not.

What survives the correction, and it survives with force:

```text
mean 0037 cost rank,  the 5 factor-blind worlds     4.20      totals mean  46.80
mean 0037 cost rank,  the 20 factor-sighted worlds 15.05      totals mean  75.15
```

**Optimising for cost selects factor-blind conventions.** It does not select them exclusively - one
podium world sees factorisation - but the blind five occupy cost ranks `1`, `2`, `3`, `5` and `10`
while the sighted twenty average rank `15.05` and cost `60.6` percent more brackets.

### 6. The budget sweep

The answer to the owner's question is a function of the declared threshold, so the whole function is
published rather than one value of it.

| regime | budget | all 25 | none | routable | unreachable in `G0`, reachable elsewhere | `G0` reach | `G0` reach rank | maximal | Spearman |
|---|---|---|---|---|---|---|---|---|---|
| transparent | 0 | 8 | 248 | 225 | **75** | 150 | 3 | 18 | +0.8741 |
| transparent | 1 | 24 | 242 | 215 | **65** | 150 | 5 | 19 | +0.8960 |
| **transparent** | **2** | **140** | **236** | **105** | **6** | **99** | **1** | **10** | **+0.8911** |
| transparent | 3 | 182 | 236 | 63 | **1** | 62 | 1 | 10 | +0.9131 |
| transparent | 4 | 205 | 236 | 40 | **0** | 40 | 1 | 12 | +0.8690 |
| transparent | 5 | 206 | 236 | 39 | **0** | 39 | 1 | 12 | +0.8727 |
| transparent | 6 | 239 | 236 | 6 | **0** | 6 | 1 | 17 | +0.6663 |
| transparent | 7 | 239 | 236 | 6 | **0** | 6 | 1 | 21 | +0.5374 |
| transparent | 8 | 245 | 236 | 0 | **0** | 0 | 1 | 25 | undefined |
| opaque | 0 | 8 | 248 | 225 | **75** | 150 | 3 | 18 | +0.8741 |
| opaque | 1 | 14 | 246 | 221 | **72** | 149 | 3 | 18 | +0.8579 |
| opaque | 2 | 35 | 244 | 202 | **63** | 139 | 3 | 13 | +0.8695 |
| opaque | 3 | 39 | 244 | 198 | **62** | 136 | 3 | 14 | +0.8724 |
| opaque | 4 | 41 | 244 | 196 | **61** | 135 | 3 | 15 | +0.8576 |
| opaque | 5 | 42 | 244 | 195 | **61** | 134 | 3 | 15 | +0.8576 |
| opaque | 6 | 45 | 244 | 192 | **61** | 131 | 3 | 13 | +0.8400 |
| opaque | 7 | 45 | 244 | 192 | **61** | 131 | 3 | 13 | +0.8400 |
| opaque | 8 | 45 | 244 | 192 | **61** | 131 | 3 | 13 | +0.8400 |

The count of tasks unreachable in `G0` but reachable elsewhere ranges from `0` to `75` across the
eighteen settings. **The published `6` is the second most conservative non-zero value in the whole
table**, and it comes from the budget calibrated to `G0`'s own demands. Every other defensible
setting that leaves a gap at all makes `G0` look worse, not better — **except transparent budget
`3`, which leaves a gap of `1`.** That is the one setting more favourable to `G0` than the
published figure, and it is named here because the sweep printed above already contains it.

The last transparent row is the null this experiment has to publish: at budget `8` nothing is
excluded, the routable set is empty, and reachability is convention-independent.

### 7. The opaque regime - robustness

0038's alternative rule set, where a bracket is visual encapsulation and a rule may not look inside
it. Here the manifest set depends on the world twice over, so reachability is not a thresholded
cost and the routable set survives an unbounded budget.

```text
                              transparent       opaque
three-way split               140/236/105   35/244/202
unreachable in G0, reachable
  elsewhere                             6           63
G0 reach (routable)                    99          139
G0 reach rank                           1            3
maximal worlds                         10           13
G0 maximal                            yes          yes
incomparable pairs                    243          273
distinct reach sets                    18           22
Spearman                          +0.8911      +0.8695
```

Under the rule change the six become `63`, spread over thirteen objects (`ellipse` 15, `hyperbola`
15, `quadratic` 5, `binomial_cube` 5, `binomial_square` 4, `difference_of_squares` 4, `midpoint` 3,
`taylor_first_term` 3, `taylor_second_term` 3, `distributive_law` 2, `trapezoid_area` 2,
`distance_components` 1, `quotient_rule` 1), and `G0` falls from joint-first to third. The premium
stays zero: all `63` are reachable at `0` brackets in their cheapest world against `G0`'s mean of
`0.1552` over the `174` tasks it can do.

**What survives:** that there are tasks unreachable in `G0` and reachable elsewhere; that the
premium for reaching them is not positive; that the order is strongly partial; that cost and reach
correlate around `+0.87` without agreeing. **What does not survive:** `G0`'s exact place (`1` against
`3`), the exact split, and the size of the gap (`6` against `63`).

## Headline questions, one sentence and a number each

1. **How many tasks are unreachable in `G0` but reachable somewhere else, and which are they?**
   `6` at the declared budget - the `roots`, the `factor_structure` and three property pairs of
   `binomial_cube`, plus writing `distance_components` at all - each reachable in `12` other worlds,
   and between `0` and `75` across the whole budget sweep.
2. **Is the cost podium really factor-blind - is the overlap total?** **No:** `3` of the podium's
   `4` worlds are factor-blind and `G10` is not, but the blind five average cost rank `4.20` against
   the sighted twenty's `15.05`, so cost does select blindness without selecting it exclusively.
3. **What is the correlation between cost rank and reachability rank?** Spearman `+0.8911`
   (transparent) and `+0.8695` (opaque), with mean absolute rank displacement `3.12` and a maximum
   of `6` - high, and partly by construction, because the budget makes reachability a thresholded
   cost.
4. **Which worlds are maximal, and is `G0` one of them?** `10` of `25` are maximal - `G0`, `G01`,
   `G03`, `G04`, `G07`, `G09`, `G10`, `G15`, `G16`, `G18` - and **yes**, `G0` is maximal, dominated
   by nothing and dominating `5`.
5. **Is there a world that is dear to write in and reaches strictly more than every cheap one?**
   **No** - `0` worlds strictly out-reach the podium - but `12` worlds, all at cost rank `14` or
   worse, each reach `5` tasks that no podium world reaches, so the relationship is complementarity
   and not domination.
6. **What does reaching an otherwise-unreachable task cost, on average?** **Nothing:** all `6` cost
   `0` brackets in their cheapest world, `0.6109` fewer than `G0`'s own mean over the tasks it can
   do; the price is paid in changing convention, not in brackets. Inside a single world the
   comparable figure is `1.1715` extra brackets on the `1108` of `5119` reachable cells that are not
   free.

## Interpretation

**1. Reachability is a partial order and it refuses to become a ranking.** `243` of `300` world
pairs are incomparable and there are `18` distinct reach sets among `25` worlds. Every previous
ranking in this project was a total order over a cost; this one is not a total order at all, and
that is the structural point. Asking "which convention is best" has no answer here. Asking "which
convention can do this task" does.

**2. The cost podium is where factorisation goes to disappear, but not perfectly.** The card's
premise was one world too strong. `G10` costs the same `45` brackets as `G0` and does see
factorisation. What holds is the tendency, and it is large: cost rank `4.20` against `15.05`. A
convention that makes the expanded, monomial-sum writing cheap is thereby a convention in which the
factored writing is dear, and the factored writing is the one that carries roots and factor
structure. The two facts are one fact.

**3. The premium is negative, and that is the finding.** The owner's scenario was "reachable in B
even if B is slow". Measured, B is not slow: the six tasks `G0` cannot reach are free in the worlds
that can. What is expensive is not the task in the other world - it is the *rest of mathematics* in
that other world. `G01` writes the binomial cube's factorisation for nothing and pays `84` brackets
across the workload against `G0`'s `45`. **The trade is not per-task, it is per-convention**, which
is exactly why a cost ranking cannot see it.

**4. The budget is where the honesty lives.** Under the transparent rules with no budget, this
experiment has no subject: reachability is convention-independent and the routable set is empty. It
would have been easy to publish the budget-zero row - `75` tasks unreachable in `G0` - and call it a
result. The threshold that was actually declared is the one calibrated to `G0`'s own demands, which
gives the second-smallest non-zero count in the whole table. Both are in the sweep.

**5. This is consistent with 0034, 0037 and 0038 and adds the axis they lack.** `G0` is `11`th on
cost over mixed formulas, `3`rd on cost over named laws, joint-first on visibility, joint-first on
reachability under a two-bracket budget - and it still cannot see the cube's roots. Those are not
five different facts. They are one decision - `G0` makes the expanded writing cheap - seen from five
sides.

## Limits

- **Reachability is defined by OUR declared shape rules.** A property unreachable under these rules
  is not unreachable under all rules. 0038 measured that the visibility *trade* survives a rule
  change while the counted bookkeeping does not, and the same holds here: the opaque regime keeps
  every qualitative conclusion and moves every count (`6` becomes `63`, `G0` moves from rank `1` to
  rank `3`). The ROADMAP standing caveat on the scope of negative results applies here as sharply as
  anywhere in the project.
- **The bracket budget is a declared threshold and not a fact about readers.** Nothing here measures
  a reader. `2` is calibrated to what `G0` demands of `33` of the `34` objects; the whole sweep
  `0`..`8` is published because the headline number moves from `75` to `0` across it.
- **Under the transparent regime the routable set is created entirely by the budget.** At budget `8`
  it is empty. The reach ranking is therefore not independent of the cost ranking, which is why the
  Spearman correlation is reported as a measurement of their disagreement rather than as evidence
  that they are different instruments.
- **The corpus is hand-chosen.** `34` objects: 0037's `33` named laws plus one calibration
  quadratic. It reflects a judgement about which laws are fundamental and is not a sample from any
  population.
- **The language has no radical and no imaginary unit.** Generation 1 has only binary `+ - * /`,
  parentheses, integer literals and named variables. Experiment 0039 accounts for `8` of its `46`
  hidden pairs this way - `7` need `i`, `1` (`parabola` x `roots`) needs a square root, and the two
  cubic identities need both. Those `8` are unreachable everywhere for a reason that is about the
  **language** and not about precedence, and no choice of convention can move them.
- **The domain component of the project semantic key is inert** (`NF-2026-00005`):
  `parseatlas.canonical.canonicalize` writes the literal `R` for every expression, so the operative
  key is `(canonical form, excluded points)`.
- **Principal variables are declared, not inferred**, and `13` of the `34` objects have none; for
  those, the five variable-borne properties are false rather than merely hidden.
- **Generation 1 has no exponentiation**, so powers are repeated products (`x * x`). This raises the
  share of `*` in every tree and flatters grammars that bind `*` tightly.
- **Associativity is fixed left** for every operator and there is no unary minus.
- **A convention that reaches more is not thereby a convention mathematics should have adopted.**

## Evidence classification

- The three-way split (`140`/`236`/`105`), the `6` tasks unreachable in `G0`, the reach counts, the
  partial order (`46`/`243`/`11`), the Spearman correlations, the premium figures and the whole
  budget sweep - **OBSERVED**, on this corpus, these 25 grammars, these rules, this budget.
- Round trip (`1250`/`0`), minimality (`1811` brackets, `0` violations), surface mirror
  (`1250`/`0`) and the witness soundness sweep (`71246` cells, `229493` claims, `0` violations) -
  **VERIFIED PROPERTIES** on this grid, not proofs over all trees.
- The `46` reachable-nowhere property tasks agreeing with 0038's `46` hidden pairs -
  **CROSS-CHECK**, two different computations required to agree.
- "The overlap between the cost podium and factor blindness is not total" - **CORRECTION** to the
  card premise, derived from 0037's own published ranking, in which rank `3` is a tie.
- Robustness across the two regimes (qualitative conclusions survive, counts do not) - **OBSERVED**
  over one alternative, equally defensible rule set; not a claim about all possible rule sets.
- "A convention that cannot reach factorisation slowed its mathematicians" - **HYPOTHESIS**. Only
  reachability is measured.
- The high cost/reach correlation - **OBSERVED**, and partly **BY CONSTRUCTION**, since a bracket
  budget makes reachability a thresholded cost under the transparent regime. Stated as such.

## Validation

```text
python -m pytest -q tests/test_reachability_first.py      49 passed
python -m pytest -q                                      889 passed   (as of this run)
```

Every headline number is pinned **literally** in the tests rather than recomputed from the module,
so a change in the result fails a test instead of silently rewriting this report. The order of the
test file is the order the argument has to be defended in: the correctness bridge first, then
soundness, then anything that measures conventions.

### Concurrency: sequential by measurement

```text
cells                                    1250   (50 writings x 25 worlds)
sequential (min of 5)                  0.2593 s  ->  2.07e-4 s / cell
process pool startup (12 workers)      1.2772 s  <- workers import this module, and so SymPy
parallel (12 workers)                  1.5908 s
speedup                                  0.20x  ->  sequential 5.0x faster
identical results                          True
```

`should_parallelise` does arithmetic on two **measured** numbers and not on a cell count; the same
rule returns `True` when the work is large enough, and both directions are pinned. The worker count
comes from the observed core count (`16` to `12`, two cores in headroom) and never from a hardcoded
constant. The per-cell cost was observed between `2.07e-4` s and `5.2e-4` s and the pool startup
between `1.28` s and `3.74` s depending on machine load; the sequential verdict holds at every
corner of that range, and a test asserts it.

### Mutation testing

On an isolated copy (tree copied into the scratchpad; the canonical repository untouched; a
preflight asserts the test run imports the **copy**), `24` mutants at the decisive places:

```text
the bracket budget is compared with < instead of <=                   KILLED
the bracket budget is not applied at all                              KILLED
a property pair may be satisfied by two different writings            KILLED
a requirement is satisfied when ANY of its properties is manifest     KILLED
a writable task demands that SOMETHING be manifest as well            KILLED
the DEAREST admissible witness is reported instead of the cheapest    KILLED
the free column is read off the world's dearest writing               KILLED
the writable task kind is dropped from the corpus                     KILLED
the control gap lists the tasks G0 CAN do                             KILLED
expensive is reported as impossible: blocked_by is always budget      KILLED
impossible is reported as expensive: blocked_by is always no_witness  KILLED
dominance becomes non-strict, so equal worlds dominate each other     KILLED
dominance is computed over ALL tasks, not the routable set            KILLED
the routable set swallows the tasks reachable everywhere              KILLED
tasks are built from what is manifest instead of from ground truth    KILLED
factor blindness looks at every writing instead of the default one    KILLED
the cost podium is truncated to rank 2                                KILLED
competition ranking becomes positional, so ties are broken silently   KILLED
the rank correlation ignores ties instead of using midranks           KILLED
the slow-but-possible baseline averages over ALL tasks                KILLED
the opaque regime is read with the transparent manifest sets          KILLED
the soundness sweep skips the opaque regime                           KILLED
the ceiling cross-check counts pair tasks as property pairs too       KILLED
cost-versus-reach uses reach over all tasks, not the routable set     KILLED

killed 24/24
```

Two further mutants were written and then discarded as **equivalent**, which is recorded rather than
hidden: making the `writable` rule fall through to `all(...)` over an empty property tuple is a
no-op, and requiring `default_cost <= budget` in the `free` column is redundant because the default
writing is the cheapest one. The second was removed from the module and replaced by a test that
asserts the implication over the whole grid, so the property is now checked instead of merely
guarded.
