# ParseAtlas experiment 0046: what survives all 25 worlds, and what it costs to survive

## The characterisation, first

A bracket-free writing over the four operators is read identically by all `25` worlds **if and only if
every operator in it is the same operator**.

> **A word is world-invariant iff its operator support has size at most `1`.** Over the full enumeration of
> `87381` words up to `8` operators — `2184525` parses — the predicate and the parser disagree on `0` words.
> Sufficiency is thesis T6. Necessity is constructive, and its witness is checked on every one of the `87348`
> non-invariant words: `0` failures.

Generalised past bracket-free writings, and checked on `437` real sources including every corpus writing:

> **A writing is world-invariant iff every maximal bracket-free chain in it uses at most one distinct
> operator.** `10925` parse checks, `0` disagreements.

The card's second question — whether invariance is bought with brackets and paid for in the structure you give up
choosing — is answered in the section below, and it splits: one half is confirmed, one half fails only
under a regime that cannot express it, and a third reading is confirmed in a stronger form than the
hypothesis proposed. A reader who stops at this sentence should not carry away a simple refutation.

## The hypothesis this card exists to test, and how it came out

The manager's hypothesis, formed from 0040's single invariant curve, was *invariance is bought with brackets, and
the price is the structure you give up choosing*. **Its first half is exact and its second half fails in the form
it was stated.**

> **Bought with brackets: CONFIRMED.** Writing the `50` corpus writings so that all `25` worlds read them
> identically costs `147` bracket pairs against the `7` the cheapest world would pay and the `47` the
> conventional `G0` pays. `49` of the `50` pay; the one that does not is `dfg * dg`, whose operator support has
> size `1`.
>
> **Costs more and shows less: THE PRIMARY REGIME CANNOT EXPRESS THIS COST.** Under experiment 0038's `transparent` regime —
> the one 0038 declared primary, in which a bracket is punctuation because the native reader parses with their own
> grammar — the invariant writing of a tree makes **exactly** the same properties manifest as the cheapest writing
> of that tree. The loss is identically `0` on all `50` writings, so a correlation between price and loss is not
> weak but undefined. Only under the `opaque` robustness regime is anything lost at all: `34` of `50` writings,
> mean `1.78` properties, and there the correlation between the brackets paid and the visibility lost is `0.1861`
> per writing and `-0.1798` per object. The brackets and the blindness are not the same trade.
>
> **What invariance really takes away is the choice: CONFIRMED.** Under free choice `16` of the `34` objects are
> written differently in different worlds. Under an invariance requirement that number is `0`, and not by a
> narrow margin: the invariant cost of a tree does not depend on the world, so every world makes the same choice.
>
> **This is definitional, not empirical, and the distinction matters.** `_look(node, opaque=False)`
> unwraps every `Group`, and every property shape function routes through it, so under the transparent
> regime **no rule can see a bracket at all** — a loss of zero is guaranteed by the regime rather than
> discovered by the sweep. Read it as "the primary regime cannot express this cost", never as "the cost
> was measured to be absent". The opaque regime, where brackets are visible, is where the question has
> empirical content, and there `34` of `50` writings do lose.

## Purpose, and the two questions that must not be mixed

The README has asked one question since the first day — *find the quantities that stay unchanged while the grammar
changes* — and the repository had never answered it as a question in its own right. There are two questions inside
it and they are not the same question.

```text
axis 1   fix the 25 worlds, vary the WRITING   ->  which source strings are read identically?
axis 2   fix the writing, vary the WORLD       ->  which measured quantities do not move?
axis 3   fix the OBJECT                        ->  what does an invariant writing cost?
```

Axis 1 is about strings. Axis 2 is about numbers taken off a string. A statement true on one says nothing about
the other, and every table below carries its axis in its heading.

The `25` worlds are `parseatlas.grammar.all_grammars` — the tied control `G0` plus the `24` strict orderings — the
same registry the whole repository uses. Nothing about them is redefined here.

## Axis 1: which writings are read identically by all 25

A **word** is a bracket-free source with distinct leaves: `a + b * c` is the word `+*`. Distinct leaves are what
make the word and the parse the same object — with the leaves all different, two parses are equal exactly when the
operator sequences were bracketed the same way.

### Necessity, which is the part T6 does not give

T6 gives sufficiency: parsing depends only on the precedence order restricted to the operators that occur, so one
operator means one restriction and one tree. The converse needs an argument, and it is short enough to state:

```text
take any position where two adjacent operators differ:   ... a_k  x  a_(k+1)  y  a_(k+2) ...
the leaf between them attaches to whichever binds tighter
    x above y  ->  a_(k+1) is the RIGHT child of the x node
    y above x  ->  a_(k+1) is the LEFT  child of the y node
both orders are realised among the 24 strict grammars, and the leaves are distinct, so the trees differ
```

Such a position exists exactly when the support has size at least `2`. The construction names the two worlds, so
every non-invariant word carries an explicit disagreeing pair, computed in one pass and then **checked against the
parser rather than trusted**. The hand-worked case is `a + b * c`, where the witness pair is `G01` and `G09`:

```text
G01  ( + - * / )   (a + b) * c      leaf b is the right child of +
G09  ( - * + / )   a + (b * c)      leaf b is the left  child of *
```

### The enumeration, and the null model that would otherwise ruin it

Most short words have small operator support and are invariant for that reason alone, so a pooled invariance rate
over any enumeration is a statement about the length bound and not about precedence. Every rate below is computed
**inside a support stratum**, and each stratum's size is cross-checked against the closed form
`C(4, k) * surj(n, k)` so that the enumeration is known to be complete rather than assumed to be.

| support | words | invariant | invariance rate | closed form agrees |
|---|---|---|---|---|
| `0` | `1` | `1` | `1.0` | yes |
| `1` | `32` | `32` | `1.0` | yes |
| `2` | `2964` | `0` | `0.0` | yes |
| `3` | `33336` | `0` | `0.0` | yes |
| `4` | `51048` | `0` | `0.0` | yes |

Pooled, `33` of `87381` words are invariant, a rate of `0.000378`. **That number is an artifact of the bound and is
reported only so that it is not mistaken for a finding**: raise `max_length` and it falls, with nothing about the
worlds having changed.

### The T6 upper bound, tight at support `1` and loose above it

T6 bounds the distinct trees a word can have by `|support|!`. The bound is tight only at the bottom:

| support | T6 bound | words attaining it | attainment rate | distinct trees over the 24 strict grammars |
|---|---|---|---|---|
| `2` | `2` | `2964` | `1.0000` | `2` on all `2964` |
| `3` | `6` | `16968` | `0.5090` | `5` on `16368`, `6` on `16968` |
| `4` | `24` | `264` | `0.0052` | `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22`, `24` |

At support `2` the bound is not merely observed to be tight, it is forced: the necessity argument gives at least
`2` and T6 gives at most `2`, so **every word with exactly two distinct operators is read in exactly two ways by
the `24` strict grammars**. At support `4` the bound is reached by `264` of `51048` words. The distinct-tree counts
observed at support `4` are `14` `15` `16` `17` `18` `19` `20` `21` `22` and `24` — `23` does not occur anywhere in
this enumeration.

### The opposite pole: the writings no two worlds agree on

| what | count | shortest occurrence |
|---|---|---|
| read identically by all `25` worlds | `33` | length `0` |
| read differently by all `25` worlds | `244` | length `8` |
| attaining the full `24`-tree strict bound | `264` | length `8` |

```text
a + b - c * d + e / f - g * h / i          25 worlds, 25 different trees
```

Every one of the `244` maximally divergent words has length exactly `8`, which is the enumeration bound. **An
enumeration stopping at `7` would have reported that no such word exists.** That is a limitation of the bound, not
a detail of it, and it is why the bound is stated in the limits below.

Largest agreeing block, by support:

| support | largest block sizes observed |
|---|---|
| `0`, `1` | `25` |
| `2` | `12` on `876` words, `13` on `2088` |
| `3` | `4` on `10408`, `5` on `6560`, `8` on `12764`, `9` on `3604` |
| `4` | `1` on `244`, `2` on `14328`, `3` on `27784`, `4` on `4372`, `6` on `3876`, `7` on `444` |

Already at support `2` no more than `13` of the `25` worlds ever agree.

### The tied control is a 25th world, not a copy of one of the 24

`G0` reads `51296` of the `87381` words as a tree **no strict grammar produces** — `58.7` percent of the
enumeration. It never does so when the word's support avoids a whole `G0` level: with no tie inside the support,
`G0`'s restriction is a strict total order and T6 forces it to agree with some strict grammar. That is a proof, and
`0` of the `51296` violate it.

| support | words where `G0` reaches a tree no strict grammar reaches |
|---|---|
| `0`, `1` | `0` |
| `2` | `876` |
| `3` | `18456` |
| `4` | `31964` |

The shortest such words have three operators; one of them is `a + b - c + d`, which `G0` reads left-associated as
`((a + b) - c) + d` while the two strict resolutions of `+` against `-` give `(a + b) - (c + d)` and
`(a + (b - c)) + d`.

### The characterisation, generalised to bracketed writings

A bracket group is a primary: the parser recurses into it, so the operators inside never meet the operators
outside. A writing therefore decomposes into independent bracket-free chains, and the condition applies to each.

> **A writing is world-invariant iff every maximal bracket-free chain in it uses at most one distinct operator.**

The necessity argument assumes the operands of a chain are pairwise distinct, which holds for the enumerated words
by construction and does **not** hold for a corpus that writes `a * a + b * b`. So on real writings this is a
prediction that has to be checked against a parse, and it was: `437` distinct sources — the `60` axis-2 entries,
the `50` invariant writings axis 3 builds, and every word up to `4` operators — `10925` parse checks, `0`
disagreements, `68` of the `437` invariant.

Ten of the `55` movable axis-2 entries are already read identically by all `25` worlds, and they are exactly the
ones the predicate names:

```text
(x + 1)/(x - 2)              a * (b + c)                (a + b) * (a + b)
(a + b) * (a - b)            a * (x - r) * (x - s)      (a + b) * (a + b) * (a + b)
(y2 - y1) / (x2 - x1)        (x1 + x2) / 2              (fxh - fx) / h            dfa * (x - a)
```

## Axis 2: which measurable quantities are constant across the worlds

Now the writing is held fixed and the world varies. `60` entries — experiment 0021's six expressions, the `50`
declared writings of 0038's corpus, and four single-operator chains — against `25` worlds is `1500` cells. Every
cell is parsed and canonicalised on its own; a T6 deduplication would be exact, because every quantity here is a
function of the tree, and it is deliberately not taken so that the grid is an observation rather than a derivation.

### The vocabulary, with its kind declared before anything was measured

`16` quantities, each labelled **in advance** as `by_construction` or `measured`.

| quantity | kind | why it cannot move, where that applies |
|---|---|---|
| `token_count` | `by_construction` | the tokenizer never receives a grammar |
| `leaf_multiset` | `by_construction` | one leaf node per number or name token, never invented or dropped |
| `operator_multiset` | `by_construction` | one `Binary` per operator token; precedence chooses the children, never the label |
| `node_count` | `by_construction` | `2k + 1` for `k` operators, so it carries nothing the operator count does not |
| `parse_tree` | `measured` | |
| `critical_path_depth` | `measured` | |
| `peak_live` | `measured` | |
| `semantic_key` | `measured` | |
| `excluded_points` | `measured` | |
| `defined_everywhere` | `measured` | |
| `free_symbols` | `measured` | |
| `total_degree` | `measured` | |
| `polynomial_degree` | `measured` | |
| `root_count` | `measured` | |
| `pole_count` | `measured` | |
| `expanded_term_count` | `measured` | |

`operator_multiset` is experiment 0021's finding. **It is a restatement of how parsing works and is worth nothing
as a discovery**, which is why it sits in its own group and is never counted beside a quantity that could have
moved and did not.

### The three groups

An entry is `frozen` when its operator support has size at most `1`, because axis 1 already guarantees one tree
there and therefore one value of everything. `5` of the `60` entries are frozen; every rate below is over the `55`
movable ones. An entry where a quantity does not apply in any world is dropped from that quantity's denominator
rather than scored as agreement.

| group | `by_construction` | `measured` |
|---|---|---|
| **always** constant | `token_count`, `leaf_multiset`, `operator_multiset`, `node_count` — `4` | **none — `0`** |
| **sometimes** constant | none — `0` | all `12` |
| **never** constant | none — `0` | none — `0` |

> **Not one measured quantity is invariant across all `25` worlds on every movable corpus entry.** The only
> quantities that survive all `25` unconditionally are the four that cannot fail to.

| quantity | kind | constant on | rate |
|---|---|---|---|
| `token_count` | `by_construction` | `55` of `55` | `1.0000` |
| `leaf_multiset` | `by_construction` | `55` of `55` | `1.0000` |
| `operator_multiset` | `by_construction` | `55` of `55` | `1.0000` |
| `node_count` | `by_construction` | `55` of `55` | `1.0000` |
| `defined_everywhere` | `measured` | `53` of `55` | `0.9636` |
| `pole_count` | `measured` | `39` of `41` | `0.9512` |
| `free_symbols` | `measured` | `52` of `55` | `0.9455` |
| `excluded_points` | `measured` | `47` of `55` | `0.8545` |
| `root_count` | `measured` | `28` of `41` | `0.6829` |
| `polynomial_degree` | `measured` | `27` of `40` | `0.6750` |
| `expanded_term_count` | `measured` | `33` of `55` | `0.6000` |
| `peak_live` | `measured` | `31` of `55` | `0.5636` |
| `total_degree` | `measured` | `14` of `43` | `0.3256` |
| `critical_path_depth` | `measured` | `14` of `55` | `0.2545` |
| `semantic_key` | `measured` | `13` of `55` | `0.2364` |
| `parse_tree` | `measured` | `10` of `55` | `0.1818` |

The ordering is itself a result: the quantities nearest the top are the coarsest, and coarseness is the only thing
that buys stability. `defined_everywhere` is a single bit and survives `53` of `55`; `semantic_key` is the object
itself and survives `13`.

### Experiment 0021 reproduced as the calibration case

| expression | `operator_multiset` constant | distinct `critical_path_depth` | distinct `semantic_key` |
|---|---|---|---|
| `2*t + 1 - t/2` | yes | `2` | `8` |
| `a + b*c - d/e` | yes | `2` | `10` |
| `2*x*x + 1 - x/2` | yes | `3` | `8` |
| `a - b*c + d/e - f` | yes | `3` | `16` |
| `a/b + c*d - e/f + g` | yes | `3` | `18` |
| `(x + 1)/(x - 2)` | yes | `1` | `1` |

0021's rigid rational expression is the one of the six the convention cannot move, and the reason is now
nameable: each of its three chains — `+`, `-`, `/` — uses one operator.

### What a convention can do to a formula, in three cases

`defined_everywhere` moves on exactly `2` of the `55` movable entries, and both are the trapezoid area:

```text
(a + b) / 2 * h      13 worlds  h*(a + b)/2      defined everywhere
                     12 worlds  (a + b)/(2*h)    undefined at h = 0
```

**A precedence convention decides whether the trapezoid-area formula has a pole.** Two more, from the same grid:

```text
2*t + 1 - t/2                    4 of 25 worlds read it as the constant 1, with no variable left
(a + b) * (a*a - a*b + b*b)      8 of 25 worlds read it as identically 0
```

## Axis 3: what invariance costs

### The invariant writing, and the proof that it is minimal

Quantifying `parseatlas.notational_cost.needs_brackets` over all `25` worlds instead of applying it to one gives
the rule for the writing every world reads back as the same tree:

```text
a leaf                             never bracketed
a Binary RIGHT child               always bracketed
a Binary LEFT  child               bracketed iff its operator differs from its parent's
```

Both halves are checked and not assumed. Round trip: `1250` checks — `50` writings in `25` worlds — `0` failures.
Minimality: each of the `147` bracket pairs is deleted and a world that then reads a different tree is named;
`0` pairs survive deletion in all `25`.

### Bought with brackets

| what is counted | invariant writing | cheapest world | conventional `G0` |
|---|---|---|---|
| bracket pairs over the `50` writings | `147` | `7` | `47` |
| bracket pairs over the `34` objects, each in its chosen writing | `84` | `0` | `17` |

`49` of the `50` writings pay something; `33` of the `34` objects do. Mean object price `2.4706` pairs, maximum
`6`. The most expensive single writing is the general form of the circle, at `9` pairs against `0`:

```text
cheapest world   x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k
invariant        ((((x * x) - (2 * h * x)) + (h * h) + (y * y)) - (2 * k * y)) + (k * k)
```

The one writing where invariance is free is `dfg * dg`, the chain rule, whose operator support has size `1`. That
is axis 1's characterisation reappearing on axis 3: **the writings that cost nothing to make invariant are exactly
the ones that were already invariant.**

### Shows less? Not under the regime that matters

Experiment 0038 declared two rule regimes and this experiment imports both unchanged.

| regime | writings losing manifest properties | mean loss | correlation with the price paid |
|---|---|---|---|
| `transparent` (0038's primary) | `0` of `50` | `0.00` | undefined — the loss does not vary |
| `opaque` (0038's robustness) | `34` of `50` | `1.78` | `0.1861` |

Under `transparent` a bracket is punctuation: the native reader of a world parses the string with their own
grammar and recovers the tree for free, so **how much of a fixed tree is bracketed cannot change what it makes
manifest**. The measured loss is identically zero across all `50` writings, which is why a correlation is
undefined rather than small. Under `opaque` a bracket hides what is inside it, and there the loss is real but does
not track the price: `15` writings pay brackets and lose nothing at all, including the circle's centre-radius form
at `6` pairs and `0` lost.

Opaque loss, distributed:

| properties lost | writings |
|---|---|
| `0` | `16` |
| `1` | `9` |
| `2` | `9` |
| `3` | `6` |
| `4` | `6` |
| `5` | `4` |

At the object level, where the comparison is against what the world would otherwise have chosen rather than
against the same tree, the sign of the effect is not even stable: under `transparent` `11` objects show less and
`5` show **more**, mean `+0.18`, correlation `0.1877`; under `opaque` `29` show less and `0` show more, mean
`0.9647`, correlation `-0.1798`. The five that show more under an invariance requirement are
`calibration_quadratic`, `difference_of_cubes`, `sum_of_cubes`, `quadratic` and `perfect_square_trinomial`. For
four of them the cheapest invariant writing is the monomial-sum one, which carries more of 0038's vocabulary than
the factored form some worlds would otherwise choose. `quadratic` goes the other way and is the sharper case: its
expanded writing `a * x * x - a * (r + s) * x + a * r * s` makes nothing manifest at all, because the leading
coefficient sits behind a bracketed sum, so the factored writing that invariance picks is the richer one.

### What invariance really takes away

| how many objects | free choice | invariance required |
|---|---|---|
| written differently in different worlds | `16` of `34` | `0` of `34` |
| manifest set differs by world, `transparent` | `16` of `34` | `0` of `34` |
| manifest set differs by world, `opaque` | `29` of `34` | `0` of `34` |

The zero is structural, not narrow. The invariant cost of a tree does not depend on the grammar, so the cheapest
invariant writing is the same writing in every world: **an invariance requirement does not reduce what each world
sees, it deletes the differences between what they see.** That is the half of the manager's hypothesis that
survives, and it survives in a stronger form than it was stated.

### The case the hypothesis was formed from

0040's one convention-stable curve, `(x - y) * (x + y)`, is this corpus's `difference_of_squares` in its factored
writing.

| quantity | value |
|---|---|
| invariant writing | `(a + b) * (a - b)` |
| invariant cost | `2` pairs |
| cheapest world | `G01`, at `0` pairs |
| conventional `G0` | `2` pairs |
| price against the cheapest world | `2` |
| manifest loss, `transparent` | `0` |
| manifest loss, `opaque` | `2` |

0040 read this curve as invariant *because it is already factored*. The sharper statement is that its two brackets
are exactly the ones every world requires, and that a world exists — `G01` — which would have written the same
object with none of them. The invariance was not free; `G0` simply happens to pay the same price.

## Multicore, by measurement

Repository policy is multicore by default and allows a sequential path where a measurement justifies one. This
experiment has three independent workloads of very different shapes, and each is decided on its own numbers. All
constants below were measured on this machine for this module and none is inherited.

```text
cores observed                              16
workers = min(cores - 2, 12, units)         12
pool startup, minimum of three raises       1.289 s   declared 2.5 s
```

| workload | units | per unit | sequential | parallel | predicted | measured winner | identical |
|---|---|---|---|---|---|---|---|
| axis-1 words | `5461` | `6.5e-04` s | `3.532` s | `2.021` s | parallel | parallel | yes |
| axis-2 cells | `1500` | `1.25e-02` s | `18.765` s | `4.927` s | parallel | parallel | yes |
| axis-3 objects | `34` | `1.01e-02` s | `0.343` s | not raised | sequential | sequential | not applicable |

The axis-3 workload is left **sequential by measurement**: `34` objects at `1.01e-02` s is `0.34` s of work, and a
pool that costs `2.5` s to raise cannot repay itself against it. The full axis-1 sweep at `max_length = 8` is
`87381` words, `57` s of sequential work at the measured per-word cost, and runs in `15.52` s across `12`
workers. Parallelism changes only how fast: sequential and parallel results are asserted equal on both parallel
workloads, in the decision run and in the test suite.

The pool startup is dominated by each worker importing this module and therefore SymPy. **The machine is shared
with a concurrently running card, so the per-unit costs move between runs**, and across three recorded runs they
ranged `5.4e-04` to `9.0e-04` s per word, `1.06e-02` to `1.34e-02` s per cell, and `1.01e-02` to `2.19e-02` s per
object, with the pool startup between `1.289` and `1.808` s. Each declared constant is therefore set to the value
**least favourable to the conclusion it supports**: the lowest per-unit cost and the highest startup where the
answer is parallel, the highest per-unit cost where the answer is sequential. The two parallel decisions and the
one sequential decision hold across the whole observed range.

## Limits

- **The enumeration is bounded at `8` operators**, that is `9` leaves, `87381` words. What lies beyond it is not
  measured, and the bound is load-bearing rather than incidental: the `244` words read differently by all `25`
  worlds and the `264` words attaining the full `24`-tree bound all appear at length `8` exactly, so an
  enumeration stopping at `7` would have reported both as empty. The characterisation itself is proved, not only
  enumerated, so it is not at risk from the bound; every count in this report is.
- **Invariance here is of the PARSE and not of the value.** `a - b - c` is read as `(a - b) - c` by all `25`
  worlds, and `-` is not associative: `(a - b) - c` and `a - (b - c)` differ by `-2c`. A single repeated operator
  being invariant is a statement about the tree every world builds, and it says nothing about arithmetic. The
  same holds for `/`. This is pinned in the test suite so it cannot blur.
- **The by-construction invariants are separated, and the separation is the point.** `token_count`,
  `leaf_multiset`, `operator_multiset` and `node_count` cannot move, because the tokenizer never sees a grammar
  and the parser makes exactly one `Binary` per operator token. Reporting them alongside a measured invariant
  would be reporting that parsing consumes each token once. `node_count` is weaker still: it is `2k + 1` for `k`
  operators and carries nothing `operator_multiset` does not.
- **The corpus is hand-chosen.** The `34` objects and `50` writings are experiment 0038's corpus, which is 0037's
  named-law corpus plus 0038's calibration quadratic, imported whole; the six axis-2 calibration expressions are
  0021's. Nothing here samples a population of mathematics, so `16` of `34` and `49` of `50` are properties of
  this corpus. The correlations are computed over `34` and `50` points respectively and are indications, not
  population statistics.
- **The `domain` component of the project's semantic key is inert** (`NF-2026-00005`): `parseatlas.canonical`
  writes the literal `"R"` for every expression, so the operative discrimination in `semantic_key` is
  `(canonical form, excluded points)`. The key is used here unchanged and this is disclosed rather than corrected
  in passing.
- **The manifest vocabulary and its two regimes are 0038's declared rules, not facts about mathematics.** The
  visibility numbers on axis 3 are relative to them, and a different, equally defensible rule set would move them.
  What does not depend on the rule set is the `transparent` result, which follows from the regime's definition:
  looking through brackets means bracket count cannot change what is manifest.
- **The necessity proof assumes distinct operands.** It is exact for the enumerated words, which have distinct
  leaves by construction. For bracketed writings with repeated operands the generalised characterisation is
  checked against the parser on `437` sources rather than proved, and a coincidence at a length beyond those
  sources is not excluded.
- **`peak_live` counts values, not bytes** — it is the Sethi-Ullman register number, imported from experiment
  0044, and it is a structural bound rather than a memory benchmark.
- **`semantic_key` is a finer discriminator than the `sympy.count_ops` counts 0021 published**, so the
  distinct-value columns here and in 0021's canonical-cost table are different quantities and must not be read
  against each other.
- **No wall-clock claim is made about mathematics.** The only timings in this report are the concurrency
  numbers, which are about this program on this machine.

## Evidence classification

- the characterisation `support <= 1` on bracket-free words: **observation** over `87381` words with `0`
  disagreements, and **symbolically justified** — T6 gives sufficiency and the adjacent-differing-pair
  construction gives necessity;
- the constructive witness pair for every non-invariant word: **observation**, `0` failures over `87348` words;
- the generalised characterisation on bracketed writings: **observation** over `437` sources with `0`
  disagreements; the necessity half is justified only where operands are distinct;
- every word with support exactly `2` having exactly `2` trees over the `24` strict grammars: **observation** on
  `2964` words, and **symbolically justified** by T6 together with the witness construction;
- `G0` reaching a tree no strict grammar reaches on `51296` words: **observation**; that it can only do so when
  the support contains a whole `G0` level is **symbolically justified** by T6 and confirmed by `0` violations;
- the four `by_construction` invariants: **symbolically justified**, and reported as restatements of the parser's
  shape rather than as findings;
- no quantity of the `measured` kind being constant on every movable entry: **observation** over `1500`
  cells;
- the trapezoid area losing and regaining its pole, `2*t + 1 - t/2` collapsing to a constant, and the sum of
  cubes collapsing to zero: **observation**;
- the invariant writing round-tripping in all `25` worlds and every one of its `147` brackets being load-bearing:
  **observation**, `0` failures on both;
- invariance costing `147` pairs against `7`: **observation** over this hand-chosen corpus;
- the zero manifest loss under `transparent`: **observation** on all `50` writings, and **justified** by the
  regime's own definition;
- an invariance requirement collapsing the per-world writing choice to one: **observation** over `34` objects,
  and **symbolically justified** — the invariant cost of a tree does not depend on the grammar;
- the correlations `0.1861`, `0.1877` and `-0.1798`: **observation** over `50` and `34` points of a hand-chosen
  corpus; no population claim is made;
- that a world with a shorter critical path or a lower `peak_live` would evaluate faster on real hardware:
  **hypothesis** — not observed here and not observed anywhere in this repository.

## Mutation check

The tests are pinned to literals, so the question is whether they would notice a defect. `13` mutants, each a
one-line change to a load-bearing decision in `invariants.py`, were applied on an **isolated copy** of the tree
and run against a targeted subset of the test file. `12` were killed on the first isolated pass. The last one
survived, and it was a real gap rather than an equivalent mutant: it made the per-writing record report the
invariant surface's manifest set where the cheapest world's belongs. Under `transparent` the two are identical —
that is the finding of this experiment, so no `transparent` assertion can ever separate them — and the only
assertions that could tell them apart were the `opaque` ones, which the file did not carry. They were added and
the mutant is killed. `13` of `13`.

One methodological note is recorded here because it invalidated a first attempt. This repository installs
`parseatlas` as an **editable** install pinned to the working tree, so running pytest from a copied directory
still imports the working tree, and every mutant reports as a survivor without ever having been loaded. The runner
therefore sets `PYTHONPATH` to the copy, proves by an import probe that the module under test lives inside the
copy, and runs a deliberately broken canary mutant that must be killed before any result is trusted. All `9`
mutants of the first, unisolated attempt reported as survivors; not one of them actually was.

## Validation

```text
python -m pytest -q tests/test_invariants.py
37 passed
```

```text
python -c "from parseatlas.invariants import axis1_report; r = axis1_report(8); print(r['word_count'], r['parse_count'], r['disagreement_count'], r['witness_failure_count'], r['characterisation_holds'], r['strata_match_closed_form'], r['control_reaches_new_tree'], r['control_new_needs_tied_pair']); [print(k, v['words'], v['invariant'], v['t6_upper_bound'], v['bound_attained'], v['control_reaches_new_tree']) for k, v in r['strata'].items()]"
```

```text
python -c "from parseatlas.invariants import axis2_report; r = axis2_report(); print(r['entry_count'], r['cell_count'], r['movable_entries'], r['frozen_entries']); print(r['groups']['by_construction']['always']); print(r['groups']['measured']['always'], r['groups']['measured']['never']); [print(k, v['kind'], v['group'], v['movable_constant'], v['movable_entries']) for k, v in r['quantities'].items()]"
```

```text
python -c "from parseatlas.invariants import price_report; r = price_report(); print(r['writing_total_invariant'], r['writing_total_cheapest'], r['writing_total_control'], r['bracket_total_invariant'], r['bracket_total_cheapest'], r['bracket_total_control']); print(r['writings_paying'], r['writings_free'], r['objects_paying'], r['objects_free'], r['max_price']); print(r['writings_losing'], r['writing_loss_mean'], r['writing_price_loss_correlation']); print(r['objects_with_world_dependent_writing'], r['objects_with_world_dependent_writing_under_invariance'], r['invariant_writing_holds'], r['invariant_writing_minimal'])"
```

```text
python -c "from parseatlas.invariants import parallel_decision; d = parallel_decision(); print(d['cores'], round(d['startup']['seconds'], 3)); [print(k, d[k]['units'], d[k]['workers'], round(d[k].get('sequential_seconds', 0), 3), round(d[k].get('parallel_seconds', 0), 3), d[k].get('identical'), d[k]['predicted_parallel']) for k in ('words', 'cells', 'price')]"
```
