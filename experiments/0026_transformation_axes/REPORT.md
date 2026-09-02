# ParseAtlas ექსპერიმენტი 0026: transformation axes beyond field arithmetic

## მიზანი

ეს არის პირველი card, რომელიც ParseAtlas-ს **equivalence-preserving mode**-ში უშვებს. ექსპერიმენტები `0001`-დან `0025`-მდე semantic-exploration mode-ში მუშაობდნენ: სხვა grammar სხვა function-ს იძლეოდა და საზომი იყო, თუ სად გადავიდა meaning. აქ meaning fixed-ია — ყოველი admitted candidate აკმაყოფილებს `R1(x) == R2(x)`-ს declared domain-ზე — და საზომი ის არის, თუ როგორ გადავიდა **representation**. ორი mode არასდროს ერევა ერთმანეთში: `src/parseatlas/transformation_axes.py` grammar registry-ს არ კითხულობს.

Owner-მა external project `UltrafastSecp256k1`-ზე (branch `experiment/representation-search`) წარმართა equivalence-preserving representation search production secp256k1 field arithmetic-ზე. მისი გაზომილი შედეგები: `5894` rewrite ცდა `12` point formula-ზე, `1494` distinct equivalent program შენახული, `0` unsound, `48` magnitude-rejected; საუკეთესო improvement `-0.34%`, ანუ noise-ის შიგნით. ის, რომ ეს formulas **local optimum**-ია ამ rewrite space-ში, იმ domain-ზე გაზომილი ფაქტია.

იმავე external search-ის მეორე შედეგი — და სწორედ ის, რამაც ეს card წარმოშვა — ის იყო, რომ **operation-count model hardware-თან შედარებით `13x`-მდე ცდებოდა**: rewrite-ები, რომლებსაც operation count ერთნაირად აფასებდა, გაზომილ დროში ერთი რიგით სცილდებოდნენ ერთმანეთს. ორივე external რიცხვი owner-ისგან მოდის და ამ repository-ში **არ არის** გადამოწმებული; ისინი აქ motivation-ია და არა evidence.

ამ card-ის კითხვა ვიწროა და მთლიანად შიდაა: იგივე ხუთი axis ჩვეულებრივ მათემატიკურ formulas-ზე, იმ domains-იდან რომლებსაც ParseAtlas უკვე ფარავს ექსპერიმენტებში `0006`-`0011`, რამდენ **structurally** იაფ equivalent representation-ს აღწევს, და ეთანხმებიან თუ არა operation count და critical-path depth ერთმანეთს იმაზე, რომელი candidate არის იაფი.

**პასუხი ერთი აბზაცით, და ის NEGATIVE TRANSFER-ია.** ამ corpus-ზე, symbolic დონეზე, operation count depth-ის **კარგი** predictor-ია: Spearman rho `0.8428` `227` admitted candidate-ზე. ის მაინც **ბრმაა** კონკრეტული არაცარიელი subset-ისთვის — candidates, რომლებიც depth-ს ამცირებენ operation count-ის შემცირების გარეშე — და ეს subset არაცარიელია ყველა შემოწმებულ depth convention-ზე. ანუ ის external შედეგი, რომელმაც ეს card წარმოშვა (operation-count model hardware-თან შედარებით `13x`-მდე ცდება), აქ **პირდაპირ არ გადმოდის**. სავარაუდო მიზეზი — და ეს არის ჰიპოთეზა და არა დასკვნა — ის არის, რომ field-arithmetic შედეგს hardware effects მართავს (data movement, ILP ceiling, register pressure), რომლებიც symbolic დონეზე საერთოდ არ არსებობს. დეტალები `ინტერპრეტაცია`-ში.

## Axis vocabulary

Vocabulary **დახურულია**, იმავე დისციპლინით რომლითაც `case_studies/RECORD_SCHEMA.md` section 4 არის დახურული: statistics მხოლოდ მაშინ არის მნიშვნელოვანი, როცა labels სტაბილურია. აღურიცხავი label არის rejection და არა ახალი class — `generate_candidates` უცნობ axis-ზე `ValueError`-ს აგდებს.

| axis | rewrite rules |
| --- | --- |
| `mul_square_trade` | `2*a*b = (a+b)**2 - a**2 - b**2`, `a*b = ((a+b)**2 - (a-b)**2)/4`, `a**2 - b**2 = (a-b)*(a+b)`, perfect-square recognition |
| `sign_placement` | additive factor-ის sign-ის flip compensation-ით, negation-ის hoisting Add-იდან |
| `algebraic_rewrite` | `factor`, `expand`, `factor_terms`, `together`, `cancel`, `collect` per free symbol |
| `operation_fusion` | `a + a <-> 2*a`, constant-multiple decomposition `n*a -> a + (n-1)*a` და `n*a -> p*(q*a)` |
| `common_subexpression_reuse` | `cse` plus frequency-based hoist; შედეგი straight-line program-ია და არა ერთი expression |

ორი rule ამ vocabulary-დან SymPy-ში **არ არის representable** და ეს ჩაწერილია და არა ჩუმად ამოგდებული:

- `sub <-> add + neg` — SymPy-ის canonical form `a - b`-სთვის უკვე `Add(a, Mul(-1, b))`-ია, ანუ transformation უკვე შესრულებულია representation-ის დონეზე;
- `a + a -> 2*a` fusing მიმართულება — `Add.flatten` მას ავტომატურად აკეთებს, ამიტომ მხოლოდ decomposing მიმართულებაა ასაგები და ის `evaluate=False`-ით შენდება.

## Cost model

`structural_cost` აბრუნებს operation counts by kind (`add`, `mul`, `div`, `pow`, `neg`, `func`), `total_operations`-ს და `depth`-ს.

Depth-ის განმარტება `src/parseatlas/critical_path.py`-დან მოდის, ანუ **depth ითვლის leaf level-ს**: leaf არის `depth = 1` და binary internal node ერთ დონეს ამატებს. SymPy associative operators-ს აბრტყელებს, ამიტომ `a + b + c + d` ერთი ოთხარგუმენტიანი `Add`-ია და დაკარგული binary tree აღარ აღდგება. `k > 2`-ზე charge ამიტომ **დაშვებაა და არა გაზომვა**, და სამივე დაშვება named parameter-ია (`structural_cost(expr, depth_convention)`), რომ არჩევანი დამალული არ იყოს:

| `depth_convention` | k-არგუმენტიან node-ზე charge | წაკითხვა |
| --- | --- | --- |
| `balanced` (default) | `ceil(log2(k))` | balanced reduction tree |
| `left_chain` | `k - 1` | სრულად სერიული left-leaning chain |
| `flat` | `1` | ერთი k-შესასვლელიანი ოპერაცია |

`k <= 2`-ზე სამივე ერთი და იგივეა, ანუ ყველა node-ზე რომელსაც SymPy binary-ად ტოვებს, სამივე convention `critical_path.py`-ს კონსტრუქციით ემთხვევა და არჩევანი უხილავია. Test-ები `test_structural_cost_depth_matches_the_critical_path_convention` და `test_all_three_depth_conventions_agree_wherever_sympy_keeps_the_tree_binary` სამ shared expression-ზე ამას ამტკიცებენ, `test_the_depth_conventions_diverge_exactly_on_a_flattened_node` კი აჩვენებს, სად და რამდენად სცილდებიან ისინი ერთმანეთს. რომელი შედეგი რომელ convention-ზეა დამოკიდებული — `Depth convention-ის sensitivity`-შია.

Reuse candidate program-ია, ამიტომ temporary არ არის leaf: მისი depth მისი defining right-hand side-ის depth-ია. სწორედ ეს ხდის reuse axis-ს საზომს.

## Proof obligation

Candidate admitted-ია მხოლოდ მაშინ, როცა **ორივე** სრულდება:

1. `simplify(original - candidate) == 0`;
2. ორივე representation-ის `excluded_points` ერთი და იგივე set-ია, გამოთვლილი `canonical.undefined_terms`-ის მეთოდით — ყოველი division, რომლის divisor არ არის non-zero literal, იხსნება თავისი პირველი free symbol-ისთვის სახელის მიხედვით.

**(2) არ ნიშნავს "domain preserved"-ს და report ამას არსად არ ამბობს.** SymPy tree-ზე ეს rule ზუსტად ერთ shape-ს ცნობს — `Pow(base, უარყოფითი რიცხვი)` — და სხვას არაფერს. მისი სამი ცნობილი ხვრელი ჩამოთვლილია `შეზღუდვები`-ში და pinned-ია test-ით; არცერთი მათგანი ამ corpus-ს არ ეხება, რადგან corpus-ში არ არის არც radical, არც logarithm და არც symbolic exponent, და მასში ყოველი division სწორედ ამ shape-ისაა.

(1)-ის დაკმაყოფილება (2)-ის დარღვევით ნიშნავს, რომ rewrite-მა division restriction წაშალა — `x/x -> 1` failure mode — და ეს არის `domain_violating` **rejection**, ცალკე დათვლილი, არასდროს win და არასდროს equivalent count-ში ჩარეული.

Numeric probe deterministic non-integer rational sample points-ზე დამოუკიდებელ შემოწმებას აკეთებს და sample set **ორივე ნიშნისაა**. ის domain violation-ს **ვერ ხედავს** — `x/x` და `1` ყოველ იმ point-ზე ემთხვევა, სადაც ორივე განსაზღვრულია — ამიტომ მისი verdict ჩაიწერება და symbolic verdict-თან შეუთანხმებლობა flag-დება, მაგრამ არ გადაწონის symbolic-ს.

## Corpus

`40` formula, `8` domain, თითო domain-ზე `5`. Corpus რეპროდუცირებადია მხოლოდ ამ report-იდან და ის `CORPUS`-ია `src/parseatlas/transformation_axes.py`-ში.

```text
quadratic_equations
    q_discriminant           b**2 - 4*a*c
    q_vertex_x               -b/(2*a)
    q_vertex_y               c - b**2/(4*a)
    q_standard_form          a*x**2 + b*x + c
    q_completed_square       a*(x + b/(2*a))**2 + c - b**2/(4*a)

geometry
    g_squared_distance       (x2 - x1)**2 + (y2 - y1)**2
    g_shoelace_area          (x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))/2
    g_rotation_x             x*cos(t) - y*sin(t)
    g_rotation_y             x*sin(t) + y*cos(t)
    g_dot_product            x1*x2 + y1*y2

algebra
    a_binomial_square        (a + b)**2
    a_binomial_cube          (a + b)**3
    a_difference_of_squares  a**2 - b**2
    a_common_factor          a*b + a*c
    a_cancelling_quotient    (a**2 - b**2)/(a - b)

calculus
    c_cubic_derivative       3*a*x**2 + 2*b*x + c
    c_product_rule           u*dv + v*du
    c_quotient_rule          (v*du - u*dv)/v**2
    c_taylor_second_order    f0 + f1*h + f2*h**2/2
    c_chain_rule             2*x*cos(x**2)

trigonometry
    t_angle_sum_sin          sin(a)*cos(b) + cos(a)*sin(b)
    t_double_angle_cos       cos(x)**2 - sin(x)**2
    t_double_angle_sin       2*sin(x)*cos(x)
    t_pythagorean            sin(x)**2 + cos(x)**2
    t_tangent_quotient       sin(x)/cos(x)

number_theory
    n_triangular             n*(n + 1)/2
    n_cubic_minus_linear     n**3 - n
    n_odd_gap                (n + 1)**2 - n**2
    n_consecutive_product    n*(n + 1)*(n + 2)
    n_two_squares_product    (a**2 + b**2)*(c**2 + d**2)

differential_equations
    d_harmonic_solution      A*cos(w*t) + B*sin(w*t)
    d_harmonic_energy        (v**2 + w**2*x**2)/2
    d_logistic_rhs           r*y*(1 - y/K)
    d_logistic_solution      K/(1 + ((K - y0)/y0)*exp(-r*t))
    d_damped_oscillator      A*exp(-c*t)*cos(w*t)

probability_statistics
    p_binomial_pmf           3*p**2*(1 - p)
    p_binomial_variance      n*p*(1 - p)
    p_normal_exponent        -(x - m)**2/(2*s**2)
    p_variance_identity      e2 - e1**2
    p_z_score                (x - m)/s
```

`40` formula `x` `5` axis = `200` (formula, axis) task.

## დაკვირვებული შედეგები

Sweep-ის totals:

```text
candidates generated          231
verified equivalent           227
domain_violating rejections     4
unsound rejections              0
symbolic/numeric disagreements  0
```

### Per-axis yield

| axis | cand | equiv | domain_viol | unsound | red. ops | red. depth | red. both | red. depth only | Spearman rho |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `mul_square_trade` | 105 | 104 | 1 | 0 | 1 | 1 | 1 | 0 | 0.582 |
| `sign_placement` | 46 | 46 | 0 | 0 | 1 | 3 | 1 | 2 | 0.853 |
| `algebraic_rewrite` | 67 | 64 | 3 | 0 | 5 | 10 | 2 | 8 | 0.630 |
| `operation_fusion` | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0.379 |
| `common_subexpression_reuse` | 3 | 3 | 0 | 0 | 2 | 0 | 0 | 0 | 1.000 |
| **total** | **231** | **227** | **4** | **0** | **9** | **14** | **4** | **10** | **0.843** |

Aggregate kind deltas verified-equivalent candidates-ზე, ანუ რომელი operation kind იზრდება ან მცირდება თითო axis-ზე:

| axis | add | mul | div | pow | neg | func |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `mul_square_trade` | +346 | +156 | +30 | +280 | +72 | +37 |
| `sign_placement` | +0 | +0 | +0 | +0 | +72 | +0 |
| `algebraic_rewrite` | +21 | +98 | +5 | +36 | -31 | +3 |
| `operation_fusion` | +16 | +8 | +0 | +7 | +9 | +3 |
| `common_subexpression_reuse` | +0 | -1 | -1 | +0 | +1 | +0 |

### Per-domain yield

| domain | cand | equiv | domain_viol | unsound | red. ops | red. depth | red. both | red. depth only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| quadratic_equations | 32 | 31 | 1 | 0 | 1 | 0 | 0 | 0 |
| geometry | 50 | 50 | 0 | 0 | 1 | 1 | 0 | 1 |
| algebra | 20 | 18 | 2 | 0 | 1 | 0 | 0 | 0 |
| calculus | 29 | 29 | 0 | 0 | 0 | 0 | 0 | 0 |
| trigonometry | 13 | 13 | 0 | 0 | 0 | 0 | 0 | 0 |
| number_theory | 25 | 25 | 0 | 0 | 2 | 2 | 2 | 0 |
| differential_equations | 37 | 36 | 1 | 0 | 2 | 6 | 0 | 6 |
| probability_statistics | 25 | 25 | 0 | 0 | 2 | 5 | 2 | 3 |

### Operation count versus depth

Spearman rank correlation operation-count delta-სა და depth delta-ს შორის, ყველა `227` verified-equivalent candidate-ზე:

```text
rho = 0.8428    n = 227
```

Sign agreement table, `sign(operation_delta)/sign(depth_delta)`:

```text
+1/+1   162      ორივე იზრდება
+1/+0    30      ops იზრდება, depth უცვლელი
 0/+0    15      ორივე უცვლელი
 0/-1     6      ops უცვლელი, depth მცირდება
-1/+0     5      ops მცირდება, depth უცვლელი
+1/-1     4      ops იზრდება, depth მცირდება
-1/-1     4      ორივე მცირდება
 0/+1     1      ops უცვლელი, depth იზრდება

sign disagreements   46 / 227  =  20.3%
```

Depth-reducing candidates invisible to an operation-count model: `10` of `14` **balanced depth convention-ზე**. ანუ იმ candidates-ის, რომლებიც critical-path depth-ს ამცირებენ, `10` operation count-ს **არ** ამცირებს: `6` მათგანი operation count-ს უცვლელს ტოვებს და `4` მას ზრდის. მაგრამ ეს კონკრეტული `10` არ არის bare fact — ის ნაწილობრივ convention-ია, და შემდეგი ორი ქვეთავი ზუსტად ამას ზომავს.

### Depth convention-ის sensitivity

`10 of 14` ითქმის იმ ერთეულებში, რომლებსაც n-ary node-ის depth charge ნაწილობრივ ადგენს. SymPy associative operator-ს აბრტყელებს და binary tree აღარ აღდგება, ამიტომ `k > 2`-ზე charge **დაშვებაა**. სამივე დაშვება module-შია (`DEPTH_CONVENTIONS`) და sweep სამივეზე გაშვებულია — ეს არის `depth_convention_sensitivity()`:

| convention | k-ზე charge | red. depth | red. both | **invisible (depth only)** | Spearman rho | sign disagreements |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `balanced` (default) | `ceil(log2(k))` | 14 | 4 | **10** | 0.8428 | 46 |
| `left_chain` | `k - 1` | 9 | 4 | **5** | 0.8810 | 28 |
| `flat` | `1` | 18 | 4 | **14** | 0.7427 | 59 |

რა **არ** მოძრაობს convention-ით: `candidates = 231`, `equivalent = 227`, `domain_violating = 4`, `unsound = 0`, `reduces_operations = 9`, `reduces_both = 4` — სამივეზე იდენტურია. Convention admission-ის შემდეგ გამოიყენება, ამიტომ ვერ ცვლის იმას, რა იქნა admitted, და ვერც იმას, რას ხედავს operation-count model; მხოლოდ depth-ს ცვლის. ამას `test_the_depth_convention_moves_depth_alone_and_never_the_verdicts` ამტკიცებს.

რა **მოძრაობს**: თვითონ headline count-ი, `5`-დან `14`-მდე, ანუ დაახლოებით `3x` diapazon-ში, `10` კი მის შუაშია. ამიტომ `10` არ არის გაზომვა — ის `balanced` convention-ის ქვეშ გაზომილი რიცხვია და ასე უნდა იკითხებოდეს.

რა არის **invariant**, ანუ რა არის ამ ქვეთავის ნამდვილი დასკვნა:

1. set **არასდროს ცარიელია**: `5`, `10` და `14` — არცერთ convention-ზე operation-count model depth-reducing candidates-ის სრულ სიმრავლეს ვერ ფარავს;
2. rho **არასდროს არის `1`-თან ახლოს**: `0.743`-დან `0.881`-მდე, ანუ არცერთ convention-ზე ორი metric ერთი და იგივე არ არის;
3. `reduces_both = 4` სამივეზე, ანუ ის candidates, რომლებსაც ორივე metric ხედავს, convention-ისგან დამოუკიდებელია.

### Headline-ის კონცენტრაცია

`10` invisible candidate `40`-ვე formula-ს არ ეკუთვნის. ისინი `4` formula-დან მოდიან:

| formula | domain | invisible candidates | აქედან axis |
| --- | --- | ---: | --- |
| `d_logistic_rhs` | differential_equations | **6** | `algebraic_rewrite` 5, `sign_placement` 1 |
| `p_binomial_variance` | probability_statistics | 2 | `algebraic_rewrite` 1, `sign_placement` 1 |
| `p_binomial_pmf` | probability_statistics | 1 | `algebraic_rewrite` 1 |
| `g_shoelace_area` | geometry | 1 | `algebraic_rewrite` 1 |

ანუ `10`-იდან `6` **ერთი formula-დან** მოდის (`r*y*(1 - y/K)`) და კიდევ `3` ორი მჭიდროდ ნათესავი formula-დან (`3*p**2*(1 - p)` და `n*p*(1 - p)` — ორივე იგივე `X*(1 - X)` shape-ია). სამი formula `40`-დან ამ headline-ის `90%`-ს ქმნის.

კონცენტრაცია თვითონ convention-დამოკიდებულია, მაგრამ თვისობრივად არა:

| convention | invisible | distinct formulas (of 40) | ყველაზე დიდი წვლილი |
| --- | ---: | ---: | --- |
| `balanced` | 10 | 4 | `d_logistic_rhs` 6 |
| `left_chain` | 5 | 2 | `d_logistic_rhs` 4 |
| `flat` | 14 | 6 | `q_completed_square` 4 |

ანუ არცერთ convention-ზე invisible set არ არის corpus-ის მასშტაბის მოვლენა: მაქსიმუმ `6` formula `40`-დან მას მთლიანად აწარმოებს.

### Domain-violating rejections

`4` rejection, ყველა `simplify`-ის მიხედვით symbolically equal, მაგრამ excluded points-ის შეცვლით:

| formula | axis | original | candidate | excluded before | excluded after |
| --- | --- | --- | --- | --- | --- |
| `a_cancelling_quotient` | `algebraic_rewrite` | `(a**2 - b**2)/(a - b)` | `a + b` | `['b']` | `[]` |
| `a_cancelling_quotient` | `mul_square_trade` | `(a**2 - b**2)/(a - b)` | `a + b` | `['b']` | `[]` |
| `q_completed_square` | `algebraic_rewrite` | `a*(x + b/(2*a))**2 + c - b**2/(4*a)` | `a*x**2 + b*x + c` | `['0']` | `[]` |
| `d_logistic_solution` | `algebraic_rewrite` | `K/(1 + (K - y0)*exp(-r*t)/y0)` | `K*y0*exp(r*t)/(K + y0*exp(r*t) - y0)` | `['y0*(1 - exp(r*t))', '0']` | `['y0*(1 - exp(r*t))']` |

კონკრეტული მაგალითი: `(a**2 - b**2)/(a - b)` განსაზღვრული არ არის `a = b`-ზე, ხოლო `a + b` ყველგან განსაზღვრულია. `simplify(original - candidate)` არის `0`, numeric probe ყველა safe point-ზე თანხმდება, და მიუხედავად ამისა ეს **არ არის** equivalent rewrite — ეს არის სხვა function. `q_completed_square` იგივე failure mode-ია `a = 0`-ზე, `d_logistic_solution` კი ნაწილობრივი: ორი restriction-იდან ერთი ქრება.

### აღწეული structural improvements

`19` verified-equivalent candidate ამცირებს ან operation count-ს, ან depth-ს, ან ორივეს. საუკეთესოები:

| formula | domain | axis | before | after | ops | depth |
| --- | --- | --- | --- | --- | --- | --- |
| `n_odd_gap` | number_theory | `mul_square_trade` | `-n**2 + (n + 1)**2` | `2*n + 1` | 5 -> 2 | 4 -> 3 |
| `n_odd_gap` | number_theory | `algebraic_rewrite` | `-n**2 + (n + 1)**2` | `2*n + 1` | 5 -> 2 | 4 -> 3 |
| `d_logistic_rhs` | differential_equations | `algebraic_rewrite` | `r*y*(1 - y/K)` | `r*y*(K - y)/K` | 6 -> 6 | 7 -> 5 |
| `g_shoelace_area` | geometry | `algebraic_rewrite` | `x1*(y2 - y3)/2 + x2*(-y1 + y3)/2 + x3*(y1 - y2)/2` | `(x1*(y2 - y3) + x2*(-y1 + y3) + x3*(y1 - y2))/2` | 14 -> 12 | 7 -> 7 |
| `p_binomial_pmf` | probability_statistics | `sign_placement` | `3*p**2*(1 - p)` | `-3*p**2*(p - 1)` | 5 -> 4 | 5 -> 4 |
| `a_common_factor` | algebra | `algebraic_rewrite` | `a*b + a*c` | `a*(b + c)` | 3 -> 2 | 3 -> 3 |
| `d_harmonic_solution` | differential_equations | `common_subexpression_reuse` | `A*cos(t*w) + B*sin(t*w)` | `_t0 = t*w; A*cos(_t0) + B*sin(_t0)` | 7 -> 6 | 5 -> 5 |

### Sequential versus parallel

`os.cpu_count() = 16`, worker count `worker_count_for(16) = max(1, min(16 - 2, 12)) = 12`, ანუ ორი core headroom-ად რჩება, რომ სრულმა sweep-მა interactive session ვერ დაახრჩოს. **შვიდი** alternating run თითო mode-ზე, სრულ `40`-formula corpus-ზე, review-ის შემდეგი fix-ების გაშვების შემდეგ ხელახლა გაზომილი:

```text
sequential (workers=1)   7.18  7.14  5.57  5.56  6.87  6.26  6.10   median 6.26 s
parallel   (workers=12)  4.01  3.27  3.43  3.26  3.40  3.55  3.47   median 3.43 s
ratio (median)           1.83x
```

წინა გაზომვა (`5.98` / `3.23` / `1.85x`, ხუთი run) ამავე machine-ზე იყო; ხელახალი გაზომვისას ამავე tree-ში სხვა worker პარალელურად ატარებდა თავის suite-ს, ამიტომ absolute wall-clock ოდნავ მაღალია და მისი tail contended-ია. მნიშვნელოვანი რიცხვი — ratio — რეპროდუცირდა: `1.83x` წინა `1.85x`-ის წინააღმდეგ. `DEFAULT_WORKERS`-ის კომენტარი ახალ გაზომვაზეა განახლებული.

Parallel იგებს, ამიტომ `DEFAULT_WORKERS = default_worker_count()` და parallel path არის default; `workers=1` sequential path-ს ზუსტად იმეორებს. Parallelism მხოლოდ სისწრაფეს ცვლის და არა იმას, რაც იზომება: `executor.map` order-ს ინახავს, `_pool_task` თავისი payload-ის pure function-ია (module-level, Windows `spawn` start method-ისთვის), და test `test_sequential_and_parallel_reports_are_identical` ორ report-ს იდენტურად ამტკიცებს ორი execution-mode field-ის გარდა.

**ეს ერთადერთი wall-clock რიცხვი ამ report-ში არის analysis harness-ის საკუთარი runtime და არაფრის სხვის.**

## ინტერპრეტაცია

**პროდუქტიული axes.** `algebraic_rewrite` ერთადერთი axis-ია, რომელიც ორივე metric-ზე თანმიმდევრულად აწარმოებს: `14` depth reduction-იდან `10` და `9` operation reduction-იდან `5` მისია. მისი yield კი **domain-ის და არა formula-ს დონეზე არ არის აღწერადი**: cell `differential_equations|algebraic_rewrite`-ს აქვს `9` candidate და `5` depth reduction, მაგრამ ხუთივე ერთი formula-დან, `d_logistic_rhs`-დან მოდის, რომლის ხუთივე `algebraic_rewrite` candidate depth-ს ამცირებს; domain-ის დანარჩენი ოთხი formula ამ cell-ში `0` depth reduction-ს იძლევა. იგივე `probability_statistics|algebraic_rewrite`-ზე: `3` depth reduction, ორი `p_binomial_pmf`-დან და ერთი `p_binomial_variance`-დან. ამიტომ სწორი ფორმულირება არის "ამ სამმა formula-მ იძლევა", და არა "ამ domains-მა იძლევა" — ეს არის `n = 1` და `n = 2` formula-ზე დაკვირვება domain-ის label-ის ქვეშ. `sign_placement` ვიწროდ პროდუქტიულია — `3` depth reduction `46` candidate-იდან — და მისი kind-delta signature მკვეთრია: `add`, `mul`, `div`, `pow`, `func` ზუსტად ნულია და მხოლოდ `neg` იცვლება, ანუ axis იმას აკეთებს, რასაც label ჰპირდება, და სხვას არაფერს. `mul_square_trade` ყველაზე მეტ candidate-ს (`105`) აწარმოებს და თითქმის ყოველთვის აძვირებს: aggregate kind deltas ყველა kind-ზე დადებითია და მისი ერთადერთი win `n_odd_gap`-ია. `common_subexpression_reuse` მხოლოდ `3` candidate-ს იძლევა `40` formula-ზე, რადგან textbook formulas იშვიათად იმეორებენ non-atomic subexpression-ს; ორივე მისი win operation-count-ია და არცერთი — depth.

**Inert axes.** არცერთი axis არ არის zero-candidate ამ corpus-ზე, მაგრამ `operation_fusion` არის **inert as an optimisation axis**: `10` candidate, `10` verified equivalent, `0` operation reduction, `0` depth reduction. ამის მიზეზი structural-ია და არა მათემატიკური — SymPy-ის canonical Add/Mul უკვე ასრულებს fusing მიმართულებას, ამიტომ ხელმისაწვდომია მხოლოდ decomposing მიმართულება, ეს კი განსაზღვრებით ამატებს node-ებს. `sub <-> add + neg` საერთოდ არ არის representable. ანუ ამ axis-ის შესახებ გაზომილი დასკვნა ეხება SymPy-ის representation-ს და არა arithmetic-ს.

**Inert domains, და რატომ არის "domain" აქ არასწორი ერთეული.** `calculus` (`29` candidate) და `trigonometry` (`13` candidate) ამ rewrite set-ზე **ვერცერთ** improvement-ს ვერ იძლევიან, ვერც operation count-ზე და ვერც depth-ზე. `quadratic_equations` (`32` candidate) და `algebra` (`20`) თითო operation reduction-ს იძლევიან და ვერცერთ depth reduction-ს. Per-domain table `differential_equations`-ს `6` depth reduction-ს და `probability_statistics`-ს `5`-ს აწერს, მაგრამ ეს რიცხვები domain-ის თვისებად **არ იკითხება**: `differential_equations`-ის ექვსივე ერთი formula-დანაა (`d_logistic_rhs`), `probability_statistics`-ის ხუთივე კი ორიდან (`p_binomial_pmf` `3`, `p_binomial_variance` `2`). მთელი corpus-ის `14` depth reduction `5` formula-დან მოდის — `d_logistic_rhs` `6`, `p_binomial_pmf` `3`, `n_odd_gap` `2`, `p_binomial_variance` `2`, `g_shoelace_area` `1` — ანუ `35` formula-ს `40`-დან **არცერთი** depth reduction არ აქვს. ეს არ არის domain-ის დონის სიგნალი; ეს არის რამდენიმე formula, რომელთაც shape `X*(1 - X/Y)` აქვთ.

**Headline: operation count depth-ის კარგი predictor-ია, ოღონდ არა სრული.** Aggregate Spearman rho `0.8428` `227` candidate-ზე **ძლიერი correlation-ია**, და ეს პირველ რიგში უნდა ითქვას: ამ ჩვეულებრივ მათემატიკურ formulas-ზე, symbolic დონეზე, operation count საშუალოდ სწორად პროგნოზირებს depth-ს. candidates-ის უმრავლესობა (`162` of `227`) ორივეს ერთდროულად ზრდის, `4` ორივეს ამცირებს, და ორი metric ერთმანეთს იშვიათად ეწინააღმდეგება.

მაგრამ aggregate rho არ არის coverage. Sign disagreement rate არის `20.3%`, per-axis rho კი `0.379`-დან (`operation_fusion`) `0.853`-მდე (`sign_placement`) მერყეობს. და გადამწყვეტი: **არსებობს არაცარიელი subset, რომელსაც operation-count model ვერ ხედავს — candidates, რომლებიც depth-ს ამცირებენ operation count-ის შემცირების გარეშე.** `balanced` convention-ზე ის `10` candidate-ია `14`-იდან; `left_chain`-ზე `5` of `9`; `flat`-ზე `14` of `18`. სამივე რიცხვი გაზომილია, არცერთი არ არის `0`, და კონკრეტული მნიშვნელობა convention-ის არჩევანზეა დამოკიდებული დაახლოებით `3x`-ის ფარგლებში. ამიტომ ამ headline-ის მტკიცე ფორმა არის თვისობრივი და არა რაოდენობრივი: **set არაცარიელია ყველა შემოწმებულ convention-ზე და rho არასდროს არის `1`-თან ახლოს**; `10` კი არის ამ set-ის ზომა `balanced` convention-ის ქვეშ და მხოლოდ იქ.

ეს set ამასთან **მცირეა და კონცენტრირებული**: `10`-იდან `6` ერთი formula-დანაა, `9` კი სამიდან. `n = 14` depth-reducing candidate `227`-იდან იმავე მასშტაბის მცირე ნიმუშია, რასაც `common_subexpression_reuse`-ის `rho = 1.000` `n = 3`-ზე — და იმავე დათქმას იმსახურებს: ამ `14`-ზე (და მით უმეტეს `10`-ზე) აგებული ნებისმიერი proportion ერთეულოვანი candidate-ის დამატება-გამოკლებაზე მკვეთრად რეაგირებს, და მისი გადატანა სხვა corpus-ზე გაზომილი არ არის. ის, რაც აქ measured-ია, არის არსებობა და არა სიხშირე.

ამ corpus-ზე operation count და depth ერთსა და იმავეს არ ზომავენ, და cost model, რომელიც მხოლოდ ერთს ითვლის, ამ ვიწრო set-ს კარგავს. ეს ეთანხმება ექსპერიმენტ `0021`-ის დასკვნას, რომ raw operation multiset grammar-ის ცვლილებას ვერ გამოხატავს.

**Ultrafast-თან მიმართება: ეს არის გაზომილი NEGATIVE TRANSFER.** ამ card-ის მოტივაცია external Ultrafast-ის შედეგი იყო, სადაც operation-count model hardware-თან შედარებით `13x`-მდე ცდებოდა. ეს **არ არის** ის, რაც აქ გაიზომა, და report ამას პირდაპირ ამბობს და არ არბილებს:

1. ამ ჩვეულებრივ formulas-ზე, symbolic დონეზე, operation count depth-ის **კარგი** predictor-ია საშუალოდ: rho `0.843`, sign agreement `79.7%`;
2. ის მაინც **ბრმაა** კონკრეტული subset-ისთვის — candidates, რომლებიც depth-ს ამცირებენ operation count-ის შემცირების გარეშე — და ეს subset არაცარიელია ყველა შემოწმებულ depth convention-ზე;
3. ამიტომ Ultrafast-ის შედეგი **პირდაპირ არ გადმოდის**. `13x` სახის შეუსაბამობა აქ არ გვხვდება; რაც გვხვდება, არის გაცილებით სუსტი და კარგად ლოკალიზებული ბრმა ლაქა.

მიზეზი, **ჰიპოთეზის სახით და არა დასკვნის სახით**: Ultrafast-ის field-arithmetic შედეგს სავარაუდოდ hardware effects მართავს — data movement, ILP-ის ჭერი, register pressure — რომლებიც symbolic დონეზე, რომელსაც ეს ექსპერიმენტი ზომავს, **საერთოდ არ არსებობს**. Symbolic tree-ს არ აქვს არც register file და არც cache; ამიტომ ის, რომ symbolic depth და symbolic operation count კარგად თანხმდებიან, არაფერს ამბობს იმაზე, თანხმდება თუ არა operation count მანქანურ დროსთან. ამ ჰიპოთეზის შემოწმება ამ card-ის ფარგლებში არ არის და მისი გაზომვა ჩვენ არ გვიცდია.

**რაც აქ ჯერ კიდევ არ ითქვა.** Rewrite set-ის საერთო პროდუქტიულობა დაბალია: admitted candidates-ის მხოლოდ `4.0%` (`9` of `227`) ამცირებს operation count-ს და `6.2%` (`14` of `227`) depth-ს, ანუ median candidate უარესია, ვიდრე original. ის, თუ ეს corpus-ის თვისებაა თუ rewrite set-ის, ერთი corpus-ით არ წყდება; ეს არის ჰიპოთეზა შემდეგი card-ისთვის და არა ამ card-ის დასკვნა.

**და ბოლოს.** Structural improvement არის **ჰიპოთეზა cost-ის შესახებ და არა გაზომილი speedup.** `n_odd_gap`-ის `5 -> 2` operation reduction ნიშნავს, რომ SymPy tree-ს სამით ნაკლები node აქვს. ეს არ ნიშნავს, რომ compiled implementation უფრო სწრაფია, არ ნიშნავს, რომ instruction count მცირდება, და არაფერს ამბობს cache-ის, register pressure-ის ან latency-ის შესახებ.

## შეზღუდვები

- ეს ექსპერიმენტი **structure-ს ზომავს და მხოლოდ structure-ს**. არცერთი wall-clock ან speedup claim formulas-ის შესახებ არ არის და არ შეიძლება იყოს გაკეთებული. SymPy operation count არ არის machine cost, და symbolic rewrite-ის Python-level timing არაფერს ამბობს compiled implementation-ზე.
- `total_operations` unweighted-ია: `mul` და `add` თითო ერთად ითვლება. ამიტომ `operation_fusion`-ის `mul -> add` shift ამ metric-ში ნულოვანია by construction; kind deltas table არსებობს სწორედ იმისთვის, რომ ეს shift მაინც ჩანდეს.
- SymPy-ის canonical form artifacts გაზომვაში შედის. `1 - p` არის `Add(1, Mul(-1, p))` და მას ერთი დამატებითი node აქვს, ხოლო `p - 1` არის `Add(-1, p)`, სადაც `-1` leaf-ია. `p_binomial_pmf`-ის depth win `5 -> 4` სწორედ ამ ასიმეტრიიდან მოდის და არა arithmetic-იდან.
- Depth convention n-ary node-ზე default-ად `ceil(log2(k))`-ია, ანუ balanced reduction. Binary node-ზე ის `critical_path.py`-ს ზუსტად ემთხვევა, `k > 2`-ზე კი ის **არჩევანია და არა გაზომვა** — და ეს არჩევანი პირდაპირ ადგენს headline-ის რიცხვს. ამიტომ ის აღარ არის hardcoded: `DEPTH_CONVENTIONS` სამივე დაშვებას ინახავს, sweep სამივეზეა გაშვებული და შედეგები `Depth convention-ის sensitivity` ქვეთავშია. Headline `10` მოქმედებს `balanced`-ზე; `left_chain`-ზე ის `5`-ია და `flat`-ზე `14`-ია.
- Excluded points project-ის არსებული მეთოდით იზომება — divisor იხსნება მისი **პირველი** free symbol-ისთვის სახელის მიხედვით. ეს კოარსეა multivariable divisor-ზე და შეიძლება restriction-ის ერთი ბრანჩი დაინახოს და მეორე არა.
- **Domain check უფრო ვიწროა, ვიდრე სიტყვა "domain".** `excluded_points` ამოწმებს **მხოლოდ** `Pow`-ს **რიცხვითი უარყოფითი** exponent-ით. სამი ცნობილი ხვრელი, სამივე `tests/test_transformation_axes.py`-ში pinned:
  1. **Radical branch restriction უხილავია.** `Pow(sqrt(x), 2, evaluate=False)` მოითხოვს `x >= 0`-ს, `x` კი არა; ორივე `excluded_points`-ად `()`-ს აბრუნებს და წყვილი `equivalent`-ად ინიშნება. ეს არასწორია.
  2. **Symbolic exponent-ის ქვეშ მიმალული division უხილავია.** `Mul(Pow(x, n), Pow(x, -n, evaluate=False))` გამორიცხავს `x = 0`-ს, `1` კი არა; `-n` არ არის `is_number`, ამიტომ არ ცნობა და წყვილი `equivalent`-ად ინიშნება. ესეც არასწორია.
  3. **საწინააღმდეგო მიმართულებით over-strict.** `sin(x)/cos(x)` და `tan(x)` **ერთი და იგივე domain-ისაა**, მაგრამ `tan`-ის pole არ არის `Pow`, ამიტომ candidate-ს `[]` აწერია და original-ს `['pi/2', '3*pi/2']`; წყვილი `domain_violating`-ად უარიყოფა. ესეც არასწორია, უბრალოდ სხვა მხარეს.
  არცერთი გამოქვეყნებული რიცხვი ამ სამზე არ არის დამოკიდებული: corpus-ში არ არის არც radical, არც logarithm და არც symbolic exponent, ხოლო ყოველი მასში არსებული division explicit numeric-exponent `Pow`-ია და ოთხივე domain violation სწორად დაიჭირა. ხვრელების გაფართოება ამ card-ის scope-ში არ არის; მათი აღწერა კი იყო და აღწერა შესწორებულია.
- Search **არ არის ამომწურავი**: `max_depth = 4` rewrite site-ებზე და `limit = 16` candidate თითო (formula, axis) წყვილზე. `200` (formula, axis) წყვილიდან ამ cap-ს **ზუსტად ერთი** აღწევს — `g_shoelace_area` / `algebraic_rewrite`, `16` candidate. მეორე ყველაზე დიდი წყვილი `6` candidate-ია, ხოლო `mul_square_trade`-ის მაქსიმუმი ერთ წყვილზე `6`-ია, ანუ ის cap-ს **არსად არ აღწევს**. მაშასადამე truncation ერთი formula-ს ერთ axis-ს ეხება და არა sweep-ს ფართოდ.
- Axes მხოლოდ **ცალ-ცალკე** გამოიყენება. Composition არ არის: Ultrafast-ის superoptimizer rewrite-ებს აჯაჭვებს, აქ კი თითო candidate ერთი axis-ის ერთი გამოყენებაა. ეს search space-ის ქვესიმრავლეა.
- Axes candidate expression-ების დონეზე disjoint არ არის: `n_odd_gap`-ის ერთი და იგივე შედეგი `2*n + 1` ორმა axis-მა დამოუკიდებლად მიაღწია და ორჯერ დაითვალა, თითო თავის axis-ში. Per-axis counts ამიტომ candidate-ის მისაღწევადობას ზომავს და არა unique representations-ს.
- `40` formula მცირე corpus-ია, `3` candidate `common_subexpression_reuse`-ზე კი იმდენად მცირე, რომ მისი `rho = 1.000` სტატისტიკურად უაზროა. **იგივე სტანდარტი headline-ზეც ვრცელდება**: `14` depth-reducing candidate `227`-იდან ასევე მცირე ნიმუშია და `5` distinct formula-დან მოდის, ხოლო მათი `10`-იანი invisible ქვესიმრავლე `4` formula-დან, აქედან `6` ერთი formula-დან (`d_logistic_rhs`). ერთი candidate-ის დამატება ან გამოკლება `10 of 14`-ს და მის `71.4%`-ს მკვეთრად ცვლის; ამიტომ ამ card-ის მტკიცე claim არის set-ის **არსებობა და არაცარიელობა**, და არა მისი წილი ან სიხშირე.
- Numeric probe `3` deterministic rational point-ია და არა randomized differential test seed-ით; ის independent cross-check-ია და არა validation suite. Sample set ახლა **ორივე ნიშნისაა** (`_SAMPLE_BASE` ალტერნირებს `+`-სა და `-`-ს შორის), რაც აუცილებელი აღმოჩნდა: ცალნიშნა (მხოლოდ დადებით) sample set-ზე sign-დამოკიდებულ არა-ეკვივალენტობას probe **პრინციპულად ვერ ხედავს** — `sqrt(x*x)` და `x` ყოველ დადებით point-ზე ემთხვევა, ამიტომ probe სწორ symbolic `unsound` verdict-ს ეწინააღმდეგებოდა და `symbolic_numeric_disagreement`-ს აყენებდა. ორნიშნა sample set-ზე probe იმავე verdict-ს **ადასტურებს**. სრულ corpus-ზე ამ ცვლილებამ არცერთი გამოქვეყნებული რიცხვი არ გადაანაცვლა (`231/227/4/0`, rho `0.8428`, invisible `10`), რადგან corpus-ში sign-დამოკიდებული rewrite არ არის და ყოველი candidate სამივე point-ზე განსაზღვრული დარჩა. რაც კვლავ რჩება შეზღუდვად: `3` point, მხოლოდ rational, მხოლოდ real, და probe domain violation-ს **მაინც ვერ ხედავს** — ეს პირობა (2)-ის საქმეა და არა probe-ის.
- `0` unsound rejection ნიშნავს, რომ ამ rule set-ის ყოველი rewrite კონსტრუქციით მართებული აღმოჩნდა. ეს არის rules-ის თვისება და არა verifier-ის სიძლიერის მტკიცებულება; verifier-ის სიძლიერეს `test_verify_equivalence_rejects_a_genuinely_non_equivalent_pair` ამოწმებს.

## Evidence-ის კლასიფიკაცია

- Candidate counts, verdict counts, cost deltas, rank correlation და sign agreement table არის executable **observations** ამ corpus-ზე.
- `4` domain_violating rejection და მათი excluded-point sets არის **observations** კონკრეტულ formulas-ზე.
- Sequential/parallel timing არის harness-ის **observation** ამ machine-ზე; ის არც formulas-ის და არც rewrite-ების cost-ს არ ზომავს.
- Three-convention sensitivity table არის **observation**: სამივე რიცხვი ერთი და იმავე corpus-ის სამი გაშვებიდან მოდის, `depth_convention_sensitivity()`-ით.
- "Operation count და depth სხვადასხვას ზომავენ" არის ამ corpus-ზე დაფიქსირებული სტრუქტურა და არა universal law.
- **Headline count `10` არის observation `balanced` convention-ის ქვეშ და არა convention-დამოუკიდებელი ფაქტი**; convention-დამოუკიდებელი observation არის ის, რომ set არაცარიელია (`5`, `10`, `14`) და rho `1`-თან ახლოს არასდროსაა (`0.743`-`0.881`).
- Ultrafast-ის შედეგის **non-transfer არის claimed და გაზომილია**: აქ operation count depth-ის კარგი predictor-ია (rho `0.843`), ანუ Ultrafast-ის `13x` სახის შეუსაბამობა ამ დონეზე არ რეპროდუცირდება. ეს არის ამ corpus-ზე დაფიქსირებული **negative transfer** და არა universal law.
- Ამ non-transfer-ის **ახსნა** — რომ field-arithmetic შედეგს hardware effects (data movement, ILP ceiling, register pressure) მართავს, რომლებიც symbolic დონეზე არ არსებობს — არის **ჰიპოთეზა** და არა დასკვნა; ის ამ card-ში არ არის გაზომილი.
- არცერთი speedup არ არის claimed, არსად.

## ვალიდაცია

```text
python -m pytest -q tests/test_transformation_axes.py
55 passed
```

```text
python -m pytest -q
289 passed
```

ამ card-ის საკუთარი წვლილი არის `55` test `tests/test_transformation_axes.py`-ში (review-ის დროს `27` იყო; `+28` review-ის fix-ებიდან — depth convention-ები, domain-check-ის სამი ცნობილი ხვრელი, signed probe, worker-count property-ები და sub-corpus-ის ზუსტი verdict distribution). სრული suite-ის რიცხვი მოძრავია, რადგან სხვა workers ამავე tree-ში პარალელურად ამატებენ tests-ს: review-ის დროს `243` იყო (`27` ჩვენი), fix-ების პირველი გატარებისას `272` (`55` ჩვენი, `217` სხვისი), ბოლო გაშვებაზე `289` (`55` ჩვენი, `234` სხვისი). სტაბილური და რეპროდუცირებადი რიცხვი აქ არის `55`; სრული suite-ის რიცხვი დროის ანაბეჭდია.

`tests/test_cross_validation.py::test_sequential_path_produces_the_same_result_as_the_parallel_path` (სხვა card-ის ფაილი, ამ card-ის allowed_writes-ში არ არის) ერთხელ დაეცა contended გაშვებაზე და იმავე ბრძანებაზე ხელახლა გავიდა; ჩაწერილია როგორც სხვისი ფაილის ინტერმიტენტული ქცევა და ჩვენს მხრიდან შეუხებელია.

Report-ის რიცხვების რეპროდუქცია:

```text
python -c "from parseatlas.transformation_axes import axis_yield_report; r = axis_yield_report(workers=1); print(r['totals']['candidates'], r['totals']['equivalent'], r['totals']['domain_violating'], r['totals']['unsound'], round(r['operation_depth_correlation'],4), r['depth_reduced_without_operation_reduction'])"
231 227 4 0 0.8428 10
```

```text
python -c "from parseatlas.transformation_axes import axis_yield_report; r = axis_yield_report(); print(r['execution'], r['workers'], r['totals']['candidates'], r['totals']['equivalent'])"
parallel 12 231 227
```

Three-convention sensitivity table-ის რეპროდუქცია:

```text
python -c "
from parseatlas.transformation_axes import depth_convention_sensitivity as s
for name, row in s(workers=1).items():
    print(name, row['reduces_depth'], row['depth_reduced_without_operation_reduction'], round(row['operation_depth_correlation'],4))
"
balanced 14 10 0.8428
left_chain 9 5 0.881
flat 18 14 0.7427
```

Candidate cap-ის რეპროდუქცია (`200` წყვილიდან რომელი აღწევს `limit = 16`-ს):

```text
python -c "
from parseatlas.transformation_axes import axis_yield_report, DEFAULT_CANDIDATE_LIMIT
r = axis_yield_report(workers=1)
print([(x['formula'], x['axis'], x['candidates']) for x in r['per_formula_axis'] if x['candidates'] >= DEFAULT_CANDIDATE_LIMIT])
print(max(x['candidates'] for x in r['per_formula_axis'] if x['axis'] == 'mul_square_trade'))
"
[('g_shoelace_area', 'algebraic_rewrite', 16)]
6
```

Headline-ის კონცენტრაციის რეპროდუქცია:

```text
python -c "
import collections
from parseatlas.transformation_axes import axis_yield_report
r = axis_yield_report(workers=1)
invisible = [i for i in r['improvements'] if i['depth_delta'] < 0 <= i['operation_delta']]
print(len(invisible), collections.Counter(i['formula'] for i in invisible).most_common())
"
10 [('d_logistic_rhs', 6), ('p_binomial_variance', 2), ('p_binomial_pmf', 1), ('g_shoelace_area', 1)]
```
