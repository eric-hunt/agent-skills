---
name: review-boundary
description: Read-only review of a completed phase of work before it merges — inventory the decisions made without asking, find where the design acquired tension, and hand back a short report to discuss. Scales from a routine drift check to putting the architecture document itself on the table. Use at the end of a phase or refactor, before opening a PR, when asked to be critical of a design, or when asked to review what a stretch of work decided rather than what it changed. Produces a report and changes nothing. Pairs with set-foundation, which lays down the tiered rules this review checks against.
metadata:
  author: Eric Hunt
  version: "1.0"
  summary: Read-only review at a phase boundary: what was decided without asking, and where the design strained
license: MIT
---

# Review at a phase boundary

A code review asks *is this correct*. This asks two different questions:

1. **What did I decide without asking?**
2. **Where did the design acquire tension it does not need?**

Both exist because design documents are written faster than anyone can read
them. A decision recorded in prose acquires authority it has not earned, and
the person paying for the resulting complexity never gets a chance to object.
This review is that chance.

**Output a short report. Twenty reviewable lines beat a seven-hundred-line
document — the long document is how the problem started.**

## This review changes nothing

Read-only from start to finish: no edits, no fixes, no commits, no PR. The
deliverable is a report and the conversation that follows it. If a planning
mode is available, run the review inside it; if not, hold the same discipline
by hand.

Two reasons this matters more here than in an ordinary review:

- **A review that fixes things on the way through is a review nobody can
  audit.** Finding and fix arrive fused, and the user never gets the choice
  this review exists to give them.
- **Half the findings are about prose, and prose is cheap to rewrite.**
  Editing a sentence so it matches the code resolves the symptom and destroys
  the evidence — the mismatch *was* the signal that a decision went
  unreviewed.

Fixes come after the user has read the report and said which ones to make.

**"Changes nothing" is about the project, not about your scratch space.** A
real review needs somewhere to put working notes, grep output, and the report
itself while it is being assembled. Nominate one gitignored path up front and
say where it is:

```bash
git check-ignore -q temp/ && echo "temp/ is ignored"
```

Everything the review writes goes there and nowhere else. Saying so at the
start also makes the deliverable concrete — a report the user can reread and
diff against the next one, rather than a wall of conversation that scrolls
away.

## Step 1 — Scope the range

Establish what "this phase" means before reading anything:

```bash
git log --oneline <base>..HEAD
git diff --stat <base>..HEAD
```

`<base>` is usually the merge-base with the trunk branch, the last release
tag, or the last merge commit. If it is not obvious, ask. Reviewing the wrong
range produces a confident report about nothing.

## Step 2 — Find the project's own documents

This review compares code against whatever the project uses to state intent.
**Do not assume the file names** — find them:

```bash
ls AGENTS.md CLAUDE.md README* CONTRIBUTING* 2>/dev/null
ls docs/ doc/ adr/ docs/adr/ rfcs/ design/ 2>/dev/null
git diff --stat <base>..HEAD -- '*.md' '*.rst' '*.adoc' '*.txt'
```

You are looking for three things, wherever they live:

- **The intent documents** — architecture notes, ADRs, design docs, the agent
  instruction file, the README's "how this works" section.
- **The invariant list** — prohibitions, "never do X", standing rules. Often a
  numbered list inside one of the above. If the project marks its rules by
  tier — `foundational`, `in question`, `contract` — that marking decides what
  is open for challenge; see *Part 3*.
- **The public surface** — what the project promises the outside world:

  | Project shape | Diff this |
  | --- | --- |
  | R package | `NAMESPACE`, `man/` |
  | Python package | `__all__`, package `__init__.py`, public modules |
  | JS/TS package | `package.json` `exports`, `index.ts` re-exports, `.d.ts` |
  | Go module | exported (capitalised) identifiers in changed packages |
  | Rust crate | `pub` items, `lib.rs` |
  | Service | route table, OpenAPI/proto schema, migrations |
  | CLI | subcommands, flags, config keys |

**If the project has no intent document**, the review still works: Part 1 is
unchanged, and the tension pass compares the code against the README, the
docstrings, and the claims the commit messages themselves make. Note the
absence in the report — an undocumented architecture is a finding, not a
blocker.

## Step 3 — Pick a depth

Every depth runs Part 1 and all six tension checks. What changes is the
**radius** — this range, or the whole project — and whether the architecture
itself is on the table. **Depth is never permission to look less carefully.**
A check run shallowly and reported clean is the one failure this review
cannot survive.

Depth is chosen in two moves: **the range sets a floor, and the user
promotes.** Maturity alone never reaches depth 3.

### The floor — read the range

| What the range shows | Floor |
| --- | --- |
| A **rule** in the intent document changed in this range alongside the code it governs, several phases have landed cleanly, and the ask is routine — "run the review, draft the PR if nothing comes up" | **1 — drift** |
| The behaviour changed and no rule governing it moved | **2 — decisions** |
| The phase strained against a stated rule — a workaround, a special case, a "fix this later" | **2 — decisions** |
| The range **created or re-tiered the rules themselves** | **2 — decisions**, and say in the report that Part 4 is structurally thin |
| Nothing points anywhere | **2 — decisions** |

This is the cheapest signal in the review, so check it mechanically:

```bash
git diff --name-only <base>..HEAD -- <intent docs>   # did it move at all?
git diff           <base>..HEAD -- <intent docs>     # did it move for this reason?
```

A range that changed behaviour without touching the document describing that
behaviour has very likely moved the code out from under the prose. Empty
output is not a clean bill — it is the reason to run check 2a properly rather
than skimming it.

**Watch for the circular range.** If the rules were written *by the commits
under review*, the depth-1 row matches for the wrong reason: a rule changed
alongside the code because the rule is new, not because the design was
revisited. Nothing has yet had a chance to disagree with it. Take the floor of
2, say so in the report, and expect Part 4 to find almost nothing — no prior
phase can have leaned on a tier that did not exist.

**A touch is not alignment, and the second command is why the first is not
enough.** A defect noted, a roadmap item ticked, a typo fixed, a link
repaired — each leaves the intent document changed and every rule in it
exactly as it was. Read the hunks and ask which happened:

- **A rule changed** — the design moved and the prose moved with it. This is
  the depth-1 case.
- **Something was appended near a rule** — a defect entry, a note, an
  exception recorded under a rule that still claims to have no exceptions.
  The document grew; the design it describes did not get revisited. Floor of
  **2**, and this is precisely where 2a pays: the rule and the note beneath
  it now disagree.
- **Nothing load-bearing changed** — treat it as untouched.

Where the project keeps its churn in separate documents, this reads itself:
a range touching only `DEFECTS.md` has not touched a rule. Where everything
lives in one file, you have to read the diff to find out — which is the cost
of that layout, paid once per review.
### The promotion — read the user

**Depth 3 is never inferred from the repository.** It needs a person asking
for it:

- "be critical", "challenge this", "push back on this"
- the user questioning a design choice they made themselves
- the user asking what a rule is costing, or whether it should exist at all

A document younger than the code *plus* a critical ask is the case depth 3
was built for: the foundations are probably wrong **and** the user is ready
to hear it. A young document on its own stays at depth 2 — unproven
foundations are a reason to check drift carefully, not a licence to reopen
them unasked.

State the depth and the signal that chose it at the top of the report, so the
user can send you up or down in one word.

| | **1 — drift** | **2 — decisions** | **3 — foundations** |
| --- | --- | --- | --- |
| Part 1 | inferred decisions in the range | + which of them belong in the docs | + which of them contradict a stated rule |
| 2a prose vs code | claims touched in the range | every claim the phase relies on | + whether the claim was ever true |
| 2b escalation | intent docs in the range | project-wide | project-wide, and is each seam real |
| 2c invariants | those the phase touched | those the phase relies on | all, and does each still earn its keep |
| 2d surface | the diff | + does it duplicate existing surface | + should existing surface shrink |
| 2e prohibitions | the range | the range and adjacent code | the range, and the prohibitions themselves |
| 2f document health | size and dead pointers | + tier distribution, enforcement split, movement | all four questions |
| Part 3 | skip | only where the phase strained a rule | required |
| Part 4 | tiers the phase touched | all tiers the phase relied on | all tiers |
| Part 5 | if the range remediates a review | same | same |

At depth 1 the architecture is settled: report drift against it, do not
relitigate it. At depth 3 the architecture is the subject.

## Part 1 — Decisions made without asking

Read the commit messages and the diff of every prose file in the range. For
each **claim about how things should be** — not each code change — ask: *was
this put to the user and accepted, or did I decide it while implementing?*

Report only the second kind. One line each, with where it landed:

```
(inferred) Backfill rounds DOWN where every other quantity rounds to nearest
           -> backfill_rows() (transfers.R:774); ARCHITECTURE.md "Rounding"
(inferred) Retry budget is per-request, not per-session
           -> Client.do() (client/retry.go:88)
(inferred) A partial write leaves the row present with a null status
           -> Writer.flush() (store/writer.py:212)
```

Rules:

- **Silence is not agreement.** A decision the user did not object to because
  they never saw it is inferred.
- **Include the small ones.** Argument defaults, column and field names,
  whether a thing warns or errors. Small decisions are the ones that
  accumulate unreviewed, and they are exactly what the user cannot keep up
  with.
- **Do not include** anything explicitly discussed and accepted, or anything
  forced by an existing invariant (that is the invariant's decision, already
  made).
- If a decision now looks wrong, say so here rather than defending it.

## Part 2 — The tension pass

Six checks. Each has a mechanical starting point, then judgement. Report
findings only — do not fix anything during the review.

### 2a. Does the prose match the code?

For every behavioural claim in the intent documents touched in this range,
**verify it against the source.** A claim checked against another document is
not checked.

Three failure shapes, and the later two are the dangerous ones:

- The prose is simply stale — says "will", describes a function that is gone.
- The prose is *correct* but every worked example teaches a different model.
  This is worse, because the reader learns from the example. The shape to look
  for: the rule says the split happens on field A, and the only demo varies
  field B. Every reader now believes the split is on B.
- The prose is correct about a path the code does not take. See *reading is
  not verification*, below.

#### Verify the citations too, and count them

Every citation in the intent documents is a claim. Resolve each one and
**report the rot rate as a number** — it is the cheapest check in this skill
and it found the most per unit effort in the first real trial.

A line-number citation fails in two ways, and only the first is obvious: an
insertion above it invalidates it, but a *deletion* silently retargets it to
whatever moved into the slot. It still resolves — to the wrong thing. Three
citations in eleven were wrong this way in a single phase.

**Resolving is not aiming, so report two numbers.** A citation *rots* when it
no longer resolves, or resolves to the wrong thing. It is *mis-aimed* when it
resolves to exactly what it names and that thing does not exercise the rule —
most often a cited test that stays green when the rule is broken. Symbol
anchoring drives rot toward zero and does nothing for aim: in one trial every
test citation resolved (0% rot) while 4 of 17 cited a test that could not fail
for its rule. Check aim with 2c's question, *how does this go red*, and for a
`foundational` rule, run the cited test against a copy with the rule broken
where that is practical. Say which citations were aimed by running and which
by reading.

Report a wrong citation as a finding, and where a document cites by line at
all, say so once: the durable fix is to cite a **symbol, a quoted test
description, or a path**, not a line, so that a rename invalidates the
citation and an unrelated edit does not.

**In this report, cite both** — `` `.well_address()` (`R/plate-map.R:44`) ``.
The report is read against the commit range in its own heading, usually within
the hour, so the line number cannot rot before it is used and it saves the
reader a search. The symbol is what makes the citation still meaningful if
they come back to it next week.

#### Quantifiers are claims about scope

Anchoring a citation fixes *where* it points. It does nothing for what the
sentence around it claims, and that is where rot went once citations stopped
rotting: four wrong claims in three commits, each next to a citation that
resolved correctly.

- **"only", "never", "always", "every", "unconditionally"** are claims about
  the whole repository. A read of the cited file cannot support one. Verify
  each with a repository-wide search, as a claim in its own right — "the only
  two calls" was four.
- **A sentence describing what a function does to its inputs** — "has
  already populated every row", "never leaves the function" — is checked
  against the function body, not against the function's name. One such claim
  was contradicted two lines into the function it described.

#### Reading is not verification

For a claim about behaviour under a condition — a default, a fallback, a
guard, anything reached only on one branch — **reading the source is not
enough. Run it.**

The trial's one under-called finding was exactly this shape: an argument
appeared to preserve a check, and reading the line supported that. Executing
it showed a null-coalescing operator short-circuiting the call that raised, so
the only validation of an input was silently skipped. The line read correctly
and the branch never ran.

Where running is impractical, say in the finding that the claim was read
rather than executed. That is a different confidence level and the report
should not flatten the two.

### 2b. Escalation language

```bash
grep -rniE '\b(unless|except|until|promoted|falls back|only when|but if)\b' \
  <intent docs> <source dirs>
```

Every hit is a candidate. For each, decide which it is:

- **A real seam** — the design genuinely has a mode switch. Is it earning its
  keep, or would one rule do?
- **A bad description** — the code has no such branch and the prose invented
  one. Fix the prose; it is actively teaching a wrong model.

The test: if explaining the API requires *"X isn't required until it is"*,
stop. That sentence is either a design smell or a description smell, and the
two need opposite fixes.

### 2c. Invariants with no example that would fail

For each prohibition in the invariant list, find the test, notebook cell, or
CI check that goes red when it is violated. Report the ones with none.
**A prohibition with no such example is a wish** — with one exception. A
prohibition on *future* code (*"resist adding a mode argument"*, *"code that
answers a different question moves out"*) cannot have an example, because
there is nothing to run until someone writes the thing forbidden. Do not ask
for one. It is vigilant by construction, and it belongs in the sweep below.
If you can name the forbidden form concretely, though, it is not this
exception: a named form can be swept for.

Then the harder half: for those that *do* have one, does it demonstrate the
invariant itself or a side effect of it? An example can exercise exactly the
right code path and still teach the wrong thing — it passes for a reason the
reader never sees.

And does it depend on **a value someone else owns**? A test asserting that
input `X` is rejected is pinned to `X` being rejectable. If an upstream
package, a vendor specification or a config default can reclassify `X`, the
test goes red on a *fix* rather than a regression. In one trial an upstream
release lifted a limit and four tests broke, all using the out-of-range index
as a sentinel for "invalid", while a boundary test written with no hardcoded
bound followed the new range unchanged. Prefer the example no external change
can reclassify.

**Apply that same test to any example you propose.** When you suggest an
example for an invariant that lacks one, you must say *how it goes red* —
what specifically breaks it, and why nothing else would produce that failure.
A proposed example is a claim like any other, and it is wrong in exactly the
way this check exists to catch more often than it looks.

Saying so has not been enough: the miss below recurred in a later trial,
after this paragraph existed, and took two more attempts to fix. So make it
mechanical. **Name the likeliest wrong implementation** — a faithful copy, a
hardcoded value, a second path, a sentinel someone else owns — and check the
proposed example fails against it. Where running is practical, run it,
against a throwaway copy under the scratch path, never the working tree.
Report which you did: *"fails against a local copy (run)"* and *"should fail
against a local copy (read)"* are different confidence levels.

The trial's own miss: for *"this is implemented in exactly one place"*, the
review proposed asserting that the local function equals the delegate across
the legal range. But a faithful *copy* returns the same values, so equality
cannot tell delegation from duplication — it passes either way. What actually
goes red is the raised condition carrying the delegate's error as its parent,
which a copy has nothing to populate. If you cannot name the thing that
breaks, you have proposed a wish to replace a wish.

#### Sweep the vigilant rules yourself

A test of known cases cannot notice a *new* case. For every vigilant
`foundational` rule (2f's list, or classify the ones this depth covers),
**do the search the tests cannot**: look for a new instance of the violation.
Search the range at every depth. At depth 2 and above, search the whole
source as well, because a vigilant rule's earlier violations had nothing to
catch them either.

This is the check that paid off on a mature project: a `foundational`
one-formatter rule, two cited tests, both passing — and a third formatter in a
plotting file neither test looked at, collapsing a quarter of a large plate
into one `NA` category. It had shipped. The tier said the rule mattered; only
the enforcement kind said nobody was watching.

When the sweep finds one, the obvious fix is **to armor the rule**, not only
to fix the instance: propose the source sweep or constraint that would have
caught it, held to the standard above.

### 2d. New surface area

Diff the public surface identified in Step 2. For each newly exported
function, argument, field, endpoint, or class:

- Did it resolve awkwardness in an existing one that should have been fixed in
  place? **In early development, fix the one function.** Two entry points
  reached for in the same situation is programmer's logic imposed on the
  user's reality.
- For a new argument or field: does the same concept now appear in two places
  that have to agree? That is the wart the project should be removing, not
  adding.
- For a new type or class: does it carry behaviour, or is it data wearing a
  type? Data gets a validator; behaviour gets a type.

### 2e. The standing prohibitions

Check the range against the project's own invariant list first. Then these
four, which apply everywhere and are the ones that pay off most often:

- **A stored derivation** — does anything persist a value it could compute?
  That is the one field nothing can contradict.
- **A property that is null for one implementor** — a field waiting to be
  filled in wrongly. Cut it rather than nulling it.
- **Defaults for the same concept in two places** — they will disagree, and
  the disagreement is unreachable until it is not.
- **A default that is a guess about the real world** — if getting it wrong
  produces a plausible-looking wrong answer rather than a loud failure, it is
  a trap. A bad value must not look like a good one.

### 2f. Document health

The first five checks read the documents for what they *say*. This one reads
them as objects, because a project's own groundwork rules state thresholds
that nothing otherwise checks — and an unchecked threshold is the same kind of
wish as an invariant with no failing example.

```bash
wc -l <intent docs>
grep -c '^### ' <the rules document>          # rule count
grep -c 'foundational' <the rules document>   # tier distribution
grep -ciE '\*\*(armored|vigilant)' <the rules document>   # enforcement, if recorded
```

Four questions, each with a mechanical start:

- **Size.** Is any document past the size its own project names as the point
  to split? Past roughly 300 lines people stop re-reading and start grepping,
  and a rule found by grep is read without its reasoning. Report the largest
  and the threshold.
- **Tier distribution, and what it is measuring.** Count the tiers, then
  place the project *before* reading the number, because the same ratio means
  opposite things in two populations:

  | The tiers were | A high `foundational` share means | Report |
  | --- | --- | --- |
  | Predicted before the code, or the project is in its first few phases | Importance marked as confidence — **the tier has stopped discriminating** | Past about two-thirds: the distribution, as one finding rather than arguing the rules one at a time. At that ratio the problem is the marking, not any mark |
  | Recovered from a codebase that has been through many phases, or promoted one at a time on evidence | **Survivorship.** The rules that were not load-bearing have already been deleted, and `in question` rules lock in as phases lean on them. The share only climbs, so past some age it mostly reports that the project is old | Do not argue the ratio. Report the enforcement split below, with the vigilant rules by name |

  The tiered document's first line should say which (`set-foundation` writes
  *"predicted before the code"* or *"recovered from the code at <ref>"*).
  Where it does not, place the project from the history — release tags,
  concepts deleted along the way, whether the `foundational` rules cite
  guards older than the document — and say which signals you used.

  **The enforcement split.** For each `foundational` rule, is it *armored* —
  would a violation nobody anticipated still go red — or *vigilant*, defended
  only by tests of the cases someone thought of? Use the word the rule
  records if it records one; otherwise apply the test yourself: **write the
  likeliest violation in a file that does not exist yet, and ask whether
  anything goes red.** A source sweep or a type constraint catches it; a test
  of known inputs does not. A prohibition on future code is vigilant by
  construction — count those separately so nobody reads them as missing
  tests. Report *"A of N foundational rules armored"* and name the vigilant
  ones. Unlike the ratio, the vigilant share **falls** as a project matures,
  because absorbing a rule into the build is what maturing looks like, and it
  points at the population where a real violation ships with every test
  green. 2c spends its attention there.

  **Movement**, where the tiers are old enough to have any. What most
  distinguishes a healthy rule set is whether its tiers still move — promoted,
  demoted, armored:

  ```bash
  git log -p --format='%h %as' -- <the rules document> \
    | grep -E '^([0-9a-f]{7,} |[-+]`(foundational|in question|contract)`)'
  ```

  Read the pairs: a `-`/`+` pair with different tiers is a move, a pair with
  the same tier is only a date changing, and a lone `+` is a new rule.
  Armoring does not show here — check the rules' enforcement lines in the
  same log. A high share with tiers still moving is fine. **Zero movement
  across many phases is the smell, whatever the ratio** — the tiers have
  frozen at the moment of least information. Say how many phases the count covers; three
  weeks of tiers cannot have moved much.
- **Dead pointers.** Does every document the agent file points at exist, and
  does every document say when to read it? A pointer to something absent
  teaches the reader that the pointers are decorative.
- **Orphans.** Is there a document nothing sends a reader to at a known
  moment, or a document whose only job is to list other documents? Both are
  findings.

Where the project's groundwork document states a threshold this list does not
cover, check that too and say which one you used. **The general rule: any
number a project writes down about its own documents should have somewhere in
this review that reports against it.**

## Part 3 — The counterfactual pass

*Depth 3 always; depth 2 only where the phase visibly strained against a rule.
Skip at depth 1.* Strain is a workaround somebody chose. An accidental
violation is a 2c finding, and a carve-out written alongside its rule is
scope; neither triggers this pass (see *Part 4 — Demote*).

An architecture document written before the code existed is a prediction. This
pass makes each prediction the phase strained against re-earn its place. The
goal is not to drop rules — it is to stop paying for one nobody would write
today.

For each strained rule:

1. **The rule**, quoted, and where it is written.
2. **The friction** — what the phase had to do to honour it, cited
   `symbol (file:line)`. Without this, there is nothing to weigh.
3. **The project without it** — concretely. Which code disappears, which
   concepts stop needing names, what the public surface becomes.
4. **What the rule buys** — the specific failure it prevents. If you cannot
   name one that has happened or would plausibly happen, *that is the
   finding.*
5. **Recommendation** — keep, narrow to the case that motivated it, or drop.

Rules for this pass:

- **Argue the deviation, then argue back.** A counterfactual that only lists
  benefits is advocacy wearing a review's clothes.
- **A rule with a scar behind it is not a rule with a reason behind it.**
  Check the history before proposing a drop:

  ```bash
  git log -S'<distinctive phrase from the rule>' -- <intent doc>
  ```

  A rule added in the same commit as a bug fix is expensive to undo, and the
  commit message usually says why.
- **Do not re-propose what the user already rejected.** If the history shows
  this deviation was considered and declined, report that instead — the
  finding is that the friction is still here, not that the decision was wrong.
- **Three at most.** If more than three rules are straining, the finding is
  the document, not the rules. Say that and stop.

### When the rules are tiered

A project whose groundwork was laid deliberately — by `set-foundation` or by
hand — marks each rule. Where those markings exist, they override your own
judgement about what is open:

| Tier | What this pass does with it |
| --- | --- |
| `foundational` | Load-bearing — changing it changes what the project is. Report friction against it always; propose dropping it only when the user explicitly asked you to be critical of the foundations. |
| `in question` | Written to get moving, never earned. **These are the first targets at depth 3** — the project has already said it expects to revisit them. |
| *anything this phase strained against* | Whatever its tier, it is also a Part 4 demotion candidate. A rule you have to work around is not the tier it claims. |
| `contract` | A loose agreement kept for consistency. Drift against it is a finding; the rule itself is not interesting. Do not cost out a deviation from one. |

An **unmarked** rule defaults to `foundational`. There is no recorded
reasoning behind it, so you cannot tell a scar from a habit — check the
history before treating it as open.

**If the project has no intent document**, invert the pass: state the
architecture the code actually implements — three to five rules, each cited —
and ask the user to confirm or correct it. That is the same conversation
entered from the other end, and at depth 3 it is usually the more valuable
one.

## Part 4 — Tier drift

*Every depth, including depth 1.* This is the one architecture-touching pass
that is safe on a routine review, because it does not reopen a decision — it
records what the last N phases already demonstrated about one. Skip it only
when the project does not tier its rules.

A tier is a claim about confidence, and confidence is exactly what a phase of
work produces. A rule that three phases have leaned on without complaint is
no longer `in question`; a `foundational` rule that this phase had to route
around was never load-bearing in the way it claimed. **Say so.** Nobody goes
back to re-tier rules on a quiet afternoon, so if this review does not raise
it, the tiers freeze at the moment of least information.

### Promote

| What you saw | Suggest |
| --- | --- |
| An `in question` rule the phase relied on repeatedly with no friction | → `foundational` |
| A rule that now has an example that goes red, where it had none before | → `foundational` |
| An `in question` rule that other rules have come to depend on — it cannot be dropped now without touching them | → `foundational`, and say which rules pinned it |
| A `contract` the code actually enforces | → `foundational`, or stop enforcing it |

**If 2f found the marking itself skewed — importance recorded as
confidence — stop here.** Proposing five individual promotions into a set
that is already two-thirds `foundational` for that reason makes the marking
less informative, not more. Report the distribution and let the user re-cut
it.

**If 2f placed a high share as survivorship, promote as normal.** An
`in question` rule locking in after phases have leaned on it is the lifecycle
tiers exist to record, not a symptom. The evidence bar below does not change.

### Demote

| What you saw | Suggest |
| --- | --- |
| A `foundational` rule this phase *knowingly* worked around, special-cased, or deferred | → `in question`, and hand it to Part 3 |
| A `foundational` rule violated *unknowingly* — the 2c sweep found an instance nobody chose | **Not a demotion.** The rule held its value; its enforcement failed. → armor it, and report the violation as a tension finding |
| A `foundational` rule with no example that goes red, several phases in | → write the example, or → `contract`. Not for a prohibition on future code, which cannot have one — leave its tier alone |
| A rule whose stated failure has never happened and which you cannot construct a case for | → `in question` |
| A `foundational` rule nothing in the range could have violated | → probably `contract`; it is describing style, not constraining behaviour |

The first two rows are easy to confuse, and the difference decides the
remedy. **A workaround is a choice; a violation is an accident.** Someone who
routes around a rule is telling you what it costs, and that is evidence about
the tier. Someone who breaks a rule without noticing is telling you nothing
about the rule and everything about its enforcement. If the violation
reproduces the very failure the rule was written to prevent, that is the rule
earning its tier, not losing it.

Likewise, **a carve-out written by the same range that wrote the rule is
scope, not strain.** Nothing leaned on the rule before the carve-out existed,
so there is nothing to have strained. This matters most in a circular range,
where every scope note arrives alongside its rule.

### Armor

Enforcement moves too, and it is recorded here because it is evidence about a
rule — but it is **not a tier move**, and the report should not make it look
like one:

| What you saw | Record |
| --- | --- |
| The range added a check that catches a novel violation of a rule that had only known-case tests | `armored` — and the rule's enforcement line should now say so |
| The range removed or narrowed such a check | `unarmored` — usually by accident, so it is also a 2c finding |

Report each as one line, in the user's own terms — the tier was their call,
so the finding is evidence, not a verdict:

```
promote  "Units convert at the boundary"  in question -> foundational
         3 phases relied on it; test-units.R:40 now goes red when violated
demote   "One well-address formatter"     foundational -> in question
         this phase added a second path at wells.R:210 rather than extend it
armored  "Grid identity"                  (stays foundational)
         test-grid.R:12 now sweeps R/ for LETTERS[ outside `.well_row()`
```

Two constraints:

- **A demotion is not a criticism of the rule.** It usually means the rule was
  written before anyone knew what it would cost, which is the normal case and
  the reason tiers exist at all.
- **Do not promote on survival alone.** A rule nothing has tested has not
  earned anything; it has merely not been in the way. Cite the phases that
  leaned on it, or leave the tier where it is.

## Part 5 — A previous round's fixes

*Every depth, whenever the range remediates an earlier review* — commit
messages that cite one, or an earlier report sitting in the scratch path.

**A review reports instances; a fix has to address the class.** So do not
check that the named instances were fixed. That is the one thing the author
certainly did. Check whether **other instances of the same class** survive:

1. For each fix, state the defect's general form in one line — not "line 40
   of the README says three", but "a count of defects restated outside the
   defects document".
2. Search for that form repository-wide.
3. **Include generated output** — `man/`, rendered notebooks, built docs,
   anything nobody edits by hand and therefore nobody greps.

In the trials that motivated this, every round of remediation introduced at
least one error the next round caught. The clearest case: a review listed
three files carrying a retired rule, the author fixed those three, and four
more survived, one of them in the shipped manual. One commit later, the same
shape again with a number updated in one file and stale in four. The worst
surviving instance lived in generated output both times.

Report survivors as tension findings. In the clean block, the scope: how many
fixes, each swept for its class, where.

## Report format

```markdown
## Phase review: <name>   <base>..<head>, N commits
_Depth N — <the signal that chose it>_

### Decisions made without asking
(inferred) <claim>  -> <symbol> (<file:line>)
...

### Tension
**<one-line finding>** — <what is wrong, and the evidence>
  <symbol> (<file:line>). Suggested: <the smallest change that resolves it>
...

### Counterfactual   <!-- depth 2-3 only -->
**<rule>** — friction at <symbol> (<file:line>). Without it: <what changes>.
  It buys: <the failure prevented, or "nothing I can name">.
  Recommend: keep / narrow / drop.

### Tier drift
promote  "<rule>"  <from> -> <to>
         <the evidence from this phase>
demote   "<rule>"  <from> -> <to>
         <the evidence from this phase>
armored  "<rule>"  (tier unchanged)
         <the check that now catches a novel violation>

Clean    <check>: <what was examined, counted> ...
Skipped  <check> — <why, usually the depth>

### Decide these
1. <the question, the two options, and your recommendation>
...
```

Rank tension findings by what they cost if left: a wrong model taught to
future readers outranks a stale sentence.

### The clean block

This block is **for the record, not for reading.** The user reads `Decide
these`; this is the part that makes "nothing to decide" falsifiable. Keep it
last, keep it short, and do not apologise for it — it should cost the reader
four seconds to skip and cost you an explicit lie to fake.

```
Clean    2a: 4 claims in ARCHITECTURE.md §Rounding, §Units, verified in source
             11 citations: 3 rot (27%); of 8 resolving, 1 mis-aimed (run)
         2c: 3 invariants, each with a failing example
         2d: NAMESPACE +2, both extend an existing verb
         2f: docs 4 files, largest 312 lines (>300 — flagged);
             tiers 10/13 foundational, recovered at v0.5.0 — survivorship;
             3 armored, 7 vigilant (5 swept in 2c, 2 future-code prohibitions)
         4:  no tier drift — nothing leaned on an `in question` rule
         5:  3 fixes from the last review, each class swept incl. man/
Skipped  2b project-wide, Part 3 — depth 1
```

Two properties earn its keep, and both are about what the line is *made of*:

- **Name the scope, never the verdict.** "4 claims in §Rounding, cited to
  source" is something you can be caught not having done. "No drift found" is
  not. Counts, not lists — the denominator is the load-bearing part, and it
  is also what keeps the block from becoming a second report.
- **`Skipped` is mandatory whenever anything was skipped.** The depth matrix
  puts checks deliberately out of scope, and a check that was out of scope
  must never read as a check that passed. A check that was *run shallowly*
  belongs here too, with the word shallow and the reason — that is the
  difference between an honest depth-1 review and a rubber stamp, and it is
  the only place that difference can show.

If this block runs longer than the findings above it, you have written a
receipt rather than a review. Compress it. If there is genuinely nothing
anywhere in the report but this block, say that in the first line — *"Nothing
to decide; the record is below"* — so the user knows the whole report is four
seconds long before they start reading it.

## After the report

Findings are not a to-do list. **Sort every finding into one of two piles,
and make the sort the most visible thing the report does:**

- **Obvious fix, no decision needed.** You know what the right change is and
  so will the user the moment they read it — a stale sentence, a wrong
  citation, a missing test. These belong in the body and nowhere else. Do not
  ask a question you already know the answer to; it costs the user the same
  attention as a real one and teaches them the list is padded.
- **Needs the user.** Two defensible options, or a cost only they can weigh.
  These go in `Decide these`, each as a question with its options and your
  recommendation, so it can be answered in a word.

This sort is worth more than any single finding in the report. A review that
produced thirteen findings and asked for three decisions has done the user's
reading for them; one that hands over thirteen questions has just moved the
work.

Three decisions is a lot. If the list is longer, either the phase needed this
review sooner, or you have not sorted hard enough — check the second before
reporting the first.

### If the user asked for a PR when nothing comes up

Honour that charge — but "nothing comes up" means nothing reached the
*decide* bar, not that the review found zero things. A stale sentence you can
cite, with an obvious fix, is not a reason to stop.

- **Nothing to decide** — say so in one line, then draft the PR. Put the
  inferred-decisions list in the PR description; that is where a reviewer
  will actually read it.
- **Something to decide** — stop at the report. Say plainly that the PR is
  held, and on what.

A PR opened over an unanswered question buries the question.

## What this review is not

- **Not a code review.** Correctness, tests and performance belong elsewhere.
  This is about what the work *decided*.
- **Not a rubber stamp.** "No tension found" across six checks on a real phase
  usually means the checks were run shallowly. Say which checks were shallow
  rather than reporting clean.
- **Not a guess.** When the repository cannot answer something — whether a
  decision was put to the user, why a guard exists — say so in those words:
  *"I cannot tell from the repository whether this was put to you."* Across
  four trials this was the habit that made the reports trustworthy, and it is
  easy to train out by accident by rewarding confident answers. Keep it.
- **Not license to refactor.** Report, then let the user choose — see
  *This review changes nothing*.
- **Not a plan.** It surfaces what needs deciding; it does not decide, and it
  does not sequence the work that follows.
