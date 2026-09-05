# Roadmap completion audit

**Georgian version:** [roadmap-audit.ka.md](roadmap-audit.ka.md)
**Written:** 2026-09-05, after experiment 0047 was commissioned. **Updated** the same day, once 0045 through 0049 landed.

The owner asked to take the roadmap to the end. This document is the map of what is left, and it is deliberately conservative: it records **which experiments bear on which phase**, and it marks every exit gate **UNVERIFIED** unless a card has explicitly discharged it.

**Nothing here declares a phase complete.** Mapping an experiment to a phase is not the same as checking that the phase's exit gate is met, and this project has spent a session finding that the difference matters. A verification card discharges gates; this document only says where to look.

## Status vocabulary

```text
CLOSED       an exit gate a card explicitly discharged, with the card named
COVERED      experiments exist that bear on every bullet, gate NOT yet checked
PARTIAL      experiments exist for some bullets and a named gap remains
OPEN         no experiment addresses it
DEFERRED     the owner or a measurement has postponed it, with the reason
BLOCKED      waiting on something outside this repository
```

## The map

| Phase | Bears on it | Status | What is missing |
|---|---|---|---|
| 1 Grammar and parsing | 0001 | COVERED | gate unchecked |
| 2 Domain-aware symbolic analysis | 0002, 0006, 0007 | COVERED | gate unchecked |
| 3 Outer-function atlas | 0002, 0032 | COVERED | gate unchecked |
| 4 Controlled corpus | 0004 | COVERED | gate unchecked |
| 5 Parameter sweeps and cost model | 0005, 0031 (5A); 0013, 0021, 0034 (5B) | COVERED | the gate asks whether a cheaper representation is cheaper *before or after* symbolic preprocessing; 0013 separates the two costs, but no card states the answer as the gate phrases it |
| 6 Rational and function semantics | 0002, 0009, 0032, **0048** | COVERED | the named gap is closed — 0048 declares four branch conventions explicitly, pins where each cut lies and checks each on a value that straddles it. The gate itself, that each semantic property carry its assumptions and failure modes, is still unchecked |
| 7 Invariant mining | 0014, 0015, 0016, **0046** | CLOSED | 0046 delivered a necessary and sufficient condition and review pushed the counterexample search to 32.8 million parses beyond the stated bound |
| 8 Precedence-space graph | 0018 | COVERED | gate unchecked |
| 9 Associativity and parenthesization | 0020, 0023, 0030 | COVERED | gate unchecked |
| 10 Numerical and statistical validation | 0012, 0025 | COVERED | gate unchecked |
| 11 Performance engine | — | DEFERRED | owner, 2026-09-05: general research first. A measurement supports the deferral — parsing is 0.26% of runtime, so a compiled parser would buy nothing; the CAS layer is the target when this resumes |
| 12 Finite fields and cryptography | 0022 | BLOCKED | the case study needs the owner's secp256k1 results; the intake exists with 327 `PENDING IMPORT` slots |
| 13 Publication and release | bilingual rule in force; 0034–0044 bilingual | PARTIAL | **0001–0033 have no English side**, and the `REPORT.md` → `REPORT.ka.md` migration is still pending for them |
| 14 Region model and representation engine | 0033 built the model; 0027, 0028 measured the negative | OPEN | the engine itself is not built; T22, T23, T24 are open |
| 15 Generation 2 and exponentiation | **0045** | CLOSED | 0045 built the 121-grammar registry, proved the extension conservative over 1,294,698 cells, and bounded the flagship result to the written form it was measured on |
| 16 Cognitive cost and parse ergonomics | — | OPEN | nothing started |
| 17 Non-commutative algebras | — | OPEN | nothing started |

Experiments not mapped above because they belong to Direction B rather than to a numbered phase: 0035, 0036, 0037, 0038, 0039, 0040, 0041, 0042, 0043, 0044, 0047 and 0049. The founding question is not a roadmap phase; it is the main line, and the roadmap predates it.

## What "to the end" actually requires

Four things, in the order they can be done:

1. **Discharge the gates.** Thirteen phases are COVERED with an unchecked gate. A verification card reads each phase's exit gate against the experiments mapped to it and reports CLOSED or names the gap. This is review work, not new research, and it is the largest single item.
2. **Close the two named gaps.** Phase 6 needs branch conventions for complex analysis. Phase 13 needs the English side of 0001–0033 and then the rename migration.
3. ~~Land the three running cards.~~ **Done.** 0045 closed Phase 15, 0046 closed Phase 7, 0048 closed Phase 6's named gap, and 0047 and 0049 answered questions the owner raised rather than phases. 0047 took three rounds and its rejections are the repository's clearest demonstration of why a declared bound must not be read as a property of the rules.
4. **Decide the long-range phases.** 14, 16 and 17 are programmes, not tasks. Phase 14 in particular is the representation engine, and T24 records the two acceptance gates it would have to pass. They are open by design and the roadmap should say whether they are still wanted before anyone starts them.

Phases 11 and 12 are not on that path: 11 is deferred by the owner with a measurement behind the deferral, and 12 waits on results from outside this repository.

## The honest position

The roadmap was written before the founding question was stated clearly, and eleven of the last thirteen experiments serve the founding question rather than a numbered phase. So "finishing the roadmap" is partly an act of bookkeeping — discharging gates on work already done — and partly a decision about which of the long-range programmes are still wanted.

The bookkeeping is worth doing. A phase marked complete without its gate checked is exactly the kind of claim this project has spent a session correcting in its own reports.
