# ParseAtlas ექსპერიმენტი 0019: operator-support reduction

## მიზანი

0017 და 0018 grammar-space-ს მთლიანად, `24` strict grammar-ის დონეზე ზომავდნენ. აქ საპირისპირო კითხვას ვსვამთ: რამდენი grammar უნდა გავუშვათ საერთოდ, რომ კონკრეტული expression-ის ყველა შესაძლო AST ვნახოთ.

განვსაზღვროთ `O(E)` — token sequence-ში ფაქტობრივად შემხვედრი binary operator-ების SET (`+ - * /`-ის subset). გამოსაცდელი claim:

```text
parse(E, G) იძლევა byte-identical serialized AST-ს ნებისმიერი ორი strict grammar-ისთვის,
რომელთა precedence ordering O(E)-ზე ერთსა და იმავე relative order-ად restrict-დება.
```

აქედან გამომდინარე `24` strict grammar უნდა დაიყოს ზუსტად `factorial(|O(E)|)` block-ად, თითო `24 / factorial(|O(E)|)` ზომის, და თითო block უნდა იძლეოდეს ერთადერთ AST-ს.

## Corpus

შემოწმდა ათი expression, support size `1`-დან `4`-მდე:

```text
a - b - c
a/b/c
a + b - c
a + b*c
a + b - c*d
a/b + c - d
2*t + 1 - t/2
a + b*c - d/e
2*x*x + 1 - x/2
a - b*c + d/e - f
```

Support ყოველთვის `parseatlas.tokenizer.tokenize`-ის `operator` token-ებიდან იღება და არა raw string-ის სკანირებით. ეს არსებითია: `t/2`-ში `/` არის operator, ხოლო `1/2`-ში იგივე სიმბოლო rational literal-ის ნაწილია და support-ში არ შედის.

## დაკვირვებული შედეგები

| expression | support | \|O(E)\| | block count | block size | distinct AST | bound = factorial(\|O\|) |
| --- | --- | --- | --- | --- | --- | --- |
| `a - b - c` | `-` | 1 | 1 | 24 | 1 | 1 |
| `a/b/c` | `/` | 1 | 1 | 24 | 1 | 1 |
| `a + b - c` | `+ -` | 2 | 2 | 12 | 2 | 2 |
| `a + b*c` | `+ *` | 2 | 2 | 12 | 2 | 2 |
| `a + b - c*d` | `+ - *` | 3 | 6 | 4 | 5 | 6 |
| `a/b + c - d` | `/ + -` | 3 | 6 | 4 | 5 | 6 |
| `2*t + 1 - t/2` | `* + - /` | 4 | 24 | 1 | 14 | 24 |
| `a + b*c - d/e` | `+ * - /` | 4 | 24 | 1 | 14 | 24 |
| `2*x*x + 1 - x/2` | `* + - /` | 4 | 24 | 1 | 14 | 24 |
| `a - b*c + d/e - f` | `- * + /` | 4 | 24 | 1 | 19 | 24 |

- ათივე expression-ზე თითო block-ის distinct serialized AST count არის ზუსტად `1`.
- ათივე expression-ზე block count უდრის `factorial(|O(E)|)`-ს და ყველა block თანაბარი ზომისაა.
- `all_reductions_hold`: `True`.
- `mean_enumeration_saving`: `0.525`.

Enumeration saving თითო expression-ზე `1 - factorial(|O(E)|) / 24` არის, ანუ support size `1`-ზე `24`-დან მხოლოდ `1` grammar-ის გაშვება საკმარისია, support size `2`-ზე `2`, size `3`-ზე `6`, size `4`-ზე კი reduction არაფერს არ ზოგავს.

## Symbolic justification

`Parser._expression(minimum_power)` მხოლოდ ორი სახის შედარებას აკეთებს:

```text
self._powers[self._current.value] >= minimum_power
```

სადაც `minimum_power` ან `0`-ია (top level და parenthesized subexpression), ან `self._powers[operator] + 1` — უკვე consume-ული operator-ის power. მთელი integer power-ებისთვის `power(next) >= power(op) + 1` იგივეა, რაც `power(next) > power(op)`.

ე.ი. parser მხოლოდ იმ operator-ების binding power-ებს ადარებს ერთმანეთს, რომლებსაც ფაქტობრივად შეხვდა token sequence-ში; `minimum_power = 0`-იანი შედარება ყოველთვის True-ა, რადგან strict grammar-ის ყველა power `>= 1`. აქედან: `O(E)`-ში არმყოფი operator-ის პოზიცია precedence ordering-ში ვერავითარ branch-ს ვერ ცვლის, ხოლო `O(E)`-ზე ერთნაირად restrict-დებული ორი grammar ყველა შედარებაზე ერთსა და იმავე პასუხს აძლევს parser-ს — მაშასადამე იდენტურ AST-ს. ეს **symbolically justified** არგუმენტია, corpus-ისგან დამოუკიდებელი.

Block-ების სტრუქტურა ამის შემდეგ წმინდა კომბინატორიკაა: `4` ელემენტის `24` permutation-ის restriction `k`-ელემენტიან subset-ზე იძლევა `factorial(k)` სხვადასხვა order-ს, თითოს უკან `24 / factorial(k)` permutation დგას.

## დარჩენილი collapse — ღია კითხვა

მთავარი და ხაზგასასმელი დაკვირვება: support reduction UPPER BOUND-ია და არა ზუსტი მნიშვნელობა. Support size `3`-ზე bound `6`-ია, დაფიქსირდა კი `5` distinct AST; support size `4`-ზე bound `24`-ია, დაფიქსირდა `14`, `14`, `14` და `19`.

კონკრეტული merged restrictions — corpus-ზე სულ `25` merged class დაფიქსირდა და ქვემოთ ჩამოთვლილია ყველა მათგანი, გენერირებული ქვემოთ მოცემული ვალიდაციის ბრძანებით (თითო ხაზი — ერთი merged class: სხვადასხვა block იდენტური AST-ით):

```text
a + b - c*d       : [+ * -] == [* + -]
a/b + c - d       : [- / +] == [/ - +]
2*t + 1 - t/2     : [+ * / -] == [+ / * -] == [/ + * -]
2*t + 1 - t/2     : [+ / - *] == [/ + - *]
2*t + 1 - t/2     : [- * + /] == [* - + /]
2*t + 1 - t/2     : [- * / +] == [- / * +] == [* - / +]
2*t + 1 - t/2     : [* + / -] == [* / + -] == [/ * + -]
2*t + 1 - t/2     : [* / - +] == [/ - * +] == [/ * - +]
a + b*c - d/e     : [+ - * /] == [- + * /]
a + b*c - d/e     : [+ - / *] == [- + / *] == [- / + *]
a + b*c - d/e     : [+ * / -] == [+ / * -] == [/ + * -]
a + b*c - d/e     : [+ / - *] == [/ + - *] == [/ - + *]
a + b*c - d/e     : [* + / -] == [* / + -] == [/ * + -]
a + b*c - d/e     : [* / - +] == [/ * - +]
2*x*x + 1 - x/2   : [+ * / -] == [+ / * -] == [/ + * -]
2*x*x + 1 - x/2   : [+ / - *] == [/ + - *]
2*x*x + 1 - x/2   : [- * + /] == [* - + /]
2*x*x + 1 - x/2   : [- * / +] == [- / * +] == [* - / +]
2*x*x + 1 - x/2   : [* + / -] == [* / + -] == [/ * + -]
2*x*x + 1 - x/2   : [* / - +] == [/ - * +] == [/ * - +]
a - b*c + d/e - f : [+ - * /] == [- + * /]
a - b*c + d/e - f : [+ - / *] == [- + / *]
a - b*c + d/e - f : [- * / +] == [- / * +]
a - b*c + d/e - f : [* / + -] == [/ * + -]
a - b*c + d/e - f : [* / - +] == [/ * - +]
```

Support size `3`-ის ორივე expression-ს ზუსტად თითო merged class აქვს (`a + b - c*d : [+ * -] == [* + -]` და `a/b + c - d : [- / +] == [/ - +]`), და სწორედ ეს ხსნის ცხრილში `6` block-ის `5` distinct AST-მდე დაცემას.

**ეს დამატებითი collapse ამ ექსპერიმენტით ახსნილი არ არის და ღია კითხვად რჩება.** Support reduction ამბობს მხოლოდ იმას, რომ `distinct_ast_count <= factorial(|O(E)|)`; რატომ არის ის ხშირად მკაცრად ნაკლები, აქ არ არის დამტკიცებული და არც corpus-ზე გაზომილი რიცხვებიდან განზოგადებული. სამუშაო **hypothesis**: მნიშვნელობა აქვს მხოლოდ იმ operator-ების relative order-ს, რომლებიც token sequence-ში ერთმანეთს რეალურად ეჯიბრებიან (მეზობელ operand-ზე კონკურენციაში ხვდებიან), და არა მთელ `O(E)`-ს — მაგრამ ეს ჯერ არც formalized-ია და არც შემოწმებული.

## შეზღუდვები

- corpus ათი expression-ია, support size `4`-ის მხოლოდ ოთხი წარმომადგენლით.
- ყველა შემოწმებული expression parenthesis-ის გარეშეა; parenthesized corpus-ზე claim ცალკე გაზომვას მოითხოვს, თუმცა symbolic არგუმენტი `_expression(0)`-ს უკვე ფარავს.
- reduction მხოლოდ strict grammars-ზეა გაზომილი; `G0` control (tied levels) ამ report-ში არ მონაწილეობს.
- identity byte-identical serialized AST-ია (`ast_to_dict` + `json.dumps(sort_keys=True)`), და არა semantic equivalence — ეს უფრო მკაცრი კრიტერიუმია, ვიდრე 0017/0018-ის equivalence class.

## Evidence-ის კლასიფიკაცია

- ცხრილის ყველა რიცხვი (block count, block size, distinct AST count, `0.525`) executable **observation** არის.
- "block-ის შიგნით AST იდენტურია" არის **symbolically justified** parser-ის power comparison-ებიდან და დამატებით ათ expression-ზე **observed**.
- `factorial(|O(E)|)`-ზე ქვემოთ დაშვებული collapse არის **observation** მიმდინარე corpus-ზე; მისი ახსნა **hypothesis**-ია და არა claimed law.

## ვალიდაცია

```text
python -c "from parseatlas.support_reduction import support_reduction_report; r = support_reduction_report(('a - b - c','a/b/c','a + b - c','a + b*c','a + b - c*d','a/b + c - d','2*t + 1 - t/2','a + b*c - d/e','2*x*x + 1 - x/2','a - b*c + d/e - f')); print(r['expression_count'], r['all_reductions_hold'], r['mean_enumeration_saving']); [print(e['source'], e['support_size'], e['block_count'], e['expected_block_size'], e['distinct_ast_count'], e['upper_bound']) for e in r['expressions']]"
```

ზემოთ მოცემული merged restrictions-ის სრული სიის (`25` ხაზი) აღდგენა:

```text
python -c "from parseatlas.grammar import strict_grammars; from parseatlas.support_reduction import serialized_ast, support_reduction_report; r = support_reduction_report(('a - b - c','a/b/c','a + b - c','a + b*c','a + b - c*d','a/b + c - d','2*t + 1 - t/2','a + b*c - d/e','2*x*x + 1 - x/2','a - b*c + d/e - f')); g = {x.id: x for x in strict_grammars()}; f = lambda e, k: serialized_ast(e['source'], g[e['blocks'][k]['grammar_ids'][0]]); [print(e['source'].ljust(17) + ' : ' + ' == '.join('[' + k + ']' for k in ks)) for e in r['expressions'] for ks in [[k for k in e['blocks'] if f(e, k) == form] for form in dict.fromkeys(f(e, k) for k in e['blocks'])] if len(ks) > 1]"
```

```text
python -m pytest -q tests/test_support_reduction.py
7 passed
```
