# ParseAtlas ექსპერიმენტი 0024: corpus-scale grammar agreement matrix და cluster structure

## შედეგი ერთი აბზაცით

**T14 (მდგრადი grammar-space cluster structure null model-ის მიღმა) ამ corpus-ზე არ დასტურდება. ეს გაზომილი უარყოფითი შედეგია.**

`3125` expression-ზე საშუალო off-diagonal agreement `0.259307`-ია. მისგან `0.072000` operator-support reduction-ითაა mechanically იძულებული, `0.167333` კი byte-identical AST-ით აიხსნება (ast-identity matrix-ის საშუალო) — ე.ი. observed agreement-ის `27.8%` პირდაპირ null model-ია და `64.5%` საერთოდ არ არის semantic collapse, არამედ იდენტური AST. როცა null model გამოკლებულია, excess matrix-ზე clustering ზუსტად `7` cluster-ს იძლევა და ეს `7` cluster **სიმრავლედ ტოლია** support size `3`-ის `7` support-reduction block-ისა (`set` თანასწორობა, `True`). ე.ი. excess-ის clustering null model-ს ხელახლა აღმოაჩენს და მეტს არაფერს. Observed matrix-ზე იმავე მეთოდით მიღებული `4` cluster-იც არ არის "null-ის მიღმა სტრუქტურა": მისი `4`-იდან `2` cluster — `(G03, G04, G06, G20)` და `(G09, G10, G12, G22)` — verbatim support-forced block-ია.

რაც ამ ექსპერიმენტიდან **დადებით** შედეგად რჩება, სხვაა: **AST diversity და semantic diversity ორი დამოუკიდებელი სიდიდეა**, და ეს `3125`-იდან `2500` expression-ზე (`0.8`) პირდაპირ იზომება. ეს null model-ს არ ეხება, ალგებრულად აიხსნება და ქვემოთ ცალკე სექციაშია.

## მიზანი

0017-მა `25 x 25` agreement matrix ხუთ expression-ზე ააგო და ღიად დატოვა მთავარი კითხვა: არის თუ არა grammar-space-ში რეალური სტრუქტურა, თუ ხუთი expression-ის შემთხვევითობა. აქ იგივე matrix `3125` controlled expression-ზე იზომება და — რაც უფრო მნიშვნელოვანია — ემატება control.

0019-მა დაამტკიცა, რომ agreement-ის ნაწილი mechanically იძულებითია: თუ token sequence-ის distinct-operator set `O(E)` ოთხზე მცირეა, `24` strict grammar იყოფა `factorial(|O(E)|)` block-ად და თითო block-ის შიგნით ყველა grammar byte-identical AST-ს იძლევა, ე.ი. **ყოველთვის** ერთ semantic class-ში ხვდება. ეს parsing artifact-ია და არა აღმოჩენა.

ამიტომ ამ ექსპერიმენტის კითხვა ასე დაისმის:

```text
observed agreement = support-forced agreement + excess
რჩება თუ არა excess-ში სტრუქტურა, როცა null model გამოკლებულია?
```

გაზომილი პასუხი: **არა, ამ corpus-ზე არ რჩება.** null model სწორედ ამისთვის აშენდა და სწორედ ეს დაიჭირა.

## Corpus

Corpus deterministic და fully reproducible არის: არც randomness, არც seed. ხუთი family, თითო ერთი template-ით, თითო parameter ოთხივე პოზიციაზე იღებს მნიშვნელობას `{1, 2, 3, 4, 5}`-დან:

```text
linear      : {a}*x + {b} - {c}*x/{d}
quadratic   : {a}*x*x + {b}*x - {c}/{d}
cubic       : {a}*x*x*x + {b}*x*x - {c}*x + {d}
rational    : ({a}*x + {b})/({c}*x - {d})
mixed_chain : {a}/{b} + {c}*x - {d}/{a}
```

- coefficient set: `(1, 2, 3, 4, 5)`, parameter-ები `(a, b, c, d)`, თანმიმდევრობა `itertools.product(values, repeat=4)`.
- `0` და უარყოფითი მნიშვნელობები გამორიცხულია: tokenizer-ს unary minus არ აქვს, ხოლო `0` template-ების `{d}`, `{b}` და `{a}` denominator-ებს undefined-ს ხდის.
- თითო family: `5^4 = 625` expression; სულ `5 * 625 = 3125`.
- family-ები interleaved-ია თითო coefficient tuple-ის შიგნით, ამიტომ even/odd split ორივე ნახევარში family-ებს თანაბრად ტოვებს.

ეს პარამეტრები `generate_corpus()["generation"]`-ში ინახება, ასე რომ corpus მხოლოდ ამ report-იდან regenerable-ია.

### Operator support — არსებითი დაკვირვება corpus-ზე

| family | მაგალითი | `O(E)` | support size | expressions |
| --- | --- | --- | --- | --- |
| linear | `2*x + 3 - 4*x/5` | `* + - /` | 4 | 625 |
| quadratic | `2*x*x + 3*x - 4/5` | `* + -` | 3 | 625 |
| cubic | `2*x*x*x + 3*x*x - 4*x + 5` | `* + -` | 3 | 625 |
| rational | `(2*x + 3)/(4*x - 5)` | `* + / -` | 4 | 625 |
| mixed_chain | `2/3 + 4*x - 5/2` | `+ * -` | 3 | 625 |

Support size distribution: `{3: 1875, 4: 1250}`.

სამი family-ის `/` სიმბოლო operator კი არა, rational literal-ია — `{c}/{d}` და `{a}/{b}` მთლიანად ერთ number token-ში ჯდება (`\d+(?:/\d+)?`), ზუსტად ისე, როგორც 0019-ში `1/2`. ამიტომ corpus-ის `60%`-ს `/` operator საერთოდ არ აქვს და მასზე support reduction `24` grammar-ს `3! = 6` block-ად, თითო `4` ზომის, ყოფს. ეს არ არის ხარვეზი — ეს არის ზუსტად ის ნაწილი corpus-ისა, სადაც null model ძლიერია და control-ს აზრი აქვს. ესვე არის მიზეზი, რის გამოც excess-ის clustering null-ის სურათს აბრუნებს (იხ. Cluster structure).

### Restriction probe corpus — ცალკე, პატარა და მიზნობრივი

Semantic class key `(canonical, domain, excluded points)`-ია, მაგრამ `3125`-იან template corpus-ზე ამ key-ის ბოლო ორი კომპონენტი **ვერცერთხელ ვერაფერს ვერ ჰყოფს** (გაზომილია: `0`, იხ. Class-key audit). ამიტომ დამატებულია ცალკე, `10`-ელემენტიანი deterministic probe corpus (`restriction_probe_corpus()`), რომლის expression-ებსაც **removable restriction** აქვთ და სადაც key ნამდვილად მუშაობს:

| family | expressions | აზრი |
| --- | --- | --- |
| `point_pair` | `1 - x / x - 1`, `2 - x / x - 2`, `x - y / y - x` | ორივე parse შეზღუდულია, მაგრამ **სხვადასხვა წერტილში** |
| `restricted_vs_free` | `x / 1 - x - 1`, `x - 1 / 1 - x`, `x - 2 / 2 - x`, `x / x - 1 - x`, `x / x - x + 1` | ერთი parse შეზღუდულია, მეორე — არა |
| `control_no_split` | `x / x`, `(x * x - 1) / (x - 1)` | removable restriction არსებობს, მაგრამ ყველა class-ს იგივე აქვს — split **არ** ხდება |

მაგალითი: `1 - x / x - 1`-ს ორი class აქვს და ორივეს canonical text `-1`-ია; მათ მხოლოდ excluded points ჰყოფს:

```text
1 - x / x - 1  ->  [('-1', 'R', ('0',)), ('-1', 'R', ('1',))]
                    /  ყველაზე მჭიდრო:  1 - (x/x) - 1 = -1,  x != 0
                    -  ყველაზე მჭიდრო:  (1-x)/(x-1)  = -1,  x != 1
```

probe corpus **არ** არის `generate_corpus()`-ის ნაწილი: გამოქვეყნებული `3125`-იანი corpus ხუთი template-ის Cartesian product-ია და ზუსტად ისეთივე რჩება.

## Metric

Semantic class key იგივეა, რაც `parseatlas.analyze`-ში:

```text
key(E, G) = (canonical expression, domain, excluded points)
```

Domain და excluded points key-ს ნაწილია, რადგან canonical text-ის equality მარტო false equivalence class-ებს ქმნის (`x/x` მარტივდება `1`-მდე, მაგრამ `x = 0`-ზე undefined რჩება). თუ ეს კომპონენტები რეალურად მუშაობს, ცალკე იზომება — იხ. Class-key audit; მოკლე პასუხი: template corpus-ზე `0`, probe corpus-ზე `8`.

Matrix უჯრა:

```text
M[i][j] = |{ E in corpus : class(E, G_i) == class(E, G_j) }| / |corpus|
```

Representation sensitivity 0017-ის განსაზღვრებით და `parseatlas.grammar_matrix.representation_sensitivity`-ის ხელახალი გამოყენებით (formula არ არის დუბლირებული):

```text
S(E) = (strict semantic classes - 1) / 23
```

## Null model და control

Parser მხოლოდ იმ operator-ების binding power-ებს ადარებს, რომლებიც token sequence-ში ფაქტობრივად შეხვდა (0019-ის symbolic არგუმენტი). აქედან null model:

```text
forced(i, j, E) = 1  <=>  grammar G_i-ისა და G_j-ის precedence LEVELS,
                          O(E)-ზე restrict-ებული, იდენტურია
```

Restriction level-ების დონეზეა და არა flat ordering-ის, რომ control `G0` (tied levels `(* /) > (+ -)`) იმავე სქემაში ჩაჯდეს. `forced = 1` იძლევა byte-identical serialized AST-ს, ე.ი. აუცილებლად ერთსა და იმავე semantic class-საც. ამიტომ ლოგიკურად ვალიდურია:

```text
N[i][j] <= M[i][j]  ყველგან
X[i][j] = M[i][j] - N[i][j] >= 0        (EXCESS matrix)
```

ორივე უტოლობა corpus-ზე გაზომილია (`625` უჯრა, `0` დარღვევა) და test-ითაც არის დაფარული.

დამატებით იზომება მეორე, უფრო მკაცრი control — `ast_identity_matrix`: რამდენად ხშირად აქვს ორ grammar-ს byte-identical serialized AST. იგი მოიცავს support reduction-საც, parenthesization-საც და 0019-ის აუხსნელ დამატებით collapse-საც. `semantic_excess = M - ast_identity` არის ის agreement, სადაც AST სხვადასხვაა და მხოლოდ მათემატიკა ემთხვევა. corpus-ზე ზუსტად ერთი კიბე ჩნდება:

```text
forced (0.072000)  <=  ast identity (0.167333)  <=  observed (0.259307)
```

## Performance

`analyze_expression()` თითო expression-ზე `25` canonicalization-ს აკეთებს. აქ pipeline deduplicated-ია: grammars ჯერ serialized AST-ით ჯგუფდება და canonicalize მხოლოდ თითო DISTINCT AST-ზე ერთხელ იძახება.

- canonicalization calls მთელ corpus-ზე: `23125` (`analyze_expression`-ის გზაზე იქნებოდა `25 * 3125 = 78125`) — `3.38x` ნაკლები.
- `analyze_expression` hot loop-ში არ იძახება.

Multicore: expression-ები დამოუკიდებელია და canonicalization CPU-bound-ია, ამიტომ corpus process-ებზე იყოფა; worker count `os.cpu_count()`-იდან გამოითვლება `cores - 1`-ით (ერთი core headroom-ად), hardcoded constant არსად არის.

Wall clock ერთადერთი რიცხვია, რომელიც run-იდან run-ში იცვლება, და ის მანქანის დატვირთვაზეა დამოკიდებული. ამ სესიაში გაზომილი **ყველა** დაწყვილებული run:

| წყვილი | sequential (`workers=1`) | parallel (auto, 15 worker) | speedup | კონტექსტი |
| --- | --- | --- | --- | --- |
| A | `159.21 s` (`50.95 ms`/expr) | `27.21 s` (`8.71 ms`/expr) | `5.85x` | იმავე process-ში მეორე parallel run: `23.04 s` (`7.37 ms`/expr) |
| B | `258.57 s` | `83.91 s` | `3.08x` | მანქანაზე პარალელურად სხვა worker მუშაობდა |

ცალკეული parallel run-ები ანალიზის დროს: `26.46 s`, `28.25 s`.

- `parallel records == sequential records`: `True` ორივე წყვილში და ყველა ცალკეულ შედარებაში.
- **speedup-ის ერთი ზუსტი რიცხვი ამ მანქანაზე არ არსებობს**: `3.08x`-დან `5.85x`-მდე იცვლება იმის მიხედვით, დატვირთულია თუ არა მანქანა. კოდი run-ებს შორის არ შეცვლილა.

Parallelism მხოლოდ სიჩქარეს ცვლის; შედეგი sequential path-ის იდენტურია.

## დაკვირვებული შედეგები

### Matrix

- ზომა `25 x 25`, expression count `3125`, diagonal ყველგან `1.0`, matrix symmetric.

| matrix | mean off-diagonal | min | max |
| --- | --- | --- | --- |
| observed `M` | `0.259307` | `0.008000` | `1.000000` |
| support-forced null `N` | `0.072000` | `0.000000` | `0.600000` |
| excess `X = M - N` | `0.187307` | `0.008000` | `1.000000` |
| ast identity | `0.167333` | `0.000000` | `1.000000` |
| semantic excess `M - ast identity` | `0.091973` | `0.000000` | `0.800000` |

- საშუალო agreement-ის `27.8%` (`0.072000 / 0.259307`) support reduction-ით არის იძულებული და **აღმოჩენა არ არის**.
- null-ის maximum `0.600000` ზუსტად `1875 / 3125`-ია — ანუ support-forced block-ის წევრები იმ და მხოლოდ იმ expression-ებზე არიან იძულებით ერთად, სადაც support size `3`-ია.
- `ast_identity` საშუალოს `0.167333`-ს იძლევა, ე.ი. observed agreement-ის `64.5%` byte-identical AST-ით აიხსნება და `35.5%` წმინდა semantic collapse-ია.

Per-family საშუალო off-diagonal:

| family | observed | support-forced | excess |
| --- | --- | --- | --- |
| linear | `0.199467` | `0.000000` | `0.199467` |
| quadratic | `0.277333` | `0.120000` | `0.157333` |
| cubic | `0.186667` | `0.120000` | `0.066667` |
| rational | `0.355733` | `0.000000` | `0.355733` |
| mixed_chain | `0.277333` | `0.120000` | `0.157333` |

`linear` და `rational` family-ებზე null ნულია (support size `4`, ყველა block singleton-ია), ამიტომ მათი agreement მთლიანად excess-ია.

### ყველაზე მეტად და ყველაზე ნაკლებად თანხმობაში მყოფი წყვილები

EXCESS matrix-ზე:

```text
highest: G19-G21 = 1.000000    G11-G19 = 1.000000    G08-G19 = 1.000000
lowest : G0-G01  = 0.008000    G0-G02  = 0.008000    G0-G05  = 0.008000
```

`0.008 = 25 / 3125` — ეს არის corpus-ის ის `25` expression, სადაც ყველა grammar ერთ class-ში ხვდება (იხ. rigid-ები ქვემოთ). ე.ი. `G0`-სა და `G01`-ს შორის სხვა არცერთ expression-ზე თანხმობა არ არის.

`G19-G21 = 1.0` და `G05-G07 = 1.0` (forced `0.0`) იმას ნიშნავს, რომ ეს წყვილები **ყველა** `3125` expression-ზე ერთ semantic class-ში არიან, ხოლო null მათ არაფერს ავალდებულებს.

Semantic excess-ის maximum: `G0-G18 = 0.800000` და `G0-G24 = 0.800000`. Control grammar `G0` (`(* /) > (+ -)`) და strict `G18` (`* / - +`) / `G24` (`/ * - +`) corpus-ის `80%`-ზე სხვადასხვა AST-ს იძლევა და მაინც ერთსა და იმავე მათემატიკურ შედეგს: `(a + b) - c` და `a + (b - c)` სტრუქტურულად სხვადასხვაა, canonical form კი ერთი.

### Always-agree partition

"ერთ semantic class-ში ყველა expression-ზე" per-expression class identity-ის ტრანზიტულობის გამო equivalence relation-ია — ეს clustering hypothesis კი არა, ზუსტი გაზომვაა. `25` grammar `10` ჯგუფად იყოფა:

```text
(G0, G18, G24)
(G01, G02, G05, G07, G08, G11, G19, G21)
(G03)
(G04, G06, G20)
(G09)
(G10, G12, G22)
(G13)
(G14, G17, G23)
(G15)
(G16)
```

- always-agree unordered pairs: `40`
- support-forced pairs (`N = 0.6`): `36`
- forced pairs, რომლებიც ასევე always-agree არიან: `22`
- forced pairs, რომლებიც corpus-ზე **მაინც იშლებიან**: `14` (ყველა მათგანს `observed = 0.8400`)
- always-agree pairs, რომლებზეც null არაფერს ამბობს (`N = 0.0`): `18`

ე.ი. null არც sufficient და არც necessary არ არის observed partition-ისთვის: ის ერთდროულად აერთიანებს იმას, რაც corpus-ზე იშლება, და ვერ ითვალისწინებს იმას, რაც corpus-ზე ერთდება. **ეს ურთიერთობის გაზომვაა და არა "null-ის მიღმა cluster structure"-ის მტკიცებულება** — ქვემოთ ნაჩვენებია, რომ ამ partition-ის cluster-ებად გამოცხადება ისევ null-ს დააბრუნებდა.

ორი კონკრეტული სტრუქტურული დაკვირვება:

```text
merge : (G01 G02 G05 G19) + (G07 G08 G11 G21)  ->  ერთი 8-იანი ჯგუფი
        ეს არის ზუსტად ის 8 strict grammar, სადაც * ორივე +-სა და --ზე სუსტად ბოჭავს
split : block (+ > * > -) = (G03 G04 G06 G20)  ->  (G03) და (G04 G06 G20)
        block (* > - > +) = (G15 G16 G18 G24)  ->  (G15), (G16) და (G18 G24)
        გამყოფი არის `/`-ის პოზიცია; G03, G09, G13, G15-ს `/` ყველაზე სუსტი აქვს
```

Split იმ `1250` expression-ზე ჩნდება, სადაც `/` ნამდვილი operator-ია — null-ს ეს პრინციპულად არ შეუძლია დაინახოს, რადგან corpus-ის `60%`-ში `/` operator საერთოდ არ არსებობს.

Per-family always-agree partition:

| family | ჯგუფები | ზომები |
| --- | --- | --- |
| linear | 8 | `1, 1, 1, 2, 3, 3, 6, 8` |
| quadratic | 4 | `4, 4, 8, 9` |
| cubic | 5 | `4, 4, 4, 5, 8` |
| rational | 4 | `4, 4, 8, 9` |
| mixed_chain | 4 | `4, 4, 8, 9` |

`linear` ყველაზე discriminating family-ია (`8` ჯგუფი), `quadratic`, `rational` და `mixed_chain` კი ერთსა და იმავე `4`-ჯგუფიან partition-ს იძლევიან.

## AST diversity vs semantic diversity — ის, რაც null model-ს გადაურჩა

ეს ამ ექსპერიმენტის მთავარი **დადებითი** შედეგია. იგი null model-ის საკითხს საერთოდ არ ეხება: ის ერთი expression-ის შიგნით ორ სხვადასხვა სიდიდეს ადარებს — რამდენი **განსხვავებული AST** წარმოშვა `25` grammar-მა და რამდენ **semantic class-ად** დაიშალა ისინი.

| family | distinct AST (25 grammar-ზე) | `C(E)` distribution |
| --- | --- | --- |
| linear | `17` (მუდმივი) | `{3: 25, 4: 100, 6: 100, 8: 400}` |
| quadratic | `5` (მუდმივი) | `{3: 125, 4: 500}` |
| cubic | `6` (მუდმივი) | `{5: 625}` |
| rational | `4` (მუდმივი) | `{1: 25, 2: 200, 4: 400}` |
| mixed_chain | `5` (მუდმივი) | `{3: 125, 4: 500}` |

- overall AST diversity distribution: `{4: 625, 5: 1250, 6: 625, 17: 625}`
- overall `C(E)` distribution: `{1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400}`
- Pearson correlation (AST diversity, `C(E)`) მთელ corpus-ზე: `0.7676`
- **expressions, სადაც AST diversity ფიქსირებულია და `C(E)` მაინც იცვლება: `2500` (`0.8`)**

`0.7676` კორელაცია ერთი შეხედვით "ორივე ერთი და იგივეა"-ს ჰგავს; `2500 / 3125` აჩვენებს, რომ ეს ასე არ არის. ოთხივე family-ში, სადაც AST diversity ლიტერალურად მუდმივია (`17`, `5`, `4`, `5`), `C(E)` მაინც ორ ან ოთხ სხვადასხვა მნიშვნელობას იღებს. მხოლოდ `cubic`-ია გამონაკლისი: `625`-ივე expression-ს `6` AST და ზუსტად `5` semantic class აქვს.

**მფლობელის დაკვირვება `27`-ელემენტიან sweep-ზე (AST diversity `17`, `C(E)` `6` და `8`) corpus-ის მასშტაბით დადასტურდა და გაფართოვდა**: `linear` family-ის სრულ `625` expression-ზე AST diversity ყოველთვის ზუსტად `17`-ია, ხოლო `C(E)` ოთხ სხვადასხვა მნიშვნელობას იღებს — `3`, `4`, `6`, `8` — მათ შორის ორივე დაკვირვებული `6` და `8`.

`C(E)`-ის ცვალებადობა ფიქსირებულ AST diversity-ზე coefficient-ებზეა დამოკიდებული და ალგებრულად აიხსნება:

```text
rational : C(E) = 1 <=> a == 1 და c == 1        (25 expression)
           C(E) = 2 <=> a == 1 xor c == 1       (200 expression)
           C(E) = 4 <=> a != 1 და c != 1        (400 expression)
linear   : C(E) = 3 <=> a == 1 და d == 1        (25)
           C(E) = 4 <=> a != 1 და d == 1        (100)
           C(E) = 6 <=> a == 1 და d != 1        (100)
           C(E) = 8 <=> a != 1 და d != 1        (400)
```

მიზეზი: `a*(x + b) == a*x + b` მაშინ და მხოლოდ მაშინ, როცა `a == 1` — სხვადასხვა AST იმავე canonical form-ში ვარდება. ე.ი. grammar-ების რაოდენობა, რომლებიც განსხვავებულ **სტრუქტურას** აშენებენ, არაფერს ამბობს იმაზე, თუ რამდენ განსხვავებულ **ფუნქციას** მიიღებ; ეს ორი განზომილება coefficient-ებით იმართება და არა grammar-ებით.

## Rigid vs sensitive

- grammar-rigid (`S(E) = 0`, ოცდაოთხივე strict grammar ერთ class-ში): `25`
- grammar-sensitive: `3100`
- rigid fraction: `0.008`
- mean `S(E)`: `0.153739`, min `0.0`, max `0.304348` (= `7 / 23`, ზუსტად 0017-ის affine baseline)

`S(E)` distribution მთელ corpus-ზე:

```text
0.000000 : 25      0.043478 : 200     0.086957 : 275
0.130435 : 1500    0.173913 : 625     0.217391 : 100
0.304348 : 400
```

Per family:

| family | rigid | sensitive | mean `S` | min `S` | max `S` |
| --- | --- | --- | --- | --- | --- |
| linear | 0 | 625 | `0.253913` | `0.086957` | `0.304348` |
| quadratic | 0 | 625 | `0.121739` | `0.086957` | `0.130435` |
| cubic | 0 | 625 | `0.173913` | `0.173913` | `0.173913` |
| rational | 25 | 600 | `0.097391` | `0.000000` | `0.130435` |
| mixed_chain | 0 | 625 | `0.121739` | `0.086957` | `0.130435` |

ყველა `25` rigid expression `rational` family-შია და ყველა მათგანს `a == 1` და `c == 1` აქვს, ე.ი. ფორმა `(1*x + b)/(1*x - d)`. 0017-ის `(x + 1)/(x - 2)` სწორედ ამ ქვეოჯახის უკოეფიციენტო წევრია.

## Cluster structure — გაზომილი უარყოფითი შედეგი

### Diagonal policy (რომელი არჩევანი გაკეთდა და რატომ)

Agreement matrix-ის diagonal **გაზომვა არ არის, განსაზღვრებაა**: ყოველი grammar თავის თავს ყველა expression-ზე ეთანხმება. observed matrix-ში ეს მუდმივი `1.0`-ია, EXCESS matrix-ში კი `1.0 - 1.0 = 0.0`. თუ signature vector-ად matrix-ის ნედლი row აიღება, grammar თავის საკუთარ ღერძზე თავის თავს **მაქსიმალურად განსხვავებულად** გამოიყურება, და ეს ზუსტად ყველაზე თანხმობაში მყოფ წყვილებს აშორებს ერთმანეთს: `left`-ისა და `right`-ის სვეტების შენარჩუნება კვადრატულ მანძილს ზუსტად `2 * X[left][right]^2`-ს უმატებს.

არჩეული გამოსავალი: **diagonal გამორიცხულია** — `profile_distance(values, ids, left, right)` ორივე შესადარებელი grammar-ის საკუთარ სვეტს აგდებს და დარჩენილ `23` კოორდინატზე ითვლის L2-ს. ორივე სვეტი იშლება (და არა მხოლოდ თითოეულის საკუთარი), რომ profile-ები ერთსა და იმავე ღერძებზე შედარდეს და მანძილი symmetric დარჩეს. ალტერნატივა — diagonal-ისთვის რაიმე "თანმიმდევრული" მნიშვნელობის მინიჭება — უარყოფილია, რადგან ნებისმიერი ასეთი მნიშვნელობა თვითნებური იქნებოდა: excess-ის diagonal არითმეტიკულად უკვე სწორია (`0.0`), პრობლემა მისი მნიშვნელობა კი არა, მისი შედარებადობაა.

**რომელი ვექტორი ქვეყნდება.** `profile_distance` წყვილურია — ის ორივე შესადარებელი grammar-ის სვეტს აგდებს — ამიტომ ცალკე grammar-ისთვის ერთი signature vector **არ არსებობს**: ნებისმიერი სრული სიგრძის ვექტორი `u` კვადრატულ მანძილს დაამატებდა `(u_a[a] - X[b][a])^2 + (X[a][b] - u_b[b])^2`-ს, რაც ნულდება მხოლოდ მაშინ, თუ თითოეული შემავსებელი მნიშვნელობა `X[a][b]`-ს უდრის, ე.ი. **მეორე** grammar-ზეა დამოკიდებული. ამიტომ `grammar_clusters` აქვეყნებს `comparable_signatures[left][right]`-ს — ზუსტად იმ `23`-კოორდინატიან ვექტორს, რომელსაც მანძილი კითხულობს — და `identical_signature_groups` მისგან პირდაპირ აგდება: ორი grammar ერთ ჯგუფშია მაშინ და მხოლოდ მაშინ, როცა `comparable_signatures[left][right] == comparable_signatures[right][left]`. `24`-კოორდინატიანი row, რომელსაც მხოლოდ საკუთარი სვეტი აქვს მოცილებული, ცალკე ველად რჩება სახელით `matrix_rows_without_self` — ის საჩვენებელი row-ია და არა clustering-ის input; ჯგუფის წევრებს ის შეიძლება **განსხვავებული** ჰქონდეთ, რადგან თითოეული კვლავ ატარებს პარტნიორის სვეტს.

ამ შესწორების შემდეგ ხელახლა გაიშვა ყველაფერი. **cluster-ები არ შეცვლილა; შეიცვალა max distance, threshold და — არსებითად — identical-profile ჯგუფები**, რომლებიც ადრე diagonal-ის გამო `25` singleton-ად ჩანდა.

### Excess matrix-ზე clustering

`grammar_clusters` ჯერ იდენტურ profile-ებს აჯგუფებს, შემდეგ complete linkage-ით აგლომერაციას აკეთებს. Threshold documented rule-ია: `0.25 * max pairwise distance`. გარე clustering library არ არის გამოყენებული.

| სიდიდე | შესწორებამდე (diagonal-ით) | შესწორების შემდეგ |
| --- | --- | --- |
| max pairwise distance | `3.172008` | `3.171987` |
| threshold | `0.793002` | `0.792997` |
| identical-profile groups | `25` singleton | `12` ჯგუფი |
| clusters | `7`, `(1,4,4,4,4,4,4)` | `7`, `(1,4,4,4,4,4,4)` (უცვლელი) |

```text
(G0)
(G01, G02, G05, G19)
(G03, G04, G06, G20)
(G07, G08, G11, G21)
(G09, G10, G12, G22)
(G13, G14, G17, G23)
(G15, G16, G18, G24)
```

**ეს `7` cluster ზუსტად ემთხვევა support reduction-ის `7` block-ს support size `3`-ზე** (`* > +=-`, `+ > - > *`, `+ > * > -`, `- > + > *`, `- > * > +`, `* > + > -`, `* > - > +`). შემოწმდა პროგრამულად: `set(clusters) == set(support blocks)` არის `True`.

ე.ი. **null model-ის მოცილების შემდეგ ამ corpus-ზე residual cluster structure არ რჩება.** Corpus-ის `60%`-ს support size `3` აქვს, ამიტომ null matrix-ის row-ები თვითონ ატარებენ block partition-ს; observed-იდან null-ის pointwise გამოკლება ამ partition-ს excess-ის row-ებში იმპრინტავს, და clustering მას უცვლელად აბრუნებს.

შესწორებულმა metric-მა ერთი ახალი, გადამოწმებული ფაქტიც გამოამჟღავნა: `12` identical-profile ჯგუფი ზუსტად support-block partition-ისა და always-agree partition-ის **საერთო დაზუსტებაა** (meet). ესეც null-ის ჩარჩოში რჩება (ქვემოთა ბლოკი ვალიდაციის სექცია `2`-ის verbatim output-ია, ხელით არაფერია ჩაწერილი):

```text
excess identical-profile groups == meet(blocks, always-agree) : True
excess identical-profile group sizes : 4, 4, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1 | groups 12 | sum 25
```

### Observed matrix-ზე clustering — არც ესაა "null-ის მიღმა"

იმავე deterministic მეთოდით, იმავე threshold factor-ით, observed matrix-ის row-ებზე:

| სიდიდე | შესწორებამდე | შესწორების შემდეგ |
| --- | --- | --- |
| max pairwise distance | `3.810621` | `3.542980` |
| threshold | `0.952655` | `0.885745` |
| identical-profile groups | `10` | `10` |
| clusters | `4`, `(9,8,4,4)` | `4`, `(9,8,4,4)` (უცვლელი) |

```text
(G0, G13, G14, G15, G16, G17, G18, G23, G24)
(G01, G02, G05, G07, G08, G11, G19, G21)
(G03, G04, G06, G20)
(G09, G10, G12, G22)
```

**ამ `4` cluster-იდან `2` — `(G03, G04, G06, G20)` და `(G09, G10, G12, G22)` — verbatim support-forced block-ია.** ე.ი. observed-row clustering-ის ნახევარი პირდაპირ null model-ია და ის "null-ის მიღმა სტრუქტურად" ვერ გამოცხადდება.

დანარჩენი ორი cluster-იც არაა დამოუკიდებელი აღმოჩენა: observed matrix-ის identical-profile ჯგუფები ზუსტად always-agree partition-ია (`True`, `10` ჯგუფი), ხოლო `4` cluster იმ `10` ჯგუფის threshold-ით გამოწვეული გაერთიანებაა. სხვა threshold factor სხვა რიცხვს მისცემდა.

პირდაპირი მტკიცებულება იმისა, რომ excess-ის cluster-ები null-ის და არა agreement-ის სურათია: `G05` და `G07` corpus-ის ყველა expression-ზე თანხმდებიან (`observed = 1.0`, `excess = 1.0`), მაგრამ სხვადასხვა excess cluster-ში ხვდებიან, რადგან მათი **null** row-ები განსხვავდება.

### Cluster stability (half-split)

Corpus even/odd index-ით ორ ნახევრად იყოფა (`1563` და `1562` expression; family balance ორივე ნახევარში დაცულია interleaved generation-ის გამო), clusters თითო ნახევარზე თავიდან ითვლება და შედარება `25 * 24 / 2 = 300` grammar pair-ის together/apart verdict-ზე ხდება.

| signature | pair agreement | together in both / either | ნახევრების clusters | thresholds |
| --- | --- | --- | --- | --- |
| excess matrix | `1.0` (`300 / 300`) | `36 / 36` | იდენტური, `(1,4,4,4,4,4,4)` | `0.793236` და `0.792758` |
| observed matrix | `1.0` (`300 / 300`) | `76 / 76` | იდენტური, `(9,8,4,4)` | `0.886011` და `0.885479` |

Always-agree partition ორივე ნახევარზე ასევე ზუსტად იდენტურია (`10` ჯგუფი, სიმბოლო-სიმბოლოში იგივე).

**`1.0` stability არცერთ შემთხვევაში არ არის იმის მტკიცებულება, რომ სტრუქტურა რეალურია.** excess-ის cluster-ები null-ის block-ებია, ხოლო block-ები corpus-ის ნებისმიერ ქვესიმრავლეზე იდენტურია განსაზღვრებით — ისინი grammar-ისა და `O(E)`-ის ფუნქციაა და არა მონაცემების. observed-ის `76 / 76`-იც იმავე პრობლემას იზიარებს იმ ნაწილში, რომელიც support block-ებს ემთხვევა. Stability აქ იმას ზომავს, რომ **მეთოდი** deterministic-ია, და არა იმას, რომ **სტრუქტურა** არსებობს.

## Class-key audit — რას აკეთებს `(F, D, U)` key რეალურად

`key_discrimination_report` ითვლის, რამდენი semantic class **მოისპობოდა**, key რომ მხოლოდ canonical text-ი ყოფილიყო.

| corpus | expressions | classes | canonical texts | classes lost without `(D, U)` | expressions სადაც key ჰყოფს |
| --- | --- | --- | --- | --- | --- |
| template (`generate_corpus`) | `3125` | `14175` | `14175` | **`0`** | **`0`** |
| restriction probe | `10` | `22` | `14` | **`8`** | **`8`** |

- template corpus-ზე `625` expression-ს (მთელი `rational` family) **აქვს** restricted class, მაგრამ ერთი expression-ის შიგნით ყველა class-ს იგივე restriction აქვს, ამიტომ key-ს დამატებითი კომპონენტები არაფერს ჰყოფენ. `3125`-ზე `classes == canonical_texts == 14175`.
- probe corpus-ზე `10`-იდან `8` expression-ს key ნამდვილად ჰყოფს; ორივე `control_no_split` item-ს — `x / x` და `(x * x - 1) / (x - 1)` — restriction აქვს, მაგრამ split `0`-ია, ე.ი. split ავტომატური არ არის.
- `domain` კომპონენტი **არსად არაფერს ჰყოფს და ვერც გაჰყოფს**: `canonicalize()` domain-ს უპირობოდ `"R"`-ს აბრუნებს, ამიტომ ორივე corpus-ზე `domain_values == ('R',)`. key contractually სწორია (იგივეა, რაც `analyze_expression`-ში), მაგრამ მისი `D` ნახევარი ამ generation-ში მკვდარი კომპონენტია.

## ინტერპრეტაცია

1. **T14 არ დასტურდება — ეს მთავარი შედეგია.** null model-ის მოცილების შემდეგ ამ corpus-ზე residual cluster structure არ რჩება: excess-ის `7` cluster სიმრავლედ ზუსტად support size `3`-ის `7` support-reduction block-ია (`True`). observed-ზე გადასვლა ამას არ ხსნის — იქაური `4` cluster-იდან `2` verbatim support block-ია. **უარყოფითი შედეგი პატიოსნად ნათქვამი უფრო ღირებულია, ვიდრე promoted artifact**, რომელიც ყველა შემდგომ claim-ს მოწამლავდა.

2. **რა არის mechanically იძულებული.** საშუალო off-diagonal agreement `0.259307`; მისგან `0.072000` (`27.8%`) support reduction-ითაა იძულებული, `0.167333` კი byte-identical AST-ითაა ახსნილი. `36` grammar pair `1875` expression-ზე (support size `3`) იძულებით ერთ class-შია. ეს parsing artifact-ია და არა აღმოჩენა.

3. **რატომ ჩავარდა excess-ის clustering.** corpus-ის `60%`-ს support size `3` აქვს, ამიტომ null matrix-ის row-ები თვითონ ატარებენ block partition-ს, `M - N` კი მას excess-ის row-ებში იმპრინტავს. ეს **corpus-ის თვისებაა და არა მეთოდის ბაგი**: `1875 / 1250` დისბალანსი null-ის სიგნალს excess-ში დომინანტს ხდის. სხვა support distribution-ზე (`1` და `2` ზომებით, ან `4`-ის უპირატესობით) იგივე მეთოდი სხვას მოგვცემდა — ეს ჯერ არ არის გაზომილი.

4. **რა გადარჩა დადებით შედეგად.** AST diversity და semantic diversity ორი დამოუკიდებელი სიდიდეა: `3125`-იდან `2500` expression-ზე (`0.8`) AST diversity ფიქსირებულია და `C(E)` მაინც იცვლება, Pearson `0.7676`-ის მიუხედავად. ეს null model-ს არ ეხება, ოთხივე non-`cubic` family-ში ჩანს და coefficient-ებით ალგებრულად აიხსნება (`a == 1` და `c == 1` კრიტერიუმებით, ზუსტი count-ებით). სწორედ ეს არის ის, რაც ამ ექსპერიმენტიდან შემდეგში წაიღება.

5. **Always-agree partition რჩება ყველაზე მკვეთრ corpus-relative გაზომვად, მაგრამ ის cluster claim არ არის.** ის exact equivalence relation-ია და არა threshold-ის შედეგი, ამიტომ threshold-ის არჩევანზე არ არის დამოკიდებული. მისი `40` pair-იდან `22` forced-ია, `18`-ს null არაფერს ეუბნება, ხოლო `36` forced pair-იდან `14` corpus-ზე იშლება (`observed = 0.84`). ე.ი. null არც sufficient და არც necessary არაა observed partition-ისთვის. მაგრამ ეს **ურთიერთობის აღწერაა** და არა მტკიცებულება იმისა, რომ არსებობს null-ის მიღმა grammar-space cluster structure.

6. **Clusters corpus-relative-ია და hypothesis-ია.** არც excess-ის `7`, არც observed-ის `4` cluster და არც `10`-ჯგუფიანი always-agree partition არ არის permutation group-ის დამტკიცებული ალგებრული თვისება. "`*` ორივე `+`-სა და `-`-ზე სუსტია, მაშასადამე grammar-ები განურჩეველია" და "`/`-ის პოზიცია არის გამყოფი" **hypotheses**-ია, რომლებიც სპეციალურად ამ claim-ისთვის აგებულ corpus-ს და symbolic არგუმენტს მოითხოვს.

7. **Corpus controlled template-ებისგან შედგება.** ხუთი template, ოთხი პარამეტრი, coefficient-ები `{1,...,5}`-დან, ყველა variable ერთი და იგივე `x`, არცერთ expression-ში unary minus, უარყოფითი ან დიდი კოეფიციენტი. აქედან გამომდინარე ეს შედეგები **არაფერს ამბობს თვითნებურ expression-ებზე** — არც უარყოფითი შედეგი ვრცელდება მათზე: T14 აქ **ამ corpus-ზე** არ დასტურდება, და არა საერთოდ.

## შეზღუდვები

- corpus `3125` expression-ია, მაგრამ მხოლოდ `5` template-ისა და `5` coefficient მნიშვნელობის Cartesian product; ეს არის სიღრმე და არა სიგანე.
- support size distribution დისბალანსირებულია (`1875` vs `1250`) და მასში `1` და `2` საერთოდ არ არის; null model-ის ძალა და, შესაბამისად, უარყოფითი შედეგიც უშუალოდ ამ distribution-ზეა დამოკიდებული.
- excess-based clustering ამ corpus-ზე null-ის partition-ს აბრუნებს; მეთოდი ინახება, რადგან სპეციფიკაციით სწორედ ის იყო მოთხოვნილი, მაგრამ მისი შედეგი structure claim-ად არ გამოდგება.
- cluster threshold documented rule-ია (`0.25 * max distance`) და არა ოპტიმიზებული სიდიდე; სხვა factor სხვა cluster count-ს მისცემდა. threshold-ის მგრძნობელობა (sweep) არ არის გაზომილი.
- diagonal signature-იდან გამორიცხულია; ეს არჩევანია და არა ერთადერთი შესაძლებლობა. სხვა თანმიმდევრული განსაზღვრება სხვა მანძილებს მისცემდა — cluster-ები ამ corpus-ზე არ შეიცვალა, მაგრამ ეს ზოგადი გარანტია არ არის.
- `domain` კომპონენტი semantic class key-ში ამ generation-ში მკვდარია: `canonicalize()` ყოველთვის `"R"`-ს აბრუნებს, ამიტომ ორივე corpus-ზე `domain_values == ('R',)`. მხოლოდ `excluded points` მუშაობს.
- `excluded points` template corpus-ზე **არაფერს ჰყოფს** (`0` of `3125`); მისი დისციპლინა მხოლოდ `10`-ელემენტიან probe corpus-ზეა load-bearing (`8` split). ე.ი. მთავარი corpus ამ key-ს არ ამოწმებს.
- `undefined_terms` excluded point-ს მხოლოდ პირველი (ანბანურად) ცვლადისთვის ხსნის, ამიტომ probe-ის `x - y / y - x` წერტილად `'y'`-ს აბრუნებს და არა წყვილს; ეს `canonical`-ის შეზღუდვაა და ამ card-ის scope-ში არ შედის.
- half-split stability ერთადერთი resampling-ია; bootstrap ან family-holdout არ არის გაშვებული. `1.0` stability, როგორც ზემოთაა ნაჩვენები, აქ სტრუქტურას არ ადასტურებს.
- agreement semantic class equality-ს ზომავს, არა structural AST equality-ს — `ast_identity_matrix` ცალკე იზომება სწორედ ამ განსხვავების საჩვენებლად.
- `G0` control matrix-შია ჩართული; strict-only ანალიზი ცალკე უნდა დარჩეს, როგორც 0017-ში იყო აღნიშნული.
- wall clock ერთი მანქანის გაზომვაა (`16` core, Windows, spawn start method), პორტატული არ არის და დატვირთვაზეა დამოკიდებული: ამავე კოდზე დაწყვილებული speedup `3.08x`-დან `5.85x`-მდე იცვლებოდა.

## Evidence-ის კლასიფიკაცია

- corpus size, family counts, support size distribution, ყველა matrix მნიშვნელობა, cluster list, threshold, stability score, `C(E)` და `S(E)` distribution-ები, class-key audit-ის რიცხვები, wall clock — executable **observations**.
- `N[i][j] <= M[i][j]` და `X[i][j] >= 0` — **symbolically justified** 0019-ის parser argument-იდან (იდენტური restricted levels იძლევა byte-identical AST-ს და მაშასადამე ერთ semantic class-ს) და დამატებით მთელ corpus-ზე **observed** (`625` უჯრა, `0` დარღვევა).
- "excess clusters == support reduction blocks" — **observation** ამ corpus-ზე, `set` თანასწორობით შემოწმებული; მისი მიზეზი (support size distribution) **explanation**-ია და არა law.
- "T14 ამ corpus-ზე არ დასტურდება" — **measured negative result**, რომელიც პირდაპირ ზემოთა observation-იდან გამომდინარეობს. ის **არ** არის მტკიცება, რომ grammar-space-ში cluster structure საერთოდ არ არსებობს.
- AST/semantic decoupling `2500 / 3125`-ზე — **observation**; მისი ალგებრული ახსნა (`a == 1` ატოლებს `a*(x+b)`-ს `a*x+b`-ს) — **symbolically justified** და corpus-ზე ზუსტი count-ებით **observed**.
- always-agree partition-ის `10` ჯგუფი, `8`-იანი merge და `/`-ით გამოწვეული split — **observations**; მათი ზოგადი ალგებრული ფორმულირება **hypothesis**-ია.
- ნებისმიერი ზოგადი კანონი grammar-space-ის cluster სტრუქტურაზე — ჯერ **არ არის claimed** არც დადებითი და არც უარყოფითი მიმართულებით.

## ვალიდაცია

### 1. სრული pipeline

```text
python -c "from parseatlas.corpus_matrix import generate_corpus, corpus_matrix, grammar_clusters, cluster_stability, diversity_report, rigidity_classification, key_discrimination_report, extreme_pairs; c = generate_corpus(); m = corpus_matrix(c); r = m['records']; print('corpus', m['expression_count'], m['family_counts'], m['support_size_counts']); print('run', m['workers'], 'workers', round(m['wall_clock_seconds'], 2), 's on', m['cpu_count'], 'cores'); k = grammar_clusters(m); print('excess clusters', k['cluster_count'], k['cluster_sizes'], 'maxd', round(k['max_distance'], 6), 'thr', round(k['threshold'], 6)); print(k['clusters']); print('excess identical-profile groups', k['identical_signature_groups']); o = grammar_clusters(m, signature_key='matrix'); print('observed clusters', o['cluster_count'], o['cluster_sizes'], 'maxd', round(o['max_distance'], 6), 'thr', round(o['threshold'], 6)); print(o['clusters']); print('always-agree', m['always_agree_partition']); s = cluster_stability(c, records=r); t = cluster_stability(c, records=r, signature_key='matrix'); print('stability excess', s['pair_agreement'], s['together_in_both'], '/', s['together_in_either'], '| observed', t['pair_agreement'], t['together_in_both'], '/', t['together_in_either']); print('excess extremes', extreme_pairs(m, 'excess_matrix', 3)); d = diversity_report(c, records=r)['overall']; print('ast', d['ast_diversity_distribution'], 'classes', d['class_count_distribution'], 'corr', round(d['correlation'], 4), 'decoupled', d['constant_ast_varying_class_count'], d['constant_ast_varying_class_fraction']); g = rigidity_classification(c, records=r)['overall']; print('rigid', g['rigid'], 'sensitive', g['sensitive'], 'meanS', round(g['mean_sensitivity'], 6)); a = key_discrimination_report(c, records=r)['overall']; print('key audit', a['classes'], 'classes', a['canonical_texts'], 'texts', 'lost without restrictions', a['classes_lost_without_the_restriction_key'], 'restricted', a['expressions_with_a_restricted_class'], 'domains', a['domain_values'])"
```

```text
corpus 3125 {'linear': 625, 'quadratic': 625, 'cubic': 625, 'rational': 625, 'mixed_chain': 625} {3: 1875, 4: 1250}
run 15 workers 28.25 s on 16 cores
excess clusters 7 (1, 4, 4, 4, 4, 4, 4) maxd 3.171987 thr 0.792997
(('G0',), ('G01', 'G02', 'G05', 'G19'), ('G03', 'G04', 'G06', 'G20'), ('G07', 'G08', 'G11', 'G21'), ('G09', 'G10', 'G12', 'G22'), ('G13', 'G14', 'G17', 'G23'), ('G15', 'G16', 'G18', 'G24'))
excess identical-profile groups (('G0',), ('G01', 'G02', 'G05', 'G19'), ('G03',), ('G04', 'G06', 'G20'), ('G07', 'G08', 'G11', 'G21'), ('G09',), ('G10', 'G12', 'G22'), ('G13',), ('G14', 'G17', 'G23'), ('G15',), ('G16',), ('G18', 'G24'))
observed clusters 4 (9, 8, 4, 4) maxd 3.54298 thr 0.885745
(('G0', 'G13', 'G14', 'G15', 'G16', 'G17', 'G18', 'G23', 'G24'), ('G01', 'G02', 'G05', 'G07', 'G08', 'G11', 'G19', 'G21'), ('G03', 'G04', 'G06', 'G20'), ('G09', 'G10', 'G12', 'G22'))
always-agree (('G0', 'G18', 'G24'), ('G01', 'G02', 'G05', 'G07', 'G08', 'G11', 'G19', 'G21'), ('G03',), ('G04', 'G06', 'G20'), ('G09',), ('G10', 'G12', 'G22'), ('G13',), ('G14', 'G17', 'G23'), ('G15',), ('G16',))
stability excess 1.0 36 / 36 | observed 1.0 76 / 76
excess extremes {'lowest': [('G0', 'G01', 0.008), ('G0', 'G02', 0.008), ('G0', 'G05', 0.008)], 'highest': [('G19', 'G21', 1.0), ('G11', 'G19', 1.0), ('G08', 'G19', 1.0)]}
ast {4: 625, 5: 1250, 6: 625, 17: 625} classes {1: 25, 2: 200, 3: 275, 4: 1500, 5: 625, 6: 100, 8: 400} corr 0.7676 decoupled 2500 0.8
rigid 25 sensitive 3100 meanS 0.153739
key audit 14175 classes 14175 texts lost without restrictions 0 restricted 625 domains ('R',)
```

### 2. უარყოფითი შედეგის პირდაპირი შემოწმება

```text
python -c "from parseatlas.corpus_matrix import generate_corpus, corpus_matrix, grammar_clusters; c = generate_corpus(); m = corpus_matrix(c); r = m['records']; S = lambda gs: {tuple(sorted(g)) for g in gs}; three = next(x for x in r if x['support_size'] == 3); b = {}; [b.setdefault(v, []).append(k) for k, v in three['support_blocks'].items()]; blocks = S(b.values()); a = m['always_agree_partition']; k = grammar_clusters(m); o = grammar_clusters(m, signature_key='matrix'); meet = [tuple(sorted(set(x) & set(y))) for x in b.values() for y in a if set(x) & set(y)]; g = k['identical_signature_groups']; sizes = sorted((len(x) for x in g), reverse=True); print('support blocks at |O(E)|=3 :', sorted(blocks)); print('excess clusters == support blocks :', S(k['clusters']) == blocks); print('observed clusters that ARE support blocks :', sorted(S(o['clusters']) & blocks)); print('observed identical-profile groups == always-agree :', S(o['identical_signature_groups']) == S(a)); print('excess identical-profile groups == meet(blocks, always-agree) :', S(k['identical_signature_groups']) == S(meet)); print('excess identical-profile group sizes :', ', '.join(map(str, sizes)), '| groups', len(sizes), '| sum', sum(sizes))"
```

```text
support blocks at |O(E)|=3 : [('G0',), ('G01', 'G02', 'G05', 'G19'), ('G03', 'G04', 'G06', 'G20'), ('G07', 'G08', 'G11', 'G21'), ('G09', 'G10', 'G12', 'G22'), ('G13', 'G14', 'G17', 'G23'), ('G15', 'G16', 'G18', 'G24')]
excess clusters == support blocks : True
observed clusters that ARE support blocks : [('G03', 'G04', 'G06', 'G20'), ('G09', 'G10', 'G12', 'G22')]
observed identical-profile groups == always-agree : True
excess identical-profile groups == meet(blocks, always-agree) : True
excess identical-profile group sizes : 4, 4, 3, 3, 3, 2, 1, 1, 1, 1, 1, 1 | groups 12 | sum 25
```

### 3. Restriction probe და class-key audit

```text
python -c "from parseatlas.corpus_matrix import restriction_probe_corpus, key_discrimination_report, expression_classes; p = restriction_probe_corpus(); a = key_discrimination_report(p, workers=1); print('probe', p['size'], p['family_counts']); print('overall', a['overall']['classes'], 'classes', a['overall']['canonical_texts'], 'texts', 'lost without restrictions', a['overall']['classes_lost_without_the_restriction_key'], 'split expressions', a['overall']['expressions_where_the_restriction_key_splits_a_class'], 'domains', a['overall']['domain_values']); print({f: (b['expression_count'], b['expressions_where_the_restriction_key_splits_a_class']) for f, b in a['families'].items()}); e = expression_classes('1 - x / x - 1'); print('1 - x / x - 1 ->', sorted((v['canonical'], v['domain'], tuple(v['excluded_points'])) for v in e['class_keys'].values()))"
```

```text
probe 10 {'point_pair': 3, 'restricted_vs_free': 5, 'control_no_split': 2}
overall 22 classes 14 texts lost without restrictions 8 split expressions 8 domains ('R',)
{'point_pair': (3, 3), 'restricted_vs_free': (5, 5), 'control_no_split': (2, 0)}
1 - x / x - 1 -> [('-1', 'R', ('0',)), ('-1', 'R', ('1',))]
```

### 4. Canonicalization saving

```text
python -c "from parseatlas.corpus_matrix import generate_corpus, corpus_records; c = generate_corpus(); r = corpus_records(c)['records']; total = sum(x['distinct_ast_count'] for x in r); print('canonicalizations', total, 'vs analyze_expression', 25 * len(r), 'saving', round(25 * len(r) / total, 2))"
```

```text
canonicalizations 23125 vs analyze_expression 78125 saving 3.38
```

### 5. Parallel/sequential ეკვივალენტობა და timing

```text
python -c "from parseatlas.corpus_matrix import generate_corpus, corpus_records; c = generate_corpus(); p = corpus_records(c); s = corpus_records(c, workers=1); q = corpus_records(c); print('parallel  ', p['workers'], round(p['wall_clock_seconds'], 2)); print('sequential', s['workers'], round(s['wall_clock_seconds'], 2)); print('parallel-2', q['workers'], round(q['wall_clock_seconds'], 2)); print('speedup   ', round(s['wall_clock_seconds']/p['wall_clock_seconds'], 2)); print('per-expression ms parallel', round(1000*p['wall_clock_seconds']/3125, 2), 'sequential', round(1000*s['wall_clock_seconds']/3125, 2)); print('identical', p['records'] == s['records'] == q['records'])"
```

```text
parallel   15 27.21
sequential 1 159.21
parallel-2 15 23.04
speedup    5.85
per-expression ms parallel 8.71 sequential 50.95
identical True
```

მეორე დაწყვილებული run, როცა მანქანაზე პარალელურად სხვა worker მუშაობდა:

```text
sequential 1 258.57
parallel   15 83.91
speedup    3.08
identical True
```

### 6. Tests

ამ card-ის საკუთარი test file — card-ით კონტროლირებადი რიცხვი:

```text
python -m pytest -q tests/test_corpus_matrix.py
43 passed in 8.60s          # დაფიქსირდა 2026-09-02T19:31:28Z
```

მთლიანი suite — **timestamped observation**, არა card-ით კონტროლირებადი სიდიდე: მას მეზობელი ექსპერიმენტების worker-ები პარალელურად ზრდიან, ამიტომ ის ამ card-ის acceptance criterion ვერ იქნება.

```text
python -m pytest -q
216 passed in 50.60s          # დაფიქსირდა 2026-09-02T18:33:01Z
243 passed in 40.46s          # დაფიქსირდა 2026-09-02T19:01:58Z
272 passed in 44.67s          # დაფიქსირდა 2026-09-02T19:31:09Z
```

შუალედურ run-ში (`2026-09-02T18:5x`) დაფიქსირდა `2 failed, 241 passed`; ორივე failure `tests/test_cross_validation.py`-ში იყო — მეზობელი card-ის (ექსპერიმენტი 0025) ფაილი, რომელიც იმ მომენტში იწერებოდა და ამ card-ის allowed writes-ში არ შედის. `src/parseatlas/cross_validation.py` `corpus_matrix`-ს არ იმპორტირებს. მომდევნო run-ზე იგივე ფაილი ცალკეც (`17 passed`) და suite-შიც (`243 passed`) გაწმინდა. ამ card-ის `tests/test_corpus_matrix.py` ყველა run-ზე `42 passed` იყო.
