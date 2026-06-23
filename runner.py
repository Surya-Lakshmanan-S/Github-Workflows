import json
import sys
from rules.rule_pr_title import check as rule_pr_title
from rules.rule_branch_name import check as rule_branch_name  # ← add here
from rules.rule_sql_keywords import check as rule_sql_keywords
from rules.rule_plsql_pairs import check as rule_plsql_pairs
from rules.rule_intendation import check as rule_intendation
from rules.rule_author_comment import check as rule_author_comment

RULES = [
    rule_pr_title,
    rule_branch_name,
    rule_sql_keywords,
    rule_plsql_pairs, 
    rule_intendation,
    rule_author_comment,
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

    # Print results
    print(json.dumps(output, indent=2))

    # Save results to file so log_results.py can read it
    with open("pr_results.json", "w") as f:
        json.dump(output, f, indent=2)

    sys.exit(0 if output["passed"] else 1)
