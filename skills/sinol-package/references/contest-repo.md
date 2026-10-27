# The contest repository

Made from contest-template (GitHub "Use this template"). What is in it:

```
_templates/{std,chk,lib,soc}/   package skeletons for `sinol-make init <id> -t _templates <type>`
_templates/extras/              testgen.hpp and two old-style generator examples
tools/contest.py                init, lint, export-all, update
.github/                        setup.yml (first push), release.yml + release.py (the `tasks` release)
.githooks/commit-msg            commit message check
<id>/                           packages
```

## tools/contest.py

| command | |
|---|---|
| `init --id 10grodek27 --name "10Gródek27"` | contest into `_templates/*/doc/__ID__zad.tex`, enables the commit hook; once per clone (the hook) |
| `lint [-v] [ids]` | static checks: config, names, groups vs scores, statement vs config (`\id`, `\RAM`, subtask table, time limits), leftover `TEMPLATE:` / `TODO`, shared files, gen.h version |
| `export-all [ids]` | `sinol-make export --export-ocen` everywhere (`sinol-make gen` first if the examples are missing), archives and `<id>_ocen.zip` / `<id>_dlazaw.zip` in `_export/` |
| `update gen [ids\|all]` | newest gen.h (sinol-gen) into `_templates/` and the given packages — a package is updated only if its tests stay byte-identical (`--force` otherwise) |
| `update tools` | `tools/`, `.github/`, `.githooks/`, `.claude/`, `.gitignore` and `README.md` (keeping its title) from contest-template |
| `update templates [ids\|all]` | `_templates/` from contest-template, keeping the contest name and removing files it no longer has; shared files (oi.h, sinol.cls, …) of the given packages |
| `update all` | tools + templates + gen, no packages |

`update` takes the latest tag; `--ref`, `--gen-from DIR`, `--template-from DIR`,
`--dry-run`. When `lint` says a package's gen.h is old, suggest `update gen <id>`;
"the old generator library, not sinol-gen" means the ingen must be ported first
(workflows/modernize.md).

## Setup of a new contest

- GitHub "Use this template" → the first push runs `setup.yml`, which writes
  the repository name into the statement templates (`\konkurs`, `\signature`).
- Clone, then `python3 tools/contest.py init --id <id> --name "<Name>"`: the
  commit hook, and the name with diacritics (`09Gródek26`) if needed.
- Default limits (1 s, 512 MB) are in `_templates/*/config.yml` and `*zad.tex`.

## Release

Every push to main builds the changed packages (`.github/release.py`) and
updates the GitHub release `tasks`: a table of all tasks with the statement
PDF, the sio2 package, the ocen tests (or `dlazaw.zip`) and the build log. The state column
(❌ work in progress, ⌛ to be verified, ✅ done) is set by editing the table or
by `!todo` / `!ver` / `!done` in a commit title; `!rebuild-<id>` /
`!rebuild-*` forces a rebuild. Mention the markers when you suggest a commit
message for a package that became ready (`abc: final tests !ver`).

## Commits

`<id>: summary` or `*: summary` for repository-wide changes, summary ≤ 50
chars, description lines ≤ 72 (enforced by `.githooks/commit-msg`).
