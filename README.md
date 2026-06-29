# sql-agent

Agentic SQL assistant — natural language queries over SQLite via Gemini.

Ask a question in plain English. The agent generates SQL, runs it against
a SQLite database populated from a Python log file, and returns a plain
English answer.

---

## How It Works

```
User question (natural language)
        ↓
Gemini generates SQL
        ↓
Security guard validates SQL (SELECT only)
        ↓
Agent runs SQL against SQLite
        ↓
Gemini interprets results
        ↓
Plain English answer
```

---

## Quickstart

### 1. Clone the repository

```bash
git clone git@github.com:MelanieM2/sql-agent.git
cd sql-agent
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure your API key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 4. Run the agent

```bash
uv run python main.py
```

By default, the agent loads `logs/sample.log`. You can specify a different
log file:

```bash
uv run python main.py --logfile path/to/your.log --db path/to/your.db
```

---

## Example Session

```
Parsing log file...
Loaded 20 log records.
Initialising database...
Database ready. Logs span 2026-06-20 08:12:01,234 to 2026-06-20 08:12:41,123.

SQL Agent ready. Type 'exit' to quit.
----------------------------------------

> Ask a question: which module had the most errors?
Generating SQL...
SQL: SELECT module, COUNT(*) as error_count FROM logs WHERE level = 'ERROR'
     GROUP BY module ORDER BY error_count DESC LIMIT 1
Running query...
Interpreting results...
Answer: The 'database' module had the most errors with 2 recorded,
        including a query timeout and a deadlock detection.

> Ask a question: what happened between 08:12:20 and 08:12:40?
Generating SQL...
SQL: SELECT * FROM logs WHERE timestamp BETWEEN '2026-06-20 08:12:20'
     AND '2026-06-20 08:12:40'
Running query...
Interpreting results...
Answer: Between 08:12:20 and 08:12:38, the system experienced a series
        of issues including a database deadlock, a service timeout, and
        multiple security alerts such as rate limiting and brute force attempts.

> Ask a question: exit
Goodbye.
```

---

## Log File Format

The agent expects Python-style log files:

```
YYYY-MM-DD HH:MM:SS,mmm LEVEL MODULE Message text here
```

Example:
```
2026-06-20 08:12:01,234 INFO auth Successfully authenticated user admin
2026-06-20 08:12:07,445 ERROR database Query timeout after 30s on table users
2026-06-20 08:12:23,789 WARNING api Rate limit reached for IP 192.168.1.45
```

---

## Project Structure

```
sql-agent/
├── sql_agent/
│   ├── parser.py        ← parses log files into LogRecord objects
│   ├── database.py      ← SQLite connection, schema, queries
│   ├── gemini_client.py ← SQL generation and result interpretation via Gemini
│   └── agent.py         ← agentic loop orchestration
├── logs/
│   └── sample.log       ← sample log data
├── tests/               ← 14 unit tests
├── main.py              ← entry point
├── .env.example         ← API key template
└── SECURITY.md          ← security policy
```

---

## Security

- API keys stored in `.env` — never committed to version control
- Only `SELECT` queries permitted — destructive SQL blocked at runtime
- Parameterised queries used for all data insertion — SQL injection prevented
- Dependencies pinned to exact versions and audited with `uv audit`

See [SECURITY.md](SECURITY.md) for full details.

---

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for dependency management
- Gemini API key — [get one here](https://aistudio.google.com/)

---

## Development Notes

This project was developed as part of a structured learning portfolio toward
Data Science, ML Engineering, and Agentic AI.

**Development tools:** Claude Sonnet 4.6 was used as an AI pair programmer
and advisor throughout development — for architecture decisions, code review,
concept explanations, and test design. All code was written, understood, and
owned by the developer.

**Runtime AI:** Gemini API (`gemini-3.1-flash-lite`) is used at runtime for
SQL generation and result interpretation — it is a functional component of
the application, not a development tool.

---

## Roadmap / Future Improvements in this project

- [ ] Add Apache/Nginx log format support in `parser.py`
- [ ] Persist conversation history across questions for follow-up context
- [ ] Add `reporter.py` for formatted report output
- [ ] Migrate to a persistent database mode — persist logs to SQLite across sessions appending new log records to the existing database rather than overwriting
- [ ] Add agentic stretch goal: parse → ask Gemini what to look for → re-parse → synthesise

---

## Project Context

This project is part of a broader personal learning roadmap through Data Science,
ML Engineering, and Agentic AI including:

* Python-based automation and agentic AI systems
* Linux system architecture and infrastructure design
* SQL, database design, and data pipeline engineering
* Applied machine learning and LLM-integrated pipelines

The goal is to bridge theoretical foundations in mathematics and machine learning
with practical systems engineering and production-style automation workflows.

---

**Connections to other projects:**
- Inherits git workflow and security framework from `linux-system-inspector` (Project 1)
- Inherits log parsing logic and Gemini API integration pattern from `log-analyzer` (Project 2)
- Extends `log-analyzer` by persisting parsed logs into SQLite and enabling natural language querying
- Planned: SSH into Acer machine, pull real `/var/log/syslog`, load and query it with this tool
- Planned: Project 4 will extend the agentic loop pattern introduced here into a Scikit-learn ML pipeline

<!--
- Stretch goal: persistent database mode — instead of repopulating SQLite from the log file
  on every run, detect an existing database and append only new records, enabling historical
  queries across multiple sessions
- Stretch goal: agentic loop — parse → ask Gemini what to look for next → re-parse → synthesise findings
- Stretch goal: multi-agent architecture — each module becomes an autonomous subagent
-->