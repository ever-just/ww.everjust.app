#!/usr/bin/env bash
# Scan a running tenant (and the platform site) for residual upstream
# branding leaks.
# Usage: ./debrand_check.sh <subdomain>
set -euo pipefail

SUB="${1:?subdomain required}"
BASE_DOMAIN="${BASE_DOMAIN:-everjust.app}"
TENANT_URL="https://${SUB}.${BASE_DOMAIN}"
PLATFORM_URL="https://${BASE_DOMAIN}"

FAIL=0

check_url() {
  local url="$1"
  local hits
  hits=$(curl -sk "$url" | grep -io "odoo" | wc -l | tr -d ' ')
  if [ "$hits" -gt 0 ]; then
    echo "LEAK: ${hits} upstream reference(s) at ${url}"
    FAIL=1
  else
    echo "clean: ${url}"
  fi
}

echo "Scanning tenant ${TENANT_URL} ..."
check_url "${TENANT_URL}/web/login"
check_url "${TENANT_URL}/web/webmanifest"

echo "Scanning platform ${PLATFORM_URL} ..."
for path in / /signup /signin /manifest.webmanifest; do
  check_url "${PLATFORM_URL}${path}"
done

if [ "$FAIL" -ne 0 ]; then
  echo "WARNING: upstream branding leaks found. Review everjust_brand overrides."
  exit 1
fi
echo "All scanned pages are clean."
