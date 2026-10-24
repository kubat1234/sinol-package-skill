# sinol-package — Claude Code skill for SIO2 task packages

A [Claude Code](https://code.claude.com) plugin with one skill for preparing
olympiad task packages for [SIO2 / OIOIOI](https://github.com/sio2project/oioioi)
with [sinol-make](https://github.com/sio2project/sinol-make), in contest
repositories made from [contest-template](https://github.com/kubat1234/contest-template),
with tests written in [sinol-gen](https://github.com/kubat1234/sinol-gen).

- **new package** (standard, checker, library, interactive): proposes a plan
  first, then writes the model and an independent second solution, slow and
  wrong solutions, the ingen (every test, statement examples included), the
  per-group input verifier and the checker / library / interactor, and checks
  it all with sinol-make. Statements only when asked (Polish by default).
- **new contest**: several packages from your specs or from loose ideas.
- **review**: an audit of any package, with findings sorted by severity.
- **modernize**: old Makefile-based packages (committed tests, old generators)
  converted to the current conventions, checked to give the same verdicts.

## Install

Needs `sinol-make` ≥ 1.9.15 (`pipx install sinol-make`), `g++`, `python3`,
`pdflatex` for statements.

Once per computer — afterwards the skill works in every directory:

```sh
claude plugin marketplace add kubat1234/sinol-package-skill
claude plugin install sinol-package@sinol-package
```

(or `/plugin` inside Claude Code). Updates: `claude plugin marketplace update sinol-package`.

A contest repository made from contest-template already declares the plugin
in `.claude/settings.json`: opening it in Claude Code offers to install it.

## Use

```sh
cd 10Grodek27 && claude
```

and ask in your own words — the skill is picked up automatically, or call it
with `/sinol-package:sinol-package`:

```
Zrób paczkę "Dzielniki": dla n ≤ 10^6 liczb ..., podzadania: n ≤ 1000 (30 pkt), bez ograniczeń (70 pkt).
Make a contest of 6 tasks from these ideas: ...
Is the package hak ready for the contest?
Modernize ../06Zakopane26/bit into this repo.
```

## Developing the skill

```
skills/sinol-package/
  SKILL.md                     entry point: modes, ground rules, which file to read when
  workflows/                   new-package, new-contest, review, modernize
  references/                  package format, task types, generator, quality, statement, sinol-make, contest repo
  references/sinol-gen/        copy of sinol-gen's docs and examples        } bin/sync-assets.sh
  scripts/contest.py           copy of contest-template's tools/contest.py  } from ../contest-template
  assets/contest-template/     copy of contest-template                     } and ../sinol-gen
  assets/VERSIONS              which versions were copied
```

After a change in contest-template or sinol-gen run `bin/sync-assets.sh` and
bump `version` in `.claude-plugin/plugin.json`.

To use your working copy instead of the installed plugin, link it as a
personal skill (and don't install the plugin at the same time):

```sh
ln -s "$PWD/skills/sinol-package" ~/.claude/skills/sinol-package
```
