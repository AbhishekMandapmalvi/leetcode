# Chapter 16: The Learning Continues

The book ends, but system design is a moving target. This chapter is a **curated study map**: read real engineering blogs, extract the *one technique* each company is famous for, and keep a habit of learning. Patterns repeat — once you've seen sharded IDs or fan-out-on-write, you recognize them everywhere.

```
   Read book ─► Read real architectures ─► Spot the repeating pattern
        ▲                                            │
        └──────────── revisit & re-derive ◄──────────┘

   real world = {scaling} ∪ {perf+DB} ∪ {microservices}
              ∪ {payments} ∪ {streaming} ∪ {realtime}
              ∪ {search} ∪ {ranking}
```

---

## Real-world architectures (one lesson each)

| Company / system        | Headline technique                          | Lesson to steal                                    |
| ----------------------- | ------------------------------------------- | -------------------------------------------------- |
| **Facebook timeline**   | Denormalized feed, aggressive caching       | Precompute the read path; reads ≫ writes           |
| **Instagram**           | Sharded IDs (time-ordered, shard-embedded)  | Generate sortable unique IDs without a central SPOF |
| **Netflix**             | Microservices + chaos engineering + CDN     | Design for failure; test it in prod (Chaos Monkey) |
| **Pinterest**           | Manual DB sharding, ID-encoded shard        | Shard early, encode the shard *into* the ID        |
| **Twitter timeline**    | Hybrid fan-out + heavy cache (Redis)        | Fan-out-on-write for most, on-read for celebrities |
| **Uber**                | Geo-sharding, dispatch, event-driven        | Partition by geography; everything is a stream     |
| **WeChat**              | Super-app, message fan-out at scale         | One pipe, many products; mailbox model for msgs    |
| **YouTube**             | CDN tiering, transcode DAG (see Ch14)       | Egress is the bill; tier hot vs long-tail          |

> Don't memorize architectures — extract the **reusable primitive**. Almost every row above is one of: precompute reads, shard smartly, embrace failure, or stream events.

---

## Scalability primers (the foundation to revisit)

The recurring toolkit behind every blog post above:

```
   horizontal scale ─► stateless services + LB
   read scale       ─► cache (look-aside) + read replicas
   write scale      ─► shard / partition + async via queue
   availability     ─► replication + failover + multi-AZ/region
   failure          ─► assume it; retry, timeout, circuit-break, bulkhead
```

- Re-read Ch1 (scale 0→millions), Ch2 (estimation), Ch3 (interview framework) before any interview — they generalize every later chapter.
- Recommended primers: the classic "Scalability for Dummies" series, Google SRE book, *Designing Data-Intensive Applications* (Kleppmann), the AWS / GCP architecture centers, and the High Scalability blog archive.

---

## Performance & databases

| System / pattern        | Technique                                                  |
| ----------------------- | ---------------------------------------------------------- |
| **Twitter cache**       | Redis fronting timelines; cache the *materialized* feed     |
| **Instagram sharded IDs** | 41-bit time + 13-bit shard + 10-bit seq → sortable, unique, decentralized |
| **Pinterest sharding**  | App-level sharding; shard id baked into every object id     |

```
   Instagram-style 64-bit ID
   ┌────────────── 41 bits ─────────────┬─ 13 ─┬─ 10 ─┐
   │           ms since epoch           │ shard│ seq  │
   └────────────────────────────────────┴──────┴──────┘
   sortable by time, globally unique, no central allocator
```

- DB scaling order: index → cache → read replicas → vertical → **shard**. Sharding is last because it removes cross-shard joins and transactions.
- Cache patterns to know: look-aside, write-through, write-back, TTL + jitter to avoid stampedes.
- Connects to Ch7 (unique ID generators) and Ch6 (key-value stores).

---

## Microservices

| Company     | Contribution                                                    |
| ----------- | --------------------------------------------------------------- |
| **Yelp**    | Service-oriented migration off a monolith; API gateway pattern  |
| **Spotify** | **Event delivery** system — reliable, ordered event pipeline at scale |

```
   Monolith ──► extract bounded contexts ──► services
                                  │
                          API gateway / service mesh
                                  │
            sync (gRPC/REST) for queries,
            async (event bus) for state-change propagation
```

- Trade-off: independent deploy/scaling vs distributed-system tax (network, partial failure, eventual consistency, observability cost).
- Spotify's lesson: an **event-delivery backbone** decouples services; treat events as the integration contract.

---

## Payment systems

```
   Order ─► Payment service ─► PSP (Stripe/Adyen) ─► Banks
              │     ▲
              ▼     │ webhook (async result)
          Ledger (double-entry, append-only)
```

- **Idempotency keys** — retries must not double-charge.
- **Exactly-once via the ledger** — money is a double-entry, append-only ledger; reconcile against the PSP daily.
- **Sagas** for distributed commit (reserve → charge → fulfill, with compensations).
- Consistency over availability: when in doubt, fail the payment, never the books.

---

## Stream processing (Kafka)

```
   Producers ─► [ Kafka topic | partitioned, replicated log ] ─► Consumers
                  └ ordered per partition, retained, replayable
   Use: event sourcing, async fan-out, log/metrics pipeline, CDC
```

- The unifying abstraction behind Uber, Spotify, WeChat, news feeds: an **append-only partitioned log**.
- Ordering is per-partition; pick the partition key deliberately (e.g. user_id).
- Enables replay, decoupling, and backpressure — the default integration layer for modern systems.
- Ties back to Ch10 (notifications), Ch11 (news feed fan-out).

---

## Real-time messaging (Slack)

```
   Client ── WebSocket ──► Gateway ──► Channel/message service
                              │              │
                         presence        message store + fan-out
```

- **WebSocket** for low-latency bidirectional push; long-poll fallback.
- Per-channel fan-out; presence is a separate, cheaper subsystem.
- Builds directly on Ch12 (chat system): connection servers, mailbox, online status.

---

## Search (Twitter Earlybird)

```
   Tweet ─► ingest ─► inverted index (sharded by time) ─► query merge
                       Earlybird = real-time, in-memory, segmented index
```

- **Inverted index**, sharded; recent segments kept in memory for real-time search.
- Trade recall/freshness vs cost: hot recent shards in RAM, older shards colder.
- Connects to Ch13 (search autocomplete) and the web-crawler chapter.

---

## Ranking (ML at scale)

```
   Candidate gen (cheap recall) ─► Lightweight rank ─► Heavy ML rerank ─► Feed
   features: real-time (clicks) + batch (history)   |  served from a feature store
```

- Multi-stage funnel: retrieve thousands cheaply, score the top hundreds with a heavy model.
- **Feature store** + online/offline parity; log-and-train loop.
- Used in every feed/recommendation system (Facebook, Pinterest, YouTube, Twitter).

---

## Continuous-learning resources

- **Engineering blogs:** Netflix, Uber, Meta, Airbnb, Discord, Cloudflare, Stripe, Dropbox.
- **Books:** *Designing Data-Intensive Applications* (Kleppmann), Google *SRE* book, *System Design Interview Vol 2* (Xu).
- **Papers:** Dynamo, Bigtable, MapReduce, Kafka, Raft, Spanner, Chubby.
- **Habit:** read one architecture write-up a week, redraw it from memory, name the primitive it uses, and map it to a chapter you've already studied.

---

## Trade-offs and gotchas

- **Patterns > architectures** — companies differ in scale and constraints; the primitive is portable, the exact design is not.
- **Everything is a trade-off** — articulate what you're sacrificing (consistency, cost, latency, complexity), not just what you gain.
- **Newer ≠ better** — a monolith + Postgres beats microservices + Kafka until you actually have the scale to justify them.
- **Always estimate first** — Ch2's back-of-envelope decides whether you even need the fancy design.

---

## One-page summary

```
   STUDY ROADMAP

   1. Re-derive fundamentals  → Ch1 scale, Ch2 estimate, Ch3 framework
   2. One blog post / week    → redraw from memory, name the primitive
   3. Map every story to:
        precompute reads | shard smart | embrace failure | stream events
   4. Core primitives to own:
        sharded IDs · fan-out (write vs read) · cache patterns
        partitioned log (Kafka) · inverted index · multi-stage ranking
        idempotent payments · saga/ledger
   5. Always: estimate → pick trade-off → state what you sacrifice
```

## Notes
_Add your own notes here._
