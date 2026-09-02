# ParseAtlas ექსპერიმენტი 0015: domain-aware invariant mining

## მიზანი

წინა identity miner მხოლოდ symbolic residual-ს ამოწმებდა. ამ ფაზაში დაემატა original domain restriction-ების შედარება და sampled counterexample detection.

## მთავარი შესწორება

`x/x` და `1`-ისთვის symbolic residual არის:

```text
x/x - 1 = 0
```

მაგრამ მარცხენა მხარე `x=0`-ზე undefined არის. ამიტომ miner ახლა აფიქსირებს:

- residual: `0`
- left restriction: `0`
- right restriction: none
- domain_equal: `False`
- is_identity: `False`

ამით canonical cancellation აღარ აქრობს საწყის validity restriction-ს.

## Calibration identities

შემოწმდა ოთხი ცნობილი identity:

```text
(x + 1)**2 = x**2 + 2*x + 1
(x - 1)*(x + 1) = x**2 - 1
sin(x)**2 + cos(x)**2 = 1
(x + 2)**3 = x**3 + 6*x**2 + 12*x + 8
```

ოთხივე შემთხვევაში:

- residual: `0`
- domain_equal: `True`
- is_identity: `True`

## Counterexample detection

არაიდენტობისთვის:

```text
x**2 = x + 1
```

sample points `{-2, -1, 0, 1, 2}`-ზე განსხვავება ფიქსირდება და `is_identity=False` ბრუნდება.

ეს sampled counterexample მხოლოდ false claim-ს უარყოფს; identity-ის დასამტკიცებლად symbolic residual და domain equality კვლავ საჭიროა.

## მეთოდოლოგიური შედეგი

Identity validation ახლა ასეთია:

```text
unsimplified parse
    -> symbolic residual
    -> original restrictions
    -> domain comparison
    -> optional counterexample sampling
    -> identity decision
```

ეს უფრო მკაცრი მიდგომაა, ვიდრე მხოლოდ canonical text equality ან residual `0`.

## შეზღუდვები

- domain extraction ამჟამად rational denominator restrictions-ზეა ორიენტირებული.
- branch cuts და complex domains შემდეგ ეტაპზე უნდა დაემატოს.
- sampled counterexamples proof-ს არ ცვლის.
- მრავალცვლადიანი domain analysis ჯერ შეზღუდულია.

## Evidence-ის კლასიფიკაცია

- residuals და restrictions **symbolically derived** არის.
- counterexamples **numerically observed** არის.
- `x/x` rejection არის **domain-aware semantic validation**.

## ვალიდაცია

```text
42 passed
```
