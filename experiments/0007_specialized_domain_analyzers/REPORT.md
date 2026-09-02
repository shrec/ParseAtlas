# ParseAtlas ექსპერიმენტი 0007: სპეციალიზებული domain analyzers

## მიზანი

კვლევის შემდეგ ეტაპზე საერთო grammar analyzer-ს დაემატა სპეციალიზებული მათემატიკური property extractors. მიზანია ერთი და იგივე კვლევითი pipeline-ის შიგნით სხვადასხვა დომენის შესაბამისი თვისებები გაიზომოს.

## განხორციელებული მიმართულებები

| დომენი | გაზომილი თვისებები |
|---|---|
| quadratic equations | discriminant, roots, root count, vertex |
| geometry | triangle area, distance, midpoint |
| algebra | expansion, factorization, simplification, zeros |
| calculus | derivative, integral, limit, critical points |
| trigonometry | identity simplification, derivative, inverse check |
| number theory | primality, factorization, gcd, lcm |

## დაკვირვებული მაგალითები

### Quadratic equations

```text
x**2 - 3*x + 2 = 0
```

მიღებული შედეგებია:

- discriminant: `1`
- roots: `1`, `2`
- vertex: `(3/2, -1/4)`

### Geometry

სამკუთხედისთვის `base=6`, `height=4`:

- area: `12`
- points `(0,0)` და `(3,4)`-ის distance: `5`
- midpoint: `(3/2, 2)`

### Algebra

```text
x**2 - 1
```

factorization:

```text
(x - 1)*(x + 1)
```

### Calculus

```text
f(x) = x**2
```

- derivative: `2*x`
- integral: `x**3/3`
- critical point: `0`

### Trigonometry

```text
sin(x)**2 + cos(x)**2 = 1
```

identity symbolic simplification-ით `1`-მდე დაიყვანება.

### Number theory

`60`-ისთვის:

- prime: `False`
- factorization: `2**2 * 3 * 5`
- gcd with `12`: `12`
- lcm with `12`: `60`

## მეთოდოლოგიური შედეგი

დადასტურდა, რომ ParseAtlas-ის ზოგადი grammar/AST layer შეიძლება გაფართოვდეს domain-specific analyzers-ით ისე, რომ parsing და symbolic interpretation ცალკე დარჩეს.

```text
grammar -> AST -> canonical form -> domain-specific properties
```

ეს extractors ჯერ calibration/reference analyzers-ია. ისინი არ წარმოადგენენ ყველა დომენის სრულ theorem prover-ს.

## შეზღუდვები

- geometry analyzer ამჟამად იყენებს მხოლოდ area, distance და midpoint-ს.
- calculus analyzer ჯერ არ ფარავს მრავალცვლადიან ანალიზს, series-ს ან differential equations-ს.
- number theory analyzer integer input-ზეა შეზღუდული.
- trigonometry analyzer მცირე identity set-ს ამოწმებს.
- symbolic output-ის სრული correctness უნდა გაგრძელდეს adversarial და numerical validation-ით.

## Evidence-ის კლასიფიკაცია

- მაგალითების შედეგები executable output-იდან **observed** არის.
- derivative, integral, factorization და quadratic properties **symbolically derived** არის.
- დომენების სრული მათემატიკური დაფარვა ჯერ არ არის claimed.

## ვალიდაცია

```text
25 passed
```
