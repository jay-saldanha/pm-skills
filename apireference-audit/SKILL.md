---
name: apireference-audit
description: Audit request/response example coverage across all API reference YAML files in risk-docs, draft missing examples, open multiple focused PRs, update the Notion audit page, and create an Asana ticket.
disable-model-invocation: false
argument-hint: "[--dry-run]"
---

## Task: API Reference Example Coverage Audit

Audit all endpoints in the API reference YAML files in `sardine-ai/risk-docs` at `/private/tmp/risk-docs` (or `/Users/jayana/risk-docs` if that path exists) for missing request/response examples, draft examples for all gaps, open small focused PRs, update the Notion audit page, and log an Asana ticket.

If `--dry-run` is passed as $ARGUMENTS, output the audit report and planned changes but do not create branches, PRs, Notion updates, or Asana tickets.

---

### Step 1 — Locate API reference YAML files

Find all OpenAPI YAML files in the repo that contain endpoint definitions:
```bash
find /private/tmp/risk-docs -name "*.yaml" | xargs grep -l "^paths:" 2>/dev/null
```

Typical files:
- `apireference.yaml`
- `credit-reports.yaml`

---

### Step 2 — Audit every endpoint for example coverage

For each file, extract every path + HTTP method combination. For each operation, check:

**Request example present?**
- POST/PUT/PATCH: `requestBody.content.application/json.examples` block exists (named examples map), OR `requestBody.content.application/json.example` exists (inline singular)
- GET/DELETE with no body: N/A — count as covered if query/path parameters all have `example:` fields

**Response example present?**
- `responses.200.content.application/json.examples` block exists, OR `responses.200.content.application/json.example` exists

Classify each endpoint as:
- **Complete** — both present (or N/A for request on GET/DELETE)
- **Response only** — has response example, missing request example (POST/PUT/PATCH only)
- **Request only** — has request example, missing response example
- **None** — no examples at all

Exceptions (do not flag):
- Endpoints returning HTTP 204 No Content — no response body possible
- GET/DELETE endpoints where all parameters already have `example:` inline values

---

### Step 3 — Print audit report

Output a table grouped by file:

```
## Audit — apireference.yaml

| Endpoint | Method | Request | Response | Gap |
|---|---|---|---|---|
| /v1/blocklists | POST | ❌ | ❌ | Both missing |
| /v1/blocklists | GET  | N/A | ❌ | Response missing |
| /v1/customers  | POST | ✅ | ✅ | — |
...

Summary: X complete, Y response-only, Z request-only, W none
```

---

### Step 4 — Group gaps into PR batches

Group the missing endpoints into small, logically cohesive PRs for easy human review. Suggested groupings (merge related areas):

| PR | Endpoints to cover |
|---|---|
| `credit-reports.yaml` | All endpoints in that file |
| `blocklists-allowlists` | /v1/blocklists/*, /v1/allowlists/* |
| `client-lists` | /v1/client-lists/* |
| `cases-queues-monitoring` | /v1/cases, /v1/queues, /v1/monitoring |
| `decisions-alerts-rules` | /v1/decision-labels/*, /v1/decisions, /v1/alerts, /v1/rules* |
| `openbanking-tracking-transactions` | /open-banking/*, /v1/tracking-links, /v2/transactions |
| `businesses` | Missing PATCH/GET /v1/businesses, /v1/businesses/web360, /v1/businesses/locations/list |
| `fix-missing-requests` | POST endpoints that have responses but no request examples |

Skip any group where all endpoints in that group are already complete.

---

### Step 5 — Draft examples for each endpoint

For each missing endpoint, draft realistic `examples:` blocks that match the existing schema. Follow the exact YAML indentation and formatting style used in the file:

**Request example block** (add after `schema:` under `requestBody.content.application/json`):
```yaml
            examples:
              example-1:
                value:
                  field: value
```

**Response example block** (add after `schema:` under `responses."200".content.application/json`):
```yaml
              examples:
                example-1:
                  value:
                    field: value
```

Use realistic, internally consistent values. For Sardine-specific fields:
- `customerId`: UUIDs like `"7c857f8a-c6a9-474f-85d4-a7f319216d94"`
- `sessionKey`: UUIDs like `"5f06c08e-0793-11eb-adc1-0242ac120002"`
- Timestamps: milliseconds like `1769731200000`, ISO strings like `"2026-04-09T14:30:00Z"`
- Risk levels: `low`, `medium`, `high`, `very_high`
- Currencies: ISO 4217 codes (`USD`, `EUR`)

---

### Step 6 — Create one branch and PR per group

For each non-empty group from Step 4:

```bash
cd /private/tmp/risk-docs
git checkout main
git checkout -b feat/api-examples-<group-name>
# Edit the YAML file(s) to insert examples
git add <file(s)>
git commit -m "docs: add request and response examples for <group description>"
gh pr create \
  --base main \
  --title "docs: add API examples for <group>" \
  --body "$(cat <<'EOF'
## Summary
Adds request and response examples for: <list of endpoints>

## Endpoints covered
- METHOD /path — what was added
...

## Notes
- Examples are drafted from the existing schema definitions
- Values use realistic Sardine-style data

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Collect each PR URL as you go.

---

### Step 7 — Update the Notion audit page

Fetch the current state of the audit page:
- Page ID: `33dd52e0dd8b800abc1cce5c2653ea3c`
- URL: https://www.notion.so/sardine/API-References-Audit-33dd52e0dd8b800abc1cce5c2653ea3c

Use `mcp__claude_ai_Notion__notion-update-page` with `command: replace_content` to write a structured audit report including:
- Audit date (today's date)
- Files audited
- Summary counts table (complete / response-only / request-only / none)
- Table of endpoints that were already complete (no changes needed)
- Section per PR with: PR link, list of endpoints covered, what was added
- Remaining notes (endpoints that are intentionally skipped with reason)

---

### Step 8 — Create an Asana ticket

Create a ticket in the Technical Writing Requests project (GID: `1208751645869782`), Inbox section (GID: `1208751645869784`).

Use `mcp__claude_ai_Asana__create_task_preview` followed by `mcp__claude_ai_Asana__create_task_confirm`.

Task details:
- **Name:** `API Reference YAML audit — add missing request/response examples`
- **Description:** Summary of the audit findings, list of PRs with links, link to the Notion report, and next steps (review + merge PRs, verify examples against production)
- **Project:** Technical Writing Requests (`1208751645869782`)
- **Section:** Inbox (`1208751645869784`)
- **Writing Request Type custom field:** API Reference (enum option GID `1208833810135761`)
  - Field GID: `1208751647138263`

---

### Step 9 — Output final summary

Print a summary table:

```
## API Reference Audit — Complete

| PR | Endpoints | Status |
|---|---|---|
| #NNNN feat/api-examples-credit-reports | 6 | Created |
| #NNNN feat/api-examples-blocklists-allowlists | 8 | Created |
...

Notion page: https://www.notion.so/sardine/API-References-Audit-33dd52e0dd8b800abc1cce5c2653ea3c
Asana ticket: <link>
```
