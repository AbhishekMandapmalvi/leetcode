"""
Token-bucket rate limiter (single-process, thread-safe).

- Each user has a bucket of capacity `capacity`.
- Tokens refill at `refill_rate` tokens/second up to `capacity`.
- A request consumes one token; if no token available -> reject.
- Allows bursts up to `capacity`.
"""

import threading
import time
from dataclasses import dataclass


@dataclass
class _Bucket:
    tokens: float
    last_refill: float


class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def allow(self, user_id: str) -> bool:
        now = time.monotonic()
        with self._lock:
            b = self._buckets.get(user_id)
            if b is None:
                b = _Bucket(tokens=float(self.capacity), last_refill=now)
                self._buckets[user_id] = b

            # Refill based on elapsed time.
            elapsed = now - b.last_refill
            b.tokens = min(self.capacity, b.tokens + elapsed * self.refill_rate)
            b.last_refill = now

            if b.tokens >= 1:
                b.tokens -= 1
                return True
            return False


if __name__ == "__main__":
    rl = TokenBucketLimiter(capacity=5, refill_rate=2)  # 2/sec, burst 5

    print("Burst of 7 instant requests (cap=5):")
    for i in range(7):
        print(f"  req {i+1}: {'ALLOW' if rl.allow('alice') else 'DENY'}")

    time.sleep(1.0)  # ~2 tokens refill
    print("\nAfter 1s sleep:")
    for i in range(3):
        print(f"  req {i+1}: {'ALLOW' if rl.allow('alice') else 'DENY'}")
