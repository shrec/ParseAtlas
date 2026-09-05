# ParseAtlas ექსპერიმენტი 0049: ეკვივალენტური writing-ების Pareto atlas

## მეოთხე კითხვა, პირველ რიგში

Owner-ის ყველაზე ბასრი კითხვა იყო, რამდენი frontier point არსებობს, რომელსაც კონვენციური world არ
აირჩევდა. **პასუხი არ არის ნული.**

> **`34` object-სა და `667` ეკვივალენტურ writing-ზე ოთხღერძიანი frontier ატარებს `59` წერტილს,
> რომელთაგან `G0` წერს `34`-ს. ანუ `25` frontier წერტილია ისეთი, რომელსაც `G0` არასდროს დაწერდა.
> მათგან `12` სხვა world-ის natural writing-ია; დანარჩენ `13`-ს კი ატლასში **ვერცერთი** world ბუნებრივად
> არ წერს — ისინი Pareto-optimal ჩაწერებია, რომლებსაც ვერცერთი კონვენციის ჩვევა არ აწარმოებს.** იმ `16`
> object-იდან, რომელზეც რომელიმე world `G0`-ისგან განსხვავებულად წერს, `12` იძლევა იმ თორმეტიდან ერთს;
> სამღერძიან ნაკრებზე ეს რიცხვი `16`-იდან `7`-მდე ეცემა.

ამ ბლოკის ადრინდელი რედაქცია `12`-ს იძლეოდა როგორც პასუხს კითხვაზე „რამდენს არ დაწერდა `G0`". ეს არის
იმ frontier წერტილების რაოდენობა, რომლებიც **სხვა world-ის natural writing-ია** — უფრო ვიწრო კითხვა.
დასმულ კითხვაზე პასუხი არის `25`, ხოლო ის `13`, რომელიც ვერცერთი world-ის ჩვევას არ ეკუთვნის, უფრო
ბასრი ნახევარია: სწორედ ისინია ის, რასაც frontier-ის მატარებელი router იგებს იმასთან შედარებით, რომელიც
world-ს ირჩევს და ისე წერს, როგორც ის world წერს.

ისინი ეგზოტიკური არ არიან — ისინი factored ფორმებია:

```text
a * (b + c)                                 where G0 writes  a * b + a * c
(a + b) * (a + b)                           where G0 writes  a * a + 2 * a * b + b * b
a * (x - r) * (x - s)                       where G0 writes  a * x * x - a * (r + s) * x + a * r * s
(x - h) * (x - h) + (y - k) * (y - k)       where G0 writes  x * x - 2 * h * x + h * h + y * y ...
y1 + m * (x - x1)                           where G0 writes  m * x + y1 - m * x1
fa + dfa * (x - a)                          where G0 writes  fa - dfa * a + dfa * x
```

თითოეული მათგანი `G0`-ს bracket-ებს უჯდება, და სწორედ ამიტომ `G0` მას არ წერს; და თითოეული ყიდულობს
იმას, რასაც bracket-ის დათვლა ვერ ხედავს: უფრო მოკლე critical path-ს, live მნიშვნელობების უფრო დაბალ
peak-ს, ან გვერდზე უფრო მეტ წაკითხვად თვისებას. **ეს არის ამ card-ის მთელი შინაარსი.** Router, რომელიც
representation-ებს ერთი რომელიმე საზომით ალაგებს, ამ `25`-ს ვერ მიაღწევს, ხოლო router, რომელიც უბრალოდ
world-ს ცვლის, ვერ მიაღწევს იმ `13`-ს, რომელსაც ვერცერთი world ბუნებრივად არ წერს. მხოლოდ router,
რომელიც frontier-ს ატარებს, მიაღწევს.

## რატომ frontier და არა ranking

Card owner-ის საკუთარი დიზაინია — და მისი წანამძღვარი ერთი წინადადებაა:

> *"There is no abstractly better until we know the objective."*

ოთხმა ადრინდელმა card-მა თითოეულმა იმავე `25` world-ის ranking აწარმოა, და ranking-ები ერთმანეთს
ეწინააღმდეგება: cost (0034, 0037), visibility (0038), depth (0041), peak memory (0044). ექსპერიმენტმა
0043 უკვე იპოვა `300` world წყვილიდან `243` შეუდარებელი, ასე რომ ნაწილობრივი წესრიგი ამ landscape-ის
დადგენილი ფორმაა. ეს card ranking-ს წყვეტს. ყოველი object-ისთვის ის აგებს **ამ object-ის ეკვივალენტური
writing-ების Pareto frontier-ს** ღერძების ნაკრებზე, რომელიც დეკლარირებულია და არა ნაგულისხმევი, და
აღწერს იმას, რისი თქმაც frontier-ს შეუძლია, ranking-ს კი არა.

**აქ არაფერი არ იკუმშება scalar-ად.** არ არის weighted sum, არ არის score და არ არის "best
representation" სვეტი, რადგან წონების არჩევა *არის* objective-ის არჩევა, ხოლო objective სწორედ ის არის,
რაც პროექტმა ჯერ არ იცის. Test ამ არარსებობას ამტკიცებს.

## ოთხი კრიტერიუმი და რომელი card არის თითოეულის მფლობელი

ყოველი საზომი შემოტანილია იმ module-იდან, რომელსაც ის ეკუთვნის, და შემოწმებულია identity-ით და არა
ტოლობით, ასე რომ ხელახალი იმპლემენტაცია test-ს ჩააგდებდა და არა `==`-ს გაივლიდა.

```text
axis         meaning                              imported from        card    direction
brackets     minimal bracket pairs, per world     notational_cost      0034    COST, minimise
depth        critical path of the tree            parallel_worlds      0041    COST, minimise
peak_live    simultaneously live values           memory_ceiling       0044    COST, minimise
visibility   manifest properties, counted         manifest_properties  0038    BENEFIT, maximise
```

**სამი მათგანი cost-ია და ერთი benefit.** მეოთხეზე ნიშნის შეცდომა არაფერს არ ააგდებს და არავითარ ფორმას
არ ცვლის; ის ჩუმად ატრიალებს atlas-ს. მიმართულება ერთ ადგილას არის დეკლარირებული, ერთი function კითხულობს
მას, ხელით აგებული წყვილი, რომელშიც მხოლოდ visibility წყვეტს, მას აფიქსირებს, ხოლო კონტროლი მთელ atlas-ს
ხელახლა უშვებს გამონაკლისის მოხსნით, ისე რომ შეცდომის ზომა გვერდზეა: visibility-ის cost-ად მიჩნევა
სამღერძიანზე `50`-ის ნაცვლად `61` optimal writing-ს დაითვლიდა და ოთხღერძიანზე `59`-ის ნაცვლად `68`-ს.
Control-ის საკუთარი headline ორივე ნიშნის ქვეშ `34`-ია, ასე რომ ნიშნის შეცდომა მხოლოდ კითხვა `3`-ში
უხილავი დარჩებოდა.

მხოლოდ `brackets` არის world-ზე დამოკიდებული; `depth`, `peak_live` და `visibility` tree-ის თვისებებია.
ამიტომ frontier იხაზება **დეკლარირებულ reference world-ში**, და default არის `G0`, რადგან ყველაზე ბასრი
კითხვა კონვენციური world-ის საკუთარ კოორდინატებში ისმება. ქვემოთ ყველა `25` არის swept.

## Writing-ების სივრცე და ზღვარი, რომელიც არ დაწესებულა

სივრცე 0039-ისაა, მთლიანად შემოტანილი და არა ხელახლა ჩამოყალიბებული: ყოველი დეკლარირებული writing-ის
ყოველი parenthesization, ზუსტი რაციონალური probe ორ დეკლარირებულ წერტილში, რომელსაც მხოლოდ გამორიცხვა
შეუძლია, და SymPy, რომელიც ყოველ გადარჩენილს ადასტურებს.

```text
declared writings                                      50
full parenthesization space                       1510820   trees, NO bound applied
trees probed                                      1510820   equal to the space, asserted
survived the exact-rational probe                     667
same-object writings confirmed by SymPy               667
(representation, world) cells                       16675
```

**ამ card-ში არსად არ არის დეკლარირებული threshold.** ყოველი word-ის Catalan სივრცე სრულად ჩამოთვლილია,
`trees_probed` უდრის `space_total`-ს, და test ამ ტოლობას ამტკიცებს, რათა მტკიცება იმისა, რომ ნაწილი
გავზომეთ, ჩუმად ვერ გავიდეს. Probe-მ არაფერი გამორიცხა ისეთი, რასაც SymPy დატოვებდა: `667` გადარჩენილი,
`667` დადასტურება. ამ ექსპერიმენტს ზღუდავს corpus და ენა, ორივე დასახელებულია შეზღუდვებში, და არცერთი
არაა რიცხვი, რომლის აწევაც შეიძლებოდა.

## Sample size-ები: object, writing და cell სამი სხვადასხვა რიცხვია

```text
objects                                                34
declared writings                                      50
equivalent writings (representations)                 667
worlds                                                 25
cells = writings x worlds                           16675
```

ისინი ცალკე test-ებში ცალკე სახელებით არის დაფიქსირებული. ექსპერიმენტი 0047 უარყოფილი იქნა იმის გამო, რომ
cell რაოდენობებს აქვეყნებდა იქ, სადაც object რაოდენობები იყო მოთხოვნილი, ხოლო test, რომელიც მათ ერთად
დააფიქსირებდა, ამ ჩანაცვლებას ვერ დაიჭერდა. **ამ report-ში არსად არცერთი world multiplier არ აღწევს
object რაოდენობამდე.**

## Null model

Object, რომლის ყველა writing ერთსა და იმავე კრიტერიუმების ვექტორს იზიარებს, არავითარ frontier
ინფორმაციას არ ატარებს: მისი frontier არის ყველაფერი და არაფერი არაა dominated. ეს object-ები
გამოკლებულია, სანამ რომელიმე rate აიღება.

```text
objects                                                34
objects with more than one equivalent writing          22   the movable set
objects with a single writing, hence a single vector   12
```

Movability ასევე ღერძების მიხედვითაა, რადგან object შეიძლება ერთზე მოძრაობდეს და მეორეზე არა:

```text
brackets       22 of 34 objects
visibility     18 of 34
depth          13 of 34
peak_live       9 of 34
```

ყოველი rate, რომელიც ქვესიმრავლეზეა აღებული, ამბობს რომელ ქვესიმრავლეზე, და ამ report-ში სამი სხვადასხვა
მნიშვნელია: `34` object, `22` movable object და `16` object, რომელზეც რომელიმე world `G0`-ისგან
განსხვავებულად წერს.

## კითხვა 1 და 2: რამდენია dominated და რამდენი რჩება

```text
axis set                    writings   optimal   dominated   dominated share
brackets, depth, visibility      667        50         617          0.925037
all four                         667        59         608          0.911544
```

მხოლოდ movable ნაკრებზე, რაც პატიოსანი მნიშვნელია:

```text
axis set                    writings   optimal   dominated   dominated share
brackets, depth, visibility      655        38         617          0.941985
all four                         655        47         608          0.928244
```

**ერთი object ატარებს writing-ების სამ მეოთხედს.** `binomial_cube`-ს აქვს `667`-იდან `502`, წილი
`0.752624`, რადგან მისი expanded writing არის `13` operator-იანი word, რომლის Catalan სივრცე `742900`
tree-ია. მისი frontier არის `3`. ამიტომ ამ report-ში ყოველი გაერთიანებული მაჩვენებელი დაბეჭდილია
per-object მაჩვენებლის გვერდით, და per-object ცხრილი სრულად არის მოცემული.

```text
object                        writings   optimal 3   optimal 4   dominated 4
calibration_quadratic                5           3           3             2
distributive_law                     2           1           2             0
binomial_square                      5           2           2             3
difference_of_squares                2           1           1             1
difference_of_cubes                  6           1           1             5
sum_of_cubes                         5           1           1             4
quadratic                           10           2           2             8
binomial_cube                      502           3           3           499
perfect_square_trinomial             5           3           3             2
line                                 3           1           2             1
circle                              37           5           5            32
ellipse                              4           1           3             1
hyperbola                            4           1           3             1
parabola                            42           4           4            38
distance_components                  1           1           1             0
slope                                1           1           1             0
midpoint                             1           1           1             0
triangle_area                        2           1           1             1
trapezoid_area                       5           1           2             3
pythagorean_form                     1           1           1             0
difference_quotient                  2           1           2             0
product_rule                         1           1           1             0
quotient_rule                        3           1           1             2
chain_rule                           1           1           1             0
linear_approximation                 2           1           2             0
taylor_first_term                    1           1           1             0
taylor_second_term                   5           2           2             3
riemann_sum_term                     2           1           1             1
dot_product                          1           1           1             0
determinant_2x2                      1           1           1             0
linear_combination                   1           1           1             0
squared_norm                         2           1           1             1
matrix_vector_component              1           1           1             0
cramer_numerator                     1           1           1             0
```

## კითხვა 3: control არასდროს არის dominated და მიზეზი ერთი ღერძია

```text
objects where G0's own writing is ON the frontier       34   of 34
objects where G0's own writing is dominated              0
```

**ეს პასუხი იძულებითია და სწორედ ასე უნდა წაიკითხოს.** სამივე დანარჩენი ღერძი პასუხს არაფერს მატებს,
რადგან ყველა `34` object-ში writing, რომელსაც `G0` ითხოვნის გარეშე ირჩევს, არის **bracket ღერძის
უნიკალური მინიმუმი მთელ `667`-writing-იან სივრცეზე**. ვერაფერი ვერ იქნება არანაკლებ იაფი და სხვაგან
უკეთესი — როცა სხვა არაფერია იმდენად იაფი. დაკვირვება ტავტოლოგია არ არის, რადგან `G0` object-ის
*დეკლარირებულ* writing-ებს შორის ირჩევს, ხოლო სივრცე ყოველ სხვა parenthesization-საც ინახავს, მაგრამ ამ
დაკვირვების პირობებში headline მხოლოდ `brackets`-იდან გამომდინარეობს. ეს არის მტკიცებულება bracket
ღერძის შესახებ და სხვა არაფრის შესახებ.

კითხვის ინფორმაციული ვერსია ისაა, თუ რა ხდება, როცა იგივე ჩვევა სხვა world-ის bracket-ებში ფასდება. იქ
უნიკალურობა ყველა `24`-ში ირღვევა:

```text
reference world       objects where G0's writing is the unique bracket minimum
G0                        34
G17                       31   it still attains the minimum in all 34, but ties in 3
G18                       31
G14                       29
G16                       26
G02, G08, G11             15
```

სადაც ტოლობა ჩნდება, დანარჩენ სამ ღერძს გადაწყვეტს. `G17`-ის ქვეშ კონვენციური expanded quadratic და
factored quadratic ერთსა და იმავე `2` bracket-ს ჯდება, ხოლო factored writing ყველაფერ დანარჩენში მკაცრად
უკეთესია:

```text
G17    (a * x * x - a * (r + s) * x) + a * r * s     brackets 2   depth 5   peak 3   visible 0
G17    a * (x - r) * (x - s)                         brackets 2   depth 3   peak 3   visible 3
```

ასე რომ კონვენციური writing არის **dominated**. `25` reference world-ზე control frontier-ზე ხვდება `34`
object-იდან `29`-სა და `34`-ს შორის.

## კითხვა 4: თორმეტი writing, რომელსაც კონვენციური world მაგიდაზე ტოვებს

მნიშვნელი არის ის `16` object, რომელზეც სულ ცოტა ერთი world-ის natural writing `G0`-ისგან განსხვავდება.
მათგან `12` ალტერნატივა Pareto-optimal-ია `G0`-ის საკუთარ კოორდინატებში და `4` არის dominated. ვექტორები
არის `(brackets, depth, peak_live, visibility)`.

```text
calibration_quadratic                                                     8 worlds
  G0    (0, 4, 3, 4)   2 * x * x + 3 * x - 5
  else  (2, 3, 3, 3)   (2 * x + 5) * (x - 1)

distributive_law                                                         12 worlds
  G0    (0, 2, 3, 3)   a * b + a * c
  else  (1, 2, 2, 2)   a * (b + c)

binomial_square                                                          12 worlds
  G0    (0, 4, 3, 4)   a * a + 2 * a * b + b * b
  else  (2, 2, 3, 3)   (a + b) * (a + b)

quadratic                                                                20 worlds
  G0    (1, 5, 3, 0)   a * x * x - a * (r + s) * x + a * r * s
  else  (2, 3, 3, 3)   a * (x - r) * (x - s)

binomial_cube                                                            12 worlds
  G0    (0, 6, 3, 4)   a * a * a + 3 * a * a * b + 3 * a * b * b + b * b * b
  else  (3, 3, 3, 3)   (a + b) * (a + b) * (a + b)

perfect_square_trinomial                                                 12 worlds
  G0    (0, 4, 3, 4)   4 * x * x + 12 * x + 9
  else  (2, 3, 3, 3)   (2 * x + 3) * (2 * x + 3)

line                                                                     16 worlds
  G0    (0, 3, 3, 3)   m * x + y1 - m * x1
  else  (1, 3, 2, 0)   y1 + m * (x - x1)

circle                                                                   12 worlds
  G0    (0, 7, 3, 3)   x * x - 2 * h * x + h * h + y * y - 2 * k * y + k * k
  else  (4, 3, 4, 0)   (x - h) * (x - h) + (y - k) * (y - k)

parabola                                                                 12 worlds
  G0    (0, 6, 3, 3)   a * x * x - 2 * a * h * x + a * h * h + k
  else  (2, 4, 3, 0)   a * (x - h) * (x - h) + k

trapezoid_area                                                           20 worlds
  G0    (0, 3, 3, 3)   a * h / 2 + b * h / 2
  else  (1, 3, 2, 2)   (a + b) / 2 * h

difference_quotient                                                      12 worlds
  G0    (0, 2, 3, 1)   fxh / h - fx / h
  else  (1, 2, 2, 0)   (fxh - fx) / h

linear_approximation                                                     20 worlds
  G0    (0, 3, 3, 3)   fa - dfa * a + dfa * x
  else  (1, 3, 2, 0)   fa + dfa * (x - a)
```

წაიკითხეთ ვექტორები და ნიმუში ერთი და იგივეა, თორმეტჯერ ნათქვამი. ალტერნატივა ყოველთვის მეტ bracket-ს
ჯდება და ყოველთვის იგებს რაღაც სხვაში: `circle` და `parabola` `4` და `2` bracket წყვილს ცვლიან critical
path-ზე, რომელიც `7`-ის ნაცვლად `3`-ია და `6`-ის ნაცვლად `4`; `line`, `trapezoid_area`,
`difference_quotient` და `linear_approximation` ერთ bracket წყვილში ყიდულობენ live მნიშვნელობების peak-ს
`3`-ის ნაცვლად `2`. **კონვენციური convention ცუდად არ წერს. ის ერთ ღერძს ოპტიმიზაციას უკეთებს, ხოლო
დანარჩენ სამს აქვს წერტილები, რომლებსაც ის არ სტუმრობს.**

`peak_live`-ის მოხსნა თორმეტიდან `5`-ს აშორებს და `7`-ს ტოვებს: `calibration_quadratic`,
`binomial_square`, `quadratic`, `binomial_cube`, `perfect_square_trinomial`, `circle` და `parabola`.
ხუთი, რომელიც ცვივა, სწორედ ისაა, ვისი ერთადერთი უპირატესობაც მეხსიერება იყო.

რომელი world-ები აწარმოებენ მათ, ესეც სპექტრია. `G01`, `G02`, `G07`, `G08` და `G11` თითოეული აწარმოებს
`12`-იდან `12`-ს; `G18`, ჩვენივე grouping `+`/`-` ტოლობის `-`-ის სასარგებლოდ გადაწყვეტით, აწარმოებს `1`-ს.

## ნაწილობრივი წესრიგი writing-ებზე

ერთი object-ის writing-ების ყოველი დაულაგებელი წყვილი არის ordered, equal ან incomparable, და სამივე
ჯამდება `C(n, 2)`-მდე თითო object-ზე, რაც მტკიცდება და არა ივარაუდება.

```text
axis set                    pairs   ordered   incomparable   equal   a ranking must invent
brackets, depth, visibility  127423     87981          28653   10789                0.309536
all four                     127423     63407          54768    9248                0.502390
```

**ოთხ ღერძზე სრულ ranking-ს landscape-ის ნახევარზე მეტისთვის წესრიგის გამოგონება მოუწევდა.** ეს იგივე
მტკიცებაა, რაც 0043-მა world-ებზე თქვა, ახლა writing-ებზე ნათქვამი, და უფრო ძლიერია: 0043-მა `300`-იდან
`243` შეუდარებელი იპოვა; აქ მხოლოდ incomparable წილი `0.429813`-ია, ხოლო ზუსტად ტოლი წყვილები კიდევ
`0.072577`-ს ამატებენ, რადგან ranking-ს არც მათი დალაგების საფუძველი აქვს.

გაერთიანებული მაჩვენებელი ერთი object-ის მაჩვენებელია. `binomial_cube` აწვდის ყველა წყვილის `0.986878`-ს,
ამიტომ per-object საშუალო მის გვერდით არის დაბეჭდილი და სწორედ ის არის ციტირებადი რიცხვი, როცა კითხვა
object-ებზეა:

```text
axis set                    per-object mean ordered   incomparable      equal    invent
brackets, depth, visibility                0.772605       0.166829   0.060565  0.227395
all four                                   0.568272       0.386870   0.044857  0.431728
```

ორივე წაკითხვა ერთსა და იმავეს ამბობს სხვადასხვა ზომით და არცერთი არ არის დაფარული.

## ღერძის დამატება: containment აქ სრულდება და კანონი არ არის

Card ითხოვს შემოწმებას, რომ ოთხღერძიანი frontier შეიცავს სამღერძიანს, იმ საფუძვლით, რომ ღერძის დამატებას
frontier-ის მხოლოდ გაზრდა შეუძლია. **ეს მსჯელობა ზოგადად არ არის ვალიდური** — და მიზეზი ტოლობებია: თუ ორი
writing ემთხვევა უფრო მცირე ნაკრების ყოველ ღერძზე და განსხვავდება დამატებულზე, წამგები უფრო დიდ ნაკრებში
dominated ხდება, მცირეში კი არ იყო. ამიტომ containment აქ გაზომვაა და არა თეორემა.

```text
contained for every object                             yes, 34 of 34
objects whose frontier grew                             7
objects unchanged                                      27
objects whose frontier shrank                           0
total growth                                           50 -> 59
pairs at risk, tied on 3 axes and different in peak   1541
of those, the loser sitting on the 3-axis frontier       0
```

`1541` წყვილს შეეძლო მისი დარღვევა და არცერთმა არ დაარღვია. ზოგადი მტკიცება უარყოფილია სწორედ ამავე
corpus-ში, უფრო მცირე ღერძების ნაკრებებზე:

```text
Pareto({depth})              for calibration_quadratic     3 writings
Pareto({brackets, depth})    for calibration_quadratic     2 writings
lost:       2 * (x * x) + (3 * x - 5)   brackets 2, depth 3
beaten by:  2 * x * x + (3 * x - 5)     brackets 1, depth 3
```

ორივე დაკარგული writing გამარჯვებულს depth-ზე ეთანაბრება და bracket-ებზე უთმობს, რაც უხილავია, სანამ
`depth` ერთადერთი ღერძია. ეს აღწერილია როგორც შედეგი და არა როგორც დეფექტი, ხოლო dominance test-ის მკაცრი
ნაწილობრივი წესრიგობა ცალკე მტკიცდება ქვემოთ.

## Sweep-ები

**ღერძების ნაკრები არის პარამეტრი, რომელიც შეიძლებოდა threshold ყოფილიყო**, ამიტომ ყველა `15` არაცარიელი
ქვესიმრავლე გაშვებულია და ქვეყნდება მთელი მესერი და არა ის `2`, რომელსაც card ასახელებს.

```text
axis set                                 writings on the frontier
brackets                                                       34
depth                                                          65
peak_live                                                     475
visibility                                                    179
brackets + depth                                               50
brackets + peak_live                                           43
brackets + visibility                                          37
depth + peak_live                                              66
depth + visibility                                             86
peak_live + visibility                                        162
brackets + depth + peak_live                                   58
brackets + depth + visibility                                  50
brackets + peak_live + visibility                              46
depth + peak_live + visibility                                 93
brackets + depth + peak_live + visibility                      59
```

**მესერი მონოტონური არ არის, და სწორედ ეს არის ის არამონოტონურობა, რომლის ძებნასაც ROADMAP ყოველ card-ს
ავალებს.** იმ ქვესიმრავლეთა წყვილებიდან, სადაც ერთი მეორეს შეიცავს, `26`-ს აქვს SUPERSET უფრო მცირე
frontier-ით. ყველაზე ბასრია `peak_live` მარტო `475`-ზე `brackets + peak_live`-ის `43`-ის წინააღმდეგ,
დანაკარგი `432`: `peak_live` მთელ corpus-ზე მხოლოდ `3` განსხვავებულ მნიშვნელობას იღებს, ასე რომ თითქმის
ყველაფერი მასზე ეთანაბრება და თითქმის არაფერია dominated, ხოლო განმასხვავებელი ღერძის დამატება ტოლობებს
წესრიგად კრავს. **მეტი კრიტერიუმი იძლევა ნაკლებ Pareto-optimal writing-ს ყოველთვის, როცა დამატებული ღერძი
არღვევს იმ ტოლობებს, რომლებსაც ძველები ვერ ხედავდნენ.** ეს რეალური მოხვევაა — და მონოტონური ინტუიცია მას
დამალავდა.

**Reference world არის ერთადერთი მოდელირების არჩევანი, რომელსაც მკითხველი შეიძლება არ დაეთანხმოს**, ამიტომ
ის swept-ია და არა დაცული.

```text
quantity                                       minimum   maximum   at G0
writings optimal, three axes                        46        57      50
writings optimal, four axes                         52        66      59
frontier points G0 would not write, three axes       7        14       7
frontier points G0 would not write, four axes       12        15      12
objects with G0 on the frontier                     29        34      34
```

`G0`-ის საკუთარი კოორდინატები `G0`-ის მიმართ ყველაზე კეთილგანწყობილია: `25`-იდან არსად არ არის იმ frontier
წერტილების რიცხვი, რომლებსაც ის არ დაწერდა, უფრო მცირე, ვიდრე თავად `G0`-თან. ამიტომ headline არის ქვედა
ზღვარი world-ებს შორის და არა ხელსაყრელი შერჩევა.

**ეკვივალენტური writing-ების რაოდენობა მესამე პარამეტრია, რომელიც შეიძლებოდა threshold ყოფილიყო.**
ქვეყნდება მთელი დაკვირვებული დიაპაზონი.

```text
writings   objects   mean share Pareto-optimal
       1        12                    1.000000
       2         7                    0.714300
       3         2                    0.500000
       4         2                    0.750000
       5         6                    0.433300
       6         1                    0.166700
      10         1                    0.200000
      37         1                    0.135100
      42         1                    0.095200
     502         1                    0.006000
```

მრუდი ეცემა, მაგრამ ის **მონოტონური არ არის**: ის ორჯერ იზრდება, `3` writing-იდან `4`-ზე და `6`-იდან
`10`-ზე. ზრდა `4`-ზე არის `ellipse` და `hyperbola`, და ადრინდელი რედაქცია მას ხსნიდა იმით, რომ მათი
ოთხი writing ურთიერთშეუდარებელია — რაც **მცდარია და საკუთარ თავს ეწინააღმდეგება**: ურთიერთშეუდარებლობა
frontier-ზე `4`-ს დატოვებდა და არა `3`-ს. მათი გაზომილი ვექტორებია `(4,4,3,5)`, `(3,4,3,5)`, `(3,4,3,5)`
და `(2,3,4,5)`. პირველი მკაცრად დომინირებულია მეორითა და მესამით — ერთი bracket წყვილით ნაკლები, დანარჩენი
ყველაფერი ტოლი — ხოლო მეორე და მესამე **ტოლია** და არა შეუდარებელი, და სწორედ ამიტომ გადარჩება `3` და არა
`4`. ზემოთ მოცემული per-object ცხრილი ზუსტად ამას ბეჭდავს: `4` writing, `3` optimal, `1` dominated. ორი object ტენდენცია არ არის და report ამას ამბობს; რასაც მრუდი
ნამდვილად ადგენს, არის ის, რომ optimal წილი დიაპაზონზე ორ რიგზე მეტით ეცემა და ჯერ კიდევ ეცემოდა იქ, სადაც
corpus ამოიწურა.

## კონტროლები

```text
round trips witnessed, every writing in every world      16675   failures  0
brackets proved required by deletion                     88171   surplus   0
dominance irreflexive, antisymmetric, transitive           yes
pairs checked for antisymmetry                          127423
triples checked for transitivity, three axes             39321   over 135 distinct vectors
triples checked for transitivity, four axes             131572   over 154 distinct vectors
frontier points found dominated                              0
dominated writings found on a frontier                       0
```

ორივე bridge audit დათვლილია **წინ**: რიცხვები `16675` და `88171` არის round trip-ები და bracket-ის
წაშლები, რომლებიც დაფიქსირდა, და არა contrexample-ები, რომლებიც გამოგვრჩა. Audit, რომელიც მხოლოდ თავის
წარუმატებლობებს აღწერს, ერთნაირად იკითხება იმის მიუხედავად, იმუშავა თუ არა detector-მა.

Transitivity კვანტიფიცირებულია თითო object-ის განსხვავებულ კრიტერიუმების ვექტორებზე და არა მის
writing-ებზე. Dominance მხოლოდ ვექტორის ფუნქციაა, ასე რომ ორი კვანტიფიკაცია ეკვივალენტურია, ხოლო
`binomial_cube`-ზე შეუმცირებელი გავლა იმავე `50` tuple-ის `126` მილიონი შედარება იქნებოდა. განსხვავებული
ვექტორების რაოდენობები მტკიცდება, რათა შემცირება შემოწმებადი იყოს.

**Mutation testing, tree-ის იზოლირებულ ასლზე და არასდროს სამუშაო tree-ზე.** `pareto_atlas.py`-ზე
გამოყენებულია `22` mutant: benefit ნიშნის ინვერსია, dominance-ის არამკაცრად ქცევა, cost მიმართულების
გადაბრუნება, frontier-იდან self-exclusion-ის მოხსნა, control-ის writing-ის ალტერნატივებში ჩათვლა,
შექმნილ წერტილებზე frontier ფილტრის გამოტოვება, ყოველი object-ის movable-ად გამოცხადება, writing
სივრცის დეკლარირებულ tree-მდე შეკვეცა, minimality და round-trip detector-ების გამორთვა, normalisation-ში
benefit ღერძის მოხსნა, `depth`-ისა და `peak_live`-ის შენაცვლება, ტოლი წყვილების ordered-ად ჩათვლა,
frontier-ების არასწორი world-ის key-ით caching და pool startup-ის შემცირება. `20` მოკლულია. `2` გადარჩა
და ორივე ეკვივალენტური mutant-ია: თითოეული ცარიელს ხდის boolean დროშას, რომლის ფაქტიც იმავე test-ში
ლიტერალური მტკიცებით დამოუკიდებლად არის დადგენილი. კიდევ ორი mutant გადარჩა პირველ გავლაზე, დაფიქსირდა და
ახლა მოკლულია იმ test-ებით, რომლებიც სწორედ მათ საპასუხოდ დაიწერა.

## Multicore

ამ card-ის დომინანტური ეტაპი მისი საკუთარი არ არის: ის არის 0039-ის `1510820` tree-ის ჩამოთვლა, რომელიც
შემოტანილია და რომელიც process-ებზე მიმდინარეობს 0039-ის საკუთარი გაზომილი გადაწყვეტილებით. ეტაპი,
რომელსაც ეს card ამატებს, არის `16675`-უჯრიანი profile grid, და მისი გზა გაზომილია და არა ნავარაუდევი.

```text
cores observed                                  16
workers, with 2 cores of headroom               12
chunks                                          44
measured seconds per cell, floor          0.000057
measured pool startup, floor                   0.9   seconds
crossover, from those two floors              17225   cells
this corpus                                   16675   cells
policy decision                          sequential
```

იატაკის მნიშვნელობებია დეკლარირებული და არა ტიპური, რადგან უფრო მცირე startup და უფრო იაფი უჯრა სწორედ ის
წაკითხვებია, რომლებიც pool-ს ეხმარება, და pool მაინც აგებს. ზღვარი თხელია და ასეც არის აღწერილი: `16675`
crossover-ის `17225`-ის წინააღმდეგ არის გზის `0.968`, ასე რომ ნახევრით უფრო დიდი corpus გადაწყვეტილებას
გადააბრუნებდა.

`parallel_decision` ორივე გზას ერთსა და იმავე სამუშაოზე ზომავს და ამოწმებს, რომ ისინი თანხმდებიან. ცხრა
გაშვება დაფიქსირდა მაშინ, როცა იმავე მანქანაზე კიდევ ორი card მუშაობდა, და სწორედ ამიტომაა სპექტრი ფართო:

```text
sequential   parallel   speedup
    0.9427     1.1593     0.813
    0.9436     1.2916     0.731
    1.0616     1.8488     0.574
    2.0620     1.6246     1.269
    2.6274    14.5230     0.181
    3.8235     8.8236     0.433
    4.4718    32.2160     0.139
    4.6591    16.6648     0.280
    7.9337    37.7953     0.210
```

Pool აგებს `9`-იდან `8`-ზე და იგებს ერთხელ — `1.269`-ით — ყველაზე ნაკლებად დატვირთულ გაშვებაზე. ორივე გზა
ყოველ გაშვებაზე იდენტურ grid-ს აწარმოებს, რაც test suite-ში მტკიცდება, ასე რომ გადაწყვეტილება მხოლოდ
სისწრაფეს ცვლის და არასდროს იმას, რაც იზომება. **Sequential გზა ვალიდური შედეგია, როცა გაზომვა ასე ამბობს,
და აქ ის ასე ამბობს თხელ ზღვარზე, რომელიც დაბეჭდილია და არა დამალული.**

## შეზღუდვები

- **Writing-ების სივრცე არის ერთი token word-ის parenthesization-ები.** კომუტაციური გადალაგებები scope-ს
  გარეთაა: `a * b + a * c` და `a * c + a * b` სხვადასხვა word-ია, და ეს ექსპერიმენტი word-ს არასდროს
  ტოვებს. აქ აღწერილი ყოველი frontier არის frontier ხელახალ bracket-ირებაზე, და ეკვივალენტური writing-ის
  უფრო ფართო გაგებას მასზე მეტი წერტილი ექნებოდა.
- **Visibility არის 0038-ის დეკლარირებული წესები და სხვა არაფერი.** თვისება manifest-ია, როცა
  დეკლარირებული shape წესი დაწერილ ფორმაზე ირთვება. ლექსიკა ფორმებს შორის ნეიტრალური არ არის:
  `monomial_sum` შვიდი თვისებიდან ოთხს ატარებს და `factored` ორს, ასე რომ writing, რომელიც შლის, ნედლ
  დათვლაზე კონსტრუქციულად უფრო მაღალ ქულას იღებს. აქ დათვლა ღერძად გამოიყენება და არასდროს როგორც
  მტკიცება იმისა, თუ რამდენ მათემატიკას ავლენს ფორმა.
- **`depth` და `peak_live` სტრუქტურული ზღვრებია და არა runtime-ები.** `depth` არის critical path და
  `peak_live` არის Sethi-Ullman register number, რომელიც ითვლის მნიშვნელობებს და არა bytes-ს. არცერთი არ
  არის დროში გაზომილი, და ამ report-ში არაფერია performance მტკიცება.
- **Corpus ხელით არის შერჩეული.** ეს არის 0038-ის `34` object `50` დეკლარირებულ writing-ში: 0037-ის
  დასახელებული კანონები პლუს calibration quadratic. `34`-იდან `12`-ს აქვს ერთადერთი ეკვივალენტური writing
  და საერთოდ ვერ ატარებს frontier ინფორმაციას, ხოლო ერთი object აწვდის `667` writing-იდან `502`-ს. ჯამები
  ამ განაწილებით არის ფორმირებული და ყოველი rate თავისი მნიშვნელით არის დაბეჭდილი.
- **Semantic key-ის domain კომპონენტი ინერტულია** (`NF-2026-00005`). `canonical.py` ყოველი
  expression-ისთვის `domain`-ში ლიტერალ `"R"`-ს წერს, ასე რომ ოპერატიული დისკრიმინაცია იმ
  ეკვივალენტობაში, რომელსაც writing-ების სივრცე ეყრდნობა, არის `(canonical form, excluded points)`. ამ
  card-ში არაფერია დამოკიდებული `domain`-ის ცვალებადობაზე, მაგრამ key უფრო სუსტია, ვიდრე მისი სახელი
  გვთავაზობს, და ეს განცხადება აქ ეკუთვნის.
- **Reference world მოდელირების არჩევანია.** მხოლოდ `brackets` არის world-ზე დამოკიდებული, ასე რომ
  frontier ერთი world-ის bracket კოორდინატებში იხაზება. `G0` არის default და ყველა `25` არის swept; ამ
  report-ის ყოველი headline ამ არჩევანთან ერთად მოძრაობს და დიაპაზონი მის გვერდით ქვეყნდება.
- **`G0`-ის natural writing არის 0038-ის განსაზღვრება**, object-ის დეკლარირებული writing-ებიდან ყველაზე
  იაფი, ტოლობები დეკლარირებული რიგით გადაწყვეტილი. იმის სხვა განსაზღვრება, თუ რას დაწერდა world
  ითხოვნის გარეშე, კითხვა `3`-ს და კითხვა `4`-ს გადაანაცვლებდა, და ეს ალტერნატიული წაკითხვა აქ არ არის
  გაზომილი.

## Evidence-ის კლასიფიკაცია

- Frontier-ების ზომები, dominated რაოდენობები, წყვილთა კლასები, ღერძების მესერი, world sweep და ზომის
  მრუდი დეკლარირებულ corpus-ზე executable **observations** არის.
- ის `12` frontier წერტილი, რომელსაც `G0` არ წერს, არის **observations**: თითოეული render-დება, ხელახლა
  parse-დება და თავისი ვექტორით იბეჭდება, და თითოეული არის same-object სივრცის წევრი, დადასტურებული SymPy-ით.
- Dominance-ის მკაცრი ნაწილობრივი წესრიგობა და სამღერძიანი frontier-ის ოთხღერძიანში ჩართულობა გამოთვლილ
  მიმართებაზე **observations** არის, მტკიცდება და არა ივარაუდება.
- მტკიცება იმისა, რომ ღერძის დამატებამ შეიძლება frontier არ გაზარდოს, არის **structural argument** ამ
  corpus-ის შიგნით გაზომილი მოწმით; ის ფორმულირებულია როგორც Pareto dominance-ის თვისება ტოლობების ქვეშ და
  არა როგორც ფაქტი notation-ის შესახებ.
- ის, რომ კითხვა `3`-ის პასუხი bracket ღერძით არის იძულებული, არის **observation** გაცხადებული
  შედეგით: ეს არის მტკიცებულება `brackets`-ის შესახებ და სხვა არაფრის შესახებ.
- Notation-ის შესახებ ზოგადი კანონი არ არის claimed. Atlas არის ნაწილობრივი წესრიგი `34` ხელით შერჩეული
  object-ის writing-ებზე ერთ operator ნაკრებში.

## ვალიდაცია

```text
1187 passed, 2 skipped
```

ამ card-ის `38` test აფიქსირებს ყოველ headline-ს ლიტერალად, object რაოდენობებსა და cell რაოდენობებს ცალკე
test-ებში ინახავს, ამტკიცებს მკაცრ ნაწილობრივ წესრიგს გამოთვლილ მიმართებაზე, აფიქსირებს benefit ნიშანს
ხელით აგებულ წყვილზე, და ამოწმებს, რომ sequential და parallel grid-ები იდენტურია.
