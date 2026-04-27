---
name: notion-to-gh
description: Sync a Notion page to the jay-saldanha/pm-skills GitHub repo. Pass a Notion URL and optional --path override; content is committed directly to main.
---

## Task: Sync Notion Page to pm-skills on GitHub

Fetch a Notion page by URL, convert its content to clean markdown, and commit it directly to `jay-saldanha/pm-skills` on `main`.

**Target repo:** `jay-saldanha/pm-skills`
**Branch:** `main` (direct commit, no PR)

---

### Arguments

```
/notion-to-gh <notion-url> [--path <relative-path>]
```

**`<notion-url>`** (required) — Accept any of these forms:
- Full URL: `https://www.notion.so/sardine/Page-Title-33dd52e0dd8b80baa764c9d6858b0253`
- Short URL: `https://www.notion.so/33dd52e0dd8b80baa764c9d6858b0253`
- Bare page ID: `33dd52e0dd8b80baa764c9d6858b0253`

**`--path <relative-path>`** (optional) — Override the inferred file path. Examples:
- `--path my-skill/SKILL.md` → writes to that skill directory
- `--path docs/reference.md` → writes to that path at the repo root

If `--path` is omitted, the path is inferred from the page title (see Step 3).

---

### Steps

#### 1. Parse the Notion page ID

Extract the 32-character hex page ID from the URL. The page ID is always the last segment of the path. Strip any human-readable title prefix that precedes it:

```
https://www.notion.so/sardine/My-Skill-Name-33dd52e0dd8b80baa764c9d6858b0253
                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

If the user passed a bare ID, use it directly.

---

#### 2. Fetch the Notion page

Call `notion-fetch` with the page ID. Capture:
- **Title** — from the page's title property
- **Body content** — the full page text

---

#### 3. Determine the target file path

If `--path` was provided, use it directly — skip the rest of this step.

Otherwise, slugify the page title:
- Lowercase
- Replace spaces and underscores with hyphens
- Strip all non-alphanumeric characters except hyphens

Examples: `"Sync Claude Skills"` → `sync-claude-skills`, `"NPS: Collect"` → `nps-collect`

**Path resolution:**
- If `~/.claude/skills/<slug>/` exists locally → target is `<slug>/SKILL.md`
- Otherwise → target is `<slug>.md` at the repo root

---

#### 4. Clone the repo

```bash
cd /tmp && rm -rf pm-skills-notion-sync
gh repo clone jay-saldanha/pm-skills pm-skills-notion-sync
```

---

#### 5. Write the file

Write the Notion page content to the target path inside the cloned repo:

- **`SKILL.md` target:** If the file already exists, preserve its YAML frontmatter and replace only the body below the closing `---`. If no frontmatter exists, write content as-is.
- **Root `.md` target:** Use the page title as the `# H1` heading, then write the body.
- Strip Notion formatting artifacts (extra blank lines, Unicode checkboxes `☐ ☑`).
- Preserve headings, bullets, numbered lists, code blocks, and tables as valid GitHub-flavored markdown.

---

#### 6. Commit and push to main

```bash
cd /tmp/pm-skills-notion-sync
git add <target-file>
git commit -m "sync: update <slug> from Notion (YYYY-MM-DD)"
git push origin main
```

Use today's date in the commit message. If `git push` fails, report the error — do not force push.

---

#### 7. Sync the local skill file (if applicable)

If the target was a `SKILL.md` inside a skill directory, also write the same content to `~/.claude/skills/<slug>/SKILL.md` so the local version stays in sync.

---

#### 8. Report back

```
Synced: <Page Title>
  Notion: <notion URL>
  File:   <target path>
  Commit: <GitHub commit URL>
```
