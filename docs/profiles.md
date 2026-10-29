# Profiles

A profile is one writer's voice in one folder. The skill's guides and the checker are the same for
everyone. The profile holds what is yours, from your rules and real writing to the habits the checker
should flag.

## Which profile is used

The checker looks in this order and takes the first it finds:

1. `--profile DIR` on the command line. A bare name like `starter` means a bundled profile.
2. The `SIGNATURE_PROFILE` environment variable, read the same way.
3. Your own profile in `~/.claude/signature/profile/`.
4. The bundled default, `profiles/jed/`.

`python3 scripts/ai_check.py --which-profile` prints the folder in use and its name. If a profile can't be
read, `--profile` stops with an error. A broken `SIGNATURE_PROFILE` falls back to the bundled default
and says so.

## What is in one

| File | What it holds |
|---|---|
| `profile.json` | The name, the checker's settings, its wording and the reminder each session starts with |
| `rules.md` | The short list of rules, read before every draft |
| `voice.md` | How you sound, the words you use and the ones you never use |
| `samples.md` | Real writing by you. `--voice` and `--baseline` measure it |
| `examples.md` | Before and after pairs. Optional |

Two profiles ship with the skill. `profiles/jed/` is mine and is the default for now. `profiles/starter/`
is blank. With it the checker flags general AI tells only, and `--voice` waits until you add samples.

## Checker settings

Everything under `checker` in `profile.json` is optional. Leave a setting out and the neutral default
applies.

| Setting | Neutral default | Jed's |
|---|---|---|
| `flag.dashes` | off | on |
| `flag.semicolons` | off | on |
| `flag.curly_quotes` | off, and `--fix` leaves them | on |
| `flag.emojis` | off | on, except in posts and messages |
| `max_commas` | 1.5 a sentence on average | 1.0 |
| `heavy_commas` | 4 in one sentence | 3 |
| `exclamations_allowed` | every register but `doc`, `customer` and `code` | not in `course` either |
| `short_floor` | 0.05 | 0.2 for `doc` and `customer` |
| `extra_banned_words` | none | "only ever", "mechanism", "psychosocial" | <!-- signature:ignore-line -->

`messages` changes the checker's wording. A key is either a tell's label like "invented anecdote" or a
`--voice` row like "words per sentence". `notes` holds the reason for each setting, so nobody has to
guess later.

The general AI tells are the same in every profile. That covers the word list and every pattern in
`references/ai-tells.md`.

## Make your own

1. Copy `profiles/starter/` to `~/.claude/signature/profile/`.
2. Add 150 words or more of your own writing to `samples.md`, each piece under its own heading.
3. Write `voice.md` and add to `rules.md` in your own words.
4. Run `ai_check.py --baseline` to see what your writing measures. Turn on the flags that match your
   habits in `profile.json`.
5. Check a few of your own pieces. If your own writing gets flagged, the profile is wrong, not you.

Your profile stays on your machine. `/signature:learn` can suggest rules from your edits as you go.

## Not in a profile yet

The guides in `references/` still carry some of my moves alongside the general craft. `SKILL.md` and the
commands still say "Jed". Calibration and the check history stay in `~/.claude/signature/`. These come
next, along with a command that builds a profile from your writing.
