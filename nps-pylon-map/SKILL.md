---
name: nps-pylon-map
description: Phase 4–5 of the NPS pipeline — Map feedback authors to Pylon accounts and identify account managers. Appends AM mapping to the Notion report. Run after /nps-notion-report.
---

## Task: Map NPS Respondents to Pylon Accounts and Identify AMs

Using the email domains from the collected NPS responses, look up accounts and account managers in Pylon, then surface the AM list per theme.

### Steps

1. **Extract unique email domains** from all feedback authors collected in `/nps-collect`. Prioritize:
   - Domains from accounts with qualitative feedback (any theme)
   - Domains with multiple detractor scores (0–2)

2. **Look up each domain in Pylon** using `search_accounts` with `domain: <domain>`. Run all lookups in parallel.

3. **Resolve account owners** — for each account found, call `get_user` with the `owner_id`. Run all lookups in parallel.

4. **Build the mapping table**:
   `| Customer Domain | Account Name (Pylon) | AM Name | AM Email | Themes from NPS |`

5. **Group by AM** — for each AM, list:
   - Which accounts they own that appeared in the NPS data
   - Which themes those accounts raised
   - How many detractor scores (0–2) came from their accounts

6. **Update the Notion report** — use `notion-update-page` to append or fill in the "Accounts & AMs to Follow Up With" table in the report created by `/nps-notion-report`.

7. **Output** the AM mapping table in the conversation so it's available for `/nps-pfrs`.

> No Slack messages or Asana tasks are sent at this stage. This step is informational only.
