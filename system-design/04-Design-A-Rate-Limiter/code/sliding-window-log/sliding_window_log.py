"""
Sliding-window log rate limiter.

- Per user we keep a sorted list of request timestamps within the last `window`.
- On request: drop entries older than `now - window`, count remaining.
- Allow if count < limit.

Pros: very accurate (no boundary burst).
Cons: O(N) memory per user where N = current request rate * window.
"""

import threading
import time
from collections import deque


class SlidingWindowLogLimiter:
    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window_seconds = window_seconds
        self._logs: dict[str, deque] = {}
        self._lock = threading.Lock()

    def allow(self, user_id: str, now: float | None = None) -> bool:
        now = now if now is not None else time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            log = self._logs.setdefault(user_id, deque())
            while log and log[0] <= cutoff:
                log.popleft()
            if len(log) < self.limit:
                log.append(now)
                return True
            return False


if __name__ == "__main__":
    rl = SlidingWindowLogLimiter(limit=3, window_seconds=1.0)

    # Reproduces the boundary scenario the fixed-window suffers from.
    print("3 requests at t=0.9 (all allowed):")
    for _ in range(3):
        print(f"  {'ALLOW' if rl.allow('u', 0.9) else 'DENY'}")

    print("\n3 more at t=1.05 (within sliding 1s window):")
    for _ in range(3):
        print(f"  {'ALLOW' if rl.allow('u', 1.05) else 'DENY'}")

    print("\nAt t=2.0 (old entries expired):")
    for _ in range(3):
        print(f"  {'ALLOW' if rl.allow('u', 2.0) else 'DENY'}")
