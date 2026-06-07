#!/usr/bin/env bash
# Manually provision an EVERJUST.APP tenant (Phase 1 — before full automation).
# Usage: ./provision_tenant.sh <subdomain> <admin_email> <admin_password>
set -euo pipefail

SUB="${1:?subdomain required}"
EMAIL="${2:?admin email required}"
PASS="${3:?admin password required}"
ODOO_CONTAINER="${ODOO_CONTAINER:-deployment-odoo-1}"

echo "Provisioning tenant: ${SUB}.everjust.app"

docker exec "$ODOO_CONTAINER" odoo \
  -d "$SUB" \
  -i base,everjust_brand,everjust_theme \
  --load-language=en_US \
  --stop-after-init --no-http

echo "Setting admin login -> ${EMAIL}"
docker exec "$ODOO_CONTAINER" psql -U everjust -d "$SUB" \
  -c "UPDATE res_users SET login='${EMAIL}' WHERE id=2;"

echo "Setting admin password"
printf "env['res.users'].browse(2).write({'password': %r}); env.cr.commit()\n" "$PASS" \
  | docker exec -i "$ODOO_CONTAINER" odoo shell -d "$SUB" --no-http

echo "Done. Tenant live at https://${SUB}.everjust.app"
