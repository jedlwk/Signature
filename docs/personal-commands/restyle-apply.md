---
description: Apply the changes Jed approved in STYLE_PLAN.md, then check them
argument-hint: [all | file N | 1.1 to 1.4 | P0]
---

Apply mode. Apply the approved changes in STYLE_PLAN.md: $ARGUMENTS

Load the jed-writing-style skill (`~/.claude/skills/jed-writing-style`) and follow `references/plan.md`,
stage two.

1. Read `STYLE_PLAN.md`. Approved means ticked boxes, or what Jed said above. If nothing is approved and
   Jed said nothing, ask. Never assume everything.
2. Make it safe to undo. In a git repo the editor skips files with uncommitted changes and says so, so tell Jed to commit
   or stash first. Outside git, pass `--backup .signature-backup/<timestamp>`.
3. Write the approved items to `.signature-backup/<timestamp>/edits.json` exactly as the plan words them (so it stays
   as a record and not in the project), then run
   `python3 ~/.claude/skills/jed-writing-style/scripts/apply_edits.py .signature-backup/<timestamp>/edits.json --dry-run`, then again without `--dry-run`. This one script edits
   every file type, including Word and PowerPoint. Never edit files by hand. Outside git, add
   `--backup .signature-backup/<timestamp>` to the real run. In a git repo leave it off, so the editor can
   skip files with uncommitted changes.
4. Skipped changes are reported, not forced. Don't retry them with looser text. Tell Jed.
5. Run `python3 ~/.claude/skills/jed-writing-style/scripts/ai_check.py` on each changed file.
6. Update the plan (replace the "Nothing has been changed yet" line), then report what changed, what was skipped and why,
   and the new scores. Mention that `STYLE_PLAN.md` and `.signature-backup/` are working files. Don't commit.
