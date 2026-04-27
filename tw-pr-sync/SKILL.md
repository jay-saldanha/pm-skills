---
name: tw-pr-sync
description: For the current month, match GitHub PRs (authored or reviewed by me) to Asana tasks on the Technical Writing Requests board — update status if a task exists, create one if not. Skip closed (not merged) PRs.
disable-model-invocation: false
argument-hint: "[month]"
---

## Task: Sync GitHub PRs to Asana Technical Writing Board

You are syncing pull requests from `sardine-ai/risk-docs` to the Asana "Technical Writing Requests" project (GID: `1208751645869782`).

**GitHub user:** `jay-saldanha`
**Repo:** `sardine-ai/risk-docs` (local path: `/Users/jayana/risk-docs`)
**Asana project GID:** `1208751645869782`
**Asana Status custom field GID:** `1208751645869803`

---

### Arguments

Accept an optional month in any natural format (e.g. `April`, `April 2026`, `last month`). Default: current calendar month.

---

### Step 1 — Determine date range

Calculate `MONTH_START` and `MONTH_END` in `YYYY-MM-DD` format for the target month.

---

### Step 2 — Fetch PRs from GitHub (run both in parallel)

```bash
# PRs authored by me, updated this month
gh api "search/issues?q=author:jay-saldanha+repo:sardine-ai/risk-docs+type:pr+updated:MONTH_START..MONTH_END&per_page=100" \
  --jq '.items[] | {number, title, html_url, state, pull_request}'

# PRs reviewed by me (not authored), updated this month
gh api "search/issues?q=reviewed-by:jay-saldanha+repo:sardine-ai/risk-docs+type:pr+updated:MONTH_START..MONTH_END+-author:jay-saldanha&per_page=100" \
  --jq '.items[] | {number, title, html_url, state, pull_request}'
```

For each PR, also fetch draft status and merge state:
```bash
gh pr view <number> --repo sardine-ai/risk-docs --json number,title,url,state,isDraft,mergedAt,author
```

Fetch only PRs where `updatedAt` falls within the month range. Deduplicate by PR number. **Skip any PR where `state=closed` and `mergedAt` is null** (closed without merging).

After filtering, you should have a list of PRs that are: open (draft or not), or merged.

---

### Step 3 — Fetch Asana project data (run both in parallel)

**Fetch all tasks:**
Use `mcp__claude_ai_Asana__get_tasks` with:
- `project_id`: `1208751645869782`
- `opt_fields`: `gid,name,notes,html_notes,custom_fields,memberships.section.gid,memberships.section.name,permalink_url,completed`

**Fetch project sections and custom field options:**
Use `mcp__claude_ai_Asana__get_project` with:
- `project_id`: `1208751645869782`

From the project response, extract:
- All section GIDs and names (to find the right section when creating tasks)
- All enum options for the status custom field (`1208751645869803`) — you need the GID for each status label (e.g. "In progress", "Not started", "Complete")

Store these mappings for use in steps 5–7.

---

### Step 4 — Build PR → Asana status and section mapping

| PR state | Asana status label | Asana section name |
|----------|-------------------|-------------------|
| Open, draft | Not started | Not started (or equivalent) |
| Open, not draft | In progress | In Progress (or equivalent) |
| Merged | Complete | Complete (or equivalent) |

Use the enum GIDs and section GIDs discovered in Step 3 to fill in the actual IDs. Match section names case-insensitively, using substring match if exact match fails (e.g. "in progress" matches "In Progress").

Known GID (from existing tooling):
- "In progress" status enum GID: `1208751645869806`

---

### Step 5 — Match each PR to an Asana task

For each PR, search the task list from Step 3 using the following priority order. Stop at the first match.

**Match 1 — Exact URL match (most reliable)**
Search each task's `notes` and `html_notes` for the string `github.com/sardine-ai/risk-docs/pull/<PR number>`. If found → match confirmed.

**Match 2 — PR number mention**
Search task name and notes for the string `#<PR number>` (e.g. `#1234`). If found → match confirmed.

**Match 3 — Fuzzy title match**
Normalize both the PR title and each task name:
- Lowercase
- Remove punctuation and stopwords (`a, an, the, in, of, for, to, and, or, with, is, on, at`)
- Tokenize into words

Match if: at least **3 significant words** (4+ characters) from the PR title appear in the task name, OR **≥ 60%** of the PR title's significant words appear in the task name (minimum 2 words required to trigger fuzzy match).

If a fuzzy match is found, mark it as `fuzzy` in the report for review.

If multiple candidates score equally, pick the one with the most recent `created_at`.

If no match is found → mark PR as `no match` (will create a new task).

---

### Step 6 — Update or create Asana tasks

**For each PR with a match found:**

Check the task's current status custom field value. If it already equals the target status GID → log as `no-op`.

If the status differs → update using `mcp__claude_ai_Asana__update_tasks`:
```json
{
  "task_id": "<task GID>",
  "custom_fields": "{\"1208751645869803\": \"<target status enum GID>\"}"
}
```

Do NOT move matched tasks to a different section — only update the status field.

---

**For each PR with no match:**

Create a new task using `mcp__claude_ai_Asana__create_tasks` with:
- `name`: `[PR #<number>] <PR title>`
- `projects`: `["1208751645869782"]`
- `memberships`: `[{"project": "1208751645869782", "section": "<target section GID>"}]`
- `custom_fields`: `{"1208751645869803": "<target status enum GID>"}`
- `notes` body:

```
PR: https://github.com/sardine-ai/risk-docs/pull/<number>
Author: <author login>
State: <Open / Merged>
Created: <createdAt date>

Auto-created by tw-pr-sync skill.
```

---

### Step 7 — Write Asana task link back to authored PR descriptions

For every PR where **`author.login == jay-saldanha`** (not review-only PRs):

1. Fetch the current PR body:
   ```bash
   gh pr view <number> --repo sardine-ai/risk-docs --json body
   ```

2. Check if the PR body already contains the Asana task URL (substring match on `app.asana.com`). If it does → skip (no-op).

3. If not present → append the Asana task link to the PR body:
   ```bash
   gh pr edit <number> --repo sardine-ai/risk-docs --body "<existing body>

   ---
   **Asana:** [<task name>](<asana permalink_url>)"
   ```

   Preserve the full existing body exactly. Only append — do not rewrite or reformat anything above the `---` separator.

   If the existing body is empty, write just:
   ```
   **Asana:** [<task name>](<asana permalink_url>)
   ```

---

### Step 8 — Report results

Print a summary table:

| PR | Title | My Role | PR State | Match | Match Type | Asana Task | Asana Action | PR Body |
|----|-------|---------|----------|-------|------------|------------|--------------|---------|
| #1234 | Fix AML guide typo | Author | Merged | ✓ | URL | [Task name](asana url) | Updated → Complete | Asana link added |
| #1240 | Add KYC integration | Author | Open | ✓ | Fuzzy ⚠️ | [Task name](asana url) | No-op | Already linked |
| #1245 | Update webhook docs | Author | Open (draft) | — | — | — | Created → Not started | Asana link added |
| #1260 | Review translations | Reviewer | Merged | ✓ | URL | [Task name](asana url) | Updated → Complete | — (not author) |

Below the table, print:
- Count of Asana tasks updated, created, no-op
- Count of PR descriptions updated with Asana link
- Count of PRs skipped (closed without merge)
- Any fuzzy matches — list them separately and ask the user to verify they are correct
- Any cases where multiple fuzzy candidates were found and tie-broken — list them for review
