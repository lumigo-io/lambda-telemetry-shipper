from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures.thread import ThreadPoolExecutor
import json

from typing import Dict, List

from lambda_telemetry_shipper.telemetry_handlers.base_handler import TelemetryHandler
from lambda_telemetry_shipper.utils import (
    TELEMETRY_SUBSCRIBER_PORT,
    HEADERS_ID_KEY,
    lambda_service,
    get_logger,
    never_fail,
    TelemetryRecord,
)


TELEMETRY_SUBSCRIPTION_REQUEST = {
    "schemaVersion": "2022-07-01",
    "destination": {
        "protocol": "HTTP",
        "URI": f"http://sandbox.localdomain:{TELEMETRY_SUBSCRIBER_PORT}",
    },
    "types": ["platform", "function"],
}
TIMEOUT_SAFETY_GAP = 0.5


def subscribe_to_telemetry_api(extension_id):
    server = HTTPServer(
        ("0.0.0.0", TELEMETRY_SUBSCRIBER_PORT), TelemetryHttpRequestHandler
    )
    server.server_activate()
    ThreadPoolExecutor().submit(server.serve_forever)

    body = json.dumps(TELEMETRY_SUBSCRIPTION_REQUEST)
    conn = lambda_service()
    conn.request(
        "PUT",
        "/2022-07-01/telemetry",
        body,
        headers={"Content-Type": "application/json", HEADERS_ID_KEY: extension_id},
    )


class TelemetryHttpRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        with never_fail("parse telemetry event"):
            size = int(self.headers.get("Content-Length", "0"))
            records: List[Dict] = json.loads(self.rfile.read(size))
            parsed_records = [TelemetryRecord.parse(r) for r in records]
            for record in parsed_records:
                handle_record(record)
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        # Do not write console logs per request
        return


def handle_record(record: TelemetryRecord) -> None:
    get_logger().debug(f"Handling {record}")
    handlers = [cls.get_singleton() for cls in TelemetryHandler.__subclasses__()]
    for handler in handlers:
        try:
            if handler.should_handle(record):
                handler.handle(record)
        except Exception:
            get_logger().exception(
                f"Exception while handling {handler.__class__.__name__}", exc_info=True
            )
