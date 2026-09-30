#!/usr/bin/env bash

set -e

CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "Error: cannot create a PR from main."
    exit 1
fi

if git diff --cached --quiet; then
    echo "Error: no staged changes."
    echo "Stage the files you want to commit first."
    exit 1
fi

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <commit-message> <pr-body-file>"
    exit 1
fi

COMMIT_MESSAGE="$1"
PR_BODY_FILE="$2"

if [ ! -f "$PR_BODY_FILE" ]; then
    echo "Error: PR body file not found: $PR_BODY_FILE"
    exit 1
fi

echo "Staged files:"
git diff --cached --name-only

echo
echo "Checking staged changes..."
git diff --cached --check

git commit -m "$COMMIT_MESSAGE"
git push -u origin "$CURRENT_BRANCH"

gh pr create \
    --title "$COMMIT_MESSAGE" \
    --body-file "$PR_BODY_FILE"

echo
echo "Pull request created."
echo "Review the PR before running finish-pr.sh."
