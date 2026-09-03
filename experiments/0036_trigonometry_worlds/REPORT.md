# ParseAtlas ექსპერიმენტი 0036: sine in the twenty-five worlds

## მიზანი

პასუხი, რომლითაც ეს report იწყება, არის **question 3** და **question 4**: გადარჩება თუ არა
ტრიგონომეტრია სხვა convention-ში, და ვინ ინახავს მას ყველაზე მეტად.

Pythagorean identity დაწერილია როგორც string:

```text
s*s + c*c
```

ჩვენს convention-ში ის `1`-ის ტოლია ყოველი `x`-ისთვის. გაზომვა აჩვენებს, რომ **`25` world-იდან
`13`-ში ის კვლავ `1`-ია** — `G0`, `G09`, `G10`, `G12`, `G13`, `G14`, `G15`, `G16`, `G17`, `G18`,
`G22`, `G23`, `G24`. დანარჩენ `12`-ში იგივე string denote-ს აკეთებს `c*s*(c + s)`-ს, ანუ
`sqrt(2)*sin(x)*sin(x + pi/4)*cos(x)`-ს — ეს არ არის constant, ეს არის wave. ე.ი. Pythagorean
identity **არ არის** ჩვენი world-ის კუთვნილება; ის იმ world-ების კუთვნილებაა, სადაც `*`
უფრო მაგრად ბოჭავს, ვიდრე `+`.

რვა identity-ის სრულ სვეტზე ყველაზე მეტს ინახავს **სამი world: `G0`, `G23`, `G24` — თითოეული
`8/8`**. ე.ი. conventional world ნამდვილად საუკეთესოთა შორისაა, მაგრამ **უნიკალურად საუკეთესო არ
არის**: `G23` (`/ * + -`) და `G24` (`/ * - +`) მას ზუსტად უტოლდებიან.

ყველაზე მკვეთრი დეტალი კი ეს არის: `G17`-ის precedence order არის `* / + -` — **ზუსტად `G0`-ის
რიგი**, ოღონდ strict, ანუ `*` და `/` ცალკე level-ებზე. `G17` ინახავს `7/8`-ს. ის კარგავს
`1 + s/c*s/c = 1/cos(x)**2`-ს, რადგან მასთან `s/c*s/c` იშლება როგორც `s/(c*s)/c = 1/c**2`.
ე.ი. ჩვენს world-ში ამ identity-ს **precedence order არ იცავს** — მას იცავს **tie**: ის, რომ `*`
და `/` ერთსა და იმავე level-ზე დგანან და chain მარცხნიდან იშლება.

## Three routes to sine

sine მათემატიკაში ერთხელ არ არის განსაზღვრული. ის ხასიათდება სულ ცოტა სამი **written form**-ით,
ხოლო written form სწორედ ის ობიექტია, რომელიც სხვა convention-ში სხვანაირად იკითხება.

```text
route 1   the series      "x - x*x*x/6 + x*x*x*x*x/120"   -> რომელი polynomial-ია ეს აქ?
route 2   the composition sin(<inner token string>)       -> რომელი wave-ია ეს აქ?
route 3   the identities  "s*s + c*c"  (s, c formal)      -> კვლავ 1-ია ეს აქ?
```

სამივე ჩვენს world-ში ერთსა და იმავე sine-ს აღწერს. **სხვაგან ისინი არ თანხმდებიან**, და სწორედ ეს
divergence არის ამ ექსპერიმენტის შედეგი.

Route 3 placeholder-ებს იყენებს, რადგან Generation 1 language-ს function-call syntax არ აქვს:
`sin(x)` მასში application-ად ვერ tokenize-დება. Identity-ის convention-sensitivity კი მთლიანად
argument level-ზეა — იმაში, თუ როგორ ასოცირდება `s*s + c*c`, და არა იმაში, თუ რას ნიშნავს `sin`.
ამიტომ string იკითხება formal `s`, `c` (და `sa`, `ca`, `sb`, `cb`) placeholder-ებით, ხოლო
substitution `s -> sin(x)`, `c -> cos(x)` მხოლოდ **reading-ის შემდეგ** ხდება.

## Corpus

Route 1 — ერთი string, sine-ის სტანდარტული truncated Maclaurin series. `^` არ არსებობს, ამიტომ
ხარისხები product-ებად იწერება — და სწორედ ეს ხდის string-ს convention-sensitive-ს:

```text
x - x*x*x/6 + x*x*x*x*x/120
```

გამოცხადებული sample point-ები (sweep-ამდე დაფიქსირებული): `0`, `pi/6`, `pi/4`, `pi/3`, `pi/2`,
`pi`, `2*pi`, `3`, `10`.

Route 2 — ხუთი inner token sequence, პირველი პროექტის founding sequence-ია:

```text
2*t + 1 - t/2
t/2 + 1 - 2*t
3*t - 2 + 1
1 - 2*t/4 + 3*t
t*t - 3*t + 2
```

outer function: `sin`, `cos`, `tan`. სულ `5 * 3 * 25 = 375` reading.

Route 3 — რვა identity, argument-level string-ებად:

| identity | string | target |
|---|---|---|
| `pythagorean` | `s*s + c*c` | `1` |
| `cofunction_zero` | `s*s + c*c - 1` | `0` |
| `double_angle_sine` | `2*s*c` | `sin(2*x)` |
| `double_angle_cosine` | `c*c - s*s` | `cos(2*x)` |
| `tangent` | `s/c` | `tan(x)` |
| `pythagorean_tangent` | `1 + s/c*s/c` | `1/cos(x)**2` |
| `angle_addition_sine` | `sa*cb + ca*sb` | `sin(a + b)` |
| `angle_addition_cosine` | `ca*cb - sa*sb` | `cos(a + b)` |

სულ `8 * 25 = 200` reading.

ყოველი ობიექტი დაჯგუფებულია project semantic key-ით — `(canonical form, domain, excluded points)`
— და **არასოდეს მხოლოდ canonical text-ით**.

## დაკვირვებული შედეგები

### Route 3: which identities survive

`25` world × `8` identity. მწკრივები დალაგებულია შენახული identity-ების რაოდენობით.

| world | precedence | pyth | cofunc | 2sc | cc-ss | s/c | 1+tan2 | sin(a+b) | cos(a+b) | kept |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---:|
| `G0` | `*/ +-` | yes | yes | yes | yes | yes | yes | yes | yes | `8` |
| `G23` | `/ * + -` | yes | yes | yes | yes | yes | yes | yes | yes | `8` |
| `G24` | `/ * - +` | yes | yes | yes | yes | yes | yes | yes | yes | `8` |
| `G13` | `* + - /` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G14` | `* + / -` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G15` | `* - + /` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G16` | `* - / +` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G17` | `* / + -` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G18` | `* / - +` | yes | yes | yes | yes | yes | . | yes | yes | `7` |
| `G12` | `- / * +` | yes | . | yes | . | yes | yes | yes | . | `5` |
| `G22` | `/ - * +` | yes | . | yes | . | yes | yes | yes | . | `5` |
| `G03` | `+ * - /` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G04` | `+ * / -` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G06` | `+ / * -` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G09` | `- * + /` | yes | . | yes | . | yes | . | yes | . | `4` |
| `G10` | `- * / +` | yes | . | yes | . | yes | . | yes | . | `4` |
| `G20` | `/ + * -` | . | . | yes | yes | yes | . | . | yes | `4` |
| `G01` `G02` `G05` `G07` `G08` `G11` `G19` `G21` | (რვა world) | . | . | yes | . | yes | . | . | . | `2` |

დაკვირვებული სტრუქტურა:

- **`8/8` ინახავს ზუსტად ის სამი world, სადაც `/` ბოჭავს არანაკლებ მაგრად, ვიდრე `*`, და ორივე
  უფრო მაგრად, ვიდრე `+` და `-`**: `G0` (tie-ით), `G23`, `G24`. ეს არის ერთადერთი კონფიგურაცია,
  რომელშიც `s/c*s/c` იშლება როგორც `(s/c)*(s/c) = s**2/c**2`.
- **`7/8` ინახავს ზუსტად ის ექვსი world, სადაც `*` პირველია** (`3! = 6` permutation): `G13`–`G18`.
  ისინი მხოლოდ `1 + s/c*s/c`-ს კარგავენ.
- `G12` და `G22` ინახავენ `1 + s/c*s/c`-ს (რადგან მათთან `/` უფრო მაგრად ბოჭავს, ვიდრე `*`),
  მაგრამ კარგავენ `c*c - s*s`-ს და `s*s + c*c - 1`-ს, რადგან `-` მათთან `*`-ზე მაგარია.
- **ორი identity convention-free-ია**: `2*s*c` და `s/c` `25`-ვე world-ში იმავეს denote-ს აკეთებენ.
  ორივე ერთ operator kind-ს იყენებს, ამიტომ precedence-ს მათზე გავლენა არ აქვს. ეს იყო
  *predicted* corpus-ში ჩადებამდე და გაზომვამ დაადასტურა — ისინი control-ია და არა შედეგი.

`pythagorean_tangent`-ის სრული სურათი (`5` semantic class):

| class | denoted | substituted | holds | worlds |
|---|---|---|:-:|---|
| `I01` | `1 + s**2/c**2` | `cos(x)**(-2)` | yes | `G0` `G12` `G22` `G23` `G24` |
| `I02` | `(s + 1)/(c**2*s)` | `(1 + 1/sin(x))/cos(x)**2` | no | `G01` `G03` `G04` `G07` `G09` `G13` `G14` `G15` |
| `I03` | `s*(s + 1)/c**2` | `(sin(x) + 1)*sin(x)/cos(x)**2` | no | `G02` `G05` `G06` `G08` |
| `I04` | `1 + c**(-2)` | `tan(x)**2 + 2` | no | `G10` `G16` `G17` `G18` |
| `I05` | `s*(c + s)/c**2` | `(-sqrt(2)*cos(2*x + pi/4) + 1)/(2*cos(x)**2)` | no | `G11` `G19` `G20` `G21` |

`I04` განსაკუთრებით ლამაზია: `1 + c**(-2)` substitution-ის შემდეგ არის `tan(x)**2 + 2`. ე.ი. იმ
ოთხ world-ში ეს string არა `sec**2`-ს, არამედ `tan**2`-ს **პლუს ორს** ნიშნავს — ცნობადი
ტრიგონომეტრიული ობიექტია, უბრალოდ სხვა.

### Route 1: the series

`25` world reading, **`14` semantic class**, **`11` განსხვავებული canonical value**. სხვაობა
`14 - 11 = 3` სწორედ triple discipline-ის შედეგია: ოთხი class **ერთსა და იმავე** function-ს
(constant `0`) denote-ს აკეთებს და მხოლოდ validity restriction-ით განსხვავდება.

| class | denoted | excl | odd (value) | odd (partial fn) | degree | `x -> +oo` | `x -> -oo` | worlds |
|---|---|---:|:-:|:-:|---|---|---|---|
| `S01` | `x**5/120 - x**3/6 + x` | `0` | yes | yes | `5` | `oo` | `-oo` | `G0` `G18` `G24` |
| `S02` | `0` | `2` | yes | no | — | `0` | `0` | `G01` `G07` |
| `S03` | `0` | `1` | yes | no | — | `0` | `0` | `G02` `G05` `G08` |
| `S04` | `(1 - x**2)/(120*x**3*(x + 6))` | `2` | no | no | `2/4` | `0` | `0` | `G03` |
| `S05` | `x - 1/(120*x*(x + 6))` | `2` | no | no | `3/2` | `oo` | `-oo` | `G04` |
| `S06` | `x*(-x**6 + 120*x + 720)/(120*(x + 6))` | `1` | no | no | `7/1` | `-oo` | `-oo` | `G06` |
| `S07` | `0` | `4` | yes | no | — | `0` | `0` | `G09` |
| `S08` | `x**5/120` | `0` | yes | yes | `5` | `oo` | `-oo` | `G10` `G12` `G22` |
| `S09` | `0` | `0` | yes | yes | — | `0` | `0` | `G11` `G19` `G21` |
| `S10` | `(-x**3 + x)/(120*x**5 + 720)` | `4` | no | no | `3/5` | `0` | `0` | `G13` `G15` |
| `S11` | `x*(120*x**5 - x**2 + 720)/(120*(x**5 + 6))` | `4` | no | no | `6/5` | `oo` | `-oo` | `G14` |
| `S12` | `x*(x**4 - 20*x**2 + 20)/120` | `0` | yes | yes | `5` | `oo` | `-oo` | `G16` |
| `S13` | `-x**5/120 - x**3/6 + x` | `0` | yes | yes | `5` | `-oo` | `oo` | `G17` `G23` |
| `S14` | `-7*x**7/720 + x` | `0` | yes | yes | `7` | `-oo` | `oo` | `G20` |

- **`25`-დან `9` world კითხულობს sine-ის series-ს როგორც identically zero**: `G01`, `G02`, `G05`,
  `G07`, `G08`, `G09`, `G11`, `G19`, `G21`. მიზეზი სტრუქტურულია — იმ ordering-ებში `-` ან `+`
  `*`-ზე მაგარია, ამიტომ `x - x*x*x/6 + ...` ჯერ `(x - x)`-ს აჯგუფებს და მთელი product ნულდება.
- **odd**: `19` world-ში reading odd-ია როგორც expression (`f(-x) == -f(x)`); მაგრამ მხოლოდ
  `13`-ში არის ის odd როგორც **partial function**. სხვაობა ექვსი world-ია (`G01`, `G02`, `G05`,
  `G07`, `G08`, `G09`), რომლებიც `0`-ს კითხულობენ, მაგრამ ატარებენ validity restriction-ს `-6`-ზე
  (ან `-6`-ის მეხუთე ფესვზე) `+6`-ზე შესაბამისი restriction-ის გარეშე. მათი domain negation-ის
  მიმართ არ არის სიმეტრიული, ამიტომ oddness-ის განსაზღვრება მათზე არ ვრცელდება.
- **roots**: `S01`-ს ერთი real root აქვს (`{0}`), `S12`-ს ხუთი
  (`{0, ±sqrt(10 - 4*sqrt(5)), ±sqrt(4*sqrt(5) + 10)}`), `S14`-ს სამი, `S04`-ს ორი (`{-1, 1}`),
  ხოლო ცხრა zero-reading-ის root set არის `Reals`.
- **periodicity: `0` world-ში, `G0`-ის ჩათვლით**. ეს გაზომილია და არა ნავარაუდევი: ყოველი
  reading-ის `sympy_periodicity` არის ან `None` (period არ არსებობს), ან sentinel `0`
  (constant function — რომელსაც *ყოველი* period აქვს და ამიტომ fundamental period არ აქვს).
  Sentinel-ს აბრუნებს ზუსტად ის ცხრა world, რომელიც `0`-ს კითხულობს.

**Truncation error — `G0` ფასდაკლების გარეშე.** truncated series polynomial-ია **ყოველ** world-ში,
ჩვენსაში ისევე, როგორც სხვაგან; ის არც periodic-ია, და **არაკონსტანტურ** reading-ებში არც bounded. (`G11`, `G19`, `G21` string-ს კონსტანტა `0`-ად კითხულობენ, ამიტომ ისინი bounded-ია — მოდული მათ სწორად `unbounded_on_reals = False`-ად აფიქსირებს.)

| `x` | `0` | `pi/6` | `pi/4` | `pi/3` | `pi/2` | `pi` | `2*pi` | `3` | `10` |
|---|---|---|---|---|---|---|---|---|---|
| true `sin(x)` | `0.0000` | `0.5000` | `0.7071` | `0.8660` | `1.0000` | `0.0000` | `0.0000` | `0.1411` | `-0.5440` |
| `G0` | `0.0000` | `0.5000` | `0.7071` | `0.8663` | `1.0045` | `0.5240` | `46.5467` | `0.5250` | `676.6667` |
| `G17` | `0.0000` | `0.4993` | `0.7022` | `0.8453` | `0.8451` | `-4.5763` | `-116.6638` | `-3.5250` | `-990.0000` |
| `G20` | `0.0000` | `0.5235` | `0.7836` | `1.0338` | `1.3414` | `-26.2224` | `-3752.3039` | `-18.2625` | `-9.72e+04` |
| `G16` | `0.0000` | `0.0637` | `0.0526` | `-0.0064` | `-0.3045` | `-2.0939` | `41.3107` | `-1.9750` | `668.3333` |
| `G03` | undef | `0.0065` | `0.0010` | `-0.0001` | `-0.0004` | `-0.0003` | `-0.0001` | `-0.0003` | `-0.0001` |
| `G01` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` | `0.0000` |

`G0`-ის absolute error იმავე point-ებზე: `0`, `0.0000`, `0.0000`, `0.0003`, `0.0045`, **`0.5240`**,
**`46.5467`**, `0.3839`, **`677.2107`**.

თუ error-ს ორ ნაწილად გავყოფთ — near (`|x| <= pi/2`) და far (`pi`, `2*pi`, `3`, `10`) — სურათი
ორმხრივია და ორივე მხარე უნდა ითქვას:

| world | max error near | max error far |
|---|---:|---:|
| `G0` `G18` `G24` | `0.00452` | `677.211` |
| `G17` `G23` | `0.15486` | `989.456` |
| `G20` | `0.34139` | `97211.678` |
| `G16` | `1.30447` | `668.877` |
| ცხრა zero-world | `1.0` | `0.544` |
| `G03` | `1.00042` | `0.544` |

- near zone-ში conventional reading **ნამდვილად და მარტივად საუკეთესოა** — `0.0045` წინააღმდეგ
  შემდეგი საუკეთესოს `0.155`-ისა.
- far zone-ში იგივე conventional reading **ზედა-შუაშია და არა ყველაზე ცუდი**: შვიდი world მასზე უარესია (`G20` `97212`, `G06` `5198`, `G17`/`G23` `990`, `G10`/`G12`/`G22` `834`). `x = 10`-ზე მისი error
  `677.21`-ია, მაშინ როცა იმ world-ის error, რომელიც string-ს უბრალოდ `0`-ს უკითხავს, `0.544`-ია.
  მიზეზი ტრივიალურია და სწორედ ამიტომ ღირს მისი დაფიქსირება: `sin` bounded-ია, quintic — არა.
  ეს არ ნიშნავს, რომ `G01` "უკეთესად კითხულობს sine-ს"; ეს ნიშნავს, რომ **series route-ის
  სიზუსტე არსად, `G0`-ის ჩათვლით, არ არის sine-ის თვისება.**

### Route 2: sine as an outer function

`5` inner source × `25` world × `3` outer function = `375` reading, ყველა
`parseatlas.functions.analyze_outer_functions`-იდან (NF-2026-00004-ით შესწორებული instrument).

founding sequence `2*t + 1 - t/2`, outer `sin` — `8` semantic class, ზუსტად როგორც 0002-ში:

| class | inner | `sin(inner)` | const | frequency | period | worlds |
|---|---|---|:-:|---|---|---|
| `O01` | `3*t/2 + 1` | `sin(3*t/2 + 1)` | no | `3/2` | `4*pi/3` | `G0` `G14` `G17` `G18` `G22` `G23` `G24` |
| `O02` | `1` | `sin(1)` | **yes** | `0` | undefined | `G01` `G02` `G07` `G08` |
| `O03` | `t/2 + 1` | `sin(t/2 + 1)` | no | `1/2` | `4*pi` | `G03` |
| `O04` | `3*t/2 + 2` | `sin(3*t/2 + 2)` | no | `3/2` | `4*pi/3` | `G04` `G06` `G20` |
| `O05` | `t + 2` | `sin(t + 2)` | no | `1` | `2*pi` | `G05` `G19` `G21` |
| `O06` | `t/2 + 1/2` | `sin(t/2 + 1/2)` | no | `1/2` | `4*pi` | `G09` `G13` `G15` |
| `O07` | `3*t/2 + 1/2` | `sin(3*t/2 + 1/2)` | no | `3/2` | `4*pi/3` | `G10` `G12` `G16` |
| `O08` | `t + 1` | `sin(t + 1)` | no | `1` | `2*pi` | `G11` |

real domain ყველა რვა class-ზე `Reals`-ია; zero set-ები `ImageSet`-ების `Union`-ია — მაგალითად
`G0`-სთვის `4*n*pi/3 - 2/3 + {2*pi/3, 4*pi/3}`, `G03`-სთვის `4*n*pi - 2 + {2*pi, 4*pi}` — ხოლო
`O02`-ისთვის `EmptySet`, რადგან constant `sin(1)` ნულს არასოდეს კვეთს.

**`4` world (`G01`, `G02`, `G07`, `G08`) — constant collapse.** მათთვის `sin`-ის ამ expression-ზე
დადება wave-ს კი არ იძლევა, არამედ fixed number-ს. ეს ზუსტად 0002-ის შედეგია და აქ ხელახლა გაიზომა.

`period`-ის relation ხელუხლებელია: `sin` და `cos` იღებენ `2*pi/|a|`-ს, `tan` კი `pi/|a|`-ს.

| world | `a` | `sin` period | `cos` period | `tan` period |
|---|---|---|---|---|
| `G0` | `3/2` | `4*pi/3` | `4*pi/3` | `2*pi/3` |
| `G03` | `1/2` | `4*pi` | `4*pi` | `2*pi` |
| `G05` | `1` | `2*pi` | `2*pi` | `pi` |

ეს დამოუკიდებლად გადამოწმდა: `functions.py` period-ს argument-ის derivative-იდან იღებს, ხოლო
`sympy.calculus.util.periodicity` composed function-ს ზომავს. **`375` reading-ზე disagreement: `0`.**

ხუთივე source-ის ჯამში:

| inner source | `sin` semantic classes | constant collapse | wave | non-wave |
|---|---:|---|---:|---:|
| `2*t + 1 - t/2` | `8` | `G01` `G02` `G07` `G08` | `21` | `4` |
| `t/2 + 1 - 2*t` | `9` | `G01` `G07` | `13` | `12` |
| `3*t - 2 + 1` | `4` | — | `25` | `0` |
| `1 - 2*t/4 + 3*t` | `14` | `G01` `G04` `G07` | `9` | `16` |
| `t*t - 3*t + 2` | `5` | — | `0` | `25` |

- `125` `(source, world)` წყვილიდან **`9`-ში argument collapse-ს აკეთებს constant-ზე**, და
  collapse-ს სულ ხუთი world აჩვენებს სადმე: `G01`, `G02`, `G04`, `G07`, `G08`.
- `125`-დან **`68` არის genuine wave**; დანარჩენ `57`-ში `sin(...)` არც constant-ია და არც
  periodic — ის არის quadratic-ის ან rational-ის sine.
- `t*t - 3*t + 2` **ყველა `25` world-ში quadratic-ია**, ამიტომ `sin`-ის მასზე დადება არსად wave-ს
  არ იძლევა. periodicity guard-ს სწორედ ეს case ამოწმებს ერთდროულად `25`-ვე reading-ზე.
- `3*t - 2 + 1`-ს პირიქით — არც ერთი world არ ანგრევს: `4` class, ოთხივე `sin(3*t + b)` სახის,
  frequency `3` ყველგან. მხოლოდ phase `b` მოძრაობს (`-1`, `-3`, `-5`, `-9`). ე.ი. ეს shape
  convention-ის მიმართ თითქმის rigid-ია.

### The five headline answers

1. **რამდენ განსხვავებულ function-ს კითხულობს `25` world sine-ის series-ში?** `14` semantic class
   `(canonical, domain, excluded points)` triple-ით; `11` განსხვავებული canonical value, თუ
   validity restriction-ებს უგულებელვყოფთ.
2. **რამდენ world-ში რჩება ეს reading odd?** `19`-ში როგორც expression, `13`-ში როგორც partial
   function (domain-ის სიმეტრიის მოთხოვნით).
3. **გადარჩება Pythagorean identity conventional world-ის გარეთ?** დიახ — `12` სხვა world-ში:
   `G09`, `G10`, `G12`, `G13`, `G14`, `G15`, `G16`, `G17`, `G18`, `G22`, `G23`, `G24`.
4. **ვინ ინახავს ყველაზე მეტ identity-ს, და არის ეს `G0`?** `8/8`-ს ინახავს სამი world — `G0`,
   `G23`, `G24`. `G0` საუკეთესოთა შორისაა, მაგრამ არა უნიკალურად საუკეთესო.
5. **outer-function route-ზე რამდენ world-ში collapse-ს აკეთებს argument constant-ზე?** founding
   sequence-ზე — `4`; ხუთივე source-ის `125` წყვილიდან — `9`; collapse-ს სადმე აჩვენებს `5` world.

## Side-by-side: `G0`, `G16`, `G20`, `G01`

რა **არის** sine ამ ოთხ world-ში, სამივე route-ით.

| | `G0` (`*/ +-`) | `G16` (`* - / +`) | `G20` (`/ + * -`) | `G01` (`+ - * /`) |
|---|---|---|---|---|
| **route 1** denoted | `x**5/120 - x**3/6 + x` | `x*(x**4 - 20*x**2 + 20)/120` | `-7*x**7/720 + x` | `0` |
| degree | `5` | `5` | `7` | — |
| odd (value / partial fn) | yes / yes | yes / yes | yes / yes | yes / **no** |
| real roots | `{0}` | `{0, ±sqrt(10-4*sqrt(5)), ±sqrt(4*sqrt(5)+10)}` | `{0, ±2**(2/3)*3**(1/3)*5**(1/6)*7**(5/6)/7}` | `Reals` |
| excluded points | none | none | none | `-6`, `0` |
| periodic | **no** | **no** | **no** | **no** |
| `x -> ±oo` | `+oo` / `-oo` | `+oo` / `-oo` | `-oo` / `+oo` | `0` / `0` |
| max error (near / far) | `0.0045` / `677.2` | `1.3045` / `668.9` | `0.3414` / `97211.7` | `1.0` / `0.544` |
| **route 2** inner | `3*t/2 + 1` | `3*t/2 + 1/2` | `3*t/2 + 2` | `1` |
| `sin(inner)` | `sin(3*t/2 + 1)` | `sin(3*t/2 + 1/2)` | `sin(3*t/2 + 2)` | `sin(1)` |
| constant argument | no | no | no | **yes** |
| frequency / period | `3/2` / `4*pi/3` | `3/2` / `4*pi/3` | `3/2` / `4*pi/3` | `0` / undefined |
| `tan` period | `2*pi/3` | `2*pi/3` | `2*pi/3` | undefined |
| real domain | `Reals` | `Reals` | `Reals` | `Reals` |
| **route 3** `s*s + c*c` | `1` | `1` | `sqrt(2)*sin(x)*sin(x+pi/4)*cos(x)` | `sqrt(2)*sin(x)*sin(x+pi/4)*cos(x)` |
| `c*c - s*s` | `cos(2*x)` | `cos(2*x)` | `cos(2*x)` | `sqrt(2)*sin(x)*cos(x)*cos(x+pi/4)` |
| `1 + s/c*s/c` | `cos(x)**(-2)` | `tan(x)**2 + 2` | `(-sqrt(2)*cos(2*x + pi/4) + 1)/(2*cos(x)**2)` | `(1 + 1/sin(x))/cos(x)**2` |
| identities kept | `8/8` | `7/8` | `4/8` | `2/8` |

წაკითხვა:

- **`G0`** — სამივე route თანხმდება იმდენად, რამდენადაც შეიძლება: series არის *ის* truncation,
  composition არის wave სუფთა `2*pi/|a|` period-ით, და რვავე identity ძალაშია.
- **`G16`** — series აქაც degree `5`-ია და აქაც odd-ია, ანუ "sine-ის ფორმის" polynomial, მაგრამ
  coefficient-ები სხვაა (`x/6` და არა `x`), ამიტომ near zone-ში ის `G0`-ზე
  დაახლოებით სამასჯერ ცუდია (`1.3045` ვიდრე `0.0045`).
  identity-ებით კი `G16` თითქმის `G0`-ია: `7/8`.
- **`G20`** — series degree `7`-ია და odd-ია, ანუ *უფრო მაღალი* რიგის approximation-ს ჰგავს,
  სინამდვილეში კი ის ყველაზე ცუდი far-zone reading-ია მთელ atlas-ში (`x = 10`-ზე error `97212`).
  composition ჯანსაღი wave-ია. identity-ებით `4/8`.
- **`G01`** — series `0`-ია, composition constant `sin(1)`-ია, identity-ებიდან მხოლოდ ის ორი
  რჩება, რომელიც არავითარ world-ში ვერ იშლება. ამ world-ში sine, სამივე route-ის მიხედვით,
  **არ არსებობს** როგორც ცნობადი ობიექტი.

## ინტერპრეტაცია

სამი route ჩვენს world-ში ერთსა და იმავე sine-ს აღწერს. სხვაგან ისინი ერთმანეთს არ ეთანხმებიან,
და divergence-ის ფორმა თანმიმდევრულია:

```text
route 2 (composition)  -- ყველაზე მდგრადი: 125 წყვილიდან 116 ინარჩუნებს ცოცხალ argument-ს
route 3 (identities)   -- ნაწილობრივ მდგრადი: 8-დან 2 identity არსად არ იშლება
route 1 (series)       -- ყველაზე მყიფე: 25 world-იდან 9 string-ს ნულს უკითხავს
```

მიზეზი სტრუქტურულია. route 2-ში მხოლოდ **argument** მოძრაობს, ხოლო `sin` ნამდვილი `sin` რჩება;
ამიტომ ის თითქმის ყოველთვის რაღაც ტრიგონომეტრიულს იძლევა. route 3-ში მოძრაობს **association**,
ამიტომ იმ identity-ებს, რომლებიც ერთ operator kind-ს იყენებენ, არაფერი ემართებათ, დანარჩენებს კი —
ემართებათ. route 1-ში მოძრაობს **მთელი expression**, და რადგან series ერთსა და იმავე ცვლადს ბევრჯერ
იმეორებს `+`, `-`, `*`, `/`-ის შერევით, ის ყველაზე მეტ ადგილს აძლევს convention-ს ჩარევისთვის.

ამიტომაც არის route 3 ამ დომენში founding question-ის ყველაზე მკვეთრი ფორმა. ის აჩვენებს, რომ
`sin**2 + cos**2 = 1`-ის "თვითცხადობა" ნაწილობრივ **notation-ის თვისებაა და არა მხოლოდ
გეომეტრიისა**: იმ `12` world-ში, სადაც `+` `*`-ზე მაგარია, იგივე გამონათქვამი wave-ს ნიშნავს, და
Pythagorean identity, რომ დაწერილიყო, ფრჩხილებს მოითხოვდა — ანუ ის იქ **უფრო ძვირი** იქნებოდა.
ROADMAP-ის direction B-ის ტერმინებში: ის იქ არ იქნებოდა parenthesis-free default.

მეორე დაკვირვება იმავე ხაზზე: `G0`-ის უპირატესობა identity-ებზე **tie-დან მოდის და არა
order-იდან**. `G17`-ს `G0`-ის ზუსტი რიგი აქვს და `7/8` აქვს; `G23`/`G24`-ს სხვა რიგი აქვთ და
`8/8` აქვთ. ე.ი. ის, რაც `1 + tan**2 = sec**2`-ს იცავს, არის `*` და `/`-ის ერთ level-ზე დგომა
(ან `/`-ის `*`-ზე მაგრობა), და არა ის, რომ `*` პირველია. ეს პირდაპირ ეხმიანება 0030-ის
associativity axis-ს: convention-ის space precedence order-ით არ ამოიწურება.

მესამე — და ეს ტექნიკური dividend-ია და არა მათემატიკური: ამ ექსპერიმენტმა იპოვა defect-ის
კლასი, რომელიც NF-2026-00004-ის ტოლფასია, ოღონდ printer-ის მხრიდან. SymPy-ის `Union` და
`FiniteSet` წევრებს hash order-ით ინახავენ, Python კი string hash-ს process-ზე randomize-ს
აკეთებს; შედეგად `str(continuous_domain(...))` **სხვადასხვა string-ია parent process-ში და pool
worker-ში**. ამ string-ზე აგებული semantic key value-ს კი არა, process-ს იქნებოდა function.
Defect ჩნდებოდა ზუსტად მაშინ, როცა sweep parallel-ად გაეშვებოდა: `1 + s/c*s/c`-ის `5` class
`6`-ად იშლებოდა. Fix — `_set_text`, რომელიც commutative set constructor-ის წევრებს მათივე
rendered text-ით ალაგებს. `sympy.core.sorting.default_sort_key` **არ** ჭრის ამ პრობლემას: ის
tangent domain-ის `ImageSet` წევრებზე ტოლ key-ებს აბრუნებს, ამიტომ `sorted` მხოლოდ იმ hash
order-ს ინახავს, რომელიც მიიღო.

## Multicore

გადაწყვეტილება **გაზომილია** და არა დაშვებული. დაკვირვებული core count: `16`; worker count =
`min(cores - 2, 12, cells)` = `12`, ანუ headroom რჩება interactive session-ისთვის.

გაზომილი pool startup (spawn-start, ყოველი worker sympy-ს import-ს აკეთებს): `3.06 s` `8`
worker-ზე, `3.49 s` `12` worker-ზე თბილ filesystem cache-ზე, `~15 s` პირველ, ცივ pool-ზე.
აქედან `POOL_STARTUP_SECONDS = 4.0`.

| atlas | cells | sec/cell | sequential | pooled | decision |
|---|---:|---:|---:|---:|---|
| series | `25` | `0.14` | `3.45 s` | `9.04 s` | **sequential** |
| identity | `200` | `0.097` | `19.37 s` | `6.21 s` | **parallel** |
| outer, phase A (per world) | `375` | `0.065` | `24.20 s` | — | **parallel** |
| outer, phase B (per composition) | `117` | `0.07` | `~8 s` | — | **parallel** |
| outer, end-to-end | | | `~45 s` | `11.41 s` | **parallel** |

ორი დასკვნა, ორივე გაზომვიდან:

- **series atlas sequential-ად რჩება.** მას identity atlas-ზე მხოლოდ რვაჯერ ნაკლები cell აქვს და
  თითქმის იმავე ღირებულების cell-ები, მაგრამ `25 * 0.14 = 3.5 s` სამუშაო pool-ის აშენებას ვერ
  ანაზღაურებს. cell count მარტო ამას ვერ გადაწყვეტს; `should_parallelise` სწორედ ამიტომ
  ღირებულებას ადარებს და არა რაოდენობას.
- **outer route-ს cell granularity შეეცვალა გაზომვის შემდეგ.** თავდაპირველი `(source, function)`
  დაყოფა `15` cell-ს იძლეოდა, რომელთაგან ერთს (`1 - 2*t/4 + 3*t` × `tan`) `19.06 s` სჭირდებოდა და
  მთელ sweep-ს აჩერებდა — parallel path `59.98 s`-ში მთავრდებოდა, sequential-ზე **ნელა**.
  `(source, function, world)` დაყოფით cell-ები `375`-ია, ყველაზე ნელი `2.35 s`, და end-to-end
  დრო `11.41 s`. სრული report (სამივე route) `24.2 s`-ში სრულდება.

Parallelism არაფერს ცვლის იმაში, თუ *რა* იზომება: სამივე atlas-ზე sequential და parallel record-ები
სრულად ემთხვევა და ეს test-ითაა დაფიქსირებული და არა ნავარაუდევი.

## შეზღუდვები

- **truncated series არსად არის sine — `G0`-ის ჩათვლით.** `x - x*x*x/6 + x*x*x*x*x/120` არის
  polynomial ყოველ world-ში: არც periodic, და არაკონსტანტურებში არც bounded, `x -> ±oo`-ზე გაქცეული. ამ report-ის
  არც ერთი მწკრივი არ ამბობს, რომ რომელიმე world "უკეთესად კითხულობს sine-ს"; ისინი სხვადასხვა
  polynomial-ს კითხულობენ და მათი error იზომება იმავე გამოცხადებულ ცხრა point-ზე.
- **route 3 placeholder-ს იყენებს და არა ნამდვილ function call-ს.** Generation 1 language-ს
  function-call syntax არ აქვს. ეს მოდელი პასუხობს კითხვას "დაიწერებოდა თუ არა ეს identity ასევე",
  და **არ** პასუხობს კითხვას "როგორი იქნებოდა ტრიგონომეტრიული semantics". კერძოდ, ის არ ეხება
  არც angle-ის განსაზღვრებას, არც radian-ის არჩევანს, არც series-ისა და circle-ის კავშირს.
- **ეს არის მოდელი და არა მტკიცებულება.** გაზომილია, თუ რას denote-ს აკეთებს **დღევანდელი
  სტანდარტული written form** სხვა convention-ში. ეს არ არის იმის მტკიცება, რომ იმ convention-ში
  ტრიგონომეტრია სწორედ ასე აშენდებოდა — სხვა notation-ში ადამიანები სხვა string-ებს დაწერდნენ.
  ეს არის *how it would have been built*-ის მოდელი და არა proof.
- corpus მცირეა: `1` series string, `5` inner source, `8` identity. სამივე რიცხვი ამ report-ის
  შედეგებზე პირდაპირ მოქმედებს; მაგალითად `pythagorean_tangent` ერთადერთი identity-ია corpus-ში,
  რომელიც `*`-სა და `/`-ს ერთ chain-ში ურევს, ამიტომ `G0` vs `G17` განსხვავება მას **ერთ**
  observation-ზე ეყრდნობა.
- sample point-ები ცხრაა და `error` მათზეა max-ით აღებული. ეს არ არის norm და არ არის
  approximation quality-ის ზოგადი საზომი.
- `undefined_terms` denominator-ს კომპლექსურ სიბრტყეზე ხსნის, ამიტომ excluded-point set-ები
  კომპლექსურ წერტილებსაც შეიცავს (`S07`, `S10`, `S11`). oddness-ის domain symmetry მხოლოდ real
  წევრებზეა შემოწმებული, რადგან მხოლოდ ისინი ზღუდავენ real function-ის domain-ს.
- route 3-ის excluded point `0` ნიშნავს "პირველი denominator variable ნულია" (`c = 0` ან
  `c*s = 0`) — ეს `parseatlas.canonical.undefined_terms`-ის საკუთარი convention-ია და აქ უცვლელად
  გადმოვიდა.

## Evidence-ის კლასიფიკაცია

- ყველა count, class, canonical form, root, period, domain, error და survival flag — **observed**,
  executable output-იდან. არც ერთი მათგანი grammar-ის მოსალოდნელი ქცევიდან არ არის გამოყვანილი.
- `sin`/`cos`-ის `2*pi/|a|` და `tan`-ის `pi/|a|` affine argument-ზე — **symbolically justified**,
  და ამ ექსპერიმენტში დამოუკიდებლად გადამოწმებული `sympy.calculus.util.periodicity`-ით
  (`375` reading, `0` disagreement).
- "`*`-first ექვსივე world ინახავს `7/8`-ს" და "`/ >= *` სამივე world ინახავს `8/8`-ს" —
  **observed structure** ამ რვა identity-ზე. ეს არ არის ზოგადი თეორემა identity-ების ყველა
  კლასზე; corpus-ის გაფართოებამდე ის ასე არ უნდა წაიკითხოს.
- set-printing defect და მისი fix — **measured**: ერთი და იმავე rendering-ის რვა დამოუკიდებელ
  interpreter-ში გაშვება, plus sequential/parallel record equality regression test.
- multicore-ის ყველა დროითი მაჩვენებელი — **measured** ამ machine-ზე (`16` core, CPython `3.14`,
  SymPy `1.14`). ისინი machine-specific-ია და გადაწყვეტილების წესის input-ია, არა მისი შედეგი.
- ამ ექსპერიმენტიდან ზოგადი დასკვნა "convention X უკეთესია მათემატიკისთვის" **არ გამოგვაქვს**.
  direction B-ის cost-ის კითხვას ეს report არ პასუხობს; ის direction A-ს ეკუთვნის.

## ვალიდაცია

```text
16 passed  # tests/test_trigonometry_worlds.py
21 passed  # + tests/test_outer_functions.py (0002-ის pinned შედეგები უცვლელია)
629 passed  # სრული suite (613 + 16), 426 s
```

Mutation testing (ხის იზოლირებულ ასლზე, `8` semantic mutant `trigonometry_worlds.py`-ზე):
**`8/8` killed**. მოკლულია — periodicity-ის constant sentinel-ის მიღება ნამდვილ period-ად;
oddness-ის domain-symmetry მოთხოვნის მოხსნა; semantic key-დან excluded-points slot-ის ამოგდება;
`_set_text`-ის ჩანაცვლება SymPy-ის hash-ordered `str()`-ით; identity verdict-ის ყოველთვის
`True`-დ დაბრუნება; parallel decision-ის ჩანაცვლება cell-count threshold-ით; constant collapse-ის
დაფარვა; truncation error-ის ნულად დაბრუნება.

პირველ გაშვებაზე `set rendering` mutant **გადარჩა**: determinism test იმ დროს ერთ process-ში
ორ `Union` construction-ს ადარებდა, ხოლო `Union` argument-ებს კონსტრუქციისას ისედაც
canonicalize-ს აკეთებს, ამიტომ ორივე ერთსა და იმავე object-ს იძლეოდა და შედარება vacuous იყო.
Test გადაკეთდა ისე, რომ rendering-ს სამ ცალკე interpreter-ში, ფიქსირებული და განსხვავებული
`PYTHONHASHSEED`-ით აშენებს და ადარებს — რის შემდეგაც mutant მოკვდა.

`tests/test_outer_functions.py::test_sine_reports_constant_collapse_and_period` (`tan` period
`2*pi` `G03`-ზე, `sin` period `4*pi`, constant collapse `G01`-ზე) ხელუხლებელია და დამატებით
ხელახლა გაიზომა ამ ექსპერიმენტის pipeline-იდან.

Reproduction:

```text
python -c "import json; from parseatlas.trigonometry_worlds import trigonometry_report; print(json.dumps(trigonometry_report()['answers'], indent=1))"
```
