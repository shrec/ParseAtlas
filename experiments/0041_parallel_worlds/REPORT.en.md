# ParseAtlas experiment 0041: which worlds write parallel forms for free

## Purpose

**Over `58` corpus entries and `25` worlds, only `6` entries have a parallelism tax that any
convention can move at all; the least-taxing worlds charge `22` and the conventional `G0` charges
`25`, which is the joint worst, ranking `20` of `25` — while `G0` is simultaneously the `5`th
cheapest world to write in. Of that tax, `21` units are forced by the corpus in every world and only
`1` to `4` units are chosen by the convention.**

Read the question twice, because it is easy to get wrong.

Depth is a property of a **tree**. For one fixed tree the depth is identical in all `25` worlds,
because every world reparses its own rendering back to that same tree. "Does the convention change
the critical path of this expression?" is therefore not a question about one tree at all, and an
experiment reporting it as one would be measuring the round-trip guarantee rather than the
conventions. That premise is measured here and not assumed: `41175` checks, one depth value every
time.

The real question is one level up. An object has many equivalent writings; they have different
depths — the left-leaning chain `a + b + c + d` has depth `3`, the balanced `(a + b) + (c + d)` has
depth `2`, and depth is exactly parallel evaluation time — and every world can write every one of
them. What differs is **what each writing costs in brackets**. So:

> In which worlds is the **cheapest** writing of an object also its **shallowest**?

Where the two coincide, that world writes parallel-ready mathematics by default. Where they diverge,
its natural notation is a sequential chain and the parallel form has to be bought with brackets. The
gap is the **parallelism tax**:

```text
tax(object, world) = depth(cheapest writing in that world) - min depth over all writings

when several writings tie for a world's minimum bracket count, the shallowest of them is taken
```

**That tie-break is a modelling choice and it decides the headline, so it is stated here rather
than left in the code.** It resolves ties in the world's favour. Taking the deepest of the tied
writings instead changes `52` of the `1450` cells — exactly the `6` movable objects the ranking
rests on — and moves the least-taxing total from `22` in `9` worlds to `23` in `2`, `G07` and
`G18`. `G0` is `25` under both. `G18`, the cheapest world to write in, is `23` under both and so
becomes joint-best on tax under the pessimistic reading.

**Section 5's central claim moves with it, and by more than the cell count suggests.** The rank
correlation between what a world costs to write and what it charges in parallelism tax is
`0.167418` under the optimistic tie-break — the near-independence the section reports — and
`0.422211` under the pessimistic one, two and a half times larger and no longer fairly described
as barely agreeing. The illustration inverts outright: `G19`, the most expensive world in the
corpus to write in and joint-first on tax at rank `1` optimistically, falls to rank `22`
pessimistically. Both quantities are computed by the module and pinned by tests; neither is
presented as the only defensible one, and section 5 should be read with this figure beside it.

Both halves are needed. `min_depth` alone is a property of the mathematics; `free_depth` alone is a
property of the notation; only the difference belongs to the pairing, which is what the founding
question is about. This is direction B applied to computation rather than to legibility.

### The null model is the main risk in this card, and it is named before any result

A pure associative chain over one repeated operator is invisible to precedence. Theorem **T6**
(operator-support reduction) says a grammar acts on an expression only through its restriction to the
operators the expression actually uses; a one-operator word has exactly one such restriction, so all
`25` worlds price every tree over that word identically. Reporting "no world parallelises a chain for
free" as a discovery would be publishing a parsing artifact.

So the split is made explicitly, T6 is **verified rather than cited** (`24525` checks, `0`
mismatches), and the ranking is rebuilt on the movable subcorpus alone.

## Space structure

An entry is one object together with the **one token word** that spells it. Its writing space is
every parenthesization of that word which still denotes the object — the Catalan space, filtered.

The filter is experiment 0039's, imported and not restated: exact rational arithmetic at two declared
probe points (seed `39`), which can only ever rule a tree **out**, followed by SymPy confirmation of
every survivor. An undefined value proves nothing and is escalated to SymPy rather than guessed.

```text
corpus entries                                          58
full parenthesization space                        1511800   trees, no bound
  largest word                                          13   operators -> 742900 trees
  binomial_cube.expanded / circle.general      742900 / 742900
discarded by the exact probe                       1510153
probe survivors                                       1647
confirmed same object by SymPy                        1647   (0.109% of the space)
rejected by SymPy                                        0
```

**The whole space was enumerated**: `trees_probed` equals `space_total`, pinned in the test suite so
that "we measured part of it" cannot pass silently.

**SymPy rejecting nothing is a fact about this corpus, not a licence to drop the confirmation.** The
probe does all the discarding here. The filter is therefore exercised directly in both directions in
the test suite: on `a - b - c - d` and on `a / b / c / d` it keeps `1` writing out of `5`, and on
`a + b + c + d` it keeps `5` of `5`.

**The confirmation is nevertheless load-bearing in principle, and the test suite shows it on a
constructed word.** `p / q - q` has `2` parenthesizations; one of them is `p / (q - q)`, which is
undefined at both declared probe points, so the probe passes it through unjudged — and SymPy is
then the only thing that removes it, leaving `1`.

The correctness bridge is run over the whole grid before any number is read off it:

```text
round-trip checks (1647 writings x 25 worlds)         41175   failures 0
bracket pairs checked minimal by deletion            158021   violations 0
depth-invariance checks                               41175   distinct depths per tree: always 1
```

## Corpus

Imported, not invented, and stated exactly.

**The named-law half — `50` entries.** `parseatlas.manifest_properties.CORPUS`: the `34` objects of
experiments 0038 and 0039 (`33` named laws plus the calibration quadratic), taken as their `50`
declared writings. Each declared writing is its own entry, because the writing space of this
experiment is the parenthesizations of one word and an object's two writings are two different words.
Its half of the space reproduces 0039 exactly: `1510820` trees, `667` same-object writings.

**The associative-chain half — `8` entries.** Added by this experiment and declared here:

```text
chain_add_4   a + b + c + d                    5 trees
chain_add_5   a + b + c + d + e               14 trees
chain_add_6   a + b + c + d + e + f           42 trees
chain_add_8   a + b + c + d + e + f + g + h  429 trees
chain_mul_4   a * b * c * d                    5 trees
chain_mul_5   a * b * c * d * e               14 trees
chain_mul_6   a * b * c * d * e * f           42 trees
chain_mul_8   a * b * c * d * e * f * g * h  429 trees
```

Lengths `4`, `5`, `6` and `8` over `+` and `*`. `4` is the shortest length at which sequential and
balanced differ; `8` makes the classical parallel-prefix gap unmistakable while the space stays
exhaustively enumerable. `-` and `/` are deliberately absent: `a - (b - c)` is a different object, so
a subtraction chain has exactly one same-object writing and cannot exhibit a depth choice at all.

Fields: `algebra` `18`, `geometry` `15`, `calculus` `11`, `associative_chain` `8`,
`linear_algebra` `6`.

## Observed results

### 1. The tax grid: `25` worlds in four blocks

```text
tax  worlds                                              free objects   count
22   G03 G09 G10 G13 G15 G16 G19 G21 G22                          46       9
23   G01 G04 G05 G07 G14 G17 G18                                  45       7
24   G11 G12 G20                                                  44       3
25   G0                                                           44       1
25   G02 G06 G08 G23 G24                                          43       5
```

Least tax `22`, worst `25`, spread `3`. The conventional world `G0` sits in the joint-worst block at
rank `20` of `25`.

### 2. The null model: `52` of `58` entries cannot move, and `21` of the tax is forced

```text
entries whose tax varies between worlds (movable)         6
entries whose tax is the same in all 25 worlds (forced)  52
  forced at zero                                         41
  forced at a positive constant                          11
    the 8 associative chains                              8   contributing 16
    binomial_cube.expanded                                1   contributing  2
    perfect_square_trinomial.expanded                     1   contributing  1
    parabola.standard                                     1   contributing  2
forced floor, identical in every world                   21
movable remainder, per world                          1 to 4
```

Every world's total is `21` plus its movable remainder, pinned cell by cell. So `21` of `22` — `95.5%`
— of the least-taxing world's total is forced by the corpus, and `21` of `25` — `84.0%` — of `G0`'s.
**The entire ranking rests on `6` objects.**

The ranking is unchanged by the split — movable spread `3` equals full spread `3`, spread survival
`1.0`, the movable ordering is identical to the full one, and `G0` ranks `20` under both — but this
is **necessarily** so and is not a robustness result. A forced row contributes the same constant to
every world, so each world's full total is `21` plus its movable total identically, and neither the
ordering nor the spread can differ. It is recorded because the arithmetic should be visible, not
because it was ever in doubt; the suite asserts it as the identity it is.

`9` entries have a single-operator support and are forced by T6 by construction:
`chain_rule.standard` and the `8` chains. T6 is verified on them cell by cell — `24525` checks, `0`
mismatches — so the chain result is a **null model result**, not a discovery.

### 3. The chains, in full: the sequential writing is free in all `25`, the balanced one never is

```text
entry          leaves  sequential depth  min depth  tax (all 25)  bracket premium  cheapest cost
chain_add_4         4                 3          2             1                1              0
chain_add_5         5                 4          3             1                1              0
chain_add_6         6                 5          3             2                1              0
chain_add_8         8                 7          3             4                3              0
chain_mul_4         4                 3          2             1                1              0
chain_mul_5         5                 4          3             1                1              0
chain_mul_6         6                 5          3             2                1              0
chain_mul_8         8                 7          3             4                3              0
```

Total chain tax `16`, the same number in every one of the `25` worlds. The cheapest writing costs `0`
brackets in every world and it is the left-leaning chain in every world; the shallowest writing costs
`1` or `3` brackets in every world. This is `n - 1` against `ceil(log2 n)`, and precedence has no say
in it.

### 4. The `6` movable entries, named

```text
entry                             writings  written depth  min depth  free worlds  G0 tax
calibration_quadratic.expanded           4              4          3           16       1
circle.general                          36              7          5           12       2
ellipse.standard                         4              3          3           17       0
hyperbola.standard                       4              3          3           17       0
quotient_rule.split                      2              3          3           17       0
taylor_second_term.standard              5              4          3           16       1
```

`3` of them (`ellipse.standard`, `hyperbola.standard`, `quotient_rule.split`) are free in `G0` and
charged `1` in exactly `8` worlds each. `3` of them are the other way round, and they are the answer
to the card's first question.

`circle.general` is the sharpest cell in the grid. Its word,
`x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k`, has `742900` parenthesizations of which `36`
are still the circle; it is written at depth `7` and can be written at depth `5`. `12` worlds charge
nothing for that, `12` charge `1` — and `G0` charges `2`, alone among the `25`.

### 5. Cost rank against tax rank: they barely agree — under one tie-break

**Read this section with the tie-break disclosure above.** The `0.167418` below assumes ties for a
world's cheapest writing are resolved toward the shallowest. Resolved the other way the same
correlation is `0.422211`, and the `G19` row in the table is the one that moves most.

Spearman rank correlation over the `25` worlds between the number of brackets a world spends writing
the corpus and the parallelism tax it charges: **`0.167`**. On the movable subcorpus alone the
correlation is the same `0.167`, necessarily — the forced floor is a constant and a constant cannot
move a rank; the agreement is the check that the null-model split did what it claims.

The concrete shape of a near-zero correlation:

```text
world  cost total  cost rank  tax total  tax rank
G18            42          1         23        10
G16            44          2         22         1
G0             47          5         25        20
G19            97         25         22         1
```

`G19` is the most expensive world in the corpus to write in and is joint-first on parallelism. `G0` is
`5`th cheapest to write in and joint-last on parallelism. Cheap notation and parallel notation are
close to unrelated here.

### 6. What the tax buys: a critical-path bound, and nothing more

```text
entries whose shallowest writing is strictly shallower than the written one     14 of 58
largest depth saving                                                       4 (chain_8: 7 -> 3)
largest ratio                                                                        2.333
corpus total, written depth                                                            187
corpus total, minimum depth                                                            162
aggregate ratio                                                                      1.154
deepest object                                             circle.general, depth 7 -> 5
```

**These are depth quotients under the unit-cost parallel model, in which every operation takes one
step and unlimited processors are free. Nothing was executed and nothing was timed.** Calling `2.333`
a speedup would be dressing a bound up as a benchmark.

### 7. Does `G0` hold any distinction here?

Asked as a uniqueness question, because that is the only form in which it has an answer.

```text
coordinate         G0 value   worlds sharing it
tax total                25   6   (G0 G02 G06 G08 G23 G24)
cost total               47   2   (G0 G24)
free objects             44   4   (G0 G11 G12 G20)
pair tax and free   25 / 44   1   (G0)
pair tax and cost   25 / 47   2   (G0 G24)
```

No single coordinate is unique to `G0`. One pair is: `G0` is the only world that charges the maximum
tax `25` while still charging nothing on `44` objects — its taxed objects are charged harder. The
per-object form of the same fact is `circle.general`, where `G0` is the only world of the `25` to
charge `2`. `0` objects are free only in `G0`, and `0` objects are taxed only in `G0`.

### 8. The headline questions, one sentence and one number each

1. **Yes, `3` objects** — `calibration_quadratic.expanded`, `circle.general` and
   `taylor_second_term.standard` have their shallowest writing free in `16`, `12` and `16` worlds
   respectively and taxed in `G0`.
2. **`9` worlds tie for least tax at `22` — `G03` `G09` `G10` `G13` `G15` `G16` `G19` `G21` `G22` —
   and `G0` ranks `20` of `25`**, in the joint-worst block at `25`.
3. **Forced, and therefore a null model result: the sequential chain is free in all `25` worlds and
   the balanced form is free in none of them**, because a single repeated operator is invisible to
   precedence under T6; verified, not assumed, over `24525` cells with `0` mismatches, and reported as
   the parsing artifact it is rather than as a finding about conventions.
4. **They barely agree: Spearman `0.167`** over the `25` worlds, the same on the movable subcorpus, and
   the cheapest world to write in (`G18`, `42` brackets) ranks `10` on tax while the dearest (`G19`,
   `97` brackets) ranks `1`.
5. **One, and it is a pair rather than a coordinate**: `G0` is the unique world charging the maximum
   tax `25` while still charging nothing on `44` objects, and the unique world charging `2` on
   `circle.general`.

## Interpretation

**1. The convention barely decides this.** `52` of `58` entries charge the same tax in every world,
and `21` of every world's total is the forced floor. Whatever makes mathematics sequential in this
corpus, precedence is not it. That is a negative result about **precedence**, measured on this corpus
and in this representation, and its scope has to be read with it.

**2. What is forced is forced by associativity, not by notation.** The chains carry `16` of the `21`
forced units, and the three forced law writings carry the remaining `5`. Every one of them is a word
whose depth choice exists but whose price is fixed: `binomial_cube.expanded` can go from depth `6` to
depth `4` for `3` brackets, in all `25` worlds equally. The parallel form is available everywhere and
free nowhere.

**3. Cheap and parallel are different axes.** A correlation of `0.167` over `25` worlds is the
substantive finding of this card, not a caveat on one. `G19` is the worst world in the corpus for
brackets and among the best for depth; `G0` is the reverse. Direction B's first experiment (0034)
ranked conventions by what mathematics costs to write; this one ranks them by what mathematics costs
to evaluate in parallel, and the two orderings are almost independent. A convention chosen for one is
not thereby good for the other.

**4. `G0` is a legibility optimum sitting in the sequential block.** It is `5`th of `25` on brackets
and joint-last on tax, and it is the only world in the corpus that charges `2` on `circle.general`.
That is not a claim that mathematics chose badly — it is the observation that the two objectives were
never traded against each other, so there is no reason for the choice made under one to be good under
the other, and here it is not.

**5. The `6` movable objects say what movement looks like when it exists.** They are conics, a
quadratic, a quotient rule and a Taylor term — objects whose word mixes `*`, `/` and `+ -`, so that a
world's ordering can make one grouping free and another not. The tax appears exactly where a world's
precedence forces the cheap reading to nest the additive part inside the multiplicative one, or the
reverse. Where the word has one operator, or where every same-object writing has the same depth,
nothing moves.

## Limitations

- **Depth is a critical-path BOUND, not a measured runtime.** Every ratio here is a quotient of two
  tree depths under the unit-cost parallel model — one step per operation, unlimited free processors,
  no scheduler, no memory system, no vectoriser. Nothing was executed and nothing was timed. `2.333`
  is not a speedup.
- **The writing space is the parenthesizations of ONE token word.** Commutative reorderings are out of
  scope, and that is a real restriction rather than a formality: `a + b + c + d` and `c + d + a + b`
  are different words here, and any rewriting that changes the token multiset — distributing,
  factoring, introducing a common subexpression — is outside the space entirely. Real parallelisation
  of mathematics uses exactly those moves. This experiment measures only what reassociation of a fixed
  word can buy.
- **The corpus is hand-chosen.** The `50` named-law writings are 0038's choices inherited whole,
  including which writings an object is allowed to have; the `8` chains were added by this card, and
  their lengths were declared for the reason stated rather than swept. A different corpus would move
  every total, and with only `6` movable entries it could move the ranking.
- **The null-model split is reported separately for exactly this reason.** `84.0%` to `95.5%` of each
  world's tax is forced and cannot rank anything. The headline ranking is a `3`-unit spread over `6`
  objects, and it is presented as such rather than as a `22` against `25` difference between
  conventions.
- **Results are relative to the declared bracket rule.** Cost is the number of bracket pairs the
  grammar forces, counted from the renderer that is derived from the parser. A different cost model —
  characters, tokens, visual chunking, stack depth — would move every cost number and could move the
  correlation.
- **The identity filter depends on SymPy.** The probe only ever discards; confirmation belongs to
  SymPy, and a SymPy error is not controlled here.
- **A cheaper or more parallel convention is not an argument that mathematics should have adopted it.**

## Evidence classification

- Space size (`1511800`), same-object writings (`1647`), the tax grid, the four-block structure, the
  per-world totals `22`, `23`, `24` and `25`, the correlation `0.167` — **OBSERVED**, on this corpus,
  on these words, under this bracket rule.
- Round trip (`41175` checks, `0` failures), minimality (`158021` brackets, `0` violations), depth
  invariance (`41175` checks), sequential equals parallel — **VERIFIED PROPERTIES** over this grid,
  not proofs over all trees.
- The chain result — **NULL MODEL RESULT**, forced by T6, verified over `24525` cells with `0`
  mismatches, and explicitly not a finding about conventions.
- The forced and movable split (`52` and `6`) and the forced floor (`21`) — **OBSERVED**, and the
  ground on which the ranking is stated to rest on `6` objects.
- The depth ratios (`1.154` aggregate, `2.333` maximum) — **BOUND**, under the unit-cost parallel
  model; not a benchmark and not a runtime.
- The single distinction of `G0` (the `25` and `44` pair, and `2` on `circle.general`) — **OBSERVED**
  uniqueness on this corpus, not a property of `G0` in general.

## Validation

```text
python -m pytest -q tests/test_parallel_worlds.py      42 passed
python -m pytest -q                                   891 passed   (as of this run)
```

The headline numbers are pinned in the tests as **literals**, not recomputed from the module, so a
change of result fails a test instead of quietly rewriting the finding. The test file is ordered
cheap-first on purpose: plumbing, depth on hand-built trees, the identity filter in both directions,
the ranking arithmetic and the concurrency policy are all checked before anything sweeps `1511800`
trees, so a broken invariant fails in seconds.

### Concurrency: parallel by measurement

```text
trees                              1511800   (58 entries, chunk = 4000 trees)
chunks                                 433
workers                                 12   (16 cores, 2 in headroom, cap 12)
sequential                          26.201 s  ->  1.733e-5 s / tree
parallel (12 workers)                8.791 s
speedup                              2.980x
identical results                     True
pool startup (12 workers)            1.251 s  (min of 5; declared 1.3)
```

**These seconds are machine- and load-specific and are not part of the result.** Review re-ran the
same probe while four other cards were running on this machine and the pool LOST: sequential
`53.53` s against parallel `59.10` s, a speedup of `0.906x`. What is load-bearing reproduced
exactly — `identical: True` over the whole tree corpus, and chunks `433` / workers `12` / cores
`16` — and the suite pins the parallelisation POLICY rather than any duration.

`should_parallelise` does arithmetic on two **measured** numbers rather than on a tree count. With
these two constants the pool pays for itself above roughly `79000` trees, so the full corpus runs
parallel and a single small entry runs sequential; both directions are pinned in the test suite so a
change to either constant that silently flipped the policy would fail. The worker count is derived
from the observed core count, never from a hardcoded constant.

### Mutation testing

On an isolated copy (tree copied into the scratchpad; the canonical repository untouched; a preflight
test asserts the import comes from the copy and not from `d:/Dev/ParseAtlas/src`), `22` mutants were
placed at the decisive points: the depth definition and its declared off-by-one, the cheapest-writing
tie-break, the tax subtraction, the bracket-count extremes, the exact probe, the SymPy confirmation,
the movable and forced split, the forced floor, the T6 invariance check, the free-object count, the
ranking and the Spearman tie handling, the declared chain lengths, the parallel decision, the
round-trip comparison, the treatment of an undefined probe value, and the right-hand bracket
threshold in the imported renderer.

```text
mutants                                 22
killed                                  19
survived                                 3
```

**The `3` survivors are reported rather than removed, and they are all the same kind.** Each is a
guard whose failure branch never fires on this corpus, so deleting its comparison changes no number
a test can see: `round_trip_never_reparses` removes the comparison in an audit that records `0`
failures, and `support_invariance_ignores_mismatch` removes the comparison in a check that records
`0` mismatches. Killing those two would need a deliberately broken fixture, which is a different
kind of test from the ones here. The third, `probe_uses_one_point`, drops the second declared probe
point and changes nothing at all: on this corpus `1` point already separates every tree the second
would have separated, which is a fact about the corpus and is recorded as one.
