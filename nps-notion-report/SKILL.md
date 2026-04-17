---
name: nps-notion-report
description: Phase 3 of the NPS pipeline — Create a Notion synthesis report from themed NPS feedback (from /nps-synthesize). Files under "Client Feedback and Surveys". Run after /nps-synthesize.
---

## Task: Create NPS Synthesis Report in Notion

Using the synthesized theme data from `/nps-synthesize`, create a Notion page under the **Client Feedback and Surveys** section.

### Parent page
`310d52e0dd8b80f7a5fdc38380432ef6` (Client Feedback and Surveys)

### Steps

1. **Determine the report title** — format: `NPS Survey Synthesis — Dashboard Feedback (<Month> <Year>)` based on the date range of responses collected.

2. **Create the Notion page** using `notion-create-pages` with `parent.page_id: 310d52e0dd8b80f7a5fdc38380432ef6`.

3. **Page structure** (in order):

   ```
   Source, period, and total response count (one line)
   > Callout: how to use the doc

   ## Executive Summary
   Top 3 themes by frequency, 2–3 sentences each.

   ## Theme Breakdown
   Table: Theme | Mentions | Severity | Accounts | AM

   ## Verbatim Quotes by Theme
   One H3 per theme, bullet list of quotes with author domain and score.

   ## High-Priority Detractor Accounts (0–2, No Comment)
   Table: Account | Domain | # of low scores | AM

   ## Accounts & AMs to Follow Up With
   Table: AM name | Email | Accounts | Themes
   > Note: no outreach sent yet

   ## Suggested PFRs
   Numbered list linking to Asana tasks (to be filled in by /nps-pfrs)
   ```

4. **Output** the Notion page URL so it can be linked from Asana PFRs in the next step.

Store the Notion page URL in context — it will be referenced by `/nps-pfrs`.
