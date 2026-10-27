# Workflow: review a package

Goal: tell the user whether the package is good enough for a contest and what
to fix. **Read-only by default** — don't change the package unless asked.
Running sinol-make writes into `in/`, `out/`, `.cache/` and may rewrite
`config.yml`, so run it on a **copy in the scratchpad**:

```sh
cp -r <pkg> <scratchpad>/review/<id> && cd <scratchpad>/review/<id>
```

## 1. Static pass

- `python3 <contest>/contest.py lint <pkg> -v` (or `scripts/contest.py lint <path> -v`
  from the skill for a foreign repo).
- Read `config.yml`, the statement, `prog/` listing. Identify the type and
  whether the package is old-style (Makefile/makefile.in — then also suggest
  workflows/modernize.md).

## 2. Correctness of the task

- Statement ↔ config: points, limits, groups, memory, examples correct.
- Is the statement unambiguous? (equal values, empty answer, 0/1-indexing,
  multiple answers without a checker, output format of special cases.)
- Model solution: read it, check complexity against limits, edge cases.
- For non-trivial tasks write your own brute force in the scratchpad and stress
  it against the model on small random inputs.

## 3. Tests

- `.cache/executables/<id>ingen.cpp.e --list` (after `gen`) gives the test →
  ingen line / arguments / size map — the quickest way to see what each group contains.
- Generator: does each group have min/max/random/special tests? Are the maximal
  tests really at the limit (n, values, answer size)? Are there tests against
  typical wrong approaches (greedy, overflow, recursion depth, hash
  collisions, slow I/O)? Are trees/graphs shuffled? Shapes (path, star…)?
- inwer: does it enforce **per-group** limits and every promise of the
  statement? A test violating its group is a blocker.
- Copy: `sinol-make gen`, `sinol-make inwer`, `sinol-make run` (WSL: `-T time`).
- If the package has few wrong solutions, write 2–3 plausible wrong ones in the
  scratchpad and check the tests reject them. Report any that pass.

## 4. Checker / library / interactor

Read against references/task-types.md: robust parsing of contestant output
(garbage, too short, too long, huge numbers), no crash = no system error,
partial points correct; interactor flushes, handles early exit (SIGPIPE),
counts queries, is not exploitable; library hides data from the contestant.

## 5. Report

```
## <id> — <title>: <verdict: ready / ready after fixes / needs work>

Blockers   (wrong answers, invalid tests, statement contradictions)
Major      (weak tests: wrong solution X gets Y points; missing group limits in inwer)
Minor      (statement wording, config cosmetics, leftovers)
Suggestions

What I ran: lint, gen, inwer, run (time tool), stress N tests ...
```

Each finding: what, where (file:line), why it matters, concrete fix. Mark
clearly what was verified by running vs. by reading.
