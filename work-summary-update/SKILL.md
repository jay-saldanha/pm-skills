---
name: work-summary-update
description: Update the Work Summary Tracker Notion page with last month's activity pulled from GitHub, Slack, Asana, and Notion. Appends both a strategic summary and a detailed task log. Run monthly.
---

## Task: Update Work Summary Tracker

Update the Notion page [Work Summary Tracker](https://www.notion.so/sardine/Work-summary-Tracker-2a8d52e0dd8b8018a2dadc6bf8b9f4ad) (page ID: `2a8d52e0dd8b8018a2dadc6bf8b9f4ad`) with a full summary of the previous month's work across GitHub, Slack, Asana, and Notion.

**GitHub user:** `jay-saldanha`
**Slack user ID:** `U07UL71V49X`
**Repo:** `sardine-ai/risk-docs`

---

### Arguments

The user may pass a month in any natural format (e.g. "April", "April 2026", "last month"). If no argument is given, default to the **previous calendar month** relative to today's date.

---

### Steps

#### 1. Determine the date range

Calculate `MONTH_START` (first day) and `MONTH_END` (last day) for the target month in `YYYY-MM-DD` format.

Example: if today is May 5, 2026 and no argument given → `MONTH_START=2026-04-01`, `MONTH_END=2026-04-30`.

---

#### 2. Pull GitHub data (run all three in parallel)

**PRs opened:**
```bash
gh api "search/issues?q=author:jay-saldanha+type:pr+created:MONTH_START..MONTH_END&per_page=50" \
  --jq '.items[] | {title, state, created_at, html_url}'
```

**PRs closed/merged:**
```bash
gh api "search/issues?q=author:jay-saldanha+type:pr+closed:MONTH_START..MONTH_END&per_page=50" \
  --jq '.items[] | {title, state, html_url}'
```

**PRs reviewed (not authored):**
```bash
gh api "search/issues?q=reviewed-by:jay-saldanha+type:pr+updated:MONTH_START..MONTH_END+-author:jay-saldanha&per_page=20" \
  --jq '.items[] | {title, state, html_url}'
```

---

#### 3. Pull Slack data

Search for public channel announcements and key work messages:

```
query: "from:<@U07UL71V49X> after:MONTH_START before:MONTH_END"
channels: #product-feature-updates, #general, #eng-announcement, #product-release-note, #technical-writer-request, #account-management
sort: timestamp asc
limit: 20
include_context: false
```

Focus on messages that announce published content, process changes, or cross-functional coordination. Ignore casual chat.

---

#### 4. Pull Asana tasks

Call `get_my_tasks` with:
- `completed_since`: `MONTH_START`
- `opt_fields`: `gid,name,completed,completed_at,due_on,projects`
- `limit`: 100

Filter to tasks where `completed_at` falls within the target month range.

---

#### 5. Pull Notion activity

Search for pages created or updated in the target month:
```
query: "documentation updates"
query_type: "internal"
filters: created_date_range start_date=MONTH_START end_date=MONTH_END
page_size: 15
```

---

#### 6. Compile the strategic section

Write a strategic month entry using this structure. Frame everything as outcomes and impact, not task lists.

```markdown
## [Month Year]

### What Shipped
[3–5 bullets — new articles and guides published, framed by what they enable for customers or the business. E.g. "Published PayFac Integration Guide — enables payment facilitators to integrate without SE support."]

### Infrastructure & Process
[2–3 bullets — translation fixes, CI improvements, process launches, tooling. Frame as scale or efficiency gains.]

### Customer Communication
[If applicable — Pylon campaigns, RN cycle managed, product blog, NPS work. Frame as reach and retention impact.]

### Cross-functional
[If applicable — notable stakeholder coordination, reviews, triage.]
```

**Framing rules:**
- Lead with outcomes, not actions. "Enables X" not "Published X."
- If a PR batch serves one initiative (e.g. API examples, translations), describe the initiative once — don't list every PR.
- Release Notes: always note it as end-to-end ownership (Notion → GitHub → Tech Docs → Slack → email).
- If output was low this month, focus on depth or quality rather than volume.

---

#### 7. Compile the task log section

Write a detailed task log for personal reference using this structure:

```markdown
## [Month Year]

### GitHub PRs Opened
- [#NNNN](url) — title (state: open/closed)
[list all PRs from step 2, sorted by PR number]

### PRs Reviewed (Not Authored)
- [#NNNN](url) — title
[list from step 2 reviews query]

### Asana Tasks Completed
- Task name (completed date)
[list from step 4, sorted by completed_at]

### Published & Announced (Slack)
- **Mon DD** — Description (channel)
[key public announcements from step 3 only — skip DMs and casual messages]
```

---

#### 8. Fetch the current Notion page

Call `notion-fetch` on page ID `2a8d52e0dd8b8018a2dadc6bf8b9f4ad` to get the current content so you can correctly target the `update_content` insertion points.

---

#### 9. Determine the correct quarter section

Map the target month to its quarter:
- Q1: January, February, March
- Q2: April, May, June
- Q3: July, August, September
- Q4: October, November, December

Find whether that quarter section already exists in the page. Use the heading format `## Q[N] [YEAR] — [Month]` for individual month sections and `## Q[N] [YEAR]` for the quarter header.

---

#### 10. Update the Notion page

Make two separate `update_content` calls:

**Call A — Strategic section:**
- If the quarter section already exists, insert the new month's strategic entry after the last existing month in that quarter (before the next `---` divider).
- If the quarter section does not exist yet, append it before the `## Supporting Numbers` section.
- Update the `## Supporting Numbers` table to reflect the new cumulative totals (increment PR count, article count, etc.).
- Update the `## What's In Flight` section to reflect what moved to "done" and what's new in progress.
- Update the `*Last updated*` footer date.

**Call B — Task log section:**
- Find the `# Task Log (Reference)` section.
- Append the new month's task log entry at the bottom of that section (after the last existing month's log).

---

#### 11. Report back

After both updates succeed, output:
- The month covered
- Count of PRs opened, articles published, Asana tasks completed
- A direct link to the Notion page: https://www.notion.so/sardine/Work-summary-Tracker-2a8d52e0dd8b8018a2dadc6bf8b9f4ad
