# Provenance of this snapshot

This directory is **vendored evidence**, not maintained code.

## Source

| Field | Value |
|---|---|
| Source repository | `UltrafastSecp256k1` |
| Branch | `experiment/representation-search` |
| Branch status | local to the project owner, **not yet pushed** to any remote |
| Landed in ParseAtlas as | `case_studies/ultrafast_secp256k1/repsearch_snapshot/` |
| Landed by | ParseAtlas experiment 0025, independent-implementation cross-validation |

The branch is not public. There is therefore no commit URL to cite, and no way
for a third party to fetch the original at the time of writing. What is
reproducible is the content itself: everything below is a byte-for-byte copy of
what the owner staged, verified with `diff -r --exclude=__pycache__` against the
staged directory before this file was added.

## What it is

An **independent implementation of the ParseAtlas idea**, written for a
different project and for a different purpose (finding cheaper representations
of secp256k1 field and point primitives). It shares no code with ParseAtlas.

The three modules that experiment 0025 depends on:

- `repsearch/expr.py` — tokenizer and a precedence-climbing parser whose
  precedence table is an **argument**, not a hardcoded convention.
- `repsearch/grammar.py` — enumerates all `4! = 24` strict precedence orders
  as `PRECEDENCE_ORDERS = list(itertools.permutations(BINARY_OPS))` and
  collapses the results into equivalence classes.
- `repsearch/poly.py` — exact multivariate polynomials and rational functions
  over Q. Equality is decided by cross-multiplication, `a/b == c/d` iff
  `a*d - c*b == 0`. No SymPy, no floating point, no probabilistic identity
  test; fingerprints only bucket candidates and every claimed equality inside a
  bucket is confirmed exactly.

The remaining modules, tools, benchmarks and CUDA sources are the rest of that
experiment. They are kept so the snapshot is the real thing and not an excerpt
curated to agree with ParseAtlas.

## File list

Sizes in bytes, as landed. `__pycache__` and `.pytest_cache` were excluded from
the copy; nothing else was.

| File | Bytes |
|---|---|
| `README.md` | 16363 |
| `cpu_fe52_op_bench.cpp` | 10324 |
| `cpu_point_formula_bench.cpp` | 32162 |
| `cuda_point_formula_search.cu` | 40773 |
| `test_cuda_point_formula_search.cu` | 21033 |
| `repsearch/__init__.py` | 0 |
| `repsearch/equiv.py` | 5904 |
| `repsearch/expr.py` | 7719 |
| `repsearch/field.py` | 6806 |
| `repsearch/fieldkernels.py` | 7675 |
| `repsearch/grammar.py` | 4380 |
| `repsearch/modarith.py` | 12694 |
| `repsearch/pointforms.py` | 12671 |
| `repsearch/poly.py` | 11532 |
| `repsearch/rewrite.py` | 17227 |
| `repsearch/slp.py` | 14456 |
| `repsearch/tablebuild.py` | 7243 |
| `tests/test_grammar_toy.py` | 2394 |
| `tests/test_point_equivalence.py` | 3945 |
| `tests/test_table_build.py` | 3054 |
| `tools/ab_bench.py` | 9595 |
| `tools/emit_cpp.py` | 1315 |
| `tools/gen_cpu_bench.py` | 17763 |
| `tools/interop_check.py` | 3530 |
| `tools/magnitude_fixpoint.py` | 2912 |
| `tools/run_point_equiv.py` | 4720 |
| `tools/run_search.py` | 5197 |
| `tools/toy_grammar.py` | 508 |

28 files, 283895 bytes total. `PROVENANCE.md` — this file — is the only file in
this directory that ParseAtlas wrote.

## Rules for this directory

1. **Frozen.** ParseAtlas does not maintain this code. Do not edit, reformat,
   lint, modernise or "fix" anything here. A change upstream is landed by
   replacing the snapshot wholesale and updating this file, never by patching
   in place.
2. **Not on the package path.** `src/parseatlas/cross_validation.py` imports it
   through an explicit `sys.path` insertion of this directory plus
   `importlib.import_module`. Nothing else in ParseAtlas imports it.
3. **Its tests are not run by the ParseAtlas suite.** `pyproject.toml` sets
   `[tool.pytest.ini_options] testpaths = ["tests"]`, so `python -m pytest -q`
   from the repository root collects only `tests/` and never
   `case_studies/ultrafast_secp256k1/repsearch_snapshot/tests/`. The snapshot's
   own tests belong to its own project and are its own project's business.
4. **If the snapshot is absent**, `parseatlas.cross_validation` raises
   `SnapshotUnavailable` with an actionable message and
   `tests/test_cross_validation.py` skips with that reason. Nothing else in the
   suite depends on it.
