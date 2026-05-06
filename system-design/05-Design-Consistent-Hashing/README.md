# Chapter 5: Design Consistent Hashing

Distribute keys (cache entries, DB rows, requests) across `N` servers in a way that **minimizes data movement** when servers are added or removed.

```
   Goal: when N changes,                Naive `hash % N` re-maps
         relocate as few keys           almost ALL keys.  Bad.
         as possible.                   Consistent hashing re-maps
                                        only ~1/N keys.  Good.
```

---

## The rehashing problem (`hash % N`)

The naïve way to assign keys to servers:
```
   server_id = hash(key) % N
```

It works fine **until N changes** (add/remove a node). Then nearly every key gets reassigned, causing a stampede of cache misses or data shuffles.

```
   N = 4 servers           Add 1 server  → N = 5

   key   hash  hash%4      key   hash  hash%5
   k1     7     3           k1    7     2     ← moved
   k2     3     3           k2    3     3
   k3    11     3           k3   11     1     ← moved
   k4     5     1           k4    5     0     ← moved
   k5     9     1           k5    9     4     ← moved

   ~80% of keys remapped just by adding 1 node
```

This is fatal for caches (mass miss → DB overload), distributed DBs (huge data shuffle), and load balancers (broken affinity).

---

## Hash space and the hash ring

**Idea:** map both servers and keys onto a **circular hash space** (e.g. SHA-1 → 0 to 2^160 − 1). Wrap the line into a ring.

```
   Hash space: 0 ─────────────────────────── 2^160 - 1
                            │
                          wrap
                            ▼
                   ┌──────────────┐
                   │      0       │
                   │   ●          │
                   │     ●  ring  │
                   │   ●          │
                   │      ●       │
                   └──────────────┘
```

---

## Place servers and keys on the ring

1. Hash each server's identifier (IP, name) to a point on the ring.
2. Hash each key to a point on the ring.
3. **Lookup rule:** walk **clockwise** from the key's position; the **first server** you meet owns that key.

```
                 0
            S0 ●
                       ● k1   ──► clockwise ──► S1 owns k1
       S3 ●                ● S1
                                 ● k2   ──► S2 owns k2
            S2 ●     ● k3
                          ──► clockwise (wrap) ──► S0 owns k3
```

Lookup cost = `O(log N)` with a sorted structure (TreeMap / sorted array + binary search).

---

## Add a server

When a new server `S4` joins between `S3` and `S0`:

```
   Before                       After (add S4)
   ──────                       ──────────────
        S0                          S0
   S3        S1                S3       S1
        S2                       S4
                                    S2

   Only keys that were owned by the next clockwise server (S0)
   AND fall in the new arc S3..S4 move to S4.
   All other keys: unchanged.
```

Result: roughly **K/N keys move**, where K = total keys and N = servers. Compare to naïve hashing where ~all K keys move.

---

## Remove a server

When `S1` leaves, all keys it owned now belong to the **next server clockwise** (`S2`).

```
   Before               After (remove S1)
                            S0
        S0                    \
   S3        S1   ──►          \   keys that were S1's
        S2                   S3 → S2  → all go to S2
```

Again, only the keys that were on `S1` move; everything else is untouched.

---

## Two issues with the basic approach

### Issue 1: Partitions are not equal-sized
Server hashes land at random positions on the ring → arc lengths differ → some servers own much larger key ranges than others.

```
        S0 ●
                ●●●●● lots of keys here
                                 ● S1
        S3 ●          ● S2
        ↑ tiny partition
```

### Issue 2: Non-uniform key distribution
Even with equal arcs, real-world keys hash unevenly — popular keys cluster on one server → **hot spots**.

```
   S0  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  ◄── hot
   S1  ▒▒
   S2  ▒▒▒▒
   S3  ▒
```

Both issues lead to **load imbalance** and reduce the benefits of horizontal scaling.

---

## Solution: Virtual nodes (vnodes / replicas)

Each physical server is hashed to **many** points on the ring (say 100–200 virtual nodes per real server, using `hash(server_id + i)` for `i = 0..M`).

```
   1 physical server  →  many vnodes scattered on the ring

       v3-0
   v0-2     v1-1
                   v2-0
       v0-0   v3-1
                v1-0
        v2-1            v0-1   …

   keys spread across many small arcs → load evens out
```

- More vnodes → more even distribution but more memory/metadata.
- The standard deviation of load drops as you add vnodes (book quotes: 100 vnodes → ~10% stdev; 200 → ~5%).
- Each physical server owns the union of its vnodes' arcs.

```
   stdev of load
       │
   ●   │
       │ ●
       │   ●
       │      ●
       │           ●  ●  ●
       └────────────────────► # vnodes per server
       (diminishing returns)
```

---

## Lookup (with vnodes)

```
   1. hash(key) → position p on the ring
   2. binary-search the sorted vnode positions for the
      first vnode at or after p (wrap to start if needed)
   3. that vnode → physical server S → S serves the key
```

Total memory: `O(N · M)` for N servers × M vnodes each.
Lookup time: `O(log(N · M))`.

---

## Putting it all together

```
   Build phase
   ───────────
   for each server S:
     for i in 0..M:
       ring.add(hash(S.id + ":" + i)) → S

   Lookup
   ──────
   p = hash(key)
   vnode = first ring entry ≥ p   (else wrap to ring[0])
   server = ring[vnode]

   Add server S_new
   ────────────────
   for i in 0..M:
     ring.add(hash(S_new.id + ":" + i)) → S_new
   only keys in the new arcs migrate

   Remove server S_old
   ───────────────────
   ring.remove(all S_old vnodes)
   keys move clockwise to the next vnode's server
```

---

## Benefits of consistent hashing

- **Minimized remapping** — only ~K/N keys move when N changes.
- **Quick scaling** — adding/removing nodes is cheap.
- **Hotspot mitigation** — vnodes spread load evenly.
- **No central coordinator** required for routing — clients (or smart proxies) can compute the destination locally.

---

## Real-world usage

| System              | Use of consistent hashing                          |
| ------------------- | -------------------------------------------------- |
| Amazon **Dynamo / DynamoDB** | data partitioning + replication           |
| Apache **Cassandra**| partitioner across the ring                        |
| **Discord**         | sharding chat channels across servers              |
| **Akamai** CDN      | mapping URLs to edge servers                       |
| **Memcached** clients (libketama) | client-side server selection         |
| **Couchbase**       | data placement                                     |
| Google **Maglev**   | network LB (uses a slightly different lookup table approach) |

---

## Trade-offs and gotchas

- **Vnode count tuning** — too few → unbalanced; too many → metadata bloat.
- **Heterogeneous hardware** — give beefier servers more vnodes (proportional to capacity).
- **Replication** — for HA, store each key on the next K vnodes belonging to **distinct** physical servers (Dynamo-style preference list).
- **Hash function quality matters** — poor hash → uneven ring even with many vnodes (use MD5, SHA-1, MurmurHash3, xxHash).
- **Rebalance cost** — even minimal movement can be expensive at PB scale; throttle migrations.
- **Cold cache after migration** — newly responsible server may need warm-up; use techniques like multi-get from old node during transition.

---

## Alternatives worth knowing

- **Range partitioning** — simple, range-scan friendly; suffers from hotspots if range is skewed.
- **Hash partitioning (`hash % N`)** — simple but the rehash problem is fatal at scale.
- **Rendezvous (Highest Random Weight) hashing** — each (key, server) pair gets a weight; pick max. No ring, simple math, similar minimal-movement property; lookup is O(N) per key.
- **Jump consistent hash** (Google) — O(1) memory, O(log N) lookup, very fast; but only supports adding/removing the **last** bucket.
- **Maglev hashing** — small lookup table for L4 LBs; very fast lookup.

---

## One-page summary

```
   Problem: hash % N reshuffles ~all keys when N changes.

   Solution: hash space → circular ring
             servers and keys both placed on the ring
             key owned by next server clockwise

   Issues:   uneven arcs + skewed keys → hot spots

   Fix:      Virtual nodes (100–200 per server)
             → smooth distribution, ~K/N moved on resize

   Used by:  Dynamo, Cassandra, Discord, Akamai, Memcached
```

## Notes
_Add your own notes here._
