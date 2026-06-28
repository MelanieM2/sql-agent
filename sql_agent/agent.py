from sql_agent.parser import parse_log_file
from sql_agent.database import create_connection, create_table, insert_records, run_query, get_date_range
from sql_agent.gemini_client import generate_sql, interpret_result


def run_agent(db_path: str, log_path: str) -> None:
    # --- Startup sequence ---
    print("Parsing log file...")
    records = parse_log_file(log_path)
    print(f"Loaded {len(records)} log records.")

    print("Initialising database...")
    conn = create_connection(db_path)
    create_table(conn)
    insert_records(conn, records)
    date_range = get_date_range(conn)
    print("Database ready.\n")

    # --- Interactive loop ---
    print("SQL Agent ready. Type 'exit' to quit.")
    print("-" * 40)

    while True:
        question = input("\n> Ask a question: ").strip()

        if not question:
            continue

        if question.lower() == "exit":
            print("Goodbye.")
            break

        try:
            # Step 1: Gemini generates SQL from natural language
            print("Generating SQL...")
            sql = generate_sql(question, date_range)
            print(f"SQL: {sql}\n")

            # Step 2: Agent runs SQL against SQLite
            print("Running query...")
            results = run_query(conn, sql)

            # Step 3: Gemini interprets results in plain English
            print("Interpreting results...")
            answer = interpret_result(question, sql, results)

            print(f"\nAnswer: {answer}")

        except ValueError as e:
            print(f"Security error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    conn.close()