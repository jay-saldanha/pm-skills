---
name: rn-sync
description: Sync newly moved "In Progress" tasks from the Asana Release Notes project to the current month's Notion release notes page. Adds new entries in the standard release notes format; skips tasks already present. Also flags missing videos and mismatched Release Month values.
disable-model-invocation: false
argument-hint: "[notion-page-url]"
---

## Task: Sync Asana In Progress → Notion Release Notes

Check the Asana Release Notes project "In Progress" section and add any new tasks to the Notion release notes page, following the established entry format. Also audit the page for missing video demos and check each Asana task's "Release Month" field against the target month.

**Asana project:** Release Notes  
**Asana project GID:** `1213848374258762`  
**In Progress section GID:** `1213836732664070`  
**Completed section GID:** `1213836732664072`  
**Release Month custom field GID:** `1213836743338972`  
**Release Notes parent Notion page:** `https://www.notion.so/17ad52e0dd8b80cfae8bdd26b71554fb`

---

### Arguments

Accept an optional Notion page URL or ID. If not provided, search the Release Notes parent Notion page for the current month's release notes page (e.g. "April 2026 Release Notes").

---

### Step 1 — Resolve the Notion page

If a URL/ID was passed as an argument, use it directly.

If no argument was given:
- Fetch the Release Notes parent page at `https://www.notion.so/17ad52e0dd8b80cfae8bdd26b71554fb`
- Find the child page matching the current month and year (e.g. "April 2026 Release Notes")
- Use that page's URL for all subsequent steps

Extract the **target month** from the page title (e.g. "April 2026"). This is used in Step 4 to validate Release Month fields.

---

### Step 2 — Fetch data in parallel

Run both simultaneously:

**A. Asana In Progress tasks**

Use `mcp__claude_ai_Asana__get_tasks` with:
- `section`: `1213836732664070`
- `opt_fields`: `name,notes,assignee,custom_fields`

The result may be very large — save it and use `jq` to extract `gid`, `name`, `notes`, and the value of the `Release Month` custom field (GID `1213836743338972`) per task:

```bash
jq '[.data[] | {
  gid,
  name,
  notes,
  release_month: (.custom_fields[] | select(.gid == "1213836743338972") | .text_value) // null
}]' <file>
```

**B. Notion page content**

Use `mcp__claude_ai_Notion__notion-fetch` on the resolved Notion page URL.

---

### Step 3 — Identify new tasks

From the Notion page content, collect all existing `## ` heading titles (these are feature entry names already on the page).

For each Asana task, check whether a heading closely matching its name already exists in the Notion page:
- Strip tags like `[P0]`, `[P1]`, `[Swan]`, etc. from the Asana task name before comparing
- Use case-insensitive substring matching
- If a match is found → mark as **existing**
- If no match → mark as **new**

---

### Step 4 — Check Release Month for all In Progress tasks

For every task (new and existing), compare its `release_month` value against the target month:

- Parse the target month from the Notion page title (e.g. "April 2026" → match strings like "April 2026", "Apr 2026", "04/2026", or just "April")
- If `release_month` is null/empty → flag as **⚠️ Release Month not set**
- If `release_month` does not match the target month → flag as **⚠️ Release Month mismatch** (show the actual value)
- If it matches → ✓

---

### Step 5 — Check for missing video demos

Scan the Notion page content for all feature entries. For each `## ` heading that represents a feature (exclude `## SDK Changelogs`, `## Feature 1`, and any heading that is just `##`):

Check if the `## Video Demo` block immediately following that entry contains only `Coming soon` (or is empty).

- If `Coming soon` or empty → flag as **⚠️ Video missing**
- If it contains any other content (a URL, an embedded video, etc.) → ✓

---

### Step 6 — Add new entries to Notion

If there are no new tasks, skip this step.

For each new task, construct a release notes entry in this format:

```
## <Clean task name (no [P0]/[P1]/[Swan] tags)>
Author: \<please tag yourself here so that I know who added these\>
### What's new
<1–3 bullets summarizing what changed, drawn from the task notes or linked Notion doc>
### Customer impact
<1–3 bullets on why customers should care>
### Description of changes
<More detailed explanation. Use bullet points. If a linked Notion page was fetched, draw on its Overview/Benefits/Key Features sections. Do not paste raw How-To steps — summarize the capability instead.>
## Video Demo
Coming soon
```

Before writing, fetch any Notion URLs found in the task notes to enrich the entry content.

Insert all new entries before the `## SDK Changelogs` section (or at the end of the page if that section doesn't exist).

Use `mcp__claude_ai_Notion__notion-update-page` with `command: update_content`. Target the last `## Video Demo\nComing soon\n## SDK Changelogs` sequence as the `old_str` anchor (unique because SDK Changelogs appears only once).

---

### Step 7 — Update Asana for newly added tasks

For each task that was successfully added to Notion in Step 6, do both of the following in parallel per task:

**A. Move to Completed section**

Use `mcp__claude_ai_Asana__update_tasks` with:
```json
{
  "task_id": "<task GID>",
  "memberships": [{"project": "1213848374258762", "section": "1213836732664072"}]
}
```

**B. Add a comment**

Use `mcp__claude_ai_Asana__add_comment` with:
```
task_id: <task GID>
text: "Added to release notes ✓\n\n<Notion page URL>"
```

Use the full canonical Notion page URL (e.g. `https://www.notion.so/sardine/April-2026-Release-Notes-32dd52e0dd8b8093a239e635c47160ed`).

Do not move or comment on tasks that were already present in Notion (skipped tasks).

---

### Step 8 — Report results

Print a full summary with three sections:

---

**Sync results**

```
Added X new entries (moved to Completed in Asana + commented):
- Task name 1
- Task name 2

Already present (skipped):
- Task name A
- Task name B
```

---

**⚠️ Release Month issues** (only shown if there are problems)

| Task | Release Month in Asana | Expected |
|------|----------------------|----------|
| Task name | April 2025 | April 2026 |
| Task name | (not set) | April 2026 |

If all tasks have the correct Release Month, print: ✓ All Release Month values match.

---

**⚠️ Missing video demos** (only shown if there are entries without videos)

- Feature name 1
- Feature name 2

If all entries have videos, print: ✓ All entries have video demos.
