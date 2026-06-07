FROM python:3.12-slim

WORKDIR /app

# Docker CLI so the control plane can run `docker exec` against the Odoo
# container for tenant database provisioning.
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
