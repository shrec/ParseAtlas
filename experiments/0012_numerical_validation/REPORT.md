# ParseAtlas ექსპერიმენტი 0012: numerical validation

## მიზანი

ამ ფაზაში symbolic canonicalization-ის შედეგები დამოუკიდებლად გადამოწმდა რეალურ sample point-ებზე. Validator ერთმანეთს ადარებს custom AST-დან მიღებულ raw symbolic expression-სა და canonical simplified expression-ს.

## Affine baseline

```text
2*x + 1 - x/2
```

შემოწმდა `5` sample point თითოეულ `25` grammar-ზე:

```text
x ∈ {-2, -1, 0, 1, 2}
```

სულ შესრულდა:

```text
25 * 5 = 125 comparisons
```

მიღებული შედეგი:

- checked: `125`
- skipped: `0`
- mismatches: `0`
- all_match: `True`

## Rational pole

```text
(x + 1)/(x - 2)
```

sample point `x=2`-ზე validator singular evaluation-ს არ ადარებს და მას skipped case-ად აფიქსირებს. სხვა sample point-ებზე raw და canonical values ერთმანეთს ემთხვევა.

## მეთოდოლოგიური შედეგი

Numerical validation სასარგებლოა როგორც symbolic analysis-ის independent sanity check, მაგრამ არ ცვლის symbolic proof-ს. რამდენიმე sample point-ზე equality არ ამტკიცებს ფუნქციების ზოგად equivalence-ს.

```text
symbolic result -> safe sample points -> numerical comparison -> mismatch report
```

## შეზღუდვები

- sample points წინასწარ არის განსაზღვრული და არა random/adversarial.
- floating-point comparison გამოიყენება მხოლოდ validation-ისთვის.
- singularities-ის სრული domain decomposition ცალკე ეტაპია.
- numerical agreement theorem-level proof-ს არ წარმოადგენს.

## Evidence-ის კლასიფიკაცია

- baseline comparisons არის **numerically validated**.
- rational pole skip არის **domain-aware validation behavior**.
- ზოგადი equivalence კვლავ symbolic/domain contract-ზეა დამოკიდებული.

## ვალიდაცია

```text
2 passed  # numerical validation tests
```
