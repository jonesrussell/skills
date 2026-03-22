---
name: waaseyaa-site-deploy
description: Use when creating and deploying a new Waaseyaa framework site to northcloud.one. Covers app scaffold, Caddy config, Deployer, GitHub Actions, server setup, and common pitfalls.
---

# Waaseyaa Site Deploy

End-to-end guide for creating and deploying a new site built on the Waaseyaa PHP CMS framework to production on northcloud.one.

## When to Use

- Creating a new Waaseyaa framework application
- Deploying a Waaseyaa site to northcloud.one for the first time
- Debugging a failed Waaseyaa deployment
- Setting up CI/CD for a Waaseyaa project

## Server Facts

| Item | Value |
|------|-------|
| Server | `<server-hostname>` (`<server-ip>`) |
| Web server | **Caddy** (NOT Nginx) |
| PHP | 8.4, FPM socket at `/run/php/php8.4-fpm.sock` |
| Deploy user | `<deploy-user>` (has NOPASSWD sudo for caddy and php-fpm reload/restart, and Caddyfile writes) |
| Admin user | `<admin-user>` (NOPASSWD sudo ALL) |
| Caddy runs as | `caddy` user, primary group `caddy`. Supplementary groups from `/etc/group` are NOT available under systemd. |
| Framework repo | `waaseyaa/framework` (public, no PAT needed) |
| Framework branch for CI | `develop/v1.1` — verify packages exist on this branch before adding deps |

## Phase 1: App Scaffold

### 1.1 Create GitHub repo

```bash
cd ~/dev && gh repo create waaseyaa/<site-name> --public --description "<description>" --clone
cd ~/dev/<site-name>
```

### 1.2 Create .gitignore

```gitignore
/vendor/
/.build/
/.env
*.sqlite
storage/framework/packages.php
```

### 1.3 Create composer.json

The Waaseyaa kernel requires the **full package stack** to boot. There is no lite mode. Use `@dev` stability (not `@alpha`) for local path repos.

```json
{
    "name": "waaseyaa/<site-name>",
    "description": "<description>",
    "type": "project",
    "license": "MIT",
    "require": {
        "php": ">=8.4",
        "waaseyaa/access": "^0.1@dev",
        "waaseyaa/admin-surface": "^0.1@dev",
        "waaseyaa/ai-agent": "^0.1@dev",
        "waaseyaa/ai-pipeline": "^0.1@dev",
        "waaseyaa/ai-schema": "^0.1@dev",
        "waaseyaa/ai-vector": "^0.1@dev",
        "waaseyaa/api": "^0.1@dev",
        "waaseyaa/cache": "^0.1@dev",
        "waaseyaa/cli": "^0.1@dev",
        "waaseyaa/config": "^0.1@dev",
        "waaseyaa/database-legacy": "^0.1@dev",
        "waaseyaa/entity": "^0.1@dev",
        "waaseyaa/entity-storage": "^0.1@dev",
        "waaseyaa/field": "^0.1@dev",
        "waaseyaa/foundation": "^0.1@dev",
        "waaseyaa/graphql": "^0.1@dev",
        "waaseyaa/i18n": "^0.1@dev",
        "waaseyaa/mcp": "^0.1@dev",
        "waaseyaa/media": "^0.1@dev",
        "waaseyaa/menu": "^0.1@dev",
        "waaseyaa/node": "^0.1@dev",
        "waaseyaa/note": "^0.1@dev",
        "waaseyaa/path": "^0.1@dev",
        "waaseyaa/plugin": "^0.1@dev",
        "waaseyaa/queue": "^0.1@dev",
        "waaseyaa/routing": "^0.1@dev",
        "waaseyaa/search": "^0.1@dev",
        "waaseyaa/ssr": "^0.1@dev",
        "waaseyaa/state": "^0.1@dev",
        "waaseyaa/taxonomy": "^0.1@dev",
        "waaseyaa/typed-data": "^0.1@dev",
        "waaseyaa/user": "^0.1@dev",
        "waaseyaa/validation": "^0.1@dev",
        "waaseyaa/workflows": "^0.1@dev"
    },
    "repositories": [
        {"type": "path", "url": "../waaseyaa/packages/*"}
    ],
    "autoload": {
        "psr-4": {
            "SiteName\\": "src/"
        }
    },
    "extra": {
        "waaseyaa": {
            "providers": [
                "SiteName\\Provider\\SiteServiceProvider"
            ]
        }
    },
    "config": {
        "optimize-autoloader": true,
        "sort-packages": true
    },
    "minimum-stability": "dev",
    "prefer-stable": true
}
```

**Do NOT add `Waaseyaa\Note\NoteServiceProvider` to providers** — it is auto-discovered from the note package's own `composer.json`. Adding it manually causes a "type already registered" error.

Before adding a package, verify it exists on the `develop/v1.1` branch:
```bash
git ls-tree --name-only origin/develop/v1.1 packages/ | sort
```

If a package only exists on `main`, use `"dev-main"` as the version constraint instead of `"^0.1@dev"`.

### 1.4 Create public/index.php

```php
<?php

declare(strict_types=1);

require __DIR__ . '/../vendor/autoload.php';

$kernel = new Waaseyaa\Foundation\Kernel\HttpKernel(dirname(__DIR__));
$kernel->handle();
```

### 1.5 Create config/waaseyaa.php

Minimal config for a static/marketing site:

```php
<?php

declare(strict_types=1);

return [
    'database' => null,
    'ssr' => [
        'theme' => '',
        'cache_max_age' => 300,
    ],
];
```

### 1.6 Create directories and install

```bash
mkdir -p storage/framework src/Controller src/Provider templates public/css
composer install
```

## Phase 2: ServiceProvider + Controller

### Route registration pattern

```php
<?php

declare(strict_types=1);

namespace SiteName\Provider;

use Waaseyaa\Foundation\ServiceProvider\ServiceProvider;
use Waaseyaa\Routing\RouteBuilder;
use Waaseyaa\Routing\WaaseyaaRouter;

final class SiteServiceProvider extends ServiceProvider
{
    public function register(): void {}

    public function routes(WaaseyaaRouter $router): void
    {
        $router->addRoute(
            'page.home',
            RouteBuilder::create('/')
                ->controller('SiteName\\Controller\\PageController::home')
                ->render()
                ->methods('GET')
                ->build(),
        );
    }
}
```

### Controller pattern

```php
<?php

declare(strict_types=1);

namespace SiteName\Controller;

use Symfony\Component\HttpFoundation\Request as HttpRequest;
use Twig\Environment;
use Waaseyaa\SSR\SsrResponse;

final class PageController
{
    public function __construct(
        private readonly Environment $twig,
    ) {}

    public function home(array $params, array $query, $account, HttpRequest $request): SsrResponse
    {
        return new SsrResponse($this->twig->render('home.html.twig', ['path' => '/']));
    }
}
```

### Local test

```bash
rm -f storage/framework/packages.php
REQUEST_METHOD=GET REQUEST_URI=/ SERVER_NAME=localhost php public/index.php
```

Should output HTML. If it outputs JSON:API errors, check the "Common Pitfalls" section.

## Phase 3: Deployment Infrastructure

### 3.1 Caddyfile

Create `Caddyfile` in the project root (NOT in `ops/nginx/`):

```caddy
# <domain> - included via import in main /etc/caddy/Caddyfile
# Deploy path: ~/<project>, current release: ~/<project>/current

<domain> {
  tls {
    issuer acme {
    }
  }

  root * /home/<deploy-user>/<project>/current/public

  encode gzip zstd

  @css {
    path /css/*
  }
  handle @css {
    header Cache-Control "public, max-age=31536000, immutable"
    file_server
  }

  @js {
    path /js/*
  }
  handle @js {
    header Cache-Control "public, max-age=31536000, immutable"
    file_server
  }

  @images {
    path /img/*
  }
  handle @images {
    header Cache-Control "public, max-age=31536000, immutable"
    file_server
  }

  @ico {
    path *.ico
  }
  handle @ico {
    header Cache-Control "public, max-age=31536000, immutable"
    file_server
  }

  @robots {
    path /robots.txt
  }
  handle @robots {
    header Cache-Control "public, max-age=3600"
    file_server
  }

  file_server
  php_fastcgi * unix//run/php/php8.4-fpm.sock {
    resolve_root_symlink
  }

  log {
    output file /home/<deploy-user>/<project>/log/access.log {
      mode 0644
    }
  }
}
```

### 3.2 deploy.php

```php
<?php

namespace Deployer;

require 'recipe/common.php';

set('application', '<project>');
set('keep_releases', 5);
set('allow_anonymous_stats', false);

set('shared_dirs', ['storage']);
set('shared_files', ['.env']);
set('writable_dirs', ['storage', 'storage/framework']);

host('production')
    ->setHostname('<domain>')
    ->set('remote_user', 'deployer')
    ->set('deploy_path', '/home/<deploy-user>/<project>')
    ->set('labels', ['stage' => 'production']);

desc('Upload pre-built release artifact from CI');
task('deploy:upload', function (): void {
    upload('.build/', '{{release_path}}/', [
        'options' => ['--recursive', '--compress'],
    ]);
});

desc('Clear Waaseyaa framework manifest cache');
task('waaseyaa:clear-manifest', function (): void {
    run('rm -f {{release_path}}/storage/framework/packages.php');
});

desc('Reload PHP-FPM to pick up new release');
task('php-fpm:reload', function (): void {
    run('sudo systemctl reload php8.4-fpm');
});

desc('Deploy to production');
task('deploy', [
    'deploy:info',
    'deploy:setup',
    'deploy:lock',
    'deploy:release',
    'deploy:upload',
    'deploy:shared',
    'deploy:writable',
    'waaseyaa:clear-manifest',
    'deploy:symlink',
    'deploy:unlock',
    'deploy:cleanup',
    'php-fpm:reload',
]);

after('deploy:failed', 'deploy:unlock');
```

If the app has database migrations, add a migrate task before `deploy:symlink`:
```php
task('waaseyaa:migrate', function (): void {
    run('set -a && . {{deploy_path}}/shared/.env && set +a && php {{release_path}}/bin/migrate');
});
```

### 3.3 GitHub Actions workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy Production

on:
  push:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  deploy:
    name: Build & Deploy
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Checkout app
        uses: actions/checkout@v4
        with:
          path: app

      - name: Checkout waaseyaa framework
        uses: actions/checkout@v4
        with:
          repository: waaseyaa/framework
          ref: develop/v1.1
          path: waaseyaa

      - name: Set up PHP 8.4
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.4'
          extensions: pdo_sqlite, sqlite3, mbstring, xml
          coverage: none

      - name: Install Composer dependencies
        working-directory: app
        run: |
          composer install \
            --no-dev \
            --no-interaction \
            --optimize-autoloader \
            --prefer-dist

      - name: Assemble build artifact
        run: |
          mkdir -p app/.build
          rsync -aL \
            --exclude='.git' \
            --exclude='.build/' \
            --exclude='tests/' \
            --exclude='docs/' \
            --exclude='.env' \
            --exclude='storage/framework/packages.php' \
            --exclude='deploy.php' \
            --exclude='Caddyfile' \
            app/ app/.build/

      - name: Install PHP Deployer
        run: composer global require deployer/deployer --no-interaction

      - name: Set up SSH key
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.DEPLOY_SSH_KEY }}

      - name: Add known host
        run: |
          mkdir -p ~/.ssh
          ssh-keyscan <domain> >> ~/.ssh/known_hosts

      - name: Deploy
        working-directory: app
        run: dep deploy production --no-interaction
```

## Phase 4: Server Setup

Run these steps **in order**. Use `deployer` for deploy-related tasks, `jones` for sudo tasks.

### 4.1 DNS

Set A records for `<domain>` and `www.<domain>` pointing to `<server-ip>`.

### 4.2 SSH key

```bash
ssh-keygen -t ed25519 -C "<deploy-user>@<domain>" -f ~/.ssh/<project>_deploy -N ""
ssh-copy-id -i ~/.ssh/<project>_deploy.pub <deploy-user>@<server-hostname>
```

Verify: `ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> "whoami"`

### 4.3 Server directory structure

```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "mkdir -p /home/<deploy-user>/<project>/{releases,shared/storage/framework,log}"
```

### 4.4 Shared .env

```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "cat > /home/<deploy-user>/<project>/shared/.env << 'EOF'
APP_ENV=production
WAASEYAA_DB=/home/<deploy-user>/<project>/shared/storage/waaseyaa.sqlite
EOF"
```

Create empty database file:
```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "touch /home/<deploy-user>/<project>/shared/storage/waaseyaa.sqlite"
```

### 4.5 Caddy log file (CRITICAL)

Caddy runs as the `caddy` user under systemd. The systemd service does NOT inherit supplementary groups. Caddy **cannot create** new files in dirs owned by `deployer`. You must pre-create the log file owned by `caddy`:

```bash
ssh <admin-user>@<server-hostname> \
  "sudo touch /home/<deploy-user>/<project>/log/access.log && \
   sudo chown caddy:caddy /home/<deploy-user>/<project>/log/access.log && \
   sudo chown caddy:caddy /home/<deploy-user>/<project>/log"
```

### 4.6 Install Caddyfile

Copy the Caddyfile to the server:
```bash
scp -i ~/.ssh/<project>_deploy Caddyfile <deploy-user>@<server-hostname>:/home/<deploy-user>/<project>/Caddyfile
```

Add the import to the main Caddyfile:
```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "echo 'import /home/<deploy-user>/<project>/Caddyfile' | sudo tee -a /etc/caddy/Caddyfile"
```

**BEFORE reloading**, validate ALL Caddyfiles:
```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "caddy validate --config /etc/caddy/Caddyfile 2>&1"
```

If validation passes, reload:
```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "sudo systemctl reload caddy"
```

If validation fails, **do NOT reload** — fix the issue first. A failed reload leaves the old config running, but a failed restart takes ALL sites offline.

### 4.7 GitHub secrets and environment

```bash
gh secret set DEPLOY_SSH_KEY --repo waaseyaa/<site-name> < ~/.ssh/<project>_deploy
gh api repos/waaseyaa/<site-name>/environments/production -X PUT
```

No `WAASEYAA_PAT` needed — the framework repo is public.

### 4.8 Push and verify

```bash
git push -u origin main
gh run watch --repo waaseyaa/<site-name>
```

After deploy succeeds, verify from the server:
```bash
ssh -i ~/.ssh/<project>_deploy <deploy-user>@<server-hostname> \
  "curl -sk https://<domain> | grep '<title>'"
```

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `Class "Waaseyaa\Database\PdoDatabase" not found` | Missing `waaseyaa/database-legacy` | Use the full package list — kernel requires everything |
| `DEFAULT_TYPE_MISSING` | No content type registered | `waaseyaa/note` package auto-discovers `NoteServiceProvider` — just include the package |
| `Entity type "note" is already registered` | `NoteServiceProvider` listed in both package auto-discovery AND your composer.json providers | Remove it from your providers list |
| `Source path "../waaseyaa/packages/X" not found` | Package doesn't exist on `develop/v1.1` branch | Check with `git ls-tree origin/develop/v1.1 packages/` — use `"dev-main"` or remove the dep |
| Caddy reload fails with "permission denied" on log file | `caddy` systemd service can't create files in deployer-owned dirs | Pre-create log file: `sudo touch ... && sudo chown caddy:caddy ...` |
| Caddy restart takes all sites offline | A Caddyfile in ANY imported site has a syntax error | Always `caddy validate` before reload/restart |
| `issuer acme {}` syntax error | Empty block on single line | Split to multi-line: `issuer acme {\n    }` |
| App returns JSON:API 500 "failed to boot" via PHP-FPM but works via CLI | Missing `WAASEYAA_DB` in shared `.env` | Add `WAASEYAA_DB=/home/<deploy-user>/<project>/shared/storage/waaseyaa.sqlite` |
| Committed to wrong repo | Terminal in wrong directory | Always verify `git remote -v` before `git add` |
| Composer constraint `^0.1@dev` fails for path repo | Package has no `branch-alias` in its composer.json | Use `"dev-main"` as the version constraint |

## Verification Checklist

After deployment, verify each item:

- [ ] `curl -sk https://<domain>` returns HTML (not JSON error)
- [ ] `curl -sk https://<domain>/css/site.css` returns CSS (static assets served)
- [ ] All pages render (check each route)
- [ ] `caddy validate --config /etc/caddy/Caddyfile` passes
- [ ] `systemctl is-active caddy` returns `active`
- [ ] GitHub Actions run shows green
- [ ] Log file is being written: `ls -la /home/<deploy-user>/<project>/log/access.log`
