#!/bin/bash
# Self-test of bottle_minos_guard.sh on real Mach-O files built here with clang: a bottle whose
# every Mach-O has a minimum macOS version at or below the limit passes; one above it, one with
# no readable version, a bottle with no Mach-O at all, and a missing file fail. Needs macOS.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
guard="$here/bottle_minos_guard.sh"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/bottlecheck.XXXXXX")" || exit 1
cleanup() { find "$tmp" -type f -delete; find "$tmp" -depth -type d -empty -delete; }
trap cleanup EXIT
fails=0

# mk <name> <dylib min or ""> [<second dylib min>]: a bottle tarball with a text file and the dylibs
mk() {
  local d="$tmp/$1"; mkdir -p "$d/libx/5.5.0/lib"
  printf 'int f(void) { return 1; }\n' > "$d/x.c"
  printf 'plain text\n' > "$d/libx/5.5.0/NOTICE.txt"
  if [ -n "$2" ]; then clang -dynamiclib -mmacosx-version-min="$2" -o "$d/libx/5.5.0/lib/libx.5.dylib" "$d/x.c" || exit 1; fi
  if [ -n "${3:-}" ]; then clang -dynamiclib -mmacosx-version-min="$3" -o "$d/libx/5.5.0/lib/liby.dylib" "$d/x.c" || exit 1; fi
  tar -czf "$d/bottle.tar.gz" -C "$d" libx
  echo "$d/bottle.tar.gz"
}
expect() { # <label> <want: pass|fail> <tarball> [PATH prefix]
  local out rc=0
  out="$(PATH="${4:+$4:}$PATH" "$guard" "$3" 2>&1)" || rc=$?
  if { [ "$2" = pass ] && [ $rc -ne 0 ]; } || { [ "$2" = fail ] && [ $rc -eq 0 ]; }; then
    echo "FAIL: $1: wanted $2, exit $rc"; echo "$out" | sed 's/^/    /'; fails=$((fails + 1))
  else
    echo "ok: $1 ($2)"
  fi
}

expect "dylib at 14.0" pass "$(mk a 14.0)"
expect "dylib at 13.0" pass "$(mk b 13.0)"
expect "two dylibs at 14.0 and 12.0" pass "$(mk c 14.0 12.0)"
expect "dylib at 15.0" fail "$(mk d 15.0)"
expect "dylib at 26.0" fail "$(mk e 26.0)"
expect "one dylib at 14.0 and one at 15.0" fail "$(mk f 14.0 15.0)"
expect "no Mach-O in the bottle" fail "$(mk g "")"
expect "missing bottle file" fail "$tmp/does-not-exist.tar.gz"
stub="$tmp/stub"; mkdir -p "$stub"
printf '#!/bin/sh\necho "Load command 1"\necho "      cmd LC_SEGMENT_64"\n' > "$stub/otool"; chmod +x "$stub/otool"
expect "Mach-O whose otool output has no minimum version" fail "$(mk h 14.0)" "$stub"

[ "$fails" -eq 0 ] || { echo "$fails check(s) failed"; exit 1; }
echo "bottle guard self-test: all cases behaved"
