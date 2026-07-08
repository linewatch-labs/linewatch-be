import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def main() -> None:
    with TestClient(app) as client:
        signin = client.post("/api/v1/auth/signin", json={"email": "operator@linewatch.local", "device_id": "verify"}).json()
        assert signin["access_token"]
        assert signin["refresh_token"]
        assert client.get("/api/v1/lines").json()[0]["id"] == "line-a"
        events = client.get("/api/v1/quality-events").json()
        assert events[0]["machineId"] == "cam-01"
        patched = client.patch(f"/api/v1/quality-events/{events[0]['id']}/status", json={"status": "acknowledged"}).json()
        assert patched["status"] == "acknowledged"
        series = client.get("/api/v1/machines/cam-01/sensor-series").json()
        assert len(series) >= 6
        ingested = client.post("/api/v1/events/ingest", json={"machine_id": "cam-01", "value": 91}).json()
        assert ingested["severity"] == "critical"
    print("api verify ok")


if __name__ == "__main__":
    main()
