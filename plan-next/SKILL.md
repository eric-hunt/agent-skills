---
name: plan-next
description: Decide what comes next at the start of a phase — bring docs/ROADMAP.md up to date with the issue tracker since the roadmap was last touched, then put the order to the user. Use on the trunk after a merge, before starting new work, when asked what to work on next, or when review-boundary reports a stale roadmap. Proposes first; writes ROADMAP.md only once the user has agreed the order, and changes nothing in the tracker. Pairs with set-foundation, which lays down the tracking convention, and review-boundary, which checks the end of a phase.
metadata:
  author: Eric Hunt
  version: "1.6"
  summary: Start-of-phase planning — reconcile ROADMAP.md with the tracker, then agree what comes next
license: MIT
---

# Plan what comes next

An issue tracker is flat, so the order work is picked up in lives in a short
`docs/ROADMAP.md`. That list is a copy of tracker state, and a copy goes stale
between phases: issues close with the PRs that fixed them, new ones are opened
on the way, a question gets answered in passing. Nobody notices a stale `Next`
until they pick up a closed item, and nobody ever notices a stale
`Open questions`.

**The deliverable is an agreed order, not a tidy file.** The mechanical half —
closed items off, new questions on — takes a minute. The half worth running
for is the judgement: where the new work goes, and whether the last phase
changed what should come first.

## Gathering in one pass

`scripts/gather.sh`, beside this file, runs the reads in Steps 1–3 and prints
one digest: checkout, convention, `since`, issues updated since, merges, the
last review's `File these` and `Decide these`, every issue `ROADMAP.md` lists
with its current state and open blockers, the open issues it does not, and a
`detail` section with the text behind them — every comment on those issues,
and the body of each one not yet placed. Run it from the project, after
Step 1's pull:

```bash
<skill-dir>/scripts/gather.sh
```

It reads only, and decides nothing: the steps below say what each section
means. Read the whole digest, `detail` included; the comments are there
because the decision is often in them. The commands below are the fallback
where the script cannot run, and the way to look closer at an issue.

## Step 1 — Be current, and find the convention

```bash
git switch <trunk> && git pull --ff-only     # usually main
gh repo view --json nameWithOwner 2>/dev/null   # a reachable tracker
ls docs/ROADMAP.md docs/DEFECTS.md 2>/dev/null
```

A checkout behind its remote reconciles the wrong file. The first row that
matches applies:

| Found | Do |
| --- | --- |
| A tracker **and** `DEFECTS.md`, whatever else is there | Stop. Moving defects to the tracker is `set-foundation`'s migration; say so, with at most a few lines on what it will meet. Reconcile nothing |
| A tracker and `ROADMAP.md` | The case this skill is for |
| A tracker, no `ROADMAP.md` | Propose one only if more than one open item needs ordering, or the project orders by milestone instead — then read the milestone |
| No tracker | Reconcile `ROADMAP.md` against `DEFECTS.md` — entries fixed or removed — by the same steps |

## Step 2 — What changed since the roadmap was last touched

Anchor on `ROADMAP.md`'s own last commit. Not the last review: a review report
is deleted before its merge.

```bash
since=$(git log -1 --format=%cI -- docs/ROADMAP.md)

# issues opened, closed, relabelled or edited since
gh issue list --state all --limit 500 --search "updated:>$since" \
  --json number,title,state,labels,milestone \
  --jq '.[] | "\(.number) \(.state) \([.labels[].name] | join(",")) \(.milestone.title // "-") \(.title)"'

# what the phase in between did
git log --first-parent --since="$since" --format='%as %h %s'

# the last review's proposals, which outlive the report. Not filtered by
# date: a roadmap touched mid-phase puts the phase's review before the anchor
git log --full-history --diff-filter=A -1 --format='%h' --name-only -- 'docs/review-*.md'
git show <hash>:<path>          # read its `File these` and `Decide these`
```

For each issue updated since, read what changed — every one, not a sample:
`gh issue view <n> --comments` for the discussion, which often records a
decision the labels have not caught up with. It prints comments only; plain
`gh issue view <n>` has the body and the blockers Step 3 needs. The digest's
`detail` already holds both.

A review's `File these` item that never became an issue may have been fixed
on the branch instead: check it against the commits made after the review
(the digest lists them under it) before proposing to file it. One with no
issue and no commit is worth one line: it was proposed, and agreed or
dropped, and the repository cannot say which. A `Decide these` item is
checked the same way. A
review older than the phase that just ended was read last time; check it
against the tracker rather than re-proposing it.

The since-list says where to look first. It is not the boundary; Step 3 is.

## Step 3 — Reconcile, both directions

Against the **whole** tracker, not only what changed since the anchor — an
item listed in `Next` and closed before it is just as stale.

```bash
gh issue list --state all --limit 500 --json number,title,state,labels,milestone \
  --jq '.[] | "\(.number) \(.state) \([.labels[].name] | join(",")) \(.milestone.title // "-") \(.title)"'
```

Match numbers by reading the lists, not by grep: `core#16` is another
repository's issue, not this one's #16.

Match sections by **role**, not heading: the list that holds the order is
`Next`, the one that holds deferred questions is `Open questions`, whatever
the file calls them. A list with neither role — items blocked elsewhere, say
— is kept and reconciled the same way, by each issue's state.

| Saw | Is |
| --- | --- |
| A listed issue, now closed | **Obvious** — drop it |
| An open `question` issue not on `Open questions` | **Obvious** — add it |
| An `enhancement` with a milestone, not in `Next` | Scheduled somewhere, missing here — place it |
| An issue on `Open questions` not labelled `question` | Decided, or never a question. Moving it off is **obvious** where the issue records the decision; its place in `Next` is a proposal. An issue still labelled `question` *and* `enhancement` stays on `Open questions`, not in `Next` |
| An open `bug` or `enhancement` not in `Next` | A candidate, not an error. `Next` is an order, not a backlog |
| An open issue small enough that a `Next` item's PR would naturally take it along | A **rider**: propose it indented directly under that item, `with #N`, and give the reason: what the host's body says it touches that the rider needs (a file it edits, a document it rewrites or condenses, a breaking release it ships in). The test is the shared PR, not a matching filename; the evidence is the host's body, in `detail`, not a guess at its scope. It lands with its host or comes back as a candidate. One that fits with nothing stays in the tracker. "Fix it first" inside one PR is still a rider: the order of commits in a PR is not a roadmap order |
| A rider whose host has closed | Closed with it: **obvious**, drop it. Still open: missed the PR; a candidate again |
| An open `bug` or `enhancement` that cannot start until a choice it lays out is made ("decide before implementing") | A question in practice. Under `Decide`: answer it now (with the issue's recommendation, if it gives one), or add `question` beside its label and put it on `Open questions`. Add, do not swap: `enhancement` keeps saying the work is wanted, and it returns as a candidate once the answer takes `question` off |
| A listed item blocked on another repository | Check that issue's state (`gh issue view <n> -R <owner/repo>`). A closed blocker unblocks it |
| A short title that no longer matches its issue | Only if the issue's **scope** changed. A paraphrase is the point of a short title |

`gh issue view <n>` shows `blocked-by:` and `blocking:`. An item does not go
first while an open issue blocks it.

A rider needs no link: it shares its host's PR. A blocker orders *separate*
PRs — one that could not be reviewed or merged until the other has.

A placement that rests on one issue landing before another — "#24 first, it
changes the signature #19 edits" — is a dependency the tracker should hold,
not only this proposal. Where it does not, propose the link under `Decide`.
Once the user agrees, `scripts/block.sh <blocked> <blocker>` records it
(`owner/repo#N` for another repository's blocker; `--remove` to undo a link
set in error), so the next phase starts from it instead of re-deriving it. A
blocker that has closed blocks nothing — the digest shows open ones only —
and its link is history: leave it.

## Step 4 — Put the order to the user

Bring the obvious fixes as done-on-agreement, and the judgement as proposals.

**Every issue in the digest's `updated` and `open` sections gets a line**
(without the script: the since-list, and each open issue not on the roadmap),
with a reason: a position in `Next`, a rider on a `Next` item, a place on
`Open questions`, dropped, left off, or a question under `Decide`. Left off is a real answer — `Next` is
not a backlog — but it is stated, not implied by silence; several left off for
one reason can share a line. An updated issue that changed nothing goes under
`unchanged`, so the count still adds up.

The proposal is read rendered, so write it as markdown, not in a code fence,
and do not lean on spacing: aligned columns collapse, and lines not in a list
run together into one paragraph. Every line is a list item; a rider is a
nested item under its host. Link each issue number to its issue
(`https://github.com/<tracker>/issues/<n>`, the digest's `tracker:` line;
`owner/repo#N` links into that repository), bold its title, and put the
reason after a dash in italics:

```markdown
**Next**

1. [#41](https://github.com/owner/repo/issues/41) **config loader ignores `XDG_CONFIG_HOME`** — _kept (was 1)_
2. [#38](https://github.com/owner/repo/issues/38) **`sync --dry-run`** — _was 2_
   - with [#56](https://github.com/owner/repo/issues/56) **`--dry-run` missing from the README** — _new; #38's body adds the flag to the README's usage section_
3. [#52](https://github.com/owner/repo/issues/52) **sync exits 0 on a partial failure** — _new bug, from the last review_

- **Dropped:** [#44](https://github.com/owner/repo/issues/44) — _closed by #50_
- **Left off:** [#55](https://github.com/owner/repo/issues/55) — _cosmetic; nothing waits on it_

**Open questions**

- [#53](https://github.com/owner/repo/issues/53) **should sync follow symlinks?** — _new_

**Decide**

- [#35](https://github.com/owner/repo/issues/35) looks answered: #50 made deletion opt-in. Close it, or move it to `Next`?

**Unchanged:** [#47](https://github.com/owner/repo/issues/47) — _a comment, no decision_
```

**Before asking, check the proposal against the digest**, not against memory
of it:

- every number in `updated` and `open` appears, in a list or under
  `unchanged`;
- every placement and every `Decide` item cites what it rests on, and a
  comment that decided something is cited by its date;
- no item in `Next` comes before an open issue that blocks it.

A miss here is the failure this step exists to prevent: an issue the user
never hears about stays wherever it was.

Ask the user to **correct**, not to author. For each placement, give the
reason in a few words — what it depends on, what it unblocks, what the last
phase left warm. Do not impose a ranking rule (bugs first, oldest first); the
order is theirs.

A rider with evidence is a placement like any other: put it under its host
and let the user strike it. `Decide` is for choices with no default — a
question to answer, a tracker change — not for a proposal you have already
made.

- **Raise an open question only with evidence** that the last phase
  changed its answer. Re-asking every question every phase trains the user to
  skip the list.
- **Do not grow `Next` to hold every open issue.** An issue off the list is not
  lost; it is in the tracker.
- **Three decisions is a lot.** If there are more, sort harder.

## Step 5 — Write it

Only once the user has agreed the order. Keep the file's existing shape and
headings; a list left empty keeps its heading and says so ("None open."). With
no file, the shape is two lists of issue numbers with short titles — riders
indented under their host — and nothing else:

```markdown
# Roadmap

_The order open issues get picked up in. `gh issue list` is the full set._

## Next

1. #38 — `sync --dry-run`
   - with #56 — `--dry-run` is missing from the README
2. #41 — the config loader ignores `XDG_CONFIG_HOME`

## Open questions

- #53 — should `sync` follow symlinks?
```

**Where it lands**, unless the project's agent file says otherwise:

- **`ROADMAP.md` alone** — a `chore` commit on the trunk. Reordering a list
  does not need a PR.
- **Anything more** — a defect cleaned up, another document brought into
  line — a `chore/` branch, since that is a change someone should review.

Push, or open the PR, on the user's word. Tracker changes proposed in
`Decide` — closing, relabelling, filing, linking a blocker — wait for it the
same way: they are
visible outside the repository.

## What this is not

- **Not a review.** It does not judge the last phase; `review-boundary` did,
  and this reads what it proposed.
- **Not a migration.** `DEFECTS.md` to the tracker is `set-foundation`'s.
- **Not grooming.** It changes nothing in the tracker unasked.
- **Not a design session.** Placing an issue in the order does not scope it.
