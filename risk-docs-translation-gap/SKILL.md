---
name: risk-docs-translation-gap
description: Audit translated files (es, ja, pt-BR) against English source in risk-docs — lists missing files per language, stale translations where English was updated after the translation, orphaned translation files, coverage percentages, and optionally posts a Notion report.
argument-hint: "[--lang es|ja|pt-BR] [--section guides|snippets|root] [--notion] [--dry-run]"
---

# risk-docs-translation-gap

Compares all English-source content files in `sardine-ai/risk-docs` against each translation tree (`es/`, `ja/`, `pt-BR/`). Produces a full gap report with four gap types:

1. **Missing** — file exists in English but has no translated counterpart at all
2. **Stale** — translated file exists but the English source was committed more recently, meaning the translation is out of date
3. **Pasted** — translated file exists and has a recent commit date, but its prose content is identical (or nearly identical) to the English source — the file was copied but never actually translated
4. **Orphaned** — file exists in the translation dir but has no English source (likely renamed or deleted)

Coverage percentages are reported across three dimensions: presence, freshness, and content quality.

`$ARGUMENTS` usage:
- `--lang es|ja|pt-BR` — scope to one language. Omit to audit all three.
- `--section guides|snippets|root` — scope to one content section. Omit to audit all.
- `--notion` — write the report to the Notion page defined in Step 6. Requires Notion MCP.
- `--dry-run` — print the report only; do not write to Notion.
- `--skip-content-check` — skip the prose-similarity check (Step 4e). Faster, but won't catch pasted-English files.

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

### 4c. Pasted content (not actually translated)

Skip this step if `--skip-content-check` is passed.

For every file present in **both** English and the translation tree (i.e., `EN_FILES ∩ {LANG}_FILES`), compare the prose content of both files to detect untranslated copies.

#### Prose extraction

Before comparing, strip non-translatable content from both versions:

```bash
# For a given .mdx file, extract prose-only lines:
# - Remove frontmatter block (lines between opening and closing ---)
# - Remove fenced code blocks (``` ... ```)
# - Remove MDX/JSX component-only lines (lines that are purely a tag: <Component ... /> or <Component>)
# - Remove import/export statements
# - Remove blank lines
# What remains: headings (#), paragraph text, list items (-/*), table cell content
```

Use this awk script to extract prose from a file:

```awk
BEGIN { in_frontmatter=0; in_code=0; fm_count=0 }
/^---$/ && fm_count < 2 { fm_count++; in_frontmatter = (fm_count == 1); next }
/^```/ { in_code = !in_code; next }
in_frontmatter || in_code { next }
/^[[:space:]]*(import |export |<[A-Z][A-Za-z]* |\/>[[:space:]]*$)/ { next }
/^[[:space:]]*$/ { next }
{ print }
```

Run this on both the English file (`/Users/jayana/risk-docs/<file>`) and the translated file (`/Users/jayana/risk-docs/<lang>/<file>`), producing `EN_PROSE` and `TRANS_PROSE`.

#### Similarity score

```
shared_lines  = count of lines in EN_PROSE that appear verbatim in TRANS_PROSE
similarity    = shared_lines / max(|EN_PROSE|, 1)
```

#### Classification

| Similarity | Classification | Meaning |
|---|---|---|
| ≥ 90% | `pasted` | English text was copied as-is; file is not translated |
| 50–89% | `partial` | Some sections translated, some still English |
| < 50% | `translated` | File appears genuinely translated |

**Special handling for YAML files** (`apireference.yaml`, `credit-reports.yaml`, etc.): YAML structure (keys, indentation) is expected to be identical. Compare only the string *values* of translatable fields (`description:`, `title:`, `summary:`, `x-description:`). Extract them with:

```bash
grep -E '^\s+(description|title|summary|x-description):' <file> | sed 's/.*: //'
```

Apply the same similarity threshold to these value strings only.

**Skip files with fewer than 5 prose lines** after extraction — too little content to judge reliably. Mark them as `too-short-to-judge` and exclude from counts.

```
PASTED_{LANG}  = { file | similarity ≥ 90% }
PARTIAL_{LANG} = { file | 50% ≤ similarity < 90% }
```

### 4d. Orphaned in translation
Files in `{LANG}_FILES` but NOT in `EN_FILES`. These exist in the translation dir but have no English source — likely renamed or deleted in English.

```
ORPHANED_{LANG} = {LANG}_FILES - EN_FILES
```

### 4e. Coverage percentages
Report three coverage numbers per language:

```
PRESENCE_COVERAGE_{LANG}  = (|EN_FILES| - |MISSING_{LANG}|) / |EN_FILES| * 100
FRESHNESS_COVERAGE_{LANG} = (|EN_FILES| - |MISSING_{LANG}| - |STALE_{LANG}|) / |EN_FILES| * 100
QUALITY_COVERAGE_{LANG}   = (|EN_FILES| - |MISSING_{LANG}| - |STALE_{LANG}| - |PASTED_{LANG}|) / |EN_FILES| * 100
```

- `PRESENCE_COVERAGE` — does a translated file exist?
- `FRESHNESS_COVERAGE` — does it exist AND is it up to date vs English?
- `QUALITY_COVERAGE` — does it exist, is it up to date, AND is it actually translated (not just English pasted)?

`QUALITY_COVERAGE` is the most meaningful number for assessing true translation completeness.

### 4f. Breakdown by section
Apply section grouping to all four gap types (`MISSING`, `STALE`, `PASTED`, `ORPHANED`):
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

| Language | Presence | Freshness | Quality | Missing | Stale | Pasted | Orphaned |
|---|---|---|---|---|---|---|---|
| Spanish (es/) | N% | N% | N% | N | N | N | N |
| Japanese (ja/) | N% | N% | N% | N | N | N | N |
| Portuguese-BR (pt-BR/) | N% | N% | N% | N | N | N | N |

- Presence = file exists in translation dir
- Freshness = file exists AND not out of date vs English source
- Quality = file exists, up to date, AND actually translated (not English pasted)

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

Group by section, sort by days_behind descending.

#### Pasted Content (N) — file exists but English text was not translated

| File | Similarity | Classification |
|---|---|---|
| guides/integration/bar.mdx | 97% | pasted |
| guides/knowledge-base/baz.mdx | 63% | partial |
| ... | | |

Group by section, sort by similarity descending (worst first).

Include a note if content-check was skipped: "Content check skipped — run without --skip-content-check to detect pasted files."

#### Orphaned in es/ (N) — no English counterpart
- <file>

---

### Japanese (ja/)

[same structure: Missing, Stale, Pasted, Orphaned]

---

### Portuguese-BR (pt-BR/)

[same structure: Missing, Stale, Pasted, Orphaned]

---

### Common Gaps (all three languages)
Files that are missing, stale, OR pasted in all three languages simultaneously.

### Priority Recommendations
List the top gaps to close, ordered by customer impact:
1. Pasted files in high-traffic sections (knowledge-base, integration) — these appear complete but are actually English
2. Stale translations with the highest days_behind in high-traffic sections
3. Files missing in all three languages (especially home.mdx, bankapi.yaml)
4. Entire sections with >80% missing in a language
5. Release notes — new release notes untranslated in all languages
6. Orphaned files that should be deleted from translation dirs
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
Three toggle blocks, one per language, each containing the stale-file table (file, EN last updated, translation last updated, days behind), sorted by days_behind descending.

**Section: Pasted Content — Not Translated (by language)**
Three toggle blocks, one per language, each containing the pasted-file table (file, similarity %, classification). This is often the most surprising section — files that look translated but contain English prose. Sort by similarity descending (worst offenders first). If content-check was skipped, note that explicitly.

**Section: Orphaned Files to Remove**
List files that should be deleted from each translation dir because they have no English counterpart.

**Section: Audit History**
Append a one-row summary to a running table at the bottom of the page (do not overwrite):

| Date | SHA | EN files | es presence% | es fresh% | es quality% | ja presence% | ja fresh% | ja quality% | pt-BR presence% | pt-BR fresh% | pt-BR quality% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| YYYY-MM-DD | <sha> | N | N% | N% | N% | N% | N% | N% | N% | N% | N% |

---

## Step 7 — Final summary

Print:
```
## Translation Audit Complete

| Language | Presence | Freshness | Quality | Missing | Stale | Pasted | Orphaned |
|---|---|---|---|---|---|---|---|
| es/ | N% | N% | N% | N files | N files | N files | N files |
| ja/ | N% | N% | N% | N files | N files | N files | N files |
| pt-BR/ | N% | N% | N% | N files | N files | N files | N files |

Most stale: <file> — <N> days behind in <lang>
Worst pasted: <file> — <N>% similarity in <lang>
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
