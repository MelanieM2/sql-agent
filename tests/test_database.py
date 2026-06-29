import pytest
import sqlite3
from sql_agent.parser import LogRecord
from sql_agent.database import (
    create_connection,
    create_table,
    insert_records,
    run_query,
    get_date_range
)


@pytest.fixture
def db():
    # Creates an in-memory SQLite database for testing
    # In-memory means no file on disk, which is fast, isolated, and auto-destroyed after test

     # SETUP PHASE — runs before the test
    conn = create_connection(":memory:")
    create_table(conn)

    yield conn # pauses here, hands conn to the test.
               # The fixture function pauses, it doesn't exit.
               # When the test finishes, pytest returns to the fixture and
               # executes everything after

    # TEARDOWN PHASE — runs after the test finishes
    conn.close() # runs and cleanup is guaranteed


@pytest.fixture
def sample_records():
    return [
        LogRecord("2026-06-20 08:12:01,234", "INFO", "auth", "User logged in"),
        LogRecord("2026-06-20 08:12:05,102", "WARNING", "database", "Connection pool low"),
        LogRecord("2026-06-20 08:12:07,445", "ERROR", "database", "Query timeout"),
    ]


def test_create_table_creates_logs_table(db):
    # Verify the logs table exists by querying sqlite_master
    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='logs'"
    )
    assert cursor.fetchone() is not None


def test_insert_records_correct_count(db, sample_records):
    insert_records(db, sample_records)
    cursor = db.execute("SELECT COUNT(*) as count FROM logs")
    assert cursor.fetchone()["count"] == 3


def test_insert_records_correct_values(db, sample_records):
    insert_records(db, sample_records)
    cursor = db.execute("SELECT * FROM logs WHERE level = 'ERROR'")
    row = cursor.fetchone()
    assert row["module"] == "database"
    assert row["message"] == "Query timeout"


def test_run_query_returns_list_of_dicts(db, sample_records):
    insert_records(db, sample_records)
    results = run_query(db, "SELECT * FROM logs")
    assert isinstance(results, list)
    assert isinstance(results[0], dict)


def test_run_query_blocks_non_select(db):
    # Verify security guard raises ValueError on destructive queries
    with pytest.raises(ValueError):
        run_query(db, "DROP TABLE logs")


def test_get_date_range_returns_correct_bounds(db, sample_records):
    insert_records(db, sample_records)
    date_range = get_date_range(db)
    assert date_range["earliest"] == "2026-06-20 08:12:01,234"
    assert date_range["latest"] == "2026-06-20 08:12:07,445"