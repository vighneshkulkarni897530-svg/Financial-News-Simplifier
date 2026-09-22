"""Core configuration and logging for FinNews AI."""

from app.core.config import settings, get_settings
from app.core.logging_config import setup_logging, logger

__all__ = ["settings", "get_settings", "setup_logging", "logger"]
