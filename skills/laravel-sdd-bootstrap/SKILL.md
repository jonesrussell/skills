---
name: laravel-sdd-bootstrap
license: MIT
description: Prepare or review a Laravel foundation and specify the first feature. Defaults to standalone PHP and Composer, Artisan's local server, Blade and SQLite. Supports recording starters, existing-project orientation and scoped application setup.
---

# Laravel SDD bootstrap

Prepare a working Laravel foundation with a clear first feature. Bootstrap completion means the starter works; it does not mean the product or tutorial feature is implemented.

## Establish the mode

Read the brief, repository instructions and existing implementation before changing files. Preserve the user's selected stack and existing work.

- **Recording starter:** prepare the runtime, dependencies, database and any requested presentation shell. Leave the teaching feature for the presenter to build on camera. Record what is prepared and what remains to be built. Do not silently implement a finished answer, auth system or second demo.
- **Orientation or planning:** inspect and explain the current foundation. Do not install packages, format code or implement features merely to describe the project.
- **Application bootstrap:** create the requested foundation and a small first-feature specification. Continue into implementation only when it is part of the request.

For interview work, establish the time limit, required stack, permitted assistance and deliverables. Do not prebuild an assumed assignment. Ask only materially blocking questions; use reasonable reversible defaults for the rest.

## Default stack

For a new project without a specified stack, use:

- Standalone PHP and Composer from the user's configured command line.
- The official plain Laravel application scaffold with Blade.
- SQLite in `database/database.sqlite` for the application database.
- `php artisan serve` on an available loopback port.
- The scaffold's existing tests and Pint. Prefer Pest when new test infrastructure is actually needed; preserve a working PHPUnit setup.

Herd is an explicit option, not the default. Do not launch Herd, link a site, change its PHP version or depend on its binaries merely because it is installed. Likewise, do not add Docker, PostgreSQL, Redis, authentication, an SPA starter, queues or a frontend build process without a requirement for them.

An existing application or an explicit user choice overrides these defaults. SQLite is a useful local default, not a promise that it suits every production workload. Read [runtime-options.md](references/runtime-options.md) only for an explicitly selected runtime, database, richer starter or Boost setup.

## Specify the foundation and first feature

Keep the specification proportional to the assignment. A recording starter may need one README and a brief in the existing editorial workspace, rather than a new roadmap.

Separate foundation acceptance from feature acceptance. Record the chosen runtime, data store, observable first-feature behaviour and exclusions. For a feedback-form lesson, for example, the starter can be verified while form fields, validation and persistence remain unimplemented.

Draft an OpenAPI contract only for a required JSON API. Do not invent an API for a Blade page or an Inertia application. Use [planning.md](references/planning.md) when the user requests a roadmap or temporary delivery tracker.

## Bootstrap

1. Inspect `php --version`, `php --ini`, required extensions, Composer and any existing lockfiles. Resolve the actual executable before configuring editor tools. Do not change a global runtime to fix one project.
2. Check compatibility against current official Laravel documentation and the selected packages. For a tutorial, record exact installed versions and retain lockfiles so the lesson can be reproduced.
3. Create a new plain application with the official installer or `composer create-project laravel/laravel project-name`. Select a verified compatible version constraint when the lesson needs a named major release. Do not replace an existing directory.
4. Configure a local `.env` and a secret-free `.env.example`. Generate an application key for a new environment. Create the SQLite file if needed, run the initial migrations and confirm the selected database from the application runtime. Never regenerate an existing application's key as routine setup.
5. Serve the app on loopback with `php artisan serve --host=127.0.0.1 --port=<available-port>`. Inspect supported options before relying on automatic port retries. Report the URL actually served.
6. Match frontend tooling to the page. A Blade lesson using CSS in `public/` needs no Vite process. If the project uses Vite, install dependencies with its package manager and verify its production build.
7. Make documented Composer scripts work on the selected OS. Use `@php` for PHP scripts. Do not leave a convenience `dev` command that starts unnecessary services or requires an unavailable extension such as `pcntl` on native Windows.

Before looking for credentials, follow the user's local credential-location guidance when present and prefer configured profiles. A basic SQLite starter should not require external service credentials.

## Recording readiness

Keep setup and lesson work visibly separate. Prepare readable styling only when requested or useful to the agreed lesson; keep markup and application behaviour for the recording at the requested starting point.

Provide a short start command, the first file to edit, the first generator command if useful, and the acceptance checks the presenter will demonstrate. A source snapshot or an authorized Git checkpoint can preserve the starting state. Never reset a rehearsal over newer user work.

Avoid installing AI tools, creating dashboards, adding CI or preparing publication assets merely to make a local tutorial starter. These can be added when requested or needed for the actual assignment. State explicitly that the unfinished lesson has not been rehearsed or verified end to end.

## Editor setup

When VS Code setup is in scope, check for the official Laravel extension before installing it. Inspect its installed configuration schema rather than assuming setting names or types.

For the default standalone runtime, use the local PHP environment and the resolved PHP executable. Keep machine-specific paths in ignored workspace settings. Preserve unrelated editor preferences and installed extensions. Readable editor and terminal font sizes are appropriate for a recording workspace.

Verify schema-valid settings and executable resolution. Do not claim language-server completion or diagnostics work merely because an extension is installed; qualify configuration separately from an observed LSP session.

## Code documentation

Record this convention in a new project's `AGENTS.md`: document non-obvious decisions, constraints and invariants near the relevant code. Use useful PHPDoc for contracts or shapes that native types cannot express. Avoid narrating obvious code and keep comments accurate as behaviour changes.

For authenticated resource features, choose one authorization boundary and preserve existing conventions. A useful default is `auth` plus per-operation `can` middleware, with Form Requests validating input and controllers coordinating work. Ownership filtering remains necessary. Do not add authentication or policies to a public tutorial form solely to apply this convention.

Before a requested file-by-file walkthrough, review the current slice for duplication, responsibility boundaries and stale rationale. Prefer focused methods to speculative architecture.

## Verify and hand off

Run checks appropriate to the chosen foundation:

- Composer validation and platform requirements.
- Migration status against the intended local database.
- Relevant existing starter tests and configured formatting checks.
- A successful HTTP response and loading assets at the actual runtime URL.
- Frontend build/type checks, PostgreSQL-specific checks or API contract validation only when those components exist.

Do not broaden testing after the relevant checks pass unless a new change or unresolved concern warrants it. Time-box setup problems and report concrete limitations rather than claiming readiness from installation alone.

Finish with the project location, runtime URL, restart command, checks actually passed and first feature ready to build. Distinguish configured tools from verified behaviour, and foundation readiness from a completed lesson or deployed application.
