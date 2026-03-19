---
name: triage-issues
description: Use when triaging GitHub issues, checking issue health, reviewing the backlog, or when SessionStart hooks report issue warnings. Triggers on "triage issues", "check issues", "issue health", "backlog review". Two tiers — Tier 1 runs lightweight checks at session start, Tier 2 runs full analysis on manual invocation.
---

# Triage Issues

A two-tier GitHub issue triage skill. Tier 1 produces quick warnings for session-start hooks. Tier 2 performs full backlog analysis with actionable recommendations requiring per-action approval.

## Tier Selection

- **Tier 1**: When invoked from a SessionStart hook or when the user asks for a quick issue check. Output warnings only, take no actions.
- **Tier 2**: When the user explicitly asks to triage issues, review the backlog, or invokes `/triage-issues`. Full analysis with action queue.

---

## Tier 1: Quick Check

Run these checks using `gh` CLI against the current repository. Output warning lines only.

### Data Gathering

```bash
gh issue list --state open --json number,title,body,updatedAt,milestone --limit 200
gh api repos/{owner}/{repo}/milestones --jq '.[] | {title, open_issues, state}'
```

### Checks

| Check | Condition | Output |
|-------|-----------|--------|
| Missing milestones | Open issue has no milestone | `WARNING: N issues missing milestones: #X, #Y` |
| Empty descriptions | Issue body is empty or under 20 characters | `WARNING: N issues have no description: #X` |
| Stale issues | No update in 14+ days | `WARNING: N stale issues (14+ days): #X, #Y` |
| Empty milestones | Open milestone with 0 open issues | `WARNING: Stale milestones (no open issues): name1, name2` |

### Output Format

```
=== Issue Triage ===
WARNING: 2 issues missing milestones: #42, #45
WARNING: 1 issue has no description: #45
WARNING: 3 stale issues (14+ days): #12, #18, #31
WARNING: Stale milestones (no open issues): v1.6 Voice Input
OK: 8 issues fully triaged
================
```

When all checks pass:

```
=== Issue Triage ===
OK: All 10 issues fully triaged
================
```

**Tier 1 rules:**
- No actions taken, warnings only
- Target execution under 5 seconds
- Output must be parseable by hooks (plain text, one warning per line)

---

## Tier 2: Full Triage

### Data Gathering

Same `gh` commands as Tier 1, plus fetch issue comments for staleness context:

```bash
gh issue list --state open --json number,title,body,labels,updatedAt,milestone,assignees --limit 200
gh api repos/{owner}/{repo}/milestones --jq '.[] | {title, number, open_issues, closed_issues, state, due_on}'
```

### Report Sections

Present the report using these sections:

**Milestone Health**
For each open milestone:
- Open / closed issue count and completion percentage
- Count of stale issues (14+ days)
- Age of oldest open issue
- Due date status (if set)

**Quality Gaps**
Issues failing the quality bar, grouped by failure type:
- No milestone assigned
- No description or description under 20 characters
- Stale (no activity 14+ days)
- No assignee (informational, not blocking)

**Potential Duplicates**
Flag issue pairs with significant title keyword overlap:
- Strip common words (the, a, an, for, to, in, of, and, or, is, it, as, at, by, on, with)
- Compare remaining significant words
- Flag pairs sharing 50%+ of significant title words
- Present as: `#X "title" <-> #Y "title" (N shared words)`

**Action Queue**
Propose actions based on findings. Present each action individually for approval.

### Action Approval Flow

Present one action at a time:

1. Describe the action and rationale
2. Wait for approval: **yes** (execute), **skip** (next action), **stop** (end queue)
3. Execute approved actions via `gh` CLI
4. Report result before moving to next action

Example actions:
- "Assign #45 to milestone vX.Y?" → `gh issue edit 45 --milestone "vX.Y"`
- "Close #12 as stale (no activity 45 days)?" → `gh issue close 12 -r "not planned" -c "Closing: no activity for 45 days. Reopen if still relevant."`
- "Comment on #31 requesting status update?" → `gh issue comment 31 -b "This issue has had no activity for N days. Is it still being worked on?"`
- "Close milestone vX.Y (no open issues)?" → `gh api -X PATCH repos/{owner}/{repo}/milestones/N -f state=closed`

### Quality Bar

| Check | Threshold | Tier 1 | Tier 2 |
|-------|-----------|--------|--------|
| Has milestone | Required | Warn | Offer to assign |
| Has description | >20 chars body | Warn | Offer to flag |
| Recent activity | <14 days since update | Warn | Offer to close/comment |
| Duplicate detection | 50%+ title word overlap | Skip | Flag pairs |
| Empty milestone | 0 open issues | Warn | Offer to close |

## Scope Boundaries

This skill does NOT:
- Auto-create issues
- Modify issue bodies (only adds comments)
- Manage labels
- Interact with PRs (separate concern)
- Take any action without per-action approval (Tier 2)
- Take any action at all in Tier 1 (warnings only)

## Dependencies

- `gh` CLI authenticated with repo access
- Repository has GitHub issues enabled
