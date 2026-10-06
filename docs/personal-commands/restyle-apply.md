---
description: Apply the changes Jed approved in STYLE_PLAN.md, then check them
argument-hint: [all | file N | 1.1 to 1.4 | P0]
---

Apply mode. Apply the approved changes in STYLE_PLAN.md: $ARGUMENTS

Load the jed-writing-style skill (`~/.claude/skills/jed-writing-style`) and follow `references/plan.md`,
stage two.

1. Read `STYLE_PLAN.md`. Approved means ticked boxes, or what Jed said above. If nothing is approved and
   Jed said nothing, ask. Never assume everything.
2. Make it safe to undo: check `git status` in a repo, otherwise back the files up to `.signature-backup/`.
3. Apply each approved change as an exact replacement. Skip any whose Before text no longer matches.
4. Run `python3 ~/.claude/skills/jed-writing-style/scripts/ai_check.py` on each changed file.
5. Update the plan, then report what changed, what was skipped, and the new scores. Don't commit.
