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

    def test_a_count_preserving_swap_of_the_two_binaries_is_refused(self):
        # each binary under the other platform: the asset counts still match
        # WANT, so only the stanza check can refuse it
        mac, lin = "/v0.2.0-beta-rc3/hyperswe-darwin-arm64", "/v0.2.0-beta-rc3/hyperswe-linux-amd64"
        swapped = FORMULA.replace(mac, "/@@MAC@@").replace(lin, mac).replace("/@@MAC@@", lin)
        self.assertNotEqual(swapped, FORMULA)
        with self.assertRaises(u.Refused):
            u.rewrite(swapped, "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_count_preserving_swap_of_a_binary_and_the_manifest_is_refused(self):
        # the Apple silicon stanza and the Intel macOS stanza trade assets
        mac = "/v0.2.0-beta-rc3/hyperswe-darwin-arm64"
        man = "/v0.2.0-beta-rc3/checksums.txt"
        lines = FORMULA.split("\n")
        i = next(n for n, l in enumerate(lines) if mac in l)
        j = next(n for n, l in enumerate(lines) if man in l)
        self.assertLess(i, j)
        lines[i], lines[j] = lines[i].replace(mac, man), lines[j].replace(man, mac)
        with self.assertRaises(u.Refused):
            u.rewrite("\n".join(lines), "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_platform_stanza_with_no_url_and_another_with_two_is_refused(self):
        # every url is in a stanza that may name its asset and the counts match
        # WANT, but the manifest sits twice under macOS Intel and never under
        # Linux ARM: only the one-url-per-stanza rule can refuse it
        import re
        intel = re.search(r"    on_intel do\n      url \"[^\"]*/checksums\.txt\"\n      sha256 \"[0-9a-f]*\"\n    end\n", FORMULA).group(0)
        arm = re.search(r"    on_arm do\n      url \"[^\"]*/checksums\.txt\"\n      sha256 \"[0-9a-f]*\"\n    end\n", FORMULA).group(0)
        moved = FORMULA.replace(arm, "", 1).replace(intel, intel + intel, 1)
        self.assertNotEqual(moved, FORMULA)
        with self.assertRaises(u.Refused):
            u.rewrite(moved, "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_pair_moved_below_both_platform_ends_is_refused(self):
        # the last Linux Intel url/sha256 pair moves out of its stanza to below
        # the closing lines of the Intel block and of on_linux: every count
        # still matches, so only closing the platform context at each end
        # can refuse it
        lin = "/v0.2.0-beta-rc3/hyperswe-linux-amd64"
        lines = FORMULA.split("\n")
        i = max(n for n, l in enumerate(lines) if lin in l and l.lstrip().startswith("url"))
        pair = lines[i:i + 2]
        del lines[i:i + 2]
        j = next(n for n, l in enumerate(lines) if l.startswith("  def install"))
        lines[j - 1:j - 1] = pair
        moved = "\n".join(lines)
        self.assertNotEqual(moved, FORMULA)
        with self.assertRaises(u.Refused):
            u.rewrite(moved, "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_pair_moved_below_its_own_cpu_end_is_refused(self):
        # same move, but only past the Intel block's end, still inside on_linux
        lin = "/v0.2.0-beta-rc3/hyperswe-linux-amd64"
        lines = FORMULA.split("\n")
        i = max(n for n, l in enumerate(lines) if lin in l and l.lstrip().startswith("url"))
        pair = lines[i:i + 2]
        del lines[i:i + 2]
        # lines[i] is now the Intel block's "    end"; put the pair after it
        self.assertEqual(lines[i], "    end")
        lines[i + 1:i + 1] = pair
        moved = "\n".join(lines)
        self.assertNotEqual(moved, FORMULA)
        with self.assertRaises(u.Refused):
            u.rewrite(moved, "v0.2.0-beta-rc4", NEW_SUMS)

    def _pair_below_ends(self, cpu_end, os_end):
        # the last Linux Intel url/sha256 pair moves to class level, below both
        # closing lines, which are rewritten as given
        lin = "/v0.2.0-beta-rc3/hyperswe-linux-amd64"
        lines = FORMULA.split("\n")
        i = max(n for n, l in enumerate(lines) if lin in l and l.lstrip().startswith("url"))
        pair = lines[i:i + 2]
        del lines[i:i + 2]
        self.assertEqual(lines[i], "    end")
        self.assertEqual(lines[i + 1], "  end")
        lines[i], lines[i + 1] = cpu_end, os_end
        lines[i + 2:i + 2] = [l.strip().join(["  ", ""]) for l in pair]
        return "\n".join(lines)

    def test_a_commented_end_is_refused_not_ignored(self):
        # valid Ruby, and the pair now sits at class level: a closing line with
        # a trailing comment must not leave the platform context open
        moved = self._pair_below_ends("    end # on_intel", "  end # on_linux")
        with self.assertRaises(u.Refused):
            u.rewrite(moved, "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_commented_end_in_place_is_refused(self):
        for old, new in (("    end\n    on_intel do", "    end # arm\n    on_intel do"),
                         ("    on_intel do", "    on_intel do # intel"),
                         ("  on_linux do", "  on_linux do # linux")):
            self.assertIn(old, FORMULA)
            with self.assertRaises(u.Refused, msg=new):
                u.rewrite(FORMULA.replace(old, new, 1), "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_closing_line_at_the_wrong_depth_or_an_unclosed_block_is_refused(self):
        with self.assertRaises(u.Refused):
            u.rewrite(FORMULA.replace("\n    end\n    on_intel do", "\n  end\n    on_intel do", 1), "v0.2.0-beta-rc4", NEW_SUMS)
        with self.assertRaises(u.Refused):
            u.rewrite(FORMULA.rstrip("\n").rsplit("\n", 1)[0] + "\n", "v0.2.0-beta-rc4", NEW_SUMS)

    def test_an_unread_structural_line_is_refused_even_when_blocks_stay_balanced(self):
        # a modifier "if" opens no block and closes none, so only the rule that
        # every block-structure line be a known form can refuse it
        odd = FORMULA.replace("  def install\n", '  def install\n    odie "no" if OS.mac?\n', 1)
        self.assertNotEqual(odd, FORMULA)
        with self.assertRaises(u.Refused):
            u.rewrite(odd, "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_line_that_hides_a_block_change_in_ruby_syntax_is_refused(self):
        # a character literal ?" and semicolons: Ruby reads this as closing the
        # Intel block and opening the arm block, so the pair after it would sit
        # in the wrong stanza; only refusing every line shape the formula is
        # not made of can catch what a lexer would misread
        L = FORMULA.split("\n")
        k = max(n for n, l in enumerate(L) if l == "    on_intel do")
        L[k + 1:k + 1] = ['      a = ?" ; end ; on_arm do ; b = ?"']
        with self.assertRaises(u.Refused):
            u.rewrite("\n".join(L), "v0.2.0-beta-rc4", NEW_SUMS)

    def test_a_whole_line_comment_may_carry_block_words(self):
        # the comment skip is what lets the formula's own explanatory comments
        # say "end" and "do"; it is the only way such a line is let through
        L = FORMULA.split("\n")
        k = next(n for n, l in enumerate(L) if l == "  on_macos do")
        L[k:k] = ["  # an end to do: if this end is read as structure the formula is refused"]
        text, _, _ = u.rewrite("\n".join(L), "v0.2.0-beta-rc4", NEW_SUMS)
        self.assertIn("# an end to do", text)

    def test_any_other_line_shape_is_refused(self):
        for extra in ('    depends_on macos: :ventura', '  livecheck do', '    puts "x"',
                      '  license "MIT"', '      sha256 "abc" # note'):
            L = FORMULA.split("\n")
            k = next(n for n, l in enumerate(L) if l == "  def install")
            L[k:k] = [extra]
            with self.assertRaises(u.Refused, msg=extra):
                u.rewrite("\n".join(L), "v0.2.0-beta-rc4", NEW_SUMS)

    def test_words_in_strings_and_comments_do_not_refuse_a_supported_formula(self):
        words = FORMULA.replace('desc "', 'desc "Runs agents to do work until the end of if ', 1)
        self.assertNotEqual(words, FORMULA)
        text, _, _ = u.rewrite(words, "v0.2.0-beta-rc4", NEW_SUMS)
        self.assertIn("v0.2.0-beta-rc4", text)

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
        # whole-line comparison: a condition with anything added to it, such as
        # "&& false", is a different line and fails
        _, steps = self.steps()
        found = 0
        for name, body in steps:
            if name.startswith("Audit") or name == "Commit and push":
                found += 1
                self.assertIn("\n        if: env.CURRENT != 'yes'\n", body, name)
                self.assertEqual([l for l in body.split("\n") if l.strip().startswith("if:")],
                                 ["        if: env.CURRENT != 'yes'"], name)
        self.assertEqual(found, 2)

    def test_the_audit_step_is_exactly_the_reviewed_commands(self):
        # the whole run block, line for line: nothing may be added after a
        # command (|| echo, ; true, a redirect) or between them
        _, steps = self.steps()
        body = [b for n, b in steps if n.startswith("Audit")][0]
        run = body.split("        run: |\n", 1)[1].rstrip("\n").split("\n")
        want = [
            "          set -euo pipefail",
            '          eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"',
            '          taps="$(brew --repository)/Library/Taps/hyper-swe"',
            '          mkdir -p "$taps"',
            '          ln -sfn "$GITHUB_WORKSPACE" "$taps/homebrew-tap"',
            "          brew trust hyper-swe/tap || true   # a brew without the command has no trust step",
            "          brew style hyper-swe/tap/hyperswe",
            "          brew audit --strict --formula hyper-swe/tap/hyperswe",
        ]
        self.assertEqual([l for l in run if l.strip()], want)
        # and no step key that changes what a failure does
        for key in ("continue-on-error", "timeout-minutes", "shell:"):
            self.assertNotIn(key, body)


if __name__ == "__main__":
    unittest.main()
