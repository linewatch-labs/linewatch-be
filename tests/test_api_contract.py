from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_api_exposes_quality_event_routes() -> None:
    main = (ROOT / "app/main.py").read_text()
    services = (ROOT / "app/services.py").read_text()

    assert '"/api/v1/lines"' in main
    assert '"/api/v1/quality-events"' in main
    assert '"/api/v1/events/ingest"' in main
    assert "sensor_series" in services
