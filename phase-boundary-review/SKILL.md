---
name: phase-boundary-review
description: Review a completed phase of work before it merges — inventory the decisions made without asking, and find where the design acquired tension. Use at the end of a phase or refactor, before opening a PR, or when asked to review what a stretch of work decided rather than what it changed.
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

## Scope the range first

Establish what "this phase" means before reading anything:

```bash
git log --oneline <base>..HEAD
git diff --stat <base>..HEAD
```

If the base is not obvious, ask. Reviewing the wrong range produces a
confident report about nothing.

## Part 1 — Decisions made without asking

Read the commit messages and the diff of every `.md` file in the range. For
each **claim about how things should be** — not each code change — ask: *was
this put to the user and accepted, or did I decide it while implementing?*

Report only the second kind. One line each, with where it landed:

```
(inferred) Backfill rounds DOWN where reagents round to nearest
           -> transfers.R:774, CLAUDE.md defect 11
(inferred) `feasible` is NA rather than FALSE on the backfill row
           -> stocks.R:714
(inferred) as_stocks() default aligned to plan_transfers()
           -> stocks.R:117
```

Rules:

- **Silence is not agreement.** A decision the user did not object to because
  they never saw it is inferred.
- **Include the small ones.** Argument defaults, column names, whether a thing
  warns or errors. Small decisions are the ones that accumulate unreviewed,
  and they are exactly what the user cannot keep up with.
- **Do not include** anything explicitly discussed and accepted, or anything
  forced by an existing invariant (that is the invariant's decision, already
  made).
- If a decision now looks wrong, say so here rather than defending it.

## Part 2 — The tension pass

Five checks. Each has a mechanical starting point, then judgement. Report
findings only — do not fix anything during the review.

### 2a. Does the prose match the code?

For every behavioural claim in `CLAUDE.md` and `docs/ARCHITECTURE.md` touched
in this range, **verify it against the source and cite `file.R:line`.** A claim
checked against another document is not checked.

Two failure shapes, and the second is the dangerous one:

- The prose is simply stale — says "will", describes a function that is gone.
- The prose is *correct* but every worked example teaches a different model.
  This is worse, because the reader learns from the example. It is what
  happened with multi-source allocation: the rule said "partitions on
  `src_barcode`" and the only demo changed `labware`.

### 2b. Escalation language

```bash
grep -rniE '\b(unless|except|until|promoted|falls back|only when|but if)\b' \
  CLAUDE.md docs/*.md R/*.R
```

Every hit is a candidate. For each, decide which it is:

- **A real seam** — the design genuinely has a mode switch. Is it earning its
  keep, or would one rule do?
- **A bad description** — the code has no such branch and the prose invented
  one. Fix the prose; it is actively teaching a wrong model.

The user's own test: if explaining the API requires *"X isn't required until
it is"*, stop. That sentence is either a design smell or a description smell.

### 2c. Invariants with no example that would fail

For each prohibition in `CLAUDE.md`, find the test or notebook cell that goes
red when it is violated. Report the ones with none. **A prohibition with no
such example is a wish.**

Then the harder half: for those that *do* have one, does it demonstrate the
invariant itself or a side effect of it? An example can exercise exactly the
right code and still teach the wrong thing.

### 2d. New surface area

```bash
git diff <base>..HEAD -- NAMESPACE
```

For each newly exported function, argument, or class:

- Did it resolve awkwardness in an existing function that should have been
  fixed in place? **In early development, fix the one function.** Two
  functions reached for in the same situation is programmer's logic imposed
  on the user's reality.
- For a new argument: does the same concept now appear in two signatures that
  have to agree? That is the wart this package removes, not adds.
- For a new class: *would you ever `filter()` it?* Data gets a gate; behaviour
  gets a class.

### 2e. The standing prohibitions

Check the range against the numbered list in `CLAUDE.md`. Most valuable in
practice:

- **A stored derivation** — does anything persist a value it could compute?
  That is the one field nothing can contradict.
- **A property that is `NA` for one implementor** — a field waiting to be
  filled in wrongly. Cut it rather than nulling it.
- **Defaults for the same concept in two places** — they will disagree, and
  the disagreement is unreachable until it is not.
- **A default that is a guess about the bench** — if getting it wrong produces
  a plausible-looking wrong answer rather than a loud failure, it is the
  `"NA1"` mistake. A bad value must not look like a good one.

## Report format

```markdown
## Phase review: <name>   <base>..<head>, N commits

### Decisions made without asking
(inferred) <claim>  -> <file:line>
...

### Tension
**<one-line finding>** — <what is wrong, and the evidence>
  <file:line>. Suggested: <the smallest change that resolves it>
...

### Clean
<checks that found nothing, one line — so the absence is informative>
```

Rank tension findings by what they cost if left: a wrong model taught to
future readers outranks a stale sentence.

## What this review is not

- **Not a code review.** Correctness, tests and performance belong elsewhere.
  This is about what the work *decided*.
- **Not a rubber stamp.** "No tension found" across five checks on a real phase
  usually means the checks were run shallowly. Say which checks were shallow
  rather than reporting clean.
- **Not license to refactor.** Report, then let the user choose. A review that
  fixes things on the way through is a review nobody can audit.

