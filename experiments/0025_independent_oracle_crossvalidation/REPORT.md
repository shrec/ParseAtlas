# ParseAtlas ექსპერიმენტი 0025: independent-implementation cross-validation

## მიზანი

ყველა წინა ექსპერიმენტს ერთი და იგივე სისუსტე ჰქონდა: partition, რომელსაც ვზომავთ, ერთი implementation-ის პროდუქტია. თუ parser-ში ან semantic key-ში სისტემატური შეცდომაა, არც ერთი შიდა test მას ვერ დაიჭერს, რადგან ყველა test იმავე კოდზეა დამოკიდებული. გავლილი test suite შიდა თანმიმდევრობას ამტკიცებს და არა იმას, რომ გაზომილი partition სწორია.

აქ იგივე კითხვას მეორე, სრულიად დამოუკიდებელი implementation პასუხობს. პროექტის owner-ს UltrafastSecp256k1-ში, branch `experiment/representation-search`-ზე, დაწერილი აქვს იმავე იდეის საკუთარი ვერსია — `repsearch`. ის ParseAtlas-თან **არც ერთ ხაზ კოდს არ იზიარებს** და, რაც უფრო მნიშვნელოვანია, equality-ს სხვა oracle-ით წყვეტს.

კითხვა ასე დაისმის:

```text
ორი დამოუკიდებელი implementation, ორი განსხვავებული equivalence oracle,
ერთი და იგივე token sequence -> ერთი და იგივე partition?
```

## Cross-validation structure

ორი oracle ერთსა და იმავე `(token sequence, G)` წყვილს ამუშავებს:

```text
ParseAtlas : custom parser      -> SymPy simplify -> semantic key (canonical, domain, excluded_points)
repsearch  : independent parser -> exact RatFunc over Q -> equality by cross-multiplication
```

`repsearch/poly.py`-ის equality განსაზღვრებაა:

```text
a/b == c/d   <=>   a*d - c*b == 0   (as polynomials over Q)
```

არც SymPy, არც floating point, არც probabilistic identity test. fingerprint მხოლოდ bucketing-ისთვის გამოიყენება და bucket-ის შიგნით ყოველი გატოლება exact cross-multiplication-ით დასტურდება. ParseAtlas კი პირიქით — SymPy-ის canonicalization-ს ეყრდნობა და key-ში `excluded_points`-საც ინახავს. ორი oracle არა მარტო სხვა კოდია: ისინი **სხვადასხვა კითხვას** პასუხობენ.

### Grammar id correspondence — derived, არა hardcoded

partition-ების შედარება აზრს კარგავს, თუ grammar label-ები არასწორად არის შესაბამისობაში მოყვანილი. ამიტომ correspondence კოდში გამოითვლება და მტკიცდება, და არა ცხრილიდან იკითხება:

```text
ParseAtlas  strict_grammars()  -> G01..G24 = itertools.permutations(("+", "-", "*", "/"))
repsearch   PRECEDENCE_ORDERS  -> list(itertools.permutations(BINARY_OPS))
```

`grammar_correspondence()` სამ ფაქტს ამოწმებს და შეუსაბამობაზე `AssertionError`-ს აგდებს:

1. `repsearch.expr.BINARY_OPS` იგივეა, რაც `parseatlas.grammar.OPERATORS` — `('+', '-', '*', '/')`.
2. ორივე თანმიმდევრობა ზუსტად `itertools.permutations`-ის რიგშია.
3. თითო ordering-ისთვის ParseAtlas-ის `Grammar.binding_power` ემთხვევა `repsearch.grammar.precedence_map(order)`-ს — ორივე `order[0]`-ს ყველაზე მაღალ binding strength-ს აძლევს.

გაზომილი შედეგი: `24` შესაბამისობა, `G01 = ('+', '-', '*', '/')`, `G24 = ('/', '*', '-', '+')`, binding power ემთხვევა ოცდაოთხივეზე.

### Snapshot

`repsearch` verbatim snapshot-ად ჩამოსხდა `case_studies/ultrafast_secp256k1/repsearch_snapshot/`-ში: `28` ფაილი, `283895` byte, `diff -r --exclude=__pycache__` სუფთა. ParseAtlas მას არ ინახავს და მისი test-ები ParseAtlas suite-ს არ ეკუთვნის (`testpaths = ["tests"]`). იმპორტი ხდება explicit `sys.path` insertion-ით და `importlib.import_module`-ით; snapshot-ის არარსებობისას `SnapshotUnavailable` აგდებს actionable ტექსტს და `tests/test_cross_validation.py` სწორედ იმ მიზეზით skip-დება.

## Corpus

პირველადი corpus რვა expression-ია:

```text
2*t + 1 - t/2
3*x + 2 - x/3
2*x*x + 1 - x/2
a + b*c - d/e
a - b*c + d/e - f
x*x - 1
2*x + 3
a/b + c*d - e/f + g
```

მეორე corpus removable restriction-ის probe-ებია:

```text
x/x
(x*x - 1)/(x - 1)
x - x + x
1/x - 1/x
```

მესამე corpus generated-ია და divergence-ის სისტემატურ ძებნას ემსახურება: ყველა უფრჩხილო `atom (op atom)^3` თანმიმდევრობა, სადაც `atom` არის `{x, y, 1, 2}`-დან და `op` არის `{+, -, *, /}`-დან — სულ `4^4 * 4^3 = 16384` token sequence.

## დაკვირვებული შედეგები

### რვა expression: identical partitions, 8/8

```text
expression              PA classes  RS classes  relation
2*t + 1 - t/2                    8           8  identical
3*x + 2 - x/3                    8           8  identical
2*x*x + 1 - x/2                  8           8  identical
a + b*c - d/e                   10          10  identical
a - b*c + d/e - f               16          16  identical
x*x - 1                          2           2  identical
2*x + 3                          2           2  identical
a/b + c*d - e/f + g             18          18  identical
```

- total: `8`, identical: `8`, refinement: `0`, divergent: `0`.
- ეს **partition-ის იგივეობაა და არა class count-ის დამთხვევა**: შედარება `tuple(sorted(tuple(sorted(block))))` სტრუქტურაზე ხდება, ე.ი. თითო block-ის membership ემთხვევა. ოცდაოთხივე grammar id ორივე partition-ის გაერთიანებაშია.
- `repsearch_unevaluated` ყველა რვაზე ცარიელია: ოცდაოთხივე grammar-ს ორივე oracle აფასებს.

### Probe-ები: ორივე oracle ეთანხმება ოთხივეზე

```text
x/x                pa=1 rs=1  identical   C01 n=24 canonical=1               excluded=('0',)
(x*x - 1)/(x - 1)  pa=2 rs=2  identical   C01 n=12 canonical=x               excluded=('1',)
                                          C02 n=12 canonical=x + 1           excluded=('1',)
x - x + x          pa=2 rs=2  identical   C01 n=12 canonical=-x              excluded=()
                                          C02 n=12 canonical=x               excluded=()
1/x - 1/x          pa=2 rs=2  identical   C01 n=12 canonical=1/(x*(x - 1))   excluded=('1', '0')
                                          C02 n=12 canonical=0               excluded=('0',)
```

ოთხივეზე დამთხვევის მიზეზი ერთი და იგივეა: restriction **ყველა grammar-ს ერთნაირად აქვს**. `x/x`-ში ერთადერთი operator-ია, ამიტომ ოცდაოთხივე grammar ერთსა და იმავე AST-ს იძლევა; `(x*x - 1)/(x - 1)`-ში ფრჩხილები restriction-ს grammar-invariant-ს ხდიან. სადაც restriction ყველა grammar-ისთვის საერთოა, ის partition-ს ვერ ყოფს და ორივე oracle ერთსა და იმავეს ხედავს.

### სად განსხვავდებიან: სისტემატური ძებნა

`16384` generated token sequence გაიფილტრა structural screen-ით (ერთი rational-function class-ის შიგნით განსხვავებული divisor sub-expression), შემდეგ გადამოწმდა ორივე oracle-ით:

```text
screened                              16384
structural candidates                  1101
candidates with all 24 grammars live   1044
confirmed divergences                    38
  parseatlas strictly finer              38
  repsearch strictly finer                0
  incomparable                            0
sequences with unevaluated grammars     552
```

ოცდათვრამეტივე divergence ერთი და იმავე ფორმისაა: repsearch-ის ერთი block ParseAtlas-ში ორ ან მეტ block-ად იშლება. მიზეზის გაზომვა:

```text
split repsearch blocks            38
  same canonical form             38
  different excluded_points set   38
  ordering-only artifacts          0
```

ე.ი. ყოველ შემთხვევაში canonical form **ერთი და იგივეა** და partition მხოლოდ `excluded_points`-ით იშლება. არც ერთი divergence არ არის `excluded_points` tuple-ის რიგის artifact — ყველგან სიმრავლეც განსხვავდება.

### ასიმეტრია, როგორც დამოუკიდებელი შედეგი

მიმართულების განაწილება ცალკე შედეგია და არა divergence-ების აღწერის დანამატი. `1044` სრულად შესადარებელ კანდიდატზე:

```text
identical                   1006
ParseAtlas strictly finer     38
repsearch strictly finer       0
incomparable                   0
undecided                      0
```

მიმართულება **ყოველთვის ერთი და იგივეა**. არც ერთხელ არ აღმოჩნდა repsearch-ის partition უფრო finer, და არც ერთხელ არ აღმოჩნდა ორი partition ურთიერთშეუდარებელი — ე.ი. ისეთი, სადაც თითოეული მეორეს ერთდროულად ჰყოფს და აერთიანებს. ეს განაწილება თავისთავად informative-ია: ორი oracle-ის უბრალო ხმაური `38 / 0 / 0`-ს ვერ მოგვცემდა, რადგან შემთხვევითი უთანხმოება ორივე მიმართულებით გაიფანტებოდა.

ოცდათვრამეტივე divergence ერთი და იმავე მიზეზისაა — ერთი და იგივე canonical form, სხვადასხვა excluded-points სიმრავლე. ეს არის პირდაპირი გაზომვითი მტკიცებულება, რომ `(F, D, U)` დისციპლინა **მუშა ნაწილია და არა დეკორაცია**: სუფთა rational-function oracle ჩუმად აერთიანებს კლასებს, რომლებიც მხოლოდ removable restriction-ით განსხვავდებიან. ის, რასაც ParseAtlas key-ში ინახავს, ალგებრულად ზედმეტი არ არის — ის ზუსტად ის კომპონენტია, რომელიც ამ სივრცეში `38`-ჯერ ჰყოფს კლასს და არც ერთხელ არ აერთიანებს.

ერთი მოჩვენებითი საწინააღმდეგო შემთხვევა არსებობს და ის oracle-ების უთანხმოება არ არის: `1/2 + x`-ზე `compare` ადრე `repsearch_strictly_finer`-ს აბრუნებდა. მიზეზი lexical-ია — ParseAtlas-ის tokenizer `1/2`-ს **ერთ რაციონალურ ლიტერალად** კითხულობს, repsearch კი `1 / 2`-ად, ამიტომ ორი oracle სხვადასხვა გამოსახულებაზე პასუხობდა. ახლა ეს შემთხვევა `incomparable_lexical_mismatch`-ად უარიყოფა (იხ. ქვემოთ), ამიტომ `repsearch strictly finer = 0` ცრუ counterexample-ით აღარ ბინძურდება.

### ორი წაკითხვადი მაგალითი

`x / x - x - 1`:

```text
repsearch : 1 class, 24 grammars, rational function -x
ParseAtlas: C01 n=12 canonical=-x  excluded=()
            C02 n=12 canonical=-x  excluded=('0',)
```

იმ თორმეტ grammar-ში, სადაც `-` უფრო მაგრად იბმის ვიდრე `/`, AST არის `x / (x - x - 1)`; divisor არის constant `-1`, ამიტომ restriction არ ჩნდება და ფუნქცია ყველგან განსაზღვრულია. დანარჩენ თორმეტში, სადაც `/` იბმის მაგრად, AST არის `(x / x) - x - 1`; divisor არის `x`, ამიტომ `x = 0` გამოირიცხება. **ორივე გამოსახულება `-x`-ია, მაგრამ ერთი ყველგან განსაზღვრულია და მეორე ნულში არა.** repsearch მათ აერთიანებს, რადგან rational function-ების ველში ისინი ერთი და იგივე ელემენტია.

`x - y / y - x`:

```text
repsearch : 1 class, 24 grammars, rational function -1
ParseAtlas: C01 n=12 canonical=-1  excluded=('y',)
            C02 n=12 canonical=-1  excluded=('0',)
```

`-`-ის მაგრად ბმისას AST არის `(x - y) / (y - x)` — მუდმივი `-1`, undefined-ია `x = y`-ზე. `/`-ის მაგრად ბმისას AST არის `x - (y / y) - x` — ისევ `-1`, undefined-ია `y = 0`-ზე. ერთი და იგივე მუდმივი ფუნქცია, ორი სხვადასხვა removable restriction.

### მესამე ტიპის განსხვავება: representability

`x/x - x/x`-ზე repsearch-ის `RatFunc` ოცდაოთხიდან `12` grammar-ს **ვერ აფასებს**: literally ნულოვანი მნიშვნელი `ZeroDivisionError`-ს აგდებს, რადგან `0` არ შეიძლება იყოს Q-ზე rational function-ის მნიშვნელი. ParseAtlas იმავე თორმეტს `zoo`-ს აძლევს, `excluded_points = ('all', '0')`. საერთო universe-ზე (დარჩენილი `12` grammar) ორივე partition ემთხვევა, ამიტომ ეს შემთხვევა `identical`-ად ითვლება და `repsearch_unevaluated`-ში აღირიცხება, და არა partition-ის განსხვავებად. generated corpus-ის `16384`-დან `552` თანმიმდევრობას აქვს ერთი მაინც ასეთი grammar.

### `compare` არ ეთანხმება იქ, სადაც შედარება საერთოდ არ მომხდარა

`compare`-ის ერთადერთი საქმე თანხმობაზე გადაწყვეტილებაა, ამიტომ ის fail-open ვერ იქნება. input, რომელზეც შედარება ვერ მოხერხდა, **undecided**-ად აღირიცხება და არასოდეს თანხმობად. სამი ასეთი შემთხვევაა და თითოეულს თავისი relation აქვს:

```text
relation                          როდის                                    გაზომილი მაგალითი
incomparable_empty_universe       repsearch ოცდაოთხივე grammar-ს ვერ       x/0  -> repsearch_unevaluated = 24,
                                  აფასებს, საერთო universe ცარიელია               compared_universe = ()
incomparable_unevaluable          ერთ-ერთი implementation source-ს          1/0  -> ZeroDivisionError: Fraction(1, 0)
                                  საერთოდ ვერ ამუშავებს                            x +  -> ValueError (parser)
incomparable_lexical_mismatch     ორი tokenizer ერთსა და იმავე token       1/2 + x -> ParseAtlas: (num 1/2)(op +)(name x)
                                  sequence-ს არ კითხულობს                          repsearch: (num 1)(op /)(num 2)(op +)(name x)
```

ამ სამივეს `identical = False`, `refinement = None` და გაზომილი `reason` აქვს; `cross_validation_report` მათ ცალკე ითვლის (`undecided`, `empty_universe`, `unevaluable`, `lexical_mismatch`) და ინარჩუნებს ამოწურვად აღრიცხვას:

```text
identical + refinement + divergent + undecided == total
```

ამ guard-ებამდე `x/0` **`identical=True`, `relation="identical"`** ბრუნდებოდა: `_restrict` ორივე მხარეს ცარიელ partition-ად აქცევდა, ცარიელი partition თავის თავს უდრის, და „შედარება ვერ მოხერხდა" იკითხებოდა როგორც „ორი oracle ეთანხმება"; `cross_validation_report` კი ამაზე identical მრიცხველს ზრდიდა. `1/0` საერთოდ `ZeroDivisionError`-ს აგდებდა `compare`-იდან. ის მოდის ParseAtlas-ის საკუთარი rational-literal გზიდან (`Fraction(1, 0)` `parser.py`-ში), და არა vendored კოდიდან — vendored snapshot არც ერთი ხაზით არ შეცვლილა; შეცდომა ამ module-ის საზღვარზე იჭერება და კლასიფიცირდება.

**ამ ანგარიშის არც ერთი რიცხვი არ იცვლება.** ეს გაზომილია და არა ნავარაუდევი:

- რვავე corpus source-სა და ოთხივე probe-ს `repsearch_unevaluated` ცარიელი აქვს, ამიტომ empty universe არსად ჩნდება;
- `16384` generated sequence-იდან, პლუს რვა corpus source, პლუს ოთხი probe — lexical mismatch-ების რაოდენობა `0` (ორივე tokenizer-ის normalized token stream ყველგან ემთხვევა; generated corpus-ში `\d+/\d+` ლიტერალი არ გვხვდება, რადგან atom-ები გამოყოფილია ჰარებით);
- sweep მხოლოდ სრული universe-ის კანდიდატებს ადასტურებს, ამიტომ `1044`-იდან არც ერთი არ არის undecided;
- ხელახალი გაშვება ამ ცვლილებების შემდეგ: `screened 16384`, `structural candidates 1101`, `confirmed candidates 1044`, `confirmed divergences 38`, `parseatlas strictly finer 38`, `repsearch strictly finer 0`, `incomparable 0`, `undecided 0`, `parse_errors 0` — უცვლელი.

### Multicore

`cross_validation_report` per-source დამოუკიდებელია, ამიტომ default-ად cores-ზე ნაწილდება. worker რაოდენობა `os.cpu_count()`-იდან გამოითვლება ორი core headroom-ით; `workers=1` sequential გზას აიძულებს. SymPy CPU-bound-ია და GIL-ს არ ათავისუფლებს, ამიტომ process pool და არა thread pool; pool function module-level-ია, რადგან Windows `spawn`-ს იყენებს.

გაზომვა რვა expression-ზე, 16 core:

```text
sequential  workers=1   elapsed=11.723s
parallel    workers=8   elapsed=5.346s
speedup     2.19x
identical details: True
```

worker რაოდენობა `8`-ია და არა `14`, რადგან item-ების რაოდენობაზე მეტი worker აზრს კარგავს. `16384`-იანი sweep-ი `14` worker-ზე გაეშვა.

## ინტერპრეტაცია

ორი implementation, რომლებიც **არც ერთ ხაზ კოდს არ იზიარებენ** და equality-ს **სხვადასხვა oracle-ით** წყვეტენ — SymPy-ის canonicalization ერთი მხრიდან, exact rational-function cross-multiplication მეორე მხრიდან — რვავე expression-ზე ერთსა და იმავე partition-ს იძლევიან, membership-ის დონეზე. ეს გაცილებით ძლიერი evidence-ია, ვიდრე რომელიმე მათგანი ცალკე: ერთი implementation-ის შიდა test suite მხოლოდ იმას ამტკიცებს, რომ კოდი თავის თავს ეთანხმება. ეს ParseAtlas-ის **პირველი external validation-ია**.

მეორე შედეგი უფრო საინტერესოა. `1044` შემოწმებული კანდიდატიდან `38`-ზე ParseAtlas-ის partition **strictly finer** აღმოჩნდა, `0`-ზე კი repsearch-ის. ეს არ არის ორი oracle-ის შეუთანხმებლობა — ეს არის განსხვავებული კითხვის განსხვავებული პასუხი. repsearch rational function-ებს ადარებს, ამიტომ removable restriction-ს განზრახ აგდებს; ParseAtlas მას `(F, D, U)` დისციპლინის მიხედვით key-ში ტოვებს. `x / x - x - 1`-ის ორი წაკითხვა ერთსა და იმავე ფუნქციას `-x` აძლევს, მაგრამ **სხვადასხვა domain-ზე**. თუ ორ representation-ს შორის არჩევანი domain-ის შენარჩუნებაზეა დამოკიდებული — და cryptographic primitive-ის ოპტიმიზაციაში სწორედ ასეა — მაშინ pure-algebra oracle ამ განსხვავებას ვერ დაინახავს, ხოლო `(F, D, U)` დისციპლინა ხედავს.

ორივე მიმართულება საჭიროა. repsearch აჩვენებს, რომ ParseAtlas-ის partition არ არის SymPy-ის artifact. ParseAtlas აჩვენებს, რომ rational-function equality არ არის საკმარისი, როცა კითხვა representation-ის არჩევანია და არა მხოლოდ ალგებრული იგივეობა.

```text
repsearch  : რომელი grammar-ები იძლევიან ერთსა და იმავე ფუნქციას?
ParseAtlas : რომელი grammar-ები იძლევიან ერთსა და იმავე ფუნქციას ერთსა და იმავე domain-ზე?
```

## შეზღუდვები

- პირველადი corpus მხოლოდ **რვა expression-ია**. რვა დამთხვევა არ არის ზოგადი თანხმობის მტკიცებულება; ის ერთი კონკრეტული corpus-ის გაზომვაა.
- ორი implementation-ის დამთხვევა **არც ერთის სისწორის მტკიცებულება არ არის**. ორივემ შეიძლება ერთი და იგივე შეცდომა დაუშვას — მაგალითად, ორივე left-associative precedence-climbing parser-ია, ამიტომ associativity-ის საერთო შეცდომა ამ შედარებით არ დაიჭირება. cross-validation სისტემატურ divergence-ს იჭერს, არა საერთო blind spot-ს.
- snapshot **frozen-ია**. ის ParseAtlas-ის მიღმა შეიძლება შეიცვალოს; ეს შედარება `experiment/representation-search`-ის ერთ კონკრეტულ მდგომარეობაზეა. branch owner-ის ლოკალურია და არ არის push-ული, ამიტომ მესამე მხარეს მისი დამოუკიდებლად მოტანა ამჟამად არ შეუძლია.
- divergence search უფრჩხილო `atom (op atom)^3` თანმიმდევრობებზეა, `{x, y, 1, 2}` atom-ებით. `38` მიღებული divergence ამ სივრცის შედეგია და არა ყველა შესაძლო expression-ის.
- ParseAtlas-ის `excluded_points` root-ს ინახავს და არა `(variable, root)` წყვილს: `x - y / y - x`-ში `('y',)` ნიშნავს `x = y`-ს, ხოლო `('0',)` ნიშნავს `y = 0`-ს. key ამ სახით უფრო coarse-ია, ვიდრე შეიძლებოდა ყოფილიყო; ამ ექსპერიმენტში ის მაინც უფრო finer აღმოჩნდა, ვიდრე rational-function equality, მაგრამ თავად key-ის გაუმჯობესება ღია რჩება.
- `divergence_search`-ის structural screen მხოლოდ ParseAtlas-ის `undefined_terms` სემანტიკას მოდელირებს; სხვა ტიპის divergence — მაგალითად SymPy-ის canonicalization-ის შეცდომა — ამ screen-ს გვერდს აუვლიდა და მას მხოლოდ full confirmation დაიჭერდა. screen-ის სისრულე გაზომილია მხოლოდ პატარა slice-ზე: `128`-ივე თანმიმდევრობის სრულმა შედარებამ (`18.7s` sequential) იგივე `6` divergence მოგვცა, რაც screen-მა; `16384`-ზე ასეთი შემოწმება არ გაშვებულა.
- **ორი implementation-ის lexical ენა არ ემთხვევა.** ParseAtlas-ის tokenizer `\d+(?:/\d+)?`-ს იღებს, ე.ი. `1/2` მისთვის ერთი რაციონალური ლიტერალია; repsearch `\d+\.\d+|\d+`-ს იღებს და `**`/`^`-საც, ე.ი. `1/2`-ს გაყოფად კითხულობს, `1.5`-ს კი ParseAtlas საერთოდ არ იღებს. სადაც ეს ხდება, ორი oracle სხვადასხვა გამოსახულებაზე პასუხობს და შედარებას აზრი ეკარგება — ამიტომ `compare` ასეთ input-ს `incomparable_lexical_mismatch`-ით უარყოფს და არა partition-ის განსხვავებად აღრიცხავს. ამ ექსპერიმენტის corpus-ები ამ ზონას არ ეხება (გაზომილი mismatch: `0`), მაგრამ ორი implementation-ის საერთო ენა უფრო ვიწროა, ვიდრე თითოეულის ცალკე.
- wall time ცვალებადია: sweep-ის სამმა გაშვებამ `49.7s`, `78.4s` და `88.8s` მოგვცა `14` worker-ზე, რადგან იმავე მანქანაზე პარალელურად სხვა agent-ის suite მუშაობდა. count-ები სამივე გაშვებაზე იდენტურია.

## Evidence-ის კლასიფიკაცია

- `8/8 identical partitions`, class count-ები `8, 8, 8, 10, 16, 2, 2, 18`, `24`-ელემენტიანი correspondence და `38 / 0 / 0` divergence breakdown executable **observations** არის.
- "ParseAtlas strictly finer" ამ `1044` კანდიდატზე გაზომილი **მიმართებაა**, არა თეორემა. თეორემა იქნებოდა: "ნებისმიერ token sequence-ზე ParseAtlas-ის partition repsearch-ის partition-ის refinement-ია". ეს ჯერ არ არის ნაჩვენები, თუმცა გაზომვა ამ მიმართულებას ეთანხმება და საპირისპირო შემთხვევა (`repsearch strictly finer`) `0`-ჯერ დაფიქსირდა. ერთადერთი შემთხვევა, სადაც `repsearch strictly finer` საერთოდ იჩენდა თავს (`1/2 + x`), lexical არტეფაქტი აღმოჩნდა და არა oracle-ების უთანხმოება; ის ახლა ცალკე უარიყოფა და `0` მასზე არ არის დამოკიდებული.
- ორი oracle-ის დამთხვევა **external validation-ია**, არა correctness proof.
- `zoo` vs `ZeroDivisionError` განსხვავება ორი oracle-ის **representability**-ის განსხვავებაა და არა partition-ის უთანხმოება; ის ცალკე აღირიცხება.
- `undecided` შედეგები (`empty universe`, `unevaluable`, `lexical mismatch`) **არც თანხმობაა და არც უთანხმოება**: ისინი აღნიშნავენ, რომ შედარება არ მომხდარა. ამ corpus-ებზე სამივე `0`-ია, ამიტომ ისინი არც ერთ გამოქვეყნებულ რიცხვს არ ეხება; ისინი guard-ებია და არა შედეგები.

## ვალიდაცია

ზუსტი ბრძანებები:

```text
python -m pytest -q tests/test_cross_validation.py
python -c "from parseatlas.cross_validation import CROSS_VALIDATION_CORPUS, cross_validation_report; r = cross_validation_report(CROSS_VALIDATION_CORPUS, workers=1); print(r['total'], r['identical'], r['refinement'], r['divergent']); print([d['parseatlas_class_count'] for d in r['details']])"
python -c "from parseatlas.cross_validation import compare; [print(s, '->', compare(s)['relation'], compare(s)['identical']) for s in ('x/0', '1/0', '1/2 + x')]"
python -c "from parseatlas.cross_validation import token_sequences, divergence_search; r = divergence_search(token_sequences(3)); print({k: r[k] for k in ('screened','structural_candidates','confirmed_candidates','sequences_with_unevaluated_grammars','confirmed_divergences','parseatlas_strictly_finer','repsearch_strictly_finer','incomparable','undecided')})"
python -m pytest -q
```

გამოსავალი:

```text
34 passed in 10.01s

8 8 0 0
[8, 8, 8, 10, 16, 2, 2, 18]

x/0 -> incomparable_empty_universe False
1/0 -> incomparable_unevaluable False
1/2 + x -> incomparable_lexical_mismatch False

{'screened': 16384, 'structural_candidates': 1101, 'confirmed_candidates': 1044,
 'sequences_with_unevaluated_grammars': 552, 'confirmed_divergences': 38,
 'parseatlas_strictly_finer': 38, 'repsearch_strictly_finer': 0, 'incomparable': 0,
 'undecided': 0}

289 passed in 58.50s
```

ამ ექსპერიმენტმა `34` test დაამატა (`tests/test_cross_validation.py`, `17`-იდან `34`-მდე). სრული suite `289 passed` იყო ამ გაზომვის მომენტში; იმავე tree-ზე პარალელურად სხვა card მუშაობდა (`tests/test_transformation_axes.py` `26`-იდან `55`-მდე გაიზარდა), ამიტომ სრული რიცხვი მხოლოდ ამ გაშვების ფოტოა.

### რას იჭერს test-ები

გადამწყვეტი test-ები `compare`-ის გადაწყვეტილებას პროდუქციის გზაზე ატარებენ და არა ხელით აწყობილ tuple-ებზე. თითოეული გადამოწმდა mutant-ის ხელახლა დადებით:

```text
mutant                                                            შედეგი
identical = left == right   ->  len(left) == len(right)           2 failed  (compare + aggregate counter)
empty-universe guard გამორთული                                    3 failed
lexical-mismatch guard გამორთული                                  2 failed  (refinement 1 -> 2: ცრუ repsearch_strictly_finer)
_refines(left, right) <-> _refines(right, left)                    5 failed
token_sequences: repeat=operator_count + 1 -> operator_count       2 failed + 4 errors
```

პირველი mutant ადრე **მთელ suite-ს გადარჩებოდა**. ახლა მას ორი test იჭერს: ერთი `compare`-ს პირდაპირ ატარებს ორ **რეალურ** partition-ზე, რომლებსაც ერთნაირი ზომა და განსხვავებული membership აქვთ (`2*x + 3`-ის ParseAtlas partition და `x*x - 1`-ის repsearch partition, ორივე `2` კლასი, ოცდაოთხივე grammar-ზე, არც ერთი მეორეს არ ახვევს), მეორე კი იმავე ჩანაცვლებას `cross_validation_report`-ის `identical` მრიცხველზე ატარებს `workers=1`-ით.

მეორე headline-ს ახლა იაფი regression guard აქვს: `token_sequences`-ის ზუსტი რაოდენობები (`64`, `1024`, `16384`) და generator-ის იმავე სივრცის `128`-თანმიმდევრობიანი slice (`atoms={x, 1}`, `operators={-, /}`), რომელიც screen-იდან confirmation-მდე ბოლომდე გადის:

```text
screened                              128
structural candidates                   7
candidates with all 24 grammars live    7
confirmed divergences                   6
  parseatlas strictly finer             6
  repsearch strictly finer              0
  incomparable                          0
sequences with unevaluated grammars    24
```

slice შეიცავს `x / x - x - 1`-ს — ერთ-ერთს იმ ორი divergence-იდან, რომელსაც ანგარიში სრულად კითხულობს — და ექვსივეზე მოწმდება მიმართულება (`_refines(finer, coarser)` და არა პირიქით) და მიზეზი (ერთი canonical form, განსხვავებული excluded points). `16384`-იანი sweep test-ში არ გადის.
