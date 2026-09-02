# ParseAtlas ექსპერიმენტი 0017: grammar equivalence matrix

## მიზანი

ამ ფაზაში ცალკეული expression-ის ანალიზიდან გადავედით თვითონ grammar-space-ის სტრუქტურის გაზომვაზე. შეიქმნა `25 x 25` pairwise matrix, სადაც თითოეული უჯრა აჩვენებს, რამდენი corpus expression-ის შემთხვევაში მოხვდნენ ორი grammar ერთ semantic class-ში.

## Metric

Representation sensitivity განისაზღვრა strict grammar-ებისთვის ასე:

```text
S(E) = (# semantic classes - 1) / 23
```

`S(E)=0` ნიშნავს, რომ ყველა strict grammar ერთ semantic class-შია, ხოლო მაღალი მნიშვნელობა ნიშნავს მეტ grammar-sensitive behavior-ს.

## Corpus

შემოწმდა ხუთი controlled expression:

```text
2*t + 1 - t/2
3*x + 2 - x/3
2*x*x + 1 - x/2
(x + 1)/(x - 2)
(x*x - 1)/(x - 1)
```

## დაკვირვებული შედეგები

- matrix ზომა: `25 x 25`
- expression count: `5`
- mean representation sensitivity: `0.1913`
- `G0` და `G01` agreement: `0.2`
- `G0` და `G03` agreement: `0.4`
- matrix diagonal-ის ყველა მნიშვნელობა `1.0`-ია.

Rational rigid expression-ები grammar agreement-ს ზრდის, ხოლო affine/polynomial expression-ები grammar-sensitive variation-ს აჩენს.

## ინტერპრეტაცია

ორი ახალი ცნება გამოიკვეთა:

```text
grammar-sensitive expression
სადაც semantic class count მაღალია

grammar-rigid expression
სადაც grammar-ების უმეტესობა ერთ semantic class-ში რჩება
```

ეს classification ჯერ corpus-relative არის. `S(E)` არ არის უნივერსალური complexity measure; ის მხოლოდ მოცემულ grammar registry-სა და semantic contract-ში sensitivity-ს აჯამებს.

Matrix მომავალში გამოიყენება grammar signatures-ისთვის:

```text
V_i = (M_i1, M_i2, ..., M_i25)
```

ამის შემდეგ შესაძლებელი იქნება grammar clustering, adjacent-swap sensitivity და precedence-space graph analysis.

## შეზღუდვები

- corpus მცირეა და controlled არის.
- matrix agreement semantic class-ის equality-ს ზომავს, არა structural AST equality-ს.
- `G0`-ის ჩათვლა matrix-ში control-vs-strict comparison-ს იძლევა, მაგრამ strict-only analysis ცალკე უნდა დარჩეს.
- matrix probability corpus-dependent არის და universal probability-ს არ წარმოადგენს.

## Evidence-ის კლასიფიკაცია

- matrix values და sensitivity scores executable **observations** არის.
- diagonal `1.0` structural self-equivalence-ით აიხსნება.
- grammar clustering და stable signatures ჯერ **research hypotheses**-ია.

## ვალიდაცია

```text
48 passed
```
