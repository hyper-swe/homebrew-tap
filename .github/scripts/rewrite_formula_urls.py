#!/usr/bin/env python3
"""rewrite_formula_urls.py [--expect N] <formula> <version>

Rewrite the release version inside a formula's literal download URLs.

A formula whose url lines carry the version as text (".../download/v0.7.6/
mgit_0.7.6_darwin_arm64.tar.gz") needs no `version` line: Homebrew reads the
version from the URL. The release update calls this after it has written the
new version, so those URLs follow. A url that interpolates #{version} (mtix's
formula) has no literal version to replace and is left as it is.

Only `url "..."` lines are touched. With --expect N the formula must hold
exactly N literal download urls, or nothing is written: a url format that has
drifted would otherwise be left on the old version and published. Exit codes:
0 done, 1 the expected number of literal urls was not found (nothing written),
2 a usage error or a version that does not look like one.
"""
import re
import sys

URL = re.compile(r'^(\s*url ")(https://github\.com/hyper-swe/[^/"]+/releases/download/)v([0-9][^/"]*)(/[^"]*)(")$')

def main(argv):
    args = argv[1:]
    expect = None
    if len(args) >= 2 and args[0] == "--expect":
        if not re.fullmatch(r"[0-9]+", args[1]):
            print(f"refusing: --expect '{args[1]}' is not a number", file=sys.stderr)
            return 2
        expect = int(args[1])
        args = args[2:]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    path, new = args
    if not re.fullmatch(r"[0-9][0-9A-Za-z.\-]*", new):
        print(f"refusing: '{new}' is not a version", file=sys.stderr)
        return 2
    with open(path) as fh:
        lines = fh.read().split("\n")
    matched = changed = 0
    out = []
    for line in lines:
        m = URL.match(line)
        if not m:
            out.append(line)
            continue
        matched += 1
        head, base, old, tail, close = m.groups()
        rewritten = head + base + "v" + new + tail.replace(old, new) + close
        if rewritten != line:
            changed += 1
        out.append(rewritten)
    if expect is not None and matched != expect:
        print(f"refusing: found {matched} literal download url(s), expected {expect}; nothing written", file=sys.stderr)
        return 1
    with open(path, "w") as fh:
        fh.write("\n".join(out))
    print(f"rewrote {changed} of {matched} literal url line(s) to {new}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
