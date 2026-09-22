"""Logging configuration for FinNews AI."""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured console logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Set third-party loggers to a reasonable level
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    app_logger = logging.getLogger("finnews")
    app_logger.setLevel(log_level)
    return app_logger


logger = setup_logging()
