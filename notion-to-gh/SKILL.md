---
name: notion-to-gh
description: Sync a Notion page to the jay-saldanha/pm-skills GitHub repo. Pass a Notion URL; the page content is committed directly to main. File path is inferred from the page title slug.
---

## Task: Sync Notion Page to pm-skills on GitHub

Fetch a Notion page by URL, convert its content to clean markdown, and commit it directly to `jay-saldanha/pm-skills` on `main`.

**Target repo:** `jay-saldanha/pm-skills`
**Branch:** `main` (direct commit, no PR)

---

### Arguments

The user passes a Notion page URL. Accept any of these forms:
- Full URL: `https://www.notion.so/sardine/Page-Title-33dd52e0dd8b80baa764c9d6858b0253`
- Short URL: `https://www.notion.so/33dd52e0dd8b80baa764c9d6858b0253`
- Bare page ID: `33dd52e0dd8b80baa764c9d6858b0253`

---

### Steps

#### 1. Parse the Notion page ID

Extract the 32-character hex page ID from the URL.

Notion URLs end with the page ID as the last path segment. The human-readable title prefix is separated by a hyphen — strip it:

```
https://www.notion.so/sardine/My-Skill-Name-33dd52e0dd8b80baa764c9d6858b0253
                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                              This is the page ID
```

If the user passed a bare ID, use it directly.

---

#### 2. Fetch the Notion page

Call `notion-fetch` with the page ID. Capture:
- **Title** — the page's top-level heading / title property
- **Body content** — the full page text

---

#### 3. Determine the target file path

Slugify the page title:
- Lowercase
- Replace spaces and underscores with hyphens
- Strip all non-alphanumeric characters except hyphens

Examples: `"Sync Claude Skills"` → `sync-claude-skills`, `"NPS: Collect"` → `nps-collect`

**Path resolution logic:**

1. Check if `~/.claude/skills/<slug>/` exists locally → target is `<slug>/SKILL.md`
2. If not, check if `<slug>.md` already exists at the repo root (via `gh api`) → target is `<slug>.md`
3. Otherwise, default to `<slug>.md` at the repo root

---

#### 4. Clone the repo

```bash
cd /tmp && rm -rf pm-skills-notion-sync
gh repo clone jay-saldanha/pm-skills pm-skills-notion-sync
```

---

#### 5. Write the file

Write the Notion page content to the target file path inside the cloned repo. Format rules:

- If the target is a `SKILL.md` (inside a skill directory): preserve any existing YAML frontmatter if the file already exists; only replace the body below the `---` block. If no prior frontmatter exists, write the content as-is (no frontmatter injection).
- If the target is a root `.md` file: write the Notion content directly, using the page title as the `# H1` heading.
- Strip Notion-specific formatting artifacts (e.g., extra blank lines, Unicode checkbox characters `☐ ☑`).
- Preserve all headings, bullet lists, numbered lists, code blocks, and tables as valid GitHub-flavored markdown.

---

#### 6. Commit and push to main

```bash
cd /tmp/pm-skills-notion-sync
git add <target-file>
git commit -m "sync: update <slug> from Notion (YYYY-MM-DD)"
git push origin main
```

Use today's date in the commit message.

---

#### 7. Sync the local skill file (if applicable)

If the target was a `SKILL.md` inside a skill directory, also write the same content to `~/.claude/skills/<slug>/SKILL.md` so the local version stays in sync with GitHub.

---

#### 8. Report back

Output a compact summary:

```
Synced: <Page Title>
  Notion: <notion URL>
  File:   <slug>/SKILL.md  (or <slug>.md)
  Commit: <GitHub commit URL>
```

If `git push` fails (e.g., conflicts), report the error and instruct the user to resolve manually — do not force push.
