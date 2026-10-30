import hashlib
import os
import unittest

import update_hyperswe_formula as u

HERE = os.path.join(os.path.dirname(__file__), "testdata")


def read(name):
    with open(os.path.join(HERE, name)) as fh:
        return fh.read()


FORMULA = read("hyperswe.rc3.rb")
SUMS = read("checksums.rc3.txt")
NEW_SUMS = (
    "1" * 64 + "  hyperswe-darwin-arm64\n"
    + "2" * 64 + "  hyperswe-linux-amd64\n"
    + "3" * 64 + "  install.sh\n"
)


class Rewrite(unittest.TestCase):
    def test_the_current_release_changes_nothing(self):
        text, old, new = u.rewrite(FORMULA, "v0.2.0-beta-rc3", SUMS)
        self.assertEqual(text, FORMULA)
        self.assertEqual((old, new), ("0.2.0-beta-rc3", "0.2.0-beta-rc3"))

    def test_a_new_release_changes_the_version_four_urls_and_four_digests_only(self):
        text, _, new = u.rewrite(FORMULA, "v0.2.0-beta-rc4", NEW_SUMS)
        self.assertEqual(new, "0.2.0-beta-rc4")
        manifest = hashlib.sha256(NEW_SUMS.encode()).hexdigest()
        a, b = FORMULA.split("\n"), text.split("\n")
        self.assertEqual(len(a), len(b))
        changed = [(x, y) for x, y in zip(a, b) if x != y]
        self.assertEqual(len(changed), 9)  # version + 4 urls + 4 digests
        self.assertIn('version "0.2.0-beta-rc4"', text)
        self.assertEqual(text.count("/download/v0.2.0-beta-rc4/"), 4)
        self.assertFalse([l for l in text.split("\n") if ("url " in l or "version " in l) and "rc3" in l])
        self.assertIn('sha256 "' + "1" * 64 + '"', text)
        self.assertIn('sha256 "' + "2" * 64 + '"', text)
        self.assertEqual(text.count('sha256 "' + manifest + '"'), 2)

    def test_the_guard_and_depends_on_survive(self):
        text, _, _ = u.rewrite(FORMULA, "v0.2.0-beta-rc4", NEW_SUMS)
        self.assertIn(u.GUARD, text)
        self.assertIn("depends_on arch: :arm64", text)
        self.assertIn("depends_on arch: :x86_64", text)

    def test_an_older_release_is_refused(self):
        with self.assertRaises(u.Refused):
            u.rewrite(FORMULA, "v0.2.0-beta-rc2", SUMS)

    def test_a_release_after_the_prerelease_series_is_newer(self):
        text, _, _ = u.rewrite(FORMULA, "v0.2.0", NEW_SUMS)
        self.assertIn('version "0.2.0"', text)

    def test_the_old_wrong_platform_shape_is_refused(self):
        with self.assertRaises(u.Refused):
            u.rewrite(read("hyperswe.rc2-wrong-arch.rb"), "v0.2.0-beta-rc3", SUMS)

    def test_a_formula_without_the_guard_is_refused(self):
        with self.assertRaises(u.Refused):
            u.rewrite(FORMULA.replace("disable!", "# disable!"), "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_missing_binary_line_is_refused(self):
        with self.assertRaises(u.Refused):
            u.rewrite(FORMULA, "v0.2.0-beta-rc4", "1" * 64 + "  hyperswe-darwin-arm64\n")

    def test_a_malformed_tag_is_refused(self):
        for tag in ("0.2.0", "v0.2", "v0.2.0 ; rm", "vx.y.z", ""):
            with self.assertRaises(u.Refused, msg=tag):
                u.rewrite(FORMULA, tag, SUMS)

    def test_a_stray_url_is_refused(self):
        bad = FORMULA.replace('url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3/hyperswe-linux-amd64"',
                              'url "https://example.com/hyperswe-linux-amd64"')
        with self.assertRaises(u.Refused):
            u.rewrite(bad, "v0.2.0-beta-rc4", NEW_SUMS)


if __name__ == "__main__":
    unittest.main()
