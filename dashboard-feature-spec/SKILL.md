---
name: dashboard-feature-spec
description: Turn an Asana feature-request task into a PM-quality feature requirements doc — fetches the task, investigates current product behavior via Explore agents and the sardine-kb, and produces a structured Current State / Requirements / Acceptance Criteria / Out of Scope spec. No code references. Output to conversation only.
argument-hint: "[asana-task-url-or-id]"
---

## Task: Dashboard Feature Requirements from Asana Task

Given an Asana task from the Dashboard project, investigate the current product behavior and produce a structured feature requirements document suitable for handing off to engineering. The spec should define **what** the feature must do, not **how** to build it.

**Pipeline position:** This is Step 2 of a two-step PM workflow. Run `/pfr-triage` first to score and rank untriaged PFRs; it emits a ready-to-run handoff list with the exact commands to invoke this skill. If a PFR's Asana `Priority` field is still TBD or stale (not yet updated after triage), the recommended priority is in the `/pfr-triage` handoff comment — use that value and note the discrepancy in the spec.

`$ARGUMENTS` is an Asana task URL or bare numeric GID. If omitted, ask the user for one before proceeding.

---

### Step 1 — Parse the task reference

Extract the Asana task GID from `$ARGUMENTS`.

- If it looks like a full permalink (contains `/task/<gid>`), extract the numeric GID from between `/task/` and the next `/` or `?`.
- If it is a bare number, use it directly.
- If `$ARGUMENTS` is empty or unparseable, ask: "Please paste the Asana task URL or GID."

---

### Step 2 — Fetch the Asana task

Call `mcp__claude_ai_Asana__get_task` with:
```json
{
  "task_id": "<extracted-gid>",
  "include_comments": true,
  "include_subtasks": true
}
```

Extract and hold for synthesis:
- **Task name** — the feature title
- **notes** — the task description (core ask)
- **comments** — any scope clarifications added by PM or eng
- **Priority** custom field display value — if the value is TBD or empty, check whether a recommended priority was passed in from a `/pfr-triage` handoff comment (e.g. `# → High · Size M`). If so, use the recommended value and note: *"Priority not yet updated in Asana; using /pfr-triage recommendation: High."*
- **ProdEng Pod** custom field display value
- **Product Area** custom field display value (multi-enum)
- **Customer** — from the task name prefix (e.g. `[RockWallet]`) or `Customers Requesting` custom field
- **Assignee** name

Summarize the ask in one sentence before proceeding.

---

### Step 3 — Investigate current product behavior (run both in parallel)

**3a. Explore agent — understand what the dashboard currently does**

Launch an Explore agent over `/Users/jayana/device-dashboard` with the goal of understanding **existing product behavior**, not code structure. The agent should answer these questions using the codebase as a source of truth:

- Does this feature or a partial version of it already exist in the product?
- What does the user currently see or experience in this area of the dashboard?
- Is this behavior the same for all clients, or does it vary by client/configuration?
- Are there any visible limitations today (e.g. missing data, missing UI controls, hardcoded values)?
- If the task involves audit logs or events: what events are currently emitted, and are they already surfaced to users?

Report findings as **observable product behavior**, not code locations. For example: "The dashboard currently shows X but does not allow Y." No code snippets or file paths in the output.

**3b. sardine-kb keyword search — backend/data context**

Run the sardine-kb keyword search pipeline using terms from the task name and description to understand:

- What backend data or APIs are relevant to this feature area?
- Are there known constraints (data availability, latency, access controls) that would affect what the feature can do?
- Is there relevant Sardine infrastructure (rules engine, ML signals, case management, etc.) that this feature should surface or integrate with?

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(echo "$PATH" | tr ':' '\n' | grep -E '/sardine-kb/bin$' | head -1 | sed 's|/bin$||')}"
if [[ -z "$PLUGIN_ROOT" || ! -f "$PLUGIN_ROOT/scripts/lib/keywords.py" ]]; then
  PLUGIN_ROOT="$(find "${HOME}/.claude/plugins/cache" -path '*/sardine-kb/*/scripts/lib' -type d 2>/dev/null | head -1 | sed 's|/scripts/lib$||')"
fi
INDEX="${PLUGIN_ROOT}/skills/sardine-kb/references/index.json"
echo "<keywords from task name and description>" \
  | python3 "${PLUGIN_ROOT}/scripts/lib/keywords.py" \
  | xargs python3 "${PLUGIN_ROOT}/scripts/lib/search.py" 2 sardine-kb "${INDEX}" \
  | CLAUDE_PLUGIN_ROOT="${PLUGIN_ROOT}" python3 "${PLUGIN_ROOT}/scripts/lib/formatter.py"
```

Read the top 1–3 matched files. Pick by summary fit to the task, not just rank order.

---

### Step 4 — Synthesize and output the requirements

Produce the spec below to the conversation. Write from a product perspective: what the user experiences, what the system must do, and what conditions must be true for the feature to be considered complete.

**Rules:**
- No code snippets, file paths, or line numbers anywhere in the output.
- Requirements must be behavioral: "The user can do X" or "The system must Y."
- Every requirement must be verifiable: someone should be able to test whether it passes or fails.
- Where behavior differs by client, call it out explicitly.
- If something is unknown or needs eng input to verify, put it in Open Questions.

Use this template:

```
## Feature Requirements: <Task Name>

**Asana task:** <name> `<gid>` | Priority: <…> | Pod: <…> | Customer: <…>

---

### Problem Statement

<1–3 sentences. What problem does this solve, for whom, and why now?
Avoid describing the solution — describe the pain or gap.
E.g.: "Compliance analysts at RockWallet cannot export audit logs directly from the dashboard, forcing them to request data manually from the engineering team.">

---

### Background & Context

<Relevant context a new team member would need to understand why this work matters.
- How did this request originate? (customer escalation, internal ask, compliance requirement, etc.)
- Any prior attempts, related work, or decisions that constrain the solution
- Business or regulatory drivers if applicable
Keep to 3–5 bullets; don't pad.>

---

### User Persona

<Who is the primary user of this feature?
- Role (e.g. Compliance Analyst, Fraud Ops, Customer Admin)
- What they're trying to accomplish in their day-to-day workflow
- Their level of technical sophistication relevant to this feature
- Secondary personas if the feature affects more than one user type>

---

### Current State

<Description of what the dashboard does today in this area, written as product behavior.
- What users can currently see and do
- Any existing limitations, gaps, or inconsistencies
- Whether behavior is consistent across all clients or varies
Call out explicitly what is missing that this task requires.>

---

### User Stories

<As a <persona>, I want to <action> so that <outcome>.
Write one story per distinct user need — typically 2–5 stories.
Stories should cover the primary happy path and key edge cases (e.g. empty state, no permissions, bulk vs. single).>

---

### Requirements

<Numbered list. Each requirement must:
- Describe a user-facing behavior or system behavior ("The user can…", "The system must…", "When X, the dashboard shows Y")
- Be clear about scope: platform-wide (all clients) vs. client-specific
- Be testable: someone can verify it passes or fails
- NOT describe implementation ("Add a field to the DB", "Call the X API")>

---

### Acceptance Criteria

<Bulleted checklist used to verify the feature is complete:
- [ ] Given <condition>, when <action>, then <observable result>
- [ ] …
Keep it concrete enough that QA or the PM can run through it without eng involvement.>

---

### Out of Scope

<Related capabilities explicitly excluded from this task.
Link to separate Asana tickets where they exist.>

---

### Open Questions

<Unresolved questions that need an answer before or during implementation.
Each should have an owner (PM, eng, data, design) and what the decision unblocks.
E.g.: "Do we show this to all clients or only the requesting customer? Owner: PM">
```

---

Output is conversation-only by design — copy the spec into the Asana task, a Notion page, or a PR description as needed.
