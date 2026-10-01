# Scripts

Speaker scripts, video voiceovers, demo walkthroughs and recorded presentations. Written for the
ear, so it should sound like Jed talking, not a document read aloud. Checker register: `script`.
Evidence for this material is thinner than for documents, so some parts are *likely* and not proven.

## Contents
- Rules
- Length and timing
- Structure
- Saying numbers and names
- Demo walkthroughs
- Checklist

## Rules

- **Shorter sentences than documents.** Mean about 10 words, none over 25. One idea per breath.
- **Contractions yes.** "it's", "we'll", "don't". Uncontracted speech sounds stiff out loud.
- **Nothing that can't be said.** No brackets, no slashes, no "e.g.", "i.e.", "etc." or "&". Write
  them the way they would be spoken.
- **Open on a real question or moment**, like the LinkedIn post. "Where does AI actually belong in
  HR?" Then answer it.
- **One concrete, personal image** per section at most. That is what people remember.
- **Signpost plainly.** "So here's what we built." "Let me show you." These spoken transitions are
  fine here, even though they would be filler in a document.
- **Point at the screen, don't describe it.** Say what matters and let the screen show the rest.
- **Warm, not performed.** No stage-voice phrases like "Imagine a world where".
- **No invented colour.** Don't add an anecdote ("one team I worked with"), a time of day, a
  headcount or a derived figure to make it vivid. Use only what Jed gave you, or leave a
  placeholder such as [a short story from the project].
- **End on the next step or a real question.** A plain "thank you" is fine. A slogan is not.

## Length and timing

Speak at about 130 to 150 words a minute. Use 140 to plan. Don't guess the length. Measure it.
Testing showed every draft landing 10 to 35 percent short of the target, so run:

```bash
python3 scripts/ai_check.py script.md --register script --target-seconds 90
```

It counts only the spoken words (not `[Slide 1]` labels or the length line) and says how many words
the target needs. Quote the checker's number in the length line, not your own estimate.

| Length | Words |
|---|---|
| 1 minute | about 140 |
| 3 minutes | about 420 |
| 5 minutes | about 700 |
| 8 minutes | about 1,100 |

State the estimated length at the top of every script, and match any limit exactly. A recorded
roundtable presentation runs 5 to 8 minutes, so aim for 700 to 1,100 words.

## Structure

Short paragraphs, one per slide or scene, labelled to match the slide numbers.

```
Estimated length: 5 minutes (about 700 words)

[Slide 1]
Opening line that is a real question or moment.

[Slide 2]
The problem, in plain words. One number if it matters.
```

Square brackets are for the slide labels only. They are never spoken.

## Saying numbers and names

- Write numbers the way they are said. "about thirty HR leaders", "two million Singapore dollars",
  "nine in the morning".
- Spell out anything awkward to read aloud. "H2O dot AI", "M I G" for an acronym said by letter.
  Keep a name exact if it is said as a word ("RAG", "Keycloak").
- Avoid long strings of digits. Round them, and say "about".
- Don't put a URL in the spoken line. Say where to find it.

## Demo walkthroughs

- Say what you are about to do, do it, then say what happened. Three short beats.
- Tell people where to look. "Look at the top right."
- Keep a fallback line ready for when the demo is slow. "While that loads, here's what's happening
  under the hood."
- Never promise a result before it appears.

## Checklist

- [ ] Estimated length stated from the checker, and inside the limit (`--target-seconds`)
- [ ] Opens on a real question or moment
- [ ] Mean about 10 words, none over 25
- [ ] No brackets, slashes, abbreviations or ampersands in the spoken lines
- [ ] Numbers written the way they are said
- [ ] Ends on the next step or a question
- [ ] `python3 scripts/ai_check.py script.md --register script` is clean
