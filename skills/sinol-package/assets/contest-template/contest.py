#!/usr/bin/env python3
"""Contest repository tool: what sinol-make does not do.

    python3 contest.py init --id 10grodek27 --name "10Gródek27"   # once per contest repo
    python3 contest.py lint [-v] [abc ...]        # static checks, nothing is compiled
    python3 contest.py export-all [abc ...]       # sinol-make export --export-ocen -> _export/
    python3 contest.py update gen|tools|templates|all [abc ...|all]   # newer gen.h / tools / templates
    python3 contest.py logo logo.png [abc ...]    # new logo in _templates and the packages

Everything else is sinol-make itself: `sinol-make init abc -t _templates std`
creates a package, `gen`, `inwer`, `run`, `verify`, `doc`, `export` work on it.
"""

import argparse
import fnmatch
import filecmp
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

try:
    import yaml
except ImportError:  # sinol-make depends on PyYAML, so it is normally present; `init` works without it
    yaml = None

HERE = Path(__file__).resolve().parent
GEN_REPO = "kubat1234/sinol-gen"                # gen.h
TEMPLATE_REPO = "kubat1234/contest-template"    # contest.py, .github/, ..., README.md, _templates/
ROOT = HERE  # contest root; --root overrides


def find_templates(root):
    """The contest's own _templates/, else the copy bundled with the sinol-package skill."""
    for t in (root / "_templates", HERE / "_templates", HERE.parent / "assets" / "contest-template" / "_templates"):
        if (t / "std").is_dir():
            return t
    return root / "_templates"


TEMPLATES = find_templates(ROOT)
# Files every package gets from its template (the same copy in each _templates/<type>/).
SHARED = ["prog/oi.h", "prog/gen.h", "doc/sinol.cls", "doc/logo.png",
          "doc/languages/sinol-en.cls", "doc/languages/sinol-lang.cls", "doc/languages/sinol-pl.cls"]
ID_RE = re.compile(r"^[a-z]{3}$")


# --------------------------------------------------------------------------- helpers

def color(code, text):
    return f"\033[{code}m{text}\033[0m" if sys.stdout.isatty() else text


def load_yaml(path):
    if yaml is None:
        sys.exit("PyYAML is missing: pip install --user sinol-make (or pyyaml)")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def packages(ids=None):
    """Package ids (relative to the contest root) or paths to package directories."""
    if ids:
        result = []
        for i in ids:
            p = ROOT / i if ID_RE.match(i) and (ROOT / i).is_dir() else Path(i).resolve()
            if not (p / "config.yml").exists() and not (p / "prog").is_dir():
                sys.exit(f"{i}: no such package")
            result.append(p)
        return result
    return sorted(p for p in ROOT.iterdir() if p.is_dir() and ID_RE.match(p.name))


def test_group(name, task_id):
    """'abc2c.in' -> 2, 'abc1ocen.in' -> 0 (same rule as sinol-make)."""
    tid = Path(name).stem[len(task_id):]
    if tid.endswith("ocen"):
        return 0
    m = re.match(r"\d+", tid)
    return int(m.group()) if m else None


def task_type(pkg):
    prog, tid = pkg / "prog", pkg.name
    if any(prog.glob(f"{tid}soc.*")):
        return "soc"
    cfg = load_yaml(pkg / "config.yml") if (pkg / "config.yml").exists() else {}
    if cfg.get("extra_compilation_files") or cfg.get("library"):
        return "lib"
    if any(prog.glob(f"{tid}chk.*")):
        return "chk"
    return "std"


# --------------------------------------------------------------------------- init

def cmd_init(args):
    """Put the contest into the statement templates and enable the commit hook."""
    cid = args.id or input("Contest id (e.g. 10grodek27): ").strip()
    name = args.name or input("Contest name (e.g. 10Gródek27): ").strip()
    if not (ROOT / "_templates").is_dir():
        sys.exit(f"{ROOT}: no _templates/ - not a contest repository")
    set_contest_name(cid, name)
    readme = ROOT / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        readme.write_text(re.sub(r"^# .*$", lambda _: f"# {name}", text, count=1, flags=re.M), encoding="utf-8")
    if (ROOT / ".git").exists():
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
        print("commit hook enabled (git config core.hooksPath .githooks)")
    else:
        print("not a git repository - run `git init`, then `contest.py init` again for the hook")


def set_contest_name(cid, name, quiet=False):
    for tex in sorted((ROOT / "_templates").glob("*/doc/__ID__zad.tex")):
        text = tex.read_text(encoding="utf-8")
        text = re.sub(r"\\signature\{[^}]*\}", lambda _: f"\\signature{{{cid}}}", text)
        text = re.sub(r"\\konkurs\{[^}]*\}", lambda _: f"\\konkurs{{{name}}}", text)
        tex.write_text(text, encoding="utf-8")
        if not quiet:
            print(f"{tex.relative_to(ROOT)}: \\signature{{{cid}}} \\konkurs{{{name}}}")


def contest_name():
    """(\\signature, \\konkurs) from the statement templates, or None if not set yet."""
    tex = ROOT / "_templates" / "std" / "doc" / "__ID__zad.tex"
    if not tex.exists():
        return None
    text = tex.read_text(encoding="utf-8")
    sig, kon = re.search(r"\\signature\{([^}]*)\}", text), re.search(r"\\konkurs\{([^}]*)\}", text)
    if not sig or not kon or "TODO" in (sig.group(1), kon.group(1)):
        return None
    return sig.group(1), kon.group(1)


# --------------------------------------------------------------------------- gen.h versions

GEN_VERSION_RE = re.compile(r'#define SINOL_GEN_VERSION "([^"]+)"')


def gen_version(path):
    m = GEN_VERSION_RE.search(Path(path).read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def version_key(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


def lint_gen_h(r, f, ref, tid):
    mine = gen_version(f)
    theirs = gen_version(ref) if ref.exists() else None
    if mine is None:
        r.warn("prog/gen.h is the old generator library, not sinol-gen - fine for this ingen; port the ingen "
               f"before `contest.py update gen {tid}`")
    elif theirs and version_key(mine) < version_key(theirs):
        r.warn(f"gen.h {mine}, _templates have {theirs}: `contest.py update gen {tid}`")
    elif theirs == mine and not filecmp.cmp(f, ref, shallow=False):
        r.warn(f"gen.h {mine} was changed in the package (differs from the released {mine}) - "
               f"move the change to {GEN_REPO}")


# --------------------------------------------------------------------------- lint

class Report:
    def __init__(self, pkg):
        self.pkg, self.items = pkg, []

    def error(self, msg):
        self.items.append(("E", msg))

    def warn(self, msg):
        self.items.append(("W", msg))

    def info(self, msg):
        self.items.append(("I", msg))

    def count(self, kind):
        return sum(1 for k, _ in self.items if k == kind)


def lint_package(pkg):
    r = Report(pkg)
    tid = pkg.name
    if not ID_RE.match(tid):
        r.error("package directory name must be 3 lowercase letters")
    cfg_path = pkg / "config.yml"
    if not cfg_path.exists():
        r.error("missing config.yml")
        return r
    try:
        cfg = load_yaml(cfg_path)
    except yaml.YAMLError as e:
        r.error(f"config.yml does not parse: {e}")
        return r
    ttype = task_type(pkg)

    # --- config.yml
    if cfg.get("sinol_task_id") != tid:
        r.error(f"sinol_task_id is {cfg.get('sinol_task_id')!r}, expected {tid!r}")
    title = str(cfg.get("title", ""))
    if not title or title == "TODO" or "__" in title:
        r.error("title is missing or still a placeholder")
    if cfg.get("sinol_contest_type") != "oi":
        r.warn(f"sinol_contest_type is {cfg.get('sinol_contest_type')!r}, the contest convention is 'oi'")
    for key in ("time_limit", "memory_limit"):
        if key not in cfg:
            r.error(f"missing {key}")
    scores = cfg.get("scores") or {}
    if not scores:
        r.error("missing scores")
    else:
        if any(not isinstance(g, int) or g < 1 for g in scores):
            r.error("scores keys must be group numbers >= 1")
        total = sum(scores.values())
        expected = cfg.get("sinol_total_score", 100)
        if total != expected:
            r.error(f"scores sum to {total}, expected {expected}")
    deps = cfg.get("subtask_dependencies") or {}
    for g, req in deps.items():
        if g not in scores:
            r.error(f"subtask_dependencies: group {g} has no score")
        for d in req or []:
            if d == 0 or d not in scores:
                r.error(f"subtask_dependencies: group {g} depends on unknown group {d}")
            if d == g:
                r.error(f"subtask_dependencies: group {g} depends on itself")
    if deps and has_cycle(deps):
        r.error("subtask_dependencies contain a cycle")
    for g, req in deps.items():  # dependencies are NOT transitive in sio2
        closure = transitive(deps, g)
        missing = closure - set(req or [])
        if missing:
            r.warn(f"subtask_dependencies: group {g} reaches {sorted(missing)} only indirectly "
                   f"(dependencies are not transitive - list them explicitly if intended)")

    # --- programs
    prog = pkg / "prog"
    names = {p.name for p in prog.iterdir()} if prog.is_dir() else set()
    if not any(re.fullmatch(rf"{tid}\.(cpp|c|py|java|rs)", n) for n in names):
        r.error(f"missing model solution prog/{tid}.cpp")
    has_ingen = any(re.fullmatch(rf"{tid}ingen\.(cpp|py|sh)", n) for n in names)
    if not any(re.fullmatch(rf"{tid}inwer\.(cpp|py)", n) for n in names):
        r.warn("missing input verifier prog/" + tid + "inwer.cpp")
    if ttype == "soc" and f"{tid}soc.cpp" not in names:
        r.error("interactive task without prog/" + tid + "soc.cpp")
    for f in cfg.get("extra_compilation_files") or []:
        if f not in names:
            r.error(f"extra_compilation_files: prog/{f} does not exist")
    known = re.compile(rf"^({tid}(\d*|s\d+|b\d+|ingen|inwer|chk|soc|lib)\.(cpp|c|py|java|rs|sh|h|hpp)"
                       rf"|{tid}lib.*|oi\.h|gen\.h|testgen\.hpp|.*\.(h|hpp))$")
    for n in sorted(names):
        if not known.match(n):
            r.warn(f"prog/{n}: unexpected file (sinol-make ignores it; remove it or rename it)")
    solutions = sorted(n for n in names if re.fullmatch(rf"{tid}(\d*|s\d+|b\d+)\.(cpp|c|py|java|rs)", n))
    if not any(re.fullmatch(rf"{tid}b\d+\..*", n) for n in solutions):
        r.info("no wrong solutions (prog/" + tid + "b*.cpp) - the tests are not shown to reject anything")
    if "sinol_expected_scores" not in cfg or not cfg.get("sinol_expected_scores"):
        r.info("no sinol_expected_scores yet - run `sinol-make run` and accept the results")

    # --- tests
    ins = sorted((pkg / "in").glob(f"{tid}*.in")) if (pkg / "in").is_dir() else []
    outs = sorted((pkg / "out").glob(f"{tid}*.out")) if (pkg / "out").is_dir() else []
    test_re = re.compile(rf"^{tid}\d+[a-z]?[a-z0-9]*\.(in|out)$")
    for d in ("in", "out"):
        for p in (pkg / d).glob("*") if (pkg / d).is_dir() else []:
            if p.is_file() and not test_re.match(p.name) and not p.name.startswith("."):
                r.error(f"{d}/{p.name}: invalid test name")
    if ttype != "soc":
        out_stems = {p.stem for p in outs}
        for p in ins:
            if p.stem not in out_stems:
                (r.warn if has_ingen else r.error)(f"in/{p.name} has no out/{p.stem}.out")
    if not ins and has_ingen:
        r.info("no tests in in/ yet - run `sinol-make gen` to check them against the scores")
    elif not any(test_group(p.name, tid) == 0 for p in ins):
        r.warn("no example test (g.example(...) in the ingen, or in/" + tid + "0.in)")
    static = cfg.get("sinol_static_tests") or []
    for pat in static:
        if not any(fnmatch.fnmatch(p.name, pat) for p in ins):
            r.warn(f"sinol_static_tests: {pat!r} matches no file in in/")
    if not has_ingen:
        r.info("no generator: all tests must be committed (add `!in/*.in` and `!out/*.out` to "
               f"{tid}/.gitignore)")
    groups = {test_group(p.name, tid) for p in ins} - {0, None}
    if groups and scores:
        for g in sorted(set(scores) - groups):
            r.error(f"group {g} has a score but no tests in in/")
        for g in sorted(groups - set(scores)):
            r.error(f"tests of group {g} exist but the group has no score")
    elif has_ingen and scores:
        r.info("only example tests in in/ - run `sinol-make gen` to check groups against scores")

    # --- statement
    zad = pkg / "doc" / f"{tid}zad.tex"
    if not zad.exists():
        r.warn(f"missing statement doc/{tid}zad.tex")
    else:
        lint_statement(r, zad.read_text(encoding="utf-8"), cfg, tid)

    # --- leftovers
    template_left = []
    for p in sorted(list(prog.glob("*")) + list((pkg / "doc").glob("*.tex")) + list((pkg / "dlazaw").rglob("*"))):
        if not p.is_file() or p.suffix not in (".cpp", ".c", ".h", ".hpp", ".py", ".tex"):
            continue
        if p.name in ("oi.h", "gen.h", "testgen.hpp"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if "__ID__" in text or "__TITLE__" in text:
            r.error(f"{p.relative_to(pkg)}: unreplaced template placeholder")
        if "TEMPLATE:" in text:
            template_left.append(str(p.relative_to(pkg)))
        if p.suffix == ".tex" and re.search(r"\bTODO\b", text):
            r.warn(f"{p.relative_to(pkg)}: contains TODO")

    if template_left:
        r.warn("template example code (marked TEMPLATE:) still in: " + ", ".join(template_left))

    # --- shared files
    for rel in SHARED:
        f = pkg / rel
        if not f.exists():
            if rel == "prog/gen.h":
                continue  # only needed by generators that use it
            (r.warn if rel.startswith("doc/") else r.error)(f"missing shared file {rel}")
        elif rel == "prog/gen.h":
            lint_gen_h(r, f, TEMPLATES / "std" / rel, tid)
        elif (TEMPLATES / "std" / rel).exists() and not filecmp.cmp(f, TEMPLATES / "std" / rel, shallow=False):
            r.warn(f"{rel} differs from _templates/std (copy the current version if that is not intended)")
    return r


def lint_statement(r, tex, cfg, tid):
    m = re.search(r"\\id\{(\w+)\}", tex)
    if m and m.group(1) != tid:
        r.error(f"statement \\id{{{m.group(1)}}} differs from package id")
    ram = re.search(r"\\RAM\{(\d+)\}", tex)
    if ram and "memory_limit" in cfg and int(ram.group(1)) != cfg["memory_limit"] // 1024:
        r.warn(f"statement \\RAM{{{ram.group(1)}}} MB but memory_limit is {cfg['memory_limit']} KiB "
               f"({cfg['memory_limit'] // 1024} MB)")
    rows = re.findall(r"^\s*(\d+)\s*&\s*\$?\s*(\d+)\s*\$?\s*&(.*?)\\\\", tex, re.M)
    scores = cfg.get("scores") or {}
    if not rows:
        r.info("no subtask table found in the statement")
        return
    table = {int(g): int(p) for g, p, _ in rows}
    if table != scores:
        r.error(f"subtask table in the statement {table} differs from config.yml scores {dict(scores)}")
    limits = cfg.get("time_limits") or {}
    for g, _, rest in rows:
        tm = re.search(r"\$?\s*([\d.,]+)\s*\$?\s*s\s*$", rest.strip())
        if not tm:
            continue
        stated = float(tm.group(1).replace(",", "."))
        real = limits.get(int(g), cfg.get("time_limit", 0)) / 1000
        if abs(stated - real) > 1e-9:
            r.error(f"statement says {stated:g} s for group {g}, config.yml has {real:g} s")


def has_cycle(deps):
    state = {}

    def visit(g):
        if state.get(g) == 1:
            return True
        if state.get(g) == 2:
            return False
        state[g] = 1
        if any(visit(d) for d in deps.get(g) or []):
            return True
        state[g] = 2
        return False

    return any(visit(g) for g in deps)


def transitive(deps, g):
    seen, stack = set(), list(deps.get(g) or [])
    while stack:
        d = stack.pop()
        if d not in seen:
            seen.add(d)
            stack.extend(deps.get(d) or [])
    return seen


def cmd_lint(args):
    errors = 0
    targets = packages(args.ids)
    check_sinol_make_version(targets)
    for pkg in targets:
        r = lint_package(pkg)
        shown = [(k, m) for k, m in r.items if args.verbose or k != "I"]
        head = f"{pkg.name}: {r.count('E')} errors, {r.count('W')} warnings"
        print(color("31" if r.count("E") else "33" if r.count("W") else "32", head))
        for k, m in shown:
            print(f"  {color({'E': '31', 'W': '33', 'I': '36'}[k], k)} {m}")
        errors += r.count("E")
    sys.exit(1 if errors else 0)


# --------------------------------------------------------------------------- sinol-make

MIN_SINOL_MAKE = (1, 9, 15)  # first version that scores subtask_dependencies


def check_sinol_make_version(targets):
    if not shutil.which("sinol-make"):
        print(color("33", "sinol-make not found: pip install --user sinol-make"))
        return
    out = subprocess.run(["sinol-make", "--version"], capture_output=True, text=True).stdout
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
    if not m or tuple(map(int, m.groups())) >= MIN_SINOL_MAKE:
        return
    uses_deps = [p.name for p in targets
                 if (p / "config.yml").exists() and load_yaml(p / "config.yml").get("subtask_dependencies")]
    if uses_deps:
        print(color("31", f"sinol-make {m.group()} ignores subtask_dependencies (used by {' '.join(uses_deps)}); "
                          f"upgrade: pipx upgrade sinol-make  (or pip install --user -U sinol-make)"))


def export_package(pkg, extra=(), log=None, timeout=None):
    """`sinol-make export --export-ocen` in pkg; returns the exit code (also used by .github/release.py).

    The archive gets attachments/<id>ocen.zip (the 0* and *ocen tests), or attachments/dlazaw.zip
    instead if the package has a dlazaw/ directory (files for contestants, see README.md).
    The statement includes in/<id>0*.in, so in a fresh clone the tests are generated first."""
    def sm(*cmd):
        print(color("1", f"[{pkg.name}] sinol-make {' '.join(cmd)}"), file=log or sys.stdout, flush=True)
        return subprocess.run(["sinol-make", *cmd], cwd=pkg, stdin=subprocess.DEVNULL, stdout=log,
                              stderr=subprocess.STDOUT if log else None, timeout=timeout).returncode

    if "--no-statement" not in extra and not list(pkg.glob(f"in/{pkg.name}0*.in")):
        rc = sm("gen")
        if rc != 0:
            return rc
    return sm("export", "--export-ocen", *extra)


def attachments(pkg):
    """(file in the last export, name to publish it under): ocen tests, dlazaw"""
    a = pkg / ".cache" / "export" / pkg.name / "attachments"
    return [(a / f"{pkg.name}ocen.zip", f"{pkg.name}_ocen.zip"), (a / "dlazaw.zip", f"{pkg.name}_dlazaw.zip")]


def cmd_export_all(args):
    out_dir = ROOT / "_export"
    out_dir.mkdir(exist_ok=True)
    failed = []
    for pkg in packages(args.ids):
        extra = ["--no-statement"] if args.no_statement else []
        if export_package(pkg, extra) != 0:
            failed.append(pkg.name)
            continue
        for f in list(pkg.glob(f"{pkg.name}*.tgz")) + list(pkg.glob(f"{pkg.name}*.zip")):
            shutil.move(str(f), out_dir / f.name)
        for src, name in attachments(pkg):
            if src.exists():
                shutil.copyfile(src, out_dir / name)
    print(f"archives in {out_dir.relative_to(ROOT)}/")
    if failed:
        print(color("31", "failed: " + " ".join(failed)))
        sys.exit(1)


# --------------------------------------------------------------------------- update

def latest_tag(repo):
    try:
        with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/tags?per_page=100", timeout=30) as f:
            tags = [t["name"] for t in json.load(f) if re.match(r"^v?\d", t["name"])]
        return max(tags, key=version_key) if tags else None
    except Exception:
        return None


def fetch(repo, ref, local):
    """(directory with the files of repo at ref, description). local = a checkout to use instead."""
    if local:
        return Path(local).resolve(), str(local)
    ref = ref or latest_tag(repo) or "main"
    url = f"https://codeload.github.com/{repo}/tar.gz/{ref}"
    try:
        with urllib.request.urlopen(url, timeout=120) as f:
            data = f.read()
    except Exception as e:
        sys.exit(f"cannot download {repo}@{ref}: {e}")
    tmp = Path(tempfile.mkdtemp(prefix="contest-update-"))
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        try:
            tar.extractall(tmp, filter="data")
        except TypeError:  # Python < 3.12
            tar.extractall(tmp)
    return next(tmp.iterdir()), f"{repo}@{ref}"


def copy_if_changed(src, dst, dry, what=None):
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return False
    print(f"  {'would update' if dry else 'updated'} {what or dst.relative_to(ROOT)}")
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return True


def build_and_run_ingen(pkg, gen_h, workdir):
    """Generate the package's tests with the given gen.h into workdir/out; returns an error or None."""
    prog = workdir / "prog"
    shutil.copytree(pkg / "prog", prog)
    shutil.copyfile(gen_h, prog / "gen.h")
    ingen = prog / f"{pkg.name}ingen.cpp"
    exe = workdir / "ingen"
    c = subprocess.run(["g++", "-std=c++20", "-O2", f"-I{prog}", str(ingen), "-o", str(exe)],
                       capture_output=True, text=True)
    if c.returncode:
        first = next((l for l in c.stderr.splitlines() if "error" in l), c.stderr.strip()[:200])
        return f"does not compile: {first}"
    out = workdir / "out"
    out.mkdir()
    r = subprocess.run([str(exe)], cwd=out, capture_output=True, text=True, timeout=1800)
    return f"ingen failed: {r.stderr.strip()[-200:]}" if r.returncode else None


def same_tests(pkg, old_h, new_h):
    """None if the ingen gives byte-identical tests with both gen.h, else what differs."""
    with tempfile.TemporaryDirectory() as t:
        a, b = Path(t) / "old", Path(t) / "new"
        a.mkdir(), b.mkdir()
        err = build_and_run_ingen(pkg, old_h, a)
        if err:
            return f"cannot compare, with the current gen.h the ingen {err}"
        err = build_and_run_ingen(pkg, new_h, b)
        if err:
            return f"with the new gen.h the ingen {err}"
        fa = {p.name: p for p in (a / "out").iterdir()}
        fb = {p.name: p for p in (b / "out").iterdir()}
        changed = sorted(n for n in fa.keys() | fb.keys()
                         if n not in fa or n not in fb or not filecmp.cmp(fa[n], fb[n], shallow=False))
        return f"tests would change: {' '.join(changed[:10])}{' ...' if len(changed) > 10 else ''}" if changed else None


def selected(ids):
    """Packages named on the command line: none, some, or `all`."""
    return packages() if ids == ["all"] else packages(ids) if ids else []


def update_gen(src, ids, dry, force):
    new = src / "gen.h"
    if not new.exists():
        sys.exit(f"{src}: no gen.h")
    print(f"gen.h {gen_version(new) or '?'}:")
    for f in sorted((ROOT / "_templates").glob("*/prog/gen.h")):
        copy_if_changed(new, f, dry)
    for pkg in selected(ids):
        f = pkg / "prog" / "gen.h"
        if not f.exists():
            continue
        if filecmp.cmp(f, new, shallow=False):
            print(f"  {pkg.name}: up to date")
            continue
        problem = same_tests(pkg, f, new) if (pkg / "prog" / f"{pkg.name}ingen.cpp").exists() else None
        if problem and not force:
            print(color("33", f"  {pkg.name}: NOT updated - {problem} (--force to update anyway)"))
            continue
        copy_if_changed(new, f, dry, f"{pkg.name}/prog/gen.h ({gen_version(f) or 'old'} -> {gen_version(new)}"
                                     f"{', ' + problem if problem else ', tests unchanged'})")


TOOL_DIRS = (".github", ".githooks", ".claude")
TOOL_FILES = ("contest.py", ".gitignore")


def update_tools(src, dry):
    print("tools:")
    for top in TOOL_DIRS:
        for f in sorted((src / top).rglob("*")) if (src / top).is_dir() else []:
            if f.is_file():
                copy_if_changed(f, ROOT / f.relative_to(src), dry)
    for name in TOOL_FILES:
        if (src / name).is_file():
            copy_if_changed(src / name, ROOT / name, dry)
    old = ROOT / "tools" / "contest.py"  # contest.py was in tools/ up to v1.0.3
    if old.exists() and (src / "contest.py").exists():
        print(f"  {'would remove' if dry else 'removed'} tools/contest.py (now ./contest.py)")
        if not dry:
            old.unlink()
            if not any((ROOT / "tools").iterdir()):
                (ROOT / "tools").rmdir()
    update_readme(src, dry)


def update_readme(src, dry):
    """README.md from contest-template, keeping this contest's title (the first `# ` line)."""
    new, dst = src / "README.md", ROOT / "README.md"
    if not new.is_file():
        return
    text = new.read_text(encoding="utf-8")
    old = dst.read_text(encoding="utf-8") if dst.exists() else ""
    title = re.search(r"^# .*$", old, flags=re.M)
    if title:
        text = re.sub(r"^# .*$", lambda _: title.group(0), text, count=1, flags=re.M)
    if text != old:
        print(f"  {'would update' if dry else 'updated'} README.md (title kept)")
        if not dry:
            dst.write_text(text, encoding="utf-8")


def update_templates(src, ids, dry):
    print("templates:")
    name = contest_name()
    for f in sorted((ROOT / "_templates").rglob("*")):  # files removed from contest-template
        rel = f.relative_to(ROOT)
        if f.is_file() and f.name != "gen.h" and not (src / rel).exists():
            print(f"  {'would remove' if dry else 'removed'} {rel}")
            if not dry:
                f.unlink()
    for f in sorted((src / "_templates").rglob("*")):
        rel = f.relative_to(src)
        # gen.h: `update gen`; logo.png belongs to the contest: `logo`
        if f.is_file() and f.name not in ("gen.h", "logo.png") and not rel.parts[-1].endswith("zad.tex"):
            copy_if_changed(f, ROOT / rel, dry)
    for f in sorted((src / "_templates").glob("*/doc/__ID__zad.tex")):
        dst = ROOT / f.relative_to(src)
        text = f.read_text(encoding="utf-8")
        if name:  # keep this contest's \signature and \konkurs
            text = re.sub(r"\\signature\{[^}]*\}", lambda _: f"\\signature{{{name[0]}}}", text)
            text = re.sub(r"\\konkurs\{[^}]*\}", lambda _: f"\\konkurs{{{name[1]}}}", text)
        if not dst.exists() or dst.read_text(encoding="utf-8") != text:
            print(f"  {'would update' if dry else 'updated'} {dst.relative_to(ROOT)}")
            if not dry:
                dst.write_text(text, encoding="utf-8")
    for pkg in selected(ids):  # shared files of packages
        for rel in SHARED:
            if rel not in ("prog/gen.h", "doc/logo.png") and (src / "_templates" / "std" / rel).exists() \
                    and (pkg / rel).exists():
                copy_if_changed(src / "_templates" / "std" / rel, pkg / rel, dry)


def cmd_update(args):
    what = args.what
    if what in ("tools", "templates", "all"):
        src, desc = fetch(TEMPLATE_REPO, args.ref if what != "all" else None, args.template_from)
        print(f"from {desc}")
        if what in ("tools", "all"):
            update_tools(src, args.dry_run)
        if what in ("templates", "all"):
            update_templates(src, args.ids if what == "templates" else [], args.dry_run)
    if what in ("gen", "all"):
        src, desc = fetch(GEN_REPO, args.ref if what == "gen" else None, args.gen_from)
        print(f"from {desc}")
        update_gen(src, args.ids if what == "gen" else [], args.dry_run, args.force)
    if args.dry_run:
        print("(dry run - nothing was changed)")


# --------------------------------------------------------------------------- logo

def cmd_logo(args):
    """The contest logo (doc/logo.png, the top of every statement) into _templates and the packages."""
    src = Path(args.file).resolve()
    if not src.is_file() or src.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"{args.file}: not a PNG file")
    for f in sorted((ROOT / "_templates").glob("*/doc")) + [pkg / "doc" for pkg in packages(args.ids)]:
        if f.is_dir():
            copy_if_changed(src, f / "logo.png", args.dry_run)
    if args.dry_run:
        print("(dry run - nothing was changed)")


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="contest id/name into _templates, enable the commit hook")
    p.add_argument("--id")
    p.add_argument("--name")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("lint", help="static checks of packages")
    p.add_argument("ids", nargs="*")
    p.add_argument("-v", "--verbose", action="store_true", help="also show info messages")
    p.set_defaults(func=cmd_lint)

    p = sub.add_parser("export-all", help="sinol-make export --export-ocen for packages, archives to _export/")
    p.add_argument("ids", nargs="*")
    p.add_argument("--no-statement", action="store_true")
    p.set_defaults(func=cmd_export_all)

    p = sub.add_parser("update", help="newer gen.h (sinol-gen), tools or _templates (contest-template) from GitHub",
                       description="gen: gen.h into _templates/*/prog and the given packages (only if their tests "
                                   "stay identical, unless --force). tools: contest.py, .github/, .githooks/, .claude/, .gitignore, "
                                   "README.md (keeps the title). templates: "
                                   "_templates/ (keeps the contest name and logo, removes what contest-template no longer has; "
                                   "gen.h only via `gen`) and the shared files "
                                   "(oi.h, sinol.cls, ...) of the given packages. all: tools + templates + gen, "
                                   "no packages. Default version: the latest tag.")
    p.add_argument("what", choices=["gen", "tools", "templates", "all"])
    p.add_argument("ids", nargs="*", help="packages to update too, or `all`")
    p.add_argument("--ref", help="tag or branch instead of the latest tag")
    p.add_argument("--gen-from", metavar="DIR", help="a local sinol-gen checkout instead of GitHub")
    p.add_argument("--template-from", metavar="DIR", help="a local contest-template checkout instead of GitHub")
    p.add_argument("--dry-run", action="store_true", help="only show what would change")
    p.add_argument("--force", action="store_true", help="update gen.h of packages even if their tests would change")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("logo", help="new contest logo (PNG) in _templates and the packages")
    p.add_argument("file", help="PNG file, e.g. 450x225 (shown 2 cm high)")
    p.add_argument("ids", nargs="*", help="packages (default: all)")
    p.add_argument("--dry-run", action="store_true", help="only show what would change")
    p.set_defaults(func=cmd_logo)

    ap.add_argument("--root", help="contest root (default: the repository containing this script)")
    args = ap.parse_args()
    if args.root:
        global ROOT, TEMPLATES
        ROOT = Path(args.root).resolve()
        TEMPLATES = find_templates(ROOT)
    args.func(args)


if __name__ == "__main__":
    main()
