# Chapter 13: Design A Search Autocomplete System

A search autocomplete (typeahead) returns the **top-k most popular queries** that start with whatever the user has typed so far, on **every keystroke**, in under ~100 ms. The core data structure is a **trie with the top-k completions cached at every node**, fed by an offline pipeline that aggregates query frequencies.

```
   user types:  d → di → din → dinn
                                  │
                                  ▼
                 ┌──────────────────────────┐
                 │  top-k for prefix "dinn"  │
                 │  1. dinner                │
                 │  2. dinner near me        │
                 │  3. dinnerware            │
                 └──────────────────────────┘
```

---

## Requirements

- **Fast** — suggestions must return in **< 100 ms** (slower feels laggy, the box is useless).
- **Relevant** — suggestions match the prefix and are **popular** (ranked by historical search frequency).
- **Sorted** — results ordered by popularity (frequency).
- **Scalable** — billions of queries; high QPS (a query *per keystroke*, not per search).
- **Highly available** — degrade, never go down.

Scope: top **5** suggestions; ranked by **frequency** only (no personalization/spelling-correction in the core design); ASCII first, Unicode later.

### Latency budget (< 100 ms)
A suggestion is requested on *every keystroke*, so the budget is tiny:

| Stage                          | Budget   |
| ------------------------------ | -------- |
| Client → server network        | ~20 ms   |
| Server lookup (trie/cache)     | **< 10 ms** |
| Server → client network        | ~20 ms   |
| Browser render                 | ~rest    |
| **Total target**               | **< 100 ms** |

> Implication: the lookup itself must be near-O(1). No SQL `LIKE` per keystroke, no sorting at query time.

### Back-of-envelope

```
   10M DAU, ~10 searches/day → 100M searches/day
   each search ≈ 20 keystrokes → ~2B autocomplete requests/day
   2B / 86400 ≈ 24K QPS (avg), peak ~5x ≈ 120K QPS
   ⇒ read-heavy, precomputed; writes (frequency updates) are batched offline
```

---

## High-level: two services

```
   ┌─────────────────────┐         ┌───────────────────────┐
   │  Data gathering     │  build  │   Query service       │
   │  service (offline)  │ ──trie──►│  (online, read-only)  │
   │  aggregate frequency│         │  prefix → top-k        │
   └─────────▲───────────┘         └───────────▲───────────┘
             │ analytics logs                   │ keystroke
        search queries                      autocomplete box
```

### Data gathering service
Consumes the **search log** and builds a **frequency table** `query -> count` (aggregated weekly/periodically). This is the source of truth that the trie is built from.

```
   user searches ──► Analytics logs ──► Aggregator (MapReduce / Spark)
                                              │
                                              ▼
                                       Frequency table
                                       query -> count
                                              │ build
                                              ▼
                                          Trie  ──► (atomic swap into query service)
```

| query              | frequency |
| ------------------ | --------- |
| `dinner`           | 1,200,000 |
| `dinner near me`   |   780,000 |
| `dinnerware`       |   140,000 |
| `dim sum`          |   430,000 |

### Query service — why naive SQL is too slow
The obvious approach:

```sql
SELECT query, frequency FROM frequency_table
WHERE query LIKE 'dinn%'
ORDER BY frequency DESC
LIMIT 5;
```

This **does not scale**:

- `LIKE 'prefix%'` over billions of rows even with an index, then a **sort** of all matches — far more than 10 ms.
- Runs on **every keystroke** → crushing QPS on the DB.
- We need the answer **precomputed**, not computed at request time. ⇒ **Trie.**

The query path we actually want:

```
   keystroke ──► LB ──► Query server ──► [shard-map] ──► Trie shard
                              │                              │
                              │ ◄──────── node.top_k ─────────┘
                              ▼
                        [ filter layer ] ──► top-k safe suggestions
                        (also: cache hot prefixes here)
```

---

## The trie

A trie (prefix tree) stores strings by character along a path from the root. The prefix is the path; descendants of a node are all completions of that prefix.

```
                (root)
                  │
                  d
                 / \
                i   o
               /     \
              n       g
             / \       \
            n   ●(dim)   ●(dog)
           /
          e
          │
          r ●(dinner)
```

### Store top-k frequencies at each node (the key optimization)
Walking the subtree to collect + sort completions on every keystroke is too slow. Instead, **cache the top-k completions (with frequency) directly at each node**. Then:

```
   query("dinn")  =  walk 4 chars to node "dinn"  →  return node.top_k
                     O(prefix length)  ≈ O(1)      O(1) (already sorted)
```

| Trie node field | Meaning                                            |
| --------------- | -------------------------------------------------- |
| `children`      | map char → child node                              |
| `is_word`       | this path is a complete query                      |
| `frequency`     | search count for the word ending here              |
| `top_k`         | **cached** list of `(word, freq)`, the best k under this prefix |

Trade-off: O(k) extra storage per node and update cost on every node along the inserted word's path — paid **offline at build time**, not at query time. Query becomes blisteringly fast.

### Limit the max prefix length
Users rarely type 60-char prefixes; a trie of unbounded depth wastes memory and the deep nodes are never queried. **Cap prefix length at `p`** (say 50). Query is then **O(p)** = effectively constant, and the trie depth is bounded.

---

## Updating the trie

The frequency of queries changes constantly. Two strategies:

| Strategy           | How                                                            | When to use                                  |
| ------------------ | -------------------------------------------------------------- | -------------------------------------------- |
| **Weekly offline rebuild** | Workers rebuild the whole trie from the aggregated frequency table on a schedule; atomically swap it in | **Default.** Autocomplete tolerates staleness; rankings shift slowly. Simple, robust. |
| **Real-time update**       | Stream search logs (Kafka) → aggregate with **Hive / Spark** → update trie nodes & their `top_k` along the path | Trending/breaking topics (Twitter). Much more complex; usually not needed. |

> Most products choose the **weekly offline** rebuild — rankings don't need second-level freshness, and an offline batch is far simpler and safer than mutating a hot, shared trie in place.

---

## Trie operations

### Create
The trie is **built offline** from the frequency table by a fleet of workers using **MapReduce**:

- **Map:** emit `(query, count)` from search logs.
- **Reduce:** sum counts per query → the frequency table.
- **Build:** insert each `query` with its frequency; while inserting, update `top_k` on every node along the path.

### Update
Either rebuild the whole trie (weekly), or — for the real-time variant — for a single query, walk its path and re-evaluate `top_k` at each ancestor (a node's `top_k` only changes if the updated word's frequency now beats its current k-th best).

### Delete (filter layer for unsafe queries)
We must **not** suggest hateful, dangerous, legally sensitive, or spammy queries. Don't try to scrub the trie itself — instead put a **filter layer between the trie and the API**: the trie returns top results, the filter removes anything on the blocklist before returning to the client. Cheap, centrally managed, and reversible.

```
   client ──► API ──► [ Trie: top-k ] ──► [ Filter layer ] ──► safe results
                                          (remove unsafe)
```

---

## Scale the storage (sharding the trie)

One trie won't fit in one machine's memory at web scale → **shard it**.

### Naive: shard by first character
26 shards (`a`–`z`). Problem: **non-uniform** — far more queries start with `s` or `c` than `x` or `z`. The `s` shard melts while `z` idles.

### Better: shard by character, then by frequency (smart sharding)
Use a **shard-map service** that assigns prefixes to shards based on **historical frequency / volume**, so each shard carries a roughly equal load. E.g. `a, b, c → shard 1`; `s → shard 2`; `t..z → shard 3`. The map is computed from the same frequency data and stored in a lookup service.

| Sharding           | Balance        | Complexity | Verdict                          |
| ------------------ | -------------- | ---------- | -------------------------------- |
| First character    | poor (skewed)  | low        | naive baseline                   |
| Char + frequency (shard map) | good | medium     | **chosen** — even load           |

```
   prefix ──► [ Shard-map service ] ──► shard id ──► Trie shard ──► top-k
              (built from frequency,    rebalanced on the weekly job)
```

Also: replicate each shard for HA + read throughput; cache the hottest prefixes at the query servers.

---

## Other talking points

- **Multi-language / Unicode** — store **Unicode codepoints** as trie keys instead of ASCII chars; nodes branch on Unicode characters. Different languages can even live in different tries/shards.
- **Personalization** — global popularity is the base; blend per-user signals (history, location, demographics) at request time as a re-ranking layer on top of trie results. Stated as a follow-up, not core.
- **Real-time / trending** — combine the offline trie with a small, fast "trending" overlay updated from a stream for breaking events.
- **Why not return on every keystroke from the DB** — see naive SQL above; everything is precomputed.
- **Browser caching / debounce** — client caches recent prefixes and debounces keystrokes to cut QPS.

---

## Real-world usage

| System                     | Autocomplete approach                                  |
| -------------------------- | ------------------------------------------------------ |
| **Google / Bing** search   | precomputed prefix structures + heavy ranking & personalization |
| **Elasticsearch**          | completion suggester (FST — finite state transducer, a compressed trie) |
| **Amazon / e-commerce**    | product/query trie ranked by popularity + conversions  |
| **IDE autocomplete**       | tries / radix trees over symbols                       |
| **Redis (RediSearch)**     | suggestion dictionary with scores                      |

---

## Trade-offs and gotchas

- **Build-time vs query-time cost** — caching `top_k` at nodes shifts all work to the offline build; query is O(prefix). This is the whole trick.
- **Staleness vs complexity** — weekly rebuild is stale but simple; real-time is fresh but hard. Pick by product need.
- **Memory** — top-k at every node is significant; cap prefix length, prune low-frequency words, shard.
- **Sharding skew** — sharding by first letter is tempting and wrong; use frequency-aware shard map and rebalance with the rebuild.
- **Safety** — never bake the blocklist into the trie; a separate filter layer is reversible and centrally controlled.
- **Atomic swap** — rebuild a new trie offline and hot-swap it; never mutate the serving trie under live traffic.

---

## One-page summary

```
   GOAL: top-k popular completions for a prefix, < 100 ms, every keystroke

   WHY NOT SQL: LIKE 'p%' + ORDER BY over billions per keystroke = too slow
   STRUCTURE:   Trie ; cache top-k (word,freq) AT EACH NODE
                query = walk prefix (O(p)) → return node.top_k (already sorted)
   BOUND:       cap max prefix length p  → query ≈ O(1)
   BUILD:       data-gathering service → frequency table (MapReduce)
                build trie offline, atomic swap
   UPDATE:      weekly offline rebuild (default) ; real-time via Hive/Spark
   DELETE:      filter layer between trie and API (unsafe queries)
   SCALE:       shard by char THEN by frequency (shard-map), replicate, cache
   EXTRA:       Unicode keys ; personalization as re-rank overlay
```

## Notes
_Add your own notes here._
