#!/usr/bin/env bash
# Print what plan-next reads before it proposes an order, as one digest.
# Run from anywhere inside the repository. Reads only: it fetches, but
# switches, pulls and writes nothing.
#
#   plan-next/scripts/gather.sh [--limit N]
#
# Sections, each headed `== name`:
#   checkout        branch, and whether it is behind its upstream
#   convention      tracker, ROADMAP.md, DEFECTS.md
#   since           ROADMAP.md's last commit, the Step 2 anchor
#   updated         issues updated since the anchor
#   merges          first-parent commits since the anchor
#   review          the last review report's `File these` and `Decide these`
#   roadmap         every issue ROADMAP.md lists, with its current state
#   open            every open issue not on ROADMAP.md
#
# Issue lines read: number state labels milestone [blocked-by:...] title

set -uo pipefail

limit=500
[[ ${1:-} == --limit ]] && limit=${2:?--limit needs a number}

cd "$(git rev-parse --show-toplevel)" || exit 1

roadmap=docs/ROADMAP.md
defects=docs/DEFECTS.md

# one line per issue; open blockers only, since a closed one blocks nothing
issue_line='"\(.number) \(.state) \([.labels[].name] | join(",") | if . == "" then "-" else . end) \(.milestone.title // "-")\([.blockedBy.nodes[]? | select(.state == "OPEN") | "\(.repository.nameWithOwner // "")#\(.number)"] | if length > 0 then " blocked-by:" + join(",") else "" end) \(.title)"'
fields=number,title,state,labels,milestone,blockedBy

section() { printf '\n== %s\n' "$1"; }

# -- checkout ---------------------------------------------------------------
section checkout
branch=$(git branch --show-current)
echo "branch: ${branch:-(detached)}"
if git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
  git fetch --quiet 2>/dev/null || echo "fetch failed; behind-count may be stale"
  echo "behind upstream: $(git rev-list --count 'HEAD..@{upstream}')"
else
  echo "no upstream"
fi

# -- convention -------------------------------------------------------------
section convention
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null)
echo "tracker: ${repo:-none}"
[[ -f $roadmap ]] && echo "roadmap: $roadmap" || echo "roadmap: none"
[[ -f $defects ]] && echo "defects: $defects" || echo "defects: none"

if [[ -n $repo && -f $defects ]]; then
  echo "stop: tracker and DEFECTS.md both present — set-foundation's migration"
  exit 0
fi

# -- since ------------------------------------------------------------------
section since
since=$(git log -1 --format=%cI -- "$roadmap" 2>/dev/null)
echo "${since:-none}"

# -- updated ----------------------------------------------------------------
if [[ -n $repo && -n $since ]]; then
  section updated
  gh issue list --state all --limit "$limit" --search "updated:>$since" \
    --json "$fields" --jq ".[] | $issue_line"
fi

# -- merges -----------------------------------------------------------------
if [[ -n $since ]]; then
  section merges
  git log --first-parent --since="$since" --format='%as %h %s'
fi

# -- review -----------------------------------------------------------------
# Not filtered by date: a roadmap touched mid-phase puts the phase's review
# before the anchor. The report never exists on the trunk, so read it from
# the commit that added it.
section review
read -r hash path < <(
  git log --full-history --diff-filter=A -1 --format='%h' --name-only \
    -- 'docs/review-*.md' | paste -sd' ' -
)
if [[ -n ${hash:-} ]]; then
  echo "$(git log -1 --format='%as' "$hash") $hash $path"
  git show "$hash:$path" | awk '
    /^#+ / { keep = /^#+ (File these|Decide these)/ }
    keep
  '
else
  echo "none"
fi

[[ -n $repo ]] || exit 0

# -- roadmap / open ---------------------------------------------------------
# Bare #N only: core#16 is another repository's issue, and a roadmap lists
# only this one's (an item blocked elsewhere lives in that tracker).
listed=""
if [[ -f $roadmap ]]; then
  listed=$(grep -oE '(^|[^[:alnum:]_/#.-])#[0-9]+' "$roadmap" \
    | grep -oE '[0-9]+$' | sort -un | paste -sd' ' -)
fi

all=$(gh issue list --state all --limit "$limit" --json "$fields" \
  --jq ".[] | $issue_line")

section roadmap
for n in $listed; do
  line=$(grep -E "^$n " <<<"$all") || line="$n not found in the last $limit issues"
  echo "$line"
done

section open
grep -E '^[0-9]+ OPEN ' <<<"$all" | while read -r n rest; do
  [[ " $listed " == *" $n "* ]] || echo "$n $rest"
done
