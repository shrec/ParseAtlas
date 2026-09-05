# ParseAtlas experiment 0056: twenty-five native machines against one machine plus a conversion

## The owner's question, answered first

The owner asked three times for `25` native parsers rather than lookup tables - each world its own
state machine, translating the string straight into that world's dataflow, compiled once and executed
a million times. **They are built, they agree with the table-driven parser on every one of the
`11000` checked cells, and they buy nothing.** Against the project's shipped parser the native
machines are faster - `1.094` times for the level-unrolled variant and `1.139` times for the
partially-evaluated one, medians over the `25` worlds - and they earn back their generation after
`430` and `265` string parses respectively, `256` to `1848` and `180` to `478` across the worlds, so
the compile-once-execute-many trade does pay against what the project runs today. But against the
**fair** control - the same generated code with only its binding-power lookup put back, one
compilation shared by all `25` worlds - the median over the `24` strict worlds is `0.946` to `0.959`
for the level-unrolled machine and `0.991` to `1.002` for the partially-evaluated one over six runs:
the first is resolvably **slower** and the second is indistinguishable, and the break-even is
**never** in `66` of `75` pooled readings for the first and `40` of `75` for the second. The entire
measured win is the shipped parser rebuilding its binding-power dictionary on every call, which a
lookup machine removes without specialising anything. **Essentially all of the effect is partial
evaluation, and none of it is about conventions**: the `24` strict native machines are, after
normalising their operator literals to their `(level, slot)` positions, **byte-identical source** -
one program with four symbols permuted - so there is no per-world code for a per-world speed
difference to come from, and the spread that the stopwatch does show across those `24` worlds is no
wider than the noise floor allows, measured with the same instrument on two machines whose true ratio
is exactly `1`. The half that survives is question 3: the emitted graphs really do differ, real
mathematics has `1` to `10` distinct readings per formula and the generated words up to `20` of a
possible `24`, the `24` orderings' mean depth and mean peak-live values are anti-correlated at
Spearman `-0.9719` on the named corpus, and at `-O2` the choice of world changes what `clang`
actually issues - from `10` to `14` instructions on one statistical formula and from `159` to `211`
on a `128`-operand word - with no noise floor on that sentence at all.

---

## What was built

`src/parseatlas/native_machines.py`. One generator emits the machine for a world, so a world is
**data to the generator and a constant to the machine**. Three variants come out of it, and the
third is the control that makes the first two readable:

```text
levels    one function per precedence level, unrolled.  No Grammar object, no dictionary, and the
          binding powers do not appear at all - they have become the call structure.
climb     the table-driven loop with its lookup partially evaluated away: one recursive function,
          the operator literals and the integer powers all constants of the code.
lookup    the same single function with the powers read from an injected POWERS dictionary at run
          time.  Its source contains NO world-specific text, so one compilation serves all 25.
```

The definition of "native" is enforced by test rather than asserted: in a native machine's emitted
source **the only subscript anywhere is into the token array**, so no table of any name is consulted
at run time.

Five architectures are compared, on the same strings, with the same denominator:

| architecture | what it is | one-off cost |
|---|---|---|
| `native_levels` | the level-unrolled machine, generated per world | `1` compilation per world |
| `native_climb` | the partially-evaluated climb machine, generated per world | `1` compilation per world |
| `table` | `parseatlas.parser.parse` exactly as the project ships it | none; it rebuilds its table per call |
| `table_lookup` | the generated control: same code, table at run time | `1` compilation for the whole registry |
| `convert` | conventional front end, then rewrite into the target world | none |

The corpus is `110` strings: the `58` named laws of experiment 0034's corpus, imported whole, and
`52` generated words - one per `(length, support)` over lengths `2` to `128` and supports of size
`1`, `2`, `3` and `4`.

---

## The null model, declared before any number and measured in two ways

A specialised parser beating a table-driven one says nothing about the `25` worlds; it is the
ordinary win of partial evaluation and it would appear with one world just as with twenty-five. The
control is therefore native `G0` against table-driven `G0` - the same world - and every claim is
stated against it.

**The structural half is stronger than any ratio and it comes first.** Each machine is emitted
symbolically, with every operator literal replaced by its `(level, slot)` position:

| variant | distinct normalised sources over the `25` worlds | classes | source bytes, `G0` / strict |
|---|---|---|---|
| `levels` | `2` | `24` + `1` | `2118` / `2633` |
| `climb` | `2` | `24` + `1` | `2253` / `2254` |
| `lookup` | `1` | `25` | identical in every world |

The `24` strict machines are **one program with four symbols permuted**. `G0` stands apart in both
native variants, and the reason is not an ordering: it is the only world in the registry with **tied**
precedence levels, so its `levels` machine has `2` level functions where the strict worlds have `4`.

**The timed half.** The noise floor is measured with the same paired instrument that produces every
ratio, on two byte-identical machines whose true ratio is exactly `1`:

```text
paired deviation from 1, median over the 25 worlds      1.4% - 1.9%
paired deviation, worst world                          11.4% - 15.9%
paired deviation, worst single round                   46.0% - 72.4%
unpaired gap between two independent medians            3.75% - 3.84% median, 45.4% - 80.1% worst
```

So a **single world's** ratio is not a resolvable quantity here, and none is presented as one. The
median over the `24` strict worlds is resolvable, because the floor on that statistic is the `1.4`
to `1.9` percent row. Read against it:

| quantity | `native_levels` | `native_climb` |
|---|---|---|
| strict-world median ratio against the lookup control, six runs | `0.946` - `0.959` | `0.991` - `1.002` |
| `G0` control ratio, six runs | `0.982` - `1.094` | `0.968` - `1.064` |
| worlds slower than the control, per run, of `25` | `21` - `24` | `10` - `15` |
| spread of the `24` strict ratios within one run | `0.086` - `0.245` | `0.101` - `0.187` |

The `24` strict worlds run **byte-identical code**, so their true ratios are equal up to what the
corpus's operator mix does to the tree shape; the observed spread of `0.086` to `0.245` is therefore
a second, independent reading of the same noise floor, and it is no wider than that floor allows.

**The conclusion the card was willing to reach.** The native architecture buys what partial
evaluation always buys, and nothing about conventions. Where it appears to buy more, the comparison
was against a parser that rebuilds its table per call.

---

## Question 1 - capability

**Stated before measuring: there is no capability gap.** A conversion that may rewrite a tree
arbitrarily reaches every tree, so both architectures reach exactly the same set of trees. The
honest questions are cost and soundness, and three things are measured rather than asserted.

**The `25` worlds accept exactly the same string language.** Every grammar in the registry describes
`primary (operator primary)*` with parentheses; only the tree differs. Over `2750` acceptance checks
(`110` strings x `25` worlds) and `250` rejection checks (`10` declared malformed strings x `25`
worlds) there are `0` failures in either direction. No world can express a string another world
cannot read.

**The conversion carries a real obligation, and the obvious implementation violates it.** A
conversion driven by the conventional parse *tree alone* is unsound: the tree does not record which
sub-expressions were bracketed, so it cannot tell `(a * b) + c` from `a * b + c` - those are the same
`G0` tree - and the two must part company in a world where `+` binds tighter than `*`. Measured
through the same audit the published agreement number comes from, the bracket-blind conversion is
wrong in `498` of `2750` cells, in **all `25`** worlds, while the native and lookup columns stay at
`0`. The sound conversion therefore needs a front end that preserves the bracket structure - strictly
more than the conventional parser produces.

**Having preserved it, the conversion then throws away everything else the front end computed.** The
rewrite reads the token order and the bracket boundaries and nothing else: the conventional parse's
work of deciding that `a + b * c` groups as `a + (b * c)` is discarded by the flatten. This is a
property of the architecture and not of the implementation, because any sound conversion must be free
to re-associate every unbracketed region and so cannot inherit the front end's associations.

**What this means for thesis T31.** Reachability outranks cost - but reachability does not separate
these two architectures, because they reach the same trees from the same strings. The criterion falls
through to cost, which is what questions 2, 3 and 4 measure. Experiments 0043 and 0028 are about
which trees a *convention* can reach cheaply; nothing in either distinguishes a native reader of a
convention from a converted one.

---

## Question 2 - throughput, with generation reported on its own line

### Generation, which is paid once

| architecture | compilations for the whole registry | one-off seconds, whole registry | one-off seconds, per world |
|---|---|---|---|
| `native_levels` | `25` | `0.0106`, range `0.0106` - `0.0262` over three suite runs | `0.000436`, `0.000388` - `0.000932` across worlds |
| `native_climb` | `25` | `0.0093` | `0.000374`, `0.000330` - `0.000820` across worlds |
| `table_lookup` | `1` | `0.000319` | `0.0000015` marginal, the table alone |
| `table` (shipped) | `0` | `0.0` | `0.0` |

The asymmetry is the architectural trade and it is measured rather than assumed: a native machine's
source differs in every world, so nothing can be shared; the control's source is identical in every
world, so the compilation is done once and each world costs one dictionary. The registry-level
overhead of going native is `0.0103` seconds for the `levels` variant and `0.0090` for `climb`.

### Execution, in the owner's unit

Medians over the `25` worlds, `58` named strings per pass, `20` passes and `9` repeats per block, so
`1160` parses per timed block:

| architecture | seconds per string | strings per second |
|---|---|---|
| `native_levels` | `0.000010978` | `91089` |
| `native_climb` | `0.000010242` | `97635` |
| `table` (shipped) | `0.000011668` | `85702` |
| `table_lookup` (control) | `0.000010260` | `97470` |
| `convert` | `0.000027680` | `36127` |

**These absolute figures are the weakest numbers in the card and they say so here.** `55` of the
`125` rate cells have their own repeats spanning more than a factor of `1.5`, which is interference
and not a reading of that cell; the world-by-world column ranges from `11.1` to `30.9` microseconds
for the same shipped parser. The ratios below are measured with the paired instrument instead, and
they are what the conclusions rest on.

### How many executions before native pays for its own generation

Against the shipped parser, the native machines are faster and the break-even is finite in **all `25`
worlds**:

| variant | ratio against the shipped parser, median over worlds | break-even, per world | registry break-even |
|---|---|---|---|
| `native_levels` | `1.094`, range `1.033` - `1.182` | `430`, range `256` - `1848` | `15370` parses, `615` per world |
| `native_climb` | `1.139`, range `1.091` - `1.249` | `265`, range `180` - `478` | `6517` parses, `261` per world |

Against the lookup control the answer is **never** in most cells: `66` of `75` pooled readings for
`native_levels` and `40` of `75` for `native_climb` report no gap at all. Where a reading is finite it
is large and unstable - median `1778` and `2321` parses, maxima `7903` and `67386` - which is what a
break-even looks like when it is dividing a fixed cost by a gap that is not resolvably positive.

**And the shipped parser's disadvantage is one line of code, not an architecture.** The lookup
control runs at `97470` strings per second against the shipped parser's `85702` without specialising
anything at all: it is the same algorithm with its binding-power dictionary built once instead of per
call.

### The conversion architecture

Parse-then-convert costs `2.251` to `2.868` times the lookup machine, median `2.660`, over the `25`
worlds. That is the price of the architecture the card put on trial against native: a front end whose
shaping work is discarded, plus a flatten, plus a reshape.

### The length sweep - no threshold was declared and none was found

Expression length is swept over `13` points from `2` to `128` operands, in two worlds, with the
passes per block scaled so every point does comparable work (`3000` operand-parses), `9` paired
rounds each. Six series result - two native variants and the conversion, in `G0` and in `G01`.

```text
                        sign changes   resolvable turns   median ratio range
G0:native_levels                   7                  0        0.991 - 1.070
G0:native_climb                    6                  0        0.957 - 1.082
G0:convert                         5                  0        0.319 - 0.616
G01:native_levels                  6                  0        0.952 - 1.025
G01:native_climb                   7                  0        0.966 - 1.029
G01:convert                        5                  0        0.307 - 0.676
```

**Every series has sign changes and not one of them is resolvable** against the round-to-round spread
of the three points involved. So over the whole swept range there is no length at which the native
machine becomes resolvably faster, and no turning point. What does move is the conversion's penalty:
it falls from `3.135` times the lookup machine at `2` operands to `1.668` at `128` in `G0`, and from
`3.259` to `1.595` in `G01`, as its fixed overhead amortises. That decline has no resolvable turning
point either.

An earlier revision of this sweep used a fixed number of passes at every length and produced ratio
readings of `0.377` and `0.356` at `3` operands. Those were the timer, not the expression, and the
scaling above is why they are gone.

---

## Question 3 - the emitted dataflow, which is the real subject

Every string is read by every world's **own native machine** - not converted, not re-parsed - and the
resulting graph is profiled with the three measures the project already owns: operation count (0021),
critical-path depth (0041, a leaf at `0`), and peak simultaneously live values (0044).

### The operation count is world-invariant, and everything else in this section depends on it

A convention re-associates a fixed sequence of operator tokens and every token becomes exactly one
node, so no world can issue an operation another world does not. Checked over `2750` cells: it holds
on all `110` entries. The negative control - one cell's multiset corrupted before the check - makes
the check fail, through the same function. **What a convention changes is the shape of the graph, not
its work.**

### On real mathematics the shapes barely differ

Over the `58` named laws, per world:

| | mean depth | mean peak live |
|---|---|---|
| shallowest worlds | `2.5000` (`G16`, `G17`, `G18`, `G23`, `G24`) | `2.4310` (`G02`, `G05`, `G08`) |
| `G0`, the conventional convention | `2.5172`, `6th` of `25` | `2.5345` |
| deepest worlds | `2.7069` (`G02`, `G05`, `G08`) | `2.5690` (`G17`, `G18`) |

The whole spread is `0.207` levels of depth and `0.138` live values. `30` of the `58` formulas have
**identical depth in all `25` worlds** and `38` of `58` identical peak live values; the mean depth
spread across worlds is `0.500`.

**The two measures are almost exactly opposed.** Ranking the `25` worlds by mean depth and by mean
peak live values on the named corpus gives a Spearman correlation of `-0.9719`. The worlds that read
real mathematics into the shallowest graphs are the same worlds that need the most simultaneously live
values. This is the classical depth-against-registers trade appearing as a property of the
*conventions* themselves rather than of a choice of writing, and it is new here: 0041 and 0044
measured the same two quantities per world as costs of a chosen writing, not as readings of a fixed
string.

### On generated words the shapes differ a great deal, and `G0` is the outlier

Over the `52` sweep words:

```text
mean depth, the 24 strict worlds      18.1346 (G03)  to  18.8269 (G10, G16, G18, G24)
mean depth, G0                        22.8269   -   4.00 deeper than the DEEPEST of the 24, 21.2%
                                                  -   4.69 deeper than the shallowest,       25.9%
```

The reason is structural rather than accidental: `G0` is the only world with tied precedence levels,
so a run of operators at the same level becomes a left chain, and a chain is as deep as it is long.
The combined-corpus figure - `G0` at `12.1182` against `9.9727` to `10.2364` for the `24` strict
worlds - is therefore **an artifact of the generated family and must not be quoted as a statement
about mathematics.** On the named corpus `G0` is `6th` of `25`.

### How many distinct graphs there actually are, against the T6 bound

**The bound is stated first.** Theorem T6 (experiment 0019) says a grammar acts on an expression only
through its restriction to the operators that expression uses, so over the `24` strict permutations a
word with `s` distinct operators can be read into at most `s!` distinct trees. `G0` is the
twenty-fifth world and is not a permutation, so over all `25` the bound is `s! + 1`.

Then the corpus is enumerated against it. The bound is respected on all `110` entries; `63` are at it
and `47` below it.

| support size | entries | bound `s!` | mean distinct trees | maximum |
|---|---|---|---|---|
| `1` | `21` | `1` | `1.000` | `1` |
| `2` | `47` | `2` | `1.681` | `2` |
| `3` | `31` | `6` | `3.645` | `6` |
| `4` | `11` | `24` | `19.000` | `20` |

Split by family, because the two halves say different things:

```text
named laws, 58 entries    mean 1.879 distinct trees, maximum 10, at the bound in 23 of 58
generated words, 52       mean 6.019 distinct trees, maximum 20, at the bound in 40 of 52
```

**In real mathematics the twenty-five worlds are nowhere near twenty-five meanings.** Of the `58`
named laws, `21` are read into exactly `1` tree by all `24` strict worlds, `34` into exactly `2`, two
into `5`, and exactly one - `variance_of_two_points`, the only formula in the corpus using all four
operators - into `10`. The support-size histogram explains it: `5` formulas use one operator, `33` use
two, `19` use three, and `1` uses four.

**And `G0` is not a twenty-fifth meaning on any named law.** Its reading coincides with some strict
permutation's reading on all `58` of them. `G0` is distinct from all `24` strict readings on `20`
entries, and every one of those is a generated word.

### What the corpus falling below the bound does and does not mean

A corpus below a bound says nothing about the bound, so the bound was searched **exhaustively**. Every
word over the four operators was enumerated for `4`, `5`, `6`, `7`, `8` and `9` operators, the
four-operator ones kept, and each read by all `24` strict machines - `237528` words in total, a finite
space searched completely:

| operators | operands | four-operator words | maximum distinct trees | words attaining `24` |
|---|---|---|---|---|
| `4` | `5` | `24` | `14` | `0` |
| `5` | `6` | `240` | `19` | `0` |
| `6` | `7` | `1560` | `21` | `0` |
| `7` | `8` | `8400` | `22` | `0` |
| `8` | `9` | `40824` | `24` | `264` |
| `9` | `10` | `186480` | `24` | `3888` |

**The T6 bound of `24` is tight, and the shortest word that attains it has `8` operators.** A witness
is `v0 + v1 - v2 * v3 + v4 / v5 - v6 * v7 / v8`. No word of `7` operators or fewer reaches it, and
that is a completed search rather than a stopped one. Over those `237528` words the observed counts
are `14`, `15`, `16`, `17`, `18`, `19`, `20`, `21`, `22` and `24`; **`23` never occurs**, which is
measured on this search and claimed for nothing longer.

The structural sweep was carried past the timed one, to `192`, `256`, `384` and `512` operands. At
every one of those lengths a four-operator cycling word gives exactly `20` distinct trees of a
possible `24`, and the `+ - *` word gives exactly `6` of `6`. So **length does not buy distinctness;
pattern does** - a hand-chosen `9`-operand word reaches `24` where a `512`-operand cycling word
reaches `20`.

---

## Question 4 - does it reach the metal

Four objects, chosen by a declared rule - the two widest depth spreads in the named corpus and the two
in the generated family, ties broken by the number of distinct graphs and then by name - emitted as C
functions by the transcription method of experiment 0053 (one
operation per statement into a named `double` temporary, so the C source is a transcript of the graph
rather than something a C compiler's own precedence has to rebuild), all `25` worlds' readings of one
object in one translation unit, compiled with `clang 21.1.0` for `x86_64-pc-windows-msvc` at `-O0` and
`-O2`, and the mnemonics inside each function counted from `clang -S` output. **Two multisets of
mnemonics are equal or they are not; there is no noise floor on anything in this section.**

**What is compared here is not what 0053 compared, and the difference matters.** 0053's kernels were
equivalent writings of one value, so an instruction difference was a difference in how the same
computation was expressed. Here the `25` readings of one string denote up to `s!` *different*
functions. Because the operation multiset is world-invariant, the arithmetic asked for is the same in
every world; a difference in total instructions is therefore data movement and scheduling.

| object | operations | distinct trees | `-O0` multisets | `-O0` instructions | `-O2` multisets | `-O2` instructions |
|---|---|---|---|---|---|---|
| `variance_of_two_points` | `10` | `10` | `3` | `37` - `39` | `9` | `10` - `14` |
| `confidence_interval_upper` | `3` | `5` | `1` | `17` | `1` | `4` |
| `sweep_+-*_128` | `127` | `7` | `1` | `513` | `4` | `167` - `209` |
| `sweep_+-*/_128` | `127` | `21` | `1` | `513` | `14` | `159` - `211` |

**At `-O0` the model is exactly right and the conventions are nearly invisible.** The arithmetic
`clang` issues equals the model's operation count in all `100` kernels - `4` objects x `25` worlds -
so the structural numbers of question 3 are about the computation the machine actually runs. Three of
the four objects compile to a **single** instruction multiset across all `25` worlds. The fourth splits
into `3`, at `37`, `38` and `39` instructions over `8`, `8` and `9` worlds, with the arithmetic
identical (`3` add, `1` sub, `3` mul, `3` div) in every one: the difference is entirely data movement,
and it is at most `2` instructions.

**At `-O2` the picture inverts.** Only one object still collapses - `confidence_interval_upper`, `4`
instructions in all `25` worlds, the choice of world erased completely. The others do not:

- `variance_of_two_points` spans `10` to `14` instructions over `9` distinct multisets, and **the
  arithmetic itself now differs**: `9` of the `25` worlds issue no division at all, and five of them
  (`G05`, `G06`, `G19`, `G20`, `G21`) come out at `1` add, `1` sub, `5` mul, `0` div for `10`
  instructions, while `G09` and `4` others issue `3` add, `1` sub, `3` mul, `2` div for `13`. The
  model's world-invariance of the operation count is exact at `-O0` and **false at `-O2`**, because
  common-subexpression elimination and reciprocal substitution find different amounts of redundancy in
  different worlds' readings of the same string;
- `sweep_+-*_128` keeps its arithmetic identical everywhere (`43` add, `42` sub, `42` mul) and still
  splits into `167` (`4` worlds), `168` (`12`), `170` (`5`) and `209` (`4`) instructions - a `25.1`
  percent spread from scheduling and data movement alone;
- `sweep_+-*/_128` spans `159` to `211` instructions over `14` multisets and `5` distinct arithmetic
  multisets. **`G0` alone sits at `159`, the fewest of all `25` worlds** - while being the deepest tree
  of all `25`, at depth `65` against a minimum of `33`.

**The model's depth ranking is inverted at the metal on the sharpest object.** Spearman correlation
between the model's critical-path depth and the instructions `clang` emits at `-O2`:

```text
variance_of_two_points     depth vs instructions  -0.7268     peak live vs instructions  +0.6290
sweep_+-*/_128             depth vs instructions  -0.1242     peak live vs instructions  +0.4468
sweep_+-*_128              depth vs instructions  +0.0969     peak live vs instructions   0.0000
```

At `-O0` the two `128`-operand words have identical instruction counts in all `25` worlds, so both
correlations there are exactly `0`. The deeper the model says a graph is, the *fewer* instructions the
optimiser emits for it on the object where the effect is largest. This is the divergence the owner
named when setting 0053 - hardware has parts the formulas do not describe - arriving now on the
convention axis rather than on the writing axis.

---

## Multicore, decided by measurement

`16` logical cores observed; `2` held back so a sweep cannot starve the interactive session; `14`
workers.

| path | sequential | parallel | decision |
|---|---|---|---|
| structural sweep, `25` worlds x `110` strings | `0.2371` s median, `0.2361` - `0.2481` | `1.0666` s median with `14` processes | **sequential** |
| compilation, `16` `clang` invocations | `0.8913` s | `0.1775` s with `14` threads, `5.02` times faster | **threads** |
| timing | always | never | **sequential**, by policy |

The pooled structural sweep is `4.50` times *slower* than the sequential one and the reason is not
pool startup: startup is `0.000289` seconds, `0.027` percent of the pooled time. The cost is per-job
process overhead against `0.0000862` seconds of work per cell, and the pooled results are identical to
the sequential ones. Timing runs are never parallel because concurrent load changes what a stopwatch
measures rather than how fast it measures.

---

## Reproduction

```bash
python -c "import json, parseatlas.native_machines as m; print(json.dumps(m.native_machines_report(), indent=1, default=str))"
python -m pytest tests/test_native_machines.py -q
```

Individual measurements: `agreement_audit`, `language_identity_audit`, `machine_isomorphism_audit`,
`noise_floor`, `tokenizer_share`, `registry_generation_cost`, `throughput_table`,
`specialisation_control`, `throughput_repeatability`, `length_curve`, `dataflow_table`,
`operation_invariance`, `distinct_graph_table`, `bound_attainment`, `long_word_check`,
`instruction_table`, `parallel_decision`. The `9`-operator row of the enumeration is
`bound_attainment((9,))` and takes `389` seconds; it is not in the default sweep.

```text
Windows-11-10.0.26200-SP0, AMD64, Intel64 Family 6 Model 167 Stepping 1, 16 logical cores
Python 3.14.3
clang version 21.1.0, target x86_64-pc-windows-msvc
```

---

## Limits

- **One machine, one interpreter, one compiler.** Every timing belongs to CPython `3.14.3` on this
  box. CPython `3.14` has a specialising adaptive interpreter of its own, and it is entirely possible
  that it already performs at run time some of what this card's generator performs ahead of time; a
  different runtime could reorder every ratio in question 2. Nothing here generalises past this box.
- **Per-world timing is not resolvable at this precision, and no per-world timing claim is made.** The
  paired noise floor reaches `15.9` percent on a world whose true ratio is exactly `1`. Only the
  median over the `24` strict worlds is read, and only because its own floor is `1.4` to `1.9` percent.
- **`55` of the `125` absolute-rate cells are contaminated** by the declared criterion, their own
  repeats spanning more than a factor of `1.5`. One world's tokenizer-share cell returned `1.200`,
  which is physically impossible - tokenizing cannot take longer than tokenizing and parsing - and is
  reported rather than dropped. The strings-per-second table is the weakest evidence in the card.
- **The shared tokenizer is `61` percent of a native end-to-end parse** (median over the `25` worlds,
  `0.6083` and `0.6143` in two runs, `0.4303` to `1.200` across worlds), so the ceiling on any parser
  specialisation measured end to end is `1.644`. A specialisation confined to the parse step cannot
  show more than that in the owner's unit, and this card did not specialise the tokenizer.
- **Only `-O0` and `-O2` were compiled.** `-ffast-math` is deliberately out of scope: it lets the
  compiler reassociate, and reassociation is precisely the difference between the `25` worlds'
  readings, so measuring under it would be asking whether the compiler can undo the conventions rather
  than what the conventions cost. 0053 measured that question on the writing axis and found
  `-O3 -ffast-math` erasing half of its objects.
- **The generated corpus follows one rule** - operators cycled in a declared order - and the
  exhaustive enumeration covers only words of `4` to `9` operators. The claim that `23` distinct trees
  never occur is a statement about those `237528` words and about nothing longer.
- **The structural sweep stops at `512` operands**, and that is a computational bound rather than a
  finding: the AST serialiser recurses once per tree level against an interpreter frame limit of
  `1000`. What was checked beyond the timed sweep's `128` is exactly the four lengths `192`, `256`,
  `384` and `512`, and the distinct-tree counts there are unchanged from `128`.
- **The conversion is one implementation.** Flatten-and-reshape is the canonical sound one; a
  rotation-based rewrite could differ by a constant factor. It could not differ asymptotically,
  because any sound conversion must be free to re-associate every unbracketed region and therefore
  must read the whole tree.
- **Generation 1 only.** Four binary operators, no unary minus, no exponentiation, no implicit
  multiplication. Experiment 0045's `121`-grammar registry is not covered, and neither is 0050's
  tiered syntax.
- **The metal half compiled `4` objects, not the corpus.** The selection rule is declared and applied
  mechanically, but `4` objects are `4` objects.
- **The `128`-operand and longer words are not mathematics.** Every figure that mixes them with the
  named laws is reported split, because the combined mean-depth ranking of the `25` worlds is entirely
  driven by them.

---

## Evidence classification

**OBSERVED** - produced by a recorded execution on the machine named above.

- The agreement grid: `11000` cells, `0` mismatches; the three negative controls at `1809`, `1516`
  and `498` mismatches.
- Language identity: `2750` acceptance and `250` rejection checks, `0` failures.
- The normalised sources: `24` strict machines byte-identical, `G0` apart, in both native variants;
  `1` source for all `25` in the control.
- Every timing figure, as a range: the noise floor, the rates, the paired ratios, the break-evens, the
  generation costs, the length curve, the parallel decision.
- Every structural count: distinct trees per entry, depths, peak live values, the Spearman
  correlations, the exhaustive enumeration over `237528` words, the long-word check to `512` operands.
- Every instruction count read out of `clang -S`.

**MODEL** - true of the model this project measures, which hardware does not implement literally.

- Operation count, critical-path depth and peak live values are a model of what a machine does. At
  `-O0` the arithmetic half of that model was confirmed exactly in `100` of `100` kernels; at `-O2` the
  operation-count half of it is **false**, and the report says where.
- The break-even is a linear model: one fixed cost, a constant per-parse gap, and executions spread
  evenly. Real workloads are not uniform across worlds, and the registry figure assumes they are.
- The Amdahl ceiling of `1.644` follows from the measured tokenizer share under the assumption that
  the tokenizer cost is unchanged by specialisation, which is true here because the tokenizer is
  literally the same function.

**STRUCTURAL** - follows from the shape of the objects and would hold on any machine.

- The T6 bound: a word with `s` distinct operators has at most `s!` readings among the `24` strict
  worlds, and at most `s! + 1` among all `25`. Its **tightness at `8` operators** is OBSERVED; the
  bound itself is structural.
- The operation multiset is world-invariant for a fixed token string, because a convention
  re-associates a fixed operator sequence and each token becomes exactly one node. Verified on `2750`
  cells, but it is a theorem, not a coincidence.
- No sound conversion can inherit the front end's associations, so it must read the whole tree and
  cannot beat a single native parse asymptotically.
- The `25` worlds describe the same string language, so no capability gap exists to measure - only
  cost and soundness.
- `G0`'s deeper readings on operator-cycling words follow from its tied levels turning same-level runs
  into left chains; the size of the effect is OBSERVED, the direction is structural.
