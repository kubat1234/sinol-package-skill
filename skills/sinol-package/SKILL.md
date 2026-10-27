---
name: sinol-package
description: Create, review and modernize SIO2 / OIOIOI task packages (sinol format) and whole contests, with sinol-make, the contest-template repository and the sinol-gen generator library (gen.h). Covers standard tasks, output checkers, libraries and interactive tasks (interactor / soc), input generators (ingen), input verifiers (inwer), model / slow / wrong solutions, config.yml (scores, subtask_dependencies, limits, expected scores) and Polish statements (sinol.cls). Use it whenever the user talks about an olympiad / sio2 task or package ("paczka", "zadanie", "ingen", "inwer", "testy", "podzadania", "wzorcówka", "sinol-make"), wants a new task or contest, asks whether a package is ready, or wants an old Makefile-based package converted — even if they don't name sinol or sio2 explicitly.
---

# Sinol packages

Packages live in a **contest repository** made from contest-template: one
directory per 3-letter task id, `_templates/` (package skeletons),
`contest.py`. Packages are built and checked with **sinol-make**; there
are no Makefiles. Tests are written with **sinol-gen** (`prog/gen.h`): the
ingen produces every test, including the statement examples, so nothing in
`in/` / `out/` is committed.

## Modes

Pick the mode from the request and read its workflow before acting:

| The user wants to… | Workflow |
|---|---|
| create one package | [workflows/new-package.md](workflows/new-package.md) |
| create several packages / a whole contest, or a new contest repository | [workflows/new-contest.md](workflows/new-contest.md) |
| know whether a package is good (theirs or someone else's) | [workflows/review.md](workflows/review.md) |
| convert an old package (Makefile, committed tests, old generator) | [workflows/modernize.md](workflows/modernize.md) |

Reference material — read the file when the task touches its topic:

| file | when |
|---|---|
| [references/generator.md](references/generator.md) | designing tests, writing the ingen or the inwer |
| [references/sinol-gen/guide.md](references/sinol-gen/guide.md), [reference.md](references/sinol-gen/reference.md) | the gen.h API itself (bundled copy of sinol-gen's docs, version in `assets/VERSIONS`) |
| [references/package-format.md](references/package-format.md) | files, test names, every `config.yml` key, scoring |
| [references/task-types.md](references/task-types.md) | checker, library or interactor protocols |
| [references/statement.md](references/statement.md) | the statement skeleton, subtask table, translations |
| [references/quality.md](references/quality.md) | before calling a package finished, and in reviews |
| [references/sinol-make.md](references/sinol-make.md) | commands, the time tool, pitfalls |
| [references/contest-repo.md](references/contest-repo.md) | `contest.py`, updates of gen.h / tools, the release, commit conventions |

## Ground rules

1. **Propose first, then build.** The user wants control over what goes into
   a package. Before creating or changing package content, say in a few lines
   what you will make — type, groups with limits and points, solutions (e.g.
   "model + independent second model + slow O(n²) + 3 wrong: overflow, greedy,
   off-by-one"), the test plan, checker / interactor — and wait for their OK.
   Offer extras (a second independent model, more wrong solutions, a
   translation) instead of adding them silently.
2. **The statement is the user's.** They usually write the story themselves
   (in Polish). Unless asked, fill only what must match the package — the
   subtask table, `\RAM`, the examples — and leave the story as `TODO`.
3. **Use the repository's own files first.** `sinol-make init <id> -t
   _templates <type>` creates a package; `sinol-make gen|inwer|run|verify|doc|export`
   work inside it; `python3 contest.py lint|export-all|update|logo` in the
   contest root (up to contest-template v1.0.3 it was `tools/contest.py`;
   `update tools` moves it). Only when the repository has no `_templates/` or
   `contest.py` (a foreign or old repo) use the bundled copies:
   `-t <skill>/assets/contest-template/_templates <type>` and
   [scripts/contest.py](scripts/contest.py) `--root <repo>`. If the package's
   `gen.h` is newer or older than the bundled docs, trust the package's file
   and mention `contest.py update gen`.
4. **Measure time correctly.** sinol-make uses sio2jail by default, which does
   not work on WSL (`uname -r` contains `microsoft`): there pass `-T time` to
   `run` / `verify`. `time` is noisy, so never accept expected scores with a
   solution near half the time limit — see
   [references/quality.md](references/quality.md#timing).
5. **Verify before saying done.** A package is finished when `contest.py lint
   <id>` has no errors, `sinol-make verify` passes and every wrong / slow
   solution fails exactly where it is meant to. Report what you ran and the
   results, and say plainly what is unverified.
6. **Stay inside the request.** Don't touch other packages, other contests or
   files the user didn't mention. A package without an ingen has its tests
   only in git — never delete them without asking. Don't commit or push unless
   asked; when you suggest a commit message use `<id>: summary` (≤ 50 chars).

## Effort by difficulty

- **Easy task** (implementation, a formula): model + one wrong + one slow if a
  slower approach exists; the basic test set per group; no stress test.
- **Medium / hard task**: also an **independent** second solution written
  without looking at the model (a subagent that gets only the specification,
  see new-package step 3), a throwaway stress test in the scratchpad (never
  committed), wrong solutions for every plausible mistake or heuristic, and
  tests aimed at each of them.

The user picks the main model; Opus suits hard tasks, reviews and
interactors. For subagents pass `model: "sonnet"` on easy, mechanical work and
keep the inherited model for hard tasks.
