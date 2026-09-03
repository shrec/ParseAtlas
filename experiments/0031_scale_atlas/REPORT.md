# ParseAtlas ექსპერიმენტი 0031: scale atlas — `8` განსაკუთრებულია თუ განაწილების ერთი წერტილი

## შედეგი ერთი აბზაცით

**არა, `8` განსაკუთრებული არ არის: `104_976` expression-ზე თექვსმეტ family-ში `C(E)`-ის mode არის `4` (`27.74%`), საშუალო `7.94`, დიაპაზონი `1`-დან `18`-მდე, ხოლო `8` მხოლოდ `12.99%`-ში ჩნდება.**

მაგრამ სამი დაზუსტება, რომელთაგან თითოეული გაზომილია და თითოეული პასუხს აზუსტებს. პირველი: `C = 8`-ის შემთხვევების `97.2%` (`13_248` / `13_634`) სამი family-იდან მოდის — `affine_div`, `quadratic_div`, `cubic_div` — და სამივეზე `8` არის **ჭერი**, ე.ი. მაქსიმალური `C(E)`, რომელსაც template საერთოდ აღწევს, generic coefficient-ებზე `61-70%` სიხშირით. `affine_div`-ს (`{a}*x + {b} - {c}*x/{d}`) დამფუძნებელი expression-ის იგივე **shape** აქვს, implicit ერთიანი კოეფიციენტის სიზუსტით; თვითონ `2*t + 1 - t/2` corpus-ის **გარეთაა** (`14` strict AST family-ის `17`-ის წინააღმდეგ, §4.1), მაგრამ მისი უახლოესი წევრი `2*x + 1 - 1*x/2` `8`-ს დამოუკიდებლად აღწევს, ე.ი. `8` ამ shape-ის saturation value-ია და არა grammar space-ის კონსტანტა; დანარჩენი ცამეტი family-ის mode-ებია `4, 5, 11, 13, 16, 18`. მეორე: null model-ზე პირობითობა `8`-ს **არ არეაბილიტირებს** — `|O(E)| = 3`-ზე (corpus-ის `31.25%`) `8` პრინციპულად მიუწვდომელია (`C(E) <= factorial(3) + 1 = 7`), ხოლო `|O(E)| = 4`-ზე `8` მართლაც ამ corpus-ის mode-ია `18.89%`-ით, მაგრამ ამ mode-ს იმავე სამი `_div` family აწვდის: მათ გარეშე stratum-ის mode `4`-ზე გადადის და `8`-ის წილი `0.74%`-ია — `25.7`-ჯერ ნაკლები (§5.1). ე.ი. პირობითი განაწილება ზუსტად ისევე corpus-relative-ია, როგორც გლობალური. მესამე: structural დონეზე `1_048_576` expression-იანი sweep `0` bound violation-ს და `0` support-block violation-ს იძლევა `26_214_400` parse-ზე, მაგრამ ამავე დროს ის **coefficient-invariant** აღმოჩნდა — მილიონი structural expression ზუსტად `16` განსხვავებულ გაზომვას ატარებს, თითო family-ზე ერთს.

Scale და wall clock: structural tier `1_048_576` expression, `351.57 s`, `15` worker; semantic tier `104_976` expression, `2097.15 s`, `15` worker (მანქანაზე პარალელურად სხვა worker-ები მუშაობდნენ).

## მიზანი

პროექტის დამფუძნებელი დაკვირვება ისაა, რომ `2*t + 1 - t/2` იძლევა `24` grammar state-ს და `8` semantic class-ს. ეს ერთი რიცხვი აქამდე მოჰყვებოდა პროექტს. კითხვა პირდაპირია: `8` მეორდება, თუ ერთი token sequence-ის შემთხვევითობა იყო.

0024-მა ნაწილობრივი პასუხი უკვე გასცა `3125` controlled expression-ზე — იქ `C(E)` განაწილება იყო `{1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}`, ე.ი. `8` შემთხვევათა `12.8%`-ში, ხოლო mode იყო `4` (`48.0%`). მაგრამ ის ხუთი template-ის ერთ ჯგუფზე გაიზომა.

ეს card იმავე კითხვას პასუხობს იმ მასშტაბსა და family spread-ზე, სადაც პასუხი უკვე ვეღარ იქნება ერთი template-ჯგუფის შემთხვევითობა.

## Module structure

`src/parseatlas/scale_atlas.py` ორ tier-ად იყოფა, რადგან ორი კითხვა სამი რიგით განსხვავებული ფასისაა:

```text
structural_sweep(spec)  ->  distinct AST, operator support, support blocks, depth spread
                            SymPy call: 0  (assertion და არა counter — იხ. §1)
                            გაზომილი: 1.20 ms/expression (sequential)

semantic_sweep(spec)    ->  C(E) პროექტის საკუთარი key-ით, AST-dedup + SymPy canonicalize
                            გაზომილი: 84.6 ms/expression (sequential, stratified sample)
```

`CorpusSpec` index-addressable-ია: worker process-ს გადაეცემა index RANGE და ის თავის slice-ს თვითონ აღადგენს spec-იდან. სწორედ ეს ტოვებს structural tier-ს `1e6`-ზე memory-flat-ად — მილიონი dictionary არასოდეს materialize-დება; worker მხოლოდ aggregate counter-ებს აბრუნებს.

`collapse_report` და `distribution_report` ორივე ერთსა და იმავე semantic record-ებს მოიხმარენ (`records=`), ამიტომ headline და "რას აიაფებს" ნაწილი ერთი და იმავე run-იდან მოდის.

## Corpus

`16` family, თითო `4` parameter-ით (`a, b, c, d`), თითო slot ან `free` ან `nonzero`:

| family | template | slot kinds |
| --- | --- | --- |
| `affine` | `{a}*x + {b} - {c}*x + {d}` | free free free free |
| `affine_div` | `{a}*x + {b} - {c}*x/{d}` | free free free nonzero |
| `linear_ratio_literal` | `{a}*x + {b} - {c}/{d}*x` | free free free nonzero |
| `linear_ratio_spaced` | `{a}*x + {b} - {c} / {d}*x` | free free free nonzero |
| `quadratic` | `{a}*x*x + {b}*x - {c}/{d}` | free free free nonzero |
| `quadratic_div` | `{a}*x*x + {b}*x - {c}*x/{d}` | free free free nonzero |
| `cubic` | `{a}*x*x*x + {b}*x*x - {c}*x + {d}` | free free free free |
| `cubic_div` | `{a}*x*x*x + {b}*x*x - {c}*x/{d}` | free free free nonzero |
| `rational` | `({a}*x + {b})/({c}*x - {d})` | free free free free |
| `rational_nested` | `{a}/({b}*x + {c}) - {d}` | free free free free |
| `mixed_chain` | `{a}/{b} + {c}*x - {d}/{a}` | nonzero nonzero free free |
| `mixed_chain_spaced` | `{a} / {b} + {c}*x - {d} / {a}` | nonzero nonzero free free |
| `chain_long` | `{a}*x + {b}/x - {c}*x + {d}/x` | free free free free |
| `repeated_variable` | `{a}*x/x + {b}*x - {c}*x/{d}` | free free free nonzero |
| `repeated_var_square` | `x*x - {a}*x + x/{b} - {c}*x*x + {d}` | free nonzero free free |
| `unit_scaled` | `1*{a}*x + {b}*1 - {c}*x/1 + {d}` | free free free free |

Generation parameters (`spec.generation()`-ში ინახება, ე.ი. corpus მხოლოდ ამ report-იდან regenerable-ია):

```text
free_values     = (0, 1, ..., values_count - 1)     # 0 და 1 შიგნითაა: degenerate coefficients
nonzero_values  = (1, 2, ..., values_count)         # position-matched, იმავე სიგრძის
parameter_names = (a, b, c, d)

index       = tuple_index * family_count + family_position
tuple_index = values_count-base ოთხციფრა big-endian რიცხვი, bound to (a, b, c, d)
            = itertools.product(range(values_count), repeat=4) order

randomness: none.  seed: none.
```

- **structural corpus**: `values_count = 16` -> `16 * 16^4 = 1_048_576` expression.
- **semantic corpus**: `values_count = 9` -> `16 * 9^4 = 104_976` expression. ეს იმავე spec-ის prefix-ია, ე.ი. semantic corpus structural corpus-ის ქვესიმრავლეა coefficient-ების დონეზე.

`nonzero` slot მხოლოდ იქაა, სადაც `0` **tokenizer-ის** შეცდომაა და არა გაზომვა: Generation 1 number token არის `\d+(?:/\d+)?`, ამიტომ დაუშორებელი `3/0` არის ერთი literal `Fraction(3, 0)` და grammar-მდე ვერ აღწევს. ყველა სხვა პოზიციაზე `0` და `1` **შიგნითაა**, რადგან 0024-მა აჩვენა, რომ coefficient-ები `C(E)`-ს ამოძრავებენ fixed template-ზეც.

### Spacing — არა კოსმეტიკა, არამედ null model

სამი წყვილი family განზრახ ერთ ცვლადს იზოლირებს. ყველაზე მკვეთრი `linear_ratio_literal` vs `linear_ratio_spaced`-ია: **ერთი და იგივე ალგებრა**, ერთი space-ის სხვაობით.

```text
2*x + 3 - 4/5*x     ->  O(E) = {*, +, -}      |O| = 3   bound 6    distinct AST 6    C(E) = 4
2*x + 3 - 4 / 5*x   ->  O(E) = {*, +, -, /}   |O| = 4   bound 24   distinct AST 19   C(E) = 13
```

`4/5` დაუშორებლად ერთი rational literal-ია და `/` operator-ად საერთოდ არ ჩნდება. ე.ი. `C(E)` არის token stream-ის თვისება და არა მათემატიკისა. იგივე კონტრასტი `mixed_chain` vs `mixed_chain_spaced`-ზეც არის.

## Null model და control

0019-ის reduction: თუ ორი strict grammar-ის precedence ordering `O(E)`-ზე ერთსა და იმავე relative order-ად restrict-დება, ისინი **byte-identical** AST-ს იძლევიან. `G0` control-ს tied level აქვს (`(* /) > (+ -)`), ამიტომ `O(E)`-ზე restriction-ის შემდეგაც strict block-ების **გარეთ**, საკუთარ block-ში რჩება. reduction-იდან **გამოიყვანება ზუსტად ეს**:

```text
C(E)  <=  all-25 distinct AST  <=  factorial(|O(E)|) + 1        # დერივაცია
```

უფრო მჭიდრო ჯაჭვი

```text
C(E)  <=  strict distinct AST  <=  factorial(|O(E)|)            # დერივაცია არ არის
```

reduction-იდან **არ** გამომდინარეობს: მისი პირველი ნაბიჯი მოითხოვს, რომ `G0`-მ ახალი semantic class არ დაამატოს. ეს კი **გაზომილი** ფაქტია და არა დერივაცია — `control_adds_a_class = 0` მთელ `104_976` expression-ზე (§6). ამიტომ ორსაფეხურიანი ფორმა ქვეყნდება: დერივაცია `+ 1`-იანი bound-ით, პლუს `G0`-ის გაზომილი შედეგი, რომელიც მას აჭერს. დასკვნებზე ეს არაფერს ცვლის, რადგან `|O| = 3`-ზე `7 < 8` და `6 < 8` თანაბრად კრძალავს `8`-ს — მაგრამ დერივაცია სწორი უნდა იყოს. `test_conditioning_on_support_size_keeps_the_null_bound` სწორედ ამ ორ ბოჭვას იყენებს: `class_count <= factorial(|O|) + 1` და `strict class_count <= factorial(|O|)`.

ე.ი. ყოველი განაწილების ნაწილი parser-ითაა იძულებული და აღმოჩენა არ არის.

ამიტომ ორივე report-ში support size distribution headline-ის გვერდითაა და `C(E)` support size-ზე **პირობითადაც** არის მოცემული. `C(E)` განაწილება, რომელიც სინამდვილეში support-size განაწილებაა, აღმოჩენა არ არის.

## Metric

Semantic class key არსად არ არის ხელახლა განსაზღვრული. `semantic_record` იძახებს `parseatlas.corpus_matrix.expression_classes`-ს, რომელიც `parseatlas.analyze`-ის იმავე key-ს იყენებს:

```text
key(E, G) = (canonical expression, domain, excluded points)
```

Test `test_semantic_tier_agrees_with_analyze_expression_on_partition_membership` პირდაპირ ამოწმებს, რომ ამ tier-ის partition MEMBERSHIP `analyze_expression`-ისას ემთხვევა ექვს სხვადასხვა family-ზე.

Collapse metric-ები class-ის უკვე გამოქვეყნებული canonical text-იდან იკითხება:

```text
constant     : free symbol არ არის და მნიშვნელობა სასრულია
degenerate   : canonical form შეიცავს zoo-ს ან nan-ს (ნულოვანი მნიშვნელი)
degree       : Poly(expr, x).degree(), ან None თუ polynomial არ არის
division     : უარყოფითმაჩვენებლიანი Pow-ების რაოდენობა (a/b -> Mul(a, Pow(b, -1)))
depth        : parseatlas.critical_path.depth_profile
```

`free_depth_saving` არის ის depth, რომელსაც სხვა grammar **ნულოვან semantic ფასად** ყიდულობს: ერთი semantic class-ის შიგნით depth-ის ყველაზე ფართო დიაპაზონი. `control_depth_saving` არის ის, რასაც `G0` იხდის იმავე semantic შედეგის ყველაზე იაფ grammar-თან შედარებით.

## დაკვირვებული შედეგები

### 1. Structural tier — `1_048_576` expression

```text
expression count : 1048576        wall clock : 351.57 s
workers          : 15             chunks     : 256 x 4096
cpu_count        : 16
support size     : {3: 327680, 4: 720896}
bound violations : 0
support-block violations : 0
```

**„SymPy call: 0" ამ ბლოკში განზრახ აღარ წერია.** დანარჩენი ყველა რიცხვი აქ დათვლილია; ეს კი
დათვლილი არ იყო — structural path არსად არ არის instrumented, ამიტომ დასათვლელი არაფერია და
`"sympy_calls": 0` კოდში literal იყო და არა გაზომვა. ის ახლა იმად ქვეყნდება, რაც არის —
**assertion** კოდის გზაზე (`sympy_call_claim`, `kind: "assertion, not a counted quantity"`).
მისი მტკიცებულება ნამდვილია და ცალკე დგას: `test_structural_path_calls_no_sympy`
`canonical.to_sympy`-ს, `canonical.simplify`-სა და `canonical.solve`-ს ჩაანაცვლებს ფუნქციით,
რომელიც `AssertionError`-ს აგდებს, და structural sweep მაინც ბოლომდე გადის.

`26_214_400` parse (`1_048_576 x 25`) და **არცერთი** დარღვევა: 0019-ის reduction ამ მასშტაბზეც უცვლელად დგას. თითო support block ზუსტად ერთ AST-ს ატარებს და strict distinct AST არასოდეს გადააჭარბებს `factorial(|O(E)|)`-ს.

Strict distinct AST განაწილება:

```text
{4: 131072, 5: 196608, 6: 131072, 15: 131072, 17: 65536, 18: 131072, 19: 131072, 20: 131072}
mode 5 (18.75%),  mean 12.25,  bound-ს აღწევს 131072 (12.5%)
```

All-25 distinct AST განაწილება (`G0`-ს ჩათვლით):

```text
{4: 131072, 5: 131072, 6: 131072, 7: 65536, 15: 131072, 17: 65536, 18: 65536, 19: 196608, 21: 131072}
```

### 2. Structural tier-ის მთავარი შედეგი: coefficient invariance

ყველა რიცხვი ზემოთ `65536 = 16^4`-ის ჯერადია. ეს შემთხვევითობა არ არის და ცალკე იზომება (`coefficient_invariance`, `invariant: True`, `families_with_a_varying_quantity: {}`):

> parser კითხულობს token KIND-ებს და binding power-ებს; coefficient არც ერთია და არც მეორე. ამიტომ ყოველი structural სიდიდე **მუდმივია ერთი template family-ის შიგნით**.

ე.ი. `1_048_576`-expression-იანი structural sweep ზუსტად `16` განსხვავებულ გაზომვას ატარებს, თითო `65536`-ჯერ გამეორებულს. ეს გაზომილი უარყოფითი შედეგია structural tier-ის მასშტაბზე: მილიონი structural expression ერთ expression-ზე მეტს არაფერს ამბობს თითო family-ზე.

| family | \|O\| | bound | strict AST | all-25 AST | blocks | min depth | max depth | depth spread |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `affine` | `3` | `6` | `6` | `7` | `6` | `4` | `5` | `1` |
| `affine_div` | `4` | `24` | `17` | `17` | `24` | `4` | `6` | `2` |
| `linear_ratio_literal` | `3` | `6` | `6` | `6` | `6` | `4` | `5` | `1` |
| `linear_ratio_spaced` | `4` | `24` | `19` | `19` | `24` | `4` | `6` | `2` |
| `quadratic` | `3` | `6` | `5` | `5` | `6` | `4` | `5` | `1` |
| `quadratic_div` | `4` | `24` | `15` | `15` | `24` | `5` | `6` | `1` |
| `cubic` | `3` | `6` | `5` | `6` | `6` | `6` | `7` | `1` |
| `cubic_div` | `4` | `24` | `15` | `15` | `24` | `5` | `8` | `3` |
| `rational` | `4` | `24` | `4` | `4` | `24` | `4` | `4` | `0` |
| `rational_nested` | `4` | `24` | `4` | `4` | `24` | `5` | `5` | `0` |
| `mixed_chain` | `3` | `6` | `5` | `5` | `6` | `3` | `4` | `1` |
| `mixed_chain_spaced` | `4` | `24` | `19` | `19` | `24` | `4` | `6` | `2` |
| `chain_long` | `4` | `24` | `20` | `21` | `24` | `4` | `6` | `2` |
| `repeated_variable` | `4` | `24` | `18` | `18` | `24` | `5` | `7` | `2` |
| `repeated_var_square` | `4` | `24` | `20` | `21` | `24` | `5` | `7` | `2` |
| `unit_scaled` | `4` | `24` | `18` | `19` | `24` | `5` | `7` | `2` |

სამი დამატებითი დაკვირვება ამ ცხრილიდან:

- **`bound` საერთოდ არ არის მჭიდრო `|O| = 4`-ზე.** `24`-ს არცერთი family არ აღწევს; მაქსიმუმი `20`-ია. `|O| = 3`-ზე კი `affine` და `linear_ratio_literal` ზუსტად `6`-ს აღწევს, ე.ი. bound იქ მჭიდროა.
- **`G0`-ს ხუთ family-ზე აქვს strict grammar-ებისთვის მიუწვდომელი ხე** (all-25 > strict): `affine`, `cubic`, `chain_long`, `repeated_var_square`, `unit_scaled`. ეს 0020-ის control-only tree-ის დამოუკიდებელი დადასტურებაა ახალ family-ებზე.
- **Parenthesization structure-ს კლავს.** `rational` და `rational_nested`-ს `|O| = 4` და bound `24` აქვთ, მაგრამ მხოლოდ `4` distinct AST და `0` depth spread: ფრჩხილები precedence-ს არჩევანს არ უტოვებენ.

Depth spread მთელ corpus-ზე: `{0: 131072, 1: 393216, 2: 458752, 3: 65536}` — `87.5%`-ზე grammar-ის არჩევანი critical-path depth-ს **ცვლის**.

### 3. Semantic tier — `104_976` expression, `C(E)`-ის სრული განაწილება

```text
expression count : 104976       wall clock : 2097.15 s
workers          : 15           chunks     : 61 x 1749
cpu_count        : 16           sympify failures : 0
canonicalizations: 1318761      dedup-ის გარეშე იქნებოდა 2624400   (1.99x ნაკლები)
```

ეს corpus ამ სესიაში **სამჯერ** სრულად გაეშვა: `2017.24 s`, `2097.15 s` და `2611.46 s` (მესამე — review-ის შემდეგ, §5.1-ის ablation-ისთვის, `56` python process-იან დატვირთვაზე). wall clock სამივეზე სხვადასხვაა, მაგრამ `C(E)` განაწილება, support size-ზე პირობითი განაწილება, distinct-AST განაწილება და canonicalization count (`1_318_761` / `2_624_400`, `0` sympify failure) **იდენტური** დარჩა. ქვემოთ გამოქვეყნებულია მეორე run; §5.1 მესამეზეა დათვლილი და მისი overall განაწილება ამ ცხრილს ზუსტად ემთხვევა.

`C(E)` განაწილება მთელ corpus-ზე:

| `C(E)` | expressions | share |
| --- | --- | --- |
| `1` | `507` | `0.0048` |
| `2` | `6614` | `0.0630` |
| `3` | `3446` | `0.0328` |
| `4` | `29124` | **`0.2774`** (mode) |
| `5` | `12302` | `0.1172` |
| `6` | `1364` | `0.0130` |
| `7` | `1453` | `0.0138` |
| `8` | `13634` | `0.1299` |
| `9` | `3321` | `0.0316` |
| `10` | `2829` | `0.0269` |
| `11` | `3454` | `0.0329` |
| `12` | `2619` | `0.0249` |
| `13` | `7789` | `0.0742` |
| `14` | `1361` | `0.0130` |
| `15` | `1253` | `0.0119` |
| `16` | `5469` | `0.0521` |
| `17` | `1565` | `0.0149` |
| `18` | `6872` | `0.0655` |

```text
mode            : 4      (29124, 27.74%)
share at 8      : 0.129877  (13634 expression)
mean C(E)       : 7.9448        max C(E) : 18        min C(E) : 1
rigid (C = 1)   : 0.0048  (507 expression)
```

Distinct AST განაწილება იმავე corpus-ზე:

```text
all 25 grammars : {4: 13122, 5: 13122, 6: 13122, 7: 6561, 15: 13122, 17: 6561, 18: 6561, 19: 19683, 21: 13122}
24 strict only  : {4: 13122, 5: 19683, 6: 13122, 15: 13122, 17: 6561, 18: 13122, 19: 13122, 20: 13122}
```

0024-თან შედარება: იქ `share at 8` იყო `400 / 3125 = 0.1280` და mode `4` (`0.4800`). აქ `0.1299` და mode `4` (`0.2774`). `8`-ის წილი თითქმის უცვლელია `3125`-იდან `104_976`-მდე და ხუთიდან თექვსმეტ family-მდე გადასვლისას; mode კი იგივე `4` დარჩა, თუმცა უფრო ბრტყელი გახდა.

### 4. `C(E)` per family — სად ცხოვრობს `8`

| family | mode | mode share | `C=8` | share at 8 | mean `C` | C range |
| --- | --- | --- | --- | --- | --- | --- |
| `affine` | `5` | `0.7292` | `0` | `0.0000` | `4.677` | `1..5` |
| `affine_div` | `8` | `0.6145` | `4032` | **`0.6145`** | `6.553` | `1..8` |
| `linear_ratio_literal` | `4` | `0.7761` | `0` | `0.0000` | `3.664` | `1..4` |
| `linear_ratio_spaced` | `13` | `0.4780` | `68` | `0.0104` | `10.898` | `2..13` |
| `quadratic` | `4` | `0.7791` | `0` | `0.0000` | `3.656` | `1..4` |
| `quadratic_div` | `8` | `0.7023` | `4608` | **`0.7023`** | `7.090` | `1..8` |
| `cubic` | `5` | `0.8669` | `0` | `0.0000` | `4.860` | `1..5` |
| `cubic_div` | `8` | `0.7023` | `4608` | **`0.7023`** | `7.103` | `1..8` |
| `rational` | `4` | `0.6158` | `0` | `0.0000` | `3.195` | `1..4` |
| `rational_nested` | `4` | `0.6798` | `0` | `0.0000` | `3.358` | `1..4` |
| `mixed_chain` | `4` | `0.7791` | `0` | `0.0000` | `3.668` | `2..4` |
| `mixed_chain_spaced` | `16` | `0.5801` | `69` | `0.0105` | `13.901` | `3..16` |
| `chain_long` | `18` | `0.5181` | `8` | `0.0012` | `16.488` | `1..18` |
| `repeated_variable` | `13` | `0.6145` | `79` | `0.0120` | `11.951` | `1..13` |
| `repeated_var_square` | `18` | `0.5293` | `8` | `0.0012` | `16.768` | `7..18` |
| `unit_scaled` | `11` | `0.4301` | `154` | `0.0235` | `9.287` | `1..11` |

**ეს ცხრილია ამ ექსპერიმენტის მთავარი პასუხი.** `8` არსად არ არის უნივერსალური რიცხვი: family mode-ები არის `4, 5, 8, 11, 13, 16, 18`. `8` mode-ია ზუსტად სამ family-ზე — `affine_div`, `quadratic_div`, `cubic_div` — და სამივეზე `8` არის **ჭერი**, ე.ი. მაქსიმალური `C(E)`, რომელსაც ეს template საერთოდ აღწევს:

```text
affine_div    C ∈ {1, 2, 3, 4, 5, 6, 8}   max 8,  8-ზე 61.45%
quadratic_div C ∈ {1, 2, 3, 4, 5, 7, 8}   max 8,  8-ზე 70.23%
cubic_div     C ∈ {1, 2, 3, 4, 5, 7, 8}   max 8,  8-ზე 70.23%
```

მთელი corpus-ის `13_634` `C=8` შემთხვევიდან `13_248` (`97.2%`) ამ სამ family-შია. დანარჩენი `386` ექვს family-ზეა მიმოფანტული.

#### 4.1 დამფუძნებელი expression `affine_div`-ის **წევრი არ არის**

`affine_div`-ს დამფუძნებელი expression-ის იგივე **shape** აქვს (`{a}*x + {b} - {c}*x/{d}`) —
implicit ერთიანი კოეფიციენტის სიზუსტით. მაგრამ თვითონ `2*t + 1 - t/2` **corpus-ში არ არის**, და
ეს ტერმინოლოგიური წვრილმანი არ არის:

```text
2*t + 1 - t/2      |O| = 4   strict AST 14   C = 8     <- corpus-ის გარეთ
2*x + 1 - 1*x/2    |O| = 4   strict AST 17   C = 8     <- affine_div-ის უახლოესი წევრი
affine_div-ის ყველა 6561 წევრი (semantic corpus):  strict AST 17, გამონაკლისის გარეშე
```

template ყოველთვის **ცხად** `{c}*x`-ს წერს, ამიტომ დამფუძნებელი expression-ის შიშველი `x/{d}` კუდი
corpus-ში საერთოდ არ ჩნდება: შემოწმდა `104_976`-ვე semantic source და `1_048_576`-ვე structural
source — არცერთი. სხვაობა **token stream-ისაა** და არა მათემატიკის, და სწორედ ეს აუქმებს
membership claim-ს: ინტერპრეტაცია 4-ის მიხედვით `C(E)` token stream-ის თვისებაა, ამიტომ
token stream-ის სხვაობა (`14` vs `17` strict AST) წევრობის საწინააღმდეგო არგუმენტია და არა
დეტალი. `test_the_founding_token_stream_is_not_in_the_corpus` და
`test_the_founding_stream_and_its_nearest_family_member_differ_structurally` ორივეს პინავს.

დასკვნა კი **უცვლელი რჩება**, რადგან უახლოესი წევრი `2*x + 1 - 1*x/2` `8`-ს **დამოუკიდებლად**
აღწევს: დამფუძნებელი `8` არის ერთი **shape-ის saturation value**, რომელსაც generic
coefficient-ები აღწევენ, და არა grammar space-ის კონსტანტა.

### 5. Null model: `C(E)` support size-ზე პირობითი

Support size განაწილება: `{3: 32_805, 4: 72_171}`.

`bound` სვეტი `factorial(|O|)`-ია, ე.ი. strict ბოჭვა; დერივებული ბოჭვა `C(E)`-ზე `factorial(|O|) + 1`-ია (იხ. „Null model და control").

| `\|O(E)\|` | n | bound = `factorial(\|O\|)` | `C(E)` განაწილება | mode | `C=8` | share at 8 |
| --- | --- | --- | --- | --- | --- | --- |
| `3` | `32805` | `6` | `{1: 20, 2: 2329, 3: 2308, 4: 17676, 5: 10472}` | `4` | `0` | `0.0000` |
| `4` | `72171` | `24` | `{1: 487, 2: 4285, 3: 1138, 4: 11448, 5: 1830, 6: 1364, 7: 1453, 8: 13634, 9: 3321, 10: 2829, 11: 3454, 12: 2619, 13: 7789, 14: 1361, 15: 1253, 16: 5469, 17: 1565, 18: 6872}` | `8` | `13634` | `0.1889` |

ეს არის ის ადგილი, სადაც null model რეალურად მუშაობს და პასუხს ცვლის:

- corpus-ის `31.25%`-ს (`|O| = 3`) `8` **პრინციპულად მიუწვდომელი** აქვს: დერივაციით `C(E) <= factorial(3) + 1 = 7`, ხოლო გაზომილი `control_adds_a_class = 0`-ის შემდეგ `C(E) <= 6`. ორივე რიცხვი `8`-ზე ნაკლებია, ამიტომ დასკვნა ბოჭვის ორივე ფორმაზე ერთია. მთლიან `12.99%`-ში ეს ნაწილი უბრალოდ ნულს უწერს.
- იმ `72_171` expression-ზე, სადაც `8` საერთოდ მიღწევადია, `8` **ამ corpus-ის mode-ია** — `18.89%`, მეორე ადგილზე `C = 4` `15.86%`-ით. მაგრამ ეს mode-ობა family mix-ს ეკიდება და არა stratum-ს: იხ. §5.1, სადაც ის ablation-ს **ვერ უძლებს**.
- `|O| = 3`-ზე mode `4`-ია `53.88%`-ით, `|O| = 4`-ზე კი პიკი სულ `18.89%`-ია: **პირობითი განაწილება ბრტყელდება support size-ის ზრდასთან ერთად**, რაც bound-ის (`6` vs `24`) პირდაპირი შედეგია.

ე.ი. `C(E)` განაწილება ნაწილობრივ მართლაც support-size განაწილებაა, და ეს ცხრილი ზუსტად ზომავს რამდენად.

#### 5.1 Ablation: `|O| = 4`-ის mode `8` სამ family-ს ეყრდნობა და არა stratum-ს

პირობითი განაწილება **გადატანადი არ არის** და ეს არ არის caveat — ეს გაზომვაა. `|O| = 4`-ის
stratum-ის `13_634` `C = 8`-იდან `13_248` სამ `_div` family-შია (`affine_div` `4032` +
`quadratic_div` `4608` + `cubic_div` `4608`), ე.ი. იმ სამში, რომლებსაც `8` **ჭერად** აქვთ (§4).
ეს სამი family მთლიანად `|O| = 4`-შია, ამიტომ მათი ამოღება `|O| = 3`-ის stratum-ს საერთოდ არ
ეხება (`32_805` expression, mode `4`, `53.88%` — უცვლელი).

| `\|O\| = 4` stratum | n | mode | mode share | `C=8` | share at 8 |
| --- | --- | --- | --- | --- | --- |
| ყველა `16` family | `72171` | **`8`** | `0.1889` | `13634` | `0.1889` |
| `affine_div` გარეშე | `65610` | `4` | `0.1640` | `9602` | `0.1464` |
| `quadratic_div` გარეშე | `65610` | `4` | `0.1617` | `9026` | `0.1376` |
| `cubic_div` გარეშე | `65610` | `4` | `0.1628` | `9026` | `0.1376` |
| სამივე `_div` გარეშე | `52488` | `4` | `0.1744` | **`386`** | **`0.0074`** |

```text
|O| = 4, სამივე _div family გარეშე (52_488 expression):
{1: 460, 2: 3997, 3: 434, 4: 9156, 5: 306, 6: 788, 7: 429, 8: 386, 9: 3321, 10: 2829,
 11: 3454, 12: 2619, 13: 7789, 14: 1361, 15: 1253, 16: 5469, 17: 1565, 18: 6872}
```

- stratum-ის mode `8`-იდან `4`-ზე გადადის, ხოლო `8`-ის წილი `18.89%`-იდან `0.74%`-ზე ეცემა —
  **`25.7`-ჯერ**;
- საწყისი უპირატესობა მცირე იყო (`18.89%` vs `15.86%`), ამიტომ **ერთი** `_div` family-ის ამოღებაც
  კი აბრუნებს mode-ს `4`-ზე — სამივე ცალკეული ვარიანტი ზემოთ ცხრილშია;
- ე.ი. პირობითი განაწილება ზუსტად ისევე **family-mix-relative-ია**, როგორც გლობალური, რომელსაც
  report სწორად უწოდებს corpus-relative-ს.

დასკვნა: support size-ზე პირობითობა null model-ს ხსნის, corpus-ს კი — **არა**. `8` არც
პირობითობით რეაბილიტირდება. ბოლო სტრიქონი კოდში `distribution_report`-ის `family_mix_ablation`-ია
(იმავე record-ებზე იმავე პირობითობა, `SATURATING_DIV_FAMILIES = ("affine_div", "quadratic_div",
"cubic_div")`-ის გარეშე); შუა სამი სტრიქონი იმავე record-ებზეა თითო family-ის ამოღებით.

### 6. Control `G0`: მიუწვდომელ ხეს აღწევს, მიუწვდომელ პასუხს — არასდროს

| სიდიდე | expressions | share |
| --- | --- | --- |
| `G0` იძლევა AST-ს, რომელსაც `24` strict grammar-იდან ვერცერთი | `32805` | `0.3125` |
| `G0` იძლევა semantic class-ს, რომელსაც `24` strict grammar-იდან ვერცერთი | **`0`** | `0.0000` |

Per family, `control_adds_an_ast` ზუსტად ხუთ family-ზეა `6561/6561` (`affine`, `cubic`, `chain_long`, `repeated_var_square`, `unit_scaled`) და ყველა დანარჩენზე `0` — ეს structural tier-ის all-25 vs strict სვეტების პირდაპირი დადასტურებაა.

`control_adds_a_class` კი მთელ `104_976` expression-ზე **ნულია**. ე.ი. tied-level control grammar `(* /) > (+ -)` corpus-ის მესამედზე მართლაც ახალ parse tree-ს აშენებს, მაგრამ ვერცერთხელ ვერ აღწევს მათემატიკურ შედეგს, რომელსაც რომელიმე strict ordering უკვე არ იძლეოდა. `C(E)` და `strict C(E)` განაწილებები ამიტომაა იდენტური.

### 7. Collapse — რას აიაფებს grammar-ის არჩევანი

ყველა რიცხვი იმავე `104_976`-expression-იან run-იდანაა.

#### 7.1 Constant collapse — ცვლადი მთლიანად ქრება

```text
expressions with a constant class      : 23085   (21.99%)
...საიდანაც grammar-dependent          : 21346   (20.33%)   # ერთი class მუდმივია, მეორე — არა
...ყველა class მუდმივია                :   947   ( 0.90%)
```

სამი გაზომილი მაგალითი (თითო family-ის matching expression-ების **შუა** ელემენტი, ე.ი. არა all-zero კუთხე):

```text
affine       1*x + 5 - 6*x + 0     C=3   classes: 5 - 5*x ,  x*(x - 1) ,  0
affine_div   1*x + 5 - 7*x/2       C=6   classes: 5 - 5*x/2 , x*(x - 2)/2 , 5/2 - 3*x , -x/2 , 0 , 5/2 - 5*x/2
mixed_chain  5/5 + 0*x - 4/5       C=3   classes: 1/5 , x - 4/5 , 1
chain_long   1*x + 8/x - 0*x + 8/x C=14  classes: ... , 1 , 1/x , x , x + 8/x
```

დამფუძნებელი expression **თვითონაც** ამ მოვლენის მაგალითია:

```text
2*t + 1 - t/2   ->   G01 (+ > - > * > /)  ->  (2 * ((t + 1) - t)) / 2  =  1
                     G01, G02, G07, G08 ოთხივე ერთსა და იმავე მუდმივ `1`-ს იძლევა
```

ეს ერთადერთი რიცხვია ამ სექციაში, რომელიც `104_976`-იანი run-იდან **არ** მოდის: დამფუძნებელი
token stream corpus-ში არ არის (§4.1), ამიტომ ის ცალკე იზომება. თანაც მისი უახლოესი
corpus-წევრი `2*x + 1 - 1*x/2` constant collapse-ს **არ** აჩვენებს — `0` constant class და
degrees `(1, 2)` — ე.ი. თვით ეს მაგალითიც დამფუძნებელი token stream-ის თვისებაა და არა family-სი.

#### 7.2 Degree difference — canonical form-ის ხარისხი იცვლება

```text
expressions where degree differs : 74995   (71.44%)
spread distribution              : {0: 29981, 1: 38795, 2: 16679, 3: 17604, 4: 1332, 5: 585}
max spread                       : 5
```

```text
affine               4*x + 4 - 5*x + 0            degrees [1, 2]        spread 1   C=4
affine_div           4*x + 4 - 5*x/1              degrees [1, 2]        spread 1   C=4
repeated_var_square  x*x - 4*x + x/5 - 4*x*x + 4  degrees [2, 3, 5]     spread 3   C=17
mixed_chain_spaced   5 / 5 + 0*x - 4 / 5          degrees [0, 1]        spread 1   C=7
```

ეს **არ** არის იაფობა: ხარისხის ცვლილება სხვა მათემატიკური ობიექტია და არა იმავე ობიექტის იაფი ვარიანტი.

#### 7.3 Division difference — canonical form-ის გაყოფების რაოდენობა იცვლება

```text
expressions where division count differs : 32562   (31.02%)
spread distribution                      : {0: 72414, 1: 21926, 2: 10464, 3: 172}
max spread                               : 3
```

```text
rational            (0*x + 5)/(1*x - 0)         division counts [0, 1]     classes: 5/x , 0
repeated_variable   5*x/x + 0*x - 0*x/1         division counts [0, 1]     classes: 5 , 5/x**2 , 5*x**2 , 5/x , 5*x
chain_long          4*x + 4/x - 5*x + 0/x       division counts [0, 1, 2]  spread 2, C=16
linear_ratio_spaced 4*x + 4 - 5 / 1*x           division counts [0, 1]     spread 1, C=10
```

#### 7.4 Depth difference — და მისი უფასო ნაწილი

```text
depth differs across grammars     : 91854   (87.50%)   spread {0: 13122, 1: 39366, 2: 45927, 3: 6561}
FREE depth saving (> 0)           : 63221   (60.22%)   {0: 41755, 1: 61747, 2: 1393, 3: 81}
G0 pays more than the cheapest
grammar with the SAME semantics   : 22158   (21.11%)   {0: 82818, 1: 22158}
```

`free_depth_saving` არის ის depth, რომელსაც სხვა grammar **ერთი და იმავე semantic class-ის შიგნით** ყიდულობს — ე.ი. იგივე პასუხი, უფრო მოკლე critical path. ეს არის ერთადერთი ოთხიდან, რომელიც სუფთა იაფობაა:

```text
affine          4*x + 2 - 8*x + 0     depth 4..5   free saving 1   G0 იხდის 1-ით მეტს
affine_div      4*x + 4 - 4*x/5       depth 4..6   free saving 1   G0 optimal-ია
quadratic       4*x*x + 4*x - 4/5     depth 4..5   free saving 1   G0 იხდის 1-ით მეტს
quadratic_div   4*x*x + 4*x - 4*x/5   depth 5..6   free saving 1   G0 optimal-ია
```

corpus-ის `21.11%`-ზე default-ური tied-level grammar `G0` **არ** არის ყველაზე იაფი იმ grammar-ებს შორის, რომლებიც ზუსტად იმავე პასუხს იძლევიან. ეს არის ის კონკრეტული ადგილი, სადაც grammar-ის არჩევანი გაზომილ სარგებელს იძლევა და მათემატიკას არ ცვლის.

#### 7.5 Degenerate classes

```text
expressions with a zoo/nan class : 3627   (3.46%)
sympify failures                 : 0
```

```text
rational            (4*x + 4)/(0*x - 4)   C=4   2 degenerate class: zoo*(x + 4) , zoo*(x + 1)
rational_nested     4/(0*x + 4) - 4       C=3   classes: -3 , -1 , zoo
mixed_chain_spaced  5 / 5 + 0*x - 5 / 5   C=9   ერთი zoo class
```

ეს არის degenerate coefficient-ების ფასი: `0` მნიშვნელი გარკვეულ parse-ებში ჩნდება და არა ყველაში. ისინი ცალკე ითვლება და **არ** ითვლება არც constant-ად და არც degree-ის სტატისტიკაში.

## Performance

| tier | expressions | parses | wall clock | workers | chunks |
| --- | --- | --- | --- | --- | --- |
| structural | `1_048_576` | `26_214_400` | `351.57 s` | `15` | `256 x 4096` |
| semantic | `104_976` | `5_248_800` | `2097.15 s` | `15` | `61 x 1749` |

- Worker count არსად არ არის hardcoded: `parseatlas.corpus_matrix.resolve_worker_count` observed core count-იდან იღებს `cores - 1`-ს (ერთი core headroom-ად interactive session-ისთვის). `cpu_count = 16`, ამიტომ ორივე tier-ზე რეალურად მიღებული worker count არის **`15`**.
- Worker count expression count-იდან იხსნება და არა chunk count-იდან; chunk size შემდეგ იზომება worker-ზე ოთხი chunk-ის წესით (`min(4096, size // (workers * 4))`).
- Structural worker **aggregate counter-ებს** აბრუნებს და არა record-ებს, ამიტომ `1e6` memory-flat-ია; semantic worker record-ებს აბრუნებს, რადგან `1e5` მათი შენახვა შესაძლებელია.
- AST dedup: `1_318_761` canonicalization ნაცვლად `2_624_400`-ისა (`1.99x` ნაკლები). `analyze_expression` hot loop-ში არ იძახება.
- Parallelism მხოლოდ სიჩქარეს ცვლის: `test_structural_sequential_and_parallel_agree` და `test_semantic_sequential_and_parallel_agree` პინავს, რომ `workers=1` და `workers=2` იდენტურ შედეგს იძლევა, `test_chunking_does_not_change_the_structural_result` კი — რომ chunk size-ის ცვლილება არაფერს ცვლის.
- **Wall clock ერთადერთი რიცხვია, რომელიც run-იდან run-ში იცვლება.** ამ სესიაში მანქანაზე პარალელურად სხვა worker-ები მუშაობდნენ (გაზომილია: `50`-მდე python process, `~1446%` CPU `1600%`-იდან; მესამე run-ის დროს `56` process). სამი სრული semantic run: `2017.24 s`, `2097.15 s` და `2611.46 s` — იდენტური შედეგებით.

## ინტერპრეტაცია

**1. `8` არ არის grammar space-ის კონსტანტა — ის ერთი template shape-ის saturation value-ია.** სამი family — `affine_div`, `quadratic_div`, `cubic_div` — ყველა იმავე `... - {c}*x/{d}` კუდით, `8`-ს **ჭერად** აქვს და generic coefficient-ებზე `61-70%` სიხშირით აღწევს. მთელი corpus-ის `C=8` შემთხვევების `97.2%` აქედან მოდის. დანარჩენი ცამეტი family-ის mode-ებია `4, 5, 11, 13, 16, 18`. თვითონ დამფუძნებელი token stream `affine_div`-ის წევრი **არ არის** (§4.1) — მას იგივე shape აქვს implicit ერთიანი კოეფიციენტის სიზუსტით, `14` strict AST family-ის `17`-ის წინააღმდეგ — მაგრამ დასკვნა ამაზე არ დგას: უახლოესი წევრი `2*x + 1 - 1*x/2` `8`-ს დამოუკიდებლად აღწევს.

**2. null model-ზე პირობითობა `8`-ს არ არეაბილიტირებს.** `|O(E)| = 4`-ზე (სადაც `8` საერთოდ მიღწევადია) `8` ამ corpus-ის ყველაზე ხშირი `C(E)`-ია — `18.89%`, `15.86%`-ის წინააღმდეგ. მაგრამ ეს პიკი stratum-ის თვისება არ არის: მას სამი `_div` family აწვდის (`13_248` / `13_634`), და მათ გარეშე stratum-ის mode `4`-ია, ხოლო `8`-ის წილი `0.74%` — `25.7`-ჯერ ნაკლები; ერთი family-ის ამოღებაც კი აბრუნებს mode-ს `4`-ზე (§5.1). ე.ი. პირობითობა null model-ს ხსნის და **არა** corpus-ს: პირობითი განაწილება ზუსტად ისევე family-mix-relative-ია, როგორც გლობალური. დამფუძნებელი `8` არც პირობითობით ხდება "თავისი stratum-ის ტიპური შედეგი" — ის იმ სამი shape-ის ტიპური შედეგია, რომლებსაც `8` ჭერად აქვთ.

**3. Structure და semantics ორი სხვადასხვა ტიპის სიდიდეა.** structural tier coefficient-invariant-ია: `1_048_576` expression-ზე მხოლოდ `16` განსხვავებული structural გაზომვაა. semantic tier კი არ არის: იმავე template-ზე coefficient-ები `C(E)`-ს `1`-დან `8`-მდე (ან `18`-მდე) ამოძრავებენ. ამიტომაა ორ tier-ად გაყოფა არა optimization, არამედ იმის აღიარება, რომ structural კითხვას მილიონი expression არ სჭირდება, semantic კითხვას კი — სჭირდება.

**4. `C(E)` token stream-ის თვისებაა და არა მათემატიკისა.** `2*x + 3 - 4/5*x` და `2*x + 3 - 4 / 5*x` ერთი და იგივე ფუნქციაა; პირველს `C = 4` აქვს, მეორეს `C = 13`. სხვაობა მხოლოდ ის არის, რომ `4/5` დაუშორებლად ერთი number token-ია. ვინც `C(E)`-ს "expression-ის თვისებად" წაიკითხავს, ცდება — ის token sequence-ის თვისებაა.

**5. Control grammar-ის ზუსტი ადგილი.** `G0` corpus-ის `31.25%`-ზე აშენებს ხეს, რომელსაც არცერთი strict ordering ვერ აშენებს, მაგრამ `0` expression-ზე აღწევს ახალ semantic class-ს. tied level structural სიახლეა და არა semantic სიახლე.

**6. "რას აიაფებს" — ერთადერთი სუფთა პასუხი depth-ია.** degree (`71.44%`) და division count (`31.02%`) სხვაობა **სხვა პასუხია** და არა იაფი პასუხი. სუფთა მოგებაა `free_depth_saving`: corpus-ის `60.22%`-ზე არსებობს grammar, რომელიც იმავე semantic class-ს უფრო მოკლე critical path-ით აღწევს, ხოლო `21.11%`-ზე default-ური `G0` **არ** არის ამ ოპტიმალურთა შორის. მაქსიმალური უფასო მოგება `3` დონეა.

## შეზღუდვები

- Corpus ერთცვლადიანია (`x`; დამფუძნებელი expression `t`-ით). multi-variable family არ არის.
- Coefficient-ები არაუარყოფითი მთელებია — structural corpus: `free 0..15`, `nonzero 1..16`; semantic corpus: `free 0..8`, `nonzero 1..9`. უარყოფითი მნიშვნელობა არ არის, რადგან Generation 1 tokenizer-ს unary minus არ აქვს.
- `16` family დაპროექტებული ნაკრებია და არა expression space-ის შემთხვევითი ნიმუში. **მთლიანი განაწილება corpus-relative-ია**: family mix-ის შეცვლა mode-საც შეცვლის. **support size-ზე პირობითი განაწილებაც ზუსტად ისევე corpus-relative-ია** — ის იმავე family mix-ზე იზომება და `|O| = 4`-ის mode `8` სამი `_div` family-ს ეყრდნობა (§5.1-ის ablation). ერთადერთი გადატანადი შედეგი **per-family ცხრილია**, რადგან ის family-ებს არ ასაშუალოებს; არც ერთი გლობალური და არც ერთი პირობითი რიცხვი გადატანადი არ არის.
- Structural tier-ის `1e6` მასშტაბი **დამატებით ინფორმაციას არ ატარებს** — ის null model-ის stress test-ია (`26_214_400` parse, `0` დარღვევა) და არა უფრო მდიდარი განაწილება.
- `degree` და `division count` class-ის გამოქვეყნებული canonical text-იდან იკითხება `sympify`-ით. `sympify_failures` ორივე run-ზე `0`-ია, მაგრამ ეს round-trip-ია და არა იგივე ობიექტი.
- `zoo`/`nan` class-ები ცალკე ითვლება და degree-ის სტატისტიკაში არ შედის; ისინი corpus-ის `3.46%`-ია.
- `canonicalize()` `domain`-ს უპირობოდ `R`-ს აბრუნებს, ამიტომ class key-ის სამი კომპონენტიდან რეალურად მხოლოდ ორს შეუძლია დისკრიმინაცია (0024-ის Class-key audit).
- `depth` არის parse tree-ის critical path და არა შესრულების დრო; ეს cost proxy-ია.
- Wall clock მანქანის დატვირთვაზეა დამოკიდებული და ამ სესიაში სხვა worker-ები პარალელურად მუშაობდნენ.

## Evidence-ის კლასიფიკაცია

- **Observations** (executable, ამ corpus-ზე ზუსტად რეპროდუცირებადი): ყველა განაწილება, count და rate; per-family ცხრილი; support size-ზე პირობითი განაწილება და მისი ablation (§5.1); collapse-ის ოთხი მოვლენის სიხშირე და მაგალითები. semantic განაწილება სამ სრულ run-ზე იდენტურია.
- **Mechanically forced (null model, აღმოჩენა არ არის)**: support size განაწილება; support block structure; `0` bound violation და `0` block violation; დერივებული ბოჭვა `C(E) <= all-25 distinct AST <= factorial(|O(E)|) + 1`. მჭიდრო ფორმა `C(E) <= strict distinct AST <= factorial(|O(E)|)` **mechanically forced არ არის** — ის `control_adds_a_class = 0`-ს ეყრდნობა, რაც გაზომვაა.
- **Corpus-relative**: გლობალური mode `4` და mean `7.94`; **და ასევე support size-ზე პირობითი განაწილება** — `|O| = 4`-ის mode `8` სამი `_div` family-ს ეყრდნობა და მათ ამოღებაზე `4`-ზე გადადის (§5.1). სამივე family mix-ს მისდევს.
- **Assertion და არა გაზომვა**: „structural path SymPy-ს არ იძახებს" — მტკიცებულება `test_structural_path_calls_no_sympy`-ია და არა counter (§1).
- **გაზომილი უარყოფითი შედეგები**: (a) structural tier coefficient-invariant-ია, ე.ი. `1e6` structural expression `16` გაზომვას უდრის; (b) `control_adds_a_class = 0` — `G0` ვერცერთხელ ვერ აღწევს ახალ semantic class-ს.
- **არ არის claimed**: რომ per-family mode-ები ამ `16` template-ის გარეთ განზოგადდება; რომ `8`-ს რაიმე გამორჩეული სტატუსი აქვს grammar space-ში; რომ `C(E)` განაწილება უცვლელი დარჩება სხვა family mix-ზე.

## ვალიდაცია

### 1. 0024-ის კალიბრაცია — გაშვებამდე

`calibration_report()` 0024-ის **საკუთარ** `3125`-expression-იან corpus-ს ატარებს **ამ** მოდულის semantic record-ში (და არა 0024-ის კოდის გზაზე):

```text
observed  = {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}
expected  = {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}
reproduces = True     mode = 4
```

`test_calibration_reproduces_the_0024_distribution` ამას test-ადაც პინავს. ეს ფაილის ყველაზე ნელი test-ია და განზრახაა ასეთი: `3125`-ის ქვესიმრავლე იმ განაწილებას შეადარებდა, რომელიც არავის გამოუქვეყნებია. (მეორე test, რომელიც სრულ corpus-ს ეხება, `test_the_founding_token_stream_is_not_in_the_corpus`-ია — ის მხოლოდ source-ებს აგენერირებს და არაფერს parse-ავს.)

### 2. Null model-ის აუდიტი მასშტაბზე

```text
1_048_576 expression x 25 grammar = 26_214_400 parse
bound violations          : 0
support block violations  : 0
```

### 3. Partition membership `analyze_expression`-თან

`test_semantic_tier_agrees_with_analyze_expression_on_partition_membership` ექვს family-ზე ამოწმებს, რომ semantic tier-ის partition **წევრობით** ემთხვევა `analyze_expression`-ისას; `test_every_family_representative_has_a_consistent_record` იმავეს იაფ ნახევარს სვამს ყველა `16` family-ზე.

### 4. Structural path SymPy-ს არ იძახებს

`test_structural_path_calls_no_sympy` `parseatlas.canonical`-ის `to_sympy`, `simplify` და `solve`-ს ჩაანაცვლებს ფუნქციით, რომელიც `AssertionError`-ს აგდებს, და structural sweep მაინც ბოლომდე გადის. **ეს არის ამ claim-ის ერთადერთი მტკიცებულება** — report და sweep აღარ ბეჭდავენ `sympy_calls: 0`-ს, რადგან ის counter არ იყო, literal იყო (§1). test ისიც ამოწმებს, რომ ველი assertion-ად არის მონიშნული და რომ hardcoded counter უკან არ დაბრუნებულა.

### 5. Sequential == parallel და chunking

`test_structural_sequential_and_parallel_agree`, `test_semantic_sequential_and_parallel_agree`, `test_chunking_does_not_change_the_structural_result`.

### 6. Corpus რეპროდუცირებადობა

`test_generator_is_deterministic_across_two_calls`, `test_index_addressing_matches_the_materialized_corpus`, `test_generation_block_rebuilds_the_same_sources` — ბოლო spec-ს **მხოლოდ** `generation()` ბლოკიდან ხელახლა აწყობს და იმავე source-ებს იღებს.

### 7. დამფუძნებელი expression corpus-ის გარეთაა

`test_the_founding_token_stream_is_not_in_the_corpus` `104_976`-ვე source-ს ამოწმებს: `2*t + 1 - t/2` არ არის, `2*x + 1 - 1*x/2` არის, და შიშველი `- x/` კუდი არსად არ ჩნდება.
`test_the_founding_stream_and_its_nearest_family_member_differ_structurally` პინავს `14` vs `17` strict AST-ს და იმას, რომ `17` family-ის მნიშვნელობაა და არა ერთი წევრისა.

### 8. Family-mix ablation

`test_family_mix_ablation_publishes_the_conditional_distribution_without_its_biggest_families` პინავს, რომ `family_mix_ablation` **იმავე** record-ებზე **იმავე** პირობითობაა და არა მეორე, სხვაგვარად ნაანგარიშევი ცხრილი: ყოველი stratum-ის განაწილება ზუსტად დარჩენილი record-ებისაა.

### 9. Tests

Review-მდე:

```text
tests/test_scale_atlas.py     38 passed in 123.32s   (მანქანა დატვირთული)
tests/test_scale_atlas.py     38 passed in  30.27s   (მანქანა თავისუფალი)
full suite                   493 passed in 371.64s   (მანქანა დატვირთული)
full suite                   493 passed in 242.33s   (მანქანა თავისუფალი)
```

Review-ის შემდეგ (ოთხი ახალი test: `test_the_founding_token_stream_is_not_in_the_corpus`,
`test_the_founding_stream_and_its_nearest_family_member_differ_structurally`,
`test_family_mix_ablation_publishes_the_conditional_distribution_without_its_biggest_families`,
`test_a_sweep_records_the_plan_it_actually_ran`):

```text
tests/test_scale_atlas.py     42 passed in  86.42s   (მანქანა დატვირთული)
full suite         2 failed, 497 passed in 590.99s   (მანქანა დატვირთული)
```

`42` არის ის რიცხვი, რომელსაც ეს card აკონტროლებს — `38`-იდან `+4`, და ყველა გადის.
სრული suite-ის ორივე ჩავარდნა **სხვა card-ის ფაილშია** — `tests/test_outer_quotient.py`
(`test_corpus_spans_affine_quadratic_and_rational_shapes` და
`test_coarsening_holds_for_every_pair_in_the_corpus`), რომელიც ამ ხეს ამავე დროს ემატებოდა და
`scale_atlas`-ს საერთოდ არ იმპორტირებს (შემოწმებულია). ეს რიცხვები აქ იმიტომ წერია, რომ ისინი
გაზომილია და არა იმიტომ, რომ ამ card-ს ეკუთვნის.

`test_worker_count_is_derived_from_the_observed_cores` review-მდე ტავტოლოგია იყო: ის
`workers=1`-ს გადასცემდა და შემდეგ `workers == 1`-ს ამოწმებდა. ახლა ის `workers=None` გზას ამოწმებს
ოთხ სხვადასხვა observed core count-ზე (`2, 4, 16, 64` -> `1, 3, 15, 63`), ე.ი. headroom-ის წესსაც
და იმასაც, რომ რიცხვი derived-ია და არა კონსტანტა; ძველი მტკიცებები ცალკე test-ში გადავიდა
(`test_a_sweep_records_the_plan_it_actually_ran`), სადაც ისინი იმას ამოწმებენ, რაც მართლა არიან —
რომ report-ში დაბეჭდილი plan გაშვებული plan-ია.
