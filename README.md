# PM Claude Skills

This repo contains Jayana's Claude Code skills — slash-command automations used in day-to-day PM and technical writing workflows.

Each subdirectory is one skill. The skill name matches the slash command (e.g., `/nps-collect`).

## Skill Categories

### NPS Pipeline
End-to-end automation for collecting, synthesizing, and acting on NPS feedback.

| Skill | Phase | What it does |
|-------|-------|--------------|
| `/nps-collect` | 1 | Collect raw NPS survey responses |
| `/nps-synthesize` | 2 | Synthesize responses into thematic buckets |
| `/nps-notion-report` | 3 | Create a Notion synthesis report |
| `/nps-pylon-map` | 4–5 | Map feedback to Pylon accounts and identify AMs |
| `/nps-pfrs` | 6 | Create Asana PFR tasks from synthesized themes |
| `/nps-pipeline` | Full | Run the full NPS pipeline end-to-end |

### Release Notes
Skills for managing the monthly product release notes workflow.

| Skill | What it does |
|-------|--------------|
| `/rn-sync` | Sync newly moved "In Progress" tasks from the Asana Release Notes project to the current month's Notion release notes page |

### Technical Writing / risk-docs
Skills for managing the `sardine-ai/risk-docs` API documentation repo and Asana TW queue.

| Skill | What it does |
|-------|--------------|
| `/apireference-audit` | Audit request/response example coverage across API reference YAML files |
| `/risk-docs-my-prs` | List all open PRs in risk-docs assigned to or created by me |
| `/risk-docs-new-pages` | List all new content pages created since a given date |
| `/tw-inbox-prs` | Create draft PRs for the newest and oldest inbox tickets in the TW Asana board |

### Claude Code / Dev Utilities
General-purpose productivity and workflow skills.

| Skill | What it does |
|-------|--------------|
| `/sync-claude-skills` | List all available Claude skills and sync them to the Notion skills reference page |
| `/notion-to-gh` | Sync new skills from the Notion skills page to the pm-skills GitHub repo — creates a folder and SKILL.md stub for each new skill, and updates the README |
| `/work-summary-update` | Update the Work Summary Tracker Notion page with last month's GitHub/Slack/Asana/Notion activity |
| `/stop-slop` | Eliminate predictable AI writing patterns from prose |
| `/update-config` | Configure the Claude Code harness via `settings.json` — hooks, permissions, automated behaviors, environment variables |
| `/keybindings-help` | Customize keyboard shortcuts in `~/.claude/keybindings.json` — rebind keys, add chord shortcuts, change the submit key |
| `/simplify` | Review recently changed code for reuse, quality, and efficiency, then fix any issues found |
| `/loop` | Run a prompt or slash command on a recurring interval — use for polling, status checks, or repeating a task on a schedule |
| `/schedule` | Create, update, list, or run scheduled remote agents on a cron schedule |
| `/claude-api` | Build apps using the Claude API or Anthropic SDK (Python/TypeScript) with prompt caching |

## Notion Reference

Skills list is synced weekly to: [List of Claude skills used](https://www.notion.so/sardine/List-of-Claude-skills-used-33dd52e0dd8b80baa764c9d6858b0253)
