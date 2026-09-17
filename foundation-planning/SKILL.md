---
name: foundation-planning
description: Lay down a project's groundwork documents — the architecture notes, invariants, and contracts — and mark each rule as foundational, in question, or a loose contract. Works on a new project before there is code, and on a running one by recovering the architecture the code already implements and putting it to the user. Use when starting a project, when a project has no architecture document, when the existing documents are not trusted, or when asked what this project's actual rules are. Runs as a conversation; writes documents only once the user has agreed to them.
metadata:
  author: Eric Hunt
  version: "1.0"
license: MIT
---

# Foundation planning

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
| `foundational` | Load-bearing. Changing it changes what the project *is*. | Can you name the failure it prevents, and has that failure happened or would it plausibly happen? | Marked too freely, everything is foundational and the tier stops carrying information. |
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
That sentence is what makes the first phase-boundary review honest.

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
  user.
- **Stated and contradicted** — the document says one thing, the code does
  another. Report the code's version; it is the one that ships.

### B3. Do not invent

**Every rule you propose in Mode B cites `file:line`.** If you cannot cite
it, it is not this project's architecture — it is your taste, and proposing
it here launders an opinion into a foundation.

Where you believe the code *should* have a rule it does not, that is a
separate list, offered after the recovered ones and labelled as a suggestion.

## Step 2 — Put it to the user before writing anything

Do not hand over forty rules to be tiered. That is the seven-hundred-line
document problem again, wearing a different hat.

Bring **at most ten**, grouped, each on one line with a proposed tier and the
evidence:

```
foundational  Well addresses are formatted in exactly one place
              -> wells.R:44, enforced; test-wells.R:112 goes red
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

## Step 3 — Write the documents

Only after the user has been through the list. Prefer the project's existing
files; create new ones only when there is nowhere for something to live.

| Content | Where |
| --- | --- |
| The rules, their tiers, and their reasoning | `docs/ARCHITECTURE.md` |
| How to work in this repo — conventions, commands, the working agreement | the agent instruction file (`AGENTS.md` / `CLAUDE.md`) |
| A decision with a date and alternatives considered | `docs/adr/NNNN-*.md`, if the project uses ADRs |
| Known defects and their measurements | `docs/DEFECTS.md` |

The agent instruction file should **point at** the architecture document, not
restate it. Two copies of a rule are two rules, and they will disagree.

### Rule format

Each rule, so that a later review can find it and check it:

```markdown
### Well addresses are formatted in exactly one place

`foundational` · (agreed 2026-09-17)

Two formatters drift, and the drift shows up as a plate that loads into the
wrong rows — a wrong answer that looks right.

Enforced at `wells.R:44`. Goes red at `tests/test-wells.R:112`.
```

Four parts, all four load-bearing:

1. **The rule**, one sentence, imperative, testable.
2. **The tier**, plus provenance — `(agreed <date>)` when the user accepted
   it, `(inferred)` when you decided it while implementing. An `(inferred)`
   tag next to a `foundational` rule should be uncomfortable; that discomfort
   is the mechanism.
3. **The failure it prevents** — not a restatement of the rule. If the only
   reason you can give is "consistency", the tier is `contract`.
4. **Where it is enforced, and what goes red.** A `foundational` rule with no
   failing example is the first thing to fix after this session.

## Step 4 — Hand off

Say plainly which rules are now on probation:

> N foundational, N in question, N contracts. The `in question` ones are
> predictions — the first phase that strains against one should cost out the
> deviation rather than work around it.

`phase-boundary-review` reads these tiers directly: it will report friction
against a `foundational` rule but not propose dropping it unasked, will go
after `in question` rules first when you ask for a critical review, and will
not spend a counterfactual on a `contract`.

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
