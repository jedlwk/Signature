# Slides

Someone glances up, reads for three seconds, and looks back at the speaker. The slide carries the
message and the speaker carries the detail. Checker register: `slides`. It reads `.pptx` files and
flags any single line over 25 words.

## Contents
- Rules
- Slide patterns
- Layout
- Speaker notes
- What not to put on a slide
- Checklist

## Rules

- **One message per slide.** If it needs two, it is two slides.
- **Headlines short and plain.** Fragments are fine. No full stop at the end of a headline or
  tagline. ("Transforming Security Operations", not "Transforming security operations.")
- **Two lines per box at most.** "too wordy.. 2 lines of description each."
- **Problem, scale, then what we did.** "a difficult solution, huge scale, big problem, our solution
  kind of messaging."
- **Show the surface.** "a lot of this is under the hood and we only explain and show the surface."
  Depth goes on a later slide or in the notes.
- **Examples concrete and a little pointed**, never generic. "still too normal" was a rejection.
- **Try-it prompts sound like a real person asking.** "Why do I get this error? Can you look into
  it?" Not "Review my app against the Definition of Done."
- **Real numbers only.** "Already run at enterprise scale. 100 people trained" came off a slide
  because it couldn't be backed up.
- **Sensitive clients are anonymised.**

## Slide patterns

| Slide | Content | Keep it to |
|---|---|---|
| Title | Name of the talk, one plain subtitle | Two lines |
| Problem | What is hard and how big it is | One claim, one number |
| Scale | Why it matters at this size | One number and what it means |
| What we did | The solution in a sentence | A headline and three short boxes at most |
| Demo | A black slide that says DEMO | One word |
| Under the hood | The surface of how it works | A simple diagram, labels not sentences |
| Result | What changed | One outcome, one real number |
| Close | The next step | One line. No summary of the deck. |

## Layout

These are starting points. Match the deck's template if there is one.

- **Fonts bigger than you think.** "i need all fonts to be bigger", "increase the smallest font size
  by 1." A rough start: headline 32pt or more, body 20pt or more, nothing under 14pt.
- **Equal boxes.** "all the 5 boxes row should have the same height. do not spillover."
- **Nothing cut off or spilling out.** Check every box.
- **Balanced.** "too cluttered" and "too much empty space" were both complaints. Keep the key content
  and give it room.
- **Never cut the key content to declutter.** "the outcome is very important! do not declutter that!"
- **Easy to copy.** Put a prompt the audience will paste inline, right after the colon.

## Speaker notes

Notes carry what the slide leaves out. Write them as a script (see the scripts reference). Slide text
is phrases. Notes are sentences you would say.

## What not to put on a slide

Filler headers ("THE GOAL", "Ten min", "what good looks like"), slogans, brochure closers, a summary
slide that repeats the deck, vague labels ("You Drive"), a title that is a tagline, and claims you
can't back up.

## Checklist

- [ ] One message per slide
- [ ] No box over two lines
- [ ] Headlines have no full stop
- [ ] Fonts big, boxes equal, nothing spilling
- [ ] Every number is real and checked
- [ ] Client names anonymised if needed
- [ ] `python3 scripts/ai_check.py deck.pptx --register slides` is clean
