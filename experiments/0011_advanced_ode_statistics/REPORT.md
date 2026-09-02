# ParseAtlas ექსპერიმენტი 0011: advanced ODE და statistics inference

## მიზანი

ამ ფაზაში differential-equation analyzer გაფართოვდა nonlinear და second-order მაგალითებით, ხოლო probability/statistics layer-ს დაემატა Normal CDF, known-sigma confidence interval და sample statistics.

## Logistic ODE

გაანალიზდა:

```text
y' = y*(1-y/10), y(0)=2
```

closed-form solution-ისთვის symbolic residual:

```text
y' - y*(1-y/10) = 0
```

მიღებული residual ზუსტად `0` არის.

## Harmonic oscillator

გაანალიზდა:

```text
y'' + 2**2*y = 0
```

solution:

```text
y(t) = 3*cos(2*t)
```

residual:

```text
y'' + 4*y = 0
```

მიღებული residual არის `0`.

## Normal CDF

`Normal(0,1)` distribution-ისთვის `x=0`-ზე:

- z-score: `0`
- CDF: `1/2`

## Confidence interval

known-sigma z interval-ისთვის:

```text
sample mean = 10
sigma = 2
n = 4
z = 1.96
```

margin არის `49/25`, ხოლო interval:

```text
[201/25, 299/25]
```

რიცხვები exact Rational-ად ინახება და float rounding არ გამოიყენება.

## Sample statistics

sample:

```text
(1, 2, 3, 4)
```

მიღებული შედეგებია:

- mean: `5/2`
- unbiased sample variance: `5/3`
- sample standard deviation: `sqrt(15)/3`

## მეთოდოლოგიური შედეგი

ამ ფაზამ გააერთიანა equation residual validation და statistical estimation metadata:

```text
model -> symbolic solution/property -> residual or estimator -> exact check
```

## შეზღუდვები

- Logistic და harmonic analyzers მხოლოდ კონკრეტულ closed-form families-ს ფარავს.
- Confidence interval analyzer known-sigma z-method-ს იყენებს; unknown-sigma t-interval ჯერ არ არის დამატებული.
- Normal CDF symbolic `erf`-ზეა დაფუძნებული და numerical tail validation ცალკე ეტაპია.
- Statistical inference causal ან empirical claim-ებს არ აკეთებს.

## Evidence-ის კლასიფიკაცია

- ODE solutions და residuals **symbolically derived and validated** არის.
- CDF, confidence interval და sample moments **exact symbolic computations** არის.
- შედეგები კონკრეტულ მოდელებსა და პარამეტრებზეა მიბმული და ზოგად theorem-ებად არ ცხადდება.

## ვალიდაცია

```text
35 passed
```
