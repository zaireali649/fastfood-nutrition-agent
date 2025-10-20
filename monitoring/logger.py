"""
Structured logging configuration.

Features:
- JSON structured logging
- Log levels by environment
- Automatic context inclusion
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json
from config.environments import get_config, is_production


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for better parsing."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def setup_logging():
    """Configure application logging."""
    log_level = get_config("log_level", "INFO")
    
    # Convert string to logging level
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter in production
    if is_production():
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return root_logger


def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """
    Log message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **context: Additional context fields
    """
    log_func = getattr(logger, level.lower(), logger.info)
    
    # Create a log record with extra context
    extra = {"extra_fields": context}
    log_func(message, extra=extra)


# Initialize logging on module import
setup_logging()

