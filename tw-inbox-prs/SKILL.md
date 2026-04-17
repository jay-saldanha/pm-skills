---
name: tw-inbox-prs
description: Look at the Asana "Technical Writing Requests" board, pick the 3 newest and 3 oldest inbox tickets, and create draft PRs from main in risk-docs for any that don't already have one. Skip tickets with no decipherable title/description and report them.
disable-model-invocation: false
argument-hint: "<newest-count> <oldest-count>"
---

## Task: Create Draft PRs from Technical Writing Requests Inbox

You are helping manage the "Technical Writing Requests" Asana project (GID: `1208751645869782`) in the `sardine-ai/risk-docs` repo at `/Users/jayana/risk-docs`.

### Steps

1. **Fetch Inbox tickets** from Asana project `1208751645869782` using `mcp__claude_ai_Asana__get_tasks` with `opt_fields=name,created_at,completed,memberships.section.name,permalink_url`. Filter to section name `"Inbox"`.

2. **Sort by `created_at`** and select:
   - 3 newest (most recent) Inbox tickets
   - 3 oldest (earliest) Inbox tickets
   - Default counts are 3/3 unless overridden by $ARGUMENTS (e.g., `/tw-inbox-prs 5 5`)

3. **Skip and report** any ticket that:
   - Has a name that is empty, a single symbol (e.g. `<`), or otherwise not decipherable
   - Substitute with the next valid ticket in the sort order

4. **Check for existing PRs** — run `gh pr list --limit 100 --json title,headRefName` in `/Users/jayana/risk-docs`. Skip any ticket whose name matches an existing open PR title or whose Asana GID appears in a branch name.

5. **For each remaining ticket**, create a draft PR:
   ```bash
   cd /Users/jayana/risk-docs
   git fetch origin main
   git checkout -b asana/<slugified-ticket-name> origin/main
   git commit --allow-empty -m "chore: scaffold branch for '<ticket name>' [Asana: <GID>]"
   git push -u origin asana/<slugified-ticket-name>
   gh pr create --title "<ticket name>" --draft --body "..."
   ```
   Branch naming: `asana/` + lowercase ticket name with spaces replaced by `-`, non-alphanumeric chars removed.

   PR body template:
   ```
   ## Asana Ticket
   [<ticket name>](<asana permalink>)

   ## Summary
   <Brief description based on ticket name>

   ## Changes
   - TBD

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

6. **Write actual content for each PR** — after pushing the scaffold branch, read the Asana ticket's `notes` field to understand the request, explore the relevant area of the repo (`guides/`, `snippets/`), then write the doc content:
   - For bug/fix tickets: find the broken file and fix it
   - For new doc tickets: create a new `.mdx` file in the appropriate `guides/` subdirectory
   - For API/integration tickets: create a guide in `guides/integration/integrationguides/<topic>/`
   - For knowledge base articles: create a file in `guides/knowledge-base/<topic>/`
   - For blog posts: create a draft in `guides/knowledge-base/case-study/` with a `draft: true` frontmatter flag and a `<Warning>` block
   - Commit the content with a descriptive message, then push

7. **Add PR link to each Asana ticket** — append to the task's `html_notes` using `mcp__claude_ai_Asana__update_task`:
   ```
   <strong>PR:</strong> <a href="https://github.com/sardine-ai/risk-docs/pull/XXXX" data-asana-dynamic="false">sardine-ai/risk-docs#XXXX</a>
   ```
   Preserve the existing `html_notes` content and append the PR line at the end before `</body>`.

8. **Move ticket to "In progress"** — update the Status custom field using `mcp__claude_ai_Asana__update_task`:
   ```json
   { "task_id": "<GID>", "custom_fields": "{\"1208751645869803\": \"1208751645869806\"}" }
   ```
   Status field GID: `1208751645869803` | "In progress" enum option GID: `1208751645869806`

9. **Return to original branch** after creating all PRs:
   ```bash
   git checkout -
   ```

10. **Report results** in a table:
   | # | Ticket | Age | PR | Status |
   |---|--------|-----|----|--------|
   | 1 (newest) | Create a new draft blog | today | #1240 | Created |
   | 2 (newest) | ... | | | |
   | 3 (newest) | ... | | | |
   | 1 (oldest) | Alert Decisioning API | 10 months | #1244 | Created |
   | ... | | | | |

   Also list any skipped/flagged tickets separately.
