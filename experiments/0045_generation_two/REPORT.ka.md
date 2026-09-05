# ParseAtlas ექსპერიმენტი 0045: გადარჩება თუ არა flagship შედეგი exponentiation-ის ქვეშ?

## მიზანი

**არა, არ გადარჩება.** როგორც კი ენა power-ის ჩაწერას შეძლებს, `a * x^2 + b * x + c` `121`
Generation 2 grammar-ზე `2`-ის ნაცვლად `6` განსხვავებულ object-ს აღნიშნავს, conventional quadratic
`13` of `25`-ის ნაცვლად `21` world-ში დგას, და object, რომლითაც ეს repository ყველაზე მეტად არის
ცნობილი — radical-ის გარეშე cubic `a*x*(b + x)*(c + x)`, roots `0`, `-b`, `-c` — **არცერთ იმ
world-ში აღარ არსებობს, რომელიც კვადრატს `x^2`-ად წერს**.

ეს scope მთელი საქმეა, და ამ წინადადების ადრინდელმა რედაქციამ ის დაკარგა, აცხადებდა რა, რომ cubic
საერთოდ არცერთ Generation 2 world-ში არ არსებობს. **ეს მცდარი იყო და review-მ დაიჭირა.**
Generation 1-ის string `a * x * x + b * x + c` კვლავ ლეგალური Generation 2 string-ია, და `121`
world-იდან `60` მას ზუსტად იმ cubic-ად კითხულობს, radical-ის გარეშე, იმ roots-ით. ქრება არა
object, არამედ **object-ის მიღწევადობა იმ ჩაწერიდან, რომელსაც `^`-ის მქონე world აირჩევდა**.

ექსპერიმენტ 0035-ის `13`/`12` split ზუსტია, რეპროდუცირებადია და აქ ხელახლა არის გამოყვანილი. ის,
რასაც ეს ექსპერიმენტი უმატებს, მისი scope-ია: ეს არის მტკიცება string-ზე `a * x * x + b * x + c`,
და ეს string იმ ენის artefact-ია, რომელსაც exponentiation არ აქვს. იგივე string Generation 2
registry-ში `61`/`60`-ად იყოფა — იგივე ორი object, იგივე ორი block, უბრალოდ უფრო დიდი registry —
ამიტომ თვით რიცხვები `13` და `12` registry-ის ზომებია და არა ფაქტები მათემატიკაზე. შეცვალეთ string
იმით, რასაც `^`-ის მქონე world ნამდვილად დაწერდა, და მეორე object აღარ არის.

ცხრა გამოქვეყნებული მტკიცება ხუთ object-ზე იმავე დამუშავებაზე გატარდა. ცხრავე სტრიქონში ზუსტად
ერთი object გადარჩება ხელახლა ჩაწერას და ყოველთვის ერთი და იგივე: **ის object, რომელსაც
conventional world კითხულობს**.

**ეს მტკიცებაა იმ ცხრა სტრიქონზე და არა ორ ექსპერიმენტზე.** Review-მ შეამოწმა ის მტკიცებები,
რომლებსაც ცხრილი გამოტოვებს, და სამი სხვაგვარად იქცევა: შეკვეცილი sine series ინახავს `7` object-ს
ორ generation-ს შორის, მათგან ექვსი არა-conventional ალტერნატივაა, რომელიც გადარჩება; cosine series
ინახავს `5`-ს, ოთხი ალტერნატივით; exponential series — `2`-ს, ერთით. ადრინდელი რედაქცია ცხრა
სტრიქონს განაზოგადებდა როგორც „0035-ისა და 0036-ის ყველა ალტერნატიული object ჩანაცვლებულია", რასაც
ეს სამი აბათილებს.

## ენა

Generation 2 არის Generation 1 პლუს ზუსტად ერთი binary operator, `^`. Thesis T26 — juxtaposition და
unary minus — მკაფიოდ scope-ის გარეთაა, ამიტომ `2x` და `-x` კვლავ ჩაუწერელია.

ხუთი operator იძლევა `5! = 120` მკაცრ precedence ordering-ს. Registry ამატებს conventional
tied-level control-ს `H0` — `^` ყველაზე მჭიდრო, შემდეგ `*` `/` ტოლ დონეზე, შემდეგ `+` `-` ტოლ
დონეზე — სულ **`121`** grammar, ზუსტად ისე, როგორც Generation 1 არის `4! = 24` მკაცრი ordering
პლუს ერთი control, სულ `25`. მკაცრი grammar-ები `H001`-დან `H120`-მდე იწოდება, რომ არცერთი
identifier არ აგვერიოს Generation 1-ის `G` identifier-ში.

`^` **right-associative-ია**, და ეს დეტალი არ არის: `2^3^2` არის `2^9 = 512` და არა `(2^3)^2 = 64`.
ამ პროექტის ყველა სხვა operator left-associative-ია, ამიტომ Generation 2 აქ პირველი grammar
family-ია, რომლის associativity ერთგვაროვანი არ არის. ასიმეტრია parser-ის ერთი წევრია — მარჯვენა
operand იკითხება `power(op) + 1`-ზე left-associative operator-ისთვის და `power(op)`-ზე
right-associative-ისთვის — და მთელი bracket წესი აქედან გამომდინარეობს, თანაც ორი ნახევარი
სიმეტრიული არ არის: მარცხენა child-ის ზღვარი **child-ის** associativity-ზეა დამოკიდებული, მარჯვენა
child-ისა კი **parent-ის** associativity-ზე. სწორედ ამიტომ `a^b^c`-ს არცერთ `121` grammar-ში
bracket არ სჭირდება, `(a^b)^c`-ს კი ყველგან სჭირდება.

**რა შეიძლება იდგეს exponent-ში.** არაფერია შეზღუდული: `^` იმავე ენის ჩვეულებრივი binary
operator-ია, ამიტომ exponent არის ის expression, რასაც grammar იქ მოათავსებს, და სწორედ ამიტომ
ჩნდება reading-ები, როგორიცაა `(a*x)**(b*x + c + 2)`. არ არსებობს ცალკე exponent syntax, არც unary
minus, არც implicit multiplication და არც function application, ხოლო გამოტოვების გარეშე ჩაწერილი
`1/2` ერთი rational literal-ია და არა division — ოთხივე Generation 1-ის ზღვარია, უცვლელად
მემკვიდრეობით მიღებული.

## Conservative extension, პირველ რიგში

საერთო parser ხელუხლებელია. Generation 2-ს საკუთარი tokenizer და parser აქვს
`src/parseatlas/generation_two.py`-ში, და სწორედ აქედან ჩნდება ვალდებულება, რომელსაც ეს ექსპერიმენტი
ყველაფერზე ადრე ხურავს: `+ - * /`-ზე შეზღუდული Generation 2 ზუსტად იმას parse-ავს, რასაც
Generation 1?

```text
sources                     94    0034's cost corpus + 0035's catalogue + 10 hand-written strings
Generation 1 grammars       25
embeddings of ^            123    24 strict x 5 positions + the tied control x 3 positions
cells                    11562
disagreements                0
```

თითოეული cell ადარებს tree-ებს და არა string-ებს: Generation 2-ის parser Generation 1-ის საკუთარ
`Binary`/`Number`/`Variable` node-ებს აშენებს, ამიტომ cell dataclass-ის ტოლობაა. `^` **ყოველ**
პოზიციაზეა ჩასმული ყოველ grammar-ში და არა მხოლოდ ზემოთ, რადგან "`^` შემთხვევით ყველაზე მჭიდროდ
იკვრება" გაცილებით სუსტი მტკიცება იქნებოდა, ვიდრე ის, რაც ამ report-ის დანარჩენ ნაწილს სჭირდება.

ორივე guarantee, რომელსაც Generation 1 მოითხოვს, იმავე წესით არის შემოწმებული მთელ `38 x 121`
grid-ზე:

```text
round trip     4598 checks     0 failures      parse2(render2(t, g), g) == t
minimality     5665 brackets   0 violations    every pair deleted in turn and reparsed
```

Minimality არის ამომწურავი ძებნა ჩანაწერებზე და არა არგუმენტი renderer-ის შესახებ: თითოეული
bracket წყვილი იშლება და შედეგი სხვა tree-ად უნდა წაიკითხოს ან საერთოდ არ უნდა დაიparse-ოს.

## Corpus

`38` სახელდებული ფორმულა, რომლებიც ნამდვილად იყენებენ power-ს, `6` სფეროში — algebra `13`, geometry
`6`, physics `6`, calculus `5`, statistics `5`, finance `3`. თითოეული ჩაწერილია Generation 2-ის
ჩანაწერით და, სადაც object საერთოდ იწერება `^`-ის გარეშე, Generation 1-ის ჩანაწერითაც: `26`
entry-ს ორივე აქვს, ხოლო `12` მხოლოდ Generation 2-ისაა, რადგან მათ სჭირდებათ symbolic exponent
(`x^n`) ან არაცვლადი base (`2^k`). ყოველი source მინიმალური ჩანაწერია საკუთარი control grammar-ის
ქვეშ, და სწორედ ეს აქცევს გამოქვეყნებულ სიას audit trail-ად და არა დეკორაციად.

## დაკვირვებული შედეგები

### 1. Headline: quadratic `121` world-ში

ერთი და იმავე მათემატიკის სამი წაკითხვა, რადგან ორი სხვადასხვა ეფექტი მოქმედებს და თითოეული
ცალკე შედეგს არასწორად წარმოადგენდა.

| ჩაწერილი ფორმა | registry | support | T6 block-ები | distinct object-ები | group-ების ზომები |
|---|---|---|---|---|---|
| `a * x * x + b * x + c` | `25` Generation 1 world | `* +` | `2` | `2` | `13`, `12` |
| `a * x * x + b * x + c` | `121` Generation 2 world | `* +` | `2` | `2` | `61`, `60` |
| `a * x^2 + b * x + c` | `121` Generation 2 world | `* + ^` | `6` | `6` | `21`, `20`, `20`, `20`, `20`, `20` |

შუა სტრიქონი მთელი registry ეფექტია: იგივე string, იგივე ორი object, იგივე ორი block, და მხოლოდ
block-ების ზომები იცვლება. **`13` და `12` არის support `{*, +}`-ის ორი T6 block-ის ზომები
`25`-grammar-იან registry-ში**, და მეტი არაფერი.

ქვედა სტრიქონი ენის ეფექტია და სწორედ მასზე დგას პასუხი.

| object | world-ები | precedence, support-ზე შეზღუდული | აღნიშნავს | degree | roots `C`-ზე | radical |
|---|---|---|---|---|---|---|
| `O01` | `21` | `^ > * > +` | `a*x**2 + b*x + c` | `2` | `(-b +- sqrt(-4*a*c + b**2))/(2*a)` | დიახ |
| `O02` | `20` | `+ > * > ^` | `(a*x)**((b + 2)*(c + x))` | — | not attempted | — |
| `O03` | `20` | `* > + > ^` | `(a*x)**(b*x + c + 2)` | — | not attempted | — |
| `O04` | `20` | `^ > + > *` | `a*(b + x**2)*(c + x)` | `3` | `-c`, `-sqrt(-b)`, `sqrt(-b)` | დიახ |
| `O05` | `20` | `* > ^ > +` | `a**2*x**2 + b*x + c` | `2` | `(-b +- sqrt(-4*a**2*c + b**2))/(2*a**2)` | დიახ |
| `O06` | `20` | `+ > ^ > *` | `a*x**(b + 2)*(c + x)` | — | not attempted | — |

Control `H0` `O01`-ში დგას, რომლის `21` world არის `20` მკაცრი ordering `^ > * > +`-ით პლუს თვითონ
control.

ექვსი reading-იდან სამი polynomial-ია `x`-ში და **სამივეს radical სჭირდება**. დანარჩენი სამი არც
polynomial-ია და არც rational function `x`-ში — ცვლადი exponent-შია — და მათი root list-ები
*not attempted*-ად არის ნაჩვენები მიზეზთან ერთად და არა ცარიელ სიად, რადგან ცარიელი სია "roots არ
არის"-ად წაიკითხებოდა, ეს კი სხვა მტკიცებაა. ეს სამი `121` world-იდან `60`-ს ფარავს.

ასე რომ, 0035-ის headline-ის ორი ნახევარი სხვადასხვანაირად ვარდება. **რაოდენობა** იცვლება, `2`-დან
`6`-მდე. **Object** ქრება: `a*x*(b + x)*(c + x)` ექვს canonical form-ს შორის არ არის. და
**შედეგი, რომელსაც ციტირებენ** — რომ worlds-ის დაახლოებით ნახევარში standard quadratic-ის
ამოსახსნელად radical არ არის საჭირო — `25` world-იდან `12`-ის ნაცვლად `121` world-იდან `0`-ზე გადადის.

### 2. Survival table

დანარჩენი object-ები, რომლებზეც 0035-მა და 0036-მა მტკიცებები გააკეთეს, ისე ჩაწერილი, როგორც
Generation 2 დაწერდა. თითოეული გამოქვეყნებული claim ციტირებულია, ხელახლა არის დაკვირვებული ორივე
generation-ში და verdict-ს იღებს დეკლარირებული წესით: Generation 2-ში მცდარი claim **does not
survive**; ჭეშმარიტი, მაგრამ სხვა world რაოდენობით — **survives with different numbers**;
ჭეშმარიტი იმავე რაოდენობით — **survives**.

| claim | object | Generation 1 -> Generation 2 object-ები | claim-ის საკუთარი რიცხვი | verdict |
|---|---|---|---|---|
| `0035_quadratic_object_count` | quadratic | `2` -> `6` | `2` -> `6` object | does not survive |
| `0035_quadratic_radical_free_cubic` | quadratic | `2` -> `6` | `12` -> `0` world | does not survive |
| `0035_quadratic_radical_free_worlds` | quadratic | `2` -> `6` | `12` -> `0` world | does not survive |
| `0035_binomial_square_object_count` | binomial square | `2` -> `5` | `2` -> `5` object | does not survive |
| `0035_binomial_square_present` | binomial square | `2` -> `5` | `13` -> `41` world | survives with different numbers |
| `0035_difference_of_squares_object_count` | difference of squares | `2` -> `2` | `2` -> `2` object | survives |
| `0035_circle_object_count` | circle | `4` -> `4` | `4` -> `4` object | survives |
| `0035_circle_present` | circle | `4` -> `4` | `9` -> `41` world | survives with different numbers |
| `0036_pythagorean_identity` | Pythagorean identity | `2` -> `2` | `13` -> `61` world | survives with different numbers |

**Claim-ები, რომლებიც არ გადარჩება, სახელებით:** `0035_quadratic_object_count`,
`0035_quadratic_radical_free_cubic`, `0035_quadratic_radical_free_worlds`,
`0035_binomial_square_object_count`.

ის, რასაც object-ების რაოდენობა მალავს, თვით reading-ებშია.

| object | Generation 1-ის ჩანაწერი და object-ები | Generation 2-ის ჩანაწერი და object-ები |
|---|---|---|
| difference of squares | `a * a - b * b`: `a**2 - b**2` (`13`), `a*b*(a - b)` (`12`) | `a^2 - b^2`: `a**2 - b**2` (`61`), `a**((b - 2)**2)` (`60`) |
| Pythagorean identity | `s * s + c * c`: `c**2 + s**2` (`13`), `c*s*(c + s)` (`12`) | `s^2 + c^2`: `c**2 + s**2` (`61`), `s**((c + 2)**2)` (`60`) |
| circle | `x * x + y * y - r * r`: `4` object, `9`/`8`/`4`/`4` | `x^2 + y^2 - r^2`: `4` object, `41`/`40`/`20`/`20` |
| binomial square | `a * a + 2 * a * b + b * b`: `2` object, `13`/`12` | `a^2 + 2 * a * b + b^2`: `5` object, `41`/`20`/`20`/`20`/`20` |

Circle ამ ცხრილის ყველაზე მკვეთრი შემთხვევაა. მისი **ფორმა** სრულად გადარჩება: ოთხი object ორივე
generation-ში, იმავე სტრუქტურის block-ებით, და conventional reading ყველაზე დიდ group-ს იკავებს.
მისი **object-ები** კი არა: იქ, სადაც Generation 1 quartic-სა და ორ შერეულ curve-ს იძლეოდა,
Generation 2 power tower-ებს იძლევა, როგორიცაა `x**((y + 2)**((r - 2)**2))`. რაოდენობის გადარჩენა
იგივე არ არის, რაც claim-ის გადარჩენა, ამიტომ object-ების სიმრავლის ტოლობა ცალკე მოწმდება და
არასოდეს გამოიყვანება რაოდენობიდან. **`9`-ვე სტრიქონში ორი generation ზუსტად ერთ object-ს იზიარებს
და `9`-ვეში ეს ის object-ია, რომელსაც conventional world კითხულობს.**

Binomial square ერთადერთი object-ია, რომელიც block-ებზე ნაკლებ object-ს იძენს: `6` block `5`
object-ს იძლევა, რადგან `^ > * > +` და `* > ^ > +` `a^2 + 2 * a * b + b^2`-ს იდენტურად წერენ —
`*` chain და ორი power ერთმანეთს არასოდეს ხვდებიან.

### 3. Cost და სად დგას conventional convention

`38`-ფორმულიანი corpus ყველა `121` grammar-ის ქვეშ, სადაც ერთი bracket წყვილი ერთი ერთეულია:

```text
cheapest    H001  ^ * / + -     24 brackets
CONTROL     H0    ^ *=/ +=-     25 brackets     rank 2 of 121, top 1.65 percent
dearest     H120  - + / * ^     70 brackets
spread                          46 brackets
```

ზუსტად ერთი grammar-ია conventional-ზე იაფი, არცერთი არ არის მასთან ტოლი, და მისი უპირატესობა ერთი
bracket-ია ერთ ფორმულაზე:

```text
H0     (x - m)^2 / (2 * s^2)      2 brackets
H001   (x - m)^2 / 2 * s^2        1 bracket
```

`H001` არ არის convention-ის გადაჯგუფება — ეს არის იგივე convention, ოღონდ tie-ები გახსნილი, `*`
`/`-ზე ზემოთ და `+` `-`-ზე ზემოთ. ერთი დაზოგილი bracket მხოლოდ `*` `/` tie-ს ეკუთვნის. ეს ზუსტად
იმ Generation 1 შედეგის ფორმაა, რომელიც roadmap-შია ჩაწერილი, სადაც ოთხ სფეროზე `G0`-ს ორი
grammar ჯობნიდა, და მათგან იაფი — `G18` — ჩვენივე დაჯგუფებაა `+`/`-` tie-ს გახსნით.

რადგან `2` of `121` და `3` of `25` ordinal-ებად არ ედრება ერთმანეთს, ყოველი rank percentile-ითაც
არის მოცემული, `100 * rank / registry size`, და ერთი და იგივე მათემატიკა ორივე ენაზეა შეფასებული.
`38` entry-დან `26` `^`-ის გარეშეც იწერება; სწორედ ეს `26` object ორივე registry-ში შეფასდა:

| ranking | corpus | registry | control-ის ჯამი | control-ის rank | percentile |
|---|---|---|---|---|---|
| Generation 2, მთელი corpus | `38` | `121` | `25` | `2` | `1.65` |
| Generation 2, მხოლოდ movable entry-ები | `34` | `121` | `23` | `2` | `1.65` |
| Generation 2, საერთო object-ები | `26` | `121` | `14` | `2` | `1.65` |
| Generation 1, იგივე საერთო object-ები | `26` | `25` | `26` | `6` | `24.0` |

ამ ცხრილის ორი წაკითხვაა და მხოლოდ ერთია უსაფრთხო. უსაფრთხო: ამ `26` object-ის ჩაწერა conventional
convention-ს Generation 1-ში `26` bracket-ად უჯდება და Generation 2-ში `14`-ად, `12`-ით ნაკლები,
`46.15` პროცენტის დაზოგვა, რადგან bracket-ში ჩასმული მამრავლი, რომელიც უნდა გამეორდეს —
`(x2 - x1) * (x2 - x1)` — power-ის არსებობისას ერთხელ იწერება. არაუსაფრთხო წაკითხვა იქნებოდა ორი
rank-ის ერთმანეთთან შედარება იმის მტკიცებულებად, რომ convention გაუმჯობესდა; registry-ები ზომით
განსხვავდება, ჩანაწერები განსხვავდება, და percentile სწორედ იმისთვისაა მოცემული, რომ ordinal
შედარება საჭირო არ გახდეს. 0037-ის `3` of `25` საკუთარ `33`-კანონიან corpus-ზე კიდევ მესამე
population-ია და აქ მხოლოდ კონტექსტისთვისაა მოყვანილი.

**T25-ის საკუთარი კითხვა, პირდაპირ დასმული.** Thesis კითხულობს, ინარჩუნებს თუ არა conventional
grammar თავის ადგილს მაშინ, როცა `^` `*`-ზე მჭიდროდ იკვრება და მაშინ, როცა უფრო თავისუფლად. `^`-ის
`5` შესაძლო პოზიციიდან თითოეული ზუსტად `24` მკაცრ ordering-ს იკავებს `120`-იდან, ამიტომ ხუთი
საშუალო პირდაპირ შედარებადია:

```text
^ at position 1 (tightest)   mean 34.0 brackets    min 24   max 44
^ at position 2              mean 40.5             min 26   max 48
^ at position 3              mean 47.0             min 33   max 61
^ at position 4              mean 53.5             min 46   max 68
^ at position 5 (loosest)    mean 60.0             min 50   max 70
```

საშუალო ყოველ პოზიციაზე ზუსტად `6.5` bracket-ით იზრდება, ოთხჯერ ზედიზედ, ხოლო იგივე ცხრილი `26`
საერთო object-ზე ზუსტად `6.25`-ით იზრდება ოთხჯერ. ყველაზე მჭიდროდან ყველაზე თავისუფლამდე სხვაობა
`26` bracket-ია. ე.ი. ამ corpus-ზე `^`-ის პოზიცია cost-ში ადიციურ წევრად იქცევა, და მისი ყველაზე
მჭიდროდ დაკვრა — ის, რასაც მათემატიკა ნამდვილად აკეთებს — ხუთი არჩევანიდან ყველაზე იაფია.

### 4. Null model, რომელიც ხუთ operator-თან უფრო მკაცრად კბენს

T6 ამბობს, რომ parse დამოკიდებულია მხოლოდ იმ precedence-ზე, რომელიც რეალურად წარმოდგენილ
operator-ებზეა შეზღუდული. ხუთ operator-თან ფასდაკლება დიდია: entry, რომლის support-ს `k` operator
აქვს, `120` მკაცრ ordering-ს `k!` block-ად ყოფს `120 / k!` ზომით და block-ის შიგნით კონსტრუქციით
ბრმაა.

```text
support size   entries   blocks it can separate   strict grammars per block
1                    3                        1                        120
2                   10                        2                         60
3                   17                        6                         20
4                    5                       24                          5
5                    3                      120                          1
```

**`38` entry-დან მხოლოდ `3` თუ არჩევს საერთოდ ყველა `120` ordering-ს** — `taylor_second_order`,
`projectile_height` და `annuity_future_value`, ის სამი, რომელიც ყველა operator-ს იყენებს.
დანარჩენ `35`-ს ეს არ შეუძლია, რასთანაც არ უნდა შევადაროთ. და სრული support საჭიროა, მაგრამ
საკმარისი არ არის: სამიდან საუკეთესო `120`-ზე მხოლოდ `36` განსხვავებულ string-ს წერს, დანარჩენი
ორი `28`-ს და `16`-ს. ამ corpus-ში არცერთი entry `36` grammar-ზე მეტს არ არჩევს.

ოთხი entry — `power_of_power_rule`, `iterated_power`, `binary_place_value`, `exponential_growth` —
ყველა `121` grammar-ის ქვეშ ერთსა და იმავე cost-ს იძლევა. ისინი ყოველ ჯამს ერთსა და იმავე
კონსტანტას უმატებენ და ვერცერთ ranking-ს ვერ ძრავენ, ამიტომ ranking მათ გარეშე ხელახლა ითვლება;
control rank `2`-ს ინარჩუნებს და `121`-ის რიგი უცვლელია, რაც ზემოთ მოცემული ranking ცხრილის მეორე
სტრიქონია.

Corpus მთლიანობაში სხვა საქმეა, ვიდრე მასში შემავალი ნებისმიერი entry. `38` cost ვექტორი `121`
განსხვავებულ profile-ს იძლევა და `38` rendering ვექტორი `121` განსხვავებულ profile-ს, ამიტომ
corpus registry-ის ყოველ grammar-ს არჩევს — თანაც სულ `40` განსხვავებულ ჯამამდე იკუმშება, რის გამოც
rank-ები ზედა ნაწილში ასე ხშირად ემთხვევა.

### 5. ყველაზე fractured object

Generation 2-ის შეკვეცილი sine series `x - x^3 / 6 + x^5 / 120` `121` world-ზე `17` განსხვავებულ
object-ს აღნიშნავს, `16` განსხვავებული canonical text-ის პირისპირ. სხვაობა semantic key-ის მუშაობაა:
ორი group ორივე `0`-ს კითხულობს, ერთი `-6`-ს გამორიცხავს, მეორე კი `-6`-ის ხუთი მეხუთე ფესვიდან ოთხს, და
მხოლოდ canonical text-ზე შედარება მათ გააერთიანებდა. ექსპერიმენტმა 0035-მა Generation 1-ის
series-ისთვის `14` object იპოვა, ე.ი. power series-ს convention-ისადმი ნაკლებად მგრძნობიარეს არ ხდის.

**რატომ ოთხი და არა ხუთი.** `x^5 + 6`-ს ხუთი მეხუთე ფესვი აქვს, ხოლო semantic key-ის excluded-points ნახევარი მათგან ოთხს აფიქსირებს, რადგან პროექტი ამოხსნას `real=True`-დ გამოცხადებულ სიმბოლოზე აწარმოებს. ეს იგივე მოკლე-ფესვების დეფექტია, რომლის გასასწორებლადაც ექსპერიმენტ 0035-ის მე-2 სექცია არსებობს, და ის აქ excluded-points კომპონენტში ჩნდება და არა roots-ში. `17`-ის `16`-თან განსხვავება, რომელზეც ეს აბზაცი დგას, ამით არ იცვლება და review-ში ხელახლა გამოიყვანეს; მცდარი მხოლოდ რიცხვი იყო.

## Multicore

Repository-ის პოლიტიკა default-ად multicore-ია და sequential გზას უშვებს მაშინ, როცა დროები ამას
ამართლებს. ორივე workload აქ ამ host-ზე გაიზომა — `16` core, Windows, spawn start method, `15`
worker ერთი core-ის მარაგით — და ორივე sequential გზას აგებს:

```text
workload        cells   sequential   parallel   speedup   records identical
cost grid          38     0.101 s     1.249 s    0.081    yes
semantic grid     121     0.766 s     1.821 s    0.421    yes
```

მიზეზი ფიქსირებული ხარჯია და არა სამუშაოს თვისება: pool-ის აწევას `1.2` წამი სჭირდება, რადგან
ყოველი spawn-ული worker SymPy-ს იმპორტს აკეთებს, სანამ რამეს გააკეთებდეს. ერთ cell-ზე ორი workload
`0.003` და `0.008` წამი ჯდება, ამიტომ routing წესი — sequential შეფასება pool-ის აწევის პლუს
გაყოფილი სამუშაოს წინააღმდეგ — ორივეს sequential გზაზე გზავნის. Crossover ნავარაუდევი კი არა,
გამოთვლილია: `205` semantic cell-ზე იგივე კოდი pool-ზე გადადის. Parallelism მხოლოდ სიჩქარეს ცვლის;
ორივე გზა ტოლ სტრუქტურებს აბრუნებს და test suite ამას ამოწმებს და არა ვარაუდობს.

## ინტერპრეტაცია

Founding question კითხულობს, რა მათემატიკა გვექნებოდა სხვა convention-ის ქვეშ. 0035-ის პასუხი
quadratic-ისთვის ნათელი იყო: worlds-ის დაახლოებით ნახევარში quadratic formula საერთოდ არ არსებობს,
რადგან standard ჩანაწერი უკვე factored cubic-ია. ეს პასუხი სწორია იმ string-ის შესახებ, რომელზეც
დაისვა. ის მდგრადი არ არის მაშინ, როცა ენა იმ operator-ს იძენს, რომელიც მათემატიკას ოთხი საუკუნეა
აქვს.

ის, რაც მას ცვლის, ნაკლებად საციტატოა და უფრო დასაცავი. `^`-ის ქვეშ standard quadratic მაინც
იმსხვრევა — `2`-ის ნაცვლად `6` object-ად — მაგრამ ეს მსხვრევა უკვე *უკეთეს* object-ს აღარ იძლევა.
ყოველ reading-ს, რომლის roots ჩაიწერება, radical სჭირდება, და reading-ების ნახევარი საერთოდ
polynomial არ არის: ესენი power tower-ებია ცვლადით exponent-ში, object-ები, რომლითაც არცერთი
world-ის სახელმძღვანელო არ დაიწყებდა. Generation 1-ის split-ს გამარჯვებული ჰყავდა; Generation 2-ისას
არავინ.

არსებობს იმავე რიცხვების მეორე, უფრო წყნარი წაკითხვა, და სწორედ ის განზოგადდება. ზომები `13` და
`12` არასოდეს ყოფილა მათემატიკაზე. ესენია ორ-operator-იანი support-ის ორი block, `25`-grammar-იან
registry-ზე დათვლილი, და იგივე string `121`-grammar-იან registry-ზე `61`-სა და `60`-ს კითხულობს.
**ამ პროექტში ნებისმიერი world რაოდენობა registry-ის ზომაა მანამ, სანამ თავის block სტრუქტურასთან
ერთად არ იქნება ნათქვამი**, და სწორედ ამ დისციპლინის გავრცელებას გვირჩევს ეს ექსპერიმენტი ყოველ
ადრინდელ რიცხვზე, რომელიც "`25` world-იდან `N`-ში" ფორმისაა.

და ბოლოს, conventional convention Generation 2-იდან უკეთესად და არა უარესად გამოდის. ის cost-ზე
`121`-იდან მეორეა, ერთი bracket-ით დამარცხებული grammar-ისგან, რომელიც თავად იმავე convention-ია
tie-ების გახსნით, და `^`-ს იმ პოზიციაზე აყენებს, რომელსაც მთელი registry ყველაზე იაფად ასახელებს.
ეს არ არის არგუმენტი, რომ convention ოპტიმალურია; ეს არის დაკვირვება, რომ ის ერთი operator, რომელიც
ყველაზე მეტად შეარყევდა Generation 1-ის ranking-ებს, არ შეარყევს.

## შეზღუდვები

- **`^` ერთადერთი დამატებული operator-ია.** T26 — juxtaposition, `2x`, და unary minus, `-x^2` —
  მკაფიოდ scope-ის გარეთაა და აქ ჩაუწერელია. სწორედ ეს ურთიერთქმედებები აქვს რეალურ notation-ს, და
  Generation 3, რომელიც მათ დაამატებს, ამ report-ის ნებისმიერ რიცხვს დაძრავს.
- **ის, რაც exponent-ში შეიძლება იდგეს, შეზღუდული არ არის, და ეს მოდელირების არჩევანია.** `^`
  იმავე ენის ჩვეულებრივი binary operator-ია, ამიტომ exponent არის ის, რასაც grammar იქ მოათავსებს,
  და reading-ები, როგორიცაა `(a*x)**(b*x + c + 2)`, ამის შედეგია. ენა, რომელიც მხოლოდ literal ან
  atomic exponent-ს დაუშვებდა, გაცილებით ნაკლებად დაიმსხვრეოდა და სხვა ექსპერიმენტი იქნებოდა.
- **Corpus hand-chosen-ია.** `38` ფორმულა ასახავს განსჯას იმის შესახებ, თუ როგორ გამოიყურება
  power-ების მქონე მათემატიკა, ხოლო მათგან `12` Generation 1-ში საერთოდ არ იწერება, რაც თავისთავად
  არჩევანია იმის შესახებ, თუ რა შევადაროთ. სხვა corpus ყოველ cost რიცხვს დაძრავდა და control-ის
  rank-საც შეცვლიდა.
- **Rank `121`-ზე ordinal-ად არ ედრება rank-ს `25`-ზე**, სწორედ ამიტომ ყოველ rank-ს აქ თავისი
  percentile ახლავს და ამიტომ ორი generation ერთსა და იმავე `26` object-ზეა შედარებული და არა
  corpus-ებს შორის. 0037-ის `3` of `25` კიდევ მესამე corpus-ია.
- **Roots `C`-ზეა და ყოველი reading-ისთვის მცდელობა არ ხდება.** Convention 0035-ისაა, უცვლელად
  გამოყენებული, და `I` radical-ად ითვლება, რადგან ის მართლაც radical-ია. Reading, რომელიც არც
  polynomial-ია და არც rational function ცვლადში, root list-ს ვერ იღებს და ასეც არის ნაჩვენები;
  `121` quadratic world-იდან `60` სწორედ ამ მდგომარეობაშია, ამიტომ "არცერთი world არ არის
  radical-ის გარეშე" ნიშნავს "არცერთი world, რომლის roots-ს ეს module ასახელებს".
- **Excluded points მხოლოდ `/` node-ებიდან მოდის.** წესი Generation 1-ისაა, უცვლელი. უარყოფითი
  exponent, ჩაწერილი როგორც `x^(0 - 2)`, წერტილს გამორიცხავდა და აღმოჩენილი არ არის; ამ corpus-ში
  ასეთს არცერთი entry არ წერს.
- **`domain` semantic key-ში ინერტულია** (`NF-2026-00005`). Triple `(canonical, domain,
  excluded points)` პროექტისაა და აქ უცვლელად გამოიყენება, მაგრამ ის ყოველთვის ლიტერალი `"R"`-ია,
  ამიტომ ფაქტობრივი discrimination ორკომპონენტიანია. ამ ექსპერიმენტის არცერთი დათვლა ამით არ
  იცვლება — sine series-ის `17` object `16` canonical text-ის პირისპირ excluded points-ით იყოფა —
  მაგრამ guarantee ისე უნდა ჟღერდეს, როგორც არის.
- **დროები ერთ host-ზეა აღებული** (`16` core, Windows, spawn start method). სხვა host-ზე რიცხვები
  სხვა იქნება და routing გადაწყვეტილება ხელახლა უნდა გაიზომოს და არა გადმოიწეროს.

## Evidence-ის კლასიფიკაცია

- **Observations** (executable, ამ repository-ში რეპროდუცირებადი): conservative extension-ის audit
  `11562` cell-ზე; round trip `4598` cell-ზე და minimality `5665` bracket-ზე; `a * x^2 + b * x + c`-ის
  `6` object group-ების ზომებით `21`/`20`/`20`/`20`/`20`/`20`; Generation 1-ის string-ის `2` object
  და `61`/`60` split Generation 2-ის registry-ში; `a*x*(b + x)*(c + x)`-ის არარსებობა `a * x^2 + b *
  x + c`-ის `121` წაკითხვაში, რაც **არ** ნიშნავს მის არარსებობას ენაში — `121` world-იდან `60` მას
  კვლავ კითხულობს Generation 1-ის string-იდან; survival table-ის ყოველი სტრიქონი, რომლის scope-იც
  ის ცხრა სტრიქონია და არა ორი ექსპერიმენტი; control-ის rank `2` of `121` და `6` of `25`; `^`-ის
  ყოველ პოზიციაზე `6.5`-bracket-იანი საფეხური; null model-ის split `3` `35`-ის წინააღმდეგ;
  Generation 2-ის sine series-ის `17` object; და დროები.
- **Interpretation** (დაკვირვებებიდან გამოტანილი და არა თვითონ დაკვირვებული): რომ იმ worlds-ის
  მათემატიკოსები ამ object-ებს ააშენებდნენ, და რომ power tower-ების world თავის სახელმძღვანელოებს
  მათით არ დაიწყებდა. ეს notational-cost არგუმენტია.
- **არ არის claimed**: რომ conventional order უკეთესია ან უარესი; რომ `121` world-ზე რაიმე universal
  law არსებობს; რომ corpus power-ების მქონე მათემატიკის representative sample-ია; რომ Generation 1-ის
  შედეგი მცდარი იყო — ის ზუსტია, და ეს ექსპერიმენტი მის scope-ს აცხადებს.

## ვალიდაცია

```text
994 passed
```

`tests/test_generation_two.py`: `51 passed`, სწორედ ამ რიგით — ჯერ conservative extension-ის audit
თავისი `11562` cell-ით pinned; შემდეგ right-associativity `2^3^2`-ზე, რომელიც `512`-ს იძლევა, და
tree-ების შედარებით; round trip და minimality მთელ `38 x 121` grid-ზე; headline quadratic
ლიტერალურად pinned, group-ების ზომებით, block-ების იარლიყებით, roots-ითა და control-ის group-ით;
0035-ისა და 0036-ის ყოველი გამოქვეყნებული claim სახელით pinned როგორც გადარჩენილი ან არა; null
model-ის split; cost ranking თავისი percentile-ებით; და sequential/parallel თანხმობა ორივე grid-ზე.

Mutation testing **იზოლირებულ ასლზე** ჩატარდა — `src/parseatlas` და test ფაილი scratch tree-ში
გადაიწერა და ყოველი mutation იქ დაედო და იქ გაეშვა, სამუშაო tree-ს არასოდეს შეხებია.

```text
BASELINE                                                            51 passed
KILLED   the power made left-associative
KILLED   left bracket threshold ignores the child's associativity
KILLED   right bracket threshold ignores the parent's associativity
KILLED   agreement audit checks only the top embedding
KILLED   excluded points dropped from the Generation 2 key
KILLED   object groups ordered smallest first
KILLED   the control's object taken as the largest group
KILLED   blocks counted as the support size rather than its factorial
KILLED   distinguishing power counts support instead of its factorial
KILLED   radical detection dropped from the root record
KILLED   an unattempted root list reported as attempted
KILLED   worker count loses the core headroom
KILLED   the parallel decision ignores the measured pool startup
KILLED   tokenizer loses Generation 1's rational literal
KILLED   the block label prints ties as a strict order
KILLED   minimality accepts every bracket without deleting it
KILLED   the domain component of the key replaced by a DIFFERENT constant
SURVIVED (expected) the domain component of the key replaced by the constant it always is

17/18 mutants killed
```

ერთადერთი გადარჩენილი განზრახია და `NF-2026-00005`-ის მუდმივი მტკიცებულებაა: `canonical["domain"]`-ის
ლიტერალი `"R"`-ით ჩანაცვლება ყველა `51` test-ს მწვანედ ტოვებს, რადგან `domain` არასოდეს იცვლება.
მის გვერდით მდგარი mutant, რომელიც მას **სხვა** კონსტანტით ცვლის, კვდება — ე.ი. ველი იკითხება,
უბრალოდ არაფერს არჩევს.
