#!/usr/bin/env bash
set -eo pipefail

pre-commit run -a
python -m pytest --cov=src/lambda_telemetry_shipper src/test
