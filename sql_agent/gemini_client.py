import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

SCHEMA = """
Table: logs
Columns:
  id        INTEGER  -- auto-incremented unique row identifier
  timestamp TEXT     -- format: YYYY-MM-DD HH:MM:SS,mmm
  level     TEXT     -- one of: INFO, WARNING, ERROR
  module    TEXT     -- one of: auth, database, api
  message   TEXT     -- free text log message
"""


def _get_client() -> genai.Client:
    # Load API key from .env file
    # Raises immediately if key is missing — fail fast, clear error
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Check your .env file.")
    return genai.Client(api_key=api_key)


def generate_sql(question: str, date_range: dict) -> str:
    # Sends the user's natural language question to Gemini
    # Includes actual date range from the database — prevents date hallucination
    # Gemini returns a SQL query based on the schema
    # Returns only the raw SQL string, nothing else
    client = _get_client()
    prompt = f"""You are a SQL expert. Given this SQLite table schema:

{SCHEMA}
The logs in this database span from {date_range['earliest']} to {date_range['latest']}.

Write a single SQLite SELECT query to answer this question:
{question}

Rules:
- Return ONLY the SQL query, no explanation, no markdown, no backticks
- Use only SELECT statements, never INSERT, UPDATE, DELETE or DROP
- Query only the logs table
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    return (response.text or "").strip()


def interpret_result(question: str, sql: str, results: list[dict]) -> str:
    # Sends the original question, the SQL used, and the raw results to Gemini
    # Gemini returns a plain English interpretation for the user
    client = _get_client()
    prompt = f"""A user asked: "{question}"

This SQL query was run:
{sql}

These are the results:
{results}

Please explain the results in plain English, directly answering the user's question.
Be concise — 2-3 sentences maximum.
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    return (response.text or "").strip()