"""Tests for formula_shas.py and for the release update's use of it.

The release's checksums.txt lists more than the four archives a formula
installs: since mgit 0.7.7 it also lists a libkrunfw archive for the same
platform. Picking a digest by a substring of the platform name then returns two
digests for darwin arm64, and the formula's sha256 holds both.
"""
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "testdata")
SCRIPT = os.path.join(HERE, "formula_shas.py")
WORKFLOW = os.path.join(HERE, "..", "workflows", "update-formula.yml")

ARM = "e175efaff33ea88f002952e922bb8e0eff606a8a38baa2f8d5d16ccbc4c76d06"
AMD = "2acd1f6c35b2d8cdced58824d5a5446dbbc32f0426e61aab054b7d9899f1bc28"
LARM = "3c2658e9173aac32828b4ca7d276be92ec2378eff5c9bfbe7a22ecefd08ade42"
LAMD = "40aeaef9c194d9e45df580f4b4f93166549019dbefcbdf43111e2be77145bd75"


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)


class PickTests(unittest.TestCase):
    def test_each_platform_gets_exactly_its_own_archive_digest(self):
        r = run("pick", os.path.join(DATA, "checksums.mgit-0.7.7.txt"), "mgit", "0.7.7")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split(), [ARM, AMD, LARM, LAMD])

    def test_a_second_archive_for_the_same_platform_is_not_picked(self):
        # libkrunfw_5.5.0_darwin_arm64.tar.gz sits in the same file and shares
        # the platform text; the digest must be the mgit archive's alone.
        r = run("pick", os.path.join(DATA, "checksums.mgit-0.7.7.txt"), "mgit", "0.7.7")
        self.assertNotIn("46958b74", r.stdout)
        self.assertEqual(len(r.stdout.split()), 4)

    def test_a_missing_archive_is_refused(self):
        r = run("pick", os.path.join(DATA, "checksums.mgit-0.7.7.txt"), "mgit", "0.7.8")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_a_listed_archive_twice_is_refused(self):
        dup = os.path.join(DATA, "checksums.duplicate.txt")
        with open(os.path.join(DATA, "checksums.mgit-0.7.7.txt")) as fh:
            body = fh.read()
        with open(dup, "w") as fh:
            fh.write(body + "0" * 64 + "  mgit_0.7.7_darwin_arm64.tar.gz\n")
        try:
            r = run("pick", dup, "mgit", "0.7.7")
        finally:
            os.remove(dup)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")


class CheckTests(unittest.TestCase):
    def test_a_formula_with_one_digest_per_literal_passes(self):
        r = run("check", os.path.join(DATA, "mgit.good.rb"))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_literal_holding_two_digests_fails_and_names_the_line(self):
        r = run("check", os.path.join(DATA, "mgit.two-digests.rb"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("line 42", r.stderr)

    def test_a_formula_with_no_sha256_literal_fails(self):
        empty = os.path.join(DATA, "mgit.empty.rb")
        with open(empty, "w") as fh:
            fh.write("class Mgit < Formula\nend\n")
        try:
            r = run("check", empty)
        finally:
            os.remove(empty)
        self.assertNotEqual(r.returncode, 0)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        with open(WORKFLOW) as fh:
            self.text = fh.read()

    def test_the_update_picks_digests_with_the_script(self):
        self.assertIn("formula_shas.py pick", self.text)

    def test_the_update_no_longer_picks_by_substring(self):
        self.assertNotIn('grep "$1" checksums.txt', self.text)

    def test_the_update_checks_the_formula_before_it_commits(self):
        check = self.text.find("formula_shas.py check")
        push = self.text.find("name: Commit and push")
        self.assertGreater(check, 0)
        self.assertGreater(push, check)


if __name__ == "__main__":
    unittest.main()
