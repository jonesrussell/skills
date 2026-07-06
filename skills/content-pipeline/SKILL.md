---
name: content-distribute
description: Post content from a stage:ready content queue issue to all target channels via Buffer API. Use when a content queue item is ready to distribute, or when user says "distribute", "post this", "send to socials".
---

# Content Distribution

## Overview

Read a `stage:ready` content queue issue from `jonesrussell/jonesrussell`, publish the associated blog post if there is one, verify it is reachable, then post the social copy to all target channels via Buffer's GraphQL API.

Supports both `type:blog-post` items (full Hugo post + social copy at `docs/social/<slug>.md`) and `type:text-post` items (social copy only, referencing a PR/commit URL — no Hugo publish step).

## Prerequisites

- Blog repo at `/home/jones/dev/blog`.
- `BUFFER_API_KEY` available — either in the environment, or auto-pulled by `buffer-post.sh` from the Ansible vault at `~/dev/waaseyaa-infra/ansible/group_vars/all/vault.yml` using `~/.ansible-vault-password`. The script handles the vault lookup; you don't need to source anything manually.
- Channel IDs for `facebook`, `linkedin`, `bluesky` live in the same vault under `vault_buffer_channel_<platform>` keys. `buffer-post.sh` resolves them automatically.
- The content queue issue has the `stage:ready` label and `## Generated Artifacts` filled in.

## Process

### Step 1: Identify the issue

The user provides an issue number or you find issues with `stage:ready` label:

```bash
gh issue list --repo jonesrussell/jonesrussell --label "stage:ready" --json number,title,labels
```

Read the issue body. Extract from the `## Generated Artifacts` section:
- For blog-post items: blog draft path, target URL, social copy path
- For text-post items: social copy path, reference URL (PR/commit, used as the link in social posts)

### Step 2: Publish the blog post (blog-post items only)

Skip this step entirely if the item is `type:text-post` — there is no blog post to publish; jump to Step 5.

Check whether the post is still a draft:

```bash
grep "^draft:" /home/jones/dev/blog/<draft-path>
```

If `draft: true`, flip it:

```bash
sed -i 's/^draft: true/draft: false/' /home/jones/dev/blog/<draft-path>
```

Commit and push:

```bash
cd /home/jones/dev/blog
git add <draft-path>
git commit -m "publish: <Post Title>"
git push
```

### Step 3: Wait for deploy (blog-post items only)

```bash
RUN_ID=$(gh run list --repo jonesrussell/blog --workflow hugo.yml --limit 1 --json databaseId --jq '.[0].databaseId')
timeout 600 gh run watch "$RUN_ID" --repo jonesrussell/blog --exit-status
```

`gh run watch` has no `--timeout` flag, so `timeout 600` enforces a 10-minute hard ceiling. If the command exits non-zero (deploy failed or timed out), stop and report — do not proceed to Buffer. If it times out (exit code 124), report "Deploy watch timed out after 10 minutes — check the Actions tab manually before proceeding."

### Step 4: Verify the post is live (blog-post items only)

```bash
curl -s -o /dev/null -w "%{http_code}" <target-url>
```

If the response is not 200, wait 30 seconds and retry up to 3 times. If still not 200, stop and report — do not post to Buffer with a broken link.

### Step 5: Read the social copy

Load the social copy from the path in the issue's Generated Artifacts. Extract the platform-specific blocks:

```
## Bluesky
...
## LinkedIn
...
## Facebook
...
```

Show the copy to the user and confirm the post mode:

- **`addToQueue` (default)** — lands in the Buffer queue at the next scheduled slot per channel
- **`shareNow`** — sends immediately on each channel

Default to `addToQueue` unless the user explicitly says "now" / "immediately" / "shareNow". Per Buffer free-tier rules: scheduled cap is 10 per channel. Before queuing with `addToQueue`, run the queue depth check in Step 5b and stop if any target channel is at >= 9.

### Step 5b: Pre-flight validation

**Queue depth check (`addToQueue` only):** If the mode is `addToQueue`, run the queue status helper first:

```bash
~/.claude/skills/content-pipeline/buffer-queue-status.sh
```

If the script exits nonzero (any channel >= 9/10 or a credential error), stop and report which channels are at cap. Do not proceed to Buffer until the user either confirms headroom exists, switches to `shareNow`, or removes the at-cap channel from the target list.

**Social copy check:** Before calling `buffer-post.sh`, verify the social copy file is complete. All three sections must be present and a reference URL must exist:

```bash
SOCIAL_FILE="<path from Generated Artifacts>"
for section in "## Bluesky" "## LinkedIn" "## Facebook"; do
  grep -q "^$section" "$SOCIAL_FILE" || { echo "Missing section: $section in $SOCIAL_FILE"; exit 1; }
done
grep -q "^Reference URL:" "$SOCIAL_FILE" || { echo "Missing Reference URL in $SOCIAL_FILE"; exit 1; }
echo "Pre-flight OK"
```

If any section header or the Reference URL line is absent, stop and report the missing item — do not proceed to Buffer with incomplete copy.

**Quality gate (all modes):** Adopted 2026-07-06 after the engagement baseline showed 0 reposts across 50 Bluesky posts — changelog-shaped copy does not travel. Before posting, check each platform's copy against these rules:

1. **No pure changelog shape.** Copy whose first sentence is "[Project]'s X now does Y" (feature announcement + repo link, nothing else) fails the gate. Rewrite to lead with the problem, the stakes, or the story — the bug-story and mission-driven posts (Minoo, rhtcircle) are the proven performers.
2. **At least one of:** a concrete problem/story hook in the first sentence, an attached image (screenshot, diagram, terminal capture), or a genuine question to readers.
3. **Cadence cap:** at most 1 Bluesky post queued per calendar day. If today's slot is taken, schedule for the next free day rather than stacking. Check with `buffer-queue-status.sh`.

If copy fails the gate, do not post it as-is. Rewrite it (keeping the facts) and show the user the before/after. Only bypass the gate if the user explicitly says to post the original.

### Step 6: Post to each channel

```bash
~/.claude/skills/content-pipeline/buffer-post.sh <platform> "<copy>" <mode>
```

Where `<platform>` is one of `facebook`, `linkedin`, `bluesky`. The script reads the channel ID and API key from the vault automatically; no `source` step needed.

Run once per platform. Capture the returned `ID:` from each call — you'll cite them in Step 7's distribution comment.

### Step 7: Close out the issue

```bash
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
gh issue comment <NUMBER> --repo jonesrussell/jonesrussell --body "## Distribution Complete

Queued in Buffer (<mode>):
- [x] Bluesky — <id>
- [x] LinkedIn — <id>
- [x] Facebook — <id>

Note: addToQueue posts have no live URL until Buffer publishes them at the scheduled slot.

Distributed at: $NOW"

gh issue edit <NUMBER> --repo jonesrussell/jonesrussell --remove-label "stage:ready" --add-label "stage:distributed"
gh issue close <NUMBER> --repo jonesrussell/jonesrussell
```

## Safety

- Always publish and verify the post is live before posting to Buffer (blog-post items only).
- Never post to Buffer with a URL that returns non-200.
- Confirm the copy with the user before executing the 3 Buffer calls.
- If any channel fails, report the error and continue with the remaining channels. Do not close the issue — leave at `stage:ready` with a comment naming the failures.

## Error handling

- GitHub Actions deploy fails → stop, report, do not proceed.
- URL check fails after 3 retries → stop, report, do not proceed.
- Buffer API returns an error on a channel → print the error, skip that channel, continue with others.
- After all attempts, summarize which channels succeeded and which failed.
