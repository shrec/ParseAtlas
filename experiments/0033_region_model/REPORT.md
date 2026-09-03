# ParseAtlas ექსპერიმენტი 0033: region model და decode obligation

## მიზანი

**პასუხი ერთი წინადადებით: დიახ — Region model-მა ამ ერთ axis-ზე გამოხატა და discharge-ით დაფარა ისეთი transformation, რომელიც 0028-ის სამივე commitment-ს (`preserve_inputs`, `preserve_outputs`, `map_equality`) ერთდროულად არღვევს, და იგივე წყვილი, რომელსაც control სწორად აცხადებს unreachable-ად და რომელსაც ვერც ერთი ცალკეული relaxation ვერ ხსნის, decode relation-ის მიწოდების შემდეგ admissible ხდება — obligation-ის სამივე ნახევარი (equality, definedness, admissibility) სიმბოლურად წყდება და declared sample set მათ მხოლოდ ადასტურებს.**

ეს არის ROADMAP Phase 14-ის (Group F, T22) პირველი increment. 0028-მა ააშენა negative control, რომელიც წყვეტს, თუ სამი structural commitment-იდან **რომელი** კეტავს target-ს. 0027-მა აჩვენა, რომ ის transformation, რომელიც ღირდა, სამივეს არღვევდა. საძიებელი, რომელიც სამივეს ინარჩუნებს, საკუთარ space-ში სრულია და representation change-ის მიმართ ბრმაა; საძიებელი, რომელიც უბრალოდ ყრის მათ, unsound-ია. Region model მესამე ვარიანტია: **დაარღვიე commitment და მის ადგილას გადაიხადე proof obligation.**

მოდული არის `src/parseatlas/region.py`. `case_studies/` snapshot არსად არ არის imported; representation საკუთარია და მთლიანად ჩვეულებრივ rational arithmetic-ში ცხოვრობს, elliptic curve-ის გარეშე.

## Model

Region არის `(inputs, state, operations, outputs, invariants)`:

```text
Region(name, inputs, operations, outputs, state, precondition, invariants)
Operation(target, kind, args)          kind in {add, sub, mul, div, neg}
StateBinding(carried, produced)        input <- output key, ე.ი. declared LOOP
```

`Operation` არის **ერთი** DAG node ერთი declared kind-ით. ეს არჩევანი განზრახია: operation multiset region-ის property უნდა იყოს და არა იმისა, თუ ვინ როგორ ჩაწერა expression. `args` არის ან სახელი, ან rational literal; `"3"` არასწორი სახელია და არა ორაზროვანი constant.

`StateBinding` არის ის, რაც region-ს region-ად აქცევს და არა ერთ formula-დ. მის გარეშე declared loop არ არსებობს, loop-ის გარეშე კი per-step overhead — T23-ის მიხედვით სწორედ ის, სადაც რეალური კითხვა წყდება — საერთოდ არ არის გამოხატვადი.

`Encoding` არის named pair of maps baseline input tuple-სა და candidate input tuple-ს შორის, თითოეული საკუთარი declared domain-ით (`domain`, `codomain`), პლუს `output_decode` — იგივე relation boundary object-ზე, candidate-ის output key-ებზე. ორი ცალკე map საჭიროა იმიტომ, რომ region-ის input-სა და output-ს ერთი shape არ მოეთხოვება და ერთი map-ის დაწერა ამას ჩუმად დაუშვებდა.

**Gate construction-ზეა და არა use-ზე.** `BrokenEncoding` იგდება, თუ:

1. `decode(encode(x)) == x` არ არის rational-function identity (cancellation-ით გადაწყვეტილი);
2. იგივე pointwise და exactly არ სრულდება ყოველ admissible sample point-ზე;
3. `encode` `codomain`-ს ტოვებს რომელიმე admissible sample point-ზე.

პირობა 1 არის accept condition, 2 და 3 მხოლოდ უარყოფენ. სამივე რეჟიმი გაზომილია:

```text
decode = num + den      -> "decode is not a left inverse ... comes back as v + 1 rather than v"
encode = (v, 2)         -> "comes back as v/2 rather than v"; 1/11 sample point გადარჩა
encode = (v, v)         -> "encode leaves the decode's declared domain at 1 of 11 admissible points"
```

`discharge(baseline, candidate, encoding, samples)` არის თვით obligation:

```text
decode(candidate(encode(x))) == baseline(x)
```

**ოთხი conjunct, თითოეული ორჯერ გაზომილი: სიმბოლურად წყდება, sample set-ით დასტურდება.**

1. **equality, symbolic** — candidate-ის output-ები encode substitution-ითა და output decode-ით შედგება და baseline-ისას cancellation-ით ედრება. rational-function კლასზე ეს decision procedure-ია.
2. **equality, sampled** — `agreement_fraction` declared deterministic sample set-ზე, exact `Fraction`-ებით. ცარიელი ან vacuous sample set `agreement_fraction`-ს `None`-ად ტოვებს და **არ** discharge-ავს.
3. **definedness** — `domain_comparison` წყვეტს **factorization-ით და არა sampling-ით**: აგროვებს იმ divisor-ებს, რომლებზეც თითოეული მხარე რეალურად ყოფს, შლის მათ ურეციდივო მამრავლებად და ადარებს მიღებულ სიმრავლეებს. sample count-ები მხოლოდ ადასტურებენ.
4. **admissibility** — candidate-ის საკუთარი declared precondition, encode-თან შედგენილი, უნდა სრულდებოდეს ყოველ იმ წერტილში, სადაც obligation იხურება. candidate, რომელიც baseline-ზე მეტს ითხოვს, არის *conditional და არასოდეს equivalent*, და ამას ახლა `Discharge` record თვითონ ამბობს და არა ორი ცალკე output-ის წამკითხველი ადამიანი.

მესამე პუნქტი ცალკეა იმიტომ, რომ candidate, რომელიც განსაზღვრულია იქ, სადაც baseline არა, არ არის მცდარი — მან object-ის domain შეცვალა, და ეს სხვა claim-ია. ხოლო ის, რომ ის **სიმბოლურად** წყდება, ამ increment-ის შესწორებული ნაწილია: sampled definedness check ვერასოდეს იტყვის მეტს, ვიდრე „იმ წერტილებში, რომლებიც ვინმემ ჩამოწერა, ორივე მხარე ერთნაირად იქცეოდა“, და candidate, რომლის pole ბადეს გვერდს უვლის, მასში **გაივლის**. ეს ზუსტად ის fail-open-ია, რომელიც პროექტმა ერთი დონით ქვემოთ, `functions.py`-ში, ახლახან გაასწორა (`NF-2026-00004` — function half სიმბოლურად წყდებოდა, domain half კი sampling-ით) და აქ ის არ მეორდება.

`precondition_check(region, samples)` ყოველ წერტილზე **ორ დამოუკიდებელ ფაქტს** ზომავს: სრულდება თუ არა declared precondition, და განსაზღვრულია თუ არა region-ის საკუთარი arithmetic. ეს ერთი და იგივე ფაქტი არ არის და მათი აღრევა ზუსტად ის გზაა, რომლითაც candidate იძენს precondition-ს, რომელიც არავის ჩაუწერია.

Verdict-ები ხუთია და **absolute claim მხოლოდ symbolic ნახევრიდან მოდის**: `unsatisfiable` მაშინ და მხოლოდ მაშინ, როცა sympy პირობას `false`-მდე დაიყვანს; `unsatisfied on the sample set` — როცა ის declared ბადეზე არსად სრულდება, sympy კი `false`-ს **არ** ამბობს; `conditional`, `unconditional`, და `undetermined` (ცარიელი sample set — არაფერი გაზომილა, ე.ი. არაფერი დასკვნილა). `Eq(b, 7)` სრულიად დაკმაყოფილებადია და 240-წერტილიან ბადეზე არსად სრულდება; მას `unsatisfiable` რომ ეწოდოს, ეს იმას ნიშნავდა, რომ სასრული sample set წყვეტს მთელი სივრცის შესახებ მტკიცებას — ზუსტად ის, რის გამოც definedness ნახევარი გადაიწერა.

`region_cost(region)` აბრუნებს operation multiset-ს kind-ების მიხედვით, total-ს, critical-path depth-ს operation DAG-ზე, maximum pressure-ზე live value-ების რაოდენობას, და declared LOOP-ის cost-ს — symbolically `n`-ში და **verified** ნამდვილ unrolling-ებთან. Loop model `n` ნაბიჯს ერთმანეთზე აწყობს state binding-ების გასწვრივ და შედეგს `cse . dce`-ით ნორმალიზებს — ზუსტად ის normaliser, რომელიც 0027-მა vendored engine-ში დააფიქსირა.

## Axis: deferred division on rational values

ერთი axis, სრულიად domain-neutral:

| | baseline `eager_division_step` | candidate `deferred_division_step` |
|---|---|---|
| inputs | `(v, a, b)` | `(num, den, a, b)` |
| operations | `t = mul(v, a)`; `u = div(t, b)` | `p = mul(num, a)`; `q = mul(den, b)` |
| outputs | `VALUE = u` | `NUM = p`, `DEN = q` |
| carried state | `1` (`v <- VALUE`) | `2` (`num <- NUM`, `den <- DEN`) |
| precondition | `Ne(b, 0)` | `Ne(den, 0)` |
| invariant | `Eq(VALUE*b, v*a)` | `Eq(NUM*den*b, DEN*num*a)` |

Encoding `deferred_division`:

```text
encode:        (v, a, b)        -> (v, 1, a, b)
decode:        (num, den, a, b) -> (num/den, a, b)
output_decode: VALUE            =  NUM/DEN
codomain:      Ne(den, 0)
```

ეს იგივე სტრუქტურაა, რაც external project-მა ხელით იპოვა: input იცვლება (value ხდება pair), output chain-ის განმავლობაში იცვლება, internal state იცვლება, equivalence კი raw equality-ს ნაცვლად common scale factor-ამდეა — pair `(num, den)` scale-invariant-ია და decode ერთადერთი ბოლო division-ია.

## დაკვირვებული შედეგები

### Encoding gate

```text
left_inverse_symbolic  True
sample_count           96      admissible 96
agreement              96/96
codomain_misses        0       codomain_hits 96
failures               []
```

### Operation multiset, symbolically `n`-ში

გაზომილია `1, 2, 3, 4, 6, 8` ნაბიჯზე და ყოველზე verified ნამდვილ unrolling-თან (`counts_verified True`, `depth_affine_verified True`):

| | eager chain | deferred chain (decode-ის ჩათვლით) |
|---|---|---|
| `mul` | `n` | `2*n` |
| `div` | `n` | `1` |
| total | `2*n` | `2*n + 1` |
| critical-path depth | `2*n` | `n + 1` |
| max live | `3` | `4` |
| carried state | `1` | `2` |

Loop-only (decode-ის გარეშე) candidate-ისთვის: `mul` `2*n`, `div` `0`, depth `n`.

### Crossover

```text
n:                 1     2     3     4     6     8
eager div:         1     2     3     4     6     8
deferred div:      1     1     1     1     1     1
division saving:   0     1     2     3     5     7
operation diff:   +1    +1    +1    +1    +1    +1
depth diff:        0    -1    -2    -3    -5    -7
```

**Crossover არის `n = 2`.** Deferred form ნაკლებ division-ს ასრულებს `n >= 2`-ზე, ზუსტად `n - 1`-ით. `n = 1`-ზე ორივე ერთ division-ს აკეთებს.

და ის, რაც ამ შედეგში მთავარია და გადამალვას არ ექვემდებარება: **deferred form არასოდეს ასრულებს ნაკლებ operation-ს.** ის `n - 1` division-ს ცვლის `n` დამატებით multiplication-ზე და ჯამში ყოველთვის ზუსტად ერთი operation-ით მეტს აკეთებს. მოგება ორია და ორივე სტრუქტურულია: division count `n`-დან `1`-მდე, და critical-path depth `2n`-დან `n+1`-მდე.

### Precondition და სად ტყდება

```text
region                   conditions      satisfied   defined   unsatisfied_but_defined   verdict
eager_division_step      Ne(b, 0)        217/240     217       0                         conditional
deferred_division_step   Ne(den, 0)      221/240     240       19                        conditional
eager_chain_4            Ne(b, 0)        217/240     217       0                         conditional
deferred_chain_4         Ne(den, 0)      221/240     240       19                        conditional
impossible_step          Ne+Eq(den, 0)     0/240     240       240                       unsatisfiable
off_grid_precondition    Eq(b, 7)          0/240     240       240                       unsatisfied on the sample set
```

ეს ცხრილი ორ განსხვავებულ ფაქტს ამბობს:

- baseline-ისთვის declared precondition **ზუსტად** ემთხვევა definedness-ს: `217` satisfied, `217` defined, `0` წერტილი, სადაც precondition ტყდება და arithmetic მაინც მუშაობს.
- candidate-ისთვის arithmetic **ტოტალურია** — `240/240` defined, არსად არ იყოფა — და precondition მაინც უფრო ძლიერია: `19` წერტილზე region ლამაზად ითვლის და შედეგი **არაფერს არ აღნიშნავს**, რადგან `den = 0`. Precondition აქ definedness-ის შესახებ საერთოდ არ არის; ის იმის შესახებ არის, denote-ს აკეთებს თუ არა output pair რაციონალურ რიცხვს.

`unsatisfiable` verdict-ს ცალკე სახელი აქვს იმიტომ, რომ candidate, რომლის precondition არსად არ სრულდება, candidate არ არის; `symbolically_unsatisfiable True` მას sympy-ის მიერ დამოუკიდებლადაც ადასტურებს.

და სწორედ ამიტომ არის ბოლო ორი მწკრივი **განსხვავებული**, თუმცა ორივეს `0/240` აქვს. `impossible_step`-ის პირობა `false`-მდე იყვანება — absolute claim დამსახურებულია. `off_grid_precondition_step`-ის `Eq(b, 7)` კი სრულიად დაკმაყოფილებადია და უბრალოდ `VALUE_POOL`-ს გვერდს უვლის; მისი `symbolically_unsatisfiable` არის `False` და verdict-იც ამას ამბობს — **unsatisfied ON THE SAMPLE SET**. 240-წერტილიან ბადეს აბსოლუტური ვერდიქტის გამოტანის უფლება არ აქვს.

**Precondition discharge by construction.** `encode` `den`-ს `1`-ზე აყენებს, ე.ი. ყოველი encoded წერტილი candidate-ის დამატებით precondition-ს ავტომატურად აკმაყოფილებს. ეს არის 0027-ის C.5(iii)-ის ("the precondition is discharged at every call site by construction rather than by assumption") ზუსტი ანალოგი ამ axis-ზე.

**და ის, რაც ამ გაზომვამ დამატებით აჩვენა:** baseline `b = 0`-ზე **პირველივე ნაბიჯზე** ვარდება; candidate `n` ნაბიჯს ბოლომდე ასრულებს და მხოლოდ decode-ზე ვარდება. Deferred form არა მხოლოდ division-ს, არამედ **domain error-საც** გადადებს. `domain_match` მაინც `True`-ია, რადგან ორივე მხარე ერთსა და იმავე წერტილებში არის განუსაზღვრელი — მაგრამ განსხვავებულ მომენტში.

### Discharge

```text
steps   keys      sample_count   outside_domain   both_defined   agreement   symbolic   discharged
1       [VALUE]   240            0                217            217/217     True       True
2       [VALUE]   240            0                217            217/217     True       True
3       [VALUE]   240            0                217            217/217     True       True
```

და იმავე record-ის დანარჩენი სამი conjunct:

```text
baseline_excluded                 ['b = 0']       candidate_excluded  ['b = 0']
symbolic_domain_match  True       sample_domain_match  True       symbolic_domain_conflict  False
candidate_precondition            ['Ne(den, 0)']  verdict on its own inputs: conditional
encoded_precondition_symbolic     True            holds at 240/240 encoded points
precondition_admissible  True     precondition_qualified  True
```

`240 - 217 = 23` წერტილი ის არის, სადაც `b = 0` და ორივე მხარე განუსაზღვრელია; ისინი agreement fraction-ში არ შედიან და `domain_match`-ს არ არღვევენ — და ეს **არა** იმიტომ, რომ ბადეზე დამთხვევა დაფიქსირდა, არამედ იმიტომ, რომ ორივე მხარის excluded სიმრავლე factorization-ით ზუსტად `b = 0`-ია.

`precondition_qualified True` ის ადგილია, სადაც model თვითონ ამბობს „conditional, never equivalent“: candidate ითხოვს `Ne(den, 0)`-ს, რასაც baseline არ ითხოვს, encode კი `den`-ს `1`-ზე აყენებს და ამ მოთხოვნას ყოველ encoded წერტილში იხდის. ეს ფრაზა `reason`-შივე წერია და ცალკე `precondition_check` call-ის წაკითხვას აღარ საჭიროებს.

### Definedness: სად და როგორ წყდება domain

Sampled definedness check-ს ერთი კონკრეტული ხვრელი აქვს და ის ბადის სასრულობაა. ორი candidate, ერთი და იგივე კონსტრუქციით, განსხვავებული pole-ით:

```text
s = sub(b, k); h = div(num, s); p = mul(h, a); pp = mul(p, s); q = mul(den, b)
NUM = pp, DEN = q          # cancellation-ის შემდეგ NUM = num*a: იგივე boundary map
```

`VALUE_POOL` არის `(-3, -2, -1, -1/2, 0, 1/3, 1, 3/2, 2, 3, 5)` — `3` მასშია, `7` არა.

```text
k   symbolic   agreement   baseline_only   candidate_excluded    extra     sym_domain   conflict   discharged
3   True       197/197     20              ['b = 0', 'b = 3']    b = 3     False        False      False
7   True       217/217      0              ['b = 0', 'b = 7']    b = 7     False        True       False
```

`k = 3`-ზე sampled ნახევარიც ხედავს: `20` წერტილი, სადაც baseline განსაზღვრულია და candidate არა. `k = 7`-ზე sampled ნახევარი **სრულიად ბრმაა** — `217/217` agreement, `0` baseline-only წერტილი, ზუსტად ისეთი რიცხვები, როგორიც ნამდვილ candidate-ს აქვს. Ground truth კი ესაა:

```text
baseline.evaluate([1, 1, 7])        -> {'VALUE': 1/7}
candidate.evaluate([1, 1, 1, 7])    -> UndefinedAtPoint
```

სიმბოლური ნახევარი ორივეს ერთნაირად აჭერს: `symbolic_domain_match False`, `candidate_extra_exclusions ['b = 7']`, `discharged False`. `symbolic_domain_conflict True` კი სწორედ იმას იწერს, რომ ბადემ ვერაფერი დაინახა — ეს არის ის flag, რომელიც equality ნახევრის `symbolic_sample_conflict`-ს შეესაბამება.

**როგორ წყდება.** თითოეული მხარე თავის excluded სიმრავლეს აწვდის: baseline — საკუთარი declared division-ებიდან; candidate მხარე — encode-ის pole-ებიდან, საკუთარი declared division-ებიდან encode-ის ჩასმით, და output decode-ის pole-ებიდან candidate-ის output-ების ჩასმით. divisor-ები იშლება ურეციდივო მამრავლებად და სიმრავლეები ედრება; `d1 ... dk`-ს zero set-ების გაერთიანება მათი ნამრავლის zero set-ია, ხოლო ორ ნამრავლს ერთი და იგივე zero set აქვს ზუსტად მაშინ, როცა მათი ურეციდივო მამრავლების სიმრავლეები ემთხვევა. ეს იგივე დისციპლინაა, რაც `canonical.undefined_terms`-სა და `transformation_axes.excluded_points`-ში, მრავალცვლადიან შემთხვევაზე გასწორებული: `solve(d, variables[0])` `den*b`-სგან `den = 0`-ს კარგავს, factorization კი არა.

### Adversarial candidate: sample agreement საკმარისი არ არის

`adversarial_deferred_step` numerator-ს დამატებით წევრს `(b - 1)(b - 2)*num`-ს უმატებს. ეს ფაქტორი ქრება ზუსტად `b in {1, 2}`-ზე:

```text
sample set                          agreement    symbolic   conflict   discharged
ADVERSARIAL_SAMPLES (32 წერტილი)    32/32 = 1    False      True       False
default sample set (217 defined)    59/217       False      False      False
```

Declared sample set-ზე sampled ნახევარი **სრულია და არაფერს ამბობს**; cancellation წყვილს მაინც უარყოფს და `symbolic_sample_conflict` ჩაიწერება იმის ნაცვლად, რომ candidate გაძვრეს. ეს 0028-ის adversarial pattern-ია decode obligation-ისთვის გადმოტანილი.

### 0028 control-თან შედარება — გაზომილი და არა ნათქვამი

იგივე წყვილი ორ დამოუკიდებელ machinery-ს გადაეცემა.

```text
reachability_verdict(as_program(eager_division_step), as_program(deferred_division_step))

  reachable         False
  violated          ('preserve_inputs', 'preserve_outputs', 'map_equality')
  satisfied         ()
  preserve_inputs   "input list differs: reference ['v','a','b'] against target ['num','den','a','b']"
  preserve_outputs  "output key set differs: target adds ['DEN','NUM'] and drops ['VALUE']"
  map_equality      "arity differs: ... the two are not maps on the same tuple"

relaxation_analysis(...)
  unblocking        ()
  sole_blocker      None
  summary           "no single relaxation helps: the target violates
                     ['preserve_inputs','preserve_outputs','map_equality'] and every one must go"
```

```text
discharge(eager_division_step, deferred_division_step, deferred_division)

  discharged        True
  symbolic_verdict  True
  agreement         217/217
  domain_match      True
```

იგივე ვერდიქტი `n = 4` chain წყვილზეც. **Control სწორია და Region model მას არ ეკამათება.** Control ამბობს: ამ წყვილს input-preserving rewrite search ვერ მიაღწევს, არც ერთი commitment-ის ცალკე მოხსნა არ შველის. Region model ამატებს ერთადერთ რამეს: **decode relation-ს, და მას გადაიხდის.** ის, რასაც control სწორად უწოდებს unreachable-ს, ხდება admissible — არა იმიტომ, რომ commitment შესუსტდა, არამედ იმიტომ, რომ მის ადგილას სხვა obligation დაიდო და გაზომვამ ის დაფარა.

## Loop cost: per-step overhead, რომელსაც per-formula count ვერ ხედავს

ორი region, `product_hoisted` და `product_sequential`, ერთსა და იმავე map-ს (`v*a*b`) ითვლიან:

```text
product_hoisted:     t = mul(a, b);  w = mul(v, t)
product_sequential:  t = mul(v, a);  w = mul(t, b)
```

Per-formula ისინი **ყველა structural რიცხვზე გაურჩეველია**:

```text
                     multiset    total   depth   max_live   carried_state
product_hoisted      {mul: 2}    2       2       3          1
product_sequential   {mul: 2}    2       2       3          1
```

Loop-ზე კი:

```text
                     operations   depth
product_hoisted      n + 1        n + 1
product_sequential   2*n          2*n
```

განსხვავება ერთადერთია: `a*b` carried chain-ის **გარეთ** ფორმირდება, ე.ი. loop მას ერთხელ ითვლის; `v*a` კი chain-ის **შიგნით**, ე.ი. ყოველ ნაბიჯზე. `cse` ამას loop model-ში ავტომატურად აჩენს. Per-formula count-ს ამის დანახვის საშუალება პრინციპულად არ აქვს, რადგან განსხვავება body-ში არ არის — ის body-ის *ადგილშია*.

და გადამწყვეტი: ეს ორი region ერთი და იგივე boundary object-ია. `identity` encoding-ით `discharge` მათ **accept**-ს აძლევს, 0028 control კი მათ `reachable=True`, `violated=[]`-ს. **არც ერთი equivalence oracle მათ ვერ დაალაგებს.** ეს არის T23-ის ("Generation is not the hard half; SELECTION is") minimal instance ამ მოდულში, გაზომილი და pinned.

## Multicore

Sequential — გაზომვით და არა ჩვევით. მთელი `axis_report()` არის ათამდე region, თორმეტამდე sympy cancellation და რამდენიმე ათასი exact rational evaluation; best of 5 ამ 16-core მანქანაზე **`0.445 s`** (symbolic definedness-ისა და admissibility conjunct-ების დამატების შემდეგ; მანამდე `0.241 s`). 0028-მა ამავე ტიპის სამუშაოსთვის process pool-ის break-even გაზომა `48` დამოუკიდებელ pair-ზე, სადაც Windows `spawn` child მხოლოდ module import-ისთვის `~0.41 s` იხდის. ეს corpus ორი რიგით ქვემოთაა ამ ზღვარზე, ე.ი. pool სუფთა დანაკარგი იქნებოდა. Parallel path არსებობს `reachability_control.reachability_sweep`-ში და corpus-ის გაზრდისთანავე თავისით ირთვება.

## ინტერპრეტაცია

**Model-მა იმუშავა იმ ერთ შემთხვევაზე, რომლისთვისაც ის აშენდა.** Transformation, რომელიც სამივე commitment-ს არღვევს, გამოიხატა ხუთი ობიექტით (`Region`, `Encoding`, `discharge`, `precondition_check`, `region_cost`) და discharge-ით დაიფარა exact და symbolic ორივე ნახევარზე. 0027-ის ცენტრალური სტრუქტურა — "ერთი substitution input-ებზე, ერთი symbolic cancellation, და DCE, რომელიც engine-ს ისედაც აქვს" — აქ ზუსტად იმავე ფორმით მუშაობს: `encode` არის substitution, `cancel` არის cancellation, `cse . dce` არის normaliser.

**რასაც Region model ამატებს 0028-ს, ერთი წინადადებით:** control ამბობს *რომელი* commitment კეტავს target-ს; Region model ამბობს *რა უნდა გადაიხადო*, რომ ის commitment დაარღვიო — და გადაიხდის.

**რაც ამ გაზომვამ დამატებით აჩვენა და card-ში არ ეწერა:**

1. Deferred form **operation-ების ჯამში არასოდეს იგებს** — ყოველთვის ზუსტად `+1`. მოგება მთლიანად division count-სა და depth-შია. Per-formula operation total ამ axis-ს **მცდარად** უარყოფდა.
2. Candidate არა მხოლოდ division-ს, არამედ domain error-საც გადადებს: baseline პირველ ნაბიჯზე ვარდება, candidate `n`-ის შემდეგ.
3. Candidate-ის precondition definedness-ის შესახებ საერთოდ არ არის — მისი arithmetic ტოტალურია. ის denotation-ის შესახებ არის. ეს განსხვავება მხოლოდ იმიტომ გამოჩნდა, რომ `precondition_check` ორივე ფაქტს ცალკე ზომავს.
4. **Domain-ის ტოლობა sampling-ით საერთოდ არ წყდება.** ეს ამ increment-ის ყველაზე ძვირად ნასწავლი პუნქტია: ორი boundary object, რომლებიც declared ბადის ყოველ წერტილში ერთნაირად იქცევიან, შეიძლება იმ წერტილში განსხვავდებოდნენ, რომელიც ბადეზე უბრალოდ არ არის — და pole-ის გადატანა ნებისმიერ არა-sampled მნიშვნელობაზე ამ counterexample-ს თავიდან აშენებს. სასრული sample set აქ არა სუსტი, არამედ **პრინციპულად უუფლებო** მოწმეა; მას მხოლოდ დადასტურება და წინააღმდეგობის ჩვენება შეუძლია, მიღება — არა. იგივე დასკვნა ეხება precondition-ის აბსოლუტურ ვერდიქტსაც.

## შეზღუდვები

- **ერთი axis არ არის engine.** აქ ერთი representation axis არის implemented — deferred division. Generation, ე.ი. candidate-ების ავტომატური წარმოქმნა, საერთოდ არ არსებობს; ყოველი region ხელით არის declared.
- **Discharge არ არის proof ყველა input-ისთვის.** Symbolic ნახევარი decision procedure-ია მხოლოდ იმ rational-function კლასისთვის, რომელშიც ეს model ცხოვრობს; მის გარეთ (transcendental, finite field, floating point) ის არაფერს არ ამბობს. Sampled ნახევარი 240 declared წერტილია და ის **ვერაფერს იღებს დამოუკიდებლად** — `adversarial_deferred_step`-მა აჩვენა, რომ მას equality-ზე გაცურება შეიძლება, `off_grid_pole_step`-მა კი — რომ definedness-ზეც; ორივე შემთხვევაში ვერდიქტი symbolic ნახევრიდან მოდის.
- **არაფერი აქ candidate-ებს არ ალაგებს.** `region_cost` ზომავს; ის არ ირჩევს. T23 selection-ს უფრო ძნელ ნახევრად ასახელებს და ეს მოდული მას არ ეხება. `product_hoisted` / `product_sequential` წყვილი ზუსტად იმას აჩვენებს, რომ equivalence აქ ვერაფერს გადაწყვეტს — მაგრამ ის, თუ **რომელი** cost რიცხვი უნდა იყოს გადამწყვეტი, აქ არ არის დადგენილი და არც არის მცდელობა.
- **არავითარი wall-clock ან speedup claim *ამ axis-ის შესახებ*.** ეს structural model-ია. აქ division ერთი operation-ია და ეს მანქანაზე მისი ღირებულების შესახებ **არაფერს** ამბობს; `2*n` operation `2*n + 1`-ის წინააღმდეგ ვერცერთი მიმართულებით ვერ ითარგმნება დროში ამ მოდულის მიერ. „Multicore“ სექციაში მოყვანილი `0.445 s` არის repository-ს მიერ მოთხოვნილი გაზომვა, რომელიც sequential path-ს ასაბუთებს, და არა transformation-ის performance შედეგი.
- **Encoding-ის gate არ იღებს domain-conditional left inverse-ს.** Accept condition არის unconditional rational-function identity. Encoding, რომლის left inverse მხოლოდ declared domain-ის ნაწილზე მართალია, უარყოფილია და არა შენახული როგორც conditional ფაქტი. ეს ამ increment-ის რეალური ზღვარია და აქ არის ჩაწერილი და არა მოგვიანებით აღმოსაჩენი.
- **`domain_match` მოითხოვს, რომ ორივე მხარე ერთსა და იმავე წერტილებში იყოს განსაზღვრული, და ორივე მიმართულება უარყოფილია.** Candidate, რომელიც domain-ს **ავიწროებს** (`candidate_extra_exclusions`, ე.ი. `b = 7`-ის შემთხვევა), და candidate, რომელიც მას **აფართოებს** (`baseline_extra_exclusions`), ორივე იღებს `discharged=False`-ს — სწორად, რადგან ეს სხვა claim-ია — მაგრამ model ჯერ არ ამბობს, რა უნდა გადაიხადოს არცერთმა.
- **რას წყვეტს და რას არ წყვეტს symbolic definedness comparison.** ის **წყვეტს** იმ excluded სიმრავლეების ტოლობას, რომლებიც explicit division-ებიდან წარმოიქმნება ამ მოდულის rational-function კლასში, ორივე მიმართულებით და ბადისგან დამოუკიდებლად. ის **არ** წყვეტს: (i) ტოლობას რაციონალურ წერტილებზე — შედარება ალგებრულად ჩაკეტილ ველზე მიდის, ე.ი. `b**2 + 1` excluded-ად ითვლება, თუმცა მას რაციონალური ფესვი არ აქვს; ეს fail-closed-ია და მხოლოდ უარყოფს; (ii) იმ შემთხვევას, როცა encoding-ს declared `domain` აქვს და excluded სიმრავლეები განსხვავდება — მაშინ ის `decided=False`-ს აბრუნებს და უარყოფს, რადგან undecidable domain comparison discharge არ არის; (iii) არაფერს radical-ის, logarithm-ის ან symbolic exponent-ის შესახებ — ისინი ამ operation vocabulary-ში არ არსებობენ, და მათი გამოჩენისას ეს შედარება უნდა გაფართოვდეს და არა გამოყენებულ იქნას როგორც არის.
- **`precondition_admissible` მოითხოვს, რომ encode-თან შედგენილი precondition სიმბოლურად `true`-მდე დაიყვანოს.** `None` (sympy ვერ წყვეტს) უარყოფად ითვლება. Candidate, რომლის დამატებითი მოთხოვნა რეალურად უვნებელია, მაგრამ sympy-სთვის გაუმჭვირვალეა, აქ უსამართლოდ უარიყოფა; ეს განზრახ არჩეული მიმართულებაა.
- **Loop model `cse . dce`-ს ეყრდნობა.** Loop-invariant hoisting ამ ნორმალიზაციის შედეგია. Region, რომლის per-step overhead ამ ორი pass-ისთვის უხილავია, აქ არასწორად დაფასდება; `counts_verified` და `depth_affine_verified` ამის დეტექტორებია და არა გარანტიები.
- **`state` binding declared-ია და არა inferred.** Loop იმიტომ არსებობს, რომ ვინმემ დაწერა. Model ვერ პოულობს loop-ს region-ში, რომელსაც state არ გამოუცხადებია.

## Evidence-ის კლასიფიკაცია

- **OBSERVED**: ყველა operation count, depth, max live, agreement fraction, precondition count, encoding gate-ის რიცხვები და 0028 control-ის ვერდიქტი. თითოეული `axis_report()`-ის ერთი გამოძახებით იწარმოება და test-ებით არის pinned.
- **JUSTIFIED**: `n`-ში symbolic operation count და depth. ისინი loop-invariant/varying split-იდან **გამოიყვანება** და შემდეგ ნამდვილ unrolling-ებთან `1, 2, 3, 4, 6, 8`-ზე **მოწმდება** (`counts_verified`, `depth_affine_verified`); closed form quote-ს არ ექვემდებარება, თუ დროშა ჩავარდა.
- **JUSTIFIED**: `decode(candidate(encode(x))) == baseline(x)` ამ წყვილისთვის — sampled agreement `217/217` პლუს exact cancellation. Cancellation rational-function კლასზე decision procedure-ია, ე.ი. ეს კლასის შიგნით proof-ია და მის გარეთ არაფერი.
- **JUSTIFIED**: definedness. ორივე მხარის excluded სიმრავლე factorization-ით დგინდება და ედრება; ეს zero-set ტოლობის decision procedure-ია ალგებრულად ჩაკეტილ ველზე ამ კლასის რაციონალური ფუნქციებისთვის, ე.ი. კლასის შიგნით proof-ია და მის გარეთ არაფერი. sample count-ები ამის დასტურია და არა მისი წყარო.
- **OBSERVED**: adversarial-ის უარყოფა და `symbolic_sample_conflict`. ეს არის test power-ის გაზომვა და არა claim.
- **OBSERVED**: `off_grid_pole_step`-ის უარყოფა და `symbolic_domain_conflict`. ესეც test power-ის გაზომვაა: ის ზომავს, თუ რამდენს **ვერ** ხედავს 240-წერტილიანი ბადე.
- **არ არის claimed**: არავითარი დროითი შედეგი; არავითარი განზოგადება სხვა axis-ზე; არავითარი ranking; არავითარი მტკიცება, რომ ეს model 0027-ის co-Z-ს **იპოვის** — მან აჩვენა მხოლოდ ის, რომ იმავე სტრუქტურის transformation-ს **გამოხატავს და discharge-ს უკეთებს**.

## ვალიდაცია

```text
python -m pytest -q tests/test_region.py
47 passed

python -m pytest -q
593 passed
```

(მთელი tree-ს ჯამი ამ სესიის განმავლობაში პარალელურად მიმდინარე ექსპერიმენტის გამო `552`-დან `593`-მდე გაიზარდა; ამ card-ის საკუთარი წვლილი არის `33 -> 47`, და ორივე გაზომვაზე failure `0`-ია.)

Test-ები პირდაპირ ფარავენ card-ის ექვს მოთხოვნას: encoding-ის უარყოფა construction-ზე; deferred candidate-ის accept agreement fraction-ითა და symbolic verdict-ით; adversarial candidate-ის უარყოფა მაშინაც, როცა declared sample set-ზე agreement სრულია; zero-denominator წერტილების იდენტიფიკაცია და `conditional` verdict; loop cost-ის განსხვავება იქ, სადაც single-step cost იდენტურია; და 0028 control-ის სამივე commitment ზუსტად pinned. მათ გარდა pinned-ია: `b = 7` off-grid pole-ის უარყოფა და `b = 3` on-grid control; ორივე მიმართულება (narrowing/widening), ორივე ბადეზე და ბადის გარეთ; ცარიელი და vacuous sample set-ის fail-closed; undecidable domain comparison-ის fail-closed; `Eq(b, 7)`-ის verdict-ის განსხვავება `unsatisfiable`-სგან; და candidate-ის precondition-ის verdict `Discharge` record-ის შიგნით.

### Mutation testing

იზოლირებულ ასლზე (repository tree-ს არ ეხება), თითო mutant ცალკე, `obligation`-ის სტრიქონსა და definedness/admissibility მექანიზმზე:

```text
M1  drop sample_total from the obligation                          caught
M2  drop domain_match from the obligation                          caught
M3  drop symbolic_verdict from the obligation                      caught
M4  drop precondition_admissible from the obligation               caught
M5  definedness decided by the sample set alone                    caught
M6  definedness drops its sample corroboration                     caught
M7  an undecidable domain comparison counts as a match             caught
M8  no divisor collected from the declared walk                    caught
M9  undecided divisors no longer make the comparison undecided     caught
M10 a vacuous sample set counts as total agreement                 caught
M11 the encoded precondition ignores its symbolic verdict          caught
M12 the decode's own poles are never collected                     caught
M13 a declared encoding domain no longer forces undecidability     caught
M14 holding nowhere on the sample grid is called unsatisfiable     caught

14/14 caught
```

M1 და M2 ის ორი mutant-ია, რომლებიც წინა რევიზიაზე გადარჩნენ: `discharged`-ის სამი conjunct-იდან ორი არაფრით არ იყო დაფიქსირებული. M6, M7 და M9 იმიტომ საჭიროებენ პირდაპირ pin-ს, რომ სწორ კოდში ისინი ვერასოდეს ჩნდებიან — `matched`-ის ორი ნახევარი და symbolic/sampled definedness ერთმანეთს ვერ ეწინააღმდეგებიან, სანამ ორივე სწორია — ე.ი. მათი გაწყვეტა მხოლოდ property-ის პირდაპირი მტკიცებით ან symbolic ნახევრის განზრახ მოტყუებით ჩანს.
