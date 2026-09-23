> **Status: applied** (2026-09-23), on `feat/enforcement-axis`, alongside
> [REFINEMENTS-from-ombre-trial.md](REFINEMENTS-from-ombre-trial.md). Where
> each item landed:
>
> - **§1** became `review-boundary` *Part 5 — A previous round's fixes*, run
>   at every depth whenever the range remediates a review.
> - **§2** became *Quantifiers are claims about scope* in 2a, including the
>   invented-mechanism case, which is checked against the function body.
> - **§3** went into 2c as written.
> - **§4** is now mechanical, because the text already existed and the miss
>   recurred anyway: name the likeliest wrong implementation, check the
>   proposal fails against it, and run that in a throwaway copy under the
>   scratch path where practical.
> - **§5**: `Decide these` and the circular-range row are untouched. Saying
>   what the repository cannot answer is named as desirable under *What this
>   review is not*. Pinning the version under test is a trial-method point,
>   not a skill one, so it lives here and in the trial method rather than in
>   either `SKILL.md`.

# Notes from trials 2–4 of `review-boundary`

_`pickr`, `v0.5.0..v0.6.0`, 2026-09-22. Three further runs after the six
refinements in #2 landed. Companion to `docs/REFINEMENTS-from-pickr-trial.md`,
which records trial 1 and what changed because of it._

Each run was a sub-agent with **no conversation history**, pointed at the repo
`SKILL.md` rather than the installed copy, with expectations pre-registered
before the report was read. The range was the author's own work, including two
rounds of remediation of earlier reviews in this same series.

## The #2 refinements held up. Evidence, not impressions:

- **Citation rot 3/11 → 0/21** across three passes. Symbol anchoring worked.
  The failure did not disappear, it *moved* — see §2.
- **2f fired correctly**: flagged size and the 69% `foundational` ratio,
  reported the ratio as borderline rather than damning, declined to propose
  individual promotions at that ratio, and found an orphan the author had
  predicted would be clean. It also avoided two dead-pointer traps —
  deliberately-named *former* filenames, and a path belonging to a sibling
  package.
- **"Execute, don't read" earned the whole trial.** The most consequential
  finding across all four runs — an argument silently partial-matching its
  replacement, so a released "breaking rename" was a no-op — is invisible to
  reading and obvious to running.

## 1. The missing check: remediation is not a sweep

**The strongest single addition I can suggest.**

Every round of remediation introduced at least one error the next round
caught. The most instructive was structural, not a typo: a review listed three
files containing a retired rule, the author fixed those three, and the next
pass found four more — one of which had **shipped in the generated manual**.
One commit later, the same shape: a defect count updated in the agent file
only, while the defects document, the architecture document and two READMEs
kept the old number.

The author had, one commit earlier, written a project rule about exactly this
class of mistake. It did not help, because that rule was about quantifiers and
this was about sweeps.

**A review reports instances; a fix has to address the class.** Suggested as a
step after Part 4:

> ### Verifying a previous round's fixes
>
> When the range contains remediation of an earlier review, do not check that
> the named instances were fixed — check whether **other instances of the same
> class** survive. For each fix, state the general form of the defect, then
> search for that form repository-wide, **including generated output**
> (`man/`, rendered notebooks, built docs) that nobody edits by hand and
> therefore nobody greps. That is where the worst surviving instance lived,
> twice.

## 2. Scope words are the new anchor rot

Symbol anchoring fixed *where* a citation points. It did nothing for what the
sentence around it claims. Four bad claims in three commits:

| written | actual |
| --- | --- |
| "the only two `quantize()` calls" | four |
| "`unique(reqs$src_barcode)`" | a condition elided, under a heading reading *"unconditionally"* |
| "never leave the function" | returned, and consumed |
| "`.resolve_src_barcodes()` has already populated every row" | it *writes* `NA` for rows it does not place |

The first three are over-scoped quantifiers. The fourth is worse — an invented
mechanism, contradicted two lines into the function being described.

For 2a: **"only", "never", "always" and "every" are claims about scope, and a
file-scoped read cannot support one.** Verify quantifiers as claims in their
own right, with a repository-wide search, rather than treating them as prose
around a citation that already checked out.

## 3. A test can pin a defect instead of a contract

Mid-trial an upstream dependency released a fix that removed a limit. Four
tests went red — all using the out-of-range index as a *sentinel* for
"invalid". They were pinned to the defect, not to the rule they were named
after. Meanwhile a boundary test written deliberately with **no hardcoded
bound** passed unchanged and followed the dependency's new range correctly.

For 2c, alongside "does the example demonstrate the invariant or a side
effect":

> Does the example depend on a **value someone else owns**? A test asserting
> that input `X` is rejected is pinned to `X` being rejectable. If an upstream
> package, a vendor specification or a config default can reclassify `X`, the
> test breaks on a *fix* rather than on a regression. Prefer an example no
> external change can reclassify.

## 4. 2c should hold its own suggestions to 2c's standard

Recurred, so repeating it from trial 1's notes: the review proposed a
replacement example, the author wrote it, and the proposed example **also**
could not fail for the invariant. Two further attempts were needed. A proposed
example is a claim, and it needs the same "how does this go red" test the
review just applied to the one it rejected.

## 5. Small, from watching four runs

- **`Decide these` held at three every time**, across reports carrying up to
  thirteen findings, and the decision-vs-obvious-fix sort was right in all
  four. Do not loosen it.
- **The circular-range note landed unprompted** in every run where it applied.
  The floor-table row proposed in trial 1's notes may be unnecessary — the
  reports reached it on their own.
- **Reviews reliably said what they could not determine** rather than guessing
  — "I cannot tell from the repository whether this was put to you". That is
  what makes them trustworthy, it is easy to train out by accident, and it is
  worth naming as desirable somewhere in the skill.
- **Pin the version under test.** The installed copy was two revisions stale;
  invoking the skill by name would have silently tested the old one. Reading
  the repo file both avoids that and pins exactly what is being evaluated.
  Worth a line wherever trials are described.
