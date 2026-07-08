from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from tortoise.contrib.fastapi import register_tortoise

from app.auth import issue_tokens, refresh_tokens
from app.models import ProductionLine, RefreshToken, User
from app.schemas import (
    IngestRequest,
    LineResponse,
    LogoutRequest,
    QualityEventResponse,
    RefreshRequest,
    SensorPointResponse,
    SigninRequest,
    StatusPatch,
    TokenResponse,
)
from app.seed import seed_data
from app.services import ingest_event, list_quality_events, sensor_series, to_quality_event_response, update_quality_event_status
from app.models import QualityEvent

app = FastAPI(title="LineWatch API", version="0.1.0")

register_tortoise(
    app,
    db_url="sqlite://:memory:",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.on_event("startup")
async def startup() -> None:
    await seed_data()


@app.post("/api/v1/auth/signin", response_model=TokenResponse)
async def signin(payload: SigninRequest) -> TokenResponse:
    user, _ = await User.get_or_create(id="user-operator", defaults={"email": payload.email})
    return TokenResponse(**await issue_tokens(user, payload.device_id))


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest) -> TokenResponse:
    tokens = await refresh_tokens(payload.user_id, payload.device_id, payload.refresh_token)
    if not tokens:
        raise HTTPException(status_code=401, detail="invalid refresh token")
    return TokenResponse(**tokens)


@app.post("/api/v1/auth/logout")
async def logout(payload: LogoutRequest) -> dict[str, bool]:
    await RefreshToken.filter(user_id=payload.user_id, device_id=payload.device_id).delete()
    return {"ok": True}


@app.get("/api/v1/lines", response_model=list[LineResponse])
async def lines() -> list[LineResponse]:
    return [LineResponse(id=line.id, name=line.name, plant=line.plant, status=line.status) for line in await ProductionLine.all()]


@app.get("/api/v1/quality-events", response_model=list[QualityEventResponse])
async def quality_events(
    lineId: Optional[str] = None,
    status: Optional[str] = None,
    cursor: Optional[str] = None,
) -> list[QualityEventResponse]:
    return await list_quality_events(lineId, status)


@app.get("/api/v1/quality-events/{event_id}", response_model=QualityEventResponse)
async def quality_event(event_id: str) -> QualityEventResponse:
    return to_quality_event_response(await QualityEvent.get(id=event_id))


@app.patch("/api/v1/quality-events/{event_id}/status", response_model=QualityEventResponse)
async def patch_status(event_id: str, payload: StatusPatch) -> QualityEventResponse:
    return await update_quality_event_status(event_id, payload.status, payload.actor_id, payload.memo)


@app.post("/api/v1/events/ingest", response_model=QualityEventResponse)
async def ingest(payload: IngestRequest) -> QualityEventResponse:
    return await ingest_event(payload)


@app.get("/api/v1/machines/{machine_id}/sensor-series", response_model=list[SensorPointResponse])
async def machine_sensor_series(
    machine_id: str,
    from_: Optional[str] = Query(default=None, alias="from"),
    to: Optional[str] = None,
) -> list[SensorPointResponse]:
    return await sensor_series(machine_id)
