---
name: sdd-stage-planner
license: MIT
description: Refine the current product build stage through conversation, maintain a readable HTML/CSS sidecar planner and propose a PR file tree before implementation. Use when working from an existing foundation toward an MVP with Spec Driven Development; this does not bootstrap or authorize product code.
---

# Sdd Stage Planner

Help the user decide what to build next without making them read raw specifications. Keep a stage-focused planner aligned with canonical specifications, contracts and a glanceable overall tracker. Work across multiple conversations and refine the workflow from actual user feedback.

## Establish the stage

Read repository instructions, product brief, roadmap, current specifications and relevant contracts. Inspect git status and enough existing implementation to distinguish scaffolding from product behavior. Preserve unrelated work. Use the project's existing stack and conventions; do not bootstrap again.

Identify the current stage from the user's direction and roadmap. A stage may contain several small slices or PRs. For example, creation and publishing can be discussed together while private create/view remains the first implementation slice. Keep later milestones visible only as boundaries or dependencies, not as a second full roadmap inside the planner.

Default to planning when the user asks to discuss, refine or specify. Creating this skill, invoking it or approving a planner's appearance does not authorize product code. Existing explicit implementation authorization still applies within its scope; do not add a redundant approval ceremony. Resolve decisions needed by the next slice before dependent code. Ask only materially blocking questions and continue independent planning work.

## Conversation-driven refinement

Start with a concise account of what is known and the most consequential unresolved choice. Use plain user journeys and concrete success/failure examples to explain tradeoffs. Avoid asking a large questionnaire or silently turning proposals into requirements.

Record decisions as Proposed, Agreed or Open. Record important assumptions and why a consequential choice was made. When the user changes direction, update affected scope, rules, acceptance criteria and proposed file list together; keep the planner internally consistent. Do not silently overwrite an agreed decision with a new default.

On resuming, recover stage, agreed decisions, remaining questions, next slice and verification evidence from project artifacts. Avoid relying on chat memory alone. Briefly state any conflicts between artifacts and resolve them before dependent implementation.

## Maintain the planning artifacts

For the requested planning workflow, maintain a portable, read-only HTML/CSS sidecar in the project's existing documentation location. Read [references/planner-content.md](references/planner-content.md) when creating or substantially revising it. Reuse an existing planner rather than proliferating files. Create/update documentation only within the user's request and repository instructions.

The planner presents the important specification decisions in readable language, not raw Markdown, YAML, full OpenAPI schemas or copied specification dumps. The specification and contract remain authoritative for implementation. Link them as optional detail. Update canonical documents when decisions materially change behavior and before code generation; if required canonical updates are not yet made, label the planner's proposal accordingly.

Keep the overall tracker short: current stage, next step and evidence-backed milestone status. The sidecar holds stage detail. Add reciprocal local links where useful. Include a snapshot date and distinguish proposed work, implementation and verified behavior. Never turn a planned file tree or passing formatting check into a feature-completion claim.

Inspect the actual application's design tokens and use its palette, borders, typography stack and light/dark treatment. Make the planner easy to read and glance at, with clear hierarchy, compact summaries and a responsive file tree. Keep it offline and independent of app routes, services and credentials. No checklist inputs, progress percentages, local storage or management controls unless requested. Detailed planning can be longer than the overall tracker, but the main decisions should be apparent at the top.

## Propose the PR structure

Inspect sibling files and existing abstractions before proposing paths. Group the expected diff by small reviewable PR/slice. Mark each path Added, Modified, Generated/ignored or Conditional, and explain its responsibility in one sentence. Distinguish proposed files from files that already exist. Use placeholder migration timestamps rather than invented generated names.

Include specification/contract changes, backend behavior, frontend pages/components and meaningful tests as needed. Identify existing files to reuse and important exclusions. Do not create empty scaffolds or a new architectural layer just to make the tree look complete. Generated Wayfinder artifacts and build outputs should not be presented as tracked source additions when ignored by the repository. Treat the file tree as a review forecast that may change with justified implementation details, not a promise to create every path.

## Move from planning to verified work

Follow project status vocabulary, commonly Draft → Ready → Implementing → Verified. Ready means relevant choices are resolved, acceptance/failure criteria are observable, contracts are designed where required and the first slice is bounded. It does not mean implementation is authorized or complete.

When implementation is authorized, use applicable framework skills and package-aware documentation, implement only the current slice and test observable behavior. Update the planner with actual changed paths, checks performed, remaining limitations and next slice. Mark Verified only from sufficient recorded evidence. Keep publication, deployment and paid provisioning within their existing authorization boundaries.

Carry agreed implementation conventions into each slice. For new authenticated Laravel resource routes, a consistent `auth` plus per-operation `can` middleware boundary can invoke policies while Form Requests validate input and controllers coordinate operations. Preserve existing conventions and do not add authentication to a public feature merely to apply this example. Before a file-by-file user review, review the full slice for duplication, responsibility boundaries, named limits and useful comments, apply justified improvements within scope, and verify them. Avoid speculative layers or custom style tooling. Keep domain-specific choices in repository guidance rather than embedding them in this skill.

Carry the code documentation standard into repository guidance outside generated sections when maintaining that guidance is in scope. Each implementation slice must explain non-obvious decisions, constraints and invariants close to the relevant handwritten code. Use useful PHPDoc for contracts and types that native declarations cannot express, and appropriate comments in other languages, following framework conventions. Explain reasons for unusual authorization, retry, concurrency, normalization or integration behavior; avoid narrating obvious code or copying full specifications. Keep comments aligned with behavior changes. Before marking a slice Verified, review its changed code for missing rationale and stale comments alongside the behavior checks. Do not add comments to generated or vendor files solely to satisfy this review.

## Validate and hand off

Check planner/spec/contract consistency and links, portable offline dependencies and readable desktop/narrow layout when permitted browser tools are available. Do not circumvent blocked local-file browser access; disclose unverified visual behavior. Run appropriate formatting/contract checks for changed artifacts; planning alone does not need application behavior tests. Report what was actually checked.

Hand off with a link to the current planner, decisions still needed and the next concrete slice. Refine this skill when the user requests or confirms a reusable workflow change, preserving project-specific details in project artifacts rather than embedding them here.
