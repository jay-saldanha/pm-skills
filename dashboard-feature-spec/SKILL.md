---
name: dashboard-feature-spec
description: Turn an Asana feature-request task into engineering feature requirements grounded in the device-dashboard codebase — fetches the task, investigates current state via Explore agents and the sardine-kb, and produces a structured Current State / Requirements / Out of Scope / Implementation Notes spec. Output to conversation only.
argument-hint: "[asana-task-url-or-id]"
---

## Task: Dashboard Feature Requirements from Asana Task

Given an Asana task from the Dashboard project, investigate the current state of the relevant feature in the `device-dashboard` codebase and produce a structured engineering feature requirements document.

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
- **Priority** custom field display value
- **ProdEng Pod** custom field display value
- **Product Area** custom field display value (multi-enum)
- **Customer** — from the task name prefix (e.g. `[RockWallet]`) or `Customers Requesting` custom field
- **Assignee** name

Summarize the ask in one sentence before proceeding.

---

### Step 3 — Investigate current state (run both in parallel)

**3a. Explore agent — device-dashboard codebase**

Launch an Explore agent over `/Users/jayana/device-dashboard` with a focused search prompt derived from the task name and description. The agent should:

- Find UI components, TRPC routes, server external-service calls, shared constants/types, and utilities related to the feature area.
- Search with multiple term variations (camelCase, snake_case, display name, API slug).
- Report exact `file:line` refs and short code excerpts (≤5 lines each) for every relevant hit.
- Explicitly answer: does the capability the task is asking for **already exist** anywhere, even partially?
- Check `/Users/jayana/device-dashboard/packages/shared/audit-logs.ts` for any related event types if the task involves logging or audit trails.
- Check `/Users/jayana/device-dashboard/server/src/event-emitter/` for relevant event emitters.

**3b. sardine-kb keyword search — backend/architecture context**

Run the sardine-kb keyword search pipeline using terms from the task name and description:

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

Produce the spec below to the conversation. Every claim about current state must be grounded in a real `file:line` from Step 3a or the KB from Step 3b. Use markdown link form for file refs: `[filename.ts:NN](relative/path#LNN)`.

Distinguish clearly:
- What **already exists** vs. what **must be built**
- Whether the change is **platform-wide** (all clients) vs. **client-specific** (only the requesting customer)

Use this template:

```
## Feature Requirements: <Task Name>

**Asana task:** <name> `<gid>` | Priority: <…> | Pod: <…> | Customer: <…>

---

### Current State

<Bulleted list of what exists today — components, routes, APIs, types — with file:line links.
Call out explicitly what is missing that the task requires.>

---

### Requirements

<Numbered list. Each requirement should be:
- Concrete and implementable (not vague)
- Paired with the target file:line where the change belongs
- Referencing existing utilities/patterns to reuse where possible
- Clear about whether it is platform-wide or scoped to a specific client>

---

### Out of Scope

<Related capabilities that are NOT part of this task — link to separate tickets if they exist.>

---

### Implementation Notes

<Gotchas, patterns to follow, existing infrastructure to wire into, ordering dependencies.>
```

---

Output is conversation-only by design — copy the spec into the Asana task, a Notion page, or a PR description as needed.
