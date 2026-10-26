# Workflow: new package

## 0. Orient (read-only)

- Find the contest root (`_templates/`, `tools/contest.py`). If the
  repository is not from contest-template, ask whether to create the package
  there anyway (with `-t <skill>/assets/contest-template/_templates <type>`) or
  in a new contest repo.
- `ls` the root — existing ids; pick an unused
  3-letter id (from the title, e.g. "Dzielniki" → `dzi`), confirm the directory
  does not exist.
- `sinol-make --version` ≥ 1.9.15 (needed for `subtask_dependencies`).

## 1. Understand the task

From the user's description extract: input/output format, limits, what is
asked, intended solution and complexity, subtasks. Ask only what blocks the
design (e.g. "is n ≤ 10^5 or 10^6?", "is any optimal answer accepted?"). Decide
the **type**: `std` (unique answer), `chk` (many correct answers or partial
points), `lib` (contestant implements functions), `soc` (interactive / adaptive).

## 2. Propose (wait for OK)

A short plan, for example:

```
abc — "Tytuł", type chk, 1 s, 512 MB
groups: 1 (n ≤ 10, 15 pts) · 2 (n ≤ 1000, 25) · 3 (a_i ≤ 2, 20) · 4 (no extra limits, 40)
deps:   4: [1, 2, 3]
solutions: abc.cpp O(n log n) · abc2.cpp independent O(n log n) (subagent)
           abcs1.cpp O(n²) → 1,2,3 · abcs2.cpp brute → 1
           abcb1.cpp greedy by value → 0 · abcb2.cpp int overflow → fails 4
tests: per group min/max/random/special (sorted, all equal, ...), anti-greedy
statement: not by me (only the subtask table) — or should I write it?
```

Offer, don't impose: second independent model, more wrong solutions,
statement or translation.

## 3. Build

1. `sinol-make init <id> -t _templates <t>` in the contest root. The package
   starts as a skeleton: title `TODO`, 1 s, 512 MB, an empty model solution,
   empty `in/` and `out/`, and toy examples of the ingen (sinol-gen), inwer and
   checker / library / interactor, marked `TEMPLATE:` — replace all of them;
   slow and wrong solutions are written from scratch.
2. `config.yml`: title, limits, `scores` (sum 100), `subtask_dependencies`
   (not transitive — list all), keep `sinol_contest_type: oi`. No
   `sinol_static_tests`: every test comes from the ingen. See
   references/package-format.md.
3. **Model solution** `prog/<id>.cpp`. For medium/hard tasks get an
   **independent** solution: spawn a subagent (`Agent`, `model: "sonnet"` for
   simpler tasks, inherit for hard ones) with ONLY the specification (format,
   limits, task, required complexity) — not your code — asking for
   `prog/<id>2.cpp`. Also write a brute force (often it becomes `<id>s1.cpp`).
4. **Stress test** (medium/hard): in the scratchpad, a small script that
   generates tiny random inputs and compares model, independent solution and
   brute until a few thousand tests agree. Delete it afterwards — nothing of it
   goes into the package.
5. **Generator** `prog/<id>ingen.cpp` with sinol-gen — read
   references/generator.md (what to generate) and
   references/sinol-gen/guide.md (how). Every group: smallest case, maximal
   case, random, special structures, and a test aimed at each wrong solution;
   `gen::check` for tests whose purpose could silently break.
6. **Statement examples and ocen tests** go into the ingen too:
   `g.example(...)` (one → `<id>0.in`, several → `0a`, `0b`; the statement
   uses `\makecompactexample{0}` or `{0a}`, `{0b}`) and `g.ocen(...)` for the
   public tests contestants get right away (usually one or a few — ask if
   unsure). Their outputs come from the model.
7. **Input verifier** `prog/<id>inwer.cpp` — strict format, per-group limits
   from `argv[1]`, every structural promise of the statement (connected,
   distinct, sorted, answer exists…).
8. **Checker / library / interactor** if the type needs it —
   references/task-types.md. Test the checker on wrong outputs by hand
   (malformed, wrong value, partial). Library / interactive task: also
   `dlazaw/`, the files for contestants (package-format.md, dlazaw).
9. **Wrong and slow solutions** — each targets one specific mistake, with a
   comment at the top saying which groups it must fail and why.
10. Statement: only if asked; otherwise keep the skeleton, fill the subtask table
    (points, conditions, time) and `\RAM`, leave the story as `TODO`.

## 4. Check

```sh
cd <id>
sinol-make gen            # inputs + outputs (outputs from the model)
sinol-make inwer
sinol-make run             # on WSL: -T time (also below)
```

If a test fails the verifier or surprises you, `.cache/executables/<id>ingen.cpp.e
--list` (run it anywhere) shows the line of the ingen and the arguments that made it.

Look at the table, not only the summary:
- all correct solutions 100, and the model well below half the time limit;
- each slow solution: OK on the small groups, TL on the big ones;
- each wrong solution: fails the groups it should; if it passes a group it
  should fail, add a test (don't weaken the solution);
- no group where everything passes trivially (group too weak).

Set the time limit from the model's time (with `time`: roughly 3–5× the model's
worst time, and slow solutions must be clearly over it). Then:

```sh
sinol-make run --apply-suggestions   # record expected scores
sinol-make verify
python3 ../tools/contest.py lint <id>
```

## 5. Report

Summary for the user: groups and points, solutions with their scores per
group, number of tests per group, what was verified (commands run), what is
left to them (statement text, `TODO`s), and anything uncertain. Suggest a commit
message `<id>: ...` (with `!ver` if the package is ready to be checked, see
references/contest-repo.md) but don't commit unless asked.
