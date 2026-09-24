> **Status: applied** (2026-09-23), on `feat/enforcement-axis`. Kept as the
> record of why the tiers gained a second axis, since the finding is evidence
> and the commits are only the conclusion. Where the implementation departs
> from the proposal below:
>
> 1. **The enforcement word is recorded, in bold.** The note argued nothing
>    new had to be written down. To be *countable* it does: `set-foundation`
>    now writes `**Armored:**` or `**Vigilant:**` in the rule's fourth part so
>    `review-boundary` can grep for it. It stays out of the tier line.
> 2. **The sharper test the note lacked is a new-file test:** write the
>    likeliest violation in a file that does not exist yet, and ask whether
>    anything goes red. Property-based tests stay a judgement call, and the
>    skill says to state which way it was called.
> 3. **The tiered document now says how its tiers were laid** — *"predicted
>    before the code"* or *"recovered from the code at <ref>"* — so a review
>    can tell survivorship from importance-marking without guessing. Not in
>    the note; it is what makes the ratio's two readings decidable.
> 4. **Movement was adopted despite being listed as unestablished.** 2f
>    reports it from depth 2 with a one-line `git log -p` grep, and says how
>    many phases the count covers, so a young rule set is not read as frozen.
> 5. **The review acts on the split, not only reports it.** 2c now searches
>    for new instances of each vigilant rule's violation — the range at every
>    depth, the whole source from depth 2 — which is the check that would
>    have found `visualize.R`. Part 4 records armoring as its own line.
> 6. **Prohibitions on future code are bounded.** A rule whose forbidden form
>    can be named is not in the category (sweep for it instead), and one that
>    is still has to cite history as its evidence.

# The `foundational` ratio mis-measures mature codebases

_`ombre`, `v0.5.0..#12`, 2026-09-23. A `set-foundation` pass over a package
with good untiered documents, followed immediately by a `review-boundary` run
in a sub-agent with **no conversation history**, pointed at the result. The
review found a live bug. Companion to `REFINEMENTS-from-pickr-trials-2-4.md`, whose
§2f data point this extends._

## The observation

The pass produced **10 `foundational` / 1 `in question` / 2 `contract`** — 77%.
2f fired, correctly by its own rule, and reported the skew as one finding
rather than arguing thirteen rules. The trials note records the same check
firing at **69% on `pickr`** and calling it "borderline rather than damning."

Both reports were right and neither was actionable. The author's response was
the same both times: *is this a real problem, or is it what a mature API looks
like?* That question has now been asked twice and the skill has no answer in
it.

**Meanwhile the same review found a live bug that the ratio could never have
pointed at.** `ombre`'s grid-identity rule — `foundational`, two cited tests,
both passing — was being violated in `R/visualize.R`, which built a plate's
y-axis with `LETTERS[i]`. On a 1536-well plate that collapsed 192 wells into a
single `NA` category. It was the third such formatter in the package's history
and it had shipped.

The two cited tests verified an inverse property and key agreement. **Neither
could notice a second formatter existing.** The rule with the weakest
enforcement in the set was the one being violated, and nothing in the tier
vocabulary said which rule that was.

## Why the ratio drifts up on a mature project

It measures **survivorship**, not discipline. `ombre` has deleted
`ColumnMapping`/`RowMapping`, a bundled `PlateMapping`, `RepSpec(interleaved=)`,
an Echo instrument layer, JMP ingestion, and a row cap at Z — six concepts
across five refactors. What survives that is *selected* for being load-bearing.
A high ratio there is the process working.

So the ratio is a good smoke detector for one failure — marking things
`foundational` to signal **importance** rather than **confidence** — which
dominates on young projects and fades on old ones. Past some age it mostly
reports that the project is old.

## The axis that would have worked

`foundational` currently conflates two populations that want opposite amounts
of a reviewer's attention:

| | `ombre`'s | A reviewer should |
| --- | --- | --- |
| **Armored** — a mechanical enforcer catches a *novel* violation | 3 of 10: conditions-classed (AST walk over `R/`), counts-by-type (S7 property setter ahead of the class check), grid identity (source sweep, added by this PR) | spend ~zero attention |
| **Vigilant** — tests cover known cases; a new violation slips through | 7 of 10 | spend all of it |

*"3 of 10 foundational rules have an enforcer that catches a novel violation"*
points straight at the population containing `visualize.R`. *"77% of rules are
foundational"* does not, and cannot.

Two properties make this the better number:

1. **It falls as a project matures**, because absorbing a rule into the build
   is what maturing looks like. The `foundational` ratio only climbs. A metric
   that moves one way is not a health metric.
2. **It is already in the document.** The rule format asks for "where it is
   enforced, and what goes red." Nothing new has to be recorded — the question
   just has to be asked sharply enough to be countable.

## Not a fourth tier

Adding `enforced` alongside `foundational`/`in question`/`contract` would break
what a tier means. A tier is a claim about **confidence**; armoring is a fact
about **enforcement**. A rule can be armored and still in question, or
foundational and defenceless. They are two axes and collapsing them would
recreate exactly the conflation this note is about.

It should be a second reported number, not a fourth bucket.

## Suggested text

For `set-foundation`, in the rule format's fourth part:

> 4. **Where it is enforced, and what goes red** — and say which kind:
>    does the check catch a **novel** violation (a source sweep, a type
>    constraint, a structural impossibility), or only a **known** one (a test
>    of the cases someone thought of)? A `foundational` rule whose enforcement
>    is only the second kind is defended by whoever remembers it. That is not a
>    reason to demote it; it is the thing a review needs to know in order to
>    spend its attention.

For `review-boundary`, replacing the bare ratio in 2f:

> Report the tier distribution **and** the enforcement split for
> `foundational` rules: how many have a check that would catch a violation
> nobody anticipated, versus how many rest on tests of known cases. On a
> project past its first few phases the second number is the one that locates
> risk — a high `foundational` ratio there is usually survivorship, since the
> rules that were not load-bearing have already been deleted.
>
> Where the ratio is high and the project is mature, do not argue the ratio.
> Report the vigilant rules by name.

## Second finding: prohibitions cannot have failing examples

`set-foundation` says a `foundational` rule with no failing example is the
first thing to fix after the session. For one shape of rule that is
unreachable, and the skill should say so rather than leave an author looking
for a test that cannot exist.

`ombre` has two: *"resist adding an `on_mismatch = "error"` argument"* and
*"`ombre` answers one question, and code that answers a different one moves
out."* Both are prohibitions on **future** code. You cannot write a test that
goes red when someone adds an argument you have not seen, and the second rule's
only evidence is deletions that already happened.

These are not weak rules — the second has been enforced three times by moving
code out of the package. They are permanently vigilant, by construction, and
naming that category would stop the "write an example" advice from firing where
it cannot be satisfied.

> A **prohibition on future code** cannot have a failing example: there is
> nothing to run until someone writes the thing it forbids. Record it as
> permanently vigilant rather than as a rule missing its test, and let the
> review spend attention there instead of asking for an example that cannot be
> constructed.

## What is not established

- **n = 2.** `ombre` at 77% and `pickr` at 69%, both this author, both R
  packages in one bundle, both tiered by an agent rather than written up over
  years. The survivorship claim is plausible and not demonstrated.
- **"Catches a novel violation" needs a sharper test than I have.** `ombre`'s
  AST sweeps are unambiguous and its S7 property constraints nearly so, but a
  thorough property-based test sits somewhere in between, and I did not have to
  adjudicate a hard case.
- **The movement signal may be the real one.** What actually distinguishes a
  healthy mature rule set is probably whether rules still get demoted or
  absorbed across phases — zero movement over many PRs being the smell, and a
  high ratio with active movement being fine. That is a cheaper and more direct
  measure than either ratio, and it needs a project with tiers old enough to
  have moved. `ombre` has exactly one data point: grid identity went from
  vigilant to armored in the PR that found the bug.
