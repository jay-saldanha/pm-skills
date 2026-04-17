---
name: nps-synthesize
description: Phase 2 of the NPS pipeline — Synthesize raw NPS responses (from /nps-collect) into thematic buckets with severity signals. Run after /nps-collect.
---

## Task: Synthesize NPS Feedback into Themes

Using the raw NPS response data collected in the previous step (from `/nps-collect`), analyze and group feedback into meaningful themes.

### Steps

1. **Compute NPS score**:
   - Promoters = scores 9–10
   - Passives = scores 7–8
   - Detractors = scores 0–6
   - NPS = (% Promoters) − (% Detractors)
   - Report: total responses, # promoters, # passives, # detractors, NPS score

2. **Extract qualitative feedback** — only use responses that have a non-trivial comment.

3. **Assign each comment to a theme bucket**. Default taxonomy (add new buckets as needed):
   - **Performance / Speed** — slow loads, timeouts, lag
   - **Real-time / Auto-refresh** — need live updates without manual refresh
   - **UX Complexity / Navigation** — too many clicks, hard to find things, confusing flows
   - **Data Accuracy** — wrong numbers, stale data, not capturing correctly
   - **Reporting / Analytics** — need better exports, charts, date pickers, precision
   - **Support** — needs better Sardine support responsiveness
   - **Missing Feature** — specific feature gap called out
   - **Positive** — explicit praise (track separately)

4. **For each theme**, output:
   - Count of mentions
   - Severity: `Blocking` (score 0–2 + complaint), `Painful` (score 3–6 + complaint), `Nice-to-have` (score 7–9 + complaint)
   - Top 2–3 verbatim quotes with author email domain and score

5. **Flag silent detractors** — accounts with multiple scores of 0–2 but no qualitative comment. List them by email domain with count of low scores.

6. **Output a theme table**:
   `| Theme | Mentions | Severity | Accounts | Sample Quote |`

Store synthesized themes in context — they will be used by `/nps-notion-report`, `/nps-pylon-map`, and `/nps-pfrs`.
