# ParseAtlas experiment 0047: find the wall, do not declare it

## The failure this card is now about

**This card has made the same mistake twice, and that is its result.** It was written to apply the
ROADMAP rule *Let the system find the wall* — do not declare a bound and then read the answer the
bound produces. It violated that rule twice, at two different levels, and the second violation was
introduced by the repair of the first.

```text
round 1   the enumeration stopped at one bracket pair per site.  The report argued the bound was
          safe — "a writing past the limit continues the curve of its cell FLAT" — and published a
          turn the bound had created.                                                     REJECTED

round 2   the repair admitted nesting and correctly withdrew the turn.  But the site walk visited
          only compound nodes, so a bracket around a LEAF was never enumerated, while the docstring
          said "every bracketable position" and the cell record said `attainable` was the largest
          count any writing reaches at all.  It was not.                            REJECTED AGAIN
```

Both times the shape of the error is identical: **a restriction on the enumeration was read as a
property of the rules.** The first was defended at length in prose; the second was not even
noticed, because the mechanism it missed is one this report itself describes and then never used.

That mechanism, stated where it belongs. In the 0038 rules `Part.is_atom` is `visible and
isinstance(node, Atom)`, and under the opaque regime a bracketed operand has `visible = False`. So
wrapping a **leaf** makes it a non-atom, and `_shape_factor_structure`, which asks for at least two
non-atom numerator factors, fires:

```text
a * (b + c)     1 bracket    opaque manifest: nothing
(a) * (b + c)   2 brackets   opaque manifest: factor_structure   — and it reparses to the same tree
```

`distributive_law / factored / G0 / opaque` was published as `bracket_counts [1, 2]`,
`attainable [0, 0]`, verdict `constant`. It **rises**.

**The general lesson, which is worth more than the curves.** An enumeration is a claim about what
exists. Every restriction on it must be declared at the point where the answer is read, and not
defended in prose somewhere else — because a defence is about the writings the restriction drops,
while the answer is an aggregate over the writings it keeps, and the two are different objects. The
round 1 defence was *true* about every individual writing past the bound and *false* about the
maximum over them. The round 2 restriction had no defence at all, only a docstring that contradicted
it. Every sweep in this report now answers one question in the report itself, by construction:
**what writings does this enumeration not produce, and would any of them change the answer?**

## The two withdrawals

### Round 1, withdrawn: "the rules admit the tax curve"

The withdrawn block read:

```text
witness_product_of_pairs under G0, opaque regime            WITHDRAWN

brackets      1                   2                     3
writing       a * b * (c * d)     (a * b) * (c * d)     ((a * b) * (c * d))
manifest      nothing             factor_structure      nothing
attainable    0                   1                     0
```

The cell's curve is the *maximum* over all writings at each bracket count. Any writing that already
carries a bracket can be padded — `(X)` rewritten as `((X))` — to any higher count without changing
what a shape rule sees, so the curve past a bracketed count is the **running maximum** of the
enumerated one, a running maximum cannot fall, and a peak with a drop after it is **impossible in
principle**. `((a * b)) * (c * d)` carries `3` brackets, reparses under `G0` to the same tree, and
still makes `factor_structure` manifest. That withdrawal stands and is reaffirmed here.

The leaf-admitting census strengthens it. At `3` brackets the census now produces
`(a) * (b) * (c * d)`, which shows `factor_structure` **without any padding at all**. So the
withdrawn `0 1 0` needed *both* restrictions: nesting to be unenumerated *and* leaves to be
unenumerated. The corrected cell is `0 1 1` in both readings:

```text
witness_product_of_pairs under G0, opaque regime            CORRECTED

brackets                 1                   2                     3
writing                  a * b * (c * d)     (a * b) * (c * d)     (a) * (b) * (c * d)
manifest                 nothing             factor_structure      factor_structure
attainable               0                   1                     1
before padding           0                   1                     1
```

### Round 2, withdrawn: "no cell of the 34-object corpus ever rises"

Every one of these sentences from the previous revision is false and is withdrawn:

```text
"no cell of the 34-object corpus ever rises"
"0 cells rise"
"cells that ever rise: 0 in every column"
"of the 17500 per-property cell curves ... exactly 0 ever rise"
"contains no object whose visibility a bracket improves"
the "opaque rises" column of the summary block
the within-cell split {constant 916, non-increasing 334}
```

The leaf-admitting census over the same `1250` opaque corpus cells says:

```text                                            withdrawn        observed
cells that ever rise                                      0              72
within-cell verdicts, attainable    constant 916,  non-increasing 334
                                 -> constant 844,  non-increasing 334,  non-decreasing 72
per-property cell curves that rise (of 17500)             0             100
```

and it names them, which is what makes the correction checkable rather than a changed number:

| writing | cells that rise | of how many worlds | property that switches on |
| --- | --- | --- | --- |
| chain_rule / standard | 25 | 25 | factor_structure |
| trapezoid_area / mean_times_height | 21 | 25 | factor_structure |
| distributive_law / factored | 13 | 25 | factor_structure |
| taylor_first_term / standard | 13 | 25 | factor_structure |

`72` cells, four writings, one property. The transparent half is untouched — `0` rises in `1250`
cells — because a leaf bracket is invisible to a transparent `_look`.

### What survives, and it is the important half

**No peak exists anywhere, and that is the load-bearing claim.** `cells_with_a_peak` is `0` in every
reading, in both grids, in both regimes — independently re-derived in review.

The clause about verdicts needs its scope, and an earlier revision of this sentence did not carry it.
Under the two **attainable** readings every within-cell verdict is `constant`, `non-increasing` or
`non-decreasing` and never `non-monotone`. Under the **pattern-mean** reading it is not: `128` of the
`1250` opaque corpus cells are non-monotone, and the witness grid carries `12` more. Those are
published in the table below and discussed by name; the summary sentence simply claimed more than
they allow. A non-monotone mean is not a peak — the mean falls and rises as the population of
writings at each bracket count changes — which is why `cells_with_a_peak` stays `0` throughout. So the round 1 withdrawal stands, the
impossibility of a peak stands, and the headline **no genuine turn exists anywhere in this
experiment** stands. What is gone is the corpus *negative* result.

## What the sweeps found

```text
A  brackets vs visibility, transparent rules   CONSTANT inside every cell, 1250 of 1250
A  brackets vs visibility, opaque rules        844 constant, 334 non-increasing, 72 NON-DECREASING,
                                               0 non-monotone, 0 peaks
A  the same rules on constructed witnesses     50 of 200 cells RISE, 0 cells peak
B  word length vs semantic diversity           NON-DECREASING in every support stratum and
                                               STILL RISING at the longest length swept
C  convention-axis width vs semantic yield     NON-DECREASING, and provably so; no widening
                                               anywhere in the sweep lost a meaning
```

Three *apparent* turns are reported and all three are refuted in place:

- the **pooled** bracket curve turns in both regimes — the opaque mean peaks at `2` brackets at
  `0.2076` and falls `0.2076` after it — while no cell underneath it peaks at all; the turn is a
  change in which objects reach that far along the axis, and the tail rests on `2` distinct objects;
- the **ceiling-fraction** curve of curve B has exactly one trough in every stratum above support
  `1`, and every trough sits where the T6 ceiling jumps from the Catalan bound to the support
  bound; the numerator moves smoothly and the denominator does not;
- the **0030 decay** from `100` per cent recovered at `k = 2` to `10.946` per cent at `k = 6` is a
  ratio whose denominator grows exponentially while its numerator is bounded by the registry size,
  and curve C shows directly that no widening ever loses a meaning.

Three fake turns, three different causes, and two withdrawn readings of the same grid. That is the
result.

## Purpose

The owner set this card twice over. As a methodological correction it applies the ROADMAP rule
*Let the system find the wall*, set on 2026-09-05:

> **Do not impose a limit in advance. Sweep the parameter until the observation shows where the
> limit is.**

Two revisions of this card have now failed that rule, in the two ways it can be failed: by declaring
a bound and defending it, and by leaving a restriction undeclared inside a repair. As a worked
example that is worth more than a clean pass would have been, and it is the reason the failure is at
the top of this report rather than in a footnote.

As a research subject the card asks for the shape the tax analogy names. Raise a tax rate and
revenue rises, up to a point, past which raising it further makes revenue *fall*. The turning point
is not derivable from the first half of the curve, and no threshold chosen in advance would have
found it. Earlier cards published a number at a bracket budget (0043), at a memory ceiling (0044)
and at an enumeration bound (0039); those numbers answer the questions they were framed around.
This card asks the other question: **where does more of something give less?**

Three parameters are swept. For each, this report publishes the full table of parameter against
observation, the first difference so a turn would show up as a sign change, the monotonicity
verdict, the argmax with its value, both the cell count and the distinct-object count behind every
point, and what the enumeration does not produce.

```text
A   how many brackets a writing carries    vs   what that writing makes manifest, by 0038 rules
B   how many operators a word carries      vs   how many distinct meanings the 25 worlds give it
C   how wide the convention axis is        vs   how many distinct meanings that axis yields
```

## Curve A: brackets against what a writing makes visible

### What is held fixed, and why that makes it a sweep

A writing of an object is its intended tree plus a set of bracketed positions. The world fixes a
**minimum** set, the brackets without which the string reparses into a different tree, and every
superset of that minimum is another writing of the *same* object. Sweeping the superset sweeps the
bracket count with the object, the world and the rules held fixed, and that is the only form of
this sweep in which "more brackets" is the cause of whatever the observation does.

The 0038 rules are imported unchanged: its seven properties, its two regimes, its shape functions,
its corpus of `34` objects in `50` named writings, and its `25` worlds. Nothing about manifestness
is re-decided here.

### What the enumeration produces, and what it does not

**Every node of the intended tree is a bracketable position, leaves and root included.** That is the
round 2 correction. A tree of `n` leaves offers `n` more sites than the previous revision counted,
and they are exactly the sites the opaque rules react to.

Bracket *subsets* cannot be enumerated: the corpus's largest writing,
`x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k`, has `27` positions and therefore `2 ** 27`
subsets, and with nesting the writings are infinite. So the unit of the census is the **bracket
pattern**: the set of *outermost* brackets of a writing, which is an antichain of positions. There
are `77336` of them for that writing and `156475` over the whole corpus, and the census is complete
and finite at once, because everything below an outermost bracket is invisible to every rule.

The question both rejections came down to, asked of this enumeration and answered by construction:

> **What writings does it not produce?** Exactly those whose brackets are not all outermost — a
> bracket inside a bracket, at any depth, in any number.
>
> **Would any of them change the answer?** No, and it is checked rather than argued. Such a writing
> has the manifest set of its pattern, in both regimes, and a bracket count at least its pattern's
> minimum, and every count above that minimum is reached by padding, which leaves the manifest set
> alone.

Five audits, each with its own declared scale:

| audit | scale | result |
| --- | --- | --- |
| every node is a site, and no leaf is ever forced | 1250 object x writing x world rows | holds in all |
| the zero-extra-bracket writing equals the 0038 surface tree | 1250 cells | agrees in all |
| every writing the census produces reparses to the intended tree | 981344 writings | agrees in all |
| a writing's manifest set is its pattern's, over EVERY bracket subset | 28968 subsets, 39 of 50 writings | agrees in all |
| the same, plus arbitrary nesting, on a seeded sample | 4000 writings, 3487 of them nested | agrees in all |

The fourth row is a **census** over the writings small enough to enumerate every bracket subset of
— `39` of the `50`, at a declared threshold of `11` positions. The fifth is a **sample**, and it is
labelled as one because nesting depth is unbounded and no census of writings exists to take; what
makes it sufficient is that the axis which *is* finite was censused in the row above it.

Past a cell's largest pattern the curve continues **constant** and is not tabulated: the largest
pattern is the most brackets a writing can carry with all of them visible, and every writing past it
repeats a pattern already counted, at a higher count, where the running maximum has already carried
the value. No cell's axis has a gap, in `2500` of `2500`.

### The three readings of a cell

```text
mean                  the average manifest count over the bracket patterns whose MINIMUM bracket
                      count is that one -- a mean over a declared population, labelled as one
unpadded attainable   the best a pattern at that count reaches before the padding carry
attainable            the best any writing at that count reaches at all, which is the running
                      maximum of the unpadded one -- every verdict is taken from this
```

The carry has exactly one exception. Out of a bracket-free writing there is nothing to double, so
`attainable(0)` is not carried into `attainable(1)`. That single exception is why the collapse at
the first opaque bracket survives and why an attainable curve can rise but never peak.

### The pooled curve, which turns

This is the curve a card would publish if it did not think about the null model. It is given first
so that it can be refuted. **Two sample columns, not one**: a cell is `object x writing x world`, so
the `25` worlds multiply a two-object tail into a fourteen-cell one.

| brackets | cells | objects | transparent mean | opaque mean | opaque attainable | opaque unpadded |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 424 | 34 | 2.0755 | 2.0755 | 2.0755 | 2.0755 |
| 1 | 638 | 34 | 1.8448 | 0.1067 | 0.1505 | 0.1505 |
| 2 | 1051 | 34 | 1.9924 | 0.2076 | 0.2426 | 0.2426 |
| 3 | 995 | 33 | 2.1377 | 0.1601 | 0.2302 | 0.1719 |
| 4 | 631 | 30 | 2.3011 | 0.1593 | 0.1791 | 0.1727 |
| 5 | 306 | 18 | 2.4673 | 0.1499 | 0.1699 | 0.1569 |
| 6 | 235 | 16 | 2.6383 | 0.1191 | 0.1191 | 0.1191 |
| 7 | 89 | 9 | 2.7191 | 0.0449 | 0.0449 | 0.0449 |
| 8 | 48 | 7 | 2.7917 | 0.0000 | 0.0000 | 0.0000 |
| 9 | 28 | 4 | 2.9286 | 0.0000 | 0.0000 | 0.0000 |
| 10 | 19 | 3 | 3.6842 | 0.0000 | 0.0000 | 0.0000 |
| 11 | 19 | 3 | 3.6842 | 0.0000 | 0.0000 | 0.0000 |
| 12 | 14 | 2 | 3.9286 | 0.0000 | 0.0000 | 0.0000 |
| 13 | 14 | 2 | 3.9286 | 0.0000 | 0.0000 | 0.0000 |
| 14 | 14 | 2 | 3.9286 | 0.0000 | 0.0000 | 0.0000 |

Under the **transparent** rules the mean, the attainable and the unpadded curves are the same three
numbers at every bracket count, because a transparent bracket is invisible: the manifest set of a
transparent cell is identical at every bracket count, in `1250` of `1250` cells. The maximum and the
mean of a constant coincide.

Both pooled curves are **non-monotone**. The transparent one troughs at `1` bracket at `1.8448` and
rises `2.0837` after it, ending at its argmax of `3.9286` at `12` brackets. The opaque mean troughs
at `1` at `0.1067` and peaks at `2` at `0.2076`, with a drop of `0.2076` after it; the opaque
**attainable** curve, a pooled average of running maxima, does the same thing at `0.1505` and
`0.2426`.

Read alone, that is a turning point at two brackets, and it would be wrong. **The tail is two
objects wide:**

| brackets | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cells | 48 | 28 | 19 | 19 | 14 | 14 | 14 |
| distinct objects | 7 | 4 | 3 | 3 | 2 | 2 | 2 |

`14` cells at `14` brackets is `2` objects in `2` writings: the `13` worlds that force no bracket on
`binomial_cube` expanded, and the `1` that forces none on `circle` general. The cell column on its
own makes a two-object tail look thicker than it is. Both columns are published throughout, and the
discipline audit takes its thin-point verdict off the object column.

### The paired first difference, where the rise is

The population changes with the parameter: a small tree has no writing with eight brackets, so the
cells present at `b = 8` are not the cells present at `b = 0`. The fix is to take each first
difference *inside* a cell and only then average, so that the two sides of every difference are the
same population.

| step | cells | transparent delta | opaque mean delta | opaque attainable delta | opaque rises | opaque falls |
| --- | --- | --- | --- | --- | --- | --- |
| 0 to 1 | 424 | 0.0000 | -1.9715 | -1.9057 | 0 | 334 |
| 1 to 2 | 638 | 0.0000 | 0.0926 | 0.1066 | 68 | 0 |
| 2 to 3 | 906 | 0.0000 | -0.0506 | 0.0044 | 4 | 0 |
| 3 to 4 | 549 | 0.0000 | -0.0155 | 0.0000 | 0 | 0 |
| 4 to 5 | 302 | 0.0000 | -0.0137 | 0.0000 | 0 | 0 |
| 5 to 6 | 219 | 0.0000 | 0.0037 | 0.0000 | 0 | 0 |
| 6 to 7 | 85 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 7 to 8 | 44 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 8 to 9 | 28 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 9 to 10 | 19 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 10 to 11 | 19 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 11 to 12 | 14 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 12 to 13 | 14 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| 13 to 14 | 14 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |

The rise and fall columns are of the attainable difference and they are the sharpest form of the
result. Under the transparent rules every paired difference is **exactly zero**. Under the opaque
rules a cell's attainable curve moves in exactly three places: it **falls** in `334` cells at the
first bracket, **rises** in `68` cells at the step to two brackets and in `4` more at the step to
three, and after that no cell moves at all. The cell by cell verdict says the same thing without any
averaging:

```text
                 attainable, padding admitted      unpadded attainable        pattern mean
transparent   constant 1250                     constant 1250            constant 1250
opaque        constant  844                     constant  778            constant  688
              non-increasing 334                non-increasing 400       non-increasing 362
              non-decreasing  72                non-decreasing  72       non-decreasing  72
              non-monotone     0                non-monotone     0       non-monotone   128

cells that ever rise:  0 transparent, 72 opaque attainable, 200 opaque pattern mean.
cells with a peak:     0 in every column, in both regimes, in both grids.
```

`66` of the `1250` opaque cells changed when padding was admitted. One of them is a named identity
and it is the round 1 correction landing inside the corpus:

```text
calibration_quadratic, factored writing, under G0, opaque regime

brackets                    2       3
unpadded attainable         1       0
attainable                  1       1
```

The `128` non-monotone cells in the pattern-mean column carry `0` peaks: they are troughs. The mean
over patterns can dip and recover — one bracket flattens a factor, two restore it — while the
maximum over the same patterns never falls back.

**Under the 0038 transparent rules a bracket is worth exactly nothing, in either direction.** That
is not a small statement. It says the visibility 0038 observes is a function of the intended tree
alone, and that the bracket count of a writing carries no information about it. Under the opaque
rules the first bracket costs `1.9715` properties on the mean reading and `1.9057` on the attainable
reading, and the second and third can buy one back.

### The seventy-two risers, and the mechanism

Every riser is `factor_structure` switching on, and every one of them works the same way: an opaque
bracket makes an operand uninspectable, therefore not an atom, therefore a compound factor.

```text
distributive_law / factored / G0 / opaque       chain_rule / standard / G0 / opaque

brackets     1               2                  brackets     0          1            2
writing      a * (b + c)     (a) * (b + c)      writing      dfg * dg   (dfg) * dg   (dfg) * (dg)
manifest     nothing         factor_structure   manifest     nothing    nothing      factor_structure
attainable   0               1                  attainable   0          0            1
patterns     1               2                  patterns     1          3            1
```

`chain_rule` is the widest riser — `25` of `25` worlds — and it is the clearest, because its
intended tree has no compound operand at all. `dfg * dg` is a product of two leaves; nothing about
it is a compound factorisation. Two brackets make the opaque rules *see* one, and ground truth
agrees that the object has two non-constant factors, so no soundness audit objects. `trapezoid_area`
rises in `21` of `25`, `distributive_law` and `taylor_first_term` in `13` each.

### The property strata

A shape rule can only be manifest where the property is actually true of the object, which is what
the 0038 `manifest => true` audit licenses, so a rate pooled over objects that do not have the
property would be observing corpus composition and not visibility. Every rate below is therefore
computed inside its own truth set, and the size of that set is part of the result — in cells and in
objects both.

| property | cells where true | objects where true | opaque rate at 0 brackets | opaque rate at 1 bracket |
| --- | --- | --- | --- | --- |
| degree | 875 | 21 | 0.9187 | 0.0000 |
| leading_coefficient | 875 | 21 | 0.4878 | 0.0000 |
| constant_term | 875 | 21 | 0.4959 | 0.0000 |
| roots | 875 | 21 | 0.3577 | 0.0000 |
| factor_structure | 800 | 20 | 0.1618 | 0.2359 |
| sign_structure | 1200 | 32 | 0.6373 | 0.0000 |
| even_parity | 125 | 4 | 0.8095 | 0.0000 |

Six of the seven rules collapse to zero at the first bracket under the opaque regime, and their
stratum curves are `non-increasing` with no turning point. The seventh is the interesting one.
`factor_structure` is the only rule that can react to a bracket by turning *on*, and its stratum
curve rises before it falls:

| brackets | cells in the stratum | objects in the stratum | opaque rate | transparent rate |
| --- | --- | --- | --- | --- |
| 0 | 272 | 20 | 0.1618 | 0.1618 |
| 1 | 407 | 20 | 0.2359 | 0.1671 |
| 2 | 675 | 20 | 0.3778 | 0.2356 |
| 3 | 628 | 19 | 0.3646 | 0.2994 |
| 4 | 400 | 17 | 0.2825 | 0.2725 |
| 5 | 219 | 12 | 0.2374 | 0.2374 |
| 6 | 158 | 12 | 0.1772 | 0.1772 |
| 7 | 55 | 6 | 0.0727 | 0.0727 |
| 8 | 26 | 4 | 0.0000 | 0.0000 |
| 9 | 18 | 2 | 0.0000 | 0.0000 |
| 10 | 13 | 1 | 0.0000 | 0.0000 |
| 11 | 13 | 1 | 0.0000 | 0.0000 |
| 12 | 13 | 1 | 0.0000 | 0.0000 |
| 13 | 13 | 1 | 0.0000 | 0.0000 |
| 14 | 13 | 1 | 0.0000 | 0.0000 |

It peaks at `2` brackets at `0.3778` and falls from there, and the fall is composition: the tail from
`10` brackets on rests on a single object.

**The two regimes do not agree on this curve, and the opaque one is the higher of the two.** That
reverses what the previous revision reported. Under the transparent rules a bracketed leaf is still
a leaf, so `(a) * (b + c)` has one compound numerator factor and `factor_structure` stays invisible;
under the opaque rules the bracket is what makes the leaf a compound factor. The two curves differ
at exactly the bracket counts `1`, `2`, `3` and `4`, and the opaque rate is at least the transparent
one at every count. **Opacity is not uniformly a loss.** For six of the seven properties it is total
loss at the first bracket; for the seventh it is a gain, and the gain is the same mechanism as the
loss seen from the other side.

The decisive check does not average anything at all: **of the `17500` per-property cell curves —
`7` properties in each of `1250` cells in each of `2` regimes — exactly `100` ever rise**, all of
them `factor_structure` under the opaque rules. The previous revision reported `0`. Those `100` are
the four rising writings under all `25` worlds, and they are more than the `72` cells whose manifest
*count* rises. In the other `28` the writing that first shows `factor_structure` shows *fewer*
properties than a lower-bracket writing already did — `distributive_law` factored under `G01` shows
`degree` and `roots` at zero brackets and only `factor_structure` at one — so the maximum falls
where the reachable set gains. That gap is the reason this reading exists.

The two ways of reading that same question — the set a writing at that count *shows*, and the set
padding carries forward — give the same `100` on this grid, because no property here ever goes off
again once it has come on. That coincidence is an observation and not a law, so the padded reading
is the one the code takes, and a hand-built record is what pins it in the tests.

### The witness: the rules admit a rise, and admit no peak

A monotone corpus result would be ambiguous between "the rules forbid it" and "this mathematics has
none of it". Four objects are declared **outside** the 0038 corpus to settle that. They are not
evidence about mathematics, they are never pooled with the corpus, and they now answer a question
the corpus answers too.

```text
witness_product_of_pairs     (a * b) * (c * d)
witness_product_of_sums      (a + b) * (c + d)
witness_triple_product       (a * b) * (c * d) * e
witness_quotient_of_pairs    (a * b) * (c * d) / f
```

Across the `200` witness cells, `50` rise somewhere and **`0` carry a peak**. All `50` risers are in
the **opaque** regime, `25` in `witness_product_of_pairs` and `25` in `witness_triple_product`, and
all of them rise once and stay up. `13` of the `100` opaque witness cells changed when padding was
admitted.

| reading | constant | non-increasing | non-decreasing | non-monotone | cells that rise | cells with a peak |
| --- | --- | --- | --- | --- | --- | --- |
| attainable, padding admitted | 50 | 0 | 50 | 0 | 50 | 0 |
| unpadded attainable | 37 | 13 | 50 | 0 | 50 | 0 |
| pattern mean | 25 | 13 | 50 | 12 | 50 | 0 |

**The unpadded column no longer peaks either**, and that is the round 2 correction reaching back
into round 1: the peak the first revision published needed both restrictions at once. With leaves
enumerated, the missing three-bracket writing exists, and the fall that made the peak is gone before
padding is ever applied.

### The argmax of every curve A curve

The methods paragraph promises the argmax for every curve, so here it is for every curve, and not
only for the one the prose happened to discuss.

| curve | argmax at | value | monotone |
| --- | --- | --- | --- |
| transparent pooled mean, attainable, unpadded | 12 brackets | 3.9286 | non-monotone |
| opaque pooled mean | 0 brackets | 2.0755 | non-monotone |
| opaque pooled attainable | 0 brackets | 2.0755 | non-monotone |
| opaque pooled unpadded attainable | 0 brackets | 2.0755 | non-monotone |
| transparent degree | 10 brackets | 1.0000 | non-monotone |
| transparent leading_coefficient | 10 brackets | 1.0000 | non-monotone |
| transparent constant_term | 12 brackets | 0.9286 | non-monotone |
| transparent roots | 1 bracket | 0.4165 | non-monotone |
| transparent factor_structure | 3 brackets | 0.2994 | non-monotone |
| transparent sign_structure | 10 brackets | 1.0000 | non-monotone |
| transparent even_parity | 5 brackets | 1.0000 | non-monotone |
| opaque factor_structure | 2 brackets | 0.3778 | non-monotone |
| opaque degree | 0 brackets | 0.9187 | non-increasing |
| opaque leading_coefficient | 0 brackets | 0.4878 | non-increasing |
| opaque constant_term | 0 brackets | 0.4959 | non-increasing |
| opaque roots | 0 brackets | 0.3577 | non-increasing |
| opaque sign_structure | 0 brackets | 0.6373 | non-increasing |
| opaque even_parity | 0 brackets | 0.8095 | non-increasing |

## Curve B: word length against semantic diversity

### The word family, and the null model that decides how it may be read

A word of length `L` is `L` operators drawn from `+ - * /` with `L + 1` **distinct** operands. The
operands are distinct on purpose: a repeated operand would add collapse that comes from the
operands rather than from the operators, and curve B is about what the operators force.

T6 is the null model and it is the single most likely way this card could have manufactured a turn.
A word whose operator support is `s` can be parsed at most `s!` ways by the 24 strict grammars,
because parsing depends only on the precedence order restricted to the operators that occur, and
the tied control adds at most one more. When the word is short the Catalan number binds instead.
So the ceiling on distinct parses is

```text
ceiling(s, L) = min(s! + 1, C(L))
```

and it does **not** grow with length once the word is long enough. Every count below is therefore
reported inside a support stratum and never pooled across them, and the ceiling is printed next to
the count so that a curve merely walking up toward it cannot be read as a discovery.

**What this sweep does not produce, and why it cannot change the answer.** It does not produce words
longer than `9`, and it does not produce words that repeat an operand. Length is a cost limit and it
is answered by the ceiling: inside a stratum the count cannot climb past `s! + 1`, so the shape
available past the limit is saturation and not a turn. Repeated operands are a different question —
they would add collapse the operators did not force — and the family is declared for that reason
rather than because it is the only one.

The sweep is exhaustive over all `4 ** L` words for `L` from `1` to `7`, which is `21844` words. The
word count quadruples per step and each word costs a sympy `simplify` per distinct parse. Past it,
a seeded sample of `256` words at each of lengths `8` and `9` is reported separately, because a
sample and a census are not the same kind of observation and because a uniform sample of long words
lands almost entirely in the large-support strata.

### The tables

Operator support `1`. Every grammar agrees on a word built from one operator, so this stratum is the
control and it is flat everywhere.

| length | words | mean distinct ASTs | mean classes | T6 ceiling | collapse ratio |
| --- | --- | --- | --- | --- | --- |
| 1 | 4 | 1.0000 | 1.0000 | 1 | 1.0000 |
| 2 | 4 | 1.0000 | 1.0000 | 2 | 1.0000 |
| 3 | 4 | 1.0000 | 1.0000 | 2 | 1.0000 |
| 4 | 4 | 1.0000 | 1.0000 | 2 | 1.0000 |
| 5 | 4 | 1.0000 | 1.0000 | 2 | 1.0000 |
| 6 | 4 | 1.0000 | 1.0000 | 2 | 1.0000 |
| 7 | 4 | 1.0000 | 1.0000 | 2 | 1.0000 |

Operator support `2`.

| length | words | mean distinct ASTs | mean classes | T6 ceiling | collapse ratio |
| --- | --- | --- | --- | --- | --- |
| 2 | 12 | 2.0000 | 1.8333 | 2 | 0.9167 |
| 3 | 36 | 2.1111 | 1.8889 | 3 | 0.9074 |
| 4 | 84 | 2.1905 | 1.9286 | 3 | 0.9008 |
| 5 | 180 | 2.2444 | 1.9556 | 3 | 0.8963 |
| 6 | 372 | 2.2796 | 1.9731 | 3 | 0.8934 |
| 7 | 756 | 2.3016 | 1.9841 | 3 | 0.8915 |

Operator support `3`.

| length | words | mean distinct ASTs | mean classes | T6 ceiling | collapse ratio |
| --- | --- | --- | --- | --- | --- |
| 3 | 24 | 5.0000 | 4.1667 | 5 | 0.8333 |
| 4 | 144 | 5.3333 | 4.4722 | 7 | 0.8390 |
| 5 | 600 | 5.5867 | 4.7067 | 7 | 0.8435 |
| 6 | 2160 | 5.7981 | 4.9019 | 7 | 0.8469 |
| 7 | 7224 | 5.9779 | 5.0670 | 7 | 0.8493 |

Operator support `4`.

| length | words | mean distinct ASTs | mean classes | T6 ceiling | collapse ratio |
| --- | --- | --- | --- | --- | --- |
| 4 | 24 | 14.0000 | 10.7500 | 14 | 0.7679 |
| 5 | 240 | 15.4167 | 12.0500 | 25 | 0.7812 |
| 6 | 1560 | 16.4590 | 13.1115 | 25 | 0.7961 |
| 7 | 8400 | 17.3362 | 14.0486 | 25 | 0.8098 |

### The verdicts, with the argmax of every curve

| stratum | classes curve | first differences | argmax | still moving at the end |
| --- | --- | --- | --- | --- |
| support 1 | constant | 0.0000 throughout | length 1, 1.0000 | no |
| support 2 | non-decreasing | 0.0556 0.0397 0.0270 0.0176 0.0110 | length 7, 1.9841 | yes |
| support 3 | non-decreasing | 0.3056 0.2344 0.1952 0.1651 | length 7, 5.0670 | yes |
| support 4 | non-decreasing | 1.3000 1.0615 0.9370 | length 7, 14.0486 | yes |

| stratum | ASTs argmax | collapse argmax | ceiling-fraction argmax |
| --- | --- | --- | --- |
| support 1 | length 1, 1.0000 | length 1, 1.0000 | length 1, 1.0000 |
| support 2 | length 7, 2.3016 | length 2, 0.9167 | length 2, 0.9167 |
| support 3 | length 7, 5.9779 | length 7, 0.8493 | length 3, 0.8333 |
| support 4 | length 7, 17.3362 | length 7, 0.8098 | length 4, 0.7679 |

No stratum turns. Three of the four are still rising when the exhaustive sweep stops, and the
argmax of each is its last point, which is the honest way to say that the sweep was stopped by cost
and not by the curve.

The first differences shrink in every moving stratum, which is what saturation looks like: the
class count is climbing toward a ceiling that does not move. At support `2` it stands at `1.9841`
against a ceiling of `3`, at support `3` at `5.0670` against `7`, and at support `4` at `14.0486`
against `25`.

### A second apparent turn, and a second cause

The class count expressed as a *fraction of the T6 ceiling* is non-monotone in every stratum above
support `1`, and each of those curves has exactly one trough.

| stratum | ceiling-fraction curve | trough at | rise after |
| --- | --- | --- | --- |
| support 2 | 0.9167 0.6296 0.6429 0.6519 0.6577 0.6614 | 3 | 0.0317 |
| support 3 | 0.8333 0.6389 0.6724 0.7003 0.7239 | 4 | 0.0850 |
| support 4 | 0.7679 0.4820 0.5245 0.5619 | 5 | 0.0799 |

Every trough sits at the length where the Catalan bound gives way to the support bound:

```text
support 2   C(2) = 2   ->   2! + 1 = 3
support 3   C(3) = 5   ->   3! + 1 = 7
support 4   C(4) = 14  ->   4! + 1 = 25
```

The numerator moves smoothly and the denominator jumps, so the ratio dips once and then resumes
climbing. That is a second kind of false turn, after composition in curve A: **a turn in a
normalised quantity whose normaliser is not continuous.** Neither is in the thing being observed.

### The collapse ratio, which is why nothing here may be pooled

The interesting quantity is not how many meanings there are but how much of the parse diversity
survives sympy: the **mean of `classes / distinct ASTs` per word**, where `1.0000` would be no
collapse at all. It is not the quotient of the two means printed beside it — at support `2`,
length `3` those give `1.8889 / 2.1111 = 0.8947` while the published figure is `0.9074`.

| stratum | collapse curve | verdict |
| --- | --- | --- |
| support 1 | 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 1.0000 | constant |
| support 2 | 0.9167 0.9074 0.9008 0.8963 0.8934 0.8915 | non-increasing |
| support 3 | 0.8333 0.8390 0.8435 0.8469 0.8493 | non-decreasing |
| support 4 | 0.7679 0.7812 0.7961 0.8098 | non-decreasing |

**The strata disagree in sign.** At support `2` the collapse strengthens with length; at supports
`3` and `4` it weakens. A pooled collapse curve would be a weighted average of two opposite trends
whose weights are decided by how many words of each support exist at each length, which is a fact
about `4 ** L` and not about mathematics. This is the clearest single reason the null model is not
a formality here.

### Past the exhaustive limit

The seeded sample of `256` words at each of lengths `8` and `9` splits very unevenly across strata,
and that is reported rather than smoothed. Support `1` receives no sampled word at all, since a
word of length `8` using one operator has probability `4` in `65536`.

| stratum | length | words | mean distinct ASTs | mean classes | collapse ratio |
| --- | --- | --- | --- | --- | --- |
| support 2 | 8 | 7 | 2.4286 | 2.0000 | 0.8571 |
| support 2 | 9 | 3 | 2.0000 | 2.0000 | 1.0000 |
| support 3 | 8 | 85 | 6.1294 | 5.2353 | 0.8535 |
| support 3 | 9 | 77 | 6.2338 | 5.2727 | 0.8494 |
| support 4 | 8 | 164 | 17.9329 | 14.6159 | 0.8169 |
| support 4 | 9 | 176 | 19.1989 | 15.8182 | 0.8233 |

At supports `3` and `4` the class count continues upward, exactly as the exhaustive curve was
heading. At support `2` the sampled rows hold `7` and `3` words, and **no turn is named from them**:
a sequence of three words is not a curve. Their only content is that nothing beyond the limit
contradicts the exhaustive shape.

## Curve C: the width of the convention axis against semantic yield

### What width means here

The convention axis of 0030 is precedence plus associativity. Its two ends are the Generation 1
registry of `24` strict precedence orders, all left-associative, and the extended registry of `384`
in which every operator may bind either way. What sits between them has not been swept before, and
it is a real axis rather than an interpolation: it says **which operators a culture had made up its
mind about**.

| width | operators freed | grammars |
| --- | --- | --- |
| 0 | none | 24 |
| 1 | + | 48 |
| 2 | + - | 96 |
| 3 | + - * | 192 |
| 4 | + - * / | 384 |

**What this sweep does not produce, and why it cannot change the answer.** It does not produce words
longer than `8`, and it does not produce orders of freeing the operators other than the declared
one. Length is answered by the set inclusion below, which holds word by word and does not depend on
which words are in the sweep. The order is answered by reporting every single-operator widening on
its own, where the declared order cannot reach it.

The sweep is exhaustive over all `4 ** L` words for `L` from `1` to `6`, which is `5460` words; each
of those is parsed under up to `384` grammars before the sympy step, and that is the computational
limit. Past it, a seeded sample of `256` words at each of lengths `7` and `8`, reported separately.

### The result that forecloses a turn, before any number is looked at

A wider axis is a **superset** of grammars, and a superset of grammars applied to one word produces
a superset of meanings. So the class count is non-decreasing in the width by construction, and no
widening can ever give strictly less than a narrower one.

The sweep checks this rather than assuming it, and checks it as a **set inclusion** and not as a
comparison of counts, which is the stronger test: for every word it compares the actual class sets
at each pair of widths in the chain, and the base set against each single-operator widening. Over
`5972` words that is `47776` inclusions, and **`0` of them lost a meaning.**

This settles what the card asked of 0030, and that experiment's decay from `100` per cent recovered
at `k = 2` to `10.946` per cent at `k = 6` is not a turn and cannot be one. It is a ratio whose
denominator, the number of Catalan trees no grammar reaches, grows exponentially with the word
length, while its numerator is bounded by the size of the registry.

### The width curves

| stratum | words | width 0 | width 1 | width 2 | width 3 | width 4 |
| --- | --- | --- | --- | --- | --- | --- |
| support 1 | 24 | 1.0000 | 1.0000 | 1.2083 | 1.2083 | 1.4167 |
| support 2 | 684 | 1.9561 | 1.9561 | 2.6199 | 2.6199 | 3.4357 |
| support 3 | 2928 | 4.8347 | 4.8347 | 6.3402 | 6.3402 | 8.1530 |
| support 4 | 1824 | 12.9408 | 12.9408 | 15.6798 | 15.6798 | 18.6886 |

| stratum | first differences | verdict | argmax | turning points |
| --- | --- | --- | --- | --- |
| support 1 | 0.0000 0.2083 0.0000 0.2083 | non-decreasing | width 4, 1.4167 | none |
| support 2 | 0.0000 0.6637 0.0000 0.8158 | non-decreasing | width 4, 3.4357 | none |
| support 3 | 0.0000 1.5055 0.0000 1.8128 | non-decreasing | width 4, 8.1530 | none |
| support 4 | 0.0000 2.7390 0.0000 3.0088 | non-decreasing | width 4, 18.6886 | none |

Every curve is **non-decreasing**, none has a turning point, and every one of them is still rising
at width `4`. That last phrase means something different here from what it means in curve B: the
axis has four operators and there is no width `5`, so the sweep covers the *whole* range of this
parameter. It stopped because the axis ran out, not because the budget did.

The shape is a staircase. The steps at widths `1` and `3` are flat to the last decimal in every
stratum, and that is the next finding.

### Two of the four dimensions are exactly inert

The width curve is a staircase, and its flat steps are not a rounding artefact. Freeing the
associativity of `+` doubles the registry from `24` grammars to `48` and yields **zero** new
meanings; freeing `*` does the same. Only `-` and `/` are live.

| stratum | freeing + | freeing - | freeing * | freeing / |
| --- | --- | --- | --- | --- |
| support 1 | 0.0000 in 0 words | 0.2083 in 5 words | 0.0000 in 0 words | 0.2083 in 5 words |
| support 2 | 0.0000 in 0 words | 0.6637 in 282 words | 0.0000 in 0 words | 0.6637 in 282 words |
| support 3 | 0.0000 in 0 words | 1.5055 in 1356 words | 0.0000 in 0 words | 1.5171 in 1356 words |
| support 4 | 0.0000 in 0 words | 2.7390 in 720 words | 0.0000 in 0 words | 2.7544 in 720 words |

The mean new classes each live widening buys, and the number of words that gain anything at all.
`-` and `/` are near-mirror images: the same number of words gains from each in every stratum, and
their mean yields differ in the **second** decimal — `1.5055` against `1.5171` at support `3`, and
`2.7390` against `2.7544` at support `4`.

The reason is immediate once stated. In a strict precedence order every operator sits alone on its
level, so freeing one operator reassociates only its own runs, and reassociating a run of `+` or of
`*` is an identity in exact rational arithmetic. `a + (b + c)` and `(a + b) + c` are the same object
with the same excluded points, so they collapse to the same semantic key. Subtraction and division
are not associative, so their runs really do split.

This is a sharper form of the ROADMAP T30 remark that associativity bought "50 percent more syntax
with zero new mathematics". Half of the axis is not merely low-yield; it is provably empty, and a
router that widened along it would be paying for `192` grammars it can never learn anything from.

### The yield per grammar added, which is where the decay actually lives

| stratum | 0 to 1, +48 grammars | 1 to 2, +48 grammars | 2 to 3, +96 grammars | 3 to 4, +192 grammars |
| --- | --- | --- | --- | --- |
| support 1 | 0.000000 | 0.004340 | 0.000000 | 0.001085 |
| support 2 | 0.000000 | 0.013828 | 0.000000 | 0.004249 |
| support 3 | 0.000000 | 0.031364 | 0.000000 | 0.009442 |
| support 4 | 0.000000 | 0.057063 | 0.000000 | 0.015671 |

The second live widening adds `192` grammars against the first one's `48`. In absolute terms it
buys slightly **more** meaning — `3.0088` new classes against `2.7390` at support `4` — and per
grammar added it buys roughly a quarter as much, `0.015671` against `0.057063`. The raw count rises
and the price per grammar falls, which is exactly the pair a single ratio would have hidden.

That is a decay in **yield**, and it is exactly the kind of quantity the 0030 ratio was observing.
Naming it a turn would be reading a falling derivative as a falling function.

### Past the exhaustive limit

| stratum | sampled words | width 0 | width 1 | width 2 | width 3 | width 4 |
| --- | --- | --- | --- | --- | --- | --- |
| support 1 | 0 | none | none | none | none | none |
| support 2 | 19 | 2.0000 | 2.0000 | 3.0526 | 3.0526 | 3.8947 |
| support 3 | 217 | 4.9862 | 4.9862 | 7.2442 | 7.2442 | 10.2304 |
| support 4 | 276 | 14.4239 | 14.4239 | 19.3949 | 19.3949 | 25.3804 |

The `512` sampled words at lengths `7` and `8` split `0`, `19`, `217` and `276` across the four
strata. Every sampled stratum keeps the same staircase, flat at widths `1` and `3` and rising at
`2` and `4`, so nothing past the exhaustive limit contradicts the shape. Support `1` receives no
sampled word, and the support `2` row rests on `19` words, so no verdict is taken from either.

## Interpretation

**A restriction you have not declared is worse than a bound you have argued for, and this card now
has one of each.** Round 1's bound was written down, defended at length, and checked by a function
whose output was the counter-evidence; every part of the machinery worked except the reading of it.
Round 2's restriction was in a single `isinstance` test, contradicted by the docstring two lines
above it and by the report's own description of the mechanism. The first is the more instructive and
the second is the more dangerous, because nothing about it looked like a decision. The rule that
catches both is the same: **state, at the point where the answer is read, which writings the
enumeration produced and which it did not.**

**The corpus negative result is gone, and what replaced it is more interesting.** "The mathematics
of the `34` named identities contains no object whose visibility a bracket improves" was a
comfortable sentence and it was false. Four of the `50` named writings improve under the opaque
rules, in `72` of the `1250` cells, and one of them — `chain_rule`, `dfg * dg` — is a product of two
bare leaves. The property that switches on is `factor_structure` in every case, and ground truth
agrees the object has two factors, so this is not a rule defect.

**Opacity is not uniformly a loss.** Six of the seven 0038 rules collapse to zero at the first
opaque bracket; the seventh is strictly *more* reachable under the opaque rules than under the
transparent ones, at every bracket count where the two differ. It is the same mechanism read from
the other side: a bracket that hides what is inside a factor is also what makes the factor countable
as a factor. The previous revision reported the two regimes as agreeing exactly on this curve, which
was an artefact of not enumerating the writings that separate them.

**The one turn this experiment can still name is composition, and it is the load-bearing result.**
Two of the three sweeps produce a pooled curve that turns and a within-cell curve that does not. In
curve A the gap is total: the pooled opaque curves peak at `2` brackets and not one of the `1250`
opaque cells underneath them peaks at all. The cause is not subtle and it is not rare — the
population changes
with the parameter, because a small object has no writing with many brackets and a short word has no
room for many operators. The fix is cheap: take the first difference inside a cell and only then
average. Any card that plots an aggregate against a parameter whose population moves with it should
publish the paired difference beside the pooled curve.

**Cells are not objects, and a sample column that counts cells hides its own thinness.** Curve A's
tail at `14` brackets holds `14` cells and `2` objects. The `25`-world multiplier is what makes the
difference, and it is precisely the tail that carries the rise the pooled transparent curve shows
after its trough. Every curve in this experiment publishes both columns, and the discipline audit
takes its thin-point verdict off the object column.

**Under the 0038 transparent rules, visibility is a function of the intended tree alone.** That
follows from the numbers rather than from the code: `0` rises and `0` falls in `3275` paired
within-cell steps, and the manifest set of a transparent cell is identical at every bracket count in
`1250` of `1250` cells. It sharpens 0038 in a way 0038 did not state. The per-world visibility
differences that experiment reports come entirely from *which writing a world chooses* and never
from how many brackets that writing carries.

**Under the opaque rules the first bracket is nearly a total loss, and the next two can buy one
property back.** The first costs `1.9715` of the `2.0755` properties visible at zero brackets on the
mean reading, and `1.9057` on the attainable reading. The second bracket then raises the attainable
curve in `68` cells and the third in `4` more, after which every paired within-cell step is exactly
zero. The 0038 sentence "a bracketed factor stops being inspectable" is the whole effect for six
rules and the exact opposite of the effect for the seventh.

**A peak is impossible, and the reason is structural rather than empirical.** An attainable curve is
a running maximum wherever a bracket exists to double, so it cannot fall after it has risen; the
only fall it admits is the step out of a bracket-free writing, which no rise can precede. That is
why `cells_with_a_peak` is `0` in every reading of every cell in both grids, and why the padded
curve of a cell has the shape `fall, then rise, then flat` and never the shape the tax analogy
names.

**Curve B saturates rather than turns, and it must.** T6 fixes a ceiling per stratum that does not
grow with length: a word whose operator support is `s` can be parsed at most `s!` ways by the 24
strict grammars, plus at most one more by the tied control, so the ceiling is `s! + 1` once the word
is long enough for that many trees to exist. Inside every stratum the class count climbs toward that
ceiling and is still climbing at length `7`. It cannot climb past it, so the shape available to this
curve is saturation and not a turn, and the honest report of it is that the curve was still rising
when the exhaustive sweep stopped.

**The collapse ratio moves in opposite directions in different strata, and that is the concrete
reason nothing here may be pooled.** At support `2` the fraction of parse diversity that survives
sympy *falls* with length; at supports `3` and `4` it *rises*. A pooled collapse curve would be an
average of two opposite trends weighted by how many words of each support happen to exist at each
length, which is a fact about `4 ** length` and not about mathematics.

**Curve C cannot turn, and this is provable rather than observed.** A wider convention axis is a
*superset* of grammars, and a superset of grammars gives a superset of meanings, so the class count
is non-decreasing in the width by construction. The sweep checks it as a set inclusion rather than
as a comparison of counts, and no widening anywhere lost a meaning. The 0030 decay from `100` per
cent to `10.946` per cent therefore cannot be a turn: it is a ratio whose denominator, the number of
unreachable Catalan trees, grows exponentially while its numerator is bounded by the size of the
registry.

**The sharper finding of curve C is that two of its four dimensions are exactly inert.** Freeing the
associativity of `+` doubles the registry from `24` grammars to `48` and yields **zero** new
meanings, in every stratum and in every word. Freeing `*` does the same. The reason is immediate
once stated: in a strict precedence order each operator sits alone on its level, so freeing one
reassociates only its own runs, and reassociating a run of `+` or of `*` is an identity in exact
rational arithmetic. Only `-` and `/` are live. This is a sharper form of the ROADMAP T30 remark
that associativity added "50 percent more syntax with zero new mathematics": half of the axis is not
merely low-yield, it is provably empty, and a router that widened along it would pay for `192`
grammars it can never learn anything from.

## Limits

Every bound below exists for a reason that is named, with what was checked beyond it.

- **Curve A enumerates bracket PATTERNS and not bracket subsets.** The writings it does not produce
  are those with a bracket inside a bracket. Such a writing has the manifest set of its pattern —
  checked over every one of `28968` bracket subsets of the `39` writings small enough to enumerate
  them all, and over `4000` arbitrarily nested writings drawn from the whole grid, `3487` of which
  no subset enumeration reaches — and a bracket count at least its pattern's minimum, where the
  running maximum has already carried the value. `0` disagreements.
- **The padding carry does not apply out of a bracket-free writing.** At `0` brackets there is
  nothing to double, so `attainable(0)` is not carried into `attainable(1)`, which is why the
  collapse at the first opaque bracket survives.
- **Past a cell's largest pattern the curve is not tabulated.** It is constant there, because every
  writing beyond it repeats a pattern already counted at a count the running maximum has reached.
  The tabulated axis has no gap in `2500` of `2500` cells.
- **Word length `7` exhaustive (curve B).** The word count is `4 ** length` and each word costs a
  sympy `simplify` per distinct parse. Past the limit, a seeded sample of `256` words at lengths `8`
  and `9`. Those samples are reported separately and no verdict is taken from them, because a
  uniform sample of long words lands almost entirely in the large-support strata: at support `2` the
  sampled rows hold `7` and `3` words.
- **Word length `6` exhaustive (curve C).** Each word is parsed under up to `384` grammars before
  the sympy step. Past the limit, a seeded sample of `256` words at lengths `7` and `8`, reported
  separately for the same reason.
- **The published scale of curves B and C is not asserted by the default test run.** It takes about
  `30` minutes and the suite cannot afford it. What the default run does assert is stated exactly in
  the Validation section below, and the published scale is asserted against the same literal tables
  when `PARSEATLAS_FULL_SWEEP=1` is set.
- **The corpus of curve A is hand-chosen.** It is the 0038 corpus, which is the 0037 named-law
  corpus plus one calibration quadratic. It is a corpus of what mathematics named, not a sample of
  mathematics, and every count in curve A is relative to it.
- **Every curve A curve has a tail point resting on fewer than `3` distinct objects.** The audit
  lists them all rather than hiding them, and no verdict in this report is taken from a tail point;
  the within-cell verdicts, which are where the results live, do not average across objects at all.
- **Visibility is whatever the 0038 declared rules say it is.** A different rule set would move
  every number here, and the two regimes already disagree on this same data: constant under
  `transparent`, and `844 / 334 / 72` under `opaque`. Neither is more correct; they are different
  questions.
- **The `72` risers are a fact about the 0038 `factor_structure` rule as much as about the
  mathematics.** The rule asks that at least two numerator factors not be leaf tokens, and an opaque
  bracket is what makes a leaf stop being one. A rule that counted *syntactic* compounds instead
  would report `0` risers, which is the withdrawn revision's answer arrived at honestly.
- **The witness objects are constructed.** They establish that the rules admit a rise. They say
  nothing about how often it occurs, and they are never pooled with the corpus.
- **The domain component of the semantic key is inert (`NF-2026-00005`).** The project key is
  `(canonical, domain, excluded points)`, but `canonical.py` always writes the literal `R` into
  `domain`, so the operative discrimination in curves B and C has two components and not three.
- **The word family of curves B and C uses distinct operands.** Repeating an operand would add
  collapse that comes from the operands rather than from the operators, and the numbers would
  differ; the family is declared for that reason and not because it is the only one.
- **The order in which curve C frees operators is declared.** It is `+`, `-`, `*`, `/`, and a
  different order gives a different width curve, which is exactly why every single-operator
  widening is also reported on its own.
- **Nothing here observes reading.** "A bracket is worth nothing under the transparent rules" is a
  statement about the 0038 shape rules and not a claim that brackets are free to a human reader.

## Classification of evidence

- Every curve, table, argmax, first difference and monotonicity verdict — **OBSERVATION**, on this
  corpus, this word family and these rules.
- The audits: `981344` writings reparsing to the intended tree, `1250` surface mirrors agreeing with
  0038, `28968` bracket subsets reducing to their patterns, `4000` nested writings agreeing with
  theirs — **VERIFIED PROPERTIES** on this grid, not a proof for every tree.
- "The pooled bracket curve turns and no cell in it peaks" — **OBSERVATION**, and it is the
  load-bearing one.
- "An attainable curve cannot fall after it has risen, so no cell of curve A can carry a peak" —
  **JUSTIFIED**: padding an existing bracket raises the count by one and leaves the manifest set
  untouched, so the curve is a running maximum wherever a bracket exists to double, and the carry
  was also checked directly on every position of a declared writing.
- "The rules admit a rise and then a fall" — **WITHDRAWN** (round 1). It was an artefact of the
  enumeration bound, and `((a * b)) * (c * d)` refutes it outright.
- "No cell of the 34-object corpus ever rises" — **WITHDRAWN** (round 2). It was an artefact of
  enumerating bracket sites at compound nodes only, and `(a) * (b + c)` refutes it outright.
- "`72` of the `1250` opaque corpus cells rise" — **OBSERVATION** on this corpus under these rules.
- "The opaque rules admit a rise" — **OBSERVATION**, on the corpus and on constructed witnesses
  both. It is an existence result, and the corpus count carries a frequency only for this corpus.
- "The opaque rules make `factor_structure` more reachable than the transparent rules do" —
  **OBSERVATION**, and the mechanism is stated: an opaque bracket makes an operand a non-atom.
- "Widening the convention axis can never reduce the meanings available" — **JUSTIFIED**: a superset
  of grammars gives a superset of meanings, and the inclusion was also checked directly on every
  widening in the sweep.
- "Freeing `+` or `*` yields no new meanings" — **JUSTIFIED**: reassociating a run of `+` or of `*`
  is an identity in exact rational arithmetic, and the sweep observed it in every word.
- "Brackets do not help a reader" — **NOT CLAIMED**. Only manifestness under declared shape rules
  was observed.

## Validation

```text
python -m pytest -q tests/test_turning_points.py                        88 passed, 2 skipped
python -m pytest -q                                                     1198 passed, 2 skipped
PARSEATLAS_FULL_SWEEP=1 python -m pytest -q tests/test_turning_points.py 90 passed
```

The suite total includes the tests of the other cards in the same wave; the line above that belongs
to this card is the first one. The third line is the published scale of curves B and C, which the
default run skips.

### What is pinned, and at which scale

- **Curve A is pinned in full by the default run.** Every pooled curve as a sequence, both sample
  columns, every paired first difference, every within-cell verdict in all three readings, the
  named risers with their objects and their property, every property stratum with its cell and
  object denominators, the witness sweep in both readings, and both withdrawn blocks as data — the
  round 1 `0 1 0` beside the corrected `0 1 1`, and the round 2 `[0, 0] constant` beside the
  corrected `[0, 1] non-decreasing`.
- **The census is pinned as a census.** Its size — `156475` patterns and `981344` legal writings —
  the gap-free axis of every cell, and the three completeness audits.
- **Curve B's published tables are written down in full in the test file, and the default run checks
  a genuine prefix of them value by value.** A row of curve B for a given `(support, length)` does
  not depend on where the sweep stops, so the affordable sweep to length `5` reproduces the
  published rows for lengths `1` to `5` exactly. Lengths `6` and `7` are asserted against the same
  literals under `PARSEATLAS_FULL_SWEEP=1`.
- **Curve C's published width curves are means over the whole stratum, so a shorter sweep is not a
  prefix of them.** Both scales are therefore pinned separately and each is labelled: the sweep to
  length `4` over `16`, `132`, `168` and `24` words in the default run, and the published sweep to
  length `6` over `24`, `684`, `2928` and `1824` words under `PARSEATLAS_FULL_SWEEP=1`, where the
  live widenings `1.5055` against `1.5171` and `2.7390` against `2.7544` are pinned too.

What is pinned is the shape and not only the extremum: each swept curve as a sequence, the sample
size and the object count at every parameter value, the monotonicity verdict of every curve
separately from its values, every turning point with its parameter and the fall after it, the strata
and their sizes, and the fact that no rate anywhere in the report is computed across strata.

### The discipline audit

The rule that no rate may be pooled across strata is checked mechanically rather than by reading.
The audit walks the whole report, finds every curve record, and reports what it found.

```text
curves found                                          50
curves without a named stratum                         0
curves without per-point sample sizes                  0
curves carrying a distinct-object column              50
curves with a point resting on fewer than 3 OBJECTS   30
```

All `30` thin curves are curve A curves, corpus and witness together, and their thin points
are the `1`-object and `2`-object tails listed above. A curve cannot even be constructed without
naming its stratum: the constructor raises rather than defaulting to an empty one, which is cheaper
than finding the omission later.

### The mutation check

The repair is only worth as much as the tests that hold it, so the ways of getting either withdrawn
finding back were re-introduced one at a time, on an isolated copy of the tree and never in the
working one, and each was run against the suite. The first is the round 2 defect exactly as it was
shipped.

```text
bracket_sites_visits_compound_nodes_only             KILLED
no_carry_at_all_the_round_one_reading                KILLED
carry_out_of_a_bracket_free_writing                  KILLED
verdicts_taken_from_the_unpadded_curve               KILLED
property_strata_ignore_padding                       KILLED
per_property_reading_ignores_padding                 KILLED
object_column_counts_cells                           KILLED
thin_point_verdict_counts_cells                      KILLED
patterns_are_not_reduced_to_the_outermost_brackets   KILLED
illegal_patterns_are_not_filtered_out                KILLED

mutants 10   killed 10   survivors 0
```

The first pass left one survivor, `per_property_reading_ignores_padding`, and the reason is worth
recording: on this grid the two readings of that curve coincide, so no assertion about the corpus
could separate them. It is killed now by a hand-built record in which they differ, which is the
right control for a contract the data does not happen to exercise.

The isolated copy is forced onto the import path and the resolution is asserted before every run.
An earlier attempt at this check reported survivors and was wrong: the project is installed into the
interpreter, so a copy that is only `cd`-ed into silently tests the real tree. That is the same
class of error as the findings this report withdraws — a control that was never exercised — and it
is recorded here for the same reason.

### Concurrency, observed, and the two payloads disagree

```text
detected cores                                   16
workers                                          15
writing pattern census,  50 items    sequential  30.9148 s   parallel  18.0660 s   speedup 1.7112
word record,            256 items    sequential  10.7898 s   parallel   2.8474 s   speedup 3.7894
```

The unit of work in curve A is now a whole writing's pattern census rather than a single cell, and
that changes the decision: a census is up to `77336` patterns of seven shape rules each, so `50` of
them are worth a process pool where `250` single cells were not. The floor is not assumed either —
it is where the crossover was observed, on prefixes of the same `50` writings:

```text
items    2    sequential   0.1336 s    parallel   0.5793 s    speedup 0.2307    sequential
items    4    sequential   0.0491 s    parallel   0.6664 s    speedup 0.0736    sequential
items    6    sequential   0.1035 s    parallel   0.8045 s    speedup 0.1286    sequential
items    8    sequential   0.1103 s    parallel   0.9393 s    speedup 0.1174    sequential
items   12    sequential   0.3282 s    parallel   1.2023 s    speedup 0.2730    sequential
items   16    sequential  13.0215 s    parallel  13.5819 s    speedup 0.9587    sequential
items   24    sequential  29.4017 s    parallel  17.9198 s    speedup 1.6407    PARALLEL
items   32    sequential  30.9999 s    parallel  18.1291 s    speedup 1.7100    PARALLEL
items   50    sequential  30.9131 s    parallel  18.8678 s    speedup 1.6384    PARALLEL
```

The crossover falls between `16` and `24`, and the floor in the module is `24`. The table also shows
why a prefix observation of a skewed workload must be read carefully: the jump from `0.3282` to
`13.0215` seconds between `12` and `16` items is the sixteenth writing entering the prefix, which is
`binomial_cube` expanded at `64274` patterns, and the jump at `24` is `circle` general at `77336`.
Two of the `50` writings hold `141610` of the `156475` patterns, so the speedup is bounded by the
largest single item and not by the core count, which is why `1.7112` and not `15`. The word records
are uniform and reach `3.7894`.

The two payloads therefore sit on opposite sides of any single crossover, and the module carries two
measured floors rather than one constant. Both paths produce identical output, which is asserted by
test rather than assumed, for the pattern censuses and for the word records.

### Reproducing the run

```text
python -c "import json; from parseatlas import turning_points as tp; print(json.dumps(tp.turning_points_report(length_exhaustive_to=7, length_sampled_to=9, axis_exhaustive_to=6, axis_sampled_to=8))[:200])"
```

The published run takes `1231.91` seconds on this host: `18.88` for curve A, `64.21` for its
reparse census, `3.08` for its completeness audit, `777.36` for curve B and
`368.36` for curve C.
