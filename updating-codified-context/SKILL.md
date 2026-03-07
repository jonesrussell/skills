---
name: updating-codified-context
description: Use when a repo has codified context already initialized (CLAUDE.md with orchestration table, docs/specs/ directory, drift-detector) and sessions have revealed stale specs, missing service docs, architecture drift, new subsystems without coverage, or MCP tools not wired.
---

# Updating Codified Context

## Overview

Systematic maintenance of an initialized codified-context repo. Fills gaps by tier (T1 → T2 → T3), verifies with drift-detector, and wires the self-trigger so future sessions auto-load this skill.

**Requires initialized state.** If CLAUDE.md lacks an orchestration table or `docs/specs/` doesn't exist, use `codified-context` skill instead.

## Baseline Failure Modes (Why This Skill Exists)

Without this skill, agents naturally:
1. **Skip creating new spec files** — map new services onto existing specs instead
2. **Miss MCP wiring** — don't check `.claude/settings.local.json` for spec-retrieval tools
3. **Miss self-trigger** — don't add the orchestration table row that auto-loads this skill
4. **Work ad-hoc** — no tier ordering, miss downstream dependencies
5. **Skip verification** — don't re-run drift-detector after changes

## Detect Initialized State

Check before starting:
- `CLAUDE.md` exists with an orchestration table (file pattern → service context → spec)
- `docs/specs/` directory exists with at least one spec file
- `tools/drift-detector.sh` or equivalent exists

If NOT initialized → use `codified-context` skill instead.

## Step 1: Audit (Identify Scope)

Run drift-detector first to establish baseline:
```bash
bash tools/drift-detector.sh 10
```

Then produce a priority table:

| Service | CLAUDE.md | Spec | Drift-detector pattern | MCP wired |
|---------|-----------|------|------------------------|-----------|
| rfp-ingestor | missing | missing | missing | n/a |
| social-publisher | missing | missing | missing | n/a |

Check MCP wiring:
```bash
cat .claude/settings.local.json   # look for spec-retrieval tool entries
cat .claude/mcp.json 2>/dev/null  # look for spec-retrieval server
```

## Step 2: Update by Tier (T1 → T2 → T3)

### T1: Service CLAUDE.mds + Root Orchestration Table

For each service missing a CLAUDE.md, read the source first:
- `main.go` — bootstrap pattern, ports, top-level flow
- `internal/config/config.go` — env vars and defaults
- Key domain files — understand what the service actually does

Write `{service}/CLAUDE.md` following the established pattern in other service CLAUDE.mds.

**After all service CLAUDE.mds are written**, add the self-trigger row to the root CLAUDE.md orchestration table:
```
| docs/specs/**, .claude/**, **/CLAUDE.md | updating-codified-context | — |
```
This causes any session touching context files to auto-load this skill.

### T2: Project Skills

Write or update project-specific skills only if:
- Domain knowledge has materially shifted (new pipeline layer, new platform adapter, etc.)
- Existing skill descriptions no longer match triggering conditions

Skip if no domain knowledge changed.

### T3: Specs + Drift-Detector + MCP

**Create new spec files** for each uncovered service — do NOT reuse existing specs for unrelated services.

Spec file template (`docs/specs/{service}.md`):
```markdown
# {Service} Spec
## File Map
## Interface / API
## Data Flow
## Config Vars
## ES Index / DB Schema (if applicable)
## Known Constraints
```

**Update drift-detector**: Add `["{service}/"]="docs/specs/{service}.md"` entries to `PATTERN_TO_SPEC`. Map each service to its own spec file.

**Wire MCP** if spec-retrieval server exists but tools aren't in `settings.local.json`:
- Add `list_specs`, `get_spec`, `search_specs` to the `permissions.allow` list
- Add the server to `enabledMcpjsonServers`

## Step 3: Verify

```bash
bash tools/drift-detector.sh 10
```

Expected: exit 0 with no MISSING or WARNING lines for newly covered services.

If spec-retrieval MCP is wired, verify:
```bash
# call search_specs with a term from the new spec
```

## Step 4: Commit

One commit per logical unit:
```
chore(context): update codified context — <summary>
```

Example: `chore(context): fill codified context gaps — rfp-ingestor, social-publisher, MCP wiring, self-trigger`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Mapping new service to existing spec in drift-detector | Create `docs/specs/{service}.md` for each new service |
| Writing CLAUDE.md from task description alone | Read the actual source code first — configs reveal env vars, mapping reveals ES constraints |
| Forgetting self-trigger row in orchestration table | Add `docs/specs/**, .claude/**, **/CLAUDE.md → updating-codified-context` row |
| Skipping MCP wiring check | Always check `.claude/settings.local.json` for spec-retrieval tools |
| Not running drift-detector before AND after | Run before to establish baseline, after to verify no regressions |
