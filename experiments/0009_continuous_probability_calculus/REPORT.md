# ParseAtlas ექსპერიმენტი 0009: continuous probability და გაფართოებული calculus

## მიზანი

ამ ეტაპზე probability/statistics analyzer გაფართოვდა continuous distribution-ებზე, ხოლო calculus analyzer-ს დაემატა limit, definite integral, Taylor series და extrema candidate analysis.

## Normal distribution

გაანალიზდა:

```text
X ~ Normal(0, 1)
point = 0
```

მიღებული შედეგები:

- z-score: `0`
- expected value: `0`
- variance: `1`
- PDF: `1/sqrt(2*pi)`

## Exponential distribution

გაანალიზდა:

```text
X ~ Exponential(2)
point = 1
```

მიღებული შედეგები:

- PDF: `2*exp(-2)`
- survival function: `exp(-2)`
- expected value: `1/2`
- variance: `1/4`

გამოყენებული ფორმულებია:

```text
f(x) = lambda*exp(-lambda*x)
S(x) = exp(-lambda*x)
E[X] = 1/lambda
Var(X) = 1/lambda**2
```

## გაფართოებული calculus

გაანალიზდა:

```text
f(x) = x**2
```

მიღებული შედეგები:

- limit at `+infinity`: `oo`
- definite integral from `0` to `1`: `1/3`
- Taylor polynomial at `0`, order `4`: `x**2`
- critical point: `0`
- critical value: `0`

## მეთოდოლოგიური შედეგი

ამ ფაზამ დაამატა continuous probability-ის density/survival/moment layer და calculus-ის მრავალმხრივი property extraction:

```text
formula -> symbolic derivation -> property -> exact validation
```

## შეზღუდვები

- Normal analyzer ჯერ არ ითვლის CDF-ს ან confidence interval-ს.
- Exponential analyzer არ ფარავს mixture/discrete censoring შემთხვევებს.
- calculus analyzer ჯერ არ აფასებს ყველა global extrema-ს ან მრავალცვლადიან ფუნქციებს.
- Taylor series-ის order და expansion point user-ის მიერ უნდა განისაზღვროს.

## Evidence-ის კლასიფიკაცია

- PDF, survival, expectation და variance **symbolically derived** არის.
- limit, integral, Taylor და critical-point შედეგები executable symbolic analysis-ით არის მიღებული.
- სტატისტიკური inference ან empirical confidence claim ამ ექსპერიმენტში არ კეთდება.

## ვალიდაცია

```text
8 passed  # domain-analysis tests
```
