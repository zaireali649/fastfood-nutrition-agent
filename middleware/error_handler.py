"""
Global error handling and logging.

Features:
- Centralized error handling
- User-friendly error messages
- Error logging to database
- Automatic error recovery
"""

import logging
import traceback
from typing import Optional, Callable, Any
from datetime import datetime
from functools import wraps
from config.database import get_supabase_client, is_database_available

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles application errors gracefully."""
    
    ERROR_MESSAGES = {
        "api_error": "We're experiencing technical difficulties with the AI service. Please try again in a moment.",
        "database_error": "We're having trouble accessing your data. Your request will use temporary storage.",
        "validation_error": "There's an issue with your input. Please check and try again.",
        "rate_limit": "You've made too many requests. Please wait a moment before trying again.",
        "budget_limit": "Daily budget limit has been reached. Please try again tomorrow.",
        "content_filter": "Your request doesn't meet our content guidelines. Please rephrase.",
        "unknown_error": "An unexpected error occurred. Our team has been notified.",
    }
    
    @classmethod
    def get_user_friendly_message(cls, error_type: str, details: Optional[str] = None) -> str:
        """
        Get user-friendly error message.
        
        Args:
            error_type: Type of error
            details: Optional additional details
            
        Returns:
            User-friendly error message
        """
        base_message = cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES["unknown_error"])
        
        if details:
            return f"{base_message} (Details: {details})"
        
        return base_message
    
    @classmethod
    def log_error(
        cls,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        profile_id: Optional[str] = None,
        user_input: Optional[str] = None,
        severity: str = "error"
    ) -> None:
        """
        Log error to database and logging system.
        
        Args:
            error_type: Type of error
            error_message: Error message
            stack_trace: Full stack trace
            profile_id: User profile ID if applicable
            user_input: User input that caused error
            severity: Error severity (warning, error, critical)
        """
        # Log to standard logging
        log_func = getattr(logger, severity, logger.error)
        log_func(f"{error_type}: {error_message}")
        
        # Log to database if available
        if is_database_available():
            try:
                client = get_supabase_client()
                client.table("error_logs").insert({
                    "error_type": error_type,
                    "error_message": error_message,
                    "stack_trace": stack_trace,
                    "profile_id": profile_id,
                    "user_input": user_input[:500] if user_input else None,  # Truncate long inputs
                    "severity": severity,
                }).execute()
            except Exception as e:
                logger.error(f"Failed to log error to database: {e}")


def handle_errors(error_type: str = "unknown_error", return_value: Any = None):
    """
    Decorator for handling errors in functions.
    
    Args:
        error_type: Type of error for categorization
        return_value: Value to return on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get stack trace
                stack_trace = traceback.format_exc()
                
                # Log error
                ErrorHandler.log_error(
                    error_type=error_type,
                    error_message=str(e),
                    stack_trace=stack_trace,
                    severity="error"
                )
                
                # Return default value
                return return_value
        
        return wrapper
    return decorator


def handle_async_errors(error_type: str = "unknown_error", return_value: Any = None):
    """
    Decorator for handling errors in async functions.
    
    Args:
        error_type: Type of error for categorization
        return_value: Value to return on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Get stack trace
                stack_trace = traceback.format_exc()
                
                # Log error
                ErrorHandler.log_error(
                    error_type=error_type,
                    error_message=str(e),
                    stack_trace=stack_trace,
                    severity="error"
                )
                
                # Return default value
                return return_value
        
        return wrapper
    return decorator


class SafetyWrapper:
    """Context manager for safe operation execution."""
    
    def __init__(
        self,
        error_type: str = "unknown_error",
        user_message: Optional[str] = None,
        profile_id: Optional[str] = None
    ):
        """Initialize safety wrapper."""
        self.error_type = error_type
        self.user_message = user_message
        self.profile_id = profile_id
        self.error_occurred = False
        self.error_message = None
    
    def __enter__(self):
        """Enter context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and handle errors."""
        if exc_type is not None:
            self.error_occurred = True
            self.error_message = ErrorHandler.get_user_friendly_message(
                self.error_type,
                str(exc_val) if exc_val else None
            )
            
            # Log error
            ErrorHandler.log_error(
                error_type=self.error_type,
                error_message=str(exc_val),
                stack_trace=traceback.format_exception(exc_type, exc_val, exc_tb),
                profile_id=self.profile_id,
                severity="error"
            )
            
            # Suppress exception (return True)
            return True
        
        return False

