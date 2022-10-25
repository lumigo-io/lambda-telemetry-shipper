from abc import ABC, abstractmethod

from lambda_telemetry_shipper.utils import TelemetryRecord


class TelemetryHandler(ABC):
    _singleton = None

    @abstractmethod
    def should_handle(self, record: TelemetryRecord):
        raise NotImplementedError()

    @abstractmethod
    def handle(self, record: TelemetryRecord):
        raise NotImplementedError()

    @classmethod
    def get_singleton(cls):
        if not cls._singleton:
            cls._singleton = cls()
        return cls._singleton
