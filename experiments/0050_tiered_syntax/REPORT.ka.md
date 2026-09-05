# ParseAtlas ექსპერიმენტი 0050: სად მთავრდება flat precedence model

## პასუხი T26-ზე

**flat precedence-ს შეუძლია ორივეს დაფარვა.** მიეცი precedence table-ს ერთი row juxtaposition-ისთვის
და ერთი row prefix minus-ისთვის, და ყოველი tiered convention, რომელიც უბრალოდ layer-ების stack-ია,
გახდება flat table — არა მხოლოდ დამთხვევით ნაპოვნი, არამედ *გადათარგმნილი* ისე, რომ თითოეული layer-ის
სიღრმე stack-ში იკითხება როგორც მისი binding power. ეს თარგმანი `670174` cell-ის წინაშე დადგა და
ყოველ მათგანში parse tree ზუსტად გაიმეორა, `0` disagreement-ით. ის "tiered syntax layers", რომელსაც
T26 მოითხოვს, layer-ების stack-ისთვის სულ ორი დამატებითი row-ია.

მიუხედავად ამისა T26 რაღაცაში მართალია, ოღონდ არა იმაში, რასაც ასახელებს. `91922` მოვლილი
convention-იდან `47951`-ს corpus-ზე flat შესატყვისი არ აქვს. **არცერთი მათგანი არ არის layer-ების
stack.** ისინი ასე იყოფა:

```text
kind                conventions   without a flat equivalent   what it is
linear                    14569                           0   a totally ordered stack of layers
exponent_prefix           14569                        6707   Python's factor rule for a power
split                     62784                       41244   a second layer chain inside ^
```

ანუ flat precedence table-ს არა tiering ამარცხებს. მას ამარცხებს წესი, რომელიც მოქმედებს **ერთ
სინტაქსურ პოზიციაში და არა სხვაში** — და ასეთი ფორმის წესი layer არ არის, ის context-ია. თეზისი ისე
უნდა გადაიწეროს, რომ ეს თქვას, რადგან დღევანდელი ფორმულირებით ის არასწორ თვისებაზე მიუთითებს.

**convention, რომლითაც ეს ექსპერიმენტი საკუთარ corpus-ს წერს, სწორედ იმათგანია, რომელსაც flat table
ვერ წვდება.** `TIGHT_JUXTAPOSITION` არის ბეჭდური მათემატიკისა და ფიზიკის წაკითხვა: `1/2x` არის
`1/(2*x)`, `-x^2` არის `-x**2`, და `x^-2` იპარსება. მისი მეზობელი ზუსტად ერთი bit-ით განსხვავდება —
Python-ის exponent-prefix წესით — და ამ მეზობელს flat შესატყვისი **აქვს**. ყველაზე მოკლე source,
რომელიც ბეჭდურ წაკითხვას `94586` flat model-იდან ყოველი მათგანისგან განასხვავებს, არის

```text
-m x + c        read as   (-(m*x)) + c
```

**და დამატებული syntax თითქმის არანაირ დამატებით მათემატიკას არ ყიდულობს.** `46` corpus source-ზე
tiered სივრცე `94` განსხვავებულ object-ს წვდება და flat სივრცე `94`-ს. ზუსტად `3` object, `1`
source-ზე, tiered სივრცეს მიუწვდომია და არცერთ flat model-ს — და სამივე, ანუ `3`, `split`
kind-იდან მოდის,
რომელსაც არსად აქვს გამოქვეყნებული ნიმუში. ის ორი kind, რომელიც რეალურ პრაქტიკას შეესაბამება, `0`-ს
ამატებს. სიმეტრიულად, `3` object `2` source-ზე flat სივრცეს მიუწვდომია და არცერთ tiered
convention-ს. ეს იგივე ფორმაა, რაც T30-მა associativity-ის ღერძზე იპოვა: მეტი syntax, ახალი
მათემატიკის გარეშე.

## გარემო

```text
Python                3.14.3
SymPy                 1.14.0
platform              Windows-11-10.0.26200-SP0
cores                 16
workers               15
whole report          113.5 s
```

## Conservative extension, პირველ რიგში

საერთო parser ხელუხლებელია. `src/parseatlas/parser.py`, `grammar.py` და `generation_two.py` ზუსტად
ისე რჩება, როგორც იყო; ეს module საკუთარ tokenizer-ს, საკუთარ layered parser-ს და საკუთარ flat
parser-ს ატარებს. ეს კი ბადებს ვალდებულებას, რომელიც ყველაფერზე ადრე იხურება: Generation 1-ზე
შეზღუდული layered parser ზუსტად იმას პარსავს, რასაც Generation 1?

```text
sources                     98    0034's cost corpus + 0035's catalogue + 14 hand-written strings
Generation 1 grammars       25
embeddings of ^            123    24 strict x 5 positions + the tied control x 3 positions
conventions per embedding   98    for the control's embeddings
                           242    for a strict grammar's embeddings
cells                  2874732
disagreements                0
```

ყოველი cell ხეებს ადარებს და არა სტრიქონებს: tiered parser Generation 1-ის საკუთარ `Binary`,
`Number` და `Variable` node-ებს აშენებს, ამიტომ cell არის dataclass ტოლობა. ის ზუსტად ერთ node
ტიპს ამატებს, `Negate`-ს, რომელიც Generation 1-ის ხეს ვერასოდეს ექნება, ამიტომ ნებისმიერი ზედმეტი
negation disagreement-ია. source, რომელსაც tiered convention *უარყოფს*, ასევე disagreement-ად
ითვლება.

**audit რეალური განსხვავების წინაშე მოწმდება და არა მხოლოდ იმას ეკითხებიან, ამბობს თუ არა
conservative-ს.** ორი დამოუკიდებელი შემოწმება:

```text
injected saboteur, one wrong tree on  a - b - c        294 disagreements over    28812 cells
literal policy `none`, a real language change         1470 disagreements over    28812 cells
                                                       naming 1/2, 1/2 * a, 1/2 + a,
                                                       a * 1/2, (1/2 + a) * b
```

მეორე არ არის mock. composite rational literal-ის მოხსნა ისეთი ენობრივი არჩევანია, რომელიც
ნებისმიერს შეიძლება მოუვიდეს, და ის ცვლის იმას, რასაც `1/2 + a` აღნიშნავს; audit-მა ხუთივე
დაზარალებული source უნდა დაასახელოს და არა შემაჯამებელი ვერდიქტი გამოიტანოს.

**site census, რომელიც ხურავს grid-ის იმ ნაწილს, რომელსაც audit არ ივლის.** split-ები სრულად
მოწმდება conventional base-ზე, ხოლო split-ის გარეშე პარამეტრები ყველა `123` embedding-ზე. ის, რაც
ამას საკმარისს ხდის, არგუმენტი არ არის: ყველა `98` source-ზე tokenizer ხედავს

```text
juxtaposition sites          0
prefix minus sites           0
```

slot, რომელსაც parser ვერასოდეს აღწევს, ხეს ვერ შეცვლის, და ეს ნულები დათვლილია და არა ნავარაუდევი.

## რა არის convention აქ

precedence permutation ოპერატორების დალაგებაა. tier assignment ეს არ არის, და ამის ზუსტად თქმა
ექსპერიმენტის ნახევარია.

- **base** არის `121` Generation 2 grammar-იდან ერთ-ერთი — level-ების stack `^ * / + -`-ზე.
- **placement** ახალ სინტაქსურ layer-ს ან *gap*-ში სვამს ორ level-ს შორის, ან ყველაზე მაღლა, ან
  ყველაზე დაბლა, ან არსებულ level-ს *ატოლებს*. base-ს `L` level-ით აქვს `2L + 1` placement:
  `7` conventional base-ისთვის, `11` strict-ისთვის.
- **Juxtaposition** იღებს placement-ს. `*`-ის alias-ის წაკითხვა **არ არის** ცალკე ღერძი — ის
  ზუსტად ის tie placement-ია იმ level-ზე, რომელიც `*`-ს იტევს, და ეს დაკვირვებულია და არა
  ნამტკიცები: ყოველი juxtaposition site-ის ცხად `*`-ად გადაწერა და გადაწერილის დაპარსვა ემთხვევა
  tie placement-ს ყველა `46` source-ზე, `0` disagreement-ით.
- **Unary minus** იღებს placement-ს.
- ნებისმიერი placement შეიძლება **split**-ად დაიშალოს: ზოგადი placement და მისგან განსხვავებული,
  რომელიც `^`-ის მარჯვენა ოპერანდში მუშაობს. split ერთადერთი ობიექტია სივრცეში, რომელიც layer-ების
  stack არ არის.
- **exponent_prefix** უშვებს prefix minus-ს `^`-ის მარჯვენა ოპერანდის თავში, რასაც უნდა ამბობდეს
  minus-ის placement. ეს არის Python-ის factor წესი power-ისთვის, და სწორედ ის აძლევს convention-ს
  საშუალებას `-x^2` წაიკითხოს როგორც `-(x^2)` და მაინც დაპარსოს `x^-2`.

ეს იძლევა `(2L+1) + (2L+1)(2L)` slot-ს juxtaposition-ისთვისაც და minus-ისთვისაც, გაორმაგებულს
flag-ით.

```text
over the conventional base H0     49 x 49 x 2  =     4802
over all 121 Generation 2 bases                   3518642
swept here                                          91922    14569 linear
                                                             14569 exponent_prefix
                                                             62784 split
not swept                                         3426720
```

**მოვლა არ არის სივრცე, და სხვაობა computational limit-ია, დასახელებული აქ, სადაც პასუხი
იკითხება.** რა მოვიარეთ: ყოველი split-ის გარეშე convention ყველა `121` base-ზე, და ყოველი
convention split-ების ჩათვლით სამ base-ზე — `H0`, `H001` და `H120`, conventional grammar და strict
registry-ის ორი ბოლო. რა არ მოვიარეთ: split convention-ები დანარჩენ `118` base-ზე. რა შემოწმდა
ზღვარს მიღმა: ვერდიქტი kind-ების მიხედვით იდენტურია სამივე სრულად მოვლილ base-ზე, და `linear`
იძლევა `0`-ს ყველა `121`-ზე.

## flat model, რომელსაც ედარება

flat model აქ არის თითო binding power თითო role-ზე და ერთი წესი prefix-ის დაშვებისთვის.

```text
roles                        7    ^  *  /  +  -  JUX  NEG
weak orders on 7 roles   47293    the ordered Bell number; ties are allowed because the
                                  conventional grammar HAS ties, * / together and + - together
prefix rules                 2    level      admit a prefix only where its own power is at least
                                             the level being parsed
                                  anywhere   admit a prefix in any operand position, classic Pratt
flat models              94586
```

ორივე prefix წესი განზრახ არის საძიებო სივრცეში. model, რომელიც მხოლოდ level-ის დამცველ წესს
დაუშვებდა, უარყოფდა `x^-2`-ს ყოველ convention-ში, სადაც minus `^`-ზე სუსტად იკვრება, და ასე
შეზღუდული flat კლასი T26-ის დადასტურებას ხელოვნურად დაამზადებდა.

**ეს ორი წესი ᲐᲠ არის ერთადერთი თავისი სახისა, და ადრინდელი რედაქცია ამტკიცებდა, რომ იყო.** Review-მ
იპოვა მესამე, რომელიც მხოლოდ power table-ზე და დაპარსვის level-ზეა დამოკიდებული — დაუშვი წინა `-`
მაშინ, როცა `power(NEG)` დაპარსვის level-ზე ნაკლები არაა, და შემდეგ მისი ოპერანდი დაპარსე ᲘᲛᲐᲕᲔ
ambient level-ზე და არა `power(NEG)`-ზე — და მისი მარტო დამატება ქვემოთ მოცემულ რიცხვებს ძრავს:
exponent prefix flat twin-ის გარეშე `6707` ხდება `5948`, split `41244` ხდება `41186`, ჯამი twin-ის
გარეშე `47951` ხდება `47134`, ხოლო განსხვავებული flat reading ვექტორი `7034` ხდება `8472`. კიდევ სამი
flat წესი შემოწმდა და ისინი ან არაფერს ძრავენ, ან ვერცერთ რიცხვს ვერ ცვლიან, ანუ მგრძნობელობა სწორედ
იმ ერთ წესს მიეწერება და არა ერთბაშად ბევრს.

**verdict-ის ფორმა ამას გაუძლებს**: linear convention-ებს flat twin ყოველ შემთხვევაში აქვთ, ხოლო
`TIGHT_JUXTAPOSITION` კვლავ `-m x + c`-ზე გამოიყოფა. მაგრამ რიცხვები პირობითია იმ flat კლასზე,
რომელიც ჩამოითვალა, და ამ რეპორტმა თავისი tiered ჩამოთვლა ვრცლად გამოიკითხა, ხოლო flat სრულად
გამოაცხადა. ეს ასიმეტრია იგივე ჩავარდნაა, რომლისთვისაც ექსპერიმენტი 0047 ორჯერ დაბრუნდა, ოღონდ
შედარების მეორე მხარეს ჩადენილი — და ის აქ ცხადდება და არა იცავს თავს.

**flat კლასი განზრახ უფრო დიდია.** მისი binary ნაწილი ხუთი ოპერატორის ყველა weak order-ს მოიცავს,
მაშინ როცა tiered სივრცის binary ნაწილი `121` რეგისტრირებული Generation 2 grammar-ია. flat მხარისთვის
მეტი თავისუფლების მიცემა სწორედ ის არის, რაც აძლიერებს დებულებას, რომ flat model-ს ეს შეუძლია; ესვე
არის მიზეზი, რის გამოც flat სივრცე `3` object-ს წვდება, რომელსაც tiered არა — და ეს ამ ასიმეტრიის
არტეფაქტია და არა tier-ების შესახებ დასკვნა.

## მთავარი შედეგი: შეუძლია თუ არა flat precedence-ს ეს?

```text
tiered conventions swept                  91922
flat models searched, exhaustively        94586
corpus sources                               46

distinct tiered reading vectors            4903
distinct flat reading vectors              7034
tiered vectors with a flat equivalent      2875
tiered vectors without one                 2028

conventions with a flat equivalent        43971
conventions without one                   47951
```

kind-ების მიხედვით, იმ ყველაზე მოკლე source-თან ერთად, რომელიც ამ kind-ის convention-ს ბოლო
გადარჩენილი flat model-ისგან განასხვავებს. source-ები მოკლედან გრძელისკენ იარება, ტოლობა
ლექსიკოგრაფიულად იჭრება, და separator ის source-ია, რომელზეც ბოლო გადარჩენილი კვდება.

```text
kind               conventions   without   vectors sep. by rejection   by tree
linear                   14569         0                          0         0
exponent_prefix          14569      6707                        491       699
split                    62784     41244                        404       434

shortest separator, exponent_prefix        a * -b     by rejection
shortest separator, split                  2^-3       by rejection
shortest tree separator, exponent_prefix   e^-k t     read as  (e^(-k)) * t
shortest tree separator, split             x^2y       read as  x^(2*y)
```

`e^-k t` ორჯერ წასაკითხია, რადგან ის ზუსტად Python-ია და ზუსტად ჩვეულებრივი ფიზიკა. Python
exponent-ში `-`-ის შემდგომ ოპერანდს პარსავს როგორც *power*-ს და არა როგორც *unary*-ს, ამიტომ
`e**-k*t` არის `(e**-k)*t`.

**ადრინდელი რედაქცია ამას ხსნიდა იმით, რომ flat table ორივე ნახევარს ერთდროულად ვერ აკეთებს — რომ
`x^-2`-ის მისაღებად prefix ყველგან უნდა დაუშვას, ხოლო ყველგან დაშვებული prefix `t`-ს ყლაპავს.
Review-მ ეს ამ რეპორტის ᲡᲐᲙᲣᲗᲐᲠᲘ მონაცემით უარყო და ორივე წანამძღვარი ვარდება.** აქ ჩამოთვლილი
`94586` flat model-იდან `1874` ᲔᲠᲗᲓᲠᲝᲣᲚᲐᲓ იმეორებს დაბეჭდილი convention-ის წაკითხვას `e^-k t`,
`x^-2`, `-x^2`, `1/2x`, `2^-3` და `a * -b`-ზე — `^7,*6,/1,+5,-4,JUX2,NEG3|anywhere` ერთი მათგანია.
`level` model, რომელშიც `NEG` `^`-ის power-ზე მაღლა ან ტოლია, იღებს `x^-2`-ს prefix-ის ყველგან
დაშვების გარეშე, ხოლო ყველგან დაშვებული prefix `t`-ს არ ყლაპავს, როცა `NEG` `JUX`-ზე მაგრად იკვრება.
ცალკე აღებული, `94586`-იდან `24682` უკვე კითხულობს `e^-k t`-ს tiered-ის წესით, ხოლო `3438` ემთხვევა
დაბეჭდილ convention-ს **ათივე** დასახელებულ ორაზროვან source-ზე.

ნამდვილი დაბრკოლება ის არის, რასაც გაშვება ასახელებს, და ის layer-ი კი არა, **context**-ია:
**`-m x + c`**, სადაც minus exponent-ის გარეთ juxtaposition-ზე ᲡᲣᲡᲢᲘ უნდა იყოს, ხოლო მის შიგნით
იგივე minus — ᲛᲐᲒᲐᲠᲘ. ვერცერთი power table ვერ ინახავს ორივეს, და სწორედ ეს — და არა prefix-ის წესი —
არის ის, რისთვისაც `TIGHT_JUXTAPOSITION`-ს flat twin არ აქვს.

თერთმეტი source განასხვავებს სულ მცირე ერთ convention-ს flat სივრცისგან:

```text
-m x + c    1 - x^2/2 + x^4/24    2^-3    a * -b    a - -b    a x + b y - c
a x^2 + b x + c    b^2 - 4 a c    e^-k t    x - x^3/6    x^2y
```

**flat შესატყვისი corpus-ზეა მიბმული და report ამას არ მალავს.** flat შესატყვისი აქვს ნიშნავს: რაღაც
flat model იმავე წაკითხვას იძლევა ყველა `46` source-ზე. ეს არ ნიშნავს, რომ ისინი ენის ყოველ
სტრიქონზე ემთხვევიან. `linear` row გამონაკლისია და დანარჩენებზე ძლიერია, რადგან იქ flat model
ძებნით არ იძებნება, არამედ layer-ების stack-იდან *აიგება*, და ტოლობა `670174` cell-ზე მოწმდება.

## Round trip და minimality, ორივე exhaustive search-ით

`render_tiered` არის ძებნა და არა ფრჩხილების წესი. parser-იდან გამოყვანილი წესი სივრცის ყოველი
context-დამოკიდებული slot-ისთვის თავიდან უნდა გამოგვეყვანა, და მისი minimality მაშინ არგუმენტი
გახდებოდა. ფრჩხილების რაოდენობის ზრდადი მიმართულებით ძებნა minimality-ს ალგორითმის თვისებად აქცევს:
პირველი ჩანაწერი, რომელიც უკან იმავე ხედ იპარსება, კონსტრუქციულად ყველაზე ცოტა ფრჩხილის წყვილს
შეიცავს.

```text
trees                            46
conventions                    4802    the whole slot space over the conventional base
cells                        220892
round trip failures               0
writings checked             900872
cheaper writings refuted     679980
bracket pairs                100156
```

ჩანაწერების სივრცე დასმული კითხვისთვის სრულია. ჩანაწერს, რომელიც ხედ უკან იპარსება, ფრჩხილი
მხოლოდ ამ ხის node-ის გარშემო შეიძლება ჰქონდეს — ნებისმიერი სხვა მონაკვეთი parse-ის ქვეხე არ
იქნებოდა — და თითოეული `*` node იწერება ან ცხადად, ან juxtaposition-ით, ამიტომ სივრცე არის node-ების
ქვესიმრავლეები გამრავლებული თითო გამრავლების არჩევანზე, და ძებნა პასუხის ქვემოთ მთელს მას ივლის.

**grid conventional base-ზე ჩერდება, რადგან სრული სივრცე მილიონზე მეტი cell-ის exhaustive search
იქნებოდა, და ეს ზღვარი გამჟღავნებულია და არა შედეგად წარმოდგენილი.** რა დევს მის მიღმა: იგივე round
trip და იგივე exhaustive minimality დანარჩენ ორ სრულად მოვლილ base-ზე split-ის გარეშე
convention-ებისთვის.

```text
trees                            46
conventions                     484    split-free, over H001 and H120
cells                         22264
round trip failures               0
writings checked             124262
cheaper writings refuted     101998
bracket pairs                 13164
```

**ერთი შეზღუდვა ამ enumeration-ზე, აქ დეკლარირებული, რადგან ის შეზღუდვაა.** ფრჩხილი მხოლოდ
შედგენილ node-ებზე დაიშვება. ფოთოლზე დასმული ფრჩხილი დაპარსვისთვის ინერტულია — `(x)` და `x` ყოველ
context-ში ერთი და იგივე primary-ია — ამიტომ ჩანაწერს, რომელიც ფოთოლს ფრჩხილავს, აქვს მკაცრად
იაფი ჩანაწერი იმავე parse-ით და მინიმუმი ვერ იქნება. ეს არგუმენტია, ამიტომ ფართო ძებნაც ხელმისაწვდომია
და test suite მას უშვებს: მთელ corpus-ზე ორივე დასახელებული convention-ით, ფოთლის ფრჩხილების დაშვება
`0` cell-ის ფრჩხილთა რაოდენობას ცვლის.

**renderer-იდან ერთი რამ ისე ამოვარდა, რაც ბარათს არ უთხოვია და ერთ ხაზს იმსახურებს.**
juxtaposition მხოლოდ დაპარსვის საკითხი არ არის. იქ, სადაც ის solidus-ზე მაგრად იკვრება, ჩანაწერს
აიაფებს, რაც direction B-ის საკუთარი ვალუტაა:

```text
object            1/(2*x)
alias reading     1 / (2 * x)      1 bracket pair
printed reading   1 / 2x           0 bracket pairs
```

## ორაზროვნების atlas

conventional base-ის `4802` convention-ზე, დაჯგუფებული იმ **object**-ის მიხედვით, რომელსაც თითოეული
წაკითხვა აღნიშნავს და არა ხის მიხედვით, რადგან ერთსა და იმავე object-ს აღმნიშვნელი ორი ხე
მათემატიკაზე უთანხმოება არ არის.

```text
source          question                              object        conventions   published reading
-x^2            is it -(x^2) or (-x)^2 ?              -x**2                4116   mathematical
                                                      x**2                  686   spreadsheet
-2^2            is it -4 or 4 ?                       -4                   4116   mathematical
                                                      4                     686   spreadsheet
1/2x            is it (1/2)*x or 1/(2*x) ?            x/2                  2744   left to right
                                                      1/(2*x)              2058   printed mathematics
6/2(1 + 2)      is it 9 or 1 ?                        9                    2744   left to right
                                                      1                    2058   printed mathematics
2x^2            juxtaposition tighter than ^ ?        2*x**2               3430   universal
                                                      4*x**2               1372   no published practice
x^2y            is the exponent 2 or 2y ?             x**2*y               3528   exponent is one token
                                                      x**(2*y)              686   exponent is the group
```

ყოველი დასახელებული გამოქვეყნებული წაკითხვა მიღწეულია; `0` აკლია. `x^2y`-ს გარდა ამისა **უარყოფს**
`4802` convention-იდან `588` — ის, რომლებშიც juxtaposition-ის layer exponent-იდან მიუწვდომელია — რაც
მესამე პასუხია და precedence table მას საერთოდ ვერ იძლევა.

მარჯვენა სვეტში მოცემული მიკუთვნებები მიკუთვნებებია და ასეც არის მონიშნული. object-ები და მათ გვერდით
მდგარი რიცხვები გაშვებიდან მოდის.

## Null model, რომელიც წყვეტს, იპოვა თუ არა ბარათმა რამე

ექსპერიმენტმა 0030 convention-ის ღერძი associativity-ით გააფართოვა, სხვაობის 12 პროცენტზე ნაკლები
დაიბრუნა და 50 პროცენტით მეტი syntax დაამატა ნულოვანი ახალი მათემატიკით. იგივე კითხვა, დასმული
tier-ებზე: რამდენ განსხვავებულ მათემატიკურ object-ს წვდება tiered სივრცე, რომელსაც flat სივრცე ვერ?

```text
corpus sources                                        46
tiered conventions                                 91922
flat models                                        94586
distinct objects reached by the tiered space          94
distinct objects reached by the flat space            94
objects only the tiered space reaches                  3   on 1 source
objects only the flat space reaches                    3   on 2 sources
```

სტრატიფიცირებული role support-ის მიხედვით, რადგან source, რომელიც `7` role-იდან `j`-ს იყენებს, ვერ
განასხვავებს იმ model-ებს, რომლებიც ამ `j`-ზე თანხმდებიან, და არასტრატიფიცირებული რიცხვი registry
იქნებოდა და არა მათემატიკა:

```text
roles used   sources   tiered objects   flat objects   only tiered   only flat
         1         4                4              4             0           0
         2        27               41             41             0           0
         3        15               49             49             3           3
```

და სტრატიფიცირებული convention-ის kind-ის მიხედვით, რაც სწორედ ის ღერძია, რომელზეც მთავარი შედეგი
დგას:

```text
kind                objects only the tiered space reaches
linear                                                  0
exponent_prefix                                         0
split                                                   3
```

ეს სამი object, ყველა `a x^2 + b x + c`-ზე:

```text
a*x**((b + 2)*(c + x))
a*x**(b*x + c + 2)
a*x**(c + x*(b + 2))
```

ესენი კვადრატულის დეგენერირებული წაკითხვებია, რომლებსაც მხოლოდ ის convention-ები აწარმოებს,
რომლებშიც juxtaposition ზოგადად ერთ tier-ზე ზის და exponent-ის შიგნით სხვაზე. გამოქვეყნებული
ნოტაცია ასე არ იქცევა. ის ორი kind, რომელიც გამოქვეყნებულ ნოტაციას *ნამდვილად* შეესაბამება —
layer-ების stack და Python-ის exponent-prefix წესი — `0` object-ს წვდება, რომელსაც flat სივრცე
აცდენს.

ის სამი object, რომელსაც flat სივრცე წვდება და tiered არა, არის `c + x*(a**2*x**2 + b)`
`a x^2 + b x + c`-ზე, და `-2**(1/6)*x**(1/6) + 1` და `1` `1 - x^2/2 + x^4/24`-ზე. ისინი არსებობენ,
რადგან flat ძებნა ხუთი binary ოპერატორის ყველა weak order-ს მოიცავს, მაშინ როცა tiered სივრცის
binary ნაწილი `121` რეგისტრირებული grammar-ია. ეს ორი სივრცის ასიმეტრიაა, ზემოთ გამჟღავნებული, და
არა tiering-ის თვისება.

## Tokenizer უფრო მეტს წყვეტს, ვიდრე grammar

juxtaposition მხოლოდ იქ არსებობს, სადაც tokenizer-ს ის დანახვა შეუძლია, ამიტომ ის, რასაც tokenizer
იღებს, შედეგის ნაწილია.

```text
accepted as juxtaposition     2x     2 x     2(x + 1)     (a + b)(a - b)     x y     (x + 1)y
refused                       xy     x2                   one identifier, by Generation 1's
                                                          maximal-munch name pattern
```

შედეგი, ხილული ყოველ corpus ჩანაწერში და არა დამალული: კვადრატული იწერება როგორც
`a x^2 + b x + c` და არა `ax^2 + bx + c`, რადგან `ax` ერთი ცვლადია.

რიცხვის pattern უფრო მნიშვნელოვანია. Generation 1 დაუშორებელ `1/2`-ს ერთ rational literal-ად იღებს.
უცვლელად დატოვებული, ეს წესი *ანადგურებს იმ ორაზროვნებას, რომელზეც ეს ბარათია*: `1/2x` იქნებოდა
literal `1/2` juxtaposition-ით მიბმული `x`-თან ყოველ convention-ში, და გამოქვეყნებულ უთანხმოებას
lexer გადაწყვეტდა მანამ, სანამ რომელიმე precedence წესი გაეშვებოდა. ამიტომ ეს წესი ცხადი ღერძია სამი
მნიშვნელობით, და მგრძნობელობა აქ არის ნაჩვენები და არა შეზღუდვების სექციაში:

```text
policy   readings of 1/2x   objects                conservative over Generation 1
gen1                    1   x/2                    yes, 0 disagreements over 28812 cells
split                   2   x/2  and  1/(2*x)      yes, 0 disagreements over 28812 cells
none                    2   x/2  and  1/(2*x)      NO, 1470 disagreements over 28812 cells
```

`split` არის ნაგულისხმევი: composite literal უკან ორ მთელად და გაყოფად იშლება მხოლოდ მაშინ, როცა მას
დაშორების გარეშე მოსდევს primary, რომელიც juxtaposition-ს ქმნის. მასთან `1/2x` ორაზროვანია, ხოლო
`1/2 x` — არა, რაც ქაღალდზეც ასე იკითხება. ის conservative რჩება, რადგან Generation 1-ის არცერთ
სტრიქონს არ შეიძლება ჰქონდეს literal, რომელსაც პირდაპირ name მოსდევს — ეს juxtaposition-ია,
რომელსაც Generation 1 ვერ წერს — და audit ამას აკვირდება და არა ამტკიცებს.

## რას არ აწარმოებს ეს enumeration

enumeration არის მტკიცება იმის შესახებ, თუ რა არსებობს, ამიტომ სივრცის მიერ გამოტოვებული ჩანაწერები
ჩამოთვლილია მანამ, სანამ რიცხვებს ვირწმუნებთ, და ის, რომელსაც პასუხის შეცვლა შეეძლო, შემოწმებულია და
არა ნამტკიცები.

```text
omitted                                              could it change the answer?
juxtaposition restricted by operand kind             CHECKED, it does not
unary +                                              no: orthogonal to both named interactions
left-associative ^                                   no: 0030's axis, it moves counts, not shape
a context other than the right operand of ^          it can only ADD non-flat conventions
more than two contexts                               same
juxtaposition as a chunk, not a left chain           no: the fold is left-associative either way
a tokenizer that reads xy as a product               yes, and it is the disclosed tokenizer limit
function application                                 out of the language entirely
```

შემოწმებული, სრულად. რეალური ნოტაცია ორი ცვლადის ნამრავლს ხაზოვან ტექსტში არასოდეს წერს
მიწებებით — `xy` ერთი იდენტიფიკატორი იქნებოდა — ამიტომ convention, რომელიც სწორედ ამ მიწებებას
კრძალავს, დამაჯერებელია, და ის tier placement არ არის, ანუ დეკლარირებულ სივრცეს კონსტრუქციულად გარეთ
რჩება. შემოწმება ყოველ corpus source-ს ისე გადაწერს, რომ name-name მიწებება აღარ დარჩეს, და მთელ
მთავარ შედეგს გადაწერილ corpus-ზე ხელახლა უშვებს, conventional base-ის `4802` convention-ზე:

```text
sources rewritten            44 of 46
kind               without a flat equivalent, unrestricted   restricted
linear                                                   0            0
exponent_prefix                                         31           28
split                                                 2755         2590
```

რიცხვები იძვრება; ვერდიქტი — არა. `linear` ორივე შემთხვევაში `0`-ია, და context-დამოკიდებული ორივე
kind არანულოვანი რჩება.

## Multicore

გადაწყვეტილება ამ host-ზე დაკვირვებებიდან მოდის და არა ცერის წესიდან. worker-ების რაოდენობა
დაკვირვებული core-ების რაოდენობიდან გამოიყვანება ერთი core-ის მარაგით, არასოდეს კონსტანტიდან.

```text
cores                                        16
workers                                      15
pool startup, two runs                     2.00 s   and   7.16 s
audit         123 payloads x 0.448 s  =   55.13 s sequential   ->  parallel
sweep          60 payloads x 1.453 s  =   87.16 s sequential   ->  parallel
render         60 payloads x 0.336 s  =   20.16 s sequential   ->  parallel
```

მარშრუტიზაციის გადაწყვეტილება უგრძნობია დაკვირვებული startup-ის დიაპაზონში: უფრო დიდ მნიშვნელობაზეც
ყველაზე იაფი დატვირთვა parallel-ად `8.51 s` ჯდება `20.16 s` sequential-ის წინააღმდეგ. Parallelism
მხოლოდ იმას ცვლის, თუ რამდენად სწრაფად, და არასოდეს იმას, რაც იწარმოება, და test suite ამას ამოწმებს
და არ ვარაუდობს: agreement audit, translation audit და render audit თითოეული ტოლ სტრუქტურას
აბრუნებს `workers=1`-ზე და `workers=3`-ზე ან `workers=4`-ზე.

მძიმე მოვლა თავის აშკარა ფორმაში pickling-ის ბიუჯეტში ვერ ჩაეტეოდა. flat პასუხის ყოველი worker-თან
გაგზავნა ათეულობით ათასი წაკითხვის ვექტორის გაგზავნას ნიშნავს; ამის ნაცვლად თითოეული source-ის
რამდენიმე განსხვავებული წაკითხვა ერთ ბაიტად იკოდება და ვექტორი `46` ბაიტი ხდება. ეს არცერთ რიცხვს არ
ცვლის, მხოლოდ იმას, თუ გაშვების რამდენი დრო იხარჯება მონაცემების გადატანაზე.

## შეზღუდვები

- **convention-ების სივრცე დეკლარირებულია.** ის არის `3518642` convention და მოვლილია `91922`, რაც
  ტოვებს `3426720` მოუვლელს, ესენია split convention-ები `121` base-იდან `118`-ზე. სხვა enumeration
  აქაურ ყოველ რიცხვს დაძრავდა. ვერდიქტი kind-ების მიხედვით იდენტურია სამივე სრულად მოვლილ base-ზე და
  `linear` არის `0` ყველა `121`-ზე, სწორედ ამას ეყრდნობა გავრცობა.
- **corpus ხელით არის შერჩეული**, `46` source `6` სფეროზე, და სწორედ ამ corpus-ში იძებნება
  განმასხვავებელი source. მის გარეთ მდგარ source-ს შეეძლო განესხვავებინა convention, რომელსაც ეს
  report flat შესატყვისის მქონედ აღრიცხავს.
- **flat შესატყვისი corpus-ზეა მიბმული** გარდა `linear` row-ისა, სადაც ის აგებული ტოლობაა,
  შემოწმებული `670174` cell-ზე.
- **juxtaposition მხოლოდ იქ არის აზრიანი, სადაც tokenizer-ს ის ესმის.** მიღებულია: `2x`, `2 x`,
  `2(x + 1)`, `(a + b)(a - b)`, `x y`, `(x + 1)y`. უარყოფილია: `xy` და `x2`, რომლებიც ერთი
  იდენტიფიკატორია Generation 1-ის უცვლელად შენარჩუნებული maximal-munch name pattern-ით.
- **composite rational literal ღერძია და არა ფაქტი.** `gen1`-ით დასახელებულ ორაზროვნებას `1/2x`
  აქვს `1` წაკითხვა და არა `2`, და atlas-ის მთელი `1/2x` row ქრება.
- **უარყოფები წაკითხვებად ითვლება** ვექტორების შედარებაში. `2028` შეუსაბამო ვექტორიდან `895`
  flat სივრცისგან უარყოფით განსხვავდება და არა სხვა ხით; დანარჩენი `1133` ხით განსხვავდება.
- **semantic key-ის domain კომპონენტი ინერტულია.** ის ყოველი გამოსახულებისთვის `R`-ად არის დაყენებული
  (NF-2026-00005), ამიტომ მოქმედი იდენტობა კანონიკური ფორმაა გამორიცხულ წერტილებთან ერთად.
- **უარყოფითი მაჩვენებლით ჩაწერილი პოლუსი არ ფიქსირდება.** `x^-2` არცერთ გამორიცხულ წერტილს არ
  იძლევა, რაც Generation 2-ის უცვლელად მემკვიდრეობით მიღებული გამჟღავნებული ზღვარია, და corpus
  ასეთ ჩანაწერებს ნამდვილად შეიცავს.
- **Associativity ფიქსირებულია ᲑᲘᲜᲐᲠᲣᲚᲘ ოპერატორებისთვის** — `^` მარჯვნივ, დანარჩენი მარცხნივ,
  juxtaposition მარცხნივ — და მისი გაფართოება 0030-ის ღერძია და აქ არ კეთდება. ეს პუნქტი ადრე ამბობდა,
  რომ associativity ფიქსირებულია დაზუსტების გარეშე, რასაც გაშვება ეწინააღმდეგება: `3178` tiered
  convention და `37386` flat model განსხვავდება იმით, როგორ ურთიერთქმედებს prefix `^`-თან, რაც
  სახელის გარდა ყველაფრით associativity-ის არჩევანია.
- **ფრჩხილი მხოლოდ შედგენილ node-ებზე დაიშვება** ჩანაწერების enumeration-ში. ფართო ძებნა
  ხელმისაწვდომია და ის `0` cell-ის ფრჩხილთა რაოდენობას ცვლის corpus-ზე ორივე დასახელებული
  convention-ით.
- **multicore-ის კონსტანტები host-ზე დაკვირვებებია**, და pool startup ერთსა და იმავე მანქანაზე ორ
  გაშვებას შორის `3.58`-ჯერ განსხვავდებოდა.

## Evidence-ის კლასიფიკაცია

- conservative extension-ის შედეგი, თარგმანის ტოლობა, flat-equivalence ვერდიქტები, atlas-ის რიცხვები
  და null model-ის რიცხვები executable **observations** არის.
- T26-ის გადმოთქმა — რომ დაბრკოლება context-ია და არა layer — არის **observation** პლუს ცხადი
  არგუმენტი, და ეს არგუმენტი ზემოთ მოცემული ერთგვაროვანი prefix წესების შესახებ არგუმენტია.
- წაკითხვების მიკუთვნება გამოქვეყნებულ პრაქტიკას მიკუთვნებაა და არა observation.
- არაფერია ნამტკიცები იმის შესახებ, რომ დეკლარირებული სივრცის გარეთ მდგარი convention ისე იქცევა,
  როგორც შიგნით მდგარები.

## ვალიდაცია

```text
python -m pytest -q tests/test_tiered_syntax.py
54 passed
```

Mutation testing გაშვებული იყო ხის იზოლირებულ ასლზე და არასოდეს სამუშაო ხეზე. `12` mutant დაედო
მზიდ ხაზებს — layer-stack-ის ამშენებელ-ს, associativity-ის წესს, parser-ის juxtaposition-ისა და
exponent-prefix-ის ტოტებს, composite-literal-ის წესს, დაშორების წესს, flat prefix წესს, flat
თარგმანს, ვექტორის კოდირებას, ფრჩხილების ძებნას, audit-ის შედარებას და role support-ს.

```text
first pass       11 killed    1 survived
survivor         an audit that treated a REJECTION as agreement
why it lived     the site census is 0, so no cell in a passing run ever rejects, and every other
                 test in the file passes with the branch broken
closed by        routing both audit paths through one cell comparison and reaching that branch
                 from a test with a convention that really does reject its input
second pass      12 killed    0 survived
```

ეს გადარჩენილი ჩასაწერია და არა ჩუმად გასასწორებელი. ეს იმავე ფორმის ხვრელია, რაც 0045-ს ჰქონდა:
ტოტი, რომელშიც მწვანე გაშვება არასოდეს შედის, დაცული მხოლოდ იმ ტესტებით, რომლებიც შემაჯამებელ
ვერდიქტს ამოწმებენ.
