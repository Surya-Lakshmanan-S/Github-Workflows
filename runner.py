"""
PR Rule Engine — Runner
───────────────────────
HOW TO ADD A NEW RULE:
1. Create a file in /rules folder
2. Import it below
3. Add it to the RULES list
That's it! ✅
"""

import json
import sys
from datetime import datetime, timezone
from rules.rule_pr_title import check as rule_pr_title
from rules.rule_pr_size import check as rule_pr_size

# ─────────────────────────────────────────
# RULE REGISTRY
# Add new rules here ↓
# ─────────────────────────────────────────
RULES = [
    rule_pr_title,
    rule_pr_size,
]


def run_all_rules(pr: dict) -> dict:
    results = []
    for rule_fn in RULES:
        result = rule_fn(pr)
        results.append(result)
    overall_passed = all(r["passed"] for r in results)
    return {
        "passed": overall_passed,
        "results": results,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runner.py <pr_payload.json>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        pr_payload = json.load(f)
    output = run_all_rules(pr_payload)

    # Enrich output with PR metadata and timestamp for the log writer
    output["pr"] = {
        "number": pr_payload.get("number", "unknown"),
        "title":  pr_payload.get("title",  ""),
        "author": pr_payload.get("author", ""),
        "base":   pr_payload.get("base",   ""),
        "head":   pr_payload.get("head",   ""),
        "files":  pr_payload.get("files",  []),
    }
    output["ran_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Write results JSON for log_writer.py to consume
    with open("pr_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))
    sys.exit(0 if output["passed"] else 1)
