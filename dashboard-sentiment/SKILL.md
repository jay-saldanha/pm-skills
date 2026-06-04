---
name: dashboard-sentiment
description: Weekly customer sentiment scan for Investigative Tools — pulls signals from Pylon, Asana, Notion, and Slack; synthesizes into themes with PRD-ready problem statements; creates a Notion report under "Client Feedback and Surveys" and sends a Slack DM. Run Mondays via /schedule.
argument-hint: "[--preview]"
---

## Task: Investigative Tools Weekly Customer Sentiment

Scan the last **14 days** of customer signals about Sardine's **Investigative Tools** (the fraud/compliance analyst dashboard). Synthesize into themes. Write a Notion report. Send a Slack DM summary.

If `$ARGUMENTS` contains `--preview`, output the full synthesis and page content as text but **do not** create the Notion page or send the Slack DM.

---

### Scope — Investigative Tools only

Only include signals clearly about these surfaces. Discard anything else.

**In scope:**
- Dashboard, Case Management, Alert queues / Alert Views, Customer Profile (incl. 2.0)
- Analytics Home, Connections graph, SAR/CTR filing
- Feature Investigator, Data Dictionary, Notification Center, Custom Widgets, Unified Transaction Table

**Out of scope:** Rules Engine, SDK, API, onboarding, billing, or surfaces owned by other product teams.

**Internal filter:** Remove any signal authored by a `sardine.ai` email or Slack user. This analysis is customer sentiment only.

---

### Step 1 — Collect (run all four sources in parallel)

Date window: last 14 days.

**Primary search terms** (use for all sources):
`dashboard` • `investigator` • `investigative tools` • `case management` • `alert queue` • `customer profile` • `analytics home`

**Secondary terms** (use if search volume is low, or to broaden Notion/Asana results):
`connections graph` • `SAR filing` • `CTR filing` • `feature investigator` • `data dictionary` • `notification center` • `custom widget`

#### A. Pylon

Call `search_issues` for each primary term. Run all searches in parallel. For each issue returned within the date window:
- Call `get_issue_messages` to get the full conversation thread.
- Record: issue title, customer email domain, key complaint/request text, date, issue URL.
- Skip issues with no customer messages (internal-only tickets).

#### B. Slack

Call `slack_search_public_and_private` for each primary search term. Run all searches in parallel. For each result within the date window:
- Record: message text, author name, channel name, permalink, date.
- Skip messages from `@sardine.ai` Slack users.
- Skip clearly internal threads (e.g. sprint planning, engineering standups). Keep anything from CSM, customer-facing, or external channels.

#### C. Asana

Search tasks modified in the last 14 days on both Investigative Tools boards:
- Dashboard board: project GID `1201546278448560`
- Case Management board: project GID `1206468225727311`

Use `search_tasks` or `get_tasks` per board. For each recently modified task:
- Record: task title, description excerpt, any customer-quoted comments, task URL.
- Focus on tasks labeled or described as customer feedback, bug reports, or feature requests citing a customer.
- Skip internal engineering tasks with no customer reference.

#### D. Notion

Run these in parallel:
1. `notion-query-meeting-notes` — meeting notes from the last 14 days mentioning any primary keyword.
2. `notion-search` — pages mentioning "investigative tools" or "dashboard" updated in the last 14 days.
3. `notion-search` scoped to parent page `310d52e0dd8b80f7a5fdc38380432ef6` (Client Feedback and Surveys) — look for recent NPS notes, QBR summaries, or CSM feedback pages.

For each Notion hit, extract verbatim customer quotes and the source page URL.

---

### Step 2 — Filter and deduplicate

1. **Cross-source dedup:** if the same customer (same email domain) raises the same issue in multiple sources, count it once. Keep both source links in the record.
2. **Noise filter:** drop signals where the keyword matches but the content is clearly not about the product (e.g. "dashboard" used metaphorically, internal process posts).
3. **Internal filter:** remove any remaining sardine.ai signals missed in Step 1.

---

### Step 3 — Synthesize

Group all filtered signals into **5–10 themes**.

For each theme:

**Theme metadata:**
- Title — concrete and specific (e.g. "Alert queue lacks bulk-assignment", not "UX issues")
- Severity — assign one:
  - `Blocking` — customer cannot complete a critical workflow
  - `Painful` — workflow possible but with significant friction or workarounds
  - `Nice-to-have` — improvement request, not blocking
- Mention count with source mix (e.g. "7: 3 Slack, 2 Pylon, 1 Asana, 1 Notion")
- Distinct accounts: number of unique customer email domains

**AM mapping** (run domain lookups in parallel):
1. Extract all unique customer email domains across the theme.
2. Call `search_accounts` with `domain: <domain>` for each domain — run in parallel.
3. For each account found, call `get_user` with the `owner_id` — run in parallel.
4. Record: `| Domain | Account Name | AM Name | AM Email |`

**Verbatim quotes:** 2–3 representative quotes per theme with source permalink.

**PRD-ready problem statement** — write in this exact format:
> *"[User segment] struggle with [specific behavior/task] because [root cause inferred from signals], leading to [observable impact on their workflow or business outcome]."*

**Roadmap mapping** — for each theme, tag it to the closest H1 2026 roadmap item:
- Q1 Foundation: Granular Permissions · Analytics Home · Data Dictionary · Custom Widgets · Unified Transaction Table
- Q2 Transformation: Dashboard 2.0 · Customer Profile 2.0 · Feature Investigator · Alert Views 2.0
- Stretch: Notification Center · 4-Eyes Rules · White Labeling
- Mark `Off-roadmap` if no current item matches — these are prioritization candidates for new PRDs.

---

### Step 4 — Create Notion report

**If `--preview`: print the full page content to the conversation as formatted text. Do not call `notion-create-pages`. Skip to Step 5.**

Create a Notion page using `notion-create-pages`:
- Parent: `310d52e0dd8b80f7a5fdc38380432ef6` (Client Feedback and Surveys)
- Title: `Investigative Tools Sentiment — Week of <today's date, YYYY-MM-DD>`

**Page structure:**

```
[one line]: Sources: Pylon · Slack · Asana · Notion | Window: <date range> | <N> signals · <X> themes · <Y> accounts
> Callout: Customer-only signals. sardine.ai authors filtered out. 14-day window ending <date>.

## Executive Summary
3–5 bullets. Top themes by severity and frequency. Total signal count. Note any Off-roadmap themes.

## Theme Breakdown
Table: Theme | Severity | Mentions | Source Mix | Distinct Accounts | Roadmap Item

## PRD-Ready Problem Statements
One bullet per theme in the format: "[User segment] struggle with…"
This section is the primary input for PRD drafting.

## Verbatim Quotes by Theme
One H3 per theme. Bullet list: quote + markdown link to source.

## Accounts & AMs to Follow Up
Table: Domain | Account Name | AM Name | AM Email | Themes

## Roadmap Mapping
Table: Roadmap Item | Themes Mapped | Signal Count | Recommended Action
(Recommended Action options: Monitor · Investigate · Escalate to PRD)

## Off-Roadmap Signals
Themes tagged Off-roadmap only. One bullet per theme with problem statement and signal count.
If none: note "No off-roadmap themes this week."

## Raw Signals Appendix
Toggle/collapsed block. All source URLs organized by source type (Pylon / Slack / Asana / Notion).
```

Save the Notion page URL in context.

---

### Step 5 — Slack DM summary

**If `--preview`: print the DM text to the conversation. Do not call `slack_send_message`.**

Look up Jayana's Slack user ID via `slack_search_users` with query `jayana.saldanha@sardine.ai` if the DM channel ID is not known. Send a direct message with:

```
Investigative Tools sentiment — week of <date>
<N> signals across <X> themes · <Y> distinct accounts

Top themes:
1. <Theme title> — <Severity>, <N> mentions
2. <Theme title> — <Severity>, <N> mentions
3. <Theme title> — <Severity>, <N> mentions

Full report: <Notion URL>
```

If a Blocking theme is present, add a line at the top:
`⚠ <N> Blocking theme(s) this week — review first.`

---

### Final output

Print a summary block to the conversation:

```
## Dashboard Sentiment Complete

- Window: <start date> → <end date>
- Signals collected: <N> total (Pylon: X · Slack: X · Asana: X · Notion: X)
- After dedup/filter: <N> signals
- Themes identified: <N> (<X> Blocking · <Y> Painful · <Z> Nice-to-have)
- Off-roadmap themes: <N>
- Distinct accounts: <N>
- Notion report: <URL>
- Slack DM: <sent to jayana.saldanha@sardine.ai | preview only>
```
