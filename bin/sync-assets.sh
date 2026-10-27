#!/bin/sh
# Refresh what the skill bundles:
#   skills/sinol-package/assets/contest-template/   contest-template (packages in foreign repos, new contests)
#   skills/sinol-package/scripts/contest.py         its contest.py
#   skills/sinol-package/references/sinol-gen/      sinol-gen docs + examples (the gen.h API)
#   skills/sinol-package/assets/VERSIONS            what was bundled
# Usage: bin/sync-assets.sh [path/to/contest-template] [path/to/sinol-gen]   (default: ../contest-template ../sinol-gen)
set -eu
BIN=$(dirname "$0")
SRC="${1:-$BIN/../../contest-template}"
GEN="${2:-$BIN/../../sinol-gen}"
SKILL="$BIN/../skills/sinol-package"
[ -f "$SRC/contest.py" ] || { echo "not a contest-template: $SRC" >&2; exit 1; }
[ -f "$GEN/gen.h" ] || { echo "not a sinol-gen checkout: $GEN" >&2; exit 1; }

DST="$SKILL/assets/contest-template"
rm -rf "$DST"
mkdir -p "$DST"
# tracked + untracked-but-not-ignored files (works before the first commit too)
git -C "$SRC" ls-files --cached --others --exclude-standard |
while IFS= read -r f; do
	[ -f "$SRC/$f" ] || continue
	mkdir -p "$DST/$(dirname "$f")"
	cp -p "$SRC/$f" "$DST/$f"
done
cp "$SRC/contest.py" "$SKILL/scripts/contest.py"

R="$SKILL/references/sinol-gen"
rm -rf "$R"
mkdir -p "$R/examples"
cp "$GEN/docs/guide.md" "$GEN/docs/reference.md" "$R/"
cp "$GEN"/examples/*.cpp "$R/examples/"

describe() { git -C "$1" describe --tags --always --dirty 2>/dev/null || echo "no git"; }
{
	echo "contest-template $(describe "$SRC")"
	echo "sinol-gen $(describe "$GEN") (gen.h $(sed -n 's/^#define SINOL_GEN_VERSION "\(.*\)"/\1/p' "$GEN/gen.h"))"
} >"$SKILL/assets/VERSIONS"
cat "$SKILL/assets/VERSIONS"
