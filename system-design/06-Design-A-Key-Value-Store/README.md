# Chapter 6: Design A Key-Value Store

A key-value store maps an opaque **key** to an opaque **value** (`put(key, value)` / `get(key)`). At scale it must be **distributed**: data spread across many nodes, replicated for durability, and available under failure — Dynamo / Cassandra style.

```
   put("user:42", {...})                 get("user:42")
        │                                      ▲
        ▼                                      │
   ┌──────────────────────────────────────────────┐
   │  Coordinator hashes key → ring of N nodes     │
   │  writes to W replicas, reads from R replicas  │
   └──────────────────────────────────────────────┘
        │        │        │        │
        ▼        ▼        ▼        ▼
      node0    node1    node2    node3   (each owns ring arcs)
```

---

## Requirements

- **API:** `put(key, value)`, `get(key)`. Key = string/hash; value = blob.
- **Small kv pairs** (< 10 KB), but billions of them.
- **Big data** — must scale horizontally; no single node holds everything.
- **Tunable** trade-offs: latency vs consistency vs availability.
- **High availability** — survive node and even datacenter failure.
- **Automatic scaling** — add/remove nodes with minimal disruption.

---

## Single-server key-value store

Start simple: an in-memory hash table.

```
   ┌──────────── memory ───────────┐
   │  "k1" → v1                     │
   │  "k2" → v2     hash table       │
   │  "k3" → v3     O(1) get/put     │
   └────────────────────────────────┘
```

- **Fast** — O(1) average, all in RAM.
- **Doesn't fit** — RAM is limited. Optimizations: **compress** values, **spill cold data to disk** (memory as cache).
- Even optimized, one server eventually hits a ceiling → must distribute.

---

## Distributed key-value store

A distributed kv store spreads pairs across many nodes. Designing it forces a confrontation with the **CAP theorem**.

### CAP theorem

In the presence of a **network Partition (P)** you must choose between **Consistency (C)** and **Availability (A)**. Partitions are unavoidable in distributed systems, so the real choice is **CP vs AP**.

```
        Consistency
            /\
           /  \
          / CA \      ◄─ ideal but impossible
         /  ⚠  \         once a partition happens
        /────────\
   CP  /          \  AP
      / pick under  \
     /   partition   \
    /─────────────────\
 Consistency       Availability
```

| Type   | Under partition | Behavior                                     | Example                |
| ------ | --------------- | -------------------------------------------- | ---------------------- |
| **CP** | sacrifice A     | block/refuse writes until consistent         | HBase, Bigtable, MongoDB (default), Zookeeper |
| **AP** | sacrifice C     | accept reads/writes, reconcile later         | Dynamo, Cassandra, Riak |
| **CA** | —               | impossible in a partition-prone network      | single-node RDBMS only |

> Example: replicas `n1, n2, n3`. If `n3` is partitioned away, a **CP** system rejects writes (no agreement possible) for consistency; an **AP** system keeps serving stale reads and accepts writes, healing when `n3` returns. This chapter designs an **AP** store (Dynamo-style) since availability is usually the priority for a kv store.

---

## System components

A Dynamo-style design needs answers for: partition, replication, consistency, conflict resolution, failure handling, write path, read path.

### 1. Data partition — consistent hashing

Split data across nodes so that (a) data is spread evenly and (b) adding/removing nodes moves minimal data. This is exactly **consistent hashing** (Chapter 5): place servers and keys on a hash ring; a key is owned by the first node clockwise; use **virtual nodes** for even load and to handle heterogeneous hardware.

```
              n0 ●
         n3 ●        ● k → walk clockwise → n1 owns k
                  ● n1
         n2 ●  ● vnodes scattered → even load
```

Benefits: **automatic scaling** (nodes join/leave cheaply) and **heterogeneity** (strong servers get more vnodes).

### 2. Data replication

For HA/durability, replicate each key to **N** nodes. Walk clockwise from the key's position and pick the first **N distinct physical** nodes (skip vnodes of a node already chosen) — this list is the **preference list**.

```
   key → ring pos
        │  clockwise, N=3, distinct physical nodes
        ▼
     [ n1 , n2 , n4 ]   ◄─ replicas (preference list)
       ^primary
```

For better fault tolerance, spread replicas across **racks / datacenters** so a single rack or DC failure doesn't lose all copies.

### 3. Consistency — N / W / R quorum

- **N** = number of replicas.
- **W** = write quorum: a write must be acked by `W` replicas to succeed.
- **R** = read quorum: a read must collect responses from `R` replicas.

A **coordinator** node fronts the client, fans out to replicas, and waits for the quorum.

```
   client ─put─► coordinator ──► n1  (ack)
                      ├────────► n2  (ack)   W=2 → return success
                      └────────► n3  (slow / later)
```

| Config            | Property                                  |
| ----------------- | ----------------------------------------- |
| `W + R > N`       | **strong consistency** (read sees latest write — quorum overlap) |
| `W = N, R = 1`    | fast reads, slow writes                    |
| `W = 1, R = N`    | fast writes, slow reads                    |
| `W + R ≤ N`       | **eventual consistency** (low latency, may read stale) |
| `W = 1`           | high availability for writes               |

Common Dynamo default: **N=3, W=2, R=2** (`W+R=4 > 3`) → strong-ish consistency with good availability.

**Consistency models**

| Model       | Guarantee                                                  |
| ----------- | ---------------------------------------------------------- |
| Strong      | every read returns the most recent write; reads block until agreed |
| Weak        | reads may not see the latest write                          |
| Eventual    | given no new writes, replicas converge; reads may be stale briefly (Dynamo / Cassandra) |

### 4. Inconsistency resolution — versioning & vector clocks

With concurrent writes to different replicas, versions diverge. Solution: treat each modification as a new **immutable version** and use a **vector clock** to detect causality vs true conflict.

A vector clock is a list of `[server, counter]` pairs attached to a value: `D([Sx, 1], [Sy, 2])`.

```
   D1 [Sx,1]                       writes are causal if one
       │ write by Sx               clock is an ancestor of the
   D2 [Sx,2]                       other → keep newer.
      / \  concurrent writes
   D3       D4                     conflict if neither is an
 [Sx,2]    [Sx,2]                  ancestor → siblings:
 [Sy,1]    [Sz,1]   ◄─ siblings → reconcile (client / app)
       \  /
        D5 [Sx,3][Sy,1][Sz,1]  ◄─ after reconciliation
```

- **Vy is an ancestor of Vx** (all of Vy's counters ≤ Vx's) → no conflict, Vx wins.
- Otherwise → **conflict / siblings**, returned to the client to merge (e.g. shopping-cart union).
- **Downside:** clocks grow with the number of writers; cap with a threshold + truncation (loses some history) — rarely an issue in practice.

### 5. Handling failures

**Failure detection — gossip protocol.** A single node's opinion ("n2 is down") isn't enough (it could be the reporter that's partitioned). Use **decentralized gossip**: each node holds a membership list with heartbeat counters; periodically each node bumps its own counter and gossips the list to random peers. If a node's counter hasn't advanced for a while, peers mark it **suspect**, then **down** once enough nodes agree.

```
   n0 ──gossip──► n2          membership list per node:
   n0 ──gossip──► n5          [ id | heartbeat | last_seen ]
        random peers           stale heartbeat → suspect → down
```

**Temporary failure — sloppy quorum + hinted handoff.** A strict quorum would block writes when replicas are down. Instead use a **sloppy quorum**: pick the first `W` healthy nodes on the ring (ignoring down ones). A substitute node accepts the write with a **hint** about the intended owner; when that owner recovers, the substitute **hands off** the data and deletes its copy. → high availability for writes.

```
   intended replica n2 is DOWN
   write goes to next healthy node n5 with hint "for n2"
        │
        ▼ when n2 returns
   n5 ──hand off──► n2,  then n5 drops the hinted copy
```

**Permanent failure — anti-entropy with Merkle trees.** To repair replicas that have drifted, compare data without shipping everything. Build a **Merkle tree** over each key range: leaves = hashes of buckets of keys, parents = hashes of children. Two replicas compare **root hashes**; if equal → in sync (0 data transferred). If different → recurse only into mismatched subtrees and sync only the differing keys.

```
          root                root
         /    \              /    \
       h01    h23          h01    h23'   ◄─ differs
      /  \    /  \              ...        recurse right only,
    h0  h1  h2  h3                         sync just that bucket
```

Cost: `O(log n)` comparison instead of scanning all keys.

**Datacenter outage.** Power loss, network outage, natural disaster. Mitigation: **replicate across multiple datacenters** so data survives a full DC loss; clients fail over to a healthy DC. (Trade-off: cross-DC writes add latency — often only `W=local quorum` is required synchronously, remote DCs replicated async.)

---

## Write path

(LSM-tree / SSTable engine, à la Cassandra / Bigtable.)

```
   put(k, v)
      │
      ▼
   ① append to commit log (WAL) on disk      ◄─ durability / crash recovery
      │
      ▼
   ② write to memtable (sorted in-memory structure, e.g. skiplist)
      │
      │  memtable full?
      ▼
   ③ flush memtable → new immutable SSTable on disk (sorted)
      │
      ▼
   ④ background compaction merges SSTables, drops tombstones
```

- The WAL makes the in-memory write **durable** before ack.
- Memtable keeps recent writes sorted and fast.
- SSTables are **immutable, sorted** files → sequential disk writes (fast).

---

## Read path

```
   get(k)
      │
      ▼
   ① is k in the memtable?  ── yes ──► return
      │ no
      ▼
   ② check Bloom filter per SSTable    ◄─ skip SSTables that
      │  (probably present?)              definitely lack k
      ▼
   ③ search candidate SSTables newest→oldest
      │  (sparse index → seek; merge versions)
      ▼
   ④ return latest value (or tombstone → "not found")
```

- A **Bloom filter** per SSTable avoids reading files that can't contain the key (no false negatives).
- A **sparse index** maps key ranges to file offsets so a lookup seeks instead of scanning.
- Reads may touch multiple SSTables → **read amplification**; compaction keeps it bounded.

---

## Storage engine: LSM tree + SSTable

| Term         | Meaning                                                              |
| ------------ | -------------------------------------------------------------------- |
| **LSM tree** | Log-Structured Merge tree: buffer writes in memory, flush sorted runs to disk, merge in background. Write-optimized. |
| **Memtable** | in-memory sorted buffer of recent writes                              |
| **SSTable**  | Sorted String Table: immutable, sorted on-disk file of kv pairs       |
| **WAL**      | write-ahead log for crash recovery                                   |
| **Bloom filter** | probabilistic membership test per SSTable to skip non-matching files |
| **Compaction** | merge SSTables, discard overwritten/deleted (tombstone) entries     |
| **Tombstone** | marker for a deleted key (deletes are writes too)                    |

LSM trades **read amplification** (must check several SSTables) for excellent **write throughput** (all sequential I/O). Contrast with **B-trees** (RDBMS): great reads, in-place random writes. Deletes are **tombstones**, reclaimed during compaction.

---

## Putting it all together

| Concern              | Technique                                         |
| -------------------- | ------------------------------------------------- |
| Partition data       | consistent hashing + virtual nodes                |
| Durability / HA      | replicate to N nodes (preference list, multi-DC)  |
| Tunable consistency  | quorum N / W / R                                  |
| Conflict resolution  | versioning + vector clocks (client reconciles)    |
| Failure detection    | gossip protocol                                   |
| Temporary failure    | sloppy quorum + hinted handoff                    |
| Permanent failure    | anti-entropy with Merkle trees                    |
| DC outage            | cross-datacenter replication                      |
| Storage engine       | LSM tree (memtable + WAL + SSTable + compaction)  |

---

## Real-world usage

| System              | Notes                                                       |
| ------------------- | ----------------------------------------------------------- |
| Amazon **Dynamo / DynamoDB** | AP, vector clocks (Dynamo paper), sloppy quorum    |
| Apache **Cassandra**| AP, tunable consistency, LSM/SSTable, gossip                |
| **Riak**            | Dynamo-style, vector clocks, AP                              |
| Google **Bigtable / HBase** | CP, SSTable + WAL + memtable origin                 |
| **LevelDB / RocksDB** | embedded LSM engines (back many of the above)             |
| **Redis**           | in-memory kv (different design point)                       |

---

## Trade-offs and gotchas

- **CP vs AP is a product decision** — banking leans CP; carts/sessions lean AP.
- **Tuning N/W/R** changes latency/consistency live; `W+R>N` ≠ linearizable (still has edge cases without read-repair).
- **Vector clock bloat** — cap entries; or use **last-write-wins** (simpler, can lose updates) like Cassandra.
- **Hinted handoff isn't durable** — if the substitute dies before handoff, the hint is lost; anti-entropy is the safety net.
- **Compaction is I/O heavy** — schedule/throttle it; it competes with live traffic.
- **Read amplification** under many SSTables — Bloom filters + leveled compaction mitigate.
- **Hotspots** — a hot key still hammers one preference list; needs app-level sharding/caching.
- **Clock-free conflict detection** — vector clocks avoid relying on wall-clock unlike LWW.

---

## One-page summary

```
   GOAL: distributed put/get — billions of small pairs, HA, scalable

   CAP:       partition is given → choose AP (Dynamo) here
   PARTITION: consistent hashing + virtual nodes
   REPLICATE: N copies, preference list, across racks/DCs
   QUORUM:    W + R > N ⇒ strong;  N=3,W=2,R=2 default
   CONFLICT:  versioning + vector clocks → client merges siblings
   DETECT:    gossip (heartbeat membership)
   TEMP FAIL: sloppy quorum + hinted handoff
   PERM FAIL: anti-entropy via Merkle trees
   DC OUTAGE: multi-datacenter replication
   ENGINE:    LSM — WAL → memtable → SSTable → compaction
              read: memtable → Bloom filter → SSTables
```

## Notes
_Add your own notes here._
