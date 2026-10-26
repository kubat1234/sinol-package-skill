# Task types

The contest repository has a skeleton of each (`_templates/{std,chk,lib,soc}`,
created by `sinol-make init <id> -t _templates <type>`) with toy examples of the
checker / library / interactor protocol. Start from it.

## std — compare with the model output

Output is compared with `out/<test>.out` ignoring whitespace differences
(oicompare). Use only when the correct output is unique.

## chk — output checker `prog/<id>chk.cpp`

Run as `<id>chk <input> <contestant_output> <model_output>`. Prints to stdout:

```
OK            or WRONG
<comment>     shown to the contestant (may be empty)
<percent>     only for OK: 100, 50, 33.3, 1/3 … (empty = 100)
```

Exit code 0. Anything else (crash, exit code > 2) is a *system error* on sio2
— the checker must never crash on any contestant output. Rules:
- Read the contestant output with `oi::Scanner(argv[2], wrong_format_callback, oi::PL)`
  so malformed output (letters, too long numbers, missing tokens, extra tokens
  at the end) becomes WRONG. `readEof()` after skipping whitespace.
- Validate everything: ranges, the claimed answer is actually achieved
  (recompute from the input), optimality compared with the model output.
- Partial points: print `OK` + percent (e.g. correct value, wrong certificate → 50).
- Compiled by sinol-make with `-Werror -Wall -Wextra -Wshadow -Wconversion`: no unused parameters, no implicit narrowing.
- Test it by hand on: correct output, other correct output, wrong value,
  invalid certificate, garbage, empty file, extra output.

## lib — library

`config.yml`:

```yaml
extra_compilation_files: ['abclib.cpp', 'abclib.h']
extra_compilation_args:
  cpp: ['abclib.cpp']
```

The solution is compiled together with `abclib.cpp` (which has `main`) and
includes `abclib.h`. Solutions implement the functions declared in the header.
- The library reads the test, calls the contestant, prints the result (compared
  with `.out`, or checked by `abcchk.cpp`).
- `fclose(stdin)` after reading, so the contestant can't read the input.
- Keep library state in an anonymous namespace / `static`, names unlikely to
  clash with contestants' globals.
- Rule violations (bad arguments, too many calls): print a message that cannot
  match the expected output and `exit(0)` → WA.
- Give contestants, in `dlazaw/` (in the template): `abclib.h` (the same as
  `prog/abclib.h`), a sample library that reads the input simply and checks
  no rules, and a sample wrong solution that shows how to use it. Describe
  them in the statement's "Komunikacja" section, with the compile command.
  See package-format.md, dlazaw.
- Memory/time of the library count to the solution: keep it light, mention it
  in limits.

## soc — interactive (`prog/<id>soc.cpp`)

sio2/sinol-make run the interactor as

```
abcsoc <num_processes> <read_fd_0> <write_fd_0> [<read_fd_1> <write_fd_1> …]
```

- stdin of the interactor = the test file (the solution never sees it),
- stdout of the interactor = verdict in the checker format (above),
- it talks to solution *i* through `fdopen(read_fd_i, "r")` / `fdopen(write_fd_i, "w")`;
- each solution gets its index as `argv[1]` and talks through its own stdin/stdout;
- interactor limits: 2 × the solution's time limit.

Rules:
- `signal(SIGPIPE, SIG_IGN)` and treat EOF / failed reads as WRONG
  ("program ended before …"), never crash.
- `fflush` after every message; the statement must tell contestants to flush
  (`cout << endl`, `fflush(stdout)`). The classic contestant mistake is
  `cin.tie(nullptr)` without flushing → deadlock → TLE; keep such a wrong
  solution in the package.
- Count queries and enforce limits; validate every query (range, format).
- Adaptive interactors: be sure the answer stays consistent with all previous
  replies; describe adaptivity in the statement.
- No `.out` files. Tests contain whatever the interactor needs (hidden data).
- `num_processes: k` in config for k solution copies.
- sinol-make has no `chkwer` for interactive tasks.
- Statement: no `\makecompactexample`; show an example dialogue in a table.
- Give contestants a sample interactor in `dlazaw/` (in the template): it
  talks through stdin/stdout, takes the hidden data from argv or a file,
  checks little; the statement says how to run it (`mkfifo`). See
  package-format.md, dlazaw.
