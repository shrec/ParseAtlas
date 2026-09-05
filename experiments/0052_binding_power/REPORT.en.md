# ParseAtlas experiment 0052: precedence is a number, and what happens when it is a vector

## What the second dimension buys over the first

**It buys `17131` new class occurrences across the `3125` sources of the corpus where the first widening
bought none — `12302` of them distinct as objects.**

Both numbers are given because they answer different questions and an earlier revision of this line gave
only the first while calling it distinct objects, which inflates it by `39%`. `17131` is the sum over
sources of the classes the pair reaches that associativity does not — the convention experiment 0030 used,
and the one that makes the columns below comparable. Counted as globally distinct classes the totals are
`8422` for precedence, `8422` for associativity and `20724` for the pair, so the gain is `12302`. **The
verdict survives both readings, and so does 0030's zero: `8422` equals `8422` globally as well.**

Experiment 0030 added associativity as a second grammar axis and reported, on the `3125`-expression
0024 corpus, fifty percent more syntax and no new mathematics. This experiment replaces the scalar
binding power by a pair and runs the same corpus through the same semantic key:

```text
0024 corpus, 3125 expressions        precedence     + associativity      binding-power pair
AST forms                                 22500              33750                   77500
semantic classes                          14175              14175                   31306
new classes over the middle column                               0                   17131
sources gaining a class                                          0                    1750
```

The first two columns are 0030's own numbers, reproduced here to the digit. The third is what one
extra component per operator reaches. `14175` classes become `31306`, a factor of `2.209`, and
`1750` of the `3125` sources — `56.000` percent of them — carry a reading no grammar in the
`precedence x associativity` registry can produce.

This is not a bigger space finding more of the same. It is a different kind of freedom, and the
stratification by operator support says so:

```text
support             expressions   precedence   + associativity      pair       new
{* + -}                    1875         7875              7875     22125     14250
{* + - /}                  1250         6300              6300      9181      2881
```

Both strata gain, and the smaller support gains more — **but that is not the control it was written as.**
The parser space is the same `6902` in both strata, so their relative gains say nothing about whether the
rise is the space widening. The genuine control is the one further down: **every single-operator stratum
gains `0`, in all three of them**, with the same `6902` parsers in play. That corpus has no single-operator
stratum, which is why the control lives there and not here.

## Purpose

The owner asked whether non-flat modelling is possible and whether there are three-dimensional ways.
`parseatlas.grammar.Grammar.binding_power` returns `dict[str, int]` — one integer per operator — and
that single integer is the flatness of the project. Every result in the repository, all 25 worlds,
is a slice of a richer space through the plane where that number is scalar.

The generalisation is classical and is what Pratt parsing already uses:

```text
1D    binding_power[op] = n                 the Generation 1 model, 25 worlds
2D    binding_power[op] = (left, right)     precedence and associativity, unified
3D    plus a prefix binding power           unary operators integrated
```

The card also put a claim about the project's own past. In a binding-power pair associativity is not
a separate parameter, it is the order within the pair; if that is right, experiment 0030, which
treated associativity as a separate axis, was varying a derived parameter as though it were
independent. That claim is verified below rather than assumed, and the verdict has two halves which
have to be stated together.

```text
half one    0030's registry embeds.  Associativity really is the order within the pair.
half two    the pair reaches parses that registry cannot.  It is a proper subspace.
```

## Space structure

### The parser

`VectorParser` is the textbook Pratt loop. It differs from `parseatlas.parser.Parser` in one line:

```text
Generation 1     while power[op] >= minimum:  right = expression(power[op] + 1)
vector           while left[op] >  minimum:   right = expression(right[op])
```

Substituting `left = 2p` and `right = 2p + 1` turns the first into the second exactly, because
`p >= m` is the same statement as `2p > 2m - 1`. So the 2D image of a Generation 1 grammar is a
change of variables and not a fit, and `agreement_audit` is the check that no arithmetic slipped.

### Associativity is the order within the pair

`a - b - c` parses left when `left` is at most `right` for that operator, and right when `left`
exceeds `right`. After consuming an operator the parser continues with a minimum taken from the
right component, so the equal-power operator is either left for the loop or swallowed by the
recursion, and that single comparison is the whole of associativity. Conventionally `(n, n+1)` is
left and `(n+1, n)` is right: the same two numbers, written in the other order.

### The behaviour of a vector grammar is a boolean matrix

The recursion is entered only with `0` — at top level and after an opening bracket — or with the
right component of some operator. With every `left` at least `1` the top-level test always passes,
so the entire parser is decided by

```text
M[a][b] = left(a) > right(b)
```

and every cell of that matrix is read off by the two-operator word `x b y a z`, which parses
right-leaning exactly when the cell holds. *Distinct matrix* and *distinct parser* are therefore
the same thing, which is what makes the behavioural quotient exact rather than a sampling.

### The enumeration bound saturates

The matrix is realisable exactly when the sets `S(a) = {b : left(a) > right(b)}` form a chain under
inclusion, because the `left` values are totally ordered. A chain of `m` subsets of an `m`-element
set is realised by `left` values in `2..m+1` and `right` values in `1..m+1`, so `bound = m + 1`
already reaches every parser there is. The scan observes this instead of asserting it:

| bound | raw assignments | distinct parsers |
| --- | --- | --- |
| 2 | 256 | 226 |
| 3 | 6561 | 2726 |
| 4 | 65536 | 6326 |
| 5 | 390625 | 6902 |
| 6 | 1679616 | 6902 |
| 7 | 5764801 | 6902 |

The bound is therefore **not** a computational limit at which an answer is read. Past `5` the raw
assignment count grows by another factor of `14.76` and the behavioural count does not move at all.

The two counts are worth reading side by side. At the saturating bound `390625` assignments name
`6902` parsers, so the *coordinates* are `56.596` times redundant while the space itself is not:
most of an enumeration over vectors is spent renaming parsers it has already found.

### The sizes of the spaces

```text
operators m                    1       2       3       4
distinct parsers, 2D           2      14     230    6902
distinct parsers, 3D           4      46    1066   41506
```

## Corpus

The reach sweep uses the word family of experiments 0020, 0023 and 0030 unchanged: every word of
length `k` over the alphabet of four operators for `k = 2..6`, canonical leaves `a, b, c`, and the
full Catalan set of parenthesizations as the denominator. That is `5456` words and `587616`
word-and-tree pairs.

The conservative-extension audit runs on `36` sources: the six expressions of 0020, the five of
0030's split corpus, the ten of its chain probe, the five of the 0017 corpus, and fifteen more
carrying nested brackets, fractions and numeric leaves, so the claim is not tested only on flat
words.

The semantic corpora are 0030's own, so the class counts stand in one column with its:

```text
0017 corpus              5 expressions
0020 corpus              6 expressions
0024 restriction probe  10 expressions
chain probe             10 expressions
0024 corpus           3125 expressions      corpus_matrix.generate_corpus()
```

## Observed results

### The conservative-extension audit

Every one of the 25 Generation 1 grammars has a 2D image, and its parse equals
`parseatlas.parser.parse` on every source, cell by cell:

```text
grammars                    25
sources                     36
cells                      900
agreements                 900
divergences                  0
grammars with no image       0
```

The images are explicit. The scalar is read from the level view, so the tied control grammar `G0`
keeps both of its ties:

| grammar | plus | minus | times | over |
| --- | --- | --- | --- | --- |
| G0 | (2, 3) | (2, 3) | (4, 5) | (4, 5) |
| G01 | (8, 9) | (6, 7) | (4, 5) | (2, 3) |
| G02 | (8, 9) | (6, 7) | (2, 3) | (4, 5) |
| G03 | (8, 9) | (4, 5) | (6, 7) | (2, 3) |
| G04 | (8, 9) | (2, 3) | (6, 7) | (4, 5) |
| G05 | (8, 9) | (4, 5) | (2, 3) | (6, 7) |
| G06 | (8, 9) | (2, 3) | (4, 5) | (6, 7) |
| G07 | (6, 7) | (8, 9) | (4, 5) | (2, 3) |
| G08 | (6, 7) | (8, 9) | (2, 3) | (4, 5) |
| G09 | (4, 5) | (8, 9) | (6, 7) | (2, 3) |
| G10 | (2, 3) | (8, 9) | (6, 7) | (4, 5) |
| G11 | (4, 5) | (8, 9) | (2, 3) | (6, 7) |
| G12 | (2, 3) | (8, 9) | (4, 5) | (6, 7) |
| G13 | (6, 7) | (4, 5) | (8, 9) | (2, 3) |
| G14 | (6, 7) | (2, 3) | (8, 9) | (4, 5) |
| G15 | (4, 5) | (6, 7) | (8, 9) | (2, 3) |
| G16 | (2, 3) | (6, 7) | (8, 9) | (4, 5) |
| G17 | (4, 5) | (2, 3) | (8, 9) | (6, 7) |
| G18 | (2, 3) | (4, 5) | (8, 9) | (6, 7) |
| G19 | (6, 7) | (4, 5) | (2, 3) | (8, 9) |
| G20 | (6, 7) | (2, 3) | (4, 5) | (8, 9) |
| G21 | (4, 5) | (6, 7) | (2, 3) | (8, 9) |
| G22 | (2, 3) | (6, 7) | (4, 5) | (8, 9) |
| G23 | (4, 5) | (2, 3) | (6, 7) | (8, 9) |
| G24 | (2, 3) | (4, 5) | (6, 7) | (8, 9) |

The audit is itself checked by being shown a divergence. Handing it a deliberately wrong image map
that writes every pair in the other order makes it report all `25` grammars as imageless; handing it
a map that is correct everywhere except a swap of plus and minus inside `G07` makes it report
exactly `G07` and leave the other `24` at zero divergences.

### The 0030 claim, verified

The whole precedence-times-associativity registry embeds, control variants included:

```text
0030 grammars                       388
sources                               5
cells                              1940
agreements                         1940
divergences                           0
distinct images                     388
```

So associativity is a coordinate of the pair, not an axis beside it, and 0030 was indeed varying a
derived parameter. But the embedding is not onto, and the gap is where the result is:

```text
flat grammars, every ordering of levels with a side per level      730
distinct parsers they induce                                       730
distinct parsers a binding-power pair induces                     6902
parsers with no flat description                                  6172
flat fraction                                                  10.577 %
```

The flat family here is more generous than anything the project has used: it is every ordered
partition of the four operators into levels — all `75` of them, `24` strict and `51` carrying ties —
crossed with a side per level. It reaches `730` parsers. The pair reaches `6902`. Nine tenths of the
parsers in the pair space cannot be written as *any* scalar precedence with *any* associativity.

The extra freedom is not more associativity. It is **asymmetric interaction between different
operators**: a pair may put times above plus on the left and below it on the right, which no single
number per operator can say. With times at `(10, 1)` and plus at `(2, 3)`:

```text
a + b * c     ->   a + (b * c)      times behaves as the tighter operator
a * b + c     ->   a * (b + c)      times behaves as the looser operator
```

### Reach against 0020 and 0030

The same `k = 2..6` range, the same words, the same denominator. Ground truth is real parsing in all
three columns, and the pair column is exhaustive over the `6902` parsers rather than sampled:

| k | words | C(k) | trees | precedence | + associativity | pair |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 2 | 32 | 28 | 32 | 32 |
| 3 | 64 | 5 | 320 | 196 | 260 | 284 |
| 4 | 256 | 14 | 3584 | 1252 | 2000 | 2552 |
| 5 | 1024 | 42 | 43008 | 7180 | 14192 | 22160 |
| 6 | 4096 | 132 | 540672 | 37420 | 92504 | 181640 |

The first two columns reproduce 0020 and 0030 exactly, which is how the third is to be trusted.
As coverage of the parenthesization space:

| k | precedence % | + associativity % | pair % |
| --- | --- | --- | --- |
| 2 | 87.500 | 100.000 | 100.000 |
| 3 | 61.250 | 81.250 | 88.750 |
| 4 | 34.933 | 55.804 | 71.205 |
| 5 | 16.695 | 32.999 | 51.525 |
| 6 | 6.921 | 17.109 | 33.595 |

And as the honest ratio, the fraction of the precedence gap each widening closes:

| k | unreachable before | associativity recovers % | pair recovers % |
| --- | --- | --- | --- |
| 2 | 4 | 100.000 | 100.000 |
| 3 | 124 | 51.613 | 70.968 |
| 4 | 2332 | 32.075 | 55.746 |
| 5 | 35828 | 19.571 | 41.811 |
| 6 | 503252 | 10.946 | 28.658 |

Aggregate over `k = 2..6`:

```text
total trees                      587616
precedence reachable              46076      7.841 %
with associativity               108988     18.547 %
with a binding-power pair        206668     35.171 %
unreachable before               541540     92.159 %
unreachable after associativity  478628     81.453 %
unreachable after the pair       380948     64.829 %
associativity recovered           62912     11.617 %   of the gap
the pair recovered               160592     29.655 %   of the gap
```

**The plain answer the card asked for: the 2D space reaches more than precedence with
associativity.** It recovers `29.655` percent of the gap where associativity recovered `11.617`,
and it reaches `1.896` times as many trees. The associativity TOTAL is at or below the pair total in every cell of the sweep. The embedding predicts
set containment and containment does hold by construction, but what the sweep records is a comparison of
counts, not of sets — `reach_2d` compares totals and `_reach_pattern` returns only a length. The stronger
statement is warranted by the embedding, not by this table.

`k = 6` is a **computational limit** and it is named here, where the answer is read. The sweep is
`5456` words and `587616` trees; the next length is `16384` words and `7028736` trees and was not
run. What is known past it is the ceiling table below, which is arithmetic: it fixes the direction
of the curve and not its size.

Per expression, on 0020's six sources:

| expression | k | C(k) | precedence | + associativity | pair |
| --- | --- | --- | --- | --- | --- |
| `a + b*c` | 2 | 2 | 2 | 2 | 2 |
| `a + b + c` | 2 | 2 | 1 | 2 | 2 |
| `2*t + 1 - t/2` | 4 | 14 | 14 | 14 | 14 |
| `a + b*c - d/e` | 4 | 14 | 14 | 14 | 14 |
| `a - b*c + d/e - f` | 5 | 42 | 19 | 24 | 42 |
| `2*x*x + 1 - x/2 + x` | 6 | 132 | 17 | 42 | 74 |

```text
mean precedence coverage        0.6801948051948052      identical to 0020
mean associativity coverage     0.814935064935065       identical to 0030
mean pair coverage              0.9267676767676768
```

`a - b*c + d/e - f` is the sharpest single cell: the pair space reaches **all** `42`
parenthesizations of a source where precedence reached `19` and associativity `24`.

### What a third component buys

A prefix operator has one operand and therefore one binding power. With no third number that power
is *derived* — it can only be the operator's own right component — and the third dimension frees it.
The family is the same word set carrying one leading prefix minus; such a word admits `C(k+1)`
trees, the Catalan convolution.

| k | words | trees per word | trees | derived prefix | free prefix | gained | ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 5 | 80 | 71 | 76 | 5 | 1.0704 |
| 3 | 64 | 14 | 896 | 638 | 736 | 98 | 1.1536 |
| 4 | 256 | 42 | 10752 | 5540 | 6952 | 1412 | 1.2549 |
| 5 | 1024 | 132 | 135168 | 45410 | 62320 | 16910 | 1.3724 |

```text
total trees                146896
derived prefix              51659     35.167 %
free prefix                 70084     47.710 %
gained                      18425
gained, as a fraction of the derived-prefix gap        19.346 %
```

The curve is **still moving**: the ratio of free to derived rises monotonically `1.0704`, `1.1536`,
`1.2549`, `1.3724` across the walked range and shows no sign of a turn. On words with no prefix
occurrence the third component is inert by construction, and this is asserted rather than argued —
the same word parses identically under every prefix power.

### Partial orders: refusing instead of choosing

The other non-flat direction is not a vector at all. Let some operator pairs be **incomparable**, so
a mixed expression is syntactically ambiguous and the grammar refuses it rather than picking a
reading. `PartialOrderParser` replaces the numeric minimum by the operator itself and asks the
relation; an incomparable verdict raises rather than resolving.

The space is every preorder on the four operators — ties and incomparabilities both:

```text
preorders                         355
of which total preorders           75      no incomparable pair
of which strict total orders       24      the Generation 1 registry
the antichain                       1      nothing ranked at all
```

All 25 registered grammars sit inside it as total preorders and reproduce
`parseatlas.parser.parse` on all `36` audit sources.

On 0020's six expressions, across all `355` preorders:

| incomparable pairs | preorders | cells | refusals | true refusals | over-refusals | silent choices |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 75 | 450 | 0 | 0 | 0 | 375 |
| 1 | 48 | 288 | 158 | 158 | 0 | 82 |
| 2 | 78 | 468 | 323 | 323 | 0 | 67 |
| 3 | 84 | 504 | 378 | 378 | 0 | 42 |
| 4 | 51 | 306 | 238 | 238 | 0 | 17 |
| 5 | 18 | 108 | 87 | 87 | 0 | 3 |
| 6 | 1 | 6 | 5 | 5 | 0 | 0 |

A source is *choice-bearing* when the `24` strict grammars do not agree on it: there the reading a
total order supplies is a convention rather than a deduction. A refusal on such a source withholds a
real arbitrariness; a refusal anywhere else withholds nothing and is counted as an over-refusal.

```text
cells                              2130
refusals                           1189     55.822 %
true refusals                      1189
over-refusals                         0
refusal precision                 1.000
silent choices                      586     27.512 %   accepted where the 24 disagree
```

The same accounting over every operator word for `k = 2..4`, which is `119280` cells:

| k | words | choice-bearing | cells | refusals | over-refusals | silent choices |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 12 | 5680 | 1512 | 0 | 2748 |
| 3 | 64 | 60 | 22720 | 9576 | 0 | 11724 |
| 4 | 256 | 252 | 90880 | 47448 | 0 | 42012 |

```text
cells                            119280
refusals                          58536     49.074 %
over-refusals                         0
silent choices                    56484     47.354 %
refusal precision                 1.000
```

**Zero over-refusals in `119280` cells and `2130` corpus cells.** A partial order never refuses a
source whose reading was not arbitrary in the first place, because a refusal is raised only where
two incomparable operators must be compared, and swapping their order is precisely what the strict
registry already does.

The price is brackets. For each of the `150` conventional readings — `25` grammars on `6` sources —
the fewest bracket pairs that still write that reading under the antichain, searched exhaustively
over every subset of internal nodes and accepted only when the writing re-parses to the very same
tree:

```text
conventional readings                150
still free of brackets                25
needing at least one bracket pair    125     83.333 %
unwritable at any bracket count        0
mean minimum bracket pairs           2.407
maximum minimum bracket pairs            4
sources the antichain refuses            5   of 6
```

So the trade is priced on both sides. A partial order buys freedom from an arbitrary reading with
perfect precision — it refuses nothing that was not arbitrary — and pays `2.407` bracket pairs on
average per conventional reading, with nothing becoming unwritable.

### The null model

The object is the project's semantic class, the canonical-form, domain and excluded-points triple,
not the AST. Counts on the four smaller corpora, `31` expressions:

| corpus | expressions | precedence classes | + associativity | pair | new | sources gaining |
| --- | --- | --- | --- | --- | --- | --- |
| 0017 corpus | 5 | 27 | 27 | 27 | 0 | 0 |
| 0020 corpus | 6 | 50 | 54 | 73 | 19 | 2 |
| 0024 restriction probe | 10 | 22 | 31 | 40 | 9 | 5 |
| chain probe | 10 | 14 | 26 | 30 | 4 | 2 |

```text
new classes over associativity        32
new classes over precedence           57
sources gaining a class                9   of 31
```

Stratified by operator support, which is where a rise that is only the space would show itself:

| support | expressions | precedence | + associativity | pair | new |
| --- | --- | --- | --- | --- | --- |
| plus | 1 | 1 | 1 | 1 | 0 |
| minus | 3 | 3 | 6 | 6 | 0 |
| over | 3 | 3 | 5 | 5 | 0 |
| times, plus | 1 | 2 | 2 | 2 | 0 |
| times, minus | 2 | 4 | 7 | 9 | 2 |
| times, over | 1 | 1 | 2 | 2 | 0 |
| plus, minus | 1 | 2 | 3 | 3 | 0 |
| minus, over | 8 | 16 | 27 | 38 | 11 |
| times, minus, over | 2 | 4 | 4 | 4 | 0 |
| plus, minus, over | 2 | 6 | 6 | 6 | 0 |
| all four | 7 | 71 | 75 | 94 | 19 |

Every single-operator stratum gains nothing, in all three of them. That is the sharpest structural
statement in this section and it is not an accident: a single repeated operator is exactly what
associativity already handles, and the pair adds nothing there because the pair *is* associativity
there. Everything the second dimension buys needs at least two operator types.

On the full `3125`-expression 0024 corpus the two established columns come out identical to 0030's
and the third is the opening of this report:

```text
                              precedence    + associativity          pair
AST forms                          22500              33750         77500
semantic classes                   14175              14175         31306
new classes                                               0         17131
sources gaining a class                                   0          1750
```

The class count rises by `120.854` percent where the previous widening moved it by nothing at all.

## Multicore observation and default path

Every heavy walk here is independent per item and CPU-bound, so every one of them distributes across
processes — but only above a threshold that was observed rather than assumed. The worker count comes
from the observed core count with one core of headroom
(`parseatlas.reachability.resolve_workers`) and never from a constant; `workers=1` forces the
sequential path and an explicit worker count bypasses the threshold in both directions.

Three repetitions per configuration on this 16-core Windows host, **each repetition in a fresh
interpreter** so both columns pay the cold sympy import chain, medians:

| workload | tasks | sequential | parallel | speedup |
| --- | --- | --- | --- | --- |
| `reach_2d`, k = 5 | 73 | 4.01 s | 6.95 s | 0.58 |
| `reach_2d`, k = 6 | 260 | 24.74 s | 8.73 s | 2.83 |
| `enumerate_2d`, bound 4 | 256 | 11.27 s | 4.91 s | 2.30 |
| `enumerate_2d`, bound 5 | 625 | 62.25 s | 20.35 s | 3.06 |
| `three_d`, k = 3 | 20 | 38.83 s | 57.06 s | 0.68 |
| `three_d`, k = 4 | 71 | 78.10 s | 35.94 s | 2.17 |
| `partial_orders` | 355 | 1.30 s | 2.26 s | 0.58 |
| `null_model` | 31 | 9.36 s | 9.57 s | 0.98 |

Reading that table honestly gives three defaults and not one, because a task count predicts well
only when the tasks cost about the same:

```text
reach_2d, enumerate_2d, null_model   parallel from 128 tasks   crossover between 73 and 256
three_d                              parallel from  32 tasks   crossover between 20 and  71
partial_orders                       sequential at any count   one task is about 4 ms
```

`partial_orders` is the clearest case against a single constant. It has `355` tasks, well past the
general threshold, and loses `1.30` s to `2.26` s when it takes them, because all `355` together are
barely a second of parsing while `15` spawned interpreters cost more than that just to start.
`three_d` is the case in the other direction: `71` tasks sit below the general threshold and still
win `2.17` times over, because one task there is `41506` parses. The general constant is `128`,
which is where `parseatlas.associativity.PARALLEL_MINIMUM_ITEMS` was independently put on the same
host.

Parallelism changes only speed and never what is produced. The sequential and parallel paths return
the same dictionary apart from the worker field, and that is asserted for `reach_2d`, `three_d`,
`enumerate_2d`, `partial_orders` and `null_model` independently of any timing.

The variance on this host is large and these numbers are an ordering, not a constant: the `reach_2d`
`k = 6` sequential repetitions were `29.76`, `24.74` and `24.57` s, and the `enumerate_2d` bound-`5`
sequential repetitions `134.07`, `52.83` and `62.25` s. A different host, or the same host under a
different load, moves the crossover.

## What the enumerations do not produce

Every restriction is named here, where the answer is read, together with what was checked past it.

| restriction | what lies past it | does it change the answer |
| --- | --- | --- |
| components bounded by `5` | bounds `6` and `7` were run: `1679616` and `5764801` assignments | no, the parser count stays `6902` |
| integer components only | order alone decides behaviour, so real components add no matrix | no |
| `left` at least `1` | a `left` of `0` makes an operator unconsumable at EVERY minimum, not only at top level, so such a grammar rejects every source containing it, ambiguous or not | not what the partial-order section prices — that reports `0` over-refusals. Excluding it costs nothing: allowing `right >= 0` and `prefix >= 0` adds no parser at any `m` |
| reach sweep stops at `k = 6` | `k = 7` and beyond, ceiling table below | direction is fixed by the ceiling, size is not |
| reach sweep uses flat words | sources with hand-written brackets | the audit and the coverage table include them |
| prefix operator only at the head | interior prefix probe, `8` sources | no, `18` trees become `19` and containment holds |
| partial orders fix associativity left | the same sweep with every side right | no, all refusal counts are identical |
| partial orders rank operator symbols | context-dependent or per-position ranks | outside the vector and the preorder model alike |
| null model uses five corpora | other corpus families | unknown, and the corpora that gain nothing are named |

The structural ceiling is arithmetic and needs no run. A source reaches at most one tree per distinct
parser, so coverage is bounded by the parser count over `C(k)`:

| k | C(k) | precedence | + associativity | pair | with a prefix |
| --- | --- | --- | --- | --- | --- |
| 6 | 132 | 0.1818 | 2.9091 | 52.2879 | 314.4394 |
| 7 | 429 | 0.0559 | 0.8951 | 16.0886 | 96.7506 |
| 8 | 1430 | 0.0168 | 0.2685 | 4.8266 | 29.0252 |
| 9 | 4862 | 0.0049 | 0.0790 | 1.4196 | 8.5368 |
| 10 | 16796 | 0.0014 | 0.0229 | 0.4109 | 2.4712 |
| 11 | 58786 | 0.0004 | 0.0065 | 0.1174 | 0.7061 |
| 12 | 208012 | 0.0001 | 0.0018 | 0.0332 | 0.1995 |

The associativity ceiling binds from `k = 7`, the pair's from `k = 10`, the prefix's from `k = 11`.
Each extra component buys about two more operators of expression length and then meets the same
Catalan wall, because the Catalan ratio two steps apart tends to `16` and the spaces are constant
multiples.

The place this card is most likely to hide something is the behavioural quotient, so it is stated
plainly. Two assignments are declared equal when they parse the `16` two-operator witness words
identically. That equality is not a heuristic: the witness family reads the comparison matrix cell
by cell, and the matrix decides every parse, so no longer word and no other corpus can split a class
the witness family merges. The equality is nevertheless checked and not only argued — grouping by
matrix and grouping by witness parse give the same partition at every bound and alphabet run.

## Interpretation

The first and largest result is that the null model **fails**, and it fails on the corpus that
recorded the previous widening's zero. Associativity multiplied the registry sixteenfold and bought
no mathematics on the 0024 corpus; the second binding-power component multiplies the class count by
`2.209` on the same corpus with the same key. The two widenings are not comparable in kind:

```text
associativity   changes what one operator does to itself
the pair        changes what one operator does to another, and asymmetrically
```

That distinction is what the support stratification shows. Single-operator sources gain nothing at
all, because there the pair only encodes associativity and associativity is already there. Every
gain lives in sources with at least two operator types, where a pair can rank times above plus on
the left and below it on the right — a statement no scalar precedence can make and no associativity
flag can repair.

The second result is the size of the flat slice. Generation 1's `25` grammars and 0030's `388` are
not merely small inside the pair space; the whole flat family, every ordering of levels with a side
per level, is `730` of `6902` parsers. The project has been working inside `10.577` percent of the
parsers that one extra integer per operator makes available, and the `6172` outside have no scalar
description at all.

The third result is negative and belongs beside the first. **A larger space is still a constant
against an exponential.** The pair recovers `29.655` percent of the precedence gap where
associativity recovered `11.617`, but the per-step recovery falls the same way it did before —
`100.000`, `70.968`, `55.746`, `41.811`, `28.658` — and the ceiling table says why. Each dimension
buys roughly two more operators of expression length. Three dimensions buy four. Nothing in this
family escapes the Catalan wall; it only postpones it.

The fourth result is the partial-order trade, and it is the cleanest of them. A partial order refuses
with **perfect precision** on everything walked here: `58536` refusals in the word sweep and `1189`
on the corpus, and not one of them landed on a source whose reading the registry agreed on. The
refusal is not conservative caution, it coincides exactly with real arbitrariness. What it costs is
`2.407` bracket pairs per conventional reading and nothing at all in expressiveness, since no
reading became unwritable. Against that stands the number on the other side: a total order accepts
`586` of `2130` cells and `56484` of `119280` silently, choosing a reading where the registry itself
does not agree.

```text
full parenthesization space
    -> prefix-power-reachable subset
    -> pair-reachable subset
    -> associativity-reachable subset
    -> precedence-reachable subset
```

## Limits

- The enumeration bound is `5` and is saturating rather than computational: bounds `6` and `7` were
  run and the parser count did not move from `6902`. What lies past `7` was not run, and the chain
  argument says nothing there can be new, but that argument is a claim about realisable matrices and
  not an executed observation.
- The behavioural quotient is a **declared** equality: two assignments are the same point when they
  parse the `16` two-operator witness words identically. The witness family provably reads the whole
  comparison matrix, so no other corpus should split a merged class, but a different corpus is the
  place such an equality would break and none was run against it beyond the sweeps reported here.
- The reach sweep stops at `k = 6`. The next length was not run, and the ceiling table fixes the
  direction of the curve past it but not its size.
- The reach sweep uses flat words. A source with hand-written brackets changes the leaf and operator
  sequence and is outside that enumeration, though the audit and the per-expression coverage table
  both contain such sources.
- The prefix sweep places the prefix operator only at the head of the word, where the tree count has
  the closed form `C(k+1)`. The interior probe covers `8` sources only.
- The partial-order space is a **declared subset** of all partial orders: it is every preorder on the
  four operator symbols with associativity fixed at left. Re-running the whole sweep with every side
  right leaves all refusal counts identical, so the fixed side does not move this answer, but ranks
  that depend on position or context are outside the model entirely.
- The semantic key carries a domain component and that component is **inert**: `canonicalize` writes
  the same literal for every expression (`NF-2026-00005`), so the operative discrimination is the
  canonical form together with the excluded points, and the triple is a pair in practice.
- The `3125`-expression run is a single observation of one templated corpus; the `250`-source figure
  quoted in the validation section is a deterministic prefix of it and not a sample of it, and its
  strata are visibly unrepresentative.
- Timings are from one contended host and are an ordering, not a reproducible constant.

## Evidence classification

- The audit, the reach tables, the coverage table, the partial-order tables and every class count are
  executable **observations** from the runs listed under validation.
- The saturating bound `5`, the identity of the behavioural quotient with the comparison matrix, and
  the containment of the associativity column inside the pair column are **symbolically justified**
  and observed as well.
- The structural ceiling, parser count over `C(k)`, is **symbolically justified** for any space of
  that size.
- That a partial order never over-refuses is an **observation** over `121410` cells and not a proof;
  the argument that a refusal implies a comparison the registry disagrees about is a sketch.
- That the pair's coverage tends to zero for every length remains a **hypothesis**; only `k` up to
  `6` was walked.

## Validation

```text
python -m pytest -q tests/test_binding_power.py
60 passed in 187.59s
```

```text
python -m pytest -q
1351 passed, 2 skipped in 1920.72s
```

The suite total is the figure at this run; other experiments add modules and tests in parallel, so
the total grows while this experiment's contribution stays fixed.

Exact commands behind the tables:

```text
python -c "from parseatlas.binding_power import agreement_audit; print(agreement_audit())"

python -c "from parseatlas.binding_power import reach_2d; print(reach_2d(6, workers=1))"

python -c "from parseatlas.binding_power import saturation_scan; print(saturation_scan())"

python -c "from parseatlas.binding_power import flat_slice; print(flat_slice())"

python -c "from parseatlas.binding_power import three_d; print(three_d(5, workers=15))"

python -c "from parseatlas.binding_power import partial_orders; print(partial_orders(workers=1))"

python -c "from parseatlas.binding_power import partial_order_sweep; print(partial_order_sweep(4))"

python -c "from parseatlas.binding_power import null_model; print(null_model(workers=1))"

python -c "from parseatlas.binding_power import null_model; from parseatlas.corpus_matrix import generate_corpus; print(null_model({'0024': tuple(i['source'] for i in generate_corpus()['expressions'])}, workers=15))"
```

The last command is the `3125`-expression run and takes `292.8` s on this host with `15` workers.
The same call on the first `250` sources of that corpus takes `27.2` s and reports `975` precedence
classes, `975` with associativity and `2100` with the pair.
