# ParseAtlas experiment 0048: the complex domain, and the branch cut as a second convention

## The answer to half A, first

The project semantic key is `(canonical form, domain, excluded points)`, and `src/parseatlas/canonical.py`
line 59 has written the literal `"domain": "R"` for every expression the repository has ever canonicalised.
The middle component has been inert for the whole history of the project, which means the project has been
silently answering *the declared domain does not change the partition* without ever asking. Asked:

> **The declared domain changes the partition on `1` of the `12` corpus sources, and on the other `11` the two
> partitions are equal. Where it changes at all it strictly REFINES: over `12` corpus sources and `42100` swept
> sources there is not one coarsening and not one crossing. And the excluded-points component differs in `57`
> of the `300` corpus cells while moving the partition in only `6` of them — `51` of the `57` differences are
> invisible to the partition.**

So the honest answer is neither "no" nor "yes". The two axes are **nearly** independent, the exception is
nameable, and the direction of the exception is one-way.

The mechanism is worth stating in one sentence, because it is what makes the number `51` large and the number
`6` small. A difference in the excluded set moves a grammar out of its class only if some *other* grammar shares
its canonical form and does not share its complex excluded set. Both halves of that coincidence are needed, and
on this corpus they meet once.

## Purpose

Three questions, and the card is explicit that they are not the same question.

- **Half A.** Does the declared analysis domain change how the 25 grammars partition? Experiment 0022 already
  proved that equivalence-class structure is a joint property of the token sequence *and* the declared domain,
  measured over `Q` against `F_p`. Nobody varied the domain again. This card varies it to `C`.
- **Half B.** Where a complex `sqrt` or `log` is taken, the branch must be chosen, and that choice is *adopted*,
  not derived. It is the same kind of object as operator precedence, so the founding question has a second
  instance — *what mathematics would we have if the cut had been placed somewhere else?* — and the two axes can
  be crossed.
- **Half C.** Over `C` every quadratic factors. The "roots on the page" advantage this project measured is
  bounded over `R` by reducibility; half C re-derives that result and separates what the wider domain buys
  for the equivalence from what it does not buy for the notation.

This card does **not** fix NF-2026-00005. `canonical.py` is untouched. The domain-aware key lives in
`src/parseatlas/complex_worlds.py` and is proved to agree with the existing key wherever the domain is `R`.

## The audit that binds the two columns

If the `R` column of this experiment did not reproduce the key the repository already computes, the `R` column
and the `C` column would be measuring different things and no comparison between them would mean anything. So
the agreement is counted rather than asserted:

```text
corpus sources                     12
grammars                           25
cells checked                     300
cells where the keys disagree       0
```

`to_symbolic` and `excluded_points` are written out in the new module rather than imported from `canonical.py`,
so the `R` branch is an independent re-derivation and the equality above is a check rather than a delegation.
Only `parse` is shared, because the parse tree is the datum both keys are keyed on.

## A second defect, found on the way

The `"R"` on the existing key is not a domain restriction. It is a symbol assumption, and the two come apart.
`excluded_points` calls SymPy's `solve` on a symbol declared `real=True` and trusts the result to be real. With
the installed SymPy that holds for `x**2 + 1`, which returns the empty list, and fails for `x**4 + 3*x**2 + 3`,
which returns four non-real roots:

```text
witness                     1 / (x*x*x*x + 3*x*x + 3)
points in the "R" key                              4
of those, non-real                                 4
points in the "C" key                              4
leaking cells on this corpus                0 of 300
```

The direction matters and it is the reason this is disclosed here rather than buried. A leak can only put
complex points into the `R` key, so it can only make the domain look **more** inert than it is. Half A's answer
is therefore a lower bound on the effect of the domain, never an inflated one. The witness is deliberately not
in the corpus: putting it there would change every half A number for a reason that has nothing to do with
half A.

## Corpus

Hand-chosen, and the choice is disclosed rather than defended as representative. It is built to populate every
T6 operator-support stratum from `1` to `4` and to contain both kinds of denominator — one with real poles and
one whose poles are complex only.

```text
2 + x + 1                        support 1: one operator, so precedence cannot act at all
x * x + 1                        support 2, no division: the excluded set is empty in both domains
x / x + 1                        support 2: some readings are CONSTANT, which half B needs
1 / (x*x + 1)                    the card's named case: no real pole, two complex ones
1 / (x*x + 1) * x                the same denominator with a second operator to move
x / (x*x + 1) + 1                the same denominator reached through a different top level
(x + 1)/(x - 2)                  a real pole: R and C see the same excluded set
(x*x - 1)/(x - 1)                a removable restriction: the value hides what the tree records
1 / x * x + 1                    division against multiplication, five classes over R
2*t + 1 - t/2                    the repository's standing linear source since 0001
2*x*x + 1 - x/2                  the repository's standing quadratic source since 0003
(x * x + 1) / 1 - (x * x + 2)    found by the sweep: the C partition strictly refines the R partition here
```

## Half A: the observed table

`R` and `C` are the class counts over the `25` grammars; `excluded` is the number of grammars whose excluded
tuple differs between the two domains.

| source | support | R | C | verdict | excluded |
|---|---|---|---|---|---|
| `2 + x + 1` | 1 | 1 | 1 | equal | 0 |
| `x * x + 1` | 2 | 2 | 2 | equal | 0 |
| `x / x + 1` | 2 | 2 | 2 | equal | 0 |
| `1 / (x*x + 1)` | 3 | 2 | 2 | equal | 13 |
| `1 / (x*x + 1) * x` | 3 | 4 | 4 | equal | 13 |
| `x / (x*x + 1) + 1` | 3 | 4 | 4 | equal | 21 |
| `(x + 1)/(x - 2)` | 3 | 1 | 1 | equal | 0 |
| `(x*x - 1)/(x - 1)` | 3 | 2 | 2 | equal | 0 |
| `1 / x * x + 1` | 3 | 5 | 5 | equal | 4 |
| `2*t + 1 - t/2` | 4 | 8 | 8 | equal | 0 |
| `2*x*x + 1 - x/2` | 4 | 8 | 8 | equal | 0 |
| `(x * x + 1) / 1 - (x * x + 2)` | 4 | 3 | 4 | **refinement** | 6 |

```text
verdict equal                                 11
verdict refinement                             1
verdict coarsening                             0
verdict neither                                0
sources whose excluded set differs anywhere    5
cells whose excluded set differs              57 of 300
of those, invisible to the partition          51
cells whose canonical form differs             0 of 300
```

The last line is a separate observation and it matters twice. Over this language — binary `+ - * /` with
rational literals — SymPy's `simplify` never produced a different canonical string under `real=True` than
under no assumption. So the whole of the domain effect observed here is carried by the **excluded-points**
component, not by the canonical form. It is also what makes the divisor-signature screen in the sweep sound
enough to be worth controlling.

### The null model, per stratum

By the operator-support reduction of experiment 0019, a source distinguishes only the orderings of the operators
it actually contains, so a support-`s` source has at most `s!` readings and therefore at most `s!` classes. A
support-1 source cannot move under any axis, and counting it in a rate hides that the denominator was never
free. Every rate below is computed inside one stratum.

| support | reading ceiling | sources | strict | rate | excluded cells |
|---|---|---|---|---|---|
| 1 | 1 | 1 | 0 | 0 / 1 | 0 |
| 2 | 2 | 2 | 0 | 0 / 2 | 0 |
| 3 | 6 | 6 | 0 | 0 / 6 | 51 |
| 4 | 24 | 3 | 1 | 1 / 3 | 6 |

Read against the null model, the stratum that carries the excluded-set difference is `3` and the stratum that
carries the partition change is `4`. They are not the same stratum, and that is the finding restated: the
excluded difference is common and mostly inert, the partition change is rare and needs more room to happen in.

## The one source that moves, and the mechanism

`(x * x + 1) / 1 - (x * x + 2)`, over `R`:

```text
('-1', 'R', ())                        G0 G09 G10 G12 G13 G14 G15 G16 G17 G18 G22 G23 G24   13
('-x*(x + 1)/(x*(x + 2) - 1)', 'R',
 ('-1 + sqrt(2)', '-sqrt(2) - 1'))     G01 G02 G03 G07 G08 G11                                6
('-x', 'R', ())                        G04 G05 G06 G19 G20 G21                                6
```

over `C`:

```text
('-1', 'C', ())                        G0 G14 G17 G18 G22 G23 G24                             7
('-1', 'C', ('-I', 'I'))               G09 G10 G12 G13 G15 G16                                6
('-x*(x + 1)/(x*(x + 2) - 1)', 'C',
 ('-1 + sqrt(2)', '-sqrt(2) - 1'))     G01 G02 G03 G07 G08 G11                                6
('-x', 'C', ())                        G04 G05 G06 G19 G20 G21                                6
```

Six grammars read the source with `x*x + 1` in a denominator. Over `R` that denominator has no root, so their
excluded set is empty and their key is identical to the seven grammars that never divide by it at all. Over `C`
the denominator has two roots, the excluded tuple becomes `('-I', 'I')`, and the class of `13` splits into `7`
and `6`. **The value never changes — both readings denote `-1` in both domains. The domain is visible in this
experiment only through what a reading is allowed to be undefined at.**

## The sweep: letting the space find the wall

`operator_count` is a computational limit, not a threshold, and the curve is published rather than a point. The
alphabet is five atoms — `x`, `1`, `2`, `(x * x + 1)`, `(x * x + 2)` — with all four operators, giving
`5^(n+1) * 4^n` sources.

A divisor-signature screen removes sources where all 25 grammars produce the same ordered list of divisor
subtrees; those have one constant excluded tuple in each domain, so their verdict is decided by the canonical
form alone. That is a **screen and not a theorem** — it is sound only if `simplify` groups the 25 readings the
same way under both assumption sets — so it is controlled rather than trusted: at `n = 1` and `n = 2` every
pruned source was recomputed the expensive way.

| n | space | pruned | live | equal | refinement | coarsening | neither |
|---|---|---|---|---|---|---|---|
| 1 | 100 | 90 | 10 | 100 | 0 | 0 | 0 |
| 2 | 2000 | 1395 | 605 | 1998 | 2 | 0 | 0 |
| 3 | 40000 | 21060 | 18940 | 39684 | 316 | 0 | 0 |

```text
prune control at n = 1     90 pruned sources recomputed, 0 wrong
prune control at n = 2   1395 pruned sources recomputed, 0 wrong
prune control at n = 3   not run: a computational limit, disclosed as one
```

The two witnesses at `n = 2` are named:

```text
(x * x + 1) / 1 - (x * x + 2)                  3 classes over R, 4 over C
(x * x + 1) / (x * x + 1) - (x * x + 2)        3 classes over R, 4 over C
```

At `n = 3` there are `316`, and the class count rises by `1` for `284` of them and by `2` for `32`. So the
refinement is not bounded to a single split: one source can have two R classes each cut in two.

### The sweep against the null model, and where the curve turns

| n | support | sources | live | strict | rate within stratum |
|---|---|---|---|---|---|
| 1 | 1 | 36 | 0 | 0 | 0 / 0 |
| 1 | 2 | 32 | 0 | 0 | 0 / 0 |
| 1 | 3 | 32 | 10 | 0 | 0 / 10 |
| 2 | 1 | 108 | 0 | 0 | 0 / 0 |
| 2 | 2 | 716 | 81 | 0 | 0 / 81 |
| 2 | 3 | 980 | 376 | 0 | 0 / 376 |
| 2 | 4 | 196 | 148 | 2 | 2 / 148 |
| 3 | 1 | 324 | 0 | 0 | 0 / 0 |
| 3 | 2 | 7268 | 972 | 0 | 0 / 972 |
| 3 | 3 | 22616 | 9790 | 12 | 12 / 9790 |
| 3 | 4 | 9792 | 8178 | 304 | 304 / 8178 |

Two things move with `n` and both would have been invisible at a single declared length. First, the support-4
rate rises from `2 / 148` to `304 / 8178`, that is from `1.35%` to `3.72%`. Second, and this is the more
interesting one, **support 3 is empty at `n = 1` and `n = 2` and is not empty at `n = 3`**: `12` sources of
`9790`. A card that had stopped at `n = 2` would have published "only support 4 can move", and that would have
been an artefact of the length rather than a property of the support. The twelve are all one shape:

```text
1 + (x * x + 1) / 1 + (x * x + 1)          2 + (x * x + 1) / 2 + (x * x + 1)
1 + (x * x + 1) / (x * x + 1) + 1          2 + (x * x + 1) / (x * x + 1) + 2
2 + (x * x + 2) / 2 + (x * x + 2)          2 + (x * x + 2) / (x * x + 2) + 2
(x * x + 1) + 1 / 1 + (x * x + 1)          (x * x + 1) + 2 / 2 + (x * x + 1)
(x * x + 1) + 1 / (x * x + 1) + 1          (x * x + 1) + 2 / (x * x + 1) + 2
(x * x + 2) + 2 / 2 + (x * x + 2)          (x * x + 2) + 2 / (x * x + 2) + 2
```

The strict count is monotone increasing over the range swept — `0`, `2`, `316` — and no coarsening and no
crossing appeared at any length.

## Half B: the branch cut as a second convention

### The conventions, declared

A convention is a ray from the origin; `arg` is taken in the half-open interval `(cut, cut + 2*pi]`, so the cut
ray itself belongs to the branch approached counter-clockwise. Four are declared, and the SymPy default is
**named as one of them** rather than used unnamed:

| name | cut | where the cut lies | arg interval | SymPy default |
|---|---|---|---|---|
| `principal` | `-pi` | the negative real axis, `arg = pi` | `(-pi, pi]` | yes |
| `negative_imaginary` | `-pi/2` | the negative imaginary axis, `arg = -pi/2` | `(-pi/2, 3*pi/2]` | no |
| `positive_axis` | `0` | the positive real axis, `arg = 0` | `(0, 2*pi]` | no |
| `positive_imaginary` | `pi/2` | the positive imaginary axis, `arg = pi/2` | `(pi/2, 5*pi/2]` | no |

`principal` reproduces SymPy's own `sqrt` and `log` on `9` probe values, `18` checks, `0` failures. An unnamed
default is an accident rather than a choice; this one is a choice and it is now on the record.

No branch decision anywhere in the module is taken by a float. The argument comparison runs on an exact
rational surrogate, the *diamond angle*, which maps `arg` in `(-pi, pi]` onto `(-2, 2]` sending `k*pi/4` to
`k/2`, exactly, for every Gaussian rational.

### Where each cut lies, observed rather than declared

A convention is not identified by its name but by the ray on which its branch is discontinuous. Each cut is
straddled by an exact rational pair at radius `4`, and **both** `sqrt` and `log` are checked, because a
convention that moved only one of them would not be a branch convention at all. The discontinuity test is a
sign test, not a magnitude comparison: for `sqrt`, the real part of `f(above) * conj(f(below))` is negative
exactly when the sheet flips; for `log`, the difference of two branch logarithms can only tend to `0` or to
plus or minus `2*pi*i`, so `pi` is their exact midpoint and is structural rather than tuned.

```text
ordered (cut, convention) pairs                16
checks (sqrt and log)                          32
jumps where the convention owns the cut         8 of 8
jumps where it does not                         0 of 24
violations                                      0
```

The straddle offset is itself swept — `1/10`, `1/100`, `1/1000`, `1/100000`, `128` checks in all — and the
classification does not move at any of them. It is therefore not a hidden threshold.

### Crossing the two axes: the headline

For each corpus source, the `25` grammars give some number of distinct inner readings over `C`; crossed with
`4` branch conventions, an independent pair of axes would give the product. The composite is recorded as the
pair `(value of the inner reading, sheet)` at every point of an exact Gaussian-rational lattice, which is
faithful — that pair determines the value under either outer function and is determined by it — and which never
mentions the inner canonical form, so what it induces is a statement about the composite rather than a
restatement of the key.

```text
product of the two axis sizes                 172
distinct composites observed                  160
difference                                     12
sources where the axes are independent          8 of 12
sources where they interact                     4 of 12
```

Stratified by operator support, because the pooled row above includes sources that cannot interact
at all:

```text
support   product   measured   independent
   1          4         4        1 of 1      (one reading; T6 forbids interaction)
   2         16        14        1 of 2
   3         72        70        5 of 6
   4         80        72        1 of 3
```

**The axes are not independent, and the entire interaction is carried by constant readings.** Per source:

| source | inner classes | product | observed | difference | constant classes |
|---|---|---|---|---|---|
| `2 + x + 1` | 1 | 4 | 4 | 0 | 0 |
| `x * x + 1` | 2 | 8 | 8 | 0 | 0 |
| `x / x + 1` | 2 | 8 | 6 | 2 | 1 |
| `1 / (x*x + 1)` | 2 | 8 | 8 | 0 | 0 |
| `1 / (x*x + 1) * x` | 4 | 16 | 16 | 0 | 0 |
| `x / (x*x + 1) + 1` | 4 | 16 | 16 | 0 | 0 |
| `(x + 1)/(x - 2)` | 1 | 4 | 4 | 0 | 0 |
| `(x*x - 1)/(x - 1)` | 2 | 8 | 8 | 0 | 0 |
| `1 / x * x + 1` | 5 | 20 | 18 | 2 | 1 |
| `2*t + 1 - t/2` | 8 | 32 | 30 | 2 | 1 |
| `2*x*x + 1 - x/2` | 8 | 32 | 32 | 0 | 0 |
| `(x * x + 1) / 1 - (x * x + 2)` | 4 | 16 | 10 | 6 | 2 |

The reason is that a constant reading takes exactly one point of the plane, so two conventions that put that
point on the same sheet give literally the same composite. That is derivable without any lattice at all, and it
is derived, so the lattice sweep has a target to converge to rather than only a plateau to sit on:

| class | value | distinct sheets under 4 conventions | forced collapse |
|---|---|---|---|
| `x / x + 1`, `G0` | `2` | 2 | 2 |
| `1 / x * x + 1`, `G0` | `2` | 2 | 2 |
| `2*t + 1 - t/2`, `G01` | `1` | 2 | 2 |
| `(x * x + 1) / 1 - (x * x + 2)`, `G0` | `-1` | 1 | 3 |
| `(x * x + 1) / 1 - (x * x + 2)`, `G09` | `-1` | 1 | 3 |

```text
constant classes                                5
deficit forced by them, no lattice involved    12
deficit observed on the declared lattice       12
non-constant classes that collapse              0
```

### The lattice is a computational limit in two directions, and the second one caught this card out

A finite lattice can merge two composites that differ only off the lattice; it can never split two that agree.
So the observed count can only rise as the lattice is refined, and the deficit can only fall — towards the `12`
that the constant classes force. The lattice has two parameters, and sweeping only the radius would have given
the wrong answer.

| radius | mesh | points | observed | difference | non-constant collapses |
|---|---|---|---|---|---|
| 1 | 1 | 9 | 145 | 27 | 14 |
| 2 | 1 | 25 | 153 | 19 | 7 |
| 3 | 1 | 49 | 154 | 18 | 6 |
| 4 | 1 | 81 | 154 | 18 | 6 |
| 6 | 1 | 169 | 154 | 18 | 6 |
| 2 | 1/2 | 81 | 158 | 14 | 2 |
| 3 | 1/2 | 169 | 159 | 13 | 1 |
| 6 | 1/2 | 625 | 159 | 13 | 1 |
| 2 | 1/3 | 169 | 159 | 13 | 1 |
| 4 | 1/3 | 625 | 160 | 12 | 0 |
| 3 | 1/4 | 625 | 160 | 12 | 0 |
| 4 | 1/5 | 1681 | 160 | 12 | 0 |

At integer mesh the curve flattens at `18` from radius `3` onwards and stays there to radius `6`, which reads
like a settled answer and is not one. Refining the mesh takes it to `12`, where it matches the derived value
and stays for every finer setting checked, up to `1681` lattice points. The last surviving artefact was one
class of `1 / x * x + 1` under `G10`, whose reading `1 + 1/x**2` reaches the third quadrant only at modulus
below `1` — at `x = -3/10 - 4/5 i` the value is `-171/5329 - 4800/5329 i` — which a half-integer lattice of any
radius contains only eight candidate points for and misses.

### Sweeping the number of conventions

Four conventions is exactly the kind of parameter that gets declared once and never questioned, so it is swept.
The sets are nested, taken from eight evenly spaced cuts at a fixed stride.

| conventions | product | observed | difference | forced by constants | observed / product |
|---|---|---|---|---|---|
| 1 | 43 | 43 | 0 | 0 | 1.0000 |
| 2 | 86 | 84 | 2 | 2 | 0.9767 |
| 4 | 172 | 160 | 12 | 12 | 0.9302 |
| 8 | 344 | 305 | 39 | 32 | 0.8866 |

The difference is monotone increasing and the ratio monotone decreasing over the range swept: **the more branch
conventions are admitted, the further the joint count falls behind the product.** The `8`-convention row is
reported with its own sensitivity in the same sentence: at the declared lattice its deficit is `39` against a
forced `32`, and the gap closes as the lattice is refined, because eight cuts carve the plane into sectors of
`pi/4` that a fixed lattice image is correspondingly less likely to reach.

| radius | mesh | points | observed | difference | non-constant collapses |
|---|---|---|---|---|---|
| 4 | 1/3 | 625 | 305 | 39 | 6 |
| 3 | 1/4 | 625 | 306 | 38 | 5 |
| 4 | 1/5 | 1681 | 311 | 33 | 1 |
| 3 | 1/7 | 1849 | 310 | 34 | 1 |
| 4 | 1/8 | 4225 | 312 | 32 | 0 |

At `4225` points the `8`-convention deficit reaches exactly the forced `32`, with no non-constant collapse left.
The sequence is not monotone as listed because the two lattice parameters do not order the settings totally: a
smaller radius with a finer mesh is neither above nor below a larger radius with a coarser one.

### Does any grammar pair that agrees under one convention disagree under another?

```text
grammar pairs examined                       3600
conventions each pair is compared under          4
pairs that agree under one and not another       0
```

**None, and this is forced rather than found.** Two grammars in the same class have the same value at every
point, hence the same sheet at every point, hence the same composite under every convention. The count is
published because the card asks for the cases by name and "none" is only worth reading beside the size of the
search; it confirms the implementation rather than discovering a fact. The branch axis can **collapse** distinct
readings and can never **split** them — **and that is wrong.** This experiment's own
`partition_equals_inner_everywhere` is `True` and `agreeing_pairs_audit` returns `0` splitting pairs of
`3600`: under every convention the composite partition EQUALS the inner partition, so two distinct readings
are never merged either. The composite is encoded as `(inner value, sheet)` and the value determines the
reading, so a merge is impossible by construction. **The real mechanism is two CONVENTIONS agreeing on one
constant reading**, which section 3 states correctly and derives without any lattice. The deficit is
one-signed because conventions can coincide, not because readings can collapse.

### The encoding is checked against the functions it stands for

Half B is counted through the `(value, sheet)` encoding, so an encoding that silently merged two composites
would understate the observed count everywhere. It is checked against actual SymPy `sqrt` and `log` values on
`1 / x * x + 1`, `100` cells at two lattice settings:

```text
lattice 9 points     encoded 15 distinct   sqrt 15   log 15   partitions agree
lattice 25 points    encoded 16 distinct   sqrt 16   log 16   partitions agree
```

## Half C: reducibility over C

The manager measured, for the owner's mathematician, that the "roots on the page" advantage exists exactly when
the quadratic factors over `Q`. Re-derived here:

| quadratic | roots | Q | R | C | factored writing in Generation 1 | expanded cheaper | factored cheaper | tie |
|---|---|---|---|---|---|---|---|---|
| `2 * x * x + 3 * x - 5` | `-5/2`, `1` | yes | yes | yes | `(2 * x + 5) * (x - 1)` | 9 | 8 | 8 |
| `x * x - 2` | `-sqrt(2)`, `sqrt(2)` | no | yes | yes | none | 13 | 8 | 4 |
| `x * x + 1` | `-I`, `I` | no | no | yes | none | 13 | 8 | 4 |

The `8` in the first row is the manager's number, reproduced. The `13` and `4` rows price the factored
**shape** with a named leaf standing in for the number the language cannot write; they measure the cost of the
shape and are not a writing of the object.

**What the wider domain buys, and what it does not.**

```text
quadratics that factor over Q                             1 of 3
quadratics that factor over R                             2 of 3
quadratics that factor over C                             3 of 3
quadratics with a factored writing in the language        1 of 3, over every domain
what C buys for the EQUIVALENCE                           2 more
what C buys for the NOTATION                              0
```

Over `C` all three factor, so the equivalence gains two. The notation gains nothing, and the reason is observed
rather than asserted, because asserting it would have been wrong. `i` **is** a legal token in Generation 1 — as
a *variable name*:

| attempt | parses | canonical form | intended | denotes it |
|---|---|---|---|---|
| `(x - i) * (x + i)` | yes | `-i**2 + x**2` | `x**2 + 1` | no |
| `(x - r) * (x + r)` | yes | `-r**2 + x**2` | `x**2 - 2` | no |
| `i * i` | yes | `i**2` | `-1` | no |

```text
attempts                3
that parse              3
that denote the object  0
```

So "Generation 1 cannot write `i`" is false as stated and true as meant. The tokeniser accepts the string, the
parser builds a tree, and what comes out carries a free symbol `i` rather than the imaginary unit. The
limitation is in the **denotation**, not in the character set, and that is exactly the line half C is about.

One more observation separates the two sides cleanly. The number of worlds in which the factored writing is
cheaper is `8` for all three quadratics, whichever field supplies the roots. The bracket count reads the shape;
it never asks where the roots live. Meanwhile the excluded set does the opposite — of the three reciprocals,
only `1 / (x * x + 1)` gains anything over `C`:

```text
1 / (2 * x * x + 3 * x - 5)     R  ('-5/2', '1')            C  ('-5/2', '1')
1 / (x * x - 2)                 R  ('-sqrt(2)', 'sqrt(2)')  C  ('-sqrt(2)', 'sqrt(2)')
1 / (x * x + 1)                 R  ()                       C  ('-I', 'I')
```

## Multicore, by measurement

Three workloads whose per-item cost differs by orders of magnitude, each decided on its own numbers rather than
on one rule. All three are CPU-bound pure Python driving SymPy or exact rational arithmetic, so processes rather
than threads. `16` cores observed; `15` used for the `40000`-source screen and `12` for the two
twelve-item tables, always leaving headroom for the interactive session.

| workload | items | sequential | parallel | speedup | parallel wins | paths agree |
|---|---|---|---|---|---|---|
| half A table | 12 | 6.27 s | 2.64 s | 2.37 | yes | yes |
| half B table | 12 | 22.23 s | 6.57 s | 3.38 | yes | yes |
| sweep screen | 2000 | 1.43 s | 1.89 s | 0.76 | no | yes |

The screen is the workload where a pool loses, so the item count at which it stops losing is swept rather than
declared:

| items | sequential | parallel | speedup | parallel wins |
|---|---|---|---|---|
| 500 | 0.25 s | 1.15 s | 0.22 | no |
| 1000 | 0.64 s | 1.87 s | 0.34 | no |
| 2000 | 1.13 s | 2.00 s | 0.56 | no |
| 4000 | 3.03 s | 2.34 s | 1.29 | yes |
| 8000 | 6.42 s | 2.89 s | 2.22 | yes |
| 16000 | 12.23 s | 4.10 s | 2.98 | yes |

The crossing is at `4000` items, so the declared floor for that workload is `4096`, the next power of two at or
above it. The half A and half B tables cross at `2`. So there are two floors in this module and both come from
the table above rather than from a rule of thumb: a half A item is a `simplify` and a `solve` on `25` grammars,
a screen item is `25` parses and no SymPy at all. Parallelism changes only how fast: agreement between the two
paths is asserted at every row here and again in the test suite.

## Interpretation

**1. The domain axis and the precedence axis are nearly, but not exactly, independent.** Eleven of twelve
sources and `39684` of `40000` swept sources at the longest length partition identically over `R` and over `C`.
That near-independence is the reason the inert `"domain": "R"` has cost the project so little so far, and the
exceptions are the reason it is still a defect. NF-2026-00005 is real, its blast radius on this corpus is `6`
cells of `300`, and this card measures that radius rather than fixing it.

**2. Where the domain acts, it refines and never coarsens.** Over everything swept there is no coarsening and
no crossing. That is a one-way structure and it is not obvious in advance: a wider domain adds excluded points
and can only split a class that agreed because a restriction was invisible. It cannot merge two classes,
because it never removes a point from an excluded set.

**3. The domain is visible only through the excluded set, on this language.** `0` of `300` cells had a
different canonical form between the two domains. With binary `+ - * /` and rational literals there is no
expression whose *value* depends on whether the symbol is real, so the entire observable effect of the domain
sits in the third component of the key. A language with `sqrt` or `log` in it would put the effect in the first
component as well, and that is the boundary of this result rather than a property of domains.

**4. The branch cut is a second convention of the same kind, and crossing it with precedence is not free.**
`172` if the axes were independent, `160` observed. The interaction is entirely one-directional — a branch
convention cannot merge two readings and cannot split one — the composite partition equals the inner
partition under every convention — and on this corpus it is
carried entirely by readings whose value is constant. That answer is worth more than the number because it is
derivable: a constant sees one point of the plane, and two cuts that agree at that point are the same
convention as far as that reading can tell.

**5. The founding question has a second instance and it behaves differently from the first.** Precedence
partitions *readings of a string*. A branch convention does not partition anything — it moves every reading at
once, and the only thing it can do to the partition is fail to move two readings differently. So the two
conventions are the same *kind* of object and not the same *shape* of object, and a card that had assumed
symmetry between them would have measured the wrong thing.

**6. Over C the equivalence gains and the notation gains nothing.** All three quadratics factor over `C`; one
of three has a factored writing in Generation 1, over every domain. The advantage the project found for
reducible quadratics is bounded over `R` by reducibility, and that bound does **not** lift over `C` — it lifts
for the equivalence and stays exactly where it was for the notation. Experiment 0039 measured that `7` of its
`46` invisible pairs need the imaginary unit and `1` needs a radical; this card says why those `8` stay
invisible, and it is not the domain that blocks them.

## Limits

- **The complex domain is reachable for the EQUIVALENCE and not for the NOTATION, and this report does not blur
  them.** Generation 1 is binary `+ - * /`, integer and rational literals, named variables and brackets. There
  is no radical and no exponentiation. A key may carry `-I` as an excluded point; no source string in this
  language denotes the imaginary unit. `i` parses as a variable, which is observed above and is the precise
  form of the limitation.
- **Each branch convention is declared and a different cut would move the numbers.** Four cuts are declared and
  the SymPy default is named as one of them; eight are used in the convention sweep. The deficit `12` is a
  statement about *these* conventions and this corpus, and the sweep shows it rising with the number of cuts
  admitted.
- **The corpus is hand-chosen.** Twelve sources, selected to populate the support strata and to contain both
  kinds of denominator. It is not a sample of anything, and every rate in this report is computed inside a
  stratum for that reason.
- **The lattice is a computational limit in two parameters.** Radius and mesh, both swept, converging to a
  value derived without a lattice. A finer lattice can only raise the observed count, never lower it, so `160`
  is a lower bound on the number of distinct composites and `12` an upper bound on the deficit. The largest
  lattice checked was `4225` points.
- **The sweep length is a computational limit.** `n = 1`, `2` and `3` were run, `42100` sources in all; the
  prune control that makes the screen reportable was run at `n = 1` and `n = 2` and not at `n = 3`. Nothing was
  checked at `n` of `4` or more, and the support-3 result shows what a shorter stopping point would have hidden.
- **NF-2026-00005 is disclosed and not fixed.** `canonical.py` still writes `"domain": "R"` unconditionally.
  This card builds the domain-aware key alongside it, proves the two agree over `R` in all `300` cells, and
  measures what the inert component costs. It does not change the production key.
- **A second defect is disclosed and not fixed.** `excluded_points` under `"R"` inherits whatever `solve`
  returns for a `real=True` symbol, and that is not always real. It does not fire on this corpus and it fires
  on a named witness.
- **The screen behind the sweep is a screen.** Its soundness rests on `simplify` grouping the `25` readings the
  same way under both assumption sets, which is a property of SymPy rather than of this experiment. It is
  controlled exhaustively at `n = 1` and `n = 2`, `1485` sources recomputed with `0` disagreements, and not at
  `n = 3`.

## Evidence classification

- The `300`-cell agreement between the new key and the existing key: **observation**, `0` disagreements, and it
  is load-bearing rather than decorative — every other number here is void without it.
- The half A table, `11` equal and `1` refinement: **observation** on a hand-chosen corpus of `12`.
- No coarsening and no crossing anywhere: **observation** over `42112` sources, plus a **structural argument** —
  a wider domain can only add excluded points, so it can split a class and cannot merge two.
- The `57` against `51` split between excluded-set differences and partition movement: **observation**.
- `0` of `300` cells with a differing canonical form: **observation**, and a property of this operator set
  rather than of domains in general.
- The sweep table and its strata, including support `3` first moving at `n = 3`: **observation**, with the prune
  screen **controlled** exhaustively at `n = 1` and `n = 2` and unchecked at `n = 3`.
- Each convention's cut located by straddling it, `32` checks at the declared offset and `128` across the
  offset sweep, `0` violations: **observation**.
- `principal` reproducing SymPy's `sqrt` and `log` on `18` checks: **observation**, and the reason the default
  is a named convention here rather than an accident.
- `172` against `160`: **observation** at the declared lattice, with the lattice sweep and the `4225`-point
  setting published beside it.
- The deficit `12` being exactly the collapse the `5` constant classes force: **structural argument** plus
  **observation** — the value is derived without a lattice, and the lattice sweep converges to it from above.
- `0` grammar pairs splitting between conventions: **structural argument**, and the `3600`-pair count that
  accompanies it is a confirmation of the implementation rather than a search that could have failed.
- The `(value, sheet)` encoding counting the same composites as SymPy's own `sqrt` and `log`: **observation**,
  `100` cells at two lattice settings.
- Half C's `8` worlds in which the factored SHAPE is cheaper: **observation**, reproducing the manager's
  earlier figure.
- `3` attempts parsing and `0` denoting: **observation**, and the correction of a claim this card would
  otherwise have asserted.
- That a language with `sqrt` or `log` in it would put the domain effect into the canonical form as well as the
  excluded set: **hypothesis**, not observed here.

## Validation

```text
python -m pytest -q tests/test_complex_worlds.py
```

```text
python -c "from parseatlas.complex_worlds import complex_worlds_report; print(complex_worlds_report()['headline'])"
```

```text
python -c "from parseatlas.complex_worlds import grid_sweep; print(grid_sweep()['rows'][-1])"
```

```text
python -c "from parseatlas.complex_worlds import screen_crossover; print(screen_crossover()['crossover'])"
```

```text
environment    Windows 11, Python 3.14, sympy 1.14, 16 cores
module         src/parseatlas/complex_worlds.py
tests          tests/test_complex_worlds.py
```
