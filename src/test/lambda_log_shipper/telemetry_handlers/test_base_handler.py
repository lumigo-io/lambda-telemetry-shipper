from lambda_telemetry_shipper.telemetry_handlers.base_handler import TelemetryHandler
from lambda_telemetry_shipper.utils import TelemetryRecord


def test_get_singleton():
    class TestTelemetryHandler(TelemetryHandler):
        def should_handle(self, record: TelemetryRecord):
            pass

        def handle(self, record: TelemetryRecord):
            pass

    result = TestTelemetryHandler.get_singleton()
    assert result == TestTelemetryHandler.get_singleton()
