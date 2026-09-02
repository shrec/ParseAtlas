# ParseAtlas ექსპერიმენტი 0013: computation cost benchmark

## მიზანი

ამ ფაზაში parsing და symbolic canonicalization ცალ-ცალკე გაიზომა. მიზანია არ აირიოს raw AST construction-ის ფასი canonical symbolic processing-ის ფასთან.

## Input

```text
2*x + 1 - x/2
```

## მეთოდი

- `25` grammar interpretation (`G0 + G01..G24`)
- `5` განმეორებითი გაშვება
- parse stage და canonicalization stage ცალ-ცალკე timed block-ებად
- aggregate metric-ებისთვის median
- raw AST node count და canonical expression string size

## დაკვირვებული შედეგები

| Metric | Median |
|---|---:|
| Grammar count | 25 |
| Raw AST nodes | 9 |
| Canonical expression size | 9 characters |
| Parse time | დაახლოებით `0.00037 s` |
| Canonicalization time | დაახლოებით `0.0753 s` |

ამ გაშვებაში canonicalization parsing-ზე დაახლოებით ორი რიგით ნელი იყო. ეს მიუთითებს, რომ symbolic processing არის ცალკე computational stage და მისი ღირებულება raw parsing cost-თან ერთად არ უნდა დაიმალოს.

## მეთოდოლოგიური შედეგი

გამოვყავით შემდეგი pipeline cost-ები:

```text
raw parsing cost
    -> AST materialization
symbolic canonicalization cost
    -> normalized expression
property extraction cost
    -> roots, domains, periods, invariants
numerical evaluation cost
    -> sample-point validation
```

შემდეგ benchmark-ებში თითოეული stage ცალკე უნდა გაიზომოს.

## შეზღუდვები

- ეს არის ერთი expression-ისა და ერთი runtime environment-ის measurement.
- timings დამოკიდებულია Python/SymPy version-ზე, CPU load-ზე და cache behavior-ზე.
- `5` repetitions მხოლოდ calibration-ისთვის არის საკმარისი; production benchmark-ს მეტი repetition და warm-up სჭირდება.
- canonical expression size operation count-ს ზუსტად არ უდრის.
- ეს შედეგი performance hypothesis-ს აძლიერებს, მაგრამ universal performance law არ არის.

## Evidence-ის კლასიფიკაცია

- node count და expression size **observed structural metrics** არის.
- timings **benchmarked local observations** არის.
- canonicalization-ის relative cost ამ run-ში დაფიქსირებული შედეგია.
- hardware-independent დასკვნა არ კეთდება.

## Reproduction

```text
.venv\\Scripts\\python.exe -c "from parseatlas.benchmark import benchmark_expression; print(benchmark_expression('2*x + 1 - x/2', repetitions=5))"
```
