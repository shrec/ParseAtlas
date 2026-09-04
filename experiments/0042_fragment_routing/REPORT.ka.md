# ParseAtlas ექსპერიმენტი 0042: გადარჩება თუ არა fragment routing seam-ებს?

## მიზანი

მფლობელის კითხვა, მისივე სიტყვებით: *შეიძლება თუ არა პრობლემა დაიშალოს fragment-ებად, თითოეული fragment ამოიხსნას იმ representation-ში, სადაც ის საუკეთესოდ იხსნება, და შედეგები შემდეგ ისევ შეერთდეს საბოლოო პასუხად?*

**ვერდიქტი, ორივე არქიტექტურაზე, ერთ აბზაცში - და ის ძირითადად უარყოფითია.**

- **MODEL I (inline: ერთი document, ერთი host convention).** Routing იგებს, და თითქმის არაფრით. ერთი გლობალური convention-ის წინააღმდეგ corpus routing-ის გარეშე `33` ფრჩხილს ჯდება, routing-ით კი `29`-ს - მოგება `4` არის `33`-ფრჩხილიან seamless prize-ზე, ანუ **prize-ის `12.1%` გადარჩება seam-ს**. Per-object baseline-თან რიცხვებია `7` და `6`: მოგება `1`, **`14.3%`**. და ამ მოგების ყოველი ფრჩხილი იყიდება იმ document-ით, რომელსაც მისივე host convention ვეღარ კითხულობს.
- **MODEL II (named intermediates).** Routing აგებს, და მძიმედ. იმავე corpus-ს `87` named intermediate სჭირდება იმისთვის, რომ მაქსიმუმ `7` ფრჩხილი მოაშოროს interior cost-ს. თითო definition line-ზე ერთი unit-ის ფასად Model II `87`-ს ჯდება გლობალური convention-ის `33`-ის წინააღმდეგ - **`54`-ით უარესი** - და definition line ერთი bracket pair-ის `0.3793`-ზე ნაკლები რომ ღირდეს, მხოლოდ მაშინ გავიდოდა Model II ნულზე.
- **და შედეგი, რომელიც card-ს წყვეტს.** შეზღუდე Model I იმ document-ებით, რომელთა decode-იც host convention-ის მკითხველს ნამდვილად შეუძლია, და inline routing **ზუსტად ნულს იძლევა**. შემოწმებულია `54375` cell-ზე - `87` fragment `25` host-ზე `25` world-ზე - `0` counterexample-ით. `render(F, h)` fragment-ის მინიმალურ-ფრჩხილიანი `h`-writing-ია, ამიტომ ნებისმიერი world, რომლის rendering-საც `h` სწორად კითხულობს, სულ მცირე იმდენივე ჯდება, რამდენიც თავად `h`. **ფრჩხილი scope-ს იფარგლავს; ის convention-ს არ ატარებს.**

ასე რომ, founding question-ის routing-ის ნახევარზე პატიოსანი პასუხი ასეთია: 0034-ის გაზომილი prize ნამდვილია, ის დიდია, და **ის fragment-ებზე არ არის - ის join-ებზეა**, ზუსტად იქ, სადაც routing-ს არაფერი აქვს შესათავაზებელი. საუკეთესო single world-ში `33` ფრჩხილიდან `21` join-ზე ზის და `9` fragment-ების შიგნით; registry-ის არცერთი world join-ებზე `21`-ზე ნაკლებს არ ტოვებს.

Module: `src/parseatlas/fragment_routing.py`. Tests: `tests/test_fragment_routing.py`.

## რას ეყრდნობა და რას არ იმეორებს

**პასუხის ნახევარი უკვე გაზომილია და ციტირდება და არა მეორდება.** ექსპერიმენტმა 0034 დაადგინა per-formula oracle თავის `58`-formula corpus-ზე: თუ თითო formula საკუთარ convention-ს აირჩევდა, corpus `3` ფრჩხილს დაჯდებოდა, საუკეთესო *ერთი* grammar კი `29`-ს იხდის. ეს `26`-ფრჩხილიანი gap ერთი გლობალური convention-ის ქონის ფასია. Formula-ს დონეზე routing მაშასადამე დაახლოებით ერთი რიგით იგებს - **და ეს რიცხვი seam-ებს სრულიად უგულებელყოფს. ეს არის prize-ის ზედა საზღვარი და არა შედეგი შეერთების შესახებ.**

`oracle_bound` იმავე სიდიდეს ამ card-ის corpus-ზე გადათვლის და გამოქვეყნებულის გვერდით დებს, ორივე შემთხვევაში საზღვრად მონიშნულს.

**ექსპერიმენტი 0038 decomposition-ის არგუმენტს აძლიერებს და მას შესავალში აქვს ადგილი.** `850` cell-ზე constant term და roots არასოდეს არიან ერთდროულად manifest, თუმცა shape rule-ებში არაფერი კრძალავს ამას. თუ პრობლემას ორივე სჭირდება, ვერცერთი single world ვერ აძლევს ორივეს, ამიტომ იქ decomposition ოპტიმიზაცია არ არის - ის იძულებითია. ეს card ამას არ ასუსტებს. ის ამბობს, რა ჯდება decomposition მაშინ, როცა ნაწილები უკან უნდა დაიდოს.

## ორი არქიტექტურა

ესენი არიან ის ორი რეალური გზა, რომლითაც SDK შეიძლება აშენდეს, და მათ seam cost-ს საერთო არაფერი აქვს.

```text
MODEL I   inline    one document, one host world; a fragment written in its own world is a
                    SUBEXPRESSION of it and pays whatever the host charges to keep the tree
MODEL II  named     each fragment is written and evaluated in its OWN world, bound to a name;
                    the name -- a leaf -- is what the next fragment uses
```

**Model I-ის seam ფრჩხილებია.** თითო fragment-ისთვის record სამ სიდიდეს ატარებს და არასოდეს ურევს მათ: რა ჯდება fragment **საკუთარ საუკეთესო world-ში**, რა ჯდება ის **host world-ში დაწერილი**, და სხვაობა - ის, რასაც ერთ-convention-იანი document კარგავს. დარიცხული seam არის თითო fragment-ზე ერთი bracket pair, რომელსაც host ვერ იტევს, ორი დამოუკიდებელი მიზეზიდან ერთ-ერთის გამო: host-ის precedence მას თავიდან დააჯგუფებდა, ან host მის შიგთავსს არასწორად წაიკითხავდა.

**Model II-ის seam definition line-ებია, და definition line უფასო არ არის.** `NAMING_UNIT_COST` თითო named intermediate-ზე ერთ unit-ს ხარჯავს, იმავე მასშტაბზე, რაზეც ერთი bracket pair. ეს არის modelling choice და ის ასეთადვეა დასახელებული: definition line სიმბოლოებში აშკარად *მეტია*, ვიდრე ერთი bracket pair - სახელი, binder, ხაზის გადატანა - ამიტომ `1` Model II-სთვის ყველაზე გულუხვი პატიოსანი ტარიფია. სწორედ იმიტომ, რომ ეს არჩევანია, `naming_break_even` აცხადებს იმ ტარიფს, რომელზეც Model II წაგებაზე გადადის, და არჩევანს უფასოდ არ ტოვებს.

**Model II-ის document self-describing-ია; Model I-ისა არა.** თითო definition line ასახელებს იმ world-ს, რომელშიც ის დაწერილია; ხაზს გარეთ არაფერი გადის. Inline document-ს ასეთი ადგილი არ აქვს. ეს სტრუქტურულია და არა modelling choice, და სწორედ ეს არის ორ არქიტექტურას შორის ნამდვილი განსხვავება.

## Splitting rule, გამოცხადებული პირველ გაზომილ რიცხვამდე

```text
Let L be the control grammar's level containing the root operator: {*, /} or {+, -}.
Descend from the root through every node whose operator lies in L.
Every operand hanging off that chain which is itself a Binary node is a FRAGMENT.
Leaves are not fragments: a leaf is one token and no convention can charge it anything.
The SKELETON is that chain with each fragment replaced by a hole.
```

ერთი წესი, გამოყენებული ყოველ object-ზე, რომელიც არაფერს კითხულობს გარდა tree-სა და control grammar-ის level-ებისა. ის `G0`-ის level-ებს კითხულობს იმიტომ, რომ intended tree განსაზღვრებით conventional notation-ის `G0`-parse-ია; split-ის შემდეგ `G0`-ს აღარაფერი ეკითხება. **სხვა წესი ამ report-ის ყოველ რიცხვს გადაანაცვლებდა** და ეს შეზღუდვებშია ნათქვამი და არა დამალული.

სამი გაშლილი split, რომ წესი ხელით შემოწმდეს:

```text
(x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)   root +   ->  2 fragments, both products
x * x / (a * a) + y * y / (b * b)               root +   ->  2 fragments, both quotients
x*x - 2*h*x + h*h + y*y - 2*k*y + k*k           root +   ->  6 fragments, all products
a / (b * c)                                     root /   ->  0 fragments: one homogeneous chain
```

## Corpus

`parseatlas.manifest_properties.CORPUS`-ის ყოველი written form - ექსპერიმენტი 0037-ის named law-ები პლუს 0038-ის calibration quadratic - რომელსაც წესი სულ მცირე ორ fragment-ად ჭრის. **ეს ფილტრი არის "composite"-ის განსაზღვრება; ვერცერთი writing ხელით არ არის არჩეული ან ამოგდებული**, და ის, რასაც წესი უარყოფს, თავისი count-ებით ქვეყნდება.

```text
composite writings          38
fragments                   87
distinct fragment sources   67
fragment counts             2 x 31,  3 x 5,  4 x 1,  6 x 1
writings excluded           12   (fewer than 2 fragments)
```

გამორიცხულები, იმ count-ით, რომელმაც ისინი გამორიცხა: `distributive_law.factored` `1`, `line.point_slope` `1`, `parabola.vertex` `1`, `midpoint.mean` `1`, `triangle_area.half_base_height` `0`, `trapezoid_area.mean_times_height` `1`, `difference_quotient.closed` `1`, `quotient_rule.closed` `1`, `chain_rule.standard` `0`, `linear_approximation.point_form` `1`, `taylor_first_term.standard` `1`, `riemann_sum_term.standard` `1`.

## Obligation ყოველ seam-ზე

ერთი world-ისთვის დაწერილი fragment სხვას რომ წაუკითხო, სხვა რამეს ნიშნავს, ამიტომ join მხოლოდ მაშინ არის ვალიდური, თუ მასზე გადამავალი მნიშვნელობა შენარჩუნებულია. ყოველი წარმოებული routing უკან decode-დება tree-მდე - skeleton იკითხება host world-ში, თითო piece კი იმ world-ში, სადაც ის იყო გამართული - და ედრება single-world composite-ს **პროექტის semantic key**-ზე `(canonical form, domain, excluded points)`, უცვლელად იმპორტირებულს `parseatlas.alternative_mathematics.semantic_key`-იდან. **და არა rendered string-ზე.**

```text
routings checked (38 objects x 4 objectives x 2 models)   304
routings whose object is preserved                        304
```

შემოწმება ცარიელი არ არის, და negative control ამას ამბობს. `ellipse.standard` ორივე fragment-ს `G01`-ში მარშრუტიზებს, სადაც `x * x / a * a` აღნიშნავს `(x*x)/(a*a)`-ს. გამოაცხადე იმავე სიმბოლოებისთვის არასწორი world და decode გვაძლევს `x**2 + y**2`-ს - სხვა function-ს, დაჭერილს key-თი და არა string-ით.

## დაკვირვებული შედეგები

### 1. სად ზის სინამდვილეში single-world document-ის ფრჩხილები

ეს არის ის სტრუქტურული ფაქტი, რომელზეც მთელი ვერდიქტი დგას. Fragment-ის შიგნით მყოფი ფრჩხილი ის არის, რომელიც routing-ს შეუძლია გადაანაცვლოს; **join**-ზე მყოფი ფრჩხილი seam-ს ეკუთვნის და არცერთ fragment-ს.

| world | whole | interior | skeleton | joins |
|---|---|---|---|---|
| `G0` (`*/ +-`) | 35 | 14 | 0 | 21 |
| `G18` (`* / - +`), best | 33 | 9 | 3 | 21 |
| floor over all 25 worlds | 33 | 0 | 0 | 21 |

**Interior-ის იატაკი `0`-ია: `87` fragment-იდან ყოველი უფასოა რომელიღაც world-ში.** Join-ის იატაკი `21`-ია და ვერცერთი world ვერ სჯობს მას. ანუ seamless prize `33` ფრჩხილია და მათგან `21` კონსტრუქციულად მიუწვდომელია.

### 2. Prize, seam და ის, რაც გადარჩა - სამი ცალკე რიცხვი

```text
one global convention, no routing (G18)            33
per-object oracle (each object picks its world)     7
per-fragment oracle, NO seam at all                 0
prize                                              33
```

ცნობისთვის, გამოქვეყნებული 0034-ის რიცხვები იმ ექსპერიმენტის საკუთარ corpus-ზე: per-formula oracle `3`, საუკეთესო single grammar `29`, gap `26`. ამ corpus-ზე gap ასევე `26`-ია (`33` მინუს `7`). **ეს ორი სხვადასხვა corpus-ის დამთხვევაა და 0034-ის რეპროდუქცია არ არის.**

### 3. ვერდიქტი, objective-ისა და model-ის მიხედვით, ერთი host convention ყველა 38 document-ზე

ეს არის like-for-like შედარება: ერთი სახლის convention ერთი სახლის convention-ის წინააღმდეგ, ერთადერთი განსხვავებით - არის თუ არა fragment-ები მარშრუტიზებული.

| objective / model | routed | interior | skeleton | seam | best host | vs `33` | host-readable |
|---|---|---|---|---|---|---|---|
| `brackets` / inline | 29 | 0 | 3 | 26 | `G18` | **+4** | 35 |
| `brackets` / named | 87 | 0 | 0 | 87 | `G0` | -54 | 38 |
| `visibility` / inline | 35 | 14 | 0 | 21 | `G0` | -2 | 38 |
| `visibility` / named | 101 | 14 | 0 | 87 | `G0` | -68 | 38 |
| `visibility_opaque` / inline | 33 | 7 | 0 | 26 | `G0` | 0 | 33 |
| `visibility_opaque` / named | 94 | 7 | 0 | 87 | `G0` | -61 | 38 |
| `depth` / inline | 35 | 14 | 0 | 21 | `G0` | -2 | 38 |
| `depth` / named | 101 | 14 | 0 | 87 | `G0` | -68 | 38 |

`brackets`/inline-ში მთელი `4`-ფრჩხილიანი მოგება ზუსტად ორი document-იდან მოდის - `circle.center_radius` და `distance_components.squared`, თითო `4`-დან `2`-მდე - და **ორივე წყვეტს host convention-ში წაკითხვადობას**. მესამე, `quadratic.expanded`, წაუკითხავი ხდება საერთოდ ყოველგვარი მოგების გარეშე.

### 4. ვერდიქტი თითო object-ზე, per-object baseline-ის წინააღმდეგ

აქ თითო document-ს შეუძლია საკუთარი host აირჩიოს, და baseline შესაბამისად ამ object-ის საუკეთესო single world-ია.

| objective / model | best single | routed | interior | skeleton | seam | wins | ties | loses |
|---|---|---|---|---|---|---|---|---|
| `brackets` / inline | 7 | 6 | 0 | 0 | 6 | 1 | 37 | 0 |
| `brackets` / named | 7 | 87 | 0 | 0 | 87 | 0 | 2 | 36 |
| `visibility` / inline | 7 | 19 | 14 | 0 | 5 | 1 | 32 | 5 |
| `visibility` / named | 7 | 101 | 14 | 0 | 87 | 0 | 2 | 36 |
| `visibility_opaque` / inline | 7 | 13 | 7 | 0 | 6 | 1 | 32 | 5 |
| `visibility_opaque` / named | 7 | 94 | 7 | 0 | 87 | 0 | 2 | 36 |
| `depth` / inline | 7 | 19 | 14 | 0 | 5 | 1 | 32 | 5 |
| `depth` / named | 7 | 101 | 14 | 0 | 87 | 0 | 2 | 36 |

ერთადერთი `brackets`/inline მოგება არის `sum_of_cubes.factored`, `2`-დან `1`-მდე:

```text
intended          (a + b) * (a * a - a * b + b * b)
host              G01  ( + - * / )
routed document   a + b * (a * a - a * b + b * b)          1 bracket pair
read in G01       a * (a - a) * (b + b) * b                a DIFFERENT object
```

Seam-ის ფრჩხილი join-ს სწორად ინახავს და შიგთავსზე ვერაფერს აკეთებს, რომელსაც `G01`-ის მკითხველი თავიდან აჯგუფებს. ეს არის Model I-ის მთელი უპირატესობა ამ corpus-ზე.

### 5. Seam, მიზეზების მიხედვით დაშლილი

| quantity | `brackets`/inline | `brackets`/named |
|---|---|---|
| fragments | 87 | 87 |
| fragments routed off `G0` | 10 | 10 |
| seam total | 6 | 87 |
| wraps forced by host precedence only | 2 | 0 |
| wraps forced by host misreading only | 4 | 0 |
| wraps forced by both | 0 | 0 |
| documents host-readable | 34 of 38 | 38 of 38 |
| forfeited by one convention | 9 | 14 |

**Model I-ის seam-ის ორი მესამედი სწორედ ის მიზეზია, რომელსაც არავინ ითვალისწინებს ბიუჯეტში.** Precedence-ის დაცვა არის ის seam, რომელსაც SDK-ის დიზაინერი იწინასწარმეტყველებდა; host-ის მიერ არასწორად წაკითხვა კი არის ის seam, რომელიც სინამდვილეში დომინირებს, და ფრჩხილი მას არ ასწორებს.

### 6. Host-readable inline routing ზუსტად არაფერს იძლევა

```text
fragments x hosts x worlds checked   54375
cheaper readable alternatives            0
total gain over all 25 hosts             0
```

არგუმენტი იძულებითია, და ბადე მას ადასტურებს და არა ანაცვლებს. Fragment-ის token word ფიქსირებულია, ამიტომ მისი `h`-writing მხოლოდ ფრჩხილების განლაგებით განსხვავდება; `render` ფრჩხილს ზუსტად იქ დებს, სადაც `h` სხვაგვარად თავიდან დააჯგუფებდა, და 0034-ის minimality audit ამოწმებს, რომ თითოეული მათგანი მზიდია; მაშასადამე `render(F, h)` არის *ის* მინიმალურ-ფრჩხილიანი `h`-writing, და ნებისმიერი world, რომლის rendering-საც `h` სწორად კითხულობს, სულ მცირე იმდენივე ჯდება. `G18`-ში readable interior-ის იატაკი `9`-ია, იდენტური `G18`-ის საკუთარი `9`-ისა.

წაკითხვადობა დეფიციტური არ არის: საშუალოდ `25` world-იდან `24.310344827586206` იძლევა rendering-ს, რომელსაც `G18` სწორად კითხულობს. სწორედ ესენი არიან ის world-ები, რომელთა rendering `G18`-ისას ემთხვევა, და ისინი ზუსტად იმდენს ჯდებიან, რამდენსაც `G18`.

### 7. ოთხი objective და ეთანხმებიან თუ არა ისინი

| objective | measures | worlds tied on a fragment (mean) | fragments where all 25 tie |
|---|---|---|---|
| `brackets` | notational cost, 0034/0037 | 22.448275862068964 | 70 |
| `visibility` | manifest properties, 0038 transparent regime | 25.0 | 87 |
| `visibility_opaque` | manifest properties, 0038 opaque regime | 23.195402298850574 | 75 |
| `depth` | critical path, imported from `parallel_worlds` | 25.0 | 87 |

Pairwise თანხმობა `87` fragment-ზე: `brackets`/`visibility` `77`, `brackets`/`visibility_opaque` `82`, `brackets`/`depth` `77`, `visibility`/`visibility_opaque` `82`, `visibility`/`depth` `87`, `visibility_opaque`/`depth` `82`. ოთხივე თანხმდება `77`-ზე. სულ არის მხოლოდ `3` განსხვავებული choice pattern: `(G0, G0, G0, G0)` `77` fragment-ზე, `(G01, G0, G01, G0)` `5`-ზე, `(G01, G0, G0, G0)` `5`-ზე.

**ოთხიდან ორს საერთოდ არ შეუძლია უპირატესობის გამოხატვა, და მიზეზი სტრუქტურულია და არა corpus-ის სიმცირე.**

- `depth` არის intended tree-ის critical path, world კი მხოლოდ იმას ირჩევს, თუ როგორ *დაწეროს* ფიქსირებული tree. გაზომილია: world-invariant ყველა `87` fragment-ზე, `0` fragment, სადაც რომელიმე world-ის minimum-cost writing intended tree-ზე ზედაპირულია, `20` fragment საერთოდ reassociable. სტრუქტურული მიზეზი ისაა, რომ იმავე operator-ის right child **ყოველ** world-ში ფრჩხილდება, ამიტომ chain-ის ყველაზე იაფი writing ყოველთვის ყველაზე ღრმაა - cost და depth ერთმანეთს ეწინააღმდეგებიან და ყველაზე იაფი writing depth-ზე არასოდეს იგებს.
- `visibility` 0038-ის **პირველად transparent regime**-ში იმავე ტიპის მიზეზით არის world-invariant: shape rule ფრჩხილს *გამჭოლად* უყურებს, ამიტომ ფიქსირებული tree-ის manifest set tree-ის და არა world-ის function-ია. გაზომილია: `87`-დან `0` fragment იცვლება, range `0`.

**Opaque** regime, სადაც ფრჩხილი მალავს იმას, რაც მის შიგნითაა, ის არის, რომელსაც უპირატესობის გამოხატვა შეუძლია: `87`-დან `12` fragment იცვლება, მაქსიმალური range `5`, და `G0` საუკეთესო world-ებს შორისაა `87`-დან `82`-ზე. სწორედ იქ ცხოვრობს ნამდვილი უთანხმოება - `5` fragment-ზე `brackets` ამბობს `G01`-ს და `visibility_opaque` ამბობს `G0`-ს:

```text
(y - k) * (y - k)     (y2 - y1) * (y2 - y1)     u * dv / (v * v)     y * y / (b * b)  twice
```

### 8. სად მიდის ათი მარშრუტიზებული fragment

ყოველი fragment, რომელიც conventional world-ს ტოვებს, `G01`-ში (`+ - * /`) მიდის, და თითოეული მათგანი additive form-ია multiplicative context-ში მჯდომი:

```text
a * (r + s) * x       (x - h) * (x - h)       (y - k) * (y - k)       x * x / (a * a)
y * y / (b * b)       (x2 - x1) * (x2 - x1)   (y2 - y1) * (y2 - y1)   u * dv / (v * v)
```

`87` fragment-იდან `77` უკვე უფასოა `G0`-ში; `70` უფასოა `25` world-იდან ყოველში. ეს არის roadmap-ის საკუთარი პროგნოზი, სხვა მიმართულებიდან მოსული: როცა `+` ყველაზე მაგრად აკავშირებს, სწორედ factored form ხდება parenthesis-free.

### 9. რა უნდა ღირდეს named intermediate

| objective | names | fixed cost | break-even vs `33` | break-even vs `7` |
|---|---|---|---|---|
| `brackets` | 87 | 0 | 0.3793 | 0.0805 |
| `visibility` | 87 | 14 | 0.2184 | negative |
| `visibility_opaque` | 87 | 7 | 0.2989 | 0.0 |
| `depth` | 87 | 14 | 0.2184 | negative |

ყოველ objective-ზე ყველაზე დიდი per-name ტარიფი, რომელზეც Model II ჯერ კიდევ იგებს, არის `0`. **Model II არ აგებს იმიტომ, რომ naming unit მის საწინააღმდეგოდ დაფასდა; ის აგებს ნებისმიერ დადებით ფასზე.**

## Headline კითხვები

1. **Model I-ში სჯობს თუ არა routing საუკეთესო single world-ს seam-ების გადახდის შემდეგ? რამდენით?** დიახ, `33`-დან `4` ფრჩხილით ერთი გლობალური host convention-ის ქვეშ (`29` `33`-ის წინააღმდეგ) და `7`-დან `1`-ით per-object baseline-ის წინააღმდეგ (`6` `7`-ის წინააღმდეგ) - და მთელი მოგება ორი document-იდან მოდის, რომლებსაც host convention ვეღარ კითხულობს.
2. **Model II-ში იგივე კითხვა.** არა: `87` `33`-ის წინააღმდეგ ერთი გლობალური convention-ის ქვეშ, `54`-ით უარესი, და `87` `7`-ის წინააღმდეგ per object, `80`-ით უარესი; definition line-ის break-even ფასი ერთი bracket pair-ის `0.3793`-ია და ვერცერთი მთელი ტარიფი ვერ იგებს.
3. **0034-ის ტიპის seamless prize-იდან რამდენი გადარჩება პროცენტულად?** `12.1%` გლობალური baseline-ის წინააღმდეგ (`4` `33`-დან), `14.3%` per-object baseline-ის წინააღმდეგ (`1` `7`-დან), და `0.0%` მას შემდეგ, რაც document-ს მოეთხოვება საკუთარ host convention-ში წაკითხვადობა.
4. **მიმართავენ თუ არა objective-ები fragment-ს ერთსა და იმავე world-ში?** ისინი თანხმდებიან `87` fragment-იდან `77`-ზე და სულ არის მხოლოდ `3` განსხვავებული pattern, მაგრამ თანხმობა ძირითადად სიჩუმეა: `visibility` და `depth` ყველა `25` world-ს აიგივებენ ყველა `87` fragment-ზე და საერთოდ ვერ გამოხატავენ უპირატესობას, `brackets` და `visibility_opaque` კი ნამდვილად არ თანხმდებიან `5`-ზე.
5. **არის თუ არა object, სადაც routing ერთ objective-ში იგებს და მეორეში აგებს?** **არა** - ნაკრები ცარიელია. საერთოდ იგებს ზუსტად ერთი object, `sum_of_cubes.factored`, და ის ოთხივე objective-ში იგებს. ხუთი object მართლაც იცვლის ვერდიქტს objective-თან ერთად - `circle.center_radius`, `distance_components.squared`, `ellipse.standard`, `hyperbola.standard`, `quotient_rule.split` - მაგრამ თითოეული **ფრეა** `brackets`-ში და **წაგებაა** დანარჩენ სამში, არასდროს მოგება. ამ სტრიქონის ადრინდელი რედაქცია პასუხობდა „დიახ, `5` მათგანი", მაშინ როცა მისივე დამაბოლოებელი წინადადება ამბობდა „ფრე"; module და suite ყოველთვის სწორად ითვლიდნენ და მხოლოდ პროზა აჭარბებდა.
6. **რამდენად ხშირად არის `G0` სწორი host შეერთებული document-ისთვის?** `brackets`/inline-ში ის არჩეულია `38` document-იდან `24`-ზე, მაგრამ *ერთადერთ* ოპტიმალურად მხოლოდ `1`-ზეა; corpus-ის დონეზე საუკეთესო გლობალური inline host არის `G18` და არა `G0`. Model II-ში ყველა `25` world აიგივდება `38` document-იდან `31`-ზე, რადგან skeleton, რომლის operand-ებიც სახელებია, leaf-ების chain-ია და არსად არაფერს ჯდება.

## ინტერპრეტაცია

შედეგი founding question-ის routing-ის ნახევარს ერთი განსხვავების ირგვლივ გადააწყობს, რომელსაც წინა oracle-ები ვერ ხედავდნენ.

```text
0034's oracle  ->  what would the corpus cost if each PIECE could pick its convention
this card      ->  what is left after the pieces have to be written down together
```

Prize ნამდვილია და დიდი - `33` ფრჩხილი `33`-დან ამ corpus-ზე, რადგან ყოველი fragment რომელიღაც world-ში უფასოა. მაგრამ ის ისე არ არის განაწილებული, როგორც routing-ის არქიტექტურას სჭირდება. **`33`-დან `21` join-ის ფრჩხილია და registry-ის ვერცერთი world ვერ ჩამოდის `21`-ზე ქვემოთ.** Routing interior-ებზე მოქმედებს; cost join-ებზეა; ორი ძლივს ემთხვევა ერთმანეთს. ეს ამ corpus-ის სიძნელის ფაქტი არ არის, ეს ფაქტია იმის შესახებ, თუ *რა არის* join: ფრჩხილი join-ზე იმიტომ არსებობს, რომ ორი განსხვავებული ფორმის ნივთი ხვდება ერთმანეთს, და ის, თუ რომელმა world-მა დაწერა რომელიმე მათგანი, არ ცვლის იმას, რომ ისინი ხვდებიან.

მეორე შედეგი ის არის, რაც SDK-ის დიზაინერმა პირველად უნდა წაიკითხოს. **Model I notational დონეზე რეალური არქიტექტურა არ არის.** ფრჩხილი scope-ს იფარგლავს; ის convention-ს არ ატარებს. Inline document, რომელიც convention-ებს ურევს, ამიტომ ან ინახავს ყოველ fragment-ს ისეთ rendering-ში, რომელსაც host-იც სწორად კითხულობს - და მაშინ ის ზუსტად ერთ-convention-იან document-ს ჯდება, minimality-დან გამომდინარე და `54375` cell-ზე შემოწმებული - ან ატარებს fragment-ებს, რომლებსაც host არასწორად კითხულობს, და მაშინ ის საერთოდ არ არის ერთი convention-ის document და სჭირდება side channel, რომელიც notation-ს არ აქვს. აქ გაზომილი `4`-ფრჩხილიანი მოგება მეორე შემთხვევაა, და მისი ფასი ისაა, რომ `38` document-იდან `3` წყვეტს იმის ნიშვნას, რასაც ამბობს.

**Model II არის ის არქიტექტურა, რომელიც მუშაობს, და ის სიიაფით არ მუშაობს.** ის `87`-ს ჯდება იქ, სადაც ერთი convention `33`-ს. ის, რასაც ის ყიდულობს, არის correctness: თითო ხაზი ასახელებს საკუთარ world-ს, ხაზს გარეთ არაფერი გადის, ყველა `38` document host-readable-ია, და object ყოველ seam-ს გადარჩება. სწორედ ეს არის ის გარიგება, რომელსაც გაზომვა სინამდვილეში ააშკარავებს - არა cost cost-ის წინააღმდეგ, არამედ **cost decodability-ის წინააღმდეგ** - და სწორედ ამიტომ SDK, რომელიც representation-ებს მარშრუტიზებს, სახელებს დააკავშირებს და expression-ებს არ ჩადგამს ერთმანეთში. 0033-ის Region model უკვე ატარებს ამ ფორმას: named intermediate არის state binding, და decode relation არის ის, რისთვისაც სახელია.

მესამე შედეგი objective-ებზეა, და ის 0038-ს ამახვილებს და არ ეწინააღმდეგება. *Object*-ის დონეზე world ირჩევს object-ის named writing-ებს შორის, და სწორედ ეს არჩევანი ცვლის visibility-ს world-ებს შორის. *Fragment*-ის დონეზე მხოლოდ ერთი writing არსებობს, და transparent regime-ში shape rule ფრჩხილებს გამჭოლად უყურებს, ამიტომ არაფერი იცვლება. **Visibility არის writing-ებს შორის არჩევანის და არა writing-ის თვისება.** Fragment-ის დონეზე routing-ს მისი გამოყენება არ შეუძლია. Opaque regime დისკრიმინაციის ნაწილს აღადგენს - `87` fragment-იდან `12` - და მაშინვე არ თანხმდება cost-თან მათგან `5`-ზე, რაც ამ სექციის ნამდვილი SDK-დიზაინის შედეგია: **router, რომელიც ფრჩხილებს აოპტიმალურებს, და router, რომელიც იმას აოპტიმალურებს, რაც იკითხება, ერთსა და იმავე fragment-ს სხვადასხვა world-ში გაგზავნიან, და პროექტს არ აქვს წესი, რომელიც ამ ორს დაალაგებს.**

## შეზღუდვები

- **Splitting rule გამოცხადებულია და არა აღმოჩენილი, და სხვა წესი ყოველ რიცხვს გადაანაცვლებდა.** Operator-ის *იდენტობაზე* დაჯაჭვა control grammar-ის level-ის ნაცვლად `circle.general`-ს `6`-ის ნაცვლად `2` fragment-ად დაჭრიდა; უფრო აგრესიული დაჯაჭვა მეტ და პატარა fragment-ს და უფრო დიდ seam-ს მოგვცემდა. წესი პირველ გაზომვამდე დაფიქსირდა და არ იყო მორგებული მანამ, სანამ routing არ მოიგებდა; report იმას იძლევა, რაც მისცა.
- **Cost არის ფრჩხილები და naming unit-ები და არა runtime.** აქ არაფერია ნათქვამი იმაზე, თუ რამდენად სწრაფად ითვლება რამე, რამდენად წასაკითხია document ადამიანისთვის, ან რამდენად ძნელია მისი სწავლება. ორი document ერთი და იმავე ფრჩხილების რაოდენობით შეიძლება ძალიან განსხვავებულად მძიმე იყოს.
- **Model II-ის naming unit არის modelling choice და ასეც უნდა წაიკითხოს.** თითო definition line-ზე ერთი unit-ის დარიცხვა definition line-ს bracket pair-ის იმავე მასშტაბზე აყენებს, რაც Model II-ს ეხმარება; break-even ტარიფები (`0.3793` გლობალური baseline-ის წინააღმდეგ, `0.0805` per-object-ის წინააღმდეგ) გამოქვეყნებულია, რომ მკითხველმა თავისი ფასი ჩასვას. ის, რაც modelling choice *არ* არის, არის Model II-ის decodability, რომელიც სტრუქტურულია.
- **Model I-ის seam ერთ bracket pair-ს ხარჯავს convention-ის გადართვაზე, რომელსაც ფრჩხილი სინამდვილეში ვერ ასიგნალებს.** ეს განზრახია და ის Model I-ს ეხმარება: პატიოსნად დარიცხული გადართვა საჭიროებს ნიშანს, რომელიც Generation 1-ის notation-ს არ აქვს. `host_readable` სვეტი არის იმის გაზომვა, რასაც ფრჩხილი ვერ აკეთებს, და სწორედ ამიტომ headline წაკითხვადი ვარიანტის წინააღმდეგაც არის ნათქვამი.
- **Corpus ხელით არის შერჩეული.** `38` composite writing `29` named object-იდან ოთხ field-ში არ არის sample რაიმე განსაზღვრული population-იდან. ფილტრი, რომელმაც ისინი წარმოქმნა, მექანიკურია, მაგრამ მის უკან მდგომი object-ები პროექტმა representative mathematics-ად შეარჩია.
- **Seam-ის ვალდებულება ადასტურებს routing-ის ᲒᲔᲒᲛᲐᲡ და არა შეერთებულ სტრიქონს.** `verify_routing` კითხულობს skeleton-ს host world-ში და თითო piece-ს იმ world-ში, სადაც ის იყო მიმართული, და ამას ადარებს single-world composite-ს semantic key-ზე. ის ხელახლა **არ** კითხულობს inline document-ს, ამიტომ document, რომელიც სწორი გეგმიდან არასწორად აიწყო, ამ შემოწმებით არ დაიჭერდა. ეს განზრახია და არა გამორჩენა: Model I-ისთვის document **არაა** ყოველთვის ერთგული host world-ში, და სწორედ ეს ჩავარდნა არის ამ ექსპერიმენტის საკუთარი შედეგი, გაზომილი და გამოქვეყნებული `host_readable` სვეტად. შემოწმება, რომელიც მოითხოვდა document-ის სწორად წაკითხვას თავის host-ში, ამტკიცებდა იმას, რასაც რეპორტი მცდარად აჩვენებს. ეს ორი სხვადასხვა კითხვაა და ორივე დაფიქსირებულია.
- **0034-ის oracle-ის რიცხვი არის seamless საზღვარი და არა მიღწეული შედეგი**, და ასეთივეა ამ card-ის `0`. ორივე თითო ნაწილს საკუთარ world-ში აფასებს და ნაწილების უკან დადებაზე საერთოდ არაფერს არიცხავს.
- **Semantic key-ის `domain` კომპონენტი ინერტულია** (`NF-2026-00005`): `canonical.py` ყოველი expression-ისთვის ლიტერალურ `"R"`-ს წერს, ამიტომ ოპერატიული დისკრიმინაცია არის `(canonical form, excluded points)`. Key აქ უცვლელად გამოიყენება და ეს ცხადდება და არა სწორდება გავლით.
- **Generation 1-ს არ აქვს exponentiation და არ აქვს unary minus**, ამიტომ კვადრატები product-ებად იწერება და fragment-ების პოპულაცია უფრო multiplicative-ია, ვიდრე რეალური notation იქნებოდა.
- **`depth` იმპორტირებულია `parallel_worlds`-იდან, რომელსაც სხვა card პარალელურად ავითარებს.** გამოყენებული function არის `depth(tree)`, critical path leaf-ით `0`-ზე. თუ იმ module-ის კონვენცია შეიცვლება, ამ card-ის depth objective მასთან ერთად შეიცვლება.

## Evidence-ის კლასიფიკაცია

- Corpus-ის ზომები (`38`, `87`, `67`), fragment count-ები, დაშლა (`interior` `14` და `9`, `joins` `21`), oracle-ის რიცხვები (`33`, `7`, `0`) და ყოველი ვერდიქტის total არის executable **observation**-ები ამ corpus-ზე და ამ `25` world-ზე.
- Round trip (`3125` შემოწმება, `0` წარუმატებლობა) და minimality (`1945` ფრჩხილი, `0` მოსაშორებელი) არის **verified properties** composite-ისა და fragment-ის ბადეზე, ხელახლა გაშვებული 0034-ის საკუთარი audit-ებიდან და არა ხელახლა იმპლემენტირებული.
- **Obligation ყოველ seam-ზე არის verified property**: `304` routing, `304` object შენარჩუნებული semantic key-ზე, negative control-ით, რომელიც ისე ვარდება, როგორც უნდა.
- „Host-readable inline routing ზუსტად ნულს იძლევა" არის **არგუმენტი** - `render`-ის minimality-დან - რომლის evidence-იც არის ამომწურავი `54375`-cell-იანი ბადე `0` counterexample-ით. ეს არის მტკიცება ამ corpus-ის fragment-ებზე და არა თეორემა ყველა tree-ზე.
- `depth`-ისა და transparent `visibility`-ის დეგენერაცია არის **სტრუქტურული** და არა corpus-conditional: ის გამომდინარეობს იქიდან, თუ რის შეცვლა აქვს world-ს უფლება. გაზომვები მოყვანილია იმისთვის, რომ მტკიცება შემოწმდეს და არა იმისთვის, რომ ის ინდუქციით დამტკიცდეს.
- „Model II არის ის არქიტექტურა, რომელიც SDK-მ უნდა გამოიყენოს" არის cost-versus-decodability გარიგების **ინტერპრეტაცია** და არა გაზომვა. გაზომილია გარიგება.
- ამ corpus-ზე `26`-ფრჩხილიანი gap-ის დამთხვევა 0034-ის `26`-თან არის **ორი corpus-ის დამთხვევა** და ამაზე მეტი არაფერია ნაცხადები.

## ვალიდაცია

```text
tests/test_fragment_routing.py     47 passed
whole suite                       891 passed, 2 failed   (ამ გაშვების მიხედვით)
```

`2` წარუმატებლობა არის `tests/test_geometry_atlas.py::test_every_svg_the_report_references_exists_and_is_not_empty` და `::test_every_figure_is_well_formed_paints_its_own_ground_and_stays_inside_the_viewbox`: ექსპერიმენტი 0040-ის figure ფაილები, რომლებსაც სხვა card პარალელურად წერს. ამ card-ში არაფერი არ იმპორტირებს და არ ეხება `geometry_atlas`-ს, და ორივე წარუმატებლობა მეორდება ამ card-ის module-ის მოშორებითაც.

Sequential parallel-ის წინააღმდეგ verdict sweep-ზე (`16` core, `12` worker, `304` cell):

```text
sequential                 7.69 s
parallel (12 processes)    3.58 s
speedup                    2.15x   ->  parallel wins
identical records          True
default decision           parallel
```

**გადაწყვეტილება გაზომილია და არა დაშვებული, და ის ორჯერ მიიღება** იმიტომ, რომ ორი workload თითო cell-ზე ორი რიგით განსხვავდება. Verdict cell არის ორი SymPy `simplify` გამოძახება `0.0273` წამზე; bracket cell არის `25` string rendering `0.00031` წამზე. `should_parallelise` sequential შეფასებას ადარებს pool startup-ს პლუს გაყოფილ სამუშაოს, ამიტომ verdict sweep პარალელდება და bracket sweep არა. გამოცხადებული კონსტანტები გაზომვებს ზემოთ ამრგვალებენ - `VERDICT_CELL_SECONDS` `0.032`, `BRACKET_CELL_SECONDS` `0.00043`, `POOL_STARTUP_SECONDS` `1.8` გაზომილი `1.40`-ის წინააღმდეგ - ასე რომ შეფასება არასოდეს არის ოპტიმისტური იმ overhead-ზე, რომელიც უნდა ამორტიზდეს. Worker-ების რაოდენობა დაკვირვებული core count-იდან იღება `2` core-ის მარაგით და `12`-ის ჭერით; ის არასოდეს არის hardcoded კონსტანტა.

Mutation testing იზოლირებულ ასლზე scratchpad-ში (canonical tree ხელუხლებელი), `17` mutant გადამწყვეტ ადგილებზე:

```text
split descends through the WRONG level                       KILLED
leaves are counted as fragments                              KILLED
the seam forgets that a host can misread a fragment          KILLED
the seam forgets host precedence                             KILLED
a named intermediate is free                                 KILLED
the seam obligation compares strings instead of objects      KILLED
the total drops the seam                                     KILLED
the decode reads every piece in the host world               KILLED
opaque visibility is minimised instead of maximised          KILLED
transparent visibility is minimised instead of maximised     SURVIVED
both visibility objectives read the same regime              KILLED
ties break to the last world instead of the conventional one KILLED
the host is always the control world                         KILLED
the readable audit calls every world readable                KILLED
reassociation is allowed to move a minus                     KILLED
the fragment oracle is priced in the control world           KILLED
host readability is asserted rather than parsed              KILLED

killed 16/17
```

**გადარჩენილი არის შედეგი და არა ხარვეზი.** Transparent visibility objective-ის maximise-დან minimise-ზე გადაბრუნება არაფერს ცვლის, რადგან ამ objective-ის ქულა world-invariant-ია ყველა `87` fragment-ზე: minimise და maximise `25` world-ის ერთსა და იმავე გათანაბრებულ სიმრავლეს ირჩევენ. ამ corpus-ზე ვერცერთი test ვერ განასხვავებს მათ, და ტესტი, რომელიც მიზეზს ამაგრებს - `test_the_two_visibility_regimes_answer_differently_for_a_structural_reason` - არის მტკიცების პატიოსანი ფორმა. იგივე mutation opaque objective-ზე გამოყენებული იკვლება.
