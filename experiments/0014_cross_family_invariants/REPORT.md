# ParseAtlas ექსპერიმენტი 0014: cross-family benchmark და invariant mining

## მიზანი

ამ ფაზაში parsing/canonicalization cost სხვადასხვა expression family-ზე შედარდა და რამდენიმე ცნობილ algebraic/trigonometric identity-ზე symbolic residual mining ჩატარდა.

## Cross-family benchmark

შემოწმდა ოთხი expression:

| Family | Expression |
|---|---|
| affine | `2*x + 1 - x/2` |
| quadratic | `2*x*x + 1 - x/2` |
| rational | `(x + 1)/(x - 2)` |
| nested | `2*(x + 1) - x/2` |

თითოეულზე გამოყენებული იყო `25` grammar და `5` repetition. Median results:

| Family | Raw AST nodes | Canonical size | Parse median (s) | Canonicalization median (s) | Ratio |
|---|---:|---:|---:|---:|---:|
| affine | 9 | 9 | 0.00042 | 0.07037 | 166.16x |
| quadratic | 11 | 16 | 0.00048 | 0.13303 | 277.44x |
| rational | 7 | 15 | 0.00042 | 0.14920 | 359.08x |
| nested | 9 | 7 | 0.00040 | 0.05142 | 129.61x |

## დაკვირვება

ოთხივე family-ზე canonicalization parse stage-ზე მნიშვნელოვნად მძიმე აღმოჩნდა. rational expression-ს ამ მცირე benchmark-ში ყველაზე მაღალი relative ratio ჰქონდა.

ეს არის consistent local observation, მაგრამ არა hardware-independent performance law. უფრო სანდო benchmark-ისთვის საჭიროა მეტი repetition, warm-up, controlled CPU load, version manifest და statistical intervals.

## Identity mining

შემოწმდა ოთხი identity:

```text
(x + 1)**2 = x**2 + 2*x + 1
(x - 1)*(x + 1) = x**2 - 1
sin(x)**2 + cos(x)**2 = 1
(x + 2)**3 = x**3 + 6*x**2 + 12*x + 8
```

ოთხივე identity-ს residual symbolic simplification-ით `0` ჰქონდა.

```text
identity_count = 4
valid_count = 4
```

## მეთოდოლოგიური შედეგი

ამ ფაზამ ორი დამოუკიდებელი მიმართულება გააერთიანა:

```text
expression family -> stage cost comparison
identity corpus -> symbolic residual -> invariant candidate
```

Identity miner ამჟამად calibration tool-ია. ის იპოვის მხოლოდ წინასწარ მიწოდებულ candidate identities-ს; ავტომატური conjecture generation და proof search შემდეგი ეტაპია.

## Evidence-ის კლასიფიკაცია

- benchmark timings არის **local benchmark observations**.
- identity residual `0` არის **symbolically validated**.
- cross-family performance generalization არ არის claimed.
- ოთხი identity-ის არსებობა არ ნიშნავს, რომ მათი ყველა domain restriction ავტომატურად შემოწმებულია.

## ვალიდაცია

```text
2 passed  # cross-family benchmark and identity-mining tests
```
