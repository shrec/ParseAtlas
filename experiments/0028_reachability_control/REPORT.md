# ParseAtlas ექსპერიმენტი 0028: reachability negative control

## მიზანი

ექსპერიმენტმა 0027-მა ერთი კონკრეტული წყვილისთვის ხელით დაადგინა, რომ target program rewrite search-ისთვის მიუწვდომელი იყო არა იმიტომ, რომ search budget მცირე იყო, არამედ იმიტომ, რომ search language კრძალავდა მას. აკრძალვა სამმა structural commitment-მა შექმნა:

1. **input preservation** — candidate reference-ის input list-ით literally იგება და არც ერთ rule-ს არ შემოაქვს free variable;
2. **output-key preservation** — candidate უარყოფილია, თუ მისი output key set reference-ის output key set-ს ზუსტად არ უდრის;
3. **map equality** — equivalence არის computed map-ის raw value equality, რაც equivalence-up-to-representation-ზე მკაცრად ძლიერია.

ეს ანალიზი ერთი წყვილისთვის ხელით გაკეთდა. ამ card-ის მიზანია იგივე მსჯელობა გახდეს **reusable და tested capability**, რადგან ROADMAP thesis T20.1 მას standing step-ად მოითხოვს: ჯერ დაამტკიცე, რას **ვერ** მიაღწევს axis set, და მხოლოდ შემდეგ დახარჯე ძალისხმევა ამ axis set-ით ძებნაზე.

მოდული არის `src/parseatlas/reachability_control.py`. `case_studies/` snapshot არსად არ არის imported; program representation საკუთარია.

## Module structure

Straight-line program არის `Assignment` ობიექტების ordered sequence named input-ებზე, რომელიც named output-ებს აწარმოებს:

```text
Program(name, inputs, body, outputs)
Assignment(target, expression)
```

`Program.__post_init__` ამოწმებს იმ property-ს, რომელსაც 0027 vendored rewriter-ზე ამტკიცებს: ყოველი ნახსენები სახელი ან declared input-ია, ან ადრე assigned target. Free variable-ის შემოტანა representation-ის დონეზეა აკრძალული, ამიტომ არც ერთ program-level rewrite-ს არ შეუძლია მისი შემოტანა. `sqrt(x)`-ის ტიპის non-rational expression ასევე უარყოფილია, რადგან equality cancellation-ით უნდა წყდებოდეს.

ორი signature ერთმანეთისგან განზრახ ასიმეტრიულია:

- `input_signature(program)` აბრუნებს **ordered tuple**-ს, რადგან position მნიშვნელობის მატარებელია — 0027-ის `Z1` და `Z` cosmetic rename არ იყო;
- `output_signature(program)` აბრუნებს **frozenset**-ს, რადგან vendored engine-ის gate ლიტერალურად `set(candidate.outputs) != output_names` არის.

შედარების ფენა:

| function | რას ზომავს |
|---|---|
| `map_equal` | raw value equality shared output key-ებზე, sample set-ზე **და** symbolic cancellation-ით |
| `projective_equal` | სუსტი relation: ერთი nonzero scale `L` თითო წერტილზე, declared weight-ებით |
| `slice_of_agreement` | constraint, რომლის ქვეშაც unequal map-ები **მაინც** ემთხვევა |
| `reachability_verdict` | structured verdict declared commitment set-ის მიმართ |
| `relaxation_analysis` | per-commitment counterfactual: რომელი ერთი შეზღუდვა დგას გზაზე |
| `evaluate_corpus_pair` | ერთი წყვილის სრული პასუხი plain data-დ, იმ წყვილისთვის, რომელსაც caller აწვდის |
| `reachability_sweep` | corpus — ჩაშენებული ან caller-ისა — და მისი შედარება ცნობილ პასუხებთან |

ორი გადაწყვეტილება `map_equal`-ში არის ის, რაც "blocked by exactly one commitment"-ს აზრიან განცხადებად აქცევს. პირველი: შედარება მხოლოდ **shared** output key-ებზე მიდის — თუ candidate ზედმეტ key-ს აქვეყნებს, ეს `preserve_outputs`-ის საქმეა, და მისი აქ ჩაკეცვა ყოველ output extension-ს map failure-დაც აჩვენებდა. მეორე: შედარება **positional** არის — program-ები, რომელთა input list მხოლოდ სახელით განსხვავდება, მაინც ერთი და იმავე ordered tuple-ის ორი ფუნქციაა, ზუსტად ისე, როგორც 0027-მა ორივე program identical tuple-ებზე გამოთვალა; სახელის განსხვავებას `preserve_inputs` წყვეტს და არა equivalence test.

`slice_of_agreement` მოდულის ყველაზე სასარგებლო output-ია. მეთოდი: აიღე თითო shared output key-ზე ორი map-ის სხვაობა, გაასუფთავე denominator, factor-ად დაშალე numerator და დაიტოვე ის irreducible factor-ები, რომლებიც **ყველა** nonzero სხვაობაშია. თითოეული ასეთი factor წყდება ერთი symbol-ის მიმართ და მიღებული substitution უკან ბრუნდება ყველა სხვაობაში; მხოლოდ ის constraint-ები ქვეყნდება, რომლებზეც ყველა სხვაობა ზუსტად ნულდება. ეს "unreachable"-ს "unreachable, და აი ის substitution, რომელიც ხიდს გადებდა"-დ აქცევს. როცა ასეთი constraint ერთზე მეტია, რომელი გახდება `primary`, ცალკე გამოცხადებული წესით წყდება — იხ. ქვემოთ.

`Evidence` ერთხელ იზომება და ყველა counterfactual-ს ერთი და იგივე გაზომვა ეძლევა, ამიტომ ორ verdict-ს შორის განსხვავება მხოლოდ commitment set-იდან შეიძლება მოდიოდეს და არასდროს ხელახალი გაზომვიდან.

Sample set deterministic-ია ორმაგად: ჯერ fixed corner block (all-ones წერტილი და წერტილები, სადაც ერთი coordinate `1`-ზე ან `0`-ზეა მიმაგრებული, ასე რომ single-input slice ყოველთვის მონახულებულია), შემდეგ `VALUE_POOL`-იდან წერტილები fixed linear congruential sequence-ით. Global RNG არსად ირევა. წერტილები distinct-ია, ამიტომ set არ შეიძლება იყოს `len(VALUE_POOL) ** arity`-ზე დიდი: arity 2-ზე ეს ჭერი `121`-ია და sample set მთელ grid-ს ავსებს, arity 3-ზე კი მოთხოვნილი `240` მიიღწევა.

## Corpus

შვიდი reference/target წყვილი, სადაც პასუხი დამოუკიდებლად, algebra-დან არის ცნობილი მოდულის გაშვებამდე. `expected_violations` corpus-შია ჩაწერილი და test file-შიც ლიტერალურად მეორდება, ასე რომ corpus entry ვერ გადაასწორებს იმას, თუ რა ჩაითვლება სწორად.

| id | reference -> target | რატომ ეს პასუხი |
|---|---|---|
| `rewriteable_polynomial` | `square_of_sum` -> `expanded_square` | ერთი polynomial-ის factored და expanded ფორმა: ერთი და იგივე input, output key და map |
| `output_extension` | `square_of_sum` -> `square_of_sum_with_cross` | target აქვეყნებს ერთ დამატებით მნიშვნელობას, რომელსაც უკვე ითვლის; shared key-ზე map ხელუხლებელია |
| `input_recoding` | `square_of_sum` -> `square_of_sum_recoded` | target სხვაგვარად encoded input-ს აცხადებს; იმავე ordered tuple-ის ფუნქციად იგივე map-ია |
| `erased_prefix` | `graded_form` -> `erased_prefix_form` | 0027-ის structural analogue ჩვეულებრივ algebra-ში: lifting prefix-ის წაშლა სხვა ფუნქციას ტოვებს იმავე სამ რიცხვზე |
| `scaled_representative` | `ratio_reduced` -> `ratio_scaled` | ნამდვილად ერთი და იგივე ობიექტი scaling convention-ის სიზუსტით, მაგრამ არა როგორც raw map |
| `specialised_input` | `product_of_inputs` -> `second_input_frozen` | ერთ-output-იანი წყვილი, რომლის სხვაობა ორ საერთო factor-ად იშლება: აიძულებს primary slice-ის არჩევანს |
| `coz_analogue` | `graded_form` -> `coz_analogue` | regression guard: სამივე commitment ერთდროულად დარღვეულია |

`erased_prefix` წყვილი 0027-ის კონსტრუქციას პირდაპირ იმეორებს, cryptographic material-ის გარეშე. Reference `graded_form` input-ებს `z`-ის მიერ მოტანილ grading-ზე ასწევს:

```text
zz = z*z ; zzz = zz*z ; u = x*zz ; s = y*zzz ; p = u + s ; q = u - s   ->  {P: p, Q: q}
```

Target `erased_prefix_form` ზუსტად ამ lifting prefix-ს შლის (`u := x`, `s := y`) და დანარჩენს უცვლელად ტოვებს. სხვაობები factor-ად ასე იშლება:

```text
P_ref - P_cand = (z - 1) * (x*z + x + y*z**2 + y*z + y)
Q_ref - Q_cand = (z - 1) * (x*z + x - y*z**2 - y*z - y)
```

საერთო irreducible factor მხოლოდ `z - 1` არის, და მისი შესაბამისი slice `z = 1` ზუსტად ის სტრუქტურაა, რაც 0027-ში `Z = 1`-ზე დაფიქსირდა.

## Primary constraint-ის არჩევა

ერთი წყვილისთვის შეიძლება **ერთზე მეტი** ჭეშმარიტი slice არსებობდეს: სხვაობა რამდენიმე საერთო factor-ად იშლება და თითოეული მათგანი დამოუკიდებლად მოწმდება symbolically. მაშინ ჩნდება კითხვა, რომელი აჩვენოს `.primary`-მ იმ caller-ს, რომელიც სიის მხოლოდ პირველ ელემენტს კითხულობს.

Card-ის მიღებული ვერსია ამას **ლექსიკოგრაფიულად** წყვეტდა და ეს არასწორ პასუხს აძლევდა. მინიმალური მაგალითი — `specialised_input`:

```text
reference  product_of_inputs   F = a*c
target     second_input_frozen F = 2*a
სხვაობა    a*c - 2*a = a * (c - 2)
```

ორივე `a = 0` და `c = 2` ჭეშმარიტი slice-ია და ორივე symbolically ვერიფიცირებულია; sample set-ზეც ორივე `11/11`-ს იძლევა. მაგრამ ისინი თანაბრად სასარგებლო არ არის:

| slice | reference slice-ზე | რას ამბობს |
|---|---|---|
| `c = 2` | `F = 2*a` — non-constant | ასახელებს დაკარგულ transformation-ს: მეორე input გაყინე `2`-ზე |
| `a = 0` | `F = 0` — constant | ორივე program კოლაფსირდება; ისინი ემთხვევა იმიტომ, რომ არც ერთი არაფერს ამბობს |

ლექსიკოგრაფიული წესი `a = 0`-ს ირჩევდა, ანუ სწორედ იმას, რომელიც არაფერს ეუბნება caller-ს. Card-ის მიღებულ corpus-ში slice-იან წყვილებს ორ-ორი output ჰქონდათ, რაც საერთო factor-ს ერთადერთს ხდის, ამიტომ ეს შემთხვევა corpus-ს არასდროს გამოუვლენია — სწორედ ამიტომ დაემატა `specialised_input`.

**გამოცხადებული წესი.** `constraints` ახლა დალაგებულია `_informativeness_key`-თი და `primary` ამ რიგის თავია:

1. `-len(non_constant_keys)` — ჯერ ის slice, რომელზეც შეთანხმებული map რაც შეიძლება მეტ shared output key-ზე **მაინც იცვლება**. Slice, რომელიც ყველა output-ს კონსტანტად აქცევს, კოლაფსის შეთანხმებას აღწერს.
2. `factor_degree` ზრდადობით — თანაბრად არა-დეგენერატულებს შორის ალგებრულად უფრო მარტივი, რადგან წრფივი constraint პირდაპირ შესასრულებელი substitution-ია.
3. `equation` ზრდადობით — ტოლობის შემთხვევაში deterministic, ასე რომ განმეორებითი გაშვება და ცალკე process ერთსა და იმავე primary-ს აბრუნებს.

პირველი კრიტერიუმი მხოლოდ reference-ს ზომავს და ეს საკმარისია: constraint მაშინ ქვეყნდება, როცა ყველა სხვაობა მასზე ზუსტად ნულდება, ანუ ორივე შეზღუდული map ერთი და იგივე rational function-ია slice-ზე.

სამივე გასაღები ცალ-ცალკეა ჩამაგრებული. მეორეს ტესტს პირველი გასაღები გათანაბრებული აქვს: სხვაობა `(b - a**2)*(c - 1)`-ია, დამატებული map-ზე, რომელიც ორივე slice-ს გადაურჩება, ამიტომ ორივე constraint `F`-ს ცვალებადს ტოვებს და არჩევანს degree წყვეტს (`c - 1` წრფივია, `a**2 - b` — არა). ლექსიკოგრაფიული წესი აქაც სხვას აირჩევდა: `a**2 - b = 0` ანბანურად წინ დგას.

**რატომ არა "უფრო პატარა slice".** განხილული იყო alternative წესი — აირჩიე constraint, რომელიც უფრო პატარა slice-ს ჭრის. იგი ამ შემთხვევას **ვერ არჩევს**: `a = 0` და `c = 2` ორივე ჰიპერსიბრტყეა და sample set-ზე ორივე ზუსტად `11` წერტილს იძლევა. გარდა ამისა, ის slice-ის ზომას sample set-იდან წაიკითხავდა და არა algebra-დან, ანუ პასუხს declared sample count-ზე დამოკიდებულს გახდიდა. Degeneracy-ს კრიტერიუმი კი წმინდად სიმბოლურია.

`max_constraints` ახლა **rank-ის შემდეგ** ჭრის სიას და არა მანამდე, თორემ cap-ს შეეძლო სწორედ informative constraint გადაეგდო: `F = a*b*c` vs `F = 2*a*b`-ს სამი საერთო factor აქვს (`a`, `b`, `c - 2`), ორი მათგანი დეგენერატულია და ორივე `c - 2`-ზე ადრე დგას ანბანურად.

`common_factors` კვლავ კანონიკური სტრიქონული რიგითაა — ის ნედლი factor-ების სიაა, იმათი ჩათვლით, რომლებიც constraint-ად ვერ იქცა (მაგალითად `x**2 - 2`, რომელსაც რაციონალური ფესვი არ აქვს). დალაგებულია მხოლოდ `constraints`.

## Caller-ის საკუთარი corpus

`reachability_sweep(pairs=None, workers=None)` ხელმოწერას თავიდანვე ჰქონდა `pairs`, მაგრამ pool task წყვილს **id-ით** ეძებდა `PAIRS_BY_ID`-ში, ამიტომ caller-ის საკუთარი წყვილი `KeyError`-ით ვარდებოდა. ეს იმას ნიშნავდა, რომ მოდულს ვერ გამოიყენებდა ის, ვისთვისაც ის დაიწერა — მისი გამოყენება მოდულის რედაქტირებას მოითხოვდა.

ახლა task-ს თავად წყვილი გადაეცემა:

```python
from parseatlas.reachability_control import CorpusPair, Program, Assignment
from parseatlas.reachability_control import DEFAULT_COMMITMENTS, reachability_sweep

pair = CorpusPair(
    id="my_pair",
    reference=Program(...),
    target=Program(...),
    commitments=DEFAULT_COMMITMENTS,
    expected_violations=("preserve_outputs",),   # რასაც caller algebra-დან ელოდება
    expected_slice=None,
    note="...",
)
report = reachability_sweep([pair], workers=1)
```

- `pairs`-ის default კვლავ `CORPUS`-ია, ამიტომ ჩაშენებული sweep უცვლელად არის უარგუმენტო გამოძახება;
- id-ს არც უნიკალურობა სჭირდება და არც `PAIRS_BY_ID`-ში ყოფნა;
- `expected_violations` და `expected_slice` არის ის, რასაც `mismatched` და `all_match_known_answers` ედრება, ანუ caller წერს თავის ვარაუდს და კითხულობს, ეთანხმება თუ არა მოდული;
- `evaluate_corpus_pair(pair)` არის ახალი public entry point; `evaluate_pair(identifier)` მას id-ით მიმართავს და ჩაშენებული corpus-ისთვის უცვლელია.

Parallel გზა caller-ის წყვილისთვისაც მუშაობს: `CorpusPair` pickle-დება (`coz_analogue` `1608` bytes, ტესტში აგებული `CALLER_PAIR` `987` bytes), ამიტომ Windows `spawn` child-ს არაფრის მოძებნა არ სჭირდება. ტესტი ამტკიცებს, რომ caller-ის corpus-ზე sequential და parallel report-ები იდენტურია.

## Multicore

Sweep per-pair independent და CPU-bound არის, ამიტომ process pool-ის გზა არსებობს: module-level `_pool_task`, `ProcessPoolExecutor` და `workers=1`, რომელიც sequential გზას აიძულებს. არჩევანი გაზომვით არის მიღებული და არა ჩვევით.

ბრძანება: შემდეგი script ინახება ფაილად (მაგალითად `bench0028.py`) და შემდეგ სრულდება
`python bench0028.py`-ით. ფაილად შენახვა აუცილებელია: Windows `spawn` start method-ის ქვეშ
თითო child ხელახლა imports caller-ის `__main__`-ს, ამიტომ `python - <<'EOF'` სახის stdin
გაშვება parallel გზაზე `BrokenProcessPool`-ით ვარდება.

```python
import time
from parseatlas.reachability_control import CORPUS, reachability_sweep


def best(pairs, workers, runs=3):
    timings = []
    for _ in range(runs):
        start = time.perf_counter()
        reachability_sweep(pairs, workers=workers)
        timings.append(time.perf_counter() - start)
    return min(timings)


if __name__ == "__main__":
    for n in (7, 28, 36, 48, 96, 384):
        pairs = (tuple(CORPUS) * 64)[:n]
        s = best(pairs, 1)
        p = best(pairs, 6)
        print(f"{n:4d} pairs  sequential {s:7.3f}s  pool6 {p:7.3f}s  speedup {s / p:5.2f}x")
```

Pair count ახლა პირდაპირ ირჩევა (`[:n]`) და არა corpus-ის ჯერადებით, რადგან corpus შვიდწყვილიანი გახდა და threshold-ის შემოწმებას ზუსტად `36` და `48` სჭირდება.

Best of six per cell, warm parent process, 16 core:

| pairs | sequential | pool of 6 | speedup |
|---|---|---|---|
| 7 | `0.171 s` | `0.793 s` | `0.22x` |
| 28 | `0.772 s` | `0.875 s` | `0.88x` |
| 36 | `0.966 s` | `0.850 s` | `1.14x` |
| 48 | `1.190 s` | `1.007 s` | `1.18x` |
| 96 | `2.424 s` | `1.401 s` | `1.73x` |
| 384 | `10.408 s` | `2.991 s` | `3.48x` |

ერთი წყვილი დაახლოებით `27 ms` sympy cancellation-ია, ხოლო Windows `spawn` child `0.41 s`-ს იხდის ამ მოდულის import-ზე, სანამ რაიმეს დაიწყებს (`python -X importtime -c "import parseatlas.reachability_control"`, best of five). ორივე სვეტის least-squares fit-ით ზემოთ მოცემულ ექვს რიგზე:

```text
sequential   -0.0585 s + 27.18 ms · n
pool         +0.7266 s +  5.94 ms · n
break-even    n = 37.0
```

Break-even `37` წყვილთანაა. (ადრე აქ დამრგვალებული კოეფიციენტები ეწერა — `27 ms · n` და `0.75 s + 5.8 ms · n` — რომლებიდანაც გადაკვეთა `35.4`-ს იძლევა და არა `37`-ს. `37` სწორია; დამრგვალება ხდიდა მას არა-reproducible-ს. ახლა ქვეყნდება fit-ის ის კოეფიციენტები, რომლებიდანაც რიცხვი რეალურად გამოდის.)

**რა შეიცვალა და რა არა.** Card-ის მიღების შემდეგ corpus ერთი წყვილით გაიზარდა, ამიტომ benchmark ხელახლა გაიზომა. Break-even იმავე ადგილას დარჩა (`36`-`37` წყვილი, ადრეც `36`), ერთი წყვილის ღირებულებაც (`26 ms` -> `27 ms`) და spawn-ის import-ღირებულებაც (`0.42 s` -> `0.41 s`). რაც შეიცვალა, არის margin `48`-თან: ადრე გაზომილი `1.44x` ამჯერად `1.18x`-ია. ეს რიცხვი ხელახლა ქვეყნდება როგორც არის; მისი მიმართულება იგივეა (`28`-ზე ქვემოთ break-even, `36`-იდან ზემოთ, `96`-იდან მკაფიო), ამიტომ `PARALLEL_THRESHOLD_PAIRS = 48` უცვლელი რჩება — ის break-even-ზე მაღლა დგას განზრახ, და უფრო მჭიდრო margin ამ კონსერვატიულ არჩევანს ასუსტებს კი არა, ამყარებს.

ამ card-ის შვიდწყვილიანი corpus ამიტომ **sequential-ად მუშაობს** — ეს გაზომილი გადაწყვეტილებაა. Worker count `os.cpu_count()`-იდან გამოიყვანება (`WORKER_HEADROOM_CORES = 2`, `WORKER_CAP = 12`) და არასდროს hardcoded constant-იდან. Test suite ამტკიცებს, რომ sequential და parallel report-ები იდენტურია: parallelism მხოლოდ სიჩქარეს ცვლის და არასდროს იმას, რაც იზომება.

## დაკვირვებული შედეგები

`python -c "from parseatlas.reachability_control import reachability_sweep; reachability_sweep(workers=1)"`:

| pair | violated commitments | map agreement | agreement fraction | slice |
|---|---|---|---|---|
| `rewriteable_polynomial` | — | `121/121` | `1` | — |
| `output_extension` | `preserve_outputs` | `121/121` | `1` | — |
| `input_recoding` | `preserve_inputs` | `121/121` | `1` | — |
| `erased_prefix` | `map_equality` | `25/240` | `5/48` | `z = 1` |
| `scaled_representative` | `map_equality` | `11/121` | `1/11` | `x = 0` |
| `specialised_input` | `map_equality` | `21/121` | `21/121` | `c = 2` |
| `coz_analogue` | `preserve_inputs`, `preserve_outputs`, `map_equality` | `25/240` | `5/48` | `z = 1` |

- reachable წყვილი: `1` (`rewriteable_polynomial`), და ის reachable-ია სამივე commitment-ის ქვეშ, `RELAXED_COMMITMENTS`-ის ქვეშ და მთელი vocabulary-ის ქვეშაც.
- blocked წყვილი: `6`.
- `all_match_known_answers`: `True` — შვიდივე verdict დამოუკიდებლად ცნობილ პასუხს ემთხვევა, slice-ის ჩათვლით.

Slice-ის ემპირიული cross-check: `erased_prefix`-ისთვის sample set `z = 1`-ზე პროექციის შემდეგ `107` განსხვავებულ წერტილს იძლევა და agreement `107/107`-ია; `scaled_representative`-ისთვის `x = 0`-ზე `11/11`; `specialised_input`-ისთვის `c = 2`-ზე `11/11`.

Relaxation analysis:

| pair | drop `preserve_inputs` | drop `preserve_outputs` | drop `map_equality` | weaken to `projective_equality` | sole blocker |
|---|---|---|---|---|---|
| `output_extension` | blocked | **reachable** | blocked | blocked | `preserve_outputs` |
| `input_recoding` | **reachable** | blocked | blocked | blocked | `preserve_inputs` |
| `erased_prefix` | blocked | blocked | **reachable** | blocked | `map_equality` |
| `scaled_representative` | blocked | blocked | **reachable** | **reachable** | `map_equality` |
| `specialised_input` | blocked | blocked | **reachable** | blocked | `map_equality` |
| `coz_analogue` | blocked | blocked | blocked | blocked | — |

`scaled_representative` და `erased_prefix` ორივე მხოლოდ `map_equality`-თია blocked, მაგრამ ისინი განსხვავდებიან იმაში, რას აკეთებს weakening: პირველი `projective_equality`-ზე გადასვლისას reachable ხდება scale-ით `L = x**2 + 1` (რომელიც rational-ებზე არასდროს ნულდება), მეორე კი არა — ის ნამდვილად სხვა ფუნქციაა და არა სხვა representative.

`coz_analogue`-ს არც ერთი ცალკეული relaxation არ ხსნის: სამივე drop blocked-ად რჩება, თითოეულს ორი დარჩენილი violation აქვს, და `map_equality`-ის `projective_equality`-ზე დასუსტებაც blocked-ს იძლევა.

## ინტერპრეტაცია

ზოგადი დებულება პირდაპირ უნდა ითქვას. **Representation search სწორედ იმიტომაა complete, რომ ის აფიქსირებს language-ს** — input-ებს, output-ებს და equivalence relation-ს. ეს სამივე commitment ერთდროულად არის ის, რაც search-ს სანდოს ხდის საკუთარ სივრცეში, და ის, რაც representation change-ს მიუწვდომელს ხდის. ეს ერთი და იგივე property-ია, და არა ორი.

აქედან პრაქტიკული დასკვნა: **axis set-ის გაფართოება ამას არ ასწორებს**. `coz_analogue` სტრიქონი ამას ზუსტად აჩვენებს — არც ერთი ცალკეული relaxation არ ცვლის verdict-ს, ამიტომ არც უფრო ღრმა search, არც უფრო ფართო beam და არც მეტი rewrite rule არაფერს შეცვლის. რაც იცვლება, არის ის, თუ **რას ატარებს search უცვლელად**.

```text
declared commitments -> reachable set -> ის, რასაც search საერთოდ ვერ ნახავს
```

ამიტომ negative control **search-ამდე** უნდა გაეშვას და არა იმედგაცრუებული შედეგის შემდეგ. თუ target ცალკეული commitment-ით არის blocked, ეს ერთი design decision-ია და არა tuning-ის პრობლემა; თუ არც ერთი ცალკეული relaxation არ შველის, მაშინ search-ის გაშვება ამ axis set-ით ცნობილად უშედეგო ხარჯია.

`slice_of_agreement`-ის როლი აქ სპეციფიკურია. "Unreachable" თავისთავად არ არის actionable. `z = 1` კი actionable არის: ის ამბობს, რომ ორი program არ არის ერთი და იმავე ფუნქციის ორი ჩანაწერი, არამედ ერთი მათგანი მეორის specialization-ია input-ის ერთ slice-ზე — ანუ დაკარგული transformation არის input encoding-ის ცვლილება და არა უფრო ჭკვიანური formula. სწორედ ეს დაასკვნა 0027-მა co-Z-ზე, და ეს დასკვნა აქ ჩვეულებრივი algebra-ს კონსტრუქციაზე რეპროდუცირდება.

`output_extension` სტრიქონი დამოუკიდებელი, იაფი შედეგია: ერთი commitment-ის მოხსნა საკმარისია იმისთვის, რომ candidate reachable გახდეს, თან shared key-ზე map საერთოდ ხელუხლებელი რჩება.

`specialised_input` კი აზუსტებს, თუ რას ნიშნავს actionable. მისი სხვაობა ორ ჭეშმარიტ slice-ად იშლება, მაგრამ მხოლოდ ერთი მათგანია ინსტრუქცია. `c = 2` ამბობს, რომ target არის reference-ის specialization მეორე input-ის ერთ მნიშვნელობაზე, ანუ იგივე დასკვნა, რაც `z = 1`-ზე 0027-ში; `a = 0` კი მხოლოდ იმას ამბობს, რომ ნულზე ყველაფერი ნულია. თუ `.primary` მეორეს აბრუნებს, negative control-ის სწორედ ის ნაწილი იკარგება, რომლისთვისაც ის დაიწერა.

## Test power და მისი გაზომილი ზღვარი

Suite-ის ძალა გაიზომა mutation testing-ით მთელი ხის **იზოლირებულ ასლზე** (`src` + test file scratchpad-ში, working tree ხელუხლებელი). თითო mutant ცალკე გაშვება, `64` ტესტი:

| mutant | შედეგი | ვინ კლავს |
|---|---|---|
| M1 — drop row-ები set subtraction-ით ჩანაცვლებული | **გადარჩა** | არავინ |
| M2 — primary ლექსიკოგრაფიულად (მიღებული ვერსიის დეფექტი) | killed | `6` ტესტი |
| M3 — rank truncate-ის შემდეგ | killed | `1` ტესტი |
| M4 — pool task ისევ id-ით ეძებს წყვილს | killed | `4` ტესტი |
| M5 — `map_equality`-ის გადაწყვეტილება declared set-ზე დამოკიდებული | killed | `7` ტესტი |
| M6 — weakening row გაყალბებული `map_equality`-ის drop-ით | killed | `2` ტესტი |
| M7 — `non_constant_keys` ყოველთვის ყველა shared key | killed | `5` ტესტი |
| M8 — sweep caller-ის წყვილებს იგნორირებს | killed | `5` ტესტი |
| M9 — `factor_degree` ranking key-დან ამოღებული | killed | `1` ტესტი |
| M10 — retained-structure ranking key-დან ამოღებული | killed | `5` ტესტი |

ათიდან ცხრა killed. M9 და M10 ცალკეა, რომ ranking-ის სამივე გასაღები დამოუკიდებლად იყოს მზიდი და არა მხოლოდ მათი ჯამი. **M1 გადარჩა, და ეს გამოსასწორებელი არ არის — ეს დასადგენი ფაქტია.**

**რატომ ვერ კვდება M1.** `reachability_verdict`-ში ვერც ერთი commitment-ის გადაწყვეტილება ვერ იყურება იმაზე, თუ რომელი **სხვა** commitment-ია declared: თითოეული მხოლოდ ორი program-ისა და გაზიარებული `Evidence`-ის ფუნქციაა. აქედან პირდაპირ გამომდინარეობს, რომ declared set-იდან ერთი სახელის მოშორება მხოლოდ ამ სახელს შლის violation-ების სიიდან. ანუ

```text
drop(c).remaining_violations  ==  baseline.violated  minus  {c}
```

არის **თეორემა და არა დამთხვევა**: ის ყველა შესაძლო reference/target წყვილისთვის მართალია, და შესაბამისად არ არსებობს წყვილი, რომელიც shipped re-decision-ს set subtraction-ისგან გამოარჩევს. კონტრმაგალითის აგება მოითხოვდა commitment-ს, რომლის გადაწყვეტილება declared set-ზეა დამოკიდებული — ზუსტად იმას, რაც მოდულს განზრახ არ აქვს. `map_equal`-ის მხოლოდ **shared** key-ებზე შედარება ამ დამოუკიდებლობის მთავარი მზიდი ნაწილია: ყველა key-ზე შედარება map-ის verdict-ს `preserve_outputs`-ზე დამოკიდებულს გახდიდა.

ხელოვნური წყვილი, რომელიც უფრო ძლიერად გამოიყურებოდა, არ აშენებულა. სამაგიეროდ დაემატა ის, რაც ნამდვილად ითქმის:

- `test_each_commitment_is_decided_independently_of_the_declared_set` — თეორემის **წანამძღვარი** პირდაპირ მოწმდება: შვიდივე წყვილი ოთხსახელიანი vocabulary-ის თექვსმეტივე ქვესიმრავლის მიმართ. M5-ს შვიდი ტესტი კლავს და ეს მათ შორისაა — ის ერთადერთია, რომელიც პირდაპირ ამ თვისებას ამოწმებს.
- `test_drop_rows_are_set_subtraction_by_construction` — თეორემა თავად არის ჩამაგრებული, docstring-ში კი ღიად წერია, რომ M1-ის ტიპის fake ამ row-ებს გაივლის და რომ ეს არის მათემატიკის თვისება და არა suite-ის ხარვეზი.
- `test_the_weakening_row_is_not_derivable_from_the_baseline_violations` — მზიდი assertion.

**Re-decision მაინც სწორი კოდია.** ეს გაიზომა M5-ისა და M1-ის კომბინაციით იმავე იზოლირებულ ასლზე, `erased_prefix`-ის drop row-ები:

```text
shipped                    preserve_inputs->[map_equality]  preserve_outputs->[map_equality]  map_equality->[]
M1 (subtraction fake)      preserve_inputs->[map_equality]  preserve_outputs->[map_equality]  map_equality->[]
M5 (დამოუკიდებლობა გატეხილი)  preserve_inputs->[map_equality]  preserve_outputs->[]              map_equality->[]
M5 + M1                    preserve_inputs->[map_equality]  preserve_outputs->[map_equality]  map_equality->[]
```

Shipped და M1 იდენტურია — ამიტომ ვერც ერთი ტესტი ვერ არჩევს მათ. მაგრამ M5-ის ქვეშ shipped re-decision და subtraction **განსხვავდება** (`preserve_outputs` row: `[]` vs `[map_equality]`). ანუ re-decision არის სწორი კოდი იმ მომენტისთვის, როცა დამოუკიდებლობა შეწყდება, და suite ახლა სწორედ იმ ცვლილებას იჭერს, რომელიც მას მზიდად აქცევს.

**Weakening row არის ის, რაც ნამდვილად ვერ ყალბდება.** ის declared set-ს `projective_equality`-ს **ამატებს**, ანუ commitment-ს, რომელიც baseline-ზე საერთოდ არ გადაწყვეტილა; მისი verdict `baseline.violated`-ის ფუნქცია არ არის. `scaled_representative` და `erased_prefix` ამას ამტკიცებს: მათი baseline violation-ები და drop row-ები სიმბოლო-სიმბოლოში ერთნაირია, weakening row კი განსხვავებული (`reachable` vs `projective_equality` blocked). M6 სწორედ აქ კვდება.

## შეზღუდვები

- მოდული წყვეტს reachability-ს **declared structural commitment-ების მიმართ**. ეს არის **necessary condition და არა sufficient**. Target, რომელიც სამივე commitment-ს აკმაყოფილებს, ამით არ არის დამტკიცებული როგორც რომელიმე კონკრეტული finite axis set-ით მიღწევადი; ეს ცალკე და უფრო რთული საკითხია, რომელსაც ეს card არ პასუხობს.
- `slice_of_agreement` აბრუნებს **sufficient** condition-ს და არა სრულ agreement locus-ს. `erased_prefix`-ზე ნამდვილი agreement locus `z = 1`-ზე ფართოა (მაგალითად `x = 0, y = 0` ნებისმიერ `z`-ზე), მაგრამ ეს კომპონენტები არც ერთი საერთო factor-ით არ აღიწერება; ისინი agreement fraction-ში ჩანს და არა constraint-ების სიაში.
- `primary` არის **რანჟირებული არჩევანი და არა ერთადერთი ჭეშმარიტი პასუხი**. ყველა report-ული constraint თანაბრად ვერიფიცირებულია; რიგი მხოლოდ იმას ამბობს, რომელი უფრო ინფორმატიულია გამოცხადებული კრიტერიუმით. Caller-ს, რომელსაც სრული სურათი სჭირდება, `constraints`-ის მთელი სია აქვს, და `non_constant_keys` თითოეულზე ხსნის, რატომ დგას ის სწორედ იქ.
- Ranking-ის მეორე გასაღები (factor degree) მარტივობის შესახებ **მსჯელობაა და არა გაზომვა**: ის ამბობს, რომ წრფივი constraint უფრო ადვილად შესასრულებელია, და ეს caller-ის მოხერხებულობის კრიტერიუმია და არა ალგებრული ჭეშმარიტება.
- Agreement fraction declared sample set-ზეა და არა მთელ domain-ზე. `5/48` არის `25/240` და არა ალბათობა.
- `projective_equal` scale-ს ერთი weight-one key-ის გაყოფით კითხულობს. თუ არც ერთ shared key-ს weight `1` არ აქვს, გამოიყენება cross-multiplied weighted test, რომელიც necessary-ია და არა sufficient; `scale_key` მაშინ `None`-ია, რომ caller-მა ეს დაინახოს. წერტილი, სადაც scale ვერ იკითხება, ითვლება `undetermined`-ად და agreement fraction-იდან გამოირიცხება.
- Evaluation assignment-ების მიხედვით მიდის და არა collapsed symbolic form-ზე, ამიტომ undefined point სწორად აღინიშნება; მაგრამ program-ის domain rational function-ების კლასით არის შემოსაზღვრული და მოდული არ მოდელირებს magnitude ან representation-level gate-ებს, რომლებსაც vendored engine ატარებს.
- Corpus შვიდი წყვილისგან შედგება და ხელით არის აშენებული. ის ვალიდაციისთვისაა და არა statistical claim-ისთვის.
- Suite ვერ არჩევს drop row-ების ხელახალ გადაწყვეტას set subtraction-ისგან, და ეს გაზომილია (M1 გადარჩა). ეს არ არის დასაფარი ხარვეზი: დამოუკიდებლად გადაწყვეტილი commitment-ებისთვის ორივე ერთსა და იმავეს იძლევა ყველა შესაძლო წყვილზე. მზიდი counterfactual არის weakening row.
- Commitment vocabulary დახურულია ოთხ სახელზე. `coordinate_change`-ის ტიპის axis, რომელსაც 0027 section C ითხოვს, აქ არ არის იმპლემენტირებული და ამ card-ის scope-ში არ შედის.

## Evidence-ის კლასიფიკაცია

- ცხრილებში მოცემული verdict-ები, agreement count-ები, slice constraint-ები და relaxation შედეგები executable **observations** არის; ისინი `reachability_sweep(workers=1)`-ით რეპროდუცირდება.
- Multicore ცხრილი **measurement** არის ერთ კონკრეტულ 16-core Windows მანქანაზე; ის ამ machine-ის მიღმა არ განზოგადდება. Mutation ცხრილიც measurement არის, იზოლირებულ ასლზე გაშვებული.
- `primary`-ის შერჩევის წესი **გამოცხადებული კონვენციაა** და არა აღმოჩენილი ფაქტი: ის ირჩევს, თუ რას ნიშნავს "უფრო ინფორმატიული", და ეს არჩევანი აქ არის დასაბუთებული, არა დამტკიცებული.
- დებულება, რომ completeness და representation change-ის მიმართ სიბრმავე ერთი და იგივე property-ია, არის **derived** არგუმენტი 0027-იდან, აქ კი ჩვეულებრივ algebra-ზე რეპროდუცირებული და test-ით მიმაგრებული.
- არ არის claimed: რომ commitment-ების დაკმაყოფილება reachability-ს ნიშნავს; რომ ეს corpus რაიმე ზოგად განაწილებას წარმოადგენს; რომ slice constraint-ები სრულ agreement locus-ს აღწერს.

## ვალიდაცია

გარემო: Python `3.14.3`, sympy `1.14.0`, Windows 11, `16` core.

```text
python -m pytest tests/test_reachability_control.py -q
64 passed
```

```text
python -m pytest -q
354 passed
```

ამ card-მდე suite `290 passed` იყო; დამატებული `64` test სრულად ამ მოდულს ეხება. Card-ის მიღების შემდეგ ეს რიცხვი `45`-დან `64`-მდე გაიზარდა (`+19`): `5` primary-ის შერჩევაზე, `3` drop/weakening row-ების ძალაზე, `8` caller-ის corpus-ზე და `3` ახალი corpus წყვილის პარამეტრიზაციებიდან.

(ეს ქვე-დაშლა review-ის შემდეგ გასწორდა. ადრე ეწერა `7` caller-ის corpus-ზე და `4` პარამეტრიზაცია; collected node-id-ების შედარებამ მიღებულ HEAD ვერსიასა და working tree-ს შორის აჩვენა `45 -> 64`, `19` დამატებული, `0` წაშლილი, დაშლით `5 / 3 / 8 / 3`. `test_an_empty_corpus_is_refused` მერვე caller-corpus ტესტია, ხოლო პარამეტრიზებული instance სამია, არა ოთხი. ჯამი და პირველი ორი bucket თავიდანვე სწორი იყო.)

Mutation run იზოლირებულ ასლზე: `10` mutant, `9` killed, `1` გადარჩენილი (M1, ზემოთ ახსნილი).

Determinism ცალკე შემოწმდა სამ დამოუკიდებელ process-ში: `reachability_sweep(workers=1)`-ის JSON digest (`sha256` sorted-key JSON-ზე, პირველი `16` hex სიმბოლო) სამივეჯერ `7c912691b5f95d0b`. Card-ის მიღებულ ვერსიაში ეს digest `35d9b1d5082b918f` იყო; ის შეიცვალა, რადგან report-ს დაემატა მეშვიდე წყვილი და `SliceConstraint`-ს ორი ახალი ველი (`non_constant_keys`, `factor_degree`).
