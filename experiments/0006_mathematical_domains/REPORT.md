# ParseAtlas ექსპერიმენტი 0006: მათემატიკური დომენების გაფართოება

## მიზანი

ParseAtlas-ის კვლევა გაფართოვდა მხოლოდ operator-precedence expression-ებიდან უფრო ფართო მათემატიკურ დომენებზე. შეიქმნა deterministic formula catalog, რომელიც სხვადასხვა საგნობრივ მიმართულებას თანაბრად ფარავს.

## დომენები

| მიმართულება | ფორმულების რაოდენობა |
|---|---:|
| quadratic equations | 125 |
| geometry | 125 |
| algebra | 125 |
| calculus | 125 |
| trigonometry | 125 |
| differential equations | 125 |
| probability and statistics | 125 |
| number theory | 125 |
| **სულ** | **1,000** |

ფორმულები გენერირებულია deterministic parameterization-ით. მაგალითად:

- quadratic equations: `n*x**2 + (n+1)*x + (n+2) = 0`
- geometry: triangle area და rectangle perimeter templates
- algebra: `(x+n)*(x-n)`
- calculus: power-rule derivative templates
- trigonometry: `sin(n*x)**2 + cos(n*x)**2 = 1`
- differential equations: `y' = n*y`
- probability/statistics: expectation და variance specifications
- number theory: `gcd(x,n)`

## ცალკე 10,000-function catalog

პარამეტრიზებული function catalog კვლავ ცალკე ინარჩუნებს `10,000` ფუნქციას:

```text
10 families * 1,000 parameterized functions = 10,000 functions
```

ამ კატალოგის სრული grammar run იძლევა:

```text
10,000 functions * 25 grammars = 250,000 interpretations
```

პირველი სრული გაშვება computationally heavy აღმოჩნდა, რადგან თითოეულ interpretation-ზე general symbolic simplification გამოიყენებოდა. ამიტომ კვლევის მეთოდოლოგიაში შევიტანეთ ორი რეჟიმი:

1. **structural catalog mode** — დიდი რაოდენობის ფუნქციების სწრაფი, deterministic enumeration და aggregate metrics;
2. **symbolic validation mode** — შერჩეულ sample-ებსა და exceptional cases-ზე სრული SymPy simplification/property analysis.

ეს ხელს უშლის 250,000-result ექსპერიმენტის ერთდროულად მძიმე და არაინფორმაციულ გაშვებად ქცევას.

## კვლევითი ინტერპრეტაცია

ამ ეტაპზე დადასტურებულია, რომ ParseAtlas-ის კვლევის სივრცე შეიძლება გაიზარდოს რამდენიმე დამოუკიდებელი ღერძით:

```text
grammar
* expression family
* coefficient parameters
* mathematical domain
* outer function
* symbolic property extractor
* numerical method
* computational cost model
```

ამ catalog-ის existence არ ნიშნავს, რომ 1,000 ფორმულის ყველა თეორემა უკვე დამტკიცებულია. ეს არის reproducible experiment registry და არა ავტომატურად დამტკიცებული mathematical truth set.

## შემდეგი ეტაპი

შემდეგ ეტაპზე domain-ების მიხედვით უნდა დაემატოს სპეციალიზებული analyzers:

- quadratic roots, discriminant და vertex;
- geometry distance, area, angle და symmetry;
- algebra factorization, identities და polynomial invariants;
- calculus derivative, integral, limit და extrema;
- differential-equation solution families;
- probability moments and distributions;
- number-theory divisibility and modular properties.

## Evidence-ის კლასიფიკაცია

- catalog counts და domain balance არის **observed** და test-ებით დადასტურებული.
- 10,000-function decomposition არის **structurally verified**.
- ყველა ფორმულის სრული symbolic theorem-level interpretation ამ ეტაპზე არ არის claimed.
- heavy full-run observation აჩვენებს საჭიროებას structural mode-სა და symbolic validation mode-ის გამიჯვნისთვის; ეს არის methodological finding და არა performance benchmark.

## ვალიდაცია

```text
2 passed  # mathematical domain catalog tests
```
