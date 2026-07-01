---
name: risk-docs-translation-gap
description: Audit translated files (es, ja, pt-BR) against English source in risk-docs — lists missing files per language, stale translations where English was updated after the translation, orphaned translation files, coverage percentages, and optionally posts a Notion report.
argument-hint: "[--lang es|ja|pt-BR] [--section guides|snippets|root] [--notion] [--dry-run]"
---

# risk-docs-translation-gap

Compares all English-source content files in `sardine-ai/risk-docs` against each translation tree (`es/`, `ja/`, `pt-BR/`). Produces a full gap report with three gap types:

1. **Missing** — file exists in English but has no translated counterpart at all
2. **Stale** — translated file exists but the English source was committed more recently, meaning the translation is out of date
3. **Orphaned** — file exists in the translation dir but has no English source (likely renamed or deleted)

Coverage percentages are reported for both presence (file exists) and freshness (file exists AND is up to date).

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

For each language, compute three gap types.

### 4a. Missing from translation
Files in `EN_FILES` but NOT in `{LANG}_FILES`. These are files that exist in English but have no translated counterpart at all.

```
MISSING_{LANG} = EN_FILES - {LANG}_FILES
```

### 4b. Stale translations
For every file that IS present in both English and the translation (i.e., `EN_FILES ∩ {LANG}_FILES`), compare the last-commit date of the English file against the last-commit date of the translated file.

Get the last-commit date for a file:
```bash
# English file
git -C /Users/jayana/risk-docs log -1 --format="%cd" --date=short -- "<file_path>"

# Translated file (e.g. for es/)
git -C /Users/jayana/risk-docs log -1 --format="%cd" --date=short -- "es/<file_path>"
```

If the English file's last-commit date is **later** than the translated file's last-commit date, the translation is stale — it existed before the English page was updated.

For efficiency, batch this with a single `git log` call across all files rather than one call per file:
```bash
# Get last-commit date for every file at once (English)
git -C /Users/jayana/risk-docs log --format="%cd %H" --date=short --name-only -- <files...> \
  | awk '/^[0-9]{4}/ { date=$1 } /\.(mdx|yaml|md)$/ { print date "\t" $0 }'

# Same for translation dir
git -C /Users/jayana/risk-docs log --format="%cd %H" --date=short --name-only -- <translated_files...> \
  | awk '/^[0-9]{4}/ { date=$1 } /\.(mdx|yaml|md)$/ { print date "\t" $0 }'
```

Record for each stale file:
- `file` — the relative path (without lang prefix)
- `en_last_updated` — date of last English commit
- `translation_last_updated` — date of last translated commit
- `days_behind` — integer difference in days

```
STALE_{LANG} = { file | file ∈ EN_FILES ∩ {LANG}_FILES AND en_last_updated > translation_last_updated }
```

### 4c. Orphaned in translation
Files in `{LANG}_FILES` but NOT in `EN_FILES`. These exist in the translation dir but have no English source — likely renamed or deleted in English.

```
ORPHANED_{LANG} = {LANG}_FILES - EN_FILES
```

### 4d. Coverage percentages
Report two coverage numbers per language:

```
PRESENCE_COVERAGE_{LANG}  = (|EN_FILES| - |MISSING_{LANG}|) / |EN_FILES| * 100
FRESHNESS_COVERAGE_{LANG} = (|EN_FILES| - |MISSING_{LANG}| - |STALE_{LANG}|) / |EN_FILES| * 100
```

`PRESENCE_COVERAGE` answers: "does a translated file exist?"
`FRESHNESS_COVERAGE` answers: "does a translated file exist AND is it up to date?"

### 4e. Breakdown by section
Apply section grouping to all three gap types (`MISSING`, `STALE`, `ORPHANED`):
- `guides/api-reference/` — API reference
- `guides/integration/` — Integration guides
- `guides/knowledge-base/` — Knowledge base
- `guides/release-notes/` — Release notes
- `snippets/` — Snippets
- root (anything without a `guides/` or `snippets/` prefix)

---

## Step 5 — Print the gap report

Output the following structure. Keep it scannable.

```
## Risk-Docs Translation Gap Report — YYYY-MM-DD
**risk-docs SHA:** <sha>
**Languages audited:** es, ja, pt-BR
**Total English source files:** N

---

### Coverage Summary

| Language | Presence coverage | Freshness coverage | Missing | Stale | Orphaned |
|---|---|---|---|---|---|
| Spanish (es/) | N% | N% | N | N | N |
| Japanese (ja/) | N% | N% | N | N | N |
| Portuguese-BR (pt-BR/) | N% | N% | N | N | N |

Presence coverage = file exists in translation dir
Freshness coverage = file exists AND is not out of date vs English source

---

### Spanish (es/)

#### Missing Files (N) — no translated counterpart exists

##### API Reference (N)
- guides/api-reference/...

##### Integration Guides (N)
- guides/integration/...

##### Knowledge Base (N)
- guides/knowledge-base/...

##### Release Notes (N)
- guides/release-notes/...

##### Snippets (N)
- snippets/...

##### Root-level (N)
- home.mdx
- bankapi.yaml

#### Stale Translations (N) — English updated after translation

| File | EN last updated | Translation last updated | Days behind |
|---|---|---|---|
| guides/knowledge-base/foo.mdx | 2026-05-10 | 2026-03-01 | 70 |
| ... | | | |

Group stale files by section (same section prefixes as missing). Sort by days_behind descending (oldest first).

#### Orphaned in es/ (N) — no English counterpart
- <file>

---

### Japanese (ja/)

[same structure: Missing, Stale, Orphaned]

---

### Portuguese-BR (pt-BR/)

[same structure: Missing, Stale, Orphaned]

---

### Common Gaps (all three languages)
Files missing OR stale in all three languages simultaneously.

### Priority Recommendations
List the top gaps to close, ordered by customer impact:
1. Stale translations with the highest days_behind that are in high-traffic sections (knowledge-base, integration)
2. Files missing in all three languages (especially home.mdx, bankapi.yaml)
3. Entire sections with >80% missing in a language
4. Release notes — new release notes untranslated in all languages
5. Orphaned files that should be deleted from translation dirs
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
Three toggle blocks, one per language, each containing the full missing-file list — so translators can use this page as a checklist.

**Section: Stale Translations (by language)**
Three toggle blocks, one per language, each containing the stale-file table (file, EN last updated, translation last updated, days behind), sorted by days_behind descending. This is the highest-value section for translators working on existing languages like Spanish.

**Section: Orphaned Files to Remove**
List files that should be deleted from each translation dir because they have no English counterpart.

**Section: Audit History**
Append a one-row summary to a running table at the bottom of the page (do not overwrite):

| Date | SHA | EN files | es presence% | es fresh% | ja presence% | ja fresh% | pt-BR presence% | pt-BR fresh% |
|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | <sha> | N | N% | N% | N% | N% | N% | N% |

---

## Step 7 — Final summary

Print:
```
## Translation Audit Complete

| Language | Presence | Freshness | Missing | Stale | Orphaned |
|---|---|---|---|---|---|
| es/ | N% | N% | N files | N files | N files |
| ja/ | N% | N% | N files | N files | N files |
| pt-BR/ | N% | N% | N files | N files | N files |

Most stale file: <file> — <N> days behind in <lang>
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
