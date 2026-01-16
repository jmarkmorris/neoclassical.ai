#!/usr/bin/env bash
set -e

A="$1"
B="$2"

if [ -z "$A" ] || [ -z "$B" ]; then
  echo "usage: $0 <dirA> <dirB>" >&2
  exit 1
fi

find "$A" -type f | while read -r afile; do
  rel="${afile#$A/}"
  bfile="$B/$rel"

  if [ -f "$bfile" ]; then
    echo "=== $A/$rel ==="
    ls -l "$afile"
    echo "=== $B/$rel ==="
    ls -l "$bfile"
    echo
  fi
done

