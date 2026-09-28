---
name: set-foundation
description: Lay down a project's groundwork documents — the architecture notes, invariants, and contracts — and mark each rule as foundational, in question, or a loose contract. Works on a new project before there is code, and on a running one by recovering the architecture the code already implements and putting it to the user. Use when starting a project, when a project has no architecture document, when the existing documents are not trusted, or when asked what this project's actual rules are. Runs as a conversation; writes documents only once the user has agreed to them. Pairs with review-boundary, which checks each phase of work against the tiers this lays down.
metadata:
  author: Eric Hunt
  version: "1.1"
  summary: Lays a project's groundwork documents and tiers each rule foundational, in question, or contract
license: MIT
---

# Set the foundation

Most architecture documents fail the same way: every sentence in them reads
as equally authoritative. A rule fought for over two days and a placeholder
typed to stop thinking about it look identical on the page, so the next
reader — human or agent — defends both with the same energy, and the project
pays complexity rent on decisions nobody actually made.

**The deliverable of this skill is the tier, not the prose.** A one-line rule
marked `in question` is worth more than a well-argued page that does not say
how firmly it is meant.

**Keep the rules short.** A rule says what it is, why, and where it lives in
the code. It does not carry the incident that motivated it, the history of its
wording, or a defence against a challenge nobody has made — git keeps all of
that, and a rule re-read every phase should not make its reader carry it.

Run this in a planning mode. It is a conversation that ends in documents.

## The tiers

Every rule gets exactly one:

| Tier | Means | The test |
| --- | --- | --- |
| `foundational` | Load-bearing. Changing it changes what the project *is*. | Can you name the failure it prevents, and has it happened or would it plausibly happen? |
| `in question` | Written to get moving. Plausible, never earned. | Would you be relieved or annoyed if someone showed you a simpler design without it? |
| `contract` | A loose agreement kept for consistency — naming, layout, formatting. | Would a violation be *wrong*, or just *inconsistent*? |

- **`in question` is the default.** A rule reaches `foundational` by argument,
  not by being written down. If unsure, say so to the user rather than
  quietly promoting it.
- **A tier is a claim about confidence, not importance.** A `contract` can
  matter every day.
- **A `contract` is a statement, not a defence.** One or two lines. It needs
  no failure story and no test — though a test that keeps the code organised
  is welcome, and its rationale belongs in the test's own comment.

## Step 1 — Which mode

```bash
git log --oneline | wc -l
ls AGENTS.md CLAUDE.md README* 2>/dev/null
ls docs/ doc/ adr/ design/ 2>/dev/null
```

- **Greenfield** — little or no code. Mode A.
- **Running project** — code exists, documents are absent, thin, or not
  trusted. Mode B, the more common and more valuable case. Good documents that
  merely lack tiers: skip to Step 2 and tier what is there.

## Mode A — Greenfield

Everything comes from the user, and the risk is twenty confident rules about a
program nobody has written. Ask, in order:

1. **What the program is for**, in one sentence, and who is harmed when it is
   wrong.
2. **The shape of the domain** — the two or three nouns everything else is
   expressed in.
3. **What must never happen** — the only real `foundational` candidates now.
4. **What is already decided** — language, storage, deployment. Mostly
   `contract`.

Write **five to eight rules**, almost all `in question`, and say so plainly:
*these are predictions, and the first phase against them tests them.* Do not
write rules about code that does not exist yet.

## Mode B — Recover the architecture the code implements

### B1. Find what the code actually enforces

```bash
# guards, assertions, validators — the rules with teeth
grep -rnE 'assert|stopifnot|match\.arg|raise |panic!|throw new|abort\(' <source dirs>

# the prose the code carries about itself
grep -rniE '\b(must|never|always|invariant|do not|cannot|required)\b' <source dirs>

# recurring commit scopes name the project's parts
git log --format='%s' | sed 's/:.*//' | sort | uniq -c | sort -rn | head -20
```

Then read the public surface and the tests. A rule with a test that goes red
is a rule the project means; a rule only in a comment is a preference.

### B2. Find the gap in both directions

- **Enforced but unstated** — the code defends it, nothing says so. Usually
  `foundational`, and the most valuable thing you will write.
- **Stated but unenforced** — for a would-be `foundational` rule, either it
  needs something that goes red or it is not `foundational`; put both options
  to the user. A prohibition on *future* code is the exception: it cannot have
  an example. A `contract` needs neither.
- **Stated and contradicted** — report the code's version; it is what ships.

### B3. Do not invent

**Every rule you propose carries a citation** — a symbol or path. If you
cannot cite it, it is your taste, not this project's architecture. Where you
think the code *should* have a rule it lacks, offer it separately, labelled as
a suggestion.

Cite **symbols, test descriptions or paths, never line numbers**: a deletion
silently retargets a line number to whatever moved into its slot.

### B4. On a mature codebase, expect a lot of `foundational`

What survives many phases was selected for being load-bearing. Tier each rule
on its own evidence and let the share land where it lands — two-thirds or more
is normal. Tell the user this in Step 2, so nobody argues the ratio later.

## Step 2 — Put it to the user before writing anything

Bring **at most ten**, each on one line with a proposed tier and the evidence:

```
foundational  Well addresses are formatted in exactly one place
              -> `.well_address()` (R/plate-map.R); vigilant — a second
                 formatter in a new file would pass the tests
in question   Units are converted at the boundary, never inside
              -> only two call sites
contract      Exported functions are verb_noun
```

Ask the user to **correct**, not to author. Flag:

- any rule you moved to `foundational` on your own judgement;
- any `in question` rule the user treats as settled;
- anything enforced that the user did not know was;
- any `foundational` rule the user believes is enforced when it is only
  vigilant.

## Step 3 — Write the documents

Only after the user has been through the list. Prefer existing files.

### Start with three

| Document | Answers | Tiered? |
| --- | --- | --- |
| `README.md` | What is this, and how do I use it? | No |
| `docs/ARCHITECTURE.md` | Why is it built this way, and how firmly? | **Yes** |
| `AGENTS.md` / `CLAUDE.md` | How do I work in this repo? | No |

The agent file *points at* the architecture document; it never restates a
rule. Two copies of a rule will disagree.

### Split further on evidence, not up front

| Signal | Split out to | Because |
| --- | --- | --- |
| A section most PRs touch while the rest sits still | `docs/DEFECTS.md`, `docs/ROADMAP.md` | Churn: if defects live in the rules document, `git log` on it stops saying when the architecture changed |
| A procedure followed during one activity | `docs/TESTING.md`, `docs/RELEASING.md` | Procedures are followed start to finish; rules are checked one at a time |
| Facts about something the project does not control — an external API, a vendor spec, unit conversion | one document per source, named for it (`docs/UNITS.md`) | A fact is verified against its source, never tiered |
| Tooling or environment | `docs/DEV-SETUP.md` | Read once at setup |
| A document past roughly 300 lines | whichever fits | Past that, people grep rather than read |

Do not create a document to hold the history of the rules. Git is that
document.

### Give every document a first line

```markdown
# Testing

_Read when writing or fixing a test. What the code **must** do is in
[ARCHITECTURE.md](ARCHITECTURE.md)._
```

Anti-patterns: a document per source module (it goes stale invisibly), an
index document, a document nothing sends a reader to.

### Rule format

```markdown
### Well addresses are formatted in exactly one place

`foundational` · created: 2026-09-08 · agreed: 2026-09-16 · **vigilant**

Two formatters drift, and the drift shows up as a plate that loads into the
wrong rows — a wrong answer that looks right.

`.well_address()` (`R/plate-map.R`) is the only formatter.
```

1. **The rule**, one sentence, imperative, testable.
2. **The tier and dates**, and for a `foundational` rule its enforcement word.
3. **The failure it prevents** — for `foundational` and `in question` rules.
   If the only reason is "consistency", it is a `contract`.
4. **Where it lives in the code**, by symbol or path. Naming the test that
   goes red is optional; a well-named test is found by searching for it.

A `contract` is parts 1 and 2 and whatever a reader needs to follow it.

### Armored or vigilant — `foundational` rules only

The enforcement word answers one question: **could a real violation ship with
every test green?** That is only worth asking of a rule whose violation
matters, so only `foundational` rules carry it.

| Word | Means |
| --- | --- |
| `armored` | A violation nobody anticipated still goes red — a source sweep, a type or schema constraint, a structure where the second path cannot be built |
| `vigilant` | Only the cases someone thought of go red — tests of known inputs, or a prohibition on code nobody has written yet |

**The test: write the likeliest violation in a file that does not exist
yet.** If something goes red, armored. It is not a tier: a vigilant
`foundational` rule is not a reason to demote, it is where `review-boundary`
spends its attention. If you can name the forbidden form of a future-code
prohibition ("no second call to `quantize()` outside `R/units.R`"), it can be
swept for — sweep for it.

### The three dates

| Field | Means |
| --- | --- |
| `created:` | When the claim was first written down, as best you can tell cheaply — use today if it is new |
| `agreed:` | When the author settled this wording |
| `altered:` | When an agent last changed the wording without a fresh agreement |

**`altered:` newer than `agreed:`, or a missing `agreed:`, is unreviewed
drift** — a comparison, not a tag you have to remember.

**The integrity rule: `agreed:` may be written only in the session where the
user accepted that wording.** Not from silence, not retroactively. If you
changed the wording, you set `altered:`.

### Point the agent file at what happens next

The agent file is always loaded; a skill is loaded on demand. Add short
**pointer lines** naming the moments this project expects something to
happen:

```markdown
## Working agreement

Rules and their tiers: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

- **At a phase boundary, before opening a PR** — run `review-boundary`. It
  reports; it changes nothing.
- **When a rule's tier stops matching how the project treats it** — re-tier it
  in `ARCHITECTURE.md`, with the date.
- **When recording a defect** — `docs/DEFECTS.md`, never `ARCHITECTURE.md`.
```

Name the moment, not the tool. Point, never restate — one line each. Only
for skills and documents the project has. The pointer names the skill; the
skill never names the project. Put them to the user: they bind future
sessions.

## Step 4 — Hand off

> N foundational (A armored, V vigilant), N in question, N contracts. The
> `in question` ones are predictions — the first phase that strains against
> one should cost out the deviation rather than work around it. The vigilant
> `foundational` ones are defended by memory: <name them>.

Naming the vigilant rules is the useful half: it says where a violation can
ship with every test green.

## What this is not

- **Not a design session.** Record what is decided and how firmly; where the
  user has not decided, the output is `in question`.
- **Not a documentation pass.** This produces rules with tiers.
- **Not permanent.** Re-run it when the `in question` list stops matching what
  the project treats as negotiable.
- **Not a licence to refactor.** Report a bug you find; do not fix it here.
