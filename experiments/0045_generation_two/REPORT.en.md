# ParseAtlas experiment 0045: does the flagship result survive exponentiation?

## Purpose

**It does not.** Once the language can write a power, `a * x^2 + b * x + c` denotes `6` distinct
objects across the `121` Generation 2 grammars rather than `2`, the conventional quadratic holds in
`21` of them rather than in `13` of `25`, and the object this repository is best known for — the
radical-free cubic `a*x*(b + x)*(c + x)` with roots `0`, `-b`, `-c` — **is denoted by no world that
writes the square as `x^2`**.

That scope is the whole of it, and an earlier revision of this sentence dropped it, claiming the
cubic was denoted by no Generation 2 world at all. **That was false and review caught it.** The
Generation 1 string `a * x * x + b * x + c` is still a legal Generation 2 string, and `60` of the
`121` worlds read it as exactly that cubic, radical-free, with those roots. What vanishes is not
the object but the object's *reachability from the written form a world with `^` would choose*.

The `13`/`12` split of experiment 0035 is exact, reproducible, and re-derived here. What this
experiment adds is its scope: it is a statement about the string `a * x * x + b * x + c`, and that
string is an artifact of a language with no exponentiation. The same string in the Generation 2
registry splits `61`/`60` — the same two objects, the same two blocks, only a larger registry — so
even the numbers `13` and `12` are registry sizes rather than facts about mathematics. Change the
string to the one a world with `^` would actually write, and the second object is gone.

Nine published claims over five objects were carried through the same treatment. In all nine rows
exactly one object survives the rewriting, and it is always the same one: **the object the
conventional world reads**.

**That is a statement about those nine rows and not about the two experiments.** Review checked the
claims the table omits and found three that behave differently: the truncated sine series shares
`7` objects between the generations, six of them non-conventional alternatives that survive; the
cosine series shares `5`, with four alternatives surviving; the exponential series shares `2`, with
one surviving. An earlier revision generalised the nine rows into "every alternative object of 0035
and 0036 is replaced", which those three falsify.

## The language

Generation 2 is Generation 1 plus exactly one binary operator, `^`. Thesis T26 — juxtaposition and
unary minus — is explicitly out of scope, so `2x` and `-x` remain unwritable.

Five operators give `5! = 120` strict precedence orderings. The registry adds the conventional
tied-level control `H0` — `^` tightest, then `*` `/` tied, then `+` `-` tied — for **`121`**
grammars, exactly as Generation 1 is `4! = 24` strict orderings plus one control for `25`. Strict
grammars are named `H001` to `H120` so that no identifier can be confused with a Generation 1 `G`
identifier.

`^` **is right-associative**, and that is not a detail: `2^3^2` is `2^9 = 512`, not `(2^3)^2 = 64`.
Every other operator in this project is left-associative, so Generation 2 is the first grammar
family here whose associativity is not uniform. The asymmetry is one term in the parser — the right
operand is parsed at `power(op) + 1` for a left-associative operator and at `power(op)` for a
right-associative one — and the whole bracket rule follows from it, with the two halves not
symmetric: a left child's threshold depends on the **child's** associativity and a right child's on
the **parent's**. That is why `a^b^c` needs no bracket in any of the `121` grammars and `(a^b)^c`
needs one in all of them.

**What may appear in an exponent.** Nothing is restricted: `^` is an ordinary binary operator of the
same language, so an exponent is whatever expression the grammar puts there, and readings such as
`(a*x)**(b*x + c + 2)` arise for that reason. There is no separate exponent syntax, no unary minus,
no implicit multiplication and no function application, and an unspaced `1/2` is one rational
literal rather than a division — all four are Generation 1 limits, inherited unchanged.

## Conservative extension, first

The shared parser is untouched. Generation 2 has its own tokenizer and parser in
`src/parseatlas/generation_two.py`, which raises the obligation this experiment discharges before
anything else: restricted to `+ - * /`, does Generation 2 parse exactly what Generation 1 parses?

```text
sources                     94    0034's cost corpus + 0035's catalogue + 10 hand-written strings
Generation 1 grammars       25
embeddings of ^            123    24 strict x 5 positions + the tied control x 3 positions
cells                    11562
disagreements                0
```

Every cell compares trees, not strings: the Generation 2 parser builds Generation 1's own
`Binary`/`Number`/`Variable` nodes, so a cell is dataclass equality. `^` is embedded at **every**
position of every grammar rather than only at the top, because "`^` happens to bind tightest" would
be a much weaker statement than the one the rest of this report needs.

The two guarantees Generation 1 requires are audited the same way over the whole `38 x 121` grid:

```text
round trip     4598 checks     0 failures      parse2(render2(t, g), g) == t
minimality     5665 brackets   0 violations    every pair deleted in turn and reparsed
```

Minimality is an exhaustive search over the writings and not an argument about the renderer: each
bracket pair is deleted and the result must reparse to a different tree or fail to parse.

## Corpus

`38` named formulas that actually use a power, in `6` areas — algebra `13`, geometry `6`, physics
`6`, calculus `5`, statistics `5`, finance `3`. Each is recorded in its Generation 2 writing and,
where the object can be written without `^` at all, in its Generation 1 writing too: `26` entries
have both, and `12` are Generation 2 only because they need a symbolic exponent (`x^n`) or a
non-variable base (`2^k`). Every source is the minimal writing under its own control grammar, which
is what makes the published list an audit trail rather than a decoration.

## Observed results

### 1. The headline: the quadratic in `121` worlds

Three readings of the same mathematics, because two different effects are in play and either alone
would misstate the result.

| written form | registry | support | T6 blocks | distinct objects | group sizes |
|---|---|---|---|---|---|
| `a * x * x + b * x + c` | `25` Generation 1 worlds | `* +` | `2` | `2` | `13`, `12` |
| `a * x * x + b * x + c` | `121` Generation 2 worlds | `* +` | `2` | `2` | `61`, `60` |
| `a * x^2 + b * x + c` | `121` Generation 2 worlds | `* + ^` | `6` | `6` | `21`, `20`, `20`, `20`, `20`, `20` |

The middle row is the whole of the registry effect: the same string, the same two objects, the same
two blocks, and only the block sizes change. **`13` and `12` are the sizes of the two T6 blocks of
the support `{*, +}` in a `25`-grammar registry**, and nothing more.

The bottom row is the language effect, and it is what the answer rests on.

| object | worlds | precedence, restricted to the support | denotes | degree | roots over `C` | radical |
|---|---|---|---|---|---|---|
| `O01` | `21` | `^ > * > +` | `a*x**2 + b*x + c` | `2` | `(-b +- sqrt(-4*a*c + b**2))/(2*a)` | yes |
| `O02` | `20` | `+ > * > ^` | `(a*x)**((b + 2)*(c + x))` | — | not attempted | — |
| `O03` | `20` | `* > + > ^` | `(a*x)**(b*x + c + 2)` | — | not attempted | — |
| `O04` | `20` | `^ > + > *` | `a*(b + x**2)*(c + x)` | `3` | `-c`, `-sqrt(-b)`, `sqrt(-b)` | yes |
| `O05` | `20` | `* > ^ > +` | `a**2*x**2 + b*x + c` | `2` | `(-b +- sqrt(-4*a**2*c + b**2))/(2*a**2)` | yes |
| `O06` | `20` | `+ > ^ > *` | `a*x**(b + 2)*(c + x)` | — | not attempted | — |

The control `H0` sits in `O01`, whose `21` worlds are the `20` strict orderings with `^ > * > +`
plus the control itself.

Three of the six readings are polynomials in `x` and **all three need a radical**. The other three
are neither polynomials nor rational functions in `x` — a variable in the exponent — and their root
lists are reported as *not attempted* with that reason rather than as an empty list, because an
empty list would read as "no roots" and that is a different claim. Those three cover `60` of the
`121` worlds.

So the two halves of 0035's headline fail in different ways. The **count** changes, `2` to `6`. The
**object** disappears: `a*x*(b + x)*(c + x)` is not among the six canonical forms. And the
**consequence people quote** — that in about half the worlds no radical is needed to solve the
standard quadratic — goes from `12` worlds of `25` to `0` worlds of `121`.

### 2. The survival table

The other objects 0035 and 0036 made claims about, written the way Generation 2 would write them.
Each published claim is quoted, re-observed in both generations, and given a verdict by a stated
rule: a claim false in Generation 2 **does not survive**; one true with different world counts
**survives with different numbers**; one true with the same counts **survives**.

| claim | object | Generation 1 -> Generation 2 objects | the claim's own number | verdict |
|---|---|---|---|---|
| `0035_quadratic_object_count` | quadratic | `2` -> `6` | `2` -> `6` objects | does not survive |
| `0035_quadratic_radical_free_cubic` | quadratic | `2` -> `6` | `12` -> `0` worlds | does not survive |
| `0035_quadratic_radical_free_worlds` | quadratic | `2` -> `6` | `12` -> `0` worlds | does not survive |
| `0035_binomial_square_object_count` | binomial square | `2` -> `5` | `2` -> `5` objects | does not survive |
| `0035_binomial_square_present` | binomial square | `2` -> `5` | `13` -> `41` worlds | survives with different numbers |
| `0035_difference_of_squares_object_count` | difference of squares | `2` -> `2` | `2` -> `2` objects | survives |
| `0035_circle_object_count` | circle | `4` -> `4` | `4` -> `4` objects | survives |
| `0035_circle_present` | circle | `4` -> `4` | `9` -> `41` worlds | survives with different numbers |
| `0036_pythagorean_identity` | Pythagorean identity | `2` -> `2` | `13` -> `61` worlds | survives with different numbers |

**The claims that do not survive, by name:** `0035_quadratic_object_count`,
`0035_quadratic_radical_free_cubic`, `0035_quadratic_radical_free_worlds`,
`0035_binomial_square_object_count`.

What the object counts hide is in the readings themselves.

| object | Generation 1 writing and objects | Generation 2 writing and objects |
|---|---|---|
| difference of squares | `a * a - b * b`: `a**2 - b**2` (`13`), `a*b*(a - b)` (`12`) | `a^2 - b^2`: `a**2 - b**2` (`61`), `a**((b - 2)**2)` (`60`) |
| Pythagorean identity | `s * s + c * c`: `c**2 + s**2` (`13`), `c*s*(c + s)` (`12`) | `s^2 + c^2`: `c**2 + s**2` (`61`), `s**((c + 2)**2)` (`60`) |
| circle | `x * x + y * y - r * r`: `4` objects, `9`/`8`/`4`/`4` | `x^2 + y^2 - r^2`: `4` objects, `41`/`40`/`20`/`20` |
| binomial square | `a * a + 2 * a * b + b * b`: `2` objects, `13`/`12` | `a^2 + 2 * a * b + b^2`: `5` objects, `41`/`20`/`20`/`20`/`20` |

The circle is the sharpest case in the table. Its **shape** survives entirely: four objects in both
generations, in blocks of the same structure, with the conventional reading holding the largest
group. Its **objects** do not: where Generation 1 offered a quartic and two mixed curves, Generation
2 offers power towers such as `x**((y + 2)**((r - 2)**2))`. A count that survives is not the same
thing as a claim that survives, so object-set equality is checked separately and never inferred from
the count. **In all `9` rows the two generations share exactly one object, and in all `9` it is the
one the conventional world reads.**

The binomial square is the one object that gains fewer objects than blocks: `6` blocks produce `5`
objects, because `^ > * > +` and `* > ^ > +` write `a^2 + 2 * a * b + b^2` identically — the `*`
chain and the two powers never meet.

### 3. Cost, and where the conventional convention ranks

The `38`-formula corpus priced under all `121` grammars, one bracket pair being one unit:

```text
cheapest    H001  ^ * / + -     24 brackets
CONTROL     H0    ^ *=/ +=-     25 brackets     rank 2 of 121, top 1.65 percent
dearest     H120  - + / * ^     70 brackets
spread                          46 brackets
```

Exactly one grammar is cheaper than the conventional one, none ties it, and its advantage is a
single bracket on a single formula:

```text
H0     (x - m)^2 / (2 * s^2)      2 brackets
H001   (x - m)^2 / 2 * s^2        1 bracket
```

`H001` is not a regrouping of the convention — it is the convention with its ties broken, `*` above
`/` and `+` above `-`. The one bracket it saves is bought by the `*` `/` tie alone. This is exactly
the shape of the Generation 1 finding recorded in the roadmap, where the two grammars beating `G0`
over four fields was `G18`, our own grouping with the `+`/`-` tie broken.

Because `2` of `121` and `3` of `25` are not comparable as ordinals, every rank is reported as a
percentile too, `100 * rank / registry size`, and the same mathematics is priced in both languages.
Of the `38` entries, `26` can be written without `^`; those `26` objects were priced in both
registries:

| ranking | corpus | registry | control total | control rank | percentile |
|---|---|---|---|---|---|
| Generation 2, whole corpus | `38` | `121` | `25` | `2` | `1.65` |
| Generation 2, movable entries only | `34` | `121` | `23` | `2` | `1.65` |
| Generation 2, the shared objects | `26` | `121` | `14` | `2` | `1.65` |
| Generation 1, the same shared objects | `26` | `25` | `26` | `6` | `24.0` |

Two readings of that table, and only one of them is safe. The safe one: writing those `26` objects
costs the conventional convention `26` brackets in Generation 1 and `14` in Generation 2, `12`
fewer, a saving of `46.15` percent, because a bracketed factor that has to be repeated —
`(x2 - x1) * (x2 - x1)` — is written once when a power exists. The unsafe one would be to read the
two ranks against each other as evidence that the convention improved; the registries differ in
size, the writings differ, and the percentile is given precisely so that no ordinal comparison has
to be made. 0037's `3` of `25` on its own `33`-law corpus is a third population again, and is quoted
here only as context.

**T25's own question, asked directly.** The thesis asks whether the conventional grammar keeps its
standing when `^` binds tighter than `*` versus looser. Each of the `5` positions `^` can occupy
holds exactly `24` of the `120` strict orderings, so the five means are directly comparable:

```text
^ at position 1 (tightest)   mean 34.0 brackets    min 24   max 44
^ at position 2              mean 40.5             min 26   max 48
^ at position 3              mean 47.0             min 33   max 61
^ at position 4              mean 53.5             min 46   max 68
^ at position 5 (loosest)    mean 60.0             min 50   max 70
```

The mean rises by exactly `6.5` brackets per position, four times over, and the same table on the
`26` shared objects rises by exactly `6.25` four times. The tightest-to-loosest gap is `26`
brackets. So on this corpus the position of `^` behaves as an additive term in the cost, and binding
it tightest — what mathematics actually does — is the cheapest of the five choices.

### 4. The null model, which bites harder with five operators

T6 says a parse depends only on the precedence restricted to the operators actually present. With
five operators the discount is large: an entry whose support has `k` operators partitions the `120`
strict orderings into `k!` blocks of `120 / k!` and is blind inside a block by construction.

```text
support size   entries   blocks it can separate   strict grammars per block
1                    3                        1                        120
2                   10                        2                         60
3                   17                        6                         20
4                    5                       24                          5
5                    3                      120                          1
```

**Only `3` of the `38` entries can distinguish all `120` orderings at all** — `taylor_second_order`,
`projectile_height` and `annuity_future_value`, the three that use every operator. The other `35`
cannot, whatever they are compared against. And full support is necessary rather than sufficient:
the best of the three writes only `36` distinct strings across the `120`, the others `28` and `16`.
No entry in this corpus separates more than `36` grammars.

Four entries — `power_of_power_rule`, `iterated_power`, `binary_place_value`, `exponential_growth` —
have the same cost under all `121` grammars. They add a constant to every total and can move no
ranking, so the ranking is recomputed without them; the control holds rank `2` and the order of the
`121` is unchanged, which is the second row of the ranking table above.

The corpus as a whole is a different matter from any entry in it. The `38` cost vectors give `121`
distinct profiles and the `38` rendering vectors give `121` distinct profiles, so the corpus does
separate every grammar in the registry — while collapsing to only `40` distinct totals, which is why
ranks tie so heavily near the top.

### 5. The most fractured object

The Generation 2 truncated sine series `x - x^3 / 6 + x^5 / 120` denotes `17` distinct objects across
the `121` worlds, against `16` distinct canonical texts. The difference is the semantic key doing
its work: two groups both read `0`, one excluding `-6` and the other excluding four of the fifth roots
of `-6`, and a comparison on canonical text alone would merge them. Experiment 0035 found `14`
objects for the Generation 1 series, so a power does not make the series less convention-sensitive.

**Why four and not five.** `x^5 + 6` has five fifth roots, and the excluded-points half of the semantic key reports four of them, because the project solves on a symbol declared `real=True`. This is the same short-root-list defect that section 2 of experiment 0035 exists to correct, reappearing inside the excluded-points component rather than the roots component. The `17`-against-`16` separation this paragraph rests on is unaffected and was re-derived in review; only the count was wrong.

## Multicore

Repository policy is multicore by default and allows a sequential path when the timings justify it.
Both workloads here were timed on this host — `16` cores, Windows, spawn start method, `15` workers
with one core of headroom — and both lose to the sequential path:

```text
workload        cells   sequential   parallel   speedup   records identical
cost grid          38     0.101 s     1.249 s    0.081    yes
semantic grid     121     0.766 s     1.821 s    0.421    yes
```

The reason is a fixed cost, not a property of the work: raising the pool takes `1.2` seconds,
because every spawned worker imports SymPy before it does anything. Per cell the two workloads cost
`0.003` and `0.008` seconds, so the routing rule — the sequential estimate against pool startup plus
the divided work — sends both to the sequential path. The crossover is computed rather than assumed:
at `205` semantic cells the same code switches to the pool. Parallelism changes only how fast; the
two paths return equal structures and the test suite pins that rather than assuming it.

## Interpretation

The founding question asks what mathematics we would have under a different convention. 0035's
answer for the quadratic was vivid: in about half the worlds there is no quadratic formula, because
the standard written form is already a factored cubic. That answer is correct about the string it
was asked of. It is not robust to the language gaining an operator that mathematics has had for four
centuries.

What replaces it is less quotable and more defensible. Under `^` the standard quadratic still
fractures — into `6` objects rather than `2` — but the fracture no longer produces a *nicer* object.
Every reading whose roots can be stated needs a radical, and half the readings are not polynomials
at all: they are power towers with the variable in the exponent, objects no textbook of any world
would open with. Generation 1's split had a winner; Generation 2's has none.

There is a second, quieter reading of the same numbers, and it is the one that generalises. The
sizes `13` and `12` were never about mathematics. They are the two blocks of a two-operator support
counted against a `25`-grammar registry, and the same string against a `121`-grammar registry reads
`61` and `60`. **Any world count in this project is a registry size until it is stated with its
block structure**, and that is a discipline this experiment recommends applying to every earlier
number of the form "in `N` of the `25` worlds".

Finally, the conventional convention comes out of Generation 2 looking better rather than worse. It
is second of `121` on cost, beaten by one bracket by a grammar that is itself the convention with
its ties broken, and it puts `^` in the position the whole registry says is cheapest. That is not an
argument that the convention is optimal; it is an observation that the one operator most likely to
have upset the Generation 1 rankings did not.

## Limits

- **`^` is the only operator added.** T26 — juxtaposition, `2x`, and unary minus, `-x^2` — is
  explicitly out of scope and unwritable here. Those interactions are the ones real notation
  actually has, and a Generation 3 that adds them could move any number in this report.
- **What may appear in an exponent is not restricted, and that is a modelling choice.** `^` is an
  ordinary binary operator over the same language, so an exponent is whatever the grammar puts
  there, and readings such as `(a*x)**(b*x + c + 2)` are a consequence. A language admitting only
  literal or atomic exponents would fracture far less, and would be a different experiment.
- **The corpus is hand-chosen.** `38` formulas reflect a judgement about what mathematics with
  powers looks like, and `12` of them cannot be written in Generation 1 at all, which is itself a
  choice about what to compare. A different corpus would move every cost number and could move the
  control's rank.
- **A rank across `121` is not comparable to a rank across `25` as an ordinal**, which is why every
  rank here carries its percentile and why the two generations are compared on the same `26` objects
  rather than across corpora. 0037's `3` of `25` is a third corpus again.
- **Roots are over `C`, and are not attempted for every reading.** The convention is 0035's, reused
  unchanged, and `I` counts as a radical because it is one. A reading that is neither a polynomial
  nor a rational function in the variable gets no root list and is reported as such; `60` of the
  `121` quadratic worlds are in that state, so "no world is radical-free" means "no world whose
  roots this module states is radical-free".
- **Excluded points come from `/` nodes only.** The rule is Generation 1's, unchanged. A negative
  exponent written as `x^(0 - 2)` would exclude a point and is not detected; no corpus entry here
  writes one.
- **`domain` is inert in the semantic key** (`NF-2026-00005`). The triple `(canonical, domain,
  excluded points)` is the project's and is used here unchanged, but it is always the literal `"R"`,
  so the effective discrimination has two components. No count in this experiment changes because of
  it — the `17` sine-series objects against `16` canonical texts are separated by excluded points —
  but the guarantee should be stated as it is.
- **The timings are from one host** (`16` cores, Windows, spawn start method). On another host the
  numbers differ and the routing decision has to be re-timed rather than copied.

## Classification of evidence

- **Observations** (executable, reproducible in this repository): the conservative-extension audit
  over `11562` cells; the round trip over `4598` cells and minimality over `5665` brackets; the `6`
  objects of `a * x^2 + b * x + c` with group sizes `21`/`20`/`20`/`20`/`20`/`20`; the `2` objects
  and `61`/`60` split of the Generation 1 string in the Generation 2 registry; the absence of
  `a*x*(b + x)*(c + x)` from the `121` readings of `a * x^2 + b * x + c`, which is NOT its absence
  from the language — `60` of the `121` worlds still read it from the Generation 1 string; every row
  of the survival table, whose scope is those nine rows and not the two experiments; the control's rank
  `2` of `121` and `6` of `25`; the `6.5`-bracket step per position of `^`; the null-model split of
  `3` against `35`; the `17` objects of the Generation 2 sine series; and the timings.
- **Interpretation** (derived from the observations rather than observed): that the mathematicians
  of those worlds would have built these objects, and that a world of power towers would not have
  opened its textbooks with them. That is a notational-cost argument.
- **Not claimed**: that the conventional order is better or worse; that any universal law over the
  `121` worlds exists; that the corpus is a representative sample of mathematics with powers; that
  the Generation 1 result was wrong — it is exact, and this experiment states its scope.

## Validation

```text
994 passed
```

`tests/test_generation_two.py`: `51 passed`, in this order — the conservative-extension audit first
with its `11562` cells pinned; right-associativity on `2^3^2` evaluating to `512` and as a tree
comparison; the round trip and minimality over the whole `38 x 121` grid; the headline quadratic
pinned literally, with group sizes, block labels, roots and the control's group; every published
claim of 0035 and 0036 pinned by name as surviving or not; the null-model split; the cost ranking
with its percentiles; and sequential/parallel agreement on both grids.

Mutation testing was carried out on an **isolated copy** — `src/parseatlas` and the test file were
copied to a scratch tree and each mutation was applied and run there, never in the working tree.

```text
BASELINE                                                            51 passed
KILLED   the power made left-associative
KILLED   left bracket threshold ignores the child's associativity
KILLED   right bracket threshold ignores the parent's associativity
KILLED   agreement audit checks only the top embedding
KILLED   excluded points dropped from the Generation 2 key
KILLED   object groups ordered smallest first
KILLED   the control's object taken as the largest group
KILLED   blocks counted as the support size rather than its factorial
KILLED   distinguishing power counts support instead of its factorial
KILLED   radical detection dropped from the root record
KILLED   an unattempted root list reported as attempted
KILLED   worker count loses the core headroom
KILLED   the parallel decision ignores the measured pool startup
KILLED   tokenizer loses Generation 1's rational literal
KILLED   the block label prints ties as a strict order
KILLED   minimality accepts every bracket without deleting it
KILLED   the domain component of the key replaced by a DIFFERENT constant
SURVIVED (expected) the domain component of the key replaced by the constant it always is

17/18 mutants killed
```

The single survivor is deliberate and is the standing evidence for `NF-2026-00005`: replacing
`canonical["domain"]` by the literal `"R"` leaves all `51` tests green, because `domain` never
varies. The mutant beside it, which replaces it by a **different** constant, dies — so the field is
read, it simply discriminates nothing.
