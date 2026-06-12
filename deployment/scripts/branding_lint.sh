#!/usr/bin/env bash
# Static branding lint: fail if user-facing source files reintroduce
# upstream "Odoo" references. Framework identifiers (imports, XML root
# tags, @odoo-module pragmas, scss variables, i18n catalogs, vendored
# READMEs/license headers) are allowed — they are never shown to users.
# Usage: ./branding_lint.sh   (run from anywhere inside the repo)
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

LEAKS=$(grep -rn --include='*.xml' --include='*.js' --include='*.html' \
    --include='*.webmanifest' --include='*.css' --include='*.scss' \
    -i 'odoo' addons control-plane \
  | grep -v '/i18n/' \
  | grep -v '/readme/' \
  | grep -viE 'odoo-module|@odoo/owl|@odoo/hoot|^\s*[^:]+:[0-9]+:\s*</?odoo|odoo\.define' \
  | grep -vE 'odoo\.csrf_token|odoo\.debug|"odoo_account"' \
  | grep -vE '<(/)?odoo( |>|$)' \
  | grep -vE '\$o-brand-odoo' \
  | grep -vE "xpath.*odoo\.com" \
  | grep -vE '^\S+:[0-9]+:\s*(//|<!--|#|\*)' \
  || true)

if [ -n "$LEAKS" ]; then
  echo "Upstream branding leaks found in user-facing files:"
  echo "$LEAKS"
  exit 1
fi
echo "Branding lint passed: no user-facing upstream references."
