from typing import List
import random

import boto3

from lambda_telemetry_shipper.configuration import Configuration
from lambda_telemetry_shipper.export_logs_handlers.base_handler import ExportLogsHandler
from lambda_telemetry_shipper.utils import get_logger, TelemetryRecord

TIME_PADDING = 30
TYPE_PADDING = 10


class S3Handler(ExportLogsHandler):
    def handle_logs(self, records: List[TelemetryRecord]) -> bool:
        if Configuration.s3_bucket_arn and records:
            get_logger().debug("S3Handler started to run")
            s3 = boto3.client("s3")
            key = S3Handler.generate_key_name(records)
            file_data = S3Handler.format_records(records)
            s3.put_object(Body=file_data, Bucket=Configuration.s3_bucket_arn, Key=key)
            get_logger().info(f"S3Handler put {len(records)} logs in {key}")
            return True
        return False

    @staticmethod
    def generate_key_name(records: List[TelemetryRecord]):
        t = min(r.record_time for r in records)
        directory = f"logs/{t.year}/{t.month}/{t.day}/"
        return f"{directory}{t.hour}:{t.minute}:{t.second}:{t.microsecond}-{random.random()}"

    @staticmethod
    def format_records(records: List[TelemetryRecord]) -> bytes:
        return "\n".join(map(S3Handler._format_record, records)).encode()

    @staticmethod
    def _format_record(r: TelemetryRecord):
        return f"{r.record_time.isoformat():{TIME_PADDING}}{r.record_type.value:{TYPE_PADDING}}{r.record}"
