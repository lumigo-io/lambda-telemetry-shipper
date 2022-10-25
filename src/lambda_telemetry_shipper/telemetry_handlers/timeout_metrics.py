import os
import json

import boto3

from lambda_telemetry_shipper.configuration import Configuration
from lambda_telemetry_shipper.telemetry_handlers.base_handler import TelemetryHandler
from lambda_telemetry_shipper.utils import get_logger, TelemetryRecord, LogType


class TimeoutMetricHandler(TelemetryHandler):
    client = None

    def should_handle(self, record: TelemetryRecord) -> bool:
        if record.record_type != LogType.RUNTIME_DONE:
            return False
        try:
            return json.loads(record.record).get("status") == "timeout"
        except Exception:
            return False

    def handle(self, record: TelemetryRecord) -> None:
        if Configuration.timeout_target_metric:
            get_logger().debug(
                f"Timeout occurred, put metric in {Configuration.timeout_target_metric}"
            )
            if not TimeoutMetricHandler.client:
                TimeoutMetricHandler.client = boto3.client("cloudwatch")
            TimeoutMetricHandler.client.put_metric_data(
                Namespace="Timeouts",
                MetricData=[
                    {
                        "MetricName": Configuration.timeout_target_metric,
                        "Value": 1,
                        "Unit": "Count",
                        "Dimensions": [
                            {
                                "Name": "FunctionName",
                                "Value": os.environ.get(
                                    "AWS_LAMBDA_FUNCTION_NAME", "Unknown"
                                ),
                            }
                        ],
                    },
                ],
            )
