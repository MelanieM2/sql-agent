import pytest
from sql_agent.parser import parse_log_file, LogRecord


def test_parse_returns_correct_number_of_records(tmp_path):
    # tmp_path is a pytest built-in fixture — creates a temporary directory
    # that is automatically cleaned up after the test runs

    # ARRANGE — set up the conditions
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth Successfully authenticated user admin\n"
        "2026-06-20 08:12:03,891 INFO database Connection established to primary DB\n"
        "2026-06-20 08:12:07,445 ERROR database Query timeout after 30s on table users\n"
    )

    # ACT — call the function we are testing
    records = parse_log_file(str(log_file))

    # ASSERT — verify the result is what we expected
    assert len(records) == 3


def test_parse_extracts_correct_fields(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth Successfully authenticated user admin\n"
    )
    records = parse_log_file(str(log_file))
    assert records[0].timestamp == "2026-06-20 08:12:01,234"
    assert records[0].level == "INFO"
    assert records[0].module == "auth"
    assert records[0].message == "Successfully authenticated user admin"


def test_parse_skips_empty_lines(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth Successfully authenticated user admin\n"
        "\n"
        "2026-06-20 08:12:03,891 INFO database Connection established to primary DB\n"
    )
    records = parse_log_file(str(log_file))
    assert len(records) == 2


def test_parse_skips_malformed_lines(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth Successfully authenticated user admin\n"
        "this line is malformed and should be skipped\n"
    )
    records = parse_log_file(str(log_file))
    assert len(records) == 1


def test_parse_returns_log_record_instances(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth Successfully authenticated user admin\n"
    )
    records = parse_log_file(str(log_file))
    assert isinstance(records[0], LogRecord)