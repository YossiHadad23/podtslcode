"""Rate Limiter - Token Bucket Algorithm."""

import time
import threading
from typing import Callable, Any
from functools import wraps

from config import api_config
from logger import logger


class TokenBucketRateLimiter:
    """Thread-safe token bucket rate limiter."""
    
    def __init__(self, max_rate: float = 1.0, capacity: int = 1):
        self.max_rate = max_rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
        logger.debug(f"RateLimiter initialized: {max_rate} req/sec")
    
    def _add_tokens(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        tokens_to_add = elapsed * self.max_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_update = now
    
    def acquire(self, blocking: bool = True) -> bool:
        """Acquire a token."""
        with self.lock:
            self._add_tokens()
            
            if self.tokens >= 1:
                self.tokens -= 1
                logger.debug(f"Token acquired. Remaining: {self.tokens:.2f}")
                return True
            
            if not blocking:
                logger.debug("Token not available")
                return False
            
            wait_time = (1 - self.tokens) / self.max_rate
            logger.debug(f"Rate limit reached. Waiting {wait_time:.2f}s")
        
        time.sleep(wait_time)
        
        with self.lock:
            self._add_tokens()
            if self.tokens >= 1:
                self.tokens -= 1
                logger.debug(f"Token acquired after wait")
                return True
            
            logger.warning("Token still not available after wait")
            return False
    
    def wait(self) -> Callable:
        """Decorator to rate-limit function calls."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                self.acquire(blocking=True)
                return func(*args, **kwargs)
            return wrapper
        return decorator


rate_limiter = TokenBucketRateLimiter(
    max_rate=api_config.MAX_REQUESTS_PER_SECOND,
    capacity=1
)
