# System Design Interview — Process

> **Open this before every practice session.** The framework is what you're trying to make automatic. Use the template for each problem.

---

## The Interview Framework (Your Default Skeleton)

Use this exact structure for every problem. Interviewers grade on whether you're *organized*, not just on whether your answer is "right." Target split for a 45-min interview: **5 / 5 / 5 / 10 / 15 / 5**.

### Step 1 — Clarify Requirements (5 min)

Don't start drawing. Ask questions first. Always cover:

**Functional requirements** — what does the system *do*?
- What are the 2-3 core user actions? (e.g., post a tweet, view a feed)
- Anything explicitly out of scope? (e.g., no DMs, no ads)

**Non-functional requirements** — what are the *qualities*?
- Read-heavy or write-heavy? Ratio?
- Latency targets (p99)? Throughput?
- Consistency vs availability tradeoff — can users tolerate stale data?
- Durability — can we ever lose data?

**Scale**
- DAU / MAU?
- Requests per second?
- Data size / growth rate?
- Geographic distribution?

> **SDE 2 tip:** Drive this conversation, don't be quizzed. State assumptions explicitly: "I'll assume 100M DAU, 80/20 read/write — does that match what you had in mind?"

### Step 2 — Back-of-Envelope Estimation (5 min)

Compute in order:
- **QPS:** DAU × actions per user per day ÷ 86,400. Multiply peak by 2-5x.
- **Storage:** items/day × bytes/item × retention period.
- **Bandwidth:** QPS × avg payload size.
- **Cache size:** typically 20% of daily reads (80/20 rule).

Memorize these:

| Thing | Value |
|---|---|
| 1 day | ~86,400 sec (~100K) |
| L1 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| SSD random read | ~150 µs |
| Network round trip (same DC) | ~500 µs |
| Cross-continent round trip | ~150 ms |
| 1 KB / 1 MB / 1 GB / 1 TB | 10³ / 10⁶ / 10⁹ / 10¹² bytes |

### Step 3 — API Design (5 min)

List 4-6 endpoints. REST is fine; mention gRPC if it's an internal/high-throughput service.

```
POST /v1/<resource>      { body }     → returns <id>
GET  /v1/<resource>/<id>              → returns <object>
GET  /v1/<resource>?cursor=&limit=    → paginated list
```

Mention: auth (token in header), rate limiting, idempotency keys for writes.

### Step 4 — High-Level Architecture (10 min)

Draw left-to-right: **Client → Load Balancer → API Gateway → Services → Data Stores**, with cache and queues in the right places.

Default building blocks to consider every time:
- Load balancer (L4 or L7)
- API gateway (auth, rate limit, routing)
- Stateless app servers (horizontally scalable)
- Primary database (which type — see cheat sheet)
- Cache layer (Redis/Memcached)
- Async work queue (Kafka, SQS) for anything not user-blocking
- CDN for static/media
- Object storage (S3) for blobs

State your data model: 2-3 main tables/collections with key fields and the partition key.

### Step 5 — Deep Dive (15 min)

Pick **2-3** components the interviewer cares about. Common deep dives:
- The hot path (feed generation, search ranking, matching)
- The storage choice and sharding strategy
- A specific scaling bottleneck

For each: state the problem, list 2 options, pick one with justification, name the tradeoff you're accepting.

### Step 6 — Scale, Bottlenecks, Wrap-Up (5 min)

Walk through what breaks at 10x the load:
- Single points of failure → replicate
- Hot partitions → consistent hashing / re-shard
- Read amplification → cache layers / read replicas
- Write amplification → batching, async writes
- Geographic latency → multi-region, edge caches

End with: "Things I'd dive deeper on with more time: X, Y, Z."

---

## Per-Problem Template (Copy For Each Practice)

```
# Problem: <name>
Date:
Time taken:

## 1. Clarifications I asked
-
-

## 2. Assumptions
- DAU:
- Read/write ratio:
- Latency target:
- Consistency model:

## 3. Estimates
- QPS (avg / peak):
- Storage / year:
- Bandwidth:

## 4. APIs
-
-

## 5. Data model
- Table:
  - Fields:
  - Indexes:
  - PK / sharding key:

## 6. High-level diagram (describe)
Client → ... → DB

## 7. Deep dives
### Component A
- Problem:
- Options:
- Choice + reason:
- Tradeoff:

## 8. Bottlenecks at 10x
-
-

## 9. What I missed / would do differently
-
```

---

## Common Mistakes at SDE 2 Interviews

1. **Jumping to architecture before clarifying.** Always 5 min of questions first.
2. **Picking exotic tech to sound smart.** "We'll use Cassandra" without justification is worse than "we'll use Postgres because joins and ACID matter here."
3. **No numbers.** Saying "it scales" means nothing. "100K QPS, 5 TB/year, 50 ms p99" earns points.
4. **Missing the cache layer.** Almost every read-heavy system needs one. State it.
5. **Hand-waving the data model.** Write the 2-3 tables with key fields and the partition key.
6. **Not naming tradeoffs.** Every decision has a downside — say it out loud. ("I'm choosing eventual consistency here; the cost is users may briefly see stale data.")
7. **Ignoring failure.** Interviewer will ask "what if the DB goes down?" Have replication and failover ready.
8. **Running out of time on intro.** Budget time per section. 5/5/5/10/15/5 is a good split for 45 min.

---

## Quick Reference Card (Memorize)

- **The skeleton:** Clarify → Estimate → API → High-level → Deep dive → Bottlenecks.
- **The default stack:** Postgres + Redis + S3 + Kafka.
- **The default scaling moves:** Cache, replicate, shard, async, CDN.
- **The default tradeoff:** Consistency vs Availability vs Latency. Pick two, name what you sacrificed.
- **The thing interviewers grade:** Did you ask before drawing? Did you cite numbers? Did you name tradeoffs?
