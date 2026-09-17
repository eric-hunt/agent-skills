---
name: phase-boundary-review
description: Read-only review of a completed phase of work before it merges — inventory the decisions made without asking, find where the design acquired tension, and hand back a short report to discuss. Scales from a routine drift check to putting the architecture document itself on the table. Use at the end of a phase or refactor, before opening a PR, when asked to be critical of a design, or when asked to review what a stretch of work decided rather than what it changed. Produces a report and changes nothing.
metadata:
  author: Eric Hunt
  version: "1.0"
license: MIT
---

# Phase boundary review

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

Every depth runs Part 1 and all five tension checks. What changes is the
**radius** — this range, or the whole project — and whether the architecture
itself is on the table. **Depth is never permission to look less carefully.**
A check run shallowly and reported clean is the one failure this review
cannot survive.

Depth is chosen in two moves: **the range sets a floor, and the user
promotes.** Maturity alone never reaches depth 3.

### The floor — read the range

| What the range shows | Floor |
| --- | --- |
| The intent document was updated in this range alongside the code it describes, several phases have landed cleanly, and the ask is routine — "run the review, draft the PR if nothing comes up" | **1 — drift** |
| The intent document was *not* touched in this range while the behaviour it describes changed | **2 — decisions** |
| The phase strained against a stated rule — a workaround, a special case, a "fix this later" | **2 — decisions** |
| Nothing points anywhere | **2 — decisions** |

The untouched-document case is worth checking mechanically. It is the
cheapest signal in the review and it is almost always right:

```bash
git diff --name-only <base>..HEAD -- <intent docs>
```

A range that changed behaviour without touching the document describing that
behaviour has very likely moved the code out from under the prose. Empty
output here is not a clean bill — it is the reason to run check 2a properly
rather than skimming it.

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
| Part 3 | skip | only where the phase strained a rule | required |

At depth 1 the architecture is settled: report drift against it, do not
relitigate it. At depth 3 the architecture is the subject.

## Part 1 — Decisions made without asking

Read the commit messages and the diff of every prose file in the range. For
each **claim about how things should be** — not each code change — ask: *was
this put to the user and accepted, or did I decide it while implementing?*

Report only the second kind. One line each, with where it landed:

```
(inferred) Backfill rounds DOWN where every other quantity rounds to nearest
           -> transfers.R:774, ARCHITECTURE.md "Rounding"
(inferred) Retry budget is per-request, not per-session
           -> client/retry.go:88
(inferred) A partial write leaves the row present with a null status
           -> store/writer.py:212
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

Five checks. Each has a mechanical starting point, then judgement. Report
findings only — do not fix anything during the review.

### 2a. Does the prose match the code?

For every behavioural claim in the intent documents touched in this range,
**verify it against the source and cite `file:line`.** A claim checked against
another document is not checked.

Two failure shapes, and the second is the dangerous one:

- The prose is simply stale — says "will", describes a function that is gone.
- The prose is *correct* but every worked example teaches a different model.
  This is worse, because the reader learns from the example. The shape to look
  for: the rule says the split happens on field A, and the only demo varies
  field B. Every reader now believes the split is on B.

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
**A prohibition with no such example is a wish.**

Then the harder half: for those that *do* have one, does it demonstrate the
invariant itself or a side effect of it? An example can exercise exactly the
right code path and still teach the wrong thing — it passes for a reason the
reader never sees.

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

## Part 3 — The counterfactual pass

*Depth 3 always; depth 2 only where the phase visibly strained against a rule.
Skip at depth 1.*

An architecture document written before the code existed is a prediction. This
pass makes each prediction the phase strained against re-earn its place. The
goal is not to drop rules — it is to stop paying for one nobody would write
today.

For each strained rule:

1. **The rule**, quoted, and where it is written.
2. **The friction** — what the phase had to do to honour it, cited
   `file:line`. Without this, there is nothing to weigh.
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

A project whose groundwork was laid deliberately marks each rule. Where those
markings exist, they override your own judgement about what is open:

| Tier | What this pass does with it |
| --- | --- |
| `foundational` | Load-bearing — changing it changes what the project is. Report friction against it always; propose dropping it only when the user explicitly asked you to be critical of the foundations. |
| `in question` | Written to get moving, never earned. **These are the first targets at depth 3** — the project has already said it expects to revisit them. |
| `contract` | A loose agreement kept for consistency. Drift against it is a finding; the rule itself is not interesting. Do not cost out a deviation from one. |

An **unmarked** rule defaults to `foundational`. There is no recorded
reasoning behind it, so you cannot tell a scar from a habit — check the
history before treating it as open.

**If the project has no intent document**, invert the pass: state the
architecture the code actually implements — three to five rules, each cited —
and ask the user to confirm or correct it. That is the same conversation
entered from the other end, and at depth 3 it is usually the more valuable
one.

## Report format

```markdown
## Phase review: <name>   <base>..<head>, N commits
_Depth N — <the signal that chose it>_

### Decisions made without asking
(inferred) <claim>  -> <file:line>
...

### Tension
**<one-line finding>** — <what is wrong, and the evidence>
  <file:line>. Suggested: <the smallest change that resolves it>
...

### Counterfactual   <!-- depth 2-3 only -->
**<rule>** — friction at <file:line>. Without it: <what changes>.
  It buys: <the failure prevented, or "nothing I can name">.
  Recommend: keep / narrow / drop.

### Clean
<checks that found nothing, one line — so the absence is informative>

### Decide these
1. <the question, the two options, and your recommendation>
...
```

Rank tension findings by what they cost if left: a wrong model taught to
future readers outranks a stale sentence.

## After the report

Findings are not a to-do list. `Decide these` is the part the user reads
first, so it holds only what actually needs them — not every finding, just
the ones where you should not be the one to pick. Each is a question with its
options and your recommendation, so the user can answer it in a word.

Three is a lot. If the list is longer, the phase needed this review sooner.

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
- **Not a rubber stamp.** "No tension found" across five checks on a real phase
  usually means the checks were run shallowly. Say which checks were shallow
  rather than reporting clean.
- **Not license to refactor.** Report, then let the user choose — see
  *This review changes nothing*.
- **Not a plan.** It surfaces what needs deciding; it does not decide, and it
  does not sequence the work that follows.
