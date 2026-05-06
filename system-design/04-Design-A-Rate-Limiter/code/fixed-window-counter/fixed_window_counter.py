"""
Fixed-window counter rate limiter.

- Time is split into fixed windows of `window_seconds`.
- Each (user, window) has an independent counter.
- Window flips reset the counter.

Boundary-burst issue: up to 2 * limit can fit in a 1-window stretch
that straddles the window boundary. A demo of that is at the bottom.
"""

import threading
import time


class FixedWindowCounterLimiter:
    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window_seconds = window_seconds
        self._counts: dict[tuple[str, int], int] = {}
        self._lock = threading.Lock()

    def _window_id(self, now: float) -> int:
        return int(now // self.window_seconds)

    def allow(self, user_id: str, now: float | None = None) -> bool:
        now = now if now is not None else time.monotonic()
        wid = self._window_id(now)
        key = (user_id, wid)
        with self._lock:
            c = self._counts.get(key, 0)
            if c < self.limit:
                self._counts[key] = c + 1
                return True
            return False


def demo_boundary_burst() -> None:
    """Illustrate the 2x-limit issue at the window boundary."""
    rl = FixedWindowCounterLimiter(limit=3, window_seconds=1.0)

    # Window W1 ends at t=1.0. Send 3 reqs in last 0.1s of W1.
    t = 0.9
    print("Last 0.1s of window 1:")
    for _ in range(3):
        print(f"  t={t:.2f}: {'ALLOW' if rl.allow('u', t) else 'DENY'}")

    # Window W2 starts at t=1.0. Send 3 more in first 0.1s of W2.
    t = 1.05
    print("First 0.1s of window 2:")
    for _ in range(3):
        print(f"  t={t:.2f}: {'ALLOW' if rl.allow('u', t) else 'DENY'}")

    print("\n=> 6 requests allowed within ~0.2s, though limit is 3 / 1s.")


if __name__ == "__main__":
    demo_boundary_burst()
