from abc import ABC, abstractmethod
from typing import List

from lambda_telemetry_shipper.utils import TelemetryRecord


class ExportLogsHandler(ABC):
    @abstractmethod
    def handle_logs(self, records: List[TelemetryRecord]):
        raise NotImplementedError()
