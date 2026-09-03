# ParseAtlas ექსპერიმენტი 0030: associativity როგორც first-class grammar parameter

## მიზანი

ROADMAP Phase 9-ის პირდაპირი კითხვაა: მთელი პროექტი აქამდე associativity-ს `left`-ზე აფიქსირებდა
და მხოლოდ precedence-ს ცვლიდა — რამდენ ახალ semantic diversity-ს იძლევა associativity precedence-თან
შედარებით?

კითხვა რაოდენობრივად მკვეთრია სწორედ იმის გამო, რაც 0020-მა და 0023-მა გაზომა. precedence მარტო
ვერასდროს გასცდება ერთ source-ზე `24` tree-ს (`25`, tied control `G0`-ის ჩათვლით), parenthesizations-ის
რაოდენობა კი Catalan-ის ტემპით იზრდება, და `k = 2..6` დიაპაზონში `587616` (word, tree) წყვილიდან
`541540` — `92.159` პროცენტი — არც ერთი strict precedence grammar-ისთვის მიუწვდომელია. ამიტომ:

```text
ხურავს თუ არა associativity ამ ხარვეზს grammar parameter-ად ქცევისას, და რამდენად?
```

პასუხი, რომელიც ქვემოთ იზომება, ერთი წინადადებით: **ხურავს, მაგრამ მხოლოდ ნაწილობრივ და
სულ უფრო ნაკლებად** — `k = 2`-ზე ხარვეზის `100` პროცენტს, `k = 6`-ზე უკვე მხოლოდ `10.946`
პროცენტს, მთელ დიაპაზონზე კი `62912` tree-ს `541540`-იდან, ანუ `11.617` პროცენტს.

### შედეგი ერთი შეხედვით

Phase 9-ის პასუხი მთელ `k = 2..6` დიაპაზონზე, ერთ ბლოკად:

```text
total trees                 587616
precedence-reachable         46076
with associativity          108988
unreachable before          541540    92.159 %
unreachable after           478628    81.453 %
recovered                    62912    11.617 %   ხარვეზის აღდგენილი წილი
```

registry იზრდება `24 -> 384` — **თექვსმეტჯერ** — და ამის სანაცვლოდ მიუწვდომელი სივრცის
**თორმეტ პროცენტზე ნაკლებს** ყიდულობს უკან. ეს არის Phase 9-ის პასუხი და ის ერთმნიშვნელოვანია.

მეორე რიცხვი, რომელიც ამის გვერდით უნდა იდგეს, semantic მხარეზეა და ის ამ ექსპერიმენტის ყველაზე
მკვეთრი დაკვირვებაა. `3125`-expression-იან 0024 corpus-ზე:

```text
AST forms                   22500 -> 33750      ზუსტად 1.5x
semantic classes            14175 -> 14175      ცვლილება არ არის
sources with a new class                    0   3125-იდან
```

ორმოცდაათი პროცენტით მეტი სინტაქსური მრავალფეროვნება და **არც ერთი ახალი მათემატიკური ობიექტი**.
ეს არის T3-ის დადასტურება სრულიად ახალ განზომილებაში: AST diversity და semantic diversity
დამოუკიდებელი სიდიდეებია. და ეს **არ** არის უნივერსალური — chain probe-ზე, სადაც `-` და `/`
მეორდება, class count ნამდვილად იზრდება, `14 -> 26`. აქედან წესი, რომელიც მთელ ექსპერიმენტს გასდევს:

```text
გამეორებულ-operator-იანი chain-ები       a - b - c,  a / b / c,  x - 1 - x - 1
    associativity ნამდვილ semantic diversity-ს ამატებს        classes 14 -> 26

templated polynomial და rational corpora  0017 corpus,  0024 corpus
    associativity semantics-ს საერთოდ არ ამატებს               classes 14175 -> 14175
    ის მხოლოდ AST form-ებს ამრავლებს                          forms   22500 -> 33750
```

ანუ associativity-ს semantic მოგება **corpus family-ზეა დამოკიდებული და არა grammar space-ის
ზომაზე**: მას იხდის გამეორებული non-associative operator და არა `16`-ჯერ დიდი registry.

`src/parseatlas/grammar.py` და `src/parseatlas/parser.py` **არ** შეცვლილა. გაფართოება
`src/parseatlas/associativity.py`-ში მათ გვერდით აშენდა, ასე რომ ყველა ადრინდელი ექსპერიმენტი
byte-reproducible რჩება, ხოლო ახალი სივრცის all-left slice ძველ registry-ს ზუსტად იმეორებს.

## Space structure

`AssociativeGrammar` არის precedence `levels` პლუს operator-ზე მიბმული side (`left` ან `right`).
levels-ის ფორმა `parseatlas.grammar.Grammar`-ისა ზუსტად იგივეა, ამიტომ tied control grammar `G0`-იც
იმავე სქემაში ჯდება.

აშენებული სივრცის ზუსტი ზომა:

```text
associativity_space()          = 4! * 2^4 = 24 * 16 = 384   strict grammars
control_associativity_space()  = 2^2      =  4              tied G0 variants
all_associativity_grammars()   = 4 + 384  = 388
```

`24` არის strict total precedence orders-ის რაოდენობა, უცვლელი `strict_grammars()`-იდან. `2^4` არის
თითო operator-ის დამოუკიდებელი left/right არჩევანი, და ის **თავისუფალია** სწორედ იმიტომ, რომ strict
ordering-ში ყოველი operator მარტო დგას საკუთარ level-ზე — ანუ ვერც ერთი level ვერ შეურევს side-ებს.

`G0` ამ მხრივ განსხვავებულია: მას ორი level აქვს (`(* /) > (+ -)`), ხოლო ერთ level-ზე ორი
სხვადასხვა side `a + b - c`-ს ნამდვილად ambiguous-ს გახდიდა. ამიტომ `G0`-ის არჩევანი **level-ზეა
და არა operator-ზე**: `2^2 = 4` და არა `2^4 = 16`. mixed level construction-ზე `AssociativeGrammar`
`ValueError`-ს აგდებს და არ ირჩევს თვითნებურ წესს.

Grammar id `G{i:02d}-LLLL` არის Generation 1-ის `G{i:02d}`-ის lift, ხოლო `LLLL` slice — მთელი ძველი
strict registry:

```text
all-left slice = 24 grammars = G01-LLLL .. G24-LLLL
[g.base_grammar() for g in all-left slice] == list(strict_grammars())     True
```

## Claim A': generalized Cartesian split

0023-ის Claim A ამბობდა: flat operator word-ის parse tree იყოფა minimum binding power-ის **ყველაზე
მარჯვენა** პოზიციაზე. ეს rightmost არჩევანი სწორედ left associativity-ს აკოდირებდა. გაფართოებული
წესი:

```text
range [lo, hi)-ზე ავიღოთ minimum binding power lo_p და მისი პოზიციების სია;
    left-associative operator  -> split ყველაზე მარჯვენა პოზიციაზე
    right-associative operator -> split ყველაზე მარცხენა პოზიციაზე
```

parser-ის მხარეს ეს precedence climbing-ის ერთსტრიქონიანი განზოგადებაა: left-associative operator
right operand-ს `power + 1`-ით იძახებს (ტოლი power loop-ს რჩება), right-associative — `power`-ით
(ტოლი power right operand-მა უნდა შთანთქას). `AssociativeParser` მხოლოდ `_expression`-ს ცვლის და
`_primary`-ს (numbers, variables, parentheses) `parseatlas.parser.Parser`-იდან იმემკვიდრებს, ასე რომ
ორი parser ვერ დაშორდება ერთმანეთს.

## Decision procedure

Claim B' — constraints. `T`-ს ყოველ internal node-ზე, რომელიც operator range `[lo, hi)`-ს ყოფს
პოზიცია `s`-ზე root operator `o = w[s]`-ით:

```text
left-associative o:   p(o) <= p(w[t])   for t in [lo, s)     weak
                      p(o) <  p(w[t])   for t in (s, hi)     strict
right-associative o:  p(o) <  p(w[t])   for t in [lo, s)     strict
                      p(o) <= p(w[t])   for t in (s, hi)     weak
```

ანუ associativity **აბრუნებს** იმას, რომელი მხარე იღებს strict constraint-ს და რომელი weak-ს. 0023-ის
procedure აქ განზოგადდა და არა ჩანაცვლდა: all-left assignment-ზე `tree_constraints_with_associativity`
`parseatlas.reachability.tree_constraints`-ს ზუსტად იმეორებს (ეს ცალკე მოწმდება `k = 2..4`-ის ყველა
word-ისა და ყველა tree-სთვის).

Claim C — decomposition. strict total order სხვადასხვა type-ს ყოველთვის სხვადასხვა power-ს აძლევს,
ამიტომ distinct types-ზე `<=` და `<` ერთსა და იმავეს ნიშნავს. აქედან გამომდინარეობს, რომ **distinct
types-ზე შეზღუდული constraint digraph associativity assignment-ზე საერთოდ არ არის დამოკიდებული** —
assignment მხოლოდ self-loops-ს ცვლის, თითო operator type-ისთვის კი self-loops სხვა type-ებისგან
დამოუკიდებელია. ამიტომ:

```text
reachable_with_associativity(T, w)
    <=>  distinct-type digraph acyclic
         AND ვერც ერთი operator type ვერ იკრძალება ორივე მხრიდან

forbid_left(o)  <=> არსებობს node root o-თი, რომელსაც თავისივე type მარჯვნივ უდგას
forbid_right(o) <=> არსებობს node root o-თი, რომელსაც თავისივე type მარცხნივ უდგას
```

ეს `2^m` assignment-ის ძებნას ერთ pass-ად ანგრევს (`m` — word-ში შემხვედრი distinct types).
შედეგად გაფართოებული procedure იმავე ხარჯშია, რაშიც 0023-ისა: constraints `O(k^2)`, cycle detection
operator types-ის რაოდენობაზე კვადრატული. Claim C ცალკე გადამოწმდა brute-force ძებნის წინააღმდეგ
`k = 2..4`-ის ყველა tree-ზე — decomposed გადაწყვეტილება, feasible assignments-ის რაოდენობა და witness
სამივე ემთხვევა.

## Corpus

Claim A'-ს პირდაპირი შემოწმება ჩატარდა 0023-ის იმავე corpus-ზე:

```text
2*t + 1 - t/2
a - b*c + d/e - f
a/b + c*d - e/f + g
a - b - c
(x + 1)/(x - 2)
```

exhaustive cross-validation გაეშვა canonical leaf sequence `a, b, c, ...`-ზე, ოთხი operator-ის
`(+ - * /)` ყველა word-ზე სიგრძით `k = 2..6`, და ყოველი word-ის ყველა Catalan parenthesization-ზე.
ground truth მიიღება რეალური parsing-ით: tree reachable-ია, თუ ის ნამდვილად წარმოიქმნება `384`
გაფართოებული grammar-იდან რომელიმეთი (precedence-only truth — `24` strict grammar-იდან).

coverage ცხრილისთვის გამოყენებულია 0020-ის ზუსტად იგივე ექვსი expression, semantic ცხრილებისთვის კი
ოთხი corpus:

```text
0017 corpus     5 expression      2*t + 1 - t/2, 3*x + 2 - x/3, 2*x*x + 1 - x/2, (x + 1)/(x - 2), (x*x - 1)/(x - 1)
0024 corpus     3125 expression   corpus_matrix.generate_corpus()
0024 probe      10 expression     corpus_matrix.restriction_probe_corpus()
chain probe     10 expression     ამ ექსპერიმენტში განსაზღვრული, იხ. ქვემოთ
```

chain probe deterministic-ია და მიზნობრივად შეიცავს **გამეორებულ non-associative operator-ს**:

```text
a - b - c        a - b - c - d      a / b / c        a / b / c / d      a - b + c - d
a * b / c / d    2*x - 1 - x        a - b*c - d      a/b - c/d - e      x - 1 - x - 1
```

## დაკვირვებული შედეგები

### All-left slice და Claim A'

```text
all_left_agreement (5 source x 25 registered grammar)
    comparison count          125
    parser agreement count    125      AST-იდენტობა parse(source, G)-სთან
    split agreement count     125
    disagreement count          0
    all-left slice reproduces Generation 1     True
```

`split_rule_agreement` მთელ გაფართოებულ სივრცეზე, right-associative grammars-ისა და ხელით ჩაწერილი
parentheses-ის ჩათვლით:

```text
grammar count        388
comparison count    1940
agreement count     1940
disagreement count     0
```

exhaustive sweep-ის შიგნით Claim A' ყოველ word-ზე ყოველი `384` grammar-ისთვის:

```text
split checks          2095104
split disagreements         0
```

### Headline: reachable trees precedence-only vs precedence + associativity

| k | patterns | C(k) | trees | precedence reachable | associativity reachable | precedence coverage % | associativity coverage % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 2 | 32 | 28 | 32 | 87.500 | 100.000 |
| 3 | 64 | 5 | 320 | 196 | 260 | 61.250 | 81.250 |
| 4 | 256 | 14 | 3584 | 1252 | 2000 | 34.933 | 55.804 |
| 5 | 1024 | 42 | 43008 | 7180 | 14192 | 16.695 | 32.999 |
| 6 | 4096 | 132 | 540672 | 37420 | 92504 | 6.921 | 17.109 |

precedence-only სვეტი 0023-ის unreachable ცხრილს ზუსტად ემთხვევა (`4`, `124`, `2332`, `35828`,
`503252` unreachable tree შესაბამისად), ანუ ახალი კოდი ძველ შედეგს ხელახლა აწარმოებს.

ხარვეზის აღდგენა — **ეს არის ის პატიოსანი ფარდობა, რომელსაც ექსპერიმენტი ეძებდა**:

| k | unreachable before | unreachable after | recovered | ხარვეზის აღდგენილი წილი % |
| --- | --- | --- | --- | --- |
| 2 | 4 | 0 | 4 | 100.000 |
| 3 | 124 | 60 | 64 | 51.613 |
| 4 | 2332 | 1584 | 748 | 32.075 |
| 5 | 35828 | 28816 | 7012 | 19.571 |
| 6 | 503252 | 448168 | 55084 | 10.946 |

Aggregate `k = 2..6`:

```text
total_patterns                    5456
total_trees                     587616
precedence reachable             46076     7.841 %
associativity reachable         108988    18.547 %
unreachable before              541540    92.159 %
unreachable after               478628    81.453 %
recovered                        62912
recovered fraction of the gap             11.617 %
total_mismatches                     0
characterization_holds            True
precedence_mismatch_count            0     (0023-ის predicate-თან სრული თანხვედრა)
nesting_violations                   0     (precedence-reachable ყოველთვის ქვესიმრავლეა)
```

**mismatch count არის `0`** `587616` (operator word, tree) წყვილზე. ეს არის card-ის მოთხოვნილი
exhaustive cross-check და ის ისევე ჩატარდა, როგორც 0023-ში: ground truth რეალური parsing-ით,
predicate — მხოლოდ constraint graph-იდან.

დამატებით, distinct trees per word:

| k | precedence (24 grammar-იდან) | associativity (384 grammar-იდან) |
| --- | --- | --- |
| 2 | 1.750 | 2.000 |
| 3 | 3.062 | 4.062 |
| 4 | 4.891 | 7.812 |
| 5 | 7.012 | 13.859 |
| 6 | 9.136 | 22.584 |

`16`-ჯერ მეტი grammar `k = 6`-ზე `2.472`-ჯერ მეტ distinct tree-ს იძლევა.

### Per-expression coverage, 0020-ის corpus-ზე

| expression | leaves | operators | C(k) | precedence | associativity | precedence coverage | associativity coverage | gained |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `a + b*c` | 3 | 2 | 2 | 2 | 2 | 1.0 | 1.0 | 0 |
| `a + b + c` | 3 | 2 | 2 | 1 | 2 | 0.5 | 1.0 | 1 |
| `2*t + 1 - t/2` | 5 | 4 | 14 | 14 | 14 | 1.0 | 1.0 | 0 |
| `a + b*c - d/e` | 5 | 4 | 14 | 14 | 14 | 1.0 | 1.0 | 0 |
| `a - b*c + d/e - f` | 6 | 5 | 42 | 19 | 24 | 0.4523809523809524 | 0.5714285714285714 | 5 |
| `2*x*x + 1 - x/2 + x` | 7 | 6 | 132 | 17 | 42 | 0.12878787878787878 | 0.3181818181818182 | 25 |

```text
mean precedence coverage      0.6801948051948052      (0020-ის mean_strict_coverage-ის იდენტური)
mean associativity coverage   0.814935064935065
```

### Semantic class counts

class key ყველგან პროექტის საერთო `(canonical, domain, excluded_points)` სამეულია
(`parseatlas.analyze`-იდან), ამიტომ `precedence_sensitivity` არის ზუსტად 0017-ის
`S(E) = (classes - 1) / 23`.

| corpus | expressions | precedence classes | associativity classes | ratio | sources with new classes |
| --- | --- | --- | --- | --- | --- |
| 0017 corpus | 5 | 27 | 27 | 1.0 | 0 |
| 0024 template corpus | 3125 | 14175 | 14175 | 1.0 | 0 |
| 0024 restriction probe | 10 | 22 | 31 | 1.4090909090909092 | 7 |
| chain probe | 10 | 14 | 26 | 1.8571428571428572 | 10 |

```text
0017 corpus   mean_precedence_sensitivity     0.19130434782608696    (0017-ის დაფიქსირებული 0.1913)
0024 corpus   mean_precedence_sensitivity     0.1537391304347826
0017 corpus   mean_associativity_sensitivity  0.011488250652741516
0024 corpus   mean_associativity_sensitivity  0.009232375979112271
```

ორი sensitivity რიცხვი **სხვადასხვა მასშტაბზეა** კონსტრუქციით: პირველი `23`-ზე ნორმირდება, მეორე
`383`-ზე. ამიტომ პატიოსანი შედარება არის raw class count და არა ეს ორი რიცხვი ერთმანეთთან.

AST form-ების რაოდენობა კი იზრდება მაშინაც, როცა semantic class count არ იზრდება:

| corpus | precedence AST forms | associativity AST forms |
| --- | --- | --- |
| 0017 corpus | 45 | 59 |
| 0024 template corpus | 22500 | 33750 |
| 0024 restriction probe | 22 | 31 |
| chain probe | 15 | 28 |

`3125`-იან corpus-ზე ეს ზუსტად `1.5`-ჯერ მეტი AST form-ია და **ნული** ახალი semantic class.
კონკრეტული მაგალითი 0017 corpus-იდან:

```text
2*x*x + 1 - x/2     AST forms 14 -> 28      semantic classes 8 -> 8
```

მიზეზი პირდაპირია: ამ corpus-ში გამეორებული operator არის `*`, ხოლო `(2*x)*x` და `2*(x*x)` **ერთი
და იგივე ფუნქციაა**. associativity ორმაგ structural diversity-ს ქმნის, რომელსაც semantic key
სამართლიანად აქრობს.

იქ კი, სადაც გამეორებული operator non-associative-ია, class count ნამდვილად იზრდება:

| source | precedence AST forms | associativity AST forms | precedence classes | associativity classes |
| --- | --- | --- | --- | --- |
| `a - b - c` | 1 | 2 | 1 | 2 |
| `a - b - c - d` | 1 | 2 | 1 | 2 |
| `a / b / c` | 1 | 2 | 1 | 2 |
| `a / b / c / d` | 1 | 2 | 1 | 2 |
| `a - b + c - d` | 2 | 3 | 2 | 3 |
| `a * b / c / d` | 2 | 4 | 1 | 2 |
| `2*x - 1 - x` | 2 | 4 | 2 | 4 |
| `a - b*c - d` | 2 | 3 | 2 | 3 |
| `a/b - c/d - e` | 2 | 4 | 2 | 4 |
| `x - 1 - x - 1` | 1 | 2 | 1 | 2 |

0024-ის restriction probe-ზე იგივე ხდება `10`-იდან `7` expression-ზე, მაგალითად
`x / 1 - x - 1`-ზე `2 -> 4` class.

### სტრუქტურული დაკვირვებები

- 0023-ის კონკრეტული უარყოფითი მაგალითი აღდგება: word `["+", "+"]`-ზე right-leaning tree
  `("+", "a", ("+", "b", "c"))` strict precedence-ით მიუწვდომელია (`p(+) < p(+)` self-loop), ხოლო
  გაფართოებულ სივრცეში reachable-ია ერთადერთი witness-ით `{"+": "right"}`. `allowed_sides` სწორედ
  `{"+": ["right"]}`-ია, ანუ ამ tree-ს left associativity **ეკრძალება**.
- ხოლო 0023-ის cycle-ის მაგალითი **არ** აღდგება: word `["+", "*", "+"]`-ზე
  `("+", ("*", ("+", "a", "b"), "c"), "d")` აწარმოებს `+ -> *` და `* -> +` edges-ს, ანუ აძალებს
  `p(+) == p(*)`-ს. associativity self-loops-ს ცვლის და არა cycles-ს, ამიტომ ეს tree ყველა
  `384` grammar-ისთვისაც მიუწვდომელი რჩება (`acyclic False`, `feasible_assignments 0`).
- `k = 2`-ზე **ყველა** `32` tree reachable ხდება: ორი operator-ის შემთხვევაში ერთადერთი დაბრკოლება
  სწორედ გამეორებული type-ის self-loop-ია, რომელსაც side-ის შეცვლა შლის.
- `a - b - c - d`-ს გაფართოებულ სივრცეშიც მხოლოდ `2` AST form აქვს `C(3) = 5`-იდან: ერთი type-ის
  chain-ს მხოლოდ ორი გლობალური არჩევანი შეესაბამება — სრულად მარცხნივ ან სრულად მარჯვნივ დახრილი.
  შუალედური სამი tree **ვერც ერთი** global associativity rule-ით ვერ მიიღწევა.

## Multicore გაზომვა და default path

ორივე მძიმე ფუნქცია item-ზე დამოუკიდებელი და CPU-bound-ია, ამიტომ ორივე processes-ზე ნაწილდება,
მაგრამ მხოლოდ გაზომილი ზღვრის ზემოთ. worker count მიიღება `os.cpu_count()`-იდან ერთი core-ის
headroom-ით (`parseatlas.reachability.resolve_workers`) და არა hardcoded constant-იდან; `workers=1`
sequential path-ს აიძულებს, explicit `workers=N` კი ზღვარს გვერდს უვლის.

გაზომვა ამ 16-core Windows host-ზე, თითო path-ზე **3 გამეორება**, median-ით. ვალიდაციის სექციაში
გამოქვეყნებულ ორივე harness-ში parallel სვეტს **explicit** worker count აქვს (`cpu_count - 1`) და
არა `workers=None`. ეს არსებითია: `None` სწორედ `PARALLEL_MINIMUM_ITEMS`-ის ქვემოთ სექვენციურ path-ს
ირჩევს, ანუ იმ ზომებზე, რომლებზეც ზღვარი წყდება, `workers=None`-ით parallel branch საერთოდ არ
გაეშვება და პირველ სვეტს გაიმეორებდა. semantic ცხრილის რიცხვები ამ ფორმას ეთანხმება — `5` source-ზე
parallel `6.99` s არის sequential `0.66` s-ის გვერდით, რაც სექვენციური path ვერ იქნებოდა. ორივე ნახევარი
test-ითაა დაფიქსირებული და არა მხოლოდ ტექსტით: `test_small_workloads_stay_sequential_by_measurement`
ამტკიცებს, რომ `verify_associativity_characterization(3)["workers"] == 1` (ანუ `None` `80` word-ზე
სექვენციურია), ხოლო `test_sequential_and_parallel_verification_agree` ამტკიცებს, რომ იმავე `k = 3`-ზე
explicit `workers=2` ნამდვილად `2` worker-ს იღებს და **იმავე** aggregate-ს აბრუნებს.

`verify_associativity_characterization`, tasks = operator words. ეს ცხრილი **მთლიანად თავიდან
გაიზომა** ამ correction run-ში, `k = 6`-ის ჩათვლით, host-ზე `42`-დან `59`-მდე python process-ის
თანაარსებობისას (მანქანას რამდენიმე agent იყოფს), ანუ ეს contended-machine რიცხვებია:

| max_operators | tasks | sequential median | parallel median | speedup |
| --- | --- | --- | --- | --- |
| 2 | 16 | 0.38 s | 13.47 s | 0.03 |
| 3 | 80 | 7.33 s | 20.19 s | 0.36 |
| 4 | 336 | 9.95 s | 11.35 s | 0.88 |
| 5 | 1360 | 39.55 s | 21.25 s | 1.86 |
| 6 | 5456 | 213.49 s | 61.07 s | 3.50 |

`semantic_diversity`, tasks = sources (0024 corpus-ის deterministic prefix-ები). ეს ცხრილი
**საწყისი სესიისაა**, იმავე host-ზე, უფრო მსუბუქი load-ის ქვეშ; correction run-ში ის თავიდან
არ გაზომილა, რადგან სრული re-measurement ამ load-ზე ერთ საათს უახლოვდება `15`-way CPU
contention-ში და იმავე მანქანაზე მომუშავე სხვა agent-ების გაზომვებსაც გააფუჭებდა. harness
ვალიდაციის სექციაშია:

| sources | sequential median | parallel median | speedup |
| --- | --- | --- | --- |
| 5 | 0.66 s | 6.99 s | 0.09 |
| 16 | 2.48 s | 30.09 s | 0.08 |
| 64 | 11.04 s | 13.66 s | 0.81 |
| 96 | 15.79 s | 19.54 s | 0.81 |
| 128 | 22.57 s | 13.09 s | 1.72 |
| 250 | 44.55 s | 24.13 s | 1.85 |
| 500 | 89.67 s | 39.34 s | 2.28 |

constant საწყის სესიაში დაწესდა:

```text
PARALLEL_MINIMUM_ITEMS = 128
```

ორი გამოქვეყნებული ცხრილი break-even-ს **სხვადასხვა ადგილას** აყენებს, და ეს თავისთავად შედეგია:

```text
semantic_diversity, მსუბუქი load     break-even  96-სა და 128 item-ს შორის   (0.81 -> 1.72)
verify, contended                    break-even 336-სა და 1360 item-ს შორის  (0.88 -> 1.86)
```

ანუ `128` არ არის უნივერსალური რიცხვი — ის load-ის ფუნქციაა. constant მაინც რჩება, და მიზეზი თავად
გაზომვაშია: ზღვართან შეცდომა ორივე მიმართულებით იაფია, ზღვრიდან შორს კი ძვირი.

```text
  16 item    contended parallel   35x წაგება      13.47 s vs  0.38 s
 336 item    contended parallel  1.14x წაგება     11.35 s vs  9.95 s
1360 item    contended parallel  1.86x მოგება     21.25 s vs 39.55 s
```

`128` სწორედ იმ ზონაშია, სადაც ცდომილება ორმაგ ციფრში ვერ გადადის; კატასტროფული წაგება მხოლოდ
პატარა workload-ზეა და `128` მას ორივე გაზომვაზე უსაფრთხოდ სცილდება.

ამ ზღვრის ქვემოთ default sequential-ია (`cpu_count 16` -> `workers 1`), ზემოთ — parallel
(`workers 15`). მიზეზი გაზომვაშივე ჩანს: spawned interpreter-ს Windows-ზე ყოველ ჯერზე უწევს
parseatlas-ის sympy import chain-ის გავლა, და ეს ფიქსირებული cost პატარა workload-ს ჭამს.

ეს **განსხვავებული** დასკვნაა, ვიდრე 0020-ის: `operator_pattern_sweep` ყველა გაზომილ ზომაზე
sequential-ად დარჩა, რადგან იქ ერთი item მიკროწამების parsing-ია; აქ კი ერთი item ან `384` parse-ია,
ან sympy `simplify`-ის სრული გაშვება, ამიტომ ზღვრის ზემოთ parallel ნამდვილად იგებს.

სრული `3125`-იანი corpus-ის ერთი parallel გაშვება ამ correction run-ში `108.55` წამია (საწყის
სესიაში იმავე host-ზე `128.29` წამი იყო).

parallelism მხოლოდ სიჩქარეს ცვლის და არა შედეგს: `workers=1` და parallel path ერთსა და იმავე
aggregate dictionary-ს აბრუნებენ (`workers` ველის გარდა). ეს ტოლობა timing-ისგან დამოუკიდებლად
მოწმდება `test_sequential_and_parallel_verification_agree`-სა და
`test_sequential_and_parallel_semantic_diversity_agree`-ში, სადაც ორივე მხარეს `workers` აშკარადაა
მითითებული (`1` და `2`), რათა parallel branch ნამდვილად გაიაროს.

Machine-load caveat: ეს რიცხვები ერთსა და იმავე host-ზეც მერყეობს და გადატანადი არ არის. ამის
ყველაზე პირდაპირი მტკიცებულება ამ correction run-ის შიგნითვეა — ზუსტად იგივე `bench(k, 1)`,
იგივე მანქანა, რამდენიმე წუთის სხვაობით:

```text
k <= 3  sequential median    1.48 s     (correction run-ის პირველი გაშვება)
k <= 3  sequential median    7.33 s     (რამდენიმე წუთის შემდეგ, გამოქვეყნებულ ცხრილში)
```

იმავე მიმართულებით მუშაობს საწყისი სესიის sequential სვეტთან შედარებაც: `k <= 4` `4.90 s` -> `9.95 s`,
`k <= 5` `16.99 s` -> `39.55 s`. `k <= 2` და `k <= 3` ისედაც ძალიან პატარაა იმისთვის, რომ სტაბილური
იყოს — იქ interpreter-ის warm-up და import chain თავად სამუშაოს აჭარბებს.

ამიტომ speedup უნდა წაიკითხოს როგორც რიგი და არა როგორც ზუსტი გამეორებადი რიცხვი, break-even-ის
მდებარეობა კი — როგორც load-ის ფუნქცია და არა როგორც ამ მანქანის მუდმივი.

## ინტერპრეტაცია

პირველი და მთავარი შედეგი: **associativity ხარვეზს ხურავს, მაგრამ ქრებადი ტემპით.** ხარვეზის
აღდგენილი წილი `k`-სთან ერთად თითქმის ნახევრდება ყოველ ნაბიჯზე:

```text
k = 2   100.000 %
k = 3    51.613 %
k = 4    32.075 %
k = 5    19.571 %
k = 6    10.946 %
```

ეს ზუსტად ის სცენარია, რომელიც card-მა წინასწარ დაასახელა, და ის ROADMAP-ის დასკვნას **აძლიერებს**
და არა ასუსტებს. სივრცე `16`-ჯერ გაიზარდა (`24 -> 384`), Catalan-ის რიცხვი კი ექსპონენციალურად
იზრდება. სტრუქტურული ჭერი პირდაპირ იკითხება: ერთ word-ზე reachable trees `<= 384`, ამიტომ

```text
coverage <= 384 / C(k)

C(6)=132    384/C = 2.909   (ჯერ არ არის შემბოჭველი)
C(7)=429    384/C = 0.895
C(8)=1430   384/C = 0.269
C(9)=4862   384/C = 0.079
C(10)=16796 384/C = 0.023
```

შესადარებლად precedence-ის ჭერი `24 / C(k)`: `k = 6`-ზე `0.182`, `k = 8`-ზე `0.017`. რადგან
`C(k+2)/C(k) -> 16`, `16`-ჯერ მეტი grammar ასიმპტოტურად **ზუსტად ორ operator-ს ყიდულობს** expression
სიგრძეში და მეტს არაფერს. associativity კონსტანტური ფაქტორია ექსპონენციალური ზრდის წინააღმდეგ.

```text
full parenthesization space -> associativity-reachable subset -> precedence-reachable subset
```

მეორე შედეგი სტრუქტურულია და ის ხსნის, **რატომ** არის აღდგენა ასეთი მცირე. Claim C-ის დაშლა
ამბობს, რომ associativity **მხოლოდ self-loops-ს ეხება** — ანუ მხოლოდ იმ constraint-ებს, სადაც
operator თავის თავს ხვდება. cycles სხვადასხვა type-ს შორის ხელუხლებელი რჩება. 0023-მა დააფიქსირა,
რომ unreachability მთლიანად გამეორებული operator types-იდან მოდის; ახლა ეს უფრო ზუსტდება:
გამეორებულ type-ს ორი განსხვავებული ეფექტი აქვს და associativity მხოლოდ ერთს შლის.

```text
unreachability-ის ორი წყარო
    self-loop  p(o) < p(o)        <- associativity შლის (side-ის შეცვლით)
    cycle      p(a) < p(b) < p(a) <- associativity ვერაფერს ვერ შვება
```

მესამე შედეგი semantic მხარეზეა და ის ყველაზე მკვეთრი უარყოფითი გაზომვაა ამ ექსპერიმენტისა.
`3125`-იან 0024 corpus-ზე associativity AST form-ების რაოდენობას `22500`-დან `33750`-მდე ზრდის —
ზუსტად `1.5`-ჯერ — და semantic class-ების რაოდენობას **საერთოდ არ ცვლის**: `14175 -> 14175`,
`0` expression ახალი class-ით. მიზეზი ალგებრულია: ამ corpus-ში (და 0017-ის corpus-ში) გამეორებული
operator არის `*`, ხოლო multiplication **მათემატიკურად associative-ია**, ამიტომ ახალი tree იმავე
ფუნქციას იძლევა.

ეს პირდაპირ აგრძელებს 0024-ის დადებით შედეგს — AST diversity და semantic diversity დამოუკიდებელი
სიდიდეებია — და აზუსტებს მას: associativity არის grammar parameter, რომელიც **მხოლოდ structural
diversity-ს იძლევა გარანტირებულად**; semantic diversity-ს ის მაშინ ამატებს, როცა გამეორებული
operator არა-associative operation-ია. chain probe-ზე, სადაც სწორედ `-` და `/` მეორდება, class count
`14`-დან `26`-მდე იზრდება და ათივე expression იგებს; 0024-ის restriction probe-ზე `22 -> 31` და
`10`-იდან `7` იგებს.

აქედან წესი, რომელიც corpus family-ზეა და არა grammar space-ის ზომაზე:

```text
გამეორებული operator არა-associative (-, /)   ->  associativity ამატებს semantic class-ებს
გამეორებული operator associative (*, +)       ->  associativity მხოლოდ AST form-ებს ამატებს
```

ანუ `16`-ჯერ დიდი registry თავისთავად **არაფერს ყიდულობს** semantic მხარეს; მას იხდის corpus-ის
ფორმა. templated polynomial და rational corpora (0017, 0024) ისე აგებულია, რომ გამეორებული operator
`*`-ია, ამიტომ იქ მოგება ზუსტად `0` class-ია `3125` expression-ზე. repeated-operator chain-ები
(`a - b - c`, `a / b / c`) კი პირიქით — იქ ყოველი expression იგებს. ერთი და იმავე grammar
გაფართოებას ორ corpus family-ზე ორი სრულიად სხვადასხვა შედეგი აქვს, და ეს corpus-ის თვისებაა.

პრაქტიკული დასკვნა Phase 9-ისთვის: associativity-ს grammar parameter-ად გატანა **ღირს** — ის
`62912` აქამდე მიუწვდომელ tree-ს ხსნის, decision procedure-ს ხარჯს არ უმატებს (Claim C), და
`a - b - c` ტიპის expression-ებზე ნამდვილ semantic diversity-ს ამატებს. მაგრამ ის **არ არის** ის,
რაც parenthesization space-ს დაფარავს. წყვილების `81.453` პროცენტი ისევ მიუწვდომელია, და ეს წილი
`k`-სთან ერთად ისევ იზრდება. explicit grouping-ის ძრავა კვლავ საჭიროა.

## შეზღუდვები

- exhaustive agreement `k = 2..6`-მდე ოთხ operator-ზე **არ** არის proof ყველა `k`-სთვის და ყველა
  alphabet-ისთვის. ეს finite range-ზე გადამოწმებული characterization-ია, არა დამტკიცებული theorem.
  იგივე ეხება Claim C-ს: მისი brute-force შემოწმება `k <= 4`-ზეა.
- associativity აქ **გლობალურია** operator type-ზე: ერთი operator მთელ expression-ში ერთსა და იმავე
  side-ს ატარებს. per-occurrence ან context-dependent associativity არ არის განხილული და სწორედ ის
  იქნებოდა შემდეგი გაფართოება.
- non-associative (`a - b - c` აკრძალული) და chained comparison-ის სტილის associativity-ები არ არის
  მოდელირებული; არჩევანი მხოლოდ ორობითია, `left` ან `right`.
- mixed-associativity level აკრძალულია construction-ზე. ეს გააზრებული არჩევანია (ambiguity), მაგრამ
  ის ნიშნავს, რომ tied levels-ის სივრცე `G0`-სთვის `4`-ია და არა `16`.
- `384` სივრცე strict precedence orders-ზეა აშენებული; tied-level grammars associativity-ით
  სისტემატურად არ არის ჩამოთვლილი (მხოლოდ `G0`-ის `4` ვარიანტი).
- semantic შედეგი corpus-dependent-ია: `0` ახალი class `3125` expression-ზე ნიშნავს, რომ **ამ
  corpus-ის templates**-ში გამეორებული operator `*`-ია. სხვა corpus-ზე რიცხვი სხვა იქნება, რასაც
  chain probe პირდაპირ აჩვენებს.
- leaf sequence ფიქსირებულია და commutativity არ განიხილება; coverage წმინდა structural
  reachability-ია.
- multicore გაზომვა ერთ host-ზეა და ორივე გაშვება სხვა agent-ების load-ის ქვეშ ჩატარდა; `128`-ის
  ზღვარი ამ machine-ის გაზომვაა და არა უნივერსალური constant. მეტიც, ორ გაშვებას შორის break-even
  თავად გადაინაცვლა, ანუ ის ერთი მანქანის მუდმივიც არ არის — load-ის ფუნქციაა.
- `semantic_diversity`-ის timing ცხრილი საწყისი სესიისაა და correction run-ში თავიდან არ გაზომილა;
  მისი harness გამოქვეყნებულია, მაგრამ თავად რიცხვები უფრო მსუბუქი load-ის არიან, ვიდრე `verify`-ის
  ცხრილი. ორი ცხრილის speedup-ები ამიტომ პირდაპირ არ ედრება ერთმანეთს.

## Evidence-ის კლასიფიკაცია

- ის, რომ all-left slice Generation 1 registry-ს ზუსტად იმეორებს, არის **OBSERVED** `125`
  AST-იდენტობის შედარებაზე და ცალკე test-ით დაფიქსირებული.
- Claim A' არის **OBSERVED** და exhaustively cross-validated: `1940` corpus comparison (parentheses-ის
  ჩათვლით) და `2095104` sweep comparison, `0` disagreement.
- Claim B' არის **OBSERVED** და exhaustively cross-validated `587616` (operator word, tree) წყვილზე
  `k = 2..6`-ისთვის, `0` mismatch. constraint rules-ის symbolic justification ზემოთაა; მისი გავრცელება
  ყველა `k`-ზე hypothesis-ია.
- Claim C (decomposition) აქვს symbolic justification distinct-type ტოლობიდან და არის **OBSERVED**
  brute-force ძებნის წინააღმდეგ `k <= 4`-ზე; ის ხსნის, რატომაა გაფართოებული procedure იმავე ხარჯში.
- `11.617` პროცენტი აღდგენილი ხარვეზი და `81.453` პროცენტი დარჩენილი unreachability არის ამ
  დიაპაზონზე დაფიქსირებული measurements და არა asymptotic laws.
- `coverage <= 384 / C(k)` ამ registry-სთვის **symbolically justified** არის, ისევე როგორც ის, რომ
  `C(k+2)/C(k) -> 16` ამ `16`-ჯერ ზრდას ორ operator-ად თარგმნის.
- `0` ახალი semantic class `3125` expression-ზე არის **OBSERVED negative result** ამ corpus-ზე; მისი
  ალგებრული ახსნა (`*` associative-ია) symbolic-ია, მაგრამ ის, რომ ეს ყველა corpus-ზე ასე იქნება,
  არ არის claimed — chain probe საპირისპიროს აჩვენებს.
- multicore break-even არის ამ host-ზე გაზომილი **observation** და ის **load-ზეა დამოკიდებული**:
  მსუბუქმა `semantic_diversity` გაზომვამ ის `96..128` item-ს შორის დააყენა, contended `verify`
  გაზომვამ კი `336..1360`-ს შორის.
  `PARALLEL_MINIMUM_ITEMS = 128` ამიტომ **არჩევანია და არა გაზომილი მუდმივი**; მისი გამართლება ის
  არის, რომ ზღვართან შეცდომის ფასი ორივე გაზომვაზე მცირეა, კატასტროფული წაგება კი ბევრად ქვემოთაა.
- headline-ის ყველა რიცხვი (`587616`, `46076`, `108988`, `541540`, `478628`, `62912`, `92.159 %`,
  `81.453 %`, `11.617 %`, `total_mismatches 0`) და ოთხივე semantic corpus ამ correction run-ში
  ხელახლა გაიზომა გამოქვეყნებული command-ებით და ციფრმა-ციფრში დაემთხვა.

## ვალიდაცია

გაშვებული ზუსტი commands:

```text
python -m pytest -q tests/test_associativity.py
python -m pytest -q
python -c "from parseatlas.associativity import all_left_agreement; print({k: v for k, v in all_left_agreement(['2*t + 1 - t/2','a - b*c + d/e - f','a/b + c*d - e/f + g','a - b - c','(x + 1)/(x - 2)']).items() if k != 'disagreements'})"
python -c "from parseatlas.associativity import split_rule_agreement; print({k: v for k, v in split_rule_agreement(['2*t + 1 - t/2','a - b*c + d/e - f','a/b + c*d - e/f + g','a - b - c','(x + 1)/(x - 2)']).items() if k != 'disagreements'})"
python -c "from parseatlas.associativity import verify_associativity_characterization as v; r = v(6); [print(b) for b in r['per_k']]; print({k: x for k, x in r.items() if k not in ('per_k', 'mismatch_examples')})"
python -c "from parseatlas.associativity import verify_associativity_characterization as v; print(v(6, workers=1)['total_mismatches'])"
python -c "from parseatlas.associativity import coverage_report_with_associativity as c; r = c(('a + b*c','a + b + c','2*t + 1 - t/2','a + b*c - d/e','a - b*c + d/e - f','2*x*x + 1 - x/2 + x')); [print(i) for i in r['expressions']]; print(r['mean_precedence_coverage'], r['mean_associativity_coverage'])"
python -c "from parseatlas.associativity import semantic_diversity as s; print({k: v for k, v in s(('2*t + 1 - t/2','3*x + 2 - x/3','2*x*x + 1 - x/2','(x + 1)/(x - 2)','(x*x - 1)/(x - 1)'), workers=1).items() if k != 'expressions'})"
```

ოთხივე semantic corpus ერთი script-იდან გაეშვა `if __name__ == "__main__":` guard-ით, რადგან
Windows-ის `spawn` start method-ზე ყოველი child caller-ის `__main__`-ს ხელახლა იმპორტავს. სწორედ ეს
script აწარმოებს ზემოთ მოცემულ class და AST-form ცხრილებს:

```python
import time

from parseatlas.associativity import semantic_diversity
from parseatlas.corpus_matrix import generate_corpus, restriction_probe_corpus

CORPUS_0017 = (
    "2*t + 1 - t/2",
    "3*x + 2 - x/3",
    "2*x*x + 1 - x/2",
    "(x + 1)/(x - 2)",
    "(x*x - 1)/(x - 1)",
)
CHAIN_PROBE = (
    "a - b - c",
    "a - b - c - d",
    "a / b / c",
    "a / b / c / d",
    "a - b + c - d",
    "a * b / c / d",
    "2*x - 1 - x",
    "a - b*c - d",
    "a/b - c/d - e",
    "x - 1 - x - 1",
)


def report(name, sources):
    t0 = time.perf_counter()
    result = semantic_diversity(sources)
    elapsed = time.perf_counter() - t0
    forms_p = sum(e["precedence_ast_forms"] for e in result["expressions"])
    forms_a = sum(e["associativity_ast_forms"] for e in result["expressions"])
    print(
        name,
        "sources", result["source_count"],
        "classes", result["total_precedence_classes"], "->", result["total_associativity_classes"],
        "ratio", result["class_ratio"],
        "new", result["sources_with_new_classes"],
        "forms", forms_p, "->", forms_a,
        "sensitivity", result["mean_precedence_sensitivity"], result["mean_associativity_sensitivity"],
        "elapsed", round(elapsed, 2),
        flush=True,
    )


if __name__ == "__main__":
    report("0017", CORPUS_0017)
    report("probe", tuple(record["source"] for record in restriction_probe_corpus()["expressions"]))
    report("chain", CHAIN_PROBE)
    report("0024", tuple(record["source"] for record in generate_corpus()["expressions"]))
```

მისი გამოსავალი ამ correction run-ში, სიტყვასიტყვით:

```text
0017  sources    5  classes    27 ->    27  ratio 1.0                 new  0  forms    45 ->    59  elapsed   0.79
probe sources   10  classes    22 ->    31  ratio 1.4090909090909092  new  7  forms    22 ->    31  elapsed   0.20
chain sources   10  classes    14 ->    26  ratio 1.8571428571428572  new 10  forms    15 ->    28  elapsed   0.42
0024  sources 3125  classes 14175 -> 14175  ratio 1.0                 new  0  forms 22500 -> 33750  elapsed 108.55
```

ანუ headline-ის ორივე semantic რიცხვი — `22500 -> 33750` AST form და `14175 -> 14175` semantic class
`0` ახალი class-ით — ამ სესიაში ხელახლა გაიზომა და ზუსტად დაემთხვა.

`verify_associativity_characterization`-ის timing harness, `3` გამეორება თითო path-ზე, სვეტები
`k`, sequential median, parallel median. parallel სვეტი **explicit** worker count-ს იღებს
(`cpu_count - 1`) და არა `workers=None`-ს, რადგან `None` `PARALLEL_MINIMUM_ITEMS`-ის ქვემოთ
სექვენციურ path-ს ირჩევს — `k <= 2` (`16` word) და `k <= 3` (`80` word) სწორედ იქ არიან, ანუ
`None`-ით ეს ორი row საერთოდ ვერ გაზომავს parallel branch-ს:

```text
python -u -c "import os, statistics, time; from parseatlas.associativity import verify_associativity_characterization as v; par = max(1, (os.cpu_count() or 1) - 1); bench = lambda k, w: [(t0 := time.perf_counter(), v(k, workers=w), time.perf_counter() - t0)[2] for _ in range(3)]; [print(k, round(statistics.median(bench(k, 1)), 2), round(statistics.median(bench(k, par)), 2)) for k in (2, 3, 4, 5, 6)]"
```

`semantic_diversity`-ის timing harness იმავე ფორმისაა, ოღონდ script file-იდან, `if __name__`
guard-ით (Windows `spawn`), რადგან tasks აქ 0024 corpus-ის deterministic prefix-ებია:

```python
import os
import statistics
import time

from parseatlas.associativity import semantic_diversity
from parseatlas.corpus_matrix import generate_corpus


def bench(sources, workers):
    samples = []
    for _ in range(3):
        t0 = time.perf_counter()
        semantic_diversity(sources, workers=workers)
        samples.append(time.perf_counter() - t0)
    return statistics.median(samples)


if __name__ == "__main__":
    corpus = tuple(record["source"] for record in generate_corpus()["expressions"])
    par = max(1, (os.cpu_count() or 1) - 1)
    for n in (5, 16, 64, 96, 128, 250, 500):
        sources = corpus[:n]
        print(n, round(bench(sources, 1), 2), round(bench(sources, par), 2), flush=True)
```

`tests/test_associativity.py`:

```text
37 passed in 73.98s (0:01:13)
```

`python -m pytest -q` მთელ repository-ზე, ორი თანმიმდევრული გაშვება ამ correction run-ში:

```text
495 passed in 366.72s (0:06:06)
1 failed, 494 passed in 1435.71s (0:23:55)
```

მეორე გაშვების ერთადერთი წაგება ამ ექსპერიმენტს **არ ეხება**: დაეცა
`tests/test_scale_atlas.py::test_structural_path_calls_no_sympy` — სხვა card-ის ფაილი, რომელიც
სუიტის მსვლელობისას იწერებოდა (`src/parseatlas/scale_atlas.py`-ის mtime გაშვების დაწყების შემდეგაა).
იზოლირებულად ის იმავე წუთს გადის (`1 passed in 3.73s`), ხოლო `parseatlas.scale_atlas`
`parseatlas.associativity`-ს საერთოდ არ იმპორტავს. ამ card-ის ფაილებში ცვლილება მხოლოდ
`src/parseatlas/associativity.py`-ის კომენტარებში და ამ REPORT-შია.

მთლიანი suite-ის რიცხვი ამ გაშვების მომენტისაა; repository-ში პარალელურად სხვა ექსპერიმენტების
modules და tests ემატება, ამიტომ total იზრდება, ხოლო `tests/test_associativity.py`-ის `37 passed`
ამ ექსპერიმენტის ფიქსირებული წვლილია.
