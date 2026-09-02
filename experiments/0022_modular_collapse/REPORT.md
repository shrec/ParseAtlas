# ParseAtlas ექსპერიმენტი 0022: modular collapse

## მიზანი

ამ ფაზაში ვამოწმებთ, არის თუ არა `G0..G24` grammars-ის equivalence class structure მხოლოდ token sequence-ის თვისება. ერთი და იმავე constant-only token sequence-ისთვის ორი grammar-ი, რომლებიც `Q`-ზე **განსხვავებულ** value-ს იძლევა, `F_p`-ში შეიძლება **ერთსა და იმავე** value-ზე მოხვდეს. ვზომავთ, როგორ იცვლება equivalence class-ების რაოდენობა `Q`-დან `F_p`-ზე გადასვლისას რამდენიმე prime-ისთვის.

სტრუქტურული დებულება: equivalence class structure არის token sequence-ისა **და** declared analysis domain-ის ერთობლივი თვისება, და არა მხოლოდ token sequence-ის.

## Domain setup

- grammars: `25` (`G0` control plus strict `G01..G24`).
- rational evaluation: exact `fractions.Fraction`; division by zero იძლევა dedicated exception-ს `UndefinedOverRationals` და caller-ი მას `undefined` group-ში ინახავს, არასოდეს აგდებს ჩუმად.
- modular evaluation: `F_p`-ში `pow(d, -1, p)`; თუ denominator კონგრუენტულია `0`-თან `mod p`, value არის undefined `F_p`-ში (`UndefinedOverFiniteField`) — ეს რეალური domain restriction-ია და არა შესანთქმელი error.
- modulus: `reduce_modulo` და `evaluate_modular` explicit-ად ითხოვენ prime modulus-ს (`_require_prime`). composite modulus არის declared domain-ის დარღვევა და უარყოფილია labelled `ValueError`-ით; ის აღარ აღწევს `pow(d, -1, m)`-მდე და bare stdlib error-ს აღარ იძლევა.
- correctness bridge: ყოველი recorded modular value ტოლი უნდა იყოს rational value-ის `mod p` reduction-ისა, **მაშინ და მხოლოდ მაშინ, როცა ორივე მხარე defined-ია**. `bridge_holds` ნიშნავს ზუსტად ამას და არაფერ სხვას.
- domain restriction (ცალკე დათვლილი კატეგორია, არა failure): grammar, რომლის rational value defined-ია, `F_p`-ში კი undefined. ორი მიზეზი აღირიცხება ცალ-ცალკე — `value_denominator_not_invertible` (თვით value-ს denominator კვდება `mod p`) და `intermediate_divisor_not_invertible` (value-ს denominator invertible-ია, მაგრამ AST-ის შიგნით რომელიღაც divisor არის `0 mod p`). ორივე `domain_restrictions`-ში ჩაიწერება და `bridge_holds`-ს **არ** ეხება.

## Corpus

შემოწმდა constant-only token sequences:

```text
2*3 + 4 - 6/2
1 + 2*3 - 4/2
8/4 + 3*2 - 1
5 - 2*3 + 9/3
7 + 6/3 - 2*4
```

primes:

```text
5, 7, 11, 13, 97
```

## დაკვირვებული შედეგები

Class count `Q`-ზე და თითო prime-ზე (თითო უჯრა არის equivalence class count `25` grammar-ზე):

| source | Q | 5 | 7 | 11 | 13 | 97 |
| --- | --- | --- | --- | --- | --- | --- |
| `2*3 + 4 - 6/2` | 3 | 3 | 3 | 3 | 3 | 3 |
| `1 + 2*3 - 4/2` | 3 | 3 | 3 | 3 | 3 | 3 |
| `8/4 + 3*2 - 1` | 3 | 3 | 3 | 3 | 3 | 3 |
| `5 - 2*3 + 9/3` | 5 | 3 | 5 | 4 | 5 | 5 |
| `7 + 6/3 - 2*4` | 3 | 3 | 2 | 3 | 3 | 3 |

Collapse (`rational_class_count - modular_class_count`) prime-ების მიხედვით, ხუთივე source-ზე შეჯამებული:

```text
{5: 2, 7: 1, 11: 1, 13: 0, 97: 0}
```

ეს რიცხვი აგრეგატია და თავისთავად ორ სხვადასხვა მექანიზმს აერთიანებს, ამიტომ ისინი ცალკეც იზომება:

- `coincidence_collapse` — ორი **defined** rational value ხვდება ერთსა და იმავე **defined** `F_p` value-ზე. მხოლოდ ამ მექანიზმს აქვს pair witness (`collapsed_pairs`).
- `restriction_collapse` — class-ები ერთიანდება მხოლოდ იმიტომ, რომ მათი grammars domain-იდან გავიდა და ერთადერთ `undefined` label-ში მოხვდა. აქ collapsed pair არასოდეს არსებობს.

ორი კომპონენტი დამოუკიდებლად ითვლება (coincidence — defined მხრიდან, restriction — undefined მხრიდან), და მათი ჯამი უნდა უდრიდეს class count-ის სხვაობას; ეს identity ტესტშია დაფიქსირებული cross-check-ად.

დეკლარირებულ corpus-ზე ხელახლა გაზომვის შემდეგ:

```text
collapse_by_prime              {5: 2, 7: 1, 11: 1, 13: 0, 97: 0}
coincidence_collapse_by_prime  {5: 2, 7: 1, 11: 1, 13: 0, 97: 0}
restriction_collapse_by_prime  {5: 0, 7: 0, 11: 0, 13: 0, 97: 0}
```

- total collapse events: `4`, აქედან coincidence `4`, restriction `0`
- total collapsed pairs: `116`
- primes where any collapse occurred: `5, 7, 11`
- correctness bridge checks: `625`, bridge failures: `0`, domain restrictions: `0`

გამოქვეყნებული `4` და `116` უცვლელი რჩება მექანიზმების გაყოფის შემდეგ, რადგან ამ corpus-ის ყველა value-ს denominator არის `1` და არცერთი grammar არ ტოვებს `F_p`-ს: `total_restriction_collapse == 0` და `total_domain_restrictions == 0` ორივე გაზომილია, და არა ნავარაუდევი.

Collapse strictly positive-ია ზუსტად სამ `(source, prime)` წყვილზე:

```text
("5 - 2*3 + 9/3", 5)  -> collapse 2 (coincidence 2, restriction 0), collapsed pairs 52
("5 - 2*3 + 9/3", 11) -> collapse 1 (coincidence 1, restriction 0), collapsed pairs 32
("7 + 6/3 - 2*4", 7)  -> collapse 1 (coincidence 1, restriction 0), collapsed pairs 32
```

### კონკრეტული collapsed pair

`7 + 6/3 - 2*4`, prime `7`:

```text
G01 -> 28  (over Q)
G09 -> 7   (over Q)
28 != 7, but 28 mod 7 == 7 mod 7 == 0
```

`Q`-ზე ამ source-ს აქვს `3` class (`1`: 13 grammar, `28`: 8 grammar, `7`: 4 grammar); `F_7`-ში დარჩა `2` class (`1`: 13 grammar, `0`: 12 grammar).

მეორე კონკრეტული წყვილი, `5 - 2*3 + 9/3`, prime `5`:

```text
G03 -> -7  (over Q)
G05 -> 18  (over Q)
-7 != 18, but -7 mod 5 == 18 mod 5 == 3
```

ამ source-ის `Q` class distribution არის `18`: 8, `2`: 5, `-4`: 4, `-7`: 4, `12`: 4; `F_5`-ში იგივე grammars გადანაწილდა როგორც `3`: 12, `2`: 9, `1`: 4.

### Collapse არ არის monotone prime-ის ზრდით

Per-source measurement აჩვენებს, რომ collapse არ ეცემა monotone-ად prime-ის ზრდისას:

```text
7 + 6/3 - 2*4 : p=5 -> 0, p=7 -> 1
5 - 2*3 + 9/3 : p=5 -> 2, p=7 -> 0, p=11 -> 1
```

აგრეგირებულ დონეზე კი ამ corpus-ზე დაფიქსირდა `collapse(5) = 2 > collapse(97) = 0`.

### Coincidence და restriction ერთმანეთისგან გამოყოფილი

დეკლარირებულ corpus-ზე მთელი collapse coincidence-ია, ამიტომ ორი მექანიზმის განსხვავება ცალკე probe sources-ზე იზომება (`p = 5`):

```text
source            collapse  coincidence  restriction  collapsed_pairs  bridge_checks  domain_restrictions
6 / 5 + 6 / 5            1            0            1                0              0                   25
2 / 5 * 5 + 1            3            0            3                0              4                   21
10 / 5 + 1               0            0            0                0             12                   13
10 / 5 - 3 / 4          -1            0           -1                0             12                   13
```

- `6 / 5 + 6 / 5`: `Q`-ზე ორი განსხვავებული defined value (`12/5`: 13 grammar, `6/55`: 12 grammar), `F_5`-ში ორივე უქმდება და ერთ `undefined` class-ში ხვდება. class count ეცემა `2 -> 1`, მაგრამ **არცერთი** value არ დამთხვევია მეორეს; ეს erasure-ია და არა coincidence. ძველი აგრეგატი ამას `collapse 1`-ად აჩვენებდა `collapsed_pair_count 0`-თან ერთად, რაც შეუსაბამო წყვილია; ახლა `restriction_collapse = 1` და `coincidence_collapse = 0`.
- `10 / 5 - 3 / 4`: ოცდახუთივე grammar `Q`-ზე ერთსა და იმავე value-ს იძლევა (`5/4`), მაგრამ `F_5`-ში 13 მათგანი კვდება intermediate divisor `5`-ზე, 12 კი რჩება და იძლევა `0`. class count **იზრდება** `1 -> 2`, ანუ restriction შეიძლება class-ს გახლიჩოს კიდეც; ამიტომ `restriction_collapse` შეიძლება უარყოფითი იყოს და ეს არ არის error.
- `10 / 5 + 1`: rational value `3` (denominator `1`, invertible `mod 5`), `F_5`-ში კი undefined, რადგან intermediate divisor `5` არის `0`. ეს არის `intermediate_divisor_not_invertible` restriction — 13 ჩანაწერი, bridge failures `0`, `bridge_holds True`. მანამდე ეს `reduction_mismatch`-ად ითვლებოდა და `bridge_holds`-ს `False`-ზე აგდებდა, რაც headline correctness claim-ს დეკლარირებული corpus-ის გარეთ unsound-ს ხდიდა.

### Tokenizer-ის დაკვირვება

`parseatlas.tokenizer`-ის number pattern `\d+(?:/\d+)?` ამ corpus-ში `6/2`, `4/2`, `8/4`, `9/3`, `6/3` fragments-ს **ერთ rational literal token-ად** კითხულობს. ამის გამო `canonical.operation_cost` ხუთივე source-ზე და ოცდახუთივე grammar-ზე იძლევა `div == 0`: declared corpus-ში `/` operator საერთოდ არ ჩნდება, და grammar variation მხოლოდ `+`, `-`, `*` precedence-ზე მოქმედებს. შესაბამისად ამ corpus-ზე ყველა rational value integer-ია (denominator `1`), ყველა `625` bridge check invertible-denominator branch-ში ხვდება, და `F_p`-ში undefined value ამ corpus-ზე არასოდეს გვხვდება.

Division path-ის დასაფარად tests-ში ცალკე probe sources გამოიყენება, სადაც `/` spacing-ის გამო ნამდვილად operator-ია:

```text
6 / 0       : all 25 grammars undefined over Q and in F_5, F_7
6 / 3 - 3   : over Q 13 grammars -> -1, 12 grammars -> undefined
6 / 5 + 1   : over Q 12 grammars -> 1, 13 grammars -> 11/5;
              in F_5 those same 13 grammars are undefined (denominator 5 not invertible),
              in F_7 none are undefined (12 -> 1, 13 -> 5)
```

`6 / 3 - 3` აჩვენებს, რომ grammar-ის არჩევა თავად წყვეტს, `Q`-ზე value defined არის თუ undefined; `6 / 5 + 1` აჩვენებს, რომ `Q`-ზე სრულიად defined value შეიძლება `F_p`-ში გაუქმდეს მხოლოდ modulus-ის არჩევის გამო.

ეს degeneracy ახლა prose-ში კი არ არის მხოლოდ გამხელილი, არამედ ტესტით არის დაფიქსირებული: `test_correctness_bridge_holds_for_every_grammar_source_and_prime` პირდაპირ ამტკიცებს `exact.denominator == 1`-ს ხუთივე source-ისა და ოცდახუთივე grammar-ისთვის (და არა tautological `denominator % p != 0`-ს, რომელიც ამ corpus-ზე ვერასოდეს ჩავარდებოდა). ნამდვილ, არატრივიალურ modular inverse-ს ცალკე ტესტი ამოწმებს probe-ებზე:

```text
6 / 5 + 1, p = 7   : 13 grammars -> 11/5, denominator 5, pow(5, -1, 7) == 3 != 1,
                     reduce_modulo(11/5, 7) == 5; bridge_checks 25, domain restrictions 0
10 / 5 - 3 / 4, p=5: 25 grammars -> 5/4, denominator 4, pow(4, -1, 5) == 4 != 1;
                     bridge_checks 12 (დანარჩენი 13 არის domain restriction)
```

## ინტერპრეტაცია

```text
token sequence + grammar -> AST
AST + declared domain -> value
value set -> equivalence classes
```

Equivalence class count ამ corpus-ზე იცვლება domain-ის შეცვლისას, თვით token sequence-ის ერთი სიმბოლოს შეცვლის გარეშე. `5 - 2*3 + 9/3`-ს `Q`-ზე აქვს `5` class, `F_5`-ში `3`, `F_11`-ში `4`, ხოლო `F_7`, `F_13`, `F_97`-ში ისევ `5`. ესე იგი class structure არის `(token sequence, domain)` წყვილის ფუნქცია.

domain-ის შეცვლა class structure-ს ორი სხვადასხვა გზით ცვლის და ეს ორი გზა ერთმანეთში არ უნდა აირიოს:

1. **coincidence** — ორი defined value ხდება ტოლი `F_p`-ში. ეს ნამდვილი modular დამთხვევაა და მას აქვს pair witness.
2. **restriction** — value საერთოდ ტოვებს domain-ს და `undefined`-ში ხვდება. აქ არაფერი დამთხვევია: ინფორმაცია იშლება. ამას pair witness არ აქვს და შეიძლება class count გაზარდოს კიდეც.

დეკლარირებულ corpus-ზე მთელი გაზომილი collapse (`4`) coincidence-ია და restriction არის `0`; ეს გაზომვის შედეგია და არა corpus-ის თვისების დაშვება.

მცირე prime უფრო მეტ coincidence-ს იძლევა იმიტომ, რომ residue space უფრო პატარაა, მაგრამ ეს არ არის მარტივი monotone კანონი: `7 + 6/3 - 2*4` `F_5`-ში საერთოდ არ collapse-დება, `F_7`-ში კი collapse-დება, რადგან coincidence დამოკიდებულია არა prime-ის ზომაზე, არამედ იმაზე, ყოფს თუ არა prime კონკრეტული value pair-ის სხვაობას (`28 - 7 = 21`, რომელსაც `7` ყოფს და `5` არა). restriction კი სულ სხვა პირობით იმართება — ყოფს თუ არა prime რომელიმე divisor-ს — ამიტომ ერთი აგრეგირებული `collapse` რიცხვი ორივეზე ერთდროულად ვერ იმსჯელებს.

## Research discipline

ეს ექსპერიმენტი არის **semantic variation mode**, და არა equivalence-preserving optimization mode. ორ განსხვავებულ rational value-ს შორის modular coincidence **არ არის** licence იმისა, რომ ერთი representation მეორეთი ჩავანაცვლოთ cryptographic code-ში.

README-ის წესი უცვლელად რჩება:

```text
In cryptographic code, semantic reinterpretation that changes the result is not an optimization.
```

`28` და `7` სხვადასხვა mathematical object-ია `Q`-ზე; ის, რომ ორივე `0`-ია `F_7`-ში, მხოლოდ იმ declared domain-ის ფაქტია და არა `F1(x) == F2(x) mod p` სახის proof obligation-ის შესრულება ყველა შემთხვევისთვის. ROADMAP Phase 12-ის მოთხოვნა — modulus metadata explicit-ად, transformation მხოლოდ equivalence-preserving — ამ report-ის არცერთი observation-ით არ არის დაკმაყოფილებული და არც არის ასე გამოცხადებული.

## შეზღუდვები

- corpus მხოლოდ ხუთი constant-only source-ისგან შედგება; variables საერთოდ არ არის.
- declared corpus-ში `/` operator არ ჩნდება tokenizer-ის rational literal pattern-ის გამო, ამიტომ `F_p`-ის undefined branch corpus-ზე არ იზომება — მხოლოდ tests-ის probe sources-ზე.
- primes მხოლოდ ხუთია და ყველა მცირეა; `secp256k1`-ის რიგის modulus არ შემოწმებულა.
- collapse ამჟამად class count-ის სხვაობას ზომავს; collapsed pair-ების structural cause (რომელი precedence swap იწვევს მას) ჯერ არ არის graph-ად აწყობილი.
- `restriction_collapse` class count-ის დონეზე ითვლება და არა grammar-ების დონეზე: ის ამბობს რამდენი class გაქრა/გაჩნდა `undefined` label-ის გამო, და არა რომელი grammar-ები დაზარალდნენ; ამისთვის `domain_restrictions` ჩანაწერებია.
- `restriction_collapse` შეიძლება უარყოფითი იყოს (class-ის გახლეჩა); `coincidence_collapse` არასოდეს არის უარყოფითი და ეს ტესტშია დაფიქსირებული.
- `G0` control grammar აგრეგატებში ჩართულია და ცალკე არ არის გამოყოფილი.
- report არ ამტკიცებს არცერთ ზოგად კანონს prime size-სა და collapse rate-ს შორის.

## Evidence-ის კლასიფიკაცია

- class count table, collapse counts, `116` collapsed pair, `625` bridge check და კონკრეტული pair-ები executable **observations** არის.
- correctness bridge (`modular value == rational value mod p`, როცა **ორივე მხარე** defined-ია) კოდში ყოველ ჯერზე მოწმდება; მისი `625/625` შესრულება ამ corpus-ზე **observation**-ია, ხოლო `rational undefined -> modular undefined` არის **symbolically justified** და ასევე კოდში მოწმდება.
- `bridge_holds`-ის scope არის definitional: domain restriction (rational defined, modular undefined) ცალკე კატეგორიაა და bridge-ს არ ეხება. ეს არის მოცემულობა და არა გაზომვა; გაზომვა არის ამ კატეგორიის count თითო source-სა და prime-ზე.
- coincidence/restriction-ის გაყოფა **definitional** decomposition-ია; ის, რომ ორი დამოუკიდებლად ნათვლელი კომპონენტის ჯამი უდრის class count-ის სხვაობას, ტესტში **გაზომილია** corpus-სა და რვა probe source-ზე, primes `2, 3, 5, 7, 11, 13, 97`.
- non-monotone collapse ამ corpus-ზე **observation**-ია; ის, რომ coincidence იმართება პირობით `prime divides (v1 - v2)` და არა prime-ის ზომით, არის **symbolically justified**.
- ის, რომ უფრო დიდი prime ზოგადად ნაკლებ collapse-ს იძლევა თვითნებურ corpus-ზე, ჯერჯერობით **hypothesis**-ია და ამ ხუთი prime-ით არ არის დამტკიცებული.

## ვალიდაცია

```text
python -c "from parseatlas.finite_field import modular_class_report, DEFAULT_PRIMES; r = modular_class_report(); print(r['collapse_by_prime'], r['total_collapse_events'], r['total_coincidence_collapse'], r['total_restriction_collapse'], r['total_collapsed_pairs'], r['collapsing_primes'], r['bridge_checks'], r['total_domain_restrictions'], r['bridge_holds']); [print(s['source'], s['rational_class_count'], [s['primes'][p]['modular_class_count'] for p in DEFAULT_PRIMES]) for s in r['sources']]"
```

```text
{5: 2, 7: 1, 11: 1, 13: 0, 97: 0} 4 4 0 116 [5, 7, 11] 625 0 True
2*3 + 4 - 6/2 3 [3, 3, 3, 3, 3]
1 + 2*3 - 4/2 3 [3, 3, 3, 3, 3]
8/4 + 3*2 - 1 3 [3, 3, 3, 3, 3]
5 - 2*3 + 9/3 5 [3, 5, 4, 5, 5]
7 + 6/3 - 2*4 3 [3, 2, 3, 3, 3]
```

მექანიზმების გაყოფა probe sources-ზე (`p = 5`):

```text
python -c "from parseatlas.finite_field import modular_class_report as m; [print(repr(s), m((s,), (5,))['sources'][0]['primes'][5]['collapse'], m((s,), (5,))['sources'][0]['primes'][5]['coincidence_collapse'], m((s,), (5,))['sources'][0]['primes'][5]['restriction_collapse'], m((s,), (5,))['bridge_holds'], m((s,), (5,))['bridge_checks'], m((s,), (5,))['total_domain_restrictions']) for s in ('10 / 5 + 1', '6 / 5 + 6 / 5', '2 / 5 * 5 + 1', '10 / 5 - 3 / 4')]"
```

```text
'10 / 5 + 1' 0 0 0 True 12 13
'6 / 5 + 6 / 5' 1 0 1 True 0 25
'2 / 5 * 5 + 1' 3 0 3 True 4 21
'10 / 5 - 3 / 4' -1 0 -1 True 12 13
```

```text
python -m pytest -q tests/test_finite_field.py
16 passed
```

სრული suite ამ report-ის დროს:

```text
python -m pytest -q
167 passed
```

(სრული suite ამ ტალღაში პარალელურად იზრდება სხვა workers-ის files-ის დამატების ხარჯზე — ამ rework-ის მსვლელობაში იგივე ბრძანებამ ზედიზედ მისცა `136`, `140` და `167`; `167` არის ბოლო run. `16 passed` არის ამ რეპორტის საკუთარი test file-ის count და მხოლოდ ის არის ამ card-ის კონტროლში.)

### Timing (ხელახლა გაზომილი)

წინა redaction-ში გამოქვეყნებული `0.0193 s` ერთი run-ის შედეგი იყო და არ მეორდებოდა. ხელახალი გაზომვა: ერთი warm-up call, შემდეგ `20` გამეორება `time.perf_counter()`-ით, სამ ცალკე process-ში:

```text
run 1: min 0.0071 s  median 0.0075 s  max 0.0082 s
run 2: min 0.0071 s  median 0.0074 s  max 0.0125 s
run 3: min 0.0074 s  median 0.0079 s  max 0.0139 s
run 4: min 0.0067 s  median 0.0073 s  max 0.0086 s
run 5: min 0.0070 s  median 0.0078 s  max 0.0142 s
```

გამოსაქვეყნებელი ფიგურა: `modular_class_report()` სრული run აღწერილ corpus-სა და primes-ზე არის `~0.0075 s` median (`5` ცალკე process, თითო `20` გამეორება; median-of-medians `0.0075 s`, overall min `0.0067 s`, overall max `0.0142 s`).

ეს ციფრი manager-ის მიერაა ხელახლა გაზომილი review-ის დროს. წინა ორი გამოქვეყნებული მნიშვნელობა — `0.0193 s` (ერთი run) და `~0.012 s` median (`0.009-0.021 s`) — **არ მეორდებოდა**: ორივე დატვირთული მანქანის შედეგი იყო. მშვიდ host-ზე median მდგრადად `0.0073-0.0079 s` დიაპაზონშია. max მნიშვნელობა (`0.014 s`) დატვირთვაზეა მგრძნობიარე, median კი არა — ამიტომ ქვეყნდება median და არა ერთჯერადი ან mean მნიშვნელობა.

Path sequential-ად რჩება: `10 ms`-ის რიგის workload-ზე process pool-ის გაშვება უფრო ძვირია, ვიდრე თავად გაზომვა, და parallel execution შედეგს ისედაც არ ცვლის — მხოლოდ იმას, რამდენად სწრაფად მიიღება.
