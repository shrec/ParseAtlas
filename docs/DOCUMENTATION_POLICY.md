# Documentation policy

**In force from 2026-09-04. This supersedes the earlier English-methodology / Georgian-reports split recorded in ROADMAP Phase 13.**

## The rule

> **Every document this project publishes exists in both English and Georgian.**

Neither language is a courtesy translation of the other. Both are normative: a reader of either one must be able to reproduce the same tables, check the same claims, and find the same limitations.

## Why both

The two audiences are real and they are not the same people.

- **Georgian** is the project's working language. It is how the owner reads results, how findings are discussed, and how a Georgian mathematician outside the project is shown the work.
- **English** is how anything here reaches prior art, review, or an outside researcher. A result nobody outside can read has not been published, only stored.

Producing one and not the other has, in practice, meant the other language falls behind and eventually contradicts the first. Requiring both at write time is cheaper than reconciling two drifted documents later.

## File convention

```text
docs/X.md                            English
docs/X.ka.md                         ქართული

experiments/NNNN_name/REPORT.en.md   English
experiments/NNNN_name/REPORT.ka.md   ქართული
```

Language is explicit in the filename. There is no unsuffixed `REPORT.md` under the new convention.

**Grandfather clause.** Experiments 0001–0039 already ship `REPORT.md` in Georgian and are linked from `docs/README.md`, `README.md` and `ROADMAP.md`. Those files keep their names for now; their English counterparts land as `REPORT.en.md`. A single migration renames `REPORT.md` to `REPORT.ka.md` across all of them once the English side exists, so the interim state is visible rather than permanent.

## What "both" requires

Translation is not the standard. **Agreement is.**

1. **Every number appears in both, identically.** If a table has 25 rows in one language it has 25 rows in the other. A figure quoted in one and omitted from the other is a defect, not an editorial choice.
2. **Every limitation appears in both.** The limits section is the part most likely to be dropped when a document is rewritten in a hurry, and it is the part an outside reader most needs.
3. **Every correction propagates to both in the same commit.** A number corrected in one language and left standing in the other is worse than never having translated it, because it now carries the authority of a document that agrees with nothing.
4. **Neither may carry a claim the other lacks.** If a sentence is worth asserting it is worth asserting twice; if it is not defensible in both, it is not defensible.
5. **The agreement obligation is about DATA, and data is written inside backticks.** Every measurement, count and bound is written as `` `47` `` in both languages and must appear identically in both; the mechanical check compares the numeric tokens **inside backticked spans**, not the whole prose. A cardinal that is an English or Georgian *word* — "one and the same", "not a single", "in one paragraph", "four reading rules" — is written as a word, in each language's own idiom, and is not required to match across the two. This rule exists because a document was once returned for writing "not 1 citation. Not 1 author, not 1 year" in English, to make a whole-prose token check agree; the check was passing and the normative English had been degraded to make it pass. **A mechanical check that can be satisfied by making a document worse is being used wrongly.** The rule has a second half, found the same week: **a quantity spelled as a word is invisible to the check.** Experiment 0056 shipped "`G09` and seven others" into both languages where its own table says five, and the numeric multisets agreed perfectly on either side of the error. So a *count* is written as a backticked numeral even in running prose — `4` others, not "four others" — while an indefinite cardinal stays a word. The two halves of this rule pull in opposite directions on purpose: **numerals for what was counted, words for what was not.**
6. **Technical terms stay in Latin script in the Georgian text** — `grammar`, `parse`, `manifest`, `round-trip`, `precedence` — because these are the terms the code and the English document use, and a Georgian reader who finds a translated coinage cannot search for it.

## Scope

Applies to: experiment reports, methodology, structural theory, case studies, the roadmap's narrative sections, README, and any document produced for an outside reader.

Does not apply to: code comments, docstrings, commit messages, and test names, which stay in English because they sit inside English-language source and are read alongside it.

## Enforcement

A card that produces a report produces both languages, and its acceptance check verifies that the numbers agree across the two — **compared over backticked spans**, per rule 5, so that idiomatic prose in either language is never the thing the check punishes. A card that corrects a number corrects it in both files or it is returned.
