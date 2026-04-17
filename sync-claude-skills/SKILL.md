---
name: sync-claude-skills
description: List all available Claude skills with explanations and sync the list to the Notion skills reference page.
disable-model-invocation: false
---

## Task: Sync Claude Skills to Notion

Read all locally installed Claude skills and update the Notion skills reference page with a complete, categorized list.

The Notion page is: `https://www.notion.so/sardine/List-of-Claude-skills-used-33dd52e0dd8b80baa764c9d6858b0253`
Skills live in: `~/.claude/skills/` (one subdirectory per skill, each containing a `SKILL.md`)

### Steps

1. **Read the system-reminder** at the top of the conversation — it lists all available skills under the `<system-reminder>` block with a one-line description for each.

2. **Also read each `SKILL.md`** file found under `~/.claude/skills/*/SKILL.md` to extract fuller descriptions from the `description:` frontmatter and the body text.

3. **Merge the two sources**: prefer the `SKILL.md` frontmatter `description` over the system-reminder snippet when both exist.

4. **Categorize skills** into these groups (add new categories as needed):
   - **NPS Pipeline** — skills prefixed with `nps-`
   - **Technical Writing / risk-docs** — skills related to the `sardine-ai/risk-docs` repo or the Asana TW queue
   - **Claude Code / Dev Utilities** — all remaining general-purpose skills

5. **Build a Notion page** with this structure (one `##` section per category, each containing a table):

   ```
   ## <Category Name>
   <one-sentence description of the category>

   | Skill | What it does |
   |-------|--------------|
   | `/skill-name` | Full description |
   ```

   For the NPS Pipeline section, add a `Phase` column between Skill and What it does.

6. **Update the Notion page** using the Notion MCP tool with `replace_content`.
   Page ID: `33dd52e0dd8b80baa764c9d6858b0253`

7. **Report back** with:
   - How many skills were found and listed
   - A link to the updated Notion page
   - Any skill directories that had no `SKILL.md` (and were skipped or sourced from system-reminder only)
