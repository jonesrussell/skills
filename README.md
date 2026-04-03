# Skills

Personal [Agent Skills](https://agentskills.io) for use with Claude Code.

## Install

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

## Creating Skills

Use `template/SKILL.md` as a starting point. See the [Agent Skills spec](https://agentskills.io/specification) for details.
