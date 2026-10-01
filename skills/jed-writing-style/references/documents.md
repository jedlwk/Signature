# Documents

READMEs, customer docs and Q&A, reports, proposals, one-pagers and course papers. The reader will
read this carefully, maybe more than once, and may forward it. Checker registers: `doc`, `customer`,
`course`.

## Contents
- Rules for every document
- README
- Customer docs and Q&A
- Reports, proposals and one-pagers
- Course papers and discussion posts
- Checklist

## Rules for every document

- **Answer first.** The first sentence of each section answers the question. No preamble, no
  restating the question.
- **Simple part first, technical part after**, and only if it is needed. "note that these are business
  users."
- **Bold lead-ins carry the structure.** "**Order is preserved.** Output rows follow input rows." They
  replace sub-headings and preamble sentences.
- **Short, but not clipped.** Mean about 13 words, a third under 8, very few over 30, under one comma
  per sentence.
- **Prose by default.** Bullets only for real lists: status codes, steps, paths.
- **No exclamation marks.** Light on contractions ("it is", "cannot").
- **Match the source exactly.** Numbering (1. / a. / i.), verbatim question titles, rubric order.
- **Length budgets are real.** "2 pager" means two pages. "max 2000" means 2000. Cut whole ideas to
  fit, don't shave syllables.
- **Numbers must be current and checked.** If it wasn't measured, don't print it.
- **Paste-ready.** Give the block, not a description of the block.
- **Sentence case headings.** "What comes back", not "What Comes Back".

## README

A non-technical person should be able to follow the steps.

Skeleton:

```
# Name

One line on what this is.

## What it does
Two or three short sentences. A before and after if it helps.

## Install
One command per code block.

## Use
The most common thing first.

## How it works
Short. Technical detail goes here, after the simple part.

## Update or fix
The one command someone will need later.
```

- One command per code block, no prompt symbol, no output mixed in.
- Say what the thing is in one line at the top.
- Keep it as short as it can be and still be complete. "some readme is too wordy. might overwhelm the
  non technical folks."

## Customer docs and Q&A

- **Answer in the customer's own numbering**, with their questions verbatim and in their order.
- **State behaviour as fact.** Never narrate testing or discovery ("we tried", "we ran", "we saw", <!-- signature:ignore-line -->
  "we deployed and checked"). Jed is supposed to know the product. <!-- signature:ignore-line -->
- **Never leave an open loop.** No "we are checking with the team", "we will come back to you", <!-- signature:ignore-line -->
  "happy to revert once there is something firm". Handle it offline. <!-- signature:ignore-line -->
- **Say what can be done.** A plain "no" is fine when the question is yes or no, then move straight
  to what works. Don't dwell on the gap.
- **Don't ask for what they can't tell you.** Cover the likely cases instead of asking a question a
  high-security customer cannot answer.
- **Be conservative with claims.** If a number wasn't measured, leave it out. Separate what is
  verified from what is expected.
- **Anonymise sensitive clients** ("a XX security company") unless told otherwise.
- **Close on what to do.** "So keep groups small, and keep your own record of which frame ids went
  into which request."

Answer skeleton:

```
**Short answer in bold.** One or two sentences that answer the question as asked.

The detail, in plain words. A code block if it helps, copyable.

What to do next, if there is anything.
```

## Reports, proposals and one-pagers

- Lead with the point or the ask. Background gets as few words as possible.
- One-pagers: a title that is a real question or claim. A one-line subtitle only if it earns its
  place. Headings that are easy to see. The outcome section gets the most room.
- Titles fit on one line.
- A section earns its place by answering something. Cut "THE GOAL" style headers that restate the
  obvious.

## Course papers and discussion posts

- **Prose only, no bullets** in anything submitted. A bulleted section will lose marks.
- **Stance first**, then one argument carried through the whole piece. Don't list separate
  observations.
- **Build one throughline.** The pieces should connect, not sit side by side.
- **Bridge between ideas** with one plain sentence.
- **Spend the words on the argument**, not the setup.
- **Use the reading as evidence.** Don't summarise it.
- **Attribute in the sentence.** "One participant said...", "Dillahunt asks...". No page numbers in
  discussion posts. In-text APA with page numbers is fine in papers.
- **Only quote from the real source.** Never invent a quote or a citation.
- **Hedge where the evidence is weak**, and nowhere else.
- **End on a genuine question** if one comes naturally. No neat takeaway.
- Discussion answers run 3 to 5 sentences per question. Label sections to match the prompt exactly.
- Follow the rubric's structure, font, spacing and page limits to the letter.
- AI disclosures follow the course's required components exactly.

## Checklist

- [ ] First sentence answers the question
- [ ] Simple part before technical part
- [ ] Source numbering and titles copied exactly
- [ ] Within the length budget
- [ ] Every number and quote is real
- [ ] No open loops, no discovery voice (customer docs)
- [ ] `python3 scripts/ai_check.py <file> --register doc` is clean
