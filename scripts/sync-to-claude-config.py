#!/usr/bin/env python3
"""Mirror this repo's skills into nebiolabs/claude-config under skills/hunt/.

This repo is the source of truth; claude-config is a mirror. The script copies
any skill whose contents differ, regenerates skills/hunt/README.md, upserts the
rows for skills/hunt/ in the root README table, then branches, commits, pushes
and opens a PR.

Usage:
    scripts/sync-to-claude-config.py [--dry-run] [--no-pr] [--no-root-readme]
                                     [--target DIR] [--branch NAME]

Each skill directory needs two things beyond SKILL.md:

  * `metadata.summary` in the front matter — one line, the README table cell.
    The front matter `description` is written for skill triggering and is far
    too long for a table.
  * `README.md` — the in-depth prose for skills/<author>/README.md. Keeping it
    with the skill means the mirror is generated in one pass, with no stubs to
    come back and fill in.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = Path.home() / "GitHub" / "claude-config"
AUTHOR = "hunt"
REPO = "nebiolabs/claude-config"
BRANCH_PREFIX = f"chore/sync-{AUTHOR}-skills-"

# Directories in this repo that are not skills.
SKIP = {".git", ".remember", ".vscode", "docs", "scripts", "temp"}


# --------------------------------------------------------------------------- #
# Reading skills
# --------------------------------------------------------------------------- #


def frontmatter(skill_md: Path) -> dict[str, str]:
    """Pull the flat keys we need out of a SKILL.md front matter block.

    Deliberately not a YAML parser: we want `name`, and `summary` from under
    `metadata`, and nothing else. A real parser would be a dependency for two
    fields.
    """
    text = skill_md.read_text()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise SystemExit(f"{skill_md}: no front matter")
    block = match.group(1)

    def field(key: str, indented: bool) -> str | None:
        prefix = r"  " if indented else r""
        m = re.search(rf"^{prefix}{key}:[ \t]*(.+?)[ \t]*$", block, re.MULTILINE)
        return m.group(1).strip().strip('"') if m else None

    name = field("name", indented=False)
    summary = field("summary", indented=True)
    if not name:
        raise SystemExit(f"{skill_md}: front matter has no `name`")
    if not summary:
        raise SystemExit(
            f"{skill_md}: front matter has no `metadata.summary`.\n"
            "  Add a one-line summary (<=100 chars) — it is the README table cell."
        )
    readme = skill_md.parent / "README.md"
    if not readme.exists():
        raise SystemExit(
            f"{skill_md.parent}/README.md is missing.\n"
            "  It holds the in-depth description for skills/<author>/README.md."
        )
    return {"name": name, "summary": summary, "prose": readme.read_text().strip()}


def discover(source: Path) -> list[dict[str, str]]:
    skills = []
    for entry in sorted(source.iterdir()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in SKIP:
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        meta = frontmatter(skill_md)
        if meta["name"] != entry.name:
            raise SystemExit(
                f"{skill_md}: front matter name '{meta['name']}' "
                f"does not match directory '{entry.name}'"
            )
        meta["path"] = entry
        skills.append(meta)
    if not skills:
        raise SystemExit(f"no skills found under {source}")
    return skills


def tree_differs(src: Path, dst: Path) -> bool:
    """True if the two directory trees are not byte-identical."""
    if not dst.exists():
        return True
    cmp = filecmp.dircmp(src, dst)

    def walk(c: filecmp.dircmp) -> bool:
        if c.left_only or c.right_only or c.diff_files or c.funny_files:
            return True
        return any(walk(sub) for sub in c.subdirs.values())

    # dircmp compares by os.stat by default; force a content comparison.
    filecmp.clear_cache()
    return walk(cmp) or _content_differs(src, dst)


def _content_differs(src: Path, dst: Path) -> bool:
    src_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    dst_files = {p.relative_to(dst) for p in dst.rglob("*") if p.is_file()}
    if src_files != dst_files:
        return True
    return any(
        (src / rel).read_bytes() != (dst / rel).read_bytes() for rel in src_files
    )


# --------------------------------------------------------------------------- #
# README rendering
# --------------------------------------------------------------------------- #


def render_author_readme(skills: list[dict[str, str]]) -> str:
    """Rebuild skills/<author>/README.md from the source repo alone.

    The table comes from each skill's `metadata.summary`; the prose below it
    comes from each skill's own README.md. Nothing is preserved from the
    mirror, so the file cannot drift and there is never a stub to fill in
    on a second pass.
    """
    name_w = max(len(f"[`{s['name']}`]({s['name']}/SKILL.md)") for s in skills)
    desc_w = max(len(s["summary"]) for s in skills)

    lines = [
        f"# skills/{AUTHOR}/",
        "",
        "Skills authored by Eric Hunt.",
        "",
        "> Mirrored from [`eric-hunt/agent-skills`](https://github.com/eric-hunt/agent-skills),",
        "> which is the source of truth. Send fixes there — edits made here are",
        "> overwritten on the next sync.",
        "",
        "## Skills",
        "",
        f"| {'Skill'.ljust(name_w)} | {'Description'.ljust(desc_w)} |",
        f"| {'-' * name_w} | {'-' * desc_w} |",
    ]
    for s in skills:
        link = f"[`{s['name']}`]({s['name']}/SKILL.md)"
        lines.append(f"| {link.ljust(name_w)} | {s['summary'].ljust(desc_w)} |")

    for s in skills:
        lines += ["", f"### [`{s['name']}`]({s['name']}/SKILL.md)", "", s["prose"]]

    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines).rstrip()) + "\n"


ROOT_ROW = re.compile(r"^\|\s*\[`(?P<name>[^`]+)`\]\((?P<path>[^)]+)\)\s*\|(?P<rest>.*)\|\s*$")


def upsert_root_readme(text: str, skills: list[dict[str, str]]) -> tuple[str, list[str]]:
    """Insert or update this author's rows in the shared, alphabetised table.

    Rows belonging to other authors are never rewritten — not even their
    padding — so the PR diff shows only what actually changed.
    """
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Skills")
    except StopIteration:
        raise SystemExit("root README: no '## Skills' heading found")

    header = next(i for i in range(start, len(lines)) if lines[i].lstrip().startswith("|"))
    end = header
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        end += 1
    rows = lines[header + 2 : end]  # skip header and separator

    widths = [0, 0]
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) >= 2:
            widths = [max(widths[0], len(cells[0])), max(widths[1], len(cells[1]))]

    kept = [r for r in rows if f"skills/{AUTHOR}/" not in r]
    changed = []
    for s in skills:
        link = f"[`{s['name']}`](skills/{AUTHOR}/{s['name']}/SKILL.md)"
        row = f"| {link.ljust(widths[0])} | {s['summary'].ljust(widths[1])} |"
        previous = next((r for r in rows if f"skills/{AUTHOR}/{s['name']}/" in r), None)
        if previous is None or previous.rstrip() != row.rstrip():
            changed.append(s["name"])
        kept.append(row)

    def sort_key(row: str) -> str:
        m = ROOT_ROW.match(row.strip())
        return (m.group("name") if m else row).lower()

    merged = lines[: header + 2] + sorted(kept, key=sort_key) + lines[end:]
    return "\n".join(merged) + "\n", changed


# --------------------------------------------------------------------------- #
# Git
# --------------------------------------------------------------------------- #


def git(target: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(target), *args], capture_output=True, text=True
    )
    if check and result.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def open_sync_pr(target: Path) -> str | None:
    """URL of an already-open PR from a previous run, if there is one.

    The change plan is computed against the target's `main`, so an unmerged
    sync PR keeps showing up as pending work. Without this check a second run
    opens a duplicate PR — noise in a repository other people watch. A gh
    failure returns None rather than blocking: this is a guard, not a gate.
    """
    result = subprocess.run(
        ["gh", "pr", "list", "--repo", REPO, "--state", "open",
         "--json", "headRefName,url"],
        cwd=target, capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    try:
        prs = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return None
    return next(
        (pr["url"] for pr in prs if pr["headRefName"].startswith(BRANCH_PREFIX)),
        None,
    )


def require_clean_main(target: Path) -> None:
    branch = git(target, "branch", "--show-current")
    if branch != "main":
        raise SystemExit(f"{target} is on '{branch}'; switch to main first")
    dirty = [
        l for l in git(target, "status", "--porcelain").splitlines()
        if not l.startswith("??")
    ]
    if dirty:
        raise SystemExit(f"{target} has uncommitted changes:\n" + "\n".join(dirty))
    git(target, "fetch", "origin", "main")
    if git(target, "rev-parse", "HEAD") != git(target, "rev-parse", "origin/main"):
        raise SystemExit(f"{target} main differs from origin/main; pull first")


# --------------------------------------------------------------------------- #


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    ap.add_argument("--branch", default=None,
                    help="branch name; passing one explicitly also overrides the "
                         "open-PR guard")
    ap.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    ap.add_argument("--no-pr", action="store_true", help="commit and push, but do not open a PR")
    ap.add_argument("--no-root-readme", action="store_true", help="leave the shared root table alone")
    ap.add_argument("--prune", action="store_true",
                    help="delete mirrored skills that no longer exist here (needed after a rename)")
    args = ap.parse_args()

    explicit_branch = args.branch is not None
    args.branch = args.branch or f"{BRANCH_PREFIX}{date.today()}"

    target = args.target.expanduser().resolve()
    skills_dir = target / "skills" / AUTHOR
    if not (target / ".git").exists():
        raise SystemExit(f"{target} is not a git repository")

    skills = discover(SOURCE)
    source_sha = subprocess.run(
        ["git", "-C", str(SOURCE), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip()

    # What differs?
    added = [s for s in skills if not (skills_dir / s["name"]).exists()]
    updated = [
        s for s in skills
        if (skills_dir / s["name"]).exists() and tree_differs(s["path"], skills_dir / s["name"])
    ]
    mirrored = {s["name"] for s in skills}
    removed = sorted(
        d.name for d in skills_dir.iterdir()
        if d.is_dir() and d.name not in mirrored
    ) if skills_dir.exists() else []

    author_readme = skills_dir / "README.md"
    new_author = render_author_readme(skills)
    author_changed = not author_readme.exists() or author_readme.read_text() != new_author

    root_readme = target / "README.md"
    root_text = root_readme.read_text()
    new_root, root_changed = ("", []) if args.no_root_readme else upsert_root_readme(root_text, skills)
    root_dirty = bool(root_changed) and not args.no_root_readme

    print(f"source  {SOURCE}  @ {source_sha}")
    print(f"target  {target}")
    for s in added:
        print(f"  + {s['name']}")
    for s in updated:
        print(f"  ~ {s['name']}")
    for name in removed:
        print(f"  - {name}" if args.prune
              else f"  ! {name} is in the mirror but not here — pass --prune to delete it")
    if author_changed:
        print(f"  ~ skills/{AUTHOR}/README.md")
    for name in root_changed:
        print(f"  ~ README.md row: {name}")

    if not (added or updated or author_changed or root_dirty or (removed and args.prune)):
        print("\nnothing to sync.")
        return 0

    pending = None if explicit_branch else open_sync_pr(target)

    if args.dry_run:
        if pending:
            print(f"\nnote: {pending} is still open — the changes above are "
                  "probably already in it.")
        print("--dry-run: nothing written.")
        return 0

    if pending:
        raise SystemExit(
            f"a sync PR is already open: {pending}\n"
            "  Merge or close it first — the plan above is computed against the "
            "target's main,\n  so re-running now would open a duplicate. Pass "
            "--branch NAME to override."
        )

    require_clean_main(target)
    git(target, "checkout", "-b", args.branch)

    if args.prune:
        for name in removed:
            shutil.rmtree(skills_dir / name)
    for s in added + updated:
        dst = skills_dir / s["name"]
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(s["path"], dst, ignore=shutil.ignore_patterns(".DS_Store"))
    if author_changed:
        author_readme.write_text(new_author)
    if root_dirty:
        root_readme.write_text(new_root)

    names = [s["name"] for s in added + updated]
    subject = (
        f"docs: add {names[0]} skill" if len(names) == 1 and added
        else f"docs: sync {AUTHOR} skills from agent-skills"
    )
    body = (
        f"{subject}\n\n"
        f"Mirrored from eric-hunt/agent-skills @ {source_sha}.\n"
    )
    if added:
        body += "\nAdded: " + ", ".join(s["name"] for s in added)
    if updated:
        body += "\nUpdated: " + ", ".join(s["name"] for s in updated)
    if removed and args.prune:
        body += "\nRemoved: " + ", ".join(removed)
    body += "\n\nCo-Authored-By: Claude Opus 5 <noreply@anthropic.com>\n"

    git(target, "add", "-A", "skills", "README.md")
    git(target, "commit", "-m", body)
    git(target, "push", "-u", "origin", args.branch)

    if args.no_pr:
        print(f"\npushed {args.branch}; PR not opened (--no-pr)")
        return 0

    pr_body = (
        f"Mirrors [`eric-hunt/agent-skills`]"
        f"(https://github.com/eric-hunt/agent-skills) @ `{source_sha}` into "
        f"`skills/{AUTHOR}/`, which is a mirror of that repo.\n\n"
    )
    if added:
        pr_body += "**Added**\n" + "".join(
            f"- `{s['name']}` — {s['summary']}\n" for s in added
        ) + "\n"
    if updated:
        pr_body += "**Updated**\n" + "".join(
            f"- `{s['name']}` — {s['summary']}\n" for s in updated
        ) + "\n"
    if removed and args.prune:
        pr_body += "**Removed**\n" + "".join(f"- `{n}`\n" for n in removed) + "\n"
    pr_body += (
        "Opened by `scripts/sync-to-claude-config.py`. Send fixes to the source "
        "repo rather than here — edits made in this repo are overwritten on the "
        "next sync.\n\n"
        "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n"
    )

    result = subprocess.run(
        ["gh", "pr", "create", "--repo", REPO,
         "--base", "main", "--head", args.branch,
         "--title", subject, "--body", pr_body],
        cwd=target, capture_output=True, text=True,
    )
    print(result.stdout.strip() or result.stderr.strip())
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
