import argparse
from sql_agent.agent import run_agent

def main():
    parser = argparse.ArgumentParser(
        description="Agentic SQL assistant — query logs in natural language"
    )
    parser.add_argument(
        "--logfile",
        type=str,
        default="logs/sample.log",
        help="Path to the log file to load (default: logs/sample.log)"
    )
    parser.add_argument(
        "--db",
        type=str,
        default="logs.db",
        help="Path to the SQLite database file (default: logs.db)"
    )
    args = parser.parse_args()
    run_agent(db_path=args.db, log_path=args.logfile)

if __name__ == "__main__":
    main()