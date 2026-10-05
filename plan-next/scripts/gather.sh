#!/usr/bin/env bash
# Print what plan-next reads before it proposes an order, as one digest.
# Run from anywhere inside the repository. Reads only: it fetches, but
# switches, pulls and writes nothing. Needs git, gh and jq.
#
#   plan-next/scripts/gather.sh [--limit N] [--max-detail N] [--since DATE]
#
# --since replaces the anchor, to re-read a phase or test on a quiet repo.
#
# Sections, each headed `== name`:
#   checkout        branch, and whether it is behind its upstream
#   convention      tracker, ROADMAP.md, DEFECTS.md
#   since           ROADMAP.md's last commit, the Step 2 anchor
#   updated         issues updated since the anchor
#   merges          first-parent commits since the anchor
#   review          the last review report's `File these` and `Decide these`,
#                   and the commits made after it
#   roadmap         every issue ROADMAP.md lists, with its current state
#   open            every open issue not on ROADMAP.md
#   detail          the text behind those lines (see below)
#
# Issue lines read: number state labels milestone [blocked-by:...] title

set -uo pipefail

limit=500
max_detail=30
since_arg=""
while (($#)); do
  case $1 in
    --limit) limit=${2:?--limit needs a number}; shift 2 ;;
    --max-detail) max_detail=${2:?--max-detail needs a number}; shift 2 ;;
    --since) since_arg=${2:?--since needs a date}; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v jq >/dev/null || { echo "gather.sh needs jq" >&2; exit 2; }
cd "$(git rev-parse --show-toplevel)" || exit 1

roadmap=docs/ROADMAP.md
defects=docs/DEFECTS.md

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
if [[ -n $since_arg ]]; then
  since=$(date -u -j -f %Y-%m-%d "$since_arg" +%Y-%m-%dT00:00:00Z 2>/dev/null ||
    date -u -d "$since_arg" +%Y-%m-%dT%H:%M:%SZ) || exit 2
  since_utc=${since:0:19}
  echo "$since (given)"
else
  since=$(git log -1 --format=%cI -- "$roadmap" 2>/dev/null)
  # the same instant in UTC, to compare against GitHub's timestamps as text
  since_utc=$(TZ=UTC0 git log -1 --date=format-local:%Y-%m-%dT%H:%M:%S \
    --format=%cd -- "$roadmap" 2>/dev/null)
  echo "${since:-none}"
fi

# -- the tracker, read once -------------------------------------------------
# Bare #N only: core#16 is another repository's issue, and a roadmap lists
# only this one's (an item blocked elsewhere lives in that tracker).
listed=""
if [[ -f $roadmap ]]; then
  listed=$(grep -oE '(^|[^[:alnum:]_/#.-])#[0-9]+' "$roadmap" \
    | grep -oE '[0-9]+$' | sort -un | paste -sd' ' -)
fi

issues="[]"
if [[ -n $repo ]]; then
  issues=$(gh issue list --state all --limit "$limit" --json \
    number,title,state,labels,milestone,blockedBy,createdAt,updatedAt,body,comments)
fi

# jq over the tracker, with the context every filter needs bound as variables
q() {
  jq -r --arg repo "$repo" --arg since "$since_utc" \
    --argjson listed "[${listed// /,}]" "$(cat <<'JQ'
# one line per issue; open blockers only, since a closed one blocks nothing.
# A blocker carries no repository field, so read it from its URL, and name
# the repository only when it is another one.
def line:
  "\(.number) \(.state) \([.labels[].name] | join(",") | if . == "" then "-" else . end) \(.milestone.title // "-")"
  + ([.blockedBy.nodes[]? | select(.state == "OPEN")
      | (.url | capture("github.com/(?<r>[^/]+/[^/]+)/issues/").r) as $r
      | "\(if $r == $repo then "" else $r end)#\(.number)"]
     | if length > 0 then " blocked-by:" + join(",") else "" end)
  + " \(.title)";
def after: .[0:19] > $since and $since != "";
def on_roadmap: .number as $n | $listed | index($n) != null;
def indent: gsub("\r"; "") | gsub("\n"; "\n    ");
JQ
)$1" <<<"$issues"
}

# -- updated ----------------------------------------------------------------
if [[ -n $repo && -n $since ]]; then
  section updated
  q '.[] | select(.updatedAt | after) | line'
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
  # A proposal fixed on the branch after the report was written never reaches
  # the tracker, and a first-parent log hides it inside the merge. Listing
  # the commits makes "already done" checkable rather than remembered.
  echo
  echo "commits after the review:"
  git log --no-merges -n 30 --format='%as %h %s' "$hash..HEAD"
else
  echo "none"
fi

[[ -n $repo ]] || exit 0

# -- roadmap / open ---------------------------------------------------------
section roadmap
for n in $listed; do
  q ".[] | select(.number == $n) | line" | grep . ||
    echo "$n not found in the last $limit issues"
done

section open
q '.[] | select(.state == "OPEN" and (on_roadmap | not)) | line'

# -- detail -----------------------------------------------------------------
# Delivered, not fetched on demand: a discussion often records a decision the
# labels have not caught up with, and whether to read it is not left to
# judgement. Which issues is set by what the proposal must account for, not by
# date: an issue opened just before a roadmap touched in passing is as
# unplaced as one opened after it.
#
#   comments  every issue in roadmap (open), open, and updated
#   body      open issues other than questions — a candidate's to place it,
#             a `Next` item's to judge what rides with it — and issues opened
#             since the anchor
#
# An issue with neither is left out; its line above is all there is.
#
# Comments posted since the anchor are marked new.
section detail
# shellcheck disable=SC2016  # jq variables, not shell ones
select_detail='[.[] | select(.state == "OPEN" or (.updatedAt | after))
    | .show_body = ((.state == "OPEN" and ([.labels[].name] | index("question") | not))
                    or (.createdAt | after))
    | select(.show_body or (.comments | length > 0))]
  | sort_by(if on_roadmap then 0 elif .state == "OPEN" then 1 else 2 end, .number)'
# shellcheck disable=SC2016
q "$select_detail | .[:$max_detail][] |
  \"#\(.number) \(.title)\",
  (if .show_body then \"  body:\n    \(.body | indent)\" else empty end),
  (.comments[] | \"  comment \(.author.login) \(.createdAt[0:10])\(if .createdAt | after then \" (new)\" else \"\" end):\n    \(.body | indent)\"),
  \"\""
rest=$(q "$select_detail | .[$max_detail:] | map(\"#\(.number)\") | join(\" \")")
[[ -n $rest ]] && echo "not detailed (over --max-detail $max_detail): $rest"
exit 0
