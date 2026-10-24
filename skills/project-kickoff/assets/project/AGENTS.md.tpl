# Working on {{NAME}}

## Start here

Read [README.md](README.md), [the brief](docs/brief.md), [the current plan](docs/plan.md) and the relevant item in [the backlog](docs/backlog.md). Read applicable [decisions](docs/decisions.md) before changing scope or architecture.

## Document authority

- Brief: product intent and scope.
- Plan: current stage, next slice and milestone boundaries.
- Backlog: canonical work-item status and acceptance evidence.
- Decisions: what was agreed, proposed, rejected or superseded and why.
- Specifications/contracts, when added: intended behavior for their bounded feature.
- A visual planner is a readable companion; it does not override these records.

Keep affected records consistent when the user changes direction. Resolve contradictions using the current user instruction and evidence; do not silently turn proposals into requirements.

## Working agreements

- Continue authorized work. A planning-only task does not authorize application implementation, production changes or external publication. Existing authorization remains valid within its scope.
- Use stable backlog IDs when reporting meaningful work. Update the relevant item's state, evidence and next step before handoff; do not create duplicate trackers.
- Preserve unrelated work. Inspect repository state and conventions before editing or initializing tools.
- Use the established stack. Record consequential changes in the decision log; add layers or dependencies only for a concrete need.
- Verify observable outcomes with checks appropriate to the change. Record what ran, what passed and what remains unverified.
- Explain non-obvious constraints and decisions close to handwritten code. Keep comments aligned with behavior.
- Keep credentials and private data out of source, fixtures, logs and planning artifacts. Use configured access and the user's credential-location guidance when applicable.

## Commands and implementation conventions

No application runtime or verified build/test commands are established by this starter. Inspect the actual project before adding commands here. Do not invent working checks or a chosen framework.
