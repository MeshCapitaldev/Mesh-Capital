import asyncio, functools, time
from typing import Callable, Tuple, Type
from app.utils.logger import get_logger

logger = get_logger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exc, wait = None, delay
            for attempt in range(1, max_attempts + 1):
                try: return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        logger.warning(f"{func.__name__} attempt {attempt}/{max_attempts}: {e}")
                        time.sleep(wait); wait *= backoff
            raise last_exc

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exc, wait = None, delay
            for attempt in range(1, max_attempts + 1):
                try: return await func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < max_attempts:
                        await asyncio.sleep(wait); wait *= backoff
            raise last_exc

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
