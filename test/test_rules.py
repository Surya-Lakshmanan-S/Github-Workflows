import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rules.rule_pr_title import check
from rules.rule_pr_size import check as check_size
from runner import run_all_rules


def make_pr(title, num_files=0):
    files = [{"filename": f"file_{i}.py", "content": ""} for i in range(num_files)]
    return {"title": title, "number": 1, "author": "test-user", "files": files}


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


class TestPRSizeRule:

    def test_no_files(self):
        result = check_size(make_pr("feat: empty", num_files=0))
        assert result["passed"] is True

    def test_small_pr(self):
        result = check_size(make_pr("feat: small", num_files=5))
        assert result["passed"] is True
        assert "✅" in result["message"]

    def test_exactly_at_warn_threshold(self):
        result = check_size(make_pr("feat: at limit", num_files=15))
        assert result["passed"] is True
        assert "✅" in result["message"]

    def test_warning_zone(self):
        result = check_size(make_pr("feat: medium", num_files=20))
        assert result["passed"] is True
        assert "⚠️" in result["message"]

    def test_exactly_at_fail_threshold(self):
        result = check_size(make_pr("feat: at fail", num_files=30))
        assert result["passed"] is True
        assert "⚠️" in result["message"]

    def test_too_large(self):
        result = check_size(make_pr("feat: huge", num_files=31))
        assert result["passed"] is False
        assert "❌" in result["message"]

    def test_very_large(self):
        result = check_size(make_pr("feat: massive", num_files=100))
        assert result["passed"] is False


class TestRunner:

    def test_runner_passes_valid_pr(self):
        pr = make_pr("feat: wire rule engine into workflow", num_files=3)
        output = run_all_rules(pr)
        assert output["passed"] is True

    def test_runner_fails_invalid_title(self):
        pr = make_pr("fixed the bug", num_files=3)
        output = run_all_rules(pr)
        assert output["passed"] is False

    def test_runner_fails_too_many_files(self):
        pr = make_pr("feat: refactor everything", num_files=50)
        output = run_all_rules(pr)
        assert output["passed"] is False

    def test_runner_collects_both_rule_results(self):
        pr = make_pr("feat: valid title small pr", num_files=5)
        output = run_all_rules(pr)
        assert len(output["results"]) == 2
        rule_names = [r["rule"] for r in output["results"]]
        assert "pr-title-format" in rule_names
        assert "pr-size-check" in rule_names


class TestLogWriter:

    def _make_results(self, title="feat: test", num_files=2, passed=True):
        files = [{"filename": f"f{i}.py", "content": ""} for i in range(num_files)]
        return {
            "passed": passed,
            "ran_at": "2024-01-01 00:00:00 UTC",
            "pr": {
                "number": "42",
                "title": title,
                "author": "test-user",
                "base": "main",
                "head": "feat/test",
                "files": files,
            },
            "results": [
                {
                    "rule": "pr-title-format",
                    "passed": passed,
                    "message": "✅ PR title is valid: 'feat: test'" if passed else "❌ Bad title",
                },
                {
                    "rule": "pr-size-check",
                    "passed": True,
                    "message": f"✅ PR size is good: {num_files} file(s) changed.",
                },
            ],
        }

    def test_log_file_created(self, tmp_path):
        import json
        from log_writer import generate_log

        results_file = tmp_path / "pr_results.json"
        results_file.write_text(json.dumps(self._make_results()))
        log_path = generate_log(str(results_file), output_dir=str(tmp_path / "logs"))
        assert os.path.exists(log_path)

    def test_log_contains_pr_metadata(self, tmp_path):
        import json
        from log_writer import generate_log

        results_file = tmp_path / "pr_results.json"
        results_file.write_text(json.dumps(self._make_results(title="feat: my feature")))
        log_path = generate_log(str(results_file), output_dir=str(tmp_path / "logs"))
        content = open(log_path).read()
        assert "feat: my feature" in content
        assert "test-user" in content
        assert "42" in content

    def test_log_shows_passed(self, tmp_path):
        import json
        from log_writer import generate_log

        results_file = tmp_path / "pr_results.json"
        results_file.write_text(json.dumps(self._make_results(passed=True)))
        log_path = generate_log(str(results_file), output_dir=str(tmp_path / "logs"))
        content = open(log_path).read()
        assert "✅ PASSED" in content

    def test_log_shows_failed(self, tmp_path):
        import json
        from log_writer import generate_log

        results_file = tmp_path / "pr_results.json"
        results_file.write_text(json.dumps(self._make_results(passed=False)))
        log_path = generate_log(str(results_file), output_dir=str(tmp_path / "logs"))
        content = open(log_path).read()
        assert "❌ FAILED" in content

    def test_log_filename_contains_pr_number(self, tmp_path):
        import json
        from log_writer import generate_log

        results_file = tmp_path / "pr_results.json"
        results_file.write_text(json.dumps(self._make_results()))
        log_path = generate_log(str(results_file), output_dir=str(tmp_path / "logs"))
        assert "pr_42_" in os.path.basename(log_path)
