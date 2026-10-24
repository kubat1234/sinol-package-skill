# Workflow: modernize an old package

Old packages (e.g. from repositories made with `new-package.sh`) have a
1000-line `Makefile`, `makefile.in`, `prog/Makefile`, `doc/Makefile`, copied
`oi.h`/`testgen.hpp`, `example-*.cpp` leftovers, hand-made generators with one
global seed, statement examples named `1ocen`, and tests duplicated between
groups. Goal: the same task in the current conventions, verified to be
equivalent.

## 1. Inspect and propose (wait for OK)

Run a quick review (workflows/review.md steps 1 and 3, read-only) and propose:

- **where**: in place, or copy into a new contest repository (ask);
- **files**: drop Makefiles, `makefile.in` (move `ID`, `TIMELIMIT`, `MEMLIMIT`
  into `config.yml`), leftovers; refresh shared files (`oi.h`, `sinol.cls`, …) from `_templates/std`;
- **config.yml**: add `sinol_task_id`, `sinol_contest_type: oi`; drop
  `sinol_static_tests` once the examples are in the ingen; check scores sum to 100;
- **tests naming**: statement examples → `<id>0.in` (one) or `0a`, `0b` (several);
  other public examples → `<id>1ocen.in`, … (update `\makecompactexample{...}`);
- **duplicated tests between groups** (find identical files with `md5sum in/*`)
  → remove the copies and add `subtask_dependencies`; check that points for
  every solution stay the same (or explain the change);
- **generator** (if it exists): port it to sinol-gen (copy `gen.h` from
  `_templates/std/prog/`, read references/sinol-gen/guide.md): the old
  functions usually stay, the test list becomes `g.group` / `g.test`, the
  statement examples and the committed ocen tests become `g.example` /
  `g.ocen` with their exact content (`gen::text(R"(...)")` or `{"line", ...}`).
  The random tests will differ from the old ones (another RNG) — say so, and
  compare the solutions' verdicts instead of the files. Keeping the exact old
  tests means reproducing the old RNG; usually not worth it, ask. Packages with
  the previous gen.h (`T(f, {...}, seed)`, no `SINOL_GEN_VERSION`) are ported the
  same way;
- **no generator** (tests only): ASK — (a) write an ingen with better tests,
  (b) an ingen that reproduces the existing tests as text (only for small
  ones), or (c) keep the files. In case (c) they stay committed: `!*.in` /
  `!*.out` in `<id>/in/.gitignore` / `<id>/out/.gitignore`. Never delete them;
- **statement**: move to the current skeleton (keep the text; fix the subtask
  table, `\RAM`, examples). Rewrite the wording only if asked;
- **inwer**: add per-group limits if missing.

## 2. Convert

Do the accepted steps. Record before/after: run all solutions on the old
package first (in a scratchpad copy) and save the table.

## 3. Verify equivalence

- Same solutions, same verdicts per group (or every difference explained —
  e.g. a wrong solution now fails thanks to better tests).
- `sinol-make inwer` passes on all tests.
- `sinol-make run --apply-suggestions`, `sinol-make verify` (WSL: `-T time`), `contest.py lint` clean.

Report the before/after table and the list of changes.
