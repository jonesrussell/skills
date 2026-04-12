#!/usr/bin/env bash
# Post to a Buffer channel via GraphQL API
# Usage: ./buffer-post.sh <platform> <text> [mode] [first_comment_url]
# platform: facebook, twitter, linkedin
# mode: addToQueue (default), shareNow, customScheduled
# first_comment_url: URL to post as first comment (linkedin and facebook only; X is manual self-reply)
# For customScheduled, set DUE_AT env var to ISO8601 datetime
# Channel IDs and API key are read from Ansible vault automatically.

set -euo pipefail

VAULT_FILE="$HOME/dev/northcloud-ansible/inventory/group_vars/all/vault.yml"
VAULT_PASS="$HOME/.ansible-vault-password"

_vault_get() {
  ansible-vault view "$VAULT_FILE" --vault-password-file "$VAULT_PASS" 2>/dev/null \
    | grep "^$1:" | sed 's/.*: *"\(.*\)"/\1/'
}

if [[ -z "${BUFFER_API_KEY:-}" ]]; then
  if [[ -f "$VAULT_FILE" && -f "$VAULT_PASS" ]]; then
    BUFFER_API_KEY=$(_vault_get vault_buffer_api_key)
    export BUFFER_API_KEY
  fi
  if [[ -z "${BUFFER_API_KEY:-}" ]]; then
    echo "Error: BUFFER_API_KEY not set and could not extract from Ansible vault" >&2
    exit 1
  fi
fi

PLATFORM="${1:?Usage: buffer-post.sh <platform> <text> [mode] [first_comment_url]}"
TEXT="${2:?Usage: buffer-post.sh <platform> <text> [mode] [first_comment_url]}"
MODE="${3:-addToQueue}"
FIRST_COMMENT_URL="${4:-}"

# Resolve channel ID from vault
case "$PLATFORM" in
  facebook)  CHANNEL_ID=$(_vault_get vault_buffer_channel_facebook) ;;
  twitter)   CHANNEL_ID=$(_vault_get vault_buffer_channel_twitter) ;;
  linkedin)  CHANNEL_ID=$(_vault_get vault_buffer_channel_linkedin) ;;
  *)
    echo "Error: unknown platform '$PLATFORM'. Use: facebook, twitter, linkedin" >&2
    exit 1
    ;;
esac

if [[ -z "$CHANNEL_ID" ]]; then
  echo "Error: no channel ID found in vault for platform '$PLATFORM'" >&2
  exit 1
fi

# Build the GraphQL mutation using Python for safe JSON encoding
RESPONSE=$(python3 -c "
import json, subprocess, sys

text = sys.argv[1]
channel_id = sys.argv[2]
mode = sys.argv[3]
platform = sys.argv[4]
due_at = sys.argv[5] if len(sys.argv) > 5 else ''
first_comment_url = sys.argv[6] if len(sys.argv) > 6 else ''
api_key = sys.argv[7]

due_at_field = f'dueAt: \"{due_at}\"' if mode == 'customScheduled' and due_at else ''

# Platform-specific metadata (type + optional firstComment)
metadata_field = ''
if platform == 'facebook':
    if first_comment_url:
        metadata_field = f'metadata: {{ facebook: {{ type: post firstComment: {json.dumps(first_comment_url)} }} }}'
    else:
        metadata_field = 'metadata: { facebook: { type: post } }'
elif platform == 'linkedin' and first_comment_url:
    metadata_field = f'metadata: {{ linkedin: {{ firstComment: {json.dumps(first_comment_url)} }} }}'

query = f'''mutation {{
  createPost(input: {{
    channelId: \"{channel_id}\"
    text: {json.dumps(text)}
    mode: {mode}
    schedulingType: automatic
    {due_at_field}
    {metadata_field}
  }}) {{
    ... on PostActionSuccess {{
      post {{
        id
        status
        text
        externalLink
      }}
    }}
    ... on NotFoundError {{ message }}
    ... on UnauthorizedError {{ message }}
    ... on UnexpectedError {{ message }}
    ... on RestProxyError {{ message }}
    ... on LimitReachedError {{ message }}
    ... on InvalidInputError {{ message }}
  }}
}}'''

payload = json.dumps({'query': query})
result = subprocess.run(
    ['curl', '-s', '-X', 'POST', 'https://api.buffer.com',
     '-H', f'Authorization: Bearer {api_key}',
     '-H', 'Content-Type: application/json',
     '-d', payload],
    capture_output=True, text=True
)
print(result.stdout)
" "$TEXT" "$CHANNEL_ID" "$MODE" "$PLATFORM" "${DUE_AT:-}" "$FIRST_COMMENT_URL" "$BUFFER_API_KEY")

# Parse response: union type — PostActionSuccess has .post; all errors have .message
echo "$RESPONSE" | python3 -c "
import json, sys

try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f'Error parsing API response: {e}', file=sys.stderr)
    sys.exit(1)

top_errors = data.get('errors', [])
if top_errors:
    for e in top_errors:
        print(e.get('message', str(e)), file=sys.stderr)
    sys.exit(1)

result = data.get('data', {}).get('createPost', {})

if 'message' in result:
    print(f'Error posting to Buffer: {result[\"message\"]}', file=sys.stderr)
    sys.exit(1)

post = result.get('post', {})
if not post:
    print('Error: unexpected empty response from Buffer', file=sys.stderr)
    print(json.dumps(data), file=sys.stderr)
    sys.exit(1)

print(f\"Posted: {post.get('status', 'unknown')}\")
print(f\"ID: {post.get('id', 'n/a')}\")
link = post.get('externalLink', '')
if link:
    print(f'Link: {link}')
"
