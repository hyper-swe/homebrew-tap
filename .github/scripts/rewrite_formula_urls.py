#!/usr/bin/env python3
"""rewrite_formula_urls.py <formula> <version>

Rewrite the release version inside a formula's literal download URLs.

A formula whose url lines carry the version as text (".../download/v0.7.6/
mgit_0.7.6_darwin_arm64.tar.gz") needs no `version` line: Homebrew reads the
version from the URL. The release update calls this after it has written the
new version, so those URLs follow. A url that interpolates #{version} (mtix's
formula) has no literal version to replace and is left as it is.

Only `url "..."` lines are touched. Exit 2 on a usage error, 1 when a literal
url was found but the version in it could not be read.
"""
import re
import sys

URL = re.compile(r'^(\s*url ")(https://github\.com/hyper-swe/[^/"]+/releases/download/)v([0-9][^/"]*)(/[^"]*)(")$')

def main(argv):
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    path, new = argv[1], argv[2]
    if not re.fullmatch(r"[0-9][0-9A-Za-z.\-]*", new):
        print(f"refusing: '{new}' is not a version", file=sys.stderr)
        return 2
    with open(path) as fh:
        lines = fh.read().split("\n")
    changed = 0
    out = []
    for line in lines:
        m = URL.match(line)
        if not m:
            out.append(line)
            continue
        head, base, old, tail, close = m.groups()
        rewritten = head + base + "v" + new + tail.replace(old, new) + close
        if rewritten != line:
            changed += 1
        out.append(rewritten)
    with open(path, "w") as fh:
        fh.write("\n".join(out))
    print(f"rewrote {changed} url line(s) to {new}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
