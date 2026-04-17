---
name: risk-docs-new-pages
description: List all new content pages created in the sardine-ai/risk-docs repo since a given date (defaults to January 1 of the current year), grouped by month, using merge date.
disable-model-invocation: false
---

## Task: List New Pages in risk-docs

List all newly created English-source content pages in `sardine-ai/risk-docs`, grouped by month, using the **merge date** (committer date) of each file's first commit.

Repo path: `/Users/jayana/risk-docs`

### Arguments

The user may pass an optional start date in any natural format (e.g. "since March", "from 2026-02-01", "this quarter"). If no date is given, default to **January 1 of the current year**.

### Steps

1. **Determine the since date** from the user's argument or default to `YYYY-01-01` where YYYY is the current year.

2. **Run this git command** from `/Users/jayana/risk-docs`:

   ```bash
   git log --diff-filter=A --name-only --format="%cd" --date=short --date-order \
     --since="<SINCE_DATE>" -- "*.mdx" "*.md"
   ```

   This uses `%cd` (committer date = merge date), not `%ad` (author date).

3. **Parse the output**: lines matching `YYYY-MM-DD` set the current date; blank lines are skipped; lines ending in `.mdx` or `.md` are filenames associated with the most recently seen date. Use this awk pattern:

   ```awk
   /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/ { date=$0; next }
   /^$/ { next }
   /\.(mdx|md)$/ { print date "\t" $0 }
   ```

4. **Filter — keep only**:
   - Files under `guides/` (knowledge base, integration guides, API reference, release notes, SDK changelogs, etc.)
   - Root-level style guide `.mdx` files (`api-style-guide.mdx`, `doc-style-guide.mdx`)
   
   **Exclude**:
   - Translation prefixes: `es/`, `ja/`, `pt-BR/`
   - `snippets/` directory
   - `.github/` directory
   - `playwright/` directory
   - Any `README.md` or `SCRIPTS_README*` files

5. **Group results by month** (e.g. `## January 2026`). Within each month sort by date ascending, then filename.

6. **Output a Markdown table per month**:

   | Merged | Page |
   |--------|------|
   | Jan 5  | [CDN Integrations: Fastly](guides/integration/cdn_integrations/fastly.mdx) |

   - Format the date as `Mon D` (e.g. `Jan 5`, `Mar 18`)
   - Make the page title human-readable: strip path prefix, replace hyphens/underscores with spaces, title-case, remove `.mdx` extension
   - Link to the file using a relative path from the repo root

7. **Print a summary line** below all tables:
   > **X new pages** merged between SINCE_DATE and TODAY across Y months.
