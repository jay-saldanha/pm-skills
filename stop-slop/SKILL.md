---
name: stop-slop
description: Eliminate predictable AI writing patterns from prose. Rewrites text to be direct, specific, active-voice, and human-sounding. Run on any prose the user provides or pastes.
disable-model-invocation: false
---

## Task: Stop Slop

Rewrite the prose the user provides to eliminate AI writing patterns. Apply every rule below. Do not explain the rules — just deliver the rewritten text, then the score.

---

### Core Rules

**1. Cut filler phrases.**
Remove throat-clearing openers ("It's worth noting that", "Let's dive into", "In today's world"), emphasis crutches ("truly," "really," "deeply," "incredibly"), and all adverbs. See `references/phrases.md`.

**2. Break formulaic structures.**
Avoid binary contrasts ("not X, it's Y"), negative listings, dramatic fragmentation, rhetorical setups ("What does this mean for you?"), false agency. See `references/structures.md`.

**3. Use active voice.**
Every sentence needs a human subject doing something. No passive constructions. No inanimate objects performing human actions ("the complaint becomes a fix," "the decision emerges").

**4. Be specific.**
No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every," "always," "never") doing vague work.

**5. Put the reader in the room.**
No narrator-from-a-distance voice. "You" beats "People." Specifics beat abstractions.

**6. Vary rhythm.**
Mix sentence lengths. Two items beat three. End paragraphs differently. No em dashes.

**7. Trust readers.**
State facts directly. Skip softening, justification, hand-holding.

**8. Cut quotables.**
If it sounds like a pull-quote, rewrite it.

---

### Quick Checks Before Delivering

Go through each item. Fix any that apply.

- Any adverbs? Kill them.
- Any passive voice? Find the actor, make them the subject.
- Inanimate thing doing a human verb ("the decision emerges")? Name the person.
- Sentence starts with a Wh- word ("What this means is...")? Restructure it.
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Any "not X, it's Y" contrasts? State Y directly.
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Narrator-from-a-distance ("Nobody designed this")? Put the reader in the scene.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.

---

### Output Format

1. **Rewritten prose** — clean, no commentary, no "Here is the revised version:" intro.
2. **Score** — rate each dimension 1–10:

| Dimension   | Question                     | Score |
|-------------|------------------------------|-------|
| Directness  | Statements or announcements? |       |
| Rhythm      | Varied or metronomic?        |       |
| Trust       | Respects reader intelligence?|       |
| Authenticity| Sounds human?                |       |
| Density     | Anything cuttable?           |       |
| **Total**   |                              | /50   |

If total is below 35: note which dimensions to revisit.

---

See `references/examples.md` for before/after transformations.
