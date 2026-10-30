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

    def test_a_binary_url_under_the_wrong_platform_is_refused(self):
        # the Linux intel stanza names the Apple silicon binary: urls are
        # darwin-arm64 twice, linux-amd64 never, so the count rule must refuse
        swapped = FORMULA.replace(
            "/v0.2.0-beta-rc3/hyperswe-linux-amd64", "/v0.2.0-beta-rc3/hyperswe-darwin-arm64")
        self.assertNotEqual(swapped, FORMULA)
        with self.assertRaises(u.Refused):
            u.rewrite(swapped, "v0.2.0-beta-rc4", NEW_SUMS)
        # and the manifest placeholder under a binary's stanza likewise
        placeholder = FORMULA.replace(
            "/v0.2.0-beta-rc3/hyperswe-darwin-arm64", "/v0.2.0-beta-rc3/checksums.txt")
        with self.assertRaises(u.Refused):
            u.rewrite(placeholder, "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_stray_url_is_refused(self):
        bad = FORMULA.replace('url "https://github.com/hyper-swe/releases/releases/download/v0.2.0-beta-rc3/hyperswe-linux-amd64"',
                              'url "https://example.com/hyperswe-linux-amd64"')
        with self.assertRaises(u.Refused):
            u.rewrite(bad, "v0.2.0-beta-rc4", NEW_SUMS)


WORKFLOW = os.path.join(os.path.dirname(__file__), "..", "workflows", "hyperswe-formula.yml")


class Workflow(unittest.TestCase):
    """A GITHUB_TOKEN push starts no workflow, so the audit must run inside
    the updater job, before the push, and a failing audit must stop the job."""

    def steps(self):
        with open(WORKFLOW) as fh:
            text = fh.read()
        parts = text.split("      - name: ")[1:]
        return text, [(p.split("\n")[0], p) for p in parts]

    def test_the_audit_runs_before_the_push_and_blocks_it(self):
        text, steps = self.steps()
        names = [n for n, _ in steps]
        audit = [i for i, (n, _) in enumerate(steps) if n.startswith("Audit")]
        push = [i for i, n in enumerate(names) if n == "Commit and push"]
        rewrite = [i for i, n in enumerate(names) if n == "Rewrite the formula"]
        self.assertEqual((len(audit), len(push), len(rewrite)), (1, 1, 1))
        self.assertLess(rewrite[0], audit[0])
        self.assertLess(audit[0], push[0])
        body = steps[audit[0]][1]
        self.assertIn("brew style hyper-swe/tap/hyperswe", body)
        self.assertIn("brew audit --strict --formula hyper-swe/tap/hyperswe", body)
        self.assertIn("set -euo pipefail", body)
        self.assertNotIn("continue-on-error", text)
        self.assertNotIn("|| true", body.replace("brew trust hyper-swe/tap || true", ""))
        self.assertEqual(text.count("git push"), 1)
        self.assertGreater(text.index("git push"), text.index("brew audit --strict"))

    def test_the_audit_runs_exactly_when_the_push_does(self):
        _, steps = self.steps()
        cond = "if: env.CURRENT != 'yes'"
        for name, body in steps:
            if name.startswith("Audit") or name == "Commit and push":
                self.assertIn(cond, body, name)


if __name__ == "__main__":
    unittest.main()
