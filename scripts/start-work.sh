#!/usr/bin/env bash

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <branch-name>"
    exit 1
fi

BRANCH_NAME="$1"

if [ -n "$(git status --porcelain)" ]; then
    echo "Error: working tree is not clean."
    git status --short
    exit 1
fi

git switch main
git pull --ff-only
git switch -c "$BRANCH_NAME"

echo "Created branch: $BRANCH_NAME"
