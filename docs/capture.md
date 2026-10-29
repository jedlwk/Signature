# Edit capture

Edit capture records what Claude writes and what you change before you commit it. Your edits are the most
honest signal of your voice there is. A score built from them can't be gamed by text that only looks like
yours. It costs you nothing once it is on.

It is off until you turn it on, and everything it keeps stays on your machine.

## How it works

1. Claude writes or edits a prose file (`.md`, `.txt`, `.rst`, `.adoc`). A hook saves Claude's version
   and notes which passages Claude wrote.
2. You edit the file and commit it, as usual.
3. At the start of each session, and whenever you run `capture.py pair`, Claude's version is compared
   with the latest commit within 14 days. Each passage Claude wrote is kept, edited or cut.
4. The result goes into `~/.claude/signature/edits.jsonl`. `capture.py report` and
   `/signature:learn --from-git` read it.

Only passages Claude wrote count. If Claude adds one paragraph to a file you wrote, your changes to the rest
of the file are your own work and are left out.

## Turn it on

The plugin brings the hooks. Without the plugin, `./install.sh --claude --capture` adds them to
`~/.claude/settings.json` and keeps a copy of the file first. Then:

```bash
python3 ~/.claude/skills/jed-writing-style/scripts/capture.py enable
```

Keep a folder out with `--exclude "*/client-work/*"`, or list paths in a repo's `.signatureignore`. Add
`--numbers-only` to keep the counts and never the text. `capture.py status` shows what is set, and `disable`
turns it off.

## Read it

```bash
python3 ~/.claude/skills/jed-writing-style/scripts/capture.py report --passages 10
```

The report shows the share of Claude's words you changed each week. A falling share means the drafts
are getting closer to you. It also lists the tells you removed and the words you cut and added most often.
`/signature:learn --from-git` turns a change you make again and again into a proposed rule, and asks before
writing anything.

## What it keeps, and for how long

| Where | What | How long |
|---|---|---|
| `~/.claude/signature/drafts/` | Claude's version of each file, waiting for a commit | Until it is paired, or 14 days |
| `~/.claude/signature/edits.jsonl` | Each pair: counts, the tells before and after, and the changed passages | 90 days |
| `~/.claude/signature/capture.json` | Your settings | Until you change them |

Only you can read these files. Nothing is sent anywhere, and nothing goes into a repo. Customer text should
stay out, so exclude those folders before you turn it on.

## Not covered yet

Commit messages, code comments, Word and PowerPoint files, and writing outside a git repo. Codex has no
matching hook, so only work done in Claude Code is recorded.
