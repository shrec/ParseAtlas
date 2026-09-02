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
