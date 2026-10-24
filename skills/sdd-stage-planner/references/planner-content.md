# Stage planner content

Adapt the layout to the stage; these are information requirements, not a fixed collection of cards.

## Reading hierarchy

At the top, show the stage name and status, the outcome in user language, current slice, next decision and explicit scope boundary. Below that, summarize:

- User journey: the main path and important alternate/error paths.
- Scope: what this stage delivers and what waits for later milestones.
- Data: proposed fields, relationships and constraints explained plainly.
- Permissions: a compact guest/owner/other-user matrix where relevant.
- Behavior: validation, lifecycle transitions, visibility and failure/recovery rules.
- Interfaces: readable operation summaries, authentication and important error behavior. Link the full contract rather than displaying raw schemas.
- Decisions: Proposed/Agreed/Open, with consequences and the slice that depends on them.
- Acceptance: concrete examples of observable success and failure tied to canonical criterion IDs.
- PR forecast: reviewable slices with paths, change type and purpose.
- Evidence: checks actually performed, limitations and source document links.

Do not assume every product needs authentication, public publishing, media or an API. Include only relevant sections and requirements.

## PR forecast presentation

Show an indented folder tree or a path table that remains readable on narrow screens. Use change badges and short purpose descriptions. Present specification/contract design separately from later implementation when that reflects the intended PR sequence.

For a Laravel project, inspect current conventions before choosing controllers, requests, resources, policies, models, factories, migrations, pages and tests. Show concrete paths only after that inspection. A shared action/service is conditional unless reuse or complexity justifies it. Do not invent API files merely because OpenAPI tooling is installed.

Separate source additions from generated route types and compiled assets. Include modified existing routes or dashboard pages only when the proposed slice actually needs them. Keep deferred features out of the current slice's PR forecast.

## Consistency checks

An Agreed planner rule should have a matching canonical requirement before implementation. A proposed endpoint should match the designed contract before it is coded. A Verified status should have evidence. A dependency or release gate should match the roadmap. If any alignment is pending, say so visibly instead of implying readiness.

Never use synthetic task completion to calculate product progress. The planner is maintained by the agent from conversation and implementation evidence; the user reads it.
