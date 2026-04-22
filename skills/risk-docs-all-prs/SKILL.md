---
name: risk-docs-all-prs
description: List all open PRs in sardine-ai/risk-docs by human authors (skipping bots), with reviewer status and merge conflict state, in a table sorted by PR number descending.
disable-model-invocation: false
---

## Task: List All Open Human-Authored PRs in risk-docs

Fetch and display every open pull request in `sardine-ai/risk-docs` authored by a human (skip dependabot, mintlify, and other bots). Show reviewer assignment and merge conflict status.

### Steps

1. **Fetch all open PRs** with this command:

   ```bash
   gh pr list --repo sardine-ai/risk-docs --state open --limit 100 \
     --json number,title,author,createdAt,url,reviewDecision,reviewRequests,reviews,mergeable
   ```

2. **Filter out bots**: skip any PR where `author.is_bot` is `true`.

3. **For each remaining PR**, extract:
   - **PR number** and **title** (full, not truncated)
   - **Author** (`author.login`)
   - **Review status**: `✅ Approved` if `reviewDecision == "APPROVED"`, otherwise `🔵 Review needed`
   - **Reviewer(s)**: combine submitted reviews (`reviews[].author.login → state`) and pending requests (`reviewRequests[].login`). Exclude bots (`devin-ai-integration`, `github-actions`, `copilot-pull-request-reviewer`). Format each as `login: state` (state = approved / commented / requested). If none, show `not assigned`.
   - **Conflicts**: `⚠️ CONFLICT` if `mergeable == "CONFLICTING"`. Leave blank if `MERGEABLE` or `UNKNOWN`.
   - **Date**: `createdAt` formatted as `Mon DD` (e.g. `Apr 14`) or `Mon DD 'YY` if not the current year.

4. **Sort** by PR number descending (newest first).

5. **Output a single Markdown table**:

   | PR | Title | Author | Review Status | Reviewer(s) | Conflicts | Date |
   |----|-------|--------|---------------|-------------|-----------|------|
   | [#1357](url) | Update iOS changelog with Xcode 26 warning | jay-saldanha | 🔵 Review needed | gisu-kim-sardine: requested | | Apr 22 |
   | [#1293](url) | feat: updated react native integration pages | gisu-kim-sardine | ✅ Approved | jay-saldanha: approved, devsherif: requested | ⚠️ CONFLICT | Apr 1 |

6. **Print a summary line** below the table, e.g.:
   > **38 open PRs** — 5 approved and waiting to merge, 2 confirmed conflicts. X closed/merged since last checked.

   If the previous run's count is known from context, note how many PRs were added or closed since then.
