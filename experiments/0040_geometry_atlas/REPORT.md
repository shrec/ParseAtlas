# ParseAtlas ექსპერიმენტი 0040: 25 world-ის გეომეტრია

## მიზანი

**`25` world-იდან `12`-ში სწორი ხაზის განტოლება არ არის სწორი ხაზი.**

`y - m*x - c` არის ის პირველი curve equation, რომელსაც ადამიანი სწავლობს. Conventional precedence-ის ქვეშ ის `-c - m*x + y`-ია: total degree `1`, ერთი ხაზი, slope `m`, intercept `c`. `12` world-ში ზუსტად იმავე written form იკითხება როგორც `(c - x)*(m - y)` - total degree `2`, `x*y` cross term-ით, `B^2 - 4*A*C = 1 > 0`, `3x3` discriminant determinant იდენტურად `0`, ანუ **degenerate conic: ორი გადამკვეთი ხაზი `x = c` და `y = m`**. ეს არც slope-ს ინახავს, არც intercept-ს, და საერთოდ ერთი curve არ არის.

ეს არის experiment `0035`-ის (alternative mathematics) გეომეტრიული მკლავი. Algebra-ში ერთი object მეორისგან coefficient-ებით განსხვავდება, და განსხვავების წაკითხვა ვარჯიშს მოითხოვს. გეომეტრიაში object-ს **classification** აქვს - line, circle, ellipse, parabola, hyperbola, cubic, quartic - და classification არის უხეში, მდგრადი, ადამიანის თვალით წასაკითხი label. ორ world-ს შეუძლია coefficient-ებზე არ დაეთანხმოს და მაინც ერთსა და იმავე სახის object-ს სწავლობდეს; როცა ისინი classification-ზე არ თანხმდებიან, ისინი **სხვა გეომეტრიას** სწავლობენ.

Worlds არის `4! = 24` strict precedence ordering პლუს conventional tied-level control `G0`, სულ `25` - იგივე registry, რომელსაც მთელი repository იყენებს (`parseatlas.grammar.all_grammars`).

### ხუთი კითხვა, ხუთი პასუხი

1. **წრეწირი წრეწირად რჩება `25`-დან `9` world-ში**; დანარჩენში ის არის სხვა conic (`4` world-ში ellipse) ან cubic curve (`12` world-ში, რომელთაგან `8`-ში ეს cubic არის სამი სწორი ხაზის გაერთიანება).
2. **სწორი ხაზი სწორი ხაზი რჩება `25`-დან `13` world-ში**, დანარჩენ `12`-ში კი ის არის degenerate conic `x*y` წევრით.
3. **ყველაზე convention-stable არის `(x - y)*(x + y)`**, რომელიც `25`-ვე world-ში ერთი და იგივე object-ია, ხოლო ყველაზე მეტად იშლება `x*x/4 + y*y/9 - 1` (ellipse), რომელიც `13` სხვადასხვა object-ს იძლევა `5` სხვადასხვა classification-ით.
4. **დიახ: `(x - y)*(x + y)` არის ერთი და იგივე object `25`-ვე world-ში** - catalogue-ის `12`-დან ერთადერთი, და ის სრულად parenthesized-ია.
5. **არა: `G0` ამ catalogue-ზე ordinary member-ია** - ის არცერთ curve-ზე მარტო არ დგას (მისი უმცირესი group `5` world-ია), და `4` სხვა world (`G17`, `G18`, `G23`, `G24`) `12`-დან `12` curve-ს ზუსტად ისე კითხულობს, როგორც ის.

## Catalogue

`12` named curve, თითოეული `(name, area, written form, coordinates, parameters, window)` სახით,
`src/parseatlas/geometry_atlas.py::CURVE_CATALOGUE`-ში. Intended tree არის ის, რასაც control grammar `G0` აძლევს - ანუ ის object, რომელსაც ჩვენ ვგულისხმობთ, როცა ამ string-ს ვწერთ.

| # | name | written form | coordinates | parameters (drawing) | რა არის ეს |
|---|---|---|---|---|---|
| 1 | `line` | `y - m*x - c` | `x, y` | `m = 1`, `c = 1` | slope-intercept form |
| 2 | `circle` | `x*x + y*y - r*r` | `x, y` | `r = 2` | წრეწირი origin-ის გარშემო |
| 3 | `ellipse` | `x*x/4 + y*y/9 - 1` | `x, y` | - | semi-axes `2` და `3` |
| 4 | `hyperbola` | `x*x/4 - y*y/9 - 1` | `x, y` | - | იგივე ღერძები, შებრუნებული ნიშნით |
| 5 | `parabola` | `y - a*x*x - b*x - c` | `x, y` | `a = 1`, `b = 2`, `c = 3` | quadratic-ის graph |
| 6 | `distance_components` | `(x - p)*(x - p) + (y - q)*(y - q) - d*d` | `x, y` | `p = 1`, `q = -1`, `d = 2` | distance formula კვადრატში |
| 7 | `midpoint_component` | `x + y/2 - m` | `x, y` | `m = 3` | midpoint-ის ერთი კოორდინატი |
| 8 | `slope_form` | `y - w/x - v` | `x, y` | `w = 2`, `v = 1` | slope relation, ერთადერთი ნამდვილი `/x` |
| 9 | `pythagorean_form` | `a*a + b*b - c*c` | `a, b` | `c = 2` | Pythagorean relation `(a, b)` სიბრტყეში |
| 10 | `trapezoid_area` | `(x + y)*h/2 - s` | `x, y` | `h = 2`, `s = 3` | ტრაპეციის ფართობი, პარალელურ გვერდებს შორის |
| 11 | `circle_through_origin` | `x*x + y*y - a*x - b*y` | `x, y` | `a = 2`, `b = 2` | წრეწირი constant term-ის გარეშე |
| 12 | `degenerate_pair` | `(x - y)*(x + y)` | `x, y` | - | ორი ხაზი ნამრავლად, control |

**Generation 1-ს არ აქვს exponentiation**, ამიტომ ყოველი კვადრატი ნამრავლადაა დაწერილი: `x*x`, და არა `x**2`. ეს არ არის სტილის არჩევანი - ეს არის შესასწავლი grammar-ის თვისება, და სწორედ ის თვისებაა, რომელიც კვადრატებს precedence permutation-ის მიმართ დაუცველს ხდის. `**`-ის მქონე grammar-ში ეს კითხვა სხვანაირად დაისმებოდა.

Objects იდარებიან პროექტის არსებული **semantic key**-ით - `(canonical expression, domain, excluded points)` - რომელიც `parseatlas.alternative_mathematics`-იდან **იმპორტირებულია** და აქ ხელახლა არ არის დაწერილი, ისე რომ "იგივე object" ნიშნავს ზუსტად იმას, რასაც `analyze_expression`-ში ნიშნავს. Standing disclosure ამ key-ზე: `canonical.py` `domain`-ში ყოველთვის ლიტერალურ `"R"`-ს წერს, ამიტომ ოპერატიული discrimination არის `(canonical form, excluded points)` - `NF-2026-00005`, იხ. შეზღუდვები.

## Classification: რა წესით ერქმევა label

`classify(expression, variables)` ჯერ expression-ს საერთო მნიშვნელზე დაჰყავს (`together`), შემდეგ ჰყოფს (`fraction`) და **numerator**-ს კლასიფიცირებს. ეს ორივე მიზეზით სწორია. მექანიკურად: `Poly` rational form-ს პირდაპირ უარყოფს, და სწორედ ამაზე მოკვდა ადრინდელი probe hyperbola-ზე. გეომეტრიულად: `N/D`-ის zero set არის `N`-ის zero set `D`-ის pole-ების გამოკლებით, ამიტომ curve-ს numerator ატარებს, ხოლო denominator - ნახვრეტებს. Denominator არასოდეს იკარგება ჩუმად: ის იწერება `denominator`, `denominator_set_aside`, `denominator_punctures` და `excluded_locus` ველებში, ცხრილში იბეჭდება და figure-ზე იხაზება dashed ხაზად.

Label-ების წესები, სრულად:

| label | წესი |
|---|---|
| `whole plane (identically zero)` | numerator არის `0` |
| `empty locus (constant in the coordinates)` | numerator-ს კოორდინატებში degree `0` აქვს და არ არის `0` |
| `line` | coordinate-degree `1` |
| `conic: circle` | coordinate-degree `2`, `B = 0`, `A = C`, `3x3` determinant არა-იდენტურად ნულოვანი |
| `conic: ellipse` / `parabola` / `hyperbola` | coordinate-degree `2`, non-degenerate, `B^2 - 4*A*C` `< 0` / `= 0` / `> 0` |
| `degenerate conic: two intersecting lines` | degree `2`, determinant იდენტურად `0`, `B^2 - 4*A*C > 0` |
| `degenerate conic: two parallel lines` / `a double line` | degree `2`, determinant `0`, `B^2 - 4*A*C = 0`; `double`, თუ factorisation-ს განმეორებადი linear factor აქვს |
| `degenerate conic: a single point` | degree `2`, determinant `0`, `B^2 - 4*A*C < 0` |
| `cubic curve` / `quartic curve` / `degree N curve` | coordinate-degree `3` / `4` / `N` |
| `conic (type set by the sign of B^2-4AC = ...)` | degree `2` symbolic discriminant-ით, რომლის ნიშანი real-parameter assumption-ებიდან არ გამომდინარეობს |
| `not polynomial in the coordinates after clearing denominators` | numerator საერთოდ არ არის polynomial |

`3x3` determinant არის `det [[A, B/2, D/2], [B/2, C, E/2], [D/2, E/2, F]]`, სტანდარტული conic discriminant.

ორი წესი, რომელიც ცალკე უნდა ითქვას, რადგან ორივე უარია და არა label:

**Degeneracy არის იდენტური განულება.** Determinant, რომელიც *შეიძლება* განულდეს parameter-ის კონკრეტულ მნიშვნელობაზე - წრეწირისთვის `-r**2` - curve-ს generic-ად non-degenerate-ად ტოვებს, ხოლო განულების locus ცალკე იწერება `degeneracy_locus`-ში. `r = 0` წრეწირს წერტილად აქცევს; ეს იმას არ ნიშნავს, რომ `x*x + y*y - r*r` წერტილია.

**Label, რომელიც coefficient-ებიდან არ მართლდება, არ გაიცემა.** `3` reading-ს ამ catalogue-ში symbolic discriminant აქვს, რომლის ნიშანი გადაუწყვეტელია (`-4*r`, `-4*d`, `-4*c`); მათ label-ის ნაცვლად უარი და სამივე branch უწერიათ, ხოლო catalogue-ის declared parameter values-ზე გადაწყვეტილი label ცალკე ველშია (`label_source: coefficients at the declared parameter values`). სამივე `r, d, c > 0`-ზე `conic: ellipse`-ია.

**Degree convention.** Plane curve-ის degree არის მისი degree **კოორდინატებში**. `x*x + y*y - r*r`-ში `r` curve-ების ოჯახს ასახელებს და არა სიბრტყის მიმართულებას, ამიტომ `total_degree` მხოლოდ declared coordinate-ებს ითვლის. Degree ყველა free symbol-ზე სხვა რიცხვია და ცალკე იწერება `ambient_total_degree`-ად. ორივე ცხრილშია, და სადაც ისინი განსხვავდებიან, იქ ეს ნათქვამია და არა არჩეული.

### Manager probe-ის ორი რიცხვი, ხელახლა გამოყვანილი

Manager-ის ორი probe ხელახლა გამოვიდა და **object count-ები ზუსტად დაემთხვა**:

```text
x*x + y*y - r*r     9 | 8 | 4 | 4     (4 distinct object)
y - m*x - c        13 | 12            (2 distinct object)
```

Label-ები კი ერთ ადგილას განსხვავდება, და მიზეზი disclosed უნდა იყოს: **ორი probe ორ სხვადასხვა degree convention-ს იყენებდა.** Circle-ის probe (`conic | quartic | cubic | cubic`) ითვლის degree-ს ყველა free symbol-ზე; line-ის probe (`line | curve with x*y`) ითვლის კოორდინატებში. ორივე ერთდროულად ვერ იქნება. Plane curve-ის degree კოორდინატებშია, ამიტომ ეს module მთელ catalogue-ზე ერთ convention-ს ატარებს, და ambient degree-ს ცალკე სვეტად ბეჭდავს - სადაც manager-ის circle label-ები ზუსტად აღდგება:

| object | grammars | coordinate degree | label (ეს report) | ambient degree | label ambient convention-ით |
|---|---|---|---|---|---|
| `-r**2 + x**2 + y**2` | `9` | `2` | `conic: circle` | `2` | conic |
| `-r*x*(r - y)*(x + y)` | `8` | `3` | `cubic curve` | `4` | quartic |
| `-r**2 + x*y*(x + y)` | `4` | `3` | `cubic curve` | `3` | cubic |
| `-r*y*(r - y) + x**2` | `4` | `2` | `conic: ellipse` | `3` | cubic |

ანუ `9 | 8 | 4 | 4` split ორივე convention-ში იდენტურია; მხოლოდ label-ები იცვლება. `8`-world reading კოორდინატებში cubic-ია და - რაც უფრო საინტერესოა - **reducible**: `-r*x*(r - y)*(x + y)` არის სამი სწორი ხაზი, `x = 0`, `y = r` და `x + y = 0`.

## დაკვირვებული შედეგები

### 1. სრული ცხრილი: `12` curve, `25` world, `48` distinct object

`300` cell (`12 x 25`), semantic key-ზე დაჯგუფებული. `48` distinct object სულ, `13` maximum ერთ curve-ზე, `1` invariant curve.

#### `line` - `y - m*x - c` - `2` object, `2` label, `G0`-ის group `13`

![line](figures/line.svg)

| object | worlds | canonical reading | classification | deg | ambient | `x*y` | denominator | grammars |
|---|---|---|---|---|---|---|---|---|
| `O01` | `13` | `-c - m*x + y` | line | `1` | `2` | no | - | `G0, G03, G04, G06, G13, G14, G15, G16, G17, G18, G20, G23, G24` |
| `O02` | `12` | `(c - x)*(m - y)` | degenerate conic: two intersecting lines | `2` | `2` | **yes** | - | `G01, G02, G05, G07, G08, G09, G10, G11, G12, G19, G21, G22` |

#### `circle` - `x*x + y*y - r*r` - `4` object, `3` label, `G0`-ის group `9`

![circle](figures/circle.svg)

| object | worlds | canonical reading | classification | deg | ambient | `x*y` | grammars |
|---|---|---|---|---|---|---|---|
| `O01` | `9` | `-r**2 + x**2 + y**2` | conic: circle | `2` | `2` | no | `G0, G13, G14, G15, G16, G17, G18, G23, G24` |
| `O02` | `8` | `-r*x*(r - y)*(x + y)` | cubic curve (სამი სწორი ხაზი) | `3` | `4` | **yes** | `G01, G02, G05, G07, G08, G11, G19, G21` |
| `O03` | `4` | `-r**2 + x*y*(x + y)` | cubic curve | `3` | `3` | no | `G03, G04, G06, G20` |
| `O04` | `4` | `-r*y*(r - y) + x**2` | conic: ellipse † | `2` | `3` | no | `G09, G10, G12, G22` |

† symbolic label: `conic (type set by the sign of B^2-4AC = -4*r)`; `r > 0`-ზე ellipse.

#### `ellipse` - `x*x/4 + y*y/9 - 1` - `13` object, `5` label, `G0`-ის group `5`

![ellipse](figures/ellipse.svg)

| object | worlds | canonical reading | classification | deg | `x*y` | denominator | grammars |
|---|---|---|---|---|---|---|---|
| `O01` | `5` | `x**2/4 + y**2/9 - 1` | conic: ellipse | `2` | no | `36` | `G0, G17, G18, G23, G24` |
| `O02` | `3` | `x**2/(8*y*(y + 4))` | degenerate conic: a double line | `2` | no | `8*y**2 + 32*y` | `G01, G03, G07` |
| `O03` | `3` | `x**2/(8*(y**2 + 4))` | degenerate conic: a double line | `2` | no | `8*y**2 + 32` | `G09, G13, G15` |
| `O04` | `3` | `x**2/4 + y**2/8` | degenerate conic: a single point | `2` | no | `8` | `G10, G12, G16` |
| `O05` | `2` | `x**2*y/(8*(y + 4))` | cubic curve (სამი ხაზი) | `3` | no | `8*y + 32` | `G02, G08` |
| `O06` | `2` | `x*(x + 4*y)*(y - 9)/36` | cubic curve (სამი ხაზი) | `3` | **yes** | `36` | `G19, G21` |
| `O07` | `1` | `(x**2/9 - y*(y + 4))/(y*(y + 4))` | conic: hyperbola | `2` | no | `9*y**2 + 36*y` | `G04` |
| `O08` | `1` | `x**2*(y - 9)/(9*(y + 4))` | cubic curve (სამი ხაზი) | `3` | no | `9*y + 36` | `G05` |
| `O09` | `1` | `(x**2*y/9 - y - 4)/(y + 4)` | cubic curve | `3` | no | `9*y + 36` | `G06` |
| `O10` | `1` | `x*y*(x + 4*y)/32` | cubic curve (სამი ხაზი) | `3` | no | `32` | `G11` |
| `O11` | `1` | `(x**2/9 - y**2 - 4)/(y**2 + 4)` | conic: hyperbola | `2` | no | `9*y**2 + 36` | `G14` |
| `O12` | `1` | `x*y*(x + 4*y)/36 - 1` | cubic curve | `3` | no | `36` | `G20` |
| `O13` | `1` | `x**2/4 + y**2/9 - y` | conic: ellipse | `2` | no | `36` | `G22` |

#### `hyperbola` - `x*x/4 - y*y/9 - 1` - `5` object, `3` label, `G0`-ის group `9`

![hyperbola](figures/hyperbola.svg)

| object | worlds | canonical reading | classification | deg | `x*y` | denominator | grammars |
|---|---|---|---|---|---|---|---|
| `O01` | `9` | `x**2/4 - y**2/9 - 1` | conic: hyperbola | `2` | no | `36` | `G0, G04, G06, G14, G17, G18, G20, G23, G24` |
| `O02` | `4` | `-x**2/(8*y*(y - 4))` | degenerate conic: a double line | `2` | no | `8*y**2 - 32*y` | `G01, G07, G09, G10` |
| `O03` | `4` | `-x**2*y/(8*y - 32)` | cubic curve (სამი ხაზი) | `3` | no | `8*y - 32` | `G02, G08, G11, G12` |
| `O04` | `4` | `-x**2/(8*y**2 - 32)` | degenerate conic: a double line | `2` | no | `8*y**2 - 32` | `G03, G13, G15, G16` |
| `O05` | `4` | `x*(x - 4*y)*(y - 9)/36` | cubic curve (სამი ხაზი) | `3` | **yes** | `36` | `G05, G19, G21, G22` |

#### `parabola` - `y - a*x*x - b*x - c` - `2` object, `2` label, `G0`-ის group `13`

![parabola](figures/parabola.svg)

| object | worlds | canonical reading | classification | deg | ambient | `x*y` | grammars |
|---|---|---|---|---|---|---|---|
| `O01` | `13` | `-a*x**2 - b*x - c + y` | conic: parabola | `2` | `3` | no | `G0, G03, G04, G06, G13, G14, G15, G16, G17, G18, G20, G23, G24` |
| `O02` | `12` | `-x*(a - y)*(b - x)*(c - x)` | quartic curve (ოთხი სწორი ხაზი) | `4` | `4` | **yes** | `G01, G02, G05, G07, G08, G09, G10, G11, G12, G19, G21, G22` |

#### `distance_components` - `(x - p)*(x - p) + (y - q)*(y - q) - d*d` - `4` object, `3` label, `G0`-ის group `9`

![distance_components](figures/distance_components.svg)

| object | worlds | canonical reading | classification | deg | ambient | `x*y` | grammars |
|---|---|---|---|---|---|---|---|
| `O01` | `9` | `-d**2 + (p - x)**2 + (q - y)**2` | conic: circle | `2` | `2` | no | `G0, G13, G14, G15, G16, G17, G18, G23, G24` |
| `O02` | `8` | `-d*(p - x)*(d + q - y)*(p + q - x - y)` | cubic curve (სამი ხაზი) | `3` | `4` | **yes** | `G01, G02, G05, G07, G08, G11, G19, G21` |
| `O03` | `4` | `-d**2 - (p - x)*(q - y)*(p + q - x - y)` | cubic curve | `3` | `3` | **yes** | `G03, G04, G06, G20` |
| `O04` | `4` | `d*(q - y)*(d + q - y) + (p - x)**2` | conic: ellipse † | `2` | `3` | no | `G09, G10, G12, G22` |

† symbolic label: `conic (type set by the sign of B^2-4AC = -4*d)`.

#### `midpoint_component` - `x + y/2 - m` - `4` object, `1` label, `G0`-ის group `9`

![midpoint_component](figures/midpoint_component.svg)

| object | worlds | canonical reading | classification | denominator | excluded points | grammars |
|---|---|---|---|---|---|---|
| `O01` | `9` | `-m + x + y/2` | line | `2` | - | `G0, G17, G18, G19, G20, G21, G22, G23, G24` |
| `O02` | `8` | `(-x - y)/(m - 2)` | line | `m - 2` | `m = 2` | `G01, G02, G03, G07, G08, G09, G13, G15` |
| `O03` | `4` | `-m + x/2 + y/2` | line | `2` | - | `G04, G05, G06, G14` |
| `O04` | `4` | `(x*(m - 2) - y)/(m - 2)` | line | `m - 2` | `m = 2` | `G10, G11, G12, G16` |

#### `slope_form` - `y - w/x - v` - `2` object, `2` label, `G0`-ის group `13`

![slope_form](figures/slope_form.svg)

| object | worlds | canonical reading | classification | deg | `x*y` | denominator | excluded | grammars |
|---|---|---|---|---|---|---|---|---|
| `O01` | `13` | `-v - w/x + y` | conic: hyperbola | `2` | **yes** | `x` | `x = 0` | `G0, G04, G05, G06, G14, G17, G18, G19, G20, G21, G22, G23, G24` |
| `O02` | `12` | `(w - y)/(v - x)` | line | `1` | no | `v - x` | `v = x` | `G01, G02, G03, G07, G08, G09, G10, G11, G12, G13, G15, G16` |

#### `pythagorean_form` - `a*a + b*b - c*c` - `4` object, `3` label, `G0`-ის group `9`

![pythagorean_form](figures/pythagorean_form.svg)

| object | worlds | canonical reading | classification | deg | ambient | cross | grammars |
|---|---|---|---|---|---|---|---|
| `O01` | `9` | `a**2 + b**2 - c**2` | conic: circle | `2` | `2` | no | `G0, G13, G14, G15, G16, G17, G18, G23, G24` |
| `O02` | `8` | `a*c*(a + b)*(b - c)` | cubic curve (სამი ხაზი) | `3` | `4` | **yes** | `G01, G02, G05, G07, G08, G11, G19, G21` |
| `O03` | `4` | `a*b*(a + b) - c**2` | cubic curve | `3` | `3` | no | `G03, G04, G06, G20` |
| `O04` | `4` | `a**2 + b*c*(b - c)` | conic: ellipse † | `2` | `3` | no | `G09, G10, G12, G22` |

† symbolic label: `conic (type set by the sign of B^2-4AC = -4*c)`.

#### `trapezoid_area` - `(x + y)*h/2 - s` - `3` object, `1` label, `G0`-ის group `9`

![trapezoid_area](figures/trapezoid_area.svg)

| object | worlds | canonical reading | classification | რომელი ხაზი | grammars |
|---|---|---|---|---|---|
| `O01` | `12` | `-h*(x + y)/(s - 2)` | line | `x + y = 0` | `G01, G02, G03, G07, G08, G09, G10, G11, G12, G13, G15, G16` |
| `O02` | `9` | `h*(x + y)/2 - s` | line | `x + y = 2*s/h` | `G0, G04, G06, G14, G17, G18, G20, G23, G24` |
| `O03` | `4` | `(h - 2*s)*(x + y)/2` | line | `x + y = 0` | `G05, G19, G21, G22` |

#### `circle_through_origin` - `x*x + y*y - a*x - b*y` - `4` object, `4` label, `G0`-ის group `9`

![circle_through_origin](figures/circle_through_origin.svg)

| object | worlds | canonical reading | classification | deg | grammars |
|---|---|---|---|---|---|
| `O01` | `9` | `-a*x - b*y + x**2 + y**2` | conic: circle | `2` | `G0, G13, G14, G15, G16, G17, G18, G23, G24` |
| `O02` | `8` | `x*y*(a - y)*(b - x)*(x + y)` | degree `5` curve (ხუთი სწორი ხაზი) | `5` | `G01, G02, G05, G07, G08, G11, G19, G21` |
| `O03` | `4` | `-a*x - b*y + x*y*(x + y)` | cubic curve | `3` | `G03, G04, G06, G20` |
| `O04` | `4` | `x**2 + y**2*(a - y)*(b - x)` | quartic curve | `4` | `G09, G10, G12, G22` |

#### `degenerate_pair` - `(x - y)*(x + y)` - `1` object, `1` label, `G0`-ის group `25`

![degenerate_pair](figures/degenerate_pair.svg)

| object | worlds | canonical reading | classification | grammars |
|---|---|---|---|---|
| `O01` | `25` | `(x - y)*(x + y)` | degenerate conic: two intersecting lines | ყველა `25` |

### 2. აგრეგატები

`300` cell-ის განაწილება classification-ის მიხედვით, და `48` distinct object-ისა:

```text
label                                       cells / 300     objects / 48
line                                             75               9
cubic curve                                      56              15
degenerate conic: two intersecting lines         37               2
conic: circle                                    36               4
conic: hyperbola                                 24               4
conic: ellipse                                   18               5
quartic curve                                    16               2
degenerate conic: a double line                  14               4
conic: parabola                                  13               1
degree 5 curve                                    8               1
degenerate conic: a single point                  3               1
```

`17` distinct object (`109` cell) არის degree `> 1` და მაინც სწორი ხაზების გაერთიანება: precedence permutation-ის ერთ-ერთი ყველაზე ხშირი შედეგი ის არის, რომ curve **იშლება ხაზების ნაკრებად**. `71` cell-ს `x*y` cross term აქვს, `49` cell-ს კი ისეთი denominator, რომელიც კოორდინატს შეიცავს - ანუ იმ world-ებში ეს curve-ები punctured-ია.

### 3. Survival: რომელი გეომეტრია გადარჩება

`survival_report` კითხულობს: რამდენ world-ში ინარჩუნებს curve **თავის საკუთარ classification-ს** (control world-ის label-ს). ეს არის `0036`-ის identity survival-ის გეომეტრიული ანალოგი.

| curve | written form | control label | survives | distinct objects | label-ების განაწილება |
|---|---|---|---|---|---|
| `degenerate_pair` | `(x - y)*(x + y)` | degenerate conic: two intersecting lines | `25`/`25` | `1` | two intersecting lines `25` |
| `midpoint_component` | `x + y/2 - m` | line | `25`/`25` | `4` | line `25` |
| `trapezoid_area` | `(x + y)*h/2 - s` | line | `25`/`25` | `3` | line `25` |
| `line` | `y - m*x - c` | line | `13`/`25` | `2` | line `13` ; two intersecting lines `12` |
| `parabola` | `y - a*x*x - b*x - c` | conic: parabola | `13`/`25` | `2` | parabola `13` ; quartic `12` |
| `slope_form` | `y - w/x - v` | conic: hyperbola | `13`/`25` | `2` | hyperbola `13` ; **line `12`** |
| `circle` | `x*x + y*y - r*r` | conic: circle | `9`/`25` | `4` | cubic `12` ; circle `9` ; ellipse `4` |
| `circle_through_origin` | `x*x + y*y - a*x - b*y` | conic: circle | `9`/`25` | `4` | circle `9` ; degree `5` `8` ; cubic `4` ; quartic `4` |
| `distance_components` | `(x - p)*(x - p) + (y - q)*(y - q) - d*d` | conic: circle | `9`/`25` | `4` | cubic `12` ; circle `9` ; ellipse `4` |
| `hyperbola` | `x*x/4 - y*y/9 - 1` | conic: hyperbola | `9`/`25` | `5` | hyperbola `9` ; cubic `8` ; double line `8` |
| `pythagorean_form` | `a*a + b*b - c*c` | conic: circle | `9`/`25` | `4` | cubic `12` ; circle `9` ; ellipse `4` |
| `ellipse` | `x*x/4 + y*y/9 - 1` | conic: ellipse | `6`/`25` | `13` | cubic `8` ; ellipse `6` ; double line `6` ; single point `3` ; hyperbola `2` |

სამი დაკვირვება ამ ცხრილიდან, რომელიც მარტო რიცხვებში არ ჩანს.

**Classification-ის გადარჩენა არ არის object-ის გადარჩენა.** `midpoint_component` `25`-ვე world-ში line-ია და მაინც `4` სხვადასხვა object: `x + y/2 = m`, `x + y = 0`, `(x + y)/2 = m` (ეს კი ორის ნამდვილი mean-ია), და `x = y`. ორი მათგანი `m`-ს საერთოდ კარგავს. იგივე `trapezoid_area`-ზე: `25`-ვე world line-ია, მაგრამ `16` world (`12 + 4`) კითხულობს ხაზს `x + y = 0`, რომელშიც ფართობი `s` საერთოდ აღარ არის, და მხოლოდ `9` world კითხულობს სწორ ხაზს `x + y = 2*s/h`. Label გადარჩა; გეომეტრია არა.

**`ellipse` ერთადერთი entry-ია, სადაც `G0`-ის group-ს გარეთაც არსებობს იმავე label-ის reading.** `survives = 6`, მაშინ როცა `G0`-ის group `5`-ია: `G22` ცალკე object-ს კითხულობს (`x**2/4 + y**2/9 - y`), რომელიც მაინც ellipse-ია. სწორედ ეს განსხვავებაა survival-ისა და object identity-ს შორის.

**ერთი curve საპირისპირო მიმართულებით მიდის.** `slope_form` `G0`-ში hyperbola-ია (`x*y` წევრით), ხოლო `12` world-ში ის **line**-ია. ანუ precedence permutation ყოველთვის არ ანგრევს გეომეტრიას - ის სირთულეს გადაანაწილებს. იმ `12` world-ში ორ წერტილს შორის slope-ის ფორმულა უფრო მარტივი object-ია, ვიდრე ჩვენთან.

### 4. `G0`-ის ადგილი

`G0`-ის group size თითო curve-ზე:

```text
degenerate_pair 25 | line 13 | parabola 13 | slope_form 13
circle 9 | hyperbola 9 | distance_components 9 | midpoint_component 9
pythagorean_form 9 | trapezoid_area 9 | circle_through_origin 9
ellipse 5
```

`G0` **არცერთ curve-ზე მარტო არ დგას**; მისი მინიმალური group `5`-ია. Agreement `G0`-თან, `12` curve-დან:

```text
G0  12   G01  1   G02  1   G03  3   G04  6   G05  2   G06  6   G07  1   G08  1
G09  1   G10  1   G11  1   G12  1   G13  7   G14 10   G15  7   G16  7   G17 12
G18 12   G19  3   G20  7   G21  3   G22  3   G23 12   G24 12
```

`4` world - `G17` (`* > / > + > -`), `G18` (`* > / > - > +`), `G23` (`/ > * > + > -`), `G24` (`/ > * > - > +`) - მთელ catalogue-ს ზუსტად `G0`-ის მსგავსად კითხულობს. ეს ოთხივე ის ordering-ია, რომელიც `*`-სა და `/`-ს ორივე additive operator-ზე მაღლა ტოვებს, ანუ `G0`-ის tied level-ს strict-ად ალაგებს ისე, რომ არსებული tie არ ირღვევა. `G0` ამ catalogue-ზე ამ ხუთეულის ჩვეულებრივი წევრია.

## Figures

`12` SVG, თითო catalogue curve-ზე ერთი, `experiments/0040_geometry_atlas/figures/`-ში. თითოეული ინახავს ამ curve-ის **ყველა** distinct reading-ს გვერდიგვერდ, თითო panel classification-ითა და world count-ით, ისე რომ მკითხველი ერთი შეხედვით ხედავს, რომ ჩვენი წრეწირი ოთხი სხვადასხვა რამაა.

**რეგენერაციის ბრძანება:**

```text
python -m parseatlas.geometry_atlas figures experiments/0040_geometry_atlas/figures
```

იგივე ბრძანება თითო figure-ის ბოლო სტრიქონზეც წერია. Headline რიცხვები:

```text
python -m parseatlas.geometry_atlas headline
```

**რატომ არის SVG პირდაპირ text-ად დაწერილი.** `matplotlib` და `numpy` არ არის დაინსტალირებული, და პროექტი განზრახ მხოლოდ `sympy`-ზეა დამოკიდებული. Pure Python-ით დაწერილი SVG dependency-free-ია, git-ში diff-დება, GitHub-ზე რენდერდება და რეგენერირებადია - ეს ზუსტად ამ repository-ის დისციპლინაა. Figure, რომელიც ვერ რეგენერირდება, არ არის მტკიცებულება.

**როგორ იხაზება curve.** Implicit curve იხაზება grid-ზე expression-ის ნიშნის sampling-ით და level `0`-ზე marching-squares contour-ით, სუფთა Python-ში (`zero_set_segments`, `145 x 145` node). სამი დეტალი, რომელიც ცალკე უნდა ითქვას:

- იხაზება **numerator**-ის zero set და არა თვითონ rational reading-ისა. Numerator polynomial-ია და უწყვეტი, ამიტომ tracer-ს pole-ზე გადახტომა არასოდეს უწევს. Denominator-ის საკუთარი zero set იმავე tracer-ით dashed ხაზად ედება ზემოდან - ეს არის ის locus, რომელიც curve-იდან ამოღებულია.
- იხაზება numerator-ის **square-free part**. Zero set ამით არ იცვლება, მაგრამ განმეორებადი factor-ი function-ს ნიშნის შეცვლის გარეშე ეხება ნულს, და მხოლოდ sign change-ზე მომუშავე tracer არაფერს დახატავდა. `x*x` არის double line და ხაზად უნდა დაიხატოს.
- **Zero set, რომელიც ერთი წერტილია, არ იხაზება sampling-ით - ის იხსნება.** `x*x/4 + y*y/8` მხოლოდ origin-ში ნულდება და არცერთი grid edge იქ ნიშანს არ იცვლის. Sampling ამას ვერ გაასწორებს: ის, დაჯდება თუ არა grid ზუსტად იმ წერტილზე, curve-ის თვისება არ არის. Classification-ს ეს შემთხვევა უკვე დასახელებული აქვს (`degenerate conic: a single point`), ხოლო conic-ისთვის ის წერტილი centre-ია - ორი კერძო წარმოებულის, `2*A*x + B*y + D` და `B*x + 2*C*y + E`, ერთდროული ნული, ანუ ერთი ზუსტი linear solve (`single_point`).

Panel-ები დახატულია catalogue-ის declared parameter მნიშვნელობებზე; classification კი symbolic form-ისაა. Figure-ის ყოველ panel-ს რაღაც უხატია - ეს test-ითაა დაცული **ორივე grid parity-ზე**, რადგან panel, რომელიც მხოლოდ მაშინ ხატავს, როცა grid curve-ს დაემთხვა, დახატული არ არის, უბრალოდ გაუმართლა. Ცარიელი panel ნიშნავს, რომ parameter singular locus-ზე დაჯდა.

ყოველ SVG-ს აქვს explicit background `rect` და explicit `fill`/`stroke` ყოველ mark-ზე, რადგან artifact და README ორივე ფონზე რენდერდება, ხოლო დაუხატავი SVG ერთ-ერთზე უხილავია. ღერძები, tick-ები და label-ები viewBox-ის შიგნით რჩება: figure-ის სიგანე ყველაზე გრძელი ტექსტური სტრიქონიდან გამომდინარეობს, panel-ის შიდა ტექსტი კი ხელმისაწვდომ პიქსელებზეა შეჭრილი. ორივე test-ითაა დაცული.

## Multicore

Repository policy multicore by default-ია გაზომილი გადაწყვეტილებით. Work unit არის თითო `(curve, world)` **cell** და არა curve: `12 x 25 = 300` item pool-ზე ბევრად უკეთ ნაწილდება, ვიდრე `12`. Worker count `resolve_worker_count`-იდან მოდის, `cpu_count - 1` (`15` ამ host-ზე, `16` core), interactive session-ისთვის ერთი core headroom-ით; hardcoded constant არსად არის.

**გაზომვა A - `parallelism_measurement`, სრული `12`-curve catalogue, `25` grammar, `3` დამოუკიდებელი გაშვება, თითო სუფთა interpreter-ში:**

```text
run   sequential_s   parallel_s   speedup   workers   identical_results
 1        9.32          3.71        2.51       15          true
 2        7.26          3.67        1.98       15          true
 3        7.62          4.03        1.89       15          true

cpu_count 16 | item_count 300 | automatic_worker_count 15 | faster_path: parallel (3/3)
```

Parallel სამივე გაშვებაზე იმარჯვებს, ამიტომ default parallel-ია.

**გაზომვა B - რატომ არის speedup `2` და არა `15`.** Pool-ის საკუთარი startup ცალკე გაიზომა - `15` worker, spawn start method, `300` triviality item, სადაც თითო worker `parseatlas.geometry_atlas`-ს და მასთან ერთად `sympy`-ს იმპორტებს:

```text
pool startup (15 worker, sympy import-ის ჩათვლით)     2.82 s
parallel wall clock (გაზომვა A)                  3.67 - 4.03 s
```

ანუ parallel wall clock-ის `~2.8 s` startup-ია და მხოლოდ `~1 s` ნამდვილი მუშაობა, მაშინ როცა იგივე მუშაობა sequential-ად `7.3 - 9.3 s`-ია. Parallelism თავის საქმეს აკეთებს; ამ catalogue-ის ზომაზე pool-ის ჩამოშენება დომინირებს, და უფრო დიდ catalogue-ზე speedup გაცილებით მაღალი იქნებოდა.

**გაზომვა C - decomposition ceiling.** Cell-ების ცალკეული cost-ები (`300` cell, sequential, ერთი process):

```text
total                    7.97 s
median cell              0.021 s
ყველაზე ნელი cell        0.189 s   (line, G0)
total / slowest          42.3
```

Ceiling `42` ბევრად მაღლა დგას `15` worker-ზე, ანუ work unit საკმარისად წვრილია და შემზღუდველი არის worker count და pool overhead, და არა რომელიმე განუყოფელი cell. ეს გაზომვა A-სა და B-ს ეთანხმება.

Parallelism მხოლოდ სიჩქარეს ცვლის - `identical_results` ამას პირდაპირ ამოწმებს object id-ების, canonical form-ების, label-ების, degree-ების, cross-term flag-ებისა და grammar list-ების შედარებით და არა ვარაუდით; სამივე გაშვებაზე `true`.

## ინტერპრეტაცია

Founding question-ის გეომეტრიული პასუხი ერთი წინადადებით: **worlds-ის თითქმის ნახევარში ის string, რომელსაც ჩვენ ხაზს ვეძახით, ხაზს არ ნიშნავს.**

ეს უფრო მკვეთრია, ვიდრე `0035`-ის algebraic შედეგი, ორი მიზეზით. პირველი: classification უხეში label-ია. Coefficient-ის ცვლილება შეიძლება უმნიშვნელო იყოს; `line` -> `degenerate conic` არა. მეორე: გეომეტრიაში object დახატვადია, და სურათი არ კამათობს. `figures/circle.svg`-ის ოთხი panel ერთსა და იმავე written form-ს აჩვენებს, და მხოლოდ ერთი მათგანი წრეწირია.

მექანიზმი ყველგან ერთია: `x*x` და `y*y` მხოლოდ იმიტომაა კვადრატი, რომ `*` მაღლა დგას. როცა `*` ჩამოდის, `x*x + y*y` აღარ არის ორი კვადრატის ჯამი, არამედ სულ სხვა ნამრავლი, და ის ნამრავლი ხშირად **იშლება**: `48` distinct object-იდან `17` არის სწორი ხაზების გაერთიანება. ეს არის ამ ექსპერიმენტის ყველაზე მოულოდნელი structural შედეგი - precedence permutation curve-ს არა უბრალოდ ამახინჯებს, არამედ მას წრფივ კომპონენტებად შლის. `x*x + y*y - r*r` `8` world-ში სამი სწორი ხაზია; `y - a*x*x - b*x - c` `12` world-ში ოთხი; `x*x + y*y - a*x - b*y` `8` world-ში ხუთი.

იმ world-ებში conic sections-ის თეორია იმ ფორმით არ დაიწერებოდა. Discriminant `B^2 - 4*A*C` degree-`2` object-ის ინსტრუმენტია; იმ world-ებში ის written form, რომელიც ჩვენ conic-ს გვაძლევს, cubic-ს ან ხაზების ნაკრებს გვაძლევს, ხოლო conic-ის მისაღებად სხვა string იქნებოდა ყველაზე იაფი. სწორედ ის string გახდებოდა "the equation of a circle".

მეორე მხრივ, არსებობს ნამდვილი convention-independent გეომეტრია, და ის ზუსტად იქ არის, სადაც notation არჩევანს არ ტოვებს: `(x - y)*(x + y)` სრულად parenthesized-ია და `25`-ვე world-ში იდენტურია. აქ `0035`-ის დასკვნა ზუსტად მეორდება - notation არ წყვეტს ყველაფერს; ის წყვეტს იქ, სადაც mixed operator-ები precedence-ის კითხვას სვამენ.

და ბოლოს, `G0` აქაც არ არის პრივილეგირებული. `4` სრული twin, არცერთი curve, სადაც ის მარტოა, და `ellipse`-ზე ის `5`-კაციან group-შია `25`-იდან. Conventional order ამ გაზომვაშიც ordinary member-ია.

```text
written form -> grammar -> curve -> classification -> drawing
```

## შეზღუდვები

- **Classification არის numerator-ისა და არა თვითონ reading-ისა.** Expression საერთო მნიშვნელზე დაჰყავს და label numerator-ს ერქმევა; denominator ცალკე იწერება (`denominator`, `denominator_punctures`, `excluded_locus`) და figure-ზე dashed ხაზად იხაზება. ეს გეომეტრიულად სწორია - `N/D`-ის zero set არის `N`-ის zero set pole-ების გამოკლებით - მაგრამ ეს ნიშნავს, რომ label curve-ს **punctures-ის გარეშე** აღწერს. `x**2/(8*y*(y + 4))` არის double line `x = 0` ორი ამოღებული წერტილით; label ამ ორ წერტილს არ ასახელებს.
- **Conic-ის label-ები real და imaginary locus-ს არ არჩევენ.** წესი შიშველი discriminant-ია, ამიტომ `x*x + y*y + 4` ღებულობს label-ს `conic: circle`, თუმცა მისი **ნამდვილი zero set ცარიელია**. სტანდარტული კლასიფიკაცია ამ შემთხვევებს `sign((A+C)·det)`-ით გამოყოფს; ჩვენ ეს არ გვაქვს. Review-მ ცალკე შეამოწმა, რომ ეს ამ deliverable-ზე **არასდროს ირთვება**: 300-ივე უჯრედი გამოცხადებულ პარამეტრებზე შემოწმდა და conic label ცარიელი real locus-ით **0-ჯერ გვხვდება**, ანუ არცერთი რიცხვი, ცხრილის სტრიქონი ან figure არ იცვლება. მაგრამ სხვა catalogue-ზე ეს გაჩნდებოდა.
- **Catalogue hand-chosen-ია.** `12` entry ასახავს განსჯას იმის შესახებ, თუ რა ითვლება standard-ად გეომეტრიაში. სხვა არჩევანი invariant/fractured-ის სხვა თანაფარდობას მოგვცემდა. კონკრეტულად, `degenerate_pair` განზრახ არის დამატებული სწორედ იმის შესამოწმებლად, არსებობს თუ არა invariant curve - ეს არ არის random sample.
- **Generation 1-ს არ აქვს exponentiation, ამიტომ კვადრატები ნამრავლადაა დაწერილი.** `x*x` არის `x**2`-ის ერთადერთი გამოსახატავი ფორმა ამ grammar-ში, და სწორედ ეს ხდის მას precedence-ის მიმართ დაუცველს. `**`-ის მქონე grammar-ში `x**2 + y**2 - r**2` სავარაუდოდ ბევრად უფრო სტაბილური იქნებოდა, და ეს კითხვა სხვა ექსპერიმენტია.
- **Class-შეცვლილი curve არ არის უარესი curve.** ის არის **სხვა object**, რომელსაც ის world შეისწავლიდა. `-r*x*(r - y)*(x + y)` სამი სწორი ხაზია და სავსებით ღირსეული გეომეტრიული object-ია; უბრალოდ ის არ არის წრეწირი. ეს report არსად არ ამბობს, რომ conventional order უკეთესია.
- **Degree კოორდინატებში ითვლება.** Parameter-ები (`r`, `m`, `c`, `d`, ...) degree-ს არ ზრდიან, რადგან ისინი ოჯახს ასახელებენ და არა სიბრტყის მიმართულებას. Ambient degree ცალკე სვეტშია და manager probe-ის circle label-ები სწორედ იმ სვეტიდან აღდგება; ორი convention სხვა label-ებს იძლევა და იგივე object count-ებს.
- **Conditional label-ები parameter-ის ნიშანზეა დამოკიდებული.** `3` reading-ის symbolic discriminant არის `-4*r`, `-4*d`, `-4*c`, რომელთა ნიშანი real-parameter assumption-ებიდან არ გამომდინარეობს. ცხრილში `†`-ით მონიშნული label არის catalogue-ის declared მნიშვნელობებზე გადაწყვეტილი (`r, d, c > 0` -> ellipse); უარყოფით მნიშვნელობებზე იგივე reading hyperbola-ა.
- **Degeneracy იდენტური განულებაა.** Determinant, რომელიც კონკრეტულ parameter-ზე შეიძლება განულდეს (`-r**2`), curve-ს non-degenerate-ად ტოვებს და locus ცალკე იწერება. ეს არჩევანია და არა თეორემა; `r = 0`-ზე წრეწირი მართლაც წერტილია.
- **Figure-ები sampling-ია.** Marching squares `145 x 145` grid-ზე მუშაობს და curve-ს polyline-ებით აპროქსიმირებს. Node-ებს შორის ის არაფერს ამბობს, და მკვეთრი cusp ან ორი ძალიან ახლო ტოტი grid-ის რეზოლუციაზე დაბლა დაიკარგება. Isolated-zero fallback მხოლოდ იმ node-ებს აჩვენებს, რომლებზეც grid ზუსტად დაჯდა.
- **Window არჩეულია.** ყველა figure `[-6, 6] x [-6, 6]`-შია, გარდა `ellipse`-ისა, რომელიც `[-9, 9]`-ია, რადგან მისი ერთ-ერთი reading hyperbola-ა `x = +-6` vertex-ებით. სხვა window curve-ის სხვა ნაწილს აჩვენებდა; classification window-ზე არ არის დამოკიდებული, სურათი კი არის.
- **`domain` semantic key-ში ინერტულია** (`NF-2026-00005`). Triple `(canonical, domain, excluded points)` პროექტისაა და აქ უცვლელად, იმპორტით გამოიყენება, მაგრამ `canonical.py` `domain`-ს ყოველთვის `"R"`-ს აყენებს, ამიტომ ფაქტობრივი discrimination ორკომპონენტიანია. ამ ექსპერიმენტის არცერთი დათვლა ამით არ იცვლება - `48`-ვე distinct object `48` განსხვავებულ canonical text-ს შეესაბამება, ანუ excluded points-საც კი არ დასჭირვებია გამყოფის როლი - მაგრამ guarantee ისე უნდა ჟღერდეს, როგორც არის.
- **Excluded points პროექტის convention-ითაა.** `canonical.undefined_terms` denominator-ს ალფავიტურად პირველი ცვლადის მიმართ ხსნის, ამიტომ `slope_form`-ის `12`-world reading-ის excluded point იწერება როგორც `v = x` და არა `x = v`. ეს key-ის თვისებაა და უცვლელად არის აღებული.
- **Speedup ერთ host-ზეა გაზომილი** (`16` core, Windows, spawn start method). სხვა host-ზე რიცხვი სხვა იქნება; გადაწყვეტილება ხელახლა უნდა გაიზომოს და არა გადმოწერილი.

## Evidence-ის კლასიფიკაცია

- **Observations** (executable, ამ repository-ში რეპროდუცირებადი): line-ის `13`/`12` split და dissenting group-ის `x*y` წევრი; circle-ის `4` object და `9 | 8 | 4 | 4` split; `48` distinct object `300` cell-ზე; per-curve survival counts; `17` object, რომელიც ხაზების გაერთიანებაა; `G0`-ის group size-ები და მისი `4` twin; label-ების განაწილება; figure-ების panel counts; multicore timing.
- **Interpretation** (გაზომილიდან გამოტანილი და არა თვითონ გაზომილი): მტკიცება, რომ იმ world-ების გეომეტრები **ამ** object-ებს შეისწავლიდნენ და conic sections-ის თეორიას სხვა written form-ზე ააშენებდნენ. ეს არის notational-cost არგუმენტი და არა measurement.
- **არ არის claimed**: რომ conventional order უკეთესია ან უარესია; რომ `24 + 1` world-ის რაიმე universal law არსებობს; რომ catalogue representative sample-ია მთელი გეომეტრიისა; რომ რომელიმე world-ის reading უფრო ან ნაკლებად "ნამდვილი" curve-ია.

## ვალიდაცია

```text
tests/test_geometry_atlas.py: 33 passed
სრული suite:                 841 passed   (755 ამ card-ის გაშვებისას; სხვაობა
                                           ზუსტად ორი პარალელური card-ის ტესტებია)
```

Pin-ები `tests/test_geometry_atlas.py`-ში:

```text
test_the_circle_is_four_different_objects_and_ours_is_the_nine_world_group
test_in_twelve_of_twenty_five_worlds_the_equation_of_a_line_is_not_a_line
test_classify_names_a_circle_an_ellipse_and_a_hyperbola_by_hand_checked_discriminants
test_classify_names_the_parabola_and_the_four_degenerate_conics
test_classify_refuses_a_label_it_cannot_justify_and_says_which_sign_decides_it
test_a_determinant_that_can_vanish_is_not_the_same_as_one_that_does
test_classify_counts_degree_in_the_coordinates_and_reports_the_ambient_degree_separately
test_classify_sets_the_denominator_aside_instead_of_dying_on_it
test_classify_never_crashes_anywhere_in_the_full_sweep
test_the_key_still_carries_excluded_points_even_though_they_split_nothing_here
test_every_svg_the_report_references_exists_and_is_not_empty
test_every_figure_is_well_formed_paints_its_own_ground_and_stays_inside_the_viewbox
test_every_panel_of_every_figure_actually_draws_something
test_the_single_point_panel_draws_its_point_at_either_grid_parity
test_the_saddle_cell_pairs_its_four_crossings_by_the_centre_value
test_the_sequential_and_parallel_paths_produce_the_same_atlas
```

`test_classify_never_crashes_anywhere_in_the_full_sweep` არის ის test, რომელიც ადრინდელი probe-ის მარცხს კეტავს: ის `12` curve-ს `25`-ვე grammar-ში კითხულობს - `300` cell - და თითოეულზე მოითხოვს არა-ცარიელ label-სა და family-ს. Hyperbola-ს rational reading-ები, რომლებზეც `Poly` სწორედ ჩავარდებოდა, ამ sweep-შია.

Mutation testing ჩატარდა **isolated copy**-ზე: `src/parseatlas`, test file და `experiments/0040_geometry_atlas/` scratch tree-ში დაკოპირდა, `PYTHONPATH` იმ ასლზე მიმართა (ეს run-ის დასაწყისში `parseatlas.__file__`-ით მოწმდება), და თითო mutation ცალკე გაეშვა. Repository არ შეხებია.

```text
BASELINE                                                                       33 passed
KILLED   classification switched to the ambient degree over all free symbols     7 failed
KILLED   the denominator is dropped instead of being set aside                   1 failed
KILLED   a conditional label is guessed instead of refused                       2 failed
KILLED   degeneracy decided by "can vanish" instead of "vanishes identically"    3 failed
KILLED   the circle test drops A == C, so every ellipse becomes a circle         5 failed
KILLED   the discriminant sign inverted (ellipse and hyperbola swapped)          7 failed
KILLED   the double-line refinement dropped (a repeated factor reads parallel)   2 failed
KILLED   the square-free part dropped, so a double line draws nothing            2 failed
KILLED   the exact single-point solve removed from the panel                     2 failed
KILLED   the semantic key reduced to canonical text alone                        6 failed
KILLED   the semantic key drops excluded points                                  1 failed
KILLED   object groups ordered smallest first                                    8 failed
KILLED   worker count loses the core headroom                                    1 failed
KILLED   the SVG background rect is dropped                                      1 failed
KILLED   panel text is emitted unclipped, so it runs past the viewBox            1 failed
KILLED   the marching-squares saddle case pairs the crossings the other way      1 failed
KILLED   the domain component of the key silently changed ("R" -> "CONSTANT")    3 failed
SURVIVED (მოსალოდნელი) domain replaced by the constant it always is ("R" -> "R")

17/18 mutants killed
```

ერთი survivor განზრახია და ის `NF-2026-00005`-ის მტკიცებულებაა: `semantic_key`-ში `canonical["domain"]`-ის ლიტერალური `"R"`-ით ჩანაცვლება `33`-ვე test-ს მწვანედ ტოვებს, რადგან `domain` მართლაც არასოდეს იცვლება. მისი გვერდით მდგარი ორი mutant კი კვდება: ის, რომელიც `domain`-ს **სხვა** მნიშვნელობას აძლევს (`"CONSTANT"`), და ის, რომელიც key-ს მთლიანად canonical text-ზე დაიყვანს - ანუ ველი კითხულობს კიდეც, უბრალოდ არაფერს არჩევს.

`the semantic key drops excluded points` პირველ გაშვებაზე გადარჩა და მასზე დაემატა targeted test (`test_the_key_still_carries_excluded_points_even_though_they_split_nothing_here`), რომელიც ორივეს pin-ავს: იმას, რომ key მართლაც ატარებს excluded points-ს (`slope_form`-ის `G0` reading-ს აქვს `x = 0`), და იმ გაზომილ ფაქტს, რომ **ამ** catalogue-ზე ისინი არცერთ ორ object-ს არ ჰყოფენ, რადგან `48`-ვე object-ს უკვე თავისი canonical text აქვს (`restriction_split_objects = 0`).
