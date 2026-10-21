---
name: ai-repository-audit
description: Audit any AI/code repository for drift from accepted structure, ownership, standards and preventive guards. Use for repeat health checks, post-cleanup reviews, or assessing whether ownership, retirement, documentation and safeguards still hold. Report findings and bounded remediation only; do not authorize or perform repairs unless explicitly requested.
---

# AI repository audit (general)

Determine whether subsequent work preserves the accepted repository structure and standards. Follow the project’s own policy docs (AGENTS.md, CONTRIBUTING.md, README, architecture docs, ADRs, or equivalent). An audit produces evidence and recommendations. It does **not** authorize repairs, deletion, environment changes, research runs, live sessions, or dispatching other workers. Perform fixes only when the user explicitly includes them in the request.

## 1. Establish the comparison

- Record the exact checkout, branch, HEAD commit, and working-tree state (clean / dirty / untracked) before any inspection.
- Honor any user-supplied baseline and scope.
- Otherwise locate the latest **accepted** cleanup, consolidation, or scoped audit from the project’s roadmap, maintenance plans, or acceptance records.
- Verify the baseline commit exists and is an ancestor. Do **not** silently substitute `main`, `origin/main`, or the newest feature commit.
- An audit that still has open findings is **not** a new clean baseline.
- If acceptance is ambiguous, state the provisional comparison and its limits clearly.

By default, inspect committed changes since the baseline, staged and unstaged changes, relevant untracked files, and the affected producer/consumer paths. A full audit expands only to currently supported surfaces; it does not traverse every sibling checkout or remote evidence store.

Explicitly distinguish:

- current HEAD
- dirty working-tree changes
- historical acceptance

If HEAD moves during the audit, record it and reconcile findings; never mix trees silently.

Group changes by **responsibility** (not just file extension) using git history and search. Inspect additions, deletions, renames, config, tests, docs, and guard exceptions. Trace current owners, callers, dynamic loaders, launch routes, and packaging for every changed boundary. A diff alone cannot prove retirement; a search with no hits cannot prove a path is unused. Report any areas left uninspected.

## 2. Inspect standards and enforcement

Read the applicable owning specs/ADRs and the current implementation **before** alleging a violation. Use the project’s documented ownership, retirement, documentation-governance, and integration-review rules as the criteria.

Review these dimensions wherever they intersect the scope:

- **Ownership & retirement**
  Competing implementations, restored retired routes, incomplete caller migration, meaningful responsibility boundaries, and supported compatibility exceptions. Distinct providers, independent oracles, and supported historical readers are **not** duplicates merely by resemblance.

- **Dependency & state boundaries**
  Product vs research/experiment separation, observations vs reconstructed/qualified state, resource ownership and side-effects. Follow indirect imports, configuration, and saved-format consumers—not just names.

- **Behavior & evidence**
  Validation, refusal/error propagation, lifecycle and recovery. Check whether tests reach the intended boundary with real producer shapes and independent positive/negative controls. A lower-level pass is not whole-journey proof.

- **Documentation & custody**
  Current owning docs and navigation, executable commands, stale competing instructions, and exact recovery routes for retained evidence. Do not copy bulk payloads just for an audit.

- **Prevention**
  Guard coverage and normal selection, changed baselines, suppressions/allowlists, bypasses, structural growth, and uncovered behavior. Size is a review signal, not an automatic defect. Check adopted limits and existing debt before claiming a regression.

Build a compact **guard matrix** from actual source and routing. For each relevant protection, classify it as:

| Status | Meaning |
|--------|---------|
| Implemented & selected | Runs in normal CI / check path |
| Implemented but unselected / bypassed | Exists but not exercised |
| Reviewer-enforced | Human process only |
| Planned | Documented but not yet real |
| Unknown | Could not determine |

Separately record execution outcome: observed pass/fail, reusable retained evidence, or not run. Inspect what each guard actually scans, its exclusions, valid/failing controls, and dynamic limits. The mere existence of a test or an unchanged test count is **not** proof that the control works.

## 3. Verify proportionately

- Reuse existing guards and retained receipts before proposing new tooling.
- Follow the project’s own interpreter, check-selection, host-lock, and evidence-reuse rules.
- Prefer dry-run / preview modes first.
- Run only bounded offline documentation, static, and named focused controls that answer the audit question.
- Inspect effects and dependencies before execution; an import or test may run product code.
- Missing prerequisites are a coverage limit, **not** permission to install packages or start research.
- State the exact commands, identities, omissions, and stopping point. Preserve failures.
- Do **not** refresh baselines, weaken checks, or rewrite evidence to make the audit pass.

## 4. Return a decision the owner can use

Lead with a clear verdict:

- New drift detected
- Only known / inherited debt
- No confirmed findings within the inspected scope
- Insufficient evidence

Then give prioritized findings that include:

- exact file / line or artifact reference
- the violated authority (doc, ADR, standard)
- concrete affected consumer / consequence
- supporting evidence

Separate:

- confirmed defects
- plausible concerns
- missing coverage

Label each item as:

- new regression
- inherited debt
- justified exception

Before calling something “new drift,” compare **both** the offending source **and** the applicable guard/contract at the accepted baseline. A failing check today does not prove when the violation began.

Recommend the **smallest** repair and verification, linking existing issue/plan owners where they exist. An audit does **not** automatically resume parked roadmap work.

Always include:

- baseline / HEAD / dirty-state scope
- the guard matrix
- material omissions

Report “no confirmed findings” when that is what the evidence supports. Never give a whole-repository clean bill from sampled paths or passing structural checks alone.

Use the response for a one-off audit. If a durable record is requested, update the existing owning report/issue or add one concise review with navigation. Do **not** create a second backlog, archive, or audit framework.
