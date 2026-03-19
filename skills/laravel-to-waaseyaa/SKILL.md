---
name: laravel-to-waaseyaa
description: Use when creating new Waaseyaa packages that port Laravel functionality, migrating Laravel features to the Waaseyaa framework, or building new packages in the waaseyaa/framework monorepo. Triggers on package scaffolding, TDD package development, or composer monorepo wiring.
---

# Laravel to Waaseyaa Package Migration

## Overview

A repeatable pattern for building new Waaseyaa packages that replace Laravel functionality. Each package follows a strict scaffold-TDD-wire-deploy pipeline proven with `waaseyaa/inertia`.

## When to Use

- Creating a new package in `/home/fsd42/dev/waaseyaa/packages/`
- Porting a Laravel feature (auth, billing, notifications, etc.) to Waaseyaa
- Building any new `waaseyaa/*` composer package in the monorepo
- When the user mentions "new waaseyaa package" or "migrate X from Laravel"

## When NOT to Use

- Modifying existing Waaseyaa packages (use normal development workflow)
- Frontend-only changes (Vue/Inertia client-side)
- Go API changes in goforms/

## The Pipeline

Every new package follows these 6 phases in order. Do not skip phases.

### Phase 1: Research

Before writing any code, understand what you're replacing:

1. **Read the migration design spec** if one exists (`docs/superpowers/specs/`)
2. **Study the Laravel source** — identify the classes, interfaces, and behaviors to port
3. **Map Laravel concepts to Waaseyaa equivalents:**

| Laravel | Waaseyaa |
|---------|----------|
| Service Provider | `ServiceProvider` (extends `Waaseyaa\Foundation\ServiceProvider\ServiceProvider`) |
| Middleware | `HttpMiddlewareInterface` (in `Waaseyaa\Foundation\Middleware`) |
| Facade | Static class (no magic, explicit methods) |
| Controller returning view | Controller returning `SsrResponse` or `InertiaResponse` |
| Config files | `$this->config` array from kernel context |
| Artisan commands | Symfony Console commands via `commands()` method |
| Eloquent models | Waaseyaa Entity system |
| Route registration | `routes(WaaseyaaRouter $router)` method on ServiceProvider |

4. **Check existing packages** for patterns to follow — especially `packages/ssr/`, `packages/inertia/`, `packages/mail/`

### Phase 2: Scaffold

Create the package skeleton:

```
packages/<name>/
├── composer.json
├── src/
│   └── <Name>ServiceProvider.php
└── tests/
    └── Unit/
```

**composer.json template:**
```json
{
    "name": "waaseyaa/<name>",
    "description": "<one-line description>",
    "type": "library",
    "license": "GPL-2.0-or-later",
    "repositories": [
        { "type": "path", "url": "../foundation" }
    ],
    "require": {
        "php": ">=8.4",
        "waaseyaa/foundation": "@dev"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.5"
    },
    "autoload": {
        "psr-4": { "Waaseyaa\\<Name>\\": "src/" }
    },
    "autoload-dev": {
        "psr-4": { "Waaseyaa\\<Name>\\Tests\\": "tests/" }
    },
    "extra": {
        "waaseyaa": {
            "providers": ["Waaseyaa\\<Name>\\<Name>ServiceProvider"]
        },
        "branch-alias": { "dev-main": "0.1.x-dev" }
    },
    "minimum-stability": "dev",
    "prefer-stable": true
}
```

**ServiceProvider stub:**
```php
<?php
declare(strict_types=1);
namespace Waaseyaa\<Name>;

use Waaseyaa\Foundation\ServiceProvider\ServiceProvider;

final class <Name>ServiceProvider extends ServiceProvider
{
    public function register(): void {}
}
```

**Wire to root composer.json** — add three entries:
1. `repositories[]` — `{ "type": "path", "url": "packages/<name>" }`
2. `require` — `"waaseyaa/<name>": "@dev"`
3. `autoload-dev.psr-4` — `"Waaseyaa\\<Name>\\Tests\\": "packages/<name>/tests/"`

**Verify:** `composer update waaseyaa/<name>` — must resolve without errors.

### Phase 3: TDD Core Components

For each source file in the package:

1. **Write the test first** at `tests/Unit/<ClassName>Test.php`
2. **Run the test** — verify it fails (class not found)
3. **Write the implementation** at `src/<ClassName>.php`
4. **Run the test** — verify it passes
5. **Move to next component**

**Conventions:**
- `declare(strict_types=1)` on every file
- `final` classes by default
- `readonly` value objects where appropriate
- PHPUnit `#[CoversClass]` attributes on test classes
- No docblocks on obvious methods — only `@param`/`@return` for arrays

**Test runner:** `vendor/bin/phpunit packages/<name>/tests/`

### Phase 4: Wire Service Provider

Once core components exist:

1. Register middleware via `middleware(EntityTypeManager)` if the package has middleware
2. Register routes via `routes(WaaseyaaRouter)` if the package has routes
3. Add any ControllerDispatcher integration (soft `instanceof` checks — no hard dependency)

### Phase 5: Verify

1. **Run package tests:** `vendor/bin/phpunit packages/<name>/tests/`
2. **Run CS Fixer:** `vendor/bin/php-cs-fixer fix packages/<name>/`
3. **Run foundation tests** if ControllerDispatcher was modified: `vendor/bin/phpunit packages/foundation/tests/`
4. **Commit** with conventional commit: `feat(<name>): <description>`

### Phase 6: Deploy

1. **Add to split workflow** — `.github/workflows/split.yml` matrix, correct layer comment
2. **Create split target repo** — `waaseyaa/<name>` on GitHub (public, no README init)
3. **Commit and push** split.yml change
4. **Tag and push** — increment the alpha tag: `git tag v0.1.0-alpha.<next> && git push origin v0.1.0-alpha.<next>` to trigger split. Check latest tag with `git tag --sort=-v:refname | head -1`.
5. **Submit to Packagist** — `https://packagist.org/packages/submit` with `https://github.com/waaseyaa/<name>`

## ControllerDispatcher Integration Pattern

When a package returns custom response types from callable controllers, add handling in `packages/foundation/src/Http/ControllerDispatcher.php` in the callable controller branch (after `SsrResponse` check):

```php
if ($result instanceof \Waaseyaa\<Name>\<ResponseType>) {
    // Handle response — use ResponseSender::json() or ResponseSender::html()
}
```

This is a **soft dependency** — if the package isn't installed, the `instanceof` check returns `false`. No error.

## Waaseyaa Architecture Reference

```
Layer 0: Foundation (foundation, cache, plugin, typed-data, database-legacy, testing, i18n, queue, state, validation, mail, github)
Layer 1: Core Data (entity, entity-storage, access, user, config, field)
Layer 2: Content Types (node, taxonomy, media, path, menu, note, relationship)
Layer 3: Services (workflows)
Layer 4: API (api, routing)
Layer 5: AI (ai-schema, ai-agent, ai-pipeline, ai-vector)
Layer 5.5: GraphQL (graphql)
Layer 6: Interfaces (cli, inertia, mcp, ssr, telescope, admin-surface)
Meta: cms, core, full
```

Dependencies point inward — higher layers depend on lower layers, never the reverse.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `autoload-dev` in root composer.json | Tests won't be found by PHPUnit |
| Hard dependency on inertia/ssr in foundation | Use soft `instanceof` checks in ControllerDispatcher |
| Skipping CS Fixer before push | CI will fail on `fn ()` vs `fn()` style |
| Not creating the GitHub split repo before tagging | Split workflow fails silently |
| Adding package to wrong layer in split.yml | Check dependency direction — higher layers only |

## Quick Reference

```bash
# Scaffold
mkdir -p packages/<name>/{src,tests/Unit}
# Write composer.json, ServiceProvider, wire root composer.json
composer update waaseyaa/<name>

# TDD loop (per component)
vendor/bin/phpunit packages/<name>/tests/Unit/<Test>.php  # RED
# write implementation
vendor/bin/phpunit packages/<name>/tests/Unit/<Test>.php  # GREEN

# Verify
vendor/bin/phpunit packages/<name>/tests/
vendor/bin/php-cs-fixer fix packages/<name>/
vendor/bin/phpunit packages/foundation/tests/  # if dispatcher modified

# Deploy
# Edit .github/workflows/split.yml
# Create waaseyaa/<name> repo on GitHub
git push
git tag v0.1.0-alpha.<next> && git push origin v0.1.0-alpha.<next>
# Submit to packagist.org
```
