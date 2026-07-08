import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def test_quality_event_status_and_ingest_flow():
    with TestClient(app) as client:
        signin = client.post(
            "/api/v1/auth/signin",
            json={"email": "operator@linewatch.local", "device_id": "pytest-device"},
        )
        assert signin.status_code == 200
        assert signin.json()["access_token"]

        lines = client.get("/api/v1/lines")
        assert lines.status_code == 200
        assert lines.json()[0]["id"] == "line-a"

        events = client.get("/api/v1/quality-events")
        assert events.status_code == 200
        event = events.json()[0]
        assert event["status"] in {"open", "acknowledged", "resolved"}

        patched = client.patch(
            f"/api/v1/quality-events/{event['id']}/status",
            json={"status": "resolved", "actor_id": "user-operator", "memo": "verified"},
        )
        assert patched.status_code == 200
        assert patched.json()["status"] == "resolved"

        ingested = client.post("/api/v1/events/ingest", json={"machine_id": "cam-01", "value": 91})
        assert ingested.status_code == 200
        assert ingested.json()["severity"] == "critical"
