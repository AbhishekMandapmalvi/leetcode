"""
Sliding-window counter rate limiter (Cloudflare-style approximation).

estimate = current_window_count
         + previous_window_count * (1 - elapsed_fraction_of_current_window)

Memory: O(1) per user (just two counters and a window id).
Accuracy: very high in practice; assumes uniform distribution within prev window.
"""

import threading
import time
from dataclasses import dataclass


@dataclass
class _State:
    window_id: int = 0
    curr_count: int = 0
    prev_count: int = 0


class SlidingWindowCounterLimiter:
    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window_seconds = window_seconds
        self._state: dict[str, _State] = {}
        self._lock = threading.Lock()

    def _window_id(self, now: float) -> int:
        return int(now // self.window_seconds)

    def allow(self, user_id: str, now: float | None = None) -> bool:
        now = now if now is not None else time.monotonic()
        wid = self._window_id(now)
        elapsed_frac = (now % self.window_seconds) / self.window_seconds

        with self._lock:
            s = self._state.setdefault(user_id, _State(window_id=wid))

            # Roll forward as needed.
            if wid == s.window_id + 1:
                s.prev_count = s.curr_count
                s.curr_count = 0
                s.window_id = wid
            elif wid > s.window_id + 1:
                s.prev_count = 0
                s.curr_count = 0
                s.window_id = wid

            estimate = s.curr_count + s.prev_count * (1 - elapsed_frac)
            if estimate < self.limit:
                s.curr_count += 1
                return True
            return False


if __name__ == "__main__":
    rl = SlidingWindowCounterLimiter(limit=5, window_seconds=1.0)

    # Fill 5 in window 1.
    print("Window 1 (t=0.5): send 6 ->")
    for _ in range(6):
        print(f"  {'ALLOW' if rl.allow('u', 0.5) else 'DENY'}")

    # Just into window 2 (elapsed_frac small) -> previous window heavily counted.
    print("\nEarly window 2 (t=1.05): send 3 ->")
    for _ in range(3):
        print(f"  {'ALLOW' if rl.allow('u', 1.05) else 'DENY'}")

    print("\nLate window 2 (t=1.95): send 3 ->")
    for _ in range(3):
        print(f"  {'ALLOW' if rl.allow('u', 1.95) else 'DENY'}")
