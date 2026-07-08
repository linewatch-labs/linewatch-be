# LineWatch BE

FastAPI + Tortoise ORM REST API for LineWatch. No GraphQL.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

OpenAPI: `http://127.0.0.1:8000/docs`

## Checks

```bash
python scripts/verify_api.py
```

## API

- `POST /api/v1/auth/signin`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/lines`
- `GET /api/v1/quality-events?lineId=&status=&cursor=`
- `GET /api/v1/quality-events/{id}`
- `PATCH /api/v1/quality-events/{id}/status`
- `POST /api/v1/events/ingest`
- `GET /api/v1/machines/{id}/sensor-series?from=&to=`

## Data Model

- `users`
- `refresh_tokens`: hashed token, unique `user + device_id`
- `production_lines`
- `machines`
- `sensor_events`
- `inspection_results`
- `quality_events`
- `action_logs`

## Demo Backend Adaptation

The demo backend's token hardening is adapted to Python REST:

- refresh token is stored as SHA-256 hash
- `user + device_id` is unique through Tortoise `unique_together`
- refresh endpoint compares only token hash
- logout deletes the device refresh token

Phone/Kakao flows are intentionally skipped for this portfolio MVP.

## Portfolio Evidence

LineWatch stores line, machine, sensor, AI inspection, quality event, and action log concepts behind a REST API. The ingest endpoint turns mock sensor/AI data into an operator-facing quality event.

## Resume Bullets

- Built a FastAPI + Tortoise ORM REST API that normalizes manufacturing sensor and Inspection AI inputs into quality events.
- Adapted a demo auth/token architecture into Python REST with hashed refresh tokens and per-device logout.
- Added mock seed data and verification flow covering signin, event listing, status update, sensor series, and ingest.
