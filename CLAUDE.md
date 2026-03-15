# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Infrastructure-only setup for running [Evolution API](https://github.com/EvolutionAPI/evolution-api) (a WhatsApp API built on Baileys) via Docker Compose. There is no application source code here — only configuration files.

## Stack

- **Evolution API** — `atendai/evolution-api:latest`, exposed on port `8080`
- **PostgreSQL 16** — primary database, exposed on host port `5433` (internal `5432`)
- **Redis 7** — cache layer, exposed on port `6379`

## Common commands

```bash
# Start all services
docker compose up -d

# Stop and remove containers (data volumes are preserved)
docker compose down

# Restart only the API (e.g. after .env changes)
docker compose up -d --force-recreate evolution-api

# Follow API logs
docker logs -f evolution-api

# Check container health
docker compose ps
```

## Environment configuration

All configuration lives in `.env`, loaded by `docker-compose.yml` via `env_file`. The main variables to set before first run:

- `AUTHENTICATION_API_KEY` — master API key for all requests
- `AUTHENTICATION_JWT_SECRET` — JWT signing secret
- `SERVER_URL` — public URL of the API (used in webhook callbacks)

Generate secrets with: `openssl rand -hex 32`

## Known issues / gotchas

- **`CONFIG_SESSION_PHONE_VERSION`** must be left **empty**. Hardcoding a version string (e.g. `2.3000.1015901307`) is a confirmed cause of QR code generation failures. See [#1900](https://github.com/EvolutionAPI/evolution-api/issues/1900).
- **`DATABASE_CONNECTION_URI`** must use port `5432` (internal container port), not `5433` (the host-mapped port). Inter-container traffic always uses the internal port.
- When creating an instance with a `number` field, Evolution API uses phone number pairing — no QR code is generated. Omit `number` to get a QR code.
