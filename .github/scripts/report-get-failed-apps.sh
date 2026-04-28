#!/bin/bash
set -e

FAILED_APPS=$(gh api repos/"$GITHUB_REPOSITORY"/actions/runs/"$GITHUB_RUN_ID"/jobs \
  --jq '.jobs[] | select(.conclusion == "failure" and (.name | startswith("App deployment and testing"))) | .name' | \
  sed 's/App deployment and testing (//' | sed 's/)//' | \
  paste -sd ", " -)

echo "failed_apps=$FAILED_APPS" >> "$GITHUB_OUTPUT"
