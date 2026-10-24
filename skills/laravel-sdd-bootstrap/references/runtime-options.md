# Explicit runtime and tooling options

Read only the section matching the user's chosen stack. The default remains standalone PHP/Composer, Artisan's local server, Blade and SQLite.

## Herd

Use Herd when the user explicitly selects it or when maintaining an already configured Herd project without a request to change runtime.

- Inspect installation and onboarding state. Show required interactive onboarding instead of hiding it.
- Link only the requested project and isolate a compatible PHP version. Do not change the global version for unrelated sites.
- Verify `herd which-php`, `herd php` and `herd composer` from the project directory.
- Confirm the linked `.test` URL responds through Herd. Do not confuse a separate Artisan server with proof of Herd readiness.
- Configure editor tools for the chosen runtime using the installed extension's actual schema. Keep machine-specific executable paths local.

Check current official Herd documentation for command syntax and supported versions. Do not purchase Herd Pro or infer that a database service is available from the free runtime.

## PostgreSQL or containers

Use the database required by the project. Preserve working databases and credentials. Do not replace a local or production database to match this skill's default.

For a Windows application with PostgreSQL in WSL Docker, verify the existing engine and service before provisioning another. Publish an available project-specific port on `127.0.0.1`. A Docker service hostname is not the host address used by native Windows PHP. Verify `pdo_pgsql` in the application's actual runtime and run migrations against the intended database.

SQLite in-memory tests do not prove PostgreSQL behaviour. Check relevant database-specific features separately. Document the actual database start and stop procedure without retiring another application's runtime.

## Richer starters and quality tooling

Use Vue/Inertia, React, Livewire, authentication, typed routes or additional analysis tools when the brief calls for them. Preserve the chosen starter's conventions.

For native Windows, install Node dependencies on Windows; do not reuse Linux-built native bindings. Generate any route/type artifacts before dependent type checks. Use the existing formatter and linter rather than inventing a custom style checker.

Add CI when requested or appropriate to the delivery scope. Keep public tutorial setup small enough that each dependency has an explainable role.

## Laravel Boost

Boost is development assistance, not a product AI feature. Use it when requested or useful for an authorized implementation workflow; it is not a prerequisite for a small recording starter.

Configure its server using the application's actual PHP runtime and working directory. Verify application information and any required database access. Do not leave a connection pointing at a retired container or host.

Where the environment supports it, verify through the current chat's MCP tools. A standalone stdio probe proves only that the server executable works, not that the chat transport is connected. Distinguish those outcomes and investigate the relevant process/log evidence before attributing recovery to a restart.
