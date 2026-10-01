# Examples

Before and after pairs, then one full run of the workflow. Every pair comes from a real correction
Jed made, or a lightly tidied version of one.

## Contents
- Before and after, by material
- A full run of the workflow

<!-- signature:ignore-start -->

## Before and after, by material

### Team message

> **Before:** It has been an incredible journey of growth and innovation. We are truly proud of the
> transformative outcomes achieved together.
>
> **After:** Six months ago this was a couple of slides and a lot of big words. Last Friday it was a
> working demo. Well done, all of you, and thank you for letting us be part of it!

Why: the real version has a past, a present and something you could check. The first has none.

### Customer doc, throat-clearing

> **Before:** Worth reading before you write your client, because there's one trap in here that would
> cost you an afternoon.
>
> **After:** **Status codes.**

Why: a bold label does the job a warning sentence was trying to do.

### Customer doc, narrating our own testing

> **Before:** We sent two frames with our own ids attached and they came back in the same order,
> laid out as our own field first and the model output after it.
>
> **After:** **Order is preserved.** Output rows follow input rows, laid out as your copied fields first
> and the model output last.

Why: Jed is supposed to know the product. State it as fact.

### Customer doc, open loop

> **Before:** A weights file trained outside the tool has no field in the detection settings today.
> Other problem types do accept one. We are checking with the team whether it can be opened up for
> detection, and will come back to you with a straight yes or no.
>
> **After:** Deleted. The answer ends on the two routes that work.

Why: never leave something outstanding on us. Say what can be done.

### Counted preamble

> **Before:** Three details cause most of the trouble on this route: [three bullets]
>
> **After:** **Two rules on this route.** The filename in `rows` has to match the uploaded filename, or
> you get a 400 naming the file. And `scoreMediaRequest` has to carry `fields`, `rows` and the media
> fields list.

Why: lead with the rules themselves. Don't announce the shape.

### Slide, stiff instruction voice

> **Before:** The four moves you'll use today. Every prompt below is one line.
>
> **After:** What I use every day

### Slide, a try-it prompt

> **Before:** TRY: Review my app against the Definition of Done.
>
> **After:** Try: Why do I get this error? Can you look into it?

Why: a person asking for help sounds like the second one.

### Slide, neutral about other tools

> **Before:** Codex only ever accelerates the build itself.
>
> **After:** Codex speeds up the build. h2oGPTe runs the app.

### Course work, the tidy triple

> **Before:** This sits mainly in Module 11, borrows the classifier design thinking from Module 9, and
> leans on Modules 14 and 15 for ethics and reproducibility.
>
> **After:** Module 11 is where this fits best. I will probably borrow from Module 9 too, since it covers
> how to design a content classifier, and from Modules 14 and 15 once I get to the ethics parts.

### Course work, jargon

> **Before:** Wilkinson's central mechanism is psychosocial rather than material.
>
> **After:** Wilkinson's point isn't really about money. It's about what the gap does to how people feel
> around each other.

### Course work, summarising instead of arguing

> **Before:** Dillahunt's paper looks at people in Detroit who mostly know others stuck with the same
> problems.
>
> **After:** I think the biggest barrier to cross-socioeconomic connection isn't access, it's trust.

### A question to someone senior

> **Before:** Is there a story for it, or is it still open?
>
> **After:** I am wondering if the difference I see here is in the method itself, or that one side
> simply has more to compare against. Just something that puzzled me.

### Peer comment

> **Before:** I came in knowing nothing about the topic and I followed the whole thing, which says a lot
> about how you built it.
>
> **After:** I had assumed it was an IP thing. Your version is that a company which cannot protect its
> model just goes back to sending my messages to the server, so it is actually my privacy on the line.
> I had not thought of it that way :O

### Code comment

> **Before:** `# This function iterates through each row of the dataframe and computes the correlation.`
>
> **After:** `# corr on log returns, raw prices trend together and inflate it`

### Doc sentence turned into a script line

> **Doc:** Filter on your side, with a cutoff taken from the experiment (typically 0.5).
>
> **Script:** Then you filter on your side. The cutoff comes from the experiment. Usually it's about 0.5.

<!-- signature:ignore-end -->

## A full run of the workflow

The task: write the opening of a LinkedIn post about a workshop.

**1. Material and mode.** A post. Draft mode. Open the posts-and-messages reference. Register: `post`.

**2. First draft (short, in the voice).**

<!-- signature:ignore-start -->

> I am thrilled to share that we hosted an incredible workshop last week — a truly transformative
> experience that showcased the robust potential of AI in the workplace. Moreover, attendees left
> empowered to leverage these tools seamlessly.

<!-- signature:ignore-end -->

That draft fell into the habits on purpose, to show what the checker catches.

**3. Run the checker.**

```bash
python3 scripts/ai_check.py post.md --register post
```

It reports: one dash, and the words thrilled, transformative, showcased, robust, empowered, <!-- signature:ignore-line -->
leverage, seamlessly and moreover. <!-- signature:ignore-line -->

**4. Fix the sentence, not just the words.** Ask what actually happened and what Jed wants people to
take from it.

> Last week I ran a workshop for 30 people from HR. None of them had written code. By lunch they had
> built a small tool that screens CVs. What surprised me was how fast they got to the real question:
> who checks its work?

**5. Check again.** Clean. Reread the ending: it is a real question, not a flourish. Done.

**6. Report in one line.** "AI check: clean, no dashes, no flagged words, sentences average 11 words."

Two things to notice. The number "30" and the CV tool only go in if Jed gave them. Never invent a
detail to make a sentence concrete. And fixing the vocabulary alone would have left a stiff sentence
about nothing. The rewrite started from what happened.
