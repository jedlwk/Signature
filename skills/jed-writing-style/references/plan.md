# Plan mode: restyle a project

Use this when Jed wants a whole project brought into his writing style: "update my docs to my style",
"restyle this repo", `/signature:plan`. It works in two stages with a hard stop between them.
Stage one writes a plan and changes nothing. Stage two applies only what Jed approved.

## Contents
- The rules
- Stage one: write the plan
- The plan file
- Approving
- Stage two: apply
- Checklist

## The rules

- **Stage one is read-only.** The only file you may create is `STYLE_PLAN.md`. Never edit, move or
  delete anything else until Jed approves.
- **Stop after writing the plan.** Don't ask "shall I go ahead?" and then go ahead. Say where the
  plan is and how to approve it, then wait.
- **Local rules win.** A project's CLAUDE.md, CONTRIBUTING, rubric, template or house style beats
  this guide. Record what you found and follow it.
- **Never invent facts to fix a sentence.** If a rewrite needs a number, name or example that isn't
  in the file, mark it NEEDS FACT and leave a placeholder.
- **Change sentences, not meaning.** Never touch quotes, code blocks, data tables, names, numbers,
  legal or licence text, or text Jed didn't write.
- **Plan the pattern, not every instance.** A file with 200 dashes gets one rule with a count and
  three examples, not 200 rows.

## Stage one: write the plan

1. **Scan.** Run the scanner from this skill's folder. Pass any paths Jed gave.

   ```bash
   python3 scripts/plan_scan.py --json
   ```

   It respects `.gitignore`, skips agent files, sample data, transcripts, archives and logs, and
   ranks files worst first. Add `--code` only if Jed asked for code comments. The options are in
   `docs/restyle.md` of the Signature repo.
2. **Check the scope.** Read the folder table and the skipped list. If a folder looks like someone
   else's text (course material, a vendor's docs, test data), leave it out and say so in the plan. If
   more than about 60 files were scanned, show Jed the folder table and ask which folders to include
   before you draft. Otherwise carry on.
3. **Read the local rules.** CLAUDE.md, README and any style notes. List what changes your plan.
4. **Draft the changes** for the 10 worst files, or the files Jed named. Read each file. Take the P0
   and P1 findings. For each, write the exact before text, the after text and the rule behind it.
   Cap a file at 12 detailed changes and group the rest as patterns. Files below that cut go in a
   table so Jed can ask for them next.
5. **Check your own rewrites.** Run `scripts/ai_check.py` on your after text (with `--facts-text` for
   the facts in the file). A rewrite that adds a new tell is worse than the original.
6. **Write `STYLE_PLAN.md`** in the project root using the template below.
7. **Stop.** Reply with the path, the counts (files, changes, items that need facts), and the ways to
   approve. Nothing else.

## The plan file

<!-- signature:ignore-start -->

```markdown
# Style plan

Made on <date> with jed-writing-style <version>. Nothing has been changed yet.

## Scope
- Scanned <n> files in <folder>. Skipped <n> (<why>).
- Rules that win here: <what CLAUDE.md or the template says, or "none found">.
- Please confirm: <folders left out, or "nothing to confirm">.

## Summary
| # | File | Register | Score now | P0 | P1 | Changes | Needs facts |
|---|---|---|---|---|---|---|---|
| 1 | README.md | doc | 13.1 | 28 | 17 | 9 | 1 |

## Needs your input
- [ ] <a question only Jed can answer, such as a missing number>

## Changes

### 1. README.md (doc, score 13.1)
- [ ] **1.1** line 12, P0 dash
  - Before: <exact text>
  - After: <exact text>
  - Why: no dashes as punctuation. A comma continues the thought.
- [ ] **1.2** pattern, 14 places, P1 "serves as"
  - Before: "serves as the entry point" (and 13 more)
  - After: "is the entry point"
  - Why: plain verbs.

## Not changing
- <quotes, code, data, third-party text, anything skipped on purpose>

## More files
| File | Score | P0 | P1 |
|---|---|---|---|
| docs/setup.md | 4.2 | 6 | 8 |

## How to approve
Tick the boxes you want, or say: "apply all", "apply file 1", "apply 1.1 to 1.4", "apply all P0".
Then run `/signature:apply`.
```

<!-- signature:ignore-end -->

## Approving

Jed approves by ticking boxes in `STYLE_PLAN.md`, or by saying which items in chat. Anything not
approved stays as it is. Jed can also edit the After text in the plan, and the edited text wins.

## Stage two: apply

Run this only when Jed has approved something.

1. **Read the plan and work out what is approved.** Ticked boxes, or what Jed said. If nothing is
   approved and Jed hasn't said, ask. Never assume "all".
2. **Make it safe to undo.**
   - In a git repo, run `git status`. If a file you will change has uncommitted work, stop and tell Jed.
     Don't stash or commit for them.
   - Outside git, copy the files you will change into `.signature-backup/<timestamp>/` first.
3. **Apply each approved change** as an exact replacement of the Before text. If the Before text no
   longer matches, skip it and say so. Never guess a nearby match.
4. **Pattern items** apply to every instance the plan listed, and only those.
5. **Word and PowerPoint files.** Use the docx or pptx skill if one is available. If not, give Jed the
   paste-ready text for each change and don't pretend it was applied.
6. **Check again.** Run `scripts/ai_check.py` on each changed file with its register. Fix anything the
   edit introduced. One more pass at most.
7. **Update the plan.** Mark applied items. Add the date, and a before and after score for every file
   you changed.
8. **Report.** Files changed, changes applied, changes skipped and why, and the new scores. Show
   `git diff --stat` if it's a repo. Don't commit unless Jed asks.

## Checklist

- [ ] Stage one wrote only `STYLE_PLAN.md`
- [ ] Local rules are listed and followed
- [ ] Every change has an exact before, an after and a reason
- [ ] Nothing in the plan needs a fact the file doesn't contain, except items marked NEEDS FACT
- [ ] The reply ends at the plan. No edits before approval
- [ ] Apply: safe to undo, exact matches only, checker run after
