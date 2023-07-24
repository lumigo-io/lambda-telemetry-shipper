import os
from typing import Optional

from lambda_telemetry_shipper.utils import get_logger


def parse_env(env_name: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(env_name, default)


def parse_env_to_bool(env_name: str, default: bool) -> bool:
    try:
        if parse_env(env_name, default="").lower() == "true":
            return True
        return default
    except Exception:
        get_logger().exception(
            f"Unable to parse environment {env_name}. Fallback to default."
        )
        return default


def parse_env_to_int(env_name: str, default: int) -> int:
    try:
        return int(parse_env(env_name) or default)
    except Exception:
        get_logger().exception(
            f"Unable to parse environment {env_name}. Fallback to default."
        )
        return default


class Configuration:
    # Should we log only the data (true) or include the time & record type as a prefix (false; default behaviour)
    disable_log_prefix: Optional[bool] = parse_env_to_bool("LUMIGO_EXTENSION_DISABLE_LOG_PREFIX", False)

    # Min batch size. Default 1KB (don't send before reaching this amount)
    min_batch_size: int = parse_env_to_int("LUMIGO_EXTENSION_LOG_BATCH_SIZE", 1_000)

    # Min batch size in milliseconds. Default 1 minute
    min_batch_time: float = (
        parse_env_to_int("LUMIGO_EXTENSION_LOG_BATCH_TIME", 60_000) / 1_000
    )

    # Destination S3 bucket to write the logs. Default None to not publish to S3.
    s3_bucket_arn: Optional[str] = parse_env("LUMIGO_EXTENSION_LOG_S3_BUCKET", None)

    # Destination Cloudwatch metric to write the timeout metrics. Default None to not publish the metric.
    timeout_target_metric: Optional[str] = parse_env(
        "LUMIGO_EXTENSION_TIMEOUT_TARGET_METRIC", default=None
    )
