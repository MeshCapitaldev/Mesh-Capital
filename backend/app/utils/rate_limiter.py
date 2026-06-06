import time, threading
from collections import deque
from typing import Optional


class RateLimiter:
    def __init__(self, calls_per_second: float = 5.0, burst: int = 10):
        self._rate = calls_per_second
        self._burst = burst
        self._tokens = float(burst)
        self._last = time.monotonic()
        self._lock = threading.Lock()

    def acquire(self, timeout: Optional[float] = 30.0) -> bool:
        deadline = time.monotonic() + (timeout or 0)
        while True:
            with self._lock:
                now = time.monotonic()
                self._tokens = min(self._burst, self._tokens + (now - self._last) * self._rate)
                self._last = now
                if self._tokens >= 1.0:
                    self._tokens -= 1.0; return True
                wait = (1.0 - self._tokens) / self._rate
            if timeout is not None and time.monotonic() + wait > deadline:
                return False
            time.sleep(min(wait, 0.1))


class SlidingWindowLimiter:
    def __init__(self, max_calls: int, window_seconds: float):
        self._max = max_calls
        self._window = window_seconds
        self._ts: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self) -> bool:
        with self._lock:
            now = time.monotonic()
            while self._ts and self._ts[0] < now - self._window:
                self._ts.popleft()
            if len(self._ts) < self._max:
                self._ts.append(now); return True
            return False

    def wait_and_acquire(self) -> None:
        while not self.acquire(): time.sleep(0.05)


llm_limiter = RateLimiter(calls_per_second=2.0, burst=5)
route_limiter = RateLimiter(calls_per_second=20.0, burst=40)
coingecko_limiter = SlidingWindowLimiter(max_calls=30, window_seconds=60.0)
