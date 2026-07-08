from datetime import datetime, timedelta, timezone

from app.models import ActionLog, Machine, ProductionLine, QualityEvent, SensorEvent, User


async def seed_data() -> None:
    operator, _ = await User.get_or_create(id="user-operator", defaults={"email": "operator@linewatch.local"})
    line, _ = await ProductionLine.get_or_create(
        id="line-a",
        defaults={"name": "Line A", "plant": "Busan Plant", "status": "warning"},
    )
    await ProductionLine.get_or_create(id="line-b", defaults={"name": "Line B", "plant": "Busan Plant", "status": "running"})
    machine, _ = await Machine.get_or_create(
        id="cam-01",
        defaults={
            "line": line,
            "name": "Vision Cam 01",
            "type": "inspection",
            "threshold_profile": {"vibration": 80, "defect_score": 0.9},
        },
    )
    press, _ = await Machine.get_or_create(
        id="press-07",
        defaults={"line": line, "name": "Press 07", "type": "pressure", "threshold_profile": {"pressure": 65}},
    )
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    for index, value in enumerate([38, 41, 63, 81, 76, 88]):
        await SensorEvent.get_or_create(
            id=f"seed-cam-{index}",
            defaults={"machine": machine, "time": now - timedelta(minutes=5 - index), "metric": "vibration", "value": value, "unit": "hz"},
        )
    for index, value in enumerate([42, 45, 49, 66, 71, 68]):
        await SensorEvent.get_or_create(
            id=f"seed-press-{index}",
            defaults={"machine": press, "time": now - timedelta(minutes=5 - index), "metric": "pressure", "value": value, "unit": "bar"},
        )
    event, _ = await QualityEvent.get_or_create(
        id="qe-1001",
        defaults={
            "line": line,
            "machine": machine,
            "severity": "critical",
            "status": "open",
            "reason": "AI defect score exceeded threshold after vibration spike",
            "defect_score": 0.93,
            "opened_at": now,
        },
    )
    await ActionLog.get_or_create(
        id="act-1",
        defaults={"quality_event": event, "actor": operator, "action": "open", "memo": "seeded portfolio event"},
    )
