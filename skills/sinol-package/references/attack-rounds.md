# Attack rounds

An attack round is one cycle:

1. A fresh subagent reads the ingen and the tests and writes new wrong or slow
   solutions that still pass them.
2. You add tests that make those solutions fail.

Your own wrong solutions are aimed at the mistakes you thought of. An
attacker that sees the tests finds what the tests miss: a heuristic that
happens to work on every random test, a bug that only one test catches, an
input order nobody shuffled, a hash table without an anti-hash test, or a
"subtask bundle" (a brute for small inputs plus a buggy fast branch).

## How many rounds: always ask

Ask the author in the plan (new-package step 2) how many rounds to run,
**whatever the difficulty**. The recommended answer depends on the task:

- **hard task:** 2–4 rounds, recommended. Mark that option "(recommended)".
- **medium task:** offer 1–2 rounds; 0 is fine.
- **easy task:** offer them anyway; 0 is the usual answer.

The author can ask for more rounds later ("jeszcze dwie rundy"). Each round
continues from the current tests and solutions; nothing is redone.

Every round makes the package bigger: in one hard task each round added about
10 tests and 10–20 solutions. So in the same plan also ask how many tests per
subtask and how many solutions should stay in the package at the end. Suggest
about 7 tests per subtask and about 15 solutions.

## Writing wrong and slow solutions: a subagent

Wrong solutions, correctness heuristics and slow solutions (new-package step 3.9)
are written by a subagent. This applies to the first set and to every attack
round. The subagent should write them because:

- it doesn't share your view of the model, so its mistakes are more like a
  contestant's;
- its compile-and-run work stays out of your context.

Give the subagent:

- the specification (format, limits, subtasks with points and dependencies);
- the model's idea and its measured time;
- the paths to read, as listed below.

Ask it for:

- each file with a header comment: the flaw, the subtasks it should fail
  (deserved score), and a small counterexample (for a wrong solution, checked
  against the model) or the worst-case family with a measured time (for a
  slow one);
- a summary table of what it wrote and the score each solution deserves.

## One round

1. **Spawn the attacker.** Use a fresh subagent with the inherited model; this
   is reasoning-heavy work. Its prompt has:
   - the specification;
   - the time limit and the model's time;
   - paths to `prog/<id>ingen.cpp`, `in/` and `out/` (with a warning that big
     tests must not be printed);
   - every existing solution, including ones removed earlier (kept in the
     scratchpad), so its ideas are new;
   - holes already accepted, so it doesn't redo them;
   - the round number;
   - a cap on new solutions (≤ 20 is a good default);
   - the compile flags of sinol-make;
   - a scratchpad folder of its own.

   Its rules:
   - Only attacks a real contestant could plausibly write.
   - Pass as many current tests as possible.
   - Run every solution under `timeout`, at most 4 processes at a time.
   - Validate every attack input with the inwer, called with a test name of
     the right group.
   - Don't run sinol-make. Don't change existing files.
   - Propose new tests as a **copy** of the ingen, with new lines at the end of
     their groups so the existing tests keep their names and contents. Check
     that the copy compiles and reproduces the old tests byte for byte.
   - Report a table: solution, flaw, deserved points, points now, and for each
     solution scoring too much, the ingen call that catches it. That call must
     be verified three ways: inwer OK, the solution fails, and the model agrees
     with the second model.
   - Leave no processes running.
2. **Review the proposed tests** before merging them. Check that each is valid
   for its group and aimed at a real flaw. Prefer one test that kills several
   solutions to one test per solution, and keep sizes moderate. Add tests that
   make the **slow** solutions fail decisively (well over the time limit, not
   just near it).
3. **Run only what is new:**
   - the new solutions × all tests;
   - all solutions × the new tests.

   Keep the results in a file in the scratchpad, keyed by solution and test,
   with the md5 of each source. A changed source invalidates that solution's
   results; if only comments changed, update the hash instead of rerunning.
   Append each round's table to a log the author can read. Ask where the log
   goes: the package directory is fine while it is untracked, but don't commit
   it.
4. **Close the round:** every solution gets exactly its deserved score. If a
   hole is too costly to close, don't add a huge test or weaken the solution.
   Record it as an accepted hole and tell the author.

## After the last round

After the rounds, pruning is the default: tests and solutions from the rounds
stay in the package only when the author decides so.

- If the author already gave the numbers, use them.
- If not, propose about 7 tests per subtask and about 15 solutions, and ask.
  Until the author answers, repeat the question in every report and status
  message. Don't drop it after asking once.
- The numbers are a target, not a hard cap. If a group needs more tests (each
  test is the only one catching some solution), or more solutions are needed
  to cover distinct flaws, keep more. Then say so clearly in the report: which
  groups or solutions are over the number, by how much, and why.

- **Tests.** For each group G, a solution is *relevant* if it passes G's
  dependency groups and fails G. Keep tests greedily until every relevant
  solution fails at least 2 kept tests of G, or 1 if only one test catches it.
  Also keep the ocen test and the min and max tests.
  - Before deleting anything, pin every kept random test with `.seed(x)`,
    where x is the seed that `./<id>ingen --list` shows for it
    (generator.md#seeds), so the kept tests stay byte-identical.
  - Then map the old results onto the new test names instead of rerunning.
  - Check the md5 of the kept inputs.
- **Solutions.** Keep the ones that check the most important things:
  - the models;
  - one slow solution per complexity class;
  - the wrong solutions that cover distinct flaws, especially ones that each
    need their own test.

  Move the others to the scratchpad instead of deleting them, and list them
  in the report with their scores.
- Finish with `sinol-make run --apply-suggestions` and `sinol-make verify`.

## Pitfalls

- A subagent that is still running skews timings. Check that its processes
  are gone before measuring.
- `pkill -f <pattern>` can match your own shell. Kill by PID.
- sinol-make caches results. Delete `.cache/executions` and `.cache/md5sums`
  if it reports stale scores.
- Kill a run at about 1.5× the time limit and count it as TL; waiting longer
  only wastes time.
