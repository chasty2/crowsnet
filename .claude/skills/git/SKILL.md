---
name: git
description: Git workflow conventions for this repo. Use when creating branches, writing commits, opening or merging pull requests, or doing any git/gh work.
---

# Git Workflow

## Branches

- Start each plan by creating a new branch; all work happens outside `main`
- One goal per branch
- Pushes to `main` are blocked by a pre-push hook; enable once per clone:
  `git config core.hooksPath .githooks`
- If the repo has no `.githooks/pre-push`, bootstrap it from this skill:
  copy `hooks/pre-push` (bundled next to this file) into `.githooks/`,
  `chmod +x` it, then run `git config core.hooksPath .githooks`

## Commits

- Commit early and often, after each meaningful change
- One commit per file or group of similar files
- Keep messages concise: the subject states *what* changed
- Add a body only when the *why* isn't obvious (complex or surprising changes)
- Commits get squashed on merge — the PR is the durable record, so don't
  duplicate PR-level detail in commit messages
- When applicable, run the integration testing workflow and have it pass
  before committing

## Pull Requests

- Title uses a semantic tag: `feat:`, `fix:`, `refactor:`, `docs:`
  (the PR title becomes the squash-commit subject on `main`, so write it
  as a good commit subject)
- Fill in the PR template (`.github/PULL_REQUEST_TEMPLATE.md`); reference
  related issues with `Closes #N`
- After pushing, check CI: `gh run list --branch <branch>`
- Check in with the user for approval before merging

## Merging

- Always squash-and-merge: `gh pr merge --squash`
