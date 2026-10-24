# Skill catalog

Generated from `catalog.json` with `python scripts/catalog.py generate`.

Start with [the tutorial guide](tutorials.md). **Maintained** means reviewed for the documented scope; it does not promise every agent runtime or model has been tested. Removed workflows are listed in [the retirement index](retired.md), outside the installable tree.

## Maintained (5)

| Skill | Category | Purpose |
| --- | --- | --- |
| [ai-repository-audit](../skills/ai-repository-audit/SKILL.md) | repository | Compare a repository with its accepted baseline and report evidence-backed drift. |
| [archive-readiness](../skills/archive-readiness/SKILL.md) | repository | Check whether requested work is complete and identify unfinished items before archiving a chat. |
| [laravel-sdd-bootstrap](../skills/laravel-sdd-bootstrap/SKILL.md) | tutorial | Prepare standalone PHP/Composer, Blade and SQLite, leaving the teaching feature for the recording. |
| [project-kickoff](../skills/project-kickoff/SKILL.md) | tutorial | Create a portable brief, plan, backlog, decisions and agent guidance without overwriting a project. |
| [sdd-stage-planner](../skills/sdd-stage-planner/SKILL.md) | tutorial | Refine the next feature and its file plan before implementation, with a readable planning companion. |

## Requirements and evidence

### ai-repository-audit

Access to the scoped repository, Git history and its accepted baseline. Run only project checks already available and authorized.

Retains the October 21 skill from 8e31ef1. Baseline, evidence and read-only boundaries reviewed. No new model benchmark or certification of a target repository is claimed.

[Behavior cases](../skills/ai-repository-audit/evals/evals.json) are inputs for evaluation, not recorded model results.

### archive-readiness

Current task context and read-only tools for the systems already in scope. No mandatory external service.

Imported from the maintainer local skill. Read-only current-task scope reviewed. No new model benchmark or product-specific integration test claimed.

[Behavior cases](../skills/archive-readiness/evals/evals.json) are inputs for evaluation, not recorded model results.

### laravel-sdd-bootstrap

PHP and Composer compatible with the selected Laravel release. Browser and editor are optional. No Herd, Node, Docker or MCP requirement for a plain Blade/public-CSS starter.

Derived from an actual native Windows Laravel recording setup using PHP 8.5.5, Composer 2.9.5 and Laravel 13.38.0. Starter tests, formatting, migrations and HTTP/assets were checked. The lesson feature was intentionally unbuilt. Other hosts and model comparisons are not benchmarked.

[Behavior cases](../skills/laravel-sdd-bootstrap/evals/evals.json) are inputs for evaluation, not recorded model results.

### project-kickoff

Filesystem access; Python 3.11+ only when using the bundled scaffold helper. No network or service account required.

Imported from the maintainer local skill updated October 23. Templates and create-only helper reviewed; helper behavior tests are included in CI. Model trigger and output comparisons have not been run.

[Behavior cases](../skills/project-kickoff/evals/evals.json) are inputs for evaluation, not recorded model results.

### sdd-stage-planner

An existing project with source and planning context. Browser inspection is useful for a visual planner; no required MCP service.

Imported from the maintainer local skill. Private/example-specific wording removed; instruction and resource review completed. No fresh cross-model or client-rendering benchmark claimed.

[Behavior cases](../skills/sdd-stage-planner/evals/evals.json) are inputs for evaluation, not recorded model results.

## Bundles

Each marketplace entry lists its exact skill directories. Installing a bundle does not install the entire collection.

- **tutorial-skills** (maintained): `laravel-sdd-bootstrap`, `project-kickoff`, `sdd-stage-planner`
- **repository-skills** (maintained): `ai-repository-audit`, `archive-readiness`
