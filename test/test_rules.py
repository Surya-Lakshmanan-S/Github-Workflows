import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rules.rule_pr_title import check
from runner import run_all_rules


def make_pr(title):
    return {"title": title, "number": 1, "author": "test-user"}


class TestPRTitleRule:

    def test_feat_title(self):
        result = check(make_pr("feat: add login page"))
        assert result["passed"] is True

    def test_fix_title(self):
        result = check(make_pr("fix: resolve null pointer"))
        assert result["passed"] is True

    def test_no_type_prefix(self):
        result = check(make_pr("Added login page"))
        assert result["passed"] is False

    def test_wip_title(self):
        result = check(make_pr("WIP"))
        assert result["passed"] is False

    def test_empty_title(self):
        result = check(make_pr(""))
        assert result["passed"] is False


class TestRunner:

    def test_runner_passes_valid_pr(self):
        pr = make_pr("feat: wire rule engine into workflow")
        output = run_all_rules(pr)
        assert output["passed"] is True

    def test_runner_fails_invalid_pr(self):
        pr = make_pr("fixed the bug")
        output = run_all_rules(pr)
        assert output["passed"] is False
