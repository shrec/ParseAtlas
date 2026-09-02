# ParseAtlas ექსპერიმენტი 0021: invariant operation multiset და variable critical-path depth

## მიზანი

ამ ფაზაში გავზომეთ, თუ რას ცვლის grammar არჩევა parse-ის cost-ში. Claim, რომელიც შემოწმდა: ფიქსირებული token sequence-ისთვის raw operation multiset — `add`, `sub`, `mul`, `div` და node count — ერთი და იგივეა ყველა grammar-ისთვის, რადგან თითოეული parse ზუსტად იმავე operator token-ებს მოიხმარს. ის, რასაც grammar ნამდვილად ცვლის, არის AST critical-path depth და, შესაბამისად, dependency structure და post-canonicalization cost.

## Cost model

- `raw_cost_signature(source, grammar)` აბრუნებს `parseatlas.canonical.operation_cost`-ის depth-გარეშე ნაწილს: `add`, `sub`, `mul`, `div`, `nodes`.
- `depth_profile(source)` `G0` control-ს პლიუს `G01..G24` strict grammars-ს ატარებს და აფიქსირებს min/max depth, depth spread, min/max depth grammars და control depth.
- `cost_invariance_report(expressions)` raw signature-ის invariance-ს ადარებს depth profile-ს და canonical cost-ს, სადაც canonical cost არის `sympy.count_ops` `parseatlas.canonical.canonicalize(ast)["sympy_expression"]`-ზე.

Signature-იდან `depth` განზრახ არის ამოღებული: სწორედ depth არის grammar-დამოკიდებული ნაწილი.

## Corpus

შემოწმდა:

```text
2*t + 1 - t/2
a + b*c - d/e
2*x*x + 1 - x/2
a - b*c + d/e - f
a/b + c*d - e/f + g
(x + 1)/(x - 2)
```

## დაკვირვებული შედეგები

grammar count: `25` (`G0` control + `G01..G24` strict).

| expression | raw signature (add/sub/mul/div/nodes) | min depth | max depth | spread | control depth | control is minimal |
|---|---|---|---|---|---|---|
| `2*t + 1 - t/2` | 1/1/1/1/9 | 4 | 5 | 1 | 4 | yes |
| `a + b*c - d/e` | 1/1/1/1/9 | 4 | 5 | 1 | 4 | yes |
| `2*x*x + 1 - x/2` | 1/1/2/1/11 | 4 | 6 | 2 | 5 | no |
| `a - b*c + d/e - f` | 1/2/1/1/11 | 4 | 6 | 2 | 5 | no |
| `a/b + c*d - e/f + g` | 2/1/1/2/13 | 4 | 6 | 2 | 5 | no |
| `(x + 1)/(x - 2)` | 1/1/0/1/7 | 3 | 3 | 0 | 3 | yes |

Aggregate:

- `expression_count`: `6`
- `all_raw_signatures_invariant`: `True`
- `mean_depth_spread`: `1.3333`
- `max_depth_spread`: `2`
- თითო expression-ზე `distinct_raw_signatures` = `1`.

Canonical cost იმავე corpus-ზე invariant **არ** არის:

| expression | canonical min | canonical max | distinct counts | min-depth grammars |
|---|---|---|---|---|
| `2*t + 1 - t/2` | 0 | 4 | 5 | 17 |
| `a + b*c - d/e` | 4 | 5 | 2 | 17 |
| `2*x*x + 1 - x/2` | 0 | 6 | 6 | 11 |
| `a - b*c + d/e - f` | 5 | 7 | 3 | 10 |
| `a/b + c*d - e/f + g` | 6 | 10 | 5 | 4 |
| `(x + 1)/(x - 2)` | 3 | 3 | 1 | 25 |

## ინტერპრეტაცია

```text
fixed token sequence -> fixed operation multiset -> variable dependency structure
```

Raw multiset invariance ნიშნავს, რომ grammar ვერ ცვლის იმას, **რამდენ** arithmetic operation-ს ასრულებს raw parse; ის მხოლოდ იმას ცვლის, **როგორ** არიან ეს operation-ები ერთმანეთზე დამოკიდებული. `a/b + c*d - e/f + g`-ზე depth 4-დან 6-მდე მერყეობს იმავე `2/1/1/2/13` signature-ზე, ანუ ერთი და იგივე ექვსი binary operation (`add` 2 + `sub` 1 + `mul` 1 + `div` 2, `nodes` 13 = 6 operator node + 7 leaf) სამ განსხვავებულ dependency chain-ში ეწყობა და მხოლოდ `4` grammar აღწევს min_depth-ს.

Rigid rational expression `(x + 1)/(x - 2)` საწინააღმდეგო ბოძია: parenthesization depth-ს ფიქსირებულს ტოვებს, spread `0` არის და სამივე ოპერაცია ყველა grammar-ში ერთსა და იმავე structure-ს ინარჩუნებს.

Control grammar `G0` ყოველთვის minimal არ არის: ექვსი expression-იდან სამზე `control_is_minimal` არის `False`, ანუ conventional precedence ამ corpus-ზე ყოველთვის ყველაზე მოკლე critical path-ს არ იძლევა.

Canonical cost-ის ცვალებადობა აჩვენებს, რომ invariance მხოლოდ raw parse-ის თვისებაა: canonicalization-ის შემდეგ grammar-ები სხვადასხვა semantic class-ში ხვდებიან და `count_ops` მათ სხვადასხვანაირად ითვლის (მაგალითად `2*x*x + 1 - x/2`-ზე `6` განსხვავებული canonical count).

## შეზღუდვები

- ეს ექსპერიმენტი structure-ს ზომავს და არა time-ს: **არავითარი wall-clock ან performance claim აქ არ კეთდება**. `depth` `canonical.operation_cost`-ის განსაზღვრებით leaf-ს `1`-ს აძლევს და თითო `Binary` node-ს `max(left, right) + 1`-ს, ამიტომ ის AST-ის დონეების რაოდენობაა leaf level-ის ჩათვლით და operator dependency-chain length-ზე ზუსტად ერთით მეტია (`depth` `4` = ზედიზედ `3` operator); ეს არ არის გაზომილი latency, ხოლო parallel-evaluation cost მხოლოდ როგორც structural upper bound იგულისხმება.
- corpus ექვსი expression-ისგან შედგება და ხელით არის შერჩეული.
- cost model უნიფორმულია: ყველა operation ერთნაირად ითვლება, `mul` და `div` განსხვავებული weight-ით არ არის აღრიცხული.
- signature `nodes`-ს ითვლის leaf-ების ჩათვლით, ამიტომ node count token count-ზეა მიბმული და არა მხოლოდ operator count-ზე.
- canonical cost `sympy.count_ops`-ის მეტრიკაზეა დამოკიდებული და სხვა canonicalization pipeline სხვა რიცხვებს მისცემდა.

## Evidence-ის კლასიფიკაცია

- raw operation multiset-ის invariance: **observation** (ექვსივე expression-ზე `distinct_raw_signatures == 1`) და **symbolically justified** — operator token multiset input-ითაა ფიქსირებული, ხოლო parser თითოეულ token-ს ზუსტად ერთხელ მოიხმარს და თითო operator token-ზე ზუსტად ერთ `Binary` node-ს ქმნის, ამიტომ counts grammar-ისგან დამოუკიდებელია.
- depth-ის ცვალებადობა grammar-ის მიხედვით: **observation** (spread `0`-დან `2`-მდე, `mean_depth_spread` = `1.3333`).
- control grammar-ის არა-მინიმალურობა სამ expression-ზე: **observation**.
- canonical cost-ის არა-invariance: **observation**.
- ის, რომ minimal depth რეალურ parallel hardware-ზე უფრო სწრაფ evaluation-ს იძლევა: **hypothesis** — ამ ექსპერიმენტში არ არის გაზომილი.

## ვალიდაცია

```text
python -c "from parseatlas.critical_path import cost_invariance_report; r = cost_invariance_report(('2*t + 1 - t/2', 'a + b*c - d/e', '2*x*x + 1 - x/2', 'a - b*c + d/e - f', 'a/b + c*d - e/f + g', '(x + 1)/(x - 2)')); print(r['expression_count'], r['all_raw_signatures_invariant'], round(r['mean_depth_spread'], 4), r['max_depth_spread']); [print(i['expression'], dict(i['raw_signature']), i['depth_profile']['min_depth'], i['depth_profile']['max_depth'], i['depth_profile']['depth_spread'], i['depth_profile']['control_depth'], i['depth_profile']['control_is_minimal'], len(i['depth_profile']['min_depth_grammars']), i['canonical_cost']) for i in r['expressions']]"
```

```text
python -m pytest -q tests/test_critical_path.py
9 passed
```
