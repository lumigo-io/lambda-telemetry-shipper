from datetime import datetime

import pytest

from lambda_telemetry_shipper.utils import never_fail, LogType, TelemetryRecord


def test_never_fail(caplog):
    with never_fail("test"):
        raise ValueError()

    # No exception raised
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].exc_info[0] == ValueError


@pytest.mark.parametrize(
    "record_type, expected",
    [
        ("platform.start", LogType.START),
        ("platform.end", LogType.END),
        ("platform.report", LogType.REPORT),
        ("function", LogType.FUNCTION),
        ("platform.extension", LogType.OTHER),
    ],
)
def test_log_type_parse(record_type, expected):
    assert LogType.parse(record_type) == expected


def test_log_type_parse_unknown():
    with pytest.raises(ValueError):
        LogType.parse("other")


def test_log_record_parse(raw_record):
    record = TelemetryRecord.parse(raw_record)
    assert record.record_type == LogType.FUNCTION
    assert record.record == '{"requestId": "1-2-3-4", "version": "$LATEST"}'
    assert record.record_time == datetime(2020, 11, 2, 12, 2, 4, 575000)
