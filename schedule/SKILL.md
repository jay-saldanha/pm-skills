---
name: schedule
description: Creates, updates, lists, or runs scheduled remote agents (triggers) that execute on a cron schedule. Use when you want to set up a recurring automated Claude Code task.
---

## Task: Schedule

Create, update, list, or run scheduled remote agents that execute on a cron schedule. These run unattended as background agents — unlike `/loop`, they persist across sessions.

---

### Usage

```
/schedule                          — list all scheduled triggers
/schedule create                   — create a new scheduled trigger
/schedule run <name>               — run a trigger immediately (one-off)
/schedule delete <name>            — delete a scheduled trigger
```

---

### Steps

#### List existing schedules

Uses `CronList` to show all configured triggers: name, cron expression, last run, next run, and the prompt that fires.

---

#### Create a new schedule

1. Ask for (or infer from context):
   - **Name** — short identifier for the trigger (e.g. `weekly-nps`)
   - **Cron expression** — standard 5-field cron (e.g. `0 9 * * 1` = every Monday at 9am)
   - **Prompt** — the slash command or instruction to run (e.g. `/nps-pipeline`)
   - **Timezone** — default UTC unless specified

2. Call `CronCreate` with the above parameters.

3. Confirm: show the next 3 scheduled run times.

**Common cron expressions:**
| Schedule | Expression |
|----------|------------|
| Every weekday at 9am | `0 9 * * 1-5` |
| Every Monday at 8am | `0 8 * * 1` |
| First of each month | `0 9 1 * *` |
| Every hour | `0 * * * *` |

---

#### Run immediately (one-off)

Uses `RemoteTrigger` to fire a scheduled agent immediately, outside its normal schedule. Useful for testing or manually triggering a monthly report.

---

#### Delete a schedule

Uses `CronDelete` with the trigger name. Asks for confirmation before deleting.

---

### When to use vs. `/loop`

| | `/schedule` | `/loop` |
|---|-------------|---------|
| **Persists across sessions** | Yes | No |
| **Runs unattended** | Yes | Only while session is open |
| **Best for** | Weekly reports, monthly syncs, daily checks | Watching a build, polling during a work session |
