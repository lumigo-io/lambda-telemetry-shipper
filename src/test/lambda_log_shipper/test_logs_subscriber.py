import pytest
import http
import json
from unittest.mock import Mock
from http.server import HTTPServer
from io import BytesIO

from lambda_telemetry_shipper.telemetry_handlers.logs_manager import LogsManager
from lambda_telemetry_shipper.telemetry_subscriber import (
    TelemetryHttpRequestHandler,
    subscribe_to_telemetry_api,
)
from lambda_telemetry_shipper.utils import TelemetryRecord


@pytest.fixture
def logs_server_mock(monkeypatch):
    class MockRequest:
        def makefile(self, *args, **kwargs):
            return BytesIO(b"POST /")

        def sendall(self, _):
            pass

    handler = TelemetryHttpRequestHandler(MockRequest(), ("0.0.0.0", 8888), Mock())
    monkeypatch.setattr(handler, "headers", {"Content-Length": "1000"}, False)
    return handler


def test_subscribe_to_logs(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(http.client, "HTTPConnection", mock)
    monkeypatch.setattr(HTTPServer, "serve_forever", lambda: None)
    monkeypatch.setattr(HTTPServer, "server_bind", lambda _: None)

    subscribe_to_telemetry_api("eid")

    expected = '{"schemaVersion": "2022-07-01", "destination": {"protocol": "HTTP", "URI": "http://sandbox.localdomain:1060"}, "types": ["platform", "function"]}'
    mock("127.0.0.1").request.assert_called_once_with(
        "PUT",
        "/2022-07-01/telemetry",
        expected,
        headers={
            "Content-Type": "application/json",
            "Lambda-Extension-Identifier": "eid",
        },
    )


def test_do_POST_happy_flow(logs_server_mock, monkeypatch, raw_record):
    monkeypatch.setattr(
        logs_server_mock,
        "rfile",
        BytesIO(b"[" + json.dumps(raw_record).encode() + b"]"),
        False,
    )
    logs_server_mock.do_POST()

    logs_manager = LogsManager.get_singleton()
    assert logs_manager.pending_logs == [TelemetryRecord.parse(raw_record)]


def test_do_POST_exception(logs_server_mock, monkeypatch, raw_record, caplog):
    monkeypatch.setattr(logs_server_mock, "rfile", BytesIO(b"no json"), False)
    logs_server_mock.do_POST()

    assert caplog.records[-1].exc_info[0].__name__ == "JSONDecodeError"
