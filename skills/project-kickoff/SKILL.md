---
name: project-kickoff
license: MIT
description: Set up a new or revived project's working folder with concise AGENTS.md guidance, a product brief, an actionable backlog, a plan and a decision log. Use for project kickoff or a reusable project-management scaffold; preserve existing repositories and their workflows.
---

# Project Kickoff

Create enough durable context for another session to continue without reconstructing project history. Adapt the starter; it is not an application generator or a mandatory development framework.

## Establish the workspace

- Honor the requested path. Inspect ancestor/project instructions, existing files and Git state. Use existing documents or issue trackers when they already own the same information.
- Recover purpose, audience, decisions, stage and source locations from conversation and evidence. Label unknowns and proposals. A planning request does not authorize application implementation or deployment.
- For a revival, record the archive and remote separately. Do not initialize unrelated Git history over an existing project identity. Reuse its repository when source recovery is selected; a planning-only folder can remain unversioned meanwhile.
- Use the supplied user-local date. Resolve routine naming/layout choices without a questionnaire.

## Apply the starter when useful

The standard-library helper copies seven templates from `assets/project/` and records origin in `.project/kickoff.json`. It never overwrites existing files, changes global instructions, creates Git history, installs packages, or calls services.

Create temporary JSON input in the task's scratch directory:

```json
{
  "name": "Example Project",
  "slug": "example-project",
  "owner": "Project owner",
  "date": "2026-10-23",
  "purpose": "The concrete outcome this project exists to deliver.",
  "stage": "Discovery",
  "prefix": "EX"
}
```

Use a real current date and confirmed details. Run with Python 3.11+:

```text
python scripts/scaffold_project.py preview --destination ABSOLUTE_PATH --config INPUT_JSON
python scripts/scaffold_project.py apply --destination ABSOLUTE_PATH --config INPUT_JSON
python scripts/scaffold_project.py check --destination ABSOLUTE_PATH
```

Resolve the script relative to this skill. Preview is inspection, not a request for fresh permission when creation is authorized. Review KEEP results and adapt existing files manually. The helper is create-only, not an upgrade/merge engine. See [starter design and alternatives](references/starter-design.md) when choosing a different system or planning template upgrades.

## Turn the scaffold into a project

- `README.md`: human orientation and links; no duplicate task board.
- `AGENTS.md`: short guidance, document authority, verified commands and project constraints. Link detailed plans. Keep machine settings out of portable defaults.
- `docs/brief.md`: problem, audience, outcome, scope and uncertain assumptions.
- `docs/plan.md`: current stage, next slice, exit evidence and later boundaries.
- `docs/backlog.md`: one work queue with stable IDs, priority, state, dependencies and observable acceptance. If GitHub/Linear/Jira owns tasks, link there instead of duplicating states.
- `docs/decisions.md`: consequential decisions with date, status, rationale and effects. Preserve superseded decisions.
- `.gitignore`: merge existing conventions. Inspect scope before excluding real project assets.

Replace starter text with confirmed context and a small useful backlog. Preserve Proposed / Agreed / Open distinctions. Ready means well-defined, not automatically authorized. Done requires evidence relevant to the task, not generated files or a formatter alone.

If a visual stage planner exists, place its maintained copy in project docs, link canonical documents and mark any old copy as a snapshot. Use the available stage-planning workflow for substantial revisions. Do not create an HTML planner for every kickoff by default.

Keep this skill generic. Product facts and stack rules belong in projects. Add specifications, ADR files, issue forms, CI or a PM service only when needed.

## Validate and hand off

Run `check`, inspect guidance for false claims and conflicting authority, and verify the next task has acceptance criteria. If the helper changes, run `python scripts/test_scaffold.py` from a scratch directory. Report the project path, next step, skill invocation and actual limitations. Installing files does not prove a running agent has reloaded them.
