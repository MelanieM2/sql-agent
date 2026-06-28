import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogRecord:
    timestamp: str
    level: str
    module: str
    message: str


LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(?P<level>\w+)\s+"
    r"(?P<module>\w+)\s+"
    r"(?P<message>.+)"
)


def parse_log_file(filepath: str) -> list[LogRecord]:
    records = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            match = LOG_PATTERN.match(line)
            if match:
                records.append(LogRecord(
                    timestamp=match.group("timestamp"),
                    level=match.group("level"),
                    module=match.group("module"),
                    message=match.group("message"),
                ))
    return records