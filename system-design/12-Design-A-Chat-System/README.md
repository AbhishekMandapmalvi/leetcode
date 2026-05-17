# Chapter 12: Design A Chat System

A chat system delivers messages between users in near real-time, supports 1-on-1 and group chat, shows online presence, and works across multiple devices. The hard parts: a **persistent connection** so the server can *push* to clients, and a **fan-out + storage** model that scales to millions of concurrent connections.

```
   Alice ──ws──► [Chat Server A] ──┐
                                   │   message queue / direct push
   Bob   ──ws──► [Chat Server B] ◄─┘
                       │
                       ▼
              ┌──────────────────┐
              │  Message store   │  (KV / HBase)
              └──────────────────┘
```

---

## Functional requirements

- **1-on-1 chat** with low delivery latency.
- **Group chat** (small groups, e.g. ≤ 100 / 500 members).
- **Online presence** indicator (online / offline / last-seen).
- **Multi-device** — same account logged in on phone + laptop, all stay in sync.
- **Push notifications** when the recipient is offline.
- **Scale:** target ~50M DAU; messages persisted; history retrievable.

Non-goals to state up front: we focus on text; media (images/video) is "upload to blob store, send a link" and out of scope for the core path.

### Back-of-envelope

```
   50M DAU
   ~ assume 10M concurrent connections (peak)
   ~ each user sends 40 messages/day → 2B messages/day
   ~ 2B / 86400 ≈ 23K messages/sec (avg), peak ~5x ≈ 100K+/sec
   storage: 2B msgs/day × ~100 bytes ≈ 200 GB/day → years of history = PB scale
```

The two numbers that drive the design: **10M concurrent long-lived connections** (memory/FD-bound, not CPU) and **PB-scale append-heavy message storage**.

---

## Communication options

The client always *sends* over HTTP fine. The problem is the **receive** path: a server cannot natively push to a client over plain HTTP. Three classic options:

```
   Polling                    Long polling                 WebSocket
   ───────                    ────────────                 ─────────
   C ──req──► S               C ──req──► S (holds)          C ══handshake══► S
   C ◄─empty─ S                       ...wait...            C ◄════ msg ════ S   (any time)
   C ──req──► S               C ◄─msg/timeout─ S            C ════ msg ════► S   (any time)
   C ◄─msg──  S               C ──req──► S (re-open)        full-duplex, 1 conn
   (poll every N s)           (reconnect each cycle)        stays open
```

| Option        | Latency        | Server load                | Notes                                        |
| ------------- | -------------- | -------------------------- | -------------------------------------------- |
| **Polling**   | up to interval | wasteful (mostly empty)    | simple; bad for chat                         |
| **Long poll** | low-ish        | many hanging requests; reconnect churn | works through most proxies; HTTP only one-way per cycle |
| **WebSocket** | low (push)     | 1 long-lived conn / client | **chosen**; full-duplex, both directions     |

> **Decision: WebSocket** for the receive path (and we may also use it for send, so one connection does both). WebSocket starts as an HTTP handshake then upgrades, so it traverses firewalls on port 80/443.

**Why not just polling:** at 10M users polling every few seconds you generate millions of mostly-empty requests/sec — enormous waste and still high latency. **Why not long polling:** a sender and receiver may be on different servers (the receiver's hanging request lands on a server that never sees the message), and frequent reconnects churn. WebSocket gives one durable, bidirectional channel — send *and* receive on the same socket.

---

## High-level design

Split services by whether they hold connection state.

```
                         ┌──────────────────────────────┐
                         │   Stateless services         │
   Client ──HTTP──►       │  (behind a load balancer)    │
        │                 │  ┌────────┐ ┌────────────┐   │
        │                 │  │  Auth  │ │ User profile│  │
        │                 │  ├────────┤ ├────────────┤   │
        │                 │  │ Group  │ │  Service   │   │
        │                 │  │  mgmt  │ │ discovery  │   │
        │                 │  └────────┘ └────────────┘   │
        │                 └──────────────────────────────┘
        │
        │  ws (persistent)  ┌──────────────────────────────┐
        └──────────────────►│  Stateful: Chat servers      │
                            │  C1 ── C2 ── C3 ... (sticky)  │
                            └───────────────┬──────────────┘
                                            │
                            ┌───────────────▼──────────────┐
                            │ 3rd-party: Push (APNs/FCM)    │
                            └──────────────────────────────┘
```

### Stateless services
Standard request/response services behind a load balancer; any instance can serve any request.

- **Auth / login** — issue tokens; validate on connect.
- **Group management** — create group, add/remove members, list members.
- **User profile** — display name, avatar, settings.
- **Service discovery** — tells the client *which chat server* to connect to (best chat server by geography + load). Backed by **Apache Zookeeper**: chat servers register themselves; the discovery service hands the client the best endpoint.

### Stateful chat service
The **chat servers** are stateful: each holds the live WebSocket connection for the users mapped to it. There is a persistent 1:1 mapping between an online client and a specific chat server for the life of the connection (so it must be **sticky**). If a chat server dies, clients reconnect (discovery re-assigns them).

### Third-party push notification
When the recipient is **offline** (no live WebSocket), we cannot push in-app. Hand off to **APNs (iOS) / FCM (Android)** to deliver a notification so the user opens the app and syncs.

---

## Storage choices

Two very different access patterns ⇒ two stores.

| Data                | Store                | Why                                                         |
| ------------------- | -------------------- | ----------------------------------------------------------- |
| User account, friend/contact list, groups | **RDBMS** (replicated) | low volume, relational, needs joins/consistency; fits in one DB easily |
| **Messages**        | **Key-value / HBase** | huge write volume, append-heavy, range scans by time, only the recent tail is hot; horizontal scale |

**Why KV/HBase for messages, not RDBMS:**

- Enormous, ever-growing data (Facebook/WhatsApp: ~60B+ messages/day) — needs easy horizontal scaling.
- Access pattern is "recent messages of a conversation, in order" → a column-family store keyed by conversation with time-sortable columns is ideal.
- Long tail is rarely read; we want cheap sequential storage.
- HBase / Cassandra used in production (HBase at Facebook Messenger, Cassandra at Discord).

---

## Message data model

### 1-on-1 message table
Primary key must let us **fetch a conversation's messages in time order**. `message_id` is the clustering key and is **monotonically increasing per conversation** (so it doubles as the sort key — no need to sort by `created_at`).

| Field          | Type      | Notes                                  |
| -------------- | --------- | -------------------------------------- |
| `message_id`   | bigint    | **PK**, globally unique, time-sortable |
| `message_from` | bigint    | sender user id                         |
| `message_to`   | bigint    | recipient user id                      |
| `content`      | text      | message body                           |
| `created_at`   | timestamp | for display                            |

### Group message table
Group conversations are read "give me messages in this channel"; partition by `channel_id`.

| Field          | Type      | Notes                                            |
| -------------- | --------- | ------------------------------------------------ |
| `channel_id`   | bigint    | **partition key** (all msgs of a group together) |
| `message_id`   | bigint    | **sort/clustering key**, time-ordered            |
| `user_id`      | bigint    | sender                                           |
| `content`      | text      | body                                             |
| `created_at`   | timestamp |                                                  |

> 1-on-1: PK `(message_id)`, lookup by participant pair. Group: composite PK `(channel_id, message_id)` so a single partition holds the channel and a range scan returns history.

### Message ID generation
`message_id` must be **(1) unique** and **(2) sortable by time** (ID order == chronological order). Options:

- **`auto_increment`** of an RDBMS — not available in NoSQL; single point.
- **Snowflake** (Twitter) — 64-bit ID = `timestamp | datacenter | machine | sequence`. Globally unique, roughly time-ordered. Good default.
- **Local sequence number** — only needs to be unique **within one conversation** (since we always query within a conversation). A per-conversation counter is far simpler than global Snowflake and still gives correct ordering inside the chat. Use this when global ordering across conversations is unnecessary.

---

## Service discovery

The client must learn the *right* chat server (geographically close, not overloaded). **Apache Zookeeper** is the coordination service:

```
   Chat servers register ──►  ┌───────────────┐
   ephemeral nodes            │   Zookeeper   │
   (host, region, load)       └───────┬───────┘
                                      │
   Client ── "where do I connect?" ──►│
            ◄── chat_server_42 (best) ─┘
   Client ══ websocket ══► chat_server_42
```

Zookeeper tracks live chat servers (ephemeral znodes auto-disappear on crash); the discovery service picks the best one by region + current load and returns it to the client.

---

## 1-on-1 message flow

```
   Alice                  Chat S1        ID gen / Queue        Chat S2          Bob
     │  msg ─────────────►  │                                    │              │
     │                      │── store ──► [KV message store]      │              │
     │                      │── get msg_id (Snowflake) ──┘        │              │
     │                      │                                     │              │
     │                      │  Bob online? ── yes ──► push ──────►│── ws ───────►│
     │                      │  Bob offline? ─ no ──► APNs/FCM push notification   │
     │ ◄── ack (delivered)──│                                     │              │
```

1. Alice sends message to her chat server **S1**.
2. S1 gets a `message_id` from the ID generator.
3. S1 **persists** the message to the KV store.
4. S1 asks: is Bob online? (presence / connection registry).
   - **Online:** forward to Bob's chat server **S2**, which pushes over Bob's WebSocket.
   - **Offline:** send to the **push notification (APNs/FCM)** service.

### Multi-device sync
Each device holds its own WebSocket and has a `cur_max_message_id` (the latest message it has seen). On connect, the client sends `cur_max_message_id`; the server streams everything newer. This keeps phone and laptop in sync and recovers messages missed while offline.

---

## Online presence

Presence is just another set of state changes broadcast to people who care.

### Heartbeat
A client wouldn't reliably send an "I'm going offline" event (it just loses network). So clients send a **periodic heartbeat** (e.g. every 5 s). If the presence server hasn't heard a heartbeat within `x` seconds, mark the user **offline**. This avoids flapping offline on brief blips.

```
   Client ─hb─►  ───hb───►  ──(silence > 30s)──►  mark OFFLINE
                 presence server timer resets each heartbeat
```

### Presence fan-out
When a user goes online/offline, who needs to know? Their **friends/contacts**. The presence server publishes the state change to each friend's channel; their chat servers push the indicator.

```
                       online: Alice
   presence server ──► fan-out to Alice's friends
        │
        ├──► Bob's chat server   ──ws──► Bob (sees Alice online)
        ├──► Carol's chat server ──ws──► Carol
        └──► Dave's chat server  ──ws──► Dave
```

This is fine for typical friend-list sizes. For **huge** groups/followings, presence fan-out is expensive — fetch presence on demand (when opening a chat) or only for group members currently in the chat view.

---

## Group chat flow

For small groups, the simple, robust model is a **per-recipient message queue (inbox)**.

```
   Alice sends to Group(Bob, Carol)

                         ┌──────────────┐
   Alice ─msg─► chat ───►│ copy into    │──► Bob's   inbox/queue ──► Bob
                         │ each member's│──► Carol's inbox/queue ──► Carol
                         │ sync inbox   │
                         └──────────────┘
```

- On send, fan the message **into each recipient's own message sync queue**.
- **Pros:** receiving is dead simple (each user only reads their own inbox); good for small groups; naturally handles offline members (they drain the queue later).
- **Cons:** write amplification — one send → N copies. Acceptable when group size is bounded (book caps small groups, e.g. ≤ 500). For very large groups, switch to a **shared per-channel log** (store once, every member range-scans the channel) at the cost of more complex read/sync logic.

---

## Read receipts

To show "delivered" / "read":

- Add a per-recipient row tracking the **last message id** they have **received** and the **last message id** they have **read**.
- When a client renders messages, it sends a `read` event with the max read `message_id`; the sender's client is notified and shows the receipt.
- In groups this is per-member, so "read by 3/5".

---

## Detailed architecture (everything together)

```
              ┌─────────┐
   Client ───►│   LB    │───► Stateless API (auth, profile, group, presence API)
      │       └─────────┘            │
      │                               ▼
      │  1) ask discovery        ┌──────────┐
      │     "which chat server?" │Zookeeper │  ◄── chat servers register (ephemeral)
      │ ◄────────────────────────│discovery │
      │                          └──────────┘
      │  2) open websocket
      ▼
   ┌───────────────┐  send   ┌──────────────┐   ┌────────────────┐
   │ Chat server S1│────────►│  ID gen      │   │ Presence server│◄─ heartbeats
   │ (holds socket)│         │ (Snowflake)  │   └───────┬────────┘
   └───────┬───────┘         └──────────────┘           │ fan-out
           │ persist                                     ▼
           ▼                                       friends' chat servers
   ┌────────────────┐   recipient online? ──► push via their chat server (S2)
   │ KV/HBase store │   recipient offline? ──► APNs / FCM
   └────────────────┘
```

---

## Scaling and other talking points

- **Chat servers are the connection bottleneck**, not CPU — each holds many idle long-lived sockets (memory + file descriptors). Scale **horizontally**; size for *concurrent connections*, not request rate.
- **Stateless services** scale trivially behind the LB; autoscale on CPU/RPS.
- **Sticky routing** — a client must stay pinned to its chat server for the connection's life; reconnect (via discovery) on failover.
- **Message store** — shard the KV/HBase store by conversation/channel id; recent tail is hot, cache it.
- **Presence at scale** — on-demand presence for large groups instead of eager fan-out.
- **Failure handling** — at-least-once delivery + client-side dedupe by `message_id`; `cur_max_message_id` recovers gaps after reconnect.
- **Media** — upload to blob/CDN, send only the URL through chat.
- **End-to-end encryption** (Signal protocol) is a common follow-up — server stores ciphertext only.

---

## Trade-offs and gotchas

- **WebSocket vs long polling** — WebSocket is the right call, but mobile networks drop connections constantly; you still need robust reconnect + resync logic.
- **Per-recipient inbox vs shared channel log** — write-amplify simplicity vs read-side complexity; choose by group size.
- **Global Snowflake vs per-conversation sequence** — don't over-engineer; local sequence is enough since queries are scoped to a conversation.
- **Heartbeat tuning** — too aggressive = battery drain + false offlines; too slow = stale presence.
- **At-least-once + dedupe** beats trying to guarantee exactly-once over flaky networks.
- **Sticky chat servers** make deploys/rollouts harder (drain connections gracefully).

---

## One-page summary

```
   GOAL: real-time 1-on-1 + group chat, presence, multi-device, ~50M DAU

   RECV:    WebSocket (full-duplex, server push)  ─ poll/long-poll rejected
   SPLIT:   stateless (auth/group/profile/discovery)
            stateful  (chat servers hold the sockets, sticky)
            3rd-party (APNs/FCM when recipient offline)
   STORE:   RDBMS for user/friend/group ;  KV/HBase for messages
   MSG ID:  Snowflake OR per-conversation local sequence (time-sortable)
   DISCOVER: Zookeeper picks best chat server by region+load
   PRESENCE: heartbeat + timeout; fan-out state to friends (on-demand if huge)
   GROUP:   per-recipient inbox (small) ; shared channel log (large)
   SYNC:    client tracks cur_max_message_id ; at-least-once + dedupe
```

## Notes
_Add your own notes here._
