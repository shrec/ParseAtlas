# ParseAtlas ექსპერიმენტი 0034: notational cost of real mathematics

## მიზანი

Conventional grammar `G0` `58` named formula-ს corpus-ზე `53` parenthesis-ს ითხოვს და 25 grammar-ს შორის **მე-11 ადგილზეა** (`G03`-სა და `G12`-სთან ტოლი). ეს არის პირველი direction B ექსპერიმენტი: 0001-0033 ფიქსირებულ token string-ს იღებდა და კითხულობდა თუ რას *ნიშნავს* ის თითო grammar-ში, აქ კი ფიქსირებულია მათემატიკური **object** - მისი intended tree - და იზომება რა *ღირს* მისი დაწერა თითო convention-ში.

```text
direction A   source string  --parse(g)-->   tree_g            (0001..0033)
direction B   intended tree  --render(g)-->  string, cost_g    (0034)
```

## 1. სად დგას conventional G0

`G0` (`*/ +-`) მთელ corpus-ზე `53` parenthesis pair-ს იხდის და ranking-ში `11`-ე ადგილზეა 25-დან; მასზე იაფია ათი grammar, მასზე ძვირი - თორმეტი.

Rank არის competition rank (`1, 2, 2, 4`) და tie-ები ნამდვილია: `53` არის აგრეთვე `G03`-ისა და `G12`-ის total.

## 2. ყველაზე იაფი grammar

ყველაზე იაფია `G09` (`- * + /`) `29` parenthesis-ით, რაც `G0`-ს `24` parenthesis-ით, ანუ **`45.28%`-ით ჯობნის**; ყველაზე ძვირია `G20` (`/ + * -`) `83`-ით, ასე რომ მთელი spread არის `54` parenthesis.

`G09`-ის სტრუქტურა ერთი წინადადებით ითქმის: `-` ყველაზე მაგრად აკავშირებს, `/` ყველაზე სუსტად. ეს ორივე ფრჩხილს კლავს იმ shape-ში, რომელიც corpus-ში ყველაზე ხშირია - `(difference) / (difference)`:

```text
G0    (y2 - y1) / (x2 - x1)      cost 2
G09    y2 - y1 / x2 - x1         cost 0
```

Manager probe-ის მიმართულება reproduce-დება, magnitude კი არა: probe-ის ათ formula-ზე `G0 = 7`, `G10 = 4`, `G06 = 15`; ამ `58`-formula corpus-ზე `G0 = 53` (rank 11), `G10 = 39` (rank 4), `G06 = 73` (rank 22). ორივე გაზომვაში `G0` არ არის optimal, `G10` მასზე იაფია და `G06` worst-ის მახლობლადაა, მაგრამ ამ corpus-ზე `G10` არ არის cheapest - cheapest `G09`-ია.

## 3. Ranking per area

Ranking **არ** არის ერთგვაროვანი area-ებზე: ოთხი area-ის winner `G09`-ია, physics-ს `G13`/`G15` (`* + - /` და `* - + /`) ურჩევნია, statistics-ს კი `G14` (`* + / -`), ასე რომ area-ს შეუძლია საკუთარი convention აირჩიოს.

| area | n | `G0` | `G0` rank | best | best grammars | worst |
|---|---|---|---|---|---|---|
| algebra | 10 | 11 | 11 | 7 | `G09` | 18 |
| arithmetic | 10 | 8 | 8 | 6 | `G09`, `G13`, `G15` | 11 |
| calculus | 9 | 8 | 12 | 4 | `G09`, `G10` | 13 |
| geometry | 9 | 10 | 17 | 2 | `G09` | 14 |
| physics | 11 | 5 | 8 | 2 | `G13`, `G15` | 12 |
| statistics | 9 | 11 | 8 | 6 | `G14` | 17 |

`G0`-ის ყველაზე სუსტი area არის geometry (rank `17`, `10` vs best `2`) - სწორედ იქ, სადაც თითქმის ყველა formula fraction-ია. ყველაზე ძლიერი area არის physics (rank `8`, `5` vs best `2`), სადაც corpus-ის ხუთი formula ერთ operator type-ს იყენებს.

## 4. Convention sensitivity

`58`-დან `5` formula convention-insensitive-ია (`cylinder_volume`, `standard_error`, `density`, `work_done`, `ohm_series_resistance` - ყველა single operator type და ყველა cost `0` ყველა grammar-ში), ხოლო ყველაზე მეტად რხევადია `distance_component_sum` (`(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)`, range `6`: `0`-დან `6`-მდე) და `variance_of_two_points` (range `5`: `2`-დან `7`-მდე).

```text
distance_component_sum
  G0    (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)              4
  G09    x2 - x1 * x2 - x1 + y2 - y1 * y2 - y1                     0
  G20   ((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1))          6
```

Range არის მათემატიკის და არა convention-ის თვისება: `distance_component_sum` ორ operator level-ს ურევს ორივე მიმართულებით, ამიტომ ყოველი reordering მას ეხება; `density` (`m / v`) კი ერთი operator-ისაა და ვერავითარი precedence order ვერ შეცვლის მის ფასს.

`G0` cheapest-ის ტოლ cost-ს `58`-დან `24` formula-ზე აღწევს, ანუ ორ მესამედზე ნაკლებზე.

## 5. რა გახდებოდა parenthesis-free

`G0`-ში `24` formula იწერება ფრჩხილების გარეშე, `G09`-ში `39`; გადასვლისას `23` formula ხდება parenthesis-free და `8` კარგავს ამ სტატუსს.

Gained (`G09`-ში free, `G0`-ში არა) - ეს არის ის მათემატიკა, რომელიც ამ convention-ში იქნებოდა natural:

```text
average_velocity  circumference_over_diameter  correlation_coefficient  covariance_term
difference_quotient  distance_component_sum  fraction_sum_common_denominator
harmonic_mean_of_two  lens_equation_focal  linear_approximation  mean_of_three  mean_of_two
midpoint_coordinate  ohm_parallel_two  pooled_mean  quadratic_factored  regression_slope
riemann_rectangle_width  slope_through_two_points  taylor_second_term  voltage_divider
weighted_mean  z_score
```

Lost (`G0`-ში free, `G09`-ში აღარ):

```text
confidence_interval_upper  difference_of_squares_expanded  harmonic_sum  mixed_number
newton_step  ohm_parallel_reciprocal  terminal_voltage  variance_shortcut
```

Trade თვალსაჩინოა: `G09` ყიდულობს ყველა "დიდ წილადს" (slope, mean, z-score, weighted mean) და ყიდის reciprocal sum-ს (`1 / a + 1 / b` ხდება `(1 / a) + (1 / b)`) და `a + b / c` ტიპის mixed term-ს.

Roadmap-ის პროგნოზი distributive law-ზე ცალკე reproduce-დება `G01`-ზე (`+ - * /`), სადაც `+` ყველაზე მაგრად აკავშირებს:

```text
grammar   a * (b + c)       a * b + a * c         (a + b) * (a + b)
G0        a * (b + c)   1   a * b + a * c     0   (a + b) * (a + b)  2
G01       a * b + c     0   (a * b) + (a * c) 2   a + b * a + b      0
```

ანუ `G01`-ში factored form არის parenthesis-free default და expanded form ხდება ძვირი - distributive law-ის ბუნებრივი მიმართულება ბრუნდება.

## Null model

Cost-ის ნაწილი forced-ია და არა chosen, ამიტომ headline-ების გვერდით ცალკე ითვლება.

- Constant formulas (cost იდენტურია 25-ვე grammar-ში): `5` from `58`. ხუთივე `support size = 1` არის, ანუ ერთი operator type-ის tree, რომელსაც precedence reordering ვერ ეხება; ეს არის 0019-ის operator-support reduction-ის პირდაპირი შედეგი.
- ამ `5` formula-ს forced total არის `0` parenthesis. ისინი არცერთ grammar-ს არაფერს არ უმატებენ.
- ამიტომ movable subcorpus-ზე (`53` formula) გადათვლისას **totals საერთოდ არ იცვლება**, spread რჩება `54` (survival `100%`), ranking იდენტურია სიმბოლო-სიმბოლოთ და `G0`-ის rank ისევ `11`-ია.

ეს იმას ნიშნავს, რომ ranking-ს არ ატარებს ის formula-ები, რომლებიც ვერ იძვრიან - მაგრამ ეს ამ corpus-ის თვისებაა და არა ზოგადი კანონი: constant formula-ს შეუძლია არა-ნულოვანი constant cost-იც ჰქონდეს (`a - (b - c)` ერთ parenthesis-ს ყველა grammar-ში ითხოვს, ტესტში ცალკეა pin-ული), და ასეთი corpus-ის შემთხვევაში forced total > 0 იქნებოდა.

მეორე null quantity: per-formula oracle. თუ თითო formula-სთვის ცალკე convention-ის არჩევა შეიძლებოდა, corpus დაჯდებოდა `3` parenthesis-ად; საუკეთესო *ერთი* grammar `29`-ს იხდის. ეს `26` parenthesis არის ერთი გლობალური convention-ის ქონის ფასი და არა `G09`-ის ნაკლი - არცერთი grammar მას ვერ აღწევს.

## Corpus

`58` named formula `6` area-ში, თითოეული შეყვანილია conventional notation-ის source string-ით და მისი intended tree მიიღება ამ string-ის `G0`-ით parse-ით, რადგან `G0` განსაზღვრებით არის ის, როგორც დღეს ვწერთ. Corpus არის auditable: ყოველი formula-სთვის `render(parse(source, G0), G0) == source`, ანუ source-ში არც ერთი ზედმეტი ფრჩხილი და არც ერთი დამალული intent არ არის (`corpus_audit`, `test_corpus_is_auditable_named_mathematics`).

Coefficient sweep აქ განზრახ არ არის: founding question template-ებზე არ არის.

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

## დაკვირვებული შედეგები

Full ranking, `25` grammar, `58` formula:

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

Correctness bridge და minimality:

```text
round-trip checks (58 formulas x 25 grammars)   1450
round-trip failures                                0
brackets emitted and re-checked                 1397
brackets that could be removed                     0
```

Round trip არის `parse(render(tree, g), g) == tree` და ის მოწმდება **production path-ში**, არა მხოლოდ ტესტებში: `render` თავად reparse-ავს საკუთარ output-ს და mismatch-ზე `RoundTripError`-ს აგდებს. Minimality მოწმდება construction-ით: rendering-ის ყოველი bracket pair რიგრიგობით იშლება და შედეგი უნდა parse-დებოდეს *სხვა* tree-ად (ან საერთოდ არ parse-დებოდეს).

Bracket rule არ არის hardcoded table. Binding power მთლიანად `Grammar.levels`-იდან იკითხება, threshold კი პირდაპირ parser-ის ორი რიცხვია: `Parser._expression` operator-ს იღებს `>= minimum_power`-ზე და right operand-ს `power(operator) + 1`-ზე parse-ავს, ამიტომ left child-ის threshold არის `parent_power`, right child-ისა კი `parent_power + 1`. სწორედ ამიტომ იგივე კოდი მუშაობს tied control grammar-ზეც, სადაც `power("*") == power("/")` და `a * b / c` free-ა, ხოლო `a / (b * c)` არა.

Sequential-versus-parallel measurement (16 core, `repeats = 5`, minimum-of-runs):

```text
sequential                 0.0273 s
parallel (16 processes)    0.3885 s
speedup                    0.070x   ->  sequential 14.2x faster
identical results          True
```

Workload არის `1450` string render pure Python-ში; process pool-ის spawn cost მას თითქმის რიგით აღემატება. `resolve_worker_count` core-ების დაკვირვებული რაოდენობიდან იღება და `PARALLEL_MINIMUM_ITEMS = 256`-ზე ნაკლებ item-ზე `1`-ს აბრუნებს, ასე რომ default path sequential-ია - **გაზომვის საფუძველზე და არა დაშვებით**. Parallel path არსებობს, ტესტით არის დაფარული და `workers=1` vs `workers=2` იდენტურ სტრუქტურას აბრუნებს.

## ინტერპრეტაცია

Direction A-ს ინსტრუმენტები ("რას ნიშნავს string") საკმარისი აღმოჩნდა direction B-ს ("რა ღირს object") ასაწყობად: იგივე `Grammar`, იგივე `Parser`, შებრუნებული მიმართულებით.

პასუხი founding question-ის პირველ ნახევარზე - is the convention we inherited any good - ამ corpus-ზე არის: **არა optimal, მაგრამ არც ცუდი**. `G0` ranking-ის შუაშია (11/25), spread-ის `44%`-ზე დგას, და `45%`-ით ძვირია cheapest-ზე. `G0` მართლაც ერთადერთია, რომელიც tied levels-ს იყენებს, მაგრამ **ეს tie აქ არაფერს ყიდულობს**. review-მ გაზომა: `a * b / c` და `a + b - c` ორივე free-ია **ექვს strict ordering-შიც** — `G01`, `G03`, `G04`, `G13`, `G14`, `G17` — ანუ ნებისმიერში, სადაც `*` წინ უსწრებს `/`-ს და `+` წინ უსწრებს `-`-ს. მათ შორის `G17` (`* / + -`) არის `G0`-ის საკუთარი strict ტყუპი და ranking-ის **მე-9 ადგილზე დგას, `G0`-ზე იაფად**.

(ამ აბზაცის წინა რედაქცია ამტკიცებდა, რომ „strict ordering-ს ერთი მათგანი ყოველთვის უჯდება". ეს **მცდარი იყო** და conventional grammar-ს ისეთ უპირატესობას მიაწერდა, რომელიც მას არ აქვს. გასწორდა review-ის შემდეგ.)

მიზეზი, რის გამოც `G09` იგებს, სტრუქტურულია და corpus-ზეა დამოკიდებული: `/`-ის ყველაზე სუსტ operator-ად ქცევა თითოეულ დიდ წილადს ორ ფრჩხილს აცლის, ხოლო `-`-ის ყველაზე მაგრად დაკავშირება difference-ებს ათავისუფლებს. Corpus-ში `slope`, `mean`, `z-score`, `weighted mean`, `pooled mean`, `difference quotient` - ყველა ეს shape-ია. ეს არ არის artefact: fraction-of-differences ნამდვილად ხშირია სასკოლო და საინჟინრო მათემატიკაში. მაგრამ ის corpus-ის თვისებაა, და სხვა corpus (მაგალითად reciprocal-ებით და series-ებით დატვირთული) `G09`-ს დასჯიდა - `harmonic_sum` და `ohm_parallel_reciprocal` მასში `G0`-ზე ძვირია.

Per-area დაშლა ამას პირდაპირ ადასტურებს: geometry-ს, სადაც თითქმის ყველაფერი წილადია, `G0` ყველაზე ცუდად ემსახურება (rank 17), physics-ს კი, სადაც formula-ების ნახევარი ერთი operator type-ისაა, თითქმის ისეთივე კარგად, როგორც ნებისმიერი სხვა.

```text
convention  ->  which shapes are free  ->  which mathematics is cheap to write
```

## შეზღუდვები

- Parenthesis count არის notational cost-ის **ერთი** საზომი და არა ერთადერთი. Reading difficulty, ხელნაწერში ambiguity, ვიზუალური grouping, სწავლების სირთულე - არცერთი მათგანი აქ არ იზომება. ორი rendering ერთი და იმავე ფრჩხილების რაოდენობით შეიძლება რადიკალურად სხვადასხვა სიმძიმის იყოს წასაკითხად.
- Corpus ხელით არის შერჩეული და ამიტომ ასახავს იმას, რასაც ეს პროექტი representative mathematics-ად თვლის. `58` formula `6` area-ში არ არის sample რაიმე განსაზღვრული population-იდან; მისი auditability (ყოველი source გამოქვეყნებულია და `G0`-ში minimal-ია) მას შესამოწმებელს ხდის და არა representative-ს.
- Generation 1 language-ს არ აქვს unary minus და არ აქვს exponentiation. სწორედ ეს ორი არის რეალურ notation-ში precedence-ის ყველაზე სადავო ადგილი (`-x^2`, `a^b^c` right-associativity), და ისინი ამ გაზომვის გარეთ არიან. კვადრატები product-ებად არის ჩაწერილი (`v * v`), რაც `*`-ის წილს corpus-ში ზრდის.
- Associativity აქ ფიქსირებულია left-ზე ყველა operator-ისთვის, რადგან parser ასეთია. 0030-ის associativity space ამ ღერძს აფართოებს, მაგრამ ამ ექსპერიმენტში არ მონაწილეობს.
- Cost ითვლება bracket **pair**-ებში. Character count ამ renderer-ზე სხვა ranking-ს არ მისცემდა (ყოველი ფრჩხილი წყვილშია), მაგრამ ეს არჩევანია და არა თეორემა.
- Corpus-ის ზოგი formula ერთსა და იმავე shape-ს იმეორებს სხვადასხვა area-ში (`slope_through_two_points` და `average_velocity` იდენტური tree-ებია). ეს განზრახაა - იგივე shape ნამდვილად მეორდება area-ებს შორის - მაგრამ ეს იმას ნიშნავს, რომ per-area totals სრულიად დამოუკიდებელი არ არის.
- და მთავარი: იაფი convention ამ corpus-ზე **არ არის არგუმენტი იმისა, რომ მათემატიკას ის უნდა მიეღო**. ეს არის მხოლოდ გაზომვა იმისა, რა დაჯდებოდა. History-ს, სწავლებას, typography-ს და inertia-ს ეს რიცხვები არ ითვალისწინებენ.

## Evidence-ის კლასიფიკაცია

- `G0`-ის rank `11`, cheapest `G09 = 29`, worst `G20 = 83`, spread `54`, free counts `24 -> 39` - ეს ყველაფერი executable **observations** არის ამ `58`-formula corpus-ზე და ამ `25` grammar-ზე.
- Round trip (`1450/1450`) და minimality (`1397` bracket, `0` removable) არის **verified properties** ამავე grid-ზე და არა proof ყველა tree-ზე. Bracket rule-ის derivation parser-იდან არის **არგუმენტი**, ხოლო მისი evidence არის grid-ის სისრულე პლუს mutation testing.
- Per-area ranking და convention sensitivity არის **corpus-conditional structure** და არა universal law. Area winner-ის ცვლა (`G09` vs `G13`/`G15` vs `G14`) ამ corpus-ის area composition-ზეა დამოკიდებული.
- Null-model accounting (`5` constant formula, forced total `0`, spread survival `100%`, oracle gap `26`) არის **observation** ამ corpus-ზე; "constant formula ყოველთვის ნულოვან cost-ს ნიშნავს" **არ** არის claimed და counter-example ტესტში პირდაპირ არის pin-ული.
- Founding question-ზე პასუხი არ არის claimed როგორც general theorem. Claimed არის ის, რომ direction B გაზომვადია, გაზომილია, და ამ corpus-ზე `G0` optimal არ არის.

## ვალიდაცია

```text
593 passed
```

ახალი ტესტები: `tests/test_notational_cost.py`, `41` ტესტი.

Mutation testing იზოლირებულ ასლზე (scratchpad-ში დაკოპირებული tree; canonical repository ხელუხლებელი), `12` mutant `notational_cost.py`-ის გადამწყვეტ ადგილებზე:

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

`operator support only walks the left spine` პირველ გაშვებაზე გადარჩა; ტესტი `test_tree_operators_walks_both_subtrees` დაემატა და mutant მოკვდა.
