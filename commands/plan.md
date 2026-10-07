---
description: Plan a change across this whole project and write STYLE_PLAN.md. The default is bringing it into Jed's style. Changes nothing until approved
argument-hint: [purpose in plain words] [paths] [--code] [--strings] [--exclude glob]
---

Plan mode. Make a plan for a change across this project with the jed-writing-style skill: $ARGUMENTS

Load the jed-writing-style skill and follow `references/plan.md`, stage one. If Jed stated a purpose in words
above (for example "rename Acme to Zenith"), the plan is for that purpose. If not, the purpose is Jed's writing
style. In short:

1. Run the scanner from the skill folder. For style: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/plan_scan.py --json`. For a rename or a
   fact change: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/jed-writing-style/scripts/plan_scan.py --find "<text>"`. Add any paths or options Jed gave above.
2. Check the scope, read the project's own rules, then draft the changes.
3. Write `STYLE_PLAN.md` in the project root.
4. Stop. Reply with the plan's path, the counts, and how to approve.

This stage is read-only. `STYLE_PLAN.md` is the only file you may create. Do not edit anything else, and
do not apply the plan. Wait for Jed to approve.
