---
name: nps-collect
description: Phase 1 of the NPS pipeline — Read all survey responses from #product-fruits-surveys in Slack. Outputs raw messages (author, score, qualitative comment, timestamp) ready for synthesis.
argument-hint: "[days-back]"
---

## Task: Collect NPS Survey Responses from Slack

Read survey responses from the `#product-fruits-surveys` Slack channel (channel ID: `C08NK3WTNBE`).

### Steps

1. **Read the channel** using `slack_read_channel` with `channel_id: C08NK3WTNBE`, `limit: 100`, `response_format: concise`.
   - If `$ARGUMENTS` is provided (e.g. `30`), only collect responses from the past N days by computing an `oldest` unix timestamp.
   - Default: collect all available messages (paginate until no more pages).

2. **Paginate** — if `pagination_info` indicates more messages, call `slack_read_channel` again with the returned cursor. Continue until all pages are retrieved.

3. **Parse and extract** from each Product Fruits NPS Survey message:
   - Author name and email
   - NPS score (0–10)
   - Qualitative comment (if present — check all follow-up question fields)
   - Timestamp

4. **Filter out noise** — skip messages that are:
   - Channel join/leave notifications
   - Notion AI summaries or bot messages
   - Qualitative comments that are clearly gibberish (single letters, "NA", "q", etc.)

5. **Output a structured list** with columns: `| Timestamp | Author | Company (email domain) | Score | Comment |`

6. **Report totals**: total responses collected, date range covered, number with qualitative comments.

Store this data in context — it will be used by `/nps-synthesize` in the next step.
