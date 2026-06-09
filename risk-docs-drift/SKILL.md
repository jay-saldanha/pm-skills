---
name: risk-docs-drift
description: Detect drift between the sardine-kb internal knowledge base and the external risk-docs site — flags stale external pages, missing external coverage, and orphaned pages. Gates every proposed external change through a content-leak filter and requires explicit human sign-off before opening PRs. Writes a Notion drift-audit report and logs an Asana ticket. Mirrors the apireference-audit skill structure.
argument-hint: "[topic-area] [--dry-run]"
---

# risk-docs-drift

Audits the external-facing `risk-docs` Mintlify site (`sardine-ai/risk-docs`) for drift against the internal `sardine-kb` knowledge base. Catches three drift types: stale external pages, missing external coverage, and orphaned pages. Every proposed change to a public doc passes a content-gate (PII / secrets / local-pointers / internal-only markers) and requires explicit human sign-off before a PR is opened.

`$ARGUMENTS` usage:
- `[topic-area]` — scope the run to one topic (e.g. `rules`, `device`, `aml`); matches against KB keywords and risk-docs page paths/titles. Omit to audit all mapped topics.
- `--dry-run` — print the drift report and proposed changes; do not create branches, PRs, Notion updates, or Asana tickets.

---

## Step 1 — Resolve both sources

### 1a. Pull risk-docs to HEAD

```bash
cd /Users/jayana/risk-docs && git pull origin main
```

If this fails (uncommitted changes, offline), warn but continue — note the SHA and age of the current checkout in the report.

Capture the current SHA for the report:
```bash
RISK_DOCS_SHA=$(cd /Users/jayana/risk-docs && git rev-parse --short HEAD)
```

### 1b. Resolve KB references dir

Use the same resolution order that `contribute` and `search-keywords` use:

```bash
# 1. Env var (set by plugin loader)
if [[ -n "$CLAUDE_PLUGIN_ROOT" ]]; then
  KB_REFS="${CLAUDE_PLUGIN_ROOT}/skills/sardine-kb/references"

# 2. Derive from $PATH (claude binary → plugins dir)
elif command -v claude &>/dev/null; then
  CLAUDE_BIN=$(command -v claude)
  PLUGIN_BASE=$(python3 -c "import os,sys; p=sys.argv[1]; print(os.path.join(os.path.dirname(os.path.dirname(p)), 'plugins', 'cache', 'sardine-common-ai-plugins', 'sardine-kb'))" "$CLAUDE_BIN") 2>/dev/null
  KB_VERSION=$(ls "$PLUGIN_BASE" 2>/dev/null | sort -V | tail -1)
  KB_REFS="${PLUGIN_BASE}/${KB_VERSION}/skills/sardine-kb/references"

# 3. Known cache path (fallback)
else
  KB_VERSION=$(ls ~/.claude/plugins/cache/sardine-common-ai-plugins/sardine-kb/ 2>/dev/null | sort -V | tail -1)
  KB_REFS="$HOME/.claude/plugins/cache/sardine-common-ai-plugins/sardine-kb/${KB_VERSION}/skills/sardine-kb/references"
fi

if [[ ! -d "$KB_REFS" ]]; then
  echo "ERROR: sardine-kb references dir not found at $KB_REFS"
  exit 1
fi
KB_INDEX="${KB_REFS}/index.json"
```

### 1c. Optional: locate sardine-all for citation tie-breaking

```bash
SARDINE_ALL="/Users/jayana/sardine-all"
if [[ ! -d "$SARDINE_ALL" ]]; then
  echo "WARNING: sardine-all not found at $SARDINE_ALL — citation tie-breaking unavailable. Continuing."
  SARDINE_ALL=""
fi
```

### 1d. Skill's own references dir (topic map)

```bash
SKILL_DIR="$HOME/.claude/skills/risk-docs-drift/references"
TOPIC_MAP="${SKILL_DIR}/topic-map.md"
```

---

## Step 2 — Load or build the topic map

The topic map is a persistent, human-curated file that records which KB docs have external-facing counterparts in risk-docs and whether they're externally relevant. It is the single most important artifact this skill creates — the mapping quality drives everything else.

### 2a. If `topic-map.md` exists

Read it. Parse the rows from the `## Mapping` table. Apply any topic-area scope from `$ARGUMENTS`. Skip to Step 3.

### 2b. If `topic-map.md` does NOT exist — derive a draft

1. Read `${KB_INDEX}` (JSON array of 80 objects, each with `file-path`, `keywords`, `body_keywords`, `summary`).
2. Read the English nav from `/Users/jayana/risk-docs/docs.json`: extract all `pages[]` path strings under `navigation.languages[0]` (the `en` entry). For each, read its frontmatter `title` and `description` from `guides/<path>.mdx`.
3. For each KB doc, fuzzy-match its `summary` and `keywords` against risk-docs page `title`/`description` values. Match criteria: ≥2 shared significant keywords (ignore stop words), or a strong semantic match on the summary. Group by KB topical area (rules-engine, device/ML, AML/compliance, case management, integrations/SDK, API surface, dashboard/UI).
4. Classify each KB doc as:
   - `Y` (externally relevant) — the topic is customer-facing (e.g. rules-engine behavior, SDK contract, API endpoints, AML thresholds)
   - `N` (internal only) — the topic is purely operational or infrastructure (e.g. vendor-failover internals, infra-modules, GCP key management, deployment pipelines)
   - `partial` — the topic has a customer-facing surface but also internal-only sections (e.g. `apis.md` covers both the public swagger spec and internal-only endpoints)

   **Heuristics for N:**
   - Doc body contains `internal only`, `internal-only`, `not in the swagger`, `Sardine-internal`, or `not exposed externally`
   - `keywords:` contains `infrastructure`, `infra`, `deployment`, `terraform`, `GCP`, `firewall`, `secrets`, `kms`
   - The only citations in the doc are to `cmd/`, `pkg/`, `internal/` paths — no `v1/` API paths or customer-observable fields

5. Draft the map as a markdown table (format: Step 2c).
6. Present the draft to the user via `AskUserQuestion`: "I derived this draft topic map from the KB index and risk-docs nav — does this look right? You can say 'looks good', call out rows that are wrong, or ask me to add/remove entries." Let the user respond freely.
7. After confirmation, also ask: "Is there a Notion page where I should write drift reports, or should I create a new one?" Save the answer for Step 7.
8. Write the confirmed map to `${TOPIC_MAP}`.

### 2c. topic-map.md format

```markdown
# sardine-kb → risk-docs topic map

> **Last updated:** YYYY-MM-DD
> **Notion drift report page ID:** <id or PENDING>

## Mapping

| KB doc | KB summary (excerpt) | risk-docs page(s) or section | Externally relevant? | Notes |
|---|---|---|---|---|
| rules-engine.md | Rule DSL, shadow rules/models… | guides/knowledge-base/rule-editor/* | Y | Full topic covered |
| vendor-failover.md | Waterfalls, timeouts… | — | N | Purely internal orchestration |
| apis.md | External + internal-only endpoints | guides/api-reference/* | partial | Only §External API sections are public |
| sdk-contract.md | SDK payload contract… | guides/integration/risk-sdk/* | partial | §Internal-only response flag must not be included |
| anomaly-detection.md | ML anomaly scoring… | guides/knowledge-base/ai-and-machine-learning/* | Y | snapshot — verify counts |
…

## Instructions for future runs
- Add new KB docs as rows when sardine-kb is updated.
- When a new risk-docs section is added, check if it maps to an existing KB doc.
- `partial` rows: read the KB doc's inline `internal only` markers to decide which sections feed external proposals.
```

---

## Step 3 — Detect the three drift types

For each row in the topic map with `Externally relevant? = Y or partial`, read both the KB doc and the mapped risk-docs page(s) in full.

### 3a. Stale external pages

For each mapped pair, compare concrete claims in the risk-docs page against the KB doc:
- Enum values (risk levels, status codes, field names)
- Documented limits, thresholds, or counts
- Endpoint paths, method signatures, request/response fields
- Feature behavior descriptions (what a flag does, how a rule fires, what a signal returns)

When the two disagree:
1. Identify the exact KB doc line making the contrary claim.
2. If `sardine-all` is available, open the cited `file.go:line` from the KB doc to confirm the KB claim is grounded in live code. Note `source-confirmed: yes/no/unable`.
3. Record a finding: `{ page, claim_in_risk_docs, kb_evidence, kb_file:line, source_confirmed, severity }`.
   - Severity: `high` = factually wrong behavior the customer would act on; `medium` = outdated terminology or count; `low` = minor phrasing difference.

For `partial` rows: read the KB doc's inline `internal only` markers (look for text matching `internal[-\s]only`, `internal-only`, `not exposed externally`, `Sardine-internal only`) to mark the boundary. Claims from internal-only sections are **excluded from comparison entirely** — they are not candidates for external pages. Only compare claims from the public-facing sections.

For `snapshot`-tagged KB docs (`snapshot` in the doc's `keywords:`): note the staleness risk in the finding and set `source_confirmed` based on a manual spot-check of the cited code line.

### 3b. Missing external coverage

For each row where `Externally relevant? = Y` and `risk-docs page(s) = —` (no mapped page):
1. Record a candidate: `{ kb_doc, kb_summary, suggested_risk_docs_section, rationale }`.
2. Suggested section is derived from the KB doc's topic area → nearest risk-docs tab/group in `docs.json`.
3. Exclude any candidate whose KB doc contains only internal-only claims (after applying the boundary from §3a).

### 3c. Orphaned external pages

Identify risk-docs pages (English `guides/`) that have **no** corresponding KB row in the topic map:
1. List all English page paths from `docs.json`.
2. Cross-reference against the `risk-docs page(s)` column in the topic map.
3. Uncovered pages are orphan candidates.
4. Filter out pages that are legitimately external-only with no internal counterpart: `guides/release-notes/*`, `guides/api-changelog/*`, `guides/sdk-changelog/*`, `guides/customer-training-academy/*` — these are expected orphans.
5. Record the remainder: `{ page, title, description }`. Do **not** propose deleting or editing them — orphan findings are report-only, for human review.

---

## Step 4 — Print the drift report

Output three tables. Keep each finding to one row; evidence in the Notes column. End with a summary count line.

```
## Risk-Docs Drift Report — YYYY-MM-DD

**KB SHA:** (plugin version e.g. 0.4.1)
**risk-docs SHA:** <sha>
**Topic scope:** all / <topic-area>
**sardine-all available:** yes / no

---

### Stale External Pages

| risk-docs page | Claim in risk-docs | KB evidence | KB doc:line | Source confirmed? | Severity |
|---|---|---|---|---|---|
| guides/knowledge-base/rule-editor/rule-basics.mdx | "risk levels are: low, medium, high" | "low, medium, high, very_high" | rules-engine.md:47 | yes (rules.go:99) | high |
…

Summary: N stale findings (X high / Y medium / Z low)

---

### Missing External Coverage

| KB doc | Topic | Suggested section in risk-docs | Rationale |
|---|---|---|---|
| anomaly-detection.md | ML anomaly scoring for transactions | guides/knowledge-base/ai-and-machine-learning/ | No page describes the anomaly signal logic customers can see in the dashboard |
…

Summary: N missing coverage gaps

---

### Orphaned External Pages (report only — no auto-edit)

| risk-docs page | Title | Notes |
|---|---|---|
| guides/knowledge-base/compliance/aml-overview.mdx | AML Overview | No KB doc covers AML at this level; may be legitimately external-only or may need a KB counterpart |
…

Summary: N orphaned pages
```

---

## Step 5 — Content-gate + human confirm

**Run this step for every stale-fix and every new-page candidate. Skip for orphans (report-only).**

This is a conversation, not a one-shot reject. Surface findings one at a time and let the user decide. Stop the clock between prompts — do not auto-batch.

### 5a. Exclude internal-only sections (pre-gate)

Before running any scan, strip all sections of the KB source text that are marked internal-only (prose containing `internal only`, `internal-only`, `Sardine-internal only`, `not exposed externally`, `not in the swagger`, `Unleash is Sardine-internal`). Only the remaining text feeds the scan and any proposed external change. Log what was stripped in the report.

### 5b. Company-wide relevance check

The question here is flipped from `contribute`: "Does this proposed external-docs change describe customer-observable behavior, a public API, or product functionality — not Sardine-internal implementation details?" If the answer is no → drop the proposal, log it as `filtered: not customer-facing`. Do not ask the user; just drop it.

### 5c. No local pointers scan

Scan the KB-sourced text for paths or URLs that only resolve internally:

```text
/Users/[^/[:space:]]+/
/home/[^/[:space:]]+/
~/(?!sardine/)
localhost:[0-9]+
https?://[^/[:space:]]+\.local/
github\.com/[^/]+/sardine-[^/]+/tree/[^/]+(?!main)
\bpkg/[a-z]                        # Go internal package paths
\bcmd/[a-z]                         # Go cmd paths
sardine-all/src/                    # monorepo-relative paths
```

For each match, show the user: "Found `<match>` on line N — this is an internal path. Options: redact / generalize / drop this proposal / fix manually." Never include internal source-code paths in an external doc.

### 5d. No PII scan

Same as `contribute` Step 4c. Scan for individual `firstname.lastname@sardine.ai` emails, phone numbers, Slack DM links, customer names tied to real merchants. Surface each one-by-one; prompt `redact to role label / keep (public author) / drop proposal / fix manually`.

### 5e. No secrets scan (hard-stop)

```text
sk_live_[A-Za-z0-9]+
AKIA[0-9A-Z]{16}
ghp_[A-Za-z0-9]{36}
glpat-[A-Za-z0-9_-]{20}
xox[abprs]-[A-Za-z0-9-]+
-----BEGIN [A-Z ]*PRIVATE KEY-----
[A-Za-z0-9_-]*\.googleapis\.com
```

If a secret pattern is found, the entire proposal is **immediately halted**: "Found a secret pattern at line N — this cannot go into an external PR. Only options: replace with `${VAR_NAME}` placeholder or fix manually." If the user picks "fix manually", re-scan before continuing.

### 5f. Explicit human sign-off (mandatory)

After all scans pass, present each proposed change to the user:

> **Proposed change:** [stale fix | new page]
> **Target:** `guides/<path>.mdx`
> **Change summary:** <one paragraph>
> **KB source:** `<kb-doc.md>` (section: `<heading>`)
> **Source confirmed?** yes/no/unable
>
> Approve this change? (yes / skip / fix manually)

Do not open a PR for any change that does not receive an explicit `yes`.

---

## Step 6 — Draft focused PRs in risk-docs

Group approved changes by topic area into small, logically cohesive PRs (mirror `apireference-audit` Step 4 logic). Each PR covers one section or one closely related cluster.

For each group with at least one approved change:

```bash
cd /Users/jayana/risk-docs
git checkout main
git pull origin main
git checkout -b docs/drift-<area>
```

**For stale fixes:** Edit the existing `.mdx` file. Update only the specific claim(s) flagged — do not rewrite surrounding copy. Follow risk-docs style: second person, active voice, sentences <25 words, sentence-case headings (see `doc-style-guide.mdx`).

**For new pages (missing coverage):** Create `guides/<suggested-section>/<kebab-case-name>.mdx` with:
```yaml
---
title: "<Title Case>"
description: "<One sentence, imperative or noun phrase>"
groups: ['risk_doc']
---
```
Register the new page in `docs.json` under the appropriate group — **pages not in `docs.json` are invisible**. Match the existing nesting depth and tab structure.

**English only:** Do not touch `es/`, `ja/`, or `pt-BR/` trees. CI auto-translates any changed English `.mdx` file via `translate-mdx.yml`.

Commit and open the PR:
```bash
git add <file(s)> docs.json
git commit -m "docs: fix drift in <area> — <one-line summary>"
gh pr create \
  --base main \
  --title "docs: fix drift in <area>" \
  --body "$(cat <<'EOF'
## Summary
<1-3 bullet points>

## Drift findings addressed
| Finding | Type | Severity |
|---|---|---|
| <claim> | stale | high |
…

## KB source
- `<kb-doc.md>` (sardine-kb v<version>)
- Source confirmed against `sardine-all` <sha or "not verified">

## Test plan
- [ ] `npx mintlify broken-links` — passes
- [ ] `node scripts/validate-docs-json.js` — passes
- [ ] New pages appear in local `mintlify dev` preview
- [ ] No es/ja/pt-BR files touched

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Collect each PR URL.

---

## Step 7 — Notion drift report

### 7a. First run (no page ID in topic-map.md)

Create a new Notion page titled "Risk-Docs Drift Audit" in the sardine workspace. Use `mcp__claude_ai_Notion__notion-create-pages`.

Persist the returned page ID into `topic-map.md` under `> **Notion drift report page ID:**`.

### 7b. Subsequent runs

Use `mcp__claude_ai_Notion__notion-update-page` with `command: replace_content` to overwrite the page with the latest report.

Page content sections:
1. **Audit metadata** — date, KB version, risk-docs SHA, scope, sardine-all available
2. **Stale pages table** — same as Step 4 printout
3. **Missing coverage table** — same as Step 4
4. **Orphaned pages table** — same as Step 4
5. **PRs opened** — table: PR link, topic area, change type, merge status (open at time of audit)
6. **Filtered proposals** — what the content-gate removed and why (transparency log)
7. **Notes for next run** — any topic-map rows that need human follow-up

---

## Step 8 — Asana ticket

Create a ticket in the Technical Writing Requests project using `mcp__claude_ai_Asana__create_task_preview_v4` followed by `mcp__claude_ai_Asana__create_task_confirm`.

Task details:
- **Name:** `Risk-docs drift audit — <YYYY-MM-DD> (<topic-area or 'all'>)`
- **Description:** Summary of the three drift-type counts, list of PRs with links, Notion report link, and next steps (review + merge PRs, check orphan list, re-run after merges)
- **Project:** Technical Writing Requests (`1208751645869782`)
- **Section:** Inbox (`1208751645869784`)
- **Writing Request Type custom field GID:** `1208751647138263` — use the Documentation enum option if the run covered narrative docs; use API Reference if focused on API surface

---

## Step 9 — Final summary

Print a summary table:

```
## Risk-Docs Drift Audit — Complete

### Results
| Drift type | Found | Approved for PR | Filtered (gate) | Report-only |
|---|---|---|---|---|
| Stale pages | N | N | N | — |
| Missing coverage | N | N | N | — |
| Orphaned pages | N | — | — | N |

### PRs opened
| PR | Area | Type | URL |
|---|---|---|---|
| docs/drift-rules | rules | stale + new page | https://github.com/sardine-ai/risk-docs/pull/NNN |
…

Notion: <url>
Asana: <url>
```

---

## When NOT to run this skill

| Situation | What to do instead |
|---|---|
| You want to add a *new* internal KB doc | `/sardine-kb:contribute` |
| You want to update an existing KB doc only | `Edit` the KB `.md` directly, run `generate-index.sh`, bump version, PR. |
| You want to audit API *examples* (not content accuracy) | `/apireference-audit` |
| You want to see what risk-docs pages are new this month | `/risk-docs-new-pages` |
| You only want the drift report without PRs/Notion/Asana | Add `--dry-run` |
