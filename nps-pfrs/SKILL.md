---
name: nps-pfrs
description: Phase 6 of the NPS pipeline — Create Product Feature Request (PFR) tasks in Asana from synthesized NPS themes. Previews each task before confirming. Run after /nps-pylon-map.
---

## Task: Create PFR Tasks in Asana from NPS Themes

Using the synthesized themes from `/nps-synthesize` and the account/AM mapping from `/nps-pylon-map`, create PFR tasks in the Asana **PFR's (Product Feature Requests)** project (GID: `1201824753129207`).

### Threshold for creating a PFR
Only create a PFR for a theme if it meets at least one of:
- 3+ qualitative mentions, OR
- 1+ "Blocking" severity mention (score 0–2 with a comment)

### Steps

1. **For each qualifying theme**, call `create_task_preview` with:
   - **Title**: `[PFR] <theme name>` (concise, action-oriented)
   - **Project GID**: `1201824753129207`
   - **Description** (include all of the following):
     ```
     **Theme:** <theme name>
     **Severity:** <Blocking / Painful / Nice-to-have>
     **Mentions:** <count> (<date range>)
     **Accounts affected:** <account name> (AM: <AM name>), ...

     **Customer quotes:**
     - "<quote>" — <email domain> (score: <N>)
     - ...

     **Context:** <1–2 sentence explanation of why this matters and who is affected>

     **Notion report:** <URL from /nps-notion-report>
     ```

2. **Show all previews** to the user before confirming any.

3. **Wait for user approval** — only call `create_task_confirm` after the user confirms they want to proceed. Confirm tasks one at a time or all at once depending on user preference.

4. **After each task is confirmed**, output the Asana task URL.

5. **Update the Notion report** — append the confirmed Asana task URLs to the "Suggested PFRs" section of the Notion report (using `notion-update-page` on the report URL from `/nps-notion-report`).

6. **Final report**: Output a summary table of all PFRs created:
   `| PFR Title | Severity | Accounts | Asana URL |`
