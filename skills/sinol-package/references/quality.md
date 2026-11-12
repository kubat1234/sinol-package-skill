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
- [ ] The attack rounds the author asked for are done; holes left open are listed in the report (attack-rounds.md).
- [ ] No group passed by a trivial/wrong approach (e.g. printing 0, a constant, the brute force on "big" groups).
- [ ] `sinol_expected_scores` recorded and `verify` passes.

## Tests
- [ ] Every group: min, max, random, special structures, anti-wrong, anti-slow tests (generator.md).
- [ ] Largest tests at the limits (n, values, answer size).
- [ ] Trees/graphs shuffled; no accidental structure (vertex 1 always the root, edges sorted).
- [ ] Dependencies (`subtask_dependencies`) instead of duplicated tests; listed explicitly (not transitive).
- [ ] Every test in the ingen (sinol-gen), examples and ocen too; nothing committed in `in/` / `out/`; no `rand()` / `<random>` / `std::shuffle`.
- [ ] One ocen test per subtask (`<k>ocen` within the limits of subtask k), unless the user decided otherwise.
- [ ] Maximal tests not all at exactly MAXN (`gen::near`); `gen::check` where a test's purpose could silently break.
- [ ] Seeds fit what the user wants (generator.md#seeds): gen.h ≥ 2.0 without seeds by default; every random test its own distinct `.seed(x)` when tests must never change after deleting others (always with gen.h 1.x).

## Checker / library / interactor
- [ ] Never crashes; malformed output = WRONG; partial points as intended (task-types.md).
- [ ] Interactor: flushes, SIGPIPE ignored, query limit, validates queries, not exploitable.
- [ ] Library reads the whole test before calling the contestant and never closes stdin/stdout (`close(0)` is RV under sio2jail); state not clashing with contestants.
- [ ] `libsec`: new secrets for this package, equal in the four files and in no header; cheating solutions (read stdin early, print `OK`, break a rule) get their messages (task-types.md).
- [ ] `dlazaw/` (library / interactive task): the header equals `prog/abclib.h`, the sample library / interactor compiles and works with the model, the statement says how to use it; tests in `dlazaw/tests/` if more than one.
- [ ] Files in `dlazaw/` have no comments and only the code the interface needs; the sample library style (terminal dialog or test reader) is the one the author chose (task-types.md).
- [ ] Test-reader sample library: the author reviewed `dlazaw/` and confirmed it gives away nothing about how the task works or is tested. No commit or push before that answer.

## Editorial
- [ ] New package: `doc/<id>opr.tex` exists, unless the user opted out. Existing package: the user was asked.
- [ ] Has all three parts: the task without the story, the quick bullets, the full explanation (editorial.md).
- [ ] Subtask table = config.yml; points and numbers come from real runs; named solutions exist in `prog/`.
- [ ] Each claim is marked as proved, measured or a rough estimate.
- [ ] Every page looked at after the last change; not in `attachments/` or `dlazaw/`.

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
