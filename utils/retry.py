import asyncio
import functools
import logging

logger = logging.getLogger(__name__)


def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for async functions with exponential backoff retry."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {exc}")
                        raise
                    logger.warning(f"{func.__name__} attempt {attempt} failed: {exc}. Retrying in {wait}s...")
                    await asyncio.sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator
