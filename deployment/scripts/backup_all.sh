#!/usr/bin/env bash
# Back up every tenant database (one pg_dump per tenant).
set -euo pipefail

ODOO_CONTAINER="${ODOO_CONTAINER:-deployment-odoo-1}"
OUT="${BACKUP_DIR:-/home/ubuntu/backups}/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUT"

DBS=$(docker exec "$ODOO_CONTAINER" psql -U everjust -tAc \
  "SELECT datname FROM pg_database WHERE datistemplate=false AND datname NOT IN ('postgres','control');")

for db in $DBS; do
  echo "Backing up $db"
  docker exec "$ODOO_CONTAINER" pg_dump -U everjust "$db" | gzip > "$OUT/${db}.sql.gz"
done

echo "Backups written to $OUT"
