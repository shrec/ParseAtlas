# ParseAtlas ექსპერიმენტი 0003: კვადრატული თვისებები

## შესავალი გამოსახულება

```text
2*x*x + 1 - x/2
```

## კონფიგურაცია

გამოსახულება გაანალიზდა `G0`-სა და `G01..G24`-ზე Generation 1 binary grammar rules-ის, exact rational constants-ის, real domain-ისა და domain-aware semantic grouping-ის გამოყენებით.

## დაკვირვებული შედეგები

აღმასრულებელმა analyzer-მა შექმნა 25 grammar result და 8 semantic class:

| Canonical form | Degree | Grammars |
|---|---:|---|
| `2*x**2 - x/2 + 1` | 2 | G0, G14, G17, G18, G22, G23, G24 |
| `x` | 1 | G01, G02, G07, G08 |
| `x*(x + 1/2)` | 2 | G03 |
| `x*(4*x + 3)/2` | 2 | G04, G06, G20 |
| `x*(x + 2)` | 2 | G05, G19, G21 |
| `x**2 - x/2 + 1/2` | 2 | G09, G13, G15 |
| `2*x**2 - x/2 + 1/2` | 2 | G10, G12, G16 |
| `x*(x + 1)` | 2 | G11 |

Conventional control grammar `G0`-ისთვის analyzer-მა გაზომა:

- degree: `2`
- coefficients: `[2, -1/2, 1]`
- discriminant: `-31/4`
- vertex: `(1/8, 31/32)`
- real roots: none

## ინტერპრეტაცია

ეს ექსპერიმენტი degree-collapse-ის კონკრეტულ observation-ს იძლევა. ოთხი strict grammar იგივე token sequence-ს linear function `x`-ად reinterpret-ირებს, დანარჩენი class-ები კი quadratic-ია. ეს observation მხოლოდ ამ expression-ს ეკუთვნის და operator precedence-სა და polynomial degree-ს შორის ზოგად კავშირს არ ამტკიცებს.

ექსპერიმენტი ასევე აჩვენებს, რატომ უნდა გამოაჩინოს canonical-form analysis-მა structural properties და მხოლოდ დაბეჭდილი expression-ები არ შეადაროს. Degree, factorization, roots, discriminant და extrema grammar interpretation-ებს შორის ერთმანეთისგან დამოუკიდებლად შეიძლება შეიცვალოს.

## Evidence-ის კლასიფიკაცია

- Class membership და degree counts executable output-იდან **observed** შედეგებია.
- Discriminant, vertex და critical-point values canonical polynomial-იდან **symbolically derived** არის.
- `G0`-ისთვის real roots-ის არქონა მისი უარყოფითი discriminant-იდან გამომდინარეობს და **symbolically justified** არის.
- Cross-family invariant არ ცხადდება.

## Reproduction

```text
.venv\\Scripts\\python.exe -m parseatlas.cli analyze "2*x*x + 1 - x/2" --format json
```
