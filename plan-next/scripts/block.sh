#!/usr/bin/env bash
# Record, or remove, that one issue blocks another — GitHub's issue
# dependency, which `gh issue view` prints as blocked-by / blocking. Writes to
# the tracker, so run it only on the user's word.
#
#   plan-next/scripts/block.sh <blocked> <blocker> [--remove]
#
# <blocked> is an issue number in this repository. <blocker> is a number here,
# or owner/repo#N for another repository's issue. Setting a link that exists,
# or removing one that does not, says so and changes nothing.

set -uo pipefail

usage() { echo "usage: block.sh <blocked> <blocker> [--remove]" >&2; exit 2; }
# Exact arguments only: an unrecognised flag must stop the script, not be
# ignored on the way to a write.
case $# in
  2) remove="" ;;
  3) [[ $3 == --remove ]] || usage; remove=$3 ;;
  *) usage ;;
esac
blocked=$1 blocker=$2
[[ $blocked =~ ^[0-9]+$ ]] || usage

repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner) || exit 1
if [[ $blocker =~ ^([^/#]+/[^/#]+)#([0-9]+)$ ]]; then
  blocker_repo=${BASH_REMATCH[1]} blocker_n=${BASH_REMATCH[2]}
elif [[ $blocker =~ ^#?([0-9]+)$ ]]; then
  blocker_repo=$repo blocker_n=${BASH_REMATCH[1]}
else
  usage
fi
label="$blocker_repo#$blocker_n"
[[ $blocker_repo == "$repo" ]] && label="#$blocker_n"

# The endpoint takes the blocker's database id, not its number.
id=$(gh api "repos/$blocker_repo/issues/$blocker_n" --jq .id) || exit 1
endpoint="repos/$repo/issues/$blocked/dependencies/blocked_by"
present=$(gh api "$endpoint" --jq "any(.[]; .id == $id)") || exit 1

if [[ -z $remove ]]; then
  if [[ $present == true ]]; then
    echo "#$blocked is already blocked by $label"
  else
    gh api -X POST "$endpoint" -F issue_id="$id" --silent &&
      echo "#$blocked is now blocked by $label"
  fi
else
  if [[ $present == true ]]; then
    gh api -X DELETE "$endpoint/$id" --silent &&
      echo "#$blocked is no longer blocked by $label"
  else
    echo "#$blocked is not blocked by $label"
  fi
fi
