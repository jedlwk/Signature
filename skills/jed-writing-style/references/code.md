# Code

Code is the one place the voice mostly steps back. Clarity beats warmth. Checker register: `code`.

## Contents
- Who wins when rules clash
- Comments
- Names
- Docstrings and types
- Error messages and logs
- Commit messages and pull requests
- Snippets inside docs
- Explaining code to Jed
- Checklist

## Who wins when rules clash

1. A rubric, template or the team lead's example. ("follow the lead's example" meant exactly this.)
2. The repo's own conventions: naming, comment density, idiom, formatter.
3. A CLAUDE.md in the folder.
4. Jed's personal style below, only when none of the above says anything.

## Comments

Comment the why, never the what. Only on lines that would surprise the next reader.

| Skip | Write |
|---|---|
| `# loop through rows` | nothing |
| `# This function computes the correlation.` | nothing, or a one-line docstring if it is public |
| `# use 5 here` | `# 5 trading days, one week of lag` |
| `# fix bug` | `# api returns 200 with an empty body when the id is stale, so check length not status` |

**Jed's personal comment style** (CS7646), for personal and course code with no house style:
short, lowercase, abbreviations fine ("corr", "feat", "cols"), like explaining to a classmate.
Example: `# corr on log returns, raw prices trend together and inflate it`. In shared or team repos, match
the repo instead.

**Do not write:** jokes, "This function is used to...", generated "Step 1:" scaffolding (numbered <!-- signature:ignore-line -->
steps are fine when they mirror a real algorithm or spec), `NOTE:` banners, a changelog in the <!-- signature:ignore-line -->
comments, or comments about code that was removed.

## Names

- Names say what a thing is. `routes_shortlist.py`, not `routes_v2.py`.
- Realistic example data in anything a customer sees: `cam01-000123`, `frame_00123.jpg`. Never `foo`
  and `bar`.
- No stale names. Rename when the meaning changes ("fix all the stale nums. and stale code").

## Docstrings and types

- No unnecessary docstrings or type annotations on code you didn't change.
- Public functions get one plain sentence on what they do and what they return, if the name doesn't
  already say it.
- Don't restate the signature in prose.

## Error messages and logs

Written for whoever sees them at the worst time.

- Say what happened and what to do. `Field 'signature_date' not found. Available: customer_name, order_total.`
- Plain words. No "Oops!", no exclamation marks, no emoji. <!-- signature:ignore-line -->
- No dashes in strings. Use a colon.

## Commit messages and pull requests

*Likely*, not much direct evidence. Keep it simple.

- Subject: one plain line saying what changed, under about 60 characters. `Fix stale ids in shortlist route`.
- Body, only if the why isn't obvious: one or two short sentences.
- No "enhance", "improve overall", "various fixes", "minor tweaks", "robust", "comprehensive". <!-- signature:ignore-line -->
- PR description: what changed, why, how it was checked. Show proof (test output, screenshot)
  rather than a long write-up.
- Follow the attribution lines the session's instructions give, if any.

## Snippets inside docs

Short, runnable, commented only where a line would surprise (`# on macOS: base64 -i`), and easy to
copy. One command per block. Realistic names. No prompt symbol (`$`) and no interleaved output.

## Explaining code to Jed

Brief, with proof. Say what changed and show it runs. Bullets are fine here because this is working
talk, not a deliverable.

## Checklist

- [ ] Matches the repo around it
- [ ] Comments say why, only where surprising
- [ ] No stale names, numbers or comments
- [ ] No dashes in comments or strings
- [ ] Error messages say what to do
- [ ] Commit message is one plain line
- [ ] `python3 scripts/ai_check.py <file>` is clean (reads comments and docstrings only)
