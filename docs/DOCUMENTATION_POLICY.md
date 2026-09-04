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
5. **Technical terms stay in Latin script in the Georgian text** — `grammar`, `parse`, `manifest`, `round-trip`, `precedence` — because these are the terms the code and the English document use, and a Georgian reader who finds a translated coinage cannot search for it.

## Scope

Applies to: experiment reports, methodology, structural theory, case studies, the roadmap's narrative sections, README, and any document produced for an outside reader.

Does not apply to: code comments, docstrings, commit messages, and test names, which stay in English because they sit inside English-language source and are read alongside it.

## Enforcement

A card that produces a report produces both languages, and its acceptance check verifies that the numbers agree across the two. A card that corrects a number corrects it in both files or it is returned.
