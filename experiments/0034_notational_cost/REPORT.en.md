# ParseAtlas experiment 0034: notational cost of real mathematics

## Purpose

On a corpus of `58` named formulas the conventional grammar `G0` requires `53` parentheses, which puts it **in 11th place** among the 25 grammars (tied with `G03` and `G12`). This is the first direction B experiment: 0001-0033 took a fixed token string and asked what it *means* under each grammar; here the mathematical **object** is fixed — its intended tree — and what it *costs* to write it under each convention is measured.

```text
direction A   source string  --parse(g)-->   tree_g            (0001..0033)
direction B   intended tree  --render(g)-->  string, cost_g    (0034)
```

## 1. Where the conventional G0 stands

Across the whole corpus `G0` (`*/ +-`) pays `53` parenthesis pairs and stands `11`th of 25 in the ranking; ten grammars are cheaper than it, twelve are more expensive.

Rank is competition rank (`1, 2, 2, 4`) and the ties are genuine: `53` is also the total of `G03` and of `G12`.

## 2. The cheapest grammar

The cheapest is `G09` (`- * + /`) at `29` parentheses, which **beats `G0` by `24` parentheses, that is by `45.28%`**; the most expensive is `G20` (`/ + * -`) at `83`, so the whole spread is `54` parentheses.

The structure of `G09` states itself in one sentence: `-` binds tightest, `/` binds loosest. Both of these kill parentheses in the shape that occurs most often in the corpus — `(difference) / (difference)`:

```text
G0    (y2 - y1) / (x2 - x1)      cost 2
G09    y2 - y1 / x2 - x1         cost 0
```

The direction of the manager probe reproduces; its magnitude does not. On the ten formulas of the probe, `G0 = 7`, `G10 = 4`, `G06 = 15`; on this `58`-formula corpus `G0 = 53` (rank 11), `G10 = 39` (rank 4), `G06 = 73` (rank 22). In both measurements `G0` is not optimal, `G10` is cheaper than it, and `G06` sits near the worst — but on this corpus `G10` is not the cheapest; the cheapest is `G09`.

## 3. Ranking per area

The ranking is **not** uniform across areas: four areas are won by `G09`, physics prefers `G13`/`G15` (`* + - /` and `* - + /`), and statistics prefers `G14` (`* + / -`), so an area is free to choose its own convention.

| area | n | `G0` | `G0` rank | best | best grammars | worst |
|---|---|---|---|---|---|---|
| algebra | 10 | 11 | 11 | 7 | `G09` | 18 |
| arithmetic | 10 | 8 | 8 | 6 | `G09`, `G13`, `G15` | 11 |
| calculus | 9 | 8 | 12 | 4 | `G09`, `G10` | 13 |
| geometry | 9 | 10 | 17 | 2 | `G09` | 14 |
| physics | 11 | 5 | 8 | 2 | `G13`, `G15` | 12 |
| statistics | 9 | 11 | 8 | 6 | `G14` | 17 |

The weakest area for `G0` is geometry (rank `17`, `10` against a best of `2`) — precisely where nearly every formula is a fraction. Its strongest area is physics (rank `8`, `5` against a best of `2`), where five of the corpus formulas use a single operator type.

## 4. Convention sensitivity

Of the `58` formulas, `5` are convention-insensitive (`cylinder_volume`, `standard_error`, `density`, `work_done`, `ohm_series_resistance` — all of a single operator type and all of cost `0` in every grammar), while the most volatile are `distance_component_sum` (`(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)`, range `6`: from `0` to `6`) and `variance_of_two_points` (range `5`: from `2` to `7`).

```text
distance_component_sum
  G0    (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)              4
  G09    x2 - x1 * x2 - x1 + y2 - y1 * y2 - y1                     0
  G20   ((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1))          6
```

Range is a property of the mathematics and not of the convention: `distance_component_sum` mixes two operator levels in both directions, so every reordering touches it; `density` (`m / v`) uses one operator, and no precedence order can change its price.

`G0` matches the cheapest cost on `24` of the `58` formulas — on fewer than two thirds.

## 5. What would become parenthesis-free

In `G0`, `24` formulas are written without parentheses; in `G09`, `39`. In the move, `23` formulas become parenthesis-free and `8` lose that status.

Gained (free in `G09`, not in `G0`) — this is the mathematics that would be natural in that convention:

```text
average_velocity  circumference_over_diameter  correlation_coefficient  covariance_term
difference_quotient  distance_component_sum  fraction_sum_common_denominator
harmonic_mean_of_two  lens_equation_focal  linear_approximation  mean_of_three  mean_of_two
midpoint_coordinate  ohm_parallel_two  pooled_mean  quadratic_factored  regression_slope
riemann_rectangle_width  slope_through_two_points  taylor_second_term  voltage_divider
weighted_mean  z_score
```

Lost (free in `G0`, no longer in `G09`):

```text
confidence_interval_upper  difference_of_squares_expanded  harmonic_sum  mixed_number
newton_step  ohm_parallel_reciprocal  terminal_voltage  variance_shortcut
```

The trade is plain: `G09` buys every "big fraction" (slope, mean, z-score, weighted mean) and sells the reciprocal sum (`1 / a + 1 / b` becomes `(1 / a) + (1 / b)`) and the mixed term of the `a + b / c` type.

The prediction of the ROADMAP about the distributive law reproduces separately on `G01` (`+ - * /`), where `+` binds tightest:

```text
grammar   a * (b + c)       a * b + a * c         (a + b) * (a + b)
G0        a * (b + c)   1   a * b + a * c     0   (a + b) * (a + b)  2
G01       a * b + c     0   (a * b) + (a * c) 2   a + b * a + b      0
```

That is: in `G01` the factored form is the parenthesis-free default and the expanded form becomes expensive — the natural direction of the distributive law reverses.

## Null model

Part of the cost is forced rather than chosen, so it is accounted for separately, alongside the headline figures.

- Constant formulas (identical cost in all 25 grammars): `5` of `58`. All five have `support size = 1`, i.e. they are trees of a single operator type, which precedence reordering cannot touch; this is a direct consequence of the operator-support reduction of 0019.
- The forced total of those `5` formulas is `0` parentheses. They add nothing to any grammar.
- Consequently, recomputing on the movable subcorpus (`53` formulas) **changes the totals not at all**: the spread stays `54` (survival `100%`), the ranking is identical symbol for symbol, and the rank of `G0` is still `11`.

This means the ranking is not carried by the formulas that cannot move — but that is a property of this corpus and not a general law: a constant formula can have a non-zero constant cost too (`a - (b - c)` requires one parenthesis in every grammar, and is pinned separately in the test), and with such a corpus the forced total would be > 0.

A second null quantity: the per-formula oracle. If a convention could be chosen separately for each formula, the corpus would cost `3` parentheses; the best *single* grammar pays `29`. Those `26` parentheses are the price of having one global convention, not a shortcoming of `G09` — no grammar reaches it.

## Corpus

`58` named formulas across `6` areas, each entered as a source string in conventional notation, its intended tree obtained by parsing that string with `G0`, since `G0` is by definition the way we write today. The corpus is auditable: for every formula `render(parse(source, G0), G0) == source`, so there is no redundant parenthesis and no hidden intent in any source (`corpus_audit`, `test_corpus_is_auditable_named_mathematics`).

A coefficient sweep is deliberately absent here: the founding question is not about templates.

| formula | source (`G0`) | `G0` | `G09` | min | max |
|---|---|---|---|---|---|
| **algebra** | | | | | |
| `distributive_law_factored` | `a * (b + c)` | 1 | 1 | 0 | 1 |
| `distributive_law_expanded` | `a * b + a * c` | 0 | 0 | 0 | 2 |
| `binomial_square_factored` | `(a + b) * (a + b)` | 2 | 2 | 0 | 2 |
| `binomial_square_expanded` | `a * a + 2 * a * b + b * b` | 0 | 0 | 0 | 3 |
| `difference_of_squares_factored` | `(a + b) * (a - b)` | 2 | 1 | 0 | 2 |
| `difference_of_squares_expanded` | `a * a - b * b` | 0 | 2 | 0 | 2 |
| `difference_of_cubes_factored` | `(a - b) * (a * a + a * b + b * b)` | 2 | 1 | 1 | 4 |
| `quadratic_factored` | `a * (x - r) * (x - s)` | 2 | 0 | 0 | 2 |
| `quadratic_expanded` | `a * x * x + b * x + c` | 0 | 0 | 0 | 2 |
| `fraction_sum_common_denominator` | `(a * d + b * c) / (b * d)` | 2 | 0 | 0 | 4 |
| **arithmetic** | | | | | |
| `mean_of_two` | `(a + b) / 2` | 1 | 0 | 0 | 1 |
| `mean_of_three` | `(a + b + c) / 3` | 1 | 0 | 0 | 1 |
| `weighted_mean` | `(w1 * x1 + w2 * x2) / (w1 + w2)` | 2 | 0 | 0 | 4 |
| `harmonic_sum` | `1 / a + 1 / b` | 0 | 2 | 0 | 2 |
| `harmonic_mean_of_two` | `2 * a * b / (a + b)` | 1 | 0 | 0 | 2 |
| `percentage_change` | `(b - a) / a * 100` | 1 | 1 | 0 | 2 |
| `percentage_of` | `p * x / 100` | 0 | 0 | 0 | 1 |
| `compound_interest_two_periods` | `p * (1 + r) * (1 + r)` | 2 | 2 | 0 | 2 |
| `simple_interest_total` | `p + p * r * t` | 0 | 0 | 0 | 1 |
| `mixed_number` | `a + b / c` | 0 | 1 | 0 | 1 |
| **geometry** | | | | | |
| `slope_through_two_points` | `(y2 - y1) / (x2 - x1)` | 2 | 0 | 0 | 2 |
| `distance_component_sum` | `(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)` | 4 | 0 | 0 | 6 |
| `midpoint_coordinate` | `(x1 + x2) / 2` | 1 | 0 | 0 | 1 |
| `trapezoid_area` | `(a + b) / 2 * h` | 1 | 1 | 0 | 2 |
| `triangle_area` | `b * h / 2` | 0 | 0 | 0 | 1 |
| `rectangle_perimeter` | `2 * (w + h)` | 1 | 1 | 0 | 1 |
| `circumference_over_diameter` | `2 * pi * r / (2 * r)` | 1 | 0 | 0 | 2 |
| `cylinder_volume` | `pi * r * r * h` | 0 | 0 | 0 | 0 |
| `cone_volume` | `pi * r * r * h / 3` | 0 | 0 | 0 | 1 |
| **calculus** | | | | | |
| `difference_quotient` | `(fxh - fx) / h` | 1 | 0 | 0 | 1 |
| `linear_approximation` | `fa + m * (x - a)` | 1 | 0 | 0 | 2 |
| `taylor_second_term` | `c2 * (x - a) * (x - a) / 2` | 2 | 0 | 0 | 3 |
| `product_rule` | `du * v + u * dv` | 0 | 0 | 0 | 2 |
| `quotient_rule` | `(du * v - u * dv) / (v * v)` | 2 | 2 | 0 | 4 |
| `newton_step` | `x - fx / dfx` | 0 | 1 | 0 | 1 |
| `derivative_of_quadratic` | `2 * a * x + b` | 0 | 0 | 0 | 1 |
| `riemann_rectangle_width` | `(b - a) / n` | 1 | 0 | 0 | 1 |
| `trapezoid_rule_term` | `(f1 + f2) * h / 2` | 1 | 1 | 0 | 2 |
| **statistics** | | | | | |
| `variance_shortcut` | `q / n - m * m` | 0 | 2 | 0 | 2 |
| `variance_of_two_points` | `(x1 * x1 + x2 * x2) / 2 - (x1 + x2) / 2 * ((x1 + x2) / 2)` | 4 | 4 | 2 | 7 |
| `z_score` | `(x - m) / s` | 1 | 0 | 0 | 1 |
| `standard_error` | `s / rootn` | 0 | 0 | 0 | 0 |
| `confidence_interval_upper` | `m + z * s / rootn` | 0 | 1 | 0 | 2 |
| `covariance_term` | `(x - mx) * (y - my) / n` | 2 | 0 | 0 | 3 |
| `correlation_coefficient` | `sxy / (sx * sy)` | 1 | 0 | 0 | 1 |
| `regression_slope` | `sxy / (sx * sx)` | 1 | 0 | 0 | 1 |
| `pooled_mean` | `(n1 * m1 + n2 * m2) / (n1 + n2)` | 2 | 0 | 0 | 4 |
| **physics** | | | | | |
| `kinetic_energy` | `m * v * v / 2` | 0 | 0 | 0 | 1 |
| `density` | `m / v` | 0 | 0 | 0 | 0 |
| `average_velocity` | `(x2 - x1) / (t2 - t1)` | 2 | 0 | 0 | 2 |
| `total_momentum` | `m1 * v1 + m2 * v2` | 0 | 0 | 0 | 2 |
| `work_done` | `f * d * costheta` | 0 | 0 | 0 | 0 |
| `ohm_series_resistance` | `r1 + r2 + r3` | 0 | 0 | 0 | 0 |
| `ohm_parallel_two` | `r1 * r2 / (r1 + r2)` | 1 | 0 | 0 | 2 |
| `ohm_parallel_reciprocal` | `1 / r1 + 1 / r2` | 0 | 2 | 0 | 2 |
| `lens_equation_focal` | `u * v / (u + v)` | 1 | 0 | 0 | 2 |
| `voltage_divider` | `vin * r2 / (r1 + r2)` | 1 | 0 | 0 | 2 |
| `terminal_voltage` | `emf - i * r` | 0 | 1 | 0 | 1 |

## Observed results

Full ranking, `25` grammars, `58` formulas:

| rank | grammar | precedence | total | free formulas | vs `G0` |
|---|---|---|---|---|---|
| 1 | `G09` | `- * + /` | 29 | 39 | -24 |
| 2 | `G13` | `* + - /` | 35 | 37 | -18 |
| 2 | `G15` | `* - + /` | 35 | 37 | -18 |
| 4 | `G10` | `- * / +` | 39 | 33 | -14 |
| 5 | `G14` | `* + / -` | 41 | 33 | -12 |
| 6 | `G16` | `* - / +` | 45 | 31 | -8 |
| 7 | `G01` | `+ - * /` | 47 | 33 | -6 |
| 7 | `G07` | `- + * /` | 47 | 33 | -6 |
| 9 | `G17` | `* / + -` | 51 | 27 | -2 |
| 9 | `G18` | `* / - +` | 51 | 27 | -2 |
| 11 | **`G0`** | **`*/ +-`** | **53** | **24** | **0** |
| 11 | `G03` | `+ * - /` | 53 | 32 | 0 |
| 11 | `G12` | `- / * +` | 53 | 24 | 0 |
| 14 | `G04` | `+ * / -` | 59 | 28 | +6 |
| 14 | `G22` | `/ - * +` | 59 | 19 | +6 |
| 16 | `G02` | `+ - / *` | 61 | 21 | +8 |
| 16 | `G08` | `- + / *` | 61 | 21 | +8 |
| 18 | `G23` | `/ * + -` | 65 | 19 | +12 |
| 18 | `G24` | `/ * - +` | 65 | 19 | +12 |
| 20 | `G05` | `+ / - *` | 67 | 16 | +14 |
| 21 | `G11` | `- / + *` | 71 | 20 | +18 |
| 22 | `G06` | `+ / * -` | 73 | 17 | +20 |
| 23 | `G19` | `/ + - *` | 77 | 15 | +24 |
| 23 | `G21` | `/ - + *` | 77 | 15 | +24 |
| 25 | `G20` | `/ + * -` | 83 | 16 | +30 |

Correctness bridge and minimality:

```text
round-trip checks (58 formulas x 25 grammars)   1450
round-trip failures                                0
brackets emitted and re-checked                 1397
brackets that could be removed                     0
```

Round trip is `parse(render(tree, g), g) == tree`, and it is checked **on the production path**, not only in the tests: `render` reparses its own output and raises `RoundTripError` on a mismatch. Minimality is checked by construction: every bracket pair of a rendering is deleted in turn, and the result must parse to a *different* tree (or fail to parse at all).

The bracket rule is not a hardcoded table. Binding power is read entirely from `Grammar.levels`, and the threshold is literally two numbers in the parser: `Parser._expression` accepts an operator at `>= minimum_power` and parses the right operand at `power(operator) + 1`, so the threshold for a left child is `parent_power` and for a right child `parent_power + 1`. That is exactly why the same code works on the tied control grammar too, where `power("*") == power("/")` and `a * b / c` is free while `a / (b * c)` is not.

Sequential-versus-parallel measurement (16 cores, `repeats = 5`, minimum-of-runs):

```text
sequential                 0.0273 s
parallel (16 processes)    0.3885 s
speedup                    0.070x   ->  sequential 14.2x faster
identical results          True
```

The workload is `1450` string renders in pure Python; the spawn cost of the process pool exceeds it by nearly an order of magnitude. `resolve_worker_count` derives from the observed number of cores and returns `1` for fewer than `PARALLEL_MINIMUM_ITEMS = 256` items, so the default path is sequential — **on the basis of a measurement and not of an assumption**. The parallel path exists, is covered by a test, and `workers=1` vs `workers=2` returns an identical structure.

## Interpretation

The instruments of direction A ("what does a string mean") proved sufficient to assemble direction B ("what does an object cost"): the same `Grammar`, the same `Parser`, run in the opposite direction.

The answer to the first half of the founding question — is the convention we inherited any good — is, on this corpus: **not optimal, but not bad either**. `G0` sits in the middle of the ranking (11/25), stands at `44%` of the spread, and is `45%` more expensive than the cheapest. `G0` is indeed the only grammar that uses tied levels, but **that tie buys nothing here**. The review measured it: `a * b / c` and `a + b - c` are both free **in six strict orderings as well** — `G01`, `G03`, `G04`, `G13`, `G14`, `G17` — that is, in any ordering where `*` precedes `/` and `+` precedes `-`. Among them `G17` (`* / + -`) is the strict twin of `G0` itself, and it **stands 9th in the ranking, cheaper than `G0`**.

(An earlier edition of this paragraph asserted that "a strict ordering always costs one of them". That was **false** and credited the conventional grammar with an advantage it does not have. Corrected after review.)

The reason `G09` wins is structural and depends on the corpus: making `/` the weakest operator strips two parentheses off every big fraction, and making `-` bind tightest frees the differences. In the corpus, `slope`, `mean`, `z-score`, `weighted mean`, `pooled mean`, `difference quotient` are all of this shape. This is not an artefact: fractions of differences really are common in school and engineering mathematics. But it is a property of the corpus, and a different corpus — one loaded with reciprocals and series, say — would punish `G09`: `harmonic_sum` and `ohm_parallel_reciprocal` are more expensive in it than in `G0`.

The per-area breakdown confirms this directly: `G0` serves geometry worst (rank 17), where almost everything is a fraction, and physics almost as well as any other grammar, where half the formulas are of a single operator type.

```text
convention  ->  which shapes are free  ->  which mathematics is cheap to write
```

## Limits

- Parenthesis count is **one** measure of notational cost and not the only one. Reading difficulty, ambiguity in handwriting, visual grouping, difficulty of teaching - none of these is measured here. Two renderings with the same parenthesis count can be radically different in reading load.
- The corpus is hand-picked and therefore reflects what this project takes to be representative mathematics. `58` formulas in `6` areas is not a sample from any defined population; its auditability (every source is published and is minimal in `G0`) makes it checkable, not representative.
- The Generation 1 language has no unary minus and no exponentiation. Those two are precisely the most contested places for precedence in real notation (`-x^2`, the right-associativity of `a^b^c`), and they lie outside this measurement. Squares are written as products (`v * v`), which raises the share of `*` in the corpus.
- Associativity is fixed to left for every operator here, because that is what the parser does. The associativity space of 0030 widens this axis, but it does not take part in this experiment.
- Cost is counted in bracket **pairs**. A character count would not give a different ranking with this renderer (every bracket is in a pair), but that is a choice and not a theorem.
- Some formulas of the corpus repeat the same shape in different areas (`slope_through_two_points` and `average_velocity` are identical trees). This is deliberate - the same shape really does recur across areas - but it means the per-area totals are not fully independent.
- And the main one: a cheap convention on this corpus is **not an argument that mathematics should have adopted it**. This is only a measurement of what it would have cost. These numbers take no account of history, teaching, typography or inertia.

## Classification of evidence

- The rank `11` of `G0`, cheapest `G09 = 29`, worst `G20 = 83`, spread `54`, free counts `24 -> 39` - all of this is executable **observation** on this `58`-formula corpus and these `25` grammars.
- Round trip (`1450/1450`) and minimality (`1397` brackets, `0` removable) are **verified properties** on that same grid and not a proof over all trees. The derivation of the bracket rule from the parser is an **argument**, and its evidence is the completeness of the grid plus mutation testing.
- Per-area ranking and convention sensitivity are **corpus-conditional structure** and not universal law. The change of area winner (`G09` vs `G13`/`G15` vs `G14`) depends on the area composition of this corpus.
- The null-model accounting (`5` constant formulas, forced total `0`, spread survival `100%`, oracle gap `26`) is **observation** on this corpus; "a constant formula always means zero cost" is **not** claimed, and a counter-example is pinned directly in the test.
- The answer to the founding question is not claimed as a general theorem. What is claimed is that direction B is measurable, has been measured, and that on this corpus `G0` is not optimal.

## Validation

```text
593 passed
```

New tests: `tests/test_notational_cost.py`, `41` tests.

Mutation testing on an isolated copy (tree copied into the scratchpad; canonical repository untouched), `12` mutants at the decisive points of `notational_cost.py`:

```text
right threshold loses the +1                KILLED
left threshold gains a +1                   KILLED
bracket test becomes non-strict (< -> <=)   KILLED
left child rendered with the right rule     KILLED
right child rendered with the left rule     KILLED
binding powers inverted                     KILLED
leaves are bracketed too                    KILLED
round-trip guard disabled                   KILLED
competition ranking becomes positional      KILLED
operator support only walks the left spine  KILLED
constant detection off by one               KILLED
cost counts one bracket too few             KILLED

killed 12/12
```

`operator support only walks the left spine` survived the first run; the test `test_tree_operators_walks_both_subtrees` was added and the mutant died.
