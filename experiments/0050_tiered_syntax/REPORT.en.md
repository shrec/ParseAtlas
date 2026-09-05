# ParseAtlas experiment 0050: where the flat precedence model ends

## The answer to T26

**A flat precedence CAN capture both of them.** Give the precedence table one row for juxtaposition
and one row for prefix minus, and every tiered convention that is a plain stack of layers becomes a
flat table — not merely matched by one, but *translated into one* by reading each layer's depth in
the stack as its binding power. The translation was put in front of `670174` cells and reproduced
the parse tree in every one of them, with `0` disagreements. The "tiered syntax layers" T26 says are
required are, for a stack of layers, two more rows.

T26 is nonetheless right about something, and it is not the thing it names. Of the `91922`
conventions swept, `47951` have no flat equivalent on the corpus. **Not one of them is a stack of
layers.** They divide as:

```text
kind                conventions   without a flat equivalent   what it is
linear                    14569                           0   a totally ordered stack of layers
exponent_prefix           14569                        6707   Python's factor rule for a power
split                     62784                       41244   a second layer chain inside ^
```

So what defeats a flat precedence table is not tiering. It is a rule that applies **in one syntactic
position and not another** — and a rule of that shape is not a layer, it is a context. The thesis
should be restated to say so, because as written it points at the wrong feature.

**The convention this experiment writes its own corpus in is one of the ones a flat table cannot
reach.** `TIGHT_JUXTAPOSITION` is the printed reading of mathematics and physics: `1/2x` is
`1/(2*x)`, `-x^2` is `-x**2`, and `x^-2` parses. Its sibling differs in exactly one bit — Python's
exponent-prefix rule — and that sibling **does** have a flat equivalent. The shortest source that
separates the printed reading from every one of the `94586` flat models is

```text
-m x + c        read as   (-(m*x)) + c
```

**And the extra syntax buys almost no extra mathematics.** Across `46` corpus sources the tiered
space reaches `94` distinct objects and the flat space reaches `94`. Exactly `3` objects, on `1`
source, are reached by the tiered space and by no flat model — and all `3` come from the `split`
kind, which has no published instance anywhere. The two kinds that do correspond to real practice
add `0`. Symmetrically, `3` objects on `2` sources are reached by the flat space and by no tiered
convention. This is the shape T30 found on the associativity axis: more syntax, no new mathematics.

## Environment

```text
Python                3.14.3
SymPy                 1.14.0
platform              Windows-11-10.0.26200-SP0
cores                 16
workers               15
whole report          113.5 s
```

## Conservative extension, first

The shared parser is untouched. `src/parseatlas/parser.py`, `grammar.py` and `generation_two.py` are
left exactly as they are; this module carries its own tokenizer, its own layered parser and its own
flat parser. That raises the obligation discharged before anything else: restricted to Generation 1,
does the layered parser parse exactly what Generation 1 parses?

```text
sources                     98    0034's cost corpus + 0035's catalogue + 14 hand-written strings
Generation 1 grammars       25
embeddings of ^            123    24 strict x 5 positions + the tied control x 3 positions
conventions per embedding   98    for the control's embeddings
                           242    for a strict grammar's embeddings
cells                  2874732
disagreements                0
```

Every cell compares trees, not strings: the tiered parser builds Generation 1's own `Binary`,
`Number` and `Variable` nodes, so a cell is dataclass equality. It adds exactly one node type,
`Negate`, which a Generation 1 tree can never contain, so a spurious negation anywhere is a
disagreement. A source the tiered convention *rejects* also counts as a disagreement.

**The audit is checked against a real divergence rather than only asked whether it says
conservative.** Two independent checks:

```text
injected saboteur, one wrong tree on  a - b - c        294 disagreements over    28812 cells
literal policy `none`, a real language change         1470 disagreements over    28812 cells
                                                       naming 1/2, 1/2 * a, 1/2 + a,
                                                       a * 1/2, (1/2 + a) * b
```

The second is not a mock. Dropping the composite rational literal is a language anyone might choose,
and it changes what `1/2 + a` denotes; the audit has to name the five affected sources rather than
report an aggregate verdict.

**The site census, which closes the part of the grid the audit does not walk.** Splits are audited
completely over the conventional base and split-free settings are audited over all `123` embeddings.
What makes that enough is not an argument: over all `98` sources the tokenizer sees

```text
juxtaposition sites          0
prefix minus sites           0
```

A slot the parser never reaches cannot change a tree, and the zeros are counted rather than assumed.

## What a convention IS here

A precedence permutation is an ordering of operators. A tier assignment is not that, and saying so
exactly is half the experiment.

- The **base** is one of the `121` Generation 2 grammars — a stack of levels over `^ * / + -`.
- A **placement** puts a new syntactic layer either in a *gap* between two levels, above all of
  them, or below all of them, or *tied* to an existing level. A base with `L` levels has `2L + 1`
  placements: `7` for the conventional base, `11` for a strict one.
- **Juxtaposition** takes a placement. The alias-for-`*` reading is **not** a separate axis — it is
  exactly the tie placement at the level holding `*`, which is observed rather than asserted:
  rewriting every juxtaposition site to an explicit `*` and parsing the rewritten string agrees with
  the tie placement on all `46` sources, `0` disagreements.
- **Unary minus** takes a placement.
- Either placement may be **split** into a general placement and a different one used inside the
  right operand of `^`. A split is the only object in the space that is not a stack of layers.
- **exponent_prefix** admits a prefix minus at the head of `^`'s right operand whatever the minus
  placement says. This is Python's factor rule for a power, and it is what lets a convention read
  `-x^2` as `-(x^2)` and still parse `x^-2`.

That gives `(2L+1) + (2L+1)(2L)` slots for each of juxtaposition and minus, doubled by the flag.

```text
over the conventional base H0     49 x 49 x 2  =     4802
over all 121 Generation 2 bases                   3518642
swept here                                          91922    14569 linear
                                                             14569 exponent_prefix
                                                             62784 split
not swept                                         3426720
```

**The sweep is not the space, and the difference is a computational limit, named here where the
answer is read.** What is swept: every split-free convention over all `121` bases, and every
convention including splits over three bases — `H0`, `H001` and `H120`, the conventional grammar and
the two ends of the strict registry. What is not swept: split conventions over the other `118`
bases. What was checked beyond the limit: the verdict per kind is identical on all three fully swept
bases, and `linear` gives `0` on all `121`.

## The flat model it is compared against

A flat model here is one binding power per role and one rule for prefix admission.

```text
roles                        7    ^  *  /  +  -  JUX  NEG
weak orders on 7 roles   47293    the ordered Bell number; ties are allowed because the
                                  conventional grammar HAS ties, * / together and + - together
prefix rules                 2    level      admit a prefix only where its own power is at least
                                             the level being parsed
                                  anywhere   admit a prefix in any operand position, classic Pratt
flat models              94586
```

Both prefix rules are in the search space on purpose. A model that admitted only the level-respecting
rule would reject `x^-2` in every convention where minus binds looser than `^`, and a flat class
handicapped like that would manufacture a confirmation of T26.

**The two rules are NOT the only two of their kind, and an earlier revision claimed they were.**
Review found a third that depends on nothing but the power table and the level being parsed — admit a
leading `-` iff `power(NEG)` is at least the level being parsed, then parse its operand at that same
ambient level rather than at `power(NEG)` — and adding it alone moves the counts below: exponent
prefix without a flat twin `6707` becomes `5948`, split `41244` becomes `41186`, the total without a
twin `47951` becomes `47134`, and distinct flat reading vectors `7034` becomes `8472`. Three further
flat rules were tried and move nothing or move no count, so the sensitivity is attributable to that
one rule and not to a shotgun.

**The verdict shape survives it**: linear conventions still have a flat twin in every case, and
`TIGHT_JUXTAPOSITION` is still separated at `-m x + c`. But the counts are conditional on the flat
class as enumerated, and this report interrogated its tiered enumeration at length while asserting
the flat one complete. That asymmetry is the same failure experiment 0047 was rejected twice for,
committed on the other side of the comparison, and it is disclosed here rather than defended.

**The flat class is deliberately the larger one.** Its binary part ranges over all weak orders on the
five operators, while the tiered space's binary part is the `121` registered Generation 2 grammars.
Giving the flat side more freedom is what makes a flat model can do it a strong statement; it is
also why the flat space reaches `3` objects the tiered space does not, which is an artefact of that
asymmetry and not a finding about tiers.

## The headline: can a flat precedence do it?

```text
tiered conventions swept                  91922
flat models searched, exhaustively        94586
corpus sources                               46

distinct tiered reading vectors            4903
distinct flat reading vectors              7034
tiered vectors with a flat equivalent      2875
tiered vectors without one                 2028

conventions with a flat equivalent        43971
conventions without one                   47951
```

Per kind, with the shortest source that separates a convention of that kind from the last surviving
flat model. Sources are walked shortest first, ties broken lexicographically, and the separator is
the source at which the last survivor dies.

```text
kind               conventions   without   vectors sep. by rejection   by tree
linear                   14569         0                          0         0
exponent_prefix          14569      6707                        491       699
split                    62784     41244                        404       434

shortest separator, exponent_prefix        a * -b     by rejection
shortest separator, split                  2^-3       by rejection
shortest tree separator, exponent_prefix   e^-k t     read as  (e^(-k)) * t
shortest tree separator, split             x^2y       read as  x^(2*y)
```

`e^-k t` is worth reading twice, because it is exactly Python and exactly ordinary physics. Python
parses the operand after the `-` in an exponent as a *power* and not as a *unary*, so `e**-k*t` is
`(e**-k)*t`.

**An earlier revision explained this by saying a flat table cannot do both halves at once — that to
accept `x^-2` it must admit a prefix anywhere, and a prefix admitted anywhere swallows the juxtaposed
`t`. Review refuted that on this report's own data and both premises fail.** Of the `94586` flat
models enumerated here, `1874` reproduce the printed convention's reading of `e^-k t`, `x^-2`,
`-x^2`, `1/2x`, `2^-3` and `a * -b` **all at once** — `^7,*6,/1,+5,-4,JUX2,NEG3|anywhere` is one. A
`level` model with `NEG` at or above `^`'s power accepts `x^-2` without admitting a prefix anywhere,
and a prefix admitted anywhere does not swallow the `t` when `NEG` binds tighter than `JUX`. In
isolation, `24682` of the `94586` already read `e^-k t` the tiered way, and `3438` match the printed
convention on **all ten** named-ambiguity sources.

The real obstruction is the one the run names, and it is a context rather than a layer: **`-m x + c`**,
where the minus must be LOOSER than juxtaposition outside the exponent while inside it the same minus
must be TIGHTER. No single power table can hold both, and that — not a rule about prefixes — is what
`TIGHT_JUXTAPOSITION` has no flat twin for.

Eleven sources separate at least one convention from the flat space:

```text
-m x + c    1 - x^2/2 + x^4/24    2^-3    a * -b    a - -b    a x + b y - c
a x^2 + b x + c    b^2 - 4 a c    e^-k t    x - x^3/6    x^2y
```

**A flat equivalent is corpus-relative and the report does not pretend otherwise.** Has a flat
equivalent means: some flat model produces the same reading on all `46` sources. It does not mean
the two agree on every string of the language. The `linear` row is the exception and is stronger
than the others, because there the flat model is not searched for but *constructed* from the layer
stack, and the identity is checked on `670174` cells.

## Round trip and minimality, both by exhaustive search

`render_tiered` is a search, not a bracket rule. A rule derived from the parser would have to be
re-derived for every context-dependent slot in the space, and its minimality would then be an
argument. Searching bracket counts upward makes minimality a property of the algorithm: the first
writing that reparses to the tree is by construction one with the fewest bracket pairs.

```text
trees                            46
conventions                    4802    the whole slot space over the conventional base
cells                        220892
round trip failures               0
writings checked             900872
cheaper writings refuted     679980
bracket pairs                100156
```

The writing space is complete for the question asked. A writing that reparses to a tree may place a
bracket only around a node of that tree — any other span would not be a subtree of the parse — and
each `*` node is written either explicitly or as juxtaposition, so the space is the subsets of nodes
crossed with the choice per multiplication, and the search visits all of it below the answer.

**The grid stops at the conventional base because the full space would be over a million cells of
exhaustive search, and that bound is disclosed rather than reported as a finding.** What lies past
it: the same round trip and the same exhaustive minimality over the split-free conventions of the
two other fully swept bases.

```text
trees                            46
conventions                     484    split-free, over H001 and H120
cells                         22264
round trip failures               0
writings checked             124262
cheaper writings refuted     101998
bracket pairs                 13164
```

**One restriction on that enumeration, declared here because it is a restriction.** Only compound
nodes are bracketable. A bracket around a leaf is inert for parsing — `(x)` and `x` are the same
primary in every context — so a writing that brackets a leaf has a strictly cheaper writing with the
same parse and cannot be a minimum. That is an argument, so the wider search is available and the
test suite runs it: over the whole corpus under both named conventions, allowing leaf brackets
changes the bracket count of `0` cells.

**One thing falls out of the renderer that the card did not ask for and is worth a line.**
Juxtaposition is not only a parsing question. Where it binds tighter than the solidus it makes a
writing cheaper, which is direction B's own currency:

```text
object            1/(2*x)
alias reading     1 / (2 * x)      1 bracket pair
printed reading   1 / 2x           0 bracket pairs
```

## The ambiguity atlas

Over the `4802` conventions of the conventional base, grouped by the **object** each reading denotes
rather than by the tree, because two trees denoting the same object are not a disagreement about
mathematics.

```text
source          question                              object        conventions   published reading
-x^2            is it -(x^2) or (-x)^2 ?              -x**2                4116   mathematical
                                                      x**2                  686   spreadsheet
-2^2            is it -4 or 4 ?                       -4                   4116   mathematical
                                                      4                     686   spreadsheet
1/2x            is it (1/2)*x or 1/(2*x) ?            x/2                  2744   left to right
                                                      1/(2*x)              2058   printed mathematics
6/2(1 + 2)      is it 9 or 1 ?                        9                    2744   left to right
                                                      1                    2058   printed mathematics
2x^2            juxtaposition tighter than ^ ?        2*x**2               3430   universal
                                                      4*x**2               1372   no published practice
x^2y            is the exponent 2 or 2y ?             x**2*y               3528   exponent is one token
                                                      x**(2*y)              686   exponent is the group
```

Every named published reading is reached; `0` are missing. `x^2y` is additionally **rejected** by
`588` of the `4802` conventions — those in which the juxtaposition layer is unreachable from an
exponent — which is a third answer that a precedence table cannot give at all.

The attributions in the right-hand column are attributions and are labelled as such. The objects and
the counts beside them come from the run.

## The null model, which decides whether the card found anything

Experiment 0030 widened the convention axis with associativity, recovered under 12 percent of the
gap, and added 50 percent more syntax for zero new mathematics. The same question, asked of tiers:
how many distinct mathematical objects does the tiered space reach that the flat space does not?

```text
corpus sources                                        46
tiered conventions                                 91922
flat models                                        94586
distinct objects reached by the tiered space          94
distinct objects reached by the flat space            94
objects only the tiered space reaches                  3   on 1 source
objects only the flat space reaches                    3   on 2 sources
```

Stratified by role support, because a source using `j` of the `7` roles cannot separate models that
agree on those `j`, and an unstratified count would be the registry rather than the mathematics:

```text
roles used   sources   tiered objects   flat objects   only tiered   only flat
         1         4                4              4             0           0
         2        27               41             41             0           0
         3        15               49             49             3           3
```

And stratified by convention kind, which is the axis the headline turns on:

```text
kind                objects only the tiered space reaches
linear                                                  0
exponent_prefix                                         0
split                                                   3
```

The three objects, all on `a x^2 + b x + c`:

```text
a*x**((b + 2)*(c + x))
a*x**(b*x + c + 2)
a*x**(c + x*(b + 2))
```

These are degenerate readings of a quadratic, produced only by conventions in which juxtaposition
sits at one tier in general and a different one inside an exponent. No published notation does that.
The two kinds of convention that *do* correspond to published notation — a stack of layers, and
Python's exponent-prefix rule — reach `0` objects the flat space misses.

The three objects the flat space reaches and the tiered space does not are
`c + x*(a**2*x**2 + b)` on `a x^2 + b x + c`, and `-2**(1/6)*x**(1/6) + 1` and `1` on
`1 - x^2/2 + x^4/24`. They exist because the flat search ranges over all weak orders on five binary
operators while the tiered space's binary part is the `121` registered grammars. That is an
asymmetry in the two spaces, disclosed above, and not a property of tiering.

## The tokenizer decides more than the grammar does

Juxtaposition exists only where the tokenizer can see it, so what it accepts is part of the result.

```text
accepted as juxtaposition     2x     2 x     2(x + 1)     (a + b)(a - b)     x y     (x + 1)y
refused                       xy     x2                   one identifier, by Generation 1's
                                                          maximal-munch name pattern
```

Consequence, visible in every corpus entry rather than hidden: the quadratic is written
`a x^2 + b x + c` and not `ax^2 + bx + c`, because `ax` is one variable.

The number pattern matters more. Generation 1 admits an unspaced `1/2` as one rational literal. Kept
unchanged, that rule *destroys the ambiguity this card is about*: `1/2x` would be the literal `1/2`
juxtaposed with `x` under every convention, and the published disagreement would be settled by the
lexer before any precedence rule ran. So the rule is an explicit axis with three values, and the
sensitivity is reported here rather than in a limits section:

```text
policy   readings of 1/2x   objects                conservative over Generation 1
gen1                    1   x/2                    yes, 0 disagreements over 28812 cells
split                   2   x/2  and  1/(2*x)      yes, 0 disagreements over 28812 cells
none                    2   x/2  and  1/(2*x)      NO, 1470 disagreements over 28812 cells
```

`split` is the default: a composite literal is split back into two integers and a division only when
a juxtaposable primary follows it with no space. Under it `1/2x` is ambiguous and `1/2 x` is not,
which is also how the two are read on paper. It stays conservative because no Generation 1 string
can have a literal followed immediately by a name — that is juxtaposition, which Generation 1 cannot
write — and the audit observes this rather than arguing it.

## What this enumeration does NOT produce

An enumeration is a claim about what exists, so the writings the space omits are listed before the
counts are believed, and the one that could plausibly move the answer is checked rather than argued.

```text
omitted                                              could it change the answer?
juxtaposition restricted by operand kind             CHECKED, it does not
unary +                                              no: orthogonal to both named interactions
left-associative ^                                   no: 0030's axis, it moves counts, not shape
a context other than the right operand of ^          it can only ADD non-flat conventions
more than two contexts                               same
juxtaposition as a chunk, not a left chain           no: the fold is left-associative either way
a tokenizer that reads xy as a product               yes, and it is the disclosed tokenizer limit
function application                                 out of the language entirely
```

The checked one, in full. Real notation never writes a product of two variable names as an adjacency
in linear text — `xy` would be one identifier — so a convention forbidding exactly that adjacency is
plausible, and it is not a tier placement, so it is outside the declared space by construction. The
check rewrites every corpus source so no name-name adjacency remains and re-runs the whole headline
on the rewritten corpus, over the `4802` conventions of the conventional base:

```text
sources rewritten            44 of 46
kind               without a flat equivalent, unrestricted   restricted
linear                                                   0            0
exponent_prefix                                         31           28
split                                                 2755         2590
```

The counts move; the verdict does not. `linear` is `0` either way, and both context-dependent kinds
remain non-zero.

## Multicore

The decision is taken from observations on this host, not from a rule of thumb. The worker count is
derived from the observed core count with one core of headroom, never from a constant.

```text
cores                                        16
workers                                      15
pool startup, two runs                     2.00 s   and   7.16 s
audit         123 payloads x 0.448 s  =   55.13 s sequential   ->  parallel
sweep          60 payloads x 1.453 s  =   87.16 s sequential   ->  parallel
render         60 payloads x 0.336 s  =   20.16 s sequential   ->  parallel
```

The routing decision is insensitive across the observed startup range: at the larger figure the
cheapest workload still costs `8.51 s` in parallel against `20.16 s` sequential. Parallelism changes
only how fast, never what is produced, and the test suite checks that rather than assuming it: the
agreement audit, the translation audit and the render audit each return equal structures at
`workers=1` and at `workers=3` or `workers=4`.

The heavy sweep would not fit in the pickling budget in its obvious form. Sending the flat answer to
each worker means sending tens of thousands of reading vectors; instead each source's handful of
distinct readings is coded to one byte and a vector becomes `46` bytes. That changes no number, only
how much of the run is spent moving data.

## Limits

- **The convention space is declared.** It is `3518642` conventions and `91922` were swept, leaving
  `3426720` unswept, being split conventions over `118` of the `121` bases. A different enumeration
  would move every count here. The verdict per kind is identical on all three fully swept bases and
  `linear` is `0` on all `121`, which is what the extension rests on.
- **The corpus is hand-chosen**, `46` sources across `6` areas, and it is the corpus a separating
  source is looked for in. A source outside it could separate a convention this report records as
  having a flat equivalent.
- **A flat equivalent is corpus-relative** except in the `linear` row, where it is a constructed
  identity checked on `670174` cells.
- **Juxtaposition is only meaningful where the tokenizer can see it.** Accepted: `2x`, `2 x`,
  `2(x + 1)`, `(a + b)(a - b)`, `x y`, `(x + 1)y`. Refused: `xy` and `x2`, which are single
  identifiers under Generation 1's maximal-munch name pattern, kept unchanged.
- **The composite rational literal is an axis, not a fact.** Under `gen1` the named ambiguity `1/2x`
  has `1` reading rather than `2`, and the whole `1/2x` row of the atlas disappears.
- **Rejections count as readings** in the vector comparison. `895` of the `2028` unmatched vectors
  are separated from the flat space by a rejection rather than by a different tree; the other `1133`
  are separated by a tree.
- **The domain component of the semantic key is inert.** It is set to `R` for every expression
  (NF-2026-00005), so the operative identity is the canonical form with the excluded points.
- **A pole written as a negative exponent is not detected.** `x^-2` contributes no excluded point,
  which is Generation 2's disclosed limit inherited unchanged, and the corpus does contain such
  entries.
- **Associativity is fixed for the BINARY operators** — `^` right, everything else left,
  juxtaposition left — and widening that is 0030's axis and is not done here. The bullet previously
  said associativity is fixed without qualification, which the run contradicts: `3178` tiered
  conventions and `37386` flat models differ in how the prefix interacts with `^`, which is an
  associativity choice in everything but name.
- **Only compound nodes are bracketable** in the writing enumeration. The wider search is available
  and changes the bracket count of `0` cells over the corpus under both named conventions.
- **The multicore constants are host observations**, and the pool startup differed by a factor of
  `3.58` between two runs on the same machine.

## Evidence classification

- The conservative-extension result, the translation identity, the flat-equivalence verdicts, the
  atlas counts and the null-model counts are executable **observations**.
- The restatement of T26 — that the obstruction is a context and not a layer — is an **observation**
  plus an explicit argument, and the argument is the one about uniform prefix rules given above.
- The attributions of readings to published practice are attributions, not observations.
- No claim is made that a convention outside the declared space behaves as the ones inside it do.

## Validation

```text
python -m pytest -q tests/test_tiered_syntax.py
54 passed
```

Mutation testing was run on an isolated copy of the tree and never on the working tree. `12`
mutants were applied to the load-bearing lines — the layer-stack builder, the associativity rule,
the juxtaposition and exponent-prefix branches of the parser, the composite-literal rule, the
spacing rule, the flat prefix rule, the flat translation, the vector coding, the bracket search, the
audit comparison and the role support.

```text
first pass       11 killed    1 survived
survivor         an audit that treated a REJECTION as agreement
why it lived     the site census is 0, so no cell in a passing run ever rejects, and every other
                 test in the file passes with the branch broken
closed by        routing both audit paths through one cell comparison and reaching that branch
                 from a test with a convention that really does reject its input
second pass      12 killed    0 survived
```

That survivor is worth recording rather than quietly fixing. It is the same shape of hole 0045 had:
a branch that a green run never enters, guarded only by tests that assert the aggregate verdict.
