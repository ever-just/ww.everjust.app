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

echo "Setting admin login + password -> ${EMAIL}"
printf "env['res.users'].browse(2).write({'login': %r, 'password': %r}); env.cr.commit()\n" "$EMAIL" "$PASS" \
  | docker exec -i "$ODOO_CONTAINER" odoo shell -d "$SUB" --no-http

echo "Configuring outgoing mail (Resend -> ${MAIL_DOMAIN:-everjust.co})"
docker exec -i "$ODOO_CONTAINER" odoo shell -d "$SUB" --no-http <<'PYEOF'
import os
key = os.environ.get('RESEND_API_KEY')
domain = os.environ.get('MAIL_DOMAIN', 'everjust.co')
Server = env['ir.mail_server']
if key and not Server.search([]):
    Server.create({
        'name': 'Resend (EVERJUST.APP)', 'smtp_host': 'smtp.resend.com',
        'smtp_port': 465, 'smtp_encryption': 'ssl', 'smtp_authentication': 'login',
        'smtp_user': 'resend', 'smtp_pass': key, 'from_filter': domain, 'sequence': 5,
    })
Dom = env['mail.alias.domain']
dom = Dom.search([('name', '=', domain)], limit=1) or Dom.create({
    'name': domain, 'bounce_alias': 'bounce', 'catchall_alias': 'catchall', 'default_from': 'noreply',
})
for company in env['res.company'].search([]):
    company.alias_domain_id = dom.id
env['ir.config_parameter'].sudo().set_param('mail.catchall.domain', domain)
env['ir.config_parameter'].sudo().set_param('mail.default.from', 'noreply')
env.cr.commit()
PYEOF

echo "Done. Tenant live at https://${SUB}.everjust.app"
