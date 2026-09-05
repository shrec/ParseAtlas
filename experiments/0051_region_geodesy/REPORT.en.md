# ParseAtlas experiment 0051: does the Region model earn its keep?

**ქართული ვერსია:** [REPORT.ka.md](REPORT.ka.md)

## The Phase 14 verdict, first

**Yes — and the observation that decides it is one line. Over `24` sampled points the two encodings of the same physical point are equal as tuples at `0` of them, while the decode relation `decode(R2(x)) == R1(x)` holds at `24` of `24`: `6` of `6` halves discharged symbolically under the declared relations, and every point corroborated in exact arithmetic with no tolerance anywhere. The project's own equivalence oracle decides `0` of the `24`, and not because it disagrees — it cannot be formed at all, because no geodetic formula is a parse of the project's grammar.**

That is the premise of Phase 14 holding on one concrete pair, which is what this card was asked to decide. Three things sharpen it, and each of them is on the page below rather than in this paragraph:

- the decode obligation is not merely *satisfiable* here, it is **the only obligation that is well formed**: the geodetic encoding is a `5`-tuple and the ECEF encoding is a `3`-tuple, so `F1(x) == F2(x)` is not a question one can ask and get a wrong answer to — it is a question one cannot ask;
- **0033's Region model transfers as a shape and as a cost model, and does not transfer as a decision procedure.** `2` of its `5` parts were reused unchanged and `3` refused this pair by construction, with the refusal text recorded. That is a finding about the model, not an inconvenience;
- **a negative answer was available and did not happen.** If the two encodings had agreed as tuples anywhere but a degenerate point, or if the decode had failed at a point the symbolic half accepted, or if 0033's `Encoding` had swallowed the pair, this report would have said so.

Module: `src/parseatlas/region_geodesy.py`. Tests: `tests/test_region_geodesy.py`.

**This card is not a geodesy library and it is not the Region engine.** Phase 14 is a programme; this is the one experiment that decides whether its premise holds before anyone commits to building the engine.

## Why this pair, and what would have refuted the card

The owner named geodesy, and the ROADMAP subsection *"Expand wherever the research demands it"* classifies this card as its **third** kind: a change of representation, which is not a language extension at all, and which no number of new operators reaches. Geodesy supplies, in classical published form, exactly what the Region model was invented for:

```text
geodetic   (phi, lambda, h)   latitude, longitude, height above the ellipsoid
ECEF       (X, Y, Z)          earth-centred, earth-fixed Cartesian
```

Two representations of one object, with a documented conversion each way. Three properties make it a test rather than an illustration, and all three are observed below rather than asserted: the seam is **asymmetric**, value equality fails **by construction**, and — the axis this repository has never had — the **choice of writing has a numerical consequence**.

## What of 0033's machinery fits, and what does not

Nothing here is argued. Each part of `parseatlas.region` was run against this pair and what it did was recorded.

| part of 0033 | reused | evidence |
|---|---|---|
| Region shape | yes | `(inputs, state, operations, outputs, invariants)` carries both representations and the iteration unchanged |
| `region_cost` | yes | priced `geodetic_to_ecef`: total `16`, depth `9`, max live `7` |
| `Operation` | no | `rw: unknown operation kind 'sqrt'; the vocabulary is ['add', 'div', 'mul', 'neg', 'sub']` |
| `Encoding` | no | `geodetic_to_ecef_attempt encode: 'sqrt(1 - phi)' is not a rational function of ['phi', 'lam', 'h']` |
| `unroll` | no | `s__1: unknown operation kind 'sin'; the vocabulary is ['add', 'div', 'mul', 'neg', 'sub']` |

**The finding, stated plainly: 0033's Region model is a model of rational-function regions.** The decode obligation generalises; the decision procedures that discharged it do not — because they were decision procedures for the rational-function class and this pair is not in it. `Encoding` parses every map with a function that refuses `sqrt`, and its construction gate decides the left inverse by cancellation. `unroll` rebuilds `Operation` objects and therefore inherits the vocabulary gate even though the loop itself is well formed.

What *does* transfer is more interesting than what does not. `region_cost` walks an operation DAG and never asks what an operation means, so it prices this vocabulary correctly without modification — it is called here, not reimplemented, with only its loop section suppressed because that section calls `unroll`, and the test checks the reuse by identity rather than by equality. The vocabulary is `4` kinds wider than 0033's and **conservative on the shared `5`**: restricted to `add`, `sub`, `mul`, `div` and `neg` it is 0033's table, arity for arity, checked against the imported table and not a copy.

## What Generation 1 cannot write

This section exists so that no reader can leave with the impression that a world in this project writes a geodetic conversion. **It does not.**

```text
parses      N + h
parses      (N + h) * c * cl
parses      p / c - N
parses      p * c + Z * s - a * rw
refused     sin(phi)                 ValueError: Unexpected token: '('
refused     cos(phi)                 ValueError: Unexpected token: '('
refused     sqrt(1 - e2 * s * s)     ValueError: Unexpected token: '('
refused     a / sqrt(1 - e2 * s * s) ValueError: Unexpected token: '('
refused     atan2(Z, p)              ValueError: Unexpected character at position 7: ','
```

`4` writings parse and `5` are refused, each with the parser's own message. The rule the split obeys is exact: **the rational skeleton of every formula parses once its transcendental leaves are bound to names outside the notation; the leaves themselves never do.**

Experiments 0002 and 0032 supply `sin`, `cos` and `sqrt` as **outer** functions — a unary function wrapping a whole Generation 1 expression, never an operand inside one. `atan2` does not exist in this project at all, and could not be an outer function if it did, because every outer function in the catalogue is unary and `atan2` is binary. Across the `6` declared regions of this card there are `63` operations, of which `16` have no Generation 1 counterpart:

| region | operations | Generation 1 | outside |
|---|---|---|---|
| `geodetic_to_ecef` | 16 | 11 | 5 |
| `geodetic_trig_to_ecef` | 12 | 11 | 1 |
| `ecef_to_geodetic_setup` | 7 | 4 | 3 |
| `ecef_to_geodetic_step_C` | 18 | 14 | 4 |
| `ecef_longitude_step` | 9 | 6 | 3 |
| `geodetic_longitude_step` | 1 | 1 | 0 |

## The ellipsoid, exactly

WGS 84, given by its **two defining constants**, from which everything else is derived as an exact rational rather than quoted:

```text
a    = 6378137                        exact, defining
1/f  = 298.257223563                  exact, defining
f    = 1 / (1/f)                      exact rational
b    = a (1 - f)                      exact rational
e2   = f (2 - f)                      exact rational
```

*PRIOR ART.* The published WGS 84 values are stated from knowledge and checked against the derivation. Every one agrees to the digits the defining document gives:

| constant | published | derived | difference |
|---|---|---|---|
| `a` | 6378137.0 | 6378137.0 | 0.0 |
| `1/f` | 298.257223563 | 298.257223563 | 0.0 |
| `b` | 6356752.314245 | 6356752.314245179 | 1.797e-07 |
| `e2` | 0.00669437999014 | 0.006694379990141317 | 1.318e-15 |
| `a*a/b` | 6399593.6258 | 6399593.625758493 | 4.151e-05 |

The two reference points are definitional rather than tabulated, and are computed through the same declared region as every other number here: `(phi, lambda, h) = (0, 0, 0)` gives ECEF `(a, 0, 0)` exactly, and `(90 deg, 0, 0)` gives `(0, 0, b)` exactly.

## The representation choice that makes an exact answer possible

`sin(phi)` is transcendental for every rational `phi` but `0`, so a sample of latitudes given as angles has no exact arithmetic behind it. The geodetic encoding is therefore declared in **trigonometric form**, and every sample latitude and longitude is built from a Pythagorean triple:

```text
geodetic, angle form           (phi, lambda, h)
geodetic, trigonometric form   (sin phi, cos phi, sin lambda, cos lambda, h)

cos = (m*m - n*n) / (m*m + n*n)      sin = 2*m*n / (m*m + n*n)
```

so `sin*sin + cos*cos == 1` exactly. Every quantity in the forward map then lies in `Q(sqrt(W))` with `W = 1 - e2 sin^2 phi` rational — one quadratic extension of the rationals, closed under all four operations. **The exact side of this experiment is exact arithmetic, not high-precision floating point.** The trigonometric form is a declared choice; it is the third representation in play and it is named again in the limits.

The sample is `24` hand-chosen points in `6` declared regimes: `6` mid-latitude, `5` near-polar, `5` near-equatorial, `4` degenerate (the exact pole and the exact equator), `2` small height, `2` at `lambda = 0`. A regime names why a point was chosen and does not partition the properties — `5` points sit at zero height and `5` on the prime meridian. Heights run from `-400` to `35786000` metres.

## Observed results

### 1. Value equality against the decode relation

This is the card's central obligation, and it is reported in three regimes that are never blended.

| regime | what it is | points it decides |
|---|---|---|
| semantic key | `parseatlas.alternative_mathematics.semantic_key` over `canonicalize` | 0 |
| exact | `decode(encode(g)) == g` in `Q(sqrt(W))`, no tolerance anywhere | 24 |
| tolerance | the float iterative inverse against the declared tolerances | 24 |

The semantic key decides nothing, and the reason is observed rather than described, because the oracle is called rather than talked about. It is offered `5` writings: `2` form a key and `3` are refused by the parser, and the split is the whole point — a key forms only for the rational **skeleton**, in which `c`, `cl` and `N` are free variables standing for nothing in particular, so it identifies a different object from the map it was extracted from. For a geodetic formula itself a key is formed `0` times. And even where a key is formed, the two encodings are a `5`-tuple and a `3`-tuple of different names.

**And the decisive half.** Over the same `24` points:

```text
plain value equality, whole tuple      0 / 24
decode relation, exact                24 / 24
decode relation, within tolerance     24 / 24
```

> **Which form, and what the row is worth.** That row compares the geodetic ANGLE form `(phi, lambda, h)`
> against `(X, Y, Z)` — the generous choice, since both are 3-tuples. But it compares radians against metres,
> so on any non-degenerate point it could not have come out otherwise. The row is reported because it was
> asked for; the informative half of this section is the decode relation holding at `24` of `24` and the
> project's own semantic key being unable to form a key for a geodetic formula at all.

Value equality holds nowhere. It does hold on `6` single components across `5` points, and every one of them is a zero meeting a zero — the longitude on the prime meridian against `Y`, and the height at sea level against `Z` on the equator. That is precisely the degenerate agreement the shape of the question predicts, and it is why the whole-tuple count is the one that matters.

The symbolic half is `6` relations, each reduced to zero under the declared relations `c^2 = 1 - s^2`, `cl^2 = 1 - sl^2` and `r^2 = 1 - e2 s^2`:

```text
p*p == X*X + Y*Y                                             residue 0
X*sin(lambda) == Y*cos(lambda)                               residue 0
height writing A:  p/c - N == h                              residue 0
height writing B:  Z/s - N(1-e2) == h                        residue 0
height writing C:  p*c + Z*s - a*r == h                      residue 0
the fixed point is the true latitude                         residue 0
```

Observed round-trip errors against the declared tolerances, at the declared convergence tolerance of `1e-12` radians:

```text
maximum latitude error      1.110e-16 rad     tolerance 1e-11
maximum longitude error     2.220e-16 rad     tolerance 1e-11
maximum height error        9.313e-10 m       tolerance 1e-06
```

The height figure is not an accident of the sample: `9.313e-10` metres is exactly one unit in the last place of a double at the Earth's radius, and every height writing subtracts two quantities of that size. It is the floor, not a result.

### 2. The seam is asymmetric

The forward direction is closed form and costs one number. The inverse is a setup, then `k` iterations, then one epilogue, and `k` is observed on the sample at each tolerance rather than assumed.

| region | operations | depth | max live | outside Generation 1 |
|---|---|---|---|---|
| `geodetic_to_ecef` | 16 | 9 | 7 | 5 |
| `ecef_to_geodetic_setup` | 7 | 5 | 5 | 3 |
| one inverse iteration | 18 | 13 | 6 | 4 |
| the inverse epilogue | 11 | 7 | 5 | 3 |

The loop converges on the **latitude**; the height is read off once at the end, by the epilogue. So the inverse costs a setup, then `k` iterations, then one epilogue, and never `k + 1` iterations: at the declared tolerance that is `7 + 3 * 18 + 11 = 72`.

| tolerance | iterations | inverse total | asymmetry ratio |
|---|---|---|---|
| 1e-06 | 1 to 2 | 54 | 3.375 |
| 1e-09 | 1 to 2 | 54 | 3.375 |
| 1e-12 | 1 to 3 | 72 | 4.5 |
| 1e-15 | 1 to 3 | 72 | 4.5 |

Every point converges at every tolerance; `0` points reached the iteration cap. At the declared `1e-12` the sample takes `36` iterations in total over `24` points, a mean of `1.5`, and the worst point takes `3`.

**Unrolling the loop confirms that nothing hoists out of it.** At `1`, `2`, `3`, `4`, `6` and `8` steps the unrolled region costs `18`, `36`, `54`, `72`, `108` and `144` operations — exactly `k` times one step, with `0` step-invariant operations. This is the opposite of 0033's axis, where the normaliser collapsed an operation every step emitted identically; here the operation that repeats is `sin(phi)` on a *changed* `phi`, and nothing repeats.

### 3. The chain: at what `n` does converting pay

The 0042 question applied here. **The declared chain:** a point is given in ECEF and required in ECEF; it receives `n` longitude increments, the increments arrive as angles, and **every intermediate longitude is published** — the chain is a track and the longitudes are the track.

```text
one increment in geodetic     lam + dlam                          1 operation
one increment in ECEF         rotate about the spin axis,
                              then publish atan2(Y, X)            9 operations
```

**The two routes are first shown to compute the same thing.** T22's obligation is about a transformation and not only about an encoding, so a cost comparison between two routes means nothing until the routes agree. One longitude increment of `0.9273` radians, applied in geodetic and then converted, against the same increment applied in ECEF as a rotation about the spin axis: the two agree at `24` of `24` points against a declared guard of `1e-06` metres, and the worst disagreement observed is `3.725e-09` metres, at `mid_9_40_41` — the point at geostationary altitude, where that is under half a unit in the last place of a double at its own magnitude.

| tolerance | seam | crossover |
|---|---|---|
| 1e-06 | 70 | 9 |
| 1e-09 | 70 | 9 |
| 1e-12 | 88 | 12 |
| 1e-15 | 88 | 12 |

At the declared tolerance the ECEF-resident route costs `9n` and the geodetic-resident route costs `88 + n`. At `n = 11` the two cost exactly the same, `99` operations each; `n = 12` is the first length at which converting strictly wins, `108` against `100`. **The curve is not still moving** — both routes are exactly linear in `n` and the difference grows by `8` per step forever, so the crossover is the whole answer and there is no second turn further out.

**The crossover moves with the tolerance, and that is the point of declaring one.** Tighten the convergence tolerance from `1e-09` to `1e-12` and the worst-case iteration count rises from `2` to `3`, the seam rises from `70` to `88`, and the crossover moves from `9` to `12`.

**It also moves with how a transcendental operation is priced — and it stops moving.** Counting every operation as one unit is a modelling choice; a reader who charges `sin`, `cos`, `sqrt` and `atan2` more can read the answer off a sweep instead of being told it does not matter:

| weight on a transcendental | seam | ECEF per step | crossover |
|---|---|---|---|
| 1 | 88 | 9 | 12 |
| 2 | 111 | 12 | 11 |
| 4 | 157 | 18 | 10 |
| 8 | 249 | 30 | 9 |
| 16 | 433 | 54 | 9 |
| 64 | 1537 | 198 | 8 |
| 256 | 5953 | 774 | 8 |

The crossover falls from `12` to `8` and stops: however expensive a transcendental call is made, converting never pays before `n = 8`, because both the seam and the per-step ECEF cost are dominated by transcendental calls in a fixed ratio.

**The control that removes the result.** If the intermediate longitudes are *not* published, the `n` rotations about one axis compose into a single rotation, the ECEF route becomes `8` operations for the rotation itself — the step's ninth operation is the `atan2` that publishes the longitude, which this control's own premise removes — plus the `n - 1` additions that accumulate the angle, the geodetic route becomes `89`, and **no crossover exists at any `n`**. Publishing every `lambda_i` is a requirement of the declared chain and not a modelling trick, but the whole result rests on it and it is reported here rather than left for a reader to find.

### 4. Equivalent writings that disagree numerically

**This is a new kind of result for this repository.** Every earlier card observed what a writing costs; none observed whether a writing is *right*. Three algebraically identical writings of the ellipsoidal height:

```text
A   h = p / cos(phi) - N                                          7 operations
B   h = Z / sin(phi) - N (1 - e2)                                 8 operations
C   h = p cos(phi) + Z sin(phi) - a sqrt(1 - e2 sin^2 phi)        9 operations
```

As the loop's epilogue the same three writings cost `9`, `9` and `11`, and the reason is structural rather than arithmetic: writing `B` divides by the sine and never touches the cosine at all, so its epilogue computes only one of the two trigonometric values.

In exact arithmetic all three return the declared height exactly, at every point where they are defined, and the symbolic half above proves that they must. In float they do not agree, and the disagreement is not small.

| point | cos(phi) | A error | B error | C error |
|---|---|---|---|---|
| `near_pole_1e_2` | 9.950e-03 | 1.304e-08 | 9.313e-10 | 9.313e-10 |
| `near_pole_1e_4` | 9.999e-05 | 3.367e-06 | 0.0 | 0.0 |
| `near_pole_1e_6` | 1.000e-06 | 4.201e-04 | 9.313e-10 | 0.0 |
| `near_pole_1e_8` | 1.000e-08 | 3.229e-02 | 0.0 | 9.313e-10 |
| `near_pole_1e_10` | 1.000e-10 | 4.449e+00 | 0.0 | 0.0 |

All errors are in metres. **Writing `A`'s error grows as `1 / cos(phi)`**: two decades closer to the pole is two decades more error, from `3.367e-06` metres to `4.449e+00` metres. Writing `C` never exceeds `9.313e-10` metres — one unit in the last place at the Earth's radius — at any of the `24` points.

**The worst disagreement is worse still, and it is a silent one.** At the exact pole writing `A` divides by a cosine that is exactly zero, so it is mathematically undefined; float does not say so, because `cos` of the nearest double to `90` degrees is not zero. It returns a finite number — minus the polar radius of curvature — in error by `6399843.625758493` metres at `pole_exact_h`. Exact arithmetic raises there and float does not, which is the entire content of the distinction the summary keeps between the maximum error and the maximum error where the writing is defined.

| writing | defined at | max error | max error where defined | silently undefined at |
|---|---|---|---|---|
| A | 24 | 6399843.625758493 | 4.448512075468898 | 2 |
| B | 22 | 9.313e-10 | 9.313e-10 | 0 |
| C | 24 | 9.313e-10 | 9.313e-10 | 0 |

**`C` is the accurate writing on this sample**, and the three writings have three different domains: `A` excludes `cos(phi) = 0`, `B` excludes `sin(phi) = 0`, and `C` excludes nothing. So "which writing is right" is not a ranking — `A` and `B` are each undefined where the other is fine, and only `C` is defined everywhere. That is the same distinction 0033 drew between an equality half and a definedness half, arriving here on its own.

**Why — observed rather than asserted.** Perturb the latitude by `d` and read the change each writing produces in the height, at `mid_3_4_5`:

| perturbation | A | B | C |
|---|---|---|---|
| 1e-06 | 8.50197968352586 | 4.782348626293242 | 3.187917172908783e-06 |
| 1e-08 | 0.08501965180039406 | 0.047823552042245865 | 0.0 |
| 1e-10 | 0.0008501950651407242 | 0.0004782341420650482 | 0.0 |

`A` and `B` fall by one decade for each decade of the perturbation; `C` falls by two and reaches zero. **Writing `C` is stationary at the true latitude and the other two are not**, which is why a latitude error of one unit in the last place costs `C` nothing and costs `A` metres.

**The same phenomenon with no angle in it at all.** Three published writings of `e2`, against the exact rational:

| writing | value | error in units in the last place |
|---|---|---|
| `f*(2-f)` | 0.006694379990141317 | 0.383 |
| `(a*a-b*b)/(a*a)` | 0.006694379990141316 | 1.617 |
| `1-(b/a)**2` | 0.00669437999014133 | 15.383 |

A factor of `40.158` between the best writing of one constant and the worst, from nothing but where the subtraction is placed.

### 5. Where the decode relation has no inverse

On the polar axis `X` and `Y` are exactly zero, so **every longitude encodes the same physical point** and the decode cannot return the one that was encoded. `2` of the `24` sample points sit there. At `1` of them the declared longitude happens to be zero and `atan2(0, 0)` agrees by coincidence; at the other the recovered longitude is wrong by `0.761` radians.

This is a fact about the decode relation's **domain** and not a numerical shortfall, and it is reported as one. It is also the sharpest single answer to the card's question: a value-equality oracle has no vocabulary in which to say *"these two encodings denote the same object, and the map back is not a function here"*, while the decode relation says exactly that and says where.

## Controls

- **the sign of the reuse claim.** `region_cost` is checked by identity against the imported function, so a reimplementation would fail rather than pass an `==`;
- **the vocabulary extension is conservative**, checked against 0033's imported arity table on all `5` shared kinds rather than against a copy of it;
- **the exact side is a field.** `Surd` is checked for commutativity, for the multiplicative inverse, for refusing to combine values from two different sample points, and for normalising the trivial extension that arises at the equator, where `W = 1` and `0 + a*sqrt(1)` would otherwise compare unequal to `a`;
- **the latitude carrier control**, which is what keeps section 4 honest. Carry the latitude as its exact `(sin, cos)` pair rounded to a double instead of as an angle in radians, and every writing is within `9.313e-10` metres at every point where it is defined. **So the disagreement is not a fact about the writing alone — it is the writing together with representing the latitude as a float angle**, and near the pole a float angle carries an absolute error that the writing either divides by a small cosine or does not;
- **the composition control** in section 3, which removes the crossover entirely;
- **the iteration cap.** `0` of the `24` points reached it at any of the `4` tolerances, so no reported iteration count is a truncation.

## Multicore

Repository policy is multicore by default with an observed decision, and here the observation says sequential.

```text
cores observed                    16
workers the policy would raise    15      (one core of headroom)
sample                            24 points
sequential                        0.054 s        0.00225 s per point
raising a pool                    2.20 s         before any work is done
break-even                        1048 points
chosen path                       sequential
sequential and parallel agree     yes
```
**These three figures are module literals, not observations of this run**, and review re-observed them on the
same idle machine. `POINT_SECONDS = 0.00225` and `POOL_STARTUP_SECONDS = 2.20` are declared constants; the
sequential total and the break-even are arithmetic on them. Re-observed: `0.001265` s per point, a factor of
`1.8` below the declared figure, pool startup `2.267` s, and a break-even of `1920` points rather than `1048`.
The decision is untouched either way — `24` points is far below both break-evens and `test_sequential_and_parallel_agree`
passes — but the card's standard is that every number comes from a run, and these three did not.


The break-even is not a chosen threshold: a pool costs its startup and then runs the work `15`-fold faster, so it is worth raising exactly when `n * t > startup + n * t / 15`, which is `1048` points at the observed rates. The sample is `24`. The parallel path is implemented, is exercised by a test on `6` points with `2` workers, and produces identical results — parallelism changes how fast, and never what is observed.

## Limits

- **Generation 1 cannot write any of this.** `16` of the `63` declared operations have no counterpart in the project's notation. `sin`, `cos` and `sqrt` exist only as unary outer functions wrapping a whole expression; `atan2` does not exist at all and is binary. No world in this project writes a geodetic conversion, and no number in this report should be read as though one did;
- **the ellipsoid is a declared choice.** WGS 84, by its two defining constants. Another ellipsoid changes every metre here and changes nothing structural;
- **the tolerances are declared choices**, and each says at its own definition what moves if it moves. The convergence tolerance `1e-12` radians decides the iteration count and therefore the seam and the crossover, which is why both are published across `4` tolerances instead of at one;
- **the sample is hand-chosen** — `24` points placed where the classical formulas are known to be delicate. It is not a sampling design and it supports no claim about a distribution of latitudes; it supports claims about the points it contains;
- **the trigonometric form is a third representation**, introduced so that an exact authority exists at all. Results stated about the geodetic encoding are stated about its trigonometric form on the exact side and about its angle form on the float side, and section 4 exists precisely because those two are not the same thing;
- **every operation counts as one unit**, including `sin`, `cos`, `sqrt` and `atan2`. That is a modelling choice, and the weight sweep in section 3 is what makes it visible rather than load-bearing. None of these counts is a time;
- **float behaviour is this machine's.** The exact-rational side is the authority, and every float figure in section 4 is an observation of IEEE-754 double arithmetic on this machine and this SymPy;
- **this card tests the Region model's premise on ONE pair.** It does not generalise to the engine, it does not show that a search would find any of these transformations, and it says nothing about whether the decode obligation is dischargeable on a pair nobody has already solved by hand.

## Evidence classification

- **observed here**: every table above, from a single run of `headline_report`;
- **prior art, stated from knowledge and checked**: the WGS 84 defining and derived constants, and the classical forms of the direct and inverse problems. The three height writings are classical and none of them is new here; what is new is the observation of what they cost each other;
- **not established**: that the Region model would *find* the trigonometric form, the robust height writing, or the crossover. This card observes that the obligation can be stated and discharged where value equality cannot even be posed. It observes nothing about search.

## Validation

`tests/test_region_geodesy.py`, `42` tests. Pinned as literals rather than recomputed: the published WGS 84 constants; the two reference points, exactly; the round trip with its tolerances; that plain value equality **fails** at every point, in its own test; that the decode obligation is discharged at every point, in a separate test; the iteration counts at all `4` tolerances; the asymmetry ratios and the epilogue they include; the crossover and its movement with the tolerance and with the transcendental weight; the composition control; that the chain's two routes compute the same thing; the cancellation result including which writing is accurate; the latitude-carrier control; the stationarity orders; the polar-axis domain fact; and that sequential and parallel agree.
