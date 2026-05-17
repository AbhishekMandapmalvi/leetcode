# Chapter 7: Design A Unique ID Generator In Distributed Systems

Generate **globally unique** IDs across many machines, with no single point of failure, at high throughput. Ideally IDs are also **roughly sortable by time** (good for DB indexes and pagination).

```
   request ──► [ ID service / library on each node ] ──► 73185209473884160
                     │ no coordination per ID
                     ▼
        unique  +  ~time-ordered  +  64-bit  +  ~10k IDs/sec/node
```

---

## Requirements

- **Unique** — no two IDs ever collide, across the whole system.
- **Numeric** and **64-bit** (fits a `BIGINT` / `long`).
- **Time-ordered** — IDs generated later sort after earlier ones (sortable by date).
- **High throughput** — ≥ 10,000 IDs/sec per node.
- **Highly available** — the generator must not be a SPOF.

Why time-ordering matters: time-ordered IDs cluster recent inserts at the **right edge of a B-tree index**, avoiding random page splits, and let you paginate "newest first" by ID alone — no extra `created_at` column or index.

---

## Why not `auto_increment`?

A single database's `AUTO_INCREMENT` / sequence is unique and ordered — **on one DB**. In a distributed setting it fails:

- **Single point of failure / bottleneck** — every insert serializes through one DB.
- **Doesn't scale** — can't shard writes; the sequence is the contention point.
- **Multiple DBs** each with their own counter → **collisions** (both produce `1, 2, 3…`).

So we need an ID scheme that works **without a global lock per ID**.

---

## Approaches

### 1. Multi-master replication

Use DB `auto_increment`, but increment by **k** (number of DB servers) with a per-server offset.

```
   k = 2 servers
   server A: 1, 3, 5, 7, ...     (start 1, step 2)
   server B: 2, 4, 6, 8, ...     (start 2, step 2)
```

| Pros                         | Cons                                                       |
| ---------------------------- | ---------------------------------------------------------- |
| reuses familiar DB feature   | hard to scale across DCs; **not time-ordered** across nodes |
| no extra service             | adding/removing a server breaks the step math; still DB-bound |

### 2. UUID

128-bit random/structured value (e.g. UUIDv4). Each node generates independently — **zero coordination**.

```
   550e8400-e29b-41d4-a716-446655440000   (collision prob ~ 0)
```

| Pros                                   | Cons                                                  |
| -------------------------------------- | ----------------------------------------------------- |
| no coordination, generate anywhere     | **128-bit** (we wanted 64) — bigger indexes/storage   |
| highly available, simple               | **not numeric**, **not time-sortable** (UUIDv4)       |
|                                        | poor DB index locality (random inserts → page splits) |

> UUIDv7 (time-ordered) fixes sortability but is still 128-bit.

### 3. Ticket server (Flickr)

A centralized DB with a single `auto_increment` table; clients call it to get the next ID (`REPLACE INTO ... ; SELECT LAST_INSERT_ID()`).

```
   node ──► [ Ticket Server (1 DB, auto_increment) ] ──► 10042
   node ──► ─────────────────────────────────────► ───►  10043
```

| Pros                                | Cons                                            |
| ----------------------------------- | ----------------------------------------------- |
| numeric, simple, easy to scale read | **single point of failure** (mitigate w/ HA pair) |
| central, predictable                | a network round-trip per ID; ID-server pair adds sync complexity |

> A common refinement: hand out IDs in **batches** (e.g. a node leases a block of 1000 IDs from the ticket server) to amortize the round-trip — fewer calls, but the node can lose a block on crash and IDs are no longer densely packed.

### 4. Twitter Snowflake (recommended)

Don't generate one global sequence — **divide and conquer**. Compose a 64-bit ID from independent sections so each machine generates locally with no coordination, yet IDs stay globally unique and time-sortable. This is the answer the interviewer is looking for.

---

## Snowflake breakdown

A signed 64-bit integer split into sections:

```
  63                    62 ........................ 22 21 ...... 17 16 ...... 12 11 .......... 0
 ┌────┐┌──────────────────────────────────────────┐┌────────────┐┌────────────┐┌──────────────┐
 │sign││            41-bit timestamp (ms)          ││ 5b  datactr ││ 5b  machine ││ 12-bit seq   │
 └────┘└──────────────────────────────────────────┘└────────────┘└────────────┘└──────────────┘
   1                       41                            5             5              12
```

| Section        | Bits | Range / meaning                                                        |
| -------------- | ---- | ---------------------------------------------------------------------- |
| Sign bit       | 1    | always `0` → keeps the ID positive (reserved)                          |
| Timestamp (ms) | 41   | milliseconds since a **custom epoch**; `2^41 ≈ 2.2e12 ms ≈ 69 years`   |
| Datacenter ID  | 5    | `2^5 = 32` datacenters                                                  |
| Machine ID     | 5    | `2^5 = 32` machines per datacenter                                      |
| Sequence       | 12   | `2^12 = 4096` IDs per **machine per millisecond**                       |

- **Datacenter + machine IDs** are assigned at startup (config / Zookeeper / env) and are **fixed at runtime**.
- **Timestamp + sequence** are generated at ID-creation time.
- **Custom epoch** (not Unix epoch 1970) maximizes the usable 69-year window from your product's launch.

**ID construction:**

```
   id =  (timestamp - CUSTOM_EPOCH) << 22
       | (datacenter_id            << 17)
       | (machine_id               << 12)
       |  sequence
```

**Throughput:** 4096 IDs/ms/machine = **~4.1 million IDs/sec/machine** — far above the 10k requirement. The high timestamp bits make IDs **time-sortable** (sort by ID ≈ sort by creation time).

**Why the timestamp goes in the high bits:** integers sort by their most-significant bits first. Putting the timestamp directly after the sign bit makes numeric ordering equal time ordering; datacenter/machine/sequence only break ties within the same millisecond.

---

## Clock synchronization (NTP)

Snowflake **assumes machine clocks are roughly synchronized** and monotonic. Reality:

- Machines use **NTP** to sync wall-clock; drift is normal.
- An NTP correction or leap second can move the clock **backward**.
- If the clock goes backward, you could **reissue a timestamp** already used → potential duplicate ID.

**Mitigations:**

- Track the **last timestamp** used. If the current clock is **less than** the last, either:
  - **spin-wait** until the clock catches up (small drift), or
  - **reject / throw** and alert if the regression is large.
- Run NTP in **slew mode** (gradually adjust) rather than step mode.
- Some implementations keep a **monotonic logical clock** that never moves backward.

---

## Section length tuning

The 41/5/5/12 split is **not sacred** — tune to your deployment:

| If you have...                          | Adjust                                              |
| --------------------------------------- | --------------------------------------------------- |
| Few DCs, many machines                  | shrink datacenter bits, grow machine bits           |
| Very bursty single-node throughput      | grow sequence bits (steal from machine/DC bits)     |
| Need > 69 years lifespan                | grow timestamp bits (costs ID-space elsewhere)      |
| No concurrency, want strict ordering    | could drop machine/DC bits entirely                 |

Constraint: the sections must still sum to ≤ 63 bits (sign bit fixed at 0). Trade-off is always **lifespan vs node count vs per-ms burst**.

---

## High availability

Snowflake is **inherently HA**: ID generation is a local computation on each node — no network call, no shared counter, no SPOF. Operational concerns instead:

- **Unique machine/DC IDs** — assigning the same `(dc, machine)` to two nodes breaks uniqueness. Use **Zookeeper / etcd / config service** to lease unique worker IDs at startup.
- **Stateless** — any node restart is safe (state is just `last_timestamp` + `sequence`, regenerated).
- **Clock guard** — the clock-regression check above is the main correctness risk; monitor it.
- **No coordination at runtime** = scales linearly by adding nodes.

---

## Approach comparison

| Approach            | 64-bit | Numeric | Time-sortable | No SPOF | No coordination |
| ------------------- | ------ | ------- | ------------- | ------- | --------------- |
| auto_increment      | ✅      | ✅       | ✅ (1 DB)      | ❌       | ❌               |
| Multi-master repl   | ✅      | ✅       | ❌             | ✅       | ❌ (step config) |
| UUID (v4)           | ❌(128) | ❌       | ❌             | ✅       | ✅               |
| Ticket server       | ✅      | ✅       | ✅             | ❌ (HA pair) | ❌ (RTT/ID) |
| **Snowflake**       | ✅      | ✅       | ✅             | ✅       | ✅               |

---

## Real-world usage

| System                      | Scheme                                              |
| --------------------------- | --------------------------------------------------- |
| **Twitter** Snowflake       | the original 64-bit design                          |
| **Discord**                 | Snowflake IDs (custom epoch = 2015-01-01)           |
| **Instagram**               | Snowflake-like: timestamp + shard ID + sequence     |
| **Sonyflake**               | Snowflake variant (more time bits, fewer machine)   |
| **MongoDB ObjectId**        | 12-byte: timestamp + machine + pid + counter        |
| **Flickr**                  | ticket server (multi-master `auto_increment`)       |

---

## Trade-offs and gotchas

- **Clock skew is the #1 bug** — backward clock → duplicate IDs. Always guard against regression.
- **Worker ID collisions** — duplicating `(dc, machine)` silently breaks uniqueness; lease them centrally.
- **Sequence exhaustion** — > 4096 IDs in one ms on one node → must spin-wait to next ms (bounded stall).
- **Not strictly monotonic globally** — only sortable to ~ms granularity; two IDs from different machines in the same ms aren't comparable by time alone.
- **Epoch is forever** — once chosen and IDs issued, the custom epoch can't change.
- **69-year lifespan** — fine for most products; plan a migration path if it matters.
- **IDs leak info** — embedded timestamp/DC can reveal creation time and scale to outsiders.

---

## One-page summary

```
   GOAL: unique + 64-bit + numeric + ~time-ordered + HA, ≥10k/s/node

   WHY NOT auto_increment: SPOF, no shard, multi-DB collisions
   OPTIONS:  multi-master (no order) | UUID (128-bit, unsorted)
             ticket server (SPOF/RTT) | Snowflake ✅

   SNOWFLAKE 64 bits:
     1  sign      = 0 (positive)
     41 timestamp = ms since custom epoch  (~69 yrs)
     5  datacenter= 32 DCs
     5  machine   = 32 nodes / DC
     12 sequence  = 4096 IDs / node / ms  (~4.1M/s/node)
     id = (ts-epoch)<<22 | dc<<17 | machine<<12 | seq

   RISKS:  clock goes backward → guard/spin; unique worker IDs via ZK
   HA:     local computation, no SPOF, scales linearly
```

## Notes
_Add your own notes here._
