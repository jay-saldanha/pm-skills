# List of Claude skills used

## NPS Pipeline

These skills run the end-to-end NPS feedback processing pipeline. Run them in order, or use `/nps-pipeline` to chain them all.

| Skill | Phase | What it does |
|-------|-------|--------------|
| `/nps-collect [days-back]` | 1 | Reads `#product-fruits-surveys` in Slack, paginates through responses, and outputs a structured list of raw NPS survey responses (author, score, comment, timestamp). |
| `/nps-synthesize` | 2 | Takes raw responses from `/nps-collect` and buckets feedback into themes, computes the NPS score, and flags silent detractors with severity signals. |
| `/nps-notion-report` | 3 | Creates a Notion synthesis report page under *Client Feedback and Surveys* from the themed output of `/nps-synthesize`. |
| `/nps-pylon-map` | 4–5 | Maps feedback authors to Pylon accounts, identifies their account managers, and appends the AM mapping table to the Notion report. |
| `/nps-pfrs` | 6 | Previews then creates Product Feature Request (PFR) tasks in Asana from synthesized NPS themes, linking each task back to the Notion report. |
| `/nps-pipeline [days-back]` | **All** | **Master pipeline** — chains all 6 phases in order (collect → synthesize → Notion report → Pylon map → PFRs), pausing for review between each phase. |

## Technical Writing / risk-docs

Skills for managing the `sardine-ai/risk-docs` GitHub repository and Asana TW request queue.

| Skill | What it does |
|-------|--------------|
| `/risk-docs-my-prs` | Lists all open PRs in `sardine-ai/risk-docs` that are created by you or assigned to you for review. Returns a detailed table with dates, authors, links, and review status. |
| `/apireference-audit [--dry-run]` | Audits request/response example coverage across all API reference YAML files in risk-docs. Drafts missing examples, opens multiple focused PRs, updates the Notion audit page, and creates an Asana tracking ticket. |
| `/risk-docs-new-pages [since date]` | Lists all new English-source content pages merged into `sardine-ai/risk-docs` since a given date (defaults to January 1 of the current year). Grouped by month, sorted by merge date. Excludes translated copies (`es/`, `ja/`, `pt-BR/`) and snippets. |
| `/tw-inbox-prs` | Looks at the Asana "Technical Writing Requests" board, picks the 3 newest and 3 oldest inbox tickets, and creates draft PRs from `main` in risk-docs for any that don't already have one. Writes doc content and links the PR back to the Asana ticket. |

## Work & Productivity

Skills for personal work tracking and monthly reporting.

| Skill | What it does |
|-------|--------------|
| `/work-summary-update [month]` | Pulls last month's activity from GitHub, Slack, Asana, and Notion, then appends a strategic summary and detailed task log to the Work Summary Tracker Notion page. Defaults to the previous calendar month. |

## Claude Code / Dev Utilities

General-purpose skills for configuring and extending your Claude Code environment.

| Skill | What it does |
|-------|--------------|
| `/update-config` | Configures the Claude Code harness via `settings.json`. Use for automated behaviors ("whenever X, do Y"), hook setup, permissions, environment variables, or any `settings.json`/`settings.local.json` changes. |
| `/keybindings-help` | Customizes keyboard shortcuts in `~/.claude/keybindings.json`. Use when you want to rebind keys, add chord shortcuts, or change the submit key. |
| `/simplify` | Reviews recently changed code for reuse, quality, and efficiency, then fixes any issues found. Run after implementing a feature to clean up the diff. |
| `/loop [interval] [command]` | Runs a prompt or slash command on a recurring interval (e.g. `/loop 5m /foo`). Omit the interval to let the model self-pace. Use for polling, recurring status checks, or repeating a task on a schedule. |
| `/schedule` | Creates, updates, lists, or runs scheduled remote agents (triggers) that execute on a cron schedule. Use when you want to set up a recurring automated Claude Code task. |
| `/claude-api` | Assists with building apps using the Claude API or Anthropic SDK (Python/TypeScript). Triggered automatically when code imports `anthropic` or `@anthropic-ai/sdk`. Apps built with this skill include prompt caching. |
| `/stop-slop` | Rewrites prose to remove predictable AI writing patterns (hedging, filler phrases, passive voice, over-explanation). Makes text direct, specific, active-voice, and human-sounding. Paste any text to clean it up. |
| `/sync-claude-skills` | Reads all installed skills from `~/.claude/skills/`, merges descriptions with the system-reminder list, and rebuilds this Notion page with a categorized, up-to-date skills reference. Run whenever a new skill is added. |
