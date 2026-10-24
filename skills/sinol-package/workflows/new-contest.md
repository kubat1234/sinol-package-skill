# Workflow: new contest / several packages

## New repository

The normal way: on GitHub **Use this template** on the contest-template
repository (the first push fills the contest name into the templates), clone,
then `python3 tools/contest.py init --id <id> --name "<name>"` (commit hook,
name with diacritics). Default limits are in `_templates/*/config.yml`. Details,
the release and `update`: references/contest-repo.md.
If the user has no GitHub template at hand, create it locally from the copy
bundled with this skill:

```sh
cp -r <skill>/assets/contest-template <dir> && cd <dir> && git init
python3 tools/contest.py init --id 10grodek27 --name "10Gródek27"
```

(`<skill>` is the directory containing this SKILL.md.) Don't commit or push
unless asked.

## Several packages

First ask (one question) how much control the user wants:

- **They specify each package** (id/title, type, limits, groups) → for each
  package run the new-package workflow; propose all plans together in one
  message and get one acceptance.
- **They give problem ideas** (or just "N problems, easy to hard") → propose a
  contest plan: per task an id, title, one-line idea, type, difficulty, groups.
  After acceptance build each package.

Plan table to propose:

```
id   title         type  difficulty  idea                                   groups
abc  Ciąg          std   easy        sum of a range after updates           2
...
```

## Building many packages

- Easy packages may be delegated to subagents (`Agent`, `model: "sonnet"`), one
  package per agent, with: the contest root, the accepted plan for that package,
  "follow workflows/new-package.md steps 3–4, do not write the statement, do
  not touch other packages, report the run table". Hard packages: do them
  yourself (or an agent with the inherited model) with the full new-package flow.
- Agents must not run `sinol-make init` for the same id in parallel; create all
  package directories first, then hand them out.
- When agents finish, **review every package yourself** (workflows/review.md,
  quick version: lint, run table, generator coverage, inwer strictness) before
  reporting. Don't relay an agent's "done" unchecked.
- Finish with `python3 tools/contest.py lint`, and a summary per package.
