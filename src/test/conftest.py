import pytest

from lambda_telemetry_shipper.telemetry_handlers.logs_manager import LogsManager
from lambda_telemetry_shipper.utils import TelemetryRecord


@pytest.fixture(autouse=True)
def log_all(monkeypatch, caplog):
    monkeypatch.setenv("LOG_SHIPPER_DEBUG", "true")


@pytest.fixture(autouse=True)
def extension_env(monkeypatch):
    monkeypatch.setenv("AWS_LAMBDA_RUNTIME_API", "127.0.0.1")


@pytest.fixture(autouse=True)
def clear_logs_manager(monkeypatch):
    LogsManager._singleton = None


@pytest.fixture
def raw_record():
    return {
        "time": "2020-11-02T12:02:04.575Z",
        "type": "function",
        "record": {"requestId": "1-2-3-4", "version": "$LATEST"},
    }


@pytest.fixture
def record(raw_record):
    return TelemetryRecord.parse(raw_record)
