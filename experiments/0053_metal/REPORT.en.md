# ParseAtlas experiment 0053: the model against the metal

## How much of a representation choice survives the compiler, counted in instructions

This is the first question because if the answer were "none", nothing else in this card would matter.
It is not none. **The answer below is read out of clang's own assembly and has no stopwatch in it**,
and that is why it comes first: this card has an instruction-level half and a timing half, only the
first of them reproduces, and the second subsection here says so before anything else is read.

> **Over `16` objects and `34` equivalent writings, compiled four ways: the two writings of an object
> compile to the identical multiset of machine instructions in `3` of `16` objects at `-O0`, in `0`
> of `16` at `-O2`, in `0` of `16` at `-O2 -march=native -ffp-contract=fast`, and in `8` of `16` at
> `-O3 -ffast-math`. A representation difference survives ordinary optimisation in the machine code
> of every object in this corpus, and `-ffast-math` erases exactly half of them. There is no noise
> floor on that sentence — two multisets of mnemonics are equal or they are not.**

At `-O2`, where nothing collapses, the difference is not marginal. Counting the instructions clang
emits for each writing compiled as a standalone function, and the multiplies among them — scalar and
packed in separate columns, because the multiply count is `2` different numbers and they do not
always agree:

```text
object            writing          instructions   mulsd   mulpd
circle            center_radius               8       0       1
circle            general                    16       6       0
parabola          vertex                      5       2       0
parabola          standard                   15       2       2
binomial_square   factored                    3       1       0
binomial_square   expanded                    8       3       0
```

**The first revision of this table printed one column, headed `mulsd`, and called it "the scalar
multiplies".** The number came from `instruction_audit`'s `multiply` field, which matches
`v?mul[sp]d` and so counted `mulpd` and `vmulpd` beside `mulsd` and `vmulsd`. `2` of the `6` rows
were wrong under their own header: review recompiled `circle/center_radius` at `-O2` and got zero
`mulsd` and one `mulpd` against the printed `1`, and `parabola/standard` came back `2` scalar and
`2` packed against the printed `4`. The instruction counts `8`/`16`, `5`/`15` and `3`/`8` were
right, and the contrast the table draws is unchanged.

**What the mislabel was hiding is better than the table.** `center_radius` is not merely the shorter
writing of the circle, it is the one clang put in a vector register: its `8` instructions are
`unpcklpd`, `unpcklpd`, `subpd`, `mulpd`, `movapd`, `unpckhpd`, `addsd`, `retq`. Counted over the
whole corpus, a packed arithmetic instruction — a packed add, subtract, multiply or divide, as
opposed to the `movapd` and `unpcklpd` shuffling around them — appears in `8` of the `34` writings
at `-O2`, in `2` at `-O2 -march=native -ffp-contract=fast` and in `1` at `-O3 -ffast-math`, and in
none at all at `-O0`. **Ordinary `-O2` is where this corpus vectorises**, and the `2` rungs above it
vectorise less, because from `-march=native` upwards the only packed arithmetic left is a
`vdivpd` — in `difference_quotient/split` and `quotient_rule/split` at `-O2nativefma`, and in
`quotient_rule/split` alone at `-O3fast` — while the rest has been rewritten into scalar fused
multiply-adds.

The `8` writings at `-O2` are `circle/center_radius`, `difference_of_cubes/expanded`,
`difference_quotient/split`, `parabola/standard`, `product_chain_8/balanced`, `quotient_rule/split`,
`sum_chain_8/balanced` and `trapezoid_area/sum_of_halves`. They belong to `8` different objects:
clang vectorised one side of `8` pairs and never both sides of one, so vectorisation is itself a
representation difference that survives to the machine code. In only `2` of those `8` is the
vectorised writing also the shorter one — the circle's `center_radius` and the difference of cubes'
`expanded`; in the other `6` the vectorised writing carries MORE instructions than its partner, so
"the compiler could vectorise it" and "the compiler emitted less code for it" are not the same
property. Over the corpus at `-O2` the multiply column splits `66` scalar against `10` packed, and
`5` of the `34` writings carry a packed multiply specifically. All of these are counts read off the
assembly and carry no noise floor.

The `8` objects whose two writings become the same code at `-O3 -ffast-math` are
`binomial_square`, `difference_quotient`, `distributive_law`, `line`, `linear_approximation`,
`product_chain_8`, `sum_chain_8` and `trapezoid_area`. The `3` at `-O0` are
`perfect_square_trinomial`, `product_chain_8` and `sum_chain_8` — the objects whose two writings
already carry the same operation multiset in the same order, so there was never a difference for
`-O0` to preserve.

### The timing half of this card does not reproduce, and it is published as ranges

**The first revision of this report opened on a timing figure, and that figure did not come back.**
It said that at `-O0` and `-O2` the choice between two writings reaches the metal in `54` of the `64`
cells those two levels contribute, and in `16` of `16` at `-O2` in the throughput regime. Review
re-ran the experiment on a quiet machine with an independently written harness. Seven further
repeats were run here, on a machine measured quiet in the same runs:

```text
                                          first revision   review, 3 runs   here, 7 runs
O0 and O2 cells reaching the metal, of 64             54       46, 47, 49        49 - 51
O2 throughput, objects reaching, of 16                16          13 - 14        13 - 14
```

Ten independent readings of the first row span `46` to `51`, and `54` is in none of them. The
reporting run of the first revision was uniformly `12%` to `29%` slower than a quiet re-run, which is
contention on the machine rather than a property of the writings.

**So every timing count in this report is now a range over repeated runs.** `survival_repeatability`
re-runs the whole survival measurement — fresh compilation, fresh process, fresh timing — and reports
the smallest and largest count each `(level, regime)` cell produced. Over seven repeats on this
machine, **`0` of the `8` cells returned the same count every time.** No survival count here is a
resolvable quantity at this precision and none is presented as one; where a number below is a single
reading, it says so.

The sharpest single instance in the card *is* reproducible, in direction and in size, and it is the
third divergence probe. Sixteen terms added as a chain (`depth` `15`) against the same sixteen added
as a balanced tree (`depth` `4`), with the operation count held fixed at `15`, over `10` runs of
the whole probe set:

```text
level          dependent-chain regime, chained against balanced
O0             161.11% - 174.94%   the balanced writing is faster in every run
O2             160.83% - 169.53%   the balanced writing is faster in every run
O2nativefma    204.62% - 233.24%   the balanced writing is faster in every run
O3fast           0.01% -   2.15%   indistinguishable
```

A structural difference worth more than a factor of three at `-O2 -march=native -ffp-contract=fast`
is gone at `-O3 -ffast-math`, because `-ffast-math` lets the compiler reassociate the chain into the
tree. **The representation choice was real, the machine paid it, and one flag removed it.** Which
half of that sentence a reader cares about — that is exactly the choice this card refuses to make
for them.

## Purpose

The owner set this card on 2026-09-05:

> *"The point is to arrange the dataflow for the processor according to different representations so
> you can SEE which is more efficient. And formulas are good, but hardware often has hidden parts
> that do not match the formulas, and sometimes on real hardware a different representation becomes
> the profitable one."*

This project measures three structural quantities on the emitted tree — operation count
(`canonical.operation_cost`, card 0021), critical-path depth (`parallel_worlds.depth`, card 0041) and
peak live values (`memory_ceiling.peak_live`, card 0044). **They are a model, and hardware does not
implement that model literally.** This card measures where the model and the machine disagree, by
emitting C, compiling it and running it. All three measures are imported from the card that owns
them and none is re-implemented; the tests check that by identity rather than by equality.

## What is emitted, and what is timed

**The emitted form is a sequence of named temporaries, one operation per C statement, not one nested
expression.** Three reasons, and the third decides it:

- the correspondence to the model is auditable — one statement per internal tree node, so a reader
  counts the model's operations by counting lines instead of trusting a parenthesisation;
- the emitted order is the tree's own post-order, so the C source is a transcript of the dataflow
  graph rather than a string a C compiler's precedence would have to re-parse into a tree;
- clang's default in C is `-ffp-contract=on`, which fuses a multiply and an add only within one
  statement. One operation per statement therefore leaves fusion off by default, and
  `-ffp-contract=fast` is the flag that permits it across statements. Fusion becomes a declared axis
  of the experiment instead of an accident of how the expression was written out — though that flag
  turns out to be inert on its own, for the reason measured under the optimisation ladder below.

Two regimes are timed, because the model makes two different predictions and one loop cannot test
both:

- **throughput** — four independent copies of the expression per loop step, four accumulators, every
  input read from a table indexed by the loop counter. Successive steps are independent, so what
  binds is how many operations are issued. This is the regime operation count should predict.
- **latency** — one accumulator, and the previous step's result folded back into one input through
  `acc * 1e-18`. Successive steps cannot overlap, so what binds is the longest chain of dependent
  operations. This is the regime depth should predict.

**The feedback goes into one input and not into all of them, and the reason is a defect this card
found in its own first harness.** With the same perturbation added to every input, a subtraction of
two variables cancels it exactly — `(x + fb) - (h + fb)` is `x - h` — and at `-ffast-math` clang
performs that cancellation, after which nothing in the loop depends on the accumulator and the
compiler deletes the loop. It did: the circle's centre-radius writing timed at `0.00` seconds per
step at `O3fast` before the harness was changed. The fixed harness feeds the variable leaf furthest
from the root, and an audit confirms that leaf sits at the tree's full depth for all `42` writings
compiled by this card, so the chain timed is the chain the model names.

**How the optimiser is prevented from deleting the work**, because a benchmark that measures an
empty loop is the classic failure here:

- every input is read from a table indexed by the loop counter, so no part of the expression is
  loop-invariant and none of it can be hoisted out;
- every loop step's result is accumulated;
- the accumulator is written through a caller-owned pointer, added into a checksum, stored into a
  `volatile double` and printed, so it is observable behaviour the C standard forbids the compiler
  to discard.

That guard is measured and not asserted. Compiling the same `34` kernels a second time with the
accumulator dropped gives, for every one of them, a timed block of `0.0` nanoseconds per step against
`0.3601` to `1.3699` nanoseconds per step with the guard — a ratio of `0.000000`. The loop is not
merely faster without the guard; it is gone. A second alarm refuses to rank any run in which a timed
block came back shorter than `10` timer ticks.

## The optimisation ladder

Four rungs, each a controlled variable, and the fusion counts are read out of the assembly of the
code that was actually timed rather than assumed:

```text
level          flags                                  fused multiply-adds in the timed loops
                                                      throughput      latency
O0             -O0                                             0            0
O2             -O2                                             0            0
O2nativefma    -O2 -march=native -ffp-contract=fast           191          250
O3fast         -O3 -march=native -ffast-math                  360          235
```

Packed (vector) instructions in the same loops: `0`, `1072`, `1083`, `2899` in the throughput regime
and `0`, `152`, `95`, `100` in the latency regime. Division instructions: `36`, `24`, `30`, `45` and
`9`, `15`, `19`, `19`.

### The third rung varies two things, and it cannot be made to vary one

**The first revision of this card called that rung `O2fma`, and the module said in its own
docstring that "The ONLY difference from `O2` is fusion". That was false, and review caught it.** The rung
carries `-march=native` as well, and which of the two flags did the work had never been measured. It
is renamed `O2nativefma` here, and each flag is now compiled on its own and counted in the timed
loops:

```text
flags                                  kernels changed from -O2    FMAs    VEX   packed
-O2                                                    0 of 34        0      0     1072
-O2 -ffp-contract=fast                                 0 of 34        0      0     1072
-O2 -march=native                                     34 of 34        0   1542     1246
-O2 -march=native -ffp-contract=fast                  34 of 34      191   1385     1083
-O2 -mfma                                             34 of 34        0   1015      747
-O2 -mfma -ffp-contract=fast                          34 of 34      107    927      658
```

> **The fusion flag on its own changes nothing at all** — all `34` timed kernels keep the `-O2`
> instruction multiset and not one fused multiply-add appears. **The ISA flag on its own fuses
> nothing** — all `34` kernels change, `1542` VEX-encoded instructions appear and the packed count
> moves from `1072` to `1246`, still with `0` FMAs. Only both together fuse.

**And the rung cannot be split into two, which is measured rather than argued.** `-mfma` is the
narrowest switch that makes an FMA instruction reachable at all, and it already rewrites all `34`
kernels by itself while still emitting `0` FMAs, because it also switches the encoding to VEX. No
flag adds fusion and changes nothing else, so this rung is reported as what it is — an ISA change and
a fusion change together — rather than as a difference the compiler does not offer.

**Every attribution this card makes to "fusion" at this rung is therefore an attribution to the two
flags together**, and both are named wherever the attribution matters.

## Corpus

Hand-chosen, and the hand is declared. `16` objects in `34` equivalent writings. Fourteen objects
take both writings verbatim from the project's own named-law corpus — 0037's laws as 0038 carries
them — so the ranking measured here is a ranking of writings the project already publishes. Two of
those get a third writing added by this card, a Horner form in each case, because the divergences the
card names are about shapes the corpus does not happen to contain. The last two objects are pure
association chains, where the operation count is held fixed and only the shape moves.

Equivalence is checked and not claimed: SymPy confirms that every writing of every object simplifies
to the same expression, and every emitted function is checked against the project's evaluator before
any timing is believed.

The four divergence probes are a separate, constructed set of `4` pairs, each holding fixed what it
claims to hold fixed:

```text
probe               writings                    ops  depth  peak  width  div  fma sites
probe_division      separate                      3      2     3      2    2          0
                    common_denominator            5      3     3      3    1          2
probe_fma           factored                     31      5     6     16    0          8
                    expanded                     31      5     6     16    0         16
probe_latency       chained                      15     15     2      1    0          0
                    balanced                     15      4     5      8    0          0
probe_registers     low_peak                     39      9     3      9    0          0
                    high_peak                    39      9     6     17    0          0
```

`width` is this card's own as-soon-as-possible schedule width — the largest number of operations
ready to issue at one step. It is not a project measure; it is here only to say what an inversion the
four declared divergences cannot explain is made of.

## Observed results

Environment, and every number below belongs to it: `Windows-11-10.0.26200-SP0`, `AMD64`,
`Intel64 Family 6 Model 167 Stepping 1, GenuineIntel`, `16` logical cores, Python `3.14.3`,
`clang version 21.1.0`, target `x86_64-pc-windows-msvc`. The wall clock is
`QueryPerformanceCounter` at `10` MHz, so one tick is `100` nanoseconds. Each timed process pins
itself to logical core `2` and raises itself to `HIGH_PRIORITY_CLASS`; without that the observed
p10-p90 band on this machine reached `132%`.

**How quiet the machine was, stated because every timing number depends on it.** Every timing run in
this revision was taken sequentially, one process at a time, with no other job of this card running
and the operating system reporting `2%` to `5%` processor load before and after. Quietness is also
measured from inside the harness, which is the figure that matters: each run carries one
byte-identical duplicate per object, and over the seven survival repeats the median gap between two
copies of the same code was `0.751%` and the worst was `14.398%`. **That worst figure is larger than
several of the effects this report ranks, and it is the reason the timing half is given as
intervals.**

### 1. Correctness, before any timing

Every emitted function this card compiles — the `34` corpus writings and the `8` probe writings —
against the exact-rational oracle, on `8` declared input rows, at all four levels: `336` checks per
level, `1344` in all, `0` failures. The largest relative deviation observed anywhere is `2.5975e-15`,
against a declared tolerance of `1e-09` — six orders of magnitude of margin. The oracle uses
`Fraction` throughout and rounds nothing, so the whole of that deviation is the machine's
floating-point rounding and none of it is the oracle's.

**And this audit can fail, which the first revision never demonstrated.** The test named for that job
built a *correct* writing and asserted the audit passed; on an isolated copy, breaking the audit two
different ways left all `65` of its tests green. The control now replaces the emitter with one that
writes `b - a` where the writing says `a - b`, and requires the audit to report `all_match is False`
with a non-empty failure list naming the kernel — through exactly the path this paragraph's `0`
failures come from. A second control makes the audit fail and requires the report to raise before any
benchmark starts. See **Validation**.

### 2. The repetition sweep, and the noise floor

The repetition count is swept rather than declared. Over `4096` to `4194304` loop steps per timed
block, at `41` blocks per kernel:

```text
loop steps   ns per step   block (ms)   ticks   p10-p90 band, median   p10-p90 band, max
      4096        0.5615       0.0023      23                 39.88%              55.56%
     16384        0.5219       0.0086      86                 34.28%              72.29%
     65536        0.4066       0.0266     266                 49.30%              74.46%
    262144        0.4118       0.1079    1080                 14.92%              62.42%
   1048576        0.4302       0.4511    4511                 27.03%              52.34%
   4194304        0.4371       1.8332   18332                 40.00%              84.60%
```

Consecutive drift in the seconds-per-step figure for that run: `7.07%`, `22.08%`, `1.27%`, `4.47%`,
`1.59%`.

**The drift is the noisiest quantity in this report, it is published rather than asserted, and that
is a correction.** `2` earlier revisions built a test on it. The first asserted that the curve
flattens monotonically, which it does not. The second replaced that with a threshold: the minimum of
the `3` drifts at or past `262144` had to fall below `8%`, a number chosen just past the largest
value `17` sweeps had produced. Review ran the card file `5` times and watched that test fail in `1` of
them, at `8.53%` against the declared `8%` — on the run that was the second-fastest of the `5`, so
the failure was not contention.

**The figures were not wrong; the inference from them was.** The manager re-derived the same
statistic over `12` sweeps and got a worst of `2.61%` and a median of `0.25%`, which agrees with what
was declared. Re-measured here over `48` sweeps, in a window in which `2` other cards were compiling
on the same machine, the same statistic ranges from `0.06%` to `11.43%` with a median of `1.82%`; it
exceeds the previously declared worst of `2.82%` in `17` of the `48` and crosses `8%` in `3` of them.
Individual drifts inside a sweep ranged from `0.00%` to `73.13%` with a median of `5.56%`, and `2` of
the `48` carried an intermediate drift above `50%`.

**The rule this produced, and it generalises past this card: do not gate on a statistic you cannot
bound — publish it with its spread.** A margin computed from a sample maximum is not a margin, and
enlarging the sample does not turn one into a bound; it only postpones the failure. The threshold is
deleted rather than raised, the numbers above are the finding, and the test now asserts only what is
deterministic about the choice: that `262144` is a point on the swept curve, that it is not the last
point, and that the timed block grows with the repetition count. That last one is a monotone
relationship in the INPUT rather than in the noise — the step count quadruples between consecutive
points — and it held in `48` of `48` sweeps, with the block growing by a factor of `551` to `1191`
end to end against the `1024` the step counts alone would give.

The timer stops binding at `262144`, where a block is `1080` ticks; longer blocks buy nothing and
lose to interference, so `262144` is the point read off the curve. At the short end the block is at the
timer's own resolution — the sweep's first point has come back as low as `9` ticks — which is why the
count is not read from there.

**The noise floor is measured, not assumed.** Every reported run carries, for each object, a second
copy of one of its writings compiled from byte-identical C, so any difference between the two is
noise by construction. Over `128` such pairs in the reporting run:

```text
median   0.242%
p90      1.298%
p95      2.062%
maximum 14.867%
```

That is one run. Over the seven survival repeats of section `5`, which carry the same duplicates, the
median identical-kernel gap was `0.751%` and the worst was `14.398%` — so the shape is stable even
though the individual figures are not.

The declared floor is the p95, `2.062%`, and not the maximum. The distribution is strongly skewed,
and one run taken while three other jobs were compiling on the same box produced a single gap of
`19.04%`; re-running that same level and regime three times with the machine quiet gave maxima of
`1.17%`, `2.39%` and `1.75%`. Taking the maximum would let one preempted block set the resolution of
the entire experiment. Nothing here rests on that choice: the floor is swept from `0` to `20%` and
the curve is published in section `7`.

### 3. The harness floor

A kernel with no arithmetic at all — it loads one value and accumulates it — gives the loop's own
cost. Measured at every level, over balanced sums of `1`, `2`, `4`, `8`, `16` and `32` leaves:

This is a timing measurement, so it is given as a range over three readings and not as one number:

```text
level          throughput, zero-operation kernel   latency, zero-operation kernel
O0                        1.0262 ns - 1.7952 ns             5.1300 ns - 5.6671 ns
O2                        0.2563 ns - 0.2567 ns             1.8616 ns - 2.0008 ns
O2nativefma               0.2331 ns - 0.3231 ns             0.9094 ns - 0.9529 ns
O3fast                    0.2178 ns - 0.2277 ns             0.9094 ns - 0.9117 ns
```

At `O2` a least-squares line through the six points gives an intercept of `0.1536` to `0.1553`
nanoseconds and a slope of `0.0604` to `0.0610` nanoseconds per operation in the throughput regime,
and an intercept of `1.8048` to `1.9090` nanoseconds and a slope of `1.0410` to `1.1327` nanoseconds
per depth level in the latency regime. The latency line is fitted against depth and not against
operation count, because these are balanced sums whose depth grows as the logarithm of their
operation count; fitting the wrong variable would make the slope meaningless.

**At `O3fast` the latency fit is not quoted as a cost at all, and the reason is a result.**
`-ffast-math` reassociates a balanced sum, so its executed depth is not its tree depth, and the
least-squares line comes back with a **negative** intercept — `-3.6215` to `-3.5302` nanoseconds over
three readings, so the sign is not an artefact of one run. A fit that cannot even be positive is the
clearest single sign that the model's depth has stopped describing what the machine runs at that
level.

The overhead is added to every writing of an object equally, so it cannot change which writing is
faster, but it compresses every relative gap in this report. Every gap here is a lower bound on the
gap between the two dataflow graphs themselves.

### 4. What survives the compiler, counted in instructions

An instruction count is not noisy. Each writing is compiled as a standalone function, the assembly is
read back, and two writings of one object that compile to the same multiset of mnemonics have had
their difference erased:

```text
level         objects whose writings compile to identical instructions
O0                 3 of 16
O2                 0 of 16
O2nativefma        0 of 16
O3fast             8 of 16
```

The eight at `O3fast` are `binomial_square`, `difference_quotient`, `distributive_law`, `line`,
`linear_approximation`, `product_chain_8`, `sum_chain_8` and `trapezoid_area`. The three at `O0` are
`perfect_square_trinomial`, `product_chain_8` and `sum_chain_8` — the objects whose two writings
already have the same operation multiset in the same order.

The same assembly answers a second question with no noise floor in it: how many writings the
compiler put in a vector register, and how the multiply count splits between scalar and packed
forms. A writing counts as vectorised when it carries at least one packed arithmetic instruction —
a packed add, subtract, multiply or divide — as opposed to the packed data movement that surrounds
them:

```text
level          writings vectorised, of 34   scalar multiplies   packed multiplies
O0                                      0                  93                   0
O2                                      8                  66                  10
O2nativefma                             2                  54                   0
O3fast                                  1                  46                   0
```

**Ordinary `-O2` is the rung that vectorises this corpus**, and the `2` rungs above it vectorise
less rather than more: from `-march=native` upwards the only packed arithmetic that survives is a
`vdivpd`, in `2` writings at `-O2nativefma` and in `1` at `-O3fast`, and everything else has been
rewritten into scalar fused multiply-adds. The opening section names the `8` writings and notes that they belong to `8`
different objects — one side of `8` pairs and never both sides of one.

**This is the half of the card that reproduces, and it reproduced exactly.** Review re-derived this
table on a different machine state with an independently written harness and obtained the same four
counts, the same eight objects named at `O3fast` and the same three at `O0`. There is no floor, no
median and no repeat count involved: the comparison is equality of two multisets of mnemonics. Every
figure in sections `5`, `6`, `7`, `8`, `9` and `10` below is a timing figure and carries the caveat
the opening states; every figure in this section and in the optimisation ladder does not.

### 5. What survives the compiler, counted in time — and this half is a range

**This is the half that does not reproduce**, and it is reported the way the opening says it must be.
The whole survival measurement was run seven times over — fresh compilation, fresh process, fresh
timing, sequentially and with nothing else running — and what is published is the smallest and the
largest value each cell produced. It is read at the floor the first revision declared, `2.062%`, so
that the new counts and the old ones answer the same question rather than two different ones:

```text
regime       level          collapsed of 16   median spread      first revision
throughput   O0                       2 - 4   16.90% - 21.57%    1/16 at 21.97%
throughput   O2                       2 - 3   40.05% - 40.88%    0/16 at 33.04%
throughput   O2nativefma            10 - 11    0.00% -  0.27%    6/16 at  5.28%
throughput   O3fast                   5 - 7   47.52% - 53.34%    7/16 at 53.50%
latency      O0                       4 - 6   16.79% - 18.93%    5/16 at 16.69%
latency      O2                       3 - 4   19.55% - 22.71%    4/16 at 20.15%
latency      O2nativefma              2 - 3   58.69% - 62.26%    3/16 at 58.72%
latency      O3fast                   2 - 5   23.67% - 26.44%    5/16 at 24.98%
```

**`0` of the `8` cells returned the same count in all seven runs.** Three of the eight counts the
first revision published fall outside the range measured here — `O0` and `O2` and `O2nativefma`, all
three in the throughput regime — as do five of its eight median spreads. No cell in this table is a
resolvable number on this machine, and every one of them is given as an interval.

**How quiet the machine was is measured in the same runs rather than asserted.** Every run carries one
byte-identical duplicate per object, so the gap between two copies of the same code is noise by
construction. Over the `112` such pairs in the seven repeats the median gap was `0.751%` and the
worst was `14.398%`. A run in which two identical kernels differ by that much cannot resolve a
five-percent effect, and that is the honest reason these counts move.

`O3fast` in the throughput regime remains bimodal: `5` to `7` of `16` objects collapse entirely while
the median spread over all `16` stays near `50%`, because the objects that do not collapse separate by
more than the objects at `O2` did. The compiler does not shrink every difference; it removes some
outright and enlarges others.

#### The `O2nativefma` throughput cell was wrong, and stably so

This is the cell review singled out, and re-measurement confirms it was not noise. The first revision
published `6` of `16` objects collapsed at a median spread of `5.28%`. Review's two dedicated runs at
the same floor gave `10` of `16` twice, at spreads of `1.023%` and `1.329%`. Seven repeats here give
`10`, `11`, `11`, `11`, `11`, `11` and `11` collapsed, at median spreads between `0.000%` and
`0.274%`.

The timer is not manufacturing that. At this rung and in this regime the timed blocks run `547` to
`2197` ticks, so quantisation at the median block is `0.183%` — an order of magnitude below the
effects being called collapsed. What the tick counts show instead is a floor:

```text
object                     writings, median block in timer ticks
distributive_law           547, 548
binomial_square            548, 548
difference_of_squares      547, 547
difference_of_cubes        548, 548
quadratic                  548, 557, 547
calibration_quadratic      547, 547, 547
perfect_square_trinomial   547, 547
line                       548, 547
circle                     548, 662
parabola                   547, 625
trapezoid_area             547, 547
difference_quotient        1094, 2186
quotient_rule              1094, 2197
linear_approximation       548, 547
sum_chain_8                870, 821
product_chain_8            820, 821
```

Nine objects have **both** their writings at `547` or `548` ticks, which is the harness's own
zero-arithmetic kernel cost at this level and in this regime — `0.2087` nanoseconds per step, a single
reading. Two more collapse at a higher common level. The five that separate are `circle`, `parabola`,
`sum_chain_8` and, by far the widest, the two objects that contain a division.

> **At `-O2 -march=native -ffp-contract=fast` in the throughput regime the arithmetic of eleven of the
> sixteen objects has become free relative to the loop that carries it. What still separates two
> writings there is division.**

### 6. The agreement table

`16` objects times `4` levels times `2` regimes is `128` object cells, each read against three model
axes. A pair of writings is an inversion when the model orders it strictly one way and the machine
orders it strictly the other way by more than the floor. A pair the model orders strictly and the
machine cannot separate is unresolved, never counted as agreement.

**The inversion count is a timing figure and it does not reproduce either.** The whole agreement
table was run three times at the floor the first revision published, `2.062%`. Against the axis each
regime is supposed to answer to — `operations` in throughput, `depth` in latency — the disagreement
count came back as `3`, `2` and `4`, where the first revision published `2` as a single reading.
Crossing every model axis against every regime gives `35`, `34` and `39` inversions in all, against
the `38` published. Per axis, over the same three runs:

```text
axis          inversions, three runs   first revision
operations                 6,  6,  8                6
depth                      5,  2,  3                2
peak_live                 24, 26, 28               30
```

> **Roughly three quarters of all inversions are on the `peak_live` axis in every run — `24` of `35`,
> `26` of `34` and `28` of `39`. The model's memory axis is the one the machine orders backwards, and
> it does so at every level including `-O0`.** That proportion is the robust statement; the exact
> counts are not, and the first revision's `30` of `38` was one draw from this distribution rather
> than a measurement of it.

The two cells the extra inversions appear in are small ones — `2.25%`, `2.38%` and `4.82%`, all just
above the `2.062%` floor — while the two named in section `8` clear `96%` in every run. The count is
unstable at the bottom of the table and not at the top, which is why the tests pin it at a floor of
`0.20` rather than at the measured one: at that resolution the small cells fall away and the count is
`2` in every run.

### 7. The floor sweep

No count in section `6` is read from one threshold. Re-reading the same timings at floors from `0` to
`20%`:

```text
floor      inversions   unresolved   concordant   collapsed object cells
 0.000%             8            3           85                   3/128
 0.250%             5            8           83                   7/128
 0.500%             4           11           81                  13/128
 1.000%             2           15           79                  25/128
 2.000%             2           17           77                  31/128
 2.062%             2           17           77                  31/128
 3.000%             2           19           75                  35/128
 5.000%             2           20           74                  40/128
10.000%             2           23           71                  50/128
20.000%             2           35           59                  62/128
```

**The sweep above is one run**, and it is kept because the shape of the curve is what it is for, not
the individual counts. The inversion count is `2` from `1%` upward and `8` at a floor of zero; the six
that vanish between `0%` and `1%` are pairs the machine separated by less than the noise between two
identical kernels, and they are not results. Three fresh runs of the whole agreement table at the
`2.062%` floor gave `3`, `2` and `4`, so the count at that resolution is not stable — see section
`6`. At a floor of `20%` it was `2` in all three, which is why that is the floor the tests pin at.

### 8. The two inversions, named — and these two do reproduce

Where the *count* of inversions moves between runs, these two particular cells do not. They appeared
in all three runs of the agreement table, in the same direction, and review reproduced both
independently. The gaps are given as ranges over three runs:

```text
O3fast, throughput, difference_of_cubes
    model prefers    a * a * a - b * b * b                        5 operations
    machine prefers  (a - b) * (a * a + a * b + b * b)            7 operations
    the machine is faster by 99.32% - 104.01%

O3fast, latency, parabola
    model prefers    a * (x - h) * (x - h) + k                    depth 4
    machine prefers  a * x * x - 2 * a * h * x + a * h * h + k    depth 6
    the machine is faster by 98.94% - 103.15%
```

Both are consistent with fusion, and the assembly says more than the stopwatch does. The timed loop
of the factored difference of cubes holds `253` instructions with `26` fused multiply-adds and `141`
packed instructions, against `210` instructions with `2` fused multiply-adds and `129` packed for the
expanded one. **The winner has more instructions**; what it has is more of the work fused and
vectorised, and those counts are read from the assembly and carry no noise floor.

The timings put the factored form at `0.2090` to `0.2232` nanoseconds per step and the expanded form
at `0.4265` to `0.4448`. The harness's own zero-arithmetic kernel at this level and in this regime
costs `0.2178` to `0.2277`, so **the factored writing is running at the floor of what this harness can
time at all** and the size of its arithmetic is not resolvable here — only the fact that the expanded
form costs about another `0.21` nanoseconds on top of the same floor.

The parabola is the cleaner of the two, because neither writing is at the floor. In the
dependent-chain regime at `O3fast` the standard form runs at `1.7315` to `1.7578` nanoseconds per step
and the vertex form at `3.4447` to `3.5671`, while the zero-operation kernel costs `0.9094` to
`0.9117`. Net of the harness the two chains cost about `0.83` and `2.60` nanoseconds — **a factor of
about three in the dependent chain, in the direction opposite to the model's ordering by depth.** At
`-ffast-math` the compiler factors the fed variable out of three terms, so the chain the model
measures as depth `6` is not the chain the machine executes. The model prefers the vertex form on an
axis the compiler stopped honouring.

### 9. The four divergence probes: prediction first, then observation

The prediction for each of the `32` cells was written before any of these numbers existed and is
pinned by a test separately from what the machine did. **The probe set was run `5` times over**, and
the table gives, per cell, how many of those runs the prediction survived and the range the gap
covered. Predictions held in `19`, `18`, `17`, `18` and `17` of `32` cells — so between `13` and `15`
of the `32` failed, and the first revision's "`16` of `32` held" was one draw from that. `none` below
means "indistinguishable at the `2.062%` floor"; a slash means the cell answered differently in
different runs.

```text
probe             regime       level          predicted     observed             held   gap range
probe_division    throughput   O0             common_den    separate             0/5     30.53% -  36.81%
probe_division    throughput   O2             common_den    common_den           5/5     59.57% - 100.08%
probe_division    throughput   O2nativefma    common_den    common_den           5/5     99.92% - 100.66%
probe_division    throughput   O3fast         common_den    common_den           5/5     99.91% - 100.17%
probe_division    latency      O0             separate      separate             5/5     14.94% -  18.70%
probe_division    latency      O2             separate      separate             5/5      5.07% -   6.81%
probe_division    latency      O2nativefma    separate      separate             5/5      6.64% -  11.63%
probe_division    latency      O3fast         separate      common_den / none    0/5      0.02% -   2.13%
probe_fma         throughput   O0             none          none                 5/5      0.25% -   1.72%
probe_fma         throughput   O2             none          expanded / none      4/5      0.26% -  10.56%
probe_fma         throughput   O2nativefma    expanded      expanded             5/5      6.57% -  10.59%
probe_fma         throughput   O3fast         expanded      factored             0/5     10.91% -  13.45%
probe_fma         latency      O0             none          none                 5/5      0.34% -   0.94%
probe_fma         latency      O2             none          expanded / none      1/5      1.24% -   5.84%
probe_fma         latency      O2nativefma    none          expanded             0/5      4.75% -   7.21%
probe_fma         latency      O3fast         none          expanded             0/5     12.97% -  15.37%
probe_latency     throughput   O0             none          balanced             0/5     30.62% -  32.32%
probe_latency     throughput   O2             none          balanced             0/5     23.85% -  33.11%
probe_latency     throughput   O2nativefma    none          balanced             0/5     19.02% -  25.36%
probe_latency     throughput   O3fast         none          chained / none       4/5      0.07% -   2.09%
probe_latency     latency      O0             balanced      balanced             5/5    161.11% - 168.85%
probe_latency     latency      O2             balanced      balanced             5/5    160.83% - 165.83%
probe_latency     latency      O2nativefma    balanced      balanced             5/5    206.29% - 233.24%
probe_latency     latency      O3fast         none          chained / none       4/5      0.01% -   2.15%
probe_registers   throughput   O0             none          high_peak            0/5     12.80% -  14.44%
probe_registers   throughput   O2             none          high_peak / none     2/5      1.26% -   2.80%
probe_registers   throughput   O2nativefma    none          high_peak            0/5      4.43% -   6.37%
probe_registers   throughput   O3fast         none          none                 5/5      0.21% -   1.43%
probe_registers   latency      O0             none          high_peak            0/5     14.57% -  16.34%
probe_registers   latency      O2             none          high_peak            0/5      4.62% -   8.71%
probe_registers   latency      O2nativefma    none          high_peak / none     4/5      0.22% -   5.06%
probe_registers   latency      O3fast         none          none                 5/5      0.11% -   1.56%
```

**Divergence 1, a division is not an operation like the others: confirmed, and it is larger than the
first revision published.** The model counts `3` operations for `a / d + b / e` and `5` for
`(a * e + b * d) / (d * e)`, so it prefers the first. The first revision reported the throughput gap
at `O2` as `53.16%`; review measured `99.91%` and `100.09%`, and five runs here give `59.57%` to
`100.08%`, with a second five-run study returning `99.82%` to `106.02%` at a median of exactly
`100.00%`. At `O2nativefma` the range is `99.92%` to `100.66%` and at `O3fast` `99.91%` to `100.17%`.

> **The machine takes about half the time for the writing the model charges five operations for
> against three.** One division instead of two, at the price of three multiplications the model
> charges for and the hardware barely notices. **The project's operation count orders these two
> writings backwards, by a factor of two.**

The prediction failed at `O0` alone, where nothing is optimised and every value goes through memory,
and it reverses in the dependent-chain regime exactly as predicted, because the common denominator
puts a multiply and an add in front of its division.

A tree cannot share a subexpression, so the reciprocal trick — `1/d` computed once and multiplied —
is not expressible in this project's representation at all. The common denominator is the only way a
tree can trade a division for multiplications, and it is the schoolbook move.

**Divergence 2, fused multiply-add: the effect is real and the stated cause is wrong.** The pair is
`8` differences of squares summed, factored against expanded, identical on all three model axes and
on schedule width, differing only in that a difference of squares is a multiply-add site and a
product of a sum and a difference is not. The expanded form does win at `O2nativefma` in the
throughput regime by `6.57%` to `10.59%`, as predicted. But it also wins in the *dependent-chain*
regime at `O2`, at `O2nativefma` and at `O3fast`, where the prediction was that fusion buys an issue
slot and not a level of the critical path — and the `O2` timed loops contain `0` fused multiply-adds,
so fusion cannot be the reason there. At `O3fast` in the throughput regime the order reverses
outright and the factored form wins by `10.91%` to `13.45%`. **Fusion changes the machine's answer,
but not in the direction or at the levels this card predicted, and the `O2` result rules out the
simple explanation.**

**Divergence 3, latency against throughput: depth is real, and the throughput regime does not hide it
as designed.** In the dependent-chain regime a depth of `15` against a depth of `4` at equal operation
count costs `161.11%` to `168.85%`, `160.83%` to `165.83%` and `206.29%` to `233.24%` at the first
three levels, with the balanced writing faster in all five runs at each — the model's depth axis is
vindicated, decisively, and this is the most reproducible effect in the card. But the throughput
regime, which was predicted to see nothing, also prefers the balanced writing in every run, by
`30.62%` to `32.32%`, `23.85%` to `33.11%` and `19.02%` to `25.36%`. Four independent copies of the
expression per loop step are not enough independence to hide a chain of `15` dependent additions.
**That is a limitation of the harness, and it is also the answer: on this machine a deep graph costs
something even where the work is nominally independent.**

**Divergence 4, register renaming against peak live: confirmed as a null, and the axis points the
wrong way.** The pair holds the operation count at `39` and the depth at `9` and moves `peak_live`
from `3` to `6`. Nothing decisive appears anywhere: the largest gap over all `8` cells is `16.34%`
over the `5` runs of the table above and `20.94%` over the `30`-run study reported in section `10`,
against `233.24%` for the depth probe. Where a gap does clear the floor, **the writing with the
larger peak live is **usually** the faster one — `30` of `30` runs for `latency/O0` and for
`latency/O2`, and `29` of `30` for `throughput/O0`, whose single flip came on a run where its gap
was `0.83%`. That is the opposite of the direction 0044 and 0049 give the axis. **The direction is
published here and asserted nowhere**, and the reason is that this report claimed it as a bound and
was wrong: review saw `latency/O2` resolve the other way, in `1` of `5` runs of this card's test
file. A `12`-run re-measurement of the probe **standalone** then returned `12` of `12` in the
published direction for all `3` cells — including the `throughput/O0` cell this report had singled
out for flipping. So the standalone evidence does not describe the environment the assertion ran in
and does not even separate the cells it was used to select. The reason is visible in this card's own extra measure: at equal operations
and equal depth the higher-peak shape has a schedule width of `17` against `9`, so it offers nearly
twice as many operations ready to issue at its busiest step. Minimising `peak_live` at these
magnitudes is not free; it is mildly harmful.

### 10. Repeatability: which cells have a measured order at all

The probe set was run `5` times over, end to end, and the smallest and largest gap each cell produced
was recorded. **`25` of the `32` cells returned the same observation in all five runs; `7` did not.**
A second five-run study, scored on direction alone and ignoring the floor, put `24` of `32` in
agreement. The widest range a single cell covered is `40.51` percentage points — `probe_division` in
the throughput regime at `O2`, from `59.57%` to `100.08%`.

The intervals also overlap: `probe_division` in the throughput regime at `O0` covered `30.53%` to
`36.81%` while `probe_latency` in the same regime at `O2` covered `23.85%` to `33.11%`, so **no single
threshold between `1%` and `100%` classifies all `32` cells the same way twice on this machine.** That
is why the report gives each probe cell its gap range rather than only its verdict, and why the tests
pin the reproducible cells by direction and size and leave the rest unpinned.

**A larger study was run for this revision, and it widened everything.** While the tests were being
repaired the probe set was run `30` more times — `14` in one batch and `16` in another, on a machine
that was also compiling `2` other cards — and the measured noise floor over those runs covered `1.25%`
to `8.15%` at a median of `2.55%`. The cells the tests read are:

```text
probe             regime       level          gap range over 30 runs
probe_division    throughput   O0              18.48% -  45.76%
probe_division    throughput   O2              53.66% - 109.41%
probe_division    throughput   O2nativefma     94.33% - 104.47%
probe_division    throughput   O3fast          95.09% - 111.89%
probe_latency     latency      O0             124.63% - 171.15%
probe_latency     latency      O2             150.19% - 172.80%
probe_latency     latency      O2nativefma    213.75% - 233.60%
probe_latency     latency      O3fast           0.09% -   4.05%
probe_registers   throughput   O0               0.83% -  16.84%
probe_registers   latency      O0               9.75% -  20.94%
probe_registers   latency      O2               0.89% -  10.78%
```

**That table says the same thing the five-run one did, only louder: the floor cannot be a constant.**
The largest gap the division probe reached in the throughput regime is `111.89%` and the smallest the
deep-chain latency probe reached at `O0` is `124.63%`, so the `130%` floor this report reads its
measured table at sits INSIDE the deep-chain cell's range: that cell resolved in `25` of the `30`
runs and did not in `5`. Any floor placed between the two populations carries a margin of about
`1.06` times, which is not a margin at all. The card's response is in the Validation section: that
one cell is no longer pinned to a classification, its size is compared with the noise floor measured
in the same run — a ratio that never fell below `15.29` — and the other `31` cells stay pinned.

### 11. The peak-live bound

Swept rather than assumed, over `8` leaf counts, taking at each the depth with the largest
constructible spread in `peak_live` at a fixed operation count:

```text
leaves   operations   depth   peak_live range   spread   max peak_live at any depth   log2 bound
     8            7       3              4..4        0                            4            4
    12           11       5              3..4        1                            4            4
    16           15       5              3..4        1                            5            5
    20           19       6              3..5        2                            5            5
    24           23       7              3..5        2                            5            5
    32           31       8              3..5        2                            6            6
    40           39       9              3..6        3                            6            6
    48           47      10              3..6        3                            6            6
```

The largest `peak_live` any tree of `n` leaves can have is `floor(log2(n)) + 1`, and the sweep
confirms the bound is tight at every point. This instruction set has `16` architectural `xmm`
registers, so **a straight-line expression would need `65536` leaves before `peak_live` could ask for
more registers than the machine has.** The fourth axis cannot bind on any expression a person would
write, and the probe's null result is not an accident of this corpus.

## Interpretation

- **A representation difference survives `-O2` in the machine code, and this is the part of the card
  that reproduces.** `0` of `16` objects compile their two writings to the same instructions at `-O2`;
  `8` of `16` do at `-O3 -ffast-math`. That is an exact statement with no floor and no repeat count in
  it, and it was re-derived independently. Everything below is a timing statement and softer.
- **The project's operation count orders two writings backwards whenever divisions differ.** This is
  the card's strongest positive timing result and it is a factor of two, not a rounding error, holding
  in `5` of `5` runs at three of the four levels. Any ranking in 0034, 0037, 0042, 0044 or 0049 that
  compares writings differing in division count is measuring something the hardware does not charge
  for in the way the count assumes.
- **The `peak_live` axis is the one to distrust.** Roughly three quarters of all inversions are on it
  in every run — `24` of `35`, `26` of `34`, `28` of `39` — at every optimisation level, and the
  designed probe shows the direction is wrong at equal operations and equal depth. The axis is a real
  property of a tree and a real bound on register demand, but on this machine, at the magnitudes any
  expression reaches, it does not predict speed and its sign is not reliably the one the frontier
  gives it.
- **The `depth` axis survives contact with the metal better than any other.** Between `2` and `5`
  inversions are on it against the `24` to `28` on `peak_live`, and the designed probe pays it
  decisively and repeatably — until `-ffast-math` reassociates the graph and the axis stops describing
  what runs.
- **Representation choice is a compile-time decision, and the optimisation level is part of the
  representation.** The same two writings of the sixteen-term sum are more than `160%` apart at `O2`
  in the dependent-chain regime and indistinguishable at `O3fast`. A router that ranks representations
  without naming the flags it will be compiled under is ranking with a free variable in it.
- **Every effect in this card is compressed by the harness and the true structural gaps are larger.**
  The loop's own cost at `O2` is about `0.256` nanoseconds per step in the throughput regime against a
  marginal `0.061` nanoseconds per operation, so a three-operation expression carries more harness
  than arithmetic. Every percentage here is a lower bound.
- **A timing number from this harness is a distribution, not a value, and the card now says so
  everywhere.** `0` of the `8` survival cells reproduced across seven runs; the headline inversion
  count moved between `2` and `4` across three; `7` of the `32` probe cells changed their answer
  across five. The effects that survive all of it — division, depth, and the two named inversions —
  are the ones worth acting on, and the rest are reported with their spread rather than ranked.

## Limits

- **One machine, one compiler, one version.** Everything is `Intel64 Family 6 Model 167 Stepping 1`
  under `clang version 21.1.0` targeting `x86_64-pc-windows-msvc` on `Windows-11-10.0.26200-SP0`. A
  different CPU or a different compiler could reorder every finding in this report, and a CPU with a
  faster divider or no fused multiply-add would move the two largest effects directly.
- **`double` only.** No single precision, no extended precision, no integers, no exact rationals. The
  project's own arithmetic is exact rational; nothing here says anything about what that costs.
- **Straight-line code only.** Every emitted function is a dataflow graph with no loop and no branch
  in it, so no loop behaviour, no branch prediction and no memory hierarchy effect beyond an
  L1-resident input table is measured. Real mathematics has loops.
- **The corpus is hand-chosen.** `16` objects and `34` writings, fourteen objects taken verbatim from
  0037's named laws and two constructed. A different sixteen objects would give a different
  disagreement count, and the count is reported with its denominator everywhere.
- **The timing half of this card is not reproducible at this precision, and that is the largest limit
  on it.** `0` of the `8` survival cells returned the same count over seven repeats; the headline
  inversion count returned `3`, `2` and `4` over three; `7` of the `32` probe cells changed their
  answer over five. Every timing figure in this report is therefore an interval, and an interval from
  one afternoon on one machine at that. The instruction-level results of the ladder and of section `4`
  carry none of this.
- **Timing is wall clock, not cycles.** The clock is `QueryPerformanceCounter` at `10` MHz. No
  performance counter is read, so nothing here separates issue pressure from cache from frequency.
  **Effects smaller than the declared floor of `2.062%` are not resolvable, and that floor is itself a
  p95 of a skewed distribution whose worst identical-kernel gap over the seven survival repeats was
  `14.398%`.**
- **`7` of the `32` probe cells have no reproducible answer.** Over the `5` runs of the whole probe set
  those cells changed their verdict, with one cell ranging over `40.51` percentage points. Their
  entries in section `9` carry the count of runs in which the prediction survived, and a cell marked
  `2/5` or `4/5` is not a settled observation.
- **Several cells are at the floor of what the harness can time.** At `O2nativefma` in the throughput
  regime nine of the sixteen objects have both writings at the same block length as a kernel with no
  arithmetic in it, and the factored difference of cubes at `O3fast` is likewise at that floor. Their
  arithmetic is not being measured; only the fact that it is too small to see is.
- **The instruction audit and the timings are taken on different code.** The identical-instruction
  count of section `4` is taken on each writing compiled as a standalone function; the fusion and
  vector counts of the ladder are taken on the timed loops. They answer different questions and are
  not interchangeable.
- **The divisions by the literal `2` in the corpus are not divisions on the machine.**
  `trapezoid_area`'s two writings divide by `2` three times between them, and clang turns every one of
  them into a multiplication at every level above `O0`, so that object cannot probe divergence `1` at
  all. This is pinned by a test rather than left implicit.
- **Two probe kernels could not be located in the assembly at `O3fast`.** The compiler inlined the
  two `probe_division` kernels into `main`, so the loop instruction audit reports them as not found
  rather than as zero. Their timings are unaffected and are consistent with the divider's throughput
  — `1.281` against `0.648` nanoseconds per step — and the corpus audit quoted in the ladder found
  every kernel it looked for.
- **The throughput regime does not isolate throughput.** Divergence `3` shows it: four-way
  independence per loop step is not enough to hide a chain of `15` dependent additions, so the
  regime's readings for deep graphs carry a latency component that has not been separated out.
- **`-ffast-math` is not a safe flag** and this card does not recommend it. It reassociates floating
  point and changes results; it is included because it is the level at which the question "does the
  compiler undo the representation?" has a non-trivial answer, and the correctness audit runs at it
  precisely so the report cannot quote a speed without having checked the value.

## Evidence classification

- The instruction counts, the fusion counts, the vector counts and the flag isolation are
  **observations** read out of clang's own assembly output. They carry no noise floor, no repeat
  count and no threshold, and they reproduced exactly under an independent re-derivation. **They are
  the strongest evidence in this card.**
- The correctness audit and the guard ratio are executable **observations** whose verdicts are
  binary rather than quantitative, and each now carries a negative control that makes it fail.
- The repetition sweep, the noise floor, the harness calibration, the agreement table, the survival
  table, the floor sweep and the probe table are executable **observations** on the declared corpus
  in the declared environment, **reported as intervals over repeated runs**. Where an interval is
  wide enough to contain both answers, the cell is reported as unresolved and is not ranked.
- The claim that `peak_live` cannot exceed `16` registers below `65536` leaves is a **structural
  argument** — the Sethi-Ullman number of a tree with `n` leaves is at most `floor(log2(n)) + 1` —
  with a sweep of `8` sizes beside it as a witness.
- The attribution of each inversion to one of the four divergences is a **classification**, not a
  proof: all consistent explanations are reported and `4` inversions have none.
- The statement that the parabola's chain is about three times shorter than the vertex form's at
  `O3fast` is an **observation** with a stated consequence and a partial cause: `1.7315` to `1.7578`
  nanoseconds per step against `3.4447` to `3.5671` over a floor of `0.9094` to `0.9117` is the
  observation, and factoring under `-ffast-math` is the reading offered for it.
- The statement that the `O2nativefma` rung cannot be split into an ISA rung and a fusion rung is an
  **observation plus a structural argument**: the observation is that `-mfma`, the narrowest switch
  that makes fusion reachable, already changes all `34` kernels while emitting `0` FMAs; the argument
  is that no smaller ISA step exists on this target.
- No general law about compiled mathematics is claimed. This is `16` hand-chosen objects and `4`
  constructed probes, on one processor, under one compiler, at one moment.

## Validation

```text
77 passed
```

That is this card's own file, `tests/test_metal.py`, run on its own, and it is the only test count
this report quotes. The file was run `6` times consecutively at accept time and returned
`77 passed` every time, in `136.49` to `190.51` seconds. One run before those `6`, taken immediately
after the accepting correction described below, returned `1 failed, 76 passed`, and its test name was
not captured; it is recorded because an uncaptured failure is still a failure, and because this card
was returned three times for exactly this kind of thing. The first revision also printed a whole-repository line, `1516 passed, 2
skipped`; review measured `1553 passed` in the same window, because `2` concurrent cards had landed
tests in between. **A whole-repository count in an experiment report goes stale the moment another
card lands**, and it is not a property of this card in any case. The whole-repository suite passes —
review took it green in the same window — and nothing outside this card imports `parseatlas.metal`,
so no change made here can move it. The number it passes with belongs to the run that takes it, not
to this page.

The `77` tests of this card check correctness before any timing is believed — at all `4`
optimisation levels, with a control that makes each level wrong in turn — pin the emitter's output
byte for byte, show the anti-elimination guard working by compiling a deliberately dead variant and
measuring that its loop is gone, pin the `4` probes' predicted table and their measured table in
separate tests, pin the agreement table's disagreement count at a floor of `0.20`, pin the
identical-instruction counts at `3`, `0`, `0` and `8`, pin the opening table's scalar and packed
multiply columns and the `8` writings clang vectorises at `-O2`, pin each flag of the `O2nativefma`
rung against the others, and skip with a reason naming `clang` when no compiler is present.

### A gate whose control could not see the failure — and the same mistake twice in one card

**The correctness gate had no test that could fire.** The test named
`test_a_deliberately_wrong_emission_is_caught_by_the_correctness_audit` built a *correct* writing and
asserted the audit passed, so a gate hardwired to pass was invisible to it. Review demonstrated this
on an isolated copy: replacing one line of `correctness_audit` so that it compared the C output
against itself left all `65` tests green, and changing `if deviation > TOLERANCE:` to `if False:` did
the same. This is the third card in the repository with that defect and ROADMAP.md carries the rule
under *"Every gate needs a test that it can FIRE"*.

The repair replaced the emitter for the duration of the test with one that writes `b - a` where the
writing says `a - b`, and asserted that the audit returns `all_match is False` with a non-empty
failure list naming the kernel. **And that repair was still one level deep.** The control ran at
`-O0` alone, so it could not see a gate that silently dropped the other `3` levels: review mutated
`all_match`'s `all(... for entry in per_level)` to `per_level[:1]` on an isolated copy — which blinds
the gate to `-O2`, to `-O2 -march=native -ffp-contract=fast` and to `-O3 -ffast-math`, the last of
them the `-ffast-math` rung this report says the audit exists to check — and all `71` tests still
passed. **That is the same failure twice inside one card.** A control that exercises `1` of the `4`
things the published claim covers cannot see the other `3` go missing, and the published claim here
is `336` checks per level, `1344` in all, `0` failures, at all `4` levels.

The control now runs at all `4` levels and asserts each level's own failure list rather than only
the aggregate. A second test makes exactly ONE level wrong at a time, by substituting a program that
computes `b - a` for that level's binary alone while every other level compiles the honest program —
the same emitter, the same clang, the same flags, the same exact-rational oracle. Under
`per_level[:1]` that test fails for `3` of its `4` parameters, because the aggregate reports
`all_match is True` while `-O2`, `-O2nativefma` or `-O3fast` is failing, and the whole file on the
mutated copy comes back `3 failed, 74 passed`. A third test makes the audit fail and requires
`metal_report` to raise **before** any benchmark starts, by making the benchmark explode if reached.

### The rule this card ended up writing: do not gate on a statistic you cannot bound

**The repetition sweep's test took `3` attempts.** The first asserted
`consecutive_drift[-1] < consecutive_drift[0]`, a comparison of two noise-dominated quantities; it
failed `3` of `5` standalone re-runs here, and review's `3` sweeps returned
`(6.67, 6.25, 0.30, 2.22, 0.33)%`, `(1.92, 3.30, 2.07, 1.87, 1.79)%` and
`(0.00, 0.96, 0.36, 0.42, 3.30)%` — the last with its largest drift at the final point. The second
replaced it with a threshold at `8%`, set just past the largest value `17` sweeps had produced, and
review watched it fail `1` of `5` runs at `8.53%`, on the second-fastest of those `5`.

**A margin measured from a sample maximum is not a margin.** Section `2` publishes what the statistic
actually does over `48` sweeps — `0.06%` to `11.43%`, median `1.82%`, above `8%` in `3` of them — and
the threshold is deleted rather than raised. The test now asserts only that `262144` is a point on
the swept curve, that it is not the last point, and that the timed block grows with the repetition
count, which is monotone in the input and held in `48` of `48`.

**`6` other declared thresholds in this file went the same way, and each is now either a comparison
made inside one run or a bound whose argument does not come from the sample.** `3` were repaired in
the previous revision:

- `test_every_probe_cell_the_machine_never_separated_is_pinned_as_an_upper_bound` carried `7`
  per-cell upper bounds, each at about `1.5` times that cell's own largest observed gap. It now
  asserts the comparison **inside one run** — every cell the machine never separated is separated by
  less than every cell it did — with one coarse ceiling of `8%` beside it so a run that collapsed
  everything to noise cannot pass.
- `PIN_FLOOR`, the floor the probes' measured table is read at, stood at `110%` while the division
  probe reached `106.02%`. It is now `130%`, the geometric mean of the two populations it separates.
- The `10` `DECISIVE_CELLS` lower bounds are six tenths of the smallest gap their cell has produced,
  and the gaps had moved while the bounds had not.

`3` more were found while repairing the sweep, by running the file `5` times and then repeating
the probe set `30` times to measure what the gates were actually standing on:

- `test_the_register_probe_finds_nothing_and_the_direction_it_hints_at_is_the_wrong_one` had already
  had its absolute bounds replaced by a comparison against the noise floor measured in the same run,
  and **that failed too**: a full suite run here returned a gap of `2.39%` against a floor of
  `4.33%`. Over `30` runs the ratio of gap to same-run floor fell as low as `0.37` for
  `latency/O2` and `0.23` for `throughput/O0`. **Neither the size nor the direction is asserted for
  this probe now.** The direction was the third attempt and it broke the same way as the first two:
  it was defended as a sign rather than a magnitude, `30` of `30` runs, and review saw it resolve
  the other way in `1` of `5` runs of this file. **A sample unanimity is a sample maximum wearing a
  different hat.** The rule was applied to every magnitude in this file and then exempted for signs,
  and the exemption is what failed. What is left carries a real margin: a within-run comparison
  against the deep-chain cells, whose smallest gap exceeded the largest register gap by a factor of
  at least `6.75` in every run, and the structural check that every register cell reports no
  observed classification at all.
- `test_the_probes_measured_order_is_pinned_separately_from_the_prediction` pinned all `32` cells'
  classification at `PIN_FLOOR`, and one of them straddles it: `probe_latency/latency/O0` ranges from
  `124.63%` to `171.15%` over `30` runs and resolved in `25` of them. **No constant floor repairs
  that**, because the floor must also stay above the division cells at `111.89%`, leaving a margin of
  about `1.06` times. That cell is now asserted to be resolved in the machine's direction or
  unresolved — never the other direction — and its size is checked against the noise floor measured
  in the same run, where the ratio never fell below `15.29`. The other `31` stay pinned exactly.
- The `DECISIVE_CELLS` bounds had closed again. The tightest stood at `0.18` against a smallest
  observed `18.48%`, a margin of `1.03` times. All `10` are re-derived over the
  `30`-run study by the same six-tenths rule, and the tightest margin left is `1.30`.

**The register probe now gates on no timing quantity at all — neither its size nor its sign — and
the rest of the file still does, with the margins named below.** Two earlier versions of this
sentence overstated: the first said that no test gates on a quantity whose observed range covers its
own threshold, which review falsified on its own run because a direction is a quantity too; the
second said no test in the file gates on timing, which is not true either. What is true is the list.
Five timing thresholds remain, each derived from a sample and each stated with its margin:
`max_ratio` under `0.01`, the harness floor median under `0.05`, a relative gap over `0.70`, a gap
over `10` times the same-run floor at a margin of about `1.5`, and a parallel speedup over `1.5`.
The tightest `DECISIVE_CELLS` margin is `1.30`. **None of them has been observed to fail, and none
of them is a bound**; they are the same class of assertion as the three this card has already had to
withdraw, and the next card to touch this file should expect to withdraw them too. Where a quantity is not resolvable, the test asserts what is structural and the timing is
published with its spread instead.

**And the sharpest thing this card learned about its own tests is about where evidence comes from.**
The `30` runs behind the direction were collected by calling the probe on its own. The assertion was
evaluated from a module-scoped fixture partway through a `77`-test file that had already compiled and
timed the whole corpus. Those are different machines in every respect that matters to a stopwatch.
**Evidence for a test's stability has to be collected the way the test runs.**

### The correction taken on acceptance

**The register probe's direction assertion was removed by the manager, and the direction is published
instead.** It was the third form the same assertion took in this file — an absolute bound, then a
ratio against the same-run floor, then a sign — and all three broke; review saw the sign resolve the
other way in `1` of `5` runs. What the test asserts now is structural: that every register cell
reports no observed classification at all, that the largest register gap sits below the smallest
deep-chain gap measured in the same run, and that the cells named as the ones that move do carry a
gap and both roles, so the pointer into section `9` cannot go stale. The direction and its spread are
in section `9`, where they belong.

### Mutation testing

`19` targeted mutations were applied to an isolated copy of the tree — never to the working tree —
each one a plausible wrong version of a load-bearing line. The original `10` were the emitter writing
the wrong operator, the emitter numbering temporaries by object identity, the latency harness feeding
the shallowest leaf instead of the deepest, the schedule width reporting the narrowest level, the
classifier counting an unresolved pair as agreement, the relative gap measured against the larger
side, the noise floor reporting its maximum instead of its declared p95, the throughput kernel
dropping its accumulator so the loop dies, the input table giving every variable the same base value,
and the shape catalogue using the wrong Sethi-Ullman rule.

`6` were added in the previous revision, `4` of them the ones review used to show the old gate was
inert, and `3` in this one:

```text
correctness_audit compares the C output against itself          killed
`if deviation > TOLERANCE:` becomes `if False:`                 killed
`all_match` hardwired to True                                   killed
metal_report stops gating on correctness                        killed
`separable` hardwired to False                                  killed
DEFAULT_ITERATIONS moved off the swept curve                    killed
`all_match` reads per_level[:1], so only -O0 is checked         killed
the scalar multiply count matches v?mul[sp]d and counts packed  killed
the vectorised count reads any packed instruction, not packed
  ADD, SUB, MUL and DIV                                         killed
```

`19` of `19` were killed. The `per_level[:1]` mutation is the one review used to show the previous
control was blind; on the mutated copy the whole file now returns `3 failed, 74 passed`.

### Concurrency

Compilation is parallel and timing is not. Over `8` independent compilations on `16` cores with `8`
workers, three repeats each: `5.612` seconds sequential against `1.314` seconds parallel, a speedup
of `4.270`. Timing runs are strictly sequential by design, because concurrent load changes the
measurement itself rather than how fast it is taken — which is what made experiment 0041's timings
irreproducible, and which is the reason the first revision of this card published a survival count no
re-run has since returned.
