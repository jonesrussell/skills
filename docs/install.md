# Install and update

Install only the skills you need. Each skill is self-contained under `skills/<name>/`.

## Repository installer

Requires Git and Python 3.11+. It uses only the Python standard library. On Windows, use `py` instead of `python` if that is your installed launcher.

```sh
python scripts/manage_skills.py list
python scripts/manage_skills.py install laravel-sdd-bootstrap --target codex --dry-run
python scripts/manage_skills.py install laravel-sdd-bootstrap --target codex
```

Targets:

| Target | Personal destination |
| --- | --- |
| `codex` | `~/.agents/skills` |
| `codex-legacy` | `$CODEX_HOME/skills`, otherwise `~/.codex/skills` |
| `claude` | `~/.claude/skills` |
| `cursor` | `~/.cursor/skills` |

Use `--dest PATH` to select a project-local skill root or a custom installation. It overrides the target's default and must be used with only one target. Relative paths resolve from the command's working directory.

```sh
python scripts/manage_skills.py install laravel-sdd-bootstrap --dest ../my-tutorial/.agents/skills --dry-run
python scripts/manage_skills.py install --bundle tutorial-skills --target codex
```

The current Codex path follows [official documentation](https://learn.chatgpt.com/docs/build-skills). Existing `.codex/skills` installations use the explicit compatibility target. Do not install the same skill into both locations without checking your client's discovery behavior.

The installer copies supporting resources with the selected skill. `--all` explicitly selects the maintained collection. An unscoped install is refused. It never prunes unrelated, vendor or client-managed skills. `sync` remains a selective install alias; the former destructive `--clean` option is gone.

## Updates and local edits

After updating the checkout, preview an update:

```sh
python scripts/manage_skills.py install laravel-sdd-bootstrap --target codex --update --dry-run
python scripts/manage_skills.py install laravel-sdd-bootstrap --target codex --update
```

`--update` replaces only an unchanged copy managed by this installer. A modified or unmanaged copy requires inspection and explicit `--replace`; replacement keeps the previous directory under the destination's `.jonesrussell-skills/backups/` directory. The tool prints its path. Receipts record content hashes, not credentials. Restoring a backup is manual: preserve the current copy and copy the selected backup to the original skill location.

Identical content is left untouched. An identical pre-existing unmanaged copy stays unmanaged; a later change still requires explicit replacement. Linked destinations, symlinks and junctions are refused. Existing symlink installations require manual handling, with their target preserved.

All selected skills are checked before writes begin. Each replacement stages a copy and restores the previous installation on a failed replacement. A multi-skill batch is not one global transaction: a later disk failure can leave earlier skills successfully updated. Inspect the output before rerunning.

```sh
python scripts/manage_skills.py audit laravel-sdd-bootstrap --target codex
```

Audit reads only. A missing or different installation returns a nonzero exit code. Restart the agent or refresh its skills if the change does not appear; copying files alone does not prove runtime discovery.

## Optional skills CLI

The third-party [skills CLI](https://github.com/vercel-labs/skills) needs Node.js 22.20+. Its default is a project install; `-g` selects a personal install.

```sh
npx skills add jonesrussell/skills --skill laravel-sdd-bootstrap -a codex
```

Its update and overwrite behavior belongs to that CLI, not this repository's Python installer. Avoid using multiple installers to manage the same destination. For a filmed version, check out the recorded commit first and install from that checkout, or use a documented GitHub tree URL supported by the CLI.

On October 24, `skills@1.7.4` discovered the five-skill collection and successfully copied only `laravel-sdd-bootstrap` into an isolated Codex project directory on Windows. This verifies that installation path, not a running model's invocation behavior.

## Claude Code marketplace

```text
/plugin marketplace add jonesrussell/skills
/plugin install tutorial-skills@jonesrussell-skills
```

`tutorial-skills` contains exactly Laravel bootstrap, project kickoff and stage planning. `repository-skills` contains exactly repository audit and archive readiness. Entries declare their exact skill paths. Do not also copy those same skills into your personal directory unless you intend duplicate discovery.

The manifest is structurally checked against this repository's catalog. Native Claude plugin loading is not part of the current automated test suite. Check it with `claude plugin validate .` and a fresh client session when releasing marketplace changes.

The old blog, code quality, Waaseyaa, workflow and planning bundles are removed. Previously installed client cache copies may persist. Review them in the client's plugin manager and uninstall obsolete bundles there. The repository installer does not modify client caches.
