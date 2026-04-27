---
name: notion-to-gh
description: Sync new skills from the Notion skills page to the pm-skills GitHub repo — creates a folder and SKILL.md stub for each new skill, and updates the README. No arguments needed.
---

## Task: Sync New Skills from Notion to pm-skills

Compare the Notion skills reference page against the `jay-saldanha/pm-skills` repo and sync any new skills that are in Notion but not yet in the repo.

**Notion page:** `https://www.notion.so/sardine/List-of-Claude-skills-used-33dd52e0dd8b80baa764c9d6858b0253`
**Page ID:** `33dd52e0dd8b80baa764c9d6858b0253`
**Target repo:** `jay-saldanha/pm-skills`
**Branch:** `main` (direct commit)

---

### Step 1 — Fetch the Notion page

Call `notion-fetch` with page ID `33dd52e0dd8b80baa764c9d6858b0253`. Parse every row across all tables. For each row extract:
- **Skill name** — strip the leading `/` and any argument hints in `[brackets]` from the command cell (e.g. `/nps-collect [days-back]` → `nps-collect`)
- **Description** — the "What it does" cell text
- **Category** — the `##` section heading the table falls under (e.g. `NPS Pipeline`, `Technical Writing / risk-docs`, `Work & Productivity`, `Claude Code / Dev Utilities`)
- **Phase** (NPS Pipeline only) — the Phase cell value if present

---

### Step 2 — Clone the repo and inventory existing skills

```bash
cd /tmp && rm -rf pm-skills-notion-sync
gh repo clone jay-saldanha/pm-skills pm-skills-notion-sync
ls /tmp/pm-skills-notion-sync/
```

Collect the names of all existing subdirectories (each is a skill). These are the skills already in the repo.

---

### Step 3 — Diff: find new skills

Compare the Notion skill list against the repo directory list. A skill is **new** if its name does not match any existing directory (case-insensitive).

If there are no new skills, report "No new skills found — repo is already up to date." and stop.

---

### Step 4 — Create a folder and SKILL.md stub for each new skill

For each new skill, create `/tmp/pm-skills-notion-sync/<skill-name>/SKILL.md` using this template:

```markdown
---
name: <skill-name>
description: <description from Notion>
---

## Task: <Title-cased skill name, spaces for hyphens>

<description from Notion>

---

### Steps

<!-- TODO: Add detailed steps -->
```

Follow the frontmatter conventions from existing skills exactly: `name`, `description` fields, no extra fields unless the skill is more complex.

---

### Step 5 — Update the README

Read `/tmp/pm-skills-notion-sync/README.md`. For each new skill, append it to the correct category table using the category from Step 1.

- Match the category to the existing `###` section in the README (case-insensitive substring match).
- If the category doesn't exist yet, create a new `###` section before the `## Notion Reference` footer section.
- For NPS Pipeline skills, add a `Phase` column entry. For all others, add a standard two-column row.
- Use the same table format as the existing README rows.

Also remove the `list-of-claude-skills-used.md` row from the README if it exists.

---

### Step 6 — Delete list-of-claude-skills-used.md if present

```bash
rm -f /tmp/pm-skills-notion-sync/list-of-claude-skills-used.md
```

---

### Step 7 — Commit and push to main

```bash
cd /tmp/pm-skills-notion-sync
git add -A
git commit -m "sync: add <skill1>, <skill2> from Notion (YYYY-MM-DD)"
git push origin main
```

List the new skill names in the commit message. Use today's date. If `git push` fails, report the error — do not force push.

---

### Step 8 — Report back

```
New skills synced: <count>
  <skill-name>  →  <skill-name>/SKILL.md  [<Category>]
  ...

README updated: yes
Commit: <GitHub commit URL>
```

If no new skills were found, say so clearly.
