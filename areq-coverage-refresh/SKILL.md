---
name: areq-coverage-refresh
description: Re-run the Sardine EMV 3DS AReq → Customers API field coverage analysis when new information arrives — reads the current Notion analysis doc and sandbox mapping, pulls context from a Slack thread, verifies against sardine-kb, produces a revised analysis, and updates the Notion doc.
argument-hint: "[slack-thread-url] [--preview]"
---

## Task: Refresh the AReq Field Coverage Analysis

The Sardine EMV 3DS AReq → Customers API coverage analysis lives here:
- **Analysis doc (to update):** `https://app.notion.com/p/37dd52e0dd8b8090ae52e93eae2d8954`
- **Sandbox mapping (source of truth for current tier classification):** `https://app.notion.com/p/385d52e0dd8b81ba8a56c3337e3e775b`
- **Slack channel for new context:** `C03QW5FAQHF`

`$ARGUMENTS` may contain:
- A Slack thread URL in the form `https://sardineai.slack.com/archives/<channel>/p<ts>` — use it to pull new context
- `--preview` — synthesize the revised analysis in the conversation but do **not** update the Notion doc

If no Slack thread URL is provided and no new information is stated in the conversation, ask: *"Is there a Slack thread with new context, or should I re-run the analysis purely from the current sandbox mapping?"*

---

## Step 1 — Parse arguments

Extract from `$ARGUMENTS`:
- **slack_thread_url** — optional. If present, parse `channel_id` (between `/archives/` and `/p`) and `message_ts` (the digits after `/p`, inserting a `.` after the 10th digit to form Slack ts format, e.g. `1781193441302659` → `1781193441.302659`).
- **preview_mode** — true if `--preview` is present.

---

## Step 2 — Collect all sources in parallel

Run all four fetches simultaneously.

**2a. Current analysis Notion doc**

Fetch `https://app.notion.com/p/37dd52e0dd8b8090ae52e93eae2d8954` via `notion-fetch`.

Extract:
- Current version number (v1, v2, etc.) from the title
- The three-tier framework summary
- The current priority matrix (Section 4)
- Any open questions or caveats noted

**2b. Sandbox mapping Notion doc**

Fetch `https://app.notion.com/p/385d52e0dd8b81ba8a56c3337e3e775b` via `notion-fetch`.

The sandbox is the authoritative source for the current Tier 1/2/3 classification. Read the full page — it is large (~65k chars) and will be saved to a file; read it in sequential 10k-char chunks until fully consumed. Extract:
- Total field counts per tier
- Any fields that changed tier since the analysis doc was last updated
- Any new sections or footnotes added by the engineering team
- The date the sandbox was last modified (shown in Notion metadata)

**2c. Slack thread (if slack_thread_url provided)**

Call `slack_read_thread` with the parsed `channel_id` and `message_ts`. Read all replies.

Extract:
- Who said what and when
- Any new spec references, spreadsheet updates, or engineering clarifications
- Any explicit corrections to the current analysis doc
- Action items directed at Jayana or Ankit

If no Slack thread URL was provided, skip this step.

**2d. sardine-kb verification**

Run the sardine-kb keyword search pipeline for the key concepts in the analysis:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(echo "$PATH" | tr ':' '\n' | grep -E '/sardine-kb/bin$' | head -1 | sed 's|/bin$||')}"
if [[ -z "$PLUGIN_ROOT" || ! -f "$PLUGIN_ROOT/scripts/lib/keywords.py" ]]; then
  PLUGIN_ROOT="$(find "${HOME}/.claude/plugins/cache" -path '*/sardine-kb/*/scripts/lib' -type d 2>/dev/null | head -1 | sed 's|/scripts/lib$||')"
fi
INDEX="${PLUGIN_ROOT}/skills/sardine-kb/references/index.json"
echo "EMV 3DS AReq Customers API field mapping challengeInd acctInfo merchantRisk" \
  | python3 "${PLUGIN_ROOT}/scripts/lib/keywords.py" \
  | xargs python3 "${PLUGIN_ROOT}/scripts/lib/search.py" 3 sardine-kb "${INDEX}" \
  | CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT}" python3 "${PLUGIN_ROOT}/scripts/lib/formatter.py"
```

Also search for adapter/validation-specific terms:

```bash
echo "issuing adapter buildValidationEnv 3DS customStrings internally computed signals" \
  | python3 "${PLUGIN_ROOT}/scripts/lib/keywords.py" \
  | xargs python3 "${PLUGIN_ROOT}/scripts/lib/search.py" 3 sardine-kb "${INDEX}" \
  | CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT}" python3 "${PLUGIN_ROOT}/scripts/lib/formatter.py"
```

Read the top 1–3 matched files from each query. Prioritise:
- `data-assembly.md` — confirms adapter structure, issuing vs. customer checkpoint
- `internally-computed-signals.md` — confirms what's natively scored vs. customStrings
- Any file matching the new Slack context (e.g. if new info mentions a specific feature or adapter)

---

## Step 3 — Identify what changed

Compare the sandbox mapping (Step 2b) and Slack context (Step 2c) against the current analysis doc (Step 2a).

For each difference, classify it as one of:

| Change type | Example |
|---|---|
| **Tier promotion** | Field moved from Tier 2 → Tier 1 |
| **Tier demotion** | Field moved from Tier 1 → Tier 2/3 |
| **New field added** | EMVCo spec update or new AReq object sub-field |
| **Build gap confirmed** | Engineering confirmed a missing implementation |
| **Build gap resolved** | Engineering shipped the missing implementation |
| **Correction** | Prior analysis had wrong tier or wrong Sardine path |
| **Spec update** | New EMVCo spec version changes field list or semantics |
| **Priority shift** | P0 work completed → shift remaining gaps down |

If no changes are found, state this clearly and do not update the Notion doc. Ask if the user wants a forced re-run anyway.

---

## Step 4 — Produce the revised analysis

Increment the version number (v2 → v3, etc.).

Update the following sections based on what changed. Sections with no changes carry forward unchanged.

### Sections to always re-evaluate:

**Sources block** — update the sandbox date and any new source references from the Slack thread.

**Three-Tier summary table** — update counts if tiers changed.

**Section 1: Tier 1 Native fields** — update the requestor-level and merchantRiskIndicator tables if any field tier changed. Note which changes are corrections from the prior version.

**Section 2: `acctInfo` revised status** — update if any acctInfo sub-field moved tiers or new sub-fields were added in the spec.

**Tier 1 Native caveat (⚠️ section)** — update if the KB reveals new information about the customer checkpoint vs. issuing checkpoint distinction.

**Section 3: New EMVCo fields** — update if the spec version changed or new fields were identified in the Slack thread.

**Section 4: Priority matrix** — re-order or update entries if:
- A P0/P1 item was shipped (promote it to "Well-Covered" and remove from matrix)
- Engineering confirmed a new build gap
- A Tier 2 field was promoted to Tier 1 (remove from matrix)

**Section 5: Spreadsheet corrections** — add any new corrections flagged in the Slack thread.

**FAQ** — carry forward unchanged unless the Slack thread introduces a new concept that warrants a new Q&A entry.

### Writing rules:

- Every change from the prior version must include a `v{N-1} Status` note: what it was before and what it is now (e.g., "❌ was missing → ✅ Tier 1").
- Do not silently overwrite prior analysis — make the delta visible.
- Do not pad sections that haven't changed. "Unchanged from vN" is acceptable as a one-line note.
- Keep the FAQ plain-language and non-technical — it's written for a non-engineer audience.

---

## Step 5 — Update the Notion doc (or preview)

**If `--preview`:** Print the full revised analysis to the conversation in formatted markdown. Do not call `notion-update-page`. Stop here and ask if the user wants to publish.

**Otherwise:**

1. Update the page title to reflect the new version number: `Sardine Customers API — EMV 3DS AReq Field Coverage: Revised Analysis (v{N})`

2. Replace the full page content using `notion-update-page` with `command: replace_content`.

3. Confirm the page URL and note the version number updated.

---

## Step 6 — Final output to conversation

Print a concise summary:

```
## AReq Coverage Analysis Updated → v{N}

**Changes from v{N-1}:**
- <N> tier changes: <list field names and direction, e.g. "acctInfo.suspiciousAccActivity: Tier 2 → Tier 1">
- <N> new fields added (from EMVCo spec update / Slack context)
- <N> build gaps: <confirmed / resolved>
- <N> priority matrix changes: <brief description>
- <N> spreadsheet corrections

**No changes in:** <list sections that carried forward unchanged>

**Notion doc:** <URL>
**Sandbox mapping last updated:** <date from Step 2b>
**New Slack context from:** <thread URL and author, or "none">
```

If there were no changes: state "No changes detected — analysis is current as of v{N}. Notion doc not updated."
