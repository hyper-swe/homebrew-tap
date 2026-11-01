#!/usr/bin/env python3
"""retag_bottle.py <dir> <from-tag> <to-tag>      copy a built bottle to another OS tag
retag_bottle.py --verify <dir> <tag>             check that a bottle's name, json and digest agree

brew bottle names a bottle after the OS of the runner that built it. retag copies the
bottle tarball to the other tag's file name (the bytes do not change, so the digest in the
json still holds) and writes a json for that tag alone, so a bottle built on a newer image
can be published for the older tag it was built to run on. The source files are untouched.
verify refuses a tarball whose name, json tag, json file names or sha256 disagree.
Exit codes: 0 done, 1 refused with the reason on stderr, 2 a usage error.
"""
import hashlib
import json
import os
import shutil
import sys


class Refused(Exception):
    pass


def _url_name(local):
    """brew writes the url-encoded file name, one dash after the formula name, in the json's filename."""
    return local.replace("--", "-", 1)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _find(dirpath, tag):
    """The one tarball tagged <tag> in dirpath and its json."""
    marker = ".%s.bottle." % tag
    tars = sorted(f for f in os.listdir(dirpath) if marker in f and f.endswith(".tar.gz"))
    if len(tars) != 1:
        raise Refused("expected one %s bottle in %s, found %d" % (tag, dirpath, len(tars)))
    return tars[0], tars[0][: -len(".tar.gz")] + ".json"


def _entry(doc, tag):
    if len(doc) != 1:
        raise Refused("the bottle json must describe exactly one formula")
    full = next(iter(doc))
    tags = doc[full].get("bottle", {}).get("tags", {})
    return full, tags


def verify(dirpath, tag):
    tar, js = _find(dirpath, tag)
    if not os.path.exists(os.path.join(dirpath, js)):
        raise Refused("%s has no json next to it" % tar)
    with open(os.path.join(dirpath, js)) as fh:
        doc = json.load(fh)
    full, tags = _entry(doc, tag)
    if list(tags) != [tag]:
        raise Refused("%s carries tags %s, want only %s" % (js, sorted(tags), tag))
    t = tags[tag]
    if t.get("local_filename") != tar:
        raise Refused("%s says local_filename is %r, but the file is %s" % (js, t.get("local_filename"), tar))
    if t.get("filename") not in (tar, _url_name(tar)):
        raise Refused("%s says filename is %r, which is neither the file %s nor its url-encoded form" % (js, t.get("filename"), tar))
    got = _sha(os.path.join(dirpath, tar))
    if t.get("sha256") != got:
        raise Refused("%s says sha256 %s, the file is %s" % (js, t.get("sha256"), got))


def retag(dirpath, src, dst):
    if src == dst:
        raise Refused("the source and destination tags are both %s" % src)
    tar, js = _find(dirpath, src)
    verify(dirpath, src)  # never retag a bottle that does not agree with itself
    new_tar = tar.replace(".%s.bottle." % src, ".%s.bottle." % dst)
    new_js = new_tar[: -len(".tar.gz")] + ".json"
    for f in (new_tar, new_js):
        if os.path.exists(os.path.join(dirpath, f)):
            raise Refused("%s already exists" % f)
    with open(os.path.join(dirpath, js)) as fh:
        doc = json.load(fh)
    full, tags = _entry(doc, src)
    entry = dict(tags[src])
    # keep the source json's convention: the url-encoded name when brew wrote that, else the file name
    entry["filename"] = _url_name(new_tar) if tags[src].get("filename") == _url_name(tar) and "--" in tar else new_tar
    entry["local_filename"] = new_tar
    doc[full]["bottle"]["tags"] = {dst: entry}
    shutil.copyfile(os.path.join(dirpath, tar), os.path.join(dirpath, new_tar))
    with open(os.path.join(dirpath, new_js), "w") as fh:
        json.dump(doc, fh, indent=2)
    verify(dirpath, dst)


def main(argv):
    try:
        if len(argv) == 4 and argv[1] == "--verify":
            verify(argv[2], argv[3])
            print("verified: %s bottle name, json and digest agree" % argv[3])
        elif len(argv) == 4 and not argv[1].startswith("-"):
            retag(argv[1], argv[2], argv[3])
            print("retagged %s -> %s" % (argv[2], argv[3]))
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except Refused as why:
        print("refusing: %s" % why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
