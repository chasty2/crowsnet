---
name: git
description: Git workflow conventions for this repo. Use when creating branches, writing commits, opening or merging pull requests, or doing any git/gh work.
---

# Git Workflow

## Branches

- Start each plan by creating a new branch; all work happens outside `main`
- Name branches `<tag>/<kebab-slug>`, where `<tag>` is one of the PR tags below
  (`feat/dev-role`, `chore/share-claude-settings`); prefix the slug with an
  issue number when the work closes one (`fix/73-update-apt-cache`)
- Pushes to `main` are blocked by a pre-push hook; enable once per clone:
  `git config core.hooksPath .githooks`
- If the repo has no `.githooks/pre-push`, bootstrap it from this skill:
  copy `hooks/pre-push` (bundled next to this file) into `.githooks/`,
  `chmod +x` it, then run `git config core.hooksPath .githooks`

## Commits

- Commit early and often, and default to splitting: a change spanning several
  files or layers is usually several commits. Squash-on-merge (see Merging)
  means intermediate commits needn't build or pass, so splitting is cheap —
  "each commit should work alone" is no reason to bundle
- Split by the *reason* for each change: a dependency bump, wiring it into the
  image, and a config tweak are separate commits even when shipped together.
  Tests ride with the code they cover
- If the subject needs "and", a comma, or a list, it is likely more than one commit —
  stage the pieces with `git add -p` and commit each separately
- Subject states *what* changed; add a body only when the *why* isn't obvious
- The PR is the durable record, so don't repeat PR-level detail in commits

## Pull Requests

- Title uses a semantic tag: `feat:`, `fix:`, `refactor:`, `docs:`, `ci:`,
  `chore:` — the same tags used as branch prefixes above
  (the PR title becomes the squash-commit subject on `main`, so write it
  as a good commit subject)
- Fill in the PR template (`.github/PULL_REQUEST_TEMPLATE.md`): Summary,
  Changes, Validation, References
- After pushing, check CI: `gh run list --branch <branch>`
- Check in with the user for approval before merging

## Merging

- Only merge once CI is green (check with `gh run list --branch <branch>`)
- Always squash-and-merge and delete the branch: `gh pr merge --squash --delete-branch`
