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
until they pick up a closed item, and nobody ever notices a stale `Door open`.

**The deliverable is an agreed order, not a tidy file.** The mechanical half —
closed items off, new questions on — takes a minute. The half worth running
for is the judgement: where the new work goes, and whether the last phase
changed what should come first.

## Step 1 — Be current, and find the convention

```bash
git switch <trunk> && git pull --ff-only
gh repo view --json nameWithOwner 2>/dev/null   # a reachable tracker
ls docs/ROADMAP.md docs/DEFECTS.md 2>/dev/null
```

A checkout behind its remote reconciles the wrong file.

| Found | Do |
| --- | --- |
| A tracker and `ROADMAP.md` | The case this skill is for |
| A tracker, no `ROADMAP.md` | Propose one only if more than one open item needs ordering, or the project orders by milestone instead — then read the milestone |
| A tracker **and** `DEFECTS.md` | Stop. Moving defects to the tracker is `set-foundation`'s migration; say so |
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

# the last review's proposals, which outlive the report
git log --full-history --diff-filter=A --since="$since" --format='%h' -- 'docs/review-*.md'
git show <hash>:<path>          # read its `File these` and `Decide these`
```

A review's `File these` item that never became an issue is worth one line: it
was proposed, and agreed or dropped, and the repository cannot say which.

## Step 3 — Reconcile, both directions

Against the **whole** tracker, not only what changed since the anchor — an
item listed in `Next` and closed before it is just as stale.

```bash
gh issue list --state all --limit 500 --json number,state,labels,milestone \
  --jq '.[] | "\(.number) \(.state) \([.labels[].name] | join(",")) \(.milestone.title // "")"'
```

Match numbers by reading the lists, not by grep: `core#16` is another
repository's issue, not this one's #16.

| Saw | Is |
| --- | --- |
| A listed issue, now closed | **Obvious** — drop it |
| An open `question` not on `Door open` | **Obvious** — add it |
| An `enhancement` with a milestone, not in `Next` | Scheduled somewhere, missing here — place it |
| A `Door open` issue no longer labelled `question` | Decided — it goes to `Next`, or it was closed |
| An open `bug` or `enhancement` not in `Next` | A candidate, not an error. `Next` is an order, not a backlog |
| A listed item blocked on another repository | Check that issue's state (`gh issue view <n> -R <owner/repo>`). A closed blocker unblocks it |
| A short title that no longer matches its issue | Only if the issue's **scope** changed. A paraphrase is the point of a short title |

`gh issue view <n>` shows `blocked-by:` and `blocking:`. An item does not go
first while an open issue blocks it.

## Step 4 — Put the order to the user

Bring the obvious fixes as done-on-agreement, and the judgement as proposals:

```
Next
1. #41  config loader ignores XDG_CONFIG_HOME   kept (was 1)
2. #52  sync exits 0 on a partial failure       new bug, from the last review
3. #38  sync --dry-run                          was 2
dropped  #44 — closed by #50

Door open
- #53  should sync follow symlinks?             new

Decide
- #35 looks answered: #50 made deletion opt-in. Close it, or move it to Next?
```

Ask the user to **correct**, not to author. For each placement, give the
reason in a few words — what it depends on, what it unblocks, what the last
phase left warm. Do not impose a ranking rule (bugs first, oldest first); the
order is theirs.

- **Raise a `Door open` question only with evidence** that the last phase
  changed its answer. Re-asking every question every phase trains the user to
  skip the list.
- **Do not grow `Next` to hold every open issue.** An issue off the list is not
  lost; it is in the tracker.
- **Three decisions is a lot.** If there are more, sort harder.

## Step 5 — Write it

Only once the user has agreed the order. Keep the file's existing shape. With
no file, the shape is two lists of issue numbers with short titles, and
nothing else:

```markdown
# Roadmap

_The order open issues get picked up in. `gh issue list` is the full set._

## Next

1. #41 — the config loader ignores `XDG_CONFIG_HOME`

## Door open

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
