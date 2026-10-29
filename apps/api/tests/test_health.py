"""Tests for the EriWatch FastAPI /health endpoint and JSON logging."""

import json
import logging

from fastapi.testclient import TestClient

from eriwatch_api.config import Settings
from eriwatch_api.logging_config import JsonFormatter
from eriwatch_api.main import create_app


def test_health_endpoint_returns_ok() -> None:
    """Verify /health returns 200 OK with service metadata and X-Request-ID header."""
    settings = Settings(environment="test", log_level="INFO")
    client = TestClient(create_app(settings=settings))

    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "EriWatch API"
    assert payload["version"] == "0.1.0"
    assert payload["environment"] == "test"
    assert "timestamp" in payload
    assert "X-Request-ID" in response.headers


def test_json_formatter_outputs_valid_json() -> None:
    """Verify structured logger formats LogRecord as valid JSON."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="eriwatch.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Health check executed for tank %s",
        args=("TN-CGL-001",),
        exc_info=None,
    )
    rendered = formatter.format(record)
    parsed = json.loads(rendered)
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "eriwatch.test"
    assert parsed["message"] == "Health check executed for tank TN-CGL-001"
    assert "timestamp" in parsed
