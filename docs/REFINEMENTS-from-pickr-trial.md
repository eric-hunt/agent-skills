# Refinements for `review-boundary` and `set-foundation`

> **Status: all six applied** (2026-09-22). Kept as the record of what the
> first real trial found and why the skills changed, since the findings are
> evidence and the commits are only the conclusion. Three changes were applied
> differently from the proposal below:
>
> 1. **Citations are scoped by how long the artifact lives.** Symbol-based
>    citation applies to documents written to outlive the session. The review
>    report cites both symbol and line, because it is read against the commit
>    range in its own heading, and the line saves the reader a search before it
>    can rot.
> 2. **Document health is one check, not two placements.** Size and tier
>    distribution went into a new `2f` alongside dead pointers and orphan
>    documents, rather than being split between Part 4 and the clean block.
>    The general lesson below — that `set-foundation` states thresholds
>    `review-boundary` never checks — is a category, and categories need a
>    home or the next threshold gets scattered too.
> 3. **The `agreed:` integrity rule is narrowed, not absolute.** "An agent
>    cannot set this field" leaves nobody able to set it. The rule as written
>    is that an agent may set it only in the session where the user accepted
>    that wording, never retroactively and never from silence.


_From the first real trial: `review-boundary` run over `pickr` `v0.4.0..v0.5.0`
(2026-09-22), in a sub-agent with **no conversation history**, against tiers
that `set-foundation` had laid down one phase earlier. Full report and a
pre-registered expectation list are in `pickr/temp/`._

## How the trial was set up, and why it is worth repeating

The reviewing agent got the repository and nothing else — no transcript, no
summary of what had been discussed. That made the run a test of two things at
once: the skill, and whether the provenance tags `set-foundation` writes carry
meaning to a reader who was not in the room.

The parent session (which had written every line under review) pre-registered
what it expected the review to find, *before* reading the report. **Do this
again.** It is the only way to tell a review that found things from a review
that confirmed what you already knew, and it caught a case where the parent's
expectations were the thing that was wrong.

## What worked, and should not be touched

- **Depth selection.** It chose depth 2 and named the signal, explicitly
  declining depth 3 because the user had not asked. Correct.
- **Part 4 restraint.** It proposed **no promotions**, on the grounds that the
  tiers were created by the range under review, so no prior phase had leaned on
  them: *"survival is not evidence."* The `Do not promote on survival alone`
  rule did real work.
- **2b discrimination.** The escalation grep returned 19 hits; 15 were the
  project *quoting* its own trap rule about escalation language. It separated
  the quoted smell from the committed one and reported the single real seam.
- **Zero false positives** across ~13 findings. Every high-cost claim was
  independently re-verified against source by the parent session and held.

## 1. The provenance tag needs three fields, not one

**This is the most important change.** `set-foundation` currently writes
`(agreed <date>)` / `(inferred)`. In the trial the reviewer found four rules
tagged with dates of `09-08` through `09-17` on prose that demonstrably did not
exist before `09-18`, and correctly reported that it could not tell a rule whose
current wording the author had read from one an agent re-narrated two days
later. **The tag has one field where it needs three.**

Replace it with:

```markdown
### Well addresses are formatted in exactly one place

`foundational` · created: 2026-09-08 · agreed: 2026-09-16 · altered: 2026-09-18
```

- **`created:`** — when the rule was first written into a document. Not when the
  code started behaving that way; that is archaeology and usually unknowable.
- **`agreed:`** — when the author and the agent settled it together. An agent
  cannot set this field.
- **`altered:`** — when the wording was last changed *without* a fresh
  agreement. An agent sets this every time it touches the rule.

Three properties make this worth the extra ink:

1. **`altered:` newer than `agreed:` means unreviewed drift.** That is the whole
   mechanism, and unlike the `(inferred)` tag it is a *mechanical* comparison —
   greppable, and a natural first line in a review's clean block: *"3 rules
   where altered > agreed."*
2. **`(inferred)` disappears, replaced by an absent `agreed:` field.** Absence
   is a stronger signal than a word, because you cannot forget to write it. A
   rule with `created:` and no `agreed:` has never been blessed by anyone, and
   the gap is visible at a glance down the column.
3. **A re-agreement moves `agreed:` forward and makes `altered:` stale**, which
   reads correctly: `altered < agreed` means the drift was subsequently blessed.

Cost: one line per rule, and the discipline that an agent may never write
`agreed:`. That second part needs saying in the skill explicitly — it is the
only field with an integrity requirement.

## 2. Stop citing `file:line`

Both skills currently say *"cite `file:line`"*. The trial found **three of
eleven citations in the rule index wrong** — in the document that had just
introduced the rule requiring citations. That is a ~27% rot rate over a single
phase, and the failures were all the dangerous kind.

**A line number is the wrong anchor in both directions:**

- An unrelated insertion above invalidates it.
- A deletion does **not** break it — it silently retargets whatever moved into
  the slot. All three failures were this: one pointed mid-comment, one at a
  roxygen `@return` tag, one at a file where the symbol appears zero times.

A citation that 404s is a nuisance. **A citation that resolves to the wrong
thing is worse than none**, because it is checkable-looking and nobody checks
it twice.

Replace the guidance with:

| Citing | Write | Why |
| --- | --- | --- |
| A function or method | `` `.well_address()` (`R/plate-map.R`) `` | LSP `goToDefinition` / one grep resolves it; survives edits above |
| A test that goes red | the `test_that()` description, quoted | stable, and renaming one is a deliberate act |
| A specific expression inside a long function | the enclosing symbol **plus a quoted fragment** | the fragment is greppable; the symbol scopes the search |
| A whole file's behaviour | the path alone | |

The principle to state in the skill: **cite something that a rename or deletion
invalidates, and that an unrelated edit does not.** Line numbers fail both
halves.

Worth adding to `review-boundary`'s 2a: *verify every citation in the intent
documents, and report the rot rate as a number.* It is cheap, mechanical, and it
was the finding with the highest ratio of value to effort in the whole run.

## 3. `review-boundary` has no document-health check

Both of the trial's genuine misses were the same shape, and the parent session
had predicted both:

- **`docs/ARCHITECTURE.md` is 853 lines** — past the ~300 that `set-foundation`
  itself names as the point to split on. Unflagged.
- **Nine of thirteen rules are `foundational`** — the distribution
  `set-foundation` warns makes the tier stop carrying information. Unflagged.

Neither is a fault of the reviewer: **no check in the skill asks either
question.** Part 4 tests each tier against evidence one rule at a time and never
looks at the shape of the whole. Suggested additions:

- A Part 4 line: *if more than roughly two-thirds of rules are `foundational`,
  the tier has stopped discriminating — report the distribution as a finding,
  not the individual rules.*
- A clean-block entry for document size, so that when a document is under the
  threshold that fact is on the record rather than unexamined: `docs: 4 files,
  largest 853 lines (>300 — flagged)`.

The general lesson: **`set-foundation` states thresholds that `review-boundary`
never checks.** Worth one pass over `set-foundation` collecting every numeric or
structural guideline it gives, and confirming the review has somewhere to report
against each. Candidates beyond these two: the anti-patterns list (a document
nobody is required to read; an index document), and the *"give every document a
first line"* rule.

## 4. The depth floor table has a blind spot

The floor table's depth-1 row is *"a rule in the intent document changed in this
range alongside the code it governs."* This range matched that shape — and the
range **was the rule-writing phase itself**, the output of `set-foundation`. The
tiers being checked against were created by the commits being checked.

The reviewer resolved it upward to depth 2 for other reasons and reported the
circularity in Part 4 on its own initiative, which is the right outcome. But it
got there by luck rather than by the table. Suggested row:

| What the range shows | Floor |
| --- | --- |
| The range **created or re-tiered** the rules themselves | **2 — decisions**, and say in the report that Part 4 is structurally thin |

## 5. Smaller notes

- **The `Decide these` cap held under pressure.** The report had ~13 findings
  and put exactly 3 in `Decide these`, correctly sorting the rest as "obvious
  fix, no decision needed." That distinction is the most useful thing the format
  does; consider making it more prominent than the three-item cap.
- **One finding was under-called, and the author caught it.** The report flagged
  `generate_picklist(format =)` as *"defensible, but the rule as written does
  not carve it out"* — reading the line. Running it showed the argument silently
  skips the only check that a transfers table came through `plan_transfers()`,
  because `%||%` short-circuits the call that raises. **2a says to verify claims
  against source; it should say that for behaviour under a conditional, reading
  the source is not verification — execute it.** This is the one place the
  review was measurably too generous.
- **A read-only review still needs somewhere to write.** Nominating a gitignored
  path up front worked well and is worth making explicit in *This review changes
  nothing*, which currently reads as though the report is conversational output.

## 6. 2c should apply its own warning to the examples it proposes

`2c`'s harder half asks whether an existing example *"demonstrates the invariant
itself or a side effect of it."* In the trial the reviewer applied that test
correctly to an existing example and then failed to apply it to its own
suggested replacement.

The finding: the `foundational` rule *"well addresses are formatted in exactly
one place"* cited a test asserting `i = 27` aborts, which the pre-delegation
hand-copy also did — a side effect, not the rule. Correct. The suggestion:
*"one expectation that `.well_address(i, j)` equals `ombre::well_address(i, j)`
across the full legal range."*

Writing it and then reintroducing the old copy showed that **the equality
expectations pass.** A faithful copy returns the same strings for rows A–Z, so
value equality cannot distinguish delegation from duplication. What goes red is
an expectation nobody proposed: that the raised condition carries the delegate's
error as its `parent`, which a local copy has nothing to populate.

Add to 2c: **when the review proposes an example for an invariant that lacks
one, it must say how the proposed example fails** — the same standard it just
applied to the example it rejected. A proposed example is a claim like any
other, and this one was wrong in exactly the way the check exists to catch.
