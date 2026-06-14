#!/usr/bin/env bash
# Post-deploy smoke test for the EVERJUST.APP control-plane / marketing site.
# Hits the public funnel endpoints on a live host and checks status + a couple
# of invariants. Exits non-zero on the first failure.
#
# Usage:
#   ./smoke_test.sh                       # tests https://everjust.app
#   ./smoke_test.sh https://staging.host  # tests another host
set -uo pipefail

BASE="${1:-https://everjust.app}"
FAILED=0

# code PATH [expected_substring]
check() {
  local want="$1" path="$2" needle="${3:-}"
  local body code
  body="$(curl -fsS -m 20 -w $'\n%{http_code}' "$BASE$path" 2>/dev/null)" || { echo "FAIL  $path  (request error)"; FAILED=1; return; }
  code="${body##*$'\n'}"
  body="${body%$'\n'*}"
  if [ "$code" != "$want" ]; then echo "FAIL  $path  (HTTP $code, wanted $want)"; FAILED=1; return; fi
  if [ -n "$needle" ] && ! grep -qiF "$needle" <<<"$body"; then
    echo "FAIL  $path  (missing: $needle)"; FAILED=1; return
  fi
  echo "ok    $path  ($code)"
}

# code PATH must_NOT_contain
check_absent() {
  local want="$1" path="$2" needle="$3" body code
  body="$(curl -fsS -m 20 -w $'\n%{http_code}' "$BASE$path" 2>/dev/null)" || { echo "FAIL  $path  (request error)"; FAILED=1; return; }
  code="${body##*$'\n'}"; body="${body%$'\n'*}"
  if [ "$code" != "$want" ]; then echo "FAIL  $path  (HTTP $code)"; FAILED=1; return; fi
  if grep -qiF "$needle" <<<"$body"; then echo "FAIL  $path  (leaked: $needle)"; FAILED=1; return; fi
  echo "ok    $path  (no '$needle')"
}

echo "Smoke testing $BASE"
echo "── funnel pages ──"
check 200 "/"                  "EVERJUST"
check 200 "/apps"              "One workspace"
check 200 "/apps/inventory"    "Inventory"
check 200 "/pricing"           "flat price"
check 200 "/docs"              "Documentation"
check 200 "/signup"
check 200 "/signin"

echo "── infra / SEO ──"
check 200 "/healthz"
check 200 "/sitemap.xml"       "<urlset"
check 200 "/robots.txt"        "Sitemap:"
check 200 "/manifest.webmanifest"
check 200 "/sw.js"

echo "── API ──"
check 200 "/api/subdomain-check?subdomain=zzqa-smoke-test"

echo "── debrand invariant ──"
check_absent 200 "/"     "Odoo"
check_absent 200 "/apps" "Odoo"

echo
if [ "$FAILED" -ne 0 ]; then echo "SMOKE TEST FAILED"; exit 1; fi
echo "All smoke checks passed."
