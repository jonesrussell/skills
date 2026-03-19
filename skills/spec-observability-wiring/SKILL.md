---
name: spec-observability-wiring
description: Use when wiring a drift-detector script into enforcement surfaces (task runner, git hooks, CI) as a hard gate in any monorepo. Triggers include "wire drift detection", "enforce spec freshness", "add spec checks to CI", "make drift detector a gate", or any request to connect an existing spec-drift or doc-staleness checker into Taskfile/Makefile, lefthook/husky, and GitHub Actions/GitLab CI. Also use when the user has a working detection script but it's not enforced anywhere.
---

# Spec Observability Wiring

Wire an existing drift-detector script into all enforcement surfaces so stale specs block merges. This skill assumes you already have a working detector — if not, build one first (see `updating-codified-context` skill).

## Why This Matters

A drift detector that only runs manually is documentation theater. Specs go stale the moment enforcement stops. The pattern here makes freshness a hard gate: you can't push, can't pass CI, can't merge if your specs are behind your code.

## Prerequisites

Before starting, verify:
1. A working drift-detector script exists (e.g., `tools/drift-detector.sh`)
2. It exits non-zero when specs are stale
3. It accepts a commit-count argument (e.g., `drift-detector.sh 5`)
4. The repo uses a task runner (Taskfile, Makefile, package.json scripts)
5. The repo uses git hooks (lefthook, husky, or raw `.git/hooks/`)
6. The repo has CI (GitHub Actions, GitLab CI, etc.)

Run the detector once to confirm it works:
```bash
bash tools/drift-detector.sh 5
```

## Step 1: Task Runner Integration

Add a dedicated task that wraps the detector. This becomes the single entry point everything else calls or mirrors.

**Taskfile.yml pattern:**
```yaml
drift:check:
  desc: "Check for spec drift (stale specs vs recent service changes)"
  cmds:
    - tools/drift-detector.sh {{.CLI_ARGS | default "5"}}
```

**Makefile pattern:**
```makefile
.PHONY: drift-check
drift-check:
	tools/drift-detector.sh $(or $(COMMITS),5)
```

**package.json pattern:**
```json
"scripts": {
  "drift:check": "tools/drift-detector.sh ${COMMITS:-5}"
}
```

Then wire it as the **first step** in all CI-like composite tasks (the ones developers run before pushing). First position means fast feedback — no waiting through lint+test only to fail on stale specs.

```yaml
# Taskfile example
ci:
  cmds:
    - task: drift:check    # first — fast, catches spec debt early
    - task: lint
    - task: test
    - task: vuln
```

Apply to all CI task variants (ci, ci:changed, ci:force, or equivalents).

## Step 2: Git Hook Integration

Add the drift check to **pre-push** (not pre-commit — drift detection needs git history which isn't available during commit staging, and it shouldn't slow down every commit).

**lefthook.yml pattern:**
```yaml
pre-push:
  parallel: true
  commands:
    spec-drift:
      run: tools/drift-detector.sh 5
```

**husky pattern** (`.husky/pre-push`):
```bash
#!/bin/sh
tools/drift-detector.sh 5
```

**Raw git hook** (`.git/hooks/pre-push`):
```bash
#!/bin/sh
tools/drift-detector.sh 5
```

The hook runs the detector directly rather than going through the task runner, keeping hook execution fast and dependency-free.

## Step 3: CI Pipeline Integration

Add a dedicated CI job that runs **in parallel** with lint/test/vuln — not as a dependency of them. This keeps the critical path short while still gating merges.

**GitHub Actions pattern:**
```yaml
spec-drift:
  name: Spec Drift Check
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # full history needed for git log comparisons

    - name: Check spec drift
      run: tools/drift-detector.sh 20
```

Key details:
- `fetch-depth: 0` is required — the detector compares commit timestamps
- Use a higher commit count (20) in CI since it covers full PR scope
- No `needs:` — runs parallel with other jobs for speed
- Job failure blocks merge via branch protection required status checks

**GitLab CI pattern:**
```yaml
spec-drift:
  stage: validate
  script:
    - tools/drift-detector.sh 20
  variables:
    GIT_DEPTH: 0
```

## Step 4: Documentation

Update the project's CLAUDE.md (or equivalent developer docs) in three places:

1. **Quick Reference / Commands section** — add the task runner command:
   > `task drift:check` — checks for stale specs, runs as first step of CI tasks

2. **Before Making Changes / Pre-flight checklist** — add the check:
   > Run `task drift:check` — if a spec is STALE, update it before or alongside your code changes

3. **Git Hooks section** — document what the pre-push hook now does:
   > pre-push: `spec-drift` (drift-detector check)

4. **Before Committing / Pre-push checklist** — add the step:
   > Run spec drift check: `task drift:check` (ensure affected specs are up to date)

## Step 5: Verify

Run through each enforcement surface:

```bash
# 1. Task runner
task drift:check              # or make drift-check, npm run drift:check

# 2. CI composite task
task ci:changed               # drift:check should run first

# 3. Git hook (dry run)
lefthook run pre-push --dry-run   # or: cat .husky/pre-push

# 4. CI config present
grep -A 10 'spec-drift' .github/workflows/test.yml

# 5. Docs updated
grep -n 'drift' CLAUDE.md
```

## Detector Output Quality

If the detector output is unclear, improve it before wiring. Good output has:
- **STALE/OK/MISSING** labels (not vague "WARNING")
- **Fix:** instruction lines telling the developer what to do
- **Changed files:** section showing which files triggered the check
- A summary line with count: `N spec(s) need review. Update specs before merging.`

## Common Mistakes

| Mistake | Why it's wrong | Fix |
|---------|---------------|-----|
| Putting drift check in pre-commit | Detector needs git history; slows every commit | Use pre-push instead |
| Making CI job a dependency of lint/test | Adds to critical path | Run parallel, gate via branch protection |
| Using shallow clone in CI | `git log` comparisons fail | `fetch-depth: 0` |
| Putting drift:check last in CI tasks | Developers wait through slow lint+test | Put it first for fast feedback |
| Not documenting in CLAUDE.md | Future sessions don't know the gate exists | Update all 3-4 doc sections |
| Running detector through task runner in hooks | Adds task runner as hook dependency | Call script directly |
