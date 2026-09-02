# ParseAtlas ექსპერიმენტი 0008: differential equations და probability/statistics

## მიზანი

წინა domain analyzers-ის შემდეგ დაემატა ორი ახალი მიმართულება: პირველი რიგის exponential ODE და Binomial probability distribution. ორივე analyzer იყენებს exact symbolic computation-ს და ამოწმებს არა მხოლოდ ფორმულას, არამედ residual/moment properties-საც.

## Differential equation

გაანალიზდა:

```text
y' = 2*y,  y(0) = 3
```

მიღებული closed-form solution:

```text
y(t) = 3*exp(2*t)
```

Differential equation residual:

```text
y'(t) - 2*y(t) = 0
```

ეს residual executable symbolic check-ით ზუსტად `0` გახდა.

## Probability and statistics

გაანალიზდა Binomial distribution:

```text
X ~ Binomial(4, 1/2)
```

შერჩეული outcome იყო `X=2`.

- PMF: `P(X=2) = 3/8`
- expected value: `E[X] = 2`
- variance: `Var(X) = 1`

გამოყენებული ფორმულებია:

```text
P(X=k) = C(n,k) p^k (1-p)^(n-k)
E[X] = n*p
Var(X) = n*p*(1-p)
```

## მეთოდოლოგიური შედეგი

ამ ფაზამ გააფართოვა property analysis-ის იდეა algebraic canonical form-იდან equation validation-მდე და distribution moments-მდე:

```text
formula -> symbolic object -> derived property -> executable check
```

ODE-სთვის derived property არის residual. Probability-სთვის derived properties არის PMF, expectation და variance.

## შეზღუდვები

- ODE analyzer ამჟამად ფარავს მხოლოდ `y' = k*y` ტიპის exponential equation-ს.
- Probability analyzer ამჟამად ფარავს მხოლოდ Binomial distribution-ს.
- სხვა ODE classes, continuous distributions, confidence intervals და statistical inference ჯერ არ არის დამატებული.
- ეს შედეგები არის კონკრეტული პარამეტრების symbolic observations და არა ყველა differential equation/probability problem-ის სრული გადაწყვეტა.

## Evidence-ის კლასიფიკაცია

- solution, residual, PMF, expectation და variance **symbolically derived** არის.
- residual `0` არის executable symbolic validation.
- distribution formulas-ის სრული generalization ამ ფაზაში არ არის claimed.

## ვალიდაცია

```text
6 passed  # specialized-domain tests
```
