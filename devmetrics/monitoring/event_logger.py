"""Structured event logger for DevMetrics.

Logs API errors, rate limits, data anomalies, and health check results
to logs/events.json in a structured JSON-lines format.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LOGS_DIR = Path(__file__).parent.parent / "logs"


def _ensure_logs_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


class EventLogger:
    """Structured event logger that writes to both Python logging and JSON file."""

    def __init__(self, source: str, log_file: str = "events.json"):
        self.source = source
        self.log_file = LOGS_DIR / log_file
        self._logger = logging.getLogger(f"devmetrics.{source}")
        _ensure_logs_dir()

    def _write_event(self, event: dict) -> None:
        """Append a JSON event to the log file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")

    def log(
        self,
        level: str,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict:
        """Log a structured event.

        Args:
            level: Log level (INFO, WARNING, ERROR, CRITICAL)
            message: Human-readable message
            context: Optional dict of additional context
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "source": self.source,
            "message": message,
            "context": context or {},
        }
        self._write_event(event)

        log_fn = getattr(self._logger, level.lower(), self._logger.info)
        log_fn(message, extra={"context": context or {}})
        return event

    def info(self, message: str, **context: Any) -> dict:
        return self.log("INFO", message, context or None)

    def warning(self, message: str, **context: Any) -> dict:
        return self.log("WARNING", message, context or None)

    def error(self, message: str, **context: Any) -> dict:
        return self.log("ERROR", message, context or None)

    def api_error(
        self, endpoint: str, status_code: int, message: str = ""
    ) -> dict:
        """Log an API error with endpoint and status code."""
        return self.log(
            "ERROR",
            message or f"API error on {endpoint}",
            {"endpoint": endpoint, "status_code": status_code},
        )

    def rate_limit(self, endpoint: str, retry_after: int) -> dict:
        """Log a rate limit hit."""
        return self.log(
            "WARNING",
            f"Rate limit exceeded on {endpoint}",
            {"endpoint": endpoint, "retry_after": retry_after},
        )

    def data_anomaly(self, metric: str, detail: str) -> dict:
        """Log a data anomaly (e.g., zero PRs returned)."""
        return self.log(
            "WARNING",
            f"Data anomaly in {metric}: {detail}",
            {"metric": metric, "detail": detail},
        )

    def health_check(
        self, page: str, success: bool, screenshot_path: Optional[str] = None
    ) -> dict:
        """Log a health check result."""
        level = "INFO" if success else "ERROR"
        msg = f"Health check {'passed' if success else 'FAILED'} for {page}"
        ctx: dict[str, Any] = {"page": page, "success": success}
        if screenshot_path:
            ctx["screenshot"] = screenshot_path
        return self.log(level, msg, ctx)


def read_events(
    log_file: str = "events.json", tail: int = 50
) -> list[dict]:
    """Read the last N events from the log file."""
    path = LOGS_DIR / log_file
    if not path.exists():
        return []
    with open(path) as f:
        lines = f.readlines()
    events = []
    for line in lines[-tail:]:
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events
