# Production Deployment

This deployment runs the frontend, backend, and PostgreSQL together with Docker Compose.

## Server Requirements

- Linux VPS with Docker and Docker Compose plugin installed.
- Open inbound port `80`.
- Optional but recommended: a domain pointed to the server IP.

## 1. Copy Project To Server

Copy the whole project folder to the server, for example:

```bash
scp -r smartsystem-new-report-updates user@SERVER_IP:/opt/smartsystem
ssh user@SERVER_IP
cd /opt/smartsystem/smartsystem-new-report-updates
```

## 2. Create Production Environment

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Set:

- `POSTGRES_PASSWORD` to a strong database password.
- `DATABASE_URL` with the same database password.
- `SECRET_KEY` to a long random string.
- `CORS_ORIGINS` to your real domain, for example `["https://plants.example.com"]`.
- SMTP values if email notifications should work.

## 3. Start The App

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

The app will be available at:

```text
http://SERVER_IP
```

Backend health check:

```text
http://SERVER_IP/health
```

The frontend calls the backend through the same public host using `/api/v1`, so the backend does not need a separate public port.

## Database

PostgreSQL is not exposed to the internet in production. It is reachable only inside the Docker network as `postgres:5432`.

Data is persisted in the Docker volume:

```text
postgres_data
```

Do not run `docker compose down -v` on the server unless you intentionally want to delete the database.

## Useful Commands

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml down
```

## Backups

Create a database backup:

```bash
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
```

Restore from a backup:

```bash
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T postgres psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

## HTTPS

For a real public demo, put HTTPS in front of this app. Simple options:

- Cloudflare tunnel.
- Nginx Proxy Manager.
- Caddy reverse proxy with automatic Let's Encrypt certificates.

With HTTPS enabled, update `.env.prod`:

```env
CORS_ORIGINS=["https://your-domain.com"]
```
