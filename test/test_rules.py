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
        result = check(make_pr("fix: resolve null pointer on signup"))
        assert result["passed"] is True

    def test_fix_with_scope(self):
        result = check(make_pr("fix(auth): handle expired tokens"))
        assert result["passed"] is True

    def test_chore_title(self):
        result = check(make_pr("chore: update dependencies"))
        assert result["passed"] is True

    def test_docs_title(self):
        result = check(make_pr("docs: update README with setup steps"))
        assert result["passed"] is True

    def test_ci_title(self):
        result = check(make_pr("ci: add pr rule engine workflow"))
        assert result["passed"] is True

    def test_uppercase_type(self):
        result = check(make_pr("FEAT: add dark mode"))
        assert result["passed"] is True

    def test_no_type_prefix(self):
        result = check(make_pr("Added login page"))
        assert result["passed"] is False

    def test_wip_title(self):
        result = check(make_pr("WIP"))
        assert result["passed"] is False

    def test_missing_space_after_colon(self):
        result = check(make_pr("feat:add login"))
        assert result["passed"] is False

    def test_empty_title(self):
        result = check(make_pr(""))
        assert result["passed"] is False

    def test_invalid_type(self):
        result = check(make_pr("update: change button color"))
        assert result["passed"] is False

    def test_description_only_colon(self):
        result = check(make_pr("feat:"))
        assert result["passed"] is False


class TestRunner:

    def test_runner_passes_valid_pr(self):
        pr = make_pr("feat: wire rule engine into workflow")
        output = run_all_rules(pr)
        assert output["passed"] is True
        assert len(output["results"]) == 1

    def test_runner_fails_invalid_pr(self):
        pr = make_pr("fixed the bug")
        output = run_all_rules(pr)
        assert output["passed"] is False

    def test_runner_output_shape(self):
        pr = make_pr("refactor: clean up runner logic")
        output = run_all_rules(pr)
        assert "passed" in output
        assert "results" in output
        result = output["results"][0]
        assert "rule" in result
        assert "passed" in result
        assert "message" in result

    def test_branch_name_passes(self):
        result = check(make_pr("paste a good example here"))
        assert result["passed"] is True

    def test_branch_name_fails(self):
        result = check(make_pr("paste a bad example here"))
        assert result["passed"] is False
