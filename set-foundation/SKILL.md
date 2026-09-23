---
name: set-foundation
description: Lay down a project's groundwork documents — the architecture notes, invariants, and contracts — and mark each rule as foundational, in question, or a loose contract. Works on a new project before there is code, and on a running one by recovering the architecture the code already implements and putting it to the user. Use when starting a project, when a project has no architecture document, when the existing documents are not trusted, or when asked what this project's actual rules are. Runs as a conversation; writes documents only once the user has agreed to them. Pairs with review-boundary, which checks each phase of work against the tiers this lays down.
metadata:
  author: Eric Hunt
  version: "1.0"
  summary: Lays a project's groundwork documents and tiers each rule foundational, in question, or contract
license: MIT
---

# Set the foundation

Most architecture documents fail the same way: every sentence in them reads
as equally authoritative. A rule fought for over two days and a placeholder
typed to stop thinking about it look identical on the page, so the next
reader — human or agent — defends both with the same energy, and the project
pays complexity rent on decisions nobody actually made.

**The deliverable of this skill is the tier, not the prose.** A one-line rule
marked `in question` is worth more than a well-argued page that does not say
how firmly it is meant.

Run this in a planning mode. It is a conversation that ends in documents, not
a document-generating pass.

## The tiers

Every rule you write gets exactly one:

| Tier | Means | The test | Cost of getting it wrong |
| --- | --- | --- | --- |
| `foundational` | Load-bearing. Changing it changes what the project *is*. | Can you name the failure it prevents, and has that failure happened or would it plausibly happen? | Marked too freely — for importance rather than confidence — everything is foundational and the tier stops carrying information. (A high share on a mature codebase is usually not this; see *B4*.) |
| `in question` | Written to get moving. Plausible, never earned. | Would you be relieved or annoyed if someone showed you a simpler design without it? | The honest default. Under-using this is the failure mode this skill exists to fix. |
| `contract` | A loose agreement kept for consistency — naming, layout, formatting. | Would a violation be *wrong*, or just *inconsistent*? | Cheap either way; these exist so they stop competing for attention with the real rules. |

Two rules about the tiers themselves:

- **`in question` is the default.** A rule reaches `foundational` by argument,
  not by being written down. If you are unsure, it is `in question` — and say
  so to the user rather than quietly promoting it. A *review* reading an
  unmarked rule does the opposite and assumes `foundational`, because it
  cannot tell a scar from a habit. The asymmetry is deliberate: be honest
  when writing, conservative when reading.
- **A tier is a claim about *confidence*, not importance.** A `contract` can
  matter every day. A `foundational` rule can sit untouched for months.

## Step 1 — Which mode

```bash
git log --oneline | wc -l
ls AGENTS.md CLAUDE.md README* 2>/dev/null
ls docs/ doc/ adr/ design/ 2>/dev/null
```

- **Greenfield** — little or no code, no intent documents. Go to Mode A.
- **Running project** — code exists, documents are absent, thin, or not
  trusted. Go to Mode B. This is the more common case and the more valuable
  one.

A project with *good* documents that merely lack tiers is Mode B with the
reading already done: skip to Step 3 and tier what is there.

## Mode A — Greenfield

There is no code to read, so everything comes from the user. The risk here is
the opposite of Mode B's: it is very easy to produce twenty confident rules
about a program nobody has written.

Ask about, in this order:

1. **What the program is for**, in one sentence, and who is harmed when it is
   wrong. Rules that do not trace back to this are decoration.
2. **The shape of the data or domain** — the two or three nouns everything
   else is expressed in terms of.
3. **What must never happen.** These are the only real candidates for
   `foundational` at this stage, because each names a failure.
4. **What is already decided and why** — language, storage, deployment. Most
   of these are `contract`; some are `foundational` and the user knows which.

Then write **the fewest rules that would let someone else start**. Five to
eight. Mark almost all of them `in question`, and say so plainly: *these are
predictions, and the first phase against them is where they get tested.*
That sentence is what makes the first boundary review honest.

**Do not write rules about code that does not exist yet.** A rule with no
code to constrain cannot be violated, cannot be tested, and will be obeyed by
accident until the day it is inconvenient.

## Mode B — Recover the architecture the code implements

The project already has an architecture. It is just not written down, and
what *is* written down may describe a different program. Your job is to read
the first, compare it to the second, and put the difference to the user.

### B1. Find what the code actually enforces

A project's real invariants are the ones it defends. Start mechanically:

```bash
# guards, assertions, validators — the rules with teeth
grep -rnE 'assert|stopifnot|match\.arg|raise |panic!|throw new|abort\(' <source dirs>

# the prose the code carries about itself
grep -rniE '\b(must|never|always|invariant|do not|cannot|required)\b' <source dirs>

# the shapes that repeat — recurring commit scopes name the project's parts
git log --format='%s' | sed 's/:.*//' | sort | uniq -c | sort -rn | head -20
```

Then read the public surface and the tests. **A rule with a test that goes
red is a rule the project means.** A rule appearing only in a comment is a
preference.

### B2. Find the gap in both directions

This is the step that makes Mode B worth running on a project that already
has documents:

- **Enforced but unstated** — the code defends it, nothing says so. These are
  usually `foundational` and are the highest-value thing you will write. They
  are also what a new contributor breaks first.
- **Stated but unenforced** — a document says it, nothing goes red when it is
  violated. *A prohibition with no failing example is a wish.* Either it needs
  an example or it needs demoting to `contract` — put both options to the
  user. The exception is a prohibition on *future* code, which cannot have an
  example at all; see *Armored or vigilant*.
- **Stated and contradicted** — the document says one thing, the code does
  another. Report the code's version; it is the one that ships.

### B3. Do not invent

**Every rule you propose in Mode B carries a citation.** If you cannot cite
it, it is not this project's architecture — it is your taste, and proposing
it here launders an opinion into a foundation.

Where you believe the code *should* have a rule it does not, that is a
separate list, offered after the recovered ones and labelled as a suggestion.

### B4. On a mature codebase, expect a lot of `foundational`

`in question` is the default, and a rule reaches `foundational` by argument.
On a project that has been through many phases, the argument is often already
in the history: the guard that was added with a bug fix, the concept that was
deleted because this rule made it redundant, the three refactors the rule
survived. What survives that is *selected* for being load-bearing. Tier each
rule honestly on its own evidence and **let the share land where it lands** —
two-thirds or more is normal here, and pulling rules back down to hit a ratio
would be the dishonest move.

Two things keep a high share from hiding a problem:

- **Report the armored/vigilant split alongside it.** On a mature project
  that split is the number that locates risk — see *Armored or vigilant*.
- **Say how the tiers were laid**, in the tiered document's first line (see
  *Give every document a first line*). A later review reads a high share very
  differently depending on whether the rules were predictions or recoveries,
  and without the line it has to guess.

Tell the user this during Step 2, before they see the count. A review will
otherwise raise the ratio later, and it is better that they meet the
reasoning here than argue it there.

### Cite symbols, not line numbers

A citation in a document written to outlive the session must survive editing.
**A line number fails in both directions**, and the second failure is the one
that matters:

- An unrelated insertion above it invalidates the citation — a nuisance.
- A deletion does *not* break it. It silently retargets whatever moved into
  that slot, so the citation still resolves, to the wrong thing. **A citation
  that resolves wrongly is worse than none**, because it looks checkable and
  so nobody checks it twice.

| Citing | Write | Why it holds |
| --- | --- | --- |
| A function or method | `` `.well_address()` (`R/plate-map.R`) `` | One grep or an LSP jump resolves it, and edits above it change nothing |
| A test that goes red | the test's description, quoted | Stable, and renaming one is a deliberate act |
| An expression inside a long function | the enclosing symbol **plus a quoted fragment** | The fragment is greppable; the symbol scopes the search |
| A whole file's behaviour | the path alone | Nothing finer is being claimed |

The principle, worth stating in the document you write so the next
contributor follows it: **cite something that a rename or a deletion
invalidates, and that an unrelated edit does not.**

## Step 2 — Put it to the user before writing anything

Do not hand over forty rules to be tiered. That is the seven-hundred-line
document problem again, wearing a different hat.

Bring **at most ten**, grouped, each on one line with a proposed tier and the
evidence:

```
foundational  Well addresses are formatted in exactly one place
              -> enforced in `.well_address()` (R/plate-map.R);
                 test_that("well addresses stop at Z") goes red
                 vigilant — a second formatter elsewhere would pass
in question   Units are converted at the boundary, never inside
              -> only two call sites; the third would be awkward
contract      Exported functions are verb_noun
              -> 14 of 16 conform
```

Ask the user to **correct**, not to author. "Which of these is wrong?" gets
answers; "what are your architectural principles?" gets silence or a lecture.

Flag explicitly:

- Any rule you moved to `foundational` on your own judgement.
- Any `in question` rule the user seems to treat as settled — that mismatch
  is the whole point of the exercise.
- Anything you found enforced that the user did not know was enforced.
- Any `foundational` rule the user believes is enforced when the enforcement
  is only vigilant. Users tend to remember that a test exists, not what it
  would miss.

## Step 3 — Write the documents

Only after the user has been through the list. Prefer the project's existing
files; create a new one only when there is nowhere for something to live.

### Start with three

| Document | Answers | Tiered? |
| --- | --- | --- |
| `README.md` | What is this, and how do I use it? | No — the audience is outside the project |
| `docs/ARCHITECTURE.md` | Why is it built this way, and how firmly? | **Yes. This is the tiered document.** |
| `AGENTS.md` / `CLAUDE.md` | How do I work in this repo? | No — commands, conventions, the working agreement |

Three is enough to start, and the split between them is by **reader and
question**, not by topic. The agent instruction file *points at* the
architecture document; it never restates a rule from it. Two copies of a rule
are two rules, and they will disagree — silently, and usually at the moment
someone is relying on one of them.

### Split further on evidence, not up front

Five thin documents on day one are worse than one honest one: nobody knows
which to open, and the empty ones read as negligence. Split a section out
when it earns it.

| Signal in an existing document | Split out to | Because |
| --- | --- | --- |
| The section is touched by most PRs while the rest sits still | `docs/DEFECTS.md`, `docs/ROADMAP.md` | Churn — see below |
| The section is a procedure followed during one activity, not a rule checked against | `docs/TESTING.md`, `docs/RELEASING.md` | Procedures are followed start to finish; rules are checked one at a time. Mixing them makes both harder to use |
| The section records something the project does not control and did not decide | one document per source — see below | A fact is verified against its source, never tiered. Keeping facts in the tiered document invites tiering things that were never ours to decide |
| The section is about tooling or environment, not the program | `docs/DEV-SETUP.md`, `docs/GIT-LFS.md` | Read once at setup, then never again. It should not compete for attention with rules read every phase |
| Any one document runs past roughly 300 lines | whichever of the above fits | Past that, people stop re-reading and start grepping, and a rule found by grep is read without its reasoning |

**The "does not control" row generalises further than its examples.** Every
project has some understanding it did not decide and cannot change: the shape
of an API it calls, a vendor's published specification for a device or file
format, how a unit or currency converts, what a standard or regulation
requires, a protocol's wire format. These share three properties that make
them the wrong shape for a tiered document — they are low-churn, they are
verifiable against something outside the repository, and a tier applied to
one would be a claim about someone else's decision. **Name the file after the
source, not the topic** (`docs/STRIPE-API.md`, `docs/UNITS.md`,
`docs/VENDOR-DOCS.md`), so that when the source changes it is obvious what
has to be re-checked and what has not.

**Churn is the most important of these and the least obvious.** A document
whose diff means something is a document you do not have to re-read. If the
defect list lives inside `ARCHITECTURE.md`, every defect fix touches
`ARCHITECTURE.md`, `git log docs/ARCHITECTURE.md` stops telling you when the
architecture changed, and the cheapest signal a boundary review has —
*did the intent document move when the behaviour did?* — is destroyed.
Splitting churn out is what keeps that signal alive.

An ADR directory (`docs/adr/NNNN-*.md`) is worth adding only if the project
will actually keep one. A dated decision with its alternatives is excellent;
three ADRs and then silence is worse than none, because it implies the
undocumented decisions were not decisions.

### Give every document a first line

Each one opens with a single line saying when to read it and where the rules
live:

```markdown
# Testing

_Read when writing or fixing a test. What the code **must** do is in
[ARCHITECTURE.md](ARCHITECTURE.md); this is how we check it._
```

That line is what makes a five-document `docs/` navigable, and it is the
thing that stops the architecture document slowly absorbing everything else.

The tiered document's first line also says **how its tiers were laid**, since
that is the one fact a later review cannot recover from the rules themselves:

```markdown
# Architecture

_Read before changing behaviour. Tiers recovered from the code at v0.5.0
(2026-09-23); `in question` rules are the open ones._
```

Write *"predicted before the code"* for Mode A and *"recovered from the code
at <tag or commit>"* for Mode B. Leave it alone afterwards: re-tiers are
dated on each rule, and this line records only where the set began.

### Anti-patterns

- **A document per source module.** It mirrors the code, so it goes stale
  invisibly, and it answers no question anyone actually has.
- **An index document.** If you need a document to find the documents, the
  README and the agent file are not doing their job.
- **A document nobody is required to read.** Either something sends the
  reader there at a known moment, or it is a diary.

### Rule format

Each rule, so that a later review can find it and check it:

```markdown
### Well addresses are formatted in exactly one place

`foundational` · created: 2026-09-08 · agreed: 2026-09-16 · altered: 2026-09-18

Two formatters drift, and the drift shows up as a plate that loads into the
wrong rows — a wrong answer that looks right.

Enforced in `.well_address()` (`R/plate-map.R`). Goes red at
`test_that("well addresses stop at Z")`. **Vigilant:** the test pins the one
formatter we know about; a second formatter in a new file would pass it.
```

Four parts, all four load-bearing:

1. **The rule**, one sentence, imperative, testable.
2. **The tier and its three dates** — see below.
3. **The failure it prevents** — not a restatement of the rule. If the only
   reason you can give is "consistency", the tier is `contract`.
4. **Where it is enforced, what goes red, and which kind of red** — see
   below. A `foundational` rule with no failing example is the first thing to
   fix after this session, unless it is a prohibition on future code.

### Armored or vigilant

A failing example says a rule *can* go red. It does not say whether it goes
red for the violation that actually arrives, which is usually one nobody has
written yet. So the fourth part names the kind, in one bolded word —
`**Armored:**` or `**Vigilant:**`, as in the example — so a review can count
them with a grep:

| Kind | Means | Typical enforcer |
| --- | --- | --- |
| **Armored** | A violation nobody anticipated still goes red | A sweep over the source (grep or AST walk in a test), a type or schema constraint, a structure in which the second path cannot be built |
| **Vigilant** | Only the cases someone thought of go red | Tests of known inputs, a reviewer who remembers |

**The test: write the likeliest violation in a file that does not exist
yet.** A second formatter in a new module, a new call site that skips the
guard, a new class without the check. If something still goes red, the rule is
armored. If only the files someone already knew about are watched, it is
vigilant. A thorough property-based test sits in between; say which way you
called it and why.

This is **not a fourth tier.** A tier is a claim about confidence; armoring is
a fact about enforcement. A rule can be armored and still `in question`, or
`foundational` and defended only by whoever remembers it. Keep the word in the
fourth part, never in the tier line, so the two axes cannot blur into one.

A vigilant `foundational` rule is not a reason to demote. It is the thing a
review needs to know in order to spend its attention, because a vigilant rule
is where a real violation can ship with every test green.

**A prohibition on future code is permanently vigilant.** *"Resist adding a
mode argument for X"*, *"code that answers a different question moves out of
this package"* — there is nothing to run until someone writes the thing
forbidden, and the forbidden thing has no fixed form to sweep for. Record it as
vigilant by construction, not as a rule missing its test, so nobody goes
looking for an example that cannot exist. Two limits keep this from becoming a
place to park any unenforced rule:

- **If you can name the forbidden form, it is not this category.** "No second
  call to `quantize()` outside `R/units.R`" can be swept for. Sweep for it.
- **It still needs evidence.** Where there is no test, cite the history
  instead: the commits that moved code out, the deviation that was proposed
  and declined.

### The three dates

A single `(agreed <date>)` cannot distinguish a rule whose current wording the
author actually read from one an agent re-narrated afterwards. Three fields
can, and the comparison between two of them is mechanical:

| Field | Means | Who may write it |
| --- | --- | --- |
| `created:` | When the rule was first written into a document. Not when the code started behaving that way — that is archaeology, and usually unknowable. | Anyone |
| `agreed:` | When the author and the agent settled this wording together. | **See the integrity rule below** |
| `altered:` | When the wording was last changed *without* a fresh agreement. | An agent sets this every time it touches the rule |

Omit a field that does not apply rather than inventing a value. Three
properties make the extra line worth it:

- **`altered:` newer than `agreed:` is unreviewed drift**, and unlike a tag
  you have to remember to write, it is a *comparison* — greppable, countable,
  and a natural first line in a review's record: *"3 rules where altered >
  agreed."*
- **A missing `agreed:` replaces the old `(inferred)` tag.** Absence is the
  stronger signal, because you cannot forget to write it, and a column of
  rules with no `agreed:` is visible at a glance.
- **A re-agreement moves `agreed:` forward and makes `altered:` stale**, which
  reads correctly: `altered < agreed` means the drift was subsequently
  blessed.

**The integrity rule: an agent may write `agreed:` only in the session where
the user accepted that wording, and never retroactively.** Not from silence,
not from "this has been here a while", not from an older agreement on
different words. If you are the one who changed the wording, the field you
touch is `altered:`. This is the only field with an integrity requirement, and
the whole mechanism rests on it — a date you can talk yourself into is worth
less than no date at all.

### Point the agent file at what happens next

The rules are now written down, but nothing sends anyone to them. Close that
gap here, while you have the user's attention, because it will not be reopened
later: add short **pointer lines** to the agent instruction file naming the
moments at which this project expects something to happen.

The reason this belongs in that file and nowhere else: **the agent file is
always loaded; a skill is loaded on demand.** Policy that has to be discovered
before it applies is not policy. So *when* lives in the agent file, *how* stays
in the skill, and neither repeats the other.

```markdown
## Working agreement

Rules and their tiers: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Cite its
reasoning so it can be judged; never cite it as the judgement.

- **At a phase boundary, before opening a PR** — run `review-boundary`. It
  reports; it changes nothing.
- **When a rule's tier stops matching how the project treats it** — re-tier it
  in `ARCHITECTURE.md`, with the date. The review will tell you when.
- **When recording a defect** — `docs/DEFECTS.md`, never `ARCHITECTURE.md`. A
  defect entry in the rules document destroys the cheapest signal a boundary
  review has.
```

Five rules for writing them:

1. **Name the moment, not the tool.** "At a phase boundary, before opening a
   PR" is something a person recognises they are standing in. "Use
   `review-boundary` for reviews" is a tautology and will never fire.
2. **Point, never restate.** No depths, no steps, no trigger lists — those
   live in the skill and will drift the moment it changes. One line is the
   budget, and the budget is the safeguard.
3. **Only for what the project actually has.** Do not write a pointer to a
   skill or a document that is not installed. A dead pointer teaches the
   reader that the pointers are decorative.
4. **Keep the coupling one-directional.** The pointer names the skill; the
   skill never names the project. Delete the pointer and the tiers still
   stand on their own.
5. **Put them to the user like everything else here.** These are operational
   policy — they bind future sessions, so they are the user's call, not
   yours.

The third bullet in the example is worth writing even where no skill is
involved: it is what makes the churn split self-enforcing, by telling the next
contributor where a defect goes *before* they put it in the wrong file.

## Step 4 — Hand off

Say plainly which rules are now on probation:

> N foundational (A armored, V vigilant), N in question, N contracts. The
> `in question` ones are predictions — the first phase that strains against
> one should cost out the deviation rather than work around it. The vigilant
> `foundational` ones are defended by memory: <name them>.

Naming the vigilant rules is the useful half of that sentence. It tells the
user where a violation can ship with every test green, and it tells them which
rules would repay a sweep if they ever want to spend an afternoon armoring
something.

`review-boundary` reads these tiers directly: it will report friction
against a `foundational` rule but not propose dropping it unasked, will go
after `in question` rules first when you ask for a critical review, and will
not spend a counterfactual on a `contract`. It reads the enforcement word too:
the vigilant `foundational` rules are the ones it searches for new violations
itself, since nothing else will.

## What this is not

- **Not a design session.** You are recording what is decided and how firmly,
  not deciding it. Where the user has not decided, the output is `in question`
  — not your best guess promoted to prose.
- **Not a documentation pass.** Docstrings, READMEs and API reference are a
  different job. This produces rules with tiers.
- **Not permanent.** A tier is a snapshot of confidence. Re-run this when the
  `in question` list has stopped matching what the project actually treats as
  negotiable.
- **Not a licence to refactor.** If recovering the architecture turns up a
  bug, report it and keep going. Fixing it here mixes a finding into a
  foundation.
