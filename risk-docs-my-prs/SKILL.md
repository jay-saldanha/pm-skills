---
name: risk-docs-my-prs
description: List all open PRs in sardine-ai/risk-docs that are created by me or assigned to me for review, in a detailed table with dates, people, links, and status.
disable-model-invocation: false
---

## Task: List My PRs in risk-docs

You are surfacing all open pull requests in `sardine-ai/risk-docs` that involve the current user — either as the author or as a requested reviewer.

The repo is at `/Users/jayana/risk-docs`. The GitHub user is `jay-saldanha`.

### Steps

1. **Fetch all open PRs** by running the following two `gh` commands from `/Users/jayana/risk-docs`:

   ```bash
   # PRs created by me
   gh pr list --repo sardine-ai/risk-docs --author jay-saldanha --state all --limit 100 \
     --json number,title,url,state,createdAt,updatedAt,author,assignees,reviewRequests,reviews,headRefName,baseRefName

   # PRs where I am a requested reviewer
   gh pr list --repo sardine-ai/risk-docs --search "review-requested:jay-saldanha" --state all --limit 100 \
     --json number,title,url,state,createdAt,updatedAt,author,assignees,reviewRequests,reviews,headRefName,baseRefName
   ```

2. **Merge and deduplicate** the two result sets by PR number.

3. **For each PR**, extract:
   - PR number and title
   - URL (direct link)
   - State: `open`, `closed`, or `merged`
   - Draft status (mark as `Draft` if applicable)
   - `createdAt` — format as `YYYY-MM-DD`
   - `updatedAt` — format as `YYYY-MM-DD`
   - **Author** (`author.login`)
   - **Assignees** (`assignees[].login`, comma-separated, or `—` if none)
   - **Reviewers** — combine `reviewRequests[].login` (pending) and unique `reviews[].author.login` (submitted), comma-separated, or `—` if none
   - **My role** — `Author`, `Reviewer`, or `Author + Reviewer`

4. **Sort** the combined list: open PRs first (newest `updatedAt` first), then closed/merged (newest `updatedAt` first).

5. **Output a Markdown table**:

   | # | Title | Status | My Role | Created | Last Updated | Author | Assignees | Reviewers | Link |
   |---|-------|--------|---------|---------|--------------|--------|-----------|-----------|------|
   | 1234 | Fix typo in AML guide | Open | Author | 2026-03-10 | 2026-03-18 | jay-saldanha | — | alice, bob | [#1234](url) |
   | 1200 | Add integration guide | Draft | Author | 2026-02-01 | 2026-03-15 | jay-saldanha | — | — | [#1200](url) |
   | 1190 | Update risk thresholds | Merged | Reviewer | 2026-01-15 | 2026-02-20 | alice | jay-saldanha | jay-saldanha | [#1190](url) |

6. **Update the CSV** at `/Users/jayana/risk-docs-my-prs.csv` incrementally — do not overwrite existing data.

   CSV header and format:
   ```
   PR Number,Title,Status,My Role,Created,Last Updated,Author,Assignees,Reviewers,URL
   1234,"Fix typo in AML guide",Open,Author,2026-03-10,2026-03-18,jay-saldanha,,alice/bob,https://github.com/...
   ```
   - Use double-quotes around fields that may contain commas
   - Multiple assignees/reviewers separated by `/`
   - Leave the field empty (not `—`) when there are none

   **Merge logic:**
   - If the CSV does not exist yet, create it with the header and all current PRs.
   - If the CSV already exists, read it and load existing rows keyed by PR Number.
   - For each PR fetched from GitHub:
     - If the PR number is **not** in the CSV → add it as a new row.
     - If the PR number **is** in the CSV and any field has changed (status, title, reviewers, assignees, updatedAt) → update that row in place.
     - If the PR number is in the CSV but was not returned by GitHub (e.g. very old closed PR no longer in the API window) → leave the existing row unchanged.
   - Write the final merged rows back to the file, preserving the original sort order of existing rows and appending new rows at the bottom.

7. **Print a summary line** below the table, e.g.:
   > Found **12 PRs** — 5 open (2 draft), 4 merged, 3 closed. You authored 8, are a reviewer on 5.
   > Saved to `/Users/jayana/risk-docs-my-prs.csv`
