# Tutorial skills

For the Laravel feedback-form lesson, install only `laravel-sdd-bootstrap`. The other tutorial skills are optional planning aids.

## Prepare the recording

```text
Use $laravel-sdd-bootstrap in recording-starter mode for a feedback form.
Use standalone PHP and Composer, Blade, SQLite and Artisan serve.
Prepare a clean starting page, but leave the form, POST route, validation,
model, migration and saving for the recording.
```

The skill checks the runtime, creates or reviews the foundation and records the remaining work. It should not introduce authentication, Docker, Herd, a frontend framework or AI packages unless the lesson needs them or you choose them.

Keep the filmed stack version and dependency lockfiles with the tutorial source. Keep the blank starting checkpoint separate from the completed demonstration. The starter being healthy does not establish that the feature works before you build it.

## Optional planning

- Use `project-kickoff` for a new project brief, plan, backlog and decision log. Its helper is create-only and preserves existing files.
- Use `sdd-stage-planner` when a substantial next feature needs a readable planner and proposed PR structure. A simple feedback-form lesson does not require an HTML planning dashboard.

## Links in video descriptions

Link the current [installation guide](install.md), the specific skill, and the immutable commit filmed. Use GitHub's file permalink action or build the URL from the full recorded SHA.

The first published Laravel bootstrap is available at [c65924b](https://github.com/jonesrussell/skills/tree/c65924b9c8e0fbdf3a5a738106cad244c2a4630d/skills/laravel-sdd-bootstrap). That link preserves its instructions and supporting files. The current repository can improve independently.

For an exact Python installation, clone the repository, check out the desired full commit in a separate checkout, and run its documented installer. A historical commit may have an older installation method; do not run its former bulk sync script as though it had current selective behavior.

Before publishing a video, record the skill SHA, exact framework/runtime versions, start command, expected starting page, and the checks actually demonstrated. Add a correction to the tutorial when a change materially affects viewers.
