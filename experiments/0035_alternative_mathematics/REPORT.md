# ParseAtlas ექსპერიმენტი 0035: alternative mathematics in 25 worlds

## მიზანი

პროექტის founding question-ის პირდაპირი პასუხი: **თუ ადამიანები operator order-ზე სხვანაირად შეთანხმდებოდნენ, მათემატიკას იმ order-ის მიხედვით ააშენებდნენ, ამიტომ თვით objects იქნებოდა სხვა.**

არგუმენტი notational-ია და არა ფილოსოფიური. მათემატიკოსი ყოველთვის ყველაზე მარტივ ჩანაწერს წერს, ხოლო ის, თუ რა არის *simple*, notation-ზეა დამოკიდებული. `a*x*x + b*x + c` სტანდარტული polynomial-ია სწორედ იმიტომ, რომ conventional precedence-ის ქვეშ იაფად იწერება. სხვა convention-ში **იგივე written form სხვა object-ს აღნიშნავს**, და სწორედ ის object იქნებოდა შესწავლილი, დასახელებული და აშენებული. ამიტომ თითო standard written form-ისთვის შეგვიძლია წავიკითხოთ, თუ რა არის ის object რეალურად თითოეულ world-ში.

Worlds არის `4! = 24` strict precedence ordering პლუს conventional tied-level control `G0`, სულ `25`.

## Catalogue

`26` standard written form, თითოეული `(name, area, written form, principal variable)` სახით, `src/parseatlas/alternative_mathematics.py::STANDARD_CATALOGUE`-ში. მოიცავს algebra-ს (linear, quadratic, cubic, monic quadratic, vertex form, difference of squares, binomial square, sum of cubes, distributive law, linear combination), geometry-ს (Pythagorean form, law of cosines form, circle form, slope form, triangle area), analysis-ს (sine/cosine/exponential truncated series, geometric sum) და arithmetic-ს (mean of two, mean of three, arithmetic progression, compound interest, Fahrenheit form, harmonic form, rate form).

Objects იდარებიან პროექტის არსებული **semantic key**-ით - `(canonical expression, domain, excluded points)` - იმავე triple-ით, რომელსაც `analyze_expression` და `corpus_matrix.expression_classes` იყენებენ. ორი world ერთსა და იმავე object-ს მხოლოდ მაშინ კითხულობს, როცა სამივეზე თანხმდება; canonical text მარტო არასოდეს არის key.

ერთი disclosure ამ key-ზე: `parseatlas/canonical.py` `domain`-ში ყოველი expression-ისთვის ლიტერალურ `"R"`-ს წერს, ამიტომ **ოპერატიული discrimination არის `(canonical form, excluded points)`**, ხოლო `domain` არის analysis setting-ის ფიქსირებული დეკლარაცია და არა გაზომილი კომპონენტი. Triple აქ ისეა გამოყენებული, როგორც პროექტი განსაზღვრავს; ზუსტდება მხოლოდ guarantee-ის ფორმულირება. ეს არის repository-wide `NF-2026-00005`, და ის pinned-ია test-ით (`test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement`) და mutation testing-ის მოსალოდნელი survivor-ით (იხ. ვალიდაცია).

## დაკვირვებული შედეგები

### 1. Standard quadratic

**`a*x*x + b*x + c` წარმოქმნის ზუსტად `2` genuinely distinct object-ს `25` world-ში: `13` world-ში ეს არის `a*x**2 + b*x + c`, degree `2`, roots `(-b +- sqrt(b**2 - 4*a*c))/(2*a)`, ხოლო `12` world-ში ეს არის `a*x*(b + x)*(c + x)`, degree `3`, roots `[0, -b, -c]` - უკვე factored და radical-ის გარეშე.**

| object | grammars | canonical | degree | roots | discriminant | vertex |
|---|---|---|---|---|---|---|
| `O01` | `13` | `a*x**2 + b*x + c` | `2` | `(-b - sqrt(-4*a*c + b**2))/(2*a)`, `(-b + sqrt(-4*a*c + b**2))/(2*a)` | `-4*a*c + b**2` | `x = -b/(2*a)`, `y = c - b**2/(4*a)` |
| `O02` | `12` | `a*x*(b + x)*(c + x)` | `3` | `0`, `-b`, `-c` | არ არსებობს | არ არსებობს |

```text
O01: G0, G09, G10, G12, G13, G14, G15, G16, G17, G18, G22, G23, G24
O02: G01, G02, G03, G04, G05, G06, G07, G08, G11, G19, G20, G21
```

### 2. Root convention: roots over `C`

**ამ module-ის ყოველი root list არის სრული multiset `C`-ზე, და ეს ცხადად წერია ყველგან, სადაც root list ან `requires_radical` იბეჭდება: module docstring-ში, `solution_formula`-ს record-ში (`root_domain`, `root_convention`), textbook page-ზე და rendered table-ის სათაურის ქვეშ.**

ეს section იმიტომ არსებობს, რომ ამ report-ის წინა ვერსია ორ სხვადასხვა convention-ს ურევდა, ერთი სიტყვის თქმის გარეშე. `parseatlas.canonical.to_sympy` symbol-ებს `real=True`-თი აშენებს; `solve` ამის შემდეგ **ყველა** complex root-ს აბრუნებს, როცა coefficients თავისუფალი symbol-ებია, და **მხოლოდ real** root-ებს, როცა ისინი რიცხვებია. ერთსა და იმავე page-ზე ორი სხვადასხვა "root" იდგა ერთდროულად.

Conventional world-ის საკუთარ page-ზე ორი ჩანაწერი იმას ამბობდა, რაც არ ისწავლება:

| written form | denotes | ძველი page | სინამდვილე `C`-ზე |
|---|---|---|---|
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | roots `-1`, radical `no`, "roots read straight off the factorisation" | `-1, -I, I`, radical `yes` |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | roots `0`, radical `no` | `5` root, `4` მათგანი complex, radical `yes` |

`(r + 1)*(r**2 + 1)` factorisation-იდან `-1` მართლაც იკითხება, `+-I` კი არა - ანუ ის წინადადება, რომ root-ები "factorisation-იდან პირდაპირ იკითხება", ამ page-ზე ცრუ იყო. იმავე page-ზე `a*a*a + b*b*b` უკვე ბეჭდავდა `b*(1/2 - sqrt(3)*I/2)`-ს: convention ერთი page-ის შიგნითაც არ იყო თანმიმდევრული.

Sweep `25` world x `26` entry = `650` page-ზე, ძველი და ახალი ქცევის პირდაპირი შედარებით:

```text
page-ები short root list-ით (multiplicity sum < degree)          22
    geometric_sum 13 | sine_series 6 | cosine_series 3
    მათგან requires_radical=False მხოლოდ ჩამოგდებული root-ების გამო   16
page-ები, სადაც root list შეიცვალა                               30
requires_radical False -> True                                   21
    ჩამოგდებული root-ების აღდგენით                                16
    მხოლოდ იმის გამო, რომ `I` ახლა radical-ად ითვლება              5
requires_radical True -> False                                    0
short root list ახალი convention-ით                               0
```

**რატომ `C` და არა "მხოლოდ real":** real-only convention განხორციელებადი არ არის. Symbolic coefficients-ის დროს root-ის realness გადაუწყვეტელია - `sqrt(-4*a*c + b**2)` real-ია თუ არა, `a`, `b`, `c`-ზეა დამოკიდებული - ამიტომ real-only-ს ერთგვაროვნად გატარება პრინციპში შეუძლებელია. `C` ერთადერთი convention-ია, რომელიც `650`-ვე page-ზე ერთსა და იმავეს ნიშნავს.

`I` ითვლება radical-ად იმავე მიზეზით, რითაც `sqrt(2)`: `I` **არის** კვადრატული ფესვი, ის, რომელიც real-coefficient world-ს უნდა მიემატოს, რომ complex root საერთოდ ჩაიწეროს. ეს `5` page-ს ეხება - `exponential_series` `G09`, `G13`, `G14`, `G15`-ში და `cosine_series` `G14`-ში - რომლებიც სრულ root list-ს ბეჭდავდნენ, მაგრამ `radical: no`-თი. ოთხივე rational reading-ია, ამიტომ მათ polynomial degree არ აქვთ და completeness-ის შემოწმებას ვერასოდეს დაეჭირა.

**Detector.** ძველი `multiplicity_complete` false assurance იყო: ის SymPy-ს *შიდა* `roots()` table-ს ადარებდა degree-ს და არა იმ list-ს, რომელსაც textbook ბეჭდავს, ამიტომ `True`-ს აბრუნებდა ზუსტად იმ შემთხვევებში, სადაც დაბეჭდილი list მოკლე იყო (`G0`/`geometric_sum`-ზე `True` `3`-დან `1` root-ის გვერდით). ის შეცვლილია `root_list_is_complete`-ით, რომელიც **დაბეჭდილ** list-ს ადარებს degree-ს, გატანილია `world_object`, `solution_formula`, `textbook` და rendered table-ში, და pinned-ია test-ით. Rational reading-ს ან zero reading-ს degree არ აქვს, ამიტომ პასუხი `None`-ია და არა ჩუმად `True`. Incomplete page ცალკე method label-ს იღებს (`degree N: INCOMPLETE - ...`) და table-ში `**INCOMPLETE: k/N**` მარკერით აღინიშნება.

გაზომვა ახალი convention-ით: `650`-დან `0` page short root list-ით.

Real-line statements ცალკეა და სახელითვე ასეა მონიშნული: `profile` (parity, boundedness, growth, periodicity, real poles) და `real_zeros` / `real_poles` / `real_removable_restrictions` reading-ს **real** ცვლადის function-ად აღწერენ; ეს სხვა კითხვაა, ვიდრე ის, თუ სად ცხოვრობს მისი root-ები.

### 3. სად არის radical საერთოდ საჭირო

**Standard quadratic-ის ამოსახსნელად radical საჭიროა `13` world-ში `25`-დან; დანარჩენ `12`-ში roots პირდაპირ coefficients-ის negation-ია და არც discriminant არსებობს, არც square root.**

უფრო ფართოდ, მთელ catalogue-ზე: `8` world-ში (`G01`, `G02`, `G05`, `G07`, `G08`, `G11`, `G19`, `G21`) **არცერთი** standard form არ საჭიროებს radical-ს. `G0`-ში `26`-დან `12` საჭიროებს, და ეს არის maximum, რომელსაც `G0` კიდევ `6` world-თან ინაწილებს.

| world | precedence | radical pages / 26 |
|---|---|---|
| `G01`, `G02`, `G05`, `G07`, `G08`, `G11`, `G19`, `G21` | სხვადასხვა | `0` |
| `G03` | `+ > * > - > /` | `2` |
| `G04`, `G06`, `G20` | სხვადასხვა | `4` |
| `G09` | `- > * > + > /` | `9` |
| `G10`, `G12`, `G13`, `G15`, `G22` | სხვადასხვა | `10` |
| **`G0`**, `G14`, `G16`, `G17`, `G18`, `G23`, `G24` | `*=/ > +=-` და `6` სხვა | `12` |

ეს counts-ები ყველა უფრო მაღალია, ვიდრე ამ report-ის წინა ვერსიაში, და მიზეზი მთლიანად section `2`-ის correction-ია: `21` page-ს `requires_radical` `False`-დან `True`-ზე გადავიდა (`16` ჩამოგდებული complex root-ების აღდგენით, `5` იმით, რომ `I` radical-ად ითვლება), `True`-დან `False`-ზე კი არცერთი. `8` radical-free world უცვლელია - არცერთ მათგანს არ ჰქონდა არც short root list და არც `I`-ის შემცველი page.

აღსანიშნავია, რომ correction-ის შემდეგ `G0` maximum-ზეა და არა შუაში. ეს `G0`-ს outlier-ად არ აქცევს: იმავე `12`-ზე დგას კიდევ `6` world, და კითხვა `6`-ის პასუხი (twins, worldview count) უცვლელია.

### 4. Convention-independent core

**Catalogue-ის `26` entry-დან `4` არის იდენტური ყველა `25` world-ში: `a*(b + c)` (distributive law), `b*h/2` (triangle area), `p*r*t/100` (compound interest), `d/t` (rate form).**

ეს entries არცერთ operator ambiguity-ს არ ტოვებენ: ან სრულად parenthesized არიან, ან ერთგვაროვანი `*`/`/` chain-ია, სადაც precedence permutation parse tree-ს არ ცვლის. დანარჩენი `22` entry fractures.

### 5. ყველაზე fractured object

**ყველაზე convention-dependent არიან truncated series: `1 - x*x/2 + x*x*x*x/24` და `x - x*x*x/6 + x*x*x*x*x/120` თითოეული `14` genuinely distinct object-ს წარმოქმნის `25` world-ში - catalogue-ის maximum.**

| entry | distinct objects |
|---|---|
| `1 - x*x/2 + x*x*x*x/24` (cosine series) | `14` |
| `x - x*x*x/6 + x*x*x*x*x/120` (sine series) | `14` |
| `1 + x + x*x/2 + x*x*x/6` (exponential series) | `5` |
| `x*x + y*y - r*r`, `a*a + b*b - c*c`, `a*a + b*b - 2*a*b*c` | `4` |
| `9*c/5 + 32` | `3` |
| დანარჩენი `15` fractured entry | `2` |

მიზეზი mechanical-ია: series-ს ყველაზე მეტი mixed operator აქვს (`+`, `-`, `*`, `/` ერთ expression-ში, ოთხივე precedence position აქტიური), ამიტომ permutation-ს ყველაზე მეტი განსხვავებული parse tree გამოაქვს.

Sine series-ზე semantic key-ის მუშაობა პირდაპირ ჩანს: `14` distinct object-ს მხოლოდ `11` canonical text შეესაბამება, რადგან `4` სხვადასხვა world-group კითხულობს `0`-ს **სხვადასხვა excluded points-ით** (`[]`, `[-6]`, `[-6, 0]`, ხოლო მეოთხე `x**5 + 6`-ის root-ებით). Canonical text-ზე შედარება ამ `4` object-ს ერთში შეაერთებდა და `14`-ის ნაცვლად `11`-ს დაითვლიდა.

### 6. არის თუ არა `G0` განსაკუთრებული

**არა: `G0` ამ catalogue-ზე გაზომვადად ordinary member-ია. მას აქვს ორი სრული twin - `G18` (`* > / > - > +`) და `G24` (`/ > * > - > +`) - რომლებიც `26`-დან `26` entry-ს ზუსტად `G0`-ის მსგავსად კითხულობენ, და `G0` არცერთ entry-ზე მარტო არ არის.**

`G0`-ის group size თითო entry-ზე: `25` (invariant entries), `13` (algebra-სა და arithmetic-ის უმეტესობა), `9` (Pythagorean/circle/law-of-cosines/exponential/Fahrenheit), `3` (sine და cosine series). მინიმალური `3` არის სწორედ `{G0, G18, G24}`.

Agreement with `G0`, `26` entry-დან:

```text
G0  26   G01  4   G02  4   G03  5   G04  6   G05  5   G06  6   G07  4   G08  4
G09 14   G10 19   G11  7   G12 19   G13 18   G14 19   G15 18   G16 23   G17 24
G18 26   G19  8   G20  9   G21  8   G22 20   G23 24   G24 26
```

`25` world მთელ catalogue-ზე მხოლოდ `17` distinct worldview-ს ქმნის (worldview = რომელ object-ს ირჩევს grammar თითოეულ entry-ზე):

```text
3  G0, G18, G24
2  G01, G07 | G02, G08 | G10, G12 | G13, G15 | G17, G23 | G19, G21
1  G03 | G04 | G05 | G06 | G09 | G11 | G14 | G16 | G20 | G22
```

### Truncated series: რა function-ია თითოეული reading

`4` series entry `35` distinct reading-ს იძლევა. მათგან **`0` არის periodic - არცერთ world-ში, `G0`-ის ჩათვლით**. ეს არ არის conventional world-ის დამცირება და არც მისი გამორჩევა: truncated series **ყველა** world-ში polynomial ან rational function-ია, და არცერთი მათგანი არ არის periodic. `G0`-ის reading `x**5/120 - x**3/6 + x` არის odd quintic, unbounded (`lim -> +oo` და `-oo`), **real** root მხოლოდ `0` (`C`-ზე კიდევ `4` complex root - იხ. section `2`). ის `sin(x)`-ს ჰგავს მხოლოდ პატარა interval-ზე, და ეს არის მასზე მთელი სიმართლე.

SymPy constant function-ს period `0`-ს აძლევს; module ამას იწერს, მაგრამ periodic-ად **არ** ითვლის, რადგან constant degenerate-ია და არა oscillating.

Boundedness კი მართლაც განსხვავდება - და საინტერესო მიმართულებით:

| entry | reading | grammars | parity | bounded | periodic |
|---|---|---|---|---|---|
| sine series | `x**5/120 - x**3/6 + x` | `G0`, `G18`, `G24` | odd | **no** | no |
| sine series | `0` | `G02`, `G05`, `G08` (და `3` სხვა group) | odd and even | yes | no (period `0`, constant) |
| sine series | `-7*x**7/720 + x` | `G20` | odd | no | no |
| cosine series | `x**4/24 - x**2/2 + 1` | `G0`, `G18`, `G24` | even | **no** | no |
| cosine series | `(x**4 - x**2/24 + 2)/(x**4 + 2)` | `G14` | even | **yes** | no |
| cosine series | `(1 - x**2)/(24*(x**4 + 2))` | `G13`, `G15` | even | **yes** | no |

`35` reading-დან `7` bounded-ია, სულ `13` grammar-ზე. ანუ `G14`-ის world-ში `1 - x*x/2 + x*x*x*x/24` არის **bounded even function limit `1`-ით ორივე მიმართულებით და real pole-ების გარეშე** - თვისებრივად უფრო ახლოს `cos`-ის globally bounded ხასიათთან, ვიდრე ჩვენი საკუთარი truncation. ეს არ ნიშნავს, რომ ის `cos`-ია; ის მაინც არ არის periodic.

### რამდენიმე სხვა გაზომილი შედეგი

- `a + b/2` არის `a + b/2` (`13` world) ან `a/2 + b/2` = **ორის ნამდვილი arithmetic mean** (`12` world). იგივე `a + b + c/3` -> `a/3 + b/3 + c/3`.
- `y - w/x - v` არის rational function pole-ით `x = 0` (`13` world) ან `(w - y)/(v - x)` (`12` world) - ანუ **ორ წერტილს შორის slope-ის ფორმულა**.
- `9*c/5 + 32` არის Fahrenheit conversion (`9` world), `9*c/37` (`12` world) ან `9*c/5 + 288` (`4` world).
- `a*a + 2*a*b + b*b` არის `(a + b)**2` (`13` world) ან `2*a**2*b**2*(a + 2)` (`12` world) - binomial square აღარ არსებობს.
- `a*x*x*x + b*x*x + c*x + d`: `13` world-ში cubic formula სჭირდება, `12` world-ში degree `6` object-ია roots-ით `[0, -b, -c, -d]`, radical-ის გარეშე.
- `1/a + 1/b` არის `(a + b)/(a*b)` (`13` world) ან `1/(b*(a + 1))` (`12` world).
- `1 + r + r*r + r*r*r` არის `r**3 + r**2 + r + 1` root-ებით `-1, -I, I` (`13` world, radical სჭირდება) ან `r**3*(4*r + 2)` degree `4`-ით და root-ებით `-1/2, 0` (`12` world, radical-ის გარეშე). სწორედ ეს entry იყო short root list-ით `13` world-ში correction-ამდე.

## Textbook pages

ქვემოთ `4` სრული generated page. Root სვეტი `C`-ზეა, როგორც section `2` ამბობს, და თითოეული table ამას საკუთარ სათაურქვეშ იმეორებს. სვეტი elided-ია მხოლოდ მაშინ, როცა root expression `80` char-ს აჭარბებს (general cubic formula `967` char-ია); elided cell ცხადად წერს root count-ს და elision-ს. Short root list-ის მქონე page `**INCOMPLETE: k/N**`-ით აღინიშნებოდა - ამ `4` page-ზე (და `650`-ვე page-ზე) ასეთი არცერთია.

### World `G0` - precedence `*=/ > +=-`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*x + b` | 1 | `-b/a` | no | one linear step |
| `a*x*x + b*x + c` | `a*x**2 + b*x + c` | 2 | `(-b - sqrt(-4*a*c + b**2))/(2*a), (-b + sqrt(-4*a*c + b**2))/(2*a)` | yes | quadratic formula: discriminant, then a square root |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3 + b*x**2 + c*x + d` | 3 | 3 roots, 967 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `x*x + b*x + c` | `b*x + c + x**2` | 2 | `-b/2 - sqrt(b**2 - 4*c)/2, -b/2 + sqrt(b**2 - 4*c)/2` | yes | quadratic formula: discriminant, then a square root |
| `a*(x - h)*(x - h) + k` | `a*(h - x)**2 + k` | 2 | `h - sqrt(-a*k)/a, h + sqrt(-a*k)/a` | yes | quadratic formula: discriminant, then a square root |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `a**2 + 2*a*b + b**2` | 2 | `-b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a*a + b*b*b` | `a**3 + b**3` | 3 | `-b, b*(1/2 - sqrt(3)*I/2), b*(1/2 + sqrt(3)*I/2)` | yes | degree 3: a radical or an unsolvable root object is required |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*x + b*y` | 1 | `-b*y/a` | no | one linear step |
| `a*a + b*b - c*c` | `a**2 + b**2 - c**2` | 2 | `-sqrt(-b**2 + c**2), sqrt(-b**2 + c**2)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a**2 - 2*a*b*c + b**2` | 2 | `b*(c - sqrt(c**2 - 1)), b*(c + sqrt(c**2 - 1))` | yes | quadratic formula: discriminant, then a square root |
| `x*x + y*y - r*r` | `-r**2 + x**2 + y**2` | 2 | `-sqrt((r - y)*(r + y)), sqrt((r - y)*(r + y))` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | 5 | 5 roots, 359 chars (elided) | yes | degree 5: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `x**4/24 - x**2/2 + 1` | 4 | 4 roots, 84 chars (elided) | yes | degree 4: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3/6 + x**2/2 + x + 1` | 3 | 3 roots, 272 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | 3 | `-1, -I, I` | yes | degree 3: a radical or an unsolvable root object is required |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `a + d*n` | 1 | `-a/d` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 32` | 1 | `-160/9` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `12/26`, polynomial pages `24`, pages with an incomplete root list `0`.

### World `G01` - precedence `+ > - > * > /`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*(b + x)` | 1 | `-b` | no | one linear step |
| `a*x*x + b*x + c` | `a*x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3*(b + x)*(c + x)*(d + x)` | 6 | `0, -b, -c, -d` | no | degree 6: 4 distinct roots over C, multiplicities summing to 6, read straight off the factorisation, no radical |
| `x*x + b*x + c` | `x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(x - h)*(x - h) + k` | `-a*(h - x)*(-h + k + x)` | 2 | `h, h - k` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a - b*b` | `a*b*(a - b)` | 2 | `0, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `2*a**2*b**2*(a + 2)` | 3 | `-2, 0` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*a*a + b*b*b` | `a**2*b**2*(a + b)` | 3 | `0, -b` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*y*(b + x)` | 1 | `-b` | no | one linear step |
| `a*a + b*b - c*c` | `a*c*(a + b)*(b - c)` | 2 | `0, -b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + b*b - 2*a*b*c` | `a**2*b*c*(a + b)*(b - 2)` | 3 | `0, -b` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `x*x + y*y - r*r` | `-r*x*(r - y)*(x + y)` | 2 | `0, -y` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `y - w/x - v` | `(w - y)/(v - x)` | - | none | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `0` | - | none | no | no equation to solve: the reading carries no power of the variable |
| `1 - x*x/2 + x*x*x*x/24` | `(1 - x)/(24*x**2*(x + 2))` | - | `1` | no | rational over C: solve the numerator, then discard the poles |
| `1 + x + x*x/2 + x*x*x/6` | `(2*x + 1)/(6*x*(x + 2))` | - | `-1/2` | no | rational over C: solve the numerator, then discard the poles |
| `1 + r + r*r + r*r*r` | `r**3*(4*r + 2)` | 4 | `-1/2, 0` | no | degree 4: 2 distinct roots over C, multiplicities summing to 4, read straight off the factorisation, no radical |
| `a + b/2` | `a/2 + b/2` | 1 | `-b` | no | one linear step |
| `a + b + c/3` | `a/3 + b/3 + c/3` | 1 | `-b - c` | no | one linear step |
| `a + n*d` | `d*(a + n)` | 1 | `-a` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/37` | 1 | `0` | no | one linear step |
| `1/a + 1/b` | `1/(b*(a + 1))` | - | none | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `0/26`, polynomial pages `22`, pages with an incomplete root list `0`.

### World `G20` - precedence `/ > + > * > -`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*(b + x)` | 1 | `-b` | no | one linear step |
| `a*x*x + b*x + c` | `a*x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3*(b + x)*(c + x)*(d + x)` | 6 | `0, -b, -c, -d` | no | degree 6: 4 distinct roots over C, multiplicities summing to 6, read straight off the factorisation, no radical |
| `x*x + b*x + c` | `x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(x - h)*(x - h) + k` | `-a*(h - x)*(-h + k + x)` | 2 | `h, h - k` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `2*a**2*b**2*(a + 2)` | 3 | `-2, 0` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*a*a + b*b*b` | `a**2*b**2*(a + b)` | 3 | `0, -b` | no | degree 3: 2 distinct roots over C, multiplicities summing to 3, read straight off the factorisation, no radical |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*y*(b + x)` | 1 | `-b` | no | one linear step |
| `a*a + b*b - c*c` | `a*b*(a + b) - c**2` | 2 | `(-b**2 - sqrt(b*(b**3 + 4*c**2)))/(2*b), (-b**2 + sqrt(b*(b**3 + 4*c**2)))/(2*b)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a*b*(a + b - 2*c)` | 2 | `0, -b + 2*c` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `x*x + y*y - r*r` | `-r**2 + x*y*(x + y)` | 2 | `(-y**2 - sqrt(y*(4*r**2 + y**3)))/(2*y), (-y**2 + sqrt(y*(4*r**2 + y**3)))/(2*y)` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `-7*x**7/720 + x` | 7 | 7 roots, 382 chars (elided) | yes | degree 7: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `1 - x**5/16` | 5 | 5 roots, 284 chars (elided) | yes | degree 5: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3*(2*x + 1)/4` | 4 | `-1/2, 0` | no | degree 4: 2 distinct roots over C, multiplicities summing to 4, read straight off the factorisation, no radical |
| `1 + r + r*r + r*r*r` | `r**3*(4*r + 2)` | 4 | `-1/2, 0` | no | degree 4: 2 distinct roots over C, multiplicities summing to 4, read straight off the factorisation, no radical |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `d*(a + n)` | 1 | `-a` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 288` | 1 | `-160` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `4/26`, polynomial pages `24`, pages with an incomplete root list `0`.

### World `G24` - precedence `/ > * > - > +`

Roots are the complete multiset over `C`; `requires_radical` counts `I` as a radical.

| standard form | denotes here | deg | roots over C | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*x + b` | 1 | `-b/a` | no | one linear step |
| `a*x*x + b*x + c` | `a*x**2 + b*x + c` | 2 | `(-b - sqrt(-4*a*c + b**2))/(2*a), (-b + sqrt(-4*a*c + b**2))/(2*a)` | yes | quadratic formula: discriminant, then a square root |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3 + b*x**2 + c*x + d` | 3 | 3 roots, 967 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `x*x + b*x + c` | `b*x + c + x**2` | 2 | `-b/2 - sqrt(b**2 - 4*c)/2, -b/2 + sqrt(b**2 - 4*c)/2` | yes | quadratic formula: discriminant, then a square root |
| `a*(x - h)*(x - h) + k` | `a*(h - x)**2 + k` | 2 | `h - sqrt(-a*k)/a, h + sqrt(-a*k)/a` | yes | quadratic formula: discriminant, then a square root |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `a**2 + 2*a*b + b**2` | 2 | `-b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a*a + b*b*b` | `a**3 + b**3` | 3 | `-b, b*(1/2 - sqrt(3)*I/2), b*(1/2 + sqrt(3)*I/2)` | yes | degree 3: a radical or an unsolvable root object is required |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*x + b*y` | 1 | `-b*y/a` | no | one linear step |
| `a*a + b*b - c*c` | `a**2 + b**2 - c**2` | 2 | `-sqrt(-b**2 + c**2), sqrt(-b**2 + c**2)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a**2 - 2*a*b*c + b**2` | 2 | `b*(c - sqrt(c**2 - 1)), b*(c + sqrt(c**2 - 1))` | yes | quadratic formula: discriminant, then a square root |
| `x*x + y*y - r*r` | `-r**2 + x**2 + y**2` | 2 | `-sqrt((r - y)*(r + y)), sqrt((r - y)*(r + y))` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational over C: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | 5 | 5 roots, 359 chars (elided) | yes | degree 5: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `x**4/24 - x**2/2 + 1` | 4 | 4 roots, 84 chars (elided) | yes | degree 4: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3/6 + x**2/2 + x + 1` | 3 | 3 roots, 272 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | 3 | `-1, -I, I` | yes | degree 3: a radical or an unsolvable root object is required |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `a + d*n` | 1 | `-a/d` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 32` | 1 | `-160/9` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational over C: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `12/26`, polynomial pages `24`, pages with an incomplete root list `0`.

`G0` და `G24` page-ები ამ catalogue-ზე უჯრედ-უჯრედ იდენტურია, თუმცა მათი precedence სრულიად სხვაა (`*=/ > +=-` vs `/ > * > - > +`). ეს არის კითხვა `6`-ის პასუხის ვიზუალური ფორმა.

## Multicore

Repository policy multicore by default-ია გაზომილი გადაწყვეტილებით. Work unit არის თითო catalogue entry (`26` ცალი), რომელიც სრულად independent-ია და CPU-bound SymPy-ს ასრულებს, ამიტომ გამოიყენება `ProcessPoolExecutor`, `resolve_worker_count`-ით `cpu_count - 1` worker (`15` ამ host-ზე, `16` core), interactive session-ისთვის ერთი core headroom-ით.

ქვემოთ სამი ცალკეული გაზომვაა. ისინი განსხვავებულ პირობებში ჩატარდა და ერთმანეთის ჩანაცვლებით არ იკითხება; თითოეულს თავისი პირობა უწერია.

**გაზომვა A - `parallelism_measurement`, სრული `26`-entry catalogue, `25` grammar, `3` დამოუკიდებელი გაშვება, თითო სუფთა interpreter-ში:**

```text
run   sequential_s   parallel_s   speedup   workers   identical_results
 1       68.00          20.96       3.24       15          true
 2       60.92          22.29       2.73       15          true
 3       57.76          18.61       3.10       15          true

cpu_count 16 | item_count 26 | automatic_worker_count 15 | faster_path: parallel (3/3)
```

Parallel სამივე გაშვებაზე იმარჯვებს, ამიტომ default parallel-ია. Speedup `2.73 - 3.24`, და არა `15`.

**გაზომვა B - per-entry decomposition cold SymPy cache-ით.** თითოეული entry ცალკე process-ში გაეშვა (`max_tasks_per_child=1`), ანუ ზუსტად იმ პირობაში, რომელშიც pool-ის worker მუშაობს, და დროც process-ის შიგნიდან აითვალა, spawn-ისა და import-ის გარეშე:

```text
cold total (26 entry)            71.99 s
ყველაზე ნელი entry  sine_series   20.18 s
total / slowest                    3.57
```

`sine_series` განუყოფელი unit-ია - pool-ს მისი დაყოფა არ შეუძლია, ამიტომ parallel wall clock მისი cost-ის მასშტაბს ვერ ჩამოსცდება. გაზომვა A-ს parallel wall clock (`18.61 - 22.29 s`) სწორედ ამ `20.18 s`-ის გარშემოა, და გაზომილი speedup (`2.73 - 3.24`) B-ს decomposition ceiling-ის (`3.57`) ქვემოთაა. ეს ორი გაზომვა ერთმანეთს ეთანხმება.

**გაზომვა C - რატომ არის speedup-ის რიცხვს spread.** per-entry cost სტაბილური სიდიდე არ არის. ერთსა და იმავე process-ში მეორე sequential pass პირველზე `1.6`-ჯერ სწრაფია, რადგან SymPy entry-ებს შორის memoise-ს აკეთებს:

```text
                    round 1    round 2
sequential total    79.95 s    50.12 s
sine_series         18.24 s     6.93 s
parallel (იმავე process-იდან გაშვებული)   23.62 s   25.08 s
```

Sequential path ამ საერთო cache-ს იყენებს, pool-ის `15` ცალკეული process კი ვერ. ამიტომაა, რომ sequential total `50 - 80 s` შუალედში ცურავს, ხოლო parallel wall clock ყველა გაზომვაზე ერთად `18.61 - 25.08 s`-ში ბევრად მჭიდროდ ზის. Speedup არის ამ ორის ფარდობა, ამიტომ spread მას თან სდევს და აქ ისეა მოყვანილი, როგორც გაზომილია და არა ერთი "ლამაზი" რიცხვით.

Pool-ის საკუთარი startup ცალკე გაზომილია (`15` worker, spawn start method, `26` უსაქმო item): `1.35 s`.

Parallelism მხოლოდ სიჩქარეს ცვლის - `identical_results` ამას პირდაპირ ამოწმებს object id-ების, canonical form-ების, grammar list-ებისა და root-ების შედარებით და არა ვარაუდით; სამივე გაშვებაზე `true`.

## ინტერპრეტაცია

Founding question-ის პასუხი ერთი წინადადებით: **worlds-ის დაახლოებით ნახევარში quadratic formula საერთოდ არ იარსებებდა.**

`12` world-ში `a*x*x + b*x + c` არის უკვე factored cubic, რომლის roots `[0, -b, -c]` პირდაპირ იკითხება coefficients-იდან. იმ worlds-ში არავინ დაწერდა discriminant-ს, არავინ შემოიღებდა `sqrt(b**2 - 4*a*c)`-ს ამ ფორმისთვის, არავინ ისწავლიდა `(-b +- sqrt(D))/(2*a)`-ს ზეპირად. `8` world-ში catalogue-ის `26` standard form-იდან **არცერთი** არ საჭიროებს radical-ს.

ეს არ ნიშნავს, რომ იმ worlds-ში quadratic equations არ იარსებებდა. ნიშნავს იმას, რომ **standard form სხვა იქნებოდა**: მათემატიკოსი მაინც უმარტივეს ჩანაწერს დაწერდა, და იმ ჩანაწერს იმ world-ში სხვა object გამოსდიოდა. სწორედ ეს object გახდებოდა textbook-ის შესავალი თავი.

მეორე მხრივ, არსებობს ნამდვილი convention-independent core: სრულად parenthesized ან ერთგვაროვანი operator chain-ები (`a*(b + c)`, `b*h/2`, `p*r*t/100`, `d/t`) ყველა `25` world-ში იდენტურია. Notation არ წყვეტს ყველაფერს - წყვეტს იქ, სადაც mixed operators precedence-ის კითხვას სვამენ.

და ბოლოს, `G0` არ არის პრივილეგირებული. მას აქვს ორი სრული twin, `25` world მხოლოდ `17` worldview-ს ქმნის, და `G0` არცერთ catalogue entry-ზე მარტო არ დგას. Conventional order ამ გაზომვაში ordinary member-ია და არა outlier.

ერთადერთი განზომილება, სადაც `G0` ზღვარზე აღმოჩნდა root convention-ის correction-ის შემდეგ, radical page count-ია: `12/26` არის catalogue-ის maximum. მაგრამ იმავე `12`-ზე კიდევ `6` world დგას (`G14`, `G16`, `G17`, `G18`, `G23`, `G24`), ამიტომ ესეც group property-ია და არა `G0`-ის თვისება. Correction-ამდე `G0` ამ სვეტში `10`-ზე ჩანდა და maximum `11` ეგონა - ორივე რიცხვი ჩამოგდებული complex root-ების artefact-ი იყო.

```text
written form -> grammar -> object -> solving procedure
```

## შეზღუდვები

- **ეს არის მოდელი და არა მტკიცება.** გაზომილია ის, რასაც standard **written forms** აღნიშნავენ სხვა convention-ების ქვეშ. ეს არის მოდელი იმისა, თუ როგორ აშენდებოდა მათემატიკა, და არა მტკიცება იმისა, რომ ზუსტად ასე აშენდებოდა. რეალურ ისტორიაში notation და objects ერთდროულად ვითარდებოდა; აქ notation ფიქსირებულია და მხოლოდ precedence იცვლება.
- **Truncated series polynomial-ია ყველა world-ში, ჩვენისაც.** `x - x*x*x/6 + x*x*x*x*x/120` არის quintic და არა `sin`. არცერთი reading არ არის periodic, `G0`-ის ჩათვლით. `sin`-ის ნამდვილი properties (periodicity, boundedness) ამ პროექტის Generation 1 grammar-ით საერთოდ არ არის მისაწვდომი, რადგან tokenizer-ს არც transcendental function აქვს და არც infinite series.
- **Catalogue hand-chosen-ია.** `26` entry ასახავს განსჯას იმის შესახებ, თუ რა ითვლება standard-ად. სხვა არჩევანი invariant/fractured-ის სხვა თანაფარდობას მოგვცემდა. კონკრეტულად, `4` invariant entry-დან სამი განზრახ არის დამატებული სწორედ იმის შესამოწმებლად, არსებობს თუ არა invariant core - ეს არ არის random sample.
- **Generation 1 grammar-ის ფარგლები.** ოთხი binary operator, unary minus-ის გარეშე, exponentiation-ის გარეშე, ყველა operator left-associative. `a*x*x` არის `x**2`-ის ერთადერთი გამოსახატავი ფორმა; `**`-ის მქონე grammar-ში ეს კითხვა სხვანაირად დაისმებოდა.
- **Principal variable არჩეულია.** თითო entry-ს ერთი principal variable აქვს catalogue-ში მითითებული (მაგ. `a*a - b*b`-სთვის `a`). სხვა არჩევანი degree-სა და roots-ს შეცვლიდა.
- **Root ordering და form SymPy-სია.** `solve` და `factor` კონკრეტულ წარმოდგენას აბრუნებენ; `-sqrt((r - y)*(r + y))` და `-sqrt(r**2 - y**2)` ერთი და იგივეა, მაგრამ string comparison-ში სხვადასხვა. ამიტომ object identity semantic key-ზეა და არა root string-ებზე. იგივე ეხება complex root-ების ფორმას: `G0`-ის quintic-ის ოთხი complex root ტრიგონომეტრიული სახითაა დაბეჭდილი (`15**(1/4)*2**(3/4)*cos(atan(sqrt(5)/5)/2) +- ...`), მაშინ როცა იგივე რიცხვები `+-sqrt(10 +- 2*sqrt(5)*I)`-დაც იწერება. Root-ების **სიმრავლე** convention-ია და გაზომილია; მათი **ჩაწერის ფორმა** SymPy-ს არჩევანია.
- **`root_list_is_complete` degree-ს ეყრდნობა.** ის მუშაობს იქ, სადაც reading-ს polynomial degree აქვს. Rational reading-სა და zero reading-ს degree არ აქვთ, ამიტომ იქ პასუხი `None`-ია: ეს არ არის დამალული `True`, მაგრამ არც გარანტიაა. `I`-ის radical-ად ჩათვლა სწორედ იმ `5` rational page-ს დაიჭერს, რომელსაც degree-ზე დაფუძნებული შემოწმება ვერ დაიჭერდა.
- **`domain` semantic key-ში ინერტულია** (`NF-2026-00005`). Triple `(canonical, domain, excluded points)` პროექტისაა და აქ უცვლელად გამოიყენება, მაგრამ `canonical.py` `domain`-ს ყოველთვის `"R"`-ს აყენებს, ამიტომ ფაქტობრივი discrimination ორკომპონენტიანია. ამ ექსპერიმენტის არცერთი დათვლა ამით არ იცვლება - `14` distinct sine-series object `11` canonical text-ის პირისპირ excluded points-ით იყოფა და არა domain-ით - მაგრამ guarantee ისე უნდა ჟღერდეს, როგორც არის.
- **Speedup ერთ host-ზეა გაზომილი** (`16` core, Windows, spawn start method). სხვა host-ზე რიცხვი სხვა იქნება; გადაწყვეტილება ხელახლა უნდა გაიზომოს და არა გადმოწერილი.

## Evidence-ის კლასიფიკაცია

- **Observations** (executable, ამ repository-ში რეპროდუცირებადი): quadratic-ის `2` object და მათი `13`/`12` split, radical-ის საჭიროება `13` world-ში, `4` invariant entry, series-ის `14` distinct reading, `0` periodic reading, `17` distinct worldview, `G0`-ის twins `G18` და `G24`, per-world radical page counts, root convention-ის sweep (`22` short page ძველი convention-ით, `0` ახლით; `21` radical flip), და multicore timing.
- **Interpretation** (გაზომილიდან გამოტანილი და არა თვითონ გაზომილი): მტკიცება, რომ იმ worlds-ის მათემატიკოსები **ამ** objects-ს ააშენებდნენ. ეს არის notational-cost არგუმენტი, არა measurement.
- **არ არის claimed**: რომ conventional order უკეთესია ან უარესია; რომ `24 + 1` worlds-ის რაიმე universal law არსებობს; რომ catalogue representative sample-ია მთელი მათემატიკის; რომ რომელიმე world-ის reading `sin`, `cos` ან `exp`-ია.

## ვალიდაცია

```text
638 passed
```

`tests/test_alternative_mathematics.py`: `28 passed`. მათ შორის quadratic-ის ორივე group pinned (grammar list-ებით, degree-ით, discriminant-ით, vertex-ით, root-ებით), `G0`-ის წევრობა degree-`2` group-ში, convention-independent object-ის pin, `textbook(G0)`-ის შემოწმება სამ ნაცნობ entry-ზე, sine series-ის non-periodicity ყველა `25` world-ში, semantic key-ის საჭიროება canonical text-ის ნაცვლად, და sequential/parallel identity.

Root convention-ისთვის დამატებული `9` test:

```text
test_every_root_list_declares_the_domain_it_was_solved_over
test_control_geometric_sum_page_reports_all_three_roots
test_control_sine_series_page_reports_all_five_roots
test_no_world_reports_a_root_list_short_of_its_degree
test_the_series_pages_of_the_control_world_are_complete_and_all_need_a_radical
test_the_completeness_check_compares_the_printed_list_not_sympys_table
test_an_incomplete_root_list_is_flagged_wherever_it_would_be_printed
test_radical_detection_counts_the_imaginary_unit
test_the_domain_component_of_the_key_is_a_fixed_declaration_not_a_measurement
```

`test_no_world_reports_a_root_list_short_of_its_degree` ის test-ია, რომელიც ამ defect-ის ჩუმად დაბრუნებას კეტავს: ის `geometric_sum`-ს ყველა `25` world-ში კითხულობს (ეს იყო entry, რომელიც `13` world-ში იყო short, და მისი `25`-ვე reading-ს polynomial degree აქვს, ამიტომ შედარებას ყოველთვის აქვს რას შეადაროს) და მოითხოვს `roots_complete is True`-ს ყველგან. რაკი ახლა არცერთი გაზომილი page short არ არის, თავად flag-ის მუშაობა ცალკე მტკიცდება: `root_list_is_complete` პირდაპირ იტესტება მოკლე list-ზე (`False`), ზუსტ list-ზე (`True`) და degree-ის გარეშე (`None`), ხოლო აშენებულ short page-ზე მოწმდება, რომ `render_textbook` `INCOMPLETE: 1/3`-ს ბეჭდავს და `_solution_method` confident label-ს **არ** იძლევა.

Mutation testing ჩატარდა **isolated copy**-ზე (repository არ შეხებია): `src/parseatlas` და test file scratch tree-ში დაკოპირდა და თითო mutation ცალკე გაეშვა.

```text
BASELINE                                                            28 passed
KILLED   roots solved with the real symbol again (ამ card-ის defect)
KILLED   completeness compared against SymPy's internal table, not the printed list
KILLED   radical detection stops counting the imaginary unit
KILLED   the printed convention line is dropped from the rendered table
KILLED   a short root list is rendered without its marker
KILLED   an incomplete list still gets a confident method label
KILLED   radical detection inverted
KILLED   semantic key drops excluded points
KILLED   constants counted as periodic
KILLED   worker count loses the core headroom
KILLED   object groups ordered smallest first
KILLED   degree 2 always reported as needing the quadratic formula
KILLED   boundedness ignores real poles
KILLED   discriminant reported for every polynomial degree
KILLED   the domain component of the key is silently dropped ("R" -> "CONSTANT")
SURVIVED (მოსალოდნელი) domain replaced by the constant it always is ("R" -> "R")

15/16 mutants killed
```

ერთი survivor განზრახია და ის NF-2026-00005-ის მტკიცებულებაა: `canonical["domain"]`-ის ლიტერალური `"R"`-ით ჩანაცვლება `28`-ვე test-ს მწვანედ ტოვებს, რადგან `domain` მართლაც არასოდეს იცვლება. მისი გვერდით მდგარი mutant, რომელიც `domain`-ს **სხვა** მნიშვნელობით ცვლის, იკვდება - ანუ ველი კითხულობს კიდეც, უბრალოდ არაფერს არჩევს.

წინა wave-ის `8` mutant-იდან `4` პირველ გაშვებაზე გადარჩა და მათზე მაშინ დაემატა targeted assertion-ები; ამჯერად ყველა თავიდან გაეშვა და ისევ მკვდარია.
