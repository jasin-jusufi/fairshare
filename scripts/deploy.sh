#!/usr/bin/env bash
# Triggers a Render deploy of a specific container image via the service deploy hook.
set -euo pipefail

: "${RENDER_DEPLOY_HOOK_URL:?RENDER_DEPLOY_HOOK_URL is required}"
: "${IMAGE:?IMAGE is required}"

image_lower=$(echo "$IMAGE" | tr '[:upper:]' '[:lower:]')
encoded=$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$image_lower")

echo "Deploying ${image_lower} to Render"
curl -fsS -X POST "${RENDER_DEPLOY_HOOK_URL}&imgURL=${encoded}"
echo
