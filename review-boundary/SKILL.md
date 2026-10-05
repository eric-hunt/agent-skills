---
name: review-boundary
description: Read-only review of a completed phase of work before it merges — inventory the decisions made without asking, find where the design acquired tension, and hand back a short report to discuss. Scales from a routine drift check to putting the architecture document itself on the table. Use at the end of a phase or refactor, before opening a PR, when asked to be critical of a design, or when asked to review what a stretch of work decided rather than what it changed. Produces a report, committed on the branch and removed before the merge, and changes nothing it reviews. Pairs with set-foundation, which lays down the tiered rules this review checks against, and plan-next, which acts on the roadmap findings at the start of the next phase.
metadata:
  author: Eric Hunt
  version: "1.6"
  summary: Read-only review at a phase boundary - what was decided without asking, and where the design strained
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

**Output a report whose decisions can be read in twenty lines** — the bold
one-line findings plus `Decide these`. Evidence can sit indented beneath them;
the skeleton must be readable on its own.

## The bar for a finding

This review exists to protect the code and the user's decisions, **not to
perfect the documents.** A review that spends its findings on wording teaches
the project to spend its phases on wording. Before reporting anything, ask:
*if this is left alone, what goes wrong?*

- **A finding about prose must name the wrong code a reader would write
  because of it.** "This sentence says `sum` fills zeros; a reader would skip
  the `NA` check" is a finding. "This sentence could be more precise" is not.
- **Not findings:** accurate prose that could be phrased better; a rule with no
  citation; a `contract` with no test; history the document does not record
  (git records it); a scope note that is true but incomplete.
- **Document bloat is a finding, and the fix is deletion.** An incident, a
  rationale for a past revision, or a count the document keeps about itself is
  weight a reader carries on every visit. Propose deleting it. Never propose a
  test that keeps a document's number in sync with another document — delete
  the number.

## This review changes nothing it reviewed

No edits to the code or documents under review, no fixes, no PR. A review that
fixes things on the way through fuses finding and fix, and the user never gets
the choice this review exists to give them. Fixes come after the user has read
the report.

Working notes and grep output go in one gitignored scratch path; nominate it up
front:

```bash
git check-ignore -q temp/ && echo "temp/ is ignored"
```

**The finished report is the one file the review leaves.** Write it to
`docs/review-<YYYY-MM-DD>-<phase>.md` — or wherever the project's agent file
says — and, once the review is done, commit it on the branch. Remove it in its
own commit before the PR merges. The findings then stay in history beside the
work that answered them, readable by anyone, rather than on one machine's
scratch path. Two details make or break this:

- **It needs a real merge.** A squash collapses the add and the delete into a
  no-op, and the report is unrecoverable once the branch is gone. On a project
  that squashes, keep the report in scratch and say so.
- **Plain `git log` will not find it**, because the file never exists on the
  trunk's first-parent line:

  ```bash
  git log --full-history --diff-filter=A --format='%as %h %s' -- 'docs/review-*.md'
  git show <hash>:<path>
  ```

A deferred `Decide these` item needs somewhere to live after the report is
deleted — an issue labelled `question`, or the roadmap where the project has no
tracker. If there is neither, say so, so the review does not silently become
the only record of an open question.

## Step 1 — Scope the range

```bash
git log --oneline <base>..HEAD
git diff --stat <base>..HEAD
```

`<base>` is usually the merge-base with the trunk, the last release tag, or
the last merge commit. If it is not obvious, ask.

## Step 2 — Find the project's own documents

**Do not assume the file names:**

```bash
ls AGENTS.md CLAUDE.md README* CONTRIBUTING* 2>/dev/null
ls docs/ doc/ adr/ docs/adr/ rfcs/ design/ 2>/dev/null
```

You are looking for **the intent documents** (architecture notes, ADRs, the
agent instruction file), **the rules** (prohibitions, standing invariants —
tiered `foundational` / `in question` / `contract` if the project uses
`set-foundation`), **where defects and future work live** — the issue
tracker (`gh issue list --state all`), or `docs/DEFECTS.md` and
`docs/ROADMAP.md` where there is none — and **the public surface**:

| Project shape | Diff this |
| --- | --- |
| R package | `NAMESPACE`, `man/` |
| Python package | `__all__`, package `__init__.py`, public modules |
| JS/TS package | `package.json` `exports`, `index.ts` re-exports, `.d.ts` |
| Go module | exported identifiers in changed packages |
| Rust crate | `pub` items, `lib.rs` |
| Service | route table, OpenAPI/proto schema, migrations |
| CLI | subcommands, flags, config keys |

With no intent document, compare the code against the README, docstrings and
commit messages, and note the absence as a finding.

## Step 3 — Pick a depth

Every depth runs Part 1 and all of Part 2. Depth changes the **radius** — this
range, or the whole project — and whether the architecture itself is on the
table. **The range sets a floor; only the user promotes to 3.**

| The range shows | Floor |
| --- | --- |
| A rule changed alongside the code it governs, and the ask is routine | **1 — drift** |
| Behaviour changed and no rule governing it moved | **2 — decisions** |
| The phase strained against a stated rule — a workaround, a special case | **2 — decisions** |
| The range wrote or re-tiered the rules themselves | **2**, and Part 4 will be thin |
| Nothing points anywhere | **2 — decisions** |

```bash
git diff --name-only <base>..HEAD -- <intent docs>   # did it move?
git diff           <base>..HEAD -- <intent docs>     # did a *rule* move?
```

A touch is not alignment: a defect noted or a link fixed leaves every rule as
it was. Read the hunks.

**Depth 3 needs a person asking** — "be critical", questioning their own
design choice, asking what a rule costs. State the depth and its signal at the
top of the report.

| | **1 — drift** | **2 — decisions** | **3 — foundations** |
| --- | --- | --- | --- |
| Part 1 | the range | + which belong in the docs | + which contradict a rule |
| Part 2 | claims and rules the range touched | + those the phase relies on, project-wide sweeps | + whether each rule still earns its keep |
| Part 3 | skip | only where the phase strained a rule | required |
| Part 4 | tiers the phase touched | all tiers the phase relied on | all tiers |
| Part 5 | if the range remediates a review | same | same |

## Part 1 — Decisions made without asking

For each **claim about how things should be** in the commit messages and the
prose diff — not each code change — ask: *was this put to the user and
accepted, or decided while implementing?* Report only the second kind, one
line each:

```
(inferred) Backfill rounds DOWN where every other quantity rounds to nearest
           -> backfill_rows() (transfers.R:774)
(inferred) Retry budget is per-request, not per-session
           -> Client.do() (client/retry.go:88)
```

- **Silence is not agreement.**
- **Include the small ones** — defaults, names, warn versus error. They
  accumulate unreviewed.
- **Exclude** anything discussed and accepted, or forced by an existing rule.
  A commit message or an `agreed:` date recording the author's acceptance
  counts; cite it. Where the repository cannot say, report it as inferred.
- If a decision now looks wrong, say so rather than defending it.

## Part 2 — The tension pass

### 2a. Does the prose match the code?

For every behavioural claim the range touched (or, at depth 2+, relies on),
**verify it against the source**, never against another document. Three
shapes, the later two worse:

- **Stale** — says "will", names a function that is gone.
- **Correct rule, wrong examples** — the rule says the split is on field A;
  the only demo varies B. Readers learn from the example.
- **Correct about a path the code does not take.**

Two habits that catch what reading misses:

- **Quantifiers are repository-wide claims.** "only", "never", "every" —
  verify with a search, not a read of the cited file.
- **For behaviour under a condition — a default, a fallback, a guard — run
  it.** A line can read correctly while an operator short-circuits the branch
  that raises. Where running is impractical, label the finding *(read)*.

A citation that points at the wrong thing is an obvious fix, one line in the
report. Do not count or grade citations.

### 2b. Escalation language

```bash
grep -rniE '\b(unless|except|until|promoted|falls back|only when|but if)\b' \
  <intent docs> <source dirs>
```

Each hit is either **a real seam** (is it earning its keep, or would one rule
do?) or **a bad description** (the code has no such branch; the prose invented
one). If explaining the API needs *"X isn't required until it is"*, that is a
design smell or a description smell, and they need opposite fixes.

### 2c. `foundational` rules that nothing would catch

**Only `foundational` rules.** An `in question` rule's fate is open and a
`contract`'s violation is merely inconsistent; neither needs a failing
example, and asking for one is how a project ends up defending style with
tests.

For each `foundational` rule the depth covers:

- **Is there anything that goes red when it is violated?** If not, report it —
  unless it is a prohibition on code nobody has written yet ("resist adding a
  mode argument"), which cannot have an example. That exception ends only
  where a sweep would catch the forbidden form's **likeliest variant**, not just
  its spelling: "no `on_mismatch` argument" is a name a rename walks past, so
  it stays a prohibition; "no `LETTERS[` outside `.row_label()`" is a
  construct, so sweep for it.
- **Sweep the vigilant ones yourself.** A test of known cases cannot notice a
  new case. For each rule marked (or that you judge) `vigilant`, search the
  source for a new instance of the violation. This is the check most likely to
  find a real, shipped bug in a mature project — a third formatter in a file
  neither test looked at, with every test green.

When you propose an example or sweep, **name the likeliest wrong
implementation** — a faithful copy, a hardcoded value, a second path — and
check the proposal fails against it (run it against a throwaway copy under the
scratch path where practical). Equality with a delegate cannot tell delegation
from a faithful copy; if you cannot name what breaks, you have proposed a wish.
Prefer examples no upstream change can reclassify: a test using an
out-of-range sentinel breaks when upstream lifts the range.

### 2d. New surface area

For each newly exported function, argument, field, endpoint or class:

- Did it route around awkwardness in an existing one that should have been
  fixed in place? **In early development, fix the one function.**
- Does the same concept now live in two places that have to agree?
- Does a new type carry behaviour, or is it data wearing a type?

### 2e. The standing prohibitions

The project's own rules first, then these four, which pay off everywhere:

- **A stored derivation** — a persisted value that could be computed.
- **A property that is null for one implementor** — cut it.
- **Defaults for one concept in two places** — they will disagree.
- **A default that guesses about the real world** — if wrong, does it produce
  a plausible wrong answer rather than a loud failure?

### 2f. Document weight

```bash
wc -l <intent docs>
```

- **Size.** Past roughly 300 lines people grep rather than read, and a rule
  found by grep is read without its reasoning. Report the largest.
- **Accretion.** Incidents, revision history, restated counts, rationale for
  wording rather than for the rule — per *The bar for a finding*, propose
  deleting them.
- **A rule in the wrong document.** A past-tense sentence that would still
  change someone's behaviour tomorrow — "we moved X out; do not move it back",
  in a changelog or a roadmap's shipped list — is a rule filed as history.
- **A rule stated twice.** The likeliest copies are in the agent file, and in
  the tier definitions. Two copies of a rule will disagree; report the second.
- **Dead pointers and orphans.** A pointer to something absent, or a document
  nothing sends a reader to.
- **The tracking convention.** Follow whichever the project uses. Report it
  when there is none — defects noted in the rules document, or nowhere — or
  when one item lives in both (a `DEFECTS.md` entry that is also an issue),
  and name the fix: re-run `set-foundation`, which carries the migration. A
  project on the fallback whose repository has a reachable tracker is worth
  one line, not a finding.
- **`ROADMAP.md` against the tracker, both directions.** A hand-kept list of
  issues is a copy of tracker state: report an issue it lists that is now
  closed, and an open `question` issue — or an `enhancement` given a
  milestone — that it does not list. A rider listed under the item this
  phase delivered, and still open, was meant to land in this PR: say so, so
  it is fixed here or knowingly left. One line each, naming the fix: run
  `plan-next`, which carries the full check and the reordering.

Do not argue the `foundational` share. On a mature project it is high because
what was not load-bearing has been deleted.

## Part 3 — The counterfactual pass

*Depth 3 always; depth 2 only where the phase knowingly worked around a rule.*

For each strained rule, at most three:

1. **The rule**, quoted.
2. **The friction** — what the phase had to do to honour it, cited.
3. **The project without it** — which code and concepts disappear.
4. **What the rule buys** — the failure it prevents. If you cannot name one,
   *that is the finding.*
5. **Recommend** keep, narrow, or drop — having argued back against yourself.

Check the history before proposing a drop (`git log -S'<phrase>'`): a rule
added with a bug fix is a scar. Do not re-propose what the user already
declined. More than three strained rules means the document is the finding.

By tier: `foundational` — report friction, propose dropping only on a critical
ask. `in question` — the first targets at depth 3. `contract` — never cost one
out. An unmarked rule defaults to `foundational`.

## Part 4 — Tier drift

*Every depth, if the project tiers its rules.* A phase is evidence about
confidence; if this review does not say so, the tiers freeze.

| Saw | Suggest |
| --- | --- |
| An `in question` rule the phase leaned on repeatedly without friction | → `foundational`, citing the phases |
| A `foundational` rule the phase *knowingly* worked around | → `in question`, and hand it to Part 3 |
| A `foundational` rule violated *unknowingly* (2c found it) | **Not a demotion** — the rule held; its enforcement failed. Armor it |
| A `foundational` rule describing style, which nothing could violate in a way that breaks behaviour | → `contract` |
| A `foundational` rule the phase found violated and **recorded** as a defect, without working around it | No move. It waits on the decision that resolves it; put that in `Decide these` |
| A `contract` the code enforces by test | Fine — a test is allowed to keep code organised. No move |

A check that now catches a novel violation is `armored`, not a tier move;
report it on its own line. Do not promote on survival alone.

```
promote  "Units convert at the boundary"  in question -> foundational
         3 phases relied on it
armored  "Grid identity"  (stays foundational)
         test-grid.R now sweeps R/ for LETTERS[ outside .row_label()
```

## Part 5 — A previous round's fixes

*Whenever the range remediates an earlier review.* A fix addresses the named
instance; check whether **other instances of the same class** survive. State
each defect's general form in one line, search repository-wide, and include
generated output (`man/`, built docs) — the survivor is usually there.

## Report format

```markdown
## Phase review: <name>   <base>..<head>, N commits
_Depth N — <the signal that chose it>_

### Decisions made without asking
(inferred) <claim>  -> <symbol> (<file:line>)

### Tension
**<the whole finding in one sentence>**
  <evidence> <symbol> (<file:line>) (run | read)
  Suggested: <the smallest change>

### Counterfactual   <!-- depth 2-3 only -->
**<rule>** — friction at <symbol>. Without it: <what changes>.
  Buys: <the failure prevented>. Recommend: keep / narrow / drop.

### Tier drift
promote | demote | armored  "<rule>"  <from> -> <to>
         <evidence>

Clean    <check>: <what was examined, counted>
Skipped  <check> — <why>

### File these
bug          "<title>"  — <one line of evidence>
enhancement  "<title>"
question     "<title>"  — <a deferred Decide-these item>

### Decide these
1. <question, options, recommendation>
```

Cite `symbol (file:line)` in the report — it is read within the hour, so the
line cannot rot first. Rank findings by what they cost if left: a wrong model
taught to future readers outranks a stale sentence.

**The clean block** is for the record: name the scope examined, never the
verdict ("4 claims in §Rounding, verified in source", not "no drift").
**One line per check, holding counts, not lists** — the denominator is what
makes it falsifiable, and a list turns it into a second report. Every skipped
or shallow check gets its own `Skipped` line. If it is all there is, say
*"Nothing to decide"* in the first line.

## After the report

Sort every finding into one of two piles:

- **Obvious fix** — you know the change and so will the user. It goes in the
  body only. Do not ask a question you know the answer to.
- **Needs the user** — two defensible options, or a cost only they can weigh.
  These go in `Decide these`, answerable in a word.

Anything real that this phase will not fix — a defect found on the way, work
the review shows is next — goes in **`File these`**, as a proposed issue with a
title and label, or a proposed `DEFECTS.md`/`ROADMAP.md` entry on the fallback.
The review files nothing itself: opening an issue is visible outside the
repository, so it waits for the user's word like any fix.

Three decisions is a lot. If there are more, sort harder.

If the user asked for a PR "if nothing comes up": nothing to decide → say so
and draft the PR, with the inferred decisions in its description. Something to
decide → hold the PR and say on what.

## What this review is not

- **Not a code review** — correctness, tests and performance belong elsewhere.
- **Not a copy-edit** — see *The bar for a finding*.
- **Not a rubber stamp** — say which checks were shallow rather than reporting
  clean.
- **Not a guess** — when the repository cannot answer whether something was
  put to the user, say so in those words.
- **Not a plan** — it surfaces what needs deciding; it does not sequence the
  work.
