# Skills

Personal [Agent Skills](https://agentskills.io) for coding, content and workflow tasks across compatible agents.

## Tutorial starting points

- [Laravel SDD Bootstrap](skills/laravel-sdd-bootstrap/SKILL.md): prepare a Laravel foundation with standalone PHP/Composer, `php artisan serve`, Blade and SQLite. Herd and richer stacks are explicit options. Recording mode leaves the feature for you to build on camera.

Example request with the skill installed:

```text
Use $laravel-sdd-bootstrap to prepare a Laravel project for a feedback-form tutorial. Set up the runtime, database and simple page styling. Leave the form, validation and saving logic for me to build on camera.
```

To install only this skill, copy the entire `skills/laravel-sdd-bootstrap` folder, including its references and agent metadata, into your agent's personal skills directory. For Codex the default is `~/.codex/skills`; for Claude Code it is `~/.claude/skills`. Review an existing copy before replacing it. The repository-wide sync below installs the full collection.

Tutorial descriptions can link directly to the skill above. For an episode tied to a particular revision, use GitHub's commit permalink so later edits do not change that lesson's instructions.

## Canonical Repo

This repository's `skills/` directory is the source of truth for custom skills across agents, wherever you clone it.

- Author skills only in `skills/*`.
- Treat Claude/Codex/Cursor install directories as mirrors.
- Use `scripts/manage_skills.py` to audit and sync local installs.

## Local Agent Setup

Audit local installs:

```bash
python3 scripts/manage_skills.py audit
```

Sync canonical skills into Codex, Claude, and Cursor:

```bash
python3 scripts/manage_skills.py sync
```

Sync a subset of targets:

```bash
python3 scripts/manage_skills.py sync --targets codex cursor
```

Notes:

- Codex installs custom skills into `~/.codex/skills` and leaves built-in skills alone.
- Cursor installs custom skills into `~/.cursor/skills`. Do not edit `~/.cursor/skills-cursor`; that directory is Cursor-managed.
- Claude Code mirrors `skills/`, `README.md`, and `.claude-plugin/marketplace.json` into the installed marketplace checkout at `~/.claude/plugins/marketplaces/jonesrussell-skills`.

## Skill Evaluation Harness

You use the local eval harness to smoke-test writing skills before you change prompts, fixtures, or docs. The harness is stdlib-only. It stores versioned eval inputs and accepted baselines under [`evals/`](evals/README.md), and the default mock runner reads deterministic outputs from `tests/fixtures/evals/mock_outputs.json`.

Run a local smoke test:

```bash
python3 scripts/eval_skills.py run --suite writing --runner mock --output-dir evals/results/local-smoke
```

This writes `run.json` and `summary.md` into `evals/results/local-smoke/`. Use that output when you want a quick check without hitting a live runner.

Run a real single-case smoke test against the local Codex CLI:

```bash
python3 scripts/eval_skills.py run --suite writing --runner codex --skill technical-writing --case-id doc_page_happy_path --output-dir evals/results/codex-smoke
```

That path reads the real skill file, runs the fixture prompt through `codex exec`, and then applies the deterministic hard-rule checks before writing the run artifact.

Compare a candidate run to a baseline:

```bash
python3 scripts/eval_skills.py compare --baseline evals/baselines/writing/v1/run.json --candidate evals/results/local-smoke/run.json
```

You promote a candidate only after you review the run and want to preserve it as the next baseline. The baseline copy keeps the full run directory together so future comparisons stay reproducible.

Promote a reviewed candidate run into the baseline tree:

```bash
python3 scripts/eval_skills.py promote-baseline --candidate evals/results/local-smoke --baseline evals/baselines/writing/v1
```

Runner expectations:

- `mock` reads `tests/fixtures/evals/mock_outputs.json`.
- `codex` runs the real skill prompt through the local `codex exec` CLI in read-only mode.
- `command` runs one external command per case and expects JSON on stdout.
- Both runners record run metadata so you can compare outputs against a named baseline later.

Verification note:

- The documented smoke commands above exercise the `mock` runner path.
- The `codex` runner path requires a working local Codex CLI login. Use `--skill` and `--case-id` to keep live runs small and cheap.
- The generic `command` runner path is still available for other executors and is covered by the unit test suite.

## Claude Code Marketplace

Register as a plugin marketplace in Claude Code:

```
/plugin marketplace add jonesrussell/skills
```

Then install a plugin bundle:

```
/plugin install blog-skills@jonesrussell-skills
/plugin install code-quality-skills@jonesrussell-skills
/plugin install waaseyaa-skills@jonesrussell-skills
/plugin install workflow-skills@jonesrussell-skills
/plugin install planning-skills@jonesrussell-skills
```

## Plugin Bundles

### blog-skills
Blog and review writing skills.
- `blog-writing` — Create new blog posts for Hugo blogs
- `blog-reviewing` — Review and audit blog posts against standards
- `film-review` — Write movie reviews for movies-of-war.com
- `session-to-blog` — Generate Hugo draft posts from Claude Code sessions
- `social-media-posts` — Create platform-specific promotion copy
- `substack-writing` — Write Substack newsletter issues for the "Ahnii!" publication
- `technical-writing` — Non-blog content: docs, READMEs, guides, site copy

### code-quality-skills
Code quality, architecture, and security review skills.
- [`ai-repository-audit`](skills/ai-repository-audit/SKILL.md) — Audit repository drift against an accepted baseline, with evidence and bounded recommendations
- `cleaning-up-codebases` — Review codebases for cruft, dead code, anti-patterns
- `codified-context` — Apply three-tier codified context architecture
- `monorepo-cleanup` — Review monorepos for cross-service issues
- `security-review` — Audit services for security vulnerabilities
- `updating-codified-context` — Update existing codified context when specs drift

### waaseyaa-skills
Waaseyaa framework development and deployment.
- `laravel-to-waaseyaa` — Migrate Laravel features to Waaseyaa packages
- `waaseyaa-planning` — Plan and orchestrate Waaseyaa framework tasks
- `waaseyaa-site-deploy` — Create and deploy Waaseyaa sites to production

### workflow-skills
Development workflow utilities.
- `changelog` — Maintain Keep a Changelog format changelogs and releases
- `documenting-session-findings` — Capture session findings before moving on
- `optimizing-responsive-images` — Responsive image sizing, format conversion, srcset
- `spec-observability-wiring` — Wire drift-detector scripts into enforcement surfaces
- `triage-issues` — Triage GitHub issues and review backlogs

### planning-skills
Project planning and orchestration.
- `claudriel-planning` — Plan and orchestrate Claudriel AI pipeline tasks
- `copilot-claudriel` — Orchestrate Claudriel tasks via GitHub Copilot
- `minoo-planning` — Plan and orchestrate Minoo platform tasks

## Related Skill Repos

MyMe and North-Cloud skills live in their own repos:
- **myme-skills** — [jonesrussell/myme](https://github.com/jonesrussell/myme) (Rust/Qt desktop app)
- **north-cloud-skills** — [jonesrussell/north-cloud](https://github.com/jonesrussell/north-cloud) (Go microservices)

## Repository Audits

Use [`ai-repository-audit`](skills/ai-repository-audit/SKILL.md) for repeat health checks or post-cleanup reviews against an accepted baseline. It checks ownership, retirement, documentation, and safeguards, then reports evidence and bounded recommendations. Repairs require an explicit request.

For an agent with the skill available:

```text
Use $ai-repository-audit against this project, using the latest accepted cleanup as the baseline. Focus on ownership and retirement.
```

Or provide a known baseline commit and narrower paths:

```text
Use $ai-repository-audit with baseline <commit>, scoped to src/ and tests/. Report findings without making repairs.
```

The report identifies the baseline and current checkout, classifies guard coverage and execution results, and distinguishes new drift from inherited debt and missing evidence. If the accepted baseline is unclear, it states the limits of the comparison.

## Creating Skills

Use `template/SKILL.md` as a starting point. See the [Agent Skills spec](https://agentskills.io/specification) for details.
