# Chapter 15: Design Google Drive

A cloud file-storage and **sync** service (Google Drive / Dropbox / OneDrive): files upload once and stay consistent across every device, with sharing, notifications and version history.

```
   ┌────────┐        ┌──────────────┐        ┌────────┐
   │ Laptop │ ◄────► │   The Cloud  │ ◄────► │ Phone  │
   └────────┘  sync  │ (single src  │  sync  └────────┘
                     │  of truth)   │
   ┌────────┐ ◄────► └──────────────┘ ◄────► ┌────────┐
   │  Web   │                                │ Tablet │
   └────────┘   edit on one → appears on all └────────┘
```

---

## Requirements

**Functional**
- Add / download files (from any device).
- **Sync** files across devices.
- See file revisions / **version history**.
- Share files; view & edit.
- **Notify** when a shared file changes.
- Snapshot + restore.

**Non-functional**
- Reliability — data loss is unacceptable.
- Fast sync; bandwidth-efficient (low cost).
- Scalable to huge traffic and storage.
- High availability; works (read-only) through partial outages.

---

## Back-of-the-envelope estimation

Assumptions
- 50M signed up, **10M DAU**
- Each user gets 10 GB free space
- Each user uploads 2 files/day, avg file = **500 KB**
- Read:write ratio ≈ **1:1** (sync is symmetric)

```
   total storage   = 50M × 10 GB              = 500 PB allocated
   uploads/day     = 10M × 2                  = 20M files/day
   upload QPS      = 20M / 86,400             ≈ 240 QPS
   peak QPS        ≈ 2× = ~480 QPS
   ingress/day     = 20M × 500 KB             ≈ 10 TB / day
```

```
   ┌──── inputs ────┐      ┌──── derived ────┐
   │ 10M DAU        │      │ 240 QPS write   │
   │ 2 files/day    │ ──►  │ ~10 TB/day in   │
   │ 500 KB/file    │      │ 500 PB ceiling  │
   │ 10 GB/user     │      │ dedup = big win │
   └────────────────┘      └─────────────────┘
```

> Storage dominates. The headline optimizations are **delta sync** (only changed blocks) and **dedup** — both cut storage and bandwidth.

---

## Start single-server, then scale

**Step 1 — one box:**
```
   Client ──► [ Web server ] ──► local /drive directory
                     │
                     ▼
              [ MySQL: metadata ]
```
- Web server: upload/download.
- MySQL: users, files, sharing.
- Local filesystem: the bytes (organized by namespace).

**Step 2 — scale storage:** vertical (bigger disk) runs out → **horizontal**. Replace the local disk with an **S3-like object store**:
- Same-region replication → durability + availability.
- Cross-region replication → disaster recovery + locality.

```
   one disk → fills up → S3-like object store
                          ├── replica (same region)  → durability
                          └── replica (other region) → DR
```

---

## High-level design

```
   ┌────────┐     ┌──────────────┐     ┌──────────────┐
   │ Client │ ──► │ Load balancer│ ──► │ API servers  │
   └───┬────┘     └──────────────┘     └──────┬───────┘
       │                                       │
       │ file bytes                  ┌──────────┼───────────┐
       ▼                             ▼          ▼           ▼
   ┌──────────────┐         ┌──────────┐ ┌────────────┐ ┌──────────────┐
   │ Block servers│ ──────► │ Cloud    │ │ Metadata   │ │ Notification │
   │ split/comp/  │         │ storage  │ │ DB + cache │ │ service      │
   │ encrypt/delta│         │ (S3)     │ └────────────┘ └──────┬───────┘
   └──────────────┘         │  │ cold   │                      │
                            └──┼────────┘                      ▼
                               ▼                          push changes
                          [ Cold storage ]                to other devices
        Offline backup queue ◄── changes while a device is offline
```

| Component        | Role                                                        |
| ---------------- | ----------------------------------------------------------- |
| **Load balancer**| Spread traffic across API servers                           |
| **API servers**  | Everything except the bytes: auth, metadata, sharing        |
| **Block servers**| Split files → blocks; compress; encrypt; upload changed blocks only |
| **Cloud storage**| Store blocks (S3-like), replicated                           |
| **Cold storage** | Infrequently accessed data (cheap tier)                      |
| **Metadata DB**  | Users, files, versions, block mappings                       |
| **Metadata cache**| Hot metadata (low-latency reads)                            |
| **Notification** | Tell other devices "something changed, re-sync"             |
| **Offline backup queue** | Buffer changes for offline devices until they reconnect |

---

## Block servers & delta sync

A file is split into fixed-size **blocks** (Dropbox uses 4 MB). Each block is hashed; only blocks that **changed** are processed and uploaded.

```
   File v1: [ B1 ][ B2 ][ B3 ][ B4 ]
   edit middle ─────────────┐
   File v2: [ B1 ][ B2 ][ B3'][ B4 ]
                         only B3' is:
                         1. split out
                         2. compressed
                         3. encrypted
                         4. uploaded
   → bandwidth & storage ∝ change size, not file size
```

Block server pipeline on upload: **split → diff vs known hashes → compress → encrypt → upload changed blocks → update metadata**. Download is the reverse: fetch needed blocks → decrypt → decompress → reassemble.

This is the single biggest efficiency lever in the whole design — it makes the `~10 TB/day` ingress estimate far smaller in practice.

---

## Sync & conflict resolution

Multiple devices edit the same file → conflicts. Rule: **first write wins, later write becomes a conflicted copy** (no silent overwrite, no auto-merge for binary files).

```
   User A saves f.doc  ──► reaches cloud first ──► becomes the file
   User B saves f.doc  ──► arrives later
        │
        ▼
   B is told "conflict": B's version saved as
   "f (User B's conflicted copy).doc"  ──► human resolves
```

- Each device holds a **local cursor / version**. On change → push to cloud → notification fans out → other devices pull the new version.
- A long-running editor is told its base version is stale **before** it overwrites.
- Presenting both copies (vs auto-merge) is the safe, expected interview answer.

---

## Metadata model

| Table         | Key columns                                                        |
| ------------- | ------------------------------------------------------------------ |
| **user**      | user_id (PK), name, email, profile, status                         |
| **device**    | device_id (PK), push_id, last_logged_in_at, user_id (FK)           |
| **namespace** | namespace_id (PK), owner_id (root dir / shared space)              |
| **file**      | file_id (PK), file_name, file_info, is_directory, parent_id, namespace_id |
| **file_version** | file_version_id (PK), file_id (FK), uploader_id, created_at     |
| **block**     | block_id (PK), file_version_id (FK), block_order (offset)           |

```
   user ──< device
   user ──< namespace ──< file ──< file_version ──< block ─► (block in S3)
```
- A **file** is an ordered list of **blocks** within a **file_version**.
- New version = new `file_version` row + only the changed `block` rows; unchanged blocks are referenced (and **deduped**).

---

## Notification service

When a device commits a change, other devices must learn quickly.

| Mechanism      | Notes                                                       |
| -------------- | ----------------------------------------------------------- |
| **Long polling** | Chosen here: notifications are infrequent & not bidirectional; simpler, firewall-friendly; client re-polls after each event |
| **WebSocket**  | Bidirectional, lower latency — overkill for occasional file-change pings |

> Dropbox uses long polling. Each client holds an open long-poll; on a change the server responds, the client syncs, then re-establishes the poll.

If a device is **offline**, changes accumulate in the **offline backup queue** and are delivered when it reconnects.

---

## Save storage space

- **Block-level dedup** — identical blocks (across versions and across users) stored once, referenced by hash.
- **Versioning limits** — keep a bounded number of versions; prune oldest, keep "moving versions" intelligently.
- **Cold tiering** — move infrequently accessed data to cold storage (cheaper, slower).

```
   100 users upload the same 50 MB installer
   naive:  100 × 50 MB = 5 GB
   dedup:  1 × 50 MB + 99 references ≈ 50 MB
```

---

## Failure handling

| Component failure  | Handling                                                        |
| ------------------ | --------------------------------------------------------------- |
| **Load balancer**  | Secondary LB takes over (heartbeat); DNS/anycast failover        |
| **Block server**   | Stateless — another picks up unfinished jobs from the queue      |
| **Cloud storage**  | Multi-region replication; serve from a healthy replica           |
| **API server**     | Stateless behind LB — drop the node, route elsewhere             |
| **Metadata cache** | Multi-node replicated; miss → fall back to metadata DB           |
| **Metadata DB**    | Primary down → promote a replica; replicas across machines       |
| **Notification svc**| On reconnect, clients re-poll and reconcile from current state  |
| **Offline backup queue** | Replicated queue; consumers re-process from last ack       |

Theme: keep the byte path **stateless + replicated**, and make every component resumable from durable state (queue or DB).

---

## Trade-offs and gotchas

- **Delta sync + dedup** turn an unaffordable storage/bandwidth bill into a manageable one — lead with these.
- **Long polling over WebSocket** — justified by traffic pattern; shows you pick the simpler tool that fits.
- **Conflicts: never auto-merge binaries** — keep both copies; let the human decide.
- **Strong consistency on metadata** (users see correct file list) but the byte store can be eventually consistent across regions.
- **Block size is a tuning knob** — bigger blocks = less metadata, worse delta granularity; smaller = finer sync, more metadata overhead.

---

## One-page summary

```
   GOAL: store files + keep them synced across devices, cheaply & reliably

   SPLIT:   file → blocks; only changed blocks move (delta sync)
   BLOCK:   split → compress → encrypt → upload → metadata
   STORE:   S3-like object store, replicated; cold tier for stale data
   META:    user/device/namespace/file/file_version/block (+ cache)
   SYNC:    long polling notifies devices; offline queue buffers
   CONFLICT:first-write-wins; loser → "conflicted copy"
   SAVE:    block dedup, version limits, cold tiering
   FAIL:    stateless byte path + replicated stores; resume from queue
```

## Notes
_Add your own notes here._
