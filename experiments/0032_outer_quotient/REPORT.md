# ParseAtlas ექსპერიმენტი 0032: outer function quotient

## მიზანი

მფლობელის კითხვა იყო: `sin`-ის ქვეშ დაფიქსირებული `8` semantic class სხვა outer function-ისთვისაც მიიღება თუ არა.

პასუხი: **`8` ეკუთვნის inner token sequence-ს და არა `sin`-ს.**

ამ პასუხს ორი ერთმანეთისგან განსხვავებული claim ამაგრებს და მათი აღრევა იყო ამ ექსპერიმენტის პირველი ვერსიის შეცდომა. ისინი აქ ცალკეა, რადგან **ერთი მათგანი მართალია, მეორე კი გაზომვამ გააქარწყლა.**

| | claim | სტატუსი |
|---|---|---|
| **მათემატიკური** | თუ ორი inner argument ერთი და იგივე function-ია, მაშინ `f` მათზე ერთსა და იმავეს იძლევა; ე.ი. outer function მხოლოდ merge-ს აკეთებს, `C_f(S) <= C_inner(S)` | **მართალია.** ერთსტრიქონიანი proof, ქვემოთ |
| **გაზომილი** | ParseAtlas-ის *implementation*-ის key ამ coarsening-ს ინარჩუნებს | **გაქარწყლდა.** `278` violation `1273` წყვილზე, root cause `functions.py`-ში, NF-2026-00004 |

გაქარწყლება მათემატიკის შესახებ არაფერს ამბობს — ის key-ის შესახებ finding-ია. fix-ის შემდეგ იმავე `1273` წყვილზე violation `0`-ია.

### მათემატიკური claim

ავიღოთ token sequence `S`. grammar `g` აწარმოებს AST `A_g`-ს, რომლის denotation `v_g` არის partial function reals-ზე. inner partition არის `g -> v_g` map-ის kernel. თუ `v_g == v_h`, მაშინ function application-ის განსაზღვრებით `f . v_g == f . v_h`. ე.ი. relation "იგივე value `f`-ის შემდეგ" **შეიცავს** relation-ს "იგივე value", inner partition **refines** outer-ს, და outer partition არის inner-ის coarsening:

```text
v_g == v_h  =>  f(v_g) == f(v_h)      =>      C_f(S) <= C_inner(S)
```

აქედან ორი შედეგი:

- outer function inner class-ს **მხოლოდ აერთიანებს**; ვერასოდეს ყოფს.
- `C_f == C_inner` მაშინ და მხოლოდ მაშინ, როცა `f` injective-ია observed value set `{v_g}`-ზე.

ეს proof-ია და measurement მას ვერაფერს დაამატებს.

### გაზომილი claim

ParseAtlas denotation-ებს პირდაპირ არ ადარებს. ის ადარებს canonical triple-ს `(canonical form, domain, excluded points)`, და ზემოთ მოყვანილი proof გაზომილ partition-ებზე მხოლოდ მაშინ გადადის, თუ ეს triple **denoted value-ის** function-ია და არა parse tree-ის. `quotient_check` სწორედ key-ს ამოწმებს და არა theorem-ს. სწორედ ეს არის falsifiable ნაწილი — და სწორედ ის დაემხო.

## შედეგი: key-მა split დაამზადა

**რომელი მიმართულებით ტყდება.** outer key-ის `domain` სლოტი inner key-ის constant `"R"`-ზე **უფრო წვრილია** (finer). ამ ექსპერიმენტის პირველი ვერსია წერდა, რომ ეს "უფრო მკაცრია, და ეს ის მიმართულებაა, რომელიც მნიშვნელოვანია: coarsening, რომელიც უფრო მკაცრ key-ს გაუძლებს, უფრო ძლიერი შედეგია". **ეს ზუსტად პირუკუა.** coarsening მხოლოდ **split**-ით შეიძლება დაირღვეს, split-ს კი მხოლოდ ის key გამოიწვევს, რომელიც inner key-ის მიერ გაერთიანებულ grammar-ებს ჰყოფს. უფრო წვრილი outer key ერთადერთი საფრთხეა claim-ისთვის და არა მისი დამატებითი მტკიცებულება.

**Root cause (NF-2026-00004).** `src/parseatlas/functions.py`-ის `_property_summary` outer function-ს **raw** parse tree-ზე აკომპოზირებდა:

```python
properties["real_domain"] = str(continuous_domain(OUTER_FUNCTIONS[name](expression), variable, S.Reals))
```

სადაც `expression` არის `to_sympy(parse(source, grammar))`, არასოდეს simplified — მაშინ როცა იმავე record-ის canonical slot და inner key `simplify(...)`-ს იყენებდა. ე.ი. **domain სლოტი parse tree-ის function იყო და არა denoted value-ის** — ზუსტად ის failure, რისი აღკვეთაც `(F, D, U)` discipline-ის მიზანია, თვით discipline-ის implementation-ის შიგნით.

მინიმალური reproducer, corpus-შია, ე.ი. ყოველ run-ზე იზომება:

```text
quotient_check("3 * 2 - t / 2 - t", "log")
  fix-მდე:        is_coarsening False, C_inner 4, C_f 5, merge_count -1
  fix-ის შემდეგ:  is_coarsening True,  C_inner 4, C_f 4, merge_count 0
```

inner class `C02` (canonical `3`, key `['3', 'R', ('2',)]`, 8 grammar) ორად იხლიჩებოდა:

```text
F02  log(3) | Union(Interval.open(-oo, 2), Interval.open(2, oo)) | G01 G07 G09 G10
F03  log(3) | Reals                                             | G02 G08 G11 G12
```

მიზეზი: `3 * 2 - t / 2 - t`-ის რვა reading-იდან ოთხი ტოვებს tree-ს `(6 - 3*t)/(2 - t)` (გაუქარვებელი removable singularity), ოთხი კი `Integer(3)`-ს, რადგან SymPy ერთ shape-ზე construction-ისას აქარწყლებს ფაქტორს და მეორეზე არა. **ორივე reading excluded point `2`-ს ატარებს**, ე.ი. validity restriction სადავო არასოდეს ყოფილა; მხოლოდ ის სლოტი არ თანხმდებოდა, რომელსაც value უნდა აღეწერა.

**იგივე defect canonical სლოტსაც სწვდებოდა.** `simplify(f(raw_tree))` და `simplify(f(raw_tree'))` ერთი value-ის ორ დაწერაზე სხვადასხვა fixed point-ზე ჩერდება: `log` `t * t - 3 / 2`-ზე იძლეოდა როგორც `log(t*(t - 3)) - log(2)`-ს, ისე `log(t*(t - 3)/2)`-ს; `abs` `1 + t + t * 2 / t`-ზე — როგორც `2*Abs(2 + 1/t)`-ს, ისე `Abs(4 + 2/t)`-ს. ეს card-ის აღწერაში არ იყო და გაზომვისას გამოჩნდა.

**Fix.** domain და composed canonical ორივე ერთსა და იმავე **canonicalised argument**-ზე ითვლება:

```python
argument = canonical_argument(to_sympy(inner_node))     # simplify(...) ერთხელ, grammar-ზე
outer = simplify(OUTER_FUNCTIONS[function_name](argument))
properties = _property_summary(argument, variable, function_name)
```

parse tree-ის validity restriction ცალკე და უცვლელად მიდის `inner_excluded_points`-ში, სადაც removable singularity ისედაც ეწერა. `outer_real_domain` accessor-იც იმავე გზაზე გადავიდა, თორემ report-ისთვის ციტირებული რიცხვი atlas-ის რიცხვს არ დაემთხვეოდა.

`argument_period`-ის `pi/|a|` (tan) და `2*pi/|a|` (sin, cos) უცვლელია და pinned test-ით არის დაფარული.

## რატომ ვერ ირთვებოდა ეს check პირველ corpus-ზე

პირველი ვერსია `0` violation-ს იძლეოდა `260` წყვილზე და ამას claim-ის მხარდაჭერად კითხულობდა. **ეს მხარდაჭერა არ იყო.** იმ corpus-ის ყოველი inner class-ის ყველა grammar `srepr`-იდენტურ raw expression-ს იძლეოდა, ე.ი. outer key ყოველ inner class-ზე trivially constant იყო და decisive check ვერ ირთვებოდა. **ნული check-იდან, რომელიც ვერ ირთვება, corpus-ის ფაქტია და არა key-ის.**

Corpus ახლა შეიცავს `4` **residue source**-ს, სადაც ორი grammar მაინც ერთსა და იმავე value-ს სტრუქტურულად განსხვავებული tree-ით denote-ს აკეთებს:

| source | inner class | canonical | raw tree-ები | grammar |
|---|---|---|---|---|
| `3 * 2 - t / 2 - t` | C02 | `3` | `3`, `(6 - 3*t)/(2 - t)` | 8 |
| `1 + t + t * 2 / t` | C02 | `4 + 2/t` | `(4*t + 2)/t`, `2*(2*t + 1)/t` | 12 |
| `t * t - 3 / 2` | C02 | `t*(t - 3)/2` | `t*(t - 3)/2`, `t*(t/2 - 3/2)` | 8 |
| `2*(t - 1)/(t - 1)` | C01 | `2` | `2`, `(2*t - 2)/(t - 1)` | 25 |

პირველი სამი paren-free-ია (residue მხოლოდ precedence-იდან მოდის, bracket-ებიდან არა); მეოთხე uncancelled quotient-ია. `test_the_corpus_can_actually_break_the_coarsening_check` ამტკიცებს, რომ ზუსტად ეს ოთხი source აწარმოებს residue-ს corpus-ში, ე.ი. coarsening test აღარ არის vacuous.

## Falsification: violation count fix-მდე და fix-ის შემდეგ

Review-მ იპოვა `114` violation `208` წყვილზე `16` source-ზე. ქვემოთ ეს დამოუკიდებლად აღდგენილია და გაფართოებულია.

**Residue source-ების პოვნა.** paren-free token sequence-ები `4` და `5` atom-ით, atom-ები `{1, 2, 3, (4), t}`-დან, ოპერატორები `{+, -, *, /}`, სულ ცოტა ერთი `/` (residue-ს division სჭირდება). თითოეულ candidate-ზე `25` grammar-ის raw reading დაჯგუფდა simplified value-ით და კითხვა იყო: აქვს თუ არა რომელიმე ჯგუფს ერთზე მეტი `srepr`.

| scan | დათვლილი candidate | residue source | წილი |
|---|---:|---:|---:|
| A (atom `{1,2,3,t}`) | 1200 | 28 | 2.3% |
| B (atom `{1,2,3,4,t}`, სხვა seed) | 2600 | 64 | 2.5% |

ორივე scan division-ის შემცველ paren-free sequence-ებზეა შემოსაზღვრული — ეს არის ის denominator, რომელსაც ზემოთა წილები ეხება, და არა ყველა paren-free sequence.

**Sweep-ები.** scan A-ს `28` source + reproducer + `5` parenthesised residue source = `34` source; scan B-ს `64` source. ორივე `13` outer function-ზე.

| sweep | source | წყვილი | violation fix-მდე | violation fix-ის შემდეგ |
|---|---:|---:|---:|---:|
| A | 34 | 442 | **126** (32 source) | **0** |
| B (დამოუკიდებელი) | 64 | 831 | **152** (59 source) | **0** |
| გაერთიანება (overlap 0) | **98** | **1273** | **278** (91 source) | **0** |

fix-მდელი რიცხვები sweep A-სთვის რეალური pre-fix build-ის გაშვებაა. sweep B-სთვის pre-fix key emulation-ით აღდგა (`simplify(f(raw))` და `continuous_domain(f(raw))`, working tree-ს გარეთ); emulation sweep A-ზე კალიბრირდა და ზუსტად იმავე `126 / 442`-ს და `32` violating source-ს დააბრუნა.

**რომელი სლოტი ატარებდა parse tree-ს.** `278` violating წყვილის კლასიფიკაცია:

| | წყვილი |
|---|---:|
| domain სლოტი ჩართულია | 208 |
| canonical სლოტი ჩართულია | 81 |
| მხოლოდ domain სლოტი | 197 |
| მხოლოდ canonical სლოტი | 70 |
| ორივე | 11 |
| გახლეჩილი inner class სულ | 294 |

**Post-fix.** იმავე `98` source-ზე, იმავე `13` function-ზე: `coarsening_failures` `0`, `split_pairs` `0`, უარყოფითი `class_count_delta` `0`, `total_merges` `+20`. **fix სრულია ამ გაზომვის ფარგლებში.**

**ერთი წყვილი ვერ იზომება — fix-მდეც და fix-ის შემდეგაც.** `t / 1 - 1 + 2 * 2` × `exp`: ერთი grammar ამ sequence-ს `t/(1 - 1)`-ად კითხულობს, რაც `zoo*t + 4`-ს იძლევა, და `simplify(exp(zoo*t + 4))` SymPy-ში `TypeError: Invalid NaN comparison`-ს აგდებს (`exptrigsimp` -> `rewrite(cos)`). ეს pre-existing SymPy ქცევაა, ორივე რეჟიმში იდენტური, და ამ card-ის ცვლილებას არ უკავშირდება. ამიტომ ზემოთ ყველგან წერია `1273` და არა `1274` — ეს წყვილი არც coarsening-ად და არც violation-ად არ ითვლება.

## Unguarded aggregate: `-130` merge

`quotient_check` `merge_count`-ს `C_inner - C_f`-ით ითვლიდა, clamp-ის გარეშე. split-ზე ეს რიცხვი **უარყოფითი** ხდება, და `merge_report` მას შემდეგ ჯამავდა `total_merges`-ში, `mean_merge_count`-ში, `merges_anywhere`-ში, `capability_unrealised`-სა და `contradicts_algebra`-ში. ე.ი. per-function summary აქტიურად შემცდარი ხდებოდა **ზუსტად მაშინ**, როცა ყველაზე მნიშვნელოვანი finding ირთვებოდა.

Sweep A-ზე (34 residue source, 442 წყვილი) გაზომილი pre-fix summary:

| მაჩვენებელი | pre-fix მნიშვნელობა | რატომ არის შემცდარი |
|---|---|---|
| `total_merges` (სულ) | `-130` | უარყოფითი merge რაოდენობა |
| `tan.mean_merge_count` | `-1.088` | `-37 / 34`, "საშუალოდ მინუს ერთი merge source-ზე" |
| `cos.merges_anywhere` | `False` | `max_merge_count` იმავე run-ში `1`-ია — parity merge იყო და გაქრა |
| `abs.merges_anywhere` | `False` | იგივე; `-18` ჩრდილავს |
| `square.merges_anywhere` | `False` | იგივე |
| `sin`, `tan` `.capability_unrealised` | `True` | "არსად არ merge-ავს" დაუზომავი წყვილებით სავსე sweep-იდან |

**Fix.**

- `merge_count` ახლა **merge სტრუქტურიდან** გამოითვლება (რამდენი inner class ჩაჯდა საზიარო outer class-ში) და არა class რაოდენობების სხვაობიდან. coarsening-ზე ორივე განსაზღვრება ერთსა და იმავე რიცხვს იძლევა და test suite ამ თანხვედრას ამოწმებს ყოველ `312` წყვილზე.
- violating წყვილზე `merge_count` არის `None` და `merges` არის `[]`. გახლეჩილ partition-ში "outer class ორ inner class-ს იტევს" აღარ ნიშნავს, რომ ისინი გაერთიანდა, ამიტომ merge-ის დასახელებაზე უარის თქმა სწორი პასუხია და არა ფრთხილობა.
- ნედლი სხვაობა რჩება როგორც `class_count_delta` — **diagnostic და არა merge count**; ის ზუსტად split-ზე ხდება უარყოფითი. ემატება `split_count` და report-ის დონეზე `split_pairs`.
- `merge_report`-ის ყველა merge aggregate მხოლოდ coarsening წყვილებზე გროვდება. `mean_merge_count`-ის მნიშვნელი არის `coarsening_pairs` და არა `sources`.
- ახალი per-function ველი `merge_evidence_complete` ამბობს, დაუზომავი წყვილის გარეშე იყო თუ არა sweep. `capability_unrealised` მას მოითხოვს: "არსად არ merge-ავს" დასკვნა არ გამოგვაქვს იმ sweep-იდან, რომლის ნაწილი ვერ გავზომეთ.

`test_aggregates_refuse_to_count_merges_from_a_violating_pair` ამ არითმეტიკას მინიატურაში აღადგენს: fabricated split (`-1`) პლუს ნამდვილი parity merge (`+1`), და ამტკიცებს, რომ `total_merges` არის `1` და არა `0`, ხოლო `merges_anywhere` — `True` და არა `False`.

## Quotient structure

`src/parseatlas/outer_quotient.py` ზომავს ორ partition-ს ერთი და იმავე key discipline-ით.

- `inner_partition(source)` — `analyze_expression`-ის `equivalence_classes`, key `(canonical, domain, excluded_points)`, `domain` სლოტში constant `"R"`.
- `outer_partition(source, function_name)` — `analyze_outer_functions`-ის per-grammar row-ები, დაჯგუფებული key-ით `(canonical, real_domain, excluded_points)`. outer layer აქ ხელახლა არ არის დაწერილი: composed canonical form, period, frequency და domain ყველა `functions.py`-დან მოდის.
- `quotient_check(source, function_name)` — პირდაპირ ამოწმებს, რომ ყოველი inner class ზუსტად ერთ outer class-ში ხვდება. თუ inner class ორ outer class-ს აღწევს, ეს **violation**-ია და სრულად იბეჭდება: inner key, grammars და თითოეული მიღწეული outer key.

outer key inner key-ზე **უფრო წვრილია**, რადგან `domain` სლოტში `continuous_domain` დგას და არა constant `"R"`. ეს არ არის უფრო ძლიერი test — ეს არის ერთადერთი სლოტი, რომელსაც split-ის დამზადება შეუძლია. ამიტომ მას ერთი მკაცრი მოთხოვნა აქვს: **denoted value-ის function უნდა იყოს.**

## Corpus

`24` inner token sequence, founding-ის ჩათვლით. ცვლადი ყველგან `t`, რადგან `functions.py` frequency-სა და period-ს `t`-ით differentiate-ს აკეთებს.

```text
affine:                     2*t + 1 - t/2        (founding)
                            1 - 2 + t
                            3*t - 2 + 1
                            t/2 + 1 - 2*t
                            1 + 2*t - 3
affine, negation-producing: 2 - 2 + t
                            4 - 4 + 3*t
quadratic:                  2*t*t + 1 - t/2
                            t*t - 3*t + 2
                            t*t*2 - t - 1
quadratic, negation:        3 - 3 + t*t
rational:                   (t + 1)/(t - 2)
                            1/t + 2 - t
                            t/t + 2*t - 1
                            2/t - 1/t + t
                            t/(t + 1) - 2
rational, negation:         5 - 5 + 1/t
mixed chain:                1 - 2*t/4 + 3*t
                            2*t*3 - 4/t + 1
                            1 - t/2*2 + t
residue (NF-2026-00004):    3 * 2 - t / 2 - t
                            1 + t + t * 2 / t
                            t * t - 3 / 2
                            2*(t - 1)/(t - 1)
```

outer function set სრულია: `sin, cos, tan, exp, log, sqrt, abs, asin, acos, atan, reciprocal, square, cube`.

`c - c + u` ფორმა შემთხვევითი არჩევანი არ არის. ეს ერთადერთი shape-ია ამ language-ში, რომელიც class-სა და მის ზუსტ negation-ს ერთდროულად აწარმოებს — `(c - c) + u == u` და `c - (c + u) == -u` — და სწორედ ის ხდის even-parity mechanism-ს საერთოდ დაკვირვებადს. `residue` ბლოკი კი coarsening check-ს ხდის non-vacuous-ად; მის გარეშე load-bearing test არაფერს ამტკიცებს.

Corpus-ის საზომები: `24` source, `25` grammar თითოზე, ჯამში `127` inner class, `312` (source, function) წყვილი.

## დაკვირვებული შედეგები (fix-ის შემდეგ)

**Coarsening.** `312` წყვილიდან violation `0`, `split_pairs` `0`. ყოველ წყვილზე `C_f <= C_inner` და ყოველი inner class ზუსტად ერთ outer class-შია. ეს ნული — განსხვავებით პირველი ვერსიისგან — corpus-იდან მოდის, რომელშიც check რეალურად შეიძლება ჩავარდეს.

Founding sequence `2*t + 1 - t/2`-ზე სამივე რიცხვი ერთმანეთს ემთხვევა ცამეტივე function-ისთვის:

| outer function | C_inner | C_f | merge |
|---|---|---|---|
| `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`, `asin`, `acos`, `atan`, `reciprocal`, `square`, `cube` | `8` | `8` | `0` |

**Per-function quotient.** `C_inner` სვეტი corpus-ზე შეჯამებულია (`127` ყოველთვის, რადგან inner partition `f`-ზე არ არის დამოკიდებული).

| outer function | Σ C_inner | Σ C_f | merges | merging sources | mean merge | coarsening failures | mechanism |
|---|---|---|---|---|---|---|---|
| `sin` | 127 | 127 | 0 | 0 | 0.00 | 0 | periodic — identity არსებობს, corpus-ში არ ირთვება |
| `cos` | 127 | **123** | **4** | 4 | 0.17 | 0 | **parity** (even) |
| `tan` | 127 | 127 | 0 | 0 | 0.00 | 0 | periodic — identity არსებობს, corpus-ში არ ირთვება |
| `exp` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `log` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `sqrt` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `abs` | 127 | **123** | **4** | 4 | 0.17 | 0 | **parity** (even) |
| `asin` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `acos` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `atan` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `reciprocal` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective — merge არ არის |
| `square` | 127 | **123** | **4** | 4 | 0.17 | 0 | **parity** (even) |
| `cube` | 127 | 127 | 0 | 0 | 0.00 | 0 | injective (odd) — merge არ არის |

სულ `12` merge `312` წყვილზე, ყველა ერთი mechanism-ით. `mean merge`-ის მნიშვნელი არის `coarsening_pairs = 24`, რაც clean sweep-ზე მთელი corpus-ია.

**რომელი class-ები გაერთიანდა.** ოთხივე შემთხვევა negation-producing source-იდან მოდის და სამივე even function-ზე მეორდება.

| source | C_inner | merged inner classes | outer canonical | mechanism |
|---|---|---|---|---|
| `2 - 2 + t` | 2 | `t`, `-t` | `cos(t)` / `Abs(t)` / `t**2` | parity: `-t = -(t)` |
| `4 - 4 + 3*t` | 3 | `3*t`, `-3*t` | `cos(3*t)` / `3*Abs(t)` / `9*t**2` | parity: `-3*t = -(3*t)` |
| `3 - 3 + t*t` | 3 | `t**2`, `-t**2` | `cos(t**2)` / `t**2` / `t**4` | parity: `-t**2 = -(t**2)` |
| `5 - 5 + 1/t` | 3 | `1/t`, `-1/t` | `cos(1/t)` / `1/Abs(t)` / `t**(-2)` | parity: `-1/t = -(1/t)` |

odd function-ები (`sin`, `tan`, `cube`, `atan`, `reciprocal`) იმავე წყვილს **არ** აერთიანებენ: `sin(-u) = -sin(u)`, და ეს ორი განსხვავებული function-ია.

**Period mechanism არ ირთვება — და ეს language-ის თვისებაა.** token language მხოლოდ rational literal-ს იღებს, ამიტომ ერთი token sequence-ის ორი reading ყოველთვის rational function-ით განსხვავდება rationals-ზე. `sin`-ისა და `cos`-ის period `2*pi`-ია, `tan`-ის `pi`; ორივე irrational. ე.ი. nonzero `pi`-free difference ვერასოდეს იქნება period-ის integer multiple. period merge precedence variation-იდან **მიუწვდომელია**, და გაზომილი ნული corpus-ის ხარვეზი არ არის. `merge_mechanism` period-ს მაინც ცნობს — ის პირდაპირ აგებულ argument-ებზეა შემოწმებული (`sin(t)` და `sin(t + 2*pi)`, `tan(3*t)` და `tan(3*t + pi)`) — რადგან არარსებობა უნდა გაიზომოს და არა ივარაუდოს.

**Period-ის ფორმულა უცვლელია.** `argument_period` დამოუკიდებლად ითვლის `2*pi/|a|`-ს `sin`/`cos`-ისთვის და `pi/|a|`-ს `tan`-ისთვის, და test suite მას `functions.py`-ის reported value-ს ადარებს ყოველ affine non-constant class-ზე. founding sequence-ის `G03` (`t/2 + 1`, frequency `1/2`): `sin` period `4*pi`, `tan` period `2*pi`. fix-მა ეს არ შეეხო.

## Singularity და domain effects

`singularity_and_domain_effects` ოთხ function-ს ზომავს `24` source-ზე.

**`tan` — variable-dependent pole-ები constant collapse-ზე ქრება.** `127` outer class-იდან `116`-ს აქვს restricted real domain (infinite pole family), `11`-ს კი სრული `Reals`. ეს თერთმეტი ზუსტად ის class-ებია, სადაც argument constant-ად ჩამოიშალა; `unrestricted == constant_argument` ყოველ class-ზე. კონკრეტული შემთხვევები:

```text
2*t + 1 - t/2      tan(1)       G01 G02 G07 G08              real domain: Reals
1/t + 2 - t        tan(1/2)     G01 G02 G03 G07 ...          real domain: Reals
t/t + 2*t - 1      -tan(2/3)    G14                          real domain: Reals
1 - t/2*2 + t      tan(2)       G22                          real domain: Reals
3 * 2 - t / 2 - t  tan(3)       G01 G02 G07 G08 G09 ...      real domain: Reals
2*(t - 1)/(t - 1)  tan(2)       ყველა 25                     real domain: Reals
```

დანარჩენებში pole family რჩება, მაგალითად founding-ის `G03`:

```text
tan(t/2 + 1)  ->  Complement(Reals, Union(ImageSet(Lambda(_n, 4*_n*pi - 2 + pi), Integers), ...))
```

`2*(t - 1)/(t - 1)` აქ განსაკუთრებით სასარგებლოა: pole-ები ქრება, მაგრამ excluded point `1` რჩება — ზუსტად ის გამიჯვნა, რომელიც domain სლოტს fix-მდე ერეოდა.

**`log` და `sqrt` — real-domain boundary grammar-იდან grammar-ზე მოძრაობს.** `24` source-იდან `22`-ში boundary იცვლის ადგილს ორივე function-ისთვის. ორი გამონაკლისი — `(t + 1)/(t - 2)` და `2*(t - 1)/(t - 1)` — თითო inner class-იანი source-ებია, ე.ი. მოძრაობის ადგილი არ რჩება. founding sequence-ზე რვა class ექვს განსხვავებულ boundary-ს იძლევა:

| class | `log` canonical | real domain | `sqrt` canonical | real domain |
|---|---|---|---|---|
| F01 | `log(3*t/2 + 1)` | `Interval.open(-2/3, oo)` | `sqrt(6*t + 4)/2` | `Interval(-2/3, oo)` |
| F02 | `0` | `Reals` | `1` | `Reals` |
| F03 | `log(t/2 + 1)` | `Interval.open(-2, oo)` | `sqrt(2*t + 4)/2` | `Interval(-2, oo)` |
| F04 | `log(3*t/2 + 2)` | `Interval.open(-4/3, oo)` | `sqrt(6*t + 8)/2` | `Interval(-4/3, oo)` |
| F05 | `log(t + 2)` | `Interval.open(-2, oo)` | `sqrt(t + 2)` | `Interval(-2, oo)` |
| F06 | `log(t/2 + 1/2)` | `Interval.open(-1, oo)` | `sqrt(2*t + 2)/2` | `Interval(-1, oo)` |
| F07 | `log(3*t/2 + 1/2)` | `Interval.open(-1/3, oo)` | `sqrt(6*t + 2)/2` | `Interval(-1/3, oo)` |
| F08 | `log(t + 1)` | `Interval.open(-1, oo)` | `sqrt(t + 1)` | `Interval(-1, oo)` |

boundary `-2`-დან `-1/3`-მდე მოძრაობს მხოლოდ precedence-ის შეცვლით, ხოლო constant collapse (F02) boundary-ს საერთოდ აშორებს: `log(1) = 0` და `sqrt(1) = 1` მთელ ღერძზეა განსაზღვრული. აღსანიშნავია, რომ F03 და F05 ერთსა და იმავე boundary-ს იზიარებენ და მაინც ცალკე class-ები რჩებიან — boundary key-ის მხოლოდ ერთი სლოტია, canonical form კი განსხვავებული.

**`reciprocal` — pole-ები მოძრაობს და ქრება.** `24` source-იდან `21`-ში pole set class-იდან class-ზე იცვლება; `127` outer class-იდან `20`-ს საერთოდ არ აქვს real pole. ორი კონკრეტული შემთხვევა:

```text
2/t - 1/t + t    t/(t**2 + 1)                       poles: EmptySet
                 t*(t - 1)                          poles: EmptySet
                 2*t/3                              poles: EmptySet
                 t*(t - 1)/(t**2*(t - 1) + 2)       poles: {-1}
                 -t/(t**2 - 1)                      poles: {-1, 1}

5 - 5 + 1/t      t                                  poles: EmptySet
                 -t                                 poles: EmptySet
                 t/(5*t - 6)                        poles: {6/5}
```

ე.ი. ერთი token sequence-ის ფარგლებში pole-ების რაოდენობა `0`-დან `2`-მდე იცვლება. მნიშვნელოვანი დეტალი: `5 - 5 + 1/t`-ის `t` და `-t` class-ებს pole არ აქვთ, მაგრამ excluded point `0` მაინც რჩება key-ში — pole გაქრა, puncture არა.

`domain_undetermined` ამ corpus-ზე `0`-ია.

## ინტერპრეტაცია

ორი დამოუკიდებელი layer-ია და მათი როლები არ ერევა.

```text
token sequence  ->  [precedence]  ->  inner partition (C_inner)
inner partition ->  [outer f]     ->  quotient of it (C_f <= C_inner)
```

პირველი layer semantic variety-ს **ქმნის**: grammar-ის შეცვლა სხვა function-ს იძლევა. მეორე layer მას მხოლოდ **კარგავს**: outer function-ს ინფორმაციის დამატება არ შეუძლია, მხოლოდ collapse. ამიტომ founding-ის `8` არასოდეს იზრდება — **სანამ key სწორია.** სწორედ ეს condition იყო ამ ექსპერიმენტის რეალური შედეგი: `1273` წყვილზე `278`-ჯერ key სწორი არ იყო და `8`-ის ანალოგები **იზრდებოდა**.

გაზომვა კიდევ ერთ რამეს აჩვენებს: ამ corpus-ზე quotient თითქმის ყოველთვის trivial-ია. `312` წყვილიდან `300`-ში `C_f == C_inner`. ერთადერთი mechanism, რომელიც ირთვება, parity-ია, და ისიც მხოლოდ იმ ოთხ source-ზე, რომლებიც სპეციალურად negation-ისთვისაა აგებული. სხვა სიტყვებით: precedence variation-ით მიღებული value-ები იმდენად "generic"-ია, რომ standard outer function-ების identity-ებს ვერ ხვდებიან — გარდა ყველაზე მარტივი, `u` და `-u`, შემთხვევისა.

domain layer სხვაგვარად იქცევა. იქ ცვლილება მასიურია: `log`/`sqrt` boundary `24`-იდან `22` source-ში მოძრაობს, `reciprocal`-ის pole set `21`-ში. ე.ი. outer function class-ებს არ აერთიანებს, მაგრამ **სად არის განსაზღვრული** — ეს grammar-იდან grammar-ზე მკვეთრად იცვლება. `tan`-ის constant collapse ამის უკიდურესი ფორმაა: უსასრულო pole family მთლიანად ქრება. სწორედ ეს სიმდიდრე ხდის domain სლოტს ერთდროულად ყველაზე ინფორმატიულად და ყველაზე საშიშად: ის ერთადერთია, რომელსაც შეუძლია ერთი value ორ class-ად აქციოს, თუ parse tree-ს წაიკითხავს.

## შეზღუდვები

- **key-ს შეუძლია split-ის დამზადება, ე.ი. `C_f` შეიძლება `C_inner`-ს გადააჭარბოს.** ეს არ არის თეორიული შესაძლებლობა: fix-მდე ის `278`-ჯერ მოხდა `1273` წყვილზე. მათემატიკა ამას კრძალავს, implementation კი — მხოლოდ იმდენად, რამდენადაც canonical triple denoted value-ის function-ია. თუ ოდესმე რომელიმე სლოტი ისევ raw parse tree-ს წაიკითხავს, ეს failure ბრუნდება, და ის **split**-ის სახით მოვა და არა გამორჩენილი merge-ის სახით.
- coarsening claim **corpus-ზეა verified**: `24` source და `13` function, `312` წყვილი, პლუს `98` residue source და `1273` წყვილი ცალკე sweep-ში. ის არ არის დამტკიცებული ყველა `f`-ისა და ყველა inner sequence-ისთვის. მათემატიკური არგუმენტი ზოგადია, გაზომვა კი key-ის სისწორეს ამოწმებს და მხოლოდ ამ source-ებზე.
- residue source-ების პოვნა exhaustive არ არის: ორი random scan `3800` candidate-ზე, ორივე paren-free და division-ის შემცველ shape-ებზე შემოსაზღვრული. სხვა ტიპის residue (მაგ. root-ებიდან, trigonometric identity-ებიდან, ან სამ და მეტ განსხვავებულ tree-იანი class-იდან) არ არის გამორიცხული და არ არის გაზომილი.
- merge canonical key-ით ფიქსირდება. თუ SymPy genuine identity-ს ვერ canonicalize-ს გაუკეთებს, ორი class განსხვავებულ key-ს შეინარჩუნებს და merge **გამოგვრჩება**, დაითვლება როგორც "merge არ არის". ყოველი merge count აქ lower bound-ია.
- `simplify` არ არის total: `zoo`-ს შემცველ reading-ზე SymPy exception-ს აგდებს (იხ. `t / 1 - 1 + 2 * 2` × `exp`). ასეთი წყვილი არც coarsening-ია და არც violation — ის უბრალოდ არ იზომება, და ეს corpus-ის გაფართოებისას უნდა გვახსოვდეს.
- `real_domain` `continuous_domain`-იდან მოდის; `undetermined` შემთხვევა ამ corpus-ზე `0`-ჯერ დაფიქსირდა, მაგრამ სხვა corpus-ზე ის key-ს გააუარესებდა.
- injectivity `FUNCTION_ALGEBRA`-ში **declared**-ია და არა დამტკიცებული. `asin`/`acos` injective-ია `[-1, 1]`-ზე; corpus-ის argument-ები ამ ინტერვალს სცილდება და real domain იზღუდება. გაზომვა declaration-ს ეთანხმება (`contradicts_algebra` ყველგან `false`), მაგრამ ეს agreement-ია და არა proof.
- `2 - 2 + t` ტიპის source-ები სპეციალურად parity-სთვისაა შერჩეული. `12` merge-ის რიცხვი corpus design-ის function-ია და არა grammar space-ის ბუნებრივი სიხშირისა.
- period mechanism-ის არარსებობა rational literal-ების შედეგია. თუ tokenizer ოდესმე `pi`-ს ან სხვა transcendental constant-ს დაუშვებს, ეს დასკვნა უნდა გადაიზომოს.

## Evidence-ის კლასიფიკაცია

- `C_inner`, `C_f`, merge count, mechanism და domain/pole რიცხვები executable **observations**-ია, `merge_report()` და `singularity_and_domain_effects()` გაშვებიდან.
- pre-fix violation count-ები (`126 / 442` და `278 / 1273`) **observations**-ია: პირველი რეალური pre-fix build-იდან, მეორე კალიბრირებული pre-fix key emulation-იდან, რომელიც პირველს ზუსტად აღადგენს.
- post-fix `0 / 1273` **observation**-ია fix-ის შემდგომი working tree-დან.
- coarsening `C_f <= C_inner` **theorem**-ია function application-იდან; `312`/`312` და `1273`/`1273` clean run მისი key-level **verification**-ია და არა proof.
- period mechanism-ის მიუწვდომლობა **structural argument**-ია language-ის literal set-ზე, corpus-ის გაზომვით დადასტურებული.
- "ეს ყველა outer function-ისთვის ყოველთვის ასეა" — **არ არის claimed**. verified-ია ცამეტ function-ზე და `24 + 98` sequence-ზე, fix-ის შემდეგ.

## ვალიდაცია

```text
python -m pytest -q tests/test_outer_quotient.py
30 passed in 155.20s (0:02:35)   # მეორე გაშვება იმავე tree-ზე: 268.90s

python -m pytest -q
505 passed in 1210.70s (0:20:10)
```

სრული suite-ის რიცხვი პარალელურად მიმდინარე სხვა card-ების ფაილებსაც შეიცავს; ამ card-ის საკუთარი წვლილია `tests/test_outer_quotient.py`-ის `30` test და `tests/test_outer_functions.py`-ის `5` test.

wall clock ამ მანქანაზე ხმაურიანია (პარალელურად სხვა card-ებიც მუშაობს): იმავე ფაილის ორმა ზედიზედ გაშვებამ `155.20 s` და `268.90 s` აჩვენა იდენტურ tree-ზე. ქვემოთა რიცხვები თითო გაზომვაა და არა საშუალო.

უდიდესი run: სრული `merge_report()` sweep, `312` წყვილი, `94.9 s` wall clock, `12` worker `16` core-ზე (`WORKER_HEADROOM_CORES = 2`, `WORKER_CAP = 12`). `singularity_and_domain_effects()` იმავე corpus-ზე ოთხ function-ზე: `220.4 s`.

falsification sweep-ები (working tree-ს გარეთ, scratch script-ებით): `98` residue source × `13` function, pre-fix და post-fix, `1273` წყვილი თითოეულ რეჟიმში.

sequential და parallel path იდენტურ report-ს აწარმოებს; ეს test suite-ში assert-ითაა დაფიქსირებული და არა ნავარაუდევი.
