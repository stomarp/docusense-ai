#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-}"

if [ -z "$API_BASE_URL" ]; then
  echo "Usage: API_BASE_URL=https://your-render-api.onrender.com ./scripts/smoke_production.sh"
  exit 1
fi

echo "Checking health endpoint..."
curl -fsS "$API_BASE_URL/health"
echo
echo "Smoke check passed."
