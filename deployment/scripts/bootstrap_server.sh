#!/bin/bash
# EVERJUST.APP - Server Bootstrap Script
# Run once on fresh Ubuntu 24.04 EC2 instance
set -euo pipefail

DOMAIN="everjust.app"
EMAIL="admin@everjust.app"

echo "=== EVERJUST.APP Bootstrap ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install dependencies
apt-get install -y \
  curl git unzip \
  docker.io docker-compose-v2 \
  nginx certbot python3-certbot-nginx python3-pip \
  fail2ban ufw

# Install GoDaddy DNS certbot plugin via pip
pip3 install certbot-dns-godaddy --break-system-packages

# Enable Docker
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# Firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Clone repo
mkdir -p /opt/everjust
cd /opt/everjust
git clone https://github.com/ever-just/ww.everjust.app.git platform
cd platform

# Copy env file (to be filled in)
if [ ! -f .env ]; then
  cp .env.example .env
  echo "NOTE: Edit /opt/everjust/platform/.env before starting services"
fi

# Create GoDaddy certbot credentials file
mkdir -p /etc/letsencrypt/godaddy
cat > /etc/letsencrypt/godaddy/credentials.ini <<'CREDS'
certbot_dns_godaddy:dns_godaddy_secret = 8tnPW2eZRuM3fBXkKwFW8L
certbot_dns_godaddy:dns_godaddy_key = gHKhkafh4D1G_8WqL3FbhrwxYrprHqrREex
CREDS
chmod 600 /etc/letsencrypt/godaddy/credentials.ini

# Wildcard SSL via DNS-01 challenge
certbot certonly \
  --authenticator dns-godaddy \
  --dns-godaddy-credentials /etc/letsencrypt/godaddy/credentials.ini \
  --dns-godaddy-propagation-seconds 60 \
  -d "${DOMAIN}" \
  -d "*.${DOMAIN}" \
  --email "${EMAIL}" \
  --agree-tos \
  --non-interactive

# Install nginx config
cp /opt/everjust/platform/deployment/nginx/everjust.conf /etc/nginx/sites-available/everjust.conf
ln -sf /etc/nginx/sites-available/everjust.conf /etc/nginx/sites-enabled/everjust.conf
rm -f /etc/nginx/sites-enabled/default

# Validate and reload nginx
nginx -t
systemctl enable nginx
systemctl reload nginx

# Auto-renew cron
echo "0 3 * * * root certbot renew --quiet && systemctl reload nginx" > /etc/cron.d/certbot-renew

echo ""
echo "=== Bootstrap complete ==="
echo "1. Edit /opt/everjust/platform/.env with your secrets"
echo "2. Run: cd /opt/everjust/platform && docker compose up -d"
echo "3. Provision TCSW tenant: bash deployment/scripts/provision_tenant.sh tcsw"
