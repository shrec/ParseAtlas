# ParseAtlas ექსპერიმენტი 0052: precedence რიცხვია, და რა ხდება, როცა ის ვექტორია

## რას ყიდულობს მეორე განზომილება პირველთან შედარებით

**ის ყიდულობს `17131` ახალ კლას-გამოჩენას იმ corpus-ის `3125` source-ზე, სადაც პირველმა გაფართოებამ
ვერაფერი იყიდა — მათგან `12302` ობიექტად განსხვავებულია.**

ორივე რიცხვი მოცემულია, რადგან ისინი სხვადასხვა კითხვას პასუხობენ, ხოლო ამ სტრიქონის ადრინდელი
რედაქცია მხოლოდ პირველს იძლეოდა და მას განსხვავებულ ობიექტებს უწოდებდა, რაც მას `39%`-ით ბერავს.
`17131` არის source-ებზე ჯამი იმ კლასებისა, რომლებსაც წყვილი აღწევს და associativity არა — ეს არის
ის კონვენცია, რომელსაც ექსპერიმენტი 0030 იყენებდა და რომელიც ქვემოთ სვეტებს შედარებადს ხდის.
გლობალურად განსხვავებულად დათვლისას ჯამებია `8422` precedence-ისთვის, `8422` associativity-სთვის და
`20724` წყვილისთვის, ანუ მოგება არის `12302`. **verdict ორივე წაკითხვაში გადარჩება, და 0030-ის ნულიც:
`8422` უდრის `8422`-ს გლობალურადაც.**

ექსპერიმენტმა 0030 associativity მეორე grammar ღერძად დაამატა და `3125`-expression-იან
0024 corpus-ზე ორმოცდაათი პროცენტით მეტი სინტაქსი და ნული ახალი მათემატიკა დააფიქსირა. ეს
ექსპერიმენტი სკალარულ binding power-ს წყვილით ცვლის და იმავე corpus-ს იმავე semantic key-ში ატარებს:

```text
0024 corpus, 3125 expressions        precedence     + associativity      binding-power pair
AST forms                                 22500              33750                   77500
semantic classes                          14175              14175                   31306
new classes over the middle column                               0                   17131
sources gaining a class                                          0                    1750
```

პირველი ორი სვეტი 0030-ის საკუთარი რიცხვებია, აქ ციფრამდე გამეორებული. მესამე ის არის, რასაც
operator-ზე ერთი დამატებითი კომპონენტი აღწევს. `14175` class ხდება `31306`, ანუ `2.209`-ჯერ მეტი,
და `3125` source-იდან `1750` — მათი `56.000` პროცენტი — ატარებს reading-ს, რომელსაც
`precedence x associativity` registry-ის ვერც ერთი grammar ვერ აწარმოებს.

ეს არ არის უფრო დიდი სივრცე, რომელიც იმავეს პოულობს მეტი რაოდენობით. ეს სხვა სახის თავისუფლებაა,
და operator support-ის მიხედვით სტრატიფიკაცია ამას ამბობს:

```text
support             expressions   precedence   + associativity      pair       new
{* + -}                    1875         7875              7875     22125     14250
{* + - /}                  1250         6300              6300      9181      2881
```

ორივე ფენა იზრდება, და უფრო პატარა support უფრო მეტად — **მაგრამ ეს ის კონტროლი არაა, რომლადაც ის
დაიწერა.** parser-ების სივრცე ორივე ფენაში იგივე `6902`-ია, ამიტომ მათი შეფარდებითი ზრდა ვერაფერს
ამბობს იმაზე, ზრდა სივრცის გაფართოებაა თუ არა. ნამდვილი კონტროლი ქვემოთაა: **ყოველი ერთ-operator-იანი
ფენა `0`-ს იძენს, სამივე მათგანი**, იმავე `6902` parser-ით. ამ corpus-ს ერთ-operator-იანი ფენა არ აქვს,
და სწორედ ამიტომ კონტროლი იქ ცხოვრობს და არა აქ.

## მიზანი

owner-მა იკითხა, შესაძლებელია თუ არა არა-ბრტყელი modelling და არსებობს თუ არა სამგანზომილებიანი
გზები. `parseatlas.grammar.Grammar.binding_power` აბრუნებს `dict[str, int]`-ს — თითო operator-ზე
თითო მთელი რიცხვი — და სწორედ ეს ერთი რიცხვია პროექტის ბრტყელობა. repository-ის ყოველი შედეგი,
სულ 25 worlds, უფრო მდიდარი სივრცის ჭრილია იმ სიბრტყით, სადაც ეს რიცხვი სკალარულია.

განზოგადება კლასიკურია და სწორედ ის არის, რასაც Pratt parsing უკვე იყენებს:

```text
1D    binding_power[op] = n                 the Generation 1 model, 25 worlds
2D    binding_power[op] = (left, right)     precedence and associativity, unified
3D    plus a prefix binding power           unary operators integrated
```

card-მა ასევე პროექტის საკუთარ წარსულზე დააყენა მტკიცება. binding-power წყვილში associativity
ცალკე პარამეტრი არ არის, ის წყვილის შიგნით რიგია; თუ ეს სწორია, ექსპერიმენტი 0030, რომელიც
associativity-ს ცალკე ღერძად განიხილავდა, წარმოებულ პარამეტრს დამოუკიდებელივით ცვლიდა. ეს მტკიცება
ქვემოთ მოწმდება და არა იგულისხმება, ხოლო განაჩენს ორი ნახევარი აქვს, რომლებიც ერთად უნდა ითქვას.

```text
half one    0030's registry embeds.  Associativity really is the order within the pair.
half two    the pair reaches parses that registry cannot.  It is a proper subspace.
```

## Space structure

### parser

`VectorParser` სახელმძღვანელოს Pratt loop-ია. ის `parseatlas.parser.Parser`-ისგან ერთი
სტრიქონით განსხვავდება:

```text
Generation 1     while power[op] >= minimum:  right = expression(power[op] + 1)
vector           while left[op] >  minimum:   right = expression(right[op])
```

`left = 2p`-სა და `right = 2p + 1`-ის ჩასმა პირველს ზუსტად მეორედ აქცევს, რადგან `p >= m` იგივე
მტკიცებაა, რაც `2p > 2m - 1`. ესე იგი Generation 1 grammar-ის 2D image ცვლადების გადანაცვლებაა
და არა მორგება, ხოლო `agreement_audit` არის შემოწმება, რომ არითმეტიკა არსად ჩამოცურდა.

### associativity არის რიგი წყვილის შიგნით

`a - b - c` მარცხნივ იშლება, როცა `left` არ აღემატება `right`-ს იმ operator-ისთვის, და მარჯვნივ,
როცა `left` აღემატება `right`-ს. operator-ის შთანთქმის შემდეგ parser მინიმუმს მარჯვენა
კომპონენტიდან იღებს, ამიტომ ტოლი power-ის operator ან loop-ს რჩება, ან რეკურსია შთანთქავს, და
სწორედ ეს ერთი შედარებაა associativity მთლიანად. კონვენციურად `(n, n+1)` მარცხენაა და `(n+1, n)`
მარჯვენა: იგივე ორი რიცხვი, სხვა რიგით ჩაწერილი.

### vector grammar-ის ქცევა boolean matrix-ია

რეკურსიაში შესვლა ხდება მხოლოდ `0`-ით — ზედა დონეზე და გამხსნელი ფრჩხილის შემდეგ — ან რომელიღაც
operator-ის მარჯვენა კომპონენტით. როცა ყოველი `left` სულ მცირე `1`-ია, ზედა დონის შემოწმება
ყოველთვის გადის, ასე რომ მთელი parser განისაზღვრება ამით:

```text
M[a][b] = left(a) > right(b)
```

და ამ matrix-ის ყოველი უჯრა იკითხება ორ-operator-იანი word-ით `x b y a z`, რომელიც მარჯვნივ
დახრილად იშლება ზუსტად მაშინ, როცა უჯრა ჭეშმარიტია. *განსხვავებული matrix* და *განსხვავებული
parser* ამიტომ ერთი და იგივეა, და სწორედ ეს ხდის behavioural quotient-ს ზუსტს და არა შერჩევითს.

### ჩამოთვლის bound გაჯერდება

matrix რეალიზებადია ზუსტად მაშინ, როცა სიმრავლეები `S(a) = {b : left(a) > right(b)}` ჩართვის
მიმართ ჯაჭვს ქმნიან, რადგან `left` მნიშვნელობები სრულად დალაგებულია. `m`-ელემენტიანი სიმრავლის
`m` ქვესიმრავლის ჯაჭვი რეალიზდება `left` მნიშვნელობებით `2..m+1`-ში და `right` მნიშვნელობებით
`1..m+1`-ში, ამიტომ `bound = m + 1` უკვე აღწევს ყველა parser-ს, რაც კი არსებობს. scan ამას
დააკვირდება და არა ამტკიცებს:

| bound | raw assignments | distinct parsers |
| --- | --- | --- |
| 2 | 256 | 226 |
| 3 | 6561 | 2726 |
| 4 | 65536 | 6326 |
| 5 | 390625 | 6902 |
| 6 | 1679616 | 6902 |
| 7 | 5764801 | 6902 |

ამიტომ bound **არ** არის computational limit, რომელზეც პასუხი იკითხება. `5`-ის შემდეგ raw
assignment count კიდევ `14.76`-ჯერ იზრდება, behavioural count კი საერთოდ არ იძვრის.

ორი რიცხვი გვერდიგვერდ უნდა წაიკითხოს. გამაჯერებელ bound-ზე `390625` assignment ასახელებს `6902`
parser-ს, ესე იგი *კოორდინატები* `56.596`-ჯერ რედუნდანტულია, თავად სივრცე კი არა: ვექტორებზე
ჩამოთვლის უმეტესი ნაწილი უკვე ნაპოვნი parser-ების ხელახლა დასახელებაზე იხარჯება.

### სივრცეების ზომები

```text
operators m                    1       2       3       4
distinct parsers, 2D           2      14     230    6902
distinct parsers, 3D           4      46    1066   41506
```

## Corpus

reach sweep უცვლელად იყენებს ექსპერიმენტების 0020, 0023 და 0030 word family-ს: ოთხი operator-ის
alphabet-ზე ყოველი `k` სიგრძის word `k = 2..6`-სთვის, canonical leaves `a, b, c`, და მნიშვნელად
parenthesizations-ის სრული Catalan სიმრავლე. ეს არის `5456` word და `587616` word-and-tree წყვილი.

conservative-extension audit `36` source-ზე გადის: 0020-ის ექვსი expression, 0030-ის split
corpus-ის ხუთი, მისი chain probe-ის ათი, 0017 corpus-ის ხუთი, და კიდევ თხუთმეტი, რომლებიც
ჩალაგებულ ფრჩხილებს, წილადებსა და რიცხვით leaf-ებს ატარებენ, ასე რომ მტკიცება მხოლოდ ბრტყელ
word-ებზე არ მოწმდება.

semantic corpora 0030-ის საკუთარია, ასე რომ class count-ები მის რიცხვებთან ერთ სვეტში დგებიან:

```text
0017 corpus              5 expressions
0020 corpus              6 expressions
0024 restriction probe  10 expressions
chain probe             10 expressions
0024 corpus           3125 expressions      corpus_matrix.generate_corpus()
```

## დაკვირვებული შედეგები

### conservative-extension audit

Generation 1-ის 25 grammar-იდან ყოველ ერთს აქვს 2D image, და მისი parse ყოველ source-ზე უჯრა-უჯრა
ემთხვევა `parseatlas.parser.parse`-ს:

```text
grammars                    25
sources                     36
cells                      900
agreements                 900
divergences                  0
grammars with no image       0
```

image-ები აშკარადაა ჩამოწერილი. სკალარი level view-დან იკითხება, ამიტომ tied control grammar `G0`
ორივე თავის tie-ს ინარჩუნებს:

| grammar | plus | minus | times | over |
| --- | --- | --- | --- | --- |
| G0 | (2, 3) | (2, 3) | (4, 5) | (4, 5) |
| G01 | (8, 9) | (6, 7) | (4, 5) | (2, 3) |
| G02 | (8, 9) | (6, 7) | (2, 3) | (4, 5) |
| G03 | (8, 9) | (4, 5) | (6, 7) | (2, 3) |
| G04 | (8, 9) | (2, 3) | (6, 7) | (4, 5) |
| G05 | (8, 9) | (4, 5) | (2, 3) | (6, 7) |
| G06 | (8, 9) | (2, 3) | (4, 5) | (6, 7) |
| G07 | (6, 7) | (8, 9) | (4, 5) | (2, 3) |
| G08 | (6, 7) | (8, 9) | (2, 3) | (4, 5) |
| G09 | (4, 5) | (8, 9) | (6, 7) | (2, 3) |
| G10 | (2, 3) | (8, 9) | (6, 7) | (4, 5) |
| G11 | (4, 5) | (8, 9) | (2, 3) | (6, 7) |
| G12 | (2, 3) | (8, 9) | (4, 5) | (6, 7) |
| G13 | (6, 7) | (4, 5) | (8, 9) | (2, 3) |
| G14 | (6, 7) | (2, 3) | (8, 9) | (4, 5) |
| G15 | (4, 5) | (6, 7) | (8, 9) | (2, 3) |
| G16 | (2, 3) | (6, 7) | (8, 9) | (4, 5) |
| G17 | (4, 5) | (2, 3) | (8, 9) | (6, 7) |
| G18 | (2, 3) | (4, 5) | (8, 9) | (6, 7) |
| G19 | (6, 7) | (4, 5) | (2, 3) | (8, 9) |
| G20 | (6, 7) | (2, 3) | (4, 5) | (8, 9) |
| G21 | (4, 5) | (6, 7) | (2, 3) | (8, 9) |
| G22 | (2, 3) | (6, 7) | (4, 5) | (8, 9) |
| G23 | (4, 5) | (2, 3) | (6, 7) | (8, 9) |
| G24 | (2, 3) | (4, 5) | (6, 7) | (8, 9) |

audit თავად მოწმდება იმით, რომ მას divergence-ს უჩვენებენ. განზრახ არასწორი image map, რომელიც
ყოველ წყვილს სხვა რიგით წერს, აიძულებს მას ყველა `25` grammar image-ის გარეშედ დააფიქსიროს; ხოლო
map, რომელიც ყველგან სწორია გარდა plus-ისა და minus-ის გაცვლისა `G07`-ის შიგნით, აიძულებს ზუსტად
`G07` დაასახელოს და დანარჩენი `24` ნულოვან divergence-ზე დატოვოს.

### 0030-ის მტკიცება, გადამოწმებული

მთელი precedence-ზე-associativity registry ჩაიდგმება, control ვარიანტების ჩათვლით:

```text
0030 grammars                       388
sources                               5
cells                              1940
agreements                         1940
divergences                           0
distinct images                     388
```

ესე იგი associativity წყვილის კოორდინატია და არა მის გვერდით მდგომი ღერძი, და 0030 ნამდვილად
წარმოებულ პარამეტრს ცვლიდა. მაგრამ ჩადგმა არ არის სიურექციული, და სწორედ ამ ხარვეზშია შედეგი:

```text
flat grammars, every ordering of levels with a side per level      730
distinct parsers they induce                                       730
distinct parsers a binding-power pair induces                     6902
parsers with no flat description                                  6172
flat fraction                                                  10.577 %
```

აქ აღებული flat family უფრო გულუხვია, ვიდრე ყველაფერი, რაც პროექტს გამოუყენებია: ეს არის ოთხი
operator-ის level-ებად ყოველი დალაგებული დაყოფა — სულ `75` ცალი, `24` strict და `51` tie-ების
მატარებელი — level-ზე side-ით გამრავლებული. ის აღწევს `730` parser-ს. წყვილი აღწევს `6902`-ს.
წყვილის სივრცის parser-ების ცხრა მეათედი ვერ ჩაიწერება *ვერც ერთი* სკალარული precedence-ით და
*ვერც ერთი* associativity-ით.

დამატებითი თავისუფლება მეტი associativity არ არის. ეს არის **ასიმეტრიული ურთიერთქმედება
სხვადასხვა operator-ს შორის**: წყვილს შეუძლია times მარცხნივ plus-ზე მაღლა დააყენოს და მარჯვნივ
დაბლა, რასაც operator-ზე ერთი რიცხვი ვერ იტყვის. times `(10, 1)`-ზე და plus `(2, 3)`-ზე:

```text
a + b * c     ->   a + (b * c)      times behaves as the tighter operator
a * b + c     ->   a * (b + c)      times behaves as the looser operator
```

### Reach 0020-სა და 0030-თან შედარებით

იგივე `k = 2..6` დიაპაზონი, იგივე words, იგივე მნიშვნელი. ground truth სამივე სვეტში რეალური
parsing-ია, ხოლო წყვილის სვეტი `6902` parser-ზე ამომწურავია და არა შერჩევითი:

| k | words | C(k) | trees | precedence | + associativity | pair |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 2 | 32 | 28 | 32 | 32 |
| 3 | 64 | 5 | 320 | 196 | 260 | 284 |
| 4 | 256 | 14 | 3584 | 1252 | 2000 | 2552 |
| 5 | 1024 | 42 | 43008 | 7180 | 14192 | 22160 |
| 6 | 4096 | 132 | 540672 | 37420 | 92504 | 181640 |

პირველი ორი სვეტი 0020-სა და 0030-ს ზუსტად იმეორებს, და სწორედ ამიტომ ენდობა მესამეს.
parenthesization სივრცის coverage-ად:

| k | precedence % | + associativity % | pair % |
| --- | --- | --- | --- |
| 2 | 87.500 | 100.000 | 100.000 |
| 3 | 61.250 | 81.250 | 88.750 |
| 4 | 34.933 | 55.804 | 71.205 |
| 5 | 16.695 | 32.999 | 51.525 |
| 6 | 6.921 | 17.109 | 33.595 |

და როგორც პატიოსანი ფარდობა, precedence ხარვეზის ის წილი, რომელსაც თითო გაფართოება ხურავს:

| k | unreachable before | associativity recovers % | pair recovers % |
| --- | --- | --- | --- |
| 2 | 4 | 100.000 | 100.000 |
| 3 | 124 | 51.613 | 70.968 |
| 4 | 2332 | 32.075 | 55.746 |
| 5 | 35828 | 19.571 | 41.811 |
| 6 | 503252 | 10.946 | 28.658 |

აგრეგატი `k = 2..6`-ზე:

```text
total trees                      587616
precedence reachable              46076      7.841 %
with associativity               108988     18.547 %
with a binding-power pair        206668     35.171 %
unreachable before               541540     92.159 %
unreachable after associativity  478628     81.453 %
unreachable after the pair       380948     64.829 %
associativity recovered           62912     11.617 %   of the gap
the pair recovered               160592     29.655 %   of the gap
```

**პირდაპირი პასუხი, რომელსაც card ითხოვდა: 2D სივრცე მეტს აღწევს, ვიდრე precedence
associativity-სთან ერთად.** ის ხარვეზის `29.655` პროცენტს აღადგენს იქ, სადაც associativity-მ
`11.617` აღადგინა, და `1.896`-ჯერ მეტ tree-ს აღწევს. associativity-ის ᲯᲐᲛᲘ sweep-ის ყოველ უჯრაში
წყვილის ჯამზე ნაკლები ან ტოლია. ჩადგმა სიმრავლურ ჩართვას წინასწარმეტყველებს და ჩართვა ნამდვილად დგას
კონსტრუქციულად, მაგრამ sweep რასაც აფიქსირებს, არის რიცხვების და არა სიმრავლეების შედარება —
`reach_2d` ჯამებს ადარებს და `_reach_pattern` მხოლოდ სიგრძეს აბრუნებს. უფრო ძლიერ დებულებას ჩადგმა
ამართლებს და არა ეს ცხრილი.

`k = 6` არის **computational limit** და ის აქვე სახელდება, სადაც პასუხი იკითხება. sweep არის `5456`
word და `587616` tree; შემდეგი სიგრძე არის `16384` word და `7028736` tree და ის არ გაშვებულა. მის
მიღმა ცნობილია მხოლოდ ქვემოთ მოცემული ჭერის ცხრილი, რომელიც არითმეტიკულია: ის მრუდის მიმართულებას
აფიქსირებს და არა მის ზომას.

expression-ების მიხედვით, 0020-ის ექვს source-ზე:

| expression | k | C(k) | precedence | + associativity | pair |
| --- | --- | --- | --- | --- | --- |
| `a + b*c` | 2 | 2 | 2 | 2 | 2 |
| `a + b + c` | 2 | 2 | 1 | 2 | 2 |
| `2*t + 1 - t/2` | 4 | 14 | 14 | 14 | 14 |
| `a + b*c - d/e` | 4 | 14 | 14 | 14 | 14 |
| `a - b*c + d/e - f` | 5 | 42 | 19 | 24 | 42 |
| `2*x*x + 1 - x/2 + x` | 6 | 132 | 17 | 42 | 74 |

```text
mean precedence coverage        0.6801948051948052      identical to 0020
mean associativity coverage     0.814935064935065       identical to 0030
mean pair coverage              0.9267676767676768
```

`a - b*c + d/e - f` ყველაზე მკვეთრი ერთეული უჯრაა: წყვილის სივრცე აღწევს **ყველა** `42`
parenthesization-ს იმ source-ისთვის, სადაც precedence `19`-ს აღწევდა და associativity `24`-ს.

### რას ყიდულობს მესამე კომპონენტი

prefix operator-ს ერთი operand აქვს და ამიტომ ერთი binding power. მესამე რიცხვის გარეშე ეს power
*წარმოებულია* — ის მხოლოდ operator-ის საკუთარი მარჯვენა კომპონენტი შეიძლება იყოს — და მესამე
განზომილება მას ათავისუფლებს. family იგივე word set-ია, რომელიც ერთ წინმდგომ prefix minus-ს
ატარებს; ასეთი word `C(k+1)` tree-ს უშვებს, Catalan-ის კონვოლუციას.

| k | words | trees per word | trees | derived prefix | free prefix | gained | ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 5 | 80 | 71 | 76 | 5 | 1.0704 |
| 3 | 64 | 14 | 896 | 638 | 736 | 98 | 1.1536 |
| 4 | 256 | 42 | 10752 | 5540 | 6952 | 1412 | 1.2549 |
| 5 | 1024 | 132 | 135168 | 45410 | 62320 | 16910 | 1.3724 |

```text
total trees                146896
derived prefix              51659     35.167 %
free prefix                 70084     47.710 %
gained                      18425
gained, as a fraction of the derived-prefix gap        19.346 %
```

მრუდი **ჯერ კიდევ მოძრაობს**: თავისუფლის შეფარდება წარმოებულთან მონოტონურად იზრდება `1.0704`,
`1.1536`, `1.2549`, `1.3724` მთელ გავლილ დიაპაზონზე და შემობრუნების ნიშანს არ აჩვენებს. იმ
word-ებზე, სადაც prefix არ გვხვდება, მესამე კომპონენტი კონსტრუქციით ინერტულია, და ეს მტკიცდება
და არა მხოლოდ განიხილება — იგივე word ყოველი prefix power-ის ქვეშ იდენტურად იშლება.

### Partial orders: არჩევის ნაცვლად უარის თქმა

მეორე არა-ბრტყელი მიმართულება საერთოდ ვექტორი არ არის. დავუშვათ, რომ ზოგიერთი operator წყვილი
**შეუდარებელია**, ასე რომ შერეული expression სინტაქსურად ორაზროვანია და grammar მას უარყოფს,
reading-ის არჩევის ნაცვლად. `PartialOrderParser` რიცხვით მინიმუმს თავად operator-ით ცვლის და
მიმართებას ეკითხება; შეუდარებელი განაჩენი აგდებს და არ წყვეტს.

სივრცე არის ოთხ operator-ზე ყოველი preorder — tie-ებიც და შეუდარებლობებიც:

```text
preorders                         355
of which total preorders           75      no incomparable pair
of which strict total orders       24      the Generation 1 registry
the antichain                       1      nothing ranked at all
```

25-ვე რეგისტრირებული grammar მის შიგნით total preorder-ებად ზის და `36`-ვე audit source-ზე
`parseatlas.parser.parse`-ს იმეორებს.

0020-ის ექვს expression-ზე, ყველა `355` preorder-ის გასწვრივ:

| incomparable pairs | preorders | cells | refusals | true refusals | over-refusals | silent choices |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 75 | 450 | 0 | 0 | 0 | 375 |
| 1 | 48 | 288 | 158 | 158 | 0 | 82 |
| 2 | 78 | 468 | 323 | 323 | 0 | 67 |
| 3 | 84 | 504 | 378 | 378 | 0 | 42 |
| 4 | 51 | 306 | 238 | 238 | 0 | 17 |
| 5 | 18 | 108 | 87 | 87 | 0 | 3 |
| 6 | 1 | 6 | 5 | 5 | 0 | 0 |

source *არჩევის მატარებელია*, როცა `24` strict grammar მასზე არ თანხმდება: იქ reading, რომელსაც
total order აწვდის, კონვენციაა და არა დასკვნა. ასეთ source-ზე უარი ნამდვილ თვითნებობას იკავებს;
სხვაგან უარი არაფერს იკავებს და over-refusal-ად ითვლება.

```text
cells                              2130
refusals                           1189     55.822 %
true refusals                      1189
over-refusals                         0
refusal precision                 1.000
silent choices                      586     27.512 %   accepted where the 24 disagree
```

იგივე აღრიცხვა `k = 2..4`-ის ყოველ operator word-ზე, რაც `119280` უჯრაა:

| k | words | choice-bearing | cells | refusals | over-refusals | silent choices |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 16 | 12 | 5680 | 1512 | 0 | 2748 |
| 3 | 64 | 60 | 22720 | 9576 | 0 | 11724 |
| 4 | 256 | 252 | 90880 | 47448 | 0 | 42012 |

```text
cells                            119280
refusals                          58536     49.074 %
over-refusals                         0
silent choices                    56484     47.354 %
refusal precision                 1.000
```

**ნული over-refusal `119280` უჯრასა და `2130` corpus უჯრაში.** partial order არასოდეს უარყოფს
source-ს, რომლის reading თავიდანვე თვითნებური არ იყო, რადგან უარი მხოლოდ იქ ჩნდება, სადაც ორი
შეუდარებელი operator უნდა შედარდეს, ხოლო მათი რიგის შეცვლა ზუსტად ის არის, რასაც strict registry
უკვე აკეთებს.

ფასი ფრჩხილებია. `150` კონვენციური reading-იდან თითოეულისთვის — `25` grammar `6` source-ზე —
აღებულია ის უმცირესი ფრჩხილის წყვილთა რაოდენობა, რომელიც ამ reading-ს antichain-ის ქვეშ მაინც
წერს, ამომწურავად მოძებნილი internal node-ების ყოველ ქვესიმრავლეზე და მიღებული მხოლოდ მაშინ, როცა
ჩანაწერი ზუსტად იმავე tree-დ იშლება უკან:

```text
conventional readings                150
still free of brackets                25
needing at least one bracket pair    125     83.333 %
unwritable at any bracket count        0
mean minimum bracket pairs           2.407
maximum minimum bracket pairs            4
sources the antichain refuses            5   of 6
```

ასე რომ გარიგება ორივე მხრიდანაა შეფასებული. partial order ყიდულობს თავისუფლებას თვითნებური
reading-ისგან სრულყოფილი სიზუსტით — ის არაფერს უარყოფს, რაც თვითნებური არ იყო — და იხდის
საშუალოდ `2.407` ფრჩხილის წყვილს თითო კონვენციურ reading-ზე, ისე რომ არაფერი ხდება ჩაუწერელი.

### Null model

ობიექტი პროექტის semantic class-ია, canonical-form-ის, domain-ისა და excluded-points-ის სამეული,
და არა AST. რიცხვები ოთხ უფრო პატარა corpus-ზე, `31` expression:

| corpus | expressions | precedence classes | + associativity | pair | new | sources gaining |
| --- | --- | --- | --- | --- | --- | --- |
| 0017 corpus | 5 | 27 | 27 | 27 | 0 | 0 |
| 0020 corpus | 6 | 50 | 54 | 73 | 19 | 2 |
| 0024 restriction probe | 10 | 22 | 31 | 40 | 9 | 5 |
| chain probe | 10 | 14 | 26 | 30 | 4 | 2 |

```text
new classes over associativity        32
new classes over precedence           57
sources gaining a class                9   of 31
```

operator support-ის მიხედვით სტრატიფიცირებული, სადაც ზრდა, რომელიც მხოლოდ სივრცეა, თავს გამოაჩენდა:

| support | expressions | precedence | + associativity | pair | new |
| --- | --- | --- | --- | --- | --- |
| plus | 1 | 1 | 1 | 1 | 0 |
| minus | 3 | 3 | 6 | 6 | 0 |
| over | 3 | 3 | 5 | 5 | 0 |
| times, plus | 1 | 2 | 2 | 2 | 0 |
| times, minus | 2 | 4 | 7 | 9 | 2 |
| times, over | 1 | 1 | 2 | 2 | 0 |
| plus, minus | 1 | 2 | 3 | 3 | 0 |
| minus, over | 8 | 16 | 27 | 38 | 11 |
| times, minus, over | 2 | 4 | 4 | 4 | 0 |
| plus, minus, over | 2 | 6 | 6 | 6 | 0 |
| all four | 7 | 71 | 75 | 94 | 19 |

ერთ-operator-იანი ყოველი ფენა ვერაფერს იძენს, სამივე მათგანი. ეს ამ სექციის ყველაზე მკვეთრი
სტრუქტურული მტკიცებაა და შემთხვევითი არ არის: ერთი გამეორებული operator ზუსტად ის არის, რასაც
associativity უკვე ამუშავებს, და წყვილი იქ არაფერს ამატებს, რადგან წყვილი იქ *არის*
associativity. ყველაფერს, რასაც მეორე განზომილება ყიდულობს, სულ მცირე ორი operator ტიპი სჭირდება.

სრულ `3125`-expression-იან 0024 corpus-ზე ორი დამკვიდრებული სვეტი 0030-ისას იდენტურად გამოდის,
ხოლო მესამე ამ report-ის დასაწყისია:

```text
                              precedence    + associativity          pair
AST forms                          22500              33750         77500
semantic classes                   14175              14175         31306
new classes                                               0         17131
sources gaining a class                                   0          1750
```

class count `120.854` პროცენტით იზრდება იქ, სადაც წინა გაფართოებამ ის საერთოდ არ დაძრა.

## Multicore დაკვირვება და default path

აქ ყოველი მძიმე გავლა item-ზე დამოუკიდებელი და CPU-bound-ია, ამიტომ ყოველი მათგანი process-ებზე
ნაწილდება — მაგრამ მხოლოდ იმ ზღვრის ზემოთ, რომელიც დაკვირვებულია და არა ნავარაუდევი. worker count
მიიღება დაკვირვებული core count-იდან ერთი core-ის headroom-ით
(`parseatlas.reachability.resolve_workers`) და არასოდეს კონსტანტიდან; `workers=1` სექვენციურ path-ს
აიძულებს, ხოლო აშკარად მითითებული worker count ზღვარს ორივე მიმართულებით უვლის გვერდს.

სამი გამეორება თითო კონფიგურაციაზე ამ 16-core Windows host-ზე, **თითო გამეორება ახალ
interpreter-ში**, ასე რომ ორივე სვეტი იხდის ცივ sympy import chain-ს, median-ებით:

| workload | tasks | sequential | parallel | speedup |
| --- | --- | --- | --- | --- |
| `reach_2d`, k = 5 | 73 | 4.01 s | 6.95 s | 0.58 |
| `reach_2d`, k = 6 | 260 | 24.74 s | 8.73 s | 2.83 |
| `enumerate_2d`, bound 4 | 256 | 11.27 s | 4.91 s | 2.30 |
| `enumerate_2d`, bound 5 | 625 | 62.25 s | 20.35 s | 3.06 |
| `three_d`, k = 3 | 20 | 38.83 s | 57.06 s | 0.68 |
| `three_d`, k = 4 | 71 | 78.10 s | 35.94 s | 2.17 |
| `partial_orders` | 355 | 1.30 s | 2.26 s | 0.58 |
| `null_model` | 31 | 9.36 s | 9.57 s | 0.98 |

ამ ცხრილის პატიოსანი წაკითხვა სამ default-ს იძლევა და არა ერთს, რადგან task count კარგად
წინასწარმეტყველებს მხოლოდ მაშინ, როცა task-ები დაახლოებით ერთნაირად ჯდება:

```text
reach_2d, enumerate_2d, null_model   parallel from 128 tasks   crossover between 73 and 256
three_d                              parallel from  32 tasks   crossover between 20 and  71
partial_orders                       sequential at any count   one task is about 4 ms
```

`partial_orders` ყველაზე ნათელი შემთხვევაა ერთი კონსტანტის წინააღმდეგ. მას `355` task აქვს, ანუ
საერთო ზღვარს კარგად სცილდება, და მათ აღებაზე `1.30` წამს `2.26` წამზე აგებს, რადგან სულ `355`
ერთად ძლივს ერთი წამის parsing-ია, ხოლო `15` spawned interpreter მარტო გაშვებაზე ამაზე მეტს ხარჯავს.
`three_d` საპირისპირო მიმართულების შემთხვევაა: მისი `71` task საერთო ზღვრის ქვემოთაა და მაინც
`2.17`-ჯერ იგებს, რადგან იქ ერთი task `41506` parse-ია. საერთო კონსტანტა არის `128`, სწორედ იქ,
სადაც `parseatlas.associativity.PARALLEL_MINIMUM_ITEMS` დამოუკიდებლად დაისვა იმავე host-ზე.

parallelism მხოლოდ სიჩქარეს ცვლის და არასოდეს იმას, რაც იწარმოება. sequential და parallel path-ები
worker ველის გარდა ერთსა და იმავე dictionary-ს აბრუნებენ, და ეს `reach_2d`-სთვის, `three_d`-სთვის,
`enumerate_2d`-სთვის, `partial_orders`-სთვის და `null_model`-სთვის ცალ-ცალკე მტკიცდება ნებისმიერი
timing-ისგან დამოუკიდებლად.

ამ host-ზე გაფანტვა დიდია და ეს რიცხვები რიგია და არა კონსტანტა: `reach_2d`-ის `k = 6` სექვენციური
გამეორებები იყო `29.76`, `24.74` და `24.57` წამი, ხოლო `enumerate_2d`-ის bound-`5` სექვენციური
გამეორებები `134.07`, `52.83` და `62.25` წამი. სხვა host, ან იგივე host სხვა დატვირთვის ქვეშ,
crossover-ს ანაცვლებს.

## რას არ აწარმოებს ჩამოთვლა

ყოველი შეზღუდვა აქ არის დასახელებული, სადაც პასუხი იკითხება, იმასთან ერთად, რაც მის მიღმა შემოწმდა.

| restriction | what lies past it | does it change the answer |
| --- | --- | --- |
| components bounded by `5` | bounds `6` and `7` were run: `1679616` and `5764801` assignments | no, the parser count stays `6902` |
| integer components only | order alone decides behaviour, so real components add no matrix | no |
| `left` at least `1` | `left`-ის `0` ოპერატორს მოუხმარებელს ხდის ᲧᲝᲕᲔᲚ მინიმუმზე და არა მხოლოდ top level-ზე, ანუ ასეთი grammar უარყოფს ყოველ source-ს, რომელიც მას შეიცავს, ორაზროვანს თუ არა | ეს არაა ის, რასაც partial-order სექცია აფასებს — ის `0` over-refusal-ს აფიქსირებს. მისი გამორიცხვა არაფერს არ ღირს: `right >= 0` და `prefix >= 0` ვერცერთ `m`-ზე ვერცერთ parser-ს არ ამატებს |
| reach sweep stops at `k = 6` | `k = 7` and beyond, ceiling table below | direction is fixed by the ceiling, size is not |
| reach sweep uses flat words | sources with hand-written brackets | the audit and the coverage table include them |
| prefix operator only at the head | interior prefix probe, `8` sources | no, `18` trees become `19` and containment holds |
| partial orders fix associativity left | the same sweep with every side right | no, all refusal counts are identical |
| partial orders rank operator symbols | context-dependent or per-position ranks | outside the vector and the preorder model alike |
| null model uses five corpora | other corpus families | unknown, and the corpora that gain nothing are named |

სტრუქტურული ჭერი არითმეტიკულია და გაშვებას არ საჭიროებს. source თითო განსხვავებულ parser-ზე **არაუმეტეს ერთ**
tree-ს აღწევს, ამიტომ coverage შემოსაზღვრულია parser count-ით `C(k)`-ზე:

| k | C(k) | precedence | + associativity | pair | with a prefix |
| --- | --- | --- | --- | --- | --- |
| 6 | 132 | 0.1818 | 2.9091 | 52.2879 | 314.4394 |
| 7 | 429 | 0.0559 | 0.8951 | 16.0886 | 96.7506 |
| 8 | 1430 | 0.0168 | 0.2685 | 4.8266 | 29.0252 |
| 9 | 4862 | 0.0049 | 0.0790 | 1.4196 | 8.5368 |
| 10 | 16796 | 0.0014 | 0.0229 | 0.4109 | 2.4712 |
| 11 | 58786 | 0.0004 | 0.0065 | 0.1174 | 0.7061 |
| 12 | 208012 | 0.0001 | 0.0018 | 0.0332 | 0.1995 |

associativity-ის ჭერი `k = 7`-იდან იბოჭება, წყვილისა `k = 10`-იდან, prefix-ისა `k = 11`-იდან.
თითო დამატებითი კომპონენტი expression-ის სიგრძეში დაახლოებით ორ operator-ს ყიდულობს და შემდეგ
იმავე Catalan კედელს ხვდება, რადგან ორი ნაბიჯით დაშორებული Catalan შეფარდება `16`-ისკენ მიისწრაფის
და სივრცეები კონსტანტური მამრავლებია.

ადგილი, სადაც ამ card-ს ყველაზე მეტად შეუძლია რაღაც დამალოს, არის behavioural quotient, ამიტომ ის
პირდაპირ ითქმის. ორი assignment ტოლად ცხადდება, როცა ისინი `16` ორ-operator-იან witness word-ს
იდენტურად შლიან. ეს ტოლობა ევრისტიკა არ არის: witness family comparison matrix-ს უჯრა-უჯრა
კითხულობს, ხოლო matrix ყოველ parse-ს განსაზღვრავს, ასე რომ ვერც უფრო გრძელი word და ვერც სხვა
corpus ვერ გახლეჩს იმ class-ს, რომელსაც witness family აერთიანებს. ტოლობა მიუხედავად ამისა
შემოწმებულია და არა მხოლოდ განხილული — matrix-ის მიხედვით დაჯგუფება და witness parse-ის მიხედვით
დაჯგუფება ერთსა და იმავე დანაწილებას იძლევა ყოველ გაშვებულ bound-სა და alphabet-ზე.

## ინტერპრეტაცია

პირველი და ყველაზე დიდი შედეგი ის არის, რომ null model **ვარდება**, და ვარდება სწორედ იმ
corpus-ზე, რომელმაც წინა გაფართოების ნული დააფიქსირა. associativity-მ registry თექვსმეტჯერ
გაზარდა და 0024 corpus-ზე მათემატიკა ვერ იყიდა; მეორე binding-power კომპონენტი იმავე corpus-ზე
იმავე key-ით class count-ს `2.209`-ჯერ ზრდის. ორი გაფართოება სახეობით არ არის შესადარებელი:

```text
associativity   changes what one operator does to itself
the pair        changes what one operator does to another, and asymmetrically
```

სწორედ ამ განსხვავებას აჩვენებს support-ის სტრატიფიკაცია. ერთ-operator-იანი source-ები საერთოდ
ვერაფერს იძენენ, რადგან იქ წყვილი მხოლოდ associativity-ს აკოდირებს და associativity უკვე იქაა.
ყოველი მოგება იმ source-ებში ცხოვრობს, სადაც სულ მცირე ორი operator ტიპია, სადაც წყვილს შეუძლია
times მარცხნივ plus-ზე მაღლა და მარჯვნივ დაბლა დააყენოს — მტკიცება, რომელსაც ვერც ერთი სკალარული
precedence ვერ იტყვის და ვერც ერთი associativity flag ვერ გაასწორებს.

მეორე შედეგი flat slice-ის ზომაა. Generation 1-ის `25` grammar და 0030-ის `388` წყვილის სივრცეში
უბრალოდ პატარები არ არიან; მთელი flat family, level-ების ყოველი დალაგება level-ზე side-ით,
`6902` parser-იდან `730`-ია. პროექტი მუშაობდა იმ parser-ების `10.577` პროცენტში, რომელსაც
operator-ზე ერთი დამატებითი მთელი რიცხვი ხელმისაწვდომს ხდის, ხოლო გარეთ დარჩენილ `6172`-ს
სკალარული აღწერა საერთოდ არ გააჩნია.

მესამე შედეგი უარყოფითია და პირველის გვერდით დგას. **უფრო დიდი სივრცე მაინც კონსტანტაა
ექსპონენტის წინააღმდეგ.** წყვილი precedence ხარვეზის `29.655` პროცენტს აღადგენს იქ, სადაც
associativity-მ `11.617` აღადგინა, მაგრამ თითო ნაბიჯზე აღდგენა იმავე წესით ეცემა, როგორც ადრე —
`100.000`, `70.968`, `55.746`, `41.811`, `28.658` — და ჭერის ცხრილი ხსნის რატომ. თითო განზომილება
expression-ის სიგრძეში დაახლოებით ორ operator-ს ყიდულობს. სამი განზომილება ოთხს. ამ family-ში
Catalan კედელს არაფერი გაურბის; ის მხოლოდ გადაიდება.

მეოთხე შედეგი partial order-ის გარიგებაა, და ის ყველაზე სუფთაა. partial order უარს ამბობს
**სრულყოფილი სიზუსტით** ყველაფერზე, რაც აქ გავლილია: `58536` უარი word sweep-ში და `1189`
corpus-ზე, და მათგან ვერც ერთი არ მოხვდა source-ზე, რომლის reading-ზეც registry თანხმდებოდა.
უარი კონსერვატიული სიფრთხილე არ არის, ის ზუსტად ემთხვევა ნამდვილ თვითნებობას. მისი ფასია `2.407`
ფრჩხილის წყვილი თითო კონვენციურ reading-ზე და საერთოდ არაფერი გამომსახველობაში, რადგან ვერც ერთი
reading ვერ გახდა ჩაუწერელი. ამის საპირისპიროდ დგას რიცხვი მეორე მხარეს: total order `2130`
უჯრიდან `586`-ს და `119280`-იდან `56484`-ს ჩუმად იღებს, ანუ ირჩევს reading-ს იქ, სადაც თავად
registry არ თანხმდება.

```text
full parenthesization space
    -> prefix-power-reachable subset
    -> pair-reachable subset
    -> associativity-reachable subset
    -> precedence-reachable subset
```

## შეზღუდვები

- ჩამოთვლის bound არის `5` და ის გამაჯერებელია და არა computational: bounds `6` და `7` გაშვებულია
  და parser count `6902`-დან არ დაძრულა. რა დევს `7`-ის მიღმა, არ გაშვებულა, და ჯაჭვის არგუმენტი
  ამბობს, რომ იქ ახალი ვერაფერი იქნება, მაგრამ ეს არგუმენტი რეალიზებად matrix-ებზე მტკიცებაა და
  არა შესრულებული დაკვირვება.
- behavioural quotient **გამოცხადებული** ტოლობაა: ორი assignment ერთი წერტილია, როცა ისინი `16`
  ორ-operator-იან witness word-ს იდენტურად შლიან. witness family დამტკიცებადად კითხულობს მთელ
  comparison matrix-ს, ასე რომ სხვა corpus-მა გაერთიანებული class არ უნდა გახლიჩოს, მაგრამ სწორედ
  სხვა corpus არის ის ადგილი, სადაც ასეთი ტოლობა გატყდებოდა, და აქ მოყვანილი sweep-ების გარდა
  არაფერი გაშვებულა მის წინააღმდეგ.
- reach sweep `k = 6`-ზე ჩერდება. შემდეგი სიგრძე არ გაშვებულა, და ჭერის ცხრილი მრუდის მიმართულებას
  მის მიღმა აფიქსირებს, მაგრამ არა მის ზომას.
- reach sweep ბრტყელ word-ებს იყენებს. ხელით ჩაწერილი ფრჩხილების მქონე source leaf-სა და operator
  თანმიმდევრობას ცვლის და ამ ჩამოთვლის გარეთაა, თუმცა audit და expression-ის მიხედვით coverage
  ცხრილი ორივე შეიცავს ასეთ source-ებს.
- prefix sweep prefix operator-ს მხოლოდ word-ის თავში აყენებს, სადაც tree count-ს აქვს ჩაკეტილი
  ფორმა `C(k+1)`. interior probe მხოლოდ `8` source-ს ფარავს.
- partial-order სივრცე ყველა partial order-ის **გამოცხადებული ქვესიმრავლეა**: ეს არის ოთხ operator
  სიმბოლოზე ყოველი preorder, associativity მარცხნივ ფიქსირებული. მთელი sweep-ის ხელახლა გაშვება
  ყოველი side-ით მარჯვნივ ყველა refusal count-ს იდენტურად ტოვებს, ასე რომ ფიქსირებული side ამ
  პასუხს არ ძრავს, მაგრამ პოზიციაზე ან კონტექსტზე დამოკიდებული rank-ები მოდელის სრულიად გარეთაა.
- semantic key domain კომპონენტს ატარებს და ეს კომპონენტი **ინერტულია**: `canonicalize` ყოველი
  expression-ისთვის ერთსა და იმავე ლიტერალს წერს (`NF-2026-00005`), ასე რომ ოპერატიული
  დისკრიმინაცია არის canonical form excluded points-თან ერთად, და სამეული პრაქტიკაში წყვილია.
- `3125`-expression-იანი გაშვება ერთი templated corpus-ის ერთი დაკვირვებაა; ვალიდაციის სექციაში
  მოყვანილი `250`-source-იანი რიცხვი მისი დეტერმინისტული prefix-ია და არა მისი შერჩევა, ხოლო მისი
  ფენები თვალსაჩინოდ არარეპრეზენტატულია.
- timing-ები ერთი დატვირთული host-იდანაა და რიგია და არა გამეორებადი კონსტანტა.

## Evidence-ის კლასიფიკაცია

- audit, reach ცხრილები, coverage ცხრილი, partial-order ცხრილები და ყოველი class count
  შესრულებადი **observations** არის ვალიდაციაში ჩამოთვლილი გაშვებებიდან.
- გამაჯერებელი bound `5`, behavioural quotient-ის იგივეობა comparison matrix-თან, და
  associativity სვეტის ჩართვა წყვილის სვეტში **symbolically justified** არის და ასევე დაკვირვებული.
- სტრუქტურული ჭერი, parser count `C(k)`-ზე, **symbolically justified** არის ამ ზომის ნებისმიერი
  სივრცისთვის.
- ის, რომ partial order არასოდეს აჭარბებს უარში, **observation** არის `121410` უჯრაზე და არა
  დამტკიცება; არგუმენტი, რომ უარი გულისხმობს შედარებას, რომელზეც registry არ თანხმდება, ესკიზია.
- ის, რომ წყვილის coverage ყოველი სიგრძისთვის ნულისკენ მიისწრაფვის, ჯერ **hypothesis** არის;
  გავლილია მხოლოდ `k` `6`-მდე.

## ვალიდაცია

```text
python -m pytest -q tests/test_binding_power.py
60 passed in 187.59s
```

```text
python -m pytest -q
1351 passed, 2 skipped in 1920.72s
```

suite-ის total ამ გაშვების მომენტისაა; repository-ში პარალელურად სხვა ექსპერიმენტების modules და
tests ემატება, ამიტომ total იზრდება, ხოლო ამ ექსპერიმენტის წვლილი ფიქსირებული რჩება.

ცხრილების უკან მდგარი ზუსტი commands:

```text
python -c "from parseatlas.binding_power import agreement_audit; print(agreement_audit())"

python -c "from parseatlas.binding_power import reach_2d; print(reach_2d(6, workers=1))"

python -c "from parseatlas.binding_power import saturation_scan; print(saturation_scan())"

python -c "from parseatlas.binding_power import flat_slice; print(flat_slice())"

python -c "from parseatlas.binding_power import three_d; print(three_d(5, workers=15))"

python -c "from parseatlas.binding_power import partial_orders; print(partial_orders(workers=1))"

python -c "from parseatlas.binding_power import partial_order_sweep; print(partial_order_sweep(4))"

python -c "from parseatlas.binding_power import null_model; print(null_model(workers=1))"

python -c "from parseatlas.binding_power import null_model; from parseatlas.corpus_matrix import generate_corpus; print(null_model({'0024': tuple(i['source'] for i in generate_corpus()['expressions'])}, workers=15))"
```

ბოლო command არის `3125`-expression-იანი გაშვება და ამ host-ზე `15` worker-ით `292.8` წამს იღებს.
იგივე გამოძახება ამ corpus-ის პირველ `250` source-ზე `27.2` წამს იღებს და აფიქსირებს `975`
precedence class-ს, `975`-ს associativity-თან და `2100`-ს წყვილთან.
