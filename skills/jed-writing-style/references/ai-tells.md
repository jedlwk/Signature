# AI tells

What makes writing read as generated, grouped by how hard it should be fixed. The checker in
`scripts/ai_check.py` finds most of these and labels them with the same tiers.

## Contents
- How to read the tiers
- P0: always fix
- P1: fix unless it is a deliberate choice
- P2: use judgement
- Fixes that stick
- Not banned on purpose

## How to read the tiers

A ban alone doesn't stick. Every rule below says what to write instead.

- **P0** is what Jed removes every single time. Never ship these.
- **P1** is a strong tell. Fix it unless Jed chose it on purpose.
- **P2** is a weak signal alone. It matters when several appear together or when it repeats.

<!-- signature:ignore-start -->

## P0: always fix

| Tell | Example | Write instead |
|---|---|---|
| **Dashes as punctuation.** Em dash, en dash, spaced hyphen, double hyphen. | "It works — mostly." | A full stop for a new thought, a comma to continue, a colon to introduce, brackets for an aside. |
| **Counted preamble** | "Three things to know:" "One thing to get right:" | Say the things. |
| **Throat-clearing** | "Worth reading before you...", "It's worth noting", "Let's dive in", "Here's the thing" | Start with the first fact. |
| **Chatbot residue** | "I hope this helps", "Great question!", "Certainly!", "As of my knowledge cutoff" | Delete. |
| **Open loop on us** (customer work) | "We are checking with the team and will come back to you." | Say what can be done. Handle the rest offline. |
| **Inflated significance** | "a pivotal moment", "marks a shift", "plays a vital role", "a testament to" | Say what actually happened. |
| **Challenge and outlook closer** | "Despite these challenges, the future looks bright." | Delete. End on the fact. |

## P1: fix unless deliberate

| Tell | Example | Write instead |
|---|---|---|
| **LLM vocabulary** | delve, leverage, robust, seamless, crucial, pivotal, comprehensive, landscape, transformative, unlock, empower, elevate, harness, tapestry, foster, underscore, showcase, enhance, garner, bolster, interplay, intricate, moreover, "only ever" | The plain word: use, strong, smooth, important, wide, help, improve. Or cut the sentence. |
| **Copula avoidance** | "serves as", "stands as", "acts as a", "represents a" | "is" |
| **Shallow -ing rider** | ", highlighting its importance", ", underscoring the need", ", showcasing", ", reflecting" | Cut it, or write a real sentence with the reason. |
| **Vague authority** | "experts say", "studies show", "many believe", "industry reports" | Name the source or drop the claim. |
| **Stacked hedge** | "could potentially", "may possibly", "it might be worth considering" | One hedge, only where evidence is weak. |
| **Hollow praise** | "Great point, it really highlights..." | Get to something specific from their post. |
| **Slogan or brochure line** | "From answers to outcomes." "It never stops." | End on the plain fact or the next step. |
| **Semicolon** | "It works; it is fast." | A full stop. |
| **Comma-heavy sentence** | Three or more commas | Split into two sentences. |
| **Exclamation mark** in a customer doc or course paper | "Great result!" | Remove. |
| **Emoji** as bullet, divider or decoration | a tick or sparkle in a heading | Remove. |

## P2: use judgement

| Tell | Example | Write instead |
|---|---|---|
| **Tidy group of three** | "borrows X, leans on Y, and uses Z" with matching clauses | Break it up. An uneven natural list ("planning, time and the right guidance") is fine. |
| **"Not X, but Y" template** | "isn't access, it's trust" | Allowed once if it is the real point. Otherwise state the point. |
| **Mirrored sentences** | "It can't change X. It can't change Y." | Vary the shape. |
| **Closing summary line** | A last sentence that repeats the paragraph | Delete it. |
| **Wordy phrase** | "in order to", "due to the fact that", "a wide range of" | to, because, many. |
| **Same opener three times** | Three sentences in a row starting "The" | Vary, unless it is Jed's deliberate repetition. |
| **Synonym cycling** | tool, platform, solution, system for one thing | Pick one name. |
| **Uniform rhythm** | Every sentence 15 to 25 words | Mix in a short line. |
| **Arguing with no one** | "Some might think..." when nobody did | Only answer real objections. |
| **Stiff instruction voice** | "Copy them word for word." | Say it the way a person would. |
| **Headers that restate the obvious** | "THE GOAL", "What good looks like" | Cut the header. |
| **Curly quotes** in plain text | "like this" | Straight quotes. |

<!-- signature:ignore-end -->

## Fixes that stick

- **Give a replacement with every ban.** "No dashes" fails. "No dashes, use a full stop or a comma"
  works.
- **Fix the sentence, not the word.** Swapping "leverage" for "utilise" keeps the same stiff sentence. <!-- signature:ignore-line -->
  Rewrite it the way you would say it.
- **Cut before you rephrase.** Most tells sit in a sentence that adds nothing.
- **Reread the endings.** Jed often flags only the second half of a sentence or the last line of a
  paragraph. The checker cannot judge a flourish.
- **Don't trade one tell for another.** Removing a dash by adding a semicolon, or removing a triple
  by adding "not X but Y", just moves the problem.
- **Two passes at most.** Check, fix, check again. A third pass usually starts to flatten the voice.

## Not banned on purpose

Public anti-AI lists also ban these. Jed uses them, so they stay.

- **"actually" and "key".** Natural words for Jed.
- **Rhetorical questions.** "Seems daunting? It sure was." is a Jed move.
- **Deliberate repetition.** "I decide... I decide..." chosen once for effect.
- **A short standalone closing line.**
- **One "not X but Y"** when it is the point.
- **Exclamation marks** in posts and messages to teammates.
