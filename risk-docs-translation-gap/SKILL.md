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

## Step 2 — Run the existing missing + stale script

The repo already has `scripts/find-stale-translations.js` which handles both missing and stale checks. Use it directly rather than reimplementing.

```bash
cd /Users/jayana/risk-docs && node scripts/find-stale-translations.js --json
```

This outputs JSON with:
- `missing` — array of `{ english, language, translated }` objects for files with no translated counterpart
- `stale` — array of `{ english, language, translated }` for files where the English source was committed more recently than the last **bot-authored** commit to the translation
- `upToDate` — count of checks that passed
- `totalChecked` — total file × language combinations checked
- `filesNeedingTranslation` — deduplicated English file list (union of missing + stale)

**Important nuance in the staleness logic:** The script only treats **bot-authored commits** (from `it.sardine@sardine.ai`) as valid evidence that a file is translated. Human commits to a locale file — such as manually pasting English content — are intentionally ignored. This means a file where a human pasted English text will still show as stale if the bot has never committed to it, which is exactly correct.

Apply any `--lang` or `--section` scope from `$ARGUMENTS` to filter the JSON output before continuing.

Store the parsed results as `MISSING` (array) and `STALE` (array) for use in later steps.

---

## Step 3 — Detect orphaned translation files

The existing script does not check for orphaned files (translations with no English counterpart). Compute this separately.

Build the English file inventory:
```bash
find /Users/jayana/risk-docs/guides /Users/jayana/risk-docs/snippets -name "*.mdx" -o -name "*.yaml" \
  | sed 's|/Users/jayana/risk-docs/||' | sort > /tmp/en_files.txt

find /Users/jayana/risk-docs -maxdepth 1 \( -name "*.mdx" -o -name "*.yaml" \) \
  | grep -v "/es/" | grep -v "/ja/" | grep -v "/pt-BR/" \
  | sed 's|/Users/jayana/risk-docs/||' | sort >> /tmp/en_files.txt
```

For each language in scope, find files in the translation dir that have no English counterpart:
```bash
# Example for es/
find /Users/jayana/risk-docs/es -name "*.mdx" -o -name "*.yaml" \
  | sed 's|/Users/jayana/risk-docs/es/||' | sort > /tmp/es_files.txt

comm -23 /tmp/es_files.txt /tmp/en_files.txt  # lines only in es/ = orphaned
```

Store as `ORPHANED_{LANG}` per language.

---

## Step 4 — Content quality check (pasted English detection)

Skip this step if `--skip-content-check` is passed.

The existing scripts do not check whether translated files contain actual translations or just copied English text. This step fills that gap.

For every file that is **not** in `MISSING` and **not** in `STALE` (i.e., it exists and was last committed by the bot after the English source), compare the prose content of both versions to detect untranslated copies.

### 4a. Prose extraction

Strip non-translatable content from both the English and translated versions before comparing:

```awk
# Extract prose-only lines from an .mdx file
BEGIN { in_frontmatter=0; in_code=0; fm_count=0 }
/^---$/ && fm_count < 2 { fm_count++; in_frontmatter = (fm_count == 1); next }
/^```/ { in_code = !in_code; next }
in_frontmatter || in_code { next }
/^[[:space:]]*(import |export |<[A-Z][A-Za-z]* |\/>[[:space:]]*$)/ { next }
/^[[:space:]]*$/ { next }
{ print }
```

This retains: headings (`#`), paragraph text, list items (`-`/`*`), table cell text.
This strips: frontmatter block, fenced code blocks, MDX/JSX component tags, import/export lines.

Run on both `risk-docs/<file>` (English) and `risk-docs/<lang>/<file>` (translation).

**Special handling for YAML files** (`apireference.yaml`, `credit-reports.yaml`, etc.): YAML structure is expected to be identical across languages — only the values of translatable fields matter. Compare only values of `description:`, `title:`, `summary:`, and `x-description:` keys:

```bash
grep -E '^\s+(description|title|summary|x-description):' <file> | sed 's/.*: //'
```

### 4b. Similarity score

```
shared_lines = count of lines in EN_PROSE that appear verbatim in TRANS_PROSE
similarity   = shared_lines / max(|EN_PROSE|, 1)
```

### 4c. Classification

| Similarity | Classification | Meaning |
|---|---|---|
| ≥ 90% | `pasted` | English text was copied as-is; not translated |
| 50–89% | `partial` | Some sections translated, some still English |
| < 50% | `translated` | File appears genuinely translated |

**Skip files with fewer than 5 prose lines** after extraction — too little content to judge. Mark as `too-short-to-judge` and exclude from counts.

```
PASTED_{LANG}  = { file | similarity ≥ 90% }
PARTIAL_{LANG} = { file | 50% ≤ similarity < 90% }
```

### 4d. Coverage percentages

```
PRESENCE_COVERAGE_{LANG}  = (total_checks - |MISSING_{LANG}|) / total_checks * 100
FRESHNESS_COVERAGE_{LANG} = (total_checks - |MISSING_{LANG}| - |STALE_{LANG}|) / total_checks * 100
QUALITY_COVERAGE_{LANG}   = (total_checks - |MISSING_{LANG}| - |STALE_{LANG}| - |PASTED_{LANG}|) / total_checks * 100
```

`total_checks` = number of English files in scope (from Step 2 JSON `totalChecked / 3`).

- `PRESENCE_COVERAGE` — does a translated file exist?
- `FRESHNESS_COVERAGE` — does it exist AND was the bot the last to commit it (after the English source)?
- `QUALITY_COVERAGE` — does it exist, is it fresh, AND does it contain actual translated prose?

`QUALITY_COVERAGE` is the most meaningful real-world number.

### 4e. Breakdown by section
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
