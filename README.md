# Backup Monitor API

A backend service for registering servers, receiving backup reports and detecting failed or overdue backups. The project is based on a real homelab use case: monitoring weekly backups for services running on Proxmox and Docker.

## Stack

- Python 3.12 and FastAPI
- PostgreSQL and SQLAlchemy 2
- Pydantic validation
- Docker Compose
- Pytest and GitHub Actions

## Features

- Register servers and their expected backup interval.
- Report successful and failed backup jobs.
- Validate timestamps, sizes and failure details.
- Calculate one of four states for every server:
  - `healthy` - the latest backup succeeded and is still current;
  - `overdue` - the latest successful backup is older than the configured interval;
  - `failed` - the most recent backup failed;
  - `missing` - no backup has been reported.
- View recent backup history for each server.
- Get a dashboard summary for all active servers.
- Detect duplicate server names and return an HTTP 409 conflict.
- Run the API and PostgreSQL together with Docker Compose.

## Architecture

```text
Client
  |
  v
FastAPI routers -> validation schemas -> backup status service
  |                                        |
  v                                        v
SQLAlchemy models -----------------> calculated health state
  |
  v
PostgreSQL
```

The backup status calculation is isolated in `app/services.py`, which keeps the business rule testable without starting a database or web server.

## Run with Docker

```bash
docker compose up --build
```

The API will be available at:

- API: `http://localhost:8000`
- Interactive documentation: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

Stop the containers with:

```bash
docker compose down
```

To also delete the local PostgreSQL volume:

```bash
docker compose down -v
```

## Local development

Create a virtual environment and install the development dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

macOS or Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Copy `.env.example` to `.env`, update the database address if needed, then run:

```bash
uvicorn app.main:app --reload
```

## API examples

Register a server:

```bash
curl -X POST http://localhost:8000/api/v1/servers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "proxmox-node-1",
    "host": "10.0.0.10",
    "environment": "homelab",
    "expected_interval_hours": 168
  }'
```

Report a completed backup:

```bash
curl -X POST http://localhost:8000/api/v1/servers/1/backups \
  -H "Content-Type: application/json" \
  -d '{
    "result": "success",
    "started_at": "2026-09-19T01:00:00Z",
    "completed_at": "2026-09-19T01:15:00Z",
    "size_mb": 512.4
  }'
```

Read the dashboard summary:

```bash
curl http://localhost:8000/api/v1/dashboard/summary
```

Example response:

```json
{
  "total_servers": 3,
  "healthy": 1,
  "overdue": 1,
  "failed": 1,
  "missing": 0
}
```

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `POST` | `/api/v1/servers` | Register a server |
| `GET` | `/api/v1/servers` | List servers and calculated backup state |
| `GET` | `/api/v1/servers/{server_id}` | Read one server |
| `POST` | `/api/v1/servers/{server_id}/backups` | Report a backup result |
| `GET` | `/api/v1/servers/{server_id}/backups` | List recent backup reports |
| `GET` | `/api/v1/dashboard/summary` | Count servers by backup state |

## Tests

```bash
pytest
```

The test suite covers the status calculation, timestamp validation, failed-backup validation, duplicate server handling and a complete API flow. GitHub Actions runs the suite for every push and pull request.

## Project scope

This is a portfolio project. It currently uses automatic table creation to keep local setup simple. A production version should add database migrations, authentication, structured logging and external alert delivery.

## Author

Stepan Gridin
