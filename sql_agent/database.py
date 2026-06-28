import sqlite3
from sql_agent.parser import LogRecord


def create_connection(db_path: str) -> sqlite3.Connection:
    # Opens existing .db file or creates it automatically if it doesn't exist
    # row_factory=sqlite3.Row allows column access by name (row["level"])
    # instead of by position (row[0]) — safer and more readable
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_table(conn: sqlite3.Connection) -> None:
    # CREATE TABLE IF NOT EXISTS — safe to call multiple times, won't overwrite
    # this defines the Schema.
    # id: auto-incremented unique row identifier, managed by SQLite
    # TEXT NOT NULL: database enforces these fields are always present
    # commit() makes the change permanent — SQLite stages changes until committed
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level     TEXT NOT NULL,
            module    TEXT NOT NULL,
            message   TEXT NOT NULL
        )
    """)
    conn.commit()


def insert_records(conn: sqlite3.Connection, records: list[LogRecord]) -> None:
    # This populates the log data
    # executemany runs the same INSERT for every record in one batch — faster than looping
    # ? placeholders prevent SQL injection: user data is bound separately
    # from SQL structure, so it is always treated as data, never as code
    conn.executemany(
        "INSERT INTO logs (timestamp, level, module, message) VALUES (?, ?, ?, ?)",
        [(r.timestamp, r.level, r.module, r.message) for r in records]
    )
    conn.commit()


def run_query(conn: sqlite3.Connection, sql: str) -> list[dict]:
    # this will be used later by the agent to answer questions

    # Security guard: only SELECT statements permitted
    # Prevents destructive queries even if Gemini generates them
    # Check lives here — as close as possible to the dangerous operation
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")
    
    # cursor holds the query result as a pointer
    # fetchall() retrieves all rows at once
    # dict(row) converts sqlite3.Row objects to plain Python dicts
    # making results easy to read and pass to Gemini as text    
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def get_date_range(conn: sqlite3.Connection) -> dict:
    # Retrieves the earliest and latest timestamp from the logs table
    # Used to give Gemini accurate date context — prevents date hallucination
    cursor = conn.execute("""
        SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest FROM logs
    """)
    row = cursor.fetchone()
    return {
        "earliest": row["earliest"],
        "latest": row["latest"]
    }