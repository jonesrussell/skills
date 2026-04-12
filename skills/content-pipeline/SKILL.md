---
name: content-distribute
description: Post content from a stage:ready content queue issue to all target channels via Buffer API. Use when a content queue item is ready to distribute, or when user says "distribute", "post this", "send to socials".
---

# Content Distribution

## Overview

Read a `stage:ready` content queue issue from jonesrussell/jonesrussell, publish the associated blog post if not already live, verify it is reachable, then post the social copy to all target channels via Buffer's GraphQL API.

## Prerequisites

- `BUFFER_API_KEY` environment variable must be set
- Channel IDs in `~/.claude/skills/content-pipeline/channels.env`
- The content queue issue must have `stage:ready` label and generated artifacts in the issue body
- Blog repo at `/home/jones/dev/blog`

## Process

### Step 1: Identify the issue

The user provides an issue number or you find issues with `stage:ready` label:

```bash
gh issue list --repo jonesrussell/jonesrussell --label "stage:ready" --json number,title
```

Read the issue body. Extract:
- Blog draft path (`content/posts/<category>/<slug>/index.md`)
- Target URL (`https://jonesrussell.github.io/blog/<slug>/`)
- Social copy paths and channels

### Step 2: Publish the blog post if draft

Check whether the post is still a draft:

```bash
grep "^draft:" /home/jones/dev/blog/<draft-path>
```

If `draft: true`, flip it:

```bash
sed -i 's/^draft: true/draft: false/' /home/jones/dev/blog/<draft-path>
```

Then commit and push:

```bash
cd /home/jones/dev/blog
git add <draft-path>
git commit -m "publish: <Post Title>"
git push
```

Show the user: "Flipped draft: false and pushed. Waiting for GitHub Actions deploy..."

### Step 3: Wait for deploy to complete

Poll the GitHub Actions workflow until it completes:

```bash
gh run list --repo jonesrussell/blog --workflow hugo.yml --limit 1 --json status,conclusion,url
```

Poll every 30 seconds. Report status updates. Fail loudly if the workflow fails — do not proceed to Buffer.

### Step 4: Verify the post is live

Once the workflow succeeds, confirm the URL is reachable:

```bash
curl -s -o /dev/null -w "%{http_code}" <target-url>
```

If the response is not 200, wait 30 seconds and retry up to 3 times. If still not 200, stop and report — do not post to Buffer with a broken link.

### Step 5: Read the social copy

Load the social copy from `docs/social/<slug>.md` in the blog repo. Extract the platform-specific blocks (Facebook, X, LinkedIn).

Show the user the copy that will be posted to each channel and ask for confirmation:

```
Ready to distribute:

**Facebook:** <copy>
**X:** <copy>
**LinkedIn:** <copy>

Post to all three? (yes/no)
```

### Step 6: Post to each channel

Load channel config:

```bash
source ~/.claude/skills/content-pipeline/channels.env
```

For each target channel, call:

```bash
~/.claude/skills/content-pipeline/buffer-post.sh "$CHANNEL_ID" "$COPY" addToQueue
```

Channel mapping:
- `x` or `twitter` → `$BUFFER_CHANNEL_TWITTER`
- `facebook` → `$BUFFER_CHANNEL_FACEBOOK`
- `linkedin` → `$BUFFER_CHANNEL_LINKEDIN`

### Step 7: Update the issue

After all channels are posted:

```bash
gh issue comment <NUMBER> --repo jonesrussell/jonesrussell --body "## Distribution Complete

Posted to:
- [x] Facebook
- [x] X/Twitter
- [x] LinkedIn

Distributed at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

gh issue edit <NUMBER> --repo jonesrussell/jonesrussell --remove-label "stage:ready" --add-label "stage:distributed"
gh issue close <NUMBER> --repo jonesrussell/jonesrussell
```

## Safety

- Always publish and verify the post is live before posting to Buffer
- Never post to Buffer with a URL that returns non-200
- Show the user the copy for each channel and wait for confirmation before executing
- If any channel fails, report the error and continue with remaining channels

## Error Handling

- If the GitHub Actions deploy fails: stop, report the failure, do not proceed
- If the URL check fails after 3 retries: stop, report, do not proceed
- If Buffer API returns an error: print the error, skip that channel, continue with others
- After all attempts, report which channels succeeded and which failed
- Do not close the issue if any channel failed — leave at `stage:ready` with a comment noting failures
