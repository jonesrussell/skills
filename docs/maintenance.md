# Maintain the collection

## Admit a useful workflow

Start from a task that was actually performed. Identify what the agent needed beyond its general knowledge: a useful default, non-obvious failure mode, reliable transformation or project-independent procedure. Do not add a skill only to fill a category.

Keep repository facts, private accounts and deployment procedures with their owning project. This public collection should work from declared prerequisites and the files it ships. Reference current official documentation for changing APIs rather than copying a manual into the repo.

New work starts as a proposal in an issue or ordinary documentation, outside the installable `skills/` tree. Add it to the catalog when its scope, resources and checks are ready. Keep names stable; categories and bundle membership can change without breaking tutorial permalinks.

## Layout and tools

```text
skills/<name>/
  SKILL.md
  agents/openai.yaml       # Optional host metadata
  references/             # Only useful conditional detail
  scripts/                # Tested workflow helpers
  assets/                 # Files used in the result
  evals/evals.json         # Realistic behavior cases
catalog.json              # Public inventory and bundle membership
scripts/                  # Repository maintenance and installation
tests/                    # Repository tooling tests
docs/                     # Installation, evidence and decisions
```

Do not create empty resource directories. Keep skills self-contained so copying one directory works. A helper used by one skill belongs inside it. Shared tooling needs multiple demonstrated consumers, a stable contract and its own tests before it becomes a separate package. Do not make a skill depend on sibling repository files that an individual installation will omit.

Prefer existing CLI tools to trivial wrappers. State required runtimes and distinguish optional tools. Helpers should accept flags or structured input, report actionable failures, and avoid interactive prompts. Use explicit output paths and preview/create-only behavior where useful. Test them in temporary directories. An install must not execute a skill's operational scripts.

MCP is appropriate for authenticated live capabilities and shared services. Use an existing connector when available. Keep tokens and account-specific configuration outside public packages. No MCP service, hook, publisher or deployment side effect is enabled by this collection's installer.

## Verification

Run from the repository root:

```sh
python scripts/catalog.py generate
python scripts/catalog.py check
python -m unittest discover -s tests
python skills/project-kickoff/scripts/test_scaffold.py
python scripts/manage_skills.py install --bundle tutorial-skills --dest .install-preview --dry-run
```

The catalog owns generated documentation and the Claude marketplace. Check required frontmatter, local links, catalog membership, evaluation case presence and bundle paths. CI runs repository and helper checks on Windows and Linux with Python 3.11. No test should use a real agent installation or a live publishing/deployment account.

Use each skill's `evals/evals.json` for manual or separately authorized model evaluations. Include realistic positive cases and a nearby request the skill should not handle. Compare actual outputs with the skill and without it or with the previous version. Inspect the produced artifacts, refusal behavior and unnecessary work. Record model, host, prompt, skill commit and observed evidence. Keep private outputs out of this repository.

Fixture validation proves the case file is well formed. It does not execute those cases or prove model quality. Do not replace observations with regex matches on preferred wording. The catalog distinguishes reviewed instructions, tested helper behavior and real workflow evidence from a benchmark that has not been run.

## Releases and history

Use normal commits and PRs. Never reset repository history to remove old skills. Record removals in `catalog.json` with reason and the exact recovery revision; generate `docs/retired.md`. Remove deprecated skills from all installable bundles and document how existing client installations are handled.

Update `CHANGELOG.md` and the catalog version when publishing a changed collection. Review the diff and CI results, then use the resulting full commit SHA in tutorial descriptions. A future release tag should be immutable once linked from a published video.

For marketplace changes, run native client validation and a discovery test when that client is available. Report its absence honestly. Structural validation alone is not an end-to-end client test.

The maintained collection is MIT licensed by the maintainer's October 24 decision. Each skill includes a generated copy of the root license so individual installs carry the notice. Keep provenance records for imported work. Do not assign this license to third-party material without checking its existing terms; historical recovery links are not a relicensing claim for removed third-party content.

## Near-term growth

First rehearse and release the Laravel feedback-form lesson. Improve the skill from that run. Next candidates are a demonstrated Drupal tutorial workflow and a promotion-planning skill that delegates posting to the current publisher. Keep these as candidates until their actual workflow and evaluation evidence exist.

The [research decision](research-2026-10.md) explains the chosen boundaries. Revisit packaging when a new supported host or tool integration creates a concrete need, not on a fixed skill-count schedule.
