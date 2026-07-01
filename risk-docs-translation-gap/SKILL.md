---
name: risk-docs-translation-gap
description: Audit translated files (es, ja, pt-BR) against English source in risk-docs — lists missing files per language, orphaned translation files, coverage percentages, and optionally posts a Notion report.
argument-hint: "[--lang es|ja|pt-BR] [--section guides|snippets|root] [--notion] [--dry-run]"
---

# risk-docs-translation-gap

Compares all English-source content files in `sardine-ai/risk-docs` against each translation tree (`es/`, `ja/`, `pt-BR/`). Produces a full gap report: missing files per language, orphaned translation files with no English counterpart, and coverage percentages by section. Optionally writes the report to Notion.

`$ARGUMENTS` usage:
- `--lang es|ja|pt-BR` — scope to one language. Omit to audit all three.
- `--section guides|snippets|root` — scope to one content section. Omit to audit all.
- `--notion` — write the report to the Notion page defined in Step 5. Requires Notion MCP.
- `--dry-run` — print the report only; do not write to Notion.

---

## Step 1 — Pull risk-docs to HEAD

```bash
cd /Users/jayana/risk-docs && git pull origin main
```

If this fails (uncommitted changes, offline), warn but continue — note the current SHA in the report.

```bash
RISK_DOCS_SHA=$(cd /Users/jayana/risk-docs && git rev-parse --short HEAD)
```

---

## Step 2 — Build the English file inventory

Collect all English-source content files. Three buckets:

### 2a. Root-level files
```bash
find /Users/jayana/risk-docs -maxdepth 1 \( -name "*.mdx" -o -name "*.yaml" \) \
  | grep -v "^/Users/jayana/risk-docs/es/" \
  | grep -v "^/Users/jayana/risk-docs/ja/" \
  | grep -v "^/Users/jayana/risk-docs/pt-BR/" \
  | sed 's|/Users/jayana/risk-docs/||' \
  | sort
```

### 2b. guides/ files
```bash
find /Users/jayana/risk-docs/guides -name "*.mdx" -o -name "*.yaml" -o -name "*.md" \
  | sed 's|/Users/jayana/risk-docs/||' \
  | sort
```

### 2c. snippets/ files
```bash
find /Users/jayana/risk-docs/snippets -name "*.mdx" -o -name "*.yaml" -o -name "*.md" \
  | sed 's|/Users/jayana/risk-docs/||' \
  | sort
```

Combine all three buckets into a single sorted list: `EN_FILES`. Apply any `--section` scope from `$ARGUMENTS` to filter this list before continuing.

**Total English file count** = `|EN_FILES|`.

---

## Step 3 — Build translation inventories

For each language in scope (default: es, ja, pt-BR), run:

```bash
# Example for es — repeat for ja and pt-BR
find /Users/jayana/risk-docs/es -name "*.mdx" -o -name "*.yaml" -o -name "*.md" \
  | sed 's|/Users/jayana/risk-docs/es/||' \
  | sort
```

Store result as `ES_FILES`, `JA_FILES`, `PT_FILES`.

---

## Step 4 — Compute the gap

For each language, compute:

### 4a. Missing from translation
Files in `EN_FILES` but NOT in `{LANG}_FILES`. These are files that exist in English but have no translated counterpart.

```
MISSING_{LANG} = EN_FILES - {LANG}_FILES
```

### 4b. Orphaned in translation
Files in `{LANG}_FILES` but NOT in `EN_FILES`. These exist in the translation dir but have no English source — likely stale, renamed, or never created in English.

```
ORPHANED_{LANG} = {LANG}_FILES - EN_FILES
```

### 4c. Coverage percentage
```
COVERAGE_{LANG} = (|EN_FILES| - |MISSING_{LANG}|) / |EN_FILES| * 100
```

### 4d. Breakdown by section
Within `MISSING_{LANG}`, group by section prefix:
- `guides/api-reference/` — API reference
- `guides/integration/` — Integration guides
- `guides/knowledge-base/` — Knowledge base
- `guides/release-notes/` — Release notes
- `snippets/` — Snippets
- root (anything without a `guides/` or `snippets/` prefix)

---

## Step 5 — Print the gap report

Output the following structure. Keep it scannable — one row per file in the missing lists.

```
## Risk-Docs Translation Gap Report — YYYY-MM-DD
**risk-docs SHA:** <sha>
**Languages audited:** es, ja, pt-BR
**Total English source files:** N

---

### Coverage Summary

| Language | Translated | Missing | Orphaned | Coverage |
|---|---|---|---|---|
| Spanish (es/) | N | N | N | N% |
| Japanese (ja/) | N | N | N | N% |
| Portuguese-BR (pt-BR/) | N | N | N | N% |

---

### Spanish (es/) — Missing Files (N total)

#### API Reference (N)
- guides/api-reference/...

#### Integration Guides (N)
- guides/integration/...

#### Knowledge Base (N)
- guides/knowledge-base/...

#### Release Notes (N)
- guides/release-notes/...

#### Snippets (N)
- snippets/...

#### Root-level (N)
- home.mdx
- bankapi.yaml

#### Orphaned in es/ (N) — no English counterpart
- <file>

---

### Japanese (ja/) — Missing Files (N total)

[same structure]

---

### Portuguese-BR (pt-BR/) — Missing Files (N total)

[same structure]

---

### Common Gaps (missing in ALL three languages)
- <file>
- ...

### Priority Recommendations
List the top gaps to close, ordered by customer impact:
1. Release notes — all new release notes (YYYY) untranslated in all languages
2. Any section where >80% of files are missing in a language
3. Root-level files (home.mdx, bankapi.yaml) missing across all languages
4. Orphaned files that should be deleted from translation dirs
```

---

## Step 6 — Notion report (only if `--notion` flag passed)

### 6a. Locate or create the Notion page

Check `~/.claude/skills/risk-docs-translation-gap/notion-page-id.txt` for a saved page ID.

**If the file exists:** use `mcp__claude_ai_Notion__notion-update-page` with `command: replace_content` to overwrite with the latest report.

**If the file does not exist:** create a new Notion page titled "Risk-Docs Translation Gap Audit" using `mcp__claude_ai_Notion__notion-create-pages`. Save the returned page ID to `~/.claude/skills/risk-docs-translation-gap/notion-page-id.txt`.

### 6b. Page content

Write the full report from Step 5, then append:

**Section: Files to Translate (by language)**
Three toggle blocks, one per language, each containing the full missing-file list — so the translators can use this page as a checklist.

**Section: Orphaned Files to Remove**
List files that should be deleted from each translation dir because they have no English counterpart.

**Section: Audit History**
Append a one-row summary to a running table at the bottom of the page (do not overwrite):

| Date | SHA | EN files | es% | ja% | pt-BR% |
|---|---|---|---|---|---|
| YYYY-MM-DD | <sha> | N | N% | N% | N% |

---

## Step 7 — Final summary

Print:
```
## Translation Audit Complete

| Language | Coverage | Missing | Orphaned |
|---|---|---|---|
| es/ | N% | N files | N files |
| ja/ | N% | N files | N files |
| pt-BR/ | N% | N files | N files |

Top priority: <single most impactful gap>
Notion: <url or "skipped (no --notion flag)">
Run again with --notion to post the report to Notion.
```

---

## When NOT to run this skill

| Situation | What to do instead |
|---|---|
| You want to check drift between internal KB and external docs | `/risk-docs-drift` |
| You want to see what new English pages were added this month | `/risk-docs-new-pages` |
| You want to audit API reference example coverage | `/apireference-audit` |
| You only want one language | Pass `--lang es` (or `ja` or `pt-BR`) |
