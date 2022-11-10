import os
import json
import logging
import http.client
from enum import Enum
from typing import Dict
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager

_logger = None

TELEMETRY_SUBSCRIBER_PORT = 1060
LUMIGO_EXTENSION_NAME = "telemetry"
HEADERS_ID_KEY = "Lambda-Extension-Identifier"
HEADERS_NAME_KEY = "Lambda-Extension-Name"


def get_logger():
    global _logger
    if not _logger:
        _logger = logging.getLogger("lambda-telemetry-handler")
        handler = logging.StreamHandler()
        if os.environ.get("LOG_SHIPPER_DEBUG", "").lower() == "true":
            _logger.setLevel(logging.DEBUG)
            handler.setLevel(logging.DEBUG)
        _logger.addHandler(handler)
    return _logger


def lambda_service():
    return http.client.HTTPConnection(os.environ["AWS_LAMBDA_RUNTIME_API"])


@contextmanager
def never_fail(part_name: str = ""):
    try:
        yield
    except Exception as e:
        get_logger().exception(
            f"An exception occurred in a never-fail code '{part_name}'", exc_info=e
        )


class LogType(Enum):
    START = "START"
    END = "END"
    REPORT = "REPORT"
    FUNCTION = "FUNCTION"
    RUNTIME_DONE = "RUNTIME_DONE"
    OTHER = "OTHER"

    @staticmethod
    def parse(record_type) -> "LogType":
        if record_type == "platform.start":
            return LogType.START
        elif record_type == "platform.end":
            return LogType.END
        elif record_type == "platform.report":
            return LogType.REPORT
        elif record_type == "platform.runtimeDone":
            return LogType.RUNTIME_DONE
        elif record_type == "function":
            return LogType.FUNCTION
        elif record_type in (
            "platform.initStart",
            "platform.telemetrySubscription",
            "platform.initRuntimeDone",
            "platform.runtimeDone",
            "platform.initReport",
            "platform.logsSubscription",
            "platform.extension",
            "platform.fault",
        ):
            return LogType.OTHER
        raise ValueError(f"Unknown record type: {record_type}")


@dataclass(frozen=True)
class TelemetryRecord:
    record_type: LogType
    record_time: datetime
    record: str
    raw: dict

    @staticmethod
    def parse(record: Dict[str, str]) -> "TelemetryRecord":
        return TelemetryRecord(
            record_type=LogType.parse(record["type"]),
            record_time=datetime.fromisoformat(record["time"][:-1]),
            record=json.dumps(record["record"]),
            raw=record,
        )
