import datetime

from lambda_telemetry_shipper.export_logs_handlers.base_handler import ExportLogsHandler
from lambda_telemetry_shipper.telemetry_handlers.logs_manager import LogsManager
from lambda_telemetry_shipper.configuration import Configuration


def test_send_batch_some_failures(caplog, record):
    class TestHandler(ExportLogsHandler):
        def handle_logs(self, records):
            1 / 0

    manager = LogsManager()
    manager.pending_logs.append(record)
    manager.send_batch()  # No exception

    assert len([r for r in caplog.records if r.levelname == "ERROR"]) == 1
    assert [r for r in caplog.records if r.levelname == "DEBUG"]


def test_send_batch_if_needed_no_send(record):
    logs = LogsManager.get_singleton()
    assert not logs.send_batch_if_needed()


def test_send_batch_if_needed_big_batch(record):
    logs = LogsManager.get_singleton()
    logs.pending_logs_size = Configuration.min_batch_size + 1
    assert logs.send_batch_if_needed()


def test_send_batch_if_needed_big_time_gap(record):
    logs = LogsManager.get_singleton()
    logs.last_sent_time = datetime.datetime.now() - datetime.timedelta(
        seconds=Configuration.min_batch_time + 1
    )
    assert logs.send_batch_if_needed()


def test_add_records_clear_after_send(record):
    for _ in range(Configuration.min_batch_size + 1):
        LogsManager.get_singleton().handle(record)
    LogsManager.get_singleton().send_batch_if_needed()
    assert not LogsManager.get_singleton().send_batch_if_needed()


def test_add_records_old_batch(record, monkeypatch):
    monkeypatch.setattr(Configuration, "min_batch_time", -1)
    LogsManager.get_singleton().handle(record)
    assert LogsManager.get_singleton().send_batch_if_needed()


def test_send_batch_empty():
    assert not LogsManager.get_singleton().send_batch()
