# ParseAtlas experiment 0035: alternative mathematics in 25 worlds

## Purpose

A direct answer to the founding question of the project: **had people agreed on a different operator order, they would have built mathematics according to that order, and so the objects themselves would have been different.**

The argument is notational, not philosophical. A mathematician always writes the simplest notation available, and what counts as *simple* depends on the notation. `a*x*x + b*x + c` is the standard polynomial precisely because it is cheap to write under conventional precedence. Under another convention **the same written form denotes a different object**, and it is that object that would have been studied, named and built upon. So for each standard written form we can read off what that object actually is in each world.

The worlds are the `4! = 24` strict precedence orderings plus the conventional tied-level control `G0`, `25` in all.

## Catalogue

`26` standard written forms, each given as `(name, area, written form, principal variable)` in `src/parseatlas/alternative_mathematics.py::STANDARD_CATALOGUE`. It covers algebra (linear, quadratic, cubic, monic quadratic, vertex form, difference of squares, binomial square, sum of cubes, distributive law, linear combination), geometry (Pythagorean form, law of cosines form, circle form, slope form, triangle area), analysis (sine/cosine/exponential truncated series, geometric sum) and arithmetic (mean of two, mean of three, arithmetic progression, compound interest, Fahrenheit form, harmonic form, rate form).

Objects are compared by the existing **semantic key** of the project — `(canonical expression, domain, excluded points)` — the same triple used by `analyze_expression` and by `corpus_matrix.expression_classes`. Two worlds read the same object only when they agree on all three; canonical text is never the key on its own.

One disclosure about that key: `parseatlas/canonical.py` writes the literal `"R"` into `domain` for every expression, so the **operative discrimination is `(canonical form, excluded points)`**, and `domain` is a fixed declaration of the analysis setting rather than a measured component. The triple is used here exactly as the project defines it; only the wording of the guarantee is made precise. This is the repository-wide `NF-2026-00005`, and it is pinned by a test (`test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement`) and by an expected mutation-testing survivor (see Validation).

## Observed results

### 1. Standard quadratic

**`a*x*x + b*x + c` produces exactly `2` genuinely distinct objects across the `25` worlds: in `13` worlds it is `a*x**2 + b*x + c`, degree `2`, roots `(-b +- sqrt(b**2 - 4*a*c))/(2*a)`, and in `12` worlds it is `a*x*(b + x)*(c + x)`, degree `3`, roots `[0, -b, -c]` — already factored and free of radicals.**

| object | grammars | canonical | degree | roots | discriminant | vertex |
|---|---|---|---|---|---|---|
| `O01` | `13` | `a*x**2 + b*x + c` | `2` | `(-b - sqrt(-4*a*c + b**2))/(2*a)`, `(-b + sqrt(-4*a*c + b**2))/(2*a)` | `-4*a*c + b**2` | `x = -b/(2*a)`, `y = c - b**2/(4*a)` |
| `O02` | `12` | `a*x*(b + x)*(c + x)` | `3` | `0`, `-b`, `-c` | does not exist | does not exist |

```text
O01: G0, G09, G10, G12, G13, G14, G15, G16, G17, G18, G22, G23, G24
O02: G01, G02, G03, G04, G05, G06, G07, G08, G11, G19, G20, G21
```

### 2. Root convention: roots over `C`

**Every root list in this module is the complete multiset over `C`, and this is stated explicitly everywhere a root list or `requires_radical` is printed: in the module docstring, in the record of `solution_formula` (`root_domain`, `root_convention`), on the textbook page, and beneath the heading of the rendered table.**

This section exists because an earlier version of this report mixed two different conventions without saying a word. `parseatlas.canonical.to_sympy` builds symbols with `real=True`; `solve` then returns **all** complex roots when the coefficients are free symbols, and **only real** roots when they are numbers. Two different notions of "root" stood on the same page at once.

On the page of the conventional world, two entries said what is not taught:

| written form | denotes | old page | the truth over `C` |
|---|---|---|---|
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | roots `-1`, radical `no`, "roots read straight off the factorisation" | `-1, -I, I`, radical `yes` |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | roots `0`, radical `no` | `5` roots, `4` of them complex, radical `yes` |

From the factorisation `(r + 1)*(r**2 + 1)` the root `-1` really can be read off, but `+-I` cannot — so the sentence that the roots "read straight off the factorisation" was false on that page. On the same page `a*a*a + b*b*b` was already printing `b*(1/2 - sqrt(3)*I/2)`: the convention was not even self-consistent within a single page.

A sweep over `25` worlds x `26` entries = `650` pages, comparing the old and the new behaviour directly:

```text
pages with a short root list (multiplicity sum < degree)          22
    geometric_sum 13 | sine_series 6 | cosine_series 3
    of these, requires_radical=False only because of dropped roots   16
pages where the root list changed                                 30
requires_radical False -> True                                    21
    by restoring dropped roots                                     16
    only because `I` now counts as a radical                        5
requires_radical True -> False                                     0
short root lists under the new convention                          0
```

**Why `C` and not "real only":** a real-only convention is not implementable. With symbolic coefficients the realness of a root is undecidable — whether `sqrt(-4*a*c + b**2)` is real depends on `a`, `b`, `c` — so real-only cannot be enforced uniformly even in principle. `C` is the only convention that means the same thing on all `650` pages.

`I` counts as a radical for the same reason `sqrt(2)` does: `I` **is** a square root, the one that must be adjoined to a real-coefficient world for a complex root to be writable at all. This affects `5` pages — `exponential_series` in `G09`, `G13`, `G14`, `G15`, and `cosine_series` in `G14` — which printed a complete root list but with `radical: no`. All four are rational readings, so they have no polynomial degree and the completeness check could never have caught them.

**Detector.** The old `multiplicity_complete` was a false assurance: it compared SymPy's *internal* `roots()` table against the degree rather than the list the textbook prints, so it returned `True` in exactly the cases where the printed list was short (`True` next to `1` of `3` roots on `G0`/`geometric_sum`). It has been replaced by `root_list_is_complete`, which compares the **printed** list against the degree, is surfaced in `world_object`, `solution_formula`, `textbook` and the rendered table, and is pinned by a test. A rational reading or a zero reading has no degree, so the answer there is `None` and not a silent `True`. An incomplete page gets its own method label (`degree N: INCOMPLETE - ...`) and is marked in the table with `**INCOMPLETE: k/N**`.

Measurement under the new convention: `0` of `650` pages with a short root list.

Real-line statements are kept separate and are marked as such by name: `profile` (parity, boundedness, growth, periodicity, real poles) and the `real_zeros` / `real_poles` / `real_removable_restrictions` readings describe the object as a function of a **real** variable; that is a different question from where its roots live.

### 3. Where a radical is needed at all

**Solving the standard quadratic requires a radical in `13` of the `25` worlds; in the remaining `12` the roots are direct negations of the coefficients, and there is neither a discriminant nor a square root.**

More broadly, over the whole catalogue: in `8` worlds (`G01`, `G02`, `G05`, `G07`, `G08`, `G11`, `G19`, `G21`) **not one** standard form requires a radical. In `G0`, `12` of `26` do, and that is the maximum, which `G0` shares with `6` further worlds.

| world | precedence | radical pages / 26 |
|---|---|---|
| `G01`, `G02`, `G05`, `G07`, `G08`, `G11`, `G19`, `G21` | various | `0` |
| `G03` | `+ > * > - > /` | `2` |
| `G04`, `G06`, `G20` | various | `4` |
| `G09` | `- > * > + > /` | `9` |
| `G10`, `G12`, `G13`, `G15`, `G22` | various | `10` |
| **`G0`**, `G14`, `G16`, `G17`, `G18`, `G23`, `G24` | `*=/ > +=-` and `6` others | `12` |

All of these counts are higher than in the previous version of this report, and the reason is entirely the correction of section `2`: `21` pages moved `requires_radical` from `False` to `True` (`16` by restoring dropped complex roots, `5` because `I` counts as a radical), and none moved from `True` to `False`. The `8` radical-free worlds are unchanged — none of them had either a short root list or a page containing `I`.

It is worth noting that after the correction `G0` is at the maximum rather than in the middle. This does not make `G0` an outlier: `6` further worlds stand at the same `12`, and the answer to question `6` (twins, worldview count) is unchanged.

### 4. Convention-independent core

**Of the `26` catalogue entries, `4` are identical in all `25` worlds: `a*(b + c)` (distributive law), `b*h/2` (triangle area), `p*r*t/100` (compound interest), `d/t` (rate form).**

These entries leave no operator ambiguity: they are either fully parenthesized or a uniform `*`/`/` chain, where a precedence permutation does not change the parse tree. The remaining `22` entries fracture.

### 5. The most fractured object

**The most convention-dependent objects are the truncated series: `1 - x*x/2 + x*x*x*x/24` and `x - x*x*x/6 + x*x*x*x*x/120` each produce `14` genuinely distinct objects across the `25` worlds — the catalogue maximum.**

| entry | distinct objects |
|---|---|
| `1 - x*x/2 + x*x*x*x/24` (cosine series) | `14` |
| `x - x*x*x/6 + x*x*x*x*x/120` (sine series) | `14` |
| `1 + x + x*x/2 + x*x*x/6` (exponential series) | `5` |
| `x*x + y*y - r*r`, `a*a + b*b - c*c`, `a*a + b*b - 2*a*b*c` | `4` |
| `9*c/5 + 32` | `3` |
| the remaining `15` fractured entries | `2` |

The reason is mechanical: the series have the most mixed operators (`+`, `-`, `*`, `/` in one expression, all four precedence positions active), so a permutation yields the most distinct parse trees.

The work done by the semantic key is directly visible on the sine series: the `14` distinct objects correspond to only `11` canonical texts, because `4` different world-groups read `0` **with different excluded points** (`[]`, `[-6]`, `[-6, 0]`, and the fourth with the roots of `x**5 + 6`). Comparison on canonical text alone would merge those `4` objects into one and count `11` instead of `14`.

### 6. Is `G0` special

**No: on this catalogue `G0` is a measurably ordinary member. It has two complete twins — `G18` (`* > / > - > +`) and `G24` (`/ > * > - > +`) — which read all `26` of `26` entries exactly as `G0` does, and `G0` stands alone on no entry.**

The group size of `G0` per entry: `25` (the invariant entries), `13` (most of algebra and arithmetic), `9` (Pythagorean/circle/law-of-cosines/exponential/Fahrenheit), `3` (the sine and cosine series). The minimum of `3` is exactly `{G0, G18, G24}`.

Agreement with `G0`, out of `26` entries:

```text
G0  26   G01  4   G02  4   G03  5   G04  6   G05  5   G06  6   G07  4   G08  4
G09 14   G10 19   G11  7   G12 19   G13 18   G14 19   G15 18   G16 23   G17 24
G18 26   G19  8   G20  9   G21  8   G22 20   G23 24   G24 26
```

Over the whole catalogue the `25` worlds produce only `17` distinct worldviews (a worldview = which object the grammar selects on each entry):

```text
3  G0, G18, G24
2  G01, G07 | G02, G08 | G10, G12 | G13, G15 | G17, G23 | G19, G21
1  G03 | G04 | G05 | G06 | G09 | G11 | G14 | G16 | G20 | G22
```

### Truncated series: what function each reading is

The `4` series entries yield `35` distinct readings. Of those, **`0` are periodic — in no world, `G0` included**. This is neither a slight against the conventional world nor a distinction for it: a truncated series is a polynomial or a rational function in **every** world, and none of them is periodic. The reading of `G0`, `x**5/120 - x**3/6 + x`, is an odd quintic, unbounded (`lim -> +oo` and `-oo`), with `0` as its only **real** root (over `C` there are `4` further complex roots — see section `2`). It resembles `sin(x)` only on a small interval, and that is the whole truth about it.

SymPy assigns period `0` to a constant function; the module records this but does **not** count it as periodic, because a constant is degenerate rather than oscillating.

Boundedness, on the other hand, really does differ — and in an interesting direction:

| entry | reading | grammars | parity | bounded | periodic |
|---|---|---|---|---|---|
| sine series | `x**5/120 - x**3/6 + x` | `G0`, `G18`, `G24` | odd | **no** | no |
| sine series | `0` | `G02`, `G05`, `G08` (and `3` other groups) | odd and even | yes | no (period `0`, constant) |
| sine series | `-7*x**7/720 + x` | `G20` | odd | no | no |
| cosine series | `x**4/24 - x**2/2 + 1` | `G0`, `G18`, `G24` | even | **no** | no |
| cosine series | `(x**4 - x**2/24 + 2)/(x**4 + 2)` | `G14` | even | **yes** | no |
| cosine series | `(1 - x**2)/(24*(x**4 + 2))` | `G13`, `G15` | even | **yes** | no |

Of the `35` readings, `7` are bounded, across `13` grammars in total. That is, in the world of `G14` the form `1 - x*x/2 + x*x*x*x/24` is a **bounded even function with limit `1` in both directions and no real poles** — qualitatively closer to the globally bounded character of `cos` than our own truncation is. This does not mean it is `cos`; it is still not periodic.

### A few other measured results

- `a + b/2` is `a + b/2` (`13` worlds) or `a/2 + b/2` = **the genuine arithmetic mean of two numbers** (`12` worlds). Likewise `a + b + c/3` -> `a/3 + b/3 + c/3`.
- `y - w/x - v` is a rational function with a pole at `x = 0` (`13` worlds) or `(w - y)/(v - x)` (`12` worlds) - that is, **the formula for the slope between two points**.
- `9*c/5 + 32` is the Fahrenheit conversion (`9` worlds), `9*c/37` (`12` worlds) or `9*c/5 + 288` (`4` worlds).
- `a*a + 2*a*b + b*b` is `(a + b)**2` (`13` worlds) or `2*a**2*b**2*(a + 2)` (`12` worlds) - the binomial square no longer exists.
- `a*x*x*x + b*x*x + c*x + d`: in `13` worlds it needs the cubic formula, in `12` worlds it is a degree-`6` object with roots `[0, -b, -c, -d]` and no radical.
- `1/a + 1/b` is `(a + b)/(a*b)` (`13` worlds) or `1/(b*(a + 1))` (`12` worlds).
- `1 + r + r*r + r*r*r` is `r**3 + r**2 + r + 1` with roots `-1, -I, I` (`13` worlds, a radical is needed) or `r**3*(4*r + 2)` of degree `4` with roots `-1/2, 0` (`12` worlds, no radical). This is precisely the entry that had a short root list in `13` worlds before the correction.

## Textbook pages

Below are `4` complete generated pages. The root column is over `C`, as section `2` states, and each table repeats this beneath its own heading. The column is elided only when the root expression exceeds `80` characters (the general cubic formula is `967` characters); an elided cell states the root count and the elision explicitly. A page with a short root list would be marked `**INCOMPLETE: k/N**` — there is no such page among these `4` (nor among all `650`).

### World `G0` — precedence `*=/ > +=-`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*x + b` | 1 | `-b/a` | no | one linear step |
| `a*x*x + b*x + c` | `a*x**2 + b*x + c` | 2 | `(-b - sqrt(-4*a*c + b**2))/(2*a), (-b + sqrt(-4*a*c + b**2))/(2*a)` | yes | quadratic formula: discriminant, then a square root |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3 + b*x**2 + c*x + d` | 3 | 3 roots, 967 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `x*x + b*x + c` | `b*x + c + x**2` | 2 | `-b/2 - sqrt(b**2 - 4*c)/2, -b/2 + sqrt(b**2 - 4*c)/2` | yes | quadratic formula: discriminant, then a square root |
| `a*(x - h)*(x - h) + k` | `a*(h - x)**2 + k` | 2 | `h - sqrt(-a*k)/a, h + sqrt(-a*k)/a` | yes | quadratic formula: discriminant, then a square root |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `a**2 + 2*a*b + b**2` | 2 | `-b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a*a + b*b*b` | `a**3 + b**3` | 3 | `-b, b*(1/2 - sqrt(3)*I/2), b*(1/2 + sqrt(3)*I/2)` | yes | degree 3: a radical or an unsolvable root object is required |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*x + b*y` | 1 | `-b*y/a` | no | one linear step |
| `a*a + b*b - c*c` | `a**2 + b**2 - c**2` | 2 | `-sqrt(-b**2 + c**2), sqrt(-b**2 + c**2)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a**2 - 2*a*b*c + b**2` | 2 | `b*(c - sqrt(c**2 - 1)), b*(c + sqrt(c**2 - 1))` | yes | quadratic formula: discriminant, then a square root |
| `x*x + y*y - r*r` | `-r**2 + x**2 + y**2` | 2 | `-sqrt((r - y)*(r + y)), sqrt((r - y)*(r + y))` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | 5 | 5 roots, 359 chars (elided) | yes | degree 5: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `x**4/24 - x**2/2 + 1` | 4 | 4 roots, 84 chars (elided) | yes | degree 4: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3/6 + x**2/2 + x + 1` | 3 | 3 roots, 272 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | 3 | `-1, -I, I` | yes | degree 3: a radical or an unsolvable root object is required |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `a + d*n` | 1 | `-a/d` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 32` | 1 | `-160/9` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `12/26`, polynomial pages `24`, pages with an incomplete root list `0`.

### World `G01` — precedence `+ > - > * > /`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*(b + x)` | 1 | `-b` | no | one linear step |
| `a*x*x + b*x + c` | `a*x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3*(b + x)*(c + x)*(d + x)` | 6 | `0, -b, -c, -d` | no | degree 6: 4 distinct roots over C, multiplicities summing to 6, read straight off the factorisation, no radical |
| `x*x + b*x + c` | `x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(x - h)*(x - h) + k` | `-a*(h - x)*(-h + k + x)` | 2 | `h, h - k` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a - b*b` | `a*b*(a - b)` | 2 | `0, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `2*a**2*b**2*(a + 2)` | 3 | `-2, 0` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*a*a + b*b*b` | `a**2*b**2*(a + b)` | 3 | `0, -b` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*y*(b + x)` | 1 | `-b` | no | one linear step |
| `a*a + b*b - c*c` | `a*c*(a + b)*(b - c)` | 2 | `0, -b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + b*b - 2*a*b*c` | `a**2*b*c*(a + b)*(b - 2)` | 3 | `0, -b` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `x*x + y*y - r*r` | `-r*x*(r - y)*(x + y)` | 2 | `0, -y` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `y - w/x - v` | `(w - y)/(v - x)` | - | none | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `0` | - | none | no | no equation to solve: the reading carries no power of the variable |
| `1 - x*x/2 + x*x*x*x/24` | `(1 - x)/(24*x**2*(x + 2))` | - | `1` | no | rational over C: solve the numerator, then discard the poles |
| `1 + x + x*x/2 + x*x*x/6` | `(2*x + 1)/(6*x*(x + 2))` | - | `-1/2` | no | rational over C: solve the numerator, then discard the poles |
| `1 + r + r*r + r*r*r` | `r**3*(4*r + 2)` | 4 | `-1/2, 0` | no | degree 4: 2 distinct roots over C, multiplicities summing to 4, read straight off the factorisation, no radical |
| `a + b/2` | `a/2 + b/2` | 1 | `-b` | no | one linear step |
| `a + b + c/3` | `a/3 + b/3 + c/3` | 1 | `-b - c` | no | one linear step |
| `a + n*d` | `d*(a + n)` | 1 | `-a` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/37` | 1 | `0` | no | one linear step |
| `1/a + 1/b` | `1/(b*(a + 1))` | - | none | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `0/26`, polynomial pages `22`, pages with an incomplete root list `0`.

### World `G20` — precedence `/ > + > * > -`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*(b + x)` | 1 | `-b` | no | one linear step |
| `a*x*x + b*x + c` | `a*x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3*(b + x)*(c + x)*(d + x)` | 6 | `0, -b, -c, -d` | no | degree 6: 4 distinct roots over C, multiplicities summing to 6, read straight off the factorisation, no radical |
| `x*x + b*x + c` | `x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(x - h)*(x - h) + k` | `-a*(h - x)*(-h + k + x)` | 2 | `h, h - k` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `2*a**2*b**2*(a + 2)` | 3 | `-2, 0` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*a*a + b*b*b` | `a**2*b**2*(a + b)` | 3 | `0, -b` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*y*(b + x)` | 1 | `-b` | no | one linear step |
| `a*a + b*b - c*c` | `a*b*(a + b) - c**2` | 2 | `(-b**2 - sqrt(b*(b**3 + 4*c**2)))/(2*b), (-b**2 + sqrt(b*(b**3 + 4*c**2)))/(2*b)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a*b*(a + b - 2*c)` | 2 | `0, -b + 2*c` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `x*x + y*y - r*r` | `-r**2 + x*y*(x + y)` | 2 | `(-y**2 - sqrt(y*(4*r**2 + y**3)))/(2*y), (-y**2 + sqrt(y*(4*r**2 + y**3)))/(2*y)` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `-7*x**7/720 + x` | 7 | 7 roots, 382 chars (elided) | yes | degree 7: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `1 - x**5/16` | 5 | 5 roots, 284 chars (elided) | yes | degree 5: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3*(2*x + 1)/4` | 4 | `-1/2, 0` | no | degree 4: 2 distinct roots over C, multiplicities summing to 4, read straight off the factorisation, no radical |
| `1 + r + r*r + r*r*r` | `r**3*(4*r + 2)` | 4 | `-1/2, 0` | no | degree 4: 2 distinct roots over C, multiplicities summing to 4, read straight off the factorisation, no radical |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `d*(a + n)` | 1 | `-a` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 288` | 1 | `-160` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `4/26`, polynomial pages `24`, pages with an incomplete root list `0`.

### World `G24` — precedence `/ > * > - > +`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*x + b` | 1 | `-b/a` | no | one linear step |
| `a*x*x + b*x + c` | `a*x**2 + b*x + c` | 2 | `(-b - sqrt(-4*a*c + b**2))/(2*a), (-b + sqrt(-4*a*c + b**2))/(2*a)` | yes | quadratic formula: discriminant, then a square root |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3 + b*x**2 + c*x + d` | 3 | 3 roots, 967 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `x*x + b*x + c` | `b*x + c + x**2` | 2 | `-b/2 - sqrt(b**2 - 4*c)/2, -b/2 + sqrt(b**2 - 4*c)/2` | yes | quadratic formula: discriminant, then a square root |
| `a*(x - h)*(x - h) + k` | `a*(h - x)**2 + k` | 2 | `h - sqrt(-a*k)/a, h + sqrt(-a*k)/a` | yes | quadratic formula: discriminant, then a square root |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `a**2 + 2*a*b + b**2` | 2 | `-b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a*a + b*b*b` | `a**3 + b**3` | 3 | `-b, b*(1/2 - sqrt(3)*I/2), b*(1/2 + sqrt(3)*I/2)` | yes | degree 3: a radical or an unsolvable root object is required |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*x + b*y` | 1 | `-b*y/a` | no | one linear step |
| `a*a + b*b - c*c` | `a**2 + b**2 - c**2` | 2 | `-sqrt(-b**2 + c**2), sqrt(-b**2 + c**2)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a**2 - 2*a*b*c + b**2` | 2 | `b*(c - sqrt(c**2 - 1)), b*(c + sqrt(c**2 - 1))` | yes | quadratic formula: discriminant, then a square root |
| `x*x + y*y - r*r` | `-r**2 + x**2 + y**2` | 2 | `-sqrt((r - y)*(r + y)), sqrt((r - y)*(r + y))` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | 5 | 5 roots, 359 chars (elided) | yes | degree 5: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `x**4/24 - x**2/2 + 1` | 4 | 4 roots, 84 chars (elided) | yes | degree 4: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3/6 + x**2/2 + x + 1` | 3 | 3 roots, 272 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | 3 | `-1, -I, I` | yes | degree 3: a radical or an unsolvable root object is required |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `a + d*n` | 1 | `-a/d` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 32` | 1 | `-160/9` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `12/26`, polynomial pages `24`, pages with an incomplete root list `0`.

The pages of `G0` and `G24` are identical cell by cell on this catalogue, even though their precedence is entirely different (`*=/ > +=-` vs `/ > * > - > +`). This is the visual form of the answer to question `6`.

## Multicore

Repository policy is multicore by default, by a measured decision. The work unit is a single catalogue entry (`26` of them), which is fully independent and runs CPU-bound SymPy, so a `ProcessPoolExecutor` is used, with `resolve_worker_count` giving `cpu_count - 1` workers (`15` on this host, `16` cores), leaving one core of headroom for the interactive session.

Three separate measurements follow. They were taken under different conditions and are not interchangeable; the conditions of each are stated with it.

**Measurement A — `parallelism_measurement`, full `26`-entry catalogue, `25` grammars, `3` independent runs, each in a clean interpreter:**

```text
run   sequential_s   parallel_s   speedup   workers   identical_results
 1       68.00          20.96       3.24       15          true
 2       60.92          22.29       2.73       15          true
 3       57.76          18.61       3.10       15          true

cpu_count 16 | item_count 26 | automatic_worker_count 15 | faster_path: parallel (3/3)
```

Parallel wins on all three runs, so the default is parallel. The speedup is `2.73 - 3.24`, not `15`.

**Measurement B — per-entry decomposition with a cold SymPy cache.** Each entry was run in its own process (`max_tasks_per_child=1`), i.e. exactly under the conditions a pool worker faces, and the time was taken from inside the process, excluding spawn and import:

```text
cold total (26 entries)           71.99 s
slowest entry     sine_series      20.18 s
total / slowest                     3.57
```

`sine_series` is an indivisible unit — the pool cannot split it — so parallel wall clock cannot fall below the scale of its cost. The parallel wall clock of measurement A (`18.61 - 22.29 s`) sits right around this `20.18 s`, and the measured speedup (`2.73 - 3.24`) lies below the decomposition ceiling of B (`3.57`). The two measurements agree with each other.

**Measurement C — why the speedup figure has a spread.** The per-entry cost is not a stable quantity. Within one and the same process, a second sequential pass is `1.6` times faster than the first, because SymPy memoises between entries:

```text
                    round 1    round 2
sequential total    79.95 s    50.12 s
sine_series         18.24 s     6.93 s
parallel (launched from the same process)   23.62 s   25.08 s
```

The sequential path uses this shared cache; the `15` separate processes of the pool cannot. That is why the sequential total drifts within `50 - 80 s`, while the parallel wall clock sits far more tightly within `18.61 - 25.08 s` across all measurements taken together. The speedup is the ratio of the two, so the spread follows it, and it is quoted here as measured rather than as a single "pretty" number.

The startup of the pool itself was measured separately (`15` workers, spawn start method, `26` idle items): `1.35 s`.

Parallelism changes only speed — `identical_results` checks this directly by comparing object ids, canonical forms, grammar lists and roots rather than by assumption; on all three runs it is `true`.

## Interpretation

The answer to the founding question, in one sentence: **in roughly half of the worlds the quadratic formula would not exist at all.**

In `12` worlds `a*x*x + b*x + c` is an already-factored cubic whose roots `[0, -b, -c]` are read straight off the coefficients. In those worlds nobody would write a discriminant, nobody would introduce `sqrt(b**2 - 4*a*c)` for this form, nobody would memorise `(-b +- sqrt(D))/(2*a)`. In `8` worlds **not one** of the `26` standard forms of the catalogue requires a radical.

This does not mean that quadratic equations would not exist in those worlds. It means that **the standard form would be different**: the mathematician would still write the simplest notation, and in that world that notation would come out as a different object. It is that object that would have become the opening chapter of the textbook.

On the other hand, there is a genuine convention-independent core: fully parenthesized or uniform operator chains (`a*(b + c)`, `b*h/2`, `p*r*t/100`, `d/t`) are identical in all `25` worlds. Notation does not decide everything — it decides where mixed operators raise the question of precedence.

And finally, `G0` is not privileged. It has two complete twins, the `25` worlds produce only `17` worldviews, and `G0` stands alone on no catalogue entry. In this measurement the conventional order is an ordinary member and not an outlier.

The one dimension where `G0` turned out to be at the edge after the correction of the root convention is the radical page count: `12/26` is the catalogue maximum. But `6` further worlds stand at the same `12` (`G14`, `G16`, `G17`, `G18`, `G23`, `G24`), so this too is a group property and not a property of `G0`. Before the correction `G0` appeared at `10` in this column and the maximum was thought to be `11` — both numbers were artefacts of dropped complex roots.

```text
written form -> grammar -> object -> solving procedure
```

## Limits

- **This is a model, not a proof.** What is measured is what the standard **written forms** denote under other conventions. It is a model of how mathematics would have been built, not a proof that it would have been built exactly so. In real history notation and objects developed together; here the notation is fixed and only the precedence varies.
- **A truncated series is a polynomial in every world, ours included.** `x - x*x*x/6 + x*x*x*x*x/120` is a quintic and not `sin`. No reading is periodic, `G0` included. The genuine properties of `sin` (periodicity, boundedness) are entirely out of reach for the Generation 1 grammar of this project, since the tokenizer has neither transcendental functions nor infinite series.
- **The catalogue is hand-chosen.** The `26` entries reflect a judgement about what counts as standard. A different choice would give a different ratio of invariant to fractured. Specifically, three of the `4` invariant entries were added deliberately to test whether an invariant core exists at all - this is not a random sample.
- **The bounds of the Generation 1 grammar.** Four binary operators, no unary minus, no exponentiation, every operator left-associative. `a*x*x` is the only expressible form of `x**2`; in a grammar with `**` the question would be posed differently.
- **The principal variable is chosen.** Each entry has one principal variable declared in the catalogue (e.g. `a` for `a*a - b*b`). A different choice would change the degree and the roots.
- **Root ordering and form belong to SymPy.** `solve` and `factor` return a particular representation; `-sqrt((r - y)*(r + y))` and `-sqrt(r**2 - y**2)` are the same thing but differ under string comparison. Hence object identity rests on the semantic key and not on root strings. The same applies to the form of complex roots: the four complex roots of the quintic of `G0` are printed trigonometrically (`15**(1/4)*2**(3/4)*cos(atan(sqrt(5)/5)/2) +- ...`), while the same numbers can also be written as `+-sqrt(10 +- 2*sqrt(5)*I)`. The **set** of roots is a convention and is measured; the **form** in which they are written is SymPy's choice.
- **`root_list_is_complete` rests on degree.** It works where the reading has a polynomial degree. Rational readings and zero readings have no degree, so the answer there is `None`: this is not a concealed `True`, but it is not a guarantee either. Counting `I` as a radical catches exactly those `5` rational pages that a degree-based check could not catch.
- **`domain` is inert in the semantic key** (`NF-2026-00005`). The triple `(canonical, domain, excluded points)` belongs to the project and is used here unchanged, but `canonical.py` always sets `domain` to `"R"`, so the effective discrimination has two components. None of the counts of this experiment changes because of it - the `14` distinct sine-series objects against `11` canonical texts are separated by excluded points and not by domain - but the guarantee should be stated as it is.
- **The speedup was measured on one host** (`16` cores, Windows, spawn start method). On another host the number will differ; the decision must be re-measured and not copied over.

## Classification of evidence

- **Observations** (executable, reproducible in this repository): the `2` objects of the quadratic and their `13`/`12` split, the requirement of a radical in `13` worlds, the `4` invariant entries, the `14` distinct readings of the series, `0` periodic readings, `17` distinct worldviews, the twins `G18` and `G24` of `G0`, the per-world radical page counts, the root-convention sweep (`22` short pages under the old convention, `0` under the new; `21` radical flips), and the multicore timings.
- **Interpretation** (derived from the measurements rather than measured): the claim that the mathematicians of those worlds would have built **these** objects. That is a notational-cost argument, not a measurement.
- **Not claimed**: that the conventional order is better or worse; that any universal law over the `24 + 1` worlds exists; that the catalogue is a representative sample of mathematics as a whole; that any world's reading is `sin`, `cos` or `exp`.

## Validation

```text
638 passed
```

`tests/test_alternative_mathematics.py`: `28 passed`. Among them: both groups of the quadratic pinned (with grammar lists, degree, discriminant, vertex and roots), the membership of `G0` in the degree-`2` group, a pin on the convention-independent objects, a check of `textbook(G0)` on three familiar entries, the non-periodicity of the sine series in all `25` worlds, the necessity of the semantic key in place of canonical text, and sequential/parallel identity.

`9` tests added for the root convention:

```text
test_every_root_list_declares_the_domain_it_was_solved_over
test_control_geometric_sum_page_reports_all_three_roots
test_control_sine_series_page_reports_all_five_roots
test_no_world_reports_a_root_list_short_of_its_degree
test_the_series_pages_of_the_control_world_are_complete_and_all_need_a_radical
test_the_completeness_check_compares_the_printed_list_not_sympys_table
test_an_incomplete_root_list_is_flagged_wherever_it_would_be_printed
test_radical_detection_counts_the_imaginary_unit
test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement
```

`test_no_world_reports_a_root_list_short_of_its_degree` is the test that closes the silent return of this defect: it reads `geometric_sum` in all `25` worlds (that was the entry which was short in `13` worlds, and all `25` of its readings have a polynomial degree, so the comparison always has something to compare) and requires `roots_complete is True` everywhere. Since no measured page is now short, the operation of the flag itself is proved separately: `root_list_is_complete` is tested directly on a short list (`False`), on an exact list (`True`) and without a degree (`None`), while on a constructed short page it is checked that `render_textbook` prints `INCOMPLETE: 1/3` and that `_solution_method` does **not** issue a confident label.

Mutation testing was carried out on an **isolated copy** (the repository was not touched): `src/parseatlas` and the test file were copied into a scratch tree and each mutation was run separately.

```text
BASELINE                                                            28 passed
KILLED   roots solved with the real symbol again (the defect of this card)
KILLED   completeness compared against SymPy's internal table, not the printed list
KILLED   radical detection stops counting the imaginary unit
KILLED   the printed convention line is dropped from the rendered table
KILLED   a short root list is rendered without its marker
KILLED   an incomplete list still gets a confident method label
KILLED   radical detection inverted
KILLED   semantic key drops excluded points
KILLED   constants counted as periodic
KILLED   worker count loses the core headroom
KILLED   object groups ordered smallest first
KILLED   degree 2 always reported as needing the quadratic formula
KILLED   boundedness ignores real poles
KILLED   discriminant reported for every polynomial degree
KILLED   the domain component of the key is silently dropped ("R" -> "CONSTANT")
SURVIVED (expected) domain replaced by the constant it always is ("R" -> "R")

15/16 mutants killed
```

The single survivor is deliberate and is the evidence for NF-2026-00005: replacing `canonical["domain"]` by the literal `"R"` leaves all `28` tests green, because `domain` really never varies. The mutant standing next to it, which replaces `domain` by a **different** value, dies — so the field is indeed read, it simply discriminates nothing.

Of the `8` mutants of the previous wave, `4` survived the first run and targeted assertions were added for them at that time; this time all were re-run and are dead again.
