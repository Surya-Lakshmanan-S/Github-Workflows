"""
PR Rule Engine — Log Writer
────────────────────────────
Reads pr_results.json and writes a human-readable log file to:
  logs/pr_<number>_<timestamp>.md

The log captures:
  - PR metadata
  - Each rule's name, status, and message
  - Overall pass/fail summary
"""

import json
import os
import sys
from datetime import datetime, timezone


def _status_icon(passed: bool) -> str:
    return "✅ PASSED" if passed else "❌ FAILED"


def generate_log(results_path: str, output_dir: str = "logs") -> str:
    with open(results_path) as f:
        data = json.load(f)

    pr       = data.get("pr", {})
    results  = data.get("results", [])
    overall  = data.get("passed", False)
    ran_at   = data.get("ran_at", datetime.now(timezone.utc).isoformat())

    pr_number = pr.get("number", "unknown")
    pr_title  = pr.get("title",  "unknown")
    pr_author = pr.get("author", "unknown")
    pr_base   = pr.get("base",   "unknown")
    pr_head   = pr.get("head",   "unknown")
    num_files = len(pr.get("files", []))

    passed_count = sum(1 for r in results if r.get("passed"))
    failed_count = len(results) - passed_count

    lines = [
        "# PR Rule Engine — Validation Log",
        "",
        f"**Run at:** {ran_at}",
        "",
        "---",
        "",
        "## PR Details",
        "",
        f"| Field   | Value |",
        f"|---------|-------|",
        f"| PR #    | {pr_number} |",
        f"| Title   | {pr_title} |",
        f"| Author  | {pr_author} |",
        f"| Base    | `{pr_base}` |",
        f"| Head    | `{pr_head}` |",
        f"| Files Changed | {num_files} |",
        "",
        "---",
        "",
        "## Rule Results",
        "",
    ]

    for i, rule in enumerate(results, start=1):
        rule_name = rule.get("rule", f"rule-{i}")
        passed    = rule.get("passed", False)
        message   = rule.get("message", "No message provided.")

        lines += [
            f"### {i}. `{rule_name}`",
            "",
            f"**Status:** {_status_icon(passed)}",
            "",
            f"**Details:** {message}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Summary",
        "",
        f"| | Count |",
        f"|---|---|",
        f"| Total Rules Run | {len(results)} |",
        f"| Passed          | {passed_count} |",
        f"| Failed          | {failed_count} |",
        "",
        f"## Overall Result: {_status_icon(overall)}",
        "",
    ]

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename  = f"pr_{pr_number}_{timestamp}.md"
    filepath  = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print(f"📝 Log written to: {filepath}")
    return filepath


if __name__ == "__main__":
    results_file = sys.argv[1] if len(sys.argv) > 1 else "pr_results.json"
    generate_log(results_file)
