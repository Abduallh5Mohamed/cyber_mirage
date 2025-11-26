"""
⚡ Error Handler with Retry Logic & Circuit Breaker
"""

import functools
import time
import logging
from typing import Callable, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = defaultdict(int)
        self.last_failure_time = defaultdict(lambda: None)
        self.state = defaultdict(lambda: "closed")  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker"""
        func_name = func.__name__
        
        # Check if circuit is open
        if self.state[func_name] == "open":
            if self.last_failure_time[func_name]:
                elapsed = time.time() - self.last_failure_time[func_name]
                if elapsed > self.timeout:
                    self.state[func_name] = "half_open"
                    logger.info(f"Circuit breaker half-open for {func_name}")
                else:
                    raise Exception(f"Circuit breaker open for {func_name}")
        
        try:
            result = func(*args, **kwargs)
            
            # Reset on success
            if self.state[func_name] == "half_open":
                self.state[func_name] = "closed"
                self.failures[func_name] = 0
                logger.info(f"Circuit breaker closed for {func_name}")
            
            return result
            
        except Exception as e:
            self.failures[func_name] += 1
            self.last_failure_time[func_name] = time.time()
            
            if self.failures[func_name] >= self.failure_threshold:
                self.state[func_name] = "open"
                logger.error(f"Circuit breaker opened for {func_name}")
            
            raise e


# Global circuit breaker
circuit_breaker = CircuitBreaker()


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time (2.0 = double each time)
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = 1
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries",
                            exc_info=True
                        )
                        raise
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {wait_time}s... Error: {str(e)}"
                    )
                    
                    time.sleep(wait_time)
                    wait_time *= backoff_factor
            
        return wrapper
    return decorator


def timeout_handler(timeout_seconds: int):
    """Timeout decorator"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout_seconds}s")
            
            # Set timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            return result
        
        return wrapper
    return decorator


class ErrorTracker:
    """Track errors for monitoring"""
    
    def __init__(self):
        self.errors = defaultdict(int)
        self.recent_errors = []
        self.max_recent = 100
    
    def record_error(self, error_type: str, error_msg: str):
        """Record an error"""
        self.errors[error_type] += 1
        self.recent_errors.append({
            "type": error_type,
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent errors
        if len(self.recent_errors) > self.max_recent:
            self.recent_errors = self.recent_errors[-self.max_recent:]
    
    def get_error_stats(self) -> dict:
        """Get error statistics"""
        return {
            "total_by_type": dict(self.errors),
            "recent_errors": self.recent_errors[-10:],
            "total_errors": sum(self.errors.values())
        }


# Global error tracker
error_tracker = ErrorTracker()


def handle_errors(error_type: str = "general"):
    """Error handling decorator"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_tracker.record_error(error_type, str(e))
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


class GracefulError(Exception):
    """Base class for graceful errors"""
    def __init__(self, message: str, recoverable: bool = True):
        self.message = message
        self.recoverable = recoverable
        super().__init__(self.message)


class ModelLoadError(GracefulError):
    """Error loading ML model"""
    pass


class EnvironmentError(GracefulError):
    """Error in environment"""
    pass


class ValidationError(GracefulError):
    """Input validation error"""
    pass


class RateLimitError(GracefulError):
    """Rate limit exceeded"""
    pass


def safe_execute(func: Callable, *args, default=None, **kwargs) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        default: Default value to return on error
        *args, **kwargs: Function arguments
    
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {str(e)}")
        error_tracker.record_error("safe_execute", str(e))
        return default
