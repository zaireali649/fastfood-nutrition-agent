"""
Advanced Retry Handler with Exponential Backoff.

Provides sophisticated retry logic for transient failures.
"""

import logging
import time
import asyncio
from typing import Callable, Any, Type, Tuple
from functools import wraps
import random

logger = logging.getLogger(__name__)


class RetryHandler:
    """Handles retries with exponential backoff and jitter."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to delays
            retriable_exceptions: Exceptions that should trigger retry
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retriable_exceptions = retriable_exceptions
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt with exponential backoff."""
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            # Add random jitter (0-50% of delay)
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Retry successful on attempt {attempt + 1}")
                
                return result
                
            except self.retriable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed. "
                        f"Last error: {e}"
                    )
        
        raise last_exception
    
    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Retry successful on attempt {attempt + 1}")
                
                return result
                
            except self.retriable_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed. "
                        f"Last error: {e}"
                    )
        
        raise last_exception


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator for adding retry logic to functions.
    
    Usage:
        @retry(max_retries=3, base_delay=1.0)
        def unstable_function():
            # Might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        handler = RetryHandler(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retriable_exceptions=retriable_exceptions
        )
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await handler.execute_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return handler.execute(func, *args, **kwargs)
            return wrapper
    
    return decorator

