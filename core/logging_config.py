"""
Structured Logging Configuration for Hermes Intelligence Platform
Uses structlog for structured, context-rich logging with JSON output support.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

import structlog
from structlog.types import Processor


def add_timestamp(logger, method_name, event_dict):
    """Add ISO timestamp to log events."""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict


def add_service_info(logger, method_name, event_dict):
    """Add service identification to log events."""
    event_dict["service"] = "hermes"
    event_dict["version"] = "6.15"
    return event_dict


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Legacy setup_logging function for backwards compatibility."""
    configure_structlog(log_level=log_level, log_file=log_file, json_output=False)


def configure_structlog(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_output: bool = False
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        json_output: Whether to output JSON formatted logs (for production)
    """
    # Ensure log directory exists
    if log_file:
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)

    # Define shared processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_timestamp,
        add_service_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        # JSON output for production/log aggregation
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Console-friendly output for development
        shared_processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback
            )
        )

    # Configure structlog
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    handlers.append(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True
    )

    # Set levels for noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    # Log initialization
    logger = get_logger(__name__)
    logger.info("logging_initialized", level=log_level, json_output=json_output)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary context to logs."""

    def __init__(self, **kwargs):
        """
        Initialize context with key-value pairs.

        Args:
            **kwargs: Context values to add to logs
        """
        self.context = kwargs

    def __enter__(self):
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars(*self.context.keys())
        return False


# Helper functions for common log patterns

def log_api_request(logger, method: str, url: str, **kwargs):
    """Log an API request with standard fields."""
    logger.info("api_request", http_method=method, url=url, **kwargs)


def log_api_response(logger, status_code: int, duration_ms: float, **kwargs):
    """Log an API response with standard fields."""
    log_method = logger.info if status_code < 400 else logger.warning
    log_method("api_response", status_code=status_code, duration_ms=round(duration_ms, 2), **kwargs)


def log_db_query(logger, query_type: str, table: str, duration_ms: float, rows: int = None, **kwargs):
    """Log a database query with standard fields."""
    logger.debug("db_query", query_type=query_type, table=table,
                 duration_ms=round(duration_ms, 2), rows_affected=rows, **kwargs)


def log_collector_run(logger, collector_name: str, status: str, duration_s: float, records: int = 0, **kwargs):
    """Log a data collector run with standard fields."""
    log_method = logger.info if status == "success" else logger.warning
    log_method("collector_run", collector=collector_name, status=status,
               duration_seconds=round(duration_s, 2), records_collected=records, **kwargs)


def log_startup(logger, component: str, **kwargs):
    """Log component startup."""
    logger.info("startup", component=component, **kwargs)


def log_shutdown(logger, component: str, **kwargs):
    """Log component shutdown."""
    logger.info("shutdown", component=component, **kwargs)


def log_error(logger, error: Exception, context: str = None, **kwargs):
    """Log an error with exception details."""
    logger.error("error", error_type=type(error).__name__, error_message=str(error),
                 context=context, **kwargs, exc_info=True)
