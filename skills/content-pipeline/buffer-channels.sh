#!/usr/bin/env bash
# Fetch Buffer channel IDs and names
# Usage: ./buffer-channels.sh
# Requires: BUFFER_API_KEY environment variable

set -euo pipefail

if [[ -z "${BUFFER_API_KEY:-}" ]]; then
  echo "Error: BUFFER_API_KEY not set" >&2
  exit 1
fi

# Fetch org ID dynamically
ORG_ID=$(curl -s -X POST https://api.buffer.com \
  -H "Authorization: Bearer ${BUFFER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ account { currentOrganization { id } } }"}' | python3 -c "
import json, sys
print(json.load(sys.stdin)['data']['account']['currentOrganization']['id'])
")

if [[ -z "$ORG_ID" ]]; then
  echo "Error: could not fetch organization ID" >&2
  exit 1
fi

curl -s -X POST https://api.buffer.com \
  -H "Authorization: Bearer ${BUFFER_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"query { channels(input: { organizationId: \\\"${ORG_ID}\\\" }) { id name service } }\"}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
channels = data.get('data', {}).get('channels', [])
for ch in channels:
    print(f\"{ch['service']:12s} {ch['id']:28s} {ch['name']}\")
"
