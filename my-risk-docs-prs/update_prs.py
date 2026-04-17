#!/usr/bin/env python3
"""
Fetches all risk-docs PRs involving jay-saldanha and writes
/Users/jayana/risk-docs-my-prs.csv with columns:
  PR Number, Title, Status, My Role, Created, Last Updated,
  Author, Assignees, Reviewers, URL
"""

import json
import subprocess
import csv
import sys
from datetime import datetime

REPO = "sardine-ai/risk-docs"
ME = "jay-saldanha"
OUT = "/Users/jayana/risk-docs-my-prs.csv"
LIMIT = 500


def gh(*args):
    result = subprocess.run(
        ["gh", *args],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def fmt_date(iso):
    if not iso:
        return ""
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d")


def logins(items):
    return "/".join(sorted(set(
        (i.get("login") or i.get("author", {}).get("login", ""))
        for i in items
        if (i.get("login") or i.get("author", {}).get("login", ""))
    )))


def my_role(pr):
    is_author = pr["author"]["login"] == ME
    reviewer_logins = set(
        r["login"] for r in pr.get("reviewRequests", [])
    ) | set(
        r["author"]["login"] for r in pr.get("reviews", [])
        if r.get("author", {}).get("login")
    )
    assignee_logins = set(a["login"] for a in pr.get("assignees", []))

    roles = []
    if is_author:
        roles.append("Author")
    if ME in reviewer_logins:
        roles.append("Reviewer")
    if ME in assignee_logins and "Reviewer" not in roles:
        roles.append("Assignee")
    if not roles:
        roles.append("Involved")
    return " + ".join(roles)


def status(pr):
    s = pr["state"].capitalize()
    if s == "Merged":
        return "Merged"
    if pr.get("isDraft"):
        return "Draft"
    return s


def fetch_prs():
    raw = gh(
        "pr", "list",
        "--repo", REPO,
        "--search", f"involves:{ME}",
        "--state", "all",
        "--limit", str(LIMIT),
        "--json", "number,title,state,isDraft,createdAt,updatedAt,"
                  "author,assignees,reviewRequests,reviews,url",
    )
    return sorted(raw, key=lambda p: p["number"], reverse=True)


def main():
    print(f"Fetching PRs from {REPO} involving {ME}…", file=sys.stderr)
    prs = fetch_prs()
    print(f"Found {len(prs)} PRs", file=sys.stderr)

    rows = []
    for pr in prs:
        reviewer_logins_raw = (
            [r["login"] for r in pr.get("reviewRequests", [])] +
            [r["author"]["login"] for r in pr.get("reviews", [])
             if r.get("author", {}).get("login")]
        )
        rows.append({
            "PR Number": pr["number"],
            "Title": pr["title"],
            "Status": status(pr),
            "My Role": my_role(pr),
            "Created": fmt_date(pr["createdAt"]),
            "Last Updated": fmt_date(pr["updatedAt"]),
            "Author": pr["author"]["login"],
            "Assignees": logins(pr.get("assignees", [])),
            "Reviewers": "/".join(sorted(set(reviewer_logins_raw))),
            "URL": pr["url"],
        })

    fieldnames = ["PR Number", "Title", "Status", "My Role",
                  "Created", "Last Updated", "Author", "Assignees",
                  "Reviewers", "URL"]

    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Written {len(rows)} rows → {OUT}", file=sys.stderr)
    # Print summary table to stdout for Claude to read
    print(f"{'#':<6} {'Status':<10} {'Role':<22} {'Title'}")
    print("-" * 80)
    for r in rows[:30]:
        print(f"{r['PR Number']:<6} {r['Status']:<10} {r['My Role']:<22} {r['Title'][:50]}")
    if len(rows) > 30:
        print(f"  … and {len(rows) - 30} more (see {OUT})")


if __name__ == "__main__":
    main()
