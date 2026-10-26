# Quality checklist

Use when finishing a package and when reviewing one.

## Task and statement
- [ ] Unambiguous: equal values, empty answer, multiple answers (→ checker), indexing, output of special cases.
- [ ] Limits in the statement = config.yml (`\RAM` in MB, time per group, points per group).
- [ ] Every subtask's conditions are checked by inwer for tests of that group.
- [ ] The statement examples (`g.example`) are the ones the story talks about, and their outputs (from the model) are what the statement claims.

## Solutions
- [ ] Model solution: correct, intended complexity, fast I/O, `long long` where needed.
- [ ] Medium/hard: an independent second correct solution agreeing with the model; stress-tested against a brute force on small inputs.
- [ ] Slow solutions for each lower complexity class mentioned in the subtasks; each passes exactly the intended groups.
- [ ] Wrong solutions for plausible mistakes (overflow, greedy, missing edge case, wrong recursion, heuristics); each fails where its header comment says.
- [ ] No group passed by a trivial/wrong approach (e.g. printing 0, a constant, the brute force on "big" groups).
- [ ] `sinol_expected_scores` recorded and `verify` passes.

## Tests
- [ ] Every group: min, max, random, special structures, anti-wrong, anti-slow tests (generator.md).
- [ ] Largest tests at the limits (n, values, answer size).
- [ ] Trees/graphs shuffled; no accidental structure (vertex 1 always the root, edges sorted).
- [ ] Dependencies (`subtask_dependencies`) instead of duplicated tests; listed explicitly (not transitive).
- [ ] Every test in the ingen (sinol-gen), examples and ocen too; nothing committed in `in/` / `out/`; no `rand()` / `<random>` / `std::shuffle`.
- [ ] Maximal tests not all at exactly MAXN (`gen::near`); `gen::check` where a test's purpose could silently break.

## Checker / library / interactor
- [ ] Never crashes; malformed output = WRONG; partial points as intended (task-types.md).
- [ ] Interactor: flushes, SIGPIPE ignored, query limit, validates queries, not exploitable.
- [ ] Library hides the input (`fclose(stdin)`), state not clashing with contestants.
- [ ] `dlazaw/` (library / interactive task): the header equals `prog/abclib.h`, the sample library / interactor compiles and works with the model, the statement says how to use it; tests in `dlazaw/tests/` if more than one.

## Package hygiene
- [ ] `contest.py lint <id>`: no errors; no `TEMPLATE:`/`TODO` left (except the story if the user writes it).
- [ ] No Makefiles, no `example-*.cpp`, no stray binaries; shared files in sync.
- [ ] `contest.py lint` has no warning about an old or modified `gen.h`.

## Timing

Time limit: about 3–5× the model's worst time measured with `time` (2–3× with
sio2jail), rounded to a nice value; slow solutions must be clearly over the
limit (TL, not "almost passes"). With `oi` scoring a correct solution between
TL/2 and TL loses points — and `time` is noisy (much more than sio2jail, especially on WSL), so:
- correct solutions should run below ~TL/4 when measured with `time`;
- a solution near TL/2 or TL makes expected scores flaky — speed it up, change
  TL, or make the tests separate it decisively;
- don't trust differences of a few percent; re-run before concluding.
