#!/usr/bin/env python3
"""formula_shas.py pick <checksums.txt> <project> <version>
formula_shas.py check <formula>

pick prints the four digests a formula installs, one per line, in formula
order: darwin arm64, darwin amd64, linux arm64, linux amd64. Each is the digest
of exactly one archive, named <project>_<version>_<os>_<arch>.tar.gz. A release's
checksums.txt lists other files too (a libkrunfw archive for darwin arm64, source
tarballs), so a digest is never picked by part of a name. An archive that is
missing, or listed more than once, prints nothing and exits 1.

check reads a formula and requires every `sha256 "..."` literal to be one
64-character hex digest, and at least one literal to exist. A violation names
the line and exits 1.

Exit codes: 0 done, 1 a refusal (nothing printed on stdout for pick), 2 usage.
"""
import re
import sys

PLATFORMS = ("darwin_arm64", "darwin_amd64", "linux_arm64", "linux_amd64")
HEX64 = re.compile(r"[0-9a-f]{64}")
LITERAL = re.compile(r'sha256 "([^"]*)"')
LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def pick(path, project, version):
    if not re.fullmatch(r"[a-z][a-z0-9-]*", project) or not re.fullmatch(r"[0-9][0-9A-Za-z.\-]*", version):
        print(f"refusing: '{project}' or '{version}' is not a project and a version", file=sys.stderr)
        return 1
    digests = {}
    with open(path) as fh:
        for raw in fh:
            m = LINE.match(raw.rstrip("\n"))
            if m:
                digests.setdefault(m.group(2), []).append(m.group(1))
    out = []
    for plat in PLATFORMS:
        name = f"{project}_{version}_{plat}.tar.gz"
        found = digests.get(name, [])
        if len(found) != 1:
            print(f"refusing: {name} is listed {len(found)} times in checksums.txt, want exactly 1", file=sys.stderr)
            return 1
        out.append(found[0])
    print("\n".join(out))
    return 0


def check(path):
    with open(path) as fh:
        lines = fh.read().split("\n")
    seen = 0
    bad = []
    for i, line in enumerate(lines, 1):
        # A literal that spans lines opens a quote and never closes it on this
        # line; count that as a violation too.
        if line.lstrip().startswith("#"):
            continue
        if re.search(r'sha256 "', line):
            seen += 1
            m = LITERAL.search(line)
            if not m or not HEX64.fullmatch(m.group(1)):
                bad.append(i)
    if seen == 0:
        print(f"refusing: {path} has no sha256 literal", file=sys.stderr)
        return 1
    if bad:
        print("refusing: a sha256 literal is not one 64-character hex digest at line " + ", line ".join(map(str, bad)), file=sys.stderr)
        return 1
    return 0


def main(argv):
    if len(argv) == 5 and argv[1] == "pick":
        return pick(argv[2], argv[3], argv[4])
    if len(argv) == 3 and argv[1] == "check":
        return check(argv[2])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
