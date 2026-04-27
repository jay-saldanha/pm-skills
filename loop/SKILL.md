---
name: loop
description: Runs a prompt or slash command on a recurring interval. Omit the interval to let the model self-pace. Use for polling, recurring status checks, or repeating a task on a schedule.
---

## Task: Loop

Run a prompt or slash command on a recurring interval. Omit the interval to let the model self-pace. Use for polling, status checks, or any task that should repeat automatically.

---

### Usage

```
/loop [interval] <prompt or /command>
```

**Examples:**
```
/loop 5m /tw-pr-sync          — run tw-pr-sync every 5 minutes
/loop 30s check build status  — poll build status every 30 seconds
/loop /nps-collect            — self-paced: model decides when to re-run
```

**Interval formats:** `30s`, `5m`, `1h` — omit for self-paced mode.

---

### How it works

#### Fixed interval mode (`/loop 5m <task>`)

1. Runs the task immediately.
2. Waits the specified interval (via `ScheduleWakeup`).
3. Re-runs the task on wake-up.
4. Repeats until the user cancels (Ctrl+C or closes the session).

The interval is chosen to stay within the 5-minute prompt cache TTL where possible. Intervals under 270s keep cache warm; longer intervals pay a cache miss.

---

#### Self-paced mode (`/loop <task>`)

1. Runs the task.
2. Claude assesses how long to wait based on what it's watching for (e.g. a build that takes ~8 minutes → sleep ~270s twice rather than polling every 60s).
3. Uses `ScheduleWakeup` with a reasoned `delaySeconds`.
4. Repeats until the task signals completion or the user cancels.

---

### When to use vs. `/schedule`

| | `/loop` | `/schedule` |
|---|---------|-------------|
| **Runs** | In your active session | As a background remote agent |
| **Stops when** | You close the session | You explicitly delete it |
| **Best for** | Watching a build, polling a PR, repeating during a work session | Daily/weekly recurring tasks that run unattended |
