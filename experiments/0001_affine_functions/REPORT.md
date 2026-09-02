# ParseAtlas ექსპერიმენტი 0001: აფინური ფუნქციები

## შესავალი გამოსახულება

```text
2*t + 1 - t/2
```

## კონფიგურაცია

- `G0`: conventional control grammar, with `*` and `/` sharing the higher level and `+` and `-` sharing the lower level.
- `G01..G24`: all strict precedence permutations, listed highest to lowest.
- Binary operators only.
- Left-to-right associativity at equal precedence.
- Real domain with exact rational constants.
- Custom parser creates the AST before symbolic conversion.
- Equivalence includes canonical function, domain, and undefined set.

## Observed Result

აღმასრულებელმა analyzer-მა 25 grammar result და 8 semantic equivalence class შექმნა. Strict grammar-ების დაჯგუფება ზუსტად იმეორებს თავდაპირველ `24 -> 8` finding-ს.

| Class | Canonical | Domain | Undefined | Grammars |
|---|---|---|---|---|
| C01 | `3*t/2 + 1` | `R` | none | G0, G14, G17, G18, G22, G23, G24 |
| C02 | `1` | `R` | none | G01, G02, G07, G08 |
| C03 | `t/2 + 1` | `R` | none | G03 |
| C04 | `3*t/2 + 2` | `R` | none | G04, G06, G20 |
| C05 | `t + 2` | `R` | none | G05, G19, G21 |
| C06 | `t/2 + 1/2` | `R` | none | G09, G13, G15 |
| C07 | `3*t/2 + 1/2` | `R` | none | G10, G12, G16 |
| C08 | `t + 1` | `R` | none | G11 |

## ინტერპრეტაცია

ეს შედეგი მხოლოდ ამ token sequence-ის observation-ია. ის არ ამტკიცებს, რომ აფინური გამოსახულებებისთვის ყოველთვის რვა class მიიღება.

ამ input-ზე conventional control grammar `G0` იზიარებს `3*t/2 + 1` class-ს. მისი control სტატუსი strict permutation ID-ებისგან მაინც განსხვავებულია და CLI მას ცალკე report-ში აჩვენებს.

analyzer undefined metadata-ს canonical expression-ისგან ცალკე ინახავს. მაგალითად, `x/x` ტექსტურად მარტივდება `1`-მდე, მაგრამ `x`-ს denominator-ის გამორიცხულ პირობად აფიქსირებს; ამიტომ ის unrestricted `1`-თან ერთ class-ში არ ერთიანდება.

## ვალიდაცია

```text
7 passed
```

Command used:

```text
.venv\\Scripts\\python.exe -m parseatlas.cli analyze "2*t + 1 - t/2" --format markdown
```
