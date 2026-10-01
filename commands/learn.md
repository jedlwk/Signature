---
description: Learn from Jed's edits. Compare what Claude wrote with what Jed changed it to, and propose a rule or example
argument-hint: [before and after, or two file paths]
---

Learn mode. Turn Jed's correction into evidence for the style guide: $ARGUMENTS

Jed's corrections are the best evidence this guide has. Your job is to find the pattern, not to log
every edit.

1. Get the two versions. Jed may paste a before and an after, give two file paths, or say "compare
   what you wrote with what I changed". If there is no second version, ask for it.
2. Compare them. List what Jed changed, then name the pattern in one line. Examples: "cut the closing
   summary", "swapped a formal word for a plain one", "removed a dash".
3. Check whether the guide already covers it. Read the matching file in the jed-writing-style
   `references/` folder. If it is covered, say so. A repeated correction means the rule is
   too weak or too buried, so propose making it stronger or moving it up.
4. Propose the change. Give the exact text and the target file. Choose one:
   - a new rule or a stronger rule
   - a new before and after pair for `examples.md`
   - a new sample for `samples.md`, if the after text is writing Jed is happy with
5. Ask before writing anything. Do not edit the guide without a yes.
6. On a yes, append a short entry to the private log, and never to the public repo. Use
   `$CLAUDE_PLUGIN_DATA/corrections.md` if that variable is set, otherwise `~/.claude/signature/corrections.md`.
   Create the folder and file if needed. Each entry has the date, the pattern in one line, and
   a before and after pair.
7. Anonymise first. Replace client names, people's names, numbers and anything confidential with
   placeholders such as [client] and [number]. Never write the real ones into the log.
8. If the log now has two or more entries with the same pattern, say so, and propose promoting the
   pattern into the guide. The guide is only updated in a clone of the Signature repo. If there is no
   clone to hand, give Jed the exact text to add.
