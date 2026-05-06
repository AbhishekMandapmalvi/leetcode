"""
Distributed rate limiter using Redis with an atomic Lua script.

Algorithm: fixed-window counter (simplest and most common in the wild).
Atomic via Lua so multiple limiter processes can share state safely.

Run a local Redis first:
    docker run --rm -p 6379:6379 redis:7

Then:
    pip install redis
    python redis_distributed_limiter.py
"""

import time

try:
    import redis  # type: ignore
except ImportError:
    raise SystemExit("pip install redis")


# KEYS[1] = counter key
# ARGV[1] = window_seconds (TTL)
# ARGV[2] = limit
# Returns: 1 if allowed, 0 if denied.
LUA_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
if current > tonumber(ARGV[2]) then
    return 0
end
return 1
"""


class RedisFixedWindowLimiter:
    def __init__(self, client: "redis.Redis", limit: int, window_seconds: int):
        self.client = client
        self.limit = limit
        self.window_seconds = window_seconds
        self._script = client.register_script(LUA_SCRIPT)

    def _key(self, user_id: str, now: float) -> str:
        bucket = int(now // self.window_seconds)
        return f"rl:{user_id}:{bucket}"

    def allow(self, user_id: str) -> bool:
        key = self._key(user_id, time.time())
        result = self._script(keys=[key], args=[self.window_seconds, self.limit])
        return result == 1


if __name__ == "__main__":
    client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    rl = RedisFixedWindowLimiter(client, limit=5, window_seconds=2)

    print("Send 8 requests (limit=5 / 2s):")
    for i in range(8):
        ok = rl.allow("alice")
        print(f"  req {i+1}: {'ALLOW' if ok else 'DENY'}")
