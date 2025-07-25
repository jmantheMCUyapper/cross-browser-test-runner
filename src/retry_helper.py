"""
Retry helper for handling flaky network connections
"""
import time
import functools
from typing import Callable, Any


def retry_on_connection_error(max_attempts: int = 3, delay: float = 2.0):
    """Decorator to retry on connection errors"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if "ConnectionError" in str(type(e)) or "Could not reach host" in str(e):
                        last_exception = e
                        if attempt < max_attempts - 1:
                            print(f"Connection error on attempt {attempt + 1}, retrying in {delay} seconds...")
                            time.sleep(delay)
                        continue
                    else:
                        # Re-raise non-connection errors immediately
                        raise

            # If all attempts failed, raise the last exception
            raise last_exception

        return wrapper

    return decorator