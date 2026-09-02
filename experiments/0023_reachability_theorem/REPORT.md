# ParseAtlas ექსპერიმენტი 0023: precedence-reachable parse trees-ის ზუსტი characterization

## მიზანი

ROADMAP Phase 9-ის ღია კითხვაა: ფიქსირებულ leaf/operator sequence-ზე რომელი binary trees შეუძლია
წარმოქმნას global precedence rule-მა და რომელი — არა. აქამდე პასუხი მხოლოდ brute-force
enumeration-ით მიიღებოდა და მხოლოდ ძალიან მოკლე input-ებისთვის მუშაობდა.

ამ ექსპერიმენტმა enumeration decision procedure-ით ჩაანაცვლა. გადამოწმდა ორი claim, ორივე
დამოუკიდებელი კოდით, `src/parseatlas/reachability.py`-ში:

- **Claim A — rightmost-minimum characterization.** ნებისმიერი რეგისტრირებული grammar `G`-სთვის
  binding-power map `p`-ით, `parse(E, G)` ემთხვევა იმ tree-ს, რომელსაც აშენებს რეკურსია: თუ
  operator range ცარიელია, დაბრუნდეს ერთადერთი leaf; სხვა შემთხვევაში ავიღოთ minimum binding power
  `lo` და გავყოთ **ყველაზე მარჯვენა** პოზიციაზე, რომელსაც `lo` power აქვს. მარჯვნიდან არჩევა სწორედ
  ტოლი power-ის operators-ის left associativity-ს აკოდირებს.
- **Claim B — order-feasibility characterization of reachability.** candidate tree `T` reachable-ია
  რომელიმე strict precedence grammar-ით მაშინ და მხოლოდ მაშინ, თუ tree-დან წაკითხული
  binding-power constraints strict total order-ს უშვებს.

## Decision procedure

`T`-ს ყოველ internal node-ზე, რომელიც operator range `[lo, hi)`-ს ყოფს პოზიცია `s`-ზე, root
operator `w[s]` უნდა აკმაყოფილებდეს:

```text
p(w[s]) <= p(w[t])   for every t in [lo, s)     weak constraint
p(w[s]) <  p(w[t])   for every t in (s, hi)     strict constraint
```

Symbolic justification პირდაპირ Claim A-ს რეკურსიიდან მოდის. `s` არის minimum-ის პოზიცია, ამიტომ
მარცხნივ არაფერი შეიძლება იყოს მკაცრად ნაკლები — ეს weak constraint-ია, და ტოლობა დაშვებულია
სწორედ იმიტომ, რომ split ყველაზე მარჯვენა minimum-ს იღებს. მარჯვნივ ტოლობაც აკრძალულია: თუ
`t > s`-ზე `p(w[t]) <= p(w[s])`, მაშინ rightmost minimum `t`-ზე ან უფრო მარჯვნივ იქნებოდა და
recursion `s`-ზე არ გაიყოფოდა.

constraints გროვდება არა პოზიციებს, არამედ **operator types**-ს შორის edges-ად. strict total
order-ში სხვადასხვა type-ს ყოველთვის განსხვავებული power აქვს, ამიტომ distinct types-ზე `<=` და `<`
ერთსა და იმავეს ნიშნავს. აქედან გამომდინარეობს decision rule:

```text
strict_reachable(T, w) holds exactly when
    (1) no strict constraint is a self-loop p(o) < p(o), and
    (2) the digraph of all constraints, restricted to distinct operator types, is acyclic
```

პირობა (2) აუცილებელია, რადგან cycle სხვადასხვა type-ს შორის მათ binding powers-ს ტოლობას
აძალებს, რასაც strict total order არ უშვებს. acyclic digraph კი topological order-ს იძლევა,
რომელიც ოთხივე operator-ზე strict total order-ად ვრცელდება.

`strict_reachable` grammars-ს **არ** enumerate-ავს: ის მხოლოდ constraint graph-იდან წყვეტს.
constraint-ების რაოდენობა `O(k^2)`-ია, cycle detection კი operator types-ის რაოდენობაზე
კვადრატულია, ანუ გადაწყვეტა polynomial time-შია.

## Corpus

Claim A-ს პირდაპირი შემოწმება ჩატარდა შემდეგ corpus-ზე, control grammar `G0`-სა და 24 strict
grammar-ზე:

```text
2*t + 1 - t/2
a - b*c + d/e - f
a/b + c*d - e/f + g
a - b - c
(x + 1)/(x - 2)
```

Claim B-ს exhaustive cross-validation გაეშვა canonical leaf sequence `a, b, c, ...`-ზე, ოთხი
operator-ის `(+ - * /)` ყველა operator word-ზე სიგრძით `k = 2..6`, და ყოველი word-ის ყველა Catalan
parenthesization-ზე. ground truth მიიღება რეალური parser-ით: tree reachable-ია, თუ ის ნამდვილად
წარმოიქმნება 24 strict grammar-იდან რომელიმეთი.

## დაკვირვებული შედეგები

Claim A, corpus-ზე:

- source count: `5`
- grammar count: `25` (`G0` control + `G01..G24` strict)
- comparison count: `125`
- agreement count: `125`
- disagreement count: `0`

Claim A ასევე გადამოწმდა exhaustive sweep-ის შიგნით, ყოველ operator word-ზე ყოველი strict
grammar-ისთვის:

- claim A checks: `130944`
- claim A disagreements: `0`

Claim B, exhaustive cross-validation `k = 2..6`:

| k | pattern_count | tree_count | unreachable_count | unreachable_fraction (%) | mismatch_count |
| --- | --- | --- | --- | --- | --- |
| 2 | 16 | 32 | 4 | 12.500 | 0 |
| 3 | 64 | 320 | 124 | 38.750 | 0 |
| 4 | 256 | 3584 | 2332 | 65.067 | 0 |
| 5 | 1024 | 43008 | 35828 | 83.305 | 0 |
| 6 | 4096 | 540672 | 503252 | 93.079 | 0 |

Aggregate:

```text
total_patterns         5456
total_trees            587616
total_unreachable      541540
unreachable_fraction   92.159 %
total_mismatches       0
characterization_holds True
```

ცალკეული structural observations:

- tree `("+", ("*", ("+", "a", "b"), "c"), "d")` operator word `["+", "*", "+"]`-ზე **არ** არის
  strict-reachable. `tree_constraints` აბრუნებს ცარიელ strict set-ს და weak set-ს
  `{("+", "+"), ("+", "*"), ("*", "+")}`. distinct types-ზე `+ -> *` და `* -> +` cycle-ს ქმნის, ანუ
  აძალებს `p(+) == p(*)`-ს, რაც strict grammar-ში შეუძლებელია.
- repeated operator word `["+", "+"]`-ზე right-leaning tree `("+", "a", ("+", "b", "c"))` არ არის
  reachable — ის strict self-loop `p(+) < p(+)`-ს წარმოქმნის; left-leaning tree
  `("+", ("+", "a", "b"), "c")` კი reachable-ია. ეს left associativity-ის პირდაპირი შედეგია.
- saturation case: operator word `["+", "*", "-", "/"]`-ზე, სადაც ოთხივე type განსხვავებულია,
  თოთხმეტივე `14` Catalan tree reachable-ია. ანუ unreachability მთლიანად repeated operator types-იდან
  მოდის.

Multicore: `verify_characterization` operator word-ზე independent და CPU-bound-ია, ამიტომ default-ად
processes-ზე ნაწილდება. worker count მიიღება `os.cpu_count()`-იდან ერთი core-ის headroom-ით და არა
hardcoded constant-იდან.

wall clock loaded developer machine-ზე reproducible point value **არ** არის, ამიტომ ქვემოთ ერთი
რიცხვის ნაცვლად მოცემულია ერთსა და იმავე machine-ზე გაზომილი **7 გამეორება** თითო path-ზე, median-ით
და range-ით:

```text
cpu_count             16
workers               15
repetitions           7 per path
parallel wall clock   median 2.37 s    range 2.33 - 2.59 s
sequential wall clock median 11.91 s   range 11.02 - 14.77 s
speedup (of medians)  5.02x
```

Machine-load caveat: ეს რიცხვები იმავე machine-ზეც კი მერყეობს და სხვა machine-ზე გადატანადი არ
არის. იმავე ორი path-ის ადრინდელმა 5-გამეორებიანმა გაშვებამ იმავე machine-ზე დააფიქსირა parallel
median `3.58` s და sequential median `12.46` s, ანუ speedup `3.48x` — რადგან იმ სერიის
პირველი parallel გაშვება cold start-ს იხდიდა (`16.25` s: Windows-ზე 15 interpreter-ის spawn პლუს
ცივი OS file cache). ამიტომ speedup უნდა წაიკითხოს როგორც დიაპაზონი — ამ machine-ზე დაახლოებით
`3.5x`-დან `5.0x`-მდე — და არა როგორც ერთი გამეორებადი რიცხვი. კონკურენტული load, core-ების
რაოდენობა და cache-ის მდგომარეობა ამ დიაპაზონსაც გადაწევს.

parallelism მხოლოდ სიჩქარეს ცვლის და არა შედეგს: `workers=1` sequential path და parallel path
ერთსა და იმავე aggregate dictionary-ს აბრუნებენ (`workers` ველის გარდა). ეს ტოლობა timing-ისგან
სრულიად დამოუკიდებლად მოწმდება `test_sequential_and_parallel_verification_agree`-ში, სადაც ორივე
მხარეს `workers` აშკარად არის მითითებული (`1` და `2`), რათა parallel branch ნამდვილად გაიაროს და
შემოწმება default-ის core count-ზე დამოკიდებული არ იყოს.

## ინტერპრეტაცია

პირველი შედეგი: reachability constraint graph-იდან polynomial time-ში წყდება. representation
search precedence space-ზე აღარ საჭიროებს grammars-ის enumerate-ს — candidate tree-ს ვწერთ,
constraints ვკითხულობთ და acyclicity-ს ვამოწმებთ. ეს enumeration-ის ექსპონენციალურ ხარჯს ერთი
graph pass-ით ცვლის და დიდი operator alphabet-ისთვისაც მუშაობს.

```text
candidate tree -> constraint edges -> cycle check -> reachable / unreachable
```

მეორე შედეგი უფრო მნიშვნელოვანია Phase 9-ისთვის. parenthesizations-ის აბსოლუტური უმრავლესობა
სტრუქტურულად მიუწვდომელია **ნებისმიერი** global precedence rule-ისთვის: `k = 6`-ზე უკვე `93.079`
პროცენტი, ხოლო მთელ დიაპაზონზე `587616` tree-დან `541540` (`92.159` პროცენტი) unreachable-ია. და
fraction `k`-სთან ერთად მონოტონურად იზრდება.

ეს არის ის რაოდენობრივი მიზეზი, რის გამოც Phase 9-ს parenthesization engine სჭირდება და არა უფრო
ფართო precedence registry. registry-ს გაფართოება მხოლოდ იმ პატარა reachable subset-ში მოძრაობს,
რომელსაც global precedence rule ეხება; unreachable უმრავლესობას მხოლოდ explicit grouping აღწევს.
saturation observation ამას აზუსტებს: სანამ ყველა operator type განსხვავებულია, precedence
საკმარისია, მაგრამ როგორც კი type მეორდება — და რეალურ expressions-ში ის თითქმის ყოველთვის
მეორდება — associativity-ის ერთი გლობალური არჩევანი tree space-ის უმეტესობას წყვეტს.

## შეზღუდვები

- exhaustive agreement `k = 2..6`-მდე ოთხ operator-ზე **არ** არის proof ყველა `k`-სთვის და ყველა
  operator alphabet-ისთვის. ეს არის finite range-ზე გადამოწმებული characterization, არა
  დამტკიცებული theorem.
- characterization ჩამოყალიბებულია მხოლოდ Generation 1 left-associative binary language-ისთვის.
  right-associative operators, unary operators, function application და n-ary nodes დაფარული არ არის.
- ground truth 24 strict grammar-ზეა აღებული; tied control grammar `G0` Claim A-ში მონაწილეობს,
  მაგრამ Claim B-ს reachability განსაზღვრება strict grammars-ზეა დაწერილი.
- leaf sequence ფიქსირებულია და leaf-ების იდენტობა შედეგზე გავლენას არ ახდენს; commutativity ან
  ნებისმიერი semantic equivalence აქ არ განიხილება — ეს წმინდა structural reachability-ია.
- corpus Claim A-სთვის ხუთი expression-ია; exhaustive sweep-ის `130944` შემოწმება ამას აძლიერებს,
  მაგრამ ორივე ისევ flat და მარტივად parenthesized input-ებზეა.

## Evidence-ის კლასიფიკაცია

- Claim A არის **OBSERVED** და exhaustively cross-validated: `125` corpus comparison და `130944`
  sweep comparison, `0` disagreement. მას თან ახლავს symbolic justification recursion-იდან, მაგრამ
  ინდუქციური proof ჩაწერილი არ არის.
- Claim B არის **OBSERVED** და exhaustively cross-validated `587616` (operator-pattern, tree)
  წყვილზე `k = 2..6`-ისთვის, `0` mismatch. constraint rules-ის symbolic justification ზემოთაა
  მოცემული; მისი გავრცელება ყველა `k`-ზე ჯერ hypothesis-ია.
- `92.159` პროცენტიანი unreachability არის დაფიქსირებული measurement ამ დიაპაზონზე და არა asymptotic
  law; `k`-ს ზრდასთან ერთად fraction-ის ზრდა მხოლოდ **observation**-ია.
- polynomial-time decidability კონკრეტული ალგორითმის თვისებაა და კოდიდან პირდაპირ იკითხება.

## ვალიდაცია

გაშვებული ზუსტი commands:

```text
python -m pytest -q tests/test_reachability.py
python -m pytest -q
python -c "from parseatlas.reachability import verify_characterization; print(verify_characterization(6))"
python -c "from parseatlas.reachability import verify_characterization; print(verify_characterization(6, workers=1))"
python -c "from parseatlas.reachability import rightmost_minimum_agreement; print(rightmost_minimum_agreement(['2*t + 1 - t/2','a - b*c + d/e - f','a/b + c*d - e/f + g','a - b - c','(x + 1)/(x - 2)']))"
```

timing block-ის ზუსტი harness (7 გამეორება თითო path-ზე):

```text
python -c "import statistics, time, os; from parseatlas.reachability import verify_characterization as vc, resolve_workers; bench = lambda w: [(t0 := time.perf_counter(), vc(6, workers=w), time.perf_counter() - t0)[2] for _ in range(7)]; par = bench(None); seq = bench(1); print('cpu_count', os.cpu_count(), 'workers', resolve_workers(5456)); print('parallel', [round(x, 2) for x in par], 'median', round(statistics.median(par), 2)); print('sequential', [round(x, 2) for x in seq], 'median', round(statistics.median(seq), 2)); print('speedup', round(statistics.median(seq) / statistics.median(par), 2))"
```

`tests/test_reachability.py`:

```text
19 passed
```

`python -m pytest -q` მთელ repository-ზე:

```text
140 passed
```
