---
name: nps-pipeline
description: Run the full NPS feedback → PFR pipeline end-to-end. Chains /nps-collect → /nps-synthesize → /nps-notion-report → /nps-pylon-map → /nps-pfrs in sequence, pausing for review between phases.
argument-hint: "[days-back]"
---

## Task: Run the Full NPS Feedback Pipeline

Run all 5 phases of the NPS pipeline in order. Each phase builds on the previous — data stays in context throughout.

Pass `$ARGUMENTS` (e.g. `30`) to limit collection to the past N days. Omit to collect all available responses.

---

### Phase 1 — Collect
/nps-collect $ARGUMENTS

After collecting, **pause and show** the response count and date range. Confirm before proceeding.

---

### Phase 2 — Synthesize
/nps-synthesize

After synthesizing, **pause and show** the theme table and NPS score. Confirm before proceeding.

---

### Phase 3 — Notion Report
/nps-notion-report

After creating the report, **pause and show** the Notion page URL. Confirm before proceeding.

---

### Phase 4–5 — Pylon Account & AM Mapping
/nps-pylon-map

After mapping, **pause and show** the AM table. Confirm before proceeding.

---

### Phase 6 — Create PFRs in Asana
/nps-pfrs

Preview all PFR tasks first. Wait for explicit user confirmation before creating each one.

---

### Final Output
After all phases complete, output a single summary:

```
## NPS Pipeline Complete

- Responses collected: <N> (<date range>)
- NPS score: <score>
- Themes identified: <N>
- Notion report: <URL>
- PFRs created: <N> (<list of Asana URLs>)
- AMs to follow up: <list>
```
