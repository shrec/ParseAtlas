# ParseAtlas ექსპერიმენტი 0029: რა ხდის expression-ს grammar-sensitive-ს?

## შედეგი ერთი აბზაცით

**პასუხი შერეულია და ორივე ნახევარი გაზომილია.** Operator support-ის ფიქსაციის შემდეგ
association-ს **ცამეტი** დამოუკიდებელი (parser-ის არა-გადათქმელი) feature ინარჩუნებს, და მათგან
ყველაზე ძლიერი **token shape-ის იდენტობაა**: რვა feature — `operator_count`, `leaf_count`,
`variable_leaf_count`, `max_operator_multiplicity`, `repeated_operator_count`, `operator_profile`,
`repetition_pattern`, `operator_word_catalan_count` — ზუსტად ერთსა და იმავე within-support
weighted `eta2 = 0.7500`-ს ატარებს (`rho k=3 = +0.7862`), ე.ი. `11.2`-ჯერ მეტს, ვიდრე
`unit_multiplier_count`-ის `0.0669`. **მაგრამ** ეს რვა feature `|O(E)| = 4`-ის შიგნით მუდმივია:
ისინი მხოლოდ ერთ stratum-ში მუშაობენ და ამ corpus-ზე პრაქტიკულად კითხულობენ "რომელი
template-ია". **ორივე** stratum-ში მხოლოდ ერთი დამოუკიდებელი კლასი იცვლება — **coefficient
degeneracy** (`unit_literal_count`, `unit_multiplier_count`, `degenerate_coefficient`). ე.ი. ის
ერთადერთი დამოუკიდებელი კლასია, რომელიც support size-ის **ორივე** მნიშვნელობაზე მოქმედებს — და
არა ერთადერთი, რომელიც საერთოდ ინარჩუნებს association-ს.

`S(E)` **ზუსტად** მუდმივი ხდება corpus-ის `2725 / 3125` (`0.872`) expression-ზე, როცა
conditioning ხდება token shape-სა და ორ unit-coefficient count-ზე (literal `1` `*`-ის მეზობლად და
`/`-ის შემდეგ); out-of-sample MAE `0.003896` baseline-ის `0.050699`-ის წინააღმდეგ (`92.3%`
შემცირება), `0` unseen cell, ორივე parity fold ერთმანეთს **ოთხ ათწილადში** ემთხვევა
(`even_fit 0.003896899182` და `odd_fit 0.003894405964` — მეხუთე ათწილადში ისინი უკვე
განსხვავდებიან). **მაგრამ** ეს predictor **არცერთ ახალ token shape-ზე არ გადადის**:
leave-one-shape-out-ზე მისი MAE **ზუსტად** baseline-ს უდრის (`0.060842 == 0.060842`, დამრგვალების
გარეშე `0.060841739130 == 0.060841739130`) და `3125 / 3125` cell unseen-ია, რადგან თითოეული cell
თავის shape-ს ასახელებს. ე.ი. shape-ის ნახევარი ხუთელემენტიანი lookup table-ია და
არა ახსნა; coefficient-ის ნახევარი კი ნამდვილი, out-of-sample დადასტურებული და ალგებრულად ახსნადი
ეფექტია.

თვითონ trap feature `support_size` სუსტი predictor-ია (`eta2 = 0.0676`, out-of-sample error
შემცირება `2.3%`), ამიტომ T6 ამ შედეგს არ შეუჭამია — მაგრამ shape-ის signal-ს მისი ორი მონათესავე,
`parenthesis_pair_count` და `distinct_ast_count`, ატარებს, და ორივე parser-ის გადათქმაა.

## მიზანი

ROADMAP-ის T4 ამ კითხვას პროექტის საკუთარ ცენტრალურ ღია კითხვად ასახელებს, T15 კი მას კვლავ
გადაუწყვეტლად იმეორებს. 0017-მა დააკვირდა, რომ ზოგი token sequence ოცდაოთხივე strict grammar-ს ერთ
semantic class-ში ტოვებს, ზოგი კი იშლება. 0024-მა ეს distribution corpus-ის მასშტაბით გაზომა,
მაგრამ **არ ახსნა**. აქ იზომება ზუსტად ის, რაც ახსნას falsifiable-ს ხდის:

```text
არსებობს თუ არა cheap structural feature-ების პატარა set,
რომელზე conditioning-იც S(E)-ს თითოეული cell-ის შიგნით (თითქმის) მუდმივს ხდის —
და რჩება თუ არა რამე, როცა operator support ფიქსირებულია?
```

### Trap, რომელიც მთელი სირთულეა

0019-ის (T6) support reduction პასუხის ნაწილს mechanically აიძულებს: თუ `O(E)`-ს ზომა `k`-ია,
`24` strict grammar `k!` block-ად იყოფა და თითო block-ის შიგნით ყველა grammar byte-identical AST-ს
აშენებს, ე.ი. აუცილებლად ერთსა და იმავე semantic class-ში ხვდება. `|O(E)| == 1`-იანი expression
**ვერ დაიშლება**, რაც არ უნდა იყოს მისი მათემატიკა. ამიტომ `|O(E)|`-ზე აშენებული predictor
parser-ს გადაამბობს და არა მათემატიკას.

Feature set-ში ოთხი feature `restates_the_parser`-ად არის მონიშნული:

| feature | რატომ |
| --- | --- |
| `support_size` | თვითონ T6-ის block structure |
| `parenthesis_pair_count` | ფრჩხილი split-ს binding power-ის წაკითხვამდე აფიქსირებს — ზუსტად ისეთივე mechanical იძულებაა |
| `distinct_ast_count` | parse-ის შედეგია და არა მისი input |
| `strict_reachable_tree_count` | 0023-ის symbolic decision procedure, რომელიც იმავე შედეგს წინასწარმეტყველებს |

ყოველი association ორჯერ ქვეყნდება: overall და **fixed support size-ის შიგნით**. **within-stratum
რიცხვი არის შედეგი**, overall კი კონტექსტი.

## Feature set

`src/parseatlas/sensitivity_predictors.py`-ის `FEATURES` არის **დახურული** set: `21` feature,
თითოეული იაფი (ერთი `tokenize`, `24` parse, plus operator word-ზე cache-ირებული Catalan
enumeration) და თითოეული დამოუკიდებლად მოტივირებული. Set დახურულია განზრახ: feature, რომელიც იმის
შემდეგ გამოიგონებოდა, რაც ვნახეთ რომელი cell არ ჩამოიშალა, პასუხზე იქნებოდა მორგებული და არა მისი
წინასწარმეტყველება.

| feature | kind | origin | parser? | მოტივაცია |
| --- | --- | --- | --- | --- |
| `support_size` | ordered | token | **yes** | `\|O(E)\|`, T6-ის სიდიდე |
| `operator_count` | ordered | token | | სულ რამდენი operator token |
| `leaf_count` | ordered | token | | number + name token-ები |
| `variable_leaf_count` | ordered | token | | ცვლადი leaf-ები |
| `distinct_variable_count` | ordered | token | | განსხვავებული ცვლადების რაოდენობა |
| `parenthesis_pair_count` | ordered | token | **yes** | explicit ფრჩხილი split-ს წინასწარ აფიქსირებს |
| `division_operator_count` | ordered | token | | `/` როგორც **operator** |
| `has_division` | ordered | token | | იმავეს presence ფორმა |
| `max_operator_multiplicity` | ordered | token | | occurrence multiset-ის ყველაზე დიდი გამეორება |
| `repeated_operator_count` | ordered | token | | რამდენი operator type მეორდება |
| `operator_profile` | categorical | operator-word | | თვითონ occurrence multiset, `'* x3, + x1, - x1'` |
| `repetition_pattern` | categorical | operator-word | | მხოლოდ multiplicity-ების multiset, `'3+1+1'` |
| `unit_literal_count` | ordered | coefficient | | literal `1`-ები |
| `zero_literal_count` | ordered | coefficient | | literal `0`-ები |
| `unit_multiplier_count` | ordered | coefficient | | literal `1` `*` token-ის მეზობლად |
| `unit_divisor_count` | ordered | coefficient | | literal `1` პირდაპირ `/`-ის შემდეგ |
| `degenerate_coefficient` | ordered | coefficient | | presence ფორმა: სადმე `0` ან `1` |
| `fractional_literal_count` | ordered | coefficient | | literal, რომელიც tokenizer-მა rational-ად წაიკითხა (`/` რომელიც **არ** არის operator) |
| `distinct_ast_count` | ordered | parse | **yes** | განსხვავებული AST-ები `24` strict grammar-ზე |
| `operator_word_catalan_count` | ordered | operator-word | | binary tree-ები **operator word-ზე**; ფრჩხილი მისთვის უხილავია, ამიტომ ფრჩხილიანი token sequence მკაცრად ნაკლებ tree-ს უშვებს, ვიდრე ეს რიცხვი ითვლის |
| `strict_reachable_tree_count` | ordered | operator-word | **yes** | 0023-ის decision procedure-ით მიღწევადი Catalan tree-ები, ფრჩხილების იგნორირებით |

**სახელის შესახებ.** `operator_word_catalan_count` და `strict_reachable_tree_count` ორივე
**operator word-ზე** ითვლება, ფრჩხილის დანახვის გარეშე, და ორივე სახელი სწორედ ამას ამბობს.
არცერთი მათგანი არ არის იმ tree-ების რაოდენობა, რომელსაც **token sequence** უშვებს: explicit
ფრჩხილი tree-ებს binding power-ის წაკითხვამდე აშორებს, ამიტომ ფრჩხილიანი source მკაცრად ნაკლებს
უშვებს. `rational` family ამ ორ feature-ზე `42`-სა და `17`-ს იღებს, მაშინ როცა `24` strict
grammar-ზე გაზომილი distinct AST count `4`-ია — და სწორედ ამ სხვაობის ტარებისთვის არსებობს
ცალკე `parenthesis_pair_count`. (ეს feature ადრე `catalan_tree_count` ერქვა; სახელი შეიცვალა
სწორედ იმიტომ, რომ ის token sequence-ის და არა operator word-ის თვისებას ჰგავდა.)

არსებული module-ები ხელახლა არ არის დაწერილი: `support_reduction.operator_support` და
`serialized_ast`, `ast_space.enumerate_parenthesizations` და `canonical_leaves`,
`reachability.strict_reachable`, `corpus_matrix.corpus_records` / `normalize_corpus` /
`resolve_worker_count`, `grammar_matrix.representation_sensitivity` (`corpus_records`-ის გავლით).

ორი feature ამ corpus-ზე **მუდმივია** და ამიტომ ვერაფერს წინასწარმეტყველებს:
`distinct_variable_count` (ყველა expression-ს ერთი ცვლადი აქვს) და `zero_literal_count`
(coefficient set `0`-ს გამორიცხავს). ეს corpus-ის შეზღუდვაა და არა feature-ების.

## Corpus

იგივე deterministic `3125`-expression corpus, რომელიც 0024-მა გამოაქვეყნა
(`corpus_matrix.generate_corpus`), ცვლილების გარეშე. Ground truth **ხელახლა გამოყვანილია** და არა
0024-იდან გადმოწერილი — ყველა რიცხვი დაემთხვა:

```text
S(E) : {0.0: 25, 0.043478: 200, 0.086957: 275, 0.130435: 1500, 0.173913: 625, 0.217391: 100, 0.304348: 400}
C(E) : {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}
rigid 25 (ყველა rational family-დან) | sensitive 3100 | mean S 0.153739 | max S 0.304348 = 7/23
support size counts : {3: 1875, 4: 1250}
```

**განსხვავება 0024-თან: არცერთი.**

corpus-ს მხოლოდ **ხუთი** distinct operator word აქვს (თითო family-ზე ერთი), რადგან template-ები
operator-ების თანმიმდევრობას აფიქსირებენ და coefficient-ები მხოლოდ leaf-ებს ცვლიან:

| family | operator word | `\|O(E)\|` | ფრჩხილები |
| --- | --- | --- | --- |
| linear | `* + - * /` | 4 | 0 |
| quadratic | `* * + * -` | 3 | 0 |
| cubic | `* * * + * * - * +` | 3 | 0 |
| rational | `* + / * -` | 4 | 2 |
| mixed_chain | `+ * -` | 3 | 0 |

ეს არის ამ ექსპერიმენტის მთავარი შეზღუდვის წყარო და ქვემოთ ცალკე დაბრუნდება.

## Metric

```text
S(E) = (strict semantic classes - 1) / 23        grammar_matrix.representation_sensitivity
C(E) = strict semantic classes
```

ორივე `corpus_matrix.corpus_records`-იდან იკითხება, ე.ი. აქ 0024-ის **იმავე** გაზომვაა და არა
მისი მეორე იმპლემენტაცია.

- **ordered feature** — Spearman rank correlation, tie-corrected (average ranks; ყველა feature აქ
  მძიმედ tied-ია, ამიტომ tie correction სავალდებულოა).
- **categorical feature** — between-group spread; rank correlation განუსაზღვრელია.
- **ორივესთვის** — `eta2` (between-group sum of squares / total sum of squares) **plus group sizes
  და per-group mean**. Coefficient მარტო არასდროს ქვეყნდება: `5`-expression-იან group-ზე
  გამოთვლილი spread არ არის findings.
- **explained_partition** — feature set-ზე conditioning; feature set **ხსნის** `S(E)`-ს ზუსტად
  მაშინ, როცა ყოველი cell-ის within-cell range `0.0`-ია.
- **holdout_check** — index parity split (`row['index'] % 2`), ზუსტად ისე, როგორც 0024 ყოფს
  corpus-ს: არც randomness, არც seed. Cell-mean predictor იჯდება ერთ ნახევარზე და ფასდება მეორეზე,
  **ორივე მიმართულებით**. Unseen cell fit-ის global mean-ზე ვარდება და ცალკე ითვლება.
- **leave_one_group_out_check** — უფრო მკაცრი deterministic hold-out: მთელი token shape იჭრება.

## დაკვირვებული შედეგები

### 1. Overall association — კონტექსტი, არა შედეგი

| feature | rho | eta2 | group sizes |
| --- | --- | --- | --- |
| `distinct_ast_count` | `+0.6261` | `0.5850` | `{4: 625, 5: 1875, 17: 625}` |
| `operator_count` | `+0.4638` | `0.0624` | `{3: 625, 5: 1875, 9: 625}` |
| `parenthesis_pair_count` | `-0.4270` | `0.1676` | `{0: 2500, 2: 625}` |
| `fractional_literal_count` | `-0.3704` | `0.0902` | `{0: 2205, 1: 715, 2: 205}` |
| `variable_leaf_count` | `+0.3218` | `0.1443` | `{1: 625, 2: 1250, 3: 625, 6: 625}` |
| `unit_literal_count` | `-0.2232` | `0.0612` | `{0: 1408, 1: 1248, 2: 408, 3: 58, 4: 3}` |
| `degenerate_coefficient` | `-0.1984` | `0.0456` | `{0: 1408, 1: 1717}` |
| `unit_multiplier_count` | `-0.1840` | `0.0486` | `{0: 2020, 1: 965, 2: 135, 3: 5}` |
| `unit_divisor_count` | `-0.1183` | `0.0090` | `{0: 3000, 1: 125}` |
| `support_size` | `+0.1111` | `0.0676` | `{3: 1875, 4: 1250}` |
| `strict_reachable_tree_count` | `+0.1111` | `0.0676` | `{5: 1875, 17: 1250}` |

**ეს ცხრილი `21` feature-იდან `11`-ს აჩვენებს.** დანარჩენი ათი გამოტოვებული არ არის: მათი
(`rho`, `eta2`) წყვილი **ბიტში** ემთხვევა ერთ-ერთ ნაჩვენებ row-ს (თვითონ ეს დამთხვევა ვალიდაცია
`2`-ის ბოლო ხაზზეა verbatim შემოწმებული):

| ნაჩვენები row | ბიტში იმავე (`rho`, `eta2`)-ით |
| --- | --- |
| `support_size` და `strict_reachable_tree_count` | `division_operator_count`, `has_division` |
| `operator_count` | `leaf_count`, `repeated_operator_count`, `operator_word_catalan_count` |
| `variable_leaf_count` | `max_operator_multiplicity` |

დარჩენილი ოთხი: `operator_profile` და `repetition_pattern` categorical-ია (`rho` განუსაზღვრელია)
და `eta2 = 0.1443` აქვს; `distinct_variable_count` და `zero_literal_count` ამ corpus-ზე მუდმივია
(`eta2 = 0.0`). ცხრილის `group sizes` სვეტი ნაჩვენები feature-ისაა — folded feature-ს იმავე
ზომის, მაგრამ სხვა label-ებიანი group-ები აქვს. სრული `21`-row ცხრილი ვალიდაცია `2`-შია, ხოლო
შემდეგი სექციის ცხრილი — რომელიც შედეგია — თვითონაც სრულია.

ორი დაკვირვება პირდაპირ ამ ცხრილიდან:

1. **`support_size`-ის overall association სუსტია** (`eta2 = 0.0676`). Trap feature მართლაც
   აიძულებს agreement-ს, მაგრამ ამ corpus-ზე `S(E)`-ს თითქმის არ წინასწარმეტყველებს. Parity
   holdout-ზე მისი MAE `0.049530`-ია baseline-ის `0.050699`-ის წინააღმდეგ — **`2.3%` შემცირება**.
2. **`strict_reachable_tree_count`-ის rho და eta2 ბიტში ემთხვევა `support_size`-ისას.** ეს
   შემთხვევითობა არ არის: 0023-ის decision procedure operator word-ზე `17`-ს აბრუნებს linear-სა და
   rational-ზე (support size `4`) და `5`-ს დანარჩენ სამზე (support size `3`), ე.ი. ამ corpus-ზე ის
   `support_size`-ის relabeling-ია და მეტი არაფერი.

### 2. Fixed support size-ის შიგნით — **ეს არის შედეგი**

```text
strata: {|O(E)| = 3 : 1875,  |O(E)| = 4 : 1250}
```

**ცხრილი სრულია — ოცდაერთივე feature, catch-all row-ების გარეშე.** სვეტი "ორივე stratum?"
აღნიშნავს feature-ს, რომელიც **ორივე** support size-ის შიგნით იცვლება; ცალკე სვეტია, რადგან
სწორედ ეს განასხვავებს "association-ს ინარჩუნებს"-ს "ორივე stratum-ში მუშაობს"-გან.

**`weighted eta2`-ის განმარტება, რადგან ორი სვეტი სხვადასხვანაირად ნორმალიზდება.** `predictor_strength`-ში `weighted_eta_squared` არის size-weighted mean იმ stratum-ებზე, სადაც feature **ცვალებადია**, და არა ყველა stratum-ზე. ამიტომ `(a)`-ს რვა feature-ის `0.7500` არის მხოლოდ `k=3`-ის ფიგურა და `3125`-იდან `1875` row-ს ფარავს, ხოლო `unit_multiplier_count`-ის `0.0669` სრულ `3125`-ს. ანუ **გამოქვეყნებული `11.2×` ორ სხვადასხვანაირად ნორმალიზებულ სიდიდეს ადარებს.**

მოდული ითვლის `pooled_eta_squared`-საც, რომელიც ყველა stratum-ზე ნორმალიზდება: იქ იგივე შედარება არის `0.4500` vs `0.0669`, ანუ **`6.7×`**. ორივე რიცხვი სწორია თავის განმარტებაში; ქვემოთ მოცემულ ცხრილში `weighted eta2` სვეტი ზემოთ აღწერილი, varying-strata ნორმალიზაციისაა. `eta2 k=3` და `eta2 k=4` სვეტები ცალ-ცალკეა და ნორმალიზაციისგან დამოუკიდებელია — ეს არის მიზეზი, რის გამოც ისინი აქვე დგას.

| feature | rho k=3 | eta2 k=3 | rho k=4 | eta2 k=4 | weighted eta2 | ორივე stratum? | parser? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `operator_count` | `+0.7862` | `0.7500` | constant | `0.0` | `0.7500` | | |
| `leaf_count` | `+0.7862` | `0.7500` | constant | `0.0` | `0.7500` | | |
| `variable_leaf_count` | `+0.7862` | `0.7500` | constant | `0.0` | `0.7500` | | |
| `max_operator_multiplicity` | `+0.7862` | `0.7500` | constant | `0.0` | `0.7500` | | |
| `repeated_operator_count` | `+0.7862` | `0.7500` | constant | `0.0` | `0.7500` | | |
| `operator_profile` | — | `0.7500` | constant | `0.0` | `0.7500` | | |
| `repetition_pattern` | — | `0.7500` | constant | `0.0` | `0.7500` | | |
| `operator_word_catalan_count` | `+0.7862` | `0.7500` | constant | `0.0` | `0.7500` | | |
| `parenthesis_pair_count` | constant | `0.0` | `-0.7733` | `0.6233` | `0.6233` | | **yes** |
| `distinct_ast_count` | constant | `0.0` | `+0.7733` | `0.6233` | `0.6233` | | **yes** |
| `fractional_literal_count` | `-0.6058` | `0.3613` | constant | `0.0` | `0.3613` | | |
| `unit_literal_count` | `-0.0825` | `0.0178` | `-0.4191` | `0.1636` | `0.0761` | **yes** | |
| `unit_multiplier_count` | `-0.0513` | `0.0359` | `-0.3759` | `0.1134` | `0.0669` | **yes** | |
| `degenerate_coefficient` | `-0.0877` | `0.0158` | `-0.3653` | `0.1230` | `0.0587` | **yes** | |
| `unit_divisor_count` | constant | `0.0` | `-0.1730` | `0.0329` | `0.0329` | | |
| `support_size` | constant | `0.0` | constant | `0.0` | — | | **yes** |
| `strict_reachable_tree_count` | constant | `0.0` | constant | `0.0` | — | | **yes** |
| `division_operator_count` | constant | `0.0` | constant | `0.0` | — | | |
| `has_division` | constant | `0.0` | constant | `0.0` | — | | |
| `distinct_variable_count` | constant | `0.0` | constant | `0.0` | — | | |
| `zero_literal_count` | constant | `0.0` | constant | `0.0` | — | | |

`unit_multiplier_count`-ის group sizes: `k=3` → `{0: 1220, 1: 565, 2: 85, 3: 5}`,
`k=4` → `{0: 800, 1: 400, 2: 50}`.

აქედან ოთხი გაზომილი ფაქტი:

**(a) ყველაზე ძლიერი დამოუკიდებელი within-support signal token shape-ის იდენტობაა და არა
coefficient-ები.** რვა feature — `operator_count`, `leaf_count`, `variable_leaf_count`,
`max_operator_multiplicity`, `repeated_operator_count`, `operator_profile`, `repetition_pattern`,
`operator_word_catalan_count` — **ზუსტად** ერთსა და იმავე `eta2 = 0.7500`-სა და `rho = +0.7862`-ს
ატარებს `|O(E)| = 3`-ის შიგნით, ე.ი. `11.2`-ჯერ მეტ weighted `eta2`-ს, ვიდრე
`unit_multiplier_count`. ისინი `parser-restating`-ად მონიშნული არ არიან და support size-ის
ფიქსაციის შემდეგაც ინარჩუნებენ association-ს — ეს გაზომილი დადებითი შედეგია და თავიდანვე უნდა
ითქვას. **მაგრამ** ამ corpus-ზე რვავე ერთსა და იმავე დაყოფას იძლევა: ვალიდაცია `2`-ის
`k=3 group sizes` ბლოკში თითოეული ზუსტად სამ მნიშვნელობას იღებს, თითოს `625` expression-ით —
ე.ი. თითო template-ზე ერთს — და `|O(E)| = 4`-ის შიგნით ყველა მუდმივია. ტოლი `eta2` ერთი და იმავე
partition-ის გაზომვაა. ე.ი. ისინი აღწერენ იმას, "რომელი template-ია", და მათი ჭეშმარიტი
ღირებულება leave-one-shape-out-ზე იზომება, სადაც შედეგი უარყოფითია (სექცია `7`).

**(b) `strict_reachable_tree_count` support size-ის ფიქსაციის შემდეგ არაფერს ხსნის.** ის ორივე
stratum-ის შიგნით მუდმივია. 0023-ის symbolic reachability count, operator word-იდან გამოთვლილი,
`S(E)`-ს ამ corpus-ზე მხოლოდ `|O(E)|`-ის მეშვეობით ეხება. **ეს გაზომილი უარყოფითი შედეგია.**

**(c) `|O(E)| = 4`-ის შიგნით ყველა operator-multiset feature მუდმივია.** `linear` და `rational`
ატარებენ **ბიტში იდენტურ** operator multiset-ს (`* x2, + x1, - x1, / x1`), იდენტურ
`operator_count`-ს (`5`), `leaf_count`-ს (`6`), `variable_leaf_count`-ს (`2`),
`division_operator_count`-ს (`1`), `operator_word_catalan_count`-ს (`42`, ორივესთვის ერთი და იგივე
სწორედ იმიტომ, რომ ის ფრჩხილს ვერ ხედავს) და
`strict_reachable_tree_count`-ს (`17`) — და მათი mean `S` ერთმანეთისგან `2.6`-ჯერ განსხვავდება
(`0.253913` და `0.097391`, ამ card-ის საკუთარ run-ში ხელახლა გამოყვანილი და 0024-ის per-family
ცხრილის იდენტური). დახურულ set-ში ამ განსხვავებას მხოლოდ
**ორი** feature ხედავს: `parenthesis_pair_count` და `distinct_ast_count` — და **ორივე parser-ის
გადათქმაა**.

**(d) coefficient degeneracy ერთადერთი დამოუკიდებელი კლასია, რომელიც ორივე stratum-ში იცვლება.**
`unit_literal_count`, `unit_multiplier_count` და `degenerate_coefficient` — მხოლოდ ეს სამი
(verbatim სია ვალიდაცია `2`-ის `varies inside BOTH support sizes` ხაზზეა). მათი
within-support weighted `eta2` პატარაა (`0.0761`, `0.0669`, `0.0587`) — `(a)`-ს რვა feature-ის
`0.7500`-ზე `11.2`-ჯერ ნაკლები — რადგან stratum-ის შიგნით template-ის label ისევ დომინირებს.
ე.ი. ეს კლასი ყველაზე **სუსტი** გადარჩენილი signal-ია და არა ყველაზე ძლიერი; მისი ერთადერთობა
ვიწროდ იმაშია, რომ ის ერთადერთია, რომელიც ორივე stratum-ში მუშაობს.
`unit_divisor_count` მხოლოდ ერთ stratum-ში იცვლება
(`|O(E)| = 4`), რადგან მხოლოდ `linear`-ს აქვს `/` როგორც operator და მისი მარჯვენა ოპერანდი
literal-ია.

### 3. Fixed token shape-ის შიგნით — სადაც coefficient-ები ძლიერდება

როცა stratum ხდება `(operator_profile, parenthesis_pair_count)` — რაც ამ corpus-ზე ზუსტად ხუთი
template-ია, თითო `625` expression — **ყველა** shape feature განსაზღვრებით მუდმივია და მხოლოდ
coefficient-ებს შეუძლიათ რამის თქმა:

| shape (family) | n | `S` მნიშვნელობები | `eta2(unit_multiplier)` | `eta2(unit_divisor)` | `(um, ud)` collapse |
| --- | --- | --- | --- | --- | --- |
| `mixed_chain` | 625 | `0.086957, 0.130435` | `1.0000` | `0.0000` | **`1.000`** |
| `rational` | 625 | `0.0, 0.043478, 0.130435` | `1.0000` | `0.0000` | **`1.000`** |
| `cubic` | 625 | `0.173913` (მუდმივი) | — | — | **`1.000`** (ტრივიალურად) |
| `quadratic` | 625 | `0.086957, 0.130435` | `0.5000` | `0.0000` | `0.680` |
| `linear` | 625 | `0.086957 … 0.304348` | `0.0908` | `0.8094` | `0.680` |

ორ template-ზე (`mixed_chain`, `rational`) `unit_multiplier_count` **მარტო** განსაზღვრავს `S(E)`-ს
ზუსტად: `eta2 = 1.0`, Spearman `-1.0`. ეს არ არის approximation.

### 4. Predictor და მისი `18` cell

გამოქვეყნებული feature set:

```text
(operator_profile, parenthesis_pair_count, unit_multiplier_count, unit_divisor_count)
```

`18` cell, `2725 / 3125 = 0.872` expression ზუსტად ჩამოშლილი (within-cell range `0.0`),
size-weighted mean range `0.007791`, baseline range `0.304348`.

| shape | `um` | `ud` | n | `S` |
| --- | --- | --- | --- | --- |
| mixed_chain | 0 | 0 | 500 | `0.130435` |
| mixed_chain | 1 | 0 | 125 | `0.086957` |
| linear | 0 | 0 | 320 | `0.304348` |
| linear | 0 | 1 | 80 | `0.130435` |
| linear | 1 | 0 | 160 | **`0.217391, 0.304348`** |
| linear | 1 | 1 | 40 | **`0.086957, 0.130435`** |
| linear | 2 | 0 | 20 | `0.217391` |
| linear | 2 | 1 | 5 | `0.086957` |
| rational | 0 | 0 | 400 | `0.130435` |
| rational | 1 | 0 | 200 | `0.043478` |
| rational | 2 | 0 | 25 | `0.0` |
| quadratic | 0 | 0 | 400 | `0.130435` |
| quadratic | 1 | 0 | 200 | **`0.086957, 0.130435`** |
| quadratic | 2 | 0 | 25 | `0.086957` |
| cubic | 0 | 0 | 320 | `0.173913` |
| cubic | 1 | 0 | 240 | `0.173913` |
| cubic | 2 | 0 | 60 | `0.173913` |
| cubic | 3 | 0 | 5 | `0.173913` |

**Support size-ის ფიქსაციის შემდეგაც ჩამოშლა რჩება** — ე.ი. ეს არ არის `|O(E)|`-ის გადათქმა:

```text
|O(E)| = 3 : 1675 / 1875 = 0.893333    9 cell    max range 0.043478
|O(E)| = 4 : 1050 / 1250 = 0.840000    9 cell    max range 0.086957
```

### 5. სამი cell, რომელიც არ ჩამოიშალა — და ზუსტად რატომ

`400` expression (`12.8%`) სამ cell-ში რჩება. სამივეს `unit_multiplier_count == 1` აქვს. მიზეზი
გაზომვით ჩანს: **ყოველი unit multiplier არ არის მნიშვნელოვანი — მნიშვნელოვანია მხოლოდ ის,
რომელიც re-association-ს ცვლის**, და `unit_multiplier_count` პოზიციას ვერ არჩევს.

Per-parameter driver-ები (public API-იდან ხელახლა გამოყვანილი, იხ. ვალიდაცია `6`):

```text
linear       a:DRIVES b:flat c:flat d:DRIVES
quadratic    a:flat b:DRIVES c:flat d:flat
cubic        a:flat b:flat c:flat d:flat
rational     a:DRIVES b:flat c:DRIVES d:flat
mixed_chain  a:flat b:flat c:DRIVES d:flat
```

- `linear = {a}*x + {b} - {c}*x/{d}` — `a` და `c` **ორივე** unit multiplier პოზიციაა, მაგრამ
  მხოლოდ `a` ცვლის `S`-ს (`c*x/d`-ში `*` და `/` ისედაც re-associate-დებიან, ამიტომ `c == 1` ახალ
  merge-ს არ ქმნის). ამიტომ `unit_multiplier_count == 1` აერთიანებს `a == 1, c != 1`-ს და
  `a != 1, c == 1`-ს — ორ სხვადასხვა `S`-ს. აქედან cell-ები `n = 160` და `n = 40`.
- `quadratic = {a}*x*x + {b}*x - {c}/{d}` — `a` და `b` ორივე unit multiplier პოზიციაა, მაგრამ
  მხოლოდ `b` drives. აქედან cell `n = 200`.
- `rational` და `mixed_chain` — driver-ები **ზუსტად** ის პოზიციებია, სადაც unit multiplier
  შეიძლება იჯდეს, ამიტომ იქ feature exact-ია (`eta2 = 1.0`).
- `cubic` — არცერთი coefficient არ drives; `S` მუდმივია, `unit_multiplier_count` კი იცვლება. ე.ი.
  არსებობს template, სადაც coefficient degeneracy **საერთოდ არაფერს** ცვლის.

### 6. Out-of-sample: parity split

```text
halves          : {'even': 1563, 'odd': 1562}
MAE             : 0.003896        baseline MAE : 0.050699        error reduction : 92.3%
RMSE            : 0.011536
exact fraction  : 0.872000        unseen cells : 0
folds           : even_fit MAE 0.003897 (18 cell, -92.3208%)  |  odd_fit MAE 0.003894 (18 cell, -92.3114%)
fold MAE exact  : even_fit 0.003896899182  |  odd_fit 0.003894405964  |  სხვაობა 0.000002493218
fold reduction  : even_fit 0.9232082810    |  odd_fit 0.9231144079
```

ორივე fold-ის MAE **ოთხ ათწილადში** ემთხვევა (`0.0039`) და მეხუთეში უკვე განსხვავდება:
`0.003896899182` და `0.003894405964`. Error reduction-ებიც სამ ათწილადში ემთხვევა
(`0.9232082810` და `0.9231144079`). ორივე fold-მა `18`-ივე cell დაინახა, და ორჯერ გაშვება
bit-identical შედეგს იძლევა.

### 7. Out-of-sample: leave-one-shape-out — **სადაც predictor იშლება**

Parity split ორივე ნახევარში **ყველა** token shape-ს ტოვებს, ამიტომ predictor-ს არასდროს ეკითხება
shape, რომელიც არ უნახავს. მკაცრი deterministic hold-out მთელ shape-ს ჭრის:

```text
MAE 0.060842 | baseline MAE 0.060842 | exact 0.000000 | unseen cells 3125 | worst fold 0.128557
MAE == baseline MAE დამრგვალების გარეშე : 0.060841739130 == 0.060841739130 -> True

held out  mixed_chain  n=625  MAE 0.040000  unseen 625
held out  linear       n=625  MAE 0.128557  unseen 625
held out  rational     n=625  MAE 0.070435  unseen 625
held out  quadratic    n=625  MAE 0.040000  unseen 625
held out  cubic        n=625  MAE 0.025217  unseen 625
```

`MAE == baseline MAE` **ზუსტად**, და `3125 / 3125` cell unseen-ია: predictor-ის ყოველი cell თავის
shape-ს ასახელებს, ამიტომ ახალ shape-ზე ის fit-ის global mean-ს აბრუნებს და მეტს არაფერს.
**ეს არის ამ ექსპერიმენტის მთავარი უარყოფითი შედეგი.**

### 8. Exhaustive subset search — რომ არჩევანი cherry-pick არ იყოს

დახურული set-ის ორი მუდმივი feature ამოვარდა; დარჩენილ `19`-ზე `1..4` ზომის **ყველა** `5035`
subset გაიზომა იმავე parity holdout-ით:

```text
best out-of-sample MAE 0.003896, მიღწეული 12 subset-ით; ყველა იძლევა 18 cell-ს და collapsed 0.872
ყოველი საუკეთესო subset შეიცავს unit_multiplier_count-სა და unit_divisor_count-ს : True
ყოველი საუკეთესო subset შეიცავს parser-restating feature-ს                      : True

თორმეტივე optimum (verbatim, ვალიდაცია 4):
   leaf_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   max_operator_multiplicity, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   operator_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   operator_profile, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   parenthesis_pair_count, max_operator_multiplicity, unit_multiplier_count, unit_divisor_count
   parenthesis_pair_count, operator_profile, unit_multiplier_count, unit_divisor_count
   parenthesis_pair_count, repetition_pattern, unit_multiplier_count, unit_divisor_count
   repeated_operator_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   repetition_pattern, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   unit_multiplier_count, unit_divisor_count, distinct_ast_count, operator_word_catalan_count
   variable_leaf_count, parenthesis_pair_count, unit_multiplier_count, unit_divisor_count
   variable_leaf_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count

  best of size 1 : MAE 0.035284  collapsed 0.000000  :: distinct_ast_count
  best of size 2 : MAE 0.025294  collapsed 0.201600  :: unit_multiplier_count, distinct_ast_count
  best of size 3 : MAE 0.012634  collapsed 0.736000  :: operator_count, unit_multiplier_count, distinct_ast_count
  best of size 4 : MAE 0.003896  collapsed 0.872000  :: operator_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count

best PARSER-RESTATING feature-ის გარეშე : MAE 0.034206  collapsed 0.571200  (35 cell)
best support_size-ის შემცველი           : MAE 0.012634
baseline (global mean)                  : MAE 0.050699
```

ოთხი რიცხვი, რომელიც ამ block-იდან იკითხება:

1. **`unit_multiplier_count` და `unit_divisor_count` ორივე სავალდებულოა**: optimum-ს მიღწეული
   თორმეტივე subset ორივეს შეიცავს.
2. **parser-restating feature-იც სავალდებულოა**: თორმეტივე შეიცავს მინიმუმ ერთს. მათ გარეშე
   საუკეთესო შედეგი `MAE 0.034206` და collapse `0.5712`-ია, ე.ი. error reduction `92.3%`-დან
   `32.5%`-მდე ეცემა და MAE `8.8`-ჯერ იზრდება.
3. **თვითონ `support_size` ვერ ეხმარება**: მისი შემცველი საუკეთესო subset `MAE 0.012634`-ია,
   `3.2`-ჯერ უარესი optimum-ზე. Trap feature არა მხოლოდ სუსტია მარტო, არამედ საუკეთესო
   predictor-ის ნაწილიც არ არის.
4. **optimum-ის shape-ის ნახევარი ურთიერთშენაცვლებადია.** თორმეტივე subset ერთი და იმავე
   ფორმისაა: `unit_multiplier_count` + `unit_divisor_count` plus ორი feature, რომლებიც ხუთ
   template-ს ერთმანეთისგან ასხვავებენ. სექცია `2(a)`-ს რვავე feature ჩნდება მინიმუმ ერთ
   optimum-ში — `leaf_count`, `max_operator_multiplicity`, `operator_count`, `operator_profile`,
   `repeated_operator_count`, `repetition_pattern`, `variable_leaf_count`,
   `operator_word_catalan_count`. ე.ი. predictor-ს არ სჭირდება **კონკრეტული** shape feature,
   სჭირდება **რომელიმე** shape identifier: ზუსტად ის, რასაც leave-one-shape-out ანგრევს.

### 9. Multicore

Feature extraction per-item დამოუკიდებელია და default-ად process-ებზე იყოფა. Worker count
`os.cpu_count()`-იდან გამოითვლება ერთი core headroom-ით (`corpus_matrix.resolve_worker_count`-ის
ხელახალი გამოყენებით); hardcoded constant არსად არის; `workers=1` sequential path-ს აიძულებს;
pool function module-level-ია, რომ Windows `spawn`-მა ის reference-ით დაპიკლოს.

| მანქანის მდგომარეობა | sequential | 15 worker | speedup | identical? |
| --- | --- | --- | --- | --- |
| idle, run A | `2.726 s` | `2.090 s` | `1.30x` | True |
| idle, run B | `2.777 s` | `2.066 s` | `1.34x` | True |
| idle, run C | `2.492 s` | `1.932 s` | `1.29x` | True |
| მანქანაზე სხვა worker მუშაობდა | `12.536 s` | `15.871 s` | `0.79x` | True |
| მანქანაზე რამდენიმე worker მუშაობდა (rework run) | `15.570 s` | `35.617 s` | `0.44x` | True |

Feature extraction expression-ზე ერთი `tokenize` plus `24` parse-ია — დაახლოებით მილიწამი — და
Catalan/reachability ნახევარი operator word-ზეა cache-ირებული (corpus-ს ხუთი word აქვს). ამიტომ
spawn-ის ფიქსირებული ფასი (ახალი interpreter plus sympy import chain) მოგების უმეტესობას ჭამს:
idle host-ზე `1.3x` რჩება, დატვირთულზე კი **ნიშანი იცვლება** — `0.79x` ერთი მეზობელი
worker-ისას და `0.44x` რამდენიმესას. ეს მანქანის და არა კოდის გაზომვაა, და ის ჩაწერილია და არა
დამალული. Parallelism მხოლოდ სიჩქარეს ცვლის: sequential და parallel rows ხუთივე გაზომვაში
bit-identical იყო და ეს test-ითაც არის დაპინული.

`feature_table`-ის ძვირი ნახევარი — `S(E)`/`C(E)`-ის canonicalization — `corpus_records`-ის გავლით
ისედაც process-ებზეა (0024-ის გაზომვით `3.08x`-`5.85x`).

## ინტერპრეტაცია

1. **პასუხი არ არის "არაფერი"** — და არც "structural feature ხსნის grammar sensitivity-ს". ის
   ორივესგან უფრო ვიწროა: **fixed token shape-ის შიგნით, coefficient degeneracy ხსნის `S(E)`-ს
   ზუსტად corpus-ის `87.2%`-ზე**, out-of-sample დადასტურებით (`MAE 0.003896` vs `0.050699`,
   `0` unseen cell). ეს არ არის მოგონილი სუსტი predictor: exhaustive search-მა `5035` subset-იდან
   უკეთესი ვერ იპოვა.

2. **მიზეზი ალგებრულია და 0024-ის დაკვირვების გაგრძელებაა.** `1` მულტიპლიკატიური ერთეულია,
   ამიტომ `1*(u + v)` და `(1*u) + v` **ერთსა და იმავე** ფუნქციას იძლევა მაშინაც, როცა AST-ები
   განსხვავებულია — და ორი grammar, რომლებიც სხვადასხვა AST-ს აშენებდნენ, ერთ semantic class-ში
   ვარდება. 0024-მა ეს `a == 1` კრიტერიუმებით `linear`-სა და `rational`-ზე დაინახა; აქ ის
   feature-ად არის დაწერილი, მთელ corpus-ზე გაზომილი და out-of-sample შემოწმებული.

3. **Trap-მა შედეგი არ შეჭამა, მაგრამ მისმა მონათესავეებმა ნაწილობრივ შეჭამეს.** `support_size`
   თვითონ სუსტი predictor-ია (`eta2 = 0.0676`, error reduction `2.3%`) და საუკეთესო subset-ის
   ნაწილიც არ არის. **მაგრამ** shape-ის signal-ს `parenthesis_pair_count` და `distinct_ast_count`
   ატარებს, და ორივე parser-ის გადათქმაა: parser-restating feature-ების სრული ამოღება MAE-ს
   `0.003896`-დან `0.034206`-მდე აზრდის. ე.ი. **პასუხის ნახევარი ამ corpus-ზე კვლავ parser-ის
   თვისებაა და არა მათემატიკის.**

4. **`|O(E)| = 4`-ის შიგნით token-multiset feature-ები ბრმაა.** `linear` და `rational` ერთსა და
   იმავე operator multiset-ს, operator count-ს, leaf count-ს, division count-ს, operator word-ის
   Catalan count-ს (ფრჩხილის დანახვის გარეშე) და reachability count-ს ატარებენ და `2.6`-ჯერ
   განსხვავებულ mean `S`-ს იძლევიან. განსხვავებას
   მხოლოდ ფრჩხილი ხედავს. **ფრჩხილი მეორე mechanical forcing-ია, T6-ის გვერდით**: ის tree-ებს
   binding power-ის წაკითხვამდე აშორებს.

5. **0023-ის reachability count ამ corpus-ზე `support_size`-ის relabeling-ია.** მისი overall rho
   და eta2 ბიტში ემთხვევა `support_size`-ისას, და ორივე stratum-ის შიგნით ის მუდმივია. მიზეზი
   იზომება: ის operator word-ს კითხულობს და **ფრჩხილს ვერ ხედავს** — `rational`-ზე `17`-ს
   აბრუნებს, სადაც გაზომილი distinct AST count `4`-ია. **ეს გაზომილი უარყოფითი შედეგია feature-ზე,
   რომელიც a priori ყველაზე პერსპექტიულად გამოიყურებოდა.**

6. **Predictor არცერთ ახალ shape-ზე არ გადადის და ეს გამოქვეყნებული უნდა იყოს ისევე ხმამაღლა,
   როგორც `0.872`.** Leave-one-shape-out-ზე MAE ზუსტად baseline-ს უდრის. Parity split — ის, რაც
   card-მა 0024-ის მიხედვით მოითხოვა — ამას **პრინციპულად ვერ დაინახავს**, რადგან ორივე ნახევარში
   ხუთივე shape-ია. ე.ი. `0.872`-ის სწორი წაკითხვაა: ხუთი ცნობილი shape-ის შიგნით coefficient-ები
   `S(E)`-ს ზუსტად განსაზღვრავენ — და არა ის, რომ structural feature-ები `S(E)`-ს ხსნიან.

7. **`unit_multiplier_count` არასწორია და მისი არასწორობა ინფორმატიულია.** ის პოზიციას ვერ არჩევს:
   `linear`-ის `c` და `quadratic`-ის `a` unit multiplier პოზიციებია, რომლებიც `S`-ს **არ** ცვლიან,
   რადგან იმ ადგილას re-association ისედაც ვალიდურია. სწორედ ეს `400` expression რჩება
   ჩამოუშლელი. **ეს კონკრეტული, ლოკალიზებული და ალგებრულად ახსნადი ჩავარდნაა და არა ხმაური.**
   Feature, რომელიც re-associable unit multiplier-ს დაითვლიდა, ამ სამ cell-საც დახურავდა — მაგრამ
   ის ჩავარდნის დანახვის შემდეგ იქნებოდა გამოგონილი, ამიტომ დახურულ set-ში არ შედის და აქ არ
   იზომება. ეს მომდევნო card-ის საგანია.

8. **`cubic` counterexample-ია coefficient story-სთვის.** მისი `625`-ივე expression-ს ზუსტად
   `S = 0.173913` აქვს, `unit_multiplier_count`-ის `0`-დან `3`-მდე ცვალებადობის მიუხედავად. ე.ი.
   არსებობს token shape, სადაც coefficient degeneracy `S(E)`-ს საერთოდ არ ეხება.

## შეზღუდვები

- **corpus-ს მხოლოდ ხუთი distinct operator word აქვს.** ყველა shape-ზე დაფუძნებული ცნება
  (`operator_profile`, `operator_count`, `repetition_pattern`, `operator_word_catalan_count`) ამ corpus-ზე
  ხუთმნიშვნელობიანი categorical-ია. Token shape-ზე conditioning პრაქტიკულად კითხვაა "რომელი
  template-ია". Leave-one-shape-out ზუსტად ამას ზომავს და პასუხი უარყოფითია.
- **`distinct_variable_count` და `zero_literal_count` მუდმივია** (ერთი ცვლადი, `0` გამორიცხული),
  ამიტომ ორივე feature ამ corpus-ზე გამოუცდელი რჩება. ეს არ ნიშნავს, რომ ისინი უსარგებლოა —
  ნიშნავს, რომ აქ ისინი არ გაზომილა.
- **support size distribution დისბალანსირებულია** (`{3: 1875, 4: 1250}`) და `1`-ს, `2`-ს და
  `5`-ზე მეტს საერთოდ არ შეიცავს. Trap-ის ყველაზე მკვეთრი შემთხვევა — `|O(E)| = 1`, სადაც
  fragmentation შეუძლებელია — ამ corpus-ზე **არ არსებობს**. ე.ი. trap აქ თავისი ყველაზე სუსტი
  ფორმით მოქმედებს.
- **`unit_multiplier_count`-ის adjacency განსაზღვრება token-დონისაა** და არა parse-დონის: literal
  `1`, რომელიც `*` token-ის მეზობლადაა. ეს განზრახაა (feature იაფი და parser-ისგან დამოუკიდებელი
  უნდა იყოს), მაგრამ სწორედ ეს ტოვებს `400` expression-ს ჩამოუშლელს.
- **exhaustive search-ის best-ს იმავე parity split-ით ვირჩევთ, რომლითაც ვაფასებთ.** `5035`
  subset-ზე მინიმუმის აღება თვითონ selection-ია და out-of-sample რიცხვი ამ არჩევანით ოპტიმისტურია.
  სწორედ ამიტომ დამოუკიდებელი შემოწმება leave-one-shape-out-ია და **ის predictor-ს baseline-ზე
  აყენებს**.
- **subset search `4`-ზე გრძელ set-ს არ ამოწმებს.** უფრო დიდი set-ები cell-ებს დააქუცმაცებდნენ —
  ექსპერიმენტისას გაზომილმა `6`-feature-იანმა set-მა `50` cell და **უარესი** out-of-sample MAE
  `0.004101` მისცა `9` unseen cell-თან ერთად — მაგრამ ეს ამომწურავად არ არის გაზომილი.
- **`operator_word_catalan_count` ფრჩხილს ვერ ხედავს, და ეს card-ის ფორმულირებიდან გადახრაა.**
  Card ითხოვდა იმ tree-ების რაოდენობას, რომელსაც **token sequence** უშვებს; გაზომილი feature კი
  operator word-ის Catalan რიცხვია, ამიტომ `rational`-ზე `42`-ს აბრუნებს, მაშინ როცა ფრჩხილიანი
  source მკაცრად ნაკლებს უშვებს. სახელი და motivation ახლა ამას პირდაპირ ამბობს, ეს test-ითაც
  არის დაპინული, მაგრამ თვითონ "token sequence-ის მიერ დაშვებული tree-ები" ამ ექსპერიმენტში
  **გაზომილი არ არის**.
- **`S(E)` semantic class equality-ს ეყრდნობა** და მემკვიდრეობით იღებს 0024-ის class-key
  შეზღუდვებს: `domain` კომპონენტი ამ generation-ში მკვდარია (`canonicalize()` ყოველთვის `R`-ს
  აბრუნებს), ხოლო `excluded points` ამ template corpus-ზე არაფერს ჰყოფს.
- **cell-mean predictor მოდელის არჩევანია** და არა ერთადერთი შესაძლებლობა. Regression, tree ან
  interaction model სხვა რიცხვს მოგვცემდა; cell mean იმიტომაა არჩეული, რომ ის ზუსტად კითხულობს
  cell-ის შიგნით `S` მუდმივია თუ არა, რაც card-ის კრიტერიუმია.
- **wall clock ერთი მანქანის გაზომვაა** (`16` core, Windows, spawn) და დატვირთვაზეა დამოკიდებული;
  feature extraction-ის speedup იმავე კოდზე `1.34x`-დან `0.79x`-მდე შეიცვალა.

## Evidence-ის კლასიფიკაცია

- feature-ების მნიშვნელობები, ყველა `rho`, `eta2`, group size, cell size, collapse fraction,
  holdout MAE/RMSE, leave-one-shape-out MAE, subset search-ის რიცხვები, ground truth-ის ხელახალი
  გამოყვანა, wall clock — executable **observations**.
- 0024-ის ground truth ხელახლა გამოვიდა განსხვავების გარეშე — **observation**, ამ card-ის
  საკუთარ run-ში.
- `strict_reachable_tree_count` support size-ის relabeling-ია ამ corpus-ზე — **observation**
  (ორი rho და ორი eta2 ბიტში ემთხვევა, ორივე stratum-ის შიგნით constant); მისი მიზეზი — რომ
  reachability operator word-ს კითხულობს და ფრჩხილს ვერ ხედავს — **symbolically justified** 0023-ის
  procedure-იდან და corpus-ზე **observed** (`17` vs გაზომილი `4`).
- support size-ის ფიქსაციის შემდეგ რვა shape feature ატარებს weighted `eta2 = 0.7500`-ს, ხოლო
  coefficient-ის კლასი `0.0587`-`0.0761`-ს — **observation** (ვალიდაცია `2`). წაკითხვა, რომ ეს
  რვა feature ამ corpus-ზე პრაქტიკულად "რომელი template-ია"-ს ეკითხება — **hypothesis**,
  რომელზეც leave-one-shape-out არის გაზომვა და მისი პასუხი უარყოფითია.
- `operator_word_catalan_count` operator word-ის და არა token sequence-ის თვისებაა
  (`rational`-ზე `42`, ფრჩხილების მიუხედავად) — **observation**, test-ით დაპინული; card-ის
  თავდაპირველი ფორმულირება "tree-ები, რომლებსაც token sequence უშვებს" ამ ექსპერიმენტში
  **გაზომილი არ არის**.
- `1` მულტიპლიკატიური ერთეულია, ამიტომ `1*(u+v)` და `1*u + v` ერთი ფუნქციაა —
  **symbolically justified**; მისი ეფექტი `S(E)`-ზე — **observed** ზუსტი count-ებით.
- ფრჩხილი mechanical forcing-ია T6-ის გვერდით — **symbolically justified** parser-ის
  არგუმენტიდან (ფრჩხილი `_primary()`-ში `_expression(0)`-ს იძახებს, ე.ი. split ფიქსირდება binding
  power-ის შედარებამდე) და corpus-ზე **observed** (`|O(E)| = 4`-ის შიგნით მხოლოდ ის და
  `distinct_ast_count` არ არის მუდმივი).
- predictor არცერთ ახალ token shape-ზე არ გადადის — **measured negative result**
  leave-one-shape-out-ზე.
- per-parameter driver-ები (`linear a, d` / `quadratic b` / `rational a, c` / `mixed_chain c` /
  `cubic` არცერთი) — **observations**; მათი ზოგადი ალგებრული ფორმულირება **hypothesis**-ია.
- re-associable unit multiplier უკეთესი feature იქნებოდა — **hypothesis**, განზრახ **არ**
  არის გაზომილი, რადგან ის ჩავარდნის დანახვის შემდეგ გამოიგონებოდა.
- ნებისმიერი ზოგადი კანონი grammar sensitivity-ზე თვითნებურ expression-ებზე — **არ არის claimed**
  არც დადებითი და არც უარყოფითი მიმართულებით.

## ვალიდაცია

ყველა ბლოკი ქვემოთ არის verbatim output; ხელით არაფერია ჩაწერილი.

### 1. Ground truth-ის ხელახალი გამოყვანა

```text
python -c "from parseatlas.corpus_matrix import generate_corpus; from parseatlas.sensitivity_predictors import feature_table, ground_truth, constant_features, FEATURE_NAMES; c = generate_corpus(); t = feature_table(c); g = ground_truth(t); print('corpus', g['expression_count'], 'support sizes', g['support_size_counts'], '|', len(FEATURE_NAMES), 'features'); print('features', t['feature_workers'], 'workers', round(t['feature_wall_clock_seconds'], 2), 's | records', t['record_workers'], 'workers', round(t['record_wall_clock_seconds'], 2), 's on', t['cpu_count'], 'cores'); print('S dist', g['sensitivity_distribution']); print('C dist', g['class_count_distribution']); print('rigid', g['rigid'], g['rigid_families'], '| sensitive', g['sensitive'], '| meanS', round(g['mean_sensitivity'], 6), '| maxS', round(g['max_sensitivity'], 6)); print('constant on this corpus', constant_features(t))"
```

```text
corpus 3125 support sizes {3: 1875, 4: 1250} | 21 features
features 15 workers 32.85 s | records 15 workers 99.59 s on 16 cores
S dist {0.0: 25, 0.043478: 200, 0.086957: 275, 0.130435: 1500, 0.173913: 625, 0.217391: 100, 0.304348: 400}
C dist {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}
rigid 25 {'rational': 25} | sensitive 3100 | meanS 0.153739 | maxS 0.304348
constant on this corpus ('distinct_variable_count', 'zero_literal_count')
```

ეს run დატვირთულ მანქანაზე შესრულდა — მეზობელი card-ის worker პარალელურად მუშაობდა — ამიტომ
wall clock იმავე სესიაში გაზომილ სხვა run-ებზე მაღალია.

### 2. Trap: overall vs fixed support size

```text
python -c "
from parseatlas.corpus_matrix import generate_corpus
from parseatlas.sensitivity_predictors import feature_table, predictor_strength, within_support_report, FEATURE_NAMES
t = feature_table(generate_corpus()); s = predictor_strength(t); w = within_support_report(t)
f = lambda x: 'None' if x is None else '%+.4f' % x
both = lambda n: s['within_strata_summary'][n]['strata_with_variation'] == 2
print('strata', s['stratum_sizes'])
print('%-30s %8s %8s | %8s %8s | %8s %8s | %5s %s' % ('feature','rho','eta2','rho k=3','eta2 k=3','rho k=4','eta2 k=4','both','parser'))
for n in FEATURE_NAMES:
    o=s['overall'][n]; a=s['within_strata'][(3,)]['features'][n]; b=s['within_strata'][(4,)]['features'][n]
    print('%-30s %8s %8s | %8s %8s | %8s %8s | %5s %s' % (n, f(o['spearman']), f(o['eta_squared']), f(a['spearman']), f(a['eta_squared']), f(b['spearman']), f(b['eta_squared']), 'yes' if both(n) else '', 'yes' if o['restates_the_parser'] else ''))
print()
print('dead inside every support size   :', w['dead_features'])
print('retained, independent            :', w['retained_independent_features'])
print('retained, parser-restating       :', w['retained_parser_restating_features'])
print('varies inside BOTH support sizes :', tuple(n for n in FEATURE_NAMES if both(n)))
print('weighted eta2 within support     :', {k: round(v,4) for k,v in w['weighted_eta_squared'].items() if v is not None})
groups = {}
for n in FEATURE_NAMES: groups.setdefault((s['overall'][n]['spearman'], s['overall'][n]['eta_squared']), []).append(n)
print('overall (rho, eta2) bit-identical:', [tuple(v) for v in groups.values() if len(v) > 1])
print('k=3 group sizes, every eta2=0.7500 feature :')
for n in FEATURE_NAMES:
    if (s['within_strata_summary'][n]['weighted_eta_squared'] or 0) > 0.7: print('   %-30s' % n, s['within_strata'][(3,)]['features'][n]['group_sizes'])
print('group sizes, unit_multiplier_count : k=3', s['within_strata'][(3,)]['features']['unit_multiplier_count']['group_sizes'], '| k=4', s['within_strata'][(4,)]['features']['unit_multiplier_count']['group_sizes'])
"
```

```text
strata {(3,): 1875, (4,): 1250}
feature                             rho     eta2 |  rho k=3 eta2 k=3 |  rho k=4 eta2 k=4 |  both parser
support_size                    +0.1111  +0.0676 |     None  +0.0000 |     None  +0.0000 |       yes
operator_count                  +0.4638  +0.0624 |  +0.7862  +0.7500 |     None  +0.0000 |       
leaf_count                      +0.4638  +0.0624 |  +0.7862  +0.7500 |     None  +0.0000 |       
variable_leaf_count             +0.3218  +0.1443 |  +0.7862  +0.7500 |     None  +0.0000 |       
distinct_variable_count            None  +0.0000 |     None  +0.0000 |     None  +0.0000 |       
parenthesis_pair_count          -0.4270  +0.1676 |     None  +0.0000 |  -0.7733  +0.6233 |       yes
division_operator_count         +0.1111  +0.0676 |     None  +0.0000 |     None  +0.0000 |       
has_division                    +0.1111  +0.0676 |     None  +0.0000 |     None  +0.0000 |       
max_operator_multiplicity       +0.3218  +0.1443 |  +0.7862  +0.7500 |     None  +0.0000 |       
repeated_operator_count         +0.4638  +0.0624 |  +0.7862  +0.7500 |     None  +0.0000 |       
operator_profile                   None  +0.1443 |     None  +0.7500 |     None  +0.0000 |       
repetition_pattern                 None  +0.1443 |     None  +0.7500 |     None  +0.0000 |       
unit_literal_count              -0.2232  +0.0612 |  -0.0825  +0.0178 |  -0.4191  +0.1636 |   yes 
zero_literal_count                 None  +0.0000 |     None  +0.0000 |     None  +0.0000 |       
unit_multiplier_count           -0.1840  +0.0486 |  -0.0513  +0.0359 |  -0.3759  +0.1134 |   yes 
unit_divisor_count              -0.1183  +0.0090 |     None  +0.0000 |  -0.1730  +0.0329 |       
degenerate_coefficient          -0.1984  +0.0456 |  -0.0877  +0.0158 |  -0.3653  +0.1230 |   yes 
fractional_literal_count        -0.3704  +0.0902 |  -0.6058  +0.3613 |     None  +0.0000 |       
distinct_ast_count              +0.6261  +0.5850 |     None  +0.0000 |  +0.7733  +0.6233 |       yes
operator_word_catalan_count     +0.4638  +0.0624 |  +0.7862  +0.7500 |     None  +0.0000 |       
strict_reachable_tree_count     +0.1111  +0.0676 |     None  +0.0000 |     None  +0.0000 |       yes

dead inside every support size   : ('support_size', 'distinct_variable_count', 'division_operator_count', 'has_division', 'zero_literal_count', 'strict_reachable_tree_count')
retained, independent            : ('operator_count', 'leaf_count', 'variable_leaf_count', 'max_operator_multiplicity', 'repeated_operator_count', 'operator_profile', 'repetition_pattern', 'operator_word_catalan_count', 'fractional_literal_count', 'unit_literal_count', 'unit_multiplier_count', 'degenerate_coefficient', 'unit_divisor_count')
retained, parser-restating       : ('parenthesis_pair_count', 'distinct_ast_count')
varies inside BOTH support sizes : ('unit_literal_count', 'unit_multiplier_count', 'degenerate_coefficient')
weighted eta2 within support     : {'operator_count': 0.75, 'leaf_count': 0.75, 'variable_leaf_count': 0.75, 'max_operator_multiplicity': 0.75, 'repeated_operator_count': 0.75, 'operator_profile': 0.75, 'repetition_pattern': 0.75, 'operator_word_catalan_count': 0.75, 'parenthesis_pair_count': 0.6233, 'distinct_ast_count': 0.6233, 'fractional_literal_count': 0.3613, 'unit_literal_count': 0.0761, 'unit_multiplier_count': 0.0669, 'degenerate_coefficient': 0.0587, 'unit_divisor_count': 0.0329}
overall (rho, eta2) bit-identical: [('support_size', 'division_operator_count', 'has_division', 'strict_reachable_tree_count'), ('operator_count', 'leaf_count', 'repeated_operator_count', 'operator_word_catalan_count'), ('variable_leaf_count', 'max_operator_multiplicity'), ('distinct_variable_count', 'zero_literal_count'), ('operator_profile', 'repetition_pattern')]
k=3 group sizes, every eta2=0.7500 feature :
   operator_count                 {3: 625, 5: 625, 9: 625}
   leaf_count                     {10: 625, 4: 625, 6: 625}
   variable_leaf_count            {1: 625, 3: 625, 6: 625}
   max_operator_multiplicity      {1: 625, 3: 625, 6: 625}
   repeated_operator_count        {0: 625, 1: 625, 2: 625}
   operator_profile               {'* x1, + x1, - x1': 625, '* x3, + x1, - x1': 625, '* x6, + x2, - x1': 625}
   repetition_pattern             {'1+1+1': 625, '3+1+1': 625, '6+2+1': 625}
   operator_word_catalan_count    {42: 625, 4862: 625, 5: 625}
group sizes, unit_multiplier_count : k=3 {0: 1220, 1: 565, 2: 85, 3: 5} | k=4 {0: 800, 1: 400, 2: 50}
```

### 3. Predictor, cell-ები, ორივე hold-out

```text
python -c "
from parseatlas.corpus_matrix import generate_corpus
from parseatlas.sensitivity_predictors import feature_table, explained_partition, holdout_check, leave_one_group_out_check
C = ('operator_profile','parenthesis_pair_count','unit_multiplier_count','unit_divisor_count')
t = feature_table(generate_corpus())
p = explained_partition(t, C); h = holdout_check(t, C); l = leave_one_group_out_check(t, C)
print('cells', p['cell_count'], '| collapsed', p['collapsed_expressions'], '/', p['expression_count'], '=', p['collapsed_fraction'], '| max cell range', round(p['max_cell_range'],6), '| weighted mean range', round(p['size_weighted_mean_range'],6), '| baseline range', round(p['baseline_range'],6))
for c in p['uncollapsed_cells']:
    print('   uncollapsed n=%-4d range=%.6f values=%s key=%s' % (c['size'], c['range'], c['distinct_values'], tuple(c['key'].values())))
for k in (3,4):
    q = explained_partition({'rows': tuple(r for r in t['rows'] if r['support_size']==k)}, C)
    print('   within |O(E)|=%d : n=%d cells=%d collapsed=%d (%.6f) max range=%.6f' % (k, q['expression_count'], q['cell_count'], q['collapsed_expressions'], q['collapsed_fraction'], q['max_cell_range']))
print('parity holdout   MAE %.6f RMSE %.6f | baseline MAE %.6f | exact %.6f | unseen cells %d | halves %s' % (h['mean_absolute_error'], h['root_mean_square_error'], h['baseline_mean_absolute_error'], h['exact_fraction'], h['total_unseen_cells'], h['half_sizes']))
print('   folds', {k: (round(v['mean_absolute_error'],6), v['cells_fitted'], round(v['mean_absolute_error_reduction'],6)) for k,v in h['folds'].items()})
print('   fold MAE, unrounded : even_fit %.12f | odd_fit %.12f | they differ by %.12f' % (h['folds']['even_fit']['mean_absolute_error'], h['folds']['odd_fit']['mean_absolute_error'], abs(h['folds']['even_fit']['mean_absolute_error'] - h['folds']['odd_fit']['mean_absolute_error'])))
print('   fold error reduction, unrounded : even_fit %.10f | odd_fit %.10f' % (h['folds']['even_fit']['mean_absolute_error_reduction'], h['folds']['odd_fit']['mean_absolute_error_reduction']))
print('leave-one-shape  MAE %.6f | baseline MAE %.6f | exact %.6f | unseen cells %d | worst fold %.6f' % (l['mean_absolute_error'], l['baseline_mean_absolute_error'], l['exact_fraction'], l['total_unseen_cells'], l['worst_fold_mean_absolute_error']))
print('   leave-one-shape MAE == baseline MAE, unrounded : %.12f == %.12f -> %s' % (l['mean_absolute_error'], l['baseline_mean_absolute_error'], l['mean_absolute_error'] == l['baseline_mean_absolute_error']))
for k, fold in l['folds'].items():
    print('   held out %-30s n=%d MAE %.6f unseen %d' % (str(k), fold['evaluate_size'], fold['mean_absolute_error'], fold['unseen_cells']))
print('deterministic', holdout_check(t, C) == h, leave_one_group_out_check(t, C) == l)
"
```

```text
cells 18 | collapsed 2725 / 3125 = 0.872 | max cell range 0.086957 | weighted mean range 0.007791 | baseline range 0.304348
   uncollapsed n=200  range=0.043478 values=(0.086957, 0.130435) key=('* x3, + x1, - x1', 0, 1, 0)
   uncollapsed n=160  range=0.086957 values=(0.217391, 0.304348) key=('* x2, + x1, - x1, / x1', 0, 1, 0)
   uncollapsed n=40   range=0.043478 values=(0.086957, 0.130435) key=('* x2, + x1, - x1, / x1', 0, 1, 1)
   within |O(E)|=3 : n=1875 cells=9 collapsed=1675 (0.893333) max range=0.043478
   within |O(E)|=4 : n=1250 cells=9 collapsed=1050 (0.840000) max range=0.086957
parity holdout   MAE 0.003896 RMSE 0.011536 | baseline MAE 0.050699 | exact 0.872000 | unseen cells 0 | halves {'even': 1563, 'odd': 1562}
   folds {'even_fit': (0.003897, 18, 0.923208), 'odd_fit': (0.003894, 18, 0.923114)}
   fold MAE, unrounded : even_fit 0.003896899182 | odd_fit 0.003894405964 | they differ by 0.000002493218
   fold error reduction, unrounded : even_fit 0.9232082810 | odd_fit 0.9231144079
leave-one-shape  MAE 0.060842 | baseline MAE 0.060842 | exact 0.000000 | unseen cells 3125 | worst fold 0.128557
   leave-one-shape MAE == baseline MAE, unrounded : 0.060841739130 == 0.060841739130 -> True
   held out ('* x1, + x1, - x1', 0)        n=625 MAE 0.040000 unseen 625
   held out ('* x2, + x1, - x1, / x1', 0)  n=625 MAE 0.128557 unseen 625
   held out ('* x2, + x1, - x1, / x1', 2)  n=625 MAE 0.070435 unseen 625
   held out ('* x3, + x1, - x1', 0)        n=625 MAE 0.040000 unseen 625
   held out ('* x6, + x2, - x1', 0)        n=625 MAE 0.025217 unseen 625
deterministic True True
```

### 4. Exhaustive subset search

```text
python -c "
import itertools
from parseatlas.corpus_matrix import generate_corpus
from parseatlas.sensitivity_predictors import feature_table, explained_partition, holdout_check, constant_features, FEATURE_NAMES, FEATURE_BY_NAME
t = feature_table(generate_corpus())
usable = [n for n in FEATURE_NAMES if n not in constant_features(t)]
rows = []
for size in (1,2,3,4):
    for combo in itertools.combinations(usable, size):
        h = holdout_check(t, combo); p = explained_partition(t, combo)
        rows.append((h['mean_absolute_error'], p['collapsed_fraction'], p['cell_count'], h['total_unseen_cells'], combo))
print('usable features', len(usable), '| subsets of size 1..4 searched', len(rows))
best = min(r[0] for r in rows)
tied = [r for r in rows if r[0] == best]
prs = {n for n in FEATURE_NAMES if FEATURE_BY_NAME[n].restates_the_parser}
print('best out-of-sample MAE %.6f attained by %d subsets; all give %s cells and collapsed %s' % (best, len(tied), {r[2] for r in tied}, {round(r[1],3) for r in tied}))
print('every best subset contains unit_multiplier_count and unit_divisor_count :', all('unit_multiplier_count' in r[4] and 'unit_divisor_count' in r[4] for r in tied))
print('every best subset contains a parser-restating feature                   :', all(set(r[4]) & prs for r in tied))
for r in sorted(tied, key=lambda r: r[4]):
    print('   tied optimum :: %s' % ', '.join(r[4]))
for size in (1,2,3,4):
    b = min((r for r in rows if len(r[4])==size), key=lambda r: r[0])
    print('  best of size %d : MAE %.6f collapsed %.6f :: %s' % (size, b[0], b[1], ', '.join(b[4])))
b = min((r for r in rows if not (set(r[4]) & prs)), key=lambda r: r[0])
print('best with NO parser-restating feature : MAE %.6f collapsed %.6f cells %d :: %s' % (b[0], b[1], b[2], ', '.join(b[4])))
b = min((r for r in rows if 'support_size' in set(r[4])), key=lambda r: r[0])
print('best CONTAINING support_size          : MAE %.6f :: %s' % (b[0], ', '.join(b[4])))
print('baseline (predict the global mean)    : MAE %.6f' % holdout_check(t, ('support_size',))['baseline_mean_absolute_error'])
"
```

```text
usable features 19 | subsets of size 1..4 searched 5035
best out-of-sample MAE 0.003896 attained by 12 subsets; all give {18} cells and collapsed {0.872}
every best subset contains unit_multiplier_count and unit_divisor_count : True
every best subset contains a parser-restating feature                   : True
   tied optimum :: leaf_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   tied optimum :: max_operator_multiplicity, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   tied optimum :: operator_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   tied optimum :: operator_profile, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   tied optimum :: parenthesis_pair_count, max_operator_multiplicity, unit_multiplier_count, unit_divisor_count
   tied optimum :: parenthesis_pair_count, operator_profile, unit_multiplier_count, unit_divisor_count
   tied optimum :: parenthesis_pair_count, repetition_pattern, unit_multiplier_count, unit_divisor_count
   tied optimum :: repeated_operator_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   tied optimum :: repetition_pattern, unit_multiplier_count, unit_divisor_count, distinct_ast_count
   tied optimum :: unit_multiplier_count, unit_divisor_count, distinct_ast_count, operator_word_catalan_count
   tied optimum :: variable_leaf_count, parenthesis_pair_count, unit_multiplier_count, unit_divisor_count
   tied optimum :: variable_leaf_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
  best of size 1 : MAE 0.035284 collapsed 0.000000 :: distinct_ast_count
  best of size 2 : MAE 0.025294 collapsed 0.201600 :: unit_multiplier_count, distinct_ast_count
  best of size 3 : MAE 0.012634 collapsed 0.736000 :: operator_count, unit_multiplier_count, distinct_ast_count
  best of size 4 : MAE 0.003896 collapsed 0.872000 :: operator_count, unit_multiplier_count, unit_divisor_count, distinct_ast_count
best with NO parser-restating feature : MAE 0.034206 collapsed 0.571200 cells 35 :: variable_leaf_count, unit_literal_count, unit_multiplier_count, unit_divisor_count
best CONTAINING support_size          : MAE 0.012634 :: support_size, operator_count, parenthesis_pair_count, unit_multiplier_count
baseline (predict the global mean)    : MAE 0.050699
```

`min` პირველ მინიმუმს აბრუნებს declaration order-ში, ამიტომ თითოეული "best of size" ერთი
წარმომადგენელია შესაძლო ტოლი subset-ებიდან; მნიშვნელოვანი რიცხვი MAE-ია და არა კონკრეტული
სახელები. თვითონ ოპტიმუმზე კი არჩევანი საერთოდ არ კეთდება — თორმეტივე ტოლი subset ზემოთ
სრულადაა ჩამოთვლილი.

### 5. Sequential/parallel ეკვივალენტობა და timing

```text
python -c "
from parseatlas.corpus_matrix import generate_corpus
from parseatlas.sensitivity_predictors import feature_rows
c = generate_corpus()
s = feature_rows(c, workers=1); p = feature_rows(c, workers=0); q = feature_rows(c, workers=0)
print('sequential', s['workers'], 'worker  ', round(s['wall_clock_seconds'],3), 's')
print('parallel  ', p['workers'], 'workers ', round(p['wall_clock_seconds'],3), 's | second run', round(q['wall_clock_seconds'],3), 's | cores', p['cpu_count'])
print('speedup   ', round(s['wall_clock_seconds']/p['wall_clock_seconds'],2))
print('identical ', s['rows'] == p['rows'] == q['rows'])
"
```

ამ rework-ის run, ძლიერ დატვირთულ მანქანაზე (რამდენიმე მეზობელი worker პარალელურად):

```text
sequential 1 worker   15.570 s
parallel   15 workers  35.617 s | second run 25.179 s | cores 16
speedup    0.44
identical  True
```

ადრინდელი run-ები იმავე კოდზე: ერთი დატვირთული — `12.536 / 15.871` (`0.79x`) — და სამი idle
დაწყვილებული run: `2.726 / 2.090` (`1.30x`), `2.777 / 2.066` (`1.34x`), `2.492 / 1.932`
(`1.29x`). `identical` ხუთივეში `True`. Contention-ის ზრდასთან ერთად speedup `1.34x`-დან
`0.44x`-მდე დაეცა — იმავე კოდზე, იმავე მანქანაზე.

### 6. Per-parameter driver-ები (რატომ არ იხურება სამი cell)

```text
python -c "
from parseatlas.corpus_matrix import generate_corpus
from parseatlas.sensitivity_predictors import feature_table
c = generate_corpus(); t = feature_table(c)
params = {e['index']: e['parameters'] for e in c['expressions']}
rows = {r['index']: r for r in t['rows']}
for fam in c['families']:
    idx = [e['index'] for e in c['expressions'] if e['family']==fam]
    drivers = []
    for name in ('a','b','c','d'):
        groups = {}
        for i in idx:
            groups.setdefault(params[i][name], set()).add(round(rows[i]['sensitivity'],6))
        drivers.append('%s:%s' % (name, 'DRIVES' if len({frozenset(v) for v in groups.values()})>1 else 'flat'))
    um = {}
    for i in idx:
        um.setdefault(rows[i]['unit_multiplier_count'], set()).add(round(rows[i]['sensitivity'],6))
    print('%-12s %s | unit_multiplier_count -> S : %s' % (fam, ' '.join(drivers), {k: sorted(v) for k,v in sorted(um.items())}))
"
```

```text
linear       a:DRIVES b:flat c:flat d:DRIVES | unit_multiplier_count -> S : {0: [0.130435, 0.304348], 1: [0.086957, 0.130435, 0.217391, 0.304348], 2: [0.086957, 0.217391]}
quadratic    a:flat b:DRIVES c:flat d:flat | unit_multiplier_count -> S : {0: [0.130435], 1: [0.086957, 0.130435], 2: [0.086957]}
cubic        a:flat b:flat c:flat d:flat | unit_multiplier_count -> S : {0: [0.173913], 1: [0.173913], 2: [0.173913], 3: [0.173913]}
rational     a:DRIVES b:flat c:DRIVES d:flat | unit_multiplier_count -> S : {0: [0.130435], 1: [0.043478], 2: [0.0]}
mixed_chain  a:flat b:flat c:DRIVES d:flat | unit_multiplier_count -> S : {0: [0.130435], 1: [0.086957]}
```

### 7. Tests

ამ card-ის საკუთარი test file — card-ით კონტროლირებადი რიცხვი:

```text
python -m pytest -q tests/test_sensitivity_predictors.py
38 passed in 47.90s          # პირველი review-მდე, დაფიქსირდა 2026-09-03T01:47Z
38 passed in 218.16s         # პირველი review-მდე, 2026-09-03T02:54Z, დატვირთულ მანქანაზე
38 passed in 30.98s          # პირველი review-მდე, 2026-09-03T03:21Z
40 passed in 285.68s         # rework, ძლიერ დატვირთულ მანქანაზე (რამდენიმე მეზობელი worker)
40 passed in 108.44s         # rework, საბოლოო tree-ზე, დაიწყო 2026-09-03T05:09Z
```

Review-ის შემდეგ ორი test დაემატა: `test_the_operator_word_catalan_count_is_blind_to_parentheses_as_its_name_says`
(feature ფრჩხილიან და ფრჩხილის გარეშე source-ზე ერთსა და იმავე `42`-ს აბრუნებს) და
`test_the_exhaustive_subset_search_reproduces`, რომელიც სექცია `8`-ის `5035`-subset search-ს
ამომწურავად ატარებს და მის ყველა გამოქვეყნებულ რიცხვს აპინავს: `19` usable feature, `5035`
subset, optimum `0.003896`, თორმეტივე ტოლი subset და მათი `18` cell / `0.872`, ოთხივე
"best of size", parser-restating feature-ების გარეშე საუკეთესო `0.034206` და `support_size`-ის
შემცველი საუკეთესო `0.012634`. ეს file-ის ყველაზე ნელი test-ია — `36.61 s` საბოლოო run-ში და
`117.02 s` დატვირთულ მანქანაზე (pytest-ის `--durations`-იდან). Test count ახლა ყოველთვის `40`-ია;
wall clock მანქანის დატვირთვას მიჰყვება.

მთლიანი suite — **timestamped observation**, არა card-ით კონტროლირებადი სიდიდე: მას მეზობელი
ექსპერიმენტების worker-ები პარალელურად ცვლიან.

```text
python -m pytest -q
460 passed in 393.05s              # პირველი review-მდე, 2026-09-03T01:52Z
493 passed in 1067.04s             # პირველი review-მდე, 2026-09-03T03:12Z, დატვირთულ მანქანაზე
493 passed in 444.32s              # პირველი review-მდე, 2026-09-03T03:20Z
499 passed in 1654.44s             # rework, ძლიერ დატვირთულ მანქანაზე
2 failed, 497 passed in 407.77s    # rework, დასრულდა 2026-09-03T05:17Z
```

ბოლო run-ის ორივე ჩავარდნა `tests/test_outer_quotient.py`-შია (`assert 127 == 115` და
`assert (24 * 13) == 260`) — ეს მეზობელი card-ის (0032) corpus-ის ზომაზე დაწერილი assertion-ებია,
რომელსაც ის worker ამ წუთებში ცვლის. ის file და მისი module ამ card-ის allowed writes-ში არ შედის
და `sensitivity_predictors`-ს არ იმპორტირებს; იმავე run-ში `tests/test_sensitivity_predictors.py`
ორმოცივე test-ით გაიარა. `499 passed` იმავე ხის იმ მდგომარეობაზეა, სადაც 0032-ის file ჯერ კიდევ
მწვანე იყო — ე.ი. suite-ის რიცხვის მოძრაობა მეზობელი card-ისაა და არა ამ card-ის.

Card-ის დაწყებისას suite `354 passed` იყო; ამ card-მა `40` test დაამატა (review-მდე `38`, plus
review-ის ორი). დანარჩენი მეზობელი worker-ების ექსპერიმენტებს (0030, 0031, 0032) ეკუთვნის და ამ
card-ის კონტროლში არ არის — სწორედ ამიტომ ეს რიცხვი timestamped observation-ია და არა acceptance
criterion. ამ card-ის სამი ფაილის გარეთ არაფერი შეცვლილა: `src/parseatlas/sensitivity_predictors.py`,
`tests/test_sensitivity_predictors.py`, `experiments/0029_sensitivity_predictors/`.

### 8. Per-shape ცხრილი (დაკვირვებული შედეგები, სექცია 3)

```text
python -c "
from parseatlas.corpus_matrix import generate_corpus
from parseatlas.sensitivity_predictors import feature_table, predictor_strength, explained_partition
SHAPE = ('operator_profile','parenthesis_pair_count')
UNITS = ('unit_multiplier_count','unit_divisor_count')
c = generate_corpus(); t = feature_table(c)
s = predictor_strength(t, SHAPE, UNITS)
family = {(r['operator_profile'], r['parenthesis_pair_count']): r['family'] for r in t['rows']}
mean = {f: [] for f in c['families']}
for r in t['rows']: mean[r['family']].append(r['sensitivity'])
for key, block in s['within_strata'].items():
    rows = tuple(r for r in t['rows'] if (r['operator_profile'], r['parenthesis_pair_count']) == key)
    q = explained_partition({'rows': rows}, UNITS)
    e = lambda n: 'None' if block['features'][n]['eta_squared'] is None else '%.4f' % block['features'][n]['eta_squared']
    v = sorted({round(r['sensitivity'],6) for r in rows})
    print('%-12s n=%d meanS %.6f eta2(um)=%s eta2(ud)=%s cells=%d collapsed=%.3f maxRange=%.6f S=%s' % (
        family[key], block['size'], sum(mean[family[key]])/len(mean[family[key]]), e('unit_multiplier_count'), e('unit_divisor_count'),
        q['cell_count'], q['collapsed_fraction'], q['max_cell_range'], v))
print('features constant inside every shape :', s['within_strata_summary']['unit_multiplier_count']['strata_count'], 'shapes of size', sorted({b['size'] for b in s['within_strata'].values()}))
"
```

```text
mixed_chain  n=625 meanS 0.121739 eta2(um)=1.0000 eta2(ud)=0.0000 cells=2 collapsed=1.000 maxRange=0.000000 S=[0.086957, 0.130435]
linear       n=625 meanS 0.253913 eta2(um)=0.0908 eta2(ud)=0.8094 cells=6 collapsed=0.680 maxRange=0.086957 S=[0.086957, 0.130435, 0.217391, 0.304348]
rational     n=625 meanS 0.097391 eta2(um)=1.0000 eta2(ud)=0.0000 cells=3 collapsed=1.000 maxRange=0.000000 S=[0.0, 0.043478, 0.130435]
quadratic    n=625 meanS 0.121739 eta2(um)=0.5000 eta2(ud)=0.0000 cells=3 collapsed=0.680 maxRange=0.043478 S=[0.086957, 0.130435]
cubic        n=625 meanS 0.173913 eta2(um)=None eta2(ud)=None cells=4 collapsed=1.000 maxRange=0.000000 S=[0.173913]
features constant inside every shape : 5 shapes of size [625]
```

`linear`-ისა და `rational`-ის mean `S` — `0.253913` და `0.097391` — აქვე იკითხება და 0024-ის
per-family ცხრილის იდენტურია.
