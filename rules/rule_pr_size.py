"""
Rule: pr-size-check
────────────────────
Ensures a PR doesn't change too many files at once.
Large PRs are harder to review and more likely to introduce bugs.

Thresholds:
  - ✅  1–15 files  → OK
  - ⚠️  16–30 files → WARNING (passes, but leaves a note)
  - ❌  31+ files   → FAIL (too large to review safely)
"""

RULE_NAME = "pr-size-check"

WARN_THRESHOLD = 15
FAIL_THRESHOLD = 30


def check(pr: dict) -> dict:
    files = pr.get("files", [])
    count = len(files)

    if count == 0:
        return {
            "rule": RULE_NAME,
            "passed": True,
            "message": "✅ No files changed (or payload built without file list).",
        }

    if count <= WARN_THRESHOLD:
        return {
            "rule": RULE_NAME,
            "passed": True,
            "message": f"✅ PR size is good: {count} file(s) changed.",
        }

    if count <= FAIL_THRESHOLD:
        return {
            "rule": RULE_NAME,
            "passed": True,
            "message": (
                f"⚠️  PR is getting large: {count} file(s) changed. "
                f"Consider splitting into smaller PRs if possible "
                f"(warning threshold: {WARN_THRESHOLD} files)."
            ),
        }

    return {
        "rule": RULE_NAME,
        "passed": False,
        "message": (
            f"❌ PR is too large: {count} file(s) changed. "
            f"Please split this into smaller PRs. "
            f"Maximum allowed: {FAIL_THRESHOLD} files."
        ),
    }
