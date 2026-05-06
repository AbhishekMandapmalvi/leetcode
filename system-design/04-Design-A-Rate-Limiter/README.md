# Chapter 4: Design A Rate Limiter

A rate limiter restricts how many requests a client can send to an API in a given time window. Excess requests are **rejected** (or queued/throttled).

```
   Allowed:  ✓ ✓ ✓ ✓ ✓        Limit: 5 req/sec per user
                       ✗ ✗ ✗   Excess → blocked (HTTP 429)
   ──────────────────────────► time
```

---

## Why rate limiting?

- **Prevent abuse / DoS** — stop a single bad actor from overwhelming the service.
- **Reduce cost** — fewer wasteful calls (especially expensive 3rd-party APIs, LLMs, payments).
- **Prevent server overload** — protect downstream DBs, queues, services from spikes.
- **Fairness** — one greedy client cannot starve others.
- **Tier enforcement** — free vs paid plans get different quotas.

Examples in the wild
- Twitter: 300 tweets / 3 hours
- Google Docs: 300 read req / 60 s / user
- AWS / GitHub: documented per-API quotas with `X-RateLimit-*` headers

---

## Where to put the rate limiter

```
   Client ──► [Rate Limiter] ──► API Server
                  │ (reject)
                  ▼
              429 + Retry-After
```

| Location          | Pros                                    | Cons                                |
| ----------------- | --------------------------------------- | ----------------------------------- |
| **Client-side**   | Cheap                                    | Easily bypassed; not trusted        |
| **Server-side**   | Trusted, full control                   | Couples logic to app code           |
| **Middleware / API gateway** | Centralized, reusable, language-agnostic | Adds a hop                |

> Rule of thumb: in a microservices world, put it in the **API gateway** (Kong, Envoy, AWS API Gateway, NGINX). For monoliths, server-side middleware is fine.

---

## Algorithms

### 1. Token bucket
Each user has a bucket holding up to `N` tokens, refilled at a constant rate `r tokens/sec`. Each request consumes a token. Empty bucket → reject.

```
   Refill rate: 1 token / 200 ms          Bucket capacity: 4
   ┌───────────────┐
   │ ● ● ● ●       │  ◄─ tokens
   └───────────────┘
       │ each request takes 1 token
       ▼
   request   ✓     ✓     ✓     ✓     ✗ (empty) ✓ (refilled)
```

- **Pros:** simple, memory-efficient, allows **bursts** up to bucket size.
- **Cons:** two parameters to tune (capacity + refill rate).
- **Used by:** Amazon, Stripe.

### 2. Leaking bucket
A FIFO queue of fixed size. Requests join the queue; processed at a constant **leak rate**. Full queue → reject.

```
   Incoming ──► ┌──────────────┐ ──► leak at fixed rate ──► API
                │ ░ ░ ░ ░      │
                │ FIFO queue   │
                └──────────────┘
                   full → drop
```

- **Pros:** smooth, constant outflow → predictable downstream load.
- **Cons:** burst-unfriendly; recent requests may starve if queue is full of old ones.
- **Used by:** Shopify.

### 3. Fixed window counter
Time is split into fixed windows (e.g. 1-second buckets). A counter tracks requests in the current window; resets when the window flips.

```
   limit = 3 / sec
   t:  |--- 1s ---|--- 1s ---|--- 1s ---|
   req:  ● ● ● ●     ● ●         ●
         ✓ ✓ ✓ ✗     ✓ ✓         ✓
```

- **Pros:** trivially simple (`INCR key; EXPIRE 1s`).
- **Cons:** **boundary burst** — 2× limit can fit in 1 sec straddling the window boundary.

```
   Window edge problem:
   |--- 0..1s ---|--- 1..2s ---|
            ● ● ●  ● ● ●
            (3 in last 0.5 s of W1) + (3 in first 0.5 s of W2)
            = 6 requests in 1 second though limit is 3/sec
```

### 4. Sliding window log
Store a timestamp per request in a sorted set (e.g. Redis `ZADD`). On each request: drop entries older than the window, then `ZCARD`. Allow if size ≤ limit.

```
   limit = 3 in last 60 s
   Sorted set (timestamps): [12:00:01, 12:00:30, 12:00:55]
   New request at 12:00:58 → size=4 ✗ reject
   New request at 12:01:05 → drop 12:00:01 → size=3 ✓ allow
```

- **Pros:** **highly accurate**, no boundary burst.
- **Cons:** memory grows with traffic (one entry per request).

### 5. Sliding window counter
Hybrid of fixed window + sliding window log. Approximates the rate using a weighted average of the previous and current window counters.

```
   prev_count = 60   curr_count = 30
   Now = 75% into the current window
   estimate = curr_count + prev_count × (1 - 75%)
            = 30 + 60 × 0.25
            = 45
```

- **Pros:** small memory, no boundary burst.
- **Cons:** approximation (assumes uniform distribution within prev window). Used in production by Cloudflare with very low error (<0.003%).

### Algorithm comparison

| Algorithm        | Memory | Burst friendly | Smoothness | Accuracy |
| ---------------- | ------ | -------------- | ---------- | -------- |
| Token bucket     | O(1)   | ✅              | medium     | high     |
| Leaking bucket   | O(N)*  | ❌              | high       | high     |
| Fixed window     | O(1)   | partial        | low        | low (boundary issue) |
| Sliding log      | O(N)*  | ✅              | high       | very high |
| Sliding counter  | O(1)   | ✅              | high       | high (approx) |
| *N = current queue/log size |   |                |            |          |

---

## High-level architecture

```
                 ┌──────────────────────────────────┐
   Client ──►    │           API Gateway            │  ──► API server
                 │  ┌────────────────────────────┐  │
                 │  │      Rate Limiter MW       │  │
                 │  │  1. lookup user/key        │  │
                 │  │  2. INCR counter in Redis  │  │
                 │  │  3. compare to rule limit  │  │
                 │  └────────────────────────────┘  │
                 └──────┬───────────────────────────┘
                        │
                        ▼
                 ┌──────────────┐    ┌──────────────────┐
                 │   Redis      │ ◄──│  Rules cache     │
                 │  counters    │    │ (loaded from     │
                 │  INCR/EXPIRE │    │  rule store/disk)│
                 └──────────────┘    └──────────────────┘
```

**Why Redis**
- In-memory → sub-ms latency.
- Atomic ops (`INCR`, `INCRBY`, `EXPIRE`) — race-free counters.
- Built-in TTL = automatic window expiration.
- Lua scripts / `WATCH-MULTI-EXEC` for multi-step atomicity.

**Reject path**
- Drop and respond `HTTP 429 Too Many Requests`.
- OR enqueue for later (rare, only for non-realtime).

---

## Rate limiter rules (Lyft style)

Rules are config-as-code (YAML), loaded into the rate limiter on startup and cached.

```yaml
domain: messaging
descriptors:
  - key: message_type
    value: marketing
    rate_limit:
      unit: day
      requests_per_unit: 5

  - key: auth_type
    value: login
    rate_limit:
      unit: minute
      requests_per_unit: 5
```

- **Domain** groups related rules.
- **Descriptor** is the dimension being limited (user, IP, API key, message type…).
- **Limit** = `requests_per_unit` per `unit` (sec/min/hour/day).

You can layer rules: per-user **and** per-IP **and** global.

---

## HTTP response headers

When a client is approaching or hitting the limit, set these headers so well-behaved clients can back off.

| Header                  | Meaning                                  |
| ----------------------- | ---------------------------------------- |
| `X-Ratelimit-Limit`     | Total allowed in window                  |
| `X-Ratelimit-Remaining` | Requests left in current window          |
| `X-Ratelimit-Retry-After` | Seconds to wait before retrying        |
| HTTP status `429`       | Too Many Requests                        |

```
   429 Too Many Requests
   X-Ratelimit-Limit: 100
   X-Ratelimit-Remaining: 0
   X-Ratelimit-Retry-After: 12
```

---

## Distributed environment: race conditions and synchronization

In a single-process limiter, an in-memory counter is fine. With **multiple rate-limiter instances** behind a LB, all sharing Redis, two issues arise:

### 1. Race condition on read–modify–write
```
   t1: read counter = 5
   t2: read counter = 5    ← two requests interleave
   t1: write counter = 6
   t2: write counter = 6   ← lost update; should be 7
```

**Fixes**
- Atomic `INCR` (Redis) — increment + return new value in one op.
- Lua scripts for "INCR + check + maybe rollback" atomically.
- `WATCH-MULTI-EXEC` (optimistic locking).
- ❌ Avoid global locks — kills throughput.

### 2. Synchronization across limiter instances
Multiple gateway instances must share state.

```
   ┌───────┐  ┌───────┐  ┌───────┐
   │ LR-1  │  │ LR-2  │  │ LR-3  │   limiter pods
   └───┬───┘  └───┬───┘  └───┬───┘
       └──────────┼──────────┘
                  ▼
         ┌─────────────────┐
         │ Centralized     │   single source of truth
         │ Redis cluster   │
         └─────────────────┘
```

- **Sticky sessions** also work (route a user always to the same pod) but break under failover and don't scale.
- **Centralized store (Redis)** is the standard answer.

---

## Performance optimization

- **Multi-region deployment** — keep the limiter near the user (lower RTT to gateway → lower added latency per request).
- **Eventual consistency between regions** — for global limits, periodic sync is OK; minor over-limit is acceptable.
- **Co-locate** the limiter with the gateway pod to avoid an extra network hop.
- **Cache rules in memory** with TTL refresh; don't read from disk per request.
- **Pipeline / batch Redis ops** when possible.

---

## Monitoring

Track:
- **Effectiveness** — how often is the limiter triggered? Per-user / per-route.
- **Latency** added by the limiter (P50/P95/P99) — should be sub-millisecond.
- **False positives** — legitimate users hitting limits → tune rules.
- **Algorithm fitness** — token bucket may be too lenient on bursty traffic; switch if needed.
- **Alerts** — if the limiter itself errors out, **fail open** vs **fail closed** is a deliberate choice (typically fail open, log loudly).

---

## Other talking points (for deep dive)

- **Hard vs soft limits** — soft warns; hard blocks.
- **Granularity** — per IP, per user, per API key, per route, per region. Layered rules.
- **Bypass for trusted clients** — internal services, allowlists.
- **Client-side back-off** — exponential back-off + jitter on 429s.
- **Rate-limiter as a service** — separate microservice (gRPC) so multiple gateways/services share it.
- **Levels** — application-level (HTTP) vs network-level (Iptables on IP-port at L3/L4).

---

## One-page summary

```
   GOAL: cap req/sec per (user|IP|key) without breaking the request path

   ALGO:    token bucket (default), sliding-window-counter (accurate)
   STORE:   Redis  ─ INCR + EXPIRE, atomic, sub-ms
   PLACE:   API gateway middleware
   REJECT:  HTTP 429 + Retry-After
   DIST:    centralized Redis avoids race; pipeline ops
   OBSERVE: P99 latency, hit rate, false positives
```

## Notes
_Add your own notes here._
