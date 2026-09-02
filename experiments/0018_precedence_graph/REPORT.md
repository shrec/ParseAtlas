# ParseAtlas ექსპერიმენტი 0018: precedence permutation graph

## მიზანი

ამ ფაზაში `G01..G24` strict precedence grammars permutation graph-ად წარმოვადგინეთ. თითო node არის ერთი strict ordering, ხოლო edge აერთებს grammars-ს, რომლებიც ერთ adjacent precedence swap-ით განსხვავდებიან.

## Graph structure

- nodes: `24`
- edges: `36`
- თითო edge-ზე ინახება swap position და semantic-change rate.

`36` edge მიიღება ოთხი operator-ის permutation graph-ისთვის:

```text
24 permutations * 3 adjacent positions / 2 = 36 unique edges
```

## Corpus

შემოწმდა:

```text
2*t + 1 - t/2
(x + 1)/(x - 2)
2*x*x + 1 - x/2
```

## დაკვირვებული შედეგები

- strict grammar node count: `24`
- adjacent-swap edge count: `36`
- semantic-change edge count: `18`
- semantic-stable edge count: `18`

Edge semantic change ნიშნავს, რომ ორივე grammar ერთსა და იმავე corpus expression-ზე ერთ semantic class-ში არ მოხვდა.

## ინტერპრეტაცია

Graph აჩვენებს, რომ precedence-space მხოლოდ unordered list არ არის. Adjacent swap ზოგ expression-ზე იწვევს semantic transition-ს, ზოგზე კი შედეგი უცვლელი რჩება.

```text
grammar node -> adjacent swap -> semantic transition
```

Rational rigid expression `(x + 1)/(x - 2)` თითქმის სრულად სტაბილურია ამ comparison-ში, ხოლო affine და quadratic expressions graph transitions-ზე რეაგირებენ.

შემდეგი ნაბიჯია edge-ებზე degree, roots, domain, poles და operation cost-ის ცვლილების დამატება.

## შეზღუდვები

- corpus მხოლოდ სამი expression-ისგან შედგება.
- graph strict grammars-ზეა; `G0` control ცალკე რჩება.
- edge change ამჟამად semantic class change-ს ზომავს და არა ცვლილების magnitude-ს.
- graph clustering და shortest-path simplification ჯერ არ არის დამატებული.

## Evidence-ის კლასიფიკაცია

- node/edge count და changed-edge count executable **observations** არის.
- grammar-space transition landscape არის მიმდინარე corpus-ზე დაფიქსირებული სტრუქტურა.
- ზოგადი graph law ან universal clustering pattern ჯერ არ არის claimed.

## ვალიდაცია

```text
50 passed
```
