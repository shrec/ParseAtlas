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

ორი გადაწყვეტილება `map_equal`-ში არის ის, რაც "blocked by exactly one commitment"-ს აზრიან განცხადებად აქცევს. პირველი: შედარება მხოლოდ **shared** output key-ებზე მიდის — თუ candidate ზედმეტ key-ს აქვეყნებს, ეს `preserve_outputs`-ის საქმეა, და მისი აქ ჩაკეცვა ყოველ output extension-ს map failure-დაც აჩვენებდა. მეორე: შედარება **positional** არის — program-ები, რომელთა input list მხოლოდ სახელით განსხვავდება, მაინც ერთი და იმავე ordered tuple-ის ორი ფუნქციაა, ზუსტად ისე, როგორც 0027-მა ორივე program identical tuple-ებზე გამოთვალა; სახელის განსხვავებას `preserve_inputs` წყვეტს და არა equivalence test.

`slice_of_agreement` მოდულის ყველაზე სასარგებლო output-ია. მეთოდი: აიღე თითო shared output key-ზე ორი map-ის სხვაობა, გაასუფთავე denominator, factor-ად დაშალე numerator და დაიტოვე ის irreducible factor-ები, რომლებიც **ყველა** nonzero სხვაობაშია. თითოეული ასეთი factor წყდება ერთი symbol-ის მიმართ და მიღებული substitution უკან ბრუნდება ყველა სხვაობაში; მხოლოდ ის constraint-ები ქვეყნდება, რომლებზეც ყველა სხვაობა ზუსტად ნულდება. ეს "unreachable"-ს "unreachable, და აი ის substitution, რომელიც ხიდს გადებდა"-დ აქცევს.

`Evidence` ერთხელ იზომება და ყველა counterfactual-ს ერთი და იგივე გაზომვა ეძლევა, ამიტომ ორ verdict-ს შორის განსხვავება მხოლოდ commitment set-იდან შეიძლება მოდიოდეს და არასდროს ხელახალი გაზომვიდან.

Sample set deterministic-ია ორმაგად: ჯერ fixed corner block (all-ones წერტილი და წერტილები, სადაც ერთი coordinate `1`-ზე ან `0`-ზეა მიმაგრებული, ასე რომ single-input slice ყოველთვის მონახულებულია), შემდეგ `VALUE_POOL`-იდან წერტილები fixed linear congruential sequence-ით. Global RNG არსად ირევა. წერტილები distinct-ია, ამიტომ set არ შეიძლება იყოს `len(VALUE_POOL) ** arity`-ზე დიდი: arity 2-ზე ეს ჭერი `121`-ია და sample set მთელ grid-ს ავსებს, arity 3-ზე კი მოთხოვნილი `240` მიიღწევა.

## Corpus

ექვსი reference/target წყვილი, სადაც პასუხი დამოუკიდებლად, algebra-დან არის ცნობილი მოდულის გაშვებამდე. `expected_violations` corpus-შია ჩაწერილი და test file-შიც ლიტერალურად მეორდება, ასე რომ corpus entry ვერ გადაასწორებს იმას, თუ რა ჩაითვლება სწორად.

| id | reference -> target | რატომ ეს პასუხი |
|---|---|---|
| `rewriteable_polynomial` | `square_of_sum` -> `expanded_square` | ერთი polynomial-ის factored და expanded ფორმა: ერთი და იგივე input, output key და map |
| `output_extension` | `square_of_sum` -> `square_of_sum_with_cross` | target აქვეყნებს ერთ დამატებით მნიშვნელობას, რომელსაც უკვე ითვლის; shared key-ზე map ხელუხლებელია |
| `input_recoding` | `square_of_sum` -> `square_of_sum_recoded` | target სხვაგვარად encoded input-ს აცხადებს; იმავე ordered tuple-ის ფუნქციად იგივე map-ია |
| `erased_prefix` | `graded_form` -> `erased_prefix_form` | 0027-ის structural analogue ჩვეულებრივ algebra-ში: lifting prefix-ის წაშლა სხვა ფუნქციას ტოვებს იმავე სამ რიცხვზე |
| `scaled_representative` | `ratio_reduced` -> `ratio_scaled` | ნამდვილად ერთი და იგივე ობიექტი scaling convention-ის სიზუსტით, მაგრამ არა როგორც raw map |
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
    for k in (1, 4, 6, 8, 16, 64):
        pairs = tuple(CORPUS) * k
        s = best(pairs, 1)
        p = best(pairs, 6)
        print(f"{len(pairs):4d} pairs  sequential {s:7.3f}s  pool6 {p:7.3f}s  speedup {s / p:5.2f}x")
```

Best of three, warm parent process, 16 core:

| pairs | sequential | pool of 6 | speedup |
|---|---|---|---|
| 6 | `0.154 s` | `0.721 s` | `0.21x` |
| 24 | `0.663 s` | `0.826 s` | `0.80x` |
| 36 | `1.024 s` | `0.880 s` | `1.16x` |
| 48 | `1.360 s` | `0.942 s` | `1.44x` |
| 96 | `2.603 s` | `1.206 s` | `2.16x` |
| 384 | `10.597 s` | `2.567 s` | `4.13x` |

ერთი წყვილი დაახლოებით `26 ms` sympy cancellation-ია, ხოლო Windows `spawn` child `0.42 s`-ს იხდის ამ მოდულის import-ზე, სანამ რაიმეს დაიწყებს (`python -X importtime -c "import parseatlas.reachability_control"`). Break-even `36` წყვილთანაა და margin მხოლოდ `48`-იდან ხდება მკაფიო, ამიტომ `PARALLEL_THRESHOLD_PAIRS = 48`.

ამ card-ის ექვსწყვილიანი corpus ამიტომ **sequential-ად მუშაობს** — ეს გაზომილი გადაწყვეტილებაა. Worker count `os.cpu_count()`-იდან გამოიყვანება (`WORKER_HEADROOM_CORES = 2`, `WORKER_CAP = 12`) და არასდროს hardcoded constant-იდან. Test suite ამტკიცებს, რომ sequential და parallel report-ები იდენტურია: parallelism მხოლოდ სიჩქარეს ცვლის და არასდროს იმას, რაც იზომება.

## დაკვირვებული შედეგები

`python -c "from parseatlas.reachability_control import reachability_sweep; reachability_sweep(workers=1)"`:

| pair | violated commitments | map agreement | agreement fraction | slice |
|---|---|---|---|---|
| `rewriteable_polynomial` | — | `121/121` | `1` | — |
| `output_extension` | `preserve_outputs` | `121/121` | `1` | — |
| `input_recoding` | `preserve_inputs` | `121/121` | `1` | — |
| `erased_prefix` | `map_equality` | `25/240` | `5/48` | `z = 1` |
| `scaled_representative` | `map_equality` | `11/121` | `1/11` | `x = 0` |
| `coz_analogue` | `preserve_inputs`, `preserve_outputs`, `map_equality` | `25/240` | `5/48` | `z = 1` |

- reachable წყვილი: `1` (`rewriteable_polynomial`), და ის reachable-ია სამივე commitment-ის ქვეშ, `RELAXED_COMMITMENTS`-ის ქვეშ და მთელი vocabulary-ის ქვეშაც.
- blocked წყვილი: `5`.
- `all_match_known_answers`: `True` — ექვსივე verdict დამოუკიდებლად ცნობილ პასუხს ემთხვევა, slice-ის ჩათვლით.

Slice-ის ემპირიული cross-check: `erased_prefix`-ისთვის sample set `z = 1`-ზე პროექციის შემდეგ `107` განსხვავებულ წერტილს იძლევა და agreement `107/107`-ია; `scaled_representative`-ისთვის `x = 0`-ზე `11/11`.

Relaxation analysis:

| pair | drop `preserve_inputs` | drop `preserve_outputs` | drop `map_equality` | weaken to `projective_equality` | sole blocker |
|---|---|---|---|---|---|
| `output_extension` | blocked | **reachable** | blocked | blocked | `preserve_outputs` |
| `input_recoding` | **reachable** | blocked | blocked | blocked | `preserve_inputs` |
| `erased_prefix` | blocked | blocked | **reachable** | blocked | `map_equality` |
| `scaled_representative` | blocked | blocked | **reachable** | **reachable** | `map_equality` |
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

## შეზღუდვები

- მოდული წყვეტს reachability-ს **declared structural commitment-ების მიმართ**. ეს არის **necessary condition და არა sufficient**. Target, რომელიც სამივე commitment-ს აკმაყოფილებს, ამით არ არის დამტკიცებული როგორც რომელიმე კონკრეტული finite axis set-ით მიღწევადი; ეს ცალკე და უფრო რთული საკითხია, რომელსაც ეს card არ პასუხობს.
- `slice_of_agreement` აბრუნებს **sufficient** condition-ს და არა სრულ agreement locus-ს. `erased_prefix`-ზე ნამდვილი agreement locus `z = 1`-ზე ფართოა (მაგალითად `x = 0, y = 0` ნებისმიერ `z`-ზე), მაგრამ ეს კომპონენტები არც ერთი საერთო factor-ით არ აღიწერება; ისინი agreement fraction-ში ჩანს და არა constraint-ების სიაში.
- Agreement fraction declared sample set-ზეა და არა მთელ domain-ზე. `5/48` არის `25/240` და არა ალბათობა.
- `projective_equal` scale-ს ერთი weight-one key-ის გაყოფით კითხულობს. თუ არც ერთ shared key-ს weight `1` არ აქვს, გამოიყენება cross-multiplied weighted test, რომელიც necessary-ია და არა sufficient; `scale_key` მაშინ `None`-ია, რომ caller-მა ეს დაინახოს. წერტილი, სადაც scale ვერ იკითხება, ითვლება `undetermined`-ად და agreement fraction-იდან გამოირიცხება.
- Evaluation assignment-ების მიხედვით მიდის და არა collapsed symbolic form-ზე, ამიტომ undefined point სწორად აღინიშნება; მაგრამ program-ის domain rational function-ების კლასით არის შემოსაზღვრული და მოდული არ მოდელირებს magnitude ან representation-level gate-ებს, რომლებსაც vendored engine ატარებს.
- Corpus ექვსი წყვილისგან შედგება და ხელით არის აშენებული. ის ვალიდაციისთვისაა და არა statistical claim-ისთვის.
- Commitment vocabulary დახურულია ოთხ სახელზე. `coordinate_change`-ის ტიპის axis, რომელსაც 0027 section C ითხოვს, აქ არ არის იმპლემენტირებული და ამ card-ის scope-ში არ შედის.

## Evidence-ის კლასიფიკაცია

- ცხრილებში მოცემული verdict-ები, agreement count-ები, slice constraint-ები და relaxation შედეგები executable **observations** არის; ისინი `reachability_sweep(workers=1)`-ით რეპროდუცირდება.
- Multicore ცხრილი **measurement** არის ერთ კონკრეტულ 16-core Windows მანქანაზე; ის ამ machine-ის მიღმა არ განზოგადდება.
- დებულება, რომ completeness და representation change-ის მიმართ სიბრმავე ერთი და იგივე property-ია, არის **derived** არგუმენტი 0027-იდან, აქ კი ჩვეულებრივ algebra-ზე რეპროდუცირებული და test-ით მიმაგრებული.
- არ არის claimed: რომ commitment-ების დაკმაყოფილება reachability-ს ნიშნავს; რომ ეს corpus რაიმე ზოგად განაწილებას წარმოადგენს; რომ slice constraint-ები სრულ agreement locus-ს აღწერს.

## ვალიდაცია

გარემო: Python `3.14.3`, sympy `1.14.0`, Windows 11, `16` core.

```text
python -m pytest tests/test_reachability_control.py -q
45 passed
```

```text
python -m pytest -q
335 passed
```

ამ card-მდე suite `290 passed` იყო; დამატებული `45` test სრულად ამ მოდულს ეხება.

Determinism ცალკე შემოწმდა სამ დამოუკიდებელ process-ში: `reachability_sweep(workers=1)`-ის JSON digest სამივეჯერ `35d9b1d5082b918f`.
