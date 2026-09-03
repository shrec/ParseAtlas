# ParseAtlas ექსპერიმენტი 0035: alternative mathematics in 25 worlds

## მიზანი

პროექტის founding question-ის პირდაპირი პასუხი: **თუ ადამიანები operator order-ზე სხვანაირად შეთანხმდებოდნენ, მათემატიკას იმ order-ის მიხედვით ააშენებდნენ, ამიტომ თვით objects იქნებოდა სხვა.**

არგუმენტი notational-ია და არა ფილოსოფიური. მათემატიკოსი ყოველთვის ყველაზე მარტივ ჩანაწერს წერს, ხოლო ის, თუ რა არის *simple*, notation-ზეა დამოკიდებული. `a*x*x + b*x + c` სტანდარტული polynomial-ია სწორედ იმიტომ, რომ conventional precedence-ის ქვეშ იაფად იწერება. სხვა convention-ში **იგივე written form სხვა object-ს აღნიშნავს**, და სწორედ ის object იქნებოდა შესწავლილი, დასახელებული და აშენებული. ამიტომ თითო standard written form-ისთვის შეგვიძლია წავიკითხოთ, თუ რა არის ის object რეალურად თითოეულ world-ში.

Worlds არის `4! = 24` strict precedence ordering პლუს conventional tied-level control `G0`, სულ `25`.

## Catalogue

`26` standard written form, თითოეული `(name, area, written form, principal variable)` სახით, `src/parseatlas/alternative_mathematics.py::STANDARD_CATALOGUE`-ში. მოიცავს algebra-ს (linear, quadratic, cubic, monic quadratic, vertex form, difference of squares, binomial square, sum of cubes, distributive law, linear combination), geometry-ს (Pythagorean form, law of cosines form, circle form, slope form, triangle area), analysis-ს (sine/cosine/exponential truncated series, geometric sum) და arithmetic-ს (mean of two, mean of three, arithmetic progression, compound interest, Fahrenheit form, harmonic form, rate form).

Objects იდარებიან პროექტის არსებული **semantic key**-ით - `(canonical expression, domain, excluded points)` - იმავე triple-ით, რომელსაც `analyze_expression` და `corpus_matrix.expression_classes` იყენებენ. ორი world ერთსა და იმავე object-ს მხოლოდ მაშინ კითხულობს, როცა სამივეზე თანხმდება; canonical text მარტო არასოდეს არის key.

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

### 2. სად არის radical საერთოდ საჭირო

**Standard quadratic-ის ამოსახსნელად radical საჭიროა `13` world-ში `25`-დან; დანარჩენ `12`-ში roots პირდაპირ coefficients-ის negation-ია და არც discriminant არსებობს, არც square root.**

უფრო ფართოდ, მთელ catalogue-ზე: `8` world-ში (`G01`, `G02`, `G05`, `G07`, `G08`, `G11`, `G19`, `G21`) **არცერთი** standard form არ საჭიროებს radical-ს. `G0`-ში `26`-დან `10` საჭიროებს. Maximum არის `11` (`G16`, `G17`, `G23`).

| world | precedence | radical pages / 26 |
|---|---|---|
| `G01`, `G02`, `G05`, `G07`, `G08`, `G11`, `G19`, `G21` | სხვადასხვა | `0` |
| `G03` | `+ > * > - > /` | `2` |
| `G04`, `G06`, `G20` | სხვადასხვა | `4` |
| `G09` | `- > * > + > /` | `7` |
| `G13`, `G15` | `* > + > - > /`, `* > - > + > /` | `8` |
| `G10`, `G12`, `G14`, `G22` | სხვადასხვა | `9` |
| **`G0`**, `G18`, `G24` | `*=/ > +=-`, `* > / > - > +`, `/ > * > - > +` | `10` |
| `G16`, `G17`, `G23` | სხვადასხვა | `11` |

### 3. Convention-independent core

**Catalogue-ის `26` entry-დან `4` არის იდენტური ყველა `25` world-ში: `a*(b + c)` (distributive law), `b*h/2` (triangle area), `p*r*t/100` (compound interest), `d/t` (rate form).**

ეს entries არცერთ operator ambiguity-ს არ ტოვებენ: ან სრულად parenthesized არიან, ან ერთგვაროვანი `*`/`/` chain-ია, სადაც precedence permutation parse tree-ს არ ცვლის. დანარჩენი `22` entry fractures.

### 4. ყველაზე fractured object

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

### 5. არის თუ არა `G0` განსაკუთრებული

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

`4` series entry `35` distinct reading-ს იძლევა. მათგან **`0` არის periodic - არცერთ world-ში, `G0`-ის ჩათვლით**. ეს არ არის conventional world-ის დამცირება და არც მისი გამორჩევა: truncated series **ყველა** world-ში polynomial ან rational function-ია, და არცერთი მათგანი არ არის periodic. `G0`-ის reading `x**5/120 - x**3/6 + x` არის odd quintic, unbounded (`lim -> +oo` და `-oo`), root მხოლოდ `0`. ის `sin(x)`-ს ჰგავს მხოლოდ პატარა interval-ზე, და ეს არის მასზე მთელი სიმართლე.

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

## Textbook pages

ქვემოთ `4` სრული generated page. `roots` სვეტი elided-ია მხოლოდ მაშინ, როცა root expression `80` char-ს აჭარბებს (general cubic formula `967` char-ია); elided cell ცხადად წერს root count-ს და elision-ს.

### World `G0` - precedence `*=/ > +=-`

| standard form | denotes here | deg | roots | radical | how it is solved |
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
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | 5 | `0` | no | degree 5: 1 roots read straight off the factorisation, no radical |
| `1 - x*x/2 + x*x*x*x/24` | `x**4/24 - x**2/2 + 1` | 4 | 4 roots, 84 chars (elided) | yes | degree 4: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3/6 + x**2/2 + x + 1` | 3 | 3 roots, 272 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | 3 | `-1` | no | degree 3: 1 roots read straight off the factorisation, no radical |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `a + d*n` | 1 | `-a/d` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 32` | 1 | `-160/9` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `10/26`, polynomial pages `24`.

### World `G01` - precedence `+ > - > * > /`

| standard form | denotes here | deg | roots | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*(b + x)` | 1 | `-b` | no | one linear step |
| `a*x*x + b*x + c` | `a*x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 roots read straight off the factorisation, no radical |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3*(b + x)*(c + x)*(d + x)` | 6 | `0, -b, -c, -d` | no | degree 6: 4 roots read straight off the factorisation, no radical |
| `x*x + b*x + c` | `x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 roots read straight off the factorisation, no radical |
| `a*(x - h)*(x - h) + k` | `-a*(h - x)*(-h + k + x)` | 2 | `h, h - k` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a - b*b` | `a*b*(a - b)` | 2 | `0, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `2*a**2*b**2*(a + 2)` | 3 | `-2, 0` | no | degree 3: 2 roots read straight off the factorisation, no radical |
| `a*a*a + b*b*b` | `a**2*b**2*(a + b)` | 3 | `0, -b` | no | degree 3: 2 roots read straight off the factorisation, no radical |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*y*(b + x)` | 1 | `-b` | no | one linear step |
| `a*a + b*b - c*c` | `a*c*(a + b)*(b - c)` | 2 | `0, -b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + b*b - 2*a*b*c` | `a**2*b*c*(a + b)*(b - 2)` | 3 | `0, -b` | no | degree 3: 2 roots read straight off the factorisation, no radical |
| `x*x + y*y - r*r` | `-r*x*(r - y)*(x + y)` | 2 | `0, -y` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `y - w/x - v` | `(w - y)/(v - x)` | - | none | no | rational: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `0` | - | none | no | no equation to solve: the reading carries no power of the variable |
| `1 - x*x/2 + x*x*x*x/24` | `(1 - x)/(24*x**2*(x + 2))` | - | `1` | no | rational: solve the numerator, then discard the poles |
| `1 + x + x*x/2 + x*x*x/6` | `(2*x + 1)/(6*x*(x + 2))` | - | `-1/2` | no | rational: solve the numerator, then discard the poles |
| `1 + r + r*r + r*r*r` | `r**3*(4*r + 2)` | 4 | `-1/2, 0` | no | degree 4: 2 roots read straight off the factorisation, no radical |
| `a + b/2` | `a/2 + b/2` | 1 | `-b` | no | one linear step |
| `a + b + c/3` | `a/3 + b/3 + c/3` | 1 | `-b - c` | no | one linear step |
| `a + n*d` | `d*(a + n)` | 1 | `-a` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/37` | 1 | `0` | no | one linear step |
| `1/a + 1/b` | `1/(b*(a + 1))` | - | none | no | rational: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `0/26`, polynomial pages `22`.

### World `G20` - precedence `/ > + > * > -`

| standard form | denotes here | deg | roots | radical | how it is solved |
|---|---|---|---|---|---|
| `a*x + b` | `a*(b + x)` | 1 | `-b` | no | one linear step |
| `a*x*x + b*x + c` | `a*x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 roots read straight off the factorisation, no radical |
| `a*x*x*x + b*x*x + c*x + d` | `a*x**3*(b + x)*(c + x)*(d + x)` | 6 | `0, -b, -c, -d` | no | degree 6: 4 roots read straight off the factorisation, no radical |
| `x*x + b*x + c` | `x*(b + x)*(c + x)` | 3 | `0, -b, -c` | no | degree 3: 3 roots read straight off the factorisation, no radical |
| `a*(x - h)*(x - h) + k` | `-a*(h - x)*(-h + k + x)` | 2 | `h, h - k` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a - b*b` | `a**2 - b**2` | 2 | `-b, b` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `a*a + 2*a*b + b*b` | `2*a**2*b**2*(a + 2)` | 3 | `-2, 0` | no | degree 3: 2 roots read straight off the factorisation, no radical |
| `a*a*a + b*b*b` | `a**2*b**2*(a + b)` | 3 | `0, -b` | no | degree 3: 2 roots read straight off the factorisation, no radical |
| `a*(b + c)` | `a*(b + c)` | 1 | `0` | no | one linear step |
| `a*x + b*y` | `a*y*(b + x)` | 1 | `-b` | no | one linear step |
| `a*a + b*b - c*c` | `a*b*(a + b) - c**2` | 2 | `(-b**2 - sqrt(b*(b**3 + 4*c**2)))/(2*b), (-b**2 + sqrt(b*(b**3 + 4*c**2)))/(2*b)` | yes | quadratic formula: discriminant, then a square root |
| `a*a + b*b - 2*a*b*c` | `a*b*(a + b - 2*c)` | 2 | `0, -b + 2*c` | no | degree 2, radical-free: the roots are already rational in the coefficients |
| `x*x + y*y - r*r` | `-r**2 + x*y*(x + y)` | 2 | `(-y**2 - sqrt(y*(4*r**2 + y**3)))/(2*y), (-y**2 + sqrt(y*(4*r**2 + y**3)))/(2*y)` | yes | quadratic formula: discriminant, then a square root |
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `-7*x**7/720 + x` | 7 | `0, -2**(2/3)*3**(1/3)*5**(1/6)*7**(5/6)/7, 2**(2/3)*3**(1/3)*5**(1/6)*7**(5/6)/7` | yes | degree 7: a radical or an unsolvable root object is required |
| `1 - x*x/2 + x*x*x*x/24` | `1 - x**5/16` | 5 | `2**(4/5)` | yes | degree 5: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3*(2*x + 1)/4` | 4 | `-1/2, 0` | no | degree 4: 2 roots read straight off the factorisation, no radical |
| `1 + r + r*r + r*r*r` | `r**3*(4*r + 2)` | 4 | `-1/2, 0` | no | degree 4: 2 roots read straight off the factorisation, no radical |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `d*(a + n)` | 1 | `-a` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 288` | 1 | `-160` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `4/26`, polynomial pages `24`.

### World `G24` - precedence `/ > * > - > +`

| standard form | denotes here | deg | roots | radical | how it is solved |
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
| `y - w/x - v` | `-v - w/x + y` | - | `w/(-v + y)` | no | rational: solve the numerator, then discard the poles |
| `b*h/2` | `b*h/2` | 1 | `0` | no | one linear step |
| `x - x*x*x/6 + x*x*x*x*x/120` | `x**5/120 - x**3/6 + x` | 5 | `0` | no | degree 5: 1 roots read straight off the factorisation, no radical |
| `1 - x*x/2 + x*x*x*x/24` | `x**4/24 - x**2/2 + 1` | 4 | 4 roots, 84 chars (elided) | yes | degree 4: a radical or an unsolvable root object is required |
| `1 + x + x*x/2 + x*x*x/6` | `x**3/6 + x**2/2 + x + 1` | 3 | 3 roots, 272 chars (elided) | yes | degree 3: a radical or an unsolvable root object is required |
| `1 + r + r*r + r*r*r` | `r**3 + r**2 + r + 1` | 3 | `-1` | no | degree 3: 1 roots read straight off the factorisation, no radical |
| `a + b/2` | `a + b/2` | 1 | `-b/2` | no | one linear step |
| `a + b + c/3` | `a + b + c/3` | 1 | `-b - c/3` | no | one linear step |
| `a + n*d` | `a + d*n` | 1 | `-a/d` | no | one linear step |
| `p*r*t/100` | `p*r*t/100` | 1 | `0` | no | one linear step |
| `9*c/5 + 32` | `9*c/5 + 32` | 1 | `-160/9` | no | one linear step |
| `1/a + 1/b` | `(a + b)/(a*b)` | - | `-b` | no | rational: solve the numerator, then discard the poles |
| `d/t` | `d/t` | 1 | `0` | no | one linear step |

radical pages `10/26`, polynomial pages `24`.

`G0` და `G24` page-ები ამ catalogue-ზე უჯრედ-უჯრედ იდენტურია, თუმცა მათი precedence სრულიად სხვაა (`*=/ > +=-` vs `/ > * > - > +`). ეს არის კითხვა `5`-ის პასუხის ვიზუალური ფორმა.

## Multicore

Repository policy multicore by default-ია გაზომილი გადაწყვეტილებით. Work unit არის თითო catalogue entry (`26` ცალი), რომელიც სრულად independent-ია და CPU-bound SymPy-ს ასრულებს, ამიტომ გამოიყენება `ProcessPoolExecutor`, `resolve_worker_count`-ით `cpu_count - 1` worker (`15` ამ host-ზე, `16` core), interactive session-ისთვის ერთი core headroom-ით.

გაზომვა (`parallelism_measurement`, სრული `26`-entry catalogue, `25` grammar):

```text
cpu_count             16
item_count            26
sequential_seconds    83.11
parallel_seconds      29.32
parallel_workers      15
speedup               2.83
identical_results     true
faster_path           parallel
```

Parallel იმარჯვებს, ამიტომ default parallel-ია. Speedup `2.83` და არა `15`, რადგან ceiling ერთი განუყოფელი unit-ითაა დაწესებული: `sine_series` entry მარტო `32.98 s`-ია `~99 s` sequential total-იდან, ანუ ideal speedup ამ decomposition-ით `~3`. გაზომილი `2.83` ამ ceiling-ზეა. Parallelism მხოლოდ სიჩქარეს ცვლის - `identical_results` ამას პირდაპირ ამოწმებს object id-ების, canonical form-ების, grammar list-ებისა და roots-ის შედარებით და არა ვარაუდით.

## ინტერპრეტაცია

Founding question-ის პასუხი ერთი წინადადებით: **worlds-ის დაახლოებით ნახევარში quadratic formula საერთოდ არ იარსებებდა.**

`12` world-ში `a*x*x + b*x + c` არის უკვე factored cubic, რომლის roots `[0, -b, -c]` პირდაპირ იკითხება coefficients-იდან. იმ worlds-ში არავინ დაწერდა discriminant-ს, არავინ შემოიღებდა `sqrt(b**2 - 4*a*c)`-ს ამ ფორმისთვის, არავინ ისწავლიდა `(-b +- sqrt(D))/(2*a)`-ს ზეპირად. `8` world-ში catalogue-ის `26` standard form-იდან **არცერთი** არ საჭიროებს radical-ს.

ეს არ ნიშნავს, რომ იმ worlds-ში quadratic equations არ იარსებებდა. ნიშნავს იმას, რომ **standard form სხვა იქნებოდა**: მათემატიკოსი მაინც უმარტივეს ჩანაწერს დაწერდა, და იმ ჩანაწერს იმ world-ში სხვა object გამოსდიოდა. სწორედ ეს object გახდებოდა textbook-ის შესავალი თავი.

მეორე მხრივ, არსებობს ნამდვილი convention-independent core: სრულად parenthesized ან ერთგვაროვანი operator chain-ები (`a*(b + c)`, `b*h/2`, `p*r*t/100`, `d/t`) ყველა `25` world-ში იდენტურია. Notation არ წყვეტს ყველაფერს - წყვეტს იქ, სადაც mixed operators precedence-ის კითხვას სვამენ.

და ბოლოს, `G0` არ არის პრივილეგირებული. მას აქვს ორი სრული twin, `25` world მხოლოდ `17` worldview-ს ქმნის, და `G0` არცერთ catalogue entry-ზე მარტო არ დგას. Conventional order ამ გაზომვაში ordinary member-ია და არა outlier.

```text
written form -> grammar -> object -> solving procedure
```

## შეზღუდვები

- **ეს არის მოდელი და არა მტკიცება.** გაზომილია ის, რასაც standard **written forms** აღნიშნავენ სხვა convention-ების ქვეშ. ეს არის მოდელი იმისა, თუ როგორ აშენდებოდა მათემატიკა, და არა მტკიცება იმისა, რომ ზუსტად ასე აშენდებოდა. რეალურ ისტორიაში notation და objects ერთდროულად ვითარდებოდა; აქ notation ფიქსირებულია და მხოლოდ precedence იცვლება.
- **Truncated series polynomial-ია ყველა world-ში, ჩვენისაც.** `x - x*x*x/6 + x*x*x*x*x/120` არის quintic და არა `sin`. არცერთი reading არ არის periodic, `G0`-ის ჩათვლით. `sin`-ის ნამდვილი properties (periodicity, boundedness) ამ პროექტის Generation 1 grammar-ით საერთოდ არ არის მისაწვდომი, რადგან tokenizer-ს არც transcendental function აქვს და არც infinite series.
- **Catalogue hand-chosen-ია.** `26` entry ასახავს განსჯას იმის შესახებ, თუ რა ითვლება standard-ად. სხვა არჩევანი invariant/fractured-ის სხვა თანაფარდობას მოგვცემდა. კონკრეტულად, `4` invariant entry-დან სამი განზრახ არის დამატებული სწორედ იმის შესამოწმებლად, არსებობს თუ არა invariant core - ეს არ არის random sample.
- **Generation 1 grammar-ის ფარგლები.** ოთხი binary operator, unary minus-ის გარეშე, exponentiation-ის გარეშე, ყველა operator left-associative. `a*x*x` არის `x**2`-ის ერთადერთი გამოსახატავი ფორმა; `**`-ის მქონე grammar-ში ეს კითხვა სხვანაირად დაისმებოდა.
- **Principal variable არჩეულია.** თითო entry-ს ერთი principal variable აქვს catalogue-ში მითითებული (მაგ. `a*a - b*b`-სთვის `a`). სხვა არჩევანი degree-სა და roots-ს შეცვლიდა.
- **Root ordering და form SymPy-სია.** `solve` და `factor` კონკრეტულ წარმოდგენას აბრუნებენ; `-sqrt((r - y)*(r + y))` და `-sqrt(r**2 - y**2)` ერთი და იგივეა, მაგრამ string comparison-ში სხვადასხვა. ამიტომ object identity semantic key-ზეა და არა root string-ებზე.
- **Speedup ერთ host-ზეა გაზომილი** (`16` core, Windows, spawn start method). სხვა host-ზე რიცხვი სხვა იქნება; გადაწყვეტილება ხელახლა უნდა გაიზომოს და არა გადმოწერილი.

## Evidence-ის კლასიფიკაცია

- **Observations** (executable, ამ repository-ში რეპროდუცირებადი): quadratic-ის `2` object და მათი `13`/`12` split, radical-ის საჭიროება `13` world-ში, `4` invariant entry, series-ის `14` distinct reading, `0` periodic reading, `17` distinct worldview, `G0`-ის twins `G18` და `G24`, per-world radical page counts, და multicore timing.
- **Interpretation** (გაზომილიდან გამოტანილი და არა თვითონ გაზომილი): მტკიცება, რომ იმ worlds-ის მათემატიკოსები **ამ** objects-ს ააშენებდნენ. ეს არის notational-cost არგუმენტი, არა measurement.
- **არ არის claimed**: რომ conventional order უკეთესია ან უარესია; რომ `24 + 1` worlds-ის რაიმე universal law არსებობს; რომ catalogue representative sample-ია მთელი მათემატიკის; რომ რომელიმე world-ის reading `sin`, `cos` ან `exp`-ია.

## ვალიდაცია

```text
610 passed
```

`tests/test_alternative_mathematics.py`: `17 passed`, მათ შორის quadratic-ის ორივე group pinned (grammar list-ებით, degree-ით, discriminant-ით, vertex-ით, roots-ით), `G0`-ის წევრობა degree-`2` group-ში, convention-independent object-ის pin, `textbook(G0)`-ის შემოწმება სამ ნაცნობ entry-ზე, sine series-ის non-periodicity ყველა `25` world-ში, semantic key-ის საჭიროება canonical text-ის ნაცვლად, და sequential/parallel identity.
