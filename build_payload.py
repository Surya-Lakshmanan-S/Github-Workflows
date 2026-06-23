"""
Builds the PR payload including file contents.
This runs inside GitHub Actions before the rule engine.
"""

import sys
import json
import os


def main():
    files_string = sys.argv[1]
    filenames = [f for f in files_string.split(",") if f]

    files_data = []
    for filename in filenames:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            files_data.append({
                "filename": filename,
                "content": content,
            })

    payload = {
        "title": os.environ.get("PR_TITLE", ""),
        "number": os.environ.get("PR_NUMBER", ""),
        "author": os.environ.get("PR_AUTHOR", ""),
        "base": os.environ.get("PR_BASE", ""),
        "head": os.environ.get("PR_HEAD", ""),
        "files": files_data,
    }

    with open("pr_payload.json", "w") as f:
        json.dump(payload, f, indent=2)


if __name__ == "__main__":
    main()
