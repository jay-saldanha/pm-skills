---
name: pfr-triage
description: Score and prioritize untriaged PFRs in the Asana PFR board using an adapted RICE rubric. Recommends Priority + T-shirt Size. Read-only — output only, Jayana applies values manually. Runs in batch (whole intake section) or on a single task URL/GID/pasted description.
---

## Task: Score PFRs using the Investigative Tools Prioritization Framework

**This skill is read-only. It never writes to Asana.** It produces a ranked table (batch mode) or a single scoring breakdown (single-task mode) that Jayana uses to manually set `Priority` and `Size` fields in Asana.

---

## Modes

**Batch mode** (no args, or `/pfr-triage batch`): Pull all incomplete tasks from the *New Product Requests* intake section and score them all.

**Single-task mode** (`/pfr-triage <task-URL-or-GID>` or `/pfr-triage` followed by pasted task text): Score one specific task and explain the recommendation. Also use this when the user says "what priority is this?" or pastes a task description.

---

## Asana references

- **Project GID:** `1201824753129207` (PFR's — Product Feature Requests)
- **Intake section GID:** `1201824753129209` (New Product Requests)
- **On Hold section GID:** `1208294174377041` (On Hold - Need More Info)
- **PM Triage section GID:** `1211344719342777` (PM Triage / Scoping)
- **Custom field GIDs:**
  - `Priority`: `1206138212227573` → enum: Very High, High, Medium, Low, TBD
  - `Size`: `1201809501120506` → enum: XXS, XS, S - 2 days, M - 1 week, L - 1 month, XL - 2-3 months, XXL - 4-6 months
  - `ARR` (number): `1213545481205653`
  - `Source` (multi_enum): `1204639558061334` → Client, Internal, Pre sales/POC, Big Rock
  - `Requesting Client` (multi_enum): `1213797034187290`
  - `PFR Product Area`: `1213975532722681`
  - `Customers Requesting` (text): `1201809490061093`
  - `ProdEng Pod`: `1205069615569318`

Load Asana tools via ToolSearch: `mcp__claude_ai_Asana__get_tasks`, `mcp__claude_ai_Asana__get_task`, `mcp__claude_ai_Asana__search_tasks`.

---

## Framework 1 — Prioritization (Adapted RICE for B2B)

**Score = (Reach × Impact × Confidence) ÷ Effort**

### Reach — breadth of affected customers
Source: count distinct entries in `Requesting Client` (multi-enum) + any names in `Customers Requesting` (text, deduplicated).

| # accounts | Reach |
|---|---|
| 1 | 1.0 |
| 2–3 | 1.3 |
| 4–10 | 1.7 |
| Platform-wide / "ALL" / Internal | 2.0 |

### Impact — ARR at stake (dominant term)
Source: `ARR` structured field first; if empty, parse `$X` / "Business impact: X" / "ARR Xk" from the description notes.

| ARR | Impact |
|---|---|
| ≥ $1M | 8 |
| $500k–$999k | 5 |
| $250k–$499k | 3 |
| $50k–$249k | 2 |
| < $50k | 1 |
| None stated / can't find | 0.5 |

### Confidence — how well-specified and validated
Source: check (a) description completeness — does it have a clear Problem, Impact, and named customer(s)? (b) `Source` field — Client = real demand, Internal = assumed demand.

| Signal | Confidence |
|---|---|
| Full description + quantified impact + named client(s) + Source=Client | 1.0 |
| Clear request, partial impact info | 0.8 |
| Vague description, no impact stated, or Source missing | 0.5 |

### Effort → uses Framework 2 below

| Size | Effort divisor |
|---|---|
| XXS | 0.1 |
| XS | 0.25 |
| S | 0.5 |
| M | 1 |
| L | 3 |
| XL | 6 |
| XXL | 12 |

If `Size` is empty, **estimate it using Framework 2** and mark the estimate as LOW confidence (eng input needed).

### Score → Priority band

| Score | Priority |
|---|---|
| ≥ 10 | **Very High** |
| 4–9.99 | **High** |
| 1.5–3.99 | **Medium** |
| < 1.5 | **Low** |

---

## Overrides (flag, don't auto-decide)

Apply AFTER computing the score. These appear as flags in the output — the PM decides whether to apply them.

1. **⚑ Strategic override → Very High candidate**: flag if the task mentions any of: regulatory/compliance requirement, contractual go-live date, churn risk, "Must have by [date]", SAR/CTR/AML filing obligation. This prevents high-ARR-low-reach regulatory asks from being mis-ranked as Low due to Reach=1.

2. **⚠ Needs More Info → route to On Hold**: flag if Confidence = 0.5. Recommend routing to the *On Hold - Need More Info* section (GID `1208294174377041`) instead of setting a Priority. Include what's missing (e.g. "no ARR, no named customer").

3. **⬆/⬇ Priority mismatch**: if the computed band differs from the requester-set `Priority` field, flag it: "Computed: High. Requester set: Low. Recommend updating ⬆."

---

## Framework 2 — T-shirt Sizing (→ `Size` field)

Score scope by layers touched × data work × breadth. When the `Size` field is already set and looks plausible, trust it; otherwise estimate.

| Size | ~Effort | Scope signature |
|---|---|---|
| **XXS** | ≤1 day | Config flag / feature toggle / copy change / surfacing a field that already exists in the data model |
| **XS** | ~1 day | Add one filter, column, or display attribute to an existing surface; trivial API field addition |
| **S** | ~2 days | New filter/column requiring backend query change; expose an existing backend field in the UI; small API param; single-table data mapping |
| **M** | ~1 week | New endpoint param + backend wiring; new dashboard widget; new aggregation type; bulk action (CSV); new data-pipeline mapping (Chronon); cross-table query |
| **L** | ~1 month | Feature spanning UI + API + data model; cross-service integration; new entity in an existing graph; per-user preference system; rule-engine feature |
| **XL** | 2–3 months | Net-new subsystem (e.g. SAR filing engine, notification center); multi-team coordination; requires data model migration |
| **XXL** | 4–6 months | Platform-level program / Big Rock |

**Sizing confidence:** Mark HIGH if the description is clear enough to size from; mark LOW if an engineer needs to weigh in. When LOW, add a note: "Confirm size with Yucheng before trusting the RICE score — effort is the denominator."

---

## Steps — Batch Mode

1. **Pull tasks** using `get_tasks` with `section=1201824753129209`, `limit=100`, `opt_fields=name,gid,completed,notes,custom_fields`. If there's a next_page, paginate until all incomplete tasks are loaded.

2. **For each incomplete task**, extract:
   - `ARR` (structured field `1213545481205653`)
   - `Size` (field `1201809501120506`, display_value)
   - `Priority` (field `1206138212227573`, display_value — the requester-set value)
   - `Source` (field `1204639558061334`)
   - `Requesting Client` (field `1213797034187290`, count of multi-enum values)
   - `Customers Requesting` (text field `1201809490061093`)
   - Notes length and description completeness (does it have a problem statement + impact?)

3. **Score each task** using both frameworks above.

4. **Output a ranked table**, sorted by Score descending:

```
| # | PFR (link) | Clients | ARR | Reach | Impact | Conf | Size (est) | Score | → Priority | Flags |
```

- Link each PFR title to `https://app.asana.com/0/1201824753129207/<gid>`.
- Under the table, list tasks routed to **Needs More Info** separately (they don't get ranked).
- Use ⚑ for strategic override, ⬆/⬇ for priority mismatch, ⚠ for Needs More Info.
- After the table, add a **"Tasks without ARR"** section listing the remaining items with a note: "These need an ARR/impact value before scoring — either add it to the Asana field or paste the task here for manual scoring."

5. **End with a brief summary**: how many scored, how many Needs More Info, biggest priority corrections found (e.g. "3 tasks set Low that compute High").

---

## Steps — Single-Task Mode

1. **Resolve the task**: if a URL or GID is given, use `get_task` to fetch it. If pasted text is given, extract the key signals from the text directly (no API call needed).

   Asana task URL format: `https://app.asana.com/0/<project>/<task-gid>` or `https://app.asana.com/1/<workspace>/task/<task-gid>`.

2. **Score it** using both frameworks. Show the full factor breakdown:

```
**PFR:** [title]
**Task:** https://app.asana.com/0/1201824753129207/<gid>

**RICE Scoring:**
- Reach: X (N client(s): ...)
- Impact: X (ARR: $...)
- Confidence: X (description: ..., Source: ...)
- Effort: X (Size: ... — estimated/confirmed, confidence: HIGH/LOW)
- **Score: X.X**

**→ Recommended Priority: [band]**
**→ Recommended Size: [band]** (confirm with eng if LOW confidence)

**Flags:**
- [Strategic override / Needs More Info / Priority mismatch / none]

**Justification:** [1–2 sentences explaining the key driver — what makes it high/low and what to watch for]
```

3. If the task's current `Priority` differs from the recommendation, call it out clearly: "Current: Low. Recommend updating to: High (⬆ 2 bands). Key driver: ARR $1.06M with low effort."

---

## Notes on calibration

After the first real triage batch, the Score → Priority bands may need adjusting if the distribution skews (e.g. everything lands High). If that happens, note it and suggest updated band thresholds. The bands above are a starting calibration, not permanent.
