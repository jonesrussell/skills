---
name: ship-pr
description: Use after a PR exists and is ready to land. Reviews, fixes, creates follow-up issues, merges, watches CI, updates docs, and cleans up the branch. Invoke with "/ship-pr" or "/ship-pr 1097".
---

# Ship PR

Review, merge, and land a pull request through to production. Handles the full lifecycle from code review to branch cleanup.

**Announce at start:** "Using ship-pr to land this PR."

## When to Use

- After creating a PR (manually or via `finishing-a-development-branch`)
- When the user says "/ship-pr", "ship it", "land it", "merge and clean up"
- After `/review` when the user wants to proceed with merge

## Input

- **PR number**: From args, current branch, or prompt the user
- If no PR number: run `gh pr list` and ask which one

## The Pipeline

Execute steps in order. Each step gates the next.

### Step 1: Review

Fetch PR details and diff. Analyze for:

- Code correctness and project convention adherence
- Missing test coverage
- Security concerns
- Performance implications

Present a concise review with clear sections.

**Output format:**

```
## Review: PR #N — <title>

### Overview
<1-2 sentences>

### Issues
- **Fix now:** <things that must be fixed before merge>
- **Follow-up:** <things worth tracking but non-blocking>

### Verdict
Ship it / Fix first / Needs discussion
```

If verdict is "Ship it" with no fix-now items, skip to Step 3.

### Step 2: Fix and Issue

**Fix now:** Apply fixes directly, commit, push.

```bash
# Fix, then:
git add <files>
git commit -m "<type>(#N): <description>"
git push
```

**Follow-up items:** Create GitHub issues for each.

```bash
gh issue create --title "<title>" --body "<context>" --label "enhancement"
```

After fixes are pushed, re-verify tests pass before proceeding.

### Step 3: Merge

```bash
gh pr merge <number> --squash
```

Verify the merge succeeded:

```bash
gh pr view <number> --json state -q '.state'
# Must return "MERGED"
```

### Step 4: Watch CI

Poll CI until the pipeline completes. Check individual jobs if the run is slow.

```bash
# Get run ID for the merge commit
gh run list --limit 1 --json databaseId -q '.[0].databaseId'

# Check job-level status
gh run view <id> --json jobs -q '.jobs[] | "\(.name): \(.status) \(.conclusion)"'
```

**If CI fails:** Report the failing job and logs. Do not proceed to cleanup.

**If CI passes:** Continue.

### Step 5: Documentation

Check if specs or docs need updating. Common triggers:

- **Spec drift:** If pre-push hooks or drift detectors flagged stale specs during the branch work, verify they were updated. If not, update them now.
- **CLAUDE.md gotchas:** If the PR introduced a new architectural pattern or gotcha, add it to the project's CLAUDE.md.
- **Changelog:** If the project uses Keep a Changelog, add an entry.

Skip this step if the PR was documentation-only or had no architectural impact.

### Step 6: Cleanup

```bash
# Update local main
git checkout main
git pull --ff-only

# Delete local feature branch
git branch -d <feature-branch>

# Delete remote branch (if not auto-deleted by merge)
git push origin --delete <feature-branch> 2>/dev/null || true
```

### Step 7: Report

Summarize what happened:

```
## Shipped: PR #N — <title>

- Reviewed: <verdict>
- Fixed: <N items> / Created: <N issues>
- Merged: squash to <base-branch>
- CI: all green (<job count> jobs)
- Docs: <updated X / no changes needed>
- Cleanup: branch deleted, main updated
```

## Relationship to Other Skills

| Skill | Scope | Handoff |
|---|---|---|
| `finishing-a-development-branch` | Tests pass, decides what to do (merge/PR/keep/discard) | Creates PR, then `ship-pr` takes over |
| `code-review:code-review` | Reviews a PR for quality | `ship-pr` includes review as Step 1 |
| `requesting-code-review` | Asks for review before completing | Precedes `ship-pr` |
| `verification-before-completion` | Verifies work is actually done | Precedes `ship-pr` |

**Typical flow:**
```
TDD/implementation → finishing-a-development-branch → creates PR → ship-pr → landed
```

## Decision Points

| Situation | Action |
|---|---|
| Review finds blocking issues | Fix in Step 2 before merging |
| Review finds only follow-ups | Create issues, proceed to merge |
| CI fails after merge | Report failure, do NOT cleanup. User decides. |
| Spec drift detected | Update spec in a follow-up commit on main |
| PR has merge conflicts | Report to user. Do not force-merge. |
| No CI pipeline configured | Skip Step 4, warn the user |

## What This Skill Does NOT Do

- Create the PR (that's `finishing-a-development-branch` or manual)
- Run the test suite pre-merge (tests should have passed before PR creation)
- Deploy to production (CI handles that)
- Decide merge strategy (defaults to squash; user can override)
