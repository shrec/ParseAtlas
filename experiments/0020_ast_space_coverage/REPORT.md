# ParseAtlas ექსპერიმენტი 0020: precedence-reachable fraction of the AST space

## მიზანი

ROADMAP Phase 9-ის ღია კითხვა იყო: სრული parenthesization space-იდან რა წილს ფარავს global precedence rule და რომელი AST-ები რჩება precedence-ით მიუწვდომელი. ამ ექსპერიმენტში ფიქსირებული leaf და operator თანმიმდევრობისთვის სრულად ჩამოვთვალეთ ყველა binary tree და შევადარეთ იმ trees-ს, რომლებსაც grammar registry (`G01..G24` strict და `G0` control) რეალურად აწარმოებს.

## Space structure

ფიქსირებული left-to-right leaf და operator თანმიმდევრობისთვის valid trees-ის რაოდენობა Catalan number `C(k)`-ია, სადაც `k` არის operator count:

```text
C(2)=2  C(3)=5  C(4)=14  C(5)=42  C(6)=132
```

`enumerate_parenthesizations` სწორედ ამ Catalan რეკურსიას ატარებს: split თითო operator position-ზე. მიღებული forms hashable tuples-ია `(op, left, right)` სახით, plain string leaves-ით, ხოლო `parseatlas.canonical.ast_to_dict`-ის output იმავე form-ში გადაიყვანება, ასე რომ enumeration და parsing ერთსა და იმავე სივრცეში იზომება.

მთავარი სტრუქტურული შეზღუდვა: registry შეიცავს `24` strict grammar-ს და `1` control grammar-ს, ესე იგი ერთი source-ისთვის reachable distinct trees ვერასდროს გადააჭარბებს `25`-ს, `C(k)` კი `k`-სთან ერთად სწრაფად იზრდება.

## Corpus

per-expression ცხრილისთვის შემოწმდა:

```text
a + b*c
a + b + c
2*t + 1 - t/2
a + b*c - d/e
a - b*c + d/e - f
2*x*x + 1 - x/2 + x
```

operator pattern sweep-ისთვის `k = 2..6` დიაპაზონში ჩამოთვლილია ყველა `4**k` operator sequence `(+ - * /)` alphabet-ზე, canonical leaf თანმიმდევრობით `a, b, c, ...`.

## დაკვირვებული შედეგები

per-expression coverage:

| expression | leaves | operators | catalan_total | strict_reachable | all_reachable | strict_coverage | all_coverage | control_only_trees |
|---|---|---|---|---|---|---|---|---|
| `a + b*c` | 3 | 2 | 2 | 2 | 2 | 1.0 | 1.0 | 0 |
| `a + b + c` | 3 | 2 | 2 | 1 | 1 | 0.5 | 0.5 | 0 |
| `2*t + 1 - t/2` | 5 | 4 | 14 | 14 | 14 | 1.0 | 1.0 | 0 |
| `a + b*c - d/e` | 5 | 4 | 14 | 14 | 14 | 1.0 | 1.0 | 0 |
| `a - b*c + d/e - f` | 6 | 5 | 42 | 19 | 20 | 0.4524 | 0.4762 | 1 |
| `2*x*x + 1 - x/2 + x` | 7 | 6 | 132 | 17 | 18 | 0.1288 | 0.1364 | 1 |

- `expression_count`: `6`
- `mean_strict_coverage`: `0.6801948051948052`
- `mean_all_coverage`: `0.6854256854256855`

operator pattern sweep, `k = 2..6`:

| k | catalan_total | pattern_count | mean_coverage | min_coverage | max_coverage | full_coverage_fraction |
|---|---|---|---|---|---|---|
| 2 | 2 | 16 | 0.875 | 0.5 | 1.0 | 0.75 |
| 3 | 5 | 64 | 0.625 | 0.2 | 1.0 | 0.375 |
| 4 | 14 | 256 | 0.36049107142857145 | 0.07142857142857142 | 1.0 | 0.09375 |
| 5 | 42 | 1024 | 0.1734561011904762 | 0.023809523809523808 | 0.47619047619047616 | 0.0 |
| 6 | 132 | 4096 | 0.07222863399621213 | 0.007575757575757576 | 0.16666666666666666 | 0.0 |

strict-only mean იმავე sweep-იდან: `k=2` -> `0.875`, `k=3` -> `0.6125`, `k=4` -> `0.34933035714285715`, `k=5` -> `0.1669456845238095`, `k=6` -> `0.06921016808712122`.

control grammar-ის არა-რედუნდანტობა, patterns რომლებზედაც `G0` აწარმოებს tree-ს, რომელსაც არც ერთი strict ordering ვერ აწევს:

| k | control_only_patterns | pattern_count | control_only_fraction |
|---|---|---|---|
| 2 | 0 | 16 | 0.0 |
| 3 | 4 | 64 | 0.0625 |
| 4 | 40 | 256 | 0.15625 |
| 5 | 280 | 1024 | 0.2734375 |
| 6 | 1632 | 4096 | 0.3984375 |

ეს ცხრილი `control_only_pattern_sweep`-ის output-ია: pattern control-only-ია მაშინ, როცა `G0`-ის tree არ არის იმ trees-ს შორის, რომლებსაც `24` strict ordering აწარმოებს იმავე source-ზე.

`a - b*c + d/e - f`-ზე control-only tree კონკრეტულად ეს არის:

```text
('-', ('+', ('-', 'a', ('*', 'b', 'c')), ('/', 'd', 'e')), 'f')
```

გამოყენებული ზუსტი command sweep ცხრილისთვის:

```text
python -c "from parseatlas.ast_space import operator_pattern_sweep; [print(item) for item in operator_pattern_sweep(max_operators=6)['levels']]"
```

per-expression ცხრილისთვის:

```text
python -c "from parseatlas.ast_space import coverage_report; [print(item) for item in coverage_report(('a + b*c', 'a + b + c', '2*t + 1 - t/2', 'a + b*c - d/e', 'a - b*c + d/e - f', '2*x*x + 1 - x/2 + x'))['expressions']]"
```

control-only ცხრილისთვის:

```text
python -c "from parseatlas.ast_space import control_only_pattern_sweep; [print(item) for item in control_only_pattern_sweep(max_operators=6)['levels']]"
```

## Multicore გაზომვა და default path

`operator_pattern_sweep`-ის sequential და parallel path გაიზომა 16 core Windows host-ზე, თითო კონფიგურაცია სუფთა process-ში (cold lru_cache), მთელ sweep-ზე:

| max_operators | workers=1 | workers=2 | workers=8 | workers=15 |
|---|---|---|---|---|
| 3 | 0.029 s | 1.218 s | 2.070 s | 3.020 s |
| 5 | 0.777 s | 2.892 s | 4.248 s | 5.937 s |
| 6 | 4.607 s | 5.464 s | 5.824 s | 8.206 s |

თითოეული უჯრა ერთი ასეთი გაშვებაა, `max_operators` და `workers` argv-დან:

```text
python -c "import sys, time; from parseatlas.ast_space import operator_pattern_sweep; t = time.perf_counter(); operator_pattern_sweep(max_operators=int(sys.argv[1]), workers=int(sys.argv[2])); print(time.perf_counter() - t)" 6 1
```

sequential path ყველა ზომაზე იგებს, ამიტომ ამ workload-ის **default sequential-ია**: `workers=None` -> `1`. მიზეზი გაზომვაშივე ჩანს — ერთი pattern მიკროწამების parsing-ია, spawned process კი ყოველ ჯერზე იხდის interpreter start-ს პლუს sympy import chain-ს, და ეს ფიქსირებული cost იმაზე დიდია, ვიდრე გასანაწილებელი სამუშაო. `k=6`-ზე გასანაწილებელი სამუშაო ყველაზე დიდია და სწორედ იქ ყველაზე პატარაა განსხვავება (`4.607` vs `5.464`), მაგრამ break-even მაინც არ მიიღწევა.

parallel path შენარჩუნებულია და ხელმისაწვდომია explicit `workers=N`-ით, `workers=0` კი worker count-ს observed core count-იდან იღებს (`cpu_count() - 1`, headroom-ით), ისე რომ hardcoded constant არსად არის. ორივე path-ის output bit-for-bit ერთნაირია და ეს `test_sequential_and_parallel_sweeps_are_identical`-ითაა დაფიქსირებული; parallelism მხოლოდ სიჩქარეზე მოქმედებს და არა შედეგზე.

## ინტერპრეტაცია

precedence-ით წარმოებული AST-ები expression-ის ზრდასთან ერთად parenthesization space-ის ქრებადი წილი ხდება. `k=2`-ზე mean coverage `0.875`-ია, `k=6`-ზე კი `0.07222863399621213`, ხოლო `full_coverage_fraction` `0.75`-იდან `0.0`-მდე ეცემა უკვე `k=5`-ზე. ეს არის **observation** ჩამოთვლილ operator patterns-ზე და არა დამტკიცებული asymptotic law.

სტრუქტურული ზედა ზღვარი ცალკე დგას: registry-ში `25` grammar-ია, ამიტომ ერთი source-ისთვის reachable trees `<= 25`, `C(k)` კი Catalan-ის ტემპით იზრდება; `k=6`-ზე ეს ზღვარი `25/132 = 0.1894`-ია და დაკვირვებული `max_coverage` `0.16666666666666666` მასზე დაბალია. ამ registry-სთვის ზღვრის ვარდნა **symbolically justified** არის.

მეორე კონკრეტული სტრუქტურული შედეგი: tied-level control grammar `G0` არ არის რედუნდანტული. `k=3`-დან დაწყებული არსებობს patterns, სადაც `G0` აღწევს tree-ს, რომელსაც არც ერთი strict total ordering ვერ აწარმოებს, და ეს წილი `k`-სთან ერთად იზრდება: `0.0625` -> `0.15625` -> `0.2734375` -> `0.3984375`. ესე იგი tied precedence levels grammar-space-ს ნამდვილად აფართოებს და არა მხოლოდ strict orderings-ის მოხერხებულ shorthand-ს წარმოადგენს.

```text
full parenthesization space -> precedence-reachable subset -> strict-reachable subset
```

## შეზღუდვები

- sweep მხოლოდ `k <= 6`-მდე მიდის; `k=7`-ზე pattern count `16384`-ია და ჯერ არ არის გაზომილი.
- corpus flat expressions-ისგან შედგება; source-ში ხელით ჩაწერილი parentheses leaf/operator თანმიმდევრობას ცვლის და ამ enumeration-ში არ შედის.
- coverage სტრუქტურულ tree form-ს ზომავს და არა semantic class-ს; ორი განსხვავებული tree შეიძლება ერთსა და იმავე canonical expression-ს იძლეოდეს.
- grammar registry ფიქსირებულია `24 + 1`-ზე; სხვა precedence system-ები, მაგალითად მეტი tied level ან non-global rules, არ არის შემოწმებული.
- parallel path ამ host-ზე ყველა გაზომილ ზომაზე უფრო ნელია და default-ად sequential არის არჩეული; ეს ერთ machine-ზე გაზომილი შედეგია და არა ზოგადი დასკვნა. სხვა host-ზე ან ბევრად უფრო ძვირ per-pattern workload-ზე break-even შეიძლება შეიცვალოს და გაზომვა თავიდან უნდა გაკეთდეს.

## Evidence-ის კლასიფიკაცია

- Catalan counts, per-expression coverage, sweep ცხრილი და control-only pattern counts executable **observations** არის.
- `reachable <= 25` და აქედან გამომდინარე coverage-ის ზედა ზღვარი `25/C(k)` ამ registry-სთვის **symbolically justified** არის.
- ის, რომ coverage ნებისმიერი global precedence system-ისთვის და ნებისმიერი `k`-სთვის ნულისკენ მიისწრაფვის, ჯერ **hypothesis** არის; აქ მხოლოდ `k <= 6` დიაპაზონია გაზომილი.
- control grammar-ის არა-რედუნდანტობა `k >= 3`-ზე **observation** არის, კონკრეტული control-only tree-ით დადასტურებული.

## ვალიდაცია

```text
python -m pytest -q tests/test_ast_space.py
9 passed
```

```text
python -m pytest -q
140 passed
```

მთლიანი suite-ის რიცხვი ამ გაშვების მომენტისაა; repository-ში პარალელურად სხვა ექსპერიმენტების modules და tests ემატება, ამიტომ total იზრდება, ხოლო `tests/test_ast_space.py`-ის `9 passed` ამ ექსპერიმენტის ფიქსირებული წვლილია.
