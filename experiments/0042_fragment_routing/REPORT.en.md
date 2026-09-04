# ParseAtlas experiment 0042: does fragment routing survive the seams?

## Purpose

The owner's question, in his words: *can a problem be split into fragments, each fragment solved in the representation where it solves best, and the results then rejoined into the final answer?*

**The verdict, both architectures, in one paragraph, and it is mostly negative.**

- **MODEL I (inline: one document, one host convention).** Routing wins, and it wins by almost nothing. Against one global convention the corpus costs `33` brackets with no routing and `29` with it - a gain of `4` on a seamless prize of `33`, so **`12.1%` of the prize survives the seam**. Against the per-object baseline the numbers are `7` and `6`: a gain of `1`, **`14.3%`**. And every bracket of that gain is bought with a document its own host convention can no longer read.
- **MODEL II (named intermediates).** Routing loses, and it loses heavily. The same corpus needs `87` named intermediates to remove at most `7` brackets of interior cost. At one unit per definition line Model II costs `87` against the global convention's `33` - **`54` worse** - and a definition line would have to cost less than `0.3793` of a bracket pair before Model II broke even.
- **And the result that decides the card.** Restrict Model I to documents a host-convention reader can actually decode, and inline routing delivers **exactly zero**. Checked over `54375` cells - `87` fragments against `25` hosts against `25` worlds - with `0` counterexamples. `render(F, h)` is the minimum-bracket `h`-writing of a fragment, so any world whose rendering `h` reads correctly costs at least as much as `h` itself. **A bracket delimits a scope; it does not carry a convention.**

So the honest answer to the founding question's routing half is: the prize measured by 0034 is real, it is large, and **it is not at the fragments - it is at the joins**, which is precisely where routing has nothing to offer. Under the best single world `21` of the `33` brackets sit at joins and `9` inside fragments; no world in the registry puts fewer than `21` at the joins.

Module: `src/parseatlas/fragment_routing.py`. Tests: `tests/test_fragment_routing.py`.

## What this builds on, and what it does not re-derive

**Half the answer was already measured and is cited, not repeated.** Experiment 0034 established the per-formula oracle on its own `58`-formula corpus: if each formula could pick its own convention the corpus costs `3` parentheses, while the best single grammar pays `29`. That `26`-parenthesis gap is the price of one global convention. Routing at formula level therefore pays by roughly an order of magnitude - **and that number ignores the seams entirely. It is an upper bound on the prize, not a result about rejoining anything.**

`oracle_bound` recomputes the same quantity on this card's corpus and reports it beside the published one, in both cases labelled as a bound.

**Experiment 0038 makes the case for decomposition stronger, and it belongs in the opening.** Across `850` cells the constant term and the roots are never manifest together, though nothing in the shape rules forbids it. If a problem needs both, no single world supplies both, so decomposition there is not an optimisation - it is forced. This card does not weaken that. It says what decomposition costs when the pieces have to be put back.

## The two architectures

They are the two real ways an SDK could be built and their seam costs have nothing in common.

```text
MODEL I   inline    one document, one host world; a fragment written in its own world is a
                    SUBEXPRESSION of it and pays whatever the host charges to keep the tree
MODEL II  named     each fragment is written and evaluated in its OWN world, bound to a name;
                    the name -- a leaf -- is what the next fragment uses
```

**Model I's seam is brackets.** For each fragment the record carries three quantities and never blends them: what the fragment costs **in its own best world**, what it costs **written in the host world**, and the difference - which is what a single-convention document forfeits. The seam charged is one bracket pair per fragment the host cannot absorb, for either of two independent reasons: the host's precedence would re-associate it, or the host would misread its interior.

**Model II's seam is definition lines, and a definition line is not free.** `NAMING_UNIT_COST` charges one unit per named intermediate, on the same scale as one bracket pair. That is a modelling choice and it is named as one: a definition line is plainly *more* than one bracket pair in characters - a name, a binder, a line break - so `1` is the most generous honest rate for Model II. Because it is a choice, `naming_break_even` reports the rate at which Model II stops winning rather than leaving the choice unpriced.

**Model II's document is self-describing; Model I's is not.** Each definition line names the world it is written in; nothing leaks across a line. An inline document has no such place. This is structural, not a modelling choice, and it is the real difference between the two.

## The splitting rule, declared before any number was looked at

```text
Let L be the control grammar's level containing the root operator: {*, /} or {+, -}.
Descend from the root through every node whose operator lies in L.
Every operand hanging off that chain which is itself a Binary node is a FRAGMENT.
Leaves are not fragments: a leaf is one token and no convention can charge it anything.
The SKELETON is that chain with each fragment replaced by a hole.
```

One rule, applied to every object, consulting nothing but the tree and the control grammar's levels. It reads `G0`'s levels because the intended tree is by definition the `G0` parse of conventional notation; nothing downstream of the split consults `G0` again. **A different rule would move every number in this report** and that is stated in the limits rather than hidden.

Three worked splits, so the rule can be checked by hand:

```text
(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)   root +   ->  2 fragments, both products
x * x / (a * a) + y * y / (b * b)               root +   ->  2 fragments, both quotients
x*x - 2*h*x + h*h + y*y - 2*k*y + k*k           root +   ->  6 fragments, all products
a / (b * c)                                     root /   ->  0 fragments: one homogeneous chain
```

## Corpus

Every written form in `parseatlas.manifest_properties.CORPUS` - experiment 0037's named laws plus 0038's calibration quadratic - that the rule cuts into at least two fragments. **The filter is the definition of "composite"; no writing was chosen or dropped by hand**, and the ones the rule rejects are published with their counts.

```text
composite writings          38
fragments                   87
distinct fragment sources   67
fragment counts             2 x 31,  3 x 5,  4 x 1,  6 x 1
writings excluded           12   (fewer than 2 fragments)
```

Excluded, with the count that excluded them: `distributive_law.factored` `1`, `line.point_slope` `1`, `parabola.vertex` `1`, `midpoint.mean` `1`, `triangle_area.half_base_height` `0`, `trapezoid_area.mean_times_height` `1`, `difference_quotient.closed` `1`, `quotient_rule.closed` `1`, `chain_rule.standard` `0`, `linear_approximation.point_form` `1`, `taylor_first_term.standard` `1`, `riemann_sum_term.standard` `1`.

## The obligation at every seam

A fragment written for one world means something else when read by another, so a join is only valid if the value crossing it is preserved. Every routing produced is decoded back to a tree - the skeleton read in the host world, each piece read in the world it was routed to - and compared to the single-world composite on the **project semantic key** `(canonical form, domain, excluded points)`, imported unchanged from `parseatlas.alternative_mathematics.semantic_key`. **Not on the rendered string.**

```text
routings checked (38 objects x 4 objectives x 2 models)   304
routings whose object is preserved                        304
```

The check is not vacuous, and the negative control says so. `ellipse.standard` routes both fragments to `G01`, where `x * x / a * a` denotes `(x*x)/(a*a)`. Declare the wrong world for those same characters and the decode gives `x**2 + y**2` - a different function, caught by the key, not by the string.

## Observed results

### 1. Where the brackets of a single-world document actually sit

This is the structural fact the whole verdict rests on. A bracket inside a fragment is one routing can move; a bracket at a **join** belongs to the seam and to no fragment.

| world | whole | interior | skeleton | joins |
|---|---|---|---|---|
| `G0` (`*/ +-`) | 35 | 14 | 0 | 21 |
| `G18` (`* / - +`), best | 33 | 9 | 3 | 21 |
| floor over all 25 worlds | 33 | 0 | 0 | 21 |

**The interior floor is `0`: every one of the `87` fragments is free in some world.** The join floor is `21` and no world beats it. So the seamless prize is `33` brackets and `21` of them are unreachable by construction.

### 2. The prize, the seam and what survives, as three separate numbers

```text
one global convention, no routing (G18)            33
per-object oracle (each object picks its world)     7
per-fragment oracle, NO seam at all                 0
prize                                              33
```

For reference, the published 0034 figures on that experiment's own corpus: per-formula oracle `3`, best single grammar `29`, gap `26`. The gap on this corpus is also `26` (`33` minus `7`). **That is a coincidence of two different corpora and is not a reproduction of 0034.**

### 3. The verdict, per objective and per model, one host convention for all 38 documents

This is the like-for-like comparison: one house convention against one house convention, the only difference being whether fragments are routed.

| objective / model | routed | interior | skeleton | seam | best host | vs `33` | host-readable |
|---|---|---|---|---|---|---|---|
| `brackets` / inline | 29 | 0 | 3 | 26 | `G18` | **+4** | 35 |
| `brackets` / named | 87 | 0 | 0 | 87 | `G0` | -54 | 38 |
| `visibility` / inline | 35 | 14 | 0 | 21 | `G0` | -2 | 38 |
| `visibility` / named | 101 | 14 | 0 | 87 | `G0` | -68 | 38 |
| `visibility_opaque` / inline | 33 | 7 | 0 | 26 | `G0` | 0 | 33 |
| `visibility_opaque` / named | 94 | 7 | 0 | 87 | `G0` | -61 | 38 |
| `depth` / inline | 35 | 14 | 0 | 21 | `G0` | -2 | 38 |
| `depth` / named | 101 | 14 | 0 | 87 | `G0` | -68 | 38 |

Under `brackets`/inline the whole `4`-bracket gain comes from exactly two documents - `circle.center_radius` and `distance_components.squared`, each `4` to `2` - and **both of them stop being readable in the host convention**. A third, `quadratic.expanded`, becomes unreadable for no gain at all.

### 4. The verdict per object, against the per-object baseline

Here each document may pick its own host, and the baseline is correspondingly the best single world for that object.

| objective / model | best single | routed | interior | skeleton | seam | wins | ties | loses |
|---|---|---|---|---|---|---|---|---|
| `brackets` / inline | 7 | 6 | 0 | 0 | 6 | 1 | 37 | 0 |
| `brackets` / named | 7 | 87 | 0 | 0 | 87 | 0 | 2 | 36 |
| `visibility` / inline | 7 | 19 | 14 | 0 | 5 | 1 | 32 | 5 |
| `visibility` / named | 7 | 101 | 14 | 0 | 87 | 0 | 2 | 36 |
| `visibility_opaque` / inline | 7 | 13 | 7 | 0 | 6 | 1 | 32 | 5 |
| `visibility_opaque` / named | 7 | 94 | 7 | 0 | 87 | 0 | 2 | 36 |
| `depth` / inline | 7 | 19 | 14 | 0 | 5 | 1 | 32 | 5 |
| `depth` / named | 7 | 101 | 14 | 0 | 87 | 0 | 2 | 36 |

The single `brackets`/inline win is `sum_of_cubes.factored`, `2` down to `1`:

```text
intended          (a + b) * (a * a - a * b + b * b)
host              G01  ( + - * / )
routed document   a + b * (a * a - a * b + b * b)          1 bracket pair
read in G01       a * (a - a) * (b + b) * b                a DIFFERENT object
```

The seam bracket keeps the join right and can do nothing about the interior, which a `G01` reader re-associates. That is the whole of Model I's advantage on this corpus.

### 5. The seam, split by reason

| quantity | `brackets`/inline | `brackets`/named |
|---|---|---|
| fragments | 87 | 87 |
| fragments routed off `G0` | 10 | 10 |
| seam total | 6 | 87 |
| wraps forced by host precedence only | 2 | 0 |
| wraps forced by host misreading only | 4 | 0 |
| wraps forced by both | 0 | 0 |
| documents host-readable | 34 of 38 | 38 of 38 |
| forfeited by one convention | 9 | 14 |

**Two thirds of Model I's seam is the reason nobody budgets for.** Precedence protection is the seam an SDK designer would predict; being misread by the host is the seam that actually dominates, and a bracket does not fix it.

### 6. Host-readable inline routing gains exactly nothing

```text
fragments x hosts x worlds checked   54375
cheaper readable alternatives            0
total gain over all 25 hosts             0
```

The argument is forced, and the grid confirms it rather than replacing it. A fragment's token word is fixed, so an `h`-writing of it differs only in bracket placement; `render` emits a bracket exactly where `h` would otherwise re-associate, and 0034's minimality audit verifies every one of them is load-bearing; therefore `render(F, h)` is *the* minimum-bracket `h`-writing, and any world whose rendering `h` reads correctly costs at least as much. Under `G18` the readable interior floor is `9`, identical to `G18`'s own `9`.

Readability is not the scarce thing: on average `24.310344827586206` of the `25` worlds produce a rendering `G18` reads correctly. Those are precisely the worlds whose rendering coincides with `G18`'s, and they cost exactly what `G18` costs.

### 7. The four objectives, and whether they agree

| objective | measures | worlds tied on a fragment (mean) | fragments where all 25 tie |
|---|---|---|---|
| `brackets` | notational cost, 0034/0037 | 22.448275862068964 | 70 |
| `visibility` | manifest properties, 0038 transparent regime | 25.0 | 87 |
| `visibility_opaque` | manifest properties, 0038 opaque regime | 23.195402298850574 | 75 |
| `depth` | critical path, imported from `parallel_worlds` | 25.0 | 87 |

Pairwise agreement over the `87` fragments: `brackets`/`visibility` `77`, `brackets`/`visibility_opaque` `82`, `brackets`/`depth` `77`, `visibility`/`visibility_opaque` `82`, `visibility`/`depth` `87`, `visibility_opaque`/`depth` `82`. All four agree on `77`. There are only `3` distinct choice patterns: `(G0, G0, G0, G0)` on `77` fragments, `(G01, G0, G01, G0)` on `5`, `(G01, G0, G0, G0)` on `5`.

**Two of the four cannot express a preference at all, and the reason is structural rather than a shortage of corpus.**

- `depth` is the critical path of the intended tree, and a world chooses only how to *write* a fixed tree. Measured: world-invariant on all `87` fragments, `0` fragments where any world's minimum-cost writing is shallower than the intended tree, `20` fragments reassociable at all. The structural reason is that a same-operator right child is bracketed in **every** world, so the cheapest writing of a chain is always the deepest one - cost and depth pull against each other and the cheapest writing never wins on depth.
- `visibility` under 0038's **primary transparent regime** is world-invariant for the same kind of reason: a shape rule looks *through* a bracket, so the manifest set of a fixed tree is a function of the tree and not of the world. Measured: `0` of `87` fragments vary, range `0`.

The **opaque** regime, where a bracket hides what is inside it, is the one that can express a preference: `12` of `87` fragments vary, maximum range `5`, and `G0` is among the best worlds on `82` of `87`. That is where the genuine disagreement lives - on `5` fragments `brackets` says `G01` and `visibility_opaque` says `G0`:

```text
(y - k) * (y - k)     (y2 - y1) * (y2 - y1)     u * dv / (v * v)     y * y / (b * b)  twice
```

### 8. Where the ten routed fragments go

Every fragment that leaves the conventional world goes to `G01` (`+ - * /`), and every one of them is an additive form sitting inside a multiplicative context:

```text
a * (r + s) * x       (x - h) * (x - h)       (y - k) * (y - k)       x * x / (a * a)
y * y / (b * b)       (x2 - x1) * (x2 - x1)   (y2 - y1) * (y2 - y1)   u * dv / (v * v)
```

`77` of the `87` fragments are already free under `G0`; `70` are free under every one of the `25` worlds. This is the roadmap's own prediction arriving from a different direction: under `+` binding tightest, the factored form is what becomes parenthesis-free.

### 9. What a named intermediate would have to cost

| objective | names | fixed cost | break-even vs `33` | break-even vs `7` |
|---|---|---|---|---|
| `brackets` | 87 | 0 | 0.3793 | 0.0805 |
| `visibility` | 87 | 14 | 0.2184 | negative |
| `visibility_opaque` | 87 | 7 | 0.2989 | 0.0 |
| `depth` | 87 | 14 | 0.2184 | negative |

At every objective the largest per-name rate at which Model II still wins is `0`. **Model II does not lose because the naming unit was priced against it; it loses at any positive price whatever.**

## Headline questions

1. **Under Model I, does routing beat the best single world after seams are paid? By how much?** Yes, by `4` brackets of `33` under one global host convention (`29` against `33`) and by `1` of `7` against the per-object baseline (`6` against `7`) - and the entire gain comes from two documents that the host convention can no longer read.
2. **Under Model II, same question.** No: `87` against `33` under one global convention, `54` worse, and `87` against `7` per object, `80` worse; the break-even price of a definition line is `0.3793` of a bracket pair and no integer rate wins.
3. **How much of the 0034-style seamless prize survives, as a percentage?** `12.1%` against the global baseline (`4` of `33`), `14.3%` against the per-object baseline (`1` of `7`), and `0.0%` once the document is required to be readable in its own host convention.
4. **Do the objectives route a fragment to the same world?** They agree on `77` of `87` fragments and there are only `3` distinct patterns, but the agreement is mostly silence: `visibility` and `depth` tie all `25` worlds on all `87` fragments and can express no preference at all, while `brackets` and `visibility_opaque` genuinely disagree on `5`.
5. **Is there any object where routing wins under one objective and loses under another?** **No** - the set is empty. Exactly one object ever wins, `sum_of_cubes.factored`, and it wins under all four objectives. Five objects do change verdict with the objective - `circle.center_radius`, `distance_components.squared`, `ellipse.standard`, `hyperbola.standard`, `quotient_rule.split` - but each is a **tie** under `brackets` and a **loss** under the other three, never a win. An earlier revision of this line answered "Yes, `5` of them" while its own trailing clause said "a tie"; the module and the suite always had it right and only the prose overclaimed.
6. **How often is `G0` the right host for the recombined document?** Under `brackets`/inline it is chosen for `24` of `38` documents but is *uniquely* optimal for only `1`; at corpus level the best global inline host is `G18`, not `G0`. Under Model II all `25` worlds tie on `31` of `38` documents, because a skeleton whose operands are names is a chain of leaves and costs nothing anywhere.

## Interpretation

The result reorganises the founding question's routing half around one distinction the earlier oracles could not see.

```text
0034's oracle  ->  what would the corpus cost if each PIECE could pick its convention
this card      ->  what is left after the pieces have to be written down together
```

The prize is real and it is large - `33` brackets of `33` on this corpus, since every fragment is free in some world. But it is not distributed the way a routing architecture needs it to be. **`21` of the `33` are join brackets and no world in the registry gets below `21`.** Routing acts on interiors; the cost is at the joins; the two barely overlap. That is not a fact about this corpus's difficulty, it is a fact about what a join *is*: the bracket at a join exists because two differently-shaped things meet, and which world wrote either of them does not change that they meet.

The second finding is the one an SDK designer should read first. **Model I is not a real architecture at the notational level.** A bracket delimits a scope; it does not carry a convention. An inline document that mixes conventions therefore either keeps every fragment in a rendering the host also reads correctly - in which case it costs exactly the single-convention document, argued from minimality and checked over `54375` cells - or carries fragments the host misreads, in which case it is not a document in one convention at all and needs a side channel the notation does not have. The `4`-bracket gain measured here is the second case, and its price is that `3` of `38` documents stop meaning what they say.

**Model II is the architecture that works, and it does not work by being cheap.** It costs `87` where one convention costs `33`. What it buys is correctness: every line names its own world, nothing leaks across a line, all `38` documents are host-readable, and the object survives every seam. That is the trade the measurement actually exposes - not cost against cost, but **cost against decodability** - and it is why an SDK that routes representations will bind names rather than nest expressions. 0033's Region model already carries this shape: a named intermediate is a state binding, and the decode relation is what a name is for.

The third finding is about the objectives, and it sharpens 0038 rather than contradicting it. At *object* level a world chooses among an object's named writings, and that choice is what makes visibility vary across worlds. At *fragment* level there is only one writing, and under the transparent regime a shape rule looks through brackets, so nothing varies. **Visibility is a property of the choice between writings, not of the writing.** Routing at fragment level cannot use it. The opaque regime restores some discrimination - `12` of `87` fragments - and immediately disagrees with cost on `5` of them, which is the real SDK-design finding of this section: **a router that optimises brackets and a router that optimises what is legible will send the same fragment to different worlds, and the project has no rule that ranks the two.**

## Limits

- **The splitting rule is declared, not discovered, and a different rule would move every number.** Chaining on operator *identity* rather than on the control grammar's level would cut `circle.general` into `2` fragments instead of `6`; chaining more aggressively would produce more, smaller fragments and a larger seam. The rule was fixed before the first measurement and was not tuned until routing won; the report gives what it gave.
- **Cost is brackets and naming units, not runtime.** Nothing here is a statement about how fast anything computes, how readable a document is to a person, or how hard it is to teach. Two documents with the same bracket count can be very differently painful.
- **Model II's naming unit is a modelling choice and must be read as one.** Charging one unit per definition line puts a definition line on the same scale as a bracket pair, which flatters Model II; the break-even rates (`0.3793` against the global baseline, `0.0805` against the per-object one) are published so the reader can substitute his own price. What is *not* a modelling choice is Model II's decodability, which is structural.
- **Model I's seam charges one bracket pair for a convention switch the bracket cannot actually signal.** That is deliberate and it favours Model I: charged honestly, a switch needs a mark the Generation 1 notation does not have. The `host_readable` column is the measurement of what the bracket fails to do, and it is why the headline is stated against the readable variant as well.
- **The corpus is hand-chosen.** `38` composite writings from `29` named objects in four fields are not a sample from any defined population. The filter that produced them is mechanical, but the objects behind it were selected by the project as representative mathematics.
- **The seam obligation certifies the routing PLAN, not the assembled string.** `verify_routing` decodes the skeleton in the host world and each piece in the world it was routed to, and compares that against the single-world composite on the semantic key. It does not re-read the inline document, so a document that was assembled wrongly from a correct plan would not be caught by this check. That is deliberate rather than an oversight: for Model I the document is **not** always faithful in the host world, and that failure is this experiment's own finding, measured and published as the `host_readable` column. A check demanding the document parse correctly in its host would therefore be asserting something the report shows to be false. The two are different questions and both are reported.
- **The 0034 oracle figure is a seamless bound, not an achieved result**, and so is this card's `0`. Both price every piece in its own world and charge nothing whatever for putting the pieces back.
- **The `domain` component of the semantic key is inert** (`NF-2026-00005`): `canonical.py` writes the literal `"R"` for every expression, so the operative discrimination is `(canonical form, excluded points)`. The key is used here unchanged and this is disclosed rather than corrected in passing.
- **Generation 1 has no exponentiation and no unary minus**, so squares are written as products and the fragment population is more multiplicative than real notation would be.
- **`depth` is imported from `parallel_worlds`, which another card is developing concurrently.** The function used is `depth(tree)`, the critical path with a leaf at `0`. If that module's convention changes, this card's depth objective changes with it.

## Evidence classification

- Corpus sizes (`38`, `87`, `67`), fragment counts, the decomposition (`interior` `14` and `9`, `joins` `21`), the oracle numbers (`33`, `7`, `0`) and every verdict total are executable **observations** on this corpus and these `25` worlds.
- Round trip (`3125` checks, `0` failures) and minimality (`1945` brackets, `0` removable) are **verified properties** on the composite-and-fragment grid, re-run from 0034's own audits rather than re-implemented.
- **The obligation at every seam is a verified property**: `304` routings, `304` objects preserved on the semantic key, with a negative control that fails as it should.
- "Host-readable inline routing gains exactly zero" is an **argument** - from the minimality of `render` - whose evidence is the exhaustive `54375`-cell grid with `0` counterexamples. It is a statement about this corpus's fragments, not a theorem about all trees.
- The degeneracy of `depth` and of transparent `visibility` is **structural**, not corpus-conditional: it follows from what a world is allowed to change. The measurements are reported so the claim can be checked, not to establish it inductively.
- "Model II is the architecture an SDK should use" is an **interpretation** of the cost-versus-decodability trade, not a measurement. What is measured is the trade.
- The `26`-bracket gap on this corpus matching 0034's `26` is a **coincidence of two corpora** and is claimed as nothing more.

## Validation

```text
tests/test_fragment_routing.py     47 passed
whole suite                       891 passed, 2 failed   (as of this run)
```

The `2` failures are `tests/test_geometry_atlas.py::test_every_svg_the_report_references_exists_and_is_not_empty` and `::test_every_figure_is_well_formed_paints_its_own_ground_and_stays_inside_the_viewbox`: experiment 0040's figure files, which another card is writing concurrently. Nothing in this card imports or touches `geometry_atlas`, and both failures reproduce with this card's module removed.

Sequential against parallel on the verdict sweep (`16` cores, `12` workers, `304` cells):

```text
sequential                 7.69 s
parallel (12 processes)    3.58 s
speedup                    2.15x   ->  parallel wins
identical records          True
default decision           parallel
```

**The decision is measured, not assumed, and it is taken twice** because the two workloads differ by two orders of magnitude per cell. A verdict cell is two SymPy `simplify` calls at `0.0273` s; a bracket cell is `25` string renderings at `0.00031` s. `should_parallelise` compares the sequential estimate against pool startup plus the divided work, so the verdict sweep parallelises and the bracket sweep does not. Declared constants round the measurements up - `VERDICT_CELL_SECONDS` `0.032`, `BRACKET_CELL_SECONDS` `0.00043`, `POOL_STARTUP_SECONDS` `1.8` against a measured `1.40` - so the estimate is never optimistic about overhead it has to amortise. Worker count is derived from the observed core count with `2` cores of headroom and a cap of `12`; it is never a hardcoded constant.

Mutation testing on an isolated copy in the scratchpad (the canonical tree untouched), `17` mutants at the decisive places:

```text
split descends through the WRONG level                       KILLED
leaves are counted as fragments                              KILLED
the seam forgets that a host can misread a fragment          KILLED
the seam forgets host precedence                             KILLED
a named intermediate is free                                 KILLED
the seam obligation compares strings instead of objects      KILLED
the total drops the seam                                     KILLED
the decode reads every piece in the host world               KILLED
opaque visibility is minimised instead of maximised          KILLED
transparent visibility is minimised instead of maximised     SURVIVED
both visibility objectives read the same regime              KILLED
ties break to the last world instead of the conventional one KILLED
the host is always the control world                         KILLED
the readable audit calls every world readable                KILLED
reassociation is allowed to move a minus                     KILLED
the fragment oracle is priced in the control world           KILLED
host readability is asserted rather than parsed              KILLED

killed 16/17
```

**The survivor is a finding, not a gap.** Flipping the transparent visibility objective from maximise to minimise changes nothing, because that objective's score is world-invariant on all `87` fragments: minimising and maximising select the same tied set of `25` worlds. No test on this corpus can distinguish them, and the test that pins the reason - `test_the_two_visibility_regimes_answer_differently_for_a_structural_reason` - is the honest form of the claim. The same mutation applied to the opaque objective is killed.
