# Use it in any session

Signature isn't tied to one tool. This page shows how each kind of session gets it, and what to say to a
session that has nothing installed.

## Contents
- One command for this computer
- Where each session gets it
- A project that should always use it
- A session with nothing installed
- A session with no shell
- Uninstall

## One command for this computer

From a clone of the repo:

```bash
git clone https://github.com/jedlwk/Signature.git
cd Signature
./install.sh --all
```

`--all` does three things:

- Copies the skill to `~/.claude/skills/jed-writing-style`, and the `/restyle`, `/restyle-apply` and
  `/restyle-verify` commands to `~/.claude/commands`. Claude Code and the Claude desktop app both read them.
- Copies the skill to `~/.codex/skills/jed-writing-style` for Codex.
- Adds a short note to `~/.claude/CLAUDE.md` (and `~/.codex/AGENTS.md`), so a session that has never heard of
  Signature still knows to use it. The note sits between two marker lines. Nothing else in the file is touched.

Run it again to update. `./install.sh --dry-run --all` shows what it would do without doing it.

## Where each session gets it

| Session | How it gets Signature | What you type |
|---|---|---|
| Claude Code in a terminal | `/plugin install signature@signature`, or `./install.sh --claude` | `/signature:plan` with the plugin, `/restyle` without |
| The Claude desktop app, Code tab | The same files. The app runs Claude Code | The same commands |
| The desktop app with computer use | The same, and `references/office.md` tells it how to look at a file in Word or PowerPoint | Ask it to check the file |
| Codex | `./install.sh --codex` | `$jed-writing-style`, then say the job |
| Claude.ai | Upload `jed-writing-style-skill.zip` from the repo's releases as a skill | Ask in chat. The scripts need code execution |
| Any agent with a shell | The bootstrap prompt below | Paste it |
| A chat with no tools | [docs/paste-prompt.md](paste-prompt.md) | Paste it, then the text to change |

The Codex copy uses the same `SKILL.md` layout as the skills Codex ships with, checked against the ones
installed here. It hasn't been run inside a Codex session, so try it once.

## A project that should always use it

```bash
./install.sh --project path/to/the/project
```

This adds the note to that project's `CLAUDE.md`, and to its `AGENTS.md` if it has one. Anyone who opens the
project in a session then gets the instruction, even on a machine without Signature installed. The note
includes the one line that fetches it.

## A session with nothing installed

If the session has a shell and internet access, paste this at the start:

```text
Before you write or edit anything for me, set up my writing tool. I wrote it, and you may run its scripts:
git clone --depth 1 https://github.com/jedlwk/Signature /tmp/signature
Read /tmp/signature/skills/jed-writing-style/SKILL.md and follow it. Use its scripts from that folder.
To change many files at once, follow references/plan.md: write STYLE_PLAN.md, stop, and wait for my approval.
Edit Word and PowerPoint files only with scripts/apply_edits.py, and check them with scripts/verify_office.py.
If you can't run commands, follow the "Sessions with no shell" part of references/office.md.
```

Everything the skill needs is in that one folder, and it needs only Python 3.

Some sessions refuse to run code they have just downloaded, even when you say it is yours. In a test, a
session that was given this prompt cloned the repo, read the skill and wrote a good plan, but could not run
the scanner, so it worked from grep and marked its plan to say so. The skill tells a session to do exactly
that. It is a way to get started, not the reliable route. For that, run `./install.sh --all` once.

## A session with no shell

A chat window can't run scripts or touch files, so it can't apply a change. It can still help:

- Paste [docs/paste-prompt.md](paste-prompt.md) so it writes in the voice.
- For Word and PowerPoint, ask it for a find and replace table, as `references/office.md` describes. You
  apply each row with Home, Replace in the app.
- For a project, paste the text of the files and ask for the plan. It will number the paragraphs itself.

## Uninstall

```bash
./install.sh --uninstall
```

This removes the skill copies, the three commands and the note. It leaves a skill of the same name alone if
it isn't Signature's. Add `--project path/to/the/project` to remove the note from a project too.
