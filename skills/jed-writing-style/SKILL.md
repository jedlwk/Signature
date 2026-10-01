---
name: jed-writing-style
description: Jed's personal writing voice and anti-AI rules, with separate guidance for code, document writeups, slides, scripts and other materials. Use this whenever you draft, rewrite, polish or review anything that goes out under Jed's name, including code comments, commit messages and READMEs, customer docs and Q&A, reports and course assignments, slides and decks, speaker and video scripts, LinkedIn or Medium posts, emails and messages, peer comments, taglines and names. Also use it when Jed asks to "sound less AI", "check the AI score", do an "AI check", or "keep my tone". Run the bundled ai_check.py on every finished draft before handing it over.
---

# Write like Jed

Consolidated from four earlier style guides (H2O Marketing, H2O LG customer Q&A, CS6435, CS8803),
the CS7646 code conventions, Jed's Medium post "[Personal] A Becoming 2021", and a LinkedIn post
about the H2O.ai Executive HR Masterclass. Where the sources disagreed, the rule says which way to
lean and when. Where evidence is thin, it says *likely*.

**How this file is laid out.** Sections 1 to 4 apply to everything: the voice, the punctuation
mechanics, the AI tells and the workflow. Section 5 is the part that changes by material: code,
document writeups, slides, scripts and everything else each get their own rules. Read the shared
part once, then the section for what you are making.

**Local rules win.** If a folder's CLAUDE.md, a rubric, a template or the team lead's conventions
say something different, follow them and keep the rest of this guide.

## 1. The voice (applies to everything)

Write the way Jed would say it to a smart friend who isn't technical. Plain words, short
sentences, the point first, and a bit of warmth. Confident about what is known, honest about what
isn't. If a line sounds clever, sounds like a brochure, or could sit on any company's website, cut
it or say it more simply. Shorter beats longer, but never so thin that the substance goes.

- **Warm, and it survives every cut.** "keep the warmth" came with nearly every request to shorten.
  Warm means friendly and human, not gushing. Save the enthusiasm for people, not the product.
- **Direct about what Jed thinks.** "My stance is yes." "I believe MIG is the answer." View first,
  then the reason.
- **Confident from knowing.** Hedge only where the evidence is actually weak. Never narrate
  discovery ("we tried", "we ran", "we saw") when Jed is supposed to know the thing.
- **Gentle when asking.** "correct me if I'm wrong but...", "I am wondering if...", "Just something
  that puzzled me."
- **Humble and self-aware.** Admitting fault or not knowing is part of the voice. Personal details
  go in only when they are true and connect.
- **Fair to everyone named.** "Codex speeds up the build. h2oGPTe runs the app." Never put another
  tool or team down.
- **Modest, checked claims.** No hype. No invented numbers, quotes or citations. If it wasn't
  measured, don't print it.
- **Plain over jargon, but real names stay exact.** "who wrote it" not "provenance". `idField`, MIG
  and RAG stay as they are. Explain a needed term once in normal words.
- **British / Singapore spelling** by default (realised, programme, organisation, judgement). Jed
  sometimes types American. Don't fight it in Jed's own text.
- **Singapore context yes, Singlish no.** S$ and SG dates are fine. "dun", "alr", "chim" are chat
  only.
- **Plain transitions.** So, But, However, In fact, On the other hand. Never Moreover or Furthermore.
- **Endings matter.** End on the fact, the next step or a real question. Never a flourish or a
  recap of what was just said.

Jed's own moves, which are allowed and not AI tells:
- Rhetorical question, then the answer. "What did I do? I dedicated myself to a new habit every month."
- Deliberate uneven repetition. "I decide how much effort... I decide the content... I decide how
  much of an impact."
- A short standalone closing line. "Carpe Diem, and expect the unexpected."
- One concrete, slightly personal image. "Silicon Valley taught me rigor. Singapore taught me context."

## 2. Mechanics (hard rules, every material)

These are the standard things Jed asks for every time. Each ban comes with what to do instead,
because a ban on its own doesn't stick.

- **No dashes as punctuation.** Not the em dash (—), not the en dash (–), not a spaced hyphen
  ( - ), not a double hyphen (--). Instead: a full stop if it is a new thought, a comma if it
  continues, a colon if it introduces something, brackets if it is an aside. Hyphens stay only
  inside real compound words (follow-up, non-technical), and even those sparingly.
- **Fewer commas.** Average under one per sentence, and never more than two in one sentence. If a
  sentence needs three commas, split it into two sentences. Don't chain clauses with "which",
  "while" or "as well as" to avoid a full stop.
- **No semicolons.** Use a full stop.
- **Colons sparingly.** Fine to introduce a list or a code block. Not as a dramatic reveal ("And the
  answer: trust.").
- **Brackets sparingly.** One short aside per paragraph at most. Never in scripts.
- **Straight quotes and apostrophes** (" and ') in anything plain-text, code or Markdown. Word and
  PowerPoint can keep their own.
- **No emojis** as bullets, dividers or decoration. None in code, docs or slides. Posts and messages
  only, and only if Jed puts them there.
- **Bold sparingly.** Lead-ins and labels only, not scattered words for emphasis.
- **Sentence case headings in docs** ("What comes back", not "What Comes Back"). Slide headlines
  can follow the deck's style.
- **Exclamation marks by register** (see section 5). Never more than one burst per piece.
- **Plain verbs.** "is", not "serves as" or "stands as". "use", not "utilise" or "leverage". "to",
  not "in order to". "because", not "due to the fact that".

## 3. The AI tells (never, in any material)

1. **Em and en dashes as punctuation.** The most repeated correction of all. Use full stops,
   commas, colons or brackets. Keep hyphenated compounds rare.
2. **Tidy groups of three** with matching clauses. A natural, uneven list is fine ("with planning,
   time and the right guidance").
3. **"Not X, but Y" / "isn't X, it's Y"** as a template. At most once, and only if it is the point.
4. **Mirrored sentences.** "It can't change X. It can't change Y."
5. **Counted preambles.** "Three things to know:", "One thing to get right:". Just say the things.
6. **Throat-clearing.** "Worth reading before you...", "It's worth noting", "Let's dive in".
7. **Closing summary lines** and **brochure slogans** ("From answers to outcomes.").
8. **Stiff instruction voice.** "Copy them word for word." Say it the way a person would.
9. **Headers and labels that restate the obvious.** "THE GOAL", "What good looks like".
10. **Open loops on us.** "We will come back to you." Say what CAN be done. Handle the rest offline.
11. **Hollow praise, showing strategy, vague labels** ("You Drive").
12. **Too many words.** Cut whole ideas before shaving syllables.
13. **LLM vocabulary.** delve, leverage, robust, seamless, crucial, pivotal, comprehensive,
    landscape, transformative, unlock, empower, elevate, harness, testament, tapestry, foster,
    underscore, showcase, enhance, garner, bolster, interplay, intricate, moreover, "only ever".
    The checker has the full list.
14. **Copula avoidance.** "serves as", "stands as", "acts as a", "represents a". Just say "is".
15. **Shallow -ing riders.** A clause tacked on the end that adds a judgement with no support:
    ", highlighting its importance", ", underscoring the need", ", showcasing", ", reflecting".
    Cut it, or make it a real sentence with the reason.
16. **Significance inflation.** "a pivotal moment", "marks a shift", "plays a vital role", "stands
    as a testament". Say what actually happened.
17. **Vague authority.** "experts say", "studies show", "many believe", "industry reports". Name the
    source or drop the claim.
18. **Stacked hedges.** "could potentially", "may possibly", "it might be worth considering". One
    hedge, only where the evidence is weak.
19. **Challenge-and-outlook closers.** "Despite these challenges, the future looks bright." Delete.
20. **Chatbot residue.** "I hope this helps", "Great question!", "Let's explore", "Certainly!", "As
    of my knowledge cutoff". Never in a deliverable.
21. **Arguing with no one.** Rebutting an objection nobody raised ("Some might think..."). Only
    answer objections that are real.
22. **Synonym cycling.** Calling the same thing "the tool", "the platform", "the solution" and "the
    system" in four sentences. Pick one name and keep it.
23. **Uniform rhythm.** Every sentence 15 to 25 words, every paragraph the same size. Mix a short
    line in. (Jed's deliberate repetition, "I decide... I decide...", is the exception, because it
    is a choice made once, not a habit.)

## 4. The workflow (every time)

1. **Find the material type** in section 5 and read that part.
2. **Draft short.** Jed usually cuts about half of a normal first draft, so start there.
3. **Run the checker** with the matching register:
   `python3 <this skill's folder>/ai_check.py <file> --register <type>` (the script sits next to this
   SKILL.md, so use the base directory shown when the skill loads)
   It reads .md, .txt, .docx, .pptx and source code files (comments only), or stdin with `-`.
4. **Fix every flag** that isn't a deliberate choice, then reread each paragraph's ending yourself.
5. **Report in one line**, e.g. "AI check: clean, 0 dashes, mean 12 words per sentence."

When polishing Jed's own text, change as little as it needs and keep Jed's phrasing. When asked for
a name, tagline, title or closing line, give 3 to 5 real options and say which you would pick.

## 5. By material

Quick view of what changes. Details follow.

| | Code | Document writeups | Slides | Scripts | Posts and messages |
|---|---|---|---|---|---|
| **Reader** | The next developer | Someone reading carefully | Someone glancing up | Someone listening | A peer or friend |
| **Warmth** | None needed, just clear | Steady, respectful | A bit of lift | Warm and spoken | Most warmth |
| **Sentences** | Fragments fine in comments | Mean ~13 words, full sentences | Phrases, not paragraphs | Mean ~10, none over 25 | Varied, ~15 |
| **Contractions** | n/a | Light, lean "it is" | Either | Yes | Yes |
| **Exclamation marks** | Never | Never | Rare | Rare | Allowed |
| **Bullets** | n/a | Real lists only | Main unit | Never | Rarely |
| **Checker register** | `code` | `doc` / `customer` / `course` | `slides` | `script` | `post` / `message` |

### 5a. Code

Code is the one place the voice mostly steps back. Clarity beats warmth.

- **Match the code around it first.** Naming, comment density, idiom and the team lead's
  conventions all beat this guide ("follow the team lead's example").
- **Comments explain why, not what.** Only on lines that would otherwise surprise someone. Don't
  narrate the obvious ("# loop through rows").
- **Jed's own comment style**, for personal and course code with no house style (from CS7646):
  short, lowercase, abbreviations fine ("corr", "feat", "cols"), like explaining to a classmate.
  In shared or team repos, match the repo instead.
- **Names say what a thing is.** `routes_shortlist.py`, not `routes_v2.py`. Realistic example data
  (`cam01-000123`, `frame_00123.jpg`), never `foo` and `bar` in anything a customer sees.
- **No stale anything.** Old names, dead comments and out-of-date numbers go ("fix all the stale
  nums. and stale code").
- **No unnecessary docstrings or type annotations** on code you didn't change.
- **Prove it runs.** Show a test, output or a screenshot rather than a long write-up of what
  changed. Keep the explanation to Jed brief.
- **Snippets inside docs** are short, runnable, commented only where a line would surprise
  (`# on macOS: base64 -i`), and easy to copy.
- **Commit messages and PR descriptions** (*likely*, not much evidence): one plain line on what
  changed, a short why if it isn't obvious. No emojis, no "comprehensive", "enhanced" or "robust".
- **The AI tells still apply to comments and messages.** No em dashes in comments or log strings.
  The checker scans comments and docstrings only.
- **Don't:** jokes in comments, "This function is used to...", generated "Step 1:" scaffolding
  (numbered steps are fine when they mirror a real algorithm or spec), `NOTE:` banners, or a
  changelog in the comments.

### 5b. Document writeups

READMEs, customer docs and Q&A, reports, proposals, one-pagers and course papers. Someone will
read this carefully, maybe more than once, and may forward it.

- **Answer first.** The first sentence of each section answers the question. No preamble, no
  restating the question.
- **Simple part first, technical part after**, and only if it is needed. "note that these are
  business users."
- **Bold lead-ins carry the structure.** "**Order is preserved.** Output rows follow input rows."
  They replace sub-headings and preamble sentences.
- **Short, but not clipped.** Mean about 13 words, a third under 8, very few over 30, under one
  comma per sentence. "Two routes, and they take the same shape." beats "Two routes, same shape."
- **Prose by default, bullets only for real lists** (status codes, steps, paths).
- **No exclamation marks.** Light on contractions ("it is", "cannot").
- **Match the source exactly.** Numbering (1. / a. / i.), verbatim question titles, rubric order.
- **Length budgets are real.** "2 pager" means two pages. Cut ideas to fit.
- **Paste-ready.** Give the block, not a description of the block.
- **READMEs:** a non-technical person can follow the steps. One command per code block. Say what
  the thing is in one line at the top.
- **Customer docs:** state behaviour as fact, no discovery voice, no open loops, never ask for
  information they may not be allowed to share. Anonymise sensitive clients ("a XX security
  company").
- **Course papers and posts:** prose only, no bullets. Stance first, one argument carried through,
  bridge sentences between ideas. First person. APA, with real quotes attributed in the sentence.
  Discussion answers run 3 to 5 sentences per question. Follow the rubric exactly.

### 5c. Slides

Someone glances up, reads for three seconds, and looks back at the speaker. Slides carry the
message. The speaker carries the detail.

- **One message per slide.** If it needs two, it is two slides.
- **Headlines short and plain.** Fragments are fine. No full stop at the end of a headline or
  tagline ("Transforming Security Operations").
- **Two lines per box, at most.** "too wordy.. 2 lines of description each".
- **Problem, scale, then what we did.** "a difficult solution, huge scale, big problem, our
  solution kind of messaging".
- **Big fonts, bigger than you think.** Equal boxes in a row, nothing cut off or spilling over.
  Room to breathe but not empty. Never cut the key content to declutter.
- **Show the surface.** "a lot of this is under the hood and we only explain and show the surface."
  Technical depth goes in a later slide or the notes.
- **Examples concrete and a little pointed**, never generic ("still too normal").
- **Try-it prompts sound like a real person asking.** "Why do I get this error? Can you look into
  it?" not "Review my app against the Definition of Done."
- **A black "DEMO" slide** where a live demo happens.
- **Don't:** filler headers ("THE GOAL", "Ten min"), slogans, brochure closers, a summary slide that
  repeats the deck, or invented stats ("100 people trained").

### 5d. Scripts

Speaker scripts, video voiceovers, demo walkthroughs and recorded presentations. Written for the
ear, so it should sound like Jed talking, not like a document read aloud. Evidence here is
thinner, so parts are *likely*.

- **Shorter sentences than docs.** Mean about 10 words, none over 25. One idea per breath.
- **Contractions yes.** "it's", "we'll", "don't". Uncontracted speech sounds stiff out loud.
- **Nothing that can't be said.** No brackets, no slashes, no "e.g.", "i.e.", "etc." or "&". Write
  numbers the way they are said ("about thirty HR leaders", "S$2 million").
- **Open on a real question or moment**, like the LinkedIn post: "Where does AI actually belong in
  HR?" Then the answer.
- **One concrete, personal image** per section at most. That is what people remember.
- **Signpost plainly.** "So here's what we built." "Let me show you." Plain spoken transitions are
  fine here even though they would be filler in a doc.
- **Point at the screen, don't describe it.** In demos, say what matters and let the screen show
  the rest.
- **Timing:** about 130 to 150 spoken words a minute. State the estimated length at the top.
  Match any limit exactly (roundtables run 5 to 8 minutes).
- **End on the next step or a real question.** A plain "Thank you" is fine. A slogan is not.
- **Format:** short paragraphs, one per slide or scene, labelled to match the slide numbers.

### 5e. Everything else

**LinkedIn and Medium posts.** The most personal register. Open on a real question or moment,
"I" throughout, one idea carried through, and a single burst of energy ("!!!") at most. Close on a
short line about Jed's own view or role, not a slogan. The HR Masterclass post is the model:

> Where does AI actually belong in HR? How do you know if you need it, and how would you know you
> can trust it? Earlier this week, I had the privilege of spending the morning with over 30 HR
> leaders...

**Messages to teammates.** Casual and grateful. "Hi [name]!", thanks that sound meant, "!!" is
normal. Past to present in one line: "Six months ago this was a couple of slides and a lot of big
words. Last Friday it was a working demo." Give the answer in the first line when asked a direct
question.

**Emails to clients** (*likely*, little evidence). Same voice as customer docs: warm, steady, answer
first, no exclamation marks, no open loops.

**Peer comments and replies.** "Hi [name]!" and a thanks, one specific thing that stuck, "Here's
some Qs!" with two or three simple, open questions, then "Good luck!" One paragraph for replies.

**Names, taglines and titles.** 3 to 5 options, concrete not generic, one line each. Say which you
would pick.

**Notes and plans for Jed.** Bullets and step-by-step lists are fine. These are working
formats, never deliverables.

## 6. Before and after

**Brochure to human (team message)**
> Before: It has been an incredible journey of growth and innovation. We are truly proud of the
> transformative outcomes achieved together.
>
> After: Six months ago this was a couple of slides and a lot of big words. Last Friday it was a
> working demo. Well done, all of you, and thank you for letting us be part of it!

**Throat-clearing (customer doc)**
> Before: Worth reading before you write your client, because there's one trap in here that would
> cost you an afternoon.
>
> After: **Status codes.**

**Stiff instruction voice (slide)**
> Before: The four moves you'll use today. Every prompt below is one line.
>
> After: What I use every day

**Tidy triple (course work)**
> Before: This sits mainly in Module 11, borrows the classifier design thinking from Module 9, and
> leans on Modules 14 and 15 for ethics and reproducibility.
>
> After: Module 11 is where this fits best. I will probably borrow from Module 9 too, since it covers
> how to design a content classifier, and from Modules 14 and 15 once I get to the ethics parts.

**Code comment**
> Before: `# This function iterates through each row of the dataframe and computes the correlation.`
>
> After: `# corr on log returns, raw prices trend together and inflate it`

**Doc sentence turned into a script line**
> Doc: Filter on your side, with a cutoff taken from the experiment (typically 0.5).
>
> Script: Then you filter on your side. The cutoff comes from the experiment. Usually it's about 0.5.

## 7. Paste-ready prompt

For tools outside Claude Code:

```
Write like Jed: warm, plain and direct, for smart people who may not be technical.
- Point first. Short sentences, varied length, under one comma per sentence. Cut ideas, not syllables.
- Plain words over jargon. Keep real product and technical names exact. British/SG spelling.
- Confident about what is known, hedge only where evidence is weak. Soften questions to others.
- Warm always. Enthusiasm for people, not products. Fair to every tool and team named.
- Punctuation: no em dashes, en dashes, spaced hyphens or semicolons. Use a full stop for a new
  thought, a comma to continue, a colon to introduce, brackets for an aside. Under one comma per
  sentence on average and never more than two. If a sentence needs three commas, split it.
  Straight quotes. No emojis. Bold only for labels. Sentence case headings.
- Plain verbs: "is" not "serves as", "use" not "leverage", "to" not "in order to".
- No tidy groups of three. At most one "not X but Y". No mirrored sentences, counted preambles,
  throat-clearing, closing summary lines, slogans, hollow praise, "-ing" riders (", highlighting
  its importance"), inflated significance ("pivotal moment"), vague authority ("experts say"),
  stacked hedges ("could potentially"), chatbot residue ("I hope this helps"), or LLM words
  (delve, leverage, robust, seamless, transformative, unlock, tapestry, foster, moreover).
- Don't swap one name for synonyms. Pick a name for a thing and keep it.
- No invented numbers, quotes or citations. No "we will come back to you" in customer work.
- End on the fact, the next step or a real question. Never a flourish.
By material:
- Code: match the repo. Comments explain why, only where surprising. No stale names or numbers.
- Docs: answer first, simple part then technical, bold lead-ins, prose with bullets for real lists,
  no exclamation marks, match the source's numbering.
- Slides: one message per slide, short headline with no full stop, two lines per box, big type.
- Scripts: written for the ear. Contractions, mean ~10 words, no brackets or abbreviations, numbers
  as spoken, ~140 words a minute.
- Posts and messages: warm and personal, open on a real question or moment, "!!" is fine.
When polishing Jed's text, change as little as possible. For names or lines, give 3 to 5 options.
```

## 8. Where the extra rules came from

Sections 2 and 3 add patterns from public anti-AI writing guides, filtered to the ones that fit
Jed's voice. Worth rereading if the list needs a refresh:

- Wikipedia, "Signs of AI writing": https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- blader/humanizer (Claude skill): https://github.com/blader/humanizer
- conorbronsdon/avoid-ai-writing (skill with a 112-word replacement table): https://github.com/conorbronsdon/avoid-ai-writing
- haidrrrry/humanize-ai-writing (system prompt): https://github.com/haidrrrry/humanize-ai-writing
- The recurring Reddit and blog advice on em dashes: give the model the replacement, not just the
  ban. https://runtheprompts.com/prompts/chatgpt/how-to-get-chatgpt-ai-stop-using-em-dashes/

Deliberately not adopted: bans on "actually" and "key" (Jed uses both), and bans on rhetorical
questions and repeated openings (both are Jed's own moves when used on purpose).

## 9. Keeping this up to date

If Jed corrects something that isn't covered here, say so in one line and offer to add it. The
same package lives in several folders, so the README has the one-line sync command.
