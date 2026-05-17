# Chapter 8: Design A URL Shortener

A URL shortener turns a long URL into a short alias (`tinyurl.com/abc123`) and **redirects** anyone who hits the alias back to the original. Read-heavy, simple data model, big scale.

```
   POST  longUrl  ──►   ┌──────────────┐  ──►  shortUrl  (write, rare)
                        │  Shortener   │
   GET   shortUrl  ──►  │  service     │  ──►  301/302 → longUrl  (read, common)
                        └──────────────┘
   Ratio ≈ 100 : 1  (reads ≫ writes)
```

---

## Requirements

**Functional**
- Shorten: given a long URL, return a short URL.
- Redirect: given a short URL, redirect to the original long URL.
- Short URL should be as short as possible and hard to guess (optional).

**Non-functional**
- High availability (a dead redirector breaks every link ever issued).
- Low latency redirect (it sits in the user's click path).
- Scalable to billions of URLs; links effectively never expire.

**Questions to ask the interviewer**
- Traffic volume? (drives the estimation below)
- Length / character set of the short URL? (affects encoding choice)
- Custom/vanity aliases allowed? Do links ever expire or get deleted?
- Do we need click analytics? (this decides 301 vs 302)
- Read-heavy or write-heavy? (almost always read-heavy → cache)

---

## Back-of-the-envelope estimation

Assume **100 million** new URLs written per day.

```
   Writes/sec  = 100,000,000 / 86,400 ≈ 1,160 writes/sec
   Reads/sec   = 100 : 1 read:write   ≈ 116,000 reads/sec
```

10-year storage:

```
   Records over 10 yr = 100M/day × 365 × 10 ≈ 365 billion records
   Bytes per record   ≈ 500 bytes (id, short, long URL, meta)
   Total storage      = 365e9 × 500 B ≈ 182.5 TB
```

| Metric            | Value (approx)         |
| ----------------- | ---------------------- |
| Write QPS         | ~1.2 K/sec             |
| Read QPS          | ~117 K/sec             |
| Records / 10 yr   | ~365 billion           |
| Storage / 10 yr   | ~180 TB                |
| Read:write ratio  | ~100:1 (read-heavy)    |

Takeaways: this is a **read-heavy** system → cache aggressively, optimize the redirect path. Storage is large but not insane → a sharded relational store or KV store both work.

---

## API endpoints

A clean REST design — two endpoints.

| Method | Endpoint                     | Body / Param        | Returns                       |
| ------ | ---------------------------- | ------------------- | ----------------------------- |
| POST   | `/api/v1/data/shorten`       | `{ "longUrl": …}`   | `201` + `shortUrl`            |
| GET    | `/api/v1/shortUrl`           | path: `{shortUrl}`  | `301`/`302` → `longUrl`       |

```
   POST /api/v1/data/shorten
   { "longUrl": "https://example.com/very/long/path?x=1" }
   ──► 201 Created
   { "shortUrl": "https://tiny.url/aZ8kQ1" }

   GET /aZ8kQ1
   ──► 301 Moved Permanently
       Location: https://example.com/very/long/path?x=1
```

---

## URL redirecting: 301 vs 302

The redirect is an HTTP response with a `Location` header. Choosing the status code is a real interview discussion.

| Aspect          | 301 Moved Permanently             | 302 Found (temporary)              |
| --------------- | --------------------------------- | ---------------------------------- |
| Browser caching | Cached — future hits skip server  | Not cached — every hit re-asks     |
| Server load     | Lower (browser remembers)         | Higher (every click reaches you)   |
| Analytics       | **Lose** repeat-click tracking    | **Full** click tracking            |
| Use when        | URL is truly permanent, save load | You want analytics / may change it |

```
   301:  click → browser cache hit → straight to longUrl   (server not hit again)
   302:  click → tiny.url server every time → 302 → longUrl  (you count every click)
```

> Rule of thumb: pick **302** if analytics matter (most commercial shorteners do); pick **301** to minimize server load.

---

## URL shortening logic

We need a function `shortUrl = f(longUrl)` where `shortUrl` is short and decodable back to the long one (via lookup).

**Length math.** With a base-62 alphabet `[0-9a-zA-Z]` (62 chars):

```
   62^6 ≈ 56.8 billion   ← 6 chars not enough for 365B records
   62^7 ≈ 3.5 trillion   ← 7 chars comfortably covers 365B
```

So a **7-character** short string over base62 is the target length.

### Approach 1 — Hash + collision resolution

Hash the long URL (MD5/SHA-1/CRC32), take the first 7 chars of the hex/base62 digest.

```
   longUrl ──► MD5 ──► 32 hex chars ──► take first 7 ──► short
                                         │
                                         ▼
                            collision? (two URLs → same 7)
                            → append a salt / recursively rehash
                              until the short is unique
```

- **Pro:** stateless-ish, same URL naturally maps to same short (idempotent).
- **Con:** truncating a hash → collisions; each write needs a DB check ("does this short exist?") and a retry loop. Extra read per write.

### Approach 2 — Base 62 conversion

Maintain a global **auto-increment ID**. Convert the unique integer ID to base62.

```
   id = 2,009,215,674,938
   convert to base62 ──► "zn9edcu"   (7 chars)
   reverse: base62 → id → DB lookup by id → longUrl
```

- **Pro:** **no collisions ever** (ID is unique by construction); short length grows predictably; reversible.
- **Con:** IDs are sequential → short codes are guessable/enumerable; needs a unique ID generator (DB sequence, or a distributed generator like Snowflake / a ZooKeeper range allocator).

### Hash vs base62

| Property              | Hash + collision        | Base 62                       |
| --------------------- | ----------------------- | ----------------------------- |
| Fixed short length    | Yes (truncate)          | No (grows with id)            |
| Collision possible    | Yes — needs resolution  | **No** (unique id)            |
| Extra DB lookup/write | Yes (collision check)   | No                            |
| Guessable next URL    | No                      | Yes (sequential) — add noise  |
| Needs ID generator    | No                      | Yes (sequence / Snowflake)    |
| Idempotent same URL   | Naturally               | Only with a uniqueness index  |

> Interview answer: **base62 + unique ID** is the cleaner default (no collision loop). If guessability matters, use a distributed ID generator and/or shuffle the alphabet.

---

## Database design

The data model is trivial — it is a key→value mapping with a primary key. At 180 TB / 365 B rows you shard, but the schema is small.

| Column     | Type          | Notes                                  |
| ---------- | ------------- | -------------------------------------- |
| `id`       | BIGINT PK     | auto-increment / Snowflake; base62 src |
| `shortUrl` | VARCHAR(7)    | unique index, the lookup key           |
| `longUrl`  | VARCHAR(2048) | original URL                           |
| `createdAt`| TIMESTAMP     | for analytics / TTL                    |

```
   ┌───────────────────────────────────────────┐
   │  urls                                      │
   ├──────────┬───────────┬─────────┬───────────┤
   │ id (PK)  │ shortUrl  │ longUrl │ createdAt │
   │ 1209476  │ "aZ8kQ1"  │ http... │ ...       │
   └──────────┴───────────┴─────────┴───────────┘
   Index on shortUrl (read path) + unique on longUrl (idempotency)
```

- A relational DB is fine; a KV store (DynamoDB / Cassandra) shines at this scale and access pattern (point lookups by key).
- Shard by `shortUrl` hash (or by id range) once a single node is exhausted.

---

## Cache & load balancer

Reads dominate (~117 K/sec). Put a cache in front of the DB; the access pattern (point lookup, hot links) is cache-perfect.

```
        ┌────────────┐
   ─►   │ Load        │  ─►  app server 1 ─┐
        │ Balancer    │  ─►  app server 2 ─┼─► ┌────────┐  miss  ┌──────────┐
   ─►   │ (round-     │  ─►  app server N ─┘   │ Cache  │ ─────► │   DB      │
        │  robin)     │                        │(Redis) │ ◄───── │ (sharded) │
        └────────────┘                         └────────┘  fill  └──────────┘
```

- **Cache:** Redis/Memcached keyed by `shortUrl → longUrl`. LRU eviction; hit ratio is very high (a few links get most clicks). On miss → read DB, backfill cache.
- **Load balancer:** spreads read/write traffic across stateless app servers; enables horizontal scale and rolling deploys.

---

## Deep dive

### Write path (shorten)

```
   client ──► LB ──► app server
                       │ 1. validate longUrl
                       │ 2. (idempotency) longUrl already shortened? → return existing
                       │ 3. get unique id  (DB sequence / Snowflake)
                       │ 4. short = to_base62(id)
                       │ 5. INSERT (id, short, longUrl, ts)
                       ▼
                     return shortUrl
```

- **Idempotency:** unique index on `longUrl` so the same long URL returns the same short (saves space, predictable).
- **ID generation:** a single auto-increment column is a bottleneck/SPOF across shards → use **Snowflake-style** 64-bit IDs or a range-allocator (each app server leases a block of IDs).

### Read path (redirect)

```
   click ──► LB ──► app server
                      │ 1. short = path segment
                      │ 2. cache.get(short)  ── hit ──► longUrl
                      │            └── miss ─► DB lookup ─► backfill cache
                      ▼
                    301 / 302 → Location: longUrl
```

- This path must be the fastest thing in the system — it is in the user's click latency budget. Cache hit → sub-ms.
- 404 if the short code does not exist.

### Rate limiter

A huge attack/abuse surface: someone can hammer `POST /shorten` (storage exhaustion) or enumerate short codes. Add a rate limiter (see Ch. 4) keyed by IP / API key at the gateway.

```
   client ──► [Rate Limiter @ gateway] ──► shorten/redirect
                  │ exceed quota
                  ▼  HTTP 429
```

### Analytics

Commercial value lives here ("how many clicks, from where, when, what device"). This is why most shorteners pick **302** (every click hits the server).

```
   redirect handler ──► emit click event ──► message queue (Kafka)
                                                 │
                                                 ▼
                                       analytics pipeline / warehouse
                                       (clicks, geo, referrer, UA, time)
```

- Fire-and-forget the event to a queue so analytics never slows the redirect.
- Aggregate offline; expose dashboards.
- Captured per click: timestamp, short code, IP→geo, referrer, user-agent.

### Availability and scaling

- App servers are **stateless** → scale horizontally behind the LB; any server handles any request.
- DB is **sharded** (by `shortUrl` hash or `id` range) and **replicated** (read replicas absorb the read fan-out beyond cache).
- The redirect path tolerates a stale cache (URLs are immutable) → cache can be huge and aggressively warmed.
- Multi-region: replicate the cache + read replicas close to users; writes can funnel to a primary region (writes are rare).

```
   region A ─┐                ┌─ region B
   cache+RR  ├─ async repl ───┤  cache+RR
             └──► primary DB ◄─┘  (writes ~1.2K/s, easy)
```

---

## Real-world usage

| System          | Notes                                                        |
| --------------- | ------------------------------------------------------------ |
| **Bitly**       | base-conversion style codes, heavy click analytics, 301/302  |
| **TinyURL**     | classic short alias service                                  |
| **t.co (X/Twitter)** | wraps every link; used for safety + analytics           |
| **YouTube `youtu.be`** | the video ID *is* effectively a base62-ish key         |
| **git short SHAs** | same idea: shortest unique prefix of a hash               |

---

## Trade-offs and gotchas

- **301 vs 302** is an analytics-vs-load trade — be ready to argue both.
- **Sequential IDs are enumerable** — shuffle the base62 alphabet, add a checksum char, or hash the id to de-correlate.
- **Custom aliases** (vanity `tiny.url/my-brand`) → need an availability check + reserved-word list.
- **Link expiration / deletion** → add TTL + cleanup job; redirect handler must 410/404 expired links.
- **ID generator is the real hard part at scale** — single auto-increment is a SPOF; Snowflake / range allocation fixes it.
- **Hot keys** — a viral link can hammer one cache shard; replicate hot entries.
- **Cache stampede** on a popular missing/expired key — use request coalescing or a short negative cache.
- **Abuse** — shorteners are used to mask phishing; add URL scanning / blocklists.

---

## Common follow-up questions

- *"How do you generate unique IDs across many app servers?"* → Snowflake (timestamp + machine id + sequence) or a ZooKeeper/DB range allocator that leases blocks of IDs per server. Avoid a single global auto-increment (SPOF + contention).
- *"Why not just hash the URL?"* → truncated hashes collide; you pay an extra DB read per write to detect/resolve. Base62(id) never collides.
- *"How do you prevent enumeration of all links?"* → shuffle the base62 alphabet, add a checksum char, or hash the id; do not expose raw sequential codes.
- *"How do you handle a viral link?"* → it's a hot cache key; replicate it across cache nodes / use a local in-process cache layer in front of Redis.
- *"What if the same URL is submitted twice?"* → unique index on `longUrl`; return the existing short (idempotent, saves storage).

---

## One-page summary

```
   GOAL: long URL ⇄ short alias, billions of links, read-heavy (100:1)

   SCALE:   ~1.2K writes/s, ~117K reads/s, ~180 TB / 10 yr
   ENCODE:  base62(unique id)  → no collisions, 7 chars (62^7≈3.5T)
            (alt) hash+truncate → collision retry loop
   API:     POST /shorten → 201 shortUrl ; GET /short → 301|302
   REDIR:   302 if analytics matter, 301 to shed load
   STORE:   KV/sharded SQL (id, shortUrl, longUrl) + Redis cache
   PATHS:   write = id→base62→insert ; read = cache→DB→redirect
   GUARD:   rate limiter @ gateway ; analytics via async queue
```

## Notes
_Add your own notes here._
