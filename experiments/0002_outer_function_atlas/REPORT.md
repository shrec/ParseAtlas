# ParseAtlas ექსპერიმენტი 0002: Outer-Function Atlas

## შესავალი გამოსახულება

```text
2*t + 1 - t/2
```

## კონფიგურაცია

შიდა expression თითოეული grammar-ისთვის ერთხელ დაიპარსა Generation 1 custom parser-ით. ყოველი AST symbolic expression-ად გარდაიქმნა და შემდეგ ამ outer function-ებზე გაანალიზდა:

```text
sin, cos, tan, exp, log, sqrt, abs,
asin, acos, atan, reciprocal, square, cube
```

ანალიზმა გამოიყენა `G0` და `G01..G24`, სულ 25 inner grammar result. Inner undefined metadata ყველა outer-function result-ში გადაეცა.

## დაკვირვებული შედეგები

- გაანალიზდა 13 outer function.
- შეიქმნა 325 outer-function result (`25 * 13`).
- ამ input-ზე თითოეულმა outer-function family-მ 8 განსხვავებული canonical form შექმნა.
- 25 inner grammar interpretation-იდან 4-ს ჰქონდა constant argument.
- ეს grammar-ები შეესაბამება inner canonical form-ს `1`.

ტრიგონომეტრიული family-ებისთვის გაზომილი period-ები იყო:

| Inner coefficient of `t` | Frequency | Period |
|---:|---:|---:|
| `0` | `0` | constant argument |
| `1/2` | `1/2` | `4*pi` |
| `1` | `1` | `2*pi` |
| `3/2` | `3/2` | `4*pi/3` |

For `tan(a*t+b)`, the corresponding periods are `pi/abs(a)`: `2*pi`, `pi`, and `2*pi/3` for `a = 1/2`, `1`, and `3/2`.

`sin` and `cos` use period `2*pi/abs(a)`, while `tan` uses the mathematically different period `pi/abs(a)`. The non-trigonometric families were analyzed for canonical form and real-domain behavior but do not have a period metric in this experiment.

## Domain-ზე დაკვირვება

Inner undefined set outer result-ებში გადადის. მაგალითად, ცალკე `x/x` smoke experiment canonical inner expression-ად იძლევა `1`-ს და ამავე დროს `x`-ს excluded denominator condition-ად ინარჩუნებს. ეს ხელს უშლის outer function-ს validity restriction-ის წაშლაში მხოლოდ იმიტომ, რომ symbolic simplification-მა უფრო მოკლე string შექმნა.

## ინტერპრეტაცია

ეს ექსპერიმენტი აჩვენებს decomposition-ს, რომელიც მოგვიანებით corpus analysis-ისთვის გამოგვადგება:

```text
grammar -> AST -> canonical algebra -> outer-function semantics -> properties
```

დაკვირვებული 8-form result მხოლოდ ამ token sequence-ს ეკუთვნის. გაზომვის გარეშე მისი სხვა expression family-ებზე განზოგადება არ შეიძლება.

## Evidence-ის კლასიფიკაცია

- რაოდენობები, canonical form-ები, constant collapse-ები და period-ები executable output-იდან **observed** შედეგებია.
- აფინური trigonometric argument-ების period values `2*pi/abs(a)`-ით **symbolically justified** არის.
- Domain და undefined-set propagation implementation contract-ია და tests-ით იფარება.
- ამ ექსპერიმენტიდან performance დასკვნა არ გამოგვაქვს; parsing, symbolic analysis და evaluation cost-ებს ცალკე benchmark-ები სჭირდება.

## Reproduction

```text
.venv\\Scripts\\python.exe -m parseatlas.cli analyze "2*t + 1 - t/2" --outer --format json
```

Report-ის შექმნისას შესრულებული focused validation:

```text
3 passed  # outer-function tests
7 passed  # complete test suite before this experiment report
```


## შესწორება 2026-09-03: NF-2026-00004 (domain slot)

ექსპერიმენტი 0032-ის review-მ bug აღმოაჩინა **სწორედ ამ ექსპერიმენტის code path-ში**,
`src/parseatlas/functions.py`-ის `_property_summary`-ში. ის outer function-ს **raw** parse
tree-ზე აკომპოზირებდა — `to_sympy(parse(source, grammar))` — და მერე იძახებდა
`continuous_domain`-ს, მაშინ როცა იმავე record-ის canonical slot და inner key `simplify(...)`-ს
იყენებდა. შედეგად ორი grammar, რომლებიც **ერთსა და იმავე** function-ს denote-ს აკეთებენ, მაგრამ
სტრუქტურულად განსხვავებულ SymPy tree-ს ტოვებენ, ერთსა და იმავე canonical string-ს და
**განსხვავებულ** domain-ს იღებდნენ. ე.ი. `real_domain` სლოტი parse tree-ის function იყო და არა
denoted value-ის — ზუსტად ის, რისი აღკვეთაც `(F, D, U)` triple discipline-ის მიზანია.

მინიმალური reproducer: `3 * 2 - t / 2 - t`. რვა grammar-ისთვის inner value არის constant `3`;
ოთხი მათგანი ტოვებს tree-ს `(6 - 3*t)/(2 - t)` (გაუქარვებელი removable singularity), ოთხი კი
`Integer(3)`-ს. `log`-ის raw tree-ზე კომპოზიცია პირველ ოთხს აძლევდა
`Union(Interval.open(-oo, 2), Interval.open(2, oo))`-ს, მეორე ოთხს `Reals`-ს. ორივე reading
excluded point `2`-ს ისედაც ატარებდა, ე.ი. validity restriction სადავო არასოდეს ყოფილა —
მხოლოდ ის სლოტი არ თანხმდებოდა, რომელსაც value უნდა აღეწერა.

**Fix.** domain ახლა canonicalised argument-ზე ითვლება (`canonical_argument = simplify(...)`), და
outer function-იც იმავე ერთ argument-ზეა კომპოზირებული. parse tree-ის validity restriction
ცალკე, უცვლელად, `inner_excluded_points`-ში მიდის.

### რა შეიცვალა ამ report-ში: არაფერი

ripple ამ ექსპერიმენტზე გაიზომა და **არც ერთი გამოქვეყნებული რიცხვი არ მოძრაობს**.

გაშვებული შემოწმება: `2*t + 1 - t/2`-ის სრული atlas (`25 grammar × 13 outer function = 325`
result) ორჯერ აიგო — fix-ამდელი და fix-შემდგომი გამოთვლით — და ველ-ველ შედარდა: `inner`,
`canonical`, `inner_excluded_points` და `properties`-ის ყოველი key (`constant_argument`,
`frequency`, `period`, `inner_real_domain`, `real_domain`). განსხვავებული ველი: **0 / 325**.
იგივე შედარება `x/x` smoke case-ზე: **0 / 325**.

მიზეზი სტრუქტურულია და არა შემთხვევითი: founding sequence-ის არც ერთი inner class არ შეიცავს
სტრუქტურულად განსხვავებულ parse tree-ს — თითოეული class-ის ყველა grammar იდენტურ `srepr`-ს
იძლევა — ამიტომ raw და canonicalised argument ამ input-ზე ერთი და იგივეა და bug ვერ ირთვება.
ის სხვა shape-ებზე ირთვება, სადაც removable singularity ერთი reading-ისთვის ქარწყლდება და
მეორისთვის არა.

fix-შემდგომ ხელახლა გაზომილი მაჩვენებლები:

| მაჩვენებელი | გამოქვეყნებული | ხელახლა გაზომილი |
|---|---|---|
| outer-function result | `325` | `325` |
| canonical form თითო family-ზე | `8` | `8` |
| constant-argument grammar | `4` | `4` |
| მათი inner canonical form | `1` | `1` |
| `sin`/`cos` period, `a = 1/2` | `4*pi` | `4*pi` |
| `sin`/`cos` period, `a = 1` | `2*pi` | `2*pi` |
| `sin`/`cos` period, `a = 3/2` | `4*pi/3` | `4*pi/3` |
| `tan` period, `a = 1/2, 1, 3/2` | `2*pi`, `pi`, `2*pi/3` | `2*pi`, `pi`, `2*pi/3` |
| reproduction command output | 13 function, 325 result | 13 function, 325 result |

regression test, რომელიც ამ bug-ს ხელახლა შემოსვლის საშუალებას აღარ აძლევს:
`tests/test_outer_functions.py::test_a_removable_singularity_does_not_move_the_composed_domain`
და `::test_the_domain_slots_are_computed_on_one_shared_canonical_argument`. ამ ფაილში
report-ის შექმნის დროინდელი `3` test-ის ნაცვლად ახლა `5`-ია.

დეტალური falsification, pre/post violation count და შესწორებული claim-ები:
`experiments/0032_outer_quotient/REPORT.md`.
