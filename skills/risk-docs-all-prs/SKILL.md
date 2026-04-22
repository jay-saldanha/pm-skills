---
name: risk-docs-all-prs
description: List all open PRs in sardine-ai/risk-docs with reviewer status and merge conflict state. Human-authored PRs shown grouped by author and as a flat table; bot PRs (dependabot, mintlify) shown in a separate table.
disable-model-invocation: false
---

## Task: List All Open PRs in risk-docs

Fetch and display every open pull request in `sardine-ai/risk-docs`. Show human-authored and bot-authored PRs in separate sections. Show reviewer assignment and merge conflict status.

### Steps

1. **Fetch all open PRs** with this command:

   ```bash
   gh pr list --repo sardine-ai/risk-docs --state open --limit 100 \
     --json number,title,author,createdAt,url,reviewDecision,reviewRequests,reviews,mergeable
   ```

2. **Split into two groups**:
   - **Human PRs**: `author.is_bot == false`
   - **Bot PRs**: `author.is_bot == true` (dependabot, mintlify, etc.)

3. **For each PR**, extract:
   - **PR number** and **title** (full, not truncated)
   - **Author** (`author.login`)
   - **Review status**: `✅ Approved` if `reviewDecision == "APPROVED"`, otherwise `🔵 Review needed`
   - **Reviewer(s)** (human PRs only): combine submitted reviews (`reviews[].author.login → state`) and pending requests (`reviewRequests[].login`). Exclude bot reviewers (`devin-ai-integration`, `github-actions`, `copilot-pull-request-reviewer`). Format each as `login: state` (state = approved / commented / requested). If none, show `not assigned`.
   - **Conflicts**: `⚠️ CONFLICT` if `mergeable == "CONFLICTING"`. Leave blank if `MERGEABLE` or `UNKNOWN`.
   - **Date**: `createdAt` formatted as `Mon DD` (e.g. `Apr 14`) or `Mon DD 'YY` if not the current year.

4. **Sort** all groups by PR number descending (newest first).

5. **Output three Markdown sections**:

   **Section 1 — Human PRs grouped by author**

   Group rows by `author.login` with a `### author-login` subheading before each author's rows. Authors sorted alphabetically; PRs within each author sorted by PR number descending.

   | PR | Title | Review Status | Reviewer(s) | Conflicts | Date |
   |----|-------|---------------|-------------|-----------|------|
   | [#1357](url) | Update iOS changelog with Xcode 26 warning | 🔵 Review needed | gisu-kim-sardine: requested | | Apr 22 |

   **Section 2 — Human PRs flat table** (all humans together, PR number descending)

   | PR | Title | Author | Review Status | Reviewer(s) | Conflicts | Date |
   |----|-------|--------|---------------|-------------|-----------|------|
   | [#1357](url) | Update iOS changelog with Xcode 26 warning | jay-saldanha | 🔵 Review needed | gisu-kim-sardine: requested | | Apr 22 |
   | [#1293](url) | feat: updated react native integration pages | gisu-kim-sardine | ✅ Approved | jay-saldanha: approved, devsherif: requested | ⚠️ CONFLICT | Apr 1 |

   **Section 3 — Bot PRs** (dependabot, mintlify, etc., PR number descending)

   | PR | Title | Bot | Conflicts | Date |
   |----|-------|-----|-----------|------|
   | [#1352](url) | chore(deps): bump follow-redirects 1.15.9 → 1.16.0 | dependabot | | Apr 20 |

6. **Print a summary line** below all sections, e.g.:
   > **59 open PRs** — 38 human (across 6 authors), 21 bot. 5 approved and waiting to merge, 2 confirmed conflicts. X closed/merged since last checked.

   If the previous run's count is known from context, note how many PRs were added or closed since then.
