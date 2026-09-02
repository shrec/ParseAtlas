# ParseAtlas ექსპერიმენტი 0005: coefficient sweep

## მიზანი

ამ ექსპერიმენტში linear template-ის coefficient-ები სისტემურად გაისინჯა, რათა შემოწმებულიყო, რამდენად სტაბილურია semantic class count სხვადასხვა რიცხვითი პარამეტრისთვის.

გამოყენებული template იყო:

```text
a*x + b - c*x/2
```

სადაც:

```text
a, b, c ∈ {-1, 1, 2}
```

უარყოფითი coefficient-ები Generation 1-ის binary-only წესების შესაბამისად ჩაიწერა, მაგალითად `-1` როგორც `(0 - 1)`.

## გაზომვის მეთოდი

თითოეული expression გაანალიზდა `G0 + G01..G24` registry-ზე. თითოეული შემთხვევისთვის ჩაიწერა:

```text
grammar count -> AST form count -> semantic class count
```

Timing ჩაიწერა მხოლოდ როგორც დამხმარე observation და არა როგორც საბოლოო benchmark.

## დაკვირვებული შედეგები

- სულ შემოწმდა `27` expression (`3^3` coefficient combination).
- თითოეულ expression-ზე გაანალიზდა `25` grammar.
- ყველა expression-ზე აღმოჩნდა `17` განსხვავებული AST form.
- semantic class distribution:
  - `6 class`: `9` expression
  - `8 class`: `18` expression

| Semantic class count | Expression count | Corpus share |
|---:|---:|---:|
| 6 | 9 | 33.3% |
| 8 | 18 | 66.7% |

## მთავარი აღმოჩენა

`8 semantic class` არ არის ამ linear template-ის უნივერსალური შედეგი. coefficient sweep-მა აჩვენა, რომ ერთი და იგივე operator/grammar structure-ის ფარგლებში class count იცვლება `6`-დან `8`-მდე.

ამ კონკრეტულ sweep-ში AST diversity უცვლელი დარჩა (`17`), მაშინ როცა semantic class count შეიცვალა. ეს მიუთითებს, რომ AST structure-ის რაოდენობა და semantic equivalence-ის რაოდენობა დამოუკიდებელი metrics-ებია.

`a = 1`-ის მქონე ცხრა expression-მა `6 class` წარმოქმნა; დანარჩენმა თვრამეტმა expression-მა `8 class`. ეს არის დაკვირვებული correlation ამ მცირე corpus-ში და არა დამტკიცებული causal law.

## ინტერპრეტაციის შეზღუდვები

- coefficient set მცირეა და არ მოიცავს `0`-ს ან უფრო დიდ rational values-ს.
- მხოლოდ ერთი linear template შემოწმდა.
- timing არ არის სანდო performance benchmark; ამისთვის საჭიროა warm-up, განმეორებითი გაშვება, median/percentile და გარემოს სრული აღწერა.
- class membership-ის მიზეზის დასამტკიცებლად საჭიროა დამატებითი symbolic feature analysis და უფრო ფართო coefficient sweep.

## Evidence-ის კლასიფიკაცია

- რაოდენობები და distribution-ები executable output-იდან **observed** შედეგებია.
- `6` და `8` class-ის განსხვავება ამ corpus-ის ფარგლებში არის **numerically reproducible**.
- `a = 1`-სა და class count-ს შორის კავშირი ჯერ მხოლოდ **hypothesis**-ია.
- უნივერსალური theorem ან invariant ამ ექსპერიმენტით არ დგინდება.

## Reproduction

```text
.venv\\Scripts\\python.exe -c "from parseatlas.sweep import run_sweep; import json; print(json.dumps(run_sweep(), indent=2))"
```
