---
name: notion-to-gh
description: Sync the Claude skills reference Notion page to the jay-saldanha/pm-skills GitHub repo. No arguments needed — commits directly to main.
---

## Task: Sync Claude Skills Notion Page to GitHub

Fetch the Claude skills reference Notion page and commit its content to `jay-saldanha/pm-skills` on `main`.

**Notion page:** `https://www.notion.so/sardine/List-of-Claude-skills-used-33dd52e0dd8b80baa764c9d6858b0253`
**Page ID:** `33dd52e0dd8b80baa764c9d6858b0253`
**Target repo:** `jay-saldanha/pm-skills`
**Target file:** `list-of-claude-skills-used.md` (repo root)
**Branch:** `main` (direct commit, no PR)

---

### Steps

#### 1. Fetch the Notion page

Call `notion-fetch` with page ID `33dd52e0dd8b80baa764c9d6858b0253`. Capture the full page content.

---

#### 2. Clone the repo

```bash
cd /tmp && rm -rf pm-skills-notion-sync
gh repo clone jay-saldanha/pm-skills pm-skills-notion-sync
```

---

#### 3. Write the file

Write the Notion content to `list-of-claude-skills-used.md` at the repo root:

- Use the page title as the `# H1` heading.
- Strip Notion formatting artifacts (extra blank lines, Unicode checkboxes `☐ ☑`).
- Preserve headings, bullets, numbered lists, code blocks, and tables as valid GitHub-flavored markdown.

---

#### 4. Commit and push to main

```bash
cd /tmp/pm-skills-notion-sync
git add list-of-claude-skills-used.md
git commit -m "sync: update list-of-claude-skills-used from Notion (YYYY-MM-DD)"
git push origin main
```

Use today's date in the commit message. If `git push` fails, report the error — do not force push.

---

#### 5. Report back

```
Synced: List of Claude skills used
  Notion: https://www.notion.so/sardine/List-of-Claude-skills-used-33dd52e0dd8b80baa764c9d6858b0253
  File:   list-of-claude-skills-used.md
  Commit: <GitHub commit URL>
```
