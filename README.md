# signature

My writing voice as a Claude Code plugin, so every session knows how to write for me without being told.

## What it adds

| Part | What it does |
|---|---|
| `skills/jed-writing-style/SKILL.md` | The style guide. One shared voice and punctuation rules, then separate rules for code, document writeups, slides, scripts and posts. |
| `skills/jed-writing-style/ai_check.py` | A checker for the AI tells I keep removing. Pass `--register` for the material type. |
| `hooks/remind.py` | A session-start reminder to load the skill. Without it, Claude only loads the skill when it judges the task relevant. It adds one short paragraph and nothing else. |

## Install

From GitHub, once the repo is pushed:

```bash
/plugin marketplace add jedlwk/Signature
```

```bash
/plugin install signature@signature
```

From this folder, before it is on GitHub:

```bash
/plugin marketplace add ~/signature
```

```bash
/plugin install signature@signature
```

Start a new session after installing. The plugin applies to every project, so the per-folder copies
are no longer needed.

## Use

Nothing to do. Ask for anything written in my name, or say "AI check". To run the checker by hand:

```bash
python3 ~/.claude/plugins/cache/signature/signature/*/skills/jed-writing-style/ai_check.py draft.md --register doc
```

Registers: `general`, `code`, `doc`, `customer`, `course`, `slides`, `script`, `post`, `message`.

## Update

Edit `skills/jed-writing-style/SKILL.md` in this folder, bump `version` in `.claude-plugin/plugin.json`,
then run `/plugin marketplace update signature`.

## Outside Claude Code

Section 7 of `SKILL.md` has a paste-ready prompt for ChatGPT, Claude.ai and other tools.
