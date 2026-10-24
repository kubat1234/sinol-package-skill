# sinol-make

Install / upgrade: `pipx install sinol-make` or `pip install --user sinol-make`;
**≥ 1.9.15** is required for `subtask_dependencies` (older versions ignore
them silently and print "Found unknown fields in config.yml").

Run inside the package directory:

| command | what it does |
|---|---|
| `sinol-make gen` | compile `prog/<id>ingen.cpp`, run it in `in/`, then generate missing/changed `.out` with the model; hand-written outputs are verified, not overwritten |
| `sinol-make gen -i` / `-o` | only inputs / only outputs |
| `sinol-make inwer` | run the input verifier on every test (also checks test order/naming) |
| `sinol-make run` | run all solutions on all tests, compare with `sinol_expected_scores` |
| `sinol-make run -s abcb1.cpp --tests abc2*.in` | subset |
| `sinol-make run --apply-suggestions` | accept the current results as expected |
| `sinol-make verify` | everything: config, gen (with sanitizers), doc, inwer, run |
| `sinol-make chkwer` | run the checker on the model outputs (not for interactive) |
| `sinol-make doc` | build all `doc/*.tex` |
| `sinol-make export` | `<id>.tgz` for sio2 (+ `attachments/<id>ocen.zip`) |
| `sinol-make init <id> -t _templates <type>` | new package from the contest's templates (only `__ID__` is replaced) |

`run` / `verify` measure with sio2jail by default. sio2jail needs perf
counters, which WSL does not have — there they fail with "failed to generate
at least one perf event config" / "Could not parse sio2jail output", so add
`-T time`. Every package in a contest: `for d in ???/; do (cd $d && sinol-make <cmd>); done`.

Pitfalls:
- `run --apply-suggestions` and other commands **rewrite config.yml**: comments
  disappear, keys get reordered. Edit config.yml with that in mind.
- `.cache/` holds compiled programs and results; delete it if something seems
  stale. `in/.md5sums`, `out/.md5sums` are caches (git-ignored).
- Every program (solutions, checker, ingen, inwer) is compiled by default with
  `-Werror -Wall -Wextra -Wshadow -Wconversion -Wfloat-equal`: unused
  parameters, shadowing and implicit narrowing (`int x = some_long_long;`)
  are compile errors. `verify` adds `-fsanitize=address,undefined` to ingen/inwer.
- Cached results are kept per time tool; after switching tools everything is
  re-run and timings change — compare runs made with the same tool.
- `gen` fails when `in/` does not exist — the templates keep `in/.gitkeep`
  (and `out/.gitkeep`) for that reason.
- When `sinol_static_tests` is present (old packages), `gen` deletes every test
  that the generator did not produce and that is not listed there.
- sinol-make keeps the compiled ingen as `.cache/executables/<id>ingen.cpp.e`;
  run it with `--list` to see which ingen line made which test.
- sio2 compiles and runs the ingen again when the package is uploaded, with its
  own compiler: keep ingens to C++17.
