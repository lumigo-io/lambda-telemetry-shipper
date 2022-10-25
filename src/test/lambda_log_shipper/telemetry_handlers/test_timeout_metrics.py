import boto3
import datetime

import pytest as pytest
import pytz
from moto import mock_cloudwatch

from lambda_telemetry_shipper.configuration import Configuration
from lambda_telemetry_shipper.telemetry_handlers.timeout_metrics import (
    TimeoutMetricHandler,
)
from lambda_telemetry_shipper.utils import TelemetryRecord, LogType


now = datetime.datetime.now(tz=pytz.utc)


@pytest.mark.parametrize(
    "record, expected",
    [
        (TelemetryRecord(LogType.START, now, "log", {}), False),  # not RUNTIME_DONE
        (TelemetryRecord(LogType.RUNTIME_DONE, now, "log", {}), False),  # not json
        (TelemetryRecord(LogType.RUNTIME_DONE, now, "{", {}), False),  # malformed json
        (
            TelemetryRecord(LogType.RUNTIME_DONE, now, "{}", {}),
            False,
        ),  # not the right status
        (
            TelemetryRecord(LogType.RUNTIME_DONE, now, '{"status": "timeout"}', {}),
            True,
        ),  # happy flow
    ],
)
def test_should_handle(record, expected):
    assert TimeoutMetricHandler.get_singleton().should_handle(record) is expected


@mock_cloudwatch
def test_handle(monkeypatch):
    monkeypatch.setattr(Configuration, "timeout_target_metric", "my_metric")
    record = TelemetryRecord(LogType.RUNTIME_DONE, now, '{"status": "timeout"}', {})
    TimeoutMetricHandler.get_singleton().handle(record)
    TimeoutMetricHandler.get_singleton().handle(record)

    data = boto3.client("cloudwatch").get_metric_data(
        StartTime=now - datetime.timedelta(minutes=2),
        EndTime=now + datetime.timedelta(minutes=2),
        MetricDataQueries=[
            {
                "Id": "1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "Timeouts",
                        "MetricName": "my_metric",
                    },
                    "Period": 300,
                    "Stat": "Sum",
                },
            }
        ],
    )
    assert data["MetricDataResults"][0]["Values"] == [2.0]
