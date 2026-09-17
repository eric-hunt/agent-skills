---
name: phase-boundary-review
description: Review a completed phase of work before it merges — inventory the decisions made without asking, and find where the design acquired tension. Use at the end of a phase or refactor, before opening a PR, or when asked to review what a stretch of work decided rather than what it changed.
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
  numbered list inside one of the above.
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
