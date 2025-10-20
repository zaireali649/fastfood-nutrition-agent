"""
Circuit Breaker Pattern for Advanced Error Handling.

Prevents cascading failures by temporarily blocking requests to failing services.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests blocked
    - HALF_OPEN: Testing recovery, limited requests allowed
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        name: str = "default"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before testing recovery
            success_threshold: Successes needed in half-open to close
            name: Circuit breaker name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.name = name
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"Circuit {self.name}: Attempting reset (HALF_OPEN)")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                logger.warning(f"Circuit {self.name}: OPEN - Request blocked")
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service temporarily unavailable."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute async function through circuit breaker.
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info(f"Circuit {self.name}: Attempting reset (HALF_OPEN)")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                logger.warning(f"Circuit {self.name}: OPEN - Request blocked")
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service temporarily unavailable."
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure > timedelta(seconds=self.recovery_timeout)
    
    def _on_success(self):
        """Handle successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.info(
                f"Circuit {self.name}: Success in HALF_OPEN "
                f"({self.success_count}/{self.success_threshold})"
            )
            
            if self.success_count >= self.success_threshold:
                logger.info(f"Circuit {self.name}: CLOSED - Service recovered")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = datetime.now()
        
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        logger.warning(
            f"Circuit {self.name}: Failure "
            f"({self.failure_count}/{self.failure_threshold})"
        )
        
        if self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit {self.name}: OPEN - Recovery failed")
            self.state = CircuitState.OPEN
            self.success_count = 0
            self.last_state_change = datetime.now()
        
        elif self.failure_count >= self.failure_threshold:
            logger.error(f"Circuit {self.name}: OPEN - Threshold exceeded")
            self.state = CircuitState.OPEN
            self.last_state_change = datetime.now()
    
    def reset(self):
        """Manually reset circuit breaker."""
        logger.info(f"Circuit {self.name}: Manual reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()
    
    def get_status(self) -> dict:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
        }


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global circuit breakers
_circuit_breakers = {}


def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """
    Get or create a circuit breaker.
    
    Args:
        name: Circuit breaker name
        **kwargs: CircuitBreaker initialization arguments
        
    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name=name, **kwargs)
    return _circuit_breakers[name]


def circuit_breaker(name: str, **breaker_kwargs):
    """
    Decorator for applying circuit breaker to functions.
    
    Usage:
        @circuit_breaker("openai_api", failure_threshold=3)
        def call_api():
            # API call
            pass
    """
    def decorator(func: Callable) -> Callable:
        breaker = get_circuit_breaker(name, **breaker_kwargs)
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await breaker.call_async(func, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return breaker.call(func, *args, **kwargs)
            return wrapper
    
    return decorator


def get_all_circuit_breaker_status() -> dict:
    """Get status of all circuit breakers."""
    return {
        name: breaker.get_status()
        for name, breaker in _circuit_breakers.items()
    }

