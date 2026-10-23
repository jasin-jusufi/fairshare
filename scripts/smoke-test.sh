#!/usr/bin/env bash
# Waits for the deployed service to report healthy and checks the API answers.
set -euo pipefail

: "${APP_URL:?APP_URL is required}"
url="${APP_URL%/}"

for attempt in $(seq 1 40); do
  if curl -fsS "${url}/health" | grep -q healthy; then
    echo "Healthy after ${attempt} attempt(s)"
    curl -fsS "${url}/households" > /dev/null
    curl -fsS "${url}/openapi.json" | grep -q "FairShare API"
    echo "Smoke test passed"
    exit 0
  fi
  sleep 15
done

echo "Service did not become healthy at ${url}" >&2
exit 1
