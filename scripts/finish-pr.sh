#!/usr/bin/env bash

set -e

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "Error: already on main."
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "Error: working tree is not clean."
    git status --short
    exit 1
fi

echo "Current branch: $CURRENT_BRANCH"
echo "This command assumes that the Pull Request has been reviewed and approved."

gh pr merge --merge --delete-branch

git switch main
git pull --ff-only

if git show-ref --verify --quiet "refs/heads/$CURRENT_BRANCH"; then
    git branch -d "$CURRENT_BRANCH"
fi

echo
echo "Workflow completed."
git status
