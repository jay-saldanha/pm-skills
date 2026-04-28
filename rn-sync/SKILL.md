---
name: rn-sync
description: Sync newly moved "In Progress" tasks from the Asana Release Notes project to the current month's Notion release notes page. Adds new entries in the standard release notes format; skips tasks already present.
disable-model-invocation: false
argument-hint: "[notion-page-url]"
---

## Task: Sync Asana In Progress → Notion Release Notes

Check the Asana Release Notes project "In Progress" section and add any new tasks to the Notion release notes page, following the established entry format.

**Asana project:** Release Notes  
**Asana project GID:** `1213848374258762`  
**In Progress section GID:** `1213836732664070`  
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

---

### Step 2 — Fetch data in parallel

Run both simultaneously:

**A. Asana In Progress tasks**

Use `mcp__claude_ai_Asana__get_tasks` with:
- `section`: `1213836732664070`
- `opt_fields`: `name,notes,assignee`

The result may be very large — save it and use `jq` to extract just `gid`, `name`, and `notes` per task.

**B. Notion page content**

Use `mcp__claude_ai_Notion__notion-fetch` on the resolved Notion page URL.

---

### Step 3 — Identify new tasks

From the Notion page content, collect all existing `## ` heading titles (these are feature entry names already on the page).

For each Asana task, check whether a heading closely matching its name already exists in the Notion page:
- Strip tags like `[P0]`, `[P1]`, `[Swan]`, etc. from the Asana task name before comparing
- Use case-insensitive substring matching
- If a match is found → skip (already added)
- If no match → mark as new

If all tasks are already present, report that and stop.

---

### Step 4 — Enrich new tasks (optional, run in parallel)

For any new task whose `notes` contain a Notion URL, fetch that Notion page to get richer content for the release notes entry.

---

### Step 5 — Add new entries to Notion

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

Insert all new entries before the `## SDK Changelogs` section (or at the end of the page if that section doesn't exist).

Use `mcp__claude_ai_Notion__notion-update-page` with `command: update_content` and a single `content_updates` array. Target the last `## Video Demo\nComing soon\n## SDK Changelogs` sequence as the `old_str` anchor (unique because SDK Changelogs appears only once).

If there is no SDK Changelogs section, append to the end of the page.

---

### Step 6 — Report results

Print a brief summary:

```
Added X new entries to [Page Title]:
- Task name 1
- Task name 2
...

Already present (skipped):
- Task name A
- Task name B
```

If no new tasks were found, say so clearly.
