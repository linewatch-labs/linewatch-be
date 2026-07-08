from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.models import ActionLog, InspectionResult, Machine, QualityEvent, SensorEvent, User
from app.schemas import IngestRequest, QualityEventResponse, SensorPointResponse


def to_quality_event_response(event: QualityEvent) -> QualityEventResponse:
    return QualityEventResponse(
        id=event.id,
        lineId=event.line_id,
        machineId=event.machine_id,
        severity=event.severity,
        status=event.status,
        reason=event.reason,
        defectScore=event.defect_score,
        openedAt=event.opened_at,
    )


async def list_quality_events(line_id: Optional[str] = None, status: Optional[str] = None) -> list[QualityEventResponse]:
    query = QualityEvent.all().order_by("-opened_at")
    if line_id:
        query = query.filter(line_id=line_id)
    if status:
        query = query.filter(status=status)
    return [to_quality_event_response(event) for event in await query]


async def update_quality_event_status(event_id: str, status: str, actor_id: str, memo: str) -> QualityEventResponse:
    event = await QualityEvent.get(id=event_id)
    event.status = status
    if status == "resolved":
        event.closed_at = datetime.now(timezone.utc)
    await event.save()
    await ActionLog.create(id=str(uuid4()), quality_event=event, actor=await User.get(id=actor_id), action=status, memo=memo)
    return to_quality_event_response(event)


async def ingest_event(payload: IngestRequest) -> QualityEventResponse:
    machine = await Machine.get(id=payload.machine_id).prefetch_related("line")
    now = datetime.now(timezone.utc)
    await SensorEvent.create(
        id=str(uuid4()),
        machine=machine,
        time=now,
        metric=payload.metric,
        value=payload.value,
        unit=payload.unit,
    )
    await InspectionResult.create(
        id=str(uuid4()),
        machine=machine,
        captured_at=now,
        defect_score=payload.defect_score,
        label=payload.label,
    )
    severity = "critical" if payload.defect_score >= 0.9 or payload.value >= 85 else "high"
    event = await QualityEvent.create(
        id=str(uuid4()),
        line=machine.line,
        machine=machine,
        severity=severity,
        status="open",
        reason=f"{payload.metric} {payload.value}{payload.unit} with AI label {payload.label}",
        defect_score=payload.defect_score,
        opened_at=now,
    )
    return to_quality_event_response(event)


async def sensor_series(machine_id: str) -> list[SensorPointResponse]:
    events = await SensorEvent.filter(machine_id=machine_id).order_by("time").limit(40)
    return [SensorPointResponse(time=event.time.strftime("%H:%M"), value=event.value) for event in events]
