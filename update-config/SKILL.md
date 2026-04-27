---
name: update-config
description: Configures the Claude Code harness via settings.json. Use for automated behaviors, hook setup, permissions, environment variables, or any settings.json/settings.local.json changes.
---

## Task: Update Config

Configure the Claude Code harness via `settings.json`. Use for automated behaviors ("whenever X, do Y"), hook setup, permissions, environment variables, or any `settings.json`/`settings.local.json` changes.

---

### When to use

- You want Claude to do something automatically before or after a tool call (e.g. "always run prettier after editing a file")
- You want to allow or deny specific tools or bash commands without being prompted
- You need to set environment variables available to Claude's bash sessions
- You want to adjust Claude Code's default behavior (auto-compact, verbose output, model, etc.)

---

### Steps

#### 1. Determine the target settings file

| File | Scope |
|------|-------|
| `~/.claude/settings.json` | Global — applies to all projects |
| `.claude/settings.json` | Project-level — checked into the repo, shared with team |
| `.claude/settings.local.json` | Project-level — local only, gitignored |

Default to project-level `settings.local.json` unless the change should be global or shared.

---

#### 2. Read the current settings file

Read the target file if it exists. If it doesn't exist, start from `{}`.

---

#### 3. Make the requested change

**Hooks** — run shell commands automatically on Claude Code events:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "prettier --write $FILE" }]
      }
    ]
  }
}
```
Supported hook events: `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SubagentStop`.

**Permissions** — allow or deny tools without prompting:
```json
{
  "permissions": {
    "allow": ["Bash(git *)", "Edit", "Read"],
    "deny": ["Bash(rm -rf *)"]
  }
}
```

**Environment variables:**
```json
{
  "env": {
    "MY_VAR": "value"
  }
}
```

**Model override:**
```json
{
  "model": "claude-opus-4-6"
}
```

---

#### 4. Validate and write

Ensure the JSON is valid. Write the updated file.

---

#### 5. Confirm

Report what was changed, which file was updated, and whether a Claude Code restart is needed for the change to take effect (hooks and model changes take effect immediately; some permission changes may require restart).
