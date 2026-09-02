# ParseAtlas ექსპერიმენტი 0004: კონტროლირებადი corpus

## მიზანი

ამ ეტაპზე შემთხვევითი expression-ების გენერირების ნაცვლად გამოვიყენეთ წინასწარ განსაზღვრული, მცირე controlled corpus. მიზანია გავზომოთ:

```text
grammar count -> AST form count -> semantic class count
```

ასევე ვაკვირდებით polynomial degree-სა და rational pole-ებს.

## Corpus

| ID | Expression | Family |
|---|---|---|
| `linear_01` | `2*t + 1 - t/2` | linear |
| `linear_02` | `3*x + 2 - x/3` | linear |
| `polynomial_01` | `2*x*x + 1 - x/2` | polynomial |
| `polynomial_02` | `x*x*x + 2*x*x - x + 1` | polynomial |
| `rational_01` | `(x + 1)/(x - 2)` | rational |
| `rational_02` | `(x*x - 1)/(x - 1)` | rational with removable restriction |

## დაკვირვებული შედეგები

| ID | Grammars | AST forms | Semantic classes | Degrees | Poles |
|---|---:|---:|---:|---|---|
| `linear_01` | 25 | 14 | 8 | `1` | none |
| `linear_02` | 25 | 14 | 8 | `1` | none |
| `polynomial_01` | 25 | 14 | 8 | `1, 2` | none |
| `polynomial_02` | 25 | 7 | 6 | `3, 4, 5` | none |
| `rational_01` | 25 | 1 | 1 | n/a | `2` |
| `rational_02` | 25 | 2 | 2 | `1` | none |

## მთავარი აღმოჩენები

1. **Class count expression family-ზეა დამოკიდებული.** პირველ affine მაგალითში მივიღეთ `8` class, მაგრამ cubic-looking expression-ზე მივიღეთ `6` class.
2. **Polynomial degree შეიძლება შეიცვალოს.** `polynomial_01`-ში degree `1`-დან `2`-მდე იცვლება, ხოლო `polynomial_02`-ში გაზომილი degree-ები `3, 4, 5`-ია.
3. **Rational ფორმები ზოგჯერ სტაბილურია.** `(x + 1)/(x - 2)`-ზე ყველა grammar ერთ semantic class-ში დარჩა და pole `x=2` შეინარჩუნა.
4. **Removable restriction ცალკე metadata-დ რჩება.** `(x*x - 1)/(x - 1)` cancellation-ის შემდეგ linear ფორმად გადადის, მაგრამ `x=1`-ზე თავდაპირველი restriction არ იკარგება.

## ინტერპრეტაციის სიფრთხილე

ეს არის მხოლოდ ექვსი კონტროლირებადი expression-ის observation. ამ მონაცემებიდან არ გამომდინარეობს უნივერსალური კანონი, რომ კონკრეტული family ყოველთვის კონკრეტულ რაოდენობის class-ს ან degree-ს შექმნის.

შემდეგი corpus გაფართოება უნდა შეიცავდეს coefficient-ების სისტემურ sweep-ს, expression depth-ის კონტროლს და უფრო მკაცრ rational-domain analysis-ს.

## ვალიდაცია

ამ ანგარიშის შექმნისას:

```text
16 passed
```

რეპროდუცირებისთვის:

```text
.venv\\Scripts\\python.exe -c "from parseatlas.corpus import run_corpus; import json; print(json.dumps(run_corpus(), indent=2))"
```
