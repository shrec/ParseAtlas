# ParseAtlas experiment 0039: what it would cost us to see the invisible 46

## Purpose

**The full parenthesization space — `1510820` trees over the `50` declared writings of this corpus — makes
exactly `1` of the `46` invisible `(object, property)` pairs of 0038 manifest, and `45` remain; and that
one turned out to be precedence-reachable, so it is a defect report against the model of 0038 and not a gain from a
wider space — which means that of those 46, `0` require a tree that precedence cannot write.**

The diagnosis of the card named two different causes, and this experiment measures what each of them buys.
The answer splits into three, and all three are measured separately:

```text
search space   the full parenthesization space (Part 1)        1 pair     measurement
language       Generation 1 has no radical and no i (Part 2)   8 pairs    requirement analysis
rules          neither the space nor the language (Part 3)    37 pairs    measurement + argument
                                                              ----------
                                                              46
```

**Part 2 is an analysis of what would have been needed, and not a measurement of rendering.** This belongs in the first section and
not in the limits, because this is precisely where this project could have made the same mistake a third time.
No number in Part 2 says that a property **is visible**; they say that the writing that
would expose it **has no existence at all** in this operator set. In Part 3, where the writing does exist, it is
genuinely **written, rendered and checked** — all 18 witnesses are given as strings and
the imported rules really do fire on them; a witness that does not fire is printed as `failing` and is not
silently dropped.

### One correction with respect to 0038: `80` does not reproduce

The card states that the best single world makes `80` of the 46 manifest. **From the table of 0038 itself
this number does not come out.** The per-world total of true-and-manifest pairs is at its maximum
**`77`** (`G0` and `G17` together), which agrees exactly with the per-world manifest total published by 0038
for `G0`. Other readings were checked too: counting cells — `77`; the opaque regime — `63`; the union of two worlds
in transparent — `92`. `80` appears nowhere, except as the best **pair** in the opaque regime
(`G07 + G17`), which is a different quantity. The number `77` is pinned in the test, and `80` is pinned as **not
reproducible**, so that the discrepancy is not lost.

## Space structure

An object has declared writings; every writing is a token word — a fixed sequence of leaves and operators -
and the number of possible trees over that word is a Catalan number. 0038 gave each
writing **one** tree (the parse of the control grammar), and the world varied only the parentheses.
Here the space is opened in full: `parseatlas.ast_space.enumerate_parenthesizations` produces every tree,
and the **imported** shape rules of `parseatlas.manifest_properties` are applied to each one.

But one filter is essential, and it is what keeps the whole experiment standing:

> **A different parenthesization of the same word is usually a different object.** `a - (b + c)` is not
> `a - b + c`. A tree that exposes a property but denotes a different thing **recovers nothing**.

So every tree is checked for identity. The check is exact: the tree is evaluated in **exact rational
arithmetic** at two declared probe points (seed `39`, not chosen post hoc), which can only
**exclude** a tree — a point where two expressions differ is a proof of their difference -
and every survivor is then confirmed with SymPy. An undefined value (division by zero) proves
nothing and is handed to SymPy rather than to guesswork.

```text
declared writings                                      50
full parenthesization space                       1510820   trees, no bound
  largest word                                         13   operators -> 742900 trees
  binomial_cube.expanded / circle.general      742900 / 742900
survived the probe                                    667
same-object trees confirmed by SymPy                  667   (0.0442% of the space)
of those, precedence-reachable                         52   (strict 51 + 1 with ties, see below)
```

**What "precedence-reachable" means here — an extended and not a strict criterion.** `strict_reachable`
decides reachability for a **tie-free** priority ordering. Four of the 25 have ties, among them
the control `G0`, so a tree that **a real grammar writes** may be declared unreachable by the strict test.
`ceiling_table` therefore computes

```text
strict_reachable(form, operators)   OR   form in registry
```

where `registry` is the actual parse of all 25 grammars. On this corpus the extension buys **one**
tree, and it is the sharpest possible case: the general writing of `circle`, which **`G0` itself
writes**. Counting it as unreachable would have been plainly wrong. The strict number `51`, the extended
`52`, and the single case where they differ — all three are pinned in the test, so that turning the
`OR` into an `AND` cannot pass silently.

**No object is restricted by a bound.** The space was selected through in full and `trees_probed` equals
`space_total`; this is pinned in the test precisely so that "we measured a part" cannot pass silently.

**In the transparent regime the manifest set of a tree does not depend on the world** — a parenthesis is punctuation
and the rule looks inside it. This is a declaration of 0038, and here it is **checked and not assumed**: all 667
same-object trees were run through all 25 grammars, `16675` checks, `0` mismatches. This is what makes the
ceiling a ceiling rather than the ceiling of one grammar.

## Corpus

The corpus is imported and not recreated: `parseatlas.manifest_properties.CORPUS` (the 33
named laws of 0037 plus the calibration quadratic, 34 objects in all, 50 writings). The principal variable comes from the same
declaration. The rules are imported **by identity and not by equality** — `PROPERTIES is
manifest_properties.PROPERTIES`, `manifest_set is manifest_properties.manifest_set`, and every shape
rule `is` its original; a copied rule set would pass an `==` check and would fail this test.

## Observed results

### 1. Part 1: the full space recovers one

```text
0038: true pairs                                      140
0038: manifest somewhere in the 25 worlds              94
0038: manifest nowhere                                 46
ceiling of the full space                              95   (+1)
recovered pairs                                         1
still invisible                                        45
```

The recovered pair is one and it is named: **`taylor_second_term` x `factor_structure`.**

```text
object     taylor_second_term          d2fa * (x - a) * (x - a) / 2
word       d2fa * x - a * x - a / 2    5 operators, 42 trees, 5 of them the same object
```

There are three trees that expose it and all three are pinned:

| tree | precedence-reachable (extended) | which worlds write it without parentheses |
|---|---|---|
| `d2fa * ((x - a) * ((x - a) / 2))` | no | - |
| `d2fa * ((x - a) * (x - a) / 2)` | no | - |
| **`d2fa * (x - a) * ((x - a) / 2)`** | **yes** | `G02` `G08` `G11` `G12` |

**Per-property recovery: `factor_structure` 1, the other six — 0.** So for six of the seven properties the
full space adds **nothing**. The answer to question 5 of the card reads straight off this.

### 2. NF-2026-00006 — defect report: a reachable tree means 0038 missed it, not that the space won

The criterion of the card is categorical: a recovered pair whose tree is **reachable** is a defect and
not a finding. That is exactly what happened, so the defect is measured and not merely mentioned.

0038 gives each writing one tree (the parse of the control) and entrusts the world with the parentheses alone.
But its own transparent regime says that a native of the world **reads the string with their own
grammar**. Then the natural question, which 0038 does not ask, is: *is there a bracket-free
string that this world reads as this object?* When there is, the world will write exactly that — it
is, after all, the cheapest, at zero parentheses — and it will read the tree its precedence gives, and not
the one 0038 gave it.

```text
(object, world) cells that have a zero-bracket reading               460
of those, reading a tree different from the one 0038 gave              36
how many (object, property) pairs it adds                              1
which one                                    (taylor_second_term, factor_structure)
```

**NF-2026-00006** — independently confirmed in review: in `G02` `G08` `G11` `G12`,
`manifest_properties` writes `taylor_second_term` as `(d2fa * x - a * x - a) / 2` with one
parenthesis, while in those same grammars the bracket-free `d2fa * x - a * x - a / 2` is read as **the same
object** at zero parentheses.

**The blast radius of the defect is exactly one pair.** That is, the `94` / `46` split of 0038 becomes
`95` / `45` after the defect is fixed, and all of its qualitative conclusions remain unchanged. The defect
is real and must still be fixed, but it shifts the numbers by one unit and not the picture.

Conversely, from this follows the answer to question 2 of the card: **of those 46, `0` require a tree
that no precedence grammar can write.** The precedence shape of our search space catches **not one** pair
of the 46.

But the shape of the space is nonetheless strict, and this is measured separately: of the `667` same-object trees only `52`
are written without parentheses under any precedence rule. That is, of the writings that **really are this
thing**, nearly 7 in 8 are natural for no world; it is simply that on this corpus none
of them carries a property that 0038 does not already see.

### 3. Part 2: the boundary of the operator set — requirement analysis and not rendering

Of the remaining `45`, `8` pairs have **no writing at all** in this operator set. Generation 1 has
only the binary `+ - * /` and the parenthesis: no exponentiation, no radical, no function call, no
literal for the imaginary unit.

| object | property | what it would need | roots |
|---|---|---|---|
| `difference_of_cubes` | `roots` | `i` **and** a radical | `b`, `b * (-1/2 +- sqrt(3) i/2)` |
| `sum_of_cubes` | `roots` | `i` **and** a radical | `-b`, `b * (1/2 +- sqrt(3) i/2)` |
| `circle` | `roots` | `i` | `h +- i (y - k)` |
| `ellipse` | `roots` | `i` | `+- i a y / b` |
| `ellipse` | `factor_structure` | `i` | `b x -+ i a y` |
| `distance_components` | `roots` | `i` | `x1 +- i (y2 - y1)` |
| `pythagorean_form` | `roots` | `i` | `+- i b` |
| `parabola` | `roots` | **a radical** | `h +- sqrt(-a k) / a` |

```text
imaginary_unit    7 pairs
radical           1 pair    (difference_of_cubes and sum_of_cubes require both)
no_closed_form    0
total             8 pairs,  7 objects
```

**The criterion is declared:** `roots` requires the numerator of the object to factor into factors of degree at
most one in the principal variable over the field of rational functions in the remaining symbols;
`factor_structure` requires two compound numerator factors. This is **exactly** what the imported
shape rule demands, translated into algebra.

Two neighbours show in one line where the boundary runs: **`hyperbola` factors over the rational field and
`ellipse` does not.** `x*x/(a*a) - y*y/(b*b)` is a difference of squares and its roots `+- a y / b`
are rational; the roots of `x*x/(a*a) + y*y/(b*b)` are `+- i a y / b`. Hence hyperbola is in Part 3
(the writing exists — and below it really is written), while ellipse is in Part 2.

**Here we differ from the manager's diagnosis by one unit, and this is said openly.** The subset hidden under
`roots` or `factor_structure` is indeed `20` objects, but under the declared criterion `13` of them factor
in Generation 1 and `7` do not — not `12` / `8`. The difference lies in the criterion and not in the measurement;
which object is on which side is written above by name.

### 4. Part 3: the residue — 37 pairs, each named

`46 - 1 - 8 = 37`. These are the pairs that are true, whose writing **exists** in this operator
set, and which are nevertheless not visible. They fall into two groups, and the distinction matters.

**(a) `different_word` — 18 pairs.** A Generation 1 writing exists, but its token word
**is not the word of any declared writing**. The parenthesization space does not change the word — it
changes only the tree — so these pairs are in principle out of reach for Part 1. **For each of them a
witness is written and rendered**, and the imported rules really do fire on it:

| object | recovered property | witness (outside the corpus) | manifest set of the witness |
|---|---|---|---|
| `quadratic` | `L` `C` `S` | `a * x * x - a * r * x - a * s * x + a * r * s` | `D L C S` |
| `hyperbola` | `R` | `(x - a * y / b) * (x + a * y / b) / (a * a)` | `D R` |
| `hyperbola` | `F` | `(b * x - a * y) * ((b * x + a * y) / (a * a * b * b))` | `D R F` |
| `distance_components` | `D` `L` `S` | `x2 * x2 - 2 * x1 * x2 + x1 * x1 + y2 * y2 - 2 * y1 * y2 + y1 * y1` | `D L S` |
| `midpoint` | `L` `C` `S` | `x1 / 2 + x2 / 2` | `D L C S` |
| `taylor_first_term` | `L` `C` `S` | `dfa * x - dfa * a` | `D L C S` |
| `taylor_second_term` | `L` `C` `S` | `d2fa * x * x / 2 - d2fa * a * x + d2fa * a * a / 2` | `D L C S` |
| `riemann_sum_term` | `S` | `fxi * b / n - fxi * a / n` | `S` |

`distance_components` is the most eloquent: in 0038 it is one of the **five objects that expose nothing in
any world**, and its ceiling in the full space is empty too — yet in an expanded
word that the corpus does not name, three of its five true properties are on the surface at once. So
its invisibility is the fault of neither the space nor the language: it is the fault of **the corpus's single named writing**.

**A witness does not count towards the recovery of Part 1.** It is evidence of which bucket a pair falls
into, and not visibility discovered; the headline number is `1` and does not grow to `19`.

**(b) `rule_limit` — 19 pairs.** **No** Generation 1 writing of these objects satisfies the
shape rule, because the shape rule demands more than the truth rule. Each has a declared reason
(`RULE_LIMIT_REASONS`) and a test requires that none be left without one.

There are two recurring reasons and they account for 19 of the 19:

```text
factor_structure (10):  truth counts even a bare symbol as a factor, the shape rule does not.
                        chain_rule (dfg * dg) and triangle_area (b * h / 2) have both factors
                        atomic; distributive_law, trapezoid_area, taylor_first_term,
                        difference_quotient, quotient_rule, riemann_sum_term - one
                        compound and one atom; slope has its compound factor in the denominator.

"at most one" (9):      constant_term requires the constant term to be a single monomial, and
                        roots requires a linear factor to carry one constant term.
                        The root of line, x1 - y1/m, is a sum of two monomials; the constant
                        term of circle, h*h + (y-k)*(y-k), is not a monomial at all. Adding two
                        is algebra, so the rule refuses.
```

This is **not** a mistake in the rules of 0038 — both clauses were introduced there deliberately and
explicitly, precisely so that "adding two" would not count as visibility. But its consequence appears
numerically here for the first time: **of the invisible 46, 19 are the fault of neither the space nor the language,
but of those two declared clauses.**

### 5. Per-property accounting

| property | hidden in 0038 | after Part 1 | blocked by the language | residue |
|---|---|---|---|---|
| `degree` | 1 | 1 | 0 | 1 |
| `leading_coefficient` | 7 | 7 | 0 | 7 |
| `constant_term` | 9 | 9 | 0 | 9 |
| `roots` | 10 | 10 | 7 | 3 |
| `factor_structure` | 12 | 11 | 1 | 10 |
| `sign_structure` | 7 | 7 | 0 | 7 |
| `even_parity` | 0 | 0 | 0 | 0 |
| **total** | **46** | **45** | **8** | **37** |

### 6. Headline questions, each in one sentence and a number

1. **Of the 46, `1` becomes manifest in the full parenthesization space** - `taylor_second_term` x
   `factor_structure`, with three exposing trees, and the ceiling rises from 94 to 95.
2. **Of those, `0` require a tree that no precedence grammar can write** - the one recovered pair
   is reachable (`G02` `G08` `G11` `G12` read the bracket-free word exactly that way), so it is a
   defect in the "one tree per writing" model of 0038 and not the price of the search space.
3. **`8` pairs are closed off by the operator set** - `7` need the imaginary unit, `1` (`parabola` x
   `roots`) a square root, and the two cubic identities need both together.
4. **After both accountings, `37` remain** - `18` of them require a different token word (and each one's
   witness is written and rendered), while `19` rest on two declared clauses of the rules
   ("at most one" and "compound factor").
5. **Yes, the full space has a ceiling of its own too:** of the 140, `45` pairs remain invisible under
   any choice of tree, six of the seven properties gain **nothing** from the full space, and the five
   objects of 0038 that expose nothing (`distance_components`, `slope`, `triangle_area`, `chain_rule`,
   `riemann_sum_term`) remain empty at the ceiling as well.

## Interpretation

**1. Precedence is not what hides the 46.** This was the main hypothesis of the card and the measurement does not
confirm it. The `92.159%` unreachability of 0023 is exact, but it is about `(word, tree)`
pairs; whereas once the word is fixed and the tree is required to denote **the same thing**, the space collapses
from `1510820` to `667`, i.e. to `0.0442%`. **Reassociation almost always changes the object and not the
view.** That is exactly why the full space buys one and not ten.

**2. The main constraint on this corpus is the token word and not the tree.** 18 of the 37 residue pairs say
exactly this: the writing exists, it is written in Generation 1, the imported rules fire on it — it is simply a different
sequence of symbols from the one or two that the corpus names. The world of 0038 chooses
**among named writings**; it does not write the object anew. This is the axis this
series does not yet measure, and it appeared here quantitatively for the first time.

**3. The rules account for nearly half of the 46, and this does not weaken 0038 — it calibrates it.** Two
clauses that 0038 introduced deliberately and explicitly ("at most one variable-free
summand", "two compound factors") stop 19 pairs. That means that the central limitation of
0038 — rule-relativity — was not merely stated but is **measurable**: another, equally conservative set of rules would
shift those 19. The standing caveat of the ROADMAP about the scale of negative results applies here at full
strength.

**4. `hyperbola` and `ellipse` show in one line that all three causes really are different.** Both
are conics of the same form, differing by one sign. The roots of `hyperbola` are rational and its writing
was written and rendered in Generation 1 (residue, `different_word`); the roots of `ellipse`
are imaginary and its writing does not exist in this language (the boundary of the language). Neither of them is
the fault of precedence.

**5. The defect is small, but it must be recorded as it is.** 0038 gives each writing one tree;
its transparent regime, meanwhile, says that a native of the world reads with their own grammar. In 36
cells these two statements contradict each other, and in one cell the contradiction has a consequence.
`94` becomes `95`, `46` becomes `45`; the qualitative conclusions of 0038 — no world shows
everything, `constant_term` x `roots` never together, the trade is real — remain unchanged.

## Limits

- **Part 2 is requirement analysis and not a measurement of rendering.** None of its numbers says
  that a property is visible. It says that the writing that would expose it has no existence in this
  operator set. No extended parser was built and none should have been — that is a change of language and a separate card.
- **Manifestness is relative to the declared shape rules of 0038.** A different rule set would shift every number,
  and 19 of the 37 residue pairs are the direct consequence of two clauses. A property that is invisible under these
  rules is **not** thereby invisible under all rules.
- **The corpus is that of 0038 and its choices were inherited** - among them which
  writings an object is given. This is not a secondary matter: 18 of the residue pairs rest on exactly that choice.
- **The parenthesization space does not change the word.** It measures "the same tokens, a different tree" and not
  "a different writing". The third axis — a new token word — is touched in this card only through witnesses
  and is not measured systematically.
- **The `rule_limit` classification is an argument and not an exhaustive search.** It states that no
  non-redundant Generation 1 writing of an object can satisfy the shape rule, and it names the reason; it
  is not a proof over all possible strings. Degenerate padding (`(a + 0) * (b + c)`) would formally
  satisfy `factor_structure`, and this is said openly rather than hidden.
- **The identity filter depends on SymPy.** The probe only excludes; confirmation belongs to SymPy;
  an error by SymPy is not controlled for here.
- **A cheaper or more "visible" convention is not an argument that mathematics should have adopted it.**

## Classification of evidence

- The size of the space (`1510820`), the same-object trees (`667`), the precedence-reachable ones among them (`52`), the ceiling
  (`95`), the recovered pair (`1`), the per-property breakdown — **OBSERVED**, on this corpus, on these
  writings, under these rules.
- `manifest => true` over the full space (`657` claims, `0` violations), grammar independence (`16675`
  checks, `0` mismatches), sequential == parallel — **VERIFIED PROPERTIES** on this space, not a
  proof over all trees.
- The 18 witnesses (same object + the rule fires) - **OBSERVED**, each separately rendered and
  checked; they are **not** counted in the headline `1`.
- The `8` pairs of Part 2 and their requirements - **REQUIREMENT ANALYSIS**, algebraic and not a
  measurement of rendering. That is exactly why they are in a separate bucket.
- The reasons for the 19 `rule_limit` pairs - **ARGUMENT**, declared and named one by one, and not
  an exhaustive search over all strings.
- The zero-bracket reading defect (`460` / `36` / `1`) - **DEFECT REPORT** against the model of 0038, with a measured
  blast radius.
- "`80` does not reproduce" - **CORRECTION**, checked against five different readings.

## Validation

```text
python -m pytest -q tests/test_visibility_ceiling.py      31 passed  (22.3 s)
python -m pytest -q                                      720 passed  (8 min 35 s)
```

The headline numbers are **pinned literally** in the tests rather than recomputed from the module;
all 37 residue pairs are written out by name in a test literal, in two groups. The test file is deliberately
ordered "cheapest first": plumbing, the identity filter and the concurrency policy are checked on a few trees
before any sweep walks 1.5 million, so a broken invariant fails in seconds and not
after a pass over the full space.

### Concurrency: parallel by measurement

```text
trees                               1510820   (50 writings, chunk = 4000 trees)
chunks                                  425
workers                                  12   (16 cores, two in headroom, cap 12)
sequential                          23.979 s  ->  1.587e-5 s / tree
parallel (12 workers)                8.611 s
speedup                               2.78x
identical results                      True
process pool startup (12 workers)    1.270 s  (min of 3; declared 1.3)
```

`should_parallelise` does arithmetic on two **measured** numbers and not on the tree count. **This is the
first workload in this series where the pool genuinely pays for itself**: the 850 cells of 0038 were `0.20` seconds of
work and could not amortise the `1.2` seconds of the pool, whereas here there are 24 seconds of work and the decision is
`parallel`. Both directions are pinned in the test (`1510820` trees -> `True`, `1000` trees ->
`False`). The worker count is derived from the observed cores and not from a hardcoded constant.

### Mutation testing

On an isolated copy (tree copied into the scratchpad; canonical repository untouched; a preflight
test checks that the import comes **from the copy** and not from `d:/Dev/ParseAtlas/src`), `20` mutants
at the decisive points:

```text
the identity filter is dropped: every parenthesization counts as the object   KILLED
the probe evaluates division as multiplication                                KILLED
a form that disagrees at a probe point is kept anyway                         KILLED
every variable of a probe point gets the same value                           KILLED
only the first exposing tree of a recovered property is reported              KILLED
a recovered property counts as reachable only if EVERY exposing tree is       KILLED
the operator word is collected root-first instead of in order                 KILLED
leaves are numbered right subtree first                                       KILLED
rebuild swaps the two operands                                                KILLED
the enumeration reuses one leaf name for every position                       KILLED
the bracket-free word is written with the wrong operators                     KILLED
a property still hidden is judged against the worlds instead of the ceiling   KILLED
the ceiling is computed under the opaque regime                               KILLED
roots accept a quadratic factor as writable in this operator set              KILLED
a bare symbol counts as a compound factor                                     KILLED
the imaginary unit is not counted as a missing constant                       KILLED
a zero-bracket reading is accepted even when it denotes another object        KILLED
a witness is reported as holding without checking that the rule fires         KILLED
every residue pair is classified as needing a different word                  KILLED
the parallel decision is taken on the tree count instead of the measurement   KILLED

killed 20/20
```

`only the first exposing tree of a recovered property is reported` is particularly valuable: this was a
**real bug in the first version of this module** and it answered question 2 of the card incorrectly -
the first tree found was unreachable, the third reachable, and the defect would not have surfaced. The mutant now
catches that regression.

On the first run **one mutant survived** — `a bare symbol counts as a compound factor`. The reason is
that the **verdict** of `factor_requirement` is the same in both cases: the number of compound
factors changes the verdict only when it is `< 2` rationally and becomes `>= 2` with the addition of `i`,
and the only such object (`ellipse`) has no bare symbol in its numerator at all.
So the `is_Symbol` clause did not change any verdict on the corpus, although it **carries** the reason for ten
`rule_limit` pairs ("one compound and one atom"). A test was added that pins exactly this **number**
on named objects (`chain_rule` 0, `triangle_area` 0, `distributive_law` 1, `slope` 1,
`ellipse` 1 -> 2 with `i`, `hyperbola` 2), and the mutant died. The numbers the report
publishes did not change by this — what is pinned is what the reasons already stand on.

### The exact commands used

```text
python -c "from parseatlas.visibility_ceiling import visibility_ceiling_report as r; print(r()['headline'])"
python -c "from parseatlas.visibility_ceiling import ceiling_table as t; d=t(); print(d['space_total'], d['same_object_trees'], d['recovered_pairs'])"
python -c "from parseatlas.visibility_ceiling import language_accounting as l; print(l()['by_requirement'])"
python -c "from parseatlas.visibility_ceiling import residue_report as r; print({k: len(v) for k, v in r()['by_cause'].items()})"
python -c "from parseatlas.visibility_ceiling import zero_bracket_readings as z; d=z(); print(d['cells_with_a_zero_bracket_reading'], d['cells_reading_a_different_tree'], d['added_pairs'])"
python -c "from parseatlas.visibility_ceiling import parallel_decision as p; print(p())"
```
