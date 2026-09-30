---
name: plan-next
description: Decide what comes next at the start of a phase — bring docs/ROADMAP.md up to date with the issue tracker since the roadmap was last touched, then put the order to the user. Use on the trunk after a merge, before starting new work, when asked what to work on next, or when review-boundary reports a stale roadmap. Proposes first; writes ROADMAP.md only once the user has agreed the order, and changes nothing in the tracker. Pairs with set-foundation, which lays down the tracking convention, and review-boundary, which checks the end of a phase.
metadata:
  author: Eric Hunt
  version: "1.0"
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

A review's `File these` item that never became an issue is worth one line: it
was proposed, and agreed or dropped, and the repository cannot say which. A
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
| An issue on `Open questions` not labelled `question` | Decided, or never a question. Moving it off is **obvious** where the issue records the decision; its place in `Next` is a proposal |
| An open `bug` or `enhancement` not in `Next` | A candidate, not an error. `Next` is an order, not a backlog |
| A listed item blocked on another repository | Check that issue's state (`gh issue view <n> -R <owner/repo>`). A closed blocker unblocks it |
| A short title that no longer matches its issue | Only if the issue's **scope** changed. A paraphrase is the point of a short title |

`gh issue view <n>` shows `blocked-by:` and `blocking:`. An item does not go
first while an open issue blocks it.

## Step 4 — Put the order to the user

Bring the obvious fixes as done-on-agreement, and the judgement as proposals.

**Every issue in the digest's `updated` and `open` sections gets a line**
(without the script: the since-list, and each open issue not on the roadmap),
with a reason: a position in `Next`, a place on `Open questions`, dropped,
left off, or a question under `Decide`. Left off is a real answer — `Next` is
not a backlog — but it is stated, not implied by silence; several left off for
one reason can share a line. An updated issue that changed nothing goes under
`unchanged`, so the count still adds up.

```
Next
1. #41  config loader ignores XDG_CONFIG_HOME   kept (was 1)
2. #52  sync exits 0 on a partial failure       new bug, from the last review; before #38, which retries on it
3. #38  sync --dry-run                          was 2
dropped   #44 — closed by #50
left off  #55 — cosmetic; nothing waits on it

Open questions
- #53  should sync follow symlinks?             new

Decide
- #35 looks answered: #50 made deletion opt-in. Close it, or move it to Next?

unchanged  #47 (a comment, no decision)
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

- **Raise an open question only with evidence** that the last phase
  changed its answer. Re-asking every question every phase trains the user to
  skip the list.
- **Do not grow `Next` to hold every open issue.** An issue off the list is not
  lost; it is in the tracker.
- **Three decisions is a lot.** If there are more, sort harder.

## Step 5 — Write it

Only once the user has agreed the order. Keep the file's existing shape and
headings; a list left empty keeps its heading and says so ("None open."). With
no file, the shape is two lists of issue numbers with short titles, and
nothing else:

```markdown
# Roadmap

_The order open issues get picked up in. `gh issue list` is the full set._

## Next

1. #41 — the config loader ignores `XDG_CONFIG_HOME`

## Open questions

- #53 — should `sync` follow symlinks?
```

**Where it lands**, unless the project's agent file says otherwise:

- **`ROADMAP.md` alone** — a `chore` commit on the trunk. Reordering a list
  does not need a PR.
- **Anything more** — a defect cleaned up, another document brought into
  line — a `chore/` branch, since that is a change someone should review.

Push, or open the PR, on the user's word. Tracker changes proposed in
`Decide` — closing, relabelling, filing — wait for it the same way: they are
visible outside the repository.

## What this is not

- **Not a review.** It does not judge the last phase; `review-boundary` did,
  and this reads what it proposed.
- **Not a migration.** `DEFECTS.md` to the tracker is `set-foundation`'s.
- **Not grooming.** It changes nothing in the tracker unasked.
- **Not a design session.** Placing an issue in the order does not scope it.
