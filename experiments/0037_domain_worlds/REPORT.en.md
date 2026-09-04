# ParseAtlas experiment 0037: domain worlds and the compromise test

## The result in one sentence

**The conventional `G0` stands 3rd of 25 over the whole mathematical workload (`45` parentheses against the best `42`), is first in two of the four fields, and is never below 6th — so it is a very good compromise, but not the optimum: two grammars beat it.**

## Purpose

`0034` placed `G0` **11th** of 25 by notational cost. `0036` placed the same `G0` **in the top three** by preservation of trigonometric identities. Neither experiment was built for this, and both pointed at the same suspicion:

> Is there a grammar that beats `G0` over the **whole** mathematical workload — or did our convention survive because it is **a good compromise across many fields** rather than the optimum in any one of them?

A convention that is average everywhere and best nowhere would look exactly like `G0` has looked so far. This card settles that.

## Corpus

**Named laws, not generated templates.** What a convention does to the distributive law is a historical question; what it does to a selected template is not.

```text
laws          33        entries       48        two-sided laws   15
fields         4        duplicates     0        canonical sources ✓
```

| field | laws | entries | two-sided |
|---|---|---|---|
| algebra | 8 | 16 | 8 |
| geometry | 11 | 15 | 1 |
| calculus | 8 | 11 | 3 |
| linear_algebra | 6 | 6 | 3 |

`canonical_sources: True` means that every source string is already the minimal rendering in the control grammar — that is, no entry brings in a parenthesis that would distort its own cost.

Generation 1 has no exponentiation and no function call, so several entries use stand-in leaves (`fx` = `f(x)`, `fxh` = `f(x + h)`, `dfa` = `f'(a)` and so on). All stand-ins are listed in the module docstring.

## Correctness bridge

Every cost figure rests on these two properties, and they are checked first:

```text
round-trip   1200 checks       0 failures
minimality   1737 parentheses  0 violations
```

A rendering that does not return to its own tree measures nothing; a rendering with a redundant parenthesis **inflates the total of that grammar and may invert the ranking**. Both are excluded.

## Observed results

### 1. The full ranking

| rank | id | precedence | algebra | geometry | calculus | linear alg. | mean | worst | total |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `G18` | `* / - +` | 1 | 3 | 1 | 1 | 1.5 | 3 | **42** ✅ |
| 2 | `G16` | `* - / +` | 1 | 3 | 6 | 1 | 2.75 | 6 | 44 |
| **3** | **`G0`** | `*/ +-` | **1** | 5 | 6 | **1** | **3.25** | **6** | **45** |
| 3 | `G10` | `- * / +` | 10 | 1 | 1 | 10 | 5.5 | 10 | 45 |
| 5 | `G15` | `* - + /` | 1 | 7 | 6 | 1 | 3.75 | 7 | 46 |
| 5 | `G17` | `* / + -` | 6 | 5 | 4 | 1 | 4.0 | 6 | 46 |
| 7 | `G09` | `- * + /` | 10 | 2 | 1 | 10 | 5.75 | 10 | 47 |
| 8 | `G14` | `* + / -` | 6 | 8 | 4 | 1 | 4.75 | 8 | 48 |
| 9 | `G13` | `* + - /` | 6 | 8 | 9 | 1 | 6.0 | 9 | 50 |
| 10 | `G24` | `/ * - +` | 1 | 12 | 12 | 1 | 6.5 | 12 | 57 |
| 11 | `G22` | `/ - * +` | 10 | 10 | 9 | 10 | 9.75 | 10 | 58 |
| 12 | `G12` | `- / * +` | 10 | 10 | 12 | 10 | 10.5 | 12 | 60 |
| 13 | `G23` | `/ * + -` | 6 | 14 | 16 | 1 | 9.25 | 16 | 61 |
| 14 | `G07` | `- + * /` | 18 | 12 | 11 | 18 | 14.75 | 18 | 80 |
| 15 | `G04` | `+ * / -` | 14 | 16 | 12 | 14 | 14.0 | 16 | 81 |
| 16 | `G03` | `+ * - /` | 14 | 16 | 17 | 14 | 15.25 | 17 | 83 |
| 17 | `G01` | `+ - * /` | 22 | 14 | 12 | 18 | 16.5 | 22 | 84 |
| 18 | `G21` | `/ - + *` | 18 | 18 | 17 | 18 | 17.75 | 18 | 91 |
| 19 | `G11` | `- / + *` | 18 | 18 | 21 | 18 | 18.75 | 21 | 93 |
| 20 | `G20` | `/ + * -` | 14 | 24 | 23 | 14 | 18.75 | 24 | 94 |
| 21 | `G08` | `- + / *` | 18 | 21 | 21 | 18 | 19.5 | 21 | 95 |
| 21 | `G19` | `/ + - *` | 22 | 20 | 19 | 18 | 19.75 | 22 | 95 |
| 23 | `G06` | `+ / * -` | 14 | 25 | 23 | 14 | 19.0 | 25 | 96 |
| 24 | `G05` | `+ / - *` | 22 | 22 | 19 | 18 | 20.25 | 22 | 97 |
| 25 | `G02` | `+ - / *` | 22 | 22 | 23 | 18 | 21.25 | 23 | 99 |

### 2. Only two grammars beat `G0`

```text
G18   * / - +     42    margin 3    -6.67%
G16   * - / +     44    margin 1    -2.22%
G0    */ +-       45
```

The worst, `G02`, pays `99` — **2.2 times more than `G0`**. So `G0` sits at the top edge of the distribution and not in the middle.

### 3. The best all-rounder is `G0` with one tie broken

`G18` is the only grammar that is **in the top 3 in all four fields**: mean rank `1.5`, worst rank `3`, first in three fields of four.

And its precedence is:

```text
G18   * / - +          strict
G0    (* /) (+ -)      tied
```

**This is not a rearrangement of our convention — it is the same grouping, with the tie between `+` and `-` broken in favour of `-`.**

### 4. No grammar wins in every field

```text
algebra          G0, G15, G16, G18, G24      (tie)
geometry         G10                          (the only outright winner)
calculus         G09, G10, G18
linear_algebra   tie, G0 inside it
──────────────────────────────────────────────────────
winner in every field:       none
G0 wins:                     algebra, linear_algebra
```

`winners_differ: True`, `grammars_winning_every_field: ()`. So **the field champions differ** — this is a routing result seen from the notational side.

### 5. The natural direction of a law reverses

Of the `15` two-sided laws, **`13` reverse direction somewhere**, and **`22` of the 25 worlds** have at least one reversal. `152` reversal cells in total.

The most striking case is the distributive law:

| grammar | factored | expanded | natural |
|---|---|---|---|
| `G0` | 2 | **0** | **expanding** |
| `G01` | **0** | 2 | **factoring** |

**In `G01` the free step of algebra is factoring; with us it is expanding.** That world would have built algebra in the opposite direction: for it, factorisation would be the primitive and expansion the derived operation.

`per_grammar["G0"] == ()` — in our convention, by definition, no law is reversed.

## Null model

An entry that uses a single operator type costs the same in every grammar and therefore **cannot carry the ranking**.

```text
constant entries          2
single-operator entries   1
all_field_ranks_stable    True
all_control_ranks_stable  True
```

Excluding those entries **changes no field rank and no control rank**. So the ranking measures conventions and not the corpus.

## Interpretation

**1. The compromise hypothesis is partly confirmed and partly refuted.**

`G0` is **not** merely "average everywhere": it is first in two fields of four and 3rd overall. But it is **not the optimum** either — `G18` beats it on every measure.

The correct description is: **a very strong compromise, very close to the optimum, but not the optimum.**

**2. The discrepancy with `0034` is apparent, and it is informative.**

In `0034` `G0` was 11th over 58 formulas; here it is 3rd over 48 entries. The difference lies in the corpus: `0034` measured mixed practical formulas (slope, mean, compound interest), whereas this card measures **fundamental laws**. **`G0` is better on laws than on everyday formulas** — which most likely reflects that the convention took shape around the writing of laws.

**3. The result for `G18` is historically interesting.**

The best all-round convention differs from ours by **one decision**: the breaking of the tie between `+` and `-`. We made them equal; `G18` binds `-` more tightly. This is not a radically different mathematics — **it is the same mathematics with one fewer conventional choice.**

## Limits

- **The corpus is hand-picked** and reflects a judgement about which laws are fundamental. A different choice would shift the ranking.
- **Parenthesis count is one measure among several.** Reading difficulty, ambiguity in handwriting, the precedence of unary minus and of exponentiation - all of that is outside it.
- **Generation 1 has no exponentiation and no function call**, so several entries use stand-in leaves. Where and which - listed.
- **A cheaper convention on this corpus is not an argument that mathematics should have adopted it.** This is a measurement of what it would have cost - not a recommendation.
- **The `domain` component of the semantic key is inert** (`NF-2026-00005`): `canonical.py` writes `"R"` for every expression, so the operative discrimination is `canonical form` + `excluded points`.
- **Negative results carry a scale.** "No grammar wins in every field" means *over these four fields, with this corpus, under the parenthesis measure* - and not in general.

## Classification of evidence

- ranking, field ranks, totals, orientation counts - **OBSERVED**, measured by execution.
- round-trip and minimality - **OBSERVED**, checked over the full corpus.
- the stability of the null model - **OBSERVED**.
- "`G0` is a compromise and not the optimum" - **OBSERVED** on this corpus.
- "the convention took shape around the laws" - **HYPOTHESIS**. The difference between `0034` and this card is consistent with that explanation but does not establish it.

## Validation

```text
python -m pytest -q tests/test_domain_worlds.py     16 passed
```

The headline numbers are pinned literally rather than recomputed from the module, so a change in the ranking **will fail the test** rather than pass silently.
