import hashlib
import json
import os
import shutil
import tempfile
import unittest

import retag_bottle as r

NAME, VER = "libkrunfw", "5.5.0"
FULL = "hyper-swe/tap/libkrunfw"


def fixture(dirpath, tag="arm64_sequoia", payload=b"bottle bytes", rebuild=0):
    suffix = ".bottle.tar.gz" if rebuild == 0 else ".bottle.%d.tar.gz" % rebuild
    fname = "%s--%s.%s%s" % (NAME, VER, tag, suffix)
    with open(os.path.join(dirpath, fname), "wb") as fh:
        fh.write(payload)
    doc = {FULL: {
        "formula": {"name": NAME, "pkg_version": VER},
        "bottle": {"root_url": "https://example.invalid", "cellar": ":any", "rebuild": rebuild,
                   "tags": {tag: {"filename": fname.replace("--", "-", 1), "local_filename": fname,
                                   "sha256": hashlib.sha256(payload).hexdigest(),
                                   "tab": {"built_on": {"os": "macOS 26"}}, "all_files": ["lib/libkrunfw.5.dylib"]}}},
    }}
    with open(os.path.join(dirpath, fname.replace(".tar.gz", ".json")), "w") as fh:
        json.dump(doc, fh)
    return fname


class Retag(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        for root, dirs, files in os.walk(self.d, topdown=False):
            for f in files:
                os.unlink(os.path.join(root, f))
            for dd in dirs:
                os.rmdir(os.path.join(root, dd))
        os.rmdir(self.d)

    def test_the_retagged_artifact_has_the_new_tag_in_its_name_and_its_json_and_the_same_bytes(self):
        src = fixture(self.d)
        r.retag(self.d, "arm64_sequoia", "arm64_sonoma")
        new = src.replace("arm64_sequoia", "arm64_sonoma")
        self.assertTrue(os.path.exists(os.path.join(self.d, new)))
        with open(os.path.join(self.d, src), "rb") as a, open(os.path.join(self.d, new), "rb") as b:
            self.assertEqual(a.read(), b.read())
        with open(os.path.join(self.d, new.replace(".tar.gz", ".json"))) as fh:
            doc = json.load(fh)
        tags = doc[FULL]["bottle"]["tags"]
        self.assertEqual(list(tags), ["arm64_sonoma"])
        # brew writes the url-encoded name (one dash after the formula name) in "filename"
        self.assertEqual(tags["arm64_sonoma"]["filename"], new.replace("--", "-", 1))
        self.assertEqual(tags["arm64_sonoma"]["local_filename"], new)
        self.assertEqual(tags["arm64_sonoma"]["tab"], {"built_on": {"os": "macOS 26"}})
        r.verify(self.d, "arm64_sonoma")

    def test_the_source_artifact_is_left_as_it_was(self):
        src = fixture(self.d)
        with open(os.path.join(self.d, src), "rb") as fh:
            before = fh.read()
        r.retag(self.d, "arm64_sequoia", "arm64_sonoma")
        with open(os.path.join(self.d, src), "rb") as fh:
            self.assertEqual(fh.read(), before)
        r.verify(self.d, "arm64_sequoia")

    def test_a_rebuild_number_is_kept_in_the_name(self):
        src = fixture(self.d, rebuild=2)
        r.retag(self.d, "arm64_sequoia", "arm64_sonoma")
        self.assertTrue(os.path.exists(os.path.join(self.d, src.replace("arm64_sequoia", "arm64_sonoma"))))

    def test_verify_refuses_a_name_json_or_digest_that_disagree(self):
        src = fixture(self.d)
        r.retag(self.d, "arm64_sequoia", "arm64_sonoma")
        new = src.replace("arm64_sequoia", "arm64_sonoma")
        jpath = os.path.join(self.d, new.replace(".tar.gz", ".json"))
        with open(jpath) as fh:
            good = fh.read()
        # the tarball bytes change after the json was written
        with open(os.path.join(self.d, new), "ab") as fh:
            fh.write(b"x")
        with self.assertRaises(r.Refused):
            r.verify(self.d, "arm64_sonoma")
        shutil.copyfile(os.path.join(self.d, src), os.path.join(self.d, new))
        r.verify(self.d, "arm64_sonoma")
        # the json names the other tag's file
        doc = json.loads(good)
        doc[FULL]["bottle"]["tags"]["arm64_sonoma"]["local_filename"] = src
        with open(jpath, "w") as fh:
            fh.write(json.dumps(doc))
        with self.assertRaises(r.Refused):
            r.verify(self.d, "arm64_sonoma")
        # the json carries a tag the file name does not
        doc = json.loads(good)
        doc[FULL]["bottle"]["tags"] = {"arm64_sequoia": doc[FULL]["bottle"]["tags"]["arm64_sonoma"]}
        open(jpath, "w").write(json.dumps(doc))
        with self.assertRaises(r.Refused):
            r.verify(self.d, "arm64_sonoma")

    def test_retag_refuses_bad_input(self):
        src = fixture(self.d)
        with self.assertRaises(r.Refused):
            r.retag(self.d, "arm64_sequoia", "arm64_sequoia")      # same tag
        with self.assertRaises(r.Refused):
            r.retag(self.d, "arm64_ventura", "arm64_sonoma")       # no such source
        r.retag(self.d, "arm64_sequoia", "arm64_sonoma")
        with self.assertRaises(r.Refused):
            r.retag(self.d, "arm64_sequoia", "arm64_sonoma")       # destination exists
        # a source whose json digest does not match its file
        d2 = tempfile.mkdtemp()
        try:
            fixture(d2)
            with open(os.path.join(d2, src), "ab") as fh:
                fh.write(b"x")
            with self.assertRaises(r.Refused):
                r.retag(d2, "arm64_sequoia", "arm64_sonoma")
            # refused before anything was written: no half-made destination is left behind
            self.assertEqual([f for f in os.listdir(d2) if "arm64_sonoma" in f], [])
        finally:
            for f in os.listdir(d2):
                os.unlink(os.path.join(d2, f))
            os.rmdir(d2)


if __name__ == "__main__":
    unittest.main()
