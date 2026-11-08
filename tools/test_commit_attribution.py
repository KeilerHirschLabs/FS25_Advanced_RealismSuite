#!/usr/bin/env python3
import subprocess
import unittest
from unittest.mock import patch
from check_commit_attribution import ambiguous_coauthors, audit


class AttributionTests(unittest.TestCase):
    def test_personal_noreply_is_valid(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: KeilerHirsch "
            "<259172531+KeilerHirsch@users.noreply.github.com>"), [])

    def test_generic_identity_rejected(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: KeilerHirsch <noreply@users.noreply.github.com>"),
            ["noreply@users.noreply.github.com"])

    def test_github_system_identity_rejected_as_coauthor(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: GitHub <noreply@github.com>"),
            ["noreply@github.com"])

    def test_system_committer_not_coauthor(self):
        self.assertEqual(ambiguous_coauthors(
            "committer GitHub <noreply@github.com>"), [])

    def test_casefold(self):
        self.assertEqual(ambiguous_coauthors(
            " CO-AUTHORED-BY: Person <NoReply@Users.NoReply.GitHub.Com> "),
            ["noreply@users.noreply.github.com"])

    def test_legitimate_person(self):
        self.assertEqual(ambiguous_coauthors(
            "Co-authored-by: Pat <pat@example.net>"), [])

    def test_plain_prose_does_not_trigger(self):
        self.assertEqual(ambiguous_coauthors(
            "An older commit said Co-authored-by: "
            "KeilerHirsch <noreply@users.noreply.github.com>."), [])


    @patch("check_commit_attribution.git")
    def test_merge_commit_coauthor_is_scanned(self, mocked_git):
        def fake_git(*args):
            if args[0] == "cat-file":
                return ""
            if args[0] == "rev-list":
                self.assertEqual(args, ("rev-list", "a" * 40 + ".." + "b" * 40))
                return "c673ee83e0a2"
            if args[0] == "log":
                if "--format=%B" in args:
                    return "Co-authored-by: KeilerHirsch <noreply@users.noreply.github.com>"
                return "259172531+KeilerHirsch@users.noreply.github.com"
            raise AssertionError(args)
        mocked_git.side_effect = fake_git
        violations, scanned = audit("push", {
            "before": "a" * 40, "after": "b" * 40})
        self.assertEqual(scanned, 1)
        self.assertEqual(violations, [
            ("c673ee83e0a2", ["noreply@users.noreply.github.com"])])

    @patch("check_commit_attribution.git")
    def test_generic_author_rejected_but_github_web_committer_allowed(self, mocked_git):
        def fake_git(*args):
            if args[0] == "cat-file":
                return ""
            if args[0] == "rev-list":
                return "abcde12345"
            if args[0] == "log":
                if "--format=%ae" in args:
                    return "noreply@users.noreply.github.com"
                if "--format=%ce" in args:
                    return "noreply@github.com"
                return "Normal commit message"
            raise AssertionError(args)
        mocked_git.side_effect = fake_git
        violations, scanned = audit("push", {
            "before": "a" * 40, "after": "b" * 40})
        self.assertEqual(scanned, 1)
        self.assertEqual(violations, [
            ("abcde12345", ["author: noreply@users.noreply.github.com"])])

    @patch("check_commit_attribution.git")
    def test_github_system_address_rejected_for_author_only(self, mocked_git):
        def fake_git(*args):
            if args[0] == "cat-file":
                return ""
            if args[0] == "rev-list":
                return "abcde12345"
            if args[0] == "log":
                if "--format=%ae" in args or "--format=%ce" in args:
                    return "noreply@github.com"
                return "Normal commit message"
            raise AssertionError(args)
        mocked_git.side_effect = fake_git
        violations, scanned = audit("push", {
            "before": "a" * 40, "after": "b" * 40})
        self.assertEqual(scanned, 1)
        self.assertEqual(violations, [
            ("abcde12345", ["author: noreply@github.com"])])

    @patch("check_commit_attribution.git")
    def test_normal_web_flow_committer_is_not_mistaken_for_foreign_user(self, mocked_git):
        def fake_git(*args):
            if args[0] == "cat-file":
                return ""
            if args[0] == "rev-list":
                return "abcde12345"
            if args[0] == "log":
                if "--format=%ae" in args:
                    return "259172531+KeilerHirsch@users.noreply.github.com"
                if "--format=%ce" in args:
                    return "noreply@github.com"
                return "Normal commit message"
            raise AssertionError(args)
        mocked_git.side_effect = fake_git
        violations, scanned = audit("push", {
            "before": "a" * 40, "after": "b" * 40})
        self.assertEqual((violations, scanned), ([], 1))

    @patch("check_commit_attribution.git")
    def test_history_rewrite_scans_entire_new_history(self, mocked_git):
        def fake_git(*args):
            if args[0] == "cat-file":
                raise subprocess.CalledProcessError(128, args)
            if args[0] == "rev-list":
                self.assertEqual(args[-1], "b" * 40)
                return "abcde12345"
            if args[0] == "log":
                return "Co-authored-by: Bad <noreply@users.noreply.github.com>"
            raise AssertionError(args)
        mocked_git.side_effect = fake_git
        violations, scanned = audit("push", {
            "before": "a" * 40, "after": "b" * 40})
        self.assertEqual(scanned, 1)
        self.assertEqual(violations, [(
            "abcde12345", ["noreply@users.noreply.github.com"])])

    @patch("check_commit_attribution.git")
    def test_normal_push_checks_only_delta(self, mocked_git):
        def fake_git(*args):
            if args[0] == "cat-file":
                return ""
            if args[0] == "rev-list":
                self.assertEqual(args[-1], "a" * 40 + ".." + "b" * 40)
                return "abcde12345"
            if args[0] == "log":
                return "Plain correctly attributed commit"
            raise AssertionError(args)
        mocked_git.side_effect = fake_git
        violations, scanned = audit("push", {
            "before": "a" * 40, "after": "b" * 40})
        self.assertEqual((violations, scanned), ([], 1))


if __name__ == "__main__":
    unittest.main()
