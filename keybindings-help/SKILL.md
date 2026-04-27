---
name: keybindings-help
description: Customizes keyboard shortcuts in ~/.claude/keybindings.json. Use when you want to rebind keys, add chord shortcuts, or change the submit key.
---

## Task: Keybindings Help

Customize keyboard shortcuts in `~/.claude/keybindings.json`. Use when you want to rebind keys, add chord shortcuts, or change the submit key.

---

### When to use

- You want to change how you submit messages (e.g. Enter instead of Shift+Enter)
- You want to bind a slash command to a key combination
- You want to add a chord shortcut (two-key sequence, e.g. `ctrl+x ctrl+c`)

---

### Steps

#### 1. Read the current keybindings file

Read `~/.claude/keybindings.json`. If it doesn't exist, start from `[]`.

---

#### 2. Identify the desired change

Common requests and their binding format:

**Change the submit key:**
```json
[
  { "key": "enter", "command": "sendMessage" },
  { "key": "shift+enter", "command": "insertNewline" }
]
```

**Bind a slash command to a key:**
```json
[
  { "key": "ctrl+shift+r", "command": "runCommand", "args": "/tw-pr-sync" }
]
```

**Chord shortcut (two-key sequence):**
```json
[
  { "key": "ctrl+x ctrl+s", "command": "sendMessage" }
]
```

**Available commands:** `sendMessage`, `insertNewline`, `runCommand`, `clearConversation`, `openHistory`, `focusInput`, `toggleSidebar`

---

#### 3. Add or modify the binding

Update the array in `~/.claude/keybindings.json`. If a binding for that key already exists, replace it. If adding a new one, append to the array.

---

#### 4. Write the file and confirm

Write the updated `~/.claude/keybindings.json`. Report the new binding and note that changes take effect immediately (no restart required).
