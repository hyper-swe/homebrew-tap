#!/usr/bin/env python3
"""update_hyperswe_formula.py <formula> <tag> <checksums.txt>

Rewrite Formula/hyperswe.rb for release <tag> from that release's signed
checksums.txt. It writes nothing unless the formula is in the supported shape:
four url lines, each followed by its sha256 line, naming exactly
hyperswe-darwin-arm64 once, hyperswe-linux-amd64 once and checksums.txt twice
(the two platforms with no build carry the manifest as a placeholder), a
single version line, and the platform-guarded disable! line, each url inside
its own platform block. Every line must be blank, a whole-line comment or one
of a fixed set of shapes (each end at its opener's indent), or the formula is
refused. A binary's sha256
comes from checksums.txt; the placeholder's is the sha256 of checksums.txt
itself. A tag older than the formula's version is refused.

Exit codes: 0 written (or already current), 1 refused with the reason on
stderr and nothing written, 2 a usage error.
"""
import hashlib
import re
import sys

BASE = "https://github.com/hyper-swe/releases/releases/download/"
URL = re.compile(r'^(\s*url ")' + re.escape(BASE) + r'v([0-9][^/"]*)/([^/"]+)(")$')
SHA = re.compile(r'^(\s*sha256 ")([0-9a-f]*)(")$')
VERSION = re.compile(r'^(\s*version ")([^"]*)(")$')
GUARD = ('  if (OS.mac? && Hardware::CPU.intel?) || (OS.linux? && Hardware::CPU.arm?)\n'
         '    disable! date: "')
TAG = re.compile(r'^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$')
WANT = {"hyperswe-darwin-arm64": 1, "hyperswe-linux-amd64": 1, "checksums.txt": 2}
# which asset each platform stanza may name: the two platforms with a build
# carry that platform's binary, the other two carry the manifest placeholder
PLACE = {
    ("macos", "arm"): "hyperswe-darwin-arm64",
    ("macos", "intel"): "checksums.txt",
    ("linux", "arm"): "checksums.txt",
    ("linux", "intel"): "hyperswe-linux-amd64",
}
# The formula is read as whole lines from a fixed set of shapes, never lexed as
# Ruby: a line that is not blank, not a whole-line comment and not one of the
# shapes below is refused, so syntax the updater would misread (a character
# literal, a semicolon, a trailing comment) cannot hide a block change. Each
# "end" must close the block opened at its own indent.
OPENERS = [
    (re.compile(r"^class [A-Z][A-Za-z0-9]* < Formula$"), "class"),
    (re.compile(r"^  on_(macos|linux) do$"), "os"),
    (re.compile(r"^    on_(arm|intel) do$"), "cpu"),
    (re.compile(r"^  def install$"), "def"),
    (re.compile(r"^  test do$"), "test"),
    (re.compile(r"^  if \(OS\.mac\? && Hardware::CPU\.intel\?\) \|\| \(OS\.linux\? && Hardware::CPU\.arm\?\)$"), "if"),
]
CLOSER = re.compile(r"^( *)end$")
KNOWN = [re.compile(r) for r in (
    r'^  desc "[^"\\]*"$',
    r'^  homepage "[^"\\]*"$',
    r'^  version "[^"\\]*"$',
    r'^    depends_on arch: :(arm64|x86_64)$',
    r'^      url "[^"\\]*"$',
    r'^      sha256 "[0-9a-f]*"$',
    r'^    disable! date: "[0-9-]+", because: "[^"\\]*"$',
    r'^    binary = Dir\["hyperswe-\*"\]\.first$',
    r'^    bin\.install binary => "hyperswe"$',
    r'^    assert_match "v#\{version\}", shell_output\("#\{bin\}/hyperswe --version"\)$',
)]


class Refused(Exception):
    pass


def parse_checksums(text):
    sums = {}
    for line in text.split("\n"):
        f = line.split()
        if len(f) == 2 and re.fullmatch(r"[0-9a-f]{64}", f[0]):
            sums[f[1].lstrip("*")] = f[0]
    return sums


def version_key(v):
    core, _, pre = v.partition("-")
    nums = tuple(int(x) for x in core.split("."))
    # no prerelease sorts after any prerelease of the same core
    parts = tuple((0, int(p)) if p.isdigit() else (1, p) for p in re.split(r"[-.]|(?<=[a-z])(?=\d)", pre) if p) if pre else ((9, 0),)
    return nums, parts


def rewrite(formula, tag, checksums):
    if not TAG.match(tag):
        raise Refused("tag %r does not look like vX.Y.Z" % tag)
    new = tag[1:]
    sums = parse_checksums(checksums)
    manifest = hashlib.sha256(checksums.encode()).hexdigest()
    lines = formula.split("\n")
    versions = [i for i, l in enumerate(lines) if VERSION.match(l)]
    if len(versions) != 1:
        raise Refused("expected one version line, found %d" % len(versions))
    old = VERSION.match(lines[versions[0]]).group(2)
    try:
        if version_key(new) < version_key(old):
            raise Refused("release %s is older than the formula's %s" % (new, old))
    except ValueError:
        raise Refused("cannot compare %s with %s" % (new, old))
    if GUARD not in formula:
        raise Refused("the platform-guarded disable! line is missing: the formula is not in the supported shape")
    seen = {}
    stanzas = {}
    out = list(lines)
    stack = []  # (kind, indent, which)
    for i, l in enumerate(lines):
        if l.strip() and not l.lstrip().startswith("#"):
            for rx, kind in OPENERS:
                mo = rx.match(l)
                if mo:
                    stack.append((kind, len(l) - len(l.lstrip()), mo.group(1) if mo.groups() else None))
                    break
            else:
                mc = CLOSER.match(l)
                if mc:
                    if not stack or stack[-1][1] != len(mc.group(1)):
                        raise Refused("line %d closes a block at the wrong depth" % (i + 1))
                    stack.pop()
                elif not any(rx.match(l) for rx in KNOWN):
                    raise Refused("line %d is not a line the updater knows: %s" % (i + 1, l.strip()))
        cur_os = next((w for k, _, w in reversed(stack) if k == "os"), None)
        cur_cpu = next((w for k, _, w in reversed(stack) if k == "cpu"), None)
        m = URL.match(l)
        if not m:
            if re.match(r'^\s*url "', l):
                raise Refused("url line outside the release download path: %s" % l.strip())
            continue
        asset = m.group(3)
        if asset not in WANT:
            raise Refused("url names %s, which the release does not build for this formula" % asset)
        if i + 1 >= len(lines) or not SHA.match(lines[i + 1]):
            raise Refused("the url line for %s is not followed by its sha256 line" % asset)
        where = (cur_os, cur_cpu)
        if PLACE.get(where) != asset:
            raise Refused("url for %s sits in the %s stanza, which must name %s" % (asset, "/".join(str(x) for x in where), PLACE.get(where)))
        stanzas[where] = stanzas.get(where, 0) + 1
        seen[asset] = seen.get(asset, 0) + 1
        if asset == "checksums.txt":
            digest = manifest
        elif asset in sums:
            digest = sums[asset]
        else:
            raise Refused("checksums.txt has no line for %s" % asset)
        out[i] = m.group(1) + BASE + "v" + new + "/" + asset + m.group(4)
        s = SHA.match(lines[i + 1])
        out[i + 1] = s.group(1) + digest + s.group(3)
    if stack:
        raise Refused("the formula ends with %d block(s) still open" % len(stack))
    if seen != WANT:
        raise Refused("expected urls %s, found %s" % (WANT, seen))
    if stanzas != {k: 1 for k in PLACE}:
        raise Refused("expected one url in each of the four platform stanzas, found %s" % stanzas)
    out[versions[0]] = VERSION.match(lines[versions[0]]).group(1) + new + '"'
    return "\n".join(out), old, new


def main(argv):
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    path, tag, sums_path = argv[1:]
    with open(path) as fh:
        formula = fh.read()
    with open(sums_path) as fh:
        checksums = fh.read()
    try:
        text, old, new = rewrite(formula, tag, checksums)
    except Refused as why:
        print("refusing: %s; nothing written" % why, file=sys.stderr)
        return 1
    if text == formula:
        print("already at %s" % new)
        return 0
    with open(path, "w") as fh:
        fh.write(text)
    print("updated %s to %s" % (old, new))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
