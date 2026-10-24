# Skills repository research and direction

Reviewed 2026-10-24. This is a repository decision record, not a claim that every agent host or model has been benchmarked.

## Recommendation

Maintain a small public collection of reusable workflows demonstrated in real work. Lead with tutorial installation. Keep each skill self-contained, keep its name and path stable, and put audience categories in the catalog rather than nesting folders several levels deep.

The first collection has five skills: `laravel-sdd-bootstrap`, `project-kickoff`, `sdd-stage-planner`, `ai-repository-audit`, and `archive-readiness`. The audit skill was added on October 21; it is retained. The project kickoff skill was updated locally on October 23 and is being brought into the public collection with its templates and helper.

Remove the other 60 historical skills from the installable tree. Their content remains recoverable at commit `c65924b9c8e0fbdf3a5a738106cad244c2a4630d`. Removal means they are unsupported in this collection. It does not mean their underlying topics are useless or that another repository's implementation is obsolete. [The retirement index](retired.md) records each disposition.

## What current guidance changes

| Finding | Application here |
| --- | --- |
| Skills should encode knowledge and procedures gained from real tasks, rather than generic instructions a capable agent already knows. | Admit new skills after an actual workflow demonstrates their value. The Laravel recording setup is the first tutorial example. |
| A skill should form one coherent unit; conditional details belong in supporting references. | Keep one stable `skills/<name>/SKILL.md` entrypoint. Put substantial stack variants in references, not a universal setup checklist. |
| Names and descriptions determine discovery. | Test related requests that should and should not activate a skill. Avoid catchall names such as `research` or `feedback` for narrow proprietary workflows. |
| A successful structure check does not demonstrate useful model behavior. | Separate packaging checks, helper tests, real workflow evidence, and model evaluations. |

These conclusions follow the [Agent Skills creator guidance](https://agentskills.io/skill-creation/best-practices) and [description evaluation guidance](https://agentskills.io/skill-creation/optimizing-descriptions). The recommended size ceiling is a prompt to simplify, not a target to fill.

The portable format requires a `SKILL.md` with a matching lowercase name and a description. Scripts, references and assets are optional. Environment requirements can be expressed in `compatibility`. Keep host-specific metadata separate where possible. [Agent Skills specification](https://agentskills.io/specification).

## Should tools ship with skills?

Yes, when the workflow needs them. Use the smallest appropriate mechanism:

| Need | Location and responsibility | Example |
| --- | --- | --- |
| Reasoning, sequence, decisions and output expectations | `SKILL.md` and selected `references/` | Prepare a Laravel lesson without implementing the feature before recording. |
| Repeatable local transformation or scaffold | Skill-local `scripts/`, with tests and documented inputs | Project kickoff's create-only scaffold helper. |
| Files copied into the result | Skill-local `assets/` | Project brief and backlog templates. |
| Existing reliable command | Document the required CLI and how to detect it | PHP, Composer and Artisan; no wrapper needed merely to repeat their commands. |
| Live authenticated service or capability shared by several workflows | Existing connector first; otherwise a separately maintained MCP service | Publishing queue inspection or posting, if later justified. |
| Installable group containing skills and service dependencies | Host plugin package with explicit members | A future publishing plugin after its service contract and ownership are stable. |

Skill-local scripts should have noninteractive inputs, useful `--help`, clear failures and machine-readable results when another tool consumes them. Declare runtime and dependency versions; use lockfiles where dependencies need reproducibility. Test create/update/refusal behavior in temporary directories. [Agent Skills script guidance](https://agentskills.io/skill-creation/using-scripts).

MCP provides tools and data; skills describe the workflow around them. That distinction supports a skill-only repository today. A new MCP server is unnecessary for PHP scaffolding, planning, or read-only repository audits. [OpenAI skill and MCP guidance](https://developers.openai.com/plugins/concepts/skills).

If a shared service is introduced, give it an explicit input/output contract, authentication boundary, observable errors and tests for uncertain or repeated mutations. Tool descriptions are not an authorization system. [MCP tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

Do not put credentials, account IDs or private vault paths in the package. The current blog repository already owns publishing, queue state, delivery receipts and retry behavior. Building a second publisher here would create competing ownership.

## Installation and distribution

Use the standard skill layout so viewers can install one skill without this repository's development tooling. Vercel's open `skills` CLI supports individual skill and agent selection; it requires Node.js 22.20 or later at this review date. It is an optional third-party installer, not a Laravel runtime requirement. [CLI README](https://github.com/vercel-labs/skills), [command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

Also provide a Python copy installer for viewers who already have Git and Python. Its useful distinction is preserving modified installations, backing up explicitly replaced copies, and never pruning unrelated skills. Avoid silent bulk synchronization.

Current OpenAI documentation identifies `~/.agents/skills` and repository `.agents/skills` as Codex discovery locations. This recording PC also has skills under the older `.codex/skills` layout. Use the current documented path for new public installs and an explicit compatibility target for existing installations. Do not automatically migrate or duplicate a user's skills. `agents/openai.yaml` can carry presentation and tool-dependency metadata. [OpenAI skills documentation](https://learn.chatgpt.com/docs/build-skills).

Claude Code supports personal `.claude/skills` directories and plugin distribution. For this repository's marketplace entries with `source: "./"`, explicit skill subdirectory arrays select the bundle's exact contents. Retain only the tutorial and repository bundles. Existing users may still have copies of removed plugins; repository removal does not prove local uninstallation. [Claude skills documentation](https://code.claude.com/docs/en/skills), [marketplace loading rules](https://code.claude.com/docs/en/plugins-reference#marketplace-entries-and-the-manifest).

OpenAI now also documents a portable root `plugin.json` format with optional MCP configuration and compatibility overlays. Keep that as a future distribution adapter; do not claim an untested universal plugin or submit to a public directory during this cleanup. [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).

For video descriptions, publish an immutable commit link as well as the current guide. A viewer should be able to reproduce the filmed version after the skill evolves. Avoid branches or auto-updates as the only record of a tutorial's dependencies.

The maintainer chose MIT licensing for the maintained original skills and helpers on October 24. Carry a license notice inside each independently installable skill. Historical removed material remains subject to its own provenance and terms.

## What the repository evidence says

- `social-media-posts` contains uncited numerical reach claims and mandatory link-in-comment rules. It excludes Bluesky, while the current blog runbook requires Bluesky, LinkedIn and Facebook with canonical URLs in each post. Remove this conflicting instruction source.
- `content-pipeline` refers to a missing queue-status helper and superseded local vault usage. Current publishing is owned by the blog repository's `docs/local-content-autopilot.md` and `docs/buffer-posting.md`. Do not revive the historical shell scripts.
- Claudia memory and personal-assistant skills depend on an unshipped memory service, personal file layout, or agent dispatcher. They do not form a self-contained public tutorial package.
- Claudriel, Minoo and Waaseyaa skills mix project architecture, fixed paths, deployment assumptions and orchestration. Their current owners should be their project repositories. This review does not certify those projects' present behavior.
- Generic cleanup, writing and research checklists need demonstrated incremental value before reintroduction. Existing architecture rules should not be imposed on every project.
- The old writing evaluation program includes mocks and captured Codex runs. Its [April 12 `real-full-v5` baseline](https://github.com/jonesrussell/skills/blob/c65924b9c8e0fbdf3a5a738106cad244c2a4630d/evals/baselines/writing/real-full-v5/run.json) reports 19 passes, but a review case passes despite having no draft to review and another uses placeholder line numbers. That exposes a grading limitation, not proof that all historical writing work failed. Preserve the program and captures in Git; use artifact-grounded cases for the current five skills.

Evidence scope: Git history, all historical skill entrypoints through inventory and dependency review, focused body review of retained and conflicting workflows, local imported skill resources, and the current blog runbooks. No historical publisher, deployment or memory mutation was executed.

## Quality gate and growth

For every skill, record its purpose, prerequisites, source of expertise, reviewed date and verification limits. Add a few realistic evaluation cases, including a boundary case. Run the same task with and without the skill, or against its previous version, in isolated workspaces. Grade observable results and inspect failures; count latency and token cost only alongside quality. A mock success is not a model benchmark. [Agent Skills output evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills).

Implementation order:

1. Curate the five-skill collection, retirement record, selective installation, explicit bundles, and Windows/Linux structural and helper checks.
2. Rehearse the Laravel video and record the actual skill commit, installed stack, starting checkpoint and demonstrated acceptance checks. Use that experience to improve the skill.
3. Add a Drupal tutorial skill only after a concrete recorded workflow establishes its useful defaults. Develop a tutorial-promotion skill from the current content pipeline, without duplicating publication code.
4. Add a shared tool only after multiple maintained workflows need the same capability and a clear owner can maintain its contract.
5. Add plugin distribution adapters when they solve a real installation need and can be tested in their target clients.

No skill count target, mandatory MCP server, giant framework, or prebuilt empty category tree is needed. The catalog and contribution rules provide room to grow while the installed surface stays small.
