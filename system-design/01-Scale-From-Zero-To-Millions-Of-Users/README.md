# Chapter 1: Scale From Zero To Millions Of Users

Build a system that supports a single user and gradually scale it up to serve millions of users.

## Key Topics

### Single server setup
**1. Once we enter URL in browser, how do we connect to the web server and get a response back?**
1. User types URL → browser asks **DNS** to resolve the domain to an IP. DNS is usually a 3rd-party paid service, not part of your servers.
2. DNS returns an IP (e.g. `15.125.23.214`) → browser opens a TCP connection to that IP on port 80/443.
3. Browser sends an HTTP(S) request → web server processes it (may query DB) → returns HTML/JSON response.
4. Two traffic sources to plan for: **web app** (server-rendered HTML/JSON, business logic) and **mobile app** (HTTP + JSON over REST).

```
                  ┌─────────┐  1. resolve api.mysite.com   ┌──────────┐
                  │         │ ───────────────────────────► │   DNS    │
                  │ Browser │ ◄─────────────────────────── │ (3rd-pty)│
                  │         │  2. 15.125.23.214            └──────────┘
                  │   or    │
                  │ Mobile  │  3. HTTP request             ┌──────────┐
                  │  App    │ ───────────────────────────► │   Web    │
                  │         │ ◄─────────────────────────── │  Server  │
                  └─────────┘  4. HTML / JSON response     └──────────┘
```

---

### Database (vertical vs horizontal scaling, replication)
Once traffic grows, separate the **web tier** and **data tier** so they can scale independently.

```
   Single server                   Web tier + Data tier
   ─────────────                   ────────────────────
   ┌───────────┐                   ┌──────────┐    ┌──────────┐
   │  Web +    │       ───►        │ Web      │ ─► │ Database │
   │  DB on    │                   │ Server(s)│    │  Server  │
   │  one box  │                   └──────────┘    └──────────┘
   └───────────┘                   scale separately
```

**Vertical vs horizontal scaling**

```
   Vertical (scale UP)              Horizontal (scale OUT)
   ───────────────────              ──────────────────────
        ┌──────┐                   ┌────┐  ┌────┐  ┌────┐
        │      │                   │ S1 │  │ S2 │  │ S3 │ …
        │BIGGER│                   └────┘  └────┘  └────┘
        │ box  │                   add more boxes
        │      │
        └──────┘
   limited by hardware              near-unlimited; needs LB
```

**1. Types of Databases**

**1.1 Relational / SQL** — store data in tables/rows; tables joined via SQL.
- Examples: MySQL, PostgreSQL, Oracle, MS SQL Server.
- Pros: mature, ACID transactions, strong consistency, expressive joins.
- Cons: rigid schema, harder to scale horizontally, joins expensive at huge scale.

**1.2 Non-Relational / NoSQL** — schema-flexible; usually no joins.

**1.2.1 Four main types of NoSQL**
- **1.2.1.1 Key-value store** — simple `key → value` lookup. Examples: Redis, Memcached, Amazon DynamoDB.
- **1.2.1.2 Graph store** — nodes + edges, optimized for relationships (social graph, fraud). Examples: Neo4j, Amazon Neptune.
- **1.2.1.3 Column store** — wide-column families, great for write-heavy / time-series / analytics. Examples: Cassandra, HBase, Google Bigtable.
- **1.2.1.4 Document store** — JSON-like documents, flexible schema. Examples: MongoDB, CouchDB, Amazon DocumentDB.

**1.2.2 Pros and cons of NoSQL**
- Pros: low latency, scales horizontally, schema flexible, great for unstructured data and very large datasets.
- Cons: weaker (often eventual) consistency, limited/no joins, no cross-document ACID, app must enforce integrity.

Choose NoSQL when you need very low latency, unstructured data, huge volume, and don't need joins/ACID.

**1.2.3 Vertical scaling (scale up)** — bigger CPU/RAM/disk on one server.
- Pros: simple, no app changes.
- Cons: hard hardware ceiling, single point of failure, expensive at the top end, no failover.

**1.2.4 Horizontal scaling (scale out)** — add more servers and split work.
- Pros: near-unlimited capacity, fault tolerant, cost effective.
- Cons: complexity (data distribution, consistency, ops).
- For DBs this means **sharding**, **replication**, or both.

---

### Load balancer
**What is a load balancer?**
A component that distributes incoming traffic across a pool of servers behind a single public IP/VIP.

**How it works (brief)**
- Clients hit the LB's public IP.
- LB forwards each request to a healthy backend over a private IP.
- LB performs health checks; unhealthy servers are pulled out automatically.
- Solves: single-server failure, traffic spikes, easy horizontal scaling.

```
                                   ┌──────────┐ private IP
                                ┌─►│  Server1 │
                                │  └──────────┘
   ┌────────┐    ┌──────────┐   │  ┌──────────┐
   │ Client │ ─► │   Load   │ ──┼─►│  Server2 │
   └────────┘    │ Balancer │   │  └──────────┘   (health-check ✓/✗)
   public IP    └──────────┘   │  ┌──────────┐
                                └─►│  Server3 │   ✗ removed if unhealthy
                                   └──────────┘
```

**Common load-balancing strategies**
- **Round robin** — simple rotation.
- **Weighted round robin** — more traffic to bigger boxes.
- **Least connections** — send to the least-busy server.
- **Least response time** — send to the fastest server.
- **IP hash / consistent hash** — sticky by client IP (useful for session affinity).

**Data replication**
- **Definition:** keep copies of the same data on multiple DB servers (master/slave, aka primary/replica).
- **How it works (briefly):** master takes all writes; changes are streamed to one or more slaves which serve reads.

```
                writes ──►  ┌────────────┐  replicate  ┌──────────┐
                            │  MASTER    │ ──────────► │  SLAVE 1 │ ◄─ reads
                            │  (writes)  │ ──────────► │  SLAVE 2 │ ◄─ reads
                            └────────────┘ ──────────► │  SLAVE 3 │ ◄─ reads
                                                       └──────────┘
                if MASTER dies → promote a SLAVE to new MASTER
```
- **Pros:** read throughput scales across replicas; high availability (promote a replica if master dies); disaster recovery; geographical distribution.
- **Cons:** replication lag → stale reads; write throughput still bound by master; failover complexity.
- **Common replication strategies:**
  - **Master–slave (single leader)** — one writer, many readers.
  - **Multi-master** — multiple writers, conflict resolution required.
  - **Synchronous** — wait for replicas (strong consistency, slower writes).
  - **Asynchronous** — don't wait (fast, may lose recent writes on failover).
  - **Semi-synchronous** — at least one replica must ack.

---

### Cache (cache tier, considerations, distributed cache)
**Definition**
A fast (usually in-memory) temporary store for the results of expensive queries/computations, sitting between the app and the DB.

**How it works (briefly) — read-through pattern**
1. Web server checks the cache.
2. **Hit** → return cached value.
3. **Miss** → query DB, write result to cache (with TTL), return.
Write paths vary: write-through, write-back, write-around.

```
   ┌──────────┐  1. get(key)   ┌────────┐
   │   Web    │ ─────────────► │ Cache  │
   │  Server  │ ◄───────────── │ (Redis)│
   └──────────┘   2a. HIT      └────────┘
        │                          ▲
        │ 2b. MISS                 │ 4. set(key, value, TTL)
        ▼                          │
   ┌──────────┐                    │
   │ Database │ ───────────────────┘
   └──────────┘  3. row from DB
```

**Cache tier**
A dedicated, horizontally-scalable cache layer (Redis, Memcached) that the web tier hits before the DB. Separating it from app servers lets it scale independently and survive app-server churn.

**Considerations**
- **When to use:** read-heavy, data rarely modified, can tolerate slight staleness.
- **TTL/expiration:** too short → many DB hits; too long → stale data.
- **Consistency:** keep DB and cache in sync (hard across regions); pick a write policy.
- **Eviction policy:** LRU (default), LFU, FIFO when full.
- **Single point of failure:** run multiple cache nodes across AZs/regions.
- **Memory sizing:** under-sized cache thrashes via constant eviction; over-provision.
- **Distributed cache:** shard data across multiple nodes (often via consistent hashing) so capacity grows with the cluster.

---

### Content Delivery Network (CDN)
**Definition**
A geographically distributed network of edge servers that cache and serve **static content** (images, CSS, JS, video) close to the user.

**How it works (briefly)**
1. User requests `image.png`.
2. Request routed to nearest CDN edge.
3. **Hit** → edge serves it directly (fast).
4. **Miss** → edge fetches from origin (your server / S3), caches with TTL, then serves.
5. Subsequent users in that region hit the edge directly.

```
    US user            EU user           ASIA user
       │                  │                  │
       ▼                  ▼                  ▼
   ┌────────┐         ┌────────┐         ┌────────┐
   │ Edge   │         │ Edge   │         │ Edge   │
   │ (US)   │         │ (EU)   │         │ (ASIA) │
   └────────┘         └────────┘         └────────┘
        \                 │                 /
         \  on MISS only  │  fetch upstream/
          \               ▼               /
                     ┌──────────┐
                     │  Origin  │  (your S3 / app server)
                     └──────────┘
```

**Considerations**
- **Cost:** charged per data transfer out — don't cache rarely-accessed content.
- **TTL/expiry:** balance freshness vs origin load.
- **Cache invalidation:** call the CDN's purge API or version the URL (`image.png?v=2`).
- **Fallback:** clients should be able to fetch from origin if CDN is down.
- **Static vs dynamic:** classic CDNs serve static; modern CDNs (Cloudflare, CloudFront) also do dynamic acceleration and edge compute.
- Examples: Cloudflare, Akamai, AWS CloudFront, Fastly.

---

### Stateless web tier
**Stateful architecture (definition)**
The server keeps client session data (logged-in user, cart, etc.) in its own memory between requests.
- **Pros:** simple, fast for the request that hits the same server.
- **Cons:** client must always be routed to the same server (sticky sessions); adding/removing servers is hard; that server's failure loses the session; autoscaling is awkward.

**Stateless architecture (definition)**
Servers hold no session state. Any request can be handled by any server. Session data lives in a shared store (Redis, DynamoDB, RDBMS) or is sent in a token (JWT) by the client.
- **Pros:** trivial horizontal scaling; easy autoscaling; fault tolerant (any server can take over); works behind any LB strategy.
- **Cons:** extra round-trip to fetch session data; the session store itself must be HA.

**Rule of thumb:** keep the web tier stateless; push state to a shared persistent store.

```
   STATEFUL (sticky)                  STATELESS (any server)
   ─────────────────                  ──────────────────────
   user A ─► Server1 [sessA]          user A ─► LB ─► any  ┐
   user B ─► Server2 [sessB]          user B ─► LB ─► any  │ all read/write
   user C ─► Server3 [sessC]          user C ─► LB ─► any  │ session in
                                                           ▼
   if Server1 dies, sessA lost        ┌──────────────────────┐
                                      │ Shared session store │
                                      │  (Redis / DynamoDB)  │
                                      └──────────────────────┘
```

---

### Data centers (geoDNS, failover)
- **Why multiple data centers:** lower latency for global users, disaster recovery, regional compliance.
- **geoDNS:** resolves the same domain to different IPs based on user location → user routed to the **nearest** data center.
- **Failover:** if a DC goes down, geoDNS reroutes traffic to a healthy DC; DNS-layer health checks trigger this.

```
                      ┌──────────────┐
                      │   geoDNS     │  routes by user location
                      └──────┬───────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  DC-US   │   │  DC-EU   │   │ DC-ASIA  │
        └──────────┘   └──────────┘   └──────────┘
              ▲              ▲              ▲
              └──────── data replication ───┘
        if DC-US ✗ → US users routed to DC-EU
```
- **Challenges:**
  - **Traffic redirection** — DNS TTL controls how fast users move on failure.
  - **Data sync** — replicate data across DCs so a redirected user finds her data (often async multi-master).
  - **Test & deploy** — automate testing in each region; deploy with blue/green or canary.

---

### Message queue
**Definition**
A durable, asynchronous buffer that decouples producers (write events) from consumers (process events).

**How it works (briefly)**
- Producers publish messages to a queue/topic.
- Queue stores messages durably (in order or by partition).
- Consumers pull (or get pushed) messages and process them.
- Producer and consumer are decoupled — either can be down/scaled independently.

```
   ┌──────────┐  publish   ┌──────────────┐  consume   ┌──────────┐
   │ Producer │ ─────────► │   Queue      │ ─────────► │ Worker 1 │
   │ (web)    │            │ [m1][m2][m3] │ ─────────► │ Worker 2 │
   └──────────┘            └──────────────┘ ─────────► │ Worker N │
                                                       └──────────┘
   producer & consumer scale independently;
   queue absorbs traffic spikes
```

**Why use one**
- Smooth out traffic spikes (buffer bursts).
- Move slow tasks (image resize, email send, video transcode) off the request path.
- Scale producers and consumers independently.
- Built-in retries and dead-letter queues.

**Types and examples**
- **Message queue (point-to-point):** RabbitMQ, ActiveMQ, AWS SQS.
- **Distributed log / pub-sub stream:** Apache Kafka, AWS Kinesis, Google Pub/Sub, Apache Pulsar.
- **Lightweight broker:** Redis Streams / Lists.

---

### Logging
- Capture errors, requests, and important events to diagnose issues.
- Per-server logs aren't enough at scale → ship to a centralized service.
- Tools: ELK (Elasticsearch + Logstash + Kibana), Splunk, AWS CloudWatch, Datadog.
- Add a **request ID** to trace a single request across services.

### Metrics
- **Host-level:** CPU, memory, disk I/O, network.
- **Aggregated:** DB tier perf, cache hit rate.
- **Business:** DAU, retention, revenue.
- Tools: Prometheus + Grafana, Datadog, New Relic, CloudWatch.
- Alert on SLO violations (latency, error rate, saturation, traffic — RED/USE methods).

### Automation
- **CI/CD** for build/test/deploy → faster releases, fewer regressions.
- Tools: Jenkins, GitHub Actions, GitLab CI, CircleCI.
- **Infra-as-code** (Terraform, CloudFormation) for reproducible environments.

---

### Database scaling
At some scale even a replicated DB can't keep up — the **master is still the write bottleneck**.

**Vertical scaling (scale up)** — bigger box; same pros/cons as before. Hits a hardware ceiling and remains a SPOF.

**Horizontal scaling = Sharding**
- Partition data across multiple DB servers; each shard holds a subset.
- Each shard has the same schema; total dataset = union of shards.
- **Sharding key (partition key):** the column that decides which shard a row lives on (e.g. `user_id % N`).
- A good shard key spreads load evenly.

```
   row with user_id = K   ─►  shard = hash(K) mod 4

   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Shard 0 │  │ Shard 1 │  │ Shard 2 │  │ Shard 3 │
   │ users   │  │ users   │  │ users   │  │ users   │
   │ %4 = 0  │  │ %4 = 1  │  │ %4 = 2  │  │ %4 = 3  │
   └─────────┘  └─────────┘  └─────────┘  └─────────┘
   total data = union of all shards; each shard has same schema
```

**Sharding challenges**
- **Resharding:** when a shard fills up or load is uneven, data must be redistributed → use **consistent hashing** (Chapter 5) to minimize movement.
- **Celebrity/hotspot problem:** one key (e.g. a celebrity account) gets disproportionate traffic → sub-shard or replicate that key.
- **Joins across shards:** hard — denormalize or join in the application layer.

**NoSQL**
- Many NoSQL systems handle sharding/replication for you (DynamoDB, Cassandra, MongoDB).
- Often adopted to scale beyond what a sharded SQL cluster can handle.

---

## Putting it all together — millions-of-users architecture
1. **Stateless web tier** behind a **load balancer**.
2. Multiple **data centers**, routed via **geoDNS**, with cross-region data replication.
3. **CDN** for static content.
4. **Cache tier** (Redis/Memcached) in front of the DB.
5. **DB** uses **replication** for reads and **sharding** for writes.
6. **Message queue** + **workers** for async work.
7. **Logging, metrics, automation** baked in from day one.

```
                              ┌──────────┐
        users ─► geoDNS ──►   │   CDN    │  (static assets)
                              └──────────┘
                                   │ dynamic
                                   ▼
                              ┌──────────┐
                              │   Load   │
                              │ Balancer │
                              └────┬─────┘
                       ┌───────────┼───────────┐
                       ▼           ▼           ▼
                   ┌──────┐    ┌──────┐    ┌──────┐
                   │ Web1 │    │ Web2 │    │ WebN │   stateless
                   └──┬───┘    └──┬───┘    └──┬───┘
                      └───────────┼───────────┘
                ┌─────────────────┼─────────────────────┐
                ▼                 ▼                     ▼
         ┌───────────┐    ┌──────────────┐      ┌────────────┐
         │  Cache    │    │  Session     │      │  Message   │
         │ (Redis)   │    │  Store       │      │  Queue     │
         └─────┬─────┘    └──────────────┘      └─────┬──────┘
               │ miss                                 ▼
               ▼                                ┌──────────┐
        ┌─────────────┐    replicate            │ Workers  │
        │  DB Master  │ ─────────────────►  Slaves (reads) │
        │  + Shards   │                        └──────────┘
        └─────────────┘
                          ── all of this lives in each Data Center ──
                          ── replicated across DCs via geoDNS ──
```

## Notes
_Add your own notes here._
