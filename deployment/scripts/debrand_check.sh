#!/usr/bin/env bash
# Scan a running tenant for any residual upstream branding leaks.
# Usage: ./debrand_check.sh <subdomain>
set -euo pipefail

SUB="${1:?subdomain required}"
URL="https://${SUB}.everjust.app"

echo "Scanning ${URL} for upstream branding references..."
HITS=$(curl -sk "$URL/web/login" | grep -io "odoo" | wc -l | tr -d ' ')

if [ "$HITS" -gt 0 ]; then
  echo "WARNING: found ${HITS} reference(s) on the login page. Review debrand module overrides."
  exit 1
fi
echo "Clean: no upstream references found on login page."
