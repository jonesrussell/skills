#!/usr/bin/env bash
# Post to a single Buffer channel via GraphQL API
# Usage: ./buffer-post.sh <channel_id> <text> [mode] [platform]
# mode: shareNow (default), addToQueue, customScheduled
# platform: facebook, twitter, linkedin (optional, used for platform-specific metadata)
# For customScheduled, set DUE_AT env var to ISO8601 datetime
# Requires: BUFFER_API_KEY environment variable

set -euo pipefail

if [[ -z "${BUFFER_API_KEY:-}" ]]; then
  # Auto-extract from Ansible vault if available
  VAULT_FILE="$HOME/dev/northcloud-ansible/inventory/group_vars/all/vault.yml"
  VAULT_PASS="$HOME/.ansible-vault-password"
  if [[ -f "$VAULT_FILE" && -f "$VAULT_PASS" ]]; then
    BUFFER_API_KEY=$(ansible-vault view "$VAULT_FILE" --vault-password-file "$VAULT_PASS" 2>/dev/null | grep vault_buffer_api_key | sed 's/.*: *"\(.*\)"/\1/' || true)
    export BUFFER_API_KEY
  fi
  if [[ -z "${BUFFER_API_KEY:-}" ]]; then
    echo "Error: BUFFER_API_KEY not set and could not extract from Ansible vault" >&2
    exit 1
  fi
fi

CHANNEL_ID="${1:?Usage: buffer-post.sh <channel_id> <text> [mode] [platform]}"
TEXT="${2:?Usage: buffer-post.sh <channel_id> <text> [mode] [platform]}"
MODE="${3:-addToQueue}"
PLATFORM="${4:-}"

# Build the GraphQL mutation using Python for safe JSON encoding
RESPONSE=$(python3 -c "
import json, subprocess, sys, os

text = sys.argv[1]
channel_id = sys.argv[2]
mode = sys.argv[3]
due_at = sys.argv[4] if len(sys.argv) > 4 else ''
platform = sys.argv[5] if len(sys.argv) > 5 else ''
api_key = sys.argv[6]

due_at_field = f'dueAt: \"{due_at}\"' if mode == 'customScheduled' and due_at else ''

# Platform-specific metadata
metadata_field = ''
if platform == 'facebook':
    metadata_field = 'metadata: { facebook: { type: post } }'

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
" "$TEXT" "$CHANNEL_ID" "$MODE" "${DUE_AT:-}" "$PLATFORM" "$BUFFER_API_KEY")

# Parse response: union type — PostActionSuccess has .post; all errors have .message
echo "$RESPONSE" | python3 -c "
import json, sys

try:
    data = json.load(sys.stdin)
except Exception as e:
    print(f'Error parsing API response: {e}', file=sys.stderr)
    sys.exit(1)

# Top-level GraphQL errors (schema/network level)
top_errors = data.get('errors', [])
if top_errors:
    for e in top_errors:
        print(e.get('message', str(e)), file=sys.stderr)
    sys.exit(1)

result = data.get('data', {}).get('createPost', {})

# Union error types all have a 'message' field, no 'post'
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
