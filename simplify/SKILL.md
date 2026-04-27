---
name: simplify
description: Reviews recently changed code for reuse, quality, and efficiency, then fixes any issues found. Run after implementing a feature to clean up the diff.
---

## Task: Simplify

Review recently changed code for reuse, quality, and efficiency, then fix any issues found. Run after implementing a feature to clean up the diff.

---

### When to use

- After finishing a feature implementation, before opening a PR
- When code feels repetitive or over-engineered after a fast first pass
- When you want a second-pass review focused on cleanup, not correctness

---

### Steps

#### 1. Get the diff

```bash
git diff HEAD
# or, if changes are staged:
git diff --cached
```

If the user specifies files or a commit range, scope the diff accordingly.

---

#### 2. Read each changed file in full

For each file in the diff, read the complete file — not just the changed lines — to understand the full context.

---

#### 3. Review for these issues (in priority order)

| Issue | What to look for |
|-------|-----------------|
| **Duplication** | Logic repeated 2+ times that could be a shared helper |
| **Dead code** | Variables assigned but never used, unreachable branches |
| **Over-abstraction** | Abstractions introduced for a single call site |
| **Unnecessary complexity** | Conditions that can be simplified, early returns that flatten nesting |
| **Inconsistency** | Style or patterns that diverge from the surrounding file |
| **Spec creep** | Code that handles hypothetical cases not required by the task |

---

#### 4. Fix issues found

Make targeted edits. Do not refactor beyond the changed files. Do not add comments, types, or docstrings to code you didn't change.

---

#### 5. Report back

List what was changed and why. If nothing needed fixing, say so.
