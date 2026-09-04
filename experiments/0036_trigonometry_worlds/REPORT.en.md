# ParseAtlas experiment 0036: sine in the twenty-five worlds

## Purpose

The answer this report opens with belongs to **question 3** and **question 4**: does
trigonometry survive under another convention, and who preserves most of it.

The Pythagorean identity, written as a string:

```text
s*s + c*c
```

Under our convention it equals `1` for every `x`. The measurement shows that **in `13` of the
`25` worlds it is still `1`** — `G0`, `G09`, `G10`, `G12`, `G13`, `G14`, `G15`, `G16`, `G17`, `G18`,
`G22`, `G23`, `G24`. In the remaining `12` the same string denotes `c*s*(c + s)`, that is
`sqrt(2)*sin(x)*sin(x + pi/4)*cos(x)` — not a constant, but a wave. So the Pythagorean
identity does **not** belong to our world; it belongs to the worlds in which `*`
binds more tightly than `+`.

Across all eight identities the most are preserved by **three worlds — `G0`, `G23` and `G24`, each
at `8/8`**. So the conventional world is indeed among the best, but it is **not uniquely
best**: `G23` (`/ * + -`) and `G24` (`/ * - +`) match it exactly.

The sharpest detail is this: the precedence order of `G17` is `* / + -` — **exactly the order of
`G0`**, but strict, with `*` and `/` on separate levels. `G17` preserves `7/8`. It loses
`1 + s/c*s/c = 1/cos(x)**2`, because for it the chain `s/c*s/c` associates as `s/(c*s)/c = 1/c**2`.
So in our world this identity is **not protected by the precedence order** — it is protected by the
**tie**: by the fact that `*` and `/` sit on the same level and the chain associates from the left.

## Three routes to sine

Sine is not defined once in mathematics. It is characterised by at least three **written forms**,
and the written form is precisely the object that is read differently under another convention.

```text
route 1   the series      "x - x*x*x/6 + x*x*x*x*x/120"   -> which polynomial is this here?
route 2   the composition sin(<inner token string>)       -> which wave is this here?
route 3   the identities  "s*s + c*c"  (s, c formal)      -> is this still 1 here?
```

All three describe the same sine in our world. **Elsewhere they do not agree**, and it is this
divergence that is the result of this experiment.

Route 3 uses placeholders because the Generation 1 language has no function-call syntax:
`sin(x)` cannot be tokenized in it as an application. The convention sensitivity of an identity lies
entirely at the argument level — in how `s*s + c*c` associates, and not in what `sin` means.
So the string is read with formal `s`, `c` (and `sa`, `ca`, `sb`, `cb`) placeholders, and the
substitution `s -> sin(x)`, `c -> cos(x)` happens only **after the reading**.

## Corpus

Route 1 — one string, the standard truncated Maclaurin series of sine. There is no `^`, so
powers are written as products — and this is precisely what makes the string convention-sensitive:

```text
x - x*x*x/6 + x*x*x*x*x/120
```

Declared sample points (fixed before the sweep): `0`, `pi/6`, `pi/4`, `pi/3`, `pi/2`,
`pi`, `2*pi`, `3`, `10`.

Route 2 — five inner token sequences, the first being the founding sequence of the project:

```text
2*t + 1 - t/2
t/2 + 1 - 2*t
3*t - 2 + 1
1 - 2*t/4 + 3*t
t*t - 3*t + 2
```

outer functions: `sin`, `cos`, `tan`. In total `5 * 3 * 25 = 375` readings.

Route 3 — eight identities, as argument-level strings:

| identity | string | target |
|---|---|---|
| `pythagorean` | `s*s + c*c` | `1` |
| `cofunction_zero` | `s*s + c*c - 1` | `0` |
| `double_angle_sine` | `2*s*c` | `sin(2*x)` |
| `double_angle_cosine` | `c*c - s*s` | `cos(2*x)` |
| `tangent` | `s/c` | `tan(x)` |
| `pythagorean_tangent` | `1 + s/c*s/c` | `1/cos(x)**2` |
| `angle_addition_sine` | `sa*cb + ca*sb` | `sin(a + b)` |
| `angle_addition_cosine` | `ca*cb - sa*sb` | `cos(a + b)` |

In total `8 * 25 = 200` readings.

Every object is grouped by the project semantic key — `(canonical form, domain, excluded points)`
— and **never by canonical text alone**.

## Observed results

### Route 3: which identities survive

`25` worlds x `8` identities. Rows are ordered by the number of identities preserved.

| world | precedence | pyth | cofunc | 2sc | cc-ss | s/c | 1+tan2 | sin(a+b) | cos(a+b) | kept |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---:|
| `G0` | `*/ +-` | yes | yes | yes | yes | yes | yes | yes | yes | `8` |
| `G23` | `/ * + -` | yes | yes | yes | yes | yes | yes | yes | yes | `8` |
| `G24` | `/ * - +` | yes | yes | yes | yes | yes | yes | yes | yes | `8` |
| `G13` | `* + - /` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G14` | `* + / -` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G15` | `* - + /` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G16` | `* - / +` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G17` | `* / + -` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G18` | `* / - +` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G12` | `- / * +` | yes | . | yes | . | yes | yes | yes | . | `5` |
| `G22` | `/ - * +` | yes | . | yes | . | yes | yes | yes | . | `5` |
| `G03` | `+ * - /` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G04` | `+ * / -` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G06` | `+ / * -` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G09` | `- * + /` | yes | . | yes | . | yes | . | yes | . | `4` |
| `G10` | `- * / +` | yes | . | yes | . | yes | . | yes | . | `4` |
| `G20` | `/ + * -` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G01` `G02` `G05` `G07` `G08` `G11` `G19` `G21` | (eight worlds) | . | . | yes | . | yes | . | . | . | `2` |

The observed structure:

- **`8/8` is preserved by exactly the three worlds in which `/` binds at least as tightly as `*`, and
  both bind more tightly than `+` and `-`**: `G0` (by the tie), `G23`, `G24`. This is the only configuration
  in which `s/c*s/c` associates as `(s/c)*(s/c) = s**2/c**2`.
- **`7/8` is preserved by exactly the six worlds in which `*` comes first** (`3! = 6` permutations): `G13`-`G18`.
  They lose only `1 + s/c*s/c`.
- `G12` and `G22` preserve `1 + s/c*s/c` (because for them `/` binds more tightly than `*`),
  but they lose `c*c - s*s` and `s*s + c*c - 1`, because for them `-` is stronger than `*`.
- **Two identities are convention-free**: `2*s*c` and `s/c` denote the same thing in all `25` worlds.
  Both use a single operator kind, so precedence has no effect on them. This was
  *predicted* before they were put into the corpus and the measurement confirmed it — they are a control and not a result.

The full picture for `pythagorean_tangent` (`5` semantic classes):

| class | denoted | substituted | holds | worlds |
|---|---|---|:-:|---|
| `I01` | `1 + s**2/c**2` | `cos(x)**(-2)` | yes | `G0` `G12` `G22` `G23` `G24` |
| `I02` | `(s + 1)/(c**2*s)` | `(1 + 1/sin(x))/cos(x)**2` | no | `G01` `G03` `G04` `G07` `G09` `G13` `G14` `G15` |
| `I03` | `s*(s + 1)/c**2` | `(sin(x) + 1)*sin(x)/cos(x)**2` | no | `G02` `G05` `G06` `G08` |
| `I04` | `1 + c**(-2)` | `tan(x)**2 + 2` | no | `G10` `G16` `G17` `G18` |
| `I05` | `s*(c + s)/c**2` | `(-sqrt(2)*cos(2*x + pi/4) + 1)/(2*cos(x)**2)` | no | `G11` `G19` `G20` `G21` |

`I04` is particularly pretty: after substitution, `1 + c**(-2)` is `tan(x)**2 + 2`. So in those
four worlds this string means not `sec**2` but `tan**2` **plus two** — a recognisable
trigonometric object, simply a different one.

### Route 1: the series

`25` world readings, **`14` semantic classes**, **`11` distinct canonical values**. The difference
`14 - 11 = 3` is exactly the result of the triple discipline: four classes denote **the same**
function (the constant `0`) and differ only by their validity restrictions.

| class | denoted | excl | odd (value) | odd (partial fn) | degree | `x -> +oo` | `x -> -oo` | worlds |
|---|---|---:|:-:|:-:|---|---|---|---|
| `S01` | `x**5/120 - x**3/6 + x` | `0` | yes | yes | `5` | `oo` | `-oo` | `G0` `G18` `G24` |
| `S02` | `0` | `2` | yes | no | - | `0` | `0` | `G01` `G07` |
| `S03` | `0` | `1` | yes | no | - | `0` | `0` | `G02` `G05` `G08` |
| `S04` | `(1 - x**2)/(120*x**3*(x + 6))` | `2` | no | no | `2/4` | `0` | `0` | `G03` |
| `S05` | `x - 1/(120*x*(x + 6))` | `2` | no | no | `3/2` | `oo` | `-oo` | `G04` |
| `S06` | `x*(-x**6 + 120*x + 720)/(120*(x + 6))` | `1` | no | no | `7/1` | `-oo` | `-oo` | `G06` |
| `S07` | `0` | `4` | yes | no | - | `0` | `0` | `G09` |
| `S08` | `x**5/120` | `0` | yes | yes | `5` | `oo` | `-oo` | `G10` `G12` `G22` |
| `S09` | `0` | `0` | yes | yes | - | `0` | `0` | `G11` `G19` `G21` |
| `S10` | `(-x**3 + x)/(120*x**5 + 720)` | `4` | no | no | `3/5` | `0` | `0` | `G13` `G15` |
| `S11` | `x*(120*x**5 - x**2 + 720)/(120*(x**5 + 6))` | `4` | no | no | `6/5` | `oo` | `-oo` | `G14` |
| `S12` | `x*(x**4 - 20*x**2 + 20)/120` | `0` | yes | yes | `5` | `oo` | `-oo` | `G16` |
| `S13` | `-x**5/120 - x**3/6 + x` | `0` | yes | yes | `5` | `-oo` | `oo` | `G17` `G23` |
| `S14` | `-7*x**7/720 + x` | `0` | yes | yes | `7` | `-oo` | `oo` | `G20` |

- **`9` of the `25` worlds read the series of sine as identically zero**: `G01`, `G02`, `G05`,
  `G07`, `G08`, `G09`, `G11`, `G19`, `G21`. The reason is structural — in those orderings `-` or `+`
  is stronger than `*`, so `x - x*x*x/6 + ...` groups `(x - x)` first and the whole product vanishes.
- **odd**: in `19` worlds the reading is odd as an expression (`f(-x) == -f(x)`); but only
  in `13` is it odd as a **partial function**. The difference is six worlds (`G01`, `G02`, `G05`,
  `G07`, `G08`, `G09`), which read `0` but carry a validity restriction at `-6`
  (or at the fifth root of `-6`) with no corresponding restriction at `+6`. Their domain is not
  symmetric under negation, so the definition of oddness does not apply to them.
- **roots**: `S01` has one real root (`{0}`), `S12` has five
  (`{0, ±sqrt(10 - 4*sqrt(5)), ±sqrt(4*sqrt(5) + 10)}`), `S14` has three, `S04` has two (`{-1, 1}`),
  and the root set of the nine zero-readings is `Reals`.
- **periodicity: `0` worlds, `G0` included**. This is measured and not assumed: the
  `sympy_periodicity` of every reading is either `None` (no period exists) or the sentinel `0`
  (a constant function — which has *every* period and therefore no fundamental period).
  The sentinel is returned by exactly the nine worlds that read `0`.

**Truncation error — `G0` without a discount.** A truncated series is a polynomial in **every** world,
in ours just as elsewhere; it is not periodic, and in the **non-constant** readings it is not bounded either. (`G11`, `G19`, `G21` read the string as the constant `0`, so they are bounded — the module correctly records them as `unbounded_on_reals = False`.)

| `x` | `0` | `pi/6` | `pi/4` | `pi/3` | `pi/2` | `pi` | `2*pi` | `3` | `10` |
|---|---|---|---|---|---|---|---|---|---|
| true `sin(x)` | `0.0000` | `0.5000` | `0.7071` | `0.8660` | `1.0000` | `0.0000` | `0.0000` | `0.1411` | `-0.5440` |
| `G0` | `0.0000` | `0.5000` | `0.7071` | `0.8663` | `1.0045` | `0.5240` | `46.5467` | `0.5250` | `676.6667` |
| `G17` | `0.0000` | `0.4993` | `0.7022` | `0.8453` | `0.8451` | `-4.5763` | `-116.6638` | `-3.5250` | `-990.0000` |
| `G20` | `0.0000` | `0.5235` | `0.7836` | `1.0338` | `1.3414` | `-26.2224` | `-3752.3039` | `-18.2625` | `-9.72e+04` |
| `G16` | `0.0000` | `0.0637` | `0.0526` | `-0.0064` | `-0.3045` | `-2.0939` | `41.3107` | `-1.9750` | `668.3333` |
| `G03` | undef | `0.0065` | `0.0010` | `-0.0001` | `-0.0004` | `-0.0003` | `-0.0001` | `-0.0003` | `-0.0001` |
| `G01` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` |

The absolute error of `G0` at the same points: `0`, `0.0000`, `0.0000`, `0.0003`, `0.0045`, **`0.5240`**,
**`46.5467`**, `0.3839`, **`677.2107`**.

If the error is split into two parts — near (`|x| <= pi/2`) and far (`pi`, `2*pi`, `3`, `10`) — the picture is
two-sided and both sides must be stated:

| world | max error near | max error far |
|---|---:|---:|
| `G0` `G18` `G24` | `0.00452` | `677.211` |
| `G17` `G23` | `0.15486` | `989.456` |
| `G20` | `0.34139` | `97211.678` |
| `G16` | `1.30447` | `668.877` |
| the nine zero-worlds | `1.0` | `0.544` |
| `G03` | `1.00042` | `0.544` |

- in the near zone the conventional reading is **genuinely and easily the best** - `0.0045` against
  `0.155` for the next best.
- in the far zone that same conventional reading is **in the upper middle and not the worst**: seven worlds are worse than it (`G20` `97212`, `G06` `5198`, `G17`/`G23` `990`, `G10`/`G12`/`G22` `834`). At `x = 10` its error
  is `677.21`, while the error of the world that simply reads the string as `0` is `0.544`.
  The reason is trivial and that is exactly why it is worth recording: `sin` is bounded, a quintic is not.
  This does not mean that `G01` "reads sine better"; it means that **the accuracy of the series
  route is nowhere, `G0` included, a property of sine.**

### Route 2: sine as an outer function

`5` inner sources x `25` worlds x `3` outer functions = `375` readings, all from
`parseatlas.functions.analyze_outer_functions` (the instrument corrected by NF-2026-00004).

The founding sequence `2*t + 1 - t/2`, outer `sin` — `8` semantic classes, exactly as in 0002:

| class | inner | `sin(inner)` | const | frequency | period | worlds |
|---|---|---|:-:|---|---|---|
| `O01` | `3*t/2 + 1` | `sin(3*t/2 + 1)` | no | `3/2` | `4*pi/3` | `G0` `G14` `G17` `G18` `G22` `G23` `G24` |
| `O02` | `1` | `sin(1)` | **yes** | `0` | undefined | `G01` `G02` `G07` `G08` |
| `O03` | `t/2 + 1` | `sin(t/2 + 1)` | no | `1/2` | `4*pi` | `G03` |
| `O04` | `3*t/2 + 2` | `sin(3*t/2 + 2)` | no | `3/2` | `4*pi/3` | `G04` `G06` `G20` |
| `O05` | `t + 2` | `sin(t + 2)` | no | `1` | `2*pi` | `G05` `G19` `G21` |
| `O06` | `t/2 + 1/2` | `sin(t/2 + 1/2)` | no | `1/2` | `4*pi` | `G09` `G13` `G15` |
| `O07` | `3*t/2 + 1/2` | `sin(3*t/2 + 1/2)` | no | `3/2` | `4*pi/3` | `G10` `G12` `G16` |
| `O08` | `t + 1` | `sin(t + 1)` | no | `1` | `2*pi` | `G11` |

The real domain is `Reals` for all eight classes; the zero sets are `Union`s of `ImageSet`s — for example
`4*n*pi/3 - 2/3 + {2*pi/3, 4*pi/3}` for `G0` and `4*n*pi - 2 + {2*pi, 4*pi}` for `G03` — while for
`O02` it is `EmptySet`, because the constant `sin(1)` never crosses zero.

**`4` worlds (`G01`, `G02`, `G07`, `G08`) — constant collapse.** For them, applying `sin` to this expression
does not give a wave but a fixed number. This is exactly the result of 0002 and it was re-measured here.

The `period` relation is untouched: `sin` and `cos` take `2*pi/|a|`, and `tan` takes `pi/|a|`.

| world | `a` | `sin` period | `cos` period | `tan` period |
|---|---|---|---|---|
| `G0` | `3/2` | `4*pi/3` | `4*pi/3` | `2*pi/3` |
| `G03` | `1/2` | `4*pi` | `4*pi` | `2*pi` |
| `G05` | `1` | `2*pi` | `2*pi` | `pi` |

This was verified independently: `functions.py` derives the period from the derivative of the argument,
while `sympy.calculus.util.periodicity` measures the composed function. **Disagreements over `375` readings: `0`.**

Summed over all five sources:

| inner source | `sin` semantic classes | constant collapse | wave | non-wave |
|---|---:|---|---:|---:|
| `2*t + 1 - t/2` | `8` | `G01` `G02` `G07` `G08` | `21` | `4` |
| `t/2 + 1 - 2*t` | `9` | `G01` `G07` | `13` | `12` |
| `3*t - 2 + 1` | `4` | - | `25` | `0` |
| `1 - 2*t/4 + 3*t` | `14` | `G01` `G04` `G07` | `9` | `16` |
| `t*t - 3*t + 2` | `5` | - | `0` | `25` |

- of the `125` `(source, world)` pairs, **the argument collapses to a constant in `9`**, and
  collapse is exhibited somewhere by five worlds in all: `G01`, `G02`, `G04`, `G07`, `G08`.
- of the `125`, **`68` are a genuine wave**; in the remaining `57` the value `sin(...)` is neither constant nor
  periodic — it is the sine of a quadratic or of a rational function.
- `t*t - 3*t + 2` **is a quadratic in all `25` worlds**, so applying `sin` to it gives a wave
  nowhere. This case is exactly what tests the periodicity guard across all `25` readings at once.
- `3*t - 2 + 1` is the opposite - no world breaks it: `4` classes, all four of the form `sin(3*t + b)`,
  frequency `3` everywhere. Only the phase `b` moves (`-1`, `-3`, `-5`, `-9`). So this shape
  is nearly rigid with respect to convention.

### The five headline answers

1. **How many different functions do the `25` worlds read in the series of sine?** `14` semantic classes
   under the `(canonical, domain, excluded points)` triple; `11` distinct canonical values if
   validity restrictions are ignored.
2. **In how many worlds does this reading remain odd?** `19` as an expression, `13` as a partial
   function (with the requirement of domain symmetry).
3. **Does the Pythagorean identity survive outside the conventional world?** Yes - in `12` other worlds:
   `G09`, `G10`, `G12`, `G13`, `G14`, `G15`, `G16`, `G17`, `G18`, `G22`, `G23`, `G24`.
4. **Who preserves the most identities, and is it `G0`?** `8/8` is preserved by three worlds - `G0`,
   `G23`, `G24`. `G0` is among the best, but not uniquely best.
5. **On the outer-function route, in how many worlds does the argument collapse to a constant?** On the founding
   sequence — `4`; over the `125` pairs from all five sources — `9`; collapse is exhibited somewhere by `5` worlds.

## Side-by-side: `G0`, `G16`, `G20`, `G01`

What sine **is** in these four worlds, along all three routes.

| | `G0` (`*/ +-`) | `G16` (`* - / +`) | `G20` (`/ + * -`) | `G01` (`+ - * /`) |
|---|---|---|---|---|
| **route 1** denoted | `x**5/120 - x**3/6 + x` | `x*(x**4 - 20*x**2 + 20)/120` | `-7*x**7/720 + x` | `0` |
| degree | `5` | `5` | `7` | - |
| odd (value / partial fn) | yes / yes | yes / yes | yes / yes | yes / **no** |
| real roots | `{0}` | `{0, ±sqrt(10-4*sqrt(5)), ±sqrt(4*sqrt(5)+10)}` | `{0, ±2**(2/3)*3**(1/3)*5**(1/6)*7**(5/6)/7}` | `Reals` |
| excluded points | none | none | none | `-6`, `0` |
| periodic | **no** | **no** | **no** | **no** |
| `x -> ±oo` | `+oo` / `-oo` | `+oo` / `-oo` | `-oo` / `+oo` | `0` / `0` |
| max error (near / far) | `0.0045` / `677.2` | `1.3045` / `668.9` | `0.3414` / `97211.7` | `1.0` / `0.544` |
| **route 2** inner | `3*t/2 + 1` | `3*t/2 + 1/2` | `3*t/2 + 2` | `1` |
| `sin(inner)` | `sin(3*t/2 + 1)` | `sin(3*t/2 + 1/2)` | `sin(3*t/2 + 2)` | `sin(1)` |
| constant argument | no | no | no | **yes** |
| frequency / period | `3/2` / `4*pi/3` | `3/2` / `4*pi/3` | `3/2` / `4*pi/3` | `0` / undefined |
| `tan` period | `2*pi/3` | `2*pi/3` | `2*pi/3` | undefined |
| real domain | `Reals` | `Reals` | `Reals` | `Reals` |
| **route 3** `s*s + c*c` | `1` | `1` | `sqrt(2)*sin(x)*sin(x+pi/4)*cos(x)` | `sqrt(2)*sin(x)*sin(x+pi/4)*cos(x)` |
| `c*c - s*s` | `cos(2*x)` | `cos(2*x)` | `cos(2*x)` | `sqrt(2)*sin(x)*cos(x)*cos(x+pi/4)` |
| `1 + s/c*s/c` | `cos(x)**(-2)` | `tan(x)**2 + 2` | `(-sqrt(2)*cos(2*x + pi/4) + 1)/(2*cos(x)**2)` | `(1 + 1/sin(x))/cos(x)**2` |
| identities kept | `8/8` | `7/8` | `4/8` | `2/8` |

How to read it:

- **`G0`** - all three routes agree as far as they can: the series is *that* truncation,
  the composition is a wave with a clean `2*pi/|a|` period, and all eight identities hold.
- **`G16`** - here too the series is of degree `5` and here too it is odd, i.e. a polynomial "of sine shape", but
  the coefficients are different (`x/6` rather than `x`), so in the near zone it is about
  three hundred times worse than `G0` (`1.3045` against `0.0045`).
  On identities, though, `G16` is almost `G0`: `7/8`.
- **`G20`** - the series is of degree `7` and is odd, so it looks like a *higher*-order approximation;
  in reality it is the worst far-zone reading in the whole atlas (error `97212` at `x = 10`).
  The composition is a healthy wave. On identities, `4/8`.
- **`G01`** - the series is `0`, the composition is the constant `sin(1)`, and of the identities only
  the two that cannot break in any world remain. In this world sine, on all three routes,
  **does not exist** as a recognisable object.

## Interpretation

The three routes describe the same sine in our world. Elsewhere they do not agree with each other,
and the shape of the divergence is consistent:

```text
route 2 (composition)  -- most robust: 116 of 125 pairs keep a live argument
route 3 (identities)   -- partly robust: 2 of the 8 identities break nowhere
route 1 (series)       -- most fragile: 9 of the 25 worlds read the string as zero
```

The reason is structural. In route 2 only the **argument** moves, while `sin` stays a genuine `sin`;
so it almost always yields something trigonometric. In route 3 the **association** moves,
so nothing happens to the identities that use a single operator kind, while the rest are affected.
In route 1 the **whole expression** moves, and since the series repeats the same variable many times
mixing `+`, `-`, `*` and `/`, it gives the convention the most room to intervene.

That is why route 3 is the sharpest form of the founding question in this domain. It shows that
the "self-evidence" of `sin**2 + cos**2 = 1` is in part **a property of the notation and not of
geometry alone**: in the `12` worlds where `+` is stronger than `*`, the same expression means a wave, and
the Pythagorean identity, to be written at all, would require parentheses — that is, it would be
**more expensive** there. In the terms of direction B of the ROADMAP: it would not be the parenthesis-free default there.

A second observation on the same line: the advantage of `G0` on identities **comes from the tie and not
from the order**. `G17` has exactly the order of `G0` and gets `7/8`; `G23`/`G24` have a different order and get
`8/8`. So what protects `1 + tan**2 = sec**2` is `*` and `/` standing on the same level
(or `/` binding tighter than `*`), and not the fact that `*` comes first. This connects directly with
the associativity axis of 0030: the space of conventions is not exhausted by precedence order.

Third — and this is a technical dividend rather than a mathematical one: this experiment found a class of
defect equivalent to NF-2026-00004, but in the printer rather than the parser. SymPy's `Union` and
`FiniteSet` keep their members in hash order, while Python randomizes string hashes per process;
as a result `str(continuous_domain(...))` **is a different string in the parent process and in a pool
worker**. A semantic key built on that string would be a function of the process rather than of the value.
The defect appeared precisely when the sweep was run in parallel: the `5` classes of
`1 + s/c*s/c` split into `6`. The fix is `_set_text`, which orders the members of a commutative
set constructor by their own rendered text. `sympy.core.sorting.default_sort_key` does **not** cut this
problem: it returns equal keys for the `ImageSet` members of the tangent domain, so `sorted` merely preserves
whatever hash order it was given.

## Multicore

The decision is **measured** and not assumed. Observed core count: `16`; worker count =
`min(cores - 2, 12, cells)` = `12`, so headroom remains for the interactive session.

Measured pool startup (spawn start, every worker importing sympy): `3.06 s` at `8`
workers, `3.49 s` at `12` workers on a warm filesystem cache, `~15 s` on the first, cold pool.
Hence `POOL_STARTUP_SECONDS = 4.0`.

| atlas | cells | sec/cell | sequential | pooled | decision |
|---|---:|---:|---:|---:|---|
| series | `25` | `0.14` | `3.45 s` | `9.04 s` | **sequential** |
| identity | `200` | `0.097` | `19.37 s` | `6.21 s` | **parallel** |
| outer, phase A (per world) | `375` | `0.065` | `24.20 s` | - | **parallel** |
| outer, phase B (per composition) | `117` | `0.07` | `~8 s` | - | **parallel** |
| outer, end-to-end | | | `~45 s` | `11.41 s` | **parallel** |

Two conclusions, both from the measurements:

- **The series atlas stays sequential.** It has only eight times fewer cells than the identity atlas and
  cells of almost the same cost, but `25 * 0.14 = 3.5 s` of work cannot pay for building the pool.
  Cell count alone cannot decide this; that is exactly why `should_parallelise` compares
  cost and not quantity.
- **The cell granularity of the outer route changed after measurement.** The initial `(source, function)`
  split gave `15` cells, one of which (`1 - 2*t/4 + 3*t` x `tan`) took `19.06 s` and
  held up the whole sweep — the parallel path finished in `59.98 s`, **slower** than sequential.
  With the `(source, function, world)` split there are `375` cells, the slowest is `2.35 s`, and the end-to-end
  time is `11.41 s`. The full report (all three routes) completes in `24.2 s`.

Parallelism changes nothing about *what* is measured: on all three atlases the sequential and parallel records
match completely, and this is fixed by a test rather than assumed.

## Limits

- **A truncated series is nowhere sine - `G0` included.** `x - x*x*x/6 + x*x*x*x*x/120` is a
  polynomial in every world: not periodic, and in the non-constant cases not bounded, running away as `x -> ±oo`. No line of this
  report says that some world "reads sine better"; they read different
  polynomials and their error is measured at the same nine declared points.
- **Route 3 uses placeholders and not a real function call.** The Generation 1 language has no
  function-call syntax. This model answers the question "would this identity be written the same way",
  and does **not** answer the question "what would trigonometric semantics look like". In particular, it touches
  neither the definition of angle, nor the choice of the radian, nor the link between the series and the circle.
- **This is a model and not a proof.** What is measured is what **today's standard written form**
  denotes under another convention. It is not a claim that trigonometry would have been built exactly this way
  in that convention — under another notation people would have written different strings.
  It is a model of *how it would have been built* and not a proof.
- The corpus is small: `1` series string, `5` inner sources, `8` identities. All three numbers bear directly
  on the results of this report; for example, `pythagorean_tangent` is the only identity in the corpus
  that mixes `*` and `/` in one chain, so the difference between `G0` and `G17` rests on **one**
  observation.
- There are nine sample points and `error` is taken as the maximum over them. This is not a norm and is not a general
  measure of approximation quality.
- `undefined_terms` solves the denominator over the complex plane, so the excluded-point sets
  contain complex points as well (`S07`, `S10`, `S11`). The domain symmetry for oddness is checked only on the real
  members, since only they restrict the domain of a real function.
- The excluded point `0` in route 3 means "the first denominator variable is zero" (`c = 0` or
  `c*s = 0`) — this is the convention of `parseatlas.canonical.undefined_terms` itself and it carried over
  unchanged here.

## Classification of evidence

- Every count, class, canonical form, root, period, domain, error and survival flag - **observed**,
  from executable output. None of them is derived from the expected behaviour of a grammar.
- `2*pi/|a|` for `sin`/`cos` and `pi/|a|` for `tan` on an affine argument - **symbolically justified**,
  and independently re-verified in this experiment with `sympy.calculus.util.periodicity`
  (`375` readings, `0` disagreements).
- "All six `*`-first worlds preserve `7/8`" and "all three worlds with `/ >= *` preserve `8/8`" -
  **observed structure** on these eight identities. It is not a general theorem over all classes
  of identities; before the corpus is extended it must not be read that way.
- The set-printing defect and its fix - **measured**: the same rendering run in eight independent
  interpreters, plus a sequential/parallel record-equality regression test.
- Every multicore timing figure - **measured** on this machine (`16` cores, CPython `3.14`,
  SymPy `1.14`). They are machine-specific and are an input to the decision rule, not its result.
- The general conclusion "convention X is better for mathematics" is **not drawn** from this experiment.
  This report does not answer the cost question of direction B; that belongs to direction A.

## Validation

```text
16 passed  # tests/test_trigonometry_worlds.py
21 passed  # + tests/test_outer_functions.py (the pinned results of 0002 are unchanged)
629 passed  # full suite (613 + 16), 426 s
```

Mutation testing (on an isolated copy of the working tree, `8` semantic mutants on `trigonometry_worlds.py`):
**`8/8` killed**. Killed were — accepting the constant sentinel of periodicity as a real period;
dropping the domain-symmetry requirement of oddness; removing the excluded-points slot from the
semantic key; replacing `_set_text` with SymPy's hash-ordered `str()`; always returning the identity verdict as
`True`; replacing the parallel decision by a cell-count threshold; masking the constant collapse;
returning the truncation error as zero.

On the first run the `set rendering` mutant **survived**: the determinism test at that time compared
two `Union` constructions inside one process, and `Union` canonicalizes its arguments at construction
anyway, so both gave the same object and the comparison was vacuous.
The test was rewritten so that it builds and compares the rendering in three separate interpreters with fixed
and differing `PYTHONHASHSEED` — after which the mutant died.

`tests/test_outer_functions.py::test_sine_reports_constant_collapse_and_period` (`tan` period
`2*pi` on `G03`, `sin` period `4*pi`, constant collapse on `G01`) is untouched and was additionally
re-measured from the pipeline of this experiment.

Reproduction:

```text
python -c "import json; from parseatlas.trigonometry_worlds import trigonometry_report; print(json.dumps(trigonometry_report()['answers'], indent=1))"
```
