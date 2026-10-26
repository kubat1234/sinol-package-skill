# Contest template

[SIO2](https://github.com/sio2project/oioioi) contest, packages built with
[sinol-make](https://github.com/sio2project/sinol-make).

## Setup

**Use this template**. The first push puts the repository name into the
statement templates (`\konkurs`, `\signature`). Then clone and:

```sh
pip install --user sinol-make        # >= 1.9.15
# pipx install sinol-make
python3 tools/contest.py init --id <contest-id> --name "<Contest Name>"   # commit hook + name with diacritics
```

## New package

```sh
sinol-make init abc -t _templates std     # std | chk (checker) | lib (library) | soc (interactive)
```

Every test, the statement example and ocen tests too, is made by `prog/abcingen.cpp`
with [sinol-gen](https://github.com/kubat1234/sinol-gen) (`prog/gen.h`, see its
`docs/guide.md`); `in/` and `out/` are generated, nothing there is committed.
`./abcingen --list` shows which line of the ingen made which test.

`_templates/extras/`: `testgen.hpp` (`cp` to `abc/prog/`), `example-testgen.cpp`, `example-oilib.cpp` (oi.h generator).

## Commands

In a package directory (`sinol-make -h`, `sinol-make <command> -h` for help):

```sh
sinol-make gen       # generate tests (ingen + model solution)
sinol-make inwer     # check tests with the verifier
sinol-make run       # run solutions; -a saves expected scores to config.yml
sinol-make verify    # full check: gen + inwer + run against expected scores
sinol-make doc       # compile the statement
sinol-make export    # package archive for SIO2
```

In the repository root:

```sh
python3 tools/contest.py lint                 # statement vs config, TODOs, old gen.h, ...
python3 tools/contest.py export-all           # export --export-ocen, archives in _export/
python3 tools/contest.py update gen [abc|all] # newer gen.h into _templates (+ packages, only if their tests stay the same)
python3 tools/contest.py update tools         # tools/, .github/, .githooks/ from contest-template
python3 tools/contest.py update templates     # _templates/ from contest-template (keeps the contest name)
```

WSL: add `-T time` to `run` / `verify` (no sio2jail).

**Release**: every push updates the [`tasks` release](../../releases/tasks)
(statement, package, ocen tests or dlazaw.zip per task). State: `!todo` / `!ver` / `!done`
in a commit title; `!rebuild-abc` / `!rebuild-*`.

## config.yml

- `sinol_expected_scores` is written by `run -a` and is what `verify`
  compares against. `run -a` rewrites the whole file, so comments in
  `config.yml` are lost.
- `subtask_dependencies`: a group's points count only if the listed groups
  also pass, e.g. `3: [1, 2]`. Not transitive, so list all of them.

## Conventions

- `prog/`: `abc.cpp` model, `abc2.cpp` correct, `abcs1.cpp` slow, `abcb1.cpp` wrong
- Tests:
  - `abc0.in` the example from the statement (`abc0a.in`, `abc0b.in` … if there are more): `g.example(...)`.
  - `abc1ocen.in`, `abc2ocen.in` … public tests, contestants get them right away: `g.ocen(...)`.
  - `abc1a.in`, `abc1b.in`, `abc2a.in` … groups: `g.group(k)`, `g.test(...)`.
  - Contestants get `abcocen.zip` (`0*` and `*ocen` tests) as an attachment.
  - None is committed; a package without an ingen commits all its tests
    (`!*.in` in `abc/in/.gitignore`, `!*.out` in `abc/out/.gitignore`).
- `abc/dlazaw/` (optional): files contestants need, committed. A library
  task: `abclib.h`, a sample library and a sample wrong solution (in the `lib`
  template); an interactive task: a sample interactor (in the `soc` template).
  Files go straight into `dlazaw/`; more than one test goes into
  `dlazaw/tests/`. With `dlazaw/` the attachment is `dlazaw.zip` **instead of**
  `abcocen.zip`, so put the tests contestants should get there by hand (they
  are often not the package tests, e.g. without the library's input guard).
- Commits: `abc: summary` / `*: summary`, ≤ 50 chars.

## Credits

`commit-msg` hook: [tfkls/sio2-contest-template](https://github.com/tfkls/sio2-contest-template)
(Unlicense). `oi.h`: sinol-make. `testgen.hpp`:
[FilipKon13/tests-generation](https://github.com/FilipKon13/tests-generation).
`sinol.cls`: OI. `example-oilib.cpp`:
[sio2project/task-package-examples](https://github.com/sio2project/task-package-examples).
