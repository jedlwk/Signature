---
description: Scan this project and write STYLE_PLAN.md, a plan to update the writing to Jed's style. Changes nothing until approved
argument-hint: [paths] [--code] [--exclude glob]
---

Plan mode. Make a plan to restyle this project with the jed-writing-style skill: $ARGUMENTS

Load the jed-writing-style skill (`~/.claude/skills/jed-writing-style`) and follow `references/plan.md`,
stage one. In short:

1. Run the scanner from the skill folder:
   `python3 ~/.claude/skills/jed-writing-style/scripts/plan_scan.py --json`
   Add any paths or options Jed gave above.
2. Check the scope, read the project's own style rules, then draft the changes for the worst files.
3. Write `STYLE_PLAN.md` in the project root.
4. Stop. Reply with the plan's path, the counts, and how to approve.

This stage is read-only. `STYLE_PLAN.md` is the only file you may create. Do not edit anything else, and
do not apply the plan. Wait for Jed to approve.
