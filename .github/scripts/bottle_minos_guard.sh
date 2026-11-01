#!/bin/bash
# bottle_minos_guard.sh <bottle.tar.gz> [limit]
# Unpack a bottle and read the minimum macOS version out of every Mach-O in it with otool.
# Fails if any is above the limit (default 14.0), if a Mach-O has no readable version, if the
# bottle holds no Mach-O at all, or if the file is missing. Prints each file's version, so the
# log is the evidence. A bottle tagged for macOS 14 must never carry a file that needs a newer one.
set -u
bottle="${1:?usage: bottle_minos_guard.sh <bottle.tar.gz> [limit]}"
limit="${2:-14.0}"
[ -f "$bottle" ] || { echo "guard: $bottle is missing" >&2; exit 1; }
work="$(mktemp -d "${TMPDIR:-/tmp}/minosguard.XXXXXX")" || exit 1
cleanup() { find "$work" -type f -delete; find "$work" -depth -type d -empty -delete; }
trap cleanup EXIT
tar -xzf "$bottle" -C "$work" || { echo "guard: $bottle cannot be unpacked" >&2; exit 1; }
machos=0
bad=0
while IFS= read -r f; do
  case "$(file -b "$f")" in *Mach-O*) ;; *) continue ;; esac
  machos=$((machos + 1))
  rel="${f#"$work"/}"
  mins="$(otool -l "$f" | awk '$1 == "cmd" && $2 == "LC_BUILD_VERSION" {b = 1; next} b && $1 == "minos" {print $2; b = 0}')"
  if [ -z "$mins" ]; then
    echo "guard: $rel has no readable minimum macOS version" >&2
    bad=1
    continue
  fi
  for m in $mins; do
    echo "guard: $rel minos $m"
    top="$(printf '%s\n' "$limit" "$m" | sort -V | tail -n 1)"
    if [ "$top" != "$limit" ]; then
      echo "guard: $rel needs macOS $m, above the limit $limit" >&2
      bad=1
    fi
  done
done < <(find "$work" -type f | sort)
if [ "$machos" -eq 0 ]; then
  echo "guard: no Mach-O file in $bottle, so there is nothing to check" >&2
  exit 1
fi
exit "$bad"
