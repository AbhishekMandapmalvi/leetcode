"""
Leaky-bucket rate limiter.

- Per user, requests enter a FIFO queue of fixed capacity.
- Queue drains at constant `leak_rate` requests/second.
- If queue is full when a request arrives -> reject.
- Output is smoothed to a constant rate (no bursts).
"""

import threading
import time
from collections import deque
from dataclasses import dataclass


@dataclass
class _BucketState:
    queue: deque  # holds enqueue timestamps
    last_leak: float


class LeakyBucketLimiter:
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity
        self.leak_rate = leak_rate  # requests per second leaving the bucket
        self._buckets: dict[str, _BucketState] = {}
        self._lock = threading.Lock()

    def _leak(self, b: _BucketState, now: float) -> None:
        # Number of requests that should have leaked since last_leak.
        elapsed = now - b.last_leak
        leaked = int(elapsed * self.leak_rate)
        if leaked > 0:
            for _ in range(min(leaked, len(b.queue))):
                b.queue.popleft()
            b.last_leak = now

    def allow(self, user_id: str) -> bool:
        now = time.monotonic()
        with self._lock:
            b = self._buckets.get(user_id)
            if b is None:
                b = _BucketState(queue=deque(), last_leak=now)
                self._buckets[user_id] = b

            self._leak(b, now)
            if len(b.queue) < self.capacity:
                b.queue.append(now)
                return True
            return False


if __name__ == "__main__":
    rl = LeakyBucketLimiter(capacity=3, leak_rate=2)  # leak 2/sec, queue 3

    print("Burst of 5 requests (cap=3):")
    for i in range(5):
        print(f"  req {i+1}: {'ALLOW' if rl.allow('bob') else 'DENY'}")

    time.sleep(1.0)
    print("\nAfter 1s (~2 leaked):")
    for i in range(3):
        print(f"  req {i+1}: {'ALLOW' if rl.allow('bob') else 'DENY'}")
