# ParseAtlas experiment 0049: the Pareto atlas of equivalent writings

## The fourth question, first

The owner's sharpest question was how many frontier points exist that the conventional world would
not choose. **The answer is not zero.**

> **Over `34` objects and `667` equivalent writings, the four-axis frontier carries `59` points, of
> which `G0` writes `34`. So `25` frontier points are ones `G0` would never write. `12` of those are
> the natural writing of some other world; the remaining `13` are written naturally by NO world in
> the atlas at all — they are Pareto-optimal writings that no convention's habit produces.** `12` of
> the `16` objects on which any world writes differently from `G0` contribute one of the twelve; on
> the three-axis set that count falls to `7` of `16`.

An earlier revision of this block gave `12` as the answer to "how many points would `G0` not write".
That is the count of frontier points that are **another world's natural writing**, which is a
narrower question. The answer to the question as asked is `25`, and the `13` that belong to no
world's habit are the sharper half: they are exactly what a router carrying the frontier gains over
one that picks a world and writes the way that world writes.

They are not exotic — they are the factored forms:

```text
a * (b + c)                                 where G0 writes  a * b + a * c
(a + b) * (a + b)                           where G0 writes  a * a + 2 * a * b + b * b
a * (x - r) * (x - s)                       where G0 writes  a * x * x - a * (r + s) * x + a * r * s
(x - h) * (x - h) + (y - k) * (y - k)       where G0 writes  x * x - 2 * h * x + h * h + y * y ...
y1 + m * (x - x1)                           where G0 writes  m * x + y1 - m * x1
fa + dfa * (x - a)                          where G0 writes  fa - dfa * a + dfa * x
```

Each of them costs `G0` brackets, which is exactly why `G0` does not write it, and each of them buys
something no bracket count can see: a shorter critical path, a smaller peak of live values, or more
properties legible on the page. **That is the whole content of this card.** A router that ranks
representations by any single measure cannot reach these `25`, and a router that merely switches
worlds cannot reach the `13` of them that no world writes naturally. Only a router that carries the
frontier can.

## Why a frontier and not a ranking

The card is the owner's own design — and its premise is one sentence:

> *"There is no abstractly better until we know the objective."*

Four earlier cards each produced a ranking of the same `25` worlds, and the rankings disagree: cost
(0034, 0037), visibility (0038), depth (0041), peak memory (0044). Experiment 0043 already found
`243` of `300` world pairs incomparable, so a partial order is the established shape of this
landscape. This card stops ranking. For each object it builds the **Pareto frontier of that object's
equivalent writings**, under an axis set that is declared rather than assumed, and reports what a
frontier can say that a ranking cannot.

**Nothing here is compressed into a scalar.** There is no weighted sum, no score, and no "best
representation" column, because choosing the weights *is* choosing the objective, and the objective
is what the project does not yet know. A test asserts the absence.

## The four criteria, and which card owns each

Every measure is imported from the module that owns it, checked by identity and not by equality, so
a re-implementation would fail the test rather than pass an `==`.

```text
axis         meaning                              imported from        card    direction
brackets     minimal bracket pairs, per world     notational_cost      0034    COST, minimise
depth        critical path of the tree            parallel_worlds      0041    COST, minimise
peak_live    simultaneously live values           memory_ceiling       0044    COST, minimise
visibility   manifest properties, counted         manifest_properties  0038    BENEFIT, maximise
```

**Three of these are costs and one is a benefit.** A sign error on the fourth raises nothing and
changes no shape; it silently inverts the atlas. The direction is declared in one place, one function
reads it, a hand-built pair in which visibility alone decides pins it, and a control re-runs the whole
atlas with the exception removed so the size of the error is on the page: treating visibility as a
cost would report `61` writings optimal instead of `50` at three axes and `68` instead of `59` at
four. The control's own headline is `34` under either sign, so a sign error would have been invisible
in question `3` alone.

Only `brackets` is world-relative; `depth`, `peak_live` and `visibility` are properties of the tree.
A frontier is therefore drawn in a **declared reference world**, and the default is `G0` because the
sharpest question is asked in the conventional world's own coordinates. All `25` are swept below.

## The writing space, and the bound that was not imposed

The space is 0039's, imported whole and not restated: every parenthesization of every declared
writing, an exact-rational probe at two declared points that can only discard, and SymPy confirming
every survivor.

```text
declared writings                                      50
full parenthesization space                       1510820   trees, NO bound applied
trees probed                                      1510820   equal to the space, asserted
survived the exact-rational probe                     667
same-object writings confirmed by SymPy               667
(representation, world) cells                       16675
```

**No threshold was declared anywhere in this card.** The Catalan space of every word was enumerated
in full, `trees_probed` equals `space_total`, and the test asserts the equality so that a claim of
having measured a part cannot pass silently. The probe discarded nothing SymPy would have kept:
`667` survivors, `667` confirmations. What bounds this experiment is the corpus and the language,
both named in the limits, and neither is a number that could have been raised.

## Sample sizes: objects, writings and cells are three different numbers

```text
objects                                                34
declared writings                                      50
equivalent writings (representations)                 667
worlds                                                 25
cells = writings x worlds                           16675
```

They are pinned in separate tests with separate names. Experiment 0047 was rejected for reporting
cell counts where object counts were asked for, and a test that pinned them together would not catch
the substitution. **No world multiplier reaches an object count anywhere in this report.**

## The null model

An object whose writings all share one criteria vector carries no frontier information: its frontier
is everything and nothing is dominated. Those objects are counted out before any rate is taken.

```text
objects                                                34
objects with more than one equivalent writing          22   the movable set
objects with a single writing, hence a single vector   12
```

Movability is also per axis, because an object can move on one and not on another:

```text
brackets       22 of 34 objects
visibility     18 of 34
depth          13 of 34
peak_live       9 of 34
```

Every rate below that is taken over a subset says which subset, and there are three different
denominators in this report: `34` objects, `22` movable objects, and `16` objects on which some world
writes differently from `G0`.

## Questions 1 and 2: how many are dominated, how many survive

```text
axis set                    writings   optimal   dominated   dominated share
brackets, depth, visibility      667        50         617          0.925037
all four                         667        59         608          0.911544
```

Over the movable set only, which is the honest denominator:

```text
axis set                    writings   optimal   dominated   dominated share
brackets, depth, visibility      655        38         617          0.941985
all four                         655        47         608          0.928244
```

**One object carries three quarters of the writings.** `binomial_cube` has `502` of the `667`, a
share of `0.752624`, because its expanded writing is a word of `13` operators whose Catalan space is
`742900` trees. Its frontier is `3`. Every pooled figure in this report is therefore printed beside a
per-object figure, and the per-object table is given in full.

```text
object                        writings   optimal 3   optimal 4   dominated 4
calibration_quadratic                5           3           3             2
distributive_law                     2           1           2             0
binomial_square                      5           2           2             3
difference_of_squares                2           1           1             1
difference_of_cubes                  6           1           1             5
sum_of_cubes                         5           1           1             4
quadratic                           10           2           2             8
binomial_cube                      502           3           3           499
perfect_square_trinomial             5           3           3             2
line                                 3           1           2             1
circle                              37           5           5            32
ellipse                              4           1           3             1
hyperbola                            4           1           3             1
parabola                            42           4           4            38
distance_components                  1           1           1             0
slope                                1           1           1             0
midpoint                             1           1           1             0
triangle_area                        2           1           1             1
trapezoid_area                       5           1           2             3
pythagorean_form                     1           1           1             0
difference_quotient                  2           1           2             0
product_rule                         1           1           1             0
quotient_rule                        3           1           1             2
chain_rule                           1           1           1             0
linear_approximation                 2           1           2             0
taylor_first_term                    1           1           1             0
taylor_second_term                   5           2           2             3
riemann_sum_term                     2           1           1             1
dot_product                          1           1           1             0
determinant_2x2                      1           1           1             0
linear_combination                   1           1           1             0
squared_norm                         2           1           1             1
matrix_vector_component              1           1           1             0
cramer_numerator                     1           1           1             0
```

## Question 3: the control is never dominated, and the reason is one axis

```text
objects where G0's own writing is ON the frontier       34   of 34
objects where G0's own writing is dominated              0
```

**This answer is forced, and it must be read that way.** In all `34` objects the writing `G0` chooses
unprompted is the **unique minimum of the bracket axis over the whole `667`-writing space**. Nothing
can be at least as cheap and better elsewhere when nothing else is as cheap at all — so the other
three axes contribute nothing to the answer. The observation is not a tautology, because `G0` chooses
among an object's *declared* writings while the space also holds every other parenthesization, but
given the observation the headline follows from `brackets` alone. It is evidence about the bracket
axis and about nothing else.

The informative version of the question is what happens when the same habit is priced in another
world's brackets. There the uniqueness fails in all `24` of them:

```text
reference world       objects where G0's writing is the unique bracket minimum
G0                        34
G17                       31   it still attains the minimum in all 34, but ties in 3
G18                       31
G14                       29
G16                       26
G02, G08, G11             15
```

Where the tie appears, the other three axes decide. Under `G17` the conventional expanded quadratic
and the factored quadratic cost the same `2` brackets, and the factored writing is strictly better on
everything else:

```text
G17    (a * x * x - a * (r + s) * x) + a * r * s     brackets 2   depth 5   peak 3   visible 0
G17    a * (x - r) * (x - s)                         brackets 2   depth 3   peak 3   visible 3
```

so the conventional writing is **dominated**. Across the `25` reference worlds the control lands on
the frontier for between `29` and `34` of the `34` objects.

## Question 4: the twelve writings the conventional world leaves on the table

The denominator is the `16` objects on which at least one world's natural writing differs from
`G0`'s. Of those, `12` alternatives are Pareto-optimal in `G0`'s own coordinates and `4` are
dominated. Vectors are `(brackets, depth, peak_live, visibility)`.

```text
calibration_quadratic                                                     8 worlds
  G0    (0, 4, 3, 4)   2 * x * x + 3 * x - 5
  else  (2, 3, 3, 3)   (2 * x + 5) * (x - 1)

distributive_law                                                         12 worlds
  G0    (0, 2, 3, 3)   a * b + a * c
  else  (1, 2, 2, 2)   a * (b + c)

binomial_square                                                          12 worlds
  G0    (0, 4, 3, 4)   a * a + 2 * a * b + b * b
  else  (2, 2, 3, 3)   (a + b) * (a + b)

quadratic                                                                20 worlds
  G0    (1, 5, 3, 0)   a * x * x - a * (r + s) * x + a * r * s
  else  (2, 3, 3, 3)   a * (x - r) * (x - s)

binomial_cube                                                            12 worlds
  G0    (0, 6, 3, 4)   a * a * a + 3 * a * a * b + 3 * a * b * b + b * b * b
  else  (3, 3, 3, 3)   (a + b) * (a + b) * (a + b)

perfect_square_trinomial                                                 12 worlds
  G0    (0, 4, 3, 4)   4 * x * x + 12 * x + 9
  else  (2, 3, 3, 3)   (2 * x + 3) * (2 * x + 3)

line                                                                     16 worlds
  G0    (0, 3, 3, 3)   m * x + y1 - m * x1
  else  (1, 3, 2, 0)   y1 + m * (x - x1)

circle                                                                   12 worlds
  G0    (0, 7, 3, 3)   x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k
  else  (4, 3, 4, 0)   (x - h) * (x - h) + (y - k) * (y - k)

parabola                                                                 12 worlds
  G0    (0, 6, 3, 3)   a * x * x - 2 * a * h * x + a * h * h + k
  else  (2, 4, 3, 0)   a * (x - h) * (x - h) + k

trapezoid_area                                                           20 worlds
  G0    (0, 3, 3, 3)   a * h / 2 + b * h / 2
  else  (1, 3, 2, 2)   (a + b) / 2 * h

difference_quotient                                                      12 worlds
  G0    (0, 2, 3, 1)   fxh / h - fx / h
  else  (1, 2, 2, 0)   (fxh - fx) / h

linear_approximation                                                     20 worlds
  G0    (0, 3, 3, 3)   fa - dfa * a + dfa * x
  else  (1, 3, 2, 0)   fa + dfa * (x - a)
```

Read the vectors and the pattern is one thing said twelve times. The alternative always costs more
brackets and always wins on something else: `circle` and `parabola` trade `4` and `2` bracket pairs
for a critical path of `3` instead of `7` and of `4` instead of `6`; `line`, `trapezoid_area`,
`difference_quotient` and `linear_approximation` buy a peak of `2` live values instead of `3` for one
bracket pair. **The conventional convention is not writing badly. It is optimising one axis, and the
other three have points it does not visit.**

Dropping `peak_live` removes `5` of the twelve and leaves `7`: `calibration_quadratic`,
`binomial_square`, `quadratic`, `binomial_cube`, `perfect_square_trinomial`, `circle` and `parabola`.
The five that fall away are exactly those whose only advantage was memory.

Which worlds produce them is itself a spread. `G01`, `G02`, `G07`, `G08` and `G11` each produce `12`
of the `12`; `G18`, our own grouping with the `+`/`-` tie broken toward `-`, produces `1`.

## The partial order over writings

Every unordered pair of writings of one object is ordered, equal, or incomparable, and the three sum
to `C(n, 2)` per object, asserted rather than assumed.

```text
axis set                    pairs   ordered   incomparable   equal   a ranking must invent
brackets, depth, visibility  127423     87981          28653   10789                0.309536
all four                     127423     63407          54768    9248                0.502390
```

**At four axes a total ranking would have to invent an order for more than half the landscape.** That
is the same statement 0043 made about worlds, now made about writings, and it is stronger: 0043 found
`243` of `300` incomparable; here the incomparable share alone is `0.429813` and the pairs that are
exactly equal add `0.072577` more, since a ranking has no basis for ordering those either.

The pooled figure is one object's figure. `binomial_cube` supplies `0.986878` of all pairs, so the
per-object mean is printed beside it and is the number to quote when the question is about objects:

```text
axis set                    per-object mean ordered   incomparable      equal    invent
brackets, depth, visibility                0.772605       0.166829   0.060565  0.227395
all four                                   0.568272       0.386870   0.044857  0.431728
```

Both readings say the same thing in different sizes and neither is suppressed.

## Adding an axis: the containment holds here, and it is not a law

The card asks for the check that the four-axis frontier contains the three-axis one, on the ground
that adding an axis can only enlarge a frontier. **That reasoning is not valid in general** — and the
reason is ties: if two writings agree on every axis of the smaller set and differ on the added one,
the loser becomes dominated in the larger set and was not dominated in the smaller. So the
containment is a measurement here and not a theorem.

```text
contained for every object                             yes, 34 of 34
objects whose frontier grew                             7
objects unchanged                                      27
objects whose frontier shrank                           0
total growth                                           50 -> 59
pairs at risk, tied on 3 axes and different in peak   1541
of those, the loser sitting on the 3-axis frontier       0
```

`1541` pairs could have broken it and none did. The general claim is refuted inside this same corpus,
on the smaller axis sets:

```text
Pareto({depth})              for calibration_quadratic     3 writings
Pareto({brackets, depth})    for calibration_quadratic     2 writings
lost:       2 * (x * x) + (3 * x - 5)   brackets 2, depth 3
beaten by:  2 * x * x + (3 * x - 5)     brackets 1, depth 3
```

Both lost writings tie the winner on depth and lose to it on brackets, which is invisible while
`depth` is the only axis. This is reported as a finding and not as a defect, and the dominance test is
separately proved to be a strict partial order below.

## Sweeps

**The axis set is a parameter that could have been a threshold**, so all `15` non-empty subsets are
run and the lattice is published rather than the `2` the card names.

```text
axis set                                 writings on the frontier
brackets                                                       34
depth                                                          65
peak_live                                                     475
visibility                                                    179
brackets + depth                                               50
brackets + peak_live                                           43
brackets + visibility                                          37
depth + peak_live                                              66
depth + visibility                                             86
peak_live + visibility                                        162
brackets + depth + peak_live                                   58
brackets + depth + visibility                                  50
brackets + peak_live + visibility                              46
depth + peak_live + visibility                                 93
brackets + depth + peak_live + visibility                      59
```

**The lattice is not monotone, and this is the non-monotonicity the ROADMAP asks every card to look
for.** Of the subset pairs where one contains the other, `26` have the SUPERSET with the SMALLER
frontier. The sharpest is `peak_live` alone at `475` against `brackets + peak_live` at `43`, a loss of
`432`: `peak_live` takes only `3` distinct values across the whole corpus, so almost everything ties
on it and almost nothing is dominated, and adding a discriminating axis collapses the ties into order.
**More criteria give fewer Pareto-optimal writings whenever the added axis breaks ties the old ones
could not see.** That is a real turn — and the monotone intuition would have hidden it.

**The reference world is the one modelling choice a reader could disagree with**, so it is swept
rather than defended.

```text
quantity                                       minimum   maximum   at G0
writings optimal, three axes                        46        57      50
writings optimal, four axes                         52        66      59
frontier points G0 would not write, three axes       7        14       7
frontier points G0 would not write, four axes       12        15      12
objects with G0 on the frontier                     29        34      34
```

`G0`'s own coordinates are the friendliest to `G0`: nowhere in the `25` is the count of frontier
points it would not write smaller than it is at `G0` itself. The headline is therefore a lower bound
among the worlds and not a favourable pick.

**The number of equivalent writings is the third parameter that could have been a threshold.** The
whole observed range is published.

```text
writings   objects   mean share Pareto-optimal
       1        12                    1.000000
       2         7                    0.714300
       3         2                    0.500000
       4         2                    0.750000
       5         6                    0.433300
       6         1                    0.166700
      10         1                    0.200000
      37         1                    0.135100
      42         1                    0.095200
     502         1                    0.006000
```

The curve falls but it is **not monotone**: it rises twice, at `3` writings to `4` and at `6` to `10`.
The rise at `4` is `ellipse` and `hyperbola`, and an earlier revision explained it by calling their
four writings mutually incomparable — which is **false, and contradicts itself**: mutual
incomparability would leave `4` on the frontier, not `3`. Their measured vectors are `(4,4,3,5)`,
`(3,4,3,5)`, `(3,4,3,5)` and `(2,3,4,5)`. The first is strictly dominated by the second and third —
one fewer bracket pair, everything else equal — and the second and third are **equal**, not
incomparable, which is why `3` survive and not `4`. The per-object table above prints exactly that:
`4` writings, `3` optimal, `1` dominated. Two objects are not a trend and the report says so; what the curve does
establish is that the optimal share falls by more than two orders of magnitude across the range and
was still falling where the corpus ran out.

## Controls

```text
round trips witnessed, every writing in every world      16675   failures  0
brackets proved required by deletion                     88171   surplus   0
dominance irreflexive, antisymmetric, transitive           yes
pairs checked for antisymmetry                          127423
triples checked for transitivity, three axes             39321   over 135 distinct vectors
triples checked for transitivity, four axes             131572   over 154 distinct vectors
frontier points found dominated                              0
dominated writings found on a frontier                       0
```

Both bridge audits are counted **forwards**: the numbers `16675` and `88171` are round trips and
bracket deletions that were witnessed, not counterexamples that were missed. An audit reporting only
its failures reads identically whether the detector fired or never ran.

Transitivity is quantified over the distinct criteria vectors of each object rather than over its
writings. Dominance is a function of the vector alone, so the two quantifications are equivalent, and
the unreduced walk over `binomial_cube` would be `126` million comparisons of the same `50` tuples.
The distinct-vector counts are asserted so the reduction is auditable.

**Mutation testing, on an isolated copy of the tree and never on the working tree.** `22` mutants were
applied to `pareto_atlas.py`: inverting the benefit sign, making dominance non-strict, flipping the
cost direction, dropping the self-exclusion from the frontier, counting the control's writing among
the alternatives, skipping the frontier filter on the created points, calling every object movable,
truncating the writing space to the declared tree, disabling the minimality and round-trip detectors,
dropping the benefit axis in normalisation, swapping `depth` for `peak_live`, misfiling equal pairs as
ordered, caching frontiers under the wrong world, and understating the pool startup. `20` were killed.
`2` survived and both are equivalent mutants: each blanks a boolean flag whose fact is independently
established by a literal assertion in the same test. Two further mutants survived the first pass, were
reported, and are now killed by tests written in response to them.

## Multicore

The dominant stage of this card is not its own: it is 0039's enumeration of `1510820` trees, which is
imported and which runs across processes under 0039's own measured decision. The stage this card adds
is the `16675`-cell profile grid, and its path was measured rather than assumed.

```text
cores observed                                  16
workers, with 2 cores of headroom               12
chunks                                          44
measured seconds per cell, floor          0.000057
measured pool startup, floor                   0.9   seconds
crossover, from those two floors              17225   cells
this corpus                                   16675   cells
policy decision                          sequential
```

The floors are declared rather than the typical values, because a smaller startup and a cheaper cell
are the readings that FAVOUR the pool, and the pool still loses. The margin is thin and is reported as
such: `16675` against a crossover of `17225` is `0.968` of the way there, so a corpus half again as
large would flip the decision.

`parallel_decision` times both paths on the same work and checks that they agree. Nine runs were
recorded while two other cards were running on the same machine, which is why the spread is wide:

```text
sequential   parallel   speedup
    0.9427     1.1593     0.813
    0.9436     1.2916     0.731
    1.0616     1.8488     0.574
    2.0620     1.6246     1.269
    2.6274    14.5230     0.181
    3.8235     8.8236     0.433
    4.4718    32.2160     0.139
    4.6591    16.6648     0.280
    7.9337    37.7953     0.210
```

The pool loses on `8` of the `9` and wins once — by `1.269` — on the least loaded run. The two paths
produce identical grids on every run, which is asserted in the test suite, so the decision changes only
how fast and never what is measured. **A sequential path is a valid outcome when the measurement says
so, and here it says so on a thin margin that is printed rather than hidden.**

## Limits

- **The writing space is parenthesizations of one token word.** Commutative reorderings are out of
  scope: `a * b + a * c` and `a * c + a * b` are different words, and this experiment never leaves a
  word. Every frontier reported here is a frontier over re-bracketing, and a wider notion of
  equivalent writing would have more points on it.
- **Visibility is 0038's declared rules and nothing else.** A property is manifest when a declared
  shape rule fires on the written form. The vocabulary is not neutral between shapes: `monomial_sum`
  carries four of the seven properties and `factored` carries two, so a writing that expands scores
  higher on the raw count by construction. The count is used here as an axis, never as a claim about
  how much mathematics a form reveals.
- **`depth` and `peak_live` are structural bounds and not runtimes.** `depth` is a critical path and
  `peak_live` is the Sethi-Ullman register number, which counts values and not bytes. Neither has been
  timed, and nothing in this report is a performance claim.
- **The corpus is hand-chosen.** It is 0038's `34` objects in `50` declared writings: 0037's named laws
  plus the calibration quadratic. `12` of the `34` have a single equivalent writing and can carry no
  frontier information at all, and one object supplies `502` of the `667` writings. The totals are
  shaped by that distribution and every rate is printed with its denominator.
- **The domain component of the semantic key is inert** (`NF-2026-00005`). `canonical.py` writes the
  literal `"R"` into `domain` for every expression, so the operative discrimination in the equivalence
  the writing space rests on is `(canonical form, excluded points)`. Nothing in this card depends on
  `domain` varying, but the key is weaker than its name suggests and the disclosure belongs here.
- **The reference world is a modelling choice.** Only `brackets` is world-relative, so a frontier is
  drawn in one world's bracket coordinates. `G0` is the default and all `25` are swept; every headline
  in this report moves with that choice and the range is published beside it.
- **`G0`'s natural writing is 0038's definition**, the cheapest of the object's declared writings with
  ties resolved to the declared order. A different definition of what a world would write unprompted
  would move question `3` and question `4`, and the alternative reading is not measured here.

## Evidence classification

- The frontier sizes, the dominated counts, the pair classes, the axis lattice, the world sweep and the
  size curve are executable **observations** on the declared corpus.
- The `12` frontier points `G0` does not write are **observations**: each is rendered, re-parsed and
  printed with its vector, and each is a member of the same-object space confirmed by SymPy.
- The strict-partial-order property of dominance and the containment of the three-axis frontier in the
  four-axis one are **observations** on the computed relation, asserted and not assumed.
- The claim that adding an axis need not enlarge a frontier is a **structural argument** with a measured
  witness inside this corpus; it is stated as a property of Pareto dominance under ties and not as a
  fact about notation.
- That question `3`'s answer is forced by the bracket axis is an **observation** with a stated
  consequence: it is evidence about `brackets` and about nothing else.
- No general law about mathematical notation is claimed. The atlas is a partial order over the writings
  of `34` hand-chosen objects in one operator set.

## Validation

```text
1187 passed, 2 skipped
```

The `38` tests of this card pin every headline as a literal, keep object counts and cell counts in
separate tests, assert the strict partial order on the computed relation, pin the benefit sign on a
hand-built pair, and check that the sequential and parallel grids are identical.
