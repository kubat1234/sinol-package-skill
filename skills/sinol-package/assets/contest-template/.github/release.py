#!/usr/bin/env python3
"""Build changed packages and publish them in the `tasks` GitHub release.

Run by .github/workflows/release.yml on every push. For each package changed
since the last release it runs `sinol-make export --export-ocen` (through
tools/contest.py) and uploads

    abc.pdf  statement        abc.tgz  package for sio2
    abc_ocen.zip  ocen tests  abc_dlazaw.zip  abc/dlazaw/ (instead of abc_ocen.zip)
    abc.log  build log

The release notes hold a table of all packages. The state column is kept
between runs (edit it by hand, or put !todo / !ver / !done in a commit title,
e.g. `abc: final tests !done`). `!rebuild-abc` / `!rebuild-*` in a commit
title forces a rebuild.

Locally: python3 .github/release.py --dry-run   (builds, writes _build/notes.md)
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from contest import attachments, export_package  # noqa: E402
BUILD = ROOT / "_build"
TAG = "tasks"
ID_RE = re.compile(r"^[a-z]{3}$")
STATES = {"!todo": "❌", "!ver": "⌛", "!done": "✅"}
BEGIN, END = "<!-- BEGIN_STATUS_TABLE -->", "<!-- END_STATUS_TABLE -->"
TIMEOUT = int(os.environ.get("RELEASE_TIMEOUT", "900"))  # seconds per package


def sh(*cmd, check=True, **kw):
    return subprocess.run(cmd, check=check, text=True, capture_output=True, cwd=ROOT, **kw).stdout


def gh(*args, check=True):
    return sh("gh", *args, check=check)


def packages():
    return sorted(p.name for p in ROOT.iterdir() if p.is_dir() and ID_RE.match(p.name) and (p / "config.yml").exists())


def title(pkg):
    m = re.search(r"^title:\s*(.*?)\s*$", (ROOT / pkg / "config.yml").read_text(encoding="utf-8"), re.M)
    return (m.group(1).strip("'\"") if m else "") or "?"


# --------------------------------------------------------------------------- previous release

def load_release(dry_run):
    """(commit of the last release or None, {id: table row cells}, asset names)"""
    if dry_run:
        return None, {}, set()
    if subprocess.run(["gh", "release", "view", TAG], cwd=ROOT, capture_output=True).returncode != 0:
        gh("release", "create", TAG, "--title", "Tasks", "--notes", "No build yet.")
        return None, {}, set()
    body = gh("release", "view", TAG, "--json", "body", "--jq", ".body")
    assets = set(gh("release", "view", TAG, "--json", "assets", "--jq", ".assets[].name").split())
    m = re.search(r"<!-- commit: ([0-9a-f]+) -->", body)
    rows = {}
    for line in body.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and ID_RE.match(cells[0]):
            rows[cells[0]] = cells
    return (m.group(1) if m else None), rows, assets


def commit_known(commit):
    return commit and subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT).returncode == 0


def to_build(prev, pkgs, old_rows):
    """Packages to rebuild and the commit titles since the last release."""
    if not commit_known(prev):
        return set(pkgs), sh("git", "log", "--format=%s").splitlines()
    titles = sh("git", "log", "--format=%s", f"{prev}..HEAD").splitlines()
    if any(re.search(r"!rebuild-\*", t) for t in titles):
        return set(pkgs), titles
    changed = sh("git", "diff", "--name-only", prev, "HEAD").splitlines()
    build = {f.split("/")[0] for f in changed} & set(pkgs)
    build |= {m for t in titles for m in re.findall(r"!rebuild-([a-z]{3})", t)} & set(pkgs)
    build |= set(pkgs) - set(old_rows)  # new packages
    return build, titles


def new_state(pkg, titles, old):
    for t in titles:  # newest first
        if t.startswith(f"{pkg}: "):
            for marker, state in STATES.items():
                if marker in t:
                    return state
    return old or STATES["!todo"]


# --------------------------------------------------------------------------- build

def build(pkg):
    """Export one package into _build/; returns (ok, message)."""
    d = ROOT / pkg
    log = BUILD / f"{pkg}.log"
    for f in d.glob(f"{pkg}*.tgz"):
        f.unlink()
    try:
        with open(log, "w") as out:
            rc = export_package(d, log=out, timeout=TIMEOUT)
        ok, msg = rc == 0, "OK" if rc == 0 else "failed"
    except subprocess.TimeoutExpired:
        ok, msg = False, f"timeout ({TIMEOUT} s)"
    for src, dst in [(d / f"{pkg}.tgz", f"{pkg}.tgz"), (d / "doc" / f"{pkg}zad.pdf", f"{pkg}.pdf")] + attachments(d):
        if src.exists():
            shutil.copyfile(src, BUILD / dst)
    print(f"{pkg}: {msg}", flush=True)
    return ok, msg


# --------------------------------------------------------------------------- notes

def notes(rows, head):
    lines = [
        "Statements, packages and ocen tests, built by a GitHub action on every push.",
        f"Last build: commit {head[:8]} <!-- commit: {head} -->",
        "",
        "State: ❌ work in progress, ⌛ to be verified, ✅ done — edit the table, or put",
        "`!todo` / `!ver` / `!done` in a commit title (`abc: final tests !done`).",
        "Force a rebuild: `!rebuild-abc` or `!rebuild-*` in a commit title.",
        "",
        BEGIN,
        "| Id | State | Name | Files | Last build |",
        "|----|-------|------|-------|------------|",
    ]
    lines += [f"| {' | '.join(r)} |" for r in rows]
    lines.append(END)
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="build everything, write _build/notes.md, no GitHub")
    args = ap.parse_args()

    repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
    url = f"https://github.com/{repo}/releases/download/{TAG}"
    head = sh("git", "rev-parse", "HEAD").strip()
    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir()

    prev, old_rows, assets = load_release(args.dry_run)
    pkgs = packages()
    rebuild, titles = to_build(prev, pkgs, old_rows)
    print(f"last release: {prev or '-'}; building: {' '.join(sorted(rebuild)) or 'nothing'}", flush=True)

    rows, failed = [], []
    for pkg in pkgs:
        old = old_rows.get(pkg, ["", "", "", "", ""])
        state = new_state(pkg, titles, old[1])
        if pkg in rebuild:
            ok, msg = build(pkg)
            if not ok:
                failed.append(pkg)
            files = [f"[{label}]({url}/{name})" for label, name in
                     (("statement", f"{pkg}.pdf"), ("package", f"{pkg}.tgz"),
                      ("ocen", f"{pkg}_ocen.zip"), ("dlazaw", f"{pkg}_dlazaw.zip"), ("log", f"{pkg}.log"))
                     if (BUILD / name).exists()]
            files_cell = " · ".join(files)
            status = f"{'✅' if ok else '❌'} {msg} ({head[:8]})"
        else:
            files_cell, status = old[3:5]
        rows.append([pkg, state, title(pkg).replace("|", "&vert;"), files_cell, status])

    text = notes(rows, head)
    (BUILD / "notes.md").write_text(text, encoding="utf-8")
    if args.dry_run:
        print(text)
    else:
        built = [f for f in BUILD.iterdir() if f.name != "notes.md"]
        if built:
            gh("release", "upload", TAG, "--clobber", *map(str, built))
        # assets of rebuilt packages that were not produced this time, and of deleted packages
        produced = {f.name for f in built}
        for name in sorted(assets):
            pkg = name[:3]
            if (pkg in rebuild and name not in produced) or pkg not in pkgs:
                gh("release", "delete-asset", TAG, name, "-y", check=False)
        gh("release", "edit", TAG, "--latest", "--notes-file", str(BUILD / "notes.md"))
    if failed:
        print("failed: " + " ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
