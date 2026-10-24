# Russell's skills

Practical agent skills for building tutorial projects, planning the next feature, and reviewing repository work. Start with the Laravel recording skill.

## Start here

| You want to | Skill |
| --- | --- |
| Prepare a Laravel tutorial or project foundation | [laravel-sdd-bootstrap](skills/laravel-sdd-bootstrap/SKILL.md) |
| Give a new project a useful brief, plan and backlog | [project-kickoff](skills/project-kickoff/SKILL.md) |
| Refine the next product stage and proposed PR | [sdd-stage-planner](skills/sdd-stage-planner/SKILL.md) |
| Check repository drift against an accepted baseline | [ai-repository-audit](skills/ai-repository-audit/SKILL.md) |
| Check whether a chat is ready to archive | [archive-readiness](skills/archive-readiness/SKILL.md) |

The Laravel default is standalone PHP and Composer, Artisan's local server, Blade and SQLite. Herd is opt-in. Recording mode leaves the lesson's feature for you to build on camera.

## Install one skill

With Node.js 22.20+ and the optional [skills CLI](https://github.com/vercel-labs/skills), run from your tutorial project:

```sh
npx skills add jonesrussell/skills --skill laravel-sdd-bootstrap -a codex
```

Select the target agent and installation scope in the CLI. Use `-a claude-code` for Claude Code. This installs instructions and supporting files; it does not install PHP or build the feature.

With Git and Python 3.11+, use the repository's selective copy installer:

```sh
git clone https://github.com/jonesrussell/skills.git
cd skills
python scripts/manage_skills.py install laravel-sdd-bootstrap --target codex --dry-run
python scripts/manage_skills.py install laravel-sdd-bootstrap --target codex
```

This route defaults to a personal install. Preview first, then install when the destination is right. Read [installation and updates](docs/install.md) for project-local destinations, existing installations, backups and Claude bundles.

## Use it

```text
Use $laravel-sdd-bootstrap to prepare a feedback-form tutorial.
Use standalone PHP and Composer. Leave the form, validation and saving
for me to build on camera. Keep the setup small.
```

In Codex CLI or IDE, use the skill selector or `$skill-name`. In another agent, invoke the installed skill using that host's interface. See the [tutorial guide](docs/tutorials.md) for the recording workflow and versioned links.

## Maintain and grow

- [Catalog and bundles](docs/catalog.md)
- [Current research and repository direction](docs/research-2026-10.md)
- [Contribution, tools and verification rules](docs/maintenance.md)
- [Retired skills and recovery links](docs/retired.md)
- [Changes](CHANGELOG.md)

The 2026 cleanup preserves Git history and removes unsupported workflows from installation. Project deployment and publishing instructions belong with their owning projects. No local installed skills are removed by updating this repository.

Structural and helper tests are automated. The catalog states the evidence available for each skill; it does not claim every model or agent host has been benchmarked.

The maintained skills, helpers and documentation are [MIT licensed](LICENSE). Each independently installable skill includes the license notice.
