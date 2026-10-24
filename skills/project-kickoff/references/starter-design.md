# Starter design and alternatives

Research checked 2026-10-23 against primary documentation. Recommendations are design judgments, not requirements imposed by these tools.

## Why this starter is small

The skill assembles context; templates provide editable artifacts; the helper makes creation repeatable. Seven files and an origin manifest are enough for an early project. The helper is create-only. It does not merge later template changes into personalized projects.

AGENTS.md contains instructions and links. The brief owns intent; the plan owns sequencing; the backlog owns task status; decisions preserve rationale. Do not maintain the same task board in multiple places. Existing workflows win over default filenames.

## Existing tools

| Approach | Useful capability | When to adopt |
| --- | --- | --- |
| [AGENTS.md](https://agents.md/) and [Codex guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Conventional Markdown instructions, with Codex global and nested project guidance. | Use concise project guidance immediately. Keep user-wide preferences in existing global guidance rather than copying machine paths into every starter. |
| [GitHub Spec Kit](https://github.com/github/spec-kit) | Structured specification, planning, task and implementation workflows, reusable templates and optional extensions. | Consider for a coordinated specification workflow. Select a process; do not install every extension by default. |
| [OpenSpec](https://openspec.dev/docs/quickstart) | Change-focused proposals, requirements, optional design notes and tasks, followed by specification reconciliation. | Useful for bounded product changes and durable behavior specifications. Avoid a competing task tracker. |
| [Copier](https://copier.readthedocs.io/en/stable/updating/) | Versioned templates and updates that reconcile template changes with generated projects. | Adopt when distributing template updates matters across several repositories. Version the template and review conflicts. |
| [Codex skills](https://learn.chatgpt.com/docs/build-skills) | Reusable instructions with optional scripts, assets and references. | Use for the kickoff procedure; keep product facts in each project. |

This personal starter implements the required local file-creation workflow. Reassess Copier when a second template release needs to update several personalized projects.

## Extensions only when needed

- Feature specs/contracts once behavior is understood.
- Separate architecture decisions when alternatives need substantial explanation.
- GitHub issue forms or a Linear/Jira board when that service becomes authoritative.
- Stack-specific build/test guidance after commands are verified.
- Release/operations runbooks when deployment is planned.
- A visual planner when it helps review scope, aligned with canonical records.

Do not install global defaults across unrelated projects as a side effect of one kickoff. Existing credential-location and communication preferences stay outside this portable template.
