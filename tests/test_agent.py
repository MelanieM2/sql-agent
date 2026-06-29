import pytest
from unittest.mock import patch   #, MagicMock
from sql_agent.agent import run_agent


def test_run_agent_loads_records_and_exits(tmp_path):
    # Creates a minimal log file and verifies agent starts and exits cleanly
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth User logged in\n"
        "2026-06-20 08:12:05,102 WARNING database Connection pool low\n"
        "2026-06-20 08:12:07,445 ERROR database Query timeout\n"
    )
    db_file = str(tmp_path / "test.db")

    # Mock input() to simulate user typing "exit" immediately
    # Mock generate_sql and interpret_result to avoid real Gemini API calls
    with patch("builtins.input", return_value="exit"), \
         patch("sql_agent.agent.generate_sql", return_value="SELECT * FROM logs"), \
         patch("sql_agent.agent.interpret_result", return_value="Test answer"):
        run_agent(db_path=db_file, log_path=str(log_file))


def test_run_agent_handles_empty_input(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth User logged in\n"
    )
    db_file = str(tmp_path / "test.db")

    # Simulate user pressing enter twice then typing exit
    with patch("builtins.input", side_effect=["", "", "exit"]), \
         patch("sql_agent.agent.generate_sql", return_value="SELECT * FROM logs"), \
         patch("sql_agent.agent.interpret_result", return_value="Test answer"):
        run_agent(db_path=db_file, log_path=str(log_file))


def test_run_agent_handles_security_violation(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text(
        "2026-06-20 08:12:01,234 INFO auth User logged in\n"
    )
    db_file = str(tmp_path / "test.db")

    # Simulate Gemini returning a destructive query — agent should handle gracefully
    with patch("builtins.input", side_effect=["drop the table", "exit"]), \
         patch("sql_agent.agent.generate_sql", return_value="DROP TABLE logs"), \
         patch("sql_agent.agent.interpret_result", return_value="Test answer"):
        run_agent(db_path=db_file, log_path=str(log_file))