# System Design — Patterns & Components Cheat Sheet

> **Keep this open while practicing.** Skim it after each problem to see if you missed a pattern that applied.

---

## Choosing a Database

| If you need... | Use | Examples |
|---|---|---|
| ACID, relational data, joins | RDBMS | Postgres, MySQL |
| Massive write throughput, time-series | Wide-column | Cassandra, ScyllaDB |
| Flexible schema, document-shaped | Document DB | MongoDB, DynamoDB |
| Low-latency lookups, caching | KV store | Redis, Memcached |
| Full-text search | Search engine | Elasticsearch, OpenSearch |
| Graph traversal | Graph DB | Neo4j |
| Geo queries | Geo-indexed | Postgres+PostGIS, geohash in any KV |
| Analytics/OLAP | Column store | ClickHouse, BigQuery, Redshift |

**Default for an interview if unsure:** Postgres for transactional + Redis for cache + S3 for blobs. Justify upgrades from there.

---

## Caching Strategies

- **Cache-aside (lazy load):** app reads cache, falls back to DB on miss, populates cache. Default choice.
- **Write-through:** writes go to cache + DB synchronously. Consistent but slower writes.
- **Write-back (write-behind):** writes go to cache, async to DB. Fast but risk of loss.
- **Refresh-ahead:** proactively refresh hot keys before expiry.

**Eviction:** LRU is the default. LFU when access patterns are skewed. TTL always set.

**Watch for:**
- **Thundering herd** → use request coalescing / locks
- **Cache stampede** on expiry → jittered TTLs
- **Cache penetration** (queries for non-existent keys) → negative caching

---

## Sharding / Partitioning

- **Range-based:** sort by key. Simple, supports range queries. Risk: hotspots.
- **Hash-based:** hash(key) → shard. Even distribution. Risk: no range queries.
- **Consistent hashing:** add/remove nodes without rehashing everything. Default for distributed caches and KV stores.
- **Geo-based:** shard by region. Good for latency and compliance.

Always name your **partition key** explicitly when discussing the data model.

---

## Replication

- **Leader-follower (single leader):** writes to leader, reads from followers. Eventual consistency on reads. Most common.
- **Multi-leader:** writes to any leader, leaders sync. Conflict resolution needed.
- **Leaderless (Dynamo-style):** writes go to multiple nodes, quorum (W + R > N) for consistency.

---

## Async Processing

Use a queue (Kafka, SQS, RabbitMQ) when:
- Work doesn't need to block the user
- Smoothing traffic spikes
- Decoupling producers and consumers
- Retries with backoff

| Tool | Use when |
|---|---|
| **Kafka** | High throughput, ordered within partition, replay-able. Default for event streams. |
| **SQS** | Simple, managed, at-least-once delivery. Default for task queues. |
| **RabbitMQ** | Flexible routing, lower throughput than Kafka. |

---

## Consistency Models (Know These Names)

- **Strong:** all reads see the latest write. Expensive across regions.
- **Eventual:** reads may be stale, will converge. Default for AP systems.
- **Read-your-writes:** a user sees their own writes immediately.
- **Monotonic reads:** never go backwards in time.
- **Causal:** related writes are seen in causal order.

### CAP / PACELC (one-liner)

Under network **P**artition, choose between **C**onsistency and **A**vailability. **E**lse (no partition), choose between **L**atency and **C**onsistency. Most real systems lean AP + eventual; banking-style systems lean CP.

---

## Common Protocols

- **HTTP/REST** — default for public APIs
- **gRPC** — internal service-to-service, binary, fast
- **WebSocket** — bidirectional, persistent (chat, live updates)
- **Server-Sent Events** — server→client streaming, simpler than WebSocket
- **Long polling** — fallback when WS isn't available

---

## Geo-Indexing (for location problems)

- **Geohash:** encode lat/lng into a string; prefix similarity ≈ proximity. Simple.
- **Quadtree:** recursive 4-way space partition. Good for variable density.
- **H3 (Uber):** hexagonal hierarchical. Uniform neighbors.
- **R-tree:** bounding box index. Built into Postgres+PostGIS.

---

## Reliability Building Blocks

- **Health checks** + load balancer eviction
- **Circuit breakers** to stop cascading failures
- **Bulkheads** to isolate failure domains
- **Retries with exponential backoff + jitter**
- **Idempotency keys** on all unsafe writes
- **Dead-letter queues** for poison messages

---

## Latency Numbers Every Engineer Should Know

| Operation | Latency |
|---|---|
| L1 cache reference | ~1 ns |
| Branch mispredict | ~3 ns |
| L2 cache reference | ~4 ns |
| Mutex lock/unlock | ~17 ns |
| Main memory reference | ~100 ns |
| Compress 1 KB with Zippy | ~2 µs |
| Send 1 KB over 1 Gbps network | ~10 µs |
| SSD random read | ~150 µs |
| Read 1 MB sequentially from memory | ~250 µs |
| Round trip within same datacenter | ~500 µs |
| Read 1 MB sequentially from SSD | ~1 ms |
| Disk seek | ~10 ms |
| Read 1 MB sequentially from disk | ~30 ms |
| Cross-continent round trip | ~150 ms |

---

## Resources

- **Xu, *System Design Interview Vol 1 & 2*** — your starting point, already done.
- **Kleppmann, *Designing Data-Intensive Applications*** — read chapters 5, 6, 7, 9 for depth on replication, partitioning, transactions, consistency.
- **hellointerview.com** — written walkthroughs, common patterns, mock interviews.
- **bytebytego.com** (Xu's blog) — keep up with new posts.
- **github.com/donnemartin/system-design-primer** — free reference.
- **YouTube:** Jordan Has No Life (rigorous), Tech Dummies (walkthroughs), Exponent (mock-style).
- **Mock interview platforms:** Pramp (free peer), Hello Interview (paid), Exponent.
