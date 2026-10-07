# Plan mode: change a whole project

Use this when Jed wants a change made across everything a project says. The usual job is bringing it into
his writing style: "update my docs to my style", "restyle this repo", `/signature:plan`. It also handles
other jobs, such as renaming a term or updating a fact everywhere. It works in two stages with a hard stop
between them. Stage one writes a plan and changes nothing. Stage two applies only what Jed approved.

## Contents
- Purposes
- If the scripts can't run
- The rules
- Stage one: write the plan
- The plan file
- Approving
- Stage two: apply
- Checklist

## What it covers

Every kind of writing in a project that can be edited safely.

| File type | What is read and edited |
|---|---|
| `.md` `.markdown` `.txt` `.rst` `.adoc` | The whole text |
| `.docx` | Body, headers, footers, footnotes and endnotes. Only the text changes |
| `.pptx` | Every slide in display order, and the speaker notes. Only the text changes |
| `.html` `.htm` | Visible text. Never tags, attributes, scripts or styles |
| `.ipynb` | Markdown cells |
| Source files, with `--code` | Comments and docstrings |
| Source files, with `--strings` | Comments, and user-facing strings such as error messages and UI copy |

Not editable here, and listed in the plan with the reason: `.pdf` (edit the file it came from), `.xlsx`,
and old `.doc` and `.ppt` files. A slide that is a picture has no editable text, and the plan says so.

## Purposes

Jed can state a purpose in plain words after the command. With none, the purpose is his writing style.
Every purpose uses the same two stages, the same plan file and the same editor.

| Purpose | Example | How to gather the changes |
|---|---|---|
| **Style** (the default) | `/signature:plan` | `scripts/plan_scan.py --json` ranks files by style problems |
| **Rename a term** | `/signature:plan rename Acme to Zenith` | `plan_scan.py --find "Acme" --ignore-case` lists every place. Use `Where: all` |
| **Update a fact** | `/signature:plan change 40 users to 55` | `plan_scan.py --find "40"` and read each match. Change only the ones that mean this fact |
| **Remove a name** | `/signature:plan anonymise client names` | `plan_scan.py --find` for each name. Replace with a placeholder Jed approves |
| **Tighten** | `/signature:plan cut every slide to two lines` | Read the units with `apply_edits.py --units`, then rewrite the long ones |
| **Anything else** | `/signature:plan make the tone warmer` | Read the units, draft the rewrites, keep every fact |

For a purpose other than style, write the purpose at the top of the plan under Scope. Don't add style
changes Jed didn't ask for, though a single sentence at the end may offer to run the style plan next.
Everything under "The rules" still applies, and a rename must not touch quotes, code, names that look
the same but mean something else, or text Jed didn't write.

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
- **Never stash, reset or check out Jed's files to look at an original.** Get the old version with
  `git show HEAD:<path>`, or from the backup folder. Those leave the working tree alone.
- **Plan the pattern, not every instance.** A file with 200 dashes gets one rule with a count and
  three examples, not 200 rows. Write it with `Where: all` and a short Before such as "serves as".
- **Every change has a Where.** In `.docx`, `.pptx`, `.html` and `.ipynb` files it is the unit number the
  scanner gave (`unit` in the JSON). In text and code files it is the line. The editor uses it to
  pick the right match when the same words appear twice.
- **A Before text is the words, never markup.** In HTML it is the visible text, such as `Acme`, never
  `<title>Acme</title>`. The editor only matches text, and a Before with tags in it is not found.
- **In Word and PowerPoint, one change is one paragraph.** The Before text must sit inside a single
  paragraph, copied exactly as `scripts/apply_edits.py --units <file>` prints it. Split anything longer.

## If the scripts can't run

Some sessions refuse to run code that was just downloaded, or can't run commands at all. Say so at the top of
the plan under Scope, in one line, and carry on by hand. Don't pretend the scanner ran.

- Find the places with grep, and read the text inside Word and PowerPoint files from their XML.
- Use `Where: all` only for a plain rename. For anything else, name the slide or paragraph in words.
- Tell Jed to re-read the units with `apply_edits.py --units` before applying, or to install Signature with
  `./install.sh`, which is the reliable route.
- At apply time, never edit a Word or PowerPoint file by hand. Give Jed the find and replace table from
  `references/office.md` instead.

## Stage one: write the plan

1. **Scan.** Run the scanner from this skill's folder. Pass any paths Jed gave.

   ```bash
   python3 scripts/plan_scan.py --json
   ```

   It respects `.gitignore`, skips agent files, sample data, transcripts, archives and logs, and
   ranks files worst first. Add `--code` if Jed asked for code comments, and `--strings` for
   user-facing text inside code. Each finding carries a `where` label and a `unit` number. The options
   are in `docs/restyle.md` of the Signature repo.
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
  - Where: line 12
  - Before: <exact text>
  - After: <exact text>
  - Why: no dashes as punctuation. A comma continues the thought.
- [ ] **1.2** pattern, 14 places, P1 "serves as"
  - Where: all
  - Before: serves as
  - After: is
  - Why: plain verbs.
- [ ] **1.3** slide 3, P1 banned word
  - Where: unit 41 (Slide 3, paragraph 2)
  - Before: <exact text from one paragraph>
  - After: <exact text>
  - Why: plain words.

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
   - Outside git, you will pass `--backup .signature-backup/<timestamp>` in step 4, so the originals are
     kept.
3. **Write the approved items to `edits.json`** in `.signature-backup/<timestamp>/`, so it stays as a
   record of exactly what was applied and doesn't litter the project. One entry per item, in the plan's
   own words. Don't rephrase the Before or After text. A pattern item gets `"all": true`.

   ```json
   {"edits": [{"id": "1.1", "file": "README.md", "before": "...", "after": "...", "where": 12}]}
   ```
4. **Run the editor.** It does every edit, for every supported file type, and you never edit files by
   hand. Dry run first, then for real.

   ```bash
   python3 scripts/apply_edits.py .signature-backup/<timestamp>/edits.json --dry-run
   python3 scripts/apply_edits.py .signature-backup/<timestamp>/edits.json
   ```

   Outside git, add `--backup .signature-backup/<timestamp>` to the real run. In a git repo leave it
   off. Git is the undo there, and without `--backup` the editor skips any file that has uncommitted
   changes.

   Items marked NEEDS FACT keep a `[placeholder]` in their After text, and the editor skips them
   until Jed has filled it in. Don't remove the brackets yourself to get around that.

   It makes exact replacements only. Word and PowerPoint files change only the text, so formatting and
   everything else stays as it was. A change whose Before text isn't found, or is found more than once
   without a Where, is skipped and reported. Never retry a skipped change with looser text. Tell Jed.
5. **Check again.** Run `scripts/ai_check.py` on each changed file with its register. Fix anything the
   edit introduced, with another edits file. One more pass at most.
   For every changed `.docx` or `.pptx`, also run `scripts/verify_office.py <file> --git` (or `--against`
   the backup). Then follow `references/office.md`. It says what to do with each result, how to check a
   slide that grew, what a session that can open Word or PowerPoint should do, and what to give Jed when
   the session has no shell.
7. **Update the plan.** Replace the line "Nothing has been changed yet" with what was applied and what
   wasn't. Mark applied items, and mark skipped ones with the reason the editor gave. Add the date, and
   a before and after score for every file you changed.
8. **Report.** Files changed, changes applied, changes skipped and why, and the new scores. For Word and
   PowerPoint files, end with the lines from `references/office.md`: what was checked, what was looked
   at, and what Jed should check. Show
   `git diff --stat` if it's a repo. Don't commit unless Jed asks. Say that `STYLE_PLAN.md` and
   `.signature-backup/` are working files Jed can delete or add to `.gitignore`.

## Checklist

- [ ] Stage one wrote only `STYLE_PLAN.md`
- [ ] Local rules are listed and followed
- [ ] Every change has an exact before, an after and a reason
- [ ] Nothing in the plan needs a fact the file doesn't contain, except items marked NEEDS FACT
- [ ] The reply ends at the plan. No edits before approval
- [ ] Apply: safe to undo, done with `apply_edits.py`, skipped items reported, checker run after
